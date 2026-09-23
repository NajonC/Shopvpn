# Upstream change review

Reviewed 2026-09-20; independently verified and qualified 2026-09-21 at the same HEAD. See [the independent review][independent]. This document records source evidence and proposed follow-up, not implementation or approval of composite business policies.

| Baseline | Commit |
|---|---|
| Historical architectural audit | `0203eece29931a8a0306e4b5c46c59228d0864dd` |
| Refreshed source review | `696695850180fc97f66457a41e86c76dcd330e1e` |

The comparison spans 198 commits and 61 changed files: 15,967 insertions and 1,346 deletions. `VERSION` is `4.5.0` at both commits. Commit titles and the unchanged version label do not establish compatibility. The review used the aggregate Git diff, targeted source inspection, and AST comparisons of relevant functions, schema declarations and routes. It did not run migration tests, application integration tests, or live-panel operations. The independent source review completed on 2026-09-21; its qualifications are incorporated below and in the linked report. P0 remains unstarted.

**Qualified verdict:** the parent subscription/arbitrary child collection architecture remains a plausible basis for separate planning with SQLite. Deployment feasibility and enforcement/recovery guarantees are unverified. P0-P6 remain proposed packages; P4 completion additionally depends on integration with P3 accounting/lifecycle, and P1 storage checks cannot alone prove end-to-end cleanup. There is no composite parent/child schema, unified `/sub/{token}` payload endpoint, or shared-quota enforcement worker in the reviewed source. The core 3x-UI creation, usage, deletion and update-addressing functions remain unchanged except for renewal behavior. `sub_info.py` is unchanged. The original concerns about distinct same-inbound identities, error-as-zero readings, application-level API errors, durable accounting, and complete URI serialization remain relevant.

**U01 — Renewal semantics changed**

The provider interface now accepts `preserve_remaining`. [Manual full renewal][renewal] passes it as true, then reads the resulting panel limit into the local service record. [Automatic renewal][auto-renew] passes `reset_usage=True` without carryover, using the provider's false default. In [3x-UI renewal][provider-renew], full renewal with carryover computes remaining allowance plus the purchased volume; replacement renewal sets the new volume. The expiry still uses the existing extension logic. The historical audit's description of simply adding the previous total and resetting usage is no longer the current behavior.

The same 3x-UI function catches a failed usage lookup and substitutes zero used bytes when calculating carryover. That can overstate remaining allowance. This refresh documents the defect; it does not authorize preserving it. Composite renewal needs a parent-level accounting decision, including offline-meter settlement, and must not apply a whole shared allowance independently as six new entitlements. Preserve intended legacy behavior while choosing composite semantics explicitly.

The reset request at provider lines 372-376 checks neither HTTP nor application success and swallows `aiohttp.ClientError`. The manual engine's read-back at lines 43-49 can fail after remote mutation but before local application. Retrying additive renewal can repeat effects. A25 must cover those boundaries, not only a failed initial usage read.

Affected: D08/D09; P2/P3/P5; A09/A11/A15/A25. The added full-renewal UI filters by a single panel, covered in U06.

**U02 — Reseller services now use local panel mirrors**

[Mirror creation][mirrors] copies a main-registry panel into the tenant database with `mirror_source_id` and `is_mirror`, so local service foreign keys no longer have to misuse main-database IDs. [Panel enumeration][panel-list] hides mirrors by default; direct lookup by local ID still works. [Reseller fulfillment][reseller] uses the local mirror ID when persisting services. This corrects an important cause of the historical persistence failure, without resolving every later database or network failure.

P0 must distinguish the local row address from the physical remote panel and canonical meter identity. A worker that enumerates only the default panel list could miss mirrored services. Counting main and mirrored views of one remote identity separately would duplicate usage. Mirror refresh, source credential changes, missing source rows, and shared-panel mutation coordination across tenants need contracts rather than assumptions about coinciding integer IDs.

Mirrors are opportunistic copies: ordinary lookup at `database.py:6839` is a local SELECT, and the mirror helper forces `is_active=1` rather than copying source activation. Existing services can retain stale connection fields. `database.py:6911-6914` explicitly permits multiple source rows for one physical panel with different credentials; `mirror_source_id` alone therefore does not establish canonical meter identity. A26 includes aliases as well as mirrors and source deactivation/removal.

Affected: D06/D07/D12; P1/P2/P3/P5; A08/A19/A26.

**U03 — Reseller models and worker eligibility expanded**

