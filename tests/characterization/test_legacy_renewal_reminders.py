"""Characterize ``renewal_engine.execute_renewal`` and
``renewal_reminders.check_and_process_auto_renewals`` at commit 4edc021.

Baseline: ``.venv/bin/python -m pytest tests/characterization/test_legacy_renewal_reminders.py --network=deny``.
The panel provider and Telegram are synthetic substitutes, not evidence.
Manual full renewal carries the remaining volume over and reads the new limit
back (case 1); automatic renewal replaces it (case 14).

Known unsafe behavior pinned here: the panel changes before the local record,
so a failed or ambiguous read-back or a crash leaves the panel renewed and the
local record unchanged (cases 5, 6, 8); ``execute_renewal`` never checks or
changes the order, so running it twice renews twice (cases 1, 9); automatic
renewal leaves the local volume unchanged although the panel volume was
replaced (case 14); automatic renewal adds the accumulated ``duration_days``,
so the period and price grow every cycle (case 15); with no renewal prices
set, every due auto-renew service gets a daily low-balance alert (case 17); a
crash after the automatic panel update and before the debit leaves the service
due, so the next cycle renews on the panel again and charges once (case 19);
expired services are still auto-renewed (case 20).
"""

import asyncio
import sqlite3
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

import database
import panel_providers
import renewal_engine
import renewal_reminders
from panel_providers.base import PanelError, PanelUserResult
from tests._harness.crash import CrashPlan, SimulatedCrash
from tests._harness.legacy_bot import RecordingBot, TelegramEvent, TelegramLog


RENEWED = "✅ سرویس شما با موفقیت تمدید شد."
NOT_FOUND = "این سرویس دیگر یافت نشد (شاید قبلا\u064b حذف شده)."
SERVER_GONE = "سرور پنل مربوط به این سرویس یافت نشد یا غیرفعال است."
BAD_KIND = "نوع سرویس برای تمدید نامعتبر است."
AUTO_DONE_13000 = "🔄 کانفیگ «auto_1» با موفقیت به\u200cصورت خودکار تمدید شد و 13,000 تومان از کیف پول شما کسر شد."
LOW_13000_5000 = "⚠\ufe0f تمدید خودکار کانفیگ «auto_1» به\u200cدلیل کمبود موجودی کیف پول انجام نشد.\nمبلغ لازم: 13,000 تومان — موجودی فعلی: 5,000 تومان.\nلطفا\u064b کیف پول خود را شارژ کنید یا تمدید خودکار را از صفحه\u200cی سرویس خاموش کنید."
LOW_0_50000 = "⚠\ufe0f تمدید خودکار کانفیگ «auto_1» به\u200cدلیل کمبود موجودی کیف پول انجام نشد.\nمبلغ لازم: 0 تومان — موجودی فعلی: 50,000 تومان.\nلطفا\u064b کیف پول خود را شارژ کنید یا تمدید خودکار را از صفحه\u200cی سرویس خاموش کنید."
HISTORY_FULL = "+20 گیگ / +30 روز"
HISTORY_VOLUME = "+5 گیگ / +0 روز"
HISTORY_TIME = "+0 گیگ / +10 روز"
HISTORY_DAYS_30 = "+0 گیگ / +30 روز"
HISTORY_AUTO_13000 = "10 گیگ / 30 روز — 13,000 تومان از کیف پول"
OWNER = 9001
BUYER = 1001
OTHER_USER = 1002
GIB = 1024 ** 3
FAR = "2030-01-01T00:00:00"


@pytest.fixture
def shop(tmp_path):
    db = database.Database(str(tmp_path / "main.db"))
    db.init_db(OWNER)
    db.add_or_update_user(BUYER, "ali", "Ali")
    db.add_or_update_user(OTHER_USER, "sara", "Sara")
    server_id = db.add_panel_server(
        "Test panel", "pasarguard", "https://panel.example.invalid", "admin", "not-a-secret"
    )
    cc = db.add_custom_config(
        BUYER,
        server_id,
        "cust_1",
        10,
        30,
        "https://sub.example.invalid/cust-1",
        expires_at=FAR,
    )
    return SimpleNamespace(db=db, db_path=str(tmp_path / "main.db"), server_id=server_id, cc=cc)


