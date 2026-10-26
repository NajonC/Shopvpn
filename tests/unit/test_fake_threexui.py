"""Behaviour tests for the controlled fake 3x-UI panel."""

import asyncio
import uuid

import pytest

from tests._harness.clock import FakeClock
from tests._harness.fake_threexui import (
    EVIDENCE_LABEL,
    FakeNotModelled,
    FakeThreeXUIPanel,
)
from tests._harness.fixtures import six_node_fixture


def _panel(panel_key="A"):
    fixture = six_node_fixture()
    clock = FakeClock()
    return fixture, clock, FakeThreeXUIPanel(fixture, panel_key, clock)


def _call(panel, method, path, *, body=None, query=None):
    return asyncio.run(
        panel.handle(
            method,
            path,
            token=panel.tokens["admin"],
            query=query,
            body=body,
        )
    )


def _seed_ali(panel):
    panel.seed_subscription(six_node_fixture(), "ali-1")


def test_label_and_docstring():
    import tests._harness.fake_threexui as fake_threexui

    assert EVIDENCE_LABEL == "substitute, not evidence"
    assert EVIDENCE_LABEL in fake_threexui.__doc__


def test_inbounds_from_fixture():
    fixture, _, panel_b = _panel("B")
    response = _call(panel_b, "GET", "/panel/api/inbounds/list")
    assert response.body["success"] is True
    inbounds = response.body["obj"]
    assert [item["id"] for item in inbounds] == [1, 2]
    for item in inbounds:
        source = fixture.inbound("B", item["id"])
        assert item["protocol"] == source.protocol
        assert item["port"] == source.listen_port
        assert item["streamSettings"]["network"] == source.transport
        assert item["streamSettings"]["security"] == source.security
        assert item["streamSettings"]["externalProxy"] == [
            {
                "forceTls": "same",
                "dest": proxy.host,
                "port": proxy.port,
                "remark": "",
            }
            for proxy in source.external_proxies
        ]
    assert inbounds[0]["streamSettings"]["wsSettings"] == {
        "path": fixture.inbound("B", 1).ws_path,
        "host": fixture.inbound("B", 1).ws_host,
        "headers": {},
    }
    grpc = inbounds[1]["streamSettings"]["grpcSettings"]
    assert grpc == {
        "serviceName": fixture.inbound("B", 2).grpc_service_name,
        "authority": "",
        "multiMode": False,
    }
    assert "decryption" not in inbounds[1]["settings"]

    clock = FakeClock()
    panel_a = FakeThreeXUIPanel(fixture, "A", clock)
    inbound_a = _call(panel_a, "GET", "/panel/api/inbounds/get/1").body["obj"]
    source_a = fixture.inbound("A", 1)
    assert inbound_a["streamSettings"]["realitySettings"]["settings"][
        "publicKey"
    ] == source_a.reality_public_key
    assert inbound_a["streamSettings"]["realitySettings"]["shortIds"] == [
        source_a.reality_short_id
    ]
    assert inbound_a["settings"]["decryption"] == "none"

    panel_c = FakeThreeXUIPanel(fixture, "C", clock)
    inbound_c = _call(panel_c, "GET", "/panel/api/inbounds/get/1").body["obj"]
    assert "decryption" not in inbound_c["settings"]
    assert inbound_c["streamSettings"]["tcpSettings"] == {
        "header": {"type": "none"}
    }
    assert _call(panel_c, "GET", "/panel/api/inbounds/get/not-an-id").body is None
    missing = _call(panel_c, "GET", "/panel/api/inbounds/get/999")
    assert missing.body == {
        "success": False,
        "msg": "Request failed (record not found)",
        "obj": None,
    }


