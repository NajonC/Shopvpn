# Status and evidence at handoff

Originally recorded 2026-09-11; refreshed 2026-09-20; independently reviewed 2026-09-21. **Review and documentation corrections are complete. P0 and implementation remain unstarted.** See [the report][independent].

| Item | Observed state |
|---|---|
| Repository | `C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn` |
| Historical audit source commit | `0203eece29931a8a0306e4b5c46c59228d0864dd` |
| Refreshed source-review commit / HEAD checked | `696695850180fc97f66457a41e86c76dcd330e1e` |
| Upstream change span | 198 commits; 61 changed files; 15,967 insertions and 1,346 deletions |
| Application version | `4.5.0` at both commits; the version label does not identify this change span |
| Application code modifications | None at the start of this documentation task; no application changes are authorized here |
| Existing untracked files | Initially three historical audits and eight handoff documents; this review adds `INDEPENDENT_REVIEW.md`. All remain untracked; no application/test changes |
| Current authorized deliverable | This handoff package under the repository's `docs/composite-subscriptions` directory |
| Implementation branches/commits created by this work | None |
| Live panel/customer changes | None |
| Automated feature test suite | Not implemented; previous audit probes are not a maintained test suite |
| Ready next step | User review of the report, then a separately authorized planning task. D01-D14/deployment evidence remain open; not ready for implementation/deployment |

The earlier attempt to begin implementation was stopped after the user clarified intent. It produced no application/test files. A dependency installation probe was interrupted; no `.test-deps` directory was observed during the original handoff. Do not assume dependencies are installed now. No implementation agents were resumed for this refresh, and no fresh review task was created. User approval to refresh documentation does not approve the open composite business policies.

**Evidence and confidence**

The historical audit at `0203eec` used static source inspection, Python AST route inspection, SQLite schema execution in memory, and isolated execution of selected actual functions with fake HTTP/database dependencies. It did not verify installed A/B/C versions/configuration, customer data, protocol connections, throughput or established-session revocation.

Those historical probes found no explicit composite tables or service uniqueness constraint, no `/sub/` payload route among 390 literal HTTP route declarations, and reproduced error-as-zero usage, false deletion success, missing persistence after a later create failure, and lost conversion fields. The route count and probe outcomes describe that old commit, not a test rerun against HEAD. Their scripts were ad hoc, not maintained repository tests.

The 2026-09-20 review compared the Git diff and targeted AST/source for schema, providers, provisioning, renewal, workers, subscription routes, tenant lifecycle, payment integration and backups. SQLite connection behavior, the base `custom_configs` schema, key 3x-UI create/usage/delete/addressing methods, and `sub_info.py` remain unchanged. No composite schema, unified payload endpoint, or shared-quota worker was found. New best-effort rollback and panel mirrors partially address earlier findings; renewal behavior and reseller lifecycle changed materially. See [UPSTREAM_REVIEW][upstream] for U01-U08 and their acceptance mapping. No application/migration tests or live-panel tests were run for the refresh.

The 2026-09-21 review found HEAD unchanged and empty tracked worktree/index diffs. It reconfirmed U01-U08, qualified renewal reset/read-back, mirror aliases, factory reset, metadata validity and restore boundaries, and corrected package completion dependencies. Isolated actual-function AST probes reproduced error-as-zero traffic, false deletion success, lost VLESS flow and misclassified sing-box REALITY using synthetic in-memory data. A current two-server AST scan found 461 literal HTTP route-like declarations and no `/sub/` payload path. These probes are source evidence, not feature acceptance or deployed compatibility tests.

**Source map for targeted verification**

