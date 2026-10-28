"""Characterize the legacy payment verification helpers at commit b1390ac.

Baseline: ``.venv/bin/python -m pytest tests/characterization/test_payment_methods_legacy.py --network=deny``.
All inputs are synthetic and the helpers are called directly (no provider, no database).
These are E-005 source leads, not method certification; composite payments must not use these helpers as authority (FR-011).

Known unsafe behaviour (payment_engine.py): (a) ``amounts_match`` accepts when the paid amount is missing or unparseable, or the expected amount is unparseable or not positive (cases 1–3, 8); (b) it has only a lower bound, so any overpayment, ``"inf"`` and a Rial amount for a Toman invoice pass (cases 5, 8); (c) a 1 % shortfall passes by default, and a tolerance of 100 accepts zero (cases 4, 7); (d) it never checks currency or unit (case 8); (e) webhook authentication defaults to mode ``none``, which accepts any request even when a secret is configured (cases 9, 10); (f) without ``amount_path`` a parsed webhook carries no amount, so the amount check passes (case 15).

Later sections (T023b–T023f) characterize the other payment modules.
"""

import hashlib
import hmac
import logging

import pytest

import payment_engine
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
