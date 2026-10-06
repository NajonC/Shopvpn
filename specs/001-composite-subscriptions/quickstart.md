# Composite subscriptions — planning review and future validation

**Current status:** Planning-only artifacts. No application/services/imports, dependencies, runtime databases/backups/secrets, live endpoints or integration experiments were authorized. G-A accounting evidence, G-C informational encoding and G-P method-specific financial evidence remain unresolved. The workflow is not complete; these commands are not evidence of feasibility or passing tests.

Read [plan.md](plan.md), [research.md](research.md), [data-model.md](data-model.md) and [contracts/](contracts/) together with unchanged spec/source ledger. All nine journeys/full launch scope remain required, not selected by priority. No tasks or Antigravity worktree are created.

## Commands available now: source/documentation review only

The existing installed shell/git/Python standard library can inspect documentation without importing the app:

```bash
cd /home/nojan/projects/shopvpn-develop/Shopvpn
git branch --show-current
git rev-parse HEAD
git status --short
git diff --check
rg -n 'G-A|G-C|G-P|E-00[1-5]|FR-|SC-' specs/001-composite-subscriptions/plan.md specs/001-composite-subscriptions/research.md
rg --files specs/001-composite-subscriptions
```

Expected: branch `main`, inspected revision recorded in research, only new planning artifacts in feature directory, all evidence gates visible and no tasks/source/config/authority edits. Spec Kit feature metadata resolves this directory separately from Git branch. `.specify/extensions.yml` was absent before and after planning. Normal Git status/diff may omit locally ignored artifacts; a direct file inventory/hash/link/fence/table/ID/whitespace review is also needed. Do not use `update.sh`: it stages/commits/pushes and installs/restarts, outside planning scope.

Present source commands such as `python main.py`, uvicorn Mini App/admin launches, install/manage services and the current `test_config_provision.py` are **not validation commands for this request**. The latter creates customer trials. Do not run them or open real `.env`/SQLite/backup files. Present planning validation exercises documentation only, not an application import/test or controlled experiment.

## Earliest feasibility checks — later explicit authorization

Before authorizing dependent implementation, prepare **isolated non-production resources** and obtain execution authorization. Product clarification is complete; do not ask the owner to guess technical facts. Record exact revision/version/config and expected/observed/pass/fail/not-run evidence, redacting credentials. A planned procedure is not a passed gate.

1. **G-A / E-001 first:** Pin disposable 3x-UI/Xray dialect and meter authority. Establish source-time/collector continuity/gap detection, explicit child/attachment/mutation/runtime proof and faithful fields. Inject independently timestamped known-byte upload/download across collector pause, failed persistence, resets/restarts and renewal/expiry boundaries. Prove attribution through effective application without deliberately suspending usable old service. Cumulative GET/`lastOnline`/HTTP completion time alone fails; if no supported mechanism exists, keep design blocked and report affected FR-034–FR-046/SC-003–SC-005 rather than implement guessed billing.
2. **G-C / E-003:** Small six-node+non-working informational-row and status-only owner-suspension import/refresh in **v2rayNG Android, NekoBox Android, Streisand iOS, V2Box iOS and v2rayN Windows**, recording exact app/core versions. Check how information entries are displayed/selected/auto-selected, no real credentials in status-only, no successful info traffic, all real protocols/fields preserved. Concrete safe encoding must be established before binding serializer; don't assume reserved/loopback/synthetic endpoints are safe.
3. **G-P / E-005:** Authorized secret-redacted configured-method inventory and sandbox invoice/receipt verification. Establish native amount/currency/merchant/reference/charges/rounding/original conversion and full invoice wallet value. Verify exact amount/evidence rejection and valid-attempt recovery; owner manual decisions require independent reference/evidence. Every actually supported method needs a safe contract; integration source presence/notification success does not prove support.
4. **E-004 early operation probe:** Disposable historical/current/feature-shaped main+reseller+no-bot+FSM fixtures; simultaneous writer shutdown/drain, coherent validated capture, missing/corrupt/skewed members and both reseller archive names, staged replacement and newer-evidence holds. Measure capture-pause impact before deploying the chosen recovery coordination. No real runtime/archive copying is authorized.

