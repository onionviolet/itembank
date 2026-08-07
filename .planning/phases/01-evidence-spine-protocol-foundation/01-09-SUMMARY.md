---
phase: 01-evidence-spine-protocol-foundation
plan: 09
subsystem: infra
tags: [renders, marking, evidence-log, jsonl, d-11, d-12, evid-03, evid-07]

# Dependency graph
requires:
  - phase: 01-07
    provides: "evidence.py's live_events()/retracted_ids() (D-10) as the retraction-aware read path session_events()/marks_by_event() build on, and append_event()'s recorded/already_recorded contract that mark_event() reuses unchanged"
  - phase: 01-08
    provides: "the disposable sqlite3 index proving the log is the sole authority -- the same posture the renders in this plan extend to the attempt markdown and the session JSON"
provides:
  - "evidence.py: session_events(log, session_id), marks_by_event(log), render_attempt_md(log, session_id, qs, bank_path), render_session_json(log, session_id, qs, bank_path), mark_event(session_id, item_id, item_ref, marks_event, verdict, rubric, notes, marker) -- D-11's views and D-12's first-class mark event"
  - "surfaces/evidence_cli.py: cmd_render() (attempt|session|daily, daily reserved for 01-10) and cmd_mark() (--file NDJSON, --marks inline JSON array, or --item/--verdict single-mark form)"
  - "surfaces/cli.py: new 'render' and 'mark' subcommands"
  - "itembank.py: session_events, marks_by_event, render_attempt_md, render_session_json, mark_event exports"
  - "GRADING.md: rewritten for the command-based marking flow"
  - "schemas/response.schema.json: mark_event $defs describes the real shape"
affects: [01-10, 01-11]

actuals:
  tokens: 15040
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "session_events()/marks_by_event() read exclusively through live_events(), never events() -- the same D-10 read-side-filter discipline attempt_number()/objective_history() already established, extended here to renders so a retracted response or a retracted mark vanishes from a view exactly as it vanishes from a count."
    - "Neither render reads the session JSON file at all -- render_attempt_md/render_session_json take only (log, session_id, qs, bank_path). This is what makes D-11 real: the session file cannot be an input to its own render, on pain of reintroducing the two-writers problem. The consequence, stated in both functions' docstrings rather than hidden: neither render can know a session's original item selection or cursor, so 'finished' isn't claimed and render_session_json's items/cursor/status describe only what the log itself proves happened."
    - "A mark never mutates the response event it grades. review_state is computed at read time in every caller (marks_by_event's result), never written back onto the immutable response event -- the response event's own score stays null forever for a short item, marked or not."
    - "cmd_mark resolves and validates every entry in a batch BEFORE appending any of them, so a batch containing one item_ref that was never answered in the session appends nothing at all, not a partial prefix of the batch that happened to resolve first."
    - "mark_event()'s dedupe_key follows response_event()'s own idempotency shape (D-17): sha256 over (session_id, marks_event, verdict, canonicalized rubric), so a replayed identical batch reports already_recorded with zero log growth, and a genuinely corrected verdict or rubric always opens a new live mark."

key-files:
  created: []
  modified:
    - evidence.py
    - surfaces/evidence_cli.py
    - surfaces/cli.py
    - itembank.py
    - GRADING.md
    - schemas/response.schema.json
    - tests/evidence_roundtrip.py

key-decisions:
  - "review_state on rendered session-JSON response records is an additive field ('n/a'/'pending'/'marked'), not in session.schema.json's required list -- the schema has no additionalProperties:false on response_record, so this is safe to add without a schema change, and it is what makes the marked/pending distinction visible from render_session_json the same way it is from render_attempt_md's MARK: line."
  - "render_session_json cannot recover a session's original seed, item selection, or cursor from the log alone (only the session file ever held those). Documented rather than guessed at: seed always reports 0, items/cursor are derived from the distinct item_refs the log proves were answered, and status is 'complete' whenever there is at least one response and 'active' when there are none -- by construction, not by comparing against an item count this function has no way to see."
  - "cmd_mark validates and resolves the whole batch before appending anything (two-pass), rather than resolve-then-append per entry in one pass as the plan's action text describes literally. This makes 'a batch with one bad item_ref appends nothing' true regardless of that entry's position in the batch, not just when it happens to be first."
  - "verdict is stored as a boolean (true=pass, false=fail) on the mark event, matching the boolean score already used on response events, rather than as the string 'pass'/'fail' the single-mark CLI convenience form (--verdict pass|fail) accepts. cmd_mark normalizes both the NDJSON batch's boolean/string verdict and the CLI's pass/fail string to one boolean before calling mark_event(), so the two input shapes the plan specifies (NDJSON true/false, --verdict pass|fail) converge on one representation rather than the event's own shape depending on which form recorded it."
  - "GRADING.md was rewritten in full rather than annotated, per the plan's own instruction ('Every one of those instructions is now wrong and must be replaced rather than annotated') -- every reference to hand-editing a MARK: line is gone, replaced by itembank render attempt / itembank mark."

