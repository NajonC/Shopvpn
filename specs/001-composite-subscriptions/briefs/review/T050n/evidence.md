# T050n reference and mutation evidence

Source hashes:
```json
{
  "ai_support.py": "1297845ea834eee309443bbc9c9a11ffcea4e982e190d9dbb9c67adfffea5eeb",
  "tests/integration/test_composite_ai_catalog_guards.py": "2b3d44a725d53dd2fd29e69b02401460de3c55285f97f3f93473100330677a6d",
  "tests/integration/test_composite_ai_catalog_legacy.py": "6dc1987657d7a54d51948af2f556d70ef500e95a2ab30b3eae55d93c3167b207",
  "tests/characterization/test_legacy_renewal_reminders.py": "84722b6b10d9fbdae768cb5fb8e8fbc3490b3a213575196210a56401c6e61ea3"
}
```

Results:
```json
[
  {
    "name": "reference",
    "disposition": "passed",
    "cases": 59,
    "failed_test_ids": []
  },
  {
    "name": "omit_both_gates",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-stock-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-stock-sqlite]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-auto-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-auto-sqlite]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-empty-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-empty-sqlite]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-stock-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-stock-sqlite]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-auto-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-auto-sqlite]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-empty-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-empty-sqlite]"
    ]
  },
  {
    "name": "omit_catalog",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-stock-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-stock-sqlite]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-auto-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-auto-sqlite]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-empty-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-empty-sqlite]"
    ]
  },
  {
    "name": "omit_options",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-stock-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-stock-sqlite]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-auto-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-auto-sqlite]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-empty-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-empty-sqlite]"
    ]
  },
  {
    "name": "wrong_marker",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-stock-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-stock-sqlite]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-auto-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-auto-sqlite]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-empty-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-empty-sqlite]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-stock-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-stock-sqlite]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-auto-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-auto-sqlite]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-empty-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-empty-sqlite]"
    ]
  },
  {
    "name": "reject_missing",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_catalog_guards::test_selected_legacy_ai_option_with_unrelated_composite[dict-auto]",
      "tests.integration.test_composite_ai_catalog_guards::test_selected_legacy_ai_option_with_unrelated_composite[dict-empty]",
      "tests.integration.test_composite_ai_catalog_guards::test_selected_legacy_ai_option_with_unrelated_composite[sqlite-auto]",
      "tests.integration.test_composite_ai_catalog_guards::test_selected_legacy_ai_option_with_unrelated_composite[sqlite-empty]",
      "tests.integration.test_composite_ai_catalog_legacy::test_legacy_ai_catalog_exact[None-dict]",
      "tests.integration.test_composite_ai_catalog_legacy::test_legacy_ai_catalog_exact[None-sqlite]",
      "tests.integration.test_composite_ai_catalog_legacy::test_legacy_ai_catalog_exact[legacy-dict]",
      "tests.integration.test_composite_ai_catalog_legacy::test_legacy_ai_catalog_exact[legacy-sqlite]"
    ]
  },
  {
    "name": "reject_explicit_legacy",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_catalog_legacy::test_legacy_ai_catalog_exact[legacy-dict]",
      "tests.integration.test_composite_ai_catalog_legacy::test_legacy_ai_catalog_exact[legacy-sqlite]"
    ]
  },
  {
    "name": "no_reason",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-stock-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-stock-sqlite]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-auto-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-auto-sqlite]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-empty-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-empty-sqlite]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-stock-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-stock-sqlite]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-auto-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-auto-sqlite]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-empty-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-empty-sqlite]"
    ]
  },
  {
    "name": "leak_name",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-stock-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-stock-sqlite]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-auto-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-auto-sqlite]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-empty-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-empty-sqlite]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-stock-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-stock-sqlite]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-auto-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-auto-sqlite]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-empty-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-empty-sqlite]"
    ]
  },
  {
    "name": "log_name",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-stock-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-stock-sqlite]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-auto-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-auto-sqlite]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-empty-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-empty-sqlite]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-stock-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-stock-sqlite]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-auto-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-auto-sqlite]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-empty-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-empty-sqlite]"
    ]
  },
  {
    "name": "count_before_refusal",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-stock-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-stock-sqlite]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-auto-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-auto-sqlite]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-empty-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-empty-sqlite]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-stock-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-stock-sqlite]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-auto-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-auto-sqlite]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-empty-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-empty-sqlite]"
    ]
  },
  {
    "name": "write_before_refusal",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-stock-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-stock-sqlite]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-auto-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-auto-sqlite]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-empty-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-empty-sqlite]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-stock-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-stock-sqlite]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-auto-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-auto-sqlite]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-empty-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-empty-sqlite]"
    ]
  },
  {
    "name": "omit_stock",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-stock-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-stock-sqlite]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-stock-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-stock-sqlite]"
    ]
  },
  {
    "name": "omit_auto",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-auto-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-auto-sqlite]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-auto-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-auto-sqlite]"
    ]
  },
  {
    "name": "omit_empty",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-empty-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-empty-sqlite]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-empty-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[show_purchase_options-empty-sqlite]"
    ]
  },
  {
    "name": "options_scan_unrelated",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_catalog_guards::test_selected_legacy_ai_option_with_unrelated_composite[dict-auto]",
      "tests.integration.test_composite_ai_catalog_guards::test_selected_legacy_ai_option_with_unrelated_composite[dict-empty]",
      "tests.integration.test_composite_ai_catalog_guards::test_selected_legacy_ai_option_with_unrelated_composite[sqlite-auto]",
      "tests.integration.test_composite_ai_catalog_guards::test_selected_legacy_ai_option_with_unrelated_composite[sqlite-empty]"
    ]
  },
  {
    "name": "late_catalog_preflight",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-stock-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-stock-sqlite]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-auto-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-auto-sqlite]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-empty-dict]",
      "tests.integration.test_composite_ai_catalog_guards::test_composite_ai_catalog_refused[list_products-empty-sqlite]",
      "tests.integration.test_composite_ai_catalog_legacy::test_legacy_ai_catalog_exact[None-dict]",
      "tests.integration.test_composite_ai_catalog_legacy::test_legacy_ai_catalog_exact[None-sqlite]",
      "tests.integration.test_composite_ai_catalog_legacy::test_legacy_ai_catalog_exact[legacy-dict]",
      "tests.integration.test_composite_ai_catalog_legacy::test_legacy_ai_catalog_exact[legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_price",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_catalog_legacy::test_legacy_ai_catalog_exact[None-dict]",
      "tests.integration.test_composite_ai_catalog_legacy::test_legacy_ai_catalog_exact[None-sqlite]",
      "tests.integration.test_composite_ai_catalog_legacy::test_legacy_ai_catalog_exact[legacy-dict]",
      "tests.integration.test_composite_ai_catalog_legacy::test_legacy_ai_catalog_exact[legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_duration",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_catalog_legacy::test_legacy_ai_catalog_exact[None-dict]",
      "tests.integration.test_composite_ai_catalog_legacy::test_legacy_ai_catalog_exact[None-sqlite]",
      "tests.integration.test_composite_ai_catalog_legacy::test_legacy_ai_catalog_exact[legacy-dict]",
      "tests.integration.test_composite_ai_catalog_legacy::test_legacy_ai_catalog_exact[legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_description",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_catalog_legacy::test_legacy_ai_catalog_exact[None-dict]",
      "tests.integration.test_composite_ai_catalog_legacy::test_legacy_ai_catalog_exact[None-sqlite]",
      "tests.integration.test_composite_ai_catalog_legacy::test_legacy_ai_catalog_exact[legacy-dict]",
      "tests.integration.test_composite_ai_catalog_legacy::test_legacy_ai_catalog_exact[legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_stock_count",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_catalog_legacy::test_legacy_ai_catalog_exact[None-dict]",
      "tests.integration.test_composite_ai_catalog_legacy::test_legacy_ai_catalog_exact[None-sqlite]",
      "tests.integration.test_composite_ai_catalog_legacy::test_legacy_ai_catalog_exact[legacy-dict]",
      "tests.integration.test_composite_ai_catalog_legacy::test_legacy_ai_catalog_exact[legacy-sqlite]"
    ]
  },
  {
    "name": "empty_marked_available",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_catalog_legacy::test_legacy_ai_catalog_exact[None-dict]",
      "tests.integration.test_composite_ai_catalog_legacy::test_legacy_ai_catalog_exact[None-sqlite]",
      "tests.integration.test_composite_ai_catalog_legacy::test_legacy_ai_catalog_exact[legacy-dict]",
      "tests.integration.test_composite_ai_catalog_legacy::test_legacy_ai_catalog_exact[legacy-sqlite]"
    ]
  },
  {
    "name": "automatic_marked_unavailable",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_catalog_legacy::test_legacy_ai_catalog_exact[None-dict]",
      "tests.integration.test_composite_ai_catalog_legacy::test_legacy_ai_catalog_exact[None-sqlite]",
      "tests.integration.test_composite_ai_catalog_legacy::test_legacy_ai_catalog_exact[legacy-dict]",
      "tests.integration.test_composite_ai_catalog_legacy::test_legacy_ai_catalog_exact[legacy-sqlite]"
    ]
  },
  {
    "name": "lost_product",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_catalog_legacy::test_legacy_ai_catalog_exact[None-dict]",
      "tests.integration.test_composite_ai_catalog_legacy::test_legacy_ai_catalog_exact[None-sqlite]",
      "tests.integration.test_composite_ai_catalog_legacy::test_legacy_ai_catalog_exact[legacy-dict]",
      "tests.integration.test_composite_ai_catalog_legacy::test_legacy_ai_catalog_exact[legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_option_id",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_catalog_guards::test_selected_legacy_ai_option_with_unrelated_composite[dict-auto]",
      "tests.integration.test_composite_ai_catalog_guards::test_selected_legacy_ai_option_with_unrelated_composite[dict-empty]",
      "tests.integration.test_composite_ai_catalog_guards::test_selected_legacy_ai_option_with_unrelated_composite[sqlite-auto]",
      "tests.integration.test_composite_ai_catalog_guards::test_selected_legacy_ai_option_with_unrelated_composite[sqlite-empty]",
      "tests.integration.test_composite_ai_catalog_legacy::test_legacy_ai_catalog_exact[None-dict]",
      "tests.integration.test_composite_ai_catalog_legacy::test_legacy_ai_catalog_exact[None-sqlite]",
      "tests.integration.test_composite_ai_catalog_legacy::test_legacy_ai_catalog_exact[legacy-dict]",
      "tests.integration.test_composite_ai_catalog_legacy::test_legacy_ai_catalog_exact[legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_option_name",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_catalog_guards::test_selected_legacy_ai_option_with_unrelated_composite[dict-auto]",
      "tests.integration.test_composite_ai_catalog_guards::test_selected_legacy_ai_option_with_unrelated_composite[dict-empty]",
      "tests.integration.test_composite_ai_catalog_guards::test_selected_legacy_ai_option_with_unrelated_composite[sqlite-auto]",
      "tests.integration.test_composite_ai_catalog_guards::test_selected_legacy_ai_option_with_unrelated_composite[sqlite-empty]",
      "tests.integration.test_composite_ai_catalog_legacy::test_legacy_ai_catalog_exact[None-dict]",
      "tests.integration.test_composite_ai_catalog_legacy::test_legacy_ai_catalog_exact[None-sqlite]",
      "tests.integration.test_composite_ai_catalog_legacy::test_legacy_ai_catalog_exact[legacy-dict]",
      "tests.integration.test_composite_ai_catalog_legacy::test_legacy_ai_catalog_exact[legacy-sqlite]"
    ]
  }
]
```

Independent valid mutations, relevant assertion failures only. No survivors/errors/skips. Scratch auto-cleaned. Reference preflights real catalog rows through real getters before the unchanged real dispatcher/catalog output; no production implementation claim.
