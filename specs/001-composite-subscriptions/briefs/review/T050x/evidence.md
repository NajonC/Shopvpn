# T050x reference and mutation evidence

Source hashes:
```json
{
  "handlers_user.py": "611ce8a3ddab0d2298f0777187c6bf688958eaa2cce22fbabc2b3bf352182c90",
  "tests/integration/test_composite_telegram_rename_entry_guards.py": "9018439cd5041fba7f6ca05717a51cd799b625056d063b308b2750217c4079c7",
  "tests/characterization/test_callbacks_fsm.py": "b9c63f3386ab154a9082415edcfdbdd61dc7fb895d1e91b5fd1401fe4edd1817"
}
```

Results:
```json
[
  {
    "name": "reference",
    "disposition": "passed",
    "cases": 33,
    "failed_test_ids": []
  },
  {
    "name": "omit_guard",
    "disposition": "killed",
    "cases": 24,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_rename_entry_refused[none-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_rename_entry_refused[none-sqlite]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_rename_entry_refused[matching-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_rename_entry_refused[matching-sqlite]"
    ]
  },
  {
    "name": "wrong_kind",
    "disposition": "killed",
    "cases": 24,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_rename_entry_refused[none-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_rename_entry_refused[none-sqlite]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_rename_entry_refused[matching-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_rename_entry_refused[matching-sqlite]"
    ]
  },
  {
    "name": "reject_missing",
    "disposition": "killed",
    "cases": 24,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[none-None-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[none-None-sqlite]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[matching-None-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[matching-None-sqlite]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[nonmatching-None-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[nonmatching-None-sqlite]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_sibling_does_not_block_rename_entry[dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_sibling_does_not_block_rename_entry[sqlite]"
    ]
  },
  {
    "name": "reject_legacy",
    "disposition": "killed",
    "cases": 24,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[none-legacy-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[none-legacy-sqlite]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[matching-legacy-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[matching-legacy-sqlite]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[nonmatching-legacy-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[nonmatching-legacy-sqlite]"
    ]
  },
  {
    "name": "no_reason",
    "disposition": "killed",
    "cases": 24,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_rename_entry_refused[none-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_rename_entry_refused[none-sqlite]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_rename_entry_refused[matching-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_rename_entry_refused[matching-sqlite]"
    ]
  },
  {
    "name": "fsm_before_refusal",
    "disposition": "killed",
    "cases": 24,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_rename_entry_refused[none-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_rename_entry_refused[none-sqlite]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_rename_entry_refused[matching-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_rename_entry_refused[matching-sqlite]"
    ]
  },
  {
    "name": "data_before_refusal",
    "disposition": "killed",
    "cases": 24,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_rename_entry_refused[none-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_rename_entry_refused[none-sqlite]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_rename_entry_refused[matching-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_rename_entry_refused[matching-sqlite]"
    ]
  },
  {
    "name": "db_before_refusal",
    "disposition": "killed",
    "cases": 24,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_rename_entry_refused[none-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_rename_entry_refused[none-sqlite]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_rename_entry_refused[matching-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_rename_entry_refused[matching-sqlite]"
    ]
  },
  {
    "name": "provider_before_refusal",
    "disposition": "killed",
    "cases": 24,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_rename_entry_refused[none-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_rename_entry_refused[none-sqlite]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_rename_entry_refused[matching-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_rename_entry_refused[matching-sqlite]"
    ]
  },
  {
    "name": "prompt_before_refusal",
    "disposition": "killed",
    "cases": 24,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_rename_entry_refused[none-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_rename_entry_refused[none-sqlite]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_rename_entry_refused[matching-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_rename_entry_refused[matching-sqlite]"
    ]
  },
  {
    "name": "leak_in_refusal",
    "disposition": "killed",
    "cases": 24,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_rename_entry_refused[none-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_rename_entry_refused[none-sqlite]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_rename_entry_refused[matching-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_rename_entry_refused[matching-sqlite]"
    ]
  },
  {
    "name": "wrong_state",
    "disposition": "killed",
    "cases": 24,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[none-None-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[none-None-sqlite]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[none-legacy-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[none-legacy-sqlite]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[matching-None-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[matching-None-sqlite]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[matching-legacy-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[matching-legacy-sqlite]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[nonmatching-None-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[nonmatching-None-sqlite]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[nonmatching-legacy-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[nonmatching-legacy-sqlite]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_sibling_does_not_block_rename_entry[dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_sibling_does_not_block_rename_entry[sqlite]"
    ]
  },
  {
    "name": "wrong_target",
    "disposition": "killed",
    "cases": 24,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[none-None-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[none-None-sqlite]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[none-legacy-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[none-legacy-sqlite]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[matching-None-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[matching-None-sqlite]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[matching-legacy-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[matching-legacy-sqlite]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[nonmatching-None-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[nonmatching-None-sqlite]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[nonmatching-legacy-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[nonmatching-legacy-sqlite]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_sibling_does_not_block_rename_entry[dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_sibling_does_not_block_rename_entry[sqlite]"
    ]
  },
  {
    "name": "clear_sentinel",
    "disposition": "killed",
    "cases": 24,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[none-None-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[none-None-sqlite]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[none-legacy-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[none-legacy-sqlite]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[matching-None-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[matching-None-sqlite]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[matching-legacy-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[matching-legacy-sqlite]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[nonmatching-None-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[nonmatching-None-sqlite]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[nonmatching-legacy-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[nonmatching-legacy-sqlite]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_sibling_does_not_block_rename_entry[dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_sibling_does_not_block_rename_entry[sqlite]"
    ]
  },
  {
    "name": "wrong_display",
    "disposition": "killed",
    "cases": 24,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[matching-None-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[matching-None-sqlite]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[matching-legacy-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[matching-legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_prefix",
    "disposition": "killed",
    "cases": 24,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[nonmatching-None-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[nonmatching-None-sqlite]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[nonmatching-legacy-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[nonmatching-legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_suffix_text",
    "disposition": "killed",
    "cases": 24,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[matching-None-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[matching-None-sqlite]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[matching-legacy-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[matching-legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_plain_text",
    "disposition": "killed",
    "cases": 24,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[none-None-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[none-None-sqlite]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[none-legacy-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[none-legacy-sqlite]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[nonmatching-None-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[nonmatching-None-sqlite]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[nonmatching-legacy-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[nonmatching-legacy-sqlite]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_sibling_does_not_block_rename_entry[dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_sibling_does_not_block_rename_entry[sqlite]"
    ]
  },
  {
    "name": "wrong_keyboard",
    "disposition": "killed",
    "cases": 24,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[none-None-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[none-None-sqlite]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[none-legacy-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[none-legacy-sqlite]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[matching-None-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[matching-None-sqlite]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[matching-legacy-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[matching-legacy-sqlite]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[nonmatching-None-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[nonmatching-None-sqlite]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[nonmatching-legacy-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_exact[nonmatching-legacy-sqlite]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_sibling_does_not_block_rename_entry[dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_sibling_does_not_block_rename_entry[sqlite]"
    ]
  },
  {
    "name": "omit_feature_check",
    "disposition": "killed",
    "cases": 24,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_restrictions[off-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_restrictions[off-sqlite]"
    ]
  },
  {
    "name": "omit_test_check",
    "disposition": "killed",
    "cases": 24,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_restrictions[test-dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_legacy_rename_entry_restrictions[test-sqlite]"
    ]
  },
  {
    "name": "scan_sibling",
    "disposition": "killed",
    "cases": 24,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_sibling_does_not_block_rename_entry[dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_composite_sibling_does_not_block_rename_entry[sqlite]"
    ]
  },
  {
    "name": "wrong_requester",
    "disposition": "killed",
    "cases": 24,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_rename_entry_guards::test_foreign_rename_entry_opaque[dict]",
      "tests.integration.test_composite_telegram_rename_entry_guards::test_foreign_rename_entry_opaque[sqlite]"
    ]
  }
]
```

Independent valid mutations, relevant assertion failures only. No survivors/errors/skips. Scratch auto-cleaned. Reference checks selected owned service before rename-entry FSM/UI; real requester SQL/legacy prompts preserved. No production implementation claim.