def test_add_then_read():
    _, _, panel = _panel()
    response = _call(
        panel,
        "POST",
        "/panel/api/clients/add",
        body={
            "inboundIds": [1],
            "client": {"id": str(uuid.uuid4()), "email": "x1", "flow": "xtls-rprx-vision"},
        },
    )
    assert response.body == {"success": True, "msg": "", "obj": None}
    inbound = _call(panel, "GET", "/panel/api/inbounds/get/1").body["obj"]
    assert inbound["settings"]["clients"][0]["email"] == "x1"
    assert inbound["settings"]["clients"][0]["enable"] is True
    traffic = _call(panel, "GET", "/panel/api/clients/traffic/x1").body["obj"]
    assert traffic["up"] == traffic["down"] == 0
    assert traffic["enable"] is True
    assert traffic["inboundId"] == 1


@pytest.mark.parametrize(
    "payload, error",
    [
        (None, "empty payload"),
        ([], "empty payload"),
        ({"inboundIds": [1], "client": {}}, "client email is required"),
        ({"inboundIds": [1], "client": {"email": ""}}, "client email is required"),
        ({"client": {"email": "x"}}, "at least one inbound is required"),
        ({"inboundIds": [], "client": {"email": "x"}}, "at least one inbound is required"),
        ({"inboundIds": [999], "client": {"email": "x"}}, "inbound 999: record not found"),
        (
            {"inboundIds": [1], "client": {"email": "x", "enable": 1}},
            "invalid client field: enable",
        ),
        (
            {"inboundIds": [1], "client": {"email": "x", "totalGB": False}},
            "invalid client field: totalGB",
        ),
        (
            {"inboundIds": [1], "client": {"email": "ali_sub1_us"}},
            "email already in use: ali_sub1_us",
        ),
        (
            {"inboundIds": [1], "client": {"email": "other", "subId": "ali-1"}},
            "subId already in use: ali-1",
        ),
    ],
)
def test_add_errors(payload, error):
    fixture, _, panel = _panel()
    panel.seed_subscription(fixture, "ali-1")
    if error == "subId already in use: ali-1":
        panel.seed_client([1], {"email": "subid-owner", "subId": "ali-1"})
    response = _call(panel, "POST", "/panel/api/clients/add", body=payload)
    assert response.body == {
        "success": False,
        "msg": f"Request failed ({error})",
        "obj": None,
    }
    if error not in {"email already in use: ali_sub1_us", "subId already in use: ali-1"}:
        assert panel.client("x") is None
    assert panel.client("ali_sub1_us") is not None


def test_add_generates_missing_vless_id():
    _, _, panel = _panel()
    _call(
        panel,
        "POST",
        "/panel/api/clients/add",
        body={"inboundIds": [1], "client": {"email": "generated"}},
    )
    assert uuid.UUID(panel.client("generated")["id"]).version == 4


def test_add_trojan_without_password_and_same_subid_readd_are_not_modelled():
    fixture, _, panel = _panel("B")
    with pytest.raises(FakeNotModelled):
        _call(
            panel,
            "POST",
            "/panel/api/clients/add",
            body={"inboundIds": [2], "client": {"email": "trojan-no-password"}},
        )
    panel = FakeThreeXUIPanel(fixture, "A", FakeClock())
    panel.seed_client([1], {"email": "same", "subId": "same-sub"})
    with pytest.raises(FakeNotModelled):
        _call(
            panel,
            "POST",
            "/panel/api/clients/add",
            body={
                "inboundIds": [1],
                "client": {"email": "same", "subId": "same-sub"},
            },
        )


def test_add_with_kept_traffic_record_is_not_modelled():
    fixture, _, panel = _panel()
    panel.seed_subscription(fixture, "ali-1")
    _call(
        panel,
        "POST",
        "/panel/api/clients/del/ali_sub1_us",
        query={"keepTraffic": "1"},
    )
    with pytest.raises(FakeNotModelled):
        _call(
            panel,
            "POST",
            "/panel/api/clients/add",
            body={"inboundIds": [1], "client": {"email": "ali_sub1_us"}},
        )


