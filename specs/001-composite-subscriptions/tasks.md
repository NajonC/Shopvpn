---

description: "Dependency-ordered, G-P-fenced task list for Composite VPN Subscriptions"
---

# Tasks: Composite VPN Subscriptions

**Input**: Design documents from `specs/001-composite-subscriptions/`: spec.md (including PR-001, PR-002 and PR-003), plan.md, research.md (RD-01–RD-10 and the E-001–E-005 ledger), data-model.md, contracts/application.md, contracts/provider.md, contracts/subscription-http.md, contracts/operations.md and quickstart.md.

**Prerequisites**: constitution 1.0.0 (`.specify/memory/constitution.md`); accepted PC-001–PC-122 (`docs/composite-subscriptions/GRILLING-PRODUCT-DECISIONS.md`).

**Generated**: 2026-10-19 at HEAD `a1358db`, on explicit owner request. plan.md's line "`tasks.md` is deliberately not generated" is superseded by that request. No other artifact was changed.

**Updated**: 2026-10-21: owner-reported routing evidence RD05-MAN-001 recorded under T082; OQ-3 resolved and the fence on T096, T099 and T120 lifted. 2026-10-22: RD05-MAN-001 and the owner's build-first decision moved to research.md RD-05 (RD05-OWN-001); OQ-5 resolved, and evidence paths follow its rule. OQ-1 and OQ-2 resolved (research.md GP-OWN-001): automatic card-to-card and methods outside the six candidates are excluded from composite plans, and T215 now enforces that. Later on 2026-10-22, after `/speckit-analyze`: T082 split into part A (as soon as authorized; gates T097) and part B (after T096 and T099); T255 adds rule precedence and API-created clients; T099, T107 and T215 clarified. Owner decisions on the analyze findings: RD03-OWN-001 (provider checks also build first, test after), RD05-OWN-002 (the panel API is the only source of connection fields; address-only changes use the equivalent move: T085, T096, T103, T113, T116, T181, T183) and the GP-D2 wording (OQ-2). Second `/speckit-analyze` run, same day: T099 no longer waits on T082 part A; subscription-level `uncertain` added to T107; zero-value safety in T095/T085 and the part A repeats in T255; manual card-to-card kept off the automatic invoice path (T212, T215); method list limited to accepted contracts (T113, T116); panel setup reads go through the worker (T098, T116); External Proxy setup in T099 and T240; test pointers fixed (T086, T103, T113). Owner decisions RD05-D6–D8: old identity disabled at publication on a same-inbound move (T181, T183); an open discrepancy blocks new generations (T086, T120, T162, T166); renewal matching ignores the address (T143, T144, T186).

**Planning status at generation**: PROVISIONAL / ERROR, only because gate **G-P** (exact configured payment-method contracts; E-005) is open. G-C closed on 2026-10-10, G-A on 2026-10-14 and RX-01 on 2026-10-17. The plan rules out only *unconditional* task generation, so this list is **conditional**:

- Every task that depends on G-P is in Phase 14 and carries **Gate: G-P (method)**. It does not start until that method's evidence task is complete and the owner has accepted the contract record.
- The method-independent finance core (Phase 3) is **not** blocked.
- Only T097 carries **Gate: E-001 probe (T082)**. On 2026-10-21 the owner lifted that fence for T096, T099 and T120 after a lab routing check (RD05-MAN-001); see OQ-3.

**Tests are mandatory.** Constitution VI and FR-086 require repeatable, isolated tests for all new and changed behavior. They also require characterization of risky legacy paths before those paths are modified. Under "Planning and Review", every behavior task must also have its own validation and recovery work. The template's "tests are optional" wording therefore does not apply here (constitution "Planning and Review": template examples MUST NOT override it).

**Authority order applied**: constitution, then PC-001–PC-122, then spec.md (including PR-001/PR-002/PR-003), then plan/research/data-model/contracts. Where a document keeps an old rule next to a later resolution, tasks follow the current rule:

| Superseded or historical wording | Current rule used by these tasks | Source |
| --- | --- | --- |
| plan.md:113 "G-A stops selection of the temporal meter/billing implementation" | Implement PR-002/RD-09: observations timed at Shopvpn receipt, decrease epochs per direction, saved boundary starting readings at most 60 s old at commit, reporting-order attribution, no remote reset | plan.md:113 resolution of 2026-10-14; GA-MAN-002 |
| 10-second composite call timeout | 15-second total call timeout. The T = 10 s stall threshold still counts a write unanswered at 10 s | RX-OWN-005 RX-D11 |
| RX-01 strict fencing predicate; `execution_hold` and `safe_to_retry` statuses | RD-10 detect-and-repair. Statuses `queued`, `dispatched`, `uncertain`, `confirmed`, `manual_hold`. Q = S = restore wait = 30 s; T = 10 s, escalating after 3 consecutive misses; R = 3; N/W = 3 within 1 hour; P = 2 min; M = 30 min | RD-10; RX-OWN-005 |
| "A retry of the same desired state waits for the quarantine" | A timed-out access-reducing request is read back and re-sent at once (RX-D7) | RX-OWN-004 |
| "No uncertain request for that client is still in quarantine" as a condition of "confirmed" | Only an uncertain request that could undo the state being confirmed blocks confirmation (RX-D8) | RX-OWN-004 |
| Delete only after the meter stops growing | Delete after the quarantine and either P without growth or M since the disable, whichever comes first (RX-D9) | RX-OWN-004 |
| RX-D3: automatic panel-only restart to be decided later | No automatic restart of any kind (RX-D12) | RX-OWN-005 |
| D3: restart loss of "about one collection interval" | Up to four collection intervals (20 s) per restart, absorbed by the store and recorded explicitly, never a usage gap | GA-OWN-004 D12 |
| V-RX-01(b) must run over direct TLS to close RX-01 | The workstation-route result is accepted for closure. A bot-host direct-TLS re-run is required before composite mutations reach production panels, after the three harness fixes | RX-OWN-005 RX-D13 |
| PC-077/PC-080 per-client validation of automatic selection | Removed, not deferred | PR-001 |
| V-CAN-03 "RX-01 execution hold" | Read as an RD-10 uncertain request in quarantine, or a panel stall | RD-10; quickstart V-CAN-03 reworded 2026-10-22 |
| 3x-UI default `restartXrayOnClientDisable` = on | Must be off on every composite panel. Verified before binding and continuously by the sweep | RX-D2; spec Assumptions (PR-003) |
| RD-05 "Gate: E-001 first six-node egress/readiness and unrelated-user preservation, before implementing dependent routing/export behavior" | Routing bindings and strict export are implemented now. The anchored-namespace, unrelated-user, six-node egress and export-field checks run after implementation (T082, T255, T257) | research.md RD05-OWN-001 (owner decision 2026-10-21, on RD05-MAN-001); OQ-3 |
| E-001 ledger "First validate exact disposable deployment API/TLS/canonical identity/mutation scope …" before dependent implementation | Provider operations (T095) are built first. T082 part A runs as soon as it is authorized, and only T097 waits on it | research.md RD03-OWN-001 (owner decision 2026-10-22) |
| plan.md:203 "G-P and RX-01 (V-RX-01(a)–(h)) probes precede work that they could invalidate … later full acceptance checks cannot retroactively justify an unverified early design" | Only G-P still precedes the work it could invalidate. The RX-01 probes ran; routing, export and provider operations are built first and checked before release (T082, T255, T257) | research.md RD05-OWN-001, RD03-OWN-001; RX-MAN-001 |
| RD-05 and data-model.md `composite_plan_nodes`: an owner-selected endpoint descriptor verified against API fields | The 3x-UI API is the only source of connection fields, with the address and port from the inbound's External Proxy entry; the owner picks only where the panel offers several values. A later panel change is an FR-041 discrepancy and blocks new generations for that node until resolved. An address-only change is an equivalent move to the same inbound; its old identity is disabled at publication. The address is not part of the renewal-matching signature | research.md RD05-OWN-002 (owner decisions 2026-10-22) |

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel: different files and no dependency on an incomplete task.
- **[Story]**: User story label (US1–US9). Used only in the user-story phases.
- **Gate: G-P (method)**: blocked until that method's G-P evidence task passes and the owner accepts its contract record.
- **Gate: E-001 probe (T082)**: depends on the result of part A of the E-001 capability probe.
- **Requires authorization**: needs explicit owner execution authorization and disposable non-production resources. Never run against production panels, payments or customers, and never offline.
- Offline tests run under `--network=deny` with synthetic data only. Each implementation task names the tests it must pass (`Tests: T…`).

## Path Conventions

- Single brownfield Python project at the repository root. Existing modules stay adapters and change only within the affected scope.
- New domain package `composite/` (plan.md "Source Code"). Helper modules not named in plan.md: `composite/secrets.py`, `composite/audit.py`, `composite/payment_methods/` and `panel_providers/threexui_composite_client.py`.
- Tests: `tests/characterization/`, `tests/unit/`, `tests/contract/`, `tests/integration/`, `tests/acceptance/` and the harness in `tests/_harness/`.
- Evidence location (OQ-5 rule; raw logs always stay outside the repository):
  - evidence that closes a research gate or drives a design decision (T082, the G-P evidence tasks) goes in `specs/001-composite-subscriptions/research.md`, following GA-MAN-002/RX-MAN-001;
  - release evidence that the implementation works (Phase 16) goes in `specs/001-composite-subscriptions/evidence/`, one redacted file per check, linked from the matching E-001–E-005 ledger row in research.md;
  - the implementation review and Constitution Check go in `specs/001-composite-subscriptions/implementation-review.md`, linked from plan.md;
  - tasks.md holds pointers only.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Package skeleton, isolated test harness and controlled substitutes. This phase adds no behavior, and generating this list installs no dependencies.

- [ ] T001 Create the `composite/` package skeleton from plan.md "Source Code": `composite/__init__.py`, `composite/service.py`, `composite/repository.py`, `composite/models.py`, `composite/migrations.py`, `composite/finance.py`, `composite/accounting.py`, `composite/lifecycle.py`, `composite/exports.py`, `composite/worker.py`, `composite/subscription_server.py`, `composite/notifications.py`, `composite/operations.py`, `composite/cli.py`, plus `composite/secrets.py`, `composite/audit.py` and `composite/payment_methods/__init__.py`. Module docstrings only; nothing reads production configuration or databases at import time
- [ ] T002 [P] Create the test tree `tests/__init__.py`, `tests/conftest.py`, `tests/characterization/`, `tests/unit/`, `tests/contract/`, `tests/integration/`, `tests/acceptance/` and `tests/_harness/`. Add `tests/README.md` stating the rule: synthetic data only, no production credentials, no production services (constitution VI; FR-086)
- [ ] T003 [P] Add a dev-only `requirements-dev.txt` (pytest, pytest-asyncio), recording the tested versions when they are first installed in an isolated virtualenv. Leave runtime `requirements.txt` unchanged (plan.md Technical Context: no new runtime framework)
- [ ] T004 [P] Extend `.gitignore` so secrets and runtime state cannot be committed (constitution III/IV known gap). Add the relevant exclusions from `_.gitignore.txt` plus runtime databases (`*.db`, `*.db-wal`, `*.db-shm`), backup archives, `.env` and key files, lab roots and evidence scratch
- [ ] T005 [P] Set up the evidence locations under the OQ-5 rule (spec "All future validation must retain…"; FR-086; constitution Governance "feature plan or linked review"):
  - create `specs/001-composite-subscriptions/evidence/README.md` defining the release-evidence record: implementation revision, versions and configuration, fixture, expected and observed results, pass/fail/not-run, redaction and cleanup, and the rule that each passing record is linked from its E-001–E-005 ledger row in research.md;
  - create `specs/001-composite-subscriptions/implementation-review.md` with empty sections for characterization exceptions, intended behavior differences, the Constitution Check and the release go/no-go;
  - turn the existing `implementation-review.md` entry in the documentation tree of `specs/001-composite-subscriptions/plan.md` into a link, without restructuring plan.md;
  - raw logs stay outside the repository
- [ ] T006 Implement the `--network=deny` pytest plugin in `tests/_harness/network_guard.py` and register it from `tests/conftest.py` (quickstart "Proposed post-implementation commands"). It fails any test that opens a non-loopback socket or selects a database or service path outside a `mktemp` lab root
- [ ] T007 [P] Implement a controllable clock in `tests/_harness/clock.py`: a UTC epoch-millisecond wall clock and a separate monotonic clock, with injectable regression and large drift (plan.md "Worker lifecycle")
- [ ] T008 [P] Implement synthetic fixture factories in `tests/_harness/fixtures.py`, following the spec FR-002 fixture table:
  - the six-node fixture: A-US, A-DE and A-RU on one REALITY 443 inbound; B-CDN (VLESS-WS); B-gRPC (Trojan); C-Direct (VMess TCP-TLS);
  - the A-only five-choice offer;
  - a second subscription for the same customer and a second customer;
  - overlapping tenant/local IDs and panel aliases.
  Secrets are generated per run and never written to the repository
- [ ] T009 [P] Implement a controlled standalone 3x-UI v3.9.0 substitute in `tests/_harness/fake_threexui.py`, modelled on the RX-MAN-001 and GA-MAN-002 observations and labelled "substitute, not evidence". It covers:
  - client writes ordered per inbound;
  - `success: true, obj: null` for missing clients;
  - "database is locked" after about 10.3 s;
  - held requests that apply after the client closes, and requests fully delivered whose response is held;
  - `restartXrayOnClientDisable`, default on, turned back on by a settings reset;
  - admin, node-sync and monitor token scopes (403);
  - a 5-second collector cadence and restart baseline loss;
  - per-direction counter decreases: reset, `updateTraffic`, database restore, recreate and periodic reset
- [ ] T010 [P] Implement payment and Telegram substitutes:
  - `tests/_harness/fake_payments.py`: a method adapter that can return confirmed, rejected, uncertain, a repeated hint, a mismatched amount or currency, and a missing or unparseable amount;
  - `tests/_harness/fake_telegram.py`: acceptance with a message reference, a lost response, retry-after, permanent rejection and a crash after dispatch
- [ ] T011 [P] Implement the multi-process SQLite and crash-injection harness in `tests/_harness/multiprocess.py` and `tests/_harness/crash.py` (plan.md "Validation and traceability"; quickstart). It runs separate processes and connections on synthetic files, with named crash points before and after each commit, each remote dispatch and each remote result
- [ ] T012 [P] Implement `tests/_harness/secret_scan.py` (FR-084; constitution III). It fails when generated tokens, UUIDs, Trojan passwords, panel tokens, subscription URLs or payment keys appear in captured logs, exception text, HTTP bodies returned to unauthorized callers, or fixture files

**Checkpoint**: the harness imports, and `python -m pytest tests --network=deny` collects with zero tests and no network access.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Characterize the affected legacy paths before changing them. Then build the storage, authority, compatibility-guard, processing-control and worker foundations that every story needs.

**⚠️ CRITICAL**: No user-story work begins until this phase is complete. Each 2A characterization task must be complete before any later task modifies the file it characterizes.

### 2A — Characterization of risky legacy paths (constitution VI; tests first, no behavior change)

Each task pins today's observable behavior, including known unsafe behavior, using synthetic substitutes, and records a reproducible baseline in the test module docstring. If isolation is impractical, the task records the constitution VI exception and its bounded follow-up in `specs/001-composite-subscriptions/implementation-review.md`.

- [ ] T013 [P] Characterize the Telegram catalog purchase in `tests/characterization/test_buy_start.py` (FR-081; SC-012):
  - `handlers_user.py:_buy_start:1038` acting as `call.from_user.id`, with product methods, tier and FSM coupon;
  - the separate wallet-debit, coupon-increment and order-insert commits at lines 1081–1096;
  - quantity;
  - stock, direct and reseller fulfillment through `config_delivery.py:deliver_config_to_user:133`;
  - the referral reward hooks
- [ ] T014 [P] Characterize both manual-receipt linkage paths in `tests/characterization/test_receipt_linkage.py`, recording the order of receipt persistence and admin notification (V-RCP-01 baseline; FR-014):
  - the FSM path, `handlers_user.py:receive_receipt:1560`;
  - the fallback at `handlers_user.py:5173` → `database.py:get_latest_pending_order_awaiting_receipt:3515`, which filters by actor and excludes orders with a crypto invoice.
  Cases: lost or stale FSM, several pending orders, another actor's order and duplicate uploads
- [ ] T015 [P] Characterize order approval in `tests/characterization/test_order_approval.py` (FR-014; PC-093):
  - `handlers_admin.py:cb_order_approve:1777`: claim, then renew/provision/allocate, then approve, then deliver;
  - `admin_only:214` accepting staff;
  - `admin_panel/server.py:api_approve_order:2125` under `require_permission("orders")`;
  - claim release after an ambiguous remote error
- [ ] T016 [P] Characterize the local finance helpers in `database.py`, including a crash between commits, in `tests/characterization/test_wallet_helpers.py` (FR-011; constitution II known gap):
  - `claim_order:3413` and `approve_order:3433`;
  - `reject_order:3470`, which commits rejection before restoring wallet and coupon;
  - `approve_topup:4662`, which approves before crediting;
  - `add_wallet_credit:4363`, which clamps the balance;
  - `_get_conn:500` committing per helper
- [ ] T017 [P] Characterize the free-test flow in `tests/characterization/test_free_test_flow.py` (FR-027; FR-031):
  - `handlers_user.py` `get_test_config:2204` and `_deliver_test_plan:2248`;
  - `cb_user_test_plan_pick:2284`, which passes `call.message`, so the recorded actor is the bot;
  - the identity-free counter in `database.py` `try_reserve_test_slot:2266` and `release_test_slot:2291`;
  - the swallowed persistence failure in `test_config_provision.py:provision_test_plan:26`;
  - `MAX_TEST_PER_USER` and `test_used`, with disabled, one-plan and multi-plan selection
- [ ] T018 [P] Characterize legacy renewal and alerts in `tests/characterization/test_legacy_renewal_reminders.py` (FR-081 manual-versus-automatic distinction; FR-078):
  - `renewal_engine.py:execute_renewal:20`: manual full carryover, with the remote additive update/reset before local state and an ambiguous read-back;
  - `renewal_reminders.py:261`: automatic replacement renewal;
  - legacy reminder thresholds and coupons;
  - `connect_alerts.py` connection alerts
- [ ] T019 [P] Characterize the provider factory in `tests/contract/test_provider_factory_legacy.py`: all eleven identifiers registered by `panel_providers/__init__.py:get_provider:98`; the `panel_providers/base.py` signatures `BasePanelProvider:29`, `PanelUserResult:13` and `PanelError:20`; units; `preserve_remaining` (FR-082; constitution V)
- [ ] T020 [P] Characterize the legacy 3x-UI adapter in `panel_providers/threexui_provider.py` against `tests/_harness/fake_threexui.py`, in `tests/characterization/test_threexui_provider.py` (FR-034; FR-037; FR-084):
  - `_session:80`: `ssl=False`, a 20-second timeout and a new session per call;
  - `_build_client:141`: generated enabled identity, no VLESS flow;
  - `create_user:167`;
  - `get_user:228`: takes the first matching export;
  - `_post_client_update:299`: no inbound filter; a timeout becomes `PanelError`;
  - `update_user:327`: enables unconditionally, substitutes zero after a read error, ignores the reset result;
  - `set_enabled:416`;
  - `get_user_usage:207`: missing object or error becomes zero;
  - `delete_user:195`: checks HTTP status only
- [ ] T021 [P] Characterize `direct_panel_provision.py:provision_direct:34` in `tests/characterization/test_direct_provision.py`: secrets and names allocated inside the call, in-memory rollback with ignored exceptions, and a persistence failure at lines 130–149 that still returns results (FR-022)
- [ ] T022 [P] Characterize legacy export in `sub_info.py`, in `tests/characterization/test_sub_info_export.py`. Legacy output stays unchanged, and composite export never reuses this code (FR-049; FR-081):
  - `_net_params_from_stream:47`;
  - `_vless_or_trojan_uri:103`: VLESS flow omitted;
  - `_xray_outbound_to_uri:138`;
  - `_singbox_outbound_to_uri:190`: REALITY becomes TLS;
  - `fetch_individual_links:297`: a failure becomes an empty list;
  - `_session:268`: TLS disabled, URLs in diagnostics
- [ ] T023 [P] Characterize the payment verification helpers, using synthetic responses only, in `tests/characterization/test_payment_methods_legacy.py` (E-005 source leads; FR-011):
  - `payment_engine.py` `amounts_match:126` (None or unparseable returns True; 1 % tolerance) and `GenericGateway.check_webhook_auth:287` (mode `none`);
  - `custom_gateway_payment.py:compute_send_amount:31`;
  - `card_to_card_payment.py` `create_invoice:66`, `normalize_amount:29` and `match_and_complete:119`;
  - `abangateway_payment.py` `toman_to_rial:60`, `try_verify_and_finalize:124` and `finalize_paid_order:171`;
  - `extra_gateway_clients.py` Tetra98, CubePay and NOWPayments create/verify/classify and the IPN signature;
  - `extra_gateway_payment.py:process_stars_payment:371`
