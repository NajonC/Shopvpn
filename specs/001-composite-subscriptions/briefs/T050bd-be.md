# Brief T050bd–be: shared gateway custom-service renewal

- **Status**: accepted
- **Tasks**: T050bd shared renewal success/repeat; T050be shared renewal failure boundaries, combined under owner authorization. Final two normal-sized families in batch7.
- **Packet type**: test-only
- **Orchestrator**: actual/recommended gpt-6.1-sol/high; established dispatch contract with real existing engine/SQL
- **Coder**: none; default antigravity/gemini-3.8-flash-high options {}; all tests money/authority/repeat safety, orchestrator-owned per step4; no non-sensitive residual work
- **Tests written by**: orchestrator

## Goal

Reject composite orders or selected custom-service targets before the shared AbanGateway/BluPal/Noapay helpers claim or enter legacy single-panel renewal. Preserve legacy renewal success, repeated invocation and caught versus propagated failure semantics without production changes. Pair shares fixtures/reference and one final offline acceptance run.

## What already exists

abangateway_payment.py finalize_paid_order171ff, blupal_payment.py173ff, noapay_payment.py203ff: get order, pending and conditional claim, renewal engine call, caught RenewalError/unexpected failures release claim, actual SQL approval, swallowed customer/admin send errors and result. Renewal returns before purchase referral or allocation. All three functions reviewed independently. renewal_engine.py execute_renewal22ff: owner-scoped custom config, active server, real factory/update_user, preserve_remaining/reset_usage for full, readback to real local volume and SQL history. database.py create_renewal_order3362, approve3386,claim3413, get_custom_config_owned7035,apply7049. Provider factory98 uses registry. Callers handlers_user954/991/1028, handlers_admin2211/2387/2580 and extra_gateway_payment323 are separate upstream seams not closed here.

## Rules

1. “Every legacy path listed in T051–T053 rejects a composite product, order or subscription with an explicit reason before any side effect” [T050]
2. “Composite rows are routed to `composite/service.py` or refused; legacy code never claims, provisions or rewards them.” [T052]
3. “Composite records MUST NOT accidentally enter legacy single-panel renewal, connection-alert, delete, supply or grant logic.” [FR-081]
4. “Existing legacy surfaces remain compatible.” [NG-01]
5. “Composite purchases/renewals create no purchase-based referral rewards, referring-reseller commissions, deferred payout promises or first-purchase referral consumption.” [NG-05]

## Files / interfaces