def test_update_is_absolute():
    fixture, clock, panel = _panel()
    panel.seed_client(
        [1],
        {
            "id": "client-id",
            "email": "ali_sub1_us",
            "subId": "subscription-id",
            "flow": "xtls-rprx-vision",
            "enable": True,
        },
    )
    created_at = panel.client("ali_sub1_us")["created_at"]
    clock.advance(1_000)
    response = _call(
        panel,
        "POST",
        "/panel/api/clients/update/ali_sub1_us",
        body={"email": "ali_sub1_us"},
    )
    assert response.body["success"] is True
    client = panel.client("ali_sub1_us")
    assert client["enable"] is False
    assert client.get("flow", "") == ""
    assert client["id"] == "client-id"
    assert client["subId"] == "subscription-id"
    assert client["created_at"] == created_at
    assert client["updated_at"] == clock.true_now_ms()


def test_update_errors():
    fixture, _, panel = _panel()
    panel.seed_subscription(fixture, "ali-1")
    error_responses = [
        _call(panel, "POST", "/panel/api/clients/update/missing", body={"email": "x"}),
        _call(
            panel,
            "POST",
            "/panel/api/clients/update/ali_sub1_us",
            body={"email": ""},
        ),
        _call(
            panel,
            "POST",
            "/panel/api/clients/update/ali_sub1_us",
            body={"email": "ali_sub1_de"},
        ),
        _call(
            panel,
            "POST",
            "/panel/api/clients/update/ali_sub1_us",
            body={"email": "ali_sub1_us", "enable": 1},
        ),
    ]
    assert [response.body["msg"] for response in error_responses] == [
        "Request failed (record not found)",
        "Request failed (client email is required)",
        "Request failed (email already in use: ali_sub1_de)",
        "Request failed (invalid client field: enable)",
    ]
    with pytest.raises(FakeNotModelled):
        asyncio.run(
            panel.handle(
                "POST",
                "/panel/api/clients/update/ali_sub1_us",
                token=panel.tokens["admin"],
                query={"inboundIds": "1"},
                body={"email": "ali_sub1_us"},
            )
        )


def test_update_leaves_other_clients_untouched():
    fixture, _, panel = _panel()
    panel.seed_subscription(fixture, "ali-1")
    before_de = panel.client("ali_sub1_de")
    before_ru = panel.client("ali_sub1_ru")
    _call(
        panel,
        "POST",
        "/panel/api/clients/update/ali_sub1_us",
        body={"email": "ali_sub1_us", "enable": False},
    )
    assert panel.client("ali_sub1_de") == before_de
    assert panel.client("ali_sub1_ru") == before_ru


def test_missing_client_traffic_is_null():
    _, _, panel = _panel()
    response = _call(panel, "GET", "/panel/api/clients/traffic/nobody")
    assert response.body == {"success": True, "msg": "", "obj": None}


def test_delete():
    fixture, _, panel = _panel()
    panel.seed_subscription(fixture, "ali-1")
    deleted = _call(panel, "POST", "/panel/api/clients/del/ali_sub1_us")
    assert deleted.body["success"] is True
    assert panel.client("ali_sub1_us") is None
    assert "ali_sub1_us" not in [c["email"] for c in panel.inbound_clients(1)]
    assert _call(panel, "GET", "/panel/api/clients/traffic/ali_sub1_us").body["obj"] is None
    again = _call(panel, "POST", "/panel/api/clients/del/ali_sub1_us")
    assert again.body["msg"] == (
        'Request failed (client "ali_sub1_us" not found in any inbound or client record)'
    )

    _call(
        panel,
        "POST",
        "/panel/api/clients/del/ali_sub1_de",
        query={"keepTraffic": "1"},
    )
    assert panel.client("ali_sub1_de") is None
    assert _call(panel, "GET", "/panel/api/clients/traffic/ali_sub1_de").body["obj"] is not None
    kept_again = _call(panel, "POST", "/panel/api/clients/del/ali_sub1_de")
    assert kept_again.body["success"] is False
    assert _call(panel, "GET", "/panel/api/clients/traffic/ali_sub1_de").body["obj"] is not None


