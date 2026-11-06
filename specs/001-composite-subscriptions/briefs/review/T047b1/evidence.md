# T047b1 verification evidence

Source baseline: `68e6fca52eba0888cb80dc6b6778d0ec0196761d`, plus the appended authority tests. Actual orchestrator: gpt-6-astra/xhigh; no coder. This is offline test-only evidence, not HTTP route or deployed-service acceptance.

## Production targeted result

Session 31636: 40 cases collected, 3 existing-authentication passes, 37 declared missing-T048 API failures (18 inherited T047a, 19 new). No setup/collection errors or skips. Exact IDs/reasons in `expected_failures.json`. Command: `.venv/bin/python -m pytest tests/integration/test_authority_matrix.py --network=deny -q --tb=line --junitxml=/tmp/t047b1-final-targeted.xml`; exit 1 only for these expected failures.

## Reference and mutations

Session 64684 completed exit 0 under `timeout --kill-after=15s 5m .venv/bin/python specs/001-composite-subscriptions/briefs/review/T047b1/verify.py`; raw log `/tmp/t047b1-mutations.BHxdSL.log`.

All 22 new cases pass against the executable web reference and real inherited auth/DB code. All 18 inherited cases pass against the supporting T047a reference. All 21 behavior-changing mutants were detected by relevant tests, with no survivors or invalid runs. Source hashes match the working tree after completion. Temporary scratch copies were removed.

| Mutation | Disposition | Relevant failing test IDs (in test_authority_matrix.py) |
| --- | --- | --- |
| omit_tenant | killed | `test_web_signed_tenant_cannot_be_replaced_by_main_selector[reseller-owner]`, `test_web_signed_tenant_cannot_be_replaced_by_main_selector[full-access-tenant]` |
| missing_tenant_is_main | killed | `test_web_adapter_refuses_incomplete_or_wrong_authentication_domain[missing-tenant]` |
| accept_main_alias | killed | `test_web_adapter_refuses_incomplete_or_wrong_authentication_domain[main-alias]` |
| omit_role | killed | `test_web_database_staff_role_cannot_be_replaced_by_signed_owner_claim[orders-permission]`, `test_web_database_staff_role_cannot_be_replaced_by_signed_owner_claim[admin-permissions]` |
| omit_mobile | killed | `test_web_adapter_refuses_incomplete_or_wrong_authentication_domain[mobile-identity]` |
| coerce_actor | killed | `test_web_adapter_refuses_incomplete_or_wrong_authentication_domain[bool-id]` |
| coerce_mapping | killed | `test_web_mapping_must_be_explicit_valid_web_id[True]` |
| omit_mapping | killed | `test_web_telegram_owner_number_does_not_authorize_unmapped_web_owner` |
| telegram_id_fallback | killed | `test_web_telegram_owner_number_does_not_authorize_unmapped_web_owner` |
| wrong_domain | killed | `test_web_explicit_owner_mapping_preserves_web_domain_and_configured_identity[1-synthetic-main-installation]`, `test_web_explicit_owner_mapping_preserves_web_domain_and_configured_identity[2-synthetic-main-second]` |
| wrong_interface | killed | `test_web_explicit_owner_mapping_preserves_web_domain_and_configured_identity[1-synthetic-main-installation]`, `test_web_explicit_owner_mapping_preserves_web_domain_and_configured_identity[2-synthetic-main-second]` |
| wrong_role | killed | `test_web_explicit_owner_mapping_preserves_web_domain_and_configured_identity[1-synthetic-main-installation]`, `test_web_explicit_owner_mapping_preserves_web_domain_and_configured_identity[2-synthetic-main-second]` |
| hardcode_web_actor | killed | `test_web_explicit_owner_mapping_preserves_web_domain_and_configured_identity[2-synthetic-main-second]` |
| hardcode_installation | killed | `test_web_explicit_owner_mapping_preserves_web_domain_and_configured_identity[2-synthetic-main-second]` |
| reject_alternative_owner | killed | `test_web_explicit_owner_mapping_preserves_web_domain_and_configured_identity[2-synthetic-main-second]` |
| leak_web_id | killed | `test_web_telegram_owner_number_does_not_authorize_unmapped_web_owner` |
| trust_query_tenant | killed | `test_web_signed_tenant_cannot_be_replaced_by_main_selector[reseller-owner]`, `test_web_signed_tenant_cannot_be_replaced_by_main_selector[full-access-tenant]` |
| trust_signed_role | killed | `test_web_database_staff_role_cannot_be_replaced_by_signed_owner_claim[orders-permission]`, `test_web_database_staff_role_cannot_be_replaced_by_signed_owner_claim[admin-permissions]` |
| omit_session_signature | killed | `test_web_invalid_session_never_reaches_principal_or_effect[tampered]` |
| omit_session_expiry | killed | `test_web_invalid_session_never_reaches_principal_or_effect[expired]` |
| allow_inactive_session | killed | `test_web_invalid_session_never_reaches_principal_or_effect[inactive]` |

