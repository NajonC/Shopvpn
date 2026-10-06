# Implementation Plan: Composite VPN Subscriptions

**Branch:** `main` (retained) | **Date:** 2026-10-04 | **Spec:** [spec.md](spec.md)

**Input:** `specs/001-composite-subscriptions/spec.md`, constitution 1.0.0, complete accepted PC-001–PC-122, source-coverage ledger, requirements checklist, CONTEXT and original composite source documents.

**Planning status: PROVISIONAL / ERROR at required research gate G-A.** The independent design is ready for review; the planning workflow is not complete and unconditional task generation is not ready. Current traffic interfaces do not establish source freshness/history continuity or allocation through renewal boundaries. G-C (information entries) and G-P (exact configured payment methods) also block their dependent contracts. [research.md](research.md) records established evidence, precise missing capability, prerequisites and earliest checks. No approved scope is dropped, no exception is inferred and no technical fact is delegated to the user to guess.

Setup ran the installed `.specify/scripts/bash/setup-plan.sh --json`. It resolved `FEATURE_SPEC=specs/001-composite-subscriptions/spec.md`, `IMPL_PLAN=specs/001-composite-subscriptions/plan.md`, `FEATURE_DIR=specs/001-composite-subscriptions`, `BRANCH=001-composite-subscriptions` from feature metadata. That BRANCH is the workflow identifier; actual Git branch is `main`. Resolved template: `.specify/templates/plan-template.md`, unchanged. Before/after hooks: `.specify/extensions.yml` absent. No branch/worktree/commit was created.

## Summary

Add a separate main-store composite entitlement over independently managed 3x-UI children, preserving current single-panel/stock/reseller behavior. Keep authoritative money, holds, entitlement, generation, accounting history and durable work together in main SQLite. Use guarded existing Telegram receipt/catalog entry points and owner web administration, optional explicit provider capabilities, a separately supervised worker and an independent Base64 subscription server. Cache only a verified complete configuration generation; separate desired restrictions from confirmed runtime state and cleanup.

Every accepted journey is launch scope: initial purchase, manual/zero-price payment, common ordinary tests/campaign, full renewal/trial conversion, customer disable/resume/leak replacement/cancellation, owner single/bulk service controls/usage-gap settlement/wallet compensation, equivalent moves including inactive cases/emergency exposure, recovery and paid reminders. Priorities do not trim this set.

The **acceptance fixture** is six independent credentials: three A VLESS REALITY routes on one public 443 listener, B VLESS WS-CDN, B Trojan gRPC, C VMess TCP-TLS; one 50-GiB/720-hour entitlement, six ordered real nodes plus information entries. The **initial live offer** is A-only with five explicitly prepared/routed credentials on its one inbound. Neither count is a maximum. v2rayNG, NekoBox, Streisand, V2Box and v2rayN are all required. Public source is capability evidence, never deployed acceptance.

## Technical Context

**Language/Version:** Existing Python source and installer-selected `python3` virtualenv; no production runtime version inspected. Proposed validation baseline Python 3.11 on Linux, retaining compatibility with supported existing installations as characterized; exact release runtime is an E-004 prerequisite. Explicit sqlite3 transaction behavior avoids relying on Python 3.12+ autocommit defaults.

**Primary Dependencies:** Existing aiogram, FastAPI/uvicorn, aiohttp, cryptography, standard-library sqlite3/asyncio/fcntl. `requirements.txt` uses lower bounds rather than a tested release lock. No new runtime framework, ORM, Redis, queue broker, gateway or database engine. Proposed dev-only pytest/pytest-asyncio for meaningful isolated checks; selected/tested dependency versions must be recorded during implementation, with no installation in this task.

**Storage:** Main SQLite is composite authority, with additive compatibility discriminators/version metadata. Existing reseller SQLite and FSM remain distinct and join affected migration/recovery. Dedicated transaction ownership, FKs/WAL, FULL synchronization for affected main writers, no network waits in DB transactions. OS locks and persistent generations coordinate processes; WAL is not distributed/cross-file atomicity.

