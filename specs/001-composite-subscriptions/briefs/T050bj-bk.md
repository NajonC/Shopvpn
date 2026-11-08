# Brief T050bj–bk: ordinary DIRECT shared fulfillment

- **Status**: accepted
- **Tasks**: T050bj success/repeat + T050bk failures; batch9 first combined pair
- **Packet type**: test-only
- **Orchestrator**: actual/recommended gpt-6.1-sol/high; settled bounded admission and legacy contract
- **Coder**: none; default antigravity/gemini-3.8-flash-high{} routing unchanged
- **Tests written by**: orchestrator (authority, money, repeats; step4); no residual coder work

## Goal

Require composite order/product refusal before shared DIRECT claims, creation, persistence, reward or delivery. Preserve supported legacy fulfillment, including zero volume/duration, quantity fallback, planned names, collisions and failure behavior. Owner authorizes pairing success/repeat and adjacent failure family in one brief, acceptance and commit.

## What already exists

`finalize_paid_order(db,bot,order_id,notify_admins_fn=None)->str` in abangateway_payment.py171–302, blupal_payment.py173–301, noapay_payment.py203–334: conditional claim, catalog DIRECT/AUTO branch, approve_order_auto, delivery, referral and optional admin. direct_panel_provision.py35–161 actual quantity/server/terms, factory, names/retries/rollback and persistence. panel_providers/__init__.py get_provider165ff chooses PROVIDERS. database.py add_custom_config6987ff writes local rows/history; approve_order_auto3453ff; real referral SQL. Stock test setup supplies synthetic catalog/owner/referrer and wrapped actual SQL; no stock allocation occurs in these paths.

## Rules

1. “Every legacy path listed in T051–T053 rejects a composite product, order or subscription with an explicit reason before any side effect” [T050]
2. “Composite rows are routed to `composite/service.py` or refused; legacy code never claims, provisions or rewards them.” [T052]
3. “Composite records MUST NOT accidentally enter legacy single-panel renewal, connection-alert, delete, supply or grant logic.” [FR-081]
4. “Existing legacy surfaces remain compatible.” [NG-01]
5. “Composite purchases/renewals create no purchase-based referral rewards, referring-reseller commissions, deferred payout promises or first-purchase referral consumption.” [NG-05]

## Files / interfaces

