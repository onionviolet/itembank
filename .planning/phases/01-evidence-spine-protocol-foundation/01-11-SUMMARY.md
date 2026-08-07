---
phase: 01-evidence-spine-protocol-foundation
plan: 11
subsystem: infra
tags: [migration, evidence-log, jsonl, d-13, d-14, evid-06, dry-run, idempotency]

# Dependency graph
requires:
  - phase: 01-07
    provides: "evidence.py's append_event()/append_line_checked()'s recorded/already_recorded dedupe contract, which the migration's own dedupe_key override rides on unmodified, and retraction_event()/live_events() as the undo path a bad migration can be corrected through"
  - phase: 01-09
    provides: "evidence.py's mark_event() (and its own idempotent dedupe key) as the exact shape a hand-edited MARK: line becomes; render_attempt_md()'s documented vocabulary (MARK: pending) confirming the render side of D-11 the migration writes into"
  - phase: 01-10
    provides: "evidence.py's day_tick_event()/load_day_log() as the exact reader/writer pair the migration's daily_log.md path reuses unmodified, and surfaces/day.py's retained comment naming this plan as load_day_log's other caller"
provides:
  - "surfaces/migrate.py: source_key(kind, path, ref), read_attempt_md(path), read_legacy_session(path), scan_legacy(base, legacy_dir), cmd_migrate(a) -- the one-shot, re-runnable, dry-run-first migration from the three legacy stores into _evidence/evidence.jsonl"
  - "itembank.py: read_attempt_md, read_legacy_session, scan_legacy, source_key exports"
  - "surfaces/cli.py: itembank migrate --base --legacy-dir --bank --subject --resolve-by-position --write"
  - "schemas/response.schema.json: mode enum gains 'legacy'; source_ref moves from a placeholder [string, null] to the real kind/path/ref/resolution shape"
  - "fixtures/legacy_attempts/*.md, fixtures/legacy_session.json, fixtures/legacy_daily_log.md -- synthetic pre-migration fixtures reproducing every legacy shape the tool must handle"
affects: []

actuals:
  tokens: 13538
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "A migrated response event's dedupe_key is source_key(kind, basename(path), ref) -- a hash of the legacy record's own identity -- never the live path's session+item+attempt+canonical dedupe_key (D-17). This is deliberate: two different unresolved legacy records (empty item key, similar answer text) could otherwise collide under the live scheme, silently merging two distinct source records into one event."
    - "mark and day_tick events reuse mark_event()/day_tick_event()'s own already-idempotent dedupe keys rather than a source_key override -- both are already correct per D-12/D-11, and day_tick_event()'s (date, lane) key means a tick imported by migration and a tick recorded live through itembank day since plan 01-10 naturally reconcile against each other, not just against a second migration run."
    - "_check_or_write(log, event, write, seen) classifies an event as recorded/already_recorded against an in-memory dedupe-key map (seeded from evidence.recent_dedupe_keys()) without necessarily appending -- this is what makes a dry run's reconciliation match a real run's one-for-one without a second code path."
    - "No resolution by default (D-14): item_id is '' and item_ref carries the original positional reference unless --resolve-by-position is given, in which case a reference is matched against TODAY's bank by current item number and the outcome (unresolved/position) is recorded on the event's own source_ref, never left to operator memory."
    - "A malformed attempt-file section or session-JSON response entry is recorded as {ref, unparsed: True} and counted in a dedicated 'unparsed' bucket -- found and accounted for, never silently dropped, and distinct from 'unresolved' (which has a real item_type but no item_id)."

key-files:
  created:
    - surfaces/migrate.py
    - fixtures/legacy_attempts/sample_bank_attempt_2026-01-02_0900.md
    - fixtures/legacy_attempts/sample_bank_attempt_2026-01-09_1400.md
    - fixtures/legacy_session.json
    - fixtures/legacy_daily_log.md
  modified:
    - surfaces/cli.py
    - itembank.py
    - schemas/response.schema.json
    - tests/evidence_roundtrip.py
    - .gitignore

