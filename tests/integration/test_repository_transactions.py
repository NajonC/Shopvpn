"""Integration tests for ``composite/repository.py`` (T032, written before T033;
RD-02; constitution II/VI). Reproduce with `.venv/bin/python -m pytest
tests/integration/test_repository_transactions.py --network=deny`. SQLite is
real, the data synthetic; separate writers are real processes through the T011
harness.

The interface these tests pin, which T033 builds:

- ``BUSY_TIMEOUT_S = 1.0`` and ``BUSY_RETRIES = 3``.
- ``EffectKey(table, column, value)``: a frozen dataclass naming one row by a
  unique key column.
- ``Repository(path, *, busy_timeout_s=BUSY_TIMEOUT_S,
  busy_retries=BUSY_RETRIES, crash=None, connect=None)``. The constructor
  touches no file. All database work runs on the repository's own single worker
  thread, on one dedicated connection it opens there on first use by calling
  ``connect(str(path), **options)`` with ``isolation_level=None`` among the
  options; ``connect=None`` means ``sqlite3.connect`` looked up at call time.
  On opening it sets ``journal_mode=WAL``, ``foreign_keys=ON`` and
  ``synchronous=FULL`` and reads back those three and ``busy_timeout``
  (``busy_timeout_s`` in milliseconds); any other value closes the connection
  and raises ``PragmaMismatch``.
- ``await run(work, *, effect=None)``: ``BEGIN IMMEDIATE``, then
  ``work(connection)``, ``crash("before commit")``,
  ``connection.execute("COMMIT")``, ``crash("after commit")``, and returns
  ``work``'s result. A busy ``BEGIN IMMEDIATE`` is tried again up to
  ``busy_retries`` times, then ``RepositoryBusy`` (``attempts``) is raised and
  ``work`` is never called. Any exception from ``work`` or from the hook before
  ``COMMIT`` rolls back and propagates unchanged. An awaitable result is closed,
  rolled back and refused with ``TypeError``. If ``work`` ended the transaction
  itself, ``TransactionOwnershipError``. If ``COMMIT`` raises, the connection
  is closed and ``IndeterminateCommit`` (``effect``; the original error as
  ``__cause__``) is raised; neither ``work`` nor ``COMMIT`` is repeated, and the
  next ``run`` opens a new connection.
- ``await query_effect(key)``: the row whose ``key.column`` equals
  ``key.value`` as a column-name dict, or ``None``, read outside any write
  transaction and never through a connection whose ``COMMIT`` failed.
  ``ValueError`` when the table or column is not a plain identifier
  (``[A-Za-z_][A-Za-z0-9_]*``), or the column is not by itself the table's
  primary key or a non-partial unique index.
- ``await close()``.
- Errors: ``RepositoryError`` and its subclasses ``RepositoryBusy``,
  ``IndeterminateCommit``, ``PragmaMismatch`` (``pragma``, ``expected``,
  ``actual``) and ``TransactionOwnershipError``.

Until T033 exists, every test fails because the module is still empty.
"""

import asyncio
from contextlib import closing
import sqlite3
import threading
import time

import pytest

import composite.repository as repository
from tests._harness import network_guard
from tests._harness.crash import CRASH_EXIT_CODE, CrashPlan, SimulatedCrash
from tests._harness.multiprocess import run_processes


START_BALANCE = 100_000
DEBIT = 30_000

SCHEMA = """
CREATE TABLE accounts (account_id TEXT PRIMARY KEY, balance INTEGER NOT NULL);
CREATE TABLE effects (
    effect_key TEXT NOT NULL UNIQUE,
    account_id TEXT NOT NULL REFERENCES accounts(account_id),
    amount INTEGER NOT NULL,
    note TEXT
);
CREATE UNIQUE INDEX effects_open_note ON effects(note) WHERE note = 'open';
CREATE TABLE counter (id INTEGER PRIMARY KEY, n INTEGER NOT NULL);
CREATE TABLE "odd-name" (k TEXT PRIMARY KEY);
CREATE TABLE odd_columns ("odd key" TEXT PRIMARY KEY);
INSERT INTO accounts VALUES ('acct', 100000);
INSERT INTO counter VALUES (1, 0);
"""


@pytest.fixture
def main_db(tmp_path):
    path = tmp_path / "main.db"
    with closing(sqlite3.connect(path)) as conn:
        conn.executescript(SCHEMA)
    return path


