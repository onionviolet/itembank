---
name: problem-intake
description: Capture user-reported product problems with exact observations, bounded diagnosis, ownership, and evidence-based closure. Use for live learner feedback, regressions, or usability defects. Do not use for speculative ideas or broad product vision.
---

# Problem Intake

Use `.planning/PROBLEM-LEDGER.md` as the one intake for user-reported product
problems. Do not create a second issue list. `WINDOWS.md` remains the narrower
ship-blocker register and is updated only when the release process requires it.

## Capture

1. Preserve the user's observation verbatim with date, flow, input method, and
   environment facts they actually supplied.
2. Record diagnosis below it as a separate agent statement. Mark it unverified
   until a reproduction or targeted test supports it.
3. Link an existing record when the report duplicates it. Do not merge reports
   merely because their wording is similar.

## Route

Name the owning phase, module, human reviewer, or external dependency. A
problem affecting scoring, keyed disclosure, evidence, identity, or recovery
requires the project's consequential-work gate. A presentation-only repair may
stay bounded when it keeps those authorities unchanged.

## Close honestly

A row moves from reported to reproduced, repair in progress, fixed and
deterministically verified, human accepted, blocked, or owned elsewhere.
State the exact verification command or direct observation. Automated checks
prepare accessibility review but do not certify it. Preserve failed and
unavailable legs.

## Handoff

Return the record ID, exact user observation, diagnosis status, owner, changed
paths, checks, open risks, and the next observable action. Keep real learner
data out of repository records.
