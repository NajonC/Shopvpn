# Independent handoff review

Reviewed 2026-09-21. **Ready for a separately authorized planning task, with blockers recorded below; not ready for implementation or deployment.** The parent subscription with arbitrary child credentials remains a plausible architecture with SQLite. The earlier unqualified viability/sequence verdict needs the accounting, recovery and package-dependency qualifications in this report. No business policy, ERD or implementation interface was selected, and P0 remains unstarted.

## Reviewed state and evidence

| Item | Result |
|---|---|
| Exact reviewed HEAD | `696695850180fc97f66457a41e86c76dcd330e1e` |
| Historical audit baseline | `0203eece29931a8a0306e4b5c46c59228d0864dd`, retained unchanged |
| Changes after refreshed baseline | None in this checkout: HEAD equals that baseline; tracked worktree and index diffs are empty |
| Historical-to-refreshed comparison | Independently confirmed: 198 commits, 61 files, 15,967 insertions, 1,346 deletions; `VERSION` is `4.5.0` at both ends |
| Initial untracked state | `COMPOSITE_SUBSCRIPTION_AUDIT.md`, `COMPOSITE_SUBSCRIPTION_AUDIT-CODEX.md`, `COMPOSITE_SUBSCRIPTION_AUDIT-AGY.md`, and the eight handoff Markdown files |
| This review's writes | Documentation only in `docs/composite-subscriptions`; the eight handoff files were updated and this report was added. No commit, branch, application/test edit, dependency installation, live mutation or deployment |

The later-change check concerns the local repository and working tree. No remote fetch was performed; it does not assert that no newer upstream commit exists elsewhere. No applicable `AGENTS.md` was found in the checkout or its ancestor chain. Three bounded read-only subagents checked source slices permitted by the review brief; their findings were reconciled with the handoff and targeted source inspection.

Evidence consists of Git comparisons, static source/AST inspection and isolated in-memory probes of actual function ASTs using synthetic responses. The probes did not import the application or use network dependencies. They reproduced HTTP-200 `success:false` traffic as zero and deletion as success, loss of VLESS `flow`, and sing-box REALITY conversion to ordinary TLS without its public key. Eight core provider methods compared equal to their historical ASTs; renewal is the material provider change. `sub_info.py` has no historical-to-HEAD diff. An AST scan of the two HTTP servers found 461 literal HTTP route-like declarations and no `/sub/` payload route; the historical 390 count remains historical. Schema, route and worker inspection found no composite implementation. No application integration, migration, acceptance or staging tests were run.

## U01-U08 verification

All eight core findings are **confirmed**, with the following source-backed qualifications. None is superseded by a later local change. Deployed behavior remains unverified.

