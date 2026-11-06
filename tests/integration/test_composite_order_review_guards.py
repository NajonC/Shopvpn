"""T050d: legacy order review must not claim, settle, or publish composites."""
import asyncio
import httpx
import pytest

from tests._harness.legacy_bot import use_synthetic_bot_settings
use_synthetic_bot_settings()
import handlers_admin
from tests._harness.legacy_bot import FakeCallbackQuery, FakeMessage, FakeUser, RecordingBot, TelegramLog, find_handler
from tests._harness.legacy_web import drain_tasks, load_admin_panel, session_cookie
from tests.characterization.test_order_approval import (
    OWNER, WEB_OWNER, custom_order, direct_order, remote, renewal_order, shop, site, stock_order, track,
)
from tests.integration.test_composite_legacy_guards import as_row


def prepare(shop, remote, monkeypatch, kind, source, representation, discriminator="legacy"):
    oid = renewal_order(shop, remote) if kind == "renewal" else {"stock": stock_order, "direct": direct_order, "custom": custom_order}[kind](shop)
    order = dict(shop.db.get_order(oid))
    product = dict(shop.db.get_product(order["product_id"])) if order["product_id"] else None
    for row in (order, product):
        if row is not None:
            row.pop("service_kind", None)
            if discriminator is not None:
                row["service_kind"] = discriminator
    if source:
        (order if source == "order" else product)["service_kind"] = "composite"
    order["receipt_file_id"] = "SECRET-ORDER-RECEIPT"
    original = shop.db.get_product
    monkeypatch.setattr(shop.db, "get_order", lambda key: as_row(order, representation) if key == oid else None)
    if product is not None:
        monkeypatch.setattr(shop.db, "get_product", lambda key: as_row(product, representation) if key == order["product_id"] else original(key))
    return oid


async def invoke(shop, log, action, channel, oid):
    if channel == "telegram":
        handler = find_handler(handlers_admin.create_admin_router(shop.db, is_main_bot=True), "callback_query", "cb_order_" + action)
        call = FakeCallbackQuery(log, FakeUser(OWNER), f"order_{action}:{oid}", FakeMessage(log, OWNER, caption="Synthetic receipt"))
        await handler(call, RecordingBot(log))
        return None
    web = load_admin_panel()
    cookie = session_cookie(web.ADMIN_PANEL_SECRET, *WEB_OWNER)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=web.app, raise_app_exceptions=False), base_url="http://panel.test") as client:
        result = await client.post(f"/api/orders/{oid}/{action}", headers={"Cookie": f"panel_session={cookie}"})
    await drain_tasks()
    return result


@pytest.mark.parametrize("kind,source", [(k,"order") for k in ("stock","direct","custom","renewal")] + [(k,"product") for k in ("stock","direct")])
@pytest.mark.parametrize("representation", ["dict", "sqlite"])
@pytest.mark.parametrize("channel", ["telegram", "web"])
@pytest.mark.parametrize("action", ["approve", "reject"])
def test_composite_order_review_refused_before_effects(shop, site, remote, monkeypatch, caplog, kind, source, representation, channel, action):
    oid = prepare(shop, remote, monkeypatch, kind, source, representation)
    log = TelegramLog() if channel == "telegram" else site.log
    effects = track(monkeypatch, shop.db, remote, log)
    reject = shop.db.reject_order
    def reject_spy(*args, **kwargs):
        effects.append(("reject_order", len(log.events)))
        return reject(*args, **kwargs)
    monkeypatch.setattr(shop.db, "reject_order", reject_spy)
    with shop.db._get_conn() as conn:
        before = list(conn.iterdump())
    users = dict(remote.users)
    response = asyncio.run(invoke(shop, log, action, channel, oid))
    assert effects == []
    assert remote.calls == [] and remote.users == users
    with shop.db._get_conn() as conn:
        assert list(conn.iterdump()) == before
    if channel == "telegram":
        assert len(log.events) == 1
        assert log.events[0].kind == "callback_answer" and log.events[0].show_alert
        assert "composite" in (log.events[0].text or "").lower()
    else:
        assert response.status_code == 403
        assert "composite" in response.json()["detail"].lower()
        assert "SECRET-ORDER" not in response.text
        assert log.events == []
    assert "SECRET-ORDER" not in caplog.text
    assert all("SECRET-ORDER" not in (e.text or "") for e in log.events)


@pytest.mark.parametrize("discriminator", [None, "legacy"])
@pytest.mark.parametrize("representation", ["dict", "sqlite"])
@pytest.mark.parametrize("channel", ["telegram", "web"])
@pytest.mark.parametrize("action", ["approve", "reject"])
def test_legacy_order_review_still_settles(shop, site, remote, monkeypatch, discriminator, representation, channel, action):
    oid = prepare(shop, remote, monkeypatch, "stock", None, representation, discriminator)
    log = TelegramLog() if channel == "telegram" else site.log
    response = asyncio.run(invoke(shop, log, action, channel, oid))
    with shop.db._get_conn() as conn:
        status = conn.execute("SELECT status FROM orders WHERE id=?", (oid,)).fetchone()[0]
        used = conn.execute("SELECT COUNT(*) FROM configs WHERE is_used=1").fetchone()[0]
    assert status == ("approved" if action == "approve" else "rejected")
    assert used == (1 if action == "approve" else 0)
    if channel == "web":
        assert response.status_code == 200 and response.json() == {"ok": True}
    assert log.events
