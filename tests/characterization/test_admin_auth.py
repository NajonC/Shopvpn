"""Characterize owner and staff web authority at commit b453ff8.

Baseline: ``.venv/bin/python -m pytest tests/characterization/test_admin_auth.py --network=deny``.
Every database is a SQLite file under ``tmp_path``; no panel, payment service or Telegram is contacted.

Pins (FR-005; FR-084): (a) session cookies use a signed base64url JSON payload and reject bad signatures/expiry, while non-ASCII inputs raise (cases 1–3); (b) mobile bearer tokens carry an unsigned tenant slug and are checked against that tenant's database (cases 4–5, 12–13); (c) permission, owner and main-tenant guards have the recorded role/tenant boundaries (cases 6–8, 14); (d) credentials come from database rows and are created/revoked by login, token and bridge routes (cases 9–11, 15–16).
"""

import asyncio
import base64
import hashlib
import hmac
import json
import time
from types import SimpleNamespace

import httpx
import pytest
from fastapi import HTTPException

import database
from admin_panel import mobile_auth, security
from tests._harness.legacy_web import load_admin_panel, session_cookie


SESSION_INVALID = "نشست منقضی شده یا نامعتبر است."
PANEL_OFF = "پنل وب این نماینده دیگر فعال نیست."
ACCOUNT_OFF = "حساب کاربری غیرفعال یا حذف شده است."
BEARER_INVALID = "توکن دسترسی نامعتبر یا باطل\u200cشده است."
TENANT_BLOCKED = "این قابلیت برای نمایندگی در دسترس نیست."
MAIN_ONLY = "این بخش فقط در پنل بات اصلی در دسترس است."
NO_PERMISSION = "دسترسی کافی نیست."
OWNER_ONLY = "این بخش فقط برای مالک است."
LOGIN_FAILED = "یوزرنیم یا پسورد اشتباه است."
PANEL_UNAVAILABLE = "این پنل در دسترس نیست."
TOKEN_NOT_FOUND = "توکن پیدا نشد."
BRIDGE_INVALID = "توکن نامعتبر است."
OWNER = 9001
TENANT_TOKEN = "777001:tenant-synthetic"
ALL_PERMS = ["orders", "users", "catalog", "discounts", "tickets", "broadcast", "resellers", "panels", "system", "settings", "backup"]
ADMIN_PERMS = ["orders", "users", "catalog", "discounts", "tickets", "broadcast", "resellers", "panels", "system", "settings"]
MID_PERMS = ["orders", "users", "tickets", "broadcast"]
MAIN_PAT = "spat_bWFpbg_synthetic-main-secret"
MID_PAT = "spat_bWFpbg_synthetic-mid-secret"
TENANT_PAT = "spat_MQ_synthetic-r1-secret"
EVIL = "https://evil.example.invalid/x"


def _sign(secret, payload):
    body = base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode()).rstrip(b"=").decode()
    return body + "." + hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()


def _payload(token):
    body = token.split(".", 1)[0]
    return json.loads(base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)))


def _sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def _refused(call):
    with pytest.raises(HTTPException) as exc:
        call()
    return exc.value.status_code, exc.value.detail


def _rows(db, sql, params=()):
    with db._get_conn() as conn:
        return [tuple(r) for r in conn.execute(sql, params)]


def _call(web, method, url, cookie=None, bearer=None, headers=None, **kwargs):
    request_headers = dict(headers or {})
    if cookie is not None:
        request_headers["Cookie"] = "panel_session=" + cookie
    if bearer is not None:
        request_headers["Authorization"] = "Bearer " + bearer

    async def request():
        transport = httpx.ASGITransport(app=web.panel.app, raise_app_exceptions=False)
        async with httpx.AsyncClient(transport=transport, base_url="http://panel.test") as client:
            return await client.request(method, url, headers=request_headers, follow_redirects=False, **kwargs)

    return asyncio.run(request())


def _cookie(web, admin_id, tenant="", role="owner", username="x", ttl_seconds=3600):
    return session_cookie(web.secret, admin_id, username, role, tenant, ttl_seconds)


def _attrs(set_cookie):
    return set_cookie.split("; ")[1:]


