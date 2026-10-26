"""Spawned, guarded processes for SQLite concurrency and crash tests.

Each child has its own process, SQLite connections, crash plan, and copy of the
fake clock. Children are guarded like the test process. Armed crash points are
reported over a pipe before the child exits immediately, leaving SQLite to
keep only committed work; a restart is another call with the same files and
clock.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Sequence
from dataclasses import dataclass
import math
import multiprocessing
from multiprocessing.connection import Connection, wait as wait_connections
import os
from pathlib import Path
import time
import traceback
from typing import Any

from tests._harness import network_guard
from tests._harness.clock import FakeClock
from tests._harness.crash import CrashPlan, _install_child_reporter


@dataclass(frozen=True)
class ChildContext:
    index: int
    count: int
    lab_root: Path
    crash: CrashPlan
    clock: FakeClock | None


@dataclass(frozen=True)
class ChildResult:
    index: int
    exit_code: int
    crashed_at: str | None
    reached: tuple[str, ...]
    value: object
    error_type: str | None
    error: str | None
    clock: FakeClock | None


def _child_bootstrap(
    index: int,
    count: int,
    lab_root: str,
    target: Callable[..., object],
    args: tuple[object, ...],
    plan: CrashPlan | None,
    clock: FakeClock | None,
    barrier: Any,
    timeout_s: float,
    report_connection: Connection,
) -> None:
    """Set up the child guard and report its target's outcome to the parent."""
    try:
        network_guard._state.install()
        network_guard._state.lab_roots = {os.path.realpath(lab_root)}

        def report_point(point: str, crashed: bool) -> None:
            report_connection.send(("point", point, crashed))

        _install_child_reporter(report_point)
        context = ChildContext(
            index=index,
            count=count,
            lab_root=Path(os.path.realpath(lab_root)),
            crash=plan if plan is not None else CrashPlan(),
            clock=clock,
        )
        barrier.wait(timeout=timeout_s)
        value = target(context, *args)
        report_connection.send(("return", value, context.clock))
    except BaseException as exc:
        try:
            report_connection.send(
                (
                    "error",
                    type(exc).__name__,
                    "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
                    str(exc),
                )
            )
        except BaseException:
            pass
        raise SystemExit(1)
    finally:
        _install_child_reporter(None)
        report_connection.close()


def _real_path_is_within(path: str, root: str) -> bool:
    try:
        return os.path.commonpath((root, path)) == root
    except ValueError:
        return False


def _validate_inputs(
    count: int,
    lab_root: Path | str,
    plans: Sequence[CrashPlan | None] | None,
) -> tuple[str, tuple[CrashPlan | None, ...] | None]:
    if not isinstance(count, int) or isinstance(count, bool):
        raise TypeError("count must be an int")
    if count < 1:
        raise ValueError("count must be >= 1")

    if plans is not None:
        if not isinstance(plans, Sequence) or isinstance(plans, (str, bytes)):
            raise ValueError("plans must be a sequence of CrashPlan or None")
        if len(plans) != count:
            raise ValueError("plans must have one item per child")
        copied_plans = tuple(plans)
        if any(plan is not None and not isinstance(plan, CrashPlan) for plan in copied_plans):
            raise ValueError("each plan must be a CrashPlan or None")
    else:
        copied_plans = None

    try:
        path = os.fspath(lab_root)
    except TypeError as exc:
        raise ValueError("lab_root must be a path to an existing directory") from exc
    if not isinstance(path, str):
        raise ValueError("lab_root must be a path to an existing directory")
    real_lab_root = os.path.realpath(path)
    if not os.path.isdir(real_lab_root):
        raise ValueError("lab_root must be an existing directory")
    guard_roots = tuple(os.path.realpath(root) for root in network_guard._state.lab_roots)
    if not guard_roots or not any(
        _real_path_is_within(real_lab_root, guard_root) for guard_root in guard_roots
    ):
        raise ValueError("lab_root must be inside a current network guard lab root")
    return real_lab_root, copied_plans


def _check_timeout(timeout_s: float) -> float:
    if isinstance(timeout_s, bool) or not isinstance(timeout_s, (int, float)):
        raise TypeError("timeout_s must be a positive number")
    if not math.isfinite(timeout_s) or timeout_s <= 0:
        raise ValueError("timeout_s must be finite and > 0")
    return float(timeout_s)


