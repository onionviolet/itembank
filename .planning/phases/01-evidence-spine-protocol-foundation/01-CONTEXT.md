# Phase 1: Evidence Spine & Protocol Foundation - Context

**Gathered:** 2026-08-06
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase delivers four things and nothing else:

1. **Stable item identity** that survives a legitimate content edit.
2. **One evidence store** replacing `_attempts/*.md`, session JSON, and `daily_log.md`.
3. **A migration** from those three stores into the one, losing no recorded response.
4. **A published protocol** — schema versions, machine-readable lint errors, defined
   idempotency on `submit`, and a contract an agent can read with no repository access.

Everything downstream reads or writes against this. The teaching loop, selection,
trends, and the auditor are all out of scope here; where a decision below touches
them (attempt numbering, mark events), it exists only because Phase 1 must not
record evidence under a rule Phase 6 will have to change.

**Explicitly not in this phase:** the hint ladder, session modes as behaviour
(the *field* is recorded, the behaviour is Phase 6), rubric marking UI, the
daemon, selection rules, trends.

</domain>

<decisions>
## Implementation Decisions

### Item Identity

- **D-01:** An item's evidence key is an **opaque ID**, assigned at first lint. The
  **content hash is a separate field** stored beside it, used only for change
  detection — never as the key. This is the direct mitigation for PITFALLS.md
  Pitfall 1 (content-hash-as-ID orphans history on every edit).
  — **Reversibility:** one-way — once evidence is recorded against opaque IDs,
  changing the key scheme needs a full re-key migration of the event log and every
  derived index.

- **D-02:** The opaque ID **lives in the bank markdown** as a new additive item
  field. The bank stays self-describing: copy the `.md` anywhere and its evidence
  still resolves. `model.py` keeps owning identity with no import from `runtime.py`,
  preserving the existing layer split.
  — **Reversibility:** one-way — the ID is written into private bank files; moving
  it elsewhere later means rewriting those files and re-keying the store.

- **D-03:** **`lint` stays read-only.** It reports items missing an ID; a separate
  explicit action assigns them, so ID assignment appears in `git diff` before you
  commit rather than happening as a side effect of validating.
  — **Reversibility:** reversible.

- **D-04:** When lint detects a content hash drifted from the recorded one:
  **warn, update the hash, keep the evidence history attached.** Satisfies EVID-02.
  Accepted risk stated plainly: a genuine rewrite that changes what the question
  asks will silently inherit the old item's trend data. Judged the right trade
  because 25 of 45 EMT wrong options are due for editing this milestone, and a
  rule that fires a standing warning on every one of them gets ignored.
  — **Reversibility:** reversible.

- **D-05:** **Item IDs are globally unique across every bank.** Evidence never needs
  to know which file a record came from, so renaming or splitting a bank file
  cannot orphan history.
  — **Reversibility:** costly — a per-bank scheme would need every existing ID
  re-issued and every event rewritten.

- **D-06:** **Objectives are namespaced by subject** (e.g. `emt:airway.opa`,
  `csci1100:loops.while`). Without this, two subjects reusing one objective word
  silently average two unrelated skills into one trend line. Existing banks need a
  subject assigned at migration.
  — **Reversibility:** costly — objective strings appear in every event record.

### Evidence Store

- **D-07:** The store is a single **append-only JSONL event log**. One line per
  event. Plain text — readable, greppable, git-diffable. Nothing is ever
  overwritten, so EVID-05 falls out of the format rather than needing code.
  — **Reversibility:** one-way — the on-disk format is what migration writes into
  and what every later phase reads.

- **D-08:** **The log is the only authority.** Queries (EVID-04) are served by a
  **disposable derived index**, rebuilt whenever the log has grown past it, and
  deletable at any time with no loss. A `sqlite3` file is acceptable *as that
  cache* — never as the system of record. This keeps PROJECT.md's "no database"
  rule intact in the sense that matters: nothing authoritative is opaque.
  — **Reversibility:** reversible — the index is by definition throwaway.

- **D-09:** **One log for everything** — every subject, session, and mode. EVID-03's
  "one store" and EVID-04's cross-subject query are then literally true rather than
  true-after-a-join. The reader works line by line and **skips and reports** a
  malformed line rather than crashing.
  — **Reversibility:** costly.

- **D-10:** Reversibility (EVID-05) means **compensating events**. Undoing appends a
  retraction referencing the original event; nothing is removed. Every view honours
  retractions. A raw line count therefore overstates history — readers must apply
  retractions, and any count shown to the learner must be a post-retraction count.
  — **Reversibility:** one-way — this is the semantics of the log.

### Migration

- **D-11:** `_attempts/*.md`, session JSON, and `daily_log.md` become
  **renders generated on demand from the log**. They are outputs, never inputs.
  — **Reversibility:** one-way — dual-writing again later would reintroduce the
  two-writers problem this decision exists to end.

