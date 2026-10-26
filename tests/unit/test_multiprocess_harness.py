"""Multi-process SQLite harness (tasks.md T011; quickstart "Multi-process tests").

"Multi-process tests use separate connections/processes on synthetic files to
exercise SQLite locks; no in-memory-only substitute for actual concurrency."
Children are spawned, guarded like the test process (SQLite only inside their
lab root, no non-loopback network), start together, and report the crash
points they reached. A crash ends the child at once, so only what SQLite
committed survives; a restart is another run on the same files and clock.
"""

import asyncio
import os
from pathlib import Path
import socket
import sqlite3
import time

import pytest

from tests._harness.clock import FakeClock
from tests._harness.crash import CRASH_EXIT_CODE, CrashPlan
from tests._harness.multiprocess import (
    ChildContext,
    ChildResult,
    run_processes,
    run_processes_async,
)
from tests._harness.network_guard import NetworkGuardError


# Child targets: module-level so spawned children can import them.


def _report(context):
    assert isinstance(context, ChildContext)
    return {"pid": os.getpid(), "index": context.index, "count": context.count}


def _claim_last_place(context, db_name):
    conn = sqlite3.connect(context.lab_root / db_name, timeout=10, isolation_level=None)
    try:
        conn.execute("BEGIN IMMEDIATE")
        taken = conn.execute("SELECT COUNT(*) FROM places").fetchone()[0]
        if taken == 0:
            conn.execute("INSERT INTO places (owner) VALUES (?)", (context.index,))
        context.crash("claim.commit.before")
        conn.execute("COMMIT")
        context.crash("claim.commit.after")
        return taken == 0
    finally:
        conn.close()


def _fail(context):
    raise ValueError("synthetic failure")


def _sleep_long(context):
    (context.lab_root / "pid").write_text(str(os.getpid()))
    time.sleep(60)


def _open_database_outside(context):
    sqlite3.connect(context.lab_root.parent / "outside.db")


def _connect_outside(context):
    socket.create_connection(("192.0.2.1", 9), timeout=1)


def _advance_clock(context, ms):
    context.clock.advance(ms)
    return context.clock.true_now_ms()


def _two_points(context):
    context.crash("first")
    context.crash("second")
    return "finished"


def _pause(context, seconds):
    time.sleep(seconds)
    return "paused"


def _places_database(lab):
    conn = sqlite3.connect(lab / "lab.db")
    conn.execute("CREATE TABLE places (owner INTEGER NOT NULL)")
    conn.commit()
    conn.close()


def _owners(lab):
    conn = sqlite3.connect(lab / "lab.db")
    try:
        return [row[0] for row in conn.execute("SELECT owner FROM places")]
    finally:
        conn.close()


def test_children_are_separate_processes(tmp_path):
    results = run_processes(_report, count=3, lab_root=tmp_path)
    assert [result.index for result in results] == [0, 1, 2]
    assert all(isinstance(result, ChildResult) for result in results)
    pids = {result.value["pid"] for result in results}
    assert len(pids) == 3 and os.getpid() not in pids
    for result in results:
        assert result.value["index"] == result.index
        assert result.value["count"] == 3
        assert (result.exit_code, result.crashed_at, result.error_type, result.error) == (
            0,
            None,
            None,
            None,
        )
        assert result.reached == ()


def test_sqlite_race_across_processes_has_one_winner(tmp_path):
    _places_database(tmp_path)
    results = run_processes(_claim_last_place, count=4, lab_root=tmp_path, args=("lab.db",))
    winners = [result.index for result in results if result.value is True]
    assert len(winners) == 1
    assert _owners(tmp_path) == winners
    for result in results:
        assert result.reached == ("claim.commit.before", "claim.commit.after")


def test_crash_before_commit_loses_the_write_and_a_restart_completes(tmp_path):
    _places_database(tmp_path)
    plan = CrashPlan().arm("claim.commit.before")
    (crashed,) = run_processes(
        _claim_last_place, count=1, lab_root=tmp_path, args=("lab.db",), plans=[plan]
    )
    assert crashed.exit_code == CRASH_EXIT_CODE
    assert crashed.crashed_at == "claim.commit.before"
    assert crashed.reached == ("claim.commit.before",)
    assert (crashed.value, crashed.error_type, crashed.error, crashed.clock) == (
        None,
        None,
        None,
        None,
    )
    assert _owners(tmp_path) == []
    assert plan.reached == () and plan.crashed_at is None

    (restarted,) = run_processes(
        _claim_last_place, count=1, lab_root=tmp_path, args=("lab.db",)
    )
    assert (restarted.exit_code, restarted.value) == (0, True)
    assert _owners(tmp_path) == [0]


