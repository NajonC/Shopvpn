"""Characterize the free-test flow in handlers_user.py (2187–2294),
test_config_provision.provision_test_plan, and the database.py test-slot helpers
at commit 6975a49. Reproduce with
`.venv/bin/python -m pytest tests/characterization/test_free_test_flow.py --network=deny`.
Telegram, the panel provider, individual-link fetching, and limited-reseller
provisioning are synthetic substitutes, not evidence.

The baseline pins unsafe behavior: plan picks reserve, provision, and record
against the bot id without checking or charging the buyer (7, 8); the counter
has no claimant, plan, or operation identity, so any release returns a slot,
including after delivery (23, 24); a failed local record is swallowed after
panel creation and the buyer still receives the link (14); a crash or
non-PanelError after reservation leaves the slot used without a record,
release, or message (15, 16); resetting usage reopens tests for past recipients
(25); and users without a users row are refused as already received (3).
"""

import asyncio
import re
import sqlite3
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

import config
import database
import handlers_user
import test_config_provision
from panel_providers.base import PanelError, PanelUserResult, PanelUsernameTakenError
from tests._harness.crash import CrashPlan, SimulatedCrash
from tests._harness.legacy_bot import (
    FakeCallbackQuery,
    FakeMessage,
    FakeUser,
    RecordingBot,
    TelegramEvent,
    TelegramLog,
    callback_rows,
    find_handler,
)


DISABLED = "در حال حاضر امکان دریافت کانفیگ تست غیرفعال است."
ALREADY = "شما قبلا\u064b کانفیگ تست خود را دریافت کرده\u200cاید. هر کاربر فقط یک بار مجاز به دریافت کانفیگ تست است."
PICK_PROMPT = "🧪 کدام مدل کانفیگ تست را می\u200cخواهید؟"
NO_PLANS = "در حال حاضر هیچ پلن کانفیگ تستی تعریف نشده است؛ با پشتیبانی تماس بگیرید."
BANK_EMPTY = "متاسفانه موجودی کانفیگ تست تمام شده است. لطفا\u064b بعدا\u064b مراجعه کنید."
PLAN_GONE = "این پلن دیگر در دسترس نیست."
BANK_LINK_1 = "🧪 کانفیگ تست شما:\n\n`vless://bank-1`"
PLAN_LINK_ONE_HOUR = "🧪 کانفیگ تست شما (One hour - 512 مگابایت / 1 ساعت):\n\n`https://sub.example.invalid/test-1`"
PLAN_LINK_TWO_DAYS = "🧪 کانفیگ تست شما (Two days - 2 گیگ / 2 روز):\n\n`https://sub.example.invalid/test-1`"
PLAN_LINK_RESELLER = "🧪 کانفیگ تست شما (One hour - 512 مگابایت / 1 ساعت):\n\n`https://sub.example.invalid/reseller-test-1`"
BUTTON_ONE_HOUR = "🧪 One hour (512 مگابایت / 1 ساعت)"
BUTTON_TWO_DAYS = "🧪 Two days (2 گیگ / 2 روز)"
INDIVIDUAL_1 = "📋 کانفیگ\u200cهای تکی این اشتراک (اگه لینک اشتراک رو نتونستی مستقیم اضافه کنی، هرکدوم از این\u200cها رو تکی وارد کن):\n\n`vless://individual-1`\n\n"
PANEL_DOWN = "⛔\ufe0f خطا در ساخت کانفیگ تست: panel down"
NAMES_TAKEN = "⛔\ufe0f ساخت نام کاربری یکتا روی پنل ناموفق بود؛ دوباره تلاش کنید."
SERVER_INACTIVE = "⛔\ufe0f پنل این پلن کانفیگ تست یافت نشد یا غیرفعال است؛ با پشتیبانی تماس بگیرید."
RESELLER_FAIL = "⛔\ufe0f reseller credit exhausted"
TEST_URL = "https://sub.example.invalid/test-1"
RESELLER_URL = "https://sub.example.invalid/reseller-test-1"
USERNAME = re.compile(r"tst[a-z0-9]{8}")
OWNER = 9001
BUYER = 1001
OTHER_USER = 1002
UNKNOWN = 4004
BOT_ID = 5005


