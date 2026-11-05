# T045 offline implementation verification

Baseline revision: `1a256e8e7e8a6be12c85fd85d48331ee6c8dd166`.
Actual orchestrator: gpt-6-astra/xhigh. Coder: codex/gpt-6-luna,
reasoningEffort=xhigh, one round. Child changed only composite/secrets.py;
all pre-delegation tracked hashes except that file, and the staged diff, were
verified unchanged. No production corrections or takeover were needed.

The accepted T044 test baseline had 2924 passes and 22 declared failures.
At selection, all 22 missing-API failures were reproduced, and 39 related
regression checks passed. Three added T045 cases also failed solely on the
missing secrets APIs, verified through a JUnit report. An unnecessary duplicate
full baseline run was interrupted before delegation and is not counted as a
successful check. Final full-suite acceptance is recorded below.

Before delegation, the orchestrator added independent backend-error fault
injection for encryption/decryption and a previously formatted log-record case.
At review, three cases were added for valid 16/24/32-byte keys and isolation
from subsequent caller keyring mutation, as already required by the brief.
They pass against the real implementation and are sensitive to both key-size
and shared-keyring mutants. No existing expectations were changed.

## Checks

Use the repository `.venv/bin/python` (Python 3.12):

```sh
.venv/bin/python -m pytest tests/unit/test_secrets_and_audit.py tests/unit/test_secrets_failures.py --network=deny -q --tb=no -k 'not diagnostic_contains'
.venv/bin/python -m pytest tests/unit/test_secret_scan.py tests/unit/test_fixture_secrets.py tests/characterization/test_webhook_secret.py --network=deny -q --tb=no
.venv/bin/python specs/001-composite-subscriptions/briefs/review/T045/verify.py
.venv/bin/python -m pytest tests/characterization tests/unit tests/contract tests/integration tests/acceptance --network=deny -q --tb=no
```

Independent focused checks: **26 passed, 2 deselected**; related checks:
**39 passed**. The two deselected cases are the T046 diagnostic-builder cases;
they remain in the full suite. Real-code scratch baseline: **26 passed**.
Mutation campaign: **34 killed**, no invalid runs, survivors or unresolved rules.

The runner exports only named source/test modules and the test harness to a
unique TemporaryDirectory under /tmp; no git metadata, configuration, keys,
databases or backups are copied. Imports are asserted to resolve to scratch.
Every mutant starts with the actual production implementation, not T044's
reference; exact-match replacements and compilation confirm the edit applied.
Selected tests must fail on the expected behavior; setup/import/syntax errors
are invalid. No production code or shared tests are mutated.

## Source-to-test mutations

The brief maps source requirements to the following exact mutations and failed
cases. The T044 audit-only mutations are deferred to T046.

