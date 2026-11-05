"""T044 diagnostic oracle only; audit persistence belongs to T046."""


def sanitized_diagnostic(*, operation, tenant_id, record_id, error=None):
    return {"operation": operation, "tenant_id": tenant_id, "record_id": record_id}