**Testing:** Proposed isolated characterization/unit/contract/integration tests with synthetic clocks/data/provider/payment/Telegram substitutes, multi-process SQLite/crash tests; separately authorized non-production panel/client/payment/load/recovery validation. No feature suite or CI was demonstrated; `test_config_provision.py` is customer trial code. Documentation/static validation only was authorized here.

**Target Platform:** Existing Linux/systemd installation, local disks, supervised bot/Mini App/admin plus proposed composite worker and public subscription process behind prepared verified HTTPS/domain. This checkout is the implementation workspace, not old Windows links. Network-filesystem WAL/multi-host writers are unsupported by this selected design.

**Project Type:** Brownfield Python Telegram shop and HTTP admin/Mini App with new domain package; no whole-bot rewrite.

**Performance Goals:** Single 60-second event-to-confirmation budgets for normal cutoff/access/replacement/cancellation/reporting recovery; current source data age ≤60 seconds, request stale suspension at five minutes; initial/renewal/test complete readiness and Telegram retrieval ≤15 minutes; applicable spendable wallet credits ≤60 seconds; paid reminder Telegram acceptance ≤five minutes; 150×five equivalent move ≤15 minutes; recoverable copy capture age ≤15 minutes and conditional prepared-host recovery ≤four hours. All exact triggers/conditions remain those in the spec timing table. These are unmeasured targets, not achieved results.

**Constraints:** SQLite, provider factory, finite bytes/time, binary units/elapsed UTC, no extra A listener/L4/shared route editor/core modification/disruptive restart. Preserve native existing-session policy and explicit unobserved usage/overrun; no finite outage-byte cap. Tenant/owner/peer authentication and complete history/cleanup survive all failures.

**Scale/Scope:** Arbitrary configured node/subscription collections; required six-node multi-panel fixture, A-only five-choice live offer, 150-recipient campaign, 100-subscriber/300-A-identity/three-shared-outbound capacity fixture and separate 750-moved-credential benchmark. Neither cohort proves active capacity or limits arbitrary larger batches. E-004 must define and measure supported normal conditions without shrinking accepted scope.

**Research unknown dispositions:** Repository mechanisms and architecture selections are resolved in RD-01–RD-08. G-A, G-C and G-P remain explicitly unresolved capability gates; runtime/load/recovery sizing and actual client/panel versions remain evidence requirements. Renaming them as evidence does not pass the workflow's research gate.

## Constitution Check

### Before research — recorded 2026-10-04

This initial check was completed before agent/public research. It evaluates planning obligations, not implemented compliance. All seven principles apply; no accepted specification/constitution conflict was found.

| Principle | Applicability and affected boundaries | Supporting requirements / required investigation and checks | Exception |
| --- | --- | --- | --- |
| I Observable contracts | Telegram callbacks/FSM, owner admin, main/reseller shared legacy paths, payment/renewal/providers/restore. Accepted channel exclusions explicitly change composite behavior. | Trace callers/defaults; additive discriminators; legacy manual/automatic renewal, all eleven provider identifiers, conversation/API and tenant regressions. | None |
| II Repeat-safe effects | Wallet/payment/coupon/test/campaign, provisioning/reset/usage/renewal/refund/revocation/cleanup. | Transactions/processes; durable identities/effect keys, desired/confirmed state and uncertainty; duplicate/concurrent/crash tests; E-001/E-002/E-005. Existing mechanisms are not presumed compliant. | None; affected unsafe patterns require remediation. |
| III Authority/secrets | Acting Telegram identity, owner-only web/payment decisions, tenant/resource access, peer verification/downloads. | Established auth helpers plus main-owner gate; exact method evidence; redaction/authorized setup/delivery; cross-tenant/role/replay checks. | None; no TLS/host-key exception. |
| IV Recoverability | Main/dependent reseller/FSM, schema, writers/backups/restore, destructive dependencies/cleanup custody. | Upgrade rerun/backward-read limits; coherent copies/off-host capture age; staged preflight/pre-copy; stale holds/newer evidence/missing members; E-004. | None |
| V Provider boundary | Shared factory/lifecycle contract and 3x-UI optional capabilities, existing units/results/identifiers. | Provider-local payload/auth translation; explicit unsupported capabilities; preserve_remaining and all provider callers; source and controlled E-001. | None |
| VI Verification | New behavior and risky affected legacy changes. | Synthetic/offline characterization and acceptance/failure cases; real versions/config/load and not-run status; authorized controlled E-001–E-005. | None; no isolation exception assumed. |
| VII Actionable failures | Timeouts/jobs/restart/lifecycle/accounting/enforcement/public endpoint, financial and notification recovery. | Finite timeouts/retries, retained original clocks/work, sanitized diagnostics/customer+owner recovery, measurable qualified timings and independent optional failures. | None |

