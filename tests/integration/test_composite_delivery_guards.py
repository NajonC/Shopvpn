"""T050c: prevent composite order/product secrets entering legacy delivery."""
import asyncio

import pytest

import config_delivery
from tests._harness.legacy_bot import RecordingBot, TelegramLog
from tests.characterization.test_direct_provision import BUYER, _order, shop
from tests.integration.test_composite_legacy_guards import as_row


@pytest.fixture
def delivery(monkeypatch):
    qr, fetched = [], []

    def build_photo(link):
        qr.append(link)
        return object()

    async def fetch(link):
        fetched.append(link)
        return ["vless://individual-synthetic"]

    monkeypatch.setattr(config_delivery, "_build_qr_photo", build_photo)
    monkeypatch.setattr(config_delivery, "fetch_individual_links", fetch)
    return qr, fetched


def inject_metadata(shop, monkeypatch, representation, *, composite=None, discriminator="legacy"):
    oid = _order(shop)
    order = dict(shop.db.get_order(oid))
    product = dict(shop.db.get_product(shop.product_id))
    for row in (order, product):
        row.pop("service_kind", None)
        if discriminator is not None:
            row["service_kind"] = discriminator
    if composite:
        (order if composite == "order" else product)["service_kind"] = "composite"
    monkeypatch.setattr(shop.db, "get_order", lambda key: as_row(order, representation) if key == oid else None)
    monkeypatch.setattr(shop.db, "get_product", lambda key: as_row(product, representation) if key == shop.product_id else None)
    return oid


@pytest.mark.parametrize("representation", ["dict", "sqlite"])
@pytest.mark.parametrize("source", ["order", "product"])
def test_composite_delivery_refused_before_publication(shop, delivery, monkeypatch, caplog, representation, source):
    oid = inject_metadata(shop, monkeypatch, representation, composite=source)
    log = TelegramLog()
    link = "https://sub.example.invalid/SECRET-DELIVERY-LINK"
    with shop.db._get_conn() as conn:
        before = list(conn.iterdump())
    with pytest.raises(ValueError, match="(?i)composite") as error:
        asyncio.run(config_delivery.deliver_config_to_user(
            RecordingBot(log), BUYER, "SECRET-DELIVERY-NAME", link, order_id=oid, db=shop.db))
    assert log.events == []
    assert delivery == ([], [])
    with shop.db._get_conn() as conn:
        assert list(conn.iterdump()) == before
    assert "SECRET-DELIVERY" not in str(error.value)
    assert "SECRET-DELIVERY" not in caplog.text


@pytest.mark.parametrize("representation", ["dict", "sqlite"])
@pytest.mark.parametrize("discriminator", [None, "legacy"])
def test_legacy_delivery_preserves_photo_link_and_individuals(shop, delivery, monkeypatch, representation, discriminator):
    oid = inject_metadata(shop, monkeypatch, representation, discriminator=discriminator)
    log = TelegramLog()
    link = "https://sub.example.invalid/legacy-delivery"
    assert asyncio.run(config_delivery.deliver_config_to_user(
        RecordingBot(log), BUYER, "Legacy plan", link, order_id=oid, db=shop.db)) is None
    assert [e.kind for e in log.events] == ["send_photo", "send_message", "send_message"]
    assert all(e.chat_id == BUYER for e in log.events)
    assert link in log.events[1].text
    assert "vless://individual-synthetic" in log.events[2].text
    assert delivery == ([link], [link])


def test_legacy_delivery_without_database_still_works(delivery):
    log = TelegramLog()
    link = "https://sub.example.invalid/legacy-delivery"
    assert asyncio.run(config_delivery.deliver_config_to_user(RecordingBot(log), BUYER, "Legacy plan", link)) is None
    assert [e.kind for e in log.events] == ["send_photo", "send_message", "send_message"]
    assert all(e.chat_id == BUYER for e in log.events)
    assert delivery == ([link], [link])
