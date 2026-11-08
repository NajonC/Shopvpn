# Brief T050bv-bw: manual STOCK/DIRECT approval

- **Status**: accepted
- **Parts**: bv success/repeat + bw failure/alias, first pair of batch12
- **Type**: test-only
- **Orchestrator**: actual/recommended gpt-6.1-sol/high; settled bounded contracts
- **Coder**: none; default antigravity/gemini-3.8-flash-high{} available
- **Tests written by**: orchestrator under skill step4 (money/authority/repeats)

## Goal
Pin real cb_order_approve STOCK/DIRECT downstream behavior beyond bounded T050d seams, refusing selected composite order/product before claim, status response or fulfillment. Owner authorizes compatible paired packets and commits. No production implementation, worktree, push or T051.

## Rules
“Every legacy path listed in T051–T053 rejects a composite product, order or subscription with an explicit reason before any side effect” [T050]. “Composite rows are routed to `composite/service.py` or refused; legacy code never claims, provisions or rewards them.” [T052]. “Composite records MUST NOT accidentally enter legacy single-panel renewal, connection-alert, delete, supply or grant logic.” [FR-081]. “Existing legacy surfaces remain compatible.” [NG-01]. “Composite purchases/renewals create no purchase-based referral rewards, referring-reseller commissions, deferred payout promises or first-purchase referral consumption.” [NG-05]. Ordinary approved composite manual payments are not globally banned [FR005].

## Files and interfaces
New tests/integration/test_composite_manual_catalog_guards.py; this brief, review/T050bv-bw artifacts, tasks.md progress. Production and all existing tests read-only. handlers_admin.py cb_order_approve1777–1974; actual SQL claim/stock/direct provider factory preserved. Synthetic Telegram/provider responses/delivery only. Fixture aliases dict/sqlite selected order/product; unrelated composite sibling remains allowed.

## Tests / checks
116 cases:24 composite order/product×dict/sqlite×STOCK/DIRECT×success/failure/prior;80 legacy cases absent/explicit kind×quantity0/2×success/failure/prior/lost claim/delivery;12 opaque role/parse/missing controls. Real stock shortage and second-create compensation. Exact paid delivery900, STOCK reward117 from900; DIRECT no reward; quantity0->1; 10GB/17day custom persistence/history/order linkage. Approval/audit before delivery, swallowed delivery errors and completed repeats pinned. Both DBs unchanged on refusal; no secret-bearing reason. Pending guarded production failures must be only24 intended missingT052 cases.

Run .venv/bin/python -m pytest tests/integration/test_composite_manual_catalog_guards.py --network=deny -q. Reference/mutations: .venv/bin/python specs/001-composite-subscriptions/briefs/review/T050bv-bw/verify.py. Full quickstart five-directory suite --network=deny; compare.py XML against T050bt-bu/offline-failures.json. All tests sensitive; no coder delegation needed.

## Open points
None.

## Reviewer verification
Setup clean5513d5c; prerequisites via bash(nonexecutable script); no extensions.yml; requirements26/26 checked. Read tasks header/layout,T050–053,FR005/081,NG01/05,SC012,constitutionI–III and skill verification. Historical accepted briefs only. No gate lifted by synthetic evidence. Initial fixture incorrectly patched router-local menus; removed before final checks.

Reference only adds admission to actual callback before status/claim; all real fulfillment untouched. Rule mapping: composite aliases->noeffects/reason plus omit/order/product/wrongselected/earlyclaim; valid legacy->overstrict; authority->opaque/noauthority; amounts/recipient/quantity->exact delivery/reward/state; failure->release/compensation; repeat->prior/real lost claim. Accepted bf-bg/bj-bk downstream mutants reused only after every source/test hash matched(reused-evidence.json), not new mutation counts. Source/test snapshot protects prior work. status-removal is redundant with conditional claim and identical refusal; retain combined status+claim removal mutant to verify business fence. Full suite separately compares all prior IDs/stable reasons. All new source/artifact lines independently reviewed. T050 stays unchecked; custom approval and extraGateway remain unclosed.

## Delegation log
Direct sensitive work, no delegated/background coder responsibilities.

Final tests staged/frozen. Required review session and full offline launched with timeout25m+kill15s; logs /tmp/b12-pair1-review.log and /tmp/b12-pair1-offline.log, XML /tmp/b12-pair1-offline.xml. Source at5513d5c plus packet diff; snapshot records every protected input. Both pending: do not accept/commit or start pair2 until completion. Runner22 validated transformations:reference+21 independent mutants. Full reference also runs36 approval characterization cases. Prior step target24 intended admission failures+80legacy passes before12opaque addition; final full suite/reference will include all116.

Review27289 stopped after reference155pass and first6kills: overly strict legacy guard caused the expected success trace to be empty, so trace[0] raised IndexError. This is a relevant expected-behavior failure in the test body (legacy provision never began), not collection/setup/import failure. Runner explicitly admits only this named mutant + exact success case + exact IndexError; all other mutants still require assertions. Production/test inputs unchanged; no broad suite rerun needed for runner-only validation correction. Full campaign restarts from fresh reference; earlier partial results not double-counted.

Offline3895 exit1:5989pass+1037declaredfailures/7026total,883.50s. compare.py verifies all1013prior failure IDs and stable reasons unchanged+24newmissingT052 failures; protected hashes match. Noerrors/skips/regressions. Reference155cases (116new+39approval characterization), not36as initially estimated. First attempted validator restart used unavailable bare python and was interrupted explicitly before replacement; no results counted. Corrected full campaign launched /tmp/b12-pair1-review-corrected.log timeout25m+15s; pending. No production/tests changed after offline run.

Review83578 exit0:155referencepasses(116new+39approvalcharacterization),21validindependentNEWmutants detected; no survivors/unexecuted/unresolvedinvalidchecks. One overstrict guard is detected by the exact missing-success-trace IndexError explained above; all other kills are relevant assertions. Scratch cleaned via TemporaryDirectory, including interrupted restart. All changed test/source-artifact lines reviewed; all hashes match. Offline5989pass+1037exactdeclaredfailures/7026total,883.50s. Pair accepted test-first; no production code changed. No remaining responsibilities for this pair.
