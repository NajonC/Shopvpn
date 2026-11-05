# T046 independent verification

Actual orchestrator: gpt-6.1-sol/high. Coder: antigravity/gemini-3.8-flash-high, options []; one round. Source baseline fd9050f, implementation branch. Checklist 26/26 passed; no extensions.yml/hook or task gate. No real services used.

## Scope and protected files

Before packet edits the checkout was clean. `snapshot.json` records HEAD and SHA-256 hashes of all tracked files (including staged orchestrator tests) immediately before delegation. `status.txt`, `staged.diff`, `unstaged.diff` retain that snapshot. After completion only composite/audit.py differs from the manifest; no existing or orchestrator-owned test changed, staged or unstaged. Coder reported no concerns. Every added production/test line was reviewed.

## Independent checks

- New tests before implementation: 12 writer failures and the two inherited diagnostic failures, all verified via JUnit as missing AuditEvent, AuditWriteError, write_audit_event or sanitized_diagnostic; 20 existing secret cases passed. No collection/setup failures.
- `tests/unit/test_audit_writer.py tests/unit/test_secrets_and_audit.py tests/unit/test_secrets_failures.py --network=deny -q`: 40 passed.
- `tests/integration/test_migrations.py --network=deny -q -k audit`: 53 passed, 1767 deselected.
- Full pre-packet baseline: 2950 passed, exactly the two declared missing-diagnostic failures, 512 inherited warnings in 636.12 s. Collected before the new writer tests were created and before the coder edited audit.py. This matches the accepted T045 baseline.
- Final full offline regression: **2964 passed, zero failures, 512 inherited warnings in 631.38 s**. Command: `.venv/bin/python -m pytest tests/characterization tests/unit tests/contract tests/integration tests/acceptance --network=deny -q`. Both inherited T046 diagnostic failures now pass, all 12 new writer cases pass, no regression. Protected hashes rechecked after full suite: audit.py is the sole changed tracked file against the pre-delegation manifest. No skips/xfails introduced.

## Mutation checks

Reproduce from repo root with `.venv/bin/python specs/001-composite-subscriptions/briefs/review/T046/verify.py`. Runner exports only explicitly named source/tests and the synthetic harness to a unique TemporaryDirectory, checks imports resolve into scratch, denies network, starts every independent mutant from clean source, checks edit match counts and compiles it, and requires relevant behavior failures from JUnit. No production configuration, DBs, keys, .git or real data copied. Scratch removed on exit. Underlying no-update/no-delete DDL mutants supplement writer API mutants without changing shared DDL.

All 27 mutants killed on the first campaign; no equivalents, survivors, invalid runs or unresolved checks. Baseline 34 cases passed before mutation. No production correction required. Brief typo corrected from eleven to ten SQL columns; implementation and named fields were already correct.

