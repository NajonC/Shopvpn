# Brief T050bx-by: manual AUTO/pool renewal approval

- **Status**: accepted
- **Parts**: bx success/repeat + by failure/alias, second/final pair of batch12
- **Type**: test-only
- **Orchestrator**: actual/recommended gpt-6.1-sol/high; settled bounded contracts
- **Coder**: none; default antigravity/gemini-3.8-flash-high{} available
- **Tests written by**: orchestrator under skill step4 (money/authority/repeats)

## Goal
Pin real cb_order_approve AUTO/pool renewal downstream behavior beyond bounded T050d seams, refusing selected composite order/product before claim, status response or fulfillment, including renewal target marker. Owner authorizes compatible paired packets and commits. No production implementation, worktree, push or T051.

## Rules
“Every legacy path listed in T051–T053 rejects a composite product, order or subscription with an explicit reason before any side effect” [T050]. “Composite rows are routed to `composite/service.py` or refused; legacy code never claims, provisions or rewards them.” [T052]. “Composite records MUST NOT accidentally enter legacy single-panel renewal, connection-alert, delete, supply or grant logic.” [FR-081]. “Existing legacy surfaces remain compatible.” [NG-01]. “Composite purchases/renewals create no purchase-based referral rewards, referring-reseller commissions, deferred payout promises or first-purchase referral consumption.” [NG-05]. Ordinary approved composite manual payments are not globally banned [FR005].

## Files and interfaces
New tests/integration/test_composite_manual_auto_pool_guards.py; this brief, review/T050bx-by artifacts, tasks.md progress. Production and all existing tests read-only. handlers_admin.py cb_order_approve1777–1974; actual SQL claim/renewal/AUTO provider factory preserved. Synthetic Telegram/provider responses/delivery only. Fixture aliases dict/sqlite selected order/product; unrelated composite sibling remains allowed.

## Tests / checks
102 cases:30 composite selected order/product/AUTO and order/product/target/pool renewal×dict/sqlite×success/failure/prior;60legacy cases absent/explicit kind×AUTO quantity0/2 or renewal×success/failure/prior/lostclaim/delivery;12opaque role/parse/missing controls. Real foreign renewal owner failure and second-create compensation. Exact paid delivery900; no AUTO/renewal referral rewards; quantity0->1; 10GB/17day custom persistence/history/order linkage. Approval/audit before delivery, swallowed delivery errors and completed repeats pinned. Both DBs unchanged on refusal; no secret-bearing reason. Pending guarded production failures must be only30 intended missingT052 cases.

Run .venv/bin/python -m pytest tests/integration/test_composite_manual_auto_pool_guards.py --network=deny -q. Reference/mutations: .venv/bin/python specs/001-composite-subscriptions/briefs/review/T050bx-by/verify.py. Full quickstart five-directory suite --network=deny; compare.py XML against T050bv-bw/offline-failures.json. All tests sensitive; no coder delegation needed.

## Open points
None.

## Reviewer verification
Setup clean29b8f4b; prerequisites via bash(nonexecutable script); no extensions.yml; requirements26/26 checked. Read tasks header/layout,T050–053,FR005/081,NG01/05,SC012,constitutionI–III and skill verification. Historical accepted briefs only. No gate lifted by synthetic evidence. Pair1 router-local menu fixture correction retained unchanged.

Reference only adds admission to actual callback before status/claim; all real fulfillment untouched. Rule mapping: composite aliases->noeffects/reason plus omit/order/product/wrongselected/earlyclaim; valid legacy->overstrict; authority->opaque/noauthority; amounts/recipient/quantity->exact delivery/reward/state; failure->release/compensation; repeat->prior/real lost claim. Accepted bf-bg/bj-bk downstream mutants reused only after every source/test hash matched(reused-evidence.json), not new mutation counts. Source/test snapshot protects prior work. status-removal is redundant with conditional claim and identical refusal; retain combined status+claim removal mutant to verify business fence. Full suite separately compares all prior IDs/stable reasons. All new source/artifact lines independently reviewed. T050 stays unchecked; custom approval/custom-service renewal/extraGateway remain unclosed. No fifth part.

## Delegation log
Direct sensitive work, no delegated/background coder responsibilities.


Pair2 source audit: actual renewal_engine.execute_renewal config branch calls extend_pool_config_expiry; AUTO delegates reseller_auto_provision real two-DB credit, mirror, persistence. No new lifecycle/product choices. Exact20GB debit forquantity2 and10day extension from2030-01-01 to2030-01-11; preserve unrelated inventory. New reference covers selected pool target only, not custom renewal. Dependency prior pair tests reused unchanged and included in full reference. Independent audit/illicitreward/target/dispatch/release/approval mutants supplement paired1evidence.

Target71424 exit1:72legacy productionpasses+30intendedmissingT052failures/102total,12.66s,noerrors/skips. All new source/artifact lines independently reviewed; variants25transformations validated. Accepted downstream bf/bg,bh/bi,bj/bk,bl/bm source/test hashes rechecked and match, not recounted as new mutants. Tests staged/frozen at29b8f4b plus packet diff. Final reference/mutation /tmp/b12-pair2-review.log and second/final offline /tmp/b12-pair2-offline.log XML /tmp/b12-pair2-offline.xml launched timeout25m+kill15s. Pending; no acceptance/commit/fifth part until checks settle. No delegated coder responsibilities.

Review89934 exit0:257referencepasses(102new+116priorpair+39approvalcharacterization),24validindependentNEWmutants detected/no survivors. All failedIDs independently reviewed: renewal target omission/wrongtarget, foreign release, approvals/audit/illicitreward, price/recipient/dispatch/quantity and fences fail relevant tests. Overstrict exact expectedbehaviorIndexError disposition retained. Allinputhashesmatch; scratch automatically cleaned. No pending coder work. Second/final full offline87932 remains pending; do not accept/commit until comparison completes. Ownlink <t3-thread://v2/6702b80d-8413-4716-8002-71572e618486/mcp:launch:36259891e05e0c1bc2115a6e3afc18c3ed94dd0bfd2cdc133707eb84ffd9d7a1>. Supervisor0ccb8e07-3bec-440b-a8e8-e175fc6e10ce finalnotificationonlyaftersettlement.

Offline87932 exit1:6061pass+1067exactdeclaredmissingT051–053failures/7128total,860.69s. compare.py verifies ALL1037priorfailureIDs/stableassertionreasons+30newmissingT052cases,protectedsource/testhashes. ALL588characterization+53providerfactorylegacy pass BOTHbatch12suites. Noerrors/skips/regressions/survivors/unexecutedchecks. Allnewsource/test/artifactlinesreviewed; scratchcleaned. Bothrequiredcheckssettledbeforeacceptance. Batch12exactlyfourparts/twopairs,218newcases,reference155+257caseexecutions(includes116priorpairreruns),45NEWvalidindependentmutants. T050unchecked, noT051/fifthpart/productionchanges/worktrees/push. Remaininginventory review/T050bx-by/remaining.md. NextT050bz manualcustompurchase success/repeat+candidateca failure afteraudit; customrenewaltargets andextraGateway remain. Allresponsibilities/background/delegatedcheckssettled; BATCH_COMPLETE/T050_REMAINING aftercommit.
