"""Characterize ``handlers_admin.cb_order_approve`` (1776–1974) and
``admin_only`` (214), through the real ``execute_renewal``,
``provision_direct`` and ``deliver_config_to_user``, at commit ``336c1c8``.
Reproduce with `.venv/bin/python -m pytest tests/characterization/test_order_approval.py --network=deny`.
Telegram, the VPN panel, and individual-link fetching are substitutes, not evidence.
reseller auto-provisioning (``provision_auto_config``) and the web panel (T015b)
are not covered here.

The baseline pins known unsafe behavior: claim, remote step, approval and log are
separate commits, so a crash leaves an order stuck in ``processing`` with a
config consumed (15) or approved but never delivered (16). An ambiguous panel
error releases the claim although the panel already applied the change, so a
custom retry is refused as a taken username (11), a direct retry leaves an
orphan and creates a second user (12), and a renewal retry adds volume twice on
the panel (13). An unexpected exception or inactive custom server keeps the
claim forever (10, 14). Delivery failures are swallowed and the admin is told
the config was sent (17). Any staff role, including ``support``, can approve
(5), and only the claim stops a concurrent double approval (8).
"""

import asyncio
import re
import sqlite3
import threading
from types import SimpleNamespace

import pytest

import config_delivery
import database
import direct_panel_provision
import handlers_admin
import renewal_engine
from panel_providers.base import PanelError, PanelUserResult, PanelUsernameTakenError
from tests._harness.crash import CrashPlan, SimulatedCrash
from tests._harness.legacy_bot import (
    FakeCallbackQuery, FakeMessage, FakeUser, RecordingBot, TelegramEvent,
    TelegramLog, find_handler,
)

OWNER = 9001
BUYER = 1001
SUPPORT = 4004
APPROVED_STOCK = '✅ خرید شما تایید شد!\n📦 محصول: Stock 30d'
APPROVED_DIRECT = '✅ خرید شما تایید شد!\n📦 محصول: Direct 50GB'
CUSTOM_BUILT = '✅ کانفیگ شخصی شما ساخته شد!'
RENEWED = '✅ سرویس شما با موفقیت تمدید شد.'
CAPTION_START = '🎉 با تشکر از خرید شما!'
LINK_STOCK_1 = '🔗 لینک اشتراک شما (برای کپی):\n`vless://stock-1`'
LINK_DIRECT = '🔗 لینک اشتراک شما (برای کپی):\n`https://sub.example.invalid/ali1`'
LINK_CUSTOM = '🔗 لینک اشتراک شما (برای کپی):\n`https://sub.example.invalid/alicustom`'
SUMMARY_100K = '💰 مبلغ کل پرداخت\u200cشده: 100,000 تومان'
SUMMARY_120K = '💰 مبلغ کل پرداخت\u200cشده: 120,000 تومان'
SUMMARY_80K = '💰 مبلغ کل پرداخت\u200cشده: 80,000 تومان'
DONE_SENT = '\n\n✅ تایید شد و کانفیگ ارسال شد.'
DONE_BUILT = '\n\n✅ تایید شد و کانفیگ ساخته شد.'
DONE_RENEWED = '\n\n✅ تایید شد و سرویس تمدید شد.'
ANSWER_STOCK = 'سفارش تایید و کانفیگ برای کاربر ارسال شد.'
ANSWER_DIRECT = 'سفارش تایید و کانفیگ به\u200cصورت خودکار ساخته شد.'
ANSWER_CUSTOM = 'سفارش تایید و کانفیگ شخصی روی پنل ساخته شد.'
ANSWER_RENEWED = 'سفارش تایید و سرویس تمدید شد.'
ADMIN_MENU = '🔧 پنل مدیریت:'
INVALID = '❌ درخواست نامعتبر است.'
NOT_FOUND = 'سفارش یافت نشد.'
ALREADY = 'این سفارش قبلاً بررسی شده است.'
PANEL_ERROR = '⛔\ufe0f خطا در ارتباط با پنل: synthetic timeout'
TAKEN = '⛔\ufe0f این نام کاربری روی پنل تکراری است؛ از کاربر بخواه نام دیگری انتخاب کند.'
PROVISION_ERROR = '⛔\ufe0f خطا در ساخت کانفیگ روی پنل: synthetic timeout'
RENEWAL_ERROR = '⛔\ufe0f تمدید ناموفق بود: synthetic timeout'
SERVER_INACTIVE = '⛔\ufe0f سرور پنل مربوطه یافت نشد یا غیرفعال است.'
SOLD_OUT = '⛔\ufe0f موجودی این محصول تمام شده! ابتدا لینک جدید اضافه کنید.'
LOG_STOCK = 'سفارش #1 | کاربر 1001 | محصول «Stock 30d» | مبلغ: 100,000'
LOG_DIRECT = 'سفارش #1 (خودکار) | کاربر 1001 | محصول «Direct 50GB» | مبلغ: 120,000'
LOG_CUSTOM = 'سفارش کانفیگ شخصی #1 | کاربر 1001 | یوزرنیم «alicustom» | 20 گیگ | مبلغ: 80,000'
LOG_RENEWAL = 'سفارش تمدید #1 | کاربر 1001 | مبلغ: 50,000'
RECEIPT_CAPTION = '🧾 سفارش #1'
CAPTION_STOCK = '┣ 🆔 شماره سفارش: #1\n┣ 📦 محصول: Stock 30d\n'
CAPTION_DIRECT = '┣ 🆔 شماره سفارش: #1\n┣ 📦 محصول: Direct 50GB\n'
CAPTION_CUSTOM = '┣ 🆔 شماره سفارش: #1\n┣ 📦 محصول: کانفیگ شخصی\n'


