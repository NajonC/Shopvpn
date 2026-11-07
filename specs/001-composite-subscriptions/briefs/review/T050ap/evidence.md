# T050ap reference and mutation evidence

Source hashes:
```json
{
  "handlers_user.py": "611ce8a3ddab0d2298f0777187c6bf688958eaa2cce22fbabc2b3bf352182c90",
  "tests/integration/test_composite_telegram_custom_wallet_guards.py": "cd9f8a138eeabd5e6e785c85b1faff48a0af45d0fda1eeab63bb4b653de86f65",
  "tests/characterization/test_callbacks_fsm.py": "b9c63f3386ab154a9082415edcfdbdd61dc7fb895d1e91b5fd1401fe4edd1817"
}
```

Results:
```json
[
  {
    "name": "reference",
    "disposition": "passed",
    "cases": 41,
    "failed_test_ids": []
  },
  {
    "name": "custom_config_receive_volume_omit_guard",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_composite_full_wallet_refused[fixed-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_composite_full_wallet_refused[fixed-sqlite]"
    ]
  },
  {
    "name": "custom_config_receive_volume_reject_missing",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[fixed-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[fixed-sqlite]"
    ]
  },
  {
    "name": "custom_config_receive_volume_reject_legacy",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-legacy-sqlite]"
    ]
  },
  {
    "name": "custom_config_receive_volume_no_reason",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_composite_full_wallet_refused[fixed-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_composite_full_wallet_refused[fixed-sqlite]"
    ]
  },
  {
    "name": "custom_config_receive_volume_early_debit",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_composite_full_wallet_refused[fixed-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_composite_full_wallet_refused[fixed-sqlite]"
    ]
  },
  {
    "name": "custom_config_receive_volume_early_provider",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_composite_full_wallet_refused[fixed-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_composite_full_wallet_refused[fixed-sqlite]"
    ]
  },
  {
    "name": "custom_config_receive_duration_omit_guard",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_composite_full_wallet_refused[choice-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_composite_full_wallet_refused[choice-sqlite]"
    ]
  },
  {
    "name": "custom_config_receive_duration_reject_missing",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[choice-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[choice-sqlite]"
    ]
  },
  {
    "name": "custom_config_receive_duration_reject_legacy",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-legacy-sqlite]"
    ]
  },
  {
    "name": "custom_config_receive_duration_no_reason",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_composite_full_wallet_refused[choice-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_composite_full_wallet_refused[choice-sqlite]"
    ]
  },
  {
    "name": "custom_config_receive_duration_early_debit",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_composite_full_wallet_refused[choice-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_composite_full_wallet_refused[choice-sqlite]"
    ]
  },
  {
    "name": "custom_config_receive_duration_early_provider",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_composite_full_wallet_refused[choice-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_composite_full_wallet_refused[choice-sqlite]"
    ]
  },
  {
    "name": "wrong_price",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[fixed-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[fixed-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[choice-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[choice-sqlite]"
    ]
  },
  {
    "name": "wrong_volume",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[fixed-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[fixed-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[choice-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[choice-sqlite]"
    ]
  },
  {
    "name": "wrong_user",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[fixed-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[fixed-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[choice-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[choice-sqlite]"
    ]
  },
  {
    "name": "omit_debit",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[fixed-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[fixed-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[choice-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[choice-sqlite]"
    ]
  },
  {
    "name": "double_debit",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[fixed-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[fixed-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[choice-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[choice-sqlite]"
    ]
  },
  {
    "name": "wrong_wallet",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[fixed-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[fixed-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[choice-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[choice-sqlite]"
    ]
  },
  {
    "name": "wrong_product",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[fixed-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[fixed-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[choice-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[choice-sqlite]"
    ]
  },
  {
    "name": "wrong_provider_days",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[fixed-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[fixed-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[choice-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[choice-sqlite]"
    ]
  },
  {
    "name": "wrong_provider_name",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[fixed-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[fixed-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[choice-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[choice-sqlite]"
    ]
  },
  {
    "name": "omit_approve",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[fixed-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[fixed-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[choice-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[choice-sqlite]"
    ]
  },
  {
    "name": "wrong_config_name",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[fixed-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[fixed-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[choice-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[choice-sqlite]"
    ]
  },
  {
    "name": "wrong_config_product",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[fixed-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[fixed-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[choice-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[choice-sqlite]"
    ]
  },
  {
    "name": "omit_delivery",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[fixed-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[fixed-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[choice-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[choice-sqlite]"
    ]
  },
  {
    "name": "omit_notify",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-fixed-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-choice-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1000-global-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-fixed-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-choice-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-None-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_legacy_full_wallet_success[1500-global-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[fixed-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[fixed-sqlite]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[choice-dict]",
      "tests.integration.test_composite_telegram_custom_wallet_guards::test_unrelated_composite_allows_wallet[choice-sqlite]"
    ]
  }
]
```

Independent valid mutations, relevant assertion failures only. No survivors/errors/skips. Scratch auto-cleaned. Reference checks selected owned service before fixed custom checkout selected-product before pricing/FSM/order/wallet/provider effects; real SQL and legacy controls preserved. No production implementation claim.
