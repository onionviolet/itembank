---
phase: 09-subject-invariant-loop-emt-math-cs-integration
status: partial
created: 2026-08-11
---

# Phase 09 — UAT (partial; held on two gates)

**Scope of this record:** UAT rows for the executed plans (09-01, 09-02, 09-03 research). Rows for the held plans (09-04 math, 09-05 runnable code + four-profile matrix) remain OPEN and are listed with their acceptance checks for the continuation.

## Closed rows (executed plans)

| Requirement | Acceptance check | Result | Evidence |
|---|---|---|---|
| LOOP-01 (subject-invariant loop) | An EMT learner completes lesson → wrong → authored hint → retry → evidence under one persisted profile; resume consumes the stored snapshot | ✅ Automated | `tests/subject_loop_roundtrip.py#test_emt_learner_loop_with_persisted_profile` (tracer + resume drift); commit 0c2ec94 |
| LOOP-04 (EMT prose + tables) | Headings/prose/lists/table in source order; semantic table in a labelled focusable overflow wrapper; no EMT-only renderer | ✅ Automated | `tests/subject_loop_roundtrip.py#test_emt_lesson_semantic_table`; goldens regenerated; commit 0c2ec94 |
| LOOP-05 (fourth subject by configuration) | A fourth profile loads from temporary settings, resolves through the public selector AND do_start, snapshot shape parity; no subject-id dispatch in application code | ✅ Automated | `tests/subject_loop_roundtrip.py#test_fourth_profile_is_configuration_only`, `#test_no_subject_dispatch_in_surfaces`; commit a6fdba6 |
| D-01..D-04 (profile data policy) | Explicit-id/known/conservative/mixed-refusal selection; settings-backed registry; conservative default code-owned | ✅ Automated | subject-loop suite (fallback/mixed/disallowed/parity/malformed); commits 0c2ec94 + a6fdba6 |
| D-12/D-13 (EMT semantics + narrow tables) | Semantic table + overflow wrapper at narrow width | ✅ Automated (markup/CSS hooks) | see LOOP-04 row; manual 320px/200% check still owed at phase close |
| D-07/D-08 (KaTeX, presentation-only) | Human approval of exact immutable release; no CDN; math never scores | ⏸ Gate OPEN | 09-03-SUMMARY.md (PENDING); commit 238782f |

## Open rows (held plans — acceptance checks for the continuation)

| Requirement | Acceptance check | Gate |
|---|---|---|
| LOOP-02 (offline Math) | Approved KaTeX bytes vendored + packaged; local-only asset graph; inline/display/error/unavailable states; zero scorer/evidence path; unplugged packaged page | 09-03 human approval (`approved katex=0.18.4`) → 09-04 |
| LOOP-03 (runnable lesson code) | One `run_source()` shared with Phase 5 runner; LAN/language/source gates before invocation; neutral observation payload; zero cursor/hint/evidence delta; static/refused states honest | Phase 5 complete + merge into this branch → 09-05 |
| LOOP-01 matrix (EMT/Math/CS/fourth) | One table-driven driver, identical transition/evidence keys; guided-discovery fixture sequence per subject | Phase 5 + 09-04 → 09-05 Task 3 |
| Manual matrix (09-VALIDATION.md) | 320px/200%, keyboard/focus, assistive table/MathML, light/dark, reduced-motion, network-unplugged; public-payload walkthrough | end of phase |

**UAT status: PARTIAL — 6 rows closed by automated evidence, 1 gate-pending (KaTeX approval), 3 rows + manual matrix owed.**
