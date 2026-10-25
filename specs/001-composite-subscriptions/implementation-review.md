# Implementation review: Composite VPN Subscriptions

Linked from [plan.md](plan.md) (constitution Governance: "feature plan or linked review"). This file records the review of the actual implementation, not the plan. Release evidence for each controlled check is in [evidence/](evidence/README.md); gate-closing evidence stays in [research.md](research.md).

A principle is never marked satisfied on a plan promise alone. Missing evidence stays visible as a gap or an approved exception (constitution "Planning and Review").

## Characterization exceptions

Filled by the Phase 2A characterization tasks when isolating a legacy path is impractical (constitution VI). Each exception records the principle, affected behavior and files, evidence, rationale, risk, compensating checks, responsible maintainer, and the remediation decision with a review date or bounded follow-up, and the reproducible baseline check. A project maintainer accepts each exception explicitly before merge or deployment (constitution Governance).

None recorded.

## Intended behavior differences

Filled by T242 after every characterization suite is re-run: each intended difference from the characterized legacy behavior, with its justification (constitution VI; FR-081; SC-012). Grandfathered legacy code that stays unchanged, such as the legacy defaults in `payment_engine.py` (T234), is recorded here too.

None recorded.

## Constitution Check

Filled by T245 against the actual diff, and updated by T264 with the release evidence. For each principle: check results, compatibility handling, operational consequences and unresolved risks, and every exception with its maintainer acceptance.

| Principle | Check result | Compatibility handling | Operational consequences | Unresolved risks and exceptions |
| --- | --- | --- | --- | --- |
| I Observable contracts | Not yet checked | | | |
| II Repeat-safe effects | Not yet checked | | | |
| III Authority/secrets | Not yet checked | | | |
| IV Recoverability | Not yet checked | | | |
| V Provider boundary | Not yet checked | | | |
| VI Verification | Not yet checked | | | |
| VII Actionable failures | Not yet checked | | | |

## Release go/no-go

Filled by T264. Every Phase 16 record shows pass, fail or not-run; every G-P method is either bound or recorded as unavailable with a reason; a failed item is reported for explicit resolution and no scope is silently reduced.

Not decided.