key-decisions:
  - "Legacy session JSON files are scanned from the same _attempts/ directory as attempt markdown (scan_legacy globs both *.md and *.json there), matching the real on-disk layout ARCHITECTURE.md documents (_attempts/session_*.json) rather than requiring a separate flag to locate them."
  - "An attempt file's item_ref is normalized to the 'q'+number shape (item_ref = \"q\" + heading number) so it is directly comparable to a session record's own item_id and to today's bank's q[\"id\"] field -- one resolution code path (match against resolve_map keyed by q[\"id\"]) serves both legacy sources instead of two."
  - "canonical on a migrated event is a stable hash of the recorded answer text ('migrated:' + sha256), never runtime.canonical_response()'s own output -- an unresolved (or even position-resolved) legacy record does not carry the full item metadata canonical_response() needs for every type (a table/dnd answer needs the item's row count, which an attempt file's rendered text never preserves), and the event's score is taken directly from the source, never recomputed, so canonical's job here is honestly 'what did the answer look like', not scoring compatibility."
  - "attempt_number is fixed at 1 for every migrated record and response_time_ms/confidence/error_category/hint_tier are always null -- a legacy store never captured these, and the Flagged Assumptions section of the plan is explicit that recording a fabricated value would be worse evidence than an honest null (the same option-a posture 01-02 already took)."
  - "--legacy-dir overrides only where attempt markdown/session JSON are read from; daily_log.md always resolves beside --base regardless of --legacy-dir, matching the plan's own phrasing ('daily_log.md beside the given base') rather than folding the tick log under the same override."
  - ".gitignore's *_attempt_*.md rule (aimed at real learner evidence) would have silently excluded the new fixtures/legacy_attempts/*.md files from every git add; carved out an explicit negation for that one directory rather than force-adding gitignored content."

requirements-completed: [EVID-06]

coverage:
  - id: D1
    description: "Running the migration against existing _attempts/*.md, session JSON and daily_log.md produces one evidence store with no recorded response lost: found equals written plus already_present, and the tool fails loudly on a mismatch instead of reporting success"
    requirement: EVID-06
    verification:
      - kind: unit
        ref: "tests/evidence_roundtrip.py#test_migration_reconciliation"
        status: pass
    human_judgment: false
  - id: D2
    description: "itembank migrate is a dry run by default reporting exact counts; importing requires the explicit --write flag"
    requirement: EVID-06
    verification:
      - kind: unit
        ref: "tests/evidence_roundtrip.py#test_migration_reconciliation"
        status: pass
    human_judgment: false
  - id: D3
    description: "Running the migration twice imports zero new events on the second run (already_present covers the whole found total minus any unparsed records, resolved/unresolved are both 0)"
    requirement: EVID-06
    verification:
      - kind: unit
        ref: "tests/evidence_roundtrip.py#test_migration_reconciliation"
        status: pass
    human_judgment: false
  - id: D4
    description: "Killing the migration partway and re-running it produces the same final event count as an uninterrupted run, with at most one malformed log line"
    requirement: EVID-06
    verification:
      - kind: unit
        ref: "tests/evidence_roundtrip.py#test_migration_reconciliation"
        status: pass
    human_judgment: false
  - id: D5
    description: "A legacy record keyed by a positional reference that cannot resolve to an item id imports as unresolved (item_id '', source_ref.resolution 'unresolved') and is counted, never dropped"
    verification:
      - kind: unit
        ref: "tests/evidence_roundtrip.py#test_migration_reconciliation"
        status: pass
    human_judgment: false
  - id: D6
    description: "Position-based resolution is a separately-invoked, explicitly-flagged opt-in (--resolve-by-position); every event it resolves records source_ref.resolution 'position'; no similarity-matching path exists"
    verification:
      - kind: unit
        ref: "tests/evidence_roundtrip.py#test_migration_reconciliation"
        status: pass
      - kind: other
        ref: "python -c \"import re; s=open('surfaces/migrate.py',encoding='utf-8').read(); assert not re.search(r'difflib|SequenceMatcher|ratio\\(', s)\""
        status: pass
    human_judgment: false
  - id: D7
    description: "Migration inputs resolve under --base by default; an explicit --legacy-dir outside --base is rejected with a named error and reads nothing"
    verification:
      - kind: unit
        ref: "tests/evidence_roundtrip.py#test_migration_reconciliation"
        status: pass
    human_judgment: false