def _cookie_value(set_cookie):
    return set_cookie.split("panel_session=", 1)[1].split(";", 1)[0]


@pytest.fixture
def panel(tmp_path_factory):
    return load_admin_panel(tmp_path_factory.getbasetemp())


@pytest.fixture
def web(monkeypatch, tmp_path_factory, tmp_path):
    panel = load_admin_panel(tmp_path_factory.getbasetemp())
    main = database.Database(str(tmp_path / "main.db"))
    main.init_db(OWNER)
    monkeypatch.setattr(panel, "main_db", main)
    monkeypatch.setattr(panel.MAIN_TENANT, "db", main)
    rd = tmp_path / "reseller_dbs"
    rd.mkdir()
    assert main.register_reseller_bot(TENANT_TOKEN, "r1bot", 5001, "R1", str(rd / "r1.db")) == 1
    tenant = database.Database(str(rd / "r1.db"))
    tenant.init_db(5001)
    main.enable_reseller_web_panel(1)
    assert main.create_web_admin("mainowner", "synthetic-hash", role="owner") == 1
    assert main.create_web_admin("mainmid", "synthetic-hash", role="mid") == 2
    assert main.create_web_admin("mainadmin", "synthetic-hash", role="admin") == 3
    assert main.create_web_admin("mainsupport", "synthetic-hash", role="support", permissions=["orders", "bogus"]) == 4
    assert tenant.create_web_admin("r1owner", "synthetic-hash", role="owner") == 1
    assert tenant.create_web_admin("r1staff", "synthetic-hash", role="admin", permissions=["orders", "resellers"]) == 2
    yield SimpleNamespace(panel=panel, main=main, tenant=tenant, secret=panel.ADMIN_PANEL_SECRET, rd=rd)
    tenant.close()
    main.close()


# Case 1
def test_session_token_is_base64url_json_with_a_hex_hmac(monkeypatch):
    monkeypatch.setattr(security, "time", SimpleNamespace(time=lambda: 1_700_000_000.0))
    valid = {"id": 7, "u": "u7", "r": "mid", "b": "", "exp": 1_700_043_200}
    token = security.create_session_token("k", 7, "u7", "mid")
    expected = "eyJpZCI6NywidSI6InU3IiwiciI6Im1pZCIsImIiOiIiLCJleHAiOjE3MDAwNDMyMDB9.6998782b41ef47a9d4328513bcb3b54c7d99f44d9b7741f55dfd5e23080ed064"
    assert token == expected == _sign("k", valid)
    tenant_token = security.create_session_token("k", 7, "u7", "mid", hours=1, tenant="shop1")
    assert tenant_token == _sign("k", {"id": 7, "u": "u7", "r": "mid", "b": "shop1", "exp": 1_700_003_600})
    assert "=" not in token and "=" not in tenant_token


# Case 2
def test_verify_session_token_needs_the_key_and_an_unexpired_exp(monkeypatch):
    monkeypatch.setattr(security, "time", SimpleNamespace(time=lambda: 1_700_000_000.0))
    valid = {"id": 7, "u": "u7", "r": "mid", "b": "", "exp": 1_700_043_200}
    assert security.verify_session_token("k", _sign("k", valid)) == valid
    assert security.verify_session_token("k", _sign("k", {"id": 1, "exp": 1_700_000_000})) == {"id": 1, "exp": 1_700_000_000}
    assert security.verify_session_token("k", _sign("k", {"id": 1, "exp": 1_699_999_999})) is None
    assert security.verify_session_token("k", _sign("k", {"id": 1})) is None
    assert security.verify_session_token("other", _sign("k", valid)) is None
    for token in (None, "", "nodot"):
        assert security.verify_session_token("k", token) is None
    body = _sign("k", {**valid, "r": "owner"}).split(".", 1)[0]
    sig = _sign("k", valid).split(".", 1)[1]
    assert security.verify_session_token("k", body + "." + sig) is None
    good = _sign("k", valid)
    assert security.verify_session_token("k", good.rsplit(".", 1)[0] + "." + good.rsplit(".", 1)[1].upper()) is None
    last = "0" if good[-1] != "0" else "1"
    assert security.verify_session_token("k", good[:-1] + last) is None
    invalid_json = "notjson." + hmac.new(b"k", b"notjson", hashlib.sha256).hexdigest()
    assert security.verify_session_token("k", invalid_json) is None


