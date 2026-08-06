---
phase: 01-evidence-spine-protocol-foundation
plan: 02
subsystem: infra
tags: [evidence-log, jsonl, item-identity, session, cli, tracer]

# Dependency graph
requires:
  - phase: 01-01
    provides: "evidence.py's locked-append primitive (append_line, iter_raw, path helpers, EVENT_SCHEMA_VERSION) and the Windows durability verdict gating this plan's first real writes"
provides:
  - "evidence.py: response_event() builder, append_event() (the one writer), events() (the defensive reader), attempt_number(), objective_history() (the first query), subject_of(), evidence_key(), idempotency_canon(), dedupe_key()"
  - "model.py: additive [ID:]/[HASH:] parsing into item_id/content_hash, empty until plan 01-04 assigns them"
  - "surfaces/session.py: cmd_start/cmd_next/cmd_submit as the first real callers of the evidence writer; served_ts on the session for response-time capture"
  - "surfaces/evidence_cli.py + itembank evidence --objective: the first reader over the evidence log"
  - "The recorded, binding EVID-07 capture-policy decision (option-a) in 01-02-PLAN.md, governing every later plan that writes a response event"
affects: [01-03, 01-04, 01-05, 01-06, 01-07, 01-08, 01-09, 01-10, 01-11]

actuals:
  tokens: 7842
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Response-event builder/writer/reader split: response_event() builds a pure dict, append_event() is the sole persistence call, events()/objective_history() are read-side consumers layered on iter_raw"
    - "Shared item-key derivation (evidence_key()) called identically by the writer's dedupe_key computation and by the caller's attempt_number lookup, so the two can never silently drift apart"
    - "Reserved-null fields carry an explicit None with the reason stated in the builder's docstring, never an absent key, per the Task 1 decision"

key-files:
  created:
    - surfaces/evidence_cli.py
    - tests/evidence_roundtrip.py
  modified:
    - evidence.py
    - model.py
    - surfaces/session.py
    - surfaces/cli.py
    - itembank.py
    - .planning/phases/01-evidence-spine-protocol-foundation/01-02-PLAN.md

key-decisions:
  - "Task 1 (checkpoint:decision) resolved as option-a: response_time_ms and confidence are captured with real values (served_ts on the session, --confidence flag); review_state is computed; error_category and hint_tier are recorded as explicit null with the reason in the code, because no error taxonomy or hint ladder exists before Phase 6/8 and a guessed value would be read as fact by later trend analysis"
  - "evidence_key(q) added as a small shared helper (not explicitly named in the plan's export list) so the item-key logic used by response_event()'s dedupe_key and by session.py's attempt_number() call site lives in exactly one place"
  - "The plan's must_haves literally names 22 event keys and separately lists 23 (including 'bank') in its own 'Created by this plan' field list and threat model T-1-06; resolved by treating the named 22 as the floor and including 'bank' as a required 23rd field, since the threat model explicitly requires and tests it"
  - "This plan's tracer covers the session path only (start/next/submit), per its own <files> list; the browser quiz page's timer field is out of scope here and stays a later plan's work"

requirements-completed: [EVID-03, EVID-04, EVID-07, EVID-08, PROTO-01]