@pytest.fixture(autouse=True)
def panel(shop, monkeypatch):
    panel = SimpleNamespace(calls=[], seen=[], errors={}, data_limit_bytes=26 * GIB)
    server = shop.db.get_panel_server(shop.server_id)

    class Provider:
        async def update_user(self, username, **kwargs):
            panel.calls.append(("update_user", server["id"], username, kwargs))
            panel.seen.append(service_by_name(shop, username))
            await asyncio.sleep(0)
            errors = panel.errors.get("update_user")
            if errors:
                raise errors.pop(0)
            return PanelUserResult(username, "https://sub.example.invalid/" + username)

        async def get_user_usage(self, username):
            panel.calls.append(("get_user_usage", server["id"], username))
            errors = panel.errors.get("get_user_usage")
            if errors:
                raise errors.pop(0)
            return {
                "used_bytes": 4 * GIB,
                "data_limit_bytes": panel.data_limit_bytes,
                "status": "active",
            }

    def factory(_server):
        return Provider()

    monkeypatch.setattr(renewal_engine, "get_provider", factory)
    monkeypatch.setattr(panel_providers, "get_provider", factory)
    return panel


def rows(shop, statement, params=()):
    conn = sqlite3.connect(shop.db_path)
    conn.row_factory = sqlite3.Row
    try:
        return [dict(row) for row in conn.execute(statement, params).fetchall()]
    finally:
        conn.close()


def sql(shop, statement, params=()):
    conn = sqlite3.connect(shop.db_path)
    try:
        conn.execute(statement, params)
        conn.commit()
    finally:
        conn.close()


def service(shop, cc_id):
    found = rows(
        shop,
        "SELECT volume_gb, duration_days, expires_at FROM custom_configs WHERE id=?",
        (cc_id,),
    )
    return tuple(found[0][key] for key in ("volume_gb", "duration_days", "expires_at"))


def service_by_name(shop, username):
    found = rows(
        shop,
        "SELECT volume_gb, duration_days, expires_at FROM custom_configs WHERE username=?",
        (username,),
    )
    return tuple(found[0][key] for key in ("volume_gb", "duration_days", "expires_at"))


def history(shop, cc_id):
    found = rows(
        shop,
        "SELECT event_type, detail FROM custom_config_history WHERE custom_config_id=? AND event_type!='purchase' ORDER BY id",
        (cc_id,),
    )
    return [(row["event_type"], row["detail"]) for row in found]


def order(shop, mode, add_volume, add_days, *, kind="custom", target=None, user=BUYER):
    order_id = shop.db.create_renewal_order(
        user,
        kind,
        shop.cc if target is None else target,
        mode,
        add_volume,
        add_days,
        1000,
    )
    return shop.db.get_order(order_id)


def now_naive():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def auto_service(shop, username="auto_1", *, hours=2, volume=10, duration=30, auto=True):
    expires = (now_naive() + timedelta(hours=hours)).isoformat()
    cc_id = shop.db.add_custom_config(
        BUYER,
        shop.server_id,
        username,
        volume,
        duration,
        "https://sub.example.invalid/" + username,
        expires_at=expires,
    )
    if auto:
        shop.db.set_custom_config_auto_renew(cc_id, BUYER, True)
    return cc_id, expires


def priced(shop):
    shop.db.set_setting("renewal_price_per_gb", "1000")
    shop.db.set_setting("renewal_price_per_day", "100")


def run_auto(shop, log):
    return asyncio.run(renewal_reminders.check_and_process_auto_renewals(RecordingBot(log), shop.db))


def UPDATE(shop, username, kwargs):
    return ("update_user", shop.server_id, username, kwargs)


def READ(shop):
    return ("get_user_usage", shop.server_id, "cust_1")


def test_full_renewal_updates_panel_reads_back_then_local(shop, panel):
    o = order(shop, "full", 20, 30)
    result = asyncio.run(renewal_engine.execute_renewal(shop.db, o))
    assert result == RENEWED
    assert panel.calls == [
        UPDATE(shop, "cust_1", {"add_volume_gb": 20, "add_days": 30, "reset_usage": True, "preserve_remaining": True}),
        READ(shop),
    ]
    assert panel.seen == [(10, 30, FAR)]
    assert service(shop, shop.cc) == (26, 60, "2030-01-31T00:00:00")
    assert history(shop, shop.cc) == [("renewal", HISTORY_FULL)]
    assert shop.db.get_order(o["id"])["status"] == "pending"


