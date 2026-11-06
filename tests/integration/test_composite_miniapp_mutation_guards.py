"""T050j: refuse unsupported Mini App custom-service mutations before effects."""
from types import SimpleNamespace

import pytest

from tests._harness.legacy_bot import use_synthetic_bot_settings
use_synthetic_bot_settings()
from tests.characterization.test_unsupported_surfaces import MAIN_TOKEN, _call, _shop, mini
from tests.integration.test_composite_legacy_guards import as_row
from tests.integration.test_composite_miniapp_retrieval_guards import dump

OPERATIONS = ("delete", "toggle", "rename", "auto-renew", "transfer", "cut-access")
LINK = "https://sub.example.invalid/SECRET-MUTATE-OLD"
NEW_LINK = "https://sub.example.invalid/SECRET-MUTATE-NEW"


def prepare(mini, monkeypatch, representation, operation, source=None, discriminator=None, unrelated=False):
    db = mini.main
    for user in (5101, 5102):
        db.add_or_update_user(user, f"u{user}", "U")
    pid = _shop(db, "Safe product", 100000, [])
    oid = db.create_order(5101, pid, 100000)
    sid = db.add_panel_server("Synthetic", "3xui", "https://panel.example.invalid", "fake-user", "fake-password")
    cc = db.add_custom_config(5101, sid, "original_name", 10, 30, LINK, order_id=oid)
    other = db.add_custom_config(5101, sid, "unrelated", 10, 30, "https://sub.example.invalid/unrelated") if unrelated else None
    calls = []

    class Provider:
        async def delete_user(self, username): calls.append(("delete", username))
        async def set_enabled(self, username, enabled): calls.append(("toggle", username, enabled))
        async def rename_user(self, username, label): calls.append(("rename", username, label))
        async def revoke_credentials(self, username):
            calls.append(("cut-access", username))
            return SimpleNamespace(subscription_url=NEW_LINK)

    def provider(server):
        calls.append(("factory", server["id"]))
        return Provider()

    class Session:
        async def __aenter__(self): return self
        async def __aexit__(self, *args): return False
        async def post(self, url, **kwargs):
            calls.append(("telegram", kwargs["json"]["chat_id"]))

    monkeypatch.setattr(mini.server, "get_provider", provider)
    monkeypatch.setattr(mini.server.aiohttp, "ClientSession", Session)
    for name, category in (("get_custom_config_owned", "custom"), ("get_custom_configs_for_user", "custom"), ("get_order", "order"), ("get_product", "product")):
        original = getattr(db, name)
        def wrap(*args, original=original, category=category, **kwargs):
            result = original(*args, **kwargs)
            def convert(row):
                if row is None: return None
                data = dict(row)
                data.pop("service_kind", None)
                if discriminator is not None: data["service_kind"] = discriminator
                if category == "custom" and other is not None and data["id"] == other: data["service_kind"] = "composite"
                if source == category: data["service_kind"] = "composite"
                return as_row(data, representation)
            return [convert(r) for r in result] if isinstance(result, list) else convert(result)
        monkeypatch.setattr(db, name, wrap)
    method = "DELETE" if operation == "delete" else "POST"
    url = f"/api/custom-configs/{cc}" + ("" if operation == "delete" else f"/{operation}")
    body = {"rename": {"new_name": "renamed_service"}, "auto-renew": {"enabled": True}, "transfer": {"target_telegram_id": 5102}}.get(operation)
    return cc, sid, method, url, ({"json": body} if body else {}), calls


@pytest.mark.parametrize("representation", ["dict", "sqlite"])
@pytest.mark.parametrize("source", ["custom", "order", "product"])
@pytest.mark.parametrize("operation", OPERATIONS)
def test_composite_miniapp_mutation_refused(mini, monkeypatch, caplog, representation, source, operation):
    _, _, method, url, kwargs, calls = prepare(mini, monkeypatch, representation, operation, source)
    before = dump(mini.main)
    code, result = _call(mini.server, method, url, token=MAIN_TOKEN, tg_id=5101, **kwargs)
    assert code == 403 and "composite" in result["detail"].lower()
    assert calls == [] and mini.alerts == [] and mini.subs == []
    assert dump(mini.main) == before
    assert "SECRET-MUTATE" not in str(result) + caplog.text


@pytest.mark.parametrize("representation", ["dict", "sqlite"])
@pytest.mark.parametrize("unrelated", [False, True])
@pytest.mark.parametrize("discriminator", [None, "legacy"])
@pytest.mark.parametrize("operation", OPERATIONS)
def test_legacy_miniapp_mutation_preserved(mini, monkeypatch, representation, discriminator, operation, unrelated):
    cc, sid, method, url, kwargs, calls = prepare(mini, monkeypatch, representation, operation, discriminator=discriminator, unrelated=unrelated)
    code, result = _call(mini.server, method, url, token=MAIN_TOKEN, tg_id=5101, **kwargs)
    assert code == 200 and result["status"] == "ok"
    with mini.main._get_conn() as conn:
        row = conn.execute("SELECT * FROM custom_configs WHERE id=?", (cc,)).fetchone()
        events = [r[0] for r in conn.execute("SELECT event_type FROM custom_config_history WHERE custom_config_id=? ORDER BY id", (cc,))]
        assert conn.execute("SELECT final_price,status FROM orders").fetchall()[0][:] == (100000, "pending")
    if operation == "delete":
        assert row is None and calls == [("factory", sid), ("delete", "original_name")]
    else:
        assert row["volume_gb"] == 10 and row["duration_days"] == 30
        event = {"auto-renew": "auto_renew_toggle", "cut-access": "cut_access"}.get(operation, operation)
        assert events == ["purchase", event]
        if operation == "toggle": assert row["enabled"] == 0 and result["enabled"] is False and calls == [("factory", sid), ("toggle", "original_name", False)]
        elif operation == "rename": assert row["display_name"] == row["username"] == result["display_name"] == "renamed_service" and calls == [("factory", sid), ("rename", "original_name", "renamed_service")]
        elif operation == "auto-renew": assert row["auto_renew"] == 1 and result["auto_renew"] is True and calls == []
        elif operation == "transfer": assert row["user_id"] == 5102 and calls == [("telegram", 5102)]
        else: assert row["subscription_url"] == result["subscription_url"] == NEW_LINK and calls == [("factory", sid), ("cut-access", "original_name")]
        if operation != "transfer": assert row["user_id"] == 5101
        if operation != "cut-access": assert row["subscription_url"] == LINK
    assert mini.alerts == [] and mini.subs == []
