"""Synthetic settings and Telegram doubles for driving legacy aiogram handlers (tasks.md T013).

Basis:

* Constitution VI: "All tests MUST use isolated synthetic or sanitized data and
  MUST NOT use production credentials or call production services."
* quickstart.md: "No production environment/key/backup import." The legacy
  ``config`` module reads ``BOT_TOKEN``/``OWNER_ID`` and calls ``load_dotenv()``
  at import, so ``use_synthetic_bot_settings()`` must run before any legacy
  module is imported; ``tests/characterization/conftest.py`` calls it.
* The doubles record every Telegram effect, in order, in one shared log, and
  never contact Telegram. They are substitute, not evidence.
"""

from __future__ import annotations

import os
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any, Callable

from aiogram import Router
from aiogram.exceptions import TelegramForbiddenError
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.methods import SendMessage

from tests._harness.fixtures import MAIN_OWNER_TELEGRAM_ID


EVIDENCE_LABEL = "substitute, not evidence"
SYNTHETIC_BOT_TOKEN = "123456:characterization-not-a-real-token"
SYNTHETIC_OWNER_ID = MAIN_OWNER_TELEGRAM_ID


def use_synthetic_bot_settings() -> None:
    """Point the legacy ``config`` module at synthetic settings and never read a ``.env``."""
    config = sys.modules.get("config")
    if config is not None and getattr(config, "BOT_TOKEN", None) != SYNTHETIC_BOT_TOKEN:
        raise RuntimeError("legacy config was imported before use_synthetic_bot_settings()")

    os.environ["PYTHON_DOTENV_DISABLED"] = "1"
    os.environ["BOT_TOKEN"] = SYNTHETIC_BOT_TOKEN
    os.environ["OWNER_ID"] = str(SYNTHETIC_OWNER_ID)
    os.environ["BOT_MODE"] = "polling"

    import dotenv.main

    check = getattr(dotenv.main, "_load_dotenv_disabled", None)
    if check is None or not check():
        raise RuntimeError("installed python-dotenv does not honour PYTHON_DOTENV_DISABLED")


@dataclass(frozen=True)
class TelegramEvent:
    kind: str
    chat_id: int | None
    message_id: int | None
    text: str | None
    parse_mode: str | None = None
    reply_markup: object | None = None
    show_alert: bool = False
    delivered: bool = True


class TelegramLog:
    """Ordered Telegram effects and per-log synthetic message identifiers."""

    def __init__(self) -> None:
        self.events: list[TelegramEvent] = []
        self._next_id = 1

    def next_message_id(self) -> int:
        message_id = self._next_id
        self._next_id += 1
        return message_id

    def record(self, event: TelegramEvent) -> None:
        self.events.append(event)

    def trace(self) -> list[tuple[str, int | None]]:
        return [(event.kind, event.chat_id) for event in self.events]

    def select(
        self, kind: str | None = None, chat_id: int | None = None
    ) -> list[TelegramEvent]:
        return [
            event for event in self.events
            if (kind is None or event.kind == kind)
            and (chat_id is None or event.chat_id == chat_id)
        ]


@dataclass(frozen=True)
class FakeUser:
    id: int
    username: str | None = None
    first_name: str = "Test"
    is_bot: bool = False


@dataclass(frozen=True)
class FakeChat:
    id: int
    type: str = "private"


@dataclass(frozen=True)
class SentMessage:
    chat_id: int
    message_id: int


class RecordingBot:
    def __init__(self, log: TelegramLog, *, blocked_chat_ids: Iterable[int] = ()) -> None:
        self.log = log
        self.blocked_chat_ids = set(blocked_chat_ids)

    async def send_message(self, chat_id, text, **kwargs) -> SentMessage:
        return self._send("send_message", chat_id, text, **kwargs)

    async def send_photo(self, chat_id, photo, caption=None, **kwargs) -> SentMessage:
        return self._send("send_photo", chat_id, caption, **kwargs)

    def _send(self, kind: str, chat_id: int, text: str | None, **kwargs) -> SentMessage:
        blocked = chat_id in self.blocked_chat_ids
        message_id = None if blocked else self.log.next_message_id()
        self.log.record(TelegramEvent(
            kind,
            chat_id,
            message_id,
            text,
            kwargs.get("parse_mode"),
            kwargs.get("reply_markup"),
            delivered=not blocked,
        ))
        if blocked:
            raise TelegramForbiddenError(
                method=SendMessage(chat_id=chat_id, text=text or ""),
                message="Forbidden: bot was blocked by the user",
            )
        return SentMessage(chat_id, message_id)


class FakeMessage:
    def __init__(
        self,
        log: TelegramLog,
        chat_id: int,
        *,
        from_user: FakeUser | None = None,
        text: str | None = None,
        message_id: int | None = None,
    ) -> None:
        self.log = log
        self.chat = FakeChat(chat_id)
        self.message_id = log.next_message_id() if message_id is None else message_id
        self.from_user = from_user
        self.text = text

    async def edit_text(
        self, text, parse_mode=None, reply_markup=None, **kwargs
    ) -> FakeMessage:
        self.log.record(TelegramEvent(
            "edit_text", self.chat.id, self.message_id, text, parse_mode, reply_markup
        ))
        return self

    async def answer(self, text, parse_mode=None, reply_markup=None, **kwargs) -> FakeMessage:
        new = FakeMessage(self.log, self.chat.id, text=text)
        self.log.record(TelegramEvent(
            "message_answer", self.chat.id, new.message_id, text, parse_mode, reply_markup
        ))
        return new

    async def delete(self) -> bool:
        self.log.record(TelegramEvent("message_delete", self.chat.id, self.message_id, None))
        return True


class FakeCallbackQuery:
    def __init__(self, log: TelegramLog, from_user: FakeUser, data: str, message: FakeMessage) -> None:
        self.log = log
        self.from_user = from_user
        self.data = data
        self.message = message

    async def answer(self, text=None, show_alert=None, **kwargs) -> bool:
        self.log.record(TelegramEvent(
            "callback_answer", None, None, text, show_alert=bool(show_alert)
        ))
        return True


def find_handler(router: Router, observer: str, name: str) -> Callable[..., Any]:
    for handler in getattr(router, observer).handlers:
        if handler.callback.__name__ == name:
            return handler.callback
    raise KeyError(f"{observer} handler {name!r} not found")


def make_state(user_id: int, *, chat_id: int | None = None, bot_id: int = 1) -> FSMContext:
    return FSMContext(
        storage=MemoryStorage(),
        key=StorageKey(
            bot_id=bot_id,
            chat_id=user_id if chat_id is None else chat_id,
            user_id=user_id,
        ),
    )


def callback_rows(markup) -> list[list[str | None]]:
    return [[button.callback_data for button in row] for row in markup.inline_keyboard]
