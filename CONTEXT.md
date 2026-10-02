# Shopvpn domain language

This glossary records the vocabulary of the intended composite-subscription
feature. These definitions do not claim that the feature is currently implemented.

## Language

### Composite-subscription feature

**Store owner**:
The person who owns and operates the main store, distinct from the customer
who owns a purchased subscription.
_Avoid_: Unqualified "owner" where subscription ownership could be confused.

**Failed-provisioning refund**:
Store-wallet restoration of actual wallet funding and the entire verified original
invoice payment for an undelivered composite order, valued at its accepted original
conversion. Required quoted invoice costs are included; separate outside fees are
outside automatic coverage.
_Avoid_: Original-payment-method refund, cash repayment.

**Support compensation credit**:
A store-wallet credit explicitly approved by the store owner for a service
failure or goodwill case. It is distinct from an automatic failed-fulfillment
refund and does not itself alter the subscription's entitlement or access.
_Avoid_: Automatic prorated refund, renewal, compensation already paid when pending.

**Extra-payment credit**:
Store-wallet credit for a separately verified additional real payment received
for a checkout already funded once. It does not buy another subscription or
renewal and is separate from any refund of the original checkout payment.
_Avoid_: Repeated callback, unverified overpayment, second fulfillment.

**Composite plan**:
A store-defined offer specifying included nodes, a shared allowance, duration,
and base price, on which purchased subscriptions are based.
_Avoid_: Purchased subscription, child credential.

**Confirmed checkout quote**:
The price, discounts, allowance, duration, and intended node choices accepted at
the customer's final checkout confirmation, remaining the agreed offer until
completion, cancellation, or rejection. Live usage and remaining validity continue
to change while payment is pending.
_Avoid_: Expired payment invoice, current catalog price, frozen renewal carryover.

**Payment quote**:
The accepted terms of one payment attempt: its native payable amount/currency,
required charges, wallet-equivalent total, and original conversion/rounding terms.
It is distinct from the retained store offer and from a later payment attempt's
then-current invoice cost.
_Avoid_: Base store price alone, current exchange rate applied to an old payment.

**Invoice payment cost**:
The entire customer-payable amount required by an accepted payment quote, including
its quoted matching offset, required charges, and conversion/rounding increments.
It excludes separate bank, wallet, or network fees charged outside that invoice.
_Avoid_: Nominal undiscounted price, arbitrary mismatched overpayment, unobserved fees.

**Subscription**:
An entitlement, purchased or issued as a free test, with an owner, one allowance, one validity policy, and
one subscription URL, associated with independently managed child credentials.
_Avoid_: Calling each exported node a separate purchased subscription.

**Subscription owner**:
The authenticated customer account assigned a composite through its own purchase
or test claim, retaining management rights through renewal, conversion, and
replacement. Knowing the URL does not confer those rights.
_Avoid_: Store owner, recipient of a shared URL, original owner replaced by renewal.

**Composite test plan**:
A store-defined free test offer issued through the existing test flow, providing
one multi-node subscription with a shared allowance and validity term. Legacy
and composite tests share the customer's test eligibility.
_Avoid_: A separate free allowance per node or per test plan, paid monthly preset.

**Launch test campaign**:
The initial promotional composite test offer of 15 GiB for 15 days, limited to
150 successfully fulfilled main-store Telegram users, once per user for this
campaign. Its closure does not close the paid catalog or other test plans, and
ordinary test-usage resets leave its recipient history and cap intact.
_Avoid_: A daily quota, a permanent limit on all future tests.

**Fulfilled campaign claim**:
A promotional test grant whose complete node set is ready and whose subscription
URL is retrievable by its customer through Telegram. It permanently consumes one
campaign place; an unresolved pending claim only holds a place.
_Avoid_: Button press, partial provisioning, delivered notification alone.

**Validity start**:
The point when the complete purchased or test subscription is ready and its URL is
available for the customer to retrieve through the main-store Telegram bot.
_Avoid_: Payment time, first connection, notification-open time.

**Monthly term**:
For paid launch composite plans, exactly 30 elapsed 24-hour days, advertised as
"30 days".
_Avoid_: Calendar month, expiry rounded to local midnight.

**Full-plan renewal**:
A renewal purchase that includes both a shared allowance and a validity duration.
The term alone does not specify whether unused allowance or time carries over.
_Avoid_: Data-only add-on, time-only add-on, automatic counter reset.

**Trial-to-paid conversion**:
A composite test subscription becoming paid through a full-plan renewal into an
eligible matching preset, keeping its URL and credentials and applying the agreed
renewal carryover rules. It does not restore test eligibility or a campaign place.
_Avoid_: A new free test, implicit node migration, a separate subscription purchase.

**Carryover**:
Preservation of eligible unused allowance or remaining validity when adding a
renewal purchase to the subscription. Carried data shares the resulting common
expiry with the newly purchased allowance.
_Avoid_: Erasing usage history, assuming expired data remains eligible.

