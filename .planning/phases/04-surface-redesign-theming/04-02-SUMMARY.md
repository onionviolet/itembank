---
phase: 04-surface-redesign-theming
plan: 02
subsystem: ui
tags: [day-plan, markdown-editing, atomic-write, sha256, optimistic-concurrency, stdlib, tdd]

# Dependency graph
requires:
  - phase: 04-01
    provides: tests/day_edit_roundtrip.py Wave 0 harness plus the supported/refused table-grammar corpus
provides:
  - surfaces/day_document.py exact-span snapshot/save adapter with SHA-256 revisions
  - itembank day --edit/--set/--revision/--force/--confirm-force structured CLI twin
  - no-write conflict and confirmed-force contract the 04-06 browser editor will reuse
affects: [04-06 browser day editor, daemon /day/<stem> routes, SURF-09 UAT]

actuals:
  tokens: 13487
  tasks: 2
  commits: 4

tech-stack:
  added: []
  patterns:
    - "Exact UTF-8 span tracking with an escape/code-span-aware cell scanner: \\| and pipes inside closed inline code are cell data, never separators"
    - "SHA-256 revision gate re-checked immediately before os.replace (D-09 tight window)"
    - "Same-directory temporary file + flush/fsync + os.replace atomic write (D-11)"
    - "Escaped-pipe display round-trip: \\| unescapes to | for the learner; submitted | is re-encoded as \\| with backslashes escaped first"

key-files:
  created:
    - surfaces/day_document.py
  modified:
    - surfaces/day.py
    - surfaces/cli.py
    - tests/day_edit_roundtrip.py

key-decisions:
  - "Task 1 was implemented as one coherent adapter carrying the full D-08..D-11 action contract, so Task 2's assertions passed on first run (no RED observed) -- documented under TDD Gate Compliance; Task 2's feat commit added the genuinely missing tight-window recheck."
  - "Force saves do not bypass the byte gate: save(force=True) behaves like a normal save at the SHA-256 level; --force + --confirm-force OVERWRITE + the conflict's current revision are the CLI's explicit second confirmation (D-10, T-04-08)."
  - "Tests prove exact-byte preservation with a common-prefix/suffix single-replacement helper rather than difflib opcodes, whose alignment is not minimal."
  - "Control-character (NUL) refusal is asserted at the adapter API level because Windows CreateProcess rejects embedded NUL in argv; the adapter is the exact path the CLI wraps."

requirements-completed: [SURF-09]

coverage:
  - id: D1
    description: "Structured dated-row snapshot (columns/cells/document/revision) for one unambiguous pipe table"
    requirement: SURF-09
    verification:
      - kind: integration
        ref: "tests/day_edit_roundtrip.py#check_task1_snapshot_via_cli"
        status: pass
    human_judgment: false
  - id: D2
    description: "Exact-byte single-cell saves preserving LF/CRLF, padding, unknown columns, prose, unrelated tables, escaped and inline-code pipes"
    requirement: SURF-09
    verification:
      - kind: integration
        ref: "tests/day_edit_roundtrip.py#check_task1_single_cell_edit"
        status: pass
    human_judgment: false
  - id: D3
    description: "Refused grammar and invalid values return invalid/unsupported with draft preserved, unchanged file hash, no temporary file"
    requirement: SURF-09
    verification:
      - kind: integration
        ref: "tests/day_edit_roundtrip.py#check_task1_refusals"
        status: pass
    human_judgment: false
  - id: D4
    description: "Atomic replace via same-directory temp file, flush/fsync and os.replace, returning the SHA-256 of bytes now on disk"
    requirement: SURF-09
    verification:
      - kind: integration
        ref: "tests/day_edit_roundtrip.py#check_task1_atomic_write"
        status: pass
    human_judgment: false
  - id: D5
    description: "No-write conflict carrying draft, fresh current snapshot and both revisions on any byte change; metadata-only changes never conflict"
    requirement: SURF-09
    verification:
      - kind: integration
        ref: "tests/day_edit_roundtrip.py#check_task2_conflict_no_write"
        status: pass
    human_judgment: false
  - id: D6
    description: "Force overwrite requires --force plus --confirm-force OVERWRITE plus the conflict's current revision and preserves unrelated concurrent edits"
    requirement: SURF-09
    verification:
      - kind: integration
        ref: "tests/day_edit_roundtrip.py#check_task2_confirmed_force"
        status: pass
    human_judgment: false