| Finding | Source anchor |
|---|---|
| Database configured as a SQLite file | [config.py:38][config] |
| Raw SQLite connection, foreign keys, WAL and local locking | [database.py:473][db-connect] |
| One server/username/upstream URL per managed service | [database.py:1043][db-services] |
| Server-level inbound array; one ordinary product provisioning server | [database.py:1431][db-migrations] |
| Existing order claim protects a local status transition | [database.py:3413][db-claim] |
| Direct provisioning now attempts rollback; durable persistence is still after remote creation | [direct_panel_provision.py:34][direct] |
| Web-admin auto-product approval still omits owner/order arguments | [admin_panel/server.py:2200][approval] |
| One identity is attached to all selected inbounds | [threexui_provider.py:167][create] |
| HTTP status-only deletion; application failure may become success | [threexui_provider.py:195][delete] |
| Single-identity traffic; missing error object can become zero | [threexui_provider.py:207][traffic] |
| Inbound-match loop sends email-wide updates without inbound selection in the payload | [threexui_provider.py:299][update] |
| Renewal now distinguishes replacement/carryover; still enables and can reset traffic | [threexui_provider.py:327][provider-renew] |
| Hourly reminders/auto-renewal and the added connection-alert job do not enforce a shared quota | [renewal_reminders.py:284][worker], [bot_manager.py:276][startup], [connect_alerts.py:60][alerts] |
| Service deletion discards local record after remote failure | [miniapp/server.py:6276][mini-delete], [admin_panel/server.py:2675][admin-delete] |
| `/api/sub-info` returns upstream metadata plus connection status; static catch-all remains | [miniapp/server.py:1319][sub-route], [miniapp/server.py:6551][static] |
| Xray conversion omits VLESS flow; sing-box conversion can misclassify REALITY | [sub_info.py:138][xray-conversion], [sub_info.py:190][sing-conversion] |
| Reseller provisioning now supports product inventory and persists a tenant-local panel mirror | [reseller_auto_provision.py:84][reseller], [database.py:6861][mirrors] |
| Manual full renewal requests carryover; automatic renewal uses the replacement default | [renewal_engine.py:39][renewal], [renewal_reminders.py:261][auto-renew] |
| Tier change can purge tenant DB; ownership transfer spans main/local records | [database.py:1930][tier-cleanup], [database.py:4824][ownership] |
| New payment gateways reuse an existing finalizer; self-service has another provisioning path | [extra_gateway_payment.py:302][gateways], [admin_panel/server.py:2779][self-service] |
| Whole-DB SQLite backup and local-instance-only replacement remain; restore accepts old/new ZIP names | [backup.py:29][backup], [database.py:526][replace] |

These source anchors were refreshed to `6966958` in the original checkout. Historical audit files still contain old line numbers; retrieve those sources at `0203eec` when checking historical claims. In another worktree, inspect its corresponding files. Line numbers and assumptions must be rechecked after further updates.

**Audit documents and disagreements**

- [Main audit][audit] contains the historical source-oriented assessment and proposed design; it has not been rewritten to describe HEAD.
- [CODEX-named audit][audit-codex] was text-equivalent to the main audit in the original handoff comparison; line-ending/hash differences do not make it independent corroboration.
- [AGY-named audit][audit-agy] is a separate assessment with illustrative snippets. Preserve it as evidence, but do not treat its schema/code examples as approved implementation.

| Disagreement / trap | Required treatment |
|---|---|
| A raw-counter high-water expression such as `max(raw, previous)` is proposed in one audit | It prevents a decrease but can miss post-reset consumption until the counter catches up. Review a delta/epoch ledger; define unknown usage across unobserved resets. |
| A proposed subscription FK points to `users.id` | Existing order/service ownership commonly stores `users.telegram_id`. Verify every migration mapping; the two IDs are not interchangeable. |
| A proposed endpoint table has `UNIQUE(server_id, email)` | If endpoint rows represent inbound attachments, this cannot represent a legacy email shared across inbounds. Define identity/meter ownership separately from attachment uniqueness. |
| An illustrative endpoint handles VLESS/VMess but not Trojan | The required six-node topology includes Trojan-gRPC. Never mark export complete after silently omitting it. |
| Sample provisioning creates enabled unlimited remote users before durable child intents | Do not adopt this as a fulfillment contract. Design recoverable creation and activation; a DB rollback cannot undo already-created remote clients. |
| Credential rotation is described using the word revoke | Existing rotation issues replacement credentials. Quota expiry/revocation must invalidate access, including retained credentials as specified. |
| Historical and refreshed “full renewal” descriptions differ | At `0203eec` the path added quota then reset usage; at `6966958` manual full renewal requests carryover and automatic renewal defaults to replacement. D09 still governs the composite policy; source behavior is not user approval. |
| Historical missing-persistence findings are treated as entirely fixed or entirely unchanged | Upstream adds best-effort rollback and tenant-local mirrors. It still lacks durable intent/cleanup across every failure; update the evidence rather than discarding the recovery requirements. |
| Current upstream client API is treated as every deployed panel's API | Pin versions and verify fixtures before relying on canonical reads, bulk operations or update scope. |
| Illustrative fan-out uses unrestricted concurrent panel mutations | Bound concurrency and coordinate writes that touch the same identity, inbound or shared panel configuration according to the deployed API's mutation scope. |
| A 3-4 day implementation estimate appears in one report | It is not an accepted schedule. Scope, compatibility, failure policies and test environments remain unsettled. |

**External technical evidence already consulted**

