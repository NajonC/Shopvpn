# T050d reference and mutation evidence

Hashes:
```json
{
  "handlers_admin.py": "73d8781de295b74025735702b21df2548f28e54f83c89e8e0d87210068b63648",
  "admin_panel/server.py": "ee9c2dc47c30d7c4a502e6a6f4b57ecfe93343f1468a7e601703da8c1bef7511",
  "tests/integration/test_composite_order_review_guards.py": "ef490f4ccc5ce65b212aa6a8ad43894017f8210900ca21ed99001b68d37dfc55",
  "tests/characterization/test_order_approval.py": "ddb22753d2afafdb991db3e1f21106719485313645983e1da982afac4f7a1f13",
  "tests/characterization/test_wallet_helpers.py": "ace7e6f4a8f906faa4ae98dd05c5faf7fd96d2668414da651c3f5500bd850622"
}
```

Results:
```json
[
  {
    "mutation": "reference",
    "disposition": "pass",
    "cases": 124,
    "failed_test_ids": []
  },
  {
    "mutation": "telegram_approve_omit",
    "disposition": "killed",
    "cases": 16,
    "failed_test_ids": [
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-dict-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-dict-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-dict-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-dict-renewal-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-dict-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-dict-direct-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-sqlite-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-sqlite-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-sqlite-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-sqlite-renewal-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-sqlite-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-sqlite-direct-product]"
    ]
  },
  {
    "mutation": "telegram_approve_omit_order",
    "disposition": "killed",
    "cases": 16,
    "failed_test_ids": [
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-dict-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-dict-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-dict-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-dict-renewal-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-sqlite-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-sqlite-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-sqlite-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-sqlite-renewal-order]"
    ]
  },
  {
    "mutation": "telegram_approve_omit_product",
    "disposition": "killed",
    "cases": 16,
    "failed_test_ids": [
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-dict-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-dict-direct-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-sqlite-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-sqlite-direct-product]"
    ]
  },
  {
    "mutation": "telegram_approve_wrong_kind",
    "disposition": "killed",
    "cases": 16,
    "failed_test_ids": [
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-dict-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-dict-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-dict-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-dict-renewal-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-dict-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-dict-direct-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-sqlite-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-sqlite-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-sqlite-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-sqlite-renewal-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-sqlite-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-sqlite-direct-product]"
    ]
  },
  {
    "mutation": "telegram_approve_reject_legacy",
    "disposition": "killed",
    "cases": 16,
    "failed_test_ids": [
      "tests.integration.test_composite_order_review_guards::test_legacy_order_review_still_settles[approve-telegram-dict-legacy]",
      "tests.integration.test_composite_order_review_guards::test_legacy_order_review_still_settles[approve-telegram-sqlite-legacy]"
    ]
  },
  {
    "mutation": "telegram_approve_reject_absent",
    "disposition": "killed",
    "cases": 16,
    "failed_test_ids": [
      "tests.integration.test_composite_order_review_guards::test_legacy_order_review_still_settles[approve-telegram-dict-None]",
      "tests.integration.test_composite_order_review_guards::test_legacy_order_review_still_settles[approve-telegram-sqlite-None]"
    ]
  },
  {
    "mutation": "telegram_approve_no_reason",
    "disposition": "killed",
    "cases": 16,
    "failed_test_ids": [
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-dict-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-dict-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-dict-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-dict-renewal-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-dict-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-dict-direct-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-sqlite-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-sqlite-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-sqlite-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-sqlite-renewal-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-sqlite-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-sqlite-direct-product]"
    ]
  },
  {
    "mutation": "telegram_approve_leak_receipt",
    "disposition": "killed",
    "cases": 16,
    "failed_test_ids": [
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-dict-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-dict-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-dict-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-dict-renewal-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-dict-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-dict-direct-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-sqlite-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-sqlite-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-sqlite-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-sqlite-renewal-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-sqlite-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-sqlite-direct-product]"
    ]
  },
  {
    "mutation": "telegram_approve_late_effect",
    "disposition": "killed",
    "cases": 16,
    "failed_test_ids": [
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-dict-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-dict-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-dict-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-dict-renewal-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-dict-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-dict-direct-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-sqlite-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-sqlite-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-sqlite-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-sqlite-renewal-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-sqlite-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-telegram-sqlite-direct-product]"
    ]
  },
  {
    "mutation": "telegram_reject_omit",
    "disposition": "killed",
    "cases": 16,
    "failed_test_ids": [
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-dict-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-dict-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-dict-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-dict-renewal-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-dict-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-dict-direct-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-sqlite-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-sqlite-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-sqlite-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-sqlite-renewal-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-sqlite-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-sqlite-direct-product]"
    ]
  },
  {
    "mutation": "telegram_reject_omit_order",
    "disposition": "killed",
    "cases": 16,
    "failed_test_ids": [
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-dict-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-dict-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-dict-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-dict-renewal-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-sqlite-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-sqlite-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-sqlite-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-sqlite-renewal-order]"
    ]
  },
  {
    "mutation": "telegram_reject_omit_product",
    "disposition": "killed",
    "cases": 16,
    "failed_test_ids": [
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-dict-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-dict-direct-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-sqlite-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-sqlite-direct-product]"
    ]
  },
  {
    "mutation": "telegram_reject_wrong_kind",
    "disposition": "killed",
    "cases": 16,
    "failed_test_ids": [
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-dict-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-dict-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-dict-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-dict-renewal-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-dict-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-dict-direct-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-sqlite-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-sqlite-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-sqlite-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-sqlite-renewal-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-sqlite-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-sqlite-direct-product]"
    ]
  },
  {
    "mutation": "telegram_reject_reject_legacy",
    "disposition": "killed",
    "cases": 16,
    "failed_test_ids": [
      "tests.integration.test_composite_order_review_guards::test_legacy_order_review_still_settles[reject-telegram-dict-legacy]",
      "tests.integration.test_composite_order_review_guards::test_legacy_order_review_still_settles[reject-telegram-sqlite-legacy]"
    ]
  },
  {
    "mutation": "telegram_reject_reject_absent",
    "disposition": "killed",
    "cases": 16,
    "failed_test_ids": [
      "tests.integration.test_composite_order_review_guards::test_legacy_order_review_still_settles[reject-telegram-dict-None]",
      "tests.integration.test_composite_order_review_guards::test_legacy_order_review_still_settles[reject-telegram-sqlite-None]"
    ]
  },
  {
    "mutation": "telegram_reject_no_reason",
    "disposition": "killed",
    "cases": 16,
    "failed_test_ids": [
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-dict-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-dict-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-dict-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-dict-renewal-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-dict-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-dict-direct-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-sqlite-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-sqlite-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-sqlite-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-sqlite-renewal-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-sqlite-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-sqlite-direct-product]"
    ]
  },
  {
    "mutation": "telegram_reject_leak_receipt",
    "disposition": "killed",
    "cases": 16,
    "failed_test_ids": [
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-dict-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-dict-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-dict-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-dict-renewal-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-dict-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-dict-direct-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-sqlite-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-sqlite-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-sqlite-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-sqlite-renewal-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-sqlite-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-sqlite-direct-product]"
    ]
  },
  {
    "mutation": "telegram_reject_late_effect",
    "disposition": "killed",
    "cases": 16,
    "failed_test_ids": [
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-dict-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-dict-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-dict-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-dict-renewal-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-dict-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-dict-direct-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-sqlite-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-sqlite-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-sqlite-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-sqlite-renewal-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-sqlite-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-telegram-sqlite-direct-product]"
    ]
  },
  {
    "mutation": "web_approve_omit",
    "disposition": "killed",
    "cases": 16,
    "failed_test_ids": [
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-dict-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-dict-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-dict-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-dict-renewal-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-dict-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-dict-direct-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-sqlite-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-sqlite-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-sqlite-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-sqlite-renewal-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-sqlite-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-sqlite-direct-product]"
    ]
  },
  {
    "mutation": "web_approve_omit_order",
    "disposition": "killed",
    "cases": 16,
    "failed_test_ids": [
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-dict-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-dict-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-dict-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-dict-renewal-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-sqlite-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-sqlite-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-sqlite-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-sqlite-renewal-order]"
    ]
  },
  {
    "mutation": "web_approve_omit_product",
    "disposition": "killed",
    "cases": 16,
    "failed_test_ids": [
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-dict-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-dict-direct-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-sqlite-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-sqlite-direct-product]"
    ]
  },
  {
    "mutation": "web_approve_wrong_kind",
    "disposition": "killed",
    "cases": 16,
    "failed_test_ids": [
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-dict-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-dict-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-dict-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-dict-renewal-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-dict-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-dict-direct-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-sqlite-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-sqlite-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-sqlite-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-sqlite-renewal-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-sqlite-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-sqlite-direct-product]"
    ]
  },
  {
    "mutation": "web_approve_reject_legacy",
    "disposition": "killed",
    "cases": 16,
    "failed_test_ids": [
      "tests.integration.test_composite_order_review_guards::test_legacy_order_review_still_settles[approve-web-dict-legacy]",
      "tests.integration.test_composite_order_review_guards::test_legacy_order_review_still_settles[approve-web-sqlite-legacy]"
    ]
  },
  {
    "mutation": "web_approve_reject_absent",
    "disposition": "killed",
    "cases": 16,
    "failed_test_ids": [
      "tests.integration.test_composite_order_review_guards::test_legacy_order_review_still_settles[approve-web-dict-None]",
      "tests.integration.test_composite_order_review_guards::test_legacy_order_review_still_settles[approve-web-sqlite-None]"
    ]
  },
  {
    "mutation": "web_approve_no_reason",
    "disposition": "killed",
    "cases": 16,
    "failed_test_ids": [
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-dict-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-dict-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-dict-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-dict-renewal-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-dict-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-dict-direct-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-sqlite-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-sqlite-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-sqlite-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-sqlite-renewal-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-sqlite-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-sqlite-direct-product]"
    ]
  },
  {
    "mutation": "web_approve_leak_receipt",
    "disposition": "killed",
    "cases": 16,
    "failed_test_ids": [
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-dict-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-dict-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-dict-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-dict-renewal-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-dict-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-dict-direct-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-sqlite-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-sqlite-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-sqlite-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-sqlite-renewal-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-sqlite-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-sqlite-direct-product]"
    ]
  },
  {
    "mutation": "web_approve_late_effect",
    "disposition": "killed",
    "cases": 16,
    "failed_test_ids": [
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-dict-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-dict-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-dict-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-dict-renewal-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-dict-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-dict-direct-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-sqlite-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-sqlite-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-sqlite-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-sqlite-renewal-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-sqlite-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[approve-web-sqlite-direct-product]"
    ]
  },
  {
    "mutation": "web_reject_omit",
    "disposition": "killed",
    "cases": 16,
    "failed_test_ids": [
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-dict-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-dict-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-dict-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-dict-renewal-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-dict-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-dict-direct-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-sqlite-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-sqlite-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-sqlite-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-sqlite-renewal-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-sqlite-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-sqlite-direct-product]"
    ]
  },
  {
    "mutation": "web_reject_omit_order",
    "disposition": "killed",
    "cases": 16,
    "failed_test_ids": [
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-dict-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-dict-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-dict-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-dict-renewal-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-sqlite-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-sqlite-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-sqlite-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-sqlite-renewal-order]"
    ]
  },
  {
    "mutation": "web_reject_omit_product",
    "disposition": "killed",
    "cases": 16,
    "failed_test_ids": [
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-dict-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-dict-direct-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-sqlite-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-sqlite-direct-product]"
    ]
  },
  {
    "mutation": "web_reject_wrong_kind",
    "disposition": "killed",
    "cases": 16,
    "failed_test_ids": [
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-dict-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-dict-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-dict-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-dict-renewal-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-dict-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-dict-direct-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-sqlite-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-sqlite-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-sqlite-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-sqlite-renewal-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-sqlite-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-sqlite-direct-product]"
    ]
  },
  {
    "mutation": "web_reject_reject_legacy",
    "disposition": "killed",
    "cases": 16,
    "failed_test_ids": [
      "tests.integration.test_composite_order_review_guards::test_legacy_order_review_still_settles[reject-web-dict-legacy]",
      "tests.integration.test_composite_order_review_guards::test_legacy_order_review_still_settles[reject-web-sqlite-legacy]"
    ]
  },
  {
    "mutation": "web_reject_reject_absent",
    "disposition": "killed",
    "cases": 16,
    "failed_test_ids": [
      "tests.integration.test_composite_order_review_guards::test_legacy_order_review_still_settles[reject-web-dict-None]",
      "tests.integration.test_composite_order_review_guards::test_legacy_order_review_still_settles[reject-web-sqlite-None]"
    ]
  },
  {
    "mutation": "web_reject_no_reason",
    "disposition": "killed",
    "cases": 16,
    "failed_test_ids": [
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-dict-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-dict-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-dict-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-dict-renewal-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-dict-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-dict-direct-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-sqlite-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-sqlite-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-sqlite-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-sqlite-renewal-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-sqlite-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-sqlite-direct-product]"
    ]
  },
  {
    "mutation": "web_reject_leak_receipt",
    "disposition": "killed",
    "cases": 16,
    "failed_test_ids": [
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-dict-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-dict-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-dict-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-dict-renewal-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-dict-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-dict-direct-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-sqlite-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-sqlite-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-sqlite-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-sqlite-renewal-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-sqlite-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-sqlite-direct-product]"
    ]
  },
  {
    "mutation": "web_reject_late_effect",
    "disposition": "killed",
    "cases": 16,
    "failed_test_ids": [
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-dict-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-dict-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-dict-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-dict-renewal-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-dict-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-dict-direct-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-sqlite-stock-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-sqlite-direct-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-sqlite-custom-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-sqlite-renewal-order]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-sqlite-stock-product]",
      "tests.integration.test_composite_order_review_guards::test_composite_order_review_refused_before_effects[reject-web-sqlite-direct-product]"
    ]
  }
]
```

All mutations independent against actual handlers plus scratch-only guards; packet assertions only, no survivors/errors/skips. Synthetic auth and services; scratch auto-cleaned. No production edits.