| Finding | Verdict and evidence | Qualification added to the handoff |
|---|---|---|
| U01 renewal | **Confirmed.** Manual carryover and subsequent read-back: [renewal engine][renewal]. Automatic replacement: [automatic renewal][auto]. Provider calculation: [3x-UI renewal][provider-renew]. | Besides error-as-zero carryover, traffic reset responses are unchecked at provider lines 372-376. A read-back failure can occur after a successful mutation but before local application at engine lines 43-52. Retrying can repeat additive effects; an ordinary successful provider call is not durable renewal settlement. |
| U02 mirrors | **Confirmed.** [Lookup/enumeration][mirror-list], [mirror creation][mirrors], and [reseller persistence][reseller-persist] use tenant-local IDs. | Lookup does not refresh the source; the helper refreshes opportunistically and forces `is_active=1`. [Multiple source rows may represent the same panel][panel-alias]. `mirror_source_id` maps rows, not proven physical meter identity. |
| U03 reseller/worker modes | **Confirmed.** [Registration][registration], [guarded supplier debit][reseller-debit], [initial startup][startup] and [reconciliation][reconcile]. | No-live-bot rows can have tenant databases but are excluded from both bot startup paths. Reminder/alert tasks start only inside [start_bot][jobs]. Atomic supplier debit does not include remote creation or the later tenant write. |
| U04 tenant lifecycle | **Confirmed.** [Tier wipe][wipe], [ownership transfer][transfer] and [deferred purge][purge]. | Transfer's tenant update is best effort after main commit; it does not move fixed-product inventory keyed by the previous reseller owner. [Factory reset][factory] also destroys management data in place, without panel cleanup. Pending file purge is not remote cleanup. |
| U05 provisioning | **Confirmed.** [Direct provisioning][direct] validates quantity/names and attempts rollback; [reseller persistence][reseller-persist] still follows remote creation. [Web approval][approval] omits owner/order arguments. | Persistence failures can still return success. Names alone are insufficient retry identity; target panel/inbound ownership must remain recoverable through configuration changes. |
| U06 integration | **Confirmed.** [Added gateways][gateways], [web self-service][self-service], [renewal filter][plans] and [test-slot reservation][test-slot]. | Self-service can refund after failed cleanup; reservation counters have no durable fulfillment identity. Fixed-product handlers cache a target while the [helper resolves it again][fixed-helper]. These paths need failure/target-change coverage, not just successful-route coverage. |
| U07 alerts/metadata | **Confirmed; metadata assumptions corrected.** [Worker][alerts] and [Mini App][connection-ui] infer activity from usage, not a current connection. | [Parser][metadata] accepts headers without checking HTTP status, defaults absent counters to zero and accepts negative integers. Missing headers/network failures do return `ok=False`; not every failure becomes zero. Worker/UI no-connection thresholds differ, and worker flags are marked even if notification delivery fails. |
| U08 backup/recovery | **Confirmed; compatibility qualified.** [SQLite backup][backup], [ZIP restore][restore] and [replacement][replace]. | Main replacement precedes tenant validation; entirely absent tenant copies are not counted as skipped. Validation is a header/schema-catalog check, not feature-schema compatibility. Some callers stop bots/services, but none proves coordinated recovery against panels. |

## Architectural challenges and acceptance gaps

These are blockers to approving the applicable implementation contracts or release claims, **not blockers to starting the separate planning task**.

