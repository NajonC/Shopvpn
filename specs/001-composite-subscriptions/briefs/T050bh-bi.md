# Brief T050bh–bi: shared pool/config renewal aliases

- **Status**: accepted
- **Tasks**: T050bh pool/config renewal success/repeat + T050bi failure boundaries; second combined pair, final two of batch8's four parts
- **Packet type**: test-only
- **Orchestrator**: actual/recommended gpt-6.1-sol/high, established admission/legacy expiry contract
- **Coder**: none; default antigravity/gemini-3.8-flash-high options {}; all tests authority/money/repeat safety, orchestrator-owned step4, no residual code
- **Tests written by**: orchestrator

## Goal

Refuse composite order/config/product aliases before shared legacy pool renewal claims and directly before engine SQL. Preserve legacy owner-scoped local-only expiry extension, repeat/status behavior and failure boundaries. No panel is used for pool renewal. Pair shares harness/reference and one final full suite, under owner authorization.

## What already exists

Three independently reviewed finalize_paid_order(db,bot,order_id,notify_admins_fn=None)->str: abangateway_payment171ff,blupal_payment173ff,noapay_payment203ff. Conditional claim, execute_renewal, catches release, approve, swallowed customer/admin sends, early return before reward/purchase dispatch. renewal_engine.py execute_renewal22ff config branch65ff: extend_pool_config_expiry(target_id,user_id,add_days), missing->RenewalError, success fixedtext. database.py get_config_by_id3187,create_renewal_order3362,approve3386,claim3413,extend_pool_config_expiry7092: owner WHERE, future carryover else now, local expires_at update only. Engine ignores pool renewal volume/mode; characterize, do not repair. Existing T050a direct order marker coverage and bd/be custom-service targets do not establish config/product aliases.

## Rules

1. “Every legacy path listed in T051–T053 rejects a composite product, order or subscription with an explicit reason before any side effect” [T050]
2. “Composite rows are routed to `composite/service.py` or refused; legacy code never claims, provisions or rewards them.” [T052]
3. “Composite records MUST NOT accidentally enter legacy single-panel renewal, connection-alert, delete, supply or grant logic.” [FR-081]
4. “Existing legacy surfaces remain compatible.” [NG-01]
5. “Composite purchases/renewals create no purchase-based referral rewards, referring-reseller commissions, deferred payout promises or first-purchase referral consumption.” [NG-05]

## Files / interfaces

