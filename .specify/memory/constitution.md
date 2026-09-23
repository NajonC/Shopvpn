# Shopvpn Constitution

## Core Principles

These rules apply prospectively under **Brownfield Adoption and Scope**. Evidence of an
existing pattern is not a claim of universal historical compliance.

### I. Preserve Observable Contracts

Changes MUST preserve existing observable Telegram flows, commands, callback/deep-link
formats, persisted conversation state, API contracts, configuration meanings/defaults, and
stored customer data unless the feature specification explicitly authorizes a breaking change
and defines migration or compatibility handling. Plans MUST identify affected clients and
installations, including reseller tenants, and how compatibility will be checked.

**Rationale and adoption:** Relative-path resolution, additive schema changes, legacy provider
settings, and order compatibility fields demonstrate existing compatibility work. Requiring
an explicit contract and review evidence for each affected change is new governance.

### II. Make Financial and Provisioning Effects Verifiable and Repeat-Safe

Payment, wallet, refund, order, inventory, reseller-credit, and provisioning changes MUST
validate the tenant, beneficiary, transaction reference, expected amount, and currency/unit
conversion before settlement. Rounding and accepted tolerances MUST be explicit.
Client-reported success, unverified callbacks, and missing/unparseable payment evidence MUST
NOT authorize settlement. Manual approvals MUST require an authorized actor and audit record.

These paths MUST prevent duplicate debits, credits, refunds, allocations, and provisioning
under repeated callbacks, concurrent approvals, retries, and restarts. Related local financial
updates MUST be atomic; effects spanning databases or external services MUST have a durable
recovery or reconciliation path. Payment confirmation, provisioning, and delivery outcomes
MUST remain distinguishable. An uncertain external result MUST be reconciled before repeating
its effect.

Purchased-entitlement and usage-accounting changes MUST specify allowance, expiry, renewal,
counter-reset, and enforcement/outage semantics. Accounting MUST identify underlying meters
and prevent duplicate consumption attribution through aliases or retries. Missing, invalid,
or stale samples MUST NOT be treated as zero consumption or current verified usage. Resets
and renewal MUST preserve accrued-consumption evidence and apply only specified billing-period
adjustments; unobserved consumption MUST remain explicit uncertainty.

Remote lifecycle operations MUST distinguish desired state from confirmed remote state and
retain the identities and pending work needed for reconciliation or cleanup. Refunds and local
record removal MUST NOT discard unresolved remote cleanup obligations.

**Rationale and adoption:** Conditional order claims, top-up status guards, gateway verification,
and provisioning compensation exist. End-to-end consistency and recovery are new requirements
strengthening uneven safeguards; exactly-once external execution is not assumed. These rules
cover purchased entitlements, metering, and remote lifecycle responsibility without certifying
existing accounting or cleanup behavior.

### III. Enforce Authority, Tenant Isolation, and Secret Boundaries

Protected operations MUST authenticate callers and enforce applicable roles, permissions,
resource ownership, and tenant boundaries on the server, reusing established helpers where
applicable. Client user IDs, tenant selectors, and hidden UI controls MUST NOT confer authority.
Cross-tenant reseller supply operations MUST explicitly authorize the main-store resource and
receiving tenant. Payment and bot callbacks MUST establish authenticity through a verified
sender or independent provider verification before trusted action.

Deployed secrets MUST come from environment or authorized tenant configuration. Secrets,
credential-bearing subscription links, and authentication payloads MUST NOT enter source
control, test fixtures, general logs, or unauthorized responses. Intentional credential setup
and customer delivery MUST be restricted to authorized recipients. Connections carrying secrets
MUST verify the intended remote peer; exceptions require the security exception process below.

**Rationale and adoption:** Tenant databases, Telegram initData validation, signed web sessions,
hashed mobile tokens, and role helpers are established boundaries. Consistent enforcement,
redaction, callback authenticity, and peer verification are prospective strengthening, not
certification of the current implementation.

### IV. Keep Data Changes and Operations Recoverable

