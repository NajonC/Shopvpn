"""Characterize the legacy payment verification helpers at commit b1390ac.

Baseline: ``.venv/bin/python -m pytest tests/characterization/test_payment_methods_legacy.py --network=deny``.
All inputs are synthetic and the helpers are called directly (no provider, no database). The settings database and the live USD rate are stubs (substitute, not evidence). Aban cases fake only the gateway client calls (and, where stated, provisioning or renewal); delivery runs against a recording bot. Tetra98, CubePay and NOWPayments cases replace only the HTTP call (``extra_gateway_clients._request``) with scripted replies.
Card-to-card cases use a real SQLite database under tmp_path and a scripted random source.
These are E-005 source leads, not method certification; composite payments must not use these helpers as authority (FR-011).

Known unsafe behaviour (payment_engine.py): (a) ``amounts_match`` accepts when the paid amount is missing or unparseable, or the expected amount is unparseable or not positive (cases 1–3, 8); (b) it has only a lower bound, so any overpayment, ``"inf"`` and a Rial amount for a Toman invoice pass (cases 5, 8); (c) a 1 % shortfall passes by default, and a tolerance of 100 accepts zero (cases 4, 7); (d) it never checks currency or unit (case 8); (e) webhook authentication defaults to mode ``none``, which accepts any request even when a secret is configured (cases 9, 10); (f) without ``amount_path`` a parsed webhook carries no amount, so the amount check passes (case 15).

Known unsafe behaviour (custom_gateway_payment.py): (g) the amount sent to the gateway is converted (×10 for Rial, a stored or live USD rate for USD) and multiplied, but the legacy amount check compares the gateway's reported amount with the unconverted Toman price, so a gateway that reports exactly what it was asked to can fail, and a Rial figure passes (case 24); (h) a missing, non-numeric, zero or negative multiplier silently becomes 1 (case 17); (i) an unknown currency, including ``"IRR"``, is silently sent as Toman (case 19); (j) USD amounts are rounded twice, before and after the multiplier, and the 1-dollar minimum is checked before the multiplier (cases 21, 22).

Known unsafe behaviour (card_to_card_payment.py): (k) the customer pays the base price plus a random offset of 100–999 Toman (1000–9999 on the last ten attempts), and the offset is kept (cases 29, 31); (l) an existing pending invoice is returned for the same order whatever the user, price or deadline (case 30); (m) ``normalize_amount`` deletes every non-digit, so decimals, signs and any other digits in the text are joined into one number (case 26); (n) the Rial-to-Toman conversion floors, and any unit other than ``rial`` counts as Toman (case 27); (o) an SMS is matched by amount alone, with no card, sender, user or order check (case 33); (p) once an invoice expires its amount is free again, so a late SMS for it completes another customer's invoice (case 35); (q) completion has no pending-status condition, so two overlapping matches of one SMS both return the invoice as completed (case 36).

Known unsafe behaviour (abangateway_payment.py): (r) verification trusts the gateway's status alone and never compares the paid amount with the invoice (case 42); (s) the invoice is marked completed before anything is delivered, so after a crash between verification and delivery every retry answers "already delivered" and the order is never fulfilled (case 44); (t) a locally expired invoice that the gateway reports paid is still verified (case 46); (u) ``finalize_paid_order`` takes only an order id and delivers any pending order with no invoice or payment check (case 48); (v) when delivery fails after payment (stock exhausted, provisioning, renewal or a missing server), the order silently returns to pending with no refund or record of the payment (cases 50–53).

Known unsafe behaviour (extra_gateway_clients.py): (w) Tetra98 verification trusts status 100 alone, with no amount or order check, and no reply short of a server error ever counts as failed (case 56); (x) CubePay's one fee setting is a percentage up to 100 and a fixed Toman amount above it, so 100 doubles the price and 101 adds 101 Toman (case 57); (y) CubePay verification checks the order and amount only when the reply includes them, ignores an unparseable amount, accepts any overpayment and treats HTTP 409 as paid (case 61); (z) NOWPayments classification compares the quoted ``price_amount``, not what was actually paid, accepts a shortfall under one cent and any overpayment, and an expected price of 0 accepts any finished payment (case 64).

A later section (T023f) characterizes ``extra_gateway_payment.process_stars_payment``.
"""

import asyncio
import hashlib
import hmac
import json
import logging
import sqlite3
from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest

import crypto_payment
import card_to_card_payment
import abangateway_client
import abangateway_payment
import database
import exchange_rate
import extra_gateway_clients
import payment_engine
from card_to_card_payment import CardToCardError, create_invoice, match_and_complete, normalize_amount, rial_to_toman
from abangateway_payment import finalize_paid_order, rial_to_toman as aban_rial_to_toman, toman_to_rial, try_verify_and_finalize
from custom_gateway_payment import CustomGatewayPaymentError, compute_send_amount
from direct_panel_provision import ProvisionError as DirectProvisionError
from payment_engine import GenericGateway, amounts_match
from extra_gateway_clients import GatewayError, cubepay_create, cubepay_payable_toman, cubepay_verify, nowpayments_classify, nowpayments_create_invoice, nowpayments_payment_status, nowpayments_verify_ipn_signature, tetra98_create, tetra98_verify
from renewal_engine import RenewalError
from tests._harness.legacy_bot import RecordingBot, TelegramLog


EXPECTED = 100_000
SECRET = "synthetic-webhook-secret"
BODY = b'{"txn_id":"T-1","status":"paid","amount":"100000"}'
OWNER = 9001
BUYER = 1001
OTHER_BUYER = 1002
CARD_1 = "6037-0000-0000-0001"
CARD_2 = "6037-0000-0000-0002"
NO_CARD = "هیچ شماره کارتی برای دریافت وجه تعریف نشده است."
NO_UNIQUE_AMOUNT = "امکان رزرو مبلغ یکتا وجود نداشت، لطفاً چند لحظه دیگر دوباره تلاش کنید."
ABAN_KEY = "synthetic-aban-key"
NO_ORDER = "⚠️ سفارش یافت نشد."
ALREADY_HANDLED = "✅ این سفارش قبلاً بررسی و تحویل داده شده است."
DELIVERED = "✅ پرداخت تایید شد و کانفیگ تحویل داده شد."
NO_ABAN_KEY = "error:کلید API آبان گیت وی تنظیم نشده است."
TETRA_KEY = "synthetic-tetra-key"
CUBE_TOKEN = "synthetic-cube-token"
NP_KEY = "synthetic-np-key"
NP_SECRET = "synthetic-ipn-secret"
CALLBACK = "https://bot.example.invalid/callback"
CUBE_HEADERS = {"Authorization": "Bearer synthetic-cube-token", "Content-Type": "application/json"}
TETRA_REFUSED_200 = "تترا۹۸: synthetic refusal (HTTP 200)."
TETRA_CREATE_FAILED_502 = "تترا۹۸: خطا در ساخت سفارش (HTTP 502)."
TETRA_CREATE_FAILED_200 = "تترا۹۸: خطا در ساخت سفارش (HTTP 200)."
TETRA_SERVER_500 = "تترا۹۸: خطای سرور (HTTP 500)."
CUBE_NO_LINK = "کیوب\u200cپی: لینک پرداخت در پاسخ نبود."
CUBE_REFUSED_400 = "کیوب\u200cپی: synthetic refusal (HTTP 400)."
CUBE_CREATE_FAILED_200 = "کیوب\u200cپی: خطا در ساخت تراکنش (HTTP 200)."
CUBE_ORDER_MISMATCH = "کیوب\u200cپی: شناسه\u200cی سفارش در پاسخ تایید با فاکتور مطابقت ندارد."
CUBE_SHORT = "کیوب\u200cپی: مبلغ پرداخت\u200cشده کمتر از مبلغ فاکتور است."
CUBE_SERVER_500 = "کیوب\u200cپی: خطای سرور (HTTP 500)."
CUBE_SERVER_503 = "کیوب\u200cپی: خطای سرور (HTTP 503)."
NP_REFUSED_400 = "NowPayments: synthetic refusal (HTTP 400)."
NP_CREATE_FAILED_200 = "NowPayments: خطا در ساخت فاکتور (HTTP 200)."
NP_STATUS_404 = "NowPayments: خطا در دریافت وضعیت پرداخت (HTTP 404)."
NP_STATUS_201 = "NowPayments: خطا در دریافت وضعیت پرداخت (HTTP 201)."
IPN_BODY = {"payment_status": "finished", "order_id": "ORD-3", "invoice_id": 5077, "price_amount": 2.35, "order_description": "اشتراک", "fee": {"depositFee": 0, "currency": "usdttrc20"}}
IPN_CANONICAL = '{"fee":{"currency":"usdttrc20","depositFee":0},"invoice_id":5077,"order_description":"اشتراک","order_id":"ORD-3","payment_status":"finished","price_amount":2.35}'
NP_PAYMENT = {"invoice_id": 5077, "order_id": "ORD-3", "payment_status": "finished", "price_amount": 2.35}