Create tests/integration/test_composite_gateway_renewal_guards.py; orchestrator-owned review/T050bd-be/*.py/json/md and this brief/tasks progress. All production/prior tests/artifacts read-only. No dependency/network. finalize_paid_order(db,bot,order_id,notify_admins_fn=None) -> str, real execute_renewal, conditional SQL, real provider registry dispatch with synthetic remote constructor/update/readback and Telegram only. Row discriminator injected only at actual reads (dict/sqlite), absent and explicit legacy remain valid; unrelated composite sibling present and unchanged. No replacement/mocking of renewal function or claim success.

## Tests

162cases:48composite order/target refusal cases across3gateways/2representations/success/prior/update-failure/approval-failure, before trace/SQL and explicit secret-free composite reason. Legacy36success/repeat cases:3gateways/2representations/absent+legacy/full+volume+time. Assert exact claim/server/name/update arguments; full20GB+30days resets/preserves and reads26GB; volume5 adds to15GB; time10 adds to40days; resulting expiry2030Jan31/Jan1/Jan11, same owner/server/link, real renewal history, approved before customer send, exact recipient/result/admin identity; no reward/stock/custom purchase dispatch or first-purchase consumption/wallet debit; second call unchanged. Legacy78failure cases:3gateways/2representations/factory/update/usage PanelError, unexpected RuntimeError, local apply failure, approval failure, customer/admin send failure, absent notifier, prior, stale pending read losing actual conditional claim, foreign target, missing order. Error text exact; factory/update/readback/apply/foreign failures release pending and no later effects; approval RuntimeError propagates after actual local renewal leaving processing and retained history; send/admin failures swallowed after approval; missing/prior no effects, losing claim no renewal. Existing panel-before-local/retry limitations characterized only.

## How to check

`.venv/bin/python -m pytest tests/integration/test_composite_gateway_renewal_guards.py --network=deny -q`:114passes+48intendedmissingT052 dispatch failures; current production has no helper admission guard, even though engine guard planned T051. Existing T050a tests cover engine separately. Reference must pass all162newcases plus9callback characterization cases. Review runner uses same interpreter in scratch with expected independent mutants per helper and engine. Final offline five directories from quickstart once after final pair diff, expected4933passes+649declaredmissingT051–053failures/5582total. Compare full failure IDs/reasons with review/T050bb-bc/offline-failures.json plus48specific new guard assertions, protect previous files/hashes.

## Out of scope

Pool/config renewal aliases, ordinary catalog branches, upstream invoice/verifier/admin/extra_gateway callers, webhooks, repair of legacy failures, actual composite service route implementation/approved ordinary composite manual-payment workflows, T051+, live services, push and fifth part.

## Open points

None.

## Reviewer verification

Clean baseline e4267b3. Checklist26/26, no hooks, no unfinished prior brief. Revalidated actual three helper blocks and renewal_engine and actual DB SQL/factory instead of assuming one gateway represents another. Independently read FR005/081/082/086,SC012,NG01/02/05,T050–053 and constitution I/II/III/V/VI; tests exercise unsupported legacy single-panel dispatch, no blanket ordinary manual-payment prohibition. No evidence/product gate in this offline test-only bounded seam. No production behavior/release claim.

Source-to-case/mutation mapping: admission order+target and before effects ->48negative cases, per-helper omit order/target/both,reason,early claim,wrong target,overstrict valid legacy. Conditional claim/status/repeat ->legacy repeat/prior/lost-claim, omit status/ignore claim. Real engine dispatch/approval/identity/result/customer/admin ->legacy successes and failures, per-helper omit renewal/approval/send/admin,wrong order/recipient/result/error,propagate unexpected,omit both catch releases. Actual engine terms/full reset/readback/persistence ->full/volume/time exact positive SQL/history,mutate volume/days/name/preserve/reset/readback/local volume/local apply. Explicit legacy/absent and sibling isolation prohibit overstrict implementations. Every mutation independently starts from clean source/fresh SQL and must fail relevant assertions/raises, no errors/skips/tooling kills. Record all failing IDs and final dispositions in evidence.json. No unresolved survivors accepted.

Artifacts: snapshot.json all tracked baseline hashes, variants.py exact-match+AST edits scratch only, verify.py source-only scratch runner(import-location preflight) and evidence.json hashes/results/failing IDs/auto-cleanup; compare.py exact offline failures and protected/source hash comparison; expected_failures.json/offline-failures.json; remaining.md final scope inventory. Only synthetic source/data copied to scratch, no real config/database/secrets. Full offline source/tests stable while checks pending. Commands `.venv/bin/python specs/001-composite-subscriptions/briefs/review/T050bd-be/verify.py` and compare.py XML baseline after review. Final pair unaccepted until both checks settle.

## Delegation log

Auto approved; direct sensitive tests only, no coder. Skill routing unchanged GeminiFlashHigh{}, actual Sol/high. Targeted run14081 exit1:114pass+48intendedguardassertion failures, no collection/setup errors. Both families stay pending combined verification. After final acceptance/commit notify actual supervisor with full report and returned own thread link; stop after these four parts.

Pending review92500: timeout15m/15s -> /tmp/t050bd-be-review.log. Preflight found review-only AST parsing of indented renewal blocks and ambiguous catch replacement invalid; repaired async-block parse and unique logger catch anchor, all65independent variants now preflight exact-match+AST validated. Running review92500 loaded old tooling; not accepted as final evidence and will resume after its termination notification. Pending offline78523: timeout20m/15s -> /tmp/t050bd-be-offline.log/XML, expected4933passes+649declaredfailures. Production/tests frozen throughout; tooling repair does not require repeating offline run.

Review92500 exit1 confirmed tooling-only indentation error after initial mutants; invalid/incomplete campaign, no acceptance claim. Corrected runner now pending session63658, same15m/15s deadline, `/tmp/t050bd-be-review-r2.log`; source/tests and offline78523 unchanged. No delegate/check replacement remains active.

Review63658 exit1 after171referencepasses and17valid kills: validator rejected the deliberate propagate_unexpected mutant's expected behavior failure (synthetic RuntimeError at invocation, caught as failure not setup/error). Source shows this mutant narrows only outer engine unexpected-exception catch to KeyError, leaving synthetic provider/local apply RuntimeError unhandled. Updated validator narrowly admits exactly RuntimeError:synthetic failure in legacy_failure_boundaries unexpected/apply cases for that named mutant only. No tests changed, no missing assertion/survivor; reviewer-tool classification repair. Fresh complete campaign required; offline78523 unchanged.

Final campaign pending10214,15m+15s grace -> /tmp/t050bd-be-review-r3.log. Expected171referencepasses and65valid independent mutants. Only review artifacts changed after source/test freeze; second offline78523 remains authoritative.

Review10214 exit0:171referencepasses(162new+9callbackcharacterization),65validindependentmutants detected (19pergateway,8engine). Independently inspected each mutant/failing-test mapping; only deliberate propagation mutants use narrowly admitted expected-behavior RuntimeError, never collection/setup/error kills. No survivors/errors/skips. Scratch auto-cleaned, source/test hashes revalidated. Full offline78523 is sole pending responsibility. Earlier incomplete tooling campaigns do not contribute mutation totals.

Combined final acceptance: offline78523 exit1,4933passes+649exactdeclaredmissingT051–053failures/5582total;601priorfailure IDs/stable reasons unchanged plus48designated missingT052helperdispatchassertions, no collection/setup/errors/skips/regressions. All588characterization and53provider-factorylegacy cases pass. All protected tracked files and reviewed source/test hashes unchanged.171referencepasses,65validindependentmutations;no unresolvedsurvivors, no pendingchecks/delegates. bd/be accepted together. Batch7 four parts bb/bc+bd/be:230newcases,68newmissingguardfailures,91validindependentmutations; exactlyTWO final offline-suite runs. Earlier incomplete review-tool campaigns fixed without altering tests/production; not counted as accepted mutation evidence. No production changes/worktrees/push, no T051 or fifth part. T050 remains unchecked. Remaining scope inventory review/T050bd-be/remaining.md;nextT050bf ordinary catalog fulfillment success/repeat. Actual Sol/high; no coder because all tests sensitive and no residual code. BATCH_COMPLETE/T050_REMAINING after final commit and queued supervisor report.
