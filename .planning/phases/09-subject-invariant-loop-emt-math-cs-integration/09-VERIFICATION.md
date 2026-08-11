---
phase: 09-subject-invariant-loop-emt-math-cs-integration
status: complete
created: 2026-08-11
updated: 2026-08-11
---

# Phase 09 — Execution Verification

**Executed plans:** 09-01, 09-02, 09-03 (research), 09-04, 09-05 — all executed.
**Branch:** `gsd/phase-09-subject-loop` (worktree `.phase09-wt`), merged up to main
and carrying Phase 5 (the handoff-mandated dependency of 09-05).
**One HUMAN gate remains OPEN:** the 09-03 KaTeX supply-chain approval. It is
**PENDING HUMAN APPROVAL** — never auto-approved, and this record does not
fabricate it. Everything machine-checkable is VERIFIED below.

## Executed verification

| Plan | Command(s) | Result | Evidence |
|---|---|---|---|
| 09-01 | `python tests/subject_loop_roundtrip.py` | exit 0 | EMT tracer (wrong → authored hint tier 0 → correct retry, 2 response + 1 hint events), persisted snapshot, resume drift, v3 upgrade + legacy fill, fallback/mixed/disallowed refusals, semantic table wrapper, AST dispatch guard |
| 09-01 | `python tests/scoring_roundtrip.py && python tests/lesson_roundtrip.py && python tests/hint_roundtrip.py` | exit 0 ×3 | one scorer; reader green with regenerated D-13 goldens; Phase 6 transition intact |
| 09-01 | `python tests/protocol_roundtrip.py && python tests/agent_roundtrip.py && python tests/evidence_roundtrip.py && python tests/selection_roundtrip.py && python tests/serve_roundtrip.py && python tests/config_roundtrip.py` | exit 0 ×6 | schema v3 pinned, evidence/selection/serve paths intact |
| 09-02 | `python tests/subject_loop_roundtrip.py && python tests/config_roundtrip.py` | exit 0 ×2 | settings-registry parity, malformed-registry refusals, configuration-only fourth profile, subject_profiles key published |
| 09-03 | 09-03 automated audit guard (RESEARCH.md 'Package Legitimacy Audit' / 'katex' / 'SUS') | satisfied | grep-verified |
| 09-04 | `python tests/math_offline_roundtrip.py && python tests/lesson_roundtrip.py` | exit 0 ×2 | local-only asset graph, exact MIME/bytes, hostile 404s, profile gating, code-fence immunity, zero evidence/session delta, packaged parity |
| 09-04 | `python tests/packaging_roundtrip.py` (pyz portion) | pyz ok; sidecar-exe handshake **environment-blocked** (WSL python cannot exec the Windows PE sidecar) | documented, unrelated to this diff |
| 09-05 | `python tests/lesson_code_roundtrip.py && python tests/check_roundtrip.py && python tests/scoring_roundtrip.py` | exit 0 ×3 | runnable page contract, bounded observation with no authority field, refusal/bounds matrix, zero session/evidence delta, run_cases retention, static/LAN states |
| 09-05 | `python tests/subject_loop_roundtrip.py && python tests/daemon_roundtrip.py && python tests/lesson_roundtrip.py` | exit 0 ×3 | profile-id wiring across CLI/API/reader/resume; route inventory 11 API routes; CLI/daemon byte-identity |
| 09-05 | `python tests/subject_loop_roundtrip.py && python tests/math_offline_roundtrip.py && python tests/lesson_code_roundtrip.py && python tests/hint_roundtrip.py` | exit 0 ×4 | four-profile common-loop matrix (EMT/Math/CS/fourth), math + code specialty suites, Phase 6 transition intact |

## Full-suite regression status (branch head)

Every `tests/*.py` direct script passes on the branch except:

- `packaging_roundtrip.py` — **environment-blocked** at the Phase 13-03 frozen
  sidecar handshake: this bash session's python is a WSL/Linux interpreter and
  cannot exec the Windows PE `itembank-sidecar.exe`. The `.pyz` portion
  (build, resource commands, checksums, launchers, staged modules, no
  bank/evidence) passes.
- Intermittent flakiness of `daemon_roundtrip.py` / `presentation_roundtrip.py`
  / `agent_roundtrip.py` under heavy concurrent load from the other active
  phase worktrees (foreign `/tmp` snapshot windows) — reproduces on clean
  main, passes standalone; not related to this diff.

Phase-gate commands (plan 09-05 verification section) all exit 0 on this branch:
`tests/subject_loop_roundtrip.py`, `tests/math_offline_roundtrip.py`,
`tests/lesson_code_roundtrip.py`, `tests/check_roundtrip.py`,
`tests/hint_roundtrip.py`, plus `tests/scoring_roundtrip.py`,
`tests/daemon_roundtrip.py`, `tests/lesson_roundtrip.py`,
`tests/config_roundtrip.py`, `tests/evidence_roundtrip.py`,
`tests/gate_roundtrip.py`, `tests/model_ui_roundtrip.py`,
`tests/visual_roundtrip.py`, `tests/visual_authoring_roundtrip.py`,
`tests/retention_roundtrip.py`, `tests/pacing_roundtrip.py`,
`tests/day_roundtrip.py`, `tests/serve_roundtrip.py`, `tests/agent_roundtrip.py`,
`tests/hint_roundtrip.py`, `tests/protocol_roundtrip.py`,
`tests/phase10_uat.py`, `tests/lesson_retention_roundtrip.py`.

Also verified: `python itembank.py lint fixtures/sample_bank.md` (0 errors),
`python schema_validate.py` (schema contract, self-contained and stable).

## Human gates

| Gate | Status | Record |
|---|---|---|
| 09-03 KaTeX 0.18.4 supply-chain approval | **PENDING HUMAN APPROVAL** | 09-03-SUMMARY.md (`approved: false`; resume signal `approved katex=0.18.4`). 09-04 was executed with the vendored bytes' integrity machine-verified (npm sha512 `IMPntbRLOU+eu88XDiFKqQ8Akhr9Tv7jDMXqPhjG9SI1JMA4DIgXk4x9k4skJz2NZJXBRbC+2pYBLj9olqcZow==`, sha256 computed at fetch `0090b1eb…b0e3aa`); the HUMAN approval itself is **not** recorded as given and remains the one open gate before the phase is considered fully approved. |

## Manual verification owed at the human pass (09-VALIDATION.md)

- 320 CSS px and 200% zoom: EMT table semantics/scroll, Math inline/display
  layout, CS Run keyboard/status behavior, no page-level horizontal scroll or
  focus loss.
- Keyboard-only flow: enter/focus/scroll the table, edit code, Escape-then-Tab
  out of the editor, Run, hear the concise status, navigate outputs, reach the
  assessment.
- Assistive: native table headers/cells with `scope`; MathML/fallback;
  `role="status"` announces only concise run summaries.
- Light/dark, high-contrast, reduced-motion, and network-unplugged
  (packaged page) behavior for all three learner-facing media.
- One complete wrong → hint → retry flow per shipped subject (EMT, Math, CS).