class FakeAban:
    """Stand-in for abangateway_client.get_invoice and verify_invoice; records calls."""

    def __init__(self):
        self.status = "pending"
        self.get_error = None
        self.verify_error = None
        self.calls = []

    async def get_invoice(self, api_key, invoice_id):
        self.calls.append(("get", api_key, invoice_id))
        if self.get_error is not None:
            raise self.get_error
        return {"invoice_id": invoice_id, "status": self.status, "amount_rial": 1, "payable_rial": 1}

    async def verify_invoice(self, api_key, invoice_id):
        self.calls.append(("verify", api_key, invoice_id))
        if self.verify_error is not None:
            raise self.verify_error
        return {"invoice_id": invoice_id, "status": "paid"}


@pytest.fixture
def aban(tmp_path, monkeypatch):
    db_path = str(tmp_path / "main.db")
    db = database.Database(db_path)
    db.init_db(OWNER)
    db.add_or_update_user(BUYER, "ali", "Ali")
    db.set_setting("abangateway_api_key", ABAN_KEY)
    monkeypatch.setattr(abangateway_payment, "ABANGATEWAY_API_KEY", "")
    remote = FakeAban()
    monkeypatch.setattr(abangateway_client, "get_invoice", remote.get_invoice)
    monkeypatch.setattr(abangateway_client, "verify_invoice", remote.verify_invoice)
    category_id = db.add_category("VPN")
    product_id = db.add_product(category_id, "Stock 30d", 100_000)
    db.add_configs(product_id, ["vless://stock-1", "vless://stock-2"])
    log = TelegramLog()
    return SimpleNamespace(db=db, db_path=db_path, remote=remote, category_id=category_id, product_id=product_id, log=log, bot=RecordingBot(log))


def aban_invoice(aban, invoice_id, order_id, status="new"):
    aban.db.create_abangateway_invoice(invoice_id, "order", order_id, BUYER, 100_000, 1_000_000, payable_rial=1_000_090, payment_url=f"https://pay.example.invalid/{invoice_id}")
    if status != "new":
        aban.db.update_abangateway_invoice_status(invoice_id, status)


def local_status(aban, invoice_id):
    return aban.db.get_abangateway_invoice_by_invoice_id(invoice_id)["status"]


def check(aban, invoice_id):
    return asyncio.run(try_verify_and_finalize(aban.db, aban.db.get_abangateway_invoice_by_invoice_id(invoice_id)))


def deliver(aban, order_id, notify=None):
    return asyncio.run(finalize_paid_order(aban.db, aban.bot, order_id, notify_admins_fn=notify))


def order_status(aban, order_id):
    return aban.db.get_order(order_id)["status"]


def stock_rows(aban):
    conn = sqlite3.connect(aban.db_path)
    try:
        return conn.execute("SELECT id, is_used, assigned_user_id, order_id FROM configs ORDER BY id").fetchall()
    finally:
        conn.close()


class FakeHttp:
    """Stand-in for extra_gateway_clients._request: records calls, replays scripted (status, data) replies."""

    def __init__(self):
        self.replies = []
        self.calls = []

    async def request(self, method, url, headers=None, json_body=None, timeout=25):
        self.calls.append((method, url, headers, json_body))
        return self.replies.pop(0)


@pytest.fixture
def http(monkeypatch):
    fake = FakeHttp()
    monkeypatch.setattr(extra_gateway_clients, "_request", fake.request)
    return fake


def gateway_error(coro):
    with pytest.raises(GatewayError) as exc:
        asyncio.run(coro)
    return str(exc.value)


def sign(secret, text, digest=hashlib.sha512):
    return hmac.new(secret.encode("utf-8"), text.encode("utf-8"), digest).hexdigest()


class ScriptedRandom:
    """Stand-in for the random module: records randint ranges, returns scripted offsets."""

    def __init__(self, *offsets):
        self.offsets = list(offsets)
        self.calls = []

    def randint(self, lo, hi):
        self.calls.append((lo, hi))
        if len(self.offsets) > 1:
            return self.offsets.pop(0)
        return self.offsets[0]


@pytest.fixture
def cards(tmp_path):
    db_path = str(tmp_path / "main.db")
    db = database.Database(db_path)
    db.init_db(OWNER)
    card_1 = db.create_card_to_card_card(CARD_1, "Synthetic Holder", "Synthetic Bank")
    card_2 = db.create_card_to_card_card(CARD_2, "Second Holder", "Second Bank")
    return SimpleNamespace(db=db, db_path=db_path, card_1=card_1, card_2=card_2)


def scripted(monkeypatch, *offsets):
    rnd = ScriptedRandom(*offsets)
    monkeypatch.setattr(card_to_card_payment, "random", rnd)
    return rnd


def invoice_rows(cards):
    conn = sqlite3.connect(cards.db_path)
    try:
        return conn.execute(
            "SELECT id, kind, ref_id, user_id, base_amount_toman, amount_toman, status "
            "FROM card_to_card_invoices ORDER BY id"
        ).fetchall()
    finally:
        conn.close()


def expire(cards, invoice_id):
    conn = sqlite3.connect(cards.db_path)
    try:
        conn.execute(
            "UPDATE card_to_card_invoices SET expires_at=? WHERE id=?",
            ((datetime.utcnow() - timedelta(minutes=1)).isoformat(), invoice_id),
        )
        conn.commit()
    finally:
        conn.close()


def sig(body=BODY, secret=SECRET, algo=hashlib.sha256):
    return hmac.new(secret.encode("utf-8"), body, algo).hexdigest()


def gateway(mode, **auth):
    return GenericGateway({
        "webhook_auth": {"mode": mode, "secret_field": "webhook_secret", **auth},
        "credentials": {"webhook_secret": SECRET},
    })


class SettingsDb:
    """Settings-only stand-in for the tenant database."""

    def __init__(self, settings=None):
        self.settings = dict(settings or {})

    def get_setting(self, key, default=None):
        return self.settings.get(key, default)


def send(config, amount_toman, settings=None):
    return asyncio.run(compute_send_amount(SettingsDb(settings), config, amount_toman))


# --- payment_engine.py (T023a) ---


def test_amounts_match_accepts_missing_paid_amount():
    assert amounts_match(None, EXPECTED) is True
    assert amounts_match(None, EXPECTED, 0) is True


def test_amounts_match_accepts_unparseable_paid_amount():
    for paid in ("", "abc", "100 تومان", "12.5.3", [], {}, True, False, object()):
        assert amounts_match(paid, EXPECTED) is True


def test_amounts_match_accepts_any_paid_amount_when_expected_is_unusable():
    for expected in (None, "abc", 0, -5, "0"):
        assert amounts_match(0, expected) is True


