"""Characterize ``renewal_engine.execute_renewal``,
``renewal_reminders.check_and_process_auto_renewals``,
``renewal_reminders.check_and_send_renewal_reminders``,
``renewal_reminders.check_and_send_volume_reminders`` and
``connect_alerts.check_and_send_connect_alerts`` at commit 4edc021.

Baseline: ``.venv/bin/python -m pytest tests/characterization/test_legacy_renewal_reminders.py --network=deny``.
The panel provider, subscription-info fetch and Telegram are synthetic substitutes, not evidence.
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
Reminders and alerts are marked sent even when the Telegram send fails (cases 25, 38); a custom config's volume reminder marks the stock config with the same id instead of itself, so the custom service gets a new reminder and a new discount code every cycle and an unrelated stock config is silenced (case 31); expiry reminders use the live subscription expiry, never the stored ``expires_at``, and a service outside the window or expired stays a candidate (cases 21, 22); every reminder creates a new single-use discount code (cases 21, 31).
"""

import asyncio
import re
import sqlite3
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

import database
import connect_alerts
import jalali
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
EXPIRY_TEMPLATE = "⏰ یادآوری اتمام سرویس\n\n📦 سرویس «{product}» شما به\u200cزودی منقضی می\u200cشود.\n\n⌛ حدود {days} روز از سرویس شما باقی مانده (انقضا: {date}).\n\n🎁 برای اینکه دچار قطعی نشوید، یک کد تخفیف اختصاصی {percent}٪ برایتان صادر شد:\n🎟 کد تخفیف: `{code}`\n⏳ این کد فقط تا {expiry_hours} ساعت آینده معتبر است.\n\n✅ اگر همین امروز تمدید کنید، از این تخفیف بهره\u200cمند خواهید شد.\nبرای تمدید، از منوی اصلی «🛒 خرید کانفیگ» را بزنید و هنگام خرید، دکمه\u200cی «🎟 وارد کردن کد تخفیف» را زده و این کد را وارد کنید."
VOLUME_TEMPLATE = "📉 یادآوری اتمام حجم\n\n📦 حجم سرویس «{product}» شما رو به اتمام است.\n\n📊 حدود {remaining} گیگابایت ({left}٪) از حجم شما باقی مانده.\n\n🎁 برای اینکه دچار قطعی نشوید، یک کد تخفیف اختصاصی {percent}٪ برایتان صادر شد:\n🎟 کد تخفیف: `{code}`\n⏳ این کد فقط تا {expiry_hours} ساعت آینده معتبر است.\n\n✅ اگر همین امروز تمدید کنید، از این تخفیف بهره\u200cمند خواهید شد.\nبرای تمدید، از منوی اصلی «🛒 خرید کانفیگ» را بزنید و هنگام خرید، دکمه\u200cی «🎟 وارد کردن کد تخفیف» را زده و این کد را وارد کنید."
CONNECTED = "✅ سرویس شما به کانفیگ متصل شد."
NOT_CONNECTED = "⚠\ufe0f هنوز به سرویس خریداری\u200cشده\u200cتان متصل نشده\u200cاید. برای راهنمای اتصال با پشتیبانی در تماس باشید."
MIB = 1024 ** 2
DAY = 86400
POOL_1 = "https://sub.example.invalid/pool-1"
POOL_2 = "https://sub.example.invalid/pool-2"
CUST_1 = "https://sub.example.invalid/cust-1"
TEST_1 = "https://sub.example.invalid/tst-1"
RENEW_CODE = re.compile(r"RENEW1001\d{4}")
VOLUME_CODE = re.compile(r"VOLUME1001\d{4}")


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


@pytest.fixture
def subs(monkeypatch):
    subs = SimpleNamespace(info={}, fetched=[])

    async def fetch_sub_info(link):
        subs.fetched.append(link)
        return subs.info.get(link, {"ok": False, "error": "unknown link"})

    monkeypatch.setattr(renewal_reminders, "fetch_sub_info", fetch_sub_info)
    monkeypatch.setattr(connect_alerts, "fetch_sub_info", fetch_sub_info)
    return subs


