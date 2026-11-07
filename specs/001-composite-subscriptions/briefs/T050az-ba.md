# Brief T050az–ba: BluPal direct custom fulfillment

- **Status**: accepted
- **Tasks**: T050az success/repeat and T050ba failure boundaries, combined under owner authorization. Neither accepted independently.
- **Packet type**: test-only
- **Orchestrator**: actual/recommended gpt-6.1-sol/high, established bounded custom contract
- **Coder**: none; default antigravity/gemini-3.8-flash-high options {}; every test is sensitive (money/identity/repeat/crash ordering), orchestrator-owned per step4; brief exceeds residual coder work
- **Tests written by**: orchestrator

## Goal

Protect direct BluPal custom-order fulfillment before claim/provider/SQL/delivery/referral. Characterize legacy success/repeat and caught versus propagated failures without changing production. These two adjacent normal-sized scenario families share the same helper/fixtures/reference and one combined offline acceptance run.

## What already exists

blupal_payment.py finalize_paid_order173–280 reads order, checks pending, claims, selects custom server and GLOBAL duration, constructs real provider factory, creates remote user, adds SQL config/history, approves, delivers, rewards on BASE price and notifies. database.py create_custom_config_order3322, approve3353, add_custom_config6987/history7142, referral4370. panel_providers/__init__.py get_provider98 dispatches PROVIDERS. Prior callback tests do not cover direct successful fulfillment. miniapp/server.py webhook independently verifies and sends a return-to-bot message for custom orders; no helper delegation there. Not included here.

## Rules

1. “Every legacy path listed in T051–T053 rejects a composite product, order or subscription with an explicit reason before any side effect” [T050]
2. “Composite rows are routed to `composite/service.py` or refused; legacy code never claims, provisions or rewards them.” [T052]
3. “Reject composite requests before any side effect on the unsupported channels” [T053]
4. “Existing legacy surfaces remain compatible.” [NG-01]
5. “Composite purchases/renewals create no purchase-based referral rewards, referring-reseller commissions, deferred payout promises or first-purchase referral consumption.” [NG-05]

## Files

Create tests/integration/test_composite_blupal_fulfillment_guards.py. Production and prior tests read-only. Review artifacts under review/T050az-ba orchestrator-owned. No new dependencies/network.

## Interfaces / Tests

Actual finalize_paid_order(db,bot,order_id,notify_admins_fn=None), actual SQL and factory registry; only provider constructor/create and delivery/Telegram are synthetic boundaries. Missing/explicit legacy and dict/sqlite forms; unrelated composite sibling is always present. Selected order/product composite refuses before trace/DB, explicit secret-free reason. Scenarios success/factory/create/delivery/prior:20 missing-T053 failures. Success/send/admin variants:12 pass, order approved, selected config/history retained with created_name,10GB/global45days (order saved17), correct owner/server/order/link/source, final900 delivery before reward, base1000 at13%=130 credited once, first-purchase flag consumed once, exact reward/admin messages, repeat no effects. Missing/server/factory/create/add/approval/delivery/prior/lost conditional claim:36 pass. Early caught errors release to pending, add error leaves processing/no row, approval error leaves row/processing, delivery error leaves row/approved; no reward/notification after failure. Existing limitations remain characterized only. Lost claim uses actual processing row and stale pending read; no artificial claim success.

## How to check

.venv/bin/python -m pytest tests/integration/test_composite_blupal_fulfillment_guards.py --network=deny -q
Full offline five directories --network=deny, once after combined final diff. Baseline4723passes+561declaredmissingT051–053failures; add48passes+20missingT053failures =4771passes+581failures/5352total. Exact failures compared to review/T050ax-ay/offline-failures.json plus packet XML; stable reasons normalized for process IDs/addresses only.

## Out of scope

Production implementation/T051+, ordinary approved composite manual routes, renewal/catalog fulfillment, Noapay/AbanGateway, webhooks, real panels/providers, legacy failure repairs, push. Four-part batch ends after ax/ay and az/ba accepted together as pairs.

## Open points

None.

## Reviewer verification

