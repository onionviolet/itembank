---
phase: 08-model-adapter-interface-tier-gate-enforcement
plan: 05
subsystem: api
tags: [model-adapter, tier-gate, daemon-routes, surface-parity, agent-assist, structural-lock, rubric-checklist, uat, no-leak, ui]

# Dependency graph
requires:
  - phase: 08-model-adapter-interface-tier-gate-enforcement
    provides: tier-gate (08-01), model-adapter boundary (08-02), model_interaction/mark_proposal evidence events (08-03), typed do_hint/do_rubric_review surfaces (08-04)
provides:
  - "Identifier-safe POST /api/hint and POST /api/rubric-review routes relayed from session.do_hint/do_rubric_review, with API_FORBIDDEN_FIELDS refusing tier/profile/facts/candidate/proposal/marker/verdict 400 before any handler (D-09)"
  - "One SURFACE_PARITY map (route, CLI command, reserved MCP tool name) covering every API_ROUTES entry per Extensibility Rule 9(a), including the two new routes (reserved tool names hint, rubric_review)"
  - "The AgentAssist learner surface in surfaces/quiz_page.py: assist slot after session details in DOM order, native details/summary 'Help and evidence' collapsed and opt-in, 'Get optional guidance' control, one bounded status line ('Preparing optional guidance…'), 'Generated support' container with the generated disclosure sentence, exact unavailable/policy-drop copy, and the requested/thinking/pass/drop/unavailable/cancelled/retry lifecycle states — no chat box or typing animation"
  - "The structural lock (D-26): a locked tier renders as a labeled lock with the unlock condition stated in UI-SPEC copy, never as model voice"
  - "The pending rubric checklist: one semantic row per point with 'Pending rubric suggestion — human review required' and the pending token only — no number/fraction/check/cross glyph and no accept control of any kind in the browser DOM; Record human mark stays CLI-only (08-04)"
  - "The blocking human UAT evidence: 08-05-UAT-EVIDENCE.md records verdict PASS (user-approved at the orchestrator checkpoint), environment, the 8-item how-to-verify checklist, and revision notes (none required)"
affects: [08-06 phase release gate, MCP surface when V2-INT-02 lands, future learner-facing model surfaces]

# Actuals (#2632) — chars/4 over the realized diff of this plan's seven code/test files.
actuals:
  tokens: 17245
  tasks: 3
  commits: 5

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Identifier-safe route relay: api_read_json -> session_index resolution -> two-clause containment (SystemExit -> 400, Exception -> 500) -> serialize only the typed payload, matching handle_api_submit exactly; authority-shaped fields refused by API_FORBIDDEN_FIELDS before any handler runs"
    - "Single SURFACE_PARITY map (route, CLI command, MCP tool name) as the parity source of truth; the parity test fails on a route without a CLI or tool name (Extensibility Rule 9(a))"
    - "Learner assist as plain chrome: native details/summary, exact UI-SPEC copy constants, one bounded status line announced once via a polite aria-live region, lifecycle states rendered from typed payloads only, assist payload threaded only in daemon-served mode (offline build ships none)"
    - "Flatten() no-leak discipline: scans over page HTML, all JSON payloads, and SERVED_JS assert private fields never cross the API/DOM boundary"

key-files:
  created:
    - .planning/phases/08-model-adapter-interface-tier-gate-enforcement/08-05-UAT-EVIDENCE.md
  modified:
    - surfaces/daemon.py
    - surfaces/quiz.py
    - surfaces/quiz_page.py
    - tests/model_ui_roundtrip.py
    - tests/daemon_roundtrip.py
    - tests/hint_roundtrip.py
    - tests/surface_roundtrip.py