def test_amounts_match_default_one_percent_floor():
    assert amounts_match(99_000, EXPECTED) is True
    assert amounts_match(99_000.0, EXPECTED) is True
    assert amounts_match("99000", EXPECTED) is True
    assert amounts_match(98_999.99, EXPECTED) is False
    assert amounts_match(98_999, EXPECTED) is False
    assert amounts_match(0, EXPECTED) is False
    assert amounts_match(-1, EXPECTED) is False


def test_amounts_match_has_no_upper_bound():
    for paid in (100_001, 1_000_000, 10**12, "inf"):
        assert amounts_match(paid, EXPECTED) is True


def test_amounts_match_paid_string_parsing():
    assert amounts_match(" 100,000 ", EXPECTED) is True
    assert amounts_match("9,9,0,0,0", EXPECTED) is True
    assert amounts_match("98,999", EXPECTED) is False
    assert amounts_match("1e5", EXPECTED) is True
    assert amounts_match("۱۰۰۰۰۰", EXPECTED) is True
    assert amounts_match("nan", EXPECTED) is False


def test_amounts_match_tolerance_argument():
    assert amounts_match(99_999, EXPECTED, 0) is False
    assert amounts_match(100_000, EXPECTED, 0) is True
    assert amounts_match(99_999, EXPECTED, -5) is False
    assert amounts_match(95_000, EXPECTED, 5) is True
    assert amounts_match(94_999, EXPECTED, 5) is False
    assert amounts_match(0, EXPECTED, 100) is True
    assert amounts_match(-1, EXPECTED, 150) is True
    with pytest.raises(TypeError):
        amounts_match(1, 100, None)


def test_amounts_match_has_no_currency_or_unit_check():
    assert amounts_match(1_000_000, EXPECTED) is True
    assert amounts_match(10, EXPECTED) is False
    assert amounts_match(1, "100,000") is True


def test_check_webhook_auth_defaults_to_mode_none():
    configs = (
        None,
        {},
        {"webhook_enabled": True},
        {"webhook_auth": None},
        {"webhook_auth": {}},
        {"webhook_auth": {"mode": ""}},
        {"webhook_auth": {"mode": None}},
    )
    for config in configs:
        g = GenericGateway(config)
        assert g.check_webhook_auth({}, {}, b"") is True
        assert g.check_webhook_auth(None, None, None) is True


def test_check_webhook_auth_mode_none_ignores_configured_secret():
    g = gateway("none", header_name="X-Signature", query_param="secret")
    assert g.check_webhook_auth({"X-Signature": "forged"}, {"secret": "forged"}, BODY) is True
    assert g.check_webhook_auth({}, {}, b"anything") is True


def test_check_webhook_auth_header_secret():
    g = gateway("header_secret", header_name="X-Webhook-Secret")
    assert g.check_webhook_auth({"x-webhook-secret": SECRET}, {}, BODY) is True
    assert g.check_webhook_auth({"X-WEBHOOK-SECRET": SECRET}, {}, BODY) is True
    assert g.check_webhook_auth({"X-Webhook-Secret": "wrong"}, {}, BODY) is False
    assert g.check_webhook_auth({}, {}, BODY) is False

    empty_credentials = GenericGateway({
        "webhook_auth": {
            "mode": "header_secret",
            "header_name": "X-Webhook-Secret",
            "secret_field": "webhook_secret",
        },
        "credentials": {},
    })
    assert empty_credentials.check_webhook_auth({"X-Webhook-Secret": ""}, {}, BODY) is False

    default_secret_field = GenericGateway({
        "webhook_auth": {"mode": "header_secret", "header_name": "X-Webhook-Secret"},
        "credentials": {"webhook_secret": SECRET},
    })
    assert default_secret_field.check_webhook_auth({"X-Webhook-Secret": SECRET}, {}, BODY) is False


def test_check_webhook_auth_query_secret():
    g = gateway("query_secret", query_param="secret")
    assert g.check_webhook_auth({}, {"secret": SECRET}, BODY) is True
    assert g.check_webhook_auth({}, {"secret": "wrong"}, BODY) is False
    assert g.check_webhook_auth({}, {"Secret": SECRET}, BODY) is False
    assert g.check_webhook_auth({}, {}, BODY) is False
    assert g.check_webhook_auth({}, None, BODY) is False


def test_check_webhook_auth_hmac():
    g = gateway("hmac_sha256", header_name="X-Signature")
    assert g.check_webhook_auth({"X-Signature": sig()}, {}, BODY) is True
    assert g.check_webhook_auth({"x-signature": "  " + sig().upper() + " "}, {}, BODY) is True
    assert g.check_webhook_auth({"X-Signature": sig(b"other")}, {}, BODY) is False
    assert g.check_webhook_auth({"X-Signature": "sha256=" + sig()}, {}, BODY) is False
    assert g.check_webhook_auth({}, {}, BODY) is False
    assert g.check_webhook_auth({"X-Signature": sig(b"")}, {}, None) is True

    alias = gateway("hmac", header_name="X-Signature")
    assert alias.check_webhook_auth({"X-Signature": sig()}, {}, BODY) is True

    md5 = gateway("hmac_sha256", header_name="X-Signature", hmac_algo="md5")
    assert md5.check_webhook_auth({"X-Signature": sig(algo=hashlib.md5)}, {}, BODY) is True
    assert md5.check_webhook_auth({"X-Signature": sig()}, {}, BODY) is False

    fallback = gateway("hmac_sha256", header_name="X-Signature", hmac_algo="no-such-algo")
    assert fallback.check_webhook_auth({"X-Signature": sig()}, {}, BODY) is True

    empty_credentials = GenericGateway({
        "webhook_auth": {
            "mode": "hmac_sha256",
            "header_name": "X-Signature",
            "secret_field": "webhook_secret",
        },
        "credentials": {},
    })
    assert empty_credentials.check_webhook_auth(
        {"X-Signature": sig(secret="")}, {}, BODY
    ) is False


def test_check_webhook_auth_unknown_mode_rejects_and_logs(caplog):
    with caplog.at_level(logging.WARNING, logger="payment_engine"):
        assert gateway("HMAC_SHA256", header_name="X-Signature").check_webhook_auth(
            {"X-Signature": sig()}, {}, BODY
        ) is False
        assert gateway("None").check_webhook_auth({}, {}, BODY) is False
        assert gateway("signature").check_webhook_auth({}, {}, BODY) is False

    records = [record for record in caplog.records if record.name == "payment_engine"]
    assert len(records) == 3
    assert all(record.levelno == logging.WARNING for record in records)
    assert [record.getMessage() for record in records] == [
        "حالت webhook_auth ناشناخته: HMAC_SHA256",
        "حالت webhook_auth ناشناخته: None",
        "حالت webhook_auth ناشناخته: signature",
    ]


def test_parse_webhook_without_amount_path_lets_amount_check_pass():
    mapping = {
        "txn_id_path": "txn_id",
        "status_path": "status",
        "success_values": ["paid"],
    }
    body = {"txn_id": "T-1", "status": "paid", "amount": 1}
    parsed = GenericGateway({"webhook_mapping": mapping}).parse_webhook(body, {})
    assert parsed == {
        "txn_id": "T-1",
        "status_value": "paid",
        "success": True,
        "amount": None,
    }
    assert amounts_match(parsed["amount"], EXPECTED) is True

    with_amount = GenericGateway({
        "webhook_mapping": {**mapping, "amount_path": "amount"},
    }).parse_webhook(body, {})
    assert with_amount["amount"] == 1
    assert amounts_match(with_amount["amount"], EXPECTED) is False

    no_success_values = GenericGateway({
        "webhook_mapping": {"txn_id_path": "txn_id", "status_path": "status"},
    }).parse_webhook(body, {})
    assert no_success_values["success"] is None


