## Rules for this job

You are the coder for the brief above. It has everything you need.

1. **Stay inside the brief.** Read the files it names, and files those import if you need to. Don't read anything else under `specs/`, `docs/`, `.specify/`, `.claude/` or `.agents/`: those files are large and you don't need them. If something seems to be missing, stop and say what.
2. **Change only the files listed under Files.** Create no other files in the repository; pytest's cache and `__pycache__` folders are fine.
3. **Tests first.** Write the tests assigned to you and check they fail for the intended missing behavior, then implement until they pass when implementation is in scope. If tests are already written, run them but never change them.
   - **Test-only packets:** stop after writing and running the assigned tests; the production implementation/DDL belongs to a later task. Report failing test IDs and reasons, distinguishing intended missing behavior from fixture, collection or assertion errors. Do not add production stubs, skips or fake passing implementations to make this packet green. Missing tables or `NotImplementedError` alone do not establish test quality: the orchestrator independently validates against a reference and mutations before acceptance.
   - **Characterization tests** are different. When the brief says its tests characterize existing code, that code is already there and you write no code: the tests must pass against it as it is. Fake only what the brief says to fake; the code under test runs for real. If a test fails because the code does something other than the brief says, don't change the expected value and don't touch the code: stop and report what the code actually does.
4. **Never weaken a test.** Don't change, skip, delete or loosen any existing test, don't add `skip` or `xfail` marks, and don't make a test pass by changing what it checks. If an existing test fails because of what the brief asks for, and the brief doesn't say that test was changed for this job, leave it as it is: stop and report the test and the conflict.
5. **Leave git alone.** `git status` and `git diff` are fine. Don't run `git add`, `commit`, `stash`, `checkout`, `restore`, `reset`, `clean` or anything else that changes git state.
6. **No network, no real services.** Don't contact real servers, VPN panels, payment services or Telegram. Don't install packages unless the brief says to, and never add a dependency it doesn't list.
7. **No real secrets.** Use the fake values from the brief, or obviously fake ones. Never print or log a token or password.
8. **Match the surrounding code**: naming, docstrings, comments and error handling.
9. **Fix nothing else.** No refactors, renames or fixes outside the brief, even if something looks wrong. Mention it in your report instead.
10. **Don't guess.** If the brief contradicts the code, is unclear or seems impossible, stop and report. Stopping with a clear question is a good result.
    Do the work yourself; do not start subagents, child tasks or new threads. Do not inspect or edit the orchestrator's reviewer-only reference/mutation artifacts unless the brief explicitly permits a particular file.
11. **Finish with the checks.** Run every command under "How to check", then end your reply with this report:

## Report

- Status: done | stopped (why)
- Files changed: <paths>
- Commands run: <command>: <result, with the last lines of output>
- Tests: <N> passed, <N> failed
- Expected pending failures: <test IDs/reasons and implementing task from the brief, or "none">
- Unexpected failures: <test IDs/reasons, or "none">
- Assumptions: <what you decided that the brief didn't say, or "none">
- Concerns: <anything that looked wrong, or "none">
