"""Stalls and late writes of the fake 3x-UI panel (tasks.md T009; RX-MAN-001).

V-RX-01 on lab replicas of v3.9.0 showed:
- writes to one inbound queue behind each other, with no timeout, and commit
  in send order;
- a write blocked by a database hold applies when the hold ends if that is
  within about 10 s, and otherwise fails with "database is locked" and never
  applies;
- reads keep working during holds, while usage collection stalls;
- a request still applies after its caller has given up, and a create that
  timed out can land after a read-back said "not found";
- a stale update that passed its lookup before a delete never brings the
  client back;
- a held update survives a panel restart.

Time is the FakeClock's; a test "gives up" by cancelling its call.
"""

import asyncio

import pytest

from tests._harness.clock import FakeClock
from tests._harness.fake_threexui import (
    COLLECTOR_INTERVAL_MS,
    DB_LOCKED_AFTER_MS,
    FakeNotModelled,
    FakeThreeXUIPanel,
)
from tests._harness.fixtures import six_node_fixture

US, DE = "ali_sub1_us", "ali_sub1_de"
LOCKED = {"success": False, "msg": "Request failed (database is locked)", "obj": None}
OK = {"success": True, "msg": "", "obj": None}


def _panel(key="A"):
    fixture = six_node_fixture()
    clock = FakeClock()
    panel = FakeThreeXUIPanel(fixture, key, clock)
    panel.seed_subscription(fixture, "ali-1")
    return clock, panel


def _call(panel, method, path, *, body=None, query=None, scope="admin"):
    return panel.handle(method, path, token=panel.tokens[scope], body=body, query=query)


def _set_enable(panel, email, enable):
    return _call(
        panel,
        "POST",
        f"/panel/api/clients/update/{email}",
        body={"email": email, "enable": enable},
    )


async def _settle():
    for _ in range(5):
        await asyncio.sleep(0)


async def _give_up(task):
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task


def test_lock_timeout_constant():
    assert DB_LOCKED_AFTER_MS == 10_300


def test_writes_apply_at_once_without_holds():
    async def scenario():
        _, panel = _panel()
        response = await _set_enable(panel, US, False)
        assert response.body == OK
        assert panel.client(US)["enable"] is False
        assert panel.pending_writes == 0

    asyncio.run(scenario())


def test_reads_work_during_a_database_hold():
    async def scenario():
        _, panel = _panel()
        panel.hold_database()
        listed = asyncio.create_task(_call(panel, "GET", "/panel/api/inbounds/list"))
        traffic = asyncio.create_task(_call(panel, "GET", f"/panel/api/clients/traffic/{US}"))
        await _settle()
        assert listed.done() and listed.result().body["success"] is True
        assert traffic.done() and traffic.result().body["obj"]["email"] == US

    asyncio.run(scenario())


def test_short_hold_applies_the_write_when_it_ends():
    async def scenario():
        clock, panel = _panel()
        panel.hold_database()
        write = asyncio.create_task(_set_enable(panel, US, False))
        await _settle()
        assert not write.done()
        assert panel.pending_writes == 1
        clock.advance(9_100)
        panel.run_due()
        await _settle()
        assert not write.done()
        assert panel.client(US)["enable"] is True
        panel.release_database()
        await _settle()
        assert write.done() and write.result().body == OK
        assert panel.client(US)["enable"] is False
        assert panel.pending_writes == 0

    asyncio.run(scenario())


def test_long_hold_fails_with_database_locked_and_never_applies():
    async def scenario():
        clock, panel = _panel()
        panel.hold_database()
        write = asyncio.create_task(_set_enable(panel, US, False))
        await _settle()
        clock.advance(DB_LOCKED_AFTER_MS - 1)
        panel.run_due()
        await _settle()
        assert not write.done()
        clock.advance(1)
        panel.run_due()
        await _settle()
        assert write.done() and write.result().body == LOCKED
        assert panel.pending_writes == 0
        clock.advance(50_000)
        panel.release_database()
        await _settle()
        assert panel.client(US)["enable"] is True

    asyncio.run(scenario())


def test_write_applies_after_the_caller_gives_up():
    async def scenario():
        clock, panel = _panel()
        panel.hold_database()
        write = asyncio.create_task(_set_enable(panel, US, False))
        await _settle()
        await _give_up(write)
        assert panel.pending_writes == 1
        clock.advance(5_000)
        panel.release_database()
        await _settle()
        assert panel.client(US)["enable"] is False
        assert panel.pending_writes == 0

    asyncio.run(scenario())


