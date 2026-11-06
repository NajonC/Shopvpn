"""T050a: manual renewal dispatch rejects composite orders before legacy effects."""
import asyncio
import sqlite3

import pytest

import renewal_engine
from tests.characterization.test_legacy_renewal_reminders import (
    BUYER, history, order, panel, pool_config, service, shop,
)


def as_row(data, representation):
    if representation == "dict":
        return data
    with sqlite3.connect(":memory:") as conn:
        conn.row_factory = sqlite3.Row
        return conn.execute(
            "SELECT " + ", ".join(f'? AS "{key}"' for key in data), tuple(data.values())
        ).fetchone()


@pytest.mark.parametrize("representation", ["dict", "sqlite"])
@pytest.mark.parametrize("kind", ["custom", "config"])
def test_composite_manual_renewal_refused_without_effects(shop, panel, representation, kind):
    target = shop.cc if kind == "custom" else pool_config(shop, "https://sub.example.invalid/stock")
    renewal = dict(order(shop, "full", 20, 30, kind=kind, target=target))
    renewal["service_kind"] = "composite"
    before = service(shop, shop.cc)
    with shop.db._get_conn() as conn:
        before_sql = list(conn.iterdump())
    with pytest.raises(renewal_engine.RenewalError, match="(?i)composite"):
        asyncio.run(renewal_engine.execute_renewal(shop.db, as_row(renewal, representation)))
    assert panel.calls == []
    assert service(shop, shop.cc) == before
    with shop.db._get_conn() as conn:
        assert list(conn.iterdump()) == before_sql
    assert history(shop, shop.cc) == []


@pytest.mark.parametrize("representation", ["dict", "sqlite"])
@pytest.mark.parametrize("discriminator", [None, "legacy"])
def test_legacy_manual_renewal_still_runs(shop, panel, representation, discriminator):
    renewal = dict(order(shop, "time", 0, 10))
    renewal.pop("service_kind", None)
    if discriminator is not None:
        renewal["service_kind"] = discriminator
    assert asyncio.run(renewal_engine.execute_renewal(shop.db, as_row(renewal, representation))) == "✅ سرویس شما با موفقیت تمدید شد."
    assert len(panel.calls) == 1
    assert panel.calls[0][3] == {"add_volume_gb": 0, "add_days": 10, "reset_usage": False, "preserve_remaining": False}
    assert service(shop, shop.cc)[1] == 40
    assert history(shop, shop.cc) == [("renewal", "+0 گیگ / +10 روز")]
