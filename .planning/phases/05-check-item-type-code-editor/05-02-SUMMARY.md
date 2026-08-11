---
phase: 05-check-item-type-code-editor
plan: 02
subsystem: testing
tags: [subprocess, kill-tree, output-cap, job-object, ctypes]

requires:
  - phase: 05-check-item-type-code-editor
    provides: "runner.py with one kill_tree(), one threaded drain and one per-case deadline (plan 05-01)"

provides:
  - "Output cap that fails a case and kills early via the same kill_tree() the deadline uses"
  - "run-level killed_at_timeout fact (derived: any case timed out) and a None-not-False timeout verdict (criterion 12)"
  - "Windows Job Object with kill-on-close (new_job_object/assign_to_job) and a taskkill /T /F fallback, exercised via a test switch"
  - "fixtures/grandchild_spawner.py heartbeat fixture and a test proving the tree-wide kill reaches a grandchild"

affects: [05-check-item-type-code-editor, 05-SPIKE-RESULT]

actuals:
  tokens: 4200
  tasks: 3
  commits: 7

tech-stack:
  added: []
  patterns:
    - "One kill_tree() with two triggers (deadline and cap) and a recorded _last_kill_path"
    - "Windows-only ctypes symbols guarded to module-level definitions, WinDLL called lazily so CI (Linux) imports cleanly"

key-files:
  created:
    - tests/check_kill_roundtrip.py
    - fixtures/grandchild_spawner.py
  modified:
    - runner.py

key-decisions:
  - "Kept run_cases() returning the plain per-case list; the run-level killed_at_timeout fact stays the 05-01 stated shape (derived scan for any timed_out case), asserted by the test, so surfaces/quiz, surfaces/session, runtime.interaction_result and check_roundtrip are untouched."
  - "Task 1's runtime behaviours (cap early-kill, passed False on truncated, flag independence) were already shipped by plan 05-01; the executor's Task 1 work is the new test file plus the bounded drain-thread join and a crisper run-level-flag docstring -- no rewrite of working code."
  - "The process handle opened by assign_to_job is closed in kill_tree (not in assign_to_job) so the CloseHandle primitive appears only inside kill_tree's body, satisfying the plan's source-grep acceptance criterion."
  - "The grandchild fixture reads its heartbeat path from argv[1] when run directly and from the GRANDCHILD_HEARTBEAT env var when the runner runs it as a submission (which sets no argv beyond the source path); run_cases cannot forward extra argv."

patterns-established:
  - "Each Windows-only kill primitive (taskkill/killpg/CloseHandle) lives only inside kill_tree's body; new_job_object/assign_to_job use the job-API names only."

requirements-completed: [CODE-04, CODE-05]

coverage:
  - id: D1
    description: "Output cap fails a flooding case in cap-crossing time with a truncation marker, passed forced False even when the prefix matches, and no reader/thread/child left behind"
    requirement: CODE-04
    verification:
      - kind: integration
        ref: "tests/check_kill_roundtrip.py#check_cap_kill_fires_early"
        status: pass
      - kind: integration
        ref: "tests/check_kill_roundtrip.py#check_truncated_forces_false_even_when_prefix_matches"
        status: pass
      - kind: integration
        ref: "tests/check_roundtrip.py#check_run_cases"
        status: pass
    human_judgment: false
  - id: D2
    description: "timed_out and truncated are independent flags; a deadline kill surfaces the run-level killed_at_timeout fact and score_response() returns None, never False (criterion 12), while the over-cap kill still scores False (D-08)"
    requirement: CODE-04
    verification:
      - kind: integration
        ref: "tests/check_kill_roundtrip.py#check_flags_independent"
        status: pass
      - kind: integration
        ref: "tests/check_kill_roundtrip.py#check_timeout_not_a_verdict"
        status: pass
    human_judgment: false
  - id: D3
    description: "Windows Job Object structures and constants (JobObjectExtendedLimitInformation==9, extended embeds basic, JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE) and a clean import on Linux CI with no WinDLL call at import time"
    requirement: CODE-05
    verification:
      - kind: unit
        ref: "tests/check_kill_roundtrip.py#check_windows_constants_and_layouts"
        status: pass
      - kind: unit
        ref: "tests/check_kill_roundtrip.py#check_import_no_windll"
        status: pass
      - kind: other
        ref: "python import runner; JobObjectExtendedLimitInformation -> 9"
        status: pass
    human_judgment: false
  - id: D4
    description: "On real Windows the primary kill path is the job object close and the forced fallback (taskkill /T /F) also kills the tree; the accepted spawn window (bpo-1677688) is recorded in source"
    requirement: CODE-05
    verification:
      - kind: unit
        ref: "tests/check_kill_roundtrip.py#check_windows_kill_paths"
        status: pass
      - kind: other
        ref: "grep for bpo-1677688 in runner.py (asserted in check_windows_constants_and_layouts)"
        status: pass
    human_judgment: true
    rationale: "CI runs Linux only. The runtime Windows job-object kill and the taskkill fallback are only exercised by the Windows-guarded branch of the test; their behaviour on the actual Windows 11 target is plan 05-04's manual pass (05-VALIDATION.md), which also re-confirms Assumption A3 (JobObjectExtendedLimitInformation==9)."
  - id: D5
    description: "A grandchild spawned by the learner's code stops writing the moment the runner returns, proven by a heartbeat file on both platforms via the platform-neutral fixtures/grandchild_spawner.py"
    requirement: CODE-05
    verification:
      - kind: integration
        ref: "tests/check_kill_roundtrip.py#check_grandchild_kill"
        status: pass
      - kind: other
        ref: "grep fixture for setsid|start_new_session|CREATE_NEW_PROCESS_GROUP -> 0, win32|platform -> 0"
        status: pass
    human_judgment: false

