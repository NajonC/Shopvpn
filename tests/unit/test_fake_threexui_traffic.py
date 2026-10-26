"""Traffic counters and collector of the fake 3x-UI panel (tasks.md T009; GA-MAN-002).

The fake copies v3.9.0's collector: every 5 s it reads Xray's cumulative
per-client counters without resetting them and adds the change to the panel's
stored totals. The first pass after the collector starts only records a
baseline, a counter lower than its last value counts from zero, and restarts,
resets, restores and recreation show up as lower stored totals.
"""

import asyncio

import pytest

from tests._harness.clock import FakeClock
from tests._harness.fake_threexui import (
    COLLECTOR_INTERVAL_MS,
    FakeNotModelled,
    FakeThreeXUIPanel,
)
from tests._harness.fixtures import six_node_fixture

US, DE, RU = "ali_sub1_us", "ali_sub1_de", "ali_sub1_ru"


def _panel():
    fixture = six_node_fixture()
    clock = FakeClock()
    panel = FakeThreeXUIPanel(fixture, "A", clock)
    panel.seed_subscription(fixture, "ali-1")
    return fixture, clock, panel


def _ready():
    """A panel whose first collector pass (the baseline) has already run."""
    fixture, clock, panel = _panel()
    clock.advance(COLLECTOR_INTERVAL_MS)
    panel.collect_due()
    return fixture, clock, panel


def _totals(panel, email):
    record = panel.traffic(email)
    return (record["up"], record["down"])


def _call(panel, method, path, scope="admin", body=None, query=None):
    return asyncio.run(
        panel.handle(method, path, token=panel.tokens[scope], query=query, body=body)
    )


def _tick(clock, panel):
    clock.advance(COLLECTOR_INTERVAL_MS)
    panel.collect_due()


def test_interval_is_five_seconds():
    assert COLLECTOR_INTERVAL_MS == 5_000


def test_first_pass_is_a_discarded_baseline():
    _, clock, panel = _panel()
    panel.serve(US, up=100, down=1_000)
    _tick(clock, panel)
    assert _totals(panel, US) == (0, 0)
    panel.serve(US, up=10, down=20)
    _tick(clock, panel)
    assert _totals(panel, US) == (10, 20)


def test_counts_appear_only_at_ticks():
    _, clock, panel = _ready()
    panel.serve(US, up=64, down=128)
    clock.advance(COLLECTOR_INTERVAL_MS - 1)
    panel.collect_due()
    assert _totals(panel, US) == (0, 0)
    clock.advance(1)
    panel.collect_due()
    assert _totals(panel, US) == (64, 128)


def test_traffic_served_at_a_tick_instant_counts_at_the_next_tick():
    _, clock, panel = _ready()
    clock.advance(COLLECTOR_INTERVAL_MS)
    panel.serve(US, up=5, down=5)
    assert _totals(panel, US) == (0, 0)
    _tick(clock, panel)
    assert _totals(panel, US) == (5, 5)


def test_api_reads_catch_up_without_an_explicit_collect():
    _, clock, panel = _ready()
    panel.serve(US, up=3, down=4)
    clock.advance(3 * COLLECTOR_INTERVAL_MS)
    obj = _call(panel, "GET", f"/panel/api/clients/traffic/{US}").body["obj"]
    assert (obj["up"], obj["down"]) == (3, 4)
    inbound = _call(panel, "GET", "/panel/api/inbounds/get/1").body["obj"]
    stats = {s["email"]: (s["up"], s["down"]) for s in inbound["clientStats"]}
    assert stats == {US: (3, 4), DE: (0, 0), RU: (0, 0)}
    assert (inbound["up"], inbound["down"]) == (3, 4)


def test_clients_are_counted_separately():
    _, clock, panel = _ready()
    panel.serve(US, up=1, down=2)
    panel.serve(DE, up=30, down=40)
    _tick(clock, panel)
    assert _totals(panel, US) == (1, 2)
    assert _totals(panel, DE) == (30, 40)
    assert _totals(panel, RU) == (0, 0)


def test_idle_ticks_leave_totals_unchanged():
    _, clock, panel = _ready()
    panel.serve(US, up=9, down=9)
    _tick(clock, panel)
    for _ in range(4):
        _tick(clock, panel)
        assert _totals(panel, US) == (9, 9)


def test_disabled_client_keeps_counting():
    _, clock, panel = _ready()
    panel.set_setting("restartXrayOnClientDisable", False)
    _call(panel, "POST", f"/panel/api/clients/update/{US}", body={"email": US, "enable": False})
    panel.serve(US, up=7, down=8)
    _tick(clock, panel)
    assert _totals(panel, US) == (7, 8)
    assert panel.traffic(US)["enable"] is False