**Pre-research gate:** PASS for read-only research and planning; no intention certified as compliance. Consequential capabilities still need evidence.

### After design — 2026-10-04

| Principle | Design/evidence supporting prospective compliance | Planned proof and remaining gap | Result / proposed exception |
| --- | --- | --- | --- |
| I | RD-01 discriminators and isolated composite domain; owner/channel/auth adapters; unchanged legacy result/update interfaces. Source trace identifies receipt, renewal, test, catalog/supply/delete/alerts/referral/FSM crossings. | Characterize all touched entry points and legacy defaults/units, reject composite direct Mini App/reseller/gift/transfer/add-on/automatic renewal, preserve manual versus automatic carryover and recorded conversation state. | Design aligned; **implementation unverified**; no exception. |
| II | RD-02/03/07 atomic main settlement+immutable receipt/effect IDs, precreated identities, outbox, reconciliation and refund independent of cleanup; RD-04 separate meter/epoch/delta/billing/gap. | Duplicate/concurrent approval/debit/refund/campaign/meter tests; unknown commit/remote responses; G-A temporal evidence and G-P method contracts. Data structures alone do not prove exact attribution or received money. | **ERROR/provisional** for G-A/G-P dependencies; no waiver. |
| III | Authenticated principal domains/main-owner guard, actor ownership in callbacks; encrypted secrets/token hash and redacted logs, peer-verified transport. Affected SSL/auth/amount risks are explicit remediation. | Forged/cross-tenant/staff/read/replay cases; configured CA/host-key/secret recovery; native callbacks verified independently. Secrets never enter fixtures/general logs. | Design aligned; proof pending; no exception. |
| IV | RD-08 maintenance/generation checks, staged validated full restore, pre-restore set, guard dependencies; recovery-held newer evidence and durable cleanup. | All writer closure/restart paths, prior-schema migration rerun, both archive names/missing/skewed members, stale financial/campaign/revocation/purge, host loss and measured RPO/RTO. | Design aligned; E-004 unverified; no exception. |
| V | Factory retained with optional capabilities/explicit Unsupported; exact child attachment/fields and safe absolute updates remain provider-local. | Contract tests for eleven legacy providers/signatures; real dialect/update/filter/runtime/restart behavior and prepared email routing E-001. | Provisional capability binding; no bypass or exception. |
| VI | Full FR/SC/source-ledger mapping below; isolated test strategy and controlled evidence gates remain distinct. | G-A/G-C/G-P first, then repeatable implementation/crash/compatibility checks and complete release E-001–E-005. No present mock/live pass asserted. | Planning review/static checks only; **workflow gate not passed**; no exception. |
| VII | Mandatory worker+independent endpoint, current-revision reconciliation, original deadlines, explicit partial/uncertain/overdue views, bounded retries durable owner obligations. | Budget/fairness/native-session/cutoff recovery and notification uncertainty at supported load. Confirmed cutoff is runtime evidence, not HTTP acknowledgement. | Design aligned; timing/capability unverified; no exception. |

**Post-design result:** No genuine conflict between constitution and accepted product decisions identified. No exception proposed or approved. Independent design obligations are covered; current accounting source cannot discharge accepted FR-034–FR-046/SC-003–SC-005, and information-entry/payment bindings remain unverified. Therefore the mandatory research/design gate is **ERROR**, not an all-principles PASS. Do not begin dependent implementation or claim completed planning until technical evidence resolves these gates.

