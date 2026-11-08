# Brief T050bb–ba: Noapay direct custom fulfillment

- **Status**: accepted
- **Tasks**: T050bb success/repeat and T050bc failure boundaries, combined under owner authorization. Neither accepted independently.
- **Packet type**: test-only
- **Orchestrator**: actual/recommended gpt-6.1-sol/high, established bounded custom contract
- **Coder**: none; default antigravity/gemini-3.8-flash-high options {}; every test is sensitive (money/identity/repeat/crash ordering), orchestrator-owned per step4; brief exceeds residual coder work
- **Tests written by**: orchestrator

## Goal

Protect direct Noapay custom-order fulfillment before claim/provider/SQL/delivery/referral. Characterize legacy success/repeat and caught versus propagated failures without changing production. These two adjacent normal-sized scenario families share the same helper/fixtures/reference and one combined offline acceptance run.

## What already exists

noapay_payment.py finalize_paid_order209–317 reads order, checks pending, claims, selects custom server and GLOBAL duration, constructs real provider factory, creates remote user, adds SQL config/history, approves, delivers, rewards on BASE price and notifies. database.py create_custom_config_order3322, approve3353, add_custom_config6987/history7142, referral4370. panel_providers/__init__.py get_provider98 dispatches PROVIDERS. Prior callback tests do not cover direct successful fulfillment. miniapp/server.py webhook independently verifies and sends a return-to-bot message for custom orders; no helper delegation there. Not included here.

## Rules

1. “Every legacy path listed in T051–T053 rejects a composite product, order or subscription with an explicit reason before any side effect” [T050]
2. “Composite rows are routed to `composite/service.py` or refused; legacy code never claims, provisions or rewards them.” [T052]
3. “Reject composite requests before any side effect on the unsupported channels” [T053]
4. “Existing legacy surfaces remain compatible.” [NG-01]
5. “Composite purchases/renewals create no purchase-based referral rewards, referring-reseller commissions, deferred payout promises or first-purchase referral consumption.” [NG-05]

## Files

Create tests/integration/test_composite_noapay_fulfillment_guards.py. Production and prior tests read-only. Review artifacts under review/T050bb-ba orchestrator-owned. No new dependencies/network.

## Interfaces / Tests

Actual finalize_paid_order(db,bot,order_id,notify_admins_fn=None), actual SQL and factory registry; only provider constructor/create and delivery/Telegram are synthetic boundaries. Missing/explicit legacy and dict/sqlite forms; unrelated composite sibling is always present. Selected order/product composite refuses before trace/DB, explicit secret-free reason. Scenarios success/factory/create/delivery/prior:20 missing-T053 failures. Success/send/admin variants:12 pass, order approved, selected config/history retained with created_name,10GB/global45days (order saved17), correct owner/server/order/link/source, final900 delivery before reward, base1000 at13%=130 credited once, first-purchase flag consumed once, exact reward/admin messages, repeat no effects. Missing/server/factory/create/add/approval/delivery/prior/lost conditional claim:36 pass. Early caught errors release to pending, add error leaves processing/no row, approval error leaves row/processing, delivery error leaves row/approved; no reward/notification after failure. Existing limitations remain characterized only. Lost claim uses actual processing row and stale pending read; no artificial claim success.

## How to check

.venv/bin/python -m pytest tests/integration/test_composite_noapay_fulfillment_guards.py --network=deny -q
Full offline five directories --network=deny, once after combined final diff. Baseline4771passes+581declaredmissingT051–053failures; add48passes+20missingT053failures =4819passes+601failures/5420total. Exact failures compared to review/T050az-ba/offline-failures.json plus packet XML; stable reasons normalized for process IDs/addresses only.

## Out of scope

Production implementation/T051+, ordinary approved composite manual routes, renewal/catalog fulfillment, BluPal/AbanGateway, webhooks, real panels/providers, legacy failure repairs, push. Batch 7 ends after bb/bc and bd/be (renewal success/repeat + failure boundaries), four parts total.

## Open points

None.

## Reviewer verification

