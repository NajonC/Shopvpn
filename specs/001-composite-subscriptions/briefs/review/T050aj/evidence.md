# T050aj reference and mutation evidence

Source hashes:
```json
{
  "handlers_user.py": "611ce8a3ddab0d2298f0777187c6bf688958eaa2cce22fbabc2b3bf352182c90",
  "tests/integration/test_composite_telegram_custom_abangateway_guards.py": "0b525d12cc80495024c95fc6eac3e6bf8fbaec22a7bf7c1ee5b33e67f0850538",
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
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[order-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[order-sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[product-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[product-sqlite]"
    ]
  },
  {
    "name": "omit_order_guard",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[order-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[order-sqlite]"
    ]
  },
  {
    "name": "omit_product_guard",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[product-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[product-sqlite]"
    ]
  },
  {
    "name": "require_both_markers",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[order-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[order-sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[product-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[product-sqlite]"
    ]
  },
  {
    "name": "wrong_order_kind",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[order-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[order-sqlite]"
    ]
  },
  {
    "name": "wrong_product_kind",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[product-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[product-sqlite]"
    ]
  },
  {
    "name": "reject_missing_marker",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[0-None-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[0-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[100-None-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[100-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_sibling_allows_abangateway[dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_sibling_allows_abangateway[sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_abangateway_gateway_error[dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_abangateway_gateway_error[sqlite]"
    ]
  },
  {
    "name": "reject_legacy_marker",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[0-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[0-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[100-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[100-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_abangateway_refusals[approved-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_abangateway_refusals[approved-sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_abangateway_refusals[restricted-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_abangateway_refusals[restricted-sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_abangateway_refusals[minimum-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_abangateway_refusals[minimum-sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_abangateway_minimum_boundary[dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_abangateway_minimum_boundary[sqlite]"
    ]
  },
  {
    "name": "no_reason",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[order-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[order-sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[product-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[product-sqlite]"
    ]
  },
  {
    "name": "leak_name",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[order-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[order-sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[product-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[product-sqlite]"
    ]
  },
  {
    "name": "state_before_refusal",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[order-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[order-sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[product-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[product-sqlite]"
    ]
  },
  {
    "name": "data_before_refusal",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[order-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[order-sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[product-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[product-sqlite]"
    ]
  },
  {
    "name": "clear_before_refusal",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[order-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[order-sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[product-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[product-sqlite]"
    ]
  },
  {
    "name": "prompt_before_refusal",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[order-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[order-sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[product-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[product-sqlite]"
    ]
  },
  {
    "name": "ack_before_refusal",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[order-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[order-sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[product-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[product-sqlite]"
    ]
  },
  {
    "name": "db_before_refusal",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[order-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[order-sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[product-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[product-sqlite]"
    ]
  },
  {
    "name": "details_before_refusal",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[order-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[order-sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[product-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_custom_abangateway_refused[product-sqlite]"
    ]
  },
  {
    "name": "approved_allowed",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_abangateway_refusals[approved-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_abangateway_refusals[approved-sqlite]"
    ]
  },
  {
    "name": "ignore_method_error",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_abangateway_refusals[restricted-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_abangateway_refusals[restricted-sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_abangateway_refusals[minimum-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_abangateway_refusals[minimum-sqlite]"
    ]
  },
  {
    "name": "wrong_actor",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[0-None-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[0-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[0-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[0-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[100-None-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[100-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[100-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[100-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_sibling_allows_abangateway[dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_sibling_allows_abangateway[sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_abangateway_minimum_boundary[dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_abangateway_minimum_boundary[sqlite]"
    ]
  },
  {
    "name": "wrong_kind",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[0-None-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[0-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[0-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[0-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[100-None-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[100-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[100-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[100-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_sibling_allows_abangateway[dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_sibling_allows_abangateway[sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_abangateway_minimum_boundary[dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_abangateway_minimum_boundary[sqlite]"
    ]
  },
  {
    "name": "wrong_amount",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[0-None-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[0-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[0-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[0-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[100-None-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[100-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[100-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[100-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_sibling_allows_abangateway[dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_sibling_allows_abangateway[sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_abangateway_minimum_boundary[dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_abangateway_minimum_boundary[sqlite]"
    ]
  },
  {
    "name": "wrong_tenant",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[0-None-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[0-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[0-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[0-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[100-None-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[100-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[100-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[100-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_sibling_allows_abangateway[dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_sibling_allows_abangateway[sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_abangateway_minimum_boundary[dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_abangateway_minimum_boundary[sqlite]"
    ]
  },
  {
    "name": "wrong_order_name",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[0-None-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[0-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[0-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[0-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[100-None-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[100-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[100-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[100-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_sibling_allows_abangateway[dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_sibling_allows_abangateway[sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_abangateway_minimum_boundary[dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_abangateway_minimum_boundary[sqlite]"
    ]
  },
  {
    "name": "wrong_minimum_boundary",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_abangateway_minimum_boundary[dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_abangateway_minimum_boundary[sqlite]"
    ]
  },
  {
    "name": "wrong_error",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_abangateway_gateway_error[dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_abangateway_gateway_error[sqlite]"
    ]
  },
  {
    "name": "wrong_check_id",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[0-None-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[0-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[0-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[0-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[100-None-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[100-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[100-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_custom_abangateway_exact[100-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_sibling_allows_abangateway[dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_composite_sibling_allows_abangateway[sqlite]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_abangateway_minimum_boundary[dict]",
      "tests.integration.test_composite_telegram_custom_abangateway_guards::test_legacy_abangateway_minimum_boundary[sqlite]"
    ]
  }
]
```

Independent valid mutations, relevant assertion failures only. No survivors/errors/skips. Scratch auto-cleaned. Reference checks selected owned service before custom abangateway invoice selected-order/product and card-details publication effects; real SQL and legacy controls preserved. No production implementation claim.
