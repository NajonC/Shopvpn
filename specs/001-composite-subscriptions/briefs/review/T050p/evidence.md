# T050p reference and mutation evidence

Source hashes:
```json
{
  "ai_support.py": "1297845ea834eee309443bbc9c9a11ffcea4e982e190d9dbb9c67adfffea5eeb",
  "tests/integration/test_composite_ai_wallet_guards.py": "8e87cdb2a069691992c81c3db74613cf0bfd15ecfc68c11f8c77aceeb93ca281",
  "tests/characterization/test_unsupported_surfaces.py": "4dee58c924d83f592f2c76dd71626addea7774f69f91bb219d3b1c38710e4bfd"
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
    "name": "omit_guard",
    "disposition": "killed",
    "cases": 28,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_wallet_guards::test_composite_ai_wallet_shortcut_refused[stock-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_composite_ai_wallet_shortcut_refused[stock-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_composite_ai_wallet_shortcut_refused[auto-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_composite_ai_wallet_shortcut_refused[auto-sqlite]"
    ]
  },
  {
    "name": "wrong_marker",
    "disposition": "killed",
    "cases": 28,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_wallet_guards::test_composite_ai_wallet_shortcut_refused[stock-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_composite_ai_wallet_shortcut_refused[stock-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_composite_ai_wallet_shortcut_refused[auto-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_composite_ai_wallet_shortcut_refused[auto-sqlite]"
    ]
  },
  {
    "name": "omit_stock",
    "disposition": "killed",
    "cases": 28,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_wallet_guards::test_composite_ai_wallet_shortcut_refused[stock-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_composite_ai_wallet_shortcut_refused[stock-sqlite]"
    ]
  },
  {
    "name": "omit_auto",
    "disposition": "killed",
    "cases": 28,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_wallet_guards::test_composite_ai_wallet_shortcut_refused[auto-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_composite_ai_wallet_shortcut_refused[auto-sqlite]"
    ]
  },
  {
    "name": "reject_missing",
    "disposition": "killed",
    "cases": 28,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-stock-None-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-stock-None-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-auto-None-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-auto-None-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[1-stock-None-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[1-stock-None-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[1-auto-None-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[1-auto-None-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_unrelated_composite_does_not_block_ai_wallet_legacy[auto-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_unrelated_composite_does_not_block_ai_wallet_legacy[auto-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_unrelated_composite_does_not_block_ai_wallet_legacy[empty-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_unrelated_composite_does_not_block_ai_wallet_legacy[empty-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_existing_refusals_preserved[stock-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_existing_refusals_preserved[stock-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_existing_refusals_preserved[wallet-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_existing_refusals_preserved[wallet-sqlite]"
    ]
  },
  {
    "name": "reject_explicit_legacy",
    "disposition": "killed",
    "cases": 28,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-stock-legacy-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-stock-legacy-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-auto-legacy-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-auto-legacy-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[1-stock-legacy-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[1-stock-legacy-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[1-auto-legacy-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[1-auto-legacy-sqlite]"
    ]
  },
  {
    "name": "no_reason",
    "disposition": "killed",
    "cases": 28,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_wallet_guards::test_composite_ai_wallet_shortcut_refused[stock-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_composite_ai_wallet_shortcut_refused[stock-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_composite_ai_wallet_shortcut_refused[auto-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_composite_ai_wallet_shortcut_refused[auto-sqlite]"
    ]
  },
  {
    "name": "leak_name",
    "disposition": "killed",
    "cases": 28,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_wallet_guards::test_composite_ai_wallet_shortcut_refused[stock-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_composite_ai_wallet_shortcut_refused[stock-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_composite_ai_wallet_shortcut_refused[auto-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_composite_ai_wallet_shortcut_refused[auto-sqlite]"
    ]
  },
  {
    "name": "log_name",
    "disposition": "killed",
    "cases": 28,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_wallet_guards::test_composite_ai_wallet_shortcut_refused[stock-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_composite_ai_wallet_shortcut_refused[stock-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_composite_ai_wallet_shortcut_refused[auto-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_composite_ai_wallet_shortcut_refused[auto-sqlite]"
    ]
  },
  {
    "name": "count_before_refusal",
    "disposition": "killed",
    "cases": 28,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_wallet_guards::test_composite_ai_wallet_shortcut_refused[stock-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_composite_ai_wallet_shortcut_refused[stock-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_composite_ai_wallet_shortcut_refused[auto-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_composite_ai_wallet_shortcut_refused[auto-sqlite]"
    ]
  },
  {
    "name": "debit_before_refusal",
    "disposition": "killed",
    "cases": 28,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_wallet_guards::test_composite_ai_wallet_shortcut_refused[stock-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_composite_ai_wallet_shortcut_refused[stock-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_composite_ai_wallet_shortcut_refused[auto-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_composite_ai_wallet_shortcut_refused[auto-sqlite]"
    ]
  },
  {
    "name": "unrelated_overblock",
    "disposition": "killed",
    "cases": 28,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_wallet_guards::test_composite_ai_wallet_shortcut_refused[stock-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_composite_ai_wallet_shortcut_refused[stock-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_composite_ai_wallet_shortcut_refused[auto-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_composite_ai_wallet_shortcut_refused[auto-sqlite]"
    ]
  },
  {
    "name": "wrong_price",
    "disposition": "killed",
    "cases": 28,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-stock-None-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-stock-None-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-stock-legacy-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-stock-legacy-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-auto-None-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-auto-None-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-auto-legacy-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-auto-legacy-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[1-stock-None-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[1-stock-None-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[1-stock-legacy-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[1-stock-legacy-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[1-auto-None-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[1-auto-None-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[1-auto-legacy-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[1-auto-legacy-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_unrelated_composite_does_not_block_ai_wallet_legacy[auto-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_unrelated_composite_does_not_block_ai_wallet_legacy[auto-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_unrelated_composite_does_not_block_ai_wallet_legacy[empty-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_unrelated_composite_does_not_block_ai_wallet_legacy[empty-sqlite]"
    ]
  },
  {
    "name": "ignore_quantity",
    "disposition": "killed",
    "cases": 28,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-stock-None-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-stock-None-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-stock-legacy-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-stock-legacy-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-auto-None-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-auto-None-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-auto-legacy-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-auto-legacy-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[1-stock-None-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[1-stock-None-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[1-stock-legacy-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[1-stock-legacy-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[1-auto-None-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[1-auto-None-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[1-auto-legacy-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[1-auto-legacy-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_unrelated_composite_does_not_block_ai_wallet_legacy[auto-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_unrelated_composite_does_not_block_ai_wallet_legacy[auto-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_unrelated_composite_does_not_block_ai_wallet_legacy[empty-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_unrelated_composite_does_not_block_ai_wallet_legacy[empty-sqlite]"
    ]
  },
  {
    "name": "float_price",
    "disposition": "killed",
    "cases": 28,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-stock-None-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-stock-None-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-stock-legacy-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-stock-legacy-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-auto-None-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-auto-None-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-auto-legacy-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-auto-legacy-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[1-stock-None-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[1-stock-None-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[1-stock-legacy-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[1-stock-legacy-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[1-auto-None-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[1-auto-None-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[1-auto-legacy-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[1-auto-legacy-sqlite]"
    ]
  },
  {
    "name": "wallet_equal_refused",
    "disposition": "killed",
    "cases": 28,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-stock-None-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-stock-None-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-stock-legacy-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-stock-legacy-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-auto-None-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-auto-None-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-auto-legacy-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-auto-legacy-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_unrelated_composite_does_not_block_ai_wallet_legacy[auto-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_unrelated_composite_does_not_block_ai_wallet_legacy[auto-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_unrelated_composite_does_not_block_ai_wallet_legacy[empty-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_unrelated_composite_does_not_block_ai_wallet_legacy[empty-sqlite]"
    ]
  },
  {
    "name": "wallet_one_short_allowed",
    "disposition": "killed",
    "cases": 28,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[1-stock-None-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[1-stock-None-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[1-stock-legacy-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[1-stock-legacy-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[1-auto-None-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[1-auto-None-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[1-auto-legacy-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[1-auto-legacy-sqlite]"
    ]
  },
  {
    "name": "ignore_stock",
    "disposition": "killed",
    "cases": 28,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_existing_refusals_preserved[stock-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_existing_refusals_preserved[stock-sqlite]"
    ]
  },
  {
    "name": "ignore_wallet_permission",
    "disposition": "killed",
    "cases": 28,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_existing_refusals_preserved[wallet-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_existing_refusals_preserved[wallet-sqlite]"
    ]
  },
  {
    "name": "wrong_quantity",
    "disposition": "killed",
    "cases": 28,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-stock-None-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-stock-None-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-stock-legacy-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-stock-legacy-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-auto-None-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-auto-None-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-auto-legacy-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-auto-legacy-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_unrelated_composite_does_not_block_ai_wallet_legacy[auto-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_unrelated_composite_does_not_block_ai_wallet_legacy[auto-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_unrelated_composite_does_not_block_ai_wallet_legacy[empty-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_unrelated_composite_does_not_block_ai_wallet_legacy[empty-sqlite]"
    ]
  },
  {
    "name": "wrong_product",
    "disposition": "killed",
    "cases": 28,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-stock-None-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-stock-None-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-stock-legacy-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-stock-legacy-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-auto-None-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-auto-None-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-auto-legacy-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-auto-legacy-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_unrelated_composite_does_not_block_ai_wallet_legacy[auto-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_unrelated_composite_does_not_block_ai_wallet_legacy[auto-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_unrelated_composite_does_not_block_ai_wallet_legacy[empty-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_unrelated_composite_does_not_block_ai_wallet_legacy[empty-sqlite]"
    ]
  },
  {
    "name": "debit_on_preview",
    "disposition": "killed",
    "cases": 28,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-stock-None-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-stock-None-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-stock-legacy-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-stock-legacy-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-auto-None-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-auto-None-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-auto-legacy-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_legacy_ai_wallet_price_boundary_preserved[0-auto-legacy-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_unrelated_composite_does_not_block_ai_wallet_legacy[auto-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_unrelated_composite_does_not_block_ai_wallet_legacy[auto-sqlite]",
      "tests.integration.test_composite_ai_wallet_guards::test_unrelated_composite_does_not_block_ai_wallet_legacy[empty-dict]",
      "tests.integration.test_composite_ai_wallet_guards::test_unrelated_composite_does_not_block_ai_wallet_legacy[empty-sqlite]"
    ]
  }
]
```

Independent valid mutations, relevant assertion failures only. No survivors/errors/skips. Scratch auto-cleaned. Reference preflights selected product metadata before the unchanged real wallet-purchase shortcut; real reads/prices/permissions/stock remain active. No production implementation claim.
