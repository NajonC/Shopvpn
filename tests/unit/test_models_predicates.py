"""Domain enums and the access, publication and confirmation predicates (T042).

These tests pin what T043 builds in `composite/models.py` (data-model §3, §4
and §10; contracts/subscription-http.md "Gate order and response"; RD-10
RX-D8). The predicates are pure: they read the facts they are given and the
time `now` (UTC epoch milliseconds) and touch no database, clock or network.

Interface (all names in `composite.models`):

- String enums whose values are the stored strings: `Lifecycle`,
  `CancelWaitKind`, `ConfirmedAccess`, `TokenStatus`, `GenerationState`,
  `RemoteWorkStatus`, `SweepOutcome`, `ChildDesiredState`, and the result enum
  `Publication` (`NOT_FOUND`, `UNAVAILABLE`, `STATUS_ONLY`, `COMPLETE_LIST`).
- Frozen dataclasses `SubscriptionAccessFacts`, `AttachmentReadBack`,
  `UncertainRequest` and `ChildAccessEvidence` with the fields listed in
  `test_fact_types_are_frozen_and_have_these_fields`.
- `is_expired(facts, now) -> bool`, `is_exhausted(facts) -> bool`,
  `desired_access(facts, now) -> bool`,
  `publication(facts, token_status) -> Publication` and
  `confirmed_access(evidence, now) -> ConfirmedAccess`.

Cases the specs leave open are deliberately not pinned here (see the T042
brief): access while `preparing`, whether a delivery block restricts access,
and whether an unconfirmed child with matching read-backs is `unknown` or
`partial`.
"""

import dataclasses

import pytest

import composite.models as m

NOW = 1_767_225_600_000  # 2026-01-01T00:00:00Z
DAY = 86_400_000
GIB = 1_073_741_824
ALLOWANCE = 50 * GIB  # 53,687,091,200 bytes
USED = 10 * GIB
AVAILABLE_AT = NOW - DAY
EXPIRES_AT = NOW + 29 * DAY
WRITE_AT = NOW - 20_000  # dispatch of the child's latest write
READ_AT = NOW - 10_000  # a read-back received after that write
IN_QUARANTINE = NOW + 5_000  # quarantine_until of a request still in quarantine


def _facts(**changes):
    values = {
        "lifecycle": "fulfilled",
        "available_at": AVAILABLE_AT,
        "expires_at": EXPIRES_AT,
        "allowance_bytes": ALLOWANCE,
        "used_bytes": USED,
        "customer_disabled": False,
        "owner_suspended": False,
        "reporting_suspended": False,
        "recovery_hold_case": None,
        "replacement_delivery_block": False,
        "initial_delivery_block": False,
        "cancel_accepted_at": None,
        "cancel_wait_kind": None,
        "cancel_final_started_at": None,
        "has_published_generation": True,
    }
    values.update(changes)
    values["lifecycle"] = m.Lifecycle(values["lifecycle"])
    if values["cancel_wait_kind"] is not None:
        values["cancel_wait_kind"] = m.CancelWaitKind(values["cancel_wait_kind"])
    return m.SubscriptionAccessFacts(**values)


# Pending permanent cancellation while an authorized renewal resolves.
RENEWAL_WAIT = {
    "lifecycle": "cancel_pending",
    "cancel_accepted_at": NOW - 60_000,
    "cancel_wait_kind": "authorized_renewal",
}
# The renewal resolved, so the final cancellation stage has started.
FINAL_AFTER_RENEWAL = {**RENEWAL_WAIT, "cancel_final_started_at": NOW - 30_000}
# No operation to wait for: the final stage starts at acceptance.
FINAL_AT_ACCEPTANCE = {
    "lifecycle": "cancel_pending",
    "cancel_accepted_at": NOW - 60_000,
    "cancel_final_started_at": NOW - 60_000,
}
CANCELLED = {
    "lifecycle": "cancelled",
    "cancel_accepted_at": NOW - 600_000,
    "cancel_final_started_at": NOW - 600_000,
}
PREPARING = {
    "lifecycle": "preparing",
    "available_at": None,
    "expires_at": None,
    "used_bytes": 0,
    "has_published_generation": False,
}
# Cancellation accepted before initial availability (FR-026).
INITIAL_CANCEL = {
    **PREPARING,
    "lifecycle": "cancel_pending",
    "initial_delivery_block": True,
    "cancel_accepted_at": NOW - 60_000,
    "cancel_wait_kind": "initial_provisioning",
}
FAILED_UNFULFILLED = {
    **PREPARING,
    "lifecycle": "failed_unfulfilled",
    "initial_delivery_block": True,
}
# A late success must never fulfil (FR-024; FR-026), even if a generation was
# marked published.
LATE_GENERATION = {"has_published_generation": True}