coverage:
  - id: D1
    description: "One itembank submit writes exactly one line to _evidence/evidence.jsonl through the one writer, and itembank evidence --objective reads that response back out of the log alone"
    requirement: EVID-03
    verification:
      - kind: unit
        ref: "tests/evidence_roundtrip.py#test_tracer_end_to_end"
        status: pass
    human_judgment: false
  - id: D2
    description: "A response recorded under --mode drill and one recorded under --mode exam are distinguishable in the log by their mode field alone, on the same item"
    requirement: EVID-08
    verification:
      - kind: unit
        ref: "tests/evidence_roundtrip.py#test_mode_recorded"
        status: pass
    human_judgment: false
  - id: D3
    description: "An absent or empty evidence.jsonl makes itembank evidence --objective print an empty history and exit 0, never raise"
    requirement: EVID-03
    verification:
      - kind: unit
        ref: "tests/evidence_roundtrip.py#test_empty_log"
        status: pass
    human_judgment: false
  - id: D4
    description: "Every response event carries the full field set (schema_version, event_id, event_type, ts, session_id, item_id, item_ref, item_type, bank, objective, subject, mode, attempt_number, answer, canonical, score, response_time_ms, confidence, error_category, hint_tier, review_state, dedupe_key, source_ref), with error_category and hint_tier explicitly null rather than absent"
    requirement: EVID-07
    verification:
      - kind: unit
        ref: "tests/evidence_roundtrip.py#test_tracer_end_to_end (raw log line key-set assertion)"
        status: pass
    human_judgment: false
  - id: D5
    description: "Exactly one append_event function exists across the whole codebase, structurally asserted the way tests/scoring_roundtrip.py already asserts one scorer"
    requirement: PROTO-01
    verification:
      - kind: unit
        ref: "tests/evidence_roundtrip.py#test_one_writer"
        status: pass
    human_judgment: false
  - id: D6
    description: "A bank markdown file carrying neither [ID:] nor [HASH:] parses to exactly the field values it parsed to today, plus two new empty-string fields; a bank whose markers precede its first option still parses a correct, unswallowed stem"
    requirement: EVID-04
    verification:
      - kind: unit
        ref: "model.py Task 2 acceptance commands (fixtures/sample_bank.md byte-identical parse, synthetic mid-stem [ID:]/[HASH:] parse, AST layer-split scan) — see 01-02-PLAN.md Task 2 acceptance_criteria"
        status: pass
    human_judgment: false
  - id: D7
    description: "No surface, query, render or report reaches a correctness verdict outside runtime.score_response() — the evidence store records verdicts, it never computes a second one"
    verification: []
    human_judgment: true
    rationale: "This is a structural/architectural prohibition (the plan's own must_haves.prohibitions marks it status: resolved, verification: judgment) rather than a single assertable test; response_event() takes score as a parameter it never computes, and evidence.py imports canonical_response from runtime rather than reimplementing it, but confirming no future call site violates this needs periodic human review, not one test."

duration: ~18min
completed: 2026-08-06
status: complete
---

# Phase 1 Plan 2: Evidence Spine Tracer & Item Identity Fields Summary

**One `itembank submit` now writes a full 23-field response event to `_evidence/evidence.jsonl` through a single writer, and `itembank evidence --objective` reads it back — the thinnest real path from a learner's answer to durable, queryable evidence, proven end to end before any later plan expands outward from it.**

## Performance