| Mutation | Relevant failed tests | Disposition |
| --- | --- | --- |
| active_write | `test_round_trip_is_independent_aes_gcm_and_hides_plaintext` | killed |
| active_only_read | `test_independently_encrypted_old_key_remains_readable` | killed |
| constant_nonce | `test_encrypt_uses_fresh_nonces_for_same_value` | killed |
| plaintext_storage | `test_round_trip_is_independent_aes_gcm_and_hides_plaintext` | killed |
| refuse_empty | `test_round_trip_is_independent_aes_gcm_and_hides_plaintext` | killed |
| refuse_unicode | `test_round_trip_is_independent_aes_gcm_and_hides_plaintext` | killed |
| ignore_version | `test_decrypt_refuses_invalid_envelope_without_secret_exception[version]` | killed |
| ignore_missing_key | `test_decrypt_refuses_invalid_envelope_without_secret_exception[missing]` | killed |
| ignore_authentication | `test_decrypt_refuses_invalid_envelope_without_secret_exception[missing]`, `test_decrypt_refuses_invalid_envelope_without_secret_exception[wrong]`, `test_decrypt_refuses_invalid_envelope_without_secret_exception[ciphertext]`, `test_decrypt_refuses_invalid_envelope_without_secret_exception[nonce]`, `test_decrypt_refuses_invalid_envelope_without_secret_exception[version]`, `test_decrypt_refuses_invalid_envelope_without_secret_exception[key_id]` | killed |
| ignore_id_authentication | `test_decrypt_refuses_invalid_envelope_without_secret_exception[key_id]` | killed |
| fallback_key | `test_missing_or_malformed_key_never_gets_fallback[keys0-active]`, `test_missing_or_malformed_key_never_gets_fallback[keys1-active]` | killed |
| invalid_key | `test_missing_or_malformed_key_never_gets_fallback[keys2-active]` | killed |
| reject_valid_key_sizes | `test_supported_aes_keys_are_copied_from_configuration[16]`, `test_supported_aes_keys_are_copied_from_configuration[24]` | killed |
| retain_mutable_configuration | `test_supported_aes_keys_are_copied_from_configuration[16]`, `test_supported_aes_keys_are_copied_from_configuration[24]`, `test_supported_aes_keys_are_copied_from_configuration[32]` | killed |
| mutable_envelope | `test_round_trip_is_independent_aes_gcm_and_hides_plaintext` | killed |
| wrong_digest | `test_sha256_digest_is_exact_utf8_without_normalization` | killed |
| trim_digest | `test_sha256_digest_is_exact_utf8_without_normalization` | killed |
| digest_encoding | `test_sha256_digest_is_exact_utf8_without_normalization` | killed |
| raw_message | `test_redaction_scrubs_log_record_and_formatted_exception[message]` | killed |
| raw_args | `test_redaction_scrubs_log_record_and_formatted_exception[positional]`, `test_redaction_scrubs_log_record_and_formatted_exception[mapping]` | killed |
| raw_exception | `test_redaction_scrubs_log_record_and_formatted_exception[exception]` | killed |
| raw_cached_exception | `test_redaction_scrubs_log_record_and_formatted_exception[cached_exception]` | killed |
| raw_stack | `test_redaction_scrubs_log_record_and_formatted_exception[cached_exception]` | killed |
| raw_extra | `test_redaction_scrubs_log_record_and_formatted_exception[extras]` | killed |
| raw_formatter_cache | `test_redaction_removes_formatter_cached_message` | killed |
| drop_context | `test_redaction_scrubs_log_record_and_formatted_exception[message]`, `test_redaction_scrubs_log_record_and_formatted_exception[positional]`, `test_redaction_scrubs_log_record_and_formatted_exception[mapping]`, `test_redaction_scrubs_log_record_and_formatted_exception[exception]`, `test_redaction_scrubs_log_record_and_formatted_exception[cached_exception]`, `test_redaction_scrubs_log_record_and_formatted_exception[extras]` | killed |
| drop_records | `test_redaction_scrubs_log_record_and_formatted_exception[message]`, `test_redaction_scrubs_log_record_and_formatted_exception[positional]`, `test_redaction_scrubs_log_record_and_formatted_exception[mapping]`, `test_redaction_scrubs_log_record_and_formatted_exception[exception]`, `test_redaction_scrubs_log_record_and_formatted_exception[cached_exception]`, `test_redaction_scrubs_log_record_and_formatted_exception[extras]` | killed |
| wrong_severity | `test_redaction_scrubs_log_record_and_formatted_exception[message]`, `test_redaction_scrubs_log_record_and_formatted_exception[positional]`, `test_redaction_scrubs_log_record_and_formatted_exception[mapping]`, `test_redaction_scrubs_log_record_and_formatted_exception[exception]`, `test_redaction_scrubs_log_record_and_formatted_exception[cached_exception]`, `test_redaction_scrubs_log_record_and_formatted_exception[extras]` | killed |
| missing_install | `test_installed_filter_protects_logger_and_descendant_handler` | killed |
| ancestor_only_filter | `test_installed_filter_protects_logger_and_descendant_handler` | killed |
| encryption_error_text | `test_crypto_backend_failure_has_sanitized_exception[encrypt]` | killed |
| encryption_error_chain | `test_crypto_backend_failure_has_sanitized_exception[encrypt]` | killed |
| decryption_error_text | `test_crypto_backend_failure_has_sanitized_exception[decrypt]` | killed |
| decryption_error_chain | `test_crypto_backend_failure_has_sanitized_exception[decrypt]` | killed |

The cached-message protection has two overlapping defenses: the allowlist loop
removes `message`, and an explicit pop removes it again. Removing only the pop
is equivalent by inspection; the combined `raw_formatter_cache` mutant bypasses
both and is caught by the cached-message test. No surviving mutant is being
counted as a kill.

The installation API protects the supplied composite logger and its currently
attached handlers. As established in T044, future entry points must call it
after configuring or adding handlers; this is library behavior, not deployed
security or release evidence. No unrelated/root loggers are modified on import.

Scratch cleanup succeeded through TemporaryDirectory. Only reproducible source
artifacts and this redacted evidence are retained; no generated credentials or
pytest tracebacks are committed.

## Source hashes

- `composite/secrets.py`: `68c290d072782155b0f0ff15da6e144b0e4dc368d23625b6fa7961b89651ee65`
- `tests/unit/test_secrets_and_audit.py`: `142dbf276616c45ce4447efd1b7bed93ab44b8ba3fa7272033a837ced309f3ab`
- `tests/unit/test_secrets_failures.py`: `e231bd52361fc78b6d28e89e814fdb70f20e9063a0b46267b15854a738dd0464`
- `specs/001-composite-subscriptions/briefs/review/T045/verify.py`: `bbcd7a5ef8e229df25146486b1247da89e4d68a5488cb4aebbfdbde1edb3d2f9`

## Final full regression

**2950 passed, 2 failed, 512 inherited warnings in 556.44 seconds.**
JUnit identities and reasons independently verified: the only failures are
`tests/unit/test_secrets_and_audit.py::test_diagnostic_contains_only_operation_tenant_record[False]`
and `[True]`, both AttributeError for the missing
`composite.audit.sanitized_diagnostic` API assigned to T046. No errors, skips,
or previously passing-test regressions. All T045 cases pass.

Accepted on the existing implementation branch. Next: T046, recommended
orchestrator gpt-6.1-sol/high; coder antigravity/gemini-3.8-flash-high, options {}.
Reason: baseline high behavioral audit work. Verification: immutable audit-writer
and diagnostic tests, real-code mutations reusing T044 diagnostic artifacts,
plus a full offline regression run. No known gate; research at selection.