**Paid reminder period**:
The reminder context beginning with successful paid catalog fulfillment, full
renewal, or trial-to-paid conversion, using the resulting shared allowance and
common expiry. It permits one logical expiry notice and one logical quota notice.
_Avoid_: Lifetime billing history, credential generation, free test term.

**Best-effort cutoff**:
Access cutoff with tracked attempts and distinct pending/confirmed outcomes,
without a promised maximum excess consumption during control or enforcement outages.
_Avoid_: Hard quota cap, confirmed cutoff when access remains unverified.

**Customer-disabled access**:
A customer's choice to disable a subscription's access while its validity clock
continues, retained through renewal, recovery, and credential replacement.
Resumption clears that choice only; other eligibility restrictions still apply.
_Avoid_: Frozen expiry, saved validity, confirmed remote disable from a request alone.

**Permanent subscription cancellation**:
A confirmed customer or store-owner decision to end a fulfilled paid or test subscription,
invalidate its URL, and revoke its credentials, without later resumption or renewal.
Required history and unresolved remote cleanup remain recorded.
_Avoid_: Reversible disable, immediate data erasure, automatic unused-service refund.

**Owner-suspended access**:
An independent store-owner restriction on the complete subscription's access,
retaining its entitlement and identities while expiry continues. Only the store
owner can clear it; other restrictions remain independent, and its unchanged URL
displays informational entries while withholding real VPN configurations.
_Avoid_: Customer-disabled access, permanent cancellation, confirmed remote cutoff
from a request alone.

**Shop-account block**:
A restriction on the customer's shop/bot interaction under the existing account
rules. It does not itself change VPN service access or remove a separate service
restriction when lifted.
_Avoid_: Owner-suspended access, credential revocation, customer blocking Telegram.

**Recovery hold**:
A restriction on affected subscriptions or operations while their current
entitlement, ownership, financial, or lifecycle history remains unverified after
recovery. It prevents dependent effects and publication of unverified credentials
until reconciliation or a specific governed remediation, with verified cases
released separately.
_Avoid_: Owner suspension, fresh allowance from a snapshot, proof of remote cutoff.

**Overrun**:
Consumption beyond a subscription's purchased shared allowance. Confirmed
overrun is absorbed by the store under the launch policy, while actual usage
remains recorded.
_Avoid_: Customer debt, additional purchased allowance, unknown usage.

**Child credential (child client)**:
An independently managed remote authentication identity belonging to a subscription;
VLESS/VMess use UUIDs and Trojan uses a protocol password.
_Avoid_: Display name, node, inbound.

**Usage-gap settlement**:
An explicit store-owner decision to absorb unrecoverable consumption while
retaining confirmed usage and the subscription's allowance and expiry. It resolves
the commercial treatment of a gap without making the missing history known.
_Avoid_: Measured zero usage, fresh allowance, automatic outage recovery.

**Replacement cooldown**:
The 24-hour waiting period after a subscription's successful replacement before
another customer replacement of that subscription is allowed. It is independent
for each subscription; failed attempts do not start it.
_Avoid_: Calendar-day reset, account-wide limit, restriction on recovering the
same pending operation.

**Leaked-access replacement**:
Replacement of a subscription's URL and every child authentication identity,
with revocation of the old URL and credentials. The purchased entitlement and
usage history continue through the change.
_Avoid_: URL-only change, renewal, fresh allowance, proof that existing sessions
have terminated.

**Node**:
A planned real VPN choice with an intended endpoint, connection settings, and
descriptive remark, exported as one real configuration entry. It does not imply
a separate purchased allowance or distinct meter.
_Avoid_: Purchased subscription, accounting identity.

**Equivalent server replacement**:
An owner-initiated move of existing subscription service to a prepared replacement
server while preserving the subscription, shared entitlement, usage history, and
expiry. It restores the intended service rather than selling a different node set.
_Avoid_: New purchase, renewal, panel API address edit alone, leaked-access replacement.

**Subscription informational entry**:
An entry displayed in a VPN app's imported configuration list to show a message,
the subscription's expiry, or its remaining shared allowance. It is separate
from the real VPN nodes and does not grant an additional credential or allowance.
_Avoid_: Working VPN node, extra meter, live usage reading from a cached name.

**Inbound**:
The panel/Xray listener and protocol configuration that accepts clients, identified
within its particular panel/server.
_Avoid_: Using an inbound number alone as a globally unique identity.

**Outbound**:
A shared server-side egress configuration, such as a country route, that can serve
multiple child credentials and subscribers.
_Avoid_: A subscriber's individual credential, display remark.

**Meter**:
An accounting identity whose upload/download increments are attributed exactly
once, even when several attachments or views report its traffic.
_Avoid_: Node count, inbound count.
