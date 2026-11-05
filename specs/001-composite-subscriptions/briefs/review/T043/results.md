# T043 mutation evidence

Reviewed implementation: base revision `f38a1cd0f3608e083cf2daac6d91c810939316b1` plus the T043 packet diff. This is offline predicate evidence, not remote enforcement or release acceptance.

- Python: project `.venv/bin/python`, Python 3.12.3.
- Reproduce from repository root: `.venv/bin/python specs/001-composite-subscriptions/briefs/review/T043/mutate.py`.
- The runner copies only the explicitly listed pure source, tests and offline harness into a unique `/tmp/shopvpn-t043-mutations-*` directory, verifies the import path, and removes that directory on exit. It does not copy databases, configuration, credentials or git metadata.
- Every mutant starts from the same unchanged production source. Scoped replacements assert match counts, produce a non-identical source, and compile. Each test run uses a fresh process and synthetic fixture state, disabled bytecode writing, and `--network=deny`.
- Unmodified baseline and restored final source: **179 passed** each.
- Final dispositions: **71 killed, 1 proven equivalent, 0 unresolved/invalid**. Kills below are relevant assertion failures or failed immutability exception expectations; setup/import/syntax errors are rejected by the runner.
- First run: 69 killed, 2 survivors, 1 equivalent. Survivors were `publication-omit-initial-cancel` and `publication-ignore-fulfillment`. The orchestrator added three cases for the independently specified initial-cancellation gate and the no-recognized-phase fallback. All three fail against pre-packet production only because `publication` is absent; all pass against the real implementation. The second campaign killed both mutants. No production edit was required.
- The equivalent empty-attachment guard removal still reaches `qualifying_count == 0` and returns UNKNOWN: summing an empty generator produces zero. `confirmation-unknown-is-partial` independently proves the underlying zero-match rule is tested, and the empty-evidence cases explicitly assert UNKNOWN.
- Scratch cleanup completed, including the separate pre-packet check of the three new cases.

## Hashes

- `composite/models.py`: `172136ed720f5730405fd4f3d3b8bd164979a81a8022a7b3e38a0615649c28bc`
- `tests/unit/test_models_predicates.py`: `975b411a62a3d84fae24cfa5e7b1e79db5301e13fea32b94d56f93492bdcbfd6`
- `specs/001-composite-subscriptions/briefs/review/T043/mutate.py`: `ca549d72749a361ded97b4e82ac159ab6543b17c684abcbcf212e8f9e4cc9c1a`

## Per-rule outcomes

All test names below are in `tests/unit/test_models_predicates.py`. The runner stops each mutant at its first relevant assertion failure; other cases may also detect it.