# --- custom_gateway_payment.py (T023b) ---


def test_compute_send_amount_toman_default():
    result = send({}, 100_000)
    assert result == {"amount": 100_000, "currency": "IRT"}
    assert type(result["amount"]) is int
    result = send({"amount_multiplier": "1.5"}, 100_000)
    assert result == {"amount": 150_000, "currency": "IRT"}
    assert type(result["amount"]) is int
    assert send({"amount_currency": "toman", "amount_multiplier": "2"}, 100_000) == {
        "amount": 200_000, "currency": "IRT"
    }
    assert send({"amount_currency": None}, 100_000) == {"amount": 100_000, "currency": "IRT"}


def test_compute_send_amount_bad_multiplier_becomes_one():
    for multiplier in (0, "0.0", -2, "-1.5", "abc", None, ""):
        assert send({"amount_multiplier": multiplier}, 100_000) == {
            "amount": 100_000, "currency": "IRT"
        }


def test_compute_send_amount_rounds_half_to_even():
    assert send({"amount_multiplier": 0.5}, 5) == {"amount": 2, "currency": "IRT"}
    assert send({"amount_multiplier": 0.5}, 7) == {"amount": 4, "currency": "IRT"}
    assert send({"amount_multiplier": 1.005}, 100_001) == {"amount": 100_501, "currency": "IRT"}


def test_compute_send_amount_rial_and_unknown_currencies():
    settings = {"usd_to_toman_rate": "abc"}
    result = send({"amount_currency": "rial"}, 100_000, settings)
    assert result == {"amount": 1_000_000, "currency": "IRR"}
    assert type(result["amount"]) is int
    assert send({"amount_currency": " Rial "}, 100_000, settings) == {
        "amount": 1_000_000, "currency": "IRR"
    }
    assert send({"amount_currency": "rial", "amount_multiplier": 1.1}, 100_000, settings) == {
        "amount": 1_100_000, "currency": "IRR"
    }
    assert send({"amount_currency": "rial", "amount_multiplier": 0.17}, 1, settings) == {
        "amount": 2, "currency": "IRR"
    }
    assert send({"amount_currency": "IRR"}, 100_000, settings) == {
        "amount": 100_000, "currency": "IRT"
    }
    assert send({"amount_currency": "eur"}, 100_000, settings) == {
        "amount": 100_000, "currency": "IRT"
    }


def test_compute_send_amount_usd_with_stored_rate(monkeypatch):
    calls = []

    async def fake_rate():
        calls.append(True)
        return 50_000.0

    monkeypatch.setattr(exchange_rate, "get_usd_to_toman_rate", fake_rate)
    settings = {"usd_to_toman_rate": "50000"}
    assert send({"amount_currency": " USD "}, 100_000, settings) == {"amount": 2.0, "currency": "USD"}
    assert send({"amount_currency": "usd", "amount_multiplier": 1.5}, 100_000, settings) == {
        "amount": 3.0, "currency": "USD"
    }
    assert calls == []


def test_compute_send_amount_usd_rounds_before_and_after_multiplier():
    settings = {"usd_to_toman_rate": "60000"}
    assert send({"amount_currency": "usd", "amount_multiplier": 3}, 100_000, settings) == {
        "amount": 5.01, "currency": "USD"
    }


def test_compute_send_amount_usd_minimum_before_multiplier():
    settings = {"usd_to_toman_rate": "50000"}
    message = "مبلغ برای پرداخت کریپتو خیلی کم است (حداقل حدود ۱ دلار)."
    for config in ({"amount_currency": "usd"}, {"amount_currency": "usd", "amount_multiplier": 10}):
        with pytest.raises(CustomGatewayPaymentError) as exc_info:
            send(config, 40_000, settings)
        assert str(exc_info.value) == message
        assert isinstance(exc_info.value.__context__, crypto_payment.CryptoPaymentError)


def test_compute_send_amount_usd_live_rate(monkeypatch, caplog):
    calls = []

    async def fake_rate():
        calls.append(True)
        return 50_000.0

    monkeypatch.setattr(exchange_rate, "get_usd_to_toman_rate", fake_rate)
    assert send({"amount_currency": "usd"}, 100_000, {"usd_to_toman_rate": "0"}) == {
        "amount": 2.0, "currency": "USD"
    }
    assert send({"amount_currency": "usd"}, 100_000, {}) == {"amount": 2.0, "currency": "USD"}
    assert len(calls) == 2

    async def failed_rate():
        calls.append(True)
        raise RuntimeError("synthetic outage")

    monkeypatch.setattr(exchange_rate, "get_usd_to_toman_rate", failed_rate)
    with caplog.at_level(logging.WARNING, logger="crypto_payment"):
        with pytest.raises(CustomGatewayPaymentError) as exc_info:
            send({"amount_currency": "usd"}, 100_000, {"usd_to_toman_rate": "0"})
    assert str(exc_info.value).startswith("دریافت نرخ")
    assert isinstance(exc_info.value.__context__, crypto_payment.CryptoPaymentError)
    records = [record for record in caplog.records if record.name == "crypto_payment"]
    assert len(records) == 1
    assert records[0].levelno == logging.WARNING
    assert records[0].getMessage() == "دریافت نرخ خودکار دلار ناموفق بود: synthetic outage"

    with pytest.raises(ValueError) as exc_info:
        send({"amount_currency": "usd"}, 100_000, {"usd_to_toman_rate": "abc"})
    assert not isinstance(exc_info.value, CustomGatewayPaymentError)


def test_sent_amount_is_not_what_the_amount_check_compares():
    half = send({"amount_multiplier": 0.5}, EXPECTED)
    assert half == {"amount": 50_000, "currency": "IRT"}
    assert amounts_match(half["amount"], EXPECTED) is False
    usd = send({"amount_currency": "usd"}, EXPECTED, {"usd_to_toman_rate": "50000"})
    assert usd["amount"] == 2.0
    assert amounts_match(usd["amount"], EXPECTED) is False
    rial = send({"amount_currency": "rial"}, EXPECTED)
    assert rial["amount"] == 1_000_000
    assert amounts_match(rial["amount"], EXPECTED) is True


# --- card_to_card_payment.py (T023c) ---


def test_normalize_amount_empty_or_digitless_is_none():
    for raw in (None, "", "   ", "abc"):
        assert normalize_amount(raw) is None


def test_normalize_amount_joins_every_digit():
    assert normalize_amount("۱۲۳,۴۵۶") == 123456
    assert normalize_amount("١٢٣٤٥٦") == 123456
    assert normalize_amount("1,250,000 ریال") == 1250000
    assert normalize_amount("12.50") == 1250
    assert normalize_amount("-500") == 500
    assert normalize_amount("مبلغ 100 کارت 6037") == 1006037
    assert normalize_amount(1000) == 1000
    assert normalize_amount(12.5) == 125
    assert normalize_amount(0) == 0
    assert normalize_amount("0") == 0


def test_rial_to_toman_floors_and_defaults_to_rial():
    assert rial_to_toman(1_250_005, "rial") == 125_000
    assert rial_to_toman(1_250_009, "rial") == 125_000
    assert rial_to_toman(1_250_005, None) == 125_000
    assert rial_to_toman(1_250_005, "RIAL") == 125_000
    assert rial_to_toman(1_250_005, "") == 125_000
    assert rial_to_toman(1_250_005, "toman") == 1_250_005
    assert rial_to_toman(1_250_005, "tomans") == 1_250_005


def test_create_invoice_without_a_card(tmp_path):
    db = database.Database(str(tmp_path / "main.db"))
    db.init_db(OWNER)
    with pytest.raises(CardToCardError) as exc_info:
        create_invoice(db, "order", 1, BUYER, 100_000)
    assert str(exc_info.value) == NO_CARD
    conn = sqlite3.connect(str(tmp_path / "main.db"))
    try:
        assert conn.execute("SELECT * FROM card_to_card_invoices").fetchall() == []
    finally:
        conn.close()


