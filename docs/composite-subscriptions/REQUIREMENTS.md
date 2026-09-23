# Requirements and scope

**Purpose:** preserve the user's requested behavior without treating suggested implementation details as approved decisions. Implementation remains paused. Read [the decision register][decisions] before choosing business policies or a physical schema.

Refreshed 2026-09-20 against the source baseline recorded in [STATUS][status]. R01-R08 and the six-node topology are unchanged. Upstream renewal/reseller behavior documented in [UPSTREAM_REVIEW][upstream] is a compatibility input; it does not settle the composite business policies.

**Agreed product requirements and constraints**

| ID | Requirement |
|---|---|
| R01 | Keep SQLite for this feature. PostgreSQL migration is deferred to a separate upgrade. |
| R02 | A purchased subscription owns an arbitrary collection of child credentials across multiple 3x-UI panel instances. The six-node example is an acceptance fixture, not a hardcoded limit. |
| R03 | Several child credentials of the same subscription may use the same server and inbound with different UUIDs/passwords and routing identities. |
| R04 | Server A uses one REALITY inbound on public port 443 in the described Steal-Oneself deployment. Do not introduce additional public VPN listeners or an L4 reverse proxy to implement the feature. |
| R05 | A subscriber receives one subscription URL and sees all six intended nodes with distinct descriptive remarks after refresh in the supported client applications. v2rayNG, NekoBox, and Streisand are named targets; exact versions must be established. |
| R06 | The purchased quota is shared across the child credentials; usage on one child reduces the remaining allowance everywhere. The quota is not multiplied by the number of children. |
| R07 | Quota exhaustion or expiry requires disabling/deleting every associated credential across A/B/C. The achievable enforcement timing during network/API failures is an unresolved operational contract, not a promise of instantaneous distributed action. |
| R08 | Preserve this work as staged, reviewable tasks in fresh sessions. The independent review gate verifies findings, checks later changes, corrects docs and assesses viability, then stops (completed 2026-09-21). A separate later agent performs design/planning and authorized implementation after the user reviews the result and requests that work. Do not combine the review gate with P0 or start the entire feature in one unbounded coding session. |

**Required example**

One user, Ali, purchases one nominal 50-GB plan for 30 days. GB versus GiB and the exact start/renewal boundary need explicit decisions; the existing code uses binary GiB conversion.

| Child | Panel/inbound | Separate credential | Server-side egress | Display remark |
|---|---|---|---|---|
| A-US | A / the REALITY inbound on 443 | Email `ali_sub1_us`, UUID A1 | US outbound | 🇺🇸 US - Reality |
| A-DE | A / the same inbound | Email `ali_sub1_de`, UUID A2 | DE outbound | 🇩🇪 DE - Reality |
| A-RU | A / the same inbound | Email `ali_sub1_ru`, UUID A3 | RU outbound | 🇷🇺 RU - Reality |
| B-CDN | B / inbound 1, VLESS-WS-CDN | Independent email and VLESS UUID | B's configured route | Server B - CDN |
| B-gRPC | B / inbound 2, Trojan-gRPC | Independent email and Trojan password | B's configured route | Server B - gRPC |
| C-Direct | C / inbound 1, VMess-TCP-TLS | Independent email and VMess UUID | Direct | Server C - Direct |

For these independent accounting identities:

```text
consumed = A_US + A_DE + A_RU + B_CDN + B_gRPC + C_Direct
remaining = max(0, purchased_quota - consumed)
```

Each contribution includes upload and download according to the accepted billing definition. Do not add the same traffic counter twice if a panel reports one shared counter on multiple inbound attachments. Do not include infrastructure tunnel overhead a second time in customer usage without an explicit billing decision.

**Terminology**

- A **subscription** is the purchased entitlement: owner, quota, validity period and one subscription URL.
- A **child client** is an independently managed remote authentication identity. UUIDs apply to VLESS/VMess; Trojan uses a protocol password. Display names are not authentication identities.
- An **inbound** is the panel/Xray listener and protocol configuration that accepts clients. Identify it by its panel/server and remote inbound ID; an inbound number alone is not globally unique.
- An **outbound** is a shared egress configuration. Creating another subscriber does not require cloning the same country outbound.
- A **node** is an entry in the exported subscription. Its display count is not automatically the number of distinct accounting counters, especially for legacy shared identities.
- A **meter** is an accounting identity whose upload/download increments must be charged exactly once. It may be modeled separately; the physical representation is a design decision.