def test_queued_writes_on_one_inbound_apply_in_send_order():
    async def scenario():
        clock, panel = _panel()
        panel.stall_inbound(1)
        first = asyncio.create_task(_set_enable(panel, US, False))
        await _settle()
        second = asyncio.create_task(_set_enable(panel, US, True))
        await _settle()
        third = asyncio.create_task(_set_enable(panel, DE, False))
        await _settle()
        assert panel.pending_writes == 3
        clock.advance(62_200)
        panel.run_due()
        await _settle()
        assert not any(task.done() for task in (first, second, third))
        assert panel.client(US)["enable"] is True
        panel.release_inbound(1)
        await _settle()
        assert [task.result().body for task in (first, second, third)] == [OK, OK, OK]
        assert panel.client(US)["enable"] is True
        assert panel.client(DE)["enable"] is False
        assert panel.pending_writes == 0

    asyncio.run(scenario())


def test_other_inbounds_proceed_during_an_inbound_stall():
    async def scenario():
        _, panel = _panel("B")
        panel.stall_inbound(1)
        blocked = asyncio.create_task(_set_enable(panel, "ali_sub1_cdn", False))
        free = asyncio.create_task(_set_enable(panel, "ali_sub1_grpc", False))
        await _settle()
        assert not blocked.done()
        assert free.done() and free.result().body == OK
        assert panel.client("ali_sub1_grpc")["enable"] is False
        assert panel.client("ali_sub1_cdn")["enable"] is True
        panel.release_inbound(1)
        await _settle()
        assert blocked.done() and panel.client("ali_sub1_cdn")["enable"] is False

    asyncio.run(scenario())


def test_lock_timeout_counts_from_reaching_the_database():
    async def scenario():
        clock, panel = _panel()
        panel.stall_inbound(1)
        panel.hold_database()
        write = asyncio.create_task(_set_enable(panel, US, False))
        await _settle()
        clock.advance(20_000)
        panel.run_due()
        await _settle()
        assert not write.done()
        panel.release_inbound(1)
        clock.advance(DB_LOCKED_AFTER_MS - 1)
        panel.run_due()
        await _settle()
        assert not write.done()
        clock.advance(1)
        panel.run_due()
        await _settle()
        assert write.result().body == LOCKED
        assert panel.client(US)["enable"] is True

    asyncio.run(scenario())


def test_timed_out_create_lands_after_a_read_back_said_not_found():
    async def scenario():
        clock, panel = _panel()
        panel.hold_database()
        create = asyncio.create_task(
            _call(
                panel,
                "POST",
                "/panel/api/clients/add",
                body={
                    "inboundIds": [1],
                    "client": {"email": "late", "id": "33333333-3333-4333-8333-333333333333"},
                },
            )
        )
        await _settle()
        await _give_up(create)
        read_back = await _call(panel, "GET", "/panel/api/clients/traffic/late")
        assert read_back.body == {"success": True, "msg": "", "obj": None}
        listed = await _call(panel, "GET", "/panel/api/inbounds/get/1")
        assert "late" not in [c["email"] for c in listed.body["obj"]["settings"]["clients"]]
        clock.advance(9_000)
        panel.release_database()
        await _settle()
        assert panel.client("late")["id"] == "33333333-3333-4333-8333-333333333333"
        assert panel.traffic("late")["up"] == 0

    asyncio.run(scenario())


def test_stale_update_after_delete_never_recreates():
    async def scenario():
        _, panel = _panel()
        panel.set_setting("restartXrayOnClientDisable", False)
        panel.stall_inbound(1)
        delete = asyncio.create_task(_call(panel, "POST", f"/panel/api/clients/del/{US}"))
        await _settle()
        stale = asyncio.create_task(_set_enable(panel, US, True))
        await _settle()
        panel.release_inbound(1)
        await _settle()
        assert delete.result().body == OK
        assert stale.result().body == {
            "success": False,
            "msg": "Request failed (record not found)",
            "obj": None,
        }
        assert panel.client(US) is None
        assert panel.traffic(US) is None
        after = await _set_enable(panel, US, True)
        assert after.body["msg"] == "Request failed (record not found)"
        assert panel.client(US) is None

    asyncio.run(scenario())


def _ready_with_traffic():
    clock, panel = _panel()
    clock.advance(COLLECTOR_INTERVAL_MS)
    panel.run_due()
    return clock, panel


def test_short_hold_delays_collection_without_loss():
    async def scenario():
        clock, panel = _ready_with_traffic()
        panel.hold_database()
        panel.serve(US, up=10, down=10)
        clock.advance(COLLECTOR_INTERVAL_MS)
        panel.run_due()
        clock.advance(1_000)
        assert panel.traffic(US)["up"] == 0
        panel.release_database()
        assert panel.traffic(US)["up"] == 10

    asyncio.run(scenario())