@pytest.fixture
def wal_db(main_db):
    """``main_db`` already in WAL, as legacy ``Database._connect`` leaves the main
    file. Two processes switching a rollback-journal file to WAL at the same
    moment can fail with "database is locked"."""
    with closing(sqlite3.connect(main_db)) as conn:
        conn.execute("PRAGMA journal_mode=WAL")
    return main_db


def scalar(path, sql, params=()):
    with closing(sqlite3.connect(path)) as conn:
        return conn.execute(sql, params).fetchone()[0]


def balance(path):
    return scalar(path, "SELECT balance FROM accounts WHERE account_id = 'acct'")


def effect_count(path):
    return scalar(path, "SELECT COUNT(*) FROM effects")


def write_lock_is_free(path):
    with closing(sqlite3.connect(path, timeout=0, isolation_level=None)) as conn:
        try:
            conn.execute("BEGIN IMMEDIATE")
        except sqlite3.OperationalError:
            return False
        conn.execute("ROLLBACK")
        return True


def key(value):
    return repository.EffectKey("effects", "effect_key", value)


def debit_work(effect_value, calls=None, amount=DEBIT):
    def work(conn):
        if calls is not None:
            calls.append(effect_value)
        if conn.execute(
            "SELECT 1 FROM effects WHERE effect_key = ?", (effect_value,)
        ).fetchone():
            return "existing"
        conn.execute(
            "UPDATE accounts SET balance = balance - ? WHERE account_id = 'acct'", (amount,)
        )
        conn.execute(
            "INSERT INTO effects (effect_key, account_id, amount, note) VALUES (?, 'acct', ?, 'debit')",
            (effect_value, amount),
        )
        return "applied"

    return work


def debit_row(effect_value, amount=DEBIT):
    return {"effect_key": effect_value, "account_id": "acct", "amount": amount, "note": "debit"}


async def using(path, body, **options):
    repo = repository.Repository(path, **options)
    try:
        return await body(repo)
    finally:
        await repo.close()


def query(path, effect_key):
    async def body(repo):
        return await repo.query_effect(effect_key)

    return asyncio.run(using(path, body))


def failing_commit_connect(applies):
    """A ``connect`` whose first COMMIT raises, after committing when ``applies``."""
    state = {"commits": 0, "failed": False}

    class FailingCommitConnection(sqlite3.Connection):
        def _commit_once(self, commit):
            state["commits"] += 1
            if state["failed"]:
                return commit()
            state["failed"] = True
            if applies:
                commit()
            raise sqlite3.OperationalError("disk I/O error")

        def execute(self, sql, parameters=(), /):
            if isinstance(sql, str) and sql.strip().rstrip(";").upper() == "COMMIT":
                return self._commit_once(lambda: super(FailingCommitConnection, self).execute(sql))
            return super().execute(sql, parameters)

        def commit(self):
            return self._commit_once(lambda: super(FailingCommitConnection, self).commit())

    def connect(database, **options):
        return sqlite3.connect(database, factory=FailingCommitConnection, **options)

    return connect, state


# Child-process targets (module level so the spawn harness can pickle them).


def _increment(context, count):
    async def main():
        repo = repository.Repository(context.lab_root / "main.db", crash=context.crash)

        def work(conn):
            n = conn.execute("SELECT n FROM counter WHERE id = 1").fetchone()[0]
            time.sleep(0.002)
            conn.execute("UPDATE counter SET n = ? WHERE id = 1", (n + 1,))
            conn.execute(
                "INSERT INTO effects (effect_key, account_id, amount, note) VALUES (?, 'acct', 0, 'inc')",
                (f"inc-{context.index}-{n}",),
            )
            return (
                conn.execute("PRAGMA journal_mode").fetchone()[0],
                conn.execute("PRAGMA foreign_keys").fetchone()[0],
                conn.execute("PRAGMA synchronous").fetchone()[0],
                conn.execute("PRAGMA busy_timeout").fetchone()[0],
            )

        try:
            for _ in range(count):
                pragmas = await repo.run(work)
        finally:
            await repo.close()
        return pragmas

    return asyncio.run(main())


def _apply_keys(context, values):
    async def main():
        repo = repository.Repository(context.lab_root / "main.db")
        try:
            return [await repo.run(debit_work(value, amount=1_000)) for value in values]
        finally:
            await repo.close()

    return asyncio.run(main())


