# Phase 1: Evidence Spine & Protocol Foundation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-06
**Phase:** 1-Evidence Spine & Protocol Foundation
**Areas discussed:** Item identity & where the ID lives, Evidence store shape on disk, Migration & what happens to the old files, Protocol surface (error codes, schema versions, contract fixture, idempotency)

---

## Item Identity & Where the ID Lives

### Q1 — What is an item's evidence key?

| Option | Description | Selected |
|--------|-------------|----------|
| Opaque ID, hash as a separate field | Stable opaque ID at first lint; content hash stored beside it for change detection. PITFALLS.md's recommendation. | ✓ |
| Content hash IS the ID, plus rekey/alias table | Matches the literal wording of issue #4. Every edit mints a new ID and needs an alias row. | |
| Opaque ID only, no content hash | Simplest schema, but makes EVID-02 unimplementable. | |

**User's choice:** Opaque ID + separate hash field.

### Q2 — Where does the opaque ID physically live?

| Option | Description | Selected |
|--------|-------------|----------|
| In the bank markdown, as a new item field | Self-describing bank; lint would edit private banks. | ✓ (Claude's discretion) |
| Sidecar index file beside the bank | Bank untouched, but file and index can separate. | |
| Inside the evidence store only | Couples the format contract to the evidence layer. | |

**User's choice:** "Do what is best since I dont understand."
**Notes:** Claude decided bank-markdown field, with the mitigation that `lint` stays read-only and a separate explicit action does the assignment, so the write is visible in `git diff`. Reasoning recorded in CONTEXT.md D-02/D-03 so it can be challenged rather than inherited.

### Q3 — What happens when lint detects the content hash drifted?

| Option | Description | Selected |
|--------|-------------|----------|
| Warn, update the hash, keep the history | Normal-case edit keeps evidence attached. Risk: a genuine rewrite inherits old trend data. | ✓ |
| Warn and require an explicit same/different choice | Rewrite-inherits-history cannot happen; one extra decision per stem edit. | |
| Warn only, hash never auto-updates | Standing warnings accumulate and get ignored. | |

**User's choice:** Warn, update, keep history.

### Q4 — Scope of item IDs and objective names?

| Option | Description | Selected |
|--------|-------------|----------|
| IDs globally unique; objectives namespaced by subject | Cross-subject query unambiguous; existing banks need a subject at migration. | ✓ |
| IDs globally unique; objectives stay bare strings | Nothing to migrate, but two subjects sharing an objective word silently merge trends. | |
| IDs scoped per bank; evidence records bank + ID | Renaming or splitting a bank breaks the key. | |

**User's choice:** Global IDs, subject-namespaced objectives.

---

## Evidence Store Shape on Disk

### Q1 — What is the evidence store physically?

| Option | Description | Selected |
|--------|-------------|----------|
| Append-only JSONL event log | Plain text, nothing overwritten, EVID-05 falls out of the format. Queries need an index. | ✓ |
| stdlib sqlite3 | Real queries, but breaks "no database" and makes evidence unreadable in a text editor. | |
| One JSON document rewritten atomically | Matches `write_session`, but full-rewrite-per-response is a flagged pitfall. | |

**User's choice:** Append-only JSONL.

### Q2 — How is EVID-04 answered without a database?

| Option | Description | Selected |
|--------|-------------|----------|
| Replay the log on every query | One code path, no cache invalidation; slow as history grows. | |
| Disposable derived index, log stays truth | Rebuildable cache (JSON or sqlite3), deletable with no loss. | ✓ |
| Log plus maintained rollups on each append | Instant queries, but a crash between two writes leaves them disagreeing. | |

**User's choice:** "2, dont forget we are also inspired by pwn.college and more."
**Notes:** Recorded as a design influence in CONTEXT.md `<specifics>`. pwn.college and CTFd both derive progress views from an append-only record of verified solves rather than storing progress state directly — the same shape as the chosen option. PROJECT.md's prior-art table already names both for the machine-checkable-verifier line; this extends it to the evidence layer.

### Q3 — One log or several?

| Option | Description | Selected |
|--------|-------------|----------|
| One log for everything | "One store" and cross-subject query become literally true. | ✓ |
| One log per subject | Blast radius contained; "one store" becomes three by another name. | |
| One log rotated by time period | Bounded working file; rotation boundary risks loss or double-counting. | |

**User's choice:** One log for everything.

### Q4 — What does EVID-05 reversibility mean in an append-only log?

| Option | Description | Selected |
|--------|-------------|----------|
| Compensating events — nothing ever removed | Retraction references the original; views honour it. | ✓ |
| Log lines hand-editable in place | Honest about single-user reality, but the guarantee becomes a convention. | |
| Git commit per evidence write | Reversibility is `git revert`, but a commit per answer is heavy and pre-empts Phase 11. | |

**User's choice:** Compensating events.

---

## Migration & What Happens to the Old Files

### Q1 — What does "become views over the store" mean for the three old files?

| Option | Description | Selected |
|--------|-------------|----------|
| Regenerated on demand from the log | Log is truth; old files are renders. Manual `short` marking must move. | ✓ |
| Frozen as read-only archive | Nothing damaged, but two places to look — the three-stores problem persists. | |
| Still written alongside, dual-write | Habits keep working, but two writers can disagree. | |

**User's choice:** Regenerated on demand.

### Q2 — How does a `short` mark get recorded now?

| Option | Description | Selected |
|--------|-------------|----------|
| A `mark` command/route appends a mark event | First-class timestamped evidence; needs batch support. | ✓ |
| The rendered attempt file stays editable and is read back | Keeps the current workflow; makes the render an input too. | |
| Defer — record `review_state` only, no marking surface | Breaks a workflow that works today, until Phase 8. | |

**User's choice:** `mark` command/route appending an event.
**Notes:** Batch marking flagged in CONTEXT.md D-12 as a requirement, not an optional nicety — twenty invocations for twenty short answers is a regression.

### Q3 — How does migration run and what proves it worked?

| Option | Description | Selected |
|--------|-------------|----------|
| Re-runnable and idempotent, with a dry-run first | Makes success criterion 2's count comparison verifiable. Needs stable per-source-record identity. | ✓ |
| One-shot, refuses to run twice | Simple, but a half-failed run leaves manual cleanup. | |
| Re-runnable, always rebuilds from scratch | Violates the append-only rule just set. | |

**User's choice:** Re-runnable and idempotent with `--dry-run`.

### Q4 — What happens to old `Qn`-keyed records that cannot resolve?

| Option | Description | Selected |
|--------|-------------|----------|
| Import as unresolved, never drop | Counts balance honestly; trend queries skip them; `report` states how many. | ✓ |
| Best-effort match, then import unresolved | Recovers more history, but a wrong match is silent and worse than no match. | |
| Refuse to migrate until every record resolves | Could block indefinitely on items that no longer exist. | |

**User's choice:** Import as unresolved.

---

## Protocol Surface

### Q1 — Where does the published contract live and what checks it?

| Option | Description | Selected |
|--------|-------------|----------|
| JSON Schema files in a `schemas/` directory | Standard format an agent already reads; no stdlib validator exists. | ✓ |
| Golden fixture files CI diffs against | No validator needed, but a fixture shows an example, not the rules. | |
| `spec --json` prints the contract | Directly satisfies PROTO-05; nothing to diff in git history. | |

**User's choice:** JSON Schema files in `schemas/`.
**Notes:** The missing-stdlib-validator problem is carried into CONTEXT.md as an open question the planner must resolve explicitly rather than leave implicit.

### Q2 — What shape does a machine-readable lint error take?

| Option | Description | Selected |
|--------|-------------|----------|
| Namespaced dotted codes | `item.missing_key` — self-describing, no lookup table. Codes become an API. | ✓ |
| Numeric codes with a published table | Stable and greppable, but meaningless without the table. | |
| No codes — structured fields only | PROTO-02 explicitly asks for a stable code. | |

**User's choice:** Namespaced dotted codes.

### Q3 — What makes two submits "the same response"?

| Option | Description | Selected |
|--------|-------------|----------|
| Same session + item + canonical answer | Reuses `canonical_response()`; collides with Phase 6 re-attempts. | ✓ (refined by Q4) |
| Same session + item, any answer — first write wins | Simplest, but forbids the second attempt Phase 6 requires. | |
| Caller supplies an idempotency key | Exact, but pushes correctness onto the caller. | |

**User's choice:** Session + item + canonical answer.

### Q4 — How is a genuine re-attempt distinguished from a duplicate?

| Option | Description | Selected |
|--------|-------------|----------|
| Attempt number is part of the key | Phase 1 defines attempt numbering ahead of Phase 6's use of it. | ✓ |
| Short time window — dedupe only within N seconds | A guess, and it makes hint-ladder gaming easier. | |
| Leave it — Phase 6 solves it later | Evidence would live under two inconsistent rules. | |

**User's choice:** Attempt number in the key.
**Notes:** Claude raised the Phase 6 collision unprompted after Q3 was answered; Q4 exists to close it rather than ship a rule Phase 6 would have to change.

---

## Claude's Discretion

- **Where the opaque ID physically lives** (Identity Q2) — user answered "do what is best since I dont understand." Claude chose the bank-markdown field with a read-only-lint mitigation. Recorded in CONTEXT.md D-02 with the fallback (sidecar index) named, and flagged so a reversal is raised as a decision checkpoint rather than made quietly.
- Event field naming, log file location, derived-index file format, and the internal shape of the rebuild pass were left unconstrained.

## Deferred Ideas

- Item deletion and retirement semantics — needed before Phase 11's auditor writes and retires items.
- Whether the old files are deleted after a verified migration or left in place.
- Whether `day`'s streak/tick data migrates into the same log — closer to Phase 10.
- PROTO-01 version-bump policy: what counts as a breaking schema change.
- How a no-repo-context agent physically receives the `schemas/` files (PROTO-05).
