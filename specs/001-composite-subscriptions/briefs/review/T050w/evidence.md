# T050w reference and mutation evidence

Source hashes:
```json
{
  "handlers_user.py": "611ce8a3ddab0d2298f0777187c6bf688958eaa2cce22fbabc2b3bf352182c90",
  "tests/integration/test_composite_telegram_autorenew_guards.py": "69ceabbe4a71cd1beed7015d5db93a1fd0b6e021ab59a996f9ad9af9160c6ecd",
  "tests/characterization/test_legacy_renewal_reminders.py": "84722b6b10d9fbdae768cb5fb8e8fbc3490b3a213575196210a56401c6e61ea3"
}
```

Results:
```json
[
  {
    "name": "reference",
    "disposition": "passed",
    "cases": 61,
    "failed_test_ids": []
  },
  {
    "name": "omit_guard",
    "disposition": "killed",
    "cases": 22,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_autorenew_guards::test_composite_autorenew_refused[0-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_composite_autorenew_refused[0-sqlite]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_composite_autorenew_refused[1-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_composite_autorenew_refused[1-sqlite]"
    ]
  },
  {
    "name": "wrong_kind",
    "disposition": "killed",
    "cases": 22,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_autorenew_guards::test_composite_autorenew_refused[0-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_composite_autorenew_refused[0-sqlite]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_composite_autorenew_refused[1-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_composite_autorenew_refused[1-sqlite]"
    ]
  },
  {
    "name": "reject_missing",
    "disposition": "killed",
    "cases": 22,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[0-None-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[0-None-sqlite]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[1-None-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[1-None-sqlite]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_unselected_composite_does_not_block_autorenew[dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_unselected_composite_does_not_block_autorenew[sqlite]"
    ]
  },
  {
    "name": "reject_legacy",
    "disposition": "killed",
    "cases": 22,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[0-legacy-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[0-legacy-sqlite]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[1-legacy-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[1-legacy-sqlite]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_existing_autorenew_restrictions[unlimited-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_existing_autorenew_restrictions[unlimited-sqlite]"
    ]
  },
  {
    "name": "no_reason",
    "disposition": "killed",
    "cases": 22,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_autorenew_guards::test_composite_autorenew_refused[0-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_composite_autorenew_refused[0-sqlite]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_composite_autorenew_refused[1-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_composite_autorenew_refused[1-sqlite]"
    ]
  },
  {
    "name": "flag_before_refusal",
    "disposition": "killed",
    "cases": 22,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_autorenew_guards::test_composite_autorenew_refused[0-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_composite_autorenew_refused[0-sqlite]"
    ]
  },
  {
    "name": "history_before_refusal",
    "disposition": "killed",
    "cases": 22,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_autorenew_guards::test_composite_autorenew_refused[0-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_composite_autorenew_refused[0-sqlite]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_composite_autorenew_refused[1-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_composite_autorenew_refused[1-sqlite]"
    ]
  },
  {
    "name": "provider_before_refusal",
    "disposition": "killed",
    "cases": 22,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_autorenew_guards::test_composite_autorenew_refused[0-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_composite_autorenew_refused[0-sqlite]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_composite_autorenew_refused[1-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_composite_autorenew_refused[1-sqlite]"
    ]
  },
  {
    "name": "fetch_before_refusal",
    "disposition": "killed",
    "cases": 22,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_autorenew_guards::test_composite_autorenew_refused[0-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_composite_autorenew_refused[0-sqlite]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_composite_autorenew_refused[1-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_composite_autorenew_refused[1-sqlite]"
    ]
  },
  {
    "name": "leak_before_refusal",
    "disposition": "killed",
    "cases": 22,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_autorenew_guards::test_composite_autorenew_refused[0-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_composite_autorenew_refused[0-sqlite]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_composite_autorenew_refused[1-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_composite_autorenew_refused[1-sqlite]"
    ]
  },
  {
    "name": "leak_in_refusal",
    "disposition": "killed",
    "cases": 22,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_autorenew_guards::test_composite_autorenew_refused[0-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_composite_autorenew_refused[0-sqlite]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_composite_autorenew_refused[1-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_composite_autorenew_refused[1-sqlite]"
    ]
  },
  {
    "name": "wrong_toggle",
    "disposition": "killed",
    "cases": 22,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[0-None-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[0-None-sqlite]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[0-legacy-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[0-legacy-sqlite]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[1-None-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[1-None-sqlite]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[1-legacy-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[1-legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_target",
    "disposition": "killed",
    "cases": 22,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[0-None-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[0-None-sqlite]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[0-legacy-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[0-legacy-sqlite]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[1-None-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[1-None-sqlite]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[1-legacy-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[1-legacy-sqlite]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_unselected_composite_does_not_block_autorenew[dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_unselected_composite_does_not_block_autorenew[sqlite]"
    ]
  },
  {
    "name": "wrong_history_type",
    "disposition": "killed",
    "cases": 22,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[0-None-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[0-None-sqlite]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[0-legacy-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[0-legacy-sqlite]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[1-None-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[1-None-sqlite]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[1-legacy-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[1-legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_history_detail",
    "disposition": "killed",
    "cases": 22,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[0-None-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[0-None-sqlite]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[0-legacy-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[0-legacy-sqlite]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[1-None-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[1-None-sqlite]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[1-legacy-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[1-legacy-sqlite]"
    ]
  },
  {
    "name": "omit_card",
    "disposition": "killed",
    "cases": 22,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[0-None-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[0-None-sqlite]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[0-legacy-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[0-legacy-sqlite]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[1-None-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[1-None-sqlite]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[1-legacy-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[1-legacy-sqlite]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_unselected_composite_does_not_block_autorenew[dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_unselected_composite_does_not_block_autorenew[sqlite]"
    ]
  },
  {
    "name": "wrong_on_alert",
    "disposition": "killed",
    "cases": 22,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[0-None-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[0-None-sqlite]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[0-legacy-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[0-legacy-sqlite]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[1-None-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[1-None-sqlite]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[1-legacy-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[1-legacy-sqlite]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_unselected_composite_does_not_block_autorenew[dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_unselected_composite_does_not_block_autorenew[sqlite]"
    ]
  },
  {
    "name": "wrong_off_alert",
    "disposition": "killed",
    "cases": 22,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[0-None-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[0-None-sqlite]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[0-legacy-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[0-legacy-sqlite]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[1-None-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[1-None-sqlite]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[1-legacy-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[1-legacy-sqlite]"
    ]
  },
  {
    "name": "omit_provider_read",
    "disposition": "killed",
    "cases": 22,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[0-None-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[0-None-sqlite]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[0-legacy-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[0-legacy-sqlite]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[1-None-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[1-None-sqlite]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[1-legacy-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_legacy_autorenew_exact_toggle[1-legacy-sqlite]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_unselected_composite_does_not_block_autorenew[dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_unselected_composite_does_not_block_autorenew[sqlite]"
    ]
  },
  {
    "name": "omit_feature_check",
    "disposition": "killed",
    "cases": 22,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_autorenew_guards::test_existing_autorenew_restrictions[off-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_existing_autorenew_restrictions[off-sqlite]"
    ]
  },
  {
    "name": "omit_test_check",
    "disposition": "killed",
    "cases": 22,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_autorenew_guards::test_existing_autorenew_restrictions[test-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_existing_autorenew_restrictions[test-sqlite]"
    ]
  },
  {
    "name": "omit_duration_check",
    "disposition": "killed",
    "cases": 22,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_autorenew_guards::test_existing_autorenew_restrictions[unlimited-dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_existing_autorenew_restrictions[unlimited-sqlite]"
    ]
  },
  {
    "name": "scan_sibling",
    "disposition": "killed",
    "cases": 22,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_autorenew_guards::test_unselected_composite_does_not_block_autorenew[dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_unselected_composite_does_not_block_autorenew[sqlite]"
    ]
  },
  {
    "name": "wrong_requester",
    "disposition": "killed",
    "cases": 22,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_autorenew_guards::test_foreign_autorenew_opaque_refusal[dict]",
      "tests.integration.test_composite_telegram_autorenew_guards::test_foreign_autorenew_opaque_refusal[sqlite]"
    ]
  }
]
```

Independent valid mutations, relevant assertion failures only. No survivors/errors/skips. Scratch auto-cleaned. Reference checks selected owned custom service before auto-renew flag/history writes and card reads; real requester SQL/toggle/history/card retained. No production implementation claim.
