---
phase: 01-evidence-spine-protocol-foundation
plan: 07
subsystem: infra
tags: [idempotency, dedupe, retraction, undo, evidence-log, jsonl, proto-03, evid-05]

# Dependency graph
requires:
  - phase: 01-02
    provides: "evidence.py's response_event()/append_event()/attempt_number()/objective_history() as the writer and readers this plan makes idempotent and retraction-aware; evidence_key()/idempotency_canon()/dedupe_key() as the D-17 building blocks this plan enforces"
  - phase: 01-06
    provides: "schema_validate.py's oneOf/$ref-capable validator and the CI schema-enforcement step this plan's response.schema.json edits must keep passing"
provides:
  - "evidence.py: locked() (extracted platform lock, one msvcrt.locking site and one fcntl.flock site), append_line_checked()/recent_dedupe_keys()/DEDUPE_WINDOW_BYTES (idempotent, race-free append), retraction_event()/retracted_ids()/live_events()/event_by_id() (D-10 compensating-append undo), attempt_number(log, session_id, item_key, canon) reading through live_events"
  - "surfaces/evidence_cli.py: cmd_retract() -- itembank retract EVENT_ID --reason; cmd_evidence's output gains a retracted count"
  - "surfaces/cli.py: itembank retract subcommand"
  - "itembank.py: event_by_id, live_events, locked, recent_dedupe_keys, retracted_ids, retraction_event exports"
  - "tests/evidence_roundtrip.py: test_duplicate_submit_dedupes(), test_retraction()"
affects: [01-08, 01-09, 01-10, 01-11]

actuals:
  tokens: 13032
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "One lock implementation (locked(fd), a contextlib.contextmanager) shared by append_line and append_line_checked -- exactly one msvcrt.locking acquire site and one fcntl.flock acquire site in evidence.py, so the 01-01 spike's measured behavior extends to the new checked writer instead of being reimplemented."
    - "append_line_checked holds locked() across the dedupe tail-read and the write in one fd; recent_dedupe_keys(path) is the public read-only entry point (opens its own handle) while the internal _tail_dedupe_keys(fd, window) is what append_line_checked calls on its already-open, already-locked fd -- so this process never requests a second Windows record lock on a file it already holds one on."
    - "response_event()'s canonical field now stores idempotency_canon()'s output (never null), the same value dedupe_key is built from, so attempt_number()'s 'does the most recent live event's canonical equal this submission's canonical' comparison is comparing the right thing for a short item too (D-17)."
    - "D-10 as a read-side filter: live_events(log) is the only function views may use for counting (attempt_number, objective_history both read through it); events(log) stays the raw reader for a tool that genuinely needs retracted history, such as an audit. retracted_ids(log) collects over the WHOLE log in one pass before anything is emitted, so a retraction physically preceding its target in the file still suppresses it."
    - "_tail_dedupe_keys is retraction-aware within its own scanned window: a dedupe key whose event_id has since been retracted is excluded from the returned map, so resubmitting an identical answer after retracting the only prior response reports recorded, not already_recorded."

key-files:
  created: []
  modified:
    - evidence.py
    - surfaces/session.py
    - surfaces/evidence_cli.py
    - surfaces/cli.py
    - itembank.py
    - schemas/response.schema.json
    - schemas/report.schema.json
    - schemas/session.schema.json
    - tests/evidence_roundtrip.py

