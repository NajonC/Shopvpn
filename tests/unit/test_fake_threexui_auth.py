"""Token handling of the fake 3x-UI panel (tasks.md T009; RX-MAN-001 V-RX-01(h)).

The fake follows v3.9.0's API authentication: a Bearer token selects one of
three scopes (admin, node-sync, monitor); unauthenticated calls get 404, a
wrong token 401, and a scope outside its allowlist 403.
"""

import asyncio

import pytest

from tests._harness.clock import FakeClock
from tests._harness.fake_threexui import FakeNotModelled, FakeThreeXUIPanel
from tests._harness.fixtures import six_node_fixture

DENIED = {"success": False, "msg": "this API token is not permitted to access this endpoint"}


def _panel():
    fixture = six_node_fixture()
    panel = FakeThreeXUIPanel(fixture, "A", FakeClock())
    panel.seed_subscription(fixture, "ali-1")
    return fixture, panel


def _call(panel, method, path, scope, body=None, query=None):
    token = panel.tokens[scope] if scope else None
    return asyncio.run(panel.handle(method, path, token=token, query=query, body=body))


def test_tokens_are_distinct_and_admin_is_the_fixture_token():
    fixture, panel = _panel()
    tokens = panel.tokens
    assert set(tokens) == {"admin", "node-sync", "monitor"}
    assert tokens["admin"] == fixture.panel("A").api_token
    assert len(set(tokens.values())) == 3
    second = FakeThreeXUIPanel(fixture, "A", FakeClock())
    assert second.tokens["node-sync"] != tokens["node-sync"]
    assert second.tokens["monitor"] != tokens["monitor"]
    for value in tokens.values():
        assert value not in repr(panel)


def test_missing_token_is_404_and_wrong_token_is_401():
    _, panel = _panel()
    missing = asyncio.run(panel.handle("GET", "/panel/api/inbounds/list"))
    assert (missing.status, missing.body) == (404, None)
    wrong = asyncio.run(panel.handle("GET", "/panel/api/inbounds/list", token="not-a-token"))
    assert (wrong.status, wrong.body) == (401, None)
    outside = _call(panel, "GET", "/login", "admin")
    assert (outside.status, outside.body) == (404, None)
    unknown = _call(panel, "GET", "/panel/api/no/such/route", "admin")
    assert (unknown.status, unknown.body) == (404, None)


def test_admin_reaches_every_modelled_route():
    _, panel = _panel()
    for method, path in [
        ("GET", "/panel/api/inbounds/list"),
        ("GET", "/panel/api/inbounds/get/1"),
        ("GET", "/panel/api/clients/traffic/ali_sub1_us"),
        ("POST", "/panel/api/setting/all"),
        ("GET", "/panel/api/server/status"),
    ]:
        response = _call(panel, method, path, "admin")
        assert response.status == 200, path
        assert response.body["success"] is True, path


@pytest.mark.parametrize(
    "method, path",
    [
        ("POST", "/panel/api/setting/all"),
        ("GET", "/panel/api/inbounds/get/1"),
        ("GET", "/panel/api/clients/traffic/ali_sub1_us"),
        ("GET", "/panel/api/clients/get/ali_sub1_us"),
    ],
)
def test_node_sync_is_refused_settings_and_single_reads(method, path):
    _, panel = _panel()
    response = _call(panel, method, path, "node-sync")
    assert (response.status, response.body) == (403, DENIED)


def test_node_sync_allowlist():
    _, panel = _panel()
    listed = _call(panel, "GET", "/panel/api/inbounds/list", "node-sync")
    assert listed.status == 200 and listed.body["success"] is True
    status = _call(panel, "GET", "/panel/api/server/status", "node-sync")
    assert status.status == 200 and status.body["success"] is True
    deleted = _call(panel, "POST", "/panel/api/clients/del/ali_sub1_us", "node-sync")
    assert deleted.status == 200 and deleted.body["success"] is True
    assert panel.client("ali_sub1_us") is None


@pytest.mark.parametrize(
    "method, path",
    [
        ("GET", "/panel/api/inbounds/list"),
        ("POST", "/panel/api/setting/all"),
        ("GET", "/panel/api/clients/traffic/ali_sub1_us"),
        ("POST", "/panel/api/clients/del/ali_sub1_us"),
    ],
)
def test_monitor_reads_server_status_only(method, path):
    _, panel = _panel()
    allowed = _call(panel, "GET", "/panel/api/server/status", "monitor")
    assert allowed.status == 200
    response = _call(panel, method, path, "monitor")
    assert (response.status, response.body) == (403, DENIED)
    assert panel.client("ali_sub1_us") is not None


def test_refused_write_changes_nothing():
    _, panel = _panel()
    before = panel.inbound_clients(1)
    response = _call(
        panel,
        "POST",
        "/panel/api/clients/update/ali_sub1_us",
        "monitor",
        body={"email": "ali_sub1_us", "enable": False},
    )
    assert response.status == 403
    assert panel.inbound_clients(1) == before


def test_unmodelled_real_route_raises_only_after_the_scope_check():
    _, panel = _panel()
    refused = _call(panel, "POST", "/panel/api/clients/bulkResetTraffic", "node-sync")
    assert (refused.status, refused.body) == (403, DENIED)
    with pytest.raises(FakeNotModelled):
        _call(panel, "POST", "/panel/api/clients/bulkResetTraffic", "admin")


def test_calls_record_scope_without_bodies():
    _, panel = _panel()
    asyncio.run(panel.handle("GET", "/panel/api/inbounds/list"))
    _call(panel, "GET", "/panel/api/inbounds/list", "node-sync")
    _call(panel, "POST", "/panel/api/setting/all", "node-sync")
    _call(panel, "POST", "/panel/api/setting/all", "admin")
    calls = [(c.method, c.path, c.scope) for c in panel.calls]
    assert calls == [
        ("GET", "/panel/api/inbounds/list", None),
        ("GET", "/panel/api/inbounds/list", "node-sync"),
        ("POST", "/panel/api/setting/all", "node-sync"),
        ("POST", "/panel/api/setting/all", "admin"),
    ]
    panel.calls.clear()
    assert len(panel.calls) == 4