Schema and persistent-state changes MUST support existing main and reseller databases within
the affected scope, preserve data unless its removal is explicitly specified, and be safe to
rerun on supported prior schemas. Plans MUST describe upgrade ordering, validation, failure
handling, and rollback or restoration when the prior application cannot read the new state.

Installation, upgrade, migration, backup, and restore changes MUST define affected services
and state, including backup exclusions. They MUST provide a consistent backup strategy,
coordinate database writers during replacement, validate restored data and schema, retain a
recovery copy before destructive replacement, and report partial restoration. Validation MUST
exercise the affected upgrade and recovery paths in a disposable environment with synthetic or
sanitized data before deployment. Deployment instructions MUST identify the release, relevant
configuration/dependency changes, health checks, and recovery steps.

Tenant deletion, reset, tier changes, and ownership transfer MUST preserve or durably hand off
responsibility for outstanding remote operations and cleanup before removing the records they
depend on. The affected plan MUST identify that responsibility and how completion is verified.

Restore changes MUST reconcile affected financial, usage, and lifecycle state against available
newer external evidence before resuming dependent mutations. Recovery MUST prevent unsafe
replay of stale work and re-enabling of known revoked access. Missing history or unavailable
evidence MUST remain explicit, with a documented remediation or risk-acceptance decision under
Governance. A restored snapshot alone MUST NOT establish current remote state or complete
historical recovery.

**Rationale and adoption:** SQLite initialization/migrations, its online backup API,
pre-restore copies, and service-stop logic provide existing foundations. Consistent validation,
coordination across processes, and demonstrated recovery are new requirements; no migration
framework or database replacement is mandated. Preserving responsibility through tenant cleanup
and reconciling stale restores are prospective requirements prompted by gaps at adoption.

### V. Preserve the Panel-Provider Boundary

New or changed VPN panel integrations MUST use the provider factory and shared provider
contract for supported lifecycle operations. Panel-specific HTTP, authentication, and payload
translation MUST remain in provider implementations. Changes MUST preserve documented input
units, user identity, subscription results, error semantics, and existing provider identifiers,
or specify compatible changes to affected callers. Unsupported capabilities MUST fail
explicitly; provider-specific setup capabilities MUST be selected explicitly by callers.

**Rationale and adoption:** At the adoption baseline, eleven registered implementations use
`BasePanelProvider`, `PanelUserResult`, `PanelError`, and `get_provider`; provisioning and
renewal reuse this boundary. This formalizes an existing architectural convention.
Subscription-link inspection is a separate integration; the contract does not imply identical
capabilities across panels.

### VI. Verify New Behavior and Characterize Risky Legacy Paths

New and changed behavior MUST have repeatable automated tests covering acceptance criteria and
relevant failures. Financial/authentication changes MUST cover applicable duplicate,
concurrency, rejection, and tenant-isolation cases; provider and data changes MUST cover affected
contracts and recovery behavior. All tests MUST use isolated synthetic or sanitized data and
MUST NOT use production credentials or call production services. Unit and offline regression
tests MUST use controlled substitutes for external services. Integration and acceptance tests
against real services MUST use explicitly authorized non-production resources and test
credentials, with documented isolation and cleanup.

Acceptance claims about actual panel/client compatibility, traffic accounting, routing,
enforcement, or remote recovery MUST be supported by repeatable non-production integration or
staging checks against recorded versions and configurations. Mock-only evidence MUST NOT be
presented as proof of these claims; unexecuted checks MUST remain identified as unverified.

Risky legacy modifications SHOULD begin with characterization tests of current observable
behavior, because the code lacks a demonstrated regression suite and behavior may be implicit.
Where isolation is impractical, the plan MUST explain why, record a reproducible baseline
check, and document an exception and bounded follow-up. Documentation-only or mechanical changes
without behavioral effects do not require new tests; review and relevant static checks MUST
verify them instead.

