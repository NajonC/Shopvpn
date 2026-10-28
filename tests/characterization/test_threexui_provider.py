"""Characterize the legacy 3x-UI provider against the fake 3x-UI panel at commit d16839b.

Baseline: ``.venv/bin/python -m pytest tests/characterization/test_threexui_provider.py --network=deny``.
The substitutes are the fake panel and its HTTPS front (substitute, not evidence), and the loopback stub for responses the fake cannot give.

Known unsafe behaviour pinned here: (a) TLS peer verification is off, so the bearer token goes to a self-signed peer a verifying client refuses (FR-084; cases 1, 2); (b) created clients carry no VLESS flow, even on a Vision inbound (case 6); (c) ``get_user`` takes the first matching export and ignores later copies (case 12); (d) client updates carry no inbound filter: each POST changes every inbound holding the email and is repeated once per inbound (cases 14, 17); (e) a timeout's message loses its fallback text and ends with ``": "`` (case 15); (f) ``update_user`` enables unconditionally (cases 18, 19), turns an unlimited expiry into a limited one when days are added (case 18), substitutes zero usage after a failed read so a carryover keeps the whole old limit (case 22), skips the read when no volume is added (case 23), and ignores the traffic-reset result, which on this panel is a 404, so usage is not reset (cases 20, 21); (g) ``set_enabled`` never reads back (case 25); (h) ``get_user_usage`` reports zero for a missing object or an application-rejected read (FR-034; cases 28, 29); (i) ``delete_user`` checks the HTTP status only (cases 31, 32).
"""

import asyncio
import contextlib
import json
import re
import time
import uuid

import aiohttp
import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer

from panel_providers import threexui_provider
from panel_providers.base import PanelError, PanelUsernameTakenError
from panel_providers.threexui_provider import ThreeXUIProvider
from tests._harness.clock import FakeClock
from tests._harness.fake_threexui import FakeThreeXUIPanel, FakeThreeXUIServer
from tests._harness.fixtures import six_node_fixture

GIB = 1024 ** 3
DAY_MS = 86_400_000
SUB_BASE = "https://sub.example.invalid/sub/"
FAR_EXPIRY_MS = 4_102_444_800_000  # 2100-01-01T00:00:00Z
FROZEN_NOW = 1_700_000_000.5
SEEDED_ID = "22222222-2222-4222-8222-222222222222"
STUB_TOKEN = "synthetic-token"
WRONG_TOKEN = "synthetic-wrong-token"
OK_ENVELOPE = {"success": True, "msg": "", "obj": None}
REJECTED = {"success": False, "msg": "boom", "obj": None}
ZERO_USAGE = {"used_bytes": 0, "data_limit_bytes": 0, "status": "disabled"}
CLIENT_KEYS = ["id", "password", "email", "enable", "expiryTime", "totalGB", "limitIp", "subId", "tgId"]
NOT_FOUND = "کاربری با نام «{}» روی پنل پیدا نشد."
AUTH = "خطا در احراز هویت (کد {}): API Token را بررسی کن."
CONNECT_INBOUND = "خطا در اتصال به پنل (inbound {}): "
TAKEN = "نام کاربری «{}» روی پنل تکراری است"
NOT_CONFIGURED = "این سرور هنوز کامل تنظیم نشده (inbound یا آدرس Subscription خالی است)."
NO_SUB_LINK = "لینک اشتراک این کاربر روی پنل یافت نشد."
UPDATE_REJECTED = "{} ناموفق بود (inbound {}): {}"
LIST = ("GET", "/panel/api/inbounds/list", "admin")
UPDATE_U1 = ("POST", "/panel/api/clients/update/u1", "admin")


def _panel(key="B"):
    fixture = six_node_fixture()
    clock = FakeClock()
    panel = FakeThreeXUIPanel(fixture, key, clock)
    panel.set_setting("restartXrayOnClientDisable", False)
    return fixture, clock, panel


def _row(base_url, token, *, inbound_ids="[1, 2]", inbound_id=None, sub_base=SUB_BASE):
    return {"api_url": base_url + "/", "api_password": token, "xui_inbound_ids": inbound_ids,
            "xui_inbound_id": inbound_id, "xui_sub_base_url": sub_base}


