---
name: "speckit-delegate"
description: "Implement Spec Kit tasks through cheaper T3 child tasks, with Codex owning the brief, sensitive tests, mutation verification and acceptance. Recommends Sol 6.1 for most orchestration and Astra for the hardest contracts. Use when the user requests delegated Spec Kit implementation or continuation of that loop; not for ordinary implementation without delegation."
---

# Delegated implementation

This is `$speckit-implement` with bounded coding packets assigned to cheaper T3 children. You, the Codex orchestrator, read the specs, design the packet and its verification, write the brief, and independently check the result. The coder implements the brief and writes only the tests assigned to it.

The coder receives no parent history, does not research the spec files and never runs Spec Kit. Keep its context small and sufficient. Model selection never lowers the acceptance standard. When the user asks to review or edit this skill, do that work only; do not start the packet loop.

## User input

Use the user's message following `$speckit-delegate` (or its named invocation). Do not require a literal `$ARGUMENTS` variable.

All optional, in any order:

- `auto`: briefs need no separate approval. Equivalent session authorization also applies. Otherwise use **ask mode** (step 5). Both modes stop at unresolved product decisions, evidence gates and phase ends; routine implementation choices are yours. Continue beyond one packet only when the user asks (step 9).
- A scope: a task range (`T013-T026`), a phase (`phase 2A`) or one task. Default: from the first unchecked task on.
- `coder <providerInstanceId>/<model>`. Default: the coder `effort.md` names for the task, otherwise `antigravity/gemini-3.8-flash-high`.
- Anything else is guidance for this run.

## Files in this skill

- [brief-template.md](brief-template.md): the brief you fill in for each packet.
- [coder-rules.md](coder-rules.md): standing rules and the report format. Append it unchanged to every coder prompt.
- [effort.md](effort.md): orchestrator model and effort, independent coder settings, task overrides and escalation rules. Read when selecting or handing off a packet.
- [verification.md](verification.md): required reference and mutation checks, acceptance by packet type, and reusable evidence. Read when designing tests and reviewing a behavioral packet.

## Setup (once per session)

1. **Feature.** Run `.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks` from the repo root and take FEATURE_DIR from its output. Briefs live in `FEATURE_DIR/briefs/`.
2. **Spec Kit checks.** Read [the installed Codex implementation skill](../speckit-implement/SKILL.md) and do its "Pre-Execution Checks" (`before_implement` hooks) and Outline step 2 (read-only checklist gate). This skill replaces its steps 3 and 5–8. Its step 4 (ignore files) becomes part of the first packet unless tasks.md already has a task for it. Invoke required hooks through their installed Codex skills/tools; printing a command is not execution. If the skill moved, locate its installed replacement; do not silently omit its gates.
3. **Orientation.** Read the tasks.md header (format, markers, path conventions) and plan.md's source-code layout. Everything else you read per packet.
4. **T3 tools.** Discover the available `orchestrator_capabilities`, `delegate_task`, `task_status`, `task_cancel` and pending-request tools using the harness's tool catalog (`ALL_TOOLS` in Codex code-mode). Do not hard-code a provider namespace or require Claude ToolSearch. Call `orchestrator_capabilities` once per thread before the first delegation; reuse it unless an error or user-named provider change requires another call. Confirm the selected coder and its options are supported and its provider can run children. If unavailable, report that and ask for a choice; never silently substitute a model or CLI. This skill explicitly uses T3 `delegate_task`, including for Luna.
5. **Unfinished packet.** If a brief in `FEATURE_DIR/briefs/` has a Status other than `accepted`, finish that packet first. Preserve its baseline and any unrelated user work.
   - `draft` or `approved`: revalidate its open points, baseline and verification plan against the current checkout, then continue at step 5 or step 6. Older briefs may need the reviewer section added before delegation.
   - `delegated (round N)`: follow the saved T3 continuation and completion notification. Read `task_status` only after completion wakes you; never use it to poll a running child. With no completion evidence, leave the packet pending rather than launch a duplicate. A task from another parent may require the user's original thread to resume it.
   - `taken over`: finish it yourself, perform step 7 verification, then go to step 8.
6. **Git.** Snapshot status, staged/unstaged diffs and relevant file hashes before packet edits. Preserve unrelated changes and exclude them from the packet commit; ask only when overlapping work has unclear ownership. Follow existing branch and commit authorization; if the default-branch choice is unresolved, ask once whether to use it or a new branch. Do not repeat an already answered question.

## The packet loop

One packet at a time, in tasks.md order. Only one coder works at a time, in this same checkout. The orchestrator makes only the step 6 delegation-log entry while the coder runs; other edits wait for it to stop.

### 1. Pick the packet