key-decisions:
  - "The daemon relays only typed runtime payloads: both new routes resolve the session through session_index, wrap session.do_hint/do_rubric_review in the house SystemExit->400/Exception->500 containment, and never accept a caller-supplied tier, profile, key, or marker"
  - "API_FORBIDDEN_FIELDS now also refuses tier, profile, facts, candidate, proposal, marker, and verdict with 400 before any handler, so a client cannot smuggle authority fields onto the wire (D-09)"
  - "SURFACE_PARITY is one map, not per-surface maps: every API_ROUTES entry has its CLI command and reserved MCP tool name in one tuple (route, cli_command, mcp_tool_name); the parity test keeps the third-surface teeth (Extensibility Rule 9(a), amended 2026-08-10)"
  - "The assist ships as native plain chrome with the exact 08-UI-SPEC Copywriting Contract strings verbatim; a locked tier renders as a labeled structural lock with the unlock condition, and the model has no typographic voice anywhere in the DOM"
  - "Pending rubric suggestions render as pending tokens per point only; the browser exposes no accepted-mark or auto-accept control of any kind — Record human mark exists only in the trusted local reviewer CLI (08-04)"

patterns-established:
  - "Relay-don't-decide: surfaces/quiz_page.py renders only typed payloads from /api/hint and /api/rubric-review; reason codes, tier numbers, provider/profile detail never reach the DOM"
  - "One-bounded-status lifecycle: exactly one polite status transition ('Preparing optional guidance…') precedes a typed outcome; announced once via a polite aria-live region; reduced motion disables nonessential animation"
  - "Pending-only rubric presentation: per-point rows carry the pending token and the exact heading; acceptance stays a human mark_event in the CLI"

requirements-completed: [TEACH-04, TEACH-05, TEACH-06, TEACH-07, TEACH-08, TEACH-09, MODEL-03, MODEL-05]