def _use(clock, panel, email, up, down):
    # The collector's first pass only sets a baseline.
    clock.advance(5_000)
    panel.run_due()
    panel.serve(email, up=up, down=down)
    clock.advance(5_000)
    panel.run_due()


def _calls(panel, start=0):
    return [(c.method, c.path, c.scope) for c in panel.calls[start:]]


def _served(server):
    return [(r.method, r.path, r.status) for c in server.connections for r in c.requests]


@contextlib.asynccontextmanager
async def stub_panel(status, body):
    seen = []
    app = web.Application()

    async def answer(request):
        seen.append((request.method, request.path))
        return web.json_response(body, status=status) if body is not None else web.Response(status=status)

    app.router.add_route("*", "/{tail:.*}", answer)
    server = TestServer(app, host="127.0.0.1")
    await server.start_server()
    try:
        yield str(server.make_url("")), seen
    finally:
        await server.close()


def _u1(panel, server):
    return ThreeXUIProvider(_row(server.base_url, panel.tokens["admin"]))


# Case 1
def test_session_settings():
    provider = ThreeXUIProvider(_row("https://panel.example.invalid/xui", STUB_TOKEN))

    async def scenario():
        s1, s2 = provider._session(), provider._session()
        try:
            assert s1 is not s2
            assert s1.connector is not s2.connector
            assert s1.connector._ssl is False  # private attribute of aiohttp 3.14.5
            assert s1.timeout == aiohttp.ClientTimeout(total=20)
            assert dict(s1.headers) == {"Authorization": "Bearer synthetic-token", "Accept": "application/json", "Content-Type": "application/json"}
        finally:
            await s1.close()
            await s2.close()

    asyncio.run(scenario())


# Case 2
def test_unverified_tls_and_one_connection_per_call():
    fixture, clock, panel = _panel()

    async def scenario():
        async with FakeThreeXUIServer(panel) as server:
            provider = _u1(panel, server)
            await provider.create_user("u1", 10, 30)
            await provider.get_user_usage("u1")
            await provider.get_user_usage("u1")
            await server.wait_connections_closed()
            assert [[(r.method, r.path, r.status) for r in c.requests] for c in server.connections] == [
                [("POST", "/xui/panel/api/clients/add", 200)],
                [("GET", "/xui/panel/api/clients/traffic/u1", 200)],
                [("GET", "/xui/panel/api/clients/traffic/u1", 200)],
            ]
            assert all(c.closed_ms is not None for c in server.connections)
            assert all(c.scope == "admin" for c in panel.calls)
            with pytest.raises(aiohttp.ClientConnectorCertificateError):
                async with aiohttp.ClientSession() as verifying:
                    async with verifying.get(server.base_url + "/panel/api/inbounds/list"):
                        pass

    asyncio.run(scenario())


# Case 3
def test_build_client_identity(monkeypatch):
    provider = ThreeXUIProvider(_row("https://panel.example.invalid/xui", STUB_TOKEN))
    monkeypatch.setattr(threexui_provider.time, "time", lambda: FROZEN_NOW)
    client, sub_id = provider._build_client("u1", 10, 30)
    assert list(client) == CLIENT_KEYS
    assert client["id"] == client["password"]
    assert uuid.UUID(client["id"]).version == 4
    assert str(uuid.UUID(client["id"])) == client["id"]
    assert client["email"] == "u1" and client["enable"] is True
    assert client["expiryTime"] == 1_702_592_000_500
    assert client["totalGB"] == 10 * GIB
    assert client["limitIp"] == client["tgId"] == 0
    assert client["subId"] == sub_id and re.fullmatch(r"[0-9a-f]{16}", sub_id)
    other, other_sub_id = provider._build_client("u1", 10, 30)
    assert other["id"] != client["id"] and other_sub_id != sub_id


# Case 4
@pytest.mark.parametrize("volume,days,total,expiry", [(0, 0, 0, 0), (0.5, 1 / 24, 536870912, 1_700_003_600_500)], ids=["unlimited", "fractional"])
def test_build_client_volume_and_expiry(monkeypatch, volume, days, total, expiry):
    provider = ThreeXUIProvider(_row("https://panel.example.invalid/xui", STUB_TOKEN))
    monkeypatch.setattr(threexui_provider.time, "time", lambda: FROZEN_NOW)
    client, _ = provider._build_client("u1", volume, days)
    assert client["totalGB"] == total
    assert client["expiryTime"] == expiry


