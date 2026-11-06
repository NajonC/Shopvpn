# T050b reference and mutation evidence

Source hashes:
```json
{
  "renewal_reminders.py": "e73d95ffebf335bf1543af1709b89dadc0dac37faae6e726454c6b86ae0e0d93",
  "connect_alerts.py": "97175e7eae047c519e7335e1b5ee4c2fbaba448803dd45d9c2f2b99f556d3f37",
  "tests/integration/test_composite_auto_renewal_guards.py": "b9d2bec8850d199f27994e32244dff9fb8393b05357e1766b028daf46e8d207c",
  "tests/integration/test_composite_reminder_guards.py": "fb62d955c0b2eb20ddc7b165c0de24b2cdccf9483c122a2cf7d2ce0d820ed8f2",
  "tests/characterization/test_legacy_renewal_reminders.py": "84722b6b10d9fbdae768cb5fb8e8fbc3490b3a213575196210a56401c6e61ea3"
}
```

Independent results:
```json
[
  {
    "mutation": "reference",
    "disposition": "pass",
    "cases": 100,
    "failures": []
  },
  {
    "mutation": "renewal_omit",
    "disposition": "killed",
    "cases": 17,
    "failures": [
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-dict-pool-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-dict-custom-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-sqlite-pool-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-sqlite-custom-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-dict-pool-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-dict-custom-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-sqlite-pool-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-sqlite-custom-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_candidate_does_not_block_later_legacy[expiry]"
    ]
  },
  {
    "mutation": "renewal_wrong_kind",
    "disposition": "killed",
    "cases": 17,
    "failures": [
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-dict-pool-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-dict-custom-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-sqlite-pool-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-sqlite-custom-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-dict-pool-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-dict-custom-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-sqlite-pool-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-sqlite-custom-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_candidate_does_not_block_later_legacy[expiry]"
    ]
  },
  {
    "mutation": "renewal_reject_legacy",
    "disposition": "killed",
    "cases": 17,
    "failures": [
      "tests.integration.test_composite_reminder_guards::test_legacy_reminder_candidate_still_processed[legacy-dict-pool-expiry]",
      "tests.integration.test_composite_reminder_guards::test_legacy_reminder_candidate_still_processed[legacy-dict-custom-expiry]",
      "tests.integration.test_composite_reminder_guards::test_legacy_reminder_candidate_still_processed[legacy-sqlite-pool-expiry]",
      "tests.integration.test_composite_reminder_guards::test_legacy_reminder_candidate_still_processed[legacy-sqlite-custom-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_candidate_does_not_block_later_legacy[expiry]"
    ]
  },
  {
    "mutation": "renewal_reject_absent",
    "disposition": "killed",
    "cases": 17,
    "failures": [
      "tests.integration.test_composite_reminder_guards::test_legacy_reminder_candidate_still_processed[None-dict-pool-expiry]",
      "tests.integration.test_composite_reminder_guards::test_legacy_reminder_candidate_still_processed[None-dict-custom-expiry]",
      "tests.integration.test_composite_reminder_guards::test_legacy_reminder_candidate_still_processed[None-sqlite-pool-expiry]",
      "tests.integration.test_composite_reminder_guards::test_legacy_reminder_candidate_still_processed[None-sqlite-custom-expiry]"
    ]
  },
  {
    "mutation": "renewal_no_reason",
    "disposition": "killed",
    "cases": 17,
    "failures": [
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-dict-pool-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-dict-custom-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-sqlite-pool-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-sqlite-custom-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-dict-pool-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-dict-custom-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-sqlite-pool-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-sqlite-custom-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_candidate_does_not_block_later_legacy[expiry]"
    ]
  },
  {
    "mutation": "renewal_leak_link",
    "disposition": "killed",
    "cases": 17,
    "failures": [
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-dict-pool-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-dict-custom-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-sqlite-pool-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-sqlite-custom-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-dict-pool-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-dict-custom-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-sqlite-pool-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-sqlite-custom-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_candidate_does_not_block_later_legacy[expiry]"
    ]
  },
  {
    "mutation": "renewal_late_fetch",
    "disposition": "killed",
    "cases": 17,
    "failures": [
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-dict-pool-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-dict-custom-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-sqlite-pool-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-sqlite-custom-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-dict-pool-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-dict-custom-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-sqlite-pool-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-sqlite-custom-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_candidate_does_not_block_later_legacy[expiry]"
    ]
  },
  {
    "mutation": "renewal_late_missing_user",
    "disposition": "killed",
    "cases": 17,
    "failures": [
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-dict-pool-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-dict-custom-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-sqlite-pool-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-sqlite-custom-expiry]"
    ]
  },
  {
    "mutation": "renewal_false_success",
    "disposition": "killed",
    "cases": 17,
    "failures": [
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-dict-pool-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-dict-custom-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-sqlite-pool-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-sqlite-custom-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-dict-pool-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-dict-custom-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-sqlite-pool-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-sqlite-custom-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_candidate_does_not_block_later_legacy[expiry]"
    ]
  },
  {
    "mutation": "volume_omit",
    "disposition": "killed",
    "cases": 17,
    "failures": [
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-dict-pool-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-dict-custom-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-sqlite-pool-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-sqlite-custom-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-dict-pool-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-dict-custom-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-sqlite-pool-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-sqlite-custom-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_candidate_does_not_block_later_legacy[volume]"
    ]
  },
  {
    "mutation": "volume_wrong_kind",
    "disposition": "killed",
    "cases": 17,
    "failures": [
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-dict-pool-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-dict-custom-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-sqlite-pool-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-sqlite-custom-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-dict-pool-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-dict-custom-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-sqlite-pool-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-sqlite-custom-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_candidate_does_not_block_later_legacy[volume]"
    ]
  },
  {
    "mutation": "volume_reject_legacy",
    "disposition": "killed",
    "cases": 17,
    "failures": [
      "tests.integration.test_composite_reminder_guards::test_legacy_reminder_candidate_still_processed[legacy-dict-pool-volume]",
      "tests.integration.test_composite_reminder_guards::test_legacy_reminder_candidate_still_processed[legacy-dict-custom-volume]",
      "tests.integration.test_composite_reminder_guards::test_legacy_reminder_candidate_still_processed[legacy-sqlite-pool-volume]",
      "tests.integration.test_composite_reminder_guards::test_legacy_reminder_candidate_still_processed[legacy-sqlite-custom-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_candidate_does_not_block_later_legacy[volume]"
    ]
  },
  {
    "mutation": "volume_reject_absent",
    "disposition": "killed",
    "cases": 17,
    "failures": [
      "tests.integration.test_composite_reminder_guards::test_legacy_reminder_candidate_still_processed[None-dict-pool-volume]",
      "tests.integration.test_composite_reminder_guards::test_legacy_reminder_candidate_still_processed[None-dict-custom-volume]",
      "tests.integration.test_composite_reminder_guards::test_legacy_reminder_candidate_still_processed[None-sqlite-pool-volume]",
      "tests.integration.test_composite_reminder_guards::test_legacy_reminder_candidate_still_processed[None-sqlite-custom-volume]"
    ]
  },
  {
    "mutation": "volume_no_reason",
    "disposition": "killed",
    "cases": 17,
    "failures": [
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-dict-pool-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-dict-custom-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-sqlite-pool-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-sqlite-custom-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-dict-pool-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-dict-custom-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-sqlite-pool-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-sqlite-custom-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_candidate_does_not_block_later_legacy[volume]"
    ]
  },
  {
    "mutation": "volume_leak_link",
    "disposition": "killed",
    "cases": 17,
    "failures": [
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-dict-pool-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-dict-custom-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-sqlite-pool-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-sqlite-custom-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-dict-pool-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-dict-custom-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-sqlite-pool-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-sqlite-custom-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_candidate_does_not_block_later_legacy[volume]"
    ]
  },
  {
    "mutation": "volume_late_fetch",
    "disposition": "killed",
    "cases": 17,
    "failures": [
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-dict-pool-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-dict-custom-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-sqlite-pool-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-sqlite-custom-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-dict-pool-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-dict-custom-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-sqlite-pool-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-sqlite-custom-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_candidate_does_not_block_later_legacy[volume]"
    ]
  },
  {
    "mutation": "volume_late_missing_user",
    "disposition": "killed",
    "cases": 17,
    "failures": [
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-dict-pool-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-dict-custom-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-sqlite-pool-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-sqlite-custom-volume]"
    ]
  },
  {
    "mutation": "volume_false_success",
    "disposition": "killed",
    "cases": 17,
    "failures": [
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-dict-pool-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-dict-custom-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-sqlite-pool-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-sqlite-custom-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-dict-pool-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-dict-custom-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-sqlite-pool-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-sqlite-custom-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_candidate_does_not_block_later_legacy[volume]"
    ]
  },
  {
    "mutation": "connect_omit",
    "disposition": "killed",
    "cases": 17,
    "failures": [
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-dict-pool-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-dict-custom-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-sqlite-pool-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-sqlite-custom-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-dict-pool-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-dict-custom-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-sqlite-pool-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-sqlite-custom-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_candidate_does_not_block_later_legacy[connection]"
    ]
  },
  {
    "mutation": "connect_wrong_kind",
    "disposition": "killed",
    "cases": 17,
    "failures": [
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-dict-pool-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-dict-custom-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-sqlite-pool-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-sqlite-custom-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-dict-pool-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-dict-custom-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-sqlite-pool-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-sqlite-custom-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_candidate_does_not_block_later_legacy[connection]"
    ]
  },
  {
    "mutation": "connect_reject_legacy",
    "disposition": "killed",
    "cases": 17,
    "failures": [
      "tests.integration.test_composite_reminder_guards::test_legacy_reminder_candidate_still_processed[legacy-dict-pool-connection]",
      "tests.integration.test_composite_reminder_guards::test_legacy_reminder_candidate_still_processed[legacy-dict-custom-connection]",
      "tests.integration.test_composite_reminder_guards::test_legacy_reminder_candidate_still_processed[legacy-sqlite-pool-connection]",
      "tests.integration.test_composite_reminder_guards::test_legacy_reminder_candidate_still_processed[legacy-sqlite-custom-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_candidate_does_not_block_later_legacy[connection]"
    ]
  },
  {
    "mutation": "connect_reject_absent",
    "disposition": "killed",
    "cases": 17,
    "failures": [
      "tests.integration.test_composite_reminder_guards::test_legacy_reminder_candidate_still_processed[None-dict-pool-connection]",
      "tests.integration.test_composite_reminder_guards::test_legacy_reminder_candidate_still_processed[None-dict-custom-connection]",
      "tests.integration.test_composite_reminder_guards::test_legacy_reminder_candidate_still_processed[None-sqlite-pool-connection]",
      "tests.integration.test_composite_reminder_guards::test_legacy_reminder_candidate_still_processed[None-sqlite-custom-connection]"
    ]
  },
  {
    "mutation": "connect_no_reason",
    "disposition": "killed",
    "cases": 17,
    "failures": [
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-dict-pool-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-dict-custom-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-sqlite-pool-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-sqlite-custom-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-dict-pool-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-dict-custom-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-sqlite-pool-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-sqlite-custom-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_candidate_does_not_block_later_legacy[connection]"
    ]
  },
  {
    "mutation": "connect_leak_link",
    "disposition": "killed",
    "cases": 17,
    "failures": [
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-dict-pool-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-dict-custom-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-sqlite-pool-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-sqlite-custom-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-dict-pool-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-dict-custom-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-sqlite-pool-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-sqlite-custom-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_candidate_does_not_block_later_legacy[connection]"
    ]
  },
  {
    "mutation": "connect_late_fetch",
    "disposition": "killed",
    "cases": 17,
    "failures": [
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-dict-pool-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-dict-custom-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-sqlite-pool-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-sqlite-custom-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-dict-pool-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-dict-custom-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-sqlite-pool-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-sqlite-custom-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_candidate_does_not_block_later_legacy[connection]"
    ]
  },
  {
    "mutation": "connect_late_missing_user",
    "disposition": "killed",
    "cases": 17,
    "failures": [
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-dict-pool-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-dict-custom-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-sqlite-pool-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-sqlite-custom-connection]"
    ]
  },
  {
    "mutation": "connect_false_success",
    "disposition": "killed",
    "cases": 17,
    "failures": [
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-dict-pool-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-dict-custom-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-sqlite-pool-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-sqlite-custom-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-dict-pool-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-dict-custom-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-sqlite-pool-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-sqlite-custom-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_candidate_does_not_block_later_legacy[connection]"
    ]
  },
  {
    "mutation": "auto_omit",
    "disposition": "killed",
    "cases": 10,
    "failures": [
      "tests.integration.test_composite_auto_renewal_guards::test_composite_auto_renewal_refused_before_effects[5000-dict]",
      "tests.integration.test_composite_auto_renewal_guards::test_composite_auto_renewal_refused_before_effects[5000-sqlite]",
      "tests.integration.test_composite_auto_renewal_guards::test_composite_auto_renewal_refused_before_effects[50000-dict]",
      "tests.integration.test_composite_auto_renewal_guards::test_composite_auto_renewal_refused_before_effects[50000-sqlite]",
      "tests.integration.test_composite_auto_renewal_guards::test_composite_auto_candidate_does_not_block_later_legacy[dict]",
      "tests.integration.test_composite_auto_renewal_guards::test_composite_auto_candidate_does_not_block_later_legacy[sqlite]"
    ]
  },
  {
    "mutation": "auto_wrong_kind",
    "disposition": "killed",
    "cases": 10,
    "failures": [
      "tests.integration.test_composite_auto_renewal_guards::test_composite_auto_renewal_refused_before_effects[5000-dict]",
      "tests.integration.test_composite_auto_renewal_guards::test_composite_auto_renewal_refused_before_effects[5000-sqlite]",
      "tests.integration.test_composite_auto_renewal_guards::test_composite_auto_renewal_refused_before_effects[50000-dict]",
      "tests.integration.test_composite_auto_renewal_guards::test_composite_auto_renewal_refused_before_effects[50000-sqlite]",
      "tests.integration.test_composite_auto_renewal_guards::test_composite_auto_candidate_does_not_block_later_legacy[dict]",
      "tests.integration.test_composite_auto_renewal_guards::test_composite_auto_candidate_does_not_block_later_legacy[sqlite]"
    ]
  },
  {
    "mutation": "auto_reject_legacy",
    "disposition": "killed",
    "cases": 10,
    "failures": [
      "tests.integration.test_composite_auto_renewal_guards::test_legacy_auto_renewal_still_debits_and_extends[legacy-dict]",
      "tests.integration.test_composite_auto_renewal_guards::test_legacy_auto_renewal_still_debits_and_extends[legacy-sqlite]",
      "tests.integration.test_composite_auto_renewal_guards::test_composite_auto_candidate_does_not_block_later_legacy[dict]",
      "tests.integration.test_composite_auto_renewal_guards::test_composite_auto_candidate_does_not_block_later_legacy[sqlite]"
    ]
  },
  {
    "mutation": "auto_reject_absent",
    "disposition": "killed",
    "cases": 10,
    "failures": [
      "tests.integration.test_composite_auto_renewal_guards::test_legacy_auto_renewal_still_debits_and_extends[None-dict]",
      "tests.integration.test_composite_auto_renewal_guards::test_legacy_auto_renewal_still_debits_and_extends[None-sqlite]"
    ]
  },
  {
    "mutation": "auto_no_reason",
    "disposition": "killed",
    "cases": 10,
    "failures": [
      "tests.integration.test_composite_auto_renewal_guards::test_composite_auto_renewal_refused_before_effects[5000-dict]",
      "tests.integration.test_composite_auto_renewal_guards::test_composite_auto_renewal_refused_before_effects[5000-sqlite]",
      "tests.integration.test_composite_auto_renewal_guards::test_composite_auto_renewal_refused_before_effects[50000-dict]",
      "tests.integration.test_composite_auto_renewal_guards::test_composite_auto_renewal_refused_before_effects[50000-sqlite]"
    ]
  },
  {
    "mutation": "auto_leak_link",
    "disposition": "killed",
    "cases": 10,
    "failures": [
      "tests.integration.test_composite_auto_renewal_guards::test_composite_auto_renewal_refused_before_effects[5000-dict]",
      "tests.integration.test_composite_auto_renewal_guards::test_composite_auto_renewal_refused_before_effects[5000-sqlite]",
      "tests.integration.test_composite_auto_renewal_guards::test_composite_auto_renewal_refused_before_effects[50000-dict]",
      "tests.integration.test_composite_auto_renewal_guards::test_composite_auto_renewal_refused_before_effects[50000-sqlite]"
    ]
  },
  {
    "mutation": "auto_late_panel",
    "disposition": "killed",
    "cases": 10,
    "failures": [
      "tests.integration.test_composite_auto_renewal_guards::test_composite_auto_renewal_refused_before_effects[5000-dict]",
      "tests.integration.test_composite_auto_renewal_guards::test_composite_auto_renewal_refused_before_effects[5000-sqlite]",
      "tests.integration.test_composite_auto_renewal_guards::test_composite_auto_renewal_refused_before_effects[50000-dict]",
      "tests.integration.test_composite_auto_renewal_guards::test_composite_auto_renewal_refused_before_effects[50000-sqlite]",
      "tests.integration.test_composite_auto_renewal_guards::test_composite_auto_candidate_does_not_block_later_legacy[dict]",
      "tests.integration.test_composite_auto_renewal_guards::test_composite_auto_candidate_does_not_block_later_legacy[sqlite]"
    ]
  },
  {
    "mutation": "auto_abort_batch",
    "disposition": "killed",
    "cases": 10,
    "failures": [
      "tests.integration.test_composite_auto_renewal_guards::test_composite_auto_candidate_does_not_block_later_legacy[dict]",
      "tests.integration.test_composite_auto_renewal_guards::test_composite_auto_candidate_does_not_block_later_legacy[sqlite]"
    ]
  },
  {
    "mutation": "renewal_abort_batch",
    "disposition": "killed",
    "cases": 17,
    "failures": [
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-dict-pool-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-sqlite-pool-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-dict-pool-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-sqlite-pool-expiry]",
      "tests.integration.test_composite_reminder_guards::test_composite_candidate_does_not_block_later_legacy[expiry]"
    ]
  },
  {
    "mutation": "volume_abort_batch",
    "disposition": "killed",
    "cases": 17,
    "failures": [
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-dict-pool-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-sqlite-pool-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-dict-pool-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-sqlite-pool-volume]",
      "tests.integration.test_composite_reminder_guards::test_composite_candidate_does_not_block_later_legacy[volume]"
    ]
  },
  {
    "mutation": "connect_abort_batch",
    "disposition": "killed",
    "cases": 17,
    "failures": [
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-dict-pool-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[1001-sqlite-pool-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-dict-pool-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_reminder_candidate_refused[None-sqlite-pool-connection]",
      "tests.integration.test_composite_reminder_guards::test_composite_candidate_does_not_block_later_legacy[connection]"
    ]
  }
]
```

Every mutant was applied independently to the passing executable reference. Relevant packet assertion failures only; no survivors/errors/skips. Source-only scratch automatically deleted. No production implementation changed.