EXPIRED = {"expires_at": NOW}
EXHAUSTED = {"used_bytes": ALLOWANCE}
RESTRICTIONS = {
    "customer_disabled": {"customer_disabled": True},
    "owner_suspended": {"owner_suspended": True},
    "reporting_suspended": {"reporting_suspended": True},
    "recovery_hold": {"recovery_hold_case": "case-1"},
}


# Enums ----------------------------------------------------------------------

ENUM_VALUES = {
    # data-model §3
    "Lifecycle": ("preparing", "fulfilled", "cancel_pending", "cancelled", "failed_unfulfilled"),
    "CancelWaitKind": ("authorized_renewal", "initial_provisioning"),
    "ConfirmedAccess": ("unknown", "partial", "confirmed_eligible", "confirmed_fresh_auth_denied"),
    # data-model §4
    "TokenStatus": ("candidate", "current", "revoked", "superseded"),
    "GenerationState": ("preparing", "complete_verified", "published", "retired", "blocked_uncertain"),
    # data-model §10
    "RemoteWorkStatus": ("queued", "dispatched", "uncertain", "confirmed", "manual_hold"),
    "SweepOutcome": ("consistent", "diverged", "unknown"),
    # composite_children.desired_state (data-model §5 schema)
    "ChildDesiredState": ("enabled", "disabled", "removed"),
}


@pytest.mark.parametrize("enum_name", sorted(ENUM_VALUES))
def test_state_enums_copy_the_stored_values(enum_name):
    enum = getattr(m, enum_name)
    values = ENUM_VALUES[enum_name]
    assert [(member.name, member.value) for member in enum] == [(v.upper(), v) for v in values]
    for value in values:
        assert enum(value) is enum[value.upper()]
        assert enum[value.upper()] == value  # a str enum, stored as its value


def test_publication_results():
    assert [member.name for member in m.Publication] == [
        "NOT_FOUND",
        "UNAVAILABLE",
        "STATUS_ONLY",
        "COMPLETE_LIST",
    ]


def test_fact_types_are_frozen_and_have_these_fields():
    fields = {
        m.SubscriptionAccessFacts: [
            "lifecycle",
            "available_at",
            "expires_at",
            "allowance_bytes",
            "used_bytes",
            "customer_disabled",
            "owner_suspended",
            "reporting_suspended",
            "recovery_hold_case",
            "replacement_delivery_block",
            "initial_delivery_block",
            "cancel_accepted_at",
            "cancel_wait_kind",
            "cancel_final_started_at",
            "has_published_generation",
        ],
        m.AttachmentReadBack: ["observed_at", "matches"],
        m.UncertainRequest: ["carries", "quarantine_until"],
        m.ChildAccessEvidence: [
            "desired",
            "latest_write_at",
            "read_backs",
            "runtime_required",
            "runtime_evidence",
            "uncertain_requests",
        ],
    }
    for cls, names in fields.items():
        assert [field.name for field in dataclasses.fields(cls)] == names, cls.__name__
    # Independent restriction flags, never one mutable `enabled` flag.
    assert "enabled" not in fields[m.SubscriptionAccessFacts]
    facts = _facts()
    with pytest.raises(dataclasses.FrozenInstanceError):
        facts.customer_disabled = True


