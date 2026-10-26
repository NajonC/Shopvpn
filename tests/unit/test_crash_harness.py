"""Named crash points (tasks.md T011; plan.md "Validation and traceability").

Production code will take an optional crash hook and call it with a name
immediately before and after each commit, remote dispatch and remote result
(owner decision 2026-10-26: the hook is passed in, never switched on by
configuration). In the test process an armed point raises SimulatedCrash; in
a harness child process it ends the process at once.
"""

import pickle

import pytest

from tests._harness.crash import CRASH_EXIT_CODE, CrashPlan, SimulatedCrash


def test_crash_exit_code():
    assert CRASH_EXIT_CODE == 86


def test_unarmed_points_are_recorded_and_never_crash():
    plan = CrashPlan()
    for point in ("checkout.commit.before", "checkout.commit.after", "checkout.commit.before"):
        plan(point)
    assert plan.reached == (
        "checkout.commit.before",
        "checkout.commit.after",
        "checkout.commit.before",
    )
    assert plan.crashed_at is None


def test_armed_point_crashes_on_its_first_hit():
    plan = CrashPlan().arm("checkout.commit.after")
    plan("checkout.commit.before")
    with pytest.raises(SimulatedCrash) as crash:
        plan("checkout.commit.after")
    assert crash.value.point == "checkout.commit.after"
    assert plan.crashed_at == "checkout.commit.after"
    assert plan.reached == ("checkout.commit.before", "checkout.commit.after")


def test_hit_counts_from_arming_and_a_point_crashes_once():
    plan = CrashPlan()
    plan("panel.dispatch.after")
    plan.arm("panel.dispatch.after", hit=2)
    plan("panel.dispatch.after")
    with pytest.raises(SimulatedCrash):
        plan("panel.dispatch.after")
    plan("panel.dispatch.after")
    assert plan.reached == ("panel.dispatch.after",) * 4
    assert plan.crashed_at == "panel.dispatch.after"


def test_several_points_can_be_armed():
    plan = CrashPlan().arm("refund.commit.before").arm("panel.result.after")
    with pytest.raises(SimulatedCrash):
        plan("panel.result.after")
    assert plan.crashed_at == "panel.result.after"
    with pytest.raises(SimulatedCrash):
        plan("refund.commit.before")
    assert plan.crashed_at == "refund.commit.before"


def test_simulated_crash_is_not_an_ordinary_exception():
    assert issubclass(SimulatedCrash, BaseException)
    assert not issubclass(SimulatedCrash, Exception)
    plan = CrashPlan().arm("telegram.dispatch.after")
    with pytest.raises(SimulatedCrash):
        try:
            plan("telegram.dispatch.after")
        except Exception:
            pytest.fail("an ordinary except clause caught the simulated crash")


def test_names_and_hits_are_validated():
    plan = CrashPlan()
    for bad in (None, 3, b"x"):
        with pytest.raises(TypeError):
            plan.arm(bad)
        with pytest.raises(TypeError):
            plan(bad)
    with pytest.raises(ValueError):
        plan.arm("")
    with pytest.raises(ValueError):
        plan("")
    for bad in (True, 1.5, "1"):
        with pytest.raises(TypeError):
            plan.arm("x", hit=bad)
    for bad in (0, -1):
        with pytest.raises(ValueError):
            plan.arm("x", hit=bad)
    assert plan.reached == ()


def test_a_pickled_plan_is_an_independent_copy():
    plan = CrashPlan().arm("x", hit=2)
    plan("y")
    copy = pickle.loads(pickle.dumps(plan))
    copy("x")
    with pytest.raises(SimulatedCrash):
        copy("x")
    assert copy.reached == ("y", "x", "x")
    assert plan.reached == ("y",)
    assert plan.crashed_at is None
