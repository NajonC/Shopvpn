# T047a verification evidence

Accepted test-only verification. Baseline commit bc72ebc; no production or existing test modifications.

Production targeted run: 18 intended missing-T048 API failures; identities/reasons in expected_failures.json.

- Reference/mutation command session: 94546; deadline 3 minutes; log /tmp/shopvpn-t047a-mutations.wSi1b8.log.
- Full offline command session: 62649; deadline 20 minutes; log /tmp/shopvpn-t047a-offline.2zOZT5.log; JUnit /tmp/shopvpn-t047a-offline.2zOZT5.xml.
- Completed statuses retrieved: mutation runner exit 0; full offline runner exit 1 solely for the declared test-only failures.

Source hashes at both launches:

- `tests/integration/test_authority_matrix.py`: `b9976880256bc73be12d64f6df190b4d2022358c5dc9aeb53af697e40190cdb7`
- `specs/001-composite-subscriptions/briefs/review/T047a/reference_service.py`: `aee30484b4de8e09569aebc720569d52fa482c63384368646916ed7fa35302dc`
- `specs/001-composite-subscriptions/briefs/review/T047a/verify.py`: `ba7aa3475cec3fee3a0e7d4ca39259a1e17f53deffc30d4a55acc1fab6f048b2`

## Results

- Reference: all 18 new cases passed.
- Mutations: 17 killed, no survivors, invalid runs or unresolved cases. Each edit applied once and started from the unmodified reference; failures are relevant assertions/expected AuthorityError outcomes.
- Full offline suite: 2964 passed, 18 expected failures, 512 inherited warnings, 565.57 seconds. Parsed JUnit confirms exact equality of failure IDs and reasons with expected_failures.json; no skips, collection errors or fixture errors. All 18 missing APIs belong to T048.
- Protected-file comparison: all 352 pre-packet tracked hashes unchanged before acceptance bookkeeping. Tests/reference/runner hashes match launch records.
- Scratch: no t047a-review directories remain. Durable reference and runner retained; raw logs/XML remain outside the repository.
- Review: all new source lines inspected; no production changes, dependencies, network calls or real secrets. No test corrections or equivalent-mutant exceptions.

## Mutation dispositions

- `callback_message_actor`: **killed** by `test_forged_callback_actor_cannot_manage_message_actor_resource`.
- `payload_actor`: **killed** by `test_forged_callback_actor_cannot_manage_message_actor_resource`.
- `payload_tenant`: **killed** by `test_own_resources_allowed_despite_untrusted_selectors_or_buyer_status[False-False]`, `test_own_resources_allowed_despite_untrusted_selectors_or_buyer_status[True-False]`, `test_own_resources_allowed_despite_untrusted_selectors_or_buyer_status[False-True]`, `test_own_resources_allowed_despite_untrusted_selectors_or_buyer_status[True-True]`.
- `main_tenant_hardcoded`: **killed** by `test_non_main_transport_cannot_manage_main_or_own_tenant_resource[own]`, `test_non_main_transport_cannot_manage_main_or_own_tenant_resource[foreign]`.
- `missing_actor_fallback`: **killed** by `test_missing_authenticated_sender_never_falls_back_to_payload_or_message[None]`, `test_missing_authenticated_sender_never_falls_back_to_payload_or_message[sender1]`.
- `omit_customer_ownership`: **killed** by `test_forged_callback_actor_cannot_manage_message_actor_resource`.
- `omit_resource_tenant`: **killed** by `test_cross_tenant_resource_refused_even_when_customer_ids_match`.
- `allow_non_main`: **killed** by `test_non_main_transport_cannot_manage_main_or_own_tenant_resource[foreign]`.
- `omit_domain`: **killed** by `test_matching_numeric_id_cannot_replace_customer_domain_interface_or_role[identity_domain-web_admin]`, `test_matching_numeric_id_cannot_replace_customer_domain_interface_or_role[identity_domain-subscription_url]`.
- `omit_interface`: **killed** by `test_matching_numeric_id_cannot_replace_customer_domain_interface_or_role[authenticated_interface-miniapp]`.
- `omit_role`: **killed** by `test_matching_numeric_id_cannot_replace_customer_domain_interface_or_role[role-owner]`.
- `reverse_ownership`: **killed** by `test_own_resources_allowed_despite_untrusted_selectors_or_buyer_status[False-False]`, `test_own_resources_allowed_despite_untrusted_selectors_or_buyer_status[True-False]`, `test_own_resources_allowed_despite_untrusted_selectors_or_buyer_status[False-True]`, `test_own_resources_allowed_despite_untrusted_selectors_or_buyer_status[True-True]`.
- `reject_payload_mismatch`: **killed** by `test_own_resources_allowed_despite_untrusted_selectors_or_buyer_status[False-False]`, `test_own_resources_allowed_despite_untrusted_selectors_or_buyer_status[True-False]`, `test_own_resources_allowed_despite_untrusted_selectors_or_buyer_status[False-True]`, `test_own_resources_allowed_despite_untrusted_selectors_or_buyer_status[True-True]`.
- `reject_reseller_buyer`: **killed** by `test_own_resources_allowed_despite_untrusted_selectors_or_buyer_status[True-False]`, `test_own_resources_allowed_despite_untrusted_selectors_or_buyer_status[True-True]`.
- `reject_discount_buyer`: **killed** by `test_own_resources_allowed_despite_untrusted_selectors_or_buyer_status[False-True]`, `test_own_resources_allowed_despite_untrusted_selectors_or_buyer_status[True-True]`.
- `hardcode_owner`: **killed** by `test_ownership_is_not_hardcoded_to_fixture_actor[202]`, `test_ownership_is_not_hardcoded_to_fixture_actor[303]`.
- `leak_target_in_error`: **killed** by `test_cross_tenant_resource_refused_even_when_customer_ids_match`.

## Reproduction and limits

Run `.venv/bin/python specs/001-composite-subscriptions/briefs/review/T047a/verify.py` from the repository root at this packet revision. It builds a source-only temporary export and uses the real tests/offline harness with reference service code. For production failures run `.venv/bin/python -m pytest tests/integration/test_authority_matrix.py --network=deny -q`; expected IDs/reasons are recorded separately.

This proves tests distinguish the specified adapter/guard behavior. The SQLite sink demonstrates composition before synthetic effects, not implementation of future command bodies, web routes, transport authenticity or shop eligibility. T048 must implement the guard and rerun adapted mutations; subsequent adapter/command tasks must verify they invoke it before real effects. T047b remains responsible for web-auth/owner mapping, signed-tenant, mobile, CSRF and HTTP URL-bearer cases.
