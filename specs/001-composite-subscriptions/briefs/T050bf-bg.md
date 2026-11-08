# Brief T050bf–bg: shared ordinary stock fulfillment

- **Status**: accepted
- **Tasks**: T050bf stock success/repeat + T050bg stock failure boundaries; one combined packet authorized by owner (first two of batch8's four parts).
- **Packet type**: test-only
- **Orchestrator**: actual/recommended gpt-6.1-sol/high; established admission contract, existing real allocation/approval/referral SQL
- **Coder**: none; default antigravity/gemini-3.8-flash-high options {}; all tests money/authority/repeat safety under step4, no residual implementation
- **Tests written by**: orchestrator

## Goal

Test refusal before shared ordinary stock legacy effects, while preserving existing legacy allocation, delivery, purchase reward, repeat and failure contracts. These tests target single-panel/stock dispatch only, preserving approved composite manual-payment routing elsewhere. No production change.

## What already exists

finalize_paid_order(db,bot,order_id,notify_admins_fn=None)->str in abangateway_payment171ff, blupal_payment173ff,noapay_payment203ff independently reviewed: get order/status/claim; ordinary get_product then stock selection, SQL approve, actual low-stock helper, delivery, reward SQL/customer send/admin. database.py add_product2836,add_configs2949,take_unused_configs3137,get_config_by_id3187,create_order3299,claim3413,approve3433; reward_referrer_if_first_purchase actual SQL. quantity uses `order["quantity"] or 1`. Allocation precedes approval, delivery precedes reward; no automatic compensation for later exceptions. stock_alerts.py check_and_notify_low_stock reads stock/threshold/state. No panel invoked for stock.

## Rules

1. “Every legacy path listed in T051–T053 rejects a composite product, order or subscription with an explicit reason before any side effect” [T050]
2. “Composite rows are routed to `composite/service.py` or refused; legacy code never claims, provisions or rewards them.” [T052]
3. “Existing legacy surfaces remain compatible.” [NG-01]
4. “Composite purchases/renewals create no purchase-based referral rewards, referring-reseller commissions, deferred payout promises or first-purchase referral consumption.” [NG-05]

## Files / interfaces

Create tests/integration/test_composite_gateway_stock_guards.py and review/T050bf-bg/*.py/json/md; this brief/tasks progress only. Prior files/production read-only. Real Database and real shared helpers, real stock alert and reward SQL; only Telegram/delivery boundary synthetic, row discriminators injected at real reads, dict and sqlite.Row. No network/dependencies. Tests sensitive; direct orchestrator authorship, no coder work.

## Tests

138 cases: 48composite order/product refusal before claim for success/shortage/delivery failure/prior across3gateways/2representations; explicit composite reason, no SQL/trace/secret. 24legacy success/repeat across3gateways/2representations/absent+legacy/quantity0+2: exact FIFO IDs, qty0->1, 17day booking, owner/order linkage, approved before delivery, exact title/links/900final price, 1000base reward->130referrer credit, first purchase consumed once, buyer wallet unchanged, repeat no changes. 66legacy failures: shortage(no partial allocation/release), allocation/approval/stock-state/delivery/reward exceptions (retained SQL characterized), swallowed referral/admin sends, prior/lost real conditional claim/missing. Exact trace, status, allocation and reward state.

## How to check

`.venv/bin/python -m pytest tests/integration/test_composite_gateway_stock_guards.py --network=deny -q`:90passes+48intendedmissingT052guard assertions. All existing 649 failures identified by review/T050bd-be/offline-failures.json remain accepted pending T051–053. Reference all138new+9callbackcharacterization must pass; independent mutations detect critical rule loss/overstrict validlegacy. Full five-directory quickstart suite once on final pair diff, compare exact prior failure IDs/stable reasons plus48specific newcases, protected file hashes. No error/skip/regression acceptance.

## Out of scope

Direct/auto ordinary provisioning, pool/config renewal(next pair), upstream verifiers/admin/extra_gateway, inline webhooks, manual composite route implementation, T051+, live services, push.

## Open points

None.

## Reviewer verification

Clean baseline46c37be. Prerequisite script required bash invocation (executable bit absent); returned correct feature. requirements checklist26/26 pass; no extensions.yml/hooks, no unfinished brief, git clean. Read tasks header/T050–053, plan source layout, specFR005/081/082/086/SC012/NG01/05 and constitution I/II/III/V/VI independently. No unresolved product/evidence gate in offline bounded seam. Existing valid manual-payment workflows remain outside the forbidden legacy stock dispatch.

Source-to-case/mutation map: order/product admission+reason+beforeeffects->negative test (omit each,earlyclaim,no_reason); absent/legacy/sibling->positive(overstrict); status/claim/qty->positive+prior/lost(failedclaim/status/qty mutations); actual allocation owner/product/FIFO/duration/linkage->success+failure SQL checks(wronguser/product/FIFO/duration/linkage); approval/alert/delivery arguments+ordering->success/errors(omitapproval/alert/delivery/wrongprice); rewardbase/recipient/admin->exacttrace+SQL+errors(omitreward/wrongamount/recipient/admin); release->shortage(omitrelease). Review artifacts variants.py deterministic edit/AST preflight,verify.py fresh synthetic scratch per independent variant/import preflight,evidence.json source hashes/dispositions,compare.py exact offline comparison,snapshot.json protects prior files,remaining.md inventory. Reference adds only early admission in scratch, no canned fulfillment; production remains missing guard.

## Delegation log

Direct sensitive tests only per step4; default Gemini routing unchanged, no coder residual. Targeted70075 completed exit1:90passes+48intended guard assertions, no setup/collection errors. All responsibilities pending final review/full offline.

Pending review1762: timeout15m+15s grace, `/tmp/t050bf-bg-review.log`, final tests/source frozen. Pending offline11070: timeout20m+15s grace, `/tmp/t050bf-bg-offline.log` and XML; exactly first batch8 full offline run. Source revision46c37be plus new stock test; hashes in evidence/snapshot. No coder/delegate. Resume on completion notifications; neither packet accepted while either check pending.

Review1762 completed exit0:147referencepasses(138new+9callbackregressions),60valid independent mutations detected(19perhelper+3realSQL), no survivors/errors/skips. Individually reviewed mappings: relevant stock assertions only, scratch auto-cleaned. Every changed/new source line reviewed; mutation source exact-count/AST preflight successful. Full offline11070 remains pending; no source/test changes while it runs. Second-pair research confirms renewal_engine config alias performs only extend_pool_config_expiry with owner SQL, never panel calls; aliases must inspect selected config AND its catalog product before claim, not infer closure from custom-config coverage. Next pair will cover that bounded dispatch and real SQL expiry/failure path.

Final acceptance: offline11070 exit1,5023passes+697exactdeclaredmissingT051–053failures/5720total.649prior IDs/stable assertion reasons unchanged plus48specificmissingT052stock guards;no errors/skips/regressions. All protected/source/test hashes match, 588characterization+53providerlegacy pass.147referencepasses,60validindependentmutants;no unresolved/pendingchecks/delegates. Combined bf/bg accepted; T050 remains unchecked. Next bh/bi pool/config renewal.
