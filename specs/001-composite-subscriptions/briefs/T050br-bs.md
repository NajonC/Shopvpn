# Brief T050br-bs: upstream admin AbanGateway catalog status

- **Status**: accepted
- **Tasks**: T050br ordinary catalog success/repeat + T050bs failure/alias boundaries; batch11 first combined packet
- **Packet type**: test-only
- **Orchestrator**: actual/recommended gpt-6.1-sol/high, established bounded contracts
- **Coder**: none; default antigravity/gemini-3.8-flash-high{} confirmed available
- **Tests written by**: orchestrator, skill step4 money/authority/repeat ownership

## Goal
Close ordinary catalog order/product aliases at cb_check_abangateway_invoice before ACK or remote effects. Preserve real STOCK/DIRECT/AUTO and pool renewal dispatch beneath that upstream callback, including local allocation, provider factory, reseller credit, history, rewards, failure release and completed repeats. Owner explicitly authorizes compatible adjacent pairing, one acceptance/commit/offline suite per pair.

## What already exists
handlers_admin.py2194–2226 cb_check_abangateway_invoice(call,bot); abangateway_payment.py134–287 try_verify_and_finalize/finalize_paid_order(db,bot,order_id,notify_admins_fn=None). Existing gateway stock/direct/auto/pool-renewal test setups retain real production chain/SQLite. Prior bn/bo covers custom aliases only.

## Rules
1. “Every legacy path listed in T051–T053 rejects a composite product, order or subscription with an explicit reason before any side effect” [T050].
2. “Composite rows are routed to `composite/service.py` or refused; legacy code never claims, provisions or rewards them.” [T052].
3. “Composite records MUST NOT accidentally enter legacy single-panel renewal, connection-alert, delete, supply or grant logic.” [FR-081].
4. “Existing legacy surfaces remain compatible.” [NG-01].
5. “Composite purchases/renewals create no purchase-based referral rewards, referring-reseller commissions, deferred payout promises or first-purchase referral consumption.” [NG-05].

## Files / interfaces
Create tests/integration/test_composite_admin_aban_catalog_status_guards.py, this brief and review/T050br-bs artifacts. Update tasks.md progress only. All production/existing tests/prior evidence read-only. No delegated implementation remains since all tests decide sensitive behavior. Root checkout/current branch only; no worktree/push.

## Tests
216 cases:64 composite dict/sqlite × order/product ×4 dispatch branches × pending/expired/paid/completed require explicit sole alert, no ACK/remote/helper/SQL effects, unchanged BOTH databases. Renewal product identity resolves actual selected pool config.128 legacy absent/explicit-kind cases cover paid success/repeat, prior order, fulfillment failure, pending, expired, cancelled, remote error, completed invoice;24 opaque role/parse/missing invoice cases. Exact selected invoice/key, verification counts/status, decoy identity, order claim, quantity2, 900 delivery, 1000 reward base/130 referrer credit, 10GB/17day persisted provision/history, reseller20GB debit, stock assignment and pool10day extension. Failure uses real stock shortage, second provider create/compensation or foreign renewal owner, then verifies release/no credit/persistence. Completed invoices intentionally fence retry even after fulfillment failure; characterize, do not fix. Unrelated composite catalog sibling must not block legacy.

## How to check
.venv/bin/python -m pytest tests/integration/test_composite_admin_aban_catalog_status_guards.py --network=deny -q
Expected64 missing-T052 refusal failures,152 legacy passes. Reference/mutations: .venv/bin/python specs/001-composite-subscriptions/briefs/review/T050br-bs/verify.py. Full offline five-directory suite from quickstart, --network=deny, compare.py against review/T050bp-bq/offline-failures.json (885 accepted IDs/stable reasons). Expected new files and brief/artifacts only. All existing source/test hashes protected in snapshot.json.

## Out of scope
Production fixes/T051+, ordinary composite manual payment bans, manual cb_order_approve, extraGateway, other upstream callers or renewal target-marker closure beyond bounded selected product/order aliases, live providers, fifth part.

## Open points
None.

