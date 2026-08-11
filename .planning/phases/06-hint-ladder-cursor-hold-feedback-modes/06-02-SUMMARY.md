---
phase: 06-hint-ladder-cursor-hold-feedback-modes
plan: 02
subsystem: surfaces
tags: [session-adapter, cli-hint, api-hint, renderer-meta, served-browser, ladder]

requires:
  - phase: 06-hint-ladder-cursor-hold-feedback-modes
    provides: teaching_transition, HINT_TIERS, hint events, v2 sessions (plan 06-01)
provides:
  - One session adapter (do_action/do_hint/do_report) used by CLI, daemon API, and served browser
  - itembank hint SESSION [--stumped] and POST /api/hint with identical structured payloads
  - Optional opaque renderer_meta (<=256 UTF-8 bytes), validated then discarded before policy/persistence
  - Served browser as a pure client of runtime actions: hold, reveal_tier, advance, defer_feedback, complete
  - Progressive fixed-tier ladder and honest stumped control on the served page
affects: [Phase 06.1 visual actions, Phase 7 selection, Phase 8 model hints, Phase 10 retention]

actuals:
  tokens: 1610
  tasks: 3
  commits: 4

tech-stack:
  added: []
  patterns:
    - One session adapter routes every surface; surfaces never reimplement policy
    - Renderer metadata is opaque, bounded, and discarded before any policy work

key-files:
  created: []
  modified:
    - surfaces/session.py
    - surfaces/cli.py
    - surfaces/daemon.py
    - surfaces/quiz.py
    - surfaces/quiz_page.py
    - tests/hint_roundtrip.py
    - tests/daemon_roundtrip.py
    - tests/serve_roundtrip.py
    - tests/evidence_roundtrip.py
    - tests/protocol_roundtrip.py
    - tests/agent_roundtrip.py

key-decisions:
  - "Every sitting action goes through session.do_action; the CLI, /api/*, and the served browser share one adapter, one runtime transition, and one evidence writer."
  - "renderer_meta is the ONLY Phase 6 renderer handoff: one opaque UTF-8 string capped at 256 bytes, discarded before policy, persistence, evidence, response, or logs; observation/canvas state belongs to Phase 06.1 and is refused by name."
  - "The served browser advances only on runtime-returned advance/complete; a practice hold keeps the card interactive for a materially different retry, and the stumped control reveals exactly one fixed tier."
  - "Diagnostic and exam responses carry no verdict (score stripped) until their release gates; the legacy /quiz/<stem>/answer route withholds the same way as /api/submit."

patterns-established:
  - "One persistence/scoring/policy path: handle_quiz_answer is a compatibility wrapper over session.do_action on the API session."
  - "Crash-window replays reconcile through evidence.attempt_number so a duplicate returns already_recorded without a second unlock."

requirements-completed: [TEACH-01, TEACH-02, TEACH-03, MODE-01, MODE-02, MODE-03, MODE-04, MODE-05, MODE-06]

coverage:
  - id: S1
    description: "CLI submit/hint/retry/report sitting over one session adapter: wrong holds, hint reveals one fixed tier, stumped uses the stumped path, correct retry advances, report carries tier-aware outcomes."
    requirement: TEACH-01
    verification:
      - kind: integration
        ref: "tests/hint_roundtrip.py#test_cli_hint_tracer"
        status: pass
    human_judgment: false
  - id: S2
    description: "POST /api/hint mirrors the CLI hint; /api/submit accepts the Phase 6 action envelope plus optional renderer_meta that is never persisted or passed to policy; authority-shaped fields and oversized metadata are refused."
    requirement: TEACH-02
    verification:
      - kind: integration
        ref: "tests/hint_roundtrip.py#test_api_hint_and_renderer_meta"
        status: pass
    human_judgment: false
  - id: S3
    description: "Served browser is a pure client: action-driven navigation, progressive fixed-tier ladder, stumped control, and no local scoring/key/tier/mode authority; diagnostic/exam pre-release responses leak no verdict or explanation."
    requirement: MODE-05
    verification:
      - kind: e2e
        ref: "tests/hint_roundtrip.py#test_served_browser_contract"
        status: pass
    human_judgment: false
  - id: S4
    description: "Regression suites updated to the Phase 6 hold/pending semantics (short answers stay pending; wrong practice answers hold) and remain green."
    requirement: MODE-03
    verification:
      - kind: unit
        ref: "tests/daemon_roundtrip.py, tests/serve_roundtrip.py, tests/evidence_roundtrip.py, tests/protocol_roundtrip.py, tests/agent_roundtrip.py"
        status: pass
    human_judgment: false

duration: 150min
completed: 2026-08-11
status: complete
---

# Phase 6 Plan 02: CLI, API and Browser Surfaces over the Hint Ladder

**One session adapter (do_action/do_hint/do_report) with CLI `hint`, `/api/hint`, opaque renderer metadata, and an action-driven served browser ladder with an honest stumped control**

## Performance