## Architecture and execution boundaries

### Local authority and financial processing

`composite/service.py` (proposed) is the common application boundary. It receives an authenticated main-tenant principal, never trusts client IDs to confer authority, and opens one transaction for each command. Compatibility `orders` rows carry `service_kind='composite'` and a unique composite checkout reference, with no fake `config_id`. Payment finalizers dispatch before legacy order claims/provision/referral logic; legacy receipt UI displays separate financial/fulfillment outcomes. `products` and `test_config_plans` discriminate the new type; corresponding selectors reject unsupported channels at server-side entry and common service layer.

Finalize price/tier/code/node snapshot and reserve sufficient wallet/coupon together. Main wallet mutation uses conditional sufficient balance, unique ledger effect and checked affected row; touched top-up/refund helpers combine status+credit so shared wallet paths cannot strand composite funds. Common coupon counters/holds and ordinary test holds must cover competing legacy and composite callers; a composite-only reservation table without updating affected legacy capacity checks would exceed capacity. Existing fulfilled `test_used` is preserved, unresolved holds stay separate and reset cannot erase them or permanent campaign recipients.

Verified receipt insertion, original payment role, order authorization/deadline and financial obligation/work creation are atomic. Duplicate transaction returns prior result; different actual receipt has separate late/extra role and full original quote credit. An indeterminate verification/commit stays uncertain, without release/replay. Unfunded quotes have no general TTL; valid attempts/manual review remain funding paths after new invoices are disabled. Suspension/cutover explicitly reject affected unfunded quotes. One partial unique open-renewal index covers quoted/review/authorized fulfillment; terminal money/cleanup records remain but do not alone prevent another checkout, unless accounting/entitlement is still unsafe.

### Remote effects, state and concurrency

See [data-model.md](data-model.md) and [provider contract](contracts/provider.md). Transactionally allocated operation/child/authentication identities precede calls. Each attempt stores immutable scope/input hash, desired revision, dispatch and result/uncertainty. Reads verify physical panel, canonical identity, secret fingerprint and expected attachments before mutation; no matching-name adoption. Calls apply absolute desired fields; reconcile after ambiguous response or crash before repeating. Rollback is a durable compensating operation, not a DB rollback assertion.

One worker singleton owns composite remote execution; OS panel locks plus durable ambiguous-scope barriers coordinate affected bot/API legacy provider writes. Account/role/UI requests only commit intent. Revisions reject stale local results, but cannot fence remote already-sent calls: keep panel scope blocked until confirmed current remote state, then converge to newest accepted restrictions. Record late conflicting results; old expiry/exhaustion disable must be reconciled after successful renewal, and obsolete enable must not erase cancellation/restrictions. An unknown provider call has no automatic lock-lease expiry that authorizes repeating its effect.

Protective requests remain admissible during checkout/other work. Leak acceptance immediately invalidates old token and records all-child revocation; reachable old nodes proceed despite other failure. New token/credentials publish only after old fresh-auth revocation, complete new readiness and Telegram retrieval. Cooldown is 86,400 seconds per subscription from successful replacement (including owner override), never failure or a fresh request. Equivalent move uses fresh moved secrets/same token, leaves unmoved identities intact, retains inactive eligibility and old exposure. Explicit emergency approval may retire old meters from serving freshness requirements; it never bypasses leak gates or claims old cleanup.

Permanent cancellation has separate acceptance/wait/final-stage timestamps. Authorized renewal resolves by its unchanged deadline, then final cancellation invalidates/revokes and refunds that renewal even if it just succeeded. Paid initial cancellation immediately blocks delivery, waits only to current provisioning outcome/original deadline, then refunds/revokes. Unfulfilled owner/test cancellation is not a new owner product action. Desired customer disable/owner suspension/reporting hold/recovery hold remain separate and expiry continues. Account block/bot outage is separate.