def pool_config(shop, link, *, hours_ago=1):
    cat = shop.db.add_category("VPN")
    pid = shop.db.add_product(cat, "Stock 30d", 100_000)
    shop.db.add_configs(pid, [link])
    sql(shop, "UPDATE configs SET is_used=1, assigned_user_id=?, assigned_at=?, expires_at=? WHERE link=?", (BUYER, (now_naive() - timedelta(hours=hours_ago)).isoformat(), FAR, link))
    return rows(shop, "SELECT id FROM configs WHERE link=?", (link,))[0]["id"]


def usage(used_bytes, *, total=10 * GIB, expire=None):
    return {"ok": True, "upload": 0, "download": used_bytes, "total": total, "expire": expire}


def expire_in(seconds):
    return int(datetime.now(timezone.utc).timestamp() + seconds)


def jalali_of(expire):
    return jalali.to_jalali_str(datetime.fromtimestamp(expire, tz=timezone.utc))


def codes(shop, source):
    return rows(shop, "SELECT code, percent, max_uses, expires_at FROM discount_codes WHERE source=? ORDER BY id", (source,))


def flag(shop, table, cid, column):
    return rows(shop, f"SELECT {column} FROM {table} WHERE id=?", (cid,))[0][column]


def fetch_count(subs, link):
    return subs.fetched.count(link)


def run_expiry(shop, log, **bot):
    return asyncio.run(renewal_reminders.check_and_send_renewal_reminders(RecordingBot(log, **bot), shop.db))


def run_volume(shop, log, **bot):
    return asyncio.run(renewal_reminders.check_and_send_volume_reminders(RecordingBot(log, **bot), shop.db))


def run_connect(shop, log, **bot):
    return asyncio.run(connect_alerts.check_and_send_connect_alerts(RecordingBot(log, **bot), shop.db))


def test_expiry_reminder_uses_subscription_expiry_and_issues_code(shop, subs):
    pool_config(shop, POOL_1)
    e = expire_in(3 * DAY + 3600)
    subs.info[POOL_1] = usage(0, expire=e)
    before = now_naive()
    log = TelegramLog()
    assert run_expiry(shop, log) == 1
    after = now_naive()
    code_row = codes(shop, "renewal_reminder")[0]
    code = code_row["code"]
    assert RENEW_CODE.fullmatch(code)
    assert code_row["percent"] == 20
    assert code_row["max_uses"] == 1
    assert before + timedelta(hours=24) <= datetime.fromisoformat(code_row["expires_at"]) <= after + timedelta(hours=24)
    assert log.events == [TelegramEvent("send_message", BUYER, 1, EXPIRY_TEMPLATE.format(product="Stock 30d", days=3, date=jalali_of(e), percent=20, code=code, expiry_hours=24), "Markdown")]
    assert flag(shop, "configs", 1, "renewal_reminder_sent") == 1
    second = TelegramLog()
    assert run_expiry(shop, second) == 0
    assert second.events == []
    assert fetch_count(subs, POOL_1) == 1


def test_expiry_reminder_window_and_expired_stay_candidates(shop, subs):
    pool_config(shop, POOL_1)
    log = TelegramLog()
    subs.info[POOL_1] = usage(0, expire=expire_in(6 * DAY + 3600))
    assert run_expiry(shop, log) == 0
    assert flag(shop, "configs", 1, "renewal_reminder_sent") == 0
    assert codes(shop, "renewal_reminder") == []
    subs.info[POOL_1] = usage(0, expire=expire_in(-3600))
    assert run_expiry(shop, log) == 0
    assert flag(shop, "configs", 1, "renewal_reminder_sent") == 0
    subs.info[POOL_1] = usage(0, expire=expire_in(3 * DAY + 3600))
    assert run_expiry(shop, log) == 1
    assert flag(shop, "configs", 1, "renewal_reminder_sent") == 1
    assert fetch_count(subs, POOL_1) == 3