def test_create_invoice_adds_a_random_offset(cards, monkeypatch):
    rnd = scripted(monkeypatch, 500)
    before = datetime.utcnow()
    inv = create_invoice(cards.db, "order", 1, BUYER, 100_000)
    after = datetime.utcnow()
    expires_at = datetime.fromisoformat(inv["expires_at"])
    assert {key: value for key, value in inv.items() if key != "expires_at"} == {
        "invoice_id": 1,
        "amount_toman": 100_500,
        "amount_rial": 1_005_000,
        "base_amount_toman": 100_000,
        "card_number": CARD_1,
        "card_holder": "Synthetic Holder",
        "bank_name": "Synthetic Bank",
        "status": "pending",
    }
    assert before + timedelta(minutes=15) <= expires_at <= after + timedelta(minutes=15)
    assert rnd.calls == [(100, 999)]
    assert invoice_rows(cards) == [(1, "order", 1, BUYER, 100_000, 100_500, "pending")]


def test_create_invoice_reuses_the_pending_invoice_for_the_same_ref(cards, monkeypatch):
    rnd = scripted(monkeypatch, 500)
    create_invoice(cards.db, "order", 1, BUYER, 100_000)
    expire(cards, 1)
    again = create_invoice(cards.db, "order", 1, OTHER_BUYER, 150_000)
    assert again["invoice_id"] == 1
    assert again["amount_toman"] == 100_500
    assert again["base_amount_toman"] == 100_000
    assert again["status"] == "pending"
    assert datetime.fromisoformat(again["expires_at"]) < datetime.utcnow()
    assert rnd.calls == [(100, 999)]
    assert invoice_rows(cards) == [(1, "order", 1, BUYER, 100_000, 100_500, "pending")]


def test_create_invoice_retries_a_taken_amount_and_rotates_cards(cards, monkeypatch):
    scripted(monkeypatch, 500)
    create_invoice(cards.db, "order", 1, BUYER, 100_000)
    rnd = scripted(monkeypatch, 500, 501)
    second = create_invoice(cards.db, "wallet_topup", 7, BUYER, 100_000)
    assert second["amount_toman"] == 100_501
    assert second["card_number"] == CARD_2
    assert rnd.calls == [(100, 999), (100, 999)]
    scripted(monkeypatch, 777)
    third = create_invoice(cards.db, "order", 2, OTHER_BUYER, 50_000)
    assert third["amount_toman"] == 50_777
    assert third["card_number"] == CARD_1


def test_create_invoice_gives_up_after_forty_attempts(cards, monkeypatch, caplog):
    scripted(monkeypatch, 500)
    create_invoice(cards.db, "order", 1, BUYER, 100_000)
    rnd = scripted(monkeypatch, 500)
    with caplog.at_level(logging.ERROR, logger="card_to_card_payment"):
        with pytest.raises(CardToCardError) as exc_info:
            create_invoice(cards.db, "order", 2, BUYER, 100_000)
    assert str(exc_info.value) == NO_UNIQUE_AMOUNT
    assert isinstance(exc_info.value.__cause__, sqlite3.IntegrityError)
    assert rnd.calls == [(100, 999)] * 30 + [(1000, 9999)] * 10
    records = [record for record in caplog.records if record.name == "card_to_card_payment"]
    assert len(records) == 1
    assert records[0].levelno == logging.ERROR
    assert records[0].getMessage() == "card_to_card: reserving a unique amount failed after 40 attempts"
    assert len(invoice_rows(cards)) == 1


def test_match_and_complete_matches_on_amount_alone(cards, monkeypatch):
    scripted(monkeypatch, 500)
    create_invoice(cards.db, "order", 1, BUYER, 100_000)
    assert match_and_complete(cards.db, 100_499, sender="x") is None
    assert invoice_rows(cards)[0][-1] == "pending"
    row = match_and_complete(
        cards.db, 100_500, sender="+98 synthetic bank", body="x" * 1500, device_id="dev-1"
    )
    assert row["id"] == 1
    assert row["status"] == "completed"
    assert row["matched_sender"] == "+98 synthetic bank"
    assert len(row["matched_body"]) == 1000
    assert row["matched_device_id"] == "dev-1"
    assert row["updated_at"] is not None
    assert match_and_complete(cards.db, 100_500) is None


def test_match_and_complete_sweeps_expired_invoices_first(cards, monkeypatch):
    scripted(monkeypatch, 500)
    create_invoice(cards.db, "order", 1, BUYER, 100_000)
    expire(cards, 1)
    assert match_and_complete(cards.db, 100_500) is None
    assert cards.db.get_card_to_card_invoice(1)["status"] == "manual_review"


def test_late_sms_completes_another_customers_invoice(cards, monkeypatch):
    scripted(monkeypatch, 500)
    create_invoice(cards.db, "order", 1, BUYER, 100_000)
    expire(cards, 1)
    assert match_and_complete(cards.db, 1) is None
    invoice_2 = create_invoice(cards.db, "wallet_topup", 3, OTHER_BUYER, 100_000)
    assert invoice_2["amount_toman"] == 100_500
    late = match_and_complete(cards.db, 100_500, body="late sms for invoice 1")
    assert late["id"] == 2
    assert late["user_id"] == OTHER_BUYER
    assert late["kind"] == "wallet_topup"
    assert late["ref_id"] == 3
    assert late["status"] == "completed"
    assert invoice_rows(cards) == [
        (1, "order", 1, BUYER, 100_000, 100_500, "manual_review"),
        (2, "wallet_topup", 3, OTHER_BUYER, 100_000, 100_500, "completed"),
    ]


class RacingDb:
    """Delegates to the real database; the first completion first runs a second, overlapping match of the same SMS."""

    def __init__(self, db, amount_toman):
        self.db = db
        self.amount_toman = amount_toman
        self.inner = None
        self.completions = 0
        self._racing = False

    def __getattr__(self, name):
        return getattr(self.db, name)

    def complete_card_to_card_invoice(self, invoice_id, **kwargs):
        self.completions += 1
        if not self._racing:
            self._racing = True
            self.inner = match_and_complete(self, self.amount_toman, sender="second")
        return self.db.complete_card_to_card_invoice(invoice_id, **kwargs)


def test_overlapping_matches_both_complete_the_invoice(cards, monkeypatch):
    scripted(monkeypatch, 500)
    create_invoice(cards.db, "order", 4, BUYER, 200_000)
    racing = RacingDb(cards.db, 200_500)
    outer = match_and_complete(racing, 200_500, sender="first")
    assert outer["id"] == 1
    assert outer["status"] == "completed"
    assert racing.inner["id"] == 1
    assert racing.inner["status"] == "completed"
    assert racing.completions == 2
    assert cards.db.get_card_to_card_invoice(1)["matched_sender"] == "first"


def test_completed_amount_is_free_for_a_new_invoice(cards, monkeypatch):
    scripted(monkeypatch, 500)
    create_invoice(cards.db, "order", 1, BUYER, 100_000)
    assert match_and_complete(cards.db, 100_500)["status"] == "completed"
    invoice_2 = create_invoice(cards.db, "order", 2, OTHER_BUYER, 100_000)
    assert invoice_2["invoice_id"] == 2
    assert invoice_2["amount_toman"] == 100_500
    assert match_and_complete(cards.db, 100_500)["id"] == 2


# --- abangateway_payment.py (T023d) ---


def test_aban_amount_conversion():
    assert toman_to_rial(100_000) == 1_000_000
    assert toman_to_rial("100000") == 1_000_000
    assert toman_to_rial(100.9) == 1_000
    assert aban_rial_to_toman(1_000_009) == 100_000