- [ ] T024 [P] Characterize background job ownership in `tests/characterization/test_background_jobs.py`: `main.py:main:30`; in `bot_manager.py`, `start_bot:191` with its jobs at lines 276–284, `stop_bot:296`, `reconcile_resellers_loop:401` and the deferred purge near line 517; and the exclusion of tenants without a running bot (FR-085 startup/shutdown)
- [ ] T025 [P] Characterize the SQLite foundations in `database.py`, in `tests/characterization/test_database_init.py` (FR-083): the `_connect:473` pragmas (WAL, foreign keys, 4-second busy timeout, `synchronous=NORMAL`), `_get_conn:500`, `init_db:584`, `_migrate_columns:1369` and `replace_file:527`
- [ ] T026 [P] Characterize backup and restore in `tests/characterization/test_backup_restore.py` (FR-076; FR-083):
  - `backup.py` `create_backup:29`, `create_full_backup:62` and `_sqlite_safe_copy:144`;
  - `restore_full_backup:157`: main replaced before tenants are validated; missing tenants invisible;
  - `_build_sftp_connect_kwargs:384` with `known_hosts=None`;
  - both reseller archive names, `reseller_<id>.db` and `reseller_<id>_level<N>.db`;
  - the restore callers `handlers_admin.py:8675` and `9092`, `admin_panel/server.py:1967` and `manage.sh:1752`
- [ ] T027 [P] Characterize destructive operations in `tests/characterization/test_destructive_ops.py` (FR-075; FR-083):
  - `database.py` `factory_reset:1330`, `delete_panel_server:6818` with force, `wipe_agent_state:1930` and `switch_agent_tier:1955`;
  - `transfer_reseller_ownership:4824`: commits main, then updates the tenant best-effort;
  - the `bot_manager.py` deferred purge
- [ ] T028 [P] Snapshot the observable Telegram contracts in `tests/characterization/test_callbacks_fsm.py`: callback-data prefixes from `keyboards.py` and `button_registry.py`, `states.py` state names, the keys `fsm_storage.py` persists, deep links, and the handling of the optional `WEBHOOK_SECRET` (FR-081; constitution I)
- [ ] T029 [P] Characterize the unsupported surfaces in `tests/characterization/test_unsupported_surfaces.py`: in `miniapp/server.py`, `get_tenant:138`, `get_verified_user:202` and its purchase, invoice and retrieval endpoints; `admin_panel/server.py:_build_reseller_self_config:2779`; and supply through `reseller_auto_provision.py` (FR-005; NG-01)
- [ ] T030 [P] Characterize owner and staff web authority in `tests/characterization/test_admin_auth.py`: in `admin_panel/server.py`, `get_current_admin:592`, `require_owner:685`, `require_main_tenant:691` and `require_permission`; `admin_panel/security.py` `create_session_token:43` and `verify_session_token:57`; and `admin_panel/mobile_auth.py` (FR-005; FR-084)
- [ ] T031 [P] Characterize invite/referral rewards, first-purchase flag consumption and shop-account blocking (`blocked_user.py`) on the purchase and test paths in `tests/characterization/test_referral_and_block.py` (NG-05; FR-063)

### 2B — Transactions, schema and migrations

- [ ] T032 [P] Write `tests/integration/test_repository_transactions.py` before T033 (RD-02; constitution II/VI). Cover:
  - two writer processes on a synthetic main file;
  - a crash before and after commit;
  - read-back of the `synchronous=FULL`, foreign-key and WAL pragmas;
  - busy overload surfaced as a typed error;
  - an indeterminate commit resolved by querying the unique effect key, never by retrying
- [ ] T033 Implement `composite/repository.py` (RD-02; FR-011; FR-085). Tests: T032.
  - Dedicated connection ownership, with an explicit `BEGIN IMMEDIATE` per command.
  - Foreign keys and WAL on; `synchronous=FULL` verified for every affected main writer.
  - A 1-second busy wait with bounded retries that surface overload.
  - Database work in a bounded thread executor, with no network waits inside a transaction.
  - `query_effect(key)` for reconciliation after an indeterminate commit
- [ ] T034 [P] Write `tests/integration/test_migrations.py` before T035–T041 (FR-083; constitution IV). Run `migrate` twice on synthetic historical, current pre-feature and feature-shaped schemas, each with main, reseller (both filename conventions), no-live-bot and FSM files. Check:
  - foreign keys, integrity, indexes, and data, effect and capacity invariants;
  - legacy rows defaulting to `service_kind='legacy'`, with the owner preserved;
  - refusal of an unsupported future schema;
  - a multi-file failure leaving issuance disabled and the pre-upgrade set retained
- [ ] T035 Implement the versioned additive migration runner in `composite/migrations.py` (contracts/operations.md "Additive upgrade"; FR-081; FR-083). Tests: T034.
  - `composite_schema_versions`, rerun safety, and refusal of unsupported future schemas.
  - Each database owns its transactions explicitly: no nested committing `Database` helpers and no implicit commit from `executescript`.
  - Add `service_kind` (default `'legacy'`) and an optional unique composite reference to `products`, `test_config_plans` and `orders`.
  - Affected reseller files receive only the compatibility metadata they need, and no composite eligibility
- [ ] T036 Add the data-model §1 DDL to `composite/migrations.py` (FR-004; FR-033). Tests: T034.
  - `composite_physical_panels`: provider `3xui` only; TLS trust reference; recorded panel and core version; capability-manifest revision; route-namespace version; write-path stall state; and the last verified `restartXrayOnClientDisable` value with its check time ("must be off … on or unreadable blocks new binding").
  - `composite_panel_aliases`, unique on `(database_installation_id, tenant_id, local_panel_server_id)`.
  - `composite_prepared_bindings`.
  - RESTRICT foreign keys, so that "A protected alias/panel cannot be force-deleted"
- [ ] T037 Add the data-model §2–§4 DDL to `composite/migrations.py` (FR-001; FR-003; FR-008; FR-051). Tests: T034.
  - `composite_plans` and `composite_plan_versions`, with the checks "Paid base price positive and duration exactly 2,592,000 seconds", "Tests use positive whole-hour durations" and "No legacy unlimited sentinel, negative duration".
  - `composite_plan_nodes`, unique on `(version, ordinal)` and on `(version, logical_node_key)`, with no maximum node count.
  - Immutable `composite_offers` and `composite_offer_nodes`.
  - `composite_subscriptions`:
    - `lifecycle` values `preparing`, `fulfilled`, `cancel_pending`, `cancelled`, `failed_unfulfilled`;
    - independent restriction columns `customer_disabled`, `owner_suspended`, `reporting_suspended`, `recovery_hold_case`, `replacement_delivery_block`, `initial_delivery_block`;
    - `cancel_accepted_at`; `cancel_wait_kind` (`authorized_renewal`, `initial_provisioning` or none); `cancel_final_started_at`.
  - `composite_tokens`: unique SHA-256 digest; status `candidate`, `current`, `revoked`, `superseded`; tombstones retained.
  - `composite_config_generations`: state `preparing`, `complete_verified`, `published`, `retired`, `blocked_uncertain`; one current published generation
- [ ] T038 Add the data-model §5–§7 DDL to `composite/migrations.py` (FR-033–FR-035; FR-043; FR-079). Tests: T034.
  - Children: `composite_children` (unique canonical remote identity per physical authority; encrypted secret; desired and confirmed state), `composite_child_attachments` and `composite_cleanup_obligations`.
  - Metering: `composite_meters`; `composite_observations` with dispatch and receipt time; `composite_meter_deltas`, unique on `(meter, direction, epoch, predecessor observation)`, with `allocation_state` `attributed`, `absorbed_exposure` or `gap_affected`; `composite_usage_gaps`.
  - Periods: `composite_entitlement_periods`; immutable `composite_boundary_readings`, unique on `(period, meter, direction)`; `composite_reminder_periods` and `composite_reminders`, unique per `(period, expiry|quota)`.
  - Bytes are checked nonnegative integers within signed 64-bit; times are UTC epoch milliseconds
- [ ] T039 Add the data-model §8–§9 DDL to `composite/migrations.py` (FR-011; FR-015; FR-020; FR-029). Tests: T034.
  - `composite_checkouts`: kind `initial`, `renewal`, `conversion`; status `quoted`, `awaiting_payment`, `manual_review`, `authorized`, `fulfilling`, `fulfilled`, `rejected`, `cancelled`, `failed`; a partial unique active-target index covering open renewal/conversion through authorized fulfilling.
  - `composite_payment_attempts`.
  - `composite_payment_receipts`: unique on `(provider, merchant_namespace, transaction_reference)`; outcome `original_funding`, `extra_credit`, `terminal_late_credit`, `mismatch_hold`.
  - Shared `financial_obligations` and `wallet_effects`: kind `wallet_debit`, `wallet_release`, `full_refund`, `late_credit`, `extra_credit`, `support_compensation`, `topup_credit`; state `owed`, `evidence_hold`, `settled`; unique business effect key.
  - `composite_manual_decisions`.
  - `resource_reservations`: resource `coupon`, `ordinary_test`, `campaign_place`; state `held`, `consumed`, `release_pending_refund`, `released`, `uncertain_hold`.
  - `composite_test_claims`; `composite_campaigns` (immutable lifetime cap 150); `composite_campaign_recipients`, unique on `(campaign, authenticated Telegram user)`
- [ ] T040 Add the data-model §10–§11 DDL to `composite/migrations.py`, with no cascade deletion of financial, history or cleanup rows (FR-075; FR-085). Tests: T034.
  - `composite_operations`.
  - `composite_remote_work` and `composite_remote_attempts`: status `queued`, `dispatched`, `uncertain`, `confirmed`, `manual_hold`; `quarantine_until`.
  - `composite_drift_sweeps` (outcome `consistent`, `diverged`, `unknown`) and `composite_divergences`.
  - `composite_batches` and `composite_batch_members`; `composite_audit_events`; `composite_notifications` with the N-01 fields.
  - `composite_processing_control`, `composite_recovery_points`, `composite_recovery_cases` and `composite_recovery_evidence`
- [ ] T041 Implement the upgrade-time reconciliation of `users.test_used` in `composite/migrations.py`, run with admissions quiesced (data-model §9; FR-027; FR-083). Preserve every prior count. Classify demonstrably pending legacy attempts into identity-based `ordinary_test` holds without counting them twice. Hold any unresolved remainder rather than subtracting it or assuming success. Tests: T034

### 2C — Domain types, secrets, authority and compatibility guards

- [ ] T042 [P] Write `tests/unit/test_models_predicates.py` (data-model §3):
  - the `desired_access` and publication predicates: a pending cancellation during an authorized renewal neither disables access nor invalidates the URL; owner suspension is status-only; expiry, exhaustion and customer or reporting disable keep the complete list;
  - `confirmed_access` aggregation (`unknown`, `partial`, `confirmed_eligible`, `confirmed_fresh_auth_denied`), including the RX-D8 rule
- [ ] T043 Implement `composite/models.py` (data-model §3–§4 and §10; FR-051; FR-053). Tests: T042.
  - State enums copied verbatim from data-model.md.
  - Independent restriction flags, never one mutable `enabled` flag.
  - Derived `expired` and `exhausted`.
  - The `desired_access`, publication and `confirmed_access` predicates
- [ ] T044 [P] Write `tests/unit/test_secrets_and_audit.py`, checked with `tests/_harness/secret_scan.py` (FR-084; constitution III/VII):
  - an AES-GCM round trip with versioned key IDs and unique nonces, and failure on a missing or wrong key;
  - the SHA-256 token digest;
  - the redaction filter on log records and exception text;
  - sanitized diagnostics carrying only operation, tenant and record IDs
- [ ] T045 [P] Implement `composite/secrets.py` (data-model "Storage and identity rules"; FR-084): versioned AES-GCM encryption of tokens, child secrets, URIs and necessary remote references, using keys only from authorized environment or configuration; digest helpers; and a log redaction filter installed on composite loggers. Tests: T044
- [ ] T046 [P] Implement `composite/audit.py`: an immutable audit-event writer (actor domain, action, resource, reason, evidence references) and the sanitized diagnostic builder used by every composite failure path, so that no failure is swallowed or reported as completed (constitution VII; FR-085). Tests: T044
- [ ] T047 [P] Write `tests/integration/test_authority_matrix.py`. Each of these attempts must change nothing (FR-005; FR-006; FR-084; SC-012):
  - a forged callback actor and a cross-tenant selector;
  - staff holding the `orders` permission, a reseller owner, and a full-access tenant that is not the main store;
  - a signed-tenant mismatch, and overlapping Telegram and web numeric IDs;
  - a mobile token on composite routes, and a cookie mutation without same-origin/CSRF;
  - a subscription-URL bearer attempting management
- [ ] T048 Implement `Principal`, `CommandContext` and `CommandResult` in `composite/service.py`, following contracts/application.md (FR-005; FR-006; FR-084). Tests: T047.
  - The Telegram principal comes from authenticated `from_user.id`; callbacks use `call.from_user.id`.
  - The web principal comes from `get_current_admin` plus an explicit main-owner mapping.
  - Caller-supplied user and tenant IDs are ignored, and a URL bearer is never a principal
- [ ] T049 Add the `/api/composite/` router scaffold to `admin_panel/server.py`, with no business routes yet (FR-005). Tests: T047.
  - Every route requires both `require_owner` and `require_main_tenant`.
  - Cookie mutations require same-origin/CSRF validation.
  - Mobile-auth tokens are rejected for composite management until parity is verified (contracts/application.md).
  - Errors use 401, 403, opaque 404, 422, 409 and 503; a replayed accepted request returns its earlier 202 or 200
- [ ] T050 [P] Write `tests/integration/test_composite_legacy_guards.py`. Every legacy path listed in T051–T053 rejects a composite product, order or subscription with an explicit reason before any side effect, and the T013–T031 characterization suites still pass for legacy rows (FR-081; SC-012)
- [ ] T051 Add `service_kind` dispatch guards to the legacy renewal and alert paths in `renewal_engine.py`, `renewal_reminders.py`, `connect_alerts.py` and `stock_alerts.py`, so that composite records never enter legacy single-panel renewal, reminder, connection-alert or stock logic (FR-081; NG-02 automatic renewal). Tests: T050; characterization T018
- [ ] T052 Add composite dispatch guards to the legacy approval, fulfillment and deletion paths (FR-081; NG-05). Composite rows are routed to `composite/service.py` or refused; legacy code never claims, provisions or rewards them. Tests: T050; characterization T013, T015 and T021.
  - `handlers_admin.py`: `cb_order_approve`, reject, delete and transfer.
  - `admin_panel/server.py`: `api_approve_order` and the delete and supply routes.
  - `config_delivery.py`, `direct_panel_provision.py` and `reseller_auto_provision.py`.
  - The purchase referral-reward hooks in `handlers_user.py`
- [ ] T053 Reject composite requests before any side effect on the unsupported channels (FR-005; NG-01; NG-02; NG-06; NG-07): the purchase, invoice and retrieval endpoints in `miniapp/server.py`; reseller supply in `admin_panel/server.py:_build_reseller_self_config`; AI shortcuts in `ai_support.py`; and the gift, custom, add-on, automatic-renewal, transfer and rename entry points in `handlers_user.py`. Tests: T050; characterization T029

### 2D — Processing control, worker skeleton and lab CLI

- [ ] T054 [P] Write `tests/integration/test_processing_control.py` (contracts/operations.md "Shared processing control"): shared admission across processes; exclusive maintenance blocking new writers and remote dispatch; an old incarnation unable to acknowledge a new restore epoch; and coordinator death leaving an explicit maintenance marker
- [ ] T055 Implement processing control in `composite/operations.py` (FR-083; constitution IV). Tests: T054.
  - An external protected control record (installation UUID, restore epoch, maintenance state), stored outside the replaceable database/FSM files and outside archives.
  - A POSIX admission lock: shared for normal transactions and dispatch, exclusive for maintenance.
  - A participant registry: incarnation, open handles and in-flight remote scope
- [ ] T056 [P] Write `tests/integration/test_worker_lifecycle.py` (plan.md "Worker lifecycle"; FR-085):
  - the singleton lock: a second worker refuses to start;
  - refusal to start on a schema, installation or restore-epoch mismatch;
  - in-flight effects reconciled before new work, and overdue original deadlines processed first;
  - a SIGTERM drain that persists uncertain dispatch and releases locks after closing database sessions;
  - unexpected death leaving intents and claims in place;
  - clock regression or large drift holding affected time decisions without moving sold clocks
- [ ] T057 Implement the worker skeleton in `composite/worker.py` (RD-06; FR-052; FR-085). Tests: T056.
  - An OS singleton lock plus a durable worker epoch.
  - Startup verification and a reconciliation hook.
  - Independent task lanes with reserved urgent capacity, and bounded calls.
  - Graceful cancellation and close, and time-sync health.
  - Discovery of main-store records without depending on bot or admin availability
- [ ] T058 [P] Implement the base lab commands in `composite/cli.py`, refusing any path outside a lab root (quickstart "Proposed post-implementation commands"; constitution VI). Tests: T034, plus a path-refusal case in `tests/integration/test_cli_lab_guards.py`.
  - `lab-seed --synthetic-only`, `schema-check`, `migrate --offline` and `lab-status`.
  - `lab-cleanup --confirm-synthetic`, which validates a disposable-root marker and stops lab writers before deleting

**Checkpoint**: characterization baselines are recorded, the schema migrates repeatably, legacy guards are in place, and the worker skeleton starts and stops safely. User-story work can begin once Phases 3–4 are also complete.

---

## Phase 3: Finance core — method-independent (NOT blocked by G-P)

**Purpose**: Everything in money handling that does not depend on a specific method's contract: the integer wallet ledger; the quote, attempt, receipt and obligation model; 30 + 73 = 103 refunds; late and extra credits; coupons; zero-price orders; one open renewal; unpayable rejection; and offline fault tests. All of it runs against the `tests/_harness/fake_payments.py` substitute. RD-07/E-005: "Implement adapter-independent finance offline; dependent method settlement is blocked until its exact contract is verified." This phase serves US1 (AS-01.2–AS-01.6), US3 (AS-03.4–AS-03.5), US5 (AS-05.4–AS-05.5), US7 (AS-07.3) and US8 (AS-08.1). Its tasks carry no story label because several stories depend on them.

**Independent Test**: With the fake adapter and synthetic wallets, every case in T059–T069 passes offline, including crash/restart and concurrency, without binding any real method.

### Tests (write first; they must fail before T070–T081)

- [ ] T059 [P] Write `tests/unit/test_pricing.py` (FR-009; AS-01.3):
  - integer floor percentage arithmetic; the tier discount first, then one code;
  - the maximum, not the sum, of the buyer-specific, permanent-tier and quantity percentages, with quantity one;
  - a percentage code applied to the tier-adjusted amount, and any code capped at that amount;
  - activity, expiry, overall and per-customer capacity, product/category and minimum/maximum checks against the tier-adjusted price;
  - reseller status alone gives no tier; no legacy early-full-renewal discount and no historic price;
  - AS-01.3: price 100 becomes 81
- [ ] T060 [P] Write `tests/unit/test_wallet_ledger.py` (FR-011; FR-025):
  - a conditional sufficient-balance debit that is never clamped;
  - a unique business effect key and a checked affected row;
  - status and `users.referral_credit` updated in one transaction;
  - a missing beneficiary refused;
  - `owed` versus `settled`: a queued credit is never complete;
  - `evidence_hold` for an unknown prior effect
- [ ] T061 [P] Write `tests/unit/test_refund_math.py` (FR-018; FR-019; SC-002):
  - AS-01.4: price 100, wallet 30 and an invoice of 73 including three quoted charges give a full refund of 103, once, at the original conversion even after settings or rates change;
  - a distinct second receipt of 73 gets a separate extra credit and is never refunded again;
  - fees outside the invoice are excluded;
  - zero actual payment gives no positive refund;
  - an unverified gross value stays an evidence gap
- [ ] T062 [P] Write `tests/integration/test_coupon_reservations.py` (FR-020; EC-08):
  - each pending checkout holds one use, consumed only by successful fulfillment;
  - the use is released once on failure, cancellation or rejection; where a refund is owed, release waits for its settlement (`release_pending_refund`);
  - cancelling an in-flight renewal restores the use, and release never revives an expired or disabled code;
  - legacy `_buy_start` and a composite checkout racing in separate processes for the last overall or per-customer use never exceed capacity;
  - coupon, test and campaign capacity stay separate
- [ ] T063 [P] Write `tests/integration/test_checkout_atomicity.py` (FR-008; FR-010; FR-012; FR-015; FR-021):
  - `confirm_checkout` creates the offer, the compatibility order (`service_kind='composite'`, unique checkout reference, no fake `config_id`), the coupon hold, the wallet debit and the work in one transaction, with crash points before and after commit;
  - quantity is one, and a repeated confirmation key returns the same checkout;
  - an open renewal is returned with no second order, debit or coupon hold (AS-03.4), while a terminal checkout does not block a new one;
  - full-wallet and validated zero-price checkouts become `authorized` with the original deadline
