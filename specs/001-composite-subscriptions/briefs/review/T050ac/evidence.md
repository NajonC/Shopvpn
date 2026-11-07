# T050ac reference and mutation evidence

Source hashes:
```json
{
  "handlers_user.py": "611ce8a3ddab0d2298f0777187c6bf688958eaa2cce22fbabc2b3bf352182c90",
  "tests/integration/test_composite_telegram_custom_username_guards.py": "45906232b01f8fb30fadfae416928f2893d2223e1bb281e182c38d79c02aacbb",
  "tests/characterization/test_callbacks_fsm.py": "b9c63f3386ab154a9082415edcfdbdd61dc7fb895d1e91b5fd1401fe4edd1817"
}
```

Results:
```json
[
  {
    "name": "reference",
    "disposition": "passed",
    "cases": 49,
    "failed_test_ids": []
  },
  {
    "name": "omit_guard",
    "disposition": "killed",
    "cases": 40,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_username_guards::test_composite_custom_username_refused[dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_composite_custom_username_refused[sqlite]"
    ]
  },
  {
    "name": "wrong_kind",
    "disposition": "killed",
    "cases": 40,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_username_guards::test_composite_custom_username_refused[dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_composite_custom_username_refused[sqlite]"
    ]
  },
  {
    "name": "reject_missing",
    "disposition": "killed",
    "cases": 40,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc--None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc--None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc-shop-None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc-shop-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa--None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa--None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa-shop-None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa-shop-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  --None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  --None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  -shop-None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  -shop-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_composite_sibling_allows_custom_username[dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_composite_sibling_allows_custom_username[sqlite]"
    ]
  },
  {
    "name": "reject_legacy",
    "disposition": "killed",
    "cases": 40,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc--legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc--legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc-shop-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc-shop-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa--legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa--legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa-shop-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa-shop-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  --legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  --legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  -shop-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  -shop-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_invalid[aa-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_invalid[aa-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_invalid[aaaaaaaaaaaaaaaaaaaaa-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_invalid[aaaaaaaaaaaaaaaaaaaaa-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_invalid[bad name-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_invalid[bad name-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_invalid[\\u0646\\u0627\\u0645-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_invalid[\\u0646\\u0627\\u0645-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_taken[-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_taken[-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_taken[shop-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_taken[shop-sqlite]"
    ]
  },
  {
    "name": "no_reason",
    "disposition": "killed",
    "cases": 40,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_username_guards::test_composite_custom_username_refused[dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_composite_custom_username_refused[sqlite]"
    ]
  },
  {
    "name": "leak_reason",
    "disposition": "killed",
    "cases": 40,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_username_guards::test_composite_custom_username_refused[dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_composite_custom_username_refused[sqlite]"
    ]
  },
  {
    "name": "state_before_refusal",
    "disposition": "killed",
    "cases": 40,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_username_guards::test_composite_custom_username_refused[dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_composite_custom_username_refused[sqlite]"
    ]
  },
  {
    "name": "data_before_refusal",
    "disposition": "killed",
    "cases": 40,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_username_guards::test_composite_custom_username_refused[dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_composite_custom_username_refused[sqlite]"
    ]
  },
  {
    "name": "clear_before_refusal",
    "disposition": "killed",
    "cases": 40,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_username_guards::test_composite_custom_username_refused[dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_composite_custom_username_refused[sqlite]"
    ]
  },
  {
    "name": "prompt_before_refusal",
    "disposition": "killed",
    "cases": 40,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_username_guards::test_composite_custom_username_refused[dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_composite_custom_username_refused[sqlite]"
    ]
  },
  {
    "name": "db_before_refusal",
    "disposition": "killed",
    "cases": 40,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_username_guards::test_composite_custom_username_refused[dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_composite_custom_username_refused[sqlite]"
    ]
  },
  {
    "name": "provider_before_refusal",
    "disposition": "killed",
    "cases": 40,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_username_guards::test_composite_custom_username_refused[dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_composite_custom_username_refused[sqlite]"
    ]
  },
  {
    "name": "loose_name_bounds",
    "disposition": "killed",
    "cases": 40,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_invalid[aa-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_invalid[aa-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_invalid[aaaaaaaaaaaaaaaaaaaaa-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_invalid[aaaaaaaaaaaaaaaaaaaaa-sqlite]"
    ]
  },
  {
    "name": "strict_name_bounds",
    "disposition": "killed",
    "cases": 40,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc--None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc--None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc--legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc--legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc-shop-None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc-shop-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc-shop-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc-shop-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa--None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa--None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa--legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa--legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa-shop-None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa-shop-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa-shop-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa-shop-legacy-sqlite]"
    ]
  },
  {
    "name": "allow_space_unicode",
    "disposition": "killed",
    "cases": 40,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_invalid[bad name-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_invalid[bad name-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_invalid[\\u0646\\u0627\\u0645-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_invalid[\\u0646\\u0627\\u0645-sqlite]"
    ]
  },
  {
    "name": "strict_whitespace",
    "disposition": "killed",
    "cases": 40,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  --None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  --None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  --legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  --legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  -shop-None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  -shop-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  -shop-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  -shop-legacy-sqlite]"
    ]
  },
  {
    "name": "omit_prefix",
    "disposition": "killed",
    "cases": 40,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc-shop-None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc-shop-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc-shop-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc-shop-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa-shop-None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa-shop-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa-shop-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa-shop-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  -shop-None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  -shop-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  -shop-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  -shop-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_taken[shop-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_taken[shop-sqlite]"
    ]
  },
  {
    "name": "wrong_separator",
    "disposition": "killed",
    "cases": 40,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc-shop-None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc-shop-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc-shop-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc-shop-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa-shop-None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa-shop-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa-shop-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa-shop-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  -shop-None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  -shop-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  -shop-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  -shop-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_taken[shop-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_taken[shop-sqlite]"
    ]
  },
  {
    "name": "omit_collision",
    "disposition": "killed",
    "cases": 40,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_taken[-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_taken[-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_taken[shop-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_taken[shop-sqlite]"
    ]
  },
  {
    "name": "wrong_collision_identity",
    "disposition": "killed",
    "cases": 40,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_taken[-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_taken[-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_taken[shop-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_taken[shop-sqlite]"
    ]
  },
  {
    "name": "wrong_saved_name",
    "disposition": "killed",
    "cases": 40,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc--None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc--None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc--legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc--legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc-shop-None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc-shop-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc-shop-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc-shop-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa--None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa--None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa--legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa--legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa-shop-None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa-shop-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa-shop-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa-shop-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  --None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  --None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  --legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  --legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  -shop-None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  -shop-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  -shop-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  -shop-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_composite_sibling_allows_custom_username[dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_composite_sibling_allows_custom_username[sqlite]"
    ]
  },
  {
    "name": "wrong_state",
    "disposition": "killed",
    "cases": 40,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc--None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc--None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc--legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc--legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc-shop-None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc-shop-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc-shop-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc-shop-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa--None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa--None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa--legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa--legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa-shop-None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa-shop-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa-shop-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa-shop-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  --None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  --None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  --legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  --legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  -shop-None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  -shop-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  -shop-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  -shop-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_composite_sibling_allows_custom_username[dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_composite_sibling_allows_custom_username[sqlite]"
    ]
  },
  {
    "name": "wrong_price",
    "disposition": "killed",
    "cases": 40,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc--None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc--None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc--legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc--legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc-shop-None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc-shop-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc-shop-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc-shop-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa--None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa--None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa--legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa--legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa-shop-None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa-shop-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa-shop-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa-shop-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  --None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  --None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  --legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  --legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  -shop-None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  -shop-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  -shop-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  -shop-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_composite_sibling_allows_custom_username[dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_composite_sibling_allows_custom_username[sqlite]"
    ]
  },
  {
    "name": "wrong_min",
    "disposition": "killed",
    "cases": 40,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc--None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc--None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc--legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc--legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc-shop-None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc-shop-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc-shop-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc-shop-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa--None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa--None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa--legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa--legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa-shop-None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa-shop-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa-shop-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa-shop-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  --None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  --None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  --legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  --legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  -shop-None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  -shop-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  -shop-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  -shop-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_composite_sibling_allows_custom_username[dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_composite_sibling_allows_custom_username[sqlite]"
    ]
  },
  {
    "name": "wrong_max",
    "disposition": "killed",
    "cases": 40,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc--None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc--None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc--legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc--legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc-shop-None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc-shop-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc-shop-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc-shop-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa--None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa--None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa--legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa--legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa-shop-None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa-shop-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa-shop-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa-shop-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  --None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  --None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  --legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  --legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  -shop-None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  -shop-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  -shop-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  -shop-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_composite_sibling_allows_custom_username[dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_composite_sibling_allows_custom_username[sqlite]"
    ]
  },
  {
    "name": "wrong_duration",
    "disposition": "killed",
    "cases": 40,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc--None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc--None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc--legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc--legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc-shop-None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc-shop-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc-shop-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc-shop-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa--None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa--None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa--legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa--legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa-shop-None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa-shop-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa-shop-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa-shop-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  --None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  --None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  --legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  --legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  -shop-None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  -shop-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  -shop-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  -shop-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_composite_sibling_allows_custom_username[dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_composite_sibling_allows_custom_username[sqlite]"
    ]
  },
  {
    "name": "wrong_keyboard",
    "disposition": "killed",
    "cases": 40,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc--None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc--None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc--legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc--legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc-shop-None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc-shop-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc-shop-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[abc-shop-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa--None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa--None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa--legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa--legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa-shop-None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa-shop-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa-shop-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[aaaaaaaaaaaaaaaaaaaa-shop-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  --None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  --None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  --legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  --legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  -shop-None-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  -shop-None-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  -shop-legacy-dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_legacy_custom_username_exact[  new_name  -shop-legacy-sqlite]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_composite_sibling_allows_custom_username[dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_composite_sibling_allows_custom_username[sqlite]"
    ]
  },
  {
    "name": "scan_sibling",
    "disposition": "killed",
    "cases": 40,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_custom_username_guards::test_composite_sibling_allows_custom_username[dict]",
      "tests.integration.test_composite_telegram_custom_username_guards::test_composite_sibling_allows_custom_username[sqlite]"
    ]
  }
]
```

Independent valid mutations, relevant assertion failures only. No survivors/errors/skips. Scratch auto-cleaned. Reference checks selected owned service before manual custom username selected-product/FSM/pricing effects; real SQL and legacy controls preserved. No production implementation claim.
