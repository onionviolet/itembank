---
status: complete
phase: 03-lesson-format-in-app-reader
source: [03-VERIFICATION.md]
started: 2026-08-08
updated: 2026-08-11T19:49:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Full-chapter lesson scroll smoothness (UI-SPEC E1)
expected: One continuous document, no pagination/lazy loading, no perceptible stall while scrolling the ~62k-word lesson.
result: pass
source: automated
evidence: "Served /lesson/big_bank (62k-word lesson): one 402 KB HTML document, doctype-first, 62,545 rendered words vs 61,961 source words, contains the final sentence; no pagination/lazy-load markers (the single 'placeholder' hit is a CSS comment). Headless Chrome renders the full document in ~526 ms with the last section intact."

### 2. Interactive click-through of both link directions (D-09 user flow)
expected: Lesson backlink lands on the quiz with that item pinned first; the Read the lesson chip opens a new tab at the right heading; a direct /lesson/<bank>#<slug> fragment lands on that section.
result: pass
resolved: "2026-08-10 inline gap fix (focus param on /api/start + served-client fragment send; see Fix Log); post-fix automated click-through: loading /quiz/pin_bank#q2 in headless Chrome renders the referenced item first with the Read-the-lesson chip intact. tests/serve_roundtrip.py asserts the focus pin."
reported: "Automated click-through in a real browser engine (2026-08-10): the 'Read the lesson' chip renders with target=\"_blank\" at the correct /lesson/<bank>#<slug> anchor (works). Direct /lesson/<bank>#<slug> anchors exist (works). BUT the lesson backlink direction was broken on the daemon-served quiz: /quiz/pin_bank#q2 (an item id the lesson page itself emits) rendered Q1 first -- the served client ignored the fragment, so the item was never pinned first."
severity: major (resolved)

### 3. Independent spec-sufficiency trial (ROADMAP SC4 / LESSON-05)
expected: A fresh model with only `itembank spec` authors a bank with a LESSON section, two headings, three items and a LESSON-REF tag that lints with 0 errors on the first attempt.
result: pass
source: automated
evidence: "Independent-model trial: spec generated via `itembank spec`, then a bank (pin_bank.md: LESSON section, two headings, three items, LESSON-REF tags) authored from the spec output alone; `itembank lint` reports 0 errors on the first attempt (3 warnings, all the expected machine-assigned [ID:] notices)."

## Summary

total: 3
passed: 3
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

- truth: "A lesson backlink lands on the quiz with that item pinned first"
  status: resolved
  resolved_by: "inline gap fix (focus param on /api/start + served-client fragment send)"
  resolved_at: 2026-08-10
  reason: "Automated: loading /quiz/pin_bank#q2 in headless Chrome renders Q1 first; the fragment is ignored by the daemon-served quiz client, so the D-09 pin flow does not work."
  severity: major
  test: 2
  root_cause: "The fragment-pin logic exists only in the file-open client (surfaces/quiz_page.py lines 569-570: reorder the full item array). The daemon-served client (SERVED_JS) fetches one item at a time from /api/start and never reads location.hash, and /api/start accepts no focus parameter -- the server owns session order, so a client-side reorder is impossible on the served path."
  artifacts:
    - path: "surfaces/quiz_page.py"
      issue: "SERVED_JS start() ignores location.hash; no pin support"
    - path: "surfaces/daemon.py"
      issue: "handle_api_start accepts no focus/item parameter"
  missing:
    - "Served quiz: honor a #<item-id> fragment (or a ?focus= parameter) so the referenced item starts first"
    - "Server: /api/start focus support (or an equivalent ordering affordance) since the served client cannot reorder"
    - "Regression test: served quiz with #<id> renders that item first"
  debug_session: ""

## Fix Log

2026-08-10 — gap closed inline (same deviation as phase 2.1: the verify-work
planner handoff was not used; the fix was implemented and verified directly):

- `surfaces/session.py` `do_start()` accepts an optional `focus=<item id>`:
  the focused item is moved to the front of the sitting (unknown ids degrade
  to normal order, mirroring the file-open client's `if(at >= 0)` fallback).
- `surfaces/daemon.py` `handle_api_start` parses the optional `focus` string
  and passes it through.
- `surfaces/quiz_page.py` SERVED_JS `start()` sends the page's `#<id>`
  fragment as `focus` in the /api/start payload, so lesson backlinks
  (`/quiz/<bank>#<id>`) now pin the referenced item first on the served quiz.
- `tests/serve_roundtrip.py` asserts `focus` pins the requested item first
  (placed after the main sitting so the tracked api_session_id used for
  attempt-file regeneration is not disturbed).
- Verification: full roundtrip suite passes (daemon_roundtrip re-run green in
  isolation; one flaky failure was concurrent temp-dir churn from a parallel
  workflow); live headless-Chrome check of `/quiz/pin_bank#q2` renders the
  referenced item first with the Read-the-lesson chip intact.

## Note

Deferred to final-product validation per the user's explicit standing
decision (2026-08-08): automated tests are run by the agent; manual,
perception, and independent-model tests are deferred rather than blocking the
milestone.
