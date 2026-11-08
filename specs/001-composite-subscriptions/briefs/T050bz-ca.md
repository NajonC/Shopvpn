# T050bz-ca manual custom purchase approval

- **Status**: accepted
- Parts: bz success/repeat + ca failures/aliases, first pair batch13.
- Type: test-only. Actual/recommended orchestrator gpt-6.1-sol/high: settled bounded contracts. Default coder antigravity/gemini-3.8-flash-high{} available, none delegated: all tests sensitive money/authority/repeat cases owned under step4.

## Goal and rules
“Every legacy path listed in T051–T053 rejects a composite product, order or subscription with an explicit reason before any side effect” [T050]. “Composite rows are routed to `composite/service.py` or refused; legacy code never claims, provisions or rewards them.” [T052]. “Composite records MUST NOT accidentally enter legacy single-panel renewal, connection-alert, delete, supply or grant logic.” [FR081]. “Existing legacy surfaces remain compatible.” [NG01]. “Composite purchases/renewals create no purchase-based referral rewards, referring-reseller commissions, deferred payout promises or first-purchase referral consumption.” [NG05]. Preserve FR005 specifically approved ordinary composite manual decisions; guard applies to legacy dispatch only.

## Files and checks
Only tests/integration/test_composite_manual_custom_guards.py, this brief, review/T050bz-ca source artifacts and tasks.md progress. Existing production/tests protected. Actual handlers_admin.cb_order_approve1777–1890, actual SQL claim/approval/config/history/audit, provider factory retained. Only external provider and delivery fake. Source audit independently read T050–053,FR005/081,NG01/05,SC012,constitutionI–III,plan source layout. requirements26/26 checked, no extensions hooks. Nonexecutable prerequisite script run through bash. Clean HEAD20d4baa on current branch; no worktree/push.

76 new cases:12 composite order/custom_product_id aliases ×dict/sqlite ×success/panel failure/prior;64 legacy absent/explicit kind ×saved17/global45 day fallback ×success/inactive/taken/panel/prior/lostclaim/delivery/persistencefailure. Unrelated composite product allowed. Exact username,volume10,delivery900 recipient/link,custom product/order linkage,purchase history,audit,no referral/wallet effects. Real stale pending read+conditional claim failure and completed repeat fence. Inactive leaves processing; panel/taken release; persistence failure after approval leaves approved/no config. Existing non-atomic crash behavior characterized only.

Run .venv/bin/python -m pytest tests/integration/test_composite_manual_custom_guards.py --network=deny -q. Reference/mutations: .venv/bin/python specs/001-composite-subscriptions/briefs/review/T050bz-ca/verify.py. Full five-directory quickstart offline suite --network=deny and XML compare.py against review/T050bx-by/offline-failures.json.

## Open points
None.

## Reviewer verification
Production target63205:64passed+12intendedmissingT052failures,8.26s; no errors/skips. Every new line reviewed. Admission reference only checks selected order/custom product before status/claim; no canned fulfillment. Mutations independently break order/product selection/reason/earlyclaim/overstrict/claim+repeat/approval/amount/recipient/durationfallback/volume/name/linkage/audit/reward/release. Each must fail relevant assertion; no setup errors count. Status omission alone redundant with real conditional claim; combined mutant verifies fence. Snapshot all tracked baseline files; preserve unpublished history. Reference includes39 approval characterization cases. All source artifacts reproducible in secret-free temporary copy with automatic cleanup. No coder responsibilities.

Pending checks: review session25177 timeout25m+kill15s, log /tmp/b13-p1-review.log; full offline session93375 same deadline, log /tmp/b13-p1-offline.log XML /tmp/b13-p1-offline.xml. Both against20d4baa plus76newtests and review artifacts. Source/tests frozen until both finish. Run commands above; offline command .venv/bin/python -m pytest tests/characterization tests/unit tests/contract tests/integration tests/acceptance --network=deny -q --tb=line --junitxml=/tmp/b13-p1-offline.xml. No acceptance until final statuses and exact failure comparison. Remaining pair source audit confirms renewal_engine.py execute_renewal custom branch; actual owned target, selected custom product, full/volume/time modes and readback/persistence/history need callback coverage. No new product decision.

Review25177 exit0:115reference passes(76new+39approvalcharacterization),20valid independent new mutants detected, no survivors. Failure IDs independently inspected: guard/alias/reason/earlyclaim composite assertions; overstrict,repeat/claim/approval,terms/beneficiary/persistence/audit/rewards valid success assertions; fallback null duration case; release taken-error assertion. No invalid runs/exemptions. Protected evidence hashes independently matched. Scratch automatically cleaned. First full offline93375 remains pending, no acceptance yet.

Offline93375 exit1:6125passed+1079exact declared missingT051–053 failures/7204total,897.58s. All1067priorfailureIDs/stablereasons match plus12newT052failures; protectedsource/testhashesmatch. Noerrors/skips/regressions. Bothrequiredcheckssettled, allnewlinesreviewed, no survivors/coderresponsibilities. T050staysunchecked.
