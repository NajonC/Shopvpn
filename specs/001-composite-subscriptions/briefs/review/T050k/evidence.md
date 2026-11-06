# T050k renewal verification

Hashes:
```json
{
  "miniapp/server.py": "63b15cf1f0ae0940dfc2085544b096b3e73ae778c94102488a8e485f7aa99cbc",
  "renewal_engine.py": "a664dabf8310e7b2fed69f127658e81cf2d36c18956e26ce33773256bbbd467a",
  "tests/integration/test_composite_miniapp_renewal_guards.py": "9af2ef76ce863eac419c9abeb7349f6ffbcafcab8fdc4a10fa4ff9e85aabe044",
  "tests/characterization/test_unsupported_surfaces.py": "4dee58c924d83f592f2c76dd71626addea7774f69f91bb219d3b1c38710e4bfd",
  "tests/characterization/test_legacy_renewal_reminders.py": "84722b6b10d9fbdae768cb5fb8e8fbc3490b3a213575196210a56401c6e61ea3"
}
```

Results:
```json
[
  {
    "name": "reference",
    "disposition": "pass",
    "cases": 122,
    "failed_test_ids": []
  },
  {
    "name": "omit",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-custom-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-custom-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-order-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-order-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-parent_product-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-parent_product-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-selected-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-selected-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-custom-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-custom-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-custom-100000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-custom-100000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-order-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-order-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-order-100000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-order-100000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-parent_product-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-parent_product-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-parent_product-100000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-parent_product-100000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-selected-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-selected-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-selected-100000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-selected-100000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-request-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-request-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-request-100000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-request-100000-sqlite]"
    ]
  },
  {
    "name": "wrong_kind",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-custom-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-custom-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-order-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-order-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-parent_product-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-parent_product-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-selected-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-selected-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-custom-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-custom-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-custom-100000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-custom-100000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-order-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-order-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-order-100000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-order-100000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-parent_product-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-parent_product-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-parent_product-100000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-parent_product-100000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-selected-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-selected-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-selected-100000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-selected-100000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-request-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-request-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-request-100000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-request-100000-sqlite]"
    ]
  },
  {
    "name": "bypass_api_custom_config_renewal_full_plans",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-custom-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-custom-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-order-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-order-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-parent_product-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-parent_product-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-selected-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-selected-30000-sqlite]"
    ]
  },
  {
    "name": "bypass_api_custom_config_renew_full",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-custom-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-custom-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-custom-100000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-custom-100000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-order-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-order-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-order-100000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-order-100000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-parent_product-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-parent_product-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-parent_product-100000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-parent_product-100000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-selected-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-selected-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-selected-100000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-selected-100000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-request-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-request-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-request-100000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-request-100000-sqlite]"
    ]
  },
  {
    "name": "omit_custom",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-custom-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-custom-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-custom-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-custom-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-custom-100000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-custom-100000-sqlite]"
    ]
  },
  {
    "name": "omit_parent_order",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-order-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-order-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-order-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-order-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-order-100000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-order-100000-sqlite]"
    ]
  },
  {
    "name": "omit_parent_product",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-parent_product-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-parent_product-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-parent_product-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-parent_product-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-parent_product-100000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-parent_product-100000-sqlite]"
    ]
  },
  {
    "name": "omit_plan_products",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-selected-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-selected-30000-sqlite]"
    ]
  },
  {
    "name": "omit_selected",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-selected-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-selected-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-selected-100000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-selected-100000-sqlite]"
    ]
  },
  {
    "name": "omit_request",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-request-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-request-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-request-100000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-request-100000-sqlite]"
    ]
  },
  {
    "name": "reject_legacy",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[plans-30000-False-legacy-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[plans-30000-False-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[plans-30000-True-legacy-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[plans-30000-True-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-30000-False-legacy-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-30000-False-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-30000-True-legacy-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-30000-True-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-False-legacy-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-False-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-True-legacy-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-True-legacy-sqlite]"
    ]
  },
  {
    "name": "reject_absent",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[plans-30000-False-None-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[plans-30000-False-None-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[plans-30000-True-None-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[plans-30000-True-None-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-30000-False-None-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-30000-False-None-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-30000-True-None-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-30000-True-None-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-False-None-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-False-None-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-True-None-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-True-None-sqlite]"
    ]
  },
  {
    "name": "no_reason",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-custom-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-custom-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-order-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-order-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-parent_product-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-parent_product-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-selected-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-selected-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-custom-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-custom-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-custom-100000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-custom-100000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-order-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-order-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-order-100000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-order-100000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-parent_product-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-parent_product-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-parent_product-100000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-parent_product-100000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-selected-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-selected-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-selected-100000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-selected-100000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-request-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-request-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-request-100000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-request-100000-sqlite]"
    ]
  },
  {
    "name": "leak_link",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-custom-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-custom-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-order-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-order-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-parent_product-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-parent_product-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-selected-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-selected-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-custom-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-custom-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-custom-100000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-custom-100000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-order-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-order-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-order-100000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-order-100000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-parent_product-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-parent_product-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-parent_product-100000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-parent_product-100000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-selected-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-selected-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-selected-100000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-selected-100000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-request-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-request-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-request-100000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-request-100000-sqlite]"
    ]
  },
  {
    "name": "late_auth",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-custom-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-custom-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-order-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-order-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-parent_product-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-parent_product-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-selected-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-selected-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-custom-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-custom-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-custom-100000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-custom-100000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-order-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-order-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-order-100000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-order-100000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-parent_product-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-parent_product-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-parent_product-100000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-parent_product-100000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-selected-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-selected-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-selected-100000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-selected-100000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-request-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-request-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-request-100000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-request-100000-sqlite]"
    ]
  },
  {
    "name": "debit_before_refusal",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-custom-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-custom-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-order-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-order-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-parent_product-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-parent_product-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-selected-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-selected-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-custom-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-custom-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-custom-100000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-custom-100000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-order-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-order-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-order-100000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-order-100000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-parent_product-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-parent_product-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-parent_product-100000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-parent_product-100000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-selected-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-selected-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-selected-100000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-selected-100000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-request-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-request-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-request-100000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-request-100000-sqlite]"
    ]
  },
  {
    "name": "remote_before_refusal",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-custom-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-custom-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-order-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-order-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-parent_product-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-parent_product-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-selected-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[plans-selected-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-custom-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-custom-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-custom-100000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-custom-100000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-order-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-order-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-order-100000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-order-100000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-parent_product-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-parent_product-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-parent_product-100000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-parent_product-100000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-selected-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-selected-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-selected-100000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-selected-100000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-request-30000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-request-30000-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-request-100000-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_composite_miniapp_renewal_refused[checkout-request-100000-sqlite]"
    ]
  },
  {
    "name": "block_unrelated",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[plans-30000-True-None-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[plans-30000-True-None-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[plans-30000-True-legacy-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[plans-30000-True-legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_plan_quote",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[plans-30000-False-None-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[plans-30000-False-None-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[plans-30000-False-legacy-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[plans-30000-False-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[plans-30000-True-None-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[plans-30000-True-None-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[plans-30000-True-legacy-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[plans-30000-True-legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_plan_volume",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[plans-30000-False-None-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[plans-30000-False-None-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[plans-30000-False-legacy-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[plans-30000-False-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[plans-30000-True-None-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[plans-30000-True-None-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[plans-30000-True-legacy-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[plans-30000-True-legacy-sqlite]"
    ]
  },
  {
    "name": "lost_wallet_debit",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-30000-False-None-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-30000-False-None-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-30000-False-legacy-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-30000-False-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-30000-True-None-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-30000-True-None-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-30000-True-legacy-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-30000-True-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-False-None-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-False-None-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-False-legacy-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-False-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-True-None-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-True-None-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-True-legacy-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-True-legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_checkout_price",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-30000-False-None-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-30000-False-None-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-30000-False-legacy-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-30000-False-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-30000-True-None-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-30000-True-None-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-30000-True-legacy-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-30000-True-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-False-None-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-False-None-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-False-legacy-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-False-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-True-None-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-True-None-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-True-legacy-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-True-legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_renewal_target",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-30000-False-None-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-30000-False-None-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-30000-False-legacy-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-30000-False-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-30000-True-None-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-30000-True-None-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-30000-True-legacy-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-30000-True-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-False-None-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-False-None-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-False-legacy-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-False-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-True-None-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-True-None-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-True-legacy-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-True-legacy-sqlite]"
    ]
  },
  {
    "name": "lost_approval",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-False-None-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-False-None-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-False-legacy-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-False-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-True-None-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-True-None-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-True-legacy-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-True-legacy-sqlite]"
    ]
  },
  {
    "name": "lost_carryover",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-False-None-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-False-None-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-False-legacy-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-False-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-True-None-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-True-None-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-True-legacy-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-True-legacy-sqlite]"
    ]
  },
  {
    "name": "lost_full_reset",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-False-None-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-False-None-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-False-legacy-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-False-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-True-None-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-True-None-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-True-legacy-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-True-legacy-sqlite]"
    ]
  },
  {
    "name": "wrong_readback",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-False-None-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-False-None-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-False-legacy-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-False-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-True-None-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-True-None-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-True-legacy-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-True-legacy-sqlite]"
    ]
  },
  {
    "name": "lost_local_renewal",
    "disposition": "killed",
    "cases": 52,
    "failed_test_ids": [
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-False-None-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-False-None-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-False-legacy-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-False-legacy-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-True-None-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-True-None-sqlite]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-True-legacy-dict]",
      "tests.integration.test_composite_miniapp_renewal_guards::test_legacy_miniapp_renewal_preserved[checkout-100000-True-legacy-sqlite]"
    ]
  }
]
```

Independent mutants with relevant packet assertions only; no survivors/errors/skips. Real signed ownership and original legacy renewal preserved; unrelated other-panel composites do not block selected legacy plans. Source-only scratch auto-cleaned; no production edits.
