# Brief T050bt-bu: upstream admin BluPal catalog status

- **Status**: accepted
- **Tasks**: T050bt ordinary catalog success/repeat + T050bu failure/alias boundaries; batch11 second/final combined packet
- **Packet type**: test-only
- **Orchestrator**: actual/recommended gpt-6.1-sol/high, established bounded contracts
- **Coder**: none; default antigravity/gemini-3.8-flash-high{} confirmed available
- **Tests written by**: orchestrator, skill step4 money/authority/repeat ownership

## Goal
Close ordinary catalog order/product aliases at cb_check_blupal_invoice before ACK or remote effects. Preserve real STOCK/DIRECT/AUTO and pool renewal dispatch beneath that upstream callback, including local allocation, provider factory, reseller credit, history, rewards, failure release and completed repeats. Owner explicitly authorizes compatible adjacent pairing, one acceptance/commit/offline suite per pair.

## What already exists
handlers_admin.py2365–2398 cb_check_blupal_invoice(call,bot); blupal_payment.py134–287 try_verify_and_finalize/finalize_paid_order(db,bot,order_id,notify_admins_fn=None). Existing gateway stock/direct/auto/pool-renewal test setups retain real production chain/SQLite. Prior bp/bq covers custom aliases only.

## Rules
1. “Every legacy path listed in T051–T053 rejects a composite product, order or subscription with an explicit reason before any side effect” [T050].
2. “Composite rows are routed to `composite/service.py` or refused; legacy code never claims, provisions or rewards them.” [T052].
3. “Composite records MUST NOT accidentally enter legacy single-panel renewal, connection-alert, delete, supply or grant logic.” [FR-081].
4. “Existing legacy surfaces remain compatible.” [NG-01].
5. “Composite purchases/renewals create no purchase-based referral rewards, referring-reseller commissions, deferred payout promises or first-purchase referral consumption.” [NG-05].

## Files / interfaces
Create tests/integration/test_composite_admin_blupal_catalog_status_guards.py, this brief and review/T050bt-bu artifacts. Update tasks.md progress only. All production/existing tests/prior evidence read-only. No delegated implementation remains since all tests decide sensitive behavior. Root checkout/current branch only; no worktree/push.

## Tests
232 cases:64 composite dict/sqlite × order/product ×4 dispatch branches × pending/expired/paid/completed require explicit sole alert, no ACK/remote/helper/SQL effects, unchanged BOTH databases. Renewal product identity resolves actual selected pool config.144 legacy absent/explicit-kind cases cover paid success/repeat, prior order, fulfillment failure, pending, expired, cancelled, remote error, completed invoice and competing real SQL claim;24 opaque role/parse/missing invoice cases. Exact selected invoice/key, verification counts/status, decoy identity, order claim, quantity2, 900 delivery, 1000 reward base/130 referrer credit, 10GB/17day persisted provision/history, reseller20GB debit, stock assignment and pool10day extension. Failure uses real stock shortage, second provider create/compensation or foreign renewal owner, then verifies release/no credit/persistence. Completed invoices intentionally fence retry even after fulfillment failure; characterize, do not fix. Unrelated composite catalog sibling must not block legacy.

## How to check
.venv/bin/python -m pytest tests/integration/test_composite_admin_blupal_catalog_status_guards.py --network=deny -q
Expected64 missing-T052 refusal failures,168 legacy passes. Reference/mutations: .venv/bin/python specs/001-composite-subscriptions/briefs/review/T050bt-bu/verify.py. Full offline five-directory suite from quickstart, --network=deny, compare.py against review/T050br-bs/offline-failures.json (949 accepted IDs/stable reasons). Expected new files and brief/artifacts only. All existing source/test hashes protected in snapshot.json.

## Out of scope
Production fixes/T051+, ordinary composite manual payment bans, manual cb_order_approve, extraGateway, other upstream callers or renewal target-marker closure beyond bounded selected product/order aliases, live providers, fifth part.

## Open points
None.

## Reviewer verification
Setup clean 00a20fe/current authorized branch. Prerequisites via bash because non-executable script; no extension hooks; requirements26/26, no active prior packet (historical template comments excluded). Read tasks header/layout, T050–053, FR005/081/082/086, SC012/NG01/05, constitution I/II/III/V/VI. Offline payment characterization does not lift G-P implementation/release gates. Authoritative source independently reviewed, bounded reference only admission; real finalization/verifier/SQL never canned.

