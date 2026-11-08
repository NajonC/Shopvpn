# T050cr/cs — direct reference payable admission and kind/status controls

- **Status**: accepted
- **Tasks**: T050; cr selected-order predicate admission/status; cs wallet_topup/reseller_request predicate and isolation.
- **Packet type**: test-only
- **Orchestrator**: actual/recommended gpt-6.1-sol/high; bounded established boolean interface, no new settlement semantics.
- **Coder**: none; default antigravity/gemini-3.8-flash-high{} available, unchanged. All tests money/authority/repeat-sensitive and owner-written under step4. No nonsensitive implementation to delegate.

## Goal and source requirements
Exercise extra_gateway_payment.ref_still_payable(db,invoice)->bool directly, independently of the Stars adapter. Preserve the boolean contract: composite selected order/product returns False; existing adapter owns explicit user-facing refusal. Do not invent exception semantics for a predicate used inside short-circuit boolean expressions.
1. “Every legacy path listed in T051–T053 rejects a composite product, order or subscription with an explicit reason before any side effect” [tasks T050]. Predicate handles admission only; adapter reasons and downstream callers remain separate obligations.
2. “Existing legacy surfaces remain compatible.” [spec NG-01].
3. “Preserve observable commands, callbacks/deep links, stored conversation state, API/configuration meanings and customer data unless an explicitly specified composite safeguard changes a directly dependent path.” [spec FR-081].
4. “every unsupported composite channel and unauthorized cross-owner/tenant operation is rejected” [spec SC-012]. This boolean predicate does not establish settlement authority.
5. “Manual payment decisions are the explicit two-interface exception in FR-014.” [spec FR-005]. Approved ordinary composite manual payments remain permitted;no blanket ban.
Independently reviewed tasksT050–053,FR005/014/081,NG01,SC012,constitutionI/II/III/VI,planlayout,quickstartofflinegroups. No live/G-P authority lifted.

## Source / files / bounds
Audited extra_gateway_payment.py:ref_still_payable359–368;extra_gateway_user.py:stars_pre_checkout68–86;database.py:get_order/get_product/create_extra_invoice5408/get_topup4647 and topupstatuses4624–4685. Predicate checks referenced order/topup pending; returns True for reseller_request without reading request state. The latter is a compatibility characterization and downstream authority/status concern, not authorization to settle.
Create tests/integration/test_composite_extra_direct_payable_guards.py, this brief, review/T050cr-cs artifacts; change tasks.md only. All source/existingtests including cp/cq immutable. No T051,worktree,push,fifthpart.

## Owner tests / exact outcomes
Tests staged before review. Real fixture DB and selected get_order/get_product sqlite/dict aliases, real SQL invoice/ref IDs;no predicate mock. No remote/network calls. Existing setup external fakes are unused here.
- 16composite cases:dict/sqlite×order/product×new/pending/completed/cancelled invoice;selected order pending;False twice,exact entire DB retained,no remote/fulfillment effects.
- 20legacy order controls:dict/sqlite×absent/legacy×pending/approved/processing/rejected/missing;only pending True,twice,unchangedDB. Unrelated composite catalog decoy retained.
- 24topup controls:dict/sqlite×absent/legacy/composite unrelated order/product×pending/approved/rejected/missing topup;only pending True,read exact selected ref twice,unchangedDB. Three pending decoys prevent mistaken selection from masquerading as refusal. Distinct invoice/order/topup domains.
- 16reseller_request controls:dict/sqlite×fourinvoice statuses×two reference values,including missing request;True twice,no order/topup/request lookup,unchangedDB. This pins the current predicate only,not request fulfillment or payment authority.

## How to check
.venv/bin/python -m pytest tests/integration/test_composite_extra_direct_payable_guards.py --network=deny -q
Expected16missingT052refusals+60passes. Prior1317declaredmissingT051–053 IDs/reasons review/T050cp-cq/offline-failures.json. Openpoints:None. Current status contains only staged newtest/untracked brief+artifacts. No coder work.