class FakePanel:
    """Synthetic VPN panel shared by every get_provider call. Substitute, not evidence."""
    def __init__(self) -> None:
        self.users: dict[str, int] = {}
        self.calls: list[tuple[str, str]] = []
        self.fail_after_apply: BaseException | None = None
        self.steps: list | None = None
        self.log: TelegramLog | None = None

    def _record(self, method, username):
        self.calls.append((method, username))
        if self.steps is not None:
            self.steps.append((f"panel.{method}", len(self.log.events)))

    def _fail(self):
        if self.fail_after_apply is not None:
            error, self.fail_after_apply = self.fail_after_apply, None
            raise error

    async def create_user(self, username, volume_gb, duration_days) -> PanelUserResult:
        self._record("create_user", username)
        if username in self.users:
            raise PanelUsernameTakenError(username)
        self.users[username] = volume_gb
        self._fail()
        return PanelUserResult(username, f"https://sub.example.invalid/{username}")

    async def update_user(self, username, add_volume_gb=0, add_days=0, reset_usage=False, preserve_remaining=False) -> None:
        self._record("update_user", username)
        self.users[username] += add_volume_gb
        self._fail()

    async def delete_user(self, username) -> None:
        self._record("delete_user", username)
        self.users.pop(username, None)


@pytest.fixture(autouse=True)
def remote(monkeypatch):
    panel = FakePanel()
    for module in (handlers_admin, renewal_engine, direct_panel_provision):
        monkeypatch.setattr(module, "get_provider", lambda server: panel)
    async def fetch_individual_links(link):
        return []

    monkeypatch.setattr(config_delivery, "fetch_individual_links", fetch_individual_links)
    async def forbidden(*args, **kwargs):
        pytest.fail("unexpected reseller provisioning")
    monkeypatch.setattr(handlers_admin, "provision_auto_config", forbidden)
    return panel