# Derived expired and exhausted ----------------------------------------------


@pytest.mark.parametrize(
    ("now", "expected"),
    [(EXPIRES_AT - 1, False), (EXPIRES_AT, True), (EXPIRES_AT + 1, True)],
    ids=["before", "at_expiry", "after"],
)
def test_expired_from_the_common_expiry(now, expected):
    assert m.is_expired(_facts(), now) is expected


@pytest.mark.parametrize(
    ("used", "expected"),
    [(ALLOWANCE - 1, False), (ALLOWANCE, True), (ALLOWANCE + 512 * 1_048_576, True)],
    ids=["one_byte_left", "at_threshold", "overrun"],
)
def test_exhausted_at_or_above_the_purchased_bytes(used, expected):
    assert m.is_exhausted(_facts(used_bytes=used)) is expected


# desired_access ---------------------------------------------------------------


def test_fulfilled_service_has_access():
    assert m.desired_access(_facts(), NOW) is True


def test_one_byte_and_one_millisecond_left_still_have_access():
    facts = _facts(expires_at=NOW + 1, used_bytes=ALLOWANCE - 1)
    assert m.desired_access(facts, NOW) is True


@pytest.mark.parametrize(
    "changes",
    [EXPIRED, EXHAUSTED, *RESTRICTIONS.values()],
    ids=["expired", "exhausted", *RESTRICTIONS],
)
def test_each_restriction_alone_removes_access(changes):
    assert m.desired_access(_facts(**changes), NOW) is False


def test_pending_cancellation_during_authorized_renewal_keeps_access():
    assert m.desired_access(_facts(**RENEWAL_WAIT), NOW) is True


@pytest.mark.parametrize(
    "changes",
    [EXPIRED, EXHAUSTED, *RESTRICTIONS.values()],
    ids=["expired", "exhausted", *RESTRICTIONS],
)
def test_renewal_wait_access_is_not_unconditional(changes):
    assert m.desired_access(_facts(**RENEWAL_WAIT, **changes), NOW) is False


@pytest.mark.parametrize(
    "changes",
    [
        FINAL_AFTER_RENEWAL,
        FINAL_AT_ACCEPTANCE,
        CANCELLED,
        FAILED_UNFULFILLED,
        {**FAILED_UNFULFILLED, **LATE_GENERATION},
    ],
    ids=["final_after_renewal", "final_at_acceptance", "cancelled", "failed_unfulfilled", "failed_late_generation"],
)
def test_no_access_after_final_cancellation_or_failed_initial(changes):
    assert m.desired_access(_facts(**changes), NOW) is False


# publication (contracts/subscription-http.md gate order) --------------------


def _publish(changes=None, token="current"):
    return m.publication(_facts(**(changes or {})), m.TokenStatus(token))


@pytest.mark.parametrize(
    "changes",
    [
        {},
        EXHAUSTED,
        {"expires_at": NOW - DAY},
        {"customer_disabled": True},
        {"reporting_suspended": True},
        RENEWAL_WAIT,
        {**RENEWAL_WAIT, **EXHAUSTED, "customer_disabled": True, "reporting_suspended": True},
    ],
    ids=[
        "fulfilled",
        "exhausted",
        "expired",
        "customer_disabled",
        "reporting_suspended",
        "renewal_wait",
        "renewal_wait_exhausted_disabled_reporting",
    ],
)
def test_complete_list_is_kept_through_ordinary_restrictions(changes):
    assert _publish(changes) is m.Publication.COMPLETE_LIST


@pytest.mark.parametrize(
    "changes",
    [
        {"owner_suspended": True},
        {"owner_suspended": True, **EXHAUSTED, "customer_disabled": True, "reporting_suspended": True},
        {"owner_suspended": True, **RENEWAL_WAIT},
        {"owner_suspended": True, "has_published_generation": False},
    ],
    ids=["owner_suspended", "with_other_restrictions", "during_renewal_wait", "no_published_generation"],
)
def test_owner_suspension_is_status_only(changes):
    assert _publish(changes) is m.Publication.STATUS_ONLY