# Case 3
def test_verify_session_token_raises_on_non_ascii_tokens(monkeypatch):
    monkeypatch.setattr(security, "time", SimpleNamespace(time=lambda: 1_700_000_000.0))
    with pytest.raises(UnicodeEncodeError):
        security.verify_session_token("k", "\u00e9.abc")
    with pytest.raises(TypeError):
        security.verify_session_token("k", "abc.\u00e9")


# Case 4
def test_generate_token_layout_hash_and_prefix(monkeypatch):
    calls = []

    def fake(size):
        calls.append(size)
        return "abcdefgh_ijkl-mnop"

    monkeypatch.setattr(mobile_auth, "secrets", SimpleNamespace(token_urlsafe=fake))
    token = "spat_bWFpbg_abcdefgh_ijkl-mnop"
    assert mobile_auth.generate_token("") == (token, "07ead49803d852044cd490dc74c424943d73ae13074ccae9695d2f53440ffe4a", "spat_bWFpbg_abcdef\u2026")
    assert mobile_auth.hash_token(token) == _sha(token)
    shop = "spat_c2hvcDE_abcdefgh_ijkl-mnop"
    assert mobile_auth.generate_token("shop1") == (shop, _sha(shop), "spat_c2hvcDE_abcdef\u2026")
    one = "spat_MQ_abcdefgh_ijkl-mnop"
    assert mobile_auth.generate_token("1") == (one, _sha(one), "spat_MQ_abcdef\u2026")
    assert mobile_auth.generate_token("main") == mobile_auth.generate_token("")
    assert calls == [32, 32, 32, 32, 32]
    assert mobile_auth.hash_token("x") == _sha("x")


# Case 5
def test_extract_tenant_slug_reads_the_unsigned_slug_part():
    for token in (None, "", "abc", "spat", "spat_", "spat_bWFpbg", "spat_bWFpbg_", "SPAT_bWFpbg_x", "spat_wyg_x"):
        assert mobile_auth.extract_tenant_slug(token) is None
    assert mobile_auth.extract_tenant_slug("spat_bWFpbg_x") == ""
    assert mobile_auth.extract_tenant_slug("spat__x") == ""
    assert mobile_auth.extract_tenant_slug("spat_!!!_x") == ""
    assert mobile_auth.extract_tenant_slug("spat_MQ_x") == "1"
    assert mobile_auth.extract_tenant_slug("spat_c2hvcDE_a_b") == "shop1"


# Case 6
def test_require_permission_blocks_resellers_in_tenants_and_lets_owners_pass(panel):
    MO = {"id": 1, "role": "owner", "permissions": [], "tenant": ""}
    TO = {**MO, "tenant": "1"}
    MS = {"id": 2, "role": "mid", "permissions": ["orders", "resellers", "no-such-key"], "tenant": ""}
    TS = {"id": 2, "role": "admin", "permissions": ["orders", "resellers"], "tenant": "1"}
    for permission in ("orders", "resellers", "no-such-key"):
        assert panel.require_permission(permission)(MS) is MS
    assert _refused(lambda: panel.require_permission("users")(MS)) == (403, NO_PERMISSION)
    for permission in ("users", "resellers", "no-such-key"):
        assert panel.require_permission(permission)(MO) is MO
    assert panel.require_permission("users")(TO) is TO
    for admin in (TO, TS):
        assert _refused(lambda: panel.require_permission("resellers")(admin)) == (403, TENANT_BLOCKED)
    assert panel.require_permission("orders")(TS) is TS
    assert _refused(lambda: panel.require_permission("users")(TS)) == (403, NO_PERMISSION)
    assert panel.MAIN_TENANT_ONLY_PERMISSIONS == {"resellers"}
    assert panel.TENANT_BLOCKED_PERMISSIONS == {"resellers"}


