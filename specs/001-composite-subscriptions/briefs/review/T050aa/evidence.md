# T050aa reference and mutation evidence

Source hashes:
```json
{
  "handlers_user.py": "611ce8a3ddab0d2298f0777187c6bf688958eaa2cce22fbabc2b3bf352182c90",
  "tests/integration/test_composite_telegram_transfer_receive_guards.py": "784f2dae2b33708e924cdbc512e2dc1d30cc85a4f41e1b11896d71e6e569a9c3",
  "tests/characterization/test_callbacks_fsm.py": "b9c63f3386ab154a9082415edcfdbdd61dc7fb895d1e91b5fd1401fe4edd1817"
}
```

Results:
```json
[
  {
    "name": "reference",
    "disposition": "passed",
    "cases": 35,
    "failed_test_ids": []
  },
  {
    "name": "omit_guard",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_composite_transfer_receive_refused[dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_composite_transfer_receive_refused[sqlite]"
    ]
  },
  {
    "name": "wrong_kind",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_composite_transfer_receive_refused[dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_composite_transfer_receive_refused[sqlite]"
    ]
  },
  {
    "name": "reject_missing",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[5103-None-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[5103-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[  005103  -None-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[  005103  -None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_composite_sibling_allows_transfer_receive[dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_composite_sibling_allows_transfer_receive[sqlite]"
    ]
  },
  {
    "name": "reject_legacy",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[5103-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[5103-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[  005103  -legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[  005103  -legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_preserves_direct_flags[off-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_preserves_direct_flags[off-sqlite]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_preserves_direct_flags[test-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_preserves_direct_flags[test-sqlite]"
    ]
  },
  {
    "name": "no_reason",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_composite_transfer_receive_refused[dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_composite_transfer_receive_refused[sqlite]"
    ]
  },
  {
    "name": "leak_reason",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_composite_transfer_receive_refused[dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_composite_transfer_receive_refused[sqlite]"
    ]
  },
  {
    "name": "state_before_refusal",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_composite_transfer_receive_refused[dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_composite_transfer_receive_refused[sqlite]"
    ]
  },
  {
    "name": "data_before_refusal",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_composite_transfer_receive_refused[dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_composite_transfer_receive_refused[sqlite]"
    ]
  },
  {
    "name": "clear_before_refusal",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_composite_transfer_receive_refused[dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_composite_transfer_receive_refused[sqlite]"
    ]
  },
  {
    "name": "prompt_before_refusal",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_composite_transfer_receive_refused[dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_composite_transfer_receive_refused[sqlite]"
    ]
  },
  {
    "name": "db_before_refusal",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_composite_transfer_receive_refused[dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_composite_transfer_receive_refused[sqlite]"
    ]
  },
  {
    "name": "provider_before_refusal",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_composite_transfer_receive_refused[dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_composite_transfer_receive_refused[sqlite]"
    ]
  },
  {
    "name": "omit_clear",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[5103-None-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[5103-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[5103-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[5103-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[  005103  -None-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[  005103  -None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[  005103  -legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[  005103  -legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_composite_sibling_allows_transfer_receive[dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_composite_sibling_allows_transfer_receive[sqlite]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_preserves_direct_flags[off-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_preserves_direct_flags[off-sqlite]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_preserves_direct_flags[test-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_preserves_direct_flags[test-sqlite]"
    ]
  },
  {
    "name": "wrong_recipient",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[5103-None-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[5103-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[5103-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[5103-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[  005103  -None-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[  005103  -None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[  005103  -legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[  005103  -legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_composite_sibling_allows_transfer_receive[dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_composite_sibling_allows_transfer_receive[sqlite]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_preserves_direct_flags[off-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_preserves_direct_flags[off-sqlite]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_preserves_direct_flags[test-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_preserves_direct_flags[test-sqlite]"
    ]
  },
  {
    "name": "wrong_service",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[5103-None-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[5103-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[5103-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[5103-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[  005103  -None-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[  005103  -None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[  005103  -legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[  005103  -legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_composite_sibling_allows_transfer_receive[dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_composite_sibling_allows_transfer_receive[sqlite]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_preserves_direct_flags[off-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_preserves_direct_flags[off-sqlite]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_preserves_direct_flags[test-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_preserves_direct_flags[test-sqlite]"
    ]
  },
  {
    "name": "wrong_prompt",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[5103-None-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[5103-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[5103-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[5103-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[  005103  -None-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[  005103  -None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[  005103  -legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[  005103  -legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_composite_sibling_allows_transfer_receive[dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_composite_sibling_allows_transfer_receive[sqlite]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_preserves_direct_flags[off-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_preserves_direct_flags[off-sqlite]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_preserves_direct_flags[test-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_preserves_direct_flags[test-sqlite]"
    ]
  },
  {
    "name": "wrong_parse_mode",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[5103-None-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[5103-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[5103-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[5103-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[  005103  -None-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[  005103  -None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[  005103  -legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[  005103  -legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_composite_sibling_allows_transfer_receive[dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_composite_sibling_allows_transfer_receive[sqlite]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_preserves_direct_flags[off-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_preserves_direct_flags[off-sqlite]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_preserves_direct_flags[test-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_preserves_direct_flags[test-sqlite]"
    ]
  },
  {
    "name": "wrong_keyboard",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[5103-None-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[5103-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[5103-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[5103-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[  005103  -None-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[  005103  -None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[  005103  -legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[  005103  -legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_composite_sibling_allows_transfer_receive[dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_composite_sibling_allows_transfer_receive[sqlite]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_preserves_direct_flags[off-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_preserves_direct_flags[off-sqlite]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_preserves_direct_flags[test-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_preserves_direct_flags[test-sqlite]"
    ]
  },
  {
    "name": "omit_self_check",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_invalid[5101-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_invalid[5101-sqlite]"
    ]
  },
  {
    "name": "omit_registration_check",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_invalid[99999-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_invalid[99999-sqlite]"
    ]
  },
  {
    "name": "wrong_invalid_reason",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_invalid[abc-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_invalid[abc-sqlite]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_invalid[-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_invalid[-sqlite]"
    ]
  },
  {
    "name": "strict_whitespace",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[  005103  -None-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[  005103  -None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[  005103  -legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_exact[  005103  -legacy-sqlite]"
    ]
  },
  {
    "name": "overstrict_feature",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_preserves_direct_flags[off-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_preserves_direct_flags[off-sqlite]"
    ]
  },
  {
    "name": "overstrict_test",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_preserves_direct_flags[test-dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_legacy_transfer_receive_preserves_direct_flags[test-sqlite]"
    ]
  },
  {
    "name": "scan_sibling",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_composite_sibling_allows_transfer_receive[dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_composite_sibling_allows_transfer_receive[sqlite]"
    ]
  },
  {
    "name": "wrong_requester",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_foreign_transfer_receive_opaque[dict]",
      "tests.integration.test_composite_telegram_transfer_receive_guards::test_foreign_transfer_receive_opaque[sqlite]"
    ]
  }
]
```

Independent valid mutations, relevant assertion failures only. No survivors/errors/skips. Scratch auto-cleaned. Reference checks selected owned service before transfer recipient confirmation FSM/prompt effects; real SQL and legacy controls preserved. No production implementation claim.
