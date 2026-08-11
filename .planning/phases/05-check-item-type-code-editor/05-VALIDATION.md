---
phase: 5
slug: check-item-type-code-editor
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-08
---

# Phase 5 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python stdlib for runtime/API (direct script execution) + a JS test runner for the CM6 editor behaviours (ruling 16, RESOLVED 2026-08-11) |
| **Config file** | none |
| **Quick run command** | `python tests/check_roundtrip.py` + `node --test tests/js/` |
| **Full suite command** | `for f in tests/*_roundtrip.py; do python "$f" || exit 1; done && node --test tests/js/` |
| **Estimated runtime** | ~20 seconds quick (the timeout cases spend real wall-clock), ~80 seconds full |

---

## Sampling Rate

- **After every task commit:** Run `python tests/check_roundtrip.py`
- **After every plan wave:** Run the full suite
- **Before `/gsd-verify-work`:** Full suite must be green **on Windows as well as CI Linux** — see
  the manual table below; CI runs `ubuntu-latest` only
- **Max feedback latency:** 80 seconds

---

## Per-Task Verification Map

*Filled by the planner on 2026-08-08. One row per task, mapped to a CODE-xx requirement.*

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 05-01-T1 | 05-01 | 1 | CODE-01 | T-5-10 | The one-way fingerprint field set is confirmed by a human before any `[HASH:]` can be written from it | checkpoint:decision | none — blocking checkpoint | n/a | ⬜ pending |
| 05-01-T2 | 05-01 | 1 | CODE-02 | T-5-10 | The one-way storage shape for the learner's source is confirmed before the append-only log is written to | checkpoint:decision | none — blocking checkpoint | n/a | ⬜ pending |
| 05-01-T3 | 05-01 | 1 | CODE-01, CODE-02, CODE-04, CODE-05 | T-5-01, T-5-02, T-5-03, T-5-05, T-5-06, T-5-08, T-5-10 | Execution happens before the scorer and never inside it; the versioned public interaction contract validates declarative renderer configuration; source/version/result/evidence stay associated while runtime.score_response remains sole grader | integration (HTTP end-to-end) | `python tests/check_roundtrip.py` | ❌ created by this task | ⬜ pending |
| 05-02-T1 | 05-02 | 2 | CODE-04 | T-5-02 | Output past the cap fails the case and triggers the shared kill immediately; the drain keeps reading so the child never blocks on a full pipe | integration | `python tests/check_kill_roundtrip.py` | ❌ created by this task | ⬜ pending |
| 05-02-T2 | 05-02 | 2 | CODE-04, CODE-05 | T-5-03, T-5-04 | The Windows kill goes through a job object with kill-on-close, with the process-tree fallback behind it; the accepted spawn window is written into the source | integration (platform-guarded) | `python tests/check_kill_roundtrip.py` | ✅ | ⬜ pending |
| 05-02-T3 | 05-02 | 2 | CODE-04 | T-5-03, T-5-11 | A grandchild that inherited the group or job stops writing when the runner returns; a failing test leaks no process | integration | `python tests/check_kill_roundtrip.py` | ✅ | ⬜ pending |
| 05-03-T1 | 05-03 | 2 | CODE-04 | T-5-13 | Both bounds are schema-ranged, so an absurd value is rejected before any submit can reach a subprocess with it | unit (CLI subprocess) | `python tests/config_roundtrip.py` | ✅ | ⬜ pending |
| 05-03-T2 | 05-03 | 2 | CODE-01, CODE-02 | T-5-12 | The agent submit path cannot reach the scorer for a `check` item without the runner having run first | integration (CLI subprocess) | `python tests/check_roundtrip.py` | ✅ | ⬜ pending |
| 05-03-T3 | 05-03 | 2 | CODE-04, CODE-05 | T-5-07, T-5-08, T-5-14 | Execution is refused by default on both routes when the daemon is network-bound; the refusal is decided before the runner and leaks no path | integration (daemon HTTP) | `python tests/check_roundtrip.py` | ✅ | ⬜ pending |
| 05-04-T1 | 05-04 | 3 | CODE-04 | T-5-03, T-5-04, T-5-15 | The Windows kill is executed on Windows rather than reasoned about; the escape rate is measured over 50 runs | manual — CI is `ubuntu-latest` only | none | n/a | ⬜ pending |
| 05-04-T2 | 05-04 | 3 | CODE-04, CODE-05 | T-5-15, T-5-16 | The measurement is recorded with its environment and sample size, and states no claim beyond the observed rate | doc gate | `grep -iqE '(out of 50\|of 50 runs)' .planning/phases/05-check-item-type-code-editor/05-SPIKE-RESULT.md` | ❌ created by this task | ⬜ pending |
| 05-05-T1 | 05-05 | 3 | CODE-03 | T-5-18 | Per-case actual output reaches both surfaces from the one run that produced the score; case material never reaches the page before the verdict | integration (daemon HTTP) | `python tests/check_roundtrip.py` | ✅ | ⬜ pending |
| 05-05-T2 | 05-05 | 3 | CODE-03, CODE-05 | T-5-17, T-5-21 | Authored text renders as text content, not markup; the honest-limits line is one constant with two readers | source assertion on rendered HTML | `python tests/check_roundtrip.py` | ✅ | ⬜ pending |
| 05-05-T3 | 05-05 | 3 | CODE-02, CODE-03 | T-5-20 | Semantic labels, focus order, and Enter/Space activation provide non-pointer parity; browser and agent paths share response/version, sole-scorer verdict, observations, and evidence semantics | integration + JS test runner + source assertion | `python tests/check_roundtrip.py` + `node --test tests/js/` (keyboard behaviours executed, not source-read; the 500-line pixel pass stays manual at 05-07-T3) | ✅ | ⬜ pending |
| 05-06-T1 | 05-06 | 4 | CODE-02, CODE-03 | T-5-22, T-5-24, T-5-28 | Submitted source is the learner prediction/action; ordered case-index/reason observations provide bounded targeted feedback without rerunning code or deriving another verdict | integration + source assertion | `python tests/check_roundtrip.py` | ✅ | ⬜ pending |
| 05-06-T2 | 05-06 | 4 | CODE-05 | T-5-07, T-5-23, T-5-25 | A page that cannot run code renders no field and scores nothing; each of three causes has its own sentence and next step | source assertion on rendered HTML | `python tests/check_roundtrip.py` | ✅ | ⬜ pending |
| 05-07-T1 | 05-07 | 5 | CODE-02, CODE-03 | T-5-10, T-5-18 | The published versioned interaction envelope/config/response/result schema validates; a non-page consumer submits through /api/submit to the same scorer and evidence semantics | schema + protocol validation | `python tests/check_roundtrip.py` and `python tests/protocol_roundtrip.py` | ✅ | ⬜ pending |
| 05-07-T2 | 05-07 | 5 | CODE-05 | T-5-26 | The honest-limits statement is provably one string in both required places, and the claim-word gate runs in the suite with exact per-file counts | automated gate | `python tests/check_roundtrip.py` | ✅ | ⬜ pending |
| 05-07-T3 | 05-07 | 5 | CODE-02, CODE-03, CODE-05 | T-5-27 | A safety promise is caught by reading, and a keyboard-only learner proves focus/activation plus response-verdict-evidence-feedback parity end to end | automated (JS runner, ruling 16) + manual checkpoint — the real-browser keyboard-only pass stays manual; the DOM-level keyboard behaviours are executed by `node --test tests/js/` in CI | `node --test tests/js/` + named manual checkpoint in `05-VALIDATION.md` | n/a | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

