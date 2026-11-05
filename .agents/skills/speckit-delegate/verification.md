# Packet verification

The orchestrator owns this review, including when it wrote the tests or took over the implementation. Run checks yourself; a coder report is not acceptance evidence. These checks establish offline behavior, not real-panel, payment-provider or release acceptance.

## Plan from the requirements

Before delegating, map the packet's authoritative requirements to exact test cases and observable outcomes in the brief's reviewer-only section. Read the referenced specification/contract/data-model rules independently of the brief to find omissions in your own design. Record:

- packet type: characterization, test-only, implementation or mechanical;
- valid inputs and transitions that must remain allowed, invalid ones that must be refused, exact boundary values and relevant combinations of restrictions;
- each critical rule's test and planned mutation, including protection against over-strict implementations;
- baseline passing suites and previously accepted missing-behavior failures, identified by test ID, reason and implementing task;
- reference/tooling provenance and unresolved design questions. Resolve questions before delegation; a convenient reference implementation is not a product decision.

For refusals, make every unrelated precondition valid. Otherwise a foreign key, duplicate fixture row or neighboring CHECK can mask the rule under test. For successful transitions, assert the resulting state and relevant retained history, not merely absence of an exception. Sensitive tests remain orchestrator-owned under SKILL.md step 4.

## Acceptance by packet type

### Characterization

Run the real existing behavior with only the brief's permitted external fakes. All new tests must pass against current code. In an external scratch copy, mutate each behavior pinned by a step 4 sensitive test (save ordering, filter, lock, amount, limit, authority check). Every behavior-changing mutation must be caught. Cover other material rules with targeted mutations where assertions could pass accidentally. Do not change production behavior to fit the brief; correct a mistaken characterization from actual evidence.

### Test-only, with production code or DDL scheduled later

Missing tables, missing attributes and `NotImplementedError` are expected development states, not sufficient acceptance checks. This applies to all such packets, including the T034 splits, T042, T059–T069 and T083–T091, whoever wrote them.

1. Collect the new cases against current production and verify their failures are the intended missing behavior. Record IDs/reasons; do not accept syntax, collection, fixture or unrelated assertion errors as expected failures. If an existing behavior already satisfies a case, record that justified pass rather than forcing an artificial failure.
2. In an external scratch copy, supply a minimal executable reference implementation or DDL for the packet's contract. Use the real test harness and interfaces; do not replace the function under test with canned answers. Limit the reference to this packet and its necessary dependencies. Explain any supporting stand-ins and do not count their behavior as verified production code.
3. Run **every new or changed case against the reference; all must pass**. Investigate mismatches against the requirements before changing either the reference or a test.
4. Run an automated mutation script against the reference, breaking each specified rule independently. For schema packets, cover removal/loosening of CHECK, UNIQUE, FOREIGN KEY, NOT NULL and trigger protections. For code, cover guards, amounts, boundaries, ownership, repeat safety and required ordering. Also introduce plausible over-strict variants: freezing mutable fields, an unapproved node cap, rejecting valid transitions, or preventing allowed access/publication.
5. Repair masked/missing cases and faulty setup, update the brief, then rerun the reference baseline and affected mutants. Accept only with the dispositions below. Production remains unimplemented in the real checkout; do not copy the reference there as part of a test-only task.

### Implementation

The packet's tests and intentionally revised tests must pass against the real implementation. Mutation verification is mandatory for rules involving money, usage/access, identity/authority/secrets, schema integrity, concurrency/crash ordering, lifecycle/recovery, or publication restrictions, regardless of the orchestrator's effort setting. For other behavior use targeted checks from the requirement mapping; mechanical docs/presentation work does not require a mutation campaign.

Reuse the matching test packet's mutation plan and tooling, adapting it to the actual implementation rather than only rerunning the reference. Mutate each applicable critical rule: wrong comparison boundaries, missing ownership/inbound filter, skipped lock/quarantine, duplicated credit, lost recovery obligation, negative/float acceptance, or a permitted transition wrongly refused. Use controlled interleavings or fault injection for concurrency and crash rules; ordinary timing luck is not evidence that a removed lock or reordered commit is detected.