def run_processes(
    target: Callable[..., object],
    *,
    count: int,
    lab_root: Path | str,
    args: Sequence[object] = (),
    plans: Sequence[CrashPlan | None] | None = None,
    clock: FakeClock | None = None,
    timeout_s: float = 30.0,
) -> tuple[ChildResult, ...]:
    """Run ``target`` in guarded spawned children, starting them together.

    The target and all values passed between parent and child must be
    picklable, and targets must be module-level functions. Children use real
    processes and SQLite locks; the parent drains each pipe while they run so
    even a child terminated with ``os._exit`` can report its crash point.
    """
    real_lab_root, copied_plans = _validate_inputs(count, lab_root, plans)
    checked_timeout = _check_timeout(timeout_s)
    child_args = tuple(args)

    mp_context = multiprocessing.get_context("spawn")
    barrier = mp_context.Barrier(count)
    processes: list[multiprocessing.Process] = []
    receivers: list[Connection] = []
    receiver_indexes: dict[Connection, int] = {}
    states: list[dict[str, Any]] = [
        {
            "reached": [],
            "crashed_at": None,
            "returned": False,
            "value": None,
            "clock": None,
            "error_type": None,
            "error": None,
            "message": None,
        }
        for _ in range(count)
    ]
    open_indexes: set[int] = set()
    start_time = time.monotonic()

    try:
        for index in range(count):
            receive_connection, send_connection = mp_context.Pipe(duplex=False)
            process = mp_context.Process(
                target=_child_bootstrap,
                args=(
                    index,
                    count,
                    real_lab_root,
                    target,
                    child_args,
                    None if copied_plans is None else copied_plans[index],
                    clock,
                    barrier,
                    checked_timeout,
                    send_connection,
                ),
            )
            try:
                process.start()
            except BaseException:
                receive_connection.close()
                send_connection.close()
                raise
            send_connection.close()
            processes.append(process)
            receivers.append(receive_connection)
            receiver_indexes[receive_connection] = index
            open_indexes.add(index)

        deadline = start_time + checked_timeout
        while open_indexes:
            open_connections = [receivers[index] for index in open_indexes]
            ready_connections = wait_connections(open_connections, timeout=0.02)
            for connection in ready_connections:
                index = receiver_indexes[connection]
                while connection.poll(0):
                    try:
                        message = connection.recv()
                    except EOFError:
                        open_indexes.discard(index)
                        break
                    kind = message[0]
                    state = states[index]
                    if kind == "point":
                        _, point, crashed = message
                        state["reached"].append(point)
                        if crashed:
                            state["crashed_at"] = point
                    elif kind == "return":
                        _, value, child_clock = message
                        state["returned"] = True
                        state["value"] = value
                        state["clock"] = child_clock
                    elif kind == "error":
                        _, error_type, error, message_text = message
                        state["error_type"] = error_type
                        state["error"] = error
                        state["message"] = message_text
                    else:
                        raise RuntimeError(f"unknown child report: {kind!r}")

            if any(process.is_alive() for process in processes) and time.monotonic() >= deadline:
                for process in processes:
                    if process.is_alive():
                        process.kill()
                for process in processes:
                    process.join()
                raise TimeoutError(f"child process did not finish within {checked_timeout} seconds")

        for process in processes:
            process.join()

        results = tuple(
            ChildResult(
                index=index,
                exit_code=process.exitcode if process.exitcode is not None else 1,
                crashed_at=state["crashed_at"],
                reached=tuple(state["reached"]),
                value=state["value"] if state["returned"] else None,
                error_type=state["error_type"],
                error=state["error"],
                clock=state["clock"] if state["returned"] else None,
            )
            for index, (process, state) in enumerate(zip(processes, states))
        )
        network_failure = next(
            (
                state["message"]
                for state in states
                if state["error_type"] == "NetworkGuardError"
            ),
            None,
        )
    finally:
        for process in processes:
            if process.is_alive():
                process.kill()
            process.join()
            process.close()
        for connection in receivers:
            connection.close()

    if network_failure is not None:
        raise network_guard.NetworkGuardError(network_failure)
    return results


async def run_processes_async(
    target: Callable[..., object],
    *,
    count: int,
    lab_root: Path | str,
    args: Sequence[object] = (),
    plans: Sequence[CrashPlan | None] | None = None,
    clock: FakeClock | None = None,
    timeout_s: float = 30.0,
) -> tuple[ChildResult, ...]:
    """Run :func:`run_processes` in a worker thread."""
    return await asyncio.to_thread(
        run_processes,
        target,
        count=count,
        lab_root=lab_root,
        args=args,
        plans=plans,
        clock=clock,
        timeout_s=timeout_s,
    )