@pytest.mark.parametrize(
    ("changes", "token"),
    [
        ({}, "revoked"),
        ({}, "superseded"),
        ({"owner_suspended": True}, "revoked"),
        (FINAL_AFTER_RENEWAL, "current"),
        (FINAL_AT_ACCEPTANCE, "current"),
        ({**FINAL_AFTER_RENEWAL, "owner_suspended": True}, "current"),
        (CANCELLED, "revoked"),
    ],
    ids=[
        "revoked",
        "superseded",
        "revoked_owner_suspended",
        "final_after_renewal",
        "final_at_acceptance",
        "final_owner_suspended",
        "cancelled",
    ],
)
def test_invalid_token_or_final_cancellation_is_not_found(changes, token):
    assert _publish(changes, token) is m.Publication.NOT_FOUND


@pytest.mark.parametrize(
    "changes",
    [
        PREPARING,
        {**PREPARING, **LATE_GENERATION},
        INITIAL_CANCEL,
        {**INITIAL_CANCEL, **LATE_GENERATION},
        {"replacement_delivery_block": True},
        {"recovery_hold_case": "case-1"},
        {"has_published_generation": False},
    ],
    ids=[
        "preparing",
        "preparing_late_generation",
        "initial_cancel",
        "initial_cancel_late_generation",
        "replacement_pending",
        "recovery_hold",
        "no_published_generation",
    ],
)
def test_blocked_or_incomplete_delivery_is_unavailable(changes):
    assert _publish(changes) is m.Publication.UNAVAILABLE


@pytest.mark.parametrize(
    "changes",
    [FAILED_UNFULFILLED, {**FAILED_UNFULFILLED, **LATE_GENERATION}],
    ids=["failed_unfulfilled", "failed_late_generation"],
)
def test_failed_initial_never_serves_entries(changes):
    assert _publish(changes) in {m.Publication.NOT_FOUND, m.Publication.UNAVAILABLE}


# confirmed_access (RD-10, RX-D8) ----------------------------------------------


# Read-backs as (observed_at, matches); None means no read-back for that attachment.
MATCH = (READ_AT, True)
MISMATCH = (READ_AT, False)
AT_WRITE = (WRITE_AT, True)
BEFORE_WRITE = (WRITE_AT - 1, True)


def _evidence(desired, read_backs=(MATCH,), *, runtime_required=False, runtime_evidence=False, requests=()):
    return m.ChildAccessEvidence(
        desired=m.ChildDesiredState(desired),
        latest_write_at=WRITE_AT,
        read_backs=tuple(
            None if read is None else m.AttachmentReadBack(observed_at=read[0], matches=read[1])
            for read in read_backs
        ),
        runtime_required=runtime_required,
        runtime_evidence=runtime_evidence,
        uncertain_requests=tuple(
            m.UncertainRequest(carries=m.ChildDesiredState(carries), quarantine_until=until)
            for carries, until in requests
        ),
    )


CONFIRMED_FOR = {
    "enabled": "confirmed_eligible",
    "disabled": "confirmed_fresh_auth_denied",
    "removed": "confirmed_fresh_auth_denied",
}


def _confirmed(evidence):
    return m.confirmed_access(evidence, NOW)


def _not_confirmed(evidence):
    return _confirmed(evidence) not in {
        m.ConfirmedAccess.CONFIRMED_ELIGIBLE,
        m.ConfirmedAccess.CONFIRMED_FRESH_AUTH_DENIED,
    }


@pytest.mark.parametrize("desired", sorted(CONFIRMED_FOR))
def test_matching_read_back_after_the_latest_write_confirms(desired):
    assert _confirmed(_evidence(desired)) is m.ConfirmedAccess(CONFIRMED_FOR[desired])
    three = _evidence(desired, (MATCH, (READ_AT - 5_000, True), (WRITE_AT + 1, True)))
    assert _confirmed(three) is m.ConfirmedAccess(CONFIRMED_FOR[desired])


