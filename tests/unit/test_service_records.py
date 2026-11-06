"""T048 records retain command progress without exposing private audit context."""

from dataclasses import FrozenInstanceError

import pytest

from composite import service


def test_authenticated_principal_cannot_be_reassigned_after_authorization():
    principal = service.Principal("telegram", 101, "synthetic-main", "customer", "telegram")
    with pytest.raises(FrozenInstanceError):
        principal.authenticated_actor_id = 202
    assert principal.authenticated_actor_id == 101


def test_command_context_retains_private_reason_but_excludes_it_from_repr(caplog):
    context = service.CommandContext(
        "synthetic-request", observed_resource_revision=7,
        audit_reason="synthetic-private-investigation",
    )
    assert (context.request_key, context.observed_resource_revision, context.audit_reason) == (
        "synthetic-request", 7, "synthetic-private-investigation",
    )
    assert context.audit_reason not in repr(context)
    assert context.audit_reason not in str(context)
    with pytest.raises(FrozenInstanceError):
        context.request_key = "another-request"
    default = service.CommandContext("synthetic-default")
    assert default.observed_resource_revision is None and default.audit_reason is None
    assert caplog.records == []


@pytest.mark.parametrize("state", ["pending", "partial", "uncertain", "confirmed"])
def test_result_preserves_distinct_progress_without_claiming_confirmation(state):
    result = service.CommandResult(
        operation_id="synthetic-operation", state=state, original_clock_at=1000,
    )
    assert (result.operation_id, result.state, result.original_clock_at) == (
        "synthetic-operation", state, 1000,
    )
    assert result.subscription_id is None and result.checkout_id is None
    assert result.financial_state is None and result.availability_state is None
    assert result.desired_restrictions == () and result.confirmed_remote_summary == ""
    assert result.target_at is None and result.escalation_at is None
    assert result.qualified_usage is None and result.retry_same_operation is False
    assert result.public_reason == "" and result.support_action == ""
    with pytest.raises(FrozenInstanceError):
        result.state = "confirmed"


def test_result_retains_original_clocks_restrictions_and_qualified_progress():
    result = service.CommandResult(
        operation_id="synthetic-operation", subscription_id="synthetic-subscription",
        checkout_id="synthetic-checkout", state="partial", financial_state="confirmed",
        availability_state="pending", desired_restrictions=("owner_suspended", "customer_disabled"),
        confirmed_remote_summary="2 of 3 disabled", original_clock_at=1000,
        target_at=61000, escalation_at=901000,
        qualified_usage={"used_bytes": 123, "fresh": False}, retry_same_operation=True,
        public_reason="Access change pending", support_action="Contact support",
    )
    assert (result.subscription_id, result.checkout_id) == ("synthetic-subscription", "synthetic-checkout")
    assert (result.state, result.financial_state, result.availability_state) == ("partial", "confirmed", "pending")
    assert result.desired_restrictions == ("owner_suspended", "customer_disabled")
    assert result.confirmed_remote_summary == "2 of 3 disabled"
    assert (result.original_clock_at, result.target_at, result.escalation_at) == (1000, 61000, 901000)
    assert result.qualified_usage == {"used_bytes": 123, "fresh": False}
    assert result.retry_same_operation is True
    assert (result.public_reason, result.support_action) == ("Access change pending", "Contact support")


@pytest.mark.parametrize("private_field", ["raw_provider_payload", "audit_reason", "subscription_url"])
def test_general_result_has_no_raw_private_or_url_delivery_field(private_field):
    # General progress is a closed record. Authorized URL delivery is a later,
    # separate operation; it must not silently acquire arbitrary payload fields.
    with pytest.raises(TypeError):
        service.CommandResult(
            operation_id="synthetic-operation", state="pending", original_clock_at=1000,
            **{private_field: "synthetic-private-value"},
        )