def test_xray_only_restart_loses_only_uncollected_traffic():
    _, clock, panel = _ready()
    panel.serve(US, up=100, down=100)
    _tick(clock, panel)
    panel.serve(US, up=7, down=7)
    restarts_before = len(panel.xray_restarts)
    panel.restart("xray")
    assert len(panel.xray_restarts) == restarts_before + 1
    assert _call(panel, "GET", "/panel/api/server/status").body["obj"]["appStats"]["uptime"] == 0
    panel.serve(US, up=3, down=3)
    _tick(clock, panel)
    assert _totals(panel, US) == (103, 103)


def test_panel_only_restart_discards_until_a_new_baseline():
    _, clock, panel = _ready()
    panel.serve(US, up=100, down=100)
    _tick(clock, panel)
    clock.advance(2_000)
    panel.serve(US, up=7, down=7)
    restarts_before = panel.xray_restarts
    panel.restart("panel")
    assert panel.xray_restarts == restarts_before
    panel.serve(US, up=3, down=3)
    clock.advance(COLLECTOR_INTERVAL_MS - 1)
    panel.collect_due()
    clock.advance(1)
    panel.collect_due()
    assert _totals(panel, US) == (100, 100)
    panel.serve(US, up=2, down=2)
    _tick(clock, panel)
    assert _totals(panel, US) == (102, 102)


def test_service_restart_resets_xray_and_the_collector():
    _, clock, panel = _ready()
    panel.serve(US, up=100, down=100)
    _tick(clock, panel)
    panel.serve(US, up=7, down=7)
    restarts_before = len(panel.xray_restarts)
    panel.restart("service")
    assert len(panel.xray_restarts) == restarts_before + 1
    panel.serve(US, up=3, down=3)
    _tick(clock, panel)
    assert _totals(panel, US) == (100, 100)
    panel.serve(US, up=2, down=2)
    _tick(clock, panel)
    assert _totals(panel, US) == (102, 102)


def test_unknown_restart_mode_is_rejected():
    _, _, panel = _ready()
    with pytest.raises(ValueError):
        panel.restart("node")


def test_restart_on_disable_also_restarts_xray_counters():
    _, clock, panel = _ready()
    panel.serve(US, up=50, down=50)
    _tick(clock, panel)
    panel.serve(DE, up=7, down=7)
    _call(panel, "POST", f"/panel/api/clients/update/{US}", body={"email": US, "enable": False})
    panel.serve(DE, up=1, down=1)
    _tick(clock, panel)
    assert _totals(panel, DE) == (1, 1)
    assert _totals(panel, US) == (50, 50)


def test_reset_traffic_zeroes_and_re_enables():
    _, clock, panel = _ready()
    panel.set_setting("restartXrayOnClientDisable", False)
    panel.serve(US, up=10, down=20)
    _tick(clock, panel)
    _call(panel, "POST", f"/panel/api/clients/update/{US}", body={"email": US, "enable": False})
    response = _call(panel, "POST", f"/panel/api/clients/resetTraffic/{US}", scope="node-sync")
    assert response.body == {"success": True, "msg": "", "obj": None}
    assert _totals(panel, US) == (0, 0)
    assert panel.client(US)["enable"] is True
    assert panel.traffic(US)["enable"] is True
    assert _totals(panel, DE) == (0, 0)
    panel.serve(US, up=5, down=6)
    _tick(clock, panel)
    assert _totals(panel, US) == (5, 6)
    inbound = _call(panel, "GET", "/panel/api/inbounds/get/1").body["obj"]
    assert (inbound["up"], inbound["down"]) == (15, 26)


def test_reset_traffic_of_unknown_client_is_not_modelled():
    _, _, panel = _ready()
    with pytest.raises(FakeNotModelled):
        _call(panel, "POST", "/panel/api/clients/resetTraffic/nobody")


def test_update_traffic_sets_each_direction():
    _, clock, panel = _ready()
    panel.serve(US, up=10, down=20)
    _tick(clock, panel)
    response = _call(
        panel,
        "POST",
        f"/panel/api/clients/updateTraffic/{US}",
        body={"upload": 10, "download": 4},
    )
    assert response.body["success"] is True
    assert _totals(panel, US) == (10, 4)
    panel.serve(US, up=1, down=1)
    _tick(clock, panel)
    assert _totals(panel, US) == (11, 5)
    _call(panel, "POST", f"/panel/api/clients/updateTraffic/{US}", body={"download": 2})
    assert _totals(panel, US) == (0, 2)


