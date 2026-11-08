# Brief T050bp-bq: admin BluPal invoice continuation

- **Status**: accepted
- **Tasks**: T050bp success/repeat + T050bq failure/alias boundaries (batch10 second/final combined packet)
- **Packet type**: test-only
- **Orchestrator**: actual/recommended gpt-6.1-sol/high; bounded established dispatch contract
- **Coder**: none; default antigravity/gemini-3.8-flash-high{} available, unchanged
- **Tests written by**: orchestrator (money, authority, repeats); no residual coder work

## Goal
Reject composite custom order/product aliases in the upstream admin automatic-payment status callback before acknowledgement, remote verification or shared dispatch. Preserve actual legacy status/finalization/SQLite and permitted general topups. This does not ban approved ordinary composite manual payments. Owner authorizes adjacent success/failure pairing, one acceptance/commit/offline suite.

## What already exists
handlers_admin.py2365–2398 cb_check_blupal_invoice(call,bot); blupal_payment.py134–287 try_verify_and_finalize/finalize_paid_order/finalize_paid_topup. Real router, admin role lookup, invoice parsing, selected invoice/order/custom-product identity and helper/SQL chain retained. Earlier T050d only bounded manual order review; T050av only user callback. No upstream closure inferred from them.

## Rules
1. “Every legacy path listed in T051–T053 rejects a composite product, order or subscription with an explicit reason before any side effect” [T050].
2. “Composite rows are routed to `composite/service.py` or refused; legacy code never claims, provisions or rewards them.” [T052].
3. “Composite records MUST NOT accidentally enter legacy single-panel renewal, connection-alert, delete, supply or grant logic.” [FR-081].
4. “Existing legacy surfaces remain compatible.” [NG-01].
5. “Composite purchases/renewals create no purchase-based referral rewards, referring-reseller commissions, deferred payout promises or first-purchase referral consumption.” [NG-05].

## Files / interfaces
Create tests/integration/test_composite_admin_blupal_status_guards.py (reuse protected common helpers in test_composite_admin_abangateway_status_guards.py), this brief, review/T050bp-bq artifacts. Change tasks.md progress only. All production, existing tests and prior evidence read-only. No coder handoff because all new tests decide sensitive behavior. Reuse real synthetic catalog, prepare, FakeCallbackQuery/RecordingBot and as_row(dict/sqlite); provider create_user and delivery boundary synthetic, actual verifier/finalizer/claim/persistence/topup SQL retained. No network/config/secret imports outside synthetic harness.

## Tests
72 cases: 16 composite order/product×dict/sqlite×pending/expired/paid/completed require one explicit alert, no remote/verify/claim/provision/delivery, identical entire DB, secret-free result. 48 legacy missing/explicit-kind×dict/sqlite×12 scenarios pending/partial/expiry/cancel/completed/remoteerror/claimloss/missingkey/priororder/missingserver/providerfailure/success. Exact remote key/id, verify ordering, selected status/claim, provider username/10GB/settings30days, persisted URL/terms/order linkage and 900 delivery; unrelated composite sibling ignored. Completed repeats no effect. Six malformed/missing/unauthorized opaque refusals, two general topups preserve composite unrelated order while crediting exactly321 once. BluPal has no separate verify endpoint: only real local claim admits delivery. claim_lost injects one competing real SQL claim then asserts actual second claim fails and no order claim/provision/delivery occurs. No canned verification/provision/settlement answers; only remote transport/provider/Telegram boundaries synthetic.

## How to check
.venv/bin/python -m pytest tests/integration/test_composite_admin_blupal_status_guards.py --network=deny -q
Expected 56 legacy passes and16 missing T052 admission failures. Full baseline IDs/stable reasons in review/T050bn-bo/offline-failures.json (869). Reference: .venv/bin/python specs/001-composite-subscriptions/briefs/review/T050bp-bq/verify.py (all72+9callback cases). Independent guard/identity/authority/ordering/overstrict/callback/finalizer/verifier/topup mutations from clean reference. One final quickstart offline five-directory suite, compare.py checks all prior identities/reasons and protected hashes. Expected status: new owned test/brief/review files only; no user changes.

## Out of scope
Manual cb_order_approve branches, extra gateway and MiniApp/webhook/user callbacks, ordinary catalog aliases, deletion/cancel, reward-hook closure, live providers, production fixes/T051+, worktrees/push/fifth part.

## Open points
None.

## Reviewer verification
Setup: clean8b207e1 expectedbranch; prerequisites via bash (script not executable); no extensions.yml/hooks; requirements checklist26/26 pass; no active prior packet (historical template comments ignored). Plan layout/tasks conventions and T050–053, FR005/081/082/086, SC012, NG01/05 independently reviewed; constitution I/II/III/V/VI. Offline tests of existing payment behavior do not lift G-P implementation/release gates. No unresolved product/evidence gate.

Mapping: T050/T052/FR081 aliases -> composite matrix/noeffects -> omit/order/product/both/ref/reason/earlyack/earlyverify. FR005/SC012 authority -> opaque cases -> omitrole/wronginvoice. NG01 valid controls -> legacy matrix/sibling/topup -> overstrictguard/topupban/wrongrefs. FR082 verifier/provider persistence -> exact remote/verify/status/provision/SQL/URL/delivery -> ignoreclaimloss/wrongremote/nostatuswrite/nofinalizer. ConstitutionII repeats/money -> completed replay/exact321 approvedtopup -> nocompletedfence/noapprovetopup. Reference supplies only bounded custom alias admission before callback ACK; no production implementation claimed.

