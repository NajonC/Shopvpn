# T050z reference and mutation evidence

Source hashes:
```json
{
  "handlers_user.py": "611ce8a3ddab0d2298f0777187c6bf688958eaa2cce22fbabc2b3bf352182c90",
  "tests/integration/test_composite_telegram_transfer_entry_guards.py": "764bf0608bdd3a483152d581549b739368cd6f213bb061db6699c8b67f23fa5f",
  "tests/characterization/test_callbacks_fsm.py": "b9c63f3386ab154a9082415edcfdbdd61dc7fb895d1e91b5fd1401fe4edd1817"
}
```

Results:
```json
[
  {
    "name": "reference",
    "disposition": "passed",
    "cases": 23,
    "failed_test_ids": []
  },
  {
    "name": "omit_guard",
    "disposition": "killed",
    "cases": 14,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_composite_transfer_entry_refused[dict]",
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_composite_transfer_entry_refused[sqlite]"
    ]
  },
  {
    "name": "wrong_kind",
    "disposition": "killed",
    "cases": 14,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_composite_transfer_entry_refused[dict]",
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_composite_transfer_entry_refused[sqlite]"
    ]
  },
  {
    "name": "reject_missing",
    "disposition": "killed",
    "cases": 14,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_legacy_transfer_entry_exact[None-dict]",
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_legacy_transfer_entry_exact[None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_composite_sibling_allows_transfer_entry[dict]",
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_composite_sibling_allows_transfer_entry[sqlite]"
    ]
  },
  {
    "name": "reject_legacy",
    "disposition": "killed",
    "cases": 14,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_legacy_transfer_entry_exact[legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_legacy_transfer_entry_exact[legacy-sqlite]"
    ]
  },
  {
    "name": "no_reason",
    "disposition": "killed",
    "cases": 14,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_composite_transfer_entry_refused[dict]",
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_composite_transfer_entry_refused[sqlite]"
    ]
  },
  {
    "name": "leak_reason",
    "disposition": "killed",
    "cases": 14,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_composite_transfer_entry_refused[dict]",
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_composite_transfer_entry_refused[sqlite]"
    ]
  },
  {
    "name": "state_before_refusal",
    "disposition": "killed",
    "cases": 14,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_composite_transfer_entry_refused[dict]",
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_composite_transfer_entry_refused[sqlite]"
    ]
  },
  {
    "name": "data_before_refusal",
    "disposition": "killed",
    "cases": 14,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_composite_transfer_entry_refused[dict]",
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_composite_transfer_entry_refused[sqlite]"
    ]
  },
  {
    "name": "clear_before_refusal",
    "disposition": "killed",
    "cases": 14,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_composite_transfer_entry_refused[dict]",
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_composite_transfer_entry_refused[sqlite]"
    ]
  },
  {
    "name": "prompt_before_refusal",
    "disposition": "killed",
    "cases": 14,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_composite_transfer_entry_refused[dict]",
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_composite_transfer_entry_refused[sqlite]"
    ]
  },
  {
    "name": "db_before_refusal",
    "disposition": "killed",
    "cases": 14,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_composite_transfer_entry_refused[dict]",
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_composite_transfer_entry_refused[sqlite]"
    ]
  },
  {
    "name": "provider_before_refusal",
    "disposition": "killed",
    "cases": 14,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_composite_transfer_entry_refused[dict]",
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_composite_transfer_entry_refused[sqlite]"
    ]
  },
  {
    "name": "omit_state",
    "disposition": "killed",
    "cases": 14,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_legacy_transfer_entry_exact[None-dict]",
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_legacy_transfer_entry_exact[None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_legacy_transfer_entry_exact[legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_legacy_transfer_entry_exact[legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_composite_sibling_allows_transfer_entry[dict]",
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_composite_sibling_allows_transfer_entry[sqlite]"
    ]
  },
  {
    "name": "wrong_target",
    "disposition": "killed",
    "cases": 14,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_legacy_transfer_entry_exact[None-dict]",
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_legacy_transfer_entry_exact[None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_legacy_transfer_entry_exact[legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_legacy_transfer_entry_exact[legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_composite_sibling_allows_transfer_entry[dict]",
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_composite_sibling_allows_transfer_entry[sqlite]"
    ]
  },
  {
    "name": "wrong_prompt",
    "disposition": "killed",
    "cases": 14,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_legacy_transfer_entry_exact[None-dict]",
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_legacy_transfer_entry_exact[None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_legacy_transfer_entry_exact[legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_legacy_transfer_entry_exact[legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_composite_sibling_allows_transfer_entry[dict]",
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_composite_sibling_allows_transfer_entry[sqlite]"
    ]
  },
  {
    "name": "wrong_keyboard",
    "disposition": "killed",
    "cases": 14,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_legacy_transfer_entry_exact[None-dict]",
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_legacy_transfer_entry_exact[None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_legacy_transfer_entry_exact[legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_legacy_transfer_entry_exact[legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_composite_sibling_allows_transfer_entry[dict]",
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_composite_sibling_allows_transfer_entry[sqlite]"
    ]
  },
  {
    "name": "omit_feature_gate",
    "disposition": "killed",
    "cases": 14,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_transfer_entry_restrictions[off-dict]",
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_transfer_entry_restrictions[off-sqlite]"
    ]
  },
  {
    "name": "omit_test_gate",
    "disposition": "killed",
    "cases": 14,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_transfer_entry_restrictions[test-dict]",
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_transfer_entry_restrictions[test-sqlite]"
    ]
  },
  {
    "name": "scan_sibling",
    "disposition": "killed",
    "cases": 14,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_composite_sibling_allows_transfer_entry[dict]",
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_composite_sibling_allows_transfer_entry[sqlite]"
    ]
  },
  {
    "name": "wrong_requester",
    "disposition": "killed",
    "cases": 14,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_foreign_transfer_entry_opaque[dict]",
      "tests.integration.test_composite_telegram_transfer_entry_guards::test_foreign_transfer_entry_opaque[sqlite]"
    ]
  }
]
```

Independent valid mutations, relevant assertion failures only. No survivors/errors/skips. Scratch auto-cleaned. Reference checks selected owned service before transfer entry FSM/prompt effects; real SQL and legacy controls preserved. No production implementation claim.
