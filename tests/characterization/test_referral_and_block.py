"""Characterize referral rewards, first-purchase flag consumption and shop-account blocking at commit 3d8b3c7.

Baseline: ``.venv/bin/python -m pytest tests/characterization/test_referral_and_block.py --network=deny``.
Every database is a SQLite file under ``tmp_path``; no panel, payment service or Telegram is contacted.

Pins (NG-05; FR-063): (a) the referrer is set once, only to an existing other user, and the first-purchase reward is a floored percent paid once (cases 1, 2); (b) disabled referral settings leave the first-purchase flag unconsumed, while a zero reward consumes it and counts toward the per-referrer cap (cases 3–5); (c) the inline-reseller commission is paid on every call whatever the referral settings (case 6); (d) the invite bonus is paid again on a repeated call for the same invitee, and the free-config prize returns an unchecked product id once per referrer (cases 7–9); (e) the middleware renames a blocked user before refusing and lets admins through, and it is registered first (cases 10–12); (f) a block changes only users.is_blocked, staff with the users permission may block but gain no owner powers, and blocking an unknown user is logged as done (cases 13, 14); (g) the Mini App refuses blocked top-ups and orders but not test claims, the bot test handler has no block check, and blocked users still earn referral rewards (cases 15–17).
"""

import asyncio
import hashlib
import hmac
import importlib
import json
import os
import sys
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import urlencode

import httpx
import pytest

import blocked_user
import config
import database
import handlers_user
from tests._harness.legacy_bot import (
    SYNTHETIC_BOT_TOKEN,
    FakeCallbackQuery,
    FakeMessage,
    FakeUser,
    RecordingBot,
    TelegramLog,
    find_handler,
    make_state,
)
from tests._harness.legacy_web import load_admin_panel, session_cookie


BLOCKED_BOT = "\u26d4\ufe0f حساب شما توسط مدیریت مسدود شده است. برای پیگیری با پشتیبانی تماس بگیرید."
BLOCKED_MINI = "حساب شما مسدود شده است."
INVITE_BONUS_5000 = "🤝 یک نفر با لینک دعوت شما به بات آمد!\n💰 5,000 تومان به کیف پول شما اضافه شد."
FREE_CONFIG_SUPPORT = "🎁 شما با تعداد دعوت\u200cهای خود، یک کانفیگ رایگان برنده شدید! برای دریافت آن با پشتیبانی تماس بگیرید."
TEST_LINK_TEXT = "🧪 کانفیگ تست شما:\n\n`vless://t@x.invalid:443#t`"
ALREADY_TESTED_MINI = "شما قبلاً کانفیگ تست خود را دریافت کرده\u200cاید."
NO_PERMISSION = "دسترسی کافی نیست."
OWNER_ONLY = "این بخش فقط برای مالک است."
WELCOME = database.DEFAULT_SETTINGS["welcome_text"]
OWNER = 9001
BUYER, REFERRER, OTHER, U4, U5, U6 = 1001, 1002, 1003, 1004, 1005, 1006
TEST_LINK = "vless://t@x.invalid:443#t"
L1, L2 = "vless://a@x.invalid:443#1", "vless://b@x.invalid:443#2"


def _rows(db, sql, params=()):
    with db._get_conn() as conn:
        return [tuple(r) for r in conn.execute(sql, params)]


def _flag(db, tg_id):
    return db.get_user(tg_id)["referral_first_purchase_rewarded"]


