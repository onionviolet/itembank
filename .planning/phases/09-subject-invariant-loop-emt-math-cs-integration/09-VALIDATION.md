---
phase: 09
slug: subject-invariant-loop-emt-math-cs-integration
status: draft
nyquist_compliant: false
wave_0_complete: false
wave_0_plan: "task-local RED-first scaffolds in 09-01, 09-04, and 09-05"
created: 2026-08-08
---

# Phase 09 — Validation Strategy

> Per-phase validation contract for the Subject-Invariant Loop execution. Standalone stdlib scripts prove the shared profile/session/feedback/evidence path, local-only Math resource graph, one-runner CS path, semantic EMT output, and configuration-only fourth profile. A final manual browser matrix covers rendered glyph/layout, keyboard and assistive behavior, narrow/zoom overflow, and a genuinely unplugged packaged artifact.

---

## Test Infrastructure

| Property | Value |
|---|---|
| **Framework** | Standalone Python assertion scripts using stdlib only |
| **Config file** | None; repository CI executes every `tests/*.py` script |
| **Quick run command** | `python tests/subject_loop_roundtrip.py` |
| **Focused Phase 9 run** | `@('tests/subject_loop_roundtrip.py','tests/math_offline_roundtrip.py','tests/lesson_code_roundtrip.py') | ForEach-Object { python $_; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE } }` |
| **Full suite command** | `Get-ChildItem tests -Filter *.py | Sort-Object Name | ForEach-Object { python $_.FullName; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE } }` |
| **Focused feedback target** | 60 seconds or less per task commit |

No external test framework or watch mode is introduced. Tests that do not exist at planning time are created RED-first inside their owning TDD task before that task changes production code; upstream Phase 3/5/6 scripts are preconditions and cannot be recreated in Phase 9.

---

## Sampling Rate

- **After every task commit:** Run that task's exact `<verify><automated>` command from the map below.
- **After Plan 09-01:** Run `python tests/subject_loop_roundtrip.py`, `python tests/scoring_roundtrip.py`, `python tests/lesson_roundtrip.py`, and `python tests/hint_roundtrip.py`.
- **After Plan 09-02:** Run `python tests/subject_loop_roundtrip.py` and `python tests/config_roundtrip.py`.
- **At the Plan 09-03 gate:** Run its research/audit guard, then require the human resume signal carrying the immutable version and 64-hex tarball SHA-256; no repository asset may exist before approval.
- **After Plan 09-04:** Run `python tests/math_offline_roundtrip.py`, `python tests/lesson_roundtrip.py`, and `python tests/packaging_roundtrip.py`.
- **After Plan 09-05:** Run the Phase 9 focused command plus `python tests/check_roundtrip.py`, `python tests/hint_roundtrip.py`, `python tests/scoring_roundtrip.py`, `python tests/daemon_roundtrip.py`, and `python tests/lesson_roundtrip.py`.
- **After every wave:** Run all completed-plan commands for that wave plus `python tests/subject_loop_roundtrip.py`; in Wave 4 run the full repository suite.
- **Before `$gsd-verify-work`:** Full suite green, packaged-artifact network-unplugged Math pass, and the UI/accessibility matrix below completed against `09-UI-SPEC.md`.
- **Max feedback latency:** focused task command under 60 seconds; the full suite is reserved for wave/phase boundaries.

---

## Per-Plan Automated Commands and Expected Evidence

