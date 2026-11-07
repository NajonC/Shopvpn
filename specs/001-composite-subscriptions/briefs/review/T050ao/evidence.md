# T050ao reference and mutation evidence

Source hashes:
```json
{
  "handlers_user.py": "611ce8a3ddab0d2298f0777187c6bf688958eaa2cce22fbabc2b3bf352182c90",
  "tests/integration/test_composite_telegram_custom_fixed_checkout_guards.py": "074742649fd5a9d10b6afe7605a80d01d80578dd6fcf6cc7f9e6363b19cefad4",
  "tests/characterization/test_callbacks_fsm.py": "b9c63f3386ab154a9082415edcfdbdd61dc7fb895d1e91b5fd1401fe4edd1817"
}
```

Results:
```json
[
  {
    "name": "reference",
    "disposition": "passed",
    "cases": 53,
    "failed_test_ids": []
  },
  {
    "name": "omit_guard",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_fixed_checkout_refused[dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_fixed_checkout_refused[sqlite]"
    ]
  },
  {
    "name": "wrong_kind",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_fixed_checkout_refused[dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_fixed_checkout_refused[sqlite]"
    ]
  },
  {
    "name": "reject_missing",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-5-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-5-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-1000-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-1000-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_sibling_allows_fixed_checkout[dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_sibling_allows_fixed_checkout[sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_invalid_volume[4-False-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_invalid_volume[4-False-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_invalid_volume[1001-False-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_invalid_volume[1001-False-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_invalid_volume[bad-False-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_invalid_volume[bad-False-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_unavailable_server_fixed_checkout[dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_unavailable_server_fixed_checkout[sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_unavailable_payment_fixed_checkout_compensates[0-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_unavailable_payment_fixed_checkout_compensates[0-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_unavailable_payment_fixed_checkout_compensates[100-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_unavailable_payment_fixed_checkout_compensates[100-sqlite]"
    ]
  },
  {
    "name": "reject_legacy",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-5-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-5-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-1000-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-1000-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_card_only[dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_card_only[sqlite]"
    ]
  },
  {
    "name": "no_reason",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_fixed_checkout_refused[dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_fixed_checkout_refused[sqlite]"
    ]
  },
  {
    "name": "leak_reason",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_fixed_checkout_refused[dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_fixed_checkout_refused[sqlite]"
    ]
  },
  {
    "name": "state_before_refusal",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_fixed_checkout_refused[dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_fixed_checkout_refused[sqlite]"
    ]
  },
  {
    "name": "data_before_refusal",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_fixed_checkout_refused[dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_fixed_checkout_refused[sqlite]"
    ]
  },
  {
    "name": "clear_before_refusal",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_fixed_checkout_refused[dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_fixed_checkout_refused[sqlite]"
    ]
  },
  {
    "name": "prompt_before_refusal",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_fixed_checkout_refused[dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_fixed_checkout_refused[sqlite]"
    ]
  },
  {
    "name": "db_before_refusal",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_fixed_checkout_refused[dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_fixed_checkout_refused[sqlite]"
    ]
  },
  {
    "name": "provider_before_refusal",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_fixed_checkout_refused[dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_fixed_checkout_refused[sqlite]"
    ]
  },
  {
    "name": "lower_boundary",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-5-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-5-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-5-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-5-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-legacy-sqlite]"
    ]
  },
  {
    "name": "upper_boundary",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-1000-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-1000-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-1000-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-1000-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-legacy-sqlite]"
    ]
  },
  {
    "name": "omit_trim",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-5-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-5-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-5-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-5-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-1000-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-1000-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-1000-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-1000-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_global_checkout_fallback[0-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_global_checkout_fallback[0-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_global_checkout_fallback[100-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_global_checkout_fallback[100-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_card_only[dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_card_only[sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_sibling_allows_fixed_checkout[dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_sibling_allows_fixed_checkout[sqlite]"
    ]
  },
  {
    "name": "wrong_final_days",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-5-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-5-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-5-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-5-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-1000-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-1000-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-1000-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-1000-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_global_checkout_fallback[0-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_global_checkout_fallback[0-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_global_checkout_fallback[100-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_global_checkout_fallback[100-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_card_only[dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_card_only[sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_sibling_allows_fixed_checkout[dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_sibling_allows_fixed_checkout[sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_unavailable_payment_fixed_checkout_compensates[0-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_unavailable_payment_fixed_checkout_compensates[0-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_unavailable_payment_fixed_checkout_compensates[100-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_unavailable_payment_fixed_checkout_compensates[100-sqlite]"
    ]
  },
  {
    "name": "global_duration",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_global_checkout_fallback[0-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_global_checkout_fallback[0-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_global_checkout_fallback[100-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_global_checkout_fallback[100-sqlite]"
    ]
  },
  {
    "name": "wrong_price",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-5-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-5-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-5-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-5-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-1000-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-1000-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-1000-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-1000-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_global_checkout_fallback[0-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_global_checkout_fallback[0-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_global_checkout_fallback[100-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_global_checkout_fallback[100-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_card_only[dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_card_only[sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_sibling_allows_fixed_checkout[dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_sibling_allows_fixed_checkout[sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_unavailable_payment_fixed_checkout_compensates[0-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_unavailable_payment_fixed_checkout_compensates[0-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_unavailable_payment_fixed_checkout_compensates[100-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_unavailable_payment_fixed_checkout_compensates[100-sqlite]"
    ]
  },
  {
    "name": "wrong_volume",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-5-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-5-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-5-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-5-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-1000-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-1000-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-1000-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-1000-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_global_checkout_fallback[0-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_global_checkout_fallback[0-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_global_checkout_fallback[100-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_global_checkout_fallback[100-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_card_only[dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_card_only[sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_sibling_allows_fixed_checkout[dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_sibling_allows_fixed_checkout[sqlite]"
    ]
  },
  {
    "name": "wrong_user",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-5-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-5-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-5-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-5-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-1000-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-1000-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-1000-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-1000-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_global_checkout_fallback[0-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_global_checkout_fallback[0-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_global_checkout_fallback[100-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_global_checkout_fallback[100-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_card_only[dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_card_only[sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_sibling_allows_fixed_checkout[dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_sibling_allows_fixed_checkout[sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_unavailable_payment_fixed_checkout_compensates[0-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_unavailable_payment_fixed_checkout_compensates[0-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_unavailable_payment_fixed_checkout_compensates[100-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_unavailable_payment_fixed_checkout_compensates[100-sqlite]"
    ]
  },
  {
    "name": "wrong_username",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-5-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-5-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-5-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-5-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-1000-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-1000-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-1000-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-1000-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_global_checkout_fallback[0-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_global_checkout_fallback[0-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_global_checkout_fallback[100-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_global_checkout_fallback[100-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_card_only[dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_card_only[sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_sibling_allows_fixed_checkout[dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_sibling_allows_fixed_checkout[sqlite]"
    ]
  },
  {
    "name": "omit_debit",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_global_checkout_fallback[100-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_global_checkout_fallback[100-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_sibling_allows_fixed_checkout[dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_sibling_allows_fixed_checkout[sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_unavailable_payment_fixed_checkout_compensates[100-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_unavailable_payment_fixed_checkout_compensates[100-sqlite]"
    ]
  },
  {
    "name": "double_debit",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_global_checkout_fallback[100-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_global_checkout_fallback[100-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_sibling_allows_fixed_checkout[dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_sibling_allows_fixed_checkout[sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_unavailable_payment_fixed_checkout_compensates[100-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_unavailable_payment_fixed_checkout_compensates[100-sqlite]"
    ]
  },
  {
    "name": "wrong_wallet_order",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_global_checkout_fallback[100-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_global_checkout_fallback[100-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_sibling_allows_fixed_checkout[dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_sibling_allows_fixed_checkout[sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_unavailable_payment_fixed_checkout_compensates[100-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_unavailable_payment_fixed_checkout_compensates[100-sqlite]"
    ]
  },
  {
    "name": "wrong_product",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-5-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-5-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-5-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-5-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-1000-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-1000-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-1000-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-1000-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_card_only[dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_card_only[sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_sibling_allows_fixed_checkout[dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_sibling_allows_fixed_checkout[sqlite]"
    ]
  },
  {
    "name": "wrong_state",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-5-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-5-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-5-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-5-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-1000-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-1000-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-1000-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-1000-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_global_checkout_fallback[0-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_global_checkout_fallback[0-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_global_checkout_fallback[100-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_global_checkout_fallback[100-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_card_only[dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_card_only[sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_sibling_allows_fixed_checkout[dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_sibling_allows_fixed_checkout[sqlite]"
    ]
  },
  {
    "name": "omit_order_id",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-5-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-5-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-5-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-5-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-1000-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-1000-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-1000-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[0-1000-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-5-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-None-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_checkout_exact[100-1000-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_global_checkout_fallback[0-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_global_checkout_fallback[0-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_global_checkout_fallback[100-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_global_checkout_fallback[100-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_card_only[dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_card_only[sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_sibling_allows_fixed_checkout[dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_sibling_allows_fixed_checkout[sqlite]"
    ]
  },
  {
    "name": "ignore_wallet_restriction",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_card_only[dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_card_only[sqlite]"
    ]
  },
  {
    "name": "scan_sibling",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_sibling_allows_fixed_checkout[dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_sibling_allows_fixed_checkout[sqlite]"
    ]
  },
  {
    "name": "omit_global_low_limit",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_invalid_volume[4-True-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_invalid_volume[4-True-sqlite]"
    ]
  },
  {
    "name": "omit_global_high_limit",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_invalid_volume[1001-True-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_invalid_volume[1001-True-sqlite]"
    ]
  },
  {
    "name": "omit_product_low_limit",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_invalid_volume[4-False-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_invalid_volume[4-False-sqlite]"
    ]
  },
  {
    "name": "omit_product_high_limit",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_invalid_volume[1001-False-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_legacy_fixed_invalid_volume[1001-False-sqlite]"
    ]
  },
  {
    "name": "skip_server_guard",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_unavailable_server_fixed_checkout[dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_unavailable_server_fixed_checkout[sqlite]"
    ]
  },
  {
    "name": "skip_payment_guard",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_unavailable_payment_fixed_checkout_compensates[0-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_unavailable_payment_fixed_checkout_compensates[0-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_unavailable_payment_fixed_checkout_compensates[100-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_unavailable_payment_fixed_checkout_compensates[100-sqlite]"
    ]
  },
  {
    "name": "no_unavailable_refund",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_unavailable_payment_fixed_checkout_compensates[0-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_unavailable_payment_fixed_checkout_compensates[0-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_unavailable_payment_fixed_checkout_compensates[100-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_unavailable_payment_fixed_checkout_compensates[100-sqlite]"
    ]
  },
  {
    "name": "price_before_refusal",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_fixed_checkout_refused[dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_composite_fixed_checkout_refused[sqlite]"
    ]
  },
  {
    "name": "double_unavailable_refund",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_unavailable_payment_fixed_checkout_compensates[0-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_unavailable_payment_fixed_checkout_compensates[0-sqlite]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_unavailable_payment_fixed_checkout_compensates[100-dict]",
      "tests.integration.test_composite_telegram_custom_fixed_checkout_guards::test_unavailable_payment_fixed_checkout_compensates[100-sqlite]"
    ]
  }
]
```

Independent valid mutations, relevant assertion failures only. No survivors/errors/skips. Scratch auto-cleaned. Reference checks selected owned service before fixed custom checkout selected-product before pricing/FSM/order/wallet/provider effects; real SQL and legacy controls preserved. No production implementation claim.