**Sampling continuity:** no three consecutive tasks lack an automated verify. The two
longest manual stretches are 05-01-T1/T2 (two blocking decision checkpoints, immediately
followed by the tracer's full automated verify) and 05-04-T1 (a manual pass whose very next
task carries a doc gate).

**Threat IDs** are defined in each plan's own `<threat_model>` block; the register is
phase-wide and consistently numbered across all seven plans.

---

## Wave 0 Requirements

*Refined by the planner: the single test file and single fixture bank originally listed
here are split in two, for two stated reasons. The test file splits along the CI boundary —
`check_roundtrip.py` covers format, scoring, evidence and rendered-page assertions and runs
identically everywhere, while `check_kill_roundtrip.py` carries the platform-guarded bound
and kill assertions — which also lets plans 05-02 and 05-03 run in the same wave without
touching the same file. The fixture bank splits so that `fixtures/check_bank.md` stays
lint-clean and can therefore back a zero-errors lint assertion, with the deliberately
invalid items in their own file, matching the existing `sample_bank.md` / `broken_bank.md`
precedent.*

- [ ] `tests/check_roundtrip.py` — new file (plan 05-01 task 3): format contract, scoring
      identities, the end-to-end HTTP submit, evidence shape, both submit paths agreeing,
      renderer-independent interaction contract/result fixtures, stable case observations,
      keyboard/pointer/agent parity, the network and language refusals, rendered-page
      assertions, item-schema validation, and the CODE-05 identity and claim-word gate
- [ ] `tests/check_kill_roundtrip.py` — new file (plan 05-02 task 1): the deadline, the
      output cap and its early kill, both Windows kill paths, and the grandchild case.
      Windows-specific assertions are platform-guarded so the file passes on Linux CI