Abort a controlled check if it reaches an unrelated listener/user/outbound or requires unapproved shared restart/core changes. Keep current evidence and failure, clean verified disposable resources only, and revise the affected technical design under governing scope. No failed probe may silently remove launch behavior. Other full timing/load/recovery checks remain required after the earliest gates pass.

## Proposed post-implementation commands — unavailable now

The `composite` package, tests, CLI/test flags and service units below **do not exist now**. These commands are target interfaces for future implementation, not scripts to run during planning. Implementing them does not itself resolve G-A/G-C/G-P. They require a separately authorized implementation phase, compatible isolated Python/dependencies and resolved dependent contracts.

Use a disposable checkout and newly generated synthetic state, never the production project runtime paths. No production environment/key/backup import. Network denial is default for offline fixtures; external substitutions and fake time are explicit. The future harness must fail if any non-test database/service URL is selected.

```bash
SHOPVPN_LAB_ROOT=$(mktemp -d /tmp/shopvpn-composite-lab.XXXXXX)
python -m composite.cli lab-seed --root "$SHOPVPN_LAB_ROOT" --synthetic-only
python -m composite.cli schema-check --root "$SHOPVPN_LAB_ROOT"
python -m composite.cli migrate --root "$SHOPVPN_LAB_ROOT" --offline
python -m composite.cli migrate --root "$SHOPVPN_LAB_ROOT" --offline
python -m pytest tests/characterization tests/unit tests/contract tests/integration --network=deny
python -m pytest tests/acceptance --network=deny
python -m composite.cli lab-status --root "$SHOPVPN_LAB_ROOT"
```

Expected: schema migration reruns without duplicate/lost legacy data; old/new main/tenant/FSM compatibility and guard defaults pass; all FR/AS/SC offline cases have meaningful failure/atomicity/recovery outcomes. Synthetic six-node fixture includes repeat purchase/customer/aliases, plus separately configured A-only five-choice case; fixtures never contain real secrets or claim physical traffic behavior. Synthetic command success must not be labeled real client/panel/payment acceptance.

Harness-specific `--network=deny` is a **proposed fixture/plugin option**, not a standard pytest option installed here. Implementation must provide the denial guard and compatible test runner, with no incidental imports of production config. Test selection must include the following groups rather than simply mirror implementation:

| Validation | Expected outcome |
| --- | --- |
| Legacy characterization | Existing Telegram/FSM/stock/custom/test/gift/naming/transfers/roles/reseller/providers and manual-carryover versus automatic-replacement behavior preserved; unsafe affected zero/error/partial behavior reproduced then remedied. |
| Finance/capacity | Duplicate/concurrent Telegram/web approval, wallet/order/coupon atomicity, exact native evidence, zero-price, one open renewal, 30+73=103 refund, distinct extra73 credit, cancelled late money and valid-attempt/unpayable cases; no repeated or lost obligation. |
| Remote/recovery | Unknown create/update/revoke and crash before/after local commits/result; same identity reconciled, no stale enable/old cutoff error, partial renewal preserves old terms, refund independent of cleanup. |
| Tests/campaign | Shared legacy/composite ordinary eligibility, callback actor, 149+1 pending campaign races/cap150, no late grant/unknown release, reset/conversion/cancel preserves permanent recipients; defaults exact. |
| Accounting/access | Distinct aliased meters, independent resets/out-of-order/invalid values/gaps, 60/61-second source freshness, five-minute original grace, deadline persistence, usage settlement qualification; G-A resolved source contract separately proven. |
| Lifecycle/bulk/export | Independent restrictions/shop block, cancellation wait/final stage, per-sub24h success cooldown, leak gate, inactive/emergency/equivalent move/sales pause and per-member retry, full cached list/status-only/invalid generations/no GET effects; no secret leakage. |
| Operations/reminders | Coherent capture/all writer closure, archive safety/member/schema and stale restore/purge/newer money/campaign/revocation holds; paid-term thresholds/delivery uncertainty/no rearming/no test reminders. |

