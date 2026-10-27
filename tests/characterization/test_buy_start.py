"""Characterize the Telegram catalog purchase in handlers_user._buy_start
(lines 1038–1253) and its three entry handlers at commit 0713f65. Reproduce
with `.venv/bin/python -m pytest tests/characterization/test_buy_start.py
--network=deny`. Telegram, panel provisioning, and individual-link fetching are
synthetic substitutes; this is substitute, not evidence.

The baseline pins known unsafe behavior: the wallet debit, coupon increment,
and order insert are separate commits, so crashes can retain a debit or coupon
use without an order, or leave a pending order holding a debit (cases 9–12);
the FSM coupon is used without revalidation (case 6); rejection still sends
admins an automatically-approved notice (cases 16 and 21); delivery failure
after approval keeps the debit while the buyer is told it was returned
(case 17); and referral rewards use the base price before the coupon (cases 9
and 23).
"""

import asyncio
import logging
import sqlite3
from types import SimpleNamespace

import pytest

import config_delivery
import database
import handlers_user
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
    make_state,
)


NOT_AVAILABLE = "این محصول در حال حاضر موجود نیست."
SHORT_STOCK = "موجودی کافی نیست. فقط 2 عدد موجود است."
PAYMENT_PLAIN = "برای تکمیل خرید، مبلغ را به شماره کارت زیر واریز کرده و سپس عکس رسید را ارسال کنید:\n\n💰 مبلغ نهایی قابل پرداخت: 100,000 تومان\n\nلطفا\u064b روش پرداخت را انتخاب کنید:"
PAYMENT_QTY2_WALLET = "برای تکمیل خرید، مبلغ را به شماره کارت زیر واریز کرده و سپس عکس رسید را ارسال کنید:\n\n🔢 تعداد: 2 عدد\n👛 استفاده از کیف پول: 50,000 تومان\n💰 مبلغ نهایی قابل پرداخت: 150,000 تومان\n\nلطفا\u064b روش پرداخت را انتخاب کنید:"
PAYMENT_TIER = "برای تکمیل خرید، مبلغ را به شماره کارت زیر واریز کرده و سپس عکس رسید را ارسال کنید:\n\n🔢 تعداد: 2 عدد\n💰 مبلغ نهایی قابل پرداخت: 160,000 تومان\n\nلطفا\u064b روش پرداخت را انتخاب کنید:"
PAYMENT_COUPON = "برای تکمیل خرید، مبلغ را به شماره کارت زیر واریز کرده و سپس عکس رسید را ارسال کنید:\n\n🎟 تخفیف کد: 30,000 تومان\n👛 استفاده از کیف پول: 20,000 تومان\n💰 مبلغ نهایی قابل پرداخت: 50,000 تومان\n\nلطفا\u064b روش پرداخت را انتخاب کنید:"
WALLET_ONLY = "⛔\ufe0f این محصول فقط با کیف پول قابل خرید است و موجودی کیف پول شما کافی نیست.\nمبلغ کسرشده از کیف پول شما بازگردانده شد."
UNEXPECTED = "⛔\ufe0f خطای غیرمنتظره\u200cای در پردازش سفارش رخ داد.\nاگر مبلغی از کیف پول شما کسر شده بود، به\u200cطور کامل بازگردانده شد. لطفا\u064b دوباره تلاش کنید یا با پشتیبانی تماس بگیرید."
SOLD_OUT = "⛔\ufe0f موجودی این محصول در حال حاضر تمام شده است.\nمبلغ کسرشده از کیف پول شما به\u200cطور کامل بازگردانده شد. لطفا\u064b بعدا\u064b دوباره تلاش کنید یا با پشتیبانی در تماس باشید."
COVERED = "✅ مبلغ سفارش شما به\u200cطور کامل از کیف پول/تخفیف پوشش داده شد.\nکانفیگ شما در پیام بعدی ارسال می\u200cشود 👇"
ADMIN_STOCK_1 = "🧾 سفارش #1\n👤 کاربر: Ali (@ali)\n🆔 آیدی عددی: 1001\n📦 محصول: Stock 30d\n💰 قیمت پایه: 100,000 تومان\n👛 استفاده از کیف پول: 100,000 تومان\n💵 مبلغ قابل پرداخت: 0 تومان\n\n✅ این سفارش به\u200cطور خودکار تایید و کانفیگ برای کاربر ارسال شد (پرداخت کامل از کیف پول/کد تخفیف)."
ADMIN_QTY2_PART = "📦 محصول: Stock 30d × 2\n💰 قیمت پایه: 200,000 تومان\n"
ADMIN_DIRECT_1 = "🧾 سفارش #1\n👤 کاربر: Ali (@ali)\n🆔 آیدی عددی: 1001\n📦 محصول: Direct 50GB\n💰 قیمت پایه: 120,000 تومان\n👛 استفاده از کیف پول: 120,000 تومان\n💵 مبلغ قابل پرداخت: 0 تومان\n\n✅ این سفارش به\u200cطور خودکار تایید و کانفیگ برای کاربر ارسال شد (پرداخت کامل از کیف پول/کد تخفیف)."
LOW_STOCK = "⚠\ufe0f هشدار اتمام موجودی\n\n📦 محصول «Stock 30d» فقط 3 کانفیگ آزاد باقی مانده (آستانه\u200cی هشدار: 3).\nلطفا\u064b هرچه زودتر کانفیگ جدید به انبار اضافه کنید."
CAPTION_START = "🎉 با تشکر از خرید شما!"
CAPTION_ORDER_1 = "┣ 🆔 شماره سفارش: #1\n┣ 📦 محصول: Stock 30d\n"
CAPTION_1_OF_2 = "┣ 🔢 کانفیگ 1 از 2\n"
CAPTION_2_OF_2 = "┣ 🔢 کانفیگ 2 از 2\n"
LINK_STOCK_1 = "🔗 لینک اشتراک شما (برای کپی):\n`vless://stock-1`"
LINK_STOCK_2 = "🔗 لینک اشتراک شما (برای کپی):\n`vless://stock-2`"
LINK_DIRECT_1 = "🔗 لینک اشتراک شما (برای کپی):\n`https://sub.example.invalid/direct-1`"
LINK_RESELLER_1 = "🔗 لینک اشتراک شما (برای کپی):\n`https://sub.example.invalid/reseller-1`"
INDIVIDUAL_1 = "📋 کانفیگ\u200cهای تکی این اشتراک (اگه لینک اشتراک رو نتونستی مستقیم اضافه کنی، هرکدوم از این\u200cها رو تکی وارد کن):\n\n`vless://individual-1`\n\n"
SUMMARY_1 = "💰 مبلغ کل پرداخت\u200cشده: 0 تومان"
SUMMARY_2 = "💰 مبلغ کل پرداخت\u200cشده: 0 تومان (2 عدد کانفیگ)"
NAME_PROMPT = "🛠 نام کانفیگ\n\nیک نام دلخواه برای کانفیگ ارسال کنید، یا از دکمه\u200cی زیر نام خودکار بگیرید.\nفقط حروف انگلیسی، عدد و آندرلاین مجاز است (بین ۳ تا 20 کاراکتر)."
PROGRESS = "⏳ در حال ثبت سفارش..."
PROVISION_ERROR = "⛔\ufe0f panel unavailable\nمبلغ کسرشده از کیف پول شما به\u200cطور کامل بازگردانده شد."
REFERRER_10000 = "🤝 تبریک! یکی از زیرمجموعه\u200cهای شما اولین خرید خود را انجام داد.\n💰 10,000 تومان به کیف پول شما اضافه شد."

