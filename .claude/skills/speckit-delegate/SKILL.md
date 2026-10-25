---
name: "speckit-delegate"
description: "Implement tasks.md by delegating the coding to a cheaper T3 child model. Claude picks a small packet of tasks, writes a brief that stands on its own, sends it to the coder (default: Antigravity Gemini 3.8 Flash High), reviews the result itself, marks the tasks [X] and commits. Use when the user asks to implement Spec Kit tasks through a child task, a delegated coder or Gemini, or to continue that loop."
argument-hint: "[auto] [scope, e.g. T013-T026 or phase 2A] [coder <providerInstanceId>/<model>]"
user-invocable: true
disable-model-invocation: false
---

# Delegated implementation

This is `/speckit-implement` with the typing done by a cheaper model. You (Claude) read the specs, decide what each piece of code must do, write that down as a brief, and check the result. The coder writes the code and tests from the brief, runs them and fixes them.

The coder never sees the spec files and never runs Spec Kit. It is cheap but weak: it can't be trusted to work through the large spec files or tasks.md on its own, and Spec Kit is installed for Claude only.

## User input

```text
$ARGUMENTS
```

All optional, in any order:

- `auto`: don't wait for the user to approve each brief. You still stop at every phase end, at blocked tasks and whenever you have a doubt. Without `auto` you're in **ask mode**: every brief waits for the user's approval.
- A scope: a task range (`T013-T026`), a phase (`phase 2A`) or one task. Default: from the first unchecked task on.
- `coder <providerInstanceId>/<model>`. Default: `antigravity/gemini-3.8-flash-high`.
- Anything else is guidance for this run.

## Files in this skill

- `brief-template.md`: the brief you fill in for each packet.
- `coder-rules.md`: standing rules and the report format. Append it unchanged to every coder prompt.

## Setup (once per session)

1. **Feature.** Run `.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks` from the repo root and take FEATURE_DIR from its output. Briefs live in `FEATURE_DIR/briefs/`.
2. **Spec Kit checks.** Read `.claude/skills/speckit-implement/SKILL.md` and do its "Pre-Execution Checks" (`before_implement` hooks) and Outline step 2 (checklist gate). This skill replaces its steps 3 and 5–8. Its step 4 (ignore files) becomes part of the first packet unless tasks.md already has a task for it.
3. **Orientation.** Read the tasks.md header (format, markers, path conventions) and plan.md's source-code layout. Everything else you read per packet.
4. **Coder.** Load the T3 tools with ToolSearch (`select:mcp__t3-code__orchestrator_capabilities,mcp__t3-code__delegate_task,mcp__t3-code__task_status`). Call `orchestrator_capabilities` with `search` set to the coder model's name and confirm its provider instance lists the model and can run child tasks. If not, stop and ask the user.
5. **Unfinished packet.** If a brief in `FEATURE_DIR/briefs/` has a Status other than `accepted`, finish that packet first. The working tree may hold that packet's files and nothing else.
   - `draft` or `approved`: continue at step 5 or step 6.
   - `delegated (round N)`: call `task_status` with the T3 task id from its Delegation log. If the child has finished, go to step 7; if it's still running, end your turn.
   - `taken over`: finish it yourself, then go to step 8.
6. **Git.** Otherwise the tree must be clean (`git status --porcelain` prints nothing). If it isn't, show the user what's there and ask; never stash or discard their work. If you're on the default branch, ask once per session whether to commit there or create a branch first.

## The packet loop

One packet at a time, in tasks.md order. Only one coder works at a time, in this same checkout, and nobody edits the checkout while it works.

### 1. Pick the packet

- Take the next unchecked task in scope. A packet is one diff you can review in one sitting: usually one task. Group only small neighbours in the same area, like creating folders, adding a dev requirements file and extending `.gitignore`.
- Split a large task by its sub-bullets into packets `T099a`, `T099b`…, and mark the task `[X]` only when all of them are accepted.
- Test tasks go before the code they test, as tasks.md orders them. A test packet is accepted when its tests exist, are collected and fail only because the behaviour isn't built yet. Committing those failing tests is expected.
- `[P]` only means order doesn't matter. Still one packet at a time.
- Don't delegate a packet that only edits Spec Kit documents under FEATURE_DIR, or one whose brief would be longer than the code. Do it yourself and go to step 8.
- **Stop and ask the user** instead of picking when the next task:
  - carries a gate or block marker (`Gate:`, `blocked until`, `BLOCKED`) that hasn't been lifted;
  - says `Requires authorization`, or needs real panels, payment services, Telegram, production data or owner evidence;
  - needs a decision the specs don't make.

  Don't skip past it unless the user says so.

### 2. Research

- Read the whole task, including its sub-bullets.
- Look up every reference in it: FR-, SC-, PR-, RD-, OQ- and other task IDs, contract and data-model sections, constitution principles. Grep for each one and read only that part; reuse what you already read for earlier packets.
- Read the code the packet changes or builds on, including earlier packets' modules and the exact legacy functions involved. Take real signatures and line numbers from the code, not from memory or the task text.
- Keep only what changes what the code must do. Leave out who decided what and when, evidence history and release checks.

### 3. Write the brief

Copy `brief-template.md` to `FEATURE_DIR/briefs/<packet-id>.md` (`T001-T004.md`, `T099.md`, `T099a.md`) and fill it in.