@pytest.fixture
def shop(tmp_path):
    db = database.Database(str(tmp_path / "main.db"))
    db.init_db(OWNER)
    db.add_or_update_user(BUYER, "ali", "Ali")
    db.add_or_update_user(OTHER_USER, "sara", "Sara")
    server_id = db.add_panel_server(
        "Test panel", "pasarguard", "https://panel.example.invalid", "admin", "not-a-secret"
    )
    router = handlers_user.create_user_router(db, is_main_bot=True)
    return SimpleNamespace(db=db, db_path=str(tmp_path / "main.db"), router=router, server_id=server_id)


@pytest.fixture(autouse=True)
def panel(monkeypatch):
    panel = SimpleNamespace(calls=[], errors=[])

    class Provider:
        def __init__(self, server_id):
            self.server_id = server_id

        async def create_user(self, username, volume_gb, duration_days):
            panel.calls.append((self.server_id, username, volume_gb, duration_days))
            await asyncio.sleep(0)
            if panel.errors:
                raise panel.errors.pop(0)
            return PanelUserResult(username, TEST_URL)

    def get_provider(server):
        return Provider(server["id"])

    monkeypatch.setattr(test_config_provision, "get_provider", get_provider)
    return panel


@pytest.fixture(autouse=True)
def remote(monkeypatch):
    fetched = []

    async def fetch_individual_links(url):
        fetched.append(url)
        return ["vless://individual-1"]

    async def unexpected_reseller_provision(*args, **kwargs):
        pytest.fail("unexpected reseller provisioning")

    monkeypatch.setattr(handlers_user, "fetch_individual_links", fetch_individual_links)
    monkeypatch.setattr(handlers_user, "provision_test_config", unexpected_reseller_provision)
    return SimpleNamespace(fetched=fetched)


def one_hour(shop):
    return shop.db.create_test_config_plan("One hour", "tst", shop.server_id, 512, 1)


def two_days(shop):
    return shop.db.create_test_config_plan("Two days", "tst", shop.server_id, 2048, 48)


def user_message(log, user=FakeUser(BUYER, "ali", "Ali")):
    message = FakeMessage(log, user.id, from_user=user, text="🧪 تست")
    message.bot = RecordingBot(log)
    return message


def bot_message(log):
    message = FakeMessage(log, BUYER, from_user=FakeUser(BOT_ID, "shop_bot", "Shop", is_bot=True))
    message.bot = RecordingBot(log)
    return message


async def press_test(router, log, user=FakeUser(BUYER, "ali", "Ali")):
    return await find_handler(router, "message", "get_test_config")(user_message(log, user))


async def press_pick(router, log, plan_id):
    call = FakeCallbackQuery(
        log, FakeUser(BUYER, "ali", "Ali"), f"user_test_plan:{plan_id}", bot_message(log)
    )
    return await find_handler(router, "callback_query", "cb_user_test_plan_pick")(call)


def rows(shop, sql, params=()):
    conn = sqlite3.connect(shop.db_path)
    conn.row_factory = sqlite3.Row
    try:
        return [dict(row) for row in conn.execute(sql, params).fetchall()]
    finally:
        conn.close()


def test_used(shop, tg_id):
    found = rows(shop, "SELECT test_used FROM users WHERE telegram_id=?", (tg_id,))
    return found[0]["test_used"] if found else None


test_used.__test__ = False


def E(kind, chat, mid, text, parse_mode=None):
    return TelegramEvent(kind, chat, mid, text, parse_mode)


def no_changes(shop, panel):
    assert test_used(shop, BUYER) == 0
    assert panel.calls == []
    assert rows(shop, "SELECT * FROM custom_configs") == []


def test_disabled_refuses_message_and_pick(shop, panel):
    plan = one_hour(shop)
    shop.db.set_setting("test_enabled", "0")
    async def scenario():
        log = TelegramLog()
        await press_test(shop.router, log)
        assert log.events == [E("message_answer", BUYER, 2, DISABLED)]
        log = TelegramLog()
        await press_pick(shop.router, log, plan)
        assert log.events == [TelegramEvent("callback_answer", None, None, DISABLED, show_alert=True)]
    asyncio.run(scenario())
    no_changes(shop, panel)


