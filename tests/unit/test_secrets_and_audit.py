"""T044 contracts for T045 secrets and T046 sanitized diagnostics.

All credentials are generated at runtime. No production configuration is read.
SecretBox(keys: dict[str, bytes], current_key_id: str) takes explicitly supplied
authorized keys; it never generates a fallback key. encrypt(str) returns frozen
EncryptedValue(version=1, key_id=str, nonce=bytes, ciphertext=bytes); decrypt
returns str. AES-GCM AAD is b'shopvpn:secrets:v1:' + key_id.encode('utf-8').
SecretError is the sanitized failure boundary. token_digest(str) is SHA-256 hex
of exact UTF-8 bytes. SecretRedactionFilter() keeps only standard non-text log
metadata plus operation/tenant_id/record_id extras; free text is discarded.
install_log_redaction(logger) protects that composite logger and its handlers.
sanitized_diagnostic(*, operation, tenant_id, record_id, error=None) returns
only the three identifying fields, without exception detail or success claims.
These interface choices are local contracts, not claims of deployed security.
"""

import dataclasses
import hashlib
import io
import logging
import secrets
import sys

import pytest
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

import composite.audit as audit
import composite.secrets as subject
from tests._harness.secret_scan import SecretScan


@pytest.fixture
def material():
    scan = SecretScan()
    token = secrets.token_urlsafe(32)
    password = secrets.token_urlsafe(24)
    uri = f"trojan://{password}@node.example.invalid:443#synthetic"
    url = f"https://shop.example.invalid/sub/{token}"
    for kind, value in (("token", token), ("password", password), ("URI", uri), ("URL", url)):
        scan.add(kind, value)
    return scan, (token, password, uri, url)


def _box():
    keys = {"old": secrets.token_bytes(32), "active": secrets.token_bytes(32)}
    return keys, subject.SecretBox(keys, "active")


def test_round_trip_is_independent_aes_gcm_and_hides_plaintext(material):
    scan, values = material
    keys, box = _box()
    for value in (*values, "", "متن آزمایشی"):
        envelope = box.encrypt(value)
        assert envelope.version == 1
        assert envelope.key_id == "active"
        assert len(envelope.nonce) == 12
        assert len(envelope.ciphertext) == len(value.encode()) + 16
        assert AESGCM(keys["active"]).decrypt(
            envelope.nonce, envelope.ciphertext, b"shopvpn:secrets:v1:active"
        ).decode() == value
        assert box.decrypt(envelope) == value
        scan.check_text(repr(envelope), source="encrypted envelope repr")
        with pytest.raises(dataclasses.FrozenInstanceError):
            envelope.key_id = "old"


def test_independently_encrypted_old_key_remains_readable(material):
    _, values = material
    keys, box = _box()
    nonce = secrets.token_bytes(12)
    ciphertext = AESGCM(keys["old"]).encrypt(
        nonce, values[0].encode(), b"shopvpn:secrets:v1:old"
    )
    envelope = subject.EncryptedValue(1, "old", nonce, ciphertext)
    assert box.decrypt(envelope) == values[0]
    assert box.encrypt(values[0]).key_id == "active"


def test_encrypt_uses_fresh_nonces_for_same_value(material):
    _, values = material
    _, box = _box()
    envelopes = [box.encrypt(values[0]) for _ in range(64)]
    assert len({e.nonce for e in envelopes}) == 64
    assert len({e.ciphertext for e in envelopes}) == 64


