"""Immutable audit events and sanitized diagnostics (T046).

Provides an immutable audit-event writer and sanitized diagnostic builder
used across composite operations.

Security & Trust Boundary:
- Event metadata and the three diagnostic identifiers (operation, tenant_id,
  record_id) are trusted, already-authorized structured inputs.
- Callers MUST NOT supply secrets, credentials, or session tokens in reason,
  evidence_ref, or diagnostic identifiers.
- Heuristic secret detection is intentionally not attempted on trusted metadata.
- Private reason/evidence text persists exactly (including quotes), is never logged,
  and must not be reused for public subscription output.
- Arbitrary error payloads and exceptions are dropped and never stored or stringified.
- Database write errors propagate as sanitized AuditWriteError with no SQL parameters
  or backend error messages exposed.
- Transactions are caller-owned: caller manages BEGIN, COMMIT, and ROLLBACK.
"""

from collections.abc import Mapping
from dataclasses import dataclass
import json
import sqlite3
from typing import Any

__all__ = [
    "AuditEvent",
    "AuditWriteError",
    "sanitized_diagnostic",
    "write_audit_event",
]

_INSERT_AUDIT_EVENT_SQL = """INSERT INTO composite_audit_events (
    event_id,
    occurred_at,
    actor_domain,
    actor_id,
    action,
    resource_kind,
    resource_id,
    reason,
    evidence_ref,
    diagnostics
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""


class AuditWriteError(Exception):
    """Sanitized failure writing an immutable audit event."""

    def __init__(self, message: str = "failed to record audit event") -> None:
        super().__init__(message)


@dataclass(frozen=True)
class AuditEvent:
    """Immutable audit event record."""

    event_id: str
    occurred_at: int
    actor_domain: str
    actor_id: str
    action: str
    resource_kind: str
    resource_id: str
    reason: str | None = None
    evidence_ref: str | None = None


def sanitized_diagnostic(
    *,
    operation: str,
    tenant_id: int,
    record_id: int,
    error: BaseException | None = None,
) -> dict[str, object]:
    """Rebuild a diagnostic dictionary containing strictly operation, tenant_id, and record_id.

    The error parameter is accepted for call-site convenience and dropped
    without inspection or stringification to prevent secret leakage.
    """
    del error
    return {
        "operation": operation,
        "tenant_id": tenant_id,
        "record_id": record_id,
    }


def write_audit_event(
    conn: sqlite3.Connection,
    event: AuditEvent,
    *,
    diagnostic: Mapping[str, Any] | None = None,
) -> str:
    """Insert an immutable audit event into composite_audit_events.

    Performs a single parameter-bound INSERT and returns event.event_id upon success.
    Caller owns transaction boundaries (no COMMIT, ROLLBACK, or BEGIN performed here).
    Database errors are caught and raised as sanitized AuditWriteError.
    """
    diagnostics_payload: str | None = None
    if diagnostic is not None:
        sanitized = {
            "operation": diagnostic["operation"],
            "tenant_id": diagnostic["tenant_id"],
            "record_id": diagnostic["record_id"],
        }
        diagnostics_payload = json.dumps(sanitized)

    params = (
        event.event_id,
        event.occurred_at,
        event.actor_domain,
        event.actor_id,
        event.action,
        event.resource_kind,
        event.resource_id,
        event.reason,
        event.evidence_ref,
        diagnostics_payload,
    )

    try:
        conn.execute(_INSERT_AUDIT_EVENT_SQL, params)
    except sqlite3.Error:
        raise AuditWriteError() from None

    return event.event_id
