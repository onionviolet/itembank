---
phase: 10-retention-pacing-trends
plan: 10-02
subsystem: lesson-completion-seam
tags: [lesson, completion, evidence, review-queue, schED-04]
key-files:
  created:
    - fixtures/lesson_retention_events.jsonl
    - tests/lesson_retention_roundtrip.py
  modified:
    - evidence.py
    - retention.py
    - surfaces/lesson.py
    - surfaces/cli.py
    - surfaces/protocol_cli.py
    - schemas/response.schema.json
    - schema_validate.py
    - build.py
    - tests/protocol_roundtrip.py
key-decisions:
  - "A lesson enters the objective review queue ONLY through an explicit, versioned `lesson_complete` evidence event appended by the one writer (SCHED-04, D-24); no page view, scroll, or model event can manufacture it, and the read/render paths stay side-effect-free."
  - "The completion event names stable identifiers only -- bank basename (never a client path, T-10-07), the Phase 3 `lesson_slug()`, the single namespaced subject shared by the referenced objectives, and the sorted unique objective list; the builder canonicalizes and validates every field because the log is append-only."
  - "The queue is a pure retention projection (`retention.lesson_queue`) over the captured snapshot -- one row per referenced objective per completion, with the bounded `lesson_review_after_days` interval, the exact next-review date from the event's local day in its own recorded zone, the event_id + snapshot_id provenance, and reason `lesson review`. No queue store, scheduler file, or second writer exists."
  - "Completion identity = (bank, lesson_slug, subject, sorted objectives, zone), so retrying the identical completion dedupes (`already_recorded`) while a compensating retraction re-enables recording."
  - "`schema_validate.py` gained `uniqueItems` (additive keyword, refused-before it was unsupported): the published schema must itself reject a duplicate objective list, per the plan's contract."
  - "`build.py` STAGE_FILES gained `retention.py` -- a 10-01 gap surfaced by the new lesson.py -> retention import; the packaged `.pyz` otherwise failed on surfaces/settings.py importing retention."
requirements-completed: [SCHED-01, SCHED-04, TREND-05]
completed: 2026-08-15
---

# Plan 10-02 Summary — The Lesson-Completion Seam and the Derived Review Queue

**Objective:** Close SCHED-04 with an explicit, versioned Phase 3 lesson-completion
event and a transparent objective review-queue entry (D-01, D-02, D-04, D-16, D-24).

## What Was Built

- `evidence.lesson_complete_event()` — the one explicit completion event builder
  (validated: non-empty session id, bank basename only, non-empty Phase 3 lesson
  slug, namespaced subject, sorted-unique namespaced objectives, non-empty zone;
  deterministic dedupe identity). Added to `KNOWN_EVENT_TYPES`, appended only
  through `evidence.append_event`.
- `itembank lesson BANK --ref HEADING --complete [--zone Z]` — the explicit
  completion action. Resolves the heading through the Phase 3 slugifier and
  reader (never a second parser/slugger), discovers the sorted unique objectives
  of items referencing it, appends exactly one event, then captures once and
  prints event status, configured interval, derived next-review date, reason and
  snapshot id from the projection. Named refusals: `--complete` without `--ref`,
  unknown heading, heading with no referenced `[OBJECTIVE:]` (D-04), objectives
  spanning subjects.
- `retention.lesson_queue(snapshot)` — the pure queue projection: one stable row
  per referenced objective per completion with interval, exact next-review date
  (event local date in the event's own zone + `lesson_review_after_days`),
  event_id/snapshot_id provenance, and reason `lesson review`. Retraction removes
  the rows from a fresh capture through the existing live-event filter; unreadable
  timestamps/zones degrade by skipping (D-09).
- Published contract: closed `lesson_complete_event` branch in
  `schemas/response.schema.json` (rejects missing/empty slug, empty or duplicate
  objectives, non-namespaced subject/objectives, client path via
  `additionalProperties: false`), with the real CLI-written event and the committed
  fixture validating and every earlier evidence variant still valid (D-16).
- `fixtures/lesson_retention_events.jsonl` — invented completion + compensating
  retraction, validated as a whole log.
- `tests/lesson_retention_roundtrip.py` — fixed-clock harness: explicit
  completion, idempotent retry, retraction removal + re-completion, read-only
  render, named refusals, zone boundary, non-completion events never feeding the
  queue, structural writer-boundary assertions.
- `schema_validate.py`: `uniqueItems` added to the supported keyword set (the
  validator refuses schemas that use unsupported keywords, so this was required
  before the schema could use it).
- `build.py`: `retention.py` staged into the packaged artifact (10-01 gap, surfaced
  by the lesson surface importing retention).

## Commits

| Task | Commit |
|------|--------|
| Task 1 + Task 2 — one atomic commit | (see `git log` — `feat(10-02)` on `phase10`) |

## Verification

- `python tests/lesson_retention_roundtrip.py` — pass
- `python tests/retention_roundtrip.py` — pass
- `python tests/lesson_roundtrip.py` — pass (Phase 3 reader/route contracts intact)
- `python tests/protocol_roundtrip.py` — pass (real completion + fixture validate,
  malformed variants rejected, earlier variants still valid, model events ignored)
- Full suite: every `tests/*_roundtrip.py` green EXCEPT the Windows-only
  `packaging_roundtrip.py` onedir gate — `dist/itembank-sidecar-onedir` is produced
  by `scripts/build_shell.ps1` (PyInstaller `.exe` freeze), which cannot run in
  this Linux bash environment. This is pre-existing and environmental: the
  packaged `.pyz` portion (which 10-02's `build.py` fix repaired) passes all 17
  checks. Flagged for the final handoff; no automated plan should block on it.

## Success Criteria

- SCHED-04 has a real explicit event and a transparent configured queue date. ✓
- No view, scroll, model event, duplicate parser, queue store, or second writer
  can manufacture completion. ✓
- Completion state remains disposable and reproducible from live evidence. ✓