- **D-12:** Because the attempt file is now a render, manual `short` marking moves to
  a **`mark` command plus the equivalent route**, appending a mark event. Marks
  become first-class evidence with a timestamp instead of a hand-edited `MARK:`
  string. **The command must accept a batch** — marking twenty short answers as
  twenty invocations is a workflow regression.
  — **Reversibility:** reversible.

- **D-13:** Migration is **re-runnable and idempotent**, with **`--dry-run` first**
  reporting what it would import and the counts it expects. Every source record maps
  to a deterministic event identity so a second run imports nothing new. This is what
  makes success criterion 2 (pre/post count comparison) verifiable rather than
  asserted.
  — **Reversibility:** reversible.

- **D-14:** Old records keyed by positional `Qn` that cannot resolve to an item ID are
  **imported as unresolved, never dropped** — the event carries the original `Qn`,
  its source file, and no item ID. Counts balance honestly. Trend queries skip
  unresolved events; `report` states how many exist. No stem-similarity guessing:
  a wrong match attaches your history to the wrong question and nothing ever tells
  you.
  — **Reversibility:** reversible — unresolved events can be attributed later.

### Protocol Surface

- **D-15:** The published contract is **JSON Schema files in a `schemas/` directory**
  — one per contract: item, session, response, report, lint error. CI validates real
  runtime output against them. Open cost the planner must solve: **there is no JSON
  Schema validator in the standard library**, so either a minimal validator is
  written here or the CI check stays shallow. Name which, do not leave it implicit.
  — **Reversibility:** one-way — a published schema is an API.

- **D-16:** Lint errors carry **namespaced dotted codes** — `item.missing_key`,
  `item.duplicate_id`, `lesson.ref_not_found` — alongside the field at fault and the
  human-readable text. Self-describing, so an authoring agent acts on the code
  without a lookup table. Codes are an API: renaming one is a breaking change.
  — **Reversibility:** one-way.

- **D-17:** **Idempotency key is session + item + attempt number + canonical
  answer.** Uses the existing `runtime.canonical_response()`, which already decides
  what a response *is* across every surface. A retried call inside one attempt
  dedupes and the tool reports `already_recorded`; a genuine second attempt records.
  — **Reversibility:** one-way — it defines what the evidence store considers a
  distinct response.

- **D-18:** **Attempt number is defined in this phase**, slightly ahead of the Phase 6
  work that consumes it. The runtime increments it when it hands an item back after a
  wrong answer. Without this, evidence recorded before Phase 6 lives under a different
  dedupe rule than everything after, and the store has two inconsistent eras.
  — **Reversibility:** one-way.

### Claude's Discretion

- **Where the ID lives (D-02)** was delegated — the user said "do what is best since
  I don't understand." The reasoning is recorded above so it can be challenged rather
  than inherited silently. If a planner finds that writing to private bank files is
  unacceptable in practice, the fallback is a sidecar index, and that reversal must be
  raised as a decision checkpoint, not made quietly.
- Event field naming, log file location, index file format, and the internal shape of
  the rebuild pass are all unconstrained.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirements
- `.planning/ROADMAP.md` §"Phase 1: Evidence Spine & Protocol Foundation" — goal, the
  five success criteria, and the two decisions the roadmap flags as needing a design
  pass at plan time.
- `.planning/REQUIREMENTS.md` lines 10–25 — EVID-01…EVID-08 and PROTO-01…PROTO-05,
  the 13 requirements this phase must satisfy.
- `.planning/PROJECT.md` §Core Value, §Constraints, §Key Decisions — the one-scorer /
  one-store guarantee, stdlib-only rule, additive-format rule, and the prior-art table.

### Risk and prior art
- `.planning/research/PITFALLS.md` **Pitfall 1** — content-hash IDs orphan evidence.
  This is the single most important input to D-01 and D-02. Read it before touching
  identity.
- `.planning/research/PITFALLS.md` §"Evidence spine" checklist item — "one evidence
  store often ships as the only store *new* writes go to, while history sits
  unmigrated." Directly motivates D-13 and D-14.
- `.planning/research/PITFALLS.md` §Pitfall on big-bang scope — migration-and-parity
  should be its own shippable checkpoint, not folded into "evidence spine done."

### Existing code constraints
- `.planning/codebase/CONCERNS.md` §"Non-atomic file writes" — only
  `runtime.py:147-150` (`write_session`) writes atomically today. That is the pattern
  to follow, and the five listed non-atomic writers are what this phase's renders
  must not reproduce.
- `.planning/codebase/CONCERNS.md` §"JSON session file format has no version evolution
  strategy" — `SESSION_VERSION = 1` exists with no migration logic. PROTO-01 has to
  fix that, not repeat it.
