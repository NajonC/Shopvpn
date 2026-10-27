"""Unit tests for the offline Telegram doubles used by legacy handlers."""

import asyncio
import os
import sys
import types

from aiogram import F, Router
from aiogram.dispatcher.event.bases import UNHANDLED
from aiogram.exceptions import TelegramForbiddenError
from aiogram.filters import StateFilter
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import pytest

from tests._harness.legacy_bot import (
    EVIDENCE_LABEL,
    SYNTHETIC_BOT_TOKEN,
    FakeCallbackQuery,
    FakeFile,
    FakeMessage,
    FakeUser,
    RecordingBot,
    SentMessage,
    TelegramEvent,
    TelegramLog,
    callback_rows,
    find_handler,
    make_state,
    route_message,
    use_synthetic_bot_settings,
)
import tests._harness.legacy_bot as legacy_bot


def _placeholder_environment(monkeypatch):
    monkeypatch.setenv("PYTHON_DOTENV_DISABLED", "placeholder")
    monkeypatch.setenv("BOT_TOKEN", "placeholder")
    monkeypatch.setenv("OWNER_ID", "placeholder")
    monkeypatch.setenv("BOT_MODE", "placeholder")


def test_label():
    assert EVIDENCE_LABEL == "substitute, not evidence"
    assert EVIDENCE_LABEL in legacy_bot.__doc__


def test_synthetic_settings_set_environment(monkeypatch):
    _placeholder_environment(monkeypatch)

    use_synthetic_bot_settings()

    assert os.environ["PYTHON_DOTENV_DISABLED"] == "1"
    assert os.environ["BOT_TOKEN"] == SYNTHETIC_BOT_TOKEN
    assert os.environ["OWNER_ID"] == "9001"
    assert os.environ["BOT_MODE"] == "polling"
    use_synthetic_bot_settings()


def test_synthetic_settings_refuse_foreign_config(monkeypatch):
    _placeholder_environment(monkeypatch)
    monkeypatch.setitem(
        sys.modules,
        "config",
        types.SimpleNamespace(BOT_TOKEN="999:not-the-synthetic-token"),
    )

    with pytest.raises(RuntimeError, match="imported before"):
        use_synthetic_bot_settings()

    assert os.environ["BOT_TOKEN"] == "placeholder"


def test_bot_records_and_blocks():
    async def scenario():
        log = TelegramLog()
        bot = RecordingBot(log, blocked_chat_ids={7})
        assert await bot.send_message(5, "hi", parse_mode="Markdown") == SentMessage(5, 1)
        assert await bot.send_photo(5, "photo-id", caption="cap") == SentMessage(5, 2)
        with pytest.raises(TelegramForbiddenError):
            await bot.send_message(7, "x")

        assert log.events == [
            TelegramEvent("send_message", 5, 1, "hi", "Markdown"),
            TelegramEvent("send_photo", 5, 2, "cap"),
            TelegramEvent("send_message", 7, None, "x", delivered=False),
        ]
        assert log.trace() == [("send_message", 5), ("send_photo", 5), ("send_message", 7)]
        assert len(log.select(chat_id=5)) == 2

    asyncio.run(scenario())


def test_message_and_callback():
    async def scenario():
        log = TelegramLog()
        msg = FakeMessage(log, 5, from_user=FakeUser(5))
        assert msg.message_id == 1
        assert msg.chat.id == 5
        await msg.edit_text("a")
        reply = await msg.answer("b")
        assert reply.message_id == 2
        await reply.edit_text("c")
        call = FakeCallbackQuery(log, FakeUser(5), "x:1", msg)
        await call.answer("no", show_alert=True)
        await call.answer()

        assert log.events == [
            TelegramEvent("edit_text", 5, 1, "a"),
            TelegramEvent("message_answer", 5, 2, "b"),
            TelegramEvent("edit_text", 5, 2, "c"),
            TelegramEvent("callback_answer", None, None, "no", show_alert=True),
            TelegramEvent("callback_answer", None, None, None),
        ]

    asyncio.run(scenario())


def test_find_handler_state_and_rows():
    router = Router()

    async def cb_x(call):
        return call

    router.callback_query.register(cb_x)
    assert find_handler(router, "callback_query", "cb_x") is cb_x
    with pytest.raises(KeyError, match="missing"):
        find_handler(router, "callback_query", "missing")

    async def state_scenario():
        state = make_state(5)
        assert state.key.user_id == state.key.chat_id == 5
        await state.update_data(a=1)
        assert await state.get_data() == {"a": 1}
        assert await state.get_state() is None

    asyncio.run(state_scenario())
    assert callback_rows(
        InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="A", callback_data="a")],
                [InlineKeyboardButton(text="B", callback_data="b")],
            ]
        )
    ) == [["a"], ["b"]]


def test_bot_sends_documents():
    async def scenario():
        log = TelegramLog()
        bot = RecordingBot(log, blocked_chat_ids={7})

        assert await bot.send_document(5, "doc-id", caption="cap", reply_markup="kb") == SentMessage(5, 1)
        with pytest.raises(TelegramForbiddenError):
            await bot.send_document(7, "doc-id", caption="c")

        assert log.events == [
            TelegramEvent("send_document", 5, 1, "cap", None, "kb"),
            TelegramEvent("send_document", 7, None, "c", delivered=False),
        ]

    asyncio.run(scenario())


def test_message_files():
    log = TelegramLog()
    empty = FakeMessage(log, 5)
    assert empty.photo is None
    assert empty.document is None

    message = FakeMessage(
        log,
        5,
        photo=[FakeFile("s"), FakeFile("l")],
        document=FakeFile("d"),
    )
    assert message.photo == [FakeFile("s"), FakeFile("l")]
    assert message.document == FakeFile("d")


def test_route_message_uses_router_filters():
    async def scenario():
        router = Router()

        async def in_state(message):
            return "state"

        async def got_photo(message):
            return "photo"

        router.message.register(in_state, StateFilter("S:a"))
        router.message.register(got_photo, F.photo)
        state = make_state(5)
        log = TelegramLog()
        bot = RecordingBot(log)

        assert await route_message(
            router, FakeMessage(log, 5, photo=[FakeFile("a")]), state, bot
        ) == "photo"
        assert await route_message(router, FakeMessage(log, 5, text="hi"), state, bot) is UNHANDLED

        await state.set_state("S:a")
        assert await route_message(
            router, FakeMessage(log, 5, photo=[FakeFile("a")]), state, bot
        ) == "state"

    asyncio.run(scenario())
