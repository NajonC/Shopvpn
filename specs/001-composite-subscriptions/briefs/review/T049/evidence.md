# T049 actual-code mutation evidence

95 production authority/configuration cases pass. All 34 behavior-changing mutants detected by relevant assertions. No references, survivors or invalid final runs. Scratch automatically removed.

Reproduce: `.venv/bin/python specs/001-composite-subscriptions/briefs/review/T049/verify.py`.

```json
{
  "source_revision": "4b0b49575be8b53fd9aa1f7c18e6be798f4802b1",
  "hashes": {
    "admin_panel/server.py": "ee9c2dc47c30d7c4a502e6a6f4b57ecfe93343f1468a7e601703da8c1bef7511",
    "composite/service.py": "e60a307a83f38b23ad80c5e806297a345eb1c6c16ed7c17402b953e34b7813af",
    "admin_panel/security.py": "d37d94910902907f9362cca31ade66d65d7a92f88312bd3eae85abb2e6b39746",
    "tests/integration/test_authority_matrix.py": "2d52f54a1fd7f2480b07249d1c0ea5703fa62ab93a34f0968df30bb7eab8c671",
    "tests/integration/test_composite_router.py": "9028e28b3a33979b6b9513e326102001a55e7302c7297923d01768925143aff3",
    "specs/001-composite-subscriptions/briefs/review/T049/verify.py": "8fa56737b55939113fb214c6d8c828109ba7ed5c6c0571dd8303c0b1b7e4de2c"
  },
  "mutations": [
    {
      "mutation": "leak_bearer",
      "disposition": "killed",
      "tests": [
        "test_http_bearers_rejected_before_any_database_change[GET-False-mobile]",
        "test_http_bearers_rejected_before_any_database_change[GET-False-subscription]",
        "test_http_bearers_rejected_before_any_database_change[GET-True-mobile]",
        "test_http_bearers_rejected_before_any_database_change[GET-True-subscription]",
        "test_http_bearers_rejected_before_any_database_change[POST-False-mobile]",
        "test_http_bearers_rejected_before_any_database_change[POST-False-subscription]",
        "test_http_bearers_rejected_before_any_database_change[POST-True-mobile]",
        "test_http_bearers_rejected_before_any_database_change[POST-True-subscription]"
      ]
    },
    {
      "mutation": "leak_cookie",
      "disposition": "killed",
      "tests": [
        "test_http_cookie_mutations_require_origin_and_session_csrf[missing-origin-POST]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[missing-origin-PUT]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[missing-origin-PATCH]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[missing-origin-DELETE]"
      ]
    },
    {
      "mutation": "unguarded_router",
      "disposition": "killed",
      "tests": [
        "test_http_router_refuses_roles_tenants_and_unmapped_owner[GET-orders-staff]",
        "test_http_router_refuses_roles_tenants_and_unmapped_owner[GET-admin-staff]",
        "test_http_router_refuses_roles_tenants_and_unmapped_owner[GET-full-access-reseller]",
        "test_http_router_refuses_roles_tenants_and_unmapped_owner[GET-telegram-number-overlap]",
        "test_http_router_refuses_roles_tenants_and_unmapped_owner[POST-orders-staff]",
        "test_http_router_refuses_roles_tenants_and_unmapped_owner[POST-admin-staff]",
        "test_http_router_refuses_roles_tenants_and_unmapped_owner[POST-full-access-reseller]",
        "test_http_router_refuses_roles_tenants_and_unmapped_owner[POST-telegram-number-overlap]"
      ]
    },
    {
      "mutation": "omit_role_guards",
      "disposition": "killed",
      "tests": [
        "test_http_router_refuses_roles_tenants_and_unmapped_owner[GET-orders-staff]",
        "test_http_router_refuses_roles_tenants_and_unmapped_owner[GET-admin-staff]",
        "test_http_router_refuses_roles_tenants_and_unmapped_owner[POST-orders-staff]",
        "test_http_router_refuses_roles_tenants_and_unmapped_owner[POST-admin-staff]"
      ]
    },
    {
      "mutation": "omit_tenant_guards",
      "disposition": "killed",
      "tests": [
        "test_http_router_refuses_roles_tenants_and_unmapped_owner[GET-full-access-reseller]",
        "test_http_router_refuses_roles_tenants_and_unmapped_owner[POST-full-access-reseller]"
      ]
    },
    {
      "mutation": "omit_owner_mapping",
      "disposition": "killed",
      "tests": [
        "test_http_router_refuses_roles_tenants_and_unmapped_owner[GET-telegram-number-overlap]",
        "test_http_router_refuses_roles_tenants_and_unmapped_owner[POST-telegram-number-overlap]"
      ]
    },
    {
      "mutation": "late_bearer_refusal",
      "disposition": "killed",
      "tests": [
        "test_http_bearers_rejected_before_any_database_change[GET-False-mobile]",
        "test_http_bearers_rejected_before_any_database_change[GET-True-mobile]",
        "test_http_bearers_rejected_before_any_database_change[POST-False-mobile]",
        "test_http_bearers_rejected_before_any_database_change[POST-True-mobile]"
      ]
    },
    {
      "mutation": "case_sensitive_bearer",
      "disposition": "killed",
      "tests": [
        "test_http_bearers_rejected_before_any_database_change[GET-False-mobile]",
        "test_http_bearers_rejected_before_any_database_change[GET-False-subscription]",
        "test_http_bearers_rejected_before_any_database_change[GET-True-mobile]",
        "test_http_bearers_rejected_before_any_database_change[GET-True-subscription]",
        "test_http_bearers_rejected_before_any_database_change[POST-False-mobile]",
        "test_http_bearers_rejected_before_any_database_change[POST-False-subscription]",
        "test_http_bearers_rejected_before_any_database_change[POST-True-mobile]",
        "test_http_bearers_rejected_before_any_database_change[POST-True-subscription]"
      ]
    },
    {
      "mutation": "omit_origin",
      "disposition": "killed",
      "tests": [
        "test_http_cookie_mutations_require_origin_and_session_csrf[missing-origin-POST]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[missing-origin-PUT]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[missing-origin-PATCH]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[missing-origin-DELETE]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[foreign-origin-POST]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[foreign-origin-PUT]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[foreign-origin-PATCH]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[foreign-origin-DELETE]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[null-origin-POST]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[null-origin-PUT]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[null-origin-PATCH]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[null-origin-DELETE]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[http-origin-POST]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[http-origin-PUT]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[http-origin-PATCH]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[http-origin-DELETE]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[port-origin-POST]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[port-origin-PUT]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[port-origin-PATCH]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[port-origin-DELETE]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[suffix-origin-POST]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[suffix-origin-PUT]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[suffix-origin-PATCH]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[suffix-origin-DELETE]"
      ]
    },
    {
      "mutation": "origin_from_host",
      "disposition": "killed",
      "tests": [
        "test_http_cookie_mutations_require_origin_and_session_csrf[foreign-origin-POST]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[foreign-origin-PUT]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[foreign-origin-PATCH]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[foreign-origin-DELETE]"
      ]
    },
    {
      "mutation": "origin_prefix_match",
      "disposition": "killed",
      "tests": [
        "test_http_cookie_mutations_require_origin_and_session_csrf[suffix-origin-POST]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[suffix-origin-PUT]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[suffix-origin-PATCH]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[suffix-origin-DELETE]"
      ]
    },
    {
      "mutation": "omit_csrf",
      "disposition": "killed",
      "tests": [
        "test_http_cookie_mutations_require_origin_and_session_csrf[missing-csrf-POST]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[missing-csrf-PUT]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[missing-csrf-PATCH]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[missing-csrf-DELETE]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[wrong-csrf-POST]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[wrong-csrf-PUT]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[wrong-csrf-PATCH]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[wrong-csrf-DELETE]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[other-session-csrf-POST]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[other-session-csrf-PUT]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[other-session-csrf-PATCH]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[other-session-csrf-DELETE]"
      ]
    },
    {
      "mutation": "unbound_csrf",
      "disposition": "killed",
      "tests": [
        "test_http_cookie_mutations_require_origin_and_session_csrf[other-session-csrf-POST]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[other-session-csrf-PUT]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[other-session-csrf-PATCH]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[other-session-csrf-DELETE]"
      ]
    },
    {
      "mutation": "post_only_csrf",
      "disposition": "killed",
      "tests": [
        "test_http_cookie_mutations_require_origin_and_session_csrf[missing-origin-PATCH]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[foreign-origin-PATCH]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[null-origin-PATCH]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[http-origin-PATCH]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[port-origin-PATCH]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[suffix-origin-PATCH]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[missing-csrf-PATCH]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[wrong-csrf-PATCH]",
        "test_http_cookie_mutations_require_origin_and_session_csrf[other-session-csrf-PATCH]"
      ]
    },
    {
      "mutation": "csrf_on_get",
      "disposition": "killed",
      "tests": [
        "test_http_router_allows_explicit_main_owner[GET-1]",
        "test_http_router_allows_explicit_main_owner[GET-2]"
      ]
    },
    {
      "mutation": "reject_second_mapped_owner",
      "disposition": "killed",
      "tests": [
        "test_http_router_allows_explicit_main_owner[GET-2]",
        "test_http_router_allows_explicit_main_owner[POST-2]",
        "test_http_router_allows_explicit_main_owner[PUT-2]",
        "test_http_router_allows_explicit_main_owner[PATCH-2]",
        "test_http_router_allows_explicit_main_owner[DELETE-2]"
      ]
    },
    {
      "mutation": "omit_signature",
      "disposition": "killed",
      "tests": [
        "test_http_router_requires_valid_session[tampered]"
      ]
    },
    {
      "mutation": "omit_expiry",
      "disposition": "killed",
      "tests": [
        "test_http_router_requires_valid_session[expired]"
      ]
    },
    {
      "mutation": "omit_active",
      "disposition": "killed",
      "tests": [
        "test_http_router_requires_valid_session[inactive]"
      ]
    },
    {
      "mutation": "optional_cookie",
      "disposition": "killed",
      "tests": [
        "test_http_router_requires_valid_session[missing]"
      ]
    },
    {
      "mutation": "url_bearer_as_authority",
      "disposition": "killed",
      "tests": [
        "test_http_bearers_rejected_before_any_database_change[GET-False-subscription]",
        "test_http_bearers_rejected_before_any_database_change[GET-True-subscription]",
        "test_http_bearers_rejected_before_any_database_change[POST-False-subscription]",
        "test_http_bearers_rejected_before_any_database_change[POST-True-subscription]"
      ]
    },
    {
      "mutation": "omit_mount",
      "disposition": "killed",
      "tests": [
        "test_real_app_mounts_configured_empty_scaffold[None-None-200]"
      ]
    },
    {
      "mutation": "ignore_configured_owner",
      "disposition": "killed",
      "tests": [
        "test_real_app_mounts_configured_empty_scaffold[None-None-200]"
      ]
    },
    {
      "mutation": "infer_missing_owner",
      "disposition": "killed",
      "tests": [
        "test_real_app_mounts_configured_empty_scaffold[COMPOSITE_MAIN_OWNER_WEB_ADMIN_ID-None-503]"
      ]
    },
    {
      "mutation": "infer_missing_installation",
      "disposition": "killed",
      "tests": [
        "test_real_app_mounts_configured_empty_scaffold[COMPOSITE_MAIN_INSTALLATION_ID-None-503]"
      ]
    },
    {
      "mutation": "infer_missing_origin",
      "disposition": "killed",
      "tests": [
        "test_real_app_mounts_configured_empty_scaffold[COMPOSITE_PUBLIC_ORIGIN-None-503]"
      ]
    },
    {
      "mutation": "permit_invalid_config",
      "disposition": "killed",
      "tests": [
        "test_invalid_trusted_config_fails_closed[settings0]",
        "test_invalid_trusted_config_fails_closed[settings1]",
        "test_invalid_trusted_config_fails_closed[settings2]",
        "test_invalid_trusted_config_fails_closed[settings3]",
        "test_invalid_trusted_config_fails_closed[settings4]",
        "test_invalid_trusted_config_fails_closed[settings5]",
        "test_invalid_trusted_config_fails_closed[settings6]",
        "test_invalid_trusted_config_fails_closed[settings7]",
        "test_invalid_trusted_config_fails_closed[settings8]",
        "test_invalid_trusted_config_fails_closed[settings9]",
        "test_invalid_trusted_config_fails_closed[settings10]",
        "test_invalid_trusted_config_fails_closed[settings11]",
        "test_invalid_trusted_config_fails_closed[settings12]",
        "test_invalid_trusted_config_fails_closed[settings13]",
        "test_invalid_trusted_config_fails_closed[settings14]"
      ]
    },
    {
      "mutation": "change_principal_installation",
      "disposition": "killed",
      "tests": [
        "test_real_app_mounts_configured_empty_scaffold[None-None-200]"
      ]
    },
    {
      "mutation": "wrong_handoff_principal",
      "disposition": "killed",
      "tests": [
        "test_real_app_mounts_configured_empty_scaffold[None-None-200]"
      ]
    },
    {
      "mutation": "reject_nondefault_ports",
      "disposition": "killed",
      "tests": [
        "test_valid_configured_origin_preserves_nondefault_ports[https://panel.example.invalid:8443]",
        "test_valid_configured_origin_preserves_nondefault_ports[http://127.0.0.1:8002]"
      ]
    },
    {
      "mutation": "malformed_origin_host",
      "disposition": "killed",
      "tests": [
        "test_invalid_trusted_config_fails_closed[settings12]",
        "test_invalid_trusted_config_fails_closed[settings13]"
      ]
    },
    {
      "mutation": "allow_default_port_origin",
      "disposition": "killed",
      "tests": [
        "test_invalid_trusted_config_fails_closed[settings14]"
      ]
    },
    {
      "mutation": "non_ascii_csrf_authorized",
      "disposition": "killed",
      "tests": [
        "test_non_ascii_csrf_is_sanitized_refusal"
      ]
    },
    {
      "mutation": "non_ascii_session_wrong_status",
      "disposition": "killed",
      "tests": [
        "test_non_ascii_session_is_unauthenticated[\"body.\\\\377\"]",
        "test_non_ascii_session_is_unauthenticated[\"\\\\377.signature\"]"
      ]
    }
  ]
}
```