# Case 5
def test_create_user_on_every_selected_inbound():
    _, _, panel = _panel()

    async def scenario():
        async with FakeThreeXUIServer(panel) as server:
            provider = _u1(panel, server)
            created = await provider.create_user("u1", 10, 30)
            assert created.username == "u1" and list(created.raw) == CLIENT_KEYS
            assert created.subscription_url == SUB_BASE + created.raw["subId"]
            for inbound_id in (1, 2):
                (client,) = panel.inbound_clients(inbound_id)
                assert client["email"] == "u1"
                assert client["id"] == client["password"] == created.raw["id"]
                assert client["subId"] == created.raw["subId"]
                assert client["totalGB"] == 10 * GIB and client["expiryTime"] == created.raw["expiryTime"]
                assert client["enable"] is True and "flow" not in client
            assert _calls(panel) == [("POST", "/panel/api/clients/add", "admin")]

    asyncio.run(scenario())


# Case 6
def test_create_user_sends_no_vless_flow():
    fixture, _, panel = _panel("A")

    async def scenario():
        async with FakeThreeXUIServer(panel) as server:
            assert fixture.inbound("A", 1).flow == "xtls-rprx-vision"
            created = await ThreeXUIProvider(_row(server.base_url, panel.tokens["admin"], inbound_ids="[1]")).create_user("u1", 10, 30)
            assert "flow" not in panel.client("u1") and "flow" not in created.raw

    asyncio.run(scenario())


# Case 7
@pytest.mark.parametrize("inbound_ids,inbound_id", [("not-json", 2), (None, 2), ("[]", 2)], ids=["invalid_json", "no_list", "empty_list"])
def test_create_user_inbound_column_fallback(inbound_ids, inbound_id):
    _, _, panel = _panel()

    async def scenario():
        async with FakeThreeXUIServer(panel) as server:
            await ThreeXUIProvider(_row(server.base_url, panel.tokens["admin"], inbound_ids=inbound_ids, inbound_id=inbound_id)).create_user("u1", 10, 30)
            assert panel.inbound_clients(1) == []
            assert [c["email"] for c in panel.inbound_clients(2)] == ["u1"]

    asyncio.run(scenario())


# Case 8
@pytest.mark.parametrize("inbounds,sub_base", [("[]", SUB_BASE), ("[1, 2]", "")], ids=["no_inbounds", "no_sub_base"])
def test_create_user_not_configured(inbounds, sub_base):
    _, _, panel = _panel()

    async def scenario():
        async with FakeThreeXUIServer(panel) as server:
            provider = ThreeXUIProvider(_row(server.base_url, panel.tokens["admin"], inbound_ids=inbounds, sub_base=sub_base))
            with pytest.raises(PanelError) as exc:
                await provider.create_user("u1", 10, 30)
            assert str(exc.value) == NOT_CONFIGURED
            assert panel.calls == []

    asyncio.run(scenario())


# Case 9
def test_create_user_duplicate_email():
    _, _, panel = _panel()

    async def scenario():
        async with FakeThreeXUIServer(panel) as server:
            provider = _u1(panel, server)
            await provider.create_user("u1", 10, 30)
            with pytest.raises(PanelUsernameTakenError) as exc:
                await provider.create_user("u1", 10, 30)
            assert str(exc.value) == TAKEN.format("u1")
            assert len(panel.inbound_clients(1)) == len(panel.inbound_clients(2)) == 1

    asyncio.run(scenario())


# Case 10
@pytest.mark.parametrize("token,inbounds,expected", [(WRONG_TOKEN, "[1, 2]", AUTH.format(401)), (None, "[7]", "Request failed (inbound 7: record not found)")], ids=["wrong_token", "unknown_inbound"])
def test_create_user_rejections(token, inbounds, expected):
    _, _, panel = _panel()

    async def scenario():
        async with FakeThreeXUIServer(panel) as server:
            provider = ThreeXUIProvider(_row(server.base_url, token or panel.tokens["admin"], inbound_ids=inbounds))
            with pytest.raises(PanelError) as exc:
                await provider.create_user("u1", 10, 30)
            assert type(exc.value) is PanelError and str(exc.value) == expected
            assert panel.client("u1") is None

    asyncio.run(scenario())