Prior pair b6bc695 accepted/clean. Prerequisite/checklist26/26/hooks absent unchanged. Independently read entire noapay_payment.finalize_paid_order209–317 and callers handlers_user991/handlers_admin2387; miniapp2334 uses separate inline custom notification, not helper. extra_gateway_payment323 dispatches AbanGateway helper, not Noapay. Shared DB/factory source contracts revalidated against FR081/082/086,NG01/02/05,FR005,SC012,T050–053 and constitution I/II/III/VI. No new authority/product decision. Test-only no production/live service evidence. All money/identity/repeat tests orchestrator-owned; no residual coder work.

Source-to-test and mutations: composite order/product selection/refusal/reason/before-effects ->20negative cases, omit each/both, early claim, wrong product, overstrict legacy/sibling variants. Legacy helper -> real factory constructor/create args, selected SQL owner/server/order/name/volume/global45duration/link/history/approval, delivery final900 before base1000 referral130 once, notifications and repeat; mutate these identities/terms/price/amount/omissions/status/claim/release/error/success. Failure family -> missing server/constructor/create caught and released; add/approval/delivery errors propagate leaving exact rows/status and no later reward; protected existing behavior only.68newcases must all pass on scratch reference; mutation campaign requires independent relevant assertions/pytest.raises failures, no setup/error/skip kills or survivors. Variants reused only after actual Noapay source exact-match/AST preflight; separate per-gateway executable scratch/reference/source hashes. No production bypass/reference patch. One full offline run only for entire az/ba pair after final diff; compare581baselinefailure IDs/reasons plus20declared missingT053 cases, protect all prior tests/artifacts. Global duration17->45 legacy difference and post-persistence failure limits characterized only, no production repair. Both constituents remain unaccepted until all combined evidence settles.

## Delegation log

Auto approved; all tests sensitive and orchestrator-owned, no residual coder work. Current clean baseline b6bc695; checklist26/26, hooks absent. No production edits. Read Noapay helper in full, actual DB/factory and source rules independently; custom branch exact-match mutation preflight (including six release statements), not inferred from BluPal equivalence. Constitutional I/II/III/V/VI reviewed, offline test-first scope only; existing failure limitations characterized without repair. Source-to-case mapping and artifacts above retained. Snapshot covers all tracked files. Default GeminiFlashHigh{} remains routing recommendation; direct work under step4 and small-residual rule.

Pending checks on stable source/tests: reference/mutations session71750, timeout15m +15s grace, `/tmp/t050bb-bc-review.log`; full offline session90585, timeout20m +15s grace, `/tmp/t050bb-bc-offline.log` and XML. Commands: `.venv/bin/python briefs/review/T050bb-bc/verify.py` (feature path prefix), and `.venv/bin/python -m pytest tests/characterization tests/unit tests/contract tests/integration tests/acceptance --network=deny -q --tb=line --junitxml=/tmp/t050bb-bc-offline.xml`. Expected77referencepasses,26mutants;4819offlinepasses+601declaredfailures. Not accepted until completed exit/results/hash comparison.

Review session71750 exit0:77referencepasses,26validindependentmutations detected; failing IDs match targeted rule families (guard order/product/reason/early effects, legacy identity/terms/SQL/claim/repeat/price/reward/failure release/admin). No errors/skips/unresolved survivors. Scratch auto-cleaned. Full offline90585 remains pending; source/tests unchanged.

Combined final acceptance: offline90585 exit1,4819passes+601declaredmissingT051–053failures/5420total;581baseline failure IDs/reasons unchanged plus20missingT053 composite guard assertions. Two history failures differed only in generated UTC date (Nov7->Nov8); inspected full diff and normalized truncated date+clock, no behavior difference. Protected tracked source/tests/artifacts unchanged.77referencepasses,26validindependentmutations;no errors/skips/regressions/unresolvedsurvivors/pendingchecks. bb/bc accepted together. Default coder none, all sensitive tests authored/reviewed by orchestrator. Batch7 continues bd/be; no T051 implementation or push.