| Mutation | Disposition | Detecting test / proof |
| --- | --- | --- |
| `expiry-equality` | killed | `test_expired_from_the_common_expiry[at_expiry]` |
| `expiry-overstrict` | killed | `test_expired_from_the_common_expiry[before]` |
| `expiry-None` | killed | `test_no_expiry_date_is_not_expired` |
| `expiry-epoch-zero` | killed | `test_no_expiry_date_is_not_expired` |
| `quota-equality` | killed | `test_exhausted_at_or_above_the_purchased_bytes[at_threshold]` |
| `quota-overstrict` | killed | `test_exhausted_at_or_above_the_purchased_bytes[one_byte_left]` |
| `access-deny-setup` | killed | `test_access_does_not_require_publication_or_completed_replacement[False-False-preparing]` |
| `access-deny-fulfilled` | killed | `test_fulfilled_service_has_access` |
| `access-allow-CANCELLED` | killed | `test_terminal_lifecycle_denies_access_independently_of_flags[cancelled]` |
| `access-allow-FAILED_UNFULFILLED` | killed | `test_terminal_lifecycle_denies_access_independently_of_flags[failed_unfulfilled]` |
| `access-allow-initial-cancel` | killed | `test_initial_cancellation_denies_access_even_without_delivery_flag[False-False]` |
| `access-deny-renewal-wait` | killed | `test_pending_cancellation_during_authorized_renewal_keeps_access` |
| `access-omit-final` | killed | `test_no_access_after_final_cancellation_or_failed_initial[final_after_renewal]` |
| `access-omit-initial` | killed | `test_each_phase_respects_each_independent_access_restriction[initial_block-fulfilled]` |
| `access-omit-customer` | killed | `test_each_restriction_alone_removes_access[customer_disabled]` |
| `access-omit-owner` | killed | `test_each_restriction_alone_removes_access[owner_suspended]` |
| `access-omit-reporting` | killed | `test_each_restriction_alone_removes_access[reporting_suspended]` |
| `access-omit-recovery` | killed | `test_each_restriction_alone_removes_access[recovery_hold]` |
| `access-omit-expired` | killed | `test_each_restriction_alone_removes_access[expired]` |
| `access-omit-exhausted` | killed | `test_each_restriction_alone_removes_access[exhausted]` |
| `access-final-epoch-zero` | killed | `test_each_phase_respects_each_independent_access_restriction[final_at_epoch-fulfilled]` |
| `access-require-publication` | killed | `test_access_does_not_require_publication_or_completed_replacement[False-False-fulfilled]` |
| `access-require-availability` | killed | `test_access_does_not_require_publication_or_completed_replacement[False-False-preparing]` |
| `access-require-replacement` | killed | `test_access_does_not_require_publication_or_completed_replacement[False-True-fulfilled]` |
| `publication-allow-REVOKED` | killed | `test_invalid_token_or_final_cancellation_is_not_found[revoked]` |
| `publication-allow-SUPERSEDED` | killed | `test_invalid_token_or_final_cancellation_is_not_found[superseded]` |
| `publication-allow-CANCELLED` | killed | `test_terminal_publication_precedes_all_other_gates[candidate-cancelled]` |
| `publication-allow-FAILED_UNFULFILLED` | killed | `test_failed_initial_never_serves_entries[failed_unfulfilled]` |
| `publication-omit-final` | killed | `test_invalid_token_or_final_cancellation_is_not_found[final_after_renewal]` |
| `publication-omit-candidate` | killed | `test_candidate_token_is_unavailable[changes0]` |
| `publication-omit-preparing` | killed | `test_gate_two_precedes_owner_status[preparing]` |
| `publication-omit-initial-cancel` | killed | `test_initial_cancellation_blocks_publication_independently_of_delivery_flag[True]` |
| `publication-omit-initial-block` | killed | `test_gate_two_precedes_owner_status[initial_block]` |
| `publication-omit-replacement` | killed | `test_blocked_or_incomplete_delivery_is_unavailable[replacement_pending]` |
| `publication-omit-recovery` | killed | `test_blocked_or_incomplete_delivery_is_unavailable[recovery_hold]` |
| `publication-final-epoch-zero` | killed | `test_terminal_publication_precedes_all_other_gates[candidate-final_at_epoch]` |
| `publication-owner-first` | killed | `test_invalid_token_or_final_cancellation_is_not_found[revoked_owner_suspended]` |
| `publication-owner-needs-generation` | killed | `test_owner_suspension_is_status_only[no_published_generation]` |
| `publication-omit-owner` | killed | `test_owner_suspension_is_status_only[owner_suspended]` |
| `publication-ignore-generation` | killed | `test_blocked_or_incomplete_delivery_is_unavailable[no_published_generation]` |
| `publication-ignore-fulfillment` | killed | `test_unrecognized_cancellation_phase_does_not_publish_a_complete_list` |
| `publication-deny-renewal-wait` | killed | `test_complete_list_is_kept_through_ordinary_restrictions[renewal_wait]` |
| `publication-restrict-customer` | killed | `test_complete_list_is_kept_through_ordinary_restrictions[customer_disabled]` |
| `publication-restrict-reporting` | killed | `test_complete_list_is_kept_through_ordinary_restrictions[reporting_suspended]` |
| `publication-restrict-exhaustion` | killed | `test_complete_list_is_kept_through_ordinary_restrictions[exhausted]` |
| `publication-restrict-expiry` | killed | `test_complete_list_is_kept_through_ordinary_restrictions[expired]` |
| `confirmation-remove-empty-guard` | equivalent | Equivalent: sum of empty evidence is zero, and the later qualifying_count == 0 guard returns UNKNOWN before any confirmation. |
| `confirmation-freshness-equality` | killed | `test_no_matching_read_back_after_the_latest_write_is_unknown[disabled-none]` |
| `confirmation-ignore-freshness` | killed | `test_no_matching_read_back_after_the_latest_write_is_unknown[disabled-none]` |
| `confirmation-ignore-mismatch` | killed | `test_no_matching_read_back_after_the_latest_write_is_unknown[disabled-none]` |
| `confirmation-missing-is-match` | killed | `test_no_matching_read_back_after_the_latest_write_is_unknown[disabled-none]` |
| `confirmation-unknown-is-partial` | killed | `test_no_matching_read_back_after_the_latest_write_is_unknown[disabled-none]` |
| `confirmation-any-is-enough` | killed | `test_some_attachments_matching_is_partial[disabled-one_unread]` |
| `confirmation-partial-is-unknown` | killed | `test_some_attachments_matching_is_partial[disabled-one_unread]` |
| `confirmation-ignore-runtime` | killed | `test_runtime_evidence_where_required[disabled]` |
| `confirmation-always-require-runtime` | killed | `test_matching_read_back_after_the_latest_write_confirms[disabled]` |
| `confirmation-runtime-partial-is-unknown` | killed | `test_runtime_evidence_where_required[disabled]` |
| `confirmation-ignore-requests` | killed | `test_request_that_could_undo_the_state_blocks_until_its_quarantine_ends[enable_while_disabled]` |
| `confirmation-first-request-only` | killed | `test_one_blocking_request_among_harmless_ones_blocks` |
| `confirmation-same-state-blocks` | killed | `test_request_that_cannot_undo_the_state_does_not_block[same_enabled]` |
| `confirmation-reducing-state-blocks` | killed | `test_request_that_cannot_undo_the_state_does_not_block[delete_while_denied]` |
| `confirmation-any-reducing-request-harmless` | killed | `test_request_that_could_undo_the_state_blocks_until_its_quarantine_ends[disable_while_enabled]` |
| `confirmation-quarantine-equality` | killed | `test_request_that_could_undo_the_state_blocks_until_its_quarantine_ends[enable_while_disabled]` |
| `confirmation-expired-request-blocks` | killed | `test_request_that_could_undo_the_state_blocks_until_its_quarantine_ends[enable_while_disabled]` |
| `confirmation-harmless-request-blocks` | killed | `test_request_that_cannot_undo_the_state_does_not_block[same_enabled]` |
| `confirmation-quarantine-partial-is-unknown` | killed | `test_request_that_could_undo_the_state_blocks_until_its_quarantine_ends[enable_while_disabled]` |
| `confirmation-enabled-is-denied` | killed | `test_matching_read_back_after_the_latest_write_confirms[enabled]` |
| `confirmation-denied-is-eligible` | killed | `test_matching_read_back_after_the_latest_write_confirms[disabled]` |
| `mutable-SubscriptionAccessFacts` | killed | `test_fact_types_are_frozen_and_have_these_fields` |
| `mutable-AttachmentReadBack` | killed | `test_facts_and_evidence_are_immutable_and_predicates_do_not_mutate_them` |
| `mutable-UncertainRequest` | killed | `test_facts_and_evidence_are_immutable_and_predicates_do_not_mutate_them` |
| `mutable-ChildAccessEvidence` | killed | `test_facts_and_evidence_are_immutable_and_predicates_do_not_mutate_them` |
