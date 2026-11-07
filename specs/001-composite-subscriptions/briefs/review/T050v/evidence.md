# T050v reference and mutation evidence

Source hashes:
```json
{
  "handlers_user.py": "611ce8a3ddab0d2298f0777187c6bf688958eaa2cce22fbabc2b3bf352182c90",
  "tests/integration/test_composite_telegram_custom_selection_guards.py": "f4d6e181b96731bc5d201e4497a1c00f2a387e9ee76fdbc4314e59b7ecf11de5",
  "tests/characterization/test_buy_start.py": "d199331dc49248a6fe63550970db5d6d8527ca7189ad1d58f08b775b9b25d696",
  "tests/characterization/test_callbacks_fsm.py": "b9c63f3386ab154a9082415edcfdbdd61dc7fb895d1e91b5fd1401fe4edd1817"
}
```

Results:
```json
[
  {
    "name": "reference",
    "disposition": "passed",
    "cases": 66,
    "failed_test_ids": []
  },
  {
    "name": "discovery_omit_guard",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_discovery_refused[singleton-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_discovery_refused[singleton-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_discovery_refused[multiple-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_discovery_refused[multiple-sqlite]"
    ]
  },
  {
    "name": "discovery_wrong_kind",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_discovery_refused[singleton-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_discovery_refused[singleton-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_discovery_refused[multiple-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_discovery_refused[multiple-sqlite]"
    ]
  },
  {
    "name": "discovery_reject_missing",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[singleton-None-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[singleton-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[multiple-None-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[multiple-None-sqlite]"
    ]
  },
  {
    "name": "discovery_reject_legacy",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[singleton-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[singleton-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[multiple-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[multiple-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_isolation_inactive_composite_does_not_affect_discovery[dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_isolation_inactive_composite_does_not_affect_discovery[sqlite]"
    ]
  },
  {
    "name": "discovery_no_reason",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_discovery_refused[singleton-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_discovery_refused[singleton-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_discovery_refused[multiple-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_discovery_refused[multiple-sqlite]"
    ]
  },
  {
    "name": "discovery_delete_before_refusal",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_discovery_refused[singleton-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_discovery_refused[singleton-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_discovery_refused[multiple-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_discovery_refused[multiple-sqlite]"
    ]
  },
  {
    "name": "discovery_state_before_refusal",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_discovery_refused[singleton-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_discovery_refused[singleton-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_discovery_refused[multiple-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_discovery_refused[multiple-sqlite]"
    ]
  },
  {
    "name": "discovery_data_before_refusal",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_discovery_refused[singleton-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_discovery_refused[singleton-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_discovery_refused[multiple-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_discovery_refused[multiple-sqlite]"
    ]
  },
  {
    "name": "discovery_write_before_refusal",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_discovery_refused[singleton-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_discovery_refused[singleton-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_discovery_refused[multiple-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_discovery_refused[multiple-sqlite]"
    ]
  },
  {
    "name": "discovery_prompt_before_refusal",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_discovery_refused[singleton-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_discovery_refused[singleton-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_discovery_refused[multiple-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_discovery_refused[multiple-sqlite]"
    ]
  },
  {
    "name": "discovery_callback_before_refusal",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_discovery_refused[singleton-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_discovery_refused[singleton-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_discovery_refused[multiple-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_discovery_refused[multiple-sqlite]"
    ]
  },
  {
    "name": "pick_omit_guard",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_pick_refused[alpha-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_pick_refused[alpha-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_pick_refused[beta-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_pick_refused[beta-sqlite]"
    ]
  },
  {
    "name": "pick_wrong_kind",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_pick_refused[alpha-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_pick_refused[alpha-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_pick_refused[beta-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_pick_refused[beta-sqlite]"
    ]
  },
  {
    "name": "pick_reject_missing",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[alpha-None-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[alpha-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[beta-None-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[beta-None-sqlite]"
    ]
  },
  {
    "name": "pick_reject_legacy",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[alpha-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[alpha-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[beta-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[beta-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_isolation_unselected_composite_does_not_affect_pick[dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_isolation_unselected_composite_does_not_affect_pick[sqlite]"
    ]
  },
  {
    "name": "pick_no_reason",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_pick_refused[alpha-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_pick_refused[alpha-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_pick_refused[beta-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_pick_refused[beta-sqlite]"
    ]
  },
  {
    "name": "pick_delete_before_refusal",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_pick_refused[alpha-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_pick_refused[alpha-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_pick_refused[beta-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_pick_refused[beta-sqlite]"
    ]
  },
  {
    "name": "pick_state_before_refusal",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_pick_refused[alpha-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_pick_refused[alpha-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_pick_refused[beta-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_pick_refused[beta-sqlite]"
    ]
  },
  {
    "name": "pick_data_before_refusal",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_pick_refused[alpha-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_pick_refused[alpha-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_pick_refused[beta-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_pick_refused[beta-sqlite]"
    ]
  },
  {
    "name": "pick_write_before_refusal",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_pick_refused[alpha-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_pick_refused[alpha-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_pick_refused[beta-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_pick_refused[beta-sqlite]"
    ]
  },
  {
    "name": "pick_prompt_before_refusal",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_pick_refused[alpha-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_pick_refused[alpha-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_pick_refused[beta-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_pick_refused[beta-sqlite]"
    ]
  },
  {
    "name": "pick_callback_before_refusal",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_pick_refused[alpha-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_pick_refused[alpha-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_pick_refused[beta-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_composite_custom_pick_refused[beta-sqlite]"
    ]
  },
  {
    "name": "discovery_scan_inactive",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_selection_guards::test_isolation_inactive_composite_does_not_affect_discovery[dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_isolation_inactive_composite_does_not_affect_discovery[sqlite]"
    ]
  },
  {
    "name": "pick_scan_siblings",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_selection_guards::test_isolation_unselected_composite_does_not_affect_pick[dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_isolation_unselected_composite_does_not_affect_pick[sqlite]"
    ]
  },
  {
    "name": "pick_unavailable_alert",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_selection_guards::test_unavailable_selected_product_control[missing-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_unavailable_selected_product_control[missing-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_unavailable_selected_product_control[inactive-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_unavailable_selected_product_control[inactive-sqlite]"
    ]
  },
  {
    "name": "discovery_omit_delete",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[singleton-None-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[singleton-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[singleton-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[singleton-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[multiple-None-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[multiple-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[multiple-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[multiple-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_isolation_inactive_composite_does_not_affect_discovery[dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_isolation_inactive_composite_does_not_affect_discovery[sqlite]"
    ]
  },
  {
    "name": "pick_omit_delete",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[alpha-None-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[alpha-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[alpha-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[alpha-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[beta-None-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[beta-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[beta-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[beta-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_isolation_unselected_composite_does_not_affect_pick[dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_isolation_unselected_composite_does_not_affect_pick[sqlite]"
    ]
  },
  {
    "name": "wrong_product",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[singleton-None-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[singleton-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[singleton-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[singleton-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[alpha-None-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[alpha-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[alpha-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[alpha-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[beta-None-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[beta-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[beta-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[beta-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_isolation_inactive_composite_does_not_affect_discovery[dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_isolation_inactive_composite_does_not_affect_discovery[sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_isolation_unselected_composite_does_not_affect_pick[dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_isolation_unselected_composite_does_not_affect_pick[sqlite]"
    ]
  },
  {
    "name": "wrong_server",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[singleton-None-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[singleton-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[singleton-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[singleton-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[alpha-None-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[alpha-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[alpha-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[alpha-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[beta-None-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[beta-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[beta-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[beta-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_isolation_inactive_composite_does_not_affect_discovery[dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_isolation_inactive_composite_does_not_affect_discovery[sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_isolation_unselected_composite_does_not_affect_pick[dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_isolation_unselected_composite_does_not_affect_pick[sqlite]"
    ]
  },
  {
    "name": "clear_sentinel",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[singleton-None-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[singleton-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[singleton-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[singleton-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[alpha-None-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[alpha-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[alpha-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[alpha-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[beta-None-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[beta-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[beta-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[beta-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_isolation_inactive_composite_does_not_affect_discovery[dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_isolation_inactive_composite_does_not_affect_discovery[sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_isolation_unselected_composite_does_not_affect_pick[dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_isolation_unselected_composite_does_not_affect_pick[sqlite]"
    ]
  },
  {
    "name": "wrong_username_state",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[singleton-None-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[singleton-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[singleton-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[singleton-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[alpha-None-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[alpha-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[alpha-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[alpha-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[beta-None-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[beta-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[beta-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[beta-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_isolation_inactive_composite_does_not_affect_discovery[dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_isolation_inactive_composite_does_not_affect_discovery[sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_isolation_unselected_composite_does_not_affect_pick[dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_isolation_unselected_composite_does_not_affect_pick[sqlite]"
    ]
  },
  {
    "name": "wrong_username_text",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[singleton-None-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[singleton-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[singleton-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[singleton-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[alpha-None-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[alpha-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[alpha-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[alpha-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[beta-None-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[beta-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[beta-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[beta-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_isolation_inactive_composite_does_not_affect_discovery[dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_isolation_inactive_composite_does_not_affect_discovery[sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_isolation_unselected_composite_does_not_affect_pick[dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_isolation_unselected_composite_does_not_affect_pick[sqlite]"
    ]
  },
  {
    "name": "wrong_username_keyboard",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[singleton-None-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[singleton-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[singleton-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[singleton-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[alpha-None-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[alpha-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[alpha-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[alpha-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[beta-None-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[beta-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[beta-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_pick_success[beta-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_isolation_inactive_composite_does_not_affect_discovery[dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_isolation_inactive_composite_does_not_affect_discovery[sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_isolation_unselected_composite_does_not_affect_pick[dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_isolation_unselected_composite_does_not_affect_pick[sqlite]"
    ]
  },
  {
    "name": "wrong_catalog_state",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[multiple-None-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[multiple-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[multiple-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[multiple-legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_catalog_text",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[multiple-None-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[multiple-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[multiple-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[multiple-legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_catalog_keyboard",
    "disposition": "killed",
    "cases": 32,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[multiple-None-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[multiple-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[multiple-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_selection_guards::test_legacy_custom_discovery_success[multiple-legacy-sqlite]"
    ]
  }
]
```

Independent valid mutations, relevant assertion failures only. No survivors/errors/skips. Scratch auto-cleaned. Reference preflights active custom-plan discovery and selected product before deletion/FSM/UI; real SQL and legacy helpers retained. No production implementation claim.
