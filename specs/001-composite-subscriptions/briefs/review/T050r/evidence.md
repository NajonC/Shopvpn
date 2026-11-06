# T050r reference and mutation evidence

Source hashes:
```json
{
  "ai_support.py": "1297845ea834eee309443bbc9c9a11ffcea4e982e190d9dbb9c67adfffea5eeb",
  "tests/integration/test_composite_ai_country_guards.py": "901dfbf4a934ea15c4df3ad39be1c28b884e617eb1eff42f3caf8a177852b8bb",
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
    "cases": 61,
    "failed_test_ids": []
  },
  {
    "name": "omit_guard",
    "disposition": "killed",
    "cases": 18,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_country_guards::test_composite_ai_country_discovery_refused[alpha-dict]",
      "tests.integration.test_composite_ai_country_guards::test_composite_ai_country_discovery_refused[alpha-sqlite]",
      "tests.integration.test_composite_ai_country_guards::test_composite_ai_country_discovery_refused[gamma-dict]",
      "tests.integration.test_composite_ai_country_guards::test_composite_ai_country_discovery_refused[gamma-sqlite]"
    ]
  },
  {
    "name": "wrong_marker",
    "disposition": "killed",
    "cases": 18,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_country_guards::test_composite_ai_country_discovery_refused[alpha-dict]",
      "tests.integration.test_composite_ai_country_guards::test_composite_ai_country_discovery_refused[alpha-sqlite]",
      "tests.integration.test_composite_ai_country_guards::test_composite_ai_country_discovery_refused[gamma-dict]",
      "tests.integration.test_composite_ai_country_guards::test_composite_ai_country_discovery_refused[gamma-sqlite]"
    ]
  },
  {
    "name": "no_reason",
    "disposition": "killed",
    "cases": 18,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_country_guards::test_composite_ai_country_discovery_refused[alpha-dict]",
      "tests.integration.test_composite_ai_country_guards::test_composite_ai_country_discovery_refused[alpha-sqlite]",
      "tests.integration.test_composite_ai_country_guards::test_composite_ai_country_discovery_refused[gamma-dict]",
      "tests.integration.test_composite_ai_country_guards::test_composite_ai_country_discovery_refused[gamma-sqlite]"
    ]
  },
  {
    "name": "return_countries_with_refusal",
    "disposition": "killed",
    "cases": 18,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_country_guards::test_composite_ai_country_discovery_refused[alpha-dict]",
      "tests.integration.test_composite_ai_country_guards::test_composite_ai_country_discovery_refused[alpha-sqlite]",
      "tests.integration.test_composite_ai_country_guards::test_composite_ai_country_discovery_refused[gamma-dict]",
      "tests.integration.test_composite_ai_country_guards::test_composite_ai_country_discovery_refused[gamma-sqlite]"
    ]
  },
  {
    "name": "return_plans_with_refusal",
    "disposition": "killed",
    "cases": 18,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_country_guards::test_composite_ai_country_discovery_refused[alpha-dict]",
      "tests.integration.test_composite_ai_country_guards::test_composite_ai_country_discovery_refused[alpha-sqlite]",
      "tests.integration.test_composite_ai_country_guards::test_composite_ai_country_discovery_refused[gamma-dict]",
      "tests.integration.test_composite_ai_country_guards::test_composite_ai_country_discovery_refused[gamma-sqlite]"
    ]
  },
  {
    "name": "write_before_refusal",
    "disposition": "killed",
    "cases": 18,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_country_guards::test_composite_ai_country_discovery_refused[alpha-dict]",
      "tests.integration.test_composite_ai_country_guards::test_composite_ai_country_discovery_refused[alpha-sqlite]",
      "tests.integration.test_composite_ai_country_guards::test_composite_ai_country_discovery_refused[gamma-dict]",
      "tests.integration.test_composite_ai_country_guards::test_composite_ai_country_discovery_refused[gamma-sqlite]"
    ]
  },
  {
    "name": "reject_missing",
    "disposition": "killed",
    "cases": 18,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_country_guards::test_legacy_ai_country_discovery_exact[None-dict]",
      "tests.integration.test_composite_ai_country_guards::test_legacy_ai_country_discovery_exact[None-sqlite]",
      "tests.integration.test_composite_ai_country_guards::test_legacy_ai_country_discovery_exact[legacy-dict]",
      "tests.integration.test_composite_ai_country_guards::test_legacy_ai_country_discovery_exact[legacy-sqlite]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[inactive_product-dict]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[inactive_product-sqlite]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[inactive_server-dict]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[inactive_server-sqlite]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[server_not_custom-dict]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[server_not_custom-sqlite]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[mirrored_server-dict]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[mirrored_server-sqlite]"
    ]
  },
  {
    "name": "reject_explicit_legacy",
    "disposition": "killed",
    "cases": 18,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_country_guards::test_legacy_ai_country_discovery_exact[legacy-dict]",
      "tests.integration.test_composite_ai_country_guards::test_legacy_ai_country_discovery_exact[legacy-sqlite]"
    ]
  },
  {
    "name": "scan_excluded_server",
    "disposition": "killed",
    "cases": 18,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[inactive_server-dict]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[inactive_server-sqlite]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[server_not_custom-dict]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[server_not_custom-sqlite]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[mirrored_server-dict]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[mirrored_server-sqlite]"
    ]
  },
  {
    "name": "ignore_inactive_products",
    "disposition": "killed",
    "cases": 18,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[inactive_product-dict]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[inactive_product-sqlite]"
    ]
  },
  {
    "name": "ignore_inactive_servers",
    "disposition": "killed",
    "cases": 18,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[inactive_server-dict]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[inactive_server-sqlite]"
    ]
  },
  {
    "name": "ignore_mirror_filter",
    "disposition": "killed",
    "cases": 18,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[mirrored_server-dict]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[mirrored_server-sqlite]"
    ]
  },
  {
    "name": "ignore_custom_use",
    "disposition": "killed",
    "cases": 18,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[server_not_custom-dict]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[server_not_custom-sqlite]",
      "tests.integration.test_composite_ai_country_guards::test_empty_catalog_control_with_composite[dict]",
      "tests.integration.test_composite_ai_country_guards::test_empty_catalog_control_with_composite[sqlite]"
    ]
  },
  {
    "name": "empty_catalog_refused",
    "disposition": "killed",
    "cases": 18,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_country_guards::test_empty_catalog_control_with_composite[dict]",
      "tests.integration.test_composite_ai_country_guards::test_empty_catalog_control_with_composite[sqlite]"
    ]
  },
  {
    "name": "wrong_country",
    "disposition": "killed",
    "cases": 18,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_country_guards::test_legacy_ai_country_discovery_exact[None-dict]",
      "tests.integration.test_composite_ai_country_guards::test_legacy_ai_country_discovery_exact[None-sqlite]",
      "tests.integration.test_composite_ai_country_guards::test_legacy_ai_country_discovery_exact[legacy-dict]",
      "tests.integration.test_composite_ai_country_guards::test_legacy_ai_country_discovery_exact[legacy-sqlite]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[inactive_product-dict]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[inactive_product-sqlite]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[inactive_server-dict]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[inactive_server-sqlite]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[server_not_custom-dict]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[server_not_custom-sqlite]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[mirrored_server-dict]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[mirrored_server-sqlite]"
    ]
  },
  {
    "name": "wrong_product",
    "disposition": "killed",
    "cases": 18,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_country_guards::test_legacy_ai_country_discovery_exact[None-dict]",
      "tests.integration.test_composite_ai_country_guards::test_legacy_ai_country_discovery_exact[None-sqlite]",
      "tests.integration.test_composite_ai_country_guards::test_legacy_ai_country_discovery_exact[legacy-dict]",
      "tests.integration.test_composite_ai_country_guards::test_legacy_ai_country_discovery_exact[legacy-sqlite]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[inactive_product-dict]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[inactive_product-sqlite]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[inactive_server-dict]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[inactive_server-sqlite]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[server_not_custom-dict]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[server_not_custom-sqlite]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[mirrored_server-dict]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[mirrored_server-sqlite]"
    ]
  },
  {
    "name": "wrong_min",
    "disposition": "killed",
    "cases": 18,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_country_guards::test_legacy_ai_country_discovery_exact[None-dict]",
      "tests.integration.test_composite_ai_country_guards::test_legacy_ai_country_discovery_exact[None-sqlite]",
      "tests.integration.test_composite_ai_country_guards::test_legacy_ai_country_discovery_exact[legacy-dict]",
      "tests.integration.test_composite_ai_country_guards::test_legacy_ai_country_discovery_exact[legacy-sqlite]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[inactive_product-dict]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[inactive_product-sqlite]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[inactive_server-dict]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[inactive_server-sqlite]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[server_not_custom-dict]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[server_not_custom-sqlite]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[mirrored_server-dict]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[mirrored_server-sqlite]"
    ]
  },
  {
    "name": "wrong_max",
    "disposition": "killed",
    "cases": 18,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_country_guards::test_legacy_ai_country_discovery_exact[None-dict]",
      "tests.integration.test_composite_ai_country_guards::test_legacy_ai_country_discovery_exact[None-sqlite]",
      "tests.integration.test_composite_ai_country_guards::test_legacy_ai_country_discovery_exact[legacy-dict]",
      "tests.integration.test_composite_ai_country_guards::test_legacy_ai_country_discovery_exact[legacy-sqlite]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[inactive_product-dict]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[inactive_product-sqlite]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[inactive_server-dict]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[inactive_server-sqlite]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[server_not_custom-dict]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[server_not_custom-sqlite]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[mirrored_server-dict]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[mirrored_server-sqlite]"
    ]
  },
  {
    "name": "drop_second_plan",
    "disposition": "killed",
    "cases": 18,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_country_guards::test_legacy_ai_country_discovery_exact[None-dict]",
      "tests.integration.test_composite_ai_country_guards::test_legacy_ai_country_discovery_exact[None-sqlite]",
      "tests.integration.test_composite_ai_country_guards::test_legacy_ai_country_discovery_exact[legacy-dict]",
      "tests.integration.test_composite_ai_country_guards::test_legacy_ai_country_discovery_exact[legacy-sqlite]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[inactive_product-dict]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[inactive_product-sqlite]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[inactive_server-dict]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[inactive_server-sqlite]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[server_not_custom-dict]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[server_not_custom-sqlite]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[mirrored_server-dict]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[mirrored_server-sqlite]"
    ]
  },
  {
    "name": "drop_second_server",
    "disposition": "killed",
    "cases": 18,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_country_guards::test_legacy_ai_country_discovery_exact[None-dict]",
      "tests.integration.test_composite_ai_country_guards::test_legacy_ai_country_discovery_exact[None-sqlite]",
      "tests.integration.test_composite_ai_country_guards::test_legacy_ai_country_discovery_exact[legacy-dict]",
      "tests.integration.test_composite_ai_country_guards::test_legacy_ai_country_discovery_exact[legacy-sqlite]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[inactive_product-dict]",
      "tests.integration.test_composite_ai_country_guards::test_isolated_composite_ai_country_discovery[inactive_product-sqlite]"
    ]
  }
]
```

Independent valid mutations, relevant assertion failures only. No survivors/errors/skips. Scratch auto-cleaned. Reference checks active products on visible custom-use servers after real SQL reads before unchanged grouping; no production implementation claim.