OWNER = 9001
BUYER = 1001
REFERRER = 1002
OTHER_BUYER = 2002
RESELLER = 3003
PENDING_DATA = {
    "order_id": 1,
    "discount_code_id": None,
    "discount_amount": 0,
    "discount_product_id": None,
    "pending_discount_code_id": None,
    "pending_discount_code_label": None,
}


@pytest.fixture
def shop(tmp_path):
    db_path = str(tmp_path / "main.db")
    db = database.Database(db_path)
    db.init_db(OWNER)
    db.add_or_update_user(BUYER, "ali", "Ali")
    db.add_or_update_user(REFERRER, "sara", "Sara")
    category_id = db.add_category("VPN")
    router = handlers_user.create_user_router(db, is_main_bot=True)
    return SimpleNamespace(db=db, db_path=db_path, router=router, category_id=category_id)


@pytest.fixture(autouse=True)
def remote(monkeypatch):
    async def unexpected_provision(*args, **kwargs):
        pytest.fail("unexpected panel provisioning")

    fetched = []

    async def fetch_individual_links(url):
        fetched.append(url)
        return ["vless://individual-1"]

    monkeypatch.setattr(handlers_user, "provision_direct", unexpected_provision)
    monkeypatch.setattr(handlers_user, "provision_auto_config", unexpected_provision)
    monkeypatch.setattr(config_delivery, "fetch_individual_links", fetch_individual_links)
    return SimpleNamespace(fetched=fetched)


def stock_product(shop, *, links=5, payment_methods=None):
    product_id = shop.db.add_product(
        shop.category_id, "Stock 30d", 100_000, payment_methods=payment_methods
    )
    shop.db.add_configs(product_id, [f"vless://stock-{i}" for i in range(1, links + 1)])
    return product_id


async def press_buy(shop, log, state, product_id, quantity, *, chat_id=BUYER, blocked=()):
    bot = RecordingBot(log, blocked_chat_ids=blocked)
    call = FakeCallbackQuery(
        log,
        FakeUser(BUYER, "ali", "Ali"),
        f"buy_start:{product_id}:{quantity}",
        FakeMessage(log, chat_id),
    )
    await find_handler(shop.router, "callback_query", "cb_buy_start")(call, state, bot)


def rows(shop, sql, params=()):
    conn = sqlite3.connect(shop.db_path)
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()


async def setup_coupon(shop, state):
    code = shop.db.create_discount_code("SAVE", fixed_amount=30_000)
    await state.update_data(discount_code_id=code, discount_amount=30_000)
    return code


def _event_texts(log):
    return [event.text for event in log.events]


