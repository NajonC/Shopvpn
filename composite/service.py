"""The application boundary for authenticated principals and command records.

Adapters establish principals from authenticated transports. Later commands must
load persisted ownership and apply shop eligibility before effects. Command
results contain only caller-sanitized public structured values; never pass raw
provider payloads, secrets, or private audit context in their summary, usage,
reason, or support fields. These records do not authorize business commands or
infer confirmed remote state.
"""

from collections.abc import Mapping
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Principal:
    identity_domain: str
    authenticated_actor_id: int
    tenant_installation_id: str
    role: str
    authenticated_interface: str


class AuthorityError(Exception):
    """An opaque authorization failure with a stable public code."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def telegram_principal(event, *, tenant_installation_id: str) -> Principal:
    """Map an already authenticated Telegram event to its sender principal."""
    sender = getattr(event, "from_user", None)
    actor_id = getattr(sender, "id", None)
    if actor_id is None:
        raise AuthorityError("unauthenticated")
    return Principal(
        "telegram", actor_id, tenant_installation_id, "customer", "telegram"
    )


def authorize_customer_resource(
    principal: Principal,
    *,
    main_installation_id: str,
    resource_tenant_installation_id: str,
    customer_telegram_id: int,
) -> None:
    """Check customer domain and persisted resource ownership without effects."""
    if (
        principal.identity_domain != "telegram"
        or principal.authenticated_interface != "telegram"
        or principal.role != "customer"
        or principal.tenant_installation_id != main_installation_id
    ):
        raise AuthorityError("forbidden")
    if (
        resource_tenant_installation_id != principal.tenant_installation_id
        or customer_telegram_id != principal.authenticated_actor_id
    ):
        raise AuthorityError("not_found")


def web_principal(
    admin,
    *,
    main_installation_id: str,
    main_owner_web_admin_id: int,
) -> Principal:
    """Map authenticated main-tenant owner data to its configured web identity."""
    if not isinstance(admin, Mapping):
        raise AuthorityError("forbidden")
    if "mobile_token_id" in admin:
        raise AuthorityError("forbidden")

    try:
        actor_id = admin["id"]
        tenant = admin["tenant"]
        role = admin["role"]
    except (KeyError, TypeError):
        raise AuthorityError("forbidden") from None

    if (
        tenant != ""
        or role != "owner"
        or type(actor_id) is not int
        or type(main_owner_web_admin_id) is not int
        or main_owner_web_admin_id <= 0
        or actor_id != main_owner_web_admin_id
    ):
        raise AuthorityError("forbidden")

    return Principal(
        "web_admin", actor_id, main_installation_id, "owner", "web"
    )


@dataclass(frozen=True)
class CommandContext:
    request_key: str
    observed_resource_revision: int | None = None
    audit_reason: str | None = field(default=None, repr=False)


@dataclass(frozen=True)
class CommandResult:
    operation_id: str
    state: str
    original_clock_at: int
    subscription_id: str | None = None
    checkout_id: str | None = None
    financial_state: str | None = None
    availability_state: str | None = None
    desired_restrictions: tuple[str, ...] = ()
    confirmed_remote_summary: str = ""
    target_at: int | None = None
    escalation_at: int | None = None
    qualified_usage: Mapping[str, object] | None = None
    retry_same_operation: bool = False
    public_reason: str = ""
    support_action: str = ""