def _debit(context, effect_value):
    async def main():
        repo = repository.Repository(context.lab_root / "main.db", crash=context.crash)
        try:
            return await repo.run(debit_work(effect_value), effect=key(effect_value))
        finally:
            await repo.close()

    return asyncio.run(main())


def _reconcile_then_debit(context, effect_value):
    async def main():
        repo = repository.Repository(context.lab_root / "main.db")
        try:
            found = await repo.query_effect(key(effect_value))
            if found is not None:
                return ("found", found)
            return ("ran", await repo.run(debit_work(effect_value), effect=key(effect_value)))
        finally:
            await repo.close()

    return asyncio.run(main())


def _open_outside_lab(context):
    outside = context.lab_root.parent.parent / "outside-lab-root" / "main.db"

    async def main():
        repo = repository.Repository(outside)
        try:
            return await repo.run(lambda conn: None)
        finally:
            await repo.close()

    return asyncio.run(main())


# Two writer processes.


def test_two_writer_processes_lose_no_update(wal_db):
    results = run_processes(_increment, count=2, lab_root=wal_db.parent, args=(100,))

    for result in results:
        assert (result.exit_code, result.error_type, result.crashed_at) == (0, None, None)
        assert result.value == ("wal", 1, 2, 1000)
        assert result.reached == ("before commit", "after commit") * 100
    assert scalar(wal_db, "SELECT n FROM counter WHERE id = 1") == 200
    assert scalar(wal_db, "SELECT COUNT(*) FROM effects WHERE note = 'inc'") == 200


def test_two_writer_processes_apply_each_effect_once(wal_db):
    values = [f"K{i}" for i in range(20)]
    results = run_processes(_apply_keys, count=2, lab_root=wal_db.parent, args=(values,))

    for result in results:
        assert (result.exit_code, result.error_type) == (0, None)
    for i in range(20):
        assert sorted(result.value[i] for result in results) == ["applied", "existing"]
    assert effect_count(wal_db) == 20
    assert balance(wal_db) == START_BALANCE - 20 * 1_000


def test_child_process_connections_pass_through_the_network_guard(tmp_path):
    with pytest.raises(network_guard.NetworkGuardError, match="outside the lab root"):
        run_processes(_open_outside_lab, count=1, lab_root=tmp_path)
    assert not (tmp_path.parent.parent / "outside-lab-root").exists()


# Crash before and after commit.


def test_process_crash_before_commit_leaves_nothing_and_a_restart_applies_once(main_db):
    (crashed,) = run_processes(
        _debit,
        count=1,
        lab_root=main_db.parent,
        args=("E-before",),
        plans=[CrashPlan().arm("before commit")],
    )
    assert (crashed.exit_code, crashed.crashed_at) == (CRASH_EXIT_CODE, "before commit")
    assert crashed.reached == ("before commit",)
    assert query(main_db, key("E-before")) is None
    assert (balance(main_db), effect_count(main_db)) == (START_BALANCE, 0)
    assert write_lock_is_free(main_db)

    (restarted,) = run_processes(
        _reconcile_then_debit, count=1, lab_root=main_db.parent, args=("E-before",)
    )
    assert restarted.value == ("ran", "applied")
    assert query(main_db, key("E-before")) == debit_row("E-before")
    assert (balance(main_db), effect_count(main_db)) == (START_BALANCE - DEBIT, 1)


def test_process_crash_after_commit_is_found_by_the_effect_key_not_repeated(main_db):
    (crashed,) = run_processes(
        _debit,
        count=1,
        lab_root=main_db.parent,
        args=("E-after",),
        plans=[CrashPlan().arm("after commit")],
    )
    assert (crashed.exit_code, crashed.crashed_at) == (CRASH_EXIT_CODE, "after commit")
    assert crashed.reached == ("before commit", "after commit")
    assert query(main_db, key("E-after")) == debit_row("E-after")
    assert (balance(main_db), effect_count(main_db)) == (START_BALANCE - DEBIT, 1)

    (restarted,) = run_processes(
        _reconcile_then_debit, count=1, lab_root=main_db.parent, args=("E-after",)
    )
    assert restarted.value == ("found", debit_row("E-after"))
    assert (balance(main_db), effect_count(main_db)) == (START_BALANCE - DEBIT, 1)