@pytest.mark.parametrize("failure", ["missing", "wrong", "ciphertext", "nonce", "version", "key_id"])
def test_decrypt_refuses_invalid_envelope_without_secret_exception(failure, material):
    scan, values = material
    keys, box = _box()
    envelope = box.encrypt(values[0])
    if failure == "missing":
        box = subject.SecretBox({"old": keys["old"]}, "old")
    elif failure == "wrong":
        box = subject.SecretBox({"active": secrets.token_bytes(32)}, "active")
    elif failure == "ciphertext":
        data = envelope.ciphertext
        envelope = dataclasses.replace(envelope, ciphertext=bytes([data[0] ^ 1]) + data[1:])
    elif failure == "nonce":
        envelope = dataclasses.replace(envelope, nonce=bytes([envelope.nonce[0] ^ 1]) + envelope.nonce[1:])
    elif failure == "version":
        envelope = dataclasses.replace(envelope, version=2)
    else:
        # Same raw key under two IDs: authentication must bind the key ID.
        box = subject.SecretBox({"active": keys["active"], "alias": keys["active"]}, "active")
        envelope = dataclasses.replace(envelope, key_id="alias")
    with pytest.raises(subject.SecretError) as caught:
        box.decrypt(envelope)
    scan.check_exception(caught.value)


@pytest.mark.parametrize("keys,current", [({}, "active"), ({"old": b"x" * 32}, "active"), ({"active": b"x" * 31}, "active")])
def test_missing_or_malformed_key_never_gets_fallback(keys, current):
    with pytest.raises(subject.SecretError):
        subject.SecretBox(keys, current)


def test_sha256_digest_is_exact_utf8_without_normalization(material):
    scan, values = material
    for value in (*values, "", "abc", " abc ", "متن"):
        digest = subject.token_digest(value)
        assert digest == hashlib.sha256(value.encode("utf-8")).hexdigest()
        assert len(digest) == 64
    assert subject.token_digest("abc") == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    scan.check_text(repr([subject.token_digest(v) for v in values]), source="digests")


@pytest.mark.parametrize("style", ["message", "positional", "mapping", "exception", "cached_exception", "extras"])
def test_redaction_scrubs_log_record_and_formatted_exception(style, material):
    scan, values = material
    secret_text = " ".join(values)
    record = logging.LogRecord("composite.test", logging.ERROR, __file__, 1, "failure", (), None)
    if style == "message":
        record.msg = secret_text
    elif style == "positional":
        record.msg, record.args = "failure %s", (secret_text,)
    elif style == "mapping":
        record.msg, record.args = "failure %(payload)s", {"payload": secret_text}
    elif style == "exception":
        try:
            raise RuntimeError(secret_text)
        except RuntimeError:
            record.exc_info = sys.exc_info()
    elif style == "cached_exception":
        record.exc_text, record.stack_info = secret_text, secret_text
    else:
        record.payload = {"authorization": secret_text}
    record.operation, record.tenant_id, record.record_id = "provision", 7, 19
    assert subject.SecretRedactionFilter().filter(record) is True
    scan.check_logs([record])
    scan.check_text(logging.Formatter().format(record), source="formatted log")
    assert (record.operation, record.tenant_id, record.record_id) == ("provision", 7, 19)
    assert record.levelno == logging.ERROR


def test_installed_filter_protects_logger_and_descendant_handler(material):
    scan, values = material
    logger = logging.getLogger("composite.t044")
    child = logging.getLogger("composite.t044.child")
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    old = logger.handlers[:], logger.filters[:], logger.level, logger.propagate
    child_old = child.handlers[:], child.filters[:], child.level, child.propagate
    try:
        logger.handlers, logger.filters = [handler], []
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
        child.handlers, child.filters = [], []
        child.setLevel(logging.NOTSET)
        child.propagate = True
        subject.install_log_redaction(logger)
        subject.install_log_redaction(logger)
        logger.error("direct %s", values[0])
        child.error("descendant %s", values[2])
        assert len(stream.getvalue().splitlines()) == 2
        scan.check_text(stream.getvalue(), source="installed logging")
    finally:
        logger.handlers, logger.filters, logger.level, logger.propagate = old
        child.handlers, child.filters, child.level, child.propagate = child_old
        handler.close()


@pytest.mark.parametrize("has_error", [False, True])
def test_diagnostic_contains_only_operation_tenant_record(has_error, material):
    scan, values = material
    error = RuntimeError(" ".join(values)) if has_error else None
    result = audit.sanitized_diagnostic(operation="provision", tenant_id=7, record_id=19, error=error)
    assert result == {"operation": "provision", "tenant_id": 7, "record_id": 19}
    scan.check_text(repr(result), source="diagnostic")
