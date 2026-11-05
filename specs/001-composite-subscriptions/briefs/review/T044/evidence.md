# T044 offline test verification

Source baseline: `ca86b22`, branch `001-composite-subscriptions-impl`.
Actual orchestrator: gpt-6.1-sol/high. No delegated coder; all tests are
orchestrator-owned under the skill's secrets rule. Owner approved the concrete
brief on 2026-11-05. No production modules or pre-existing tests changed.

Interpreter: repository `.venv/bin/python` (Python 3.12).

```sh
.venv/bin/python -m pytest tests/characterization tests/unit tests/contract tests/integration tests/acceptance --network=deny -q
.venv/bin/python -m pytest tests/unit/test_secrets_and_audit.py --network=deny -q
.venv/bin/python specs/001-composite-subscriptions/briefs/review/T044/verify.py
```

Before adding T044, the full offline suite passed: **2924 passed**, 512 inherited
deprecation warnings, 565.17 seconds. No accepted pending failures at baseline.

T044's 22 cases collect normally. Each fails on an absent API in the production
docstring stubs: SecretBox (9), SecretError (3), token_digest (1),
SecretRedactionFilter (6), install_log_redaction (1), sanitized_diagnostic (2).
The first 20 belong to T045, the last two to T046. Per-case names and reasons
were checked from a temporary JUnit report; collection/setup failures were absent.

Reference: **22 passed**. Real cryptography AESGCM, hashlib, logging and the actual
SecretScan/network-denial harness run in a source-only temporary directory.
Imports were asserted to resolve into scratch; no production configuration,
database, credentials or git metadata were copied. The reference audit module
implements only the diagnostic builder, not the future audit-event writer.

Mutation results: **28 killed**, zero survivors/equivalences or unresolved runs.
The runner records exact edits, asserts a single match, restores the original
module between variants, and requires the named relevant case to fail. Its JSON
output names failed tests without retaining synthetic secret-bearing tracebacks.

| Mutations | Rule | Relevant tests (prefixes in verify.py) |
| --- | --- | --- |
| active_write, active_only_read | Versioned active writes / old-key reads | round_trip, independently_encrypted |
| constant_nonce | Unique nonce for repeated plaintext | encrypt_uses_fresh_nonces |
| plaintext_storage | Real authenticated encryption | round_trip |
| refuse_empty, refuse_unicode | Valid input preservation | round_trip |
| ignore_version, ignore_missing_key, ignore_authentication, ignore_id_authentication | Version/key/integrity refusal, including same-key relabelling | decrypt_refuses_invalid_envelope |
| fallback_key, invalid_key | No invented or malformed key | missing_or_malformed_key |
| wrong_digest, trim_digest, digest_encoding | Exact SHA-256 UTF-8 digest | sha256_digest |
| raw_message, raw_args, raw_exception, raw_cached_exception, raw_stack, raw_extra | No secret on any raw/formatted log surface | redaction_scrubs_log_record |
| drop_context, drop_records | Preserve safe diagnostics and logging | redaction_scrubs_log_record |
| missing_install, ancestor_only_filter | Installed filter handles direct/propagated records | installed_filter |
| diagnostic_error, diagnostic_no_record, diagnostic_success | Diagnostic allowlist, truthful failure context | diagnostic_contains_only |

One initial drop_context variant deleted attributes and was classified invalid
by the runner's AttributeError guard. Replaced with nulling those attributes so
the independent expected-value assertions fail directly. The full campaign was
rerun and produced 28 valid kills. This required no test changes.

Both review scratch directories were deleted automatically on exit. Reference,
mutations and this compact evidence remain reproducible in the repository.

SHA-256 of reviewed sources:

```text
142dbf276616c45ce4447efd1b7bed93ab44b8ba3fa7272033a837ced309f3ab  tests/unit/test_secrets_and_audit.py
6538fc8b0979d4dbec6946a0a96905d8d55e31d105bd897317dbfb0ef48336f5  reference_secrets.py
83045f8f915725643bc83c8fb9410c933f0cce16ed7cf6ac9ca82188b812363b  reference_audit.py
cf56a0ff3cae036992307881af9d680b7beb43c70f624499ff226d8d33e8d202  verify.py
```

Final full offline regression: **2924 passed, 22 failed**, 512 inherited warnings
in 612.27 seconds. Every failure is one of the 22 declared missing-behavior
cases above; no previously passing case regressed. Final command used `--tb=no`
in addition to the full-suite command above. Exit 1 is expected for this test-only
packet. No skip/xfail or existing-test edits were introduced.
T045 must reuse/adapt the cryptographic/redaction mutations against real code;
T046 must reuse/adapt the diagnostic mutations. This is no deployment evidence.
