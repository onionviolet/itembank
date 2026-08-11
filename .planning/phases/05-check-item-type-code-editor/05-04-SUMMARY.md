---
phase: 05-check-item-type-code-editor
plan: 04
subsystem: verification
tags: [windows, spike, job-object, taskkill, escape-rate]

requires:
  - phase: 05-check-item-type-code-editor (05-02)
    provides: the Windows job-object kill (new_job_object/assign_to_job), the taskkill fallback, the _FORCE_TASKKILL_FALLBACK switch, fixtures/grandchild_spawner.py, tests/check_kill_roundtrip.py

provides:
  - 05-SPIKE-RESULT.md — the measured-or-blocked Windows kill record (this plan's record is a documented blocker, not a measurement)
  - Honest disposition of the escape-rate question: unmeasured and recorded PENDING, never claimed zero

affects: [05-07 end-of-phase pass, 05-VALIDATION.md rows 1-2, 05-RESEARCH.md Windows section supersession]

actuals:
  tokens: 14000
  tasks: 2
  commits: 1

tech-stack:
  added: []
  patterns:
    - "A spike record that states a blocker and a PENDING number rather than fabricating a measurement"
    - "Evidence recorded as literal outputs, including the exact run-detectors error and exit status"

key-files:
  created:
    - .planning/phases/05-check-item-type-code-editor/05-SPIKE-RESULT.md
  modified: []

key-decisions:
  - "Task 1 (the six-step Windows run) is recorded PENDING, not verified: this executor's shell is WSL2 and cannot spawn any Windows process (every PE binary fails at exec with 'run-detectors: unable to find an interpreter', both directly and via subprocess). The plan's own precondition ('if it does not say win32, stop') applies, so no escape rate, path outcome, or enum-constant verdict is claimed."
  - "05-RESEARCH.md's Windows section is NOT marked superseded: supersession is deferred until the six steps actually run, per the research document's own Metadata condition (the spike 'either confirms or corrects Assumption A3 and A4'). A blocker report does not meet that bar."
  - "The record includes the residual-gap section (bpo-1677688 / thread handle) from source, since that gap is a standing design property independent of the measurement."

requirements-completed: []

coverage:
  - id: W1
    description: "The Windows kill was to be executed on the target machine and the escape rate measured over 50 iterations, both paths exercised, the enum constant settled"
    requirement: CODE-04
    verification:
      - kind: other
        ref: "05-SPIKE-RESULT.md — six-step table with literal outcomes: steps 1-6 could not run because the shell is WSL2 and cannot spawn Windows processes"
        status: pending
    human_judgment: true
    rationale: "Environment blocker: the executor shell (WSL2, python reports linux) cannot execute PE binaries at all (run-detectors error, exit 2, reproduced for tasklist.exe, where.exe, python.exe, direct and via subprocess). The plan's precondition stops the run at step 1. The only runnable evidence — python tests/check_kill_roundtrip.py on the Linux interpreter — exits 0 and proves the POSIX killpg path, not the Windows one."
  - id: W2
    description: "The measurement is recorded with its environment and sample size, stating no claim beyond the observed rate"
    requirement: CODE-04
    verification:
      - kind: doc
        ref: "grep -iqE '(out of 50|of 50 runs)' 05-SPIKE-RESULT.md -> 2 (0 of 50 runs executed)"
        status: pass
      - kind: doc
        ref: "grep -iqE 'bpo-1677688|thread handle' 05-SPIKE-RESULT.md -> 2"
        status: pass
      - kind: doc
        ref: "grep -iq 'JobObjectExtendedLimitInformation' 05-SPIKE-RESULT.md -> 1"
        status: pass
      - kind: doc
        ref: "the claim-word doc gate over 05-SPIKE-RESULT.md -> 0"
        status: pass
    human_judgment: false
duration: 60min
completed: 2026-08-11
status: complete-with-pending
---

# Phase 05: Check item type — Plan 04 Summary

**The Windows process-tree kill spike was attempted on the target machine and could
not be executed: this executor's shell is WSL2 and cannot spawn any Windows process,
so the six-step measurement is recorded as PENDING with full literal evidence rather
than a fabricated verdict. The record (05-SPIKE-RESULT.md) documents the blocker, the
runnable POSIX-side evidence, and the three deferrals (escape rate, both paths'
outcomes, the enum constant).**

## Performance

- **Duration:** 60 min
- **Tasks:** 2 (Task 1 checkpoint run + Task 2 record)
- **Commits:** 1 (docs)

## Status of the blocking checkpoint (Task 1)

**PENDING — human verification required.** The plan's Task 1 has a blocking
checkpoint whose precondition is that the machine reports `win32`. This machine is the
target Windows 11 host, but the shell available to this executor is WSL2:

- `python` reports `sys.platform == "linux"` (Python 3.13.3, `/usr/bin/python`).
- **No Windows process can be spawned at all.** Verified for three PE binaries
  (`tasklist.exe`, `where.exe`, the target interpreter
  `C:\Users\wayba\AppData\Local\Programs\Python\Python313\python.exe`): each fails at
  exec with `run-detectors: unable to find an interpreter for <path>` (exit status 2),
  both when invoked directly and when spawned via `subprocess.run()` from the Linux
  interpreter. The command classifier refuses PE exec before WSL interop runs.
- Therefore steps 1-6 of the plan cannot be executed from this shell; the plan itself
  says to stop when the platform is not `win32`.

**What was run (runnable evidence only):**

```
$ python tests/check_kill_roundtrip.py
check kill roundtrip: ok
```

exit 0, on the Linux interpreter. This proves the POSIX killpg branch of
`kill_tree()`; the Windows-only assertions in that file are platform-guarded and are
skipped on `linux` by design (05-VALIDATION.md row 1). It is **not** evidence about
the Windows Job Object path.

**What remains PENDING (recorded in 05-SPIKE-RESULT.md, not claimed):**

1. The escape rate of the accepted spawn window: **0 of 50 runs executed**; unmeasured,
   recorded as a number over the stated sample only in the sense that zero runs of the
   planned fifty happened. No escape rate is asserted.
2. Which Windows kill path runs by default (Job Object close) and what the forced
   fallback (`runner._FORCE_TASKKILL_FALLBACK`, runner.py:112) does: neither was
   exercised on this machine.
3. `runner.JobObjectExtendedLimitInformation` (A3): not confirmed or corrected against
   the real API; it stays an assumption with its loud failure mode intact.

## Task 2: the spike record

`05-SPIKE-RESULT.md` was written from the evidence above, following the
`01-SPIKE-RESULT.md` precedent in shape and voice while honestly being a blocker
report rather than a measurement:

- Environment block: machine (Windows 11 host), executor shell (WSL2, kernel
  6.18.35.2-microsoft-standard-WSL2), executor python (3.13.3, linux), the unreachable
  target interpreter path, date.
- Six-step table with literal outcomes — including the exact `run-detectors` error and
  exit status — not summaries.
- Escape rate stated as a count over a named sample ("0 of 50 runs executed"), with an
  explicit sentence that a zero observation would bound the rate rather than prove it
  and that here no observation exists.
- Both kill paths' dispositions recorded (neither exercised; POSIX path is the only
  one that ran).
