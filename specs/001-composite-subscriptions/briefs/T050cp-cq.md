# T050cp/cq — direct shared invoice admission and legacy creation controls

- **Status**: accepted
- **Tasks**: T050 remains unchecked. Pair cp selected order/product admission; cq direct creation/reuse/failure compatibility.
- **Packet type**: test-only
- **Orchestrator**: actual/recommended gpt-6.1-sol/high; established bounded admission and compatibility contracts, no new lifecycle design.
- **Coder**: none; default antigravity/gemini-3.8-flash-high{} confirmed available. All tests decide money, identity or repeat safety and are owner-written per step 4; no nonsensitive implementation remains to delegate.

## Goal
Exercise real extra_gateway_payment.create_invoice_for directly, independently of make_order_handler. Unsupported selected composite order/product aliases refuse before pending lookup or remote creation; ordinary absent/legacy markers retain creation/reuse and failure behavior.

## Rules and source review
1. “Every legacy path listed in T051–T053 rejects a composite product, order or subscription with an explicit reason before any side effect” [tasks T050].
2. “Preserve observable commands, callbacks/deep links, stored conversation state, API/configuration meanings and customer data unless an explicitly specified composite safeguard changes a directly dependent path.” [spec FR-081].
3. “Existing legacy surfaces remain compatible.” [spec NG-01].
4. “every unsupported composite channel and unauthorized cross-owner/tenant operation is rejected” [spec SC-012].
5. “Manual payment decisions are the explicit two-interface exception in FR-014.” [spec FR-005]. This extra automatic gateway boundary does not ban the approved ordinary composite manual-payment exception.
Read independently: tasks T050–053; FR005/014/081,NG01,SC012; constitution I/II/III/VI; plan source layout and quickstart offline groups. G-P/live evidence remains open; no production/live authority granted.

## Files / exact interfaces
Create tests/integration/test_composite_extra_direct_create_guards.py and review/T050cp-cq source artifacts. Change this brief and tasks.md only. All production and existing tests read-only.
Audited extra_gateway_payment.py:create_invoice_for141–211, _result214–225, stars_for_amount131–133; database.py:create_extra_invoice5408 and get_pending_extra_invoice_for_ref5446; extra_gateway_registry six gateways. Reuse test_composite_extra_order_entry_guards.setup fixture only for real DB/settings/remote fakes, never invoke its handler. Real signature create_invoice_for(db,tenant_id,tg_id,gateway,kind,ref_id,amount_toman,order_name).
Tests already owner-written and staged; no coder changes. All6 gateways × dict/sqlite × order/product × fresh/existing =48 composite cases. All6 × dict/sqlite × absent/legacy =24 direct success/reuse controls;18 failure cases disabled/remote/conversion. Nonconverting remote gateways use disabled availability for conversion control (no claim of conversion coverage there). Synthetic remote creation/exchange only; no wire/authentication claim.
Exact invoice900toman,Stars36@25,Cube990@10%;distinct invoice/order IDs;actor/reference/kind/metadata/remote ID/URL/order number/status;exact callback/IPN and remote args. Pending reuse unchanged/no second remote,no order/wallet/reward/delivery mutation. Disabled checks precede reuse. Remote/conversion errors create no invoice.

## How to check / bounds
.venv/bin/python -m pytest tests/integration/test_composite_extra_direct_create_guards.py --network=deny -q
Baseline48 intended missingT052 direct-composite failures,42passes. Expected IDs/reasons in review/T050cp-cq/expected_failures.json. Prior1269 declared IDs/reasons review/T050cn-co/offline-failures.json. All characterization and provider-factory legacy must pass.
No production changes,T051,fifthpart,worktree,push or unrelated edits. Open points: None.

## Reviewer verification
Baseline clean aa40a1700630a8ae99ec6690df3d7fecfc6cb5b9; snapshot.json protects all tracked Python source/tests. Prerequisites via bash (script lacks executable bit);checklist26/26;no hooks/AGENTS;ignore setup already accepted.
Reference variants.py adds bounded direct order/product guard before pending lookup; no other production changes. Scratch verify.py executes all90new+39approval characterization cases; all must pass. Each mutation fresh source and synthetic DB; exact replacement count/AST checked. Mutation mappings: order/product/selectedreference/selectedproduct/reason/late_guard->48composite;overstrict->valid absent/legacy;availability->disabled+existing;actor/reference/kind/amount/payable/meta/remoteid->SQLsuccess;remoteamount/label/Cubefee/Starsrate->exactremote+SQL;repeat->savedDB+single remote. Relevant assertion or DID NOT RAISE only; no syntax/setup errors count.
Reproduce .venv/bin/python specs/001-composite-subscriptions/briefs/review/T050cp-cq/verify.py. Uses temporary source-only scratch, no .git/config/data;networkdeny;automatic cleanup. Reference is review tooling only. Source artifacts retained.
Full offline command: timeout --kill-after=15s 25m .venv/bin/python -m pytest tests/characterization tests/unit tests/contract tests/integration tests/acceptance --network=deny -q --tb=line --junitxml=/tmp/b17-p1-offline.xml > /tmp/b17-p1-offline.log 2>&1. Compare IDs/stablereasons/protected hashes with compare.py XML priorbaseline. Acceptance pending all checks and every changed line review.

Pending bounded runs: mutation/reference session70132,log/tmp/b17-p1-review.log,20mdeadline;fulloffline#1session52296,log/XML/tmp/b17-p1-offline.*,25mdeadline. Source/tests frozen. No coder/delegation running; await completion notifications, do not poll.

Review70132 completed exit0:129referencepasses(90new+39characterization);20NEW independent valid mutants killed. Relevant failing IDs in evidence.json reviewed;no survivors/invalid/unexecuted campaigns. Preflight corrected nonunique remote-argument substitutions and a duplicate variant name before campaign execution;excluded preflight errors are not kills. Repeat mutant uses a distinct synthetic order number to avoid a UNIQUE collision masking the repeat assertion. Scratch auto-cleaned. Reviewed every new test/artifact line;all production/existingtests remain protected. Fulloffline52296 still pending;no acceptance yet.

Offline52296 exit1:6696passed+1317exactdeclaredmissingT051–053failures/8013total,907.92s. Prior1269IDs/stable reasons match plus precisely48newmissingT052refusals. All588characterization+53providerfactorylegacy pass;noerrors/skips/regressions. Protectedhashesmatch. Allfirstpairresponsibilities settled;accepted. Nextcr/cs direct ref_still_payable order admission + wallet/reseller/status controls,Sol/high,defaultGeminiFlashHigh{} available;all sensitive tests owner-written.