def test_expiry_reminder_settings_change_threshold_and_coupon(shop, subs):
    pool_config(shop, POOL_1)
    shop.db.set_setting("renewal_reminder_days_before", "10")
    shop.db.set_setting("renewal_discount_percent", "35")
    shop.db.set_setting("renewal_discount_expiry_hours", "48")
    e = expire_in(6 * DAY + 3600)
    subs.info[POOL_1] = usage(0, expire=e)
    log = TelegramLog()
    assert run_expiry(shop, log) == 1
    code = codes(shop, "renewal_reminder")[0]
    assert code["percent"] == 35
    assert log.events[0].text == EXPIRY_TEMPLATE.format(product="Stock 30d", days=6, date=jalali_of(e), percent=35, code=code["code"], expiry_hours=48)


def test_expiry_reminder_disabled_selects_nothing(shop, subs):
    shop.db.set_setting("renewal_reminder_enabled", "0")
    pool_config(shop, POOL_1)
    log = TelegramLog()
    assert run_expiry(shop, log) == 0
    assert subs.fetched == []
    assert codes(shop, "renewal_reminder") == []


def test_expiry_reminder_marked_even_when_blocked(shop, subs):
    pool_config(shop, POOL_1)
    subs.info[POOL_1] = usage(0, expire=expire_in(3 * DAY + 3600))
    log = TelegramLog()
    assert run_expiry(shop, log, blocked_chat_ids={BUYER}) == 1
    assert len(log.events) == 1
    assert log.events[0].delivered is False
    assert flag(shop, "configs", 1, "renewal_reminder_sent") == 1
    assert len(codes(shop, "renewal_reminder")) == 1


def test_expiry_reminder_unreadable_subscription_is_retried(shop, subs):
    pool_config(shop, POOL_1)
    log = TelegramLog()
    assert run_expiry(shop, log) == 0
    assert run_expiry(shop, log) == 0
    assert flag(shop, "configs", 1, "renewal_reminder_sent") == 0
    assert codes(shop, "renewal_reminder") == []
    assert fetch_count(subs, POOL_1) == 2


def test_expiry_reminder_custom_configs_skip_tests(shop, subs):
    t = shop.db.add_custom_config(BUYER, shop.server_id, "tst_1", 1, 1, TEST_1, expires_at=FAR, source="test")
    e = expire_in(3 * DAY + 3600)
    subs.info[CUST_1] = usage(0, expire=e)
    subs.info[TEST_1] = usage(0, expire=e)
    log = TelegramLog()
    assert run_expiry(shop, log) == 1
    code = codes(shop, "renewal_reminder")[0]["code"]
    assert log.events[0].text == EXPIRY_TEMPLATE.format(product="cust_1", days=3, date=jalali_of(e), percent=20, code=code, expiry_hours=24)
    assert flag(shop, "custom_configs", shop.cc, "renewal_reminder_sent") == 1
    assert flag(shop, "custom_configs", t, "renewal_reminder_sent") == 0
    assert fetch_count(subs, TEST_1) == 0


def test_volume_reminder_percent_threshold(shop, subs):
    pool_config(shop, POOL_1)
    log = TelegramLog()
    subs.info[POOL_1] = usage(int(7.9 * GIB))
    assert run_volume(shop, log) == 0
    assert flag(shop, "configs", 1, "volume_reminder_sent") == 0
    assert codes(shop, "volume_reminder") == []
    subs.info[POOL_1] = usage(8 * GIB)
    second = TelegramLog()
    assert run_volume(shop, second) == 1
    code_row = codes(shop, "volume_reminder")[0]
    code = code_row["code"]
    assert VOLUME_CODE.fullmatch(code)
    assert code_row["percent"] == 20
    assert code_row["max_uses"] == 1
    assert second.events[0] == TelegramEvent("send_message", BUYER, 1, VOLUME_TEMPLATE.format(product="Stock 30d", remaining="2.00", left=20, percent=20, code=code, expiry_hours=24), "Markdown")
    assert flag(shop, "configs", 1, "volume_reminder_sent") == 1


