"""Characterize manual receipt linkage in ``handlers_user.receive_receipt``
(1559–1584), ``receipt_wrong_type``, the fallback in
``reseller_request_receipt_catch`` (5126–5262),
``database.get_latest_pending_order_awaiting_receipt`` (3515–3526), and
``_notify_admins_of_order`` at commit ``84b8489``. Reproduce the baseline with
`.venv/bin/python -m pytest tests/characterization/test_receipt_linkage.py
--network=deny`. Telegram and FSM storage use synthetic substitutes, not
evidence; the database, router, filters, handlers, and keyboards are real.
Only the user router is routed here; the main bot's other routers are out of
scope.

The baseline pins known unsafe behavior: both paths save the receipt before
notifying admins in separate steps, so a crash or error between them leaves a
saved receipt no admin has seen, and the fallback then refuses the buyer's
retry (cases 6 and 15); the FSM path accepts another buyer's order and does not
check for an earlier receipt (case 5); a duplicate upload after the FSM path
can attach to an older pending order of the same buyer (case 13); concurrent
duplicates both pass, overwrite the receipt, and each notify admins (cases 7
and 14); every admin role gets approve buttons and only the last admin's
message is recorded (case 16); and the fallback chooses the newest eligible
order of any kind, ignores card-to-card invoices, and excludes an order with a
crypto invoice of any status (cases 9 and 10).
"""

import asyncio
import logging
import sqlite3
import threading
from types import SimpleNamespace

import pytest

import database
import handlers_user
from tests._harness.crash import CrashPlan, SimulatedCrash
from tests._harness.legacy_bot import (
    FakeFile,
    FakeMessage,
    FakeUser,
    RecordingBot,
    callback_rows,
    find_handler,
    make_state,
    route_message,
    TelegramLog,
)


ADMIN_ORDER_1 = '🧾 سفارش #1\n👤 کاربر: Ali (@ali)\n🆔 آیدی عددی: 1001\n📦 محصول: Stock 30d\n💰 قیمت پایه: 100,000 تومان\n💵 مبلغ قابل پرداخت: 100,000 تومان'
CONFIRM = '✅ رسید شما برای بررسی ارسال شد. پس از تایید ادمین، کانفیگ برای شما ارسال خواهد شد.'
NOT_REGISTERED = '❌ رسید شما ثبت نشد.\nدلیل: هیچ سفارش یا درخواست شارژ در انتظار رسیدی برای شما پیدا نشد (احتمالاً ارتباط قطع شده بود یا قبلاً بررسی شده است).\n\nلطفاً دوباره از منوی اصلی همان مسیر خرید یا شارژ کیف پول را طی کنید و رسید را مجدداً ارسال کنید.'
WRONG_TYPE = 'لطفاً عکس یا فایل رسید پرداخت را ارسال کنید.'
NOT_VALID = 'سفارش معتبر یافت نشد. لطفاً دوباره از منو شروع کنید.'
ADMIN_ORDER_1_BOB = '🧾 سفارش #1\n👤 کاربر: Bob (@bob)\n🆔 آیدی عددی: 2002\n📦 محصول: Stock 30d\n💰 قیمت پایه: 100,000 تومان\n💵 مبلغ قابل پرداخت: 100,000 تومان'
ADMIN_ORDER_1_WALLET = '🧾 سفارش #1\n👤 کاربر: Ali (@ali)\n🆔 آیدی عددی: 1001\n📦 محصول: Stock 30d\n💰 قیمت پایه: 100,000 تومان\n👛 استفاده از کیف پول: 20,000 تومان\n💵 مبلغ قابل پرداخت: 80,000 تومان'
ADMIN_RENEWAL_2 = '🧾 سفارش تمدید سرویس #2\n👤 کاربر: Ali (@ali)\n🆔 آیدی عددی: 1001\n🔄 نوع: تمدید حجم سرویس\n🎯 هدف: کانفیگ شخصی #7\n🔋 افزایش حجم: 10 گیگابایت\n💰 قیمت پایه: 50,000 تومان\n💵 مبلغ قابل پرداخت: 50,000 تومان'
FALLBACK_ERROR = '⚠️ در ثبت رسید شما خطایی رخ داد. لطفاً دوباره تلاش کنید یا با پشتیبانی تماس بگیرید.'

OWNER = 9001
BUYER = 1001
OTHER_BUYER = 2002
ORDER_BUTTONS_1 = [["order_approve:1", "order_reject:1"]]