# Coverage metadata (#1602)
coverage:
  - id: D1
    description: "Identifier-safe POST /api/hint and POST /api/rubric-review: typed payloads relayed from session.do_hint/do_rubric_review, API_FORBIDDEN_FIELDS refusal of tier/profile/facts/candidate/proposal/marker/verdict (400 before any handler), SystemExit->400/Exception->500 containment matching handle_api_submit, and one SURFACE_PARITY map covering every API route with a CLI twin and reserved MCP tool name (Extensibility Rule 9(a))"
    requirement: TEACH-05
    verification:
      - kind: unit
        ref: "tests/daemon_roundtrip.py#check_api_assist_routes"
        status: pass
      - kind: unit
        ref: "tests/daemon_roundtrip.py#check_api_forged_fields"
        status: pass
      - kind: unit
        ref: "tests/daemon_roundtrip.py#check_api_reject_path_fields"
        status: pass
      - kind: unit
        ref: "tests/daemon_roundtrip.py#check_surface_parity"
        status: pass
      - kind: unit
        ref: "tests/hint_roundtrip.py#test_api_hint_and_renderer_meta"
        status: pass
    human_judgment: false
  - id: D2
    description: "AgentAssist learner surface: assist region after the session details in DOM order, native details/summary 'Help and evidence' collapsed and opt-in, 'Get optional guidance' control, exactly one bounded status transition ('Preparing optional guidance…') before a typed outcome, 'Generated support' container with the generated disclosure sentence and no correctness claim, exact unavailable/policy-drop copy, and the requested/thinking/pass/drop/unavailable/cancelled/retry lifecycle — never a chat box or typing animation"
    requirement: TEACH-06
    verification:
      - kind: unit
        ref: "tests/model_ui_roundtrip.py#check_dom_order_and_copy"
        status: pass
      - kind: unit
        ref: "tests/model_ui_roundtrip.py#check_lifecycle_and_lock"
        status: pass
      - kind: unit
        ref: "tests/model_ui_roundtrip.py#check_assist_wire"
        status: pass
    human_judgment: false
  - id: D3
    description: "Structural lock (D-26): a locked tier renders as a labeled structural lock with the unlock condition stated using UI-SPEC copy, never as model voice or provider text"
    requirement: TEACH-05
    verification:
      - kind: unit
        ref: "tests/model_ui_roundtrip.py#check_lifecycle_and_lock"
        status: pass
      - kind: unit
        ref: "tests/model_ui_roundtrip.py#check_no_leak"
        status: pass
    human_judgment: false
  - id: D4
    description: "Pending rubric checklist: one semantic row per point showing 'Pending rubric suggestion — human review required' with the pending token only — no number, fraction, check, or cross glyph; no accepted-mark or auto-accept control exists anywhere in the browser DOM, and Record human mark remains the trusted local reviewer CLI path (itembank mark --proposal) whose result the report reflects"
    requirement: TEACH-09
    verification:
      - kind: unit
        ref: "tests/model_ui_roundtrip.py#check_pending_rubric_rows"
        status: pass
      - kind: unit
        ref: "tests/model_ui_roundtrip.py#check_no_leak"
        status: pass
      - kind: unit
        ref: "tests/model_surface_roundtrip.py#test_cmd_mark_proposal_human_accept"
        status: pass
    human_judgment: false
  - id: D5
    description: "No-leak API/DOM boundary and responsive/accessibility behaviour: flatten() scans over page HTML, all JSON payloads, and SERVED_JS assert no key, tier number, fact text, profile name, backend class, gate reason, or dropped candidate phrase appears; 320px/200% zoom shows no horizontal scroll; reduced motion disables nonessential animation; lifecycle status changes announce once via a polite aria-live region; the offline build page stays unchanged"
    requirement: MODEL-03
    verification:
      - kind: unit
        ref: "tests/model_ui_roundtrip.py#check_no_leak"
        status: pass
      - kind: unit
        ref: "tests/model_ui_roundtrip.py#check_responsive_and_motion"
        status: pass
      - kind: unit
        ref: "python tests/serve_roundtrip.py"
        status: pass
      - kind: unit
        ref: "tests/daemon_roundtrip.py#check_answer_scoring"
        status: pass
    human_judgment: false
  - id: D6
    description: "Blocking human UAT (Task 3): verdict PASS recorded in 08-05-UAT-EVIDENCE.md with the environment (Windows, Python 3.13.3), the 8-item how-to-verify checklist, and revision notes (none required), backed by the passing automated suites and the user's explicit approval at the orchestrator checkpoint"
    verification: []
    human_judgment: true
    rationale: "The blocking gate is a human decision by definition (checkpoint:human-verify, gate=blocking): the user approved at the orchestrator checkpoint. The automated suites prove the DOM/JSON/JS boundary, lifecycle wiring, exact copy, responsive, and no-leak assertions; live-page observation and visual adequacy are the human's call, recorded in the UAT evidence file."

# Metrics
duration: ~35min
completed: 2026-08-11
status: complete
---

# Phase 08 Plan 05: Identifier-Safe Daemon Assist Routes, AgentAssist Learner Surface, and the Blocking Human UAT Summary

**The learner-facing boundary ships: /api/hint and /api/rubric-review relay only typed payloads behind an authority-field 400 wall and one SURFACE_PARITY map, the quiz page renders runtime-gated AgentAssist as plain chrome (one bounded status line, Generated support disclosure, labeled structural lock, pending rubric rows with no accept path), and the blocking human UAT recorded a user-approved PASS.**

## Performance

- **Duration:** ~35 min
- **Started:** 2026-08-11T01:50:00Z
- **Completed:** 2026-08-11T02:30:00Z
- **Tasks:** 3
- **Files modified:** 7 code/test files (surfaces/daemon.py, surfaces/quiz.py, surfaces/quiz_page.py, tests/model_ui_roundtrip.py, tests/daemon_roundtrip.py, tests/hint_roundtrip.py, tests/surface_roundtrip.py) plus the UAT-EVIDENCE.md and this SUMMARY.md

## Accomplishments

