# Application, payment and interface contracts

**Proposed, not present endpoints/functions.** Implementation must retain existing observable legacy contracts and add explicit composite dispatch. G-A/G-P/G-C in [research.md](../research.md) remain blocking for dependent work. This file defines inputs/results, not controller implementation.

## Application boundary

Proposed `composite/service.py` is used by Telegram handlers, owner web routes and verified method callbacks. All mutations require a server-established `Principal {identity_domain, authenticated_actor_id, tenant_installation_id, role, authenticated_interface}` and `CommandContext {request_key, observed_resource_revision?, audit_reason?}`. Caller-supplied user/tenant IDs cannot replace it. Main Telegram customer commands require acting Telegram user, ownership and applicable existing shop eligibility. A URL bearer is never a management principal.

`CommandResult {operation_id, subscription_id?, checkout_id?, state, financial_state?, availability_state?, desired_restrictions, confirmed_remote_summary, original_clock_at, target_at?, escalation_at?, qualified_usage?, retry_same_operation, public_reason, support_action}` distinguishes pending/partial/uncertain/confirmed. No raw provider payload, secret or private owner reason in general result/logs. Authorized `retrieve_url` is the only customer management result containing their usable current subscription URL, gated by publication/ownership.

| Proposed command | Inputs and authorization | Required result / invariant |
| --- | --- | --- |
| `confirm_checkout` | Customer main Telegram; selected owner plan/version, final quote confirmation key, optional one code; renewal adds owned target and current matching offer. No customer override of terms or recipient. | Atomic accepted offer, quantity1, eligible pricing/holds/wallet; existing open renewal returned without another effect. Full-wallet/zero-price authorization distinguished from invoice funding. Preview shows nodes/GiB/720h/base/discounts/invoice cost/refund destination and continuing carryover/time estimate. |
| `create_payment_attempt` | Owned retained checkout; currently permitted method/config and amount; safe G-P method contract. | Immutable native quote accepted before settlement, durable invoice creation identity; source-valid existing attempts remain valid if new creation disabled. No new attempt on known ineligible funding or duplicate unresolved create. |
| `cancel_unfunded_checkout` | Customer owner, explicit confirmation; atomic check not yet fully authorized. | Terminal quote, actual wallet release/coupon outcome, no existing-service change; valid later receipt becomes full original-value wallet credit. Race with authorization chooses one transaction order. |
| `submit_manual_receipt` | Owned attempt/order, actual message/callback sender, supported manual method; sanitized evidence/file reference. | Await owner review, never received-money state from upload alone. |
| `decide_manual_payment` | Main owner, Telegram receipt or owner web; amount/unit/reference/beneficiary/evidence/reason. | Same verification/settlement command for both interfaces; one authorized audit and original verification clock, no staff fallback, approval ≠ availability. |
| `verify_external_receipt` | Method adapter/server callback; independent verified provider receipt evidence, exact quote linkage/authentication. No user success flag. | Unique actual receipt gets original-funding/extra/terminal-late role once; mismatches held. Same transaction reference cannot settle another context. |
| `claim_test` | Actual main Telegram actor; current active plan/ordinary eligibility/campaign capacity. | Accepted sequence+ordinary/campaign holds and unchanged15min deadline, or existing pending claim/refusal with no debit/hold. Legacy/composite common eligibility. |
| `subscription_details` / `retrieve_url` | Authenticated owning main customer. | Terms/qualified usage/restrictions/checkout/operation/refund/support; current permitted URL only after full readiness+retrievability. No usable partial/replacement-unconfirmed/recovery-uncertain delivery. |
| `disable_access` / `resume_access` | Owning customer, accepted request idempotency; resume currently eligible. | Disable persists without term pause. Resume clears customer flag only; all-child work/confirmed progress. No owner/history restriction bypass. |
| `replace_leaked_access` | Owning paid/test customer, per-subscription successful24h cooldown; pending retry same operation. | Immediately old URL invalid+all-old revoke; new token withheld until old denial/new full readiness. Native-session explanation/re-import guidance. No owner approval on ordinary eligible request. |
| `confirm_permanent_cancellation` | Owning paid/test customer, explicit irreversible/no-unused-refund confirmation. | Initial-delivery block or fulfilled bounded-renewal wait as applicable; final token/revoke/refund clocks independent and persisted. No ownership reassignment/history deletion. |

No customer HTTP composite checkout/retrieval API is exposed at launch. Telegram purchase/retrieve is distinct from unauthenticated VPN-client URL refresh. Mini App, reseller tenant/supply/self-service, AI shortcuts, fixed inventory, gift/custom/add-on/automatic-renewal and legacy transfer entry points must explicitly reject composite requests before side effects. Authenticated main-store customers with reseller/discount status still qualify as ordinary buyers. Legacy supported routes/callbacks/defaults remain characterized separately.

## Telegram adapters and conversation compatibility

Add compact callbacks in a new `cmp:` namespace for catalog/confirm/pay/details/test/renew/access/leak/cancel. Use opaque local resource and confirmation nonce references fitting Telegram's callback size; do not include URL tokens/auth secrets or let a callback encode its own acting user. Exact byte grammar is frozen during implementation with characterization coverage and no collision with existing prefixes. Durable command keys derive from accepted confirmation identity; update/callback retries return operation progress. Existing `states.py` and `fsm_storage.py` keys remain readable; new states carry only draft references, not authoritative settlement/secret records.

Extend existing `btn_test`: zero active plans retains compatible legacy fallback; one eligible active plan directly selects, multiple plans show eligible options; disabled test behavior unchanged. Read `call.from_user.id`, never the bot-authored callback message actor. Both old and composite plans use shared operation-based main test reservation and preserve configured ordinary maximum. Existing supported callback/deep-link routes cannot accidentally enter a composite renewal/delete/alert/referral path.