def test_missing_or_empty_product_is_refused(shop):
    async def scenario():
        shop.db.add_wallet_credit(BUYER, 150_000)
        state = make_state(BUYER)
        log = TelegramLog()
        await press_buy(shop, log, state, 999, 1)
        empty = shop.db.add_product(shop.category_id, "Empty", 100_000)
        await press_buy(shop, log, state, empty, 1)

        assert log.events == [
            TelegramEvent("callback_answer", None, None, NOT_AVAILABLE, show_alert=True),
            TelegramEvent("callback_answer", None, None, NOT_AVAILABLE, show_alert=True),
        ]
        assert rows(shop, "SELECT COUNT(*) FROM orders")[0][0] == 0
        assert shop.db.get_wallet_credit(BUYER) == 150_000
        assert await state.get_state() is None

    asyncio.run(scenario())


def test_quantity_above_stock_is_refused(shop):
    async def scenario():
        product_id = stock_product(shop, links=2)
        shop.db.add_wallet_credit(BUYER, 150_000)
        state = make_state(BUYER)
        log = TelegramLog()
        await press_buy(shop, log, state, product_id, 3)

        assert log.events == [TelegramEvent("callback_answer", None, None, SHORT_STOCK, show_alert=True)]
        assert rows(shop, "SELECT COUNT(*) FROM orders")[0][0] == 0
        assert shop.db.get_wallet_credit(BUYER) == 150_000
        assert rows(shop, "SELECT COUNT(*) FROM configs WHERE is_used=1")[0][0] == 0

    asyncio.run(scenario())


def test_quantity_below_one_becomes_one(shop):
    async def scenario():
        product_id = stock_product(shop)
        state = make_state(BUYER)
        log = TelegramLog()
        await press_buy(shop, log, state, product_id, 0)

        order = shop.db.get_order(1)
        assert (order["quantity"], order["base_price"], order["final_price"], order["status"]) == (
            1, 100_000, 100_000, "pending"
        )
        assert log.select("edit_text")[0].text == PAYMENT_PLAIN

    asyncio.run(scenario())


def test_unpaid_remainder_shows_payment_choice(shop):
    async def scenario():
        product_id = stock_product(shop)
        shop.db.set_referred_by(BUYER, REFERRER)
        shop.db.add_wallet_credit(BUYER, 50_000)
        state = make_state(BUYER)
        log = TelegramLog()
        await press_buy(shop, log, state, product_id, 2)

        order = shop.db.get_order(1)
        assert (order["status"], order["quantity"], order["base_price"], order["tier_discount_amount"],
                order["wallet_used"], order["discount_amount"], order["final_price"], order["config_id"]) == (
            "pending", 2, 200_000, 0, 50_000, 0, 150_000, None
        )
        assert shop.db.get_wallet_credit(BUYER) == 0
        assert shop.db.get_wallet_credit(REFERRER) == 0
        assert shop.db.get_user(BUYER)["referral_first_purchase_rewarded"] == 0
        assert rows(shop, "SELECT COUNT(*) FROM configs WHERE is_used=1")[0][0] == 0
        assert await state.get_state() == "BuyFlow:waiting_receipt"
        assert await state.get_data() == PENDING_DATA
        assert log.trace() == [("edit_text", BUYER), ("callback_answer", None)]
        event = log.select("edit_text")[0]
        assert event.text == PAYMENT_QTY2_WALLET
        assert event.parse_mode == "Markdown"
        assert callback_rows(event.reply_markup) == [["pay_card2card"], ["cancel_flow"]]

    asyncio.run(scenario())


def test_tier_discount_sets_base_price(shop):
    async def scenario():
        product_id = stock_product(shop)
        shop.db.set_user_reseller_tier(BUYER, "silver", 20)
        state = make_state(BUYER)
        log = TelegramLog()
        await press_buy(shop, log, state, product_id, 2)

        order = shop.db.get_order(1)
        assert (order["base_price"], order["tier_discount_amount"], order["wallet_used"],
                order["final_price"], order["status"]) == (160_000, 40_000, 0, 160_000, "pending")
        assert log.select("edit_text")[0].text == PAYMENT_TIER

    asyncio.run(scenario())


def test_fsm_coupon_is_used_without_revalidation(shop):
    async def scenario():
        product_id = stock_product(shop)
        other = shop.db.add_product(shop.category_id, "Other", 50_000)
        code = shop.db.create_discount_code("OLD", fixed_amount=30_000, max_uses=1, product_id=other)
        conn = sqlite3.connect(shop.db_path)
        try:
            conn.execute("UPDATE discount_codes SET used_count=1, is_active=0 WHERE id=?", (code,))
            conn.commit()
        finally:
            conn.close()
        shop.db.add_wallet_credit(BUYER, 20_000)
        state = make_state(BUYER)
        await state.update_data(
            discount_code_id=code, discount_amount=30_000, discount_product_id=other
        )
        log = TelegramLog()
        await press_buy(shop, log, state, product_id, 1)

        order = shop.db.get_order(1)
        assert (order["discount_code_id"], order["discount_amount"], order["wallet_used"],
                order["base_price"], order["final_price"], order["status"]) == (
            code, 30_000, 20_000, 100_000, 50_000, "pending"
        )
        assert rows(shop, "SELECT used_count, is_active FROM discount_codes WHERE id=?", (code,)) == [(2, 0)]
        assert shop.db.get_wallet_credit(BUYER) == 0
        assert log.select("edit_text")[0].text == PAYMENT_COUPON
        assert await state.get_data() == PENDING_DATA

    asyncio.run(scenario())


