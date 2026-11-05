# Orchestrator and coder selection

Use **GPT-6.1 Sol for most orchestration** and reserve **GPT-6 Astra for the hardest contract design and unresolved review gaps**. These are project routing recommendations, not measured guarantees of equal reliability or subscription savings. Both models must meet `verification.md`.

Select three things separately: the orchestrator model/effort, the coder model/options, and the required verification. An Astra recommendation does not automatically choose Luna; a Sol packet does not get weaker verification.

## Orchestrator routing

1. The user's explicit settings win. Otherwise use `gpt-6.1-sol` at the task's baseline effort below, then apply an Astra override if listed or justified by the escalation rules.
2. `medium` is for mechanical changes, docs, presentation and straightforward additions to established patterns. `high` is the usual behavioral review setting. `xhigh` is for well-defined but interacting rules, concurrency, crash ordering and difficult test design. Set/recommend the level explicitly rather than relying on model defaults.
3. An implementation whose difficult design and adversarial tests are already accepted can use Sol at `high` if the packet introduces no new concurrency, authority or lifecycle semantics. Explain that choice. Otherwise keep the baseline `xhigh`. Review test quality before relying on it.
4. Sub-packets inherit the task's routing unless their actual scope justifies a different level; grouped packets take the highest required level. Split large tasks rather than defaulting to `max` or `ultra`. Do not recommend `low` for independent behavioral review. Explicit user overrides remain valid.
5. For tasks added later (for example by `$speckit-converge`) use these criteria and record the reason. Completed tasks are not reopened merely because routing changed.

### Astra overrides for this feature

Default to `gpt-6-astra` at `xhigh` for the following packets. These overrides concern the demanding design/review portion; a later implementation with a settled contract can return to Sol under rule 3.

| Task | Why Astra is recommended |
| --- | --- |
| T043 | T042's accepted brief leaves five behavior questions unresolved. Settle access/publication/confirmation semantics before delegating; its reference choices are not approval. |
| T045, T047 | Cryptographic behavior and the first composite authority matrix; happy-path tests can conceal boundary errors. |
| T054 | First cross-process maintenance/restore-incarnation contract and crash cases. |
| T064, T067, T069 | Receipt settlement identities and concurrent outcomes, financial crash boundaries, and the reusable payment contract test kit. |
| T086, T088–T090 | RX-01 quarantine and late reversals, terminal revocation ordering, accounting epochs and cross-process panel lock coverage. |
| T142 | Renewal boundary attribution with delayed readings and worker failures. |
| T161, T162 | Cancellation clocks and refunds, leak revocation and publication interleavings. |
| T181 | Moves interacting with pending replacements, discrepancies and inactive subscriptions; split by scenario family. |
| T190, T193, T198 | Coherent restore, uncertain/newer history and actual restore replacement/caller integration. |
| T245, T264 | Final implementation and release gap review across contracts; split T245 by principle. Evidence/authorization gates still apply. |

Other packets, including most `xhigh` entries below, remain Sol by default. For T043 the initial recommendation is **Astra/xhigh, Gemini Flash High coder**: its baseline is `high`, so the existing coder policy still selects Gemini. Resolve T042's open decisions and complete the brief first. If this packet has already been completed, recommend the actual next unchecked task instead.

### Escalation and session handoff

Escalate a packet's recommendation to Astra/xhigh when source rules conflict, security/financial/recovery semantics remain ambiguous, or a reference/mutation survivor exposes an interaction the current orchestrator cannot explain. First inspect the failure: a missing import, fixture typo or routine coder mistake is a local fix, not an escalation. For large work, split by rules or sub-bullets before increasing model cost.

Do not bring Astra in as a second reviewer for every Sol packet. One orchestrator owns the packet. If an escalation is needed, save a compact handoff in the brief: exact unresolved rules, relevant source locations, test/mutation IDs, existing artifacts and work completed. Do not mark it accepted. Recommend the user's next session settings; do not spawn an orchestrator, create a thread or pretend to switch your own model. If the user explicitly chooses to continue with the current model, continue the investigation with unchanged acceptance requirements.

At selection and handoff report the **recommended** model/effort and reason. In the brief/report record the **actual** model/effort from runtime metadata when known, otherwise say unknown. An Astra session can finish an ordinary Sol-recommended packet without restarting merely to match this table. Existing user permission to keep going is not revoked by a recommendation.

## Baseline task effort

The table preserves the 2026-10-26 task assessment for `specs/001-composite-subscriptions/tasks.md`. It supplies Sol's initial effort and preserves the 2026-10-27 coder allocation. Orchestrator overrides above do not change that allocation. It is a starting assessment; packet-specific evidence and user instructions take precedence.

### Baseline criteria

**xhigh** when the packet has any of these:

1. races between processes, crash/restart ordering, or one transaction that must write several records together;
2. the hard rule sets: RX-01 retries and quarantine, the descriptor-discrepancy, move and leak rules (RD05-OWN-002), and the usage-accounting core (epochs, deltas, boundary readings, cutoff);
3. changes to how legacy code moves money, takes locks, or restores or deletes data;
4. crypto code or the authority boundary;
5. a first test packet whose pattern later ones copy: T013 (first Telegram-handler characterization), T069 (the payment test kit every Phase 14 method reuses), T110 (first acceptance test file);
6. a final review whose whole job is finding gaps: T245, T264.