def test_update_traffic_errors_and_scope():
    _, _, panel = _ready()
    path = f"/panel/api/clients/updateTraffic/{US}"
    bad_type = _call(panel, "POST", path, body={"upload": True, "download": 0})
    assert bad_type.body["msg"] == "Request failed (invalid traffic field: upload)"
    bad_body = _call(panel, "POST", path, body=[1, 2])
    assert bad_body.body["msg"] == "Request failed (invalid traffic body)"
    with pytest.raises(FakeNotModelled):
        _call(panel, "POST", path, body={"upload": -1, "download": 0})
    with pytest.raises(FakeNotModelled):
        _call(panel, "POST", "/panel/api/clients/updateTraffic/nobody", body={"upload": 0})
    refused = _call(panel, "POST", path, scope="node-sync", body={"upload": 0})
    assert refused.status == 403
    assert _totals(panel, US) == (0, 0)


def test_periodic_reset_zeroes_one_client_only():
    _, clock, panel = _ready()
    panel.serve(US, up=10, down=20)
    panel.serve(DE, up=1, down=1)
    _tick(clock, panel)
    panel.periodic_reset(US)
    assert _totals(panel, US) == (0, 0)
    assert _totals(panel, DE) == (1, 1)
    assert panel.traffic(US)["enable"] is True
    inbound = _call(panel, "GET", "/panel/api/inbounds/get/1").body["obj"]
    assert (inbound["up"], inbound["down"]) == (11, 21)
    panel.serve(US, up=4, down=4)
    _tick(clock, panel)
    assert _totals(panel, US) == (4, 4)
    with pytest.raises(KeyError):
        panel.periodic_reset("nobody")


def test_restore_lowers_totals_and_restarts_the_service():
    fixture, clock, panel = _ready()
    panel.serve(US, up=100, down=100)
    _tick(clock, panel)
    saved = panel.snapshot()
    panel.serve(US, up=50, down=50)
    _tick(clock, panel)
    _call(panel, "POST", "/panel/api/clients/add",
          body={"inboundIds": [1], "client": {"email": "late", "id": "11111111-1111-4111-8111-111111111111"}})
    panel.set_setting("restartXrayOnClientDisable", False)
    assert _totals(panel, US) == (150, 150)
    restarts_before = len(panel.xray_restarts)
    panel.restore(saved)
    assert len(panel.xray_restarts) == restarts_before + 1
    assert _totals(panel, US) == (100, 100)
    assert panel.client("late") is None
    assert panel.setting("restartXrayOnClientDisable") is True
    panel.serve(US, up=9, down=9)
    _tick(clock, panel)
    assert _totals(panel, US) == (100, 100)
    panel.serve(US, up=1, down=1)
    _tick(clock, panel)
    assert _totals(panel, US) == (101, 101)


def test_recreated_client_starts_at_zero():
    _, clock, panel = _ready()
    panel.set_setting("restartXrayOnClientDisable", False)
    panel.serve(US, up=10, down=10)
    _tick(clock, panel)
    secret = panel.client(US)["id"]
    _call(panel, "POST", f"/panel/api/clients/del/{US}")
    panel.serve(US, up=99, down=99)
    _call(panel, "POST", "/panel/api/clients/add",
          body={"inboundIds": [1], "client": {"email": US, "id": secret}})
    assert _totals(panel, US) == (0, 0)
    _tick(clock, panel)
    assert _totals(panel, US) == (0, 0)
    panel.serve(US, up=2, down=3)
    _tick(clock, panel)
    assert _totals(panel, US) == (2, 3)


def test_client_added_after_the_baseline_counts_from_zero():
    _, clock, panel = _ready()
    _call(panel, "POST", "/panel/api/clients/add",
          body={"inboundIds": [1], "client": {"email": "new", "id": "22222222-2222-4222-8222-222222222222"}})
    panel.serve("new", up=6, down=7)
    _tick(clock, panel)
    assert _totals(panel, "new") == (6, 7)


def test_serve_validation_and_unknown_clients():
    _, clock, panel = _ready()
    with pytest.raises(ValueError):
        panel.serve(US, up=-1)
    with pytest.raises(TypeError):
        panel.serve(US, down=True)
    with pytest.raises(TypeError):
        panel.serve(US, up=1.5)
    panel.serve("nobody", up=5, down=5)
    _tick(clock, panel)
    assert panel.traffic("nobody") is None
    assert [_totals(panel, e) for e in (US, DE, RU)] == [(0, 0)] * 3


def test_kept_traffic_of_a_deleted_client_stops_growing():
    _, clock, panel = _ready()
    panel.set_setting("restartXrayOnClientDisable", False)
    panel.serve(US, up=10, down=10)
    _tick(clock, panel)
    _call(panel, "POST", f"/panel/api/clients/del/{US}", query={"keepTraffic": "1"})
    panel.serve(US, up=5, down=5)
    _tick(clock, panel)
    assert _totals(panel, US) == (10, 10)


def test_traffic_inspection_returns_a_copy():
    _, _, panel = _ready()
    record = panel.traffic(US)
    record["up"] = 999
    assert panel.traffic(US)["up"] == 0