duration: 21min
completed: 2026-08-09
status: complete
---

# Phase 4 Plan 2: Lossless Day-Plan Editing Adapter Summary

**Exact-byte structured day-plan editing with SHA-256 optimistic concurrency and a confirmed-force path -- `surfaces/day_document.py` snapshot/save adapter plus an `itembank day --edit/--set/--revision` CLI twin, proving D-08 through D-11 before any browser wiring**

## Performance

- **Duration:** ~21 min
- **Started:** 2026-08-09T03:10:00Z
- **Completed:** 2026-08-09T03:30:39Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments

- `surfaces/day_document.py` reads one unambiguous pipe table as a structured dated-row projection (columns, display cells, full document text, 64-hex SHA-256 revision) and never serializes Markdown: saves are exact UTF-8 cell-span replacements applied in descending byte order.
- The escape/code-span-aware scanner keeps `\|` and pipes inside closed inline code as cell data, so those cells are edited as one unit while unknown columns, surrounding prose, unrelated tables, LF/CRLF, and padding stay byte-identical outside the edited cell.
- Every refused construct from 04-UI-SPEC -- duplicate dates, missing header/rule/dated row, multiline/ragged rows, HTML tables, unclosed code spans, unknown columns, date-column edits, newline/control characters -- returns `invalid`/`unsupported` with the submitted draft intact, an unchanged file hash, and no temporary artifact.
- Every save re-reads the full bytes and compares SHA-256 twice: once at entry (conflict carries draft, fresh current snapshot, and both revisions) and again immediately before `os.replace` inside the write path, so a write landing in the analysis window can never be overwritten (D-09/T-04-05).
- `itembank day --edit/--set/--revision/--force/--confirm-force OVERWRITE` is the structured CLI twin; force is an explicit two-input second confirmation that still patches only requested cells against fresh bytes and refuses a third-version replay.

## Task Commits

Each task was committed atomically:

1. **Task 1 RED: failing structured day-edit snapshot/save assertions** - `a108b5c` (test)
2. **Task 1 GREEN: lossless dated-row snapshot and exact-span save adapter** - `96c65f0` (feat)
3. **Task 2: stale-revision conflict and confirmed-force assertions** - `d095e1a` (test)
4. **Task 2 GREEN: re-read/re-check revision immediately before `os.replace`** - `7a31d6e` (feat)

**Plan metadata:** pending final docs commit.

## Files Created/Modified

- `surfaces/day_document.py` - exact-span snapshot/save adapter: byte scanner, table grammar, SHA-256 revisions, temp-file fsync + `os.replace`, draft-preserving conflict/invalid results.
- `surfaces/day.py` - `_day_edit` structured edit branch in `cmd_day` (tick/check/due/server paths untouched).
- `surfaces/cli.py` - `day` parser gains `--edit`, repeatable `--set`, `--revision`, `--force`, `--confirm-force`.
- `tests/day_edit_roundtrip.py` - Task 1/2 behavior assertions: snapshot contract, single-span byte proof, supported-grammar preservation corpus, refusals, atomic write, stale conflicts, force gates, tight-window race.

## Decisions Made