def test_card_only_product_skips_wallet(shop):
    async def scenario():
        product_id = stock_product(shop, payment_methods=["card"])
        shop.db.add_wallet_credit(BUYER, 150_000)
        state = make_state(BUYER)
        log = TelegramLog()
        await press_buy(shop, log, state, product_id, 1)

        order = shop.db.get_order(1)
        assert (order["wallet_used"], order["final_price"], order["status"]) == (0, 100_000, "pending")
        assert shop.db.get_wallet_credit(BUYER) == 150_000
        event = log.select("edit_text")[0]
        assert event.text == PAYMENT_PLAIN
        assert callback_rows(event.reply_markup) == [["pay_card2card"], ["cancel_flow"]]

    asyncio.run(scenario())


def test_wallet_only_product_with_short_wallet_is_rejected(shop):
    async def scenario():
        product_id = stock_product(shop, payment_methods=["wallet"])
        shop.db.add_wallet_credit(BUYER, 30_000)
        state = make_state(BUYER)
        log = TelegramLog()
        await press_buy(shop, log, state, product_id, 1)

        order = shop.db.get_order(1)
        assert (order["status"], order["wallet_used"], order["final_price"]) == ("rejected", 30_000, 70_000)
        assert shop.db.get_wallet_credit(BUYER) == 30_000
        assert await state.get_state() is None
        assert await state.get_data() == {}
        assert len(log.events) == 2
        assert log.events[0] == TelegramEvent("edit_text", BUYER, 1, WALLET_ONLY)
        assert log.events[1] == TelegramEvent("callback_answer", None, None, None)

    asyncio.run(scenario())


def test_wallet_coupon_and_order_are_separate_commits(shop, monkeypatch):
    async def scenario():
        product_id = stock_product(shop)
        shop.db.add_wallet_credit(BUYER, 100_000)
        state = make_state(BUYER)
        await setup_coupon(shop, state)
        log = TelegramLog()
        calls = []
        reads = []
        for name in (
            "add_wallet_credit", "increment_discount_usage", "create_order",
            "take_unused_configs", "approve_order", "reward_referrer_if_first_purchase",
        ):
            real = getattr(shop.db, name)

            def wrapper(*args, _name=name, _real=real, **kwargs):
                result = _real(*args, **kwargs)
                calls.append((_name, args, kwargs))
                if _name in ("add_wallet_credit", "increment_discount_usage"):
                    reads.append((
                        rows(shop, "SELECT referral_credit FROM users WHERE telegram_id=?", (BUYER,))[0][0],
                        rows(shop, "SELECT used_count FROM discount_codes WHERE id=1")[0][0],
                        rows(shop, "SELECT COUNT(*) FROM orders")[0][0],
                    ))
                return result

            monkeypatch.setattr(shop.db, name, wrapper)

        await press_buy(shop, log, state, product_id, 1)

        assert calls == [
            ("add_wallet_credit", (1001, -70_000), {}),
            ("increment_discount_usage", (1,), {}),
            ("create_order", (1001, 1), {
                "base_price": 100_000, "wallet_used": 70_000, "discount_code_id": 1,
                "discount_amount": 30_000, "quantity": 1, "config_name": None,
                "tier_discount_amount": 0,
            }),
            ("take_unused_configs", (1, 1001, 1), {}),
            ("approve_order", (1, [1]), {}),
            ("reward_referrer_if_first_purchase", (1001, 100_000), {}),
        ]
        assert reads == [(30_000, 0, 0), (30_000, 1, 0)]

    asyncio.run(scenario())


def test_crash_before_coupon_increment_keeps_wallet_debit(shop, monkeypatch):
    async def scenario():
        product_id = stock_product(shop)
        shop.db.add_wallet_credit(BUYER, 50_000)
        state = make_state(BUYER)
        await setup_coupon(shop, state)
        log = TelegramLog()
        plan = CrashPlan().arm("before increment_discount_usage")
        real = shop.db.increment_discount_usage

        def wrapper(*args, **kwargs):
            plan("before increment_discount_usage")
            return real(*args, **kwargs)

        monkeypatch.setattr(shop.db, "increment_discount_usage", wrapper)
        with pytest.raises(SimulatedCrash):
            await press_buy(shop, log, state, product_id, 1)

        fresh = database.Database(shop.db_path)
        assert fresh.get_wallet_credit(BUYER) == 0
        assert rows(shop, "SELECT used_count FROM discount_codes WHERE code='SAVE'")[0][0] == 0
        assert rows(shop, "SELECT COUNT(*) FROM orders")[0][0] == 0
        assert rows(shop, "SELECT COUNT(*) FROM configs WHERE is_used=1")[0][0] == 0
        assert plan.crashed_at == "before increment_discount_usage"
        assert log.events == []

    asyncio.run(scenario())