@pytest.fixture
def shop(tmp_path):
    db_path = str(tmp_path / "main.db")
    db = database.Database(db_path)
    db.init_db(OWNER)
    db.add_or_update_user(BUYER, "ali", "Ali")
    db.add_or_update_user(OTHER_BUYER, "bob", "Bob")
    product_id = db.add_product(db.add_category("VPN"), "Stock 30d", 100_000)
    router = handlers_user.create_user_router(db, is_main_bot=True)
    return SimpleNamespace(db=db, db_path=db_path, router=router, product_id=product_id)


def order(shop, user=BUYER, **kwargs) -> int:
    return shop.db.create_order(user, shop.product_id, 100_000, **kwargs)


def photo(log, file_id, user=BUYER):
    from_user = FakeUser(BUYER, "ali", "Ali") if user == BUYER else FakeUser(OTHER_BUYER, "bob", "Bob")
    return FakeMessage(
        log,
        user,
        from_user=from_user,
        photo=[FakeFile(f"{file_id}-small"), FakeFile(file_id)],
    )


async def waiting_state(order_id):
    state = make_state(BUYER)
    await state.set_state("BuyFlow:waiting_receipt")
    await state.update_data(order_id=order_id)
    return state


async def send(shop, log, message, state, bot):
    result = await route_message(shop.router, message, state, bot)
    assert result is None  # a handler took the message (UNHANDLED otherwise)
    return result


def order_row(shop, order_id):
    conn = sqlite3.connect(shop.db_path)
    conn.row_factory = sqlite3.Row
    try:
        return dict(conn.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone())
    finally:
        conn.close()


def admin_events(log):
    return [event for event in log.events if event.kind in ("send_photo", "send_document")]


def hold_first_two(monkeypatch, db, name):
    real = getattr(db, name)
    lock = threading.Lock()
    count = 0
    barrier = threading.Barrier(2, timeout=5)

    def held(*args, **kwargs):
        nonlocal count
        with lock:
            count += 1
            call_number = count
        if call_number <= 2:
            barrier.wait()
        return real(*args, **kwargs)

    monkeypatch.setattr(db, name, held)


def handlers_records(caplog, level):
    return [record for record in caplog.records if record.name == "handlers_user" and record.levelno == level]


def test_fsm_receipt_is_saved_before_admins_are_notified(shop, monkeypatch):
    async def scenario():
        order(shop)
        log = TelegramLog()
        bot = RecordingBot(log)
        state = await waiting_state(1)
        seen = []
        real_set = shop.db.set_order_receipt

        def record_set(order_id, file_id, receipt_type="photo"):
            seen.append(len(log.events))
            return real_set(order_id, file_id, receipt_type)

        monkeypatch.setattr(shop.db, "set_order_receipt", record_set)
        await send(shop, log, photo(log, "r1"), state, bot)

        row = order_row(shop, 1)
        assert seen == [0]
        assert (row["receipt_file_id"], row["receipt_type"], row["status"]) == ("r1", "photo", "pending")
        assert row["admin_chat_id"] == OWNER
        assert row["admin_message_id"] == log.events[0].message_id
        assert log.trace() == [("send_photo", OWNER), ("message_answer", BUYER)]
        assert [event.text for event in log.events] == [ADMIN_ORDER_1, CONFIRM]
        assert callback_rows(log.events[0].reply_markup) == ORDER_BUTTONS_1
        assert log.events[1].reply_markup is not None
        assert await state.get_state() is None
        assert await state.get_data() == {}

    asyncio.run(scenario())


def test_fsm_document_receipt(shop):
    async def scenario():
        order(shop)
        log = TelegramLog()
        state = await waiting_state(1)
        message = FakeMessage(log, BUYER, from_user=FakeUser(BUYER, "ali", "Ali"), document=FakeFile("doc1"))

        await send(shop, log, message, state, RecordingBot(log))

        row = order_row(shop, 1)
        assert (row["receipt_file_id"], row["receipt_type"]) == ("doc1", "document")
        assert log.trace() == [("send_document", OWNER), ("message_answer", BUYER)]
        assert log.events[0].text == ADMIN_ORDER_1

    asyncio.run(scenario())


