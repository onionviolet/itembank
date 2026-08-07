---
phase: 01-evidence-spine-protocol-foundation
plan: 08
subsystem: infra
tags: [sqlite3, index, query, evidence-log, jsonl, evid-04, evid-08, d-08]

# Dependency graph
requires:
  - phase: 01-02
    provides: "evidence.py's objective_history(log, objective) stub (a linear scan behind a fixed signature) and cmd_evidence's original --objective-only surface, which this plan replaces the internals of without changing the callers"
  - phase: 01-07
    provides: "live_events()/retracted_ids() (D-10) as the retraction-aware read path both the sqlite projection and its linear-scan fallback build on; locked() as the shared advisory-lock primitive ensure_index() reuses for its own on-disk .lock file"
provides:
  - "evidence.py: INDEX_VERSION, rebuild_index(), index_stale(), ensure_index() -- the disposable sqlite3 projection (D-08), full-rebuild-or-incremental with a truncation-safe staleness rule, wrapped in degrade-never-block fallback"
  - "evidence.py: index_for_log(), event_matches(), objective_rollup(), and the rewritten objective_history(log, objective, prefix, subject, mode, session_id, since) -- one query answering the objective question across every session and subject, indexed with a live_events() fallback that agrees with it exactly"
  - "surfaces/evidence_cli.py: cmd_evidence gains --prefix/--subject/--mode/--session/--since/--rebuild-index, by_mode/index/index_rebuilt output keys, and a single ensure_index() call site (inside objective_history()) that cmd_evidence deliberately does not duplicate"
  - "surfaces/cli.py: evidence subparser's new flags; --objective no longer required"
  - "itembank.py: INDEX_VERSION, ensure_index, event_matches, index_for_log, index_stale, objective_rollup, rebuild_index exports"
  - "schemas/report.schema.json: objective_history variant documents by_mode/index/index_rebuilt as optional additive fields"
  - "tests/evidence_roundtrip.py: test_objective_query(), test_index_is_disposable(), extended test_mode_recorded(), flatten() helper"
affects: [01-09, 01-10, 01-11]

actuals:
  tokens: 12200
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "sqlite3 imported lazily inside _index_connect() only, never at module top -- evidence.py still imports and evidence still records/reads through live_events() on a Python build without sqlite3."
    - "Full rebuild writes to index + '.tmp' then os.replace()s into place, the same tmp-then-replace pattern runtime.write_session() uses for a session file, so a half-built index can never replace a good one."
    - "index_stale() treats an unopenable or corrupted index identically to a missing one (return True, 0, full rebuild) by catching the open/query exception internally, rather than letting it escape to whichever caller happens to be checking staleness at the time."
    - "objective_history() is the ONE call site that invokes ensure_index() -- cmd_evidence deliberately does not call it a second time to learn 'used'/'fallback' status, inferring it afterward via a read-only index_stale() check instead, so a regression that skips ensure_index() inside objective_history() is observable rather than silently masked by a redundant refresh happening beside it."
    - "event_matches(ev, objective, prefix, subject, mode, session_id, since) is the one filter predicate both the indexed SQL path and the live-scan fallback implement identically, and that surfaces/evidence_cli.py reuses to count retracted rows under the same query -- so the three cannot silently disagree about what a query matched."
    - "Prefix matching is two escaped LIKE clauses (objective LIKE 'x.%' ESCAPE '\\' OR objective LIKE 'x:%' ESCAPE '\\'), never a bare LIKE 'x%', so 'emt:airway' can never also match 'emt:airwaymanagement'."

key-files:
  created: []
  modified:
    - evidence.py
    - itembank.py
    - schemas/report.schema.json
    - surfaces/cli.py
    - surfaces/evidence_cli.py
    - tests/evidence_roundtrip.py

