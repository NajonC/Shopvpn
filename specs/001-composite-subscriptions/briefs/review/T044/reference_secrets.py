"""Executable T044 test oracle; NOT a production secrets implementation."""
from dataclasses import dataclass
import hashlib
import logging
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class SecretError(ValueError):
    pass


@dataclass(frozen=True)
class EncryptedValue:
    version: int
    key_id: str
    nonce: bytes
    ciphertext: bytes


class SecretBox:
    def __init__(self, keys, current_key_id):
        if current_key_id not in keys:
            raise SecretError("missing active key")
        if any(len(key) not in (16, 24, 32) for key in keys.values()):
            raise SecretError("invalid key size")
        self.keys = dict(keys)
        self.current_key_id = current_key_id

    def encrypt(self, plaintext):
        key_id = self.current_key_id
        nonce = os.urandom(12)
        aad = b"shopvpn:secrets:v1:" + key_id.encode("utf-8")
        ciphertext = AESGCM(self.keys[key_id]).encrypt(nonce, plaintext.encode("utf-8"), aad)
        return EncryptedValue(1, key_id, nonce, ciphertext)

    def decrypt(self, value):
        if value.version != 1:
            raise SecretError("unsupported version")
        try:
            key = self.keys[value.key_id]
            aad = b"shopvpn:secrets:v1:" + value.key_id.encode("utf-8")
            result = AESGCM(key).decrypt(value.nonce, value.ciphertext, aad)
            return result.decode("utf-8")
        except Exception:
            raise SecretError("decryption failed") from None


def token_digest(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


# Only these fields survive, since arbitrary extra values can hold credentials.
_STANDARD = set(logging.makeLogRecord({}).__dict__)
_CONTEXT = {"operation", "tenant_id", "record_id"}


class SecretRedactionFilter(logging.Filter):
    def filter(self, record):
        record.msg = "[redacted]"
        record.args = ()
        record.exc_info = None
        record.exc_text = None
        record.stack_info = None
        for key in list(vars(record)):
            if key not in _STANDARD | _CONTEXT:
                delattr(record, key)
        return True


def install_log_redaction(logger):
    if not any(isinstance(f, SecretRedactionFilter) for f in logger.filters):
        logger.addFilter(SecretRedactionFilter())
    for handler in logger.handlers:
        if not any(isinstance(f, SecretRedactionFilter) for f in handler.filters):
            handler.addFilter(SecretRedactionFilter())
