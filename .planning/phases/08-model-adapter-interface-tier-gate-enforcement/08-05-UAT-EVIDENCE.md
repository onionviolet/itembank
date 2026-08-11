---
status: pass
phase: 08-model-adapter-interface-tier-gate-enforcement
plan: 05
type: blocking-human-checkpoint
source: 08-05-PLAN.md Task 3 (checkpoint:human-verify, gate=blocking)
approved: 2026-08-11
updated: 2026-08-11
---

# 08-05 Blocking Human UAT Evidence — AgentAssist learner surface over the daemon

## Verdict

**PASS** — user-approved at the orchestrator checkpoint. The user selected
"approved — proceed to 08-05 closure" when the plan-08-05 checkpoint was
presented, per the plan's Task 3 `<resume-signal>` ("Type 'approved' or
describe the issues found for revision"). No issues were raised, so the plan
proceeds to 08-06 (release gate).

## Environment

| Field | Value |
|-------|-------|
| OS | Windows (Windows 11) |
| Python | 3.13.3 (`python --version` at closure) |
| Browser | Live observation performed by the user at the orchestrator checkpoint. This closure's automated evidence is browser-free DOM/JSON/JS string scanning (the repo's round-trip suites ship no browser dependency); the visual/UX adequacy judgment rests on the user's explicit approval. |

## Automated Evidence Basis

The three suites in the plan's `<verification>` list ran green at closure:

1. `python tests/model_ui_roundtrip.py` — **ok**: assist DOM/copy, lifecycle +
   structural lock, pending rubric rows, no-leak boundary,
   responsive/reduced-motion/announce-once all held.
2. `python tests/daemon_roundtrip.py` — **ok: daemon served 62 checks** — index,
   quiz, answer scoring, cross-bank isolation, stem collisions, the route/CLI
   inventory, the `/api/*` session routes including the two new assist routes,
   the `/report` page, and the detect-and-attach startup path all held.
3. `python tests/serve_roundtrip.py` — **ok**: served sitting scored 6 items
   via `/api/start` + `/api/submit`, recorded 6 evidence events once, refreshed
   the attempt view, and kept the static offline build green.

Schema-contract deviation check (the plan's verification list does not name
`schema_validate.py`, but the phase-standard contract check was re-confirmed):
`python itembank.py schema --all` parses, `python tests/protocol_roundtrip.py`
green, `test_schema_uses_supported_keywords_only()` (tests/model_gate_roundtrip.py)
green — recorded in 08-05-SUMMARY.md Deviations.

## Checklist — plan Task 3 how-to-verify (8 items)

Each item is marked **satisfied/verified**. The evidence column is honest about
provenance: **Automated** = proven by the passing suites listed above; **User
approval** = the human backstop at the orchestrator checkpoint for judgments a
DOM/JSON assertion cannot fully express (visual adequacy, live-page behaviour).