- [ ] T064 [P] Write `tests/integration/test_receipt_settlement.py` (FR-011; FR-013; FR-014; EC-01; SC-002):
  - unique receipt binding; a repeated hint returns the earlier outcome;
  - the same reference on another checkout or a top-up fails or returns the original binding;
  - concurrent callback and manual decisions settle once, and the authorization clock starts once;
  - mismatched or unparseable evidence becomes `mismatch_hold`;
  - a client success flag, a receipt upload alone, a missing amount, 99 % acceptance and unbounded excess never settle;
  - an indeterminate commit is resolved by an effect query before any retry
- [ ] T065 [P] Write `tests/integration/test_unpayable_and_unfunded.py` (FR-016; FR-017; EC-02). AS-01.5:
  - a retained quote survives disabled new invoices while a valid issued attempt or a legitimate manual review remains;
  - a configuration or restriction change that leaves no permitted path rejects the quote, restores the actual wallet funding within 60 s (fake clock) and releases the coupon once;
  - a temporary outage, verification uncertainty or one expired invoice does not reject it;
  - customer cancellation, owner rejection and owner-suspension or cutover rejection are terminal;
  - later valid money credits the full original quoted invoice value once, within 60 s, without fulfillment or reopening
- [ ] T066 [P] Write `tests/integration/test_zero_price.py` (FR-021):
  - a validated zero-price initial purchase, renewal or conversion is authorized with no debit, no external request and no fabricated receipt;
  - it retains the zero amount and the discount evidence, and its 15-minute deadline starts at validated confirmation;
  - it yields no positive refund and consumes neither ordinary test eligibility nor campaign capacity;
  - offers with a zero base price are refused
- [ ] T067 [P] Write `tests/integration/test_finance_offline_faults.py` (E-005 offline; SC-002; FR-072 money):
  - crash and restart at every financial commit and at the adapter create and verify boundaries, restarting with the same state and clocks;
  - every obligation settles exactly once;
  - 60-second wallet targets are measured from their specified start events;
  - no obligation is duplicated or lost across two worker processes
- [ ] T068 [P] Write `tests/integration/test_shared_wallet_paths.py`: the touched legacy `approve_topup` and `reject_order` paths now commit status and credit atomically, and their observable results match the T016 baseline except for that documented fix (constitution II; FR-074 directly dependent legacy wallet paths)
- [ ] T069 [P] Write the reusable adapter contract kit in `tests/contract/test_payment_adapter_contract.py`. It runs against the fake adapter now and is reused by every Phase 14 group (contracts/application.md "Payment adapter interface"; FR-011; FR-013). Assertions:
  - exact native amount and currency equality, with explicitly quoted provider-unit rounding as the only allowed rounding;
  - a missing, unparseable or nonfinite amount gives `EvidenceFailure`;
  - repeated hints are not distinct receipts;
  - the transaction reference is globally scoped, and the verification source is authenticated;
  - the original conversion is immutable;
  - the invoice value is the full value, including required offsets and charges

### Implementation

- [ ] T070 Implement pricing and the quote preview in `composite/finance.py` (FR-003; FR-009; FR-018; FR-025). Tests: T059.
  - FR-009 arithmetic and eligibility.
  - Preview data for the checkout disclosure: nodes, explicit GiB with a binary-unit explanation, "30 days", base price, reductions, total payable, total invoice cost and fee boundary, the store-wallet refund destination, and the notice that fulfilled service has no automatic unused-service refund
- [ ] T071 Implement the integer wallet ledger in `composite/finance.py` (FR-011; FR-025; constitution II). Tests: T060.
  - `financial_obligations` and `wallet_effects` writes with unique effect keys, and a conditional debit.
  - `users.referral_credit` updated in the same transaction.
  - `evidence_hold` for unknown prior effects.
  - Settlement marked only when the credit is spendable
- [ ] T072 Route the affected legacy wallet helpers in `database.py` (`approve_topup`, `reject_order` and the `add_wallet_credit` callers on shared wallet paths) through the T071 transaction primitive, so status and credit commit together while legacy results are preserved (RD-02; FR-074). Tests: T068; characterization T016
- [ ] T073 Implement the shared coupon reservation guard over `resource_reservations` in `composite/finance.py`, and route the legacy coupon increment in `handlers_user.py:_buy_start` and the coupon helpers in `database.py` through it (FR-020; data-model §9). Tests: T062; characterization T013
- [ ] T074 Implement `confirm_checkout` in `composite/service.py` for `initial`, `renewal` and `conversion` (FR-008; FR-010; FR-012; FR-015; FR-021). Tests: T063, T066.
  - Validate the principal, offer, ownership, price, eligibility and capacity, and enforce the partial unique open-renewal index.
  - Atomically create the immutable offer, the compatibility order, the coupon hold, a conditional wallet debit (wallet first, up to the store price) and durable work.
  - Full-wallet and zero-price checkouts become `authorized` with the original deadline.
  - An existing open renewal returns its progress instead
- [ ] T075 Implement the payment-attempt model and adapter interface in `composite/finance.py` (FR-013; RD-07). Tests: T064, T069.
  - `PaymentMethodAdapter` with `quote_attempt`, `create_or_reconcile_invoice` and `verify_receipt`.
  - An immutable accepted `AttemptQuote`: native amount, currency and scale; rate and rounding; offsets and charges; the full wallet-equivalent invoice value.
  - A durable invoice-creation intent, reconciled after an uncertain create.
  - New attempts may quote current conversion against the same retained offer.
  - A method registry that refuses any method without an owner-accepted G-P contract record. This is the fence that Phase 14 lifts one method at a time
- [ ] T076 Implement `verify_external_receipt` in `composite/service.py` (FR-011; FR-019; RD-07). Tests: T064.
  - Verify independently outside the transaction.
  - Inside one transaction: insert and bind the unique receipt, assign its role (`original_funding`, `extra_credit`, `terminal_late_credit` or `mismatch_hold`), start the authorization clock and create the fulfillment work.
  - Maintain a shared receipt-key registry across checkout and top-up contexts within one merchant namespace
- [ ] T077 Implement the `decide_manual_payment` settlement transaction in `composite/service.py` (FR-014; PC-093). Its Telegram and web wiring is fenced in Phase 14 under card-to-card. Tests: T064.
  - Main owner principal only, with no staff fallback.
  - Evidence digest; checked tenant, customer, amount, unit and method; decision, reason, idempotency key and audit.
  - The same command serves Telegram and web, and approval never implies availability
- [ ] T078 Implement full-refund obligations in `composite/finance.py` (FR-018; FR-020; FR-025). Tests: T061.
  - The refund is the actual original wallet contribution plus the full original verified invoice value in wallet units (30 + 73 = 103), at the original conversion only.
  - Coupon release is atomic with refund settlement.
  - Settlement is independent of remote cleanup and notifications
- [ ] T079 Implement `cancel_unfunded_checkout`, owner rejection and the unpayable evaluator in `composite/service.py` (FR-016; FR-017). Tests: T065.
  - The evaluator runs on configuration and payment-restriction change events.
  - Valid issued attempts and legitimate manual reviews count as funding paths; temporary outages and a single invoice's expiry are ignored.
  - When loss of every path is established: reject, restore the wallet within 60 s and release the coupon once.
  - A race with authorization resolves to a single transaction order
- [ ] T080 Implement late and extra credits in `composite/finance.py` (FR-017; FR-019). Tests: T061, T064.
  - Later valid money on a terminal checkout becomes a `terminal_late_credit` of the full original quoted value, once.
  - A distinct real extra receipt becomes an `extra_credit`, with no service, coupon use, wallet debit, carryover or deadline change
- [ ] T081 Implement the financial lane in `composite/worker.py` (FR-025; FR-072). Tests: T067.
  - Settle `owed` obligations within 60 s under normal conditions, independently of panels and notifications.
  - Hold unknown prior effects.
  - After a restart, settle verifiable overdue money within 60 s of safe processing resuming and record the missed original deadline

**Checkpoint**: the finance core passes offline and no real method is bound. Phase 14 lifts the T075 registry fence one method at a time.

---

## Phase 4: Remote execution and accounting core (Foundational for US1–US8)

**Purpose**: The shared machinery for touching panels and counting usage:
- optional 3x-UI composite capabilities and a verified-TLS panel client;
- the worker's remote lanes;
- RX-01 detect-and-repair, with the values the owner set in RX-OWN-005;
- the continuous sweep and terminal revocation;
- meter ingestion under PR-002/RD-09;
- status projection, N-01 notifications and escalation.

It includes the RX-MAN-001 lab design findings: admin-scope panel token handling (finding 3), explicit connection close (finding 5) and continuous re-verification of `restartXrayOnClientDisable` (finding 4). RX-01 and G-A are closed, so this phase is not gated, except for T097 (**Gate: E-001 probe (T082)**).

**Independent Test**: Against `tests/_harness/fake_threexui.py`, the offline equivalents of V-RX-01(i)–(p) and V-NOT-01/04/05/06 pass, and the legacy provider contracts (T019) still pass.

### E-001 capability probe (lab evidence)

- [ ] T082 Run the E-001 capability probe in two parts. **Requires authorization**: disposable standalone 3x-UI v3.9.0 / Xray-core v26.9.30 panels with `restartXrayOnClientDisable` off, direct TLS, synthetic clients only; never production. Record the results in `specs/001-composite-subscriptions/research.md` as named entries beside the decisions they support (provider capabilities beside RD-03, routing and export beside RD-05), each linked from the E-001 ledger row, following RX-MAN-001 (contracts/provider.md; quickstart "Earliest feasibility checks" item 1; OQ-3; OQ-4).
  - **Part A, as soon as it is authorized** (research.md RD03-OWN-001). Establish:
    - creation with explicit authentication, inactive creation, and canonical lookup;
    - the full mutation scope, including the inbound filter;
    - absolute updates that preserve unrelated fields and users;
    - the periodic-traffic-reset field and its scope, and the semantics of zero native quota/expiry;
    - a read-only way to fetch the panel's routing rules with the admin-scope token (used by T099);
    - candidate `confirm_runtime_state` mechanisms
  - **Part B, after T096 and T099** (RD05-OWN-001). Once T099 fixes the composite prefix, the owner rewrites the lab rules to it (for example `regexp:^cmp1_[a-z0-9]+_us$`), and the quickstart item 1 "Routing and export quick check" runs. Establish:
    - an anchored authenticated-email route namespace matching owner-prepared rules, for clients created through the panel API, with actual egress and unrelated users preserved (RD-05);
    - the exact export fields for the four fixture protocols, including the External Proxy address and port (RD05-OWN-002), compared with T096's descriptors

  Only T097 waits on this task (part A; RD03-OWN-001). The other items check the Phase 4 provider work against a real panel and are repeated at release (T255, T257).

  Owner-reported routing evidence RD05-MAN-001 and the owner's build-first decision RD05-OWN-001 (2026-10-21) are recorded in research.md under RD-05.

### Tests (write first)

- [ ] T083 [P] Write `tests/contract/test_composite_capabilities.py`: the ten non-3x-UI providers raise an explicit `UnsupportedCapability` for every composite capability, and legacy signatures, results, units and `preserve_remaining` are unchanged (re-run T019) (FR-082; constitution V)
- [ ] T084 [P] Write `tests/contract/test_threexui_composite_client.py` (RX-MAN-001 findings 3 and 5; RX-D11; FR-084):
  - peer verification rejects a wrong certificate identity, and the total call timeout is 15 s;
  - each call uses a fresh connection that is explicitly closed (the socket is observed closed and never reused from a pool), and its close time is recorded as the quarantine origin;
  - an admin-scope token is required: a node-sync or monitor token (403 on settings or single-client reads) fails binding;
  - the token never appears in logs, errors or fixtures;
  - "database is locked" is classified rejected-no-effect (lab-observed at v3.9.0, not a source guarantee);
  - `success: true, obj: null` becomes `confirmed_absent`, never zero traffic
- [ ] T085 [P] Write `tests/contract/test_threexui_composite_operations.py`, covering each operation in contracts/provider.md (FR-034; FR-041):
  - `inspect_child`;
  - `prepare_child`: inactive, with the exact persisted secret and attachments;
  - `apply_child_state`: absolute fields from a fresh canonical merge, unrelated users untouched;
  - no operation relies on a zero native quota or expiry to mean "no access" (RD03-OWN-001);
  - `observe_meter`: strict nonnegative, non-boolean integers, receipt time, and an explicit no-observation outcome;
  - `observe_inbound_clients`: a failed, timed-out or malformed read is `unknown`;
  - `revoke_child` and `confirm_runtime_state`;
  - `export_node`: every connection field comes from the panel read (RD05-OWN-002). No External Proxy entry, several values without an owner pick, or a pick that no longer exists fails readiness. A panel value that differs from the saved descriptor is reported as a mismatch and never adopted silently.
  Composite paths never call the reset, bulk-reset or update-traffic endpoints
- [ ] T086 [P] Write `tests/integration/test_rx01_detect_and_repair.py`: offline equivalents of V-RX-01(i)–(p) using the fake panel and fake clock (RD-10; PR-003; FR-085; SC-007). Check that:
  - an access-reducing state is dispatched immediately, and a timed-out access cut is read back and re-sent at once (RX-D7);
  - retries of uncertain creates and access-restoring requests wait Q = 30 s from connection close plus a reconciling read-back, and the restore wait is 30 s;
  - confirmation follows RX-D8;
  - the sweep (S = 30 s) repairs and records a late reversal without rewriting confirmation history;
  - a repair that times out escalates after R = 3 failures;
  - N/W = 3 divergences within 1 hour opens an FR-041 discrepancy, during which access-reducing repairs continue and access-restoring repairs pause;
  - 3 consecutive writes missing T = 10 s raise a panel-stall escalation, and nothing is restarted automatically;
  - the quarantine is per client, and there is one writer per physical panel;
  - the budget is five attempts, with 1/2/4/8/15 s backoff after a definite no-effect failure;
  - a node whose panel connection fields differ from its saved descriptor opens an FR-041 discrepancy and leaves published links unchanged (RD05-OWN-002 RD05-D5), and the node is not ready for a new generation until the discrepancy is resolved (RD05-D7);
  - the worked check holds: 0 → 15 → 45 → about 46 s, within 60 s
- [ ] T087 [P] Write `tests/integration/test_restart_setting_verification.py` (RX-D2; RX-MAN-001 finding 4): binding is refused when `restartXrayOnClientDisable` is on or unreadable. The sweep's lower-cadence re-verification detects a settings reset that turns it back on, blocks new composite binding and opens FR-041 drift, while existing subscriptions stay managed
- [ ] T088 [P] Write `tests/integration/test_terminal_revocation.py`: offline V-RX-01(d) and (p) (RX-D9):
  - disable at once and record final traffic;
  - delete after the quarantine and either P = 2 min without meter growth or M = 30 min since the disable, whichever comes first, batched per panel;
  - record traffic after deletion as unmetered exposure on the cleanup obligation, with the still-growing flag;
  - a stale enable released after the delete does not resurrect the client
- [ ] T089 [P] Write `tests/unit/test_accounting_ingest.py` (FR-033; FR-034; AS-02.1; EC-04; SC-003):
  - an observation requires HTTP and application success, the owned canonical object and strict integers, and receipt time is its observation time;
  - out-of-order responses are diagnostic only, and deltas are unique per `(meter, direction, epoch, predecessor)`;
  - a decrease opens a new epoch for that direction only, records a gap and never yields negative usage;
  - aliases and attachments never double-count;
  - the restart-loss annotation (at most 20 s, D12) never blocks and is never a gap or zero
- [ ] T090 [P] Write `tests/integration/test_panel_lock_coordination.py` (RD-03): the worker and legacy 3x-UI writers on a composite-bound panel serialize through the same per-panel OS lock across processes. A crash after dispatch leaves a durable uncertain-scope marker, while other panels and reads proceed
- [ ] T091 [P] Write `tests/integration/test_notifications_n01.py`: the offline core of V-NOT-01/04/05/06 (contracts/operations.md N-01; FR-085):
  - 5 s connect and 15 s operation limits;
  - at most five automatic network attempts per logical notice, across all opportunities and restarts, with 5/15/30/60 s backoff and retry-after honored;
  - 300 s opportunities that reopen automatically for still-relevant known-unsent notices;
  - uncertain sends are never resent automatically, and accepted notices never rearm;
  - overdue owner alerts are shown immediately on recovery;
  - the manual two-call, 300 s window after genuine exhaustion

### Implementation

- [ ] T092 Add optional composite capabilities to `panel_providers/base.py`, defaulting to an explicit `UnsupportedCapability` and leaving legacy signatures untouched (FR-082; constitution V): the `CompositeCapabilities` manifest, `inspect_child`, `prepare_child`, `apply_child_state`, `observe_meter`, `observe_inbound_clients`, `export_node`, `revoke_child` and `confirm_runtime_state`. Tests: T083
- [ ] T093 Implement the composite 3x-UI HTTP client in `panel_providers/threexui_composite_client.py` (RX-D11; FR-084). The legacy `_session` in `threexui_provider.py` is unchanged. Tests: T084.
  - TLS verification against the configured CA or certificate identity.
  - A 15-second total call timeout.
  - A fresh connection per call, closed explicitly by awaiting transport close (RX-MAN-001 finding 5).
  - Recorded dispatch, close and receipt times.
  - Typed transport and application errors, with sanitized messages
- [ ] T094 Implement admin-scope panel credential handling in `composite/lifecycle.py` and `panel_providers/threexui_composite_client.py` (RX-MAN-001 finding 3; constitution III; FR-084). Tests: T084.
  - The token comes from the environment or authorized configuration, and is stored only encrypted through `composite/secrets.py`.
  - A scope probe at binding requires that the restart setting and single clients are readable; a node-sync or monitor scope blocks binding.
  - The token is kept out of logs, errors, fixtures, source control and unencrypted backups.
  - Rotation re-verifies the scope.
  - The external recovery-prerequisite inventory lists the token without its value
- [ ] T095 Implement `inspect_child`, `prepare_child`, `apply_child_state`, `observe_meter`, `observe_inbound_clients` and `revoke_child` in `panel_providers/threexui_provider.py` over the T093 client (contracts/provider.md; FR-022; FR-034). Legacy methods are unchanged. Until T082 part A confirms the zero quota/expiry semantics, nothing relies on a zero native quota or expiry to mean "no access" (research.md RD03-OWN-001). Tests: T085; characterization T020.
  - The exact persisted credential and attachments, and inactive preparation.
  - Inbound-filtered absolute writes from a fresh canonical read.
  - Strict meter parsing.
  - No reset, bulk or update-traffic calls
- [ ] T096 Implement `export_node` in `panel_providers/threexui_provider.py`: one strict descriptor per logical node for VLESS REALITY, VLESS WS-CDN, Trojan gRPC and VMess TCP-TLS, carrying every field listed in contracts/provider.md "Physical routing and export". A missing field fails explicitly; there is no first-link fallback and no invented default (FR-049). Every connection field comes from the 3x-UI API, with the address and port from the inbound's External Proxy entry; the owner's node setup adds only a pick where the panel offers several values (research.md RD05-OWN-002). Tests: T085. The fields v3.9.0 actually returns are checked after implementation (T082 part B; T257). Fence lifted 2026-10-21 (OQ-3).
- [ ] T097 Implement `confirm_runtime_state` in `panel_providers/threexui_provider.py` using the mechanism selected from T082. Until a mechanism is selected, it returns an explicit unsupported/pending outcome, so fresh-authentication denial or availability is never claimed from API acceptance alone (FR-037; FR-056; FR-060; constitution VII). Tests: T085. **Gate: E-001 probe (T082); OQ-4**
- [ ] T098 Implement physical panel registration and the capability manifest in `composite/lifecycle.py`, with the owner route `POST /api/composite/panels` in `admin_panel/server.py` (FR-004; FR-033; contracts/provider.md manifest). The route only records the request; the worker performs the bounded panel reads (15 s timeout) and the screen shows the result (plan.md "Account/role/UI requests only commit intent"). Tests: T083, T087.
  - Verify the TLS identity and the admin token scope.
  - Record the 3x-UI and Xray versions (target v3.9.0 / v26.9.30) and require a standalone topology; master/node blocks binding.
  - Require `restartXrayOnClientDisable` off.
  - Record collector cadence 5 s, `restart_loss_bound` 20 s, restart-evidence availability, periodic-reset absence and `inbound_client_read`.
  - Map aliases only on verified physical ownership; ambiguous aliases are held.
  - Any absent or contradictory capability blocks binding and sales
