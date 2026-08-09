---
phase: 03-lesson-format-in-app-reader
plan: 03
subsystem: lint
tags: [lesson, LESSON-REF, lint, LINT_CODES, lint-error-schema, CI-couplings]

# Dependency graph
requires:
  - phase: 03-lesson-format-in-app-reader
    provides: "parse_lesson()'s declared six-key shape (source/body/intro/headings/error/detail), the LESSON/LESSON-REF grammar, and the reader/route/CLI twin from plans 03-01/03-02"
provides:
  - "Four published lesson lint codes: item.lesson_ref_unknown (error, by item number), lesson.duplicate_heading (error), lesson.orphan_heading (warning), lesson.src_unreadable (error) -- all members of LINT_CODES, the closed lint_error.schema.json code enum, and an accepted namespace"
  - "lint(questions, lesson=LESSON_UNCHECKED): an optional keyword parameter whose sentinel default leaves every pre-03-03 caller byte-identical, and whose lesson data turns the checks on -- lesson=None (no ## LESSON section) makes every LESSON-REF unknown, never a skip"
  - "cmd_lint and cmd_serve gate on the same lesson-supplied errors; serve refuses a dangling lesson reference unless --force"
  - "fixtures/broken_bank.md exercises the unknown-reference, duplicate-heading and orphan-heading codes through CI; fixtures/lesson_broken_src_bank.md exercises lesson.src_unreadable; CI schema-validates both fixtures' live --json output"
  - "REQUIREMENTS.md LESSON-04 restated at ROADMAP SC3's severity (fails, by item number) so the two governing documents no longer disagree (D-05)"
affects: [03-04 renderer scope, 03-05 CLI --ref, 03-06 spec grammar text, Phase 9 shared subject lessons]

# Actuals (#2632) - pairs with the plan's estimate (chars/4 over the realized diff)
actuals:
  tokens: 10005
  tasks: 3
  commits: 4

tech-stack:
  added: []
  patterns:
    - "Sentinel-default optional parameter (LESSON_UNCHECKED): 'caller did not supply lesson data' and 'caller supplied it and there is no lesson section' demand opposite behaviour, and parse_lesson()'s None result is data, not absence"
    - "Per-item lesson check inside lint()'s existing enumerate loop, so the finding is tagged by the item's own Qn number without re-deriving numbering"
    - "Bank-level lesson findings ordered in document order for the headings, byte-identical across runs"
    - "Coupling tests read the accepted namespace prefixes from the protocol test module (one shared definition) and compare LINT_CODES vs the schema enum in both directions"

key-files:
  created:
    - fixtures/lesson_broken_src_bank.md
  modified:
    - model.py
    - itembank.py
    - schemas/lint_error.schema.json
    - tests/lesson_roundtrip.py
    - tests/protocol_roundtrip.py
    - tests/evidence_roundtrip.py
    - surfaces/cli.py
    - surfaces/quiz.py
    - fixtures/broken_bank.md
    - .github/workflows/ci.yml
    - .planning/REQUIREMENTS.md

key-decisions:
  - "The locked lint messages from 03-UI-SPEC.md's Copywriting Contract are reproduced verbatim (unknown-reference, duplicate-heading, orphan-heading, src_unreadable), so CI substring greps and authoring agents read the same strings"
  - "lesson.src_unreadable echoes the bank-author-written basename, never the resolved absolute path, while the raw OS-error detail stays as the reason (T-3-09 intent; UI-SPEC permits raw OS error text as the reason)"
  - "Bank-level findings trail per-item findings, so the first BANK-tagged error (lesson.duplicate_heading) follows the established bank.answer_position_skew convention; tests/evidence_roundtrip.py's ordering assertion was extended to admit BANK errors last"
  - "fixtures/broken_bank.md carries three headings and one LESSON-REF to a missing heading, so all three headings are unreferenced and each produces the locked orphan warning -- the plan's 'one no item references' is satisfied by presence, and CI greps only assert the messages appear"

requirements-completed: [LESSON-04]