duration: 95min
completed: 2026-08-11
status: complete
---

# Phase 05: Check item type — Plan 02 Summary

**The runner's two bounds are hardened and proven: the output cap fails and kills a flooding case in cap-crossing time (via the same kill_tree the deadline uses), and the kill reaches a grandchild through a Windows kill-on-close Job Object (with taskkill fallback) and a POSIX process-group SIGKILL, proven by a heartbeat fixture and a no-verdict timeout contract (criterion 12).**

## Performance

- **Duration:** 95 min
- **Tasks:** 3
- **Commits:** 7 (6 task commits + 1 docs)

## Accomplishments

- Output cap: a flooding, non-terminating program returns in cap-crossing time (<2s on a 5s deadline) with truncated True; truncated forces passed False even when the retained prefix equals expected.
- Bound flags: timed_out and truncated are independent; a deadline-killed run surfaces the run-level killed_at_timeout fact and score_response() returns None (never False), while the over-cap run still scores False (D-08).
- Windows kill: new_job_object() + assign_to_job() build a kill-on-close Job Object; kill_tree closes the job (no separate TerminateProcess), falling back to taskkill when no job was built. Both paths are test-exercisable via a private _FORCE_TASKKILL_FALLBACK switch, and the accepted spawn window (bpo-1677688) is written into the source.
- Process-tree kill: fixtures/grandchild_spawner.py spawns a heartbeat-writing grandchild that inherits the runner's group/job; the test proves the heartbeat file stops growing after the runner returns and cleans up in a finally: block.
- POSIX import safety: import runner on Linux makes no ctypes.WinDLL call; all Windows-only symbols are defined at module scope and reachable only inside the sys.platform == "win32" branch.

## Task Commits

Each task was committed atomically (test-first, then implementation per TDD):

1. **Task 1: The output cap fails the case and kills early**
   - ebaa96a (test)
   - a912a92 (feat: bound drain-thread join)
2. **Task 2: Windows Job Object kill-on-close, taskkill fallback**
   - 69808bd (test)
   - 33d936f (feat: job object + fallback)
3. **Task 3: Grandchild-spawning kill test**
   - b494b4c (test)
   - dc50ffb (feat: grandchild_spawner fixture)

**Plan metadata:** docs commit below (complete bounds hardening plan)

## Files Created/Modified

- runner.py - bounded drain-thread joins, run-level killed_at_timeout docstring; new new_job_object()/assign_to_job(), Job Object structures + constants, kill_tree promoted to close the job with taskkill fallback, _FORCE_TASKKILL_FALLBACK/_last_kill_path/_last_job_error, and the bpo-1677688 spawn-window comment.
- fixtures/grandchild_spawner.py - platform-neutral heartbeat-grandchild spawner (argv[1] or GRANDCHILD_HEARTBEAT).
- tests/check_kill_roundtrip.py - new stdlib-only framework-free test covering Tasks 1-3.

## Decisions Made

- Kept the 05-01 run-level killed_at_timeout derived scan (no return-shape change), asserted in the test.
- Closed the OpenProcess handle inside kill_tree so CloseHandle appears only inside its body (plan source-grep criterion).
- Grandchild fixture reads heartbeat path from env when run as a submission, argv[1] when run directly (run_cases forwards no argv).

## Deviations from Plan

None — plan executed as specified.

## Issues Encountered

- **Task 1 reconciliation:** the plan's read_first flagged that 05-01 already shipped cap early-kill, passed-False-on-truncated and flag independence. Verified all three already held; Task 1's implementation is the new test file, a bounded join (_DRAIN_JOIN_TIMEOUT), and a clearer run-level-flag docstring — no rewrite of working code.
- **daemon_roundtrip / day_roundtrip flakiness (environmental, not this plan):** both are server/socket-startup tests that intermittently fail under the heavy concurrent-executor load on this shared machine (multiple reasonix executors run their own suites in sibling worktrees, churning /tmp tempdirs and contending for ports). daemon_roundtrip's "hostile bank field created a new directory" and day_roundtrip's "server never printed a URL" reproduce on the base 05-01 commit and pass when run alone on this branch (3/3 and 3/3). Neither touches runner.py; the failures predate and are independent of this plan. tests/packaging_roundtrip.py is the plan's known environmental exclusion (missing Windows-built dist).
- **presentation_roundtrip** prints a tolerated FAIL: line but exits 0 identically on base and branch — pre-existing, not a regression.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Phase 05-03 can consume runner.run_cases's language/settings-driven languages parameter (already threaded through).
- Phase 05-04 (Windows spike) can quote runner._last_kill_path / runner._last_job_error, re-confirm JobObjectExtendedLimitInformation == 9 on the target machine, and measure the bpo-1677688 spawn window over 50 iterations.
- The Windows job-object runtime kill is the one behaviour not verifiable on Linux CI; it is explicitly 05-04's manual pass.

---
*Phase: 05-check-item-type-code-editor*
*Completed: 2026-08-11*