- [ ] T099 Implement prepared bindings in `composite/lifecycle.py` (FR-004; RD-05). Deactivation keeps the management references. Tests: T085. Routing mechanism: RD05-MAN-001 (research.md RD-05); the anchored namespace is checked after implementation (T082 part B), and six-node egress and unrelated-user preservation again at release (T255). Fence lifted 2026-10-21 (OQ-3).
  - Panel-qualified inbound; protocol, transport and security fingerprint; intended egress key.
  - A versioned anchored authenticated-email route namespace, validated against owner-prepared rules that Shopvpn never writes. Shopvpn reads those rules through the panel API with the admin-scope token (T094). The read is built now and verified by T082 part A (RD03-OWN-001), so T099 does not wait for it.
  - Binding is refused unless the inbound has an External Proxy entry, or the owner's recorded pick among several still exists (RD05-OWN-002 RD05-D4).
  - Readiness and egress evidence, and an owner activation audit
- [ ] T100 Implement the worker's remote lanes in `composite/worker.py` (plan.md "Worker lifecycle"; FR-085). Tests: T086, T090.
  - Per-panel fair queues, the per-panel OS mutation lock, reserved capacity for urgent restrictions, and bounded concurrent reads.
  - At most five automatic mutation attempts, with 1/2/4/8/15 s backoff after a definite no-effect failure.
  - Missed 60-second targets marked as soon as they elapse.
  - `manual_hold` on exhaustion, with no automatic deletion.
  - Cleanup observations backing off up to five minutes
- [ ] T101 Make the affected legacy 3x-UI writers take the same per-panel OS lock when the panel is composite-bound: `renewal_engine.py`, `direct_panel_provision.py`, `test_config_provision.py`, and the 3x-UI mutations reached from `handlers_admin.py` and `admin_panel/server.py` (RD-03; FR-081). Tests: T090; characterization T018, T020 and T021
- [ ] T102 Implement the RX-01 remote-work state machine in `composite/lifecycle.py` (RD-10; FR-085; PR-003). Original clocks never restart. Tests: T086.
  - `queued` → `dispatched` → `uncertain` (`quarantine_until` = connection close + Q) → read-back → `confirmed` or a repair.
  - RX-D7: an access-reducing state is read back and re-sent immediately.
  - Retries of uncertain creates and access-restoring requests are gated by Q; the restore wait is configurable, default 30 s.
  - Confirmation follows RX-D8.
  - The owner values are configuration with defaults: Q = S = restore wait = 30 s; T = 10 s × 3; R = 3; N/W = 3 per hour; P = 2 min; M = 30 min
- [ ] T103 Implement the continuous sweep in `composite/lifecycle.py`, scheduled by `composite/worker.py` (RD-10 items 5–7; RX-D12; FR-041; FR-085). Tests: T086 (discrepancy); T085 (descriptor comparison).
  - Every S, read each composite inbound with `observe_inbound_clients`.
  - Compare every owned identity, including inactive and cleanup-pending ones, and flag deleted identities that reappear.
  - Repair mismatches and record `composite_divergences` with their exposure. A failed read is `unknown`.
  - Repeated divergence opens an FR-041 discrepancy; repair failures and stalls escalate.
  - At the T104 cadence, compare each bound node's connection fields with its saved descriptor. A difference opens an FR-041 discrepancy and never changes published links (RD05-OWN-002 RD05-D5).
  - Never restart anything automatically
- [ ] T104 Implement continuous re-verification of `restartXrayOnClientDisable` in `composite/lifecycle.py`, at a lower cadence than the sweep (RX-D2; RX-MAN-001 finding 4). A value of on, or an unreadable setting, is recorded with its time on the panel, blocks new composite binding and raises FR-041 drift with owner attention. Existing subscriptions stay managed. Tests: T087
- [ ] T105 Implement terminal revocation in `composite/lifecycle.py` (RX-D9; FR-022; constitution II). Tests: T088.
  - Disable at once and record final traffic.
  - Delete after the quarantine and either P without growth or M since the disable, batched per panel.
  - Record exposure after deletion, and the still-growing flag, on `composite_cleanup_obligations`.
  - Refunds and a local terminal status never erase the obligation
- [ ] T106 Implement meter registration and `ingest_observation` in `composite/accounting.py`, with a meter-collection lane in `composite/worker.py` (candidate cadence 15 s) (FR-033; FR-034; RD-09). Tests: T089.
  - The validity rules, and receipt time as observation time.
  - Chain, epoch, delta and gap writes in one transaction, with alias deduplication.
  - Restart-loss annotations from `server/status` `appStats.uptime` where available (D12)
- [ ] T107 Implement the status projection in `composite/service.py` for customer, owner and support views (FR-007; FR-085). Tests: T086.
  - Per subscription: the restriction state `requested`, `partial`, `uncertain` or `confirmed` (FR-007; data-model.md state transitions). `uncertain` is derived: some child has an uncertain request that could undo the state. Customer, owner and support views all show it. Per child: `confirmed_access` (`unknown`, `partial`, `confirmed_eligible`, `confirmed_fresh_auth_denied`) and the RD-10 request status (`queued`, `dispatched`, `uncertain`, `confirmed`, `manual_hold`).
  - Kept separate: stale observations, desired state, pending action, uncertain requests in quarantine, recorded divergences and sweep repairs, the confirmed remote result and delivery
- [ ] T108 Implement the N-01 delivery engine in `composite/notifications.py` (contracts/operations.md N-01; FR-085). A notification failure never blocks money, access or accounting. Tests: T091.
  - Logical notice keys, and immutable original due, target and miss records.
  - An attempt is reserved before dispatch; opportunities, backoff and retry-after.
  - Uncertainty handling, automatic catch-up, and the audited manual recovery window
- [ ] T109 Implement the shared escalation framework in `composite/service.py` (FR-039; FR-054; FR-057; FR-060; FR-068; FR-072). Tests: T086, T091.
  - Mark missed 60-second targets.
  - At 15 minutes: owner web attention, an attempted owner Telegram alert through T108, and customer pending/support status.
  - All clocks are measured from the original acceptance, readiness or final-stage event and survive restarts

**Checkpoint**: Composite remote work is repeat-safe and self-repairing offline, and its usage readings are ingested correctly. Story phases can now proceed. T097 (**Gate: E-001 probe (T082)**) waits for T082's results and OQ-4.

---

## Phase 5: User Story 1 — Purchase and receive the complete subscription (Priority: P1) 🎯 MVP

**Goal**: An eligible main-store Telegram customer selects a preset, pays and retrieves one complete subscription URL. Offline, payment means wallet or zero-price funding; external methods follow from Phase 14. The owner sees money received, provisioning, availability and refunds separately.

**Independent Test** (spec): With prepared plans, isolated customer wallets and controlled payment and panel substitutes, execute a purchase, an ambiguous creation, a delivery failure and a duplicate settlement.

### Tests for User Story 1 (write first)

- [ ] T110 [P] [US1] Write `tests/acceptance/test_us1_purchase.py` (SC-001; SC-002):
  - AS-01.1: six independent credentials, one 53,687,091,200-byte allowance and one URL; the 720-hour term starts at complete availability; a second checkout is independent;
  - AS-01.2: payment verified at 12:00 and still incomplete at 12:15 is cancelled, its credit is spendable by 12:16, cleanup is retained and nothing is delivered late; a failed push alone does not cancel;
  - AS-01.3–AS-01.5 through the finance core;
  - AS-01.6 (offline V-CAN-04)
- [ ] T111 [P] [US1] Write `tests/integration/test_fulfillment_recovery.py` (FR-007; FR-022–FR-024; FR-072):
  - identities are persisted before any call, and an ambiguous create reconciles to the same intended identity, never adopting a same-name user;
  - five of six nodes ready stays pending;
  - a crash at every fulfillment boundary; a local persistence failure is never reported as fulfillment;
  - a restart keeps the original 15-minute deadline;
  - payment, provisioning, availability, notification and cleanup outcomes stay distinguishable in the customer and owner status views (T107)
- [ ] T112 [P] [US1] Write `tests/integration/test_catalog_telegram.py` (FR-003; FR-005; FR-006; FR-010; FR-025):
  - `cmp:` callbacks take the actor from `call.from_user.id`;
  - the preview shows nodes, GiB with the binary-unit explanation, "30 days", base price, reductions, total, invoice cost and fee boundary, refund destination and the no-unused-service-refund notice;
  - buyers with reseller or discount status buy as ordinary customers, without reseller credit;
  - unsupported channels are refused;
  - the callback grammar fits Telegram's size limit and collides with no prefix in the T028 snapshot
- [ ] T113 [P] [US1] Write `tests/unit/test_composite_plans.py`, plus route cases for T116 in `tests/integration/test_composite_plan_routes.py` (FR-001; FR-002; FR-003; FR-008; FR-010): finite positive bytes; paid duration exactly 2,592,000 s; a positive base price; any positive node count (the six-node fixture and the A-only five); immutable versions; edits affecting only new offers; sold terms surviving edits; node connection fields taken from the panel read, with an owner pick required only where the panel offers several values (RD05-OWN-002); the routes list and accept only methods with an accepted contract in the T075 registry, and hand panel reads to the worker
- [ ] T114 [P] [US1] Write `tests/integration/test_initial_cancellation.py`: offline V-CAN-04 (FR-026; AS-01.6):
  - cancellation at 12:14 blocks delivery immediately, even if children become ready later;
  - the final stage starts at the earlier of a clean outcome or 12:15;
  - credit and revocation targets fall at final start + 60 s, and escalation at final start + 15 min;
  - no URL is ever delivered late;
  - if complete availability came before acceptance, the fulfilled-service rules apply instead
- [ ] T115 [P] [US1] Write `tests/integration/test_public_endpoint_minimal.py` (FR-051; FR-052):
  - the 43-character base64url token is looked up by digest on a fresh read-only snapshot;
  - an unknown, malformed or revoked token gets an opaque 404;
  - an unfulfilled or initial-delivery-blocked subscription gets a 503 with no real credentials;
  - a fulfilled, verified generation gets a 200 Base64 complete real list;
  - no write and no panel call happens

### Implementation for User Story 1

- [ ] T116 [US1] Implement the owner plan routes `GET/POST/PATCH /api/composite/plans` in `admin_panel/server.py`, backed by `composite/service.py`: immutable plan versions, prepared node bindings, ordered node remarks and egress, finite exact units and selected payment-method restrictions (FR-002; FR-003; FR-004; FR-008). Node connection fields are read from the panel when a node is saved, never typed in; the owner picks only where the panel offers several values (research.md RD05-OWN-002). The route only records the request; the worker performs the bounded panel read (15 s timeout) and the screen shows its result. The payment-method list shows and accepts only methods with an accepted contract in the T075 registry (FR-010; T215). Tests: T113
- [ ] T117 [P] [US1] Add composite plan and panel-registration screens to `admin_panel/static/app.js`. They render only the validation results and previews the server returns; behavior is covered by the T113 route tests (FR-002; FR-004)
- [ ] T118 [US1] Implement the Telegram catalog and checkout adapter (FR-003; FR-005; FR-006; FR-010; FR-025; NG-05). Tests: T112.
  - `keyboards.py`: the `cmp:` namespace, with opaque references and confirmation nonces, grammar frozen against T028.
  - `states.py`: draft references only.
  - `handlers_user.py`: dispatch composite before the inventory, naming, single-panel and referral logic in `_buy_start`; show the T070 preview; call `confirm_checkout`.
  - No purchase referral reward
- [ ] T119 [US1] Implement initial fulfillment orchestration in `composite/lifecycle.py` (FR-001; FR-022; FR-023; RD-09 "Other periods"). Tests: T111.
  - Allocate child identities, secrets, route emails and meter links transactionally before any call.
  - Prepare children inactive with their exact attachments, then converge access under the current restrictions.
  - Build a candidate generation and take initial chain-node meter readings.
  - The subscription is ready only when every intended node is confirmed
- [ ] T120 [US1] Implement the complete generation builder in `composite/exports.py`: one real URI per intended node, in saved order, with distinct owner remarks and the exact protocol fields from the T096 descriptors; encrypted content plus a fingerprint. A missing faithful export fails readiness; it never produces a shorter list (FR-049). A node with an open descriptor discrepancy is not ready for a new generation, while existing generations are still served (research.md RD05-OWN-002 RD05-D7). Tests: T086, T111, T115. Fence lifted 2026-10-21 (OQ-3).
- [ ] T121 [US1] Implement the Telegram retrieval-readiness acknowledgement in `handlers_user.py` and the availability transaction in `composite/service.py` (FR-023; data-model §4). Tests: T110, T111.
  - First verify the customer-visible details and handler, and current main-bot liveness.
  - Then, before the original deadline, atomically set `available_at`, the common `expires_at`, publication, coupon consumption and the initial entitlement period
- [ ] T122 [US1] Implement the minimal public endpoint in `composite/subscription_server.py`, a separate FastAPI/uvicorn process (FR-051; FR-052). US6 completes the gate table. Tests: T115.
  - `GET /sub/{token}` gated on a fresh read-only snapshot.
  - 404 for unknown or revoked tokens; 503 for unfulfilled or initial-delivery-blocked subscriptions; 200 with the Base64 list for a fulfilled, verified generation
- [ ] T123 [US1] Implement initial-deadline enforcement in `composite/lifecycle.py`, driven by `composite/worker.py` (FR-024; FR-025). Tests: T110, T111. If complete availability and retrieval are not reached within 15 minutes of verification or zero-price authorization, atomically:
  - set the terminal delivery block;
  - create the full refund obligation;
  - retain the children and their cleanup through terminal revocation (T105);
  - forbid late delivery
- [ ] T124 [US1] Implement paid initial cancellation in `handlers_user.py` and `composite/service.py` (FR-026). Tests: T114.
  - Require explicit confirmation, and set `initial_delivery_block` immediately.
  - Wait for the provisioning outcome or the original deadline.
  - Then run the final stage: invalidate the token, revoke all created children, and credit the full original funding and invoice value without proration.
  - 60-second targets and 15-minute escalation
- [ ] T125 [US1] Implement customer subscription details in Telegram (`handlers_user.py`; `subscription_details` and `retrieve_url` in `composite/service.py`) (FR-007; FR-008). Tests: T110.
  - Show terms, restrictions, qualified usage, checkout/fulfillment/refund progress, the support path, and the preset name plus a stable subscription identifier.
  - Return the usable URL only after full readiness and retrievability
- [ ] T126 [US1] Implement the owner subscription detail route `GET /api/composite/subscriptions/{id}` in `admin_panel/server.py`, with a view in `admin_panel/static/app.js`. It shows child pending, failure and divergence states, financial, coupon, test, campaign and cleanup obligations, and actionable progress. It exposes no secrets and is not a general history browser (FR-007). Tests: T047, T110
- [ ] T127 [US1] Send fulfillment and failure notices through N-01 (`composite/notifications.py`), with one logical key per operation. A failed push never cancels a retrievable fulfillment, and retries cause no duplicate financial or provisioning effect (FR-022; FR-023). Tests: T091, T110

**Checkpoint**: US1 passes offline with wallet-only and zero-price funding. External funding waits for Phase 14. This MVP is a validation increment, not a release: every journey is launch scope.

---

## Phase 6: User Story 2 — Use one allowance with truthful status and enforcement (Priority: P1)

**Goal**: The customer sees shared usage and expiry truthfully, and missing observations are visible. Restrictions cover every credential, and recovery never silently grants new service.

**Independent Test** (spec): Seed a fulfilled subscription with distinct and aliased meter observations, then exercise usage, clock boundaries, panel and manager outages, and recovery.

### Tests for User Story 2 (write first)

- [ ] T128 [P] [US2] Write `tests/acceptance/test_us2_allowance.py` covering AS-02.1–AS-02.6 and EC-03 (SC-003; SC-004)
- [ ] T129 [P] [US2] Write `tests/integration/test_freshness_grace_cutoff.py` (FR-035–FR-037; EC-03):
  - freshness: fresh at 60 s and warned at 61 s, with the oldest required observation time shown; fetch, refresh and restart never advance observation time;
  - the last reliable balance is retained with its genuine as-of time, otherwise shown as `unknown`;
  - grace: suspension is requested at five minutes from each meter's last trustworthy observation, and a restart at 12:04 does not extend it; known exhaustion or expiry acts immediately, with no grace;
  - cutoff: the budget is measured from the actual crossing and includes panel lag and detection; expiry needs no fresh traffic; an unreachable cutoff stays pending
- [ ] T130 [P] [US2] Write `tests/integration/test_reporting_recovery.py` (FR-039; AS-02.5):
  - restoration is automatic once identities, fresh readings, reconciled history, remaining allowance and validity, and the absence of independent restrictions are all verified;
  - every credential is confirmed within 60 s, with no dwell period, and partial enablement stays pending;
  - a lost prerequisite or a newer restriction prevents stale enablement;
  - escalation at 15 minutes, with no extension or compensation
- [ ] T131 [P] [US2] Write `tests/integration/test_usage_gap_and_drift.py` (FR-040; FR-041; AS-02.6):
  - with intact history, an owner gap settlement leaves at most 30 GiB of 50 when 20 are confirmed, keeps the gap unknown and keeps the original expiry; it is refused when purchase or revocation history is missing;
  - restart loss and usage reported after a renewal boundary are not gaps;
  - unexpected remote quota, expiry or enable changes never enlarge the entitlement;
  - a missing, renamed or mismatched identity is held for investigation, never recreated or adopted

### Implementation for User Story 2

- [ ] T132 [US2] Implement freshness and qualification in `composite/accounting.py` (FR-035). Tests: T129.
  - Current verification requires every current-serving required meter to be at most 60 s old by receipt time, with reconciled history; show the oldest required time.
  - Warn immediately on known incomplete or untrustworthy reporting.
  - Keep the last reliable balance, or show `unknown`; never zero, full or unlimited.
  - Report retired emergency meters as separate exposure
- [ ] T133 [US2] Implement the reporting-grace evaluator in `composite/lifecycle.py`. Grace runs per required meter from its last trustworthy observation. At five minutes, request `reporting_suspended` for the whole subscription, including credentials on healthy panels. Failures, retries and restarts never restart the clock, and only that subscription is affected (FR-036). Tests: T129
- [ ] T134 [US2] Implement shared cutoff in `composite/lifecycle.py`, with the urgent lane in `composite/worker.py` (candidate 5-second scheduling and expiry checks) (FR-037). Tests: T129.
  - Exhaustion at or above the exact purchased bytes, or the common expiry, triggers an access-reducing dispatch to every child, regardless of URL state or stale meters.
  - During outages cutoff is best effort, with attempts and exposure retained.
  - A successful request or a hidden URL is never reported as verified cutoff
- [ ] T135 [US2] Implement native-session handling in `composite/service.py`, with the customer and support texts in `handlers_user.py`. The wording distinguishes fresh-authentication revocation from traffic on an already-authenticated session. Exposure from existing sessions is recorded; there is no forced termination, custom session kill or disruptive restart (FR-038; NG-04). Tests: T128
- [ ] T136 [US2] Implement automatic reporting recovery in `composite/lifecycle.py`: check the prerequisites, dispatch the access-restoring change after the restore wait, target confirmation within 60 seconds and escalate at 15 minutes through T109. The original expiry keeps running (FR-039). Tests: T130
- [ ] T137 [US2] Implement owner usage-gap settlement, `POST /api/composite/subscriptions/{id}/usage-gap-settlement`, in `admin_panel/server.py` and `composite/accounting.py` (FR-040). Tests: T131.
  - Requires intact non-usage history and documented failed recovery attempts.
  - Records the gap, evidence, reason, responsible owner, accepted risk and outcome.
  - Shows the settlement-based available allowance.
  - Is never a grant, a reset or a generic resume
- [ ] T138 [US2] Implement FR-041 discrepancy handling in `composite/lifecycle.py`, with an owner web view in `admin_panel/server.py` and `admin_panel/static/app.js` (FR-041). Tests: T131.
  - Local terms stay authoritative, and verified identities are reconciled to the approved settings.
  - Mismatched identities are held for investigation.
  - An owner alert is attempted, and the customer sees truthful uncertainty.
  - Unrelated users and routes are preserved
- [ ] T139 [US2] Present qualified usage in the Telegram details (`handlers_user.py`) and owner views (`admin_panel/server.py`): GiB with the binary-unit explanation; the as-of time; delayed, unknown or settlement qualification; the store-absorbed restart-loss limitation; and recorded PR-003 temporary reversals (FR-007; FR-034; FR-035; FR-085). Tests: T128

**Checkpoint**: US1 and US2 both work independently; enforcement and freshness are proven offline, and real-panel timing is left for Phase 16.

---

## Phase 7: User Story 3 — Renew or convert a trial without changing imports (Priority: P1)

**Goal**: A customer renews, or converts a trial, through Telegram, with carryover and any forfeited time disclosed before payment. Each subscription has at most one open renewal, and the URL and credentials stay the same.

**Independent Test** (spec): Seed active, exhausted, expired, trial, disabled and owner-suspended subscriptions, and test renewal with controlled usage and payment/application times.

### Tests for User Story 3 (write first)

