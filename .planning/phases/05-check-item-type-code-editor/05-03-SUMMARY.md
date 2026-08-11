---
phase: 05-check-item-type-code-editor
plan: 03
subsystem: api
tags: [check, runner, settings, daemon, security, evidence]

requires:
  - phase: 05-check-item-type-code-editor (05-01)
    provides: the runner gate on the browser submit path, runner.run_cases, score_response check branches

provides:
  - The check settings group (timeout_seconds, max_output_bytes, languages, allow_lan) in the published schema and shipped itembank.json
  - One shared runner gate on the agent submit path (D-14), consolidating the 05-01 inline gate
  - Settings-derived bounds on both submit paths
  - Network-bound execution refusal on both submit routes when check.allow_lan is false (D-09)
  - Unknown-language refusal with its own distinct locked sentence, contained by the daemon

affects: [05-05 editor surface, 05-06 page readout, 05-07 docs and rendering, Phase 6 action envelope]

actuals:
  tokens: 10134
  tasks: 3
  commits: 6

tech-stack:
  added: []
  patterns:
    - "One shared runner gate function (run_check_source) reached by both submit paths, never a second copy"
    - "Network-refusal decided live via settings.load_settings at submit time, never cached at bind"
    - "Bind mode pinned onto the handler class through serve_scoped's extra, defaulting closed (loopback)"

key-files:
  created: []
  modified:
    - schemas/settings.schema.json
    - itembank.json
    - surfaces/session.py
    - surfaces/quiz.py
    - surfaces/daemon.py
    - tests/check_roundtrip.py
    - tests/config_roundtrip.py

key-decisions:
  - "The shared check gate was hosted in surfaces/session.py (run_check_source) and imported into surfaces/quiz.py, rather than in quiz.py, so that the plan's own verify grep (run_cases present in surfaces/session.py) holds while still having exactly one implementation."
  - "THIS_PHASE was left untouched. It is already 7 (at or above 5), so the four check keys report as read by this phase; the plan's stale leave-at-2.1 criterion does not match the current watermark and no bump was needed."
  - "Unknown-language at run time is only reachable for a lint-clean bank via settings drift; because merge_over_defaults always keeps the shipped python entry, the test uses a [LANG: ruby] item started with --force against default settings."

requirements-completed: [CODE-01, CODE-02, CODE-04, CODE-05]

coverage:
  - id: C1
    description: "The check settings group (timeout_seconds default 5, max_output_bytes default 65536, languages default python map, allow_lan default false) is typed, bounded and defaulted in the published schema and appears in itembank config"
    requirement: CODE-01
    verification:
      - kind: integration
        ref: "python tests/config_roundtrip.py (test_check_group_contract, test_schema_names_every_project_key)"
        status: pass
      - kind: integration
        ref: "python itembank.py config | grep -c check.allow_lan  -> 1"
        status: pass
    human_judgment: false
  - id: C2
    description: "The check group is shipped in itembank.json and load_settings returns all four keys with python in languages"
    requirement: CODE-01
    verification:
      - kind: integration
        ref: "load_settings check-group assert (set == four keys, python present) -> check group ok"
        status: pass
    human_judgment: false
  - id: C3
    description: "The agent/CLI submit path runs the runner before scoring, through one shared helper, and produces evidence identical to the browser path (D-14, T-5-12)"
    requirement: CODE-02
    verification:
      - kind: integration
        ref: "python tests/check_roundtrip.py (check_agent_path, check_cross_path)"
        status: pass
    human_judgment: false
  - id: C4
    description: "The runner deadline and output cap come from settings, not a constant read at point of use"
    requirement: CODE-02
    verification:
      - kind: integration
        ref: "python tests/check_roundtrip.py check_agent_path timeout_seconds=1 (under 5s)"
        status: pass
    human_judgment: false
  - id: C5
    description: "Neither submit path can reach score_response for a check item without the runner having run first (one shared implementation)"
    requirement: CODE-04
    verification:
      - kind: integration
        ref: "python tests/scoring_roundtrip.py (no second scorer function introduced)"
        status: pass
    human_judgment: false
  - id: C6
    description: "Code execution is refused by default on both submit routes when the daemon is bound to all interfaces and check.allow_lan is false, writing no evidence (D-09, T-5-07)"
    requirement: CODE-04
    verification:
      - kind: integration
        ref: "python tests/check_roundtrip.py check_network_refusal"
        status: pass
    human_judgment: false
  - id: C7
    description: "The unknown-language case returns its own distinct locked sentence and does not crash the daemon (T-5-08)"
    requirement: CODE-05
    verification:
      - kind: integration
        ref: "python tests/check_roundtrip.py check_network_refusal + check_agent_path unknown-language"
        status: pass
    human_judgment: false

