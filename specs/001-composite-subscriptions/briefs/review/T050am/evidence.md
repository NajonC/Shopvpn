# T050am reference and mutation evidence

Source hashes:
```json
{
  "handlers_user.py": "611ce8a3ddab0d2298f0777187c6bf688958eaa2cce22fbabc2b3bf352182c90",
  "tests/integration/test_composite_telegram_custom_customgw_guards.py": "1c20111ae609ee5a1389c6c9a1ae77e9d13c40ddcd8e7ae4e73ddfee7da27f92",
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
    "name": "omit_guard",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[order-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[order-sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[product-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[product-sqlite]"
    ]
  },
  {
    "name": "omit_order_guard",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[order-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[order-sqlite]"
    ]
  },
  {
    "name": "omit_product_guard",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[product-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[product-sqlite]"
    ]
  },
  {
    "name": "require_both_markers",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[order-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[order-sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[product-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[product-sqlite]"
    ]
  },
  {
    "name": "wrong_order_kind",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[order-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[order-sqlite]"
    ]
  },
  {
    "name": "wrong_product_kind",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[product-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[product-sqlite]"
    ]
  },
  {
    "name": "reject_missing_marker",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[0-None-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[0-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[100-None-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[100-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_sibling_allows_customgw[dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_sibling_allows_customgw[sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_gateway_error[dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_gateway_error[sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_without_url[dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_without_url[sqlite]"
    ]
  },
  {
    "name": "reject_legacy_marker",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[0-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[0-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[100-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[100-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_refusals[approved-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_refusals[approved-sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_refusals[restricted-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_refusals[restricted-sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_refusals[minimum-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_refusals[minimum-sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_refusals[disabled-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_refusals[disabled-sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_refusals[no_gateway-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_refusals[no_gateway-sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_minimum_boundary[dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_minimum_boundary[sqlite]"
    ]
  },
  {
    "name": "no_reason",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[order-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[order-sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[product-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[product-sqlite]"
    ]
  },
  {
    "name": "leak_name",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[order-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[order-sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[product-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[product-sqlite]"
    ]
  },
  {
    "name": "state_before_refusal",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[order-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[order-sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[product-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[product-sqlite]"
    ]
  },
  {
    "name": "data_before_refusal",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[order-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[order-sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[product-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[product-sqlite]"
    ]
  },
  {
    "name": "clear_before_refusal",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[order-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[order-sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[product-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[product-sqlite]"
    ]
  },
  {
    "name": "prompt_before_refusal",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[order-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[order-sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[product-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[product-sqlite]"
    ]
  },
  {
    "name": "ack_before_refusal",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[order-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[order-sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[product-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[product-sqlite]"
    ]
  },
  {
    "name": "db_before_refusal",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[order-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[order-sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[product-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[product-sqlite]"
    ]
  },
  {
    "name": "details_before_refusal",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[order-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[order-sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[product-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_custom_customgw_refused[product-sqlite]"
    ]
  },
  {
    "name": "approved_allowed",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_refusals[approved-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_refusals[approved-sqlite]"
    ]
  },
  {
    "name": "ignore_method_error",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_refusals[restricted-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_refusals[restricted-sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_refusals[minimum-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_refusals[minimum-sqlite]"
    ]
  },
  {
    "name": "wrong_actor",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[0-None-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[0-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[0-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[0-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[100-None-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[100-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[100-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[100-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_sibling_allows_customgw[dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_sibling_allows_customgw[sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_minimum_boundary[dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_minimum_boundary[sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_without_url[dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_without_url[sqlite]"
    ]
  },
  {
    "name": "wrong_kind",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[0-None-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[0-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[0-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[0-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[100-None-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[100-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[100-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[100-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_sibling_allows_customgw[dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_sibling_allows_customgw[sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_minimum_boundary[dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_minimum_boundary[sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_without_url[dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_without_url[sqlite]"
    ]
  },
  {
    "name": "wrong_amount",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[0-None-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[0-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[0-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[0-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[100-None-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[100-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[100-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[100-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_sibling_allows_customgw[dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_sibling_allows_customgw[sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_minimum_boundary[dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_minimum_boundary[sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_without_url[dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_without_url[sqlite]"
    ]
  },
  {
    "name": "wrong_tenant",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[0-None-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[0-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[0-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[0-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[100-None-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[100-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[100-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[100-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_sibling_allows_customgw[dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_sibling_allows_customgw[sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_minimum_boundary[dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_minimum_boundary[sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_without_url[dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_without_url[sqlite]"
    ]
  },
  {
    "name": "wrong_order_name",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[0-None-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[0-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[0-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[0-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[100-None-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[100-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[100-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_custom_customgw_exact[100-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_sibling_allows_customgw[dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_composite_sibling_allows_customgw[sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_minimum_boundary[dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_minimum_boundary[sqlite]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_without_url[dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_without_url[sqlite]"
    ]
  },
  {
    "name": "wrong_minimum_boundary",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_minimum_boundary[dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_minimum_boundary[sqlite]"
    ]
  },
  {
    "name": "wrong_error",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_gateway_error[dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_gateway_error[sqlite]"
    ]
  },
  {
    "name": "disabled_gateway_allowed",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_refusals[disabled-dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_refusals[disabled-sqlite]"
    ]
  },
  {
    "name": "no_url_wrong_message",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_without_url[dict]",
      "tests.integration.test_composite_telegram_custom_customgw_guards::test_legacy_customgw_without_url[sqlite]"
    ]
  }
]
```

Independent valid mutations, relevant assertion failures only. No survivors/errors/skips. Scratch auto-cleaned. Reference checks selected owned service before custom customgw invoice selected-order/product and card-details publication effects; real SQL and legacy controls preserved. No production implementation claim.