duration: ~30min
completed: 2026-08-06
status: complete
---

# Phase 1 Plan 11: Bring the History In Summary

**`itembank migrate` -- a dry-run-first, re-runnable one-shot import of `_attempts/*.md`, session JSON and `daily_log.md` into `_evidence/evidence.jsonl` through the one evidence writer, with unresolved-by-default item attribution and a reconciliation that fails loudly on any count mismatch -- closes phase success criterion 2.**

## Performance

- **Duration:** ~30 min
- **Started:** 2026-08-06T20:10:25-05:00 (continuation from 01-10)
- **Completed:** 2026-08-06T20:41:00-05:00
- **Tasks:** 3
- **Files modified:** 10

## Accomplishments

- `surfaces/migrate.py` is a new module reading the three legacy stores and never writing to them. `source_key(kind, path, ref)` gives every legacy record a deterministic sha256 identity (kind, source file basename, an in-file reference) that becomes a migrated `response` event's `dedupe_key` -- this is what makes "a second run imports nothing new" fall out of `evidence.append_event()`'s own idempotency check, rather than needing separate bookkeeping. `mark` and `day_tick` events reuse `evidence.mark_event()`/`evidence.day_tick_event()`'s own already-idempotent keys instead of the `source_key` override, since both are already correct (D-12/D-11) and a `day_tick`'s `(date, lane)` key means an imported tick and a live-recorded tick from `itembank day` naturally reconcile against each other too.
- `read_attempt_md(path)` splits a pre-01-09 attempt file on `## Item N, type` headings, extracting the auto verdict (`[auto: correct]`/`[auto: WRONG]` into `score`), the selected-answer or verbatim fenced text into `answer`, the objective line, and the `MARK:` line plus per-bullet rubric marks into `mark`/`rubric`. A section whose heading does not parse, or whose type is unrecognized, is recorded as `{"ref": ..., "unparsed": True}` and counted, never dropped. `read_legacy_session(path)` does the same for a session JSON's `responses` array, keyed by array index plus the legacy `item_id`.
- **No resolution by default (D-14).** Every imported response carries `item_id` of `""` and `item_ref` set to the original positional reference (normalized to `"qN"` for both an attempt heading number and a session's own `item_id`, so one resolution path serves both sources) unless `--resolve-by-position BANK.md` is given -- a separate, explicit opt-in that matches a reference against today's bank by current item number and records `source_ref.resolution` of `"position"` on every event it resolves. A reference with no match stays unresolved even under the flag. There is no stem-similarity or fuzzy-matching path, confirmed by a source-text assertion (`difflib|SequenceMatcher|ratio(`).
- **Scope (T-1-03).** `scan_legacy(base, legacy_dir=None)` resolves `_attempts/` (holding both attempt markdown and session JSON, matching the real on-disk layout) and `daily_log.md` beside `base` by default; `--legacy-dir` is resolved with `os.path.abspath` and rejected with `MigrationScopeError` unless it lies inside `os.path.abspath(base)`.
- **Dry run by default.** `cmd_migrate(a)` scans, resolves, builds every event and checks it against the existing log's dedupe keys (`_check_or_write`, seeded from `evidence.recent_dedupe_keys()`) without appending anything unless `--write` is given. It prints house-style `found:`/`wrote:` (or `would write:`) status lines plus a JSON reconciliation object (`schema_version`, `dry_run`, `found`, `written`, `unresolved_refs`), and exits non-zero with every unaccounted reference named if `found` and `written` (resolved + unresolved + unparsed + ticks + already_present) ever disagree.
- Wired as `itembank migrate` in `surfaces/cli.py` (`--base`, `--legacy-dir`, `--bank`, `--subject`, `--resolve-by-position`, `--write`); `source_key`, `read_attempt_md`, `read_legacy_session`, `scan_legacy` exported from `itembank.py`.
- `schemas/response.schema.json`'s `mode` enum gained `"legacy"` (an attempt-file-sourced record has no captured mode) and `source_ref` moved from the placeholder `["string", "null"]` to its real shape (`kind`, `path`, `ref`, `resolution`), matching the standing phase rule that a response-event shape change moves the schema with it. Confirmed against real migrated output: `schema_validate.py schemas/response.schema.json --jsonl` on a filtered set of migrated `response` lines reports 0 errors.
- Four synthetic fixtures (`fixtures/legacy_attempts/*.md` x2, `fixtures/legacy_session.json`, `fixtures/legacy_daily_log.md`) deliberately cover every legacy shape: auto correct/WRONG verdicts, a passed short-answer mark with per-bullet rubric marks, an unmarked short answer, an item heading (`## Item 9, mc`) with no corresponding bank item, a hand-corrupted section heading, an unfinished sitting, and a day log whose header names one fewer lane than the current build (the pre-sixth-lane case `load_day_log`'s docstring describes).
- `tests/evidence_roundtrip.py#test_migration_reconciliation()` proves EVID-06 and both of its probe edges against a total computed independently of `surfaces/migrate.py` (a plain `## Item ` count, `len(responses)`, and `surfaces.day.load_day_log`'s own tick mapping -- never `scan_legacy`): dry run appends nothing and matches the independent count; a `--write` run's written-plus-already_present accounts for the whole found total; a second `--write` run imports zero new events; an interrupted-then-resumed run reaches the same total with at most one malformed line; every `q9` response is present, unresolved, and empty-`item_id`; `--resolve-by-position` resolves `q1`-`q6` while `q9` stays unresolved; `--legacy-dir` outside `--base` is rejected and appends nothing; and the legacy files are byte-identical before and after every run.

## Task Commits

Each task was committed atomically:

1. **Task 1: Write the three synthetic legacy fixtures** - `7a3aaaa` (feat)
2. **Task 2: Build the dry-run-first, re-runnable migration** - `b308446` (feat)
3. **Task 3: Prove the counts reconcile, twice and after an interruption** - `095a3aa` (test)

_Note: no TDD red/green/refactor split was called for; all three tasks are `type="auto"`._

## Files Created/Modified

- `surfaces/migrate.py` (new) - `source_key()`, `read_attempt_md()`, `read_legacy_session()`, `scan_legacy()`, `MigrationScopeError`, `cmd_migrate()` and its `_build_response_event()`/`_check_or_write()`/`_migrated_canon()`/`_namespace_objective()`/`_bank_from_attempt_filename()` helpers
- `fixtures/legacy_attempts/sample_bank_attempt_2026-01-02_0900.md`, `fixtures/legacy_attempts/sample_bank_attempt_2026-01-09_1400.md` - synthetic pre-migration attempt files
- `fixtures/legacy_session.json` - synthetic pre-`served_ts` session JSON
- `fixtures/legacy_daily_log.md` - synthetic pre-sixth-lane day log
- `surfaces/cli.py` - new `migrate` subcommand
- `itembank.py` - `read_attempt_md`, `read_legacy_session`, `scan_legacy`, `source_key` added to the `from surfaces.migrate import (...)` block and `__all__`
- `schemas/response.schema.json` - `mode` enum gains `"legacy"`; `source_ref` fleshed out to the real `kind`/`path`/`ref`/`resolution` shape
- `tests/evidence_roundtrip.py` - `_lay_out_legacy_tree()`, `_independent_legacy_count()`, `_fingerprint_legacy_files()`, `migrate_json()`, `test_migration_reconciliation()`
- `.gitignore` - carved `fixtures/legacy_attempts/*_attempt_*.md` out of the `*_attempt_*.md` learner-evidence ignore rule

## Decisions Made

See `key-decisions` in frontmatter above -- six decisions: scanning session JSON from the same `_attempts/` directory as attempt markdown; normalizing an attempt file's `item_ref` to `"qN"` so one resolution path serves both legacy sources; a migration-specific `canonical` field (a stable answer-text hash) rather than reusing `runtime.canonical_response()`, which cannot be computed honestly for every type from a rendered legacy record; fixing `attempt_number` at 1 and every EVID-07 capture field at `null` for a migrated record; `--legacy-dir` overriding only the attempts location, never `daily_log.md`'s; and the `.gitignore` carve-out for the new fixture files.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] `.gitignore`'s `*_attempt_*.md` rule would have silently excluded the new fixtures**
- **Found during:** Task 1, staging the newly-written fixture files for commit
- **Issue:** `.gitignore` already carries `*_attempt_*.md` (aimed at real learner attempt files, which must never enter the repo). The plan's own required fixture filenames (`fixtures/legacy_attempts/sample_bank_attempt_2026-01-02_0900.md` and the second file) match that pattern, so `git add` would have silently staged nothing for them -- a required, plan-named artifact would never reach the commit at all.
- **Fix:** Added a scoped negation (`!fixtures/legacy_attempts/`, `!fixtures/legacy_attempts/*_attempt_*.md`) rather than force-adding gitignored content, so the carve-out is visible and permanent in `.gitignore` itself instead of a one-off `git add -f`.
- **Files modified:** `.gitignore`
- **Verification:** `git status --short fixtures/` showed the two new files as untracked (not ignored) after the edit; `git add` staged them normally.
- **Committed in:** `7a3aaaa` (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (blocking gitignore conflict), found while staging Task 1's own required deliverables.
**Impact on plan:** No scope creep -- the fix only makes the plan's own named fixture paths committable; nothing else in `.gitignore`'s learner-evidence protection changed.

## Issues Encountered

- **`tests/durability_roundtrip.py`'s kill-probe is intermittently flaky under subprocess load** (pre-existing, out of scope per the standing phase note carried in every prior plan's summary). Ran cleanly on every full-suite pass during this plan's work; not chased.
- The reconciliation test's second-run and interruption-resume assertions initially compared `already_present` against the full found total directly; the deliberately-corrupted fixture section (an intentional, permanent "unparsed" record that never reaches `append_event` at all) meant `already_present` alone never equals the found total on a repeat run -- it equals `found total minus unparsed`. Caught immediately by the test's own first run (a genuine red, not a hand-flipped negative-test check) and fixed before committing Task 3.

## User Setup Required

None - no external service configuration required. The plan's own `<human-check>` step (running `itembank migrate --base <your private bank directory>` against real history) is optional operator verification outside this executor's scope, not a setup requirement.

## Next Phase Readiness

- Phase success criterion 2 ("running the one-time migration against existing `_attempts/*.md`, session JSON and `daily_log.md` produces a single evidence store with no recorded response lost, verified by comparing pre- and post-migration counts") is now real and automated: `itembank migrate` reconciles `found` against `written` on every run and fails loudly on any mismatch, and `test_migration_reconciliation` proves it against an independently-computed total.
- This is the last plan in Phase 1 (`evidence-spine-protocol-foundation`). Every store that used to write independently (`_attempts/*.md`, session JSON, `daily_log.md`) is now either a render over the log (01-09/01-10) or a one-time importable history (this plan); `evidence.py`'s writer, reader, idempotency, retraction, disposable index, renders, marks and day ticks are all in place and tested.
- No blockers identified. The one open item remains the pre-existing `durability_roundtrip.py` kill-probe timing sensitivity noted in every prior plan's summary in this phase; it did not reproduce during this plan's work.

---
*Phase: 01-evidence-spine-protocol-foundation*
*Completed: 2026-08-06*

## Self-Check: PASSED

- FOUND: surfaces/migrate.py
- FOUND: fixtures/legacy_attempts/sample_bank_attempt_2026-01-02_0900.md
- FOUND: fixtures/legacy_attempts/sample_bank_attempt_2026-01-09_1400.md
- FOUND: fixtures/legacy_session.json
- FOUND: fixtures/legacy_daily_log.md
- FOUND: tests/evidence_roundtrip.py
- FOUND: schemas/response.schema.json
- FOUND: surfaces/cli.py
- FOUND: itembank.py
- FOUND: .gitignore
- FOUND: 7a3aaaa (Task 1 commit)
- FOUND: b308446 (Task 2 commit)
- FOUND: 095a3aa (Task 3 commit)