# Case 11
def test_get_user_reads_current_export():
    _, _, panel = _panel()

    async def scenario():
        async with FakeThreeXUIServer(panel) as server:
            provider = _u1(panel, server)
            created = await provider.create_user("u1", 10, 30)
            start = len(panel.calls)
            result = await provider.get_user("u1")
            assert result.username == "u1"
            assert result.subscription_url == SUB_BASE + created.raw["subId"]
            assert result.raw == panel.client("u1")
            assert _calls(panel, start) == [LIST]

    asyncio.run(scenario())


# Case 12
def test_get_user_takes_first_matching_export():
    async def scenario():
        body = {"success": True, "msg": "", "obj": [
            {"id": 1, "settings": "{not json"},
            {"id": 2, "settings": json.dumps({"clients": [{"email": "other", "subId": "other00000000000"}, {"email": "u1", "subId": "first00000000000"}]})},
            {"id": 3, "settings": {"clients": [{"email": "u1", "subId": "second0000000000"}]}}]}
        async with stub_panel(200, body) as (base, seen):
            result = await ThreeXUIProvider(_row(base, STUB_TOKEN)).get_user("u1")
            assert result.subscription_url == "https://sub.example.invalid/sub/first00000000000"
            assert result.raw == {"email": "u1", "subId": "first00000000000"}
            assert seen == [("GET", "/panel/api/inbounds/list")]
        with_body = {"success": True, "msg": "", "obj": [{"id": 1, "settings": {"clients": [{"email": "u1", "subId": ""}]}}]}
        async with stub_panel(200, with_body) as (base, _):
            with pytest.raises(PanelError) as exc:
                await ThreeXUIProvider(_row(base, STUB_TOKEN)).get_user("u1")
            assert str(exc.value) == NO_SUB_LINK

    asyncio.run(scenario())


# Case 13
@pytest.mark.parametrize("which,expected", [("missing", NOT_FOUND.format("ghost")), ("no_sub_base", NO_SUB_LINK), ("wrong_token", AUTH.format(401))], ids=["missing", "no_sub_base", "wrong_token"])
def test_get_user_failures(which, expected):
    _, _, panel = _panel()

    async def scenario():
        async with FakeThreeXUIServer(panel) as server:
            admin = _u1(panel, server)
            await admin.create_user("u1", 10, 30)
            if which == "missing":
                provider, username = admin, "ghost"
            elif which == "no_sub_base":
                provider, username = ThreeXUIProvider(_row(server.base_url, panel.tokens["admin"], sub_base="")), "u1"
            else:
                provider, username = ThreeXUIProvider(_row(server.base_url, WRONG_TOKEN)), "u1"
            with pytest.raises(PanelError) as exc:
                await provider.get_user(username)
            assert str(exc.value) == expected

    asyncio.run(scenario())


# Case 14
def test_post_client_update_has_no_inbound_filter():
    _, _, panel = _panel()

    async def scenario():
        async with FakeThreeXUIServer(panel) as server:
            provider = _u1(panel, server)
            await provider.create_user("u1", 10, 30)
            start = len(panel.calls)
            async with provider._session() as session:
                assert await provider._post_client_update(session, "u1", 2, {**panel.client("u1"), "enable": False}, "LABEL") == OK_ENVELOPE
            assert all(panel.inbound_clients(i)[0]["enable"] is False for i in (1, 2))
            assert _calls(panel, start) == [UPDATE_U1]

    asyncio.run(scenario())


# Case 15
def test_post_client_update_timeout_becomes_panel_error():
    _, _, panel = _panel()

    async def scenario():
        async with FakeThreeXUIServer(panel) as server:
            provider = _u1(panel, server)
            await provider.create_user("u1", 10, 30)
            server.hold_requests()
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False), headers={"Authorization": "Bearer " + panel.tokens["admin"]}, timeout=aiohttp.ClientTimeout(total=0.2)) as session:
                with pytest.raises(PanelError) as exc:
                    await provider._post_client_update(session, "u1", 2, {**panel.client("u1"), "enable": False}, "LABEL")
            assert type(exc.value) is PanelError
            assert str(exc.value) == CONNECT_INBOUND.format(2)
            assert isinstance(exc.value.__cause__, asyncio.TimeoutError)
            assert server.held_requests == 1
            server.drop_requests()
            assert panel.client("u1")["enable"] is True

    asyncio.run(scenario())


