"""T045: cryptographic backend failures must not expose credential text."""

import logging
import secrets

import pytest
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

import composite.secrets as subject
from tests._harness.secret_scan import SecretScan


@pytest.mark.parametrize("method", ["encrypt", "decrypt"])
def test_crypto_backend_failure_has_sanitized_exception(method, monkeypatch):
    secret = secrets.token_urlsafe(32)
    scan = SecretScan()
    scan.add("token", secret)
    box = subject.SecretBox({"active": secrets.token_bytes(32)}, "active")
    envelope = box.encrypt(secret)

    def fail(*args, **kwargs):
        raise ValueError(secret)

    # Replace only the external library operation, never the wrapper under test.
    monkeypatch.setattr(AESGCM, method, fail)
    with pytest.raises(subject.SecretError) as caught:
        getattr(box, method)(secret if method == "encrypt" else envelope)
    scan.check_exception(caught.value)


def test_redaction_removes_formatter_cached_message():
    secret = secrets.token_urlsafe(32)
    scan = SecretScan()
    scan.add("token", secret)
    record = logging.LogRecord("composite.test", logging.ERROR, __file__, 1, secret, (), None)
    logging.Formatter().format(record)
    assert subject.SecretRedactionFilter().filter(record) is True
    scan.check_text(repr(vars(record)), source="post-formatter record")
    scan.check_text(logging.Formatter().format(record), source="reformatted record")


@pytest.mark.parametrize("size", [16, 24, 32])
def test_supported_aes_keys_are_copied_from_configuration(size):
    key = secrets.token_bytes(size)
    configured = {"active": key}
    box = subject.SecretBox(configured, "active")
    configured.clear()
    plaintext = "synthetic valid input"
    envelope = box.encrypt(plaintext)
    assert AESGCM(key).decrypt(
        envelope.nonce, envelope.ciphertext, b"shopvpn:secrets:v1:active"
    ).decode("utf-8") == plaintext
    assert box.decrypt(envelope) == plaintext