@pytest.fixture
def shop(tmp_path):
    db = database.Database(str(tmp_path / "main.db"))
    db.init_db(OWNER)
    db.add_or_update_user(BUYER, "ali", "Ali")
    category_id = db.add_category("VPN")
    stock_id = db.add_product(category_id, "Stock 30d", 100_000)
    db.add_configs(stock_id, [f"vless://stock-{i}" for i in range(1, 6)])
    server_id = db.add_panel_server("Panel A", "pasarguard", "https://panel.example.invalid", "synthetic-user", "synthetic-pass")
    db.add_product(category_id, "Direct 50GB", 120_000, is_auto_provision=True, auto_provision_volume_gb=50, provision_server_id=server_id)
    handler = find_handler(handlers_admin.create_admin_router(db, is_main_bot=True), "callback_query", "cb_order_approve")
    return SimpleNamespace(db=db, db_path=tmp_path / "main.db", category_id=category_id, server_id=server_id, handler=handler)


def stock_order(shop):
    return shop.db.create_order(BUYER, 1, 100_000)


def direct_order(shop):
    return shop.db.create_order(BUYER, 2, 120_000, config_name="ali1")


def custom_order(shop, server_id=None):
    return shop.db.create_custom_config_order(BUYER, 20, "alicustom", server_id or shop.server_id, 80_000, custom_duration_days=30)


def renewal_order(shop, panel):
    config_id = shop.db.add_custom_config(BUYER, shop.server_id, "ren1", 30, 30, "https://sub.example.invalid/ren1")
    panel.users["ren1"] = 30
    return shop.db.create_renewal_order(BUYER, "custom", config_id, "volume", 10, 0, 50_000)


async def approve(shop, log, bot, who=OWNER, data="order_approve:1", expect=None):
    message = FakeMessage(log, who, caption=RECEIPT_CAPTION)
    result = await shop.handler(FakeCallbackQuery(log, FakeUser(who), data, message), bot)
    assert result is expect
    return message


def track(monkeypatch, db, panel, log):
    steps = []
    methods = ("claim_order", "release_order_claim", "take_unused_configs", "approve_order", "approve_order_auto", "approve_custom_config_order", "approve_renewal_order", "add_custom_config", "apply_custom_config_renewal", "log_admin_action", "reward_referrer_if_first_purchase")
    for name in methods:
        real = getattr(db, name)
        def wrapper(*args, _name=name, _real=real, **kwargs):
            steps.append((_name, len(log.events)))
            return _real(*args, **kwargs)
        monkeypatch.setattr(db, name, wrapper)
    panel.steps, panel.log = steps, log
    return steps


def names(steps):
    return [name for name, _ in steps]


def hold_first_two(monkeypatch, db, name):
    real = getattr(db, name)
    barrier = threading.Barrier(2, timeout=5)
    lock, count = threading.Lock(), 0
    def held(*args, **kwargs):
        nonlocal count
        with lock:
            count += 1
            wait = count <= 2
        if wait:
            barrier.wait()
        return real(*args, **kwargs)
    monkeypatch.setattr(db, name, held)


def order_row(shop):
    with sqlite3.connect(shop.db_path) as conn:
        conn.row_factory = sqlite3.Row
        return dict(conn.execute("SELECT * FROM orders WHERE id=1").fetchone())


def configs(shop):
    with sqlite3.connect(shop.db_path) as conn:
        return conn.execute("SELECT id,is_used,assigned_user_id,order_id FROM configs ORDER BY id").fetchall()


def custom_configs(shop):
    with sqlite3.connect(shop.db_path) as conn:
        return conn.execute("SELECT user_id,panel_server_id,username,volume_gb,order_id,source FROM custom_configs ORDER BY id").fetchall()


def renewal_volume(shop):
    with sqlite3.connect(shop.db_path) as conn:
        return conn.execute(
            "SELECT volume_gb FROM custom_configs WHERE id=1"
        ).fetchone()[0]


def admin_logs(shop):
    with sqlite3.connect(shop.db_path) as conn:
        return conn.execute("SELECT admin_id,action,details,record_type,record_id FROM admin_logs ORDER BY id").fetchall()


def user_events(log):
    return log.select(chat_id=BUYER)


def answers(log):
    return log.select(kind="callback_answer")


def delivered(log, text, caption, link, summary):
    events = user_events(log)
    assert [e.kind for e in events] == ["send_message", "send_photo", "send_message", "send_message"]
    assert events[0].text == text
    assert events[1].text.startswith(CAPTION_START) and caption in events[1].text
    assert events[2].text == link and events[2].parse_mode == "Markdown"
    assert events[3].text == summary