requirements-completed: [EVID-03, EVID-07]

coverage:
  - id: D1
    description: "The attempt markdown and the session JSON are generated on demand from the evidence log; neither is read back as an input by anything, and the log is the only place a response is stored"
    requirement: EVID-03
    verification:
      - kind: unit
        ref: "tests/evidence_roundtrip.py#test_renders_match_log"
        status: pass
    human_judgment: false
  - id: D2
    description: "Rendering the same session twice produces byte-identical output; rendering after an unrelated event for a different session produces the same bytes again"
    requirement: EVID-03
    verification:
      - kind: unit
        ref: "tests/evidence_roundtrip.py#test_renders_match_log"
        status: pass
    human_judgment: false
  - id: D3
    description: "Events sharing an identical ts render in log order, stable across repeated renders and across an explicit --rebuild-index of the (unrelated) disposable query index"
    requirement: EVID-03
    verification:
      - kind: unit
        ref: "tests/evidence_roundtrip.py#test_renders_match_log"
        status: pass
    human_judgment: false
  - id: D4
    description: "A short answer is marked by a command that accepts a batch -- three answers in one invocation -- and each mark lands as a timestamped mark event rather than a hand-edited line in a file"
    requirement: EVID-07
    verification:
      - kind: unit
        ref: "tests/evidence_roundtrip.py#test_mark_flow"
        status: pass
    human_judgment: false
  - id: D5
    description: "A marked response renders with the recorded verdict and each rubric point's outcome; an unmarked short response renders as pending, a different state from wrong, and the underlying response event's score stays null throughout"
    requirement: EVID-07
    verification:
      - kind: unit
        ref: "tests/evidence_roundtrip.py#test_mark_flow"
        status: pass
    human_judgment: false
  - id: D6
    description: "Marking the same response twice with the same verdict records one mark event and reports already_recorded; marking it with a different verdict records a second mark, and the most recent live mark is the one every view uses; retracting that correction restores the original verdict"
    requirement: EVID-07
    verification:
      - kind: unit
        ref: "tests/evidence_roundtrip.py#test_mark_flow"
        status: pass
    human_judgment: false
  - id: D7
    description: "evidence.py contains no function that recomputes a verdict, and a mark never mutates the response event it grades"
    verification:
      - kind: other
        ref: "python -c \"import re; s=open('evidence.py',encoding='utf-8').read(); assert not re.search(r'(?m)^def \\w*score\\w*\\(', s)\" (exit 0); tests/evidence_roundtrip.py#test_mark_flow asserts the short item's response event score is None throughout"
        status: pass
    human_judgment: false

duration: ~12min
completed: 2026-08-06
status: complete
---

# Phase 1 Plan 9: Renders and Marking Summary

**The attempt markdown and the session JSON stop being written files and become pure functions of `_evidence/evidence.jsonl` (`render_attempt_md`, `render_session_json`), and manual `short`-answer marking moves from a hand-edited `MARK:` line to a batch `itembank mark` command that appends first-class, correctable, undoable `mark` events — closing the two-writers gap EVID-03/D-11 exists to end.**

## Performance

- **Duration:** ~12 min
- **Started:** 2026-08-06T19:34:10-05:00
- **Completed:** 2026-08-06T19:46:28-05:00
- **Tasks:** 3
- **Files modified:** 7

## Accomplishments

