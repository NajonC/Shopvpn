# Brief T050bl–bm: ordinary AUTO shared fulfillment

- **Status**: accepted
- **Tasks**: T050bl success/repeat + T050bm failure boundaries; batch9 second and final combined pair
- **Packet type**: test-only
- **Orchestrator**: actual/recommended gpt-6.1-sol/high; settled bounded dispatch contract
- **Coder**: none; default antigravity/gemini-3.8-flash-high{} routing unchanged
- **Tests written by**: orchestrator (money/authority/repeats); no residual coder work

## Goal

Refuse composite order/product aliases before shared ordinary AUTO effects while preserving legacy two-database credit/fixed-inventory provision, mirror persistence, delivery/rewards and repeats/failures. Adjacent success/failure family paired by explicit owner authorization; one acceptance/commit/full offline suite.

## What already exists

Three finalize_paid_order(db,bot,order_id,notify_admins_fn=None)->str helpers at abangateway_payment.py171ff,blupal_payment.py173ff,noapay_payment.py203ff dispatch AUTO when is_auto_provision and no provision_server_id. reseller_auto_provision.py34–226 provision_auto_config(local_db,product,quantity=1,user_id=None,order_id=None,source='direct_product',username_prefix='r',product_id_for_config=None): real owner lookup, main Database(MAIN_DB_PATH), reseller/supply credit checks, active panel, actual factory, create/retries/rollback, conditional consumption, mirror and local persistence. database.py consume_reseller_credit7429ff,consume_reseller_product_credit7553ff,get_or_create_mirror_panel_server6861ff,add_custom_config6987ff. Real helpers/SQL retained; external remote/Telegram synthetic only. Fixed-product sqlite.Row currently calls unsupported .get: characterize propagated AttributeError with processing claim/no credit; do not repair.

## Rules

1. “Every legacy path listed in T051–T053 rejects a composite product, order or subscription with an explicit reason before any side effect” [T050]
2. “Composite rows are routed to `composite/service.py` or refused; legacy code never claims, provisions or rewards them.” [T052]
3. “Composite records MUST NOT accidentally enter legacy single-panel renewal, connection-alert, delete, supply or grant logic.” [FR-081]
4. “Existing legacy surfaces remain compatible.” [NG-01]
5. “Composite purchases/renewals create no purchase-based referral rewards, referring-reseller commissions, deferred payout promises or first-purchase referral consumption.” [NG-05]

## Files / interfaces

Create tests/integration/test_composite_gateway_auto_guards.py,thisbrief,review/T050bl-bm artifacts; tasks.md progress only. Allproduction/existingtests read-only. Reuse DIRECT fixture setup (provider substitute and wrappedactualclaim/persistence/delivery), then configure AUTO product/noexplicitpanel and separate synthetic main.db; actualDatabase constructor/path, realSQL. Deterministic random names substitute only; two main panels force selectedremoteid2 versus mirroredlocalid3. No network/secretconfig/dependencies/live services.

## Tests

228cases:48composite3helpers×2representations×2aliases×4scenarios(success,second-unitfailure,delivery,prior) explicitsecretfreerefusal/no trace and both DBdumpsunchanged.54positive3helpers×3representation/modelcombos(dict+sqlitevolume,dictfixed)×2kind(absent/legacy)×3terms(quantity0duration0,quantity2duration17,durationNone30). Exact provider/owner/quantity10GiB/terms,remaining80of100volumeor8of10inventory,mirrorlocalID/sourcecredentials/persistedrows/history/productNULL,orderedURLs/price900/approval/referral130/firstpurchase;repeatsnoeffects acrossbothDBs.126failurecases3helpers×2supplymodels×21scenarios:owner,disabled,shortage,inactive,factory,create,second,rollback,collision,race,mirror,persist,approval,delivery,reward,send,admin,prior,lostclaim,missing,sqlitefixed. Beforeconsume inject competingSQLstate1 then real conditionalUPDATE must fail, rollback both created units and release; exacttraces/status/credit/localrows/rewards asserted. Factorypropagates,mirror/persistencefailures swallowedaftercredit;deliveryafterapproval/non-atomic limits characterizedonly.

