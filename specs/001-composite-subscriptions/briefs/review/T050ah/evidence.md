# T050ah reference and mutation evidence

Source hashes:
```json
{
  "handlers_user.py": "611ce8a3ddab0d2298f0777187c6bf688958eaa2cce22fbabc2b3bf352182c90",
  "tests/integration/test_composite_telegram_custom_card_auto_guards.py": "2729becf7c05a422569d5eb7af80a06e27bfc928b658e83195a7c932c6f26810",
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
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[order-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[order-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[product-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[product-sqlite]"
    ]
  },
  {
    "name": "omit_order_guard",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[order-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[order-sqlite]"
    ]
  },
  {
    "name": "omit_product_guard",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[product-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[product-sqlite]"
    ]
  },
  {
    "name": "require_both_markers",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[order-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[order-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[product-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[product-sqlite]"
    ]
  },
  {
    "name": "wrong_order_kind",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[order-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[order-sqlite]"
    ]
  },
  {
    "name": "wrong_product_kind",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[product-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[product-sqlite]"
    ]
  },
  {
    "name": "reject_missing_marker",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-17-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-17-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_sibling_allows_custom_card[dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_sibling_allows_custom_card[sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_card_auto_reservation_error[dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_card_auto_reservation_error[sqlite]"
    ]
  },
  {
    "name": "reject_legacy_marker",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-17-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-17-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_card_entry_refusals[approved-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_card_entry_refusals[approved-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_card_entry_refusals[restricted-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_card_entry_refusals[restricted-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_card_entry_refusals[minimum-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_card_entry_refusals[minimum-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_card_minimum_boundary_allowed[dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_card_minimum_boundary_allowed[sqlite]"
    ]
  },
  {
    "name": "no_reason",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[order-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[order-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[product-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[product-sqlite]"
    ]
  },
  {
    "name": "leak_name",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[order-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[order-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[product-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[product-sqlite]"
    ]
  },
  {
    "name": "state_before_refusal",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[order-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[order-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[product-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[product-sqlite]"
    ]
  },
  {
    "name": "data_before_refusal",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[order-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[order-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[product-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[product-sqlite]"
    ]
  },
  {
    "name": "clear_before_refusal",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[order-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[order-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[product-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[product-sqlite]"
    ]
  },
  {
    "name": "prompt_before_refusal",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[order-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[order-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[product-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[product-sqlite]"
    ]
  },
  {
    "name": "ack_before_refusal",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[order-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[order-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[product-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[product-sqlite]"
    ]
  },
  {
    "name": "db_before_refusal",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[order-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[order-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[product-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[product-sqlite]"
    ]
  },
  {
    "name": "details_before_refusal",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[order-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[order-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[product-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[product-sqlite]"
    ]
  },
  {
    "name": "disabled_allowed",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_card_entry_refusals[disabled-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_card_entry_refusals[disabled-sqlite]"
    ]
  },
  {
    "name": "approved_allowed",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_card_entry_refusals[approved-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_card_entry_refusals[approved-sqlite]"
    ]
  },
  {
    "name": "ignore_method_error",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_card_entry_refusals[restricted-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_card_entry_refusals[restricted-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_card_entry_refusals[minimum-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_card_entry_refusals[minimum-sqlite]"
    ]
  },
  {
    "name": "wrong_duration",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-17-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-17-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-17-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-17-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_global_duration",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_username",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-17-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-17-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-17-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-17-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_sibling_allows_custom_card[dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_sibling_allows_custom_card[sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_card_minimum_boundary_allowed[dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_card_minimum_boundary_allowed[sqlite]"
    ]
  },
  {
    "name": "wrong_volume",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-17-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-17-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-17-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-17-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_sibling_allows_custom_card[dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_sibling_allows_custom_card[sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_card_minimum_boundary_allowed[dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_card_minimum_boundary_allowed[sqlite]"
    ]
  },
  {
    "name": "wrong_wallet",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_sibling_allows_custom_card[dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_sibling_allows_custom_card[sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_card_minimum_boundary_allowed[dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_card_minimum_boundary_allowed[sqlite]"
    ]
  },
  {
    "name": "wrong_final_price",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-17-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-17-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-17-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-17-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_sibling_allows_custom_card[dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_sibling_allows_custom_card[sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_card_minimum_boundary_allowed[dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_card_minimum_boundary_allowed[sqlite]"
    ]
  },
  {
    "name": "wrong_actor",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-17-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-17-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-17-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-17-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_sibling_allows_custom_card[dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_sibling_allows_custom_card[sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_card_minimum_boundary_allowed[dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_card_minimum_boundary_allowed[sqlite]"
    ]
  },
  {
    "name": "wrong_rial",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-17-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-17-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-17-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-17-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_sibling_allows_custom_card[dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_sibling_allows_custom_card[sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_card_minimum_boundary_allowed[dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_card_minimum_boundary_allowed[sqlite]"
    ]
  },
  {
    "name": "wrong_timeout",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-17-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-17-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-17-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-17-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_sibling_allows_custom_card[dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_sibling_allows_custom_card[sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_card_minimum_boundary_allowed[dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_card_minimum_boundary_allowed[sqlite]"
    ]
  },
  {
    "name": "wrong_check",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-17-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-17-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-17-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-17-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_sibling_allows_custom_card[dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_sibling_allows_custom_card[sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_card_minimum_boundary_allowed[dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_card_minimum_boundary_allowed[sqlite]"
    ]
  },
  {
    "name": "wrong_minimum_boundary",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_card_minimum_boundary_allowed[dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_card_minimum_boundary_allowed[sqlite]"
    ]
  },
  {
    "name": "early_reservation",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[order-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[order-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[product-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_custom_card_entry_refused[product-sqlite]"
    ]
  },
  {
    "name": "wrong_kind",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-17-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-17-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-17-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-17-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_sibling_allows_custom_card[dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_sibling_allows_custom_card[sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_card_minimum_boundary_allowed[dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_card_minimum_boundary_allowed[sqlite]"
    ]
  },
  {
    "name": "lose_reentry_reservation",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-17-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-17-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-17-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-17-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[0-None-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-17-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-None-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_custom_card_entry_exact[100-None-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_sibling_allows_custom_card[dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_composite_sibling_allows_custom_card[sqlite]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_card_minimum_boundary_allowed[dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_legacy_card_minimum_boundary_allowed[sqlite]"
    ]
  },
  {
    "name": "wrong_error_text",
    "disposition": "killed",
    "cases": 36,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_card_auto_reservation_error[dict]",
      "tests.integration.test_composite_telegram_custom_card_auto_guards::test_card_auto_reservation_error[sqlite]"
    ]
  }
]
```

Independent valid mutations, relevant assertion failures only. No survivors/errors/skips. Scratch auto-cleaned. Reference checks selected owned service before custom automatic-card reservation selected-order/product and card-details publication effects; real SQL and legacy controls preserved. No production implementation claim.