def test_fsm_text_message_is_refused(shop):
    async def scenario():
        order(shop)
        log = TelegramLog()
        state = await waiting_state(1)

        await send(
            shop,
            log,
            FakeMessage(log, BUYER, from_user=FakeUser(BUYER, "ali", "Ali"), text="hi"),
            state,
            RecordingBot(log),
        )

        assert log.trace() == [("message_answer", BUYER)]
        assert log.events[0].text == WRONG_TYPE
        assert order_row(shop, 1)["receipt_file_id"] is None
        assert await state.get_state() == "BuyFlow:waiting_receipt"
        assert await state.get_data() == {"order_id": 1}

    asyncio.run(scenario())


def test_stale_fsm_is_refused_and_cleared(shop):
    async def scenario():
        order(shop)
        shop.db.reject_order(1)
        log = TelegramLog()
        bot = RecordingBot(log)
        state = await waiting_state(1)

        await send(shop, log, photo(log, "r1"), state, bot)

        assert log.trace() == [("message_answer", BUYER)]
        assert log.events[0].text == NOT_VALID
        assert log.events[0].reply_markup is None
        assert order_row(shop, 1)["receipt_file_id"] is None
        assert await state.get_state() is None
        assert await state.get_data() == {}

        second_state = make_state(BUYER)
        await second_state.set_state("BuyFlow:waiting_receipt")
        order(shop)
        log.events.clear()
        await send(shop, log, photo(log, "r2"), second_state, bot)

        assert log.trace() == [("message_answer", BUYER)]
        assert log.events[0].text == NOT_VALID
        assert order_row(shop, 2)["receipt_file_id"] is None
        assert await second_state.get_state() is None

    asyncio.run(scenario())


def test_fsm_accepts_an_order_of_another_buyer(shop):
    async def scenario():
        order(shop, user=OTHER_BUYER)
        log = TelegramLog()
        state = await waiting_state(1)

        await send(shop, log, photo(log, "r1"), state, RecordingBot(log))

        row = order_row(shop, 1)
        assert row["user_id"] == OTHER_BUYER
        assert row["receipt_file_id"] == "r1"
        assert log.trace() == [("send_photo", OWNER), ("message_answer", BUYER)]
        assert [event.text for event in log.events] == [ADMIN_ORDER_1_BOB, CONFIRM]

    asyncio.run(scenario())


def test_crash_between_fsm_receipt_and_admin_notice(shop):
    async def scenario():
        order(shop)
        log = TelegramLog()
        bot = RecordingBot(log)
        state = await waiting_state(1)
        plan = CrashPlan().arm("admin send_photo")

        async def crash_send_photo(*args, **kwargs):
            plan("admin send_photo")

        bot.send_photo = crash_send_photo
        with pytest.raises(SimulatedCrash):
            await send(shop, log, photo(log, "r1"), state, bot)

        row = order_row(shop, 1)
        assert row["receipt_file_id"] == "r1"
        assert row["admin_chat_id"] is None
        assert row["admin_message_id"] is None
        assert log.events == []
        assert await state.get_state() == "BuyFlow:waiting_receipt"
        assert await state.get_data() == {"order_id": 1}

        await send(shop, log, photo(log, "r2"), state, RecordingBot(log))

        row = order_row(shop, 1)
        assert row["receipt_file_id"] == "r2"
        assert row["admin_chat_id"] == OWNER
        assert log.trace() == [("send_photo", OWNER), ("message_answer", BUYER)]
        assert await state.get_state() is None

    asyncio.run(scenario())


def test_concurrent_fsm_duplicates_both_pass(shop, monkeypatch):
    async def scenario():
        order(shop)
        hold_first_two(monkeypatch, shop.db, "get_order")
        log = TelegramLog()
        bot = RecordingBot(log)
        state = await waiting_state(1)

        await asyncio.gather(
            send(shop, log, photo(log, "r1"), state, bot),
            send(shop, log, photo(log, "r2"), state, bot),
        )

        row = order_row(shop, 1)
        sent = admin_events(log)
        assert row["status"] == "pending"
        assert row["receipt_file_id"] in {"r1", "r2"}
        assert len(sent) == 2
        assert all(event.kind == "send_photo" and event.chat_id == OWNER for event in sent)
        assert all(event.text == ADMIN_ORDER_1 for event in sent)
        assert all(callback_rows(event.reply_markup) == ORDER_BUTTONS_1 for event in sent)
        assert row["admin_message_id"] in {event.message_id for event in sent}
        answers = log.select(kind="message_answer")
        assert len(answers) == 2
        assert all(event.text == CONFIRM for event in answers)
        assert await state.get_state() is None

    asyncio.run(scenario())