def test_aban_check_without_or_with_env_key(aban, monkeypatch):
    order = aban.db.create_order(BUYER, aban.product_id, 100_000)
    aban_invoice(aban, "inv_syn_1", order)
    aban.db.set_setting("abangateway_api_key", "")
    assert check(aban, "inv_syn_1") == NO_ABAN_KEY
    assert aban.remote.calls == []
    assert local_status(aban, "inv_syn_1") == "new"
    monkeypatch.setattr(abangateway_payment, "ABANGATEWAY_API_KEY", "synthetic-env-key")
    assert check(aban, "inv_syn_1") == "not_paid_yet"
    assert aban.remote.calls == [("get", "synthetic-env-key", "inv_syn_1")]


def test_aban_unpaid_statuses(aban):
    order = aban.db.create_order(BUYER, aban.product_id, 100_000)
    aban_invoice(aban, "inv_syn_1", order)
    aban.remote.status = "pending"
    assert check(aban, "inv_syn_1") == "not_paid_yet"
    assert local_status(aban, "inv_syn_1") == "new"
    aban.remote.status = "partially_paid"
    assert check(aban, "inv_syn_1") == "not_paid_yet"
    assert local_status(aban, "inv_syn_1") == "pending"
    aban.remote.status = None
    assert check(aban, "inv_syn_1") == "not_paid_yet"
    assert local_status(aban, "inv_syn_1") == "pending"
    assert aban.remote.calls == [("get", ABAN_KEY, "inv_syn_1")] * 3


def test_aban_expired_or_cancelled(aban):
    order_1 = aban.db.create_order(BUYER, aban.product_id, 100_000)
    order_2 = aban.db.create_order(BUYER, aban.product_id, 100_000)
    aban_invoice(aban, "inv_syn_1", order_1)
    aban_invoice(aban, "inv_syn_2", order_2)
    aban.remote.status = "expired"
    assert check(aban, "inv_syn_1") == "expired"
    assert local_status(aban, "inv_syn_1") == "expired"
    aban.remote.status = "cancelled"
    assert check(aban, "inv_syn_2") == "cancelled"
    assert local_status(aban, "inv_syn_2") == "cancelled"
    assert all(call[0] == "get" for call in aban.remote.calls)


def test_aban_paid_is_verified_without_an_amount_check(aban):
    order = aban.db.create_order(BUYER, aban.product_id, 100_000)
    aban_invoice(aban, "inv_syn_1", order)
    aban.remote.status = "paid"
    assert check(aban, "inv_syn_1") == "verified_now"
    assert local_status(aban, "inv_syn_1") == "completed"
    assert aban.remote.calls == [("get", ABAN_KEY, "inv_syn_1"), ("verify", ABAN_KEY, "inv_syn_1")]


def test_aban_completed_invoice_is_not_rechecked(aban):
    order = aban.db.create_order(BUYER, aban.product_id, 100_000)
    aban_invoice(aban, "inv_syn_1", order, status="completed")
    aban.remote.status = "expired"
    assert check(aban, "inv_syn_1") == "already_delivered"
    assert aban.remote.calls == []
    assert local_status(aban, "inv_syn_1") == "completed"


def test_aban_crash_between_verification_and_delivery_loses_the_order(aban):
    order = aban.db.create_order(BUYER, aban.product_id, 100_000)
    aban_invoice(aban, "inv_syn_1", order)
    aban.remote.status = "paid"
    assert check(aban, "inv_syn_1") == "verified_now"
    assert check(aban, "inv_syn_1") == "already_delivered"
    assert aban.remote.calls == [("get", ABAN_KEY, "inv_syn_1"), ("verify", ABAN_KEY, "inv_syn_1")]
    assert order_status(aban, order) == "pending"
    assert aban.log.events == []

    order_2 = aban.db.create_order(BUYER, aban.product_id, 100_000)
    aban_invoice(aban, "inv_syn_2", order_2, status="pending")
    aban.remote.status = "paid"
    aban.remote.verify_error = abangateway_client.AbanGatewayAlreadyVerified(
        "already verified", code="already_verified", http_status=409
    )
    assert check(aban, "inv_syn_2") == "already_delivered"
    assert local_status(aban, "inv_syn_2") == "completed"
    assert order_status(aban, order_2) == "pending"


def test_aban_gateway_errors(aban):
    order = aban.db.create_order(BUYER, aban.product_id, 100_000)
    aban_invoice(aban, "inv_syn_1", order, status="pending")
    aban.remote.status = "paid"
    aban.remote.verify_error = abangateway_client.AbanGatewayNotYetPaid(
        "not yet paid", code="not_yet_paid", http_status=402
    )
    assert check(aban, "inv_syn_1") == "error:not yet paid"
    assert local_status(aban, "inv_syn_1") == "pending"
    aban.remote.verify_error = None
    aban.remote.get_error = abangateway_client.AbanGatewayError("synthetic network failure")
    assert check(aban, "inv_syn_1") == "error:synthetic network failure"
    assert local_status(aban, "inv_syn_1") == "pending"


def test_aban_locally_expired_invoice_is_still_verified(aban):
    order = aban.db.create_order(BUYER, aban.product_id, 100_000)
    aban_invoice(aban, "inv_syn_1", order, status="expired")
    aban.remote.status = "paid"
    assert check(aban, "inv_syn_1") == "verified_now"
    assert local_status(aban, "inv_syn_1") == "completed"


def test_finalize_missing_order(aban):
    assert deliver(aban, 999) == NO_ORDER
    assert aban.log.events == []


def test_finalize_delivers_any_pending_order_once(aban):
    order = aban.db.create_order(BUYER, aban.product_id, 100_000)
    notified = []

    async def notify(bot, order_id):
        notified.append(order_id)

    assert deliver(aban, order, notify) == DELIVERED
    assert order_status(aban, order) == "approved"
    assert stock_rows(aban) == [(1, 1, BUYER, order), (2, 0, None, None)]
    assert notified == [order]
    assert aban.log.trace() == [("send_message", OWNER), ("send_photo", BUYER), ("send_message", BUYER), ("send_message", BUYER)]
    assert "vless://stock-1" in aban.log.events[2].text
    assert deliver(aban, order, notify) == ALREADY_HANDLED
    assert len(aban.log.events) == 4
    assert notified == [order]
    assert stock_rows(aban) == [(1, 1, BUYER, order), (2, 0, None, None)]


def test_finalize_refuses_orders_that_are_not_pending(aban):
    rejected = aban.db.create_order(BUYER, aban.product_id, 100_000)
    processing = aban.db.create_order(BUYER, aban.product_id, 100_000)
    conn = sqlite3.connect(aban.db_path)
    try:
        conn.execute("UPDATE orders SET status='rejected' WHERE id=?", (rejected,))
        conn.execute("UPDATE orders SET status='processing' WHERE id=?", (processing,))
        conn.commit()
    finally:
        conn.close()
    assert deliver(aban, rejected) == ALREADY_HANDLED
    assert deliver(aban, processing) == ALREADY_HANDLED
    assert order_status(aban, rejected) == "rejected"
    assert order_status(aban, processing) == "processing"
    assert aban.log.events == []
    assert stock_rows(aban) == [(1, 0, None, None), (2, 0, None, None)]


def test_finalize_out_of_stock_returns_the_order_to_pending(aban):
    first = aban.db.create_order(BUYER, aban.product_id, 100_000)
    second = aban.db.create_order(BUYER, aban.product_id, 100_000)
    third = aban.db.create_order(BUYER, aban.product_id, 100_000)
    assert deliver(aban, first) == DELIVERED
    assert deliver(aban, second) == DELIVERED
    n = len(aban.log.events)
    text = deliver(aban, third)
    assert text.startswith("⚠️ پرداخت تایید شد ولی موجودی")
    assert order_status(aban, third) == "pending"
    assert len(aban.log.events) == n


