---
status: pending_human
phase: 05-check-item-type-code-editor
source: [05-VERIFICATION.md]
started: 2026-08-11
updated: 2026-08-11
---

## Current Test

[automated testing complete; two human checkpoints pending]

## Tests

### 1. Windows process-tree kill (plan 05-04 Task 1)
expected: On the target Windows 11 machine, the job-object kill terminates the whole tree; the escape rate over 50 iterations is a measured number; the forced taskkill fallback also kills the tree; runner.JobObjectExtendedLimitInformation is confirmed or corrected.
result: blocked
blocked_by: environment
reason: "The 05-04 spike requires an interpreter reporting win32. This session's shell is WSL2 (`python` reports linux) and cannot spawn any Windows process — tasklist.exe, where.exe and the target python.exe all fail at exec with 'run-detectors: unable to find an interpreter' (verified direct and via subprocess). Per the plan's own precondition ('if it does not say win32, stop'), the six steps are recorded PENDING in 05-SPIKE-RESULT.md: 0 of 50 runs executed on Windows; both kill paths unexercised; the enum constant unconfirmed. No measurement is fabricated."

### 2. End-of-phase manual pass (plan 05-07 Task 3)
expected: Five observations from a real browser against a served page: gutter row N on editor line N at 500 lines with a long line scrolling; Tab/Shift-Tab/undo feel; ten-case readout navigable + a never-terminating run rendering the pending treatment with its timeout row in the warning colour; no sentence in SPEC/README/page copy/refusals implying a safety promise; keyboard-only parity with /api/submit.
result: blocked
blocked_by: environment
reason: "This session cannot keep a daemon alive for a real browser: background jobs are denied by the command gate, and the browser backend returns ERR_CONNECTION_REFUSED once the launcher exits (verified by serving the bank and navigating). The five items are recorded PENDING. Partial automated evidence exists and is noted: node --test tests/js/ executes Tab insert + focus, Shift-Tab dedent, Enter newline, read-only-after-submit with the source visible, 1-based gutter growth, and no-wrap against the real vendored bundle."

### 3. Keyboard/editor contract (automated half of item 5)
expected: Tab inserts a literal tab and keeps focus; Shift-Tab dedents the current line only, never past column 0; Enter inserts a newline; after submit the editor is read-only with the source visible; the gutter is 1-based and grows; a long line does not wrap.
result: pass
source: automated
evidence: "node --test tests/js/ — 7/7 tests pass, executing the real vendored bundle + boot script under pinned jsdom 29.1.1 (tests/js/package-lock.json)."

### 4. Per-case matrix contract (automated)
expected: Each case renders one row (Case N, status from the stable reason, input where authored, expected vs pattern label, actual); a mixed pass/fail stays dichotomous; a null verdict renders pending; no case material reaches the page pre-answer.
result: pass
source: automated
evidence: "tests/check_roundtrip.py#check_matrix_contract — locked status strings, .case selectors, mixed-failure observations with distinct case_index/reason, pre-submit contract leak-free, killed run -> None + timeout observation."

### 5. Three refusal states (automated)
expected: Offline file page shows the locked refusal + skip that records and counts nothing; network refusal renders as pending; language refusal as error; honest-limits survives all three; connectivity copy unchanged.
result: pass
source: automated
evidence: "tests/check_roundtrip.py#check_refusal_states — file refusal + skip in the built page, both server sentences in the served page (distinct), skip handler advances without verify/settle/close, connectivity sentences unchanged, no generic message (grep 0)."

### 6. Vendored editor + honest-limits identity (automated)
expected: The CM6 bundle is pinned, hashed and license-reviewed under §4a, embedded locally with no CDN; the honest-limits statement is one constant in SPEC and the page; the claim-word gate passes.
result: pass
source: automated
evidence: "tests/check_roundtrip.py#check_vendor_integrity + check_honest_limits_gate; python itembank.py guard . — PASS."

### 7. Schema + renderer-independent consumer (automated)
expected: Every check public_item validates against item.schema.json; invalid versions/extra executable renderer fields/non-string responses are rejected; a killed-at-timeout result validates with null verdict/score; a non-page consumer reaches the same /api/submit semantics.
result: pass
source: automated
evidence: "tests/check_roundtrip.py#check_schema_consumer + tests/protocol_roundtrip.py#test_check_contract_pins — PASS."

### 8. Full suite
expected: python tests/*_roundtrip.py and node --test tests/js/ exit 0.
result: pass (with two pre-existing environmental exclusions)
source: automated
evidence: "Full suite green except tests/packaging_roundtrip.py (missing Windows-built dist — pre-existing, documented in 05-02-SUMMARY) and the tolerated presentation_roundtrip FAIL line (pre-existing, exits 0). node --test tests/js/ 7/7."

## Sign-off

- [x] All automated acceptance criteria across plans 05-01..05-07 pass.
- [ ] Human checkpoint 1 (Windows kill spike, 05-04) — PENDING.
- [ ] Human checkpoint 2 (end-of-phase pass, 05-07 Task 3) — PENDING.
- [x] No claim anywhere in this phase's output asserts a safety property the runtime does not have (claim-word gate + reading-pass handoff recorded).
