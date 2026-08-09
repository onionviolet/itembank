---
phase: 03-lesson-format-in-app-reader
plan: 03-02
subsystem: lesson-reader
tags: [lesson, LESSON-SRC, shared-source, path-containment, degraded-state, reader]

# Dependency graph
requires:
  - phase: 03-lesson-format-in-app-reader
    provides: "parse_lesson()'s declared six-key shape (source/body/intro/headings/error/detail), the LESSON/LESSON-REF grammar, the /lesson route and CLI twin from plan 03-01"
provides:
  - "[LESSON-SRC:] preamble directive: one bank sources its lesson from an external markdown file another bank can share"
  - "Path-containment refusal for [LESSON-SRC:] decided from the resolved path before any open (T-3-02)"
  - "Degraded reader state for unreadable sources on the daemon route and the CLI twin, in the var(--warn) tone (T-3-04)"
affects: [03-03 lint lesson.* codes, 03-05 CLI --ref, 03-06 spec text, Phase 9 shared subject lessons]

# Actuals (#2632) - pairs with the plan's estimate (chars/4 over the realized diff)
actuals:
  tokens: 6636
  tasks: 2
  commits: 3

tech-stack:
  added: []
  patterns:
    - "One branch in the loader: [LESSON-SRC:] substitutes the external file's text for the preamble before the section match, so parser and reader stay origin-agnostic (D-02)"
    - "Separator-suffixed path containment (absolute path plus os.sep prefix), reusing surfaces/migrate.py:scan_legacy()'s proven shape"
    - "Conditional template substitution (__WARN_CSS__): the degraded state's styling ships only on the page that renders it"

key-files:
  created:
    - fixtures/lesson_shared.md
    - fixtures/lesson_src_bank.md
  modified:
    - model.py
    - surfaces/lesson.py
    - tests/lesson_roundtrip.py

key-decisions:
  - "An external source wins over an inline ## LESSON section when a bank carries both; the precedence is documented in parse_lesson()'s docstring"
  - "The degraded page echoes the bank-author-written directive path, grabbed from the bank text, never the resolved absolute path or the raw OS error text (T-3-07); the reason stays with itembank lint"
  - "The warn CSS is substituted in only for the degraded branch, so a bank with no lesson stays visually distinct from a bank whose lesson source broke"

requirements-completed: [LESSON-01, LESSON-06]

coverage:
  - id: D1
    description: "[LESSON-SRC:] external-source loader branch - one branch in the loader, identical six-key shape for inline and external lessons, external wins over inline"
    requirement: LESSON-01
    verification:
      - kind: unit
        ref: "tests/lesson_roundtrip.py#test_lesson_src_shared_parse"
        status: pass
      - kind: unit
        ref: "tests/lesson_roundtrip.py#test_lesson_src_two_banks_share"
        status: pass
      - kind: unit
        ref: "tests/lesson_roundtrip.py#test_lesson_src_wins_over_inline"
        status: pass
    human_judgment: false
  - id: D2
    description: "Path containment refusal - relative climbs, absolute outside paths and prefix-sibling directories refused before any open, subdirectory paths accepted (T-3-02)"
    requirement: LESSON-01
    verification:
      - kind: unit
        ref: "tests/lesson_roundtrip.py#test_lesson_src_traversal_refused"
        status: pass
      - kind: unit
        ref: "tests/lesson_roundtrip.py#test_lesson_src_absolute_refused"
        status: pass
      - kind: unit
        ref: "tests/lesson_roundtrip.py#test_lesson_src_prefix_sibling_refused"
        status: pass
      - kind: unit
        ref: "tests/lesson_roundtrip.py#test_lesson_src_subdirectory_accepted"
        status: pass
      - kind: unit
        ref: "tests/lesson_roundtrip.py#test_lesson_src_missing_file"
        status: pass
    human_judgment: false
  - id: D3
    description: "Degraded reader state - unreadable source renders a 200 var(--warn) page on the daemon route and the byte-identical CLI page, raising on neither; plain empty state stays warn-free (T-3-04)"
    requirement: LESSON-06
    verification:
      - kind: integration
        ref: "tests/lesson_roundtrip.py#test_lesson_src_degraded_daemon_and_cli"
        status: pass
      - kind: integration
        ref: "tests/lesson_roundtrip.py#test_lesson_plain_empty_state_has_no_warning"
        status: pass
    human_judgment: false

# Metrics
duration: 313min
completed: 2026-08-09
status: complete
---

# Phase 3 Plan 02: Lesson Shared-Source & Degraded Reader Summary

**[LESSON-SRC:] shares one lesson file across banks behind a pre-open path-containment refusal, and an unreadable source degrades to a warn-toned reader page on both the daemon route and the CLI twin**

## Performance

- **Duration:** 313 min (5h 13m)
- **Started:** 2026-08-08T19:48:53Z
- **Completed:** 2026-08-09T01:01:24Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments

- `parse_lesson()` gained the one `[LESSON-SRC:]` branch D-02 allows: the directive's path resolves against the bank's own directory, and a relative climb, an absolute path, or a prefix-sibling directory is refused **before any open** on the same absolute-path-plus-separator-suffix containment shape `surfaces/migrate.py` already proves. On acceptance the external file's text replaces the preamble, so the section match, heading walk, and returned key set run over one string -- an externally sourced lesson returns byte-for-byte the same six-key shape as an inline one.
- Missing or otherwise unreadable sources return a structured dict (`error: lesson.src_unreadable` with a detail reason) instead of raising; the `lesson.*` lint namespace stays unpublished, locked by a test, for plan 03-03's one-commit coupling.
- The reader degrades rather than breaks: `lesson_page()` renders the existing empty-state layout plus the locked `var(--warn)` sentence and the bank-author-written directive path in a wrapping, HTML-escaped `<code>` element -- no answer key, no rationale, no raw OS error, no resolved absolute path (T-3-07). The daemon route serves it at 200 and `itembank lesson` writes the byte-identical page and prints `0 lesson section(s)`; the plain empty state carries no warn styling, so "no lesson here" and "the lesson could not be read" stay distinguishable.
- Two fixtures prove the shared case: `fixtures/lesson_shared.md` (lesson-only reading material, ignored by `scan_dir`) and `fixtures/lesson_src_bank.md` (a bank sourcing it, with two `[LESSON-REF:]` items so the cross-bank backlink case is real).

## Task Commits

Each task was committed atomically (Task 1 followed the TDD RED/GREEN cycle):

1. **Task 1 RED - shared-source and containment tests** - `5189c1b` (test)
2. **Task 1 GREEN - LESSON-SRC loader branch** - `f0dd64a` (feat)
3. **Task 2 - degraded reader state** - `e1e6037` (feat)

**Plan metadata:** `25de3b1` (docs: complete plan)

## Files Created/Modified

- `model.py` - `parse_lesson()`: the `[LESSON-SRC:]` capture, containment refusal before any open, structured `lesson.src_unreadable` errors, external-over-inline precedence in the docstring
- `surfaces/lesson.py` - `WARN_SENTENCE`/`WARN_CSS` and the degraded branch of `lesson_page()`: empty-state layout plus the warn note, wrapping code element, `__WARN_CSS__` substitution
- `fixtures/lesson_shared.md` - lesson-only markdown two banks can share (2 headings, no items)
- `fixtures/lesson_src_bank.md` - bank sourcing its lesson externally with two LESSON-REF items
- `tests/lesson_roundtrip.py` - shared-parse, two-bank, missing-file, traversal/absolute/prefix-sibling refusal, subdirectory acceptance, external-over-inline, degraded daemon+CLI, plain-empty-state tests

## Decisions Made

- **External wins over inline:** a bank carrying both an inline `## LESSON` and a `[LESSON-SRC:]` directive resolves to the external file's headings; documented in the function docstring rather than left to discovery.
- **Page shows the author-written path:** the degraded note's `<code>` element carries the directive value grabbed from the bank text (the same read that supplies the title), never the resolved absolute path or the raw OS error text -- T-3-07's "echoes what the bank file already contains".
- **Warn styling is conditional:** `__WARN_CSS__` substitution keeps `var(--warn)` off the plain empty state, matching the acceptance criterion that the two states are visually distinguishable while `grep var(--warn)` still finds the style in the module.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- **Environmental test flake (out of scope):** one `daemon_roundtrip.py` run failed its hostile-`/api/start` directory-snapshot check because the agent harness itself created directories under `%TEMP%` (a `claude\...\scratchpad` tree and `.tmpi01XLt`) during the test window. The test snapshots the entire temp parent and flags any concurrent directory creation. It passes in isolation and on re-run; the plan's changes touch neither `handle_api_start` nor any directory-writing path. Not caused by this plan, not fixed.
- **POSIX path in acceptance criteria:** the plan's criteria use `/tmp/src.html`; on this Windows machine the CLI verification used `%TEMP%` paths with the identical exit-0 / `2 lesson section(s)` contract.

## Verification

- `python tests/lesson_roundtrip.py` -> `ok: lesson roundtrip (slug, parse, fingerprint, LESSON-SRC, degraded state, route, CLI twin, both link directions)`
- Full suite (`python tests/*.py`, 16 files) -> all pass
- All Task 1 and Task 2 acceptance criteria pass (key-set equality, `lesson_shared.md` source basename, MARKER_DO_NOT_LEAK never reaches the dict, `lesson.src_unreadable` absent from `LINT_CODES`, `os.sep` containment in source, degraded page `var(--warn)`/no `var(--bad)`, plain empty state warn-free, no nowrap/text-overflow)
- `python itembank.py lesson fixtures/lesson_src_bank.md --out <tmp>` -> exit 0, `2 lesson section(s)`, page carries both shared headings, both backlinks (`/quiz/lesson_src_bank#q1`, `#q2`) and the shared file's prose
- `python itembank.py daemon fixtures --no-open --port 0` -> `GET /lesson/lesson_src_bank` returns 200 with the shared headings, backlinks and shared prose
- `python itembank.py guard .` -> exit 0, 0 offending files

## Next Phase Readiness

- Ready for **03-03** (lint: `lesson.duplicate_heading`, `lesson.src_unreadable`, `lesson.orphan_heading`, `item.lesson_ref_unknown`, the two CI couplings, and the REQUIREMENTS.md reconciliation). The `lesson.*` namespace is deliberately unpublished here: `LINT_CODES` and `schemas/lint_error.schema.json` are untouched and locked by `test_lesson_src_stays_out_of_lint_namespace` and `tests/protocol_roundtrip.py`.
- The degraded page points readers at `itembank lint <bank>` for the reason detail, which 03-03's `lesson.src_unreadable` finding will surface.

## Self-Check: PASSED

All created files exist (`fixtures/lesson_shared.md`, `fixtures/lesson_src_bank.md`, `03-02-SUMMARY.md`); all three task commits exist in `git log` (`5189c1b`, `f0dd64a`, `e1e6037`).

---
*Phase: 03-lesson-format-in-app-reader*
*Completed: 2026-08-09*