Create tests/integration/test_composite_gateway_pool_renewal_guards.py; this brief/review/T050bh-bi/*.py/json/md/tasks progress. Everything else read-only. Reuse stock catalog setup but actual renewal orders/claim/engine/SQL; marker injection at real order/config/product reads, dict/sqlite.Row. Telegram synthetic only; clock frozen database.datetime=2026Nov8 noon. Unrelated composite sibling never refused/changed. No replacement of claim/engine/SQL operations. No network/dependencies.

## Tests

192cases:54shared refusal combinations3gateways/2representations/3markers(order,config,targetproduct)/3scenarios(success,prior,approvalfailure), explicitsecretfreecomposite reason and unchanged SQL/no trace before claim.6directengine refusals3markers/2representations before actual SQL, RenewalError.72legacy success/repeat3gateways/2representations/absent+legacy/time+full+volume/future+expired: exact SQL args target/owner/10+30+0days, futureJan1->Jan11/31/1 2030; expired->Nov18/Dec8/Nov8noon2026; entire config rows unchanged except expiry, sibling unchanged, approvebefore exactcustomer/admin, wallet/referral unchanged, secondinvoke no effects.60failurecases3gateways/2representations/SQLRuntimeError,approvalRuntimeError,send,admin,noadmin,prior,lostrealclaim,foreign,missingtarget,missingorder. SQL/foreign/missing release; approval propagates after local update leavingprocessing, send/admin swallowedafterapproval, exacttraces/status/error and retainedSQL. Existing non-atomic expiry-before-approval limitation characterized only.

## How to check

`.venv/bin/python -m pytest tests/integration/test_composite_gateway_pool_renewal_guards.py --network=deny -q`:132passes+60intendedmissingguards (54T052shared,6T051engine). Expected previous697failures by full IDs/reasons in review/T050bf-bg/offline-failures.json. Reference every192new+9callback cases must pass. Independent mutants from same clean reference, fresh synthetic state, beforeacceptance; full five-directory quickstart suite once after finalpairdiff. Compare allfailure IDs/stable reasons and protected hashes; no setup/errors/skips/regressions.

## Out of scope

Ordinary direct/auto provisioning, upstream admin/extra_gateway, webhooks, Telegram renewal/payment caller UI, fixes to legacy limitations, actual composite approved manualpayment routing, T051+, live services/push/fifthpart.

## Open points

None.

## Reviewer verification

Clean baseline5bfed75. Setup gates already checked for this session:26/26checklist,nohooks, no unfinishedbrief; snapshot protects all existingfiles except authorized tasks progress. Independently re-read FR005/081/082/086,SC012,NG01/05,T050–053,constitutionI/II/III/V/VI; references remain bounded dispatch safeguards and never blanket ordinary composite manual-payment bans. All downstream realconfig SQL/getter/product aliases independently researched. No product/evidence blocker.

Mapping: T050/FR081/T052 admission order/config/product->54sharednegative+6directnegative: omit each in each helper and engine,reason,earlyclaim; NG01 absent+legacy/sibling valid->72positive(overstrict). Status/realconditionalclaim/repeat->positive/prior/lost(omitstatus/ignoreclaim). Exact engine dispatch/target/owner/days/expiry->success+foreign+missing+SQLfailure(wrongtarget/owner/days,discardcarryover,expiredwrongbase,nopersistence,removeSQLowner). Approval/send/admin/result/errors/release->success+failureexacttrace/SQL(omitapproval/send/admin/wrongrecipient/result/error/release). NG05 earlyreturn=>positive/failure no referral consumption or wallet effects. Each behavior-changing mutant must fail relevantassertion or specifiedexpectedbehaviorfailure, never setup/import/toolerror. Reference only admission checks in scratch, selected foreignconfig filtered by owner before inspecting product to preserve opacity; no cannedrenewal replacement.

Artifacts variants.py deterministicedit+ASTpreflight;verify.py imports-from-scratch/sourceonly export,freshSQL,reference/mutations;evidence.json hashes/results/IDs;snapshot.json protected hashes;compare.py offline identities/stable reasons;remaining.md exactinventory. Reproduce `.venv/bin/python specs/001-composite-subscriptions/briefs/review/T050bh-bi/verify.py`. Source/test must remain stable while background checks run.

## Delegation log

Direct sensitive tests only under step4; no coder residual, defaultGemini routing unchanged. Targeted35037 exit1:132passes+60intendedmissingguardfailures, no setup/collection errors. All checks pending before acceptance.

Pending review13946:15m+15s deadline -> /tmp/t050bh-bi-review.log. Pending offline83300:20m+15s -> /tmp/t050bh-bi-offline.log/XML; exactly second and final batch8 offline run. Production/tests frozen. Reference expects201passes,58independentmutants. Next inventory review/T050bh-bi/remaining.md, no fifth part. Own thread link for final supervisor notification: <t3-thread://v2/6702b80d-8413-4716-8002-71572e618486/mcp:launch:11970ea99ace97a8693df0622862640364afa7dc0ea067ed24e228f22ae919ef>. Notify actual supervisor only after all checks/commits settle.

Review13946 completed exit0:201referencepasses(192new+9callbackregressions);58valid independent mutations detected(16perhelper+6engine+4SQL). Independently read all failing-ID mappings: admission variants fail respective beforeclaim/directengine assertions, overstrict rejects permitted legacy, expiry/owner mutations fail exact row/error assertions. No survivors/errors/skips/tooling failures. All reviewed source/test and baseline protected hashes match; scratch auto-cleaned. Every new line reviewed, reference remains scratch-only bounded dispatch, real SQL and engine retained. Full offline83300 is sole pending responsibility; no source/test changes or extra delegate/check.

Final acceptance:offline83300 exit1,5155passes+757exactdeclaredmissingT051–053failures/5912total;697priorfailureIDs/stable assertion reasons unchanged plus60designatedmissingguards(54T052helpers+6T051engine). No errors/skips/regressions; all588characterization+53providerfactorylegacy pass in both finaloffline runs. Protected/source/test hashes unchanged,201referencepasses,58validindependentmutants,no survivors/pendingchecks/delegates. Combined bh/bi accepted. Batch8 fourparts bf/bg+bh/bi:330newcases,348referencepasses(including18callbackregressions),118validindependentmutants,108newmissingguardfailures. ExactlyTWO finaloffline runs. No production/worktree/push/T051/fifthpart. Actual/recommended Sol/high, no coder because alltests sensitive/no residualwork; defaultGeminiFlashHigh routing unchanged. BATCH_COMPLETE and T050_REMAINING after commit; T050 stays unchecked. Exactinventory review/T050bh-bi/remaining.md,nextT050bj ordinaryDIRECTsuccess/repeat,adjacentbkfailures. All responsibilities settled before finalqueuednotification to actual supervisor.