def closes(log, message, done, answer):
    edit, response, menu = log.events[-3:]
    assert edit == TelegramEvent(
        "edit_caption", message.chat.id, message.message_id, RECEIPT_CAPTION + done
    )
    assert response == TelegramEvent("callback_answer", None, None, answer)
    assert menu.kind == "send_message"
    assert menu.chat_id == message.chat.id
    assert menu.text == ADMIN_MENU
    assert menu.reply_markup is not None


def alert(log, text):
    assert log.events == [TelegramEvent("callback_answer", None, None, text, show_alert=True)]


def test_stock_approval_claims_allocates_approves_then_delivers(shop, remote, monkeypatch):
    stock_order(shop)
    log = TelegramLog()
    bot = RecordingBot(log)
    steps = track(monkeypatch, shop.db, remote, log)
    message = asyncio.run(approve(shop, log, bot))
    assert steps == [("claim_order", 0), ("take_unused_configs", 0), ("approve_order", 0), ("log_admin_action", 0), ("reward_referrer_if_first_purchase", 0)]
    assert log.trace() == [("send_message", 1001), ("send_photo", 1001), ("send_message", 1001), ("send_message", 1001), ("edit_caption", 9001), ("callback_answer", None), ("send_message", 9001)]
    delivered(log, APPROVED_STOCK, CAPTION_STOCK, LINK_STOCK_1, SUMMARY_100K)
    closes(log, message, DONE_SENT, ANSWER_STOCK)
    assert order_row(shop)["status"] == "approved" and order_row(shop)["config_id"] == 1
    assert configs(shop) == [(1, 1, 1001, 1), (2, 0, None, None), (3, 0, None, None), (4, 0, None, None), (5, 0, None, None)]
    assert admin_logs(shop) == [(9001, "order_approve", LOG_STOCK, None, None)]


def test_direct_approval_creates_on_panel_before_approving(shop, remote, monkeypatch):
    direct_order(shop)
    log = TelegramLog()
    bot = RecordingBot(log)
    steps = track(monkeypatch, shop.db, remote, log)
    message = asyncio.run(approve(shop, log, bot))
    assert steps == [
        ("claim_order", 0),
        ("panel.create_user", 0),
        ("add_custom_config", 0),
        ("approve_order_auto", 0),
        ("log_admin_action", 0),
    ]
    assert log.trace() == [
        ("send_message", 1001),
        ("send_photo", 1001),
        ("send_message", 1001),
        ("send_message", 1001),
        ("edit_caption", 9001),
        ("callback_answer", None),
        ("send_message", 9001),
    ]
    delivered(log, APPROVED_DIRECT, CAPTION_DIRECT, LINK_DIRECT, SUMMARY_120K)
    closes(log, message, DONE_BUILT, ANSWER_DIRECT)
    assert remote.users == {"ali1": 50}
    assert custom_configs(shop) == [(1001, 1, "ali1", 50, 1, "direct_product")]
    assert order_row(shop)["status"] == "approved"
    assert order_row(shop)["config_id"] is None
    assert admin_logs(shop) == [(9001, "order_approve", LOG_DIRECT, None, None)]


def test_custom_config_approval_creates_on_panel_before_approving(shop, remote, monkeypatch):
    custom_order(shop)
    log = TelegramLog()
    bot = RecordingBot(log)
    steps = track(monkeypatch, shop.db, remote, log)
    message = asyncio.run(approve(shop, log, bot))
    assert steps == [
        ("claim_order", 0),
        ("panel.create_user", 0),
        ("approve_custom_config_order", 0),
        ("add_custom_config", 0),
        ("log_admin_action", 0),
    ]
    assert log.trace() == [
        ("send_message", 1001),
        ("send_photo", 1001),
        ("send_message", 1001),
        ("send_message", 1001),
        ("edit_caption", 9001),
        ("callback_answer", None),
        ("send_message", 9001),
    ]
    delivered(log, CUSTOM_BUILT, CAPTION_CUSTOM, LINK_CUSTOM, SUMMARY_80K)
    closes(log, message, DONE_BUILT, ANSWER_CUSTOM)
    assert custom_configs(shop) == [(1001, 1, "alicustom", 20, 1, "custom_config")]
    assert admin_logs(shop) == [(9001, "custom_config_approve", LOG_CUSTOM, None, None)]


