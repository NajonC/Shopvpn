"""T047a: Telegram identity and resource authority (implemented by T048).

The real service adapter and guard run before a synthetic SQLite effect sink.
This exercises their composition, not future business commands or web routes.
Transport authentication is the adapter's caller precondition; no live Telegram.
"""

import sqlite3
from types import SimpleNamespace

import pytest

from composite import service


MAIN = "synthetic-main-installation"
OTHER = "synthetic-other-installation"


def event(actor=101, *, callback=True, reseller=False, discount=False):
    # Deliberately disagree with the authenticated actor and trusted installation.
    result = SimpleNamespace(
        from_user=SimpleNamespace(id=actor, is_reseller=reseller, has_discount=discount),
        user_id=202,
        tenant_installation_id=OTHER,
    )
    if callback:
        result.message = SimpleNamespace(from_user=SimpleNamespace(id=202))
        result.data = "cmp:details:202:synthetic-other-installation"
    return result


@pytest.fixture
def store(tmp_path):
    """Synthetic effect witness, not a substitute composite repository/schema."""
    conn = sqlite3.connect(tmp_path / "authority.db")
    conn.execute("CREATE TABLE resources (id TEXT PRIMARY KEY, tenant TEXT, customer INTEGER, effects INTEGER)")
    conn.executemany("INSERT INTO resources VALUES (?, ?, ?, 0)", [
        ("own", MAIN, 101), ("second", MAIN, 101),
        ("another", MAIN, 202), ("foreign", OTHER, 101),
    ])
    conn.commit()
    yield conn, []
    conn.close()


def snapshot(store):
    conn, effects = store
    return list(conn.execute("SELECT * FROM resources ORDER BY id")), list(effects)


def attempt(store, principal, resource):
    """Only the adapter/guard are production behavior under test.

    Resource authority comes from a persisted row, never the event payload.
    Future T048/T118 commands must reuse the guard before their own effects.
    """
    conn, effects = store
    tenant, customer = conn.execute(
        "SELECT tenant, customer FROM resources WHERE id = ?", (resource,)
    ).fetchone()
    service.authorize_customer_resource(
        principal, main_installation_id=MAIN,
        resource_tenant_installation_id=tenant, customer_telegram_id=customer,
    )
    conn.execute("UPDATE resources SET effects = effects + 1 WHERE id = ?", (resource,))
    conn.commit()
    effects.append((resource, principal.authenticated_actor_id))


def refused(store, principal, resource, code):
    before = snapshot(store)
    with pytest.raises(service.AuthorityError) as error:
        attempt(store, principal, resource)
    assert error.value.code == code
    assert str(error.value) == code  # no target, payload, or private detail
    assert snapshot(store) == before


@pytest.mark.parametrize("callback", [False, True], ids=["message", "callback"])
def test_authenticated_sender_and_trusted_installation_define_principal(callback):
    principal = service.telegram_principal(event(callback=callback), tenant_installation_id=MAIN)
    assert isinstance(principal, service.Principal)
    assert (principal.identity_domain, principal.authenticated_actor_id,
            principal.tenant_installation_id, principal.role,
            principal.authenticated_interface) == ("telegram", 101, MAIN, "customer", "telegram")


def test_forged_callback_actor_cannot_manage_message_actor_resource(store):
    principal = service.telegram_principal(event(), tenant_installation_id=MAIN)
    refused(store, principal, "another", "not_found")


def test_cross_tenant_resource_refused_even_when_customer_ids_match(store):
    principal = service.telegram_principal(event(), tenant_installation_id=MAIN)
    refused(store, principal, "foreign", "not_found")


@pytest.mark.parametrize("resource", ["own", "foreign"])
def test_non_main_transport_cannot_manage_main_or_own_tenant_resource(store, resource):
    principal = service.telegram_principal(event(), tenant_installation_id=OTHER)
    assert principal.tenant_installation_id == OTHER
    refused(store, principal, resource, "forbidden")


@pytest.mark.parametrize("reseller,discount", [(False, False), (True, False), (False, True), (True, True)])
def test_own_resources_allowed_despite_untrusted_selectors_or_buyer_status(store, reseller, discount):
    principal = service.telegram_principal(
        event(reseller=reseller, discount=discount), tenant_installation_id=MAIN,
    )
    # Two owned subscriptions remain independently manageable; no arbitrary cap.
    attempt(store, principal, "own")
    attempt(store, principal, "second")
    assert snapshot(store) == ([
        ("another", MAIN, 202, 0), ("foreign", OTHER, 101, 0),
        ("own", MAIN, 101, 1), ("second", MAIN, 101, 1),
    ], [("own", 101), ("second", 101)])