Main bot has a proposed retrieval-readiness acknowledgement for complete candidate generation. It verifies customer-visible durable details/handler and current bot liveness, then performs the availability transaction before exposing URL. Actual availability demonstration is E-004; a stored URL/registered function alone does not suffice. Failed push is separately retryable if retrieval is genuinely functional. Authenticated customer retrieving a ready candidate can satisfy retrieval evidence without postponing term until first connection. No artificial new deadline.

Polling updates originate from authenticated Telegram transport. Affected webhook deployment requires verified expected secret/sender boundary; optional legacy `WEBHOOK_SECRET` cannot authenticate new composite callbacks by omission. Secret failures produce no trusted action. No live message is sent during planning.

## Owner web administration

Proposed `/api/composite/...` routes in existing `admin_panel/server.py`, with both `require_owner` and `require_main_tenant`, verified role/resource checks in service and existing session/security boundaries. Staff/reseller-owner read access is not implied. Cookie mutations require same-origin/CSRF validation; protected mobile authentication must map to the same main owner, or explicitly reject composite management until its parity is verified. Interface hiding is supplementary.

| Proposed route | Contract |
| --- | --- |
| `GET/POST/PATCH /api/composite/plans` | Owner catalog/test plan configuration with finite exact units, immutable versioning/prepared node binding and selected methods. Changes affect new offers only; no sold-term/node rewrite. |
| `GET /api/composite/subscriptions/{id}` | Relevant current state, child discrepancies, usage qualification, financial/coupon/test/campaign/cleanup obligations and actionable progress; secrets restricted to necessary authorized delivery/setup. No general history browser. |
| `POST /api/composite/actions/preview` then `/confirm` | Single/bulk owner suspend/resume/permanent cancel; exact subscription/customer set, action/reason/version digest and signed/session-bound preview key. Changed set requires new preview. Per-member accepted result; completed results not rolled back. |
| `POST /api/composite/replacements/preview` then `/confirm` | Owner-prepared equivalent old-to-new bindings, active/inactive eligibility, original terms/current uncertainty, emergency authorization separately explicit. Publish each subscription independently, same URL/fresh moved identities; sales/claims/unfunded checkout behavior specified. No arbitrary topology editor. |
| `POST /api/composite/subscriptions/{id}/leak-replacement` | Owner reason/audit; may bypass cooldown only, not pending operation, readiness/revocation/accounting gates. |
| `POST /api/composite/subscriptions/{id}/usage-gap-settlement` | Intact non-usage history, documented failed recovery/evidence/reason/store-risk acceptance; retain unknown gap/confirmed consumption/terms. No generic recovery resume or grant/reset. |
| `POST /api/composite/compensation/preview` then `/confirm` | Positive equal amount per unique main-store customer, subscriptions for context, count/total/prior refund/credit preview; per-customer unique effect and interrupted recovery. No access/term/test changes. |
| Existing manual approve/reject order route | Dispatch composite rows before legacy claim/fulfill. Owner+main gate and normalized manual evidence required; both Telegram/web converge on same transaction. Keep unrelated staff legacy permissions. |

Errors use existing HTTP conventions: unauthenticated401, unauthorized403, missing/unowned opaque404, invalid422, stale preview/unsafe concurrent transition409, verified temporary prerequisite failure503. A repeated accepted request returns its prior202/pending or200/complete result, not a new operation. No blanket409 busy rejection for promised protective intent: accept it and order remote convergence. Operational failures show sanitized operation/record/tenant ID, missing evidence and permitted recovery action.

## Payment adapter interface (G-P binding required)

Proposed signatures:

```text
quote_attempt(checkout, method_config_version, requested_remainder) -> AttemptQuote
create_or_reconcile_invoice(persisted_attempt_intent) -> InvoiceObservation
verify_receipt(persisted_attempt, notification_hint) -> VerifiedReceipt | EvidenceFailure
```

`AttemptQuote`: method/merchant namespace, expected native amount+currency+scale, quoted rate/rounding increment/mode, offset/required charges, complete original wallet-equivalent invoice value, validity/method conditions, evidence version. Quote acceptance precedes debit-independent external settlement; remote quote changes must be accepted by customer before payment, never silently substituted.

`VerifiedReceipt`: actual globally scoped transaction/charge reference, merchant/tenant/customer/checkout/attempt linkage, exact native amount/currency and immutable original conversion evidence, authenticated verification source/time; manual evidence additionally owner actor/reason/reference. Repeated hints are not distinct receipts. No missing/unparseable/malformed/nonfinite amount, default99% match, excess acceptance, currency mismatch or unknown beneficiary settlement. Provider-unit rounding is explicit quote equality, not a fuzzy percentage.

`EvidenceFailure`: definite rejection versus uncertain/unavailable, sanitized missing field/reason and safe requery/reference. Generic unverified webhook success cannot settle. Independent server verification can authenticate receipt even when notification is only a hint. Actually enabled methods must be inventoried and safely bound; this planning document does not declare any existing method certified or silently disabled.

## Required interface regressions

Characterize existing Telegram/menu/callback/FSM values, legacy test direct/multiple/fallback behavior, stock/custom/provider/manual/automatic renewal, receipt and web roles, tenant selectors/overlapping IDs, reseller main-buyer versus tenant, payments/rewards, and blocked-account behavior. Test owner/customer/staff forged callbacks/CSRF/signed-tenant mismatch/transaction reuse, no secret in public/private-unauthorized output/log and no unsupported direct endpoint effect. Financial and lifecycle progress statuses are distinct on both allowed payment interfaces. Full FR/SC/source mapping remains in [plan.md](../plan.md).