def test_renewal_approval_updates_panel_before_approving(shop, remote, monkeypatch):
    renewal_order(shop, remote)
    log = TelegramLog()
    bot = RecordingBot(log)
    steps = track(monkeypatch, shop.db, remote, log)
    message = asyncio.run(approve(shop, log, bot))
    assert steps == [
        ("claim_order", 0),
        ("panel.update_user", 0),
        ("apply_custom_config_renewal", 0),
        ("approve_renewal_order", 0),
        ("log_admin_action", 0),
    ]
    assert log.trace() == [
        ("send_message", 1001),
        ("edit_caption", 9001),
        ("callback_answer", None),
        ("send_message", 9001),
    ]
    assert user_events(log)[0].text == RENEWED
    closes(log, message, DONE_RENEWED, ANSWER_RENEWED)
    assert remote.users["ren1"] == 40
    assert renewal_volume(shop) == 40
    assert order_row(shop)["status"] == "approved"
    assert admin_logs(shop) == [(9001, "renewal_approve", LOG_RENEWAL, None, None)]


def test_support_staff_can_approve(shop):
    shop.db.add_admin(SUPPORT, "support")
    assert shop.db.is_full_admin(SUPPORT) is False
    stock_order(shop)
    log = TelegramLog()
    message = asyncio.run(approve(shop, log, RecordingBot(log), who=SUPPORT))
    assert order_row(shop)["status"] == "approved"
    assert log.trace() == [
        ("send_message", 1001),
        ("send_photo", 1001),
        ("send_message", 1001),
        ("send_message", 1001),
        ("edit_caption", 4004),
        ("callback_answer", None),
        ("send_message", 4004),
    ]
    assert admin_logs(shop) == [(4004, "order_approve", LOG_STOCK, None, None)]


def test_non_staff_callback_is_ignored(shop, remote, monkeypatch):
    stock_order(shop)
    log = TelegramLog()
    steps = track(monkeypatch, shop.db, remote, log)
    asyncio.run(approve(shop, log, RecordingBot(log), who=BUYER, expect=True))
    assert log.events == [TelegramEvent("callback_answer", None, None, None)]
    assert steps == []
    assert order_row(shop)["status"] == "pending"


def test_invalid_missing_and_claimed_orders_are_refused(shop, remote, monkeypatch):
    stock_order(shop)
    shop.db.claim_order(1)
    log = TelegramLog()
    steps = track(monkeypatch, shop.db, remote, log)
    bot = RecordingBot(log)
    cases = [
        ("order_approve:abc", INVALID),
        ("order_approve:99", NOT_FOUND),
        ("order_approve:1", ALREADY),
    ]
    for data, expected in cases:
        if log.events:
            log.events.clear()
        asyncio.run(approve(shop, log, bot, data=data))
        alert(log, expected)
    assert steps == []
    assert order_row(shop)["status"] == "processing"
    assert all(row[1] == 0 for row in configs(shop))


def test_concurrent_approvals_settle_once(shop, monkeypatch, remote):
    shop.db.add_admin(SUPPORT, "support")
    stock_order(shop)
    log = TelegramLog()
    bot = RecordingBot(log)
    steps = track(monkeypatch, shop.db, remote, log)
    hold_first_two(monkeypatch, shop.db, "get_order")

    async def scenario():
        return await asyncio.gather(
            approve(shop, log, bot, who=OWNER),
            approve(shop, log, bot, who=SUPPORT),
        )

    asyncio.run(scenario())
    assert order_row(shop)["status"] == "approved"
    assert configs(shop) == [(1, 1, 1001, 1), (2, 0, None, None), (3, 0, None, None), (4, 0, None, None), (5, 0, None, None)]
    assert len(admin_logs(shop)) == 1
    assert admin_logs(shop)[0][1] == "order_approve"
    assert admin_logs(shop)[0][0] in {OWNER, SUPPORT}
    assert sorted(e.text for e in answers(log)) == sorted([ALREADY, ANSWER_STOCK])
    assert [e for e in answers(log) if e.text == ALREADY][0].show_alert is True
    assert len([e for e in user_events(log) if e.text == APPROVED_STOCK]) == 1
    assert names(steps).count("claim_order") == 2
    assert names(steps).count("take_unused_configs") == 1
    assert names(steps).count("approve_order") == 1