# Case 7
def test_require_owner_checks_the_role_only(panel):
    MO = {"id": 1, "role": "owner", "permissions": [], "tenant": ""}
    TO = {**MO, "tenant": "1"}
    assert panel.require_owner(MO) is MO
    assert panel.require_owner(TO) is TO
    for role in ("admin", "mid", "support"):
        admin = {"id": 2, "role": role, "permissions": ALL_PERMS, "tenant": ""}
        assert _refused(lambda: panel.require_owner(admin)) == (403, OWNER_ONLY)


# Case 8
def test_require_main_tenant_checks_the_tenant_only(panel):
    support = {"id": 4, "role": "support", "permissions": [], "tenant": ""}
    TO = {"id": 1, "role": "owner", "permissions": [], "tenant": "1"}
    TS = {"id": 2, "role": "admin", "permissions": ["orders"], "tenant": "1"}
    assert panel.require_main_tenant(support) is support
    for admin in (TO, TS):
        assert _refused(lambda: panel.require_main_tenant(admin)) == (403, MAIN_ONLY)


# Case 9
def test_session_cookie_refusals(web):
    def me(cookie=None, **kwargs):
        return _call(web, "GET", "/api/me", cookie=cookie, **kwargs)

    for cookie in (None, session_cookie("other-secret", 1, "x", "owner"), _cookie(web, 1, ttl_seconds=-1), "nodot"):
        response = me(cookie)
        assert response.status_code == 401 and response.json() == {"detail": SESSION_INVALID}
    response = me(_cookie(web, 1, tenant="nosuch"))
    assert response.status_code == 401 and response.json() == {"detail": PANEL_OFF}
    assert web.main.register_reseller_bot("777002:tenant-synthetic", "r2bot", 5002, "R2", str(web.rd / "missing.db")) == 2
    web.main.enable_reseller_web_panel(2)
    response = me(_cookie(web, 1, tenant="2"))
    assert response.status_code == 401 and response.json() == {"detail": PANEL_OFF}
    web.main.disable_reseller_web_panel(1)
    response = me(_cookie(web, 1, tenant="1"))
    assert response.status_code == 401 and response.json() == {"detail": PANEL_OFF}
    web.main.enable_reseller_web_panel(1)
    assert me(_cookie(web, 1, tenant="1")).status_code == 200
    web.main.toggle_reseller_bot(1)
    response = me(_cookie(web, 1, tenant="1"))
    assert response.status_code == 401 and response.json() == {"detail": PANEL_OFF}
    for admin_id in (99,):
        response = me(_cookie(web, admin_id))
        assert response.status_code == 401 and response.json() == {"detail": ACCOUNT_OFF}
    assert web.main.set_web_admin_active(2, False)
    response = me(_cookie(web, 2))
    assert response.status_code == 401 and response.json() == {"detail": ACCOUNT_OFF}


# Case 10
def test_session_role_and_permissions_come_from_the_database_row(web):
    expected = [
        (2, "owner", "forged", {"id": 2, "username": "mainmid", "role": "mid", "permissions": MID_PERMS, "tenant": "", "reseller_profile": None}),
        (1, "support", "x", {"id": 1, "username": "mainowner", "role": "owner", "permissions": ALL_PERMS, "tenant": "", "reseller_profile": None}),
        (3, "x", "x", {"id": 3, "username": "mainadmin", "role": "admin", "permissions": ADMIN_PERMS, "tenant": "", "reseller_profile": None}),
        (4, "x", "x", {"id": 4, "username": "mainsupport", "role": "support", "permissions": ["orders"], "tenant": "", "reseller_profile": None}),
    ]
    for admin_id, role, username, expected_json in expected:
        response = _call(web, "GET", "/api/me", cookie=_cookie(web, admin_id, role=role, username=username))
        assert response.status_code == 200 and response.json() == expected_json