def test_used_counter_refuses_before_plans(shop, panel):
    one_hour(shop)
    shop.db.mark_test_used(BUYER)
    async def scenario():
        log = TelegramLog()
        await press_test(shop.router, log)
        assert log.events == [E("message_answer", BUYER, 2, ALREADY)]
    asyncio.run(scenario())
    assert test_used(shop, BUYER) == 1 and panel.calls == []


def test_unknown_user_is_refused_as_already_used(shop, panel):
    one_hour(shop)
    async def scenario():
        log = TelegramLog()
        await press_test(shop.router, log, FakeUser(UNKNOWN, "ghost", "Ghost"))
        assert log.events == [E("message_answer", UNKNOWN, 2, ALREADY)]
    asyncio.run(scenario())
    assert test_used(shop, UNKNOWN) is None and panel.calls == []


def test_one_active_plan_is_delivered_directly(shop, panel, remote):
    p = one_hour(shop)
    before = datetime.now(timezone.utc).replace(tzinfo=None)
    async def scenario():
        log = TelegramLog()
        await press_test(shop.router, log)
        return log
    log = asyncio.run(scenario())
    after = datetime.now(timezone.utc).replace(tzinfo=None)
    assert log.events == [E("message_answer", BUYER, 2, PLAN_LINK_ONE_HOUR, "Markdown"), E("send_message", BUYER, 3, INDIVIDUAL_1, "Markdown")]
    assert remote.fetched == [TEST_URL]
    assert len(panel.calls) == 1
    server, name, volume, duration = panel.calls[0]
    assert (server, volume, duration) == (shop.server_id, 0.5, 1 / 24) and USERNAME.fullmatch(name)
    assert test_used(shop, BUYER) == 1
    configs = rows(shop, "SELECT * FROM custom_configs")
    assert len(configs) == 1
    row = configs[0]
    assert (row["user_id"], row["panel_server_id"], row["username"], row["volume_gb"], row["duration_days"], row["subscription_url"], row["source"], row["product_id"], row["order_id"], row["status"]) == (BUYER, shop.server_id, name, 0.5, 1 / 24, TEST_URL, "test", p, None, "active")
    expires = datetime.fromisoformat(row["expires_at"])
    assert before + timedelta(hours=1) <= expires <= after + timedelta(hours=1)
    history = rows(shop, "SELECT * FROM custom_config_history")
    assert len(history) == 1 and history[0]["event_type"] == "purchase"


def test_inactive_plans_are_ignored(shop, panel):
    p1, p2 = one_hour(shop), two_days(shop)
    shop.db.update_test_config_plan(p1, is_active=0)
    async def scenario():
        log = TelegramLog(); await press_test(shop.router, log); return log
    log = asyncio.run(scenario())
    assert log.events[0] == E("message_answer", BUYER, 2, PLAN_LINK_TWO_DAYS, "Markdown")
    assert panel.calls[0][2:] == (2.0, 2.0)
    assert rows(shop, "SELECT product_id FROM custom_configs")[0]["product_id"] == p2


def test_several_plans_offer_a_pick_without_reserving(shop, panel):
    p1, p2 = one_hour(shop), two_days(shop)
    shop.db.update_test_config_plan(p2, sort_order=-1)
    async def scenario():
        log = TelegramLog(); await press_test(shop.router, log); return log
    log = asyncio.run(scenario())
    assert len(log.events) == 1
    event = log.events[0]
    assert (event.kind, event.chat_id, event.message_id, event.text) == ("message_answer", BUYER, 2, PICK_PROMPT)
    assert callback_rows(event.reply_markup) == [[f"user_test_plan:{p2}"], [f"user_test_plan:{p1}"]]
    assert [[b.text for b in row] for row in event.reply_markup.inline_keyboard] == [[BUTTON_TWO_DAYS], [BUTTON_ONE_HOUR]]
    no_changes(shop, panel)


def test_pick_reserves_against_the_bot_and_refuses_buyer(shop, panel):
    p1, _ = one_hour(shop), two_days(shop)
    async def scenario():
        log = TelegramLog(); await press_pick(shop.router, log, p1); return log
    log = asyncio.run(scenario())
    assert log.events == [E("message_delete", BUYER, 1, None), E("message_answer", BUYER, 2, ALREADY), TelegramEvent("callback_answer", None, None, None)]
    no_changes(shop, panel)
    assert test_used(shop, BOT_ID) is None


