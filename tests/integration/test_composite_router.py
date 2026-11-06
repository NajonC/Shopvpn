"""T049: trusted configuration and the actual admin app's router mounting.

Test-only witnesses are added just before FastAPI copies the empty scaffold.
Authentication, configuration, dependencies and app assembly run for real.
"""

import sys
from types import SimpleNamespace

import pytest
from fastapi import FastAPI, Request

from tests._harness.legacy_web import load_admin_panel, session_cookie
from tests.integration.test_authority_matrix import (
    HTTP_ORIGIN, MAIN, authority_web, csrf_header, http_call, http_probe,
    http_refused, http_state,
)


@pytest.mark.parametrize("settings", [
    {"main_installation_id": ""}, {"main_installation_id": None},
    {"main_owner_web_admin_id": None}, {"main_owner_web_admin_id": True},
    {"main_owner_web_admin_id": "1"}, {"main_owner_web_admin_id": 0},
    {"public_origin": ""}, {"public_origin": "null"},
    {"public_origin": "https://user:pass@panel.example.invalid"},
    {"public_origin": HTTP_ORIGIN + "/path"},
    {"public_origin": HTTP_ORIGIN + "?x=1"},
    {"public_origin": HTTP_ORIGIN + "#fragment"},
    {"public_origin": "https://bad host.example.invalid"},
    {"public_origin": "https://panel\\evil.example.invalid"},
    {"public_origin": HTTP_ORIGIN + ":443"},
])
def test_invalid_trusted_config_fails_closed(authority_web, settings):
    web = authority_web
    config = dict(main_installation_id=MAIN, main_owner_web_admin_id=1,
                  public_origin=HTTP_ORIGIN)
    config.update(settings)
    router = web.panel.create_composite_router(**config)
    effects = []

    async def read():
        effects.append("read")
        return {"ok": True}

    router.add_api_route("/_authority_read", read, methods=["GET"])
    app = FastAPI()
    app.include_router(router)
    cookie = session_cookie(web.panel.ADMIN_PANEL_SECRET, 1, "synthetic", "owner")
    http_refused(web, app, effects, "GET", 503, cookie=cookie)


@pytest.mark.parametrize("origin", ["https://panel.example.invalid:8443", "http://127.0.0.1:8002"])
def test_valid_configured_origin_preserves_nondefault_ports(authority_web, origin):
    web = authority_web
    router = web.panel.create_composite_router(
        main_installation_id=MAIN, main_owner_web_admin_id=1, public_origin=origin,
    )
    effects = []

    async def write():
        effects.append("write")
        return {"ok": True}

    router.add_api_route("/_authority_write", write, methods=["POST"])
    app = FastAPI()
    app.include_router(router)
    cookie = session_cookie(web.panel.ADMIN_PANEL_SECRET, 1, "synthetic", "owner")
    response = http_call(app, "POST", cookie=cookie,
                         headers={"Origin": origin, "X-Composite-CSRF": csrf_header(web, cookie)})
    assert response.status_code == 200
    assert effects == ["write"]


def test_non_ascii_csrf_is_sanitized_refusal(authority_web):
    web = authority_web
    app, effects = http_probe(web)
    cookie = session_cookie(web.panel.ADMIN_PANEL_SECRET, 1, "synthetic", "owner")
    # Raw header bytes are legal input to ASGI; compare_digest(str, str) alone
    # raises TypeError for a decoded non-ASCII header instead of refusing it.
    before = http_state(web, effects)
    response = http_call(app, "POST", cookie=cookie,
                         headers={"Origin": HTTP_ORIGIN, "X-Composite-CSRF": b"\xff"})
    assert response.status_code == 403
    assert http_state(web, effects) == before
    assert cookie not in response.text


@pytest.mark.parametrize("cookie", ['"body.\\377"', '"\\377.signature"'])
def test_non_ascii_session_is_unauthenticated(authority_web, cookie):
    web = authority_web
    app, effects = http_probe(web)
    # Cookie octal escapes arrive over ASCII HTTP and decode to non-ASCII.
    http_refused(web, app, effects, "GET", 401, cookie=cookie)


