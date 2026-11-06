"""Executable T047a reference only; never installed into the working service.

Trusted adapters supply transport events, installation identity and stored owner
metadata. This guard does not authenticate arbitrary Python objects, implement
business commands, or replace shop eligibility checks.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Principal:
    identity_domain: str
    authenticated_actor_id: int
    tenant_installation_id: str
    role: str
    authenticated_interface: str


class AuthorityError(Exception):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def telegram_principal(event, *, tenant_installation_id):
    sender = getattr(event, "from_user", None)
    actor = getattr(sender, "id", None)
    if actor is None:
        raise AuthorityError("unauthenticated")
    return Principal("telegram", actor, tenant_installation_id, "customer", "telegram")


def authorize_customer_resource(principal, *, main_installation_id,
                                resource_tenant_installation_id, customer_telegram_id):
    if (principal.identity_domain != "telegram"
            or principal.authenticated_interface != "telegram"
            or principal.role != "customer"
            or principal.tenant_installation_id != main_installation_id):
        raise AuthorityError("forbidden")
    if (resource_tenant_installation_id != principal.tenant_installation_id
            or customer_telegram_id != principal.authenticated_actor_id):
        raise AuthorityError("not_found")