## Reviewer verification
Baseline clean5f164c8; alltrackedPython source/tests protected by snapshot.json. Same26/26checklist/nohooks/noAGENTS. Reference variants.py adds order/product guard before pending-order return;booleanFalse,no userreason change. All76new+39approvalcharacterization must pass scratch reference.
Mutation map:order/product/selectedproduct->compositealiases;overstrict->pendinglegacy;orderstatus/approved/missing->exactorderbool;topupstatus/approved/missing/reference->exacttopupbool+readids;reference_domain->invoice/refdistinction;kind_dispatch->closedtopup;reseller_default->legacyTrue;narrowinvoiceStatus->composite+resellercontrols;globalcompositeban->unrelatedcomposite topuppreservation. Freshsource/syntheticDB per mutant,exacteditcount+ASTchecks,noinvalidkills.
Reproduce .venv/bin/python specs/001-composite-subscriptions/briefs/review/T050cr-cs/verify.py;temporarysourceonlyscratch/networkdeny/automaticcleanup,source artifacts retained. Compare XML with compare.py against priorbaseline including16declarednewrefusals and protectedhashes. Review every newsource/test/artifact line, no production changes.
Full offline suite #2: timeout --kill-after=15s 25m .venv/bin/python -m pytest tests/characterization tests/unit tests/contract tests/integration tests/acceptance --network=deny -q --tb=line --junitxml=/tmp/b17-p2-offline.xml > /tmp/b17-p2-offline.log 2>&1. Noacceptancewhilepending.

Target78536 completed:16intendedmissingT052failures+60passes/76total,7.07s,noerrors/skips. Pending review27657 log/tmp/b17-p2-review.log deadline20m;fulloffline#2session33578 log/XML/tmp/b17-p2-offline.* deadline25m. Source/tests frozen;no fifthpart/coder. All changed test/artifact lines reviewed against source. Await completion notifications;no polling.

Review27657 exit0:115referencepasses(76new+39characterization),16independentvalidmutants detected;all relevantfailureIDs reviewed. Final source review added explicit unwanted invoice-claim and wallet-credit mutations against existing unchanged-DB assertions. Full campaign rerun pending session25597,log/tmp/b17-p2-review-final.log,20mdeadline;final tally must count unique mutations only,not duplicate rerun counts. Tests/production source unchanged;offline33578 remains valid and pending. No fifthpart;no coder/delegated tasks.

Finalreview25597exit0:115referencepasses;18NEWdistinctvalidindependentmutants detected. claim_side_effect and wallet_side_effect each fail directcompositereference unchangedDB assertion;all earlier16remain detected with matching relevant IDs. No survivor/invalid/unexecuted checks. Freshsource/state per variant,scratchcleaned. No historical/duplicate counts reused. Offline33578 pendingonly;no source/test changes or fifthpart.

Offline33578exit1:6756passed+1333exactdeclaredmissingT051–053failures/8089total,908.79s. compare.py confirms prior1317IDs/stablereasons+precisely16newmissingT052refusals/protectedhashesmatch. All588characterization+53providerfactorylegacy pass BOTH batch17 suites,noerrors/skips/regressions. Exactlytwofullsuites. Finalreview115referencepasses+18NEWvalidindependentmutants. All changed source/test/artifact lines reviewed;no pending checks,coders/delegation/survivors/invalidruns. Accepted. Batch17fourparts cp/cq+cr/cs done;166distinctnewcases(102productionpasses+64intendedmissingguards),244referenceexecutions(includes78characterization),38NEWdistinctmutants. No duplicate campaign counts reused. No productionchanges/worktrees/push/T051/fifthpart. No blockers;G-P/livegates unchanged. T050 remains unchecked. Nextct directcheck_invoice admission/status/remote verification before claim, sourceauditfirst;pair with compatible process_invoice/deliver boundedcaller controls if suitable. Sol/high;defaultGeminiFlashHigh{} available;step4 sensitiveownership unchanged. Exact remaining inventory review/T050cr-cs/remaining.md.
