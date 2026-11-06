# T050g web supply verification

Hashes:
```json
{
  "admin_panel/server.py": "ee9c2dc47c30d7c4a502e6a6f4b57ecfe93343f1468a7e601703da8c1bef7511",
  "tests/integration/test_composite_reseller_web_guards.py": "db7f6de5ca9646a2a186b7763a70b5ca0472cf9b9f81088fe7a7514cc54e52da",
  "tests/characterization/test_unsupported_surfaces.py": "4dee58c924d83f592f2c76dd71626addea7774f69f91bb219d3b1c38710e4bfd"
}
```

Results:
```json
[
  {
    "name": "reference",
    "disposition": "pass",
    "cases": 45,
    "failed_test_ids": []
  },
  {
    "name": "helper_omit",
    "disposition": "killed",
    "cases": 14,
    "failed_test_ids": [
      "tests.integration.test_composite_reseller_web_guards::test_composite_reseller_web_refused_before_effects[fixed-product-dict]",
      "tests.integration.test_composite_reseller_web_guards::test_composite_reseller_web_refused_before_effects[fixed-product-sqlite]"
    ]
  },
  {
    "name": "helper_wrong_kind",
    "disposition": "killed",
    "cases": 14,
    "failed_test_ids": [
      "tests.integration.test_composite_reseller_web_guards::test_composite_reseller_web_refused_before_effects[fixed-product-dict]",
      "tests.integration.test_composite_reseller_web_guards::test_composite_reseller_web_refused_before_effects[fixed-product-sqlite]"
    ]
  },
  {
    "name": "helper_reject_legacy",
    "disposition": "killed",
    "cases": 14,
    "failed_test_ids": [
      "tests.integration.test_composite_reseller_web_guards::test_legacy_reseller_web_preserves_credit_and_service[fixed-legacy-dict]",
      "tests.integration.test_composite_reseller_web_guards::test_legacy_reseller_web_preserves_credit_and_service[fixed-legacy-sqlite]"
    ]
  },
  {
    "name": "helper_reject_absent",
    "disposition": "killed",
    "cases": 14,
    "failed_test_ids": [
      "tests.integration.test_composite_reseller_web_guards::test_legacy_reseller_web_preserves_credit_and_service[fixed-None-dict]",
      "tests.integration.test_composite_reseller_web_guards::test_legacy_reseller_web_preserves_credit_and_service[fixed-None-sqlite]"
    ]
  },
  {
    "name": "helper_no_reason",
    "disposition": "killed",
    "cases": 14,
    "failed_test_ids": [
      "tests.integration.test_composite_reseller_web_guards::test_composite_reseller_web_refused_before_effects[fixed-product-dict]",
      "tests.integration.test_composite_reseller_web_guards::test_composite_reseller_web_refused_before_effects[fixed-product-sqlite]"
    ]
  },
  {
    "name": "helper_leak_name",
    "disposition": "killed",
    "cases": 14,
    "failed_test_ids": [
      "tests.integration.test_composite_reseller_web_guards::test_composite_reseller_web_refused_before_effects[fixed-product-dict]",
      "tests.integration.test_composite_reseller_web_guards::test_composite_reseller_web_refused_before_effects[fixed-product-sqlite]"
    ]
  },
  {
    "name": "helper_late_factory",
    "disposition": "killed",
    "cases": 14,
    "failed_test_ids": [
      "tests.integration.test_composite_reseller_web_guards::test_composite_reseller_web_refused_before_effects[fixed-product-dict]",
      "tests.integration.test_composite_reseller_web_guards::test_composite_reseller_web_refused_before_effects[fixed-product-sqlite]"
    ]
  },
  {
    "name": "helper_late_commit",
    "disposition": "killed",
    "cases": 14,
    "failed_test_ids": [
      "tests.integration.test_composite_reseller_web_guards::test_composite_reseller_web_refused_before_effects[fixed-product-dict]",
      "tests.integration.test_composite_reseller_web_guards::test_composite_reseller_web_refused_before_effects[fixed-product-sqlite]"
    ]
  },
  {
    "name": "api_reseller_self_fixed_omit",
    "disposition": "killed",
    "cases": 14,
    "failed_test_ids": [
      "tests.integration.test_composite_reseller_web_guards::test_composite_reseller_web_refused_before_effects[fixed-request-dict]",
      "tests.integration.test_composite_reseller_web_guards::test_composite_reseller_web_refused_before_effects[fixed-request-sqlite]"
    ]
  },
  {
    "name": "api_reseller_self_fixed_wrong_kind",
    "disposition": "killed",
    "cases": 14,
    "failed_test_ids": [
      "tests.integration.test_composite_reseller_web_guards::test_composite_reseller_web_refused_before_effects[fixed-request-dict]",
      "tests.integration.test_composite_reseller_web_guards::test_composite_reseller_web_refused_before_effects[fixed-request-sqlite]"
    ]
  },
  {
    "name": "api_reseller_self_fixed_reject_legacy",
    "disposition": "killed",
    "cases": 14,
    "failed_test_ids": [
      "tests.integration.test_composite_reseller_web_guards::test_legacy_reseller_web_preserves_credit_and_service[fixed-None-dict]",
      "tests.integration.test_composite_reseller_web_guards::test_legacy_reseller_web_preserves_credit_and_service[fixed-None-sqlite]",
      "tests.integration.test_composite_reseller_web_guards::test_legacy_reseller_web_preserves_credit_and_service[fixed-legacy-dict]",
      "tests.integration.test_composite_reseller_web_guards::test_legacy_reseller_web_preserves_credit_and_service[fixed-legacy-sqlite]"
    ]
  },
  {
    "name": "api_reseller_self_fixed_no_reason",
    "disposition": "killed",
    "cases": 14,
    "failed_test_ids": [
      "tests.integration.test_composite_reseller_web_guards::test_composite_reseller_web_refused_before_effects[fixed-request-dict]",
      "tests.integration.test_composite_reseller_web_guards::test_composite_reseller_web_refused_before_effects[fixed-request-sqlite]"
    ]
  },
  {
    "name": "api_reseller_self_fixed_late_commit",
    "disposition": "killed",
    "cases": 14,
    "failed_test_ids": [
      "tests.integration.test_composite_reseller_web_guards::test_composite_reseller_web_refused_before_effects[fixed-request-dict]",
      "tests.integration.test_composite_reseller_web_guards::test_composite_reseller_web_refused_before_effects[fixed-request-sqlite]"
    ]
  },
  {
    "name": "api_reseller_self_fixed_discard_marker",
    "disposition": "killed",
    "cases": 14,
    "failed_test_ids": [
      "tests.integration.test_composite_reseller_web_guards::test_composite_reseller_web_refused_before_effects[fixed-request-dict]",
      "tests.integration.test_composite_reseller_web_guards::test_composite_reseller_web_refused_before_effects[fixed-request-sqlite]"
    ]
  },
  {
    "name": "api_reseller_self_custom_omit",
    "disposition": "killed",
    "cases": 14,
    "failed_test_ids": [
      "tests.integration.test_composite_reseller_web_guards::test_composite_reseller_web_refused_before_effects[custom-request-dict]",
      "tests.integration.test_composite_reseller_web_guards::test_composite_reseller_web_refused_before_effects[custom-request-sqlite]"
    ]
  },
  {
    "name": "api_reseller_self_custom_wrong_kind",
    "disposition": "killed",
    "cases": 14,
    "failed_test_ids": [
      "tests.integration.test_composite_reseller_web_guards::test_composite_reseller_web_refused_before_effects[custom-request-dict]",
      "tests.integration.test_composite_reseller_web_guards::test_composite_reseller_web_refused_before_effects[custom-request-sqlite]"
    ]
  },
  {
    "name": "api_reseller_self_custom_reject_legacy",
    "disposition": "killed",
    "cases": 14,
    "failed_test_ids": [
      "tests.integration.test_composite_reseller_web_guards::test_legacy_reseller_web_preserves_credit_and_service[custom-None-dict]",
      "tests.integration.test_composite_reseller_web_guards::test_legacy_reseller_web_preserves_credit_and_service[custom-None-sqlite]",
      "tests.integration.test_composite_reseller_web_guards::test_legacy_reseller_web_preserves_credit_and_service[custom-legacy-dict]",
      "tests.integration.test_composite_reseller_web_guards::test_legacy_reseller_web_preserves_credit_and_service[custom-legacy-sqlite]"
    ]
  },
  {
    "name": "api_reseller_self_custom_no_reason",
    "disposition": "killed",
    "cases": 14,
    "failed_test_ids": [
      "tests.integration.test_composite_reseller_web_guards::test_composite_reseller_web_refused_before_effects[custom-request-dict]",
      "tests.integration.test_composite_reseller_web_guards::test_composite_reseller_web_refused_before_effects[custom-request-sqlite]"
    ]
  },
  {
    "name": "api_reseller_self_custom_late_commit",
    "disposition": "killed",
    "cases": 14,
    "failed_test_ids": [
      "tests.integration.test_composite_reseller_web_guards::test_composite_reseller_web_refused_before_effects[custom-request-dict]",
      "tests.integration.test_composite_reseller_web_guards::test_composite_reseller_web_refused_before_effects[custom-request-sqlite]"
    ]
  },
  {
    "name": "api_reseller_self_custom_discard_marker",
    "disposition": "killed",
    "cases": 14,
    "failed_test_ids": [
      "tests.integration.test_composite_reseller_web_guards::test_composite_reseller_web_refused_before_effects[custom-request-dict]",
      "tests.integration.test_composite_reseller_web_guards::test_composite_reseller_web_refused_before_effects[custom-request-sqlite]"
    ]
  }
]
```

All mutants independent with relevant packet assertions; no survivors/errors/skips. Real synthetic signed-session HTTP, main/tenant accounting and external fakes. Scratch auto-cleaned; no production edits.
