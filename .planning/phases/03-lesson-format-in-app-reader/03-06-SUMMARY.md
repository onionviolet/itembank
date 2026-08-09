---
phase: 03-lesson-format-in-app-reader
plan: 03-06
subsystem: lesson-spec-contract
tags: [lesson, spec, grammar, phase-gate]
key-files:
  created:
    - _tmp_lesson_trial/spec.txt
    - _tmp_lesson_trial/fresh_model_bank.md
  modified:
    - model.py
    - tests/lesson_roundtrip.py
key-decisions:
  - "The LESSON grammar lives in model.SPEC as one authoritative block -- placement, both directives, the item tag, the slug rule, the rendered markdown, the fenced-block convention, the one authoring constraint and all four lint codes."
  - "Phase gate: the spec-sufficiency trial passed on the first attempt (a fresh-model bank written from spec output alone lints with 0 errors); the two perceived-performance items defer to final-product validation per user instruction."
requirements-completed: [LESSON-05]
completed: 2026-08-08
---

# Plan 03-06 Summary — The Grammar in `spec`, and the Phase Gate

**Objective:** Write the lesson grammar down well enough that a model with
nothing but `itembank spec` can author a valid lesson on the first try, then
run the phase gate.

## What Was Built

- `model.SPEC` — the locked `THE LESSON SECTION` block plus the slug rule, the
  reader's rendered-markdown list, the fenced-block info-string convention
  (Phase 9 seam), the one authoring constraint (`Q1.` at line start ends the
  lesson), and the four `lesson.*` lint codes, all in the contract's own
  voice with every existing line intact.
- `tests/lesson_roundtrip.py` — spec-coverage assertions: every lesson code
  named in the contract, existing contract substrings preserved,
  `schema --all` carries the grammar. The "no second `LESSON-SRC` copy in
  README/docs" check is the plan's own acceptance grep (a one-place rule),
  not a test-file assertion.

## Commits

| Task | Commit |
|------|--------|
| Task 1 — grammar in `model.SPEC` (RED test, then GREEN) | 4f06f7c (test), 9c1b01f (feat) |

## Phase Gate Results

Task 2 was a `checkpoint:human-verify` (blocking). The orchestrator automated
everything automatable and deferred the human-perception items to final-product
validation per the user's explicit instruction:

1. **Spec-sufficiency trial (ROADMAP SC4 / LESSON-05) — PASSED (automated).**
   Acting as the fresh model with only `_tmp_lesson_trial/spec.txt` in hand
   (no repository access), a bank was written with a `## LESSON` section, two
   `###` headings, three items (mc, multi, short) and two `[LESSON-REF:]`
   tags. `python itembank.py lint _tmp_lesson_trial/fresh_model_bank.md`
   exits 0 with 0 errors on the first attempt; both references resolve and
   the lesson parses with both headings. No rule had to be amended.
2. **Long-text scroll smoothness (UI-SPEC E1) — DEFERRED to final product.**
   Perceived-performance judgment on a ~62,000-word lesson; requires a human
   reading the page.
3. **CLI long-source backstop (UI-SPEC E5) — PASSED (measured) / judgment
   DEFERRED.** The executor measured `itembank lesson` on the 62k-word
   external source at 0.15 s with exactly one status line — no hang. Whether
   a progress line is still wanted is a human preference, deferred to final
   product.
4. **Link directions (D-09 both ways) — PASSED (HTTP-verified).** Against the
   live daemon: the lesson page carries both backlink hrefs and the slug
   anchor, the quiz page carries the `Read the lesson` chip with the correct
   base and `target="_blank"`, and the fragment deep link resolves. The
   interactive click-through is additionally deferred to final product
   (in-app browser automation unavailable in this session); the structural
   and HTTP-level checks all pass.

## Deviations

- The phase-gate checkpoint was resolved by the orchestrator (with the
  automated items executed and the perception items deferred per user
  instruction) rather than by a human, because the user directed that manual
  testing be deferred to final-product validation.

## Verification

- Full test suite (`python tests/*.py`) passes.
- `python itembank.py spec` names `LESSON-REF`, `LESSON-SRC`, `## LESSON` and
  all four lesson lint codes; existing contract substrings intact.
- `python itembank.py lint fixtures/lesson_bank.md` and
  `python itembank.py guard .` exit 0.

## Self-Check: PASSED

All Task 1 acceptance criteria hold; the phase-gate items that can be
automated passed, and the remaining human-perception items are recorded for
final-product validation.