# Case 16
@pytest.mark.parametrize("wrong,expected", [(False, UPDATE_REJECTED.format("LABEL", 2, "Request failed (record not found)")), (True, AUTH.format(401))], ids=["unknown_email", "wrong_token"])
def test_post_client_update_rejections(wrong, expected):
    _, _, panel = _panel()

    async def scenario():
        async with FakeThreeXUIServer(panel) as server:
            await _u1(panel, server).create_user("u1", 10, 30)
            provider = ThreeXUIProvider(_row(server.base_url, WRONG_TOKEN)) if wrong else _u1(panel, server)
            async with provider._session() as session:
                with pytest.raises(PanelError) as exc:
                    await provider._post_client_update(session, "ghost" if not wrong else "u1", 2, {"email": "ghost"}, "LABEL")
            assert str(exc.value) == expected

    asyncio.run(scenario())


async def _setup_u1(panel, server):
    provider = _u1(panel, server)
    created = await provider.create_user("u1", 10, 30)
    return provider, created


# Case 17
def test_update_user_additive():
    _, clock, panel = _panel()

    async def scenario():
        async with FakeThreeXUIServer(panel) as server:
            provider, created = await _setup_u1(panel, server)
            _use(clock, panel, "u1", GIB, 2 * GIB)
            start = len(panel.calls)
            result = await provider.update_user("u1", add_volume_gb=5)
            assert all(panel.inbound_clients(i)[0]["totalGB"] == 15 * GIB and panel.inbound_clients(i)[0]["expiryTime"] == created.raw["expiryTime"] for i in (1, 2))
            assert result.raw["totalGB"] == 15 * GIB and result.subscription_url == SUB_BASE + created.raw["subId"]
            assert _calls(panel, start) == [LIST, UPDATE_U1, UPDATE_U1]
            assert await provider.get_user_usage("u1") == {"used_bytes": 3 * GIB, "data_limit_bytes": 15 * GIB, "status": "active"}

    asyncio.run(scenario())


# Case 18
@pytest.mark.parametrize("expiry,kind", [(FAR_EXPIRY_MS, "future"), (1_000, "past"), (0, "unlimited")], ids=["future", "past", "unlimited"])
def test_update_user_add_days(expiry, kind):
    _, _, panel = _panel()

    async def scenario():
        async with FakeThreeXUIServer(panel) as server:
            panel.seed_client([1, 2], {"email": "u2", "id": SEEDED_ID, "password": SEEDED_ID, "subId": "seeded0000000000", "totalGB": 10 * GIB, "expiryTime": expiry, "enable": False})
            provider = _u1(panel, server)
            before = int(time.time() * 1000)
            result = await provider.update_user("u2", add_days=3)
            after = int(time.time() * 1000)
            client = panel.client("u2")
            if kind == "future":
                assert client["expiryTime"] == FAR_EXPIRY_MS + 3 * DAY_MS
            else:
                assert before + 3 * DAY_MS <= client["expiryTime"] <= after + 3 * DAY_MS
            assert client["enable"] is True and client["totalGB"] == 10 * GIB
            assert result.subscription_url == SUB_BASE + "seeded0000000000"

    asyncio.run(scenario())


# Case 19
def test_update_user_enables_unconditionally():
    _, _, panel = _panel()

    async def scenario():
        async with FakeThreeXUIServer(panel) as server:
            provider, created = await _setup_u1(panel, server)
            await provider.set_enabled("u1", False)
            await provider.update_user("u1")
            assert all(panel.inbound_clients(i)[0]["enable"] is True and panel.inbound_clients(i)[0]["totalGB"] == 10 * GIB and panel.inbound_clients(i)[0]["expiryTime"] == created.raw["expiryTime"] for i in (1, 2))

    asyncio.run(scenario())


def _reset_calls():
    return [LIST, UPDATE_U1, ("POST", "/panel/api/inbounds/1/resetClientTraffic/u1", None), UPDATE_U1, ("POST", "/panel/api/inbounds/2/resetClientTraffic/u1", None)]


