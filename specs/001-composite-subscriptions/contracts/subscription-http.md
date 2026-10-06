# Public composite subscription contract

**Proposed service:** `composite/subscription_server.py`, separate FastAPI/uvicorn process behind owner-prepared HTTPS/domain. No route exists in current code. This is independent of optional Mini App/admin and Telegram authentication after fulfillment. It reads authoritative state using SQLite read-only snapshots and cannot send panel/payment mutations. Information-entry URI encoding remains **G-C provisional**; the semantic response/gating contract is fixed.

## Request and token handling

`GET /sub/{token}` accepts an opaque 256-bit random base64url token (43 unpadded characters); token digest identifies one main-store subscription/current token generation. No tenant/user/panel selector or credential query parameter is accepted. Knowledge grants download only, no account details or management. `HEAD` applies identical gates without body. Unknown/malformed/revoked/superseded tokens return the same opaque404 with no real authentication/other identity/replacement secret. No redirect to new URL. Unsupported methods return405.

Provider API URLs/tokens, raw owner audit/evidence and unrelated customer information never appear. Store base URL is owner-prepared HTTPS configuration validated without credentials in logs. Public service uses authorized decryption key for only necessary export rendering; main DB secrets otherwise inaccessible through handlers. Proxy/app/metrics redact full token-bearing path and body; use non-secret request/record identifiers. Credentials/URLs excluded from analytics, general exception messages and source-controlled fixtures. `Referrer-Policy: no-referrer`, `Cache-Control: no-store, private`; no shared CDN payload cache or stale-success fallback that could defeat suspension/revocation/recovery gates.

## Gate order and response

Evaluate current token/subscription/recovery/restriction/generation state in a fresh transaction on every request. Never serve a cached body before current gates; cache encrypted complete real generation, not final unrestricted response. A concurrently accepted restriction wins subsequent gate snapshots; a previously downloaded payload cannot be recalled and remote revocation remains separate.

| Priority | Condition | Response |
| --- | --- | --- |
| 1 | Unknown/invalidated/revoked/superseded token or permanently final-cancelled service | Opaque404; no usable subscription, real child or replacement secret/redirect. |
| 2 | Unfulfilled, initial delivery blocked, pending leak new delivery, or unverified recovery ownership/current token/generation |503 temporary unavailability/support with no real credentials; a still-valid known owner suspension may show safe known status only when ownership/token are verified. Hold must not publish stale generation. |
| 3 | Valid verified owner-suspended subscription |200 Base64 information entries only, from accepted owner suspension even if remote disable pending. No real child secret/private reason. Known expiry/qualified allowance/support and honest requested/partial/confirmed restriction. |
| 4 | Fulfilled token with verified complete current generation, including ordinary panel-management outage, stale-reporting suspension, expiry, exhaustion or customer disable |200 complete current real-node list plus information entries. Never omit failed/offline/inactive nodes. Explain freshness and restriction/pending native exposure; download success ≠ VPN availability. |
| 5 | Otherwise no trustworthy complete current configuration |503 temporary unavailability, no empty/partial/invented real success. |

Owner release clears owner restriction only and returns permitted full list on same URL subject to higher gates. Initial terminal timeout/initial cancellation never exposes late created credentials. Leak old token never reveals new token. Equivalent move changes only fully ready current descriptors and preserves token; during pending move use verified permissible prior generation if gates allow, never mixed partial new nodes.

## Body and exact real-node export

Successful responses have `Content-Type: text/plain; charset=utf-8`, ASCII standard Base64 of UTF-8 newline-separated URI strings, deterministic LF order and a final newline before Base64 encoding. Do not switch to native YAML/JSON or a supported raw-text alternative by client user-agent. One real URI per owner-configured intended node, stable saved ordinal/remark; info entries are separate. Endpoint does not refetch provider links. Complete-generation content fingerprints bind descriptor+child authentication+version, and all required fields were verified before publication.

Paid/test allowance remains one parent; five A-only real entries versus six fixture real entries are unrelated to headers or informational count. Real URIs retain actual VLESS flow/REALITY keys/short ID/SNI/fingerprint, WS host/path/CDN endpoint, Trojan password/gRPC service/mode, and VMess TCP/TLS parameters from prepared settings. Do not select first native address, substitute defaults or invent missing fields. Strict export failure blocks readiness rather than serving a smaller list.

Select three semantic information categories: store/support status, known expiry, and shared remaining allowance+source timestamp/qualification. Actual count/row placement may vary where validated client parsers require it; incidental screenshot values are not acceptance. Format shop values using explicit GiB/MiB with binary explanation in Telegram/admin; third-party labels do not change purchased bytes. Show UTC time with explicit zone in imported snapshots; customer/admin localization can additionally use configured shop zone without changing absolute terms. Precision must not represent remaining value higher than exact remaining bytes; use a conservative decimal rendering, with exact bytes accessible in Telegram/admin details.

Current usage uses oldest required trustworthy source timestamp, every required meter≤60seconds plus reconciled history. Known failure or61seconds warns immediately. Retain last reliable whole-subscription balance with genuine as-of time; absent trustworthy whole figure is `unknown`, never zero/full/unlimited. Owner usage settlement shows settlement-based available allowance and unknown historical gap. Retired emergency exposure is qualified separately, not fresh serving meter. Imported names stay snapshots until client refresh, never live pushes. Known expiry is independently shown.

Omit optional numeric `Subscription-Userinfo` quota headers in the baseline design to avoid another unsupported unit/freshness interpretation; required information is in displayed names. Any later header addition needs the same trustworthy-source contract and five-client validation, not default-zero substitution. No optional header creates enforcement or current-connection claims.

**G-C gate:** No primary evidence establishes one safe universally imported non-working information URI across the required five apps. Do not pick a loopback/reserved-address/synthetic-auth URI solely because it parses or appears in a screenshot. Earliest authorized check must show accepted info rows, owner-suspension-only refresh and manual/automatic selection consequences without real credentials/endpoints. A concrete wire encoding can then be bound and recorded; until then dependent renderer design is provisional. Unknown encoded details do not defer this launch behavior or authorize dropping an app/row requirement.

## Availability and side-effect guarantees

GET/HEAD never provisions, enables, renews, resets, clears restrictions, credits money, calls a panel, updates true sample time or acknowledges an operation. Access/request logging is sanitized and does not alter domain state. Bot/Telegram/optional UI loss after fulfillment does not invalidate token; worker loss preserves last complete public generation and honestly stale accounting. Endpoint/HTTPS/domain/database/key outage is explicit503/unavailability, not advertised continuous uptime. No external URL-domain failover is assumed.

Offline tests decode deterministic output and all-node exact fields, gate precedence/secret leakage, changed generation/suspension race, no write capability/network effect, retained list during declared outages and unknown/stale usage. Controlled E-003 records exact versions/platforms/cores for v2rayNG, NekoBox, Streisand, V2Box and v2rayN, six real handshakes/traffic/egress, import/refresh/order/remarks, info selection/status-only outcomes and cleanup. Those checks are not run here.
