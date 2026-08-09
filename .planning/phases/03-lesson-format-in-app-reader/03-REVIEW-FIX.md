---
phase: 03-lesson-format-in-app-reader
fixed_at: 2026-08-08T21:17:23-05:00
review_path: .planning/phases/03-lesson-format-in-app-reader/03-REVIEW.md
iteration: 1
findings_in_scope: 3
fixed: 3
skipped: 0
status: all_fixed
---

# Phase 03: Code Review Fix Report

**Fixed at:** 2026-08-08T21:17:23-05:00
**Source review:** `.planning/phases/03-lesson-format-in-app-reader/03-REVIEW.md`
**Iteration:** 1

**Summary:**
- Findings in scope: 3 (WR-01, WR-02, WR-03; default `critical_warning` scope -- IN-01 and IN-02 were out of scope)
- Fixed: 3
- Skipped: 0

All three warnings were contract-accuracy issues in the LESSON grammar's SPEC
text inside `model.py`, plus one spec-coverage assertion that had locked the
inaccurate boundary wording. Each fix makes the SPEC describe what the parser
and the locked tests actually do.

## Fixed Issues

### WR-01: SPEC's lesson-boundary rule contradicts the implemented parser and its locked test

**Files modified:** `model.py`, `tests/lesson_roundtrip.py`
**Commit:** 611917d
**Applied fix:** Reworded the SPEC to describe the real, context-sensitive
boundary: in `THE LESSON SECTION`, the lesson now runs "to the first `Qn.`
line that parses as a real question"; in `ONE CONSTRAINT`, a question-marker-
shaped line "ends the lesson only when it parses as a real question" and "a
line merely shaped like one stays in the prose," with the Pitfall-2 rationale
(a first-match-only boundary would silently cut illustrative prose) stated
instead of the old claim that the boundary is not context-sensitive. Updated
the two substring assertions in `test_spec_documents_lesson_grammar` to pin
the corrected meaning ("parses as a real question", "stays in the prose").
The parser and the locked Pitfall-2 test were intentionally left unchanged.

### WR-02: "one item carries at most one reference" is unenforced, and duplicate tags are silently dropped

**Files modified:** `model.py`
**Commit:** c84c1ae
**Applied fix:** Chose the reviewer's documentation alternative over adding a
new lint code: the SPEC now states the actual behavior -- "if an item carries
more than one `[LESSON-REF:]` tag, only the first is read" -- instead of
presenting an unenforced "at most one reference" rule beside enforced codes.
No parser or lint behavior changed, so no locked tests were affected.

### WR-03: headings containing `]` cannot be referenced by any item

**Files modified:** `model.py`
**Commit:** fb85db2
**Applied fix:** Documented the restriction in the SPEC: "a referenced
heading's text must not contain `]` -- the tag reads up to the first closing
bracket, so a bracketed heading can never be named." The parser guard and
grammar change were left for a future decision (the reviewer phrased them as
"consider"), since the SPEC now warns an authoring agent about the failure
mode and `item.lesson_ref_unknown` still fires if it happens.

## Verification

Verification ran inside the isolated review-fix worktree
(`git worktree` at `.claude/worktrees/rf-03-710-1786241564`, branch
`gsd-reviewfix/03-710`) against the committed source at HEAD:

- Tier 1: re-read each edited section; fix text present, surrounding code intact.
- Tier 2: `ast.parse` syntax check on `model.py` and `tests/lesson_roundtrip.py` -- passed.
- Targeted behavior: `python tests/lesson_roundtrip.py` (includes the five
  spec-coverage tests and the Pitfall-2 boundary lock) -- passed after each fix.

The full test suite was not run, per the per-fix verification scope; the
verifier phase handles end-to-end validation.

---

_Fixed: 2026-08-08T21:17:23-05:00_
_Fixer: the agent (gsd-code-fixer)_
_Iteration: 1_