def test_long_hold_loses_usage_collected_more_than_the_timeout_before_release():
    async def scenario():
        clock, panel = _ready_with_traffic()
        panel.hold_database()
        panel.serve(US, up=10, down=10)
        panel.serve(DE, up=4, down=4)
        clock.advance(47_000)
        panel.run_due()
        assert panel.traffic(US)["up"] == 0
        panel.serve(US, up=7, down=7)
        clock.advance(8_000)
        panel.run_due()
        panel.release_database()
        assert (panel.traffic(US)["up"], panel.traffic(US)["down"]) == (7, 7)
        assert panel.traffic(DE)["up"] == 0
        panel.serve(US, up=1, down=1)
        clock.advance(COLLECTOR_INTERVAL_MS)
        panel.run_due()
        assert panel.traffic(US)["up"] == 8

    asyncio.run(scenario())


def test_held_response_applies_but_never_returns():
    async def scenario():
        _, panel = _panel()
        panel.set_setting("restartXrayOnClientDisable", False)
        panel.hold_responses()
        write = asyncio.create_task(_set_enable(panel, US, False))
        read = asyncio.create_task(_call(panel, "GET", "/panel/api/inbounds/list"))
        await _settle()
        assert not write.done() and not read.done()
        assert panel.client(US)["enable"] is False
        await _give_up(write)
        panel.release_responses()
        await _settle()
        assert read.done() and read.result().body["success"] is True
        assert panel.pending_writes == 0

    asyncio.run(scenario())


def test_api_down_refuses_calls_and_held_writes_survive_a_panel_restart():
    async def scenario():
        clock, panel = _panel()
        panel.set_setting("restartXrayOnClientDisable", False)
        panel.hold_database()
        write = asyncio.create_task(_set_enable(panel, US, False))
        await _settle()
        await _give_up(write)
        calls_before = len(panel.calls)
        panel.api_down()
        with pytest.raises(ConnectionRefusedError):
            await _call(panel, "GET", "/panel/api/inbounds/list")
        assert len(panel.calls) == calls_before
        panel.restart("panel")
        clock.advance(9_000)
        panel.api_up()
        panel.release_database()
        await _settle()
        assert panel.client(US)["enable"] is False
        listed = await _call(panel, "GET", "/panel/api/inbounds/list")
        assert listed.status == 200

    asyncio.run(scenario())


def test_refused_scope_is_answered_at_once_during_a_hold():
    async def scenario():
        _, panel = _panel()
        panel.hold_database()
        refused = await _call(
            panel,
            "POST",
            f"/panel/api/clients/updateTraffic/{US}",
            body={"upload": 0},
            scope="node-sync",
        )
        assert refused.status == 403
        assert panel.pending_writes == 0

    asyncio.run(scenario())


def test_deferred_unmodelled_write_fails_loudly():
    async def waiting_caller():
        _, panel = _panel("B")
        panel.hold_database()
        create = asyncio.create_task(
            _call(
                panel,
                "POST",
                "/panel/api/clients/add",
                body={"inboundIds": [2], "client": {"email": "no-password"}},
            )
        )
        await _settle()
        panel.release_database()
        await _settle()
        with pytest.raises(FakeNotModelled):
            create.result()

    async def abandoned_caller():
        _, panel = _panel("B")
        panel.hold_database()
        create = asyncio.create_task(
            _call(
                panel,
                "POST",
                "/panel/api/clients/add",
                body={"inboundIds": [2], "client": {"email": "no-password"}},
            )
        )
        await _settle()
        await _give_up(create)
        with pytest.raises(FakeNotModelled):
            panel.release_database()

    asyncio.run(waiting_caller())
    asyncio.run(abandoned_caller())


def test_restore_with_pending_writes_is_not_modelled():
    async def scenario():
        _, panel = _panel()
        saved = panel.snapshot()
        panel.hold_database()
        write = asyncio.create_task(_set_enable(panel, US, False))
        await _settle()
        with pytest.raises(FakeNotModelled):
            panel.restore(saved)
        await _give_up(write)

    asyncio.run(scenario())


def test_hold_and_stall_misuse():
    _, panel = _panel()
    with pytest.raises(RuntimeError):
        panel.release_database()
    panel.hold_database()
    with pytest.raises(RuntimeError):
        panel.hold_database()
    with pytest.raises(KeyError):
        panel.stall_inbound(99)
    panel.stall_inbound(1)
    with pytest.raises(RuntimeError):
        panel.stall_inbound(1)
    panel.release_inbound(1)
    with pytest.raises(RuntimeError):
        panel.release_inbound(1)
    with pytest.raises(KeyError):
        panel.release_inbound(99)
    with pytest.raises(RuntimeError):
        panel.release_responses()
    panel.hold_responses()
    with pytest.raises(RuntimeError):
        panel.hold_responses()


def test_collect_due_is_run_due():
    clock, panel = _panel()
    panel.serve(US, up=1, down=1)
    clock.advance(2 * COLLECTOR_INTERVAL_MS)
    panel.collect_due()
    panel.serve(US, up=2, down=2)
    clock.advance(COLLECTOR_INTERVAL_MS)
    panel.run_due()
    assert panel.traffic(US)["up"] == 2
