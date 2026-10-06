# Provider, remote work and accounting contracts

**Proposed optional capabilities**, through existing `get_provider(server)` and `BasePanelProvider`. Existing methods, registered identifiers, `PanelUserResult`, typed errors and `preserve_remaining` remain compatible. Other providers default to explicit `UnsupportedCapability`; no caller makes panel-specific HTTP or selects unsupported composite brand. This contract is provisional where E-001/G-A evidence is missing.

## Capability manifest and explicit child scope

`CompositeCapabilities {panel/core revisions, API dialect, TLS trust reference, explicit_auth, inactive_create, canonical_lookup, mutation_scope, absolute_update, runtime_confirmation, native_session_policy, meter_authority/topology, source_time/epoch/continuity, billing_boundary_evidence, counter_retention, strict_node_export, route_namespace_match, shared_restart_conditions}` is versioned and recorded against a **verified physical panel**, not guessed from `panel_type='3xui'` or inbound-list success. Absent/contradictory required capability blocks binding/sales. Source research versions are not automatically supported versions.

`ChildIntent {operation/subscription/child/generation IDs, physical panel, canonical email/key, explicit auth type+encrypted secret reference/fingerprint, exact inbound attachments, protocol/flow settings, owner-prepared route binding, desired_fields, desired_revision}` is durable before calls. It contains no customer-supplied routing rule. Composite current source HTTP must move to peer verification with configured trusted CA/certificate identity; transport/application failure has typed semantics and sanitized messages. Don't expose token/body/URI excerpts.

Selected child management avoids panel-side automatic reset/renewal and separate commercial allowances. Candidate zero native quota/expiry fields mean manager-controlled finite parent entitlement, not unlimited product. This field binding and disable/runtime behavior must pass capability checks before use. Creation is disabled until complete preparation and legitimate access convergence. No remote generated secret is accepted as replacement for intended persisted authentication. Ordinary renewal never calls generic additive `update_user(reset_usage=True)`.

## Provider operations

| Proposed signature | Meaning and required evidence |
| --- | --- |
| `inspect_child(scope) -> ChildObservation` | Distinguish found_verified, confirmed_absent, owner/generation/attachment mismatch, unsupported, transient and invalid application response. Return actual canonical auth/settings/membership fingerprint. Same name alone is insufficient. Missing object cannot mean zero traffic or permission to adopt/recreate. |
| `prepare_child(intent) -> MutationObservation` | Exact persisted credential and attachment set, inactive state, no shared route/listener/outbound changes. Response may be confirmed, rejected-no-effect or uncertain/partial; reconcile same intent before retry. Current `create_user` internally generated enabled secret is not this operation. |
| `apply_child_state(intent, canonical_observation) -> MutationObservation` | Absolute desired settings using fresh verified canonical field merge and correct full API scope; one coordinated canonical write, not stale per-inbound snapshot loop. Preserve unrelated fields/users. Latest restrictions/revision checked before call and after evidence. |
| `observe_meter(scope) -> MeterObservation` | Strict upload/down integers, verified underlying authority/ownership/topology, observation sequence/time/epochs/continuity evidence; declared incomplete/invalid/stale/gap if unavailable. No invented source time. |
| `export_node(intent, prepared_descriptor) -> VerifiedNodeDescriptor` | One exact selected protocol endpoint/transport/security/flow/remark; no first-link fallback, extra native addresses, defaults or omission. Return explicit missing-required-field failure. |
| `revoke_child(scope, current_intent) -> MutationObservation` | Deny fresh authentication via supported controls; preserve traffic/identity needed for accounting/cleanup. Delete only after retention/absence/runtime contract known; disable first when it preserves useful evidence. No reset or unapproved shared restart. |
| `confirm_runtime_state(scope, desired) -> RuntimeEvidence` | Positive evidence appropriate to deployed native behavior, backed by controlled fresh-authentication checks. API acceptance or DB desired state alone is not confirmation. If installed panel has no safe runtime proof, fail explicitly and keep pending; E-001 must resolve the supported mechanism before implementation/release claims. |

`MutationObservation {scope, intended_revision, dispatch/request_reference, application_result, affected_attachment_set, confirmed_db_fields?, runtime_evidence?, observed_at, definite_no_effect?, partial_effects?, uncertainty_reason?}`. Any timed-out request or local failure after dispatch stays uncertain until independent reconciliation. `success:true` cannot alone imply complete provisioning/revocation or gap-free metering. An `UnsupportedCapability` is distinct from transient retryable failure.

Fresh-auth confirmation uses actual native credential authentication, not ping/TCP-open/download/list-removal nor an additional mux stream over an authenticated tunnel. Existing native sessions remain separate recorded exposure. No custom Xray session-kill/core modification or service-wide restart is introduced. Runtime restart-on-disable settings and implicit API restart conditions must be checked against unrelated users; dangerous bulk operations are not selected.

## Physical routing and export

Select versioned anchored authenticated-email namespace matching owner-prepared route rules, one child canonical email per intended route/opaque identity. Lifecycle retains intended routing identity across renewal; leak/equivalent moves generate fresh identities in the appropriate prepared namespace. The owner supplies listener/inbound/outbound policy, route precedence and supported regex/core settings. Shopvpn validates selected binding and actual egress in controlled checks, never generates or edits shared configuration.

