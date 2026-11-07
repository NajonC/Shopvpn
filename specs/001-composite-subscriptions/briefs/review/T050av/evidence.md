# T050av reference and mutation evidence

Source hashes:
```json
{
  "handlers_user.py": "611ce8a3ddab0d2298f0777187c6bf688958eaa2cce22fbabc2b3bf352182c90",
  "blupal_payment.py": "193a324a443dc38ed19622a4bf02bc049eaf51ab965b2ffcb9caeb100c7a6332",
  "tests/integration/test_composite_telegram_blupal_status_guards.py": "ffd60b10035e6148e75a79d3da6beea792c92b89a9a24929094ba73999e4440c",
  "tests/characterization/test_callbacks_fsm.py": "b9c63f3386ab154a9082415edcfdbdd61dc7fb895d1e91b5fd1401fe4edd1817"
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
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[pending-order-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[pending-order-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[pending-product-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[pending-product-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[expired-order-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[expired-order-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[expired-product-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[expired-product-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[paid_prior-order-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[paid_prior-order-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[paid_prior-product-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[paid_prior-product-sqlite]"
    ]
  },
  {
    "name": "omit_order_guard",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[pending-order-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[pending-order-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[expired-order-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[expired-order-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[paid_prior-order-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[paid_prior-order-sqlite]"
    ]
  },
  {
    "name": "omit_product_guard",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[pending-product-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[pending-product-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[expired-product-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[expired-product-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[paid_prior-product-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[paid_prior-product-sqlite]"
    ]
  },
  {
    "name": "both_required",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[pending-order-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[pending-order-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[pending-product-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[pending-product-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[expired-order-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[expired-order-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[expired-product-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[expired-product-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[paid_prior-order-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[paid_prior-order-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[paid_prior-product-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[paid_prior-product-sqlite]"
    ]
  },
  {
    "name": "wrong_ref",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[pending-order-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[pending-order-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[pending-product-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[pending-product-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[expired-order-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[expired-order-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[expired-product-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[expired-product-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[paid_prior-order-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[paid_prior-order-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[paid_prior-product-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[paid_prior-product-sqlite]"
    ]
  },
  {
    "name": "no_reason",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[pending-order-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[pending-order-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[pending-product-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[pending-product-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[expired-order-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[expired-order-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[expired-product-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[expired-product-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[paid_prior-order-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[paid_prior-order-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[paid_prior-product-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[paid_prior-product-sqlite]"
    ]
  },
  {
    "name": "early_ack",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[pending-order-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[pending-order-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[pending-product-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[pending-product-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[expired-order-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[expired-order-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[expired-product-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[expired-product-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[paid_prior-order-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[paid_prior-order-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[paid_prior-product-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[paid_prior-product-sqlite]"
    ]
  },
  {
    "name": "early_verify",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[pending-order-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[pending-order-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[pending-product-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[pending-product-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[expired-order-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[expired-order-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[expired-product-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[expired-product-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[paid_prior-order-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[paid_prior-order-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[paid_prior-product-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[paid_prior-product-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[pending-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[pending-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[pending-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[pending-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[expired-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[expired-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[expired-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[expired-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[cancelled-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[cancelled-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[cancelled-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[cancelled-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[remote_error-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[remote_error-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[remote_error-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[remote_error-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[race_lost-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[race_lost-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[race_lost-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[race_lost-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_prior-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_prior-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_prior-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_prior-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_missing_server-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_missing_server-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_missing_server-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_missing_server-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_wallet_topup_status_retains_exact_credit[dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_wallet_topup_status_retains_exact_credit[sqlite]"
    ]
  },
  {
    "name": "no_ownership",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_blupal_status_guards::test_status_opaque_refusals[foreign-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_status_opaque_refusals[foreign-sqlite]"
    ]
  },
  {
    "name": "wrong_lookup",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[pending-order-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[pending-order-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[pending-product-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[pending-product-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[expired-order-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[expired-order-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[expired-product-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[expired-product-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[paid_prior-order-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[paid_prior-order-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[paid_prior-product-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_composite_custom_status_refused[paid_prior-product-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[pending-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[pending-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[pending-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[pending-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[expired-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[expired-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[expired-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[expired-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[cancelled-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[cancelled-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[cancelled-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[cancelled-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[completed-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[completed-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[completed-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[completed-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[remote_error-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[remote_error-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[remote_error-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[remote_error-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[race_lost-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[race_lost-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[race_lost-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[race_lost-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_prior-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_prior-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_prior-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_prior-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_missing_server-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_missing_server-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_missing_server-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_missing_server-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_wallet_topup_status_retains_exact_credit[dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_wallet_topup_status_retains_exact_credit[sqlite]"
    ]
  },
  {
    "name": "wrong_helper_input",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[pending-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[pending-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[pending-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[pending-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[expired-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[expired-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[expired-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[expired-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[cancelled-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[cancelled-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[cancelled-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[cancelled-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[completed-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[completed-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[completed-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[completed-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[remote_error-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[remote_error-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[remote_error-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[remote_error-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[race_lost-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[race_lost-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[race_lost-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[race_lost-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_prior-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_prior-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_prior-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_prior-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_missing_server-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_missing_server-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_missing_server-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_missing_server-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_wallet_topup_status_retains_exact_credit[dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_wallet_topup_status_retains_exact_credit[sqlite]"
    ]
  },
  {
    "name": "wrong_pending",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[pending-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[pending-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[pending-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[pending-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[completed-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[completed-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[completed-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[completed-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[race_lost-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[race_lost-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[race_lost-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[race_lost-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_prior-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_prior-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_prior-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_prior-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_missing_server-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_missing_server-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_missing_server-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_missing_server-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_wallet_topup_status_retains_exact_credit[dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_wallet_topup_status_retains_exact_credit[sqlite]"
    ]
  },
  {
    "name": "wrong_expired",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[cancelled-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[cancelled-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[cancelled-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[cancelled-legacy-sqlite]"
    ]
  },
  {
    "name": "no_finalizer",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_prior-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_prior-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_prior-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_prior-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_missing_server-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_missing_server-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_missing_server-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_missing_server-legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_finalizer_ref",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_prior-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_prior-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_prior-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_prior-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_missing_server-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_missing_server-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_missing_server-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_missing_server-legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_topup_ref",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_blupal_status_guards::test_wallet_topup_status_retains_exact_credit[dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_wallet_topup_status_retains_exact_credit[sqlite]"
    ]
  },
  {
    "name": "legacy_overstrict",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[pending-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[pending-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[pending-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[pending-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[expired-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[expired-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[expired-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[expired-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[cancelled-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[cancelled-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[cancelled-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[cancelled-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[completed-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[completed-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[completed-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[completed-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[remote_error-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[remote_error-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[remote_error-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[remote_error-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[race_lost-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[race_lost-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[race_lost-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[race_lost-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_prior-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_prior-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_prior-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_prior-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_missing_server-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_missing_server-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_missing_server-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_missing_server-legacy-sqlite]"
    ]
  },
  {
    "name": "sibling_overstrict",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[pending-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[pending-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[pending-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[pending-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[expired-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[expired-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[expired-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[expired-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[cancelled-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[cancelled-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[cancelled-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[cancelled-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[completed-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[completed-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[completed-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[completed-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[remote_error-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[remote_error-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[remote_error-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[remote_error-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[race_lost-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[race_lost-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[race_lost-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[race_lost-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_prior-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_prior-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_prior-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_prior-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_missing_server-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_missing_server-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_missing_server-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_missing_server-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_wallet_topup_status_retains_exact_credit[dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_wallet_topup_status_retains_exact_credit[sqlite]"
    ]
  },
  {
    "name": "ignore_lost_invoice_claim",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[race_lost-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[race_lost-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[race_lost-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[race_lost-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_prior-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_prior-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_prior-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_prior-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_missing_server-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_missing_server-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_missing_server-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_missing_server-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_wallet_topup_status_retains_exact_credit[dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_wallet_topup_status_retains_exact_credit[sqlite]"
    ]
  },
  {
    "name": "claim_wrong_invoice",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[race_lost-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[race_lost-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[race_lost-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[race_lost-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_prior-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_prior-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_prior-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_prior-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_missing_server-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_missing_server-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_missing_server-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_missing_server-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_wallet_topup_status_retains_exact_credit[dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_wallet_topup_status_retains_exact_credit[sqlite]"
    ]
  },
  {
    "name": "skip_completed_shortcut",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[completed-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[completed-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[completed-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[completed-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[race_lost-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[race_lost-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[race_lost-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[race_lost-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_prior-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_prior-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_prior-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_prior-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_missing_server-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_missing_server-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_missing_server-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[paid_missing_server-legacy-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_wallet_topup_status_retains_exact_credit[dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_wallet_topup_status_retains_exact_credit[sqlite]"
    ]
  },
  {
    "name": "force_paid_for_pending",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[pending-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[pending-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[pending-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[pending-legacy-sqlite]"
    ]
  },
  {
    "name": "omit_remote_error_reason",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[remote_error-None-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[remote_error-None-sqlite]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[remote_error-legacy-dict]",
      "tests.integration.test_composite_telegram_blupal_status_guards::test_legacy_status_exact[remote_error-legacy-sqlite]"
    ]
  }
]
```

Independent valid mutations, relevant assertion failures only. No survivors/errors/skips. Scratch auto-cleaned. Reference checks the owned invoice order/custom-product identity before remote verification and shared status effects; real SQL invoice claims and legacy status/opacity controls preserved. No production implementation claim.