def test_lost_fsm_falls_back_and_saves_before_notifying(shop, monkeypatch, caplog):
    async def scenario():
        order(shop, wallet_used=20_000)
        log = TelegramLog()
        state = make_state(BUYER)
        seen = []
        real_set = shop.db.set_order_receipt

        def record_set(order_id, file_id, receipt_type="photo"):
            seen.append(len(log.events))
            return real_set(order_id, file_id, receipt_type)

        monkeypatch.setattr(shop.db, "set_order_receipt", record_set)
        await send(shop, log, photo(log, "r1"), state, RecordingBot(log))

        row = order_row(shop, 1)
        assert seen == [0]
        assert row["receipt_file_id"] == "r1"
        assert row["receipt_type"] == "photo"
        assert row["admin_message_id"] == log.events[0].message_id
        assert log.trace() == [("send_photo", OWNER), ("message_answer", BUYER)]
        assert [event.text for event in log.events] == [ADMIN_ORDER_1_WALLET, CONFIRM]
        records = handlers_records(caplog, logging.WARNING)
        assert len(records) == 1
        assert records[0].args == (1, BUYER)
        assert await state.get_state() is None

    asyncio.run(scenario())


def test_fallback_picks_newest_eligible_order_of_the_sender(shop):
    async def scenario():
        for _ in range(4):
            order(shop)
        order(shop, user=OTHER_BUYER)
        shop.db.create_crypto_invoice("txn-2", "order", 2, BUYER, 100_000, 1.0)
        conn = sqlite3.connect(shop.db_path)
        try:
            conn.execute("UPDATE crypto_invoices SET status='expired'")
            conn.commit()
        finally:
            conn.close()
        shop.db.set_order_receipt(3, "old", "photo")
        shop.db.reject_order(4)
        log = TelegramLog()

        await send(shop, log, photo(log, "r1"), make_state(BUYER), RecordingBot(log))

        assert [order_row(shop, index)["receipt_file_id"] for index in range(1, 6)] == [
            "r1", None, "old", None, None
        ]
        assert log.events[0].text == ADMIN_ORDER_1
        assert log.trace() == [("send_photo", OWNER), ("message_answer", BUYER)]

    asyncio.run(scenario())


def test_fallback_ignores_order_kind_and_card_invoice(shop):
    async def scenario():
        order(shop)
        renewal_id = shop.db.create_renewal_order(BUYER, "custom", 7, "volume", 10, 0, 50_000)
        assert renewal_id == 2
        shop.db.create_card_to_card_invoice(1, "order", 2, BUYER, 50_000, 50_123, "2099-01-01T00:00:00")
        log = TelegramLog()

        await send(shop, log, photo(log, "r1"), make_state(BUYER), RecordingBot(log))

        assert order_row(shop, 2)["receipt_file_id"] == "r1"
        assert order_row(shop, 1)["receipt_file_id"] is None
        assert [event.text for event in log.events] == [ADMIN_RENEWAL_2, CONFIRM]
        assert callback_rows(log.events[0].reply_markup) == [["order_approve:2", "order_reject:2"]]

    asyncio.run(scenario())


def test_fallback_never_takes_another_buyers_order(shop, caplog):
    async def scenario():
        order(shop, user=OTHER_BUYER)
        log = TelegramLog()

        await send(shop, log, photo(log, "r1"), make_state(BUYER), RecordingBot(log))

        assert order_row(shop, 1)["receipt_file_id"] is None
        assert log.trace() == [("message_answer", BUYER)]
        assert log.events[0].text == NOT_REGISTERED
        assert log.events[0].reply_markup is not None
        records = handlers_records(caplog, logging.WARNING)
        assert len(records) == 1
        assert records[0].args == (BUYER,)

    asyncio.run(scenario())


def test_duplicate_after_fsm_upload_is_refused(shop):
    async def scenario():
        order(shop)
        log = TelegramLog()
        state = await waiting_state(1)
        bot = RecordingBot(log)

        await send(shop, log, photo(log, "r1"), state, bot)
        assert log.events[-1].text == CONFIRM
        log.events.clear()
        await send(shop, log, photo(log, "r2"), state, bot)

        assert order_row(shop, 1)["receipt_file_id"] == "r1"
        assert log.trace() == [("message_answer", BUYER)]
        assert log.events[0].text == NOT_REGISTERED

    asyncio.run(scenario())