The source audit consulted [3x-UI client API documentation](https://github.com/MHSanaei/3x-ui/blob/main/docs/content/docs/en/reference/api/clients.mdx), [its controller routes](https://github.com/MHSanaei/3x-ui/blob/main/internal/web/controller/client.go), [Xray routing documentation](https://xtls.github.io/en/config/routing.html), and [Xray's user matcher](https://github.com/XTLS/Xray-core/blob/main/app/router/condition.go#L149-L189). They are moving upstream references. They establish leads for version verification, not the installed API/core contract on the user's servers.

**Development environment notes**

The original checkout is on Windows with PowerShell. `py -0p` found no registered Python during the historical audit. Bundled Python at `C:/Users/win 11/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe` was also used for read-only AST/document checks during the refresh. The original runtime lacked `aiohttp`; current application dependency availability has not been verified. A future implementation session should discover its own runtime and use an isolated dependency environment. Read the current [requirements file][requirements-file]; do not install dependencies during the documentation-only next task.

**Package progress**

| Package | Status | Implementation/test evidence |
|---|---|---|
| Original documentation handoff (2026-09-11) | Prepared and reviewed | Seven documents/50 local links checked; original independent document review found no material issues. This is historical evidence, not review of the refresh. |
| Refreshed handoff (2026-09-20) | Prepared; documentation checks passed | Eight documents and 88 local links checked; source anchors, reference definitions, tables, code fences, whitespace and R/D/P/U/A/S identifiers checked. No feature tests. |
| Independent review gate | Complete, 2026-09-21 | [Source-backed report][independent]; U01-U08 confirmed with qualifications; no later local changes; ready for separate planning with blockers recorded |
| P0 design/planning | Not started; separate later task | None; open decisions remain open |
| P1 SQLite foundation | Not started | None |
| P2 panel adapter | Not started | None |
| P3 accounting/lifecycle | Not started | None |
| P4 subscription delivery | Not started | None |
| P5 application integration | Not started | None |
| P6 independent review/staging | Not started | None |

Update this table with actual commits and test results after each authorized task. Make reviewed handoff documents available in the task's starting commit; do not assume untracked files will appear in a new worktree. No Git commit, new Codex task, or deployment is performed by this documentation task.

Historical refresh validation checked eight documents and 88 local link occurrences on 2026-09-20. Independent review validation found no issues across nine documents, 129 local link occurrences and 85 line anchors; reference definitions, fences, whitespace and requirement/decision/acceptance IDs were checked. R01-R08, D01-D14, P0-P6, U01-U08, A01-A33 and S01-S13 retain their IDs. Tracked application/index diffs remain empty. No application integration, migration or staging tests ran; no dependency installation, commit, new Codex task or deployment occurred. Read-only subagents were used only for the authorized review.

[config]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/config.py:38>
[db-connect]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/database.py:473>
[db-services]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/database.py:1043>
[db-migrations]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/database.py:1431>
[db-claim]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/database.py:3413>
[direct]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/direct_panel_provision.py:34>
[approval]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/admin_panel/server.py:2200>
[create]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/panel_providers/threexui_provider.py:167>
[delete]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/panel_providers/threexui_provider.py:195>
[traffic]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/panel_providers/threexui_provider.py:207>
[update]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/panel_providers/threexui_provider.py:299>
[provider-renew]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/panel_providers/threexui_provider.py:327>
[worker]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/renewal_reminders.py:284>
[startup]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/bot_manager.py:276>
[mini-delete]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/miniapp/server.py:6276>
[admin-delete]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/admin_panel/server.py:2675>
[sub-route]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/miniapp/server.py:1319>
[static]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/miniapp/server.py:6551>
[xray-conversion]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/sub_info.py:138>
[sing-conversion]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/sub_info.py:190>
[reseller]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/reseller_auto_provision.py:84>
[renewal]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/renewal_engine.py:39>
[auto-renew]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/renewal_reminders.py:261>
[audit]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/COMPOSITE_SUBSCRIPTION_AUDIT.md>
[audit-codex]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/COMPOSITE_SUBSCRIPTION_AUDIT-CODEX.md>
[audit-agy]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/COMPOSITE_SUBSCRIPTION_AUDIT-AGY.md>
[requirements-file]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/requirements.txt>
[upstream]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/docs/composite-subscriptions/UPSTREAM_REVIEW.md>
[alerts]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/connect_alerts.py:60>
[mirrors]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/database.py:6861>
[tier-cleanup]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/database.py:1930>
[ownership]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/database.py:4824>
[gateways]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/extra_gateway_payment.py:302>
[self-service]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/admin_panel/server.py:2779>
[backup]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/backup.py:29>
[replace]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/database.py:526>
[independent]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/docs/composite-subscriptions/INDEPENDENT_REVIEW.md>