## How to check

`.venv/bin/python -m pytest tests/integration/test_composite_gateway_auto_guards.py --network=deny -q`:180legacy passes+48intendedmissingT052guardfailures. Baseline805declaredmissingT051–053failures by IDs/stableassertionreasons review/T050bj-bk/offline-failures.json. `.venv/bin/python specs/001-composite-subscriptions/briefs/review/T050bl-bm/verify.py`:all228new+9callbackreferencepasses;69independentmutants from clean reference/freshSQL:17/helper+13AUTO+5SQL. One final offlinefive-directoryquickstartsuite;compare.py confirms exactlypriorfailures+48new,allprotected/source/testhashesmatch,noerrors/skips/regressions. Reference not production implementation.

## Out of scope

Upstream handlers/webhooks/UI and all otherremaininginventory;fixingfixedsqlitebug/legacycompensation;T051implementation;fifthpart;push/worktrees/liveproviders;blanketordinarycompositemanualpaymentbans.

## Open points

None.

## Reviewer verification

Baseline5574ae3clean; setup gates carried fromfirstpair;nohooks,26/26checklist;allpriorbriefsaccepted. IndependentFR005/081/082/086,SC012,NG01/05,T050–053,constitutionI/II/III/V/VI source review retained; no product/evidencegate. Snapshot alltracked hashes/status/diffs and source/testhashes in evidence. Real bothDBread/write/conditionalconsume/mirror/factory,nosyntheticmoneyanswers.

Mapping:T050/FR081/T052 aliasadmission->negativebeforeclaimandunchangedbothDBs(omitorder/product,reason,earlyclaim,overstrict);NG01->positiveabsent/legacy/quantityfallback/unlimited/None/nonselectedcomposite(retainedcontrols);FR082->realproviderterms/retry/rollback/mirror/persist/history/linkage(volume/duration/qty/retry/rollback/mirror/source/history/linkage);NG05->negative/noeffects and positive130reward/repeat(no/wrongreward/recipient);atomiccredit/fixedinventory/rollback->positives+controlledrace(removecondition/consume/wrongamount/log);approval/delivery/admin/status/claim/release->exacttrace/status/rewardfailures(mutantsforeacheffect). AllindependentvariantsASTandmatchcountvalidated; relevantassertionfailures only, noinvalidcounts/survivorsallowed. Scratch earlyadmission reference only, no real provisionreplacement. SQLguardslaterremainunimplemented.

Artifacts variants.py/verify.py/compare.py/snapshot.json/evidence.json/expected_failures.json/offline-failures.json/remaining.md;importsconfirmedinsource-onlymktempscratch,noconfig/DB/secretscopied,automaticcleanup. Requiredchecksrecordedbelow; noacceptanceuntilsettled.

## Delegation log

Directstep4sensitiveownership,nocoder. Initialtargetcollectionfailedbecauseresellerimportprecededsyntheticsettings;reorderedafterharnessimport. Target59030 exposedfixturelate-boundmirrorclosure:capturedoriginalmethodasdefault,keepingactualSQL;noacceptancefromsetupfailures. Correctedtarget92953 pending before finalchecks.

Correctedtarget92953 exit1:180legacy passes+48expectedmissingT052guards/228total,noerrors/skips/setupfailures. Preflight70uniquevariants(reference+69mutants),allwholemoduleAST/exactmatchcountsvalid. Source/tests staged/frozen; review96032 deadline15m+15s->/tmp/t050bl-bm-review.log; offline71655 deadline20m+15s->/tmp/t050bl-bm-offline.log/XML. Exactlysecond/finalbatch9fullsuite. Bothpending;noacceptance/commit/fifthpartuntilsettled. No runningcoders/delegates. Allsource/test/newartifactlinesreviewed;positivefixedSQLitebugcaseandmirrorsourceIDscheckedagainstactualcode. Retainowner9001/privatecustomer5101/priceterms;no sourceimplementation.