def test_finalize_auto_provision(aban, monkeypatch):
    product = aban.db.add_product(aban.category_id, "Auto 30d", 100_000, is_auto_provision=True, auto_provision_volume_gb=10, provision_server_id=7)
    order = aban.db.create_order(BUYER, product, 100_000)
    calls = []

    async def failed_provision(db, product, quantity, user_id=None, order_id=None):
        calls.append((product["id"], quantity, user_id, order_id))
        raise DirectProvisionError("synthetic panel down")

    monkeypatch.setattr(abangateway_payment, "provision_direct", failed_provision)
    assert deliver(aban, order) == "⚠️ پرداخت تایید شد ولی ساخت خودکار کانفیگ ناموفق بود: synthetic panel down\nبا پشتیبانی تماس بگیرید."
    assert calls == [(product, 1, BUYER, order)]
    assert order_status(aban, order) == "pending"
    assert aban.log.events == []

    async def successful_provision(db, product, quantity, user_id=None, order_id=None):
        return [{"subscription_url": "vless://auto-1"}]

    monkeypatch.setattr(abangateway_payment, "provision_direct", successful_provision)
    assert deliver(aban, order) == DELIVERED
    assert order_status(aban, order) == "approved"
    assert aban.log.trace() == [("send_photo", BUYER), ("send_message", BUYER), ("send_message", BUYER)]


def test_finalize_renewal(aban, monkeypatch, caplog):
    order = aban.db.create_renewal_order(BUYER, "config", 1, "full", 10, 30, 80_000)

    async def renewal_error(db, order):
        raise RenewalError("synthetic renewal failure")

    monkeypatch.setattr(abangateway_payment, "execute_renewal", renewal_error)
    assert deliver(aban, order) == "⛔️ تمدید ناموفق بود: synthetic renewal failure\nبا پشتیبانی تماس بگیرید."
    assert order_status(aban, order) == "pending"

    async def renewal_crash(db, order):
        raise RuntimeError("synthetic crash")

    monkeypatch.setattr(abangateway_payment, "execute_renewal", renewal_crash)
    with caplog.at_level(logging.ERROR, logger="abangateway_payment"):
        text = deliver(aban, order)
    assert text.startswith("⛔️ خطای غیرمنتظره")
    assert order_status(aban, order) == "pending"
    records = [record for record in caplog.records if record.name == "abangateway_payment" and record.levelno == logging.ERROR]
    assert len(records) == 1
    assert records[0].exc_info

    async def renewal_success(db, order):
        return "synthetic renewal done"

    monkeypatch.setattr(abangateway_payment, "execute_renewal", renewal_success)
    assert deliver(aban, order) == "synthetic renewal done"
    assert order_status(aban, order) == "approved"
    assert aban.log.trace() == [("send_message", BUYER)]
    assert aban.log.events[0].text == "synthetic renewal done"


def test_finalize_custom_config_without_server(aban):
    order = aban.db.create_custom_config_order(BUYER, 10, "synthetic_user", 42, 90_000)
    assert deliver(aban, order) == "⛔️ سرور مربوط به کانفیگ شخصی یافت نشد؛ با پشتیبانی تماس بگیرید."
    assert order_status(aban, order) == "pending"
    assert aban.log.events == []


# --- extra_gateway_clients.py (T023e) ---


def test_tetra98_create_sends_rial(http):
    http.replies = [
        (200, {"status": 100, "Authority": "A-1", "payment_url_web": "https://pay.example.invalid/web/A-1", "payment_url_bot": "https://pay.example.invalid/bot/A-1"}),
        (200, {"status": "100", "Authority": 77}),
    ]
    assert asyncio.run(tetra98_create(TETRA_KEY, 100_000, CALLBACK, "x" * 250, "ORD-1")) == {
        "remote_id": "A-1", "payment_url": "https://pay.example.invalid/web/A-1",
        "meta": {"bot_url": "https://pay.example.invalid/bot/A-1"},
    }
    assert asyncio.run(tetra98_create(TETRA_KEY, 99.9, CALLBACK, "d", "ORD-1")) == {
        "remote_id": "77", "payment_url": "https://tetra98.com/payment/77", "meta": {"bot_url": ""},
    }
    assert http.calls[0] == (
        "POST", "https://tetra98.com/api/create_order", None,
        {"ApiKey": TETRA_KEY, "Hash_id": "ORD-1", "Amount": 1_000_000, "Description": "x" * 200, "CallbackURL": CALLBACK},
    )
    assert http.calls[1][3]["Amount"] == 990


def test_tetra98_create_errors(http):
    for reply, expected in (
        ((200, {"status": "101", "message": "synthetic refusal"}), TETRA_REFUSED_200),
        ((502, {}), TETRA_CREATE_FAILED_502),
        ((200, {"status": 100}), TETRA_CREATE_FAILED_200),
    ):
        http.replies = [reply]
        assert gateway_error(tetra98_create(TETRA_KEY, 100_000, CALLBACK, "d", "ORD-1")) == expected


@pytest.mark.parametrize("reply, expected", [
    ((200, {"status": 100}), "paid"),
    ((200, {"status": "100"}), "paid"),
    ((200, {"status": 100, "Amount": 10, "Hash_id": "OTHER"}), "paid"),
    ((200, {"status": 101}), "pending"),
    ((201, {"status": 100}), "pending"),
    ((400, {"status": "-1"}), "pending"),
    ((404, {}), "pending"),
    ((500, {}), TETRA_SERVER_500),
])
def test_tetra98_verify_trusts_status_alone(http, reply, expected):
    http.replies = [reply]
    if expected == TETRA_SERVER_500:
        assert gateway_error(tetra98_verify(TETRA_KEY, "A-1")) == expected
    else:
        assert asyncio.run(tetra98_verify(TETRA_KEY, "A-1")) == expected
    assert http.calls == [("POST", "https://tetra98.com/api/verify", None, {"ApiKey": TETRA_KEY, "authority": "A-1"})]


@pytest.mark.parametrize("amount, fee, expected", [
    (100_000, 0, 100_000), (100_000, -5, 100_000), (100_000, 2.5, 102_500),
    (99_999, 1.5, 101_499), ("100000", 1, 101_000), (100_000, 100, 200_000),
    (100_000, 100.4, 100_100), (100_000, 100.5, 100_100), (100_000, 101, 100_101),
    (100_000, 101.5, 100_102),
])
def test_cubepay_payable_toman(amount, fee, expected):
    result = cubepay_payable_toman(amount, fee)
    assert result == expected
    assert type(result) is int


def test_cubepay_create_sends_rial(http):
    http.replies = [
        (200, {"success": True, "authority": "CB-1", "payment_link": "https://pay.example.invalid/cb/1", "pay_page_url": "https://pay.example.invalid/page/1", "pay_amount_toman": 102_500}),
        (200, {"success": True, "authority": 88, "pay_page_url": "https://pay.example.invalid/page/88"}),
    ]
    args = (CUBE_TOKEN, 102_500, CALLBACK, "y" * 250, "ORD-2", 1001)
    assert asyncio.run(cubepay_create(*args)) == {
        "remote_id": "CB-1", "payment_url": "https://pay.example.invalid/cb/1", "meta": {"pay_amount_toman": 102_500},
    }
    assert http.calls[0] == (
        "POST", "https://cubevps.ir/smspay/api/create-payment.php", CUBE_HEADERS,
        {"amount": 1_025_000, "order_id": "ORD-2", "callback_url": CALLBACK, "type": "card",
         "customer_user_id": "1001", "description": "y" * 200},
    )
    assert asyncio.run(cubepay_create(*args)) == {
        "remote_id": "88", "payment_url": "https://pay.example.invalid/page/88", "meta": {"pay_amount_toman": None},
    }