- `.planning/codebase/ARCHITECTURE.md` — the four-layer split that identity work must
  not violate.

### No external specs beyond these
The format contract itself lives in `model.py` (`SPEC`) rather than as a separate
document; read it from source.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`runtime.canonical_response()`** (`runtime.py:66`) — already decides what a
  response *is* across every surface. D-17's idempotency key builds directly on it;
  do not write a second normalizer.
- **`runtime.write_session()`** (`runtime.py:143`) — the only correct atomic write in
  the codebase (tmp + `os.replace()`). The index rebuild and any render write should
  copy this pattern.
- **`model.lint()`** (`model.py:207`) — already accumulates `(errors, warnings)` as
  `"Qn: message"` strings and already checks duplicate IDs (`model.py:218-221`).
  PROTO-02 extends the shape of what it returns; it does not need a new linter.
- **`model.SPEC`** (`model.py:122`) — the precedent for handing an agent a contract
  with no repository access. The `schemas/` directory should be reachable the same way.

### Established Patterns
- Items already carry an `"id"` field (`model.py:40`), currently derived as
  `"q" + number` — positional. D-01/D-02 replace how it is populated, not whether it
  exists, so the field is already threaded through every surface.
- `SESSION_VERSION = 1` (`runtime.py:20`) is the existing versioning precedent, and
  CONCERNS.md flags it as having no migration path. PROTO-01 must ship version
  *evolution*, not just version *stamps*.
- Every surface reaches a verdict through `runtime.score_response()`. Evidence writes
  must funnel just as narrowly — one writer, called from every surface.

### Integration Points
- `model.py` — ID field parsing, ID assignment action, content-hash computation,
  coded lint errors.
- `runtime.py` — the evidence writer, the idempotency check, attempt numbering, the
  index rebuild, session/response schema versions.
- `surfaces/session.py`, `surfaces/quiz.py` — currently write session JSON and attempt
  markdown directly; both become callers of the evidence writer, and their outputs
  become renders.
- `surfaces/day.py:434-482` (`load_day_log` / `write_day_log`) — `daily_log.md`
  becomes a render over the log. CONCERNS.md already flags this reader as fragile
  (header-row column mapping) and untested for concurrent writes.
- `tests/` — `scoring_roundtrip.py` and `serve_roundtrip.py` are the closest existing
  harnesses for the migration parity test.

</code_context>

<specifics>
## Specific Ideas

- **pwn.college and CTFd as an influence on the store shape** (user, this session:
  "dont forget we are also inspired by pwn.college and more"). Both derive their
  progress views from an append-only record of verified solves rather than storing
  progress state directly — the same shape as D-07/D-08. PROJECT.md's prior-art table
  already names them for "a machine-checkable verifier as the spine of a learning
  platform"; this extends that to the evidence layer. The takeaway to carry: the
  verified event is the atomic unit, and everything a learner sees is a view over it.
- The user delegated D-02 explicitly rather than guessing. Treat further identity
  questions the same way — present the mechanism and the cost, do not assume prior
  knowledge of hashing or content addressing.

</specifics>

<deferred>
## Deferred Ideas

- **Item deletion and retirement semantics** — what happens when an item with recorded
  evidence is removed from a bank, and whether retired items stay queryable. Raised and
  set aside; needed before the auditor (Phase 11) starts writing and retiring items.
- **Whether the old files are deleted after a verified migration** or left in place
  indefinitely. Not required for any success criterion here.
- **Whether `day`'s streak/tick data migrates into the same log** or stays separate.
  Touches Phase 10 (Retention, Pacing & Trends) more than this one.
- **PROTO-01 version-bump policy** — what counts as a breaking change to a published
  schema. Deferred; the versions are stamped in this phase, the policy can be written
  when the first bump is needed.
- **How a no-repo-context agent physically receives the `schemas/` files** (PROTO-05).
  A `spec`-style command that prints them is the obvious answer but was not decided.

</deferred>

---

## Open Questions Flagged for Research / Plan Time

These are named in ROADMAP.md as needing their own design pass, and this discussion
did not resolve them:

1. **Windows append-write durability.** Single-`write()` atomicity is a POSIX
   assumption. D-07 makes the whole store depend on it. The roadmap calls for a spike
   on this platform before the append pattern is trusted — that spike is now
   load-bearing, not optional.
2. **The exact event field set for EVID-07** — response time, confidence, error
   category, hint tier reached, session mode, and manual-review state must all be
   recorded whether or not anything reads them yet, because an uncaptured field cannot
   be backfilled. The list is known; the field names, types, and null semantics are not.
3. **JSON Schema validation with no stdlib validator** (from D-15) — decide between a
   minimal hand-written validator and a shallower CI check, and say which.

---

*Phase: 1-Evidence Spine & Protocol Foundation*
*Context gathered: 2026-08-06*
