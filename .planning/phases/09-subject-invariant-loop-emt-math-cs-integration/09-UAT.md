---
phase: 09-subject-invariant-loop-emt-math-cs-integration
status: complete
created: 2026-08-11
updated: 2026-08-11
---

# Phase 09 — UAT

**Scope of this record:** UAT rows for every executed plan (09-01..09-05).
One human gate (KaTeX approval) remains OPEN; every machine-checkable row is
closed by automated evidence on branch `gsd/phase-09-subject-loop`.

## Closed rows

| Requirement | Acceptance check | Result | Evidence |
|---|---|---|---|
| LOOP-01 (subject-invariant loop) | EMT/Math/CS + a configured fourth subject traverse one lesson → wrong → authored hint → retry → evidence loop under one persisted profile; resume consumes the stored snapshot | ✅ Automated | `tests/subject_loop_roundtrip.py#test_emt_learner_loop_with_persisted_profile` (tracer + resume drift), `#test_four_subjects_share_one_guided_loop` (table-driven matrix: identical transitions hold → reveal_tier → complete, cursor progression, tier-0 hint, evidence spine, outcome); commits 0c2ec94, 0ed3783 |
| LOOP-02 (offline Math) | Vendored immutable KaTeX local-only asset graph; inline/display/error/unavailable states; zero scorer/evidence path; packaged parity | ✅ Automated (machine-checkable) | `tests/math_offline_roundtrip.py`; 09-04-SUMMARY.md. **Human supply-chain approval still PENDING** (09-03 gate — never auto-approved). |
| LOOP-03 (runnable lesson code) | One `run_source()` shared with the Phase 5 runner; LAN/language/source gates before invocation; neutral observation payload; zero cursor/hint/evidence delta; static/refused states honest | ✅ Automated | `tests/lesson_code_roundtrip.py` (bounded observation, refusal/bounds matrix, zero session/evidence delta, run_cases retention, static/LAN states); `tests/check_roundtrip.py` (runner contract); commit fbd4f82 |
| LOOP-04 (EMT prose + tables) | Headings/prose/lists/table in source order; semantic table in a labelled focusable overflow wrapper; no EMT-only renderer | ✅ Automated (markup/CSS hooks) | `tests/subject_loop_roundtrip.py#test_emt_lesson_semantic_table`, `_medium_emt` in the shared matrix; manual 320px/200% check owed at the human pass |
| LOOP-05 (fourth subject by configuration) | A fourth profile loads from temporary settings, completes the SAME shared driver with no production edit; no subject-id dispatch in application code | ✅ Automated | `tests/subject_loop_roundtrip.py#test_fourth_profile_is_configuration_only`, `#test_four_subjects_share_one_guided_loop` (fourth row), `#test_no_subject_dispatch_in_surfaces`; commits a6fdba6, 0ed3783 |
| D-01..D-04 (profile data policy) | Explicit-id/known/conservative/mixed-refusal selection; only the id crosses a client boundary; CLI/API/reader/resumed sessions resolve one id through the same selector; unknown/mixed fail before writes without path disclosure; resume uses the stored snapshot | ✅ Automated | `tests/subject_loop_roundtrip.py#test_profile_id_wired_through_clients`, `#test_only_id_crosses_client_boundary`, `#test_unknown_and_mixed_fail_before_writes`, `#test_resume_uses_stored_snapshot_with_explicit_id`; commit 941c907 |
| D-05..D-08 (semantic media seam) | Stable sequential data-code-block ids without reparse; local presentation-only math; reader renders byte-identical without the capability | ✅ Automated | `tests/lesson_code_roundtrip.py#test_runnable_page_contract`, `tests/math_offline_roundtrip.py#test_profile_snapshot_drives_the_presentation_seam`; commits cee3d18, fbd4f82 |
| D-09..D-11 (one runner, server gating, zero Run evidence) | Lesson execution and check execution share `run_source()` + bounds/tree cleanup; every gate before invocation; observation payload has no correctness authority; Run changes no session/evidence state | ✅ Automated | `tests/lesson_code_roundtrip.py` (one-runner proof via `test_run_cases_retains_phase5_contract`; zero-evidence delta; refusal matrix); commits fbd4f82 |
| D-12..D-15 (EMT semantics + four-profile proof) | Four profiles traverse one table-driven driver; only medium/type/verifier/response vary; each fixture orders context → action → targeted feedback → retry → explanation | ✅ Automated | `tests/subject_loop_roundtrip.py#test_four_subjects_share_one_guided_loop` + `run_subject_case`; fixtures/subject_loop_{emt,math,cs}.md; commit 0ed3783 |
| 09-UI-SPEC runnable-code contract | data-code-block identity, visible labels, exact ready/loading/completed/timeout/truncated/request-error/refusal copy, persistent role=status, non-live labelled streams, edit retention, independent block state, focus/escape hooks, reduced-motion and narrow/zoom CSS hooks | ✅ Automated (source/DOM/payload assertions) | `tests/lesson_code_roundtrip.py`; manual keyboard/320px/200%/assistive pass owed (09-VALIDATION.md) |

## Open items (human pass at phase close)

| Item | Acceptance check | Owner |
|---|---|---|
| 09-03 KaTeX supply-chain approval | A human replies `approved katex=0.18.4` (or refuses) — the checkpoint is never auto-approved | Human (PENDING — recorded in 09-03-SUMMARY.md and 09-VERIFICATION.md) |
| Manual accessibility/responsive matrix | 320px/200%, keyboard-only flow, assistive table/MathML, light/dark, reduced-motion, network-unplugged packaged page, one wrong → hint → retry flow per shipped subject | Human (09-VALIDATION.md) |

**UAT status: COMPLETE for all machine-checkable rows — 11 rows closed by
automated evidence; 1 human gate (KaTeX approval) and the manual
accessibility/responsive matrix remain open.**
