# T050an reference and mutation evidence

Source hashes:
```json
{
  "handlers_user.py": "611ce8a3ddab0d2298f0777187c6bf688958eaa2cce22fbabc2b3bf352182c90",
  "tests/integration/test_composite_telegram_custom_receipt_guards.py": "3dd32088c6988c476b489a3bb8b9feb9a5696f2bc1487da54fdea1ead1f7d66a",
  "tests/characterization/test_receipt_linkage.py": "5282debcc60522ccd5ad4ea793a13ce2c9d481bb8dd79e088592f0e636feda42"
}
```

Results:
```json
[
  {
    "name": "reference",
    "disposition": "passed",
    "cases": 47,
    "failed_test_ids": []
  },
  {
    "name": "omit_guard",
    "disposition": "killed",
    "cases": 30,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-order-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-order-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-product-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-product-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-order-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-order-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-product-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-product-sqlite]"
    ]
  },
  {
    "name": "omit_order_guard",
    "disposition": "killed",
    "cases": 30,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-order-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-order-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-order-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-order-sqlite]"
    ]
  },
  {
    "name": "omit_product_guard",
    "disposition": "killed",
    "cases": 30,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-product-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-product-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-product-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-product-sqlite]"
    ]
  },
  {
    "name": "require_both_markers",
    "disposition": "killed",
    "cases": 30,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-order-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-order-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-product-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-product-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-order-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-order-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-product-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-product-sqlite]"
    ]
  },
  {
    "name": "wrong_order_kind",
    "disposition": "killed",
    "cases": 30,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-order-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-order-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-order-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-order-sqlite]"
    ]
  },
  {
    "name": "wrong_product_kind",
    "disposition": "killed",
    "cases": 30,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-product-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-product-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-product-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-product-sqlite]"
    ]
  },
  {
    "name": "reject_missing_marker",
    "disposition": "killed",
    "cases": 30,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[None-photo-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[None-photo-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[None-document-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[None-document-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[None-both-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[None-both-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_sibling_allows_custom_receipt[dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_sibling_allows_custom_receipt[sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_blocked_admin_custom_receipt[dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_blocked_admin_custom_receipt[sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_refusals[approved-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_refusals[approved-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_refusals[no_file-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_refusals[no_file-sqlite]"
    ]
  },
  {
    "name": "reject_legacy_marker",
    "disposition": "killed",
    "cases": 30,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[legacy-photo-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[legacy-photo-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[legacy-document-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[legacy-document-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[legacy-both-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[legacy-both-sqlite]"
    ]
  },
  {
    "name": "no_reason",
    "disposition": "killed",
    "cases": 30,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-order-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-order-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-product-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-product-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-order-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-order-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-product-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-product-sqlite]"
    ]
  },
  {
    "name": "leak_name",
    "disposition": "killed",
    "cases": 30,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-order-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-order-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-product-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-product-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-order-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-order-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-product-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-product-sqlite]"
    ]
  },
  {
    "name": "state_before_refusal",
    "disposition": "killed",
    "cases": 30,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-order-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-order-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-product-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-product-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-order-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-order-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-product-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-product-sqlite]"
    ]
  },
  {
    "name": "data_before_refusal",
    "disposition": "killed",
    "cases": 30,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-order-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-order-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-product-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-product-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-order-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-order-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-product-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-product-sqlite]"
    ]
  },
  {
    "name": "clear_before_refusal",
    "disposition": "killed",
    "cases": 30,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-order-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-order-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-product-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-product-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-order-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-order-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-product-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-product-sqlite]"
    ]
  },
  {
    "name": "prompt_before_refusal",
    "disposition": "killed",
    "cases": 30,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-order-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-order-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-product-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-product-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-order-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-order-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-product-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-product-sqlite]"
    ]
  },
  {
    "name": "db_before_refusal",
    "disposition": "killed",
    "cases": 30,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-order-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-order-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-product-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-product-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-order-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-order-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-product-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-product-sqlite]"
    ]
  },
  {
    "name": "details_before_refusal",
    "disposition": "killed",
    "cases": 30,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-order-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-order-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-product-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-product-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-order-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-order-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-product-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-product-sqlite]"
    ]
  },
  {
    "name": "approved_allowed",
    "disposition": "killed",
    "cases": 30,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_refusals[approved-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_refusals[approved-sqlite]"
    ]
  },
  {
    "name": "omit_receipt_save",
    "disposition": "killed",
    "cases": 30,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[None-photo-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[None-photo-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[None-document-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[None-document-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[None-both-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[None-both-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[legacy-photo-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[legacy-photo-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[legacy-document-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[legacy-document-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[legacy-both-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[legacy-both-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_sibling_allows_custom_receipt[dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_sibling_allows_custom_receipt[sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_blocked_admin_custom_receipt[dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_blocked_admin_custom_receipt[sqlite]"
    ]
  },
  {
    "name": "wrong_receipt_type",
    "disposition": "killed",
    "cases": 30,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[None-photo-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[None-photo-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[None-document-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[None-document-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[None-both-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[None-both-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[legacy-photo-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[legacy-photo-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[legacy-document-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[legacy-document-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[legacy-both-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[legacy-both-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_sibling_allows_custom_receipt[dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_sibling_allows_custom_receipt[sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_blocked_admin_custom_receipt[dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_blocked_admin_custom_receipt[sqlite]"
    ]
  },
  {
    "name": "wrong_notify_file",
    "disposition": "killed",
    "cases": 30,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[None-photo-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[None-photo-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[None-document-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[None-document-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[None-both-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[None-both-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[legacy-photo-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[legacy-photo-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[legacy-document-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[legacy-document-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[legacy-both-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[legacy-both-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_sibling_allows_custom_receipt[dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_sibling_allows_custom_receipt[sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_blocked_admin_custom_receipt[dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_blocked_admin_custom_receipt[sqlite]"
    ]
  },
  {
    "name": "retain_success_fsm",
    "disposition": "killed",
    "cases": 30,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[None-photo-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[None-photo-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[None-document-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[None-document-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[None-both-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[None-both-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[legacy-photo-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[legacy-photo-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[legacy-document-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[legacy-document-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[legacy-both-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[legacy-both-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_sibling_allows_custom_receipt[dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_sibling_allows_custom_receipt[sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_blocked_admin_custom_receipt[dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_blocked_admin_custom_receipt[sqlite]"
    ]
  },
  {
    "name": "wrong_success",
    "disposition": "killed",
    "cases": 30,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[None-photo-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[None-photo-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[None-document-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[None-document-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[None-both-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[None-both-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[legacy-photo-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[legacy-photo-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[legacy-document-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[legacy-document-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[legacy-both-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[legacy-both-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_sibling_allows_custom_receipt[dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_sibling_allows_custom_receipt[sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_blocked_admin_custom_receipt[dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_blocked_admin_custom_receipt[sqlite]"
    ]
  },
  {
    "name": "omit_menu",
    "disposition": "killed",
    "cases": 30,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[None-photo-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[None-photo-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[None-document-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[None-document-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[None-both-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[None-both-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[legacy-photo-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[legacy-photo-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[legacy-document-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[legacy-document-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[legacy-both-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[legacy-both-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_sibling_allows_custom_receipt[dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_sibling_allows_custom_receipt[sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_blocked_admin_custom_receipt[dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_blocked_admin_custom_receipt[sqlite]"
    ]
  },
  {
    "name": "receipt_before_refusal",
    "disposition": "killed",
    "cases": 30,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-order-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-order-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-product-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-product-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-order-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-order-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-product-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-product-sqlite]"
    ]
  },
  {
    "name": "admin_before_refusal",
    "disposition": "killed",
    "cases": 30,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-order-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-order-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-product-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[photo-product-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-order-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-order-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-product-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_custom_receipt_refused[document-product-sqlite]"
    ]
  },
  {
    "name": "wrong_photo_size",
    "disposition": "killed",
    "cases": 30,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[None-photo-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[None-photo-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[None-both-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[None-both-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[legacy-photo-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[legacy-photo-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[legacy-both-dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_legacy_custom_receipt_exact[legacy-both-sqlite]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_sibling_allows_custom_receipt[dict]",
      "tests.integration.test_composite_telegram_custom_receipt_guards::test_composite_sibling_allows_custom_receipt[sqlite]"
    ]
  }
]
```

Independent valid mutations, relevant assertion failures only. No survivors/errors/skips. Scratch auto-cleaned. Reference checks selected owned service before custom noapay invoice selected-order/product and card-details publication effects; real SQL and legacy controls preserved. No production implementation claim.