coverage:
  - id: D1
    description: "Four lesson lint codes published together in LINT_CODES, the closed lint_error.schema.json code enum, and an accepted namespace prefix (the two CI couplings landed in the same commit)"
    requirement: LESSON-04
    verification:
      - kind: unit
        ref: "tests/lesson_roundtrip.py#test_lesson_lint_codes_published"
        status: pass
      - kind: unit
        ref: "tests/protocol_roundtrip.py#test_lint_codes_declared"
        status: pass
      - kind: unit
        ref: "tests/lesson_roundtrip.py#test_lint_codes_schema_enum_contains_all_codes"
        status: pass
      - kind: unit
        ref: "tests/lesson_roundtrip.py#test_schema_enum_has_no_undeclared_codes"
        status: pass
      - kind: unit
        ref: "tests/lesson_roundtrip.py#test_lint_codes_namespace_prefixes_match_protocol"
        status: pass
    human_judgment: false
  - id: D2
    description: "lint(questions, lesson=LESSON_UNCHECKED) -- sentinel default keeps every pre-03-03 caller byte-identical; lesson=None makes every LESSON-REF unknown rather than skipped"
    requirement: LESSON-04
    verification:
      - kind: unit
        ref: "tests/lesson_roundtrip.py#test_lesson_lint_default_unchanged"
        status: pass
      - kind: unit
        ref: "tests/lesson_roundtrip.py#test_lesson_lint_sentinel_exported"
        status: pass
      - kind: unit
        ref: "tests/lesson_roundtrip.py#test_lesson_lint_no_section_means_every_ref_unknown"
        status: pass
    human_judgment: false
  - id: D3
    description: "item.lesson_ref_unknown is an error, by item number, with the locked actionable message -- never a warning and never a render-time crash (ROADMAP SC3)"
    requirement: LESSON-04
    verification:
      - kind: unit
        ref: "tests/lesson_roundtrip.py#test_lesson_lint_unknown_reference"
        status: pass
      - kind: unit
        ref: "tests/lesson_roundtrip.py#test_unknown_reference_is_error_not_warning"
        status: pass
    human_judgment: false
  - id: D4
    description: "lesson.duplicate_heading (error) and lesson.orphan_heading (warning) bank-level findings in deterministic document order, with the locked messages"
    requirement: LESSON-04
    verification:
      - kind: unit
        ref: "tests/lesson_roundtrip.py#test_lesson_lint_duplicate_heading"
        status: pass
      - kind: unit
        ref: "tests/lesson_roundtrip.py#test_lesson_lint_orphan_heading"
        status: pass
    human_judgment: false
  - id: D5
    description: "lesson.src_unreadable appends exactly one BANK error carrying the structured detail, echoing the authored basename rather than a resolved absolute path, with no heading-level findings"
    requirement: LESSON-04
    verification:
      - kind: unit
        ref: "tests/lesson_roundtrip.py#test_lesson_lint_src_unreadable"
        status: pass
    human_judgment: false
  - id: D6
    description: "cmd_lint and cmd_serve supply the lesson so a dangling LESSON-REF fails lint by item number and serve refuses the bank unless --force; build/study/export keep one-argument lint calls (no lesson link rendered, D-12)"
    requirement: LESSON-04
    verification:
      - kind: integration
        ref: "verified during execution: python itembank.py lint fixtures/broken_bank.md (non-zero, by item) and python itembank.py serve fixtures/broken_bank.md (refuses; --force starts)"
        status: pass
    human_judgment: false
  - id: D7
    description: "Fixtures and CI exercise all four codes against the published schema -- broken_bank message greps extended, src-broken fixture schema-validated, and a local test pushes both fixtures' live --json entries through schema_validate.validate"
    requirement: LESSON-04
    verification:
      - kind: unit
        ref: "tests/lesson_roundtrip.py#test_broken_lesson_fixtures_validate_against_schema"
        status: pass
      - kind: integration
        ref: ".github/workflows/ci.yml (Broken fixture is caught + Runtime output matches published schema steps)"
        status: pass
    human_judgment: false
  - id: D8
    description: "REQUIREMENTS.md LESSON-04 restated at ROADMAP SC3's severity (fails, by item number) so the two governing documents no longer disagree (D-05)"
    requirement: LESSON-04
    verification:
      - kind: other
        ref: "grep: LESSON-04 appears in the requirement line and its traceability row; 'warns when a LESSON-REF' no longer appears"
        status: pass
    human_judgment: false

# Metrics
duration: 17min
completed: 2026-08-08
status: complete
---

# Phase 3 Plan 03: Lesson Lint Codes & Couplings Summary

**A dangling LESSON-REF now fails `itembank lint` by item number with a locked, actionable message, the whole `lesson.*` code namespace ships in one commit through every file that must know it, and REQUIREMENTS.md stops contradicting the ROADMAP**

## Performance

- **Duration:** 17 min
- **Started:** 2026-08-08T20:08:37Z
- **Completed:** 2026-08-08T20:25:08Z
- **Tasks:** 3
- **Files modified:** 12 (1 created)

## Accomplishments