def test_pick_with_bot_user_row_records_the_bot(shop, panel):
    p1, _ = one_hour(shop), two_days(shop)
    shop.db.add_or_update_user(BOT_ID, "shop_bot", "Shop")
    shop.db.mark_test_used(BUYER)
    async def scenario():
        log = TelegramLog(); await press_pick(shop.router, log, p1); return log
    log = asyncio.run(scenario())
    assert log.events == [E("message_delete", BUYER, 1, None), E("message_answer", BUYER, 2, PLAN_LINK_ONE_HOUR, "Markdown"), E("send_message", BOT_ID, 3, INDIVIDUAL_1, "Markdown"), TelegramEvent("callback_answer", None, None, None)]
    assert test_used(shop, BUYER) == 1 and test_used(shop, BOT_ID) == 1
    configs = rows(shop, "SELECT * FROM custom_configs")
    assert len(configs) == 1 and configs[0]["user_id"] == BOT_ID and configs[0]["product_id"] == p1
    assert len(panel.calls) == 1


def test_pick_of_inactive_or_missing_plan(shop, panel):
    p1, _ = one_hour(shop), two_days(shop)
    shop.db.update_test_config_plan(p1, is_active=0)
    async def scenario():
        log = TelegramLog(); await press_pick(shop.router, log, p1); await press_pick(shop.router, log, 999); return log
    log = asyncio.run(scenario())
    assert log.events == [TelegramEvent("callback_answer", None, None, PLAN_GONE, show_alert=True)] * 2
    no_changes(shop, panel)


def test_panel_error_releases_slot(shop, panel, remote):
    one_hour(shop); panel.errors = [PanelError("panel down")]
    async def scenario():
        log = TelegramLog(); await press_test(shop.router, log); return log
    log = asyncio.run(scenario())
    assert log.events == [E("message_answer", BUYER, 2, PANEL_DOWN)]
    assert test_used(shop, BUYER) == 0 and len(panel.calls) == 1
    assert rows(shop, "SELECT * FROM custom_configs") == [] and remote.fetched == []


def test_taken_usernames_retry_ten_times(shop, panel):
    one_hour(shop); panel.errors = [PanelUsernameTakenError("taken") for _ in range(10)]
    async def scenario():
        log = TelegramLog(); await press_test(shop.router, log); return log
    log = asyncio.run(scenario())
    assert log.events == [E("message_answer", BUYER, 2, NAMES_TAKEN)]
    assert len(panel.calls) == 10 and all(USERNAME.fullmatch(c[1]) for c in panel.calls)
    assert test_used(shop, BUYER) == 0 and rows(shop, "SELECT * FROM custom_configs") == []


def test_taken_username_retries_with_new_name(shop, panel):
    one_hour(shop); panel.errors = [PanelUsernameTakenError("taken")]
    async def scenario():
        log = TelegramLog(); await press_test(shop.router, log); return log
    log = asyncio.run(scenario())
    assert log.events[0] == E("message_answer", BUYER, 2, PLAN_LINK_ONE_HOUR, "Markdown")
    assert len(panel.calls) == 2
    assert rows(shop, "SELECT username FROM custom_configs")[0]["username"] == panel.calls[1][1]
    assert test_used(shop, BUYER) == 1


def test_inactive_server_releases_slot(shop, panel):
    one_hour(shop)
    conn = sqlite3.connect(shop.db_path)
    try:
        conn.execute("UPDATE panel_servers SET is_active=0"); conn.commit()
    finally:
        conn.close()
    async def scenario():
        log = TelegramLog(); await press_test(shop.router, log); return log
    log = asyncio.run(scenario())
    assert log.events == [E("message_answer", BUYER, 2, SERVER_INACTIVE)]
    no_changes(shop, panel)


