"""Unit tests for the controllable test clock."""

import time
import pytest

from tests._harness.clock import (
    DEFAULT_MONOTONIC_START_MS,
    DEFAULT_WALL_START_MS,
    FakeClock,
)

W = DEFAULT_WALL_START_MS
M = DEFAULT_MONOTONIC_START_MS


def test_defaults() -> None:
    clock = FakeClock()
    assert clock.now_ms() == W == 1_767_225_600_000
    assert clock.true_now_ms() == W
    assert clock.monotonic_ms() == M == 1_000_000
    assert clock.drift_ppm() == 0
    assert type(clock.now_ms()) is int
    assert type(clock.true_now_ms()) is int
    assert type(clock.monotonic_ms()) is int


def test_custom_start() -> None:
    clock = FakeClock(wall_start_ms=5_000, monotonic_start_ms=7)
    assert clock.now_ms() == 5_000
    assert clock.true_now_ms() == 5_000
    assert clock.monotonic_ms() == 7


def test_advance_moves_all_three() -> None:
    clock = FakeClock()
    clock.advance(1_500)
    assert clock.now_ms() == W + 1_500
    assert clock.true_now_ms() == W + 1_500
    assert clock.monotonic_ms() == M + 1_500

    clock.advance(0)
    assert clock.now_ms() == W + 1_500
    assert clock.true_now_ms() == W + 1_500
    assert clock.monotonic_ms() == M + 1_500


def test_advance_rejects_negative() -> None:
    clock = FakeClock()
    with pytest.raises(ValueError):
        clock.advance(-1)
    assert clock.now_ms() == W
    assert clock.true_now_ms() == W
    assert clock.monotonic_ms() == M
    assert clock.drift_ppm() == 0


def test_rejects_non_int_arguments() -> None:
    clock = FakeClock()
    with pytest.raises(TypeError):
        clock.advance(1.5)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        clock.advance(True)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        clock.advance("1")  # type: ignore[arg-type]

    with pytest.raises(TypeError):
        clock.step_wall(1.0)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        clock.step_wall(False)  # type: ignore[arg-type]

    with pytest.raises(TypeError):
        clock.set_drift_ppm(0.5)  # type: ignore[arg-type]

    with pytest.raises(TypeError):
        FakeClock(wall_start_ms=1.0)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        FakeClock(monotonic_start_ms=True)  # type: ignore[arg-type]


def test_regression() -> None:
    clock = FakeClock()
    clock.step_wall(-60_000)
    assert clock.now_ms() == W - 60_000
    assert clock.true_now_ms() == W
    assert clock.monotonic_ms() == M

    clock.advance(1_000)
    assert clock.now_ms() == W - 59_000
    assert clock.true_now_ms() == W + 1_000
    assert clock.monotonic_ms() == M + 1_000


def test_forward_jump() -> None:
    clock = FakeClock()
    clock.step_wall(3_600_000)
    assert clock.now_ms() == W + 3_600_000
    assert clock.true_now_ms() == W
    assert clock.monotonic_ms() == M

    clock.step_wall(0)
    assert clock.now_ms() == W + 3_600_000
    assert clock.true_now_ms() == W
    assert clock.monotonic_ms() == M


def test_fast_drift() -> None:
    clock = FakeClock()
    clock.set_drift_ppm(500_000)
    clock.advance(1_000)
    assert clock.now_ms() == W + 1_500
    assert clock.true_now_ms() == W + 1_000
    assert clock.monotonic_ms() == M + 1_000


def test_slow_drift() -> None:
    clock = FakeClock()
    clock.set_drift_ppm(-250_000)
    clock.advance(4_000)
    assert clock.now_ms() == W + 3_000
    assert clock.monotonic_ms() == M + 4_000


def test_drift_fraction_is_exact() -> None:
    clock = FakeClock()
    clock.set_drift_ppm(1)
    clock.advance(999_999)
    assert clock.now_ms() == W + 999_999

    clock.advance(1)
    assert clock.now_ms() == W + 1_000_001
    assert clock.monotonic_ms() == M + 1_000_000


def test_negative_drift_fraction() -> None:
    clock = FakeClock()
    clock.set_drift_ppm(-1)
    clock.advance(1)
    assert clock.now_ms() == W

    clock.advance(999_999)
    assert clock.now_ms() == W + 999_999


def test_frozen_wall_and_drift_limit() -> None:
    clock = FakeClock()
    clock.set_drift_ppm(-1_000_000)
    clock.advance(5_000)
    assert clock.now_ms() == W
    assert clock.monotonic_ms() == M + 5_000

    with pytest.raises(ValueError):
        clock.set_drift_ppm(-1_000_001)
    assert clock.drift_ppm() == -1_000_000


def test_drift_back_to_zero() -> None:
    clock = FakeClock()
    clock.set_drift_ppm(500_000)
    clock.advance(1_000)
    clock.set_drift_ppm(0)
    clock.advance(1_000)
    assert clock.now_ms() == W + 2_500
    assert clock.drift_ppm() == 0


def test_resync() -> None:
    clock = FakeClock()
    clock.step_wall(-30_000)
    clock.set_drift_ppm(100_000)
    clock.advance(10_000)
    assert clock.now_ms() == W - 19_000

    clock.resync()
    assert clock.now_ms() == W + 10_000 == clock.true_now_ms()
    assert clock.drift_ppm() == 0
    assert clock.monotonic_ms() == M + 10_000

    clock.advance(1_000)
    assert clock.now_ms() == W + 11_000


def test_resync_clears_accumulator() -> None:
    clock = FakeClock()
    clock.set_drift_ppm(1)
    clock.advance(999_999)
    clock.resync()
    clock.set_drift_ppm(1)
    clock.advance(1)
    assert clock.now_ms() == W + 1_000_000


def test_clocks_are_independent() -> None:
    clock1 = FakeClock()
    clock2 = FakeClock()
    clock1.advance(5_000)
    assert clock2.now_ms() == W
    assert clock2.true_now_ms() == W
    assert clock2.monotonic_ms() == M
    assert clock2.drift_ppm() == 0


def test_reads_no_system_clock(monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("System clock read detected")

    monkeypatch.setattr(time, "time", forbidden)
    monkeypatch.setattr(time, "time_ns", forbidden)
    monkeypatch.setattr(time, "monotonic", forbidden)
    monkeypatch.setattr(time, "monotonic_ns", forbidden)

    clock = FakeClock()
    clock.now_ms()
    clock.true_now_ms()
    clock.monotonic_ms()
    clock.drift_ppm()
    clock.advance(100)
    clock.step_wall(50)
    clock.set_drift_ppm(10)
    clock.resync()
