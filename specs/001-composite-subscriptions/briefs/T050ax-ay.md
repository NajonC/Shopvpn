# Brief T050ax–ay: AbanGateway direct custom fulfillment

- **Status**: accepted
- **Tasks**: T050ax success/repeat and T050ay failure boundaries, combined under owner authorization. Neither accepted independently.
- **Packet type**: test-only
- **Orchestrator**: actual/recommended gpt-6.1-sol/high, established bounded custom contract
- **Coder**: none; default antigravity/gemini-3.8-flash-high options {}; every test is sensitive (money/identity/repeat/crash ordering), orchestrator-owned per step4; brief exceeds residual coder work
- **Tests written by**: orchestrator

## Goal

Protect direct AbanGateway custom-order fulfillment before claim/provider/SQL/delivery/referral. Characterize legacy success/repeat and caught versus propagated failures without changing production. These two adjacent normal-sized scenario families share the same helper/fixtures/reference and one combined offline acceptance run.

## What already exists

abangateway_payment.py finalize_paid_order171–272 reads order, checks pending, claims, selects custom server and GLOBAL duration, constructs real provider factory, creates remote user, adds SQL config/history, approves, delivers, rewards on BASE price and notifies. database.py create_custom_config_order3322, approve3353, add_custom_config6987/history7142, referral4370. panel_providers/__init__.py get_provider98 dispatches PROVIDERS. Prior callback tests do not cover direct successful fulfillment. miniapp/server.py webhook independently verifies and sends a return-to-bot message for custom orders; no helper delegation there. Not included here.

## Rules

1. “Every legacy path listed in T051–T053 rejects a composite product, order or subscription with an explicit reason before any side effect” [T050]
2. “Composite rows are routed to `composite/service.py` or refused; legacy code never claims, provisions or rewards them.” [T052]
3. “Reject composite requests before any side effect on the unsupported channels” [T053]
4. “Existing legacy surfaces remain compatible.” [NG-01]
5. “Composite purchases/renewals create no purchase-based referral rewards, referring-reseller commissions, deferred payout promises or first-purchase referral consumption.” [NG-05]

## Files

Create tests/integration/test_composite_abangateway_fulfillment_guards.py. Production and prior tests read-only. Review artifacts under review/T050ax-ay orchestrator-owned. No new dependencies/network.

## Interfaces / Tests

Actual finalize_paid_order(db,bot,order_id,notify_admins_fn=None), actual SQL and factory registry; only provider constructor/create and delivery/Telegram are synthetic boundaries. Missing/explicit legacy and dict/sqlite forms; unrelated composite sibling is always present. Selected order/product composite refuses before trace/DB, explicit secret-free reason. Scenarios success/factory/create/delivery/prior:20 missing-T053 failures. Success/send/admin variants:12 pass, order approved, selected config/history retained with created_name,10GB/global45days (order saved17), correct owner/server/order/link/source, final900 delivery before reward, base1000 at13%=130 credited once, first-purchase flag consumed once, exact reward/admin messages, repeat no effects. Missing/server/factory/create/add/approval/delivery/prior/lost conditional claim:36 pass. Early caught errors release to pending, add error leaves processing/no row, approval error leaves row/processing, delivery error leaves row/approved; no reward/notification after failure. Existing limitations remain characterized only. Lost claim uses actual processing row and stale pending read; no artificial claim success.

## How to check

.venv/bin/python -m pytest tests/integration/test_composite_abangateway_fulfillment_guards.py --network=deny -q
Full offline five directories --network=deny, once after combined final diff. Baseline4675passes+541declaredmissingT051–053failures; add48passes+20missingT053failures =4723passes+561failures/5284total. Exact failures compared to review/T050aw/offline-failures.json plus packet XML; stable reasons normalized for process IDs/addresses only.

## Out of scope

Production implementation/T051+, ordinary approved composite manual routes, renewal/catalog fulfillment, Noapay/BluPal, webhooks, real panels/providers, legacy failure repairs, push. Four-part batch ends after ax/ay and az/ba accepted together as pairs.

