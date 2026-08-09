---
phase: 03-lesson-format-in-app-reader
reviewed: 2026-08-08T21:15:00Z
depth: standard
files_reviewed: 2
files_reviewed_list:
  - model.py
  - tests/lesson_roundtrip.py
findings:
  critical: 0
  warning: 3
  info: 2
  total: 5
status: issues_found
---

# Phase 03: Code Review Report

**Reviewed:** 2026-08-08T21:15:00Z
**Depth:** standard
**Files Reviewed:** 2
**Status:** issues_found

## Summary

Reviewed plan 03-06's changes (`git diff 502d378..HEAD`): the new `THE LESSON
SECTION` / `THE SLUG RULE` / `WHAT THE READER RENDERS` / `ONE CONSTRAINT` /
`LESSON LINT CODES` blocks in `model.SPEC`, the `[LESSON-REF:]` shared-field
line, and five new spec-coverage tests in `tests/lesson_roundtrip.py`. The
change is purely additive (doc text plus assertions), and every new assertion
passes against the current code, so there are no Critical findings and no
security issues.

The concern is contract accuracy, which is the point of this plan: the SPEC is
meant to let an authoring agent produce a valid lesson with no source access,
yet three of its claims disagree with the parser behavior the test suite locks
in. The most serious is the lesson-boundary rule (WR-01), which states the
opposite of the deliberate, test-locked Pitfall-2 behavior. The remaining
warnings cover unenforced or undocumented tag constraints, and the info items
are wording-precision and coverage-claim nits.

## Warnings

### WR-01: SPEC's lesson-boundary rule contradicts the implemented parser and its locked test

**File:** `model.py:483-484`, `model.py:519-524`
**Issue:** The new SPEC text states the lesson "run[s] to the first `Qn.`
marker" and, in ONE CONSTRAINT, that "A line inside lesson prose that begins
like a question marker -- `Q1.` at the start of a line -- ends the lesson
there," explicitly claiming the boundary is *not* context-sensitive. The
implementation is the opposite: `parse_lesson()` (model.py:172-176, 199-206)
only stops at a chunk that both begins with `Qn.` and parses as a real
question, and `tests/lesson_roundtrip.py:164-211`
(`test_prose_line_shaped_like_question_marker`) locks that a `Q1.`-shaped
prose line stays inside the lesson. Reproduced live: a bank whose lesson
contains "Q1. This is a prose line, not a question." parses both headings and
keeps the line in the first heading's body. The new
`test_spec_documents_lesson_grammar` (tests/lesson_roundtrip.py:1455-1484)
asserts the substrings "question marker" and "ends the lesson," so the test
suite now blesses the inaccurate sentence. An authoring agent gets a false
model of the boundary, and a maintainer "fixing" the parser to honor the spec
would break the Pitfall-2 protection and truncate real lessons.
**Fix:** Reword the SPEC to describe the actual boundary, e.g. "a line that
begins like a question marker and parses as a complete question ends the
lesson; a line merely shaped like one stays in the prose" -- and update the
new substring assertions to match. Alternatively, change `parse_lesson()` and
the locked test to enforce the spec's context-insensitive rule, but that
reverses the deliberate design decision documented at model.py:172-176.

### WR-02: "one item carries at most one reference" is unenforced, and duplicate tags are silently dropped

**File:** `model.py:48`, `model.py:497-499`
**Issue:** The SPEC asserts "one item carries at most one reference" as a
rule, but nothing enforces it. `parse_question()` reads the tag with
`grab()` (first match only), and `LINT_CODES` has no duplicate-reference code.
Reproduced live: an item carrying `[LESSON-REF: Alpha]` and `[LESSON-REF:
Beta]` parses with `lesson_ref == "Alpha"` and lint returns zero errors for
the dropped tag -- worse, the dropped `Beta` reference then triggers
`lesson.orphan_heading` for the Beta section, actively misreporting the
author's intent. The rule is presented alongside enforced rules (e.g.
`item.lesson_ref_unknown`), so an authoring agent reasonably expects a
violation to be caught.
**Fix:** Add an `item.lesson_ref_duplicate` lint code (and decide whether the
first or last tag should win), or soften the SPEC to state the actual
behavior: "if an item carries more than one `[LESSON-REF:]`, only the first
is read."

### WR-03: headings containing `]` cannot be referenced by any item

**File:** `model.py:48`, `model.py:497`
**Issue:** The tag regex `\[LESSON-REF:\s*(.*?)\]` is non-greedy and stops at
the first `]`, so a heading whose text contains a bracket -- e.g. `A
[Special] Heading` -- can never be referenced. Reproduced live:
`[LESSON-REF: A [Special] Heading]` parses as `A [Special`, slugifies to
`a-special` and fails against the heading's slug `a-special-heading`,
producing `item.lesson_ref_unknown`. The new SPEC promises the tag "names
readable heading text," with no warning about this failure mode, which
defeats the plan's first-try authoring goal.
**Fix:** Document the restriction in the SPEC (e.g. "heading text must not
contain `]`"), and consider a parser guard or a tag grammar that captures the
full line's bracket group, with tests for both.

## Info

### IN-01: Slug rule "punctuation dropped" is imprecise about hyphens

**File:** `model.py:502-503`
**Issue:** The SPEC says a heading's slug is text "lowercased, whitespace
collapsed, punctuation dropped." `lesson_slug()` (model.py:145-165) actually
keeps hyphens: it drops every character outside ASCII letters, digits, spaces
and hyphens, then collapses whitespace runs to hyphens. So "A-B" and "AB" do
not collide, although "punctuation dropped" predicts they do -- an author
asked to predict collisions gets the wrong answer for hyphenated headings.
**Fix:** Tighten the wording, e.g. "drops every character except ASCII
letters, digits, spaces and hyphens, then collapses whitespace runs to a
single hyphen."

### IN-02: SUMMARY claims a README/docs duplicate-guard test that is not in the diff

**File:** `tests/lesson_roundtrip.py:1453-1540`
**Issue:** The 03-06 SUMMARY's "What Was Built" section credits
`tests/lesson_roundtrip.py` with an assertion that "no second `LESSON-SRC`
copy exists in README/docs," but the committed diff adds only the five
spec-substring tests; no README/docs scan exists anywhere in `tests/`.
Today's repo state happens to satisfy the claim, but nothing guards it from
regressing when a future doc rewrite re-states the grammar.
**Fix:** Add the assertion (scan README.md/docs for a second `[LESSON-SRC:`
grammar block and fail if found), or correct the SUMMARY so the claim is not
attributed to the test suite.

---

_Reviewed: 2026-08-08T21:15:00Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