- **Duration:** ~18 min (this continuation; Task 1's checkpoint wait is excluded)
- **Started:** 2026-08-06T16:35:19Z (approx, continuation resume point)
- **Completed:** 2026-08-06T16:52:47Z
- **Tasks:** 3
- **Files modified:** 8 (2 created, 6 modified, including the plan file itself)

## Accomplishments

- Resolved Task 1's one-way-door decision: option-a, capturing `response_time_ms` and
  `confidence` with real values and recording `error_category`/`hint_tier` as explicit,
  documented `null` rather than either omitting them or guessing at values Phases 6/8
  haven't earned yet.
- `model.py` parses `[ID: ...]` and `[HASH: ...]` additively into `item_id`/`content_hash`,
  extends the stem-terminator alternation so identity markers preceding an item's first
  option no longer get swallowed into the stem, and documents both fields in `SPEC` —
  every existing fixture bank still parses byte-identically.
- `evidence.py` grows from primitive to spine: `response_event()` builds the full 23-key
  event dict (22 named in the plan's must_haves plus `bank`, required by its own field list
  and threat model); `append_event()` is the one writer; `events()` degrades on an unknown
  `event_type` or newer `schema_version` instead of crashing; `attempt_number()` and
  `objective_history()` are the first two readers.
- `surfaces/session.py`'s `cmd_start`, `cmd_next` and `cmd_submit` become real callers:
  `next` now writes `served_ts` (it was read-only before this plan), and `submit` computes
  `response_time_ms` from it, reads the new `--confidence` flag, and calls
  `evidence.append_event()` alongside the existing session write.
- `surfaces/evidence_cli.py` (new) and `itembank evidence --objective` are the first reader
  surface; `submit --confidence` and `start --mode drill` round out the CLI surface this
  plan needed.
- `tests/evidence_roundtrip.py` drives the real CLI end to end against a bank copied into a
  tempdir, covering the tracer, drill/exam mode distinguishability, an absent-log empty
  history, and a structural one-writer guard — all four pass, and so does every other test
  in the suite (`agent_roundtrip.py` in particular, confirming the session-surface changes
  don't break the existing JSON assessment contract).

## Task Commits

Each task was committed atomically:

1. **Task 1: Decide the on-disk response-event contract and the EVID-07 capture policy** - `873e7d8` (docs) — resolution recorded inline in `01-02-PLAN.md`
2. **Task 2: Parse the two additive identity fields in model.py** - `ea748ef` (feat)
3. **Task 3: End-to-end — one submitted response reaches the log and comes back out of it** - `1d44e0b` (feat, message amended once for a shell-escaping artifact; content unchanged, see Issues Encountered)

_Note: no TDD red/green/refactor split was called for; Task 3 is type="tracer" and its `<verify>` was run directly after the single implementation commit._

## Files Created/Modified

- `evidence.py` - Added `subject_of()`, `evidence_key()`, `idempotency_canon()`, `dedupe_key()`, `response_event()`, `append_event()`, `events()`, `attempt_number()`, `objective_history()`; imports `canonical_response` from `runtime`
- `model.py` - `parse_question()` adds `item_id`/`content_hash`; stem terminator extended with `\n[ID`/`\n[HASH`; `SPEC` documents both fields
- `surfaces/session.py` - `cmd_start`/`cmd_next` write `served_ts`; `cmd_submit` computes `response_time_ms`, reads `--confidence`, calls `evidence.append_event()`; new `ms_since()` helper
- `surfaces/evidence_cli.py` (new) - `cmd_evidence()`, the query surface over `objective_history()`
- `surfaces/cli.py` - New `evidence` subparser; `submit --confidence`; `start --mode` gains `drill`
- `itembank.py` - Eight new evidence names added to the `from evidence import (...)` block and `__all__`, alphabetized
- `tests/evidence_roundtrip.py` (new) - `test_tracer_end_to_end`, `test_mode_recorded`, `test_empty_log`, `test_one_writer`
- `.planning/phases/01-evidence-spine-protocol-foundation/01-02-PLAN.md` - Task 1's resolution recorded inline as a `<resolution>` block

## Decisions Made

- **Task 1: option-a**, as detailed in `key-decisions` above and recorded verbatim in
  `01-02-PLAN.md`'s new `<resolution>` block — the binding EVID-07 capture policy for every
  later plan.
- **`evidence_key(q)` added as a shared helper.** The plan's `attempt_number(log, session_id,
  item_key)` signature requires the caller to derive the same item key
  `response_event()`/`dedupe_key()` use internally. Rather than duplicate `q.get("item_id")
  or "ref:" + q["id"]` in both `evidence.py` and `surfaces/session.py`, it is one function
  both call, so the writer's dedupe key and the reader's attempt-count lookup can never
  silently disagree about what an item's evidence key is.
- **`canonical` (the event field) vs. the idempotency canon (used only inside `dedupe_key`)
  are kept distinct.** `canonical` on the event is the plain `runtime.canonical_response(q,
  answer)` output (`None` for `short`, matching every other consumer of that function);
  `idempotency_canon()`'s `short:`-prefixed hash exists only to give `dedupe_key` something
  comparable for constructed responses. Conflating the two would have made the event's
  `canonical` field lie about what `canonical_response` actually returns for a `short` item.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Plan's must_haves count (22) undercounts its own required field list (23, including `bank`)**
- **Found during:** Task 3, writing `response_event()` and its test
- **Issue:** `must_haves.truths` names exactly 22 event keys and says "all 22 keys present,"
  but the plan's own "Created by this plan" field list (line ~485) and threat model T-1-06
  both name/require a 23rd field, `bank` (basename only, tested for no path separator).
  These two parts of the same plan disagree by one field.
- **Fix:** Included `bank` as a required field on every event (23 total), matching the field
  list and the threat model rather than the truths count, since `bank`'s presence is both
  explicitly specified elsewhere in the same plan and load-bearing for T-1-06's mitigation.
  `tests/evidence_roundtrip.py` treats the 22 named keys as a floor and separately asserts
  `bank` is present and path-separator-free.
- **Files modified:** `evidence.py`, `tests/evidence_roundtrip.py`
- **Verification:** `test_tracer_end_to_end` passes, asserting all 22 named keys plus `bank`
- **Committed in:** `1d44e0b` (Task 3 commit)

**2. [Rule 2 - Missing Critical] Added `evidence_key()` shared helper**
- **Found during:** Task 3, wiring `attempt_number()`'s caller in `surfaces/session.py`
- **Issue:** The plan's `attempt_number(log, session_id, item_key)` signature requires the
  caller to independently compute the same item key `response_event()`/`dedupe_key()` derive
  internally. Duplicating `q.get("item_id") or "ref:" + q["id"]` in two files risks the two
  copies drifting apart, which would silently break attempt-number correctness.
- **Fix:** Extracted `evidence_key(q)` in `evidence.py`, called by both `response_event()`
  and `surfaces/session.py:cmd_submit`.
- **Files modified:** `evidence.py`, `surfaces/session.py`
- **Verification:** `tests/evidence_roundtrip.py` and `tests/agent_roundtrip.py` both pass
- **Committed in:** `1d44e0b` (Task 3 commit)

**3. [Rule 1 - Bug] First test draft used the fixtures bank in place, writing evidence into the repo tree**
- **Found during:** Task 3, first run of `tests/evidence_roundtrip.py`
- **Issue:** An initial draft of `start_and_submit()` passed the shared `fixtures/sample_bank.md`
  path directly to `itembank start`, rather than a copy inside the tempdir the plan's action
  text explicitly calls for ("Copy fixtures/sample_bank.md into a tempfile.mkdtemp()
  directory so the log lands outside the repository tree"). Since `evidence.log_path()` is
  derived from the bank's own directory, this wrote a real `_evidence/` directory under
  `fixtures/` in the repository working tree, and the query against `--base <tempdir>` found
  nothing (`count: 0` instead of 1).
- **Fix:** Copied `fixtures/sample_bank.md` into each test's `tempfile.mkdtemp()` directory
  before driving the CLI against that copy; cleaned up the accidentally-created (gitignored)
  `fixtures/_evidence/` and `fixtures/_attempts/` directories from the working tree.
- **Files modified:** `tests/evidence_roundtrip.py`
- **Verification:** `tests/evidence_roundtrip.py` passes; `git status` confirms no stray
  gitignored artifacts remain under `fixtures/`
- **Committed in:** `1d44e0b` (Task 3 commit)

---

**Total deviations:** 3 auto-fixed (1 plan-inconsistency bugfix, 1 missing-critical helper, 1 test-authoring bug)
**Impact on plan:** All three keep the tracer's actual behavior aligned with the plan's own stated field list, threat model, and explicit tempdir instruction. No scope creep — no new capability was added beyond what the plan already specified elsewhere in its own text.

## Issues Encountered

- The Task 3 commit was created once with a message containing literal backticks
  (`` `--confidence` ``, `` `evidence` ``, `` `drill` ``); the shell tool interpreted these as
  command substitution before the commit was made, silently dropping the quoted words from
  the recorded message (the commit itself and all file contents were correct — only the
  message text was affected). Fixed with a single `git commit --amend` using a heredoc to
  avoid shell interpolation, before any other commit was built on top of it. No file content
  changed; only the message.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The evidence spine is now real end to end: `evidence.py` has a writer, a builder, a
  defensive reader, and a first query, and `surfaces/session.py` is a proven caller.
- `01-03` (machine-readable lint error codes) and `01-04` (item identity assignment via
  `itembank id-assign`, which will populate the `item_id`/`content_hash` fields this plan
  parses but leaves empty) can both build directly on this without redesigning the event
  shape.
- `01-05` (published schemas) should encode the Task 1 decision's field-by-field capture
  policy directly into `response.schema.json`'s field descriptions, especially the stated
  reasons for `error_category`'s and `hint_tier`'s reserved nulls — this summary and the
  plan's `<resolution>` block are the source text for that.
- The browser quiz page's response-time timer (mentioned in Task 1's option-a cost but out
  of this plan's `<files>` scope) remains open for whichever later plan touches
  `surfaces/quiz.py`'s attempt-writing path.
- No blockers identified for `01-03` onward.

---
*Phase: 01-evidence-spine-protocol-foundation*
*Completed: 2026-08-06*

## Self-Check: PASSED

- FOUND: surfaces/evidence_cli.py
- FOUND: tests/evidence_roundtrip.py
- FOUND: .planning/phases/01-evidence-spine-protocol-foundation/01-02-SUMMARY.md
- FOUND: 873e7d8 (Task 1 commit)
- FOUND: ea748ef (Task 2 commit)
- FOUND: 1d44e0b (Task 3 commit)