def test_volume_and_time_renewals_add_without_reset(shop, panel):
    volume_order = order(shop, "volume", 5, 0)
    assert asyncio.run(renewal_engine.execute_renewal(shop.db, volume_order)) == RENEWED
    assert panel.calls == [UPDATE(shop, "cust_1", {"add_volume_gb": 5, "add_days": 0, "reset_usage": False, "preserve_remaining": False})]
    assert service(shop, shop.cc) == (15, 30, FAR)
    time_order = order(shop, "time", 0, 10)
    assert asyncio.run(renewal_engine.execute_renewal(shop.db, time_order)) == RENEWED
    assert panel.calls[-1] == UPDATE(shop, "cust_1", {"add_volume_gb": 0, "add_days": 10, "reset_usage": False, "preserve_remaining": False})
    assert service(shop, shop.cc) == (15, 40, "2030-01-11T00:00:00")
    assert history(shop, shop.cc) == [("renewal", HISTORY_VOLUME), ("renewal", HISTORY_TIME)]


def test_full_renewal_without_volume_skips_read_back(shop, panel):
    o = order(shop, "full", 0, 30)
    assert asyncio.run(renewal_engine.execute_renewal(shop.db, o)) == RENEWED
    assert panel.calls == [UPDATE(shop, "cust_1", {"add_volume_gb": 0, "add_days": 30, "reset_usage": True, "preserve_remaining": True})]
    assert service(shop, shop.cc) == (10, 60, "2030-01-31T00:00:00")
    assert history(shop, shop.cc) == [("renewal", HISTORY_DAYS_30)]


def test_expired_service_extends_from_now(shop, panel):
    sql(shop, "UPDATE custom_configs SET expires_at='2020-01-01T00:00:00' WHERE id=?", (shop.cc,))
    before = now_naive()
    o = order(shop, "time", 0, 10)
    asyncio.run(renewal_engine.execute_renewal(shop.db, o))
    after = now_naive()
    expires_at = datetime.fromisoformat(service(shop, shop.cc)[2])
    assert before + timedelta(days=10) <= expires_at <= after + timedelta(days=10)
    assert service(shop, shop.cc)[1] == 40


def test_ambiguous_read_back_keeps_panel_change_only(shop, panel):
    panel.errors["get_user_usage"] = [PanelError("read-back timed out")]
    o = order(shop, "full", 20, 30)
    with pytest.raises(renewal_engine.RenewalError) as exc:
        asyncio.run(renewal_engine.execute_renewal(shop.db, o))
    assert str(exc.value) == "read-back timed out"
    assert isinstance(exc.value.__cause__, PanelError)
    assert panel.calls == [UPDATE(shop, "cust_1", {"add_volume_gb": 20, "add_days": 30, "reset_usage": True, "preserve_remaining": True}), READ(shop)]
    assert service(shop, shop.cc) == (10, 30, FAR)
    assert history(shop, shop.cc) == []


def test_unexpected_read_back_error_propagates(shop, panel):
    panel.errors["get_user_usage"] = [TimeoutError("read timed out")]
    o = order(shop, "full", 20, 30)
    with pytest.raises(TimeoutError):
        asyncio.run(renewal_engine.execute_renewal(shop.db, o))
    assert len(panel.calls) == 2
    assert service(shop, shop.cc) == (10, 30, FAR)
    assert history(shop, shop.cc) == []


def test_panel_update_error_becomes_renewal_error(shop, panel):
    panel.errors["update_user"] = [PanelError("panel down")]
    o = order(shop, "full", 20, 30)
    with pytest.raises(renewal_engine.RenewalError, match="panel down"):
        asyncio.run(renewal_engine.execute_renewal(shop.db, o))
    assert len(panel.calls) == 1
    assert service(shop, shop.cc) == (10, 30, FAR)


