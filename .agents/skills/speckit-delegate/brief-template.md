# Brief <packet-id>: <short title>

- **Status**: draft
- **Tasks**: <task IDs>
- **Packet type**: characterization | test-only | implementation | mechanical
- **Orchestrator**: <actual model/effort; recommended model/effort and reason if different>
- **Coder**: <providerInstanceId>/<model>
- **Coder options**: <explicit supported settings; Luna reasoningEffort=xhigh unless overridden>
- **Tests written by**: coder | orchestrator (<reason, e.g. money: refund amounts>)

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

<If the orchestrator wrote them: "Already written and staged. Don't change them: `<path>`, …">

File: `<path>`

1. `<test_name>`: given …; when …; then … <exact values>.

## How to check

<Exact commands, run from the repo root, and what each must show.>

<For test-only packets: identify each intended missing-behavior failure and its later implementation task. Reference/mutation acceptance belongs to the orchestrator. For all packets: list any accepted pending failures outside scope by ID/reason, not just counts.>

<Expected working-tree status before delegation, including the brief and pre-existing orchestrator/user edits. These are not permission to change those files.>

## Out of scope

<What the coder might be tempted to do but must not: later tasks, refactors, fixes to unrelated code.>

## Open points

None.

---

## Reviewer verification

Everything from this heading onward is for the orchestrator only; exclude it from the coder prompt. Never record secrets.

- **Baseline**: <source revision, passing suites, pending failure IDs/reasons and implementing tasks>
- **Protected files**: <orchestrator-owned tests and unrelated changes; hashes/diff snapshot>
- **Source review**: <authoritative sections checked independently of the brief; omissions or contradictions resolved>
- **Reference**: <needed for test-only packets; path and supporting stand-ins, or reason not applicable>
- **Artifacts**: <FEATURE_DIR/briefs/review/packet-id/ files owned by the orchestrator, or none>

| Source rule | Required valid/invalid behavior | Test IDs | Mutation and relevant expected failure | Final disposition/evidence |
| --- | --- | --- | --- | --- |
| <source> | <boundary, allowed update, refusal, combination> | <IDs> | <loosening and over-strict variants as applicable> | <pending initially; killed or justified equivalent at acceptance> |

- **Results**: <production checks; reference pass count; mutation counts by disposition; equivalence reasoning; no unresolved required checks at acceptance>
- **Corrections**: <brief gaps, fixture errors, missing cases, implementation issues, or none>
- **Reproduce**: <exact interpreter/commands, source/artifact hashes, scratch setup; never depend solely on a /tmp path>
- **Cleanup**: <scratch deleted; reusable source artifacts retained>
- **Next**: <packet; orchestrator model/effort; coder/options; reason; verification/artifacts; blockers>

## Delegation log

Not sent to the coder. Record actual settings, returned task/thread link and continuation; do not poll running tasks. Direct work uses a row with no child task.

| Round | T3 task id / child link | Actual coder/options | Result / next | Notes |
| --- | --- | --- | --- | --- |
