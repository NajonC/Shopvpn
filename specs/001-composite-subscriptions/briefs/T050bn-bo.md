# Brief T050bn-bo: admin AbanGateway invoice continuation

- **Status**: accepted
- **Tasks**: T050bn success/repeat + T050bo failure/alias boundaries (batch10 first combined packet)
- **Packet type**: test-only
- **Orchestrator**: actual/recommended gpt-6.1-sol/high; bounded established dispatch contract
- **Coder**: none; default antigravity/gemini-3.8-flash-high{} available, unchanged
- **Tests written by**: orchestrator (money, authority, repeats); no residual coder work

## Goal
Reject composite custom order/product aliases in the upstream admin automatic-payment status callback before acknowledgement, remote verification or shared dispatch. Preserve actual legacy status/finalization/SQLite and permitted general topups. This does not ban approved ordinary composite manual payments. Owner authorizes adjacent success/failure pairing, one acceptance/commit/offline suite.

## What already exists
handlers_admin.py2194–2226 cb_check_abangateway_invoice(call,bot); abangateway_payment.py126–285 try_verify_and_finalize/finalize_paid_order/finalize_paid_topup. Real router, admin role lookup, invoice parsing, selected invoice/order/custom-product identity and helper/SQL chain retained. Earlier T050d only bounded manual order review; T050au only user callback. No upstream closure inferred from them.

## Rules
1. “Every legacy path listed in T051–T053 rejects a composite product, order or subscription with an explicit reason before any side effect” [T050].
2. “Composite rows are routed to `composite/service.py` or refused; legacy code never claims, provisions or rewards them.” [T052].
3. “Composite records MUST NOT accidentally enter legacy single-panel renewal, connection-alert, delete, supply or grant logic.” [FR-081].
4. “Existing legacy surfaces remain compatible.” [NG-01].
5. “Composite purchases/renewals create no purchase-based referral rewards, referring-reseller commissions, deferred payout promises or first-purchase referral consumption.” [NG-05].

## Files / interfaces
Create tests/integration/test_composite_admin_abangateway_status_guards.py, this brief, review/T050bn-bo artifacts. Change tasks.md progress only. All production, existing tests and prior evidence read-only. No coder handoff because all new tests decide sensitive behavior. Reuse real synthetic catalog, prepare, FakeCallbackQuery/RecordingBot and as_row(dict/sqlite); provider create_user and delivery boundary synthetic, actual verifier/finalizer/claim/persistence/topup SQL retained. No network/config/secret imports outside synthetic harness.

## Tests
76 cases: 16 composite order/product×dict/sqlite×pending/expired/paid/completed require one explicit alert, no remote/verify/claim/provision/delivery, identical entire DB, secret-free result. 52 legacy missing/explicit-kind×dict/sqlite×13 scenarios pending/partial/expiry/cancel/completed/remoteerror/alreadyverified/verifyerror/missingkey/priororder/missingserver/providerfailure/success. Exact remote key/id, verify ordering, selected status/claim, provider username/10GB/settings30days, persisted URL/terms/order linkage and 900 delivery; unrelated composite sibling ignored. Completed repeats no effect. Six malformed/missing/unauthorized opaque refusals, two general topups preserve composite unrelated order while crediting exactly321 once. No canned verification/provision/settlement answers; only remote transport/provider/Telegram boundaries synthetic.

## How to check
.venv/bin/python -m pytest tests/integration/test_composite_admin_abangateway_status_guards.py --network=deny -q
Expected 60 legacy passes and16 missing T052 admission failures. Full baseline IDs/stable reasons in review/T050bl-bm/offline-failures.json (853). Reference: .venv/bin/python specs/001-composite-subscriptions/briefs/review/T050bn-bo/verify.py (all76+9callback cases). Independent guard/identity/authority/ordering/overstrict/callback/finalizer/verifier/topup mutations from clean reference. One final quickstart offline five-directory suite, compare.py checks all prior identities/reasons and protected hashes. Expected status: new owned test/brief/review files only; no user changes.