key-decisions:
  - "response_event()'s canonical field switched from runtime.canonical_response()'s raw output to evidence.idempotency_canon()'s output, per Task 1's explicit instruction. This changes what a short item's canonical field holds (a 'short:'+sha256 string instead of null) so it can never diverge from the value dedupe_key is built from -- if it did, attempt_number's comparison would be comparing the wrong thing and every short retry would look like a new attempt. schemas/response.schema.json's canonical property description and type (narrowed from [string,null] to string) were updated in the same commit per the standing phase decision that a response-event shape change requires the schema to move with it."
  - "append_line_checked's dedupe tail-read is retraction-aware from Task 1's commit onward (checking a literal 'retraction' event_type string, not the RETRACTION_EVENT_TYPE constant that doesn't exist until Task 2), so the low-level writer never needed a second pass once Task 2 landed the rest of the retraction machinery."
  - "attempt_number's signature gained a required canon parameter and now finds the most recent LIVE response event for a session+item key: same canonical -> same attempt (dedupe), different canonical -> next attempt. Task 1 landed it reading through events(); Task 2 changed exactly that one word to live_events(), per the plan's own task split, so a retracted response can never hold an attempt open."
  - "cmd_submit now skips appending a second data['responses'] entry when the evidence writer reports already_recorded (a crash-retry), so a resubmission of the same answer can never double-count in session_summary/report. The entry it does append gains an optional status field, documented additively in session.schema.json."
  - "Fixed a pre-existing plan-number attribution swap in response.schema.json's $defs while touching the file for retraction_event's real body: mark_event was labeled 'written by plan 01-07' and retraction_event 'written by plan 01-09', backwards from what 01-07 (this plan) and 01-09 (confirmed against 01-09-PLAN.md's own must_haves, which describes marking short answers) actually own."

requirements-completed: [PROTO-03, EVID-05]

coverage:
  - id: D1
    description: "Submitting the same response twice to the same item inside the same attempt records one accepted response; the tool states which happened (recorded vs already_recorded, naming the existing event_id on a duplicate)"
    requirement: PROTO-03
    verification:
      - kind: unit
        ref: "tests/evidence_roundtrip.py#test_duplicate_submit_dedupes"
        status: pass
    human_judgment: false
  - id: D2
    description: "A genuinely different response to the same item opens a new attempt (attempt_number 2) and records a second event, for both an auto-scored item and the short item, including the short-item whitespace/casing dedupe fallback"
    requirement: PROTO-03
    verification:
      - kind: unit
        ref: "tests/evidence_roundtrip.py#test_duplicate_submit_dedupes"
        status: pass
    human_judgment: false
  - id: D3
    description: "Retracting an event appends a reasoned compensating event; retracting an already-retracted event reports already_retracted and appends nothing; retracting an unknown event_id exits non-zero naming 'no event' and appends nothing; a retraction physically preceding its target in the log still suppresses it; a retracted response no longer holds an attempt open"
    requirement: EVID-05
    verification:
      - kind: unit
        ref: "tests/evidence_roundtrip.py#test_retraction"
        status: pass
    human_judgment: false
  - id: D4
    description: "Nothing is ever removed from the log: after a retraction, the original event line is still present and readable, and itembank evidence's count is post-retraction while its new retracted field reports how much was undone"
    requirement: EVID-05
    verification:
      - kind: unit
        ref: "tests/evidence_roundtrip.py#test_retraction"
        status: pass
    human_judgment: false
  - id: D5
    description: "The advisory lock is held across the dedupe read AND the write (T-1-02), and the CI schema step's response.schema.json contract still validates real submit output after the canonical field's shape change"
    verification:
      - kind: unit
        ref: "tests/durability_roundtrip.py (locked probe, kill probe) and a manual CI schema step run (start/submit/report/evidence/lint against schemas/*.json)"
        status: pass
    human_judgment: false

duration: ~40min
completed: 2026-08-06
status: complete
---

# Phase 1 Plan 7: Idempotent Writer and Compensating Retractions Summary

**One definition of a distinct response (session + item + attempt + canonical answer, extended for `short` via `idempotency_canon()`), a lock-protected dedupe check that tells the caller `recorded` vs `already_recorded` and names the existing event, and `itembank retract` as an append-only, reasoned undo that a retraction-aware `live_events()` filters out of every count without ever deleting the original line.**

## Performance

- **Duration:** ~40 min
- **Started:** 2026-08-06 (continuation from 01-06)
- **Completed:** 2026-08-06
- **Tasks:** 3
- **Files modified:** 9