Upstream now supports volume credit, per-product quantity inventory, commission/discount tiers, dedicated bots, and reseller records without a live Telegram bot. The old `reseller_level` migration/API is replaced by newer role and capability behavior; an old column may still exist in an upgraded database. [Registration][registration] uses `has_live_bot`, and [bot reconciliation][bot-reconcile] excludes records where it is false. [Reseller provisioning][reseller] consumes either volume credit or fixed-product inventory, using guarded database updates after remote creation.

Composite sale eligibility remains D07. For each approved tenant type, accounting and revocation must run independently of Telegram polling and UI availability. Define which database owns the entitlement, which owns supplier credit/inventory, and how one purchased unit is charged once. This is a larger integration matrix, not permission to enable every new reseller mode for composites automatically.

Affected: D07/D11/D12; P0/P1/P3/P5; A03/A19/A27/A28; S12.

**U04 — Tier changes and ownership transfers affect cleanup**

[Tier switching and cleanup][tier-cleanup] can remove reseller registrations and the tenant's database files. [Ownership transfer][ownership] updates main-registry ownership and attempts to update the tenant owner. Neither is a composite lifecycle operation at this baseline.

If child identities, meters and pending revocations are stored only in the removed database, destroying it would erase responsibility for still-active remote credentials. P0 must define a retention/transfer/revocation policy for tier changes, deletion, ownership transfer and deferred purge. Required cleanup must remain durable outside any database scheduled for deletion, or deletion must wait. Changing a business owner must not silently change customer ownership or duplicate remote credentials. Ownership changes spanning databases also need partial-failure recovery.

The ownership helper does not transfer every supplier/customer relationship: fixed-product inventory remains keyed by the old reseller ID and `users.owner_reseller_id` is not rewritten. Whether those should move is still D07/D14. [Factory reset][factory-reset] is another destructive path: it clears management, panel, order and inventory data in place without remote cleanup. Retaining the DB file or only excluding future composite tables from reset does not preserve deleted dependencies. The deferred purge queue records file cleanup, not confirmation of remote revocation.

Affected: D06/D07/D12/D14; P1/P3/P5; A17/A19/A29; S13.

**U05 — Provisioning has best-effort rollback and chosen names**

[Direct provisioning][direct] now validates quantity, reads `orders.config_name`, tries user-selected names, and attempts deletion of already-created users after certain failures. Reseller provisioning also attempts rollback and guards credit/inventory consumption. The old finding that there is no rollback must remain historical. These helpers still create remotely before persisting all local service records; cleanup failures can be swallowed, and local persistence failures can be logged without making fulfillment fail. This is not durable all-or-nothing provisioning.

The [web-admin auto-product approval branch][approval] still calls provisioning without the owner/order arguments. P5 must carry fulfillment identity through every approved entry point. P3 must retain stable child intentions through ambiguous timeouts and failed rollback. Customer-selected names should not become an unvalidated routing authority or collide across subscriptions; naming and display behavior need to satisfy D04/D14.

Affected: D04/D10/D14; P1/P3/P5; A03-A06/A28.

**U06 — More fulfillment paths and a single-panel renewal filter**

[Additional gateways][gateways] reuse `abangateway_payment.finalize_paid_order`; their invoice polling and callback paths must reach the same idempotent composite fulfillment service. The [reseller web self-service builder][self-service] creates directly through a provider and records a mirrored local service. Fixed-product bot purchase paths and atomic test-slot reservations add further integration/compensation cases. Upstream also added panel providers; existing providers must remain compatible with the extended interface, while composite support stays scoped to 3x-UI unless separately approved.

The [Mini App full-renewal plan list][renewal-plans] selects products whose single `provision_server_id` equals the service's `panel_server_id`; its submission handler repeats that check. A composite parent cannot use that criterion unchanged. Define eligible renewal plans at entitlement/topology level, preserving applicable pricing, discounts and payment-method restrictions. Do not bypass existing order/invoice claims or reserve one test slot/charge per child.

Compensation differs by entry point. Web self-service (`admin_panel/server.py:2827-2837`) can refund supplier state after failed remote cleanup; test-slot reservation (`database.py:2284`) is an atomic counter without a durable operation identity. Fixed-product handlers (`handlers_user.py:2371-2383`, `2410-2421`) cache a target while `reseller_auto_provision.py:265` resolves it again. A28 must cover crashes around debit/reservation, failed cleanup with refund, and a changed target between resolution and persistence.

Affected: D01/D07/D09/D10; P2/P3/P5; A03/A23/A25/A28/A33.

**U07 — Connection alerts now consume subscription metadata**

The [connection-alert worker][alerts] fetches each service URL, checks upload plus download, and records connection/no-connection notification flags. It runs alongside reminders; it is not a global quota enforcer. Mini App `/api/sub-info` now also derives connection status from fetched metadata. This is usage-based activity inference, not proof of a current connection.

