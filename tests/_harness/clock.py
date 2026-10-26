"""Controllable test clock with wall, monotonic, and true times."""

DEFAULT_WALL_START_MS = 1_767_225_600_000  # 2026-01-01T00:00:00Z
DEFAULT_MONOTONIC_START_MS = 1_000_000


def _check_int(val: object, name: str) -> int:
    if type(val) is not int:
        raise TypeError(f"{name} must be an int, got {type(val).__name__}")
    return val


class FakeClock:
    """Test clock: UTC epoch-millisecond wall clock plus a separate monotonic clock."""

    def __init__(
        self,
        *,
        wall_start_ms: int = DEFAULT_WALL_START_MS,
        monotonic_start_ms: int = DEFAULT_MONOTONIC_START_MS,
    ) -> None:
        """Initialize FakeClock with initial wall and monotonic start times."""
        _check_int(wall_start_ms, "wall_start_ms")
        _check_int(monotonic_start_ms, "monotonic_start_ms")

        self._true_ms: int = wall_start_ms
        self._wall_ms: int = wall_start_ms
        self._monotonic_ms: int = monotonic_start_ms
        self._drift_ppm: int = 0
        self._drift_acc: int = 0

    def now_ms(self) -> int:
        """Return wall time in UTC epoch milliseconds."""
        return self._wall_ms

    def monotonic_ms(self) -> int:
        """Return monotonic time in milliseconds."""
        return self._monotonic_ms

    def true_now_ms(self) -> int:
        """Return true scenario UTC time in epoch milliseconds."""
        return self._true_ms

    def drift_ppm(self) -> int:
        """Return current drift in parts per million."""
        return self._drift_ppm

    def advance(self, ms: int) -> None:
        """Advance true and monotonic time by ms, updating wall time with drift."""
        _check_int(ms, "ms")
        if ms < 0:
            raise ValueError("ms must be >= 0")

        self._true_ms += ms
        self._monotonic_ms += ms

        self._drift_acc += ms * self._drift_ppm
        whole = self._drift_acc // 1_000_000
        self._wall_ms += ms + whole
        self._drift_acc -= whole * 1_000_000

    def step_wall(self, delta_ms: int) -> None:
        """Jump wall time by delta_ms without changing true or monotonic time."""
        _check_int(delta_ms, "delta_ms")
        self._wall_ms += delta_ms

    def set_drift_ppm(self, ppm: int) -> None:
        """Set wall clock drift in parts per million."""
        _check_int(ppm, "ppm")
        if ppm < -1_000_000:
            raise ValueError("ppm must be >= -1_000_000")
        self._drift_ppm = ppm

    def resync(self) -> None:
        """Restore trusted time: wall time = true time, drift = 0, accumulator = 0."""
        self._wall_ms = self._true_ms
        self._drift_ppm = 0
        self._drift_acc = 0
