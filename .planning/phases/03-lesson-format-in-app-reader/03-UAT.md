---
status: diagnosed
phase: 03-lesson-format-in-app-reader
source: [03-VERIFICATION.md]
started: 2026-08-08
updated: 2026-08-10T23:10:00Z
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
result: issue
reported: "Automated click-through in a real browser engine: the 'Read the lesson' chip renders with target=\"_blank\" at the correct /lesson/<bank>#<slug> anchor (works). Direct /lesson/<bank>#<slug> anchors exist (works). BUT the lesson backlink direction is broken on the daemon-served quiz: /quiz/pin_bank#q2 (an item id the lesson page itself emits) renders Q1 first -- the served client ignores the fragment, so the item is never pinned first."
severity: major

### 3. Independent spec-sufficiency trial (ROADMAP SC4 / LESSON-05)
expected: A fresh model with only `itembank spec` authors a bank with a LESSON section, two headings, three items and a LESSON-REF tag that lints with 0 errors on the first attempt.
result: pass
source: automated
evidence: "Independent-model trial: spec generated via `itembank spec`, then a bank (pin_bank.md: LESSON section, two headings, three items, LESSON-REF tags) authored from the spec output alone; `itembank lint` reports 0 errors on the first attempt (3 warnings, all the expected machine-assigned [ID:] notices)."

## Summary

total: 3
passed: 2
issues: 1
pending: 0
skipped: 0
blocked: 0

## Gaps

- truth: "A lesson backlink lands on the quiz with that item pinned first"
  status: failed
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

## Note

Deferred to final-product validation per the user's explicit standing
decision (2026-08-08): automated tests are run by the agent; manual,
perception, and independent-model tests are deferred rather than blocking the
milestone.
