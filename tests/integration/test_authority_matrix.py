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