def test_crash_before_order_insert_keeps_debit_and_coupon_use(shop, monkeypatch):
    async def scenario():
        product_id = stock_product(shop)
        shop.db.add_wallet_credit(BUYER, 50_000)
        state = make_state(BUYER)
        await setup_coupon(shop, state)
        log = TelegramLog()
        plan = CrashPlan().arm("before create_order")
        real = shop.db.create_order

        def wrapper(*args, **kwargs):
            plan("before create_order")
            return real(*args, **kwargs)

        monkeypatch.setattr(shop.db, "create_order", wrapper)
        with pytest.raises(SimulatedCrash):
            await press_buy(shop, log, state, product_id, 1)

        assert database.Database(shop.db_path).get_wallet_credit(BUYER) == 0
        assert rows(shop, "SELECT used_count FROM discount_codes WHERE code='SAVE'")[0][0] == 1
        assert rows(shop, "SELECT COUNT(*) FROM orders")[0][0] == 0
        assert log.events == []

    asyncio.run(scenario())


def test_crash_after_order_insert_leaves_pending_order(shop, monkeypatch):
    async def scenario():
        product_id = stock_product(shop)
        shop.db.add_wallet_credit(BUYER, 100_000)
        state = make_state(BUYER)
        await setup_coupon(shop, state)
        log = TelegramLog()
        plan = CrashPlan().arm("before take_unused_configs")
        real = shop.db.take_unused_configs

        def wrapper(*args, **kwargs):
            plan("before take_unused_configs")
            return real(*args, **kwargs)

        monkeypatch.setattr(shop.db, "take_unused_configs", wrapper)
        with pytest.raises(SimulatedCrash):
            await press_buy(shop, log, state, product_id, 1)

        order = database.Database(shop.db_path).get_order(1)
        assert (order["status"], order["wallet_used"], order["discount_amount"], order["final_price"]) == (
            "pending", 70_000, 30_000, 0
        )
        assert database.Database(shop.db_path).get_wallet_credit(BUYER) == 30_000
        assert rows(shop, "SELECT used_count FROM discount_codes WHERE code='SAVE'")[0][0] == 1
        assert rows(shop, "SELECT COUNT(*) FROM configs WHERE is_used=1")[0][0] == 0
        assert log.events == []
        assert await state.get_state() is None
        assert await state.get_data() == {}

    asyncio.run(scenario())


def test_unexpected_error_after_order_insert_rejects_and_refunds(shop, monkeypatch, caplog):
    async def scenario():
        product_id = stock_product(shop)
        shop.db.add_wallet_credit(BUYER, 100_000)
        state = make_state(BUYER)
        await setup_coupon(shop, state)
        log = TelegramLog()

        def fail(*args, **kwargs):
            raise RuntimeError("synthetic failure")

        monkeypatch.setattr(shop.db, "take_unused_configs", fail)
        with caplog.at_level(logging.ERROR, logger="handlers_user"):
            await press_buy(shop, log, state, product_id, 1)

        order = shop.db.get_order(1)
        assert (order["status"], order["wallet_used"]) == ("rejected", 70_000)
        assert shop.db.get_wallet_credit(BUYER) == 100_000
        assert rows(shop, "SELECT used_count FROM discount_codes WHERE code='SAVE'")[0][0] == 0
        assert await state.get_state() is None
        assert await state.get_data() == {}
        assert log.trace() == [("edit_text", BUYER), ("callback_answer", None)]
        assert log.select("edit_text")[0].text == UNEXPECTED
        records = [r for r in caplog.records if r.name == "handlers_user" and r.levelno == logging.ERROR]
        assert len(records) == 1
        assert records[0].args == (1, 1001)
        assert records[0].exc_info[0] is RuntimeError

    asyncio.run(scenario())


def test_stock_purchase_covered_by_wallet_acts_as_sender(shop, remote):
    async def scenario():
        product_id = stock_product(shop)
        shop.db.add_wallet_credit(BUYER, 150_000)
        state = make_state(BUYER)
        log = TelegramLog()
        await press_buy(shop, log, state, product_id, 1, chat_id=555)

        order = shop.db.get_order(1)
        assert (order["status"], order["user_id"], order["config_id"], order["quantity"],
                order["base_price"], order["wallet_used"], order["discount_amount"],
                order["final_price"], order["admin_chat_id"], order["admin_message_id"]) == (
            "approved", 1001, 1, 1, 100_000, 100_000, 0, 0, 9001, log.events[0].message_id
        )
        assert shop.db.get_wallet_credit(BUYER) == 50_000
        config = rows(shop, "SELECT is_used, assigned_user_id, order_id FROM configs WHERE id=1")[0]
        assert config == (1, 1001, 1)
        assert rows(shop, "SELECT is_used FROM configs WHERE id BETWEEN 2 AND 5") == [(0,)] * 4
        assert await state.get_state() is None
        assert await state.get_data() == {}
        assert log.trace() == [
            ("send_message", 9001), ("edit_text", 555), ("send_photo", 1001),
            ("send_message", 1001), ("send_message", 1001), ("callback_answer", None),
        ]
        assert log.events[0].text == ADMIN_STOCK_1
        assert log.events[0].reply_markup is None
        assert log.events[1].text == COVERED
        assert log.events[2].text.startswith(CAPTION_START)
        assert CAPTION_ORDER_1 in log.events[2].text
        assert log.events[3].text == LINK_STOCK_1
        assert log.events[3].parse_mode == "Markdown"
        assert log.events[4].text == SUMMARY_1
        assert remote.fetched == []

    asyncio.run(scenario())