def test_crash_between_panel_and_local_record(shop, panel, monkeypatch):
    plan = CrashPlan().arm("after_panel_update")

    def crash(*args, **kwargs):
        plan("after_panel_update")

    monkeypatch.setattr(shop.db, "apply_custom_config_renewal", crash)
    o = order(shop, "full", 20, 30)
    with pytest.raises(SimulatedCrash):
        asyncio.run(renewal_engine.execute_renewal(shop.db, o))
    assert plan.crashed_at == "after_panel_update"
    assert panel.calls == [UPDATE(shop, "cust_1", {"add_volume_gb": 20, "add_days": 30, "reset_usage": True, "preserve_remaining": True}), READ(shop)]
    assert service(shop, shop.cc) == (10, 30, FAR)
    assert history(shop, shop.cc) == []


def test_renewal_is_not_idempotent(shop, panel):
    o = order(shop, "time", 0, 10)
    assert asyncio.run(renewal_engine.execute_renewal(shop.db, o)) == RENEWED
    assert asyncio.run(renewal_engine.execute_renewal(shop.db, o)) == RENEWED
    assert len([call for call in panel.calls if call[0] == "update_user"]) == 2
    assert service(shop, shop.cc) == (10, 50, "2030-01-21T00:00:00")
    assert [event for event, _ in history(shop, shop.cc)] == ["renewal", "renewal"]
    assert shop.db.get_order(o["id"])["status"] == "pending"


def test_target_of_another_user_is_not_found(shop, panel):
    o = order(shop, "full", 20, 30, user=OTHER_USER)
    with pytest.raises(renewal_engine.RenewalError) as exc:
        asyncio.run(renewal_engine.execute_renewal(shop.db, o))
    assert str(exc.value) == NOT_FOUND
    assert panel.calls == []


def test_inactive_server_is_refused(shop, panel):
    sql(shop, "UPDATE panel_servers SET is_active=0")
    o = order(shop, "full", 20, 30)
    with pytest.raises(renewal_engine.RenewalError, match=SERVER_GONE):
        asyncio.run(renewal_engine.execute_renewal(shop.db, o))
    assert panel.calls == []


def test_unknown_target_kind_is_refused(shop, panel):
    o = order(shop, "full", 1, 1, kind="bogus")
    with pytest.raises(renewal_engine.RenewalError, match=BAD_KIND):
        asyncio.run(renewal_engine.execute_renewal(shop.db, o))
    assert panel.calls == []


def test_pool_config_renewal_is_local_only(shop, panel):
    cat = shop.db.add_category("VPN")
    pid = shop.db.add_product(cat, "Stock 30d", 100_000)
    shop.db.add_configs(pid, ["vless://pool-1"])
    sql(shop, "UPDATE configs SET is_used=1, assigned_user_id=?, expires_at=? WHERE id=1", (BUYER, FAR))
    o = order(shop, "full", 20, 10, kind="config", target=1)
    assert asyncio.run(renewal_engine.execute_renewal(shop.db, o)) == RENEWED
    assert rows(shop, "SELECT expires_at FROM configs WHERE id=1")[0]["expires_at"] == "2030-01-11T00:00:00"
    assert panel.calls == []
    other_order = order(shop, "full", 20, 10, kind="config", target=1, user=OTHER_USER)
    with pytest.raises(renewal_engine.RenewalError) as exc:
        asyncio.run(renewal_engine.execute_renewal(shop.db, other_order))
    assert str(exc.value) == NOT_FOUND


def test_auto_renewal_replaces_and_debits(shop, panel):
    priced(shop)
    shop.db.add_wallet_credit(BUYER, 50_000)
    cc, old = auto_service(shop)
    log = TelegramLog()
    assert run_auto(shop, log) == 1
    assert panel.calls == [UPDATE(shop, "auto_1", {"add_volume_gb": 10, "add_days": 30, "reset_usage": True})]
    assert panel.seen == [(10, 30, old)]
    assert shop.db.get_wallet_credit(BUYER) == 37_000
    assert service(shop, cc) == (10, 60, (datetime.fromisoformat(old) + timedelta(days=30)).isoformat())
    assert history(shop, cc) == [("renewal", HISTORY_DAYS_30), ("auto_renew", HISTORY_AUTO_13000)]
    assert log.events == [TelegramEvent("send_message", BUYER, 1, AUTO_DONE_13000)]