### Accounting, renewal and export (conditional design)

Distinct confirmed increments are ingested once by physical meter/epoch/sample; upload/down resets are independent. Invalid boolean/negative/nonintegral values, missing identities/application errors/stale authority cannot generate samples. An unexplained decrease/panel baseline restart/overlapping interval records a gap, preserving confirmed totals and original grace clocks. Delayed retired traffic is retained and attributed to the proper generation/period; old overrun never becomes debt against renewal. No remote quota reset on ordinary composite renewal.

Effective renewal commits one new period only after every child is ready under currently applicable restrictions and accounting evidence resolves the boundary. New available data is new bytes plus eligible old unspent bytes after intervening use; old overrun contributes zero debt. Pre-expiry verification is strictly `< old_expiry`, with within-window completion; at/after expiry forfeits expired data. Effective expiry is `application_time + 2,592,000 + min(max(old_expiry-application_time,0),1,296,000)` seconds. Carry old data only while eligible under FR-043/044; no separate data expiry or whole-day rounding. Term expiration during pending work still cuts old access. Coupon/reminder period changes are atomic with successful effective grant. A partially applied failed renewal refunds independently and reconciles current old terms.

**G-A stops selection of the temporal meter/billing implementation:** source lacks the evidence required above. Preserve observed intervals/ambiguity and contractual formulas; do not implement a receive-time split or silently treat uncertain interval as zero/absorbed. A generic design intention, 15-second polling or owner usage settlement cannot make normal renewal compliant. Initial/replacement/movement accounting readiness and trustworthy freshness also depend on this gate.

Public read-only service performs token/generation/hold/owner-suspension gates on a fresh DB snapshot for each request, then renders cached complete real entries plus qualified info snapshots. It never calls a panel, refreshes sample time, provisions/enables or settles. Revoked token is an opaque unavailable response with no new-token redirect; uncertain generation is temporary unavailability; owner suspension returns status-only; ordinary expiry/exhaustion/customer-disable/reporting suspension/outage keeps complete current entries. See [subscription HTTP contract](contracts/subscription-http.md). Informational wire encoding is provisional at G-C; all five-client selection effects need resolution before dependent serialization.

### Worker lifecycle and operational coordination

Proposed services `v2raybot-composite-worker` and `v2raybot-subscriptions` are required infrastructure once feature is deployed; existing `v2raybot`, `v2raybot-miniapp` and `v2raybot-adminpanel` remain. Worker discovers main DB records without requiring bot/admin availability. Start under singleton lock, verify schema/installation/restore epoch, reconcile in-flight effects, process overdue original deadlines first, then accounting/expiry/revocation/recovery/refunds/reservations/moves/reminders with reserved urgent capacity. Financial work can complete despite panel failure. Downloads survive worker/bot/optional UI failure when public infrastructure and verified cached generation remain available.

Use independent task lanes, bounded calls and per-panel fair queues; initial scheduling candidates in RD-06 are unmeasured. For remote transient work: 10-second total call timeout, at most five automatic mutation attempts at 1/2/4/8/15-second backoff where deadlines allow, each preceded by reconciliation of uncertainty; mark missed 60-second target as soon as elapsed. Exhaustion leaves manual obligations and allows safe scheduled observation/authorized retry; no automatic deletion. Retained cleanup observations can back off to five minutes, independently of urgent current enforcement. Fifteen-minute targets/escalations refer to original acceptance/readiness/final-stage event, not last retry. Notifications have separate finite retries, acceptance receipts and uncertain-send handling; never claim exactly-once Telegram delivery.

On SIGTERM, stop accepting work, cancel/drain bounded calls, persist uncertain dispatch where needed, release locks after closing DB sessions; unexpected death leaves intents/claims, not success. No old worker can acknowledge a new restore epoch. Supervisor restart uses same operations and deadlines. Wall-clock UTC stores absolute events; monotonic timers bound waits; clock regression/large drift raises a hold for affected time decisions until trusted time is restored, without moving sold clocks. Deployment includes time-sync health and disk/DB lock/queue/sample-lag/cleanup/refund metrics with sanitized record IDs.