| Plan | Automated command(s) | Test files / evidence locations | Explicit evidence required before the plan is complete |
|---|---|---|---|
| 09-01 | `python tests/subject_loop_roundtrip.py`; `python tests/scoring_roundtrip.py`; `python tests/lesson_roundtrip.py`; `python tests/hint_roundtrip.py` | `tests/subject_loop_roundtrip.py`, upstream scoring/lesson/hint scripts, `09-01-SUMMARY.md` | One EMT trace records wrong response, authored hint, correct retry, and unchanged shared transition/evidence shapes; the stored profile survives registry drift; unknown/mixed/disallowed cases are explicit; native table order and wrapper hooks are asserted. |
| 09-02 | `python tests/subject_loop_roundtrip.py`; `python tests/config_roundtrip.py` | `tests/subject_loop_roundtrip.py`, `tests/config_roundtrip.py`, `09-02-SUMMARY.md` | Schema/default/checked-in registries match, malformed profiles fail closed, a temporary fourth entry loads through public configuration, and the source guard finds no production subject-id dispatch. |
| 09-03 | `python -c "from pathlib import Path; s=Path('.planning/phases/09-subject-invariant-loop-emt-math-cs-integration/09-RESEARCH.md').read_text(encoding='utf-8'); assert 'Package Legitimacy Audit' in s and 'katex' in s.lower() and 'SUS' in s"` plus the blocking human gate | `09-RESEARCH.md`, immutable approval fields in `09-03-SUMMARY.md` | The summary names the official immutable version/tag, MIT license result, npm tarball SHA-256, and complete browser/font inventory; no vendored asset exists before approval. |
| 09-04 | `python tests/math_offline_roundtrip.py`; `python tests/lesson_roundtrip.py`; `python tests/packaging_roundtrip.py` | `tests/math_offline_roundtrip.py`, `tests/lesson_roundtrip.py`, `tests/packaging_roundtrip.py`, `09-04-SUMMARY.md` | Checkout and `.pyz` contain byte-identical approved assets; every CSS font resolves locally; no external URL/fallback exists; inline/display/error/code-immunity and `09-UI-SPEC.md` DOM/state hooks pass without any scoring/evidence path. |
| 09-05 | Phase 9 focused command plus `python tests/check_roundtrip.py`, `python tests/hint_roundtrip.py`, `python tests/scoring_roundtrip.py`, `python tests/daemon_roundtrip.py`, `python tests/lesson_roundtrip.py`, then the full suite | `tests/lesson_code_roundtrip.py`, `tests/subject_loop_roundtrip.py`, upstream check/hint/scoring/daemon/lesson scripts, three synthetic fixtures, `09-05-SUMMARY.md` | Lesson Run reuses one bounded runner and changes no session/evidence authority; exact ready/loading/completed/error/refusal DOM states pass; EMT/Math/CS/fourth use one driver with equal transition/evidence keys and the guided-discovery sequence. |

The `09-NN-SUMMARY.md` for each plan records the command, exit code, and evidence assertions observed. The phase verification/UAT artifact records the manual browser/accessibility rows; a command name without its asserted evidence is not sufficient sign-off.

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure / invariant behavior | Test type | Automated command | File state before task | Status |
|---|---:|---:|---|---|---|---|---|---|---|
| 09-01-01 | 01 | 1 | LOOP-01, LOOP-04 | T-09-01..04 | One persisted profile reaches the real lesson/wrong/hint/retry/evidence path; table remains semantic | tracer/integration | `python tests/subject_loop_roundtrip.py` | `tests/subject_loop_roundtrip.py` created RED-first in task | pending |
| 09-01-02 | 01 | 1 | LOOP-01 | T-09-01..03 | Conservative fallback, mixed-subject refusal, disallowed-type no-write behavior | integration | `python tests/subject_loop_roundtrip.py` | extend prior task | pending |
| 09-02-01 | 02 | 2 | LOOP-01, LOOP-05 | T-09-05..07 | Closed schema and runtime validator reject forged capability/verifier data | unit/integration | `python tests/subject_loop_roundtrip.py && python tests/config_roundtrip.py` | subject test exists; config test is upstream | pending |
| 09-02-02 | 02 | 2 | LOOP-05 | T-09-05..07 | Fourth profile loads from temporary configuration; no subject-name application dispatch | integration/source guard | `python tests/subject_loop_roundtrip.py` | extend prior task | pending |
| 09-03-01 | 03 | 2 | LOOP-02 | T-09-SC, T-09-09 | A blocking human reviews official immutable metadata and records exact ownership/source/version/license/distribution/SHA-256 without downloading archive/package bytes or creating vendor/cache/staging/repository changes | audit + human gate | `python -c "from pathlib import Path; s=Path('.planning/phases/09-subject-invariant-loop-emt-math-cs-integration/09-RESEARCH.md').read_text(encoding='utf-8'); assert 'Package Legitimacy Audit' in s and 'katex' in s.lower() and 'SUS' in s"` | audit exists; immutable metadata-only approval is human-gated | pending |
| 09-04-01 | 04 | 3 | LOOP-02 | T-09-08, T-09-SC | Approved bytes only; complete fonts/license; checkout/zipapp parity; private files excluded | packaging/integration | `python tests/packaging_roundtrip.py` | upstream test extended RED-first | pending |
| 09-04-02 | 04 | 3 | LOOP-02 | T-09-09..11 | Closed local assets, safe Math options, raw-source fallback, no scorer/evidence path, UI contract states | browser/contract/integration | `python tests/math_offline_roundtrip.py && python tests/lesson_roundtrip.py && python tests/packaging_roundtrip.py` | math test created RED-first in task | pending |
| 09-05-01 | 05 | 4 | LOOP-03 | T-09-12..14 | One bounded runner, server-side policy, neutral observation payload, zero cursor/hint/evidence delta | integration | `python tests/lesson_code_roundtrip.py && python tests/check_roundtrip.py && python tests/scoring_roundtrip.py` | lesson-code test created RED-first; others upstream | pending |
| 09-05-02 | 05 | 4 | LOOP-01, LOOP-03, LOOP-05 | T-09-12, T-09-15 | Only profile id crosses clients; stored snapshot is authoritative; no path/capability authority leak | integration | `python tests/subject_loop_roundtrip.py && python tests/daemon_roundtrip.py && python tests/lesson_roundtrip.py` | extend subject test; others upstream | pending |
| 09-05-03 | 05 | 4 | LOOP-01..05 | T-09-12..15 | EMT/Math/CS/fourth share one driver, transitions, evidence shape, guided sequence, and UI contract | phase integration | `python tests/subject_loop_roundtrip.py && python tests/math_offline_roundtrip.py && python tests/lesson_code_roundtrip.py && python tests/hint_roundtrip.py` | all focused scripts exist by this task | pending |