# Case 11
def test_session_tenant_comes_from_the_signed_payload(web):
    response = _call(web, "GET", "/api/me", cookie=_cookie(web, 1), params={"b": "1"})
    assert response.status_code == 200
    assert (response.json()["username"], response.json()["tenant"], response.json()["reseller_profile"]) == ("mainowner", "", None)
    response = _call(web, "GET", "/api/me", cookie=_cookie(web, 1, tenant="1"))
    data = response.json()
    assert response.status_code == 200
    assert (data["username"], data["role"], data["permissions"], data["tenant"]) == ("r1owner", "owner", ALL_PERMS, "1")
    assert data["reseller_profile"]["enabled"] is True and data["reseller_profile"]["web_panel_enabled"] is True
    assert data["reseller_profile"]["owner_telegram_id"] == 5001
    assert _call(web, "GET", "/api/me", cookie=_cookie(web, 2)).json()["username"] == "mainmid"
    response = _call(web, "GET", "/api/me", cookie=_cookie(web, 2, tenant="1"))
    assert (response.json()["username"], response.json()["role"], response.json()["permissions"], response.json()["tenant"]) == ("r1staff", "admin", ["orders", "resellers"], "1")
    response = _call(web, "GET", "/api/me", cookie=_cookie(web, 3, tenant="1"))
    assert response.status_code == 401 and response.json() == {"detail": ACCOUNT_OFF}
    web.main.set_reseller_link_slug(1, "shop1")
    for slug in ("shop1", "1"):
        response = _call(web, "GET", "/api/me", cookie=_cookie(web, 1, tenant=slug))
        assert response.status_code == 200 and response.json()["tenant"] == slug and response.json()["username"] == "r1owner"
    no_b = _sign(web.secret, {"id": 1, "u": "x", "r": "owner", "exp": int(time.time()) + 600})
    response = _call(web, "GET", "/api/me", cookie=no_b)
    assert response.status_code == 200 and response.json()["tenant"] == "" and response.json()["username"] == "mainowner"


# Case 12
def test_bearer_token_is_checked_against_its_own_tenant_database(web):
    assert web.main.create_mobile_token(1, "phone", _sha(MAIN_PAT), "spat_bWFpbg_synthe") == 1
    assert web.tenant.create_mobile_token(1, "tablet", _sha(TENANT_PAT), "spat_MQ_synthe") == 1
    assert _rows(web.main, "SELECT last_used_at FROM mobile_app_tokens WHERE id=1") == [(None,)]
    expected_main = {"id": 1, "username": "mainowner", "role": "owner", "permissions": ALL_PERMS, "tenant": "", "mobile_token_id": 1}
    response = _call(web, "GET", "/api/me", bearer=MAIN_PAT)
    assert response.status_code == 200 and response.json() == expected_main
    assert _rows(web.main, "SELECT last_used_at FROM mobile_app_tokens WHERE id=1")[0][0] is not None
    response = _call(web, "GET", "/api/me", headers={"Authorization": "BEARER  " + MAIN_PAT + "  "})
    assert response.status_code == 200 and response.json() == expected_main
    expected_tenant = {"id": 1, "username": "r1owner", "role": "owner", "permissions": ALL_PERMS, "tenant": "1", "mobile_token_id": 1}
    response = _call(web, "GET", "/api/me", bearer=TENANT_PAT)
    assert response.status_code == 200 and response.json() == expected_tenant
    response = _call(web, "GET", "/api/web-admins", bearer=TENANT_PAT)
    assert response.status_code == 200 and [row["username"] for row in response.json()] == ["r1owner", "r1staff"]
    for token in ("spat_MQ_synthetic-main-secret", "spat_bWFpbg_synthetic-r1-secret"):
        response = _call(web, "GET", "/api/me", bearer=token)
        assert response.status_code == 401 and response.json() == {"detail": BEARER_INVALID}