The [metadata parser][metadata] does not check HTTP status, defaults missing upload/download/total fields to zero, and accepts negative integers. Missing headers and network failures do return `ok=False`, which consumers skip; a partial header can instead be accepted as unused. There is no freshness state. The Mini App (`miniapp/server.py:1297-1313`) ignores the separate no-connection volume threshold used by the worker (`connect_alerts.py:98-99`). The worker marks notification flags even when delivery fails (lines 83-87, 104-108). Existing flags and `ok=True` are consequently not evidence of reliable delivery or valid fresh accounting.

P4/P5 must supply appropriate aggregate metadata and one logical alert state per parent. Missing or stale readings must not appear as a fresh unused subscription. Define how the endpoint and worker obtain the same authoritative accounting state without requiring one live call per child for every download. A public endpoint must remain usable by subscriber apps independently of Telegram authentication and optional Mini App visibility.

Aggregate lifetime usage after renewal or rotation is not automatically evidence that current credentials have connected. D09/D11 must distinguish billing history from the selected activity/alert boundary; A32 covers this without choosing a reset policy.

Affected: D02/D09/D11/D12; P3/P4/P5; A09/A20/A32.

**U08 — Backup compatibility remains, but recovery is still incomplete**

[Single-database backup][backup] still copies the whole SQLite database, so new tables stored there are included. Full ZIPs now use `reseller_<id>.db`; [restore][full-restore] accepts both that name and the historical `reseller_<id>_level<N>.db`. ZIP creation snapshots databases sequentially and can skip missing/failed tenant copies; it is not an atomic snapshot of all financial and entitlement state.

[Database replacement][replace] still coordinates only its local database instance, replaces the file, and does not itself run migrations or reconcile panels. Restore paths must coordinate all bot/HTTP/accounting writers and in-flight remote operations, migrate before resuming consumers, and reconcile the restored state. Pending work from a previous process/restore generation must not blindly replay old enable/create/renewal operations.

An old snapshot may contain 20 GB consumed even though the user has since exhausted 50 GB, renewed, rotated credentials, or gained additional children. Same-epoch panel counters can help recover missing usage, but cannot reconstruct all lost purchases, resets, ownership or revocation history. Define uncertainty handling and orphan discovery; a backup cannot recreate records that never reached it. Preserve subscription tokens and document the external URL/domain and infrastructure prerequisites. The bot ZIP does not back up the remote panels, Xray routing/outbounds, or external server configuration.

Full restore replaces main before tenant validation (`backup.py:203-241`), and entirely absent required tenant archive members are not reported as skipped. Its validator (`backup.py:361-377`) does not establish feature-schema compatibility. Bot full restore stops selected current-registry bots (`handlers_admin.py:8688`), but reconciliation can restart them; single/UI replacement does not coordinate all writers. `manage.sh:1793-1795` does attempt to stop the three known services, while ignoring stop errors. None of these caller differences establishes safe recovery against panels. Stale restored file-purge jobs must also participate in recovery ordering.

Affected: D08/D11/D12/D13/D14; P1/P3/P5/P6; A23/A30/A31; S11.

**Follow-up and approval boundary**

The independent review is complete and returned in [its report][independent]. All U01-U08 core findings were confirmed with qualifications, and no later local source changes were found. D01-D14 remain open; P0 and implementation remain unstarted. The user must separately request the planning task. This review does not grant permission to change running infrastructure, fix application code, create tasks, or deploy.

[renewal]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/renewal_engine.py:39>
[auto-renew]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/renewal_reminders.py:261>
[provider-renew]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/panel_providers/threexui_provider.py:327>
[mirrors]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/database.py:6861>
[panel-list]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/database.py:6843>
[reseller]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/reseller_auto_provision.py:84>
[registration]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/database.py:4734>
[bot-reconcile]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/bot_manager.py:419>
[tier-cleanup]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/database.py:1930>
[ownership]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/database.py:4824>
[direct]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/direct_panel_provision.py:34>
[approval]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/admin_panel/server.py:2197>
[gateways]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/extra_gateway_payment.py:302>
[self-service]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/admin_panel/server.py:2779>
[renewal-plans]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/miniapp/server.py:815>
[alerts]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/connect_alerts.py:60>
[backup]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/backup.py:29>
[full-restore]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/backup.py:209>
[replace]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/database.py:526>
[independent]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/docs/composite-subscriptions/INDEPENDENT_REVIEW.md>
[factory-reset]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/database.py:1314>
[metadata]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/sub_info.py:359>