def test_local_record_failure_is_swallowed(shop, panel, monkeypatch):
    one_hour(shop)
    def fail_record(*args, **kwargs):
        raise sqlite3.OperationalError("database is locked")
    monkeypatch.setattr(shop.db, "add_custom_config", fail_record)
    async def scenario():
        log = TelegramLog(); await press_test(shop.router, log); return log
    log = asyncio.run(scenario())
    assert log.events == [E("message_answer", BUYER, 2, PLAN_LINK_ONE_HOUR, "Markdown"), E("send_message", BUYER, 3, INDIVIDUAL_1, "Markdown")]
    assert len(panel.calls) == 1 and test_used(shop, BUYER) == 1
    assert rows(shop, "SELECT * FROM custom_configs") == []


def test_crash_after_panel_create_keeps_slot_without_record(shop, panel, monkeypatch):
    one_hour(shop); plan = CrashPlan().arm("after_panel_create")
    def crash_record(*args, **kwargs):
        plan("after_panel_create")
    monkeypatch.setattr(shop.db, "add_custom_config", crash_record)
    log = TelegramLog()
    with pytest.raises(SimulatedCrash):
        asyncio.run(press_test(shop.router, log))
    assert plan.crashed_at == "after_panel_create" and len(panel.calls) == 1
    assert test_used(shop, BUYER) == 1 and rows(shop, "SELECT * FROM custom_configs") == []
    assert log.events == []


def test_ambiguous_panel_error_keeps_slot_without_record(shop, panel):
    one_hour(shop); panel.errors = [TimeoutError("read timed out")]
    log = TelegramLog()
    with pytest.raises(TimeoutError):
        asyncio.run(press_test(shop.router, log))
    assert len(panel.calls) == 1 and test_used(shop, BUYER) == 1
    assert rows(shop, "SELECT * FROM custom_configs") == [] and log.events == []


def test_double_press_delivers_once(shop, panel):
    one_hour(shop)
    async def scenario():
        log = TelegramLog()
        await asyncio.gather(press_test(shop.router, log), press_test(shop.router, log))
        return log
    log = asyncio.run(scenario())
    assert len(panel.calls) == 1 and test_used(shop, BUYER) == 1
    assert len(rows(shop, "SELECT * FROM custom_configs")) == 1
    assert sorted(e.text for e in log.select("message_answer")) == sorted([PLAN_LINK_ONE_HOUR, ALREADY])
    assert [e.text for e in log.select("send_message")] == [INDIVIDUAL_1]


def test_legacy_link_bank_fallback(shop, panel, remote):
    shop.db.add_test_configs(["vless://bank-1", "vless://bank-2"])
    async def scenario():
        log = TelegramLog(); await press_test(shop.router, log); return log
    log = asyncio.run(scenario())
    assert log.events == [E("message_answer", BUYER, 2, BANK_LINK_1, "Markdown")]
    assert remote.fetched == [] and test_used(shop, BUYER) == 1
    bank = rows(shop, "SELECT * FROM test_configs ORDER BY id")
    assert bank[0]["is_used"] == 1 and bank[0]["assigned_user_id"] == BUYER and bank[0]["assigned_at"] is not None
    assert bank[1]["is_used"] == 0


def test_legacy_link_bank_empty_releases_slot(shop, panel):
    async def scenario():
        log = TelegramLog(); await press_test(shop.router, log); return log
    log = asyncio.run(scenario())
    assert log.events == [E("message_answer", BUYER, 2, BANK_EMPTY)]
    assert test_used(shop, BUYER) == 0


def test_limited_bot_without_plans_never_uses_bank(shop, panel):
    shop.db.add_test_configs(["vless://bank-1"])
    router = handlers_user.create_user_router(shop.db, is_main_bot=False)
    async def scenario():
        log = TelegramLog(); await press_test(router, log); return log
    log = asyncio.run(scenario())
    assert log.events == [E("message_answer", BUYER, 2, NO_PLANS)]
    assert test_used(shop, BUYER) == 0 and rows(shop, "SELECT is_used FROM test_configs")[0]["is_used"] == 0