- [ ] T140 [P] [US3] Write `tests/acceptance/test_us3_renewal.py` covering AS-03.1–AS-03.6 and EC-05; ordinary renewal keeps the URL, every child identity, the replacement cooldown and existing restrictions (FR-048; SC-005)
- [ ] T141 [P] [US3] Write `tests/unit/test_renewal_arithmetic.py` (FR-043–FR-045; EC-05):
  - expiry = application time + 2,592,000 + min(max(old_expiry − application_time, 0), 1,296,000) s;
  - 20 GiB with 10 d 12 h left gives 70 GiB for 40 d 12 h; with 20 old days left the result is 45 days, 5 days forfeited;
  - verification strictly before the old expiry protects carryover within the original window; verification at or after expiry forfeits it;
  - old use of 53 GiB on 50 GiB, then a 50 GiB renewal, gives 50 GiB with no debt;
  - 512 MiB reported late leaves 49.5 GiB (exhausted at the boundary) or 69.5 GiB (20 GiB carried);
  - no whole-day or DST rounding
- [ ] T142 [P] [US3] Write `tests/integration/test_boundary_worker.py`: offline V-GA-05(a)–(d) and V-GA-06(a)–(d) (FR-043; FR-046; FR-047; D7; D8):
  - V-GA-05: a dropped boundary-read response is retried; an older delayed response is diagnostic only; a crash after commit and before acknowledgement returns the existing period for the same operation key; concurrent commits give one boundary;
  - V-GA-06: a blocked second panel restored before the deadline; one kept blocked through the deadline (the renewal fails and no counter changes); a reading aged past 60 s (a re-read is required); a retired emergency-exposure meter (its first later delta is `absorbed_exposure`)
- [ ] T143 [P] [US3] Write `tests/integration/test_renewal_matching_and_blocks.py` (FR-042; FR-062; AS-03.5):
  - matching uses the saved intended node signature, not the plan ID or name, and different nodes need a separate purchase;
  - after an address-only change, a subscription not yet moved still matches the new plan version, because the address is not part of the signature (RD05-OWN-002 RD05-D8);
  - accounting uncertainty, owner suspension, pending cancellation, dependent recovery and a pending move each block renewal, with an explanation and no debit; customer disable alone does not;
  - owner suspension rejects unfunded quotes and restores wallet and coupon, while an already authorized renewal resolves under suspension

### Implementation for User Story 3

- [ ] T144 [US3] Implement renewal/conversion eligibility, matching and the Telegram renewal flow in `composite/service.py` and `handlers_user.py` (FR-015; FR-042; FR-043). Tests: T143.
  - Offered presets must match the saved node semantics, using the stable logical signature that survives authorized moves. The External Proxy address and port are not part of it (research.md RD05-OWN-002 RD05-D8).
  - The preview shows the combined allowance, resulting expiry and forfeited time, qualified by continuing usage.
  - Repeated selection returns the open checkout
- [ ] T145 [US3] Implement `establish_period_boundary` in `composite/accounting.py`, running inside the effective-renewal transaction after all children are ready (FR-043; FR-046; PR-002; D7; D8). Tests: T142.
  - Re-read every required meter immediately before commit, and save immutable boundary readings per meter and direction.
  - Return `pending_stale_reading` if any current-serving reading is older than 60 s.
  - Mark a stale retired meter's first later delta `absorbed_exposure`.
  - Key the commit by the renewal operation.
  - Perform no remote mutation and no reset
- [ ] T146 [US3] Implement renewal balances in `composite/accounting.py`: `U_old`, `O`, eligible `C`, `N = A_new + C` and `U_new` across later epochs, plus the exact expiry formula with the 45-day cap, timely-payment protection and absorbed overrun (FR-043; FR-044; FR-045). Tests: T141
- [ ] T147 [US3] Implement renewal application in `composite/lifecycle.py` (FR-046; FR-048; FR-079; FR-085; A15). Tests: T140, T142.
  - Confirm every required child for the renewed terms under the current restrictions, using RD-10 confirmation; the old allowance and expiry keep governing access while the renewal is pending.
  - Reconcile obsolete old-term exhaustion or expiry disables to the renewed terms, without clearing independent restrictions.
  - Keep the URL and every child identity.
  - Then commit the period, boundary readings, grant, expiry, reminder period, checkout and coupon consumption atomically.
  - A pending cancellation then proceeds to its final stage
- [ ] T148 [US3] Implement renewal failure at the original 15-minute deadline in `composite/lifecycle.py` (FR-047; AS-03.3). Tests: T140, T142.
  - End eligibility and create the full refund, once.
  - Keep the subscription on its old terms, less actual use and time, and reconcile partial remote benefits.
  - No boundary, no counter reset and no late revival
- [ ] T149 [US3] Implement trial conversion in `composite/service.py` and `handlers_user.py` (FR-032; AS-03.6). Tests: T140.
  - Optional, customer-initiated, matching paid renewal of a fulfilled test.
  - Preserves URL and credentials, applies the normal pricing, carryover, cap, deadline and refund rules, and keeps test and campaign history and the replacement cooldown.
  - With no matching preset, it is a separate purchase
- [ ] T150 [US3] Implement the owner-suspension funding boundary as a service function in `composite/service.py`; US5 suspension acceptance invokes it (T169) (FR-062; AS-03.5). Tests: T143.
  - Block new renewal and conversion funding.
  - Reject quotes not yet fully verified, restore the wallet within 60 s and release the coupon once.
  - Credit later valid money without reopening the quote.
  - Let an already authorized renewal resolve within its window while the subscription stays suspended

**Checkpoint**: Renewal is proven offline, including the boundary-worker cases; the panel re-runs (V-GA-02/05/06) are in Phase 16.

---

## Phase 8: User Story 4 — Claim an eligible composite free test (Priority: P1)

**Goal**: An eligible customer uses the existing test flow to choose a legacy or composite test. The owner configures composite tests and the bounded launch campaign without creating extra per-plan eligibility.

**Independent Test** (spec): Use synthetic test histories and concurrent requests at the campaign boundary, and exercise failure, uncertainty, reset and conversion.

### Tests for User Story 4 (write first)

- [ ] T151 [P] [US4] Write `tests/acceptance/test_us4_tests_campaign.py` covering AS-04.1–AS-04.5, including owner-edited positive whole-hour test settings being honored and never mutating issued tests (FR-028; SC-006)
- [ ] T152 [P] [US4] Write `tests/integration/test_campaign_races.py` (FR-029; FR-030; EC-08; SC-006):
  - 149 fulfilled, 1 pending and concurrent eligible claims in separate processes never allocate a 151st place; held plus fulfilled stays at or below 150, in acceptance order;
  - a repeated request returns the same pending claim;
  - confirmed failure releases ordinary eligibility and the place once;
  - an unknown outcome keeps the holds past the deadline, forbids late delivery and alerts the owner;
  - a retry after release gets no priority;
  - 150 fulfilled closes the campaign permanently
- [ ] T153 [P] [US4] Write `tests/integration/test_test_eligibility_shared.py` (FR-027; FR-031):
  - one common `MAX_TEST_PER_USER` across legacy and composite tests, with the actor taken from `call.from_user.id`;
  - disabled, one-plan and multi-plan behavior and the legacy fallback preserved (re-run T017);
  - a general reset or maximum change never erases campaign recipients, returns places, duplicates or discards unresolved holds, or reopens the cap;
  - reset legacy users who never received the campaign may still qualify

### Implementation for User Story 4

- [ ] T154 [US4] Implement owner composite test-plan configuration in `admin_panel/server.py` and `admin_panel/static/app.js` (FR-028). Tests: T151.
  - A finite allowance with explicit MiB labels and a positive whole-hour duration; defaults 209,715,200 bytes / 3,600 s.
  - Enable and disable alongside legacy plans.
  - Edits never change tests already issued
- [ ] T155 [US4] Replace counter-only test reservation with shared, operation-based reservations (FR-027; FR-030; data-model §9). Route `database.py` `try_reserve_test_slot`/`release_test_slot` (affected scope) and `claim_test` in `composite/service.py` through `resource_reservations`, carrying identity, acceptance sequence and the unchanged 15-minute deadline. Tests: T152, T153; characterization T017
- [ ] T156 [US4] Extend `btn_test` in `handlers_user.py` (FR-027). Tests: T153.
  - Zero active plans keeps the legacy fallback; one eligible plan is selected directly; several plans show options.
  - Disabled behavior is unchanged.
  - The actor comes from `call.from_user.id`
- [ ] T157 [US4] Implement the campaign in `composite/service.py` (FR-029; FR-030; FR-074). Tests: T152.
  - 16,106,127,360 bytes for 1,296,000 s from availability.
  - An immutable cap of 150, once per authenticated user per campaign lifetime, with permanent recipients and closure at 150 fulfilled.
  - Claims pause while campaign history is unverified
- [ ] T158 [US4] Implement test fulfillment through the US1 orchestration (T119–T121), with the claim deadline in `composite/lifecycle.py` (FR-030; AS-04.3). Tests: T151, T152.
  - At 15 minutes nothing is delivered late.
  - An uncertain outcome keeps its holds, with owner web attention and an attempted alert.
  - Confirmed failure releases the holds once, and no wallet credit is created
- [ ] T159 [US4] Keep the general test reset separate in the reset paths of `handlers_admin.py`, `admin_panel/server.py` and `database.py`: reset only verified ordinary fulfilled counts, never campaign recipients or unresolved claims (FR-031; AS-04.4; AS-08.5). Tests: T153

**Checkpoint**: Free tests and the 150-place campaign work alongside legacy tests, with concurrency proven offline.

---

## Phase 9: User Story 5 — Control access and repair a leak (Priority: P1)

**Goal**: Paid and test customers can disable and resume access, replace leaked access, or cancel their own subscriptions permanently. The owner has explicit, independent controls and support remedies.

**Independent Test** (spec): Seed fulfilled subscriptions and in-flight renewal and replacement states, then interleave authorized and unauthorized customer and owner actions.

### Tests for User Story 5 (write first)

- [ ] T160 [P] [US5] Write `tests/acceptance/test_us5_controls.py` covering AS-05.1–AS-05.6 for both paid and test subscriptions; test subscriptions get the same controls (FR-032 control parity; SC-007)
- [ ] T161 [P] [US5] Write `tests/integration/test_cancellation_phases.py`: offline V-CAN-01–V-CAN-03 (FR-018; FR-058–FR-060; FR-085):
  - during the authorized-renewal wait, further funding is rejected but access, the URL and the full list remain;
  - expiry, exhaustion, customer disable, owner or reporting suspension and a recovery hold still restrict access during the wait;
  - the final stage starts at 12:05, 12:04 or 12:15, with credit and revocation targets at 12:06, 12:05 or 12:16 and escalation at 12:20, 12:19 or 12:30;
  - with an RD-10 uncertain request in quarantine, or a stalled panel, the URL is still invalidated locally and the full renewal refund still settles once;
  - earlier purchases are not refunded, nothing is prorated, and a zero-price renewal refunds nothing
- [ ] T162 [P] [US5] Write `tests/integration/test_leak_replacement.py` (FR-055–FR-057; AS-05.2; AS-05.3):
  - the old URL is invalidated and every old credential revoked immediately, even with one panel down;
  - the new URL is withheld until old fresh authentication is denied and the new set is fully ready and retrievable, with no fallback to leaked credentials;
  - the 86,400 s cooldown starts only at success and applies per subscription; pending retries continue the same operation;
  - an audited owner override bypasses the cooldown only, and emergency cutover cannot bypass the gate;
  - a node with an open descriptor discrepancy keeps the replacement pending, with the usual escalation (RD05-OWN-002 RD05-D7);
  - the 60-second target and 15-minute escalation
- [ ] T163 [P] [US5] Write `tests/integration/test_owner_bulk_and_compensation.py` (FR-061; FR-064; AS-05.5; AS-05.6):
  - the preview digest binds the exact subscriptions, customers, action and reason, and a changed selection needs a new preview;
  - subscriptions are deduplicated and results kept per member; an interrupted bulk action resumes only unfinished members;
  - owner suspension is status-only immediately;
  - compensation of 10 × 50 totals 500, with one credit per unique customer across subscriptions, recovery without repeats, and no change to access, terms or tests
- [ ] T164 [P] [US5] Write `tests/integration/test_block_separation.py` (FR-063; EC-09):
  - a shop-account block, the customer blocking the bot and notification outages never suspend, invalidate, cancel or refund;
  - verification, credits, accounting, expiry and cleanup continue;
  - staff block permission confers no owner powers (re-run T031)

### Implementation for User Story 5

- [ ] T165 [US5] Implement customer disable and resume in `handlers_user.py` and `composite/service.py` (FR-053; FR-054; AS-05.1). Tests: T160.
  - Disable persists `customer_disabled` without pausing the term and enqueues access-reducing work for every child.
  - Resume clears only that flag and requires current eligibility.
  - 60-second confirmation and 15-minute escalation; the legacy test toggle is preserved
- [ ] T166 [US5] Implement leak replacement in `composite/service.py` and `composite/lifecycle.py` (FR-055; FR-056; FR-057). Tests: T162.
  - On acceptance, revoke the token and set `replacement_delivery_block` immediately.
  - Preallocate replacement identities with fresh UUIDs or Trojan passwords, and revoke every old credential at once.
  - Publish the new token only after old fresh authentication is confirmed denied and the new set is fully ready and retrievable. A node with an open descriptor discrepancy is not ready (research.md RD05-OWN-002 RD05-D7).
  - Start the 86,400 s cooldown at success.
  - Explain re-import and the existing-session limitation
- [ ] T167 [US5] Implement the owner leak-replacement override, `POST /api/composite/subscriptions/{id}/leak-replacement`, in `admin_panel/server.py` (FR-057). Tests: T162.
  - Records a reason and audit; it bypasses only the cooldown and cannot compete with a pending operation.
  - A failed override starts no cooldown
- [ ] T168 [US5] Implement permanent cancellation in `handlers_user.py`, with explicit irreversible confirmation, and `composite/lifecycle.py` (FR-058; FR-059; FR-060). Tests: T161.
  - Acceptance blocks renewal funding.
  - When does the final stage start? For fulfilled service with no in-flight renewal, at acceptance. With an authorized renewal, at its success, its confirmed terminal failure or the original deadline.
  - The final stage invalidates the token, revokes every child and fully refunds the in-flight renewal.
  - Separate 60-second credit and revocation targets, and 15-minute escalation.
  - No reactivation and no duplicate refund
- [ ] T169 [US5] Implement owner single and bulk suspend, resume and permanent cancel in `admin_panel/server.py` (`/api/composite/actions/preview` and `/confirm`), `composite/service.py` and `admin_panel/static/app.js` (FR-061; FR-062). Tests: T163.
  - Preview and confirm with a reason; deduplication; operations and results kept per member.
  - Owner suspension is status-only from acceptance and invokes T150
- [ ] T170 [US5] Implement support wallet compensation, `POST /api/composite/compensation/preview` and `/confirm`, in `admin_panel/server.py` and `composite/finance.py`: an equal positive amount per unique main-store customer, prior refunds and credits shown, one unique effect per customer, and recovery of interrupted batches (FR-064). Tests: T163
- [ ] T171 [US5] Keep shop-account blocks separate in `handlers_user.py` and `blocked_user.py`: a block restricts interaction and eligibility only, and composite processing continues for blocked accounts (FR-063). Tests: T164
- [ ] T172 [US5] Enforce admissibility of protective controls in `composite/service.py`. Disable, leak repair and cancellation are accepted while an unpaid renewal quote, an RX-01 quarantine, a panel stall or other work is pending. They are ordered through current intent, never refused with a generic busy error (FR-015; FR-085; EC-06). Tests: T160, T161

**Checkpoint**: Protective controls and their precedence hold across payment and remote failures offline.

---

## Phase 10: User Story 6 — Refresh a complete, understandable VPN list (Priority: P1)

**Goal**: Customers import one URL in their chosen required client and receive each configured real node, plus clearly distinguished information entries. This completes the T122 minimal endpoint.

**Independent Test** (spec): Validate the complete export cases offline. The controlled import, refresh and traffic checks on recorded versions of all five required applications are E-003, in Phase 16.

### Tests for User Story 6 (write first)

- [ ] T173 [P] [US6] Write `tests/contract/test_subscription_http_gates.py` (FR-049; FR-051; AS-06.1 offline part; AS-06.2; AS-06.3; SC-008):
  - the five-priority gate table of contracts/subscription-http.md;
  - the six-node fixture lists its real entries in configured order, and a panel's duplicate native addresses never add unconfigured nodes;
  - `HEAD` applies the same gates without a body, and other methods get 405;
  - `Content-Type: text/plain; charset=utf-8`, `Cache-Control: no-store, private` and `Referrer-Policy: no-referrer`;
  - no redirect to a replacement token;
  - owner suspension serves information entries only, with no real child secret and no private reason;
  - outage, expiry, exhaustion, customer disable, stale-reporting suspension and a pending cancellation during an authorized renewal all keep the complete list;
  - an uncertain recovery generation gets 503;
  - a concurrently accepted restriction wins the next snapshot
- [ ] T174 [P] [US6] Write `tests/unit/test_info_entries.py` (FR-050; EC-11):
  - the three selected VLESS structures (`time.alarm:10`, `data.alarm:10`, `status.alarm:10`, `encryption=none&packetEncoding=xudp`), using synthetic UUIDs unrelated to purchased credentials;
  - UTF-8 fragments percent-encoded exactly once;
  - ASCII standard Base64 of LF-separated lines with a final newline;
  - expiry text; quota text with as-of, unknown and settlement qualification; requested/pending/confirmed restriction text;
  - UTC times with an explicit zone, and a conservative decimal that never exceeds the exact remaining bytes
- [ ] T175 [P] [US6] Write `tests/integration/test_subscription_no_side_effects.py` (FR-052; SC-008):
  - requests run on a read-only database handle with the network denied;
  - no panel call, provisioning, enable, renewal, reset, credit, observation-time advance or acknowledgement happens;
  - token-bearing paths are redacted in access logs, and a secret scan of logs and bodies passes;
  - after fulfillment, with the bot, admin and worker down, the last verified generation is still served, with honestly stale accounting

### Implementation for User Story 6

- [ ] T176 [US6] Complete the gate engine in `composite/subscription_server.py`, in contracts/subscription-http.md priority order, evaluated on a fresh transaction for every request (FR-051). Tests: T173.
  1. 404 for an unknown, revoked or superseded token, or once final cancellation has started.
  2. 503 for an unfulfilled or initial-delivery-blocked subscription, a pending leak delivery or an unverified recovery generation.
  3. 200 with information entries only for a verified owner suspension.
  4. 200 with the complete current list otherwise.
  5. 503 when no trustworthy complete configuration exists
- [ ] T177 [US6] Implement the information-entry renderer in `composite/exports.py` using the selected VLESS encoding (FR-050; PR-001). Tests: T174.
  - Content comes from the current expiry, qualified usage with its source time, and the public restriction/support snapshot.
  - Entries create no child, meter or allowance, and do not count toward readiness
- [ ] T178 [US6] Harden independence and secrecy in `composite/subscription_server.py` (FR-052; FR-084). Tests: T175.
  - A read-only SQLite URI connection, with the decryption key used only for export rendering.
  - Sanitized access logging, without token paths.
  - No shared-cache headers and no stale-success fallback.
  - An explicit 503 on endpoint, HTTPS, database or key outage
- [ ] T179 [US6] Add import and refresh guidance for the five required clients to Telegram retrieval in `handlers_user.py`: one URL; imported names are snapshots until refreshed; information entries may fail to connect when selected (PR-001); a successful download does not mean the VPN is reachable (FR-049; FR-050; FR-052). Tests: T110

**Checkpoint**: The public endpoint's gates, encoding and secrecy are proven offline; real five-client compatibility is left to E-003 (T257).

---

## Phase 11: User Story 7 — Replace a failed or filtered server (Priority: P1)

**Goal**: The owner moves one or many existing subscriptions to prepared equivalent infrastructure, while customers keep their subscription URLs and entitlement history.

**Independent Test** (spec): Prepare equivalent synthetic targets and a mixed active/inactive cohort. Verify individual completion, emergency authorization, the sales pause and the recorded capacity targets.

### Tests for User Story 7 (write first)

- [ ] T180 [P] [US7] Write `tests/acceptance/test_us7_moves.py` covering AS-07.1–AS-07.4 and EC-07 (SC-009)
- [ ] T181 [P] [US7] Write `tests/integration/test_move_batches.py` (FR-065–FR-071):
  - the preview shows the exact subscriptions, customers and old-to-new mapping, with inactive members visible;
  - only moved children get fresh secrets; unmoved credentials and the token stay unchanged;
  - an address-only move to the same inbound (RD05-OWN-002 RD05-D5) gives fresh secrets and the new address on the same token. The old client is disabled at publication and its secret is refused on that inbound; it is deleted only after its final usage is read (RD05-D6). Only the old plan version stops selling (RD05-D8);
  - each subscription switches only when its moved set is ready; one failure never blocks or rolls back the others, and a retry never re-moves completed members;
  - inactive subscriptions move inactive, owner-suspended ones stay status-only, cancelled ones are cleanup-only and recovery-held ones are ineligible;
  - emergency cutover removes old meters from current-serving freshness while their exposure stays tracked, and it cannot bypass leak repair;
  - a notice per member;
  - an offline 150 × 5 scheduling smoke test showing the cutoff and accounting lanes are not starved (not the E-004 benchmark)

