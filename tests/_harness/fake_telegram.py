"""A controlled Telegram bot stand-in for aiogram: substitute, not evidence.

Basis for its behavior:

* Contract (contracts/operations.md N-01): result fields, outcomes (accepted,
  rejected, retry after, lost response, crashed), and retry semantics.
* Source (aiogram 3.31.0): aiogram error classes (TelegramBadRequest,
  TelegramForbiddenError, TelegramNetworkError, TelegramRetryAfter) and error
  texts ("Bad Request: message text is empty", "Forbidden: bot was blocked by the user",
  "Too Many Requests: retry after {n}", "Request timeout error").
* Fake choice: global retry-after window, per-chat sequential message IDs,
  recording of sent messages and attempts, and synthetic outcome queuing
  (CrashAfterDispatch, lost response).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramNetworkError,
    TelegramRetryAfter,
)
from aiogram.methods import SendMessage
from aiogram.types import Chat, Message

if TYPE_CHECKING:
    from tests._harness.clock import FakeClock

EVIDENCE_LABEL = "substitute, not evidence"


class CrashAfterDispatch(BaseException):
    """Synthetic crash simulating process death immediately after dispatch."""


@dataclass(frozen=True)
class FakeSentMessage:
    message_id: int
    chat_id: int | str
    text: str = field(repr=False)
    accepted_ms: int


@dataclass(frozen=True)
class FakeSendAttempt:
    chat_id: int | str
    outcome: str
    at_ms: int


class FakeTelegramBot:
    """Fake Telegram bot standing in for aiogram's Bot.send_message."""

    def __init__(self, clock: FakeClock) -> None:
        self._clock: FakeClock = clock
        self._sent: list[FakeSentMessage] = []
        self._attempts: list[FakeSendAttempt] = []
        self._blocked_chats: set[int | str] = set()
        self._queue: list[tuple[str, ...] | tuple[str, int]] = []
        self._retry_after_until_ms: int = 0
        self._chat_message_counters: dict[int | str, int] = {}

    @property
    def sent(self) -> tuple[FakeSentMessage, ...]:
        return tuple(self._sent)

    @property
    def attempts(self) -> tuple[FakeSendAttempt, ...]:
        return tuple(self._attempts)

    def queue_lost_response(self) -> None:
        self._queue.append(("lost_response",))

    def queue_crash_after_dispatch(self) -> None:
        self._queue.append(("crash",))

    def queue_retry_after(self, seconds: int) -> None:
        if type(seconds) is not int:
            raise TypeError(f"seconds must be an int, got {type(seconds).__name__}")
        if seconds <= 0:
            raise ValueError(f"seconds must be > 0, got {seconds}")
        self._queue.append(("retry_after", seconds))

    def block_chat(self, chat_id: int | str) -> None:
        self._blocked_chats.add(chat_id)

    def unblock_chat(self, chat_id: int | str) -> None:
        self._blocked_chats.discard(chat_id)

    def __repr__(self) -> str:
        return "FakeTelegramBot()"

    def __str__(self) -> str:
        return self.__repr__()

    def _deliver(self, chat_id: int | str, text: str, now: int) -> int:
        msg_id = self._chat_message_counters.get(chat_id, 0) + 1
        self._chat_message_counters[chat_id] = msg_id
        self._sent.append(FakeSentMessage(msg_id, chat_id, text, now))
        return msg_id

    async def send_message(
        self, chat_id: int | str, text: str, **kwargs: object
    ) -> Message:
        now = self._clock.true_now_ms()
        method = SendMessage(chat_id=chat_id, text=text)

        # 1. Empty text check
        if text == "":
            self._attempts.append(FakeSendAttempt(chat_id, "rejected", now))
            raise TelegramBadRequest(
                method=method, message="Bad Request: message text is empty"
            )

        # 2. Blocked chat check
        if chat_id in self._blocked_chats:
            self._attempts.append(FakeSendAttempt(chat_id, "rejected", now))
            raise TelegramForbiddenError(
                method=method, message="Forbidden: bot was blocked by the user"
            )

        # 3. Retry-after window open check
        if now < self._retry_after_until_ms:
            rem_ms = self._retry_after_until_ms - now
            n = (rem_ms + 999) // 1000
            self._attempts.append(FakeSendAttempt(chat_id, "retry after", now))
            raise TelegramRetryAfter(
                method=method,
                message=f"Too Many Requests: retry after {n}",
                retry_after=n,
            )

        # 4. Oldest queued outcome check
        if self._queue:
            queued = self._queue.pop(0)
            kind = queued[0]
            if kind == "retry_after":
                seconds = queued[1]
                self._retry_after_until_ms = now + (seconds * 1000)
                self._attempts.append(FakeSendAttempt(chat_id, "retry after", now))
                raise TelegramRetryAfter(
                    method=method,
                    message=f"Too Many Requests: retry after {seconds}",
                    retry_after=seconds,
                )
            elif kind == "lost_response":
                self._deliver(chat_id, text, now)
                self._attempts.append(FakeSendAttempt(chat_id, "lost response", now))
                raise TelegramNetworkError(
                    method=method, message="Request timeout error"
                )
            elif kind == "crash":
                self._deliver(chat_id, text, now)
                self._attempts.append(FakeSendAttempt(chat_id, "crashed", now))
                raise CrashAfterDispatch("crash after dispatch")

        # 5. Otherwise deliver and return Message, outcome "accepted"
        msg_id = self._deliver(chat_id, text, now)
        self._attempts.append(FakeSendAttempt(chat_id, "accepted", now))
        dt = datetime.fromtimestamp(now // 1000, tz=timezone.utc)
        chat = (
            Chat(id=chat_id, type="private")
            if isinstance(chat_id, int)
            or (isinstance(chat_id, str) and chat_id.lstrip("-").isdigit())
            else Chat.model_construct(id=chat_id, type="private")
        )
        return Message(
            message_id=msg_id,
            date=dt,
            chat=chat,
            text=text,
        )