## Out of scope
Manual cb_order_approve branches, extra gateway and MiniApp/webhook/user callbacks, ordinary catalog aliases, deletion/cancel, reward-hook closure, live providers, production fixes/T051+, worktrees/push/fifth part.

## Open points
None.

## Reviewer verification
Setup: clean2b42daa expectedbranch; prerequisites via bash (script not executable); no extensions.yml/hooks; requirements checklist26/26 pass; no active prior packet (historical template comments ignored). Plan layout/tasks conventions and T050–053, FR005/081/082/086, SC012, NG01/05 independently reviewed; constitution I/II/III/V/VI. Offline tests of existing payment behavior do not lift G-P implementation/release gates. No unresolved product/evidence gate.

Mapping: T050/T052/FR081 aliases -> composite matrix/noeffects -> omit/order/product/both/ref/reason/earlyack/earlyverify. FR005/SC012 authority -> opaque cases -> omitrole/wronginvoice. NG01 valid controls -> legacy matrix/sibling/topup -> overstrictguard/topupban/wrongrefs. FR082 verifier/provider persistence -> exact remote/verify/status/provision/SQL/URL/delivery -> noverify/nocomplete/wrongremote/nostatuswrite/nofinalizer. ConstitutionII repeats/money -> completed replay/exact321 approvedtopup -> nocompletedfence/noapprovetopup. Reference supplies only bounded custom alias admission before callback ACK; no production implementation claimed.

Artifacts: snapshot.json all tracked hashes/diffs baseline; variants.py,verify.py,compare.py,evidence.json,expected_failures.json,offline-failures.json,remaining.md. Scratch exports only source/test Python (no .git/config/DB/credentials), confirms imports there and auto-cleans. Every mutation independent, exact match/AST validated; only relevant assertion failure counts. All new source/test/artifact lines must be reviewed before acceptance. T050 stays unchecked.

## Delegation log
Direct sensitive tests under skill step4; no child. Initial production target found wrong success-text expectation; corrected from actual sharedhelper literal before verification. Target/verification/fullsuite pending.

Corrected production target exit1:60pass+16intendedmissingT052guards/76total,6.67s,noerrors/skips. Preflight25uniquevalidAST transformations(reference+24mutants). New tests staged/frozen; all new source/test/artifact lines reviewed. Review deadline20m+15s, /tmp/t050bn-review.log; offline deadline25m+15s /tmp/t050bn-offline.log/XML. Session IDs recorded by harness; bothpending. No acceptance/coder/nextpacket edits until settled. Actual source unchanged, protected baseline snapshot retained.

Review78104 completed exit0:85referencepasses(all76new+9callback),24validindependentmutantscaught,nosurvivors/errors/skips/invalid/unexecutedchecks. Every failed-IDmapping reviewed; aliases fail before remote and explicitreason, validcase overstrict refusal caught, actualverifier mutations fail exactremote/status/verify/repeat assertions, actualtopupapproval omission fails exactcredit/status. Reference scratch automaticallycleaned. Offline95204 stillpending; tests/sourceunchanged, noacceptance/nextpacket yet. Boundedcustomorder/productadmissionreference only; ordinarycatalogaliases/manualreview/extraGatewayremaininventory work.

Offline95204 completed exit1:5521pass+869exactdeclaredmissingT051–053failures/6390total,in768.74s. compare.py confirms853priorIDs/stableassertionreasonsunchanged+16newmissingT052admissionfailures,alltrackedprotected/source/testhashesmatch,noerrors/skips/regressions. All588characterization+53providerfactorylegacycasespass. New76cases/reference85/mutations24 accepted; no checks/delegates pending for this pair. Tests are test-first missingbehavior coverage, not a passing implementation suite. Source/test/artifact lines all reviewed; snapshot also confirms no production edits. T050 remains unchecked. Next T050bp/bq admin BluPal status success/repeat + failures/aliases, same Sol/high, defaultGeminiFlashHigh{}, sensitive tests owned here.