### Implementation for User Story 7

- [ ] T182 [US7] Implement move preview and confirm, `POST /api/composite/replacements/preview` and `/confirm`, in `admin_panel/server.py`, `composite/service.py` and `admin_panel/static/app.js`, with a separate explicit emergency authorization (FR-065; FR-066; FR-067). Tests: T181
- [ ] T183 [US7] Implement per-subscription move execution in `composite/lifecycle.py` (FR-065; FR-067). Tests: T181.
  - Preallocate fresh identities for the moved children.
  - Prepare and verify replacement readiness and trustworthy metering.
  - Publish the changed descriptors on the same token only when the set is complete.
  - Keep unmoved children, history and cooldown, and send old identities through terminal revocation.
  - The target may be the same inbound with a new address: an address-only change (RD05-OWN-002 RD05-D5). New secrets and fresh client names are issued as in any move. The old identity is disabled when the new list is published and deleted after the RX-D9 wait, never before its final usage is read (RD05-D6).
  - Changing a management API address alone is not a move
- [ ] T184 [US7] Implement explicit emergency cutover in `composite/lifecycle.py` and `composite/accounting.py` (FR-066; D8). Tests: T181.
  - Requires the old management API to be unreachable, and owner review of the last confirmed usage.
  - Records the store's acceptance of unmeasured old consumption, the pending old revocation and the exposure.
  - Retired meters leave current-serving freshness.
  - Old usage confirmed later is reconciled once under the overrun rules
- [ ] T185 [US7] Handle inactive and terminal histories in `composite/lifecycle.py` (FR-070). Tests: T181.
  - Fulfilled histories that are expired, exhausted, customer-disabled, owner-suspended or reporting-suspended move in their inactive state.
  - Cancelled subscriptions are cleanup-only.
  - Recovery-held cases stay ineligible
- [ ] T186 [US7] Implement catalog and checkout behavior at cutover in `composite/service.py` (FR-071; AS-07.3). Tests: T181.
  - Stop new offers and claims on the old topology. For an address-only change, that means the old plan version (research.md RD05-OWN-002 RD05-D8).
  - Reject affected unfunded quotes through T079, with wallet and coupon release and the late-credit rules.
  - Block renewal funding while the subscription's move is pending.
  - Authorized work keeps its terms and deadlines.
  - Reopen sales when the owner activates a prepared equivalent offer
- [ ] T187 [US7] Send a move notice per subscription through N-01 in `composite/notifications.py` as each one completes, without waiting for the batch. The notice states that the URL is unchanged and the entitlement is not reset, and asks the customer to refresh (FR-069). Tests: T181
- [ ] T188 [US7] Implement move scheduling and overdue handling in `composite/worker.py` (FR-068). Tests: T181.
  - Authorized move clocks include queueing and retries, and never restart.
  - Unfinished work is marked overdue at 15 minutes, with owner attention and an attempted alert.
  - The current accounting and cutoff lanes are never starved

**Checkpoint**: Equivalent moves are independent per subscription and keep URLs and history; the 150 × 5 timing is measured in Phase 16 (T259).

---

## Phase 12: User Story 8 — Recover safely and retain responsibilities (Priority: P1)

**Goal**: After a process or host loss, the owner can tell verified recovery apart from unresolved history. Neither customer money nor revoked access is replayed from an old snapshot.

**Independent Test** (spec): Using disposable synthetic backups and controlled newer external evidence, exercise an intact-history restart, a stale restore, lost identities and protected destructive actions.

### Tests for User Story 8 (write first)

- [ ] T189 [P] [US8] Write `tests/acceptance/test_us8_recovery.py` covering AS-08.1–AS-08.5 and EC-08–EC-10 (SC-010)
- [ ] T190 [P] [US8] Write `tests/integration/test_capture_restore.py` (FR-073; FR-083):
  - a coherent capture with active writer processes, using an online backup per file under the writer barrier, with manifest and checksums;
  - both reseller archive names;
  - missing, corrupt, skewed, unexpected, duplicate and path-traversal members rejected in staging;
  - the complete pre-restore set retained, writers verified closed, the restore epoch incremented, and stale purges and leases fenced;
  - an interrupted replacement staying in maintenance with per-member state
- [ ] T191 [P] [US8] Write `tests/integration/test_backup_delivery_b01.py`: offline V-BAK-01 with a controlled SFTP substitute (FR-076):
  - 10 s connect, 30 s no-progress and 120 s attempt limits;
  - three attempts with 15/45 s backoff; deadline capture + 600 s, or any earlier still-current capture + 900 s;
  - unique attempt paths; a partial file, a size-only match or a file with a live writer never becomes a recovery point;
  - the predecessor is retained, and a transfer never resets capture age;
  - a pinned host-key mismatch stops all attempts
- [ ] T192 [P] [US8] Write `tests/integration/test_destructive_guards.py` (FR-075; FR-083; AS-08.5):
  - factory reset, panel force deletion, customer, plan or order removal, tenant tier change, deletion, ownership transfer and stale purge are all refused when they would lose protected evidence, pending work, campaign history or sole cleanup responsibility;
  - refusals carry sanitized blocking IDs and the allowed paths, and `force` cannot bypass them;
  - an ordinary test reset still works (re-run T027)
- [ ] T193 [P] [US8] Write `tests/integration/test_catch_up_and_holds.py` (FR-072–FR-074; AS-08.1; AS-08.2):
  - a manager returning at 12:30 after a 12:15 deadline starts no new window;
  - verifiable overdue credit is spendable within 60 s of safe processing resuming;
  - unknown effects are held, and overdue attention is shown immediately;
  - a stale snapshot that predates a cancellation, rotation, refund and campaign grants publishes no unverified generation, repeats no credit and reopens no campaign place;
  - verified cases are released individually

### Implementation for User Story 8

- [ ] T194 [US8] Integrate shared admission and maintenance into the affected legacy writers (contracts/operations.md; FR-083): main-database connections in `database.py`; jobs, reconciler and purge in `bot_manager.py`; `main.py`; `fsm_storage.py`; `admin_panel/server.py`; and `miniapp/server.py` all register as participants and honor maintenance. Tests: T190; characterization T024 and T025
- [ ] T195 [US8] Implement `enter_maintenance` and `leave_maintenance` in `composite/operations.py` (FR-083; FR-085). Tests: T190.
  - Close admission and drain bounded work.
  - Stop the reconciler, purge, cache, notifier and public readers before replacement, and verify they are closed; a failure is blocking.
  - Persist dispatched uncertainty, and never shorten a quarantine.
  - Reopen only version-compatible participants, with the worker starting in reconciliation mode
- [ ] T196 [US8] Implement `capture_recovery_set` in `backup.py` and `composite/operations.py`, at a candidate five-minute cadence (FR-076; RD-08). Tests: T190.
  - A brief coherent writer barrier that touches no panels and no sessions.
  - An SQLite online backup per member, with schema, integrity and invariant validation.
  - A manifest with installation and capture epoch and checksums, including the required dependent tenants and FSM.
  - Versioned authenticated encryption, with keys stored separately, and documented exclusions
- [ ] T197 [US8] Implement B-01 off-host delivery in `backup.py` (FR-076; contracts/operations.md B-01). Tests: T191.
  - SFTP with a pinned, verified host identity in the affected composite path, remediating `known_hosts=None` there.
  - Unique immutable attempt paths, a completion manifest and a full read-back checksum.
  - Persisted attempts and budget, the retained predecessor and the last verified capture age
- [ ] T198 [US8] Implement `preflight_restore` and `restore_validated_set` in `backup.py`, and route the restore callers in `handlers_admin.py`, `admin_panel/server.py` and `manage.sh` through them (FR-073; FR-083). Tests: T190; characterization T026.
  - Decrypt in isolation and validate the whole staged set.
  - Retain the complete pre-restore set and newer evidence externally.
  - Verify writers are closed and increment the restore epoch.
  - Replace coherently, migrate, then start reconciliation; never report a silent main-first success
- [ ] T199 [US8] Implement restore reconciliation and recovery cases in `composite/operations.py` and `composite/service.py` (FR-073; FR-074). Tests: T193.
  - Evaluate newer local evidence, verifiable payment references, panel identities and runtime state, token/generation/revocation facts, usage and boundary evidence, and coupon, test and campaign outcomes.
  - Hold uncertain effects, and restrict or clean up only verified owned identities.
  - Release verified cases individually; campaign claims pause while campaign history is unverified.
  - An irrecoverable non-usage gap requires a recorded governed remediation
- [ ] T200 [US8] Implement intact-history catch-up in `composite/worker.py` (FR-072; AS-08.1). Tests: T193.
  - On restart, act on overdue original clocks first and record missed deadlines.
  - Settle verifiable overdue money within 60 s, and show overdue owner attention immediately.
  - Never grant new time or data, and never restore revoked access
- [ ] T201 [US8] Implement destructive-operation guards in `database.py` (`factory_reset`, `delete_panel_server`, `wipe_agent_state`, `switch_agent_tier`, `transfer_reseller_ownership`) and on the `bot_manager.py` deferred purge, checked within the same admission and transaction boundary (FR-075; FR-083). Deactivation excludes new offers but keeps management and cleanup. Tests: T192
- [ ] T202 [US8] Implement recovery-point health in `admin_panel/server.py` and `composite/operations.py` (FR-076; EC-09). Tests: T191.
  - Show the last verified recoverable capture time and age, overdue or unknown protection, and the repair action, with an attempted N-01 owner alert.
  - A backup failure never suspends or refunds customers
- [ ] T203 [US8] Implement `recovery-status` in `composite/cli.py`, and document the prepared-host recovery procedure in `docs/composite-subscriptions/OPERATIONS-RUNBOOK.md` (FR-077; AS-08.4). Tests: T189.
  - The four-hour target runs from owner initiation with every prerequisite available; waiting for prerequisites is reported separately.
  - Retries never restart the clock.
  - Partial, held and overdue functions are reported truthfully

**Checkpoint**: Recovery, stale-restore holds and destructive guards are proven offline; the recovery point objective (RPO) and recovery time objective (RTO) are measured in Phase 16 (T260).

---

## Phase 13: User Story 9 — Receive useful paid-service reminders (Priority: P2)

**Goal**: For each paid period, a paid customer receives one logical expiry reminder and one quota reminder when renewal is eligible. The owner controls the existing valid thresholds.

**Independent Test** (spec): Seed paid reminder periods with carried data and restricted states, and exercise boundaries and delivery failures without sending real messages.

### Tests for User Story 9 (write first)

- [ ] T204 [P] [US9] Write `tests/acceptance/test_us9_reminders.py` covering AS-09.1–AS-09.3 (SC-011)
- [ ] T205 [P] [US9] Write `tests/integration/test_reminder_eligibility.py`: offline V-NOT-02 and V-NOT-03 (FR-078–FR-080):
  - defaults of 120 h and 80 %, and the alternative remaining-data mode (default 2 GiB) without double sending;
  - one logical notice per type per successful paid period, using the new plus carried allowance;
  - owner, recovery, movement and renewal blocks make the notice wait without consuming it, and it resumes automatically;
  - obsolete notices are cancelled when terms change, on cancellation and on expiry;
  - customer disable alone still permits reminders;
  - no reminder for still-free tests, no coupon, and no rearming on toggle, refresh, restart or replacement

### Implementation for User Story 9

- [ ] T206 [US9] Implement reminder periods and the evaluator in `composite/notifications.py` (FR-079; FR-080). Tests: T205.
  - The period is created by the T121 or T147 commit.
  - Thresholds are snapshotted from the existing main-store reminder settings (`settings_schema.py`).
  - The original due time is when condition and eligibility both hold; the normal target is five minutes.
  - Delivery goes through N-01
- [ ] T207 [US9] Add composite reminder messages, with details and renewal links, to `handlers_user.py` and `keyboards.py`. The quota wording stays accurate when usage exceeds 80 %, and messages make no connection-status claims; legacy reminders are unaffected thanks to the T051 guard (FR-078; FR-080). Tests: T204

**Checkpoint**: All nine journeys are implemented offline. External payment still needs Phase 14, and release still needs Phases 15–16.

---

## Phase 14: Payment method bindings — BLOCKED until each method's G-P contract is verified (except T215)

**Purpose**: Bind each candidate configured method to the Phase 3 adapter interface (T075) and lift the registry fence for that method only.

**⛔ Gate G-P / E-005** (RD-07: "dependent method settlement is blocked until its exact contract is verified"):
- Every task in this phase carries **Gate: G-P (method)**, except T215, which only enforces the GP-OWN-001 exclusions.
- Each group starts with its evidence task. That task adds a G-P entry for the method under RD-07 in `specs/001-composite-subscriptions/research.md` (OQ-5 rule: gate-closing evidence goes in research.md, raw logs outside the repository), recording:
  - the native amount, currency and scale;
  - the merchant namespace and the transaction/charge reference, with its uniqueness and reuse rules;
  - quoted charges and fees; conversion and rounding evidence; the full original wallet-equivalent invoice value;
  - the independent verification source; uncertain create/verify recovery; duplicate and late notifications.
- The owner then accepts the contract record. No later task in the group starts before that.

**If a contract cannot be verified safely**, the method is not bound. It stays unavailable to composite plans, with the reason recorded and reported to the owner for remediation or an explicit governance decision. It is neither dropped silently nor enabled silently (RD-07; PC-092).

**Scope**: Adding a brand-new gateway is out of scope (PC-092: "adding a new gateway is outside this feature") and would be a separate feature. Groups are independent of each other and can proceed in any order once T208 is done.

### Shared inventory

- [ ] T208 Produce the secret-redacted inventory of enabled methods for the main store, plus plan-level method restrictions, as a G-P entry under RD-07 in `specs/001-composite-subscriptions/research.md` (E-005; FR-010; RD-07). **Gate: G-P (inventory)**; **Requires authorization**. An enabled method outside the six candidate groups is recorded and stays unavailable to composite plans under owner decision GP-OWN-001 (OQ-1, OQ-2; enforced by T215); it is neither bound nor silently dropped. Inventory:
  - manual card-to-card (`card_to_card_enabled`) and automatic card-to-card (`card_to_card_auto_enabled`, SMS forwarder);
  - Aban;
  - the extra gateways `zarinpal`, `aqayepardakht`, `tetra98`, `cubepay`, `nowpayments` and `tgstars`;
  - BluPal, Noapay, Plisio/crypto, and custom gateways

### Group A — Card-to-card (manual; FR-014; V-RCP-01)

- [ ] T209 G-P evidence for manual card-to-card: an owner-manual contract record as a G-P entry under RD-07 in `specs/001-composite-subscriptions/research.md`, using test cards or a non-production setup and no customer money (FR-013; FR-014; PC-093). **Gate: G-P (card-to-card)**; **Requires authorization**. Record:
  - the native unit (Toman or Rial, through `card_to_card_payment.normalize_amount`/`rial_to_toman`);
  - whether the `create_invoice` random offset applies in manual mode;
  - the merchant namespace (card or account);
  - the bank reference or tracking evidence the owner checks, and its uniqueness and reuse rules;
  - the owner's acceptance of the contract
- [ ] T210 [P] Write `tests/contract/test_method_card_to_card.py` using the T069 contract kit, with synthetic evidence (FR-011; FR-013). **Gate: G-P (card-to-card)**
- [ ] T211 [P] Write `tests/integration/test_receipt_linkage_composite.py`: offline V-RCP-01. Re-runs T014 and T015 for legacy rows (FR-005; FR-011; FR-014; SC-002). **Gate: G-P (card-to-card)**.
  - The FSM path and the database fallback, with lost or stale FSM, several pending legacy and composite orders, the crypto-invoice exclusion, a forged actor or order, duplicate uploads, and simultaneous Telegram and web approval.
  - Composite dispatch precedes receipt persistence and admin notification on both paths.
  - Receipt upload or latest-order selection alone never settles
- [ ] T212 Implement the manual card-to-card adapter in `composite/payment_methods/card_to_card.py`. Its quote follows the T209 contract: native amount, offset if the contract has one, and wallet-equivalent invoice value. Attempts follow the manual receipt flow (the `pay_card2card` path in `handlers_user.py`) and never call `card_to_card_payment.create_invoice`, which creates the automatic mode's amount-matched invoice (GP-OWN-001 GP-D1). The merchant namespace and bank reference feed the unique receipt key (FR-013; RD-07). Tests: T210. **Gate: G-P (card-to-card)**
- [ ] T213 Dispatch composite receipts on both linkage paths in `handlers_user.py`, before receipt persistence and admin notification (FR-014; V-RCP-01). Tests: T211. **Gate: G-P (card-to-card)**.
  - The FSM `receive_receipt` path, and the fallback at line 5173.
  - Verify the tenant, customer, checkout and attempt association.
  - When the candidate is ambiguous, require explicit selection of an owned checkout.
  - Receipt reuse and duplicate-settlement checks are never weakened
- [ ] T214 Wire owner manual review to `decide_manual_payment` (T077) from both interfaces (FR-014; PC-093). Tests: T211. **Gate: G-P (card-to-card)**.
  - Telegram: composite review callbacks in `handlers_admin.py`, owner-only, not gated by `admin_only` staff permission.
  - Web: composite dispatch in the existing approve/reject route in `admin_panel/server.py`, with a review view in `admin_panel/static/app.js`.
  - Both interfaces run one settlement transaction and one audit record; delegated staff are refused; approval never implies availability
- [ ] T215 Keep automatic card-to-card and every method outside the six candidate groups unavailable to composite plans, per owner decision GP-OWN-001 in research.md (OQ-1, OQ-2; FR-010; FR-011). Legacy use of those methods is unchanged. Tests: new cases in `tests/contract/test_payment_adapter_contract.py`, `tests/integration/test_catalog_telegram.py` and `tests/integration/test_card_auto_exclusion.py`. **Gate: none**: it enforces an exclusion and needs no method evidence. Depends on T075, T116 and T118, not on T208.
  - The T075 registry holds no contract for them, so it refuses quotes and attempts.
  - The composite plan routes in `admin_panel/server.py` (T116) do not list them, and refuse them if submitted.
  - The composite checkout in `handlers_user.py` (T118) never offers them.
  - The SMS-forwarder webhook (`miniapp/server.py` `/api/webhooks/sms-forwarder`) and the `pay_card_auto` callbacks in `handlers_user.py` never create or complete a composite invoice: `card_to_card_payment.match_and_complete` finds no composite invoice to match.
  - Adding one later needs its own Phase 14-style group (GP-OWN-001 GP-D2)

### Group B — NOWPayments

- [ ] T216 G-P evidence for NOWPayments as a G-P entry under RD-07 in `specs/001-composite-subscriptions/research.md`, using a sandbox or non-production account (FR-011; FR-013; FR-018). **Gate: G-P (NOWPayments)**; **Requires authorization**. Record:
  - the USD price, derived from Toman with the configured crypto rate and recorded as an exact Decimal;
  - the invoice versus `payment_id` identity, and partial or over payments (`nowpayments_classify`);
  - server-side `payment_status` verification;
  - the IPN signature (`nowpayments_ipn_secret` is optional today);
  - network fees inside versus outside the invoice, the merchant namespace, and reference uniqueness
- [ ] T217 [P] Write `tests/contract/test_method_nowpayments.py` using the T069 kit. An unsigned or unauthenticated IPN is only a hint and never settles; a partial payment never funds the purchase; an overpayment is not accepted automatically (FR-011; FR-019). **Gate: G-P (NOWPayments)**
- [ ] T218 Implement `composite/payment_methods/nowpayments.py` over `extra_gateway_clients.py`. The quote has exact USD minor units and the recorded rate. Invoice creation is keyed by a durable order intent and reconciled after a timeout. Verification uses server-side payment status (FR-013; RD-07). Tests: T217. **Gate: G-P (NOWPayments)**
- [ ] T219 Dispatch composite NOWPayments callbacks at `miniapp/server.py` `/api/webhooks/nowpayments`, before the legacy `extra_gateway_payment.py` finalization, and register NOWPayments references in the shared receipt-key registry (T076) for the same merchant namespace, so legacy top-ups cannot reuse them (FR-011; RD-07). Tests: T217. **Gate: G-P (NOWPayments)**

### Group C — Tetra (tetra98)

- [ ] T220 G-P evidence for Tetra98 as a G-P entry under RD-07 in `specs/001-composite-subscriptions/research.md` (FR-011; FR-013). **Gate: G-P (Tetra98)**; **Requires authorization**. Record:
  - `tetra98_create` with `amount_toman` and the `authority` identity;
  - which fields `tetra98_verify` returns, in particular whether it confirms the amount and a payment reference;
  - the `/api/pay-return/tetra98` callback, the requery behavior, and fees
