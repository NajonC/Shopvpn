## Rules for this job

You are the coder for the brief above. It has everything you need.

1. **Stay inside the brief.** Read the files it names, and files those import if you need to. Don't read anything else under `specs/`, `docs/`, `.specify/`, `.claude/` or `.agents/`: those files are large and you don't need them. If something seems to be missing, stop and say what.
2. **Change only the files listed under Files.** Create no other files in the repository; pytest's cache and `__pycache__` folders are fine.
3. **Tests first.** Write the listed test cases, run them and watch them fail because the code doesn't exist yet. Then write the code until they pass. If the brief says the tests are already written, don't change those files at all.
4. **Never weaken a test.** Don't change, skip, delete or loosen any existing test, don't add `skip` or `xfail` marks, and don't make a test pass by changing what it checks.
5. **Leave git alone.** `git status` and `git diff` are fine. Don't run `git add`, `commit`, `stash`, `checkout`, `restore`, `reset`, `clean` or anything else that changes git state.
6. **No network, no real services.** Don't contact real servers, VPN panels, payment services or Telegram. Don't install packages unless the brief says to, and never add a dependency it doesn't list.
7. **No real secrets.** Use the fake values from the brief, or obviously fake ones. Never print or log a token or password.
8. **Match the surrounding code**: naming, docstrings, comments and error handling.
9. **Fix nothing else.** No refactors, renames or fixes outside the brief, even if something looks wrong. Mention it in your report instead.
10. **Don't guess.** If the brief contradicts the code, is unclear or seems impossible, stop and report. Stopping with a clear question is a good result.
11. **Finish with the checks.** Run every command under "How to check", then end your reply with this report:

## Report

- Status: done | stopped (why)
- Files changed: <paths>
- Commands run: <command>: <result, with the last lines of output>
- Tests: <N> passed, <N> failed
- Assumptions: <what you decided that the brief didn't say, or "none">
- Concerns: <anything that looked wrong, or "none">
