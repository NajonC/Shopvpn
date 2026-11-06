"""T050b: never debit, renew, or send low-wallet alerts for composite candidates."""
import asyncio

import pytest

import renewal_reminders
from tests._harness.legacy_bot import RecordingBot, TelegramLog
from tests.characterization.test_legacy_renewal_reminders import (
    BUYER, auto_service, history, panel, priced, service, shop,
)
from tests.integration.test_composite_legacy_guards import as_row


@pytest.mark.parametrize("representation", ["dict", "sqlite"])
@pytest.mark.parametrize("balance", [5000, 50000])
def test_composite_auto_renewal_refused_before_effects(shop, panel, monkeypatch, caplog, representation, balance):
    priced(shop)
    shop.db.add_wallet_credit(BUYER, balance)
    cc, _ = auto_service(shop)
    row = dict(shop.db.get_custom_configs_due_for_auto_renew()[0])
    row["service_kind"] = "composite"
    row["subscription_url"] = "https://sub.example.invalid/SECRET-AUTO-LINK"
    monkeypatch.setattr(shop.db, "get_custom_configs_due_for_auto_renew", lambda: [as_row(row, representation)])
    log = TelegramLog()
    with shop.db._get_conn() as conn:
        before = list(conn.iterdump())
    assert asyncio.run(renewal_reminders.check_and_process_auto_renewals(RecordingBot(log), shop.db)) == 0
    assert panel.calls == []
    assert log.events == []
    assert shop.db.get_wallet_credit(BUYER) == balance
    assert history(shop, cc) == []
    with shop.db._get_conn() as conn:
        assert list(conn.iterdump()) == before
    messages = [r.getMessage().lower() for r in caplog.records if r.levelname == "WARNING"]
    assert any("composite" in m and "auto" in m for m in messages)
    assert "SECRET-AUTO-LINK" not in caplog.text


@pytest.mark.parametrize("representation", ["dict", "sqlite"])
@pytest.mark.parametrize("discriminator", [None, "legacy"])
def test_legacy_auto_renewal_still_debits_and_extends(shop, panel, monkeypatch, representation, discriminator):
    priced(shop)
    shop.db.add_wallet_credit(BUYER, 50000)
    cc, _ = auto_service(shop)
    row = dict(shop.db.get_custom_configs_due_for_auto_renew()[0])
    if discriminator is not None:
        row["service_kind"] = discriminator
    monkeypatch.setattr(shop.db, "get_custom_configs_due_for_auto_renew", lambda: [as_row(row, representation)])
    log = TelegramLog()
    assert asyncio.run(renewal_reminders.check_and_process_auto_renewals(RecordingBot(log), shop.db)) == 1
    assert shop.db.get_wallet_credit(BUYER) == 37000
    assert service(shop, cc)[1] == 60
    assert len(panel.calls) == 1
    assert panel.calls[0][3] == {"add_volume_gb": 10, "add_days": 30, "reset_usage": True}
    assert history(shop, cc) == [("renewal", "+0 گیگ / +30 روز"), ("auto_renew", "10 گیگ / 30 روز — 13,000 تومان از کیف پول")]
    assert len(log.events) == 1


@pytest.mark.parametrize("representation", ["dict", "sqlite"])
def test_composite_auto_candidate_does_not_block_later_legacy(shop, panel, monkeypatch, representation):
    priced(shop)
    shop.db.add_wallet_credit(BUYER, 50000)
    cc, _ = auto_service(shop)
    row = dict(shop.db.get_custom_configs_due_for_auto_renew()[0])
    composite = dict(row, service_kind="composite")
    legacy = dict(row, service_kind="legacy")
    monkeypatch.setattr(shop.db, "get_custom_configs_due_for_auto_renew", lambda: [as_row(composite, representation), as_row(legacy, representation)])
    log = TelegramLog()
    assert asyncio.run(renewal_reminders.check_and_process_auto_renewals(RecordingBot(log), shop.db)) == 1
    assert shop.db.get_wallet_credit(BUYER) == 37000
    assert service(shop, cc)[1] == 60
    assert len(panel.calls) == 1
    assert len(log.events) == 1
    assert history(shop, cc) == [("renewal", "+0 گیگ / +30 روز"), ("auto_renew", "10 گیگ / 30 روز — 13,000 تومان از کیف پول")]
