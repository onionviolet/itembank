---
phase: 16C
slug: strategies-notes-prototype-convergence
# status lifecycle: draft (seeded by plan-phase) -> validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-15
planner_filled: 2026-08-15
---

# Phase 16C Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded from `16C-RESEARCH.md` section "Validation Architecture". The
> Per-Task Verification Map below is filled by the planner against the nine
> 16C plans; the final plan's closure task finalizes the Status column,
> replaces the Estimated runtime placeholder with a measured figure, and
> resolves the sign-off boxes, the same closure pattern 16A-10 and 16B-11 set.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | None. Direct-execution Python scripts, this project's established convention (not pytest, not unittest) |
| **Config file** | none. See the `tests/*_roundtrip.py` and `tests/*_tracer.py` convention; every test file defines its own local `fail(msg)` helper |
| **Quick run command** | `python tests/<new_test_file>.py` for whichever single new or extended test file the task adds |
| **Full suite command** | the CI invocation in `.github/workflows/ci.yml`, confirmed verbatim by the planner before any verify step cites it (16B-RESEARCH precedent); local equivalent `for t in tests/*.py; do python "$t" || exit 1; done` |
| **Estimated runtime** | Unknown for the new 16C files. Do not record a figure until one has been measured on this machine. The 16C-09 closure task replaces this cell with the measured full-suite figure and names the machine and Python version. |

---

## Sampling Rate

- **After every task commit:** the specific new or changed test file the
  task's verify step names, plus `python itembank.py guard .` on any task that
  touches `fixtures/` or note-content-bearing files (Pitfall 8: real note
  content never enters the repository).
- **After every plan wave:** every new 16C test file so far, plus
  `python tests/evidence_roundtrip.py` (the evidence store gains additive
  event types) and `python tests/lesson_roundtrip.py` (the trio reads lesson
  parsing), both shipped.
- **Evidence additivity, after every task that touches `evidence.py`:** the
  byte-identical old-log fixture must pass: an evidence log written before
  16C parses identically, and a reader meeting an unknown event type
  skip-and-warns rather than failing (16C-RESEARCH Pattern 3).
- **Precedence composition, after every task that touches the resolver:**
  re-run the 16B conflict fixture alongside the 16C extension so the two
  contracts never diverge (16B-UI-SPEC decision D8; Pitfall 10).
- **Before `/gsd-verify-work`:** full suite green, the cross-subject suite
  tracer green, and `python itembank.py guard .` reporting `0 offending
  files`.
- **Freeze gate:** no 16C freeze record is written on a red cross-subject
  suite, a missing or rejecting human review, an unresolved precondition
  divergence from the 14B, 16A, or 16B plan text or freeze records, an open
  13.9 A9 closure, or a skipped prototype (trio or A/B/C tracer) with no
  recorded judgment (mirrors 14A-04 Task 4, 14B-06, 15A-06, 15B-07, 16A-10,
  and 16B-11).
- **Max feedback latency:** to be measured, not asserted.

---

## Phase Requirements -> Test Map

| Req ID | Behavior | Automated Command | File |
|--------|----------|-------------------|------|
| NOTE-01 | Note record carries every required field; an anchor invalidated by a lesson revision keeps the objective attachment and flags the broken selector with a relocation state; authored pre-highlighting yields zero evidence and zero learner ownership | `python tests/note_schema_roundtrip.py` | Wave 0, created by 16C-02 |
| NOTE-02 | Source-backed review promotes one synthetic note; the unreviewed note stays learner-private and non-authoritative; no silent path from note to source, lesson, key, score, or mastery | `python tests/note_promotion_roundtrip.py` | Wave 0, created by 16C-06 |
| NOTE-03 | A fictional proof with a rubric reads as pending evidence until a scripted human mark settles it; a non-human marker is refused (composes shipped `mark_event`) | `python tests/note_promotion_roundtrip.py` | Wave 0, created by 16C-06 |
| STRATEGY-01 | Each of the four registered strategies declares its full contract; a strategy marked unavailable falls back to continuous reading | `python tests/strategy_registry_roundtrip.py` | Wave 0, created by 16C-03 |
| STRATEGY-02 | The conflict matrix resolves toward the higher layer with 16B's copy verbatim and a stated reason; no runtime-authority setting changes mid-sitting; the fixture extends 16B's, never duplicates it | `python tests/strategy_precedence_roundtrip.py` | Wave 0, created by 16C-05 |
| GRAPH-03 | A missing denominator reports indeterminate; a pending prose mark stays pending; a version-split objective reads unknown on the new identity; no aggregate completion, mastery, or readiness score string appears anywhere in output; Retrievability never renders as a percentage | `python tests/progress_claim_roundtrip.py` | Wave 0, created by 16C-04 |
| Trio (STYLE-DISCIPLINE binding order) | One parse feeds three projections (notebook page, Cornell, concept map); each validator fails its deliberately broken fixture (a cue without notes, an unlabelled edge, an anchor to a moved block); each output degrades to coherent plain Markdown | `python tests/note_trio_roundtrip.py` | Wave 0, created by 16C-07 |
| UPGRADE-01 | The eleven-item baseline audit runs first over a synthetic pre-13.5 lesson; the enhancement lands as a bounded diff with identity and source history preserved | `python tests/legacy_upgrade_roundtrip.py` | Wave 0, created by 16C-08 |
| UPGRADE-02 | A scripted upgrade touching a synthetic item's keyed answer halts for explicit assessment review | `python tests/legacy_upgrade_roundtrip.py` | Wave 0, created by 16C-08 |
| Freeze gate | All fixtures above in one pass over the four synthetic subjects, plus prototype A/B/C success-gate assertions, plus `python itembank.py guard .` reporting 0 offenders, plus the evidence-log additivity check | `python tests/cross_subject_suite_tracer.py` | Wave 0, created by 16C-09 |