1. **One parent bucket is feasible; polling alone does not establish a bounded cutoff.** Giving each of six children the purchased quota is still six remote allowances. Stale totals are lower bounds. A panel-API outage or complete coordinator outage while VPN traffic continues defeats a fixed overshoot promise without an additional agreed enforcement contract. D02 must settle the guarantee, including established sessions; A12-A16 and S05-S07 must test it. No fixed interval, local-grant design or outage policy is approved here.
2. **The current adapter is not the child-creation contract.** [Creation][create] chooses server-wide inbound defaults, generates credentials inside the request path, enables immediately, and derives expiry separately per call. It does not accept the required persisted child intent, explicit B inbound selection or common absolute expiry, and its client builder has no `flow` field. P2 must establish protocol-valid creation as well as export; fixing a serializer cannot repair wrong remote authentication settings. A02/A05/A21/S02-S04 need this distinction. A14 must follow the deployed mutation scope rather than mandate an email-wide update for every possible API version.
3. **Canonical remote identity spans database aliases.** Local IDs, source IDs, panel URLs and names are insufficient by themselves to prove one physical meter or owner. Stale/disabled mirrors and multiple source rows can miss or double-charge a meter. A26 now explicitly includes these cases. D06/D12 still need an ownership and discovery contract; no schema or canonical key is selected.
4. **Renewal and fulfillment cross irreversible boundaries.** Existing local order claims, debit guards and best-effort rollback do not atomically cover panel effects, supplier state and tenant records. A25 now includes failed reset and failed post-mutation read-back; A28 includes crashes around debit/reservation, refund despite failed cleanup, and changed targets. Preserve intended legacy behavior without turning current defects into composite policy.
5. **Lifecycle ownership can disappear without deleting a DB file.** A29/S13 now include factory reset and supplier ownership boundaries, alongside tier/delete/purge. Leaving future composite tables out of the reset list alone would not preserve their deleted owner, panel and order dependencies. A stale restored purge queue is also destructive work, not merely an old enable/renew command. D14 must decide transfer/revoke/reset behavior and durable responsibility without assuming existing wipe behavior is acceptable.
6. **Backup inclusion is not safe restore.** Sequential main/registry/tenant snapshots can disagree. [Restore][restore] can replace main then fail/skip tenants, or leave newer files for absent archive members. The [bot restore caller][bot-restore] stops current registry bots but normal reconciliation can restart them; [manage.sh][shell-restore] attempts to stop all three services but ignores stop errors. A30/A31/S11 now explicitly cover these boundaries and stale destructive work. Lost purchases, resets or revocations cannot be exactly reconstructed from current counters alone; D08/D13 need explicit uncertainty and data-loss limits.
7. **P3/P4 parallelism has an integration dependency.** Payload serializers can be developed independently against settled contracts, but P4 cannot pass authoritative metadata, cache invalidation and revoked-state acceptance before integration with P3 accounting/lifecycle. The old P4 input list omitted this completion dependency. Similarly, P1 can prove storage-retention invariants, but end-to-end cleanup/restore through actual entry points requires P3/P5. The package document now records these qualifications without creating a new implementation plan.
8. **Metadata has validity and history boundaries.** A32 now includes partial/negative/non-success/stale responses, differing thresholds and failed notification delivery. Lifetime billed usage after a renewal/rotation is not automatically evidence that the current credential generation has connected. D09/D11 must define that relationship and what “connected” means; the review does not select thresholds or alert reset/delivery policy. The public endpoint cannot depend on optional Telegram or Mini App availability.