**Rationale and adoption:** This is new policy. At adoption, no established automated test suite
or CI configuration was tracked; `test_config_provision.py` implements customer trial provisioning.
There is no claim of historical test-first development, universal TDD, or a coverage threshold.
Controlled real-service validation is included because substitutes cannot establish deployed
protocol, metering, enforcement, or recovery behavior.

### VII. Make Failures Actionable

New or changed external calls and scheduled processing MUST define timeouts, retry limits,
and failure outcomes. Retried side effects MUST follow Principle II. Financial, provisioning,
data, and authorization failures MUST produce sanitized diagnostics identifying the operation
and relevant tenant/record, plus a user or operator recovery path where action is required.
They MUST NOT be silently swallowed or reported as completed work.
Exhausting automatic retries MUST leave unresolved financial and remote lifecycle obligations
durably recorded and visible for reconciliation or operator recovery.

Optional integration failures SHOULD degrade independently, because notification, map, rate
source, or AI-support outages need not disable unrelated shop operations. Fallbacks MUST be
explicit in the plan and observable when they affect results. They MUST NOT bypass
authentication or financial verification. Background work MUST define startup, shutdown, and
restart behavior for stateful effects.

Enforcement and recovery changes MUST define measurable timing guarantees, tenant coverage,
and outage behavior in their feature plan. Diagnostics MUST distinguish stale observations,
pending remote action, and confirmed completion; an accepted API request alone MUST NOT be
reported as verified access cutoff.

**Rationale and adoption:** Logging, typed integration errors, timeouts, fallback rate sources,
and per-bot job management already exist. Consistent diagnostics and recoverable partial
outcomes are new requirements extending practices that are currently uneven. Requiring
enforcement evidence does not promise instantaneous distributed cutoff.

## Brownfield Adoption and Scope

This initial constitution is effective from **2026-09-22**, its ratification date. It governs
a mature inherited product, including when that code is adopted into a new repository. It
MUST NOT be represented as evidence of original Spec-Driven Development or historical
compliance with newly adopted rules. In-progress plans MUST complete the Constitution Check
before further implementation or release review; completed historical work is not
retroactively certified.

- New code MUST comply. Modified legacy code MUST comply within the reasonably affected scope:
  changed behavior and directly affected callers, data, authorization, and operational paths.
- Untouched legacy code may be grandfathered. A change MUST NOT be required to modernize an
  unrelated subsystem. Repository-wide modernization MUST use separate bounded specifications.
- Known exceptions relevant to a change MUST appear in its feature plan. Grandfathering MUST
  NOT justify copying unsafe legacy patterns into new code or expanding their exposure.
- Plans MUST distinguish observed implementation, inconsistent conventions, prospective policy,
  and intended behavior in draft/untracked documentation. README claims and Spec Kit scaffolding
  MUST NOT alone be treated as proof of deployed behavior.

The adoption baseline is source revision `696695850180fc97f66457a41e86c76dcd330e1e` (`6966958`).
This is a fixed historical reference for the inspected inherited source, not a requirement that the repository’s current HEAD remain at that revision.
This identifies the inherited source even if a new repository starts a separate Git history.
Static inspection found aiogram bots with per-bot dispatchers and SQLite/FSM state; FastAPI
Mini App and web/mobile admin boundaries; shared database, payment, provisioning, renewal,
and delivery modules; registered panel providers; and shell-managed services. These describe
the inherited system, not mandatory technology choices for all future work.

Known gaps at adoption, not exemptions already approved for future changes:

- Financial transitions span separate commits and remote effects. Top-up credit, wallet debit
  and order creation, rejection/refund, invoice completion, renewal, and provisioning persistence
  have crash or partial-success risks. Best-effort provisioning rollback is not durable recovery;
  some persistence failures can still be reported as successful fulfillment.
- 3X-UI traffic errors can become zero usage, deletion can report success without verifying the
  application response, and renewal reset/read-back failures leave uncertain effects. Manual
  full renewal requests carryover; automatic renewal requests replacement. These distinct
  flows require characterization, not an assumed common renewal policy.
