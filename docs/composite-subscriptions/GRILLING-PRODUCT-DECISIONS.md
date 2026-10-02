# Composite subscriptions: product interview decisions

Status: product clarification complete as input to Spec Kit specify; PC-001-PC-122 accepted and RV-001 findings resolved. Technical design and evidence remain deferred; the user initiates the next step.
Started: 2026-09-25. Working repository: `/home/nojan/projects/shopvpn-develop/Shopvpn`.
Last updated: 2026-10-02.
Source inspected: `a0513d3a0e5d68351bea7c3c8ddbd007550fc27a`.

This is an input to the later Spec Kit specify step, not a competing specification,
implementation plan, or approval to build. It preserves accepted product decisions,
their reasons, and observable acceptance implications. Accepted interview answers
are recorded below; unresolved recommendations and questions remain unapproved.

## Authority and evidence

- The [constitution](../../.specify/memory/constitution.md), version 1.0.0, governs
  the feature and remains unchanged. Its `6966958` source baseline is historical.
  No constitutional exception has been requested or accepted in this interview.
- The user's 2026-09-25 interview instructions are referenced as **USER-01**.
  They preserve confirmed requirements, require one question at a time, and
  supersede historical agent handoffs, paused-work instructions, and P0-P6 packages
  with the Spec Kit workflow. They do not approve OPEN policies.
- **USER-02:** On 2026-10-02 the user requested a fresh critical review of
  Q-080-Q-109 after switching models, including whether those questions were
  appropriate, whether ambiguities were missed, and whether to close. This is
  a review request, not acceptance of Q-109 or authority to change accepted PCs.
- Read inputs: [REQUIREMENTS](REQUIREMENTS.md), [ACCEPTANCE](ACCEPTANCE.md),
  [DECISIONS](DECISIONS.md), [STATUS](STATUS.md),
  [UPSTREAM_REVIEW](UPSTREAM_REVIEW.md), and
  [INDEPENDENT_REVIEW](INDEPENDENT_REVIEW.md). These files remain unchanged.
  Their older checkout links are historical references, not this workspace.
- `/grill-with-docs` and its dependencies
  [grilling](../../.agents/skills/grilling/SKILL.md) and
  [domain-modeling](../../.agents/skills/domain-modeling/SKILL.md) are available
  and loaded. USER-01's one-question sequence overrides the grilling skill's
  multi-question rounds. Read-only source exploration supports the interview.
- A/S references below mean desired acceptance scenarios, never passing tests.
  D01-D14 are the original open decision topics; a product answer may settle only
  part of a D topic. U01-U08 are historical findings, subject to current inspection.
- Stable record IDs: **PC-xxx** accepted product inputs/answers, **Q-xxx** interview
  questions, **REC-xxx** recommendations with explicit approval status, **F-xxx** current source facts,
  **BC-xxx** user-confirmed business context, **X-xxx** public upstream source
  observations, and **E-xxx** external evidence gaps.
  **RV-xxx** records review findings and recommendations, not accepted policies.
  IDs are retained if an answer is superseded.
  Later answers must include the user's exact wording where precision matters,
  the agreed behavior, rationale, references, and observable implications.
- Each decision's "Not settled" field describes the limits of that answer alone.
  Later accepted IDs can resolve those items; the current question and unresolved
  branch map describe the current interview frontier.

## Confirmed business context

### BC-001 — Sales have not started

- **Source:** User's 2026-09-25 follow-up to Q-002: "what would be your
  recommendation if you knew the fact that i havent started to sell yet?"
- **Fact supplied:** The user has not started selling yet.
- **Clarified 2026-09-27, answer to Q-049:** "The store has not started selling
  any VPNs yet (neither legacy nor composite)." This covers both catalogs; it
  still does not establish empty persisted data or waive compatibility.
- **Implication:** Preserving an established purchasing habit is not an evidenced
  reason to recommend both sales channels. This changes REC-002's recommendation;
  it does not answer Q-002 or approve either channel.
- **Boundary:** This statement does not establish that all installations or stored
  data are empty, and does not waive PC-003 or the constitution's compatibility
  obligations. It does not establish which interface future buyers prefer.

### BC-002 — User has daily experience with the named VPN apps

- **Source:** 2026-09-28, answer to Q-069: "yes and i dont think there would be
  any blockers by these. im using them day to day."
- **Fact supplied:** The user reports daily use of the discussed apps and expects
  them to support the intended subscription experience without blockers.
- **Implication:** Record that practical experience as supporting context for
  the selected client coverage, not as a reason to manufacture a compatibility
  blocker. Later verification should focus on the actual composite fixture,
  selected versions, and informational entries.
- **Boundary:** No exact versions/configurations or controlled composite results
  were supplied. This statement does not itself waive constitution VI or prove
  every required fixture/metadata behavior. No current blocker is established
  by this statement, and no exception was requested.

### BC-003 — Frequent entry-IP filtering is a launch continuity concern

- **Source:** 2026-09-28, response to Q-074: "since iran's gfw is filtering ips
  very often we should have to be able to have some kind of workaround at least."
- **Business context:** The user expects recurring filtering of the VPN entry
  address and needs to replace that VPS without making customers lose their
  existing subscription allowance or expiry. This is user-supplied operating
  context, not an independently measured filtering frequency or a guarantee that
  any replacement address will remain reachable.

## Accepted product inputs

These inputs were already confirmed in USER-01 or REQUIREMENTS; they are preserved,
not presented as new answers or implementation evidence. Full source constraints
continue to apply even where this record summarizes them.

### PC-001 — One purchased entitlement, independent credentials

- **Accepted basis:** USER-01; R02, R03, R05, R06.
- **Behavior:** A customer purchases one subscription and receives one subscription
  URL containing an arbitrary collection of independently managed VPN credentials
  across 3x-UI panels. Several credentials may share the same panel and inbound
  while using distinct UUIDs/passwords and routing identities. The collection
  shares one purchased allowance and validity policy; child count must not
  multiply the purchased allowance.
- **Rationale:** Multiple connection choices are one purchased service.
- **Observable implications:** A02/A07/A20/A21/S04/S05 verify independent credentials,
  the complete intended node set, and one shared bucket. Quantity-to-entitlement
  purchase behavior still needs an explicit release decision; six children are
  not six purchased units.

### PC-002 — Preserve the topology example without a six-node maximum

- **Accepted basis:** USER-01; R02-R05; REQUIREMENTS required example.
- **Behavior:** Preserve the six-node acceptance fixture: A-US/A-DE/A-RU are
  separate identities in A's one REALITY inbound on public port 443, using the
  intended US/DE/RU egress; B-CDN is VLESS-WS-CDN, B-gRPC is Trojan-gRPC, and
  C-Direct is VMess-TCP-TLS. Preserve their specified distinct descriptive remarks.
  Do not introduce additional public VPN listeners on A or an L4 reverse proxy
  to deliver the feature. Six is an example, not a hardcoded maximum.
- **Rationale:** Independent identities and egress choices must fit the confirmed
  deployment constraint.
- **Observable implications:** A02/A21/S02-S04 check topology, complete protocol
  settings, actual egress, and client import/refresh. Named client targets remain
  v2rayNG, NekoBox, and Streisand; exact versions are unresolved. The nominal
  50-GB/30-day example does not settle byte units, activation, or renewal boundaries.

### PC-003 — SQLite and bounded compatibility scope

- **Accepted basis:** USER-01; R01; REQUIREMENTS correctness item 7 and scope boundaries;
  constitution I/V and Brownfield Adoption and Scope.
- **Behavior:** Retain SQLite. Preserve existing single-panel, stock-link, and
  existing-provider behavior within the affected scope. PostgreSQL migration,
  a whole-bot rewrite, and new composite panel brands beyond 3x-UI are outside
  this feature. Detailed storage design belongs to planning.
- **Rationale:** Deliver the new entitlement without replacing the database or
  silently changing existing services and unrelated payment/business policy.
- **Observable implications:** A01/A23/A33 cover affected compatibility. Existing
  legacy workflows being preserved does not make each one eligible for composites.

### PC-004 — Shared accounting and real revocation

- **Accepted basis:** USER-01; R06/R07; REQUIREMENTS correctness items 2-4;
  constitution II/VII.
- **Behavior:** Attribute each distinct underlying meter's upload plus download
  once, as already specified in REQUIREMENTS' accounting example. Do not charge
  infrastructure tunnel overhead a second time without an explicit billing
  decision; no such additional charge is approved here. Missing, invalid,
  or stale usage is not zero or verified current usage. Preserve accrued usage
  through failures and resets; unobserved consumption remains explicit uncertainty.
  Exhaustion or expiry requires disabling/deleting every associated credential.
  Hiding the subscription URL or removing a node from its payload does not revoke
  credentials already delivered. Keep cleanup responsibility until confirmed.
- **Rationale:** One allowance must remain meaningful despite independently usable
  credentials and uncertain remote outcomes.
- **Observable implications:** A07-A17/S05-S08 distinguish last confirmed usage,
  desired revocation, pending remote action, and confirmed access enforcement.
  Cutoff timing, tolerated overshoot, established-session behavior, and treatment
  of uncertain usage remain open; instantaneous distributed cutoff is not promised.

### PC-005 — Preserve sold topology and recovery responsibility

- **Accepted basis:** REQUIREMENTS correctness items 1, 5, 6, 8, 10-12;
  constitution II-IV/VII; USER-01.
- **Behavior:** Product edits must not silently change sold subscriptions without
  an explicit migration. Preserve tenant/customer ownership, intended credential
  identities, and responsibility for pending remote operations through retries,
  refunds, deletion, reset, transfer, and recovery. Eligible composite tenants
  must retain accounting and enforcement independently of optional bot/UI
  availability. Backups/recovery must include the affected subscription records
  and their relationship to panels; an old snapshot is not proof of current
  allowance or remote state. No general infrastructure-backup service is implied.
- **Rationale:** Payment, delivery, remote access, and management responsibility
  must remain distinguishable and recoverable.
- **Observable implications:** A03-A06/A19/A24/A26-A31/S10-S13 exercise these
  invariants for the approved scope. Exact migration, transfer/revoke, refund,
  retention, restore-uncertainty, and data-loss policies are still undecided.

## Accepted interview answers

### PC-006 — Initial composite sales are main-store only

- **Accepted:** 2026-09-25, answer to Q-001: "yes for now only the main store."
- **Behavior:** The initial release supports composite sales only through the
  main store. Reseller-operated stores are outside initial composite sales scope.
  This is an initial-release boundary, not a permanent ban on future reseller
  support. Existing reseller single-panel and stock-link behavior remains subject
  to PC-003's compatibility requirement.
- **Rationale discussed:** One selling business narrows ownership, charging, and
  recovery responsibilities. The trade-off is postponing reseller-store composite
  distribution. The user selected the scope without supplying additional reasons.
- **References:** D07 (partially resolved); U03/U06; A19/A23/A27/A28/A33; S12;
  constitution I/III and Brownfield Adoption and Scope.
- **Observable implications:** Approved main-store purchase paths can sell
  composites. Reseller-tenant purchase/provisioning paths must not offer or create
  composites, including requests made directly to their endpoints. Shared changes
  preserve affected existing reseller workflows and ownership isolation.
  Composite reseller staging is outside launch scope; relevant legacy regression
  and cross-tenant rejection checks still apply. These are future checks, not passes.
- **Not settled by this answer:** Telegram versus Mini App, operator interfaces,
  management actions, custom products, trials/gifts, payment methods, and buyers
  with reseller/discount/referral status in the main store. In particular, this
  does not separately approve main-store reseller-credit/inventory purchase modes.

### PC-007 — Launch customer purchases and URL retrieval through Telegram only

- **Accepted:** 2026-09-25, answer to Q-002: "yes for launch i would prefer only
  from the telegram bot."
- **Behavior:** Initial composite customer purchases and retrieval of their
  subscription URL use the main-store Telegram bot only. Composite Mini App
  checkout and customer-facing URL retrieval are deferred. This does not promise
  a date for later Mini App support or remove existing legacy Mini App behavior.
- **Rationale discussed:** With sales not yet started (BC-001), focus launch
  validation on one complete customer purchase/delivery journey and its failure
  handling. The trade-off is postponing graphical Mini App shopping. This is a
  product scope choice, not an engineering-effort estimate.
- **References:** PC-006; BC-001; D07/D10/D11; F-007; A19/A20/A23/A28;
  constitution I/III.
- **Observable implications:** An eligible customer can purchase an approved
  composite product and obtain its subscription URL through the main-store bot.
  Mini App purchase paths must not create composite orders or provision composites,
  including direct requests to those paths. A shared catalog must not accidentally
  expose an unsupported composite checkout. Affected legacy flows remain usable.
  Subscription refresh by VPN clients still uses the delivered subscription URL;
  Telegram-only shopping does not require VPN clients to authenticate to Telegram
  or make enforcement depend on Telegram availability.
- **Not settled:** Operator setup/management interfaces, customer management
  actions and their interfaces, product modes, payment methods, trials/gifts,
  and buyer eligibility within the main store. Supporting Telegram checkout does
  not automatically approve every existing bot flow for composites.

### PC-008 — Preset composite plans only at launch

- **Accepted:** 2026-09-25, answer to Q-003: "yes i agree with what youve
  recommended."
- **Behavior:** Launch customers choose from store-defined preset composite
  plans. Each plan specifies included nodes, one shared allowance, duration,
  and base price. Customers cannot build a composite by selecting their own
  nodes, allowance, or duration. The store can offer multiple presets; the
  six-node fixture is an example, not the only preset or a size limit.
- **Rationale discussed:** A clear offer and predictable fulfillment expectations
  are easier to validate before sales begin. The accepted trade-off is less
  customer customization; the store creates additional presets for different needs.
- **References:** PC-001/PC-002/PC-005; D07 (partially resolved); F-007/F-008;
  REQUIREMENTS correctness item 6; A19/A23/A24/A28; constitution I/III.
- **Observable implications:** Launch checkout presents the chosen preset's
  nodes, shared allowance, duration, and base price. Customer requests cannot
  override those plan parameters to create a custom composite. Existing custom
  single-panel flows remain subject to the compatibility boundary. Changing a
  preset must not silently alter subscriptions already sold (PC-005).
- **Not settled:** Exact units, rounding, numeric plan values, unlimited plans,
  activation/renewal semantics, quantity limits, discounts, payment methods,
  trials/gifts, customer display-name selection, or operator roles/interfaces.
  Preset-only scope is not approval of any particular plan price or quota.

### PC-009 — Owner-only composite operator actions at launch

- **Accepted:** 2026-09-25, answer to Q-004: "yes owner only."
- **Behavior:** At launch, only the main-store owner may configure composite
  plans and perform manual operator management of composite subscriptions.
  Delegated staff do not receive those composite operator powers. Existing
  staff permissions for unrelated legacy services are not removed by this choice.
- **Rationale discussed:** Keep configuration and manual recovery decisions with
  one accountable operator while establishing the service. The accepted trade-off
  is that actions requiring operator intervention wait when the owner is unavailable.
- **References:** PC-006/PC-008; D07/D14 (partially resolved); A19/A24/A28;
  constitution I/III.
- **Observable implications:** The authenticated main-store owner can perform
  the composite operator actions subsequently approved for release. Delegated
  staff, reseller owners, and ordinary customers cannot perform those operator
  actions, including by direct requests or crafted callbacks. Permissions are
  enforced beyond hidden UI controls. Automated fulfillment, accounting, and
  quota/expiry enforcement do not require the owner to remain online or approve
  every ordinary purchase as a consequence of this role restriction.
- **Not settled:** Exact manual actions, operator interface, any staff read-only
  visibility, and customer self-service actions on their own subscriptions.
  "Owner" here means the main-store owner, not the customer owning a subscription.
  Existing payment verification/manual-payment-approval rules are not changed
  by this operator-scope decision.

### PC-010 — Web admin panel for launch composite operator management

- **Accepted:** 2026-09-25, answer to Q-005: "lets go with your recommendation."
- **Behavior:** The existing web admin panel is the only launch interface for
  the main-store owner to configure composite plans and perform approved manual
  composite subscription management. Composite operator management through
  Telegram admin menus is deferred. Customer purchase and subscription-URL
  retrieval remain in the Telegram bot under PC-007.
- **Rationale discussed:** Inspect multiple panels, child credentials, and their
  individual pending/failure states together while supporting one launch operator
  interface. The accepted trade-off is needing web-admin access for these actions
  rather than handling them entirely in Telegram chat.
- **References:** PC-007-PC-009; D07/D10/D14 (partially resolved); F-008/F-011;
  A19/A23/A28; constitution I/III/VII.
- **Observable implications:** Approved composite plan and manual subscription
  operations are available to the authenticated main-store owner in web admin.
  Existing Telegram administrative handlers must not accidentally act on composites
  using single-panel assumptions. Existing legacy administration remains available
  within PC-003's compatibility scope. Interface choice does not weaken owner-only
  authorization or make automated enforcement depend on an open admin session.
- **Not settled:** Exact operator actions, owner alert channels, payment-approval
  interfaces, native-mobile-app feature support, or staff read-only visibility.
  This does not authorize manual off-catalog sales or expand customer sales channels.

### PC-011 — No partial initial delivery

- **Accepted:** 2026-09-25, answer to Q-006: "yes wait for the complete plan
  ofcourse."
- **Behavior:** All nodes required by the purchased preset must be confirmed ready
  before customer access and successful fulfillment. If any required node is not
  ready, show payment as confirmed and provisioning as pending; withhold usable
  subscription payloads and individual credentials. Do not silently omit failed
  nodes, deliver a smaller bundle, or present partial provisioning as fulfillment
  success. This applies to arbitrary preset sizes, not only the six-node fixture.
- **Rationale discussed:** Deliver the complete purchased offer. The accepted
  trade-off is that one failing node delays access to the otherwise ready nodes.
- **References:** PC-001/PC-002/PC-007/PC-008; D10 (partially resolved); R02/R05;
  A02-A06/A20/A28; S02-S04; constitution II/VII.
- **Observable implications:** For a paid six-node order with five confirmed ready
  nodes and one failed or ambiguous creation, the customer sees a pending order
  and receives no usable partial service. The owner can distinguish confirmed
  payment from incomplete provisioning. Required identities and pending work
  survive retries/restarts (PC-005); a successful payment or uncertain create
  response alone cannot establish readiness. Once the full set is ready, this
  gate permits delivery, subject to the delivery policy still to be defined.
- **Not settled:** Maximum wait, retries/recovery policy, cancellation/refund
  outcomes, validity start, delivery-notification failures, or service degradation
  after successful delivery. The readiness verification mechanism and remote
  activation sequence remain planning/controlled-validation questions.

### PC-012 — Fifteen-minute provisioning deadline, then cancel and refund

- **Later clarification:** PC-049 includes initial URL availability in this same
  deadline; complete provisioning alone is insufficient if retrieval is unavailable.
- **Accepted:** 2026-09-25, answer to Q-007: "lets go with 15 then."
  This selects the proposed 15-minute deadline and its stated cancellation/
  full-refund-initiation outcome for incomplete provisioning.
- **Behavior:** Allow up to 15 minutes from verified payment for the complete
  purchased node set to become ready. Attempt recovery during that window.
  If the complete plan is still not ready at the deadline, automatically cancel
  the unfulfilled order and initiate a full refund. Do not deliver late partial
  or complete provisioning results for that canceled order. Keep already-created
  credentials and their cleanup obligations tracked separately from the refund.
- **Rationale discussed:** Give customers a clear limit on waiting for an
  undelivered paid service. The accepted trade-off is canceling some orders that
  might succeed after a longer outage and incurring refund/cleanup work.
- **References:** PC-005/PC-011; D10 (partially resolved); A03-A06/A17/A28;
  constitution II/VII.
- **Observable implications:** A paid order still missing a required ready node
  15 minutes after verified payment cannot remain eligible for later delivery;
  it is canceled with a distinguishable refund obligation. Repeated processing
  must not duplicate refunds or recreate/deliver the canceled service. The owner
  can see unresolved cleanup even after a refund completes. Refund initiation
  must not be reported as confirmed completion before its effect is verified.
- **Evidence boundary:** Fifteen minutes is the accepted product deadline, not
  a measured processing time or a demonstrated availability guarantee. How a
  total application outage affects execution of the deadline and refund remains
  an explicit unresolved operational contract, not an assumed exception.
- **Not settled:** Refund destination and completion timing, early customer
  cancellation, detailed recovery/retry policy, payment methods, and the
  separate treatment of notification failure after complete provisioning.

### PC-013 — Failed-provisioning refunds become store-wallet credit

- **Accepted:** 2026-09-25, answer to Q-008: "no, all of it should become store
  wallet credit."
- **Behavior:** Refund the full amount paid toward a composite order canceled
  for failed provisioning as store-wallet credit, including both wallet-funded
  and externally paid portions. This failure path does not return the external
  portion through the original payment method. Credit the verified order
  customer's wallet once; payment, order, beneficiary, and amount must be verified
  under constitution II/III.
- **Rationale:** The user explicitly selected store credit instead of the
  recommended original-funding-source refunds. This keeps compensation inside
  the store; the trade-off is that externally paid funds become store credit
  rather than money returned to the customer's external payment method.
- **References:** PC-005/PC-012; D07/D10 (partially resolved); F-012;
  A03/A19/A28; constitution II/III/VII.
- **Observable implications:** For an illustrative verified order paid with
  30 wallet units plus 70 external units, failed-provisioning cancellation credits
  100 units to the customer's store wallet in total, not just the 30-unit wallet
  contribution. Repeated callbacks, retries, and restarts must not credit that
  compensation again. A refund is complete only after the wallet credit is
  confirmed; failed crediting remains a visible obligation. Remote cleanup
  remains tracked even after credit succeeds. The current wallet-only rejection
  helper (F-012) is not sufficient evidence that this behavior exists.
- **Not settled:** Wallet-credit completion deadline and total-application-outage
  behavior; payment-method eligibility; conversion/fee treatment; discount-code
  restoration; customer-facing policy disclosure; and cancellation/refunds after
  successful fulfillment. A full refund is not permission to mint the nominal
  undiscounted plan price when the verified paid amount was lower.

### PC-014 — Validity starts when the complete service is available in Telegram

- **Accepted:** 2026-09-25, answer to Q-009: "lets go with what you've recommended."
- **Behavior:** Start the purchased validity period when the complete subscription
  is ready and its subscription URL is available for the customer to retrieve
  through the main-store Telegram bot. All child credentials share the same
  expiry derived from this start. Payment or partial provisioning does not start
  the term. Opening a notification or making the first VPN connection does not
  determine the start; time runs once the complete service is available.
- **Rationale discussed:** Provisioning delay does not consume purchased days,
  and the entitlement has one clear start independent of detecting first use.
  The accepted trade-off is that unused time after availability still counts.
- **References:** PC-007/PC-011/PC-012; D03/D09/D11 (partially resolved); F-002;
  A02/A05/A12/A20; constitution II.
- **Observable implications:** Staggered creation does not give children different
  expiry times. A paid order still being provisioned has not started its purchased
  term. Once the complete service and URL are available in the bot, leaving the
  message unread or postponing first connection does not postpone expiry. Readiness
  alone, with no customer URL availability, is insufficient to start validity.
- **Not settled:** Exact day/time arithmetic, notification-delivery failure versus
  URL-availability failure, long delivery outages, renewal anchoring, expiry grace,
  and compensation for outages after activation. The 15-minute PC-012 deadline
  currently concerns incomplete provisioning; treatment of a fully provisioned
  but unavailable-to-customer service remains an explicit follow-up question.

### PC-015 — Binary GiB allowances and explicit shop labels

- **Accepted:** 2026-09-25, answer to Q-010: "yes go with binary GiB."
- **Behavior:** Express composite plan allowances in binary GiB and label them
  as GiB in the shop's customer and owner views. One GiB is exactly 1,073,741,824
  bytes; a 50 GiB preset therefore grants 53,687,091,200 bytes in one shared
  allowance for the subscription, not that amount independently per child.
- **Rationale discussed:** Retain the current provider's binary quota convention
  while making the advertised unit explicit. The trade-off is using a less
  familiar label that needs a brief explanation for customers.
- **References:** PC-001/PC-004/PC-008; D03 (partially resolved); R06; F-002;
  A07/A12; constitution II/V.
- **Observable implications:** Shop views identify the composite allowance as
  GiB; the 50 GiB example maps to the exact byte limit above. Billing thresholds
  use that byte amount without multiplying by child count. Third-party VPN
  applications may use their own display conventions; their labels do not change
  the purchased byte allowance. Unrelated legacy display behavior is not changed
  by this decision.
- **Not settled:** Actual plan values/prices, fractional allowance eligibility,
  display precision/rounding, unlimited-plan eligibility, enforcement timing and
  overshoot policy. Upload plus download counted once is an existing preserved
  input (PC-004), not a newly reopened question.

### PC-016 — Both allowance and validity are finite at launch

- **Accepted:** 2026-09-25, answer to Q-011: "yes at launch both should be finite."
- **Behavior:** Every launch composite preset has a finite shared data allowance
  and a finite validity period. Unlimited-data and no-expiry composite plans are
  outside launch scope. Legacy unlimited services are not changed by this choice.
- **Rationale discussed:** Give each purchase clear limits while establishing
  shared accounting and enforcement. The accepted trade-off is not offering
  unlimited-data or no-expiry composite products initially.
- **References:** PC-004/PC-008/PC-014/PC-015; D03 (partially resolved); R06/R07;
  A12/A23; constitution I/II.
- **Observable implications:** Composite plan setup and purchase do not permit
  an unlimited allowance or no-expiry term, including legacy sentinel values
  that mean unlimited. Each sold composite has both a finite byte allowance and
  a finite term leading to the shared expiry. Either exhaustion or expiry requires
  revocation under PC-004, with timing/outage policy still to be selected.
- **Not settled:** Actual plan sizes/prices, numeric input bounds, fractional
  values, exact day/time arithmetic, renewal, and enforcement guarantees. No
  maximum node count, quota, or duration is introduced by this scope choice.

### PC-017 — Allow a short grace period for unavailable usage

- **Accepted:** 2026-09-25, answer to Q-012: "yes allow a short grace period."
- **Behavior:** A short grace period is permitted when trustworthy usage becomes
  unavailable while VPN access may still work. This answer does not choose a
  number of minutes or a timestamp from which to measure them.
- **Rationale discussed:** Tolerate transient accounting/reporting outages before
  interrupting service. The trade-off is continued possible consumption while
  the shared total is uncertain.
- **References:** PC-004/PC-016; D02/D08 (partially resolved); A09/A13/A16;
  S05-S07; constitution II/VII.
- **Observable implications:** Temporary missing usage need not cause immediate
  suspension solely because one reading failed. Last confirmed consumption is
  retained and uncertainty remains visible; missing usage is not fresh zero.
  This grace does not waive the established exhaustion/expiry revocation
  requirement or imply confirmed cutoff of unreachable credentials.
- **Still requires explicit selection:** The exact duration and starting
  timestamp, whole-subscription versus narrower action after grace, and
  resumption conditions. Q-013 makes the proposed package concrete. Only the
  grace-period preference is recorded as unequivocally accepted by this answer.

### PC-018 — Five-minute usage grace, then whole-subscription suspension attempts

- **Accepted:** 2026-09-25, answer to the concrete Q-013 policy: "yes 5 minutes
  is ok."
- **Behavior:** Measure a five-minute grace from each required credential/meter's
  last trustworthy usage reading. If any required reading reaches five minutes
  old without a fresh trustworthy replacement, request suspension of every
  credential in the affected subscription, including those on healthy panels.
  Failed retries and process restarts do not restart the clock. Known exhaustion
  or expiry does not receive this grace. Resume only after usage is reconciled
  and the subscription remains eligible; accounting recovery cannot override an
  independent suspension/revocation.
- **Rationale discussed:** Allow brief reporting failures to recover, with a
  defined point to seek restriction. The accepted trade-off is possible continued
  consumption during grace and interruption of healthy nodes in longer outages.
- **References:** PC-004/PC-016/PC-017; D02/D08 (partially resolved);
  A09/A12/A13/A16; S05-S07; constitution II/VII.
- **Observable implications:** A required meter last read reliably at 12:00
  reaches its suspension-request threshold at 12:05 if no reliable replacement
  arrives. A failed read/restart at 12:04 does not move that to 12:09. Other
  healthy nodes are included in the suspension intent. If retained confirmed
  usage already exhausts the quota, or expiry occurs sooner, the system does
  not wait for the five-minute uncertainty window to end.
- **Capability boundary:** Five minutes is the selected grace threshold, not a
  guaranteed completed access cutoff. Unreachable credentials remain visibly
  pending and may continue to work until control returns. Suspension cannot
  be reported complete before confirmation. No hard quota-overrun bound was
  established by this answer; Q-014 addresses that separate release requirement.
- **Not settled:** Normal sampling/freshness targets, time to complete cutoff,
  total-coordinator-outage behavior, exact overrun tolerance, lost-history recovery,
  automatic versus owner-triggered resumption, and paused-time compensation.

### PC-019 — Best-effort cutoff is acceptable for launch

- **Accepted:** 2026-09-26, answer to Q-014: "no i think for launch the
  best-effort cutoff is acceptable."
- **Behavior:** Launch may use best-effort cutoff without a guaranteed maximum
  amount of excess consumption during panel-control or enforcement-service
  outages. A proven finite outage-overrun bound is not a launch requirement.
  PC-018's five-minute usage grace and whole-subscription suspension attempts
  remain required; this choice does not cancel them.
- **Rationale:** The user selected best-effort launch scope instead of making
  launch depend on proving a finite outage-overrun bound. The accepted trade-off
  is that delivered credentials may continue consuming while control is lost,
  without an agreed maximum additional amount.
- **References:** PC-004/PC-018; D02 (partially resolved); R06/R07;
  A09/A12/A13/A16/A17; S05-S07; constitution II/VI/VII.
- **Observable implications:** Outage tests record actual continued consumption
  and pending remote cutoff honestly. Unknown usage does not become zero, and
  pending action is not labeled confirmed cutoff. Reconciliation and cleanup
  obligations survive failures and recovery. Neither the customer-facing product
  nor acceptance evidence may claim a hard outage cap based on the five-minute
  rule. The allowance remains shared; this does not authorize separate purchased
  buckets per child, intentional quota multiplication, or unlimited launch plans.
- **Not settled:** Normal-operation cutoff target and measurements, established
  sessions, full enforcement-service recovery behavior, overshoot billing or
  renewal consequences, and customer-facing disclosure wording. No numeric
  overshoot tolerance or automatic overage charge is approved by this answer.

### PC-020 — Sixty-second normal-operation target for blocking new connections

- **Accepted:** 2026-09-26, answer to Q-015: "yes 60 seconds seems a reasonable
  choice."
- **Behavior:** Under supported normal operating conditions, all associated
  credentials must stop accepting new VPN connections within 60 seconds of
  crossing the purchased shared byte allowance or reaching the common expiry.
  The 60 seconds includes observation/detection and enforcement time; it does
  not begin only when the system notices the event. PC-018's five-minute usage
  grace is not added to already-known exhaustion or expiry.
- **Rationale discussed:** Establish a measurable normal-operation cutoff target
  alongside the accepted best-effort outage behavior. The accepted trade-off is
  that some additional traffic may pass during the window; a tighter target
  would require tighter operational timing.
- **References:** PC-004/PC-018/PC-019; D02 (partially resolved); A12/A13/A16;
  S05/S07; E-002; constitution VI/VII.
- **Observable implications:** Controlled checks measure from quota crossing or
  expiry to denial of new connections on every required credential, including
  credentials imported before the cutoff. An accepted disable request or hiding
  the URL is not enough to pass. The combined detection and enforcement delay
  must meet 60 seconds under the supported normal conditions and representative
  load. Results remain unverified until those checks run.
- **Boundary:** This is an accepted product target, not evidence of current
  capability, a polling interval, or permission for a separate extra allowance.
  PC-019's outage limitation still applies; no numeric byte-overrun cap is added.
- **Not settled:** Already-established connections, precise supported operating
  envelope, normal metadata freshness, and outage-recovery timing. Q-016 addresses
  the established-connection behavior separately.

### PC-021 — Leave existing-connection handling to supported panel controls

- **Accepted:** 2026-09-26, answer to Q-016: "i would go with however the 3x-ui
  panel handles the open connection itself" and "i would not like to touch the
  xray core itself and close the open connections ourselves". The user cited
  `/panel/api/clients/bulkDisable` and explicitly said they did not know its
  effect on open connections. Their suggested industry practice is not treated
  as verified evidence.
- **Behavior:** At quota exhaustion or expiry, use supported 3x-UI controls and
  accept their native handling of already-established connections. Do not modify
  Xray core or add custom direct session-termination logic for this feature.
  There is no additional requirement to terminate existing connections within
  60 seconds; REC-016's proposed requirement is rejected. PC-020's 60-second
  normal-operation target for new VPN connections remains in force, and PC-019's
  best-effort outage policy remains unchanged.
- **Rationale discussed:** Keep enforcement within the panel integration and
  avoid building and maintaining independent core/session controls. The selected
  trade-off is dependence on panel behavior: already-authenticated connections
  may continue carrying traffic beyond quota or expiry without an agreed maximum
  lifetime. Native behavior must be described honestly rather than advertised
  as immediate cessation of all traffic.
- **References:** PC-003/PC-004/PC-019/PC-020; D01/D02; R07; A12/A13/A16;
  S05-S07; X-001/X-002; E-001/E-002; constitution I/II/V/VI/VII.
- **Observable implications:** Controlled checks separately exercise fresh VPN
  authentication and pre-existing TCP, UDP, and multiplexed traffic on recorded
  panel/core/client versions. Record native termination/continuation and any
  effects on unrelated customers. Fresh-authentication checks must still meet
  PC-020; existing-session continuation alone does not fail a newly invented
  60-second termination gate. API success, a changed count, or hiding a URL
  cannot be reported as proof that all traffic has stopped. Unresolved or skipped
  credential actions remain visible and subject to reconciliation.
- **Boundary:** The cited endpoint is a capability candidate, not a selected
  detailed API design or proof it exists on deployed versions. Native restart
  behavior and its impact require investigation; this answer does not separately
  authorize adding disruptive shared-core restarts. Constitution V's provider
  boundary still applies. No constitutional exception is requested or required
  merely by accepting native existing-session behavior.
- **Not settled:** Actual deployed native behavior, the supported operating
  envelope, and any consequences requiring reconsideration after controlled
  checks. X-002 notes that a new request within an existing multiplexed tunnel
  is not necessarily a fresh VPN authentication; no application-request cutoff
  promise has been approved. Suspension, cancellation, and credential rotation
  policies remain subject to their own product decisions.

### PC-022 — Automatically recover from a usage-reporting suspension

- **Accepted:** 2026-09-26, answer to Q-017: "yes automatically should be
  recovered."
- **Behavior:** After a PC-018 stale-usage suspension, automatically restore
  access without requiring store-owner approval once all required usage is
  trustworthy and reconciled, allowance and validity remain, and no independent
  suspension, cancellation, or revocation prohibits access. Panel reachability
  alone is insufficient. Missing usage history cannot be treated as zero to
  establish eligibility. Re-enablement remains pending until confirmed; partial
  recovery must not be presented as completed recovery.
- **Rationale discussed:** Restore paid service after temporary reporting
  failures without making customers wait for the owner. The trade-off is possible
  repeated suspension and recovery while reporting is unstable; manual approval
  would add oversight but also operational work and restoration delay.
- **References:** PC-004/PC-018-PC-021; D08 (partially resolved);
  A09/A12/A13/A16; S06/S07; constitution II/VII.
- **Observable implications:** An eligible subscription suspended solely for
  stale reporting resumes without owner action after trustworthy reconciliation.
  A now-exhausted, expired, independently suspended, canceled, or revoked
  subscription does not resume through this recovery path. A responding panel
  with incomplete accounting evidence does not qualify. Failed or partial remote
  re-enablement remains distinguishable from confirmed restoration.
- **Not settled:** Recovery completion target, any stability dwell time,
  permanently lost history, time compensation, refunds for service interruptions,
  or recovery from a total coordinator outage. No worker or retry design selected.

### PC-023 — Reporting suspensions do not extend launch validity

- **Accepted:** 2026-09-26, answer to Q-018: "yes we are keeping the original
  expiry for launch".
- **Behavior:** At launch, validity keeps counting during a usage-reporting
  suspension. Keep the original common expiry; do not automatically pause the
  clock or extend the term by the suspended time. If expiry passes before
  reporting recovers, PC-022's automatic recovery must not reactivate the
  subscription merely because usage is trustworthy again.
- **Rationale discussed:** Keep the purchased term predictable without treating
  reporting/control failure as proof that all access stopped. Native existing
  connections or credentials with unconfirmed suspension may still carry traffic.
  The accepted trade-off is that a service interruption may cost the customer
  usable paid time without an automatic extension.
- **References:** PC-014/PC-018/PC-021/PC-022; D03/D08 (partially resolved);
  A12/A13/A16; S06/S07; constitution II/VII.
- **Observable implications:** A subscription expiring at 18:00 still expires
  at 18:00 after a 14:00-14:20 reporting suspension, not 18:20. Recovery at 18:05
  cannot restore that expired entitlement through the reporting-recovery path.
  Multiple reporting suspensions do not accumulate automatic validity extensions.
- **Not settled:** Discretionary owner compensation, broader outage/refund
  policies, other kinds of suspension, or paid renewal. This answer neither
  authorizes nor excludes separate compensation management flows.

### PC-024 — Customer-initiated full-plan renewal only at launch

- **Accepted:** 2026-09-26, answer to Q-019: "we go with your recommendation".
- **Behavior:** Offer customer-initiated full-plan renewal through the main-store
  Telegram bot. Renewal purchases an allowance and a duration together. Defer
  automatic renewal and standalone data-only or time-only add-ons for composite
  subscriptions at launch. Customer-initiated means the customer chooses and
  pays for renewal; it does not introduce a new store-owner approval requirement.
  Preserve affected existing single-panel and stock-link behavior under PC-003.
- **Rationale discussed:** Provide a repeat-purchase path with fewer billing
  modes to explain and verify at launch. Customers must actively renew and
  cannot purchase only additional data or days for a composite subscription.
- **References:** PC-003/PC-007/PC-008/PC-014/PC-016; D09/D10 (partially resolved);
  A15/A23/A25; F-003/F-008; constitution I/II.
- **Observable implications:** Eligible composite customers can initiate a paid
  full-plan renewal through Telegram. Composite subscriptions are not enrolled
  in or charged by automatic renewal, and composite data-only/time-only add-ons
  are unavailable. Legacy renewal modes are not removed by this scope decision.
  A25 coverage must distinguish approved composite modes from preserved legacy
  modes rather than silently enabling all modes for composites.
- **Not settled:** Eligible plans, early/late renewal, allowance carryover or
  replacement, expiry arithmetic, URL/credential continuity, payment methods,
  partial failure, or handling suspended/uncertain subscriptions. Choosing a
  full-plan purchase does not itself select replacement accounting.

### PC-025 — Renewal may select another preset with the same node configuration

- **Accepted:** 2026-09-26, answer to Q-020 and its same-configuration
  recommendation: "yes ofcourse they should be able to choose another plan
  for renewal."
- **Behavior:** Customers may renew into another offered composite preset with
  the same node configuration as their purchased subscription, including a
  different allowance or duration. Renewal is not limited to the original plan.
  Preserve the saved panels, inbounds, protocols, intended egress, and node set;
  renewal does not add, remove, or replace nodes. A different node configuration
  requires a separate subscription purchase at launch. Compare eligibility
  against the saved sold configuration, not just the original plan's current
  name or edited definition.
- **Rationale discussed:** Permit customers to change the quantity or duration
  of service without introducing node migration into renewal. The trade-off is
  that changes of locations or protocols require another subscription purchase.
- **References:** PC-005/PC-008/PC-024; D09 (partially resolved);
  A15/A24/A25; constitution I/II.
- **Observable implications:** A 50-GiB/30-day subscription can renew into an
  offered 100-GiB/30-day preset with matching nodes. A preset with a changed
  panel, inbound, protocol, route, or node set is not an eligible renewal target.
  Editing the original catalog plan must not silently migrate the sold service
  or make a mismatching configuration eligible merely by retaining its plan ID.
- **Not settled:** Carryover, timing, URL/credential continuity, prices/discounts,
  or the case where no matching preset remains offered. No matching algorithm
  or detailed schema is selected.

### PC-026 — Customers may renew early

- **Accepted:** 2026-09-26, answer to Q-021: "yes they should be able to renew
  early."
- **Behavior:** A customer may initiate full-plan renewal while the subscription
  still has both data and validity remaining. Exhaustion or expiry is not a
  prerequisite for renewal. Eligible plan choices follow PC-025. This permission
  does not override independent access restrictions or waive usage reconciliation.
- **Rationale discussed:** Let customers purchase before an interruption instead
  of waiting for depletion or expiry. The trade-off is the need for an explicit
  policy and clear checkout explanation for remaining data and time.
- **References:** PC-024/PC-025; D09 (partially resolved); A15/A25;
  constitution II.
- **Observable implications:** An otherwise eligible customer with both unused
  allowance and an unexpired term can initiate renewal; the flow does not reject
  them solely because their existing entitlement remains usable.
- **Not settled:** Carryover versus replacement, immediate versus scheduled
  application, exact expiry arithmetic, limits on successive purchases, partial
  failure, or renewal of exhausted/expired/suspended subscriptions. The user's
  explicit answer settles early eligibility; it is not approval of every late
  renewal or recovery case mentioned in REC-021.

### PC-027 — Early renewal carries forward both unused data and remaining time

- **Later qualification:** PC-032 caps total remaining validity after renewal
  at 45 days, superseding unrestricted time carryover here. Data carryover remains.
- **Accepted:** 2026-09-26, answer to Q-022: "yes it should be able to carry
  both forward".
- **Behavior:** When renewal is successfully applied before expiry with unused
  allowance and time remaining, add the purchased allowance to the reconciled
  unused allowance and extend the existing common expiry by the purchased
  duration. The additional allowance becomes usable as part of that renewal;
  do not queue a separate future plan. The combined allowance shares the extended
  expiry, without a separate earlier expiry for the carried data. This applies
  when switching to another eligible preset under PC-025 as well.
- **Accounting boundary:** Calculate and apply the addition once to the shared
  subscription, not once per child. Usage before successful application reduces
  the old remaining balance. Preserve accrued-consumption evidence; missing or
  stale readings must not inflate carryover or be treated as zero usage.
- **Rationale discussed:** Avoid forfeiting paid value because a customer renews
  early. The accepted trade-off is that the combined balance can exceed the
  selected preset's headline allowance and duration, so checkout must clearly
  explain the combined result and service details must reflect it.
- **References:** PC-004/PC-015/PC-024-PC-026; D03/D09 (partially resolved);
  A07/A10/A11/A15/A25; F-003; constitution II.
- **Observable implications:** If 20 GiB and 10 days remain at successful
  application, renewing with 50 GiB/30 days yields 70 GiB available with 40 days
  until the common expiry. The 20-GiB remainder does not expire after the first
  10 days. Retries cannot add the allowance or duration twice, and the number
  of child credentials does not multiply either addition.
- **Not settled:** Renewal after expiry or exhaustion, overrun debt, maximum
  accumulated balances or successive-purchase limits, uncertain-usage settlement,
  partial remote failure, and precise day-to-time conversion. No storage design
  or remote counter-reset mechanism is selected by this product policy.

### PC-028 — Expired unused data does not carry into late renewal

- **Later qualification:** PC-038 protects data carryover for payment verified
  before expiry when successful renewal processing crosses that expiry. Payment
  verified at or after expiry still follows the no-expired-data-carryover rule.
- **Accepted:** 2026-09-26, answer to Q-023: "yes your recommendation is perfect."
- **Behavior:** Unused data expires with the old validity term. An otherwise
  eligible retained subscription may renew after expiry, receiving only the
  newly purchased plan's allowance and its full duration from successful renewal
  application. Do not restore the expired unused balance or subtract the gap
  since expiry from the purchased duration. Keep historical usage and entitlement
  evidence even though that expired unused allowance is no longer spendable.
  Early renewal continues to carry both balances under PC-027.
- **Rationale discussed:** Give the validity deadline a clear commercial meaning
  rather than preserving expired unused data as future credit. The accepted
  trade-off is forfeiture of unused data when the customer misses that deadline;
  checkout must distinguish early carryover from renewal after expiry.
- **References:** PC-004/PC-016/PC-024-PC-027; D03/D09 (partially resolved);
  A12/A15/A25; constitution II.
- **Observable implications:** Expiry with 20 GiB unused followed two days later
  by successful 50-GiB/30-day renewal yields 50 GiB for 30 days, not 70 GiB or
  28 days. Expired data is not restored through retry or automatic reporting
  recovery. This is a paid renewal rule, not automatic post-expiry reactivation.
- **Not settled:** Renewal after quota exhaustion while time remains, overrun
  debt, recovery of deleted/canceled/revoked services, retention duration,
  payment-versus-application failures, or renewal with uncertain usage.

### PC-029 — Preserve time after quota exhaustion, subject to a 45-day limit

- **Accepted:** 2026-09-26, answer to Q-024: "yes but with maximum of 45 days
  if that makes sense."
- **Accepted portion:** Permit renewal after quota exhaustion while validity
  remains, preserving remaining time subject to a requested 45-day maximum.
  Unrestricted accumulation in REC-024 is not approved. The user supplied the
  numeric limit but did not specify whether it measures total remaining validity
  after renewal or only the old time carried forward.
- **Rationale/context:** The limit responds to Q-024's identified trade-off:
  repeated renewal by heavy data users can accumulate a long validity balance.
  The exact effect on paid time requires clarification before acceptance
  arithmetic or checkout behavior can be specified.
- **References:** PC-024-PC-028; Q-024/Q-025; D03/D09; A12/A15/A25;
  constitution II.
- **Observable implications:** Renewal after exhaustion is not categorically
  disallowed, and its eventual time rule must incorporate the agreed 45-day
  limit. Exact boundary examples cannot yet be marked agreed. Do not silently
  discard time, shorten a purchased plan, reject payment, or choose a cap
  interpretation based only on this answer.
- **Still requires explicit selection:** Meaning and measurement of the 45-day
  maximum; treatment of excess time; applicability beyond quota-exhausted renewal
  to PC-027's ordinary early renewal; plans with durations above 45 days; and
  existing balances already above the limit. Q-025 first clarifies the metric.
  Overrun debt and partial renewal failures remain separate unresolved policies.

### PC-030 — Cap total remaining validity at 45 days after exhausted renewal

- **Accepted:** 2026-09-26, answer to Q-025: "we are selling monthly plans for
  launch. yes 45 days total remaining". Monthly-plan scope is recorded in PC-031.
- **Behavior:** For the quota-exhausted renewal discussed in PC-029, the cap is
  45 days of total remaining validity immediately after successful application,
  not 45 carried days plus the new term. Preserve the full purchased duration
  and carry only the old time that fits under the total cap. Old time exceeding
  that capacity is forfeited. Show the resulting expiry and any forfeited time
  before payment; do not silently shorten the purchased duration.
- **Rationale discussed:** Directly limit accumulation from repeated renewal
  while allowing some time carryover. The accepted trade-off is forfeiture of
  part of the otherwise unexpired old term when the total reaches the cap.
- **References:** PC-029/PC-031; D03/D09; A15/A25; constitution II.
- **Observable implications:** With a 30-day purchased term, 10 old days yields
  40 days total; 20 old days yields 45 days total, retaining 15 and forfeiting
  5 old days. It must not yield 50 days or treat the cap as permission for
  45 old days plus another 30. These examples illustrate the selected cap;
  the exact meaning of a launch "month" still requires definition in PC-031.
- **Not settled:** Applying the cap to ordinary early renewal with unused data
  (PC-027), exact day/month arithmetic, unusual existing balances already above
  45 days, compensation adjustments, or overrun debt. Q-026 addresses scope.

### PC-031 — Monthly plans at launch

- **Scope clarified by PC-055/PC-056:** The monthly restriction applies to paid
  launch presets. Composite test plans are supported separately, including the
  explicitly required 15-day launch promotion. This is a product-scope refinement,
  not a constitutional exception.
- **Accepted:** 2026-09-26, additional product scope in the Q-025 answer:
  "we are selling monthly plans for launch."
- **Behavior:** Launch composite presets are monthly plans. Earlier permission
  to select another preset remains subject to this launch catalog scope and
  PC-025's matching-node requirement. It does not require offering non-monthly
  durations at launch.
- **Rationale/context:** The user supplied this scope while resolving the
  possible conflict between the 45-day total cap and longer purchased terms.
  The earlier hypothetical need to sell longer-than-45-day plans is not an
  initial-release requirement. Monthly does not, by itself, define an exact
  count of hours or calendar-month arithmetic.
- **References:** PC-008/PC-016/PC-024/PC-025/PC-030; D03/D09; A03/A15/A25.
- **Observable implications:** Initial purchase and renewal offers use the
  monthly launch catalog; differing data allowances remain permissible.
  Multi-month or other duration presets are not silently introduced based on
  the earlier broad eligibility discussion.
- **Not settled:** Whether "monthly" means exactly 30 days or a calendar month,
  the definition of a day/timezone boundary, and any future non-monthly products.

### PC-032 — The 45-day validity cap also applies to ordinary early renewal

- **Accepted:** 2026-09-26, answer to Q-026: "yes".
- **Behavior:** Apply PC-030's 45-day total-remaining-validity cap when renewing
  with unused data as well as after quota exhaustion. Retain PC-027's data
  carryover; qualify its time carryover by preserving the purchased term and
  only the old time that fits within the total cap. Forfeit excess old time and
  disclose that loss and the resulting expiry before payment. This explicitly
  supersedes PC-027 only where its full time carryover would exceed the cap.
- **Rationale discussed:** Use one validity rule whether renewal occurs just
  before or after quota exhaustion. The accepted trade-off is forfeiting excess
  old paid time even when the subscription remains active and has unused data.
- **References:** PC-027/PC-030/PC-031; D03/D09; A15/A25; constitution II.
- **Observable implications:** For a 30-day renewal, 20 GiB and 20 days remaining
  plus a 50-GiB plan yields 70 GiB and 45 days; 5 old days are forfeited and
  disclosed. With 10 old days, the result is 70 GiB and 40 days. Having a small
  positive data balance must not bypass the cap that would apply at zero data.
- **Boundary:** This is a validity cap, not a data-balance cap. It applies to
  the composite renewal transaction and does not authorize shortening unrelated
  subscriptions or background truncation outside renewal. PC-028 still governs
  the lapse of expired unused data and the new term after expiry.
- **Not settled:** Exact month/day arithmetic, exceptional old balances above
  the cap, compensation adjustments, accumulated-data limits, and concurrency
  or partial-failure outcomes beyond the established repeat-safety requirements.

### PC-033 — Monthly means exactly 30 elapsed days

- **Accepted:** 2026-09-27, answer to Q-027: "yes 30 days."
- **Behavior:** A monthly launch plan provides exactly 30 elapsed 24-hour days
  (720 hours; 2,592,000 seconds), advertised as "30 days" in purchase and renewal
  offers. The 45-day total-validity cap uses the same elapsed-time unit
  (1,080 hours; 3,888,000 seconds). Apply these durations at the already selected
  activation or renewal boundary, with one common absolute expiry for all
  credentials. Calendar-month lengths, local midnight, timezone changes, and
  daylight-saving changes do not alter the purchased duration. Do not round
  remaining carryover to whole days when determining the resulting expiry.
- **Rationale discussed:** Give every customer the same purchased duration and
  use consistent arithmetic for renewal and its cap. The accepted trade-off is
  that expiry need not fall on the same calendar date or local wall-clock time
  in the next month.
- **References:** PC-014/PC-028/PC-030-PC-032; D03/D09 (partially resolved);
  A12/A15/A25; constitution II/VII.
- **Observable implications:** A new term lasts 720 hours whether it begins in
  a short or long calendar month or crosses a daylight-saving transition. A
  remaining 10 days and 12 hours plus a 30-day renewal yields 40 days and
  12 hours, without whole-day rounding. Remaining validity after a capped
  renewal cannot exceed 1,080 hours under PC-030/PC-032. Offers say "30 days"
  rather than leaving "monthly" to imply calendar-month billing.
- **Not settled:** Display timezone and formatting precision, delayed or partial
  renewal application, or exceptional old balances. Storage representation and
  scheduling/clock coordination remain planning topics, not selected designs.

### PC-034 — The store absorbs overrun without customer debt

- **Accepted:** 2026-09-27, answer to Q-028: "yes the store must absorb it."
- **Behavior:** At launch, the store absorbs confirmed usage beyond the old
  purchased allowance before cutoff takes effect. Do not debit the customer's
  wallet, create an overrun debt, or deduct that excess from a later renewal.
  Preserve actual consumption and overrun evidence rather than rewriting usage
  to the purchased limit. Usage after the effective renewal boundary consumes
  the renewed allowance normally.
- **Rationale discussed:** Keep prepaid purchases predictable under best-effort
  cutoff and native handling of established connections. The accepted trade-off
  is additional store-funded consumption, potentially substantial during outages,
  without the hard overrun bound rejected in PC-019.
- **References:** PC-004/PC-019-PC-021/PC-027-PC-033; D02/D08/D09;
  A07/A12/A15/A16/A25; S05-S07; constitution II/VII.
- **Observable implications:** After confirmed usage of 53 GiB against an old
  50-GiB allowance, a 50-GiB renewal grants the full new 50 GiB, not 47 GiB.
  The old 53-GiB usage and 3-GiB overrun remain recorded, and no customer wallet
  deduction or receivable is created for that excess. Later receipt of evidence
  attributable to old overrun must not turn it into debt against the new purchase.
- **Boundary:** This does not create an extra promised allowance, authorize
  intentional quota multiplication, or remove cutoff and recovery obligations.
  Unknown usage remains explicit uncertainty, not verified zero or a fabricated
  overrun amount.
- **Not settled:** Attribution of readings spanning renewal, settlement when
  usage cannot be reconciled, and permanently missing history. No meter,
  counter-reset, remote quota, or worker design is selected.

### PC-035 — Reconcile uncertain usage before accepting renewal payment

- **Accepted:** 2026-09-27, answer to Q-029: "yes for launch ill go with your
  recommendation."
- **Behavior:** At launch, temporarily block renewal payment when known usage
  uncertainty prevents reliable carryover and renewal accounting. Explain in
  Telegram that renewal is temporarily unavailable while usage is reconciled.
  Do not knowingly debit the wallet or invite a new external renewal payment
  under that condition. Once the accounting prerequisite is satisfied, make
  checkout available again subject to the other eligibility rules. Missing
  usage is not zero; store absorption of confirmed overrun under PC-034 does
  not establish a reliable balance when evidence is missing.
- **Rationale discussed:** Avoid taking payment before the renewal balance can
  be established. The accepted trade-off is that a customer may reach exhaustion
  or expiry while waiting and cannot purchase a pending renewal through this
  deliberately blocked checkout.
- **References:** PC-004/PC-018/PC-027/PC-034; D08/D09/D10;
  A09/A11/A15/A25; F-003; constitution II/VII.
- **Observable implications:** An accounting outage that makes the balance
  unreliable prevents a new renewal wallet debit/payment invitation and produces
  an explanatory temporary-unavailability state. Restored trustworthy accounting
  removes this particular block without owner approval. An error-as-zero usage
  result cannot make checkout eligible or enlarge carryover.
- **Boundary:** This does not change the five-minute access grace or require
  earlier suspension of existing service. It neither selects an exact freshness
  threshold nor requires perfectly simultaneous meter readings.
- **Not settled:** Failure after payment initiation/verification, payments via
  already-issued links, partial remote renewal, permanently missing history,
  or any compensation for waiting. Existing financial obligations cannot be
  silently discarded; their recovery policy remains to be decided.

### PC-036 — Paid renewal waits for every required node

- **Accepted:** 2026-09-27, answer to Q-030: "yes we wait for every required node."
- **Behavior:** Require every credential in the purchased node set to be
  confirmed ready for the renewed entitlement before declaring renewal successful
  or making that entitlement effective. Distinguish verified payment from pending
  renewal. Updating only some credentials or receiving an unverified panel
  response is not successful renewal.
- **Pending-access policy:** The old allowance and expiry continue to govern
  access while renewal is pending, including ongoing consumption and ordinary
  cutoff. Do not deliberately suspend an otherwise usable old entitlement solely
  because renewal is pending or silently grant the new entitlement to only part
  of the node set. Existing outages, stale-usage rules, and independent access
  restrictions still apply; uninterrupted access during a panel outage is not
  promised.
- **Rationale discussed:** Preserve the complete-plan promise while protecting
  previously purchased service. The accepted trade-off is that one failed panel
  can delay renewal and the old entitlement can exhaust or expire during the wait.
- **References:** PC-011/PC-024-PC-035; D09/D10; A14/A15/A25; F-003;
  constitution II/VII.
- **Observable implications:** If only five of six example nodes are ready,
  show payment received and renewal pending, not successful renewal. An eligible
  old entitlement remains governed by its existing limits during that period;
  its ordinary expiry/exhaustion is not overridden by the pending purchase.
  Partial remote effects and accounting evidence remain visible and recoverable;
  they must not be hidden by a local success flag or assumed atomic rollback.
- **Not settled:** Maximum wait, cancellation/refund outcome, recovery of partial
  remote effects, or carryover if the old expiry passes during processing.
  Technical feasibility remains subject to controlled checks; no staging,
  rollback, storage, or worker design is selected.

### PC-037 — Incomplete renewal cancels after 15 minutes with full wallet credit

- **Accepted:** 2026-09-27, answer to Q-031: "yes."
- **Behavior:** Measure 15 minutes from verified renewal payment. If the complete
  renewal cannot be confirmed within that window, automatically cancel that
  renewal and initiate credit of its entire actual paid amount to the customer's
  store wallet, including externally funded portions, exactly once. Refund the
  paid amount, not an undiscounted nominal price. The canceled/refunded renewal
  must not later grant the purchased benefits.
- **Prior-subscription boundary:** Preserve the original subscription under its
  old allowance and expiry, accounting for actual consumption and elapsed time.
  Refunding renewal does not cancel the original purchase, authorize deletion
  of its credentials, restore spent allowance, erase consumption, or reactivate
  an entitlement that has since expired or exhausted its allowance.
- **Remote responsibility:** Reconcile partial renewal changes against the
  entitlement that should still apply. Retain remote identities, usage evidence,
  and unresolved work after wallet credit. Refund completion is distinct from
  remote reconciliation; unavailable panels need not have been instantly reverted.
- **Rationale discussed:** Give a predictable wait and the same store-wallet
  remedy as failed initial provisioning. The accepted trade-off is cancellation
  even if a panel recovers just after the deadline, with remote recovery work
  potentially continuing after refund.
- **References:** PC-012/PC-013/PC-036; D09/D10; A05/A06/A14/A15/A25;
  constitution II/IV/VII.
- **Observable implications:** A renewal paid at 12:00 that remains incomplete
  at 12:15 is canceled and has its full paid amount credited through the refund
  process once. A panel returning at 12:16 does not revive that renewal. Retried
  payment/refund processing does not duplicate credit or entitlement. Existing
  service is not deleted as if these were newly provisioned disposable credentials.
- **Not settled:** Wallet-credit completion timing, total-application-outage
  catch-up, customer cancellation before the deadline, accidental benefits
  consumed during partial application, or another renewal while reconciliation
  remains pending. No rollback algorithm or financial schema is selected.

### PC-038 — Timely verified payment protects carryover across processing delay

- **Accepted:** 2026-09-27, answer to Q-032: "yes".
- **Behavior:** If renewal payment is verified strictly before the old expiry
  and the renewal successfully completes within its 15-minute window, preserve
  eligibility to carry unused data even when completion occurs after that expiry.
  Reconcile actual usage through the effective renewal boundary: data consumed
  while waiting cannot be granted again. Confirmed old overrun remains absorbed
  by the store under PC-034 rather than reducing the newly purchased allowance.
- **Time/access boundary:** If the old term has elapsed when renewal completes,
  grant the full new 30-day duration from successful application. Protecting
  carryover does not extend the old term's access while renewal is pending or
  make a partially applied renewal effective. PC-036 still governs readiness.
- **Qualification of PC-028:** Payment verified at or after expiry receives no
  expired-data carryover. Starting checkout alone does not reserve carryover.
  A renewal canceled under PC-037 does not revive expired data or reserve it
  for another purchase; this protection applies to the timely paid renewal
  that successfully completes.
- **Rationale discussed:** Avoid loss of unused data solely due to store/panel
  processing delay after on-time payment. The accepted trade-off is distinguishing
  the payment boundary for carryover eligibility from the application boundary
  for the renewed service's effective allowance and validity.
- **References:** PC-027/PC-028/PC-034-PC-037; D03/D09/D10;
  A12/A15/A25; constitution II/VII.
- **Observable implications:** With old expiry 18:00, verified payment 17:59,
  and complete application 18:03, 20 GiB remaining after reconciliation plus
  a 50-GiB renewal gives 70 GiB and 30 days from 18:03. The old entitlement
  still expires at 18:00 while waiting. Verification at 18:00 or later does
  not qualify for this protection. A cancellation at the renewal deadline
  follows PC-037 rather than granting protected carryover later.
- **Not settled:** Usage attribution when evidence spans the renewal boundary,
  permanently missing history, and payment-verification delay before this
  qualifying boundary. Uncertainty cannot be guessed away; no attribution
  algorithm or storage design is selected.

### PC-039 — Ordinary renewal preserves the URL and all child credentials

- **Accepted:** 2026-09-27, answer to Q-033: "yes both must kept the same.
  revoking is another matter."
- **Behavior:** Ordinary successful renewal keeps the existing subscription URL
  and every child credential identity, including renewal into another eligible
  preset with the same saved node configuration. Do not require customers to
  replace their imported URL or credentials merely because they renew. Apply
  the accepted allowance/validity changes without creating additional independently
  usable identities as a renewal side effect.
- **Separate lifecycle boundary:** Revocation and credential replacement remain
  separate actions. Renewal must not undo a separately authorized revocation or
  replacement or be represented as recovery from a leaked URL/credential.
- **Rationale discussed:** Maintain customer configuration through repeat
  purchases. The accepted trade-off is that someone holding a copied URL or
  credential retains access under the renewed entitlement unless separately
  revoked or replaced. Hiding or changing a URL alone is not revocation of
  credentials already downloaded (PC-004).
- **References:** PC-001/PC-004/PC-005/PC-025/PC-036; D09/D11/D14;
  A14/A20/A21/A25; constitution I/II/III.
- **Observable implications:** Successful ordinary renewal leaves the public
  subscription URL and the identities in its node set unchanged. Previously
  imported configurations remain usable under the renewed entitlement without
  re-import solely due to renewal. Renewal retries do not mint extra credentials
  or resurrect an identity separately revoked or replaced.
- **Not settled:** Who can request/perform replacement, URL-versus-credential
  replacement scope, timing and failures of revocation/replacement, or recovery
  of deleted/externally lost identities. No token or API design is selected.

### PC-040 — Customer self-service replacement, once every 24 hours

- **Accepted:** 2026-09-27, answer to Q-034: "no the customers must be able to
  replace leaked access once every 24 hours."
- **Behavior:** Launch customers must be able to initiate replacement of their
  own leaked composite access through the Telegram bot without requiring the
  store owner to perform the action. Apply a once-every-24-hours restriction.
  REC-034's owner-managed-only recommendation is rejected.
- **Authority boundary:** Customer self-service concerns the customer's own
  subscription; it does not grant operator powers over another customer's
  service, plan configuration, or another tenant. PC-009's owner-only operator
  role and PC-010's web-admin operator interface remain intact. Ordinary renewal
  still preserves URL and credentials under PC-039; replacement is separate.
- **Rationale/trade-off:** The user chose direct customer recovery from leaked
  access instead of waiting for owner availability. The supplied 24-hour limit
  constrains repetition; its precise application needs clarification before
  boundary acceptance cases can be written.
- **References:** PC-004/PC-007/PC-009/PC-010/PC-039; D10/D11/D14;
  A14/A20/A21/A28; F-008; constitution III/VII.
- **Observable implications:** An eligible customer can invoke their own
  replacement flow through Telegram without an owner approval step. Cross-user
  or cross-tenant requests fail authority checks. An unrestricted repeat action
  is not compliant with the requested 24-hour limit. Precise cooldown tests
  depend on Q-035; no reset timestamp or account-wide scope is silently assumed.
- **Not settled:** Whether the limit is per subscription or per customer,
  its starting event, handling failed/pending replacement, first-use availability,
  owner override, URL/credential replacement scope, existing sessions, and
  partial-failure outcomes. No rate-limit or provider algorithm is selected.

### PC-041 — Per-subscription replacement cooldown starts on successful completion

- **Accepted:** 2026-09-27, answer to Q-035: "yes. i agree with you."
- **Behavior:** Apply a rolling 24-hour cooldown separately to each subscription,
  measured from its last successful replacement completion. Replacing one
  subscription does not block another belonging to the same customer. The first
  replacement requires no waiting period from purchase or delivery, subject to
  other eligibility rules. Ordinary renewal does not reset or bypass the cooldown.
- **Failures and pending work:** A failed replacement does not consume the
  allowance. While an operation is pending or its outcome uncertain, repeated
  requests refer to that same operation rather than start an independent
  replacement. Retries and recovery of that operation do not consume additional
  customer replacement allowances.
- **Rationale discussed:** Avoid penalizing technical failures or preventing
  independent recovery of another leaked subscription. The accepted trade-off
  is that a customer with several subscriptions can perform several replacements
  across their account within a day, unlike an account-wide limit.
- **References:** PC-040; D10/D11/D14; A14/A20/A21/A28;
  constitution II/III/VII.
- **Observable implications:** Successful completion at 10:00 UTC permits the
  next replacement of that subscription at 10:00 UTC the following day, not
  midnight. A request before that boundary is blocked by the cooldown. A failure
  does not start that clock; an unresolved request does not create another
  replacement. A different subscription remains independently eligible, and
  renewal of the original subscription does not clear its cooldown.
- **Not settled:** Exact replacement scope and completion criteria, operator
  overrides, eligibility while suspended/expired, partial-failure recovery, or
  separate abuse protection for repeated failed requests. No rate-limiter,
  locking, or retry algorithm is selected.

### PC-042 — Replace the URL and every child's authentication identity

- **Accepted:** 2026-09-27, answer to Q-036: "yes the subscription url must
  change and every child credential must change their uuid."
- **Behavior:** One customer leaked-access replacement changes the subscription
  URL and every child credential's authentication identity in the purchased node
  set. Invalidate the old URL and revoke the old credentials through supported
  panel controls. Do not redirect old URLs to, or expose, replacement secrets.
  Deliver the replacement URL to the authorized customer through Telegram and
  explain that their devices must import it.
- **Protocol meaning:** The user's "UUID" wording denotes replacement of every
  child's usable authentication secret: new UUIDs for VLESS/VMess and a new
  password for Trojan. Changing an unused `id` field while leaving a Trojan
  password usable would not replace that credential. This is a terminology
  clarification for the confirmed protocol mix, not approval to change protocols
  or reuse a single identity across independent children. See F-013 and the
  existing child-credential glossary definition.
- **Entitlement boundary:** Keep the same subscription, saved node configuration,
  shared allowance, expiry, and accrued usage history. Actual consumption during
  replacement still counts. Replacement does not replenish data, extend validity,
  or revive expired, exhausted, or independently suspended access.
- **Rationale discussed:** Address a leak that can expose the entire node set;
  changing only the URL does not revoke credentials already downloaded. The
  accepted trade-off is re-import on every customer device and replacement of
  all children, including any not individually known to have leaked.
- **References:** PC-004/PC-039-PC-041; D08/D11/D14;
  A10/A14/A17/A20/A21; S07; F-013; constitution II/III/VII.
- **Observable implications:** The replacement URL and each protocol's actual
  authentication identity differ from their old values. The old URL cannot
  retrieve new secrets. Previously imported old credentials must undergo real
  revocation rather than merely disappear from the new payload. Purchased
  balances and history are preserved without extra allowance or validity.
- **Not settled:** Revocation/delivery sequence, partial failures, cutoff timing,
  existing-session behavior, and complete-success criteria. This does not claim
  instantaneous active-session termination or select a replacement algorithm.

### PC-043 — Revoke leaked access before delivering complete replacements

- **Accepted:** 2026-09-27, answer to Q-037: "yes lets go with that."
- **Behavior:** Once an authorized replacement is accepted, invalidate the old
  URL and begin revoking every old credential without waiting for the new set
  to be ready. Revoke reachable nodes even if another panel is unavailable.
  Unreachable or uncertain old credentials remain visibly pending; invalidating
  the URL or receiving an accepted API request is not proof of remote cutoff.
- **Delivery and completion:** Deliver the usable new URL only after the complete
  replacement node set is ready and old credentials are confirmed revoked for
  fresh authentication. Until then, show replacement/revocation pending and do
  not start PC-041's success-based cooldown. Do not restore known leaked
  credentials solely to recover from a failed replacement.
- **Rationale discussed:** Prioritize ending leaked access over continuity during
  replacement. The accepted trade-off is interruption for the legitimate customer
  while a panel outage prevents completion. An unreachable old credential may
  still work even while old credentials on healthy panels have been revoked.
- **References:** PC-004/PC-040-PC-042; D08/D11/D14;
  A14/A17/A20/A21; S07; constitution II/III/VII.
- **Observable implications:** Replacement starts old-access revocation before
  complete new delivery is available. A six-node example with five replacements
  ready and one unresolved old credential remains pending, with no complete
  replacement URL delivered and no successful-replacement cooldown started.
  Recovery does not re-enable the known leaked set as a convenience fallback.
- **Not settled:** Numeric revocation/delivery targets, treatment of already-open
  sessions, long-running failure escalation, and interruption compensation.
  Confirmed fresh-authentication revocation is not proof that every old session
  stopped. No atomic remote transaction or detailed replacement method is selected.

### PC-044 — Replacement accepts native handling of already-open sessions

- **Accepted:** 2026-09-27, answer to Q-038: "yep."
- **Behavior:** Leaked-access replacement accepts supported 3x-UI handling of
  already-established sessions, consistently with PC-021. Complete replacement
  under PC-043's old-URL-invalid, old-fresh-authentication-revoked, and all-new-
  nodes-ready criteria, without requiring custom forced termination of every
  existing session. Do not promise that replacement immediately disconnects
  every device or stops all traffic using an already-authenticated connection;
  explain this native-session limitation to customers.
- **Rationale discussed:** Respect the chosen panel integration boundary without
  custom Xray changes or session-killing logic. The accepted trade-off is that
  a holder of leaked access may retain an already-open connection for a duration
  with no agreed or verified upper bound, even after replacement succeeds.
- **References:** PC-021/PC-042/PC-043; D02/D11/D14;
  A14/A17/A21; S07; X-001/X-002; E-001/E-002; constitution V/VI/VII.
- **Observable implications:** Controlled checks separately exercise old-credential
  fresh authentication, replacement credentials, and pre-existing ordinary and
  multiplexed sessions on recorded panel/core/client versions. Existing-session
  continuation alone does not fail an invented immediate-disconnection gate.
  UI and support wording must not equate successful replacement with proof that
  every existing connection was closed. Confirmed old-credential revocation for
  fresh authentication is still required; a successful request alone is not proof.
- **Boundary:** Actual deployed session behavior remains unverified. This does
  not authorize custom core modifications or disruptive shared restarts, and
  does not change quota/validity accounting or create fresh allowance.
- **Not settled:** Normal replacement timing, long-running failure escalation,
  and interruption compensation. No specific endpoint or termination mechanism
  is selected.

### PC-045 — Complete replacement within 60 seconds under normal conditions

- **Accepted:** 2026-09-27, answer to Q-039: "yes."
- **Behavior:** Under supported normal operating conditions, complete leaked-
  access replacement within 60 seconds of accepting the authorized customer
  request. By then, the old URL is invalid, all old credentials reject fresh
  authentication, every replacement node is ready, and the new URL is available
  for customer retrieval through Telegram. Include preparation, panel action,
  verification, and delivery availability in the interval; do not restart the
  clock on retries or begin timing only after remote work.
- **Completion boundary:** Customer reading/importing the new URL is outside
  this interval. PC-044 still permits native behavior of already-open sessions;
  the target is not a guarantee of their termination. During outages, retain
  pending status and recovery responsibility without restoring leaked access
  or claiming unverified completion.
- **Rationale discussed:** Provide a short, measurable interruption target for
  revocation-first replacement. The accepted trade-off is that all required
  panels must finish within the interval; supported versions/load must be
  validated rather than assuming current capability.
- **References:** PC-040-PC-044; D11/D14; A14/A17/A20/A21;
  S07/S09; E-001/E-002; constitution VI/VII.
- **Observable implications:** Controlled checks measure from request acceptance
  to all completion conditions under representative supported load. A new URL
  alone, partial node readiness, or an accepted revoke request does not pass.
  Retry does not create a fresh 60-second window. Actual results remain unverified
  until the required controlled checks run.
- **Boundary:** This is an accepted product target, not measured capability, a
  polling interval, or a hardcoded maximum number of nodes. Missing the target
  does not itself authorize cancellation, restoring old access, or compensation.
- **Not settled:** Long-running failure escalation, compensation, supported
  operating envelope, and outage recovery timing. No worker or provider algorithm
  is selected.

### PC-046 — Escalate incomplete replacement to the owner after 15 minutes

- **Accepted:** 2026-09-27, answer to Q-040: "yes sir."
- **Behavior:** At 15 minutes from acceptance of an authorized replacement
  request, flag an incomplete operation as needing owner attention in the web
  admin, attempt a Telegram notification to the owner, and tell the customer
  replacement remains pending and needs support attention. Keep operation status
  visible independently of notification delivery; a failed notification is not
  reported as delivered. Retries and restarts do not move the original threshold.
- **Recovery boundary:** Continue recoverable automatic reconciliation where
  possible without requiring owner approval. If automatic attempts are exhausted,
  retain unresolved obligations for manual recovery. Escalation does not cancel
  replacement, restore known leaked credentials, declare success, or start the
  successful-replacement cooldown. The normal 60-second target remains distinct;
  its miss must not be hidden until the 15-minute escalation point.
- **Authority/interface boundary:** Telegram notifications do not expand the
  operator interface; manual composite operator actions remain owner-only in
  the web admin under PC-009/PC-010.
- **Rationale discussed:** Allow transient recovery while ensuring prolonged
  customer interruption reaches the operator. The accepted trade-off is an alert
  for an outage that may resolve shortly afterward, versus delaying attention.
- **References:** PC-009/PC-010/PC-041-PC-045; D10/D11/D14;
  A14/A17/A21; S07; constitution II/VII.
- **Observable implications:** A request accepted at 12:00 and unresolved at
  12:15 is flagged for owner attention, with notification outcomes distinguished
  from the replacement outcome. A retry at 12:14 does not postpone escalation
  to 12:29. Recovery can finish afterward without a new customer replacement;
  old leaked access is not restored as a timeout fallback.
- **Not settled:** Owner response/resolution time, reminder cadence, total-app
  outage catch-up, compensation, and numeric retry budgets. This is future
  product behavior, not authorization to send notifications or create scheduled
  automations during this interview.

### PC-047 — Owner may override the replacement cooldown with an audit record

- **Accepted:** 2026-09-27, answer to Q-041: "yes."
- **Behavior:** The authenticated main-store owner may authorize an urgent
  replacement before the customer's cooldown ends through the web admin.
  Record the actor, affected subscription, reason, and outcome. Customers and
  delegated staff cannot use this override. The same full replacement scope,
  revocation priority, accounting preservation, completion checks, and normal
  timing/escalation requirements still apply.
- **Pending-operation boundary:** An override must not create a competing
  replacement while an existing one is pending or uncertain; recover that
  operation instead. Successful owner-triggered replacement starts a fresh
  24-hour customer cooldown for the subscription. A failed attempt does not.
- **Authority boundary:** This overrides only the cooldown. It does not bypass
  ownership, other eligibility, suspension, or revocation restrictions; grant
  general balance-adjustment powers; or authorize direct core commands.
- **Rationale discussed:** Provide an urgent recovery path after another leak
  within a day. The accepted trade-off is owner/support work and an exception
  to the customer limit that requires an audit trail.
- **References:** PC-009/PC-010/PC-040-PC-046; D10/D11/D14;
  A14/A20/A21/A28; constitution II/III/VII.
- **Observable implications:** The owner can initiate an otherwise eligible
  replacement during cooldown with a recorded reason. Customer or delegated-staff
  attempts cannot bypass it. A successful override restarts the customer's
  rolling 24 hours; pending/failed attempts do not produce extra operations or
  falsely start a success-based clock.
- **Not settled:** Other owner-management capabilities, support intake, and
  eligibility for inactive/revoked subscriptions. No audit-storage or override
  implementation is selected.

### PC-048 — Failed-order wallet credit is usable within 60 seconds of cancellation

- **Accepted:** 2026-09-27, answer to Q-042: "yes."
- **Behavior:** Under normal application and database conditions, complete the
  full agreed wallet credit for a canceled failed initial purchase or renewal
  within 60 seconds of cancellation. Make it visible in the wallet balance and
  refund status and spendable on another eligible purchase. Do not wait for
  remote credential cleanup or reversal of partial renewal changes. Complete
  the credit exactly once across retries, repeated callbacks, and restarts.
- **Financial boundary:** Credit the actual paid amount, including external
  funding, under PC-013/PC-037. A successful Telegram notification is not a
  prerequisite for posting the credit. An application/database outage does not
  make an unposted credit complete; retain the pending financial obligation.
- **Rationale discussed:** Make returned funds promptly usable without waiting
  for unreachable panels. The accepted trade-off is that funds can be returned
  while remote access or mutation reconciliation remains unresolved; those
  responsibilities must still be retained and pursued.
- **References:** PC-012/PC-013/PC-037; D10; A05/A06/A25;
  F-012/E-005; constitution II/VII.
- **Observable implications:** For verified payment at 12:00 and cancellation
  at the 12:15 deadline, wallet credit is usable by 12:16 under normal conditions,
  even if remote cleanup remains pending. Retrying the same refund cannot credit
  again. An attempted or queued refund is not reported as completed credit.
- **Not settled:** Catch-up timing after total application/database outage and
  escalation if credit cannot be posted. This is a product target requiring
  verification, not a selected transaction/schema or worker design.

### PC-049 — Initial fulfillment deadline includes usable URL availability

- **Accepted:** 2026-09-27, answer to Q-043: "yes".
- **Behavior:** The initial 15-minute deadline from verified payment requires
  both readiness of every required node and availability of a usable subscription
  URL for the authorized customer to retrieve through Telegram. If the combined
  condition is unmet at the deadline, cancel the initial order, apply the full
  wallet-credit policy in PC-013/PC-048, and retain cleanup obligations even if
  every credential has already been created. Do not add a second delivery window
  after provisioning or deliver a canceled order late.
- **Notification distinction:** A failed automatic notification alone does not
  invalidate fulfillment if the usable URL is retrievable through the bot's
  subscription-management flow. Actual customer reading, requesting the URL,
  or connecting is not required. A URL stored only internally while customer
  retrieval is unavailable does not establish delivery availability. Retry
  notification without duplicating financial or provisioning effects.
- **Rationale discussed:** Align the waiting limit with the availability-based
  validity start and the customer's ability to obtain the purchase. The accepted
  trade-off is cancellation and cleanup of a fully provisioned order when
  delivery remains unavailable.
- **References:** PC-007/PC-011-PC-014/PC-048; D10/D11;
  A03-A06/A20/A28; constitution II/VII.
- **Observable implications:** Complete panel provisioning at 12:10 after
  payment at 12:00 does not fulfill an initial order if the customer still cannot
  retrieve its usable URL at 12:15; cancellation and refund follow. Conversely,
  URL availability at 12:10 meets the delivery condition even if the automatic
  message fails or the customer does not open the bot until later.
- **Boundary:** This governs initial delivery. A later outage after successful
  fulfillment is not automatically an initial-order refund. PC-014 still governs
  validity start; this does not approve a new notification or endpoint architecture.
- **Not settled:** Total-application-outage catch-up and exact validation evidence
  for delivery availability. Those must not be silently treated as proven.

### PC-050 — Reseller/discount-status accounts may buy as main-store customers

- **Accepted:** 2026-09-27, answer to Q-044: "yes."
- **Behavior:** Otherwise eligible main-store customer accounts may buy composite
  subscriptions through ordinary Telegram checkout regardless of reseller or
  discount status. The subscription belongs to the purchasing customer account
  in the main store. Do not reject an account solely for also having a reseller
  role or discount tier.
- **Scope boundary:** PC-006 still excludes composite reseller-store sales and
  reseller supply flows. This buyer eligibility does not enable reseller GB
  credit, fixed-product inventory, or cross-tenant management for composites.
  Ordinary ownership, blocked-user, and other applicable access restrictions
  still apply; reseller status grants no exemption.
- **Rationale discussed:** Avoid arbitrary exclusion of main-store customers
  while preserving the distinction between buyer status and the business making
  the sale. The accepted trade-off is the need for explicit pricing eligibility
  for these accounts, instead of blocking all reseller-related statuses.
- **References:** PC-006/PC-007/PC-008; D07; A03/A19/A28;
  F-007/F-009/F-014/F-015; constitution I/III.
- **Observable implications:** Two otherwise equivalent eligible main-store
  customers can both reach composite checkout even if one has reseller/discount
  status. Their subscriptions stay under their respective main-store customer
  ownership; the purchase does not create a reseller-store composite or consume
  wholesale inventory/GB credit.
- **Not settled:** Tier discounts, coupons, commissions, referral rewards,
  quantity, and payment-method scope. Buyer eligibility alone does not approve
  those financial benefits or copy unsafe existing settlement behavior.

### PC-051 — Initial purchases honor applicable tier discounts and discount codes

- **Accepted:** 2026-09-27, answer to Q-045: "yes."
- **Behavior:** Initial main-store composite purchases honor configured eligible
  tier discounts and discount codes in the ordinary catalog order: tier reduction
  first, then one eligible code against the reduced price. An automatic tier
  reduction requires the buyer's assigned tier to be enabled and use the discount
  model; a reseller flag alone is insufficient. Use the maximum of configured
  buyer-specific, permanent-tier, and applicable quantity percentages, not their
  sum. This does not by itself authorize multi-unit checkout.
- **Amounts and restrictions:** Preserve integer-floor percentage-discount
  arithmetic in the shop's existing integral price unit. Percentage codes use
  the tier-adjusted amount; either fixed or percentage code reduction is capped
  at that amount so the final price cannot be negative. Respect configured code
  activity, usage limits, expiry, product/category restrictions, and minimum/
  maximum purchase thresholds, using the tier-adjusted price for amount
  eligibility. Financial verification and repeat-safety remain required; F-015's
  cached-code weakness is not approved behavior.
- **Entitlement/refund boundary:** Discounts alter price, not the purchased nodes,
  shared allowance, or duration. Failed-order wallet refunds use the actual paid
  amount, not the nominal price or discount value, under PC-013/PC-048.
- **Rationale discussed:** Keep configured customer benefits consistent across
  the main-store catalog. The accepted trade-off is lower revenue per composite
  sale, including tier/code stacking across a multi-panel service, which the
  owner must consider when setting prices and discounts.
- **References:** PC-008/PC-013/PC-050; D07/D10; A03/A19/A28;
  F-014/F-015; constitution I/II.
- **Observable implications:** Base price 100, eligible 10% tier reduction, and
  eligible 10% code produce 81, not 80. Disabled/non-discount tiers do not gain
  automatic tier reductions. Ineligible codes do not lower the charge. A capped
  code cannot create a negative amount or a refund of more than was paid.
- **Not settled:** Renewal discounts, commissions/referral rewards, zero-total
  checkout, quote validity, coupon-use restoration after failure, quantity,
  payment-method scope, and currency conversion. No new prices or discount
  percentages, coupon records, or financial storage design are selected.

### PC-052 — Composite renewals use the selected preset price and tier-plus-code discounts

- **Accepted:** 2026-09-27, answer to Q-046: "yes we'll go with your recommendation."
- **Behavior:** Price a composite renewal from the selected eligible preset's
  current base price, not the subscription's historic purchase price. Apply the
  buyer's applicable configured tier discount, then one eligible discount code,
  with PC-051's eligibility, restrictions, ordering, caps, and integer-floor
  arithmetic. Code product/category eligibility refers to the selected renewal
  preset. Do not apply the separate legacy early-full-renewal discount to launch
  composites, either instead of these reductions or as a third stacked reduction.
- **Boundary:** This is an explicit composite policy, not a claim of existing
  renewal parity. Preserve affected legacy single-panel and stock-link renewal
  pricing. Discounts change price only; accepted allowance/time carryover and
  the 45-day total remaining validity cap continue to apply.
- **Rationale discussed:** Give composite customers consistent purchase/renewal
  pricing and avoid a third discount layer alongside carryover. The accepted
  trade-offs are reduced renewal revenue compared with undiscounted pricing and
  no separate early-renewal promotion for composites at launch.
- **References:** PC-024-PC-026/PC-032/PC-050/PC-051; D03/D07/D09/D10;
  A03/A12/A15/A25; F-016; constitution I/II.
- **Observable implications:** A renewal preset priced at 100 with an applicable
  10% tier reduction and eligible 10% code costs 81. Enabling the legacy early-
  renewal promotion does not further reduce that composite price. A different
  eligible preset supplies its own current price and code eligibility, rather
  than the original subscription's purchase price or product restrictions.
- **Not settled:** Quote validity and price/eligibility changes before payment,
  zero-total orders, coupon restoration, commissions/referral rewards, payment-
  method restrictions, or checkout quantities. No new discount configuration
  or settlement implementation is approved.

### PC-053 — Purchase-based referral rewards and reseller commissions deferred

- **Accepted:** 2026-09-27, answer to Q-047: "i think not for launch. maybe later."
- **Behavior:** Initial composite purchases and composite renewals generate no
  purchase-based referral reward or referring-reseller commission at launch.
  Do not accrue deferred payouts or promise retroactive rewards for these
  transactions. Possible later support is not approved launch scope.
- **Eligibility and compatibility:** A composite purchase does not consume or
  mark fulfilled first-purchase referral-reward eligibility; a later otherwise-
  qualifying legacy purchase can still qualify. Preserve referral relationships,
  accrued wallet credit, affected legacy reward behavior, and the composite
  buyer's accepted tier/code discounts and ordinary buyer eligibility. This
  exclusion does not disable existing invite-only rewards. Composite free-
  product rewards, trials, and gifts remain separate unresolved scope choices.
- **Rationale discussed:** Narrow launch financial obligations before sales
  begin, avoiding additional payout and refund-reversal policies. The accepted
  trade-off is no purchase-based incentive for referring composite customers.
- **References:** PC-006/PC-050-PC-052; D07/D10; A03/A19/A28;
  F-015/F-016; constitution I/II.
- **Observable implications:** An eligible referred buyer can purchase or renew
  a discounted composite without creating any referral/commission wallet credit,
  future payout obligation, or first-purchase reward consumption. A subsequent
  qualifying legacy purchase retains its existing reward behavior. Repeated
  completion processing does not introduce a composite reward.
- **Not settled:** Whether or how rewards will be introduced after launch;
  composite trial/gift/free-product flows. No future reward basis, rate, or
  retrospective entitlement is approved.

### PC-054 — One subscription per checkout, with separate additional purchases

- **Accepted:** 2026-09-27, answer to Q-048: "yes one subscription per checkout is enough."
- **Behavior:** Each initial composite checkout purchases exactly one subscription.
  Customers may own additional subscriptions through separate checkouts; this is
  not a one-subscription-per-customer limit. Each has its own URL, independent
  child credentials, allowance, validity, fulfillment outcome, and refund
  obligation. Separate purchases do not pool allowance or expiry. Each renewal
  targets one existing subscription.
- **Quantity and pricing:** Checkout quantity is one for PC-051/PC-052. A
  configured quantity discount applies only if its threshold qualifies at one;
  do not count child nodes or aggregate separate orders to reach a higher
  threshold. Other eligible tier/code discounts remain available. Node count
  remains independent of purchase quantity; six is still only an example.
- **Rationale discussed:** Tie each payment and failure/refund outcome to one
  entitlement, avoiding multi-subscription partial fulfillment at launch. The
  accepted trade-off is repeated checkout for several subscriptions and no batch
  quantity discount.
- **References:** PC-001/PC-002/PC-008/PC-011-PC-013/PC-051/PC-052;
  D07/D10; A02-A06/A19/A28; constitution II/VII.
- **Observable implications:** Two successful separate checkouts produce two
  independently managed subscriptions. Failure/refund of one does not alter the
  other. A subscription containing six or more nodes still has purchase quantity
  one and cannot qualify for a multiple-unit discount through its node count.
- **Not settled:** Capacity targets, simultaneous operation rules, general account
  restrictions, or future bulk checkout. This choice does not bypass existing
  account eligibility checks.

### PC-055 — Composite support in the existing free test engine

- **Accepted:** 2026-09-27, explicit replacement for REC-049: "Extend the existing
  bot test feature (`btn_test`) so it can provision composite multi-node
  subscriptions, using the exact same user-facing logic and quota rules
  (`MAX_TEST_PER_USER` / `test_used`) as the legacy test system." Also: "The admin
  should be able to define composite test plans alongside legacy ones."
- **Behavior:** Include composite free tests at launch through the existing main-
  store Telegram test entry and plan-selection flow. Composite and legacy test
  plans coexist. Preserve the common per-user test entitlement governed by
  `MAX_TEST_PER_USER` and `test_used`; do not introduce an extra independent
  composite test allowance or reset test usage merely by adding a plan. Current
  source sets the maximum to one (F-017); this is not a per-plan free entitlement.
  Composite test-plan definition is in scope for the store owner through web
  administration under PC-009/PC-010. "Admin" does not silently broaden those
  previously accepted operator roles or interfaces.
- **Scope:** This rejects deferring all complimentary composite issuance. It
  positively approves free tests; referral gift products and manual owner grants
  remain unresolved, not automatically approved or excluded. Tests are separate
  from paid monthly presets. Main-store scope, independent child credentials,
  one URL, shared allowance, SQLite, and affected legacy compatibility remain.
- **Rationale supplied:** The store is pre-launch for both legacy and composite
  sales, and the user requires the existing test mechanism to support the new
  service. Coexistence avoids a separate customer trial workflow. The rejected
  recommendation's smaller scope is not an accepted reason to defer this work.
- **Constitution boundary:** No conflict with the constitution's product policies
  was found. Preserving intended test behavior does not authorize copying unsafe
  identity, concurrency, or uncertain-provisioning handling. Principles II/III
  still require repeat-safe allocation, authenticated customer ownership, and
  reconciliation of ambiguous remote effects. No exception is approved.
- **References:** USER-01; BC-001; PC-001-PC-003/PC-006-PC-010/PC-031/PC-053;
  D07/D10/D14; A03/A19/A27-A29; F-008/F-017; constitution I-III/VII.
- **Observable implications:** The test button can deliver a selected composite
  test as one multi-node subscription alongside legacy test offers. With the
  current maximum of one, an already-consumed legacy test blocks an additional
  composite test and vice versa. Existing selection and test-disabled behavior
  remain meaningful. Adding future test plans alone does not create new quota.
- **Not settled:** Campaign claim accounting (Q-050), composite trial completion/
  failure deadlines and validity start, later conversion/renewal, management
  capabilities, reset behavior relative to the campaign, and other complimentary
  flows. No detailed implementation or unsafe legacy behavior is selected.

### PC-056 — Initial 15-GiB, 15-day campaign for 150 users

- **Accepted:** 2026-09-27, explicit Q-049 answer: "For our initial launch, offer
  a special promotional composite test plan: 15 GiB data allowance, valid for
  15 days." "Capped at the first 150 users total. Once 150 users claim this
  promotional plan, it closes automatically, while normal catalog plans and
  future admin-defined test plans remain supported."
- **Behavior:** Include a promotional composite test plan with one shared
  15-GiB allowance and a 15-day validity term. Binary GiB follows PC-015, so the
  allowance is 16,106,127,360 bytes total, not per child. The campaign admits at
  most 150 users total in the main store, not 150 per node/panel or a recurring
  daily quota. It closes automatically when its 150-user claim limit is reached.
  Closing this campaign does not close the paid catalog or remove support for
  other/future owner-defined test plans. Those plans still respect PC-055's
  shared per-user test quota.
- **Scope refinement:** This explicitly authorizes a 15-day free promotional
  term outside PC-031/PC-033's paid monthly catalog. Finite data/time still apply.
  It does not change paid launch plans to 15 days or approve a permanent campaign
  reset, additional campaign rounds, or automatic enrollment of all store users.
- **Rationale supplied:** Initial launch giveaway while no VPN sales have begun,
  with a bounded recipient count and continued support for ordinary offers.
- **References:** BC-001; PC-015/PC-016/PC-031/PC-033/PC-055;
  D03/D07/D10/D14; A03-A06/A19/A28; constitution II/III/VII.
- **Observable implications:** Every issued campaign subscription has a shared
  15-GiB allowance and a 15-day term; it does not multiply the grant by node count.
  No 151st campaign recipient is admitted, including under concurrent requests.
  Campaign closure leaves normal catalog availability and other test-plan support
  intact. These are requirements, not passing tests.
- **Not settled:** Exact successful-claim point, in-flight eligibility and failure
  treatment (Q-050), day/start semantics for trials, campaign reset/repeat-user
  rules, and whether trial entitlements can convert or renew into paid plans.

### PC-057 — Campaign places count permanently only after successful fulfillment

- **Accepted:** 2026-09-27, answer to Q-050: "Yes, I agree. A campaign place
  should only count permanently after successful fulfillment. If provisioning
  fails, the held place and the user's test allowance should both be released."
- **Behavior:** Allocate places in order of accepted eligible claim requests.
  Hold a campaign place and the user's ordinary test allowance during pending
  provisioning. Successfully fulfilled grants plus pending claims must never
  exceed 150. Fulfillment requires every required node ready and the complete
  subscription URL retrievable by that customer through Telegram. A failed push
  notification alone does not prevent fulfillment when retrieval is available.
  Repeat requests refer to the same pending claim, not another allocation.
- **Failure and uncertainty:** A definitive provisioning failure without
  fulfillment releases both the campaign place and the user's test allowance,
  allowing another eligible claim or the affected user's retry. Unknown remote
  outcomes stay pending until reconciled; a timeout alone is not proof that
  nothing was issued. Preserve cleanup obligations through failure and release.
- **Closure:** Stop accepting additional claims while all 150 places are either
  pending or fulfilled, but distinguish this temporary full state from completed
  campaign closure. Permanently close when 150 grants have been fulfilled.
  A fulfilled trial's later expiry or exhaustion does not replenish a place.
- **Rationale discussed:** Spend the giveaway on successful recipients rather
  than failed attempts, while preventing concurrent over-allocation. The accepted
  trade-off is that unresolved claims can temporarily hold campaign capacity.
- **References:** PC-055/PC-056; D10/D14; A03-A06/A19/A28;
  F-017/F-018; constitution II/III/VII.
- **Observable implications:** With 149 completed claims and one pending, a new
  claimant cannot obtain an extra place. Confirmed failure of the pending claim
  frees its place and user's test allowance exactly once. Successful fulfillment
  instead closes the campaign at 150. Repeated callbacks, retries, and restarts
  do not increase grants or release the same allowance twice. No partial node
  set counts as a successfully fulfilled campaign grant.
- **Not settled:** Failure/escalation deadlines, trial validity start, campaign
  behavior on ordinary quota resets, repeat-user campaign eligibility after a
  reset, and later trial conversion/renewal. No reservation schema or algorithm
  is selected, and controlled acceptance remains unexecuted.

### PC-058 — Composite test validity starts at complete service availability

- **Accepted:** 2026-09-27, answer to Q-051: "yes."
- **Behavior:** All composite test plans start their configured duration when
  every required node is ready and the complete subscription URL is retrievable
  by the eligible customer through the main-store Telegram bot. All children
  share one expiry. The initial promotional term is exactly 15 elapsed 24-hour
  days (360 hours, 1,296,000 seconds) from that point.
- **Boundaries:** Provisioning time does not consume trial validity. Acceptance
  of a claim, creation of the first child, opening a notification, and first VPN
  use do not start the clock. Once available, delaying retrieval, import, or use
  does not pause, extend, or restart the term. Different children must not start
  separate validity periods during provisioning.
- **Rationale discussed:** Match the paid-subscription availability rule and
  provide the full advertised term after fulfillment. The accepted trade-off is
  that an available but unused trial still consumes its validity; first-use
  activation is not selected.
- **References:** PC-014/PC-033/PC-055-PC-057; D03/D10;
  A03-A06/A12/A19; constitution II/VII.
- **Observable implications:** A campaign request accepted at 12:00 and fulfilled
  at 12:07 expires exactly 360 hours after 12:07, even if the customer imports it
  the following day. Failed push notification does not delay activation when the
  complete URL remains retrievable. No calendar-midnight or DST adjustment turns
  the elapsed 360-hour grant into a different duration.
- **Not settled:** Pending-claim failure/escalation deadline, interruption
  compensation, conversion/renewal, and other trial management capabilities.

### PC-059 — Composite test claims have a 15-minute fulfillment deadline

- **Accepted:** 2026-09-27, answer to Q-052: "yes".
- **Behavior:** Every composite test claim, including the launch promotion, has
  15 minutes from acceptance of the eligible request for all required nodes to
  become ready and the complete URL to become retrievable through Telegram.
  Retries/restarts do not move the deadline. A definitive failure can end the
  attempt earlier; it need not wait until 15 minutes.
- **Deadline outcome:** If incomplete at the deadline, stop late delivery and
  tell the customer the claim could not be completed within the deadline. Keep
  remote reconciliation/cleanup obligations. Confirmed failure without fulfillment
  releases the test allowance and any campaign place under PC-057. Unknown
  remote outcomes retain those holds pending reconciliation, even beyond the
  deadline; distinguish that state from final failure. Flag owner attention in
  web admin and attempt an owner Telegram notification for the uncertain case.
  Notification attempts must not be represented as delivered when unconfirmed.
  Late remote success for a canceled, unfulfilled claim goes to reconciliation/
  cleanup, not late customer delivery.
- **Financial/retry boundary:** Free-test failure creates no monetary wallet
  refund or credit. Once the allowance/place is released, a retry is a new
  eligible claim subject to current availability, without permanent campaign
  priority from the old failed request.
- **Rationale discussed:** Give trials the same customer-visible waiting limit
  as initial paid fulfillment, retaining honest handling of uncertain effects.
  The accepted trade-offs are needing a new request after resolved failure and
  potentially holding allowance/campaign capacity longer while effects remain
  uncertain.
- **References:** PC-012/PC-049/PC-055-PC-058; D10/D14;
  A03-A06/A19/A28; constitution II/VII.
- **Observable implications:** A claim accepted at 12:00 cannot first deliver
  a trial at 12:16. A confirmed failed claim restores its held entitlements
  exactly once; an unresolved remote operation remains visible and does not
  become assumed failure or success at 12:15. Retry/restart does not create a
  fresh deadline for the same claim. No free-test refund wallet entry is created.
- **Not settled:** Total-application-outage catch-up, owner resolution time,
  ordinary test resets relative to campaign eligibility, and technical retry/
  cleanup mechanisms. This product notification policy does not authorize
  messages or automations during the interview.

### PC-060 — General test resets cannot alter campaign history or its cap

- **Accepted:** 2026-09-27, answer to Q-053: "Yes, of course. They are completely
  separate things. General test resets must leave the 150-user campaign recipient
  history and the 150-cap strictly intact."
- **Behavior:** Preserve ordinary `MAX_TEST_PER_USER` / `test_used` eligibility
  and the existing general test-reset capability. Independently, permit only
  one successful launch-campaign grant per main-store Telegram user over this
  campaign's lifetime. A general test reset must not erase successful recipients,
  lower the campaign count, return a fulfilled place, permit a duplicate grant,
  or reopen the campaign after 150 fulfilled recipients. Changing the ordinary
  maximum likewise does not permit a repeat campaign grant. Trial expiry/deletion
  must preserve the history needed to enforce these limits.
- **Eligibility examples:** A reset previous campaign recipient may qualify for
  another available test plan under ordinary rules, but not this promotion again.
  A user whose previous test was legacy, who has never successfully claimed the
  campaign, can claim it after becoming ordinarily eligible if a place remains.
  Confirmed failed campaign attempts remain retryable under PC-057/PC-059.
  A reset must not duplicate or discard unresolved composite claim obligations.
- **Identity boundary:** Campaign recipients are authenticated Telegram users
  in the main store. No extra real-person/device verification is selected, and
  this does not claim to prevent one person using multiple Telegram accounts.
- **Rationale discussed:** Keep the distinct-recipient campaign limit separate
  from reusable general test eligibility. The user explicitly emphasized this
  separation. A general reset cannot rerun the same giveaway; any future campaign
  requires a separate explicit scope decision.
- **References:** PC-055-PC-059; F-018; D10/D14;
  A03/A19/A28-A31; constitution I-IV.
- **Observable implications:** After 150 successful recipients, resetting all
  ordinary test usage leaves the campaign closed and its count/history intact.
  Before closure, a reset previous recipient cannot claim again; refusal must
  not consume their otherwise available quota for a different test plan. Repeated
  resets do not replenish completed campaign places.
- **Not settled:** Future campaigns, trial-to-paid conversion, and trial management
  capabilities. No campaign storage representation or reset algorithm is chosen.

### PC-061 — Composite trials can convert to paid service through renewal

- **Accepted:** 2026-09-27, answer to Q-054: "Yes, I agree. Customers should be
  able to convert their composite trial into a paid subscription through the
  renewal flow, keeping the same URL and credentials."
- **Behavior:** A fulfilled composite test, including the promotional campaign
  trial, can become paid through customer-initiated Telegram full-plan renewal.
  The paid preset must match its saved node configuration under PC-025. Keep the
  same subscription URL and child credentials through ordinary successful
  conversion, as in PC-039. No automatic charge or compulsory conversion.
- **Renewal policy:** Apply the previously agreed current-preset tier-plus-code
  pricing, eligibility/restrictions, complete-node success gate, 15-minute paid-
  renewal deadline, and full-actual-payment wallet refund on failure. Carry
  eligible unused trial data/time into the purchased allowance and 30-day term,
  with the 45-day total remaining validity cap. Expired unused data lapses except
  for the agreed pre-expiry verified-payment protection. Preserve actual usage;
  confirmed old overrun does not reduce the new paid allowance. Failed conversion
  leaves the original trial less actual usage/elapsed time, without replenishment
  or extension. Subsequent renewals follow the same paid renewal rules.
- **Campaign/test boundary:** Conversion neither resets test usage nor returns
  a campaign place, erases participation, or grants another free test. If no
  matching paid preset is available, the customer may separately purchase a paid
  subscription; conversion does not silently migrate nodes.
- **Rationale discussed:** Provide a direct trial-to-paid path without another
  URL import. The accepted trade-off is carrying promotional benefits into the
  first paid period, increasing its available data/time and campaign cost.
- **References:** PC-024-PC-039/PC-052/PC-055-PC-060; D03/D09/D10/D14;
  A12/A15/A19/A25; constitution II/VII.
- **Observable implications:** At successful application, 10 GiB and 5 days
  remaining plus a 50-GiB/30-day paid preset yield 60 GiB and 35 days with the
  same URL/credentials. Failed payment/provisioning does not create paid benefits;
  applicable verified-payment failure refunds remain governed by PC-037/PC-048.
  Campaign recipient count and ordinary test consumption are unchanged by success.
- **Not settled:** Other trial management capabilities and remaining general
  renewal edge cases. This is intended composite behavior, not proof of legacy
  trial conversion or provider compatibility.

### PC-062 — Standard composite quick-check test default

- **Partly superseded by PC-063:** The ten-minute duration and requirement to
  extend duration input precision are withdrawn. The original answer below is
  preserved as history. PC-064 subsequently settles the replacement default as
  configurable 200 MiB and one hour. Ten-minute support remains withdrawn.
- **Accepted:** 2026-09-27, additional Q-054 instruction: "for the general
  composite test plan (outside the 150-user campaign), please note that our
  standard default will be a quick check plan: 200 MB data allowance with a
  10-minute expiry (to let users verify ping and connectivity)."
- **Behavior:** Support a standard general composite test default outside the
  capped campaign, with one shared allowance described by the user as "200 MB"
  and exactly 10 elapsed minutes (600 seconds) of validity. Under PC-058, that
  clock starts when the complete service and retrievable URL are available, not
  at request time or first use. This is a default, not a hardcoded maximum or
  replacement for owner-defined test plans. PC-055's shared ordinary per-user
  test quota still applies; this default grants no additional per-plan allowance.
- **Separation:** The campaign remains 15 GiB/15 days for 150 users, unchanged.
  The campaign's cap does not become a cap on the general quick-check plan.
  Paid presets remain 30 days. Test-to-paid conversion follows PC-061.
- **Unit still unresolved:** Preserve the user's literal "200 MB" until Q-055
  settles decimal MB versus binary MiB. Do not silently equate 200,000,000 bytes
  with 209,715,200 bytes. The accepted magnitude and short duration do not approve
  ambiguous customer labels or change PC-015's agreed binary GiB for other plans.
- **Rationale supplied:** Let users verify ping and connectivity quickly.
- **References:** PC-015/PC-031/PC-033/PC-055-PC-061; D02/D03/D10/D14;
  A03/A07/A12/A19; F-019; constitution I/II/VII.
- **Observable implications:** The standard quick-check test has a common expiry
  600 seconds after availability, not rounded up to one hour or one day. Its
  shared data allowance must not multiply with node count. Current whole-hour
  admin inputs (F-019) are an implementation gap to address, not a reason to
  alter the requested duration. No passing real-panel timing test is claimed.
- **Not settled:** Exact byte count and unit label (Q-055), initial enablement/
  selection priority when campaign and standard tests coexist, and other trial
  management capabilities. No schema, precision representation, or UI design is
  chosen here.

### PC-063 — Retain configurable whole-hour general tests; withdraw ten-minute scope

- **Accepted:** 2026-09-27, correction during Q-055: "ok for the general tests
  we go with the current admin(full hours. dont make an explicit feature)".
  The user also asked: "doesnt the current legacy test allow the admin to
  customize the test accounts?" That question is a request for source facts,
  not approval of REC-055's unit/label recommendation.
- **Behavior:** Preserve the existing general test configuration model with
  positive whole-hour durations. Withdraw PC-062's ten-minute default and its
  proposed minute-level admin capability requirement. Do not add a minutes-input
  feature to satisfy that superseded request. Owner-defined composite test plans
  remain configurable under PC-055; a standard quick-check default must not be
  hardcoded as the only allowed amount or duration.
- **Source clarification:** Existing legacy test plans already allow configurable
  name, prefix, panel, allowance, and whole-hour duration, with multiple plans and
  edit/enable/disable operations (F-018/F-019). Composite support must add the
  agreed independent multi-node entitlement, not pretend the legacy engine
  already implements composites. Composite operator access remains PC-009/PC-010.
- **Rationale supplied:** Use current admin whole-hour behavior without adding
  a separate short-duration capability. This overrides the earlier ten-minute
  preference rather than silently rounding that old request.
- **References:** PC-055/PC-058/PC-062; F-018/F-019;
  D03/D10/D14; A03/A19/A29; constitution I.
- **Observable implications:** General composite test duration is configured in
  positive whole hours; there is no ten-minute acceptance requirement or implied
  promise that a one-hour entry produces ten minutes. Changing an owner's test
  plan parameters is supported rather than being blocked by a fixed quick-check
  constant. The separate campaign remains 15 GiB for 15 days (360 hours), with
  its 150-user history/cap unchanged.
- **Not settled:** Numeric replacement default duration, final byte interpretation
  and labeling of the proposed 200-MB default, and initial active-plan selection.
  The user's factual question did not select a new amount or a unit conversion.

### PC-064 — Configurable standard test default is 200 MiB for one hour

- **Accepted:** 2026-09-27, answer to Q-055/Q-056: "ok so for q55 and q56 we go
  with your recommendation."
- **Behavior:** Set the standard general composite test default to 200 MiB
  (209,715,200 bytes), shared across all child credentials, and one elapsed hour
  (3,600 seconds). Both are owner-configurable plan values, not fixed restrictions
  on other test plans. Preserve positive whole-hour duration configuration under
  PC-063; do not revive PC-062's withdrawn ten-minute requirement. The clock
  starts at full availability under PC-058.
- **Units and labeling:** The 200 value retains the existing test engine's binary
  byte interpretation. Following the approved Q-055 recommendation, make MiB
  explicit in composite administration and customer allowance information. This
  does not change or relabel unrelated legacy plans/fields. The accepted existing
  whole-hour behavior controls duration where Q-055's older wording mentioned
  ten minutes; Q-056's one-hour replacement is the current decision.
- **Scope:** The ordinary shared per-user test quota still applies. The capped
  launch campaign remains 15 GiB/15 days for 150 distinct recipients, with its
  independent history intact. This general default does not create extra test
  eligibility or dictate that every owner-defined plan use these values.
- **Rationale discussed:** Keep binary units consistent with the existing 3x-UI
  test path and PC-015. Use the shortest positive whole-hour duration supported
  by current administration without adding minute-level configuration. The
  accepted trade-offs are about 4.86% more bytes than decimal 200 MB and a longer
  testing window than the withdrawn ten-minute idea.
- **References:** PC-015/PC-055/PC-058/PC-062/PC-063; Q-055/Q-056;
  F-018/F-019; D02/D03/D10/D14; A03/A07/A12/A19; constitution I/II.
- **Observable implications:** The unchanged default grants 209,715,200 bytes
  total and one common expiry 3,600 seconds after full availability. Editing
  the plan's configured allowance/duration is supported; the defaults do not
  override owner settings. Multiple child nodes do not multiply the allowance.
  No ten-minute admin control or decimal reinterpretation is required.
- **Not settled:** Initial active-plan selection, consequences of later edits for
  existing issued trials, and remaining trial management capabilities. No new
  schema or provisioning design is approved.

### PC-065 — Free composite tests have the same leaked-access replacement policy

- **Accepted:** 2026-09-27, answer to Q-057: "yes."
- **Behavior:** Extend PC-040-PC-047's customer-requested leaked-access replacement
  to issued free composite tests, including the launch campaign and the standard
  quick-check plan. First replacement is immediately eligible. Successful
  completion starts the rolling 24-hour per-subscription cooldown; failures do
  not consume it and retries of a pending operation do not create another one.
- **Replacement contract:** Rotate the URL and every child credential, use the
  same revoke-first ordering and complete-delivery gate, 60-second normal target,
  15-minute owner escalation, native existing-session limitation, and audited
  owner cooldown override. The existing-session limitation must remain explicit;
  replacement does not promise that all already-open connections terminate.
- **Entitlement boundary:** Preserve actual usage, remaining allowance, and
  original expiry. Replacement neither grants another trial nor resets test
  usage, returns a campaign place, or erases participation. An expired, exhausted,
  or independently restricted trial must not gain usable access through this
  operation. Conversion to paid service under PC-061 retains the same subscription's
  replacement cooldown, as ordinary renewal already does.
- **Rationale discussed:** Give trial users the same protection against leaked
  access and keep one replacement policy through conversion. The accepted
  trade-off is additional multi-panel work for free and potentially short-lived
  trials while their validity continues to run.
- **References:** PC-040-PC-047/PC-055-PC-064; D11/D14;
  A14/A17/A19/A21; constitution II/III/VII.
- **Observable implications:** A fulfilled one-hour test can request its first
  replacement without waiting 24 hours, but successful replacement grants no new
  hour or allowance. A paid conversion during the resulting cooldown does not
  make a second customer replacement immediately eligible. The campaign count
  and ordinary test consumption remain unchanged by replacement success/failure.
- **Not settled:** Other management controls and remaining general lifecycle
  policies. Controlled provider/client validation remains required and unexecuted.

### PC-066 — Customer access disable/resume does not pause expiry

- **Accepted:** 2026-09-27, answer to Q-058: "yes."
- **Behavior:** Customers can disable and resume their own paid and free-test
  composite subscriptions through Telegram. Disabling requests that every child
  credential reject fresh connections; hiding the URL alone is insufficient.
  Keep the existing URL/credentials, remaining allowance, recorded actual usage,
  and original expiry. Disabling neither saves unused time nor resets data,
  grants compensation, or freezes the validity clock. Present this as access
  disable/resume, not a term pause. Native panel handling of existing connections
  remains applicable; continued traffic is not promised to end immediately and
  actual consumption still counts.
- **Resume authority:** Clear only the customer's own disable request. Resume
  requires otherwise eligible service: unexpired validity, remaining allowance,
  sufficiently trustworthy required usage under the agreed reporting/recovery
  rules, and no independent owner/security/recovery restriction. It cannot
  override expiry, exhaustion, stale-usage suspension, revocation, or incomplete
  leaked-access replacement. A request is not remote completion; keep pending
  outcomes visible until the required nodes' state is confirmed.
- **Persistent choice:** Automatic recovery, renewal including trial-to-paid
  conversion, and credential replacement must not silently clear the customer's
  disabled choice. An eligible customer explicitly requests resumption.
- **Compatibility:** Including tests is an explicit composite capability;
  current legacy tests exclude toggle (F-020). Preserve affected legacy toggle
  eligibility and behavior rather than silently enabling it for legacy tests.
- **Rationale discussed:** Provide reversible customer control without adding
  validity freezing or a new time-credit policy. The accepted trade-off is
  additional multi-panel lifecycle work, and a disabled test can expire unused.
- **References:** PC-014/PC-018/PC-022/PC-023/PC-039/PC-058/PC-061/PC-065;
  D03/D11/D14; A12/A14/A17/A19/A21; F-020; constitution II/III/VII.
- **Observable implications:** Disable with 40 minutes left and resume ten
  minutes later leaves at most 30 minutes. Expired/exhausted service cannot
  regain usable access through resume. Successful renewal of a customer-disabled
  subscription leaves it disabled until the customer separately resumes it.
- **Not settled:** Numeric completion/escalation targets (Q-059), handling rapid
  conflicting requests, and other customer/owner management capabilities. No
  lifecycle algorithm, worker, or endpoint is selected.

### PC-067 — Access-state changes target 60 seconds and escalate at 15 minutes

- **Accepted:** 2026-09-28, answer to Q-059: "yes".
- **Behavior:** Under supported normal conditions, complete an authorized,
  eligible customer disable/resume request within 60 seconds of acceptance,
  including remote action and confirmation across all required nodes. Disable
  means all children reject fresh authentication, with native existing-session
  handling separate. Resume means every required child is ready for otherwise
  eligible access under PC-066. Retries/restarts do not restart the clock, and
  the clock does not begin only after panel calls.
- **Eligibility boundary:** Explain and refuse known-ineligible resume rather
  than promising activation. Recheck continued eligibility; a newly expired,
  exhausted, or restricted subscription must not be enabled merely to complete
  an earlier request. Request acceptance, partial remote action, and confirmed
  completion remain distinguishable.
- **Escalation:** If unresolved after 15 minutes from acceptance, flag owner
  attention in web admin, attempt an owner Telegram notification, and show the
  customer the pending/blocked status and support path. A missed 60-second target
  is visible when it occurs, not hidden until escalation. Notification failure
  must neither erase pending work nor be reported as delivered. Continue
  recoverable reconciliation where possible, retaining manual recovery work
  when automatic attempts are exhausted. Fifteen minutes is not cancellation,
  rollback, or permission to reverse the customer's desired access state.
- **Outage/entitlement boundary:** Retain best-effort cutoff during control/panel
  outages, without claiming completed all-node state from a pending request.
  Expiry continues and actual usage remains counted. Missing these targets alone
  creates no automatic expiry extension or wallet compensation.
- **Rationale discussed:** Match leaked-access replacement's completion and
  owner-attention targets. The accepted trade-off is alerts during extended
  outages and the requirement to demonstrate the normal target under supported
  versions and load before claiming it is met.
- **References:** PC-019-PC-021/PC-045/PC-046/PC-066;
  D02/D11/D14; A14/A17/A19/A21; S07/S09; E-001/E-002;
  constitution II/VI/VII.
- **Observable implications:** In controlled normal-operation checks, a request
  accepted at 12:00 is confirmed across required nodes by 12:01. If still
  unresolved at 12:15 it needs owner attention, while desired state and recovery
  responsibility persist. An expired subscription does not resume to satisfy
  the target. These are accepted targets, not passing checks or polling periods.
- **Not settled:** Total-application-outage catch-up, owner response time,
  competing-request behavior, and technical coordination/retry mechanisms.

### PC-068 — No automatic refunds for voluntarily unused fulfilled service

- **Later qualification:** PC-073 separately covers cancellation requested while
  a paid renewal is still in flight: that renewal is refunded in full after
  resolution even if it succeeds after the request. It does not create a general
  refund right for renewals already fulfilled before cancellation was requested.
- **Accepted:** 2026-09-28, answer to Q-060: "we'll go with your recommendation."
- **Behavior:** At launch, do not automatically refund unused data or validity
  after successful initial paid fulfillment, paid renewal, or trial-to-paid
  conversion when a customer changes their mind or voluntarily stops using the
  service. Customer disable/non-use creates no wallet credit, original-method
  reimbursement, or monetary value for unused entitlement. There is no implicit
  buyback rate for remaining allowance or time.
- **Scope boundary:** Preserve all agreed full-wallet refunds for failed paid
  fulfillment and renewal. Later service outages or operator fault are separate
  remedy cases, not automatically treated as voluntary non-use. Owner-approved
  goodwill/manual remedies remain unresolved. This decision does not select
  customer permanent cancellation/deletion or its revocation behavior and does
  not resolve every possible dispute or failure remedy.
- **Rationale discussed:** Avoid pricing unused time, data, and carried promotional
  benefits, keeping launch finances predictable. The accepted trade-off is less
  flexibility for customers who stop using a working service.
- **References:** PC-011-PC-014/PC-037/PC-048/PC-061/PC-066;
  D03/D10/D14; A03-A06/A12/A15/A25/A28; F-021; constitution II/VII.
- **Observable implications:** Voluntarily disabling a fulfilled subscription
  with 30 GiB and 15 days remaining creates no automatic wallet credit. A failed
  later paid renewal still produces the PC-037 refund. Explain these launch
  refund terms before checkout; successful service delivery and voluntary
  non-use must not be confused with failed paid fulfillment.
- **Not settled:** Owner-approved compensation, remedies for post-fulfillment
  outages or operator fault, and permanent cancellation/deletion policies.

### PC-069 — Owner-approved support compensation uses store-wallet credit

- **Accepted:** 2026-09-28, answer to Q-061: "yes but admin should be able to
  choose multiple costumers at once too." The additional multi-customer
  requirement is recorded separately in PC-070.
- **Behavior:** The store owner can approve a specified positive store-wallet
  credit through web administration for a composite support case, including
  post-fulfillment service failure or discretionary goodwill. Choose the amount
  case by case. Record the actor, affected customer/subscription, reason, amount,
  and confirmed or pending outcome. Duplicate submissions, retries, or restarts
  must not credit the same approved action twice. Failed/pending credit remains
  honestly reported and recoverable.
- **Scope:** Do not introduce automatic proration, outage-to-money formulas,
  original-method refunds, or automatic time/data extensions for these support
  cases. The credit itself does not renew, extend, reset, disable, revoke, or
  delete service, or alter test/campaign eligibility/history. Any lifecycle
  action is separate. Guaranteed failed-fulfillment refunds remain automatic
  and exact-amount; they must not wait for owner discretion. Show prior credits/
  refunds when deciding further compensation so a further grant is explicit.
- **Authority:** "Admin" in this answer retains PC-009/PC-010's store-owner-only,
  web-admin scope. It does not silently authorize other staff or customers.
- **Rationale discussed:** Provide a flexible support remedy without defining
  automatic compensation for every outage. The accepted trade-off is owner work
  and case-by-case outcomes rather than a guaranteed compensation schedule.
- **References:** PC-009/PC-010/PC-013/PC-023/PC-048/PC-067/PC-068;
  D10/D14; A03-A06/A19/A25/A28; F-021; constitution II/III/VII.
- **Observable implications:** A chosen credit reaches the intended customer's
  wallet once with an audit record, leaving subscription expiry, allowance, and
  access unchanged by that credit action. An unauthorized staff/customer request
  cannot grant it. Failed automatic refunds still follow their guaranteed path.
- **Not settled:** Completion/owner-response targets, compensation budgets/caps,
  support-case eligibility promises, and bulk amount semantics (Q-062).

### PC-070 — Compensation supports selecting multiple customers at once

- **Accepted:** 2026-09-28, explicit addition to Q-061: "admin should be able
  to choose multiple costumers at once too."
- **Behavior:** The owner must be able to select multiple main-store customers
  in one compensation operation rather than being limited to issuing each credit
  through a separate one-customer interaction. Single-customer compensation
  remains available. All PC-069 authority, audit, repeat-safety, recovery, and
  entitlement-separation requirements apply to the selected recipients.
- **Rationale supplied:** The user requires multi-customer selection. This enables
  handling a shared incident without repeated individual selection.
- **References:** PC-006/PC-009/PC-010/PC-069; D10/D14;
  A03/A19/A28; constitution II/III/VII.
- **Observable implications:** The owner can select more than one intended
  customer for a compensation action. Merely supporting one-customer wallet
  adjustment is insufficient acceptance evidence. The operation must not credit
  unrelated/unselected customers or another store's customers.
- **Not settled:** Whether the entered amount is per customer or a shared budget,
  differing amounts within one selection, batch-size limits, selection/filter
  mechanics, and interrupted-batch outcome handling. No specific interface,
  storage schema, or transaction/worker architecture is selected.

### PC-071 — Bulk compensation applies the entered amount per unique customer

- **Accepted:** 2026-09-28, answer to Q-062: "yes."
- **Behavior:** In a multi-customer compensation action, the owner enters one
  positive amount that applies equally in full to each unique selected customer.
  It is not a total budget split among recipients. A customer selected through
  multiple subscriptions or repeated selections is one recipient and receives
  one credit for that action. Show the resolved recipients, unique count, amount
  per customer, total credit, and reason before the owner authorizes it.
- **Selection boundary:** Do not add an unselected recipient to the approved
  action without renewed authorization of that changed selection. For launch,
  use separate actions for groups requiring different amounts, rather than a
  per-recipient amount editor or automatic shared-budget division. Preserve
  PC-069's customer/subscription context, audit, and repeat-safe crediting.
- **Rationale discussed:** Make total compensation predictable and avoid division/
  rounding ambiguity or multiple credits for a customer's several subscriptions.
  The accepted trade-off is separate actions for differing compensation amounts.
- **References:** PC-069/PC-070; D10/D14; A03/A19/A28;
  constitution II/III/VII.
- **Observable implications:** Selecting ten unique customers and entering 50
  shop price units previews and credits 50 each, 500 total, not 5 each. Listing
  one of those customers twice does not change the recipient count or total.
  Reprocessing the same approved action cannot credit those customers again.
  The example specifies neither an actual currency nor a real compensation grant.
- **Not settled:** Batch-size limits, interrupted-action outcomes, and selection/
  filtering details. No all-or-nothing versus partial-commit architecture,
  storage schema, or permission to perform actual credits is selected here.

### PC-072 — Customers may permanently cancel fulfilled composite subscriptions

- **Later sequencing qualification:** When a paid renewal is already in flight,
  PC-073 defers the subscription's credential revocation until that renewal
  resolves, then requires immediate revocation initiation and a full renewal
  refund. Pending-cancellation presentation, early URL invalidation, and stalled
  renewal outcomes require explicit treatment; do not silently apply two
  contradictory concurrent mutation sequences.
- **Accepted:** 2026-09-28, answer to Q-063: "Yes, I agree. Customers should be
  able to permanently cancel their own paid or test composite subscription
  through Telegram with explicit confirmation and without an automatic refund."
- **Behavior:** Offer customer-requested permanent cancellation for their own
  fulfilled paid or test composite subscription through Telegram, with explicit
  confirmation explaining permanent loss of that service and no automatic unused-
  service refund. Distinguish this from reversible access disable. Once accepted,
  invalidate the subscription URL and pursue revocation of every child credential.
  List removal or URL hiding is not proof of credential revocation. All old
  credentials must reject fresh authentication; already-open connections remain
  subject to the accepted native panel behavior rather than custom termination.
- **Permanent state:** The canceled subscription cannot resume or renew. Recovery
  must not reactivate it. Future service requires a separate eligible purchase
  or test claim; cancellation does not restore ordinary test allowance, return
  a completed campaign place, or erase participation.
- **Records and remote responsibility:** Keep financial, usage, and ownership
  history and every identity/pending obligation needed for cleanup and auditing.
  Permanent cancellation is not immediate deletion of all records. Distinguish
  accepted cancellation, pending remote revocation, and confirmed all-child
  revocation; an unreachable panel must not be reported as confirmed cutoff.
- **Rationale discussed:** Let customers end service without support while
  preserving cleanup responsibility. The accepted trade-off is irreversible
  loss of remaining service without automatic compensation; reversible disable
  remains available for temporary breaks.
- **References:** PC-004/PC-005/PC-060/PC-066/PC-068/PC-069;
  D11/D14; A14/A17/A19/A26/A29-A31; F-021; constitution II-IV/VII.
- **Observable implications:** After confirmed customer cancellation, the old
  URL cannot supply usable credentials. Unconfirmed remote cutoff stays visible
  as pending. Retry cannot refund, recreate access, or erase campaign/test history.
  A canceled subscription is rejected as a renewal or resume target.
- **Not settled:** Pending paid renewal/replacement/credit interactions (Q-064
  addresses paid renewal), numeric completion/escalation targets, archive display,
  and retention periods. No record-deletion or storage algorithm is selected.

### PC-073 — Resolve an in-flight renewal before revocation, then refund it in full

- **Accepted:** 2026-09-28, revised Q-064 answer: "Yes, refund the renewal payment."
  "If the customer requests cancellation while a renewal is in-flight, let the
  renewal operation finish cleanly first. Once it finishes, immediately revoke
  the subscription and refund 100% of the renewal payment to the customer's
  store wallet (no usage math needed since it was just renewed)."
- **Behavior:** Record the customer's confirmed permanent cancellation request
  while the verified-paid renewal is in flight. Let that renewal operation resolve
  first rather than intentionally racing a revocation against its ongoing
  changes. Once it finishes, immediately begin permanent subscription revocation
  and refund the full actual renewal payment to the customer's store wallet,
  including wallet/external funding. A renewal that succeeds after the request
  still receives this full refund; do not prorate it for usage, elapsed time,
  or newly granted/remaining allowance. Preserve actual usage evidence even
  though it is not used to reduce this refund.
- **Refund boundary:** Refund only the affected in-flight renewal payment, not
  previously fulfilled purchases or earlier renewals. PC-068/PC-072 still govern
  a cancellation requested after renewal had already fulfilled. If a failed
  renewal has already received its required refund, cancellation must not credit
  it a second time. Unverified payment evidence cannot authorize a credit.
  The same rule covers a paid trial-to-paid conversion in flight; ordinary test
  usage and campaign recipient history remain intact.
- **Lifecycle boundary:** Pending cancellation is not confirmed revocation. The
  final state remains permanently canceled, with URL invalidation, all-child
  revocation, no future resume/renewal, retained cleanup obligations, and native
  existing-session handling under PC-072. A possible renewed-access interval
  before revocation completes is not permission to charge back part of this
  refund. No further paid renewal should be admitted for a subscription with
  confirmed pending permanent cancellation.
- **Rationale supplied:** "To avoid complex race conditions, use a sequential
  completion approach." Capture the requested observable order and full-refund
  policy. It reduces intended overlap but does not prove that timeouts, late
  remote responses, duplicate callbacks, or crashes cannot race; constitution
  II/IV/VII still require reconciliation, repeat-safety and honest outcomes.
  No worker architecture, lock, algorithm, schema, or constitutional exception
  is approved by this product sequence.
- **References:** PC-013/PC-036/PC-037/PC-048/PC-061/PC-068/PC-072;
  D09/D10/D14; A03-A06/A15/A25/A28; constitution II/IV/VII.
- **Observable implications:** A cancellation requested during paid renewal
  remains recorded while that renewal resolves. If it then succeeds, the system
  proceeds to revoke the subscription and credits 100% of that actual renewal
  payment once. Brief intervening usage does not reduce the refund. A previously
  completed renewal is not retroactively made refundable by this rule.
- **Not settled:** What counts as resolution when renewal stalls or remote
  outcome is unknown (Q-065), numeric post-resolution revocation/refund targets,
  URL behavior during the wait, and overlapping credential replacement/support
  credits. PC-037's existing 15-minute renewal deadline has not been explicitly
  extended or removed; reconcile it with this sequence rather than infer an
  unlimited wait or falsely classify uncertainty as clean completion.

### PC-074 — Original renewal deadline bounds pending-cancellation waiting

- **Accepted:** 2026-09-28, answer to Q-065: "yes."
- **Behavior:** Preserve the renewal's original 15-minute deadline from verified
  payment. A permanent cancellation request during that renewal does not restart
  the timer. Earlier successful resolution proceeds immediately under PC-073;
  earlier confirmed terminal failure proceeds to cancellation and its required
  refund. If still incomplete at the original deadline, end renewal fulfillment
  eligibility, refund the full actual verified renewal payment once, and move
  the subscription toward permanent revocation rather than awaiting successful
  renewal indefinitely.
- **Uncertainty boundary:** Failed fulfillment at the deadline does not prove
  that remote effects are known or every call has stopped. Keep ambiguous actions,
  partial changes, and revocation pending for durable reconciliation. Do not
  report a clean remote failure or completed cutoff without evidence. Reconcile
  late renewal effects toward revoked access; do not reactivate the canceled
  subscription. Show the unresolved revocation to customer and owner with a
  support path and retain responsibility until resolved.
- **Refund timing:** Do not wait for remote cleanup or notification success.
  Under normal application/database conditions, the actual-payment wallet refund
  is visible and spendable within 60 seconds of the renewal's failure/cancellation
  decision under PC-048. Repeated cancellation or renewal completion must not
  duplicate the refund. No usage proration applies under PC-073.
- **Rationale discussed:** Retain the sequential normal path while preventing
  an unavailable panel from holding verified payment indefinitely. The accepted
  trade-off is durable timeout reconciliation; waiting alone does not eliminate
  all cancellation/remote-effect races.
- **References:** PC-037/PC-048/PC-072/PC-073; D09/D10/D14;
  A03-A06/A15/A25/A28; constitution II/IV/VII.
- **Observable implications:** Payment verified at 12:00 and cancellation requested
  at 12:14 retain the 12:15 deadline, not 12:29. If renewal is still incomplete,
  the normal-condition refund is usable by 12:16 while unresolved remote cutoff
  remains visible. A later panel response cannot supply a renewed active service
  or another wallet credit. These are requirements, not demonstrated checks.
- **Not settled:** Numeric revocation completion/escalation targets, refund timing
  after the successful-renewal branch, URL behavior during the wait, total-app
  outage catch-up, and other overlapping operations. No remote-call interruption
  or coordination algorithm is selected.

### PC-075 — Final cancellation targets 60 seconds and escalates at 15 minutes

- **Accepted:** 2026-09-28, answer to Q-066: "yes."
- **Stage start:** Begin final cancellation immediately after the confirmed
  request if no paid renewal is in flight. Otherwise begin immediately upon
  renewal success, confirmed terminal failure, or its original 15-minute
  fulfillment deadline under PC-073/PC-074. During the preceding wait, show
  cancellation pending; URL invalidation and credential revocation belong to
  this final stage rather than an earlier competing cancellation operation.
  The pending cancellation blocks further renewals under PC-073.
- **Normal completion:** Immediately initiate URL invalidation and all-child
  revocation at stage start. Within 60 seconds under supported normal conditions,
  the URL is invalid and every child is confirmed to reject fresh authentication.
  This does not promise forced termination of existing sessions, which retain
  native panel behavior. If a renewal refund is required, make its full verified
  amount visible and spendable within the same 60 seconds under normal app/database
  conditions, including the successful-renewal-after-request branch. The refund
  does not wait for remote revocation/cleanup or notification delivery.
- **Escalation:** Unresolved final-stage work at 15 minutes needs owner attention
  in web admin, an attempted owner Telegram notification, and customer-visible
  pending components/support path. Keep credit outcome distinct from remote
  revocation. Show a missed 60-second target when it occurs. Notification failure
  does not count as delivery or discard pending work. Preserve canceled state
  and recovery obligations; retries/restarts neither reset timers nor reactivate
  service or duplicate refunds. Escalation is not abandonment or reversal.
- **Rationale discussed:** Preserve the requested sequential renewal behavior
  with a measurable final phase consistent with other access controls. The
  accepted trade-off is that total waiting can include the remaining renewal
  window plus final-stage time, with outage cutoff still best-effort under PC-019.
- **References:** PC-019-PC-021/PC-048/PC-067/PC-072-PC-074;
  D02/D09/D10/D11/D14; A14/A17/A25/A28; E-001/E-002;
  constitution II/VI/VII.
- **Observable implications:** If renewal resolves at 12:05 after a pending
  cancellation, final work begins then; under normal conditions URL/all-child
  fresh-authentication revocation and the required wallet credit complete by
  12:06. Unresolved work at 12:20 is escalated. With no renewal, these clocks
  start at cancellation acceptance. A panel outage cannot delay an otherwise
  processable refund or be represented as confirmed remote cutoff.
- **Not settled:** Cancellation during other operations, total-app outage
  catch-up, and owner response time. Targets are unverified; no technical
  coordination, transaction, worker, or scheduling design is approved.

### PC-076 — Base64-encoded configuration-link subscriptions are required

- **Accepted basis:** 2026-09-28, Q-067 clarification: "i dont know about clash.
  i think the standard these days are base64 encoding configs like this:
  (vless://xxxxxx,,,vless://xxxxxx,,,vmess://,,, and so) and apps like v2box
  streisand v2rayn v2rang and... can decode them and add them."
- **Behavior selected:** Support the requested Base64-encoded list of protocol
  configuration links through the single composite subscription URL. Preserve
  the actual VLESS/VMess/Trojan configuration content required by the approved
  topology. The user's commas/ellipses are illustrative, not an agreed wire
  delimiter; ordinary URI-list text is newline-separated (F-022/F-023).
- **Scope boundary:** This confirms the desired Base64 URI-list experience. It
  does not approve every client/version, establish that this is a universal
  current standard, or explicitly defer native Clash YAML/sing-box JSON. The
  user expressed uncertainty about Clash; uncertainty is not approval of its
  exclusion. Q-067 remains open only for that remaining export scope. Raw text
  output as a separately supported form likewise is not inferred from this
  statement alone. R05's existing named targets remain required.
- **Client examples:** V2Box and v2rayN were newly mentioned as examples; record
  them for client-matrix clarification rather than silently require every app
  implied by "and...". Preserve "v2rang" as supplied, without silently selecting
  an additional application/version from that spelling. Screenshot client Throne
  is visual context, not a separately approved compatibility target.
- **Rationale supplied:** The user wants an ordinary subscription experience in
  which supported apps decode the links and add the configurations.
- **References:** PC-001/PC-002/PC-007; R05; D05; A20-A22/S04;
  F-022/F-023; X-003; E-003; constitution I/V/VI.
- **Observable implications:** A supported client fetches the one URL, decodes
  the subscription and imports all required actual nodes with intact protocol
  fields and remarks. Real handshakes/traffic still require controlled evidence;
  decoding alone is not fulfillment of compatibility acceptance.
- **Not settled:** Native structured format deferral (Q-067), raw output coverage,
  additional release-client targets/exact versions, and client-specific treatment
  of informational entries requested in PC-077.

### PC-077 — Subscription informational entries for messages, expiry and remaining data

- **Accepted:** 2026-09-28, explicit additional request: "one thing i want for
  subs is creating fake configs like this image to show messages and expiry date
  and quota remaining". The attached image was successfully viewed at its WSL
  path despite the initial Windows-path read error.
- **Behavior required:** Include informational entries in the subscription's
  imported configuration list, using their displayed names to communicate store
  messages, subscription expiry and remaining shared allowance. These are
  informational entries distinct from real VPN nodes and independently managed
  child credentials. They do not grant extra allowance, create additional real
  panel clients/meters, or count as working VPN endpoints in the six-node fixture.
  PC-002's six intended working nodes must remain complete alongside this newly
  requested information presentation.
- **Observed image, IMG-001:** Attachment named
  `codex-clipboard-1d6b76be-e456-4cea-a592-15c7a64722a4.png`, viewed 2026-09-28,
  shows a Throne configuration list with ordinary nodes and bottom VLESS-shaped
  rows displaying a message, status, traffic figures and expiry information.
  This is evidence of the requested presentation, not of these rows being
  functional connections or safe to auto-select. Do not copy addresses, account
  identifiers, logs, or incidental values from the screenshot into fixtures.
  Exact status fields, identifiers, row count, placement, and wording are not
  implied requirements merely because they appear in the image.
- **Accounting boundary:** Remaining allowance/expiry refer to the parent
  composite entitlement, not a single child's independent-looking panel limits.
  Preserve PC-004's distinction between verified data, stale readings, and
  unknown usage. A display entry must not fabricate current remaining quota,
  zero use, unlimited service, or successful remote cutoff from missing evidence.
- **Rationale supplied:** Make messages and subscription information visible in
  the VPN app's configuration list, as in the user's example.
- **References:** USER-01; PC-001/PC-002/PC-004/PC-015/PC-076;
  R05; D02/D05/D11; A07-A17/A20-A22/S04; IMG-001; F-023; E-003;
  constitution II/V/VI/VII.
- **Observable implications:** Import/refresh can show the requested information
  alongside all real nodes, without treating those rows as additional purchased
  VPN credentials or quota allocations. Validate real-node counts separately
  from total displayed rows. Display values are subscription-refresh snapshots,
  not a promise that an already-imported name updates live without refresh.
- **Not settled:** Exact information-row representation/labels, stale-value text
  and timestamps, placement, selectable/non-connectable behavior and automatic
  selection effects in each supported client, refresh expectations, optional
  metadata headers, and behavior for revoked/expired public URLs. No synthetic
  endpoint address, credential material, schema, or serializer is selected here.

### PC-078 — Launch exports only the Base64 URI-list subscription with information entries

- **Accepted:** 2026-09-28, final Q-067 answer: "yes only this for launch."
- **Behavior:** Launch composite delivery uses the Base64-encoded URI-list
  subscription required by PC-076, including PC-077's informational entries for
  messages, expiry, and remaining allowance. Native Clash YAML, native sing-box
  JSON, and a separate supported raw-text export are deferred beyond launch.
  This is an explicit release-scope choice; it does not remove affected legacy
  output capabilities or authorize changing existing legacy links.
- **Node/client boundary:** Preserve every intended working node, stable ordering,
  distinct descriptive remarks and all required protocol/transport/security
  fields. Information entries are separate from real nodes. Do not silently
  drop nodes/fields to obtain a parseable output. R05/PC-002's v2rayNG, NekoBox,
  and Streisand targets remain required, with exact versions and actual import,
  refresh, handshakes and traffic needing controlled evidence. An incompatible
  required client is a blocker, not permission to drop it or claim compatibility.
- **Scope meaning:** Deferring native profile exports does not itself exclude
  an app because of its core; actual URI import and protocol compatibility must
  be established. V2Box/v2rayN examples and the screenshot's Throne client do not
  automatically expand the required release matrix under this format decision.
- **Rationale discussed:** Match the user's requested subscription experience
  while reducing the number of formats to support and verify at launch. The
  accepted trade-off is postponing native exports for users who require those
  other formats. No universal client interoperability is claimed.
- **References:** PC-001/PC-002/PC-007/PC-076/PC-077; R05; D05;
  A20-A22/S04; F-022/F-023; X-003; E-003; constitution I/V/VI.
- **Observable implications:** The launch URL supplies a complete Base64 URI
  list with the agreed information presentation; native Clash/sing-box or raw
  output is not a launch acceptance requirement. Six-node fixture checks still
  verify six working VPN endpoints separately from information-only rows. Passing
  a decoder alone is not passing the named-client compatibility checks.
- **Not settled:** Exact client versions/additional required apps, information-
  entry display/freshness/selection behavior, download outages/cache policy,
  revoked/expired URL responses, and serializer/endpoint details deferred to
  planning. No protocol implementation or architectural design is approved.

### PC-079 — Information entries retain timestamped last-reliable quota during delays

- **Accepted:** 2026-09-28, answer to Q-068: "yes sir."
- **Behavior:** When usage updates are delayed or incomplete, retain the last
  reliable composite remaining-allowance figure with its usage-update timestamp
  and an explicit delayed/incomplete warning. Identify it as last-confirmed
  information, not the current verified balance. If no reliable whole-subscription
  figure exists, show remaining allowance as unknown; do not fabricate zero use,
  zero remaining, full quota, unlimited quota, or treat missing child readings
  as zero. Keep the known subscription expiry visible independently.
- **Snapshot boundary:** Include an as-of timestamp with usage information even
  while updates are healthy. Imported configuration names are snapshots until
  subscription refresh, not a live dashboard. The timestamp must reflect source
  usage information; fetching the URL or restarting the app/server does not
  advance it without a real usage update.
- **Enforcement/status boundary:** During PC-018's grace period, delayed usage
  information is not confirmed suspension. Distinguish requested/pending
  suspension from confirmed cutoff. These display rules do not extend the
  five-minute grace, change accounting, or promise live pushes into VPN apps.
- **Rationale discussed:** Preserve useful context without concealing uncertainty.
  The accepted trade-off is that an old balance may overstate remaining usable
  allowance, requiring conspicuous qualification; hiding it entirely was the
  alternative.
- **References:** PC-004/PC-015/PC-018/PC-077/PC-078; D02/D05/D08/D11;
  A07-A17/A20-A22; F-023; E-002/E-003; constitution II/VI/VII.
- **Observable implications:** A prior reliable 12-GiB balance during an update
  outage is displayed as last confirmed with its actual update time and warning.
  A never-known balance is shown as unknown. Repeated subscription downloads
  without new readings do not make the timestamp appear fresh or clear the
  warning. Expiry remains displayed when known even if usage is unavailable.
- **Not settled:** Exact wording/localization/timezone layout, row count and
  placement, display rounding, client selection behavior, and refresh interval.
  No sample-aggregation algorithm or live update mechanism is selected.

### PC-080 — Five named apps are required launch compatibility targets

- **Accepted:** 2026-09-28, answer to Q-069: "yes and i dont think there would
  be any blockers by these. im using them day to day."
- **Behavior:** Add V2Box and v2rayN to the existing v2rayNG, NekoBox, and
  Streisand launch targets. Establish and record a supported version/platform/core
  matrix during planning and controlled validation. This is not a promise about
  every historical/future version or fork. Throne is not mandatory solely
  because it appears in the screenshot; "and..." does not imply every VPN app.
- **Required verification:** In each supported target, verify the single Base64
  URL's import/refresh, all intended working fixture nodes and remarks, actual
  protocol/security/transport handshakes and traffic, and the informational-entry
  display with agreed stale-data presentation. Information rows are not working
  nodes. Investigate selection/automatic-selection effects as part of E-003;
  do not substitute parser success or screenshot appearance for compatibility.
- **Rationale discussed:** Include the two additional apps the user named without
  claiming universal support. The user expects no blockers based on daily use
  (BC-002). The discussed trade-off is a larger verification matrix; no actual
  incompatibility has been established in this interview.
- **References:** PC-002/PC-076-PC-079; BC-002; R05; D05;
  A20-A22/S04; E-003; constitution VI.
- **Observable implications:** Release evidence includes the five named apps
  at recorded versions. The original three alone are no longer sufficient client
  coverage. Any demonstrated unmet mandatory behavior requires resolution or
  explicit scope revision, not silent omission of a client, node, or field.
- **Not settled:** Exact versions/platform/core combinations and actual validation
  results, plus informational-row selection behavior. Those facts must be
  researched/tested rather than guessed by the user. No client installation,
  integration test, or service execution is authorized in this interview.

### PC-081 — Keep complete subscription downloads available during management outages

- **Accepted:** 2026-09-28, answer to clarified Q-070: "oh yes lets go with
  your recommendation."
- **Behavior:** For an already fulfilled subscription with a still-valid URL
  and no expiry, permanent-revocation, or replacement-delivery block, continue
  serving the last verified complete configuration for its current credential
  generation while panel management APIs are unavailable. This includes stale-usage
  suspension pending or confirmed. Preserve every intended real node and its
  protocol/security fields and remarks; do not silently drop nodes, substitute
  endpoints, or return a successful empty/partial list because a panel is unreachable.
- **Status and enforcement:** Include informational entries with timestamped
  last-reliable usage or explicit unknown usage under PC-079. Distinguish delayed
  readings during grace, suspension requested/pending, and confirmed suspension.
  PC-018's five-minute threshold still runs from the last trustworthy reading;
  it requests suspension of every child of each affected subscription, including
  healthy-panel children. Unrelated subscriptions are not globally suspended.
  Unreachable credentials may remain usable under PC-019's best-effort cutoff;
  PC-022's reconciliation and eligibility conditions still govern automatic recovery.
- **Boundaries:** Serving the list does not enable credentials, certify VPN
  reachability, make usage fresh, or extend grace. Never accept an invalidated URL,
  restore old rotated/revoked credentials, or bypass cancellation, replacement
  delivery gates, or other access policy. Without a trustworthy complete current
  configuration, report temporary unavailability rather than inventing fields or
  presenting a partial list as success. A download must not provision clients,
  reset usage, or initiate renewal.
- **Rationale discussed:** Customers can retain their node list and see outage
  information on refresh while enforcement continues. The accepted trade-off is
  that listed nodes may be disabled, unreachable, or externally changed; listing
  is not a live health guarantee. Blocking downloads would not revoke credentials
  already imported into apps.
- **References:** PC-001/PC-004/PC-018-PC-023/PC-042/PC-043/PC-078-PC-080;
  D05/D11; A20-A22/S04; constitution II/V/VII.
- **Observable implications:** With a complete previously verified configuration,
  losing a required panel's management API does not remove its nodes from refreshes.
  At five minutes without trustworthy readings, all affected subscriptions request
  whole-subscription suspension, while their permitted URLs still return the complete
  list with accurate pending/confirmed status. No download clears that restriction.
  Invalidated URLs and superseded credentials do not become available through fallback.
- **Not settled:** Downloads for expired, exhausted, customer-disabled, or
  owner-disabled subscriptions; public-endpoint outages; external panel-edit policy.
  No cache/storage design, TTL, API sequence, or worker architecture is selected.

### PC-082 — Keep downloads available after expiry, exhaustion, or customer disable

- **Accepted:** 2026-09-28, answer to Q-071: "yes".
- **Behavior:** Fulfilled paid and test composite subscriptions continue serving
  their complete current node list through a still-valid URL after expiry, quota
  exhaustion, or voluntary customer disable. Informational entries explain the
  inactive state and show known expiry and appropriately qualified usage. Describe
  pending versus confirmed credential cutoff accurately; list availability does
  not establish that remote enforcement has completed.
- **Access boundaries:** Downloading must not enable credentials, renew service,
  reset usage, or clear voluntary disable. Ordinary renewal retains the URL and
  credentials under PC-039 and preserves customer disable under PC-066. Permanent
  cancellation, URL invalidation, and replacement-delivery gates take precedence.
  Never publish superseded or revoked credentials through this policy. Without a
  trustworthy complete current configuration, report temporary unavailability
  rather than a misleading successful partial list, following PC-081.
- **Rationale discussed:** Keep the familiar node list and current status available
  through ordinary renewal or eligible resume. The accepted trade-off is that
  inactive nodes remain visible and connection attempts fail where cutoff has
  taken effect. Denying downloads would not revoke credentials already imported.
- **References:** PC-028/PC-039/PC-042/PC-066/PC-072-PC-075/PC-078-PC-081;
  D05/D09/D11; A15/A20-A22; constitution II/VII.
- **Observable implications:** Refresh after expiry, exhaustion, or customer
  disable returns the complete current list with the correct inactive reason;
  it does not restore access or erase usage. Successful eligible renewal retains
  the same URL; an existing customer disable still requires eligible resume.
  Permanently invalidated URLs do not regain download access through this rule.
- **Not settled:** Owner/security restrictions and exact invalid-URL responses.
  No HTTP implementation, client refresh behavior, or storage design is selected.

### PC-083 — Owner prepares shared routing infrastructure

- **Accepted:** 2026-09-28, answer to Q-072: "yes ofcourse i would configure them."
- **Behavior:** The store owner prepares the shared panel inbounds/listeners,
  country outbounds, and routing policy for launch. Shopvpn manages independent
  subscription credentials and their intended route assignments within that setup.
  Subscription creation, renewal, replacement, and cancellation must not rewrite
  shared routing policy, clone country outbounds, add public listeners, or disturb
  unrelated subscribers' routes. Shopvpn creation/editing of shared routing
  infrastructure and generation of administrator-applied shared configurations
  are deferred from this feature's launch scope.
- **Required result:** A-US/A-DE/A-RU still must reach their respective intended
  outbounds through A's one REALITY inbound. Remarks and flags are not evidence
  of correct egress. Validate the prepared setup against supported versions in
  controlled non-production checks before claiming it meets this requirement.
- **Rationale discussed:** Keep subscriber lifecycle operations from taking
  ownership of shared networking configuration. The accepted trade-off is owner
  preparation and maintenance when adding countries/routes, with less automation.
- **References:** PC-001-PC-003/PC-008-PC-011; R03/R04; D04; A02/A21;
  S02/S03; F-024; constitution I/V/VI.
- **Observable implications:** The acceptance fixture uses owner-prepared shared
  infrastructure, delivers each intended egress, and leaves unrelated routes
  intact across subscription lifecycle operations. Adding subscribers does not
  multiply shared country outbounds or public listeners. A capability mismatch
  must be surfaced for resolution rather than silently changing shared rules
  or dropping the required egress behavior.
- **Not settled:** Routing syntax, credential naming conventions, regex support,
  API methods, readiness-check mechanism, and actual deployed-version feasibility.
  These remain planning or controlled-evidence questions, not approved designs.

### PC-084 — Owner may settle an unrecoverable usage gap at the store's expense

- **Accepted:** 2026-09-28, answer to Q-073: "yes i agree with you."
- **Scope:** An affected composite subscription has intact entitlement and
  lifecycle history but an unrecoverable consumption gap, such as an unexpected
  panel counter reset. This is not general permission to restore missing purchase,
  payment, token, or revocation history from assumptions.
- **Behavior:** After attempts to recover missing usage, the store owner may
  explicitly approve a usage-gap settlement in web admin. Preserve all confirmed
  consumption and subtract any additional reliably recovered consumption. The
  store absorbs the remaining unmeasured usage; retain the purchased allowance
  and original expiry. Do not grant a fresh full allowance, erase known usage,
  estimate a customer charge, or create customer debt.
- **Pending and recovery:** Until settlement, preserve the uncertainty and apply
  PC-018's existing grace/suspension rules without restarting the grace clock.
  A responding panel alone cannot trigger recovery while history is unresolved.
  After settlement, resume only when current metering is trustworthy for all
  required children, allowance and time remain, and no customer disable,
  cancellation, revocation, or other restriction prohibits access. Remote enable
  remains pending until confirmed. Ordinary fully reconciled outage recovery
  under PC-022 remains automatic; this resolution requires explicit owner action.
- **Evidence and audit:** Record the subscription, gap and available evidence,
  reason, responsible owner, accepted financial risk, and outcome. The historical
  gap remains explicitly unknown, never relabeled as measured zero. Customer
  usage displays must not claim exact historical consumption; they may show the
  allowance available after the settlement as such. No constitutional exception
  or permission to fabricate evidence is approved.
- **Rationale discussed:** Restore eligible service without indefinite suspension
  or penalizing customers for lost panel evidence. The accepted trade-off is owner
  intervention and potentially unmeasured consumption borne by the store.
- **References:** PC-004/PC-018/PC-019/PC-022/PC-023/PC-034/PC-035;
  D08; A09/A11/A13/A16; F-025; constitution II/IV/VII.
- **Observable implications:** A 50-GiB entitlement with 20 GiB confirmed used
  and no additional recoverable usage may resume with 30 GiB remaining and its
  original expiry after explicit owner settlement and eligibility checks. Any
  additional reliably recovered usage reduces that remainder. Known exhaustion
  or expiry cannot be reversed through this action. Audit and usage history
  retain the gap and the commercial decision; a reset alone never replenishes
  the subscription or automatically authorizes recovery.
- **Not settled:** Counter-reset detection, evidence retrieval, reconciliation
  algorithms, storage, and general recovery from lost entitlement/lifecycle
  history remain planning or separate product questions.

### PC-085 — Initial deployment uses A with five intended outbound choices

- **Accepted:** 2026-09-28, response to Q-074: "for launch i would only use one
  server(server A) and i wont use the two other example servers B and C"; the
  user describes five different outbounds and asks whether these yield five nodes.
- **Behavior:** The intended initial live deployment uses A only, with five
  intended outbound choices. B and C are not required live launch servers.
  Under the confirmed independent-credential model, representing those choices
  as five real exported nodes requires five independently identified/routed
  credentials per subscription on A's prepared inbound. Five server-side
  outbounds alone do not automatically create five customer-visible nodes.
- **Boundary:** This is the initial deployment shape, not a hardcoded maximum,
  a single-panel-only feature restriction, or removal of the existing multi-panel
  six-node acceptance fixture. PC-001-PC-003 remain preserved. Five nodes sharing
  one public entry address do not provide five independent entry-IP failure domains.
- **Rationale:** Match the user's actual launch infrastructure while preserving
  the feature's confirmed generality and independent-credential routing model.
- **References:** BC-003; PC-001-PC-003/PC-083; R02-R06; S02-S04;
  F-024; X-004.
- **Observable implications:** The launch configuration can represent five
  distinct node choices on the same prepared inbound and shared allowance.
  The controlled multi-panel fixture remains required evidence rather than a
  demand to operate B and C in the initial live store.
- **Not settled:** The five route destinations/remarks, actual prepared settings,
  and supported-version verification. No deployed topology has been inspected.

### PC-086 — Launch must support continuity on a replacement VPN server

- **Accepted:** 2026-09-28, response to Q-074 asks how to buy another VPS and let
  customers continue using their subscription "while their data usage and expiry
  remain the same," targeting an equivalent inbound through the replacement
  panel's management API. This rejects blanket migration deferral in REC-074.
- **Required outcome:** Provide a launch path for the owner to replace the VPN
  server serving existing subscriptions with an owner-prepared equivalent server
  and inbound. Continue the same customer subscription and subscription URL,
  preserving shared allowance, accrued usage, original expiry, ownership, and
  applicable access restrictions. Replacement is not a new purchase or renewal
  and must not reset confirmed consumption or grant a fresh validity term.
- **Scope:** The requested case is restoration of equivalent service after
  entry-server filtering/failure. It does not approve arbitrary additions/removals,
  different country/protocol offers, automatic failover, or a general topology
  editor. PC-083's owner responsibility for preparing shared infrastructure remains.
- **Customer continuity:** Updated configuration must describe the replacement
  VPN destination and its actual required settings. Customers need a successful
  refresh of their still-reachable subscription URL to receive changed connection
  details; this is not a promise of moving existing sessions or making an
  unreachable download endpoint usable merely by changing an API address.
- **Rationale:** The expected filtering scenario makes equivalent server
  replacement essential to honoring existing subscriptions. A blanket deferral
  would leave this launch need unmet. The database/API-address suggestion is a
  feasibility question, not approval to overwrite panel identities or accounting.
- **References:** BC-003; PC-004/PC-005/PC-083-PC-085; D08/D11/D13/D14;
  A24; S03/S04/S11; F-026; X-004; constitution II/IV/V/VI/VII.
- **Observable implications:** An existing subscription continues on the equivalent
  replacement with the same URL and expiry, and confirmed pre-replacement usage
  remains consumed. The five intended routes remain represented. Retired credentials
  and unobserved usage retain explicit recovery/cleanup responsibility. Correctness
  cannot be established by changing the panel row's API address alone.
- **Not settled:** Old-server cutoff versus availability during migration, unknown
  old usage and subsequent exposure, credential reuse/rotation, batch scope,
  completion/failure timing, and customer refresh behavior. These requirements
  do not select storage, worker location, API methods, or migration algorithms.

### PC-087 — Owner may authorize emergency cutover before old-server revocation

- **Accepted:** 2026-09-28, answer to Q-075: "yes."
- **Behavior:** When the old server's management API is unreachable, the owner
  may explicitly authorize emergency cutover to an equivalent, fully ready
  replacement after reviewing affected subscriptions, last-confirmed usage, and
  old-server uncertainty. Current metering on the replacement must be trustworthy.
  Preserve known usage, shared allowance, expiry, and independent restrictions.
  This is not automatic failover or an automatic waiver after an API failure.
- **Old-server obligations:** The store accepts exposure to unmeasured old-server
  consumption. Preserve unknown history and confirmed consumption; do not invent
  a final zero reading. Retain old identities, available meter evidence, and
  pending revocation/cleanup, and continue reconciliation when possible. Attribute
  confirmed usage once; PC-034's store-absorbed-overrun policy remains. An entry IP
  filtered from some customers is not evidence that every old credential is revoked.
- **Explicit uncertainty-policy qualification:** After this owner-authorized
  retirement, missing old-server readings alone do not suspend the replacement
  under PC-018. The retired server remains an unresolved exposure/cleanup
  obligation rather than a required current-serving meter. Current required
  replacement meters still follow the five-minute rule. This does not declare
  the retired server's usage fresh or its cleanup complete.
- **Restriction precedence:** The action cannot clear customer disable, known
  expiry/exhaustion, cancellation, or other independent restrictions. It does not
  bypass PC-043's revocation-before-delivery gate for leaked-access replacement.
  Where the old management API is reachable, collect usage and seek confirmed
  revocation; filtering the VPN entry address does not establish API unreachability
  from the subscription manager's location.
- **Rationale discussed:** Restore service without waiting indefinitely for an
  unreachable server. The accepted trade-off is possible simultaneous access on
  old and replacement servers and unknown additional consumption borne by the
  store, with no guaranteed finite bound while old access remains uncontrolled.
- **References:** PC-004/PC-018-PC-023/PC-034/PC-043/PC-084-PC-086;
  D02/D08/D14; A16/A17/A24; constitution II/IV/VII.
- **Observable implications:** With old A unreachable and an eligible fully ready
  A' available, an explicitly approved cutover can restore service without claiming
  old revocation. Old A's missing samples alone no longer trigger suspension of A'.
  Missing required A' readings still trigger the ordinary stale-usage policy.
  Old cleanup and usage uncertainty remain visible and survive retries/restarts;
  revoked or expired subscriptions are not re-enabled by the move.
- **Not settled:** New versus reused credentials, batch scope, completion/failure
  timing, and refresh support. No worker, API sequence, or storage design selected.

### PC-088 — Fresh moved-node credentials with a stable subscription URL

- **Accepted:** 2026-09-28, answer to Q-076: "yes."
- **Behavior:** Equivalent server replacement issues fresh authentication
  identities for every moved child: new UUIDs for VLESS/VMess and new protocol
  passwords for Trojan. Preserve the subscription URL, intended node choices and
  remarks, ownership, shared allowance, accrued usage, original expiry, and
  applicable restrictions. Credentials on nodes outside the replacement remain
  unchanged.
- **Delivery and retirement:** The updated payload contains the new connection
  settings and credentials only after the applicable readiness/cutover conditions
  are met; do not publish an incomplete replacement as a completed move. Customers
  refresh their existing subscription URL. Old imported credentials must not
  authenticate on the replacement. Fresh identities do not themselves revoke
  old-server access; PC-087's explicit emergency authorization and retained
  identities, history, and cleanup obligations continue to apply.
- **Separate lifecycle:** This owner operation does not consume, restart, or
  clear the customer's existing 24-hour leaked-access replacement cooldown. It
  does not repair a leaked subscription URL, which remains unchanged. PC-039's
  identity-preserving ordinary renewal behavior remains unchanged.
- **Rationale discussed:** Avoid carrying retired-server credentials forward
  as valid credentials on the replacement, while preserving subscription
  continuity. The accepted trade-off is that manually copied configurations and
  unrefreshed apps cannot access the replacement with the old settings/secrets.
- **References:** PC-039-PC-044/PC-065/PC-086/PC-087; D08/D11/D14;
  A14/A17/A21/A24; constitution II/IV.
- **Observable implications:** Replacing A with A' gives all five moved nodes
  fresh credentials while the customer refreshes the same URL. Remaining
  allowance, expiry, and usage history are preserved; existing customer disable
  remains effective. Old credentials fail authentication on A', even if access
  on unreachable old A remains pending revocation. Any unmoved nodes retain their
  credentials, and the customer's replacement cooldown timestamp is unchanged.
- **Not settled:** Batch selection, per-subscription versus whole-batch
  completion/failure, migration timing, and refresh support. No API, generation,
  or accounting representation is selected.

### PC-089 — Bulk server replacement with independent subscription completion

- **Accepted:** 2026-09-28, answer to Q-077: "yes."
- **Behavior:** The owner can select one, several, or all affected subscriptions
  for equivalent server replacement in web admin. Preview the actual subscriptions
  and old-to-replacement server mapping before authorization. If selecting by
  customer, make included subscriptions clear; multiple subscriptions remain
  separate entitlements. Preserve ownership, allowance, history, expiry,
  restrictions, and any required explicit PC-087 emergency-cutover approval.
- **Completion:** Each subscription switches independently once its complete
  intended replacement set is ready and applicable cutover conditions are met.
  All five moved nodes must be ready for each A-only launch subscription. A
  failed or pending subscription must not block or roll back other completed
  subscriptions. Report individual outcomes and partial batch completion honestly.
- **Recovery:** Retrying unfinished work must not create another migration or
  issue fresh credentials again for subscriptions already completed merely
  because they were selected in the same batch. Incomplete replacement must not
  be presented as a completed move or published as a complete replacement list.
- **Rationale discussed:** Restore affected subscriptions promptly without one
  owner operation per customer or making all customers wait for one failure.
  The accepted trade-off is temporarily mixed outcomes requiring monitoring and
  recovery of the unsuccessful subscriptions.
- **References:** PC-009/PC-010/PC-054/PC-086-PC-088; D10/D14;
  A03-A06/A24; constitution II/IV/VII.
- **Observable implications:** Of 100 selected subscriptions, 99 may complete
  while one remains pending with a visible reason and recovery path. A retry
  recovers the unfinished subscription without moving the 99 again. The UI does
  not label the whole batch complete while an included subscription is pending.
  One hundred is an example, not a batch-size or customer limit.
- **Not settled:** Migration timing, eligibility of historical records, and
  customer refresh notifications. No concurrency, transaction, queue, or retry
  algorithm is selected.

### PC-090 — Fifteen-minute replacement benchmark with overdue recovery

- **Accepted:** 2026-09-28, answer to Q-078: "yes."
- **Target:** Under supported normal operating conditions, complete equivalent
  server replacement within 15 elapsed minutes of owner authorization for up to
  150 eligible subscriptions with five moved nodes each: 750 replacement
  credentials. The replacement server, equivalent inbound/routes, and required
  access must already be prepared and available. VPS purchasing/setup time is
  excluded; waiting within the authorized operation is included. Retries and
  process restarts do not restart the original timer.
- **Completion meaning:** Every still-eligible selected subscription has its
  full ready replacement set, trustworthy current metering, and updated
  configurations available through its unchanged URL under applicable access
  restrictions. This does not mean customers have refreshed their apps or
  existing sessions have moved. PC-087 may permit an unavailable old server;
  outstanding old cleanup remains separately pending, never falsely confirmed.
  Do not override expiry, exhaustion, cancellation, or customer restrictions to
  meet the target. Other subscriptions' accounting and enforcement continue.
- **Overdue behavior:** At 15 minutes, unfinished work is visibly overdue and
  requires owner attention in web admin plus an attempted Telegram owner
  notification. Continue bounded, repeat-safe recovery and retain unresolved
  obligations. Do not automatically roll back completed subscriptions, discard
  pending work, or reset quota/expiry. This is a completion target and escalation
  threshold, not a new purchase's cancellation/refund deadline.
- **Capacity boundary:** The 150-subscription benchmark reflects the launch
  campaign; it is not a cap on customers, active subscriptions, or bulk selection.
  Larger batches remain supported with progress visible, but a universal
  15-minute guarantee for arbitrary batch sizes is not approved. Their operating
  envelope requires measurement. The benchmark does not replace the multi-panel
  fixture or establish an active-connection capacity limit.
- **Rationale discussed:** Set an observable restoration expectation for an actual
  planned cohort. The accepted trade-off is up to 15 minutes after preparation
  under supported normal conditions rather than an instant-restoration promise.
- **References:** PC-020/PC-046/PC-056/PC-085-PC-089; D02/D13/D14;
  A16/A24; S09; E-002/E-004; constitution VI/VII.
- **Observable implications:** A controlled 150-subscription/five-node check
  measures from authorization through complete replacement availability, including
  internal waiting. An unfinished operation at 15 minutes is overdue and escalated
  while successful subscriptions remain moved and pending work stays recoverable.
  Normal accounting/enforcement targets continue to apply during the check.
- **Not settled:** Supported infrastructure/load and measured results. This is
  an accepted product target, not a passing benchmark or architecture choice.

### PC-091 — Notify customers to refresh after their replacement is ready

- **Accepted:** 2026-09-28, answer to Q-079: "yes."
- **Behavior:** After each subscription's replacement is complete and its updated
  configuration is retrievable, attempt a notification to its owning customer
  through the main-store Telegram bot. Identify the subscription, explain that
  its URL is unchanged and the replacement has not reset allowance or expiry,
  and tell the customer to refresh it in their VPN app. Do not wait for unrelated
  subscriptions in the batch to finish. Respect actual restrictions: migration
  completion must not imply usable access for a disabled or otherwise ineligible
  subscription.
- **Delivery failure:** A blocked bot, Telegram outage, or failed notification
  does not undo the replacement or prevent its URL from serving ready configurations.
  Keep status and refresh guidance available when the customer opens their
  subscription in the bot. Track failed/uncertain notification delivery separately,
  use bounded delivery recovery, and expose unresolved notification failures to
  the owner without repeating migration. Avoid duplicate notices where delivery
  is known, without claiming exactly-once external message delivery.
- **Evidence boundary:** Sending a notification does not prove that the customer
  read it or refreshed their app. No silent client update or movement of existing
  sessions is promised.
- **Rationale discussed:** Customers with cached configurations need refresh
  guidance to benefit from restored service. The accepted trade-off is an
  additional service message; customers unable to receive it may stay on old
  settings until independently refreshing or checking the bot.
- **References:** PC-007/PC-049/PC-086-PC-090; D10/D11/D14;
  A20/A24/A27; constitution III/VII.
- **Observable implications:** A subscription completing before the rest of its
  batch can receive its own refresh notice. Simulated notification failure leaves
  ready replacement configurations available, records the notification failure,
  and does not reprovision credentials. The customer's bot view still provides
  completion status and refresh guidance.
- **Not settled:** Wording/localization and notification transport/retry details
  belong to planning; no real customer messages were sent in this interview.

### PC-092 — Existing configured payment options with plan restrictions

- **Accepted:** 2026-09-29, answer to Q-080: "yes. lets go with your recommendation."
- **Behavior:** Initial composite purchases, full-plan renewals, and trial-to-paid
  conversions use the store's existing configured Telegram payment options.
  When the selected plan allows wallet payment, apply available wallet credit
  first up to the discounted price. Pay any remainder through an existing external
  method enabled and permitted for that plan and amount. A customer with no wallet
  balance may pay the full amount externally where allowed. A separate wallet
  top-up is not mandatory; adding a new gateway is outside this feature.
- **Restrictions:** Apply the selected composite plan's payment restrictions to
  renewal/conversion as well as initial purchase, plus enabled-method and applicable
  minimum-amount checks. Do not copy the inspected legacy renewal bypass. General
  wallet-top-up restrictions remain separate and do not implicitly authorize a
  method for purchase/renewal. If no permitted method covers the payable remainder,
  explain that checkout cannot proceed and do not retain a wallet debit for an
  unpayable order.
- **Money and authority:** Preserve accepted tier/coupon pricing and actual-paid
  wallet refunds. Method availability does not approve unsafe verification,
  client-reported success, duplicate settlement, or unauthorized manual approvals.
  Affected payment paths must meet the constitution. Inability to verify a configured
  integration is an issue to resolve, not permission to grant unverified service.
- **Rationale discussed:** Keep familiar payment options and allow spending refund
  wallet credit without forcing a top-up step. The accepted trade-off is more
  payment paths to validate, including combined wallet/external payments, compared
  with wallet-only checkout.
- **References:** PC-006/PC-007/PC-013/PC-024/PC-050-PC-052/PC-061;
  D07/D09/D10; A25/A28; F-014-F-016/F-027; constitution I/II/III/VII.
- **Observable implications:** An eligible order priced at 100 with 30 permitted
  wallet credit uses 30 from the wallet and an allowed external method for 70.
  Full permitted wallet coverage requires no external payment. A method forbidden
  by the selected plan cannot be used for its renewal merely because globally
  enabled. An unpayable remainder does not strand a wallet debit. Actual-paid
  failed-fulfillment refunds continue to follow PC-013.
- **Not settled:** Manual payment-approval interfaces, late-payment/cancellation
  policy, gateway verification details, and required conversion/rounding evidence.
  No runtime gateway configuration or secrets were inspected.

### PC-093 — Owner manual payment decisions through Telegram and web admin

- **Accepted:** 2026-09-29, answer to Q-081: "yes."
- **Behavior:** The main-store owner can review and approve/reject manual
  composite purchase/renewal payment requests through both the existing Telegram
  receipt workflow and web admin. Composite payment decisions are owner-only;
  staff or customers cannot authorize them. Verify payment evidence, beneficiary,
  order, amount, method, and tenant before recording confirmed payment. Retain
  the authorized actor and decision audit. A receipt upload or customer assertion
  alone does not establish verified settlement.
- **Repeat safety and outcomes:** Competing/repeated decisions through either
  interface must not duplicate financial or provisioning effects. Verified payment
  starts the accepted fulfillment/renewal deadline regardless of interface.
  Approval must not claim completed provisioning before the full agreed
  readiness/delivery gate is satisfied.
- **Interface scope:** This settles PC-010's explicitly open payment-approval
  boundary. Composite plan configuration and other owner subscription management
  remain web-admin-only. Preserve unrelated general wallet-top-up and legacy
  receipt workflows and permissions under PC-003. This does not approve composite
  reseller sales or manual off-catalog issuance.
- **Rationale discussed:** Let the owner act where receipts arrive while retaining
  web-admin visibility. The accepted trade-off is validating two financial control
  surfaces for authority, audit, and duplicate settlement instead of one.
- **References:** PC-009/PC-010/PC-012/PC-013/PC-037/PC-092;
  D07/D10; A03/A19/A28; F-027/F-028; constitution II/III/VII.
- **Observable implications:** The same eligible receipt can be decided by the
  authenticated owner through either interface. Concurrent approvals settle and
  fulfill once. A non-owner staff member permitted to process legacy orders cannot
  thereby approve a composite order. Payment confirmation, complete delivery,
  and any pending provisioning remain visibly distinct.
- **Not settled:** Exact UI, verification implementation, receipt visibility for
  staff, and shared operation mechanics belong to planning or separate scope
  questions; existing source guards do not prove these new behaviors.

### PC-094 — Cancelled checkouts retain cancellation and credit later verified money

- **Accepted:** 2026-09-29, answer to Q-082: "yes."
- **Cancellation scope:** Customers may cancel their own composite initial
  purchase, renewal, or trial-conversion checkout while full payment remains
  unverified. End that checkout without changing an existing subscription.
  Restore any wallet amount already deducted once; under normal application/
  database conditions make it usable within 60 seconds of accepted cancellation.
- **Later payment:** If its corresponding external payment is subsequently
  validly verified, credit 100% of the verified external amount to the same
  customer's store wallet once. Under normal application/database conditions,
  make it usable within 60 seconds of verification, including delayed gateway
  callbacks or owner receipt verification. Keep the checkout cancelled; do not
  create a subscription, renew/convert an existing one, or resurrect provisioning.
- **Evidence and recovery:** Link the cancelled order, payment evidence, and
  wallet credit for reconciliation and show the customer the outcome. Duplicate
  callbacks/approvals cannot credit twice. A previously restored wallet deduction
  is not credited again as newly received external money. Unmatched, invalid, or
  amount-mismatched evidence stays visible for authorized investigation; do not
  silently discard it or invent a valid payment.
- **Boundary:** Cancellation must be accepted before full payment verification.
  Already verified in-flight renewal cancellation continues under PC-073-PC-075.
  Verified initial purchases already provisioning are a separate unresolved case.
  A customer choosing to order again makes a fresh purchase at then-current
  prices, offers, and eligibility; the cancelled quote is not silently reinstated.
- **Rationale discussed:** Honor cancellation while preserving genuine received
  money as usable credit. The accepted trade-off is needing a fresh checkout if
  the customer still wants service and receiving store credit under PC-013 rather
  than an automatic original-method cash refund.
- **References:** PC-013/PC-037/PC-048/PC-073-PC-075/PC-092/PC-093;
  D07/D10; A03-A06/A25/A28; F-029; constitution II/III/VII.
- **Observable implications:** A checkout priced at 100 with 30 deducted from the
  wallet returns 30 upon accepted cancellation. Later verification of its external
  70 credits 70 once, while the order remains cancelled and no service is issued
  or renewed. Each restoration/credit meets its own normal-condition 60-second
  target. Repeated late callbacks do not increase the credit or restore the order.
- **Not settled:** Verified initial-fulfillment cancellation, invoice/quote expiry,
  amount-mismatch remediation, and provider conversion/rounding evidence. Gateway,
  state-machine, and storage implementation remain deferred.

### PC-095 — Customer cancellation of paid initial provisioning

- **Accepted:** 2026-09-29, answer to Q-083: "yes."
- **Eligibility:** Customers may cancel their own verified paid initial composite
  purchase through explicit confirmation in Telegram while initial fulfillment
  is incomplete. Complete subscription readiness and URL availability, rather
  than notification reading or first VPN use, determine that boundary.
- **Sequence:** Let already-running provisioning reach a clean outcome or the
  original 15-minute deadline from verified payment, whichever comes first.
  Show cancellation pending during that bounded wait; cancellation does not
  restart the deadline. Once cancellation is accepted, do not make a new URL or
  configuration available to the customer even if remote creation succeeds later.
- **Final phase:** At that outcome/deadline, cancel the order, refund 100% of
  the actual verified payment to the store wallet once without usage proration,
  and revoke/clean up created credentials. Under normal application/database
  conditions, credit is visible and spendable within 60 seconds of the final-stage
  decision, independently of cleanup or notifications. Under supported normal
  panel conditions, invalidate any issued token and confirm every created
  credential rejects fresh authentication within 60 seconds of final-stage start.
  Native existing-session handling remains unchanged.
- **Uncertainty and escalation:** Unknown remote outcomes remain unknown. Retain
  identities and pending cleanup rather than claiming completed cutoff. At 15
  minutes from final-stage start, unresolved work needs owner web-admin attention,
  an attempted owner Telegram notice, and a customer-visible pending/support
  outcome. Continue bounded recovery; retries/restarts do not reset timers,
  duplicate refunds, or let late remote success deliver/reactivate the order.
- **Boundary:** If complete fulfillment and URL availability preceded cancellation
  acceptance, PC-072's fulfilled-subscription cancellation with no automatic
  unused-service refund applies, subject to previously accepted refund exceptions.
  PC-073-PC-075 still govern verified in-flight renewal, and PC-094 governs
  checkout cancellation before full payment verification.
- **Rationale discussed:** Allow withdrawal from an undelivered initial purchase
  using the same bounded sequential approach as renewal. The accepted trade-off
  is waiting for the provisioning outcome or remaining original window before
  final refund, rather than immediate credit at the cancellation request.
- **References:** PC-011-PC-014/PC-048/PC-049/PC-068/PC-072-PC-075/PC-094;
  D10/D14; A03-A06/A17/A28; F-029; constitution II/IV/VII.
- **Observable implications:** Payment verified at 12:00 and cancellation accepted
  at 12:14 keep the 12:15 provisioning deadline. If still unresolved, final
  cancellation starts then and normal-condition credit is usable by 12:16;
  unresolved cleanup is escalated at 12:30. No late result delivers the cancelled
  order. If provisioning resolves earlier, final-phase clocks begin earlier.
- **Not settled:** Remote interruption/coordination mechanics and measured timing
  evidence belong to planning/validation. This does not certify safe cancellation
  in the existing handlers or select an implementation algorithm.

### PC-096 — Restore coupon uses for failed or eligible cancelled orders

- **Accepted:** 2026-09-29, answer to Q-084: "yes."
- **Behavior:** A pending composite checkout holds one coupon use; permanently
  consume it only for a successfully fulfilled order whose purchase/renewal is
  retained. Release the held/consumed use once if initial fulfillment or renewal
  fails, checkout cancellation is accepted before full payment verification, or
  paid initial cancellation is accepted before fulfillment and the required
  refund is settled. For PC-073's cancellation requested during paid renewal,
  restore that renewal's coupon use upon settlement of its full cancellation
  refund even if the remote renewal completed before final revocation.
- **Limits and repeat safety:** Restore applicable overall and per-customer use
  allowances for the order once. Multiple child nodes do not consume multiple
  uses. Retries, repeated refund/cancellation, and callbacks cannot release twice.
  Late verified payment credited under PC-094 cannot consume the cancelled
  order's coupon again. Where no payment was due/received, release on the terminal
  failed or accepted cancellation outcome; this does not itself approve zero-price
  fulfillment.
- **Boundaries:** Restoration does not extend expiry, enable a disabled code,
  override product/category/amount restrictions, or reserve future availability
  for the same customer. A new checkout must meet current eligibility and capacity.
  Later cancellation of an already-fulfilled subscription under the no-refund
  policy does not restore its coupon. Discretionary support credit does not
  automatically restore uses. General test eligibility and the 150-user campaign
  history/cap remain independent.
- **Rationale discussed:** Avoid spending a limited-use benefit on a failed or
  withdrawn order covered by full-refund rules. The accepted trade-off is pending
  orders occupying capacity temporarily and another eligible checkout being able
  to claim capacity after release.
- **References:** PC-013/PC-037/PC-051/PC-052/PC-073-PC-075/PC-094/PC-095;
  D07/D09/D10; A03-A06/A25/A28; F-015/F-029; constitution II/VII.
- **Observable implications:** A failed one-use coupon order restores its use
  once when its required refund settles; repeated callbacks do not increase the
  configured limit. A cancelled pending-renewal full refund restores that renewal's
  use. A fulfilled subscription cancelled later does not. An expired coupon stays
  expired even after capacity is restored, and campaign places are not reopened.
- **Not settled:** Reservation/release mechanics, pending-quote duration, and
  zero-price fulfillment eligibility remain planning or separate product choices.

### PC-097 — Valid discounts may produce zero-price normal catalog fulfillment

- **Accepted:** 2026-09-29, answer to Q-085: "yes."
- **Behavior:** If valid configured discounts reduce the total price of an
  eligible normal composite catalog purchase, renewal, or trial conversion to
  zero, fulfill it after the customer's final checkout confirmation and current
  price/discount/ownership validation. Deduct no wallet credit, request no external
  payment, and do not fabricate a paid transaction. Record zero amount and actual
  discount/authorization evidence; repeated confirmation cannot duplicate issuance.
- **Entitlement:** Discounts affect price only. Preserve the full selected
  allowance/duration, complete node gate, usage/carryover, restrictions, identity
  rules, and other accepted lifecycle behavior. Catalog fulfillment does not use
  or reset `test_used`, claim a campaign place, reopen its cap, or erase prior
  trial/campaign history. An eligible zero-price normal renewal can convert a
  trial without renewing test eligibility. This does not approve zero-base-price
  offers, arbitrary owner grants, or another complimentary issuance flow.
- **Timing and failure:** Apply the same 15-minute complete-fulfillment deadline
  from accepted final confirmation with validated zero price. Validity starts at
  full readiness and URL availability. Failure or eligible cancellation preserves
  cleanup/recovery and releases coupon use under PC-096. Actual payment of zero
  cannot create a positive monetary refund. Coupon restrictions/limits remain
  required.
- **Rationale discussed:** Honor legitimate configured promotions without a
  meaningless payment step or treating a normal catalog order as a test. The
  accepted trade-off is full normal-plan benefits being granted free under eligible
  discounts, making configured eligibility and usage limits consequential.
- **References:** PC-008/PC-011-PC-016/PC-051/PC-052/PC-055-PC-061/
  PC-092/PC-095/PC-096; D07/D09/D10; A03-A06/A25/A28; F-030;
  constitution II/III/VII.
- **Observable implications:** An eligible 100%-discount normal checkout performs
  no debit/payment request and receives the full selected plan after complete
  fulfillment. Its 15-minute clock starts at validated confirmation; failure
  releases the coupon once and credits no nominal undiscounted money. Test usage
  and permanent campaign recipient/count history are unchanged.
- **Not settled:** Accepted quote lifetime and later catalog/coupon changes are
  separate product choices. No lifecycle/storage algorithm or passing zero-price
  acceptance result is approved here.

### PC-098 — Honor confirmed quotes until completion, cancellation, or rejection

- **Accepted:** 2026-09-29, answer to Q-086: "yes."
- **Behavior:** At final customer confirmation, validate current price,
  tier/coupon eligibility and capacity, ownership, and selected offer. Hold one
  permitted coupon use and preserve the accepted order's quoted price/reductions,
  selected allowance, duration, and intended node choices. Later price, tier,
  coupon, or catalog edits affect new checkouts. An already accepted held coupon
  use remains honored if its code subsequently expires or is disabled; this does
  not authorize new uses after expiry/disable.
- **Lifetime:** The quote remains until completion, accepted customer cancellation,
  or authorized owner rejection. Add no new general unpaid-order or manual-receipt
  expiry timer at launch. Payment methods retain their own invoice validity and
  verification rules. Expiry of an external invoice alone does not cancel the
  parent checkout, release held wallet/coupon value, or authorize payment. Another
  currently permitted payment attempt may be made against the same pending quote,
  without duplicate settlement.
- **Boundaries:** Live usage, remaining validity, unused-data eligibility, and
  renewal carryover continue to change while payment is pending. PC-038's
  verified-payment boundary, verification/security rules, current payment-method
  availability, and applicable access restrictions remain effective. An explicit
  equivalent-server replacement is separate from a silent catalog edit and must
  preserve intended service. Terminal cancellation/rejection requires a new
  checkout using current offers and eligibility.
- **Owner rejection:** Before full payment verification, authorized owner rejection
  releases held wallet/coupon value and credits subsequently validly verified
  external money under PC-094/PC-096's treatment. Preserve the rejected outcome;
  late money does not reopen or fulfill it. This is an explicit extension beyond
  PC-094's earlier customer-cancellation scope. The owner cannot silently reprice
  an already verified payment.
- **Rationale discussed:** Honor the offer the customer accepted while paying or
  awaiting manual review. The accepted trade-off is old prices/promotions and
  coupon capacity remaining tied to pending orders until explicitly resolved.
- **References:** PC-005/PC-008/PC-025/PC-038/PC-051/PC-052/PC-086-PC-097;
  D07/D09/D10; A03/A24/A25/A28; F-015/F-031; constitution I/II/VII.
- **Observable implications:** A confirmed 100-unit quote remains 100 after a price
  increase; its allowance, duration, and intended node choices also remain the
  agreed offer. A later-expired held coupon remains honored for this order, while
  a new order cannot use it. An expired gateway invoice alone does not restore
  the held wallet/coupon or cancel the quote. Owner rejection releases holds once;
  verified later money becomes wallet credit once without provisioning. Renewal
  usage/time continue advancing while the quote is pending.
- **Not settled:** Quote storage, offer snapshots, and invoice processing belong
  to planning. Treatment of two distinct real payments for one retained checkout
  is a separate product question; a repeated callback is already prohibited from
  duplicating settlement by the constitution.

### PC-099 — Credit distinct extra payments without duplicating the purchase

- **Accepted:** 2026-09-29, answer to Q-087: "yes."
- **Behavior:** Settle the quoted composite purchase/renewal once. When a second
  distinct payment is independently verified as real money received for the same
  beneficiary and checkout, with its own transaction reference, expected external
  amount, and currency/unit conversion, credit the entire extra received amount to
  that customer's store wallet once. Make the credit visible and spendable within
  60 seconds of verification/recognition under normal application and database
  availability, independently of panel cleanup or notification.
- **Purchase boundaries:** The extra payment creates no second subscription,
  renewal, wallet deduction, or coupon use. It does not restart fulfillment's
  15-minute deadline or change the original verified-payment boundary governing
  carryover. A repeated notification/approval for the same transaction is not
  another receipt and creates no extra credit. A transaction already settled or
  credited cannot be claimed again through another order.
- **Verification and refunds:** Mismatched or unverifiable payments require
  investigation and cannot authorize settlement. Extra-payment credit is separate
  from the original checkout's refund obligation. If the checkout fails, refund
  its original actual paid amount once, retaining the extra receipt's credit
  without refunding that money again. Cancelled/rejected-order late payments
  follow PC-094/PC-098 and do not reopen the order.
- **Rationale discussed:** Account for every verified receipt while preserving
  the customer's single confirmed purchase. The accepted trade-off is wallet
  credit rather than an automatic return through the original payment method.
- **References:** PC-013/PC-037/PC-048/PC-051/PC-052/PC-073/PC-092-PC-098;
  D07/D09/D10; A03-A06/A25/A28; F-029/F-031; constitution II/III/VII.
- **Observable implications:** A 100-unit checkout using 30 wallet units and one
  verified external payment of 70 is funded once. A second distinct valid payment
  of 70 credits 70 to the wallet within the normal 60-second target. Replaying
  either payment notification creates nothing further. If fulfillment then fails,
  the original 100 is refunded once, in addition to the already credited extra 70;
  the extra 70 is not refunded a second time. The original fulfillment clock and
  coupon-use count remain unchanged.
- **Not settled:** Payment-ledger design, gateway reconciliation, and controlled
  duplicate-payment evidence belong to planning/verification. This does not approve
  arbitrary overpayments, underpayments, or missing payment evidence.

### PC-100 — Defer additional ad hoc complimentary composite grants

- **Accepted:** 2026-09-29, answer to Q-088: "yes ofcourse."
- **Behavior:** At launch, complimentary composite issuance remains available
  through the agreed `btn_test` flow, the 15-GiB/15-day/150-user campaign, future
  owner-defined composite test plans, and independently agreed valid-discount
  normal checkout, including eligible zero-price purchase/renewal. Defer an owner
  action that directly creates free off-catalog composites for one or many
  customers outside those flows.
- **Boundaries:** Preserve the shared existing test eligibility and permanent
  campaign recipient history/cap. Owner-only plan configuration does not itself
  authorize direct grants. Single and bulk support wallet credit remain approved
  but do not directly issue subscriptions or bypass test/campaign rules. Preserve
  affected legacy gift/manual-issuance behavior. Purchase-based referral composite
  rewards remain deferred under PC-053. This does not reinstate Q-049's rejected
  blanket deferral of complimentary composite issuance.
- **Rationale discussed:** Support the explicitly requested promotion and
  configurable tests through flows with agreed entitlement, eligibility, and
  delivery rules. The accepted trade-off is that the owner cannot push extra
  complimentary composites to an individual or selected group outside customer
  claim/checkout and the agreed test rules.
- **References:** PC-006-PC-010/PC-053-PC-064/PC-069-PC-071/PC-097;
  Q-049; D07/D10/D14; A03/A19/A27-A29; F-008/F-017/F-018;
  constitution I-III/VII.
- **Observable implications:** An eligible customer can claim an owner-configured
  composite test or the campaign, subject to their respective rules. A normal
  eligible discounted zero-price checkout still receives its selected plan.
  Composite operator management has no extra single/bulk free-grant action outside
  those flows. Bulk wallet credit does not directly create composites, reset
  `test_used`, or reopen campaign places. Legacy gift/manual-issuance behavior is
  preserved within the affected scope.
- **Not settled:** Paid purchases for another person and customer ownership
  transfer remain separate from this free-grant boundary. No new grant workflow,
  schema, implementation task, or passing acceptance result is approved here.

### PC-101 — Keep launch composite ownership with the purchasing or claiming account

- **Accepted:** 2026-09-29, answer to Q-089: "yes."
- **Behavior:** Assign a purchased composite to its authenticated main-store
  Telegram buyer and a composite test/campaign claim to its authenticated claimant.
  Keep that account as the subscription's management owner throughout launch
  renewal, trial conversion, credential replacement, and equivalent-server
  replacement. Defer checkout for another recipient and customer/store-owner
  reassignment of a composite to another customer account, including through
  existing legacy service-transfer actions.
- **Authority and money:** The assigned customer retains their approved
  self-service controls. Required refunds and extra-payment credits remain with
  the checkout's verified beneficiary. The same customer may own multiple
  separately purchased subscriptions. Possession of a URL does not confer account
  ownership or management rights. No device/concurrent-session limit or different
  handling of existing sessions is approved by this ownership boundary.
- **Recovery boundaries:** Preserve affected legacy transfer behavior. A
  store/tenant ownership change is distinct from subscription reassignment and
  cannot discard financial, test/campaign, usage, revocation, or remote cleanup
  responsibility. Lost-record/account-identity recovery is not silently authorized
  as an ownership-transfer shortcut; PC-005 and constitution IV still govern.
- **Rationale discussed:** Align payment beneficiary, test eligibility, permanent
  campaign history, management rights, and cancellation/refund responsibility with
  one authenticated customer. The accepted trade-off is no official purchase for
  another bot account or handover of composite management at launch, despite the
  legacy transfer feature.
- **References:** PC-004-PC-010/PC-050/PC-054-PC-061/PC-069-PC-075/
  PC-094-PC-100; D07/D10/D14; A19/A23/A28/A29; F-008/F-017/F-032;
  constitution I-IV.
- **Observable implications:** Initial purchase/test ownership uses the verified
  acting customer's account. After conversion, renewal, leak repair, or server
  replacement, the same customer retains management and monetary responsibility.
  A different account cannot select itself as recipient or acquire composite
  management through customer/admin legacy-transfer requests. Existing affected
  legacy transfers remain available. Merely sharing a URL does not change owner,
  test/campaign records, refund beneficiary, or management permissions.
- **Not settled:** Store/tenant destructive operations and recovery of missing
  account/lifecycle records need separate coverage. No account migration, data
  schema, or new management workflow is selected here.

### PC-102 — Owner single/batch suspension, resumption, and permanent cancellation

- **Accepted:** 2026-09-30, answer to Q-090: "yes i agree with you."
- **Authority and scope:** The authenticated main-store owner may use web admin
  to suspend, resume, or permanently cancel fulfilled paid/test composites,
  individually or in a selected batch. Preview exact affected subscriptions and
  customers and the requested action; require explicit confirmation and a reason.
  Record actor, reason, subscription, action, and pending/confirmed outcome.
  Deduplicate selected subscriptions, report each result, and do not conceal or
  undo completed results because another subscription fails. Retries do not repeat
  completed financial or lifecycle effects. Delegated staff cannot perform these
  composite actions.
- **Owner suspension:** Restrict the complete subscription's access independently
  of customer disable. Keep URL, credentials, allowance, history, and original
  expiry; account for actual consumption while remote action remains pending.
  No automatic refund or expiry extension results. Customers cannot clear the
  owner's restriction. Owner resumption clears only that restriction and enables
  access only with trustworthy usage, remaining allowance/validity, and no
  customer disable, cancellation, or other restriction. Renewal, rotation,
  server replacement, and automatic recovery do not clear owner suspension.
- **Permanent cancellation:** Explicitly confirmed owner cancellation invalidates
  the URL and revokes every child credential, cannot be resumed/renewed, and
  retains history and unresolved cleanup. Apply no automatic unused-service refund;
  separate owner-approved wallet compensation remains possible. Extend
  PC-073-PC-075 to owner cancellation during an in-flight paid renewal: let it
  resolve cleanly or reach its original 15-minute deadline, then revoke and
  refund 100% of that renewal's actual payment to the same customer's wallet once,
  without usage proration. This explicitly extends the earlier customer-only rule.
- **Timing and recovery:** Apply the established normal 60-second required-child
  access-change target per subscription and native existing-session handling.
  Final cancellation also requires URL invalidation and any required wallet credit
  under the respective normal 60-second targets. Show desired versus confirmed
  outcome. At 15 minutes of unresolved suspend/resume or final cancellation stage,
  expose owner web-admin attention, attempt the owner Telegram alert, and show
  truthful customer pending/support status when available. Preserve bounded
  recovery without restarting timers, losing obligations, or claiming completion
  from an accepted request. PC-074/PC-075 bound the separate paid-renewal wait.
- **Rationale discussed:** Give the owner enforceable service controls that
  customers and unrelated lifecycle actions cannot undo. The accepted trade-off
  is waiting for owner release while expiry continues and unused service receives
  no automatic compensation.
- **References:** PC-004/PC-009/PC-010/PC-021-PC-023/PC-066-PC-075/PC-101;
  D10/D14; A14-A19/A23/A28/A29; F-020/F-021/F-033;
  constitution I-IV/VII.
- **Observable implications:** An owner-suspended trial or paid composite retains
  its identity and expiry, and the customer's resume request cannot re-enable it.
  Owner resume cannot bypass a simultaneous customer disable or expired/exhausted
  entitlement. A bulk request reports completed and pending subscriptions
  separately without duplicate effects on retry. Owner permanent cancellation
  revokes all child credentials and invalidates the URL; a concurrently in-flight
  paid renewal receives its full actual-payment wallet refund once under the
  existing sequential rule. Missed targets and unresolved cleanup remain visible.
- **Not settled:** Account-block coupling, renewal-payment eligibility, and URL
  download behavior during owner suspension are separate dependent choices.
  This does not add an owner cancellation action for an unfulfilled initial/test
  claim or approve arbitrary entitlement editing. Architecture and performance
  evidence remain planning/verification work.

### PC-103 — Shop-account blocks do not automatically restrict VPN service

- **Accepted:** 2026-09-30, answer to Q-091: "oh yes we'll go with your recommendation."
- **Behavior:** Keep shop/bot account blocking as the existing interaction and
  eligibility restriction. It does not automatically create or clear a composite
  service restriction, invalidate an otherwise valid URL, rotate credentials, end
  an entitlement, extend expiry, or issue a refund. Use PC-102's explicit owner
  service action, individually or in a selected batch, when VPN access itself
  should be restricted. Unblocking an account does not resume a separately
  owner/customer-disabled, exhausted, expired, cancelled, or otherwise restricted
  subscription.
- **Outage and authority boundaries:** A store-admin account block is distinct
  from a customer blocking the Telegram bot or a Telegram/startup/notification
  failure. None of these events by itself authorizes VPN suspension/cancellation.
  Existing subscription URL/state gates still apply. Preserve blocked-account
  restrictions on shop interaction and applicable purchase, test, and management
  eligibility; no new bypass is approved. Staff account-block permissions do not
  confer owner-only composite service powers.
- **Continuing responsibilities:** Required payment verification, owed wallet
  credits/refunds, usage accounting, expiry enforcement, and cleanup continue when
  the customer cannot interact with the bot. Account blocking does not erase
  obligations, restart deadlines, or override accepted fulfillment/delivery gates.
- **Rationale discussed:** Make the consequence of each action explicit rather
  than cutting off purchased/test service as a hidden result of shop blocking.
  The accepted trade-off is a separate explicit service action when both shop
  interaction and VPN access need restriction.
- **References:** PC-004/PC-009/PC-010/PC-050/PC-066-PC-075/PC-081/PC-082/
  PC-098/PC-101/PC-102; D10/D11/D14; A14-A20/A23/A27-A29;
  F-015/F-033; constitution I-III/VII.
- **Observable implications:** Blocking an account leaves its otherwise active
  composite usable under its existing allowance/expiry, and does not rotate or
  invalidate its otherwise valid URL. An owner must separately suspend/cancel
  to request credential cutoff. Unblocking an owner-suspended customer does not
  clear that service restriction. Required refunds, enforcement, and pending
  cleanup continue while bot interaction is blocked. A bot-account block alone
  is never reported as revocation of already imported credentials.
- **Not settled:** Owner-suspension download behavior and renewal-payment
  eligibility remain dependent product choices. This approves no endpoint,
  permission schema, or worker architecture.

### PC-104 — Owner suspension serves status entries without real configurations

- **Accepted:** 2026-09-30, answer to Q-092: "yes i agree."
- **Behavior:** Once owner suspension is accepted, keep the URL/token and child
  identities unchanged but withhold all real child configuration links, including
  while remote disable is pending. The valid URL returns the agreed Base64
  informational entries showing owner suspension, a support path, known expiry,
  and accurately qualified quota where available. Use a customer-facing
  explanation without private operator audit details or real child authentication
  data in the status-only result.
- **Access and delivery boundaries:** Show pending versus confirmed cutoff
  truthfully. Withholding configurations does not revoke already imported
  credentials or terminate native existing sessions; PC-102's credential
  enforcement and PC-021's panel policy remain required. This is an explicit
  owner-suspension exception to complete-node downloads. It does not permit
  accidental missing/partial real-node lists during ordinary API outages.
- **Owner release:** The same URL returns the permitted current generation under
  its applicable delivery gates after the owner clears this restriction. Ordinary
  expiry, exhaustion, customer disable, and stale-usage suspension retain
  PC-081/PC-082's complete-list behavior when no separate owner restriction,
  invalidation, or replacement gate applies. Owner release does not clear another
  restriction or restore allowance/expiry. Cancelled/superseded URLs cannot use
  this policy to publish real credentials or redirect to a new secret URL.
  Fetching cannot provision, renew, reset usage, or clear a restriction.
- **Rationale discussed:** Stop redistributing actual configurations during an
  explicit operator restriction while keeping a reversible URL and useful status.
  The accepted trade-off is a refresh potentially removing real nodes from a
  client's presentation and requiring another refresh after owner release.
- **References:** PC-004/PC-021/PC-078-PC-082/PC-102/PC-103;
  D05/D10/D11/D14; A14-A22/A32; E-003; constitution II/III/VI/VII.
- **Observable implications:** Fetching an owner-suspended URL produces status
  entries without real child configuration links, even if cutoff is still pending
  on a panel. The status does not claim confirmed revocation without evidence.
  Owner release preserves the URL/identities; subsequent permitted refresh
  restores the complete current node list. Mere customer disable or expiry
  continues to return that list under PC-082. Fetching never changes entitlement
  or access state.
- **Not settled:** Exact five-app refresh/selection behavior requires controlled
  evidence; no compatibility or existing-node removal result is claimed. Renewal
  payment during owner suspension remains a separate choice. Serializer syntax,
  fake-configuration generation, HTTP response, cache, and worker design belong
  to planning.

### PC-105 — Owner suspension blocks new renewal funding and closes unfunded quotes

- **Accepted:** 2026-09-30, answer to Q-093: "yes i agree with you."
- **New funding:** During owner suspension, do not start a new composite
  renewal/trial-conversion checkout, deduct new wallet funds, invite an external
  renewal payment, or accept a new zero-price renewal authorization. Explain that
  the owner must lift this restriction first; payment cannot lift it. The block
  applies to the restricted subscription, not all otherwise eligible purchases
  or subscriptions. Customer disable and ordinary expiry/exhaustion retain their
  independently agreed renewal eligibility.
- **Unfunded quotes:** On accepting owner suspension, reject this subscription's
  renewal quotes that have not reached full verified payment or validated
  zero-price final confirmation. Release held wallet contribution and coupon use
  once; wallet value is visible/spendable within the normal 60-second application/
  database target. This is an explicit terminal rejection under PC-098, not a new
  unpaid-order expiry timer or silent repricing. After owner release, a new quote
  uses current offers, eligibility, and prices.
- **Late money:** Subsequently validly verified external money for a rejected
  renewal becomes store-wallet credit once under PC-094/PC-098. It cannot reopen
  the quote, renew, or clear the restriction. Wallet value already released is
  not returned again with late external credit. Mismatched/unverifiable payments
  remain investigation; repeated notifications and distinct extra receipts remain
  separate under PC-099.
- **Already authorized renewal:** A renewal fully payment-verified or validly
  zero-price-authorized before suspension resolves under its original 15-minute
  deadline and complete-node/settlement rules. Preserve the owner restriction
  throughout: confirmed entitlement changes do not authorize access or real
  configuration download while suspended. Success applies agreed allowance,
  expiry, and carryover once; validity continues and suspension alone gives no
  automatic refund. Failure/timeout receives the accepted actual-payment wallet
  refund and coupon restoration, with cleanup retained. A separate permanent
  cancellation accepted during the in-flight renewal still follows
  PC-102/PC-073-PC-075's sequential revocation/full renewal-payment refund.
- **Rationale discussed:** Avoid knowingly taking new money while an operator
  restriction prevents service, while resolving an already verified transaction
  without unsafe rollback/replay. The accepted trade-off is waiting for owner
  release with expiry continuing, loss of the closed quote's old offer/price
  guarantee, and a previously verified renewal potentially completing while
  access remains restricted. Owner compensation remains discretionary.
- **References:** PC-024-PC-039/PC-061/PC-069-PC-071/PC-094/PC-096-PC-099/
  PC-102-PC-104; D09/D10/D14; A03-A06/A15/A19/A25/A28;
  constitution II/III/VII.
- **Observable implications:** An owner suspension closes an unfunded renewal
  quote and restores its held wallet/coupon once. A later verified external
  receipt credits only its actual external amount and never renews. An earlier
  fully verified renewal can finish once within its original deadline but remains
  owner-suspended with status-only downloads; its successful terms keep advancing.
  A rejected zero-price renewal produces no positive refund. Repeated actions do
  not repeat benefits, credits, or coupon release. A new checkout after release
  uses then-current pricing rather than the closed quote.
- **Not settled:** Ordering/recovery algorithms, state schema, gateway workflow,
  and controlled evidence belong to planning/verification. No generalized
  entitlement editing or account-wide service prohibition is selected.

### PC-106 — One faithful real export per explicitly configured plan node

- **Accepted:** 2026-09-30, answer to Q-094: "yes i agree."
- **Behavior:** Each included node has one owner-selected intended endpoint/
  configuration and descriptive remark. Ordinary complete export publishes one
  faithful real URI per included node in the plan's stable configured order.
  The initial A-only five-choice plan exports five real entries; the six-node
  acceptance fixture exports six. Informational rows are additional status entries,
  not real VPN nodes or extra allowance/meter grants. Neither number is a maximum;
  arbitrary configured collections remain supported.
- **Advertised alternatives:** A panel's alternative addresses, duplicates, or
  multiple native links for an identity do not automatically add nodes, credentials,
  allowance, or meters. Another real choice requires an explicitly configured
  included plan node under the independent-credential/shared-accounting rules.
  New catalog choices cannot silently change accepted quotes or sold subscriptions.
  Equivalent-server replacement preserves intended choices; broader topology
  editing/migration remains unapproved.
- **Faithful fulfillment:** Preserve the chosen node's address/port, protocol,
  transport, security/flow settings, UUID/password, and intended routing. Do not
  arbitrarily select the first native link or invent missing settings. If the
  intended configuration cannot be identified/exported faithfully, do not report
  complete fulfillment or silently omit it; complete-delivery gates and their
  failure/refund rules remain effective. Already fulfilled downloads retain the
  permitted verified complete current configuration under PC-081/PC-082, with
  PC-104's owner-suspension exception and invalidation/replacement gates. Fetching
  must not create extra credentials or alter entitlement.
- **Rationale discussed:** Keep the list aligned with purchased choices rather
  than accidental expansion from panel export settings. The accepted trade-off
  is owner selection of each endpoint and no automatic visibility for another
  advertised address.
- **References:** PC-001-PC-005/PC-008/PC-011/PC-049/PC-076-PC-086/PC-098/PC-104;
  R02-R05; D04/D05/D11; A01/A02/A20-A24/A28; F-022/F-034;
  E-001/E-003; constitution I/II/V/VI/VII.
- **Observable implications:** A native panel list containing several aliases
  for one configured node still yields one selected real entry. Plan order and
  distinct descriptive remarks remain stable across ordinary refresh. Five
  configured real nodes plus informational rows are distinguishable from five
  purchased quotas or an implementation maximum of five. Missing faithful required
  export cannot pass complete fulfillment. A new advertised endpoint does not
  silently expand an existing customer's list or double-count traffic.
- **Not settled:** Selection/API/serializer/storage design belongs to planning.
  Actual endpoint, routing, and five-client compatibility remain controlled
  evidence; no arbitrary topology migration or passing result is approved here.

### PC-107 — Catch up verified financial obligations after intact-history outages

- **Accepted:** 2026-09-30, answer to Q-095: "yes i agree with you."
- **Original clocks:** Whole-manager outages/restarts do not reset original
  fulfillment/renewal deadlines, expiry, last-trustworthy-sample grace, replacement
  cooldown, campaign history/cap, or restrictions. Reconcile uncertain effects
  before repeating them and use trustworthy original timing/outcome evidence.
  Initial fulfillment/renewal not completed within its original 15-minute window
  follows its terminal failure/refund policy, without a new window or late
  benefits. Remote clients existing during an initial outage do not by themselves
  prove timely URL availability under PC-049.
- **Financial catch-up:** For an overdue obligation with verified beneficiary,
  actual amount, and established prior financial-effect outcome, make wallet
  refund/credit visible and spendable within 60 seconds of safe application/
  database processing resuming. If verification was established before the outage,
  start this catch-up target at safe processing resumption. Cleanup/notification
  failure does not delay an otherwise verifiable credit. Record the originally
  missed deadline and recovered outcome rather than claiming timely completion.
  Repeated recovery cannot duplicate credits or other effects.
- **Uncertainty and attention:** Unknown payment or prior debit/credit/refund
  outcomes require reconciliation before settlement/retry, not fabricated proof
  or a potentially duplicate credit. On recovery, make overdue unresolved work
  visible to the owner, attempt the existing owner Telegram alert, and retain
  truthful customer pending/support status where available. Do not restart a
  15-minute attention timer to hide overdue work. Once a money obligation is
  verifiable and processing safe, apply the normal 60-second credit target.
- **Previously fulfilled service:** Retain allowance, original expiry, and
  restrictions while accounting/remote state catch up under the accepted outage,
  cutoff, recovery, and usage-gap policies. Do not automatically renew/refill,
  re-enable known revoked access, create absorbed-overrun debt, extend expiry, or
  compensate for the outage. PC-019's best-effort exposure remains: manager
  unavailability cannot guarantee timely cutoff while VPN data paths continue.
- **Scope:** This is recovery with intact committed history. It does not approve
  automatic resumption from stale backups, missing payment/purchase/revocation
  records, or corruption; constitution IV requires separate reconciliation and
  remediation in those cases.
- **Rationale discussed:** Restore owed money promptly without erasing original
  deadlines or replaying effects. The accepted trade-off is refunding overdue
  unfulfilled orders instead of late delivery and requiring owner attention when
  safe reconciliation remains impossible.
- **References:** PC-005/PC-012-PC-014/PC-018-PC-023/PC-037/PC-048/PC-049/
  PC-057-PC-059/PC-067/PC-073-PC-075/PC-094-PC-105;
  D02/D08/D10/D13; A03-A06/A15/A16/A25/A28/A30/A31;
  F-005/F-029/F-031; E-002/E-004/E-005; constitution II/IV/VII.
- **Observable implications:** A manager returning at 12:30 after an initial
  order missed its 12:15 delivery deadline cancels/refunds under the existing
  policy rather than granting another 15 minutes. Its safely verifiable overdue
  credit is spendable within 60 seconds of safe processing resumption. A repeated
  restart credits nothing twice. Unknown prior credit stays pending and visible;
  expiry/grace/cooldowns do not restart. A retained cleanup failure does not delay
  a verifiable refund or disappear because money was returned.
- **Not settled:** Stale-restore uncertainty, whole-host recovery/data-loss
  objectives, backup strategy, polling/retry algorithms, worker architecture,
  and controlled recovery evidence remain separate product/planning topics.

### PC-108 — Hold affected operations while stale-restore history is uncertain

- **Accepted:** 2026-09-30, answer to Q-096: "yes."
- **Verification:** A restored snapshot is historical evidence, not current
  proof of payment, allowance, expiry, campaign capacity, URL/credential
  generation, or remote access. Reconcile available newer evidence before
  dependent financial, provisioning, enable, or export mutations resume. Preserve
  pre-restore evidence, history, identities, and cleanup/recovery responsibility;
  apply established newer restrictions, cancellations/rotations, purchases,
  renewals, usage, and financial outcomes without replaying stale effects.
- **Subscription recovery hold:** Where entitlement, management ownership, or
  current generation remains uncertain, do not recreate/enable credentials,
  publish potentially revoked/superseded configurations, refill allowance, extend
  expiry, transfer ownership, or report restored access from the snapshot alone.
  Show recovery-pending/support status without presenting uncertain expiry/usage
  as current fact. Pursue safe suspension/cleanup for credentials with verified
  management ownership under the existing best-effort policy. Do not mutate
  unverified remote identities or claim a hold terminated already imported access
  or native existing sessions.
- **Money, eligibility, and scope:** Hold affected operations whose prior
  financial outcomes or claim eligibility cannot be established. Do not
  automatically repeat debits/refunds/credits, restore coupon capacity, reset
  `test_used`, or reopen the campaign from old counts. Unverified permanent
  campaign history/cap pauses new campaign claims until resolved. Other verified
  catalog/test paths may operate when their own financial/eligibility state is
  safe. Release verified subscriptions/operations individually. Widen the hold
  only where affected shared state cannot safely be isolated; directly dependent
  legacy wallet/restore callers may be affected and require explicit later
  compatibility/restore coverage.
- **Owner remediation:** Show unresolved gaps and partial recovery with affected
  records, evidence, and a remediation/support path. PC-084's usage-gap settlement
  applies only with intact entitlement/ownership/lifecycle history; it is not
  blanket acceptance of lost purchase, refund, revocation, rotation, or campaign
  history. Irrecoverable gaps need a specific documented remediation or
  risk-acceptance decision under constitution Governance. This approval grants no
  constitutional exception and no generic resume override of these obligations.
- **Rationale discussed:** Avoid resurrecting cancelled access, duplicating money,
  or granting another test/campaign place from old data. The accepted trade-off
  is longer affected-customer interruption and owner investigation when snapshots
  plus live panel state cannot establish complete history.
- **References:** PC-004/PC-005/PC-018-PC-023/PC-057-PC-060/PC-084/PC-094-PC-107;
  D08/D10/D13/D14; A03-A06/A09/A11/A15-A20/A28-A31;
  F-035; E-004/E-005; constitution II-IV/VII.
- **Observable implications:** Restoring a pre-cancellation/rotation snapshot
  cannot automatically enable or publish its old credentials. An uncertain prior
  refund stays pending without another credit. Missing campaign history does not
  reopen places or allow repeat recipients. Independently verified subscriptions
  may recover without waiting for unrelated unresolved cases. Partial recovery
  and pending cutoff remain visible; reachable APIs alone do not establish all
  missing history or terminate existing traffic.
- **Not settled:** Recovery-point/time objectives, backup scope/mechanisms,
  evidence sources, orphan discovery, and reconciliation architecture remain
  product/planning topics. No restore or actual history-reconstruction result
  has been demonstrated here.

### PC-109 — Guard composite responsibilities against reset and forced deletion

- **Accepted:** 2026-10-01, answer to Q-097: "yes."
- **Destructive protection:** Reject main-store factory reset when it would erase
  composite ownership, financial/usage/lifecycle history, pending work, or permanent
  campaign recipient/cap history. Protect referenced panel, customer, subscription,
  and dependent records from removal that loses required evidence or sole
  management/cleanup responsibility. A generic `force` option or confirmation
  phrase cannot bypass this protection. Add no new customer hard-delete flow.
- **Operator path:** Explain blocked operations and affected responsibilities to
  the owner. Use approved cancellation, safe cleanup, or equivalent-server
  replacement to address service, retaining required history and unresolved
  obligations. Cancelling all subscriptions or refunding orders does not authorize
  erasing campaign history, financial evidence, or pending old-server cleanup.
  Reset/panel-row removal cannot silently perform remote batch revocation or
  automatic refunds with unreviewed consequences.
- **Panel deactivation:** Exclude panels retired/deactivated for new composite
  sales/test claims from newly accepted offers/claims. Deactivation does not itself
  stop existing composite accounting, enforcement, or cleanup, or revoke access.
  Retain usable management references; explicit service restriction and equivalent
  replacement remain separate actions.
- **Compatibility and scope:** Preserve affected legacy-only behavior outside
  composite dependencies. Ordinary test-usage resets remain supported under
  PC-060 with campaign history/cap intact. This is a launch destructive-loss guard,
  not a general teardown/export/handoff feature. Future removal/retention policy
  must preserve or durably hand off obligations under constitution IV. Required
  accounting evidence remains protected without mandating every raw sample be
  retained forever.
- **Rationale discussed:** Prevent orphaned credentials, lost owed money, and
  reopened campaign eligibility. The accepted trade-off is the reset/force-delete
  shortcut becoming unavailable for protected composite data; deliberate service
  controls and retained records are required.
- **References:** PC-004/PC-005/PC-057-PC-060/PC-072-PC-075/PC-086-PC-091/
  PC-101-PC-108; D10/D13/D14; A17/A19/A23/A24/A26/A28-A31;
  F-006/F-036; constitution I-IV/VII.
- **Observable implications:** A force-delete request cannot erase panel records
  needed by composite children/cleanup, and factory reset cannot wipe composite
  or permanent campaign history. The owner sees a reason and the affected records.
  Panel deactivation prevents new composite offers/claims using it while existing
  management responsibilities continue. General test-counter reset does not erase
  campaign recipient history or restore campaign places. Legacy-only operations
  outside protected dependencies preserve their affected behavior.
- **Not settled:** Catalog and existing-checkout behavior during equivalent
  replacement remains a separate choice. Tombstone design, retention period,
  cleanup algorithms, and any future teardown architecture belong to planning
  or a separately approved feature.

### PC-110 — Pause affected sales during cutover and reopen independently

- **Accepted:** 2026-10-01, answer to Q-098: "i agree with you."
- **New sales and claims:** At owner-authorized retirement/cutover of the old
  serving topology, stop accepting new initial checkouts/test claims using it.
  Reject affected quotes not yet fully payment-verified or validly zero-price-
  authorized. Restore held wallet contribution within the normal 60-second
  target and release coupon use once; later validly verified external money
  becomes wallet credit under PC-094/PC-098, never late fulfillment. This is
  explicit operational rejection, not silent repricing or an unpaid-order TTL.
- **Independent reopening:** Keep unaffected offers/claims available when their
  own prerequisites are safe. Explain affected temporary unavailability. Refused
  new attempts cannot debit money, reserve test allowance/campaign capacity,
  start a fulfillment clock, or gain waiting-queue priority. Explicit owner
  activation of a prepared, validated equivalent replacement offering can reopen
  new purchases/tests before all existing subscriptions move. Newly accepted
  orders/claims use current prices and eligibility; permanent campaign history
  and its cap remain intact.
- **Previously accepted work:** Fully payment-verified purchases/renewals,
  validly zero-price-authorized orders, and accepted pending test claims keep
  original terms, clocks, reservations, and complete-fulfillment gates. They may
  finish on the owner's explicitly authorized equivalent target only while
  preserving intended node choices/service, accounting prerequisites, authority,
  and delivery gates. Do not substitute an unrelated topology, create a second
  entitlement, restart 15 minutes, or revive terminal failed/cancelled work.
  Missed timely completion follows existing refund/coupon or test/campaign
  reservation rules. Unknown claim outcomes retain their holds until reconciled;
  remote cleanup remains separate. Pending renewal retains prior entitlement
  under PC-036/PC-037.
- **Renewal during movement:** Block new renewal/conversion funding while that
  subscription's equivalent move is pending, closing its affected unfunded
  renewal quotes as above. After its complete replacement is ready with
  trustworthy accounting, normal renewal eligibility resumes subject to other
  restrictions without waiting for the batch. Explicit equivalent movement
  preserves matching-plan eligibility through the intended node choices; changed
  physical server/inbound identifiers alone do not disqualify an otherwise
  matching preset. Different country/protocol/node sets still require a separate
  purchase or separately approved broader migration.
- **Rationale discussed:** Avoid accepting work onto a retired/unready target
  while reopening prepared offers and completed customers independently. The
  accepted trade-off is a temporary affected sales/test/renewal pause, loss of
  closed quotes' old price guarantees, and refunds when already funded operations
  cannot complete within their original window.
- **References:** PC-005/PC-011-PC-014/PC-025/PC-035-PC-039/PC-049/
  PC-057-PC-061/PC-083/PC-086-PC-091/PC-094-PC-099/PC-105/PC-109;
  D04/D07/D09/D10/D14; A03-A06/A19/A24/A25/A28; constitution I-IV/VII.
- **Observable implications:** Retiring A closes its unfunded quote and restores
  held wallet/coupon once; a late verified payment credits the wallet rather than
  provisioning. A prepared equivalent A replacement can accept new orders while
  an older customer's move remains pending. Previously verified work keeps its
  original deadline and either completes faithfully or follows its failure policy.
  A successfully moved customer can renew into a matching offer while unrelated
  migration cases remain pending; physical identifier changes alone cannot reject
  that match. A refused new test claim consumes no test allowance or campaign place.
- **Not settled:** Historical subscription eligibility for replacement remains
  a separate question. Worker ordering, concurrency algorithms, catalog/storage
  identity, APIs, and tasks belong to planning; this answer selects none of them.

### PC-111 — Move inactive fulfilled subscriptions without restoring access

- **Accepted:** 2026-10-01, answer to Q-099: "yes i agree."
- **Eligibility:** Owner equivalent-replacement selection includes fulfilled paid
  and test subscriptions that have not been permanently cancelled, including
  expired, exhausted, customer-disabled, owner-suspended, and stale-usage-suspended
  subscriptions. The bulk preview explicitly identifies included inactive cases;
  "all affected subscriptions" must not silently mean only active subscriptions.
- **Preservation:** Keep allowance, actual consumption/history, original expiry,
  ownership, unchanged URL, and every applicable restriction. Moved credentials
  are provisioned in the required inactive state; completing movement is not
  permission to enable access. Continue responsibility for accounting and cleanup
  of old credentials. Stale-usage recovery still follows PC-022/PC-087's verified
  accounting conditions, rather than treating movement alone as proof of recovery.
- **Later return:** Eligible renewal/conversion or resumption uses the same URL
  and current replacement credentials under normal entitlement/restriction gates.
  Movement does not replenish expired/exhausted entitlement, clear independent
  customer/owner restrictions, reset cooldown/test/campaign history, or authorize
  resumption from uncertain data. Downloads and refresh notices reflect actual
  status, including PC-104's status-only owner-suspension response.
- **Terminal and uncertain cases:** Permanently cancelled subscriptions remain
  cleanup-only and are not recreated on the replacement. Unfulfilled or terminal
  failed orders/claims cannot be revived through historical subscription selection.
  Accepted pending fulfillment follows PC-110's original window and gates.
  PC-108 recovery-hold cases with uncertain entitlement, ownership, or lifecycle
  remain ineligible until verified or specifically remediated under the
  constitution; bulk selection cannot waive that requirement.
- **Capacity meaning:** PC-090's supported normal 15-minute benchmark includes
  selected eligible inactive subscriptions as well as active ones: up to 150
  subscriptions with five moved credentials each. It remains an unverified target,
  not a customer/selection maximum or an infrastructure-capacity result.
- **Rationale discussed:** Preserve later renewal/resumption through the same URL
  after retirement of the old server. The accepted trade-off is replacement work
  and remote credential capacity for customers who may never return, instead of
  requiring a separately defined later migration before their return.
- **References:** PC-005/PC-022-PC-039/PC-061/PC-066/PC-072-PC-075/
  PC-082/PC-086-PC-091/PC-102/PC-104-PC-110; D08/D09/D10/D14;
  A12/A15/A17-A19/A24/A29-A31; constitution II-IV/VII.
- **Observable implications:** An expired test or exhausted paid subscription
  can move with inactive credentials, unchanged URL/expiry, and no fresh grant;
  a later eligible conversion/renewal uses the moved identities. Owner-suspended
  subscriptions stay suspended with status-only exports. Cancelled subscriptions
  gain no replacement credentials; uncertain recovery-held cases cannot bypass
  verification by inclusion in a batch. A mixed active/inactive 150-subscription
  benchmark counts both groups toward its selected cohort.
- **Not settled:** Selection algorithms, schema, retention periods, worker
  architecture, tasks, and controlled measured results belong to planning or
  verification, not this product answer.

### PC-112 — Fifteen-minute recoverable local-history objective

- **Accepted:** 2026-10-01, answer to Q-100: "yes i agree."
- **Objective:** Under supported normal operating conditions, maintain a
  completed, validated recoverable copy of required authoritative local composite
  state captured at most 15 elapsed minutes ago and accessible after loss of the
  subscription-management host. Scope includes ownership/tokens, entitlement/
  usage and billing boundaries, money/coupon outcomes, test/campaign eligibility
  and permanent recipient history, current/retired credential identities, pending
  work/cleanup responsibility, and required dependent main-store state. This does
  not assert those records already exist or select their physical storage.
- **Truthful protection status:** Measure age from the verified capture point,
  not a delivery timestamp, file modification, or attempted backup. Expose the
  last verified recoverable point and overdue/unknown protection to the owner.
  Validation/delivery failure cannot report fresh protection. Make failures
  actionable in web admin, attempt an owner Telegram alert, and retain actual
  failure/recovery outcomes rather than treating a send attempt as successful
  notification delivery.
- **Limits and missed objective:** This is a launch objective requiring
  controlled proof, not existing implementation, zero data loss, permission to
  erase uncertain financial/revocation/campaign history, or current panel-state
  proof. Copying every 15 minutes alone does not establish validated available
  protection. If missed, retain actual exposure and apply PC-108's reconciliation,
  holds, and specific governed remediation after loss; never invent the missing
  interval. Expiry and existing service/financial rules continue. An overdue
  backup alone introduces no automatic mass VPN suspension or new refund.
- **Rationale discussed:** Limit unrecoverable paid-operation and capped-campaign
  history compared with daily backups. The accepted trade-off is more backup,
  validation, availability, storage, and transfer work than an hourly/daily
  objective; a one-hour alternative would leave a larger gap to investigate.
- **References:** PC-003-PC-005/PC-057-PC-060/PC-084/PC-107-PC-111;
  D13; A23/A30/A31; S11; F-035/F-037; E-004/E-005;
  constitution II-IV/VI/VII.
- **Observable implications:** Losing the management host at 12:00 under supported
  normal conditions leaves a validated accessible recovery point captured at
  11:45 or later. A newly attempted transfer of a 10:00 capture cannot make it
  fresh. Failed validation/unavailable delivery exposes overdue or unknown
  protection and owner recovery action, without claiming the objective passed.
  Later restore reconciles missing/newer history under PC-108 rather than replaying
  credits, reopening campaign places, or enabling revoked credentials.
- **Not settled:** Whole-host recovery-time expectations remain a product choice.
  Snapshot/journal method, cadence, destinations, retention, encryption/secret
  recovery, restore coordination, general infrastructure backup, and tasks belong
  to planning. No new minute-based admin control or database replacement is selected.

### PC-113 — Four-hour safe recovery objective on prepared infrastructure

- **Accepted:** 2026-10-01, answer to Q-101: "yes i agree."
- **Conditional target:** Under supported normal conditions, target four elapsed
  hours from owner-initiated recovery with a prepared replacement host, an
  available validated required recovery copy, release/configuration/authorized
  secret inputs, and external HTTPS/domain/panel prerequisites. Owner response
  before recovery starts, host procurement/preparation, and unavailable external
  dependencies are outside this conditional target and reported separately.
  Do not advertise four hours from the original incident. Once prerequisites
  are met and recovery starts, retries/restarts do not restart its clock.
- **Recovered functions:** Restore main-store Telegram customer management,
  owner web management, existing public subscription URL identity, and safe
  accounting/enforcement/recovery processing for independently verified
  subscriptions and financial operations. Apply PC-107/PC-108: keep original
  clocks/terms, catch up verifiable credits, reconcile newer evidence before
  dependent effects, and retain confirmed cancellation/rotation/restrictions and
  remote cleanup. Serve permitted verified complete or status-only downloads
  under existing policies; never publish stale tokens/credential generations to
  meet the target.
- **Partial and overdue recovery:** Unresolved newer/missing history or required
  unavailable services remain truthfully pending/recovery-held, with evidence,
  owner action, and governed remediation. Restore truthful status/recovery
  management for these cases and report partial completion. A running process,
  replaced file, or some recovered customers is not a fully recovered store.
  The target does not promise reconstruction of irrecoverable history or waive
  holds. Missed targets expose overdue recovery and affected functions/cases,
  retaining bounded repeat-safe recovery and obligations.
- **Service and scope:** Preserve best-effort outage exposure and original
  expiry. No automatic extension, outage refund, fresh allowance, or guaranteed
  hard cutoff during manager unavailability is introduced. Discretionary wallet
  compensation remains available. This selects no failover architecture and
  requires no always-ready second deployment.
- **Rationale discussed:** Give an owner-operated launch a measurable restoration
  goal without promising instant disaster recovery. The accepted trade-off is
  up to four hours of control/download interruption after preparation, plus
  response/infrastructure preparation before that clock; a one-hour target would
  require more operational investment and unbounded best effort less predictability.
- **References:** PC-005/PC-019/PC-023/PC-069-PC-071/PC-081/PC-082/
  PC-086-PC-091/PC-104/PC-107-PC-112; D11/D13;
  A16/A20/A23/A30/A31; S06/S11; F-035/F-037; E-004/E-005;
  constitution II-IV/VI/VII.
- **Observable implications:** Recovery beginning at 12:00 with stated
  prerequisites ready targets verified management/URL/accounting availability by
  16:00, without starting another four hours after a retry. A lost cancellation
  or uncertain financial case stays held and visible while verified cases recover.
  Reports distinguish prerequisite waiting, partial recovery, overdue functions,
  and confirmed restoration; neither copied files nor old credentials alone prove
  success. Existing entitlement/cutoff/refund rules survive recovery.
- **Not settled:** Exact supported load, measured feasibility, backup/deployment
  methods, evidence sources, hosting/secret handling, restore architecture, and
  task breakdowns belong to planning/controlled verification. No recovery test
  or performance claim is made here.

### PC-114 — Investigate unexpected panel identity loss before recreating service

- **Accepted:** 2026-10-01, answer to Q-102: "yes i agree."
- **Authority and intact identities:** The agreed local entitlement, ownership,
  intended credential generation, and restrictions govern the composite. Routine
  direct panel edits do not renew, refill, cancel, transfer, or replace it. With
  an intact verified identity and trustworthy accounting, bounded repeat-safe
  reconciliation may restore already approved desired enable/disable, quota, or
  expiry settings; do not adopt extra allowance, later expiry, or cleared
  restrictions from unexpected remote edits.
- **Unexpected identity loss:** Missing, unexpectedly renamed/replaced, or
  mismatched managed identities require owner-controlled investigation/recovery,
  not silent recreation, unrelated-user adoption, fresh UUID issuance, or a
  zero-usage new epoch. Retain known usage, identities, ownership, restrictions,
  and cleanup evidence. Expose the discrepancy and recovery path in owner web
  admin with an attempted Telegram alert and truthful customer uncertainty.
  Publish no unverified replacement configuration; mutate only verified owned
  identities, leaving unrelated clients/shared routes intact.
- **Existing grace and terms:** Lost reliable required usage follows the whole-
  subscription five-minute threshold from the last trustworthy sample, never
  detection/retry time. Known expiry/exhaustion and independent restrictions
  receive no grace. Cutoff remains pending/confirmed under native-session and
  best-effort policies. Identity loss creates no automatic refund, extension,
  fresh quota, or test/campaign reset; unknown usage is never zero.
- **Recovery:** The owner investigates and restores intended service through
  verified recovery/approved replacement controls. An unrecoverable usage gap
  requires explicit PC-084 settlement with intact entitlement/ownership/lifecycle;
  other missing history follows PC-108's reconciliation/governance boundaries.
  Automatic resumption requires verified intended identities, current trustworthy
  metering, reconciled usage, and all normal eligibility/restriction gates under
  PC-022. Recovery cannot resurrect cancelled service, bypass leak-replacement
  gates, clear independent holds, or create another entitlement.
- **Scope:** No general repair UI, arbitrary remote-history import, panel-user
  adoption, or shared-infrastructure editing is approved. Ordinary API outages
  with intact credentials still recover automatically under PC-022; owner
  investigation is for unexplained identity/history changes.
- **Rationale discussed:** Avoid undoing deliberate revocation or losing
  unobserved usage through automatic recreation. The accepted trade-off is owner
  investigation and possible whole-subscription interruption while identity or
  history remains uncertain.
- **References:** PC-004/PC-005/PC-018-PC-023/PC-034-PC-039/PC-042-PC-047/
  PC-083/PC-084/PC-086-PC-088/PC-102/PC-107-PC-113;
  D08/D10/D14; A09/A11/A14-A19/A24/A31; F-004/F-013/F-025/F-039;
  E-001/E-002; constitution II-V/VII.
- **Observable implications:** Deleting a child directly in 3x-UI does not
  silently recreate it or report full unused allowance. The owner sees the known
  identity, uncertainty, and recovery action; other nodes follow the original
  stale threshold without a restarted timer. An intact child's unauthorized
  later expiry does not extend the purchased term. Verified recovery preserves
  history and independent restrictions; unknown other history cannot be absorbed
  through the usage-only settlement control.
- **Not settled:** Detection/reconciliation/repair mechanisms, counter epochs,
  polling, APIs, and actual panel behavior belong to planning/controlled evidence.

### PC-115 — Sixty-second normal usage freshness with earlier delay warnings

- **Accepted:** 2026-10-02, answer to Q-103: "yes i agree."
- **Normal freshness:** Under supported normal conditions, Telegram subscription
  details/refresh and newly fetched public subscription responses show reconciled
  whole-subscription usage/remaining allowance using trustworthy required
  observations at most 60 elapsed seconds old. Age includes integration/display
  delay and is measured from underlying trustworthy readings, not refresh, HTTP
  response, cache writes, or the last attempted update. This does not select a
  polling interval or add another 60 seconds to PC-020's combined observation/
  enforcement target.
- **Complete and conservative evidence:** Usage is current/verified only when
  all required current meters have trustworthy readings no older than 60 seconds
  and history is reconciled. A newer healthy meter cannot conceal another one's
  delay. Where required readings differ in time, show the oldest required
  trustworthy observation time rather than an apparently simultaneous exact
  balance. PC-087's excluded retired-server cleanup meters do not independently
  stale verified replacement accounting.
- **Delay warning:** Warn as soon as an update is known incomplete/untrustworthy
  or any required reading exceeds 60 seconds. Retain PC-079's last reliable
  whole-subscription figure with its genuine timestamp and delayed/incomplete
  qualification, or unknown if no reliable figure exists. A 61-second-old figure
  is not current verified usage. The five-minute stale-meter suspension threshold
  remains unchanged; grace is not confirmed cutoff and fetch/retry cannot restart
  it. Known expiry/exhaustion and independent restrictions still apply. Never
  fabricate zero/full/unlimited allowance from incomplete evidence.
- **Consistency and snapshots:** Customer displays, exports, accounting
  eligibility, and recovery use compatible freshness/uncertainty meanings. A
  reachable API or fresh partial reading cannot settle missing history.
  Informational configuration names remain snapshots until the customer refreshes
  the app. No live push, compulsory app refresh frequency, per-download panel
  call, or simultaneous/synchronous sampling design is approved.
- **Rationale discussed:** Provide timely shared allowance while exposing delay
  throughout the existing grace period. The accepted trade-off is more frequent
  reliable observations and earlier visible warnings; a looser display target
  would reduce observation load but provide less timely information.
- **References:** PC-004/PC-015/PC-018-PC-022/PC-079/PC-081/PC-082/
  PC-084/PC-087/PC-104/PC-107-PC-114; D02/D08/D11;
  A07-A17/A20/A32; S05-S07; F-023/F-025/F-039; E-001-E-004;
  constitution II/VI/VII.
- **Observable implications:** A required reading aged 60 seconds can qualify
  if complete/trustworthy; at 61 seconds the same figure is marked delayed.
  A panel failure produces the warning even before that age threshold. One
  child's newer sample cannot make the parent current while another is delayed.
  At five minutes the suspension rule still initiates, with pending versus
  confirmed status distinguished. Repeated downloads do not advance source time;
  already imported labels do not update until client refresh.
- **Not settled:** Automatic resumption completion timing remains a product
  question. Supported-load feasibility, timestamp representation, serializer/
  cache behavior, observation/reconciliation algorithms, and detailed display
  rounding belong to planning/controlled verification. No result is claimed.

### PC-116 — Confirm automatic resumption within sixty seconds of verified readiness

- **Accepted:** 2026-10-02, answer to Q-104: "yes i agree."
- **Target and start:** Preserve PC-022's automatic recovery. Under supported
  normal conditions, confirm fresh-authentication availability on every required
  credential within 60 elapsed seconds after intended identities/current readings
  are verified, history is reconciled (including valid explicit PC-084 settlement
  where needed), PC-115 freshness is met, allowance/time remain, and no independent
  restriction/cancellation/revocation prohibits access. Start at verified
  satisfaction of those prerequisites, not later worker selection/retry. Mere
  API reachability, partial readings, or unresolved history do not qualify.
- **No added dwell or waived safeguards:** Ordinary resolved API outages require
  no fixed stability waiting period or new owner approval. Existing explicit
  identity/usage-gap investigation and settlement remain required where applicable.
  Retries/restarts do not reset the clock. Lost prerequisites or a newer
  restriction/cancellation/expiry prevent older work from enabling access;
  communicate changed/pending state and apply the relevant cutoff/hold. Partial
  enablement cannot be presented as confirmed whole-subscription restoration.
- **Attention and continuity:** At 15 elapsed minutes from eligible recovery
  readiness, unfinished restoration is overdue, visible/actionable in owner web
  admin with attempted owner Telegram alert and customer pending/support status.
  Keep bounded repeat-safe recovery and unresolved obligations. Do not reset
  allowance, extend expiry, erase pending work, or silently report success to
  compensate. Independent customer/owner holds retain their own release gates;
  cancelled subscriptions never qualify. Native existing-session handling and
  best-effort outage limits remain unchanged.
- **Rationale discussed:** Restore still-valid service promptly with the same
  normal expectation as customer resume. The accepted trade-off is possible
  repeated suspension/resumption while reporting is unstable, rather than an
  intentional additional waiting period delaying every restoration.
- **References:** PC-018-PC-023/PC-039/PC-066/PC-067/PC-084/PC-087/
  PC-102/PC-107-PC-115; D02/D08/D10; A09/A12-A16/A19/A31;
  S06/S07; E-001/E-002/E-004; constitution II/VI/VII.
- **Observable implications:** Verified eligible readiness at 12:00 targets
  confirmed new-connection availability on all required credentials by 12:01.
  A retry at 12:00:30 does not restart 60 seconds; unresolved work at 12:15 needs
  owner attention. A cancellation or expiry arriving before completion prevents
  stale re-enablement. One enabled child cannot establish complete restoration;
  missing historical evidence cannot be treated as zero to start the target.
- **Not settled:** Supported-load evidence, observation and retry/concurrency
  algorithms, worker architecture, and actual restoration measurements belong
  to planning/verification. This is an accepted target, not a passing check.

### PC-117 — Paid expiry/quota reminders without test/activity alerts or automatic coupons

- **Accepted:** 2026-10-02, answer to Q-105: "yes i agree."
- **Included scope:** Simple Telegram expiry and shared-quota reminders for
  fulfilled paid composite subscriptions, including tests after successful paid
  conversion. The owner can enable/disable each reminder type. Messages describe
  the one subscription's shared allowance/expiry and lead to its appropriate bot
  details/eligible renewal flow, not another entitlement or one alert per child.
  Use authoritative verified composite terms/accounting, without unsafe legacy
  header defaults or current-session claims.
- **Deferred optional alerts:** No optional expiry/quota reminders for still-free
  tests, including the campaign, and no composite "connected", "not connected",
  current-online/session, or first-use alerts at launch. Previously agreed paid/
  test fulfillment/failure/pending/support/replacement messages and retrievable
  truthful status remain required. Informational configuration entries and the
  customer's ability to inspect test terms/use paid conversion remain supported.
- **No automatic reminder coupon:** A composite reminder creates no promotional
  coupon. Existing valid owner-defined coupons and agreed checkout discounts
  remain available. Preserve affected legacy reminder settings and gift/reward
  behavior outside composite scope; do not remove their coupons globally.
- **Delivery outcome:** Failed/uncertain optional delivery remains distinct from
  success and cannot be permanently marked sent merely because attempted. Keep
  bounded repeat-safe delivery recovery and visible unresolved outcomes.
  Reminder failure cannot change allowance, expiry, enforcement, refund deadlines,
  campaign history, or eligibility. This approves no real notifications now.
- **Rationale discussed:** Help paying customers act before finite service runs
  out without inheriting automatic discounts or historical-usage-as-connection
  assertions. The accepted trade-off is fewer prompts for free-test conversion
  and no connection alerts/automatic reminder coupons at launch.
- **References:** PC-006-PC-010/PC-024/PC-051-PC-053/PC-055-PC-064/
  PC-079/PC-091/PC-103-PC-105/PC-115/PC-116; D07/D09/D11;
  A15/A19/A23/A25/A28/A32; F-038/F-039; constitution I-III/VII.
- **Observable implications:** A paid composite can receive one parent-based
  expiry/quota reminder rather than five/six child notices. A still-free campaign
  or quick test has no optional expiry/quota/connection alert; its mandatory
  fulfillment/status messages still work. Successful conversion makes paid
  reminder scope applicable. Sending a composite reminder issues no discount
  code, and failed delivery neither disables service nor becomes proven success.
  A legacy reminder continues its affected behavior outside this feature.
- **Not settled:** Thresholds, timing, repeat boundaries, and restricted-state
  eligibility remain dependent product choices. Existing five-day/80% source
  defaults are not accepted merely by this scope answer. Delivery mechanisms,
  worker architecture, localization, and tasks belong to planning.

### PC-118 — Configured reminder thresholds with one logical notice per paid period

- **Accepted:** 2026-10-02, answer to Q-106: "yes i agree."
- **Thresholds/defaults:** Respect existing valid main-store reminder enable/
  threshold settings while preserving their legacy behavior. Defaults are both
  reminder types enabled, expiry within five elapsed 24-hour days (120 hours)
  while not expired, and quota at or above 80% used. Retain the existing selectable
  alternative quota mode: remaining at or below a configured binary GiB threshold,
  with a two-GiB default when that mode is selected. Only the selected quota mode
  governs; crossing both conditions creates no second quota reminder. No automatic
  reminder coupons apply under PC-117.
- **Current shared terms:** Use current verified shared allowance and actual
  common expiry, not child limits or historical lifetime usage. Successful initial
  paid catalog fulfillment, full renewal, or trial-to-paid conversion starts a
  new logical reminder period. Its granted allowance includes carried unused data
  and newly granted data; already billed historical consumption cannot immediately
  trigger 80% because cumulative meters remain large. Carryover and the 45-day
  cap affect actual expiry. PC-097 zero-price normal catalog fulfillment follows
  its product-class terms without being treated as a free test.
- **Repeat boundaries:** One logical notice of each type per successful paid
  period. Failed/unfunded/pending renewal creates no new period. Refresh, restart,
  setting toggles/threshold edits, recovery, customer disable/resume, and credential/
  server replacement do not rearm a known successful notice. Failed/uncertain
  delivery follows PC-117 recovery without deliberately repeating known successful
  sends; exactly-once external Telegram delivery is not claimed for unknown outcomes.
- **Eligibility/obsolete notices:** Require the reminder type enabled, its
  verified condition true, fulfilled non-cancelled/non-expired service, no paid
  renewal in flight, and currently permitted ordinary paid renewal. Wait during
  owner suspension, recovery uncertainty, migration pending, or other blocking
  gates and reevaluate after resolution without consuming the notice. Customer
  disable alone permits reminders/renewal and is not cleared by either. An
  exhausted but unexpired eligible subscription can receive an accurate exhaustion
  quota notice; never describe threshold 80% as actual use when usage is higher.
  Cancel obsolete warnings after changed terms/cancellation/expiry.
- **Timing/evidence:** Under supported normal conditions, target Telegram
  acceptance within five elapsed minutes after condition and eligibility are
  satisfied, including observation/waiting. Acceptance does not establish reading.
  Known expiry is independent of traffic, but uncertainty blocking renewal also
  blocks an optional renewal prompt. Quota eligibility uses PC-115 fresh complete
  reconciled accounting. Telegram failure remains pending under bounded recovery
  and does not change VPN access or refunds.
- **Rationale discussed:** Consistent owner controls and advance prompts without
  spam or lifetime-usage false alarms after carryover. The accepted trade-off is
  no repeated optional reminder within a paid period when ignored, and waiting
  while a blocking restriction remains unresolved.
- **References:** PC-015/PC-023-PC-039/PC-051-PC-052/PC-061/
  PC-066/PC-072-PC-075/PC-097/PC-103-PC-105/PC-110/PC-115-PC-117;
  D03/D09/D11; A07/A12/A15/A19/A25/A32; F-038/F-039;
  E-002/E-004; constitution I-III/VI/VII.
- **Observable implications:** A healthy paid subscription entering its configured
  five-day/80% window gets an eligible logical notice within five minutes under
  normal conditions. Six nodes do not yield six reminders. A successful renewal
  with carried data does not reuse old lifetime use as newly consumed allowance.
  Restart/rotation cannot rearm a known sent notice; failed delivery is recoverable.
  An owner-held subscription receives no blocked-renewal prompt; after release,
  a still-valid qualifying condition can trigger. Legacy reminder settings and
  behavior remain preserved outside composite changes.
- **Not settled:** Notification bookkeeping, period/meter representation,
  scheduler/retry algorithms, UI/storage, localization, and actual load/delivery
  evidence belong to planning/controlled verification; no worker design is selected.

### PC-119 — Defer remaining optional naming, entitlement editing, and legacy import

- **Accepted:** 2026-10-02, answer to Q-107: "yes i agree."
- **Personal names:** Defer customer-selected service/configuration names at
  checkout and later personal renaming, both bot-only labels and remote identity/
  email changes. Distinguish subscriptions by preset name and a stable subscription
  identifier in Telegram; retain owner-defined node remarks/order. Do not rename
  accounting/routing identities to change a display label. Existing legacy naming
  remains supported within the compatibility boundary.
- **Sold entitlement/topology edits:** Defer ad hoc owner allowance/expiry edits,
  manual data/time grants or resets, and arbitrary changes to a purchased node
  set/countries/protocols/routes. Use approved full renewal/conversion and explicit
  equivalent replacement/recovery controls with their gates/history preservation.
  Future catalog/test presets remain owner-configurable without mutating sold
  snapshots. Usage-gap settlement and wallet compensation remain supported;
  neither supplies a fresh bucket or manual time/data grant.
- **Legacy import:** Defer automatic and manual legacy-to-composite import/
  conversion. Preserve single-panel/stock-link behavior; a separate new composite
  purchase cannot consume, transfer, or silently replace a legacy entitlement.
  BC-001's pre-sales context does not authorize discarding legacy data/fixtures
  or compatibility verification.
- **Retained scope:** All accepted paid/test/campaign fulfillment, discounts/
  coupons, renewal/conversion, customer management, owner single/bulk controls/
  compensation, usage-gap handling, equivalent migration, protected history/
  recovery, reminders, and truthful status remain in scope. No new history browser,
  arbitrary repair UI, builder, or teardown feature is approved. Required operation
  visibility and audit/support evidence remain required.
- **Rationale discussed:** Keep launch management predictable without hidden
  accounting/identity changes or unestablished imported history. The accepted
  trade-off is fixed customer names and fewer ad hoc correction shortcuts, using
  approved renewal/recovery/compensation/cancellation or separate purchase instead
  of inventing an exception.
- **References:** PC-003/PC-005/PC-008/PC-024-PC-039/PC-055-PC-064/
  PC-069-PC-075/PC-083-PC-091/PC-100-PC-118; BC-001;
  D07/D09/D10/D13/D14; A14/A19/A23/A24/A28-A31;
  F-008/F-039; constitution I-IV/VII.
- **Observable implications:** Two purchases of one preset are distinguishable
  by stable subscription identifier without customer naming. Editing a future
  preset does not add quota/days/nodes to sold copies. No composite rename/reset/
  arbitrary topology/import action appears as an implicitly inherited legacy
  feature. Legacy naming and existing services preserve their affected behavior;
  owner test-plan configuration and all explicitly approved lifecycle controls
  remain usable.
- **Not settled:** Future optional feature policies require separate explicit
  review. Identifier format, schema/storage, UI implementation, worker architecture,
  and tasks belong to planning. Refund fee/conversion scope was open at this
  answer under F-040 and is subsequently resolved by PC-120.

### PC-120 — Full quoted invoice value at original conversion for obligated wallet credits

- **Accepted:** 2026-10-02, answer to Q-108: "yes i agree."
- **Refund basis:** Keep the accepted store-wallet destination, refund/credit
  triggers, beneficiaries, deadlines, and repeat-safety. An eligible full refund
  returns the actual original wallet-funded portion plus the wallet-equivalent
  value of the entire validly verified original external invoice payment. Include
  disclosed required matching offsets, checkout/provider charges, and native-unit
  conversion/rounding increments included in the accepted payment quote and
  verified payable amount. The store absorbs these quoted costs even if the
  provider retained them. A zero actual payment creates no positive refund.
- **Exact example:** A discounted store price of 100 funded by 30 wallet units
  and an invoice requiring 73 (70 store remainder plus three quoted required
  charges) yields an eligible full refund of 103 wallet units once. It does not
  yield only 100 or the undiscounted nominal price. A separately verified second
  payment of 73 follows PC-099 as a distinct extra-payment credit, creates no
  second purchase, and is not refunded again with the original payment. Late
  verified external money after a cancelled/rejected checkout follows the same
  full invoice-value basis without repeating already returned wallet funds.
- **Coverage boundary:** Required costs in the accepted invoice do not create
  another subscription or justify an arbitrary mismatched overpayment. Separate
  bank, wallet, or network fees charged outside that invoice are not automatically
  reimbursed; they require discretionary owner support compensation without
  estimating or inventing them. Disclose total invoice cost and this boundary
  before payment. This decision does not add an automatic fee refund for a
  normally fulfilled purchase outside existing agreed refund/credit triggers.
- **Original payment terms:** Fix each accepted payment attempt's native
  currency/unit, required payable amount, quoted charges, wallet-equivalent total,
  and applicable conversion/rounding terms before it can authorize settlement.
  Credits use those original verified terms, not later market rates or changed
  admin conversion settings. Method-native invoice expiry remains applicable.
  A new permitted attempt may quote current method conversion/charges for the
  same PC-098 retained store offer, disclosing its new total without repricing
  the base offer or altering an already issued/paid attempt. Retaining the store
  offer does not freeze the native-currency cost of every future payment attempt.
- **Verification and uncertainty:** Validate beneficiary, checkout/tenant/
  reference, exact accepted native payable amount/currency, and original conversion
  evidence. Any permitted provider-unit rounding must be explicit in the quote
  and later plan. Do not copy blanket 99% acceptance, unbounded excess acceptance,
  missing/unparseable evidence acceptance, or current-rate recomputation from
  inspected legacy paths. Unknown/mismatched amount or fee evidence remains
  visible for investigation/reconciliation without fabricated gross value or
  duplicate credit. Method support requires establishing these facts; source
  presence/enabled configuration alone does not demonstrate safe support.
- **Preserved scope:** Selected allowance/duration, tier/coupon calculation basis,
  test/campaign history, and fulfillment clocks do not change. Preserve unaffected
  legacy payment behavior. No new gateway, general wallet-unit change,
  original-payment-method refund integration, or constitutional exception is
  approved.
- **Rationale discussed:** Make the full-refund promise match what the accepted
  invoice required the customer to pay, and prevent later exchange-rate changes
  from changing that recovery obligation. The accepted trade-off is store
  absorption of quoted costs while separate external fees remain outside
  automatic reimbursement. Base-store-price-only credit with nonrefundable
  quoted invoice costs was not selected.
- **References:** PC-013/PC-037/PC-048/PC-051/PC-052/PC-073-PC-075/
  PC-092-PC-099/PC-107/PC-108; D07/D10/D13;
  A03-A06/A19/A25/A28/A30/A31; F-012/F-027/F-029/F-040; E-005;
  constitution I-III/VII.
- **Observable implications:** The 100/30/73 example credits 103 once on an
  eligible full refund, even after a conversion-setting change. Repeated callbacks
  cannot refund twice; a distinct extra receipt receives its own credit without
  duplicate fulfillment or a later duplicate refund. A later verified cancelled
  invoice credits its original verified full wallet-equivalent amount without
  returning the wallet portion again. Quoted charges and separate outside fees
  are distinguishable before payment. Missing currency/amount/conversion proof
  cannot settle or fabricate credit. Required provider charges do not add quota,
  days, or campaign/test participation.
- **Not settled:** Actual enabled-method contracts, provider fee/rate evidence,
  exact supported conversion/rounding rules, quote/ledger storage,
  verification/reconciliation algorithms, and controlled failure checks remain
  planning/evidence work. No actual fees, safe gateway availability, passing
  integration, or new exception is established.

### PC-121 — One open renewal checkout per subscription

- **Accepted:** 2026-10-02, answer to Q-110: "yes i agree with you."
- **Behavior:** A composite subscription may have at most one open renewal/
  trial-to-paid-conversion checkout. This includes an accepted quote awaiting
  payment/manual review and a verified or zero-price-authorized renewal still
  being fulfilled. Another renewal attempt for that subscription returns to
  the existing checkout or its progress instead of creating a second order,
  deducting more wallet value, reserving another coupon use, or soliciting
  another renewal purchase. The boundary is per subscription, not per customer;
  other subscriptions and separate initial purchases retain their eligibility.
- **Changing the selected offer:** While the checkout is not fully funded,
  the customer can explicitly cancel it under PC-094/PC-096 and choose a new
  renewal offer using then-current terms and eligibility. An already verified
  renewal follows its existing completion, failure, and permanent-cancellation
  rules; a new selection cannot silently replace or cancel its purchased terms.
  After successful completion, another distinct early renewal remains allowed
  subject to the existing carryover and 45-day-total-remaining policy.
- **Terminal outcomes and recovery:** A failed/cancelled checkout does not block
  a new eligible checkout solely because unrelated cleanup remains. Unresolved
  effects affecting this subscription's entitlement/accounting must still meet
  the existing verification/reconciliation gates before accepting new payment.
  This does not permit unsafe replay or interpreting unknown remote effects as
  complete merely to admit another renewal.
- **Payment attempts:** Multiple currently permitted payment attempts against
  the same retained checkout remain allowed under PC-098. They are not separate
  renewal purchases. Late or distinct extra valid payments follow PC-094/
  PC-099/PC-120 without additional fulfillment, wallet debit, coupon consumption,
  or duplicate credit. Invoice expiry does not introduce a checkout expiry timer.
- **Protective controls:** Holding an unpaid renewal quote does not itself add
  a restriction on the customer's accepted disable, leak-protection, or
  cancellation controls. Existing authority, eligibility and lifecycle rules
  continue to govern those actions.
- **Rationale discussed:** Avoid accidental double purchases and competing
  carryover calculations for one subscription while keeping the pending checkout
  understandable. The accepted trade-off is completing or cancelling the
  existing eligible checkout before selecting another renewal offer, rather
  than supporting distinct simultaneous renewal orders for the same subscription.
- **References:** PC-024-PC-039/PC-054/PC-061/PC-094-PC-099/PC-105/PC-110/
  PC-120; Q-110; RV-001-A; F-041; D09/D10; A03-A06/A15/A25/A28;
  constitution II/III/VII.
- **Observable implications:** Starting another renewal while the first awaits
  receipt review shows the first order without another debit or coupon hold.
  Repeating the action during verified fulfillment shows progress. Retrying an
  allowed payment method for that order is supported; a distinct extra valid
  receipt produces its agreed wallet credit, not a second renewal. Another
  subscription owned by the same customer can renew independently. A successful
  completed renewal does not permanently disable subsequent early renewal.
- **Not settled:** Coordination, uniqueness/storage, payment-attempt bookkeeping,
  and race/recovery verification belong to planning. RV-001-B's treatment of a
  retained quote losing its funding path was subsequently resolved in PC-122. No schema,
  lock, queue, worker architecture, or passing concurrency result is selected.

### PC-122 — Reject an unpayable checkout while protecting valid existing attempts

- **Accepted:** 2026-10-02, answer to Q-111: "yes i agree."
- **Trigger and scope:** When a configuration or payment-restriction change
  leaves an initial purchase, renewal or trial-conversion checkout without a
  permitted funding path, automatically reject it once that absence is
  established. This applies before full payment verification or validated
  zero-price authorization. Explain why payment can no longer be completed.
- **Release and timing:** Restore the actual wallet contribution once and
  release the held coupon use once under the existing cancellation/release
  policies. Under normal application/database conditions, restored wallet funds
  must be visible and spendable within 60 seconds of rejection. Do not increase
  the wallet debit automatically, require a top-up, change the accepted plan or
  price, or invent a funding method to preserve an otherwise unpayable checkout.
- **Exact example:** A 100-unit checkout has deducted 30 wallet units and still
  requires 70. If no permitted option or valid existing payment attempt remains
  for the 70, reject it, restore 30 once, and release its coupon reservation.
  A later checkout uses current prices/offers/eligibility; rejection ends the
  old quote and its reserved promotion. Other payable checkouts are unaffected.
  Rejecting a renewal checkout does not cancel or alter the existing subscription.
- **Valid existing attempts:** An already issued attempt that remains valid,
  authorized and safely verifiable counts as a remaining funding path, including
  a legitimate payment awaiting owner manual review. Disabling a method for
  new invoices alone does not silently invalidate such an existing attempt.
  Preserve the pending quote while a permitted path remains. An invalid or
  unauthorized attempt cannot be treated as a path to bypass payment restrictions
  or verification; receipt upload alone still does not prove verified settlement.
- **Outage/expiry boundary:** A temporary gateway outage, uncertain verification,
  or ordinary invoice expiry alone does not establish loss of every permitted
  funding path. This does not introduce a general unpaid-checkout/manual-receipt
  expiry timer or automatically cancel a quote merely because one invoice expires.
  PC-098's retained-quote policy continues subject to this explicit rejection case.
- **Later money and already authorized orders:** Valid external money verified
  after rejection becomes store-wallet credit once for its complete original
  quoted wallet-equivalent value under PC-094/PC-099/PC-120. Do not reopen,
  provision, renew, or return the earlier wallet portion again. Unknown or
  mismatched payment evidence remains visible for verification/reconciliation.
  Already fully verified or zero-price-authorized orders keep their original
  fulfillment deadlines and outcome rules; a later payment-setting change
  cannot retrospectively reject them under this policy.
- **Rationale discussed:** Release customer money and limited coupon capacity
  when the store cannot accept the checkout's payment. The accepted trade-off
  is loss of its old price/promotion guarantee after rejection, instead of
  preserving the offer through an additional funding-adjustment policy.
- **References:** PC-092-PC-099/PC-105/PC-110/PC-120/PC-121; Q-111;
  RV-001-B; F-042; D07/D09/D10; A03-A06/A19/A25/A28;
  constitution II/III/VII.
- **Observable implications:** The 100/30/70 example releases wallet and coupon
  value exactly once, including after repeated eligibility checks or restarts.
  A remaining valid authorized invoice or legitimate pending manual review
  prevents classification as wholly unpayable merely because new invoices were
  disabled. Temporary gateway failure does not alone cancel the order. Valid
  late external money credits its original quoted value without fulfillment
  or double wallet restoration. A payment verified before the restriction change
  continues under its original fulfillment clock.
- **Not settled:** Detection/coordination, supported-method validity and
  verification evidence, storage, financial reconciliation, and race/failure
  checks belong to planning and controlled validation. No method availability,
  schema, algorithm, or passing result is established by this decision.

## Interview question history

### Q-001 — Initial sellers and commercial model

**Status:** answered; accepted seller scope recorded in PC-006.
**References:** D07; U03/U06; A27/A28; S12.

Who needs to be able to sell composite subscriptions in the first release:
only the main store selling directly to end customers, or reseller-operated stores too?
This asks which business operates the sale. A buyer's reseller/discount status and
commission attribution are separate eligibility questions, not exclusions settled here.

**REC-001 — seller scope accepted in PC-006; other eligibility details unselected:**
The recommendation presented was to start with main-store retail sales to its own end
customers; defer composite reseller supply and reseller-store sales. This keeps
initial ownership, charging, and recovery responsibilities within one business.
The trade-off is delaying composite availability through resellers; if reseller
distribution is essential to launch, choose it explicitly now. This recommendation
does not select Telegram versus Mini App, operator interfaces, payment methods,
custom plans, trials, gifts, or renewal features.

### Q-002 — Main-store customer purchase channels

**Status:** answered; Telegram-only launch scope accepted in PC-007.
**Prerequisite:** PC-006.
**References:** D07/D10/D11; BC-001/F-007; A20/A23/A28.

At launch, should customers be able to buy a composite subscription and retrieve
its subscription URL through the Telegram bot, the Mini App, or both?

**REC-002 — revised recommendation accepted in PC-007:** Launch composite customer purchases and
subscription URL retrieval through the main-store Telegram bot only; defer
composite Mini App checkout. With sales not yet started (BC-001), validate one
complete purchase-to-delivery experience and its failure handling before adding
a second composite checkout surface. The existing bot purchase path (F-007) is
the recommended starting point, not proof that it is technically cheaper or
that future buyers prefer it. The trade-off is postponing a graphical Mini App
checkout and requiring initial composite buyers to use bot interactions.

**Recommendation history:** The earlier suggestion to support both channels was
never accepted. It relied on a customer-interface-continuity rationale unsupported
by the newly supplied launch context, and is superseded by the recommendation
above. The request for revised advice did not itself approve a channel; the
subsequent explicit answer quoted in PC-007 accepted Telegram-only launch scope.

This recommendation does not select operator interfaces, approve all existing
management actions or product modes, remove legacy Mini App functionality, or
set a release date/commitment for later composite Mini App support. Those choices
remain separate.

### Q-003 — Preset products versus customer-built composite plans

**Status:** answered; preset-only launch scope accepted in PC-008.
**Prerequisites:** PC-006/PC-007.
**References:** D07; F-007/F-008; REQUIREMENTS correctness item 6; A23/A24/A28.

For launch, should customers choose only from preset composite plans defined by
the store, or also be able to build custom plans?

**REC-003 — accepted in PC-008:** Launch with preset composite plans only. The store
defines each plan's included nodes, shared allowance, duration, and base price;
the customer chooses a plan rather than choosing their own nodes, allowance,
or duration. This makes the offer and fulfillment expectations easier to explain
and validate before sales begin. The trade-off is less purchasing flexibility
and a need for the store to create additional presets for different needs.
This does not choose exact quota units, unlimited-plan support, activation,
renewal, payment methods, discounts, quantity limits, trial/gift eligibility,
or the interface used by operators to define plans. The six-node fixture remains
an acceptance example, not the only allowed preset or a size limit.

### Q-004 — Launch operator authority

**Status:** answered; owner-only operator scope accepted in PC-009.
**Prerequisites:** PC-006/PC-008.
**References:** D07/D14; A19/A24/A28; constitution III.

At launch, should configuring composite plans and performing manual subscription
management be restricted to the main-store owner, or also available to delegated staff?

**REC-004 — accepted in PC-009:** Restrict those composite operator actions to the
main-store owner at launch. This keeps configuration and manual recovery decisions
with one accountable operator while the launch process is established. The
trade-off is that support actions needing operator intervention must wait when
the owner is unavailable; staff cannot take them over. This does not remove
existing staff permissions for unrelated legacy services. Automated fulfillment,
accounting, and enforcement are separate from manual operator authority, and
the exact manual actions and operator interface remain to be selected. No new
approval step for ordinary customer purchases is proposed by this recommendation.

### Q-005 — Owner's composite administration interface

**Status:** answered; web-admin-only operator interface accepted in PC-010.
**Prerequisites:** PC-007/PC-008/PC-009.
**References:** D07/D10/D14; F-008/F-011; A19/A23/A28.

For configuring composite plans and manually managing composite subscriptions,
should the owner use the existing web admin panel, Telegram admin menus, or both?

**REC-005 — accepted in PC-010:** Use the existing web admin panel as the only launch
interface for composite operator configuration and manual management. Multiple
panels, child credentials, and their individual failure/pending states are easier
to inspect together in an administrative page; one operator interface also limits
the launch UI scope. Customers still buy through Telegram under PC-007.
The trade-off is that the owner needs the web admin panel for these actions and
cannot perform them entirely through Telegram chat. This choice does not select
the exact management actions, alert channels, native-mobile-app support, or
authorize manual off-catalog sales. Existing legacy administration remains covered
by PC-003. Backend architecture belongs to planning.

### Q-006 — Complete fulfillment versus partial service

**Status:** answered; complete-plan gate accepted in PC-011.
**Prerequisites:** PC-001/PC-007/PC-008.
**References:** D10; R02/R05; A02-A06/A20/A28; S02-S04; constitution II/VII.

If payment succeeds and five of a plan's six required nodes provision successfully
but the sixth fails, should the customer wait for the complete plan or receive
partial service immediately?

**REC-006 — accepted in PC-011:** Require the complete purchased node set before customer
access and fulfillment success. Show payment as confirmed and fulfillment as
pending while incomplete; do not deliver a usable subscription payload or individual
credentials for only the ready subset, or label that subset successful fulfillment.
This preserves the preset offer and avoids silently substituting a smaller service.
The trade-off is that failure of one required node delays access to all of them,
including those already provisioned. Six is only the example; the same rule would
apply to every node required by the purchased preset.

This recommendation does not decide how long the customer waits, cancellation or
refund rights, rollback versus recover-forward, retry limits, validity start,
notification-delivery success, or policy for outages after successful fulfillment.
Those depend on this gate and remain separate. Technical proof of readiness and
remote activation mechanics belong in planning and controlled validation; payment
confirmation alone or an ambiguous create result cannot establish readiness.

### Q-007 — Provisioning deadline and failure outcome

**Status:** answered; deadline and failure outcome accepted in PC-012.
**Prerequisite:** PC-011.
**References:** D10; A03-A06/A17/A28; constitution II/VII.

How long should a paid order be allowed to remain incompletely provisioned before
the store cancels it and starts a full refund?

**REC-007 — accepted in PC-012:** Allow up to 15 minutes from verified payment for the
complete node set to become ready. Attempt recovery within that window. If the
complete set is not ready by the deadline, automatically cancel the unfulfilled
order and initiate a full refund; do not deliver a late partial or completed
result from the canceled order. Keep cleanup of already-created credentials
tracked separately from the refund. This gives customers a clear limit on
waiting. The trade-off is canceling some purchases that might have recovered
after a longer outage, with associated refund and cleanup work.

Fifteen minutes is an accepted product deadline, not a measured provisioning time
or demonstrated operational guarantee. Refund destination, completion timing,
early customer cancellation, retry scheduling, and handling total application
outage remain open. "Initiate a full refund" must not be shown as "refund completed"
before the financial effect is confirmed; refunds do not erase cleanup obligations.
No chosen schema, retry algorithm, or worker architecture is implied.

### Q-008 — Destination of a failed-order refund

**Status:** answered; all-store-wallet-credit outcome accepted in PC-013.
**Prerequisite:** PC-012.
**References:** D07/D10; F-012; A03/A28; constitution II/VII.

For a composite order canceled because provisioning failed, should the refund
return to the original funding sources, or may the whole amount become store
wallet credit?

**REC-008 — rejected; PC-013 records the user's selected alternative:**
The recommendation was to return the amount actually paid to its original funding
sources: restore the wallet-funded portion to the wallet, and return externally
paid funds through their original payment route. For mixed funding, refund each
portion once; do not turn the external portion into compulsory store credit.
Where an approved payment route cannot refund automatically, retain a visible
refund obligation for the owner to complete and verify manually. This lets a
customer recover their money when the store could not deliver. The trade-off is
slower external refunds and more owner work than a wallet-only refund policy.

That original-source recommendation is not the chosen policy. PC-013 selects
store-wallet credit without approving every existing gateway. Exact completion
deadline, fees/conversion handling, and discount restoration remain to be decided.

### Q-009 — Start of purchased validity

**Status:** answered; availability-based validity start accepted in PC-014.
**Prerequisites:** PC-011/PC-012.
**References:** D03/D09/D11; F-002; A02/A05/A12/A20; constitution II.

Should the purchased validity period start at payment, when the complete
subscription and its URL are available to the customer in the bot, or at first
VPN use?

**REC-009 — accepted in PC-014:** Start validity when the complete subscription is ready
and its subscription URL is made available for the customer to retrieve in the
Telegram bot. All child credentials share the same expiry derived from that
start. Provisioning delay does not consume the purchased term. Opening a message
or making the first VPN connection does not control the start: time runs once
the complete service is available, even if the customer waits to use it.
This gives one clear entitlement boundary without depending on observing first
traffic. The trade-off is that unused time after availability still counts.

This does not yet settle exact day/time arithmetic, failed proactive Telegram
notification versus failed URL availability, long delivery outages, renewal
anchoring, expiry grace, or compensation for outages after activation. The
creation/activation mechanism belongs to planning; F-002's per-call expiry must
not silently become the new shared validity rule.

### Q-010 — Purchased allowance unit

**Status:** answered; binary GiB and explicit labels accepted in PC-015.
**Prerequisites:** PC-001/PC-008.
**References:** D03; R06; F-002; A07/A12; constitution II/V.

Should composite plan allowances use binary GiB or decimal GB?

**REC-010 — accepted in PC-015:** Retain the current binary quota convention for composites
and clearly label their allowances as GiB in the shop's customer and owner views.
One GiB is 1,073,741,824 bytes, so a 50 GiB preset grants exactly 53,687,091,200
bytes shared across all children. Decimal 50 GB would instead grant 50,000,000,000
bytes. Binary units match the currently inspected provider conversion (F-002)
without silently changing its documented caller expectations. The trade-off is
that GiB is less familiar to some customers than GB, so the label needs a brief
explanation. Third-party VPN-client display conventions are not controlled by
this shop-label decision.

This recommendation does not choose actual presets/prices, fractional plan values,
display precision/rounding, traffic attribution details, unlimited-plan eligibility,
or enforcement tolerance. It does not authorize relabeling unrelated legacy flows.

### Q-011 — Finite versus unlimited launch plans

**Status:** answered; finite allowance and validity accepted in PC-016.
**Prerequisites:** PC-008/PC-014/PC-015.
**References:** D03; R06/R07; A12/A23.

Should every launch composite plan have both a finite data allowance and a finite
validity period, or should unlimited data or unlimited validity also be offered?

**REC-011 — finite-plan scope accepted in PC-016:** Require both a finite, positive data allowance and a
finite, positive validity period for launch composite presets. This keeps each
sale's entitlement and termination conditions explicit while validating the shared
quota feature. The trade-off is that unlimited-data and no-expiry composites cannot
be sold at launch. This does not change unlimited legacy services or set a maximum
quota, duration, or node count. Actual preset sizes/prices, fractional values,
expiry arithmetic, renewal and enforcement guarantees remain separate decisions.

### Q-012 — Availability versus restriction during usage uncertainty

**Status:** partially answered; a short grace period is accepted in PC-017.
Exact timing and post-grace action continue in Q-013.
**Prerequisites:** PC-004/PC-016.
**References:** D02/D08; R06/R07; A09/A13/A16; S05-S07; constitution II/VII.

If a panel stops providing trustworthy usage while its VPN still works, should
the affected subscription keep working or be temporarily suspended?

**REC-012 — grace preference accepted; remaining details proposed in Q-013:**
Allow a brief, explicitly bounded grace period, then
seek suspension of the entire affected subscription if trustworthy accounting
has not recovered, including its reachable children on otherwise healthy panels.
Only permit resumption once usage has been reconciled and the entitlement is
still eligible; accounting recovery must not override exhaustion, expiry, or an
independent operator suspension. This prioritizes limiting exposure to unknown
consumption over uninterrupted service. The trade-off is interrupting working
nodes because another panel's usage cannot be trusted.

**Capability boundary:** A panel that cannot be controlled may continue serving
already-delivered credentials. Requesting suspension of the whole subscription
does not prove all access has stopped; unreachable credentials remain pending
until their state can be confirmed. This recommendation alone does not establish
a hard quota ceiling or bounded outage overshoot. Any such guarantee requires
separately demonstrated enforcement capability under E-001/E-002.

Grace duration and its reference timestamp, normal-operation freshness/cutoff
targets, recovery timing, total-coordinator-outage behavior, and treatment of
irrecoverably missing usage remain subsequent decisions. No numeric default,
polling interval, retry algorithm, or remote quota-allocation design is selected.

### Q-013 — Concrete usage-grace limit and resulting action

**Status:** answered; concrete five-minute policy accepted in PC-018.
**Prerequisite:** PC-017.
**References:** D02/D08; A09/A12/A13/A16; S05-S07; constitution II/VII.

Should the usage-outage policy be five minutes from the last trustworthy reading
for any required meter, followed by attempted suspension of the whole subscription?

**REC-013 — accepted in PC-018:** Use five minutes measured from the last trustworthy
usage reading for each required child/meter. If any required meter reaches that
age without a new trustworthy reading, request suspension of every credential in
the affected subscription, including those on healthy panels. Failed retries,
cached/invalid readings, and process restarts must not restart the countdown.
Confirmed exhaustion or expiry still requires revocation without waiting for
this usage-uncertainty grace to elapse. Resume only after usage is reconciled and
the subscription remains eligible, respecting independent suspension/revocation.

Five minutes tolerates brief reporting failures while limiting how long the
system deliberately leaves reachable credentials enabled under uncertainty.
The trade-off is possible extra consumption during the grace and interruption
of healthy nodes during longer reporting outages. This is a proposed product
threshold, not a measured safe interval or a guaranteed cutoff within five minutes.
Unreachable credentials remain pending and may continue to work until control
returns; this policy does not establish a hard cap on outage consumption.

Normal sample cadence, cutoff propagation bounds, treatment of total-coordinator
outage, irrecoverably lost history, and any paused-time compensation remain open.
Implementation and evidence for the selected threshold belong to planning and
controlled validation, without choosing an algorithm or worker design here.

### Q-014 — Required guarantee on excess usage during outages

**Status:** answered; best-effort launch policy accepted in PC-019.
**Prerequisites:** PC-004/PC-016/PC-018.
**References:** D02; R06/R07; A12/A16; S05-S07; E-001/E-002; constitution II/VI/VII.

Must launch have a proven maximum amount of usage beyond the purchased allowance,
including during panel-control or enforcement-service outages, or is best-effort
cutoff without such an outage bound acceptable?

**REC-014 — rejected; PC-019 records the user's selected alternative:**
The recommendation was to require a finite, tested maximum overrun as a launch
condition, including when panel control is unavailable or the enforcement service
is stopped while VPN traffic continues. Accept that meeting this requirement may
cause temporary access interruptions or delay launch. This limits the business's
exposure to additional consumption; the alternative permits continuing traffic
without an agreed outage-overrun bound until control can recover.

The exact allowed amount would be chosen next if this requirement is accepted.
It is not a zero-overrun guarantee or approval of any numeric tolerance. PC-018
only defines when to request suspension; it cannot establish a bound while the
requesting service is down or a panel cannot be controlled. Feasibility remains
unverified for the deployed panels and existing sessions. Controlled evidence is
required before claiming the bound, and no enforcement architecture is selected
here. A failed feasibility check would require a revised product decision rather
than silently substituting best-effort cutoff for a promised bound.

The user instead accepted best-effort cutoff for launch. A finite outage-overrun
bound must not be retained as an implicit release gate. Relevant controlled
enforcement, accounting, and recovery checks still apply under the selected policy.

### Q-015 — Normal-operation cutoff target

**Status:** answered; 60-second normal-operation target accepted in PC-020.
**Prerequisites:** PC-004/PC-018/PC-019.
**References:** D02; A12/A13/A16; S05/S07; E-002; constitution VI/VII.

When all panels and the enforcement service are operating normally, should every
credential stop accepting new VPN connections within 60 seconds of shared-quota
exhaustion or the common expiry time?

**REC-015 — accepted in PC-020:** Set a maximum 60-second end-to-end target under supported
normal operating conditions, from crossing the purchased shared byte allowance
or reaching the common expiry to denial of new connections with every associated
credential. Include usage-observation/detection delay and remote action delay;
do not start the clock only after the system notices the threshold or treat an
accepted API request as proof of cutoff. Test against supported deployments and
representative load. This provides a measurable launch target alongside PC-019's
explicit outage limitation.

The trade-off is a window in which additional traffic may pass during normal
operation. A tighter target reduces that window but requires tighter operational
timing. Sixty seconds is an accepted product target, not measured current capability,
an allowed extra data grant, or a chosen polling interval. It does not choose a
numeric byte-overrun bound. Established-connection termination, normal freshness
display, and outage-recovery timing remain separate. The five-minute stale-usage
rule is not an additional grace for already-known exhaustion or expiry.

### Q-016 — Connections already open at exhaustion or expiry

**Status:** answered; native panel behavior selected in PC-021.
**Prerequisites:** PC-019/PC-020.
**References:** D02; R07; S05-S07; E-001/E-002; constitution I/III/VI/VII.

At quota exhaustion or expiry, should existing VPN connections also be terminated,
or may they continue until they close naturally?

**REC-016 — rejected; PC-021 records the selected alternative:** Terminate already-open connections as well as blocking
new ones, using the same 60-second end-to-end target under supported normal
operation. Otherwise, a long-lived connection could continue using the service
after the purchased allowance or term is exhausted. The trade-off is interruption
of active downloads, calls, and other sessions. PC-019's best-effort limitation
continues to apply during control/enforcement outages.

This is a proposed product requirement, not proof that supported panels can
terminate the affected sessions. Targeted termination without disrupting unrelated
customers must be demonstrated in controlled checks for recorded panel/core and
protocol versions; a successful disable response cannot substitute for that
evidence. Do not silently weaken the requirement or choose a disruptive shared
infrastructure operation if targeted behavior proves unavailable. Such a finding
would require a product decision or remain an explicit release blocker. No
specific panel operation, connection-kill mechanism, or infrastructure change is
selected in this interview. Behavior for suspension/rotation beyond exhaustion
and expiry remains to be specified where applicable.

The user instead chose supported panel controls without custom core changes or
session-killing logic. The proposed existing-session termination deadline and
targeted-termination capability must not remain implicit launch gates. Public
source findings X-001/X-002 characterize risk, not deployed behavior or passing tests.

### Q-017 — Recovery after a usage-reporting suspension

**Status:** answered; automatic recovery accepted in PC-022.
**Prerequisites:** PC-018-PC-021.
**References:** D08; A09/A12/A13/A16; S06/S07; constitution II/VII.

After suspension because usage reporting stayed stale for five minutes, should
access resume automatically once trustworthy usage is reconciled and the
subscription is still eligible, or require the store owner's approval?

**REC-017 — accepted in PC-022:** Resume automatically when all required usage is
trustworthy and reconciled, the subscription has remaining allowance and time,
and no separate suspension, cancellation, or revocation prohibits access.
Never infer eligibility from a successful connection to the panel alone, treat
missing history as zero, or override an independent restriction. Remote
re-enablement remains pending until confirmed; partial recovery is not reported
as complete recovery.

This restores paid service without waiting for the owner after a temporary
reporting outage. The trade-off is that unstable reporting may cause repeated
suspension and recovery; owner approval offers manual oversight but delays
restoration and adds operational work. This recommendation does not select a
recovery deadline, stability dwell time, compensation, or handling of permanently
lost usage history. Those remain separate choices; no retry or worker design is
selected here.

### Q-018 — Validity during a usage-reporting suspension

**Status:** answered; unchanged expiry accepted in PC-023.
**Prerequisites:** PC-014/PC-018/PC-021/PC-022.
**References:** D03/D08; A12/A13/A16; S06/S07; constitution II/VII.

Should the subscription's validity keep counting during a usage-reporting
suspension, or pause and extend the expiry by that suspension's duration?

**REC-018 — accepted in PC-023:** For launch, retain the fixed common expiry during
these suspensions, with no automatic clock pause or time extension. Recovery
after expiry therefore does not automatically reactivate the subscription.
For example, a subscription due to expire at 18:00 still expires at 18:00 after
a 14:00-14:20 reporting suspension, rather than moving expiry to 18:20.

This keeps the purchased calendar term predictable and avoids treating a
reporting/control outage as proof of complete loss of access: PC-018/PC-021
allow uncertain remote suspension and native continuation of established
connections. The trade-off is that customers can lose usable paid time during
an interruption caused by the service. Pausing would compensate time but would
require an explicit definition of which interval counts despite partial or
unconfirmed cutoff. Discretionary owner compensation and broader outage/refund
policies remain separate, unapproved choices; this recommendation does not
implicitly add or exclude their management flows.

### Q-019 — Initial-release renewal modes

**Status:** answered; customer-initiated full-plan renewal accepted in PC-024.
**Prerequisites:** PC-007/PC-008/PC-014/PC-016.
**References:** D09/D10; A15/A25; F-003/F-008; constitution I/II.

Should launch offer only customer-initiated full-plan renewal through Telegram,
or also automatic renewal and separate data/time add-ons?

**REC-019 — accepted in PC-024:** Offer customer-initiated full-plan renewal through the
main-store Telegram bot; defer automatic renewal and standalone data-only or
time-only add-ons for composite subscriptions. Here, customer-initiated means
the customer chooses and pays for renewal; it does not mean a new requirement
for store-owner approval. A full-plan renewal purchases an allowance and a term
together. Existing single-panel/stock-link behavior remains governed by PC-003.

This gives customers a repeat-purchase path with fewer billing modes to explain
and verify at launch. The trade-off is that customers must take action to renew
and cannot buy just extra data or days. Current manual and automatic legacy
renewals have different accounting behavior (F-003); neither implicitly selects
composite policy. A25's proposed scenario coverage does not require approving
every composite renewal mode.

Eligible renewal plans, early/late renewal, allowance carryover or replacement,
expiry arithmetic, URL/credential continuity, payment methods, partial failure,
and suspended/uncertain subscriptions remain subsequent choices. This question
does not approve any of those policies or a detailed implementation.

### Q-020 — Eligible plans for renewal

**Status:** answered; alternative matching presets accepted in PC-025.
**Prerequisites:** PC-005/PC-008/PC-024.
**References:** D09; A15/A24/A25; constitution I/II.

Should customers be allowed to renew into another offered preset with the same
node configuration but a different allowance or duration, or be limited to
their original plan?

**REC-020 — accepted in PC-025:** Allow renewal into any offered composite preset whose
node configuration matches the purchased subscription's saved configuration,
including presets with different allowance or duration. Renewal must not add,
remove, or replace nodes or change their panel, inbound, protocol, or intended
egress. Compare against what was sold, not merely the original plan's current
name or edited definition. Moving to a different node configuration requires
a separate subscription purchase at launch; topology migration is not included
in this recommendation.

This lets customers change how much service they buy without introducing node
migration into renewal. The trade-off is that customers cannot change locations
or protocols through renewal. Limiting renewal to the original plan would be
simpler to present but unnecessarily restrict allowance/duration choices when
the delivered node configuration is the same.

This does not select carryover, renewal timing, URL/credential rotation policy,
pricing/discount rules, or what happens when no matching preset remains offered.
Those remain separate product choices. No matching algorithm or schema is selected.

### Q-021 — Early renewal eligibility

**Status:** answered; early renewal accepted in PC-026; late-renewal cases remain open.
**Prerequisites:** PC-024/PC-025.
**References:** D09; A15/A25; constitution II.

May a customer renew while the subscription still has both remaining data and
validity, or must they wait until its allowance is exhausted or it expires?

**REC-021 — early eligibility accepted in PC-026; late-renewal cases unselected:** Allow early renewal as well as renewal after exhaustion
or expiry, subject to the separately defined eligibility and reconciliation
rules. Customers should not have to wait for an interruption to purchase their
next full plan. This does not allow renewal to override independent suspension,
cancellation, or revocation, or to ignore uncertain usage.

The benefit is customer control over when to make the purchase. The trade-off
is that early renewal needs explicit treatment of remaining data and time, and
a clear checkout explanation to prevent surprises. Carryover versus replacement,
immediate versus scheduled application, exact expiry arithmetic, recovery from
partial renewal, and limits on successive purchases are not selected here.
Eligibility of expired records is not a promise to retain them indefinitely or
restore deleted credentials; retention and lifecycle boundaries remain open.

### Q-022 — Treatment of remaining data and time on early renewal

**Status:** answered; carryover of both balances accepted in PC-027.
**Prerequisites:** PC-024-PC-026.
**References:** D03/D09; A07/A10/A11/A15/A25; F-003; constitution II.

When a customer renews before expiry with data and time remaining, should the
new plan add to those balances or replace them?

**REC-022 — accepted in PC-027:** Add the purchased allowance to the reconciled unused
allowance and extend the existing common expiry by the purchased duration when
the renewal is successfully applied. Make the additional allowance usable as
part of that renewal rather than scheduling a separate future plan. The combined
allowance shares the extended expiry; the old remainder does not expire on a
separate earlier date. Apply the addition once to the subscription, not once per
child, and retain accrued-consumption evidence rather than erasing history.

For example, if 20 GiB and 10 days remain at successful application, buying a
50-GiB/30-day renewal leaves 70 GiB available and 40 days until the common expiry.
Any traffic consumed before that boundary reduces the old remaining allowance;
missing or stale usage must not be used to overstate the balance.

This avoids forfeiting paid value merely because the customer renews early,
including when choosing another eligible preset. The trade-off is that the
resulting balance can exceed the selected preset's headline allowance/duration,
so checkout and service details must explain the combined entitlement. Replacement
would give a simpler fresh-plan balance but discard unused paid data and time.

This recommendation covers early renewal while both balances remain. Treatment
after expiry or exhaustion, overrun debt, maximum accumulated balances, successive
purchases, and renewal with uncertain usage or partial remote failure remain
separate choices. It does not select a storage scheme, counter-reset mechanism,
or precise day-to-time conversion.

### Q-023 — Unused data when renewing after expiry

**Status:** answered; expired data does not carry forward under PC-028.
**Prerequisites:** PC-016/PC-024-PC-027.
**References:** D03/D09; A12/A15/A25; constitution II.

If a subscription expires with unused data, should a later renewal restore that
unused data or should it have expired with the old term?

**REC-023 — accepted in PC-028:** Unused data expires with the old validity term. Allow
an otherwise eligible retained subscription to renew after expiry, but grant
only the new plan's allowance, with its full duration starting when renewal is
successfully applied. Do not revive the expired unused balance or deduct the
elapsed gap from the newly purchased duration. Preserve historical usage and
entitlement evidence even though the old unused data is no longer spendable.

For example, expiry with 20 GiB unused followed two days later by successful
50-GiB/30-day renewal yields 50 GiB and 30 days, not 70 GiB or 28 days. Early
renewal under PC-027 still carries both balances forward.

This gives the validity deadline a clear commercial meaning and avoids retaining
expired unused data as a future credit. The trade-off is that a customer who
misses the deadline loses unused data; restoring it would be more forgiving but
would make validity primarily an access pause rather than the end of that data's
usability. The checkout must make this distinction clear.

This question does not select renewal after quota exhaustion while time remains,
overrun debt, deleted/canceled/revoked-service recovery, retention duration,
payment-versus-application failures, or the handling of usage uncertainty.

### Q-024 — Remaining time when renewing after quota exhaustion

**Status:** partially answered; time preservation with a 45-day limit recorded
in PC-029. The cap's meaning is pending Q-025.
**Prerequisites:** PC-024-PC-028.
**References:** D03/D09; A12/A15/A25; constitution II.

If the data allowance is exhausted but the subscription has not expired, should
renewal preserve the remaining time or start a new term from renewal?

**REC-024 — accepted only with the user's 45-day qualification in PC-029:** Allow renewal after quota exhaustion and preserve any
time still remaining at successful application. Grant the new purchased data
allowance and extend the existing common expiry by the purchased duration.
Exhaustion alone should not forfeit unexpired time. For example, with exactly
zero data remaining and 10 days until expiry, a 50-GiB/30-day renewal yields
50 GiB and 40 days. If the original expiry has already passed at application,
PC-028 instead gives the new duration from successful application.

This consistently preserves unexpired paid time, as early renewal does under
PC-027. The trade-off is that frequent renewals by heavy data users can accumulate
a longer validity balance than the selected preset's headline duration. Starting
a new term would limit that accumulation but discard remaining paid time.

This example assumes no overrun beyond the old allowance. Treatment of overrun
debt is a separate question; it is not silently forgiven or deducted here.
Maximum accumulated balances, repeated-purchase limits, partial failure, and
independent suspension/revocation remain separate. Renewal is not permission
to bypass usage reconciliation or discard accrued-consumption evidence.

### Q-025 — Meaning of the 45-day renewal maximum

**Status:** answered; total-remaining cap accepted in PC-030 and monthly launch
scope supplied in PC-031. **Prerequisite:** PC-029.
**References:** PC-027; D03/D09; A15/A25; constitution II.

Does the 45-day maximum mean total validity remaining immediately after renewal,
or a maximum of 45 old days carried forward in addition to the purchased duration?

**REC-025 — accepted in PC-030 for quota-exhausted renewal:** For the quota-exhausted renewal being discussed, use
45 days as the maximum total remaining validity after successful renewal.
For a purchased term no longer than 45 days and an old balance within that limit,
retain only the old time that fits alongside the full purchased duration.
For example, 10 old days plus a 30-day plan gives 40 days; 20 old days plus that
plan gives 45 days, carrying 15 and forfeiting 5 old days. Show the resulting
expiry and any forfeited time before payment. Do not silently shorten the newly
purchased duration.

This directly bounds the accumulated remaining term. A 45-day carryover-only
limit would instead allow 45 old days plus a new 30-day plan, or 75 days total.
The total cap's accepted trade-off is loss of some otherwise unexpired paid
time when the limit is reached, as recorded in PC-030.

Plans longer than 45 days and old balances already above 45 require a separate
policy; the recommendation does not authorize silently shortening either.
Whether the cap also limits PC-027's early renewal while data remains is another
scope decision. Do not silently replace that accepted full-carryover policy.
No cap computation/storage implementation is selected here.

### Q-026 — Apply the validity cap to renewal with data remaining

**Status:** answered; cap applies to ordinary early renewal under PC-032.
**Prerequisites:** PC-027/PC-030/PC-031.
**References:** D03/D09; A15/A25; constitution II.

Should the 45-day total-remaining-validity cap also apply when a customer renews
early while still having data left?

**REC-026 — accepted in PC-032:** Apply the same cap to ordinary early renewal as to
quota-exhausted renewal. Retain PC-027's unused-data carryover, but qualify its
time carryover: preserve the newly purchased term and only as much old time as
fits within 45 days total. Disclose any forfeited old time and resulting expiry
before payment. This refinement of PC-027 is accepted in PC-032.

For a 30-day purchased term, a customer with 20 GiB and 20 days remaining who
renews with 50 GiB receives 70 GiB and 45 days, forfeiting 5 old days. With
10 old days, the earlier 70-GiB/40-day example remains unchanged.

One rule avoids making the validity limit depend on whether the customer renews
just before or just after the last data is consumed. The trade-off is limiting
the previously agreed full time carryover even for customers whose service is
still active. The alternative is to keep unrestricted time carryover for those
customers and reserve the cap for quota-exhausted renewal. This question does
not impose a data-balance cap, choose exact month/day arithmetic, or authorize
shortening unrelated existing subscriptions outside a renewal transaction.

### Q-027 — Exact meaning of a monthly term and a day

**Status:** answered; 30 elapsed days accepted in PC-033.
**Prerequisites:** PC-014/PC-028/PC-030-PC-032.
**References:** D03/D09; A12/A15/A25; constitution II/VII.

For launch, should a monthly plan mean exactly 30 elapsed 24-hour days, or one
calendar month from its start?

**REC-027 — accepted in PC-033:** Define the monthly launch term as exactly 30 elapsed
24-hour days (720 hours, 2,592,000 seconds), and label the duration as "30 days"
in purchase and renewal offers. Define the 45-day cap using the same elapsed-time
unit (1,080 hours, 3,888,000 seconds). Measure from the already selected activation
or renewal boundary, retaining a common absolute expiry for all credentials.
Month lengths, local midnight, timezone changes, and daylight-saving changes must
not add or remove purchased time; do not round remaining carryover to whole days
when determining the resulting expiry. Display timezone is a separate choice.

This provides the same purchased duration for every customer and makes renewal
and the cap consistent. The trade-off is that expiry may not fall on the same
calendar date or local wall-clock time the following month. Calendar-month
billing would match an anniversary expectation but vary the actual term and
require explicit handling of dates absent from the following month.

This selects product time semantics only. Storage representation, scheduling,
clock coordination, formatting precision, and delayed/partially applied renewal
handling remain separate; no implementation is prescribed by the arithmetic.

### Q-028 — Who bears usage beyond the purchased allowance

**Status:** answered; store-funded overrun accepted in PC-034.
**Prerequisites:** PC-019-PC-021/PC-027-PC-033.
**References:** D02/D08/D09; A07/A12/A15/A16/A25; S05-S07; constitution II/VII.

If the customer uses more than the purchased allowance before cutoff takes
effect, should that excess reduce the next renewal's allowance or be absorbed
by the store?

**REC-028 — accepted in PC-034:** For launch, the store absorbs confirmed overrun from
the old entitlement. Do not charge it to the customer's wallet, create a debt,
or subtract it from a later renewal. For example, confirmed usage of 53 GiB
against an old 50-GiB allowance followed by a 50-GiB renewal grants the full
new 50 GiB, not 47 GiB. Preserve the actual 53-GiB usage evidence and the
3-GiB overrun; do not rewrite consumption to hide the excess. Usage after the
effective renewal boundary consumes the renewed allowance normally.

This keeps a prepaid purchase predictable under the selected best-effort cutoff
and native existing-session behavior. The trade-off is that the store bears
additional consumption, potentially substantial during outages, without an
agreed hard overrun bound. Deducting from renewal would recover that cost but
could deliver less than the advertised purchase and make delayed readings turn
into unexpected customer debt.

This recommendation does not grant an extra allowance or cancel cutoff/recovery
obligations. Unknown usage remains unknown; attribution of readings spanning
renewal and settlement when usage cannot be reconciled still require a separate
policy. It selects no meter algorithm, remote quota scheme, or worker design.

### Q-029 — Renewal checkout when usage cannot be reconciled

**Status:** answered; payment waits for reconciled usage under PC-035.
**Prerequisites:** PC-004/PC-018/PC-027/PC-034.
**References:** D08/D09/D10; A09/A11/A15/A25; F-003; constitution II/VII.

When missing or unreliable usage prevents a trustworthy renewal balance, should
renewal payment wait until reconciliation, or may the customer pay for a pending
renewal while the store resolves it?

**REC-029 — accepted in PC-035:** Temporarily block renewal payment while known usage
uncertainty prevents reliable carryover and renewal accounting. Explain that
renewal is temporarily unavailable while usage is reconciled; do not knowingly
debit the wallet or invite a new external renewal payment under that condition.
Make checkout available again once the accounting prerequisite is satisfied,
subject to the other renewal eligibility rules. Missing usage must not become
zero, and absorbing confirmed overrun under PC-034 does not erase uncertainty.

This avoids taking payment for an entitlement whose balance cannot yet be
established. The trade-off is that the customer cannot complete renewal during
the reporting problem and may reach exhaustion or expiry while waiting. Taking
payment for a pending renewal would let them pay once and wait, but requires
additional delay, cancellation, and compensation rules.

This is a checkout eligibility proposal, not a change to PC-018's five-minute
access grace or an instruction to suspend sooner. It does not select a sample
freshness threshold or require perfectly simultaneous readings. A reporting
failure after payment initiation/verification, an already-issued payment link,
permanent missing history, or a partial remote renewal still needs an explicit
recovery policy. This question does not silently cancel or refund existing
financial obligations, and it selects no reconciliation algorithm.

### Q-030 — Successful fulfillment of a paid renewal

**Status:** answered; all required nodes must be ready under PC-036.
**Prerequisites:** PC-011/PC-024-PC-035.
**References:** D09/D10; A14/A15/A25; F-003; constitution II/VII.

If payment is verified but only some credentials can be updated, should renewal
remain pending until every required credential is ready, or count as fulfilled
with partial availability?

**REC-030 — accepted in PC-036:** Require every credential in the purchased node set
to be confirmed ready for the renewed entitlement before declaring renewal
successful or making that entitlement effective. Display verified payment and
pending renewal separately. A successful request for some children or an
unverified panel response is not completed renewal.

While renewal is pending, the old entitlement continues to govern access: retain
its remaining allowance and original expiry, including ordinary consumption and
cutoff. Do not deliberately suspend an otherwise eligible old entitlement solely
because renewal is pending, and do not silently grant the new allowance or term
on only a subset of nodes. Existing outage, stale-usage, and independent access
restrictions still apply; this is not a promise of uninterrupted service when
the underlying panel is unavailable.

This extends the complete-plan principle to renewal while protecting previously
purchased service. The trade-off is that one failed panel delays renewal even
if others are ready; the old entitlement can exhaust or expire during that wait.
Unlike initial provisioning, failed renewal must reconcile changes to existing
credentials and preserve prior usage evidence. Do not assume remote mutations
are atomic: any partially applied state must remain visible and recoverable.

The maximum wait, cancellation/refund policy, reconciliation of partial remote
effects, and carryover consequences if the old expiry passes during processing
remain separate product decisions. No rollback algorithm, staging method, schema,
or worker architecture is selected here. Feasibility requires controlled evidence.

### Q-031 — Timeout and refund for an incomplete paid renewal

**Status:** answered; 15-minute cancellation and full wallet credit accepted in PC-037.
**Prerequisites:** PC-012/PC-013/PC-036.
**References:** D09/D10; A05/A06/A14/A15/A25; constitution II/IV/VII.

Should an incomplete paid renewal use the same 15-minute deadline and full
store-wallet refund as failed initial provisioning?

**REC-031 — accepted in PC-037:** Measure 15 minutes from verified renewal payment.
If the complete renewal cannot be confirmed within that window, automatically
cancel that renewal and initiate credit of its entire paid amount to the
customer's store wallet, including any externally funded portion, exactly once.
Do not substitute the undiscounted nominal price for the actual amount paid.
A canceled/refunded renewal must not later grant its purchased benefits.

Preserve the prior subscription under its old allowance and expiry, accounting
for time elapsed and traffic actually consumed. A renewal refund is not
cancellation of the original subscription or permission to delete its existing
credentials, erase consumption, or restore already-spent allowance. Reconcile
any partial renewal changes against the entitlement that should still apply;
retain identities and pending remote work after the refund. This does not
promise instantaneous reversal on an unavailable panel.

This gives customers a predictable wait and a consistent store-wallet remedy.
The trade-off is that a slow renewal is canceled even if a panel recovers just
after the deadline, while the store can still have remote reconciliation work
after returning the money. The old entitlement may legitimately be expired or
exhausted by then; the refund does not itself reactivate it.

Refund completion timing, total-application-outage catch-up, customer cancellation
before the deadline, accidental benefits already consumed during partial remote
application, and retry eligibility while reconciliation remains pending are
separate choices. No rollback algorithm or financial storage design is selected.

### Q-032 — Timely renewal payment but completion after the old expiry

**Status:** answered; timely-payment carryover protection accepted in PC-038.
**Prerequisites:** PC-027/PC-028/PC-034-PC-037.
**References:** D03/D09/D10; A12/A15/A25; constitution II/VII.

If renewal payment is verified before the old expiry but all-node completion
happens after it, should unused data remain eligible for carryover or lapse
because of the processing delay?

**REC-032 — accepted in PC-038:** Protect data-carryover eligibility when renewal payment
is verified strictly before the old expiry and that renewal successfully completes
within its 15-minute window. Do not forfeit otherwise eligible unused data solely
because processing crosses the expiry. Reconcile actual usage through the renewal
boundary: data consumed while waiting cannot be granted again, and confirmed
overrun does not reduce the newly purchased allowance under PC-034.

For example, expiry is 18:00, verified payment is 17:59, and complete renewal
application is 18:03. If 20 GiB remains after reconciliation, renewing with
50 GiB yields 70 GiB. Since the old time has elapsed, the new 30-day term runs
from successful application at 18:03. The old entitlement still expires at
18:00 while renewal is pending; eligibility protection does not extend access
or make renewal effective on only some nodes.

PC-038 refines PC-028 for a timely paid renewal delayed by processing. Payment
verified at or after expiry still follows PC-028's no-expired-data-carryover rule;
starting checkout alone does not reserve carryover. A renewal canceled under
PC-037 does not revive expired data or preserve it for a subsequent purchase.

The benefit is that store/panel processing delay does not penalize an on-time
payment. The trade-off is an additional distinction between the payment boundary
used for carryover eligibility and the successful-application boundary used for
effective service. No meter attribution algorithm is selected. Ambiguous usage
must remain explicit rather than being guessed away.

### Q-033 — URL and credential continuity through renewal

**Status:** answered; URL and credential continuity accepted in PC-039.
**Prerequisites:** PC-001/PC-005/PC-025/PC-036.
**References:** D09/D11/D14; A14/A20/A21/A25; constitution I/II/III.

Should a normal successful renewal preserve the existing subscription URL and
all child credentials so customers can keep using their imported configurations?

**REC-033 — accepted in PC-039:** Keep the same subscription URL and existing child
credential identities during ordinary renewal, including switching between
eligible presets with the same saved node configuration. Do not require a new
URL import or replacement credentials merely because a subscription was renewed.
Update entitlement information under the accepted accounting/validity rules;
do not silently create duplicate independently usable identities as a side
effect of renewal. Renewal must not undo a separate authorized revocation or
credential replacement.

This makes renewal convenient and avoids disrupting customer configuration.
The trade-off is that a previously copied URL or credential remains usable
under the renewed entitlement unless separately revoked or replaced. Renewal
is not a compromise-recovery action. Hiding or changing the URL alone also
cannot revoke credentials already downloaded, as preserved in PC-004.

Which launch actors can request replacement, whether URL and credential changes
are paired, and the timing/failure behavior of replacement remain later product
choices. Recovery of deleted or externally lost credentials is not implicitly
approved by this ordinary-renewal policy. No token format or provider mutation
mechanism is selected.

### Q-034 — Customer self-service versus owner-managed replacement

**Status:** answered; customer self-service with a 24-hour limit selected in PC-040.
**Prerequisites:** PC-007/PC-009/PC-010/PC-039.
**References:** D10/D11/D14; A14/A20/A21/A28; F-008/F-011; constitution III/VII.

At launch, may customers replace a leaked subscription URL/credentials themselves
through the Telegram bot, or should replacement be handled by the store owner?

**REC-034 — rejected; PC-040 records the selected alternative:** Make replacement owner-managed through the existing
web-admin interface at launch. Customers can contact support to request help,
but cannot directly trigger composite URL/credential replacement through a
self-service action. No delegated-staff replacement permission is added; PC-009
already limits composite operator authority to the main-store owner. This is
a proposal for the remaining customer self-service scope, not a re-questioning
of that settled operator role.

This keeps an infrequent, disruptive operation under owner supervision while
launch behavior is established. The trade-off is that a customer with leaked
access must wait for the owner, while self-service could recover access sooner
and reduce support work. Existing legacy replacement flows are not removed by
this proposed composite-only boundary.

The support contact mechanism, identity/ownership verification experience,
whether URL and all credentials are replaced together, cutoff timing, existing
sessions, and partial-failure behavior remain separate choices. This recommendation
does not prescribe new ticketing infrastructure or approve implementation.

The user instead requires customer self-service once every 24 hours. Owner-only
replacement must not remain an implicit launch restriction; PC-009 still governs
operator authority separately from the customer's own authorized self-service.

### Q-035 — Scope and starting event of the replacement cooldown

**Status:** answered; per-subscription completion-based cooldown accepted in PC-041.
**Prerequisite:** PC-040.
**References:** D10/D11/D14; A14/A20/A21/A28; constitution II/III/VII.

Should the 24-hour limit apply separately to each subscription, measured from
its last successfully completed replacement, or across all of a customer's
subscriptions?

**REC-035 — accepted in PC-041:** Use a per-subscription rolling 24-hour cooldown starting
at successful replacement completion. A replacement completed at 10:00 UTC makes
that subscription eligible again at 10:00 UTC the following day, not at the next
calendar midnight. Replacing one subscription does not block replacement of a
different subscription owned by the same customer. The first replacement has
no cooldown from purchase or delivery, subject to other eligibility rules.

A failed replacement does not consume the allowance. While a replacement is
pending or its outcome is uncertain, repeated customer requests must refer to
that operation rather than start another independent replacement. Retrying or
recovering the same operation is not another customer replacement allowance.
Ordinary renewal must not reset or bypass a running cooldown.

This avoids penalizing customers for technical failure or preventing recovery
of a second independently leaked subscription. The trade-off is that customers
with several subscriptions can perform more replacements across their account
than under an account-wide limit. Rate protection against repeated failed
requests can be designed separately without presenting those failures as a
successful replacement or silently imposing a new product cooldown.

The actual replacement scope and its completion criteria, owner overrides,
eligibility during suspension/expiry, and partial-failure recovery remain open.
This chooses no locking, retry, or rate-limiter implementation.

### Q-036 — What leaked-access replacement changes

**Status:** answered; URL and all-child identity replacement accepted in PC-042.
**Prerequisites:** PC-004/PC-039-PC-041.
**References:** D08/D11/D14; A10/A14/A17/A20/A21; S07; constitution II/III/VII.

Should leaked-access replacement change both the subscription URL and every
child credential, revoking the old set while keeping the existing entitlement?

**REC-036 — accepted in PC-042:** Provide one customer replacement action that replaces
the subscription URL and every child credential in the purchased node set.
Invalidate the old URL and revoke the old credentials through supported panel
controls; changing a URL alone must not be represented as revoking configurations
already downloaded. Keep the same subscription, node configuration, shared
allowance, expiry, and accumulated usage history. Actual consumption during
replacement still counts; replacement does not grant fresh quota, reset the term,
or revive expired/exhausted/suspended access.

Deliver the replacement URL to the authorized customer through Telegram and
explain that their devices must import it. Old URLs must not redirect to or
reveal replacement secrets. The trade-off is disruption across the customer's
devices, including ones whose individual credentials were not known to have
leaked. In return, the action covers a leaked URL that could expose the entire
node set rather than leaving other copied credentials usable for new access.

The sequence of old-access revocation versus new delivery, partial failures,
normal-operation timing, existing-session behavior, and what constitutes complete
replacement remain subsequent decisions. This does not promise instantaneous
termination of active connections or select API methods, credential formats,
or a replacement algorithm. PC-041's cooldown starts only when the eventual
completion criteria are met.

### Q-037 — Prioritize revocation or continuity during leaked-access replacement

**Status:** answered; revocation-first replacement accepted in PC-043.
**Prerequisites:** PC-004/PC-040-PC-042.
**References:** D08/D11/D14; A14/A17/A20/A21; S07; constitution II/III/VII.

Should leaked-access replacement start revoking old access before the complete
replacement is ready, even if that interrupts the customer's service?

**REC-037 — accepted in PC-043:** Prioritize revocation: invalidate the old URL and start
revoking all old credentials as soon as the authorized replacement is accepted,
rather than intentionally retaining leaked access until new delivery is ready.
Apply revocation to reachable nodes even if another panel is unavailable. Keep
unreachable/uncertain old credentials visibly pending; do not claim access is
fully revoked just because the URL is invalid or a request was accepted.

Deliver the usable replacement URL only when the complete replacement node set
is ready and old credentials are confirmed revoked for fresh authentication.
Until those conditions are met, report replacement/revocation pending rather
than success, and do not start PC-041's successful-replacement cooldown. Do not
restore known leaked credentials solely to recover from a failed replacement.

This reduces deliberate exposure after a reported leak. The trade-off is that
the legitimate customer may lose working access while a panel outage prevents
completion; one unreachable old credential can also remain usable while other
credentials have been revoked. Waiting for replacement readiness would preserve
continuity longer but intentionally keep leaked credentials available longer.

Existing sessions require a separate explicit policy: fresh-authentication
revocation is not proof that all old traffic stopped. Numeric cutoff and delivery
targets, long-running failure escalation, and interruption compensation remain
open. This selects customer-visible ordering and completion expectations, not
an algorithm or atomic remote transaction; feasibility remains unverified.

### Q-038 — Already-open leaked sessions after replacement

**Status:** answered; native existing-session handling accepted in PC-044.
**Prerequisites:** PC-021/PC-042/PC-043.
**References:** D02/D11/D14; A14/A17/A21; S07; X-001/X-002;
E-001/E-002; constitution V/VI/VII.

Should leaked-access replacement use the same native panel handling of existing
sessions accepted for exhaustion/expiry, even if an already-open leaked session
continues after its old credential is replaced?

**Why this consequence needs an explicit choice:** PC-021 already rules out
custom Xray changes/session-killing logic for the feature. This question does
not reopen that implementation boundary; it resolves what the customer is
promised when recovering from a leak. Static evidence X-001/X-002 distinguishes
fresh authentication from ongoing traffic, including activity within an existing
multiplexed tunnel. Deployed behavior remains unverified.

**REC-038 — accepted in PC-044:** Accept supported 3x-UI handling of already-established
sessions during replacement, consistently with PC-021. Complete replacement
according to PC-043's invalid-old-URL, old-fresh-authentication-revoked, and
all-new-nodes-ready criteria, without an additional requirement to force-close
every existing session. Do not promise that replacement immediately disconnects
every device or stops all old traffic; explain the native-session limitation.
Characterize actual behavior in controlled checks against recorded versions.

This respects the chosen panel boundary and avoids turning replacement into
a custom core-control feature. The trade-off is that a holder of leaked access
may retain an already-authenticated connection for an unbounded, unverified
duration. Rejecting that limitation would require evidence of supported native
termination behavior or a revised launch requirement, not silently adding core
modifications or disruptive shared restarts.

Normal replacement timing and operator escalation remain separate choices. No
specific endpoint or session-termination technique is selected by this question.

### Q-039 — Normal-operation completion target for replacement

**Status:** answered; 60-second normal-operation target accepted in PC-045.
**Prerequisites:** PC-040-PC-044.
**References:** D11/D14; A14/A17/A20/A21; S07/S09; E-001/E-002;
constitution VI/VII.

When the bot and all required panels are healthy, should complete leaked-access
replacement be available to the customer within 60 seconds of accepting their
authorized request?

**REC-039 — accepted in PC-045:** Set a 60-second end-to-end completion target under
supported normal operating conditions, starting when the authorized replacement
request is accepted. By that deadline, the old URL must be invalid, all old
credentials must reject fresh authentication, every replacement node must be
ready, and the new URL must be available for the customer to retrieve through
Telegram. Include preparation, panel action, verification, and delivery
availability; do not start the clock after remote work or reset it on retry.
Customer reading/importing the URL is outside this completion interval.

This gives a short, measurable interruption target after choosing revocation
first. The trade-off is that every required panel must complete its part within
the interval, which may require narrowing the supported operating envelope if
controlled validation cannot meet the target. This is proposed product behavior,
not a demonstrated capability, polling interval, or hardcoded node maximum.

PC-044's native existing-session limitation remains: the target does not promise
termination of already-open sessions. During panel/bot outages, retain pending
revocation/replacement and recovery responsibility rather than claim success
or restore leaked access. Missing this target does not itself select automatic
cancellation, compensation, or an owner-escalation deadline; those are separate.
Evidence must cover recorded versions and representative supported load before
claiming compliance. No worker or provider algorithm is selected.

### Q-040 — Owner attention for a replacement that remains incomplete

**Status:** answered; 15-minute owner escalation accepted in PC-046.
**Prerequisites:** PC-009/PC-010/PC-041-PC-045.
**References:** D10/D11/D14; A14/A17/A21; S07; constitution II/VII.

Should a replacement still incomplete 15 minutes after request acceptance be
escalated to the store owner while recovery remains pending?

**REC-040 — accepted in PC-046:** At 15 minutes from acceptance of the authorized
replacement request, flag an incomplete operation as needing owner attention
in the web admin and attempt a Telegram notification to the owner. Tell the
customer the replacement remains pending and needs support attention. Do not
present an attempted notification as delivered when it failed; keep the pending
operation visible independently of notifications.

Continue recoverable automatic reconciliation where possible without waiting
for owner approval, while retaining unresolved obligations for manual recovery
if automatic attempts are exhausted. The 15-minute point is an escalation
threshold, not cancellation, a successful-replacement cooldown trigger, or
permission to restore known leaked credentials. Retries/restarts do not move
the original escalation threshold. Telegram is a notification channel here;
manual composite operator actions remain in the web admin under PC-010.

This gives transient problems time to recover while keeping an interrupted
customer from waiting indefinitely without operator visibility. The trade-off
is that a short-lived outage can still generate a support alert; a longer
threshold reduces alerts but delays human attention. PC-045's normal 60-second
target remains separate, and a miss must not be hidden until 15 minutes.

Owner response/resolution time, reminder cadence, total-application-outage
catch-up, interruption compensation, and numeric retry budgets are not selected.
This is an accepted future product notification policy, not authorization to
send messages or create a reminder/automation during this interview.

### Q-041 — Owner override of the customer replacement cooldown

**Status:** answered; audited owner cooldown override accepted in PC-047.
**Prerequisites:** PC-009/PC-010/PC-040-PC-046.
**References:** D10/D11/D14; A14/A20/A21/A28; constitution II/III/VII.

Should the store owner be able to authorize an urgent replacement before the
customer's 24-hour cooldown ends, for example after a second leak?

**REC-041 — accepted in PC-047:** Permit the authenticated main-store owner to override
only the replacement cooldown through the web admin, recording the actor, affected
subscription, reason, and outcome. Customers and delegated staff cannot use this
override. The same complete URL/all-credential replacement, revocation priority,
accounting preservation, completion checks, and timing/escalation rules apply.

An override does not start a competing operation while replacement is already
pending or uncertain; recover the existing operation instead. A successfully
completed owner-triggered replacement starts a fresh 24-hour customer cooldown
for that subscription. A failed attempt does not start it. Other eligibility,
ownership, suspension, and revocation restrictions are not bypassed merely by
overriding the cooldown.

This provides an urgent recovery path when a customer leaks replacement access
again within a day. The trade-off is additional owner/support responsibility and
an exception to the customer rate limit, which needs an audit trail. Without
the override, the customer would have to wait for the remaining cooldown before
another replacement even when a second leak is verified.

No general authority to adjust balances, waive other lifecycle constraints,
or run direct core commands is implied. Other owner-management capabilities and
the support intake experience remain separate product choices.

### Q-042 — Completion time for failed-order wallet credit

**Status:** answered; usable credit within 60 seconds accepted in PC-048.
**Prerequisites:** PC-012/PC-013/PC-037.
**References:** D10; A05/A06/A25; F-012/E-005; constitution II/VII.

When a failed initial purchase or renewal is canceled, should its full wallet
credit become visible and spendable within 60 seconds under normal application
and database operation?

**REC-042 — accepted in PC-048:** Complete the agreed full store-wallet credit within
60 seconds of cancellation under normal application/database conditions, without
waiting for remote credential cleanup or reversal of partial renewal changes.
The balance and refund status must reflect the completed credit and allow its
use in another eligible purchase. Post it exactly once even across retries,
duplicate callbacks, and restarts. A completed credit must not depend on a
Telegram notification being successfully delivered.

For example, verified payment at 12:00 followed by the incomplete-order deadline
and cancellation at 12:15 produces usable wallet credit no later than 12:16
under those normal conditions. The 15-minute deadline is not restarted, and
60 seconds is not measured from eventual remote cleanup.

This makes the promised refund usable promptly instead of leaving the customer
waiting on an unreachable panel. The trade-off is that money may already have
been returned while remote access or mutation reconciliation remains unresolved;
the store must retain and pursue those obligations. Credit remains the actual
paid amount, including external funding, under PC-013/PC-037.

An application/database outage does not make an unposted credit complete.
Keep pending financial obligations visible/recoverable; catch-up timing after
total outage and escalation if credit cannot be posted remain separate decisions.
This target does not select a schema, transaction implementation, or worker.

### Q-043 — Initial fulfillment deadline includes URL availability

**Status:** answered; initial URL availability is required by PC-049.
**Prerequisites:** PC-007/PC-011-PC-014/PC-048.
**References:** D10/D11; A03-A06/A20/A28; constitution II/VII.

If all credentials are ready but the customer still cannot retrieve a usable
subscription URL through Telegram by 15 minutes after verified payment, should
the initial order be canceled and refunded?

**REC-043 — accepted in PC-049:** Include delivery availability in the same initial
15-minute deadline: every required node must be ready and the usable subscription
URL must be available for the authorized customer to retrieve through the bot.
If that combined condition is not met by the deadline, cancel the initial order,
apply PC-013/PC-048's full-wallet-credit policy, and retain cleanup obligations
even when all credentials have already been created. Do not start a second
15-minute delivery window after provisioning or deliver the canceled order late.

A failed automatic notification alone does not fail fulfillment if the customer
can retrieve the usable URL from the bot's subscription-management flow. The
customer need not open the notification, request the URL, or connect to complete
fulfillment; actual availability is the gate. By contrast, saving the URL only
in internal records while the customer-facing retrieval flow is unavailable
does not establish delivery availability. Retry failed notifications without
duplicating payment, provisioning, or delivered credentials.

This aligns the waiting limit with PC-014's availability-based validity start
and the customer's ability to obtain the purchase. The trade-off is canceling
a fully provisioned order because delivery remains unavailable; treating it as
fulfilled instead would leave a paid customer without access to their URL.

This addresses initial delivery only. A later outage after successful fulfillment
does not automatically become an initial-order refund under this rule. Total-app
outage catch-up and the observable evidence used to establish availability remain
separate operational/validation questions. No notification architecture is selected.

### Q-044 — Main-store buyers with reseller or discount status

**Status:** answered; ordinary buyer eligibility accepted in PC-050.
**Prerequisites:** PC-006/PC-007/PC-008.
**References:** D07; A03/A19/A28; F-007/F-009/F-014; constitution I/III.

Should an account with reseller or discount status still be allowed to buy a
composite subscription through the main store as an ordinary customer?

**REC-044 — accepted in PC-050:** Allow otherwise eligible main-store customer accounts
to use the ordinary Telegram composite checkout regardless of reseller/discount
status. The purchased subscription belongs to that purchasing customer account
in the main store. Do not exclude an account solely because it also has a
reseller role or discount tier.

This follows the current distinction between buyer status and the business
operating the sale (F-014), avoiding an arbitrary restriction on the main-store
customer population. PC-006 still excludes composite reseller storefronts and
reseller supply flows; allowing these accounts as buyers does not enable those
flows, reseller GB credit, fixed-product inventory, or cross-tenant management.

The trade-off is that checkout must apply explicit eligibility and pricing rules
for these accounts rather than treating every reseller-related flag as a reason
to block access. The alternative would reserve launch composites for ordinary
retail-status accounts only. Whether existing tier discounts, coupons, commissions,
or referral rewards apply to composite purchases remains a separate product
choice; source facts describing them are not approval of those benefits.

### Q-045 — Discounts on initial composite purchases

**Status:** answered; initial-purchase tier discounts and codes accepted in PC-051.
**Prerequisites:** PC-008/PC-013/PC-050.
**References:** D07/D10; A03/A19/A28; F-014/F-015; constitution I/II.

Should initial composite purchases honor the existing configured tier discounts
and eligible discount codes, or use the preset's undiscounted price at launch?

**REC-045 — accepted in PC-051:** Honor applicable existing tier discounts and discount
codes on initial main-store composite purchases. Apply the tier reduction first,
then one eligible discount code to the reduced price, following the ordinary
catalog's pricing order. Do not grant a discount merely because `is_reseller`
is set: the assigned tier must be enabled and use the discount model. Retain
the maximum of the configured buyer-specific, permanent-tier, and applicable
quantity percentages rather than adding them together. This does not itself
approve multi-unit checkout.

Preserve integer-floor percentage-discount arithmetic in the shop's existing
integral price unit. Compute a percentage code against the tier-adjusted amount;
cap either fixed or percentage code reduction at that amount so the price
cannot become negative. Respect configured code activity, usage limits, expiry,
product/category restrictions, and minimum/maximum purchase thresholds. As in
the inspected ordinary flow, code amount eligibility uses the tier-adjusted
price. Financial verification and repeat-safety remain mandatory; the cached
code-amount weakness in F-015 is not an approved shortcut around valid pricing.

This keeps configured customer benefits consistent across the main-store catalog.
For example, a base price of 100 with a 10% tier reduction and an eligible 10%
code becomes 81, not 80. The trade-off is reduced revenue per composite sale,
including stacked tier/code reductions across a service spanning several panels;
the owner must account for that when setting the preset price and discounts.

Discounts affect the amount paid, not the purchased node set, allowance, or term.
Failed-order refunds remain limited to the actual paid amount under PC-013.
Renewal discounts, commissions/referral rewards, zero-total checkout, quote
validity, coupon-use restoration after failure, and payment-method restrictions
remain separate choices. No new prices, percentages, coupon records, currency
conversion, or financial storage design is selected by this recommendation.

### Q-046 — Pricing and discounts for composite renewal

**Status:** answered; renewal pricing and discounts accepted in PC-052.
**Prerequisites:** PC-024-PC-026/PC-050/PC-051.
**References:** D03/D07/D09/D10; A03/A12/A15/A25; F-016; constitution I/II.

Should composite renewals use the selected preset's current price with the same
applicable tier-then-code discount rules as initial composite purchases, without
an additional early-renewal discount at launch?

**REC-046 — accepted in PC-052:** Price a composite renewal from the selected eligible
preset's current base price, not the subscription's historic purchase price.
Apply the buyer's applicable configured tier discount and then one eligible code
using PC-051's eligibility, restrictions, order and rounding rules. Assess code
product/category eligibility against the selected renewal preset. Do not apply
the separate legacy early-full-renewal discount to composites at launch, either
as an alternative automatic reduction or as a third stacked discount. Keep
existing single-panel and stock-link renewal pricing unchanged within scope.

This gives composite buyers one understandable discount policy for purchase and
renewal and avoids a third discount layer on top of the accepted carryover.
For a selected preset priced at 100, an applicable 10% tier reduction and eligible
10% code produce 81. The trade-off is lower renewal revenue than charging the
undiscounted preset price, while customers do not receive the separate legacy
early-renewal promotion. Matching legacy renewal behavior instead would exclude
tiers/codes and retain its separately configured early-renewal incentive.

F-016 establishes that this would be a new composite policy, not existing renewal
parity. Discounts affect price only; accepted data/time carryover and caps remain
unchanged. Quote validity and changes before payment, zero-total orders, coupon
restoration, commissions/referral rewards, and payment-method restrictions are
separate unresolved choices. No checkout quantity policy, numeric discount
configuration, or settlement design is selected by this recommendation.

### Q-047 — Referral rewards and reseller commissions at launch

**Status:** answered; launch rewards deferred in PC-053.
**Prerequisites:** PC-006/PC-050-PC-052.
**References:** D07/D10; A03/A19/A28; F-015/F-016; constitution I/II.

Should composite purchases and renewals generate purchase-based referral rewards
or referring-reseller commissions at launch?

**REC-047 — accepted in PC-053:** Defer both purchase-based reward types for composites
at launch. Neither an initial composite purchase nor a composite renewal should
create referral reward credit or referring-reseller commission credit. Do not
consume or mark fulfilled the customer's first-purchase referral-reward
eligibility merely because a composite purchase occurred; it remains available
for a later otherwise-qualifying legacy purchase. Do not accrue deferred rewards
or promise retroactive payouts when composite rewards are introduced later.

Keep the buyer's accepted tier/code discounts and ordinary buyer eligibility.
Preserve existing referral relationships, accrued wallet credit, and affected
legacy reward behavior. Invite-only rewards are separate from purchase-triggered
rewards and are not disabled by this recommendation; composite free-product
rewards, trials, and gifts still need their own scope decision.

This narrows launch financial obligations while sales have not started, avoiding
additional payout eligibility, discount-basis, duplicate-payment, and reversal
rules for a service that already has full-wallet failure refunds. The trade-off
is no purchase-based incentive for people directing customers to composites.
The alternative is to include rewards now and explicitly settle their qualifying
events, amount basis, completion timing, and refund treatment. Existing reward
hooks and reseller buyer status do not themselves approve those payouts.

Observable implication if accepted: a referred buyer can receive the agreed
discounts and buy or renew a composite without any new reward/commission wallet
entry, any queued future payout, or consumption of first-purchase reward
eligibility. Existing legacy reward tests remain compatibility checks.

### Q-048 — One subscription per checkout

**Status:** answered; one subscription per checkout accepted in PC-054.
**Prerequisites:** PC-001/PC-008/PC-011-PC-013/PC-051/PC-052.
**References:** D07/D10; A02-A06/A19/A28; constitution II/VII.

Should each launch composite checkout buy exactly one subscription, with customers
able to buy additional independent subscriptions through separate checkouts?

**REC-048 — accepted in PC-054:** Limit each initial composite checkout to one purchased
subscription. Customers may own multiple subscriptions by making separate
purchases; do not impose a one-subscription-per-customer rule. Each purchase has
its own URL, independent child credentials, allowance, validity, fulfillment
outcome, and refund obligation. Never pool separate purchases' allowances or
expiry. Child-node count remains independent of purchase quantity and is not
limited to six. A renewal targets one existing subscription.

For PC-051/PC-052 pricing, the checkout quantity is one: any configured quantity
discount must qualify at quantity one. Neither node count nor separate orders
are aggregated to qualify for higher quantity-discount thresholds. Other eligible
tier/code discounts remain available. This does not select capacity targets or
authorize bypassing existing general account restrictions.

This keeps each payment's success or failure tied to one entitlement, avoiding
multi-subscription partial fulfillment and split refunds at launch. The trade-off
is repeated checkout for customers wanting several subscriptions and no batch
quantity discount. Supporting multi-unit checkout is the alternative and would
require separately agreed partial-success and refund outcomes.

Observable implication if accepted: two separate purchases yield two independently
managed subscriptions; failure of one follows its own refund policy and does not
alter the other. A multi-node subscription still counts as quantity one.

### Q-049 — Complimentary composite issuance at launch

**Status:** answered; blanket deferral rejected. Composite tests and the launch
campaign accepted in PC-055/PC-056; other complimentary flows remain open.
**Prerequisites:** PC-006-PC-010/PC-016/PC-031/PC-053/PC-054.
**References:** D07/D10/D14; A03/A19/A27-A29; F-008; constitution I/III.

Should launch support complimentary composite issuance through trials, referral
gift products, or owner-created free subscriptions outside customer checkout?

**REC-049 — rejected; retained only as interview history:** Defer these complimentary composite issuance flows at
launch. Trial requests, referral free-product rewards, and manual owner grants
must not create a composite subscription. Preserve their affected legacy
single-panel/stock-link behavior. Owner-only composite administration does not
implicitly authorize creation of complimentary composites. Do not silently
substitute a composite into an existing trial/gift configuration.

This keeps launch issuance centered on the agreed preset checkout and its
fulfillment rules, without adding trial eligibility, gift ownership, or manual
grant rules. The trade-off is no dedicated free composite trial or complimentary
grant for prospective customers. Including these flows now would require
explicit eligibility, allowance, duration, and delivery choices; it must not
silently override the accepted finite monthly launch catalog.

This question is limited to complimentary issuance outside checkout. A legitimate
discount code reducing a checkout to zero is a separate unresolved financial
case, not implicitly prohibited or approved here. Paid purchases for another
person, ownership transfer, and remedies for existing customers also remain
separate choices. Controlled acceptance fixtures are not a customer acquisition
flow; this decision neither prohibits them nor authorizes running them now.

Observable implication if accepted: existing trial, referral-product, and manual
grant entry points cannot issue composites, while affected legacy behavior is
preserved. Composite checkout remains governed by its independently accepted
eligibility, pricing, and fulfillment rules.

### Q-050 — What counts toward the campaign's 150-user limit

**Status:** answered; successful-fulfillment counting accepted in PC-057.
**Prerequisites:** PC-055/PC-056; F-017.
**References:** D10/D14; A03-A06/A19/A28; constitution II/III/VII.

Should the campaign count successfully fulfilled trials, with places held during
provisioning, rather than permanently consuming a place for every attempted claim?

**REC-050 — accepted in PC-057:** Give eligible users places in order of accepted claim
requests. Hold a place and the user's ordinary test allowance while provisioning
is pending, so successful grants plus pending claims cannot exceed 150. Count
the claim as successful only when all required nodes are ready and the complete
subscription URL is available to that customer through Telegram. A failed push
notification alone is not failure if the URL is retrievable. Repeat requests
must refer to the same pending claim, not allocate another place or subscription.

If provisioning definitively fails without fulfillment, release the campaign
place and the user's test allowance so another eligible claim can use the place
and the affected customer can retry. An unknown remote outcome remains pending
until reconciled; a timeout alone is not evidence that nothing was issued. Retain
all cleanup obligations. Do not label 150 in-flight claims as 150 completed
giveaways: temporarily stop accepting more claims while all places are occupied,
and close the campaign when 150 grants are successfully fulfilled. A successfully
issued trial's later expiry/exhaustion does not replenish a campaign place.

This preserves the intended giveaway for 150 recipients rather than spending
places on panel failures, while preventing concurrent over-allocation. The trade-
off is that unresolved claims can temporarily hold campaign capacity. Counting
every attempt permanently instead is simpler to explain operationally but can
end the campaign with fewer than 150 recipients. No additional fraud/identity
verification, reservation implementation, or failure timeout is selected here.

### Q-051 — When the promotional trial's validity starts

**Status:** answered; availability-based test activation accepted in PC-058.
**Prerequisites:** PC-014/PC-033/PC-055-PC-057.
**References:** D03/D10; A03-A06/A12/A19; constitution II/VII.

Should the promotional trial's 15-day clock start only when all required nodes
are ready and its complete URL is retrievable through Telegram?

**REC-051 — accepted in PC-058:** Apply the availability-based activation rule to all
composite test plans: start their configured duration when the complete service
is ready and the URL is available to the eligible customer through Telegram.
For the initial promotion, 15 days means exactly 15 elapsed 24-hour days
(360 hours, 1,296,000 seconds) from that point, with one common expiry across all
children. Provisioning time does not consume the trial term. Request acceptance,
first child creation, notification opening, and first VPN connection are not
activation events. No pause or restart of this clock arises merely because the
customer waits to retrieve/import/use the available URL.

This matches the purchased-subscription rule and gives the full advertised trial
duration after fulfillment. The trade-off is that customers who leave a ready
trial unused still consume its validity; first-use activation would avoid that
but would require a separate activation policy and reliable first-use evidence.
This question does not choose a pending-claim timeout, compensation, or conversion
to a paid subscription.

Observable implication if accepted: a claim accepted at 12:00 and fulfilled at
12:07 expires exactly 360 hours after 12:07, regardless of later import time.
Different children must not start separate 15-day periods during provisioning.

### Q-052 — Completion deadline for composite test claims

**Status:** answered; 15-minute trial deadline accepted in PC-059.
**Prerequisites:** PC-012/PC-049/PC-055-PC-058.
**References:** D10/D14; A03-A06/A19/A28; constitution II/VII.

Should an accepted composite test claim have a 15-minute fulfillment deadline,
after which it cannot be delivered late and moves to failure recovery?

**REC-052 — accepted in PC-059:** Allow up to 15 minutes from acceptance of the eligible
claim for every required node to become ready and the complete URL to become
retrievable through Telegram. Apply this to the launch campaign and other
composite tests. Retries and restarts do not restart the clock. A definitive
failure may end the attempt sooner; there is no requirement to wait out the
deadline when failure is already established.

If still incomplete at the deadline, stop that claim from becoming a later
delivery, tell the customer it could not be completed within the deadline, and
retain any remote reconciliation/cleanup obligations. For confirmed failure
without fulfillment, release the user's test allowance and any campaign place
under PC-057. If the remote outcome is uncertain, keep those holds pending until
reconciliation, distinguish that from final failure, flag owner attention in web
admin, and attempt an owner Telegram notification. An attempted notification is
not confirmed delivery. Do not invent a successful grant or release holds merely
because 15 minutes elapsed. A late remote success for a canceled, unfulfilled
claim must be reconciled for cleanup, not supplied to the customer as a late trial.

No payment was collected for this test claim, so this failure creates no wallet
refund or monetary credit. A retry after release is a new eligible claim with
its own availability check; it does not retain permanent campaign priority.

This gives free claims the same customer-visible waiting limit as paid initial
fulfillment while preserving PC-057's treatment of uncertain effects. The trade-
off is that a trial delayed by a longer outage must be requested again after
failure is resolved, and uncertain outcomes can hold quota beyond 15 minutes.
The alternative is to keep the claim deliverable after that point and treat
15 minutes only as an escalation threshold.

Total-application-outage catch-up, numeric retry budgets, owner resolution time,
and exact cleanup mechanics remain unresolved or deferred to planning. This is
a proposed future notification policy, not authorization to send messages now.

### Q-053 — Campaign eligibility after an ordinary test-usage reset

**Status:** answered; strict separation from general resets accepted in PC-060.
**Prerequisites:** PC-055-PC-059; F-018.
**References:** D10/D14; A03/A19/A28-A31; constitution I-IV.

Should the launch campaign remain one successful grant per Telegram user, with
its 150-user total and closure preserved even when the owner resets ordinary
test usage?

**REC-053 — accepted in PC-060:** Keep ordinary `MAX_TEST_PER_USER` / `test_used` behavior
for eligibility across test plans, including the owner's existing test-usage
reset capability. Separately, the initial campaign permits only one successful
grant per main-store Telegram user for the lifetime of this campaign. An ordinary
test-usage reset must not erase campaign participation or successful-claim count,
return a completed campaign place, or reopen a campaign closed at 150 recipients.
Changing the configured ordinary test maximum likewise must not grant a repeat
of this campaign. Trial expiry or deletion must not erase the evidence needed
to enforce those campaign limits.

A previously successful campaign recipient whose ordinary test allowance is
reset can qualify for another eligible test plan under the normal rules, but
cannot claim this launch promotion again. A user who previously took a legacy
test, has no successful campaign grant, and later becomes eligible through an
ordinary reset can claim the promotion if a campaign place is still available.
Confirmed failed claims remain retryable under PC-057/PC-059 and do not become
successful campaign participation. Existing legacy reset behavior is preserved;
reset must not duplicate or discard unresolved composite claim obligations.

This treats "150 users total" as distinct recipients rather than repeated grants
to the same accounts. The trade-off is that a general test reset cannot rerun the
same giveaway for previous recipients; a later promotion would require a distinct
explicit campaign decision. No additional real-person/device verification is
selected: the user identity remains the authenticated Telegram account in the
main store. This does not claim prevention of one person using multiple accounts.

Observable implication if accepted: after 150 fulfilled grants, resetting ordinary
test usage leaves the campaign closed while allowing other eligible tests. Before
closure, a reset recipient is refused a duplicate campaign grant without losing
their eligibility for another available test plan.

### Q-054 — Converting a composite test into a paid subscription

**Status:** answered; trial-to-paid renewal accepted in PC-061, with the new
standard quick-check default recorded separately in PC-062.
**Prerequisites:** PC-024-PC-039/PC-052/PC-055-PC-060.
**References:** D03/D09/D10/D14; A12/A15/A19/A25; constitution II/VII.

Should a composite test customer be able to buy a paid full-plan renewal on that
same subscription, using the already accepted renewal rules?

**REC-054 — accepted in PC-061:** Allow a fulfilled composite test, including a campaign
trial, to become paid through the Telegram full-plan renewal flow. The selected
paid preset must match the subscription's saved node configuration under PC-025.
Use the accepted current-preset tier-plus-code pricing, complete-node fulfillment
gate, 15-minute paid-renewal deadline/full-actual-payment wallet refund on failure,
and existing renewal eligibility/restriction rules. Keep its URL and child
credentials through ordinary successful conversion as in PC-039.

Apply the same carryover policy to remaining trial benefits: eligible unused
trial data and time carry forward with the purchased quota and 30-day term,
subject to the 45-day total remaining validity cap. After expiry, unused data
lapses, subject to the already agreed pre-expiry verified-payment protection.
Actual usage remains recorded; confirmed old overrun is not charged against the
new paid allowance. Example: 10 GiB and 5 days remaining plus a 50-GiB/30-day
paid preset yield 60 GiB and 35 days at successful application. Failure leaves
only the original trial entitlement, less elapsed time and actual consumption;
it does not replenish or extend the trial.

Conversion does not reset ordinary test usage, return a campaign place, erase
campaign participation, or grant another free test. Without a matching paid
preset, the customer can buy a separate paid subscription through normal checkout;
no silent node migration is authorized. Later renewals follow the same paid
renewal rules. No automatic charge or compulsory conversion is introduced.

This gives the launch giveaway a direct path to a paid service without requiring
another URL import. The trade-off is that unused promotional benefits can increase
the first paid period's data/time, which the store must include in campaign cost.
The alternative is to require a separate purchase with a new URL and no transfer
of trial benefits. This is a proposed composite product rule, not a claim that
current legacy trials already support identical conversion behavior.

### Q-055 — Exact unit for the standard quick-check allowance

**Status:** initially clarified without approval; later binary unit/label
recommendation accepted together with Q-056 in PC-064. The ten-minute wording
remains superseded by PC-063/PC-064, not reinstated by this acceptance.
**Prerequisites:** PC-015/PC-062; F-019.
**References:** D02/D03/D10; A03/A07/A19; constitution I/II.

For the standard "200 MB" quick-check test, should the allowance mean binary
200 MiB (209,715,200 bytes), consistent with the existing test conversion and
the agreed binary GiB policy, or decimal 200 MB (200,000,000 bytes)?

**REC-055 — unit/label accepted in PC-064; ten-minute duration superseded:** Use 200 MiB = 209,715,200 bytes, one shared allowance
across the subscription, and explicitly label it MiB in composite administration
and customer-facing allowance information. Retain the 10-minute validity from
PC-062. Do not relabel or change unrelated legacy plans through this decision.

This is consistent with PC-015's binary units and the existing 3x-UI test path's
effective MB arithmetic (F-019). The trade-off is approximately 4.86% more data
than decimal 200 MB and a less familiar but precise unit label. Decimal MB is a
valid alternative if that is the intended advertised amount; it must be explicit
rather than inferred from a legacy field name. No storage representation or
customer-display rounding policy is selected by this question.

### Q-056 — Configurable quick-check default using the current admin units

**Status:** answered; configurable 200-MiB/one-hour default accepted in PC-064.
**Prerequisites:** PC-055/PC-058/PC-062/PC-063; F-018/F-019.
**References:** D02/D03/D10/D14; A03/A07/A12/A19; constitution I/II.

Should the standard general composite test default be 200 in the existing MB
field and 1 hour, with both values remaining owner-configurable?

**REC-056 — accepted in PC-064:** Use 200 in the current test allowance field, preserving
its existing binary meaning on the 3x-UI path: 200 MiB = 209,715,200 bytes shared
across all children. Use 1 elapsed hour (3,600 seconds) as the standard duration,
starting at complete availability under PC-058. These are configurable default
values, not new limits, fixed constants for all tests, or restrictions on creating
other plans. Preserve current whole-hour administration under PC-063 and ordinary
shared per-user quota under PC-055.

One hour is the shortest positive whole-hour setting in the existing admin. It
keeps the quick-check offer as short as the selected interface allows, while
requiring no minute-level capability. The trade-off is a longer validity window
than the withdrawn ten-minute idea, and existing binary MB semantics provide
approximately 4.86% more bytes than decimal MB. The user can choose different
default values; all remain distinct from the 15-GiB/15-day capped campaign.

This recommendation does not require renaming unrelated legacy fields or changing
their units. The byte meaning is explicit for the specification; REC-055's
proposed relabeling was not approved and must not be silently imported here.
Initial active-plan selection and handling of later plan edits for issued trials
are separate questions, not selected by a configurable default.

### Q-057 — Leaked-access replacement for free composite tests

**Status:** answered; trial replacement parity accepted in PC-065.
**Prerequisites:** PC-040-PC-047/PC-055-PC-064.
**References:** D11/D14; A14/A17/A19/A21; constitution II/III/VII.

Should free composite tests also support customer-requested leaked-access
replacement under the same rules as paid composite subscriptions?

**REC-057 — accepted in PC-065:** Extend PC-040-PC-047's replacement behavior to issued
composite tests, including the capped campaign and standard quick-check plan.
First replacement is immediately eligible; successful completion starts the
same rolling 24-hour cooldown per subscription. Failed attempts do not consume
the cooldown, and pending retries remain the same operation. Preserve the same
URL-and-every-child-credential rotation, revoke-first ordering, complete-delivery
gate, 60-second normal target, 15-minute owner escalation, native existing-session
limitation, and audited owner cooldown override.

Replacement retains actual usage, remaining allowance, and original expiry.
It does not grant a new trial, reset ordinary test usage, return a campaign place,
or erase participation. An expired/exhausted/restricted trial must not be restored
to usable access by replacement. Trial-to-paid conversion does not reset the
same subscription's replacement cooldown; it remains ordinary renewal under
PC-061. This question does not introduce a new entitlement extension or override.

This gives trial users the same protection when an access link leaks and keeps
one replacement policy across the trial-to-paid transition. The trade-off is
additional multi-panel work for a free, potentially short-lived test; its clock
continues running during replacement. The alternative is to reserve self-service
replacement for paid subscriptions and require support for trial leaks.

### Q-058 — Customer disable/resume access without pausing validity

**Status:** answered; customer access control accepted in PC-066.
**Prerequisites:** PC-014/PC-018/PC-022/PC-023/PC-039/PC-058/PC-061/PC-065.
**References:** D03/D11/D14; A12/A14/A17/A19/A21; F-020;
constitution II/III/VII.

Should customers be able to disable and resume access to their own composite
subscriptions, both paid and free tests, while expiry continues unchanged?

**REC-058 — accepted in PC-066:** Offer customer-controlled access disable/resume through
Telegram for both paid and test composite subscriptions. Disabling requests that
all child credentials reject fresh connections; URL hiding alone is insufficient.
It does not stop the validity clock, save unused time, reset data, replenish usage,
rotate the URL/credentials, or grant compensation. Clearly describe this as
disabling access, not freezing the subscription term. Existing connections use
the already agreed native panel behavior, so continued traffic is not promised
to stop immediately and actual usage remains accounted for.

Resume restores only the customer's own disable request and only if the
subscription is otherwise eligible: unexpired, allowance remaining, required
usage sufficiently trustworthy under the agreed reporting/recovery rules, and
no independent owner/security/recovery restriction. It cannot override expiry,
exhaustion, stale-usage suspension, revocation, or incomplete leaked-access
replacement. Automatic recovery, renewal (including trial conversion), and
credential replacement must not silently clear the customer's disable choice.
The customer can request resume; remote completion remains distinct from that
request and pending outcomes remain visible until confirmed for required nodes.

This provides reversible customer control without creating a validity-freezing
benefit or separate time-accounting policy. Extending it to tests is an explicit
composite choice: F-020 shows current legacy tests lack this control. The trade-
off is additional multi-panel lifecycle work, and a disabled trial can expire
without being used. Existing legacy toggle eligibility/behavior remains preserved
within affected scope.

Observable implication if accepted: disabling a trial with 40 minutes left and
resuming 10 minutes later leaves at most 30 minutes, not 40. Resume after expiry
cannot restore access. A subscription voluntarily disabled before a renewal
remains disabled after that renewal succeeds. Numeric completion/escalation
targets and rapid conflicting requests remain unresolved; no toggle algorithm,
worker, or endpoint is selected here.

### Q-059 — Completion and escalation targets for access disable/resume

**Status:** answered; completion/escalation targets accepted in PC-067.
**Prerequisites:** PC-019-PC-021/PC-045/PC-046/PC-066.
**References:** D02/D11/D14; A14/A17/A19/A21; S07/S09;
E-001/E-002; constitution II/VI/VII.

Should access disable/resume use a 60-second normal completion target and
15-minute owner escalation if the accepted request remains unresolved?

**REC-059 — accepted in PC-067:** Under supported normal conditions, complete the
authorized, eligible customer's requested access-state change within 60 seconds
of acceptance, including remote application and confirmation across required
nodes. For disable, every child must reject fresh authentication; native existing-
session handling remains separate. For resume, every required child must be
ready for eligible access, subject to the restrictions in PC-066. Do not start
the clock after panel calls or restart it on retries/restarts. Known-ineligible
resume requests must explain the blocking condition, not promise activation.
Recheck continued eligibility: a newly expired/exhausted/restricted subscription
cannot be enabled merely to satisfy a previously accepted resume request.

If unresolved at 15 minutes from request acceptance, flag owner attention in
web admin, attempt an owner Telegram notification, and show the customer the
pending/blocked state and support path. Show a missed 60-second target when it
occurs rather than hide it until escalation. Notification failure must not erase
pending work or be reported as delivery. Continue recoverable reconciliation
where possible while preserving manual recovery responsibility after automatic
attempts are exhausted. The 15-minute point is escalation, not automatic
cancellation, rollback, or reversal of the customer's desired access state.

Panel/control outages retain PC-019's best-effort cutoff limitation: pending is
not proof of all-node disable or resume. Keep expiry running and account for
actual usage throughout. No automatic expiry extension or wallet compensation
arises merely from this access-state operation missing its target.

Using the same targets as leaked-access replacement gives customers and the
owner a consistent expectation. The trade-off is owner alerts during extended
outages and the need to demonstrate the 60-second target with recorded versions
and supported load. These are proposed product targets, not existing measured
capabilities, polling intervals, or worker decisions. Total-application-outage
catch-up, owner response time, and competing requests remain separate questions.

### Q-060 — Automatic refunds for unused service after fulfillment

**Status:** answered; no automatic unused-service refunds accepted in PC-068.
**Prerequisites:** PC-011-PC-014/PC-037/PC-048/PC-061/PC-066.
**References:** D03/D10/D14; A03-A06/A12/A15/A25/A28;
F-021; constitution II/VII.

Should launch composites automatically refund unused data or time when a customer
changes their mind or voluntarily stops using successfully fulfilled service?

**REC-060 — accepted in PC-068:** Do not offer automatic change-of-mind or prorated
unused-service refunds after successful fulfillment at launch. This applies to
initial paid purchases, successful paid renewals, and trial-to-paid conversions.
Voluntary non-use or customer access disable does not create wallet credit,
original-payment reimbursement, or monetary value for unused allowance/time.
Do not introduce an implicit buyback rate for remaining data or validity.

The already accepted full-wallet refunds for failed paid fulfillment/renewal
remain required. A later service outage or other operator fault is a separate
remedy question, not silently classified as voluntary non-use. Owner-approved
goodwill credits/manual remedies remain unresolved; this recommendation does
not approve them or forbid them. It also does not decide whether customers can
permanently cancel/delete a fulfilled subscription or how its access is revoked.

This avoids pricing unused time and data, including carried promotional benefits,
and makes launch finances predictable. The trade-off is less flexibility for a
customer who stops using a working service. The alternative is an explicit
post-fulfillment refund policy with qualifying conditions, calculation basis,
cutoff time, and access-revocation consequences.

Observable implication if accepted: a customer who voluntarily disables a
successfully delivered plan with 30 GiB and 15 days remaining receives no
automatic wallet credit. The same customer still receives the agreed refund if
a later paid renewal fails under PC-037. Clearly present the launch refund terms
before checkout; do not describe this narrower policy as a decision about every
possible dispute or failure remedy.

### Q-061 — Owner-approved compensation for service failures and support cases

**Status:** answered; owner compensation accepted in PC-069, with required
multi-customer selection added in PC-070.
**Prerequisites:** PC-009/PC-010/PC-013/PC-023/PC-048/PC-067/PC-068.
**References:** D10/D14; A03-A06/A19/A25/A28; F-021; constitution II/III/VII.

Should launch compensation for post-fulfillment service failures and other
support/goodwill cases be manually approved by the owner as store-wallet credit?

**REC-061 — accepted in PC-069, extended by PC-070:** Allow the store owner, through web administration, to
grant a specified positive store-wallet credit for a composite support case,
including post-fulfillment service failure or a discretionary goodwill exception.
The owner chooses the amount case by case; no automatic proration, outage-to-money
formula, automatic original-payment refund, or automatic time/data extension is
introduced for these cases at launch. Record the actor, affected customer and
subscription, reason, amount, and confirmed/pending outcome. Ensure the same
approved action cannot credit twice through retries, duplicate submissions, or
restarts. Report a failed or pending credit honestly and keep it recoverable.

This credit is a distinct support decision. It does not itself renew, extend,
reset, disable, revoke, or delete the subscription or change test/campaign
eligibility/history. Any lifecycle action remains separately authorized under
its own policy. Preserve the automatic, exact-amount failed-fulfillment refunds
already accepted; an owner must not be required to approve those guaranteed
refunds. Existing credited/refunded amounts must remain visible to the owner
when making a further support decision so it is explicit rather than an
accidental duplicate settlement.

This provides a remedy for real support cases without requiring a launch
compensation formula for every outage. The trade-off is owner workload and
case-by-case outcomes rather than a guaranteed automatic compensation schedule.
The alternative is an explicit automatic service-failure remedy with qualifying
conditions, measurement, and amounts; those have not been agreed.

Observable implication if accepted: one owner-approved credit of a chosen amount
adds that amount to the correct customer's store wallet once, with an audit trail,
while subscription allowance, expiry, and access state remain unchanged by the
credit action itself. Other staff and customers cannot authorize the credit.
Numeric owner-response/credit-completion targets, compensation budgets or caps,
and support-case eligibility promises are not selected by this recommendation.

### Q-062 — Amount semantics for multi-customer compensation

**Status:** answered; equal amount per unique recipient accepted in PC-071.
**Prerequisites:** PC-069/PC-070.
**References:** D10/D14; A03/A19/A28; constitution II/III/VII.

Should the owner-entered bulk compensation amount apply in full to each selected
customer, rather than being a total budget divided between them?

**REC-062 — accepted in PC-071:** Enter one positive amount per selected customer, with
the same amount applied to each unique selected customer in that action. A
customer appearing through several subscriptions or selections is one recipient,
not several credits. Before authorization, show the resolved recipients, unique
recipient count, amount per customer, total credit, and reason. For example,
selecting ten customers and entering 50 shop price units means 50 each and 500
total, not 5 each. This example does not choose a currency or actual credit.

For launch, use separate actions for groups that need different amounts rather
than a per-recipient amount editor or automatic splitting of a shared budget.
Preserve PC-069's customer/subscription context, audit, and repeat-safe crediting.
No unselected recipient may be added after the owner approves the resolved
selection without a new authorization of the changed selection.

This gives the owner a predictable total and avoids division/rounding or hidden
multiple credits for customers with several subscriptions. The trade-off is
separate actions when different customers merit different amounts. The
alternative is a shared-budget or individually varied bulk credit workflow,
which requires its own allocation and rounding policy.

Batch-size limits, interrupted-action recovery outcomes, and selection/filter
design remain separate; no all-or-nothing versus partial-commit architecture is
selected here. Owner authorization here describes the future product flow,
not permission to issue any real credit during this interview.

### Q-063 — Customer-requested permanent cancellation after fulfillment

**Status:** answered; permanent customer cancellation accepted in PC-072.
**Prerequisites:** PC-004/PC-005/PC-060/PC-066/PC-068/PC-069.
**References:** D11/D14; A14/A17/A19/A26/A29-A31; F-021;
constitution II-IV/VII.

Should customers be able to permanently cancel their own fulfilled paid or
free-test composite subscription through Telegram?

**REC-063 — accepted in PC-072:** Offer permanent cancellation for a customer's own
fulfilled composite subscription, including free tests, with an explicit
confirmation that it ends that subscription without an automatic unused-service
refund. Distinguish this from PC-066's reversible access disable. Once accepted,
invalidate the subscription URL and pursue revocation of every child credential;
removing the subscription from a list or hiding its URL is not completed
revocation. Old fresh authentication must be blocked; native panel handling of
already-open sessions remains the chosen boundary, with no promise to kill them.

The canceled subscription cannot be resumed or renewed, and recovery must not
reactivate it. A customer wanting service later makes a separate eligible
purchase or test claim; cancellation itself neither restores test allowance nor
returns a completed campaign place. Preserve the financial/usage/ownership
history and all identities/pending cleanup needed for recovery and auditing.
Permanent service cancellation does not mean immediate erasure of all records.
Distinguish cancellation accepted, remote revocation pending, and confirmed
all-child revocation; do not report confirmed cutoff when a panel is unreachable.

This lets customers end access without contacting support while keeping deletion
from discarding recovery responsibility. The trade-off is an irreversible choice
that gives up remaining service without automatic compensation. Reversible access
disable remains available for customers who may return. The alternative is to
reserve permanent cancellation for owner-assisted support at launch.

Observable implication if accepted: a customer-confirmed canceled subscription's
old URL cannot supply usable credentials; remote cutoff stays visibly pending
until confirmed for all children. Retrying cancellation does not refund, issue
new access, or erase campaign participation. Cancellation during pending renewal/
replacement/credit, numeric completion/escalation targets, customer archive display,
and record-retention periods remain unresolved. No record-deletion algorithm or
data-retention architecture is selected by this recommendation.

### Q-064 — Permanent cancellation while a paid renewal remains unfulfilled

**Status:** answered with a revised sequence in PC-073: finish the in-flight
renewal first, then revoke and refund it fully, even if it succeeds after the request.
**Prerequisites:** PC-013/PC-036/PC-037/PC-048/PC-068/PC-072.
**References:** D09/D10/D14; A03-A06/A15/A25/A28; F-012/F-021;
constitution II/IV/VII.

If a customer permanently cancels while a verified-paid renewal is still
unfulfilled, should cancellation also stop that renewal and refund its payment
as store-wallet credit?

**REC-064 — full renewal refund accepted; immediate interruption sequence replaced by PC-073:** Allow permanent cancellation to take precedence over
a paid renewal that has not successfully fulfilled when cancellation is accepted.
Cancel that unfulfilled renewal, prevent late renewal benefits or reactivation,
and refund its full actual verified payment exactly once as store-wallet credit,
including wallet and external funding. Use PC-048's normal-condition target:
the credit is visible and spendable within 60 seconds of the renewal's confirmed
cancellation, independent of remote cleanup or notification success. Do not wait
out the original 15-minute renewal deadline after the customer has canceled.

This refund concerns an unfulfilled paid operation; it does not refund unused
service already delivered on the underlying subscription. If the renewal had
already fulfilled before cancellation was accepted, PC-068/PC-072 apply and
there is no automatic unused-service refund for that completed renewal. The
customer's confirmation must make the applicable renewal/refund outcome clear.
Do not infer the effective ordering solely from a stale screen or an ambiguous
panel response. Uncertain renewal/payment outcomes remain visibly pending for
reconciliation rather than fabricated as fulfilled or canceled; cancellation's
access-revocation responsibility must still be retained.

Preserve all remote identities, partial changes, accounting and recovery work.
Late remote renewal effects must be reconciled toward the canceled subscription's
revoked state, not used to restore it. Repeated cancellation and payment callbacks
must not create additional refunds or another renewal. This applies equally to
a pending paid trial-to-paid conversion. Original trial usage/campaign history
is not reversed by canceling that paid conversion.

This avoids keeping money for a renewal the system must no longer deliver,
while retaining the agreed no-refund policy for fulfilled service. The trade-off
is an additional cancellation/payment race that must have an auditable outcome.
The alternative is to block permanent cancellation until the renewal resolves,
leaving reversible disable as the immediate customer control.

Late payment arriving after cancellation, pre-verification checkout cancellation,
and cancellation during credential replacement remain separate cases. This is
a proposed product outcome, not a choice of transaction ordering algorithm.

### Q-065 — Stalled renewal while permanent cancellation is pending

**Status:** answered; original deadline and timeout recovery accepted in PC-074.
**Prerequisites:** PC-037/PC-048/PC-072/PC-073.
**References:** D09/D10/D14; A03-A06/A15/A25/A28; constitution II/IV/VII.

Should the existing 15-minute renewal deadline bound the wait before pending
permanent cancellation moves to refund and revocation recovery?

**REC-065 — accepted in PC-074:** Preserve the original renewal deadline, measured from
verified payment, without starting a new 15-minute window when cancellation is
requested. If the renewal succeeds sooner, proceed immediately under PC-073.
If it reaches a confirmed terminal failure sooner, proceed to cancellation and
the required refund then. If it is still incomplete at the original 15-minute
deadline, end eligibility for renewal fulfillment, refund its full actual verified
payment once, and move the subscription toward permanent revocation rather than
waiting indefinitely for a successful renewal.

A deadline is a failed fulfillment outcome, not proof that remote effects are
known or all calls have stopped. Keep ambiguous remote actions, partial changes,
and revocation durably pending for reconciliation; do not report a clean remote
failure or completed cutoff without evidence. Prevent late renewal outcomes from
restoring the canceled subscription, reconciling them toward revoked access.
Refund processing does not depend on all remote cleanup completing. Under normal
app/database conditions, apply PC-048's 60-second usable-wallet-credit target from
the renewal's failure/cancellation decision. Show the unresolved revocation to
the owner and customer with a support path; this does not authorize abandoning it.

This keeps the sequential normal path while ensuring an unavailable panel cannot
hold the customer's verified renewal payment indefinitely. The trade-off is that
the timeout path still needs durable reconciliation rather than eliminating all
race conditions by waiting. The alternative is to keep the refund/cancellation
waiting for definitive remote resolution, potentially without a bounded duration.

No exact recovery algorithm or interruption of an in-flight network call is
selected. Numeric revocation completion/escalation targets and total-application-
outage catch-up remain separate; unknown effects must not be relabeled as known
success or failure merely to satisfy a timer.

### Q-066 — Completion and escalation targets for final cancellation

**Status:** answered; final-stage targets and timing boundaries accepted in PC-075.
**Prerequisites:** PC-019-PC-021/PC-048/PC-067/PC-072-PC-074.
**References:** D02/D09/D10/D11/D14; A14/A17/A25/A28;
E-001/E-002; constitution II/VI/VII.

Should the final cancellation stage have the same 60-second normal completion
target and 15-minute unresolved-operation escalation used for access changes?

**REC-066 — accepted in PC-075:** Begin final cancellation immediately when the confirmed
request is accepted if no paid renewal is in flight. If there is an in-flight
paid renewal, begin immediately when it succeeds, reaches confirmed terminal
failure, or reaches its original 15-minute fulfillment deadline under PC-073/
PC-074. During that wait, display cancellation pending rather than completed
revocation; URL invalidation and credential revocation belong to the final
cancellation stage rather than an earlier competing cancellation operation.
The confirmed pending request blocks further renewals under PC-073.

Under supported normal conditions, within 60 seconds of that stage beginning,
invalidate the subscription URL and confirm that every child rejects fresh
authentication. Immediately initiate both URL invalidation and revocation at
stage start; the target is not permission to delay starting. Existing sessions
continue to use native panel handling, without a forced-session termination
promise. If PC-073/PC-074 requires a renewal refund, make that full verified
amount visible and spendable in the wallet within the same 60 seconds under
normal application/database conditions, including when the renewal succeeded
after the cancellation request. Refund completion does not wait for panel
revocation or notification delivery.

If final cancellation work remains unresolved 15 minutes after that stage starts,
flag owner attention in web admin, attempt an owner Telegram notification, and
show the pending components to the customer with a support path. Failed/pending
credit and incomplete remote revocation must remain distinguishable. A missed
60-second target is visible when it occurs, not hidden until escalation. Preserve
recovery obligations and the canceled state; retries/restarts do not reset the
timers, reactivate service, or issue another refund. Escalation is not abandonment
or reversal of cancellation.

This preserves the user's sequential renewal policy and gives the final phase
a measurable target consistent with other access controls. The trade-off is
that the total wait can include the remaining renewal window plus final-stage
time, and outages can leave remote cutoff pending beyond the target under the
accepted best-effort policy. These targets require controlled evidence; no
instantaneous distributed revocation or successful integration is claimed.

Cancellation during other operations, owner response time, and total-application-
outage catch-up remain separate. No worker, transaction, or scheduling design
is selected by the product-visible stage boundaries.

### Q-067 — Remaining format scope after the Base64 clarification

**Status:** answered; Base64-only launch scope and explicit deferral accepted in PC-078.
**Prerequisites:** PC-001/PC-002/PC-007; REQUIREMENTS R05 and scope boundaries;
ACCEPTANCE open format choice; DECISIONS D05.
**References:** D05; A20-A22; S04; E-003; constitution I/V/VI.

The user has confirmed the desired Base64 URI-list experience in PC-076 and
requested informational entries in PC-077, but has not approved deferring native
structured exports. Should launch concentrate on that Base64 subscription and
explicitly defer native Clash YAML and sing-box JSON exports?

**REC-067 — revised recommendation accepted in PC-078:** Make the required complete
Base64 URI-list subscription, with the informational entries requested in PC-077,
the launch export. Explicitly defer native Clash YAML and sing-box JSON generation
for composites; a separate supported raw-text export is not required at launch.
Preserve required protocol/transport/security fields, all intended nodes,
distinct descriptive remarks and stable ordering. Do not silently drop a node
or required field to make an export parse. Existing legacy output capabilities
remain preserved within the affected scope.

The earlier recommendation included raw text as well as Base64 and is narrowed
here in response to the user's described Base64 experience. No unapproved raw
export or structured-format exclusion becomes accepted through that revision.
Clash YAML and sing-box JSON mean alternative generated profile formats; deferring
them does not itself exclude an app merely because its underlying core differs.
Actual compatibility depends on its import and protocol support and remains
subject to controlled checks, not inferred from a core name.

Keep v2rayNG, NekoBox, and Streisand as the required named client targets from
R05/PC-002. Exact supported versions and successful import, refresh and working
connections for all fixture nodes must be established by controlled checks under
S04/E-003. This recommendation is a release-scope choice, not evidence that a
particular application version supports every URI or that valid Base64 proves
compatibility. If the selected output cannot meet a confirmed client requirement,
report a compatibility blocker; do not silently drop the client or claim success.

This narrows the number of export implementations to verify at launch while
preserving the requested one-URL, complete-node experience. The trade-off is no supported
native structured export for users who require a Clash YAML or sing-box JSON
profile. Supporting all three export families initially is the alternative and
requires additional agreed client/version coverage and acceptance evidence.

REQUIREMENTS:74 and ACCEPTANCE:24 explicitly leave this release choice open;
none of these formats has previously been deferred by the user. No automatic
client detection rule, serializer design, API parameter, caching policy, or
conversion dependency is selected here. The six-node fixture remains an example,
not a cap on export size or child count.

### Q-068 — Information entries when usage updates are delayed

**Status:** answered; timestamped last-reliable display accepted in PC-079.
**Prerequisites:** PC-004/PC-015/PC-018/PC-077/PC-078.
**References:** D02/D05/D08/D11; A07-A17/A20-A22; F-023;
E-002/E-003; constitution II/VI/VII.

When usage updates are delayed or incomplete, should the subscription information
retain the last reliable remaining-allowance figure with its timestamp and a clear
warning, rather than hide that figure entirely?

**REC-068 — accepted in PC-079:** Display the last reliable composite allowance figure
as explicitly last-confirmed information, along with its usage-update timestamp
and an indication that updates are delayed/incomplete. Do not present it as the
current verified remaining balance. When there is no reliable whole-subscription
figure, display remaining allowance as unknown; do not invent zero use, zero
remaining, full quota, unlimited quota, or sum missing child readings as zero.
Keep the known subscription expiry visible independently of usage availability.

Include an as-of timestamp with usage information even when updates are healthy,
because imported configuration names remain snapshots until the app refreshes.
Expiry/allowance names are not a live account dashboard. During PC-018's grace
period, indicate delayed information without claiming confirmed suspension;
after an enforcement request, distinguish suspension pending from confirmed
cutoff under the existing policy. These display choices do not extend the
five-minute grace, change quota accounting, or promise live pushes to VPN apps.

For example, a conceptual label may convey "Last confirmed: 12 GiB remaining;
updated 12:34; usage updates delayed." Exact wording, localization, timestamp
layout, and number of rows are presentation details, not chosen strings here.
Usage timestamps must reflect the source information, not be advanced merely
because a customer refreshed the subscription or the app/server restarted.

This preserves useful context without concealing uncertainty. The trade-off is
that the old figure can overstate what remains now and needs a conspicuous
qualification. The alternative is to hide the numeric figure whenever required
usage is unreliable and show only an unknown/delayed state. Supported-client
rendering and refresh behavior still require controlled validation; no client
auto-refresh interval or sample-aggregation algorithm is selected.

### Q-069 — Adding V2Box and v2rayN to required launch-client coverage

**Status:** answered; five-app launch coverage accepted in PC-080, with daily-use
context recorded separately in BC-002.
**Prerequisites:** PC-002/PC-076-PC-079; R05.
**References:** D05; A20-A22/S04; E-003; constitution VI.

Should V2Box and v2rayN join v2rayNG, NekoBox, and Streisand as required launch
compatibility targets?

**REC-069 — accepted in PC-080:** Require demonstrated compatibility in those five named
apps for launch. Establish an explicit supported version/platform/core matrix
during planning and controlled validation; do not promise every historical or
future version, every fork, or every app implied by the user's "and...". Do not
add Throne as a mandatory release target solely because it appears in IMG-001.

For each supported target, verify the one Base64 URL's import and refresh, all
intended fixture nodes with preserved remarks and working protocol/security/
transport handshakes and traffic, and the requested informational-entry display
including the agreed stale-data presentation. Informational rows must not be
miscounted as extra working nodes. Investigate their selection/automatic-selection
behavior as part of E-003; that behavior is not proven by the screenshot or a
successful parser. Exact handling and supported limitations remain to be agreed
where evidence exposes a conflict.

This includes the two additional apps the user explicitly mentioned without
claiming universal compatibility. The trade-off is a larger release verification
matrix and potential blockers if a required app/version cannot support the
fixture or information presentation. The alternative is to keep the original
three mandatory and assess the others without a launch compatibility promise.
Unmet mandatory compatibility is a blocker requiring evidence or an explicit
scope revision, never permission to silently drop nodes, fields, or an app.

This is a product coverage choice; exact current versions must be researched
and recorded rather than guessed by the user. No controlled integrations or
client installations are authorized during this interview, and no passing
compatibility claim is made here.

### Q-070 — Subscription downloads during panel management outages

**Status:** answered; clarified recommendation accepted in PC-081.
**Prerequisites:** PC-001/PC-004/PC-018-PC-021/PC-042/PC-043/PC-078-PC-080.
**References:** D05/D11; A20-A22/S04; constitution II/V/VII.

**User clarification, 2026-09-28:** The user asked whether an unavailable panel
management API would also prevent usage collection and therefore stale/suspend
the whole subscription for everyone. This is a question about existing policy,
not acceptance of REC-070 or a request to change enforcement.

**Existing policy applies:** If the outage prevents trustworthy required usage
readings, PC-018's clock runs from each meter's last trustworthy reading. At five
minutes without replacement, request suspension of every credential in each
affected subscription, including healthy-panel children. All subscribers whose
subscriptions depend on that affected panel/reading can be affected; subscriptions
that do not depend on it are not globally suspended merely because this panel
is down. If all launch subscriptions include that panel, the effect can cover
all of them. This is not an immediate suspension after one failed API call.
PC-019 means an unreachable panel may also be impossible to disable, so its
credentials can remain usable while revocation/suspension is pending. Panel API
failure does not itself prove that its VPN listener or every existing session
stopped. PC-022 requires reconciled usage and continuing eligibility for recovery.

Q-070 concerns what a download returns, not permission to skip that suspension.
Should a still-valid, already-fulfilled subscription URL return the last verified
complete configuration with explicit delayed-usage/suspension status during this
outage, including while stale-usage suspension is pending or confirmed?

**REC-070 — clarified recommendation accepted in PC-081:** For an already fulfilled subscription with
a still-valid URL and no expiry/permanent revocation/replacement-delivery block,
continue supplying the last verified complete configuration for its current
credential generation when management APIs are unavailable, including while
its credentials are suspended or awaiting suspension for stale usage. Preserve
all intended real nodes, protocol/security fields and remarks. Do not silently
drop a node, substitute another endpoint, or serve a successful empty/partial
payload solely because a panel cannot currently be queried. Include the agreed
informational entries, showing dated/uncertain usage under PC-079 where applicable.

This availability does not certify that each VPN route is currently reachable,
make missing usage current, extend stale-data grace, or suspend enforcement.
PC-018/PC-019's existing suspension and best-effort remote-cutoff rules continue.
Present the known lifecycle state accurately: delayed usage during grace,
suspension requested/pending after the threshold, or confirmed suspension only
when established. Returning credentials in the list does not enable them. Conversely,
blocking a download would not revoke configurations customers already imported.
Never use this fallback to accept an invalidated URL, resurrect rotated/revoked
credentials, or bypass cancellation, replacement delivery gates, or other access
policy. If no trustworthy complete configuration for the permitted current
credentials exists, report temporary unavailability rather than inventing fields
or silently publishing a misleading partial list. Fetching a subscription must
not provision clients, reset usage, or initiate renewal under A20.

This keeps the node list and outage information available on refresh while the
backend applies the suspension policy. The trade-off is that listed nodes may
be disabled, unreachable, or have externally changed settings; listing is not a
live health or access guarantee. The alternative is to make subscription downloads
unavailable during this condition; that does not itself stop already-imported
credentials from working where remote cutoff remains unconfirmed.

This selects customer-visible outage behavior, not a cache/storage design, TTL,
API call sequence, or worker. The public endpoint being unavailable itself,
responses for expired or customer/owner-disabled subscriptions, and external panel-edit policy
remain separate cases. Controlled client behavior on failure and refresh still
requires verification.

### Q-071 — Downloads after expiry, exhaustion, or customer disable

**Status:** answered; accepted in PC-082.
**Prerequisites:** PC-028/PC-039/PC-042/PC-066/PC-072-PC-075/PC-078-PC-081.
**References:** D05/D09/D11; A15/A20-A22; constitution II/VII.

Should an expired, quota-exhausted, or voluntarily customer-disabled subscription
still let its valid URL download the complete current node list with a clear
explanation of its inactive state?

**REC-071 — accepted in PC-082:** Yes, for fulfilled paid and test composite subscriptions,
retain downloads through a still-valid URL in these three states. Include the
complete current node list and informational entries showing the actual reason
access is unavailable, known expiry, and appropriately qualified usage. Preserve
all credential enforcement and truthful pending-versus-confirmed cutoff status.
Fetching the URL must not enable access, renew service, reset usage, or clear the
customer's voluntary disable. Renewal keeps the same URL and credentials under
PC-039 and does not clear a voluntary disable under PC-066. If a separate permanent
cancellation, URL invalidation, or replacement-delivery gate applies, it takes
precedence; never serve superseded or revoked credentials through this policy.
Without a trustworthy complete current configuration, report temporary
unavailability under PC-081's rule.

This keeps the app's list and status information available across ordinary renewal
or eligible customer resume. The trade-off is that inactive nodes remain visible
and connection attempts will fail where cutoff has taken effect. Rejecting all
downloads in these states would remove access to updated informational rows, while
not itself revoking configurations already imported. Owner/security restrictions
and permanently invalid URL response details remain separate questions. No client
refresh behavior, HTTP response implementation, or storage design is selected.

### Q-072 — Owner responsibility for shared routing setup

**Status:** answered; owner-prepared shared infrastructure accepted in PC-083.
**Prerequisites:** PC-001-PC-003/PC-008-PC-010/PC-011; required A-US/A-DE/A-RU fixture.
**References:** R03/R04; REQUIREMENTS domain model and open routing boundary;
  D04; A02/A21; S02/S03; F-024; constitution I/V/VI.

For launch, should the store owner prepare the shared inbounds, outbounds, and
routing policy in the panels, with Shopvpn managing subscription credentials
that use that prepared setup, or must Shopvpn also create/edit shared routing
infrastructure?

**REC-072 — accepted in PC-083:** Make shared infrastructure preparation an owner
deployment responsibility for launch. The owner prepares the shared listeners,
country outbounds, and routing policy; Shopvpn manages independent subscriber
credentials and their intended route assignments within that prepared setup.
Creating, renewing, replacing, or cancelling a subscription must not rewrite
shared routing policy, clone country outbounds, add public listeners, or disturb
unrelated subscribers' routes. Defer a Shopvpn feature that creates/edits shared
routing infrastructure or generates administrator-applied shared configurations.

Correct per-credential egress remains required: the A-US/A-DE/A-RU credentials
must reach their respective intended outbounds from the same REALITY inbound.
Naming or flags alone are not evidence. Initial setup must be validated against
supported versions in controlled non-production checks; do not advertise an
unverified setup as meeting that requirement. This does not prescribe routing
syntax, identity naming, regex use, API methods, or how configuration readiness
is checked; those feasibility details belong to planning and controlled evidence.

The rationale is to keep launch subscription lifecycle operations from taking
ownership of shared networking configuration. The trade-off is deliberate owner
setup and maintenance before selling a topology, with less automation when new
countries/routes are introduced. If supported panel/core capabilities cannot
satisfy this boundary, surface that evidence for resolution rather than silently
adding shared configuration mutations or dropping the required egress behavior.

### Q-073 — Owner resolution of an unrecoverable usage gap

**Status:** answered; owner-approved usage-gap settlement accepted in PC-084.
**Prerequisites:** PC-004/PC-018/PC-019/PC-022/PC-023/PC-034/PC-035;
  intact entitlement and lifecycle history, with a gap in usage evidence.
**References:** D08; A09/A11/A13/A16; F-025; constitution II/IV/VII.

If an unexpected panel counter reset leaves some consumption permanently
unrecoverable, should the owner be able to resolve the affected subscription by
having the store absorb that unmeasured consumption, instead of leaving it
suspended indefinitely?

**REC-073 — accepted in PC-084:** Yes, through an explicit, audited owner decision in
the web admin after attempts to recover the missing usage. Until resolved, apply
the existing uncertainty policy: preserve confirmed usage, do not treat the reset
as zero consumption or fresh complete history, and use PC-018's existing grace
and suspension rules without restarting the grace clock. Mere API recovery does
not satisfy PC-022 while the gap remains unresolved.

For this resolution, retain all confirmed consumption and subtract any additional
usage that can be reliably recovered. The owner may accept the remaining unknown
gap at the store's expense. Preserve the original purchased allowance and expiry;
do not grant a new full allowance, erase known consumption, estimate a customer
charge, or create customer debt. Record the affected subscription, gap/evidence,
reason, owner, accepted financial risk, and outcome. Keep the historical usage
gap explicitly unknown; accepting its cost does not make its bytes measured zero.

Resume only after current metering is trustworthy for all required children,
this accounting uncertainty is explicitly settled, allowance/time remain, and
no customer disable, cancellation, revocation, or other restriction prohibits
access. Keep pending remote enable distinct from confirmed recovery. This is an
owner-approved commercial resolution, not automatic recovery from a mere successful
poll; ordinary fully reconciled outage recovery under PC-022 remains automatic.
Usage displays must not relabel incomplete historical consumption as exact;
the allowance available after the owner settlement may be shown as such.

Example: a 50-GiB entitlement has 20 GiB of retained confirmed consumption. If no
additional bytes can be recovered, the owner can authorize continued service
with 30 GiB remaining and the original expiry, explicitly absorbing the unknown
gap. Any additional reliably recovered consumption must reduce that remainder.
Known exhaustion or expiry cannot be reversed through this resolution.

The rationale is to restore service without inventing usage or penalizing the
customer for lost panel evidence. The trade-off is manual owner intervention and
potential unmeasured usage borne by the store. The alternative is to keep access
suspended until exact reconciliation is possible, which may never happen.
This does not authorize a general restore from missing purchase, payment, token,
or revocation history, waive constitutional evidence requirements, or choose
counter-reset detection, storage, or reconciliation algorithms.

### Q-074 — Launch scope for changing an issued subscription's nodes

**Status:** answered; blanket deferral rejected. Equivalent server replacement
is required by PC-086; initial deployment clarified in PC-085. Broader topology
editing remains unapproved.
**Prerequisites:** PC-001/PC-005/PC-008/PC-025/PC-039/PC-042/PC-083.
**References:** D04/D09/D13/D14; A24; REQUIREMENTS correctness item 6.

Does launch need an owner operation to add, remove, or replace nodes in already
issued paid/test composite subscriptions, or can that migration feature wait?

**REC-074 — rejected as a blanket launch deferral:** Defer topology migration for existing composite
subscriptions at launch. Owners may configure new topologies for future purchases
or test claims, but each issued subscription retains its saved node set, protocols,
and intended routes. Catalog edits, ordinary renewal, and credential replacement
must not silently migrate it. Existing matching-topology renewal choices remain
subject to PC-025; this does not reopen the accepted choice to switch eligible
allowance/price presets during renewal.

Keep the infrastructure needed to honor issued subscriptions available for their
service obligations; a catalog edit or local panel-record deletion is not a way
to retire those obligations or discard cleanup responsibility. Temporary outages
continue through the agreed suspension/recovery policies. This recommendation
does not forbid repairing the same intended service, but replacing a sold node
with a different panel, protocol, or intended route is a migration, not repair.

The rationale is to keep launch focused on issuing and managing a stable promised
node set. The trade-off is that a permanent server loss cannot be solved by moving
existing subscriptions to another topology through a launch management feature;
it requires operational repair or a separately agreed customer remedy. An owner
migration capability would address that need but requires explicit continuity,
credential-revocation, accounting, and partial-failure policies. No migration
algorithm or task breakdown is selected here.

### Q-075 — Replacement when the old server cannot confirm revocation

**Status:** answered; explicit emergency cutover accepted in PC-087.
**Prerequisites:** PC-004/PC-018-PC-023/PC-043/PC-084-PC-086.
**References:** D02/D08/D14; A16/A17/A24; constitution II/IV/VII.

If the old server's management API is also unreachable, should replacement
activation wait until its old credentials can be disabled, or may the owner
explicitly authorize switching while old-server cleanup remains pending?

**REC-075 — accepted in PC-087:** Permit explicit owner-authorized emergency cutover to
an equivalent, fully ready replacement after reviewing affected subscriptions,
last-confirmed usage, and old-server uncertainty. Preserve known usage, allowance,
expiry, and independent access restrictions. Current metering on the replacement
must be trustworthy. No automatic failover or automatic waiver is implied.

The owner accepts the store's exposure to unmeasured old-server consumption.
Preserve its unknown history and any confirmed consumption; do not fabricate a
final zero reading. Retain old identities, available metering evidence, and pending
revocation/cleanup; continue reconciliation when possible and do not treat an
IP blocked from some customers as proof of global revocation. Confirmed usage
remains attributable once; existing store-absorbed-overrun policy still applies.

For this explicitly approved retirement, missing old-server readings alone must
not immediately re-suspend the replacement under PC-018. The retired server remains
an unresolved exposure/cleanup obligation rather than a required current-serving
meter. This is a narrow proposed qualification of stale-meter recovery for server
replacement; current required replacement meters still follow the five-minute rule.
It must not clear customer disable, known expiry/exhaustion, cancellation, or
leaked-access replacement's separately accepted revocation-before-delivery gate.

The rationale is to restore service when waiting for a failed server could prevent
recovery indefinitely. The trade-off is that old credentials may still work from
other networks, creating possible simultaneous access and unknown additional
consumption, without a guaranteed finite bound. The alternative is to require
confirmed old-credential cutoff before activating the replacement, extending the
outage if the old panel cannot be reached. Where the old API remains reachable,
collect usage and seek confirmed revocation; entry-IP filtering alone does not
imply an API or metering failure from the subscription manager's location.

### Q-076 — Credential identity during equivalent server replacement

**Status:** answered; fresh moved-node credentials accepted in PC-088.
**Prerequisites:** PC-039-PC-044/PC-065/PC-086/PC-087.
**References:** D08/D11/D14; A14/A17/A21/A24; constitution II/IV.

Should each moved node receive a fresh credential on the replacement server,
while the customer's subscription URL stays the same?

**REC-076 — accepted in PC-088:** Yes. Generate fresh authentication identities for every
moved child: new UUIDs for VLESS/VMess and new protocol passwords for Trojan.
Retain the subscription URL, intended node choices/remarks, ownership, shared
allowance, accrued usage, original expiry, and applicable restrictions. Credentials
of nodes not involved in the server replacement remain unchanged. The updated
payload contains the replacement connection settings and credentials only after
the applicable readiness/cutover conditions are met; do not silently publish an
incomplete replacement as a completed move.

Customers refresh the existing URL to obtain the new credentials and destination
settings. Old imported entries must not authenticate to the replacement using
their old credentials. PC-087 still permits unresolved old-server access under
explicit owner approval; issuing new credentials does not itself revoke old ones.
Old identities/history and cleanup obligations remain retained.

This owner operation is distinct from customer leaked-access replacement: it
does not consume, restart, or clear the customer's existing 24-hour replacement
cooldown, and it does not repair a leaked subscription URL because that URL remains
unchanged. Ordinary renewal's identity-preservation rule is also unchanged.

The rationale is to avoid making credentials from the retired server valid on
its replacement and to distinguish the old/new access identities. The trade-off
is that manually copied configurations and apps that have not refreshed will not
gain access to the replacement. Reusing credentials could preserve identity but
would also allow the same secrets on both servers; changed endpoint/security
settings can still require refresh either way. Exact API operations, identity
generation, and accounting representation remain planning details.

### Q-077 — Bulk server replacement with independent subscription outcomes

**Status:** answered; bulk replacement and independent outcomes accepted in PC-089.
**Prerequisites:** PC-009/PC-010/PC-054/PC-086-PC-088.
**References:** D10/D14; A03-A06/A24; constitution II/IV/VII.

Should the owner be able to replace a server for selected or all affected
subscriptions in one web-admin action, with each subscription completing
independently rather than waiting for every subscription in the batch?

**REC-077 — accepted in PC-089:** Yes. Allow selection of one, several, or all affected
subscriptions, with a preview of the subscriptions and old-to-replacement server
mapping before owner authorization. Preserve per-subscription ownership,
entitlement, restrictions, and any required explicit emergency-cutover approval.
Selecting an affected customer must make the actual subscriptions included clear;
do not silently treat a customer's multiple subscriptions as one entitlement.

Each subscription switches only when its complete intended replacement set is
ready and the applicable cutover conditions are satisfied. For the A-only launch
case, all five moved nodes must be ready for that subscription. A failed or pending
subscription must not block or roll back other completed subscriptions. Show
per-subscription outcomes and a truthful partial-batch summary; retries recover
unfinished work without creating another migration or new credentials for already
completed subscriptions merely because they were in the same batch.

Example: out of 100 selected subscriptions, 99 may complete and serve their full
replacement node lists while one remains pending with a visible reason and
recovery path. Do not report the whole batch as completed or publish a partial
replacement for the failed subscription. This is an example, not a batch-size cap.

The rationale is to restore as many affected subscriptions as possible during an
IP-blocking incident without requiring one operation per customer. The trade-off
is a period with mixed migration outcomes and owner follow-up for failures,
instead of one all-or-nothing batch result. Timing targets, eligibility details
for historical records, and customer refresh notifications remain separate;
no concurrency, queue, transaction, or retry algorithm is selected.

### Q-078 — Normal replacement target and overdue recovery

**Status:** answered; replacement benchmark and overdue recovery accepted in PC-090.
**Prerequisites:** PC-020/PC-046/PC-056/PC-085-PC-089.
**References:** D02/D13/D14; A16/A24; S09; E-002/E-004; constitution VI/VII.

Is a 15-minute normal-operation target acceptable for replacing a batch of 150
eligible subscriptions with five moved nodes each, once the replacement server
is prepared and the owner authorizes the operation?

**REC-078 — accepted in PC-090:** Require completion within 15 elapsed minutes of owner
authorization for the launch benchmark of up to 150 subscriptions with five moved
nodes each (750 replacement credentials). The replacement server, equivalent
inbound/routes, and required access must already be prepared and available; this
does not measure VPS purchasing/setup time. Include waiting within the operation
in the target, not only time spent actively processing each subscription. Applicable
PC-087 emergency authorization may permit an unavailable old server; its pending
cleanup remains separately visible and is not falsely included as confirmed
revocation in the replacement-completion claim.

Completion means every still-eligible selected subscription has its full ready
replacement set, trustworthy current metering, and updated configurations available
through its unchanged subscription URL under the applicable restriction policy.
It does not mean customers have already refreshed their apps or existing sessions
have moved. No expiry, exhaustion, cancellation, or customer restriction may be
overridden to meet the target. Other subscriptions' required accounting and
enforcement must continue during the operation.

At 15 minutes, any unfinished work is visibly overdue and needs owner attention
in web admin, with an attempted Telegram owner notification. Continue bounded,
repeat-safe recovery and retain unresolved obligations; do not automatically roll
back completed subscriptions, erase pending work, or reset purchased expiry/quota.
The original operation timer does not restart on retries or process restart.
This is a completion target and escalation threshold, not permission to discard
work at the deadline or a new purchase's automatic-refund deadline.

The 150-subscription benchmark is grounded in the launch campaign, not a cap on
paid subscribers, total active subscriptions, or bulk selection. Larger batches
remain supported with visible progress, but no universal 15-minute guarantee is
selected for arbitrary batch sizes. Their measured operating envelope belongs
in planning/validation. This benchmark does not replace the existing multi-panel
acceptance fixture or establish an active-connection capacity limit.

The rationale is a measurable launch restoration expectation tied to an actual
planned cohort. The trade-off is accepting up to 15 minutes after preparation
under supported normal conditions rather than promising instant recovery. This
is a proposed product target, not evidence that the current code or deployment
can meet it. Controlled checks must establish supported infrastructure, load,
and compatibility; no benchmark execution or architecture is selected here.

### Q-079 — Customer refresh notification after server replacement

**Status:** answered; customer refresh notifications accepted in PC-091.
**Prerequisites:** PC-007/PC-049/PC-086-PC-090.
**References:** D10/D11/D14; A20/A24/A27; constitution III/VII.

Should each customer receive a Telegram notification when their subscription's
replacement is ready, telling them to refresh its existing subscription URL?

**REC-079 — accepted in PC-091:** Yes. After each subscription's replacement is complete
and its updated configuration is retrievable, attempt a notification to its owning
customer through the main-store Telegram bot. Identify the affected subscription,
tell the customer to refresh it in their VPN app, and explain that the subscription
URL is unchanged and replacement has not reset their remaining allowance or expiry.
The message must respect actual access restrictions; completed migration must not
be advertised as usable access if the customer has disabled the subscription or
it is otherwise ineligible. Do not wait for all other subscriptions in the batch
before notifying a completed one.

A blocked bot, Telegram outage, or notification failure does not undo a completed
replacement or block its URL from serving the ready configurations. Keep the
replacement status and refresh guidance available when the customer opens their
subscription in the bot. Track failed or uncertain notification delivery separately
from migration outcome, use bounded delivery recovery, and make unresolved
notification failure visible to the owner without repeating the server migration.
Do not claim the customer read the message or refreshed their app solely because
the notification was sent. Avoid duplicate notices for the same completion where
delivery is known, without promising exactly-once external message delivery.

The rationale is that customers with cached configurations need to know a refresh
is required; otherwise backend recovery may not restore their practical access.
The trade-off is an additional service notification, and customers who cannot
receive it may remain on old settings until they independently refresh or check
the bot. No silent update of client apps or movement of established sessions is
promised. Wording/localization and notification transport/retry implementation
remain planning details.

### Q-080 — Payment methods for composite purchases and renewals

**Status:** answered; existing configured methods and plan restrictions accepted in PC-092.
**Prerequisites:** PC-006/PC-007/PC-013/PC-024/PC-050-PC-052/PC-061.
**References:** D07/D09/D10; A25/A28; F-014-F-016/F-027;
  constitution I/II/III/VII.

Should composite purchases, renewals, and trial-to-paid conversions use the
store's existing configured Telegram payment options, or require customers to
fund their store wallet first?

**REC-080 — accepted in PC-092:** Use the existing configured Telegram payment options
for initial composite purchase, full-plan renewal, and trial-to-paid conversion.
When the selected plan allows wallet payment, apply available wallet credit first
up to the discounted price; pay any remainder through an existing external method
that is enabled and allowed for that selected plan and amount. A customer with no
wallet balance may pay the full amount externally where allowed. Do not force a
separate wallet top-up before every purchase, and do not introduce a new payment
gateway as part of this feature.

Apply the selected composite plan's payment restrictions to renewal/conversion
as well as initial purchase, along with enabled-method and applicable minimum-amount
checks. Do not copy the inspected legacy renewal bypass of product restrictions.
Separate wallet-top-up restrictions remain applicable to top-ups; they do not
implicitly authorize a method for direct purchase or renewal. If no permitted
method can cover the payable remainder, explain that checkout cannot proceed
without retaining a wallet debit for an unpayable order.

Preserve the agreed tier/coupon calculation and full actual-paid wallet-refund
policy. Payment-method availability does not approve unsafe verification,
client-reported success, duplicate settlement, or unauthorized manual approval;
affected paths must meet the constitution. A configured method that cannot satisfy
required verification is a concrete integration issue to resolve, not permission
to grant service on unverified evidence. No enabled runtime gateway configuration
or secrets have been inspected, and this is not a claim that every existing
integration already meets the feature's requirements.

The rationale is to keep the familiar payment choices and let customers spend
refund wallet credit without adding a mandatory top-up step. The trade-off is
more payment paths to validate, including split wallet/external payments. A
wallet-only checkout would reduce direct-order payment integration scope but
require customers with insufficient credit to top up before ordering. Gateway
verification details, conversion/rounding rules, and late-payment/cancellation
policy remain separate evidence or product questions.

### Q-081 — Interfaces for owner manual payment approval

**Status:** answered; owner-only decisions through both interfaces accepted in PC-093.
**Prerequisites:** PC-009/PC-010/PC-012/PC-013/PC-037/PC-092.
**References:** D07/D10; A03/A19/A28; F-027/F-028; constitution II/III/VII.

For manually reviewed composite purchase/renewal payments, should the store owner
be able to approve or reject the payment request from both Telegram and web admin,
or only from web admin?

**REC-081 — accepted in PC-093:** Allow the main-store owner to review and approve/reject
manual composite payment requests through both the existing Telegram receipt
workflow and web admin. Restrict these composite actions to the owner; staff or
customers cannot authorize them. Check the payment evidence, beneficiary, order,
amount, method, and tenant before recording verified payment, and retain the
authorized actor and decision audit. A receipt upload or customer assertion alone
is not verified settlement. Repeated or competing decisions from either interface
must not duplicate financial or provisioning effects.

This settles the explicitly open payment-approval interface boundary in PC-010.
Composite plan configuration and other owner subscription management remain
web-admin-only. Existing general wallet-top-up and legacy receipt workflows are
preserved within PC-003's scope; this does not restrict unrelated top-up approvals
or approve composite sales through reseller/admin issuance flows.

Confirmed payment starts the accepted fulfillment/renewal deadline, regardless
of which interface records the confirmation. Approval must not report completed
provisioning before the full agreed readiness/delivery gate is satisfied.

The rationale is to let the owner act where manual payment receipts arrive while
also retaining web-admin visibility. The trade-off is two financial control
surfaces to validate for authorization, audit, and repeat-safe settlement. Web-only
approval would reduce that scope but require opening the admin panel for every
composite receipt. Exact UI, payment verification, and shared operation mechanics
remain planning details.

### Q-082 — Payment verified after a checkout cancellation

**Status:** answered; checkout cancellation and later wallet credit accepted in PC-094.
**Prerequisites:** PC-013/PC-037/PC-048/PC-073-PC-075/PC-092/PC-093.
**References:** D07/D10; A03-A06/A25/A28; F-029; constitution II/III/VII.

If a customer cancels a composite checkout while it is awaiting full payment
verification, but its external payment is subsequently verified, should that
money become store-wallet credit rather than automatically fulfilling the
cancelled purchase or renewal?

**REC-082 — accepted in PC-094:** Yes. Permit the customer to cancel their own initial
purchase, renewal, or trial-conversion checkout while full payment remains
unverified. End that checkout without changing an existing subscription. Restore
any wallet amount already deducted for it once; under normal app/database
conditions make that restoration usable within 60 seconds of accepted cancellation.

If the corresponding external payment is later validly verified, credit 100% of
the verified external amount to the same customer's store wallet once, including
after a delayed gateway callback or owner receipt verification. Make it usable
within 60 seconds of that verification under normal app/database conditions.
Keep the checkout cancelled: do not create a new subscription, renew/convert an
existing one, or resurrect provisioning because payment arrived late. Keep the
cancelled order and payment/credit evidence linked for reconciliation and show
the customer the resulting credit/outcome. A duplicate callback or approval must
not credit twice; prior wallet restoration must not be included again as newly
received external money.

Example: a checkout priced at 100 has 30 deducted from the wallet and awaits 70
externally. Cancellation returns 30. Later verification of the external 70 credits
70 once, while the order remains cancelled. The customer may place a fresh order
if desired; that new order uses then-current prices, offers, and eligibility.

This applies when cancellation is accepted before full payment verification. It
does not replace the accepted sequential-cancellation policy for an already
verified in-flight renewal under PC-073-PC-075. Verified initial purchases already
in provisioning remain a separate case. Unmatched, invalid, or amount-mismatched
payment evidence must remain visible for authorized investigation rather than
invented as a valid payment or silently discarded; detailed provider verification
and conversion rules remain planning/evidence work.

The rationale is to honor the customer's cancellation while retaining genuine
received money as usable credit. The trade-off is that a customer who intended
to complete the original order must check out again, and repayment is store
credit under PC-013 rather than an automatic original-method cash refund. No
gateway callback, state-machine, or storage implementation is selected.

### Q-083 — Cancellation of a verified paid initial purchase before fulfillment

**Status:** answered; paid initial-provisioning cancellation accepted in PC-095.
**Prerequisites:** PC-011-PC-014/PC-048/PC-049/PC-068/PC-072-PC-075/PC-094.
**References:** D10/D14; A03-A06/A17/A28; F-029; constitution II/IV/VII.

Should a customer be able to cancel an initial composite purchase after payment
is verified but before the complete subscription and URL are available?

**REC-083 — accepted in PC-095:** Yes, through explicit customer confirmation in Telegram.
Accept cancellation only while initial fulfillment is incomplete. Following the
accepted sequential approach for renewal, let the already-running provisioning
operation reach a clean outcome or its original 15-minute deadline from verified
payment, whichever comes first; a cancellation request does not restart that
deadline. Show cancellation pending during this bounded wait. Once cancellation
is accepted, do not make a new subscription URL/configuration available to the
customer, even if remote creation subsequently succeeds.

Upon that outcome/deadline, cancel the order, refund 100% of the actual verified
payment to the store wallet once without usage proration, and revoke/clean up
all created credentials. Under normal application/database conditions, the
refund is visible and spendable within 60 seconds of this final-stage decision,
independently of remote cleanup or notifications. Under supported normal panel
conditions, invalidate any issued token and confirm all created credentials reject
fresh authentication within 60 seconds of final-stage start. Native existing-session
handling remains unchanged. Do not falsely confirm revocation when a panel is
unreachable; retain identities, uncertainty, and pending cleanup.

If final-stage work remains unresolved at 15 minutes from its start, escalate to
owner attention in web admin with an attempted owner Telegram notice and a
customer-visible pending/support outcome. Continue bounded recovery rather than
discarding obligations. Retries/restarts do not reset timers, duplicate refunds,
or allow late remote success to deliver/reactivate the cancelled purchase.

Once complete fulfillment and URL availability occurred before cancellation
acceptance, use PC-072's permanent cancellation of a fulfilled subscription with
no automatic unused-service refund, subject to already accepted specific refund
exceptions. Reading a notification or first using VPN traffic is not the
fulfillment boundary under PC-014/PC-049. This question does not reopen cancellation
of verified in-flight renewals or of checkouts awaiting full payment verification.

The rationale is to let customers withdraw from an undelivered initial purchase
while keeping the same bounded sequential cancellation approach. The trade-off
is waiting for provisioning resolution or the remaining original fulfillment
window before the final refund phase, rather than immediate credit at request time.
No network-call interruption, lifecycle algorithm, or task breakdown is selected.

### Q-084 — Restore coupon-use allowance after failed or pending-order cancellation

**Status:** answered; coupon-use restoration accepted in PC-096.
**Prerequisites:** PC-013/PC-037/PC-051/PC-052/PC-073-PC-075/PC-094/PC-095.
**References:** D07/D09/D10; A03-A06/A25/A28; F-015/F-029;
  constitution II/VII.

Should a coupon's limited-use allowance be restored when a composite order fails
or is cancelled before completion and its payment is fully refunded?

**REC-084 — accepted in PC-096:** Yes. A pending checkout holds one coupon use; permanently
consume it only for a successfully fulfilled order whose purchase/renewal is
retained. Release the held/consumed use once if initial fulfillment or renewal
fails, checkout cancellation is accepted before full payment verification, or
paid initial cancellation is accepted before fulfillment and its required refund
is settled. Include PC-073's special cancellation requested while paid renewal
is in flight: restore that renewal's coupon use when its full cancellation refund
is settled, even if the remote renewal completed before final revocation.

Restore both applicable overall and per-customer use allowances for that order,
without double release on retries, callbacks, or repeated cancellation/refund.
Do not count multiple child nodes as multiple coupon uses. A late verified payment
credited under PC-094 cannot re-consume the cancelled order's coupon. If no
payment was due/received, release the use on the corresponding terminal failed
or accepted cancellation outcome; zero-price fulfillment eligibility itself is
not selected by this question.

Release does not extend coupon expiry, re-enable a disabled code, override
product/category/amount restrictions, or guarantee availability to this customer
on a new checkout; current eligibility and capacity are checked again. An already
fulfilled subscription cancelled later under the no-refund policy does not
restore its purchase coupon. A discretionary support compensation credit also
does not automatically restore coupon uses. General test eligibility and the
150-user campaign recipient history/cap remain independent and unchanged.

The rationale is to avoid spending a limited-use benefit on an order that fails
or is withdrawn under the accepted full-refund policies. The trade-off is that
pending orders temporarily occupy coupon capacity and released capacity can be
claimed by another eligible checkout. Keep financial/refund and coupon outcomes
recoverable and visible; reservation storage, release algorithms, pending-quote
duration, and detailed eligibility verification remain planning or later product
questions.

### Q-085 — Zero-price checkout after valid discounts

**Status:** answered; zero-price normal catalog fulfillment accepted in PC-097.
**Prerequisites:** PC-008/PC-011-PC-016/PC-051/PC-052/PC-055-PC-061/
  PC-092/PC-095/PC-096.
**References:** D07/D09/D10; A03-A06/A25/A28; F-030; constitution II/III/VII.

If valid configured discounts reduce a composite catalog purchase or renewal's
total price to zero, should the customer receive the normal selected plan without
a payment step, independently of free-test eligibility?

**REC-085 — accepted in PC-097:** Yes. After the customer confirms the checkout and its
current price/discount/ownership eligibility is verified, fulfill the selected
normal catalog plan without deducting wallet credit, requesting an external
payment, or fabricating a paid transaction. Record the zero amount and actual
discount/authorization evidence. This applies to eligible initial purchase,
full-plan renewal, and trial-to-paid conversion into a normal catalog preset.

Discounts alter price only: preserve full selected allowance/duration, complete
node readiness, usage/carryover, original restrictions, ordinary identity rules,
and all other accepted subscription lifecycle behavior. Zero-price catalog
fulfillment does not use or reset `test_used`, claim a campaign place, reopen its
cap, or erase prior trial/campaign history. An existing trial can convert through
an eligible zero-price normal renewal without receiving new free-test eligibility.
This does not approve zero-base-price catalog offers, arbitrary owner free grants,
or another complimentary issuance flow; it covers valid discounts on otherwise
supported catalog checkout.

Use the same 15-minute complete-fulfillment deadline, starting at accepted final
customer checkout confirmation with validated zero price instead of verified
payment. Validity still begins at complete readiness and URL availability. A
failure or eligible cancellation retains cleanup/recovery responsibility and
releases coupon use under PC-096, but cannot create a positive monetary refund
when the actual paid amount was zero. Coupon usage limits and repeat-safe issuance
remain required; no duplicate grants on repeated confirmation.

The rationale is to honor legitimate owner-configured promotions without treating
a normal catalog order as a test or asking the customer to pay zero. The trade-off
is that valid promotions can grant full normal-plan benefits free of charge, so
configured coupon restrictions and limits matter. The alternative is an explicit
launch rule preventing discounts from producing zero-price composite checkout,
which would need a defined minimum or rejection policy rather than silently
clamping the agreed PC-051 pricing behavior. No fulfillment/state/storage algorithm
is selected.

### Q-086 — Honor an accepted checkout quote through later catalog/coupon edits

**Status:** answered; quote preservation and rejection treatment accepted in PC-098.
**Prerequisites:** PC-005/PC-008/PC-025/PC-051/PC-052/PC-092-PC-097.
**References:** D07/D09/D10; A03/A24/A25/A28; F-015/F-031;
  constitution I/II/VII.

Should a finally confirmed checkout keep its agreed price, discount, and selected
plan terms despite later catalog/coupon edits, until the order completes or is
cancelled/rejected, without adding a general unpaid-quote expiry timer at launch?

**REC-086 — accepted in PC-098:** Yes. At final customer confirmation, validate current
price, tier/coupon eligibility, remaining coupon capacity, ownership, and selected
offer before accepting the checkout. Hold one permitted coupon use and honor that
accepted order's quoted price/reductions and selected allowance, duration, and
intended node choices. Subsequent price, tier, coupon, or catalog edits affect
new checkouts rather than silently repricing/changing this accepted one. A coupon
that later expires or is disabled remains valid for its already accepted held use;
that does not permit new uses after expiry/disable.

Preserve the quote until completion, accepted customer cancellation, or authorized
owner rejection. Do not add a new store-wide unpaid-order or manual-receipt expiry
timer for launch. Selected payment methods retain their own invoice validity and
verification rules. Expiry of one external invoice does not alone declare its
parent checkout cancelled, restore its held wallet/coupon, or authorize payment;
the customer can choose another currently permitted payment attempt for the same
still-pending quote. Repeated attempts must not produce duplicate settlement.
Actual cancelled-order late money follows PC-094.

This quote does not freeze live usage, unused-data eligibility, remaining validity,
or renewal carryover while payment is pending. Those continue under the accepted
renewal policies, including PC-038's verified-payment boundary. Payment security,
current method availability, and applicable access restrictions still govern;
locking a price does not waive verification or authorize an ineligible action.
PC-086-PC-091's explicit equivalent-server replacement remains separate from
silent catalog edits and must preserve intended service.

If the owner rejects the pending checkout before full payment verification, use
the same held-wallet/coupon release and later validly verified external-money
credit treatment as PC-094/PC-096, retaining the rejected outcome. This explicitly
proposes that qualification for owner rejection; it is not inferred as previously
approved by PC-094's customer-cancellation answer.

The rationale is to honor the offer the customer accepted while paying or waiting
for manual review. The trade-off is old prices/promotions and coupon capacity
remaining tied to pending orders until completion or cancellation/rejection.
The owner can review and reject pending requests through the agreed interfaces;
they cannot silently replace a verified payment with an increased price. A new
quote after terminal cancellation/rejection uses then-current offers/eligibility.
No quote storage, snapshot schema, or invoice-processing algorithm is selected.

### Q-087 — Credit a separately verified extra payment without another entitlement

**Status:** answered; distinct extra-payment credit accepted in PC-099.
**Prerequisites:** PC-013/PC-037/PC-048/PC-051/PC-052/PC-073/PC-092-PC-098.
**References:** D07/D09/D10; A03-A06/A25/A28; F-029/F-031;
  constitution II/III/VII.

If two distinct real payments are verified for the same checkout, should the
extra payment become store-wallet credit rather than another subscription or
another renewal?

**REC-087 — accepted in PC-099:** Yes. Settle the quoted purchase/renewal once. If a
second distinct payment is independently verified as real money received for
the same beneficiary and checkout, with its own transaction reference and the
expected external amount and currency/unit conversion, credit the entire extra
received amount to that customer's store wallet once. Make it visible and
spendable within 60 seconds of verification/recognition under normal application
and database availability, independently of panel cleanup or notification.
This covers distinct valid payment attempts, not acceptance of mismatched or
unverifiable amounts; those require investigation and cannot authorize settlement.

For example, a 100-unit order funded with 30 wallet units and a verified external
payment of 70 is funded once. If another distinct valid 70-unit payment is also
received for that order, credit the extra 70 to the wallet. Do not issue a second
subscription, add a second renewal, deduct the wallet again, or consume another
coupon use. Do not restart fulfillment's 15-minute deadline or move its original
verified-payment boundary for carryover eligibility.

A repeated callback or approval for the same payment reference is not another
payment and creates no extra credit. A transaction already settled/credited must
not be claimed again through another order. Keep the extra-payment credit separate
from the original checkout's required refunds: if fulfillment subsequently fails,
refund its original actual paid amount once and retain the extra payment's own
credit, without refunding that extra money again. Cancelled/rejected-order late
money follows PC-094/PC-098; it does not reopen the order.

The rationale is to reconcile every verified receipt while preserving the
customer's one confirmed purchase. The trade-off is receiving store credit rather
than an automatic return through the original payment method, consistent with
the accepted failed-order refund policy. No payment-ledger schema, gateway
reconciliation algorithm, or passing duplicate-payment result is selected.

### Q-088 — Boundary for additional complimentary issuance

**Status:** answered; additional ad hoc complimentary grants deferred in PC-100.
**Prerequisites:** PC-006-PC-010/PC-053-PC-064/PC-069-PC-071/PC-097.
**References:** D07/D10/D14; A03/A19/A27-A29; F-008/F-017/F-018;
  constitution I-III/VII.

For launch, should complimentary composite issuance stay within the agreed test
plans/campaign and valid discount checkout, with additional ad hoc owner gifts
or manual off-catalog free grants deferred?

**REC-088 — accepted in PC-100:** Yes. Preserve composite support in `btn_test`, the
15-GiB/15-day/150-user campaign, future owner-defined composite test plans, their
shared existing test eligibility, and the independently agreed valid-discount
normal checkout (including eligible zero-price purchase/renewal). Do not add an
owner action that directly creates complimentary off-catalog composites for
one or many customers outside those flows at launch. This narrows only the
remaining ad hoc grant branch; it does not reinstate Q-049's rejected blanket
deferral of complimentary composite issuance.

Owner-only plan configuration does not by itself authorize direct grants.
Manual support wallet credit and bulk wallet credit remain available under their
accepted policies; they are not direct subscription issuance or a bypass of test
quota/campaign history. Preserve affected legacy gift/manual-issuance behavior.
Purchase-based referral composite rewards are already deferred by PC-053 and
are not being re-asked. Paid purchases for somebody else and ownership transfer
remain separate questions, rather than being decided by this free-grant boundary.

The rationale is to provide the explicitly requested launch promotion and
configurable tests while keeping entitlement, eligibility, and delivery governed
by already defined flows. The trade-off is that the owner cannot directly push
an extra free composite subscription, including to a selected group, bypassing
customer claim/checkout or the agreed test rules. The alternative is to include
such grants explicitly and resolve their allowance, duration, recipient consent,
delivery, and quota/campaign treatment before specification. No grant workflow,
schema, implementation task, or test result is selected.

### Q-089 — Keep launch subscriptions with the purchasing or claiming account

**Status:** answered; stable purchasing/claiming-account ownership accepted in PC-101.
**Prerequisites:** PC-004-PC-010/PC-050/PC-054-PC-061/PC-069-PC-075/
  PC-094-PC-100.
**References:** D07/D10/D14; A19/A23/A28/A29; F-008/F-017/F-032;
  constitution I-III/IV.

For launch, should each composite remain assigned to the Telegram account that
purchases or claims it, with checkout for another recipient and customer/admin
ownership reassignment deferred?

**REC-089 — accepted in PC-101:** Yes. Assign a purchased composite to the authenticated
main-store Telegram buyer and a composite test/campaign claim to its authenticated
claimant. Keep that customer account as the subscription's management owner at
launch, including after renewal, trial conversion, credential replacement, or
equivalent-server replacement. Do not add a different recipient to checkout or
allow a customer or store owner to reassign a composite to another customer
account through the legacy service-transfer action.

The assigned customer controls their approved self-service actions, and refunds
or extra-payment credits remain with the checkout's verified beneficiary under
the accepted policies. Multiple separately purchased subscriptions for the same
customer remain allowed. Possession of a subscription URL does not grant access
to another customer's bot account or management controls. This decision would
not create a device/concurrent-session limit or change the agreed native panel
handling of existing sessions.

Preserve affected legacy ownership-transfer behavior. Subscription ownership
reassignment is distinct from a store/tenant ownership change: deferring the
customer transfer feature does not permit such administrative changes or resets
to erase financial, campaign, usage, revocation, or remote cleanup responsibility
under PC-005 and constitution IV. Recovery of lost records or an account identity
problem is not silently authorized as an ownership-transfer shortcut.

The rationale is to keep payment beneficiary, test eligibility, permanent campaign
history, management rights, and cancellation/refund responsibility aligned with
one authenticated customer while launching. The trade-off is that a customer
cannot officially buy for another bot account or hand over management of an
existing composite, even though a legacy service-transfer flow exists. Including
reassignment instead would require explicit recipient authorization, historical
ownership/refund rules, and treatment of access already known to the former owner.
No account-migration design, data schema, or task breakdown is selected.

### Q-090 — Owner suspension, resumption, and permanent cancellation controls

**Status:** answered; owner single/batch service controls accepted in PC-102.
**Prerequisites:** PC-004/PC-009/PC-010/PC-021-PC-023/PC-066-PC-075/PC-101.
**References:** D10/D14; A14-A19/A23/A28/A29; F-020/F-021/F-033;
  constitution I-IV/VII.

Should the main-store owner have web-admin controls to suspend, resume, or
permanently cancel fulfilled paid/test composites, individually or in a selected
batch, using the established access and cancellation policies?

**REC-090 — accepted in PC-102:** Yes. The authenticated main-store owner may select one
or multiple fulfilled composite subscriptions, preview the exact affected
subscriptions/customers and requested action, and explicitly confirm it with a
reason. Record actor, reason, subscription, action, and separate pending/confirmed
outcomes. Deduplicate selected subscriptions and show each subscription's result;
failure of one must not conceal or undo another's completed result. Retries do not
repeat completed financial or lifecycle effects. Delegated staff cannot perform
these composite actions.

Suspension places an independent owner restriction on the complete subscription's
access. Preserve the URL, credentials, shared allowance, usage history, and original
expiry; account for actual consumption while remote suspension is pending. No
automatic refund or expiry extension results from suspension. A customer cannot
clear an owner restriction through their resume control. Owner resumption clears
only this owner restriction, and enables access only with trustworthy usage,
remaining allowance/validity, and no customer disable, cancellation, or other
restriction. Renewal, rotation, server replacement, and automatic recovery do not
clear an owner restriction. Renewal-payment eligibility and download behavior
during owner suspension remain dependent product questions, not approved here.

Permanent owner cancellation requires explicit confirmation and invalidates the
URL/revokes every child credential. It cannot be resumed or renewed and retains
history and unresolved cleanup. Apply the established fulfilled-cancellation
policy: no automatic unused-service refund; separate owner-approved wallet
compensation remains possible. Explicitly extend PC-073-PC-075's in-flight paid
renewal rule to this owner cancellation: let the renewal resolve cleanly or reach
its original 15-minute deadline, then revoke and refund 100% of that renewal's
actual payment to the same customer wallet once, without usage proration. That
extension is proposed here, not inferred from the earlier customer-only answer.

Use the established normal 60-second all-required-credential access-change target
per subscription and native existing-session handling. Permanent cancellation
also requires URL invalidation and any required wallet credit under the respective
normal 60-second targets. Distinguish desired action from confirmed completion.
At 15 minutes of unresolved suspension/resumption or final cancellation stage,
show owner web-admin attention, attempt the owner Telegram alert, and expose
truthful customer pending/support status when available; retain bounded recovery
without resetting the clock, discarding obligations, or falsely reporting success.
PC-074/PC-075 govern the separate wait for an already-paid renewal.

The rationale is to give the owner useful service controls without letting a
customer or unrelated lifecycle operation undo an operator restriction. The
trade-off is owner intervention being required to lift an owner suspension, with
validity continuing and no automatic unused-service compensation. This does not
decide whether the existing customer-account block should apply such a service
restriction automatically. It does not add an owner cancellation action for an
unfulfilled initial/test claim, arbitrary entitlement editing, or new schemas,
algorithms, worker architecture, or tasks.

### Q-091 — Keep shop-account blocking separate from VPN service restriction

**Status:** answered; separate account/service restrictions accepted in PC-103.
**Prerequisites:** PC-004/PC-009/PC-010/PC-050/PC-066-PC-075/PC-081/PC-082/
  PC-098/PC-101/PC-102.
**References:** D10/D11/D14; A14-A20/A23/A27-A29; F-015/F-033;
  constitution I-III/VII.

Should blocking a customer's shop/bot account leave existing composite VPN access
unchanged, with a separate explicit owner suspension or cancellation required to
restrict that service?

**REC-091 — accepted in PC-103:** Yes. Preserve the shop-account block as an interaction
and eligibility restriction under existing rules. It does not automatically
create or clear a composite service restriction, invalidate an otherwise valid
subscription URL, rotate credentials, end an entitlement, extend expiry, or issue
a refund. Unblocking the shop account likewise does not resume an owner- or
customer-disabled, exhausted, expired, cancelled, or otherwise restricted
subscription. Use PC-102's explicit owner web-admin service action, individually
or in a selected batch, to restrict the VPN service itself.

This concerns a store-admin block of the customer's shop account. A customer
blocking the Telegram bot, a Telegram outage, or bot startup/notification failure
does not itself authorize service suspension/cancellation either; previously
accepted accounting, enforcement, recovery, and URL policies continue. An
otherwise valid URL remains governed by its own subscription state and delivery
gates. Owner-suspension download behavior is a separate unresolved choice.

Preserve existing blocked-account bot/shop restrictions; this does not create a
blocked-customer exception to purchase, test eligibility, or management
authorization. Continue required financial verification, owed credits/refunds,
usage accounting, expiry enforcement, and retained cleanup obligations even when
the customer cannot interact with the bot. Blocking does not erase those
obligations, restart their existing deadlines, or override other accepted
fulfillment/delivery gates. Staff ability to block accounts for legacy shop
purposes does not confer owner-only composite service powers.

The rationale is to make the intended consequence explicit and avoid cutting off
paid/test VPN access as a hidden consequence of a shop-interaction block. The
trade-off is that the owner must perform a separate service action when both
shop interaction and VPN access should be restricted. Simply blocking someone
in the bot cannot be presented as revoking credentials already imported into an
app. No endpoint, permission-schema, or worker design is selected.

### Q-092 — Withhold real configurations during owner suspension

**Status:** answered; status-only owner-suspension downloads accepted in PC-104.
**Prerequisites:** PC-004/PC-021/PC-078-PC-082/PC-102/PC-103.
**References:** D05/D10/D11/D14; A14-A22/A32; E-003;
  constitution II/III/VI/VII.

While an owner suspension is in effect, should its still-valid subscription URL
return only informational entries, withholding all real VPN configurations until
the owner lifts that restriction?

**REC-092 — accepted in PC-104:** Yes. Keep the subscription URL/token and child identities
unchanged, but stop publishing real child configuration links once the owner
suspension is accepted, including while remote disable is still pending. Return
the agreed Base64 informational entries identifying owner suspension and a support
path, with known expiry and accurately qualified quota where available. Use a
customer-facing suspension explanation; do not publish private operator audit
details or real child authentication data in the status-only result.

Describe pending versus confirmed cutoff truthfully. Withholding configurations
does not establish that already imported credentials or native existing sessions
have stopped; PC-102's required-child enforcement and PC-021's native panel policy
remain necessary. This status-only result is an explicit owner-suspension exception
to complete-node downloads, not accidental loss of required nodes during an API
outage or permission to omit healthy nodes from ordinary fulfilled downloads.

When the owner lifts this restriction, the same URL again follows the applicable
delivery gates for the permitted current generation. PC-081/PC-082's complete
current node list remains available for ordinary expired, exhausted, customer-
disabled, or stale-usage-suspended subscriptions with no separate owner restriction
or invalidation/replacement gate. Resumption does not clear those other access
restrictions or restore allowance/expiry. Permanently cancelled or superseded URLs
cannot use this policy to return real credentials or redirect to a new secret URL.
Fetching status/configuration cannot provision, renew, reset usage, or clear a hold.

The rationale is to stop redistributing actual access configurations during an
explicit operator restriction while preserving a reversible URL and useful
customer status. The trade-off is that a refresh may remove the real node list
in a client's presentation, requiring another refresh after owner release. Exact
refresh/selection behavior in the five required apps must be tested under E-003;
no existing-node removal or compatibility outcome is claimed now. The alternative
is retaining the complete disabled node list as under voluntary customer disable.
No serializer syntax, fake-configuration algorithm, HTTP status, cache design, or
worker architecture is selected.

### Q-093 — Stop new renewal funding during owner suspension

**Status:** answered; owner-suspension renewal funding boundary accepted in PC-105.
**Prerequisites:** PC-024-PC-039/PC-061/PC-094/PC-096-PC-099/PC-102-PC-104.
**References:** D09/D10/D14; A03-A06/A15/A19/A25/A28;
  constitution II/III/VII.

Should owner suspension prevent new renewal funding and close renewal quotes
not yet fully funded, while already verified renewals finish under their original
deadline without lifting the owner restriction?

**REC-093 — accepted in PC-105:** Yes. While owner suspension is present, do not start a
new composite renewal/trial-conversion checkout, deduct new wallet funds, invite
an external renewal payment, or accept a new zero-price renewal authorization.
Explain that the owner must first lift the service restriction; payment cannot
lift it. This restriction is per subscription, not a new account-wide block on
otherwise eligible purchases/subscriptions. Customer disable and ordinary
expiry/exhaustion retain their separately agreed renewal eligibility.

When owner suspension is accepted, reject this subscription's renewal quotes
that have not reached full verified payment (or validated zero-price final
confirmation). Release any held wallet contribution and coupon use once, with
wallet value visible/spendable within the normal 60-second application/database
target. This explicitly adds a reason for terminal quote rejection under PC-098;
it is not an unapproved unpaid-order expiry timer or silent repricing. After
owner release, a new checkout uses current offers/eligibility/prices.

Any subsequently validly verified external payment for such a rejected renewal
becomes store-wallet credit once under PC-094/PC-098. It cannot reopen the quote,
renew the subscription, or clear the suspension. Previously returned wallet value
must not be returned again when late external money arrives. Mismatched or
unverifiable payments remain investigation, not settlement. PC-099 continues to
separate repeated notifications from distinct extra receipts.

If full payment was already verified, or a zero-price renewal already validly
authorized, before the owner suspension, let that in-flight renewal resolve
under its original 15-minute clock and accepted complete-node/settlement rules.
It must preserve the owner restriction throughout; confirmed entitlement changes
do not authorize access or real-configuration download while the hold remains.
On complete success apply the accepted allowance/expiry/carryover once, with
validity continuing under the owner hold and no automatic refund merely because
of that suspension. On renewal failure/timeout use the accepted full actual-
payment wallet refund and coupon restoration, retaining cleanup. A separately
accepted permanent cancellation while renewal is in flight still invokes
PC-102/PC-073-PC-075's sequential revocation and full renewal-payment refund.

The rationale is to avoid knowingly taking new renewal money when an operator
restriction prevents service, without treating a later suspension as permission
to undo or replay an already verified transaction. The trade-off is that a held
customer cannot renew until owner release, unused time continues passing, and
closed unpaid quotes lose their old price/offer guarantee. An already verified
renewal can complete while access remains restricted; owner compensation remains
discretionary under PC-069-PC-071. No ordering algorithm, state schema, gateway
workflow, worker architecture, or task breakdown is selected.

### Q-094 — Export one real configuration per explicitly configured plan node

**Status:** answered; one faithful real export per configured node accepted in PC-106.
**Prerequisites:** PC-001-PC-005/PC-008/PC-011/PC-049/PC-076-PC-086/PC-098/PC-104.
**References:** R02-R05; D04/D05/D11; A01/A02/A20-A24/A28; F-022/F-034;
  E-001/E-003; constitution I/II/V/VI/VII.

Should a composite export exactly one real configuration for each explicitly
configured plan node, rather than automatically including every alternative
address or link advertised by its panel?

**REC-094 — accepted in PC-106:** Yes. Each included node has one owner-selected intended
connection endpoint/configuration and a descriptive remark. In an ordinary
complete export, publish exactly one faithful real URI for each such node, in
the plan's stable configured order. The initial A-only five-choice plan therefore
has five real entries; the six-node acceptance fixture has six. Informational
entries are additional status rows, not real VPN nodes or allowance/meter grants.
Neither five nor six is a feature maximum; arbitrary configured collections
remain supported under PC-001/PC-002.

Panel-advertised alternative addresses, duplicates, or multiple native links for
the same identity do not automatically add choices, credentials, allowance, or
meters. To offer another real choice, the owner must explicitly configure it as
an included plan node under the independent-credential and shared-accounting
rules. A new catalog choice does not silently change an accepted quote or sold
subscription. Equivalent-server replacement preserves intended choices under
its existing policy; broader topology editing/migration remains unapproved.

Export must preserve the selected node's actual address/port, protocol, transport,
security/flow settings, UUID/password, and intended routing. Do not arbitrarily
pick the first native link or invent missing settings when the intended endpoint
cannot be identified faithfully. The complete-delivery gates and existing
failure/refund rules still apply; unsupported/missing required exports cannot
be called successful fulfillment or silently omitted. Already fulfilled downloads
use their permitted verified complete current configuration under PC-081/PC-082,
with the explicit owner-suspension exception PC-104 and invalidation/replacement
gates retained. No download may create extra credentials or change entitlement.

The rationale is a predictable list matching the purchased choices rather than
accidental expansion from panel export settings. The trade-off is owner selection
of each intended endpoint; a second advertised address is not automatically
visible as another choice. Faithful export/routing/client support remains
controlled evidence under E-001/E-003. No selection algorithm, API method,
endpoint schema, serializer implementation, or task breakdown is chosen.

### Q-095 — Financial catch-up after a whole-manager outage with intact history

**Status:** answered; intact-history financial catch-up accepted in PC-107.
**Prerequisites:** PC-005/PC-012-PC-014/PC-018-PC-023/PC-037/PC-048/PC-049/
  PC-057-PC-059/PC-067/PC-073-PC-075/PC-094-PC-105.
**References:** D02/D08/D10/D13; A03-A06/A15/A16/A25/A28/A30/A31;
  F-005/F-029/F-031; E-002/E-004/E-005; constitution II/IV/VII.

After the entire subscription manager returns with intact committed history,
should it apply the original deadlines and complete any overdue, verified wallet
refunds/credits within 60 seconds of restored safe financial processing?

**REC-095 — accepted in PC-107:** Yes. Application outages/restarts do not reset original
fulfillment/renewal deadlines, expiry, last-trustworthy-sample grace, replacement
cooldown, campaign history/cap, or retained restrictions. On recovery, reconcile
uncertain effects before repeating them and use trustworthy original outcome/
timing evidence. If complete initial delivery or renewal was not achieved within
its original 15-minute window, apply the agreed terminal failure/refund policy;
do not offer a new window or late benefits merely because the manager restarted.
For initial fulfillment, remote credentials existing during the outage alone do
not establish timely URL availability under PC-049.

For a money obligation whose beneficiary, actual verified amount, and prior
debit/credit/refund outcome are established from intact history and required
verification, make an overdue wallet refund/credit visible and spendable within
60 seconds after application/database processing can safely perform it. If
those prerequisites were already established before the outage, the target
starts when safe financial processing resumes. This catch-up target does not
retroactively claim the original 60-second deadline was met. Track its missed
deadline and resulting recovery outcome; repeated recovery cannot duplicate it.
Cleanup or notification failure does not delay an otherwise verifiable credit.

Unknown payment or prior financial-effect outcomes remain explicit and are
reconciled before settlement/retry; the target cannot authorize fabricated
evidence or duplicate credit. Show overdue unresolved obligations to the owner
on recovery, attempt the existing owner Telegram alert, and retain the customer
pending/support state when available. Do not hide overdue work behind a newly
started 15-minute attention timer. Once an uncertain money obligation becomes
verifiable and processing safe, its normal 60-second credit target applies.

Previously fulfilled subscriptions retain their original allowance/expiry and
restrictions while outage accounting and remote state catch up. Do not renew,
refill, re-enable known revoked access, create debt for absorbed overrun, grant
automatic expiry extensions, or award automatic compensation for the outage.
Use the established stale-usage, cutoff, recovery, and owner gap-settlement
policies. A manager outage cannot guarantee timely remote cutoff while VPN paths
continue; PC-019's best-effort exposure remains accepted and measurable as missed
or pending work rather than falsely confirmed enforcement.

This question concerns restart/outage recovery with intact committed records.
A stale backup restore, missing purchase/revocation/payment history, or corrupt
records requires constitution IV's separate reconciliation/remediation decision
and is not approved for automatic resumption by this answer. The rationale is
prompt financial catch-up without erasing deadlines or replaying effects. The
trade-off is overdue orders failing/refunding instead of being delivered after
recovery, and owner attention where safe reconciliation remains impossible.
Whole-host recovery-time/data-loss promises, backup strategy, polling/retry
algorithms, worker architecture, and task breakdown remain unselected.

### Q-096 — Recovery hold for uncertain stale-backup history

**Status:** answered; affected-operation stale-restore recovery hold accepted in PC-108.
**Prerequisites:** PC-004/PC-005/PC-018-PC-023/PC-057-PC-060/PC-084/
  PC-094-PC-107.
**References:** D08/D10/D13/D14; A03-A06/A09/A11/A15-A20/A28-A31;
  F-035; E-004/E-005; constitution II-IV/VII.

After a stale-backup restore, should affected subscriptions and operations remain
on a recovery hold until their current entitlement, ownership, financial effects,
and lifecycle restrictions can be verified?

**REC-096 — accepted in PC-108:** Yes. A restored snapshot is historical evidence, not
proof of current payment, allowance, expiry, campaign capacity, URL/credential
generation, or remote access state. Reconcile against available newer evidence
before dependent financial/provisioning/enable/export mutations resume. Restore
known newer cancellation, rotation, owner/customer restriction, purchase/renewal,
usage, and financial outcomes without replaying old effects. Preserve pre-restore
evidence, history, intended identities, and cleanup/recovery responsibility.

Keep affected subscriptions on explicit recovery hold where eligibility or
current credential generation remains uncertain: do not recreate/enable clients,
publish potentially revoked/superseded real configurations, grant a fresh bucket,
extend expiry, transfer ownership, or report restored access from the snapshot
alone. Give truthful recovery-pending/support status without presenting uncertain
expiry or usage as current fact. For credentials with verified management
ownership, pursue safe access suspension/cleanup under the existing best-effort
policy; do not mutate unverified remote identities or claim that a hold has
terminated already imported access/native sessions.

Hold affected money/claim operations whose prior outcomes or eligibility cannot
be established. Do not automatically debit/refund/credit a transaction that may
already have settled, restore coupon capacity, reset `test_used`, or reopen the
150-user campaign using old counts. If permanent campaign history/cap cannot be
verified, pause new campaign claims until resolved; other verified catalog/test
paths remain available when their own financial and eligibility state is safe.
Release verified subscriptions/operations individually instead of unnecessarily
holding an entire recovered store. If shared affected state cannot be isolated,
expand the hold only as far as required to avoid unsafe effects; shared wallet
recovery may affect directly dependent legacy callers and must be explicit in
the later compatibility/restore plan.

Make unresolved gaps and partial recovery visible to the owner with evidence,
affected records, and a remediation/support path. The existing PC-084 usage-gap
settlement remains available only when entitlement/ownership/lifecycle history
is intact; it cannot authorize a blanket acceptance of missing purchase, refund,
revocation, rotation, or campaign history. Irrecoverable gaps require a specific
documented remediation or risk-acceptance decision under constitution Governance.
This answer does not itself grant an exception or let a generic resume button
override those constitutional obligations.

The rationale is to avoid resurrecting cancelled access, duplicating money, or
granting another campaign/test allowance after old-data restoration. The trade-off
is longer interruption for affected customers and owner investigation where a
snapshot and live panel state cannot establish complete history. Recovery-point/
time promises, backup scope/mechanisms, evidence sources, orphan-discovery rules,
and detailed reconciliation architecture remain separate choices/planning work.

### Q-097 — Block destructive resets and panel deletion that erase composite responsibility

**Status:** answered; destructive-operation composite guards accepted in PC-109.
**Prerequisites:** PC-004/PC-005/PC-057-PC-060/PC-072-PC-075/PC-086-PC-091/
  PC-101-PC-108.
**References:** D10/D13/D14; A17/A19/A23/A24/A26/A28-A31; F-006/F-036;
  constitution I-IV/VII.

For launch, should factory reset and forced panel deletion be blocked whenever
they would erase composite history or the records needed to manage/reconcile
existing credentials and money?

**REC-097 — accepted in PC-109:** Yes. Reject the main-store factory-reset action while
it would erase composite ownership, financial/usage/lifecycle history, pending
work, or permanent campaign recipient/cap history. Protect referenced panel,
customer, subscription, and dependent records from destructive removal that
would lose required evidence or sole management/cleanup responsibility. A generic
`force` option or confirmation phrase cannot bypass this composite protection.
No new customer hard-delete flow is added by this answer.

Show the owner why the operation is blocked and which composite responsibilities
or histories remain. Use the already approved permanent cancellation, safe
cleanup, or equivalent-server replacement controls to address service; those
actions still retain required history and unresolved remote obligations.
Cancelling all subscriptions or refunding orders does not authorize erasing
permanent campaign history, financial evidence, or pending old-server cleanup.
Do not turn a database reset or panel-row removal into an implicit batch remote
revocation or automatic refund with unreviewed consequences.

A panel retired/deactivated for new composite sales or test claims must be
excluded from newly accepted composite offers/claims, but deactivation cannot
by itself stop existing composite accounting, enforcement, or retained cleanup,
or revoke existing access. Keep
management references usable for those responsibilities; explicit owner service
restriction and equivalent replacement remain separate approved operations.
Affected legacy-only reset/deletion/deactivation behavior outside composite
dependencies remains preserved. Ordinary test-usage resets remain approved
under PC-060 and must preserve campaign history/cap; they are distinct from a
whole-store factory reset.

This is a launch guard against destructive loss, not approval of a new export/
handoff/general teardown feature. Future removal or retention changes require an
explicit compatible policy preserving or durably handing off obligations under
constitution IV. Raw-sample compaction/retention mechanisms are planning work;
the guard protects required accounting evidence rather than mandating retention
of every raw sample forever.

The rationale is to prevent local administration from orphaning credentials,
losing owed money, or reopening the campaign. The trade-off is the existing
reset/force-delete shortcut becoming unavailable for composite-bearing data;
the owner must use the deliberate service controls and retain protected records.
No tombstone schema, retention period, cleanup algorithm, teardown architecture,
or tasks are selected.

### Q-098 — Catalog and pending checkout behavior during equivalent-server replacement

**Status:** answered; cutover sales and renewal policy accepted in PC-110.
**Prerequisites:** PC-005/PC-011-PC-014/PC-025/PC-035-PC-039/PC-049/
  PC-057-PC-061/PC-083/PC-086-PC-091/PC-094-PC-099/PC-105/PC-109.
**References:** D04/D07/D09/D10/D14; A03-A06/A19/A24/A25/A28;
  constitution I-IV/VII.

When retiring a server for equivalent replacement, should affected new checkouts/
test claims pause and unfunded quotes close until a ready replacement offering
is explicitly activated, without waiting for every existing customer to migrate?

**REC-098 — accepted in PC-110:** Yes. At the owner's authorized retirement/cutover of
the old serving topology, stop accepting new initial checkouts/test claims using
it. Reject affected quotes not yet fully payment-verified or zero-price-authorized;
restore held wallet contribution and coupon use once under the normal 60-second
wallet target. Validly verified external money arriving after rejection becomes
wallet credit under PC-094/PC-098, not late fulfillment. This is explicit
operational quote rejection, not silent repricing or an unpaid-order expiry timer.

Keep unaffected offers/claims available when their own prerequisites are safe.
Explain affected temporary unavailability; a refused new claim/checkout cannot
debit money, reserve test allowance/campaign capacity, start a fulfillment clock,
or gain priority in a new waiting queue. Owner activation of a prepared,
validated equivalent replacement offering can reopen new purchases/test claims
before all existing subscriptions have moved. Apply current prices and test/
campaign eligibility to newly accepted orders/claims. The campaign's permanent
recipient history/cap remains unchanged.

Already fully payment-verified purchases/renewals, validly zero-price-authorized
orders, and accepted pending test claims retain their original terms, clocks,
reservations, and complete-fulfillment gates. They may finish on the owner's
explicitly authorized equivalent target only when intended node choices/service,
accounting prerequisites, authority, and all delivery gates are preserved. Do not
silently substitute an unrelated topology, create another entitlement, restart
15 minutes, or revive a terminal failed/cancelled claim/order. If timely complete
fulfillment cannot be achieved, use the accepted failure/refund/coupon or test/
campaign reservation rules; uncertain claim outcomes retain their holds until
reconciled, and remote cleanup remains independent. Renewal preserves the prior
entitlement while pending under PC-036/PC-037.

For an existing subscription whose equivalent move is still pending, block new
renewal/conversion funding and close affected unfunded renewal quotes as above;
do not charge for a pending migration. Once that subscription's full replacement
is ready with trustworthy accounting, permit normal renewal subject to its other
eligibility/restriction rules, without waiting for the remaining batch. Matching
renewal offers remain eligible when their intended node choices match through
the explicit equivalent replacement; changed physical server/inbound identifiers
alone must not make an otherwise matching preset ineligible. Different country/
protocol/node sets still require a separate purchase or a separately approved
broader migration. This defines product equivalence, not a storage identity model.

The rationale is to stop accepting work onto a retired/unready target while
reopening service independently for prepared new offers and completed customers.
The trade-off is temporary unavailability of affected sales/tests/renewals,
loss of closed quotes' old price guarantees, and refunds for paid operations that
cannot finish within their original window. No worker ordering, concurrent-
operation algorithm, catalog schema, migration API, or tasks are selected.

### Q-099 — Equivalent replacement for inactive subscription histories

**Status:** answered; inactive replacement eligibility accepted in PC-111.
**Prerequisites:** PC-005/PC-023-PC-039/PC-061/PC-066/PC-072-PC-075/
  PC-082/PC-086-PC-091/PC-102/PC-104-PC-110.
**References:** D08/D09/D10/D14; A12/A15/A17-A19/A24/A29-A31;
  constitution II-IV/VII.

Should equivalent replacement also cover non-cancelled expired, exhausted, and
disabled subscriptions, while preserving their inactive state?

**REC-099 — accepted in PC-111:** Yes. Permit the owner to select fulfilled paid or test
subscriptions that are not permanently cancelled, including expired, exhausted,
customer-disabled, owner-suspended, and stale-usage-suspended subscriptions.
The bulk preview must explicitly identify included inactive subscriptions;
"all affected subscriptions" is not silently limited to active access.
Replacement preserves their allowance, actual usage/history, original expiry,
ownership, URL, and every applicable restriction. Provision moved credentials
in their required inactive state rather than enabling them merely to complete
replacement. Continue accounting/cleanup responsibility for old credentials.

After successful equivalent movement, subsequent eligible renewal/conversion or
resumption uses the unchanged subscription URL and the current replacement
credentials, under its normal terms and independent restriction gates. Movement
does not replenish an expired/exhausted subscription, clear customer/owner holds,
reset cooldown/test/campaign history, or authorize a resume from uncertain data.
Downloads and refresh notices must represent the actual state; owner suspension
still serves status-only entries under PC-104.

Permanently cancelled subscriptions remain terminal and cleanup-only; do not
recreate their service on the replacement. Unfulfilled or terminal failed orders/
claims are not historical fulfilled subscriptions and cannot be revived through
this selection. Accepted pending fulfillment retains PC-110's original-window
policy. Cases under PC-108 recovery hold with uncertain entitlement, ownership,
or lifecycle remain ineligible until verified or specifically remediated under
the constitution; selecting them cannot waive that requirement.

The PC-090 benchmark counts selected eligible inactive subscriptions as well as
active ones: up to 150 subscriptions with five moved credentials each under its
supported normal conditions, not a new limit. Technical feasibility and measured
results remain unverified.

The rationale is to preserve later renewal/resumption through the same URL after
the old server retires. The trade-off is replacement work and remote credential
capacity for customers who may never return. Selecting only active subscriptions
would require a separately defined later migration before those customers could
renew/resume; that alternative is not approved here. No selection algorithm,
schema, retention period, worker architecture, or tasks are chosen.

### Q-100 — Recoverable local-history objective for whole-host loss

**Status:** answered; fifteen-minute recovery-point objective accepted in PC-112.
**Prerequisites:** PC-003-PC-005/PC-057-PC-060/PC-084/PC-107-PC-111.
**References:** D13; A23/A30/A31; S11; F-035/F-037; E-004/E-005;
  constitution II-IV/VI/VII.

For launch, should the normal recovery objective be a verified copy of required
local history captured no more than 15 minutes ago and recoverable after loss
of the subscription-management host?

**REC-100 — accepted in PC-112:** Yes. Under supported normal operating conditions,
maintain a completed, validated recoverable copy of the required authoritative
local composite state whose capture point is at most 15 elapsed minutes old and
which remains accessible if the management host is lost. The scope includes
subscription ownership/tokens, entitlement/usage and billing boundaries, money/
coupon outcomes, test/campaign eligibility and permanent recipient history,
current/retired credential identities, and pending work/cleanup responsibility,
with required dependent main-store state. It does not assume all those records
are already present or decide their storage design.

Measure age from the verified capture point, not a file's delivery timestamp or
an attempted backup. Show the owner the last verified recoverable point and
whether the objective is overdue/unknown; backup validation or delivery failure
must not report fresh protection. Make failures actionable in web admin and
attempt an owner Telegram alert, retaining the failure/recovery outcome rather
than treating a send attempt as successful delivery.

This is a launch recovery objective requiring controlled proof, not a claim that
current code supplies it, a zero-data-loss promise, permission to discard unknown
financial/revocation/campaign history, or proof of current panel state. Copying
every 15 minutes alone does not establish it: completion/validation/availability
must meet the objective. If the objective is missed, record the actual exposure
and use PC-108's reconciliation/hold/governed-remediation rules after loss rather
than inventing the missing interval. Expiry and existing service/financial rules
remain unchanged; this recommendation adds no automatic mass VPN suspension or
new refund solely because a backup is overdue.

The rationale is to limit unrecoverable local history for paid operations and
the capped launch campaign; a daily recovery point can lose a substantial part
of either. The trade-off is more backup/validation/availability work and storage/
transfer cost than an hourly or daily objective. A one-hour objective is a lower-
cost alternative with a larger history gap to investigate after failure.

Recovery-time expectations are the next independent product choice. Snapshot/
journal method, cadence, destinations, retention, encryption/secret recovery,
restore coordination, general infrastructure backup, and implementation tasks
remain planning work. No new minute-based admin control or database replacement
is selected by this objective.

### Q-101 — Four-hour safe recovery objective on a prepared host

**Status:** answered; four-hour prepared-host recovery objective accepted in PC-113.
**Prerequisites:** PC-005/PC-019/PC-023/PC-069-PC-071/PC-081/PC-082/
  PC-086-PC-091/PC-104/PC-107-PC-112.
**References:** D11/D13; A16/A20/A23/A30/A31; S06/S11;
  F-035/F-037; E-004/E-005; constitution II-IV/VI/VII.

Should launch recovery target safe management and subscription-URL availability
within four hours of owner-initiated recovery on a prepared replacement host?

**REC-101 — accepted in PC-113:** Yes. Under supported normal conditions, target four
elapsed hours from the owner beginning recovery with a prepared replacement host,
the required available validated recovery copy, release/configuration/authorized
secret inputs, and external HTTPS/domain/panel prerequisites. Host purchasing/
provisioning, owner response time before recovery begins, and unavailable external
dependencies are outside that conditional target; report them separately rather
than implying restoration within four hours of the original incident. Once the
target's conditions are met and recovery begins, retries/process restarts do not
restart its clock. Target feasibility remains unverified.

Within the target, restore main-store Telegram customer management, owner web
management, the existing public subscription URL identity, and safe accounting/
enforcement/recovery processing for independently verified subscriptions and
financial operations. Apply PC-107/PC-108: retain original clocks/terms,
catch up verifiable credits, reconcile newer evidence before dependent effects,
and preserve confirmed cancellation/rotation/restrictions and remote cleanup.
Restoring the public endpoint must not publish a stale token or credential
generation merely to meet the target. Continue permitted verified complete or
status-only downloads under the existing access policies.

Cases with unresolved newer/missing history or unavailable required services
remain truthfully pending/recovery-held with evidence, owner action, and the
existing governed remediation boundaries. Bring up truthful status/recovery
management for those cases and report partial recovery; do not call a running
process, restored file, or some recovered customers a fully recovered store.
The conditional objective measures verified service recovery with unresolved
cases explicitly reported; it is not a four-hour promise to reconstruct
irrecoverable history or bypass holds. If the target is missed, show overdue
recovery, affected functions/cases, and owner action while retaining bounded
repeat-safe recovery and obligations.

Preserve PC-019's outage exposure and PC-023's original expiry. No automatic
time extension, automatic outage refund, fresh allowance, or hard cutoff while
the manager is unavailable is introduced. Approved discretionary wallet
compensation remains available. Do not require an always-ready second deployment
or select any failover architecture in this interview.

The rationale is a measurable restoration goal suitable for an owner-operated
launch without promising instant disaster recovery. The trade-off is up to four
hours of control/download interruption after prerequisites are ready, plus owner
response/infrastructure preparation time before that clock. A tighter one-hour
target would require more operational investment; an unbounded best-effort
objective would provide less predictable recovery. Exact supported load, backup/
deployment method, evidence sources, hosting, secret handling, restore mechanisms,
and task breakdowns remain planning/controlled-verification work.

### Q-102 — Owner-controlled recovery of unexplained panel identity loss

**Status:** answered; owner-controlled identity-loss recovery accepted in PC-114.
**Prerequisites:** PC-004/PC-005/PC-018-PC-023/PC-034-PC-039/PC-042-PC-047/
  PC-083/PC-084/PC-086-PC-088/PC-102/PC-107-PC-113.
**References:** D08/D10/D14; A09/A11/A14-A19/A24/A31;
  F-004/F-013/F-025/F-039; E-001/E-002; constitution II-V/VII.

Should unexplained deletion or identity replacement of a managed child in 3x-UI
require owner-controlled investigation/recovery instead of automatic recreation?

**REC-102 — accepted in PC-114:** Yes. The agreed local entitlement, ownership, intended
credential generation, and restrictions remain authoritative for the composite.
Routine direct panel edits are not an alternative way to renew, refill, cancel,
transfer, or replace it. For an intact verified managed identity with trustworthy
accounting, bounded repeat-safe reconciliation may restore its already approved
desired enable/disable, quota, or expiry settings; do not adopt extra allowance,
later expiry, or cleared restrictions from an unexpected panel edit.

An unexpectedly missing, renamed/replaced, or mismatched managed identity must
not be silently recreated, adopted as an unrelated user, replaced with a fresh
UUID, or reported as a zero-usage new epoch. Retain known usage, identities,
ownership, restrictions, and cleanup evidence. Make the discrepancy visible to
the owner with an attempted Telegram alert and recovery path; show truthful
customer service/accounting uncertainty rather than full-health claims. Do not
publish an unverified replacement identity/configuration. Safe operations still
require verified ownership and must not alter unrelated panel clients or shared
routes.

Apply the existing whole-subscription stale-meter rule when reliable required
usage is lost: five minutes from the last trustworthy sample, not five minutes
from noticing deletion or each retry. Established expiry/exhaustion and explicit
restrictions continue without that grace. Track cutoff as pending/confirmed under
the native-session and best-effort policies; unknown usage is never zero. Identity
loss does not itself refund, extend validity, grant more quota, or consume/reset
test/campaign eligibility.

The owner investigates and uses verified recovery/approved replacement controls
to restore the intended service. Unrecoverable consumption requires PC-084's
explicit usage-gap settlement only when entitlement/ownership/lifecycle history
is intact; missing other history remains under PC-108's specific reconciliation/
governance boundaries. Resume automatically only after intended identity/current
metering and all normal eligibility/restriction conditions are verified under
PC-022. Repair cannot resurrect a terminal cancelled subscription, bypass leak
replacement gates, clear customer/owner restrictions, or mint a new entitlement.
This approves no separate general repair UI, arbitrary remote-history import,
panel user adoption, or shared-infrastructure edit feature.

The rationale is to avoid undoing a deliberate revocation or losing unobserved
consumption through apparently helpful recreation. The trade-off is owner
investigation and possible whole-subscription interruption instead of automatic
repair when the identity/history is uncertain. Ordinary API outages with intact
credentials still follow the already accepted automatic-recovery policy; this
question does not reopen that choice. Exact detection, reconciliation and repair
mechanics, counter epochs, polling, and APIs belong to planning and controlled
verification.

### Q-103 — Sixty-second healthy usage freshness and earlier delay warnings

**Status:** answered; normal freshness and delay warnings accepted in PC-115.
**Prerequisites:** PC-004/PC-015/PC-018-PC-022/PC-079/PC-081/PC-082/
  PC-084/PC-087/PC-104/PC-107-PC-114.
**References:** D02/D08/D11; A07-A17/A20/A32; S05-S07;
  F-023/F-025/F-039; E-001-E-004; constitution II/VI/VII.

Should normal usage information be no more than 60 seconds old, with older or
incomplete readings visibly marked delayed even before five-minute suspension?

**REC-103 — accepted in PC-115:** Yes. Under supported normal conditions, a customer's
Telegram subscription details/refresh and a newly fetched public subscription
response should show reconciled whole-subscription usage/remaining allowance
using trustworthy required observations at most 60 elapsed seconds old. Measure
age from underlying trustworthy readings, including integration/display delay,
not the bot refresh, HTTP response, cache-write time, or last successful attempt.
The normal freshness target does not add another 60 seconds to PC-020's combined
quota-crossing observation/enforcement target or select a polling interval.

Call usage current/verified only when every required current meter has trustworthy
readings at most 60 seconds old and history is reconciled. A newer healthy child's
reading cannot hide another required meter's older reading. The customer-visible
timestamp must conservatively represent the required observations; show the
oldest required trustworthy observation time where readings differ rather than
claiming a simultaneous exact balance. Retired-server cleanup meters excluded by
PC-087 do not independently stale verified replacement accounting.

As soon as an update is known incomplete/untrustworthy, or any required reading
is older than 60 seconds, qualify information as delayed/incomplete under PC-079.
Retain the last reliable whole-subscription figure and its genuine timestamp;
show unknown if none exists. A 61-second-old value may still be useful context,
but is not a current verified balance. This warning is separate from PC-018's
suspension request when a required reading reaches five minutes old. Do not label
grace as confirmed cutoff, reset it on fetch/retry, or fabricate zero/unlimited
usage. Known expiry/exhaustion and independent restrictions remain effective.

Use compatible freshness/uncertainty semantics for customer displays, exports,
accounting eligibility, and recovery; API reachability or a fresh partial reading
cannot make unresolved history trustworthy. Informational configuration names
remain snapshots until the customer refreshes their app. This approves no live
push, compulsory app refresh frequency, per-download panel call, or synchronous
sampling design.

The rationale is timely useful shared allowance without hiding delays during
the already approved five-minute grace. The trade-off is more frequent reliable
observations and visible delay warnings sooner than suspension; a looser display
target reduces observation load but provides less timely customer information.
Supported-load feasibility, timestamp representation, serialization/caching,
sampling and reconciliation algorithms, and detailed display rounding remain
planning/controlled-verification questions. No passing measurement is asserted.

### Q-104 — Sixty-second automatic resumption after verified recovery readiness

**Status:** answered; automatic resumption target accepted in PC-116.
**Prerequisites:** PC-018-PC-023/PC-039/PC-066/PC-067/PC-084/PC-087/
  PC-102/PC-107-PC-115.
**References:** D02/D08/D10; A09/A12-A16/A19/A31; S06/S07;
  E-001/E-002/E-004; constitution II/VI/VII.

Once all recovery conditions are verified, should automatic access restoration
complete within 60 seconds under normal conditions?

**REC-104 — accepted in PC-116:** Yes. Preserve PC-022's already approved automatic
recovery. Under supported normal conditions, once all required intended
identities/current readings are verified, history is reconciled (including an
explicit valid PC-084 settlement if necessary), usage freshness meets PC-115,
allowance/time remain, and no independent restriction/cancellation/revocation
prevents access, target confirmed fresh-authentication availability on every
required credential within 60 elapsed seconds. Start at verified satisfaction
of those prerequisites, not later worker selection or retry. Mere API reachability,
an incomplete reading, or unresolved history does not start an eligible recovery.

Add no fixed stability dwell or manual approval for an ordinary resolved API
outage. Any required explicit identity/usage-gap investigation/settlement remains
under its accepted policy, not waived by automatic resumption. Retries/restarts
do not restart the recovery clock. If prerequisites cease to hold or a newer
restriction/cancellation/expiry applies, do not let an older recovery operation
enable access; retain truthful changed/pending status and the applicable cutoff
or hold. Partial enablement is not confirmed whole-subscription restoration.

At 15 elapsed minutes from eligible recovery readiness, unfinished restoration
is overdue and actionable in owner web admin with an attempted owner Telegram
alert and customer pending/support status. Retain bounded repeat-safe recovery
and all unresolved remote obligations. Do not compensate by resetting allowance,
extending expiry, silently declaring success, or erasing pending work. Independent
customer/owner holds remain until their own authorized release; permanently
cancelled subscriptions never qualify. Native existing-session handling and
best-effort outage limits remain unchanged.

The rationale is prompt recovery of still-valid service using the same normal
access-restoration expectation as customer resume. The trade-off is potential
repeated suspension/resumption during unstable reporting without a fixed dwell;
adding an intentional dwell would delay restoration. This is a product timing
target and attention threshold, not evidence it passed, a sampling interval,
retry/concurrency algorithm, worker architecture, or supported-load selection.

### Q-105 — Launch scope of optional customer reminders

**Status:** answered; paid reminder scope and optional exclusions accepted in PC-117.
**Prerequisites:** PC-006-PC-010/PC-024/PC-051-PC-053/PC-055-PC-064/
  PC-079/PC-091/PC-103-PC-105/PC-115/PC-116.
**References:** D07/D09/D11; A15/A19/A23/A25/A28/A32;
  F-038/F-039; constitution I-III/VII.

Should launch support expiry/quota reminders for paid composites, while deferring
test reminders and connection/activity alerts?

**REC-105 — accepted in PC-117:** Yes. Include simple Telegram expiry and shared-quota
reminders for fulfilled paid composite subscriptions, including a test after
successful paid conversion. Let the owner enable/disable these reminder types.
Messages describe the one subscription's shared allowance/expiry and lead to
its appropriate bot details/eligible renewal flow rather than another entitlement
or one alert per child. Use authoritative verified composite terms/accounting,
never unsafe legacy header defaults or a false current-session inference.

Defer optional expiry/quota reminders for still-free tests, including the campaign,
and defer "connected", "not connected", current-online/session, and first-use
alerts for composites. This excludes optional reminder features only: mandatory
fulfillment/failure/pending/support/replacement messages and retrievable truthful
status already agreed for paid and test subscriptions remain required. Customer
informational entries also remain required; a test customer can inspect its own
terms and use the accepted conversion flow.

Do not automatically generate a promotional coupon as a side effect of a
composite reminder. Existing valid owner-defined coupons and approved checkout
discounts remain supported. Preserve affected legacy reminders, their settings,
and existing gift/reward behavior outside composite scope rather than removing
their coupon functionality globally.

Failed or uncertain optional reminder delivery is distinct from successful
delivery, cannot be permanently counted as sent merely on attempt, and must
follow bounded repeat-safe delivery recovery with visible unresolved outcome.
It must not change allowance, expiry, enforcement, refund deadlines, campaign
history, or eligibility. No real notifications are authorized by this interview.

The rationale is to help paying customers act before finite service runs out
without inheriting automatic discounts or historical-usage-as-connection claims.
The trade-off is fewer prompts for free-test conversion and no connection alerts
or automatic reminder coupons at launch. Thresholds, timing, repeat boundaries,
and which restricted states receive optional reminders are dependent choices;
the source's five-day/80% defaults are facts, not approved by this scope answer.
Delivery mechanisms, worker architecture, localization, and tasks remain planning.

### Q-106 — Configured reminder thresholds and one logical notice per paid term

**Status:** answered; reminder thresholds/repeat/eligibility rules accepted in PC-118.
**Prerequisites:** PC-015/PC-023-PC-039/PC-051-PC-052/PC-061/
  PC-066/PC-072-PC-075/PC-097/PC-103-PC-105/PC-110/PC-115-PC-117.
**References:** D03/D09/D11; A07/A12/A15/A19/A25/A32;
  F-038/F-039; E-002/E-004; constitution I-III/VI/VII.

Should reminders use the owner's existing configured thresholds (defaults: five
days before expiry and 80% used), with one logical notice of each type per
successfully fulfilled paid term?

**REC-106 — accepted in PC-118:** Yes. Respect existing valid main-store enable/threshold
settings for composite reminders while preserving their legacy behavior. Defaults
remain both types enabled, expiry within five elapsed 24-hour days (120 hours)
while not yet expired, and quota at or above 80% used. Retain the existing
configurable alternative quota mode: remaining allowance at or below the chosen
binary GiB threshold, whose source default is two GiB. The alternative is used
only if selected; do not send another quota reminder just because both percent
and remaining-byte conditions happen to be true. No automatic coupons apply.

The thresholds concern the subscription's current verified shared allowance and
actual common expiry, never one node's allowance or historical lifetime usage.
After successful initial paid catalog fulfillment or successful full renewal/
test-to-paid conversion, start a new logical reminder period. The current period's
allowance includes carried unused data plus the newly granted data; previously
billed historical consumption cannot immediately trigger 80% merely because its
cumulative counter is large. Carried validity and the 45-day cap affect the actual
current expiry used for the expiry threshold. Authorized zero-price normal
catalog fulfillment follows the same product-class terms under PC-097.

Allow one logical reminder of each type per successfully fulfilled paid period.
Failed/unfunded/pending renewal does not start another period. Repeated refresh,
restart, enabled-setting toggle, threshold edit, ordinary recovery, customer
disable/resume, or credential/server replacement does not rearm a successfully
sent reminder in the same period. Retry known failed/uncertain delivery under
PC-117 without deliberately duplicating known successful sends; do not claim
exactly-once external Telegram delivery where its outcome is uncertain.

Optional reminders are eligible only when the relevant type is enabled, the
verified condition currently holds, service is fulfilled and not permanently
cancelled/expired, no paid renewal is in flight, and an ordinary paid renewal is
currently permitted. Skip owner suspension/recovery uncertainty/migration-pending
or other gates that block renewal; reevaluate after they resolve rather than
silently consuming the notice. Customer-disabled access alone does not prohibit
the reminder or renewal; neither notice nor renewal clears that disable. An
exhausted but unexpired subscription may receive the quota notice if ordinary
renewal is eligible, accurately saying it is exhausted. Never present the 80%
threshold as its actual consumption if delivery catches it at a higher figure.

Under supported normal conditions, target Telegram acceptance of a qualifying
reminder within five elapsed minutes of its condition and eligibility being
satisfied, including observation/waiting time. Notification receipt does not
prove reading. Known expiry may support the expiry condition independently of
traffic, but unresolved usage that blocks renewal still blocks a renewal prompt;
quota eligibility requires PC-115's fresh reconciled complete accounting. Failed
or unavailable Telegram delivery remains honestly pending under bounded recovery,
independent of VPN access/refunds. Cancel obsolete reminders whose conditions no
longer hold rather than sending a stale warning after renewal/cancellation/expiry.

The rationale is consistent owner controls, useful advance prompts, and no spam
or lifetime-usage false alarms after carryover. The trade-off is no repeated
optional reminder within a paid period even if ignored, and no prompt while a
blocking restriction is unresolved. Exact notification bookkeeping, period/meter
representation, scheduler/retry algorithms, UI/storage, localization, and load
evidence remain planning/controlled-verification work; this selects no worker.

### Q-107 — Defer remaining optional personalization and service-editing flows

**Status:** answered; remaining optional launch boundaries accepted in PC-119.
**Prerequisites:** PC-003/PC-005/PC-008/PC-024-PC-039/PC-055-PC-064/
  PC-069-PC-075/PC-083-PC-091/PC-100-PC-118.
**References:** D07/D09/D10/D13/D14; A14/A19/A23/A24/A28-A31;
  F-008/F-039; constitution I-IV/VII.

Should launch defer the remaining optional personalization and generalized
service-editing/import flows, keeping changes to sold composites within the
already approved renewal, restriction, recovery, and replacement controls?

**REC-107 — accepted in PC-119:** Yes. Defer customer-selected service/configuration
names at checkout and later personal renaming, including both bot-only labels
and remote credential/email renames. Distinguish subscriptions in Telegram using
their preset name and a stable subscription identifier; preserve owner-defined
node remarks/order. Do not rename accounting or routing identities merely to
change a customer-facing label. Existing legacy naming remains supported.

Defer ad hoc owner editing of a sold composite's allowance/expiry, manual data/
time grants or resets, and arbitrary changes to its purchased node set/countries/
protocols/routes. Sold terms change only through accepted successful full renewal/
conversion and the expressly approved equivalent replacement/recovery policies,
with their gates and history preservation. Catalog/test presets for future
orders remain owner-configurable; future edits do not mutate sold snapshots.
Explicit usage-gap settlement and wallet support compensation stay supported,
but neither is a shortcut to a fresh bucket or a time/data grant.

Defer automatic or manual import/conversion of existing legacy subscriptions into
composites. Preserve their existing single-panel/stock-link behavior. A customer
can separately purchase a new offered composite; it must not consume, transfer,
or silently replace a legacy entitlement. The launch lacks prior VPN sales under
BC-001, but this does not authorize discarding existing legacy fixtures/data or
compatibility checks.

Keep all accepted paid/test/campaign fulfillment, discounts/coupons, renewal/
conversion, customer disable/resume/leak replacement/cancellation, owner single/
bulk controls/compensation, usage-gap handling, equivalent migration, protected
history/recovery, reminder, and truthful status flows. This question approves no
new history browser, arbitrary repair UI, product builder, or teardown feature.
Required existing customer/owner operation visibility and audit/support evidence
remain required rather than being deferred as an optional convenience.

The rationale is a clear launch management boundary that avoids hidden identity/
accounting changes and importing history whose semantics are not established.
The trade-off is fixed customer-facing names and fewer ad hoc owner corrections;
use approved renewal, recovery, compensation, cancellation, or a separate purchase
as appropriate, without inventing an exception. Future optional features need
their own explicitly reviewed behavior. No schema, identifier format, storage
design, worker architecture, or tasks are selected.

### Q-108 — Full invoice-payment wallet credit, including quoted charges at original conversion

**Status:** answered; invoice-inclusive original-conversion basis accepted in PC-120.
**Prerequisites:** PC-013/PC-037/PC-048/PC-051/PC-052/PC-073-PC-075/
  PC-092-PC-099/PC-107/PC-108/PC-119.
**References:** D07/D10/D13; A03-A06/A19/A25/A28/A30/A31;
  F-012/F-027/F-029/F-040; E-005; constitution I-III/VII.

Should existing full-refund/late-payment/extra-payment wallet credit cover the
verified invoice's entire customer-payable amount, including its quoted required
fees or matching offsets, using the original payment quote's conversion?

**REC-108 — accepted in PC-120:** Yes. Keep the accepted store-wallet destination and
existing refund/credit triggers, beneficiaries, deadlines, and repeat-safety.
For an eligible full refund, return the original actual wallet-funded portion
plus the wallet-equivalent value of the entire validly verified original external
invoice payment. Include its disclosed required matching offset, checkout/provider
charge, and native-unit conversion/rounding increment where included in the
accepted payment quote and verified payable amount. Do not limit reimbursement
to the base store amount if the required invoice payment was higher. The store
absorbs those quoted payment costs on its obligated full-refund path, even if a
provider retained the fee. A zero actual payment still creates no positive refund.

Illustrative wallet-unit example: a discounted store price of 100 is funded by
30 wallet units and an external invoice requiring 73 (70 store remainder plus
three quoted required charges). Eligible full refund credits 103 wallet units
once, not 100, and does not grant the nominal undiscounted price. A separately
verified second payment of 73 follows PC-099 as a distinct extra receipt; it
creates no second purchase and is not refunded again when the original fails.
Late verified external money after cancelled/rejected checkout follows the same
gross invoice-value basis without repeating already returned wallet funds.

Required charges disclosed in the one accepted invoice are part of its total
payment cost, not another subscription or an arbitrary mismatched overpayment.
They do not change selected allowance/duration, tier/coupon calculation basis,
test/campaign history, or fulfillment timers. This choice introduces no automatic
charge refund for a normally fulfilled purchase outside the already agreed
refund/credit triggers. Separate bank/wallet/network fees charged outside the
accepted invoice are not automatically reimbursed: they may be unobservable and
require discretionary owner support compensation, without estimating or inventing
them. Disclose total invoice cost and this boundary before payment.

Fix each accepted payment attempt's native currency/unit, required payable amount,
quoted charges, wallet-equivalent total, and applicable conversion/rounding terms
before it can authorize composite settlement. Refund/credit uses those original
verified terms, not later market rates or changed admin conversion settings.
Method-native invoice expiry still applies. A new permitted payment attempt may
quote then-current method conversion/charges for the same PC-098 retained store
offer, with its new total disclosed; do not silently reprice the base offer or
alter an already issued/paid attempt. Final store quote preservation does not
promise every future external invoice has the same native-currency cost.

Verify beneficiary, checkout/tenant/reference, exact accepted native payable
amount/currency, and original conversion evidence before settlement. Any permitted
provider unit rounding must be explicit in the quote and later plan; do not adopt
the source's blanket 99% acceptance, unbounded excess, missing/unparseable evidence,
or current-rate recomputation. Mismatch/unknown payment or fee evidence remains
visible for investigation/reconciliation, not fabricated gross value or silent
duplicate credit. Method support requires establishing these facts; source
presence/enabled configuration alone does not prove a method can safely fulfill
the composite contract. Preserve unaffected legacy payment behavior; no new
gateway, general wallet-unit change, original-method refund integration, or
approved constitutional exception is introduced.

The rationale is an understandable full-refund promise based on what the invoice
required the customer to pay and protection against exchange-rate changes during
recovery. The trade-off is store absorption of quoted payment charges and no
automatic coverage of separate unobserved external fees. Another option is base-
store-price-only credit with nonrefundable invoice fees, but that would narrow
the intended full-paid refund and needs explicit disclosure/approval. Specific
gateway evidence, method rounding/amount conversions, quote/ledger schema,
verification/reconciliation algorithms, and tasks remain planning/controlled
verification; actual fees/rates or safe method availability are not established.

### Q-109 — Confirm shared understanding and close the product interview

**Status:** not separately answered. USER-02 requested critical review instead;
  PC-121/PC-122 now resolve both resulting findings. Retained as the historical
  closure checkpoint; the current recommendation and stopping boundary are below.
**Prerequisites:** PC-001-PC-120; completed current-source consistency review.
**References:** USER-01; R01-R07; D01-D14; E-001-E-005;
  constitution I-VII; grilling skill's final shared-understanding requirement.

Are we aligned that the accepted decisions are sufficiently clear as input to
your later Spec Kit specify step, while the listed technical/evidence questions
remain unapproved designs or unverified results?

**REC-109 — unapproved:** Yes. Close this product interview after your explicit
confirmation. Preserve PC-001-PC-120 and the source documents as inputs, keep
E-001-E-005 and deferred planning questions visible, and stop so you can initiate
Spec Kit specify. This confirmation is about our shared understanding; it adds
no product policy, architecture choice, permission to implement, formal
specification/plan, release approval, or constitutional exception.

The review preceding this question found no material product contradiction or
remaining product choice blocking specification. RV-001 subsequently qualifies
that readiness conclusion without changing accepted decisions. Exact panel/client
versions and compatibility, payment
verification/conversion contracts, routing/meter behavior, and actual timing,
capacity, backup and recovery outcomes still require planned controlled evidence.
No scenario is marked passed, and daily client use is not treated as either a
demonstrated blocker or the required composite test evidence. Discovery of an
incompatible method or inability to meet an accepted behavior must trigger an
explicit revisit of that behavior, rather than silently weakening it.

The rationale is to carry the accepted product inputs into one later specification
without extending this interview into design. The trade-off is that specification
readiness does not establish implemented feasibility or release readiness.

### Q-110 — One open renewal checkout per subscription

**Status:** answered; one open renewal checkout per subscription accepted in PC-121.
**Prerequisites:** PC-024-PC-039/PC-054/PC-061/PC-094-PC-099/PC-105/PC-110;
  RV-001-A; F-041.
**References:** D09/D10; A03-A06/A15/A25/A28; constitution II/III/VII.

Should each composite subscription have at most one open renewal/conversion
checkout at a time, with repeated attempts returning to that existing checkout
or its progress instead of starting a second purchase?

**REC-110 — accepted in PC-121:** Yes. Apply this boundary per subscription, covering
an accepted renewal quote awaiting payment/manual review and a verified or
zero-price-authorized renewal still being fulfilled. A second attempt to renew
that same subscription returns to the existing checkout/status; it does not
create another order, deduct more wallet value, reserve another coupon use,
or solicit another renewal purchase. Other subscriptions and separate initial
purchases remain eligible under their own rules.

To select a different renewal plan while the existing checkout is still
unfunded, explicitly cancel that checkout under PC-094/PC-096 and begin a new
one at current offers/eligibility. An already verified renewal follows its
existing completion/failure/permanent-cancellation rules; changing one's mind
does not silently replace or cancel its purchased terms. After successful
completion, a later distinct early renewal remains allowed under the existing
carryover and 45-day rules. A failed/cancelled checkout cannot prevent another
eligible checkout merely because unrelated cleanup remains, but unresolved
effects affecting this subscription's entitlement/accounting must still satisfy
the existing verification and reconciliation gates before new payment.

Multiple permitted payment attempts against the one retained checkout remain
allowed under PC-098; they are not multiple renewal orders. Late or distinct
extra valid payments continue under PC-094/PC-099/PC-120, without another
fulfillment or duplicate wallet credit. Invoice expiry does not add a new
checkout expiry timer. This recommendation does not turn an unpaid quote into
a new restriction on customer disable, leak protection, or cancellation, and
does not choose locks, queues, schemas, or worker ordering.

The rationale is to prevent accidental double purchases and competing carryover
calculations for one subscription, while keeping an understandable pending
checkout. The trade-off is that customers must finish or cancel the existing
eligible checkout before choosing another renewal offer; distinct simultaneous
renewal orders for one subscription would not be supported at launch.

### Q-111 — Reject a retained checkout that has no permitted funding path

**Status:** answered; unpayable-checkout rejection and valid-attempt protection accepted in PC-122.
**Prerequisites:** PC-092-PC-099/PC-105/PC-110/PC-120/PC-121;
  RV-001-B; F-042.
**References:** D07/D09/D10; A03-A06/A19/A25/A28;
  constitution II/III/VII.

If a configuration or payment restriction change leaves an unverified checkout
with no permitted way to complete its payment, should the store reject that
checkout and release its wallet/coupon holds automatically?

**REC-111 — accepted in PC-122:** Yes, once the absence of a permitted funding path is
established. Apply this to initial purchase, renewal and trial-conversion
checkouts not yet fully payment-verified or zero-price-authorized. Explain the
payment-unavailability reason, terminally reject the checkout, restore any actual
wallet contribution once, and release its held coupon use once. Under normal
application/database conditions, restored wallet value is visible and spendable
within 60 seconds of rejection. Do not automatically increase the wallet debit,
require a top-up, change the accepted plan/price, or invent another funding method
to keep an otherwise unpayable checkout alive.

Example: a 100-unit checkout has used 30 wallet units and still requires 70.
If no permitted option or valid existing payment attempt remains for that 70,
reject it, return the 30 once and release its coupon. A later new checkout uses
current offers/eligibility; the rejected checkout no longer preserves its old
price or coupon reservation. Other payable checkouts remain unaffected, and
rejection of a renewal does not cancel or alter the existing subscription.

An already issued payment attempt that remains valid, authorized and safely
verifiable counts as an existing funding path, including a legitimate manual
payment awaiting owner review. Disabling a method for new invoices alone must
not silently invalidate such an existing attempt. A temporary gateway outage,
uncertain verification, or ordinary invoice expiry alone is not established
loss of every permitted funding path. Preserve the pending quote when a
permitted path remains; no general unpaid-order or manual-receipt expiry timer
is added. Payment restrictions and verification cannot be bypassed by calling
an invalid or unauthorized attempt a remaining path.

If valid external money is verified after rejection, credit its complete
original quoted wallet-equivalent value once under PC-094/PC-099/PC-120;
do not reopen the order, provision/renew, or repeat the restored wallet portion.
Already fully verified/zero-price-authorized orders retain their original
fulfillment deadlines and success/failure rules rather than being retrospectively
rejected by a payment-setting change. Unknown/mismatched money remains visible
for verification/reconciliation without invented credit or discarded evidence.

The rationale is to release money and limited coupon capacity when the store
can no longer accept the checkout's payment. The trade-off is losing that
checkout's old price/promotion guarantee after rejection; preserving the offer
while changing or releasing only its funding would require another explicit
funding treatment. Detection/coordination, exact method-validity evidence,
storage, and algorithms remain planning work. The user's explicit answer is
recorded in PC-122; no additional design or evidence is approved by that answer.

## Interview outcome and next-step boundary

The known product-question frontier is empty following PC-121 and PC-122.
RV-001-A/B are resolved, and the final consistency check found no remaining
product blocker or new constitutional conflict. The reviewer now recommends
closing the product interview. This is an assessment of specification readiness,
not a claim that every possible future edge case has been anticipated.

Under USER-01's instruction to finish when the product decisions are sufficiently
clear for specification, interview work stops here. The user's Q-111 answer
approves PC-122; it is not recorded as a separate answer to Q-109 or as permission
to generate a formal specification, plan, tasks, or implementation. The user
initiates the later Spec Kit specify step. No further product question is pending.

Use PC-001-PC-122, the branch/readiness indexes, and the preserved reference
documents as inputs to that one specification. E-001-E-005 remain unverified;
schemas, algorithms, worker design and other technical questions remain planning
work. If later evidence requires changing an accepted product promise, expose
the concrete conflict and seek its explicit resolution. No constitutional
exception or passing acceptance result is inferred from interview completion.

## Critical review requested after Q-109

### RV-001 — Review Q-080-Q-109 before accepting closure

- **Requested:** 2026-10-02, USER-02. The request does not answer Q-109.
- **Evidence:** Read Q-080-Q-109 in full, the corresponding PC-092-PC-120 and
  relevant earlier accepted policies, constitution and reference documents;
  rechecked current payment/renewal source at the recorded HEAD. A read-only
  fact audit checked payment assumptions independently. No runtime data or
  live service was used. This review does not claim access to missing historical
  assistant wording beyond the persisted question/decision record.
- **Overall assessment:** The questions largely address the same consequential
  issues a focused interview should cover. Q-080-Q-087/Q-108 resolve genuine
  payment and refund boundaries; Q-088-Q-094 define issuance, authority and export
  behavior; Q-095-Q-104 cover outages, recovery and observable timing; Q-105-Q-107
  establish optional-feature boundaries. No material contradiction with the
  confirmed scope or constitution was identified in those accepted answers.
- **Interview quality:** Some recommendations are longer and contain more
  dependent clauses than necessary. The sequence could have been consolidated
  around common principles, with each concrete business consequence kept
  reviewable. Recovery objectives are valid product targets, but their conditional
  start points and unverified feasibility must stay explicit. This criticism
  does not revoke accepted decisions or imply every timing/correctness detail
  needed another user question.
- **Previously accepted trade-off to retain:** Q-086 deliberately allows old
  prices and held coupon/wallet value to remain attached to unpaid quotes without
  a general expiry timer. That can require owner cleanup of abandoned requests.
  A bounded quote window would have been another reasonable recommendation,
  but preference alone is not a reason to reopen the explicit accepted choice.
  RV-001-B concerns a different consequence: loss of every permitted funding path.
- **RV-001-A — Overlapping renewal checkouts, resolved by PC-121:** PC-054's one
  subscription per checkout and PC-099's duplicate/extra payment rules do not
  choose whether two distinct renewal checkouts may target the same subscription
  before the first finishes. The existing source permits distinct pending orders
  and protects claims per order, not per renewal target (F-041). PC-035/PC-105/
  PC-110 block particular conditions; they do not establish a general one-open-
  renewal policy. Whether to take a second payment, reopen the first checkout,
  or refuse a second purchase is customer-visible and affects carryover,
  45-day forfeiture, coupons and cancellation. Q-110 subsequently resolved this
  choice as one open renewal checkout per subscription; PC-121 records acceptance.
- **Overlap follow-through:** Existing cancellation, owner/customer restriction,
  leak-revocation and migration rules must govern overlapping work in the later
  specification. A generic technical busy state cannot silently refuse a
  promised protective action, clear a newer restriction, or admit competing
  purchases. The implementation coordination belongs in planning; if a remaining
  customer-visible priority cannot be derived from accepted rules, expose that
  precise choice rather than inventing it. This is not approval of a new
  priority matrix or a request to interview every possible event ordering.
- **RV-001-B — Retained quote loses a permitted payment path, resolved by PC-122:**
  PC-092 prohibits stranding wallet funds for an unpayable remainder; PC-098
  retains an accepted quote/holds until completion, cancellation or rejection
  while keeping current method availability applicable. Example: an accepted
  100-unit quote has used 30 wallet units, then no permitted payment option can
  cover the remaining 70 after a configuration/minimum change (F-042). At review
  it was unclear whether this causes terminal rejection and releases wallet/coupon
  holds, or preserves the offer through another explicitly defined funding
  treatment. The already agreed no-stranded-wallet boundary must be preserved.
  This is not ordinary invoice expiry, an automatic unpaid-order TTL, or proof
  that a temporary provider outage makes a checkout permanently unpayable.
  Treatment of already issued still-valid attempts must remain explicit.
  Q-111 subsequently resolved this as automatic rejection with wallet/coupon
  release only once no permitted path remains, protecting valid existing
  attempts and already verified orders. PC-122 records the accepted conditions.
- **Not additional product blockers:** Exact panel/client versions, supported
  payment verification/conversion, routing, measured cutoff/overshoot, backup/
  restore performance and supported load remain E-001-E-005 planning/controlled
  evidence. The 150-subscription replacement benchmark is not an active-session
  capacity guarantee. Unsafe legacy receipt matching, amount reuse, and gateway
  finalization are implementation/evidence risks already constrained by the
  accepted verification/late-credit policies, not reasons to reopen those policies.
- **Closure recommendation:** RV-001-A/B are resolved by PC-121/PC-122. The
  final check supports closing product clarification as input to specify, with
  no further identified product blocker. PC-001-PC-122 are accepted; Q-109 was
  not separately answered and does not authorize downstream work. The two new
  decisions follow explicit answers, not an inference from the review request.

## Product branch review

This is an interview map, not a task breakdown. RV-001-A/B are resolved by
PC-121/PC-122. No product question is pending; remaining design/evidence work
is identified separately for the later Spec Kit workflow.

| Branch | Settled scope and consequential remaining choices | References |
|---|---|---|
| Participants, channels, and issuance | Main-store Telegram sales, owner web-admin operations, preset plans, buyer eligibility, discounts, reward exclusions, and one subscription per checkout are settled (PC-006-PC-010/PC-050-PC-054). Composite tests/campaign, eligibility, conversion, and editable standard defaults are settled (PC-055-PC-064). Test activation/presentation follows PC-055's existing `btn_test` logic under F-017/F-018, with owner-only composite plan management. Existing configured methods/manual payment authority are settled by PC-092/PC-093. Ad hoc grants, gifting/reassignment, personal names, and legacy import are deferred by PC-100/PC-101/PC-119. No further channel/issuance assumption is being sought. | D07/D10; A03/A19/A27/A28 |
| Fulfillment and money | Complete-plan delivery, activation, 15-minute paid/test deadlines, failed-payment wallet refunds, and 60-second normal wallet-credit availability are settled (PC-011-PC-016/PC-037/PC-048/PC-049/PC-057-PC-059). Voluntary cancellation and in-flight-renewal refunds are settled (PC-068/PC-072-PC-075). Cancellation/late payments, coupon restoration, zero-price orders, quote preservation, and distinct extra-payment credit are settled by PC-094-PC-099; financial catch-up/stale-restore holds by PC-107/PC-108. PC-120 settles full quoted invoice-value credit at original conversion, including required quoted charges while excluding separate outside fees from automatic coverage. PC-122 resolves RV-001-B: reject an unverified checkout once no permitted funding path remains, release wallet/coupon holds, preserve valid existing attempts, and credit later verified money without reopening it. Actual method evidence remains unverified. | D10; A03-A06/A25/A28 |
| Validity and renewal | Monthly duration, carryover, the 45-day cap, matching-plan choices, no automatic renewal, overrun treatment, identity continuity, and trial conversion are settled (PC-023-PC-039/PC-061). Owner suspension's new/unfunded/already-verified renewal boundary is settled by PC-105. New renewal funding during migration and matching presets after an explicit equivalent move are settled by PC-110. PC-111 includes inactive fulfilled histories in equivalent replacement while preserving entitlement and restrictions. PC-121 settles RV-001-A as one open renewal/conversion checkout per subscription, with repeated attempts returning to that checkout/status. | D03/D09; A12/A15/A25 |
| Usage and uncertainty | Units, meter attribution, five-minute grace, whole-subscription suspension, best-effort outage cutoff, normal 60-second enforcement, native existing-session behavior, automatic reconciled recovery, and owner usage-gap settlement are settled (PC-004/PC-015-PC-022/PC-034/PC-084). PC-087 explicitly qualifies retired-server metering during emergency cutover. PC-107 covers intact-history manager outage/restart without new clocks or late fulfillment; PC-113 adds prepared-host recovery timing. PC-114 covers unexpected direct panel edits/identity loss; PC-115 sets normal usage/display freshness; PC-116 sets automatic resumption timing. Remaining feasibility is evidence; counter/rounding mechanisms belong to planning unless they change a visible promise. | D02/D03/D08; A07-A16; S05-S07 |
| Customer and owner management | Customer replacement/cooldown, owner override, trial parity, disable/resume, cancellation, and single/bulk wallet compensation are settled (PC-040-PC-047/PC-065-PC-075). Ownership reassignment is deferred by PC-101. Owner single/bulk restrictions/cancellation are settled by PC-102, account-block separation by PC-103, and owner-suspension exports/funding by PC-104/PC-105. PC-119 defers personal naming, ad hoc sold-entitlement/topology editing, and legacy import while retaining approved controls. Interrupted bulk compensation requires repeat-safe recovery under the constitution; mechanics remain planning. | D10/D14; A14-A19/A24/A29/A32 |
| Subscription delivery | Base64-only export, informational rows, timestamped uncertain usage, five required client apps, and outage/inactive downloads are settled (PC-076-PC-082). Status-only owner-suspension downloads and one faithful real export per configured node are settled by PC-104/PC-106; fresh-versus-delayed usage is settled by PC-115. PC-117/PC-118 settle paid reminders and their thresholds/repeat/eligibility. Same-URL continuity across equivalent replacement/prepared-host recovery follows PC-086/PC-113; optional bot/UI independence follows PC-005. Exact public HTTPS/domain/deployment prerequisites and real-client information-row behavior remain planning/evidence, not new hosting architecture approvals. | D05/D11; A20-A22/A32; S04/S07 |
| Server replacement and recovery | Owner-prepared infrastructure, A-only/five-choice initial deployment, equivalent replacement, emergency cutover, fresh moved credentials, bulk per-subscription outcomes, the 15-minute/150-subscription benchmark, and customer refresh notices are settled (PC-083/PC-085-PC-091). Broader topology editing is not approved. Missing-history stale-restore holds and destructive-operation guards are settled by PC-108/PC-109. Catalog/new-order and renewal behavior during replacement is settled by PC-110; PC-111 covers inactive fulfilled histories without activation or terminal revival. PC-112 sets the normal fifteen-minute recoverable local-history objective; PC-113 sets four-hour conditional recovery on prepared infrastructure. Actual results/prerequisites remain evidence, not product approvals to guess. | D04/D08/D13/D14; A24/A29-A31; S03/S09/S11/S13 |
| Acceptance and non-goals | Existing compatibility and the multi-panel fixture remain required despite initial live A-only deployment. PC-112/PC-113 define recovery-point/time targets without verified performance; PC-119 closes remaining optional management/import scope. Exact client/panel/payment method evidence and supported load remain planning/controlled verification, not approvals to guess. PC-121/PC-122 resolve both RV-001 findings; no further product blocker is identified. Interview work concludes under USER-01's stopping condition, with specify initiated by the user. Architecture and execution of tests remain outside this interview. | D01/D05/D13; A01-A33/S01-S13 as applicable |

The table summarizes the current frontier; accepted PCs remain the detailed source
of each answer. It does not reopen settled customer test management, compensation,
formats, client coverage, or download policies. Historical "Not settled" fields
remain scoped to the time of the individual answer. No new choice is approved by
being listed here; questions requiring evidence remain distinct from product choices.

## Current repository facts, not product approvals

Static source inspection only, at the current revision above. No application
imports, services, live calls, runtime databases, secrets, or feature tests were used.

- **F-001:** `custom_configs` currently records one panel server, username, and
  upstream subscription URL per managed service (`database.py:1043`). The 3x-UI
  provider creates one identity over its configured inbound list
  (`panel_providers/threexui_provider.py:167`). This is not the proposed set of
  independently managed multi-panel child credentials.
- **F-002:** 3x-UI creation converts volume with `1024 ** 3`, enables the identity
  immediately, and derives expiry from each call's current time
  (`panel_providers/threexui_provider.py:141`). Composite units and activation are
  selected separately in PC-015/PC-014; existing immediate enablement and per-call
  expiry are not thereby approved. References: D03; independent review
  architectural challenge 2.
- **F-003:** Manual full renewal passes `preserve_remaining=True` and reads back
  the remote limit (`renewal_engine.py:39`); automatic renewal requests a usage
  reset without carryover (`renewal_reminders.py:261`). The 3x-UI carryover path
  substitutes zero after a usage error, and its reset response is unchecked
  (`panel_providers/threexui_provider.py:327`). This confirms the relevant U01
  source risks; none is an approved composite policy.
- **F-004:** Missing traffic objects can currently yield zero usage; deletion
  returns success based on HTTP status alone
  (`panel_providers/threexui_provider.py:195`, `:207`). These must not be adopted
  as composite accounting or revocation acceptance semantics (constitution II/VII).
- **F-005:** Reminder/connection-alert jobs start inside bot startup
  (`bot_manager.py:276`); reconciliation excludes tenants with `has_live_bot=0`
  (`bot_manager.py:419`). This supports the U03 tenant-coverage concern if those
  tenants are approved for composite sales; it does not choose a worker design.
- **F-006:** Factory reset clears service, panel, order, and owner-related shop
  data (`database.py:1314`). The current table list is not an approved composite
  reset policy. References: U04; constitution IV.
- **F-007:** Ordinary catalog purchases exist in Telegram and Mini App and branch
  between stock links, direct-panel supply, and reseller auto-provisioning
  (`handlers_user.py:1086`, `miniapp/server.py:1698`). Reseller models include
  commission, discount purchasing, fixed-product inventory, and volume credit
  (`database.py:1652`). Reseller actor, tenant/storefront, and interface are
  distinct dimensions; excluding one does not automatically exclude the others.
- **F-008:** Custom builders, trials, referral gifts, and reseller web self-service
  are separate entry points (`handlers_user.py:1604`, `:2204`, `:524`;
  `admin_panel/server.py:2732`). Customer management already includes toggle,
  rename, automatic renewal, transfer, history, credential replacement, and
  renewal (`miniapp/server.py:628`, `:662`). Their existence does not approve
  their composite equivalents. Web/mobile clients also share administrative
  endpoints (`admin_panel/server.py:585`). References: D07/D09/D10/D14; U06.
- **F-009:** Existing reseller capability checks differ: dedicated reseller
  tenants can receive full-access treatment in `database.py:2361`, while the
  web product-creation route rejects direct-panel/stock products for reseller
  tenants (`admin_panel/server.py:2988`). Initial scope must be explicit rather
  than assuming existing interface parity. This is source evidence, not a
  proposed unrelated reseller-policy change.
- **F-010:** Narrow searches of current Python source for composite/bundle/
  multi-panel terms found no composite implementation, and inspected provisioning
  paths remain single-panel. This finding is bounded to the inspected source;
  it does not assert anything about deployed or external components.
- **F-011:** Existing web administration has product, panel, and managed-service
  routes (`admin_panel/server.py:2980`, `:4749`, `:2453`, `:2528`), and Telegram
  administration has product and panel setup handlers (`handlers_admin.py:649`,
  `:1048`, `:4345`). Both are candidate existing interfaces to extend; neither
  currently establishes approved composite operator behavior. Shared web/mobile
  authentication noted in F-008 does not itself approve native-mobile feature scope.
- **F-012:** The current rejection helper restores only `wallet_used` and releases
  discount-code usage for pending orders (`database.py:3470`); it does not refund
  the externally paid portion. Inspected verified-payment provisioning failures
  release the order for support/retry without initiating an external refund
  (`abangateway_payment.py:230`, `blupal_payment.py:230`, `noapay_payment.py:262`).
  Manual web rejection calls that same wallet-only helper
  (`admin_panel/server.py:2241`). No original-method refund initiation was found
  in those inspected paths; a remote `refunded` status classification is not
  initiation (`extra_gateway_clients.py:249`). This does not establish that
  payment providers lack refund APIs or that an owner cannot refund elsewhere.
  Both full-wallet compensation and original-source external refunds would
  require additional composite behavior; neither is an existing complete policy.

- **F-013:** Current 3x-UI creation supplies a UUID value in both `id` and
  `password` fields (`panel_providers/threexui_provider.py:141`). Its existing
  `revoke_credentials` method changes `id`, `password`, and `subId` across the
  found inbound attachments for one username, copying other client fields
  (`panel_providers/threexui_provider.py:382`). This supports distinguishing
  protocol UUIDs from password credentials; it does not prove composite-wide
  replacement, remote cutoff, counter continuity, or failure recovery. Its shared
  identity across a legacy username's attachments is not approval to collapse
  the independent composite identities required by PC-001.

- **F-014:** Current ordinary Telegram catalog checkout does not exclude a buyer
  solely for reseller/discount status in the inspected handlers and `_buy_start`
  (`handlers_user.py:577`, `:621`, `:1038`). `_buy_start` asks for tier pricing
  and uses the buyer's monetary wallet when allowed by product payment methods
  (`handlers_user.py:1072`); it does not use that buyer's reseller GB credit or
  fixed-product inventory as the payment balance in this path. The pricing helper
  applies an automatic discount only when the user's assigned reseller tier is
  enabled and its model is `discount` (`database.py:1839`). It uses the maximum
  of user-specific, tier-permanent, and qualifying quantity percentages, not
  their sum, with integer-floor discount arithmetic. Mere reseller status or a
  different tier model does not trigger that helper's discount. `_buy_start`
  separately subtracts any discount-code amount from the tier-adjusted total.
  These are current-source facts, not approved composite pricing or evidence of
  complete settlement safety. Reseller selling/supply and commission flows remain
  distinct scope questions.

- **F-015:** Ordinary checkout's discount-code path supports activity, usage,
  expiry, product/category, and purchase-amount restrictions, with percentage
  flooring and fixed/percentage amounts capped at the supplied price
  (`database.py:4572`). However, manually entered code amounts are cached and
  final `_buy_start` reads that amount without revalidating the code there
  (`handlers_user.py:660`, `:1068`); current source is not proof of fresh
  settlement validation. Commission is separate from buyer discounts: an
  `owner_reseller_id` relationship can credit the referring reseller's money
  wallet (`database.py:4248`, `:4370`). The ordinary wallet-complete purchase
  passes `order["base_price"]` to that reward hook (`handlers_user.py:1151`),
  representing a tier-adjusted amount before coupon deductions in this path.
  Neither that commission basis nor cached-code settlement behavior is approved
  for composites. General blocked-user/membership checks also remain applicable
  (`bot_manager.py:222`, `blocked_user.py:52`); reseller status is no exemption.

- **F-016:** The inspected Telegram full-plan renewal starts from the selected
  product's current price (`handlers_user.py:3658`) and does not use the ordinary
  initial-purchase tier helper or a coupon-entry/application path. Instead it can
  apply a separately configured early-full-renewal percentage to a managed custom
  service when its locally stored expiry falls within the configured remaining-day
  window (`handlers_user.py:3670`), using `round` on the reduced price. Renewal
  order creation has no tier/coupon arguments (`database.py:3362`). Thus matching
  PC-051 for composites is a new product choice. Renewal checkout also uses the
  monetary wallet and globally enabled payment methods without the selected
  product's payment allowlist in the inspected path (`handlers_user.py:3472`,
  `:3500`; `keyboards.py:646`). Inspected renewal completion branches do not call
  the ordinary purchase reward hook (`handlers_user.py:3483`,
  `handlers_admin.py:1796`, `abangateway_payment.py:186`,
  `miniapp/server.py:3053`). These are bounded source observations, not approval
  of composite discounts, payment restrictions, or rewards and not runtime proof.

- **F-017:** Current source sets `MAX_TEST_PER_USER = 1` (`config.py:78`).
  The Telegram test entry checks `test_enabled` and the user's shared `test_used`,
  automatically selects a sole active test plan, or offers a picker for several
  (`handlers_user.py:2203`). `_deliver_test_plan` reserves the user's allowance
  before provisioning and releases it for caught provisioning errors
  (`handlers_user.py:2249`). The reservation updates the user's shared count,
  without a plan dimension (`database.py:2266`); release decrements it
  (`database.py:2291`). Multiple test plans already exist and their current
  definition has one panel, volume and duration (`database.py:3239`, `:3258`).
  This is intended-flow evidence, not proof of composite compatibility or complete
  failure safety. The multi-plan callback passes `call.message` to a helper that
  reads `message.from_user.id` (`handlers_user.py:2288`); the affected identity
  path requires characterization and authenticated-customer attribution under
  constitution III, not copying an unverified callback sender assumption. General
  test usage reset exists (`database.py:2300`); that does not establish what a
  future capped campaign should do on reset. No runtime settings/data were read.

- **F-018:** Multiple test-plan administration is present in Telegram
  (`handlers_admin.py:1446`; `keyboards.py:1888`) and web settings
  (`admin_panel/server.py:5633`); existing broad settings permission is not an
  override of PC-009's composite owner-only policy. No aggregate campaign cap or
  automatic cap-based closure was found in inspected plan fields, CRUD, and claim
  handlers. The shared per-user quota is scoped to the current store database,
  not proven unique across stores (`database.py:2266`; `miniapp/server.py:165`).
  Ordinary admin reset clears positive test usage, permitting another test
  (`database.py:2302`; `handlers_admin.py:4904`; `admin_panel/server.py:5601`),
  so the current counter alone is not a distinct lifetime campaign-recipient
  count. With no active plans, the full-access Telegram path can fall back to
  the legacy manual test bank (`handlers_user.py:2219`); closing one campaign
  is not disabling the entire test feature. Legacy test provisioning also
  suppresses errors when saving the created service locally before returning
  its URL (`test_config_provision.py:56`); that is not evidence of durable
  fulfillment and must not be copied as approved composite recovery behavior.
  All findings are static and bounded to inspected paths.

- **F-019:** Existing test provisioning divides `volume_mb` by 1024 and
  `duration_hours` by 24 before calling the provider (`test_config_provision.py:35`).
  The 3x-UI provider multiplies that volume by 1024 cubed to produce bytes and
  the duration by 86,400 to produce an immediate expiry
  (`panel_providers/threexui_provider.py:151`). Therefore 200 in the existing MB
  field produces 209,715,200 bytes in this path, despite the MB-style label.
  Current web test-plan inputs require integer `duration_hours`
  (`admin_panel/server.py:5583`) and positive duration (`:5644`); Telegram test
  duration entry/edit also uses integer hours (`handlers_admin.py:1507`, `:1632`).
  These inputs do not express the new ten-minute default. Static arithmetic is
  not proof of panel behavior or a choice of composite duration representation;
  immediate creation-time expiry is not PC-058's availability-based activation.

- **F-020:** The Telegram managed-service toggle resolves an owned service,
  requires custom-service kind and the enabled `svc_show_toggle` setting, and
  explicitly rejects tests (`handlers_user.py:3206`). It calls provider
  `set_enabled`, then updates local enabled state and records history; this
  path neither adjusts expiry nor resets quota. The 3x-UI implementation copies
  each client's fields and changes only `enable`
  (`panel_providers/threexui_provider.py:416`). This is access enable/disable,
  not a validity-clock pause. It does not establish safe composite restoration
  eligibility, distributed completion, or native active-session termination.
  Current exclusion of tests is a legacy fact, not approval or prohibition of
  the composite-test control accepted in PC-066.

- **F-021:** The inspected Telegram customer deletion flow offers an irreversible
  removal confirmation (`handlers_user.py:3030`). For managed services it resolves
  the customer's own record, attempts provider deletion, and then removes the
  local record even when the remote attempt raises an exception
  (`handlers_user.py:3065`). No prorated refund or wallet-credit call appears in
  this handler. This is bounded source evidence, not a claim that every refund
  entry point has been inspected. It is also not approval to copy local removal
  after uncertain remote deletion into composites; constitution II/IV and PC-005
  require durable cleanup responsibility and honest pending/completed status.
  The owned-service deletion helper can hide the parent order from the customer
  after its last service is removed, retaining it for admin reporting without
  changing it to refunded or crediting the wallet (`database.py:3560`). Pending
  checkout cancellation is separate and calls the wallet-portion-only rejection
  helper (`handlers_user.py:1339`; `database.py:3470`). Web admin deletion likewise
  has no automatic unused-service refund (`admin_panel/server.py:2674`); generic
  wallet adjustment is a separate explicit amount operation (`:2423`). None of
  these facts approves a composite cancellation or manual-compensation policy.

- **F-022:** Current 3x-UI creation returns the panel subscription URL
  (`panel_providers/threexui_provider.py:192`). The individual-link helper reads
  raw/Base64 URI text and extracts supported URIs from some Xray/sing-box JSON
  (`sub_info.py:253`, `:297`). Input parsing is not evidence of a complete
  composite Clash or sing-box exporter. A hardcoded client User-Agent in this
  helper is not a tested compatibility matrix. R05's named client targets remain
  confirmed, while D05 and the explicit format scope notes still require a user
  decision on initial formats; A21/A22/S04 are desired, unexecuted verification.

- **F-023:** Bounded tracked-source searches found no existing generator for the
  requested informational/fake configuration rows. After Base64 decoding, the
  individual-link parser accepts every nonempty line beginning with a recognized
  URI scheme without distinguishing informational rows or checking connectivity
  (`sub_info.py:32`, `:335`); delivery describes extracted links as importable
  configurations (`config_delivery.py:96`). Metadata is consumed separately:
  `fetch_sub_info` reads `subscription-userinfo` and `profile-title`
  (`sub_info.py:352`), but not a usage-sample timestamp/freshness indicator.
  Missing individual usage fields default to zero and absent expiry/zero total
  can be displayed as unlimited (`sub_info.py:363`, `:393`). These legacy fallbacks
  are not approved composite accounting. Neither URI extraction nor metadata
  parsing establishes the requested presentation or safe client auto-selection.

- **F-024:** Read-only current-source inspection for D04 found that ordinary
  direct provisioning selects one panel and calls `create_user(username, volume,
  duration)` (`direct_panel_provision.py:47`, `:98`). The 3x-UI provider reads
  configured existing inbound IDs and sends the client identity/quota/expiry
  payload to them (`panel_providers/threexui_provider.py:125`). No outbound-selection
  parameter or shared routing-rule mutation appears in this inspected path.
  Bounded tracked-source search found outbound parsing in subscription utilities,
  not a shared 3x-UI routing/outbound manager. This does not prove per-child country
  routing support or select D04's ownership policy. REQUIREMENTS explicitly leaves
  modification, verification, and administrator-applied generation alternatives
  open (`REQUIREMENTS.md:76`). Correct intended egress remains required under
  S03, independently of who prepares the shared infrastructure.

- **F-025:** The current 3x-UI `get_user_usage` returns current `up + down`,
  allowance, and enabled status without a historical sample or counter epoch
  (`panel_providers/threexui_provider.py:207`). It does not compare a lower
  returned value with retained confirmed usage. HTTP/network errors raise, but
  an HTTP-200 application failure or absent traffic object/counters can default
  to zero (`:210`). Existing renewal may also substitute zero after a lookup
  failure (`:330`) and sends unchecked reset requests (`:372`). These patterns
  are not approved composite behavior. The inspected provider cannot reconstruct
  usage erased between a last trustworthy reading and an external reset from
  post-reset totals alone. Whether independent retained panel/core history can
  recover that interval is an unverified deployment capability; no live evidence
  was accessed. A09-A11 and constitution II require retained confirmed usage and
  explicit uncertainty, not automatic replenishment or invented exact totals.

- **F-026:** Editing a panel record updates its API address, selected inbound IDs,
  and subscription base URL locally (`admin_panel/server.py:4903`,
  `database.py:6792`). Existing service lookups resolve that referenced record
  (`handlers_user.py:2804`); the update does not import clients or migrate usage.
  Ordinary 3x-UI creation generates new credentials/subId and derives expiry from
  current time plus duration (`panel_providers/threexui_provider.py:150`). Its
  delivered subscription URL comes from `xui_sub_base_url` plus `subId` (`:192`),
  distinct from `api_url` (`:77`), but not evidence of a stable composite endpoint.
  Direct provisioning stores the ordinary service result (`direct_panel_provision.py:118`),
  not a demonstrated composite migration/history contract. An inbound ID is
  panel-scoped; equal numeric IDs do not establish equivalent protocol/security,
  routing, or identity settings. These static facts support treating the requested
  server replacement as required new behavior, not an existing address-edit feature.

- **F-027:** Initial Telegram checkout uses wallet credit up to the discounted
  price when the selected product permits wallet (`handlers_user.py:1072`),
  fulfills directly when fully covered (`:1114`), and offers external payment
  for the remainder (`:1223`). Nullable product allowlists are read through
  `database.py:5745`; menu filtering applies enabled status, allowed methods,
  and configured minimum amounts (`keyboards.py:664`). Initial callbacks also
  use a product/minimum-amount helper (`handlers_user.py:138`); if no external
  method can pay the remainder, the order is rejected and its wallet deduction
  returned (`:1186`). Supported source routes include manual/automatic card
  transfer, Plisio crypto, AbanGateway, BluPal, NoaPay, configured custom gateways,
  and main-bot extra gateways (`extra_gateway_registry.py:4`,
  `extra_gateway_payment.py:66`): Zarinpal, AqayePardakht, Tetra98, CubePay,
  NOWPayments, and Telegram Stars. No runtime gateway availability was inspected.
  Legacy renewal automatically uses wallet and offers globally enabled methods
  without the selected preset's allowlist (`handlers_user.py:3472`), and its
  order uses `product_id=0` (`database.py:3373`). These are source facts, not
  approval of all methods, verification safety, or restriction bypass for composites.
  PC-013/PC-051/PC-052 leave payment eligibility open, while PC-010 separately
  leaves manual payment-approval interfaces unresolved.

- **F-028:** Current initial/renewal receipt handlers accept photo/document
  evidence and notify admins (`handlers_user.py:1559`, `:3918`), using shared
  approve/reject buttons (`keyboards.py:799`). Telegram order callbacks use
  `admin_only` (`handlers_admin.py:1776`, `:1976`), which checks membership in
  the admins table rather than the owner role (`database.py:2357`, `:2398`).
  Web order approval/rejection use the `orders` permission
  (`admin_panel/server.py:2124`, `:2241`, `:661`), also permitting authorized
  non-owner staff. Both paths claim a pending order (`database.py:3413`) and
  contain audit calls (`handlers_admin.py:1804`, `:1996`;
  `admin_panel/server.py:2142`; `database.py:2742`). They combine approval and
  fulfillment; these static guards/audits do not prove composite repeat-safe
  settlement or separate confirmation/provisioning outcomes. Owner-only composite
  payment decisions through both interfaces would be a new scoped policy, not
  removal of existing legacy staff rights or a general wallet-top-up change.

- **F-029:** Telegram `cancel_flow` rejects an order only while its stored status
  is pending and then clears the conversation (`handlers_user.py:1339`). It
  depends on the conversation's `order_id` and displays cancellation even if
  the order is no longer pending and no rejection occurred; this is not an
  approved durable composite cancellation control. The
  rejection helper conditionally changes pending to rejected and subsequently
  restores `wallet_used` and decrements coupon usage (`database.py:3470`);
  these separate steps are not proof of crash-safe financial recovery. In the
  inspected AbanGateway path, invoice verification may set the invoice completed
  before order finalization (`abangateway_payment.py:125`). Its finalizer returns
  an already-reviewed/delivered message for any non-pending order (`:181`), with
  no late-payment wallet credit in that branch. The inspected BluPal finalizer
  has the same non-pending return (`blupal_payment.py:181`). This is bounded
  evidence of a late-paid cancelled-order risk, not a claim about every gateway
  or approval of its handling for composites. Invoice/payment verification and
  actual fulfillment must remain distinct under constitution II/VII.

- **F-030:** Current initial Telegram checkout caps coupon reductions at the
  tier-adjusted price (`database.py:4613`) and permits a configured 100% tier
  discount (`:1793`, `:1839`). It computes nonnegative post-discount price and
  draws wallet funds only up to that amount (`handlers_user.py:1075`). The stored
  `final_price` is remaining external payment after both discount and wallet
  deduction (`database.py:3299`): zero therefore covers both a truly zero-cost
  order and a positive-price order fully wallet-funded. The `final_price <= 0`
  initial branch provisions/allocates, approves, and delivers without external
  payment/manual approval (`handlers_user.py:1114`, `:1163`); handled failure
  rejects and invokes wallet/coupon restoration (`database.py:3470`). This is
  static initial-purchase evidence, not composite approval, renewal coupon parity,
  or proof of safe zero-price issuance across crashes/concurrent confirmations.

- **F-031:** Initial orders store quoted base price, discount ID/value, wallet
  contribution, and remaining amount (`database.py:3299`); renewal orders store
  quoted price, wallet contribution, volume, and days (`:3362`) without current
  legacy renewal coupon fields. Representative payment creation uses the stored
  remaining amount (`handlers_user.py:1383`, `:3766`), and manual approval does
  not reprice/revalidate coupons (`handlers_admin.py:1785`). Initial final checkout
  recalculates tier price but trusts the coupon amount cached earlier in the
  conversation (`handlers_user.py:1068`, earlier validation `:752`), an existing
  validation gap rather than an approved lock. Bounded checkout/database/runner
  inspection found no general expiry timer for unpaid orders or manual receipts;
  receipt submission checks pending status without an age deadline (`:1559`).
  Aban requests a 60-minute invoice lifetime (`abangateway_payment.py:99`), but
  expiry changes invoice state without rejecting/refunding the order (`:151`).
  Automatic card-payment expiry becomes manual review (`database.py:6055`).
  Thus invoice expiry and terminal order cancellation are distinct current
  behaviors. Stored price is not a demonstrated complete offer snapshot: initial
  manual fulfillment reloads the current product (`handlers_admin.py:1886`).
  These are source facts, not approval of composite quote validation, lifetime,
  or immunity to offer edits.

- **F-032:** Ordinary Telegram checkout creates its order for `call.from_user.id`
  (`handlers_user.py:1086`), passes that buyer into managed provisioning
  (`direct_panel_provision.py:118`), and delivers to the buyer
  (`handlers_user.py:1174`). No different-recipient selector was found in that
  bounded checkout. Legacy customer service transfer is a separate confirmed
  action for an owned custom/managed service, excluding tests and requiring an
  existing bot user in the target-selection step (`handlers_user.py:3344`,
  `:3367`, `:3396`). Web administration also has transfer under `users` permission,
  excludes tests, and records history/audit/notification
  (`admin_panel/server.py:2614`). The shared mutation updates only
  `custom_configs.user_id` (`database.py:7196`); the inspected transfer paths do
  not rotate URL/credentials, revoke access already delivered, alter entitlement
  or `test_used`, or reassign the original purchase order. History remains tied
  to the service and receives a transfer event. Test ownership follows the
  requesting account in the intended handler/provisioning paths
  (`handlers_user.py:2258`, `test_config_provision.py:56`), subject to F-017's
  callback identity caveat. These are current source facts, not approval of
  composite paid gifting or ownership reassignment. Static read-only exploration
  used the current-product-flows agent; no application or live service was run.

- **F-033:** Web customer block/unblock calls `set_user_blocked` and writes audit
  history (`admin_panel/server.py:2384`); the database mutation changes only
  `users.is_blocked` (`database.py:2169`). Those inspected actions call no panel
  provider and do not change or revoke VPN services. Bot middleware prevents
  blocked non-admin customers' messages/callbacks reaching handlers
  (`blocked_user.py:52`, registration `bot_manager.py:222`). Existing web managed
  service toggle excludes tests, requires an active panel, calls `set_enabled`,
  then stores the local enabled flag/history/audit (`admin_panel/server.py:2528`).
  Its 3x-UI implementation changes matching clients' `enable` and checks the API
  response, without readback or authentication-level verification
  (`panel_providers/threexui_provider.py:416`, `:299`). The local service flag has
  no distinct customer versus owner restriction (`database.py:7160`), and the
  customer toggle can re-enable an otherwise eligible service
  (`handlers_user.py:3206`). Existing web deletion excludes tests and removes the
  local service despite a provider exception or false result
  (`admin_panel/server.py:2674`, `database.py:3560`), so it cannot prove remote
  revocation; F-004/F-021 retain the provider deletion caveat. These actions use
  `users` permission rather than the new composite owner-only scope. These are
  bounded current-source facts, not approved composite blocking, suspension,
  resumption, or cancellation policy. The existing read-only exploration agent
  inspected these paths; no application or live service was run.

- **F-034:** Current 3x-UI creation constructs an upstream subscription URL from
  `xui_sub_base_url` and `subId`, rather than selecting/exporting individual native
  configurations; one identity/subId can use several configured inbounds
  (`panel_providers/threexui_provider.py:167`). Managed-service storage retains
  that URL (`database.py:6987`). URL refresh uses the first matching client record
  across returned inbounds and reconstructs its subscription URL, not one selected
  advertised endpoint within the payload (`panel_providers/threexui_provider.py:248`).
  Native URI/Base64 parsing preserves all recognized URI lines in returned order
  without a one-entry limit, deduplication, or intended-endpoint matching; HTML
  fallback collects recognized URI matches (`sub_info.py:326`). JSON traversal
  processes profiles/outbounds but individual Xray conversions use the first
  `vnext`/user or server, so it does not preserve every possible JSON endpoint
  (`sub_info.py:240`, `:143`). Optional individual-config delivery iterates the
  entire parsed list; message chunking limits message length rather than node
  count (`config_delivery.py:179`, `:96`). No composite one-entry-per-node policy
  is established by these bounded legacy paths. The existing read-only exploration
  agent inspected current source; no runtime configuration, database, or service
  was accessed, and no compatibility result is claimed.

- **F-035:** Ordinary backup copies one application SQLite database through
  SQLite's Backup API (`backup.py:29`); full backup separately snapshots main/
  listed reseller databases and packages a manifest (`backup.py:93`). Those
  functions do not capture separate FSM stores, deployment files, payment-provider
  records, or remote VPN state. FSM uses `<db_path>.fsm.sqlite3`
  (`bot_manager.py:205`). Restore validation checks size/header and querying
  `sqlite_master`, not business history or external consistency (`backup.py:361`).
  Database replacement saves a pre-restore copy, closes connections/clears caches,
  removes old WAL/SHM files, overwrites the application DB, and reopens on access
  (`database.py:526`); no comparison/reconciliation of newer payment/wallet,
  usage, cancellation/rotation, test/campaign, or live-panel evidence was found in
  that bounded path. Inspected Telegram, web, and Mini App restore entry points
  add no such barrier (`handlers_admin.py:9091`, `admin_panel/server.py:1967`,
  `miniapp/server.py:6498`). Full restore's bot-process reconciliation restarts
  bots from restored reseller rows, not external financial/VPN-state reconciliation
  (`handlers_admin.py:8669`, `bot_manager.py:400`). These are bounded source facts,
  not an executed restore or constitutional-compliance claim. The existing
  read-only exploration agent inspected current source; no backup, runtime DB,
  secret, or live service was accessed.

- **F-036:** Factory reset deletes users/`test_used`, orders, wallet/payment
  data, panels, services/test plans, histories/logs, and settings, preserving
  reseller-bot registrations and owner administration before seeding defaults;
  no pending-money/service/cleanup guard is present (`database.py:1310`, `:1330`).
  Web, Mini App, and Telegram reset require owner confirmation and attempt backup
  without external financial/credential reconciliation; Telegram proceeds after
  a failed backup attempt (`admin_panel/server.py:2011`, `miniapp/server.py:6531`,
  `handlers_admin.py:9172`). Panel deletion checks only `custom_configs` references
  unless forced; force deletes local services, and either mode removes panel test
  plans/custom products and the panel row without provider revocation/refund/
  cleanup handoff (`database.py:6818`). Telegram/web expose forced deletion
  (`handlers_admin.py:4770`, `admin_panel/server.py:4919`). Deactivation flips
  `is_active` without revocation/obligation checks, while ordinary provisioning/
  renewal reject inactive panels (`admin_panel/server.py:4878`,
  `database.py:6792`, `direct_panel_provision.py:47`, `renewal_engine.py:34`).
  No ordinary shop-customer hard-delete path was found in the bounded endpoint/
  shared-mutation search; provider `delete_user` means remote-client deletion.
  These are scoped source findings, not proof of composite history protection or
  any executed destructive operation. The existing read-only exploration agent
  inspected current source without accessing runtime data, secrets, or services.

- **F-037:** The current backup loop defaults to 24 hours, starts its first cycle
  after 60 seconds, and re-reads `backup_interval_hours`; its internal parser
  accepts fractional hours with a one-second minimum (`backup.py:334`, `:358`).
  Telegram owner controls offer 6/12/24/48-hour presets, while custom entry
  converts `int(float(input))` and accepts only 1-720 whole hours
  (`keyboards.py:1286`, `handlers_admin.py:8817`). Those controls cannot select
  a 15-minute interval. Backup delivery attempts target the bot's admins and
  optional second chat/SFTP; failures are logged and swallowed
  (`backup.py:278`, `:311`, `:319`). The owner sync-test callback can consequently
  report success despite a failed destination, referring the owner to logs
  (`handlers_admin.py:8772`). No verified off-host recoverable-history age or
  whole-host recovery guarantee is established by these static paths. Defaults
  describe source, not deployed settings. Read-only fact delegation inspected
  current code without runtime data, secrets, backup files, or service calls.

- **F-038:** Legacy expiry/quota reminder defaults are enabled: five days before
  expiry and 80% consumed (alternative two binary GiB remaining), with a generated
  20% coupon valid for 24 hours (`database.py:224`, `:6139`, `:6204`). The worker
  fetches upstream subscription metadata, skips unavailable values, excludes
  expired expiry notices, and directs customers to a new purchase rather than
  the agreed composite renewal flow (`renewal_reminders.py:40`, `:77`, `:140`,
  `:166`). Candidate queries exclude managed tests (`database.py:6181`, `:6247`).
  Both reminder branches mark sent even after Telegram delivery failure; the
  hourly loop starts with the bot (`renewal_reminders.py:96`, `:180`, `:284`;
  `bot_manager.py:276`). Separate connection/activity alerts default disabled:
  one MiB cumulative usage is a "connected" proxy and a configured threshold
  after 24 hours is a "not connected" proxy; they do not establish current
  sessions/handshakes (`database.py:241`, `:6279`; `connect_alerts.py:69`, `:91`).
  Tests are excluded, checks occur every 15 minutes, and failed sends can still
  mark flags (`database.py:6341`; `connect_alerts.py:82`, `:103`, `:148`). These
  source defaults and historical usage proxies are not composite alert approvals
  or demonstrated reliable delivery. Read-only delegation used no runtime data.

- **F-039:** Customer Telegram details/inquiry refresh provider and upstream
  subscription data (`handlers_user.py:2787`, `:2894`, `:2945`). The subscription
  parser has no observation timestamp/freshness field, defaults absent traffic/
  total to zero, and displays zero total/absent expiry as unlimited
  (`sub_info.py:352`, `:388`); provider usage/status supplies no online/handshake
  evidence (`panel_providers/threexui_provider.py:207`). Thus fetching successfully
  does not prove fresh composite measurements. Customer rename currently rejects
  tests, accepts `[A-Za-z0-9_]{3,20}` with optional prefix/duplicate checks, attempts
  provider rename, and falls back to display-only on `PanelError`
  (`handlers_user.py:3239`, `:3273`, `:3296`; `database.py:7176`). The 3x-UI
  provider modifies client emails; its comment warns old usage may cease appearing
  under the new name (`panel_providers/threexui_provider.py:426`). Personal display
  labeling and remote credential/accounting-identity rename are different behaviors;
  that comment is a source risk, not controlled panel proof. Read-only delegation
  inspected current source without services, runtime data, or experiments.

- **F-040:** Store order/wallet prices are integer toman, with base price,
  discount, wallet contribution, and remaining external `final_price` stored for
  initial/renewal orders (`database.py:3299`, `:3362`). Both gateway dispatches
  receive that external remainder (`handlers_user.py:1367`, `:3750`). The current
  rejection helper returns only wallet contribution (`database.py:3470`).
  Gateway customer payable amounts can differ: automatic card transfer adds and
  verifies an offset-inclusive amount (`card_to_card_payment.py:66`, `:119`);
  BluPal separately stores provider `final_amount_rial` (`blupal_payment.py:109`);
  Noapay sets `fee_on_user=True` and separately stores `quoted_total_toman`
  (`noapay_payment.py:123`); CubePay adds configured percentage/fixed fee and
  verifies stored payable rial (`extra_gateway_clients.py:147`;
  `extra_gateway_payment.py:175`, `:218`). These are source distinctions, not
  proof of actual deployed fees or a composite refund-fee policy.
  Aban/BluPal convert toman/rial by ten with integer reverse division
  (`abangateway_payment.py:60`, `blupal_payment.py:75`). Plisio converts base
  toman using a creation-time configured/fetched rate, rounds USD to two decimals,
  and stores base toman/source USD, without a separate persisted rate snapshot
  (`crypto_payment.py:50`, `:103`; `database.py:5005`); its signed callback status
  alone does not independently compare paid amount/currency or derive network
  fees (`miniapp/server.py:3462`). Direct Stars rounds up, stores the payable
  count, and requires exact `XTR`/count (`extra_gateway_payment.py:98`, `:153`,
  `:371`). Custom gateway creation applies configured conversion but verification
  recomputes it with current settings (`custom_gateway_payment.py:31`, `:144`;
  `miniapp/server.py:3413`). Default comparison permits at least 99% with no upper
  bound and accepts missing/unparseable amounts (`payment_engine.py:126`;
  `miniapp/server.py:2695`). Those unsafe comparison/current-rate patterns are
  not composite approval or constitutional exceptions. Static inspection cannot
  establish gross customer outlay, actual fees, settlement deductions, current
  rates, method availability, or provider contracts. Read-only delegation inspected
  current source only, without runtime data, secrets, live calls, or experiments.

- **F-041:** Current legacy renewal entry checks ownership, service type and
  matching plans but no pending renewal for the same target
  (`handlers_user.py:3544`, `:3647`). `_process_renewal_order` debits wallet
  funds and creates an order (`:3463`); `create_renewal_order` inserts a new
  pending order for its target without a per-target pending-order gate
  (`database.py:3362`). `claim_order` claims only the specified order ID
  (`:3413`), not every order for that subscription. Receipt submission clears
  conversation state and permits returning to the menu (`handlers_user.py:3918`);
  lost-state fallback associates a receipt with the customer's latest pending
  order lacking a receipt (`:5162`; `database.py:3515`). These facts make distinct
  overlapping checkout orders a concrete case; they do not approve this behavior
  for composites or establish safe receipt-to-order evidence. No runtime
  concurrency experiment was performed.

- **F-042:** Current payment selection re-checks current product-method
  restrictions and gateway minimum amounts (`handlers_user.py:138`). A forbidden
  method selection returns an error without itself releasing the order's earlier
  wallet debit. Source therefore does not establish the desired composite
  transition when all permitted methods cease covering a retained quote's
  remainder. Separately, automatic card invoice expiry changes it to manual review
  and releases the unique amount reservation (`database.py:6055`); matching uses
  currently pending exact amounts (`:6038`; `card_to_card_payment.py:119`). A late
  transfer can require investigation; amount equality alone cannot establish
  PC-093/PC-120's beneficiary/order/reference evidence. These are static source
  risks, not actual configured-method availability or authorization to alter
  accepted refund/quote policies.

## Public upstream observations, not deployed facts or product approvals

Read-only public documentation/source inspection: X-001/X-002 on 2026-09-26 and
X-003/X-004 on 2026-09-28. No deployed
panels, application services, secrets, or runtime databases were accessed, and
no experiments were run. These sources are separate from this repository's HEAD.

- **X-001:** Official 3x-UI [OpenAPI source](https://github.com/MHSanaei/3x-ui/blob/main/frontend/public/openapi.json)
  documents `/panel/api/clients/bulkDisable`, returning changed and skipped
  results. The inspected [bulk client implementation](https://github.com/MHSanaei/3x-ui/blob/main/internal/web/service/client_bulk.go)
  distinguishes credential removal from ending its current session and has a
  conditional restart path. Static source does not establish the deployed
  version, configuration, restart impact, or a completed traffic cutoff. These
  are moving `main` references accessed on the date above; they are not version
  pins or an approved implementation choice.
- **X-002:** Official Xray-core source at release v26.3.27, commit
  `d2758a023cd7f4174a5a5fa4ff66e487d4342ba0`, delegates
  [user removal](https://github.com/XTLS/Xray-core/blob/d2758a023cd7f4174a5a5fa4ff66e487d4342ba0/app/proxyman/command/command.go)
  to protocol handlers. Inspection of the VLESS, Trojan, and VMess removal
  paths found authentication-record removal without a general existing-session
  cancellation; VLESS also has special reverse-outbound cleanup. The
  [multiplexing handler](https://github.com/XTLS/Xray-core/blob/d2758a023cd7f4174a5a5fa4ff66e487d4342ba0/common/mux/server.go)
  can dispatch inner requests using an already-authenticated connection's user
  context. Inference: ongoing traffic, potentially including new activity within
  an existing tunnel, may survive credential removal. Neither universal survival
  nor a termination deadline is proven. This is not the user's deployed version.

- **X-003:** Official v2rayN [subscription documentation](https://github.com/2dust/v2rayN/wiki/Description-of-subscription)
  describes protocol-link subscriptions including VLESS and VMess, and its
  [subscription handler source](https://github.com/2dust/v2rayN/blob/master/v2rayN/ServiceLib/Handler/SubscriptionHandler.cs)
  includes Base64 subscription decoding. Official 3x-UI
  [share-link documentation](https://github.com/MHSanaei/3x-ui/blob/main/docs/content/docs/en/config/share-links.mdx)
  describes protocol URI forms and transport/security parameters. These support
  the described URI-list model, not a claim that every named app/version accepts
  every fixture protocol, informational row, or Base64 output. These are moving
  upstream references accessed on 2026-09-28, not deployed version pins. No
  universal "current standard" or informational-row interoperability is proven.

- **X-004:** Official [Xray routing documentation](https://xtls.github.io/en/config/routing.html)
  describes routing by source user to a selected outbound. It supports the
  conceptual distinction between an exported credential/node and a shared
  outbound; adding five outbounds alone does not generate five subscription
  entries. Official [3x-UI client API documentation](https://github.com/MHSanaei/3x-ui/blob/main/docs/content/docs/en/reference/api/clients.mdx)
  documents creating clients attached to selected inbound IDs. These are capability
  references for the proposed equivalent-server replacement, not proof of a
  complete migration workflow or deployed-version compatibility. No API selection,
  shared-rule modification, or raw database-edit procedure is approved. Current
  public documentation was read; no customer panels or live services were contacted.

## Evidence requiring investigation or controlled experiments

- **E-001:** Exact deployed 3x-UI/Xray versions, credential/meter/mutation scope,
  counter persistence and resets, protocol creation, and routing behavior.
  References: D01/D04/D08; S01-S03/S08. Repository source cannot establish deployment.
- **E-002:** Measured cutoff/overshoot, stale-data exposure, coordinator/panel
  outages, and behavior of already-established connections. References: D02;
  S05-S07. Product preferences must be separated from demonstrated feasibility.
  PC-019 does not require proof of a finite outage-overrun cap; it still requires
  honest measured outcomes, pending-state reporting, and validation against the
  eventual normal-operation target. The rejected REC-014 is not a release gate.
  PC-021 also rejects REC-016's forced existing-session termination gate. Test
  fresh authentication separately from existing/multiplexed sessions, record
  native panel behavior and unrelated-customer impact, and verify PC-020's
  60-second target. X-001/X-002 are static evidence, not these controlled results.
  PC-044 extends the native-session policy to leaked-access replacement; verify
  its separate fresh-authentication and new-credential completion criteria.
  PC-045's 60-second replacement target is accepted but not yet demonstrated.
  PC-067 adds the 60-second normal disable/resume target across all required
  nodes, with eligibility and pending-state checks. It also remains unverified.
  PC-075 adds final cancellation's URL/all-child revocation target and separate
  wallet completion requirement; these too require controlled evidence.
- **E-003:** All six handshakes and refresh behavior in agreed versions of the
  named clients and each approved format. References: D05; S04.
  PC-077 additionally requires checking informational-entry display, imports and
  refresh, their effect on node counts, selection/automatic selection, and stale
  information presentation. IMG-001 demonstrates appearance only. V2Box/v2rayN
  examples in PC-076 were subsequently made required launch targets by PC-080:
  verify v2rayNG, NekoBox, Streisand, V2Box, and v2rayN at recorded supported
  versions. BC-002 records daily-use experience, not a demonstrated incompatibility
  or a substitute for the actual composite checks.
- **E-004:** Capacity, external URL/routing recovery prerequisites, and disposable
  restore/lifecycle exercises for the eventual approved scope. References:
  D11/D13/D14; S09/S11-S13. PC-112 accepts the normal fifteen-minute recoverable
  local-history objective, which requires controlled capture/validation/off-host
  availability and stale-restore checks; no passing result is claimed. PC-113
  accepts four-hour conditional safe recovery on prepared infrastructure, with
  prerequisite waiting and unresolved partial recovery reported separately.
  Its supported environment/load and measured result also remain unverified.
- **E-005:** Verified settlement amounts and conversion/fee behavior for eventual
  approved payment methods, plus reliable wallet-credit completion under failures.
  F-040 distinguishes base order funding, offset-inclusive received payment,
  provider payable charges, and separately incurred external fees. PC-120 settles
  the product policy: full accepted invoice-value credit at original conversion,
  with quoted required costs included and separate outside fees excluded from
  automatic coverage. Existing code supplies no demonstrated uniform contract.
  Actual method amount/currency/rate/rounding and fee evidence must be verified
  without copying unsafe legacy comparisons or inventing original conversion data.
  F-012 only establishes inspected local behavior, not the new refund guarantee.
  External original-method refund capability is not required for PC-013's selected
  failed-provisioning policy; the rejected REC-008 must not create an unnecessary
  external-refund integration requirement. Any controlled integration checks remain
  unverified.

No experiments are authorized in this interview. Any remaining evidence blocker
will be stated explicitly at the stopping point; it must not be guessed away.

## Deferred to Spec Kit planning

Physical schema and compatibility mappings; meter/sample representation; algorithms;
worker/process ownership, scheduling, coordination, leases and retry mechanisms;
API contracts and serializers; endpoint hosting implementation; migration mechanics;
technical test design; and task breakdowns. SQLite remains fixed. Product-visible
defaults, limits, timing expectations, and failure outcomes must still be recorded
before these are designed. D06/D12 are principally planning topics with ownership
and tenant-coverage consequences retained in the interview.

## Specification-readiness review and reading index

Reviewed 2026-10-02 against the current source revision recorded above, including
an independent read-only consistency audit. This section is a reading guide to
the accepted answers, not another specification or a change to the reference
documents' historical OPEN status.

- **Product blockers:** The initial review after PC-120 found none. The fresh
  USER-02 review RV-001 subsequently identified two interactions: overlapping
  renewal checkouts and a retained quote losing its permitted funding path.
  PC-121 and PC-122 settle both. The final check found no further product
  blocker; the reviewer recommends closure under USER-01's stopping condition.
  Q-109 was not separately answered and grants no downstream authorization.
  Earlier accepted PCs are unchanged.
- **Constitution:** No amendment or exception was accepted. Preserve financial
  verification, ownership/isolation, unique usage attribution, honest uncertainty,
  retained cleanup, safe stale-restore recovery, and controlled validation.
  Best-effort cutoff/native existing-session behavior is a product choice, not
  evidence of compliance or permission to claim unverified cutoff. Missing
  history still needs the specific Governance treatment in PC-108.
- **Confirmed inputs:** R01-R07 remain preserved by the accepted PCs. The
  six-node multi-panel fixture remains required verification and is not a maximum;
  PC-085's initial live A-only/five-choice setup does not erase it. USER-01's
  Spec Kit workflow supersedes R08's historical handoff process and P0-P6,
  without approving their architectural proposals or changing the source files.
- **External evidence:** E-001-E-005 are still unverified. Source inspection,
  the user's daily client experience, and proposed acceptance scenarios are not
  passing composite integration results. No actual compatibility failure or
  demonstrated inability to meet the accepted product contract was established.
  Evidence can be researched/planned during the later workflow; any finding
  requiring a changed product promise must be explicitly revisited.
- **Work boundary:** No application service, live service, runtime database,
  secret, integration experiment, formal specification/plan/tasks, code change,
  or Git commit was used or created in this interview. Documentation checks do
  not certify release readiness. The user initiates the later specify step.

The table locates accepted product answers relevant to each original D topic.
It does not approve an original recommendation wholesale; detailed wording,
conditions, exceptions, reference IDs, and observable implications stay in the PCs.

| Original topic | Accepted product inputs to consult | Still deferred or unverified |
|---|---|---|
| D01 — Panel/core support | PC-001-PC-005/PC-021/PC-083/PC-106/PC-114 | Exact supported versions; API/protocol, meter, mutation, native session and routing evidence. |
| D02 — Enforcement/outages | PC-018-PC-023/PC-034/PC-067/PC-075/PC-079/PC-087/PC-107/PC-115/PC-116 | Mechanisms and measured timing/exposure. No finite outage-overrun cap or forced existing-session termination is required. |
| D03 — Units/activation/terms | PC-014-PC-016/PC-027-PC-033/PC-055-PC-064 | Clock/representation implementation and boundary verification; finite binary units, 30-day paid terms, 45-day total remaining cap and test exceptions are settled. |
| D04 — Routing ownership | PC-002/PC-083/PC-085-PC-091/PC-106 | Prepared routing/egress and faithful export evidence; no approval to modify shared listeners, outbounds or unrelated routes. |
| D05 — Formats/client coverage | PC-076-PC-082/PC-104/PC-106/PC-115 | Recorded versions of the five named apps, complete six-node handshakes, information-row and refresh behavior; Clash/sing-box are explicitly deferred. |
| D06 — Storage/compatibility | PC-001-PC-005/PC-101/PC-108/PC-109/PC-119 | SQLite schema, compatibility mapping and physical addressing design; no storage proposal is selected. |
| D07 — Buyers/issuance/money | PC-006-PC-010/PC-050-PC-064/PC-092-PC-103/PC-117-PC-120/PC-122 | Actual safely supported configured payment methods and their evidence; no additional reseller, Mini App, gift or commission flow is assumed. |
| D08 — Usage/reset uncertainty | PC-004/PC-018-PC-023/PC-034/PC-084/PC-087/PC-107/PC-108/PC-114-PC-116 | Counter/sample/epoch representation, attribution algorithms and actual reset/recovery evidence; unknown usage remains explicit. |
| D09 — Renewal/conversion | PC-024-PC-039/PC-052/PC-061/PC-105/PC-110/PC-118/PC-119/PC-121 | Repeat-safe operation design, carryover/mutation evidence and matching-preset implementation; approved equivalent movement preserves intended matching. |
| D10 — Fulfillment/refunds | PC-011-PC-014/PC-036-PC-038/PC-048/PC-049/PC-055-PC-075/PC-092-PC-099/PC-107/PC-108/PC-120-PC-122 | Durable operation and financial design, exact method conversions/rounding and controlled failure checks; complete-plan gates and gross quoted invoice-value credits are settled. |
| D11 — URL/metadata/refresh | PC-005/PC-039-PC-045/PC-049/PC-076-PC-082/PC-091/PC-104/PC-106/PC-113/PC-115/PC-117/PC-118 | Public HTTPS/domain prerequisites, endpoint/token/cache/serializer design and client evidence; URL withholding does not revoke imported credentials. |
| D12 — Processing/deployment | PC-003-PC-005/PC-009/PC-107/PC-108/PC-112-PC-116 | Process ownership, worker scheduling, concurrency/leases/retries/maintenance and load evidence; eligible coverage and optional bot/UI independence remain required. |
| D13 — Migration/backup/recovery | PC-086-PC-091/PC-107-PC-114/PC-119/PC-120 | Mechanics and measured recovery/capacity, external prerequisites and lost-history reconciliation; legacy import is deferred, stale snapshots are not current proof. |
| D14 — Management/history | PC-040-PC-047/PC-065-PC-075/PC-088/PC-101-PC-111/PC-114/PC-119 | Credential/lifecycle sequencing, retained history/cleanup and destructive-operation protection evidence; no arbitrary sold-topology edit, ownership reassignment or history-erasing shortcut is approved. |

This review does not replace detailed campaign/test reservation and reset rules,
coupon/zero-price handling, sequential cancellation of an in-flight paid renewal,
or the prerequisites/limits on timing targets. Those exact accepted conditions
remain in their individual records. No technical uncertainty becomes an approved
choice by being listed here.

## Terminology and document changes

[CONTEXT.md](../../CONTEXT.md) records feature vocabulary from REQUIREMENTS and
the composite-plan, store-owner, failed-provisioning-refund, and validity-start
meanings settled in PC-008/PC-009/PC-013/PC-014. It describes the intended feature,
not a claim of current behavior. Best-effort cutoff terminology follows PC-019;
full-plan renewal terminology follows PC-024 and does not imply a reset policy.
Carryover terminology follows PC-027; PC-028 excludes expired unused data.
Monthly-term terminology follows PC-033's exact 30-day meaning.
Overrun terminology follows PC-034 and does not imply customer debt.
Replacement-cooldown terminology follows PC-041/PC-047, including successful
owner-triggered replacement.
Leaked-access replacement terminology follows PC-042.
Usage-gap settlement terminology follows PC-084; it resolves the commercial
treatment of missing consumption without claiming to reconstruct it.
Equivalent server replacement terminology follows PC-086. PC-087 permits explicit
owner-approved emergency cutover with tracked old-server cleanup, and PC-088
requires fresh credentials for moved nodes while preserving the subscription URL.
Paid-reminder-period vocabulary follows PC-118 and distinguishes its current
shared terms from lifetime billing history and credential generations.
Payment-quote and invoice-payment-cost vocabulary follows PC-120, distinguishing
the original accepted invoice conversion/cost from the retained store offer and
separate outside fees. Glossary definitions summarize terms only; the accepted
PCs preserve the complete policy.
No additional ADR is proposed: pre-launch product policies are recorded here,
and no separate architectural choice meeting all three skill criteria was selected.

Files created so far:

- `docs/composite-subscriptions/GRILLING-PRODUCT-DECISIONS.md`
- `CONTEXT.md`

Constitution and six reference documents are preserved. No application code,
formal specification, plan, tickets, services, or Git commits were created.