## Project Structure

### Documentation (this feature)

```text
specs/001-composite-subscriptions/
├── spec.md                         existing, unchanged
├── reference-coverage.md           existing, unchanged
├── checklists/requirements.md      existing, unchanged
├── plan.md                         this provisional plan
├── research.md                     decisions and E-001–E-005 gates
├── data-model.md                   proposed entities/invariants/transitions
├── quickstart.md                   present vs future validation
└── contracts/
    ├── application.md              commands, authority, UI/payment contracts
    ├── provider.md                 optional provider/worker/accounting contracts
    ├── subscription-http.md        public complete-export/gating contract
    └── operations.md               migration/maintenance/recovery contracts
```

`tasks.md` is deliberately not generated. Historical P0–P6 packages are not the task structure.

### Source Code (repository root)

```text
database.py, payment_engine.py, *_payment.py             existing shared boundaries
handlers_user.py, handlers_admin.py, keyboards.py       existing Telegram adapters
admin_panel/server.py, admin_panel/security.py          existing owner interfaces
admin_panel/static/app.js                              existing owner UI
miniapp/server.py                                      existing unsupported-channel guard
panel_providers/base.py, panel_providers/__init__.py     existing provider boundary
panel_providers/threexui_provider.py                    existing 3x-UI adapter
main.py, bot_manager.py, renewal_reminders.py            existing dispatch/job compatibility
backup.py, fsm_storage.py, install.sh, manage.sh, update.sh existing affected operations
composite/                                             proposed package
  service.py, repository.py, models.py, migrations.py
  finance.py, accounting.py, lifecycle.py, exports.py
  worker.py, subscription_server.py, notifications.py, operations.py, cli.py
tests/                                                proposed isolated suites
  characterization/, unit/, contract/, integration/, acceptance/
```

**Structure Decision:** Keep existing modules as adapters with bounded shared safeguards; move new domain logic into `composite/`. Provider-specific HTTP/auth/normalization stays in `panel_providers/`. No new service may bypass the factory, and no general handler rewrite is proposed. Proposed tests/CLI/service unit files do not exist now; commands are clearly labeled in quickstart.

## Upgrade, deployment and recovery design

1. Later implementation first characterizes risky affected paths and resolves G-A/G-C/G-P. A tested release identifies revision/runtime/dependencies/schema/capability manifests and peer trust. Include secret/runtime/backup exclusions in affected source-control/update handling; `update.sh` staging/pushing all files cannot be the feature release procedure.
2. Ship compatibility guards and additive schema changes with issuance disabled. Stop admission and quiesce all affected DB/FSM writers, including bot reconciler/purge/cache loops, both APIs, notifier and future worker/subscription server; verify closure before replacement/migration. Capture/validate a protected complete pre-upgrade recovery set. Migrate main then enumerate every registry tenant including inactive/no-live-bot; apply compatible additive discriminator/guard metadata, preserving all legacy data. Fail visibly, retain prior set and refuse partial enablement.
3. Rerun migrations on historical/current/feature synthetic schemas; check FKs, indexes, entity/effect/count invariants and required fields, owner preservation and version range. A migration transaction never calls nested committing helpers/unsafe executescript. Reseller composites remain forbidden; no composite child synthesis from old services. A new process refuses unsupported future schema. Old binaries are fenced while composites or new financial obligations exist.
4. Prepare owner panels/routes/TLS/capability registration, external keys and public HTTPS/domain; start worker/public process in guarded state. Check lock singleton, restore epoch, queue/reconciliation health, secret-free logs and public invalid-token behavior; then bot/admin health and all controlled release gates. Enable owner-validated catalog only after evidence passes. A-only live five-choice setup never replaces six-node acceptance.
5. Capture a coherent backup under the shared affected-writer gate; include main, required dependent tenants/FSM, generation/schema/manifest/checksums and required identity/financial/accounting/campaign/work history. Do not include raw environment keys in unencrypted archive; authorized DB secrets require protected encryption/delivery. External release/config/key/domain/HTTPS/panel prerequisites are inventoried separately. Verify off-host retained copy and capture time; maintain ≤15-minute age normally. Missing/skew/transfer failure gives owner overdue/unknown+attempted alert, without mass access/refund changes.
6. Restore entire staged set only after archive safety/integrity/schema/data/member validation, verified closed writers and complete pre-restore copy. Both legacy reseller ZIP names are accepted; pre-feature archives never prove absence of newer composite history. Maintain external installation/restore epoch and newer accessible evidence across replacement. Reject mixed versions/missing expected members or report bounded partial recovery with affected holds before restart; no silent main-first success. Stale queues/leases/purges are invalidated and cannot re-enable/recredit/delete newer state.
7. Reconcile known newer payment/ledger/coupon/test/campaign/revocation/generation/usage facts, release verified records independently and resume verifiable overdue money within its catch-up deadline. Unknown money/claims/generations stay held; only verified owned identities may be safely restricted/cleaned. Usage-only owner settlement cannot resolve non-usage history. Four-hour target starts once all owner-prepared prerequisites exist and recovery is initiated, never restarts on retry; truthful functions/partial/held/overdue report required.
8. Guard factory reset/customer/panel/catalog/tenant/tier/ownership/purge deletion from losing protected evidence/dependencies; force/confirmation never bypasses. Deactivation prevents new offer/claim use but retains current management credentials and work. Rollback after issuance uses a feature-aware compatible build or coordinated full restoration plus reconciliation; old code over live composites is not safe rollback. No requested hard-delete or cleanup-history erasure is added.

