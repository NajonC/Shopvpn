"""Characterize the legacy payment verification helpers at commit b1390ac.

Baseline: ``.venv/bin/python -m pytest tests/characterization/test_payment_methods_legacy.py --network=deny``.
All inputs are synthetic and the helpers are called directly (no provider, no database). The settings database and the live USD rate are stubs (substitute, not evidence). Aban cases fake only the gateway client calls (and, where stated, provisioning or renewal); delivery runs against a recording bot.
Card-to-card cases use a real SQLite database under tmp_path and a scripted random source.
These are E-005 source leads, not method certification; composite payments must not use these helpers as authority (FR-011).

Known unsafe behaviour (payment_engine.py): (a) ``amounts_match`` accepts when the paid amount is missing or unparseable, or the expected amount is unparseable or not positive (cases 1–3, 8); (b) it has only a lower bound, so any overpayment, ``"inf"`` and a Rial amount for a Toman invoice pass (cases 5, 8); (c) a 1 % shortfall passes by default, and a tolerance of 100 accepts zero (cases 4, 7); (d) it never checks currency or unit (case 8); (e) webhook authentication defaults to mode ``none``, which accepts any request even when a secret is configured (cases 9, 10); (f) without ``amount_path`` a parsed webhook carries no amount, so the amount check passes (case 15).

Known unsafe behaviour (custom_gateway_payment.py): (g) the amount sent to the gateway is converted (×10 for Rial, a stored or live USD rate for USD) and multiplied, but the legacy amount check compares the gateway's reported amount with the unconverted Toman price, so a gateway that reports exactly what it was asked to can fail, and a Rial figure passes (case 24); (h) a missing, non-numeric, zero or negative multiplier silently becomes 1 (case 17); (i) an unknown currency, including ``"IRR"``, is silently sent as Toman (case 19); (j) USD amounts are rounded twice, before and after the multiplier, and the 1-dollar minimum is checked before the multiplier (cases 21, 22).

Known unsafe behaviour (card_to_card_payment.py): (k) the customer pays the base price plus a random offset of 100–999 Toman (1000–9999 on the last ten attempts), and the offset is kept (cases 29, 31); (l) an existing pending invoice is returned for the same order whatever the user, price or deadline (case 30); (m) ``normalize_amount`` deletes every non-digit, so decimals, signs and any other digits in the text are joined into one number (case 26); (n) the Rial-to-Toman conversion floors, and any unit other than ``rial`` counts as Toman (case 27); (o) an SMS is matched by amount alone, with no card, sender, user or order check (case 33); (p) once an invoice expires its amount is free again, so a late SMS for it completes another customer's invoice (case 35); (q) completion has no pending-status condition, so two overlapping matches of one SMS both return the invoice as completed (case 36).

Known unsafe behaviour (abangateway_payment.py): (r) verification trusts the gateway's status alone and never compares the paid amount with the invoice (case 42); (s) the invoice is marked completed before anything is delivered, so after a crash between verification and delivery every retry answers "already delivered" and the order is never fulfilled (case 44); (t) a locally expired invoice that the gateway reports paid is still verified (case 46); (u) ``finalize_paid_order`` takes only an order id and delivers any pending order with no invoice or payment check (case 48); (v) when delivery fails after payment (stock exhausted, provisioning, renewal or a missing server), the order silently returns to pending with no refund or record of the payment (cases 50–53).

Later sections (T023e–T023f) characterize the other payment modules.
"""

import asyncio
import hashlib
import hmac
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
import payment_engine
from card_to_card_payment import CardToCardError, create_invoice, match_and_complete, normalize_amount, rial_to_toman
from abangateway_payment import finalize_paid_order, rial_to_toman as aban_rial_to_toman, toman_to_rial, try_verify_and_finalize
from custom_gateway_payment import CustomGatewayPaymentError, compute_send_amount
from direct_panel_provision import ProvisionError as DirectProvisionError
from payment_engine import GenericGateway, amounts_match
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