def test_hook_points_bracket_the_commit(main_db):
    events = []

    def hook(point):
        visible = scalar(main_db, "SELECT COUNT(*) FROM effects WHERE effect_key = 'E1'")
        events.append((point, visible))

    def work(conn):
        events.append(("work", None))
        return debit_work("E1")(conn)

    async def body(repo):
        return await repo.run(work, effect=key("E1"))

    assert asyncio.run(using(main_db, body, crash=hook)) == "applied"
    assert events == [("work", None), ("before commit", 0), ("after commit", 1)]


def test_in_process_crash_before_commit_rolls_back_and_frees_the_connection(main_db):
    plan = CrashPlan().arm("before commit")

    async def body(repo):
        with pytest.raises(SimulatedCrash):
            await repo.run(debit_work("E1"), effect=key("E1"))
        assert write_lock_is_free(main_db)
        assert await repo.query_effect(key("E1")) is None
        return await repo.run(debit_work("E2"), effect=key("E2"))

    assert asyncio.run(using(main_db, body, crash=plan)) == "applied"
    assert plan.crashed_at == "before commit"
    assert query(main_db, key("E1")) is None
    assert query(main_db, key("E2")) == debit_row("E2")
    assert balance(main_db) == START_BALANCE - DEBIT


def test_in_process_crash_after_commit_keeps_the_commit(main_db):
    plan = CrashPlan().arm("after commit")

    async def body(repo):
        with pytest.raises(SimulatedCrash):
            await repo.run(debit_work("E1"), effect=key("E1"))

    asyncio.run(using(main_db, body, crash=plan))
    assert query(main_db, key("E1")) == debit_row("E1")
    assert balance(main_db) == START_BALANCE - DEBIT


# Pragmas and transaction ownership.


def test_pragmas_are_read_back_on_the_dedicated_connection(main_db):
    def work(conn):
        return (
            conn.in_transaction,
            conn.execute("PRAGMA journal_mode").fetchone()[0],
            conn.execute("PRAGMA foreign_keys").fetchone()[0],
            conn.execute("PRAGMA synchronous").fetchone()[0],
            conn.execute("PRAGMA busy_timeout").fetchone()[0],
        )

    async def body(repo):
        return await repo.run(work)

    assert repository.BUSY_TIMEOUT_S == 1.0
    assert repository.BUSY_RETRIES == 3
    assert asyncio.run(using(main_db, body)) == (True, "wal", 1, 2, 1000)
    assert asyncio.run(using(main_db, body, busy_timeout_s=0.25)) == (True, "wal", 1, 2, 250)
    assert scalar(main_db, "PRAGMA journal_mode") == "wal"


def test_a_pragma_that_does_not_read_back_is_refused():
    calls = []

    async def body(repo):
        for _ in range(2):
            with pytest.raises(repository.PragmaMismatch) as caught:
                await repo.run(lambda conn: calls.append(conn))
            error = caught.value
            assert isinstance(error, repository.RepositoryError)
            assert (error.pragma, error.expected, error.actual) == ("journal_mode", "wal", "memory")

    asyncio.run(using(":memory:", body))
    assert calls == []


def test_constructor_touches_no_file(tmp_path):
    path = tmp_path / "new.db"

    async def body(repo):
        return None

    asyncio.run(using(path, body))
    assert not path.exists()


def test_write_lock_is_taken_before_work_runs(main_db):
    def work(conn):
        return conn.in_transaction, write_lock_is_free(main_db)

    async def body(repo):
        return await repo.run(work)

    assert asyncio.run(using(main_db, body)) == (True, False)
    assert write_lock_is_free(main_db)


def test_foreign_keys_are_enforced_and_the_whole_command_rolls_back(main_db):
    def work(conn):
        debit_work("E1")(conn)
        conn.execute(
            "INSERT INTO effects (effect_key, account_id, amount, note) VALUES ('E2', 'nobody', 1, 'debit')"
        )

    async def body(repo):
        with pytest.raises(sqlite3.IntegrityError, match="FOREIGN KEY"):
            await repo.run(work)

    asyncio.run(using(main_db, body))
    assert (balance(main_db), effect_count(main_db)) == (START_BALANCE, 0)
    assert write_lock_is_free(main_db)


