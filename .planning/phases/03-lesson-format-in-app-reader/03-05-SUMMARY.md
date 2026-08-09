---
phase: 03-lesson-format-in-app-reader
plan: 05
subsystem: ui
tags: [lesson, cli, markdown, argparse, python-stdlib]

# Dependency graph
requires:
  - phase: 03-04
    provides: "render_markdown block/inline scope and lesson_page's accepted-but-ignored ref parameter"
  - phase: 03-01
    provides: "lesson_page/cmd_lesson CLI twin and model.lesson_slug"
provides:
  - "--ref filtering on `itembank lesson`: one section plus its backlinks, resolved through model.lesson_slug"
  - "the locked hard stop for an explicitly requested heading that does not exist"
  - "cmd_lesson's observable contract: default output path, count semantics, exactly one status line"
  - "correct per-heading backlink placement in the rendered lesson document"
affects: [03-06, Phase 4 surface reconciliation, Phase 9 loop]

# Actuals (#2632) -- pairs with the plan's estimate (36000 raw tokens).
actuals:
  tokens: 5283
  tasks: 2
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "one slugifier: model.lesson_slug() reconciles the CLI's --ref text, the item tag and the HTML anchor"
    - "the render function signals a --ref miss by returning None; cmd_lesson owns the sys.exit hard stop"
    - "the success line reports sections actually rendered (1 under --ref, 0 for empty/degraded, heading count otherwise)"

key-files:
  created: []
  modified:
    - surfaces/lesson.py
    - surfaces/cli.py
    - tests/lesson_roundtrip.py

key-decisions:
  - "D-11 executed: --ref filters output to one heading plus its backlinks because the CLI has no anchor to jump to"
  - "lesson_page returns None on a --ref miss so the route, CLI and tests share one render without inheriting an exit path"
  - "resolved the deferred 03-04 backlink-placement quirk: each heading's section is rendered from its own text/body with its backlinks directly beneath -- the association --ref filtering required"

patterns-established:
  - "one slugifier: --ref text, item tag and HTML anchor all resolve through model.lesson_slug, never raw comparison"
  - "one degraded-state policy: no-lesson and unreadable-source banks write their page and exit 0 on both surfaces; the only hard stop is an explicitly requested missing heading"
  - "the count reports what was written, so a caller can act on it"

requirements-completed: [LESSON-06]

# Coverage metadata (#1602)
coverage:
  - id: D1
    description: "--ref selects one section and its backlinks through model.lesson_slug, or hard-stops with the locked message"
    requirement: LESSON-06
    verification:
      - kind: unit
        ref: "tests/lesson_roundtrip.py#test_lesson_ref_filters_one_section"
        status: pass
      - kind: unit
        ref: "tests/lesson_roundtrip.py#test_lesson_ref_slug_variants_resolve"
        status: pass
      - kind: integration
        ref: "tests/lesson_roundtrip.py#test_lesson_ref_cli_match_exits_zero_count_one"
        status: pass
      - kind: integration
        ref: "tests/lesson_roundtrip.py#test_lesson_ref_cli_miss_hard_stops"
        status: pass
    human_judgment: false
  - id: D2
    description: "cmd_lesson's observable contract -- default output path beside the bank, count semantics, exactly one locked status line, empty/degraded banks write and exit 0, CLI file byte-identical to the route's render"
    requirement: LESSON-06
    verification:
      - kind: integration
        ref: "tests/lesson_roundtrip.py#test_lesson_cli_default_output_path"
        status: pass
      - kind: integration
        ref: "tests/lesson_roundtrip.py#test_lesson_cli_exactly_one_status_line"
        status: pass
      - kind: integration
        ref: "tests/lesson_roundtrip.py#test_lesson_cli_no_lesson_bank_writes_empty_and_exits_zero"
        status: pass
      - kind: integration
        ref: "tests/lesson_roundtrip.py#test_lesson_cli_file_byte_identical_to_render"
        status: pass
    human_judgment: false
  - id: D3
    description: "the daemon route selects no section -- the browser's selection mechanism stays the fragment, never a query parameter"
    requirement: LESSON-06
    verification:
      - kind: integration
        ref: "tests/lesson_roundtrip.py#test_lesson_route_selects_no_section"
        status: pass
    human_judgment: false
  - id: D4
    description: "`itembank lesson` prints no progress line while rendering a very large [LESSON-SRC:] file, so a slow render must not read as a hang"
    requirement: LESSON-06
    verification: []
    human_judgment: true
    rationale: "Whether silence reads as a hang is a human judgment, not a timing threshold -- carried as a UAT backstop in 03-VALIDATION.md per the plan's own statement."

# Metrics
duration: 8min
completed: 2026-08-08
status: complete
---

# Phase 3 Plan 5: CLI Twin Completeness Summary