@pytest.mark.parametrize(
    "read_back",
    [None, MISMATCH, AT_WRITE, BEFORE_WRITE],
    ids=["none", "mismatch", "at_the_write", "before_the_write"],
)
@pytest.mark.parametrize("desired", sorted(CONFIRMED_FOR))
def test_no_matching_read_back_after_the_latest_write_is_unknown(desired, read_back):
    assert _confirmed(_evidence(desired, (read_back,))) is m.ConfirmedAccess.UNKNOWN
    stale_three = (None, MISMATCH, AT_WRITE)
    assert _confirmed(_evidence(desired, stale_three)) is m.ConfirmedAccess.UNKNOWN


@pytest.mark.parametrize(
    "read_backs",
    [
        (MATCH, MATCH, None),
        (MATCH, MISMATCH, MATCH),
        (MATCH, BEFORE_WRITE, MATCH),
    ],
    ids=["one_unread", "one_mismatch", "one_before_the_write"],
)
@pytest.mark.parametrize("desired", sorted(CONFIRMED_FOR))
def test_some_attachments_matching_is_partial(desired, read_backs):
    assert _confirmed(_evidence(desired, read_backs)) is m.ConfirmedAccess.PARTIAL


@pytest.mark.parametrize("desired", sorted(CONFIRMED_FOR))
def test_runtime_evidence_where_required(desired):
    assert _not_confirmed(_evidence(desired, runtime_required=True))
    with_runtime = _evidence(desired, runtime_required=True, runtime_evidence=True)
    assert _confirmed(with_runtime) is m.ConfirmedAccess(CONFIRMED_FOR[desired])


@pytest.mark.parametrize(
    ("desired", "carries"),
    [
        ("enabled", "enabled"),
        ("disabled", "disabled"),
        ("removed", "removed"),
        ("disabled", "removed"),
        ("removed", "disabled"),
    ],
    ids=["same_enabled", "same_disabled", "same_removed", "delete_while_denied", "disable_while_removed"],
)
def test_request_that_cannot_undo_the_state_does_not_block(desired, carries):
    evidence = _evidence(desired, requests=[(carries, IN_QUARANTINE)])
    assert _confirmed(evidence) is m.ConfirmedAccess(CONFIRMED_FOR[desired])


@pytest.mark.parametrize(
    ("desired", "carries"),
    [
        ("disabled", "enabled"),
        ("removed", "enabled"),
        ("enabled", "disabled"),
        ("enabled", "removed"),
    ],
    ids=["enable_while_disabled", "enable_while_removed", "disable_while_enabled", "delete_while_enabled"],
)
def test_request_that_could_undo_the_state_blocks_until_its_quarantine_ends(desired, carries):
    for until in (IN_QUARANTINE, NOW + 1):
        assert _not_confirmed(_evidence(desired, requests=[(carries, until)])), until
    for until in (NOW, NOW - 1):
        evidence = _evidence(desired, requests=[(carries, until)])
        assert _confirmed(evidence) is m.ConfirmedAccess(CONFIRMED_FOR[desired]), until


def test_one_blocking_request_among_harmless_ones_blocks():
    harmless = [("disabled", IN_QUARANTINE), ("removed", IN_QUARANTINE), ("enabled", NOW)]
    denied = _evidence("disabled", requests=harmless)
    assert _confirmed(denied) is m.ConfirmedAccess.CONFIRMED_FRESH_AUTH_DENIED
    assert _not_confirmed(_evidence("disabled", requests=[*harmless, ("enabled", IN_QUARANTINE)]))

    eligible = _evidence("enabled", requests=[("enabled", IN_QUARANTINE), ("disabled", NOW - 1)])
    assert _confirmed(eligible) is m.ConfirmedAccess.CONFIRMED_ELIGIBLE
    assert _not_confirmed(_evidence("enabled", requests=[("enabled", IN_QUARANTINE), ("removed", NOW + 1)]))
