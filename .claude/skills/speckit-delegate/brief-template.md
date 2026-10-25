# Brief <packet-id>: <short title>

- **Status**: draft
- **Tasks**: <task IDs>
- **Coder**: <providerInstanceId>/<model>
- **Tests written by**: coder | Claude (<reason, e.g. money: refund amounts>)

<!-- Status: draft → approved → delegated (round N) → [taken over] → accepted -->

## Goal

<Two to four plain sentences: what this packet adds and where it fits in the feature.>

## What already exists

<Modules, classes and functions this packet builds on, with paths and real signatures. "Nothing yet" is fine.>

## Rules

<Numbered. Each rule copied word for word from the spec, plan, contracts or data model, with its source in brackets, e.g. [spec FR-004]. Only rules that change what the code must do.>

1. …

## Files

Create:
- `<path>`: <purpose>

Change:
- `<path>`: <what changes, with function names and line ranges>

Read only:
- `<path>` lines <a–b>: <why>

Touch nothing else.

## Interfaces

<Exact signatures, dataclasses, table columns, constants and error types the code must have.>

## Tests

<If Claude wrote them: "Already written and staged. Don't change them: `<path>`, …">

File: `<path>`

1. `<test_name>`: given …; when …; then … <exact values>.

## How to check

<Exact commands, run from the repo root, and what each must show.>

## Out of scope

<What the coder might be tempted to do but must not: later tasks, refactors, fixes to unrelated code.>

## Open points

None.

---

## Delegation log

Not sent to the coder.

| Round | T3 task id | Result | Notes |
| --- | --- | --- | --- |
