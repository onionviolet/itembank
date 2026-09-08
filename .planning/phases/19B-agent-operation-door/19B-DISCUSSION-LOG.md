# Phase 19B: Agent Operation Door - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution
> agents. Decisions are captured in `19B-CONTEXT.md`. This log preserves the
> alternatives considered.

**Date:** 2026-09-06
**Phase:** 19B-agent-operation-door
**Areas discussed:** Proposal retention

## Proposal retention

| Option | Description | Selected |
|--------|-------------|----------|
| Durable review record | Retain settled proposals when useful for future review, audit, comparison, and recovery. | Yes |
| Automatic compaction | Remove or compact proposal files immediately after journal settlement. | No |

**User's choice:** "remain accordingly for future review if useful?"

**Notes:** Settled proposal records remain durable by default. Any later
compaction must be an explicit maintenance operation that preserves stable
identity, disposition, provenance, journal linkage, and review facts.

## The agent's Discretion

Internal path and helper naming may be chosen during planning within the
authority, atomicity, reload, and recovery constraints in `19B-CONTEXT.md`.

## Deferred Ideas

Retention-policy controls and proposal compaction wait for evidence from real
proposal volume.
