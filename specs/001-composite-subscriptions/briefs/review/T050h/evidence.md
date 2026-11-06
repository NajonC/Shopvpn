# T050h checkout/invoice verification

Hashes:
```json
{
  "miniapp/server.py": "63b15cf1f0ae0940dfc2085544b096b3e73ae778c94102488a8e485f7aa99cbc",
  "tests/integration/test_composite_miniapp_purchase_invoice_guards.py": "a2480471c7a472bfa4b1e32cd31bcd4ea21d16a2bf659431b26e156dccb97514",
  "tests/characterization/test_unsupported_surfaces.py": "4dee58c924d83f592f2c76dd71626addea7774f69f91bb219d3b1c38710e4bfd"
}
```

Results:
```json
[
  {
    "name": "reference",
    "disposition": "pass",
    "cases": 135,
    "failed_test_ids": []
  },
  {
    "name": "omit_guard",
    "disposition": "killed",
    "cases": 104,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[purchase-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[purchase-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[purchase-request-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[purchase-request-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[crypto-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[crypto-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[crypto-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[crypto-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[abangateway-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[abangateway-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[abangateway-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[abangateway-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[blupal-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[blupal-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[blupal-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[blupal-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[noapay-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[noapay-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[noapay-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[noapay-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[custom:synthetic-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[custom:synthetic-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[custom:synthetic-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[custom:synthetic-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[card_auto-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[card_auto-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[card_auto-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[card_auto-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:zarinpal-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:zarinpal-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:zarinpal-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:zarinpal-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:aqayepardakht-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:aqayepardakht-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:aqayepardakht-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:aqayepardakht-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tetra98-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tetra98-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tetra98-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tetra98-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:cubepay-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:cubepay-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:cubepay-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:cubepay-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:nowpayments-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:nowpayments-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:nowpayments-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:nowpayments-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tgstars-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tgstars-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tgstars-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tgstars-order-sqlite]"
    ]
  },
  {
    "name": "wrong_kind",
    "disposition": "killed",
    "cases": 104,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[purchase-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[purchase-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[crypto-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[crypto-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[crypto-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[crypto-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[abangateway-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[abangateway-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[abangateway-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[abangateway-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[blupal-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[blupal-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[blupal-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[blupal-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[noapay-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[noapay-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[noapay-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[noapay-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[custom:synthetic-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[custom:synthetic-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[custom:synthetic-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[custom:synthetic-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[card_auto-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[card_auto-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[card_auto-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[card_auto-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:zarinpal-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:zarinpal-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:zarinpal-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:zarinpal-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:aqayepardakht-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:aqayepardakht-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:aqayepardakht-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:aqayepardakht-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tetra98-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tetra98-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tetra98-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tetra98-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:cubepay-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:cubepay-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:cubepay-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:cubepay-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:nowpayments-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:nowpayments-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:nowpayments-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:nowpayments-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tgstars-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tgstars-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tgstars-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tgstars-order-sqlite]"
    ]
  },
  {
    "name": "omit_request_marker",
    "disposition": "killed",
    "cases": 104,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[purchase-request-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[purchase-request-sqlite]"
    ]
  },
  {
    "name": "omit_order",
    "disposition": "killed",
    "cases": 104,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[crypto-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[crypto-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[abangateway-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[abangateway-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[blupal-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[blupal-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[noapay-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[noapay-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[custom:synthetic-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[custom:synthetic-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[card_auto-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[card_auto-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:zarinpal-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:zarinpal-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:aqayepardakht-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:aqayepardakht-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tetra98-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tetra98-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:cubepay-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:cubepay-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:nowpayments-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:nowpayments-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tgstars-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tgstars-order-sqlite]"
    ]
  },
  {
    "name": "omit_product",
    "disposition": "killed",
    "cases": 104,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[purchase-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[purchase-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[crypto-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[crypto-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[abangateway-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[abangateway-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[blupal-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[blupal-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[noapay-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[noapay-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[custom:synthetic-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[custom:synthetic-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[card_auto-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[card_auto-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:zarinpal-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:zarinpal-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:aqayepardakht-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:aqayepardakht-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tetra98-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tetra98-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:cubepay-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:cubepay-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:nowpayments-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:nowpayments-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tgstars-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tgstars-product-sqlite]"
    ]
  },
  {
    "name": "bypass_api_create_order",
    "disposition": "killed",
    "cases": 104,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[purchase-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[purchase-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[purchase-request-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[purchase-request-sqlite]"
    ]
  },
  {
    "name": "bypass_api_order_crypto_invoice",
    "disposition": "killed",
    "cases": 104,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[crypto-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[crypto-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[crypto-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[crypto-order-sqlite]"
    ]
  },
  {
    "name": "bypass_api_order_abangateway_invoice",
    "disposition": "killed",
    "cases": 104,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[abangateway-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[abangateway-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[abangateway-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[abangateway-order-sqlite]"
    ]
  },
  {
    "name": "bypass_api_order_blupal_invoice",
    "disposition": "killed",
    "cases": 104,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[blupal-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[blupal-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[blupal-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[blupal-order-sqlite]"
    ]
  },
  {
    "name": "bypass_api_order_noapay_invoice",
    "disposition": "killed",
    "cases": 104,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[noapay-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[noapay-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[noapay-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[noapay-order-sqlite]"
    ]
  },
  {
    "name": "bypass_api_order_extra_gateway_invoice",
    "disposition": "killed",
    "cases": 104,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:zarinpal-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:zarinpal-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:zarinpal-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:zarinpal-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:aqayepardakht-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:aqayepardakht-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:aqayepardakht-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:aqayepardakht-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tetra98-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tetra98-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tetra98-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tetra98-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:cubepay-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:cubepay-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:cubepay-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:cubepay-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:nowpayments-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:nowpayments-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:nowpayments-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:nowpayments-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tgstars-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tgstars-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tgstars-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tgstars-order-sqlite]"
    ]
  },
  {
    "name": "bypass_api_order_custom_gateway_invoice",
    "disposition": "killed",
    "cases": 104,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[custom:synthetic-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[custom:synthetic-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[custom:synthetic-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[custom:synthetic-order-sqlite]"
    ]
  },
  {
    "name": "bypass_api_order_card_auto_invoice",
    "disposition": "killed",
    "cases": 104,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[card_auto-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[card_auto-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[card_auto-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[card_auto-order-sqlite]"
    ]
  },
  {
    "name": "bypass_extra_zarinpal",
    "disposition": "killed",
    "cases": 104,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:zarinpal-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:zarinpal-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:zarinpal-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:zarinpal-order-sqlite]"
    ]
  },
  {
    "name": "bypass_extra_aqayepardakht",
    "disposition": "killed",
    "cases": 104,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:aqayepardakht-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:aqayepardakht-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:aqayepardakht-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:aqayepardakht-order-sqlite]"
    ]
  },
  {
    "name": "bypass_extra_tetra98",
    "disposition": "killed",
    "cases": 104,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tetra98-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tetra98-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tetra98-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tetra98-order-sqlite]"
    ]
  },
  {
    "name": "bypass_extra_cubepay",
    "disposition": "killed",
    "cases": 104,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:cubepay-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:cubepay-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:cubepay-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:cubepay-order-sqlite]"
    ]
  },
  {
    "name": "bypass_extra_nowpayments",
    "disposition": "killed",
    "cases": 104,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:nowpayments-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:nowpayments-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:nowpayments-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:nowpayments-order-sqlite]"
    ]
  },
  {
    "name": "bypass_extra_tgstars",
    "disposition": "killed",
    "cases": 104,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tgstars-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tgstars-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tgstars-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tgstars-order-sqlite]"
    ]
  },
  {
    "name": "reject_legacy",
    "disposition": "killed",
    "cases": 104,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[purchase-legacy-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[purchase-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[crypto-legacy-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[crypto-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[abangateway-legacy-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[abangateway-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[blupal-legacy-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[blupal-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[noapay-legacy-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[noapay-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[custom:synthetic-legacy-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[custom:synthetic-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[card_auto-legacy-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[card_auto-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:zarinpal-legacy-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:zarinpal-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:aqayepardakht-legacy-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:aqayepardakht-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:tetra98-legacy-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:tetra98-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:cubepay-legacy-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:cubepay-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:nowpayments-legacy-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:nowpayments-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:tgstars-legacy-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:tgstars-legacy-sqlite]"
    ]
  },
  {
    "name": "reject_absent",
    "disposition": "killed",
    "cases": 104,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[purchase-None-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[purchase-None-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[crypto-None-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[crypto-None-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[abangateway-None-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[abangateway-None-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[blupal-None-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[blupal-None-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[noapay-None-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[noapay-None-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[custom:synthetic-None-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[custom:synthetic-None-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[card_auto-None-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[card_auto-None-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:zarinpal-None-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:zarinpal-None-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:aqayepardakht-None-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:aqayepardakht-None-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:tetra98-None-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:tetra98-None-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:cubepay-None-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:cubepay-None-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:nowpayments-None-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:nowpayments-None-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:tgstars-None-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:tgstars-None-sqlite]"
    ]
  },
  {
    "name": "no_explicit_reason",
    "disposition": "killed",
    "cases": 104,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[purchase-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[purchase-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[purchase-request-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[purchase-request-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[crypto-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[crypto-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[crypto-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[crypto-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[abangateway-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[abangateway-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[abangateway-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[abangateway-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[blupal-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[blupal-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[blupal-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[blupal-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[noapay-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[noapay-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[noapay-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[noapay-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[custom:synthetic-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[custom:synthetic-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[custom:synthetic-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[custom:synthetic-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[card_auto-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[card_auto-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[card_auto-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[card_auto-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:zarinpal-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:zarinpal-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:zarinpal-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:zarinpal-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:aqayepardakht-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:aqayepardakht-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:aqayepardakht-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:aqayepardakht-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tetra98-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tetra98-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tetra98-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tetra98-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:cubepay-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:cubepay-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:cubepay-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:cubepay-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:nowpayments-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:nowpayments-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:nowpayments-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:nowpayments-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tgstars-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tgstars-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tgstars-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tgstars-order-sqlite]"
    ]
  },
  {
    "name": "leak_product_name",
    "disposition": "killed",
    "cases": 104,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[purchase-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[purchase-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[purchase-request-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[purchase-request-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[crypto-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[crypto-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[crypto-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[crypto-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[abangateway-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[abangateway-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[abangateway-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[abangateway-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[blupal-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[blupal-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[blupal-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[blupal-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[noapay-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[noapay-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[noapay-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[noapay-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[custom:synthetic-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[custom:synthetic-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[custom:synthetic-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[custom:synthetic-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[card_auto-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[card_auto-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[card_auto-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[card_auto-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:zarinpal-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:zarinpal-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:zarinpal-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:zarinpal-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:aqayepardakht-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:aqayepardakht-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:aqayepardakht-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:aqayepardakht-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tetra98-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tetra98-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tetra98-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tetra98-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:cubepay-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:cubepay-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:cubepay-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:cubepay-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:nowpayments-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:nowpayments-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:nowpayments-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:nowpayments-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tgstars-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tgstars-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tgstars-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tgstars-order-sqlite]"
    ]
  },
  {
    "name": "late_after_auth_write",
    "disposition": "killed",
    "cases": 104,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[purchase-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[purchase-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[purchase-request-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[purchase-request-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[crypto-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[crypto-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[crypto-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[crypto-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[abangateway-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[abangateway-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[abangateway-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[abangateway-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[blupal-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[blupal-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[blupal-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[blupal-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[noapay-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[noapay-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[noapay-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[noapay-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[custom:synthetic-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[custom:synthetic-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[custom:synthetic-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[custom:synthetic-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[card_auto-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[card_auto-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[card_auto-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[card_auto-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:zarinpal-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:zarinpal-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:zarinpal-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:zarinpal-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:aqayepardakht-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:aqayepardakht-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:aqayepardakht-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:aqayepardakht-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tetra98-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tetra98-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tetra98-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tetra98-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:cubepay-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:cubepay-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:cubepay-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:cubepay-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:nowpayments-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:nowpayments-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:nowpayments-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:nowpayments-order-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tgstars-product-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tgstars-product-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tgstars-order-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_composite_miniapp_purchase_invoice_refused[extra:tgstars-order-sqlite]"
    ]
  },
  {
    "name": "wrong_amount_api_order_crypto_invoice",
    "disposition": "killed",
    "cases": 104,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[crypto-None-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[crypto-None-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[crypto-legacy-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[crypto-legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_amount_api_order_abangateway_invoice",
    "disposition": "killed",
    "cases": 104,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[abangateway-None-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[abangateway-None-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[abangateway-legacy-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[abangateway-legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_amount_api_order_blupal_invoice",
    "disposition": "killed",
    "cases": 104,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[blupal-None-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[blupal-None-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[blupal-legacy-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[blupal-legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_amount_api_order_noapay_invoice",
    "disposition": "killed",
    "cases": 104,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[noapay-None-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[noapay-None-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[noapay-legacy-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[noapay-legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_amount_api_order_extra_gateway_invoice",
    "disposition": "killed",
    "cases": 104,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:zarinpal-None-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:zarinpal-None-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:zarinpal-legacy-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:zarinpal-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:aqayepardakht-None-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:aqayepardakht-None-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:aqayepardakht-legacy-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:aqayepardakht-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:tetra98-None-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:tetra98-None-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:tetra98-legacy-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:tetra98-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:cubepay-None-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:cubepay-None-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:cubepay-legacy-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:cubepay-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:nowpayments-None-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:nowpayments-None-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:nowpayments-legacy-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:nowpayments-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:tgstars-None-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:tgstars-None-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:tgstars-legacy-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[extra:tgstars-legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_amount_api_order_custom_gateway_invoice",
    "disposition": "killed",
    "cases": 104,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[custom:synthetic-None-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[custom:synthetic-None-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[custom:synthetic-legacy-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[custom:synthetic-legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_amount_api_order_card_auto_invoice",
    "disposition": "killed",
    "cases": 104,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[card_auto-None-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[card_auto-None-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[card_auto-legacy-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[card_auto-legacy-sqlite]"
    ]
  },
  {
    "name": "lost_checkout_wallet_debit",
    "disposition": "killed",
    "cases": 104,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[purchase-None-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[purchase-None-sqlite]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[purchase-legacy-dict]",
      "tests.integration.test_composite_miniapp_purchase_invoice_guards::test_legacy_miniapp_purchase_invoice_preserved[purchase-legacy-sqlite]"
    ]
  }
]
```

Independent mutants against actual signed-auth/route code plus scratch-only early guard. Relevant packet assertions only; no survivors/errors/skips. Existing legacy auth sequence write preserved; rejected composites leave full DB unchanged. Scratch auto-cleaned; no production edits/payment-provider acceptance claim.