@pytest.mark.parametrize("actor", [202, 303])
def test_ownership_is_not_hardcoded_to_fixture_actor(store, actor):
    store[0].execute("UPDATE resources SET customer = ? WHERE id = 'own'", (actor,))
    store[0].commit()
    principal = service.telegram_principal(event(actor), tenant_installation_id=MAIN)
    attempt(store, principal, "own")
    assert store[0].execute("SELECT customer, effects FROM resources WHERE id = 'own'").fetchone() == (actor, 1)
    assert store[1] == [("own", actor)]


@pytest.mark.parametrize("sender", [None, SimpleNamespace(id=None)])
def test_missing_authenticated_sender_never_falls_back_to_payload_or_message(store, sender):
    forged = event()
    forged.from_user = sender
    before = snapshot(store)
    with pytest.raises(service.AuthorityError) as error:
        principal = service.telegram_principal(forged, tenant_installation_id=MAIN)
        attempt(store, principal, "another")
    assert error.value.code == "unauthenticated"
    assert str(error.value) == "unauthenticated"
    assert snapshot(store) == before


@pytest.mark.parametrize("field,value", [
    ("identity_domain", "web_admin"),
    ("identity_domain", "subscription_url"),
    ("authenticated_interface", "miniapp"),
    ("role", "owner"),
])
def test_matching_numeric_id_cannot_replace_customer_domain_interface_or_role(store, field, value):
    # Server-established principals for other domains are not Telegram customers.
    fields = dict(identity_domain="telegram", authenticated_actor_id=101,
                  tenant_installation_id=MAIN, role="customer", authenticated_interface="telegram")
    fields[field] = value
    refused(store, service.Principal(**fields), "own", "forbidden")


# T047b1: authenticated web identity mapping. HTTP router/CSRF is T047b2.
# The authentication function runs for real; only its databases/configuration
# are synthetic. The effect sink witnesses the adapter boundary, not a route.
@pytest.fixture
def authority_web(monkeypatch, tmp_path_factory, tmp_path):
    import database
    from tests._harness.legacy_web import load_admin_panel

    panel = load_admin_panel(tmp_path_factory.getbasetemp())
    main = database.Database(str(tmp_path / "web-main.db"))
    main.init_db(2)  # Telegram owner 2 overlaps an UNMAPPED web owner id.
    tenant = database.Database(str(tmp_path / "web-tenant.db"))
    tenant.init_db(2)
    monkeypatch.setattr(panel, "main_db", main)
    monkeypatch.setattr(panel.MAIN_TENANT, "db", main)
    monkeypatch.setattr(panel, "OWNER_ID", 2)
    assert main.register_reseller_bot(
        "777001:synthetic-authority", "synthetic", 2, "Synthetic", tenant.db_path,
    ) == 1
    main.enable_reseller_web_panel(1)
    assert main.create_web_admin("mapped-owner", "synthetic-hash", role="owner") == 1
    assert main.create_web_admin("unmapped-owner", "synthetic-hash", role="owner") == 2
    assert main.create_web_admin("orders-staff", "synthetic-hash", role="support", permissions=["orders"]) == 3
    assert main.create_web_admin("admin-staff", "synthetic-hash", role="admin") == 4
    assert tenant.create_web_admin("tenant-owner", "synthetic-hash", role="owner") == 1
    yield SimpleNamespace(panel=panel, main=main, tenant=tenant)
    tenant.close()
    main.close()


def web_cookie(web, actor=1, *, tenant="", role="owner", ttl_seconds=3600):
    from tests._harness.legacy_web import session_cookie
    # This harness signs independently; it does not use the verifier under test.
    return session_cookie(web.panel.ADMIN_PANEL_SECRET, actor, "synthetic", role, tenant, ttl_seconds)


def authenticated_web_admin(web, cookie, *, query=b"b=1&user_id=2", body=None):
    import asyncio
    import json
    from starlette.requests import Request

    payload = json.dumps(body or {"id": 2, "role": "owner", "tenant": "1"}).encode()

    async def receive():
        return {"type": "http.request", "body": payload, "more_body": False}

    request = Request({
        "type": "http", "method": "POST", "scheme": "https",
        "server": ("panel.example.invalid", 443), "path": "/api/composite/probe",
        "query_string": query,
        "headers": [(b"cookie", ("panel_session=" + cookie).encode())],
    }, receive)
    return asyncio.run(web.panel.get_current_admin(request))


def map_web(admin, *, mapped_owner=1, installation=MAIN):
    return service.web_principal(
        admin, main_installation_id=installation,
        main_owner_web_admin_id=mapped_owner,
    )


def web_effect(store, principal):
    # Not a production command: record the returned identity for comparison.
    store[0].execute("UPDATE resources SET effects = effects + 1 WHERE id = 'own'")
    store[0].commit()
    store[1].append((principal.identity_domain, principal.authenticated_actor_id,
                     principal.tenant_installation_id, principal.role,
                     principal.authenticated_interface))