**high** for other behaviour work: characterizing legacy code (a wrong test fails against the real code), schema copied from data-model.md, routes and handlers, keeping secrets out of logs, money rules the spec gives worked examples for, and code whose hard part an earlier xhigh test packet already pinned.

**medium** for screens that only show what the server returns, Telegram texts, docs, mechanical snapshots, small additions to an existing feature, service units, and recording lab results.

Split T086, T103, T181 and T183 into sub-packets by their bullets, and T245 by constitution principle.

### Levels

† = blocked by a gate or needs the owner's authorization; step 1 stops there anyway.

| Phase | xhigh | high | medium |
| --- | --- | --- | --- |
| 2A characterization | T013, T016 | T014, T015, T017, T018, T020, T021, T023, T024, T026, T027, T029–T031 | T019, T022, T025, T028 |
| 2B schema | T032–T035 | T036–T041 | |
| 2C types, authority, guards | T042, T045, T047–T049 | T043, T044, T046, T050–T053 | |
| 2D control, worker, CLI | T054–T057 | T058 | |
| 3 finance core | T060, T062–T065, T067–T069, T071–T079, T081 | T059, T061, T066, T070, T080 | |
| 4 remote, accounting | T084–T086, T088–T090, T093, T095, T097†, T100–T103, T105, T106 | T082†, T087, T091, T094, T096, T098, T099, T104, T107–T109 | T083, T092 |
| 5 US1 purchase | T110, T111, T114, T119–T121, T123, T124 | T112, T113, T115, T116, T118, T122, T125, T126 | T117, T127 |
| 6 US2 allowance | T129–T131, T133, T134, T136 | T128, T132, T137, T138 | T135, T139 |
| 7 US3 renewal | T141–T143, T145–T148, T150 | T140, T144, T149 | |
| 8 US4 tests, campaign | T152, T155, T157 | T151, T153, T158, T159 | T154, T156 |
| 9 US5 controls | T161–T163, T166, T168–T170, T172 | T160, T164, T165, T167 | T171 |
| 10 US6 list | T173 | T174–T176, T178 | T177, T179 |
| 11 US7 moves | T181–T184, T186 | T180, T185, T188 | T187 |
| 12 US8 recovery | T190, T193–T196, T198–T201 | T189, T191, T192, T197 | T202, T203 |
| 13 US9 reminders | | T204–T206 | T207 |
| 14 payments† | T209–T214, T216–T236 | T208, T215 (not gated) | |
| 15 polish | T241, T245 | T238, T242, T243 | T237, T239, T240, T244 |
| 16 release† | T249, T255, T264 | T247, T248, T250, T251, T253, T254, T256, T258–T262 | T246, T252, T257, T263 |

### Notes

- Later acceptance files (T128, T140, T160, T180, T189) are high: their edge cases are in the same story's xhigh tests, and the spec scenarios they run have exact values.
- Notifications and reminders (T091, T108, T204–T206) are high: a bug sends a duplicate or late message; it doesn't touch money or access.
- T059, T061 and T066 are high: the spec gives worked examples (100 → 81, 30 + 73 = 103), and the race side of money is in T060 and T062–T065.
- T044 is high but T045 is xhigh: crypto mistakes often still pass standard tests.
- Phase 16 runs checks designed earlier, so it is high by default. T249 (lab harness code for the RX-01 re-run), T255 (the largest campaign, with the connection-value change path) and T264 are the exceptions.

## Coder

A packet uses SKILL.md's default coder, `antigravity/gemini-3.8-flash-high`, unless this section names another. The user's `coder` argument wins over both. Luna, `codex/gpt-6-luna`, runs at `reasoningEffort` `xhigh` (SKILL.md step 6).

- **Phase 2A** (characterization; owner decision 2026-10-27): Luna for T013–T018, T020, T021, T023 and T026–T031; Gemini for T019, T022, T024 and T025. Luna writes all the tests of its packets (SKILL.md step 4). T023 and T029 span many files: split them into sub-packets by file.
- **Phase 2B onwards** (owner decision 2026-10-27): Luna for packets whose **baseline table level** is xhigh, Gemini for high and medium. Orchestrator effort changes or Astra overrides do not silently change this choice. The orchestrator still writes the step 4 sensitive test groups. For an unlisted task, classify its baseline using the criteria above, then choose the coder separately from any Astra escalation.

Pass Luna's `reasoningEffort: "xhigh"` in `target.options` even when the parent runs at medium/high. For `antigravity/gemini-3.8-flash-high`, High is part of the model ID; pass only options the capability tool actually lists. A user-specified coder/effort wins. An unavailable requested provider/model must be reported, never substituted without the user's choice.

## Verification is independent of effort

Apply `verification.md` based on the packet's behavior. All test-only packets need a passing reference and rule-based mutations; characterization needs the specified behavioral mutations; critical implementations need mutations against the real code. Medium effort does not exempt a sensitive rule, and xhigh alone does not require mutation tests for a documentation-only review. Keep the actual reasoning and acceptance evidence in the brief so future routing can improve from observed gaps.