For 100 subscribers, A has 1 inbound, 300 client identities, and 3 shared country outbounds. Three grouped email rules can select those outbounds. Current Xray also documents email regex matching; whether to use static patterns depends on deployed-version support and naming policy. Grouped rules are not automatically constant-time lookups. [Xray routing](https://xtls.github.io/en/config/routing.html), [user matcher source](https://github.com/XTLS/Xray-core/blob/main/app/router/condition.go#L149-L189).

**Correctness requirements for the implementation design**

These express the reliability needed to deliver R02-R07; they do not mandate particular table names or worker libraries.

1. Persist intended child identities and ownership before remote creation. Retrying an ambiguous timeout must reconcile the intended identity instead of creating unrelated replacement credentials.
2. Preserve accumulated traffic through API failures, restarts, credential changes and controlled counter resets. Missing/error responses must not become valid zero samples.
3. Make concurrent lifecycle operations deterministic. An old enable/renewal task must not undo a newer revocation.
4. Retain management records and pending cleanup until remote revocation is confirmed. Hiding a link or deleting a database row does not revoke credentials already imported into an app.
5. Treat subscription quantity separately from child count. Two purchased units ordinarily mean two entitlements, not one entitlement charged twice or twelve quota allocations for one user.
6. Keep plan templates separate from sold topology. Product edits must not silently change existing subscriptions unless an explicit migration is requested.
7. Preserve the existing single-panel and stock-link workflows while adding composites. Do not introduce unrelated payment/business-policy changes through the implementation.
8. Preserve tenant ownership. Telegram IDs, internal user row IDs, local reseller databases, and main-registry server IDs must not be interchanged.
9. Export all required protocol/transport/security fields and route A's credentials to the intended outbounds. A country flag alone does not select egress.
10. Preserve responsibility for remote credentials through reseller tier changes, ownership transfers, tenant deletion, database purge and in-place factory reset. Pending cleanup and its owner/panel dependencies must survive removal or clearing of the database that previously owned them; the transfer/revoke/reset policy remains open.
11. Cover every tenant approved for composite sales, including tenants without a live Telegram bot. Hiding an admin panel or Mini App must not inadvertently stop quota/expiry enforcement. Local panel mirrors must not cause missed clients or duplicate accounting of a remote meter.
12. Define backup and restore as recovery of both local records and their relationship to live panels. Include subscription tokens, child identities, usage history, billing boundaries, and pending operations in the owning database backups. Old snapshots must not be treated as proof of current allowance or current remote state. Unrecoverable history remains explicit uncertainty.

**Scope boundaries**

PostgreSQL migration, a rewrite of the whole bot, additional A listeners, and L4 proxy infrastructure are outside this feature. Future support for other panel brands is not implied by the current 3x-UI target; existing providers must still work.

The original audit request mentions Base64, Clash and sing-box. No initial format has been removed from scope by user approval. Determine release coverage in D05; do not silently substitute a Base64-only implementation or claim that structurally valid export proves compatibility with every named application/core version.

Whether the bot should create/modify Xray routing rules, merely verify preconfigured rules, or generate an administrator-applied configuration remains open. So do the treatment of existing services, composite custom/test/reseller products, renewal semantics, public endpoint hosting and outage enforcement policy. See [DECISIONS][decisions].

Backup compatibility belongs to this feature's recovery design. The existing bot backup contains SQLite databases, not a complete copy of remote 3x-UI/Xray infrastructure or external HTTPS/domain configuration. Define those prerequisites in the recovery procedure; building a general infrastructure-backup service is not implicitly in scope. New upstream panel providers remain legacy compatibility targets, not additional composite panel brands approved for this release.

[decisions]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/docs/composite-subscriptions/DECISIONS.md>
[status]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/docs/composite-subscriptions/STATUS.md>
[upstream]: <C:/Users/win 11/Desktop/Workstuff/Workspace/Telegram/fork-of-shopvpn/Shopvpn/docs/composite-subscriptions/UPSTREAM_REVIEW.md>