def test_sold_out_releases_claim(shop, monkeypatch, remote):
    product_id = shop.db.add_product(shop.category_id, "Empty", 10_000)
    shop.db.create_order(BUYER, product_id, 10_000)
    log = TelegramLog()
    steps = track(monkeypatch, shop.db, remote, log)
    asyncio.run(approve(shop, log, RecordingBot(log)))
    alert(log, SOLD_OUT)
    assert names(steps) == ["claim_order", "take_unused_configs", "release_order_claim"]
    assert order_row(shop)["status"] == "pending"


def test_inactive_custom_server_keeps_claim(shop, monkeypatch, remote):
    server_id = shop.db.add_panel_server("Panel B", "pasarguard", "https://panel-b.example.invalid", "synthetic-user", "synthetic-pass")
    shop.db.update_panel_server(server_id, is_active=0)
    custom_order(shop, server_id=server_id)
    log = TelegramLog()
    steps = track(monkeypatch, shop.db, remote, log)
    bot = RecordingBot(log)
    asyncio.run(approve(shop, log, bot))
    alert(log, SERVER_INACTIVE)
    assert names(steps) == ["claim_order"]
    assert remote.calls == []
    assert order_row(shop)["status"] == "processing"
    log.events.clear()
    asyncio.run(approve(shop, log, bot))
    alert(log, ALREADY)


def test_ambiguous_custom_error_releases_claim_and_blocks_retry(shop, monkeypatch, remote):
    custom_order(shop)
    remote.fail_after_apply = PanelError("synthetic timeout")
    log = TelegramLog()
    steps = track(monkeypatch, shop.db, remote, log)
    bot = RecordingBot(log)
    asyncio.run(approve(shop, log, bot))
    alert(log, PANEL_ERROR)
    assert names(steps) == ["claim_order", "panel.create_user", "release_order_claim"]
    assert order_row(shop)["status"] == "pending"
    assert remote.users == {"alicustom": 20}
    assert custom_configs(shop) == []
    log.events.clear()
    asyncio.run(approve(shop, log, bot))
    alert(log, TAKEN)
    assert order_row(shop)["status"] == "pending"
    assert remote.users == {"alicustom": 20}
    assert custom_configs(shop) == []


def test_ambiguous_direct_error_leaves_orphan_and_retry_creates_another(shop, remote):
    direct_order(shop)
    remote.fail_after_apply = PanelError("synthetic timeout")
    log = TelegramLog()
    bot = RecordingBot(log)
    asyncio.run(approve(shop, log, bot))
    alert(log, PROVISION_ERROR)
    assert order_row(shop)["status"] == "pending"
    assert remote.calls == [("create_user", "ali1")]
    assert custom_configs(shop) == []
    log.events.clear()
    asyncio.run(approve(shop, log, bot))
    assert order_row(shop)["status"] == "approved"
    new = remote.calls[2][1]
    assert remote.calls[1:] == [("create_user", "ali1"), ("create_user", new)]
    assert re.fullmatch(r"ali1_[a-z0-9]{3}", new)
    assert set(remote.users) == {"ali1", new}
    assert custom_configs(shop) == [(1001, 1, new, 50, 1, "direct_product")]
    assert [e.text for e in user_events(log) if e.kind == "send_message" and e.text and e.text.startswith("🔗")] == [f"🔗 لینک اشتراک شما (برای کپی):\n`https://sub.example.invalid/{new}`"]


