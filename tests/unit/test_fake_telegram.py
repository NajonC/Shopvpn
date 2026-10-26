"""Fake Telegram bot for notification delivery (tasks.md T010; N-01).

Queue acceptance is not Telegram acceptance: a lost response or a crash
after dispatch leaves the message delivered while the sender cannot know it,
retry-after refuses sends until its window ends, and a blocked chat refuses
every send. Errors are aiogram's own, as the bot code already catches them.
"""

import asyncio
from datetime import datetime, timezone

from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramNetworkError,
    TelegramRetryAfter,
)
from aiogram.types import Message
import pytest

from tests._harness.clock import FakeClock
from tests._harness.fake_telegram import (
    EVIDENCE_LABEL,
    CrashAfterDispatch,
    FakeSendAttempt,
    FakeSentMessage,
    FakeTelegramBot,
)
import tests._harness.fake_telegram as fake_telegram


def _bot():
    clock = FakeClock()
    return clock, FakeTelegramBot(clock)


def test_label_and_docstring():
    assert EVIDENCE_LABEL == "substitute, not evidence"
    assert EVIDENCE_LABEL in fake_telegram.__doc__


def test_accepted_send_returns_a_message_reference_per_chat():
    async def scenario():
        clock, bot = _bot()
        clock.step_wall(-60_000)
        start = clock.true_now_ms()
        assert clock.now_ms() != start
        first = await bot.send_message(1001, "hello", parse_mode="HTML")
        assert isinstance(first, Message)
        assert (first.message_id, first.chat.id, first.text) == (1, 1001, "hello")
        assert first.date == datetime.fromtimestamp(start // 1000, tz=timezone.utc)
        clock.advance(1_000)
        second = await bot.send_message(1001, "again")
        other = await bot.send_message(2002, "other chat")
        assert (second.message_id, other.message_id) == (2, 1)
        assert bot.sent == (
            FakeSentMessage(1, 1001, "hello", start),
            FakeSentMessage(2, 1001, "again", start + 1_000),
            FakeSentMessage(1, 2002, "other chat", start + 1_000),
        )
        assert bot.attempts == (
            FakeSendAttempt(1001, "accepted", start),
            FakeSendAttempt(1001, "accepted", start + 1_000),
            FakeSendAttempt(2002, "accepted", start + 1_000),
        )

    asyncio.run(scenario())


def test_lost_response_delivers_but_raises_a_network_error():
    async def scenario():
        clock, bot = _bot()
        bot.queue_lost_response()
        with pytest.raises(TelegramNetworkError):
            await bot.send_message(1001, "paid")
        assert bot.sent == (FakeSentMessage(1, 1001, "paid", clock.true_now_ms()),)
        assert [attempt.outcome for attempt in bot.attempts] == ["lost response"]

    asyncio.run(scenario())


def test_crash_after_dispatch_delivers_then_crashes():
    async def scenario():
        _, bot = _bot()
        bot.queue_crash_after_dispatch()
        with pytest.raises(CrashAfterDispatch):
            await bot.send_message(1001, "renewed")
        assert [message.text for message in bot.sent] == ["renewed"]
        assert [attempt.outcome for attempt in bot.attempts] == ["crashed"]

    assert issubclass(CrashAfterDispatch, BaseException)
    assert not issubclass(CrashAfterDispatch, Exception)
    asyncio.run(scenario())


def test_retry_after_refuses_every_send_until_its_window_ends():
    async def scenario():
        clock, bot = _bot()
        bot.queue_retry_after(5)
        with pytest.raises(TelegramRetryAfter) as first:
            await bot.send_message(1001, "reminder")
        assert first.value.retry_after == 5
        clock.advance(2_500)
        with pytest.raises(TelegramRetryAfter) as second:
            await bot.send_message(2002, "another chat")
        assert second.value.retry_after == 3
        clock.advance(2_500)
        message = await bot.send_message(1001, "reminder")
        assert message.message_id == 1
        assert [attempt.outcome for attempt in bot.attempts] == [
            "retry after",
            "retry after",
            "accepted",
        ]
        assert [m.text for m in bot.sent] == ["reminder"]

    asyncio.run(scenario())


def test_blocked_chat_is_refused_until_unblocked():
    async def scenario():
        _, bot = _bot()
        bot.block_chat(1001)
        for _ in range(2):
            with pytest.raises(TelegramForbiddenError) as refused:
                await bot.send_message(1001, "alert")
            assert "bot was blocked by the user" in str(refused.value)
        assert (await bot.send_message(2002, "alert")).message_id == 1
        bot.unblock_chat(1001)
        assert (await bot.send_message(1001, "alert")).message_id == 1
        assert [attempt.outcome for attempt in bot.attempts] == [
            "rejected",
            "rejected",
            "accepted",
            "accepted",
        ]

    asyncio.run(scenario())


def test_empty_text_is_a_permanent_bad_request():
    async def scenario():
        _, bot = _bot()
        with pytest.raises(TelegramBadRequest) as refused:
            await bot.send_message(1001, "")
        assert "message text is empty" in str(refused.value)
        assert bot.sent == ()
        assert [attempt.outcome for attempt in bot.attempts] == ["rejected"]

    asyncio.run(scenario())


def test_queued_outcomes_apply_to_later_sends_in_order():
    async def scenario():
        _, bot = _bot()
        bot.queue_lost_response()
        bot.queue_crash_after_dispatch()
        with pytest.raises(TelegramNetworkError):
            await bot.send_message(1001, "one")
        with pytest.raises(CrashAfterDispatch):
            await bot.send_message(1001, "two")
        assert (await bot.send_message(1001, "three")).message_id == 3
        assert [attempt.outcome for attempt in bot.attempts] == [
            "lost response",
            "crashed",
            "accepted",
        ]

    asyncio.run(scenario())


def test_refusals_come_before_queued_outcomes():
    async def scenario():
        _, bot = _bot()
        bot.queue_lost_response()
        bot.block_chat(1001)
        with pytest.raises(TelegramForbiddenError):
            await bot.send_message(1001, "blocked")
        with pytest.raises(TelegramBadRequest):
            await bot.send_message(2002, "")
        with pytest.raises(TelegramNetworkError):
            await bot.send_message(2002, "lost")
        bot.queue_retry_after(1)
        bot.queue_lost_response()
        with pytest.raises(TelegramRetryAfter):
            await bot.send_message(2002, "flood")
        with pytest.raises(TelegramRetryAfter):
            await bot.send_message(2002, "still flood")
        assert [m.text for m in bot.sent] == ["lost"]

    asyncio.run(scenario())


def test_retry_after_needs_a_positive_whole_number_of_seconds():
    _, bot = _bot()
    for bad in (True, 1.5, "5", None):
        with pytest.raises(TypeError):
            bot.queue_retry_after(bad)
    for bad in (0, -1):
        with pytest.raises(ValueError):
            bot.queue_retry_after(bad)


def test_message_text_is_kept_out_of_reprs():
    async def scenario():
        _, bot = _bot()
        url = "https://sub.example.invalid/s/synthetic-subscription-token"
        await bot.send_message(1001, f"Your link: {url}")
        assert bot.sent[0].text == f"Your link: {url}"
        assert url not in repr(bot.sent)
        assert url not in repr(bot.attempts)
        assert url not in repr(bot)

    asyncio.run(scenario())
