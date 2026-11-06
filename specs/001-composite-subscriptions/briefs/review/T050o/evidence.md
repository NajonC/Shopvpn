# T050o reference and mutation evidence

Source hashes:
```json
{
  "ai_support.py": "1297845ea834eee309443bbc9c9a11ffcea4e982e190d9dbb9c67adfffea5eeb",
  "tests/integration/test_composite_ai_trial_guards.py": "ccee912bd86ee5f37c969577091787bb6fbcdf84e69128cbae112c800174c133",
  "tests/characterization/test_free_test_flow.py": "3e6b88540f7c55aba7805cc28dadcb5eee608a4b9b35bc7288c88f461385138f",
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
    "name": "omit_guard",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_trial_guards::test_composite_ai_trial_refused[False-dict]",
      "tests.integration.test_composite_ai_trial_guards::test_composite_ai_trial_refused[False-sqlite]",
      "tests.integration.test_composite_ai_trial_guards::test_composite_ai_trial_refused[True-dict]",
      "tests.integration.test_composite_ai_trial_guards::test_composite_ai_trial_refused[True-sqlite]"
    ]
  },
  {
    "name": "wrong_marker",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_trial_guards::test_composite_ai_trial_refused[False-dict]",
      "tests.integration.test_composite_ai_trial_guards::test_composite_ai_trial_refused[False-sqlite]",
      "tests.integration.test_composite_ai_trial_guards::test_composite_ai_trial_refused[True-dict]",
      "tests.integration.test_composite_ai_trial_guards::test_composite_ai_trial_refused[True-sqlite]"
    ]
  },
  {
    "name": "only_first_plan",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_trial_guards::test_composite_ai_trial_refused[True-dict]",
      "tests.integration.test_composite_ai_trial_guards::test_composite_ai_trial_refused[True-sqlite]"
    ]
  },
  {
    "name": "reject_missing",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[eligible-None-dict]",
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[eligible-None-sqlite]",
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[disabled-None-dict]",
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[disabled-None-sqlite]",
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[used-None-dict]",
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[used-None-sqlite]",
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[no_user-None-dict]",
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[no_user-None-sqlite]",
      "tests.integration.test_composite_ai_trial_guards::test_inactive_composite_trial_does_not_block_legacy[dict]",
      "tests.integration.test_composite_ai_trial_guards::test_inactive_composite_trial_does_not_block_legacy[sqlite]"
    ]
  },
  {
    "name": "reject_explicit_legacy",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[eligible-legacy-dict]",
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[eligible-legacy-sqlite]",
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[disabled-legacy-dict]",
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[disabled-legacy-sqlite]",
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[used-legacy-dict]",
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[used-legacy-sqlite]",
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[no_user-legacy-dict]",
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[no_user-legacy-sqlite]"
    ]
  },
  {
    "name": "no_reason",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_trial_guards::test_composite_ai_trial_refused[False-dict]",
      "tests.integration.test_composite_ai_trial_guards::test_composite_ai_trial_refused[False-sqlite]",
      "tests.integration.test_composite_ai_trial_guards::test_composite_ai_trial_refused[True-dict]",
      "tests.integration.test_composite_ai_trial_guards::test_composite_ai_trial_refused[True-sqlite]"
    ]
  },
  {
    "name": "leak_name",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_trial_guards::test_composite_ai_trial_refused[False-dict]",
      "tests.integration.test_composite_ai_trial_guards::test_composite_ai_trial_refused[False-sqlite]",
      "tests.integration.test_composite_ai_trial_guards::test_composite_ai_trial_refused[True-dict]",
      "tests.integration.test_composite_ai_trial_guards::test_composite_ai_trial_refused[True-sqlite]"
    ]
  },
  {
    "name": "log_name",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_trial_guards::test_composite_ai_trial_refused[False-dict]",
      "tests.integration.test_composite_ai_trial_guards::test_composite_ai_trial_refused[False-sqlite]",
      "tests.integration.test_composite_ai_trial_guards::test_composite_ai_trial_refused[True-dict]",
      "tests.integration.test_composite_ai_trial_guards::test_composite_ai_trial_refused[True-sqlite]"
    ]
  },
  {
    "name": "reserve_before_refusal",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_trial_guards::test_composite_ai_trial_refused[False-dict]",
      "tests.integration.test_composite_ai_trial_guards::test_composite_ai_trial_refused[False-sqlite]",
      "tests.integration.test_composite_ai_trial_guards::test_composite_ai_trial_refused[True-dict]",
      "tests.integration.test_composite_ai_trial_guards::test_composite_ai_trial_refused[True-sqlite]"
    ]
  },
  {
    "name": "include_inactive",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[no_plan-None-dict]",
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[no_plan-None-sqlite]",
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[no_plan-legacy-dict]",
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[no_plan-legacy-sqlite]",
      "tests.integration.test_composite_ai_trial_guards::test_inactive_composite_trial_does_not_block_legacy[dict]",
      "tests.integration.test_composite_ai_trial_guards::test_inactive_composite_trial_does_not_block_legacy[sqlite]"
    ]
  },
  {
    "name": "ignore_disabled",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[disabled-None-dict]",
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[disabled-None-sqlite]",
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[disabled-legacy-dict]",
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[disabled-legacy-sqlite]"
    ]
  },
  {
    "name": "ignore_used",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[used-None-dict]",
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[used-None-sqlite]",
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[used-legacy-dict]",
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[used-legacy-sqlite]"
    ]
  },
  {
    "name": "allow_one_extra",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[used-None-dict]",
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[used-None-sqlite]",
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[used-legacy-dict]",
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[used-legacy-sqlite]"
    ]
  },
  {
    "name": "refuse_unused",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[eligible-None-dict]",
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[eligible-None-sqlite]",
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[eligible-legacy-dict]",
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[eligible-legacy-sqlite]",
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[no_plan-None-dict]",
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[no_plan-None-sqlite]",
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[no_plan-legacy-dict]",
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[no_plan-legacy-sqlite]",
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[no_user-None-dict]",
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[no_user-None-sqlite]",
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[no_user-legacy-dict]",
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[no_user-legacy-sqlite]",
      "tests.integration.test_composite_ai_trial_guards::test_inactive_composite_trial_does_not_block_legacy[dict]",
      "tests.integration.test_composite_ai_trial_guards::test_inactive_composite_trial_does_not_block_legacy[sqlite]"
    ]
  },
  {
    "name": "ignore_no_plan",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[no_plan-None-dict]",
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[no_plan-None-sqlite]",
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[no_plan-legacy-dict]",
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[no_plan-legacy-sqlite]"
    ]
  },
  {
    "name": "reject_missing_user",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[no_user-None-dict]",
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[no_user-None-sqlite]",
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[no_user-legacy-dict]",
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[no_user-legacy-sqlite]"
    ]
  },
  {
    "name": "reserve_on_eligibility",
    "disposition": "killed",
    "cases": 26,
    "failed_test_ids": [
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[eligible-None-dict]",
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[eligible-None-sqlite]",
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[eligible-legacy-dict]",
      "tests.integration.test_composite_ai_trial_guards::test_legacy_ai_trial_eligibility_preserved[eligible-legacy-sqlite]",
      "tests.integration.test_composite_ai_trial_guards::test_inactive_composite_trial_does_not_block_legacy[dict]",
      "tests.integration.test_composite_ai_trial_guards::test_inactive_composite_trial_does_not_block_legacy[sqlite]"
    ]
  }
]
```

Independent valid mutations, relevant assertion failures only. No survivors/errors/skips. Scratch auto-cleaned. Reference checks active test-plan metadata inside real eligibility function before unchanged legacy eligibility checks; no production implementation claim.
