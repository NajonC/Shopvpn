# T050at reference and mutation evidence

Source hashes:
```json
{
  "handlers_user.py": "611ce8a3ddab0d2298f0777187c6bf688958eaa2cce22fbabc2b3bf352182c90",
  "tests/integration/test_composite_telegram_card_status_guards.py": "346f9d1b077984600dea4c8c9155587c651cfea75b315e94ca6c8aad2abb5483",
  "tests/characterization/test_callbacks_fsm.py": "b9c63f3386ab154a9082415edcfdbdd61dc7fb895d1e91b5fd1401fe4edd1817"
}
```

Results:
```json
[
  {
    "name": "reference",
    "disposition": "passed",
    "cases": 47,
    "failed_test_ids": []
  },
  {
    "name": "omit_guard",
    "disposition": "killed",
    "cases": 38,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-False-order-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-False-order-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-False-product-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-False-product-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-True-order-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-True-order-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-True-product-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-True-product-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[completed-False-order-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[completed-False-order-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[completed-False-product-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[completed-False-product-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[manual_review-False-order-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[manual_review-False-order-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[manual_review-False-product-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[manual_review-False-product-sqlite]"
    ]
  },
  {
    "name": "omit_order_guard",
    "disposition": "killed",
    "cases": 38,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-False-order-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-False-order-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-True-order-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-True-order-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[completed-False-order-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[completed-False-order-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[manual_review-False-order-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[manual_review-False-order-sqlite]"
    ]
  },
  {
    "name": "omit_product_guard",
    "disposition": "killed",
    "cases": 38,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-False-product-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-False-product-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-True-product-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-True-product-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[completed-False-product-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[completed-False-product-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[manual_review-False-product-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[manual_review-False-product-sqlite]"
    ]
  },
  {
    "name": "both_required",
    "disposition": "killed",
    "cases": 38,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-False-order-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-False-order-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-False-product-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-False-product-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-True-order-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-True-order-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-True-product-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-True-product-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[completed-False-order-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[completed-False-order-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[completed-False-product-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[completed-False-product-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[manual_review-False-order-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[manual_review-False-order-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[manual_review-False-product-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[manual_review-False-product-sqlite]"
    ]
  },
  {
    "name": "wrong_link",
    "disposition": "killed",
    "cases": 38,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-False-order-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-False-order-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-False-product-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-False-product-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-True-order-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-True-order-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-True-product-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-True-product-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[completed-False-order-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[completed-False-order-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[completed-False-product-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[completed-False-product-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[manual_review-False-order-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[manual_review-False-order-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[manual_review-False-product-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[manual_review-False-product-sqlite]"
    ]
  },
  {
    "name": "no_reason",
    "disposition": "killed",
    "cases": 38,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-False-order-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-False-order-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-False-product-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-False-product-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-True-order-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-True-order-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-True-product-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-True-product-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[completed-False-order-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[completed-False-order-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[completed-False-product-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[completed-False-product-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[manual_review-False-order-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[manual_review-False-order-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[manual_review-False-product-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[manual_review-False-product-sqlite]"
    ]
  },
  {
    "name": "early_expiry",
    "disposition": "killed",
    "cases": 38,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-False-order-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-False-order-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-False-product-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-False-product-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-True-order-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-True-order-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-True-product-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[pending-True-product-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[completed-False-order-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[completed-False-order-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[completed-False-product-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[completed-False-product-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[manual_review-False-order-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[manual_review-False-order-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[manual_review-False-product-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_composite_card_status_refused[manual_review-False-product-sqlite]"
    ]
  },
  {
    "name": "no_ownership",
    "disposition": "killed",
    "cases": 38,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_card_status_guards::test_card_status_opaque_refusals[foreign-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_card_status_opaque_refusals[foreign-sqlite]"
    ]
  },
  {
    "name": "no_expiry",
    "disposition": "killed",
    "cases": 38,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[pending-False-\\u23f3 \\u0647\\u0646\\u0648\\u0632 \\u067e\\u06cc\\u0627\\u0645\\u06a9 \\u0628\\u0627\\u0646\\u06a9 \\u0628\\u0631\\u0627\\u06cc \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062f\\u0631\\u06cc\\u0627\\u0641\\u062a \\u0646\\u0634\\u062f\\u0647. \\u06a9\\u0645\\u06cc \\u0635\\u0628\\u0631 \\u06a9\\u0646.-None-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[pending-False-\\u23f3 \\u0647\\u0646\\u0648\\u0632 \\u067e\\u06cc\\u0627\\u0645\\u06a9 \\u0628\\u0627\\u0646\\u06a9 \\u0628\\u0631\\u0627\\u06cc \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062f\\u0631\\u06cc\\u0627\\u0641\\u062a \\u0646\\u0634\\u062f\\u0647. \\u06a9\\u0645\\u06cc \\u0635\\u0628\\u0631 \\u06a9\\u0646.-None-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[pending-False-\\u23f3 \\u0647\\u0646\\u0648\\u0632 \\u067e\\u06cc\\u0627\\u0645\\u06a9 \\u0628\\u0627\\u0646\\u06a9 \\u0628\\u0631\\u0627\\u06cc \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062f\\u0631\\u06cc\\u0627\\u0641\\u062a \\u0646\\u0634\\u062f\\u0647. \\u06a9\\u0645\\u06cc \\u0635\\u0628\\u0631 \\u06a9\\u0646.-legacy-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[pending-False-\\u23f3 \\u0647\\u0646\\u0648\\u0632 \\u067e\\u06cc\\u0627\\u0645\\u06a9 \\u0628\\u0627\\u0646\\u06a9 \\u0628\\u0631\\u0627\\u06cc \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062f\\u0631\\u06cc\\u0627\\u0641\\u062a \\u0646\\u0634\\u062f\\u0647. \\u06a9\\u0645\\u06cc \\u0635\\u0628\\u0631 \\u06a9\\u0646.-legacy-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[pending-True-\\u23f3 \\u0645\\u0647\\u0644\\u062a \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062a\\u0645\\u0627\\u0645 \\u0634\\u062f\\u0647 \\u0648 \\u0628\\u0631\\u0627\\u06cc \\u0628\\u0631\\u0631\\u0633\\u06cc \\u062f\\u0633\\u062a\\u06cc \\u0628\\u0647 \\u0627\\u062f\\u0645\\u06cc\\u0646 \\u0627\\u0631\\u0633\\u0627\\u0644 \\u0634\\u062f.-None-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[pending-True-\\u23f3 \\u0645\\u0647\\u0644\\u062a \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062a\\u0645\\u0627\\u0645 \\u0634\\u062f\\u0647 \\u0648 \\u0628\\u0631\\u0627\\u06cc \\u0628\\u0631\\u0631\\u0633\\u06cc \\u062f\\u0633\\u062a\\u06cc \\u0628\\u0647 \\u0627\\u062f\\u0645\\u06cc\\u0646 \\u0627\\u0631\\u0633\\u0627\\u0644 \\u0634\\u062f.-None-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[pending-True-\\u23f3 \\u0645\\u0647\\u0644\\u062a \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062a\\u0645\\u0627\\u0645 \\u0634\\u062f\\u0647 \\u0648 \\u0628\\u0631\\u0627\\u06cc \\u0628\\u0631\\u0631\\u0633\\u06cc \\u062f\\u0633\\u062a\\u06cc \\u0628\\u0647 \\u0627\\u062f\\u0645\\u06cc\\u0646 \\u0627\\u0631\\u0633\\u0627\\u0644 \\u0634\\u062f.-legacy-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[pending-True-\\u23f3 \\u0645\\u0647\\u0644\\u062a \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062a\\u0645\\u0627\\u0645 \\u0634\\u062f\\u0647 \\u0648 \\u0628\\u0631\\u0627\\u06cc \\u0628\\u0631\\u0631\\u0633\\u06cc \\u062f\\u0633\\u062a\\u06cc \\u0628\\u0647 \\u0627\\u062f\\u0645\\u06cc\\u0646 \\u0627\\u0631\\u0633\\u0627\\u0644 \\u0634\\u062f.-legacy-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[completed-True-\\u2705 \\u0627\\u06cc\\u0646 \\u067e\\u0631\\u062f\\u0627\\u062e\\u062a \\u0642\\u0628\\u0644\\u0627\\u064b \\u062a\\u0627\\u06cc\\u06cc\\u062f \\u0648 \\u062a\\u062d\\u0648\\u06cc\\u0644 \\u062f\\u0627\\u062f\\u0647 \\u0634\\u062f\\u0647 \\u0627\\u0633\\u062a.-None-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[completed-True-\\u2705 \\u0627\\u06cc\\u0646 \\u067e\\u0631\\u062f\\u0627\\u062e\\u062a \\u0642\\u0628\\u0644\\u0627\\u064b \\u062a\\u0627\\u06cc\\u06cc\\u062f \\u0648 \\u062a\\u062d\\u0648\\u06cc\\u0644 \\u062f\\u0627\\u062f\\u0647 \\u0634\\u062f\\u0647 \\u0627\\u0633\\u062a.-None-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[completed-True-\\u2705 \\u0627\\u06cc\\u0646 \\u067e\\u0631\\u062f\\u0627\\u062e\\u062a \\u0642\\u0628\\u0644\\u0627\\u064b \\u062a\\u0627\\u06cc\\u06cc\\u062f \\u0648 \\u062a\\u062d\\u0648\\u06cc\\u0644 \\u062f\\u0627\\u062f\\u0647 \\u0634\\u062f\\u0647 \\u0627\\u0633\\u062a.-legacy-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[completed-True-\\u2705 \\u0627\\u06cc\\u0646 \\u067e\\u0631\\u062f\\u0627\\u062e\\u062a \\u0642\\u0628\\u0644\\u0627\\u064b \\u062a\\u0627\\u06cc\\u06cc\\u062f \\u0648 \\u062a\\u062d\\u0648\\u06cc\\u0644 \\u062f\\u0627\\u062f\\u0647 \\u0634\\u062f\\u0647 \\u0627\\u0633\\u062a.-legacy-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[manual_review-True-\\u23f3 \\u0645\\u0647\\u0644\\u062a \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062a\\u0645\\u0627\\u0645 \\u0634\\u062f\\u0647 \\u0648 \\u0628\\u0631\\u0627\\u06cc \\u0628\\u0631\\u0631\\u0633\\u06cc \\u062f\\u0633\\u062a\\u06cc \\u0628\\u0647 \\u0627\\u062f\\u0645\\u06cc\\u0646 \\u0627\\u0631\\u0633\\u0627\\u0644 \\u0634\\u062f.-None-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[manual_review-True-\\u23f3 \\u0645\\u0647\\u0644\\u062a \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062a\\u0645\\u0627\\u0645 \\u0634\\u062f\\u0647 \\u0648 \\u0628\\u0631\\u0627\\u06cc \\u0628\\u0631\\u0631\\u0633\\u06cc \\u062f\\u0633\\u062a\\u06cc \\u0628\\u0647 \\u0627\\u062f\\u0645\\u06cc\\u0646 \\u0627\\u0631\\u0633\\u0627\\u0644 \\u0634\\u062f.-None-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[manual_review-True-\\u23f3 \\u0645\\u0647\\u0644\\u062a \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062a\\u0645\\u0627\\u0645 \\u0634\\u062f\\u0647 \\u0648 \\u0628\\u0631\\u0627\\u06cc \\u0628\\u0631\\u0631\\u0633\\u06cc \\u062f\\u0633\\u062a\\u06cc \\u0628\\u0647 \\u0627\\u062f\\u0645\\u06cc\\u0646 \\u0627\\u0631\\u0633\\u0627\\u0644 \\u0634\\u062f.-legacy-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[manual_review-True-\\u23f3 \\u0645\\u0647\\u0644\\u062a \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062a\\u0645\\u0627\\u0645 \\u0634\\u062f\\u0647 \\u0648 \\u0628\\u0631\\u0627\\u06cc \\u0628\\u0631\\u0631\\u0633\\u06cc \\u062f\\u0633\\u062a\\u06cc \\u0628\\u0647 \\u0627\\u062f\\u0645\\u06cc\\u0646 \\u0627\\u0631\\u0633\\u0627\\u0644 \\u0634\\u062f.-legacy-sqlite]"
    ]
  },
  {
    "name": "no_refresh",
    "disposition": "killed",
    "cases": 38,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[pending-True-\\u23f3 \\u0645\\u0647\\u0644\\u062a \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062a\\u0645\\u0627\\u0645 \\u0634\\u062f\\u0647 \\u0648 \\u0628\\u0631\\u0627\\u06cc \\u0628\\u0631\\u0631\\u0633\\u06cc \\u062f\\u0633\\u062a\\u06cc \\u0628\\u0647 \\u0627\\u062f\\u0645\\u06cc\\u0646 \\u0627\\u0631\\u0633\\u0627\\u0644 \\u0634\\u062f.-None-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[pending-True-\\u23f3 \\u0645\\u0647\\u0644\\u062a \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062a\\u0645\\u0627\\u0645 \\u0634\\u062f\\u0647 \\u0648 \\u0628\\u0631\\u0627\\u06cc \\u0628\\u0631\\u0631\\u0633\\u06cc \\u062f\\u0633\\u062a\\u06cc \\u0628\\u0647 \\u0627\\u062f\\u0645\\u06cc\\u0646 \\u0627\\u0631\\u0633\\u0627\\u0644 \\u0634\\u062f.-None-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[pending-True-\\u23f3 \\u0645\\u0647\\u0644\\u062a \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062a\\u0645\\u0627\\u0645 \\u0634\\u062f\\u0647 \\u0648 \\u0628\\u0631\\u0627\\u06cc \\u0628\\u0631\\u0631\\u0633\\u06cc \\u062f\\u0633\\u062a\\u06cc \\u0628\\u0647 \\u0627\\u062f\\u0645\\u06cc\\u0646 \\u0627\\u0631\\u0633\\u0627\\u0644 \\u0634\\u062f.-legacy-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[pending-True-\\u23f3 \\u0645\\u0647\\u0644\\u062a \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062a\\u0645\\u0627\\u0645 \\u0634\\u062f\\u0647 \\u0648 \\u0628\\u0631\\u0627\\u06cc \\u0628\\u0631\\u0631\\u0633\\u06cc \\u062f\\u0633\\u062a\\u06cc \\u0628\\u0647 \\u0627\\u062f\\u0645\\u06cc\\u0646 \\u0627\\u0631\\u0633\\u0627\\u0644 \\u0634\\u062f.-legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_completed",
    "disposition": "killed",
    "cases": 38,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[completed-True-\\u2705 \\u0627\\u06cc\\u0646 \\u067e\\u0631\\u062f\\u0627\\u062e\\u062a \\u0642\\u0628\\u0644\\u0627\\u064b \\u062a\\u0627\\u06cc\\u06cc\\u062f \\u0648 \\u062a\\u062d\\u0648\\u06cc\\u0644 \\u062f\\u0627\\u062f\\u0647 \\u0634\\u062f\\u0647 \\u0627\\u0633\\u062a.-None-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[completed-True-\\u2705 \\u0627\\u06cc\\u0646 \\u067e\\u0631\\u062f\\u0627\\u062e\\u062a \\u0642\\u0628\\u0644\\u0627\\u064b \\u062a\\u0627\\u06cc\\u06cc\\u062f \\u0648 \\u062a\\u062d\\u0648\\u06cc\\u0644 \\u062f\\u0627\\u062f\\u0647 \\u0634\\u062f\\u0647 \\u0627\\u0633\\u062a.-None-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[completed-True-\\u2705 \\u0627\\u06cc\\u0646 \\u067e\\u0631\\u062f\\u0627\\u062e\\u062a \\u0642\\u0628\\u0644\\u0627\\u064b \\u062a\\u0627\\u06cc\\u06cc\\u062f \\u0648 \\u062a\\u062d\\u0648\\u06cc\\u0644 \\u062f\\u0627\\u062f\\u0647 \\u0634\\u062f\\u0647 \\u0627\\u0633\\u062a.-legacy-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[completed-True-\\u2705 \\u0627\\u06cc\\u0646 \\u067e\\u0631\\u062f\\u0627\\u062e\\u062a \\u0642\\u0628\\u0644\\u0627\\u064b \\u062a\\u0627\\u06cc\\u06cc\\u062f \\u0648 \\u062a\\u062d\\u0648\\u06cc\\u0644 \\u062f\\u0627\\u062f\\u0647 \\u0634\\u062f\\u0647 \\u0627\\u0633\\u062a.-legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_review",
    "disposition": "killed",
    "cases": 38,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[pending-True-\\u23f3 \\u0645\\u0647\\u0644\\u062a \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062a\\u0645\\u0627\\u0645 \\u0634\\u062f\\u0647 \\u0648 \\u0628\\u0631\\u0627\\u06cc \\u0628\\u0631\\u0631\\u0633\\u06cc \\u062f\\u0633\\u062a\\u06cc \\u0628\\u0647 \\u0627\\u062f\\u0645\\u06cc\\u0646 \\u0627\\u0631\\u0633\\u0627\\u0644 \\u0634\\u062f.-None-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[pending-True-\\u23f3 \\u0645\\u0647\\u0644\\u062a \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062a\\u0645\\u0627\\u0645 \\u0634\\u062f\\u0647 \\u0648 \\u0628\\u0631\\u0627\\u06cc \\u0628\\u0631\\u0631\\u0633\\u06cc \\u062f\\u0633\\u062a\\u06cc \\u0628\\u0647 \\u0627\\u062f\\u0645\\u06cc\\u0646 \\u0627\\u0631\\u0633\\u0627\\u0644 \\u0634\\u062f.-None-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[pending-True-\\u23f3 \\u0645\\u0647\\u0644\\u062a \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062a\\u0645\\u0627\\u0645 \\u0634\\u062f\\u0647 \\u0648 \\u0628\\u0631\\u0627\\u06cc \\u0628\\u0631\\u0631\\u0633\\u06cc \\u062f\\u0633\\u062a\\u06cc \\u0628\\u0647 \\u0627\\u062f\\u0645\\u06cc\\u0646 \\u0627\\u0631\\u0633\\u0627\\u0644 \\u0634\\u062f.-legacy-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[pending-True-\\u23f3 \\u0645\\u0647\\u0644\\u062a \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062a\\u0645\\u0627\\u0645 \\u0634\\u062f\\u0647 \\u0648 \\u0628\\u0631\\u0627\\u06cc \\u0628\\u0631\\u0631\\u0633\\u06cc \\u062f\\u0633\\u062a\\u06cc \\u0628\\u0647 \\u0627\\u062f\\u0645\\u06cc\\u0646 \\u0627\\u0631\\u0633\\u0627\\u0644 \\u0634\\u062f.-legacy-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[manual_review-True-\\u23f3 \\u0645\\u0647\\u0644\\u062a \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062a\\u0645\\u0627\\u0645 \\u0634\\u062f\\u0647 \\u0648 \\u0628\\u0631\\u0627\\u06cc \\u0628\\u0631\\u0631\\u0633\\u06cc \\u062f\\u0633\\u062a\\u06cc \\u0628\\u0647 \\u0627\\u062f\\u0645\\u06cc\\u0646 \\u0627\\u0631\\u0633\\u0627\\u0644 \\u0634\\u062f.-None-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[manual_review-True-\\u23f3 \\u0645\\u0647\\u0644\\u062a \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062a\\u0645\\u0627\\u0645 \\u0634\\u062f\\u0647 \\u0648 \\u0628\\u0631\\u0627\\u06cc \\u0628\\u0631\\u0631\\u0633\\u06cc \\u062f\\u0633\\u062a\\u06cc \\u0628\\u0647 \\u0627\\u062f\\u0645\\u06cc\\u0646 \\u0627\\u0631\\u0633\\u0627\\u0644 \\u0634\\u062f.-None-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[manual_review-True-\\u23f3 \\u0645\\u0647\\u0644\\u062a \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062a\\u0645\\u0627\\u0645 \\u0634\\u062f\\u0647 \\u0648 \\u0628\\u0631\\u0627\\u06cc \\u0628\\u0631\\u0631\\u0633\\u06cc \\u062f\\u0633\\u062a\\u06cc \\u0628\\u0647 \\u0627\\u062f\\u0645\\u06cc\\u0646 \\u0627\\u0631\\u0633\\u0627\\u0644 \\u0634\\u062f.-legacy-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[manual_review-True-\\u23f3 \\u0645\\u0647\\u0644\\u062a \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062a\\u0645\\u0627\\u0645 \\u0634\\u062f\\u0647 \\u0648 \\u0628\\u0631\\u0627\\u06cc \\u0628\\u0631\\u0631\\u0633\\u06cc \\u062f\\u0633\\u062a\\u06cc \\u0628\\u0647 \\u0627\\u062f\\u0645\\u06cc\\u0646 \\u0627\\u0631\\u0633\\u0627\\u0644 \\u0634\\u062f.-legacy-sqlite]"
    ]
  },
  {
    "name": "legacy_overstrict",
    "disposition": "killed",
    "cases": 38,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[pending-False-\\u23f3 \\u0647\\u0646\\u0648\\u0632 \\u067e\\u06cc\\u0627\\u0645\\u06a9 \\u0628\\u0627\\u0646\\u06a9 \\u0628\\u0631\\u0627\\u06cc \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062f\\u0631\\u06cc\\u0627\\u0641\\u062a \\u0646\\u0634\\u062f\\u0647. \\u06a9\\u0645\\u06cc \\u0635\\u0628\\u0631 \\u06a9\\u0646.-None-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[pending-False-\\u23f3 \\u0647\\u0646\\u0648\\u0632 \\u067e\\u06cc\\u0627\\u0645\\u06a9 \\u0628\\u0627\\u0646\\u06a9 \\u0628\\u0631\\u0627\\u06cc \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062f\\u0631\\u06cc\\u0627\\u0641\\u062a \\u0646\\u0634\\u062f\\u0647. \\u06a9\\u0645\\u06cc \\u0635\\u0628\\u0631 \\u06a9\\u0646.-None-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[pending-False-\\u23f3 \\u0647\\u0646\\u0648\\u0632 \\u067e\\u06cc\\u0627\\u0645\\u06a9 \\u0628\\u0627\\u0646\\u06a9 \\u0628\\u0631\\u0627\\u06cc \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062f\\u0631\\u06cc\\u0627\\u0641\\u062a \\u0646\\u0634\\u062f\\u0647. \\u06a9\\u0645\\u06cc \\u0635\\u0628\\u0631 \\u06a9\\u0646.-legacy-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[pending-False-\\u23f3 \\u0647\\u0646\\u0648\\u0632 \\u067e\\u06cc\\u0627\\u0645\\u06a9 \\u0628\\u0627\\u0646\\u06a9 \\u0628\\u0631\\u0627\\u06cc \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062f\\u0631\\u06cc\\u0627\\u0641\\u062a \\u0646\\u0634\\u062f\\u0647. \\u06a9\\u0645\\u06cc \\u0635\\u0628\\u0631 \\u06a9\\u0646.-legacy-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[pending-True-\\u23f3 \\u0645\\u0647\\u0644\\u062a \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062a\\u0645\\u0627\\u0645 \\u0634\\u062f\\u0647 \\u0648 \\u0628\\u0631\\u0627\\u06cc \\u0628\\u0631\\u0631\\u0633\\u06cc \\u062f\\u0633\\u062a\\u06cc \\u0628\\u0647 \\u0627\\u062f\\u0645\\u06cc\\u0646 \\u0627\\u0631\\u0633\\u0627\\u0644 \\u0634\\u062f.-None-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[pending-True-\\u23f3 \\u0645\\u0647\\u0644\\u062a \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062a\\u0645\\u0627\\u0645 \\u0634\\u062f\\u0647 \\u0648 \\u0628\\u0631\\u0627\\u06cc \\u0628\\u0631\\u0631\\u0633\\u06cc \\u062f\\u0633\\u062a\\u06cc \\u0628\\u0647 \\u0627\\u062f\\u0645\\u06cc\\u0646 \\u0627\\u0631\\u0633\\u0627\\u0644 \\u0634\\u062f.-None-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[pending-True-\\u23f3 \\u0645\\u0647\\u0644\\u062a \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062a\\u0645\\u0627\\u0645 \\u0634\\u062f\\u0647 \\u0648 \\u0628\\u0631\\u0627\\u06cc \\u0628\\u0631\\u0631\\u0633\\u06cc \\u062f\\u0633\\u062a\\u06cc \\u0628\\u0647 \\u0627\\u062f\\u0645\\u06cc\\u0646 \\u0627\\u0631\\u0633\\u0627\\u0644 \\u0634\\u062f.-legacy-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[pending-True-\\u23f3 \\u0645\\u0647\\u0644\\u062a \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062a\\u0645\\u0627\\u0645 \\u0634\\u062f\\u0647 \\u0648 \\u0628\\u0631\\u0627\\u06cc \\u0628\\u0631\\u0631\\u0633\\u06cc \\u062f\\u0633\\u062a\\u06cc \\u0628\\u0647 \\u0627\\u062f\\u0645\\u06cc\\u0646 \\u0627\\u0631\\u0633\\u0627\\u0644 \\u0634\\u062f.-legacy-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[completed-True-\\u2705 \\u0627\\u06cc\\u0646 \\u067e\\u0631\\u062f\\u0627\\u062e\\u062a \\u0642\\u0628\\u0644\\u0627\\u064b \\u062a\\u0627\\u06cc\\u06cc\\u062f \\u0648 \\u062a\\u062d\\u0648\\u06cc\\u0644 \\u062f\\u0627\\u062f\\u0647 \\u0634\\u062f\\u0647 \\u0627\\u0633\\u062a.-None-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[completed-True-\\u2705 \\u0627\\u06cc\\u0646 \\u067e\\u0631\\u062f\\u0627\\u062e\\u062a \\u0642\\u0628\\u0644\\u0627\\u064b \\u062a\\u0627\\u06cc\\u06cc\\u062f \\u0648 \\u062a\\u062d\\u0648\\u06cc\\u0644 \\u062f\\u0627\\u062f\\u0647 \\u0634\\u062f\\u0647 \\u0627\\u0633\\u062a.-None-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[completed-True-\\u2705 \\u0627\\u06cc\\u0646 \\u067e\\u0631\\u062f\\u0627\\u062e\\u062a \\u0642\\u0628\\u0644\\u0627\\u064b \\u062a\\u0627\\u06cc\\u06cc\\u062f \\u0648 \\u062a\\u062d\\u0648\\u06cc\\u0644 \\u062f\\u0627\\u062f\\u0647 \\u0634\\u062f\\u0647 \\u0627\\u0633\\u062a.-legacy-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[completed-True-\\u2705 \\u0627\\u06cc\\u0646 \\u067e\\u0631\\u062f\\u0627\\u062e\\u062a \\u0642\\u0628\\u0644\\u0627\\u064b \\u062a\\u0627\\u06cc\\u06cc\\u062f \\u0648 \\u062a\\u062d\\u0648\\u06cc\\u0644 \\u062f\\u0627\\u062f\\u0647 \\u0634\\u062f\\u0647 \\u0627\\u0633\\u062a.-legacy-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[manual_review-True-\\u23f3 \\u0645\\u0647\\u0644\\u062a \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062a\\u0645\\u0627\\u0645 \\u0634\\u062f\\u0647 \\u0648 \\u0628\\u0631\\u0627\\u06cc \\u0628\\u0631\\u0631\\u0633\\u06cc \\u062f\\u0633\\u062a\\u06cc \\u0628\\u0647 \\u0627\\u062f\\u0645\\u06cc\\u0646 \\u0627\\u0631\\u0633\\u0627\\u0644 \\u0634\\u062f.-None-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[manual_review-True-\\u23f3 \\u0645\\u0647\\u0644\\u062a \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062a\\u0645\\u0627\\u0645 \\u0634\\u062f\\u0647 \\u0648 \\u0628\\u0631\\u0627\\u06cc \\u0628\\u0631\\u0631\\u0633\\u06cc \\u062f\\u0633\\u062a\\u06cc \\u0628\\u0647 \\u0627\\u062f\\u0645\\u06cc\\u0646 \\u0627\\u0631\\u0633\\u0627\\u0644 \\u0634\\u062f.-None-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[manual_review-True-\\u23f3 \\u0645\\u0647\\u0644\\u062a \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062a\\u0645\\u0627\\u0645 \\u0634\\u062f\\u0647 \\u0648 \\u0628\\u0631\\u0627\\u06cc \\u0628\\u0631\\u0631\\u0633\\u06cc \\u062f\\u0633\\u062a\\u06cc \\u0628\\u0647 \\u0627\\u062f\\u0645\\u06cc\\u0646 \\u0627\\u0631\\u0633\\u0627\\u0644 \\u0634\\u062f.-legacy-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[manual_review-True-\\u23f3 \\u0645\\u0647\\u0644\\u062a \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062a\\u0645\\u0627\\u0645 \\u0634\\u062f\\u0647 \\u0648 \\u0628\\u0631\\u0627\\u06cc \\u0628\\u0631\\u0631\\u0633\\u06cc \\u062f\\u0633\\u062a\\u06cc \\u0628\\u0647 \\u0627\\u062f\\u0645\\u06cc\\u0646 \\u0627\\u0631\\u0633\\u0627\\u0644 \\u0634\\u062f.-legacy-sqlite]"
    ]
  },
  {
    "name": "sibling_overstrict",
    "disposition": "killed",
    "cases": 38,
    "failed_test_ids": [
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[pending-False-\\u23f3 \\u0647\\u0646\\u0648\\u0632 \\u067e\\u06cc\\u0627\\u0645\\u06a9 \\u0628\\u0627\\u0646\\u06a9 \\u0628\\u0631\\u0627\\u06cc \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062f\\u0631\\u06cc\\u0627\\u0641\\u062a \\u0646\\u0634\\u062f\\u0647. \\u06a9\\u0645\\u06cc \\u0635\\u0628\\u0631 \\u06a9\\u0646.-None-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[pending-False-\\u23f3 \\u0647\\u0646\\u0648\\u0632 \\u067e\\u06cc\\u0627\\u0645\\u06a9 \\u0628\\u0627\\u0646\\u06a9 \\u0628\\u0631\\u0627\\u06cc \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062f\\u0631\\u06cc\\u0627\\u0641\\u062a \\u0646\\u0634\\u062f\\u0647. \\u06a9\\u0645\\u06cc \\u0635\\u0628\\u0631 \\u06a9\\u0646.-None-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[pending-False-\\u23f3 \\u0647\\u0646\\u0648\\u0632 \\u067e\\u06cc\\u0627\\u0645\\u06a9 \\u0628\\u0627\\u0646\\u06a9 \\u0628\\u0631\\u0627\\u06cc \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062f\\u0631\\u06cc\\u0627\\u0641\\u062a \\u0646\\u0634\\u062f\\u0647. \\u06a9\\u0645\\u06cc \\u0635\\u0628\\u0631 \\u06a9\\u0646.-legacy-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[pending-False-\\u23f3 \\u0647\\u0646\\u0648\\u0632 \\u067e\\u06cc\\u0627\\u0645\\u06a9 \\u0628\\u0627\\u0646\\u06a9 \\u0628\\u0631\\u0627\\u06cc \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062f\\u0631\\u06cc\\u0627\\u0641\\u062a \\u0646\\u0634\\u062f\\u0647. \\u06a9\\u0645\\u06cc \\u0635\\u0628\\u0631 \\u06a9\\u0646.-legacy-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[pending-True-\\u23f3 \\u0645\\u0647\\u0644\\u062a \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062a\\u0645\\u0627\\u0645 \\u0634\\u062f\\u0647 \\u0648 \\u0628\\u0631\\u0627\\u06cc \\u0628\\u0631\\u0631\\u0633\\u06cc \\u062f\\u0633\\u062a\\u06cc \\u0628\\u0647 \\u0627\\u062f\\u0645\\u06cc\\u0646 \\u0627\\u0631\\u0633\\u0627\\u0644 \\u0634\\u062f.-None-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[pending-True-\\u23f3 \\u0645\\u0647\\u0644\\u062a \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062a\\u0645\\u0627\\u0645 \\u0634\\u062f\\u0647 \\u0648 \\u0628\\u0631\\u0627\\u06cc \\u0628\\u0631\\u0631\\u0633\\u06cc \\u062f\\u0633\\u062a\\u06cc \\u0628\\u0647 \\u0627\\u062f\\u0645\\u06cc\\u0646 \\u0627\\u0631\\u0633\\u0627\\u0644 \\u0634\\u062f.-None-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[pending-True-\\u23f3 \\u0645\\u0647\\u0644\\u062a \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062a\\u0645\\u0627\\u0645 \\u0634\\u062f\\u0647 \\u0648 \\u0628\\u0631\\u0627\\u06cc \\u0628\\u0631\\u0631\\u0633\\u06cc \\u062f\\u0633\\u062a\\u06cc \\u0628\\u0647 \\u0627\\u062f\\u0645\\u06cc\\u0646 \\u0627\\u0631\\u0633\\u0627\\u0644 \\u0634\\u062f.-legacy-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[pending-True-\\u23f3 \\u0645\\u0647\\u0644\\u062a \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062a\\u0645\\u0627\\u0645 \\u0634\\u062f\\u0647 \\u0648 \\u0628\\u0631\\u0627\\u06cc \\u0628\\u0631\\u0631\\u0633\\u06cc \\u062f\\u0633\\u062a\\u06cc \\u0628\\u0647 \\u0627\\u062f\\u0645\\u06cc\\u0646 \\u0627\\u0631\\u0633\\u0627\\u0644 \\u0634\\u062f.-legacy-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[completed-True-\\u2705 \\u0627\\u06cc\\u0646 \\u067e\\u0631\\u062f\\u0627\\u062e\\u062a \\u0642\\u0628\\u0644\\u0627\\u064b \\u062a\\u0627\\u06cc\\u06cc\\u062f \\u0648 \\u062a\\u062d\\u0648\\u06cc\\u0644 \\u062f\\u0627\\u062f\\u0647 \\u0634\\u062f\\u0647 \\u0627\\u0633\\u062a.-None-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[completed-True-\\u2705 \\u0627\\u06cc\\u0646 \\u067e\\u0631\\u062f\\u0627\\u062e\\u062a \\u0642\\u0628\\u0644\\u0627\\u064b \\u062a\\u0627\\u06cc\\u06cc\\u062f \\u0648 \\u062a\\u062d\\u0648\\u06cc\\u0644 \\u062f\\u0627\\u062f\\u0647 \\u0634\\u062f\\u0647 \\u0627\\u0633\\u062a.-None-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[completed-True-\\u2705 \\u0627\\u06cc\\u0646 \\u067e\\u0631\\u062f\\u0627\\u062e\\u062a \\u0642\\u0628\\u0644\\u0627\\u064b \\u062a\\u0627\\u06cc\\u06cc\\u062f \\u0648 \\u062a\\u062d\\u0648\\u06cc\\u0644 \\u062f\\u0627\\u062f\\u0647 \\u0634\\u062f\\u0647 \\u0627\\u0633\\u062a.-legacy-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[completed-True-\\u2705 \\u0627\\u06cc\\u0646 \\u067e\\u0631\\u062f\\u0627\\u062e\\u062a \\u0642\\u0628\\u0644\\u0627\\u064b \\u062a\\u0627\\u06cc\\u06cc\\u062f \\u0648 \\u062a\\u062d\\u0648\\u06cc\\u0644 \\u062f\\u0627\\u062f\\u0647 \\u0634\\u062f\\u0647 \\u0627\\u0633\\u062a.-legacy-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[manual_review-True-\\u23f3 \\u0645\\u0647\\u0644\\u062a \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062a\\u0645\\u0627\\u0645 \\u0634\\u062f\\u0647 \\u0648 \\u0628\\u0631\\u0627\\u06cc \\u0628\\u0631\\u0631\\u0633\\u06cc \\u062f\\u0633\\u062a\\u06cc \\u0628\\u0647 \\u0627\\u062f\\u0645\\u06cc\\u0646 \\u0627\\u0631\\u0633\\u0627\\u0644 \\u0634\\u062f.-None-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[manual_review-True-\\u23f3 \\u0645\\u0647\\u0644\\u062a \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062a\\u0645\\u0627\\u0645 \\u0634\\u062f\\u0647 \\u0648 \\u0628\\u0631\\u0627\\u06cc \\u0628\\u0631\\u0631\\u0633\\u06cc \\u062f\\u0633\\u062a\\u06cc \\u0628\\u0647 \\u0627\\u062f\\u0645\\u06cc\\u0646 \\u0627\\u0631\\u0633\\u0627\\u0644 \\u0634\\u062f.-None-sqlite]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[manual_review-True-\\u23f3 \\u0645\\u0647\\u0644\\u062a \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062a\\u0645\\u0627\\u0645 \\u0634\\u062f\\u0647 \\u0648 \\u0628\\u0631\\u0627\\u06cc \\u0628\\u0631\\u0631\\u0633\\u06cc \\u062f\\u0633\\u062a\\u06cc \\u0628\\u0647 \\u0627\\u062f\\u0645\\u06cc\\u0646 \\u0627\\u0631\\u0633\\u0627\\u0644 \\u0634\\u062f.-legacy-dict]",
      "tests.integration.test_composite_telegram_card_status_guards::test_legacy_card_status_and_global_expiry[manual_review-True-\\u23f3 \\u0645\\u0647\\u0644\\u062a \\u0627\\u06cc\\u0646 \\u0645\\u0628\\u0644\\u063a \\u062a\\u0645\\u0627\\u0645 \\u0634\\u062f\\u0647 \\u0648 \\u0628\\u0631\\u0627\\u06cc \\u0628\\u0631\\u0631\\u0633\\u06cc \\u062f\\u0633\\u062a\\u06cc \\u0628\\u0647 \\u0627\\u062f\\u0645\\u06cc\\u0646 \\u0627\\u0631\\u0633\\u0627\\u0644 \\u0634\\u062f.-legacy-sqlite]"
    ]
  }
]
```

Independent valid mutations, relevant assertion failures only. No survivors/errors/skips. Scratch auto-cleaned. Reference checks the owned invoice order/custom-product identity before shared status maintenance/claims; real SQL expiry and legacy status/opacity controls preserved. No production implementation claim.
