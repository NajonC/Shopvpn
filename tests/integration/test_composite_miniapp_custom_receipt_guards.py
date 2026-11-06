"""T050m: custom checkout and receipt adapters refuse unsupported composites."""
import json
from types import SimpleNamespace

import pytest

from tests._harness.legacy_bot import use_synthetic_bot_settings
use_synthetic_bot_settings()
from tests.characterization.test_unsupported_surfaces import MAIN_TOKEN, _call, _shop, mini
from tests.integration.test_composite_legacy_guards import as_row
from tests.integration.test_composite_miniapp_retrieval_guards import dump

LINK = "https://sub.example.invalid/SECRET-CUSTOM-LINK"
SCENARIOS = [("purchase", "request", w) for w in (30000, 100000)] + [("receipt_stock", s, 30000) for s in ("order", "product")] + [(k, "order", 30000) for k in ("receipt_custom", "receipt_renewal")]


def prepare(mini, monkeypatch, representation, kind, wallet, source=None, discriminator=None):
    db = mini.main
    db.add_or_update_user(5101, "u5101", "U")
    db.add_wallet_credit(5101, wallet)
    sid = db.add_panel_server("Synthetic", "3xui", "https://panel.example.invalid", "fake-user", "fake-password")
    db.update_panel_server(sid, used_for_custom_config=1)
    db.set_setting("custom_config_enabled", "1")
    db.add_pricing_tier(1, None, 10000)
    oid = pid = None
    if kind == "receipt_stock":
        pid = _shop(db, "Safe stock", 100000, [])
        oid = db.create_order(5101, pid, 100000)
    elif kind == "receipt_custom": oid = db.create_custom_config_order(5101, 10, "safe_custom", sid, 100000)
    elif kind == "receipt_renewal":
        cc = db.add_custom_config(5101, sid, "safe_service", 10, 30, LINK)
        oid = db.create_renewal_order(5101, "custom", cc, "time", 0, 30, 100000)
    calls = []

    class Provider:
        async def create_user(self, username, volume_gb, days):
            calls.append(("create", username, volume_gb, days))
            return SimpleNamespace(username=username, subscription_url=LINK)

    def provider(server):
        calls.append(("factory", server["id"]))
        return Provider()

    async def send(db_arg, token, caption, markup, photo, filename, content_type):
        assert db_arg is db and token == MAIN_TOKEN
        calls.append(("receipt", caption, json.loads(markup), photo, filename, content_type))
        return "synthetic-receipt-file", 1, [(9001, 77)]

    monkeypatch.setattr(mini.server, "get_provider", provider)
    monkeypatch.setattr(mini.server, "send_photo_to_admins", send)
    for name, category in (("get_order", "order"), ("get_product", "product")):
        original = getattr(db, name)
        def wrap(*args, original=original, category=category, **kwargs):
            row = original(*args, **kwargs)
            if row is None: return None
            data = dict(row)
            data.pop("service_kind", None)
            if discriminator is not None: data["service_kind"] = discriminator
            if source == category: data["service_kind"] = "composite"
            return as_row(data, representation)
        monkeypatch.setattr(db, name, wrap)
    body = {"username": "safe_custom", "volume_gb": 10}
    if discriminator is not None: body["service_kind"] = discriminator
    if source == "request": body["service_kind"] = "composite"
    path = "/api/custom-configs" if kind == "purchase" else f"/api/orders/{oid}/receipt"
    kwargs = {"json": body} if kind == "purchase" else {"files": {"photo": ("receipt.jpg", b"synthetic-receipt", "image/jpeg")}}
    return sid, oid, path, kwargs, calls


@pytest.mark.parametrize("representation", ["dict", "sqlite"])
@pytest.mark.parametrize("kind,source,wallet", SCENARIOS)
def test_composite_miniapp_custom_receipt_refused(mini, monkeypatch, caplog, representation, kind, source, wallet):
    _, _, path, kwargs, calls = prepare(mini, monkeypatch, representation, kind, wallet, source)
    before = dump(mini.main)
    code, result = _call(mini.server, "POST", path, token=MAIN_TOKEN, tg_id=5101, **kwargs)
    assert code == 403 and "composite" in result["detail"].lower()
    assert calls == [] and dump(mini.main) == before and mini.alerts == [] and mini.subs == []
    assert "SECRET-CUSTOM" not in str(result) + caplog.text


@pytest.mark.parametrize("representation", ["dict", "sqlite"])
@pytest.mark.parametrize("discriminator", [None, "legacy"])
@pytest.mark.parametrize("kind,wallet", [("purchase", w) for w in (30000, 100000)] + [(k, 30000) for k in ("receipt_stock", "receipt_custom", "receipt_renewal")])
def test_legacy_miniapp_custom_receipt_preserved(mini, monkeypatch, representation, discriminator, kind, wallet):
    sid, oid, path, kwargs, calls = prepare(mini, monkeypatch, representation, kind, wallet, discriminator=discriminator)
    code, result = _call(mini.server, "POST", path, token=MAIN_TOKEN, tg_id=5101, **kwargs)
    assert code == 200
    if kind == "purchase":
        assert mini.main.get_wallet_credit(5101) == 0
        with mini.main._get_conn() as conn:
            assert tuple(conn.execute("SELECT user_id,is_custom_config,custom_username,custom_volume_gb,custom_panel_server_id,base_price,wallet_used,final_price,status FROM orders").fetchone()) == (5101, 1, "safe_custom", 10, sid, 100000, wallet, 100000-wallet, "approved" if wallet == 100000 else "pending")
            rows = conn.execute("SELECT user_id,username,volume_gb,duration_days,subscription_url,source,order_id FROM custom_configs").fetchall()
            assert conn.execute("SELECT COUNT(*) FROM custom_config_history").fetchone()[0] == (1 if wallet == 100000 else 0)
        if wallet == 30000:
            assert result["status"] == "pending_payment" and result["order_id"] == 1 and result["final_price"] == 70000
            assert calls == [] and rows == []
        else:
            assert result == {"status": "approved", "order_id": 1, "link": LINK}
            assert calls == [("factory", sid), ("create", "safe_custom", 10, 30)]
            assert [tuple(r) for r in rows] == [(5101, "safe_custom", 10, 30, LINK, "custom_config", 1)]
    else:
        assert result == {"status": "sent"} and mini.main.get_wallet_credit(5101) == wallet
        assert len(calls) == 1 and calls[0][0] == "receipt"
        _, caption, markup, photo, filename, content_type = calls[0]
        assert f"#{oid}" in caption and "🆔 آیدی عددی: 5101" in caption
        assert "💵 مبلغ قابل پرداخت: 100,000 تومان" in caption and "💰 قیمت پایه: 100,000 تومان" in caption
        assert ("Safe stock" if kind == "receipt_stock" else "safe_custom" if kind == "receipt_custom" else "---") in caption
        assert markup["inline_keyboard"][0][0]["callback_data"] == f"order_approve:{oid}"
        assert markup["inline_keyboard"][0][1]["callback_data"] == f"order_reject:{oid}"
        assert (photo, filename, content_type) == (b"synthetic-receipt", "receipt.jpg", "image/jpeg")
        order = mini.main.get_order(oid)
        assert (order["status"], order["final_price"], order["receipt_file_id"], order["receipt_type"], order["admin_chat_id"], order["admin_message_id"]) == ("pending", 100000, "synthetic-receipt-file", "photo", 9001, 77)
    assert mini.alerts == [] and mini.subs == []
