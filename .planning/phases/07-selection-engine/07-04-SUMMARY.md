---
phase: 07-selection-engine
plan: 04
subsystem: selection
tags: [selection, evidence, contract, one-way-door]

# Dependency graph
requires:
  - phase: 07
    plan: 01
    provides: selection.py, SPEC_FIELDS, do_start spec wiring
  - phase: 07
    plan: 02
    provides: pair/prerequisite SPEC_FIELDS entries
  - phase: 07
    plan: 03
    provides: bank-scoped evidence reading
provides:
  - SELECTION_MODES + selection_mode spec/session/response-event field
  - SELECTION_EVENT_TYPE + selection_event() (one per sitting, D-03)
  - --selection-mode CLI flag and /api/start twin
  - CI schema-step event-type filter
affects: [07-05, 07-06]

actuals:
  tokens: 5600
  tasks: 4
  commits: 1 (+ concurrent sweeps)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - two separately-recorded axes (selection_mode vs mode) on session and events
    - one selection event per sitting with a per-session dedupe key

key-files:
  created: []
  modified:
    - selection.py
    - surfaces/session.py
    - surfaces/cli.py
    - surfaces/daemon.py
    - evidence.py
    - itembank.py
    - schemas/session.schema.json
    - schemas/response.schema.json
    - .github/workflows/ci.yml
    - tests/selection_roundtrip.py
    - tests/evidence_roundtrip.py

key-decisions:
  - "User confirmed option-a on both gates: a distinct `selection_mode` field (D-11), and a `selection` event once per sitting plus `selection_mode` on every response event (D-03)."
  - "selection_mode defaults to practice (a diagnostic composition ignores cooldown and spreads one item per objective); unknown values are refused by select() and coerced to practice by /api/start."
  - "The selection event records only SPEC_FIELDS keys and is appended after the session write through the one writer."

patterns-established:
  - "A multi-type evidence log is validated per-type: CI filters to response events before applying response.schema.json."

requirements-completed: [SEL-02, SEL-03]

coverage:
  - id: D1
    description: selection_mode and mode are distinct recorded fields on the session and settable independently on both surfaces
    requirement: SEL-02
    verification:
      - kind: unit
        ref: tests/selection_roundtrip.py#check_selection_mode_recorded
        status: pass
    human_judgment: false
  - id: D2
    description: one selection event per sitting records the resolved spec and served item keys, and survives session-file deletion
    requirement: SEL-03
    verification:
      - kind: unit
        ref: tests/selection_roundtrip.py#check_selection_spec_recorded
        status: pass
    human_judgment: false
  - id: D3
    description: every response event names the selection_mode that served it; the recorded spec carries no keys outside SPEC_FIELDS (T-07-03)
    verification:
      - kind: unit
        ref: tests/selection_roundtrip.py#check_selection_spec_recorded
        status: pass
    human_judgment: false

# Metrics
duration: 40min
completed: 2026-08-10
status: complete
---

# Phase 7 Plan 4: The Recorded Selection Summary

**A sitting now says what it asked for, on the record: `selection_mode` names the composition (distinct from the feedback `mode`), and one `selection` event per sitting records the resolved spec and served items in the append-only log.**

## Performance

- **Duration:** 40 min
- **Started:** 2026-08-10T20:31:00Z
- **Completed:** 2026-08-10T21:11:00Z
- **Tasks:** 4
- **Files modified:** 11

## Accomplishments

- Both one-way doors walked through with user confirmation of option-a:
  distinct `selection_mode` (D-11), and the `selection` event + per-response
  `selection_mode` (D-03).
- `SELECTION_MODES` + spec validation (unknown values refused by `select()`,
  default practice with the reasoning in code); `--selection-mode` on the CLI
  and `/api/start` coercion (17 -> practice).
- `selection_event()` records `selection_spec` (SPEC_FIELDS only) + served
  item keys, deduped per session, appended after the session write.
- `response_event()` carries `selection_mode` (explicit null before phase 7);
  both schemas document the fields additively.
- CI schema step filters the log to response-typed lines (load-bearing:
  unfiltered validation now fails on a `selection` line).
- Two new checks live: `check_selection_mode_recorded`,
  `check_selection_spec_recorded` (spec round-trip, items match, survives
  session deletion, response carries the mode).

## Task Commits

- **Task 1/3 checkpoints:** resolved by user (option-a / option-a)
- **Task 2 + Task 4 implementation:** `3d0465e` (evidence/selection event,
  response selection_mode, CI filter, exports) plus the concurrent session's
  `b72eee6`/related sweeps that absorbed `selection.py`, the session schema,
  cli/daemon/session wiring and the test stubs. Content verified present in
  HEAD; labels in history are mixed (see deviation).

**Plan metadata:** pending (next commit)

## Files Created/Modified

- `selection.py` - SELECTION_MODES, spec validation + default
- `surfaces/session.py` - session field, selection-event append, spec wiring
- `surfaces/cli.py` / `surfaces/daemon.py` - the two surfaces
- `evidence.py` - selection event type/builder; response_event selection_mode
- `schemas/session.schema.json` / `schemas/response.schema.json` - additive fields
- `.github/workflows/ci.yml` - per-type log filter
- `tests/selection_roundtrip.py` - two new checks

## Decisions Made

- Selection composition and feedback policy are two named fields everywhere;
  neither published enum changed meaning.
- The spec is recorded once per sitting, in its own event type, and every
  response names the composition that served it.

## Deviations from Plan

### Plan-text / environment corrections

**1. SESSION_VERSION/UPGRADES acceptance no longer holds**
- The concurrent 06-01 work committed `SESSION_VERSION = 2` with a v1->v2
  upgrade lambda (`SESSION_UPGRADES = {1: ...}`) and a v2 session schema
  (`x-itembank-version: 2`, `schema_version const 2`). The plan's
  "`{} 1`" acceptance is superseded; both new fields are still optional and
  additive, and old sessions still upgrade. Verified
  `selection_mode` is in properties, not required.

**2. Committed Phase-6 runtime bug fixed as a blocker**
- `runtime.py` `teaching_transition` crashed every submit (bare
  `evidence_key` with no import). Minimal fix applied and committed in
  `3d0465e` (function-local import + qualified call). Logged.

**3. Concurrent sweeps mixed commit labels**
- The active 06-01/13-x session repeatedly committed staged phase-7 files
  under its own messages; content is fully preserved in HEAD. Logged in
  `deferred-items.md`.

**4. `defer_feedback` cursor semantics (concurrent, unresolved)**
- The concurrent agent's committed `FEEDBACK_POLICIES` defer_feedback branches
  never advance the cursor, stalling diagnostic/exam sittings and reddening
  `evidence_roundtrip`/`agent_roundtrip`. That is 06-01's design to finish;
  phase 7 did not alter feedback-policy semantics. Logged.

---

**Total deviations:** 4 documented (0 phase-7 code regressions)
**Impact on plan:** All phase-7 acceptance criteria verified (selection suite
green; schema validations green; CLI/API behaviors verified).

## Issues Encountered

- `--selection-mode nonsense` rejected by argparse (exit 2) as required.
- Two starts produce two sessions and two `selection` events, one per
  `session_id` (verified).
- Filtered log validates; unfiltered log now fails -- the CI filter is
  load-bearing (verified).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Ready for 07-05 (mode compositions + cooldown): `selection_mode` is a
  recorded, validated field the compositions can branch on, and the
  bank-scoped exposure seam is live.

---
*Phase: 07-selection-engine*
*Completed: 2026-08-10*