def test_restart_on_disable_and_delete_with_setting_on():
    fixture, clock, panel = _panel()
    panel.seed_subscription(fixture, "ali-1")
    assert panel.setting("restartXrayOnClientDisable") is True
    _call(
        panel,
        "POST",
        "/panel/api/clients/update/ali_sub1_us",
        body={"email": "ali_sub1_us", "enable": False},
    )
    _call(panel, "POST", "/panel/api/clients/del/ali_sub1_de")
    assert panel.xray_restarts == (clock.true_now_ms(), clock.true_now_ms())
    assert _call(panel, "GET", "/panel/api/server/status").body["obj"]["appStats"][
        "uptime"
    ] == 0
    clock.advance(5_000)
    assert _call(panel, "GET", "/panel/api/server/status").body["obj"]["appStats"][
        "uptime"
    ] == 5
    _call(
        panel,
        "POST",
        "/panel/api/clients/update/ali_sub1_ru",
        body={"email": "ali_sub1_ru", "enable": True},
    )
    assert len(panel.xray_restarts) == 2


def test_no_restart_with_setting_off():
    fixture, _, panel = _panel()
    panel.seed_subscription(fixture, "ali-1")
    panel.set_setting("restartXrayOnClientDisable", False)
    _call(
        panel,
        "POST",
        "/panel/api/clients/update/ali_sub1_us",
        body={"email": "ali_sub1_us", "enable": False},
    )
    _call(panel, "POST", "/panel/api/clients/del/ali_sub1_de")
    assert panel.xray_restarts == ()


def test_settings_reset():
    _, _, panel = _panel()
    assert _call(panel, "POST", "/panel/api/setting/all").body["obj"][
        "restartXrayOnClientDisable"
    ] is True
    panel.set_setting("restartXrayOnClientDisable", False)
    assert _call(panel, "POST", "/panel/api/setting/all").body["obj"][
        "restartXrayOnClientDisable"
    ] is False
    panel.reset_settings()
    assert _call(panel, "POST", "/panel/api/setting/all").body["obj"] == {
        "restartXrayOnClientDisable": True,
        "webPort": 2053,
        "webBasePath": "/xui/",
    }


def test_seed_subscription_on_each_panel():
    fixture = six_node_fixture()
    clock = FakeClock()
    panels = {
        key: FakeThreeXUIPanel(fixture, key, clock) for key in ("A", "B", "C")
    }
    for panel in panels.values():
        panel.seed_subscription(fixture, "ali-1")
    assert [client["email"] for client in panels["A"].inbound_clients(1)] == [
        "ali_sub1_us",
        "ali_sub1_de",
        "ali_sub1_ru",
    ]
    assert [client["email"] for client in panels["B"].inbound_clients(1)] == [
        "ali_sub1_cdn"
    ]
    grpc_client = panels["B"].inbound_clients(2)[0]
    grpc_credential = next(
        credential
        for credential in fixture.subscription("ali-1").credentials
        if credential.email == "ali_sub1_grpc"
    )
    assert grpc_client["password"] == grpc_credential.secret
    assert "id" not in grpc_client
    direct_client = panels["C"].inbound_clients(1)[0]
    assert direct_client["security"] == "auto"


def test_returned_values_are_copies():
    fixture, _, panel = _panel()
    panel.seed_subscription(fixture, "ali-1")
    returned = panel.client("ali_sub1_us")
    returned["email"] = "changed"
    assert panel.client("ali_sub1_us")["email"] == "ali_sub1_us"
    inbound_clients = panel.inbound_clients(1)
    inbound_clients[0]["email"] = "changed"
    assert panel.client("ali_sub1_us")["email"] == "ali_sub1_us"
    traffic = _call(panel, "GET", "/panel/api/clients/traffic/ali_sub1_us")
    traffic.body["obj"]["email"] = "changed"
    assert _call(panel, "GET", "/panel/api/clients/traffic/ali_sub1_us").body[
        "obj"
    ]["email"] == "ali_sub1_us"
    response = _call(panel, "GET", "/panel/api/inbounds/get/1")
    response.body["obj"]["settings"]["clients"][0]["email"] = "changed"
    assert panel.client("ali_sub1_us")["email"] == "ali_sub1_us"