def test_auto_renewal_period_and_price_grow(shop, panel):
    priced(shop)
    shop.db.add_wallet_credit(BUYER, 50_000)
    cc, _old = auto_service(shop)
    assert run_auto(shop, TelegramLog()) == 1
    sql(shop, "UPDATE custom_configs SET expires_at=? WHERE id=?", ((now_naive() + timedelta(hours=2)).isoformat(), cc))
    assert run_auto(shop, TelegramLog()) == 1
    assert panel.calls[1] == UPDATE(shop, "auto_1", {"add_volume_gb": 10, "add_days": 60, "reset_usage": True})
    assert shop.db.get_wallet_credit(BUYER) == 21_000
    assert service(shop, cc)[1] == 120


def test_low_balance_alerts_once_per_day(shop, panel):
    priced(shop)
    shop.db.add_wallet_credit(BUYER, 5_000)
    cc, _old = auto_service(shop)
    log = TelegramLog()
    assert run_auto(shop, log) == 0
    assert log.events == [TelegramEvent("send_message", BUYER, 1, LOW_13000_5000)]
    assert panel.calls == []
    assert rows(shop, "SELECT auto_renew_alert_date FROM custom_configs WHERE id=?", (cc,))[0]["auto_renew_alert_date"] == datetime.now(timezone.utc).date().isoformat()
    assert shop.db.get_wallet_credit(BUYER) == 5_000
    assert run_auto(shop, log) == 0
    assert len(log.events) == 1


def test_unpriced_auto_renewal_always_alerts(shop, panel):
    shop.db.add_wallet_credit(BUYER, 50_000)
    auto_service(shop)
    log = TelegramLog()
    assert run_auto(shop, log) == 0
    assert log.events == [TelegramEvent("send_message", BUYER, 1, LOW_0_50000)]
    assert panel.calls == []
    assert shop.db.get_wallet_credit(BUYER) == 50_000


def test_auto_renewal_panel_error_skips_without_debit(shop, panel):
    priced(shop)
    shop.db.add_wallet_credit(BUYER, 50_000)
    cc, old = auto_service(shop)
    panel.errors["update_user"] = [PanelError("panel down")]
    log = TelegramLog()
    assert run_auto(shop, log) == 0
    assert len(panel.calls) == 1
    assert shop.db.get_wallet_credit(BUYER) == 50_000
    assert service(shop, cc) == (10, 30, old)
    assert history(shop, cc) == []
    assert log.events == []


def test_crash_before_debit_renews_again_next_cycle(shop, panel, monkeypatch):
    priced(shop)
    shop.db.add_wallet_credit(BUYER, 50_000)
    cc, old = auto_service(shop)
    plan = CrashPlan().arm("before_debit")
    original = shop.db.add_wallet_credit

    def debit(user_id, delta):
        plan("before_debit")
        return original(user_id, delta)

    monkeypatch.setattr(shop.db, "add_wallet_credit", debit)
    with pytest.raises(SimulatedCrash):
        run_auto(shop, TelegramLog())
    assert len(panel.calls) == 1
    assert shop.db.get_wallet_credit(BUYER) == 50_000
    assert service(shop, cc) == (10, 30, old)
    assert run_auto(shop, TelegramLog()) == 1
    assert len(panel.calls) == 2
    assert shop.db.get_wallet_credit(BUYER) == 37_000
    assert service(shop, cc)[1] == 60


def test_auto_renewal_due_selection(shop, panel):
    priced(shop)
    shop.db.add_wallet_credit(BUYER, 100_000)
    auto_service(shop, "expired_1", hours=-48)
    auto_service(shop, "later_1", hours=48)
    auto_service(shop, "manual_1", auto=False)
    auto_service(shop, "unlimited_1", duration=0)
    disabled, _ = auto_service(shop, "disabled_1")
    sql(shop, "UPDATE custom_configs SET enabled=0 WHERE id=?", (disabled,))
    assert run_auto(shop, TelegramLog()) == 1
    assert [call[2] for call in panel.calls] == ["expired_1"]
    assert shop.db.get_wallet_credit(BUYER) == 87_000