- `surfaces/daemon.py` exposes `POST /api/hint` and `POST /api/rubric-review` through identifier-safe handlers: `api_read_json` first, session resolution strictly through `session_index` (unknown session → 400 with no evidence write), `session.do_hint`/`do_rubric_review` wrapped in the house two-clause containment (SystemExit → 400, Exception → 500), and only the returned typed payload serialized — the exact `handle_api_submit` shape (D-08/D-09).
- `API_FORBIDDEN_FIELDS` is extended with `tier`, `profile`, `facts`, `candidate`, `proposal`, `marker`, and `verdict`, so a client can never smuggle authority fields onto the wire: a body naming any of them is refused 400 before the handler runs (D-09, T-08-41).
- One `SURFACE_PARITY` map now covers every `API_ROUTES` entry as `(route, cli_command, mcp_tool_name)` — the two new routes carry CLI twins (`hint`, `rubric-review`) and reserved MCP tool names (`hint`, `rubric_review`) — and the parity test fails on any route without a CLI or tool name (Extensibility Rule 9(a), amended 2026-08-10).
- `surfaces/quiz_page.py` ships `AGENT_ASSIST_HTML` and `ASSIST_JS` with the assist slot placed after the session details region in the DOM order 08-UI-SPEC locks: native `details/summary` "Help and evidence" collapsed and opt-in, a "Get optional guidance" control, exactly one bounded status line ("Preparing optional guidance…"), a "Generated support" container with the generated disclosure sentence, the exact unavailable/policy-drop copy, and the requested/thinking/pass/drop/unavailable/cancelled/retry lifecycle — no chat box, no typing animation, announce-once via a polite aria-live region.
- The structural lock (D-26) renders as a labeled lock with the unlock condition stated in UI-SPEC copy and no model voice; the pending rubric checklist renders one semantic row per point with "Pending rubric suggestion — human review required" and the pending token only — no number/fraction/check/cross glyph and no accepted-mark or auto-accept control anywhere in the browser DOM (Record human mark stays the trusted local CLI, T-08-43).
- The no-leak boundary is proven by flatten() scans over the page HTML, all JSON payloads, and SERVED_JS asserting no key, tier number, fact text, profile name, backend class, gate reason, or dropped candidate phrase appears anywhere (D-09, T-08-40); the offline build page stays unchanged and the 320px/200% / reduced-motion / announce-once behaviour holds.
- The blocking human UAT (Task 3) recorded verdict **PASS** in `08-05-UAT-EVIDENCE.md`: the user approved at the orchestrator checkpoint, with the environment (Windows, Python 3.13.3), the 8-item how-to-verify checklist each marked satisfied/verified, and revision notes stating none required.

## Task Commits

Each task was committed atomically, tests first:

| Task | Commit(s) | Type |
|------|-----------|------|
| Task 1: Tracer — identifier-safe `/api/hint` and `/api/rubric-review` routes plus SURFACE_PARITY | `7d1336c` (feat), `f450eaa` (test) | feat / test |
| Task 2: AgentAssist lifecycle, structural lock, and pending rubric checklist in the quiz page | `bddd31f` (feat), `56a8922` (test) | feat / test |
| Task 3: Blocking human UAT — learner surfaces over the daemon, with durable evidence | approved at orchestrator checkpoint; evidence in `08-05-UAT-EVIDENCE.md` | human-verify |

**Plan metadata:** `docs(08-05): complete identifier-safe assist routes and AgentAssist learner surface plan` (final commit — includes SUMMARY.md, UAT-EVIDENCE.md, STATE.md, ROADMAP.md)

## Files Created/Modified

