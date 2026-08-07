---
status: testing
phase: 02-daemon-consolidation-settings-foundation
source: [02-VERIFICATION.md]
started: 2026-08-07T19:29:34Z
updated: 2026-08-07T19:29:34Z
---

## Current Test

number: 1
name: `--lan` reaches a phone on the same wifi
expected: |
  Start `itembank daemon <dir> --lan`, note the printed phone URL, open it in a browser on a
  phone joined to the same wifi, and confirm the index and a quiz page render. The page renders
  on the second device, proving the bind actually widened beyond loopback and is reachable across
  the network, not just locally addressable.
awaiting: user response

## Tests

### 1. `--lan` reaches a phone on the same wifi
expected: |
  Start `itembank daemon <dir> --lan`, note the printed phone URL, open it in a browser on a
  phone joined to the same wifi, and confirm the index and a quiz page render. The page renders
  on the second device, proving the bind actually widened beyond loopback and is reachable across
  the network, not just locally addressable.
result: [pending]

### 2. `/` and `/report` render legibly at scale
expected: |
  Open `/` and `/report?session=<id>` in a real browser at various window widths and with 20+
  scanned banks/plans, and with a session carrying 10+ pending short items; confirm the 8-point
  spacing scale, the four-font-size/two-weight typography, the 60/30/10 color split, and that
  rows/objective lists wrap and scroll with the page rather than truncating or clipping. Visual
  rendering matches 02-UI-SPEC.md's Spacing/Typography/Color contract at scale.
result: [pending]

### 3. Concurrent `config set` writes never tear `itembank.json`
expected: |
  Run two `itembank config set` invocations against the same `itembank.json` at effectively the
  same instant (e.g. two shells launched together) and confirm the file never ends up torn or
  unparseable, and that the surviving value is one of the two writers' values (last-writer-wins),
  not a hybrid. No torn/corrupt file under concurrent writes; at most one writer's change is
  silently dropped.
result: [pending]

## Summary

total: 3
passed: 0
issues: 0
pending: 3
skipped: 0
blocked: 0

## Gaps