def test_crash_after_commit_keeps_the_write(tmp_path):
    _places_database(tmp_path)
    plan = CrashPlan().arm("claim.commit.after")
    (crashed,) = run_processes(
        _claim_last_place, count=1, lab_root=tmp_path, args=("lab.db",), plans=[plan]
    )
    assert (crashed.exit_code, crashed.crashed_at) == (CRASH_EXIT_CODE, "claim.commit.after")
    assert crashed.reached == ("claim.commit.before", "claim.commit.after")
    assert _owners(tmp_path) == [0]
    (restarted,) = run_processes(
        _claim_last_place, count=1, lab_root=tmp_path, args=("lab.db",)
    )
    assert restarted.value is False
    assert _owners(tmp_path) == [0]


def test_plans_apply_per_child(tmp_path):
    _places_database(tmp_path)
    results = run_processes(
        _claim_last_place,
        count=2,
        lab_root=tmp_path,
        args=("lab.db",),
        plans=[None, CrashPlan().arm("claim.commit.before")],
    )
    assert (results[0].exit_code, results[0].value) == (0, True)
    assert results[1].crashed_at == "claim.commit.before"
    assert _owners(tmp_path) == [0]


def test_reached_points_are_reported_with_or_without_a_crash(tmp_path):
    (finished,) = run_processes(_two_points, count=1, lab_root=tmp_path)
    assert (finished.value, finished.reached) == ("finished", ("first", "second"))
    (crashed,) = run_processes(
        _two_points, count=1, lab_root=tmp_path, plans=[CrashPlan().arm("second")]
    )
    assert (crashed.crashed_at, crashed.reached) == ("second", ("first", "second"))


def test_child_exception_is_reported_not_raised(tmp_path):
    (failed,) = run_processes(_fail, count=1, lab_root=tmp_path)
    assert failed.exit_code == 1
    assert failed.error_type == "ValueError"
    assert "synthetic failure" in failed.error
    assert (failed.crashed_at, failed.value, failed.clock) == (None, None, None)


def test_network_guard_applies_in_children(tmp_path):
    lab = tmp_path / "lab"
    lab.mkdir()
    with pytest.raises(NetworkGuardError):
        run_processes(_open_database_outside, count=1, lab_root=lab)
    assert not (tmp_path / "outside.db").exists()
    with pytest.raises(NetworkGuardError):
        run_processes(_connect_outside, count=1, lab_root=lab)


def test_timeout_kills_every_child(tmp_path):
    started = time.monotonic()
    with pytest.raises(TimeoutError):
        run_processes(_sleep_long, count=1, lab_root=tmp_path, timeout_s=3.0)
    assert time.monotonic() - started < 15
    pid = int((tmp_path / "pid").read_text())
    with pytest.raises(ProcessLookupError):
        os.kill(pid, 0)


def test_each_child_gets_a_copy_of_the_clock(tmp_path):
    clock = FakeClock()
    clock.advance(1_000)
    before = clock.true_now_ms()
    results = run_processes(
        _advance_clock, count=2, lab_root=tmp_path, args=(5_000,), clock=clock
    )
    for result in results:
        assert result.value == before + 5_000
        assert result.clock.true_now_ms() == before + 5_000
    assert clock.true_now_ms() == before
    (no_clock,) = run_processes(_report, count=1, lab_root=tmp_path)
    assert no_clock.clock is None


def test_async_runner_keeps_the_event_loop_running(tmp_path):
    async def scenario():
        ticks = 0

        async def ticker():
            nonlocal ticks
            while True:
                ticks += 1
                await asyncio.sleep(0.01)

        task = asyncio.create_task(ticker())
        results = await run_processes_async(_pause, count=1, lab_root=tmp_path, args=(0.5,))
        task.cancel()
        return ticks, results

    ticks, (result,) = asyncio.run(scenario())
    assert result.value == "paused"
    assert ticks >= 10


def test_arguments_are_validated(tmp_path):
    with pytest.raises(ValueError):
        run_processes(_report, count=0, lab_root=tmp_path)
    with pytest.raises(ValueError):
        run_processes(_report, count=2, lab_root=tmp_path, plans=[None])
    with pytest.raises(ValueError):
        run_processes(_report, count=1, lab_root=tmp_path / "missing")
    with pytest.raises(ValueError):
        run_processes(_report, count=1, lab_root=Path("/"))