- **Duration:** 150 min
- **Started:** 2026-08-11T02:00:00Z (approx)
- **Completed:** 2026-08-11T04:30:00Z (approx)
- **Tasks:** 3
- **Files modified:** 11

## Accomplishments
- `surfaces/session.py` now has one `do_action` adapter: load/upgrade session + bank, reconcile teaching state from live evidence, invoke `teaching_transition`, append response/hint events through the one writer, apply only returned cursor/status/state changes, atomically persist.
- `itembank hint SESSION [--stumped]` and `POST /api/hint` return the identical structured fixed-tier payload (including stumped unlock path).
- `/api/submit` accepts the normalized Phase 6 action envelope (or the legacy answer form) plus an optional opaque `renderer_meta` string capped at 256 UTF-8 bytes, which is discarded before policy, persistence, evidence, response, or logs; observation/canvas-state and other authority-shaped fields are refused by name.
- The served browser (`quiz_page.py`) now renders runtime actions only: `hold` keeps the card interactive and offers a hint, `reveal_tier` appends the progressive ladder, `advance`/`complete` move on with the released explanation, `defer_feedback` acknowledges without a verdict; the stumped control reveals exactly one fixed tier.
- `handle_quiz_answer` was retired as a direct scoring path and is now a compatibility wrapper over `session.do_action` on the API session, preserving `cmd_serve`'s banner, mode flag, progress line, and attempt-file regeneration.

## Task Commits

1. **Task 1: TRACER - one CLI sitting** - adapter + CLI in `6c9e9eb`, tests in `96626af`
2. **Task 2: /api/hint + renderer_meta** - `dcbce87`/`b8fed76` (committed by the concurrent 07-06/03.2 thread alongside its own work) + `6c9e9eb`, tests `96626af`
3. **Task 3: Served browser ladder** - `6c9e9eb`, tests `96626af`

## Files Created/Modified
- `surfaces/session.py` - do_action/do_hint/do_report, renderer_meta gate, attempt-number reconciliation
- `surfaces/cli.py` - `hint` subcommand with `--stumped`
- `surfaces/daemon.py` - `/api/hint` route, action-envelope submit, renderer_meta validation, authority-field rejection, legacy-route wrapper
- `surfaces/quiz_page.py` - action-driven close flow, ladder renderer, stumped/hint controls
- Tests - `hint_roundtrip.py` (+3 06-02 tests), `daemon_roundtrip.py`, `serve_roundtrip.py`, `evidence_roundtrip.py`, `protocol_roundtrip.py`, `agent_roundtrip.py`

## Decisions Made
- One adapter for every surface: CLI, /api/*, and the served browser all call `session.do_action`, so no surface can diverge in scoring, cursor, tier, or disclosure.
- `renderer_meta` is the only Phase 6 renderer handoff and is discarded before any policy work; Phase 06.1 owns visual/canvas actions and observations.
- The browser never infers: it advances only on `advance`/`complete`, holds on `hold`, and renders exactly the returned ladder.
- Diagnostic/exam withhold verdicts at the API boundary too (score stripped), matching D-12/D-13.

## Deviations from Plan
- **Concurrent-thread interleaving:** a second Codex thread (Phases 7/13/03.2) worked the same workspace and committed portions of this plan's daemon/CLI surface work (e.g. `/api/hint`, `cmd_hint`) inside its own commits (`dcbce87`, `b8fed76`). This plan's own commits (`6c9e9eb`, `96626af`) carry the session adapter, served ladder, and the remaining wiring. All functionality is present and all suites pass.
- **Regression test updates (Rule 1):** the Phase 6 hold/pending semantics changed every session-driving test's assumptions (default diagnostic sessions never advanced; short answers stopped the cursor). Updated `daemon_roundtrip`, `serve_roundtrip`, `evidence_roundtrip`, `protocol_roundtrip`, and `agent_roundtrip` to drive practice sessions, follow the session's current item, handle holds with retries, and treat a pending short as the sitting's terminal state.
- **session_index resilience (Rule 2):** a future-versioned session file no longer kills the daemon's session index; it is skipped and the route returns 4xx.

**Total deviations:** 3 (1 concurrent-thread interleaving, 2 test/robustness)
**Impact on plan:** All necessary for coherent Phase 6 behavior; no scope creep.

## Issues Encountered
- The concurrent thread's history-aware Phase 7 selector made same-bank/same-seed sessions non-deterministic (evidence from the first sitting changes the second's selection); tests now use separate bank copies or follow the live session order.
- `tests/daemon_roundtrip.py`'s hostile-bank directory snapshot is flaky when other tests leak temp dirs into the same parent; the touched checks now clean up their workdirs.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- All Phase 6 plans complete; `python tests/hint_roundtrip.py` plus protocol/agent/serve/daemon/evidence/scoring/surface regressions pass.
- Phase 6 verification next: regression gate, verifier, phase completion. Phase 06.1 and the dependent chain (7-11) can proceed on the runtime contract.

---
*Phase: 06-hint-ladder-cursor-hold-feedback-modes*
*Completed: 2026-08-11*