- `evidence.py` gained `session_events(log, session_id)` (every LIVE response event for one session, in stable `(ts, log order)`, built on `live_events` so a retracted response vanishes from a render exactly as it vanishes from a count) and `marks_by_event(log)` (the most recent LIVE `mark` event per response `event_id`, read the same way -- a retracted mark leaves the response pending again).
- `render_attempt_md(log, session_id, qs, bank_path)` reproduces `surfaces/quiz.attempt_markdown`'s document shape (title, status line, per-item sections, short-item rubric block) built entirely from the log and the parsed bank, with two deliberate differences: the provenance line names the session and states plainly that editing the file changes nothing, and the `MARK:` line reports `pending` or the recorded verdict/rubric outcomes read through `marks_by_event` instead of accepting a hand edit. It reuses `runtime.response_text()` for the selected-answer line, so option *text* (not a reshuffle-fragile letter) survives the move to a render.
- `render_session_json(log, session_id, qs, bank_path)` reconstructs the session dict shape `surfaces/session.py` writes today, from `session_events()` alone. Documented rather than silently approximated: `seed` cannot be recovered from the log (always 0), and `items`/`cursor`/`status` describe exactly what the log proves happened (every distinct item_ref with a live response), not the session's original selection, which only the session file itself ever held.
- `mark_event(session_id, item_id, item_ref, marks_event, verdict, rubric, notes, marker)` builds a first-class mark event: `verdict` coerced to boolean, `rubric` a list of `{point, pass}`, `marker` rejected outright with `ValueError` unless `"human"` (T-1-24 -- a model verdict is not accepted evidence before Phase 8/TEACH-09), and a `dedupe_key` over `(session_id, marks_event, verdict, canonicalized rubric)` matching `response_event()`'s own D-17 idempotency shape.
- `surfaces/evidence_cli.py` gained `cmd_render()` (`itembank render attempt|session|daily --session ID --bank BANK.md [--out FILE]`, atomic tmp-then-`os.replace()` write per T-1-22, `daily` reserved with a named "not yet implemented" exit rather than silently no-oping) and `cmd_mark()` (`--file` NDJSON or `-` for stdin, `--marks` inline JSON array, or `--item`/`--verdict` for one answer -- exactly one required; every entry's `item_ref` is resolved to its most recent live response event and the WHOLE batch is validated before anything is appended, so an unresolved reference anywhere in the batch appends nothing at all).
- `surfaces/cli.py` wires `render` and `mark` subcommands; `itembank.py` exports the five new `evidence.py` functions.
- `GRADING.md` was rewritten in full for the command-based flow: rendering an attempt (`itembank render attempt`), a worked NDJSON batch example, the single-mark convenience form, what a rubric entry looks like, correcting a mark by remarking, undoing one with `itembank retract`, and the standing rule that a model's proposed verdict is not accepted evidence in this milestone.
- `schemas/response.schema.json`'s `mark_event` `$defs` entry moved from a placeholder (`event_type` const only) to the real shape (`session_id`, `item_id`, `item_ref`, `marks_event`, `verdict`, `rubric`, `notes`, `marker`, `dedupe_key`), per the standing phase rule that a payload shape change moves the schema in the same plan.
- `tests/evidence_roundtrip.py` gained `test_renders_match_log()` and `test_mark_flow()`, both checked against a shared `drive_full_session()` helper and against the log directly (`itembank.session_events`) rather than against the renders' own output.

## Task Commits

Each task was committed atomically:

1. **Task 1: Generate the attempt markdown and the session JSON from the log** - `d17db41` (feat)
2. **Task 2: Make marking a batch command that appends events** - `d32a189` (feat)
3. **Task 3: Pin the renders against the log in tests/evidence_roundtrip.py** - `65557aa` (test)

_Note: no TDD red/green/refactor split was called for; all three tasks are `type="auto"`._

## Files Created/Modified

- `evidence.py` - `session_events()`, `marks_by_event()`, `render_attempt_md()`, `render_session_json()`, `mark_event()`, `MARK_EVENT_TYPE`; `KNOWN_EVENT_TYPES` gains `"mark"`; `_tail_dedupe_keys()` generalized (see Deviations)
- `surfaces/evidence_cli.py` - `cmd_render()`, `cmd_mark()` and its `_resolve_marks_event()`/`_normalize_verdict()`/`_normalize_rubric()`/`_load_marks_batch()` helpers
- `surfaces/cli.py` - new `render` subcommand (`kind`, `--session`, `--bank`, `--base`, `--out`) and `mark` subcommand (`--session`, `--base`, `--file`, `--marks`, `--item`, `--verdict`)
- `itembank.py` - `session_events`, `marks_by_event`, `render_attempt_md`, `render_session_json`, `mark_event` added to the `from evidence import (...)` block and `__all__`
- `GRADING.md` - rewritten in full for the `itembank mark`/`itembank render attempt` flow
- `schemas/response.schema.json` - `mark_event` `$defs` fleshed out to the real shape
- `tests/evidence_roundtrip.py` - `drive_full_session()`, `mark_json()`, `test_renders_match_log()`, `test_mark_flow()`

## Decisions Made

See `key-decisions` in frontmatter above — five decisions: the additive `review_state` field on rendered session-JSON responses; the documented, honest approximation `render_session_json` makes for `seed`/`items`/`cursor`/`status` given it never reads the session file; `cmd_mark`'s two-pass resolve-then-append (stronger than the plan's literal per-entry description); `verdict` normalized to boolean across both input shapes the plan specifies; and the full rewrite (not annotation) of `GRADING.md`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `_tail_dedupe_keys()` only tracked dedupe keys for `event_type == "response"`, so a mark's own `dedupe_key` was never honoured**
- **Found during:** Task 2, manually confirming the "re-running an identical batch reports already_recorded" acceptance criterion
- **Issue:** `append_line_checked()`'s dedupe check (`_tail_dedupe_keys`, written in plan 01-07 before `mark` events existed) explicitly skipped any event whose `event_type` was not `"response"`. A replayed identical mark batch therefore never found its own prior mark in the scanned tail and recorded a duplicate mark event every time, instead of reporting `already_recorded` -- breaking D-12's stated idempotency requirement for the mark command.
- **Fix:** Generalized the tail scan to track the dedupe key of any event carrying a non-null `dedupe_key` (response or mark today), rather than hardcoding `event_type == "response"`. A retraction is still handled by its own explicit branch beforehand (its `dedupe_key` is always `None` regardless).
- **Files modified:** `evidence.py`
- **Verification:** `tests/evidence_roundtrip.py#test_mark_flow` asserts a replayed identical NDJSON batch reports `already_recorded` for all three entries and the log's line count is unchanged; `test_duplicate_submit_dedupes` (01-07) and `test_retraction` (01-07) both re-ran green after the change, confirming response-event dedupe and retraction-window behavior are unaffected.
- **Committed in:** `d32a189` (Task 2 commit)

