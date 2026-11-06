# T050i retrieval verification

Hashes:
```json
{
  "miniapp/server.py": "63b15cf1f0ae0940dfc2085544b096b3e73ae778c94102488a8e485f7aa99cbc",
  "tests/integration/test_composite_miniapp_retrieval_guards.py": "c626c838b773b8dd98c8684c7677783f08b087e0edb00424242c815c73274267",
  "tests/characterization/test_unsupported_surfaces.py": "4dee58c924d83f592f2c76dd71626addea7774f69f91bb219d3b1c38710e4bfd"
}
```

Results:
```json
[
  {
    "name": "reference",
    "disposition": "pass",
    "cases": 95,
    "failed_test_ids": []
  },
  {
    "name": "omit",
    "disposition": "killed",
    "cases": 64,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[orders-order-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[orders-order-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[orders-product-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[orders-product-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[customs-custom-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[customs-custom-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_pool-order-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_pool-order-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_pool-product-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_pool-product-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_custom-custom-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_custom-custom-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-order-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-order-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-product-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-product-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-row-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-row-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_custom-custom-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_custom-custom-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_custom-row-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_custom-row-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[invoice_status-order-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[invoice_status-order-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[invoice_status-product-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[invoice_status-product-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[history-custom-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[history-custom-sqlite]"
    ]
  },
  {
    "name": "wrong_kind",
    "disposition": "killed",
    "cases": 64,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[orders-order-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[orders-order-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[orders-product-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[orders-product-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[customs-custom-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[customs-custom-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_pool-order-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_pool-order-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_pool-product-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_pool-product-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_custom-custom-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_custom-custom-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-order-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-order-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-product-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-product-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-row-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-row-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_custom-custom-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_custom-custom-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_custom-row-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_custom-row-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[invoice_status-order-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[invoice_status-order-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[invoice_status-product-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[invoice_status-product-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[history-custom-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[history-custom-sqlite]"
    ]
  },
  {
    "name": "bypass_api_orders",
    "disposition": "killed",
    "cases": 64,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[orders-order-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[orders-order-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[orders-product-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[orders-product-sqlite]"
    ]
  },
  {
    "name": "bypass_api_custom_configs",
    "disposition": "killed",
    "cases": 64,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[customs-custom-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[customs-custom-sqlite]"
    ]
  },
  {
    "name": "bypass_api_sub_info",
    "disposition": "killed",
    "cases": 64,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_pool-order-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_pool-order-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_pool-product-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_pool-product-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_custom-custom-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_custom-custom-sqlite]"
    ]
  },
  {
    "name": "bypass_api_expiring",
    "disposition": "killed",
    "cases": 64,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-order-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-order-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-product-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-product-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-row-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-row-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_custom-custom-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_custom-custom-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_custom-row-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_custom-row-sqlite]"
    ]
  },
  {
    "name": "bypass_api_card_auto_invoice_status",
    "disposition": "killed",
    "cases": 64,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[invoice_status-order-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[invoice_status-order-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[invoice_status-product-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[invoice_status-product-sqlite]"
    ]
  },
  {
    "name": "bypass_api_custom_config_history",
    "disposition": "killed",
    "cases": 64,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[history-custom-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[history-custom-sqlite]"
    ]
  },
  {
    "name": "omit_orders",
    "disposition": "killed",
    "cases": 64,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[orders-order-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[orders-order-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_pool-order-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_pool-order-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-order-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-order-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[invoice_status-order-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[invoice_status-order-sqlite]"
    ]
  },
  {
    "name": "omit_customs",
    "disposition": "killed",
    "cases": 64,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[customs-custom-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[customs-custom-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_custom-custom-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_custom-custom-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_custom-custom-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_custom-custom-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[history-custom-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[history-custom-sqlite]"
    ]
  },
  {
    "name": "omit_rows",
    "disposition": "killed",
    "cases": 64,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-row-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-row-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_custom-row-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_custom-row-sqlite]"
    ]
  },
  {
    "name": "omit_products",
    "disposition": "killed",
    "cases": 64,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[orders-product-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[orders-product-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_pool-product-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_pool-product-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-product-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-product-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[invoice_status-product-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[invoice_status-product-sqlite]"
    ]
  },
  {
    "name": "reject_legacy",
    "disposition": "killed",
    "cases": 64,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[orders-legacy-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[orders-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[customs-legacy-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[customs-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[sub_pool-legacy-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[sub_pool-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[sub_custom-legacy-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[sub_custom-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[expiring_pool-legacy-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[expiring_pool-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[expiring_custom-legacy-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[expiring_custom-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[invoice_status-legacy-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[invoice_status-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[history-legacy-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[history-legacy-sqlite]"
    ]
  },
  {
    "name": "reject_absent",
    "disposition": "killed",
    "cases": 64,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[orders-None-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[orders-None-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[customs-None-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[customs-None-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[sub_pool-None-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[sub_pool-None-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[sub_custom-None-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[sub_custom-None-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[expiring_pool-None-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[expiring_pool-None-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[expiring_custom-None-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[expiring_custom-None-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[invoice_status-None-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[invoice_status-None-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[history-None-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[history-None-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_requested_legacy_service_not_blocked_by_unrelated_composite[sub_pool-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_requested_legacy_service_not_blocked_by_unrelated_composite[sub_pool-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_requested_legacy_service_not_blocked_by_unrelated_composite[expiring_pool-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_requested_legacy_service_not_blocked_by_unrelated_composite[expiring_pool-sqlite]"
    ]
  },
  {
    "name": "no_reason",
    "disposition": "killed",
    "cases": 64,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[orders-order-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[orders-order-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[orders-product-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[orders-product-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[customs-custom-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[customs-custom-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_pool-order-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_pool-order-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_pool-product-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_pool-product-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_custom-custom-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_custom-custom-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-order-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-order-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-product-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-product-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-row-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-row-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_custom-custom-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_custom-custom-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_custom-row-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_custom-row-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[invoice_status-order-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[invoice_status-order-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[invoice_status-product-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[invoice_status-product-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[history-custom-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[history-custom-sqlite]"
    ]
  },
  {
    "name": "leak_link_or_name",
    "disposition": "killed",
    "cases": 64,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[orders-order-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[orders-order-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[orders-product-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[orders-product-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[customs-custom-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[customs-custom-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_pool-order-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_pool-order-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_pool-product-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_pool-product-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_custom-custom-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_custom-custom-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-order-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-order-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-product-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-product-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-row-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-row-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_custom-custom-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_custom-custom-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_custom-row-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_custom-row-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[invoice_status-order-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[invoice_status-order-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[invoice_status-product-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[invoice_status-product-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[history-custom-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[history-custom-sqlite]"
    ]
  },
  {
    "name": "late_auth",
    "disposition": "killed",
    "cases": 64,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[orders-order-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[orders-order-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[orders-product-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[orders-product-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[customs-custom-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[customs-custom-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_pool-order-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_pool-order-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_pool-product-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_pool-product-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_custom-custom-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_custom-custom-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-order-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-order-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-product-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-product-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-row-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-row-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_custom-custom-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_custom-custom-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_custom-row-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_custom-row-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[invoice_status-order-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[invoice_status-order-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[invoice_status-product-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[invoice_status-product-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[history-custom-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[history-custom-sqlite]"
    ]
  },
  {
    "name": "fetch_before_refusal",
    "disposition": "killed",
    "cases": 64,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[orders-order-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[orders-order-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[orders-product-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[orders-product-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[customs-custom-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[customs-custom-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_pool-order-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_pool-order-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_pool-product-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_pool-product-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_custom-custom-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[sub_custom-custom-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-order-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-order-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-product-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-product-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-row-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_pool-row-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_custom-custom-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_custom-custom-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_custom-row-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[expiring_custom-row-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[invoice_status-order-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[invoice_status-order-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[invoice_status-product-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[invoice_status-product-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[history-custom-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_composite_miniapp_retrieval_refused[history-custom-sqlite]"
    ]
  },
  {
    "name": "block_unrelated_sub_info",
    "disposition": "killed",
    "cases": 64,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_retrieval_guards::test_requested_legacy_service_not_blocked_by_unrelated_composite[sub_pool-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_requested_legacy_service_not_blocked_by_unrelated_composite[sub_pool-sqlite]"
    ]
  },
  {
    "name": "block_unrelated_expiry",
    "disposition": "killed",
    "cases": 64,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_retrieval_guards::test_requested_legacy_service_not_blocked_by_unrelated_composite[expiring_pool-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_requested_legacy_service_not_blocked_by_unrelated_composite[expiring_pool-sqlite]"
    ]
  },
  {
    "name": "wrong_order_link",
    "disposition": "killed",
    "cases": 64,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[orders-None-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[orders-None-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[orders-legacy-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[orders-legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_custom_link",
    "disposition": "killed",
    "cases": 64,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[customs-None-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[customs-None-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[customs-legacy-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[customs-legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_sub_info",
    "disposition": "killed",
    "cases": 64,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[sub_pool-None-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[sub_pool-None-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[sub_pool-legacy-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[sub_pool-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[sub_custom-None-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[sub_custom-None-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[sub_custom-legacy-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[sub_custom-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_requested_legacy_service_not_blocked_by_unrelated_composite[sub_pool-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_requested_legacy_service_not_blocked_by_unrelated_composite[sub_pool-sqlite]"
    ]
  },
  {
    "name": "lost_expiring",
    "disposition": "killed",
    "cases": 64,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[expiring_pool-None-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[expiring_pool-None-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[expiring_pool-legacy-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[expiring_pool-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[expiring_custom-None-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[expiring_custom-None-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[expiring_custom-legacy-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[expiring_custom-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_requested_legacy_service_not_blocked_by_unrelated_composite[expiring_pool-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_requested_legacy_service_not_blocked_by_unrelated_composite[expiring_pool-sqlite]"
    ]
  },
  {
    "name": "lost_history",
    "disposition": "killed",
    "cases": 64,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[history-None-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[history-None-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[history-legacy-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[history-legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_invoice_amount",
    "disposition": "killed",
    "cases": 64,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[invoice_status-None-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[invoice_status-None-sqlite]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[invoice_status-legacy-dict]",
      "tests.integration.test_composite_miniapp_retrieval_guards::test_legacy_miniapp_retrieval_preserved[invoice_status-legacy-sqlite]"
    ]
  }
]
```

Independent mutants with relevant packet assertions only; no survivors/errors/skips. Real signed ownership and original legacy exports preserved; unrelated composites do not block requested legacy sub/expiry. Source-only scratch auto-cleaned; no production edits.