Prior pair c9761f8 accepted/clean. Prerequisite/checklist26/26/hooks absent unchanged. Independently read entire blupal_payment.finalize_paid_order173–280 and callers handlers_user991/handlers_admin2387; miniapp2334 uses separate inline custom notification, not helper. extra_gateway_payment323 dispatches AbanGateway helper, not BluPal. Shared DB/factory source contracts revalidated against FR081/082/086,NG01/02/05,FR005,SC012,T050–053 and constitution I/II/III/VI. No new authority/product decision. Test-only no production/live service evidence. All money/identity/repeat tests orchestrator-owned; no residual coder work.

Source-to-test and mutations: composite order/product selection/refusal/reason/before-effects ->20negative cases, omit each/both, early claim, wrong product, overstrict legacy/sibling variants. Legacy helper -> real factory constructor/create args, selected SQL owner/server/order/name/volume/global45duration/link/history/approval, delivery final900 before base1000 referral130 once, notifications and repeat; mutate these identities/terms/price/amount/omissions/status/claim/release/error/success. Failure family -> missing server/constructor/create caught and released; add/approval/delivery errors propagate leaving exact rows/status and no later reward; protected existing behavior only.68newcases must all pass on scratch reference; mutation campaign requires independent relevant assertions/pytest.raises failures, no setup/error/skip kills or survivors. Variants reused only after actual BluPal source exact-match/AST preflight; separate per-gateway executable scratch/reference/source hashes. No production bypass/reference patch. One full offline run only for entire az/ba pair after final diff; compare561baselinefailure IDs/reasons plus20declared missingT053 cases, protect all prior tests/artifacts. Global duration17->45 legacy difference and post-persistence failure limits characterized only, no production repair. Both constituents remain unaccepted until all combined evidence settles.

## Delegation log

Auto approved under owner's paired-packet authorization. Direct sensitive tests only per skill step4, no coder. Source/test/variant line review completed independently before launch. Actual Sol/high; default GeminiFlashHigh{} routing remains unchanged. Stop after four total parts (ax/ay + az/ba), no fifth part or push.

- Pending review84633: timeout15m/15s verify.py -> /tmp/t050az-ba-review.log; expected77referencepasses/26validmutations. Pending offline33773: timeout20m/15s full five directories -> /tmp/t050az-ba-offline.log/XML. Source/test unchanged after launch. Expected4771passes+581exactdeclaredmissingT051–053failures,5352total. Full first-pair baseline c9761f8 protected by snapshot. Remaining inventory prepared with explicit pending-final status and no fifth part. Final report only after both checks settle, exact failure comparison, acceptance/commit/clean tree.

- Review84633 exit0:77referencepasses (68new+9callbackcharacterization),26validindependentmutations detected, no errors/skips/unresolvedsurvivors. Each result/failing ID and source mapping independently reviewed against its variant; selected BluPal module/import hashes confirmed, prior AbanGateway files untouched. Source/helper/factory/SQL contracts independently inspected before pattern reuse; no assumption that one helper test protects the other. Scratch auto-cleaned. Final offline33773 remains sole pending responsibility before acceptance/commit/report.

- Combined final acceptance: offline33773 exit1,4771passes+581exactdeclaredmissingT051–053failures/5352total; all561priorfailure IDs/stable first assertion reasons match after process address/clock normalization,20newfailures exclusively designated custom-dispatch/reason assertions. All examined and protected hashes unchanged.77referencepasses/26validmutations, no errors/skips/regressions/unresolvedsurvivors/pendingchecks. Both az and ba accepted together. Total batch136newcases/40newmissingT053failures/52validindependentmutations; exactlyTWO final offline runs for FOUR normal-sized scenario families. Prior pair c9761f8. No production changes or push, T050 remains unchecked, nextT050bb Noapay direct custom success/repeat; exact inventory review/T050az-ba/remaining.md. No fifth part begun. Final commit/clean-state and queued supervisor report close batch.
- Final XML independently confirms588characterization+53provider-factorylegacy cases pass. BATCH_COMPLETE/T050_REMAINING after final commit/report; no T050_COMPLETE claim. No live-service or release-evidence claims.
