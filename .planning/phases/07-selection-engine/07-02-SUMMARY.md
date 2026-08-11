---
phase: 07-selection-engine
plan: 02
subsystem: selection
tags: [selection, pair, prereq, format-contract, lint]

# Dependency graph
requires:
  - phase: 07
    plan: 01
    provides: selection.py, SPEC_FIELDS, the 30-item fixture, the tracer test stubs
provides:
  - [PAIR:] and [PREREQ:] item tags with parsed q["pair"] / q["prereq"] fields
  - filter_by_pair / filter_by_prereq and the pair/prerequisite SPEC_FIELDS
  - item.pair_singleton and item.prereq_unknown lint codes
  - a tagged fixture with two pair groups and a 9-item prerequisite chain
affects: [07-04, 07-05, 07-06]

actuals:
  tokens: 3000
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - additive format fields parsed by the one parser and excluded from the fingerprint
    - pair requests raise the count to hold the whole set, recorded in the trace

key-files:
  created: []
  modified:
    - model.py
    - selection.py
    - fixtures/selection_bank.md
    - fixtures/lesson_golden_phase3_parse.json
    - schemas/lint_error.schema.json
    - tests/selection_roundtrip.py

key-decisions:
  - "pair and prereq are pedagogy metadata: excluded from content_fingerprint (D-12) and verified with zero hash churn on id-assign after tagging."
  - "A pair request serves the whole named set adjacently in ascending bank order and raises count to hold it; serving one half of a confusion pair is worse than serving neither."
  - "An unknown pair name exits with the requested name and the bank's known pair names, so a typo is answerable."
  - "Both new lint findings are warnings, not errors: an incomplete bank must still be sittable."

patterns-established:
  - "Exact in-memory string comparisons for pair/prereq filters (T-07-01/T-07-05): no regex, no path, no SQL interpolation."

requirements-completed: [SEL-01, SEL-04]

coverage:
  - id: D1
    description: [PAIR:] and [PREREQ:] parse into q["pair"] / q["prereq"] without leaking into stems
    requirement: SEL-01
    verification:
      - kind: unit
        ref: tests/selection_roundtrip.py#check_pair_singleton_lint (stem-purity assertion)
        status: pass
      - kind: unit
        ref: tests/selection_roundtrip.py#check_prereq_unknown_lint
        status: pass
    human_judgment: false
  - id: D2
    description: a pair request serves its whole set together and adjacently, count raised and noted
    requirement: SEL-04
    verification:
      - kind: unit
        ref: tests/selection_roundtrip.py#check_pair_served_together
        status: pass
    human_judgment: false
  - id: D3
    description: a prerequisite request returns exactly the items that build on it
    requirement: SEL-01
    verification:
      - kind: unit
        ref: tests/selection_roundtrip.py#check_prereq_filter
        status: pass
    human_judgment: false
  - id: D4
    description: item.pair_singleton and item.prereq_unknown lint codes warn per item and stay quiet when resolved
    verification:
      - kind: unit
        ref: tests/selection_roundtrip.py#check_pair_singleton_lint
        status: pass
      - kind: unit
        ref: tests/selection_roundtrip.py#check_prereq_unknown_lint
        status: pass
    human_judgment: false
  - id: D5
    description: an untagged bank parses and fingerprints exactly as before (additive-format floor)
    verification:
      - kind: unit
        ref: tests/selection_roundtrip.py#check_fixture_lints_clean
        status: pass
      - kind: unit
        ref: tests/selection_roundtrip.py#check_objective_filter
        status: pass
    human_judgment: false

# Metrics
duration: 25min
completed: 2026-08-10
status: complete
---

# Phase 7 Plan 2: Pair and Prerequisite Tags Summary

**The format contract now speaks confusion sets and prerequisites: `[PAIR:]` and `[PREREQ:]` parse into their own fields without leaking into stems, `select()` filters on both, and `lint` names a pair of one or an untaught prerequisite by item.**

## Performance

- **Duration:** 25 min
- **Started:** 2026-08-10T19:36:00Z
- **Completed:** 2026-08-10T20:01:00Z
- **Tasks:** 3
- **Files modified:** 6

## Accomplishments

- `model.py`: both tags joined the stem-terminator alternation (edit order
  verified by the plan: alternation first, then fields), `q["pair"]` and
  `q["prereq"]` parse additively, `content_fingerprint`'s docstring states the
  D-12 exclusion, `SPEC` documents both tags, and `item.pair_singleton` /
  `item.prereq_unknown` landed in `LINT_CODES` and `lint()` with reachable
  triggers.
