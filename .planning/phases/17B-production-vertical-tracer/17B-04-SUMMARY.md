---
phase: 17B-production-vertical-tracer
plan: 04
wave: 4
date: 2026-09-05
status: tasks 1 to 3 complete; task 4 (human acceptance) deferred to Weibao
---

# 17B-04 summary

## Why this summary exists

A measured fact contradicted the plan. Task 1's restore drill failed: the
plan assumed the frozen 14B package surface could carry the tracer's unit,
and it could not. Six of seven canonical objects and zero of forty evidence
events crossed a clean-machine restore. The plan also assumed a Windows
host and a human acceptance signature, and neither was available.

Everything else is in the record it belongs in and is not repeated here:
the transcripts in `evidence/17B-04-restore.md`,
`evidence/17B-04-egress.md`, and `evidence/17B-04-restore-repair.md`, and
the final gate states, defects, owners, and freeze condition in
`17B-GATES.md`.

## What happened

- **Task 1 (G10), fail then repaired.** `tools/restore_drill_17b.py` is a
  stdlib-only drill taking `--commit`, so 17C can sweep any commit rather
  than this working tree. It ran offline for real (proxies at the discard
  port, sockets raising inside the worker) and reported two defects,
  `17B-04 D-06 item 10` and `item 11`. Both were contract changes in frozen
  surfaces, so wave 4 routed them rather than patching in place. They were
  repaired afterwards under Weibao's 2026-09-05 directive; the repair, the
  two additive record types it added, and the re-run are in
  `evidence/17B-04-restore-repair.md`.
- **Task 2 (G11), pass.** Egress is not applicable, established four
  independent ways rather than by trusting waves 2 and 3. The
  rights-unknown refusal and the redaction check both hold.
- **Task 3, exit record.** Written into `17B-GATES.md`. Defect ids are
  wave-qualified throughout, because waves 2 and 3 each numbered their
  D-06 items from 1 and the bare numbers collide.
- **Task 4, human acceptance.** Deferred to Weibao under his standing
  directive, recorded as owed, never self-certified.

## Deviations

The drill ran POSIX rather than PowerShell (this machine is macOS, not the
Windows host D-07 assumes). The G4 screen-reader walk and the G8 visual
acceptance stay owed to Weibao.
