# T048 real-code mutation evidence

Production baseline: 50 passed. All 47 behavior-changing mutants detected; no survivors or invalid runs. No reference implementation installed. Source-only scratch automatically removed.

Reproduce: `.venv/bin/python specs/001-composite-subscriptions/briefs/review/T048/verify.py`.

```json
{
  "source_revision": "774dcb5f27b266ca942f968e4243fb31b1b492db",
  "hashes": {
    "composite/service.py": "e60a307a83f38b23ad80c5e806297a345eb1c6c16ed7c17402b953e34b7813af",
    "tests/integration/test_authority_matrix.py": "2d52f54a1fd7f2480b07249d1c0ea5703fa62ab93a34f0968df30bb7eab8c671",
    "tests/unit/test_service_records.py": "66966d4ea2ab17810e3fabcf794d11b6192726c500806f380bdd7853d5a322e3",
    "specs/001-composite-subscriptions/briefs/review/T048/verify.py": "d3803c79a5cfe75506438ea37bd73540c95c32355039f2c2c8f0579d3ddbc618",
    "specs/001-composite-subscriptions/briefs/review/T047b1/verify.py": "aaa6c62581d8f3c742adad2fcbc1f98449dc9daecef7568d49ea8557efff9c6f",
    "admin_panel/server.py": "4a3b40f3d8fc2927b01e8a40c82f2dd8f660936e34af4ed099fc19267ae264a7",
    "admin_panel/security.py": "d37d94910902907f9362cca31ade66d65d7a92f88312bd3eae85abb2e6b39746"
  },
  "mutations": [
    {
      "mutation": "callback_message_actor",
      "disposition": "killed",
      "tests": [
        "test_forged_callback_actor_cannot_manage_message_actor_resource"
      ]
    },
    {
      "mutation": "payload_actor",
      "disposition": "killed",
      "tests": [
        "test_forged_callback_actor_cannot_manage_message_actor_resource"
      ]
    },
    {
      "mutation": "payload_tenant",
      "disposition": "killed",
      "tests": [
        "test_own_resources_allowed_despite_untrusted_selectors_or_buyer_status[False-False]",
        "test_own_resources_allowed_despite_untrusted_selectors_or_buyer_status[True-False]",
        "test_own_resources_allowed_despite_untrusted_selectors_or_buyer_status[False-True]",
        "test_own_resources_allowed_despite_untrusted_selectors_or_buyer_status[True-True]"
      ]
    },
    {
      "mutation": "main_tenant_hardcoded",
      "disposition": "killed",
      "tests": [
        "test_non_main_transport_cannot_manage_main_or_own_tenant_resource[own]",
        "test_non_main_transport_cannot_manage_main_or_own_tenant_resource[foreign]"
      ]
    },
    {
      "mutation": "missing_actor_fallback",
      "disposition": "killed",
      "tests": [
        "test_missing_authenticated_sender_never_falls_back_to_payload_or_message[None]",
        "test_missing_authenticated_sender_never_falls_back_to_payload_or_message[sender1]"
      ]
    },
    {
      "mutation": "omit_customer_ownership",
      "disposition": "killed",
      "tests": [
        "test_forged_callback_actor_cannot_manage_message_actor_resource"
      ]
    },
    {
      "mutation": "omit_resource_tenant",
      "disposition": "killed",
      "tests": [
        "test_cross_tenant_resource_refused_even_when_customer_ids_match"
      ]
    },
    {
      "mutation": "allow_non_main",
      "disposition": "killed",
      "tests": [
        "test_non_main_transport_cannot_manage_main_or_own_tenant_resource[foreign]"
      ]
    },
    {
      "mutation": "omit_domain",
      "disposition": "killed",
      "tests": [
        "test_matching_numeric_id_cannot_replace_customer_domain_interface_or_role[identity_domain-web_admin]",
        "test_matching_numeric_id_cannot_replace_customer_domain_interface_or_role[identity_domain-subscription_url]"
      ]
    },
    {
      "mutation": "omit_interface",
      "disposition": "killed",
      "tests": [
        "test_matching_numeric_id_cannot_replace_customer_domain_interface_or_role[authenticated_interface-miniapp]"
      ]
    },
    {
      "mutation": "omit_role",
      "disposition": "killed",
      "tests": [
        "test_matching_numeric_id_cannot_replace_customer_domain_interface_or_role[role-owner]"
      ]
    },
    {
      "mutation": "reverse_ownership",
      "disposition": "killed",
      "tests": [
        "test_own_resources_allowed_despite_untrusted_selectors_or_buyer_status[False-False]",
        "test_own_resources_allowed_despite_untrusted_selectors_or_buyer_status[True-False]",
        "test_own_resources_allowed_despite_untrusted_selectors_or_buyer_status[False-True]",
        "test_own_resources_allowed_despite_untrusted_selectors_or_buyer_status[True-True]"
      ]
    },
    {
      "mutation": "reject_payload_mismatch",
      "disposition": "killed",
      "tests": [
        "test_own_resources_allowed_despite_untrusted_selectors_or_buyer_status[False-False]",
        "test_own_resources_allowed_despite_untrusted_selectors_or_buyer_status[True-False]",
        "test_own_resources_allowed_despite_untrusted_selectors_or_buyer_status[False-True]",
        "test_own_resources_allowed_despite_untrusted_selectors_or_buyer_status[True-True]"
      ]
    },
    {
      "mutation": "reject_reseller_buyer",
      "disposition": "killed",
      "tests": [
        "test_own_resources_allowed_despite_untrusted_selectors_or_buyer_status[True-False]",
        "test_own_resources_allowed_despite_untrusted_selectors_or_buyer_status[True-True]"
      ]
    },
    {
      "mutation": "reject_discount_buyer",
      "disposition": "killed",
      "tests": [
        "test_own_resources_allowed_despite_untrusted_selectors_or_buyer_status[False-True]",
        "test_own_resources_allowed_despite_untrusted_selectors_or_buyer_status[True-True]"
      ]
    },
    {
      "mutation": "hardcode_customer_owner",
      "disposition": "killed",
      "tests": [
        "test_ownership_is_not_hardcoded_to_fixture_actor[202]",
        "test_ownership_is_not_hardcoded_to_fixture_actor[303]"
      ]
    },
    {
      "mutation": "leak_target_in_error",
      "disposition": "killed",
      "tests": [
        "test_cross_tenant_resource_refused_even_when_customer_ids_match"
      ]
    },
    {
      "mutation": "omit_web_tenant",
      "disposition": "killed",
      "tests": [
        "test_web_signed_tenant_cannot_be_replaced_by_main_selector[reseller-owner]",
        "test_web_signed_tenant_cannot_be_replaced_by_main_selector[full-access-tenant]"
      ]
    },
    {
      "mutation": "missing_tenant_is_main",
      "disposition": "killed",
      "tests": [
        "test_web_adapter_refuses_incomplete_or_wrong_authentication_domain[missing-tenant]"
      ]
    },
    {
      "mutation": "accept_main_alias",
      "disposition": "killed",
      "tests": [
        "test_web_adapter_refuses_incomplete_or_wrong_authentication_domain[main-alias]"
      ]
    },
    {
      "mutation": "omit_web_role",
      "disposition": "killed",
      "tests": [
        "test_web_database_staff_role_cannot_be_replaced_by_signed_owner_claim[orders-permission]",
        "test_web_database_staff_role_cannot_be_replaced_by_signed_owner_claim[admin-permissions]"
      ]
    },
    {
      "mutation": "omit_mobile",
      "disposition": "killed",
      "tests": [
        "test_web_adapter_refuses_incomplete_or_wrong_authentication_domain[mobile-identity]"
      ]
    },
    {
      "mutation": "coerce_actor",
      "disposition": "killed",
      "tests": [
        "test_web_adapter_refuses_incomplete_or_wrong_authentication_domain[bool-id]"
      ]
    },
    {
      "mutation": "coerce_mapping",
      "disposition": "killed",
      "tests": [
        "test_web_mapping_must_be_explicit_valid_web_id[True]"
      ]
    },
    {
      "mutation": "omit_mapping",
      "disposition": "killed",
      "tests": [
        "test_web_telegram_owner_number_does_not_authorize_unmapped_web_owner"
      ]
    },
    {
      "mutation": "telegram_id_fallback",
      "disposition": "killed",
      "tests": [
        "test_web_telegram_owner_number_does_not_authorize_unmapped_web_owner"
      ]
    },
    {
      "mutation": "wrong_domain",
      "disposition": "killed",
      "tests": [
        "test_web_explicit_owner_mapping_preserves_web_domain_and_configured_identity[1-synthetic-main-installation]",
        "test_web_explicit_owner_mapping_preserves_web_domain_and_configured_identity[2-synthetic-main-second]"
      ]
    },
    {
      "mutation": "wrong_interface",
      "disposition": "killed",
      "tests": [
        "test_web_explicit_owner_mapping_preserves_web_domain_and_configured_identity[1-synthetic-main-installation]",
        "test_web_explicit_owner_mapping_preserves_web_domain_and_configured_identity[2-synthetic-main-second]"
      ]
    },
    {
      "mutation": "wrong_role",
      "disposition": "killed",
      "tests": [
        "test_web_explicit_owner_mapping_preserves_web_domain_and_configured_identity[1-synthetic-main-installation]",
        "test_web_explicit_owner_mapping_preserves_web_domain_and_configured_identity[2-synthetic-main-second]"
      ]
    },
    {
      "mutation": "hardcode_web_actor",
      "disposition": "killed",
      "tests": [
        "test_web_explicit_owner_mapping_preserves_web_domain_and_configured_identity[2-synthetic-main-second]"
      ]
    },
    {
      "mutation": "hardcode_installation",
      "disposition": "killed",
      "tests": [
        "test_web_explicit_owner_mapping_preserves_web_domain_and_configured_identity[2-synthetic-main-second]"
      ]
    },
    {
      "mutation": "reject_alternative_owner",
      "disposition": "killed",
      "tests": [
        "test_web_explicit_owner_mapping_preserves_web_domain_and_configured_identity[2-synthetic-main-second]"
      ]
    },
    {
      "mutation": "leak_web_id",
      "disposition": "killed",
      "tests": [
        "test_web_telegram_owner_number_does_not_authorize_unmapped_web_owner"
      ]
    },
    {
      "mutation": "trust_query_tenant",
      "disposition": "killed",
      "tests": [
        "test_web_signed_tenant_cannot_be_replaced_by_main_selector[reseller-owner]",
        "test_web_signed_tenant_cannot_be_replaced_by_main_selector[full-access-tenant]"
      ]
    },
    {
      "mutation": "trust_signed_role",
      "disposition": "killed",
      "tests": [
        "test_web_database_staff_role_cannot_be_replaced_by_signed_owner_claim[orders-permission]",
        "test_web_database_staff_role_cannot_be_replaced_by_signed_owner_claim[admin-permissions]"
      ]
    },
    {
      "mutation": "omit_session_signature",
      "disposition": "killed",
      "tests": [
        "test_web_invalid_session_never_reaches_principal_or_effect[tampered]"
      ]
    },
    {
      "mutation": "omit_session_expiry",
      "disposition": "killed",
      "tests": [
        "test_web_invalid_session_never_reaches_principal_or_effect[expired]"
      ]
    },
    {
      "mutation": "allow_inactive_session",
      "disposition": "killed",
      "tests": [
        "test_web_invalid_session_never_reaches_principal_or_effect[inactive]"
      ]
    },
    {
      "mutation": "mutable_Principal",
      "disposition": "killed",
      "tests": [
        "test_authenticated_principal_cannot_be_reassigned_after_authorization"
      ]
    },
    {
      "mutation": "mutable_CommandContext",
      "disposition": "killed",
      "tests": [
        "test_command_context_retains_private_reason_but_excludes_it_from_repr"
      ]
    },
    {
      "mutation": "mutable_CommandResult",
      "disposition": "killed",
      "tests": [
        "test_result_preserves_distinct_progress_without_claiming_confirmation[pending]",
        "test_result_preserves_distinct_progress_without_claiming_confirmation[partial]",
        "test_result_preserves_distinct_progress_without_claiming_confirmation[uncertain]",
        "test_result_preserves_distinct_progress_without_claiming_confirmation[confirmed]"
      ]
    },
    {
      "mutation": "expose_private_reason",
      "disposition": "killed",
      "tests": [
        "test_command_context_retains_private_reason_but_excludes_it_from_repr"
      ]
    },
    {
      "mutation": "claim_confirmed",
      "disposition": "killed",
      "tests": [
        "test_result_preserves_distinct_progress_without_claiming_confirmation[pending]",
        "test_result_preserves_distinct_progress_without_claiming_confirmation[partial]",
        "test_result_preserves_distinct_progress_without_claiming_confirmation[uncertain]"
      ]
    },
    {
      "mutation": "reset_clock",
      "disposition": "killed",
      "tests": [
        "test_result_retains_original_clocks_restrictions_and_qualified_progress"
      ]
    },
    {
      "mutation": "drop_restrictions",
      "disposition": "killed",
      "tests": [
        "test_result_retains_original_clocks_restrictions_and_qualified_progress"
      ]
    },
    {
      "mutation": "drop_usage_qualification",
      "disposition": "killed",
      "tests": [
        "test_result_retains_original_clocks_restrictions_and_qualified_progress"
      ]
    },
    {
      "mutation": "accept_private_result_field",
      "disposition": "killed",
      "tests": [
        "test_general_result_has_no_raw_private_or_url_delivery_field[audit_reason]"
      ]
    }
  ]
}
```

Final full offline suite: **3014 passed, 68 declared T049 failures**, 602 warnings in 605.37 seconds. XML failure identities exactly equal `expected_failures.json`; all messages are missing `admin_panel.server.create_composite_router`. Zero errors/skips/regressions. No production/test modifications between check launch and acceptance. Targeted 50 passes and legacy auth 16 passes independently reproduced.