def _snapshot(db):
    names = [r[0] for r in _rows(db, "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
    return {name: _rows(db, f"SELECT * FROM {name} ORDER BY rowid") for name in names}


def _load_miniapp(base_dir):
    existing = sys.modules.get("miniapp.server")
    if existing is not None:
        if existing.main_db.db_path == config.DB_PATH:
            raise RuntimeError("miniapp.server was imported before _load_miniapp()")
        return existing

    original = config.DB_PATH
    config.DB_PATH = os.path.join(tempfile.mkdtemp(prefix="shopvpn-miniapp-", dir=base_dir), "import.db")
    try:
        return importlib.import_module("miniapp.server")
    finally:
        config.DB_PATH = original


def _init_data(token, tg_id, auth_date="now"):
    pairs = {"user": json.dumps({"id": tg_id, "username": f"u{tg_id}", "first_name": "U"}, separators=(",", ":"))}
    if auth_date == "now":
        pairs["auth_date"] = str(int(time.time()))
    elif auth_date is not None:
        pairs["auth_date"] = str(auth_date)
    check = "\n".join(f"{k}={v}" for k, v in sorted(pairs.items()))
    key = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    pairs["hash"] = hmac.new(key, check.encode(), hashlib.sha256).hexdigest()
    return urlencode(pairs)


def _call(server, method, url, token=None, tg_id=None, init_data=None, **kwargs):
    headers = {}
    if init_data is not None:
        headers["X-Init-Data"] = init_data
    elif token:
        headers["X-Init-Data"] = _init_data(token, tg_id)

    async def request():
        transport = httpx.ASGITransport(app=server.app, raise_app_exceptions=False)
        async with httpx.AsyncClient(transport=transport, base_url="http://miniapp.test") as client:
            return await client.request(method, url, headers=headers, **kwargs)

    response = asyncio.run(request())
    return response.status_code, response.json()


@pytest.fixture
def db(tmp_path):
    conn = database.Database(str(tmp_path / "main.db"))
    conn.init_db(OWNER)
    for u in (BUYER, REFERRER, OTHER, U4, U5, U6):
        conn.add_or_update_user(u, f"u{u}", "U")
    yield conn
    conn.close()


@pytest.fixture
def web(monkeypatch, tmp_path_factory, tmp_path):
    panel = load_admin_panel(tmp_path_factory.getbasetemp())
    main = database.Database(str(tmp_path / "main.db"))
    main.init_db(OWNER)
    monkeypatch.setattr(panel, "main_db", main)
    monkeypatch.setattr(panel.MAIN_TENANT, "db", main)
    main.add_or_update_user(BUYER, "u1001", "U")
    main.add_or_update_user(REFERRER, "u1002", "U")
    assert main.create_web_admin("mainowner", "synthetic-hash", role="owner") == 1
    assert main.create_web_admin("staffusers", "synthetic-hash", role="support", permissions=["users"]) == 2
    assert main.create_web_admin("stafforders", "synthetic-hash", role="support", permissions=["orders"]) == 3
    yield SimpleNamespace(panel=panel, main=main, secret=panel.ADMIN_PANEL_SECRET)
    main.close()


@pytest.fixture
def mini(monkeypatch, tmp_path_factory, tmp_path):
    server = _load_miniapp(tmp_path_factory.getbasetemp())
    main = database.Database(str(tmp_path / "main.db"))
    main.init_db(OWNER)
    monkeypatch.setattr(server, "main_db", main)
    main.add_or_update_user(BUYER, "u1001", "U")
    main.add_or_update_user(REFERRER, "u1002", "U")
    yield SimpleNamespace(server=server, main=main)
    main.close()


# Case 1
def test_set_referred_by_keeps_only_the_first_existing_referrer(db):
    db.set_referred_by(BUYER, BUYER)
    db.set_referred_by(BUYER, 7777)
    db.set_referred_by(8888, REFERRER)
    assert db.get_user(BUYER)["referred_by"] is None
    assert db.get_user(8888) is None
    db.set_referred_by(BUYER, REFERRER)
    db.set_referred_by(BUYER, OTHER)
    assert db.get_user(BUYER)["referred_by"] == REFERRER


# Case 2
def test_first_purchase_reward_is_a_floored_percent_paid_once(db):
    db.set_referred_by(BUYER, REFERRER)
    assert db.reward_referrer_if_first_purchase(OTHER, 100_000) is None
    assert _flag(db, OTHER) == 0 and db.get_wallet_credit(REFERRER) == 0
    assert db.reward_referrer_if_first_purchase(4242, 100_000) is None
    assert db.reward_referrer_if_first_purchase(BUYER, 99_999) == (9_999, REFERRER)
    assert _flag(db, BUYER) == 1 and db.get_wallet_credit(REFERRER) == 9_999
    assert db.reward_referrer_if_first_purchase(BUYER, 99_999) is None
    assert db.get_wallet_credit(REFERRER) == 9_999
    db.set_setting("referral_percent", "25")
    db.set_referred_by(U4, REFERRER)
    assert db.reward_referrer_if_first_purchase(U4, 1_000) == (250, REFERRER)
    assert db.get_wallet_credit(REFERRER) == 10_249


# Case 3
def test_disabled_referral_settings_leave_the_flag_unconsumed(db):
    db.set_referred_by(BUYER, REFERRER)
    db.set_setting("referral_enabled", "0")
    assert db.reward_referrer_if_first_purchase(BUYER, 100_000) is None
    assert _flag(db, BUYER) == 0 and db.get_wallet_credit(REFERRER) == 0
    db.set_setting("referral_enabled", "1")
    db.set_setting("referral_button_enabled", "0")
    assert db.reward_referrer_if_first_purchase(BUYER, 100_000) is None
    assert _flag(db, BUYER) == 0
    db.set_setting("referral_button_enabled", "1")
    assert db.reward_referrer_if_first_purchase(BUYER, 100_000) == (10_000, REFERRER)
    assert _flag(db, BUYER) == 1 and db.get_wallet_credit(REFERRER) == 10_000


# Case 4
def test_zero_reward_still_consumes_the_flag(db):
    for user in (BUYER, OTHER, U4):
        db.set_referred_by(user, REFERRER)
    db.set_setting("referral_percent", "0")
    assert db.reward_referrer_if_first_purchase(BUYER, 100_000) is None
    assert _flag(db, BUYER) == 1
    db.set_setting("referral_percent", "10")
    assert db.reward_referrer_if_first_purchase(BUYER, 100_000) is None
    assert db.get_wallet_credit(REFERRER) == 0
    assert db.reward_referrer_if_first_purchase(OTHER, 9) is None
    assert _flag(db, OTHER) == 1
    assert db.reward_referrer_if_first_purchase(U4, 0) is None
    assert _flag(db, U4) == 1 and db.get_wallet_credit(REFERRER) == 0


# Case 5
def test_commission_cap_counts_consumed_flags_per_referrer(db):
    for user in (BUYER, OTHER, U4, U5):
        db.set_referred_by(user, REFERRER)
    db.set_referred_by(U6, OTHER)
    db.set_setting("referral_commission_max_count", "1")
    db.set_setting("referral_percent", "0")
    assert db.reward_referrer_if_first_purchase(BUYER, 100_000) is None
    assert _flag(db, BUYER) == 1
    db.set_setting("referral_percent", "10")
    assert db.reward_referrer_if_first_purchase(OTHER, 100_000) is None
    assert _flag(db, OTHER) == 1 and db.get_wallet_credit(REFERRER) == 0
    assert db.reward_referrer_if_first_purchase(U6, 100_000) == (10_000, OTHER)
    assert db.get_wallet_credit(OTHER) == 10_000
    db.set_setting("referral_commission_max_count", "3")
    assert db.reward_referrer_if_first_purchase(U4, 100_000) == (10_000, REFERRER)
    assert db.get_wallet_credit(REFERRER) == 10_000
    assert db.reward_referrer_if_first_purchase(U5, 100_000) is None
    assert _flag(db, U5) == 1 and db.get_wallet_credit(REFERRER) == 10_000


# Case 6
def test_inline_reseller_commission_runs_on_every_call(db):
    db.enable_inline_reseller(U4, 20)
    db.set_owner_reseller_id(U5, U4)
    db.set_setting("referral_enabled", "0")
    db.set_setting("referral_button_enabled", "0")
    assert db.reward_referrer_if_first_purchase(U5, 50_000) is None
    assert db.get_wallet_credit(U4) == 10_000
    expected = [(U4, U5, 50_000, 10_000)]
    assert _rows(db, "SELECT owner_reseller_id, buyer_id, paid_amount, commission_amount FROM reseller_inline_commission_log") == expected
    assert db.reward_referrer_if_first_purchase(U5, 50_000) is None
    assert db.get_wallet_credit(U4) == 20_000 and _flag(db, U5) == 0
    assert db.reward_referrer_if_first_purchase(U5, 0) is None
    assert db.get_wallet_credit(U4) == 20_000
    db.set_setting("reseller_inline_commission_enabled", "0")
    assert db.reward_referrer_if_first_purchase(U5, 50_000) is None
    assert db.get_wallet_credit(U4) == 20_000
    assert len(_rows(db, "SELECT * FROM reseller_inline_commission_log")) == 2


# Case 7
def test_invite_bonus_pays_on_every_call_up_to_the_cap(db):
    for user in (OTHER, U4, U5):
        db.set_referred_by(user, REFERRER)
    empty = {"invite_bonus": None, "free_config_product_id": None}
    assert db.apply_referral_invite_rewards(OTHER, REFERRER) == empty
    assert db.get_wallet_credit(REFERRER) == 0
    db.set_setting("referral_invite_bonus_enabled", "1")
    db.set_setting("referral_invite_bonus_amount", "5000")
    db.set_setting("referral_invite_bonus_max_count", "2")
    assert db.apply_referral_invite_rewards(OTHER, REFERRER) == {"invite_bonus": 5000, "free_config_product_id": None}
    assert db.apply_referral_invite_rewards(U4, REFERRER) == {"invite_bonus": 5000, "free_config_product_id": None}
    assert db.apply_referral_invite_rewards(U5, REFERRER) == empty
    assert db.get_wallet_credit(REFERRER) == 10_000
    assert [db.get_user(u)["referral_invite_bonus_given"] for u in (OTHER, U4, U5)] == [1, 1, 0]
    db.set_setting("referral_invite_bonus_max_count", "0")
    for _ in range(2):
        assert db.apply_referral_invite_rewards(U5, REFERRER)["invite_bonus"] == 5000
    assert db.get_wallet_credit(REFERRER) == 20_000
    assert db.apply_referral_invite_rewards(OTHER, 7777) == empty
    db.set_setting("referral_button_enabled", "0")
    assert db.apply_referral_invite_rewards(OTHER, REFERRER) == empty
    assert db.get_wallet_credit(REFERRER) == 20_000
    db.set_setting("referral_button_enabled", "1")
    db.set_setting("referral_invite_bonus_amount", "0")
    assert db.apply_referral_invite_rewards(OTHER, REFERRER) == empty
    assert db.get_wallet_credit(REFERRER) == 20_000


# Case 8
def test_free_config_reward_is_one_time_at_the_threshold(db):
    db.set_setting("referral_free_config_enabled", "1")
    db.set_setting("referral_free_config_threshold", "2")
    db.set_setting("referral_free_config_product_id", "7")
    results = []
    for user in (OTHER, U4, U5):
        db.set_referred_by(user, REFERRER)
        results.append(db.apply_referral_invite_rewards(user, REFERRER))
    assert [r["free_config_product_id"] for r in results] == [None, 7, None]
    assert all(r["invite_bonus"] is None for r in results)
    assert db.get_user(REFERRER)["referral_free_config_given"] == 1
    db.set_referred_by(U6, OTHER)
    db.set_setting("referral_free_config_threshold", "0")
    assert db.apply_referral_invite_rewards(U6, OTHER) == {"invite_bonus": None, "free_config_product_id": None}
    db.set_setting("referral_free_config_threshold", "1")
    db.set_setting("referral_free_config_product_id", "")
    assert db.apply_referral_invite_rewards(U6, OTHER) == {"invite_bonus": None, "free_config_product_id": None}
    db.set_setting("referral_free_config_product_id", "8")
    assert db.apply_referral_invite_rewards(U6, OTHER) == {"invite_bonus": None, "free_config_product_id": 8}
    assert db.get_user(OTHER)["referral_free_config_given"] == 1


# Case 9
def test_start_ref_link_records_the_referrer_and_sends_invite_rewards(db):
    db.set_setting("referral_invite_bonus_enabled", "1")
    db.set_setting("referral_invite_bonus_amount", "5000")
    db.set_setting("referral_invite_bonus_max_count", "0")
    pid = db.add_product(db.add_category("C"), "Gift", 50_000)
    db.set_setting("referral_free_config_enabled", "1")
    db.set_setting("referral_free_config_threshold", "1")
    db.set_setting("referral_free_config_product_id", str(pid))
    log = TelegramLog()
    bot = RecordingBot(log)
    cmd_start = find_handler(handlers_user.create_user_router(db, is_main_bot=True), "message", "cmd_start")

    def start(uid, text):
        msg = FakeMessage(log, uid, from_user=FakeUser(uid, "new", "N"), text=text)
        asyncio.run(cmd_start(msg, make_state(uid), bot))

    start(BUYER, "/start ref1002")
    assert [(e.kind, e.chat_id, e.text) for e in log.events] == [
        ("send_message", REFERRER, INVITE_BONUS_5000),
        ("send_message", REFERRER, FREE_CONFIG_SUPPORT),
        ("message_answer", BUYER, WELCOME),
    ]
    assert tuple(db.get_user(BUYER)[k] for k in ("username", "referred_by", "referral_invite_bonus_given")) == ("new", REFERRER, 1)
    assert db.get_wallet_credit(REFERRER) == 5000
    assert db.get_user(REFERRER)["referral_free_config_given"] == 1
    log.events.clear()
    start(BUYER, "/start ref1003")
    start(OTHER, "/start ref1003")
    start(1007, "/start ref7777")
    assert log.trace() == [("message_answer", BUYER), ("message_answer", OTHER), ("message_answer", 1007)]
    assert db.get_user(BUYER)["referred_by"] == REFERRER
    assert db.get_user(OTHER)["referred_by"] is None
    assert db.get_user(1007)["referred_by"] is None
    assert db.get_wallet_credit(REFERRER) == 5000 and db.get_wallet_credit(OTHER) == 0


# Case 10
def test_middleware_lets_unblocked_users_and_admins_through(db, monkeypatch):
    monkeypatch.setattr(blocked_user, "Message", FakeMessage)
    monkeypatch.setattr(blocked_user, "CallbackQuery", FakeCallbackQuery)
    mw = blocked_user.BlockedUserMiddleware(db)
    log = TelegramLog()
    handled = []

    async def handler(event, data):
        handled.append(event)
        return "handled"

    m = FakeMessage(log, BUYER, text="hi")
    assert asyncio.run(mw(handler, m, {"event_from_user": FakeUser(BUYER, "renamed", "R")})) == "handled"
    assert (db.get_user(BUYER)["username"], db.get_user(BUYER)["first_name"]) == ("renamed", "R")
    assert asyncio.run(mw(handler, m, {"event_from_user": FakeUser(1007, None, "")})) == "handled"
    assert tuple(db.get_user(1007)[k] for k in ("username", "first_name", "is_blocked")) == ("", "", 0)
    db.add_or_update_user(OWNER, "owner", "O")
    db.set_user_blocked(OWNER, True)
    assert asyncio.run(mw(handler, m, {"event_from_user": FakeUser(OWNER, "owner", "O")})) == "handled"
    count = db.count_users()
    assert asyncio.run(mw(handler, m, {})) == "handled"
    assert db.count_users() == count

    def fail(*args):
        raise RuntimeError("synthetic")

    monkeypatch.setattr(db, "add_or_update_user", fail)
    assert asyncio.run(mw(handler, m, {"event_from_user": FakeUser(1008, "x", "X")})) == "handled"
    assert db.get_user(1008) is None
    assert len(handled) == 5 and log.events == []


# Case 11
def test_middleware_refuses_blocked_users_after_registering_them(db, monkeypatch):
    monkeypatch.setattr(blocked_user, "Message", FakeMessage)
    monkeypatch.setattr(blocked_user, "CallbackQuery", FakeCallbackQuery)
    mw = blocked_user.BlockedUserMiddleware(db)
    log = TelegramLog()
    handled = []

    async def handler(event, data):
        handled.append(event)
        return "handled"

    db.set_user_blocked(BUYER, True)
    assert blocked_user.BLOCKED_MESSAGE == BLOCKED_BOT
    m = FakeMessage(log, BUYER, text="hi")
    assert asyncio.run(mw(handler, m, {"event_from_user": FakeUser(BUYER, "again", "A")})) is None
    assert [(e.kind, e.chat_id, e.text, e.show_alert) for e in log.events] == [("message_answer", BUYER, BLOCKED_BOT, False)]
    assert (db.get_user(BUYER)["username"], db.get_user(BUYER)["first_name"]) == ("again", "A")
    log.events.clear()
    callback = FakeCallbackQuery(log, FakeUser(BUYER), "buy:1", m)
    assert asyncio.run(mw(handler, callback, {"event_from_user": FakeUser(BUYER, "again", "A")})) is None
    assert [(e.kind, e.chat_id, e.text, e.show_alert) for e in log.events] == [("callback_answer", None, BLOCKED_BOT, True)]
    log.events.clear()
    assert asyncio.run(mw(handler, SimpleNamespace(), {"event_from_user": FakeUser(BUYER, "again", "A")})) is None
    assert log.events == []

    def fail(*args):
        raise RuntimeError("synthetic")

    monkeypatch.setattr(db, "add_or_update_user", fail)
    assert asyncio.run(mw(handler, m, {"event_from_user": FakeUser(BUYER, "y", "Y")})) is None
    assert len(log.events) == 1 and log.events[0].kind == "message_answer"
    assert db.get_user(BUYER)["username"] == "again"
    assert handled == []


# Case 12
def test_blocking_is_registered_first_on_messages_and_callbacks():
    text = (Path(__file__).resolve().parents[2] / "bot_manager.py").read_text()
    assert text.count("BlockedUserMiddleware(db)") == 1
    for observer in ("message", "callback_query"):
        lines = [f"dp.{observer}.outer_middleware({name})" for name in ("blocked_mw", "presence_mw", "force_join_mw")]
        for line in lines:
            assert text.count(line) == 1
        positions = [text.index(line) for line in lines]
        assert positions == sorted(positions)


# Case 13
def test_block_flag_changes_nothing_else(db):
    pid = db.add_product(db.add_category("C"), "P", 100_000)
    db.add_configs(pid, [L1, L2])
    db.take_unused_configs(pid, BUYER, 1)
    db.take_unused_configs(pid, OTHER, 1)
    with db._get_conn() as conn:
        conn.execute("UPDATE configs SET is_disabled=1 WHERE assigned_user_id=?", (BUYER,))
        conn.execute("UPDATE configs SET expires_at=? WHERE assigned_user_id=?", ((datetime.utcnow() - timedelta(days=1)).isoformat(), OTHER))
    db.set_referred_by(BUYER, REFERRER)
    db.add_wallet_credit(BUYER, 30_000)
    assert db.get_user_status(BUYER) == "active" and db.get_user_status(OTHER) == "expired"
    assert db.get_all_user_ids() == [BUYER, REFERRER, OTHER, U4, U5, U6]
    assert db.get_expired_user_ids() == [OTHER]
    s0 = _snapshot(db)
    db.set_user_blocked(BUYER, True)
    db.set_user_blocked(OTHER, True)
    db.set_user_blocked(4242, True)
    s1 = _snapshot(db)
    assert {k: v for k, v in s1.items() if k != "users"} == {k: v for k, v in s0.items() if k != "users"}
    cols = [r[1] for r in _rows(db, "PRAGMA table_info(users)")]
    before = {r[cols.index("telegram_id")]: dict(zip(cols, r)) for r in s0["users"]}
    after = {r[cols.index("telegram_id")]: dict(zip(cols, r)) for r in s1["users"]}
    changed = {uid: [c for c in cols if before[uid][c] != after[uid][c]] for uid in before}
    assert {uid: fields for uid, fields in changed.items() if fields} == {BUYER: ["is_blocked"], OTHER: ["is_blocked"]}
    assert 4242 not in after
    assert db.get_user_status(BUYER) == "blocked" and db.get_user_status(OTHER) == "blocked"
    assert db.get_all_user_ids() == [REFERRER, U4, U5, U6]
    assert db.get_expired_user_ids() == [] and db.get_wallet_credit(BUYER) == 30_000
    db.set_user_blocked(BUYER, False)
    db.set_user_blocked(OTHER, False)
    assert _snapshot(db) == s0 and db.get_user_status(BUYER) == "active"


def _web_call(web, method, url, admin_id):
    cookie = session_cookie(web.secret, admin_id, f"admin{admin_id}", "owner" if admin_id == 1 else "support")

    async def request():
        transport = httpx.ASGITransport(app=web.panel.app, raise_app_exceptions=False)
        async with httpx.AsyncClient(transport=transport, base_url="http://panel.test") as client:
            return await client.request(method, url, headers={"Cookie": "panel_session=" + cookie}, follow_redirects=False)

    response = asyncio.run(request())
    return response.status_code, response.json()


# Case 14
def test_web_panel_block_routes_need_only_the_users_permission(web):
    assert _web_call(web, "POST", "/api/users/1001/block", 2) == (200, {"ok": True})
    assert web.main.get_user(BUYER)["is_blocked"] == 1
    assert _rows(web.main, "SELECT admin_id, action, record_type, record_id FROM admin_logs") == [(2, "user_block", "user", "1001")]
    assert _web_call(web, "POST", "/api/users/1002/block", 3) == (403, {"detail": NO_PERMISSION})
    assert web.main.get_user(REFERRER)["is_blocked"] == 0
    assert _web_call(web, "GET", "/api/web-admins", 2) == (403, {"detail": OWNER_ONLY})
    assert _web_call(web, "POST", "/api/users/1001/unblock", 2) == (200, {"ok": True})
    assert web.main.get_user(BUYER)["is_blocked"] == 0
    assert _web_call(web, "POST", "/api/users/4242/block", 1) == (200, {"ok": True})
    assert web.main.get_user(4242) is None
    assert _rows(web.main, "SELECT admin_id, action, record_type, record_id FROM admin_logs") == [
        (2, "user_block", "user", "1001"), (2, "user_unblock", "user", "1001"), (1, "user_block", "user", "4242")
    ]


# Case 15
def test_miniapp_refuses_blocked_topups_and_orders_but_not_test_claims(mini):
    server, main = mini.server, mini.main
    main.set_referred_by(BUYER, REFERRER)
    main.set_user_blocked(BUYER, True)
    main.add_wallet_credit(BUYER, 100_000)
    main.add_test_configs([TEST_LINK])
    pid = main.add_product(main.add_category("C"), "P", 100_000)
    main.add_configs(pid, [L1])
    token = SYNTHETIC_BOT_TOKEN
    assert _call(server, "POST", "/api/wallet/topup-request", token=token, tg_id=BUYER, json={"amount": 50_000}) == (403, {"detail": BLOCKED_MINI})
    assert _rows(main, "SELECT * FROM wallet_topups") == []
    assert _call(server, "POST", "/api/orders", token=token, tg_id=BUYER, json={"product_id": pid}) == (403, {"detail": BLOCKED_MINI})
    assert _rows(main, "SELECT * FROM orders") == []
    assert main.get_wallet_credit(BUYER) == 100_000 and main.count_available_configs(pid) == 1
    assert _call(server, "GET", "/api/test-config", token=token, tg_id=BUYER) == (200, {"enabled": True, "used": False, "available": 1, "link": None, "plans": []})
    assert _call(server, "POST", "/api/test-config/claim", token=token, tg_id=BUYER, json={}) == (200, {"link": TEST_LINK})
    assert tuple(main.get_user(BUYER)[k] for k in ("test_used", "referral_first_purchase_rewarded", "is_blocked")) == (1, 0, 1)
    assert _rows(main, "SELECT id, is_used, assigned_user_id FROM test_configs") == [(1, 1, BUYER)]
    assert main.get_wallet_credit(REFERRER) == 0
    assert _call(server, "GET", "/api/test-config", token=token, tg_id=BUYER) == (200, {"enabled": True, "used": True, "available": 0, "link": TEST_LINK, "plans": []})
    assert _call(server, "POST", "/api/test-config/claim", token=token, tg_id=BUYER, json={}) == (400, {"detail": ALREADY_TESTED_MINI})


# Case 16
def test_bot_test_handler_has_no_block_check_and_consumes_no_referral_flag(db):
    db.set_referred_by(BUYER, REFERRER)
    db.set_user_blocked(BUYER, True)
    db.add_test_configs([TEST_LINK])
    log = TelegramLog()
    handler = find_handler(handlers_user.create_user_router(db, is_main_bot=True), "message", "get_test_config")
    message = FakeMessage(log, BUYER, from_user=FakeUser(BUYER, "u1001", "U"), text=db.get_setting("btn_test"))
    asyncio.run(handler(message))
    assert [(e.kind, e.chat_id, e.text, e.parse_mode) for e in log.events] == [("message_answer", BUYER, TEST_LINK_TEXT, "Markdown")]
    assert tuple(db.get_user(BUYER)[k] for k in ("test_used", "referral_first_purchase_rewarded", "is_blocked")) == (1, 0, 1)
    assert _rows(db, "SELECT id, is_used, assigned_user_id FROM test_configs") == [(1, 1, BUYER)]
    assert db.get_wallet_credit(REFERRER) == 0


# Case 17
def test_blocked_users_still_earn_referral_rewards(db):
    db.set_referred_by(BUYER, REFERRER)
    db.set_user_blocked(BUYER, True)
    db.set_user_blocked(REFERRER, True)
    db.add_wallet_credit(BUYER, 7_000)
    assert db.reward_referrer_if_first_purchase(BUYER, 100_000) == (10_000, REFERRER)
    assert db.get_wallet_credit(REFERRER) == 10_000 and db.get_wallet_credit(BUYER) == 7_000
    db.set_setting("referral_invite_bonus_enabled", "1")
    db.set_setting("referral_invite_bonus_amount", "5000")
    db.set_referred_by(OTHER, REFERRER)
    assert db.apply_referral_invite_rewards(OTHER, REFERRER)["invite_bonus"] == 5000
    assert db.get_wallet_credit(REFERRER) == 15_000