def test_ambiguous_renewal_error_applies_twice_on_retry(shop, remote):
    renewal_order(shop, remote)
    remote.fail_after_apply = PanelError("synthetic timeout")
    log = TelegramLog()
    bot = RecordingBot(log)
    asyncio.run(approve(shop, log, bot))
    alert(log, RENEWAL_ERROR)
    assert order_row(shop)["status"] == "pending"
    assert remote.users["ren1"] == 40
    assert renewal_volume(shop) == 30
    log.events.clear()
    asyncio.run(approve(shop, log, bot))
    assert order_row(shop)["status"] == "approved"
    assert remote.users["ren1"] == 50
    assert renewal_volume(shop) == 40
    assert user_events(log)[0].text == RENEWED
    assert admin_logs(shop) == [(9001, "renewal_approve", LOG_RENEWAL, None, None)]


@pytest.mark.parametrize("kind", ["direct", "custom", "renewal"])
def test_unexpected_error_keeps_claim(shop, remote, kind):
    if kind == "direct":
        direct_order(shop)
    elif kind == "custom":
        custom_order(shop)
    else:
        renewal_order(shop, remote)
    remote.fail_after_apply = RuntimeError("synthetic")
    log = TelegramLog()
    bot = RecordingBot(log)
    with pytest.raises(RuntimeError, match="synthetic"):
        asyncio.run(approve(shop, log, bot))
    assert order_row(shop)["status"] == "processing"
    assert log.events == []
    asyncio.run(approve(shop, log, bot))
    alert(log, ALREADY)


def test_crash_between_allocation_and_approval(shop, monkeypatch):
    stock_order(shop)
    log = TelegramLog()
    bot = RecordingBot(log)
    plan = CrashPlan().arm("before approve_order")
    real = shop.db.approve_order

    def crash_before_approval(*args, **kwargs):
        plan("before approve_order")
        return real(*args, **kwargs)

    monkeypatch.setattr(shop.db, "approve_order", crash_before_approval)
    with pytest.raises(SimulatedCrash):
        asyncio.run(approve(shop, log, bot))
    assert order_row(shop)["status"] == "processing"
    assert order_row(shop)["config_id"] is None
    assert configs(shop)[0] == (1, 1, 1001, None)
    assert log.events == []
    assert admin_logs(shop) == []
    monkeypatch.setattr(shop.db, "approve_order", real)
    asyncio.run(approve(shop, log, bot))
    alert(log, ALREADY)
    assert configs(shop)[1:] == [(2, 0, None, None), (3, 0, None, None), (4, 0, None, None), (5, 0, None, None)]


def test_crash_after_approval_before_delivery(shop, monkeypatch):
    stock_order(shop)
    log = TelegramLog()
    bot = RecordingBot(log)
    plan = CrashPlan().arm("user notice")

    async def crash_on_notice(chat_id, text, **kwargs):
        plan("user notice")

    monkeypatch.setattr(bot, "send_message", crash_on_notice)
    with pytest.raises(SimulatedCrash):
        asyncio.run(approve(shop, log, bot))
    assert order_row(shop)["status"] == "approved"
    assert configs(shop)[0] == (1, 1, 1001, 1)
    assert log.events == []
    assert len(admin_logs(shop)) == 1
    asyncio.run(approve(shop, log, RecordingBot(log)))
    alert(log, ALREADY)
    assert user_events(log) == []


def test_blocked_buyer_order_is_still_approved_and_reported_sent(shop):
    stock_order(shop)
    log = TelegramLog()
    message = asyncio.run(approve(shop, log, RecordingBot(log, blocked_chat_ids={BUYER})))
    assert order_row(shop)["status"] == "approved"
    assert log.trace() == [("send_message", 1001), ("edit_caption", 9001), ("callback_answer", None), ("send_message", 9001)]
    assert log.events[0].delivered is False
    assert log.events[0].text == APPROVED_STOCK
    closes(log, message, DONE_SENT, ANSWER_STOCK)