def test_volume_reminder_gb_mode(shop, subs):
    shop.db.set_setting("volume_reminder_mode", "gb")
    shop.db.set_setting("volume_reminder_gb_left", "2")
    pool_config(shop, POOL_1)
    subs.info[POOL_1] = usage(int(7.5 * GIB))
    assert run_volume(shop, TelegramLog()) == 0
    subs.info[POOL_1] = usage(8 * GIB)
    assert run_volume(shop, TelegramLog()) == 1
    assert flag(shop, "configs", 1, "volume_reminder_sent") == 1


def test_volume_reminder_skips_unlimited(shop, subs):
    pool_config(shop, POOL_1)
    subs.info[POOL_1] = usage(9 * GIB, total=0)
    log = TelegramLog()
    assert run_volume(shop, log) == 0
    assert flag(shop, "configs", 1, "volume_reminder_sent") == 0
    assert codes(shop, "volume_reminder") == []


def test_custom_volume_reminder_marks_the_stock_table(shop, subs):
    pool_config(shop, POOL_1)
    subs.info[POOL_1] = usage(1 * GIB)
    subs.info[CUST_1] = usage(9 * GIB)
    log = TelegramLog()
    assert run_volume(shop, log) == 1
    first_code = codes(shop, "volume_reminder")[0]["code"]
    assert log.events[0].text == VOLUME_TEMPLATE.format(product="cust_1", remaining="1.00", left=10, percent=20, code=first_code, expiry_hours=24)
    assert flag(shop, "custom_configs", shop.cc, "volume_reminder_sent") == 0
    assert flag(shop, "configs", 1, "volume_reminder_sent") == 1
    second = TelegramLog()
    assert run_volume(shop, second) == 1
    second_code = codes(shop, "volume_reminder")[1]["code"]
    assert second.events[0].text == VOLUME_TEMPLATE.format(product="cust_1", remaining="1.00", left=10, percent=20, code=second_code, expiry_hours=24)
    assert len(codes(shop, "volume_reminder")) == 2
    assert fetch_count(subs, POOL_1) == 1


def test_connect_alerts_disabled_by_default(shop, subs):
    pool_config(shop, POOL_1)
    subs.info[POOL_1] = usage(2 * MIB)
    log = TelegramLog()
    assert run_connect(shop, log) == (0, 0)
    assert subs.fetched == []
    assert log.events == []


def test_connect_alert_after_first_use(shop, subs):
    shop.db.set_setting("connect_alert_enabled", "1")
    pool_config(shop, POOL_1)
    subs.info[POOL_1] = usage(2 * MIB)
    log = TelegramLog()
    assert run_connect(shop, log) == (1, 0)
    assert log.events == [TelegramEvent("send_message", BUYER, 1, CONNECTED)]
    assert flag(shop, "configs", 1, "connect_alert_sent") == 1
    assert flag(shop, "configs", 1, "no_connect_alert_sent") == 0
    second = TelegramLog()
    assert run_connect(shop, second) == (0, 0)
    assert fetch_count(subs, POOL_1) == 1


