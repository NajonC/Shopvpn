# T050s reference and mutation evidence

Source hashes:
```json
{
  "ai_support.py": "1297845ea834eee309443bbc9c9a11ffcea4e982e190d9dbb9c67adfffea5eeb",
  "tests/integration/test_composite_ai_stock_retrieval_guards.py": "be01b981a1df43edcc9fff1ba14f50509b05dab1a52b9f8f285e315e869e3f8a",
  "tests/characterization/test_legacy_renewal_reminders.py": "84722b6b10d9fbdae768cb5fb8e8fbc3490b3a213575196210a56401c6e61ea3"
}
```

Results:
```json
[
  {
    "name": "reference",
    "disposition": "passed",
    "cases": 91,
    "failed_test_ids": []
  },
  {
    "name": "omit_both",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_service_qr-config-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_service_qr-config-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_service_qr-order-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_service_qr-order-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_individual_configs-config-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_individual_configs-config-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_individual_configs-order-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_individual_configs-order-sqlite]"
    ]
  },
  {
    "name": "omit_config",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_service_qr-config-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_service_qr-config-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_individual_configs-config-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_individual_configs-config-sqlite]"
    ]
  },
  {
    "name": "omit_order",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_service_qr-order-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_service_qr-order-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_individual_configs-order-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_individual_configs-order-sqlite]"
    ]
  },
  {
    "name": "omit_qr",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_service_qr-config-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_service_qr-config-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_service_qr-order-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_service_qr-order-sqlite]"
    ]
  },
  {
    "name": "omit_individual",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_individual_configs-config-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_individual_configs-config-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_individual_configs-order-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_individual_configs-order-sqlite]"
    ]
  },
  {
    "name": "wrong_marker",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_service_qr-config-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_service_qr-config-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_service_qr-order-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_service_qr-order-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_individual_configs-config-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_individual_configs-config-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_individual_configs-order-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_individual_configs-order-sqlite]"
    ]
  },
  {
    "name": "no_reason",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_service_qr-config-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_service_qr-config-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_service_qr-order-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_service_qr-order-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_individual_configs-config-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_individual_configs-config-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_individual_configs-order-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_individual_configs-order-sqlite]"
    ]
  },
  {
    "name": "reject_missing",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_ai_stock_retrieval_preserved[request_service_qr-config-None-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_ai_stock_retrieval_preserved[request_service_qr-config-None-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_ai_stock_retrieval_preserved[request_service_qr-config-legacy-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_ai_stock_retrieval_preserved[request_service_qr-config-legacy-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_ai_stock_retrieval_preserved[request_service_qr-order-None-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_ai_stock_retrieval_preserved[request_service_qr-order-None-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_ai_stock_retrieval_preserved[request_service_qr-order-legacy-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_ai_stock_retrieval_preserved[request_service_qr-order-legacy-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_ai_stock_retrieval_preserved[request_individual_configs-config-None-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_ai_stock_retrieval_preserved[request_individual_configs-config-None-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_ai_stock_retrieval_preserved[request_individual_configs-config-legacy-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_ai_stock_retrieval_preserved[request_individual_configs-config-legacy-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_ai_stock_retrieval_preserved[request_individual_configs-order-None-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_ai_stock_retrieval_preserved[request_individual_configs-order-None-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_ai_stock_retrieval_preserved[request_individual_configs-order-legacy-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_ai_stock_retrieval_preserved[request_individual_configs-order-legacy-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_unrelated_composite_order_allows_legacy_stock_retrieval[request_service_qr-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_unrelated_composite_order_allows_legacy_stock_retrieval[request_service_qr-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_unrelated_composite_order_allows_legacy_stock_retrieval[request_individual_configs-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_unrelated_composite_order_allows_legacy_stock_retrieval[request_individual_configs-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_stock_retrieval_restrictions[request_service_qr-empty_link-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_stock_retrieval_restrictions[request_service_qr-empty_link-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_stock_retrieval_restrictions[request_service_qr-native_link-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_stock_retrieval_restrictions[request_service_qr-native_link-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_stock_retrieval_restrictions[request_individual_configs-empty_link-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_stock_retrieval_restrictions[request_individual_configs-empty_link-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_stock_retrieval_restrictions[request_individual_configs-native_link-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_stock_retrieval_restrictions[request_individual_configs-native_link-sqlite]"
    ]
  },
  {
    "name": "reject_explicit_legacy",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_ai_stock_retrieval_preserved[request_service_qr-config-legacy-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_ai_stock_retrieval_preserved[request_service_qr-config-legacy-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_ai_stock_retrieval_preserved[request_service_qr-order-legacy-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_ai_stock_retrieval_preserved[request_service_qr-order-legacy-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_ai_stock_retrieval_preserved[request_individual_configs-config-legacy-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_ai_stock_retrieval_preserved[request_individual_configs-config-legacy-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_ai_stock_retrieval_preserved[request_individual_configs-order-legacy-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_ai_stock_retrieval_preserved[request_individual_configs-order-legacy-sqlite]"
    ]
  },
  {
    "name": "scan_unrelated",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_unrelated_composite_order_allows_legacy_stock_retrieval[request_service_qr-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_unrelated_composite_order_allows_legacy_stock_retrieval[request_service_qr-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_unrelated_composite_order_allows_legacy_stock_retrieval[request_individual_configs-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_unrelated_composite_order_allows_legacy_stock_retrieval[request_individual_configs-sqlite]"
    ]
  },
  {
    "name": "leak_response",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_service_qr-config-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_service_qr-config-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_individual_configs-config-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_individual_configs-config-sqlite]"
    ]
  },
  {
    "name": "leak_log",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_service_qr-config-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_service_qr-config-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_individual_configs-config-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_individual_configs-config-sqlite]"
    ]
  },
  {
    "name": "fetch_before_refusal",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_service_qr-config-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_service_qr-config-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_service_qr-order-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_service_qr-order-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_individual_configs-config-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_individual_configs-config-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_individual_configs-order-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_individual_configs-order-sqlite]"
    ]
  },
  {
    "name": "provider_before_refusal",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_service_qr-config-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_service_qr-config-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_service_qr-order-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_service_qr-order-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_individual_configs-config-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_individual_configs-config-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_individual_configs-order-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_individual_configs-order-sqlite]"
    ]
  },
  {
    "name": "write_before_refusal",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_service_qr-config-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_service_qr-config-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_service_qr-order-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_service_qr-order-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_individual_configs-config-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_individual_configs-config-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_individual_configs-order-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_composite_ai_stock_retrieval_refused[request_individual_configs-order-sqlite]"
    ]
  },
  {
    "name": "wrong_requester",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_foreign_ai_stock_retrieval_opaque[request_service_qr-config-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_foreign_ai_stock_retrieval_opaque[request_service_qr-config-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_foreign_ai_stock_retrieval_opaque[request_service_qr-order-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_foreign_ai_stock_retrieval_opaque[request_service_qr-order-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_foreign_ai_stock_retrieval_opaque[request_individual_configs-config-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_foreign_ai_stock_retrieval_opaque[request_individual_configs-config-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_foreign_ai_stock_retrieval_opaque[request_individual_configs-order-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_foreign_ai_stock_retrieval_opaque[request_individual_configs-order-sqlite]"
    ]
  },
  {
    "name": "preflight_wrong_requester",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_foreign_ai_stock_retrieval_opaque[request_service_qr-config-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_foreign_ai_stock_retrieval_opaque[request_service_qr-config-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_foreign_ai_stock_retrieval_opaque[request_individual_configs-config-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_foreign_ai_stock_retrieval_opaque[request_individual_configs-config-sqlite]"
    ]
  },
  {
    "name": "ignore_disabled",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_stock_retrieval_restrictions[request_service_qr-disabled-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_stock_retrieval_restrictions[request_service_qr-disabled-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_stock_retrieval_restrictions[request_individual_configs-disabled-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_stock_retrieval_restrictions[request_individual_configs-disabled-sqlite]"
    ]
  },
  {
    "name": "ignore_approved",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_stock_retrieval_restrictions[request_service_qr-unapproved-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_stock_retrieval_restrictions[request_service_qr-unapproved-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_stock_retrieval_restrictions[request_individual_configs-unapproved-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_stock_retrieval_restrictions[request_individual_configs-unapproved-sqlite]"
    ]
  },
  {
    "name": "wrong_id_request_service_qr",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_ai_stock_retrieval_preserved[request_service_qr-config-None-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_ai_stock_retrieval_preserved[request_service_qr-config-None-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_ai_stock_retrieval_preserved[request_service_qr-config-legacy-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_ai_stock_retrieval_preserved[request_service_qr-config-legacy-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_ai_stock_retrieval_preserved[request_service_qr-order-None-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_ai_stock_retrieval_preserved[request_service_qr-order-None-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_ai_stock_retrieval_preserved[request_service_qr-order-legacy-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_ai_stock_retrieval_preserved[request_service_qr-order-legacy-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_unrelated_composite_order_allows_legacy_stock_retrieval[request_service_qr-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_unrelated_composite_order_allows_legacy_stock_retrieval[request_service_qr-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_stock_retrieval_restrictions[request_service_qr-native_link-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_stock_retrieval_restrictions[request_service_qr-native_link-sqlite]"
    ]
  },
  {
    "name": "wrong_id_request_individual_configs",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_ai_stock_retrieval_preserved[request_individual_configs-config-None-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_ai_stock_retrieval_preserved[request_individual_configs-config-None-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_ai_stock_retrieval_preserved[request_individual_configs-config-legacy-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_ai_stock_retrieval_preserved[request_individual_configs-config-legacy-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_ai_stock_retrieval_preserved[request_individual_configs-order-None-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_ai_stock_retrieval_preserved[request_individual_configs-order-None-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_ai_stock_retrieval_preserved[request_individual_configs-order-legacy-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_ai_stock_retrieval_preserved[request_individual_configs-order-legacy-sqlite]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_unrelated_composite_order_allows_legacy_stock_retrieval[request_individual_configs-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_unrelated_composite_order_allows_legacy_stock_retrieval[request_individual_configs-sqlite]"
    ]
  },
  {
    "name": "qr_accept_empty",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_stock_retrieval_restrictions[request_service_qr-empty_link-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_stock_retrieval_restrictions[request_service_qr-empty_link-sqlite]"
    ]
  },
  {
    "name": "qr_reject_native",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_stock_retrieval_restrictions[request_service_qr-native_link-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_stock_retrieval_restrictions[request_service_qr-native_link-sqlite]"
    ]
  },
  {
    "name": "individual_accept_native",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_stock_retrieval_restrictions[request_individual_configs-native_link-dict]",
      "tests.integration.test_composite_ai_stock_retrieval_guards::test_legacy_stock_retrieval_restrictions[request_individual_configs-native_link-sqlite]"
    ]
  }
]
```

Independent valid mutations, relevant assertion failures only. No survivors/errors/skips. Scratch auto-cleaned. Reference resolves real owned stock targets, checks config and matching approved-order metadata before unchanged retrieval shortcuts; no production implementation claim.