# Case 13
def test_bearer_refusals_never_fall_back_to_the_cookie(web):
    assert web.main.create_mobile_token(1, "phone", _sha(MAIN_PAT), "spat_bWFpbg_synthe") == 1
    assert web.main.create_mobile_token(2, "mid", _sha(MID_PAT), "spat_bWFpbg_synthe") == 2
    assert web.tenant.create_mobile_token(1, "tablet", _sha(TENANT_PAT), "spat_MQ_synthe") == 1
    cookie = _cookie(web, 1)
    for token in ("garbage", "spat_bWFpbg_unknown-secret"):
        response = _call(web, "GET", "/api/me", cookie=cookie, bearer=token)
        assert response.status_code == 401 and response.json() == {"detail": BEARER_INVALID}
    response = _call(web, "GET", "/api/me", cookie=cookie, headers={"Authorization": "Basic abc"})
    assert response.status_code == 200 and response.json()["username"] == "mainowner"
    response = _call(web, "GET", "/api/me", bearer=MID_PAT)
    assert response.status_code == 200 and response.json()["role"] == "mid"
    assert web.main.set_web_admin_active(2, False)
    response = _call(web, "GET", "/api/me", cookie=cookie, bearer=MID_PAT)
    assert response.status_code == 401 and response.json() == {"detail": BEARER_INVALID}
    assert web.main.revoke_mobile_token(1)
    response = _call(web, "GET", "/api/me", cookie=cookie, bearer=MAIN_PAT)
    assert response.status_code == 401 and response.json() == {"detail": BEARER_INVALID}
    assert _call(web, "GET", "/api/me", bearer=TENANT_PAT).status_code == 200
    web.main.disable_reseller_web_panel(1)
    response = _call(web, "GET", "/api/me", bearer=TENANT_PAT)
    assert response.status_code == 401 and response.json() == {"detail": BEARER_INVALID}
    response = _call(web, "GET", "/api/me", cookie=_cookie(web, 1, tenant="1"))
    assert response.status_code == 401 and response.json() == {"detail": PANEL_OFF}


# Case 14
def test_routes_apply_the_owner_permission_and_main_tenant_guards(web):
    response = _call(web, "GET", "/api/web-admins/permissions", cookie=_cookie(web, 1))
    assert response.status_code == 200 and response.json() == {"permissions": ALL_PERMS}
    response = _call(web, "GET", "/api/web-admins/permissions", cookie=_cookie(web, 1, tenant="1"))
    assert response.status_code == 200 and response.json() == {"permissions": [p for p in ALL_PERMS if p != "resellers"]}
    response = _call(web, "GET", "/api/web-admins/permissions", cookie=_cookie(web, 3))
    assert response.status_code == 403 and response.json() == {"detail": OWNER_ONLY}
    response = _call(web, "GET", "/api/web-admins", cookie=_cookie(web, 1, tenant="1"))
    assert response.status_code == 200 and [row["username"] for row in response.json()] == ["r1owner", "r1staff"]
    response = _call(web, "GET", "/api/web-admins", cookie=_cookie(web, 1))
    assert response.status_code == 200
    assert [row["username"] for row in response.json()] == ["mainowner", "mainadmin", "mainmid", "mainsupport"]
    assert response.json()[0]["password_hash"] == "synthetic-hash"
    for admin_id in (1, 3):
        response = _call(web, "GET", "/api/reseller-panels-lite", cookie=_cookie(web, admin_id))
        assert response.status_code == 200 and response.json() == []
    response = _call(web, "GET", "/api/reseller-panels-lite", cookie=_cookie(web, 2))
    assert response.status_code == 403 and response.json() == {"detail": NO_PERMISSION}
    for admin_id in (1, 2):
        response = _call(web, "GET", "/api/reseller-panels-lite", cookie=_cookie(web, admin_id, tenant="1"))
        assert response.status_code == 403 and response.json() == {"detail": TENANT_BLOCKED}
    response = _call(web, "GET", "/api/system/stats", cookie=_cookie(web, 1, tenant="1"))
    assert response.status_code == 403 and response.json() == {"detail": MAIN_ONLY}


