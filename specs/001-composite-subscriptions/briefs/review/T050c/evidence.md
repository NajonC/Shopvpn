# T050c reference and mutation evidence

Hashes:
```json
{
  "direct_panel_provision.py": "50214cabd6217a7d59053fe9fe1775cf3229f01a243b63c8d4fc2087ec62cbf3",
  "config_delivery.py": "e580f3b2a6911729fc3421b5b39848a063fd84960c45223d70e2c23b4e9f5619",
  "tests/integration/test_composite_direct_guards.py": "f180a51578059bef79aac008c5724fe0d979845eea18c5ea7b92fd6a3607857b",
  "tests/integration/test_composite_delivery_guards.py": "11bde707016cf2cd5fa444216e2d291dbe3ca29ee7ab8cc4895d491d47e7514a",
  "tests/characterization/test_direct_provision.py": "4e9f59c67778e1020b4d60f7c8bac6eccb7672d8ae90bf56164aba108d0d88e5",
  "tests/characterization/test_buy_start.py": "d199331dc49248a6fe63550970db5d6d8527ca7189ad1d58f08b775b9b25d696",
  "tests/characterization/test_order_approval.py": "ddb22753d2afafdb991db3e1f21106719485313645983e1da982afac4f7a1f13"
}
```

Results:
```json
[
  {
    "name": "reference",
    "disposition": "pass",
    "cases": 123,
    "failed_test_ids": []
  },
  {
    "name": "direct_omit",
    "disposition": "killed",
    "cases": 16,
    "failed_test_ids": [
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[order-dict-1]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[order-dict-2]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[order-sqlite-1]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[order-sqlite-2]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[product-dict-1]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[product-dict-2]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[product-sqlite-1]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[product-sqlite-2]"
    ]
  },
  {
    "name": "direct_omit_product",
    "disposition": "killed",
    "cases": 16,
    "failed_test_ids": [
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[product-dict-1]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[product-dict-2]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[product-sqlite-1]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[product-sqlite-2]"
    ]
  },
  {
    "name": "direct_omit_order",
    "disposition": "killed",
    "cases": 16,
    "failed_test_ids": [
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[order-dict-1]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[order-dict-2]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[order-sqlite-1]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[order-sqlite-2]"
    ]
  },
  {
    "name": "direct_wrong_kind",
    "disposition": "killed",
    "cases": 16,
    "failed_test_ids": [
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[order-dict-1]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[order-dict-2]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[order-sqlite-1]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[order-sqlite-2]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[product-dict-1]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[product-dict-2]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[product-sqlite-1]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[product-sqlite-2]"
    ]
  },
  {
    "name": "direct_no_reason",
    "disposition": "killed",
    "cases": 16,
    "failed_test_ids": [
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[order-dict-1]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[order-dict-2]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[order-sqlite-1]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[order-sqlite-2]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[product-dict-1]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[product-dict-2]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[product-sqlite-1]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[product-sqlite-2]"
    ]
  },
  {
    "name": "direct_leak_secret",
    "disposition": "killed",
    "cases": 16,
    "failed_test_ids": [
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[order-dict-1]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[order-dict-2]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[order-sqlite-1]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[order-sqlite-2]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[product-dict-1]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[product-dict-2]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[product-sqlite-1]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[product-sqlite-2]"
    ]
  },
  {
    "name": "direct_reject_legacy",
    "disposition": "killed",
    "cases": 16,
    "failed_test_ids": [
      "tests.integration.test_composite_direct_guards::test_legacy_direct_still_builds_and_persists[legacy-dict-1]",
      "tests.integration.test_composite_direct_guards::test_legacy_direct_still_builds_and_persists[legacy-dict-2]",
      "tests.integration.test_composite_direct_guards::test_legacy_direct_still_builds_and_persists[legacy-sqlite-1]",
      "tests.integration.test_composite_direct_guards::test_legacy_direct_still_builds_and_persists[legacy-sqlite-2]"
    ]
  },
  {
    "name": "direct_reject_absent",
    "disposition": "killed",
    "cases": 16,
    "failed_test_ids": [
      "tests.integration.test_composite_direct_guards::test_legacy_direct_still_builds_and_persists[None-dict-1]",
      "tests.integration.test_composite_direct_guards::test_legacy_direct_still_builds_and_persists[None-dict-2]",
      "tests.integration.test_composite_direct_guards::test_legacy_direct_still_builds_and_persists[None-sqlite-1]",
      "tests.integration.test_composite_direct_guards::test_legacy_direct_still_builds_and_persists[None-sqlite-2]"
    ]
  },
  {
    "name": "direct_late_factory",
    "disposition": "killed",
    "cases": 16,
    "failed_test_ids": [
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[order-dict-1]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[order-dict-2]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[order-sqlite-1]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[order-sqlite-2]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[product-dict-1]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[product-dict-2]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[product-sqlite-1]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[product-sqlite-2]"
    ]
  },
  {
    "name": "direct_late_provision",
    "disposition": "killed",
    "cases": 16,
    "failed_test_ids": [
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[order-dict-1]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[order-dict-2]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[order-sqlite-1]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[order-sqlite-2]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[product-dict-1]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[product-dict-2]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[product-sqlite-1]",
      "tests.integration.test_composite_direct_guards::test_composite_direct_refused_before_provision[product-sqlite-2]"
    ]
  },
  {
    "name": "delivery_omit",
    "disposition": "killed",
    "cases": 9,
    "failed_test_ids": [
      "tests.integration.test_composite_delivery_guards::test_composite_delivery_refused_before_publication[order-dict]",
      "tests.integration.test_composite_delivery_guards::test_composite_delivery_refused_before_publication[order-sqlite]",
      "tests.integration.test_composite_delivery_guards::test_composite_delivery_refused_before_publication[product-dict]",
      "tests.integration.test_composite_delivery_guards::test_composite_delivery_refused_before_publication[product-sqlite]"
    ]
  },
  {
    "name": "delivery_omit_product",
    "disposition": "killed",
    "cases": 9,
    "failed_test_ids": [
      "tests.integration.test_composite_delivery_guards::test_composite_delivery_refused_before_publication[product-dict]",
      "tests.integration.test_composite_delivery_guards::test_composite_delivery_refused_before_publication[product-sqlite]"
    ]
  },
  {
    "name": "delivery_omit_order",
    "disposition": "killed",
    "cases": 9,
    "failed_test_ids": [
      "tests.integration.test_composite_delivery_guards::test_composite_delivery_refused_before_publication[order-dict]",
      "tests.integration.test_composite_delivery_guards::test_composite_delivery_refused_before_publication[order-sqlite]"
    ]
  },
  {
    "name": "delivery_wrong_kind",
    "disposition": "killed",
    "cases": 9,
    "failed_test_ids": [
      "tests.integration.test_composite_delivery_guards::test_composite_delivery_refused_before_publication[order-dict]",
      "tests.integration.test_composite_delivery_guards::test_composite_delivery_refused_before_publication[order-sqlite]",
      "tests.integration.test_composite_delivery_guards::test_composite_delivery_refused_before_publication[product-dict]",
      "tests.integration.test_composite_delivery_guards::test_composite_delivery_refused_before_publication[product-sqlite]"
    ]
  },
  {
    "name": "delivery_no_reason",
    "disposition": "killed",
    "cases": 9,
    "failed_test_ids": [
      "tests.integration.test_composite_delivery_guards::test_composite_delivery_refused_before_publication[order-dict]",
      "tests.integration.test_composite_delivery_guards::test_composite_delivery_refused_before_publication[order-sqlite]",
      "tests.integration.test_composite_delivery_guards::test_composite_delivery_refused_before_publication[product-dict]",
      "tests.integration.test_composite_delivery_guards::test_composite_delivery_refused_before_publication[product-sqlite]"
    ]
  },
  {
    "name": "delivery_leak_secret",
    "disposition": "killed",
    "cases": 9,
    "failed_test_ids": [
      "tests.integration.test_composite_delivery_guards::test_composite_delivery_refused_before_publication[order-dict]",
      "tests.integration.test_composite_delivery_guards::test_composite_delivery_refused_before_publication[order-sqlite]",
      "tests.integration.test_composite_delivery_guards::test_composite_delivery_refused_before_publication[product-dict]",
      "tests.integration.test_composite_delivery_guards::test_composite_delivery_refused_before_publication[product-sqlite]"
    ]
  },
  {
    "name": "delivery_reject_legacy",
    "disposition": "killed",
    "cases": 9,
    "failed_test_ids": [
      "tests.integration.test_composite_delivery_guards::test_legacy_delivery_preserves_photo_link_and_individuals[legacy-dict]",
      "tests.integration.test_composite_delivery_guards::test_legacy_delivery_preserves_photo_link_and_individuals[legacy-sqlite]"
    ]
  },
  {
    "name": "delivery_reject_absent",
    "disposition": "killed",
    "cases": 9,
    "failed_test_ids": [
      "tests.integration.test_composite_delivery_guards::test_legacy_delivery_preserves_photo_link_and_individuals[None-dict]",
      "tests.integration.test_composite_delivery_guards::test_legacy_delivery_preserves_photo_link_and_individuals[None-sqlite]"
    ]
  },
  {
    "name": "delivery_late_publication",
    "disposition": "killed",
    "cases": 9,
    "failed_test_ids": [
      "tests.integration.test_composite_delivery_guards::test_composite_delivery_refused_before_publication[order-dict]",
      "tests.integration.test_composite_delivery_guards::test_composite_delivery_refused_before_publication[order-sqlite]",
      "tests.integration.test_composite_delivery_guards::test_composite_delivery_refused_before_publication[product-dict]",
      "tests.integration.test_composite_delivery_guards::test_composite_delivery_refused_before_publication[product-sqlite]"
    ]
  },
  {
    "name": "delivery_reject_nodb",
    "disposition": "killed",
    "cases": 9,
    "failed_test_ids": [
      "tests.integration.test_composite_delivery_guards::test_legacy_delivery_without_database_still_works"
    ]
  }
]
```

Independent mutations against passing reference; relevant assertions or exact deliberate over-strict exceptions in positive controls only. No survivors/errors/skips. Scratch auto-cleaned; no production code changed.
