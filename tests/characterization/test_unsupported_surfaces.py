"""Characterize the unsupported customer surfaces at commit a80a80b.

Baseline: ``.venv/bin/python -m pytest tests/characterization/test_unsupported_surfaces.py --network=deny``.
Every database is a SQLite file under ``tmp_path``; no panel, payment service or Telegram is contacted.

Pins (FR-005; NG-01): (a) the Mini App serves the main store and every active reseller store whose Mini App is on, chosen by the `b` query value (cases 1–3); (b) initData must be signed with that store's bot token, but initData without `auth_date` never expires (cases 4, 5); (c) a purchase debits the wallet at once, before any payment, and a wallet-paid purchase hands out stock at once (cases 6, 7); (d) a reseller store sells its own catalog through the Mini App (case 9); (e) invoice and retrieval endpoints check the owning Telegram ID, and an automatic card-to-card invoice is issued although that mode is off (cases 10, 11).
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
from types import SimpleNamespace
from urllib.parse import urlencode

import httpx
import pytest
from fastapi import HTTPException

import config
import database
from tests._harness.legacy_bot import SYNTHETIC_BOT_TOKEN


OWNER = 9001
MAIN_TOKEN = SYNTHETIC_BOT_TOKEN
TENANT_TOKEN = "777001:tenant-synthetic"
L1, L2, L3 = "vless://a@x.invalid:443#1", "vless://b@x.invalid:443#2", "vless://c@x.invalid:443#3"
STORE_UNAVAILABLE = "این فروشگاه در دسترس نیست."
MINIAPP_OFF = "مینی\u200cاپ برای این نماینده فعال نیست."
DB_MISSING = "دیتابیس این فروشگاه در دسترس نیست."
DB_NOT_READY = "دیتابیس این فروشگاه هنوز آماده نیست."
BAD_INIT_DATA = "initData نامعتبر است."
BLOCKED = "حساب شما مسدود شده است."
NO_PRODUCT = "این محصول موجود نیست."
ORDER_NOT_FOUND = "سفارش یافت نشد."
ALREADY_REVIEWED = "این سفارش قبلاً بررسی شده است."
NO_CARD = "هیچ شماره کارتی برای دریافت وجه تعریف نشده است."
INVOICE_NOT_FOUND = "فاکتور یافت نشد."
DEFAULT_CARD_HOLDER = "نام صاحب حساب"
NOT_ENOUGH_STOCK_2 = "موجودی کافی نیست. فقط 2 عدد موجود است."


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


def _rows(db, sql, params=()):
    with db._get_conn() as conn:
        return [tuple(r) for r in conn.execute(sql, params)]


def _count(db, table):
    return _rows(db, f"SELECT COUNT(*) FROM {table}")[0][0]


def _shop(db, name, price, links):
    cat = db.add_category("C")
    pid = db.add_product(cat, name, price)
    db.add_configs(pid, links)
    return pid


def _reseller(main, rd):
    rd.mkdir(exist_ok=True)
    main.register_reseller_bot(TENANT_TOKEN, "r1bot", 5001, "R1", str(rd / "r1.db"))
    tenant = database.Database(str(rd / "r1.db"))
    tenant.init_db(5001)
    return tenant


def PENDING(order_id, final_price):
    return {
        "status": "pending_payment", "order_id": order_id, "final_price": final_price,
        "quantity": 1, "card_number": "0000-0000-0000-0000", "card_holder": DEFAULT_CARD_HOLDER,
        "card_to_card_enabled": True, "crypto_enabled": False, "abangateway_enabled": False,
        "blupal_enabled": False, "noapay_enabled": False, "card_to_card_auto_enabled": False,
        "extra_gateways": [],
    }


@pytest.fixture
def mini(monkeypatch, tmp_path_factory, tmp_path):
    server = _load_miniapp(tmp_path_factory.getbasetemp())
    main = database.Database(str(tmp_path / "main.db"))
    main.init_db(OWNER)
    monkeypatch.setattr(server, "main_db", main)
    alerts = []

    async def low_stock(send_fn, db, product_id):
        alerts.append((db.db_path, product_id))

    subs = []

    async def sub_info(link):
        subs.append(link)
        return {"ok": False, "marker": "synthetic"}

    monkeypatch.setattr(server, "check_and_notify_low_stock", low_stock)
    monkeypatch.setattr(server, "fetch_sub_info", sub_info)
    yield SimpleNamespace(server=server, main=main, alerts=alerts, subs=subs, rd=tmp_path / "reseller_dbs")
    main.close()


# --- miniapp/server.py (T029a) ---


# Case 1
def test_get_tenant_main_store_when_b_is_empty_or_zero(mini):
    m, s = mini.main, mini.server
    for value in ("", "0", "  "):
        tenant = s.get_tenant(value)
        assert tenant.db is m
        assert tenant.bot_token == MAIN_TOKEN
        assert tenant.tenant_id == ""


# Case 2
def test_get_tenant_resolves_reseller_by_id_or_slug(mini):
    m, s = mini.main, mini.server
    t = _reseller(m, mini.rd)
    try:
        x = s.get_tenant(" 1 ")
        assert (x.bot_token, x.tenant_id, x.db.db_path) == (TENANT_TOKEN, "1", str(mini.rd / "r1.db"))
        assert x.db is not m
        m.set_reseller_link_slug(1, "shop-one")
        y = s.get_tenant("shop-one")
        assert (y.bot_token, y.tenant_id, y.db.db_path) == (TENANT_TOKEN, "shop-one", str(mini.rd / "r1.db"))
        x.db.close()
        y.db.close()
    finally:
        t.close()


# Case 3
def test_get_tenant_refusals(mini):
    m, s = mini.main, mini.server

    def refusal(value, expected):
        with pytest.raises(HTTPException) as error:
            s.get_tenant(value)
        assert (error.value.status_code, error.value.detail) == expected

    refusal("9", (404, STORE_UNAVAILABLE))
    refusal("nope", (404, STORE_UNAVAILABLE))
    mini.rd.mkdir()
    m.register_reseller_bot(TENANT_TOKEN, "r1bot", 5001, "R1", str(mini.rd / "r1.db"))
    refusal("1", (503, DB_MISSING))
    db = database.Database(str(mini.rd / "r1.db"))
    db.init_db(5001)
    db.close()
    m.toggle_reseller_bot(1)
    refusal("1", (404, STORE_UNAVAILABLE))
    m.toggle_reseller_bot(1)
    m.set_reseller_miniapp_enabled(1, False)
    refusal("1", (404, MINIAPP_OFF))
    (mini.rd / "empty.db").write_bytes(b"")
    m.register_reseller_bot("777002:tenant-two-synthetic", "r2bot", 5002, "R2", str(mini.rd / "empty.db"))
    refusal("2", (503, DB_NOT_READY))


# Case 4
def test_init_data_must_be_signed_with_the_store_token(mini):
    m, s = mini.main, mini.server
    assert _call(s, "GET", "/api/orders")[0] == 422
    assert _call(s, "GET", "/api/orders", init_data="x=1&hash=00") == (401, {"detail": BAD_INIT_DATA})
    assert _call(s, "GET", "/api/orders", token=MAIN_TOKEN, tg_id=5101) == (200, [])
    old = _init_data(MAIN_TOKEN, 5101, int(time.time()) - 86401)
    assert _call(s, "GET", "/api/orders", init_data=old) == (401, {"detail": BAD_INIT_DATA})
    assert _call(s, "GET", "/api/orders", init_data=_init_data(MAIN_TOKEN, 5101, None)) == (200, [])
    tampered = _init_data(MAIN_TOKEN, 5101).replace("%22id%22%3A5101", "%22id%22%3A5102")
    assert _call(s, "GET", "/api/orders", init_data=tampered) == (401, {"detail": BAD_INIT_DATA})
    assert _rows(m, "SELECT telegram_id, username, first_name FROM users ORDER BY telegram_id") == [(5101, "u5101", "U")]


# Case 5
def test_init_data_is_checked_against_the_tenant_token(mini):
    m, s = mini.main, mini.server
    t = _reseller(m, mini.rd)
    try:
        assert _call(s, "GET", "/api/orders?b=1", token=MAIN_TOKEN, tg_id=6101) == (401, {"detail": BAD_INIT_DATA})
        assert _call(s, "GET", "/api/orders?b=1", token=TENANT_TOKEN, tg_id=6101) == (200, [])
        assert _call(s, "GET", "/api/orders", token=TENANT_TOKEN, tg_id=6101) == (401, {"detail": BAD_INIT_DATA})
        assert _rows(t, "SELECT telegram_id FROM users WHERE telegram_id=6101") == [(6101,)]
        assert _rows(m, "SELECT telegram_id FROM users WHERE telegram_id=6101") == []
    finally:
        t.close()


# Case 6
def test_purchase_debits_wallet_before_payment(mini):
    m, s = mini.main, mini.server
    pid = _shop(m, "P", 100000, [L1, L2])
    m.add_or_update_user(5101, "u5101", "U")
    m.add_wallet_credit(5101, 30000)
    assert _call(s, "POST", "/api/orders", token=MAIN_TOKEN, tg_id=5101, json={"product_id": pid}) == (200, PENDING(1, 70000))
    assert m.get_wallet_credit(5101) == 0
    assert _rows(m, "SELECT user_id, product_id, status, base_price, wallet_used, final_price FROM orders") == [(5101, pid, "pending", 100000, 30000, 70000)]
    assert m.count_available_configs(pid) == 2
    assert mini.alerts == []


# Case 7
def test_wallet_paid_purchase_hands_out_stock_at_once(mini):
    m, s = mini.main, mini.server
    pid = _shop(m, "P", 100000, [L1, L2, L3])
    m.add_or_update_user(5101, "u5101", "U")
    m.add_wallet_credit(5101, 100000)
    code, body = _call(s, "POST", "/api/orders", token=MAIN_TOKEN, tg_id=5101, json={"product_id": pid})
    exp = m.get_config_by_id(1)["expires_at"]
    assert exp is not None
    assert (code, body) == (200, {"status": "approved", "order_id": 1, "link": L1, "links": [L1], "expires_at": exp})
    assert m.get_wallet_credit(5101) == 0
    assert _rows(m, "SELECT status, wallet_used, final_price FROM orders") == [("approved", 100000, 0)]
    assert m.count_available_configs(pid) == 2
    assert mini.alerts == [(str(m.db_path), pid)]
    expected = [{"id": 1, "product_name": "P", "quantity": 1, "status": "approved", "final_price": 0, "expires_at": exp, "link": L1, "links": [L1], "config_ids": [1], "is_disabled": False, "is_custom_config": False}]
    assert _call(s, "GET", "/api/orders", token=MAIN_TOKEN, tg_id=5101) == (200, expected)
    assert _call(s, "GET", "/api/orders", token=MAIN_TOKEN, tg_id=5102) == (200, [])
    assert _call(s, "POST", "/api/orders/1/card-auto-invoice", token=MAIN_TOKEN, tg_id=5101) == (400, {"detail": ALREADY_REVIEWED})


# Case 8
def test_purchase_refusals_leave_no_trace(mini):
    m, s = mini.main, mini.server
    pid = _shop(m, "P", 100000, [L1, L2])
    m.add_or_update_user(5101, "u5101", "U")
    m.add_wallet_credit(5101, 30000)
    m.add_or_update_user(5103, "u5103", "U")
    m.set_user_blocked(5103, True)
    assert _call(s, "POST", "/api/orders", token=MAIN_TOKEN, tg_id=5103, json={"product_id": pid}) == (403, {"detail": BLOCKED})
    assert _call(s, "POST", "/api/orders", token=MAIN_TOKEN, tg_id=5101, json={"product_id": 99}) == (400, {"detail": NO_PRODUCT})
    assert _call(s, "POST", "/api/orders", token=MAIN_TOKEN, tg_id=5101, json={"product_id": pid, "quantity": 5}) == (400, {"detail": NOT_ENOUGH_STOCK_2})
    assert _count(m, "orders") == 0
    assert m.get_wallet_credit(5101) == 30000
    assert m.count_available_configs(pid) == 2


# Case 9
def test_reseller_store_sells_its_catalog_through_the_miniapp(mini):
    m, s = mini.main, mini.server
    t = _reseller(m, mini.rd)
    try:
        tpid = _shop(t, "TP", 50000, [L1])
        assert _call(s, "POST", "/api/orders?b=1", token=TENANT_TOKEN, tg_id=6101, json={"product_id": tpid}) == (200, PENDING(1, 50000))
        assert _rows(t, "SELECT user_id, product_id, status, final_price FROM orders") == [(6101, tpid, "pending", 50000)]
        assert _count(m, "orders") == 0
        code, body = _call(s, "GET", "/api/orders?b=1", token=TENANT_TOKEN, tg_id=6101)
        assert code == 200
        assert [o["product_name"] for o in body] == ["TP"]
        assert _call(s, "POST", "/api/orders/1/card-auto-invoice", token=MAIN_TOKEN, tg_id=6101) == (404, {"detail": ORDER_NOT_FOUND})
    finally:
        t.close()


# Case 10
def test_card_invoice_checks_owner_but_not_the_mode_setting(mini):
    m, s = mini.main, mini.server
    pid = _shop(m, "P", 100000, [L1, L2])
    assert _call(s, "POST", "/api/orders", token=MAIN_TOKEN, tg_id=5101, json={"product_id": pid}) == (200, PENDING(1, 100000))
    assert m.get_setting("card_to_card_auto_enabled", "0") == "0"
    assert _call(s, "POST", "/api/orders/1/card-auto-invoice", token=MAIN_TOKEN, tg_id=5102) == (404, {"detail": ORDER_NOT_FOUND})
    assert _call(s, "POST", "/api/orders/1/card-auto-invoice", token=MAIN_TOKEN, tg_id=5101) == (400, {"detail": NO_CARD})
    assert _count(m, "card_to_card_invoices") == 0
    m.create_card_to_card_card("0000111122223333", "Synthetic Holder", "Synthetic Bank")
    code, b1 = _call(s, "POST", "/api/orders/1/card-auto-invoice", token=MAIN_TOKEN, tg_id=5101)
    assert code == 200
    assert b1["invoice_id"] == 1
    assert b1["base_amount_toman"] == 100000
    assert 100100 <= b1["amount_toman"] <= 100999
    assert b1["amount_rial"] == b1["amount_toman"] * 10
    assert (b1["card_number"], b1["card_holder"], b1["bank_name"], b1["status"]) == ("0000111122223333", "Synthetic Holder", "Synthetic Bank", "pending")
    assert _call(s, "POST", "/api/orders/1/card-auto-invoice", token=MAIN_TOKEN, tg_id=5101) == (200, b1)
    assert _call(s, "GET", "/api/card-auto-invoice/1/status", token=MAIN_TOKEN, tg_id=5102) == (404, {"detail": INVOICE_NOT_FOUND})
    assert _call(s, "GET", "/api/card-auto-invoice/1/status", token=MAIN_TOKEN, tg_id=5101) == (200, {"status": "pending", "amount_toman": b1["amount_toman"]})
    assert _count(m, "card_to_card_invoices") == 1


# Case 11
def test_sub_info_only_for_the_callers_links(mini):
    m, s = mini.main, mini.server
    pid = _shop(m, "P", 100000, [L1, L2])
    m.add_or_update_user(5101, "u5101", "U")
    m.add_wallet_credit(5101, 100000)
    assert _call(s, "POST", "/api/orders", token=MAIN_TOKEN, tg_id=5101, json={"product_id": pid})[1]["status"] == "approved"
    sid = m.add_panel_server("P1", "3xui", "https://p1.example.invalid", "api-user", "synthetic-pass")
    m.add_custom_config(5101, sid, "cfg1", 10, 30, "https://sub.example.invalid/1")
    assert _call(s, "GET", "/api/sub-info", token=MAIN_TOKEN, tg_id=5101, params={"link": L1}) == (200, {"ok": False, "marker": "synthetic"})
    sub_url = "https://sub.example.invalid/1"
    assert _call(s, "GET", "/api/sub-info", token=MAIN_TOKEN, tg_id=5101, params={"link": sub_url}) == (200, {"ok": False, "marker": "synthetic"})
    assert _call(s, "GET", "/api/sub-info", token=MAIN_TOKEN, tg_id=5102, params={"link": L1}) == (403, {"detail": "forbidden"})
    assert _call(s, "GET", "/api/sub-info", token=MAIN_TOKEN, tg_id=5101, params={"link": L2}) == (403, {"detail": "forbidden"})
    assert mini.subs == [L1, sub_url]
