# T050f custom-service shortcut verification

Hashes:
```json
{
  "ai_support.py": "1297845ea834eee309443bbc9c9a11ffcea4e982e190d9dbb9c67adfffea5eeb",
  "tests/integration/test_composite_ai_service_guards.py": "2a5947d149a76d01428128a1fb30f2d2040bd31f40613759bca404f0df136638",
  "tests/characterization/test_legacy_renewal_reminders.py": "84722b6b10d9fbdae768cb5fb8e8fbc3490b3a213575196210a56401c6e61ea3"
}
```

Results:
```json
[
  {
    "name": "reference",
    "disposition": "pass",
    "cases": 93,
    "failed_test_ids": []
  },
  {
    "name": "omit",
    "disposition": "killed",
    "cases": 54,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[set_service_auto_renew-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[set_service_auto_renew-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[get_service_history-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[get_service_history-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_service_qr-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_service_qr-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_individual_configs-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_individual_configs-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_toggle_service_enabled-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_toggle_service_enabled-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_rename_service-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_rename_service-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_regenerate_service_access-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_regenerate_service_access-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_transfer_service-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_transfer_service-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_delete_service-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_delete_service-sqlite]"
    ]
  },
  {
    "name": "wrong_kind",
    "disposition": "killed",
    "cases": 54,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[set_service_auto_renew-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[set_service_auto_renew-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[get_service_history-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[get_service_history-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_service_qr-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_service_qr-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_individual_configs-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_individual_configs-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_toggle_service_enabled-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_toggle_service_enabled-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_rename_service-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_rename_service-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_regenerate_service_access-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_regenerate_service_access-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_transfer_service-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_transfer_service-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_delete_service-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_delete_service-sqlite]"
    ]
  },
  {
    "name": "reject_legacy",
    "disposition": "killed",
    "cases": 54,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[set_service_auto_renew-dict-legacy]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[set_service_auto_renew-sqlite-legacy]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[get_service_history-dict-legacy]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[get_service_history-sqlite-legacy]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[request_service_qr-dict-legacy]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[request_service_qr-sqlite-legacy]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[request_individual_configs-dict-legacy]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[request_individual_configs-sqlite-legacy]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[request_toggle_service_enabled-dict-legacy]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[request_toggle_service_enabled-sqlite-legacy]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[request_rename_service-dict-legacy]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[request_rename_service-sqlite-legacy]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[request_regenerate_service_access-dict-legacy]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[request_regenerate_service_access-sqlite-legacy]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[request_transfer_service-dict-legacy]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[request_transfer_service-sqlite-legacy]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[request_delete_service-dict-legacy]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[request_delete_service-sqlite-legacy]"
    ]
  },
  {
    "name": "reject_absent",
    "disposition": "killed",
    "cases": 54,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[set_service_auto_renew-dict-None]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[set_service_auto_renew-sqlite-None]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[get_service_history-dict-None]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[get_service_history-sqlite-None]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[request_service_qr-dict-None]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[request_service_qr-sqlite-None]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[request_individual_configs-dict-None]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[request_individual_configs-sqlite-None]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[request_toggle_service_enabled-dict-None]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[request_toggle_service_enabled-sqlite-None]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[request_rename_service-dict-None]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[request_rename_service-sqlite-None]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[request_regenerate_service_access-dict-None]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[request_regenerate_service_access-sqlite-None]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[request_transfer_service-dict-None]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[request_transfer_service-sqlite-None]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[request_delete_service-dict-None]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[request_delete_service-sqlite-None]"
    ]
  },
  {
    "name": "no_explicit_reason",
    "disposition": "killed",
    "cases": 54,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[set_service_auto_renew-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[set_service_auto_renew-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[get_service_history-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[get_service_history-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_service_qr-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_service_qr-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_individual_configs-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_individual_configs-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_toggle_service_enabled-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_toggle_service_enabled-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_rename_service-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_rename_service-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_regenerate_service_access-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_regenerate_service_access-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_transfer_service-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_transfer_service-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_delete_service-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_delete_service-sqlite]"
    ]
  },
  {
    "name": "bypass_set_service_auto_renew",
    "disposition": "killed",
    "cases": 54,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[set_service_auto_renew-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[set_service_auto_renew-sqlite]"
    ]
  },
  {
    "name": "bypass_get_service_history",
    "disposition": "killed",
    "cases": 54,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[get_service_history-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[get_service_history-sqlite]"
    ]
  },
  {
    "name": "bypass_request_service_qr",
    "disposition": "killed",
    "cases": 54,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_service_qr-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_service_qr-sqlite]"
    ]
  },
  {
    "name": "bypass_request_individual_configs",
    "disposition": "killed",
    "cases": 54,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_individual_configs-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_individual_configs-sqlite]"
    ]
  },
  {
    "name": "bypass_request_toggle_service_enabled",
    "disposition": "killed",
    "cases": 54,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_toggle_service_enabled-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_toggle_service_enabled-sqlite]"
    ]
  },
  {
    "name": "bypass_request_rename_service",
    "disposition": "killed",
    "cases": 54,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_rename_service-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_rename_service-sqlite]"
    ]
  },
  {
    "name": "bypass_request_regenerate_service_access",
    "disposition": "killed",
    "cases": 54,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_regenerate_service_access-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_regenerate_service_access-sqlite]"
    ]
  },
  {
    "name": "bypass_request_transfer_service",
    "disposition": "killed",
    "cases": 54,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_transfer_service-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_transfer_service-sqlite]"
    ]
  },
  {
    "name": "bypass_request_delete_service",
    "disposition": "killed",
    "cases": 54,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_delete_service-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_delete_service-sqlite]"
    ]
  },
  {
    "name": "fetch_before_refusal",
    "disposition": "killed",
    "cases": 54,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[set_service_auto_renew-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[set_service_auto_renew-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[get_service_history-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[get_service_history-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_service_qr-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_service_qr-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_individual_configs-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_individual_configs-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_toggle_service_enabled-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_toggle_service_enabled-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_rename_service-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_rename_service-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_regenerate_service_access-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_regenerate_service_access-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_transfer_service-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_transfer_service-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_delete_service-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_delete_service-sqlite]"
    ]
  },
  {
    "name": "provider_before_refusal",
    "disposition": "killed",
    "cases": 54,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[set_service_auto_renew-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[set_service_auto_renew-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[get_service_history-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[get_service_history-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_service_qr-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_service_qr-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_individual_configs-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_individual_configs-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_toggle_service_enabled-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_toggle_service_enabled-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_rename_service-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_rename_service-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_regenerate_service_access-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_regenerate_service_access-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_transfer_service-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_transfer_service-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_delete_service-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_delete_service-sqlite]"
    ]
  },
  {
    "name": "write_before_refusal",
    "disposition": "killed",
    "cases": 54,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[set_service_auto_renew-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[set_service_auto_renew-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[get_service_history-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[get_service_history-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_service_qr-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_service_qr-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_individual_configs-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_individual_configs-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_toggle_service_enabled-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_toggle_service_enabled-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_rename_service-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_rename_service-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_regenerate_service_access-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_regenerate_service_access-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_transfer_service-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_transfer_service-sqlite]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_delete_service-dict]",
      "tests.integration.test_composite_ai_service_guards::test_composite_ai_service_shortcut_refused[request_delete_service-sqlite]"
    ]
  },
  {
    "name": "wrong_enabled_set_service_auto_renew",
    "disposition": "killed",
    "cases": 54,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[set_service_auto_renew-dict-None]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[set_service_auto_renew-dict-legacy]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[set_service_auto_renew-sqlite-None]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[set_service_auto_renew-sqlite-legacy]"
    ]
  },
  {
    "name": "wrong_enabled_request_toggle_service_enabled",
    "disposition": "killed",
    "cases": 54,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[request_toggle_service_enabled-dict-None]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[request_toggle_service_enabled-dict-legacy]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[request_toggle_service_enabled-sqlite-None]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[request_toggle_service_enabled-sqlite-legacy]"
    ]
  },
  {
    "name": "wrong_name",
    "disposition": "killed",
    "cases": 54,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[request_rename_service-dict-None]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[request_rename_service-dict-legacy]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[request_rename_service-sqlite-None]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[request_rename_service-sqlite-legacy]"
    ]
  },
  {
    "name": "wrong_target",
    "disposition": "killed",
    "cases": 54,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[request_transfer_service-dict-None]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[request_transfer_service-dict-legacy]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[request_transfer_service-sqlite-None]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[request_transfer_service-sqlite-legacy]"
    ]
  },
  {
    "name": "lost_history",
    "disposition": "killed",
    "cases": 54,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[get_service_history-dict-None]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[get_service_history-dict-legacy]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[get_service_history-sqlite-None]",
      "tests.integration.test_composite_ai_service_guards::test_legacy_ai_service_shortcut_preserved[get_service_history-sqlite-legacy]"
    ]
  }
]
```

All mutants independent against passing executable reference, relevant packet assertions only. No survivors/errors/skips; scratch auto-cleaned. Custom x-service aliases only; stock c aliases and catalog/financial AI tools remain later T050 work.