# Case 15
def test_login_sets_a_12_hour_cookie_from_the_database_row(web):
    web.main.set_web_admin_password(1, security.hash_password("main-pass-123"))
    assert web.main.get_web_admin(1)["last_login"] is None
    before = int(time.time())
    response = _call(web, "POST", "/api/login", json={"username": "MainOwner", "password": "main-pass-123"})
    after = int(time.time())
    assert response.status_code == 200 and response.json() == {"id": 1, "username": "mainowner", "role": "owner", "tenant": ""}
    set_cookie = response.headers["set-cookie"]
    assert set_cookie.startswith("panel_session=")
    assert _attrs(set_cookie) == ["HttpOnly", "Max-Age=43200", "Path=/", "SameSite=lax"]
    value = _cookie_value(set_cookie)
    assert value == _sign(web.secret, _payload(value))
    payload = _payload(value)
    exp = payload.pop("exp")
    assert payload == {"id": 1, "u": "mainowner", "r": "owner", "b": ""}
    assert before + 43200 <= exp <= after + 43200
    assert web.main.get_web_admin(1)["last_login"] is not None
    response = _call(web, "POST", "/api/login", json={"username": "MainOwner", "password": "wrong"})
    assert response.status_code == 401 and response.json() == {"detail": LOGIN_FAILED}
    response = _call(web, "POST", "/api/login", json={"username": "MainOwner", "password": "main-pass-123", "b": "nosuch"})
    assert response.status_code == 401 and response.json() == {"detail": PANEL_UNAVAILABLE}
    response = _call(web, "POST", "/api/login", json={"username": "MainOwner", "password": "main-pass-123", "b": "1"})
    assert response.status_code == 401 and response.json() == {"detail": LOGIN_FAILED}
    response = _call(web, "POST", "/api/logout")
    assert response.status_code == 200 and response.json() == {"ok": True}
    assert response.headers["set-cookie"].startswith('panel_session="";')
    assert "Max-Age=0" in response.headers["set-cookie"]


# Case 16
def test_mobile_tokens_are_per_admin_and_the_bridge_redirects_anywhere(web):
    response = _call(web, "POST", "/api/app/tokens", cookie=_cookie(web, 1), json={"name": "phone"})
    assert response.status_code == 200
    data = response.json()
    assert sorted(data) == ["id", "name", "server_url", "token"]
    assert (data["id"], data["name"], data["server_url"]) == (1, "phone", "http://panel.test")
    token = data["token"]
    assert token.startswith("spat_bWFpbg_")
    assert _rows(web.main, "SELECT admin_id, token_hash, token_prefix FROM mobile_app_tokens") == [(1, _sha(token), token[:18] + "\u2026")]
    assert token not in str(_rows(web.main, "SELECT * FROM mobile_app_tokens"))
    response = _call(web, "GET", "/api/me", bearer=token)
    assert response.status_code == 200 and response.json()["mobile_token_id"] == 1
    response = _call(web, "DELETE", "/api/app/tokens/1", cookie=_cookie(web, 2))
    assert response.status_code == 404 and response.json() == {"detail": TOKEN_NOT_FOUND}
    assert _call(web, "GET", "/api/me", bearer=token).status_code == 200
    before = int(time.time())
    response = _call(web, "GET", "/app/webview-bridge", params={"token": token, "next": EVIL})
    after = int(time.time())
    assert response.status_code == 307 and response.headers["location"] == EVIL
    set_cookie = response.headers["set-cookie"]
    assert _attrs(set_cookie) == ["HttpOnly", "Max-Age=3600", "Path=/", "SameSite=lax"]
    value = _cookie_value(set_cookie)
    assert value == _sign(web.secret, _payload(value))
    payload = _payload(value)
    exp = payload.pop("exp")
    assert payload == {"id": 1, "u": "mainowner", "r": "owner", "b": ""}
    assert before + 43200 <= exp <= after + 43200
    response = _call(web, "GET", "/app/webview-bridge", params={"token": "spat_bWFpbg_unknown-secret"})
    assert response.status_code == 401 and response.json() == {"detail": BRIDGE_INVALID}
    response = _call(web, "DELETE", "/api/app/tokens/1", cookie=_cookie(web, 1))
    assert response.status_code == 200 and response.json() == {"ok": True, "deleted": False}
    response = _call(web, "GET", "/api/me", bearer=token)
    assert response.status_code == 401 and response.json() == {"detail": BEARER_INVALID}
    response = _call(web, "DELETE", "/api/app/tokens/1", cookie=_cookie(web, 1))
    assert response.status_code == 200 and response.json() == {"ok": True, "deleted": True}
    response = _call(web, "DELETE", "/api/app/tokens/1", cookie=_cookie(web, 1))
    assert response.status_code == 404 and response.json() == {"detail": TOKEN_NOT_FOUND}