key-decisions:
  - "objective_history() keeps returning a bare list of row dicts (not a (rows, status) tuple), per the plan's explicit 'keep the returned row shape exactly as plan 01-02 defined it' instruction. This means cmd_evidence cannot learn the index's used/fallback status from objective_history()'s return value directly; it infers status after the query via a read-only evidence.index_stale() check instead of calling ensure_index() a second time, which would have masked the exact regression Task 3's acceptance criteria asks the tests to catch."
  - "index_stale()'s open/query step (connecting to the index file and reading its meta table) is wrapped in its own try/except, catching a corrupt file or a directory sitting at the index path and returning (True, 0) rather than letting the exception propagate. The plan's docstring text already listed 'an index that cannot even be opened' as a full-rebuild trigger, but the first-draft implementation only wrapped that step in try/finally (for connection cleanup), not try/except -- an exception there would have escaped index_stale() uncaught. Found and fixed while manually confirming test_index_is_disposable's acceptance-criteria 'goes red' check (see Deviations)."
  - "--rebuild-index's 'say so in the output' instruction is implemented as an additive index_rebuilt boolean field, keeping the index field's own vocabulary strictly to 'used'/'fallback' as the plan's own text specifies, rather than adding a third value to that field."
  - "The plan's action text describes an optional dual-format ('human-readable form... one line per event... followed by the per-mode rollup') alongside the JSON output. Not implemented: cmd_evidence's existing five callers (test_tracer_end_to_end, test_mode_recorded, test_empty_log, test_duplicate_submit_dedupes, test_retraction, all from plans 01-02/01-07) parse the full captured stdout as one JSON document via json.loads(out); printing any additional text around that document would raise 'Extra data' in every one of them. No CLI flag to select the human form is listed among the six flags the plan itself enumerates for cli.py, and the plan's own 'Created by this plan' artifact list for surfaces/evidence_cli.py names only two new output keys (by_mode, index), not a second output mode. Read together, JSON-only is the literal, testable contract; the prose is describing an aspiration this plan's own artifact list does not commit to. Counts and the trail are still presented and nothing else (the gamification-key prohibition), satisfied structurally within the one JSON document."
  - "schemas/report.schema.json was updated even though it is not named in the plan's frontmatter files_modified or Task 2's <files> list, because the plan's own read_first section names it explicitly and the standing phase rule (recorded in every prior plan's prompt) requires a schema to move with any payload shape change in the same plan. Documented as a Rule 2 addition below."

requirements-completed: [EVID-04, EVID-08]

coverage:
  - id: D1
    description: "One query (itembank evidence) answers 'how am I doing on objective X over time' across every session and every subject, reading from the log; the disposable sqlite3 index is a cache in front of it that can be deleted, corrupted, or made permanently unwritable with no change in answer"
    requirement: EVID-04
    verification:
      - kind: unit
        ref: "tests/evidence_roundtrip.py#test_objective_query"
        status: pass
      - kind: unit
        ref: "tests/evidence_roundtrip.py#test_index_is_disposable"
        status: pass
    human_judgment: false
  - id: D2
    description: "Exact objective match is the default; --prefix matches an objective beginning with the argument followed by '.' or ':' and never a longer word sharing the same stem (emt:airway vs emt:airwaymanagement)"
    requirement: EVID-04
    verification:
      - kind: unit
        ref: "tests/evidence_roundtrip.py#test_objective_query"
        status: pass
    human_judgment: false
  - id: D3
    description: "A drill-mode correct and an exam-mode correct on the same item are reported in separate by_mode buckets and never summed into one combined figure anywhere in the query output"
    requirement: EVID-08
    verification:
      - kind: unit
        ref: "tests/evidence_roundtrip.py#test_mode_recorded"
        status: pass
    human_judgment: false
  - id: D4
    description: "Events sharing an identical ts are returned in stable log order, unchanged by a --rebuild-index; an unused objective returns count 0 and exits 0 rather than raising"
    requirement: EVID-04
    verification:
      - kind: unit
        ref: "tests/evidence_roundtrip.py#test_objective_query"
        status: pass
    human_judgment: false
  - id: D5
    description: "Every SQL filter value is bound as a ? parameter, never concatenated or %-formatted into the query text (T-1-19); confirmed no execute() call's SQL argument contains a % or + operator"
    verification:
      - kind: other
        ref: "grep -n '.execute(' evidence.py, manually inspected -- no line building an execute() SQL argument uses % or +"
        status: pass
    human_judgment: false
  - id: D6
    description: "The output JSON never carries a gamification key (points, level, badge, badges, streak, xp, score_total) anywhere in its structure, per PROJECT.md's Out of Scope table"
    verification:
      - kind: unit
        ref: "tests/evidence_roundtrip.py#test_mode_recorded (flatten() recursive key walk)"
        status: pass
    human_judgment: false