- Task 1's implementation was designed as one coherent adapter delivering the plan's full action contract, so Task 2's conflict/force assertions passed on first run; the Task 2 feat commit supplied the one genuinely missing piece (the immediately-before-replace re-check). See TDD Gate Compliance below.
- Force is a CLI-level second confirmation, never a byte-gate bypass: `save(force=True)` still requires the conflict's current revision and still fails on a third version.
- Escaped pipes display as literal `|` to the learner; submitted values are stored with backslashes escaped first and pipes as `\|`, so `_display(_encode(value)) == value` always holds.
- Test byte preservation with a common-prefix/suffix `single_replacement` helper because difflib opcodes are alignment-dependent and can report several spans for one true replacement.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Tight-window revision re-check before `os.replace`**
- **Found during:** Task 2 (stale-save rejection)
- **Issue:** `save` compared the SHA-256 at entry, leaving a TOCTOU window between that comparison and `os.replace`; a concurrent write landing in the analysis window would have been silently overwritten, violating D-09's "immediately before replacement" and T-04-05's high-severity mitigation.
- **Fix:** `_atomic_replace(path, data, expected_rev)` re-reads the target and raises `StaleRevisionError` on mismatch; `save` converts it into the same no-write conflict carrying the newest bytes. A deterministic race-window test (spy rewrites the file between the first read and the replace) proves the gate.
- **Files modified:** surfaces/day_document.py, tests/day_edit_roundtrip.py
- **Verification:** `python tests/day_edit_roundtrip.py` green
- **Committed in:** `7a31d6e`

**2. [Rule 3 - Blocking] Windows CreateProcess rejects embedded NUL in argv**
- **Found during:** Task 1 (control-character refusal test)
- **Issue:** `subprocess.run` raised `ValueError: embedded null character` when the test passed `--set EMT=a\x00b` through the CLI.
- **Fix:** Control-character (newline and NUL) refusal is asserted through `day_document.save` directly -- the exact adapter path the CLI wraps -- rather than via a subprocess argv that Windows cannot carry.
- **Files modified:** tests/day_edit_roundtrip.py
- **Verification:** `python tests/day_edit_roundtrip.py` green
- **Committed in:** `d095e1a`

---

**Total deviations:** 2 auto-fixed (1 missing critical, 1 blocking)
**Impact on plan:** Both fixes were required for the plan's correctness contract (no overwrite ever, and platform-runnable tests). No scope creep.

## TDD Gate Compliance

- Task 1: `test(...)` commit `a108b5c` observed RED (module absent) -> `feat(...)` commit `96c65f0` observed GREEN. Gate sequence satisfied.
- Task 2: `test(...)` commit `d095e1a` was written first but **passed on first run** because Task 1's GREEN implementation already delivered the D-09/D-10 conflict and force contract (the adapter was built coherently to the plan's full action text). No RED was observable for Task 2's assertions without reverting already-correct Task 1 work. A `feat(...)` commit `7a31d6e` followed with the genuinely missing tight-window re-check. Gate sequence present in log order, but Task 2's RED observation is structurally preempted -- recorded here for the verifier rather than silently skipped.

## Issues Encountered

- difflib's `SequenceMatcher` opcodes are not minimal: a single cell replacement can surface as multiple overlapping spans (e.g. "ch 2 finish" -> "ch 3, start" reuses "ch "). Added `single_replacement` (common-prefix/suffix) as the authoritative byte-preservation proof; exact-equality assertions remain.
- Task 2's concurrency tests passed immediately (see TDD Gate Compliance); no implementation defect was found in the first-run Task 1 adapter.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The stable `day_document.snapshot(path, year, iso)` / `day_document.save(path, iso, edits, revision, force=False)` interface is ready for plan 04-06's browser editor: the daemon day route can call the adapter directly and hand the structured conflict (`draft` + `current` snapshot) to the side-by-side recovery UI.
- Full CI suite (all 20 `tests/*.py`) passes locally with the new CLI flags and adapter in place.
- SURF-09's data-loss boundary is proven at the CLI slice; the Obsidian two-editor scenario still needs the 04-06 daemon wiring and its end-of-phase UAT.

---
*Phase: 04-surface-redesign-theming*
*Completed: 2026-08-09*

## Self-Check: PASSED

- Created files verified on disk: `04-02-SUMMARY.md`, `surfaces/day_document.py`
- Commits verified in git log: `a108b5c` (test), `96c65f0` (feat), `d095e1a` (test), `7a31d6e` (feat)
