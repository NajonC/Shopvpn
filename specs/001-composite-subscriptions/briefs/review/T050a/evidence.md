# T050a reference and mutations

Source SHA256:
```json
{
  "renewal_engine.py": "a664dabf8310e7b2fed69f127658e81cf2d36c18956e26ce33773256bbbd467a",
  "stock_alerts.py": "fe0541106a094fc984f06b08cebb31264b8e5bec2dc1ae4c4a0cf6ed26440e85",
  "tests/integration/test_composite_legacy_guards.py": "03d3b03df34e4b07b6cbaac501a538df04751e36518cf7908e34813c7bde9218",
  "tests/integration/test_composite_stock_guards.py": "bf1eb3a8fd7b8bcf03916932a5bc6e4fa14aa21eb715b2398bd61466132a6eed",
  "tests/characterization/test_legacy_renewal_reminders.py": "84722b6b10d9fbdae768cb5fb8e8fbc3490b3a213575196210a56401c6e61ea3"
}
```

Results:
```json
[
  {
    "name": "reference",
    "passes": 54,
    "failed_test_ids": [],
    "disposition": "pass"
  },
  {
    "name": "manual_omit",
    "passes": 11,
    "failed_test_ids": [
      "tests.integration.test_composite_legacy_guards::test_composite_manual_renewal_refused_without_effects[custom-dict]",
      "tests.integration.test_composite_legacy_guards::test_composite_manual_renewal_refused_without_effects[custom-sqlite]",
      "tests.integration.test_composite_legacy_guards::test_composite_manual_renewal_refused_without_effects[config-dict]",
      "tests.integration.test_composite_legacy_guards::test_composite_manual_renewal_refused_without_effects[config-sqlite]"
    ],
    "disposition": "killed"
  },
  {
    "name": "manual_wrong_kind",
    "passes": 11,
    "failed_test_ids": [
      "tests.integration.test_composite_legacy_guards::test_composite_manual_renewal_refused_without_effects[custom-dict]",
      "tests.integration.test_composite_legacy_guards::test_composite_manual_renewal_refused_without_effects[custom-sqlite]",
      "tests.integration.test_composite_legacy_guards::test_composite_manual_renewal_refused_without_effects[config-dict]",
      "tests.integration.test_composite_legacy_guards::test_composite_manual_renewal_refused_without_effects[config-sqlite]"
    ],
    "disposition": "killed"
  },
  {
    "name": "manual_reject_legacy",
    "passes": 13,
    "failed_test_ids": [
      "tests.integration.test_composite_legacy_guards::test_legacy_manual_renewal_still_runs[legacy-dict]",
      "tests.integration.test_composite_legacy_guards::test_legacy_manual_renewal_still_runs[legacy-sqlite]"
    ],
    "disposition": "killed"
  },
  {
    "name": "manual_reject_absent",
    "passes": 13,
    "failed_test_ids": [
      "tests.integration.test_composite_legacy_guards::test_legacy_manual_renewal_still_runs[None-dict]",
      "tests.integration.test_composite_legacy_guards::test_legacy_manual_renewal_still_runs[None-sqlite]"
    ],
    "disposition": "killed"
  },
  {
    "name": "stock_omit",
    "passes": 13,
    "failed_test_ids": [
      "tests.integration.test_composite_stock_guards::test_composite_stock_refused_before_alert_state[dict]",
      "tests.integration.test_composite_stock_guards::test_composite_stock_refused_before_alert_state[sqlite]"
    ],
    "disposition": "killed"
  },
  {
    "name": "stock_no_reason",
    "passes": 13,
    "failed_test_ids": [
      "tests.integration.test_composite_stock_guards::test_composite_stock_refused_before_alert_state[dict]",
      "tests.integration.test_composite_stock_guards::test_composite_stock_refused_before_alert_state[sqlite]"
    ],
    "disposition": "killed"
  },
  {
    "name": "stock_leak_name",
    "passes": 13,
    "failed_test_ids": [
      "tests.integration.test_composite_stock_guards::test_composite_stock_refused_before_alert_state[dict]",
      "tests.integration.test_composite_stock_guards::test_composite_stock_refused_before_alert_state[sqlite]"
    ],
    "disposition": "killed"
  },
  {
    "name": "stock_reject_legacy",
    "passes": 12,
    "failed_test_ids": [
      "tests.integration.test_composite_stock_guards::test_legacy_low_stock_still_notifies[legacy-dict]",
      "tests.integration.test_composite_stock_guards::test_legacy_low_stock_still_notifies[legacy-sqlite]",
      "tests.integration.test_composite_stock_guards::test_legacy_stock_state_false_sends_nothing"
    ],
    "disposition": "killed"
  },
  {
    "name": "stock_reject_absent",
    "passes": 13,
    "failed_test_ids": [
      "tests.integration.test_composite_stock_guards::test_legacy_low_stock_still_notifies[None-dict]",
      "tests.integration.test_composite_stock_guards::test_legacy_low_stock_still_notifies[None-sqlite]"
    ],
    "disposition": "killed"
  },
  {
    "name": "manual_late",
    "passes": 11,
    "failed_test_ids": [
      "tests.integration.test_composite_legacy_guards::test_composite_manual_renewal_refused_without_effects[custom-dict]",
      "tests.integration.test_composite_legacy_guards::test_composite_manual_renewal_refused_without_effects[custom-sqlite]",
      "tests.integration.test_composite_legacy_guards::test_composite_manual_renewal_refused_without_effects[config-dict]",
      "tests.integration.test_composite_legacy_guards::test_composite_manual_renewal_refused_without_effects[config-sqlite]"
    ],
    "disposition": "killed"
  },
  {
    "name": "stock_late",
    "passes": 13,
    "failed_test_ids": [
      "tests.integration.test_composite_stock_guards::test_composite_stock_refused_before_alert_state[dict]",
      "tests.integration.test_composite_stock_guards::test_composite_stock_refused_before_alert_state[sqlite]"
    ],
    "disposition": "killed"
  }
]
```

All mutants independently applied to the passing reference. All failures are relevant packet assertions or the exact expected RenewalError from deliberate over-strict mutations on legacy-positive cases; no errors/skips. Scratch automatically deleted.