def test_an_error_from_work_rolls_back_and_propagates_unchanged(main_db):
    error = ValueError("synthetic failure")

    def work(conn):
        debit_work("E1")(conn)
        raise error

    async def body(repo):
        with pytest.raises(ValueError) as caught:
            await repo.run(work, effect=key("E1"))
        assert caught.value is error
        return await repo.run(debit_work("E2"))

    assert asyncio.run(using(main_db, body)) == "applied"
    assert query(main_db, key("E1")) is None
    assert balance(main_db) == START_BALANCE - DEBIT


@pytest.mark.parametrize("statement", ["COMMIT", "ROLLBACK"])
def test_work_that_ends_the_transaction_itself_is_refused(main_db, statement):
    def work(conn):
        conn.execute("UPDATE counter SET n = n + 1 WHERE id = 1")
        conn.execute(statement)

    async def body(repo):
        with pytest.raises(repository.TransactionOwnershipError) as caught:
            await repo.run(work)
        assert isinstance(caught.value, repository.RepositoryError)
        return await repo.run(debit_work("E1"))

    assert asyncio.run(using(main_db, body)) == "applied"
    assert write_lock_is_free(main_db)
    assert balance(main_db) == START_BALANCE - DEBIT


def test_async_work_is_refused_and_nothing_is_written(main_db):
    async def work(conn):
        conn.execute("UPDATE counter SET n = n + 1 WHERE id = 1")

    async def body(repo):
        with pytest.raises(TypeError):
            await repo.run(work)
        return await repo.run(debit_work("E1"))

    assert asyncio.run(using(main_db, body)) == "applied"
    assert scalar(main_db, "SELECT n FROM counter WHERE id = 1") == 0
    assert write_lock_is_free(main_db)


# Bounded thread executor.


def test_work_runs_on_one_worker_thread_one_command_at_a_time(main_db):
    threads = []
    conns = []
    active = {"now": 0, "max": 0}
    lock = threading.Lock()

    def work(conn):
        with lock:
            active["now"] += 1
            active["max"] = max(active["max"], active["now"])
        threads.append(threading.get_ident())
        conns.append(conn)
        time.sleep(0.05)
        conn.execute("UPDATE counter SET n = n + 1 WHERE id = 1")
        with lock:
            active["now"] -= 1

    async def body(repo):
        await asyncio.gather(*(repo.run(work) for _ in range(5)))

    asyncio.run(using(main_db, body))
    assert len(threads) == 5
    assert set(threads) != {threading.get_ident()}
    assert len(set(threads)) == 1
    assert all(conn is conns[0] for conn in conns)
    assert active["max"] == 1
    assert scalar(main_db, "SELECT n FROM counter WHERE id = 1") == 5


def test_blocking_work_does_not_block_the_event_loop(main_db):
    def work(conn):
        time.sleep(0.3)
        return "done"

    async def ticker(stop):
        ticks = 0
        while not stop.is_set():
            await asyncio.sleep(0.01)
            ticks += 1
        return ticks

    async def body(repo):
        stop = asyncio.Event()
        ticks = asyncio.create_task(ticker(stop))
        result = await repo.run(work)
        stop.set()
        return result, await ticks

    result, ticks = asyncio.run(using(main_db, body))
    assert result == "done"
    assert ticks >= 5


# Busy overload.


def test_busy_overload_surfaces_as_a_typed_error_without_running_work(main_db):
    calls = []

    async def body(repo):
        await repo.run(lambda conn: None)
        with closing(
            sqlite3.connect(main_db, isolation_level=None, check_same_thread=False)
        ) as holder:
            holder.execute("BEGIN IMMEDIATE")
            started = time.monotonic()
            with pytest.raises(repository.RepositoryBusy) as caught:
                await repo.run(lambda conn: calls.append(conn), effect=key("E1"))
            waited = time.monotonic() - started
            holder.execute("ROLLBACK")
        assert isinstance(caught.value, repository.RepositoryError)
        assert caught.value.attempts == 3
        assert waited >= 0.25
        return await repo.run(debit_work("E2"))

    assert asyncio.run(using(main_db, body, busy_timeout_s=0.1, busy_retries=2)) == "applied"
    assert calls == []
    assert balance(main_db) == START_BALANCE - DEBIT