- Take the next unchecked task in scope. A packet is one diff you can review in one sitting: usually one task. Group only small neighbours in the same area, like creating folders, adding a dev requirements file and extending `.gitignore`.
- Split a large task by its sub-bullets into packets `T099a`, `T099b`…, and mark the task `[X]` only when all of them are accepted.
- Test tasks go before the code they test, as tasks.md orders them. Expected failing tests may be committed only after the test-only reference and mutation checks in `verification.md`; missing tables or methods alone are insufficient evidence.
- A characterization task (Phase 2A) records what existing code does today. Its tests must pass against today's code at once, and the coder changes nothing outside `tests/`. Say in the brief's Goal that the tests characterize existing code, so the coder follows that part of coder rule 3.
- `[P]` only means order doesn't matter. Still one packet at a time.
- Don't delegate a packet that only edits Spec Kit documents under FEATURE_DIR, or one whose brief would be longer than the code. Do it yourself, perform the applicable step 7 checks, then go to step 8. Direct work and takeovers have the same acceptance requirements.
- **Stop and ask the user** instead of picking when the next task:
  - carries a gate or block marker (`Gate:`, `blocked until`, `BLOCKED`) that hasn't been lifted;
  - says `Requires authorization` that has not been given, or needs real panels, payment services, Telegram, production data or owner evidence beyond the authorized scope;
  - needs an unresolved product or authority decision the specs don't make.

  Don't skip past it unless the user says so.
- Before deep research, name the packet, recommended orchestrator model/effort, coder model/options, verification type and routing reason from `effort.md`. Record the actual orchestrator separately. A recommendation does not switch this session's model; see that file for escalation and handoff behavior.

### 2. Research

- Read the whole task, including its sub-bullets.
- Look up every reference in it: FR-, SC-, PR-, RD-, OQ- and other task IDs, contract and data-model sections, constitution principles. Grep for each one and read only that part; reuse what you already read for earlier packets.
- Read the code the packet changes or builds on, including earlier packets' modules and the exact legacy functions involved. Take real signatures and line numbers from the code, not from memory or the task text.
- Find the existing tests that check that code: the task's `Tests:` line names the Phase 2A suites it touches (`characterization T016` means T016's test file), and grep `tests/` for the functions the packet changes. Put them in the brief's "How to check" so the coder runs them too. Most must keep passing as they are; if the specs make the packet change what one of them checks, step 4 says what to do.
- Record the test baseline: passing suites and any previously accepted test-only failures, by test ID and missing behavior. Review source requirements for missing brief rules, including valid cases that must remain allowed; do not derive the verification checklist only from your own brief. Keep evidence gates visible, but omit unrelated history from the coder prompt.

### 3. Write the brief

Copy `brief-template.md` to `FEATURE_DIR/briefs/<packet-id>.md` (`T001-T004.md`, `T099.md`, `T099a.md`) and fill it in.