- Panel aliases and tenant-local mirrors do not establish unique physical meter identity.
  Tenant tier changes, deletion, ownership transfer, and factory reset can lose management or
  cleanup responsibility. Existing per-bot jobs do not cover tenants without running bots.
- `payment_engine.py` permits an unauthenticated custom webhook mode, and its amount matcher
  accepts missing/unparseable amounts; bot webhook secrets are optional. 3X-UI/subscription TLS
  checks and backup SFTP host checks are disabled. These conflict with the prospective rules.
- Backup validation is shallow; sequential database snapshots and partial restoration can leave
  inconsistent tenant state. Main replacement can precede tenant validation, and missing tenant
  copies may go unreported. Restore does not establish coordinated reconciliation with panels.
  Database archives are not complete environment/FSM or remote-infrastructure backups.
- The active `.gitignore` excludes only bytecode; broader exclusions are in `_.gitignore.txt`.
  `update.sh` stages and pushes all files. Provisioning cleanup and delivery errors are
  sometimes ignored. These are risks, not endorsed practices.

Inspection excluded secrets, runtime databases, backups, and live services.
Large handlers, API modules, and front-end assets were assessed through relevant paths, not
every function or UI state. Deployment versions/configuration, external Android clients, and
actual restore success remain unverified. The active HTTP servers are `miniapp/server.py` and
`admin_panel/server.py`.
No applicable `AGENTS.md` or established automated test/CI instructions were found in the
inspected source repository. Spec Kit scaffolding is not production evidence.

Separately reviewed composite-subscription proposals informed risk analysis but are not part
of source revision `6966958`. No composite implementation or passing acceptance suite was
established at adoption. The rules here do not depend on those documents being present and
do not approve a composite feature design. Feature policies, topology, storage constraints,
provider scope, and worker design belong in their own specifications and plans.

## Planning and Review

Every Spec Kit plan MUST complete a Constitution Check before research and repeat it after
design. For each principle it MUST record applicability, affected boundaries, evidence or
planned checks, and exceptions. Specifications MUST make intended behavioral changes explicit;
tasks MUST include resulting validation and recovery work. Template examples, including
optional-test wording, MUST NOT override this constitution.

Implementation review MUST repeat the Constitution Check against the actual diff and record
check results, compatibility handling, operational consequences, and unresolved risks. A
principle MUST NOT be marked satisfied solely because a plan promises compliance. Missing
evidence MUST remain visible as a gap or approved exception. Volatile versions, commands,
provider settings, and feature-specific designs belong in feature artifacts or operational
documentation, not additional permanent constitutional mandates.

## Governance

This constitution takes precedence over conflicting repository conventions and template
examples for work within its scope. Exceptions MUST identify the principle, affected
behavior/files, evidence, rationale, risk, compensating checks, responsible maintainer, and
remediation decision with a review date or bounded follow-up. A project maintainer MUST
explicitly accept each exception in the feature plan or linked review before merge or
deployment. Security, financial-integrity, authorization, and data-integrity exceptions MUST
explicitly justify retained risk and choose remediation now, a bounded follow-up, or reasoned
risk acceptance; silence or "legacy behavior" alone is insufficient. Exceptions MUST NOT
silently amend the constitution.

Amendments MUST state proposed wording, repository evidence or explicitly proposed new policy,
rationale, scope/compatibility impact, and transition treatment for existing work. A project
maintainer MUST approve them through recorded review. Amendments MUST update this document,
its version, and Last Amended date, and assess dependent workflow guidance without silently
changing unrelated artifacts.

Constitution versions MUST use semantic versioning: **MAJOR** for incompatible removals or
redefinitions of governance; **MINOR** for added principles or materially expanded guidance;
**PATCH** for clarifications without changed obligations. Ratified MUST retain the original
adoption date. **1.0.0** records initial adoption, not a product release or a declaration of
legacy compliance.

**Version**: 1.0.0 | **Ratified**: 2026-09-22 | **Last Amended**: 2026-09-23
