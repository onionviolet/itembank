# Phase 2: Daemon Consolidation & Settings Foundation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-07
**Phase:** 2-Daemon Consolidation & Settings Foundation
**Areas discussed:** none interactively — user delegated all four presented areas

---

## Gray areas presented

| Area | Description offered | Outcome |
|------|----------------------|---------|
| Daemon architecture | New `daemon.py` + one route table vs. merging existing per-surface Handler subclasses | Delegated |
| Second-instance behavior | Detect-and-attach singleton vs. today's silent OS-assigned-port fallback | Delegated |
| Bank addressing in routes | Startup-scanned working directory + allowlist vs. raw path in URL; also decided `/api/*` scope | Delegated |
| Settings scope & mechanism | Which of the six PROJECT.md keys ship now, and how invalid values are rejected | Delegated |

**User's response:** "just decide whats best and auto everything" — declined to discuss any area individually.

---

## Claude's Discretion

All four areas above were resolved by Claude's judgment rather than user selection.
See `02-CONTEXT.md` §Implementation Decisions (D-01 through D-07) for the specific
choices and their rationale, each grounded in the pre-roadmap research doc's
architecture sketch and in Phase 1 precedent (dotted lint codes, `schema_validate.py`,
additive settings sequencing).

## Deferred Ideas

None — no discussion turns occurred, so no scope-creep ideas surfaced to defer.
