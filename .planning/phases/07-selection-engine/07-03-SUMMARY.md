---
phase: 07-selection-engine
plan: 03
subsystem: selection
tags: [evidence, sqlite, index, bank-scoping, cooldown]

# Dependency graph
requires:
  - phase: 01
    provides: the disposable sqlite3 index, objective_history/event_matches, live_events
provides:
  - bank column + idx_bank on the index; objective/bank on every objective_history row
  - bank= filter on event_matches/objective_history
  - itembank evidence --bank
affects: [07-05, 07-06]

actuals:
  tokens: 4800
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - every filter bound as a ? parameter; SELECT construction never %-formats a value
    - index is a cache: delete-and-requery and stale-version rebuild are asserted

key-files:
  created: []
  modified:
    - evidence.py
    - schemas/report.schema.json
    - surfaces/evidence_cli.py
    - surfaces/cli.py
    - tests/evidence_roundtrip.py

key-decisions:
  - "INDEX_VERSION 1 -> 2: the projection gained a bank column (D-13); the bump alone forces the one rebuild, and the index stays disposable."
  - "objective and bank ride on every objective_history row so a caller can group by objective without re-reading the log (D-13, remediation composition)."
  - "bank= is orthogonal to the subject/objective precedence rule; a bank-scoped query with no objective is the normal exposure case."

patterns-established:
  - "The CLI's --bank threads through objective_history AND the scoped retracted count through the same event_matches predicate, so the count next to the query is the count for that query (01-08's no-drift rule)."

requirements-completed: [SEL-03]

coverage:
  - id: D1
    description: bank-scoped exposure queries return only that bank's live responses, identically through the indexed and fallback paths
    requirement: SEL-03
    verification:
      - kind: unit
        ref: tests/evidence_roundtrip.py#test_bank_scoped_query
        status: pass
      - kind: unit
        ref: tests/evidence_roundtrip.py#test_index_bank_disposable_and_version
        status: pass
    human_judgment: false
  - id: D2
    description: every objective_history row names its own objective and bank, recorded not re-derived
    verification:
      - kind: unit
        ref: tests/evidence_roundtrip.py#test_history_row_width
        status: pass
    human_judgment: false
  - id: D3
    description: itembank evidence --bank is a working CLI surface whose document validates against report.schema.json
    verification:
      - kind: integration
        ref: schema_validate.py schemas/report.schema.json <evidence --bank document>
        status: pass
    human_judgment: false

# Metrics
duration: 30min
completed: 2026-08-10
status: complete
---

# Phase 7 Plan 3: Bank-Scoped Evidence Index Summary

**"The last N responses in this bank" is now cheaply answerable: the disposable sqlite3 index carries a `bank` column with its own index, every `objective_history()` row names its objective and bank, and `itembank evidence --bank` exposes the filter on the CLI.**

## Performance

- **Duration:** 30 min
- **Started:** 2026-08-10T20:01:00Z
- **Completed:** 2026-08-10T20:31:00Z
- **Tasks:** 3
- **Files modified:** 5

## Accomplishments

- `INDEX_VERSION = 2`, `bank TEXT` column, `idx_bank ON events(bank, ts)`,
  and `bank` projected by `_insert_response_row`.
- `objective` and `bank` on every `objective_history()` row (indexed and
  fallback), matching the recorded event values.
- `bank=` threaded through `event_matches()` (exact equality), both query
  halves (bound as `?`, never formatted), and `objective_history()`; the
  SELECT construction carries no `%`-formatting of a filter value.
- `itembank evidence --bank <bank>`: filters the query, scopes the retracted
  count through the same predicate, prints `bank` on the document, and
  composes with `--objective`/`--subject`.
- `schemas/report.schema.json`: `bank` on `objective_history`, and
  `objective`/`bank` on `objective_history_row` (additive, typed
  `["string","null"]`).
- Three new `evidence_roundtrip` checks: bank scoping (disjoint + exhaustive +
  every row banked), row width (recorded objective), and disposability +
  stale-version rebuild. Both mutations verified (removing `bank = ?` breaks
  scoping; reverting INDEX_VERSION breaks the stale-shape check).

## Task Commits

1. **Task 1: bank column + widened rows + filter** - absorbed into the
   concurrent session's `c08aa42` (see deviation); content verified in HEAD.
2. **Task 2: `itembank evidence --bank`** - `d8a21ce` (CLI flag; the
   `cmd_evidence` threading landed with `c08aa42`)
3. **Task 3: bank-scoping tests** - `b8fc6cc`

**Plan metadata:** pending (next commit)

## Files Created/Modified

- `evidence.py` - index v2, bank column/index, widened rows, bank= filter
- `schemas/report.schema.json` - documented bank/objective fields
- `surfaces/evidence_cli.py` - --bank threading + scoped retracted count
- `surfaces/cli.py` - --bank flag on the evidence subparser
- `tests/evidence_roundtrip.py` - three new checks

## Decisions Made

- The version bump alone forces the rebuild; the index stays disposable
  (deleting it and re-querying returns identical rows).
- Bank-scoping is orthogonal to subject/objective precedence; no objective is
  required for a bank-scoped exposure query.

## Deviations from Plan

### Coordination

**1. Concurrent commit absorbed the Task-1/part-of-Task-2 files**
- **Found during:** commit
- **Issue:** The concurrent 06-01 session's `c08aa42` swept up staged
  `evidence.py`, `schemas/report.schema.json` and `surfaces/evidence_cli.py`
  changes (mixed labels, content preserved in HEAD).
- **Fix:** Verified every phase-7 symbol is present in HEAD; committed the
  remaining pieces (`d8a21ce`, `b8fc6cc`). Logged in `deferred-items.md`.

---

**Total deviations:** 1 documented (coordination; no code regression)
**Impact on plan:** None; all acceptance criteria verified.

## Issues Encountered

- `git apply` temp artifacts briefly tripped `test_one_writer`'s repo-wide
  scan; removed before commit.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Ready for 07-04 (selection_mode/selection_spec recording) and 07-05
  (cooldown via `objective_history(bank=...)`): the bank-scoped exposure seam
  D-13 promised is now real and CLI-provable.

---
*Phase: 07-selection-engine*
*Completed: 2026-08-10*