duration: 75min
completed: 2026-08-11
status: complete
---

# Phase 05-03: Check settings group, agent-path gate, and network-bound execution refusal

**Both submit paths now run a learner's check code through one shared settings-driven gate before scoring, and execution is refused by default on both routes whenever the daemon is reachable from the network.**

## Performance

- **Duration:** ~75 min
- **Started:** 2026-08-11
- **Completed:** 2026-08-11
- **Tasks:** 3
- **Files modified:** 7

## Accomplishments

- Added the four-key check settings group (typed, ranged, defaulted) to the schema and shipped itembank.json; itembank config prints them and config set rejects bad values with published dotted codes.
- Consolidated the 05-01 inline check gate (which was already present in do_action) into one shared helper, run_check_source in surfaces/session.py, imported by surfaces/quiz.py record_answer, and made both paths read bounds from settings.
- Made D-09 real: DaemonHandler.lan is pinned through serve_scoped's extra, both submit handlers gate before the runner, and the locked LAN-refusal sentence is returned with no evidence written; the unknown-language case returns its own distinct sentence and does not crash the daemon.

## Task Commits

1. **Task 1: The check settings group** - e077e67 (feat)
2. **Task 2: Gate the agent submit path on the runner** - baaa2d3 (test), a57fd59 (feat)
3. **Task 3: Refuse network-bound execution** - e310daa (test), 13bd69f (feat)

**Plan metadata:** the SUMMARY commit (docs) closes the plan.

## Files Created/Modified

- schemas/settings.schema.json - Added the check group with x-itembank-phase 5.
- itembank.json - Shipped defaults for the check group.
- surfaces/session.py - Added run_check_source shared helper and the unknown-language SystemExit; wired do_action to it.
- surfaces/quiz.py - record_answer now uses the shared helper with settings-derived bounds.
- surfaces/daemon.py - Added LAN_REFUSAL_COPY, DaemonHandler.lan, _refuse_check_execution, gated both submit handlers, contained SystemExit in handle_quiz_answer, and pinned the bind mode in serve_scoped and cmd_daemon.
- tests/check_roundtrip.py - Agent-path, cross-path, and network-refusal tests.
- tests/config_roundtrip.py - Check-group contract test.

## Decisions Made

- Hosted the one shared gate in surfaces/session.py (not quiz.py) so the plan's run_cases-in-session.py verify holds while keeping a single implementation; this is a recorded deviation.
- Left THIS_PHASE untouched (already 7).
- Used a --force-started [LANG: ruby] item for the run-time unknown-language case because the shipped python allowlist always survives the settings merge.

## Deviations from Plan

### Auto-fixed Issues

**1. Current-state mismatch - the plan text assumed a pre-Phase-6 session.py**
- **Found during:** Task 2
- **Issue:** The plan said do_submit called score_response() directly at line 122 and needed a new gate; in the current branch do_submit delegates to do_action and plan 05-01 already added an inline gate there (with runner DEFAULT bounds). The fix was to consolidate that existing gate into the shared run_check_source helper (per the plan's explicit intent) rather than adding a third copy, and to switch it to settings-derived bounds.

**2. Shared-helper host - placed in session.py instead of quiz.py**
- **Found during:** Task 2
- **Issue:** The plan's verify section requires run_cases to appear in surfaces/session.py. Hosting the helper in quiz.py and importing it into session.py would have left session.py with zero run_cases references and failed that grep. Hosted in session.py and imported into quiz.py instead; still exactly one shared implementation, no import cycle.

**3. Unknown-language reachability**
- **Found during:** Task 2
- **Issue:** merge_over_defaults always keeps the shipped python entry in check.languages, and lint only allows python, so a run-time unknown language is only reachable for a lint-clean bank by settings drift. The test authors a [LANG: ruby] item and starts it with --force against default settings so the runtime allowlist miss is real.

**4. Evidence-size measurement in the network-refusal test**
- **Found during:** Task 3
- **Issue:** /api/start appends a selection evidence event, so the evidence log grows on session creation even when a refused submit writes nothing. The test now measures the log size after the session is started and asserts it is unchanged across the refused submit.

**5. daemon_roundtrip flake**
- **Found during:** full-suite verification
- **Issue:** tests/daemon_roundtrip.py failed once in a heavy batch run on the hostile-bank-field-on-api-start assertion. It passes in isolation and when run immediately after check_roundtrip.py; no /api/start or bank-field code was touched by this plan. Recorded as an environment flake, not a regression.