def refuse_web(store, admin, **kwargs):
    before = snapshot(store)
    with pytest.raises(service.AuthorityError) as error:
        web_effect(store, map_web(admin, **kwargs))
    assert error.value.code == str(error.value) == "forbidden"
    assert snapshot(store) == before


@pytest.mark.parametrize("actor,installation", [(1, MAIN), (2, "synthetic-main-second")])
def test_web_explicit_owner_mapping_preserves_web_domain_and_configured_identity(authority_web, store, actor, installation):
    admin = authenticated_web_admin(authority_web, web_cookie(authority_web, actor, role="support"))
    assert admin["role"] == "owner"  # DB role, not even a correctly signed stale claim.
    principal = map_web(admin, mapped_owner=actor, installation=installation)
    assert isinstance(principal, service.Principal)
    web_effect(store, principal)
    assert store[1] == [("web_admin", actor, installation, "owner", "web")]
    assert store[0].execute("SELECT effects FROM resources WHERE id = 'own'").fetchone() == (1,)
    assert store[0].execute("SELECT sum(effects) FROM resources WHERE id != 'own'").fetchone() == (0,)


@pytest.mark.parametrize("actor", [3, 4], ids=["orders-permission", "admin-permissions"])
def test_web_database_staff_role_cannot_be_replaced_by_signed_owner_claim(authority_web, store, actor):
    admin = authenticated_web_admin(authority_web, web_cookie(authority_web, actor))
    assert admin["role"] != "owner" and "orders" in admin["permissions"]
    # Match the trusted mapping so that only the role guard can reject this.
    refuse_web(store, admin, mapped_owner=actor)


@pytest.mark.parametrize("full_access", [False, True], ids=["reseller-owner", "full-access-tenant"])
def test_web_signed_tenant_cannot_be_replaced_by_main_selector(authority_web, store, full_access):
    admin = authenticated_web_admin(
        authority_web, web_cookie(authority_web, tenant="1"),
        query=b"b=&tenant=&user_id=1", body={"tenant": "", "id": 1},
    )
    assert (admin["id"], admin["role"], admin["tenant"]) == (1, "owner", "1")
    if full_access:
        assert authority_web.panel.require_full_access_tenant(admin) is admin
    refuse_web(store, admin)


def test_web_telegram_owner_number_does_not_authorize_unmapped_web_owner(authority_web, store):
    admin = authenticated_web_admin(authority_web, web_cookie(authority_web, 2))
    assert admin["id"] == authority_web.panel.OWNER_ID == 2
    assert admin["tenant"] == "" and admin["role"] == "owner"
    refuse_web(store, admin, mapped_owner=1)


@pytest.mark.parametrize("mapped_owner", [None, 0, "1", True])
def test_web_mapping_must_be_explicit_valid_web_id(authority_web, store, mapped_owner):
    admin = authenticated_web_admin(authority_web, web_cookie(authority_web))
    refuse_web(store, admin, mapped_owner=mapped_owner)


@pytest.mark.parametrize("patch", [
    {"tenant": None}, {"tenant": "main"}, {"tenant": "1"},
    {"id": True}, {"id": "1"}, {"id": None},
    {"mobile_token_id": 9},
], ids=["missing-tenant", "main-alias", "other-tenant", "bool-id", "string-id", "missing-id", "mobile-identity"])
def test_web_adapter_refuses_incomplete_or_wrong_authentication_domain(authority_web, store, patch):
    admin = authenticated_web_admin(authority_web, web_cookie(authority_web))
    admin.update(patch)
    refuse_web(store, admin)


def test_web_valid_identity_never_becomes_customer_authority_on_equal_numbers(authority_web, store):
    admin = authenticated_web_admin(authority_web, web_cookie(authority_web))
    principal = map_web(admin)
    store[0].execute("UPDATE resources SET customer=1 WHERE id='own'")
    store[0].commit()
    refused(store, principal, "own", "forbidden")


@pytest.mark.parametrize("invalid", ["tampered", "expired", "inactive"])
def test_web_invalid_session_never_reaches_principal_or_effect(authority_web, store, invalid):
    from fastapi import HTTPException

    cookie = web_cookie(authority_web, ttl_seconds=-60 if invalid == "expired" else 3600)
    if invalid == "tampered":
        cookie = cookie[:-1] + ("1" if cookie[-1] == "0" else "0")
    if invalid == "inactive":
        # Seed an inactive authenticated row directly. The legacy administration
        # helper deliberately refuses to deactivate owners; it is not under test.
        with authority_web.main._get_conn() as conn:
            conn.execute("UPDATE web_admins SET is_active=0 WHERE id=1")
        assert not authority_web.main.get_web_admin(1)["is_active"]
    before = snapshot(store)
    with pytest.raises(HTTPException) as error:
        admin = authenticated_web_admin(authority_web, cookie)
        web_effect(store, map_web(admin))
    assert error.value.status_code == 401
    assert snapshot(store) == before
