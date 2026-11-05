"""Domain types: plans, subscriptions, child credentials and their states."""

from dataclasses import dataclass
from enum import StrEnum


class Lifecycle(StrEnum):
    PREPARING = "preparing"
    FULFILLED = "fulfilled"
    CANCEL_PENDING = "cancel_pending"
    CANCELLED = "cancelled"
    FAILED_UNFULFILLED = "failed_unfulfilled"


class CancelWaitKind(StrEnum):
    AUTHORIZED_RENEWAL = "authorized_renewal"
    INITIAL_PROVISIONING = "initial_provisioning"


class ConfirmedAccess(StrEnum):
    UNKNOWN = "unknown"
    PARTIAL = "partial"
    CONFIRMED_ELIGIBLE = "confirmed_eligible"
    CONFIRMED_FRESH_AUTH_DENIED = "confirmed_fresh_auth_denied"


class TokenStatus(StrEnum):
    CANDIDATE = "candidate"
    CURRENT = "current"
    REVOKED = "revoked"
    SUPERSEDED = "superseded"


class GenerationState(StrEnum):
    PREPARING = "preparing"
    COMPLETE_VERIFIED = "complete_verified"
    PUBLISHED = "published"
    RETIRED = "retired"
    BLOCKED_UNCERTAIN = "blocked_uncertain"


class RemoteWorkStatus(StrEnum):
    QUEUED = "queued"
    DISPATCHED = "dispatched"
    UNCERTAIN = "uncertain"
    CONFIRMED = "confirmed"
    MANUAL_HOLD = "manual_hold"


class SweepOutcome(StrEnum):
    CONSISTENT = "consistent"
    DIVERGED = "diverged"
    UNKNOWN = "unknown"


class ChildDesiredState(StrEnum):
    ENABLED = "enabled"
    DISABLED = "disabled"
    REMOVED = "removed"


class Publication(StrEnum):
    NOT_FOUND = "not_found"
    UNAVAILABLE = "unavailable"
    STATUS_ONLY = "status_only"
    COMPLETE_LIST = "complete_list"


@dataclass(frozen=True)
class SubscriptionAccessFacts:
    lifecycle: Lifecycle
    available_at: int | None
    expires_at: int | None
    allowance_bytes: int
    used_bytes: int
    customer_disabled: bool
    owner_suspended: bool
    reporting_suspended: bool
    recovery_hold_case: str | None
    replacement_delivery_block: bool
    initial_delivery_block: bool
    cancel_accepted_at: int | None
    cancel_wait_kind: CancelWaitKind | None
    cancel_final_started_at: int | None
    has_published_generation: bool


@dataclass(frozen=True)
class AttachmentReadBack:
    observed_at: int
    matches: bool


@dataclass(frozen=True)
class UncertainRequest:
    carries: ChildDesiredState
    quarantine_until: int


@dataclass(frozen=True)
class ChildAccessEvidence:
    desired: ChildDesiredState
    latest_write_at: int
    read_backs: tuple[AttachmentReadBack | None, ...]
    runtime_required: bool
    runtime_evidence: bool
    uncertain_requests: tuple[UncertainRequest, ...]


def is_expired(facts: SubscriptionAccessFacts, now: int) -> bool:
    if facts.expires_at is None:
        return False
    return now >= facts.expires_at


def is_exhausted(facts: SubscriptionAccessFacts) -> bool:
    return facts.used_bytes >= facts.allowance_bytes


def desired_access(facts: SubscriptionAccessFacts, now: int) -> bool:
    if facts.lifecycle == Lifecycle.PREPARING:
        pass
    elif facts.lifecycle == Lifecycle.FULFILLED:
        pass
    elif (
        facts.lifecycle == Lifecycle.CANCEL_PENDING
        and facts.cancel_wait_kind == CancelWaitKind.AUTHORIZED_RENEWAL
    ):
        pass
    else:
        return False

    if facts.cancel_final_started_at is not None:
        return False
    if facts.initial_delivery_block:
        return False
    if facts.customer_disabled:
        return False
    if facts.owner_suspended:
        return False
    if facts.reporting_suspended:
        return False
    if facts.recovery_hold_case is not None:
        return False
    if is_expired(facts, now):
        return False
    if is_exhausted(facts):
        return False

    return True


def publication(facts: SubscriptionAccessFacts, token_status: TokenStatus) -> Publication:
    if (
        token_status in (TokenStatus.REVOKED, TokenStatus.SUPERSEDED)
        or facts.lifecycle in (Lifecycle.CANCELLED, Lifecycle.FAILED_UNFULFILLED)
        or facts.cancel_final_started_at is not None
    ):
        return Publication.NOT_FOUND

    if (
        token_status == TokenStatus.CANDIDATE
        or facts.lifecycle == Lifecycle.PREPARING
        or (
            facts.lifecycle == Lifecycle.CANCEL_PENDING
            and facts.cancel_wait_kind == CancelWaitKind.INITIAL_PROVISIONING
        )
        or facts.initial_delivery_block
        or facts.replacement_delivery_block
        or facts.recovery_hold_case is not None
    ):
        return Publication.UNAVAILABLE

    if facts.owner_suspended:
        return Publication.STATUS_ONLY

    is_previously_fulfilled = facts.lifecycle == Lifecycle.FULFILLED or (
        facts.lifecycle == Lifecycle.CANCEL_PENDING
        and facts.cancel_wait_kind == CancelWaitKind.AUTHORIZED_RENEWAL
    )
    if is_previously_fulfilled and facts.has_published_generation:
        return Publication.COMPLETE_LIST

    return Publication.UNAVAILABLE


def confirmed_access(evidence: ChildAccessEvidence, now: int) -> ConfirmedAccess:
    total_attachments = len(evidence.read_backs)
    if total_attachments == 0:
        return ConfirmedAccess.UNKNOWN

    qualifying_count = sum(
        1
        for rb in evidence.read_backs
        if rb is not None
        and rb.matches is True
        and rb.observed_at > evidence.latest_write_at
    )

    if qualifying_count == 0:
        return ConfirmedAccess.UNKNOWN

    if qualifying_count < total_attachments:
        return ConfirmedAccess.PARTIAL

    if evidence.runtime_required and not evidence.runtime_evidence:
        return ConfirmedAccess.PARTIAL

    for req in evidence.uncertain_requests:
        is_harmless = (
            req.carries == evidence.desired
            or (
                evidence.desired in (ChildDesiredState.DISABLED, ChildDesiredState.REMOVED)
                and req.carries in (ChildDesiredState.DISABLED, ChildDesiredState.REMOVED)
            )
        )
        if not is_harmless and now < req.quarantine_until:
            return ConfirmedAccess.PARTIAL

    if evidence.desired == ChildDesiredState.ENABLED:
        return ConfirmedAccess.CONFIRMED_ELIGIBLE
    return ConfirmedAccess.CONFIRMED_FRESH_AUTH_DENIED
