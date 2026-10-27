# Effort per task

The reasoning effort to run Claude at for each packet of `specs/001-composite-subscriptions/tasks.md`, set on 2026-10-26 from a review of every unchecked task. Steps 1 and 9 of SKILL.md name a packet's level so the user can run its session at that effort.

- A sub-packet (`T086a`) has its task's level. A packet that groups several tasks gets the highest of their levels.
- For a task that isn't listed (added later, for example by `/speckit-converge`), choose with the rules below and tell the user the level and the reason.

## Rules

**xhigh** when the packet has any of these:

1. races between processes, crash/restart ordering, or one transaction that must write several records together;
2. the hard rule sets: RX-01 retries and quarantine, the descriptor-discrepancy, move and leak rules (RD05-OWN-002), and the usage-accounting core (epochs, deltas, boundary readings, cutoff);
3. changes to how legacy code moves money, takes locks, or restores or deletes data;
4. crypto code or the authority boundary;
5. a first test packet whose pattern later ones copy: T013 (first Telegram-handler characterization), T069 (the payment test kit every Phase 14 method reuses), T110 (first acceptance test file);
6. a final review whose whole job is finding gaps: T245, T264.

**high** for other behaviour work: characterizing legacy code (a wrong test fails against the real code), schema copied from data-model.md, routes and handlers, keeping secrets out of logs, money rules the spec gives worked examples for, and code whose hard part an earlier xhigh test packet already pinned.

**medium** for screens that only show what the server returns, Telegram texts, docs, mechanical snapshots, small additions to an existing feature, service units, and recording lab results.

Never **low**: it is too thin for the review, where the coder's mistakes are caught. Never **max**: split the task instead. T086, T103, T181 and T183 split into sub-packets by their bullets, and T245 by constitution principle.

## Levels

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

## Notes

- Later acceptance files (T128, T140, T160, T180, T189) are high: their edge cases are in the same story's xhigh tests, and the spec scenarios they run have exact values.
- Notifications and reminders (T091, T108, T204–T206) are high: a bug sends a duplicate or late message; it doesn't touch money or access.
- T059, T061 and T066 are high: the spec gives worked examples (100 → 81, 30 + 73 = 103), and the race side of money is in T060 and T062–T065.
- T044 is high but T045 is xhigh: crypto mistakes often still pass standard tests.
- Phase 16 runs checks designed earlier, so it is high by default. T249 (lab harness code for the RX-01 re-run), T255 (the largest campaign, with the connection-value change path) and T264 are the exceptions.

## Coder

A packet uses SKILL.md's default coder, `antigravity/gemini-3.8-flash-high`, unless this section names another. The user's `coder` argument wins over both. Luna, `codex/gpt-6-luna`, runs at `reasoningEffort` `xhigh` (SKILL.md step 6).

- **Phase 2A** (characterization; owner decision 2026-10-27): Luna for T013–T018, T020, T021, T023 and T026–T031; Gemini for T019, T022, T024 and T025. Luna writes all the tests of its packets (SKILL.md step 4). T023 and T029 span many files: split them into sub-packets by file.
- **Phase 2B onwards** (owner decision 2026-10-27): Luna for packets whose level is xhigh, Gemini for high and medium. Claude still writes the step 4 test groups, so Luna writes code against Claude's tests.