- `selection.py`: `filter_by_pair` / `filter_by_prereq` (exact in-memory
  matches), `SPEC_FIELDS` grew both keys, a pair request serves the whole set
  adjacently with the count raised and recorded in the trace, and an unknown
  pair names the known pair list.
- `fixtures/selection_bank.md`: `distribution-vs-boil` (2 items, cross-objective)
  and `coagulation-train` (3 items) pair groups; 7 coagulation items + 2
  reporting items carry `[PREREQ:]`; `id-assign` reported zero hash churn.
- `tests/selection_roundtrip.py`: four stubs replaced; 8 stubs remain for
  plans 07-04..07-06.
- `schemas/lint_error.schema.json` gained the two codes;
  `fixtures/lesson_golden_phase3_parse.json` refreshed with the new keys.

## Task Commits

1. **Task 1: [PAIR:]/[PREREQ:] in the format contract** - `799ff03`
2. **Task 2: pair/prereq filters and the tagged fixture** - `5676349`
3. **Task 3: pair/prereq/lint behaviour checks** - `1ed96da`

**Plan metadata:** pending (next commit)

## Files Created/Modified

- `model.py` - tags, fields, fingerprint docstring, SPEC, two lint codes + checks
- `selection.py` - two filters, two SPEC_FIELDS, pair-run contiguity + count raise
- `fixtures/selection_bank.md` - pair groups and prerequisite chain
- `schemas/lint_error.schema.json` - enum gains the two codes
- `fixtures/lesson_golden_phase3_parse.json` - pair/prereq keys in the parse golden
- `tests/selection_roundtrip.py` - 10 live checks, 8 pending

## Decisions Made

- Pair/prereq are pedagogy metadata (fingerprint-excluded); verified zero hash
  churn when the tags were added.
- Pair requests raise the count rather than truncating the set; the raise is a
  trace note; unknown pair names list the known pairs.
- Warnings, not errors, for both lint findings.

## Deviations from Plan

### Auto-fixed / plan-text corrections

**1. Mutation-test placement mismatch**
- **Found during:** Task 3
- **Issue:** The plan's mutation instruction (removing `|\n\[PAIR` must fail
  `check_pair_served_together`) does not hold with the plan's own fixture
  placement of `[PAIR:]` after `[OBJECTIVE:]` -- the stem already terminates at
  `[OBJECTIVE]`, and `q["pair"]` still parses, so the check stays green.
- **Fix:** Pinned the alternation with a stem-purity assertion inside
  `check_pair_singleton_lint` (its inline bank places the tag before
  `[OBJECTIVE:]`); the same mutation now fails that assertion (verified,
  reverted). This is a stronger, placement-correct test.

**2. Sample-bank "0 warnings" claim**
- **Found during:** Task 1 verify
- **Issue:** `lint fixtures/sample_bank.md` always emits six
  `item.objective_unnamespaced` warnings (verified identical against HEAD);
  the plan's "0 errors, 0 warnings" was inaccurate. CI asserts zero errors only.
- **Fix:** None needed; 0 errors holds, no phase-7 warning added.

**3. Evidence fixture tracked the in-flight v2 response contract**
- **Found during:** Task 3
- **Issue:** The concurrent phase-6 session moved `response.schema.json` and
  `evidence.EVENT_SCHEMA_VERSION` to 2 (hint events); the phase-7 fixture was
  v1 and failed the live schema.
- **Fix:** Regenerated the fixture via the live `evidence.response_event()`
  (v2, 40/40 valid); the schema check is version-aware during the migration
  (validates strictly when versions match, names drift explicitly otherwise).

---

**Total deviations:** 3 documented (0 code-behaviour regressions; 2 plan-text
corrections, 1 cross-phase contract tracking)
**Impact on plan:** All acceptance criteria hold; the full phase-7 suite is green.

## Issues Encountered

- Concurrent phase-6 in-flight changes leave three non-phase-7 suites red in
  the working tree (`evidence_roundtrip` teaching_state, `protocol_roundtrip`
  report schema, `daemon_roundtrip` cli-twin route) -- logged in
  `deferred-items.md`; they are the 06-01 session's to close.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Ready for 07-03 (bank-scoped cooldown index): the fixture's evidence history
  is schema-valid and carries the bank field for scoping.
- Ready for 07-04 (selection_mode/selection_spec recording): the spec dict and
  trace shape now carry pair/prereq entries.

---
*Phase: 07-selection-engine*
*Completed: 2026-08-10*