## Validation and traceability

The existing source ledger remains authoritative for PC/R/D/A/S dispositions. The following compact mapping adds design/test responsibility without editing or relabeling that ledger. Every row is a **planned check**, not passing evidence; constituent FR conditions, examples, interactions and all 44 AS remain required.

| Spec requirements / success criteria | Design responsibility | Planned validation / source ledger |
| --- | --- | --- |
| FR-001–FR-008; SC-001/SC-012 | RD-01/05, saved offers/logical nodes/children/physical aliases, auth adapters | AS-01.1/04.1/06.1; six-node plus A-only five; second subscription/customer/tenant aliases; A01/A02/A07/A18/A19/A20/A21/A26/A33; E-001/E-003/E-004 |
| FR-009–FR-021; SC-002/SC-005 | RD-02/07, quote/attempt/receipt/effect/holds, one renewal | AS-01.3–01.5/03.4–03.5; tier floor/caps/zero-price, native exact units, 103 refund/extra credit, valid-attempt protection vs unpayable, simultaneous owner decisions; E-005 |
| FR-022–FR-026; SC-001/SC-002 | RD-03/06, intent/readiness/retrieval/deadlines/cleanup | AS-01.1–01.2/01.6; partial/timeouts/commit-crash/push failure/late readiness, initial cancellation final clock; A03–A06/A28; E-001/E-004/E-005 |
| FR-027–FR-032; SC-006/SC-005 | RD-01/02, common test reservation/campaign/permanent recipient/conversion | AS-04.1–04.5/03.6; capacity 149+1 races, forged callback actor, unknown hold/no late grant, reset/cancel/conversion permanence, exact 200 MiB/hour and 15 GiB/15 days; A28/A29; E-004 |
| FR-033–FR-041; SC-003/SC-004 | RD-04/03/06, authority/epochs/deltas/gaps/restrictions | AS-02.1–02.6, EC-03/04; known-byte direction/reset/alias/out-of-order/gap, 60/61-second source freshness, restart grace, measured fresh-auth and native exposure; A07–A17/A26; G-A, E-001/E-002 |
| FR-042–FR-048; SC-005 | RD-04/07/03, period cut/protected carryover/absolute terms | AS-03.1–03.6, EC-05; exact partial-day/strict expiry/45-day cap, old overrun, late old disable, no duplicate or reset, old-access continuity and partial reversal; A09/A11/A15/A25; G-A, E-001/E-002/E-005 |
| FR-049–FR-052; SC-008 | RD-05/06, complete cached generation/read-only public gates | AS-06.1–06.3, EC-11; all fields/remarks/order/actual egress in five clients, info-only selection, invalid old link/no redirect, disabled APIs/bot and no fetch mutations; A21/A22/A32/S02–S04/S12; G-C, E-003 |
| FR-053–FR-060; SC-007/SC-002 | RD-03/06/07, independent restrictions/rotation/cancel/refund | AS-05.1–05.4; protective controls overlap unpaid/authorized renewals, initial wait vs final stage, 24-hour per-sub success cooldown, runtime old revocation, native sessions and original clocks; A14/A24/A25/S07/S08/S10; E-002/E-005 |
| FR-061–FR-064; SC-007/SC-002 | RD-02/03, owner batch preview/audit/dedup/compensation | AS-05.5–05.6; no staff powers, one effect per unique customer, reason/preview changed list, interrupted partial bulk and no rollback of completed members; E-005 |
| FR-065–FR-071; SC-009 | RD-03/05/06, equivalent map/retired meter/exposure/catalog pause | AS-07.1–07.4, EC-07; inactive moved state, unmoved secrets/URL/history, emergency distinct from leak, independent 150×5 benchmark/notification, authorised pending work clocks; A24/S03/S09/S10; E-001/E-002/E-004 |
| FR-072–FR-077; SC-010/SC-002 | RD-08/02/03, capture/restore epochs/recovery holds/guards | AS-08.1–08.5, EC-08–10; fresh capture/off-host loss, conditional four hours, missing/skew/corrupt members, stale money/claims/revocations/purges, no reset clocks or replay; A29–A31/S11/S13; E-004/E-005 |
| FR-078–FR-080; SC-011 | RD-06, paid period/reminder outbox/eligibility | AS-09.1–09.3; initial+conversion+zero-price paid period, 120h/80% or selected 2GiB, no lifetime-use alarm/rearm/test notice/coupon, uncertain send and obsolete work; A32; E-004 |
| FR-081–FR-086; SC-012 | All RD; affected legacy seams/provider/operations/auth | Characterization of callbacks/FSM, stock/custom/test/gift/naming/transfers/payments/reseller mirrors/providers, known risky negative cases, synthetic upgrade/recovery and unsupported composite endpoints; A01/A18/A19/A23/A25–A33/S11–S13; all E IDs |