def test_cubepay_create_errors(http):
    for reply, expected in (
        ((200, {"success": True, "authority": "CB-1"}), CUBE_NO_LINK),
        ((400, {"success": False, "message": "synthetic refusal"}), CUBE_REFUSED_400),
        ((200, {"success": True}), CUBE_CREATE_FAILED_200),
    ):
        http.replies = [reply]
        assert gateway_error(cubepay_create(CUBE_TOKEN, 102_500, CALLBACK, "d", "ORD-2", 1001)) == expected


def test_cubepay_verify_request(http):
    http.replies = [(200, {"success": True, "order_id": "ORD-2", "amount": 1_025_000})]
    assert asyncio.run(cubepay_verify(CUBE_TOKEN, "CB-1", "ORD-2", 1_025_000)) == "paid"
    assert http.calls == [(
        "POST", "https://cubevps.ir/smspay/api/verify-payment.php", CUBE_HEADERS, {"authority": "CB-1"},
    )]


@pytest.mark.parametrize("reply, expected", [
    ((200, {"success": True, "order_id": "ORD-9", "amount": 1_025_000}), CUBE_ORDER_MISMATCH),
    ((200, {"success": True, "order_id": "ORD-2", "amount": 1_024_999}), CUBE_SHORT),
    ((409, {"amount": 1}), CUBE_SHORT),
    ((200, {"success": True}), "paid"),
    ((200, {"success": True, "order_id": "ORD-2", "amount": 9_999_999}), "paid"),
    ((200, {"success": True, "order_id": "ORD-2", "amount": "1.025e6"}), "paid"),
    ((200, {"success": True, "order_id": "ORD-2", "amount": "abc"}), "paid"),
    ((409, {}), "paid"),
    ((200, {"success": False}), "pending"), ((200, {}), "pending"),
    ((402, {"order_id": "ORD-9", "amount": 1}), "pending"), ((400, {}), "pending"),
    ((404, {}), "failed"), ((410, {}), "failed"),
    ((500, {}), CUBE_SERVER_500), ((503, {"success": True}), CUBE_SERVER_503),
])
def test_cubepay_verify_outcomes(http, reply, expected):
    http.replies = [reply]
    call = cubepay_verify(CUBE_TOKEN, "CB-1", "ORD-2", 1_025_000)
    if expected in (CUBE_ORDER_MISMATCH, CUBE_SHORT, CUBE_SERVER_500, CUBE_SERVER_503):
        assert gateway_error(call) == expected
    else:
        assert asyncio.run(call) == expected


def test_nowpayments_create_invoice(http):
    http.replies = [(200, {"id": 5077, "invoice_url": "https://pay.example.invalid/np/5077"})]
    args = (NP_KEY, 2.35, "ORD-3", "z" * 250, "https://bot.example.invalid/ipn?b=7")
    assert asyncio.run(nowpayments_create_invoice(*args)) == {
        "remote_id": "5077", "payment_url": "https://pay.example.invalid/np/5077", "meta": {"price_usd": 2.35},
    }
    assert http.calls == [(
        "POST", "https://api.nowpayments.io/v1/invoice", {"x-api-key": NP_KEY, "Content-Type": "application/json"},
        {"price_amount": 2.35, "price_currency": "usd", "order_id": "ORD-3", "order_description": "z" * 200,
         "ipn_callback_url": "https://bot.example.invalid/ipn?b=7"},
    )]
    http.replies = [(400, {"message": "synthetic refusal"})]
    assert gateway_error(nowpayments_create_invoice(*args)) == NP_REFUSED_400
    http.replies = [(200, {"id": 1})]
    assert gateway_error(nowpayments_create_invoice(*args)) == NP_CREATE_FAILED_200


def test_nowpayments_payment_status(http):
    http.replies = [(200, dict(NP_PAYMENT))]
    assert asyncio.run(nowpayments_payment_status(NP_KEY, "P-9")) == NP_PAYMENT
    assert http.calls == [("GET", "https://api.nowpayments.io/v1/payment/P-9", {"x-api-key": NP_KEY}, None)]
    http.replies = [(404, {"payment_status": "finished"})]
    assert gateway_error(nowpayments_payment_status(NP_KEY, "P-9")) == NP_STATUS_404
    http.replies = [(201, {})]
    assert gateway_error(nowpayments_payment_status(NP_KEY, "P-9")) == NP_STATUS_201


DROP = object()


@pytest.mark.parametrize("changes, expected_usd, expected", [
    ({}, 2.35, "paid"), ({"invoice_id": "5078"}, 2.35, "failed"), ({"invoice_id": DROP}, 2.35, "failed"),
    ({"order_id": "ORD-4"}, 2.35, "failed"), ({"order_id": DROP}, 2.35, "failed"),
    ({"price_amount": 2.345}, 2.35, "paid"), ({"price_amount": 2.34}, 2.35, "failed"),
    ({"price_amount": 1000}, 2.35, "paid"), ({"price_amount": "2.35"}, 2.35, "paid"),
    ({"price_amount": "abc"}, 2.35, "failed"), ({"price_amount": DROP}, 2.35, "failed"),
    ({"price_amount": DROP}, 0, "paid"), ({"actually_paid": 0.01, "pay_amount": 5}, 2.35, "paid"),
    ({"payment_status": "partially_paid", "actually_paid": 0.01}, 2.35, "pending"),
    ({"payment_status": "waiting"}, 2.35, "pending"), ({"payment_status": "confirming"}, 2.35, "pending"),
    ({"payment_status": "confirmed"}, 2.35, "pending"), ({"payment_status": "sending"}, 2.35, "pending"),
    ({"payment_status": "FINISHED"}, 2.35, "pending"), ({"payment_status": DROP}, 2.35, "pending"),
    ({"payment_status": "failed"}, 2.35, "failed"), ({"payment_status": "refunded"}, 2.35, "failed"),
    ({"payment_status": "expired"}, 2.35, "failed"),
])
def test_nowpayments_classify(changes, expected_usd, expected):
    payment = {**NP_PAYMENT, **changes}
    for key, value in changes.items():
        if value is DROP:
            payment.pop(key, None)
    assert nowpayments_classify(payment, "5077", "ORD-3", expected_usd) == expected


def test_nowpayments_ipn_signature():
    assert json.dumps(IPN_BODY, sort_keys=True, separators=(",", ":"), ensure_ascii=False) == IPN_CANONICAL
    sig_value = sign(NP_SECRET, IPN_CANONICAL)
    reordered = {key: IPN_BODY[key] for key in reversed(IPN_BODY)}
    reordered["fee"] = {key: IPN_BODY["fee"][key] for key in reversed(IPN_BODY["fee"])}
    for secret, body, signature in (
        (NP_SECRET, IPN_BODY, sig_value), (NP_SECRET, IPN_BODY, "  " + sig_value.upper() + "\n"),
        (NP_SECRET, reordered, sig_value),
    ):
        assert nowpayments_verify_ipn_signature(secret, body, signature) is True
    for secret, body, signature in (
        (NP_SECRET, IPN_BODY, sign(NP_SECRET, json.dumps(IPN_BODY, sort_keys=True))),
        (NP_SECRET, IPN_BODY, sign(NP_SECRET, json.dumps(IPN_BODY, sort_keys=True, separators=(",", ":")))),
        (NP_SECRET, IPN_BODY, sign("other-secret", IPN_CANONICAL)),
        (NP_SECRET, {**IPN_BODY, "price_amount": 2.36}, sig_value),
        ("", IPN_BODY, sign("", IPN_CANONICAL)), (None, IPN_BODY, sig_value),
        (NP_SECRET, IPN_BODY, ""), (NP_SECRET, IPN_BODY, None), (NP_SECRET, IPN_BODY, sig_value[:64]),
        (NP_SECRET, IPN_BODY, sign(NP_SECRET, IPN_CANONICAL, hashlib.sha256)),
    ):
        assert nowpayments_verify_ipn_signature(secret, body, signature) is False