- **It must stand on its own.** Copy each rule the coder needs, word for word, with its source in brackets; never just name an ID. Test it: could a developer who has never seen the specs do this from the brief and the files it names? If not, add what's missing.
- **Be exact**: paths, names, signatures, table columns, constants, error types, exact expected values in the test cases, and the exact interpreter in commands (for example the project virtualenv's `python`).
- **Point into big files**: name the function and line range, not just the file.
- **Open points must say "None"** before the brief goes out. If the specs don't answer something, ask the user; the coder must never guess.
- **Keep it short.** Most briefs fit in about 150 lines. A much longer one usually means the packet is too big.

### 4. Decide who writes the tests

The coder writes the tests from the brief's case list, unless they decide any of these, in which case you write them:

- money: prices, wallet, debits, refunds, payment results;
- usage accounting: meters, allowance, accounting epochs, cutting access when data or time runs out;
- repeat safety: idempotency, duplicates, concurrency, crash ordering;
- tenant authority and secrets.

The user can override this for a packet. When you write them: put them where the brief says, run them and confirm they fail only because the behaviour isn't built yet, then `git add` them so you can see later whether the coder touched them. Fill in "Tests written by" and list the files as already written.

### 5. Approve

- **Ask mode**: show the user the brief's path and a short summary: goal, files, test cases and anything you weren't sure about. Wait, apply their changes, then set Status `approved`.
- **Auto mode**: set Status `approved` yourself, unless you have a doubt; then ask.

### 6. Delegate

1. Save the output of `git status --porcelain`; you'll compare against it.
2. Call `delegate_task`:
   - `task`: the brief without its Delegation log, followed by the full text of `coder-rules.md`;
   - `title`: `<packet-id>: <short title>`;
   - `target`: `{"providerInstanceId": …, "model": …}` for the coder;
   - `role`: `implementation`, `mode`: `async`; leave `isolation` and `runtimeMode` unset (shared checkout, inherited mode);
   - `clientRequestId`: `<FEATURE_DIR name>-<packet-id>-r<round>`, e.g. `001-composite-subscriptions-T099-r1`. Reuse it only to retry that same round.
3. Check the returned provider and model are the coder's. Add a row to the Delegation log (round, T3 task id) and set Status `delegated (round N)`.
4. Tell the user in one line what's running and end your turn. Don't poll; T3 wakes this thread when the child finishes.

If the child asks a question, answer it from the specs with the pending-request tools (`t3_pending_request_read`, `t3_pending_request_respond`, with the child's thread id) if you can, and add the answer to the brief; otherwise ask the user. If it waits on an approval, tell the user to answer it in the child's thread.

### 7. Review

When the child finishes, check everything yourself; never take its report on trust.

1. Read its report. If it stopped, read why. If the brief was missing something, fix the brief and start a new round; that round doesn't count toward the limit below.
2. Compare `git status --porcelain` with your snapshot. Only the files the brief lists may be new or changed. If you wrote the tests, `git diff --name-only -- <test files>` must print nothing; anything there means the coder changed them.
3. Run the brief's "How to check" commands yourself. Once the test harness exists, also run the full offline suite from FEATURE_DIR/quickstart.md. New tests must pass, and nothing that passed before may fail.
4. Read every changed line and every new file:
   - each rule in the brief is implemented, and nothing outside it was done;
   - each listed test case exists and really checks the stated result: no `assert True`, no mocking of the code under test, no added `skip` or `xfail`, no loosened existing test;
   - no network calls, real-looking secrets, logged tokens, or dependencies the brief doesn't list;
   - it reads like the surrounding code.
5. Decide:
   - **Accept** when everything passes. You may fix small, obvious things yourself instead of spending a round (a missing import, a name, a typo; roughly 10 lines at most). Note them in the log.
   - **New round** otherwise. Write the findings in the log, then call `delegate_task` again with round N+1 and its own clientRequestId. Send the brief, a "Round N+1: what to fix" section listing each problem with file and line, the line "Your previous attempt is still in the working tree. Fix it; don't start over.", and `coder-rules.md`. If the attempt is too broken to fix, first move it aside with `git stash push -u -m "<packet-id> round N rejected" -- <paths the coder changed>`, and tell the coder it starts fresh instead.
   - **Take over** after two coder rounds that still fail: set Status `taken over`, finish the packet yourself, and note it in the log.

### 8. Accept and commit

1. Mark the packet's finished tasks `[X]` in tasks.md. Set the brief's Status `accepted` and complete its log.
2. Stage exactly the packet's files, its brief and tasks.md, by name; never `git add -A`.
3. Commit on the current branch. `<feature>` is FEATURE_DIR's name without its number, e.g. `composite-subscriptions`:

   ```text
   feat(<feature>): <packet-id> <what was built>

   Brief: <FEATURE_DIR>/briefs/<packet-id>.md
   Coder: <providerInstanceId>/<model>, <N> round(s)[; Claude fixes: …][; finished by Claude]
   ```

   Use `test(<feature>)` for a packet that only adds tests. A packet you did yourself gets `Done by Claude` instead of the Brief and Coder lines. Follow the session's attribution rules.
4. Tell the user in one line: packet, result, commit hash.

### 9. Next

- **Ask mode**: research and write the next brief, then ask for approval (step 5).
- **Auto mode**: go on to the next packet.
- **Always stop** when the scope is done, at a stop condition from step 1, and at the end of each tasks.md phase. At a phase end, run the full suite, list what was built, the packets you took over and the concerns from the coder's reports, and wait for the user.

## When every task is done

Do `/speckit-implement`'s step 9 (completion validation) and its "Mandatory Post-Execution Hooks" yourself, then report.

## Never

- Point the coder at the spec files or ask it to run a Spec Kit command.
- Let the coder near real panels, payment services, Telegram, production data or secrets.
- Run two coders at once in this checkout, or edit it while one is working.
- Mark a task `[X]` you haven't verified.
- Discard or stash anything that isn't the coder's own work.
