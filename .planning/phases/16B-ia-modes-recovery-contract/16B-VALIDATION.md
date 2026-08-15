---
phase: 16B
slug: ia-modes-recovery-contract
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-15
planner_filled: 2026-08-15
---

# Phase 16B Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded from `16B-RESEARCH.md` section "Validation Architecture". The
> Per-Task Verification Map below was filled by the planner against the eleven
> 16B plans on 2026-08-15. Plan 16B-11 Task 3 finalizes the Status column,
> replaces the Estimated runtime placeholder with a measured figure, and
> resolves the sign-off boxes, the same closure pattern 16A-10 Task 3 set.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | None. Direct-execution Python scripts, this project's established convention (not pytest, not unittest) |
| **Config file** | none. See the `tests/*_roundtrip.py` and `tests/*_tracer.py` convention; every test file defines its own local `fail(msg)` helper |
| **Quick run command** | `python tests/<new_test_file>.py` for whichever single new or extended test file the task adds |
| **Full suite command** | `for t in tests/*.py; do python "$t" || exit 1; done` |
| **Estimated runtime** | Unknown for the new 16B files. Do not record a figure until one has been measured on this machine. Plan 16B-11 Task 3 step 6 replaces this cell with the measured full-suite figure and names the machine and Python version. |

---

## Sampling Rate

- **After every task commit:** the quick run command for that task's specific
  new or changed test file, plus `python itembank.py guard .` on any task that
  touches `fixtures/`, `sample_course.py`, or `surfaces/cli.py`'s `cmd_guard`.
- **After every plan wave:** the full suite command.
- **Before `/gsd-verify-work`:** full suite green, the loop-interruption
  storyboard suite green, the route-parity check green, and
  `python itembank.py guard .` reporting `0 offending files`.
- **Route parity, after every task that touches `surfaces/daemon.py`:**
  re-run `python tests/daemon_roundtrip.py` so a new IA route never lands in one
  of the four parallel route structures without the others.
- **Settings additivity, after every task that touches
  `schemas/settings.schema.json` or `surfaces/settings.py`:** re-run
  `python tests/config_roundtrip.py` and re-verify the baseline recorded in
  `16B-PRECONDITION.md`.
- **Freeze gate:** no 16B freeze record is written on a red storyboard or
  interruption suite, a missing or rejecting human review, an unresolved
  precondition divergence from the 14A or 16A plan text, or a skipped walk stage
  with no recorded judgment (mirrors 14A-04 Task 4, 14B-06, 15A-06, 15B-07, and
  16A-10).
- **Max feedback latency:** to be measured, not asserted.

---

## Phase Requirements -> Test Map

