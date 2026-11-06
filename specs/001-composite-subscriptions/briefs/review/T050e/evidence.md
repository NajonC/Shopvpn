# T050e reference and mutation evidence

Hashes:
```json
{
  "reseller_auto_provision.py": "5eddd2e0098f879631fa2863f8c2f38b9068f63c34345e58719dcf5052972c73",
  "tests/integration/test_composite_reseller_provision_guards.py": "6a2e033ac5a232f9db45bba961c0907f6735f68a8ec81057152e80f6b1d042ac",
  "tests/characterization/test_unsupported_surfaces.py": "4dee58c924d83f592f2c76dd71626addea7774f69f91bb219d3b1c38710e4bfd"
}
```

Results:
```json
[
  {
    "name": "reference",
    "disposition": "pass",
    "cases": 51,
    "failed_test_ids": []
  },
  {
    "name": "provision_auto_config_omit",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[auto-product-dict]",
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[auto-product-sqlite]",
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[auto-order-dict]",
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[auto-order-sqlite]"
    ]
  },
  {
    "name": "provision_auto_config_wrong_kind",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[auto-product-dict]",
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[auto-product-sqlite]",
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[auto-order-dict]",
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[auto-order-sqlite]"
    ]
  },
  {
    "name": "provision_auto_config_no_reason",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[auto-product-dict]",
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[auto-product-sqlite]",
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[auto-order-dict]",
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[auto-order-sqlite]"
    ]
  },
  {
    "name": "provision_auto_config_leak_name",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[auto-product-dict]",
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[auto-product-sqlite]",
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[auto-order-dict]",
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[auto-order-sqlite]"
    ]
  },
  {
    "name": "provision_auto_config_reject_legacy",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_reseller_provision_guards::test_legacy_reseller_provision_preserves_credit_and_records[auto-legacy-dict]",
      "tests.integration.test_composite_reseller_provision_guards::test_legacy_reseller_provision_preserves_credit_and_records[auto-legacy-sqlite]"
    ]
  },
  {
    "name": "provision_auto_config_reject_absent",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_reseller_provision_guards::test_legacy_reseller_provision_preserves_credit_and_records[auto-None-dict]",
      "tests.integration.test_composite_reseller_provision_guards::test_legacy_reseller_provision_preserves_credit_and_records[auto-None-sqlite]",
      "tests.integration.test_composite_reseller_provision_guards::test_legacy_reseller_provision_preserves_credit_and_records[test-None-dict]",
      "tests.integration.test_composite_reseller_provision_guards::test_legacy_reseller_provision_preserves_credit_and_records[test-None-sqlite]",
      "tests.integration.test_composite_reseller_provision_guards::test_legacy_reseller_provision_preserves_credit_and_records[test-legacy-dict]",
      "tests.integration.test_composite_reseller_provision_guards::test_legacy_reseller_provision_preserves_credit_and_records[test-legacy-sqlite]"
    ]
  },
  {
    "name": "provision_auto_config_late_commit",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[auto-product-dict]",
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[auto-product-sqlite]",
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[auto-order-dict]",
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[auto-order-sqlite]"
    ]
  },
  {
    "name": "provision_auto_config_omit_product",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[auto-product-dict]",
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[auto-product-sqlite]"
    ]
  },
  {
    "name": "provision_auto_config_omit_order",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[auto-order-dict]",
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[auto-order-sqlite]"
    ]
  },
  {
    "name": "provision_auto_config_late_factory",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[auto-product-dict]",
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[auto-product-sqlite]",
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[auto-order-dict]",
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[auto-order-sqlite]"
    ]
  },
  {
    "name": "provision_test_config_omit",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[test-plan-dict]",
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[test-plan-sqlite]"
    ]
  },
  {
    "name": "provision_test_config_wrong_kind",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[test-plan-dict]",
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[test-plan-sqlite]"
    ]
  },
  {
    "name": "provision_test_config_no_reason",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[test-plan-dict]",
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[test-plan-sqlite]"
    ]
  },
  {
    "name": "provision_test_config_leak_name",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[test-plan-dict]",
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[test-plan-sqlite]"
    ]
  },
  {
    "name": "provision_test_config_reject_legacy",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_reseller_provision_guards::test_legacy_reseller_provision_preserves_credit_and_records[test-legacy-dict]",
      "tests.integration.test_composite_reseller_provision_guards::test_legacy_reseller_provision_preserves_credit_and_records[test-legacy-sqlite]"
    ]
  },
  {
    "name": "provision_test_config_reject_absent",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_reseller_provision_guards::test_legacy_reseller_provision_preserves_credit_and_records[test-None-dict]",
      "tests.integration.test_composite_reseller_provision_guards::test_legacy_reseller_provision_preserves_credit_and_records[test-None-sqlite]"
    ]
  },
  {
    "name": "provision_test_config_late_commit",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[test-plan-dict]",
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[test-plan-sqlite]"
    ]
  },
  {
    "name": "provision_reseller_fixed_product_omit",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[fixed-product-dict]",
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[fixed-product-sqlite]"
    ]
  },
  {
    "name": "provision_reseller_fixed_product_wrong_kind",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[fixed-product-dict]",
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[fixed-product-sqlite]"
    ]
  },
  {
    "name": "provision_reseller_fixed_product_no_reason",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[fixed-product-dict]",
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[fixed-product-sqlite]"
    ]
  },
  {
    "name": "provision_reseller_fixed_product_leak_name",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[fixed-product-dict]",
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[fixed-product-sqlite]"
    ]
  },
  {
    "name": "provision_reseller_fixed_product_reject_legacy",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_reseller_provision_guards::test_legacy_reseller_provision_preserves_credit_and_records[fixed-legacy-dict]",
      "tests.integration.test_composite_reseller_provision_guards::test_legacy_reseller_provision_preserves_credit_and_records[fixed-legacy-sqlite]"
    ]
  },
  {
    "name": "provision_reseller_fixed_product_reject_absent",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_reseller_provision_guards::test_legacy_reseller_provision_preserves_credit_and_records[fixed-None-dict]",
      "tests.integration.test_composite_reseller_provision_guards::test_legacy_reseller_provision_preserves_credit_and_records[fixed-None-sqlite]"
    ]
  },
  {
    "name": "provision_reseller_fixed_product_late_commit",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[fixed-product-dict]",
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[fixed-product-sqlite]"
    ]
  },
  {
    "name": "provision_reseller_fixed_product_late_factory",
    "disposition": "killed",
    "cases": 20,
    "failed_test_ids": [
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[fixed-product-dict]",
      "tests.integration.test_composite_reseller_provision_guards::test_composite_reseller_provision_refused_before_effects[fixed-product-sqlite]"
    ]
  }
]
```

All mutants independent; relevant packet assertions or exact deliberate over-strict exceptions only. No survivors/errors/skips. Synthetic source-only scratch auto-cleaned; no production edits.
