# T050ae reference and mutation evidence

Source hashes:
```json
{
  "handlers_user.py": "611ce8a3ddab0d2298f0777187c6bf688958eaa2cce22fbabc2b3bf352182c90",
  "tests/integration/test_composite_telegram_custom_volume_guards.py": "b5f2f8e1dcf881c3c2cae1dc790d519a170545c5b07e50a87d382ec8ee146851",
  "tests/characterization/test_callbacks_fsm.py": "b9c63f3386ab154a9082415edcfdbdd61dc7fb895d1e91b5fd1401fe4edd1817"
}
```

Results:
```json
[
  {
    "name": "reference",
    "disposition": "passed",
    "cases": 43,
    "failed_test_ids": []
  },
  {
    "name": "omit_guard",
    "disposition": "killed",
    "cases": 34,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_volume_guards::test_composite_volume_refused[dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_composite_volume_refused[sqlite]"
    ]
  },
  {
    "name": "wrong_kind",
    "disposition": "killed",
    "cases": 34,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_volume_guards::test_composite_volume_refused[dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_composite_volume_refused[sqlite]"
    ]
  },
  {
    "name": "reject_missing",
    "disposition": "killed",
    "cases": 34,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-5-None-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-5-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-1000-None-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-1000-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-5-None-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-5-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-1000-None-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-1000-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_composite_sibling_allows_volume[dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_composite_sibling_allows_volume[sqlite]"
    ]
  },
  {
    "name": "reject_legacy",
    "disposition": "killed",
    "cases": 34,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-5-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-5-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-1000-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-1000-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-5-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-5-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-1000-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-1000-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_invalid_volume_retained[4-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_invalid_volume_retained[4-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_invalid_volume_retained[1001-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_invalid_volume_retained[1001-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_invalid_volume_retained[-1-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_invalid_volume_retained[-1-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_invalid_volume_retained[5.0-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_invalid_volume_retained[5.0-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_invalid_volume_retained[bad-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_invalid_volume_retained[bad-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_invalid_volume_retained[-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_invalid_volume_retained[-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_zero_price_clears[dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_zero_price_clears[sqlite]"
    ]
  },
  {
    "name": "no_reason",
    "disposition": "killed",
    "cases": 34,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_volume_guards::test_composite_volume_refused[dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_composite_volume_refused[sqlite]"
    ]
  },
  {
    "name": "leak_reason",
    "disposition": "killed",
    "cases": 34,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_volume_guards::test_composite_volume_refused[dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_composite_volume_refused[sqlite]"
    ]
  },
  {
    "name": "state_before_refusal",
    "disposition": "killed",
    "cases": 34,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_volume_guards::test_composite_volume_refused[dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_composite_volume_refused[sqlite]"
    ]
  },
  {
    "name": "data_before_refusal",
    "disposition": "killed",
    "cases": 34,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_volume_guards::test_composite_volume_refused[dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_composite_volume_refused[sqlite]"
    ]
  },
  {
    "name": "clear_before_refusal",
    "disposition": "killed",
    "cases": 34,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_volume_guards::test_composite_volume_refused[dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_composite_volume_refused[sqlite]"
    ]
  },
  {
    "name": "prompt_before_refusal",
    "disposition": "killed",
    "cases": 34,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_volume_guards::test_composite_volume_refused[dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_composite_volume_refused[sqlite]"
    ]
  },
  {
    "name": "db_before_refusal",
    "disposition": "killed",
    "cases": 34,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_volume_guards::test_composite_volume_refused[dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_composite_volume_refused[sqlite]"
    ]
  },
  {
    "name": "provider_before_refusal",
    "disposition": "killed",
    "cases": 34,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_volume_guards::test_composite_volume_refused[dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_composite_volume_refused[sqlite]"
    ]
  },
  {
    "name": "lower_boundary",
    "disposition": "killed",
    "cases": 34,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-5-None-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-5-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-5-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-5-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-5-None-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-5-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-5-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-5-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_zero_price_clears[dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_zero_price_clears[sqlite]"
    ]
  },
  {
    "name": "upper_boundary",
    "disposition": "killed",
    "cases": 34,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-1000-None-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-1000-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-1000-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-1000-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-1000-None-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-1000-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-1000-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-1000-legacy-sqlite]"
    ]
  },
  {
    "name": "omit_bounds",
    "disposition": "killed",
    "cases": 34,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_invalid_volume_retained[4-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_invalid_volume_retained[4-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_invalid_volume_retained[1001-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_invalid_volume_retained[1001-sqlite]"
    ]
  },
  {
    "name": "reject_valid_integer",
    "disposition": "killed",
    "cases": 34,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-5-None-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-5-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-5-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-5-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-1000-None-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-1000-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-1000-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-1000-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-5-None-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-5-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-5-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-5-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-1000-None-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-1000-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-1000-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-1000-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_invalid_volume_retained[4-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_invalid_volume_retained[4-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_invalid_volume_retained[1001-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_invalid_volume_retained[1001-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_zero_price_clears[dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_zero_price_clears[sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_composite_sibling_allows_volume[dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_composite_sibling_allows_volume[sqlite]"
    ]
  },
  {
    "name": "omit_trim",
    "disposition": "killed",
    "cases": 34,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-5-None-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-5-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-5-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-5-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-1000-None-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-1000-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-1000-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-1000-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-5-None-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-5-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-5-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-5-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-1000-None-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-1000-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-1000-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-1000-legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_price",
    "disposition": "killed",
    "cases": 34,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-5-None-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-5-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-5-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-5-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-1000-None-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-1000-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-1000-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-1000-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-5-None-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-5-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-5-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-5-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-1000-None-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-1000-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-1000-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-1000-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_composite_sibling_allows_volume[dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_composite_sibling_allows_volume[sqlite]"
    ]
  },
  {
    "name": "wrong_volume",
    "disposition": "killed",
    "cases": 34,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-5-None-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-5-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-5-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-5-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-1000-None-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-1000-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-1000-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-1000-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-5-None-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-5-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-5-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-5-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-1000-None-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-1000-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-1000-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-1000-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_composite_sibling_allows_volume[dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_composite_sibling_allows_volume[sqlite]"
    ]
  },
  {
    "name": "reject_free",
    "disposition": "killed",
    "cases": 34,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-5-None-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-5-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-5-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-5-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-5-None-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-5-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-5-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-5-legacy-sqlite]"
    ]
  },
  {
    "name": "zero_price_passes",
    "disposition": "killed",
    "cases": 34,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_zero_price_clears[dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_zero_price_clears[sqlite]"
    ]
  },
  {
    "name": "omit_zero_clear",
    "disposition": "killed",
    "cases": 34,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_zero_price_clears[dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_zero_price_clears[sqlite]"
    ]
  },
  {
    "name": "wrong_duration_state",
    "disposition": "killed",
    "cases": 34,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-5-None-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-5-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-5-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-5-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-1000-None-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-1000-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-1000-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-1000-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-5-None-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-5-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-5-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-5-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-1000-None-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-1000-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-1000-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-1000-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_composite_sibling_allows_volume[dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_composite_sibling_allows_volume[sqlite]"
    ]
  },
  {
    "name": "wrong_min_days",
    "disposition": "killed",
    "cases": 34,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-5-None-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-5-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-5-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-5-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-1000-None-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-1000-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-1000-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-1000-legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_max_days",
    "disposition": "killed",
    "cases": 34,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-5-None-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-5-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-5-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-5-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-1000-None-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-1000-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-1000-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-1000-legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_days_prompt",
    "disposition": "killed",
    "cases": 34,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-5-None-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-5-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-5-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-5-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-1000-None-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-1000-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-1000-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits0-1000-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-5-None-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-5-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-5-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-5-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-1000-None-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-1000-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-1000-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_legacy_volume_exact[limits1-1000-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_composite_sibling_allows_volume[dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_composite_sibling_allows_volume[sqlite]"
    ]
  },
  {
    "name": "scan_sibling",
    "disposition": "killed",
    "cases": 34,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_volume_guards::test_composite_sibling_allows_volume[dict]",
      "tests.integration.test_composite_telegram_custom_volume_guards::test_composite_sibling_allows_volume[sqlite]"
    ]
  }
]
```

Independent valid mutations, relevant assertion failures only. No survivors/errors/skips. Scratch auto-cleaned. Reference checks selected owned service before custom volume selected-product/pricing/FSM effects; real SQL and legacy controls preserved. No production implementation claim.
