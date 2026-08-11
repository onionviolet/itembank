---
phase: 09-subject-invariant-loop-emt-math-cs-integration
status: partial
created: 2026-08-11
---

# Phase 09 — Execution Verification (partial; held on two gates)

**Executed plans:** 09-01 (complete), 09-02 (complete), 09-03 (research complete, human approval PENDING).
**Held plans:** 09-04 (blocked on the 09-03 human approval gate — never auto-approved), 09-05 (blocked on Phase 5 — gate polled to budget, Phase 5 ALIVE at 3/7 plan summaries, mid-05-04).

## Executed verification

| Plan | Command(s) | Result | Evidence |
|---|---|---|---|
| 09-01 | `python tests/subject_loop_roundtrip.py` | exit 0 | EMT tracer (wrong → authored hint tier 0 → correct retry, 2 response + 1 hint events), persisted snapshot, resume drift against a live registry/settings edit, v3 upgrade + legacy one-time fill, fallback/mixed/disallowed refusals, semantic table wrapper, AST dispatch guard |
| 09-01 | `python tests/scoring_roundtrip.py && python tests/lesson_roundtrip.py && python tests/hint_roundtrip.py` | exit 0 ×3 | one scorer intact; lesson reader green with regenerated D-13 goldens (diff = wrapper line only); Phase 6 transition intact |
| 09-01 | `python tests/protocol_roundtrip.py && python tests/agent_roundtrip.py && python tests/evidence_roundtrip.py && python tests/selection_roundtrip.py && python tests/serve_roundtrip.py && python tests/config_roundtrip.py` | exit 0 ×6 | schema v3 pinned, cross-subject evidence/selection paths intact with selected-items subject resolution |
| 09-02 | `python tests/subject_loop_roundtrip.py` | exit 0 | settings-registry parity (schema default == missing-file == checked-in itembank.json), malformed-registry refusals, configuration-only fourth profile through select_profile AND do_start, lesson_layout enum |
| 09-02 | `python tests/config_roundtrip.py` | exit 0 | subject_profiles key published; phase-9 discovery rows; inert floor 4; model_backend/suggestion_reveal active |
| 09-03 | 09-03 automated audit guard (RESEARCH.md contains 'Package Legitimacy Audit', 'katex', 'SUS') | satisfied by grep (lines 112/118/122) | — |
| 09-03 | Human gate | **OPEN** | ask tool returned no interactive answer; checkpoint never auto-approved |

## Full-suite regression status (branch gsd/phase-09-subject-loop, main tip + 4 commits)

All `tests/*.py` pass except the documented environment/load items:

- `packaging_roundtrip.py` exit 1: **environment-blocked** at the Phase 13-03 frozen-sidecar handshake — this bash session runs a WSL/Linux python that cannot exec the Windows PE `itembank-sidecar.exe`; cmd/powershell blocked by the approval gate. The `.pyz` portion passes (build, resource commands, checksums, launchers, staged `subjects.py`, no bank/evidence).
- `daemon_roundtrip.py`, `presentation_roundtrip.py`, `agent_roundtrip.py`: intermittent flaky **under concurrent load** from other active phase worktrees (foreign `mkdtemp` dirs in `/tmp` snapshot windows; hostile-bank stems 404 by daemon allowlist before `do_start`). Reproduces on clean main; passes standalone.

## Verification still owed (when the gates lift)

- 09-04: `python tests/math_offline_roundtrip.py && python tests/lesson_roundtrip.py && python tests/packaging_roundtrip.py`; `.pyz` + network-unplugged Math pass; vendor inventory vs approved integrity.
- 09-05: `python tests/lesson_code_roundtrip.py && python tests/check_roundtrip.py && python tests/scoring_roundtrip.py`; subject-loop matrix + math/code specialty suites; `python tests/daemon_roundtrip.py && python tests/lesson_roundtrip.py`; full `tests/*.py`; manual 320px/200%, keyboard/focus, assistive-table/MathML, light/dark, reduced-motion, network-unplugged matrix per 09-VALIDATION.md.
