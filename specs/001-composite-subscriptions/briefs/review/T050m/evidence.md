# T050m custom checkout/receipt verification

Hashes:
```json
{
  "miniapp/server.py": "63b15cf1f0ae0940dfc2085544b096b3e73ae778c94102488a8e485f7aa99cbc",
  "tests/integration/test_composite_miniapp_custom_receipt_guards.py": "fc4f40419efd2a916510b7eb61d100e39df43ddd657bd4d70bd0c497680aff62",
  "tests/characterization/test_unsupported_surfaces.py": "4dee58c924d83f592f2c76dd71626addea7774f69f91bb219d3b1c38710e4bfd",
  "tests/characterization/test_receipt_linkage.py": "5282debcc60522ccd5ad4ea793a13ce2c9d481bb8dd79e088592f0e636feda42"
}
```

Results:
```json
[
  {
    "name": "reference",
    "disposition": "pass",
    "cases": 80,
    "failed_test_ids": []
  },
  {
    "name": "omit",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[purchase-request-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[purchase-request-30000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[purchase-request-100000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[purchase-request-100000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_stock-order-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_stock-order-30000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_stock-product-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_stock-product-30000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_custom-order-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_custom-order-30000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_renewal-order-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_renewal-order-30000-sqlite]"
    ]
  },
  {
    "name": "wrong_kind",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[purchase-request-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[purchase-request-30000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[purchase-request-100000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[purchase-request-100000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_stock-order-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_stock-order-30000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_stock-product-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_stock-product-30000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_custom-order-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_custom-order-30000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_renewal-order-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_renewal-order-30000-sqlite]"
    ]
  },
  {
    "name": "bypass_api_create_custom_config",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[purchase-request-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[purchase-request-30000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[purchase-request-100000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[purchase-request-100000-sqlite]"
    ]
  },
  {
    "name": "bypass_api_order_receipt",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_stock-order-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_stock-order-30000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_stock-product-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_stock-product-30000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_custom-order-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_custom-order-30000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_renewal-order-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_renewal-order-30000-sqlite]"
    ]
  },
  {
    "name": "omit_request",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[purchase-request-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[purchase-request-30000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[purchase-request-100000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[purchase-request-100000-sqlite]"
    ]
  },
  {
    "name": "omit_order",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_stock-order-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_stock-order-30000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_custom-order-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_custom-order-30000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_renewal-order-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_renewal-order-30000-sqlite]"
    ]
  },
  {
    "name": "omit_product",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_stock-product-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_stock-product-30000-sqlite]"
    ]
  },
  {
    "name": "reject_legacy",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[purchase-30000-legacy-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[purchase-30000-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[purchase-100000-legacy-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[purchase-100000-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_stock-30000-legacy-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_stock-30000-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_custom-30000-legacy-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_custom-30000-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_renewal-30000-legacy-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_renewal-30000-legacy-sqlite]"
    ]
  },
  {
    "name": "reject_absent",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[purchase-30000-None-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[purchase-30000-None-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[purchase-100000-None-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[purchase-100000-None-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_stock-30000-None-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_stock-30000-None-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_custom-30000-None-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_custom-30000-None-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_renewal-30000-None-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_renewal-30000-None-sqlite]"
    ]
  },
  {
    "name": "no_reason",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[purchase-request-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[purchase-request-30000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[purchase-request-100000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[purchase-request-100000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_stock-order-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_stock-order-30000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_stock-product-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_stock-product-30000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_custom-order-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_custom-order-30000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_renewal-order-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_renewal-order-30000-sqlite]"
    ]
  },
  {
    "name": "leak_link",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[purchase-request-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[purchase-request-30000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[purchase-request-100000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[purchase-request-100000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_stock-order-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_stock-order-30000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_stock-product-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_stock-product-30000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_custom-order-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_custom-order-30000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_renewal-order-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_renewal-order-30000-sqlite]"
    ]
  },
  {
    "name": "late_auth",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[purchase-request-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[purchase-request-30000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[purchase-request-100000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[purchase-request-100000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_stock-order-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_stock-order-30000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_stock-product-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_stock-product-30000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_custom-order-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_custom-order-30000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_renewal-order-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_renewal-order-30000-sqlite]"
    ]
  },
  {
    "name": "debit_before_refusal",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[purchase-request-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[purchase-request-30000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[purchase-request-100000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[purchase-request-100000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_stock-order-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_stock-order-30000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_stock-product-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_stock-product-30000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_custom-order-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_custom-order-30000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_renewal-order-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_renewal-order-30000-sqlite]"
    ]
  },
  {
    "name": "provider_before_refusal",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[purchase-request-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[purchase-request-30000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[purchase-request-100000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[purchase-request-100000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_stock-order-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_stock-order-30000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_stock-product-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_stock-product-30000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_custom-order-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_custom-order-30000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_renewal-order-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_renewal-order-30000-sqlite]"
    ]
  },
  {
    "name": "admin_delivery_before_refusal",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[purchase-request-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[purchase-request-30000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[purchase-request-100000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[purchase-request-100000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_stock-order-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_stock-order-30000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_stock-product-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_stock-product-30000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_custom-order-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_custom-order-30000-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_renewal-order-30000-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_composite_miniapp_custom_receipt_refused[receipt_renewal-order-30000-sqlite]"
    ]
  },
  {
    "name": "wrong_purchase_price",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[purchase-30000-None-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[purchase-30000-None-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[purchase-30000-legacy-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[purchase-30000-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[purchase-100000-None-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[purchase-100000-None-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[purchase-100000-legacy-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[purchase-100000-legacy-sqlite]"
    ]
  },
  {
    "name": "lost_wallet_debit",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[purchase-30000-None-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[purchase-30000-None-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[purchase-30000-legacy-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[purchase-30000-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[purchase-100000-None-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[purchase-100000-None-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[purchase-100000-legacy-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[purchase-100000-legacy-sqlite]"
    ]
  },
  {
    "name": "lost_purchase_approval",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[purchase-100000-None-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[purchase-100000-None-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[purchase-100000-legacy-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[purchase-100000-legacy-sqlite]"
    ]
  },
  {
    "name": "lost_local_record",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[purchase-100000-None-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[purchase-100000-None-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[purchase-100000-legacy-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[purchase-100000-legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_purchase_link",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[purchase-100000-None-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[purchase-100000-None-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[purchase-100000-legacy-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[purchase-100000-legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_provider_duration",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[purchase-100000-None-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[purchase-100000-None-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[purchase-100000-legacy-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[purchase-100000-legacy-sqlite]"
    ]
  },
  {
    "name": "lost_receipt_file",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_stock-30000-None-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_stock-30000-None-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_stock-30000-legacy-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_stock-30000-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_custom-30000-None-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_custom-30000-None-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_custom-30000-legacy-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_custom-30000-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_renewal-30000-None-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_renewal-30000-None-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_renewal-30000-legacy-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_renewal-30000-legacy-sqlite]"
    ]
  },
  {
    "name": "lost_admin_message",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_stock-30000-None-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_stock-30000-None-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_stock-30000-legacy-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_stock-30000-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_custom-30000-None-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_custom-30000-None-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_custom-30000-legacy-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_custom-30000-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_renewal-30000-None-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_renewal-30000-None-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_renewal-30000-legacy-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_renewal-30000-legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_approve_callback",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_stock-30000-None-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_stock-30000-None-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_stock-30000-legacy-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_stock-30000-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_custom-30000-None-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_custom-30000-None-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_custom-30000-legacy-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_custom-30000-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_renewal-30000-None-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_renewal-30000-None-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_renewal-30000-legacy-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_renewal-30000-legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_payable_caption",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_stock-30000-None-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_stock-30000-None-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_stock-30000-legacy-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_stock-30000-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_custom-30000-None-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_custom-30000-None-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_custom-30000-legacy-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_custom-30000-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_renewal-30000-None-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_renewal-30000-None-sqlite]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_renewal-30000-legacy-dict]",
      "tests.integration.test_composite_miniapp_custom_receipt_guards::test_legacy_miniapp_custom_receipt_preserved[receipt_renewal-30000-legacy-sqlite]"
    ]
  }
]
```

Independent mutants with relevant packet assertions only; no survivors/errors/skips. Real signed ownership and original legacy custom checkout and receipt storage/delivery preserved. Source-only scratch auto-cleaned; no production edits.