- `surfaces/daemon.py` - `handle_api_hint` / `handle_api_rubric_review` routes in API_ROUTES, ROUTE_CLI entries, SURFACE_PARITY map, API_FORBIDDEN_FIELDS extension
- `surfaces/quiz.py` - `page_for` threads the assist payload in daemon-served mode only (offline/build mode ships no assist)
- `surfaces/quiz_page.py` - `AGENT_ASSIST_HTML`, `ASSIST_JS`, assist slot in TEMPLATE, lifecycle/status markup, pending rubric checklist markup, exact UI-SPEC copy constants, structural lock markup
- `tests/model_ui_roundtrip.py` - six assist checks (DOM order + copy, lifecycle + lock, pending rubric rows, no-leak, responsive + motion, assist wire)
- `tests/daemon_roundtrip.py` - 62 checks including assist-route containment, forbidden-field 400s, and SURFACE_PARITY assertions
- `tests/hint_roundtrip.py` - Phase 6 `/api/hint` tracer updated to the 08-05 rewired model-hint payload (deviation, see below)
- `tests/surface_roundtrip.py` - quiz-page script-slot baseline 2→3 (deviation, see below)
- `.planning/phases/08-model-adapter-interface-tier-gate-enforcement/08-05-UAT-EVIDENCE.md` - blocking human UAT evidence (verdict PASS)

## Decisions Made

- The daemon relays only typed runtime payloads and never accepts a caller-supplied tier, profile, key, or marker; both new routes follow `handle_api_submit` exactly, so there is one house pattern for `/api/*` session routes.
- Authority-shaped fields are refused by `API_FORBIDDEN_FIELDS` before any handler runs — a 400, not a filter.
- SURFACE_PARITY is one map with three columns (route, CLI command, MCP tool name); the parity test keeps the third-surface teeth for the day a dispatcher exists.
- The learner assist is plain chrome with 08-UI-SPEC copy verbatim: the structural lock labels its unlock condition, the model has no typographic voice, and the browser exposes no accept path — pending rubric rows carry the pending token only.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Companion test files `tests/hint_roundtrip.py` and `tests/surface_roundtrip.py` updated by the executor**
- **Found during:** Task 1 (route rewire) and Task 2 (quiz-page script slots)
- **Issue:** The plan's `files_modified` lists five code/test files, but two existing suites were invalidated by its own required behaviour: rewiring `/api/hint` from the Phase 6 tier reveal to the model-orchestrated typed payload breaks `tests/hint_roundtrip.py::test_api_hint_and_renderer_meta` (it asserted `reveal_tier`), and adding the assist script slot to the shared quiz template changes `tests/surface_roundtrip.py::check_quiz_script_safety`'s benign baseline from exactly two `<script>` tags to exactly three. The plan's `<verify>` requires those suites to stay green.
- **Fix:** `test_api_hint_and_renderer_meta` now asserts the typed model-hint payload (status `unavailable`, `interaction_id` minted, `authored.available` true, no `reason` code) and the `test_cli_hint_tracer` docstring reflects the rewire; `check_quiz_script_safety` expects exactly three script slots (offline + served + assist) with inactive slots emptied.
- **Files modified:** tests/hint_roundtrip.py, tests/surface_roundtrip.py
- **Verification:** `python tests/hint_roundtrip.py`, `python tests/surface_roundtrip.py` green
- **Committed in:** `f450eaa`, `56a8922` (part of the task commits)

**2. [Verification deviation - the plan's `schema_validate.py --all` is not this repo's CLI]**
- **Found during:** final verification (closing 08-05; same condition recorded by 08-04)
- **Issue:** `python schema_validate.py --all` is not a CLI this repo ships; `schema_validate.py` is a two-argument validator. The 08-05 `<verification>` list itself does not name it, but the phase-standard contract check is re-recorded here for continuity.
- **Fix:** Ran `python itembank.py schema --all` (parses, all contracts), `python tests/protocol_roundtrip.py` (green), and `test_schema_uses_supported_keywords_only()` from `tests/model_gate_roundtrip.py` (green), plus the three plan-verification suites.
- **Verification:** `python itembank.py schema --all`, `python tests/protocol_roundtrip.py`, `python tests/model_gate_roundtrip.py`

