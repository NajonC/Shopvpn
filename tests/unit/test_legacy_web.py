"""Unit tests for the offline web panel helpers used by legacy handlers."""

import asyncio
import os
import time

from tests._harness.legacy_bot import TelegramEvent, TelegramLog
from tests._harness.legacy_web import BotApiRecorder, drain_tasks, load_admin_panel, session_cookie


def test_load_admin_panel_uses_a_throwaway_database(tmp_path_factory):
    server = load_admin_panel(tmp_path_factory.getbasetemp())
    import config

    assert server.main_db.db_path != config.DB_PATH
    assert os.path.basename(server.main_db.db_path) == "import.db"
    assert not server.main_db.db_path.startswith(config.BASE_DIR)
    assert load_admin_panel(tmp_path_factory.getbasetemp()) is server


def test_session_cookie_matches_the_panel_format(tmp_path_factory):
    load_admin_panel(tmp_path_factory.getbasetemp())
    from admin_panel.security import verify_session_token

    token = session_cookie("k", 7, "mid1", "mid")
    payload = verify_session_token("k", token)
    assert payload["id"] == 7
    assert payload["u"] == "mid1"
    assert payload["r"] == "mid"
    assert payload["b"] == ""
    assert payload["exp"] > time.time()
    assert verify_session_token("k", session_cookie("k", 7, "mid1", "mid", tenant="t1"))["b"] == "t1"
    assert verify_session_token("other", token) is None
    assert verify_session_token("k", session_cookie("k", 7, "mid1", "mid", ttl_seconds=-1)) is None


def test_bot_api_recorder_records_and_blocks():
    async def scenario():
        log = TelegramLog()
        api = BotApiRecorder(log, blocked_chat_ids={2})
        assert await api.send_message("tok", 1, "hi", parse_mode="Markdown") is True
        assert await api.send_photo("tok", 2, b"png", "q.png", "cap") is False
        assert log.events == [
            TelegramEvent("send_message", 1, None, "hi", "Markdown", None),
            TelegramEvent("send_photo", 2, None, "cap", delivered=False),
        ]
        assert api.tokens == ["tok", "tok"]

    asyncio.run(scenario())


def test_drain_tasks_waits_for_nested_tasks():
    async def scenario():
        values = []

        async def inner():
            await asyncio.sleep(0)
            values.append("inner")

        async def outer():
            await asyncio.sleep(0)
            values.append("outer")
            asyncio.create_task(inner())

        asyncio.create_task(outer())
        await drain_tasks()
        assert values == ["outer", "inner"]

    asyncio.run(scenario())