def test_stock_purchase_of_two_sends_each_link_and_low_stock_alert(shop):
    async def scenario():
        product_id = stock_product(shop)
        shop.db.add_wallet_credit(BUYER, 250_000)
        state = make_state(BUYER)
        log = TelegramLog()
        await press_buy(shop, log, state, product_id, 2)

        assert log.trace() == [
            ("send_message", 9001), ("send_message", 9001), ("edit_text", 1001),
            ("send_photo", 1001), ("send_message", 1001), ("send_photo", 1001),
            ("send_message", 1001), ("send_message", 1001), ("callback_answer", None),
        ]
        texts = _event_texts(log)
        assert texts[0] == LOW_STOCK
        assert ADMIN_QTY2_PART in texts[1]
        assert texts[2] == COVERED
        assert CAPTION_1_OF_2 in texts[3]
        assert texts[4] == LINK_STOCK_1
        assert CAPTION_2_OF_2 in texts[5]
        assert texts[6] == LINK_STOCK_2
        assert texts[7] == SUMMARY_2
        order = shop.db.get_order(1)
        assert (order["quantity"], order["base_price"], order["wallet_used"], order["config_id"]) == (
            2, 200_000, 200_000, 1
        )
        configs = shop.db.get_order_configs(1)
        assert [config["id"] for config in configs] == [1, 2]
        assert [config["assigned_user_id"] for config in configs] == [1001, 1001]
        assert shop.db.get_wallet_credit(BUYER) == 50_000

    asyncio.run(scenario())


def test_stock_taken_by_another_buyer_rejects_and_refunds(shop, monkeypatch):
    async def scenario():
        product_id = stock_product(shop, links=1)
        shop.db.add_wallet_credit(BUYER, 100_000)
        state = make_state(BUYER)
        log = TelegramLog()
        real = shop.db.take_unused_configs

        def take_after_other(*args, **kwargs):
            real(1, OTHER_BUYER, 1)
            return real(*args, **kwargs)

        monkeypatch.setattr(shop.db, "take_unused_configs", take_after_other)
        await press_buy(shop, log, state, product_id, 1)

        order = shop.db.get_order(1)
        assert (order["status"], order["wallet_used"]) == ("rejected", 100_000)
        assert shop.db.get_wallet_credit(BUYER) == 100_000
        config = rows(shop, "SELECT assigned_user_id, order_id FROM configs WHERE id=1")[0]
        assert config == (2002, None)
        assert log.trace() == [("send_message", 9001), ("edit_text", 1001), ("callback_answer", None)]
        assert log.events[0].text == ADMIN_STOCK_1
        assert log.events[1].text == SOLD_OUT
        assert await state.get_state() is None

    asyncio.run(scenario())


def test_delivery_failure_after_approval_keeps_debit(shop, caplog):
    async def scenario():
        product_id = stock_product(shop)
        shop.db.add_wallet_credit(BUYER, 100_000)
        state = make_state(BUYER)
        log = TelegramLog()
        with caplog.at_level(logging.ERROR, logger="handlers_user"):
            await press_buy(shop, log, state, product_id, 1, chat_id=555, blocked={1001})

        order = shop.db.get_order(1)
        assert (order["status"], order["config_id"], order["wallet_used"]) == ("approved", 1, 100_000)
        assert shop.db.get_wallet_credit(BUYER) == 0
        config = rows(shop, "SELECT assigned_user_id, order_id FROM configs WHERE id=1")[0]
        assert config == (1001, 1)
        assert log.trace() == [
            ("send_message", 9001), ("edit_text", 555), ("send_photo", 1001),
            ("send_message", 1001), ("edit_text", 555), ("callback_answer", None),
        ]
        assert log.events[2].delivered is False
        assert log.events[3].delivered is False
        assert log.events[3].text.startswith(CAPTION_START)
        assert log.events[1].text == COVERED
        assert log.events[4].text == UNEXPECTED
        records = [r for r in caplog.records if r.name == "handlers_user" and r.levelno == logging.ERROR]
        assert len(records) == 1
        assert records[0].args == (1, 1001)
        assert await state.get_state() is None

    asyncio.run(scenario())


def _direct_product(shop):
    return shop.db.add_product(
        shop.category_id,
        "Direct 50GB",
        120_000,
        is_auto_provision=True,
        auto_provision_volume_gb=50,
        provision_server_id=7,
    )


def test_direct_product_asks_for_name_first(shop):
    async def scenario():
        product_id = _direct_product(shop)
        shop.db.add_wallet_credit(BUYER, 120_000)
        state = make_state(BUYER)
        log = TelegramLog()
        await press_buy(shop, log, state, product_id, 1)

        assert await state.get_state() == "BuyFlow:waiting_config_name"
        assert await state.get_data() == {"buy_name_product_id": product_id, "buy_name_quantity": 1}
        assert rows(shop, "SELECT COUNT(*) FROM orders")[0][0] == 0
        assert shop.db.get_wallet_credit(BUYER) == 120_000
        assert log.trace() == [("edit_text", 1001), ("callback_answer", None)]
        event = log.select("edit_text")[0]
        assert event.text == NAME_PROMPT
        assert callback_rows(event.reply_markup) == [["custom_config_random_username"], ["cancel_flow"]]

    asyncio.run(scenario())