**3. [UAT evidence basis] The blocking human checkpoint was approved by the user at the orchestrator checkpoint**
- **Found during:** Task 3 (blocking human UAT)
- **Issue:** Task 3's `<resume-signal>` expects the verdict to be recorded during an interactive session; the user approved ("approved — proceed to 08-05 closure") at the orchestrator checkpoint presentation.
- **Fix:** The closure recorded verdict PASS, the environment (Windows, Python 3.13.3), and the 8-item how-to-verify checklist in `08-05-UAT-EVIDENCE.md`, each item marked satisfied/verified with an honest split between what the passing automated suites proved (`model_ui_roundtrip`, `daemon_roundtrip` 62 checks, `serve_roundtrip`) and what the user's explicit approval covered (live-page observation, visual/UX adequacy, keyboard/CSS-off inspection). Revision notes: none required.
- **Files modified:** `.planning/phases/08-model-adapter-interface-tier-gate-enforcement/08-05-UAT-EVIDENCE.md`

---

**Total deviations:** 3 (2 auto-fixed issues, 1 verification deviation, 1 UAT-evidence basis note)
**Impact on plan:** All necessary for the plan's own verification to stay green and for the checkpoint verdict to be recorded durably; no scope creep.

## Issues Encountered

- **Known environment condition (not fixed):** in-repo `python tests/evidence_roundtrip.py` and `python tests/scoring_roundtrip.py` fail their structural one-writer/one-scorer scans because the pre-existing `.phase*-wt` / `.merge*-wt` git worktrees ship second `evidence.py`/`runtime.py` files (observed: `.merge031-wt`, `.phase031-wt`, `.phase061-wt`, `.phase062-wt`, `.phase07-verify-tmp`, `.phase09-wt`, `.phase091-wt`, `.phase10-wt`, `.phase11-wt`, `.phase9994-wt`, `.phase9994x-wt`). Both tests pass in a clean copy of the tree that excludes the worktrees (`git archive HEAD` → `/tmp`, `evidence contract: ok`, `scoring contract: ok`). Nothing under the worktrees was touched.
- No code defects found in the 08-05 surface; the plan-verification suites and the companion suites are all green.

## User Setup Required

None - no external service configuration required. The default disabled backend path is the recorded UAT environment.

## Next Phase Readiness

- Plan 08-06 (phase release gate) can run against a learner surface whose assist routes are identifier-safe, parity-mapped, and no-leak proven, with the blocking human UAT recorded PASS — the plan's `key_links` chain (checkpoint → 08-05-UAT-EVIDENCE.md PASS → 08-06 release gate) is satisfied.
- A provider-connected pass path only needs a configured backend profile; the rendering, disclosure, and lock behaviour are already asserted over the rendered template.

---
*Phase: 08-model-adapter-interface-tier-gate-enforcement*
*Completed: 2026-08-11*

## Self-Check: PASSED

- Created files: `.planning/phases/08-model-adapter-interface-tier-gate-enforcement/08-05-SUMMARY.md` exists; `08-05-UAT-EVIDENCE.md` exists.
- Commits: the four task commits `f450eaa`, `7d1336c`, `56a8922`, `bddd31f` verified present on main, and the final `docs(08-05): complete identifier-safe assist routes and AgentAssist learner surface plan` metadata commit present (includes SUMMARY.md, UAT-EVIDENCE.md, STATE.md, ROADMAP.md).
- Verification: `python tests/model_ui_roundtrip.py` green; `python tests/daemon_roundtrip.py` green (62 checks); `python tests/serve_roundtrip.py` green; `python itembank.py schema --all` parses; `python tests/protocol_roundtrip.py` green; `test_schema_uses_supported_keywords_only()` green; `tests/evidence_roundtrip.py` and `tests/scoring_roundtrip.py` green in a clean copy excluding `.phase*-wt`/`.merge*-wt` (known in-repo worktree condition).

## PLAN COMPLETE