```text
REAL IMPLEMENTATION BASELINE: 34 passed
{"mutation": "wrong_event_id", "disposition": "killed", "tests": ["test_write_retains_exact_metadata[telegram]", "test_write_retains_exact_metadata[web_admin]", "test_write_retains_exact_metadata[payment_callback]", "test_write_retains_exact_metadata[system]", "test_write_retains_exact_metadata[cli]"]}
{"mutation": "wrong_occurred_at", "disposition": "killed", "tests": ["test_write_retains_exact_metadata[telegram]", "test_write_retains_exact_metadata[web_admin]", "test_write_retains_exact_metadata[payment_callback]", "test_write_retains_exact_metadata[system]", "test_write_retains_exact_metadata[cli]"]}
{"mutation": "wrong_actor_domain", "disposition": "killed", "tests": ["test_write_retains_exact_metadata[telegram]", "test_write_retains_exact_metadata[web_admin]", "test_write_retains_exact_metadata[payment_callback]", "test_write_retains_exact_metadata[cli]"]}
{"mutation": "wrong_actor_id", "disposition": "killed", "tests": ["test_write_retains_exact_metadata[telegram]", "test_write_retains_exact_metadata[web_admin]", "test_write_retains_exact_metadata[payment_callback]", "test_write_retains_exact_metadata[system]", "test_write_retains_exact_metadata[cli]"]}
{"mutation": "wrong_action", "disposition": "killed", "tests": ["test_write_retains_exact_metadata[telegram]", "test_write_retains_exact_metadata[web_admin]", "test_write_retains_exact_metadata[payment_callback]", "test_write_retains_exact_metadata[system]", "test_write_retains_exact_metadata[cli]"]}
{"mutation": "wrong_resource_kind", "disposition": "killed", "tests": ["test_write_retains_exact_metadata[telegram]", "test_write_retains_exact_metadata[web_admin]", "test_write_retains_exact_metadata[payment_callback]", "test_write_retains_exact_metadata[system]", "test_write_retains_exact_metadata[cli]"]}
{"mutation": "wrong_resource_id", "disposition": "killed", "tests": ["test_write_retains_exact_metadata[telegram]", "test_write_retains_exact_metadata[web_admin]", "test_write_retains_exact_metadata[payment_callback]", "test_write_retains_exact_metadata[system]", "test_write_retains_exact_metadata[cli]"]}
{"mutation": "wrong_reason", "disposition": "killed", "tests": ["test_write_retains_exact_metadata[telegram]", "test_write_retains_exact_metadata[web_admin]", "test_write_retains_exact_metadata[payment_callback]", "test_write_retains_exact_metadata[system]", "test_write_retains_exact_metadata[cli]"]}
{"mutation": "wrong_evidence_ref", "disposition": "killed", "tests": ["test_write_retains_exact_metadata[telegram]", "test_write_retains_exact_metadata[web_admin]", "test_write_retains_exact_metadata[payment_callback]", "test_write_retains_exact_metadata[system]", "test_write_retains_exact_metadata[cli]"]}
{"mutation": "frozen_event", "disposition": "killed", "tests": ["test_write_retains_exact_metadata[telegram]", "test_write_retains_exact_metadata[web_admin]", "test_write_retains_exact_metadata[payment_callback]", "test_write_retains_exact_metadata[system]", "test_write_retains_exact_metadata[cli]"]}
{"mutation": "refuse_system", "disposition": "killed", "tests": ["test_write_retains_exact_metadata[system]"]}
{"mutation": "refuse_null_reason", "disposition": "killed", "tests": ["test_optional_metadata_and_distinct_event_ids"]}
{"mutation": "omit_insert", "disposition": "killed", "tests": ["test_write_retains_exact_metadata[telegram]", "test_write_retains_exact_metadata[web_admin]", "test_write_retains_exact_metadata[payment_callback]", "test_write_retains_exact_metadata[system]", "test_write_retains_exact_metadata[cli]"]}
{"mutation": "ignore_duplicate", "disposition": "killed", "tests": ["test_duplicate_is_explicit_failure_and_does_not_replace"]}
{"mutation": "replace_duplicate", "disposition": "killed", "tests": ["test_duplicate_is_explicit_failure_and_does_not_replace"]}
{"mutation": "commit_write", "disposition": "killed", "tests": ["test_writer_does_not_commit_or_rollback_caller_work"]}
{"mutation": "rollback_error", "disposition": "killed", "tests": ["test_duplicate_is_explicit_failure_and_does_not_replace"]}
{"mutation": "diagnostic_missing_id", "disposition": "killed", "tests": ["test_diagnostic_contains_only_operation_tenant_record[False]", "test_diagnostic_contains_only_operation_tenant_record[True]"]}
{"mutation": "diagnostic_claims_success", "disposition": "killed", "tests": ["test_diagnostic_contains_only_operation_tenant_record[False]", "test_diagnostic_contains_only_operation_tenant_record[True]"]}
{"mutation": "diagnostic_error_text", "disposition": "killed", "tests": ["test_diagnostic_contains_only_operation_tenant_record[False]", "test_diagnostic_contains_only_operation_tenant_record[True]"]}
{"mutation": "stored_extra_fields", "disposition": "killed", "tests": ["test_writer_sanitizes_persisted_diagnostics"]}
{"mutation": "stored_missing_id", "disposition": "killed", "tests": ["test_writer_sanitizes_persisted_diagnostics"]}
{"mutation": "swallow_write_error", "disposition": "killed", "tests": ["test_database_error_is_explicit_and_secret_safe"]}
{"mutation": "backend_error_text", "disposition": "killed", "tests": ["test_database_error_is_explicit_and_secret_safe"]}
{"mutation": "backend_error_chain", "disposition": "killed", "tests": ["test_database_error_is_explicit_and_secret_safe"]}
{"mutation": "missing_update_guard", "disposition": "killed", "tests": ["test_written_rows_remain_immutable[UPDATE composite_audit_events SET reason = 'changed' WHERE event_id = 'ae-1']"]}
{"mutation": "missing_delete_guard", "disposition": "killed", "tests": ["test_written_rows_remain_immutable[DELETE FROM composite_audit_events WHERE event_id = 'ae-1']"]}
27 mutations killed; no survivors; scratch removed on exit.
SHA256 composite/audit.py: 2e6ea861300afe0d09f4cc3c861f63a04da88d9aacd201120282b9bd3515ea0c
SHA256 composite/migrations.py: 60c79faf2441ae1715e0b632234673da1e313c85fd6af89135af7b557f14303b
SHA256 tests/unit/test_audit_writer.py: 58a79dee9d08e7c3dae9d293ce0cc6f34c6fe793d4dbc2b5532a66c4f796e7dd
SHA256 tests/unit/test_secrets_and_audit.py: 142dbf276616c45ce4447efd1b7bed93ab44b8ba3fa7272033a837ced309f3ab
```
