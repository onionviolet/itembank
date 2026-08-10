---
status: testing
phase: 03-lesson-format-in-app-reader
source: [03-VERIFICATION.md]
started: 2026-08-08
updated: 2026-08-10
---

## Current Test

number: 1
name: Full-chapter lesson scroll smoothness (UI-SPEC E1 backstop)
expected: |
  Serving the ~62,000-word lesson at /lesson/big_bank scrolls top to bottom as
  one continuous document with no pagination, lazy loading, or perceptible
  stall.
awaiting: user response

## Tests

### 1. Full-chapter lesson scroll smoothness (UI-SPEC E1)
expected: One continuous document, no pagination/lazy loading, no perceptible stall while scrolling the ~62k-word lesson.
result: [pending]

### 2. Interactive click-through of both link directions (D-09 user flow)
expected: Lesson backlink lands on the quiz with that item pinned first; the Read the lesson chip opens a new tab at the right heading; a direct /lesson/<bank>#<slug> fragment lands on that section.
result: [pending] (structure and HTTP-level hrefs verified; interactive click-through not yet run)

### 3. Independent spec-sufficiency trial (ROADMAP SC4 / LESSON-05)
expected: A fresh model with only `itembank spec` authors a bank with a LESSON section, two headings, three items and a LESSON-REF tag that lints with 0 errors on the first attempt.
result: [pending] (the orchestrator-run trial with the same spec output lints 0 errors on the first attempt; an independent-model run is not yet done)

## Summary

total: 3
passed: 0
issues: 0
pending: 3
skipped: 0
blocked: 0

## Gaps

None. All automated must-haves pass (12/13, 0 failed); the single
present-but-behavior-unverified truth is item 2, whose structure is wired and
HTTP-verified.

## Note

Deferred to final-product validation per the user's explicit standing
decision (2026-08-08): automated tests are run by the agent; manual,
perception, and independent-model tests are deferred rather than blocking the
milestone.