def test_limited_bot_uses_reseller_provisioning(shop, panel, remote, monkeypatch):
    p1 = one_hour(shop); router = handlers_user.create_user_router(shop.db, is_main_bot=False); calls = []
    async def provide(db, plan, user_id):
        calls.append((db, plan["id"], user_id)); return {"subscription_url": RESELLER_URL}
    monkeypatch.setattr(handlers_user, "provision_test_config", provide)
    async def scenario():
        log = TelegramLog(); await press_test(router, log); return log
    log = asyncio.run(scenario())
    assert log.events == [E("message_answer", BUYER, 2, PLAN_LINK_RESELLER, "Markdown"), E("send_message", BUYER, 3, INDIVIDUAL_1, "Markdown")]
    assert len(calls) == 1 and calls[0][0] is shop.db and calls[0][1:] == (p1, BUYER)
    assert remote.fetched == [RESELLER_URL] and panel.calls == [] and test_used(shop, BUYER) == 1


def test_limited_bot_provision_error_releases_slot(shop, panel, monkeypatch):
    one_hour(shop); router = handlers_user.create_user_router(shop.db, is_main_bot=False)
    async def fail(*args, **kwargs):
        raise handlers_user.ProvisionError("reseller credit exhausted")
    monkeypatch.setattr(handlers_user, "provision_test_config", fail)
    async def scenario():
        log = TelegramLog(); await press_test(router, log); return log
    log = asyncio.run(scenario())
    assert log.events == [E("message_answer", BUYER, 2, RESELLER_FAIL)]
    assert test_used(shop, BUYER) == 0


def test_counter_helpers_are_identity_free(shop):
    assert shop.db.try_reserve_test_slot(BUYER, 1) is True and test_used(shop, BUYER) == 1
    assert shop.db.try_reserve_test_slot(BUYER, 1) is False and test_used(shop, BUYER) == 1
    shop.db.release_test_slot(BUYER); assert test_used(shop, BUYER) == 0
    shop.db.release_test_slot(BUYER); assert test_used(shop, BUYER) == 0
    assert [shop.db.try_reserve_test_slot(BUYER, 2) for _ in range(3)] == [True, True, False]
    assert test_used(shop, BUYER) == 2
    assert shop.db.try_reserve_test_slot(UNKNOWN, 1) is False
    shop.db.release_test_slot(UNKNOWN)
    assert test_used(shop, UNKNOWN) is None


def test_any_release_reopens_a_delivered_test(shop, panel):
    one_hour(shop)
    async def press(log): await press_test(shop.router, log)
    first = TelegramLog(); asyncio.run(press(first)); assert test_used(shop, BUYER) == 1
    shop.db.release_test_slot(BUYER); assert test_used(shop, BUYER) == 0
    second = TelegramLog(); asyncio.run(press(second))
    assert second.events[0] == E("message_answer", BUYER, 2, PLAN_LINK_ONE_HOUR, "Markdown")
    assert len(rows(shop, "SELECT * FROM custom_configs WHERE user_id=?", (BUYER,))) == 2
    assert len(panel.calls) == 2 and test_used(shop, BUYER) == 1


def test_reset_reopens_tests_for_past_recipients(shop, panel):
    one_hour(shop)
    first = TelegramLog(); asyncio.run(press_test(shop.router, first))
    assert shop.db.reset_all_test_usage() == [BUYER] and test_used(shop, BUYER) == 0
    assert len(rows(shop, "SELECT * FROM custom_configs")) == 1
    second = TelegramLog(); asyncio.run(press_test(shop.router, second))
    assert second.events[0] == E("message_answer", BUYER, 2, PLAN_LINK_ONE_HOUR, "Markdown")
    assert len(rows(shop, "SELECT * FROM custom_configs")) == 2 and test_used(shop, BUYER) == 1


def test_max_test_per_user_is_module_global(shop, panel, monkeypatch):
    one_hour(shop)
    assert config.MAX_TEST_PER_USER == 1 and handlers_user.MAX_TEST_PER_USER == 1
    monkeypatch.setattr(handlers_user, "MAX_TEST_PER_USER", 2)
    logs = []
    for _ in range(3):
        log = TelegramLog(); asyncio.run(press_test(shop.router, log)); logs.append(log)
    assert [log.events[0].text for log in logs] == [PLAN_LINK_ONE_HOUR, PLAN_LINK_ONE_HOUR, ALREADY]
    assert test_used(shop, BUYER) == 2 and len(rows(shop, "SELECT * FROM custom_configs")) == 2
    assert len(panel.calls) == 2