*Status vocabulary: pending · green · red · flaky. A human gate supplements but never replaces the automated row for 09-03-01.*

---

## Wave Sampling Matrix

| Wave | Plans | Required automated sample before advancing | Human dependency |
|---:|---|---|---|
| 1 | 09-01 | Subject loop + scoring + lesson + hint scripts | none |
| 2 | 09-02, 09-03 | Subject loop + config + 09-03 audit guard | Non-automatable metadata-only KaTeX immutable source/version/license/distribution/SHA-256 approval; no byte download; Wave 3 remains blocked until recorded |
| 3 | 09-04 | Math offline + lesson + packaging + subject loop | network-unplugged visual check may be recorded at phase gate; automation must already prove local-only graph |
| 4 | 09-05 | All Phase 9 focused scripts, check/hint/scoring/daemon/lesson regressions, then every `tests/*.py` | end-of-phase browser/accessibility matrix |

---

## Requirement and Decision Coverage

| Contract | Automated evidence | Manual evidence |
|---|---|---|
| LOOP-01 / D-01..04 | Table-driven subject loop, stored snapshot/resume drift, fallback/mixed/disallowed cases, client-id-only tests | Inspect one resumed shipped-subject sitting and its path-free profile metadata |
| LOOP-02 / D-05..08 | Tarball/package inventory, local asset allowlist, no network strings/fallback, delimiter/code immunity, safe options, no scorer/evidence calls | Open packaged Math lesson with networking disabled; inline/display/wide/error formulas at 320px/200% |
| LOOP-03 / D-09..11 | `run_source()` reuse, LAN/language/source gates, timeout/output cap, exact UI state copy, neutral payload, byte-for-state zero evidence delta | Keyboard edit/Run/Escape flow, multiple blocks, status announcement, retained edits/output |
| LOOP-04 / D-12..13 | Shared renderer source guard, native table tag/order/header/cell/wrapper checks | Keyboard and screen-reader table navigation at narrow width and 200% zoom |
| LOOP-05 / D-02, D-15 | Temporary fourth settings entry plus AST guard and common driver | none beyond reviewing the executable output |
| Roadmap guided discovery / D-14 | Fixtures assert context→action/prediction→targeted hint→retry→explanation and identical transition/evidence shapes | Complete the sequence once per shipped subject and confirm media controls remain subordinate |
| `09-UI-SPEC.md` plus global UI contract | Structural/state/copy/focus/overflow assertions, key-free public payload/state fixtures, and offline/degraded behavior in subject, math, lesson-code, and lesson scripts | Math glyph/layout, EMT semantic scroll, CS keyboard/status, light/dark, reduced motion, 1280/768/375 responsive views, plus the stricter 320px/200% phase stress case |

Deferred Phase 10 scheduling/pacing, private-bank authoring, and additional language runners are excluded from this validation scope.

---

## Wave 0 and RED-First Requirements

The phase keeps exactly five plans and four execution waves. It therefore uses task-local RED-first test creation rather than a sixth validation-only plan:

- [ ] 09-01 Task 1 creates executable `tests/subject_loop_roundtrip.py` before modifying `subjects.py`, session schema/state, or surfaces.
- [ ] 09-04 Task 1 extends existing `tests/packaging_roundtrip.py` with failing KaTeX inventory/archive assertions before copying approved assets.
- [ ] 09-04 Task 2 creates executable `tests/math_offline_roundtrip.py` before adding asset routes or the Math adapter.
- [ ] 09-05 Task 1 creates executable `tests/lesson_code_roundtrip.py` before extracting `run_source()` or adding the daemon route/control.
- [ ] Every upstream prerequisite named in a task `<precondition>` exists and passes. Missing Phase 3/5/6 contracts halt execution; Phase 9 does not create substitutes.

Set `wave_0_complete: true` only after these RED-first scaffolds have been observed at their owning task boundary and the required upstream scripts exist. `nyquist_compliant: true` and `status: validated` remain execution/validation outcomes, not planning claims.

---

## Manual-Only Verifications

| Behavior | Requirement | Why manual | Test instructions |
|---|---|---|---|
| Packaged offline Math layout | LOOP-02 | String/resource tests prove locality, not browser glyph layout or MathML reading quality | Build/open the `.pyz`, disable networking, load a Math lesson containing inline, display, wide, malformed, and dollar-sign-in-code cases. Confirm local rendering, contained overflow, source fallback, no external request, and accessible formula representation. |
| EMT table semantics and narrow flow | LOOP-04 | Screen-reader header association and keyboard-scroll usability require assistive/perceptual judgment | At 320 CSS px and 200% zoom, keyboard to the labeled table wrapper, scroll all columns, read headers/cells with Narrator/NVDA, and continue to the next lesson element without page-level overflow. |
| Runnable code keyboard/status flow | LOOP-03 | Focus, announcement timing, and editor escape behavior are interactive | With keyboard only, edit source, use Tab/Shift+Tab, Escape then Tab out, run it, and inspect loading/completed/nonzero/timeout/truncated/request-error/refusal states. Confirm focus stays predictable and edits/output persist. |
| Shared guided-discovery sequence | LOOP-01 | Pedagogical continuity and media subordination require learner-flow judgment | For EMT, Math, and CS: read context, make the requested prediction/action, answer wrong, request one targeted hint, retry materially, and read explanation. Confirm the same flow vocabulary and no media control advances/scored the session. |
| Color/reflow/reduced motion | LOOP-02, LOOP-03, LOOP-04 | Cross-surface perception is not fully captured by HTML assertions | Capture and inspect the three surfaces at 1280, 768, and 375 CSS px in light/dark and reduced motion, then repeat the strict 320px/200% and high-contrast stress case. State and recovery remain textual, DOM order is unchanged, controls remain reachable, and no page-level horizontal scroll appears. |
| Public-payload and degraded-state walkthrough | LOOP-01, LOOP-02, LOOP-03 | Automated fixtures prove payload boundaries; a learner-visible recovery pass confirms the result remains comprehensible | With networking disabled and no provider or private key material in browser state, inspect EMT/Math/CS ready, loading, success, malformed, timeout, refusal, and unavailable fixtures. Confirm raw lesson/math/code sources remain readable, no answer/capability/path authority appears in DOM/JSON, and each state offers the next legal action. |

---

## Validation Sign-Off

- [ ] Every plan task has an automated command in this map and in its PLAN `<verify>` block.
- [ ] No three consecutive tasks lack a focused automated sample.
- [ ] Task-local RED-first files exist before their production changes; upstream Phase 3/5/6 prerequisites pass.
- [ ] Plan 09-03 records exact human-approved immutable source/version/license/distribution/SHA-256 without any archive/package download; 09-04 alone fetches and verifies bytes before writing assets.
- [ ] No watch-mode or interactive command blocks automated execution.
- [ ] Focused feedback latency remains under 60 seconds; full suite runs at the Wave 4/phase boundary.
- [ ] LOOP-01..05, D-01..15, threat mitigations, and `09-UI-SPEC.md` contracts are green.
- [ ] Manual offline/browser/accessibility matrix is complete with evidence in verification/UAT artifacts.
- [ ] Responsive evidence covers 1280/768/375 plus 320px/200%, and public-payload/degraded fixtures prove no key, source-path authority, hidden verifier, or external-asset dependency reaches the browser.
- [ ] `nyquist_compliant: true`, `wave_0_complete: true`, and `status: validated` are set only after the corresponding checks exist and pass.

**Approval:** pending execution evidence