Inject deterministic crash/failure at transaction, invoice creation/verification, provider dispatch/read-back, publication, refund/hold release, backup delivery and replacement boundaries. Restart with same state and clocks; prove uniqueness/current-revision reconciliation/retained obligations rather than merely checking a success response. Multi-process tests use separate connections/processes on synthetic files to exercise SQLite locks; no in-memory-only substitute for actual concurrency.

## Authorized staged end-to-end verification — later, not run

Prerequisites: approved disposable panels/routes/listeners/outbounds and unrelated control users; sandbox enabled payment methods and controlled Telegram bot/owner accounts; prepared HTTPS/domain with verified CA/host identity; isolated synthetic main/dependent tenants/FSM; recorded tested release/runtime/capability manifests; independently accessible encrypted off-host copy/key inventory; explicit all-five client version/core matrix and traffic/authentication/time instrumentation. A and B/C acceptance topology remain separate from actual A-only five-choice deployment. All secrets are test-only and excluded from logs/evidence/source.

Future lab worker/public service commands (not present):

```bash
python -m composite.worker --lab-root "$SHOPVPN_LAB_ROOT"
python -m composite.subscription_server --lab-root "$SHOPVPN_LAB_ROOT" --listen 127.0.0.1:18003
```

Run in separate terminals/supervision only after authorized lab setup; never accidentally start them against default real DB. Owner-prepared HTTPS front end is required for client acceptance; loopback HTTP fixture alone cannot prove real client compatibility/public recovery. Controlled campaigns must record E-001–E-005 outcomes from research, including actual fresh-authentication denial from quota crossing/expiry within60seconds, native existing TCP/UDP/multiplex exposure, outages/recovery/partial actions, all six real protocol handshakes/egress/five-client refresh, original invoice-value settlement and critical deadlines.

Measure **both distinct** load fixtures: 100 subscribers/300 A identities/three shared outbounds with representative traffic, then 150 eligible subscriptions×five moved identities completing per-sub availability within15minutes with inactive members and unrelated accounting continuing. Larger batches remain supported without inventing the same universal deadline. Record CPU/memory/descriptors/queue/counter lag/SQLite contention. Supported normal conditions must satisfy accepted targets, not define away failures.

Recovery test: verify a completed validated off-host copy's **capture** age≤15minutes after simulated management-host loss, then initiate prepared-owner recovery and measure safe specified functions within4hours. Use stale snapshots with newer cancellation/rotation/receipt/refund/campaign/usage and missing/corrupt/skewed members; release verified cases and retain explicit holds/cleanup. Test forced reset/panel/tier/ownership/purge guard at actual entry points. Missing history cannot be called zero/full recovery.

## Cleanup and retained evidence

Offline lab cleanup target (future):

```bash
python -m composite.cli lab-cleanup --root "$SHOPVPN_LAB_ROOT" --confirm-synthetic
```

The cleanup command must validate its disposable marker/path, stop every lab writer/service and close DB/FSM handles. For remote controlled checks, inventory only created verified-owned test identities/invoices/messages/domains; revoke and independently verify fresh-auth denial/removal as appropriate, preserve final traffic/evidence and retain pending cleanup on uncertainty. Never erase a failed cleanup record or touch unrelated/preexisting users/routes/listeners. Retain sanitized revision/config/version/result/evidence ledger before deleting local synthetic scratch state. Real test resources require provider-specific authorized cleanup; no blanket `rm`/reset force command. Planning-only checks need no service/data cleanup because none ran.