## Reviewer verification
Setup clean b397bdae5b1ebbd9ddec9587f026948ef24852ce/current authorized branch. Prerequisites via bash because non-executable script; no extension hooks; requirements26/26, no active prior packet (historical template comments excluded). Read tasks header/layout, T050–053, FR005/081/082/086, SC012/NG01/05, constitution I/II/III/V/VI. Offline payment characterization does not lift G-P implementation/release gates. Authoritative source independently reviewed, bounded reference only admission; real finalization/verifier/SQL never canned.

Mapping: T050/T052 aliases -> composite64 noeffects/alert -> omit/order/product/both/wrongrefs/reason/earlyACK/earlyverify. FR005/SC012 authority -> opaque24 -> noauthority/wronginvoice. NG01 legacy -> paid/pending/cancel/failure -> overstrict/dispatch/quantity. FR082 -> actual factory/provider/provision/persistence/delivery -> wrongquantity/price/directdispatch/approval. ConstitutionII -> repeat and failure -> completedfence/verifier/complete/release/rewardbase. Prior critical downstream mutations reused only after every recorded source/test/database/factory hash matches, saved reused-evidence.json for bf-bg/bh-bi/bj-bk/bl-bm/bn-bo; not counted as new mutations. Full suite reruns all prior tests. No upstream closure inferred from shared evidence alone.

Artifacts snapshot.json, variants.py, verify.py, compare.py, reused-evidence.json, evidence.json, expected_failures.json, offline-failures.json, remaining.md. Scratch source-only exports synthetic harness, validates imports, automatically deletes. Mutants independently start from clean reference and AST/exact-match validate; relevant assertion failures required. Review every new line before acceptance. T050 remains unchecked.

Corrections before final checks: imported synthetic settings before handlers; imported catalog fixture explicitly; reference uses actual renewal_target_id column. Initial collection/fixture failures are tooling corrections and never counted as expected behavior or mutation kills.

## Delegation log
Direct step4 sensitive tests; no residual coder work. Next bt-bu corresponding BluPal status, same routing/verification. No acceptance while checks pending.

Production target30706 completed exit1:64 intended composite-admission failures +152 legacy passes/216total,24.91s; no errors/skips. Test file staged/frozen. Review92271 deadline20m+15s, /tmp/t050br-review.log, pending;31 AST/exact-match transformations (reference+30 independent mutants). Every new test/source/artifact line reviewed; reused helper evidence hashes all match. No offline launched yet, no acceptance/commit while pending.

Review92271: passing225-case reference,28 valid mutants caught before wrong_direct_dispatch hit lab DB isolation guard, not a valid kill. Corrected fixture to bind AUTO's MAIN_DB_PATH to synthetic main DB for every branch, so wrong routing exercises actual isolated supply refusal. No product behavior or expectation weakened. Required full reference/mutation rerun follows; initial invalid result not counted. All new lines reviewed.

Final review74744 pending: /tmp/t050br-review-final.log deadline20m+15s. First full batch11 offline suite pending: /tmp/t050br-offline.log and XML, deadline25m+15s. Source/tests frozen; no coder/second packet edits until both settle. Full source/test/reviewer artifact lines reviewed; source unchanged, T050 unchecked.

Review74744 completed exit0:225 reference passes (216 new+9 callback),30 valid independent mutants all caught, no survivors/errors/skips/invalid/unexecuted final runs. Relevant failed-ID mappings independently reviewed: wrong routing now fails paid DIRECT result assertion; release mutant fails fulfillment_failure DIRECT pending/release assertion; renewal approval/dispatch fail actual renewal cases, price/quantity/reward fail paid STOCK cases. Scratch automatically deleted. Prior invalid lab-path mutation corrected and completely rerun, not counted. Offline24008 remains pending; source/tests frozen, no acceptance or second packet edits.

Offline24008 completed exit1:5729pass+949 exact declared missingT051–053 failures/6678total,868.10s. All885 prior IDs/stable assertion reasons unchanged+64 new missingT052 admission failures. Protected source/test hashes match; all588 characterization+53 provider-factory legacy cases pass. No errors/skips/regressions/pending checks, source and all new lines reviewed. Accepted test-first work, not wholly passing implementation suite. Inventory review/T050br-bs/remaining.md. T050 unchecked; second pair bt/bu follows.
