# Release evidence

This folder holds the release evidence that the composite subscriptions implementation works: one redacted file per check (tasks.md Phase 16, OQ-5 rule). Evidence that closes a research gate or drives a design decision does not go here; it stays in [research.md](../research.md) beside the decision it supports. The implementation review and Constitution Check are in [implementation-review.md](../implementation-review.md).

## Rules

- One file per check, named after the check: for example `E-001.md`, `V-RX-01-i-p.md`, `V-CAN.md`.
- Every passing record is linked from its row of the [E-001–E-005 ledger](../research.md#evidence-ledger-e-001e-005) in research.md. A failed or not-run record is not linked as support; its result is reported for explicit resolution, and no scope is silently reduced.
- Raw logs, captures and harness output stay outside the repository. A record quotes only the redacted lines it needs.
- Redact credentials and tokens: panel tokens, client UUIDs, Trojan passwords, subscription URLs and tokens, payment keys and merchant secrets. Write `<redacted>` in their place.
- Controlled checks run only on explicitly authorized non-production resources with test credentials. No production panel serving customers, no real customer money and no production data.
- A synthetic or mock-only result is never presented as proof of real panel, client, payment, traffic, routing, enforcement or remote-recovery behavior. A check that did not run stays `not-run`.
- Say who ran the check. A result reported by the owner and not reproduced by an agent is labelled **owner-reported manual**, as in research.md.

## Record format

Each record has these sections, in this order.

```markdown
# <check ID>: <short title>

- **Result**: pass | fail | not-run
- **Date**: <YYYY-MM-DD>
- **Run by**: <agent | owner (owner-reported manual)>
- **Task**: <tasks.md task ID>
- **Ledger row**: <E-00x>

## Implementation revision

<Commit hash of the code under test, and whether the working tree was clean.>

## Versions and configuration

<Panel, Xray-core, client app, OS and Python versions; the panel settings the check depends on (for example `restartXrayOnClientDisable`); the route from the manager to each panel (direct TLS from the bot host, or the workstation route); load, where the check measures timing or capacity.>

## Authorization and isolation

<Who authorized the run, which disposable resources were used, and how unrelated users, listeners and outbounds were kept out of reach.>

## Fixture

<The synthetic fixture used: nodes, inbounds, customers, subscriptions and payment methods. No real secrets.>

## Expected result

<What the requirement says must happen, with its FR, SC or V- reference.>

## Observed result

<What actually happened, with measured values and redacted excerpts. Every difference from the expected result is stated.>

## Redaction and cleanup

<What was redacted, where the raw logs are kept outside the repository, which test resources were removed, and how the removal was verified. A cleanup that failed or is still pending is recorded, not erased.>
```