**`itembank lesson --ref` filters to one section through the one slugifier (or hard-stops), and the CLI's output contract — default path, honest section count, one status line — is locked by tests**

## Performance

- **Duration:** 8 min
- **Started:** 2026-08-09T01:45:40Z
- **Completed:** 2026-08-09T01:54:25Z
- **Tasks:** 2
- **Files modified:** 3 code/test files (+ 1 planning log note)

## Accomplishments
- `itembank lesson <bank> --ref "<heading>"` renders exactly that heading's section and its backlinks, resolved through `model.lesson_slug()` — the same value the item tag and the HTML anchor use — so a caller can type the heading with different casing, spacing or punctuation and still reach it.
- A `--ref` naming no heading (including a bank with no lesson section at all) hard-stops with the locked message `no lesson heading matching '<text>' in <bank>`; the render function itself signals the miss by returning None and carries no exit path, so the route, CLI and tests share one render.
- The CLI's observable contract is now fixed: no `--out` writes beside the bank with a lesson-suffixed name (the `cmd_study` rule), the success line reports sections actually rendered (1 under `--ref`, 0 for empty/degraded, heading count otherwise), exactly one status line is printed with no progress output, and the written file is byte-identical to what the daemon route serves.
- Fixed the deferred backlink-placement quirk: each heading's section is now rendered from its own text and body with its backlinks directly beneath, so the filtered page is the full page narrowed rather than a second layout, and the full page matches the Copywriting Contract's per-heading shape.

## Task Commits

Each task was committed atomically:

1. **Task 1: `--ref` selects one section, through the one slugifier, or stops**
   - `7c80026` (test) — failing `--ref` filter, slug-variant and hard-stop tests
   - `9cd71d1` (feat) — `--ref` section selection through `model.lesson_slug`
2. **Task 2: The CLI's observable contract — counts, default output path, and what never stops**
   - `8c049da` (feat) — output contract locked: counts, default path, one status line

## Files Created/Modified
- `surfaces/lesson.py` — `lesson_page(..., ref=...)` filters by slug (None on miss); `cmd_lesson` hard-stops, derives the default output path like `cmd_study`, and reports the rendered section count; per-heading section/backlink assembly
- `surfaces/cli.py` — `--ref` flag on the `lesson` subparser
- `tests/lesson_roundtrip.py` — 18 new tests covering filter, slug variants, hard stop, route-no-ref, exit-free render, default path, count semantics, one status line, degraded/empty exits, byte identity, and `--help`
- `.planning/phases/03-lesson-format-in-app-reader/deferred-items.md` — resolution note for the 03-04 backlink-placement discovery

## Decisions Made
- `lesson_page` returns None on a `--ref` miss and `cmd_lesson` owns the `sys.exit` hard stop, keeping the render function usable by the route, the CLI and tests without any of them inheriting an exit path.
- The `--ref` matching rule is `model.lesson_slug()` equality — never raw string comparison — so the CLI agrees with the item tag and the HTML anchor structurally, not by coincidence.
- The deferred backlink-placement quirk had to be fixed as part of this task: correct `--ref` filtering requires each heading's section and its own backlinks to be one unit, which the old `</section>`-re-split assembly could not produce.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Fixed the deferred backlink-placement quirk in `lesson_page` assembly**
- **Found during:** Task 1 (`--ref` section selection)
- **Issue:** The pre-existing (03-01) assembly re-split `render_markdown`'s output on `</section>` and attached each heading's backlinks to the next chunk, nesting section B inside section A and leaving both backlink lists after the last heading's prose. The plan requires the filtered page to contain exactly the matched heading's section and its own backlinks, which this split made structurally impossible — the discovery was already logged as a deferred item at commit `71522c1`.
- **Fix:** Rendered each heading's section from its own text and body (`render_markdown("### <text>\n\n<body>")`) and appended that heading's backlinks directly beneath it; a `--ref` scope then drops the other sections while keeping the shared chrome. The full page now matches the Copywriting Contract's per-heading shape.
- **Files modified:** `surfaces/lesson.py`, `tests/lesson_roundtrip.py`
- **Verification:** full suite green; `test_lesson_ref_filters_one_section` and the backlink-order assertion lock the placement
- **Committed in:** `9cd71d1`

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** The fix was required for the plan's core behavior (correct `--ref` output) and also resolved a logged deferred defect. No scope creep.

## Issues Encountered
None beyond the deferred quirk documented above, which was resolved as part of Task 1.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Ready for 03-06 (`spec` documents the grammar, plus the phase gate): the reader's per-heading render and the CLI contract are now stable, so the spec text can describe observable behavior the phase gate can check.
- The 03-04 deferred backlink-placement item is closed; `deferred-items.md` carries the resolution note.

## Self-Check: PASSED

- SUMMARY and all key files exist on disk.
- All three task commits verified in `git log`: `7c80026` (test), `9cd71d1` (feat), `8c049da` (feat).