def test_busy_retries_wait_out_a_short_lock(main_db):
    calls = []

    async def body(repo):
        await repo.run(lambda conn: None)
        with closing(
            sqlite3.connect(main_db, isolation_level=None, check_same_thread=False)
        ) as holder:
            holder.execute("BEGIN IMMEDIATE")
            release = threading.Timer(0.3, lambda: holder.execute("ROLLBACK"))
            release.start()
            try:
                started = time.monotonic()
                result = await repo.run(debit_work("E1", calls))
                waited = time.monotonic() - started
            finally:
                release.join()
        return result, waited

    result, waited = asyncio.run(using(main_db, body, busy_timeout_s=0.1, busy_retries=20))
    assert result == "applied"
    assert waited >= 0.25
    assert calls == ["E1"]
    assert balance(main_db) == START_BALANCE - DEBIT


# Indeterminate commit.


def test_indeterminate_commit_that_landed_is_found_not_retried(main_db):
    connect, state = failing_commit_connect(applies=True)
    calls = []
    conns = []

    def tracked(work):
        def wrapper(conn):
            conns.append(conn)
            return work(conn)

        return wrapper

    async def body(repo):
        with pytest.raises(repository.IndeterminateCommit) as caught:
            await repo.run(tracked(debit_work("E1", calls)), effect=key("E1"))
        error = caught.value
        assert isinstance(error, repository.RepositoryError)
        assert error.effect == key("E1")
        assert isinstance(error.__cause__, sqlite3.OperationalError)
        assert (calls, state["commits"]) == (["E1"], 1)
        assert await repo.query_effect(error.effect) == debit_row("E1")
        assert await repo.run(tracked(lambda conn: "next")) == "next"

    asyncio.run(using(main_db, body, connect=connect))
    assert len(conns) == 2 and conns[1] is not conns[0]
    assert calls == ["E1"]
    assert (balance(main_db), effect_count(main_db)) == (START_BALANCE - DEBIT, 1)


def test_indeterminate_commit_that_did_not_land_is_discarded_never_committed_later(main_db):
    connect, state = failing_commit_connect(applies=False)
    calls = []
    conns = []

    def tracked(work):
        def wrapper(conn):
            conns.append(conn)
            return work(conn)

        return wrapper

    async def body(repo):
        with pytest.raises(repository.IndeterminateCommit) as caught:
            await repo.run(tracked(debit_work("E1", calls)), effect=key("E1"))
        assert caught.value.effect == key("E1")
        assert write_lock_is_free(main_db)
        assert await repo.query_effect(key("E1")) is None
        assert (calls, state["commits"]) == (["E1"], 1)
        return await repo.run(tracked(debit_work("E2", calls)), effect=key("E2"))

    assert asyncio.run(using(main_db, body, connect=connect)) == "applied"
    assert len(conns) == 2 and conns[1] is not conns[0]
    assert calls == ["E1", "E2"]
    assert query(main_db, key("E1")) is None
    assert query(main_db, key("E2")) == debit_row("E2")
    assert (balance(main_db), effect_count(main_db)) == (START_BALANCE - DEBIT, 1)


# Effect queries.


def test_query_effect_reads_by_unique_key_or_primary_key(main_db):
    async def body(repo):
        await repo.run(debit_work("E1"))
        return (
            await repo.query_effect(key("E1")),
            await repo.query_effect(key("missing")),
            await repo.query_effect(repository.EffectKey("accounts", "account_id", "acct")),
            await repo.query_effect(repository.EffectKey("counter", "id", 1)),
        )

    assert asyncio.run(using(main_db, body)) == (
        debit_row("E1"),
        None,
        {"account_id": "acct", "balance": START_BALANCE - DEBIT},
        {"id": 1, "n": 0},
    )


@pytest.mark.parametrize(
    "table, column",
    [
        ("effects", "note"),
        ("effects", "amount"),
        ("nothing_here", "effect_key"),
        ("effects; DROP TABLE accounts", "effect_key"),
        ("effects", "effect_key = effect_key OR 1"),
        ("odd-name", "k"),
        ("odd_columns", "odd key"),
    ],
)
def test_query_effect_refuses_names_that_are_not_plain_unique_keys(main_db, table, column):
    async def body(repo):
        with pytest.raises(ValueError):
            await repo.query_effect(repository.EffectKey(table, column, "debit"))

    asyncio.run(using(main_db, body))
    assert balance(main_db) == START_BALANCE
