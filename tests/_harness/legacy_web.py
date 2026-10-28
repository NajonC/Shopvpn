"""Helpers for tasks.md T015 web panel order approval characterization.

Basis:

- Constitution VI: "All tests MUST use isolated synthetic or sanitized data and MUST NOT use production credentials or call production services."
- ``admin_panel/server.py`` opens ``config.DB_PATH``, the repository's
  ``bot_database.db``, and runs ``init_db`` at import. ``load_admin_panel``
  points it at a throwaway file inside the caller's directory first; under
  pytest this must be pytest's temporary directory because the network guard
  refuses SQLite files elsewhere.
- The recorder and cookie are substitutes, not evidence.
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
import json
import os
import sys
import tempfile
import time
from collections.abc import Iterable
from types import ModuleType

from tests._harness.legacy_bot import TelegramEvent, TelegramLog, use_synthetic_bot_settings


def load_admin_panel(db_dir: str | os.PathLike | None = None) -> ModuleType:
    """Load the web panel with its import-time database isolated from the repo."""
    use_synthetic_bot_settings()
    import config

    existing = sys.modules.get("admin_panel.server")
    if existing is not None:
        if existing.main_db.db_path == config.DB_PATH:
            raise RuntimeError("admin_panel.server was imported before load_admin_panel()")
        return existing

    original = config.DB_PATH
    config.DB_PATH = os.path.join(
        tempfile.mkdtemp(prefix="shopvpn-admin-panel-", dir=db_dir), "import.db"
    )
    try:
        import admin_panel.server as server
    finally:
        config.DB_PATH = original
    return server


def session_cookie(
    secret: str,
    admin_id: int,
    username: str,
    role: str,
    tenant: str = "",
    ttl_seconds: int = 3600,
) -> str:
    """Build a synthetic panel session cookie."""
    payload = {
        "id": admin_id,
        "u": username,
        "r": role,
        "b": tenant,
        "exp": int(time.time()) + ttl_seconds,
    }
    body = base64.urlsafe_b64encode(
        json.dumps(payload, separators=(",", ":")).encode("utf-8")
    ).rstrip(b"=").decode("ascii")
    signature = hmac.new(secret.encode("utf-8"), body.encode("ascii"), hashlib.sha256).hexdigest()
    return f"{body}.{signature}"


class BotApiRecorder:
    """Record synthetic Telegram sends without contacting Telegram."""

    def __init__(self, log: TelegramLog, blocked_chat_ids: Iterable[int] = ()) -> None:
        self.log = log
        self.blocked_chat_ids = set(blocked_chat_ids)
        self.tokens: list[str] = []

    async def send_message(
        self, bot_token, chat_id, text, parse_mode=None, reply_markup=None
    ) -> bool:
        self.tokens.append(bot_token)
        ok = chat_id not in self.blocked_chat_ids
        self.log.record(TelegramEvent(
            "send_message", chat_id, None, text, parse_mode, reply_markup, delivered=ok
        ))
        return ok

    async def send_photo(
        self, bot_token, chat_id, photo_bytes, filename="photo.png", caption=""
    ) -> bool:
        self.tokens.append(bot_token)
        ok = chat_id not in self.blocked_chat_ids
        self.log.record(TelegramEvent(
            "send_photo", chat_id, None, caption, delivered=ok
        ))
        return ok


async def drain_tasks() -> None:
    """Wait for outstanding background tasks, including nested tasks."""
    current = asyncio.current_task()
    while True:
        tasks = [task for task in asyncio.all_tasks() if task is not current and not task.done()]
        if not tasks:
            return
        await asyncio.gather(*tasks)