def test_direct_product_with_automatic_name(shop, monkeypatch, remote):
    async def scenario():
        product_id = _direct_product(shop)
        shop.db.add_wallet_credit(BUYER, 120_000)
        state = make_state(BUYER)
        log = TelegramLog()
        await press_buy(shop, log, state, product_id, 1)
        log.events.clear()
        calls = []

        async def provision(db, product, quantity, user_id=None, order_id=None):
            calls.append((db is shop.db, product["id"], quantity, user_id, order_id))
            return [{
                "username": "direct_user_1", "subscription_url": "https://sub.example.invalid/direct-1",
                "volume_gb": 50, "duration_days": 30,
            }]

        monkeypatch.setattr(handlers_user, "provision_direct", provision)
        callback = FakeCallbackQuery(
            log, FakeUser(BUYER, "ali", "Ali"), "custom_config_random_username", FakeMessage(log, BUYER)
        )
        await find_handler(shop.router, "callback_query", "cb_buy_random_config_name")(
            callback, state, RecordingBot(log)
        )

        assert calls == [(True, product_id, 1, 1001, 1)]
        order = shop.db.get_order(1)
        assert (order["status"], order["config_id"], order["config_name"],
                order["wallet_used"], order["final_price"]) == ("approved", None, None, 120_000, 0)
        assert shop.db.get_wallet_credit(BUYER) == 0
        assert remote.fetched == ["https://sub.example.invalid/direct-1"]
        assert log.trace() == [
            ("send_message", 9001), ("edit_text", 1001), ("send_photo", 1001),
            ("send_message", 1001), ("send_message", 1001), ("send_message", 1001),
            ("callback_answer", None),
        ]
        assert _event_texts(log)[0] == ADMIN_DIRECT_1
        assert _event_texts(log)[1] == COVERED
        assert _event_texts(log)[2].startswith(CAPTION_START)
        assert _event_texts(log)[3] == LINK_DIRECT_1
        assert _event_texts(log)[4] == INDIVIDUAL_1
        assert log.events[4].parse_mode == "Markdown"
        assert _event_texts(log)[5] == SUMMARY_1
        assert await state.get_state() is None
        assert await state.get_data() == {}

    asyncio.run(scenario())


def test_direct_product_with_typed_name(shop, monkeypatch):
    async def scenario():
        product_id = _direct_product(shop)
        shop.db.add_wallet_credit(BUYER, 120_000)
        state = make_state(BUYER)
        log = TelegramLog()
        await press_buy(shop, log, state, product_id, 1)
        log.events.clear()
        calls = []

        async def provision(db, product, quantity, user_id=None, order_id=None):
            calls.append((db is shop.db, product["id"], quantity, user_id, order_id))
            return [{
                "username": "direct_user_1", "subscription_url": "https://sub.example.invalid/direct-1",
                "volume_gb": 50, "duration_days": 30,
            }]

        monkeypatch.setattr(handlers_user, "provision_direct", provision)
        bot = RecordingBot(log)
        message = FakeMessage(log, BUYER, from_user=FakeUser(BUYER, "ali", "Ali"), text="myname")
        await find_handler(shop.router, "message", "buy_receive_config_name")(message, state, bot)

        assert log.trace() == [
            ("message_answer", 1001), ("send_message", 9001), ("edit_text", 1001),
            ("send_photo", 1001), ("send_message", 1001), ("send_message", 1001),
            ("send_message", 1001),
        ]
        assert log.events[0].text == PROGRESS
        assert log.events[2].message_id == log.events[0].message_id
        order = shop.db.get_order(1)
        assert (order["config_name"], order["status"]) == ("myname", "approved")
        assert calls == [(True, product_id, 1, 1001, 1)]

    asyncio.run(scenario())


def test_direct_provision_error_rejects_and_refunds(shop, monkeypatch):
    async def scenario():
        product_id = _direct_product(shop)
        shop.db.add_wallet_credit(BUYER, 120_000)
        state = make_state(BUYER)
        log = TelegramLog()
        await press_buy(shop, log, state, product_id, 1)
        log.events.clear()

        async def provision(*args, **kwargs):
            raise handlers_user.DirectProvisionError("panel unavailable")

        monkeypatch.setattr(handlers_user, "provision_direct", provision)
        callback = FakeCallbackQuery(
            log, FakeUser(BUYER, "ali", "Ali"), "custom_config_random_username", FakeMessage(log, BUYER)
        )
        await find_handler(shop.router, "callback_query", "cb_buy_random_config_name")(
            callback, state, RecordingBot(log)
        )

        order = shop.db.get_order(1)
        assert (order["status"], order["wallet_used"]) == ("rejected", 120_000)
        assert shop.db.get_wallet_credit(BUYER) == 120_000
        assert log.trace() == [("send_message", 9001), ("edit_text", 1001), ("callback_answer", None)]
        assert _event_texts(log) == [ADMIN_DIRECT_1, PROVISION_ERROR, None]
        assert await state.get_state() is None
        assert await state.get_data() == {}

    asyncio.run(scenario())


