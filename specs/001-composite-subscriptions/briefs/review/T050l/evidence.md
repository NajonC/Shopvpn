# T050l trial verification

Hashes:
```json
{
  "miniapp/server.py": "63b15cf1f0ae0940dfc2085544b096b3e73ae778c94102488a8e485f7aa99cbc",
  "test_config_provision.py": "da8a1d32405af0c8e95b45185ab7d00e09799a7a81d2c18cfa3e698f2f8d3180",
  "tests/integration/test_composite_miniapp_trial_guards.py": "3dcd4de0a432b086bb03dec394fbae36bfc4d45d084887509c7a673e9705814e",
  "tests/characterization/test_unsupported_surfaces.py": "4dee58c924d83f592f2c76dd71626addea7774f69f91bb219d3b1c38710e4bfd",
  "tests/characterization/test_free_test_flow.py": "3e6b88540f7c55aba7805cc28dadcb5eee608a4b9b35bc7288c88f461385138f"
}
```

Results:
```json
[
  {
    "name": "reference",
    "disposition": "pass",
    "cases": 101,
    "failed_test_ids": []
  },
  {
    "name": "omit",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[status_plan-plan-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[status_plan-plan-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[status_custom-custom-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[status_custom-custom-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[status_stock-stock-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[status_stock-stock-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_explicit-plan-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_explicit-plan-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_explicit-request-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_explicit-request-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_implicit-plan-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_implicit-plan-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_implicit-request-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_implicit-request-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_stock-request-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_stock-request-sqlite]"
    ]
  },
  {
    "name": "wrong_kind",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[status_plan-plan-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[status_plan-plan-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[status_custom-custom-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[status_custom-custom-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[status_stock-stock-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[status_stock-stock-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_explicit-plan-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_explicit-plan-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_explicit-request-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_explicit-request-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_implicit-plan-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_implicit-plan-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_implicit-request-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_implicit-request-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_stock-request-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_stock-request-sqlite]"
    ]
  },
  {
    "name": "bypass_api_test_config_status",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[status_plan-plan-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[status_plan-plan-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[status_custom-custom-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[status_custom-custom-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[status_stock-stock-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[status_stock-stock-sqlite]"
    ]
  },
  {
    "name": "bypass_api_test_config_claim",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_explicit-plan-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_explicit-plan-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_explicit-request-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_explicit-request-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_implicit-plan-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_implicit-plan-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_implicit-request-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_implicit-request-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_stock-request-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_stock-request-sqlite]"
    ]
  },
  {
    "name": "omit_status_plans",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[status_plan-plan-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[status_plan-plan-sqlite]"
    ]
  },
  {
    "name": "omit_status_custom",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[status_custom-custom-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[status_custom-custom-sqlite]"
    ]
  },
  {
    "name": "omit_status_stock",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[status_stock-stock-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[status_stock-stock-sqlite]"
    ]
  },
  {
    "name": "omit_explicit_plan",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_explicit-plan-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_explicit-plan-sqlite]"
    ]
  },
  {
    "name": "omit_implicit_plan",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_implicit-plan-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_implicit-plan-sqlite]"
    ]
  },
  {
    "name": "omit_request",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_explicit-request-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_explicit-request-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_implicit-request-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_implicit-request-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_stock-request-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_stock-request-sqlite]"
    ]
  },
  {
    "name": "reject_legacy",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[status_plan-False-legacy-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[status_plan-False-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[status_custom-False-legacy-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[status_custom-False-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[status_stock-False-legacy-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[status_stock-False-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-False-legacy-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-False-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_implicit-False-legacy-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_implicit-False-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_stock-False-legacy-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_stock-False-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-True-legacy-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-True-legacy-sqlite]"
    ]
  },
  {
    "name": "reject_absent",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[status_plan-False-None-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[status_plan-False-None-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[status_custom-False-None-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[status_custom-False-None-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[status_stock-False-None-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[status_stock-False-None-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-False-None-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-False-None-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_implicit-False-None-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_implicit-False-None-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_stock-False-None-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_stock-False-None-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-True-None-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-True-None-sqlite]"
    ]
  },
  {
    "name": "no_reason",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[status_plan-plan-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[status_plan-plan-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[status_custom-custom-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[status_custom-custom-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[status_stock-stock-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[status_stock-stock-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_explicit-plan-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_explicit-plan-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_explicit-request-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_explicit-request-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_implicit-plan-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_implicit-plan-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_implicit-request-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_implicit-request-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_stock-request-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_stock-request-sqlite]"
    ]
  },
  {
    "name": "leak_link",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[status_plan-plan-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[status_plan-plan-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[status_custom-custom-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[status_custom-custom-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[status_stock-stock-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[status_stock-stock-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_explicit-plan-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_explicit-plan-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_explicit-request-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_explicit-request-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_implicit-plan-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_implicit-plan-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_implicit-request-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_implicit-request-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_stock-request-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_stock-request-sqlite]"
    ]
  },
  {
    "name": "late_auth",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[status_plan-plan-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[status_plan-plan-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[status_custom-custom-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[status_custom-custom-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[status_stock-stock-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[status_stock-stock-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_explicit-plan-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_explicit-plan-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_explicit-request-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_explicit-request-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_implicit-plan-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_implicit-plan-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_implicit-request-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_implicit-request-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_stock-request-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_stock-request-sqlite]"
    ]
  },
  {
    "name": "reserve_before_refusal",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[status_plan-plan-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[status_plan-plan-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_explicit-plan-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_explicit-plan-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_explicit-request-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_explicit-request-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_implicit-plan-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_implicit-plan-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_implicit-request-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_implicit-request-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_stock-request-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_stock-request-sqlite]"
    ]
  },
  {
    "name": "remote_before_refusal",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[status_plan-plan-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[status_plan-plan-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_explicit-plan-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_explicit-plan-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_explicit-request-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_explicit-request-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_implicit-plan-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_implicit-plan-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_implicit-request-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_composite_miniapp_trial_refused[claim_implicit-request-sqlite]"
    ]
  },
  {
    "name": "block_unrelated",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-True-None-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-True-None-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-True-legacy-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-True-legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_used",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[status_plan-False-None-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[status_plan-False-None-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[status_plan-False-legacy-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[status_plan-False-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[status_custom-False-None-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[status_custom-False-None-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[status_custom-False-legacy-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[status_custom-False-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[status_stock-False-None-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[status_stock-False-None-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[status_stock-False-legacy-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[status_stock-False-legacy-sqlite]"
    ]
  },
  {
    "name": "lost_status_link",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[status_custom-False-None-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[status_custom-False-None-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[status_custom-False-legacy-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[status_custom-False-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[status_stock-False-None-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[status_stock-False-None-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[status_stock-False-legacy-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[status_stock-False-legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_status_label",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[status_plan-False-None-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[status_plan-False-None-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[status_plan-False-legacy-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[status_plan-False-legacy-sqlite]"
    ]
  },
  {
    "name": "lost_plan_reservation",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-False-None-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-False-None-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-False-legacy-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-False-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_implicit-False-None-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_implicit-False-None-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_implicit-False-legacy-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_implicit-False-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-True-None-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-True-None-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-True-legacy-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-True-legacy-sqlite]"
    ]
  },
  {
    "name": "lost_stock_reservation",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_stock-False-None-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_stock-False-None-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_stock-False-legacy-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_stock-False-legacy-sqlite]"
    ]
  },
  {
    "name": "lost_stock_assignment",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_stock-False-None-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_stock-False-None-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_stock-False-legacy-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_stock-False-legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_volume_unit",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-False-None-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-False-None-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-False-legacy-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-False-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_implicit-False-None-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_implicit-False-None-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_implicit-False-legacy-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_implicit-False-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-True-None-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-True-None-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-True-legacy-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-True-legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_duration_unit",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-False-None-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-False-None-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-False-legacy-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-False-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_implicit-False-None-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_implicit-False-None-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_implicit-False-legacy-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_implicit-False-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-True-None-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-True-None-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-True-legacy-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-True-legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_claimant",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-False-None-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-False-None-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-False-legacy-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-False-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_implicit-False-None-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_implicit-False-None-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_implicit-False-legacy-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_implicit-False-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-True-None-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-True-None-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-True-legacy-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-True-legacy-sqlite]"
    ]
  },
  {
    "name": "lost_local_record",
    "disposition": "killed",
    "cases": 44,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-False-None-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-False-None-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-False-legacy-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-False-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_implicit-False-None-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_implicit-False-None-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_implicit-False-legacy-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_implicit-False-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-True-None-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-True-None-sqlite]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-True-legacy-dict]",
      "tests.integration.test_composite_miniapp_trial_guards::test_legacy_miniapp_trial_preserved[claim_explicit-True-legacy-sqlite]"
    ]
  }
]
```

Independent mutants with relevant packet assertions only; no survivors/errors/skips. Real signed ownership and original legacy trial selection/allowance/provision/exports preserved; unselected composite plan does not block explicit legacy claim. Source-only scratch auto-cleaned; no production edits.