| Req ID | Behavior | Automated Command | File |
|--------|----------|-------------------|------|
| FLOW-01 | Loops A through G each resume at an exact step boundary with a next justified action after interruption; an empty run states an outcome; tied loops order deterministically | `python tests/ia_storyboard_tracer.py` | Wave 0, created by 16B-10 |
| FLOW-02 | Reading, lesson, practice, feedback, and the next course action without reconstructing context, with the model backend disabled, through the one runtime and the one parser | `python tests/ia_storyboard_tracer.py` | Wave 0, created by 16B-10 |
| APP-01 | Course shelf with exact resume cues and attention states; two-course fixture with one corrupted course showing its last valid overview and plain-file access | `python tests/ia_route_roundtrip.py` | Wave 0, created by 16B-02, extended by 16B-04 |
| APP-02 | Identical routes and deep links across both layouts, explicit back semantics, anchor targets, and the three enumerated stability scenarios | `python tests/ia_route_roundtrip.py` | Wave 0, created by 16B-02, extended by 16B-05 |
| APP-03 | Offline help routed from named error codes; four additive settings groups; first-launch sample course and walkthrough reachable with no roots, no agent, and no network; mode-layer visibility | `python tests/ia_route_roundtrip.py`, `python tests/config_roundtrip.py`, `python tests/mode_layer_roundtrip.py`, `python tests/degraded_state_roundtrip.py` | Partial. `tests/config_roundtrip.py` ships; the other three are Wave 0 |

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 16B-01-T1 | 16B-01 | 1 | FLOW-01, FLOW-02, APP-01, APP-02, APP-03 | T-16B-01-01, -02, -03, -06, -09 | A withheld freeze, an unresolved upstream precondition, or a post-edit additivity baseline halts the wave by name | integration | `python -c "…assert journal.ENTRY_STATES…len(daemon.API_ROUTES)==12…print('16B preconditions match')"` (plan 16B-01 verify block, verbatim) | n/a, inline | ⬜ pending |
| 16B-01-T2 | 16B-01 | 1 | APP-01, APP-02 | T-16B-01-04, -05 | A one-way module-boundary decision is recorded with a named option id, never silently defaulted | manual-only | none, blocking checkpoint | n/a | ⬜ pending |
| 16B-02-T1 | 16B-02 | 2 | APP-02, APP-03 | T-16B-02-04, -05 | The new route joins the one dispatcher and the four parallel structures, so the loopback token gate covers it | integration (tracer) | `python tests/ia_route_roundtrip.py && python tests/daemon_roundtrip.py` | ❌ Wave 0 | ⬜ pending |
| 16B-02-T2 | 16B-02 | 2 | APP-03 | T-16B-02-01, -02, -06, -07 | No journal payload, no absolute path, and no invented percent reaches the Activity page | integration | `python tests/ia_route_roundtrip.py` | ❌ Wave 0 | ⬜ pending |
| 16B-02-T3 | 16B-02 | 2 | APP-02 | T-16B-02-03, -04, -05 | One dispatcher only, and the fixed-literal-before-regex order holds | integration | `python tests/ia_route_roundtrip.py && python tests/daemon_roundtrip.py` | ❌ Wave 0 | ⬜ pending |
| 16B-03-T1 | 16B-03 | 3 | APP-03 | T-16B-03-04, -07 | An unknown code is answered rather than refused, and no help page carries a path | unit | `python tests/ia_route_roundtrip.py` | ❌ Wave 0 | ⬜ pending |
| 16B-03-T2 | 16B-03 | 3 | APP-03 | T-16B-03-01, -02, -05 | A bounded code pattern refuses traversal at dispatch and no 404 body carries a path or a traceback | integration | `python tests/ia_route_roundtrip.py && python tests/daemon_roundtrip.py` | ❌ Wave 0 | ⬜ pending |
| 16B-03-T3 | 16B-03 | 3 | APP-03 | T-16B-03-03 | Help resolves with no network, no proxy, and no configured backend, and the structural scan is proven able to fail | integration | `python tests/ia_route_roundtrip.py` | ❌ Wave 0 | ⬜ pending |
| 16B-04-T1 | 16B-04 | 4 | APP-01 | T-16B-04-08 | Every course, name, and cue in the corpus is invented and no `.md` file is written | unit | `python -c "…build_corrupted_course…print(len(dirs), sorted(m.unreadable))"` plus `python itembank.py guard .` | ❌ Wave 0 | ⬜ pending |
| 16B-04-T2 | 16B-04 | 4 | APP-01 | T-16B-04-01, -02, -03, -05, -06, -07 | A record that will not parse yields a basename-only degraded card, never a partial record and never a percent | unit | `python tests/ia_route_roundtrip.py` | ❌ Wave 0 | ⬜ pending |
| 16B-04-T3 | 16B-04 | 4 | APP-01 | T-16B-04-01, -04 | The shelf renders one healthy card beside one degraded card, escapes every record value, and falls back to the shipped listing | integration | `python tests/ia_route_roundtrip.py && python tests/daemon_roundtrip.py` | ❌ Wave 0 | ⬜ pending |
| 16B-05-T1 | 16B-05 | 5 | APP-02 | T-16B-05-01, -02, -03 | Bounded id and closed area patterns refuse traversal at dispatch; an unknown course is a path-free 404 | integration | `python tests/ia_route_roundtrip.py && python tests/daemon_roundtrip.py` | ❌ Wave 0 | ⬜ pending |
| 16B-05-T2 | 16B-05 | 5 | APP-02 | T-16B-05-04, -05, -07, -08 | One route per object at every width; restoration is progressive enhancement with a stated noscript path | integration | `python tests/ia_route_roundtrip.py` | ❌ Wave 0 | ⬜ pending |
| 16B-05-T3 | 16B-05 | 5 | APP-02 | T-16B-05-03, -05 | A rename keeps the link, a dead anchor keeps the page, and a missing focus target has a real fallback | integration | `python tests/ia_route_roundtrip.py` | ❌ Wave 0 | ⬜ pending |
| 16B-06-T1 | 16B-06 | 6 | APP-03 | T-16B-06-02, -03, -06 | Four additive keys, every default restrictive, no path in any default, and the shipped validator accepts the schema | unit | `python -c "…sv.check_schema(s)…print('16B settings schema ok')"` (plan 16B-06 verify block, verbatim) | n/a, inline | ⬜ pending |
| 16B-06-T2 | 16B-06 | 6 | APP-03 | T-16B-06-01, -04, -07 | A pre-phase settings file is unchanged in every existing key and a bad value gets one of the six shipped codes | integration | `python tests/config_roundtrip.py` | ✅ exists, extended | ⬜ pending |
| 16B-06-T3 | 16B-06 | 6 | APP-03 | T-16B-06-05 | A preference nothing enforces says so where it is offered | integration | `python tests/config_roundtrip.py && python itembank.py config` | ✅ exists, extended | ⬜ pending |
| 16B-07-T1 | 16B-07 | 7 | APP-03 | T-16B-07-01, -03, -06 | A learner preference never wins over runtime authority or system safety, and no live-state collector exists | unit | `python tests/mode_layer_roundtrip.py` | ❌ Wave 0 | ⬜ pending |
| 16B-07-T2 | 16B-07 | 7 | APP-03 | T-16B-07-02, -04, -05 | A fixed layer renders read-only with no form control, and the shipped settings page is byte-unchanged by default | integration | `python tests/mode_layer_roundtrip.py && python tests/theme_roundtrip.py` | ❌ Wave 0 | ⬜ pending |
| 16B-07-T3 | 16B-07 | 7 | APP-03 | T-16B-07-01, -03 | Six named conflicts resolve upward with the exact locked sentence and three of them are a preference losing to a fixed layer | unit | `python tests/mode_layer_roundtrip.py` | ❌ Wave 0 | ⬜ pending |
| 16B-08-T1 | 16B-08 | 8 | FLOW-02, APP-03 | T-16B-08-01, -05, -06, -07, -08 | Four path shapes reduce to one basename; every banner carries a code, a help link, and a next action | unit | `python tests/degraded_state_roundtrip.py` | ❌ Wave 0 | ⬜ pending |
| 16B-08-T2 | 16B-08 | 8 | FLOW-02 | T-16B-08-02, -03, -04 | The locked card carries none of the content it withholds and nothing that reads as continuing a conversation | unit | `python tests/degraded_state_roundtrip.py` | ❌ Wave 0 | ⬜ pending |
| 16B-08-T3 | 16B-08 | 8 | FLOW-02, APP-03 | T-16B-08-01, -06 | Two degraded states render over HTTP with their help links followed and confirmed to resolve | integration | `python tests/degraded_state_roundtrip.py && python tests/ia_route_roundtrip.py` | ❌ Wave 0 | ⬜ pending |
| 16B-09-T1 | 16B-09 | 9 | APP-03 | T-16B-09-04, -05, -07, -08 | The sample course is fixed bytes, obviously synthetic, and cannot be committed; the guard stays green with it materialized | integration | `python itembank.py guard . && python tests/ia_route_roundtrip.py` | ❌ Wave 0 | ⬜ pending |
| 16B-09-T2 | 16B-09 | 9 | APP-03 | T-16B-09-01, -02, -03 | One mutating route, one allowed field, cross-origin refused, and a half-written state file reads as the default | integration | `python tests/ia_route_roundtrip.py && python tests/daemon_roundtrip.py` | ❌ Wave 0 | ⬜ pending |
| 16B-09-T3 | 16B-09 | 9 | APP-03 | T-16B-09-06, -07 | First launch works with nothing configured, and a walkthrough killed mid-step resumes at its recorded step | integration | `python tests/ia_route_roundtrip.py && python itembank.py guard .` | ❌ Wave 0 | ⬜ pending |
| 16B-10-T1 | 16B-10 | 10 | FLOW-01 | T-16B-10-05, -06 | Every step boundary resumes at the following step, an empty run states an outcome, and no next action carries a percent | unit | `python tests/ia_storyboard_tracer.py` | ❌ Wave 0 | ⬜ pending |
| 16B-10-T2 | 16B-10 | 10 | FLOW-01 | T-16B-10-04, -05, -07 | Resume is recomputed from a file read off disk after every in-memory reference is dropped | integration | `python tests/ia_storyboard_tracer.py` | ❌ Wave 0 | ⬜ pending |
| 16B-10-T3 | 16B-10 | 10 | FLOW-02 | T-16B-10-01, -02, -03 | With the backend unreachable, scoring, the authored hint ladder, evidence, and reports all run, and the served verdict equals the one scorer's | integration | `python tests/ia_storyboard_tracer.py` | ❌ Wave 0 | ⬜ pending |
| 16B-11-T1 | 16B-11 | 11 | FLOW-01, FLOW-02, APP-01, APP-02, APP-03 | T-16B-11-02, -03, -04, -05, -07 | Every figure is measured, every leg is marked, and no runtime-materialized state is untracked | integration | `for t in tests/*.py; do python "$t" \|\| exit 1; done` | ❌ Wave 0 | ⬜ pending |
| 16B-11-T2 | 16B-11 | 11 | FLOW-01, FLOW-02, APP-01, APP-02, APP-03 | T-16B-11-01, -05 | A human, not an agent, judges whether the contract is legible and honest | manual-only | none, blocking checkpoint | n/a | ⬜ pending |
| 16B-11-T3 | 16B-11 | 11 | FLOW-01, FLOW-02, APP-01, APP-02, APP-03 | T-16B-11-02, -06, -08 | The freeze record describes the tree it freezes, or names the leg that withheld it | integration | `python -c "…assert frozen != withheld…print('freeze record shape ok:', …)"` (plan 16B-11 verify block, verbatim) | n/a, inline | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/ia_route_roundtrip.py`, created by plan 16B-02 Task 1 and extended
      by plans 16B-03, 16B-04, 16B-05, 16B-08, and 16B-09. Covers APP-01,
      APP-02, APP-03.
- [ ] `tests/ia_storyboard_tracer.py`, created by plan 16B-10 Task 1. Covers
      FLOW-01 and FLOW-02.
- [ ] `tests/mode_layer_roundtrip.py`, created by plan 16B-07 Task 1. Covers the
      mode-layer precedence clause of the Phase 16B goal and shares its fixture
      shape with Phase 16C's `STRATEGY-02`.
- [ ] `tests/degraded_state_roundtrip.py`, created by plan 16B-08 Task 1. Covers
      the eight-state degraded matrix and the FLOW-02 locked-card clause.
- [ ] `fixtures/course_storyboard_corpus.py`, created by plan 16B-04 Task 1 and
      extended by plan 16B-10 Task 2. The shared synthetic fixture the route and
      storyboard suites both draw from.
- [ ] `sample_course.py`, created by plan 16B-09 Task 1. The bundled first-run
      content the APP-03 fixture needs.
- [ ] Framework install: none. Standard library only, no new dependency.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| The one-way module-boundary decision for the new IA module | APP-01, APP-02 | A published module path every later plan imports; `PLANNING-DIRECTIVES.md` section 2 rule 1 requires a stop for a decision other phases build against | Plan 16B-01 Task 2: present the three options with the recommended default, record the chosen option id and the answer verbatim under `## D-16B-2` |
| Whether nine routes, eight degraded sentences, twelve help entries, six attention chips, seven mode layers, the locked refusal card, the seven empty-outcome sentences, and the first-run walkthrough are legible and honest to a learner | FLOW-01, FLOW-02, APP-01, APP-02, APP-03 | A test proves a string is present; it cannot prove the string explains what happened to the person reading it. `PLANNING-DIRECTIVES.md` section 3a forbids an agent signing its own accepted recommendation | Plan 16B-11 Task 2, steps 1 through 11 in full, producing `16B-REVIEW.md` with one of the literal verdict words, a signature, and a date |
| The post-paint focus and scroll restoration after following a deep link | APP-02 | A Python test that drives a subprocess daemon observes served bytes, never focus after paint in a browser | Follow a `/course/<id>/learn#<anchor>` link in a real browser, confirm focus lands on the target heading clear of the sticky context line, then use the in-page Back control and confirm focus and scroll return to the prior position |
| Narrow-layout rendering of long course names, long root paths, long walkthrough step copy, and many-course and many-job overflow | APP-01, APP-02, APP-03 | Wrapping, scrolling, and clipping are rendering outcomes Phase 17A owns; 16B fixes the structural and copy contract only | Deferred to Phase 17A's same-flow three-direction visual comparison and accessibility QA; carried in the 16B freeze record's open items with Phase 17A named as owner |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency measured, not asserted
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
