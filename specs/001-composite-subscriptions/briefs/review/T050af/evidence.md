# T050af reference and mutation evidence

Source hashes:
```json
{
  "handlers_user.py": "611ce8a3ddab0d2298f0777187c6bf688958eaa2cce22fbabc2b3bf352182c90",
  "tests/integration/test_composite_telegram_custom_duration_guards.py": "f4c0aa7e42f8eab1bf13888982c6e1c3b2cac69ca59ff31515d8100dc18ddfba",
  "tests/characterization/test_callbacks_fsm.py": "b9c63f3386ab154a9082415edcfdbdd61dc7fb895d1e91b5fd1401fe4edd1817"
}
```

Results:
```json
[
  {
    "name": "reference",
    "disposition": "passed",
    "cases": 45,
    "failed_test_ids": []
  },
  {
    "name": "omit_guard",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_duration_refused[dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_duration_refused[sqlite]"
    ]
  },
  {
    "name": "wrong_kind",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_duration_refused[dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_duration_refused[sqlite]"
    ]
  },
  {
    "name": "reject_missing",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_sibling_allows_duration[dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_sibling_allows_duration[sqlite]"
    ]
  },
  {
    "name": "reject_legacy",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_invalid_duration_retained[1-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_invalid_duration_retained[1-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_invalid_duration_retained[61-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_invalid_duration_retained[61-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_invalid_duration_retained[-1-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_invalid_duration_retained[-1-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_invalid_duration_retained[2.0-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_invalid_duration_retained[2.0-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_invalid_duration_retained[bad-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_invalid_duration_retained[bad-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_invalid_duration_retained[-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_invalid_duration_retained[-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_card_only_preserves_wallet[dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_card_only_preserves_wallet[sqlite]"
    ]
  },
  {
    "name": "no_reason",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_duration_refused[dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_duration_refused[sqlite]"
    ]
  },
  {
    "name": "leak_reason",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_duration_refused[dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_duration_refused[sqlite]"
    ]
  },
  {
    "name": "state_before_refusal",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_duration_refused[dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_duration_refused[sqlite]"
    ]
  },
  {
    "name": "data_before_refusal",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_duration_refused[dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_duration_refused[sqlite]"
    ]
  },
  {
    "name": "clear_before_refusal",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_duration_refused[dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_duration_refused[sqlite]"
    ]
  },
  {
    "name": "prompt_before_refusal",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_duration_refused[dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_duration_refused[sqlite]"
    ]
  },
  {
    "name": "db_before_refusal",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_duration_refused[dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_duration_refused[sqlite]"
    ]
  },
  {
    "name": "provider_before_refusal",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_duration_refused[dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_duration_refused[sqlite]"
    ]
  },
  {
    "name": "lower_boundary",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-legacy-sqlite]"
    ]
  },
  {
    "name": "upper_boundary",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-legacy-sqlite]"
    ]
  },
  {
    "name": "omit_bounds",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_invalid_duration_retained[1-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_invalid_duration_retained[1-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_invalid_duration_retained[61-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_invalid_duration_retained[61-sqlite]"
    ]
  },
  {
    "name": "reject_valid",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_sibling_allows_duration[dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_sibling_allows_duration[sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_card_only_preserves_wallet[dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_card_only_preserves_wallet[sqlite]"
    ]
  },
  {
    "name": "omit_trim",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_sibling_allows_duration[dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_sibling_allows_duration[sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_card_only_preserves_wallet[dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_card_only_preserves_wallet[sqlite]"
    ]
  },
  {
    "name": "wrong_min_default",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_max_default",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_final_days",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_sibling_allows_duration[dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_sibling_allows_duration[sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_card_only_preserves_wallet[dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_card_only_preserves_wallet[sqlite]"
    ]
  },
  {
    "name": "missing_product_state",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_duration_guards::test_missing_duration_product_clears[dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_missing_duration_product_clears[sqlite]"
    ]
  },
  {
    "name": "wrong_price",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_sibling_allows_duration[dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_sibling_allows_duration[sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_card_only_preserves_wallet[dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_card_only_preserves_wallet[sqlite]"
    ]
  },
  {
    "name": "wrong_volume",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_sibling_allows_duration[dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_sibling_allows_duration[sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_card_only_preserves_wallet[dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_card_only_preserves_wallet[sqlite]"
    ]
  },
  {
    "name": "wrong_user",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_sibling_allows_duration[dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_sibling_allows_duration[sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_card_only_preserves_wallet[dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_card_only_preserves_wallet[sqlite]"
    ]
  },
  {
    "name": "wrong_username",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_sibling_allows_duration[dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_sibling_allows_duration[sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_card_only_preserves_wallet[dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_card_only_preserves_wallet[sqlite]"
    ]
  },
  {
    "name": "omit_debit",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_sibling_allows_duration[dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_sibling_allows_duration[sqlite]"
    ]
  },
  {
    "name": "double_debit",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_sibling_allows_duration[dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_sibling_allows_duration[sqlite]"
    ]
  },
  {
    "name": "wrong_wallet_order",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_sibling_allows_duration[dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_sibling_allows_duration[sqlite]"
    ]
  },
  {
    "name": "wrong_product",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_sibling_allows_duration[dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_sibling_allows_duration[sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_card_only_preserves_wallet[dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_card_only_preserves_wallet[sqlite]"
    ]
  },
  {
    "name": "wrong_state",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_sibling_allows_duration[dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_sibling_allows_duration[sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_card_only_preserves_wallet[dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_card_only_preserves_wallet[sqlite]"
    ]
  },
  {
    "name": "omit_order_id",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits0-2-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits1-60-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits2-1-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-None-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_duration_exact[limits3-90-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_sibling_allows_duration[dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_sibling_allows_duration[sqlite]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_card_only_preserves_wallet[dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_card_only_preserves_wallet[sqlite]"
    ]
  },
  {
    "name": "ignore_wallet_restriction",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_card_only_preserves_wallet[dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_legacy_card_only_preserves_wallet[sqlite]"
    ]
  },
  {
    "name": "scan_sibling",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_sibling_allows_duration[dict]",
      "tests.integration.test_composite_telegram_custom_duration_guards::test_composite_sibling_allows_duration[sqlite]"
    ]
  }
]
```

Independent valid mutations, relevant assertion failures only. No survivors/errors/skips. Scratch auto-cleaned. Reference checks selected owned service before random custom username selected-product/FSM/pricing effects; real SQL and legacy controls preserved. No production implementation claim.