---

## Wave 0 Gaps

- [ ] `fixtures/note_strategy_corpus.py` (shared four-subject synthetic
      generator; fictional content only, fixed seed, guard-green)
- [ ] all eight test files named above
- [ ] Framework install: none, stdlib only

---

## Per-Task Verification Map

> Filled by the planner against the nine 16C plans on 2026-08-15; one row per
> task, columns matching 16B-VALIDATION.md. Plan 16C-09 Task 3 finalizes the
> Status column, replaces the Estimated runtime placeholder with a measured
> figure, and resolves the sign-off boxes, the same closure pattern 16A-10 and
> 16B-11 set.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 16C-01-T1 | 16C-01 | 1 | GRAPH-03, NOTE-01..03, STRATEGY-01..02, UPGRADE-01..02 | T-16C-01-01, -02, -03, -05, -06 | A missing module, a withheld freeze, an unresolved upstream precondition, an unwalked 13.9, or a moved shipped surface halts the wave by name; baselines are taken before any 16C edit | integration | `python -c "…assert journal.ENTRY_STATES…len(evidence.KNOWN_EVENT_TYPES)==14…print('16C preconditions match')"` (plan 16C-01 verify block, verbatim) | n/a, inline | ⬜ pending |
| 16C-01-T2 | 16C-01 | 1 | NOTE-01 | T-16C-01-04 | A held user decision (D-12.6-5 placement and Evidence prominence) is recorded with a named option id, never silently defaulted | manual-only | none, blocking checkpoint | n/a | ⬜ pending |
| 16C-02-T1 | 16C-02 | 2 | NOTE-01 | T-16C-02-01 | Fictional-only deterministic corpus written to caller directories; the repository stays guard-green | unit | `python -c "…build_all…print('corpus ok')" && python itembank.py guard .` | ❌ Wave 0 | ⬜ pending |
| 16C-02-T2 | 16C-02 | 2 | NOTE-01 | T-16C-02-02, -03, -04, -05 | Closed vocabularies raise on unknowns; a broken anchor keeps its objective flagged, never auto-relocated; authored pre-highlighting yields zero events and zero ownership | unit + fixture | `python tests/note_schema_roundtrip.py && python schema_validate.py --all schemas` | ❌ Wave 0 | ⬜ pending |
| 16C-02-T3 | 16C-02 | 2 | NOTE-01 | T-16C-02-01 | A stray note document outside fixtures/ fails guard by name through one additive marker | integration | `python tests/note_schema_roundtrip.py && python tests/guard_roundtrip.py && python itembank.py guard .` | ❌ Wave 0 | ⬜ pending |
| 16C-03-T1 | 16C-03 | 2 | STRATEGY-01 | T-16C-03-01, -02, -04 | Four data-record contracts with content-free evidence effects; an unknown, unavailable, or disallowed strategy falls back to continuous reading and raises nothing | unit + fixture | `python tests/strategy_registry_roundtrip.py` | ❌ Wave 0 | ⬜ pending |
| 16C-03-T2 | 16C-03 | 2 | STRATEGY-01 | T-16C-03-02, -03 | The picker renders only the three row classes, never a fifth option, and the fallback row states its sentence with continuous reading preselected | unit | `python tests/strategy_registry_roundtrip.py` | ❌ Wave 0 | ⬜ pending |
| 16C-04-T1 | 16C-04 | 2 | GRAPH-03 | T-16C-04-02, -03, -04 | The nine-field tuple validates settlement; a missing denominator reads indeterminate; pending stays pending; a version split reads unknown with zero transfer | unit + fixture | `python tests/progress_claim_roundtrip.py` | ❌ Wave 0 | ⬜ pending |
| 16C-04-T2 | 16C-04 | 2 | GRAPH-03 | T-16C-04-01 | The rendered output carries no percent character, no aggregate row, and seven separate dimension labels; enrichment never changes a required denominator | unit + fixture | `python tests/progress_claim_roundtrip.py` | ❌ Wave 0 | ⬜ pending |
| 16C-05-T1 | 16C-05 | 3 | STRATEGY-02 | T-16C-05-01, -02, -03, -04 | The collector calls the one 16B function, conflicts carry its sentence exactly, no second precedence implementation exists, and a sitting locks preference changes out | unit + fixture | `python tests/strategy_precedence_roundtrip.py && python tests/strategy_registry_roundtrip.py` | ❌ Wave 0 | ⬜ pending |
| 16C-05-T2 | 16C-05 | 3 | STRATEGY-02 | T-16C-05-01, -02 | The STRATEGY-02 matrix runs as appended CONFLICT_CASES rows inside 16B's own fixture, including a preference losing to runtime authority | integration | `python tests/mode_layer_roundtrip.py && python tests/strategy_precedence_roundtrip.py` | ✅ exists, extended | ⬜ pending |
| 16C-06-T1 | 16C-06 | 3 | NOTE-02, NOTE-03 | T-16C-06-01, -04 | Two additive content-free event types through the one writer; pre-16C logs byte- and view-identical to the recorded baselines; unknown types still skip-and-warn | integration | `python tests/note_promotion_roundtrip.py && python tests/evidence_roundtrip.py` | ❌ Wave 0 | ⬜ pending |
| 16C-06-T2 | 16C-06 | 3 | NOTE-02 | T-16C-06-02 | Promotion blocks on unsourced claims with a stated count, stops on conflict, accepts only as a derived cited copy, and an unreviewed note stays private and inert | integration | `python tests/note_promotion_roundtrip.py` | ❌ Wave 0 | ⬜ pending |
| 16C-06-T3 | 16C-06 | 3 | NOTE-03 | T-16C-06-03, -05 | An artifact reads pending until a human mark; a model marker raises; a proposal never settles; deletion is honest and leaves the log byte-identical | integration (composes shipped mark_event) | `python tests/note_promotion_roundtrip.py && python tests/evidence_roundtrip.py` | ❌ Wave 0 | ⬜ pending |
| 16C-07-T1 | 16C-07 | 4 | NOTE-01, STRATEGY-01 | T-16C-07-02 | parse_lesson and parse_terms called exactly once across six renders; no projection opens a file; every output coherent plain Markdown | integration | `python tests/note_trio_roundtrip.py && python tests/lesson_roundtrip.py` | ❌ Wave 0 | ⬜ pending |
| 16C-07-T2 | 16C-07 | 4 | NOTE-01 | T-16C-07-04 | Each broken fixture fails exactly its own check with the locked refusal sentence, and the plain form always renders beside the refusal | unit + fixture | `python tests/note_trio_roundtrip.py && python itembank.py guard .` | ❌ Wave 0 | ⬜ pending |
| 16C-07-T3 | 16C-07 | 4 | NOTE-01, NOTE-02, STRATEGY-01 | T-16C-07-01, -03, -05 | Gates A, B, C: no draft loss and no key in any projection; a wrong claim stays labeled and unpromotable; relocation never auto-applies and ownership survives export | integration (tracer) | `python tests/note_trio_roundtrip.py` | ❌ Wave 0 | ⬜ pending |
| 16C-08-T1 | 16C-08 | 5 | UPGRADE-01 | T-16C-08-02, -03 | Eleven audit rows in fixed order, unavailable records read plan-text stand-in, and the module writes nothing | unit + fixture | `python tests/legacy_upgrade_roundtrip.py && python itembank.py guard .` | ❌ Wave 0 | ⬜ pending |
| 16C-08-T2 | 16C-08 | 5 | UPGRADE-01 | T-16C-08-03, -04 | Cosmetic and reasonless changes are skipped with the locked sentence; a cannot-express enhancement links a derived projection with untouched original bytes | unit + fixture | `python tests/legacy_upgrade_roundtrip.py` | ❌ Wave 0 | ⬜ pending |
| 16C-08-T3 | 16C-08 | 5 | UPGRADE-02 | T-16C-08-01, -05 | A keyed-answer change halts with the locked sentence, two affordances, no diff, no override, untouched bytes; skill mirrors stay byte-identical | integration | `python tests/legacy_upgrade_roundtrip.py && diff -rq .agents/skills .claude/skills` | ❌ Wave 0 | ⬜ pending |
| 16C-09-T1 | 16C-09 | 6 | all eight | T-16C-09-02, -03, -04, -05, -06 | Nine scenarios over four subjects in one measured pass; 13.9 closure checked directly with a named halt; every figure measured | integration (tracer) | `python tests/cross_subject_suite_tracer.py && python itembank.py guard .` | ❌ Wave 0 | ⬜ pending |
| 16C-09-T2 | 16C-09 | 6 | all eight | T-16C-09-01 | A human, not an agent, judges whether the contract copy is legible and honest | manual-only | none, blocking checkpoint | n/a | ⬜ pending |
| 16C-09-T3 | 16C-09 | 6 | all eight | T-16C-09-02, -03, -05 | The freeze record describes the re-run tree or names the withholding leg; the two headings are mutually exclusive | integration | `python -c "…assert frozen != withheld…print('freeze record shape ok:', …)"` (plan 16C-09 verify block, verbatim) | n/a, inline | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Sign-Off

- [ ] Cross-subject missing-feature suite green in one pass
- [ ] Guard reports 0 offending files
- [ ] Evidence-log additivity fixture green
- [ ] Human contract-legibility review recorded in `16C-REVIEW.md`
- [ ] `16C-FREEZE.md` written with the ROADMAP-required scope statement, or a
      named withholding