def test_duplicate_after_fsm_upload_lands_on_an_older_order(shop):
    async def scenario():
        order(shop)
        order(shop)
        log = TelegramLog()
        state = await waiting_state(2)
        bot = RecordingBot(log)

        await send(shop, log, photo(log, "r1"), state, bot)
        assert order_row(shop, 2)["receipt_file_id"] == "r1"
        log.events.clear()
        await send(shop, log, photo(log, "r2"), state, bot)

        assert order_row(shop, 1)["receipt_file_id"] == "r2"
        assert order_row(shop, 2)["receipt_file_id"] == "r1"
        assert [event.text for event in log.events] == [ADMIN_ORDER_1, CONFIRM]

    asyncio.run(scenario())


def test_concurrent_fallback_duplicates_both_pass(shop, monkeypatch, caplog):
    async def scenario():
        order(shop)
        hold_first_two(monkeypatch, shop.db, "get_latest_pending_order_awaiting_receipt")
        log = TelegramLog()
        bot = RecordingBot(log)

        await asyncio.gather(
            send(shop, log, photo(log, "r1"), make_state(BUYER), bot),
            send(shop, log, photo(log, "r2"), make_state(BUYER), bot),
        )

        row = order_row(shop, 1)
        assert row["receipt_file_id"] in {"r1", "r2"}
        assert len(admin_events(log)) == 2
        assert all(event.text == ADMIN_ORDER_1 for event in admin_events(log))
        answers = log.select(kind="message_answer")
        assert len(answers) == 2
        assert all(event.text == CONFIRM for event in answers)
        records = handlers_records(caplog, logging.WARNING)
        assert len(records) == 2
        assert all(record.args == (1, BUYER) for record in records)

    asyncio.run(scenario())


def test_fallback_error_after_saving_receipt_blocks_retry(shop, monkeypatch, caplog):
    async def scenario():
        order(shop)
        real = shop.db.list_admins

        def fail_list_admins():
            raise RuntimeError("synthetic failure")

        monkeypatch.setattr(shop.db, "list_admins", fail_list_admins)
        log = TelegramLog()
        bot = RecordingBot(log)
        state = make_state(BUYER)

        await send(shop, log, photo(log, "r1"), state, bot)

        row = order_row(shop, 1)
        assert row["receipt_file_id"] == "r1"
        assert row["admin_chat_id"] is None
        assert log.trace() == [("message_answer", BUYER)]
        assert log.events[0].text == FALLBACK_ERROR
        assert log.events[0].reply_markup is None
        records = handlers_records(caplog, logging.ERROR)
        assert len(records) == 1
        assert records[0].args == (1, BUYER)
        assert records[0].exc_info[0] is RuntimeError

        monkeypatch.setattr(shop.db, "list_admins", real)
        log.events.clear()
        await send(shop, log, photo(log, "r2"), state, bot)

        row = order_row(shop, 1)
        assert row["receipt_file_id"] == "r1"
        assert row["admin_chat_id"] is None
        assert log.trace() == [("message_answer", BUYER)]
        assert log.events[0].text == NOT_REGISTERED

    asyncio.run(scenario())


def test_every_admin_role_gets_review_buttons(shop):
    async def scenario():
        shop.db.add_admin(4004, "support")
        shop.db.add_admin(5005, "mid")
        order(shop)
        log = TelegramLog()
        state = await waiting_state(1)

        await send(shop, log, photo(log, "r1"), state, RecordingBot(log, blocked_chat_ids={5005}))

        assert log.trace() == [
            ("send_photo", 4004),
            ("send_photo", 5005),
            ("send_photo", OWNER),
            ("message_answer", BUYER),
        ]
        assert log.events[1].delivered is False
        sent = admin_events(log)
        assert len(sent) == 3
        assert all(event.text == ADMIN_ORDER_1 for event in sent)
        assert all(callback_rows(event.reply_markup) == ORDER_BUTTONS_1 for event in sent)
        row = order_row(shop, 1)
        assert row["admin_chat_id"] == OWNER
        assert row["admin_message_id"] == log.events[2].message_id
        assert log.events[-1].text == CONFIRM

    asyncio.run(scenario())


def test_fallback_steps_aside_while_a_state_is_set(shop):
    async def scenario():
        order(shop)
        log = TelegramLog()
        state = make_state(BUYER)
        await state.set_state("BuyFlow:waiting_config_name")
        bot = RecordingBot(log)
        handler = find_handler(shop.router, "message", "reseller_request_receipt_catch")

        result = await handler(photo(log, "r1"), state, bot)

        assert result is None
        assert log.events == []
        assert order_row(shop, 1)["receipt_file_id"] is None

    asyncio.run(scenario())