## Open points

None.

## Reviewer verification

Setup prerequisite via bash (script lacks executable bit); root branch clean7c3edaa; requirements checklist26/26 pass, hooks absent; previous packets accepted. Protected preexisting hash snapshot captured before edits. Source reviewed T050–053, FR005/081/SC012/NG01/02/05, constitution I/II/III/VI. No authority/product/evidence gate for offline test-only work.

| Source rule | Tests | Mutations |
| --- | --- | --- |
| custom refusal/order+product identity |20negative cases| omit each/both guards, no reason, early claim, wrong product, overstrict legacy/sibling |
| FR081 legacy factory/terms/SQL/history/approval/delivery |success + failures|wrong server/name/volume/duration/owner/link/order, omit add/approval, wrong price, delivery before approval|
| money/repeat/notifications |success + failures|wrong base amount, omit reward/admin, remove status/claim/release, wrong return and error reason|

Scratch executable reference adds custom-only order/product dispatch before status/claim. Ordinary routes untouched. Every new test must pass on reference; each deterministic AST-valid independent mutant must fail by relevant assertion, no errors/skips. Review evidence records exact failing IDs, source hashes, scratch cleanup. Full offline pending. Orchestrator read every new line independently against actual source; initial expectation corrected from1000 to900 delivery price after verifying create_custom_config_order subtracts wallet100; base reward1000 unchanged.

## Delegation log

No child: all sensitive tests owned by orchestrator. Shared checkout never mutated for reference. Auto approved under owner paired-packet authorization. No acceptance until combined checks settle.
- Pending checks: review session20124 (`timeout --kill-after=15s 15m .venv/bin/python .../review/T050ax-ay/verify.py`, /tmp/t050ax-ay-review.log); full offline session26063 (`timeout --kill-after=15s 20m .venv/bin/python -m pytest` five directories --network=deny -q --tb=line --junitxml=/tmp/t050ax-ay-offline.xml, /tmp/t050ax-ay-offline.log). Both examine unchanged production at7c3edaa plus the staged68-case test file. No coder running. No polling/acceptance while checks pending. Completion resumes review automatically.

- Review20124 stopped because mutation-validator only allowed literal assertion text; early_claim correctly triggered pytest.raises DID NOT RAISE for legacy lost-claim failure paths. Validator now accepts this explicit behavioral expectation failure too; exceptions/setup errors still rejected.77referencepasses established. Rerun campaign required; production/test diff unchanged and offline26063 remains pending.
- Review rerun39725 pending -> /tmp/t050ax-ay-review-r2.log, same15mdeadline. Compare tool ready for final XML: checks every prior failure ID and stable first assertion line (subsequent repr expansions are process-dependent); all20new failures must be designated custom-refusal assertion cases, protected hashes and reviewed evidence hashes unchanged. No extra full-suite run.

- Review39725 exit0:77referencepasses (68new+9callback characterization),26valid independent mutations detected; no survivors/errors/skips. Each mutant failure identity independently reviewed against its intended rule (order/product/refusal/overstrict sibling and legacy; actual SQL conditional claim; provider/server/username/volume/globalduration; retained owner/name/link/order/config approval; final-price delivery; base-price reward/notifications; caught release/error/return). No canned code under test. Full new source/test/tooling line review completed; finalprice900 is payment remainder, base1000 still referral basis. Existing post-persistence failures and global-duration behavior characterized only. Scratch auto-cleaned. Full offline26063 remains sole pending check; neither ax nor ay accepted.

- Combined final acceptance: offline26063 exit1,4723passes+561exactdeclaredmissingT051–053failures/5284total. All541priorfailure IDs/stable first assertion reasons match after removing process addresses and generated clock-of-day text (two history cases);20newfailures exclusively missing custom dispatch/reason. Protected hashes and examined source/test hashes unchanged.26validmutations/77referencepasses, no regressions/errors/skips/survivors/pendingchecks. Both ax and ay accepted together. No production changes or push.