Artifacts: snapshot.json all tracked hashes/diffs baseline; variants.py,verify.py,compare.py,evidence.json,expected_failures.json,offline-failures.json,remaining.md. Scratch exports only source/test Python (no .git/config/DB/credentials), confirms imports there and auto-cleans. Every mutation independent, exact match/AST validated; only relevant assertion failure counts. All new source/test/artifact lines must be reviewed before acceptance. T050 stays unchecked.

## Delegation log
Direct sensitive money/authority/repeat tests under skillstep4; no residualcoderwork. Prior pair accepted8b207e1. All earlier hooks/checklist gates unchanged; target/preflight pending. Pair bp success/repeat and bq failures/aliases follow actual distinct BluPal status normalization/conditionalSQLclaim semantics, not an extra doubled packet. Four assignedparts total; no fifth begins.

Target19118 completed exit1:56legacyproductionpasses+16intendedmissingT052guardfailures/72total,7.80s,noerrors/skips. All new case/source/artifact lines reviewed. SQL mutations additionally remove the real conditionalinvoiceclaim, credit322instead321 and leave topupstatuspending. The controlled competing-claim case catches SQL loss independent of helper checking. Reference preserves actual credit/claim/persistence SQL. Reusable prior critical sharedcustomfulfillment evidence is explicitly T050ax-ay and T050az-ba evidence.json/variants.py: all protected helper/test/database/factory hashes rechecked identical in this checkout. Prior26mutantsperhelper cover settingsduration/name/volume/owner/persistence/linkage/approval/release/deliveryprice/reward/admin semantics; the fullsuite reruns those tests. These reusable mutations are not recounted as new batch10 mutations. First pair likewise retains matching T050ax-ay evidence. No closure claimed for additional upstream aliases/extraGateway/manualreview.

Final source/tests staged/frozen; preflight27uniquevalidAST transformations(reference+26independentmutants). Review deadline20m+15s /tmp/t050bp-review.log and finaloffline deadline25m+15s /tmp/t050bp-offline.log/XML; bothpending. Session IDs recorded by harness. Exactlysecondfinalbatch10offline; noacceptance/commit/fifthpart/T051/delegates until checkssettle.

Review4352 completed exit0:81referencepasses(all72new+9callback),26validindependentmutantscaught(18callback+5helper+3realSQL),nosurvivors/errors/skips/invalid/unexecutedchecks. All failed-IDmappingsreviewed:actualclaimlosshelperandSQLconditionmutantsbothfailclaim_lostexactevents assertion;wrongSQLcredit/statusfail321/approvedtopupassertions;guard/alias/authority/ordering/overstrictcasesallrelevant. Everymutationstartsfromsamecleanreference/freshsyntheticDB. Scratchautomaticallycleaned. Offline26914stillpending;source/testsremainfrozen;noacceptance/commit/fifthpart. Batchreference166passesand50validnewmutantssofar,firstpaircommitted8b207e1.

Offline26914 completed exit1:5577pass+885exactdeclaredmissingT051–053failures/6462total,in784.21s. compare.py confirms869priorIDs/stableassertionreasonsunchanged+16newmissingT052guards;allprotected/source/testhashesmatch,noerrors/skips/regressions. Bothbatch10offlineXMLsindependentlyconfirmall588characterization+53providerfactorylegacypass. All new source/test/reviewerartifactlinesreviewed, all required checks settled, scratchauto-cleaned. No production changes/worktrees/push/T051implementation/fifthpart/delegates. T050 staysunchecked.

Batch10 fourpartsaccepted: bn success/repeat+bo failure/alias adminAbanGateway; bp success/repeat+bq failure/alias adminBluPal.148newcases,166referencepasses(including18callback),50validnewindependentmutantsnosurvivors. Exactlytwooffline suites:5521pass+869declaredfailures/6390total and5577pass+885declaredfailures/6462total. Acceptedtest-firstmissingT052guards, not a passingimplementation suite. Actual/recommendedSolhigh;defaultGeminiFlashHigh{}unchanged;all tests skillstep4 sensitive/orchestrator-owned,no residualcoderwork. No blockers or pendingchecks; preexistingcompleted-before-fulfillment and settingsduration30 legacysemantics characterized only. Exact remaininginventory review/T050bp-bq/remaining.md. NextrecommendedT050br:ordinarycatalogaliasesinupstreamadminAban/BluPalstatuscallbacks, then manualapprovaldownstreamclosure/extraGateway. BATCH_COMPLETE/T050_REMAINING aftercommitandcleanstatus. Finalnotificationtosupervisor0ccb8e07-3bec-440b-a8e8-e175fc6e10ce onlyafterallsettled;ownlink <t3-thread://v2/6702b80d-8413-4716-8002-71572e618486/mcp:launch:c5899fdd1833418fa490776ade6fe4e344f214d5c5d1d9d74db03ba9fd30b81d>.
