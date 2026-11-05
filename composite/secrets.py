"""Encryption and safe logging helpers for stored composite secrets.

Call :func:`install_log_redaction` after configuring each composite logger's
handlers, and call it again when adding handlers. This protects the logger and
its currently attached handlers; it cannot secure handlers added in the future.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import logging
import secrets

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class SecretError(ValueError):
    """A sanitized error raised by secret storage operations."""


@dataclass(frozen=True)
class EncryptedValue:
    """Versioned AES-GCM ciphertext; contains no retained plaintext."""

    version: int
    key_id: str
    nonce: bytes
    ciphertext: bytes


class SecretBox:
    """Encrypt secrets with explicitly supplied, authorized AES keys."""

    def __init__(self, keys: dict[str, bytes], current_key_id: str) -> None:
        try:
            copied = dict(keys)
            if not copied or current_key_id not in copied:
                raise ValueError
            for key in copied.values():
                if not isinstance(key, bytes) or len(key) not in (16, 24, 32):
                    raise ValueError
            current_key_id.encode("utf-8")
        except Exception:
            raise SecretError("Invalid secret key configuration") from None
        self._keys = copied
        self._current_key_id = current_key_id

    def encrypt(self, plaintext: str) -> EncryptedValue:
        try:
            if not isinstance(plaintext, str):
                raise ValueError
            key_id = self._current_key_id
            aad = b"shopvpn:secrets:v1:" + key_id.encode("utf-8")
            nonce = secrets.token_bytes(12)
            ciphertext = AESGCM(self._keys[key_id]).encrypt(
                nonce, plaintext.encode("utf-8"), aad
            )
            return EncryptedValue(1, key_id, nonce, ciphertext)
        except Exception:
            raise SecretError("Secret encryption failed") from None

    def decrypt(self, value: EncryptedValue) -> str:
        try:
            if not isinstance(value, EncryptedValue) or value.version != 1:
                raise ValueError
            key = self._keys.get(value.key_id)
            if key is None:
                raise ValueError
            aad = b"shopvpn:secrets:v1:" + value.key_id.encode("utf-8")
            plaintext = AESGCM(key).decrypt(value.nonce, value.ciphertext, aad)
            return plaintext.decode("utf-8")
        except Exception:
            raise SecretError("Secret decryption failed") from None


def token_digest(token: str) -> str:
    """Return the lowercase SHA-256 hex digest of the exact UTF-8 token."""
    try:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()
    except Exception:
        raise SecretError("Token digest failed") from None


_STANDARD_RECORD_FIELDS = frozenset(logging.makeLogRecord({}).__dict__)
_TRUSTED_FIELDS = ("operation", "tenant_id", "record_id")


class SecretRedactionFilter(logging.Filter):
    """Keep standard metadata and trusted identifiers, discarding log content."""

    def filter(self, record: logging.LogRecord) -> bool:
        trusted = {name: getattr(record, name) for name in _TRUSTED_FIELDS if hasattr(record, name)}
        for name in tuple(record.__dict__):
            if name not in _STANDARD_RECORD_FIELDS and name not in _TRUSTED_FIELDS:
                delattr(record, name)
        record.msg = "[redacted]"
        record.args = ()
        record.exc_info = None
        record.exc_text = None
        record.stack_info = None
        record.__dict__.pop("message", None)
        record.__dict__.update(trusted)
        return True


def install_log_redaction(logger: logging.Logger) -> None:
    """Install redaction on a composite logger and its current handlers."""
    if not any(isinstance(item, SecretRedactionFilter) for item in logger.filters):
        logger.addFilter(SecretRedactionFilter())
    for handler in logger.handlers:
        if not any(isinstance(item, SecretRedactionFilter) for item in handler.filters):
            handler.addFilter(SecretRedactionFilter())