Mapping: T050/T052 aliases -> composite64 noeffects/alert -> omit/order/product/both/wrongrefs/reason/earlyACK/earlyverify. FR005/SC012 authority -> opaque24 -> noauthority/wronginvoice. NG01 legacy -> paid/pending/cancel/failure -> overstrict/dispatch/quantity. FR082 -> actual factory/provider/provision/persistence/delivery -> wrongquantity/price/directdispatch/approval. ConstitutionII -> repeat and failure -> completedfence/verifier/complete/release/rewardbase. Prior critical downstream mutations reused only after every recorded source/test/database/factory hash matches, saved reused-evidence.json for bf-bg/bh-bi/bj-bk/bl-bm/bn-bo; not counted as new mutations. Full suite reruns all prior tests. No upstream closure inferred from shared evidence alone.

Artifacts snapshot.json, variants.py, verify.py, compare.py, reused-evidence.json, evidence.json, expected_failures.json, offline-failures.json, remaining.md. Scratch source-only exports synthetic harness, validates imports, automatically deletes. Mutants independently start from clean reference and AST/exact-match validate; relevant assertion failures required. Review every new line before acceptance. T050 remains unchecked.

Reused first-pair fixture corrections: synthetic settings before handlers, explicit catalog fixture import, actual renewal_target_id column and synthetic MAIN_DB_PATH on every branch. No new tooling/fixture failures in this pair.

## Delegation log
Direct step4 sensitive tests; no residual coder work. Next bv manual approval downstream closure after source audit, same routing/verification. No acceptance while checks pending.

BluPal verification differs: no separate verify endpoint; actual claim_blupal_invoice must conditionally claim the selected remote invoice. claim_lost calls original SQL claim twice under controlled interleaving, asserts first succeeds and second fails; callback must return completed without entering order finalizer. Independent helper-ignore-claim and real-SQL-condition-removal mutants required. All prior downstream evidence including bp-bq matches every hash. No residual coder work. No fifth part starts.

Target73470 completed exit1:168legacypasses+64 intended missingT052 admission failures/232total,27.75s,noerrors/skips. All new source/test/SQL/review artifact lines independently read, preflight31 transformations. Final tests staged/frozen; review /tmp/t050bt-review.log deadline20m+15s and second/final batch11 offline /tmp/t050bt-offline.log/XML deadline25m+15s pending. No acceptance/commit/fifth part until both settle. Corrected fixture isolation from first pair reused unchanged; no new fixture/tooling issue. Actual BluPal has no verify call; helper ignore-claim and real SQL condition mutations both target controlled claim_lost cases. No pending coder responsibilities.

Review79651 completed exit0:241referencepasses(232new+9callbacks),30valid independent mutants caught(16 callback+13 helper+1 actualSQL),nosurvivors/errors/skips/invalid/unexecutedruns. All failed-ID mappings reviewed: both ignored failed claim and removed SQL claim condition fail claim_lost STOCK exact response assertion; no upstream order claim/provision happens on competing claim in baseline. Quantity/price/reward/approval/dispatch/release failures relevant. Scratch auto-cleaned. Batch total466referencepasses/60newvalidmutants. Second/final offline87159 pending; no acceptance/fifthpart while pending; source/tests frozen.

Offline87159 completed exit1:5897pass+1013exactdeclaredmissingT051–053 failures/6910total,907.63s. compare.py confirms all949priorIDs/stable assertion reasons unchanged+64newmissingT052admissionfailures. Every protected source/test hash matches;588characterization+53providerfactorylegacy pass both batch11offline suites. Noerrors/skips/regressions; allsource/test/artifactlinesreviewed. Scratchautocleaned. Both required checks settled before acceptance; no delegated/residual work.

Batch11 fourparts accepted as exactlytwo compatiblepairs: br success/repeat+bs failure/alias AbanGateway catalog and bt success/repeat+bu failure/alias BluPal catalog.448newcases,466referencepasses,60validNEWindependentmutants/no survivors. Exactlytwooffline:5729pass+949declaredfailures/6678total and5897pass+1013declaredfailures/6910total. Test-first missingguard coverage accepted, not a whollypassingimplementation suite. T050 staysunchecked; noT051/fifthpart/productionchanges/worktrees/push. Exact remaininginventory review/T050bt-bu/remaining.md. NextT050bv manualapprovaldownstreamclosure after sourceaudit, sameSolhigh/defaultGeminiFlashHigh{} routing; all sensitive tests orchestrator-owned understep4. No blockers/pendingchecks. BATCH_COMPLETE/T050_REMAINING aftercommitandcleanstatus. Actual supervisingthread0ccb8e07-3bec-440b-a8e8-e175fc6e10ce queuednotification onlyafterfinalsettlement; ownlink <t3-thread://v2/6702b80d-8413-4716-8002-71572e618486/mcp:launch:c148db8ea45d7685b4a6e691ad8cf3b262fbcf02b22a0af28df113b28666a794>.
