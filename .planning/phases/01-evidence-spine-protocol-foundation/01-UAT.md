---
status: testing
phase: 01-evidence-spine-protocol-foundation
source: [01-VERIFICATION.md]
started: 2026-08-06T00:00:00Z
updated: 2026-08-06T00:00:00Z
---

## Current Test

number: 1
name: `itembank schema --all` is sufficient for a fresh model to author all six item types
expected: |
  A model with no repository access, given only the pasted output of `itembank schema --all`,
  authors one item of each of the six types plus one legal recorded response — with no
  back-and-forth needed to discover a field the schema left out.
awaiting: user response

## Tests

### 1. `itembank schema --all` sufficiency for a fresh model context

expected: Give a model with no repository access only the pasted output of `itembank schema --all`. Ask it to author one item of each of the six types (mc, multi, table, dnd, build, short) plus one legal recorded response. It succeeds from the schema text alone, with no back-and-forth to discover fields the schema omitted.

why_human: 01-06-PLAN.md's own Task 3 marks this a sufficiency judgment, not a string match. `tests/protocol_roundtrip.py` confirms the output parses, is self-contained, and is byte-stable across runs. None of that confirms a genuinely fresh model can author from it. 01-06-SUMMARY.md carried this forward undone, as the plan designed.

how_to_run: `python itembank.py schema --all` — paste the output into a fresh model context with no other files attached.

result: [pending]

### 2. `render_session_json`'s seed/selection approximation is acceptable

expected: Inspect a session recovered by `render_session_json` after the live session JSON is deleted. Judge whether reporting `seed: 0` always, and deriving `items`/`cursor`/`status` from the distinct item_refs the log proves were answered rather than the session's true original selection, is good enough for what builds on it — the day cockpit, resumed sittings, agent tooling.

why_human: 01-09-PLAN.md and 01-09-SUMMARY.md both document this as a deliberate, honest approximation rather than a bug. `render_session_json` cannot recover the original seed or cursor from an append-only log, because only the session file ever held them, and it says so rather than guessing. Whether that tradeoff is acceptable for the selection engine and retention work in later phases is a product decision, not a code-correctness question.

decision_shape: Either accept the approximation as-is, or open a follow-up plan that captures seed and original selection as first-class logged facts at session start.

result: [pending]

## Summary

total: 2
passed: 0
issues: 0
pending: 2
skipped: 0
blocked: 0

## Gaps