@pytest.fixture
def mounted_panel(monkeypatch, tmp_path_factory):
    """Re-import actual server under synthetic config; intercept only mounting."""
    import admin_panel

    old_module = sys.modules.get("admin_panel.server")
    old_attribute = getattr(admin_panel, "server", None)
    seen = []
    original_include = FastAPI.include_router

    def include(app, router, *args, **kwargs):
        if router.prefix == "/api/composite":
            seen.append(tuple(router.routes))

            async def witness(request: Request):
                principal = request.state.composite_principal
                return {"actor": principal.authenticated_actor_id,
                        "installation": principal.tenant_installation_id,
                        "domain": principal.identity_domain}

            router.add_api_route("/_authority_read", witness, methods=["GET"])
            router.add_api_route("/_authority_write", witness, methods=["POST"])
        return original_include(app, router, *args, **kwargs)

    monkeypatch.setattr(FastAPI, "include_router", include)
    sys.modules.pop("admin_panel.server", None)
    if hasattr(admin_panel, "server"):
        del admin_panel.server
    panel = None
    try:
        panel = load_admin_panel(tmp_path_factory.getbasetemp())
        yield panel, seen
    finally:
        if panel is not None:
            panel.main_db.close()
        sys.modules.pop("admin_panel.server", None)
        if old_module is not None:
            sys.modules["admin_panel.server"] = old_module
        if old_attribute is not None:
            admin_panel.server = old_attribute
        elif hasattr(admin_panel, "server"):
            del admin_panel.server


@pytest.mark.parametrize("setting,value,expected", [
    (None, None, 200),
    ("COMPOSITE_MAIN_INSTALLATION_ID", None, 503),
    ("COMPOSITE_MAIN_OWNER_WEB_ADMIN_ID", None, 503),
    ("COMPOSITE_MAIN_OWNER_WEB_ADMIN_ID", "not-an-id", 503),
    ("COMPOSITE_MAIN_OWNER_WEB_ADMIN_ID", "0", 503),
    ("COMPOSITE_PUBLIC_ORIGIN", None, 503),
    ("COMPOSITE_PUBLIC_ORIGIN", "null", 503),
])
def test_real_app_mounts_configured_empty_scaffold(monkeypatch, request, setting, value, expected):
    monkeypatch.setenv("COMPOSITE_MAIN_INSTALLATION_ID", MAIN)
    # Choose web id 2 to catch hardcoded id 1; missing mapping must still fail closed.
    monkeypatch.setenv("COMPOSITE_MAIN_OWNER_WEB_ADMIN_ID", "2")
    monkeypatch.setenv("COMPOSITE_PUBLIC_ORIGIN", HTTP_ORIGIN)
    if setting:
        if value is None:
            monkeypatch.delenv(setting, raising=False)
        else:
            monkeypatch.setenv(setting, value)
    panel, seen = request.getfixturevalue("mounted_panel")
    assert seen == [()]  # actual mounting once, without a business/test route
    assert panel.main_db.create_web_admin("first", "synthetic-hash", role="owner") == 1
    assert panel.main_db.create_web_admin("mapped", "synthetic-hash", role="owner") == 2
    cookie = session_cookie(panel.ADMIN_PANEL_SECRET, 2, "synthetic", "support")
    headers = {"Origin": HTTP_ORIGIN, "X-Composite-CSRF": csrf_header(SimpleNamespace(panel=panel), cookie)}
    for method in ("GET", "POST"):
        response = http_call(panel.app, method, cookie=cookie, headers=headers,
                             query="?b=1&user_id=1&tenant=spoofed")
        assert response.status_code == expected, response.text
        if expected == 200:
            assert response.json() == {"actor": 2, "installation": MAIN, "domain": "web_admin"}
    if expected == 200:
        wrong_owner = session_cookie(panel.ADMIN_PANEL_SECRET, 1, "synthetic", "owner")
        assert http_call(panel.app, "GET", cookie=wrong_owner).status_code == 403