duration: ~21min
completed: 2026-08-06
status: complete
---

# Phase 1 Plan 8: Query Objective History via Disposable SQLite Index Summary

**A `sqlite3` projection rebuilt from `_evidence/evidence.jsonl` (full or incremental, truncation-safe, deletable at any time with no loss) now answers `itembank evidence`'s cross-subject, cross-session objective query, with `--prefix`/`--subject`/`--mode`/`--session`/`--since`/`--rebuild-index` filters and a per-mode `by_mode` rollup that keeps a drill correct and an exam correct apart.**

## Performance

- **Duration:** ~21 min
- **Started:** 2026-08-06T18:56Z (approx, continuation from 01-07)
- **Completed:** 2026-08-06T19:18Z
- **Tasks:** 3
- **Files modified:** 6

## Accomplishments

- `evidence.py` gained `INDEX_VERSION`, `rebuild_index(log, index)` (full rebuild through `index + ".tmp"` then `os.replace()`, built on `events(log)` so a torn line warns and is skipped rather than aborting), `index_stale(log, index)` (returns `(stale, offset)`; missing/unopenable/corrupt index, a version mismatch, or a log smaller than the index's own recorded `log_bytes` all force `offset` 0; unchanged size+mtime is the only "not stale" case), and `ensure_index(log, index)` (applies that rule under the same `locked()` advisory lock `append_line` takes, re-checks staleness once the lock is held, and wraps the whole operation so an index that cannot be built falls back to `"fallback"` rather than blocking a query). `sqlite3` is imported lazily inside `_index_connect()` alone.
- `objective_history(log, objective, prefix=False, subject=None, mode=None, session_id=None, since=None)` is now the real data layer plan 01-02's tracer stubbed: it calls `ensure_index()` and queries the sqlite3 projection when it answers `"used"`, or falls back to a `live_events()` linear scan — using the exact same `event_matches()` predicate — when it cannot be built at all. Default is exact objective equality; `--prefix` matches an objective equal to or beginning with the argument followed by `.` or `:`, implemented as two parameterized, escaped `LIKE` clauses rather than a bare `LIKE 'x%'` so `emt:airway` never also matches `emt:airwaymanagement`. `--subject` filters on the indexed `subject` column alone, ignoring `--objective` entirely.
- `objective_rollup(rows)` is EVID-08's visible half: a per-mode `{attempts, correct, wrong, pending}` rollup, so a drill correct and an exam correct are counted in different buckets and never summed into one figure.
- `surfaces/evidence_cli.py`'s `cmd_evidence` gains `--prefix`, `--subject`, `--mode`, `--session`, `--since` and `--rebuild-index`; `--objective` is no longer required, but the command exits non-zero naming the accepted flags if none of `--objective`/`--subject`/`--session` is given. Output gains `by_mode`, `index` (`"used"`/`"fallback"`) and `index_rebuilt`. `cmd_evidence` deliberately calls `ensure_index()` exactly zero times itself — `objective_history()` is the one call site — and infers the reported `index` status afterward via a read-only `evidence.index_stale()` check, so a future regression that skips `ensure_index()` inside `objective_history()` stays visible instead of being masked by a redundant refresh sitting beside it.
- `surfaces/cli.py`'s `evidence` subparser carries the six new flags; `schemas/report.schema.json`'s `objective_history` variant documents `by_mode`/`index`/`index_rebuilt` as optional additive properties.
- `tests/evidence_roundtrip.py` gained `test_objective_query()` (a synthetic, id-assigned bank spanning two subjects — `emt:airway.opa`, `emt:airwaymanagement`, `csci1100:loops.while` — driven through four sessions; exact match, `--prefix` adjacency, `--subject`-alone, the empty-objective rule, and hand-built same-`ts` log ordering both before and after `--rebuild-index`) and `test_index_is_disposable()` (D-08's central claim, plus a genuine regression discriminator: a response event appended directly to the log must be reflected on the very next query, and the fallback warning must never print in the happy path — both of which are what actually catch a skipped `ensure_index()` call, since `objective_history()`'s own inner exception handler would otherwise quietly self-heal via the fallback path and mask a naive "does it still return correct data" check). `test_mode_recorded()` was extended with the `by_mode` assertion and a `flatten()`-based recursive gamification-key check.

## Task Commits

Each task was committed atomically:

1. **Task 1: Build the disposable sqlite3 projection with a staleness rule that survives truncation** - `1ec0918` (feat)
2. **Task 2: Serve the cross-subject objective query from the index, with per-mode rollup** - `f8b8266` (feat)
3. **Task 3: Prove the index is disposable and the query is stable** - `30ca87f` (test)

_Note: no TDD red/green/refactor split was called for; all three tasks are `type="auto"`._

## Files Created/Modified

- `evidence.py` - `INDEX_VERSION`, `rebuild_index()`, `index_stale()`, `ensure_index()`, `_index_connect()`/`_create_index_schema()`/`_insert_response_row()`/`_mark_index_retracted()`/`_set_index_meta()`/`_index_tail_update()` (private helpers); `index_for_log()`, `event_matches()`, `objective_rollup()`; `objective_history()` rewritten to the indexed/fallback pair, signature extended with `prefix`/`subject`/`mode`/`session_id`/`since`
- `surfaces/evidence_cli.py` - `cmd_evidence()` rewritten: six new flags read, `by_mode`/`index`/`index_rebuilt` output keys, single `ensure_index()` call site preserved by design
- `surfaces/cli.py` - `evidence` subparser: `--prefix`, `--subject`, `--mode`, `--session`, `--since`, `--rebuild-index`; `--objective` default `""` instead of `required=True`
- `itembank.py` - `INDEX_VERSION`, `ensure_index`, `event_matches`, `index_for_log`, `index_stale`, `objective_rollup`, `rebuild_index` added to the `from evidence import (...)` block and `__all__`
- `schemas/report.schema.json` - `objective_history` variant's `properties` gains `by_mode`, `index` (enum `used`/`fallback`), `index_rebuilt`, each documented as optional/additive
- `tests/evidence_roundtrip.py` - `test_objective_query()`, `test_index_is_disposable()`, `flatten()` helper, `parse_json_tail()` helper, `SYNTH_BANK_TEXT` fixture, extended `test_mode_recorded()`

## Decisions Made

See `key-decisions` in frontmatter above — five decisions: keeping `objective_history()`'s return shape a bare list (forcing `cmd_evidence` to infer index status via a read-only check rather than a second `ensure_index()` call, which is itself what makes the Task 3 regression tests meaningful); the `index_stale()` try/except fix found while confirming that design choice; `index_rebuilt` as an additive boolean rather than widening `index`'s own vocabulary; the JSON-only output decision (documented at length since it is the one place this plan's prose and its own testable artifact list disagree); and the schemas/report.schema.json update despite not being named in the plan's file lists.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `index_stale()` let an unopenable/corrupted index's exception escape instead of treating it as "stale, full rebuild"**
- **Found during:** Task 3, manually confirming (per the plan's own acceptance criteria) that `test_index_is_disposable` goes red when `objective_history()` skips its `ensure_index()` call
- **Issue:** The first-draft `index_stale()` wrapped the sqlite3 connect-and-read-meta step in `try/finally` (for connection cleanup) but not `try/except`. The function's own docstring already documented "an index that cannot even be opened" as a full-rebuild trigger (`return True, 0`), but the code did not implement that for the connect/query step itself — only for the missing-file and version-mismatch cases. A directory or corrupted file at the index path would raise `sqlite3.OperationalError`/`DatabaseError` straight out of `index_stale()`, uncaught, rather than being handled as staleness.
- **Fix:** Wrapped the connect-and-read-meta step in `try/except Exception: return True, 0`, matching the docstring's own stated contract.
- **Files modified:** `evidence.py`
- **Verification:** `test_index_is_disposable`'s corrupted-index and unwritable-directory scenarios both pass (rebuild or fallback, same rows, exit 0); the CLI's own `try/except` around the post-query `index_stale()` call in `cmd_evidence` is now genuinely a defensive backstop rather than the only thing standing between this bug and a crash.
- **Committed in:** `f8b8266` (Task 2 commit — found while doing Task 3's manual confirmation work, but the bug was in Task 2's code, so the fix landed in Task 2's commit rather than being re-opened)

**2. [Rule 1 - Bug, discovered via the plan's own acceptance-criteria process] `cmd_evidence`'s original design called `ensure_index()` twice per query**
- **Found during:** Task 3, the first attempt at manually confirming `test_index_is_disposable` goes red when `objective_history()` skips `ensure_index()`
- **Issue:** The first-draft `cmd_evidence` called `evidence.ensure_index(log, index)` itself (to learn `"used"`/`"fallback"` for the output) and then called `objective_history()`, which calls `ensure_index()` again internally. This is not incorrect (both calls agree), but it meant `cmd_evidence`'s own call silently refreshed the index every time, so a regression that broke `objective_history()`'s internal call was invisible to any test driving the query through the CLI — the outer call papered over it.
- **Fix:** Removed `cmd_evidence`'s direct `ensure_index()` call. `objective_history()` is now the one call site; `cmd_evidence` infers `"used"`/`"fallback"` after the query via a read-only `evidence.index_stale()` check instead.
- **Files modified:** `surfaces/evidence_cli.py`
- **Verification:** With this fix in place, temporarily replacing `objective_history()`'s `ensure_index()` call with a hardcoded `"used"` makes `test_index_is_disposable` fail immediately (`"a query never built the disposable index at all"`); reverting restores green. Confirmed and reverted; not committed as a mutation.
- **Committed in:** `f8b8266` (Task 2 commit)

---

**Total deviations:** 2 auto-fixed bugs, both found during the plan's own mandated Task 3 acceptance-criteria confirmation step ("confirm by making that change temporarily, observing red... and restoring") rather than during ordinary test runs — the process the plan specifies for validating a negative test surfaced two real correctness gaps a purely positive test suite would not have caught.
**Impact on plan:** Both fixes are structural correctness/observability improvements with no scope creep — no new capability was added beyond what Task 1/Task 2's own text specified (a full-rebuild trigger on an unopenable index; a single, honest `ensure_index()` call site).

## Issues Encountered

- **`tests/durability_roundtrip.py`'s kill-probe is intermittently flaky under subprocess load** (pre-existing, out of scope per the standing phase note carried in every prior plan's summary in this phase). Failed 2 of 6 runs during this plan's work with a bare `FileNotFoundError` on the probe's own temp file — unrelated to any file this plan touches (`evidence.py`'s only shared surface with the durability probe, `locked()`/`append_line`, was not modified by this plan). Retried and passed; not chased further.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase success criterion 4 is met: one query (`itembank evidence`) answers the objective question across every session and every subject, reading from `_evidence/evidence.jsonl` alone, with the sqlite3 index provably a disposable cache in front of it.
- `evidence.py`'s new surface (`INDEX_VERSION`, `rebuild_index`, `index_stale`, `ensure_index`, `index_for_log`, `event_matches`, `objective_rollup`) is exported from `itembank.py` and ready for any later plan (Phase 7 selection, Phase 10 trends) that needs the same indexed cross-subject read path rather than reimplementing a scan.
- The EVID-08 "unclassified edge" flagged in this plan's own frontmatter (mode vocabulary recorded as a free string, not validated against an enum in `evidence.py`) remains carried forward as documented — `schemas/session.schema.json` still enumerates the five current modes, so a future mode is an additive schema change, not a silent one.
- The dual JSON/human-readable output form described in the plan's action text but not implemented (see Decisions Made) is a documented, deliberate scope decision, not a gap — no artifact in the plan's own "Created by this plan" list or acceptance criteria requires it, and implementing it would have broken five existing tests' `json.loads(out)` contract from plans 01-02/01-07.
- No blockers identified for `01-09` onward. The one open item remains the pre-existing `durability_roundtrip.py` kill-probe timing sensitivity, unaffected by this plan's changes.

---
*Phase: 01-evidence-spine-protocol-foundation*
*Completed: 2026-08-06*

## Self-Check: PASSED

- FOUND: evidence.py
- FOUND: itembank.py
- FOUND: schemas/report.schema.json
- FOUND: surfaces/cli.py
- FOUND: surfaces/evidence_cli.py
- FOUND: tests/evidence_roundtrip.py
- FOUND: 1ec0918 (Task 1 commit)
- FOUND: f8b8266 (Task 2 commit)
- FOUND: 30ca87f (Task 3 commit)