## Accomplishments

- Extracted `append_line`'s platform lock into a reusable `locked(fd)` context manager (`contextlib.contextmanager`) so there is exactly one `msvcrt.locking` acquire site and one `fcntl.flock` acquire site in `evidence.py`, confirmed by re-running `tests/durability_roundtrip.py`'s locked probe (10,000 lines, 0 deviations) and kill probe against the refactored code.
- `append_line_checked(path, line, dedupe_key)` opens the fd once and holds `locked()` across both the dedupe tail-read and the write, making the check-then-append sequence race-free (T-1-02) rather than advisory. `recent_dedupe_keys(path, window=DEDUPE_WINDOW_BYTES)` is the public read-only entry point; the shared internal `_tail_dedupe_keys(fd, window)` is what the checked writer calls on its own already-locked fd, so the process never requests a second Windows record lock on a file it already holds one on. `DEDUPE_WINDOW_BYTES = 8 MiB` bounds the scan, documented with both the reasoning (a dedupe key carries the session_id, so a duplicate can only come from the same sitting) and the residual (a duplicate older than the window is recorded again, recoverable by retraction).
- `append_event()` now returns `{"accepted": bool, "status": "recorded"|"already_recorded", "event_id": ...}`, and a `dedupe_key` of `None` (a retraction) always writes. `attempt_number(log, session_id, item_key, canon)` implements D-17/D-18 in one rule: the most recent live response event for that session+item decides whether a submission is a retry (same canonical, same attempt) or opens the next attempt (different canonical, `attempt_number + 1`).
- `response_event()`'s `canonical` field now stores `idempotency_canon()`'s output rather than `runtime.canonical_response()`'s directly, closing the exact gap RESEARCH.md's Pitfall 1 named: a `short` item's `canonical` field used to be `null`, which meant `attempt_number`'s canonical comparison could never work for constructed response. It is now always a string (`"short:"` + sha256 of the normalized text for `short`), and `schemas/response.schema.json`'s `canonical` property was updated in the same commit (description and narrowed type) per the standing phase decision that a response-event shape change moves the schema with it.
- `surfaces/session.py`'s `cmd_submit` computes the canon ahead of `attempt_number`, and now skips appending a second `data["responses"]` entry when the writer reports `already_recorded` — a crash-retry catches the session up rather than recording a second response, so `session_summary`/`report` counts can never be inflated by a retry.
- D-10's undo: `retraction_event(retracts, reason, actor="human")` builds a compensating event (`dedupe_key` always `None`, raises `ValueError` on an empty reason); `retracted_ids(log)` collects every `retracts` target over the WHOLE log in one pass before anything is emitted, so a retraction that physically precedes its target still suppresses it; `live_events(log)` is the one filter views may use for counting (`attempt_number` and `objective_history` both read through it now); `event_by_id(log, event_id)` validates a retract target. `KNOWN_EVENT_TYPES` gained `"retraction"`.
- `itembank retract EVENT_ID --reason "..."` (`surfaces/evidence_cli.py:cmd_retract`, wired in `surfaces/cli.py`): exits non-zero naming `"no event"` for an unknown id with nothing appended; reports `already_retracted` (naming the existing retraction's event_id) with nothing appended for a repeat; otherwise appends the retraction and reports `retracted`. `itembank evidence`'s output gained a `retracted` integer alongside its already-post-retraction `count`.
- `tests/evidence_roundtrip.py` gained `test_duplicate_submit_dedupes` (PROTO-03: an auto-scored item and the `short` item, each driven through submit/rewind/submit-identical/rewind/submit-different, asserting `already_recorded` with the original `event_id` on a retry and `recorded` with `attempt_number` 2 on a genuinely different answer — including the short-item whitespace/casing dedupe pair RESEARCH.md's Warning Signs call for by name) and `test_retraction` (EVID-05: two responses under one shared objective, retract/re-retract/retract-unknown, a hand-built log whose retraction physically precedes its target, and confirmation that retracting the only response for an item lets a resubmission of the same answer report `recorded`).

## Task Commits

Each task was committed atomically:

1. **Task 1: Make the writer idempotent and teach it a retry from a second attempt** - `4486394` (feat)
2. **Task 2: Undo by appending — compensating retractions and retraction-aware views** - `bdfb632` (feat)
3. **Task 3: Pin duplicate submission and retraction in tests/evidence_roundtrip.py** - `b531be3` (test)

_Note: no TDD red/green/refactor split was called for; all three tasks are `type="auto"`. Task 1's `attempt_number`/`objective_history` were written against `events()` and switched to `live_events()` in Task 2's commit, matching the plan's own task boundary (Task 2's read_first explicitly names these two functions as "changed in Task 1" and then re-touched here) rather than introducing the retraction machinery inside Task 1's commit._

## Files Created/Modified

- `evidence.py` - `locked()`, `append_line_checked()`, `_tail_dedupe_keys()`, `recent_dedupe_keys()`, `DEDUPE_WINDOW_BYTES`; `append_event()` returns recorded/already_recorded; `attempt_number(log, session_id, item_key, canon)`; `response_event()`'s `canonical` field now `idempotency_canon()`'s output; `retraction_event()`, `retracted_ids()`, `live_events()`, `event_by_id()`; `KNOWN_EVENT_TYPES` gains `"retraction"`
- `surfaces/session.py` - `cmd_submit` computes `canon` before `attempt_number`; skips a duplicate `data["responses"]` append on `already_recorded`; appends a `status` field on the responses it does record
- `surfaces/evidence_cli.py` - `cmd_retract()`; `cmd_evidence`'s output gains `retracted`
- `surfaces/cli.py` - new `retract` subcommand (`event_id`, `--reason` required, `--base`)
- `itembank.py` - `event_by_id`, `live_events`, `locked`, `recent_dedupe_keys`, `retracted_ids`, `retraction_event` exports
- `schemas/response.schema.json` - `canonical` property description/type updated for the new never-null semantics; `mark_event`/`retraction_event` $defs plan-number attribution corrected
- `schemas/report.schema.json` - new optional `retracted` field documented on the objective-history shape
- `schemas/session.schema.json` - new optional `status` field documented on a response record
- `tests/evidence_roundtrip.py` - `test_duplicate_submit_dedupes()`, `test_retraction()`, `rewind_cursor()`, `different_answer()`, `log_lines_for_item()` helpers

## Decisions Made

See `key-decisions` in frontmatter above — five decisions: the `canonical` field's switch to `idempotency_canon()`'s output (and the schema update that had to move with it), the retraction-aware dedupe tail scan landing in Task 1's commit ahead of Task 2's retraction machinery, `attempt_number`'s deliberate two-commit evolution (`events()` → `live_events()`) matching the plan's own task split, `cmd_submit`'s skip-on-duplicate fix, and the mark_event/retraction_event plan-number attribution correction in `response.schema.json`.

## Deviations from Plan

None beyond what the plan's own Task 1 action text explicitly called for (the `canonical` field fix) and one drive-by documentation correction, both logged above as key decisions rather than as unplanned deviations — the plan's own text directed both.

**1. [Rule 1 - Bug, directed by plan text] `response_event()`'s `canonical` field was computed from `runtime.canonical_response()` directly instead of `idempotency_canon()`**
- **Found during:** Task 1, "Confirm the short fallback" action step, which explicitly instructed verifying this and fixing it if not already true
- **Issue:** For a `short` item, the event's `canonical` field was `null` (from `canonical_response()`) while `dedupe_key` was built from `idempotency_canon()`'s `"short:"+sha256(...)` fallback — two different values, meaning `attempt_number`'s "does the most recent event's canonical equal this one" comparison could never work for constructed response, exactly the gap RESEARCH.md's Pitfall 1 names.
- **Fix:** `response_event()` now stores `idempotency_canon()`'s output in `canonical`, matching `dedupe_key`'s input value exactly.
- **Files modified:** `evidence.py`, `schemas/response.schema.json` (description + type narrowed to `string`, per the standing phase rule that a response-event shape change moves the schema with it in the same plan)
- **Verification:** `tests/evidence_roundtrip.py#test_duplicate_submit_dedupes` asserts every `short` event's `canonical` starts with `"short:"`; manually confirmed the test goes red when the fallback is removed; the CI schema step (`schema_validate.py schemas/response.schema.json --jsonl ...`) re-run locally after the change, 0 errors.
- **Committed in:** `4486394` (Task 1 commit)

---

**Total deviations:** 1 (plan-directed bugfix, not a discovered deviation — recorded here because it changed a schema alongside code)
**Impact on plan:** No scope creep; the fix and its schema update are exactly what Task 1's own action text specified.

## Issues Encountered

- **`tests/durability_roundtrip.py`'s kill-probe is intermittently flaky under subprocess load** (pre-existing, out of scope per the standing phase note). Ran cleanly on every full-suite pass during this plan's work (varying record counts across runs, as in every prior plan's summary in this phase), never a failure.
- **Reconstructing atomic per-task commits for `evidence.py`.** Task 1's `attempt_number`/`objective_history` and Task 2's retraction machinery are genuinely interdependent (Task 1's docstring names `live_events`, a Task 2 function). To keep the three commits honest to the plan's own task boundaries rather than landing all of `evidence.py`'s changes in one commit, the executor temporarily reduced the working tree to a true Task-1-only state (no retraction section, `attempt_number`/`objective_history` reading `events()`), re-ran Task 1's full `<verify>` block against that isolated state, committed, then restored the Task 2 additions and re-verified before that commit — rather than committing the combined diff under Task 1's message. No functional impact; this is a process note about how the atomic-commit discipline was honored given the interdependency, not a deviation in the shipped code.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The evidence spine now has one enforced definition of a distinct response, working identically for the four auto-scored types and `short`'s fallback, and reversibility is real: an undo is always a compensating append, verified never to delete anything, with every learner-facing count reading through the retraction filter.
- `evidence.py`'s new surface (`locked`, `append_line_checked`, `recent_dedupe_keys`, `retraction_event`, `retracted_ids`, `live_events`, `event_by_id`) is exported from `itembank.py` and ready for `01-08` (the sqlite index behind `objective_history`'s same signature, explicitly named in that function's own docstring) and `01-09` (which gives `mark_event` its real body, alongside `render_attempt_md`/`render_session_json` reading through `live_events` the same way this plan's `attempt_number`/`objective_history` now do).
- `response.schema.json`'s `retraction_event` $defs shape is descriptive, not yet enforced by a top-level `oneOf` against a raw `evidence.jsonl` line — deliberately out of this plan's `<files>` scope; a later schema-hardening plan can wire it in without redesigning `retraction_event()`'s shape.
- No blockers identified for `01-08` onward. The one open item remains the pre-existing `durability_roundtrip.py` kill-probe timing sensitivity noted in every prior plan's summary in this phase; it did not reproduce during this plan's work.

---
*Phase: 01-evidence-spine-protocol-foundation*
*Completed: 2026-08-06*

## Self-Check: PASSED

- FOUND: evidence.py
- FOUND: surfaces/session.py
- FOUND: surfaces/evidence_cli.py
- FOUND: surfaces/cli.py
- FOUND: itembank.py
- FOUND: schemas/response.schema.json
- FOUND: schemas/report.schema.json
- FOUND: schemas/session.schema.json
- FOUND: tests/evidence_roundtrip.py
- FOUND: 4486394 (Task 1 commit)
- FOUND: bdfb632 (Task 2 commit)
- FOUND: b531be3 (Task 3 commit)