---

**Total deviations:** 1 auto-fixed bug, found during the plan's own mandated manual confirmation of a stated acceptance criterion.
**Impact on plan:** No scope creep -- a structural correctness fix inside the exact idempotency guarantee Task 2's action text specifies for the mark command, with no new capability beyond what the task already required.

## Issues Encountered

- **`tests/durability_roundtrip.py`'s kill-probe is intermittently flaky under subprocess load** (pre-existing, out of scope per the standing phase note carried in every prior plan's summary). Ran cleanly on every full-suite pass during this plan's work; not chased.
- Confirmed both of Task 3's own mandated negative-test discriminators by hand: temporarily swapping `live_events()` for `events()` inside `session_events()` turned `test_renders_match_log` red at the retraction assertion (`session_events` did not drop by one), and temporarily making `marks_by_event()` keep the *first* mark instead of the most recent turned `test_mark_flow` red at the corrected-verdict assertion (`MARK: FAIL` never appeared). Both changes were reverted immediately after observing red; neither was committed.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase success criterion (EVID-03: "One evidence store replacing three") is now real for two of the three legacy stores: the attempt markdown and the session JSON are both generated views over `_evidence/evidence.jsonl`, proven byte-stable, log-ordered, and retraction-aware by `test_renders_match_log`. The third, `daily_log.md`, is explicitly deferred to plan 01-10 -- `cmd_render`'s `daily` kind already exists in the CLI surface and exits with a named "not yet implemented" error rather than silently doing nothing, so the gap stays visible until 01-10 fills it.
- `evidence.py`'s new surface (`session_events`, `marks_by_event`, `render_attempt_md`, `render_session_json`, `mark_event`, `MARK_EVENT_TYPE`) is exported from `itembank.py` and ready for 01-10's `render_daily_log()` to follow the same read-through-`live_events()` pattern.
- The `_tail_dedupe_keys()` generalization fixed in this plan also means any future event type that carries a real `dedupe_key` (the reserved `day_tick` event named in `schemas/response.schema.json`, arriving in 01-10) will dedupe correctly without a further edit to that function.
- No blockers identified for `01-10` onward. The one open item remains the pre-existing `durability_roundtrip.py` kill-probe timing sensitivity, unaffected by this plan's changes.

---
*Phase: 01-evidence-spine-protocol-foundation*
*Completed: 2026-08-06*

## Self-Check: PASSED

- FOUND: evidence.py
- FOUND: surfaces/evidence_cli.py
- FOUND: surfaces/cli.py
- FOUND: itembank.py
- FOUND: GRADING.md
- FOUND: schemas/response.schema.json
- FOUND: tests/evidence_roundtrip.py
- FOUND: d17db41 (Task 1 commit)
- FOUND: d32a189 (Task 2 commit)
- FOUND: 65557aa (Task 3 commit)