Use unit tests for arithmetic/transitions/parser normalization; provider/payment contracts for strict evidence, not mock acceptance; real multi-process integration for transactional uniqueness/crash ordering/locks/capture/restart. Inject crashes immediately before/after each DB commit and remote dispatch/result; assert retained obligations and original clocks, and reconcile instead of repeating uncertain effect. Check auth/cross-tenant selectors and secret output/log boundaries throughout. Tests isolate external traffic using explicit substitutes/network denial; no production credentials/endpoints. G-A/G-C/G-P probes precede work that they could invalidate; later full acceptance checks cannot retroactively justify an unverified early design.

## Complexity Tracking

No constitutional violation or exception is proposed. New worker and download process are necessary to satisfy explicit interface independence and stateful processing, using existing runtime dependencies. Their supervision/backup/restore overhead is recorded in RD-06/08; it is not a justification for weakening any requirement.

## Review outcome and stopping point

Planning artifacts and static validation are provided for review, with gates visible. All eight artifact files passed local-link, code-fence, table-column, placeholder and whitespace checks; the mapping includes all 86 FR and 12 SC IDs and research retains all five E IDs. All 14 protected input hashes match the pre-edit record; Git reports only these eight new files and no tracked or staged change. These checks validate document structure and preservation, not implemented behavior or semantic acceptance. Existing inputs, application/tests/config/skills/templates remain unchanged. No integration check passed, no `tasks.md`, implementation, commit/push or Antigravity worktree was created. Resolve G-A with technical evidence first; resolve G-C and each G-P binding before dependent tasks. Full E-001–E-005 release evidence remains required even after those early gates pass.