Six-node descriptor fields are exhaustive by protocol:

- VLESS REALITY: UUID, exact endpoint/443, encryption, required flow, transport, server name, public key, short ID, supported fingerprint and any required path field.
- VLESS WS-CDN: UUID, intended CDN endpoint/port, TLS/SNI/fingerprint where configured, Host/path and transport options.
- Trojan gRPC: protocol password, endpoint/port, security/SNI, serviceName and any mode/authority fields required by prepared settings.
- VMess TCP-TLS: UUID, security/alterId as configured, endpoint/port, TCP/header settings, TLS/SNI and owner remark.

Normalize exact fields into provider-local descriptor, preserve them in strict URI encoding and verify exported authentication matches canonical intended credential. No extra public A listener/L4/outbound clone; five live choices and six acceptance nodes remain distinct. Public source suggests feasibility but actual version-specific flow mutation/route precedence is unverified.

## Remote execution and fencing

Bot/admin/payment processes persist intent only for composite side effects. Worker holds main singleton OS lock; provider writes use physical-panel OS lock and durable uncertain-scope marker across affected Shopvpn callers. Reconciliation reads may run with bounded concurrency; writes on a panel serialize conservatively until narrower safe scope is proved. Main-thread locks/DB leases are not remote fencing. On process death, release of OS lock does not prove provider action was absent: unresolved dispatched marker blocks another conflicting effect until safe read-back/proof.

Worker claim/ack predicates include installation/restore epoch, operation identity, child generation and current desired revision. Obsolete results are recorded, not acknowledged as current success. If a late remote enable/disable conflicted with current desired state, reconcile and issue safe current absolute correction. Permanent cancellation and accepted leak intent cannot be overwritten; successfully renewed eligible terms must also escape obsolete old-term cutoff. Protective acceptance does not wait for remote locks. Deadlines/targets remain original even when uncertainty prevents effect execution; missed target and required recovery are visible.

10-second total call timeout is the initial proposed setting, with finite retry policy and urgent scheduling from plan; measure before release. Rejected-no-effect can retry if still eligible. Unknown result must first reconcile. Retry exhaustion leaves cleanup/refund/remote obligations and owner action, never a completed flag or local removal. Partial compensation/refund is not global rollback; refund can settle even while revoke remains uncertain.

## Accounting interface — G-A unresolved

Proposed `ingest_observation(meter_id, evidence) -> AccountingResult` transaction validates physical owner/source sequence/directions/epochs, inserts once, advances only trustworthy source time, generates per-direction deltas and retains gap/billing allocation evidence. Return confirmed uncapped lifetime use, current period allocation, remaining qualified allowance, oldest required source time, freshness/gaps/serving-versus-retired exposure and desired enforcement trigger. Duplicate/alias/out-of-order source observations never create new consumption or a fake fresh timestamp.

Proposed `establish_period_boundary(subscription, operation, evidence) -> BoundaryResult` must establish through-effective-application old usage, expired/timely carry eligibility, actual overrun versus new-period consumption and all-child readiness without deliberately interrupting usable old service. Source timestamps/time intervals and lineage must permit attributable increments. An ambiguous interval cannot be split at HTTP receipt, attributed entirely to the new period, erased or declared absorbed automatically. Native resets must preserve confirmed history and disclose lost intervals; ordinary composite renewal avoids them.

The inspected cumulative traffic GET lacks required trustworthy measurement clocks/atomic cut/continuity evidence. This is **a blocking capability gap, not a TODO to fill timestamps with `now()`**. Obtain supported non-disruptive source evidence and controlled known-byte tests before finalizing these interfaces' implementations; no direct core API bypass, new custom core or generic per-renewal owner intervention is presumed authorized. If infeasible under exact versions, report affected FR-034–FR-046/SC-003–SC-005 for explicit resolution. Meter tables and mocks cannot resolve it.

Fresh verified display requires every current-serving meter source age≤60seconds and reconciled/explicitly settled history. Known invalidity warns immediately. Any last-trustworthy required meter reaches grace at five minutes across restart; exhaustion/expiry acts earlier. Explicit emergency cutover may retire old meters from current grace, while unknown exposure/late use/cleanup remains. Known allowance exhaustion uses exact bytes; cutoff budget includes panel internal measurement lag, worker detection, queue, action and runtime confirmation within60seconds normally. No finite outage excess or forced existing-session promise is added.

## Required provider checks

Offline contract tests retain all eleven factory identifiers and legacy signatures/result/unit/error/`preserve_remaining` distinctions; strict new capabilities reject unsupported providers. Characterize actual old create/update/delete/usage/export defects with synthetic responses, and verify changed paths remediate rather than copy them. Authorized E-001/E-002 checks record exact TLS/auth/dialect/attachment/runtime/reset/overlay/version behavior, six protocols/egress, unknown effects, fresh handshakes/native sessions and unchanged control users/shared infrastructure. None is run by planning.