The single-listener A topology has no demonstrated architectural contradiction. Current [Xray routing documentation](https://xtls.github.io/en/config/routing.html) supports authenticated-user email matching to outbounds, with first-match rule ordering; [the matcher source](https://github.com/XTLS/Xray-core/blob/main/app/router/condition.go) evaluates explicit users and regexes. This supports the topology in principle, not the installed versions, rule precedence or performance. Current [3x-UI controller source](https://github.com/MHSanaei/3x-ui/blob/main/internal/web/controller/client.go) exposes per-email lookup/link routes despite the local provider's older “no single-client GET” comment. These moving upstream references were checked as capability leads only; D01/S01 must pin actual supported deployments.

SQLite is not disproved by the review. [WAL and instance-local locking][sqlite] do not establish cross-process leases, cross-database settlement or remote request ordering. Capacity and lock-contention guarantees remain unverified under A18/S09; changing the database engine would not remove the remote uncertainty. The agreed SQLite constraint, six-node fixture, single A listener and Base64/Clash/sing-box scope boundary remain intact.

Nonblocking issues are stale historical line anchors, residual `reseller_level` display terminology, and handoff portability. They do not invalidate the model. The handoff remains untracked: a new worktree will need these documents explicitly supplied or committed by a separately authorized action. No copying/commit is assumed here.

## Open decisions and deployment evidence

All D01-D14 remain **OPEN**. The later planning task must resolve or identify the approval/evidence needed for each applicable contract before dependent implementation:

| ID | Question still unresolved |
|---|---|
| D01 | Which exact A/B/C panel/core versions and API capabilities are supported, including read/write/reset and mutation scope? |
| D02 | What delay, overshoot, worker/panel outage and established-session behavior is acceptable? |
| D03 | What quota unit, start/activation boundary, common expiry and unlimited-plan meaning apply? |
| D04 | Who owns routing rules and stable country identity names, and how is route precedence verified? |
| D05 | Which versions of Base64/URI, Clash and sing-box consumers must support all six nodes? Any reduction needs explicit scope approval. |
| D06 | How do parent/service compatibility, local/source aliases, canonical meters and ownership relate? |
| D07 | Which sale/tenant modes are eligible, and who owns charges, supplier credit/inventory and cross-database settlement? |
| D08 | Which samples, epochs and resets are trustworthy, and what happens to unobserved or lost usage? |
| D09 | What renewal/add-on/carryover, offline settlement, suspension ordering and plan eligibility apply? |
| D10 | What constitutes completed fulfillment and how do cancellation, refund, reservation and cleanup recover? |
| D11 | Where is the public endpoint hosted, how are tokens/tenants resolved, and what do freshness, alert history and rotation mean? |
| D12 | Which processes own workers and tenant discovery, mutation coordination, SQLite claims and restore maintenance? |
| D13 | What migration/rollout, backup completeness, data-loss, uncertain recovery and rollback limits are acceptable? |
| D14 | What happens to identities, customer/supplier ownership and cleanup on rotation, transfer, tier/delete/purge and factory reset? |

Deployment evidence still required: sanitized A/B/C configurations and actual versions; user/meter scope and counter persistence across resets/restarts; routing and listener ownership; all six real protocol handshakes in the named app versions; HTTPS/domain/token recovery prerequisites; actual process/tenant/database layout; measured load, cutoff/overshoot and established-flow behavior; and isolated stale-restore/tenant lifecycle exercises. A25-A33 and S11-S13 are strengthened specifications, not passes. No live credential or mutation was requested for this review.

## Documentation changes and stopping point

- Added this independent report and updated README/STATUS to record review completion and conditional planning readiness.
- Expanded U01/U02/U04/U06/U07/U08 evidence; kept all U IDs, both baselines and historical audit files intact.
- Clarified factory reset, alias identity and activity-history questions in REQUIREMENTS/DECISIONS; all D IDs remain open.
- Corrected P4's completion dependency and P1's end-to-end proof boundary in WORK_PACKAGES.
- Refined existing acceptance cases, including A02/A14/A16/A25-A32 and S06/S11/S13; no new case was marked passed and no policy default was selected.
- Marked NEXT_SESSION_PROMPT as the completed review brief so it is not mistaken for authorization to begin P0.

**Review gate complete.** After reading this result, the user can separately authorize planning. That task must turn the unresolved questions and evidence gaps into reviewable contracts and distinguish proposals from approvals. This review stops here; P0-P6 are not started.

[renewal]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/renewal_engine.py:39>
[auto]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/renewal_reminders.py:261>
[provider-renew]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/panel_providers/threexui_provider.py:327>
[mirror-list]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/database.py:6839>
[mirrors]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/database.py:6861>
[panel-alias]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/database.py:6911>
[reseller-persist]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/reseller_auto_provision.py:182>
[registration]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/database.py:4734>
[reseller-debit]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/reseller_auto_provision.py:159>
[startup]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/main.py:47>
[reconcile]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/bot_manager.py:419>
[jobs]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/bot_manager.py:276>
[wipe]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/database.py:1930>
[transfer]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/database.py:4824>
[purge]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/bot_manager.py:517>
[factory]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/database.py:1314>
[direct]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/direct_panel_provision.py:34>
[approval]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/admin_panel/server.py:2197>
[gateways]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/extra_gateway_payment.py:302>
[self-service]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/admin_panel/server.py:2779>
[plans]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/miniapp/server.py:814>
[test-slot]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/database.py:2284>
[fixed-helper]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/reseller_auto_provision.py:265>
[alerts]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/connect_alerts.py:60>
[connection-ui]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/miniapp/server.py:1284>
[metadata]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/sub_info.py:359>
[backup]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/backup.py:29>
[restore]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/backup.py:203>
[replace]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/database.py:526>
[bot-restore]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/handlers_admin.py:8688>
[shell-restore]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/manage.sh:1793>
[create]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/panel_providers/threexui_provider.py:141>
[sqlite]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/database.py:473>
