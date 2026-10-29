"""Characterize the optional ``WEBHOOK_SECRET`` in ``bot_manager.py`` at commit 18bf94e.

Baseline: ``.venv/bin/python -m pytest tests/characterization/test_webhook_secret.py --network=deny``.
Requests are built with ``aiohttp.test_utils.make_mocked_request`` and Telegram is a fake aiogram
session (substitute, not evidence); no socket is opened. Part of tasks.md T028 (FR-081; constitution I).

Observable contract: ``config.WEBHOOK_SECRET`` is read once at import from the environment and defaults
to ``""``. ``WebhookServer._dispatch`` checks the ``X-Telegram-Bot-Api-Secret-Token`` header only when
the secret is non-empty: a missing or different header gets 401 before the route lookup, and an unknown
token hash gets 404 (case 1); with an empty secret any header, or none, reaches the route lookup (case
2). The route is ``/webhook/{sha256(token) hex}``. ``start_bot`` in webhook mode passes the secret to
``setWebhook`` as ``secret_token``, and ``None`` when the secret is empty (case 3).
"""

import asyncio
import hashlib
import os
import subprocess
import sys
from pathlib import Path

import pytest
from aiogram import Bot
from aiogram.client.session.base import BaseSession
from aiogram.methods import SetWebhook
from aiohttp import web
from aiohttp.test_utils import make_mocked_request

import bot_manager
from tests._harness.legacy_bot import SYNTHETIC_BOT_TOKEN

SECRET = "synthetic-webhook-secret"
TOKEN = "200001:tenant-a-synthetic"
TOKEN_HASH = hashlib.sha256(TOKEN.encode()).hexdigest()
HEADER = "X-Telegram-Bot-Api-Secret-Token"
REPO_ROOT = Path(__file__).resolve().parents[2]


class _Handled:
    """Stands in for aiogram's ``SimpleRequestHandler`` (not the code under test)."""

    def __init__(self):
        self.requests = []

    async def handle(self, request):
        self.requests.append(request)
        return web.Response(status=200, text="handled")


def _server():
    server = bot_manager.WebhookServer()
    handler = _Handled()
    server._handlers[TOKEN_HASH] = handler
    return server, handler


def _status(server, token_hash, headers=None):
    request = make_mocked_request(
        "POST", f"/webhook/{token_hash}", headers=headers or {}, match_info={"token_hash": token_hash},
    )
    return asyncio.run(server._dispatch(request)).status


# Case 1
def test_set_secret_rejects_missing_or_wrong_header(monkeypatch):
    monkeypatch.setattr(bot_manager, "WEBHOOK_SECRET", SECRET)
    server, handler = _server()
    assert bot_manager._webhook_path_for_token(TOKEN) == TOKEN_HASH
    assert len(TOKEN_HASH) == 64
    assert _status(server, TOKEN_HASH) == 401
    assert _status(server, TOKEN_HASH, {HEADER: "wrong"}) == 401
    assert _status(server, TOKEN_HASH, {HEADER: ""}) == 401
    assert _status(server, TOKEN_HASH, {HEADER: SECRET + " "}) == 401
    assert _status(server, "0" * 64) == 401
    assert handler.requests == []
    assert _status(server, "0" * 64, {HEADER: SECRET}) == 404
    assert _status(server, TOKEN_HASH, {HEADER: SECRET}) == 200
    assert len(handler.requests) == 1


# Case 2
def test_empty_secret_skips_the_header_check(monkeypatch):
    monkeypatch.setattr(bot_manager, "WEBHOOK_SECRET", "")
    server, handler = _server()
    assert _status(server, TOKEN_HASH) == 200
    assert _status(server, TOKEN_HASH, {HEADER: "anything"}) == 200
    assert _status(server, "0" * 64) == 404
    assert len(handler.requests) == 2


class _StopStart(BaseException):
    """Ends ``start_bot`` right after ``setWebhook``; ``except Exception`` there does not catch it."""


class _RecordingSession(BaseSession):
    def __init__(self, calls):
        super().__init__()
        self.calls = calls

    async def make_request(self, bot, method, timeout=None):
        self.calls.append(method)
        if isinstance(method, SetWebhook):
            raise _StopStart
        return True

    async def stream_content(self, url, headers=None, timeout=30, chunk_size=65536, raise_for_status=True):
        raise NotImplementedError
        yield b""

    async def close(self):
        pass


# Case 3
@pytest.mark.parametrize(("secret", "expected"), [(SECRET, SECRET), ("", None)])
def test_start_bot_passes_secret_to_set_webhook(monkeypatch, tmp_path, secret, expected):
    calls = []

    async def no_listen(self, host, port):
        self.started = True

    monkeypatch.setattr(bot_manager, "BOT_MODE", "webhook")
    monkeypatch.setattr(bot_manager, "WEBHOOK_BASE_URL", "https://hook.example.invalid")
    monkeypatch.setattr(bot_manager, "WEBHOOK_SECRET", secret)
    monkeypatch.setattr(bot_manager.WebhookServer, "start", no_listen)
    monkeypatch.setattr(
        bot_manager, "Bot",
        lambda token, default=None: Bot(token=token, default=default, session=_RecordingSession(calls)),
    )
    manager = bot_manager.BotManager()
    with pytest.raises(_StopStart):
        asyncio.run(manager.start_bot(TOKEN, str(tmp_path / "a.db"), 700000001, is_main_bot=False))
    assert [type(m).__name__ for m in calls] == ["SetWebhook"]
    assert calls[0].url == f"https://hook.example.invalid/webhook/{TOKEN_HASH}"
    assert calls[0].secret_token == expected
    assert calls[0].drop_pending_updates is True
    assert manager.instances == {}


# Case 4
def test_config_default_is_empty_string(tmp_path):
    env = {k: v for k, v in os.environ.items() if k != "WEBHOOK_SECRET"}
    env.update(PYTHON_DOTENV_DISABLED="1", BOT_TOKEN=SYNTHETIC_BOT_TOKEN, OWNER_ID="1", BOT_MODE="polling")
    out = subprocess.run(
        [sys.executable, "-c", "import config; print(repr(config.WEBHOOK_SECRET))"],
        cwd=REPO_ROOT, env=env, capture_output=True, text=True, check=True,
    )
    assert out.stdout == "''\n"