Offline71655 completed exit1:5461passes+853exactdeclaredmissingT051–053failures/6314total,in863.39s. IndependentXMLcomparison confirms805priorIDs/stableassertionreasons unchanged+48newAUTOmissingT052guardfailures;noerrors/skips/regressions,all588characterization+53providerfactorylegacypass. Exactlytwo finaloffline suites inbatch9 (first5281+805,second5461+853). Review96032 remains pending;tests/sourcefrozen,noextraoffline/delegates/fifthpart.

Review96032 exit124 at15m deadline after237referencepasses+63validindependentmutants(51helper+12AUTO); remaining6notexecuted, campaignincompleteandnotaccepted. No survivors observed, but timeoutisnotpass. Removedonlyits /tmp/T050bl-bm-6nqp9d2r source-onlyscratch aftertermination. Runnernowwritesincrementalrecordsandusespytest-xonlyformutants(firstrelevantfailedassertionissufficient);reference still runsevery237case. Freshcompletecampaign57449,25m+15sdeadline,/tmp/t050bl-bm-review-final.log,pending,all69mutantsrestartedindependentlyfromsamecleanreference. No source/testchanges,sobothfinalofflinesuitesremainvalid;noextrafullsuite. No unresolvedproductdecision/blocker,onlyverificationpending.


Final review57449 exit0:237referencepasses(228new+9callback) and69validindependentmutantsdetected(17perhelper+13actualAUTO+5actualSQL),nosurvivors/equivalents/invalid/unexecutedvariants. Allfailed-IDmappingsreviewed:aliasguardsfailbeforeclaim/reason;overstrictguard/unlimitedrejectvalidcontrols;creditamount/fixedquantity/log/mirror/history/linkage fail exactSQL/row/trace;removingrealconditionalvolume/fixedSQLfailscontrolledraceassertions. Fullreferenceeverynewcasepasses. Earlierdeadlinecampaignsupersededbythiscompletecampaign;noincompletecheckcountedaspass. Scratchauto-cleaned;exactfinalcompare.pyconfirms853declaredfailureIDs/stablereasonsandallprotected/source/testhashesmatch. Allnewsource/test/reviewerartifactlinesreviewed,nostubs/cannedanswers/xfails/skips/testloosening/productionchanges. No requiredchecks/delegatespending.

Batch9fourpartsaccepted:bj/bkDIRECT+bl/bmAUTO;402newcases,420referencepasses(including18callback),130validindependentmutants,nosurvivors;exactlytwofinaloffline suites(5281+805/6086;5461+853/6314),all588characterization+53providerfactorylegacypassboth,noerrors/skips/regressions. Bothguardfailuresetsaretest-firstmissingT052behavior,notfullypassingimplementationsuite. ExistingfixedRowbugandlegacycompensation/persistence/deliverylimitscharacterizedonly. T050unchecked;nextbnupstreamadmininvoiceapproval/statusbeforedispatch,aftercheckingpriorcb_order_approveboundedcoverage;actualextra_gateway_admin.py/extra_gateway_payment.py/extra_gateway_user.py,notextra_gateway.py. Exactinventoryreview/T050bl-bm/remaining.md. No fifthpart/T051/worktrees/push/liveevidence. BATCH_COMPLETE/T050_REMAINING aftercommitandcleanstatus. Finalqueuednotificationonlyafterallsettledtosupervisor0ccb8e07-3bec-440b-a8e8-e175fc6e10ce,ownlink <t3-thread://v2/6702b80d-8413-4716-8002-71572e618486/mcp:launch:ed62b4bc47cd803d6e7b8d42f4144c49c38164da1d25c3168f88e5ef9c76b62a>.