def test_no_connect_alert_after_hours(shop, subs):
    shop.db.set_setting("no_connect_alert_enabled", "1")
    pool_config(shop, POOL_1, hours_ago=23)
    subs.info[POOL_1] = usage(0)
    log = TelegramLog()
    assert run_connect(shop, log) == (0, 0)
    assert flag(shop, "configs", 1, "no_connect_alert_sent") == 0
    sql(shop, "UPDATE configs SET assigned_at=? WHERE id=1", ((now_naive() - timedelta(hours=30)).isoformat(),))
    second = TelegramLog()
    assert run_connect(shop, second) == (0, 1)
    assert second.events == [TelegramEvent("send_message", BUYER, 1, NOT_CONNECTED)]
    assert flag(shop, "configs", 1, "no_connect_alert_sent") == 1


def test_no_connect_then_connect_both_sent(shop, subs):
    shop.db.set_setting("connect_alert_enabled", "1")
    shop.db.set_setting("no_connect_alert_enabled", "1")
    pool_config(shop, POOL_1, hours_ago=30)
    subs.info[POOL_1] = usage(0)
    assert run_connect(shop, TelegramLog()) == (0, 1)
    subs.info[POOL_1] = usage(2 * MIB)
    assert run_connect(shop, TelegramLog()) == (1, 0)
    assert flag(shop, "configs", 1, "connect_alert_sent") == 1
    assert flag(shop, "configs", 1, "no_connect_alert_sent") == 1
    assert fetch_count(subs, POOL_1) == 2


def test_custom_config_uses_created_at_and_skips_tests(shop, subs):
    shop.db.set_setting("no_connect_alert_enabled", "1")
    t = shop.db.add_custom_config(BUYER, shop.server_id, "tst_1", 1, 1, TEST_1, expires_at=FAR, source="test")
    created = (now_naive() - timedelta(hours=30)).strftime("%Y-%m-%d %H:%M:%S")
    sql(shop, "UPDATE custom_configs SET created_at=?", (created,))
    subs.info[CUST_1] = usage(0)
    subs.info[TEST_1] = usage(0)
    log = TelegramLog()
    assert run_connect(shop, log) == (0, 1)
    assert log.events == [TelegramEvent("send_message", BUYER, 1, NOT_CONNECTED)]
    assert flag(shop, "custom_configs", shop.cc, "no_connect_alert_sent") == 1
    assert fetch_count(subs, TEST_1) == 0


def test_alert_text_placeholders(shop, subs):
    shop.db.set_setting("connect_alert_enabled", "1")
    shop.db.set_setting("connect_alert_text", "used {used_gb} GB, threshold {threshold_gb} GB")
    pool_config(shop, POOL_1)
    subs.info[POOL_1] = usage(int(1.5 * GIB))
    log = TelegramLog()
    assert run_connect(shop, log) == (1, 0)
    assert log.events[0].text == "used 1.50 GB, threshold 0.001 GB"
    shop.db.set_setting("connect_alert_text", "bad {nope}")
    pool_config(shop, POOL_2)
    subs.info[POOL_2] = usage(2 * MIB)
    second = TelegramLog()
    assert run_connect(shop, second) == (1, 0)
    assert second.events[0].text == "bad {nope}"


def test_alert_marked_even_when_blocked(shop, subs):
    shop.db.set_setting("connect_alert_enabled", "1")
    pool_config(shop, POOL_1)
    subs.info[POOL_1] = usage(2 * MIB)
    log = TelegramLog()
    assert run_connect(shop, log, blocked_chat_ids={BUYER}) == (1, 0)
    assert len(log.events) == 1
    assert log.events[0].delivered is False
    assert flag(shop, "configs", 1, "connect_alert_sent") == 1


def test_unreadable_subscription_skips_alerts(shop, subs):
    shop.db.set_setting("connect_alert_enabled", "1")
    shop.db.set_setting("no_connect_alert_enabled", "1")
    pool_config(shop, POOL_1, hours_ago=30)
    log = TelegramLog()
    assert run_connect(shop, log) == (0, 0)
    assert flag(shop, "configs", 1, "connect_alert_sent") == 0
    assert flag(shop, "configs", 1, "no_connect_alert_sent") == 0
    assert log.events == []