def test_reseller_product_provisions_without_name(shop, monkeypatch, remote):
    async def scenario():
        product_id = shop.db.add_product(
            shop.category_id, "Reseller 50GB", 90_000,
            is_auto_provision=True, auto_provision_volume_gb=50,
        )
        shop.db.add_wallet_credit(BUYER, 90_000)
        state = make_state(BUYER)
        log = TelegramLog()
        calls = []

        async def provision(db, product, quantity, user_id=None, order_id=None):
            calls.append((db is shop.db, product["id"], quantity, user_id, order_id))
            return [{
                "username": "reseller_user_1", "subscription_url": "https://sub.example.invalid/reseller-1",
                "volume_gb": 50, "duration_days": 30,
            }]

        monkeypatch.setattr(handlers_user, "provision_auto_config", provision)
        await press_buy(shop, log, state, product_id, 1)

        assert calls == [(True, product_id, 1, 1001, 1)]
        order = shop.db.get_order(1)
        assert (order["status"], order["config_id"], order["config_name"], order["wallet_used"]) == (
            "approved", None, None, 90_000
        )
        assert shop.db.get_wallet_credit(BUYER) == 0
        assert remote.fetched == ["https://sub.example.invalid/reseller-1"]
        assert log.trace() == [
            ("send_message", 9001), ("edit_text", 1001), ("send_photo", 1001),
            ("send_message", 1001), ("send_message", 1001), ("send_message", 1001),
            ("callback_answer", None),
        ]
        assert "Reseller 50GB" in _event_texts(log)[0]
        assert "90,000 تومان" in _event_texts(log)[0]
        assert _event_texts(log)[1] == COVERED
        assert _event_texts(log)[2].startswith(CAPTION_START)
        assert _event_texts(log)[3] == LINK_RESELLER_1
        assert _event_texts(log)[4] == INDIVIDUAL_1
        assert _event_texts(log)[5] == SUMMARY_1

    asyncio.run(scenario())


def test_first_covered_purchase_rewards_referrer_on_base_price(shop):
    async def scenario():
        product_id = stock_product(shop)
        shop.db.set_referred_by(BUYER, REFERRER)
        shop.db.add_wallet_credit(BUYER, 200_000)
        state = make_state(BUYER)
        await setup_coupon(shop, state)
        log = TelegramLog()
        await press_buy(shop, log, state, product_id, 1)

        order = shop.db.get_order(1)
        assert (order["status"], order["base_price"], order["discount_amount"], order["wallet_used"]) == (
            "approved", 100_000, 30_000, 70_000
        )
        assert shop.db.get_wallet_credit(REFERRER) == 10_000
        assert shop.db.get_user(BUYER)["referral_first_purchase_rewarded"] == 1
        assert log.trace()[:2] == [("send_message", 1002), ("send_message", 9001)]
        assert log.events[0].text == REFERRER_10000

        log.events.clear()
        await press_buy(shop, log, make_state(BUYER), product_id, 1)
        second = shop.db.get_order(2)
        assert (second["status"], second["wallet_used"]) == ("approved", 100_000)
        assert shop.db.get_wallet_credit(REFERRER) == 10_000
        assert log.select(chat_id=REFERRER) == []
        assert shop.db.get_wallet_credit(BUYER) == 30_000

    asyncio.run(scenario())


def test_referrer_message_failure_is_ignored(shop):
    async def scenario():
        product_id = stock_product(shop)
        shop.db.set_referred_by(BUYER, REFERRER)
        shop.db.add_wallet_credit(BUYER, 100_000)
        state = make_state(BUYER)
        log = TelegramLog()
        await press_buy(shop, log, state, product_id, 1, blocked={REFERRER})

        assert shop.db.get_order(1)["status"] == "approved"
        assert shop.db.get_wallet_credit(REFERRER) == 10_000
        assert log.events[0].kind == "send_message"
        assert log.events[0].chat_id == REFERRER
        assert log.events[0].delivered is False
        assert log.events[0].text == REFERRER_10000
        assert log.trace()[1:] == [
            ("send_message", 9001), ("edit_text", 1001), ("send_photo", 1001),
            ("send_message", 1001), ("send_message", 1001), ("callback_answer", None),
        ]

    asyncio.run(scenario())


def test_inline_reseller_commission_on_every_covered_purchase(shop):
    async def scenario():
        product_id = stock_product(shop)
        shop.db.add_or_update_user(RESELLER, "res", "Res")
        shop.db.enable_inline_reseller(RESELLER, 5)
        shop.db.set_owner_reseller_id(BUYER, RESELLER)
        shop.db.add_wallet_credit(BUYER, 200_000)
        log = TelegramLog()
        await press_buy(shop, log, make_state(BUYER), product_id, 1)
        await press_buy(shop, log, make_state(BUYER), product_id, 1)

        assert shop.db.get_wallet_credit(RESELLER) == 10_000
        assert rows(
            shop,
            "SELECT owner_reseller_id, buyer_id, paid_amount, commission_amount "
            "FROM reseller_inline_commission_log ORDER BY id",
        ) == [(3003, 1001, 100_000, 5_000), (3003, 1001, 100_000, 5_000)]
        assert log.select(chat_id=RESELLER) == []

    asyncio.run(scenario())