- **It must stand on its own.** Copy each rule the coder needs, word for word, with its source in brackets; never just name an ID. Test it: could a developer who has never seen the specs do this from the brief and the files it names? If not, add what's missing.
- **Be exact**: paths, names, signatures, table columns, constants, error types, exact expected values in the test cases, and the exact interpreter in commands (for example the project virtualenv's `python`).
- **Point into big files**: name the function and line range, not just the file.
- **Open points must say "None"** before the brief goes out. Resolve routine choices from the requirements and code. If a product or authority decision remains unspecified, ask the user; neither a reference implementation nor a model recommendation authorizes inventing it.
- **Keep it short.** Most briefs fit in about 150 lines. A much longer one usually means the packet is too big.
- **Expected `git status` output includes your own files.** The brief file is untracked until the packet is committed, and the test files you wrote or changed (and implementation-review.md, if step 4 changed it) are staged, so list them as already there. Otherwise a careful coder sees an unexpected line and stops.
- **Reread it for contradictions before it goes out.** Every rule must agree with the Files entries, examples, interfaces and checks. When a rule says one thing and an example shows another, the coder has to guess or stop.
- **Plan verification now.** Fill the reviewer-only section of `brief-template.md` using `verification.md`. Declare packet type, source-to-test mapping, expected failures, required mutations and reusable artifact paths. Keep this section out of the coder prompt.

### 4. Decide who writes the tests

The coder writes the tests from the brief's case list, unless the tests decide any of these, in which case you write them:

- money: prices, wallet, debits, refunds, payment results;
- usage accounting: meters, allowance, accounting epochs, cutting access when data or time runs out;
- repeat safety: idempotency, duplicates, concurrency, crash ordering;
- tenant authority and secrets.

The user can override this for a packet. When you write them: put them where the brief says, run them and confirm they fail for the intended missing behavior (characterization tests: pass on today's code), then stage exactly those files and save their hashes so you can detect coder changes, including staged ones. Fill in "Tests written by" and list them as already written. Test-only acceptance also requires a passing reference and mutation verification, even when you wrote every test.

**Characterization packets with Luna.** When `effort.md` gives a characterization packet to `codex/gpt-6-luna`, the coder writes all its tests, the groups above included (owner decision, 2026-10-27). The groups are there mainly so a coder doesn't check its own code with its own tests; in a characterization packet the code under test is existing code that nobody changes, so a wrong expected value fails. You still design each test in the groups: the brief says what it fakes, where it breaks in and the exact values it checks, and a test that needs a valid signature or token builds one itself rather than through the code under test. Step 7 checks each one by breaking the code on purpose. With any other coder, and in every packet that adds or changes code, the groups stay yours.

**Tests a packet changes on purpose.** Phase 2A pins legacy behaviour, known bugs included, and some later tasks fix those bugs. T072, for example, makes `reject_order` commit the rejection and the refund together, so T016's case of a crash between the two, which loses the refund, no longer holds. When the specs make a packet change what an existing test checks, you change that test before delegating, whoever the coder is; the coder never does (coder rule 4).

- Change only what the specs change and keep every other check. Take the new expected values from the specs, never from what the new code does. Delete a case only when nothing it checks is left.
- Run it and confirm it fails only because the change isn't built yet. `git add` it and list it in the brief as already written, naming the cases that changed.
- If it is a Phase 2A test (`tests/characterization/`, `tests/contract/test_provider_factory_legacy.py`), also record the change under "Intended behavior differences" in `FEATURE_DIR/implementation-review.md` (the first entry replaces "None recorded."): the test and the task that wrote it, the behaviour before and after, this packet, and the spec rule that requires the change. `git add` it too. T242 checks this list when it re-runs every suite.

### 5. Approve

- **Ask mode**: prepare the complete brief and verification plan, then show its path and summarize goal, files and checks. Explain that this skill's ask mode requires brief approval. Honor existing approval for that concrete packet; otherwise wait, apply changes and set Status `approved`.
- **Auto mode**: set Status `approved` yourself when the brief is settled. Ask only for an unresolved decision or authorization, naming its source; don't ask again for actions the session already authorizes.

### 6. Delegate

1. Save status, protected file hashes and staged/unstaged diffs; status alone cannot reveal edits to an already modified file.
2. Call `delegate_task`:
   - `task`: the brief's coder-facing portion only (before `## Reviewer verification`), followed by the full text of `coder-rules.md`. For older briefs, omit the Delegation log and any reviewer-only artifacts;
   - `title`: `<packet-id>: <short title>`;
   - `target`: exact provider/model and supported settings in `target.options`. Luna uses `{"providerInstanceId":"codex","model":"gpt-6-luna","options":{"reasoningEffort":"xhigh"}}` unless the user specifies another effort. Gemini uses `antigravity/gemini-3.8-flash-high`; do not invent a separate effort option where none is listed. Never rely on the parent's inherited effort;
   - `role`: `implementation`, `mode`: `async`; leave `isolation` and `runtimeMode` unset (shared checkout, inherited mode);
   - `clientRequestId`: `<FEATURE_DIR name>-<packet-id>-r<round>`, e.g. `001-composite-subscriptions-T099-r1`. Reuse it only to retry that same round.
3. Check the returned provider, model and options. Cancel a mismatched run immediately, inspect any partial edits, and report it rather than silently accepting a different coder. Record task id, child thread link, round, settings and returned `next` in the Delegation log; set Status `delegated (round N)`. This orchestrator-owned log entry is the sole checkout edit allowed while the child runs; its brief must list that file as read-only.
4. Follow the returned `next`. When completion will wake this thread, report the returned child link verbatim and end the turn. Never poll through status, sleeps, watchers or thread waits. Cancel any running task you replace or no longer need with `task_cancel`; don't interrupt its child thread or launch another coder beside it.

If the child asks a question, use the available pending-request tool (currently `t3_pending_request`, actions `list`, `read`, `respond`, with `childThreadId`) to answer from the specs. Don't edit the shared checkout while the child runs; record the clarification in the brief once it stops. If a product decision is missing, ask the user. Pending-request responses cannot grant permissions: direct required approval to the child's returned link. Use `request_secret` for credentials only the user can provide, never chat or the brief.

### 7. Review

When the child finishes, check everything yourself; never take its report on trust.

1. Read its report. If it stopped, read why. If the brief was missing something, fix the brief and start a new round; that round doesn't count toward the limit below.
2. Compare status, both diffs and protected hashes with the snapshot. Only the brief's allowed files may differ. Orchestrator-owned tests, existing tests and unrelated user work must be unchanged by the coder, even if it staged an edit.
3. Run the brief's checks yourself, complete [verification.md](verification.md), and run the full offline suite from FEATURE_DIR/quickstart.md against the final packet. Acceptance depends on packet type: characterization and implemented behavior pass; test-only work passes against the reference and fails only as declared against current production. Previously accepted missing-behavior failures may remain only when identified in the baseline and outside this packet. No regression of passing tests is allowed. If the specs require changing a previously passing test that step 2 missed, follow step 4 and verify its new expectation fails against the pre-packet code in an external scratch copy. Record reference/mutation results and all survivor dispositions before acceptance.
4. Read every changed line and every new file:
   - each rule assigned to this packet is implemented or tested as its packet type requires, and nothing outside it was done;
   - each listed test case exists and really checks the stated result: no `assert True`, no mocking of the code under test, no added `skip` or `xfail`, no loosened existing test;
   - no network calls, real-looking secrets, logged tokens, or dependencies the brief doesn't list;
   - it reads like the surrounding code.
5. Decide:
   - **Accept** when the packet's acceptance checks are satisfied. Fix small, obvious review findings yourself rather than launching another delegate (a missing import, name or typo; roughly 10 lines). Re-run affected checks and note the fixes. A few changed lines can still represent a significant design correction; record it as such and re-check the source-to-test mapping.
   - **New round** otherwise. Write the findings in the log, then call `delegate_task` again with round N+1 and its own clientRequestId. Send only the coder-facing brief, a "Round N+1: what to fix" section listing each problem with file and line, the line "Your previous attempt is still in the working tree. Fix it; don't start over.", and `coder-rules.md`. Keep reviewer-only artifacts out. If the attempt is too broken to fix, first preserve and set aside only the coder's changes; use a path-scoped stash only where those paths contain no prior user/orchestrator edits. Otherwise isolate the coder's diff without discarding the baseline. Tell the coder whether to repair or start fresh.
   - **Take over** after two coder rounds that still fail: set Status `taken over`, finish the packet yourself, and note it in the log. Brief repairs don't count as coder failures, but after two brief-repair rounds stop delegating and diagnose the contract; split or hand off using `effort.md` rather than loop indefinitely. Escalation never waives verification.

### 8. Accept and commit

1. Mark the packet's finished tasks `[X]` in tasks.md. Set the brief's Status `accepted` and complete its log.
2. Stage exactly the packet's files, its brief, reusable review artifacts and tasks.md, plus implementation-review.md if changed, by name; never `git add -A`. Inspect the staged diff so unrelated user changes are excluded.
3. Commit on the current branch. `<feature>` is FEATURE_DIR's name without its number, e.g. `composite-subscriptions`:

   ```text
   feat(<feature>): <packet-id> <what was built>

   Brief: <FEATURE_DIR>/briefs/<packet-id>.md
   Orchestrator: <actual model>, <actual effort>
   Coder: <providerInstanceId>/<model>, <N> round(s)[; orchestrator fixes: …][; finished by orchestrator]
   ```

   Use `test(<feature>)` for tests only. A packet you did yourself keeps its verification record and uses `Coder: none; implemented by orchestrator`. Report actual known model/settings, never attribute work to a recommended model that did not run. Follow the session's attribution rules. This step commits implementation packets when authorized; editing this skill alone does not authorize a commit or a push.
4. Tell the user in one line: packet, result, commit hash.

### 9. Next

Default to one packet per session, with a compact handoff so the next session need not reread earlier transcripts. This limits context growth; actual quota savings depend on the provider and caching. The task list, briefs and reusable verification artifacts retain the state.

- Find the next unchecked task and apply `effort.md`. Save and report: `Next: <packet> | Orchestrator: <model>/<effort> | Coder: <provider/model, options> | Why: <reason> | Verification: <type/artifacts> | Blockers: <none or exact decision/gate>`. Recommend starting the next session with those settings and `$speckit-delegate`, then stop. Do not create a new thread or switch models yourself.
- If the user asked to keep going, announce the same recommendation and continue under their selected settings unless there is an unresolved escalation or gate. In ask mode obtain the next concrete brief approval; in auto mode continue directly. Model advice alone is not a new permission gate.
- **Always stop** when the scope is done, at a stop condition from step 1, and at the end of each tasks.md phase. At a phase end, run the full suite, list what was built, the packets you took over and the concerns from the coder's reports, and wait for the user.

## When every task is done

Do the installed `$speckit-implement` skill's step 9 (completion validation) and "Mandatory Post-Execution Hooks" yourself, then report. Missing-behavior test failures are no longer acceptable when their implementation tasks are complete.

## Never

- Point the coder at the spec files or ask it to run a Spec Kit command.
- Let the coder near real panels, payment services, Telegram, production data or secrets.
- Run two coders at once in this checkout, or edit it while one is working except for the step 6 delegation-log entry.
- Mark a task `[X]` you haven't verified.
- Discard or stash anything that isn't the coder's own work.
