---
status: partial
phase: 07-selection-engine
source: [07-VERIFICATION.md]
started: 2026-08-10
updated: 2026-08-10
---

## Tests

### 1. Explain legibility (SEL-05)
expected: "itembank select --explain" output reads as plain English - each
line names the item, the reason, and a distinct runner-up - and leaks no key,
rationale, or option text.
result: needs-review
source: manual
evidence: "Sample output in 07-VERIFICATION.md (criterion 5). Automated
grammar checks pass; human eyeball of the wording is the E1 backstop."

### 2. /api/start preview writes no session
expected: Previewing a selection never appends evidence or creates a session.
result: pass
source: automated
evidence: "check_preview_writes_no_session passes; surfaces/session.py:155
documents the no-evidence preview contract."

### 3. Mode compositions differ
expected: diagnostic, practice, remediation, and exam each produce a session
whose composition matches its purpose.
result: pass
source: automated
evidence: "check_mode_compositions_differ passes (four modes differ, each per
its purpose)."

### 4. Selection settings and profiles
expected: The selection settings group exists, profiles expand key-by-key, and
explicit flags override profile keys.
result: pass
source: automated
evidence: "check_profile_flags_override passes; selection settings group and
profiles in schemas/settings.schema.json."

## Summary

total: 4
passed: 3
blocked: 0
needs-review: 1 (explain legibility)

## Gaps

No code defects found. The five roadmap criteria not covered by the executed
plans (guided path, fringe, blueprint/CASE, reach, pending-mark invariant) are
recorded in 07-VERIFICATION.md as gaps, not UAT failures.
