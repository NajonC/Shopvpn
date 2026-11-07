# T050ab reference and mutation evidence

Source hashes:
```json
{
  "handlers_user.py": "611ce8a3ddab0d2298f0777187c6bf688958eaa2cce22fbabc2b3bf352182c90",
  "tests/integration/test_composite_telegram_transfer_confirm_guards.py": "cfbf7311b820875df3ea54c3eb68007ae304c7227ced944257158aa0058a5921",
  "tests/characterization/test_callbacks_fsm.py": "b9c63f3386ab154a9082415edcfdbdd61dc7fb895d1e91b5fd1401fe4edd1817"
}
```

Results:
```json
[
  {
    "name": "reference",
    "disposition": "passed",
    "cases": 35,
    "failed_test_ids": []
  },
  {
    "name": "omit_guard",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_transfer_confirm_refused[dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_transfer_confirm_refused[sqlite]"
    ]
  },
  {
    "name": "wrong_kind",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_transfer_confirm_refused[dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_transfer_confirm_refused[sqlite]"
    ]
  },
  {
    "name": "reject_missing",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_sibling_allows_transfer_confirm[dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_sibling_allows_transfer_confirm[sqlite]"
    ]
  },
  {
    "name": "reject_legacy",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-legacy-sqlite]"
    ]
  },
  {
    "name": "no_reason",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_transfer_confirm_refused[dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_transfer_confirm_refused[sqlite]"
    ]
  },
  {
    "name": "leak_reason",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_transfer_confirm_refused[dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_transfer_confirm_refused[sqlite]"
    ]
  },
  {
    "name": "transfer_before_refusal",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_transfer_confirm_refused[dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_transfer_confirm_refused[sqlite]"
    ]
  },
  {
    "name": "history_before_refusal",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_transfer_confirm_refused[dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_transfer_confirm_refused[sqlite]"
    ]
  },
  {
    "name": "prompt_before_refusal",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_transfer_confirm_refused[dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_transfer_confirm_refused[sqlite]"
    ]
  },
  {
    "name": "provider_before_refusal",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_transfer_confirm_refused[dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_transfer_confirm_refused[sqlite]"
    ]
  },
  {
    "name": "notification_before_refusal",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_transfer_confirm_refused[dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_transfer_confirm_refused[sqlite]"
    ]
  },
  {
    "name": "list_before_refusal",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_transfer_confirm_refused[dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_transfer_confirm_refused[sqlite]"
    ]
  },
  {
    "name": "omit_transfer",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_sibling_allows_transfer_confirm[dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_sibling_allows_transfer_confirm[sqlite]"
    ]
  },
  {
    "name": "wrong_target",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_sibling_allows_transfer_confirm[dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_sibling_allows_transfer_confirm[sqlite]"
    ]
  },
  {
    "name": "wrong_service",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_sibling_allows_transfer_confirm[dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_sibling_allows_transfer_confirm[sqlite]"
    ]
  },
  {
    "name": "wrong_owner",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_sibling_allows_transfer_confirm[dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_sibling_allows_transfer_confirm[sqlite]"
    ]
  },
  {
    "name": "wrong_history_type",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_sibling_allows_transfer_confirm[dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_sibling_allows_transfer_confirm[sqlite]"
    ]
  },
  {
    "name": "wrong_history_detail",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_sibling_allows_transfer_confirm[dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_sibling_allows_transfer_confirm[sqlite]"
    ]
  },
  {
    "name": "sibling_history",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_sibling_allows_transfer_confirm[dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_sibling_allows_transfer_confirm[sqlite]"
    ]
  },
  {
    "name": "erase_history",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_sibling_allows_transfer_confirm[dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_sibling_allows_transfer_confirm[sqlite]"
    ]
  },
  {
    "name": "wrong_alert",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_sibling_allows_transfer_confirm[dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_sibling_allows_transfer_confirm[sqlite]"
    ]
  },
  {
    "name": "wrong_notification_target",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_sibling_allows_transfer_confirm[dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_sibling_allows_transfer_confirm[sqlite]"
    ]
  },
  {
    "name": "wrong_notification_label",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-legacy-sqlite]"
    ]
  },
  {
    "name": "omit_notification",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_sibling_allows_transfer_confirm[dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_sibling_allows_transfer_confirm[sqlite]"
    ]
  },
  {
    "name": "omit_list",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-False-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[False-True-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-False-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-None-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-None-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-legacy-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_legacy_transfer_confirm_exact[True-True-legacy-sqlite]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_sibling_allows_transfer_confirm[dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_sibling_allows_transfer_confirm[sqlite]"
    ]
  },
  {
    "name": "omit_feature_gate",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_transfer_confirm_restrictions[off-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_transfer_confirm_restrictions[off-sqlite]"
    ]
  },
  {
    "name": "omit_test_gate",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_transfer_confirm_restrictions[test-dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_transfer_confirm_restrictions[test-sqlite]"
    ]
  },
  {
    "name": "scan_sibling",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_sibling_allows_transfer_confirm[dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_composite_sibling_allows_transfer_confirm[sqlite]"
    ]
  },
  {
    "name": "wrong_requester",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_foreign_transfer_confirm_opaque[dict]",
      "tests.integration.test_composite_telegram_transfer_confirm_guards::test_foreign_transfer_confirm_opaque[sqlite]"
    ]
  }
]
```

Independent valid mutations, relevant assertion failures only. No survivors/errors/skips. Scratch auto-cleaned. Reference checks selected owned service before transfer confirmation ownership/history/notification effects; real SQL and legacy controls preserved. No production implementation claim.