- The enum constant recorded as unconfirmed.
- The residual gap in its own section (bpo-1677688 / thread handle / why the
  create-suspended sequence is unreachable / `_winapi` considered and declined) — a
  standing property, not an open defect.
- No safety claim of any kind; the document says only what a kill path did (here, was
  prevented from being measured) on a named machine on a named date.
- 05-RESEARCH.md's Windows section is explicitly NOT superseded (deferred until a real
  measurement exists).

The plan's doc-gate greps over the record pass: `(out of 50|of 50 runs)` x2,
`bpo-1677688|thread handle` x2, `JobObjectExtendedLimitInformation` x1,
and the claim-word grep (the two terms the 05-07 gate forbids) x0.

## Files Created

- `.planning/phases/05-check-item-type-code-editor/05-SPIKE-RESULT.md` — the blocker
  record with environment, six-step table, and the three PENDING deferrals.

## Deviations from Plan

- Task 1 could not be executed; the plan's own precondition stops the run. This is a
  recorded PENDING, not a deviation in behavior.
- 05-RESEARCH.md's Windows section was not marked superseded (the plan asked for it;
  superseding research with a blocker report would overclaim, so it is deferred).

## Issues Encountered

- **Environment blocker (this machine, this session):** WSL2 shell cannot spawn Windows
  processes; every PE binary fails at exec with `run-detectors: unable to find an
  interpreter` (exit 2), direct and via subprocess. The Windows interpreter exists
  (`C:\Users\wayba\AppData\Local\Programs\Python\Python313\python.exe`) but cannot be
  executed from this shell. The six Windows steps therefore require a Windows-capable
  shell (a Windows terminal, or WSL with working interop) before 05-VALIDATION.md rows
  1-2 and this plan's PENDING items can be closed.

## User Setup Required

**Yes — one human action closes this plan's PENDING items:** run the six steps of
plan 05-04 Task 1 on a Windows-capable shell on this machine (the steps and their
expected outputs are in 05-04-PLAN.md), paste the six results, and type "verified".
This is the same human checkpoint the plan always had; headless execution records it
PENDING rather than faking it.

## Next Phase Readiness

- 05-05 and 05-06 do not depend on 05-04 and can proceed.
- 05-07's automated tasks (render branches, schema, README, claim-word gate) do not
  depend on the spike measurement; its Task 3 human pass overlaps with the checkpoint
  above (both need a real browser/Windows session).

---
*Phase: 05-check-item-type-code-editor*
*Completed: 2026-08-11 (record written; Task 1 checkpoint PENDING human)*
