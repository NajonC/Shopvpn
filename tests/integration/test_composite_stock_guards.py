"""T050a: stock alerts guard rejects composite products before legacy alert state."""
import asyncio
import logging
import sqlite3

import pytest

import stock_alerts


def as_row(data, representation):
    if representation == "dict":
        return data
    with sqlite3.connect(":memory:") as conn:
        conn.row_factory = sqlite3.Row
        return conn.execute(
            "SELECT " + ", ".join(f'? AS "{key}"' for key in data), tuple(data.values())
        ).fetchone()


class FakeSender:
    def __init__(self):
        self.calls = []

    async def __call__(self, admin_id, text):
        self.calls.append((admin_id, text))


class FakeDB:
    def __init__(self, stock=2, threshold="3", should_alert=True, product=None, admins=None):
        self.stock = stock
        self.threshold = threshold
        self.should_alert = should_alert
        self.product = product
        self.admins = admins if admins is not None else [9001, 9002]
        self.state_calls = []

    def count_available_configs(self, product_id):
        return self.stock

    def get_setting(self, key, default="3"):
        if key == "low_stock_threshold":
            return self.threshold
        return default

    def check_low_stock_alert_state(self, product_id, stock, threshold):
        self.state_calls.append((product_id, stock, threshold))
        return self.should_alert

    def get_product(self, product_id):
        if product_id == 7:
            return self.product
        return None

    def list_admins(self):
        return list(self.admins)


@pytest.mark.parametrize("representation", ["dict", "sqlite"])
def test_composite_stock_refused_before_alert_state(caplog, representation):
    product_data = {
        "id": 7,
        "name": "Synthetic plan SECRET-STOCK-NAME",
        "service_kind": "composite",
    }
    product = as_row(product_data, representation)
    db = FakeDB(
        stock=2,
        threshold="3",
        should_alert=True,
        product=product,
        admins=[9001, 9002],
    )
    sender = FakeSender()

    res = asyncio.run(stock_alerts.check_and_notify_low_stock(sender, db, 7))

    assert res is None
    assert sender.calls == []
    assert db.state_calls == []
    warnings = [
        r
        for r in caplog.records
        if r.levelno == logging.WARNING
        and "composite" in r.getMessage().lower()
        and "stock" in r.getMessage().lower()
    ]
    assert len(warnings) >= 1
    assert "SECRET-STOCK-NAME" not in caplog.text


@pytest.mark.parametrize("representation", ["dict", "sqlite"])
@pytest.mark.parametrize("discriminator", [None, "legacy"])
def test_legacy_low_stock_still_notifies(representation, discriminator):
    product_data = {"id": 7, "name": "Synthetic plan"}
    if discriminator is not None:
        product_data["service_kind"] = discriminator
    product = as_row(product_data, representation)
    db = FakeDB(
        stock=2,
        threshold="3",
        should_alert=True,
        product=product,
        admins=[9001, 9002],
    )
    sender = FakeSender()

    res = asyncio.run(stock_alerts.check_and_notify_low_stock(sender, db, 7))

    assert res is None
    assert db.state_calls == [(7, 2, 3)]
    assert len(sender.calls) == 2
    assert [call[0] for call in sender.calls] == [9001, 9002]
    for admin_id, text in sender.calls:
        assert "Synthetic plan" in text
        assert "2" in text
        assert "3" in text


def test_legacy_stock_state_false_sends_nothing():
    product_data = {"id": 7, "name": "Synthetic plan", "service_kind": "legacy"}
    product = as_row(product_data, "dict")
    db = FakeDB(
        stock=2,
        threshold="3",
        should_alert=False,
        product=product,
        admins=[9001, 9002],
    )
    sender = FakeSender()

    res = asyncio.run(stock_alerts.check_and_notify_low_stock(sender, db, 7))

    assert res is None
    assert db.state_calls == [(7, 2, 3)]
    assert sender.calls == []
