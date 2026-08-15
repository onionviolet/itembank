---
phase: 16A
slug: semantic-capability-activity-contract
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-15
---

# Phase 16A Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded from `16A-RESEARCH.md` section "Validation Architecture". The planner
> fills the Per-Task Verification Map once plan and task IDs exist.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | None. Direct-execution Python scripts, this project's established convention (not pytest, not unittest) |
| **Config file** | none. See the `tests/*_roundtrip.py` and `tests/*_tracer.py` convention; every test file defines its own local `fail(msg)` helper |
| **Quick run command** | `python tests/<new_test_file>.py` for whichever single new or extended test file the task adds |
| **Full suite command** | `for t in tests/*.py; do python "$t" || exit 1; done` |
| **Estimated runtime** | Unknown for the new 16A files. Do not record a figure until one has been measured on this machine. |

---

## Sampling Rate

- **After every task commit:** the quick run command for that task's specific
  new or changed test file, plus `python itembank.py guard .` on any task that
  touches `fixtures/`.
- **After every plan wave:** the full suite command.
- **Before `/gsd-verify-work`:** full suite green, the portable rich-lesson
  stress corpus tracer green, and `python itembank.py guard .` reporting
  `0 offending files`.
- **Freeze gate:** no 16A freeze record is written on a red stress-corpus
  tracer or a red adversarial suite (mirrors 14A-04 Task 4, 14B-06, 15A-06,
  and 15B-07).
- **Max feedback latency:** to be measured, not asserted.

---

## Phase Requirements -> Test Map

Seeded from `16A-RESEARCH.md`. The planner expands this into the Per-Task
Verification Map below.

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| CAP-01 | Every semantic teaching role parses and renders in both continuous reader and guided modes; an unknown optional semantic renders its fallback with a warning; an unknown required semantic fails safely | Tracer scenario over the stress corpus | `python tests/capability_stress_corpus_tracer.py` (new) | Wave 0 gap |
| CAP-02 | A declared capability's full support profile is inspectable; a capability with its renderer marked unavailable shows the static instructional path | Unit assertions over the capability registry plus one tracer scenario | `python tests/capability_stress_corpus_tracer.py` (new) | Wave 0 gap |
| CAP-03 | Two registered output modes (outline, glossary) compose from one stress-corpus lesson's shared schemas; one unregistered mode stays a named backburner catalog entry | Tracer scenario | `python tests/capability_stress_corpus_tracer.py` (new) | Wave 0 gap |
| ACTIVITY-01 | Every declared activity in the stress corpus carries all ten fields; one unsupported response form falls back to its declared static equivalent | Tracer scenario | `python tests/capability_stress_corpus_tracer.py` (new) | Wave 0 gap |
| ACTIVITY-03 | A scripted agent, a note, and an import each attempt to leak a key, invent a score, auto-grade prose, or edit a frozen sitting; every attempt is refused | Adversarial fixture calling real `runtime.py` and `evidence.py` functions | `python tests/assessment_authority_adversarial.py` (new) | Wave 0 gap |
| A11Y-02 | The localization fixture set (RTL, mixed code and math direction, CJK, combining marks, long strings, localized numbers and units) renders inside the stress corpus without corruption | Tracer scenario with byte-level assertions on preserved UTF-8 | `python tests/capability_stress_corpus_tracer.py` (new) | Wave 0 gap |
| PORT-01 | The stress corpus, opened outside the app with every derived HTML, index, and cache deleted, stays readable; core meaning, captions, citations, and fallbacks survive; derived views rebuild | Tracer scenario following the golden-parse-snapshot precedent | `python tests/capability_stress_corpus_tracer.py` (new) | Wave 0 gap |

---

## Per-Task Verification Map

Populated by the planner at plan time. The final 16A plan's freeze-gate task
updates the Status column and replaces the Estimated runtime placeholder above
with a measured figure.

| Plan | Task | Req ID | Behavior | Test Type | Automated Command | Assertion function | Status |
|------|------|--------|----------|-----------|-------------------|--------------------|--------|
| (planner fills) | | | | | | | |

---

## Wave 0 Requirements

Seeded from `16A-RESEARCH.md` Wave 0 Gaps; the planner confirms ownership per
plan and task. All 16A test infrastructure is new direct-execution Python
scripts beside the existing `tests/` set. No framework and no install step.

- [ ] `tests/capability_stress_corpus_tracer.py`, the freeze-gate tracer
  covering CAP-01, CAP-02, CAP-03, ACTIVITY-01, A11Y-02, and PORT-01 in one
  run, following `tests/three_domain_tracer.py`'s (14B) and
  `tests/file_fault_tracer.py`'s (14A) structure (`fail(msg)`, named
  `scenario_*()` functions, `main()`, a final `"TRACER: N passed, M skipped,
  0 failed"` line).
- [ ] `tests/assessment_authority_adversarial.py`, ACTIVITY-03's dedicated
  adversarial suite, calling real `runtime.py` and `evidence.py` functions.
- [ ] `fixtures/lesson_capability_corpus.py`, the synthetic stress-corpus
  generator (fictional content, fixed seed, following
  `fixtures/corpus_14b.py`'s convention), including the medical evolving-case
  fixture and the disputed-timeline fixture the freeze gate names by name.
- [ ] A golden-parse snapshot for the byte-identical additivity fixture,
  following `fixtures/lesson_golden_phase3_parse.json`'s shipped precedent,
  proving a bank or lesson using none of the new callout kinds parses
  unchanged.
- [ ] `capabilities.py` and its unit assertions (no pre-existing module covers
  a capability-profile registry).

*(No pre-existing test infrastructure covers this phase's seven requirements
directly; all listed gaps are new. The infrastructure the new tests call,
`runtime.py`, `evidence.py`, and `model.py`'s parsing, is shipped and
unchanged.)*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Freeze-gate legibility review | all seven | The freeze gate requires a human reviewer to judge that the stress corpus, capability profiles, activity declarations, refusals, and portability evidence are legible and correct; an agent never self-certifies its own contract | (planner fills with the final plan's how-to-verify steps) |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency measured, not asserted
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