- [ ] T221 [P] Write `tests/contract/test_method_tetra98.py` using the T069 kit. If the verify response cannot confirm the exact amount and reference, the contract test expects `EvidenceFailure` and the method stays unbound (FR-011). **Gate: G-P (Tetra98)**
- [ ] T222 Implement `composite/payment_methods/tetra98.py` over `extra_gateway_clients.py`: an exact Toman quote, an invoice keyed by a durable intent, server-side verification and recovery after an uncertain create (FR-013). Tests: T221. **Gate: G-P (Tetra98)**
- [ ] T223 Dispatch composite Tetra98 returns and callbacks at `miniapp/server.py` `/api/pay-return/{gateway}`, before the legacy `extra_gateway_payment.py` handling. The return is treated as a hint followed by server-side verification, and the reference is registered with T076 (FR-011). Tests: T221. **Gate: G-P (Tetra98)**

### Group D — CubePay (fee included in invoice cost)

- [ ] T224 G-P evidence for CubePay as a G-P entry under RD-07 in `specs/001-composite-subscriptions/research.md` (FR-013; FR-018). **Gate: G-P (CubePay)**; **Requires authorization**. Record:
  - the `cubepay_payable_toman` fee semantics (`cubepay_fee` up to 100 is a percentage; above that, a fixed Toman amount);
  - the ×10 `expected_rial` used by `cubepay_verify`;
  - that the fee is part of the quoted invoice cost; the authority and reference identity; and the callback
- [ ] T225 [P] Write `tests/contract/test_method_cubepay.py` using the T069 kit (FR-013; FR-018). **Gate: G-P (CubePay)**.
  - The fee is disclosed before payment and included in the original wallet-equivalent invoice value.
  - A full refund returns wallet funding plus the whole invoice, fee included (the 30 + 73 pattern).
  - Rial/Toman ×10 equality is exact
- [ ] T226 Implement `composite/payment_methods/cubepay.py` over `extra_gateway_clients.py` and `extra_gateway_payment.cubepay_payable`: the quote includes the fee, and verification checks exact Rial equality (FR-013; FR-018). Tests: T225. **Gate: G-P (CubePay)**
- [ ] T227 Dispatch composite CubePay returns and callbacks at `miniapp/server.py` `/api/pay-return/{gateway}`, before the legacy handling, with server-side verification and registration with T076 (FR-011). Tests: T225. **Gate: G-P (CubePay)**

### Group E — Aban (Toman × 10 = Rial)

- [ ] T228 G-P evidence for Aban as a G-P entry under RD-07 in `specs/001-composite-subscriptions/research.md` (FR-011; FR-013). **Gate: G-P (Aban)**; **Requires authorization**. Record:
  - `abangateway_payment.toman_to_rial` (× 10) and `rial_to_toman`;
  - the `create_invoice`, `get_invoice` and `verify_invoice` fields, and the `AbanGatewayAlreadyVerified` and `AbanGatewayNotYetPaid` semantics;
  - the webhook body (`extract_invoice_id_from_webhook`); the merchant and API-key source; and fees
- [ ] T229 [P] Write `tests/contract/test_method_abangateway.py` using the T069 kit (FR-011). **Gate: G-P (Aban)**.
  - × 10 conversion is exact, with no rounding loss.
  - The webhook is a hint only; settlement requires `get_invoice` or `verify_invoice`.
  - "Already verified" returns the prior binding and never settles twice
- [ ] T230 Implement `composite/payment_methods/abangateway.py` over `abangateway_client.py`: an exact Rial quote, an invoice keyed by a durable intent, and server-side verification (FR-013). Tests: T229. **Gate: G-P (Aban)**
- [ ] T231 Dispatch composite Aban callbacks at `miniapp/server.py` `/api/webhooks/abangateway`, and in `abangateway_payment.py` `finalize_paid_order`/`finalize_paid_topup`, before the legacy order or top-up logic. Register the references with T076 (FR-011; FR-081). Tests: T229. **Gate: G-P (Aban)**

### Group F — Generic/custom gateway (only where server-side verification is possible)

- [ ] T232 G-P evidence per configured custom gateway key as a G-P entry under RD-07 in `specs/001-composite-subscriptions/research.md`. **Gate: G-P (generic gateway)**; **Requires authorization**. A gateway without exact server-side verification is recorded as ineligible for composite plans and reported to the owner (RD-07; FR-011). Record, per gateway:
  - whether a server-side verify request exists that returns an exact amount (`amount_path`), currency and transaction reference;
  - the webhook authentication mode;
  - the `custom_gateway_payment.compute_send_amount` unit (IRT, IRR or USD multiplier) and its rounding
- [ ] T233 [P] Write `tests/contract/test_method_generic_gateway.py` using the T069 kit, plus remediation tests for the composite path (FR-011; constitution III known gap). **Gate: G-P (generic gateway)**.
  - Webhook auth mode `none` never authorizes composite settlement.
  - `payment_engine.amounts_match` is never used: a missing or unparseable amount, the 1 % tolerance and any excess are all rejected.
  - IRT, IRR and USD multipliers are exact
- [ ] T234 Remediate the composite path in `payment_engine.py` with a strict verification entry point (constitution III/II; FR-084). It requires exact quoted native equality, maps a missing or unparseable amount to `EvidenceFailure`, and requires an authenticated webhook or a server-side verify. Legacy defaults stay unchanged; untouched legacy code is grandfathered, and that is recorded in `specs/001-composite-subscriptions/implementation-review.md`. The unsafe pattern is not copied into composite code. Tests: T233. **Gate: G-P (generic gateway)**
- [ ] T235 Implement `composite/payment_methods/generic_gateway.py` over `GenericGateway` and the T234 strict path, enabled only for gateway keys with an accepted contract (FR-013). Tests: T233. **Gate: G-P (generic gateway)**
- [ ] T236 Dispatch composite custom-gateway callbacks and returns at `miniapp/server.py` `/api/webhooks/custom/{gateway_key}` and `/api/pay/custom/{gateway_key}/return`, before the legacy handling, with registration in T076 (FR-011). Tests: T233. **Gate: G-P (generic gateway)**

**Checkpoint**: Each bound method passes its contract tests offline. Its E-005 sandbox acceptance is T262, in Phase 16.

---

## Phase 15: Polish & Cross-Cutting Concerns

**Purpose**: Deployment, release procedure, operator visibility, documentation, regression and the implementation-time Constitution Check. These run after the desired stories are complete.

- [ ] T237 [P] Add supervised service units for `v2raybot-composite-worker` and `v2raybot-subscriptions` to `install.sh` and `manage.sh` (plan.md "Upgrade, deployment and recovery design" step 4; RD-06; FR-052). Tests: T241.
  - Both start in a guarded state, with the restart policy, health checks and time-sync health.
  - The existing `v2raybot`, `v2raybot-miniapp` and `v2raybot-adminpanel` services are unchanged
- [ ] T238 [P] Replace the stage-and-push-all behavior for feature releases in `update.sh` with a release procedure (plan.md step 1; constitution IV known gap). The procedure:
  - stages only tracked release files and refuses runtime databases, secrets and backups;
  - records the release manifest: revision, runtime, dependencies, schema and capability manifests, and peer trust
- [ ] T239 Implement health and metrics as `composite/cli.py health` and an owner web health view in `admin_panel/server.py` (contracts/operations.md "Health and validation"; constitution VII). General logs carry operational IDs only. Tests: `tests/integration/test_health_views.py`. Show:
  - worker singleton, schema and epoch; source age; queue, lock, call and database delay;
  - requested versus confirmed restrictions; RX-01 uncertain requests in quarantine; sweep freshness, divergences and repairs; panel stalls; the `restartXrayOnClientDisable` check;
  - missed original deadlines; credits owed versus spendable; cleanup and exposure;
  - N-01 and B-01 state, and held recovery cases
- [ ] T240 [P] Write `docs/composite-subscriptions/OPERATIONS-RUNBOOK.md` (constitution I/IV; FR-083):
  - deployment and upgrade ordering, and guarded enablement;
  - rollback rules: a feature-aware build or a coordinated restore, never old code over live composites;
  - the external recovery-prerequisite inventory: keys, domain/HTTPS and panel admin tokens, listed without their values;
  - verifying that `restartXrayOnClientDisable` is off, and its panel-wide effect on legacy services;
  - manual panel restarts at quiet hours (RX-D10), and stall-alert handling without automatic restart (RX-D12 guidance);
  - re-running V-GA and V-RX-01 when versions or the route change; the master/node prohibition;
  - every composite inbound needs an External Proxy entry, or the owner's recorded pick among several, before binding (RD05-OWN-002 RD05-D4);
  - changing a node's address: an equivalent move to the same inbound, plus a new plan version for new sales (RD05-D5);
  - setting up the A-only live offer
- [ ] T241 Write `tests/integration/test_upgrade_rehearsal.py`, an offline rehearsal of plan.md "Upgrade, deployment and recovery design" steps 2, 3 and 8 on synthetic state (constitution IV; FR-083):
  - issuance stays disabled while guards and schema ship;
  - all writers are quiesced and a pre-upgrade recovery set is captured;
  - main migrates first, then every registry tenant, including inactive and no-bot ones; the migration reruns cleanly;
  - partial enablement is refused, and an old binary is fenced once composites exist;
  - rollback before issuance restores the pre-upgrade state
- [ ] T242 Re-run every characterization suite (`tests/characterization/` and `tests/contract/test_provider_factory_legacy.py`), and record each intended behavior difference with its justification in `specs/001-composite-subscriptions/implementation-review.md` (constitution VI; FR-081; SC-012)
- [ ] T243 [P] Write `tests/integration/test_repository_secret_scan.py`: scan the repository, fixtures, captured test logs and `specs/001-composite-subscriptions/evidence/` for tokens, credentials, panel tokens, payment keys and subscription URLs (FR-084; constitution III)
- [ ] T244 Run the quickstart commands in a `mktemp` lab root and record the results in `specs/001-composite-subscriptions/implementation-review.md` (quickstart; FR-086): `lab-seed`, `schema-check`, `migrate` twice, `pytest tests/characterization tests/unit tests/contract tests/integration --network=deny`, `pytest tests/acceptance --network=deny`, `lab-status` and `lab-cleanup`
- [ ] T245 Record the implementation Constitution Check against the actual diff for principles I–VII in `specs/001-composite-subscriptions/implementation-review.md` (constitution "Planning and Review" and Governance). Missing evidence stays a visible gap; no principle is marked satisfied on a plan promise alone. Record:
  - check results, compatibility handling, operational consequences and unresolved risks;
  - every exception, with maintainer acceptance

---

## Phase 16: Release acceptance (not runnable until implementation + authorized non-production resources)

**Purpose**: The controlled checks that the constitution and FR-086 require before release. They cover:
- deployed panel, client and payment behavior;
- timing, load, movement and recovery.

**Rules for every task here**:
- **Requires authorization**: explicit owner execution authorization, and disposable non-production resources with test credentials. No production panel serving customers, no real customer money and no production data.
- Every result is recorded in `specs/001-composite-subscriptions/evidence/` in the T005 format: revision, versions, configuration, expected, observed, pass/fail/not-run, redaction and cleanup. Each passing record is linked from its E-001–E-005 ledger row in research.md.
- Abort if a check touches an unrelated user, listener or outbound.
- A failure is reported to the owner for explicit resolution. It is never absorbed by silently changing values or reducing scope.
- Unexecuted checks stay recorded as **not run**.

- [ ] T246 Prepare the authorized release environment and record it in `specs/001-composite-subscriptions/evidence/release-environment.md` (quickstart "Authorized staged end-to-end verification"; E-004 prerequisites). **Requires authorization**. It comprises:
  - disposable standalone 3x-UI v3.9.0 / Xray-core v26.9.30 panels A, B and C with `restartXrayOnClientDisable` off, plus unrelated control users and prepared routes, listeners and outbounds;
  - owner-prepared HTTPS/domain with a verified CA;
  - sandbox accounts for the bound payment methods;
  - controlled Telegram bot and owner accounts;
  - isolated synthetic main, tenant and FSM state;
  - an encrypted off-host destination with a pinned host key;
  - the five-client version, platform and core matrix;
  - traffic, authentication and time instrumentation;
  - the exact release revision, Python runtime and dependency versions
- [ ] T247 Run V-GA-05, V-GA-06 and the worker re-run of V-GA-02 against the implemented worker on the T246 panels, recording the results in `specs/001-composite-subscriptions/evidence/V-GA-release.md` (GA-OWN-003 D11; FR-034; FR-043–FR-047; SC-003; SC-005). **Requires authorization**.
  - A failure blocks release and goes to the owner for explicit resolution of FR-034–FR-046 and SC-003–SC-005.
  - Re-run V-GA-01–V-GA-04 if a deployed version changed, and re-check G-A if master/node has been enabled
- [ ] T248 Run V-RX-01(i)–(p) against the implemented worker, recording the results in `specs/001-composite-subscriptions/evidence/V-RX-01-i-p.md` (RX-D6; RD-10; FR-085; SC-007). **Requires authorization**. Show that:
  - late reversals are detected, repaired and recorded within the owner-set values;
  - access-reducing changes are never delayed by a quarantine;
  - unrelated clients are unaffected;
  - "confirmed" is never claimed early;
  - stalls escalate, with no automatic restart
- [ ] T249 Fix the three RX-MAN-001 harness limitations in the V-RX-01 lab harness (kept outside the repository), recording the harness revision and a self-test of each fix in `specs/001-composite-subscriptions/evidence/V-RX-01-b-bot-host.md` (RX-MAN-001 "Harness limitations"; RX-D13). The fixes:
  1. b1-natsplit must really split and hold the request across TLS records; aiohttp sent the whole 607-byte request as one record;
  2. the relay must not count the client's closing TLS record as request bytes;
  3. requests sent through aiohttp must record the server certificate fingerprint
- [ ] T250 Re-run V-RX-01(b) from the bot host over the direct-TLS manager-to-panel route, after T249 and before any composite mutation reaches a production panel. Use the composite client's verified-TLS configuration with a fresh, explicitly closed connection per call. Append the results to `specs/001-composite-subscriptions/evidence/V-RX-01-b-bot-host.md` (RX-D4; RX-D13; FR-084). **Requires authorization**.
  - Record whether a request not fully delivered before close ever executes (expected: never), and whether a fully delivered one executes after close.
  - A failing result goes to the owner for explicit resolution.
  - Re-run (b) whenever the route changes
- [ ] T251 Run V-CAN-01–V-CAN-04 against the T246 panels with controlled payments, recording the results in `specs/001-composite-subscriptions/evidence/V-CAN.md` (E-002; FR-026; FR-058–FR-060; SC-005; SC-007). **Requires authorization**. Check:
  - phase-aware access and publication during the waits;
  - final-stage clocks and escalation;
  - URL invalidation;
  - full renewal refunds that settle independently of revocation and notification
- [ ] T252 Run V-NOT-01–V-NOT-06 against a controlled Telegram bot, recording the results in `specs/001-composite-subscriptions/evidence/V-NOT.md` (E-004; FR-078–FR-080; FR-085; SC-011). **Requires authorization**. Measure:
  - actual acceptance latency against the five-minute normal target;
  - the five-attempt cap across opportunities, blocks and restarts;
  - automatic catch-up of known-unsent notices, and the hold on uncertain ones
- [ ] T253 Run V-BAK-01 against the authorized off-host destination, recording the results in `specs/001-composite-subscriptions/evidence/V-BAK-01.md` (E-004; FR-076; SC-010). **Requires authorization**. Simulate source-host loss and measure:
  - the accessible validated capture age, at most 15 minutes;
  - read-back bandwidth and temporary storage;
  - overlapping five-minute captures
- [ ] T254 Run V-RCP-01 with the bound card-to-card method and a controlled bot and owner, recording the results in `specs/001-composite-subscriptions/evidence/V-RCP-01.md` (E-005; FR-005; FR-014; SC-002). Depends on T209–T214. **Requires authorization**. Cover:
  - both receipt linkage paths, including ambiguous candidates;
  - simultaneous Telegram and web owner decisions;
  - refusal of staff;
  - unique settlement
- [ ] T255 Run the full E-001 campaign, recording the results in `specs/001-composite-subscriptions/evidence/E-001.md` (FR-001; FR-002; FR-004; FR-033; FR-034; FR-082; SC-001; SC-003). **Requires authorization**. Establish:
  - exact versions and configuration, and the six protocol-ready identities with actual egress (A-US, A-DE and A-RU on A's single 443 REALITY inbound; B-CDN; B-gRPC; C-Direct);
  - the create, lookup, update, delete and reset mutation scope, unique meters and counter persistence;
  - no periodic reset on composite children, and no remote reset at renewal;
  - creation with explicit authentication and inactive creation, repeating T082 part A (RD03-OWN-001);
  - absolute updates that preserve unrelated fields and users;
  - the meaning of a zero native quota or expiry, with no composite child relying on it to mean "no access";
  - aliases and attachments, and repeated uncertain creation reconciling to the same owner;
  - unrelated users, shared configuration, listeners and outbounds unchanged;
  - rule precedence: with the owner's other routing rules in place, the anchored composite rules and those rules each still select their intended outbound (RD05-MAN-001 "not established");
  - clients created through the panel API, as Shopvpn creates them, route like the UI-created clients of RD05-MAN-001 (RD05-D2);
  - `restartXrayOnClientDisable` off, with drift detection exercised
- [ ] T256 Run the full E-002 campaign, recording the results in `specs/001-composite-subscriptions/evidence/E-002.md` (FR-036–FR-039; FR-053–FR-060; FR-085; SC-004; SC-007). **Requires authorization**. Measure:
  - fresh-authentication denial within 60 s of the actual quota crossing or expiry, including detection;
  - the five-minute stale-reading request;
  - the 60-second access, replacement, cancellation, resume and recovery targets, and the 15-minute escalations;
  - panel/API and whole-manager outages;
  - restart undercount within 20 s, and direction resets;
  - native TCP, UDP and multiplexed sessions, with the exposure recorded;
  - effects on unrelated customers
- [ ] T257 Run E-003 with v2rayNG, NekoBox, Streisand, V2Box and v2rayN at recorded versions, platforms and cores, recording the results in `specs/001-composite-subscriptions/evidence/E-003.md` (FR-049–FR-052; AS-06.1–AS-06.3; SC-008). **Requires authorization**. No automatic-selection validation is required (PR-001). Each client must:
  - import and refresh the one URL;
  - show the six real nodes in configured order, with correct remarks, handshakes, traffic and intended egress;
  - show the information entries with expiry, qualified quota, timestamps, warnings and restriction text;
  - refresh to status-only under owner suspension, and back to the full list on the same URL after release;
  - get no redirect from an invalidated old link, with no fetch causing mutations
- [ ] T258 Run the E-004 load fixture, recording the results in `specs/001-composite-subscriptions/evidence/E-004-load.md` (plan.md Performance Goals; FR-085; SC-003; SC-004). **Requires authorization**.
  - 100 subscribers, 300 A identities and three shared outbounds, with representative traffic.
  - Record CPU, memory, descriptors, queues, counter lag and SQLite contention.
  - Confirm the accepted targets inside the measured supported envelope.
  - Measure the impact of the capture pause
- [ ] T259 Run the E-004 move benchmark, recording the results in `specs/001-composite-subscriptions/evidence/E-004-move.md` (FR-068; SC-009). **Requires authorization**.
  - 150 eligible subscriptions × five moved credentials, including inactive members, each reach complete availability within 15 minutes of authorization.
  - Unrelated accounting continues meanwhile.
  - A larger batch shows honest progress without the 15-minute promise
- [ ] T260 Run the E-004 recovery campaign, recording the results in `specs/001-composite-subscriptions/evidence/E-004-recovery.md` (FR-072–FR-077; FR-083; SC-010). **Requires authorization**. Check that:
  - after simulated management-host loss, a completed validated off-host copy is at most 15 minutes old by capture time;
  - owner-initiated prepared-host recovery reaches the specified safe functions within four hours;
  - stale snapshots with newer cancellations, rotations, receipts, refunds, campaign grants and usage are held correctly;
  - missing, corrupt and skewed members and both reseller archive names are handled;
  - writer and operation interruption is safe;
  - the tenant tier, delete, ownership, purge and factory-reset guards work at the real entry points
- [ ] T261 Run a disposable upgrade-and-rollback rehearsal on a sanitized copy of supported prior main, reseller and FSM state, following plan.md steps 2–4 and 8, recording the results in `specs/001-composite-subscriptions/evidence/upgrade-rehearsal.md` (constitution IV; FR-083). **Requires authorization**. Check:
  - issuance stays disabled until evidence passes, and the migration reruns cleanly;
  - guards are verified;
  - rollback before issuance works;
  - an old binary is refused over live composites
- [ ] T262 Run E-005 for each method bound in Phase 14, using sandbox or non-production accounts and recording the results in `specs/001-composite-subscriptions/evidence/E-005.md` (FR-009–FR-021; SC-002). **Requires authorization**. Check per method:
  - exact native amount and currency, verification and transaction identity, quoted charges, and original conversion and rounding;
  - the 30 + 73 = 103 refund and the distinct extra 73 credit;
  - rejection of missing evidence; protected valid attempts and unpayable rejection; one open renewal;
  - measured 60-second wallet completion;
  - duplicate, concurrent and partial failures, and recovery from intact and stale states
- [ ] T263 Validate the initial live A-only offer configuration on a non-production replica of panel A, recording the results in `specs/001-composite-subscriptions/evidence/A-only-offer.md` (FR-002; FR-004). **Requires authorization**. This is recorded separately from the six-node acceptance and never replaces it.
  - Five explicitly prepared and routed credentials on A's single public 443 REALITY inbound.
  - No added listener or L4 proxy.
  - Actual egress for each choice
- [ ] T264 Record the release go/no-go in `specs/001-composite-subscriptions/implementation-review.md` (plan.md step 4; RX-D2; RX-D13). A failed item is reported for explicit resolution; no scope is silently reduced. **Requires authorization** for the production steps.
  - Every Phase 16 record shows pass, fail or not-run.
  - The T245 Constitution Check is updated with the evidence.
  - Every G-P method is either bound or recorded as unavailable with a reason.
  - With owner authorization and read-only access, verify on each production panel that `restartXrayOnClientDisable` is off and the admin-scope token has the right scope, before binding it to composite use. The RX-D13 precondition is met by T250.
  - Enable the owner-validated catalog only after all evidence passes

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)** has no dependencies.
- **Phase 2 (Foundational)** depends on Phase 1. Run 2A characterization first: every task that modifies a legacy file names the characterization task it depends on. Then 2B (schema), then 2C (types, authority, guards), then 2D (control, worker, CLI). Phase 2 blocks all later phases.
- **Phase 3 (Finance core)** depends on 2B and 2C. **G-P does not block it.**
- **Phase 4 (Remote and accounting core)** depends on 2B and 2D. T082 is evidence that needs authorization: part A can run as soon as it is authorized, and only T097 waits for its results (and for OQ-4); part B runs after T096 and T099.
- **Phases 5–13 (US1–US9)** depend on Phases 2–4; stories that move money also depend on Phase 3.
- **Phase 14 (Payment bindings)** depends on T069 and T075–T077 (Phase 3) and on T208, except T215, which depends only on T075, T116 and T118. Each group's evidence task gates the rest of that group, and the groups are independent of each other. The card-to-card receipt flow also needs T118. A group can start as soon as its evidence is available, alongside story work.
- **Phase 15 (Polish)** depends on the stories being released.
- **Phase 16 (Release acceptance)** depends on implementation of the stories it checks, on Phase 14 for E-005 and V-RCP-01, and on explicit authorization. T250 must pass before any composite mutation reaches a production panel.