# Case 20
def test_update_user_full_replacement_ignores_reset_result():
    _, clock, panel = _panel()

    async def scenario():
        async with FakeThreeXUIServer(panel) as server:
            provider, _ = await _setup_u1(panel, server)
            _use(clock, panel, "u1", GIB, 2 * GIB)
            start = len(panel.calls)
            await provider.update_user("u1", add_volume_gb=20, reset_usage=True)
            assert all(panel.inbound_clients(i)[0]["totalGB"] == 20 * GIB for i in (1, 2))
            assert _calls(panel, start) == _reset_calls()
            served = _served(server)
            assert ("POST", "/xui/panel/api/inbounds/1/resetClientTraffic/u1", 404) in served
            assert ("POST", "/xui/panel/api/inbounds/2/resetClientTraffic/u1", 404) in served
            assert await provider.get_user_usage("u1") == {"used_bytes": 3 * GIB, "data_limit_bytes": 20 * GIB, "status": "active"}

    asyncio.run(scenario())


# Case 21
def test_update_user_full_carryover():
    _, clock, panel = _panel()

    async def scenario():
        async with FakeThreeXUIServer(panel) as server:
            provider, _ = await _setup_u1(panel, server)
            _use(clock, panel, "u1", GIB, 2 * GIB)
            start = len(panel.calls)
            await provider.update_user("u1", add_volume_gb=20, reset_usage=True, preserve_remaining=True)
            expected = [("GET", "/panel/api/clients/traffic/u1", "admin")] + _reset_calls()
            assert _calls(panel, start) == expected
            assert all(panel.inbound_clients(i)[0]["totalGB"] == 27 * GIB for i in (1, 2))
            assert await provider.get_user_usage("u1") == {"used_bytes": 3 * GIB, "data_limit_bytes": 27 * GIB, "status": "active"}

    asyncio.run(scenario())


# Case 22
def test_update_user_carryover_read_error_substitutes_zero():
    _, clock, panel = _panel()

    async def scenario():
        async with FakeThreeXUIServer(panel) as server:
            admin, _ = await _setup_u1(panel, server)
            _use(clock, panel, "u1", GIB, 2 * GIB)
            provider = ThreeXUIProvider(_row(server.base_url, panel.tokens["node-sync"]))
            start = len(panel.calls)
            await provider.update_user("u1", add_volume_gb=20, reset_usage=True, preserve_remaining=True)
            assert _calls(panel, start)[0] == ("GET", "/panel/api/clients/traffic/u1", "node-sync")
            assert all(panel.inbound_clients(i)[0]["totalGB"] == 30 * GIB for i in (1, 2))
            assert ("GET", "/xui/panel/api/clients/traffic/u1", 403) in _served(server)

    asyncio.run(scenario())


# Case 23
@pytest.mark.parametrize("preserve", [True, False], ids=["carryover", "replacement"])
def test_update_user_full_renewal_without_volume(preserve):
    _, _, panel = _panel()

    async def scenario():
        async with FakeThreeXUIServer(panel) as server:
            provider, _ = await _setup_u1(panel, server)
            start = len(panel.calls)
            await provider.update_user("u1", reset_usage=True, preserve_remaining=preserve)
            assert all(panel.inbound_clients(i)[0]["totalGB"] == 10 * GIB for i in (1, 2))
            calls = _calls(panel, start)
            assert calls[0] == LIST and not any(path.startswith("/panel/api/clients/traffic/") for _, path, _ in calls)

    asyncio.run(scenario())


# Case 24
def test_update_user_missing_client():
    _, _, panel = _panel()

    async def scenario():
        async with FakeThreeXUIServer(panel) as server:
            provider = _u1(panel, server)
            start = len(panel.calls)
            with pytest.raises(PanelError) as exc:
                await provider.update_user("ghost", add_volume_gb=1)
            assert str(exc.value) == NOT_FOUND.format("ghost")
            assert _calls(panel, start) == [LIST]

    asyncio.run(scenario())


# Case 25
def test_set_enabled_toggles_every_inbound():
    _, _, panel = _panel()

    async def scenario():
        async with FakeThreeXUIServer(panel) as server:
            provider, created = await _setup_u1(panel, server)
            start = len(panel.calls)
            assert await provider.set_enabled("u1", False) is None
            for i in (1, 2):
                client = panel.inbound_clients(i)[0]
                assert client["enable"] is False
                assert all(client[k] == created.raw[k] for k in ("id", "subId", "totalGB", "expiryTime"))
            assert _calls(panel, start) == [LIST, UPDATE_U1, UPDATE_U1]
            await provider.set_enabled("u1", True)
            assert all(panel.inbound_clients(i)[0]["enable"] is True for i in (1, 2))

    asyncio.run(scenario())