Create tests/integration/test_composite_gateway_direct_guards.py, this brief and review/T050bj-bk/* review sources/results; add tasks.md progress only. All production and existing tests read-only. Real provision_direct/factory/SQL; synthetic PROVIDERS entry/remote create/delete and Telegram delivery/send/admin. Marker injection on actual order/product reads supports dict/sqlite.Row; unrelated composite product remains untouched. No live services/dependencies/worktrees/push.

## Tests

174 cases:48 composite3helpers×2representations×2aliases×4scenarios(success/second-unit failure/delivery/prior) require no trace/unchanged full DB and explicit secret-free reason.36positive3helpers×2representations×absent/legacy×3terms(quantity0/volume0/duration0;quantity2/10GiB/17days;durationNone=>30). Exact planned names, owner/panel/order/source/productNULL, persisted units/history, approval before delivery, ordered URLs/price900, base-price1000 reward130 and first-purchase consumption; repeat unchanged.90failures:inactive/factory/create/second/rollback/collision/persistence/approval/delivery/reward/send/admin/prior/lostconditionalclaim/missing. Exact trace/status/local rows/reward, collision suffix, rollback attempts; characterize swallowed persistence and failed compensation without repairing legacy limits.

## How to check

`.venv/bin/python -m pytest tests/integration/test_composite_gateway_direct_guards.py --network=deny -q`:126legacy passes+48expected missingT052 admission failures. Full baseline IDs/reasons:review/T050bh-bi/offline-failures.json (757failures). `.venv/bin/python specs/001-composite-subscriptions/briefs/review/T050bj-bk/verify.py`:all174+9callback reference passes, independent mutants from clean baseline; no invalid runs/survivors. One final five-directory offline suite for this pair. compare.py compares exact prior IDs/stable reasons,48designatednewfailures and protected/source/test hashes.

## Out of scope

AUTO (next pair), callers/webhooks/ordinary Telegram/UI, production implementation T051+, manual-payment route bans, compensation fixes, live evidence and release acceptance.

## Open points

None.

## Reviewer verification

Baseline clean2f0ac94;setup bash prerequisite script (executable bit absent),26/26 checklist,nohooks,nounfinishedbrief. tasks header/plan layout and FR005/081/082/086,SC012,NG01/05,T050–053,constitutionI/II/III/V/VI independently reviewed. Bounded dispatch refusal does not ban approved ordinary composite manual-payment workflows. Snapshot alltracked hashes; gitstatus clean before new file,staged/unstaged diff empty; preserve unpublishedhistory.

Mapping T050/FR081/T052->negativealiases(beforeclaim,reason,omitorder/product);NG01->positiveabsent/legacyandzeros(overstrictguard/zeroreject);FR082->realprovider/naming/terms/persistedrows(volume/duration/names/source/history/linkage/retries/rollback);NG05->noeffectsnegative/exact130positive(rewardomit/wrongamount/recipient);claim/status/quantity/owner/approval/delivery/release/admin mutations->exacttrace/state/repeats/failures. No canned function results in reference: scratch-only early admission insertion retains actual DIRECT/factory/SQL. No live-provider claim.

Artifacts verify.py/variants.py/compare.py/snapshot.json/evidence.json/expected_failures.json/offline-failures.json/remaining.md. Verify source-only exports to mktemp scratch, asserts imports point there, fresh SQL percase, independent mutants,AST/matchcounts, relevant assertion failures only,automaticcleanup.

## Delegation log

Direct step4 ownership,no coder. Initial targeted45310:120pass+48missingguard+6incorrectfactoryexpectations; corrected from actual source to propagating PanelError/processing. Initial review64104 cancelled after shell python-not-found prevented setup; no acceptance evidence from it. Corrected .venv/bin/python command. Review7017:15m+15sdeadline,/tmp/t050bj-bk-review.log; pending. Tests/source frozen.

Full offline97862:20m+15sdeadline,/tmp/t050bj-bk-offline.log,/tmp/t050bj-bk-offline.xml,pending; first of exactlytwo batch9finaloffline runs. Source revision2f0ac94 plus directtest; hashes recorded by review. Ownlink <t3-thread://v2/6702b80d-8413-4716-8002-71572e618486/mcp:launch:ed62b4bc47cd803d6e7b8d42f4144c49c38164da1d25c3168f88e5ef9c76b62a>. Supervisor0ccb8e07-3bec-440b-a8e8-e175fc6e10ce only notified at actual finalsettlement/blocker.

Review7017 completed exit1:183referencepasses and51helpermutants detected before invalid module-filter selection deselected all tests for DIRECT-module mutation. No invalid run counted as a kill; fixed runner selection to filter only gateway-named mutants. Corrected complete campaign54505,15m+15s,/tmp/t050bj-bk-review-fixed.log,pending. Production/test unchanged; offline97862 remains pending. Source review retained factory-before-try propagation and non-atomic persistence/delivery limitations.

Review54505 completed exit1 after183referencepasses+59validindependentmutants; last2SQLvariants blocked by AST parsing an indented method fragment, no mutationexecuted/counted. Corrected generator validates replacement count in fragment and AST on whole module. Complete campaign40007,15m+15s,/tmp/t050bj-bk-review-final.log,pending. No production/test edits; offline97862 remains pending. Independently reviewed AUTO source for next pair: real two-database credit/fixed inventory, atomic conditional consume, rollback, mirror and swallow local failures; fixed_product sqlite.Row uses .get and currently propagates AttributeError (will characterize, not repair).

Offline97862 completed exit1:5281passed+805declaredfailures/6086total in819.19s. Independently parsed XML:757prior failureIDs/stableassertionreasons exactly unchanged+48newDIRECTmissingT052guards. No errors/skips/regressions; all588characterization and53providerfactorylegacy pass. Only pendingresponsibility for this pair is corrected mutationcampaign40007 and finalhashcomparison. Source/tests remain frozen. AUTO draft prepared outside checkout only; no nextpacket implementation started before acceptance.

Final review40007 exit0:183referencepasses(174new+9callback);61validindependentmutants detected(17/helper+8actualDIRECT+2actualSQL),no survivors/invalid/unexecuted variants. Read all test/artifact/source lines and relevant failed-ID mappings; admission fails beforeclaim/reason, zero overstrict rejects permitted control, real provisioner/SQL changes fail exact terms/rows/history/linkage/trace. Corrected tooling runs supersede earlier incomplete attempts; no incorrect kill counted. Scratch auto-cleaned. compare.py final:all805declaredfailureIDs/stablereasons and allprotected/source/test hashes match. No errors/skips/regressions/pendingchecks/delegates. Pair accepted;T050 remains unchecked. Nextbl/bm,AUTOrealcredit/mirror,preservefixedRowbugcharacterization. Firstofflinesuite only; no furtherDIRECTbroadchecksneeded.