- `lint()` gained one optional keyword parameter, `lesson=LESSON_UNCHECKED`. The sentinel default means a caller that never heard of lessons gets byte-for-byte what it got before this phase; a caller that supplies lesson data passes whatever `parse_lesson()` returned -- a heading dict (checks run), None (every non-empty LESSON-REF is unknown, never a skipped check, D-05), or an unreadable-source error dict (`lesson.src_unreadable`, with no heading-level findings).
- Four codes are published in the one sorted-set `LINT_CODES`, the closed `schemas/lint_error.schema.json` code enum, and an accepted namespace prefix, all in one commit: `item.lesson_ref_unknown` (error, by the item's own Qn number), `lesson.duplicate_heading` (error, naming both headings and the shared slug), `lesson.orphan_heading` (warning, never an error), and `lesson.src_unreadable` (error, carrying the structured detail).
- `cmd_lint` loads the lesson beside the questions and passes it, so the CLI gate fails a dangling reference by item number; `cmd_serve` gates on the same errors, refusing the bank unless `--force`, while `build`/`study`/`export` keep one-argument calls because none of them renders a lesson link (D-12).
- `fixtures/broken_bank.md` now carries lesson material CI already lints and schema-validates: two slug-colliding headings, an orphan heading, and a LESSON-REF to a missing heading. A new `fixtures/lesson_broken_src_bank.md` exercises the unreadable-source code. CI's message greps and the schema step cover all four codes against live output.
- REQUIREMENTS.md LESSON-04 now states the ROADMAP SC3 severity -- fails, by item number -- so the two governing documents agree (D-05).
- Task 3 locked the couplings locally: LINT_CODES vs the schema enum are asserted equal in both directions (failures name the offending members), both broken fixtures' live `--json` output is pushed through `schema_validate.validate`, namespace prefixes are read from `protocol_roundtrip.LINT_PREFIXES` rather than restated, and the unknown-reference finding is asserted to live in errors, never warnings.

## Task Commits

Each task was committed atomically (Task 1 followed the TDD RED/GREEN cycle):

1. **Task 1 RED - lesson lint tests** - `c33a317` (test)
2. **Task 1 GREEN - codes and the lint(questions, lesson=...) gate** - `4654b84` (feat)
3. **Task 2 - gates, fixtures, CI, REQUIREMENTS reconciliation** - `b3dbce0` (feat)
4. **Task 3 - coupling guards** - `348d040` (test)

**Plan metadata:** (final docs commit, see git log)

## Files Created/Modified

- `model.py` - `LESSON_UNCHECKED` sentinel, four new `LINT_CODES` members, `lint(questions, lesson=...)` with the per-item and bank-level lesson checks, src-path basename echo (T-3-09)
- `itembank.py` - `LESSON_UNCHECKED` added to the explicit model import and `__all__`, alphabetically
- `schemas/lint_error.schema.json` - four new closed-enum members, list kept alphabetically, version stays 1 (additive)
- `tests/lesson_roundtrip.py` - lesson-lint behavior tests plus the Task 3 coupling guards (enum equality both directions, live-output schema validation, namespace-prefix sharing, error-not-warning severity lock)
- `tests/protocol_roundtrip.py` - `LINT_PREFIXES` lifted to module level; `test_lint_codes_declared` reads it
- `tests/evidence_roundtrip.py` - ordering assertion admits BANK-tagged errors last (Rule 3 accommodation)
- `surfaces/cli.py` - `cmd_lint` supplies `parse_lesson(a.bank)`
- `surfaces/quiz.py` - `cmd_serve` supplies the lesson; `cmd_build` stays one-argument
- `fixtures/broken_bank.md` - lesson section (two colliding headings + orphan) and a LESSON-REF to a missing heading
- `fixtures/lesson_broken_src_bank.md` - new fixture with an unreadable `[LESSON-SRC:]` and two clean items
- `.github/workflows/ci.yml` - three new message greps; src-broken fixture linted and schema-validated in the schema step
- `.planning/REQUIREMENTS.md` - LESSON-04 restated at ROADMAP severity

## Decisions Made

- **Sentinel default over None-as-default:** `lesson=LESSON_UNCHECKED` distinguishes "no lesson data supplied" from "lesson data supplied and there is no section", because `parse_lesson()` legitimately returns None for the second and the two demand opposite behaviour. The default keeps every pre-03-03 caller byte-identical.
- **Locked messages verbatim:** all four messages reproduce 03-UI-SPEC.md's Copywriting Contract strings, so CI substring greps and authoring agents read identical text.
- **Authored path, not resolved path:** the `src_unreadable` finding echoes the bank-author-written basename while the raw OS-error detail stays as the reason -- the reader page already deferred the reason detail to lint (03-02), and lint is the diagnostic surface.
- **First BANK error admitted:** `lesson.duplicate_heading` is the first error tagged `BANK`; like `bank.answer_position_skew` it trails every per-item finding, and the pre-existing ordering test was extended to enforce that convention rather than banning BANK errors.
- **One shared prefix list:** the accepted namespace prefixes now live in `protocol_roundtrip.LINT_PREFIXES` and are read, not restated, by the coupling test.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] src_unreadable message initially echoed the resolved absolute path**
- **Found during:** Task 2 (src-fixture lint verification)
- **Issue:** The path-recovery regex took the OS error's quoted filename, which is the resolved absolute path; the locked message then disclosed an absolute path the bank file does not contain, contrary to T-3-09's echo-the-authored-path intent.
- **Fix:** For the OS-error case, echo only the basename of the quoted path (which equals the directive's own filename); the escape-refusal case already carries the exact authored directive.
- **Files modified:** model.py
- **Verification:** `python itembank.py lint fixtures/lesson_broken_src_bank.md` now prints `[LESSON-SRC: missing_lesson.md] could not be read (...)`; full suite passes.
- **Committed in:** b3dbce0 (Task 2 commit)

**2. [Rule 3 - Blocking] tests/evidence_roundtrip.py's ordering assertion predated any BANK-tagged error**
- **Found during:** Task 2 full-suite run
- **Issue:** `test_lint_order_stable` asserted lint errors are in non-decreasing item order and treated any non-`Qn` tag as -1, so plan 03-03's first BANK-tagged error (`lesson.duplicate_heading` on the enlarged broken fixture) failed the suite.
- **Fix:** Extended the errors check to mirror the existing warnings check: non-BANK entries stay in item order and BANK entries must be last -- the convention `bank.answer_position_skew` already established.
- **Files modified:** tests/evidence_roundtrip.py
- **Verification:** evidence_roundtrip passes; full suite passes.
- **Committed in:** b3dbce0 (Task 2 commit)

**3. [Rule 3 - Plan discrepancy] The plan's '26 existing codes' and `len(c)==30` acceptance criterion miscounted**
- **Found during:** Task 1 acceptance verification
- **Issue:** The plan states 26 existing lint codes and an acceptance criterion of `len(LINT_CODES)==30`; the actual pre-plan count is 27 (verified by `import itembank` and the schema enum), so the correct post-plan total is 31.
- **Fix:** None needed in code -- 31 is the correct, verified total. The authoritative invariants (sortedness, uniqueness, schema-enum equality in both directions, Task 3's `e == set(LINT_CODES)`) all pass; the plan's literal `==30` cannot be satisfied without dropping an existing code and was recorded as a plan miscount rather than chased.
- **Files modified:** none (criterion documented)
- **Verification:** `protocol contract: ok (31 lint codes declared, ...)`; all Task 1 and Task 3 acceptance criteria except the miscounted literal pass.

---

**Total deviations:** 3 (1 bug, 2 plan/test discrepancies)
**Impact on plan:** All fixes were necessary for correctness and for the full suite to pass. No scope creep: evidence_roundtrip.py was the only out-of-plan file touched, and the change is a mechanical extension of an existing ordering invariant.

## Issues Encountered

- **Patch anchoring slip during Task 2:** an early edit briefly wired the lesson-supplied lint call into `cmd_build` instead of `cmd_serve` (the opposite of the plan's instruction). Caught by the serve-refusal verification showing 9 pre-existing errors and no lesson finding; corrected within the task, and the final code matches the plan exactly (build stays one-argument, serve passes the lesson).
- **Broken fixture orphan count:** with three headings and a single LESSON-REF pointing at a missing heading, all three headings are unreferenced, so `itembank lint fixtures/broken_bank.md` reports three `lesson.orphan_heading` warnings rather than one. This follows the plan's literal fixture instructions; CI greps assert the messages appear, not a specific count.
- **Pre-existing crash, out of scope:** `itembank build --force fixtures/broken_bank.md` crashes in `runtime.answer_text` on Q2's `CORRECT: F` (no option F). Present before this plan (verified against the parent commit); not caused by, and not fixed by, 03-03.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Ready for **03-04** (the renderer's real markdown scope and the Phase 9 fenced-code seam): the lesson grammar and reader are already in place, and lint now fails dangling references loudly instead of leaving them to a render-time surprise.
- Ready for **03-05** (`--ref` filtering) and **03-06** (`spec` grammar text): the `lesson.*` namespace is published, schema-valid, and CI-exercised.

## Self-Check: PASSED

All created files exist (`fixtures/lesson_broken_src_bank.md`, `03-03-SUMMARY.md`); all four task commits exist in `git log` (`c33a317`, `4654b84`, `b3dbce0`, `348d040`).

---
*Phase: 03-lesson-format-in-app-reader*
*Completed: 2026-08-08*