# Case 26
@pytest.mark.parametrize("which,expected", [("missing", NOT_FOUND.format("ghost")), ("wrong_token", AUTH.format(401))], ids=["missing", "wrong_token"])
def test_set_enabled_failures(which, expected):
    _, _, panel = _panel()

    async def scenario():
        async with FakeThreeXUIServer(panel) as server:
            admin = _u1(panel, server)
            await admin.create_user("u1", 10, 30)
            provider, username = (admin, "ghost") if which == "missing" else (ThreeXUIProvider(_row(server.base_url, WRONG_TOKEN)), "u1")
            with pytest.raises(PanelError) as exc:
                await provider.set_enabled(username, False)
            assert str(exc.value) == expected
            if which == "wrong_token":
                assert panel.client("u1")["enable"] is True

    asyncio.run(scenario())


# Case 27
def test_get_user_usage_reads_traffic():
    _, clock, panel = _panel()

    async def scenario():
        async with FakeThreeXUIServer(panel) as server:
            provider, _ = await _setup_u1(panel, server)
            _use(clock, panel, "u1", GIB, 2 * GIB)
            active = {"used_bytes": 3 * GIB, "data_limit_bytes": 10 * GIB, "status": "active"}
            assert await provider.get_user_usage("u1") == active
            await provider.set_enabled("u1", False)
            assert await provider.get_user_usage("u1") == {**active, "status": "disabled"}

    asyncio.run(scenario())


# Case 28
def test_get_user_usage_missing_object_is_zero():
    _, clock, panel = _panel()

    async def scenario():
        async with FakeThreeXUIServer(panel) as server:
            provider, _ = await _setup_u1(panel, server)
            _use(clock, panel, "u1", GIB, 2 * GIB)
            assert await provider.get_user_usage("ghost") == ZERO_USAGE
            await provider.delete_user("u1")
            assert await provider.get_user_usage("u1") == ZERO_USAGE

    asyncio.run(scenario())


# Case 29
def test_get_user_usage_rejected_read_is_zero():
    async def scenario():
        async with stub_panel(200, REJECTED) as (base, seen):
            assert await ThreeXUIProvider(_row(base, STUB_TOKEN)).get_user_usage("u1") == ZERO_USAGE
            assert seen == [("GET", "/panel/api/clients/traffic/u1")]

    asyncio.run(scenario())


# Case 30
def test_get_user_usage_http_error_raises():
    _, _, panel = _panel()

    async def scenario():
        async with FakeThreeXUIServer(panel) as server:
            with pytest.raises(PanelError) as exc:
                await ThreeXUIProvider(_row(server.base_url, WRONG_TOKEN)).get_user_usage("u1")
            assert str(exc.value) == AUTH.format(401)

    asyncio.run(scenario())


# Case 31
def test_delete_user_checks_status_only():
    _, _, panel = _panel()

    async def scenario():
        async with FakeThreeXUIServer(panel) as server:
            provider = _u1(panel, server)
            await provider.create_user("u1", 10, 30)
            assert await provider.delete_user("u1") is True
            assert panel.inbound_clients(1) == panel.inbound_clients(2) == []
            assert await provider.delete_user("u1") is True
            assert _calls(panel)[-2:] == [("POST", "/panel/api/clients/del/u1", "admin")] * 2
            await provider.create_user("u2", 10, 30)
            assert await ThreeXUIProvider(_row(server.base_url, WRONG_TOKEN)).delete_user("u2") is False
            assert panel.client("u2") is not None

    asyncio.run(scenario())


# Case 32
@pytest.mark.parametrize("status,body,expected", [(404, None, False), (500, None, False), (200, REJECTED, True)], ids=["not_found", "server_error", "rejected_envelope"])
def test_delete_user_status_mapping(status, body, expected):
    async def scenario():
        async with stub_panel(status, body) as (base, seen):
            result = await ThreeXUIProvider(_row(base, STUB_TOKEN)).delete_user("u1")
            assert result is expected
            assert seen == [("POST", "/panel/api/clients/del/u1")]

    asyncio.run(scenario())
