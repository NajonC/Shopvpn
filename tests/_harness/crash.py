"""Named crash points for deterministic crash-ordering tests.

Production code receives this hook as an optional argument and calls it at
named commit and remote-operation boundaries. Omitting the hook leaves crash
injection inactive by default; it is never switched on by configuration or
environment. A provided plan records reached point names and triggers only
when a matching point is explicitly armed. Nothing is added to ``composite/``
for this harness.

In the test process a crash is a :class:`SimulatedCrash` exception, so
``finally`` blocks and context managers still run. Only a harness child
process crashes for real, immediately after reporting the crash to its parent.
"""

from __future__ import annotations

import os
from typing import Callable


CRASH_EXIT_CODE = 86


class SimulatedCrash(BaseException):
    """A named crash signal raised in the test process."""

    def __init__(self, point: str) -> None:
        self.point = point
        super().__init__(point)


_ChildReporter = Callable[[str, bool], None]
_child_reporter: _ChildReporter | None = None


def _install_child_reporter(reporter: _ChildReporter | None) -> None:
    """Install the harness-only callback used to report child crash points."""
    global _child_reporter
    _child_reporter = reporter


def _validate_point(point: object) -> str:
    if not isinstance(point, str):
        raise TypeError("point must be a str")
    if point == "":
        raise ValueError("point must not be empty")
    return point


class CrashPlan:
    """Record named points and raise once when an armed point is reached."""

    def __init__(self) -> None:
        self._reached: tuple[str, ...] = ()
        self._armed: dict[str, tuple[int, int]] = {}
        self._crashed_at: str | None = None

    def arm(self, point: str, *, hit: int = 1) -> CrashPlan:
        """Arm ``point`` to crash on its ``hit``-th reach from now."""
        point = _validate_point(point)
        if not isinstance(hit, int) or isinstance(hit, bool):
            raise TypeError("hit must be an int that is not bool")
        if hit < 1:
            raise ValueError("hit must be >= 1")
        self._armed[point] = (hit, 0)
        return self

    def __call__(self, point: str) -> None:
        """Record a point and crash if its armed hit count has been reached."""
        point = _validate_point(point)
        self._reached = (*self._reached, point)

        armed = self._armed.get(point)
        should_crash = False
        if armed is not None:
            hit, reached_since_arming = armed
            reached_since_arming += 1
            if reached_since_arming == hit:
                del self._armed[point]
                self._crashed_at = point
                should_crash = True
            else:
                self._armed[point] = (hit, reached_since_arming)

        reporter = _child_reporter
        if reporter is not None:
            reporter(point, should_crash)

        if should_crash:
            if reporter is not None:
                os._exit(CRASH_EXIT_CODE)
            raise SimulatedCrash(point)

    @property
    def reached(self) -> tuple[str, ...]:
        """The immutable ordered list of reached points."""
        return self._reached

    @property
    def crashed_at(self) -> str | None:
        """The most recently triggered crash point, if any."""
        return self._crashed_at