### Fences

| Fence | Tasks | Lifted by |
| --- | --- | --- |
| G-P per method | T208–T214, T216–T236 | An owner-accepted evidence record per method: T208 (inventory), then T209, T216, T220, T224, T228 and T232. T215 is not gated (GP-OWN-001) |
| E-001 probe | T097 | T082 part A's candidate mechanisms, plus OQ-4 (runtime confirmation). Lifted for T096, T099 and T120 on 2026-10-21 (OQ-3) |
| Requires authorization | T082, T208, T209, T216, T220, T224, T228, T232, T246–T248, T250–T264 | Explicit owner execution authorization for each run, on disposable non-production resources |
| Before production composite mutations | T250; T264 production checks | RX-D13 re-run passed; production panels verified read-only |

### User Story Dependencies

- **US1 (P1)**: needs only Phases 2–4. Offline funding is wallet-only or zero-price; external funding needs a bound Phase 14 method.
- **US2 (P1)**: needs Phase 4. Testable on seeded fulfilled subscriptions, without US1 handlers.
- **US3 (P1)**: needs Phase 4 and T132 (freshness), and reuses the US1 orchestration (T119, T121). T150 is invoked by US5 (T169).
- **US4 (P1)**: reuses the US1 orchestration (T119–T121).
- **US5 (P1)**: needs Phase 4 (RX-01 engine, terminal revocation). Testable on seeded subscriptions. T169 calls T150 (US3).
- **US6 (P1)**: completes the US1 endpoint (T122) and builds on the generation builder (T120).
- **US7 (P1)**: needs US1 (T119, T120), T105 and T079.
- **US8 (P1)**: needs T055 and T081. Its reconciliation coverage grows as other stories land.
- **US9 (P2)**: needs the period commits (T121, T147) and N-01 (T108).

### Critical path

Setup → 2A → 2B → 2C/2D → (Phase 3 ∥ Phase 4) → US1 → US2 → US3 → US5 → US7 → US8 → Phase 15 → Phase 16. US4, US6 and US9 branch off once their dependencies are done. Phase 14 groups proceed as their G-P evidence arrives.

### Within Each User Story

- Write tests first and see them fail before implementing. Characterize a touched legacy file before modifying it.
- Order: models and predicates → services and lifecycle → handlers and routes → UI → notifications.
- Every implementation task names the tests it must pass. Recovery cases (crash, restart, retry, uncertainty) live in those tests, not in a later phase.
- Finish a story's checkpoint before relying on it from another story.

### Parallel Opportunities

- 106 tasks carry [P].
- All 2A characterization tasks (T013–T031), the Phase 3 tests (T059–T069) and the Phase 4 tests (T083–T091) can run in parallel.
- After Phases 2–4, US2, US4, US5 and US6 can be built in parallel by different people; US3 and US7 follow their dependencies.
- After T208, Phase 14 groups B–F can run in parallel; group A also needs T118.
- Phase 16 campaigns can share the T246 environment and run in parallel where they do not disturb each other's measurements.

---

## Parallel Example: Foundational characterization

```bash
Task: "T013 Characterize _buy_start in tests/characterization/test_buy_start.py"
Task: "T014 Characterize receipt linkage in tests/characterization/test_receipt_linkage.py"
Task: "T020 Characterize the legacy 3x-UI adapter in tests/characterization/test_threexui_provider.py"
Task: "T026 Characterize backup/restore in tests/characterization/test_backup_restore.py"
```

## Parallel Example: User Story 1

```bash
Task: "T110 Acceptance AS-01.1–AS-01.6 in tests/acceptance/test_us1_purchase.py"
Task: "T111 Fulfillment recovery in tests/integration/test_fulfillment_recovery.py"
Task: "T112 Catalog callbacks in tests/integration/test_catalog_telegram.py"
Task: "T113 Plan validation in tests/unit/test_composite_plans.py"
Task: "T114 Initial cancellation in tests/integration/test_initial_cancellation.py"
Task: "T115 Minimal endpoint in tests/integration/test_public_endpoint_minimal.py"
# then, in parallel with T116: T117 owner UI screens in admin_panel/static/app.js
```

## Parallel Example: User Story 2

```bash
Task: "T128 tests/acceptance/test_us2_allowance.py"
Task: "T129 tests/integration/test_freshness_grace_cutoff.py"
Task: "T130 tests/integration/test_reporting_recovery.py"
Task: "T131 tests/integration/test_usage_gap_and_drift.py"
```

## Parallel Example: User Story 3

```bash
Task: "T140 tests/acceptance/test_us3_renewal.py"
Task: "T141 tests/unit/test_renewal_arithmetic.py"
Task: "T142 tests/integration/test_boundary_worker.py"
Task: "T143 tests/integration/test_renewal_matching_and_blocks.py"
```

## Parallel Example: User Story 4

```bash
Task: "T151 tests/acceptance/test_us4_tests_campaign.py"
Task: "T152 tests/integration/test_campaign_races.py"
Task: "T153 tests/integration/test_test_eligibility_shared.py"
```

## Parallel Example: User Story 5

```bash
Task: "T160 tests/acceptance/test_us5_controls.py"
Task: "T161 tests/integration/test_cancellation_phases.py"
Task: "T162 tests/integration/test_leak_replacement.py"
Task: "T163 tests/integration/test_owner_bulk_and_compensation.py"
Task: "T164 tests/integration/test_block_separation.py"
```

## Parallel Example: User Story 6

```bash
Task: "T173 tests/contract/test_subscription_http_gates.py"
Task: "T174 tests/unit/test_info_entries.py"
Task: "T175 tests/integration/test_subscription_no_side_effects.py"
```

## Parallel Example: User Story 7

```bash
Task: "T180 tests/acceptance/test_us7_moves.py"
Task: "T181 tests/integration/test_move_batches.py"
```

## Parallel Example: User Story 8

```bash
Task: "T189 tests/acceptance/test_us8_recovery.py"
Task: "T190 tests/integration/test_capture_restore.py"
Task: "T191 tests/integration/test_backup_delivery_b01.py"
Task: "T192 tests/integration/test_destructive_guards.py"
Task: "T193 tests/integration/test_catch_up_and_holds.py"
```

## Parallel Example: User Story 9

```bash
Task: "T204 tests/acceptance/test_us9_reminders.py"
Task: "T205 tests/integration/test_reminder_eligibility.py"
```

## Parallel Example: Payment bindings (after T208, each group gated on its own evidence)

```bash
Task: "T217 tests/contract/test_method_nowpayments.py"      # after T216
Task: "T221 tests/contract/test_method_tetra98.py"          # after T220
Task: "T225 tests/contract/test_method_cubepay.py"          # after T224
Task: "T229 tests/contract/test_method_abangateway.py"      # after T228
Task: "T233 tests/contract/test_method_generic_gateway.py"  # after T232
```

---

## Implementation Strategy

### MVP first (validation increment, not a release)

1. Complete Phase 1 (Setup) and Phase 2 (Foundational, characterization first).
2. Complete Phase 3 (Finance core) and Phase 4 (Remote and accounting core). Request authorization for T082 part A early: T097 waits on it, and it checks the Phase 4 provider work against a real panel. Part B follows T096 and T099.
3. Complete Phase 5 (US1).
4. **Stop and validate**: run the US1 tests and the full characterization suite offline. US1 then works with wallet-only and zero-price funding.

### Incremental delivery

1. Add US2 → US3 → US4 → US5 → US6 → US7 → US8 → US9, validating each checkpoint offline without breaking earlier stories.
2. Run each Phase 14 group as its G-P evidence arrives. A group that cannot be verified leaves its method unavailable to composite plans, with the reason recorded and reported.
3. Phase 15, then Phase 16 under explicit authorization.

### Launch scope

Every accepted journey is launch scope: plan.md says "Priorities do not trim this set." Release therefore requires:
- all nine stories;
- the owner-selected bound payment methods;
- Phase 15;
- every Phase 16 record at pass, with the T264 go/no-go.

The MVP above is an internal validation increment only.

### Parallel team strategy

With several developers, the team completes Phases 1–4 together, then splits the stories along the dependency list above. A separate person can own Phase 14 evidence and bindings, since that work proceeds independently of the stories.

---

## Requirement coverage (generated from the task text)

Generated by parsing every task block and expanding ranges such as "FR-058–FR-060". All 86 FR, 12 SC and 44 AS identifiers are referenced, and every FR has at least one implementation task and at least one test or validation task.

| Requirement | Tasks (implementation, tests and release evidence) |
| --- | --- |
| FR-001 | T037, T113, T119, T255 |
| FR-002 | T008, T113, T116, T117, T255, T263 |
| FR-003 | T037, T070, T112, T113, T116, T118 |
| FR-004 | T036, T098, T099, T116, T117, T255, T263 |
| FR-005 | T029, T030, T047–T049, T053, T112, T118, T211, T254 |
| FR-006 | T047, T048, T112, T118 |
| FR-007 | T107, T111, T125, T126, T139 |
| FR-008 | T037, T063, T074, T113, T116, T125 |
| FR-009 | T059, T070, T262 |
| FR-010 | T063, T074, T112, T113, T116, T118, T208, T215, T262 |
| FR-011 | T016, T023, T033, T039, T060, T064, T069, T071, T076, T210, T211, T215–T217, T219–T221, T223, T227–T229, T231–T233, T236, T262 |
| FR-012 | T063, T074, T262 |
| FR-013 | T064, T069, T075, T209, T210, T212, T216, T218, T220, T222, T224–T226, T228, T230, T235, T262 |
| FR-014 | T014, T015, T064, T077, T209, T211, T213, T214, T254, T262 |
| FR-015 | T039, T063, T074, T144, T172, T262 |
| FR-016 | T065, T079, T262 |
| FR-017 | T065, T079, T080, T262 |
| FR-018 | T061, T070, T078, T161, T216, T224–T226, T262 |
| FR-019 | T061, T076, T080, T217, T262 |
| FR-020 | T039, T062, T073, T078, T262 |
| FR-021 | T063, T066, T074, T262 |
| FR-022 | T021, T095, T105, T111, T119, T127 |
| FR-023 | T111, T119, T121, T127 |
| FR-024 | T111, T123 |
| FR-025 | T060, T070, T071, T078, T081, T112, T118, T123 |
| FR-026 | T114, T124, T251 |
| FR-027 | T017, T041, T153, T155, T156 |
| FR-028 | T151, T154 |
| FR-029 | T039, T152, T157 |
| FR-030 | T152, T155, T157, T158 |
| FR-031 | T017, T153, T159 |
| FR-032 | T149, T160 |
| FR-033 | T036, T038, T089, T098, T106, T255 |
| FR-034 | T020, T038, T085, T089, T095, T106, T139, T247, T255 |
| FR-035 | T038, T129, T132, T139, T247 |
| FR-036 | T129, T133, T247, T256 |
| FR-037 | T020, T097, T129, T134, T247, T256 |
| FR-038 | T135, T247, T256 |
| FR-039 | T109, T130, T136, T247, T256 |
| FR-040 | T131, T137, T247 |
| FR-041 | T085–T087, T103, T104, T131, T138, T247 |
| FR-042 | T143, T144, T247 |
| FR-043 | T038, T141, T142, T144–T146, T247 |
| FR-044 | T141, T146, T247 |
| FR-045 | T141, T146, T247 |
| FR-046 | T142, T145, T147, T247 |
| FR-047 | T142, T148, T247 |
| FR-048 | T140, T147 |
| FR-049 | T022, T096, T120, T173, T179, T257 |
| FR-050 | T174, T177, T179, T257 |
| FR-051 | T037, T043, T115, T122, T173, T176, T257 |
| FR-052 | T057, T115, T122, T175, T178, T179, T237, T257 |
| FR-053 | T043, T165, T256 |
| FR-054 | T109, T165, T256 |
| FR-055 | T162, T166, T256 |
| FR-056 | T097, T162, T166, T256 |
| FR-057 | T109, T162, T166, T167, T256 |
| FR-058 | T161, T168, T251, T256 |
| FR-059 | T161, T168, T251, T256 |
| FR-060 | T097, T109, T161, T168, T251, T256 |
| FR-061 | T163, T169 |
| FR-062 | T143, T150, T169 |
| FR-063 | T031, T164, T171 |
| FR-064 | T163, T170 |
| FR-065 | T181–T183 |
| FR-066 | T181, T182, T184 |
| FR-067 | T181–T183 |
| FR-068 | T109, T181, T188, T259 |
| FR-069 | T181, T187 |
| FR-070 | T181, T185 |
| FR-071 | T181, T186 |
| FR-072 | T067, T081, T109, T111, T193, T200, T260 |
| FR-073 | T190, T193, T198, T199, T260 |
| FR-074 | T068, T072, T157, T193, T199, T260 |
| FR-075 | T027, T040, T192, T201, T260 |
| FR-076 | T026, T191, T196, T197, T202, T253, T260 |
| FR-077 | T203, T260 |
| FR-078 | T018, T205, T207, T252 |
| FR-079 | T038, T147, T205, T206, T252 |
| FR-080 | T205–T207, T252 |
| FR-081 | T013, T018, T022, T028, T035, T050–T052, T101, T231, T242 |
| FR-082 | T019, T083, T092, T255 |
| FR-083 | T025–T027, T034, T035, T041, T055, T190, T192, T194, T195, T198, T201, T240, T241, T260, T261 |
| FR-084 | T012, T020, T030, T044, T045, T047, T048, T084, T093, T094, T178, T234, T243, T250 |
| FR-085 | T024, T033, T040, T046, T056, T057, T086, T091, T100, T102, T103, T107, T108, T139, T147, T161, T172, T195, T248, T252, T256, T258 |
| FR-086 | T002, T005, T244 |
| SC-001 | T110, T255 |
| SC-002 | T061, T064, T067, T110, T211, T254, T262 |
| SC-003 | T089, T128, T247, T255, T258 |
| SC-004 | T128, T247, T256, T258 |
| SC-005 | T140, T247, T251 |
| SC-006 | T151, T152 |
| SC-007 | T086, T160, T248, T251, T256 |
| SC-008 | T173, T175, T257 |
| SC-009 | T180, T259 |
| SC-010 | T189, T253, T260 |
| SC-011 | T204, T252 |
| SC-012 | T013, T047, T050, T242 |

---

## Open questions (not resolvable from the documents)

- **OQ-1 — Automatic card-to-card (SMS forwarder). Resolved 2026-10-22: not offered for composite plans at launch** (research.md GP-OWN-001 GP-D1). In the source, the automatic mode matches a forwarded SMS to a pending invoice by amount only, with no bank reference, while FR-011 requires a unique transaction reference. Manual card-to-card (FR-014) stays a candidate. T215 enforces the exclusion.
- **OQ-2 — Enabled methods outside the six candidates. Resolved 2026-10-22: not offered for composite plans, because no G-P contract is bound for them** (research.md GP-OWN-001 GP-D2; FR-010; PC-092). Plan settings do not list them, so they cannot be ticked by mistake; once a method's own group is accepted, it becomes selectable. No spec change is needed: PC-092 already treats an integration Shopvpn cannot verify as no permission to grant service. This covers Zarinpal, Aqayepardakht, Telegram Stars, BluPal, Noapay and Plisio/crypto. T208 still records which are enabled, and T215 enforces the exclusion. Any of them can be added later with its own Phase 14-style group before 001's release, or as a small follow-up feature after it.
- **OQ-3 — Is RD-05's routing/export check still a pre-implementation gate? Resolved 2026-10-21: no.** RD-05 says "Gate: E-001 first six-node egress/readiness and unrelated-user preservation, before implementing dependent routing/export behavior", while plan.md's status lines name only G-P as blocking. These tasks first fenced T096, T099 and T120 behind T082. The owner then confirmed in a lab, on the deployed versions, that Xray `user` regex rules route clients to the matching outbound without a restart and that clients matching no rule keep their normal route (RD05-MAN-001) and chose to implement first and test after (RD05-OWN-001); both are recorded in research.md under RD-05. The fence is lifted for those three tasks; the remaining checks run after implementation (T082, T255, T257). research.md RD-05 and the E-001 ledger row now mark the old gate as lifted (2026-10-22).
- **OQ-4 — Which runtime evidence confirms fresh-authentication state?** contracts/provider.md keeps `confirm_runtime_state` as "still an E-001 capability", to "fail explicitly and keep pending" if no safe runtime proof exists. No document selects the production mechanism, for example an active authentication probe from the manager host or a panel runtime read. Until one is selected, nothing that needs runtime proof can be reported as confirmed:
  - leak-replacement success (FR-056);
  - final-cancellation completion (FR-060);
  - verified cutoff (FR-037; SC-004).
  T082 collects the candidates; choosing one is a technical/owner decision. T097 is fenced on it.
- **OQ-5 — Where release evidence lives. Resolved 2026-10-22.** Spec Kit 1.0.10 has no convention for evidence or review files: its scripts recognize only spec, plan, tasks, research, data-model, quickstart, contracts and checklists, and `checklists/` tests requirement quality, not implementation. The owner chose this rule: evidence that closes a research gate or drives a design decision goes in research.md (as GC-MAN-001, GA-MAN-002, RX-MAN-001 and RD05-MAN-001 do); release evidence that the implementation works goes in `evidence/`, one file per check, linked from the E-001–E-005 ledger; the implementation review and Constitution Check go in `implementation-review.md`, linked from plan.md because the constitution requires a "feature plan or linked review"; tasks.md keeps pointers only. RD05-MAN-001 was moved from T082 to research.md RD-05 accordingly, and T005, T082, the G-P evidence tasks and the Phase 16 rules follow the rule.

---

## Notes

- [P] tasks touch different files and have no dependency on an incomplete task; [USn] maps a task to its user story for traceability.
- This list adds no requirement. Any requirement change found during implementation goes through owner approval as a new PR-00x refinement; it is not made by editing tasks.
- No task approves a constitutional exception. Exceptions follow the Governance section and are recorded in `implementation-review.md` (T245).
- Not tasked, by decision: an automatic or deliberate Xray restart for leak cases (RX-MAN-001 finding 2). RX-D12 rules out automatic restarts, and the owner has made no decision on deliberate ones. Owner manual restarts (RX-D10) need no Shopvpn control.
- Mobile-auth parity for composite owner management is not built. Following contracts/application.md's allowed default, composite routes reject mobile tokens (T049) until parity is verified.
- The template's "commit after each task" applies only when the owner asks for commits. Generating this list made no commit.
- Historical P0–P6 packages are not this task structure (plan.md).
