"""T050k: Mini App full-renewal selection/checkout refuse relevant composites."""
import re

import pytest

from tests._harness.legacy_bot import use_synthetic_bot_settings
use_synthetic_bot_settings()
import renewal_engine
from tests.characterization.test_unsupported_surfaces import MAIN_TOKEN, _call, mini
from tests.integration.test_composite_legacy_guards import as_row
from tests.integration.test_composite_miniapp_retrieval_guards import dump

LINK = "https://sub.example.invalid/SECRET-RENEW-LINK"
SCENARIOS = [("plans", s, 30000) for s in ("custom", "order", "parent_product", "selected")] + [("checkout", s, wallet) for s in ("custom", "order", "parent_product", "selected", "request") for wallet in (30000, 100000)]


def prepare(mini, monkeypatch, representation, kind, wallet, source=None, discriminator=None, unrelated=False):
    db = mini.main
    db.add_or_update_user(5101, "u5101", "U")
    db.add_wallet_credit(5101, wallet)
    sid = db.add_panel_server("Synthetic", "3xui", "https://panel.example.invalid", "fake-user", "fake-password")
    category = db.add_category("Renewal")
    parent = db.add_product(category, "Old product", 100000)
    oid = db.create_order(5101, parent, 100000)
    cc = db.add_custom_config(5101, sid, "renew_service", 10, 30, LINK, order_id=oid)
    selected = db.add_product(category, "Safe renewal", 100000, is_auto_provision=True, auto_provision_volume_gb=20, provision_server_id=sid)
    other = None
    if unrelated:
        other_sid = db.add_panel_server("Other", "3xui", "https://other.example.invalid", "fake", "fake")
        other = db.add_product(category, "Other panel composite", 100000, is_auto_provision=True, auto_provision_volume_gb=20, provision_server_id=other_sid)
    calls = []

    class Provider:
        async def update_user(self, username, **kwargs): calls.append(("update", username, kwargs))
        async def get_user_usage(self, username):
            calls.append(("usage", username))
            return {"data_limit_bytes": 26 * 1024 ** 3}

    def provider(server):
        calls.append(("factory", server["id"]))
        return Provider()

    monkeypatch.setattr(renewal_engine, "get_provider", provider)
    for name in ("get_custom_config_owned", "get_order", "get_product", "get_all_products"):
        original = getattr(db, name)
        def wrap(*args, original=original, name=name, **kwargs):
            result = original(*args, **kwargs)
            def convert(row):
                if row is None: return None
                data = dict(row)
                data.pop("service_kind", None)
                if discriminator is not None: data["service_kind"] = discriminator
                relevant = (name == "get_custom_config_owned" and source == "custom") or (name == "get_order" and data["id"] == oid and source == "order") or (name in ("get_product", "get_all_products") and ((data["id"] == parent and source == "parent_product") or (data["id"] == selected and source == "selected") or data["id"] == other))
                if relevant: data["service_kind"] = "composite"
                return as_row(data, representation)
            return [convert(r) for r in result] if isinstance(result, list) else convert(result)
        monkeypatch.setattr(db, name, wrap)
    path = f"/api/custom-configs/{cc}/" + ("renewal-full-plans" if kind == "plans" else "renew-full")
    body = {"product_id": selected}
    if discriminator is not None: body["service_kind"] = discriminator
    if source == "request": body["service_kind"] = "composite"
    return cc, sid, selected, oid, path, ({"json": body} if kind == "checkout" else {}), calls


@pytest.mark.parametrize("representation", ["dict", "sqlite"])
@pytest.mark.parametrize("kind,source,wallet", SCENARIOS)
def test_composite_miniapp_renewal_refused(mini, monkeypatch, caplog, representation, kind, source, wallet):
    _, _, _, _, path, kwargs, calls = prepare(mini, monkeypatch, representation, kind, wallet, source)
    before = dump(mini.main)
    code, result = _call(mini.server, "GET" if kind == "plans" else "POST", path, token=MAIN_TOKEN, tg_id=5101, **kwargs)
    assert code == 403 and "composite" in result["detail"].lower()
    assert calls == [] and mini.alerts == [] and mini.subs == [] and dump(mini.main) == before
    assert "SECRET-RENEW" not in str(result) + caplog.text


@pytest.mark.parametrize("representation", ["dict", "sqlite"])
@pytest.mark.parametrize("discriminator", [None, "legacy"])
@pytest.mark.parametrize("unrelated", [False, True])
@pytest.mark.parametrize("kind,wallet", [("plans", 30000), ("checkout", 30000), ("checkout", 100000)])
def test_legacy_miniapp_renewal_preserved(mini, monkeypatch, representation, discriminator, unrelated, kind, wallet):
    cc, sid, selected, oid, path, kwargs, calls = prepare(mini, monkeypatch, representation, kind, wallet, discriminator=discriminator, unrelated=unrelated)
    before = dump(mini.main)
    code, result = _call(mini.server, "GET" if kind == "plans" else "POST", path, token=MAIN_TOKEN, tg_id=5101, **kwargs)
    assert code == 200
    if kind == "plans":
        assert result == [{"id": selected, "name": "Safe renewal", "price": 100000, "original_price": None, "discount_percent": None, "volume_gb": 20, "duration_days": 30}]
        expected = [re.sub(r'(INSERT INTO "sqlite_sequence" VALUES\(\'users\',)([0-9]+)(\);)', lambda m: m[1] + str(int(m[2]) + 1) + m[3], line) for line in before]
        assert expected != before and dump(mini.main) == expected and calls == []
    else:
        assert mini.main.get_wallet_credit(5101) == 0
        with mini.main._get_conn() as conn:
            order = conn.execute("SELECT user_id,is_renewal,renewal_target_kind,renewal_target_id,renewal_mode,renewal_add_volume_gb,renewal_add_days,wallet_used,final_price,status FROM orders WHERE id!=?", (oid,)).fetchone()
            assert tuple(order) == (5101, 1, "custom", cc, "full", 20, 30, wallet, 100000-wallet, "approved" if wallet == 100000 else "pending")
            row = conn.execute("SELECT user_id,volume_gb,duration_days,subscription_url FROM custom_configs WHERE id=?", (cc,)).fetchone()
            events = [r[0] for r in conn.execute("SELECT event_type FROM custom_config_history WHERE custom_config_id=? ORDER BY id", (cc,))]
            assert conn.execute("SELECT final_price,status FROM orders WHERE id=?", (oid,)).fetchone()[:] == (100000, "pending")
        if wallet == 30000:
            assert result["status"] == "pending_payment" and result["final_price"] == 70000 and result["order_id"] == oid + 1
            assert calls == [] and tuple(row) == (5101, 10, 30, LINK) and events == ["purchase"]
        else:
            assert result == {"status": "approved", "order_id": oid + 1, "message": "✅ سرویس شما با موفقیت تمدید شد."}
            assert calls == [("factory", sid), ("update", "renew_service", {"add_volume_gb": 20, "add_days": 30, "reset_usage": True, "preserve_remaining": True}), ("usage", "renew_service")]
            assert tuple(row) == (5101, 26, 60, LINK) and events == ["purchase", "renewal"]
    assert mini.alerts == [] and mini.subs == []
