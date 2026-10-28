"""Characterize the legacy payment verification helpers at commit b1390ac.

Baseline: ``.venv/bin/python -m pytest tests/characterization/test_payment_methods_legacy.py --network=deny``.
All inputs are synthetic and the helpers are called directly (no provider, no database). The settings database and the live USD rate are stubs (substitute, not evidence).
These are E-005 source leads, not method certification; composite payments must not use these helpers as authority (FR-011).

Known unsafe behaviour (payment_engine.py): (a) ``amounts_match`` accepts when the paid amount is missing or unparseable, or the expected amount is unparseable or not positive (cases 1–3, 8); (b) it has only a lower bound, so any overpayment, ``"inf"`` and a Rial amount for a Toman invoice pass (cases 5, 8); (c) a 1 % shortfall passes by default, and a tolerance of 100 accepts zero (cases 4, 7); (d) it never checks currency or unit (case 8); (e) webhook authentication defaults to mode ``none``, which accepts any request even when a secret is configured (cases 9, 10); (f) without ``amount_path`` a parsed webhook carries no amount, so the amount check passes (case 15).

Known unsafe behaviour (custom_gateway_payment.py): (g) the amount sent to the gateway is converted (×10 for Rial, a stored or live USD rate for USD) and multiplied, but the legacy amount check compares the gateway's reported amount with the unconverted Toman price, so a gateway that reports exactly what it was asked to can fail, and a Rial figure passes (case 24); (h) a missing, non-numeric, zero or negative multiplier silently becomes 1 (case 17); (i) an unknown currency, including ``"IRR"``, is silently sent as Toman (case 19); (j) USD amounts are rounded twice, before and after the multiplier, and the 1-dollar minimum is checked before the multiplier (cases 21, 22).

Later sections (T023c–T023f) characterize the other payment modules.
"""

import asyncio
import hashlib
import hmac
import logging

import pytest

import crypto_payment
import exchange_rate
import payment_engine
from custom_gateway_payment import CustomGatewayPaymentError, compute_send_amount
from payment_engine import GenericGateway, amounts_match


EXPECTED = 100_000
SECRET = "synthetic-webhook-secret"
BODY = b'{"txn_id":"T-1","status":"paid","amount":"100000"}'


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