## Provenance

```text
SHA256 tests/integration/test_authority_matrix.py: 1e22b5fd47edb99f6daa3ae6dabd8a8ea9a8a9779f721eb5fd315ab2c6d7e989
SHA256 specs/001-composite-subscriptions/briefs/review/T047b1/reference_web.py: a5dc5cabc3acee5729b46921a21a32d0fcf34eea11db8c7a00a228995c4bebac
SHA256 specs/001-composite-subscriptions/briefs/review/T047b1/verify.py: aaa6c62581d8f3c742adad2fcbc1f98449dc9daecef7568d49ea8557efff9c6f
SHA256 specs/001-composite-subscriptions/briefs/review/T047a/reference_service.py: aee30484b4de8e09569aebc720569d52fa482c63384368646916ed7fa35302dc
SHA256 admin_panel/server.py: 4a3b40f3d8fc2927b01e8a40c82f2dd8f660936e34af4ed099fc19267ae264a7
SHA256 admin_panel/security.py: d37d94910902907f9362cca31ade66d65d7a92f88312bd3eae85abb2e6b39746
```

## Corrections and limitations

The initial reference run correctly exposed a fixture error: the legacy deactivation helper refuses owner rows. The corrected test seeds the inactive synthetic row directly and asserts that precondition before authentication. It preserves the intended 401 expectation and changes no production code. The corrected reference baseline and campaign both pass.

The SQLite sink witnesses adapter-before-effect composition only. T048 must apply the mutations to real implementation; T047b2/T049 must separately exercise the router, same-origin/CSRF and actual mobile/URL bearer requests. Trusted owner mapping is a test-supplied configuration binding, not an actual deployment identity. Source-only scratch export excludes credentials, environment files and runtime databases; all database activity is isolated by the offline harness.

## Full offline suite

Session 19849 completed exit 1 in 570.33 s under the 20-minute deadline: **2967 passed, exactly 37 declared T048 missing-API failures**, 534 inherited warnings. No setup/collection errors or skips. All failure identities and messages exactly match expected_failures.json; the 18 inherited cases remain unchanged and the 19 new failures are assigned to T048. No passing-test regression. Logs: `/tmp/t047b1-offline.uDd2vH.log`, XML `/tmp/t047b1-final-offline.xml`.

Command: `timeout --kill-after=15s 20m .venv/bin/python -m pytest tests/characterization tests/unit tests/contract tests/integration tests/acceptance --network=deny -q --tb=line --junitxml=/tmp/t047b1-final-offline.xml`.

Protected tracked hashes still match the pre-packet snapshot except the deliberately appended authority tests; the prior test content is preserved as an exact prefix. Production remains unimplemented. All new source and evidence reviewed; no required packet checks remain pending. T047 remains incomplete until T047b2 is accepted.