If the earlier reference omitted a critical rule, add verification now. A green test suite or an earlier accepted test packet does not close that gap. If the contract changes with authorization, update its requirement mapping and tests before judging the code.

### Mechanical work

Review the diff and run applicable static checks. Explain briefly why no behavioral mutation applies. Do not invent behavior tests for documents, wording or formatting changes alone.

## What counts as a detected mutation

- Establish a passing unmodified baseline for the selected tests. Run each mutant from that same clean starting point with fresh synthetic state; mutations must not accumulate.
- Verify that the intended edit actually applied. Use deterministic scripts with an expected match count and a record of the changed rule. A no-op replacement is not an equivalent mutant.
- A **killed** mutant produces a relevant failed assertion or expected-behavior failure. Syntax/import errors, broken setup, unrelated missing tables, tooling failures and unexplained timeouts are invalid runs, not kills. Repair or replace invalid mutants and run again.
- A **surviving behavior-changing** mutant blocks acceptance. Add or correct the independently justified test, fix a masked precondition, or repair the implementation as appropriate, then rerun. Do not weaken requirements to improve the score.
- A **proven equivalent/redundant** mutant may survive with a written explanation grounded in the entire contract and implementation. Example: removing T034c's `quota_mode` enum CHECK changes no allowed row because the threshold CHECK already imposes the same domain. A surviving mutant is not equivalent merely because current tests pass. If redundant protections mask one another, also remove them together to verify that loss of the underlying business rule is caught.
- An unresolved, unexecuted or invalid mutation is not a pass. Split an oversized packet or escalate the unresolved reasoning; do not silently waive a required check for quota savings.

There is no minimum mutation count or blanket 100% kill-score target. The requirement mapping, relevant failures, positive cases and justified equivalences matter. A finite campaign cannot prove that no other bug exists.

## Scratch execution and durable evidence

Use a unique directory created with `mktemp -d` under `/tmp` for review execution. Export the needed source and explicitly named packet files into it, including the reviewed uncommitted changes. Do not copy `.git`, real configuration, credentials, production databases, backups or unrelated user files. Do not create a child checkout for this review: it is local orchestrator work, not another delegated task.

Use the project's recorded interpreter/dependencies, synthetic data and offline/network-denial harness. Confirm imports and database paths point into scratch. Execute mutations only in that copy; never mutate the shared checkout or its test files. Do not run review mutation work concurrently with a child writing the shared checkout.

Keep reproducible **source** artifacts at `FEATURE_DIR/briefs/review/<packet-id>/`: the reference when required, mutation definitions/runner, and only necessary injection/reproduction helpers. These are review tooling, not production implementation or release evidence. Name these files in the orchestrator-owned portion of the brief and stage them explicitly with the accepted packet. Copy them into scratch to execute. Keep the brief's review summary compact:

- source revision plus packet diff/artifact hashes and exact interpreter/commands;
- production baseline and declared pending failures;
- passing reference result when applicable;
- mutation IDs mapped to rules, relevant failing test IDs, and final dispositions (killed, justified equivalent, unresolved/invalid);
- corrections to the brief/tests, equivalence proofs, and reproduction instructions;
- scratch cleanup outcome and the next packet that should reuse the artifacts.

Delete only the scratch directories created for this review, on success or failure after preserving useful synthetic diagnostics. Keep the source artifacts and compact evidence through subsequent implementation so later sessions can reproduce the review without relying on `/tmp`. Never retain secrets or bulky generated databases/output in the repository. For historical packets whose scripts existed only in `/tmp`, check availability and reconstruct from the authoritative rules if missing; do not claim a rerun of unavailable evidence.

## Regression and quota discipline

Run targeted tests per mutation through one automated script; summarize output by rule and failing test rather than feeding every subprocess log to the model. Reuse references and requirement mappings instead of rebuilding them for each implementation packet. Do not run the entire suite for every mutant.

Run the brief's commands and the full offline suite against the final unmutated checkout before acceptance. Compare failure identities and reasons with the baseline, not only counts. Pending test-only cases outside this packet may remain only with their implementing task identified; cases this packet implements must now pass. Investigate flakes and report them rather than hiding them with unconditional retries. Repeat broad checks after material fixes, not after an unchanged successful run. Record the final result before marking tasks complete.