| # | Plan how-to-verify item | Result | Evidence |
|---|-------------------------|--------|----------|
| 1 | Start the daemon on a temporary lesson bank (`python itembank.py daemon . --no-open`) and open the quiz at the printed localhost URL. | satisfied/verified | **Automated:** serve_roundtrip (served quiz over a temp bank via `/api/start` + `/api/submit`, attempt refresh); daemon_roundtrip `check_served_api_flow`, `check_serve_attempt_refresh`, detect-and-attach startup path. **User approval:** checkpoint sign-off. |
| 2 | Answer a question wrong in practice mode; confirm `Help and evidence` is collapsed, subordinate, and opt-in; click `Get optional guidance` and observe exactly one polite status transition (`Preparing optional guidance…`) before a typed outcome — never a chat box or typing animation. | satisfied/verified | **Automated:** model_ui_roundtrip `check_dom_order_and_copy` (assist region after session details in DOM order; native `details/summary` `Help and evidence`; opt-in collapsed by default) and `check_lifecycle_and_lock` (single bounded status line `Preparing optional guidance…`; typed outcome only; no chat/typing-animation markup in ASSIST_JS; announce-once aria-live). **User approval:** live observation of the one-transition behaviour. |
| 3 | With the default disabled backend, confirm the exact unavailable copy (`Generated help is unavailable. You can keep learning with the lesson and authored hints.`) and that the authored hint ladder and answer flow still work. | satisfied/verified | **Automated:** model_ui_roundtrip `check_lifecycle_and_lock` (unavailable copy verbatim per 08-UI-SPEC Copywriting Contract); daemon_roundtrip `check_answer_scoring` (answer flow) and `check_api_assist_routes` (typed unavailable payload from `session.do_hint` with no reason code); serve_roundtrip offline build green. **User approval:** checkpoint sign-off. |
| 4 | If a backend profile is enabled, confirm passed guidance renders in the `Generated support` container with the generated disclosure sentence and no correctness claim; confirm the locked-tier structural lock labels its unlock condition. | satisfied/verified | **Automated:** model_ui_roundtrip `check_lifecycle_and_lock` (`Generated support` container + generated disclosure sentence, no correctness claim; labeled structural lock with the unlock condition stated and no model voice) and `check_no_leak` (no tier/backend/profile detail in the passed render). **Caveat:** the closure environment has the default disabled backend, so the passed-path render is proven by DOM/JS assertion over the rendered template, not by a live provider round trip; the visual adequacy judgment is covered by **user approval**. |
| 5 | Submit a short answer and open the pending rubric suggestion: each point shows `Pending rubric suggestion — human review required` with pass/fail/uncertain rows, never a number, fraction, check, or cross glyph; confirm no accept button exists in the browser. | satisfied/verified | **Automated:** model_ui_roundtrip `check_pending_rubric_rows` (one pending row per point, exact heading, pending token only — no number/fraction/check/cross glyph) and `check_no_leak` (no accepted-mark control of any kind in the browser DOM). **User approval:** checkpoint sign-off. |
| 6 | Confirm `Record human mark` exists only in the CLI (`itembank mark --session … --proposal …`), and that after it the report shows the human mark. | satisfied/verified | **Automated:** 08-04's `python tests/model_surface_roundtrip.py` `test_cmd_mark_proposal_human_accept` (human-only accept path); this plan's `check_no_leak` (no accept control in the browser) and daemon_roundtrip `check_report_populated` (report reflects the human mark). **User approval:** checkpoint sign-off. |
| 7 | Resize to 1280, 768, 375, and 320px at 200% zoom: no horizontal scroll; keyboard-only operation of the disclosure and retry control; a screen-reader/CSS-off inspection reveals no tier, key, fact, profile, backend, or drop detail. | satisfied/verified | **Automated:** model_ui_roundtrip `check_responsive_and_motion` (320px/200% no horizontal scroll; reduced motion disables nonessential animation) and `check_no_leak` (flatten() scan over page HTML, all JSON payloads, and SERVED_JS for key strings, tier numbers, fact text, profile names, backend classes, gate reasons, and dropped candidate phrases; CSS-off/attribute scan) and `check_dom_order_and_copy` (keyboard-native disclosure, announce-once). **User approval:** live keyboard/CSS-off inspection. |
| 8 | Record the verdict, environment (OS, browser, Python version), and each checklist result in `.planning/phases/08-model-adapter-interface-tier-gate-enforcement/08-05-UAT-EVIDENCE.md`. | satisfied/verified | This file. |

## Honesty Note — what automation proved vs. what approval covered

- **Automation proved:** the no-leak API/DOM boundary (forbidden fields refused
  400 before any handler; flatten() scans over HTML/JSON/JS find no key, tier,
  fact, profile, backend, gate-reason, or drop detail), the exact UI-SPEC copy
  strings verbatim, the lifecycle-state wiring (requested/thinking/pass/drop/
  unavailable/cancelled/retry), one pending row per rubric point with the
  pending token only and no browser accept control, the structural lock with
  the unlock condition and no model voice, the 320px/200% no-horizontal-scroll
  and reduced-motion behaviour, and that the offline build page and the
  answer/submit/score/evidence/report loop stay green.
- **User approval covered:** the live-page observation (opening the daemon URL,
  clicking through, one polite status transition, no chat/typing UI), the
  visual/UX adequacy judgment, keyboard-only operation and screen-reader/CSS-off
  inspection, and the overall learner-facing sign-off. This closure did not
  re-run a live browser session; it re-ran the automated suites and recorded
  the user's checkpoint decision verbatim.

## Revision Notes

**None required.** No issues were found and no revision was requested at the
checkpoint. The plan may proceed to 08-06 (phase release gate).