- [ ] `fixtures/check_bank.md` — new synthetic fixture, **lint-clean**: a two-case passing
      item, a three-case mixed pass/fail item, an item whose reference solution never
      terminates, an item whose reference solution floods stdout past the cap, and an item
      using `[MATCH: regex]`
- [ ] `fixtures/broken_check_bank.md` — new synthetic fixture, **deliberately invalid**: an
      item naming a language absent from the allowlist (`item.check_lang_unknown`, error)
      and an item with a single `CASE)` line (`item.check_too_few_cases`, warning)
- [ ] `fixtures/grandchild_spawner.py` — the grandchild fixture (plan 05-02 task 3), with no
      platform branch of its own and no call that would detach it from the group or job the
      runner created; the test's cleanup runs in a `finally:` block so a failing assertion
      leaves no process behind

No framework install — the project forbids one.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| The Windows process-tree kill actually kills a grandchild | CODE-04 | **CI is `ubuntu-latest` only.** The Job Object path cannot be exercised by CI at all; it can only be run on the target Windows 11 machine, matching the `01-01-PLAN.md` spike precedent | On Windows: run `python tests/check_roundtrip.py`, then confirm with `tasklist` that no orphaned `python.exe` from the grandchild fixture survives the timeout |
| The `CREATE_SUSPENDED` race window | CODE-04 | CPython's Windows `_execute_child` closes the child's thread handle before returning (`bpo-1677688`), so a race-free assign-then-resume is not reachable through `subprocess.Popen`. Whether the residual window ever loses a grandchild in practice is empirical | Run the grandchild fixture repeatedly (50 iterations) on Windows and confirm zero escapes; record the observed rate rather than claiming zero |
| Gutter-to-line pixel alignment at 500 lines | CODE-03 | Sub-pixel font-metric drift is a visual judgment | Paste 500 lines into the editor, scroll to the bottom, confirm line 500 in the gutter sits on line 500 of the editor document |
| The editor's tab and shift-tab behavior preserves usable undo | CODE-03 | Undo-stack behavior differs per browser and is not scriptable here | Type, Tab, Shift-Tab, then Ctrl-Z repeatedly and confirm the document walks back sensibly |
| Keyboard-only submission reaches equivalent feedback | CODE-02, CODE-03 | Focus order, semantic announcement, and actual non-pointer readability require a browser and human observation | Without mouse/trackpad, focus the labelled source field, enter source, activate Check with Enter and Space on separate runs, reach verdict/case feedback, and compare version/response/verdict/observations/evidence semantics with `/api/submit` |
| No documentation anywhere claims sandboxing | CODE-05 | Partly automatable (the grep), but judging whether some *other* sentence overclaims safety is a reading task | Run the grep for `sandbox` / `isolat` / `contain`, then read the `check` sections of `SPEC`, README, and the UI copy for any implied safety claim |

---

## Interactive Contract Amendment Source Audit

| Source | Item | Coverage | Proof |
|--------|------|----------|-------|
| GOAL | Renderer-independent interactive-item contract in Phase 5 goal / Success Criterion 5 | COVERED | 05-01-T3 publishes the versioned contract/result seam; 05-05-T3 proves non-pointer and agent parity; 05-07-T1/T3 validate it automatically and manually |
| REQ | CODE-01 through CODE-05 | COVERED | Existing seven-plan mapping remains intact; amendments strengthen CODE-02/CODE-03 without adding a grader or changing execution bounds/documentation scope |
| RESEARCH | Runner-before-scorer, two submit paths, no pre-answer key leakage, stdlib-only | COVERED | 05-01/05-05/05-07 keep `runtime.score_response()` authoritative, exercise browser plus `/api/submit`, validate declarative config, and install no package |
| CONTEXT | D-01/D-12/D-13/D-14 interaction boundary | COVERED | Raw source stays the D-12 response; results vector reaches D-01's sole scorer; source/version persist with evidence; both D-14 submit paths share the contract |
| CONTEXT | Deferred hints/model feedback and partial credit | EXCLUDED | Phase 6/8 remain responsible; Phase 5 exposes stable observations only |
| ROADMAP | Canvas/SVG/manipulative renderer types | EXCLUDED | Explicitly assigned to Phase 06.1; Phase 5 proves the reusable envelope with `check` only |
| BENCHMARKS | Brilliant and other competitors | COVERED AS CONSTRAINT | Interaction benchmarks only; no proprietary prompt, copy, markup, styling, or content is copied |

No source item is missing, and no additional Phase 5 plan is required.

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 80s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
