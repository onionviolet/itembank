---
phase: 15B-quality-blueprint-acceptance
plan: 07
type: execute
wave: 7
depends_on: ["15B-06"]
files_modified:
  - tests/acceptance_tracer.py
  - fixtures/corpus_15b.py
  - .planning/phases/15B-quality-blueprint-acceptance/15B-TRACER-REPORT.md
  - .planning/phases/15B-quality-blueprint-acceptance/15B-REVIEW.md
  - .planning/phases/15B-quality-blueprint-acceptance/15B-FREEZE.md
  - .planning/phases/15B-quality-blueprint-acceptance/15B-DECISIONS.md
  - .planning/phases/15B-quality-blueprint-acceptance/15B-VALIDATION.md
autonomous: false
requirements: [ACTIVITY-02, RELIABILITY-03, AGENT-03]
estimate:
  tokens: 76000
  raw_tokens: 76000
  tasks: 3
  confidence: low
must_haves:
  truths:
    - "One synthetic cited blueprint, one drafted lesson treatment, and one drafted practice set are walked in a single tracer run from draft through all five ACTIVITY-02 gates to a journaled acceptance, and the exam-fidelity claim is False at every point before the fifth gate reports and True only after it."
    - "A mid-flow edit to a synthetic source marks its dependents stale and blocks acceptance by name until a rebind, migrate, supersede, or retain review is recorded, asserted in one continuous scenario rather than across two isolated unit cases."
    - "One migration proposal is accepted and a second is rejected through the reviewer path, with the live autonomy policy re-read at accept time, and a third proposal whose proposer equals the reviewer is refused with graph.migration_self_accept in the same run."
    - "A proposal over two attempts on one objective names its window, its denominator of two, and its uncertainty of sparse, and carries no key whose lowercase name contains mastery, completion, readiness, progress, percent, or score at any nesting depth."
    - "The whole operation replays from the operation journal alone, in a fresh process, with no chat transcript and no in-memory state: every accept_revision entry is found by reading journal.entries and its recorded state and message reproduce what the run did."
    - "The tracer measures rather than asserts: every duration, byte count, entry count, and denominator in 15B-TRACER-REPORT.md is a figure the run produced on the machine and Python version the report names, and no budget number appears that was not measured."
    - "No 15B freeze record is written on a red tracer, on a missing or rejecting human review, or on absent Phase 13.9 evidence. On any missing leg the file opens with a Freeze withheld section naming that leg, the string Frozen at 15B appears nowhere in it, and the phase stays open."
    - "The shipped runtime is unregressed: tests/scoring_roundtrip.py, tests/evidence_roundtrip.py, tests/audit_authoring_roundtrip.py, tests/audit_quality_roundtrip.py, tests/audit_coverage_roundtrip.py, and tests/audit_roundtrip.py each exit 0 as subprocesses before any 15B module is imported, and a red shipped suite skips every scenario rather than reporting passes."
  prohibitions:
    - statement: "The freeze record must not claim a leg that was not run; a leg that could not be executed is named as withheld rather than described as satisfied or omitted from the list."
      status: kept
      verification: flagged-unverified
    - statement: "An agent must not sign its own acceptance-quality review; the judgment that acceptance, rejection, and staleness dispositions are legible and correct is a human's, and a green tracer is not that judgment."
      status: kept
      verification: flagged-unverified
    - statement: "The tracer corpus must not contain, paraphrase, or be derived from real course material, real exam content, a real syllabus, a real learner's notes, or any real bank; the synthetic blueprint and its drafted treatments are fictional stand-ins whose only relationship to a real assessment is their shape."
      status: kept
      verification: flagged-unverified
  artifacts:
    - "tests/acceptance_tracer.py, the freeze-gate tracer, whose final line is TRACER: N passed, M skipped, 0 failed"
    - "fixtures/corpus_15b.py gains build_all_15b"
    - ".planning/phases/15B-quality-blueprint-acceptance/15B-TRACER-REPORT.md"
    - ".planning/phases/15B-quality-blueprint-acceptance/15B-REVIEW.md"
    - ".planning/phases/15B-quality-blueprint-acceptance/15B-FREEZE.md"
    - "15B-DECISIONS.md gains the dated D-15B-4 freeze-scope answer"
    - "15B-VALIDATION.md with its Per-Task Verification Map statuses updated, its runtime placeholder replaced by a measured figure, and its sign-off boxes resolved"
  key_links:
    - "The staleness scenario must edit a real fixture source file and recompute the live fingerprint through identity.object_fingerprint rather than passing two hand-written strings. Comparing two literals proves classify_staleness compares strings; editing a file and watching acceptance block proves the pipeline notices a real change, which is what RELIABILITY-03's Fixture sentence asks for."
    - "The replay scenario must run in a fresh subprocess that imports nothing the first run left in memory and reads only journal.entries. A replay inside the same process could pass by reading a module-level value the run happened to leave behind, which is a green test measuring nothing."
    - "shipped_suite_check() runs before any 15B module is imported, as subprocesses, and a red result skips every scenario rather than failing one. A phase tracer that reports passes while the shipped scorer is broken is worse than a red tracer, because it hides which layer moved."
    - "Task 3 re-runs the tracer rather than trusting Task 1's recorded result, because the review in Task 2 may have prompted a fix and a freeze record must describe the tree it is freezing rather than the tree that was tested."
---

<objective>
Run the phase's own freeze gate and either write the freeze or name the leg
that withheld it.

The ROADMAP Phase 15B freeze gate, quoted in full: "the lesson-plus-practice
acceptance tracer: one synthetic cited blueprint paired with one drafted lesson
treatment and one drafted practice set, walked from draft through all five
gates to journaled acceptance; the exam-fidelity claim appearing only after the
fifth gate; a mid-flow synthetic source edit marking dependents stale and
blocking acceptance until a recorded disposition; a migration proposal accepted
and a second one rejected through the reviewer path; and a sparse-evidence
proposal (two attempts on one objective) that names its window, denominator,
and uncertainty and refuses a mastery percentage, all replayed from the
operation journal."

This is the last plan of Phase 15B. It builds no new capability. It proves the
five it inherited, records what it measured, and either writes the freeze or
names the leg that withheld it.

Decisions already made, cited, and never re-derived here:

- **ROADMAP.md Phase 15B freeze gate**, quoted above.
- **ROADMAP.md Phase 13.9 governance clause**, quoted: "no 14B-or-later freeze
  commits before this skeleton has been walked." Plans 14B-06 and 15A-06 both
  check it as an explicit precondition; this freeze carries the same check.
- **PLANNING-DIRECTIVES section 3a**, the accepted-recommendation discipline
  requiring every accepted recommendation to name its owner, its verification,
  its evidence class, and its failure condition, and its rule that an agent
  never self-certifies.
- **ROADMAP.md Phase 15B prototype-before-freeze coupling**, quoted: "the 15B
  freeze covers the blueprint, audit, acceptance, staleness, and
  proposal-discipline surfaces only. It is explicitly not the course schema
  freeze, not a lesson-profile grammar freeze, not an agent job protocol
  freeze, and not a learner-facing surface freeze, and its freeze record says
  so."
- **15B-RESEARCH.md Wave 0 Gaps**, which names the tracer's structure:
  `fail(msg)`, named `scenario_*()` functions, `main()`, and a final
  `"TRACER: N passed, M skipped, 0 failed"` line.
- **15B-RESEARCH.md Environment Availability**: the freeze gate uses fixture
  and mock data for any model-authored content, never a live backend,
  following 15A's own precedent.

Decisions this plan makes and locks, so the executor never guesses (the
`PLANNING-DIRECTIVES.md` section 5 bar):

| Open question | Locked answer | One-line rationale |
|---|---|---|
| Which drafted lesson treatment the tracer uses | A fictional lesson stand-in bound as a `guided-lesson` treatment on one objective of the synthetic blueprint's course, built by `fixtures/corpus_15b.py` | The ROADMAP gate names a lesson plus a practice set; the treatment vocabulary is `graph.TREATMENT_KINDS`, already locked by 14B-03, and this phase adds no twelfth member. |
| How the staleness leg is exercised | By editing a real fixture source file and recomputing its live fingerprint, not by passing two hand-written strings | Comparing literals proves string comparison. Editing a file and watching acceptance block proves the pipeline notices a real change. |
| Where the replay runs | In a fresh subprocess that reads only `journal.entries(base)` | A replay in the same process can pass by reading state the first run left in memory. |
| Whether the tracer may fix a red scenario | Yes, a fix forced by a red scenario is a fix and is recorded as one; but no new public function, constant, or schema is added by this plan | The gate proves the phase; a capability discovered missing at the gate is a planning miss and is recorded as such rather than absorbed silently. |
| Freeze scope | The 15B freeze covers `blueprint.py`'s full public surface, the three new schemas, the `graph.py`, `course.py`, `director.py`, and `authoring.py` additions, and the one `journal.RECORD_TYPES` member, and explicitly does NOT freeze the course schema, the lesson profile, the agent job protocol, or any learner-facing surface | ROADMAP's own coupling clause, quoted above, and the same boundary 14B and 15A both inherited and restated. |
| What a `reject` review verdict does | Fails leg 2 and withholds the freeze by name | An agent never overrides a human reviewer's rejection, and a freeze written over a rejection would be a record of a judgment nobody made. |

Purpose: prove the phase rather than describe it.
Output: the tracer, the measured report, the human review, and either the
freeze or the named withholding.
</objective>

<context>
@.planning/phases/15B-quality-blueprint-acceptance/15B-RESEARCH.md
@.planning/phases/15B-quality-blueprint-acceptance/15B-VALIDATION.md
@.planning/phases/15B-quality-blueprint-acceptance/15B-DECISIONS.md
@.planning/phases/15B-quality-blueprint-acceptance/15B-01-PLAN.md
@.planning/phases/15B-quality-blueprint-acceptance/15B-02-PLAN.md
@.planning/phases/15B-quality-blueprint-acceptance/15B-06-PLAN.md
@.planning/phases/15A-director-treatment-policy/15A-06-PLAN.md
@.planning/phases/14B-graph-course-package-prototype/14B-06-PLAN.md
@.planning/ROADMAP.md
@.planning/REQUIREMENTS.md
@.planning/PLANNING-DIRECTIVES.md
@.agents/skills/OPERATION-CONTRACT.md
</context>

## Artifacts this phase produces (plan 15B-07 share)

- `tests/acceptance_tracer.py` with these functions: `fail(msg)`,
  `shipped_suite_check()`, `scenario_five_gate_acceptance()`,
  `scenario_fidelity_claim_ordering()`, `scenario_staleness_blocks()`,
  `scenario_migration_accept_and_reject()`,
  `scenario_sparse_evidence_proposal()`, `scenario_course_audit_provenance()`,
  `scenario_journal_replay()`, `measure_budgets()`, and `main()`, whose final
  line is `TRACER: N passed, M skipped, 0 failed`.
- `fixtures/corpus_15b.py` gains `build_all_15b(dest)`, which builds the
  blueprint course, its source with its rights values, its objectives, its
  drafted lesson treatment, its drafted practice set, its migration proposals,
  its sparse and dense evidence rows, and its audit signals in one call, so the
  tracer sets up in one statement.
- `.planning/phases/15B-quality-blueprint-acceptance/15B-TRACER-REPORT.md`,
  `15B-REVIEW.md`, `15B-FREEZE.md`.
- `15B-DECISIONS.md` gains the dated section
  `## D-15B-4. The Phase 15B freeze scope`.
- `15B-VALIDATION.md` with its Per-Task Verification Map statuses updated, its
  runtime placeholder replaced by a measured figure, and its sign-off boxes
  resolved.

No new module, no new public function on `blueprint.py`, `graph.py`,
`course.py`, `director.py`, or `authoring.py`, no CLI command, no daemon route,
no schema file, and no journal record type is produced by this plan.

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: the lesson-plus-practice acceptance tracer</name>
  <files>tests/acceptance_tracer.py, fixtures/corpus_15b.py, .planning/phases/15B-quality-blueprint-acceptance/15B-TRACER-REPORT.md</files>
  <read_first>
- `.planning/ROADMAP.md`, the Phase 15B freeze-gate paragraph, quoted in this
  plan's objective. Each scenario function implements exactly one of its
  clauses and names that clause in its docstring.
- `.planning/REQUIREMENTS.md`, the three Fixture sentences for ACTIVITY-02,
  RELIABILITY-03, and AGENT-03, verbatim.
- `tests/three_domain_tracer.py` in full as landed, the 14B freeze-gate tracer
  this file copies in structure: its `fail(msg)`, its named `scenario_*()`
  functions, its `shipped_suite_check()`, its `measure_budgets()`, and its
  final `TRACER:` line format.
- `tests/four_subject_review.py` in full as landed, the 15A tracer that
  `tests/three_domain_tracer.py` was itself extended into, in particular how it
  runs shipped suites as subprocesses and how it skips rather than fails on a
  red one.
- `tests/blueprint_roundtrip.py` in full as it stands after plan 15B-06, every
  `check_*` function, so no scenario duplicates a unit assertion instead of
  exercising a path.
- `blueprint.py`, `graph.py`, `course.py`, `director.py`, and `authoring.py` in
  full as they stand after plan 15B-06.
- `fixtures/corpus_15b.py` in full as it stands after plan 15B-06:
  `build_blueprint_fixture`, `build_draft_set`, `build_item_facts`,
  `build_golden_sidecar`, `build_staleness_fixture`, `edit_source`,
  `build_reconciliation_case`, `build_acceptance_fixture`,
  `build_audit_signals`, `build_sparse_evidence`, `build_dense_evidence`, and
  `teardown`.
- `.planning/phases/14A-identity-lifecycle-operation/14A-04-PLAN.md` and
  `.planning/phases/14B-graph-course-package-prototype/14B-06-PLAN.md`, for the
  `measure_budgets()` convention: it asserts nothing and prints only what the
  run produced.
  </read_first>
  <behavior>
Assertions `tests/acceptance_tracer.py` must make. Write the file first and
confirm it fails before touching the fixtures.

`shipped_suite_check()`, run first, before any 15B module is imported:

- `python tests/scoring_roundtrip.py`, `python tests/evidence_roundtrip.py`,
  `python tests/audit_authoring_roundtrip.py`,
  `python tests/audit_quality_roundtrip.py`,
  `python tests/audit_coverage_roundtrip.py`, and
  `python tests/audit_roundtrip.py` each exit 0, run as subprocesses. A red
  shipped suite skips every scenario and the final line reports the skips
  rather than reporting passes.
- All three of `14A-FREEZE.md`, `14B-FREEZE.md`, and `15A-FREEZE.md` exist with
  their `## Frozen at` headings and none carries a `## Freeze withheld`
  heading. Their absence or a withholding skips every scenario.

`scenario_five_gate_acceptance()`, implementing ACTIVITY-02's Fixture sentence:

- `fixtures.corpus_15b.build_all_15b(dest)` builds one course root carrying one
  schema-valid cited blueprint, one drafted lesson treatment, one drafted
  practice set, at least three objectives, and at least one registered source.
- `course.bind_blueprint` makes the blueprint durable and the sidecar's
  revision advances by exactly one.
- One `authoring.run_authoring` call over the drafted practice set with the
  bound blueprint and its item facts returns a report whose `status` is
  `"written"`, and its `proposal.gates` carries all four arrays:
  `lint_errors`, `lint_warnings`, `quality_findings`, and
  `blueprint_findings`.
- The drafted lesson treatment is bound through `course.bind_treatment` with a
  `treatment_kind` that is a member of `graph.TREATMENT_KINDS`, and no twelfth
  token appears anywhere in the run.
- The five gate results recorded by the run name exactly `blueprint.GATE_STEPS`
  and each reports `passed`.

`scenario_fidelity_claim_ordering()`, the claim clause of the ROADMAP gate:

- Running the same drafted set with the blueprint absent produces a report
  whose `gates.blueprint_findings` holds exactly one `blueprint.absent` warn
  finding, whose write still succeeds, and for which
  `blueprint.fidelity_claim` over the recorded results is `False`.
- Running with a drafted set that fails gate 4 only (a forbidden tool, from
  `build_draft_set(dest, "tool_forbidden")`) leaves gates 1, 2, 3, and 5
  passing and `fidelity_claim` `False`, and writes nothing.
- Running the conforming set with the blueprint bound produces
  `fidelity_claim` `True`.
- The claim is asserted at each of the five points in the run, not only at the
  end: after gate 1, after gate 2, after gate 3, after gate 4, and after gate
  5. It is `False` at the first four and `True` only at the fifth.

`scenario_staleness_blocks()`, implementing RELIABILITY-03's Fixture sentence:

- Before any edit, `blueprint.staleness_report` over the course's dependents
  returns rows whose `stale` is all `False`, and
  `director.accept_revision(..., staleness_rows=rows, dispositions=[])`
  succeeds.
- `fixtures.corpus_15b.edit_source(fixture, marker)` rewrites the synthetic
  source mid-flow, and the live fingerprint is recomputed through
  `identity.object_fingerprint` on the file's bytes rather than being read back
  from any stored value.
- After the edit, the rebuilt rows mark every dependent of that source stale,
  and `director.accept_revision` with the same arguments raises `DirectorError`
  with code `director.acceptance_blocked`, the sidecar bytes are unchanged, and
  one `refused` journal entry names every blocked dependency.
- Recording a `blueprint.disposition_record` with each of the four
  `STALENESS_DISPOSITIONS` in turn, rebuilding the case each time, clears the
  block and the acceptance succeeds. All four are exercised, so `retain` is
  proven usable in the tracer and not only in the unit test.
- A second `edit_source` after a clearing disposition supersedes it, and the
  acceptance is blocked again with `blueprint.disposition_superseded`.
- No path in the run rebuilt or regenerated the stale derivative; asserted by
  comparing the drafted set's bytes before and after the block.

`scenario_migration_accept_and_reject()`, the acceptance clause of the ROADMAP
gate:

- One migration proposal is accepted through `director.accept_revision` with
  `decision="accept"` and a settings dict whose autonomy level permits it; the
  recorded row's `state` becomes `"accepted"` and carries the reviewer and the
  rationale.
- A second proposal is rejected with `decision="reject"`; its row's `state`
  becomes `"rejected"` and the row is present, not removed.
- A third proposal whose recorded `actor` equals the reviewer is refused with
  `graph.migration_self_accept`, and the refusal is journaled.
- The same accepted proposal accepted a second time is refused with
  `graph.migration_already_settled`.
- One acceptance attempted with a `recommend-only` settings dict is refused
  with `director.autonomy_exceeded`, proving the policy is re-read at accept
  time; the proposal itself is unchanged by the refusal.
- The 14B bypass guard still fires: the path that would set a state directly
  still raises `graph.migration_state_not_settable`, asserted in this same run.

`scenario_sparse_evidence_proposal()`, implementing AGENT-03's Fixture
sentence:

- `blueprint.evidence_proposal` over `build_sparse_evidence`'s exactly two rows
  on one objective returns a record whose `denominator` is `2`, whose
  `uncertainty` is `"sparse"`, whose `window` carries `start`, `end`, and the
  `boundary` value `"half-open"`, whose `missing_signals` is non-empty, and
  whose `competing_explanations` is non-empty.
- A recursive walk over the record finds no `float` and no key whose lowercase
  name contains `mastery`, `completion`, `readiness`, `progress`, `percent`, or
  `score`.
- The record's `status` is `"recommendation"`, and nothing in the run acts on
  it: no binding, no session, no evidence event, and no selection is produced
  by the proposal.
- `evidence.py` is not written by any part of the run, asserted by capturing
  the evidence log's bytes before the tracer and comparing them after.

`scenario_course_audit_provenance()`, the audit clause of the ROADMAP gate:

- `blueprint.course_audit` over the run's own recorded signals returns a
  schema-valid report in which every row names a `vocabulary` that is a member
  of `blueprint.COVERAGE_VOCABULARIES`.
- The set of distinct vocabularies cited across the run's rows has at least two
  members, so the provenance field is proven to be carrying information rather
  than a constant.
- No state string in the report is outside the vocabulary its row cites,
  asserted against the live vocabularies.
- After the mid-flow source edit, the report's `stale` is `True` and its
  `stale_inputs` names the edited source.

`scenario_journal_replay()`, the replay clause of the ROADMAP gate:

- A fresh subprocess is launched that imports only `journal` and reads
  `journal.entries(base)`, with no other module from this phase imported and
  with no value carried from the first run.
- Every `accept_revision` entry the run produced is found, its `state` is
  `applied` or `refused` as the run produced it, and its `message` reproduces
  the reason.
- The count of `accept_revision` entries in the replay equals the count the run
  recorded, asserted as an integer equality rather than a subset check.
- The replay reads no file the tracer wrote outside `_journal/`, and it needs
  no chat transcript, asserted by the subprocess receiving only the base path
  as an argument.

`measure_budgets()`:

- Asserts nothing. Prints only what the run produced: the wall-clock seconds
  for each scenario, the total tracer duration, the byte size of the course
  sidecar after the run, the number of journal entries, the number of gate
  findings by severity, and the sparse proposal's denominator, each labeled
  measured, with the machine and the Python version printed once at the top.

`main()`:

- Runs `shipped_suite_check()` first, then each scenario in the order listed,
  counting passes and skips, and prints as its final line exactly
  `TRACER: N passed, M skipped, 0 failed` with the real counts substituted. It
  exits 0 only when the failed count is 0.
  </behavior>
  <action>
1. Create `tests/acceptance_tracer.py` first, with the local `fail(msg)`
   helper, the `ROOT` and `sys.path.insert` header convention, every function
   named in this plan's Artifacts section, and every assertion in
   `<behavior>`. Run `python tests/acceptance_tracer.py` and confirm it fails
   because `build_all_15b` does not exist yet.

2. Add `build_all_15b(dest)` to `fixtures/corpus_15b.py`, composing every
   builder plans 15B-02 through 15B-06 added into one call and returning a
   dict carrying at minimum the keys `base`, `course_root`, `blueprint`,
   `bank_path`, `state_dir`, `item_facts`, `source_path`,
   `source_object_id`, `migration_ids`, `reviewer_actor`, `proposer_actor`,
   `settings_recommend_only`, `settings_approved_bounded_write`,
   `sparse_rows`, `dense_rows`, and `audit_signals`. It adds no new fixture
   content beyond composition plus one fictional lesson stand-in bound as a
   `guided-lesson` treatment. All content is fictional and fixed-seed: the
   subject is a fictional standards blueprint stand-in whose only relationship
   to any real assessment is its shape, and paraphrase of real material is
   forbidden as firmly as copying is.

3. Run the tracer until every scenario passes. A red scenario is fixed in the
   module it belongs to, and the fix is recorded in the summary as a fix rather
   than absorbed silently. Do not add a new public function, constant, or
   schema; if a scenario cannot pass without one, stop and record that as a
   planning miss in `15B-TRACER-REPORT.md`'s Open items section rather than
   building it here.

4. Write
   `.planning/phases/15B-quality-blueprint-acceptance/15B-TRACER-REPORT.md`
   with exactly these sections: **What the tracer ran** (each scenario function
   with the ROADMAP clause and the Fixture sentence it implements); **Measured
   budgets** (every figure `measure_budgets()` printed, verbatim, with the
   machine and the Python version named, and a sentence stating that no figure
   in this section was chosen rather than measured); **What was refused** (each
   refusal code the run produced, with the scenario that produced it);
   **Open items** (every flagged assumption carried forward from plans 15B-01
   through 15B-06, each with the phase or reviewer that owns it, plus any
   planning miss found in step 3). No em dash characters.

5. Run `python itembank.py guard .` and confirm `0 offending files`.
  </action>
  <verify>
  <automated>python tests/acceptance_tracer.py && python itembank.py guard .</automated>
Expected: the tracer's final line reads `TRACER: 7 passed, 0 skipped, 0 failed`
and it exits 0, and `guard` prints `0 offending files`. The degraded behavior
this task must prove rather than paper over is the skip path: with any shipped
suite red or any freeze record missing, `shipped_suite_check()` causes every
scenario to skip and the final line reports the skips rather than reporting
passes. Confirm by temporarily pointing the shipped-suite list at a
nonexistent file, observing the skip line, and restoring it.
  </verify>
  <acceptance_criteria>
- `python tests/acceptance_tracer.py` exits 0 and its final line matches
  `TRACER: N passed, 0 skipped, 0 failed`.
- Every one of the seven `scenario_*()` functions named in this plan's
  Artifacts section exists in `tests/acceptance_tracer.py` and is called by
  `main()`.
- `python -c "import blueprint; print(len(blueprint.BLUEPRINT_CODES))"` prints
  `23`.
- `.planning/phases/15B-quality-blueprint-acceptance/15B-TRACER-REPORT.md`
  exists with all four named sections.
- The Measured budgets section names the machine and the Python version and
  carries no figure that was not printed by `measure_budgets()`.
- The evidence log's bytes are identical before and after the tracer run.
- `python itembank.py guard .` prints `0 offending files`.
- Neither `tests/acceptance_tracer.py` nor `15B-TRACER-REPORT.md` contains an
  em dash character.
  </acceptance_criteria>
  <precondition>Plans 15B-02 through 15B-06 are green, and Phases 14A, 14B, and 15A have landed with all three freeze records present and free of a withholding heading.</precondition>
  <reversibility rating="reversible">The tracer proves; it builds nothing other
  code depends on. Changing a scenario costs one edit.</reversibility>
  <done>All seven scenarios pass in one run, every figure in the report was
  measured on the machine the report names, and every clause of the ROADMAP
  freeze gate has a named scenario implementing it.</done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <name>Task 2: the acceptance-quality review a human signs</name>
  <files>.planning/phases/15B-quality-blueprint-acceptance/15B-REVIEW.md</files>
  <read_first>
- `.planning/phases/15B-quality-blueprint-acceptance/15B-TRACER-REPORT.md` as
  written by Task 1, in full.
- `.planning/ROADMAP.md`, the Phase 15B freeze-gate paragraph and the Phase
  15B prototype-before-freeze coupling clause, both quoted in this plan's
  objective.
- `.planning/REQUIREMENTS.md`, the three Fixture sentences for ACTIVITY-02,
  RELIABILITY-03, and AGENT-03, verbatim.
- `.planning/PLANNING-DIRECTIVES.md` section 3a, the accepted-recommendation
  discipline paragraph, which names owner, verification, evidence class, and
  failure condition as required of every accepted recommendation.
- `.planning/phases/15A-director-treatment-policy/15A-REVIEW.md` if it exists,
  the 15A precedent for a human review artifact of this shape, and
  `.planning/phases/14B-graph-course-package-prototype/14B-AUTHORABILITY-REVIEW.md`
  if it exists.
  </read_first>
  <what-built>
Task 1 built and ran the lesson-plus-practice acceptance tracer: one synthetic
cited blueprint paired with one drafted lesson treatment and one drafted
practice set, walked from draft through all five gates to journaled acceptance,
with the exam-fidelity claim asserted False at each of the first four gates and
True only after the fifth; a mid-flow synthetic source edit marking dependents
stale and blocking acceptance until each of the four dispositions was recorded
in turn; one migration accepted and one rejected through the reviewer path with
the live autonomy policy re-read at accept time; a sparse-evidence proposal over
two attempts naming its window, denominator, and uncertainty; and the whole
operation replayed from the journal alone in a fresh process. The tracer is
green and its measured figures are recorded in `15B-TRACER-REPORT.md`.

What the tracer cannot decide is whether any of this is legible. A green test
proves the machinery refuses what it says it refuses; it cannot tell you that a
reviewer reading a blocked acceptance would know what changed and what to do
about it, or that a blueprint finding names something a course builder could
act on, or that a sparse proposal reads as honest uncertainty rather than as a
hedge. That judgment is the freeze gate's actual subject, and an agent never
signs it for itself.
  </what-built>
  <how-to-verify>
1. Read `.planning/phases/15B-quality-blueprint-acceptance/15B-TRACER-REPORT.md`
   end to end.

2. Run the tracer yourself and watch it:

```
python tests/acceptance_tracer.py
```

   Expected final line: `TRACER: N passed, 0 skipped, 0 failed`, exit code 0.

3. Read the blocked acceptance specifically. Find the `refused` journal entry
   the staleness scenario produced and answer in `15B-REVIEW.md`:
   - Does the refusal message tell you which dependency changed?
   - Would you know, from that message alone, which of rebind, migrate,
     supersede, or retain you should record?
   - Is it obvious that nothing was written and nothing was rebuilt?

4. Read the blueprint findings specifically, from the `tool_forbidden` run.
   Answer:
   - Does each finding name a field a course builder could actually change?
   - Are the `blueprint.unverifiable` warn findings distinguishable from
     failures, and is it clear that the exam-fidelity claim rests only on the
     fields reported as checked?
   - Would you accept the drafted set, reject it, or send it back?

5. Read the sparse-evidence proposal specifically. Answer:
   - Reading only this record, would you know how much evidence it rests on?
   - Does the uncertainty level read as honest rather than as a hedge?
   - Are the competing explanations real alternatives, or restatements?
   - Is it obvious that this is a recommendation and not something that
     happened?

6. Read the course audit report specifically. Answer:
   - Can you tell, for each row, which vocabulary its state came from?
   - Does any row read as if it were merging two vocabularies?
   - Does any number in the report read as a mastery or completion claim?

7. Read the accepted and rejected migrations. Answer:
   - Is the rejected proposal still visible as a decision rather than as an
     absence?
   - Is the reviewer and the rationale legible on both?

8. Confirm Phase 13.9 has actually been walked: check that
   `.planning/phases/13.9-walking-skeleton/` contains at least one
   `*-SUMMARY.md` file and that the recorded evidence it names exists. If it
   has not been walked, say so; Task 3 will withhold the freeze on that leg.

9. Record every answer in
   `.planning/phases/15B-quality-blueprint-acceptance/15B-REVIEW.md` under a
   dated heading, with these sections: **What was reviewed**, **Judgments**
   (the questions from steps 3 through 7, grouped by step), **Concerns**,
   **Verdict** (one of `accept`, `accept with concerns recorded`, or
   `reject`), and **Signed** (name and date).
  </how-to-verify>
  <acceptance_criteria>
- `.planning/phases/15B-quality-blueprint-acceptance/15B-REVIEW.md` exists with
  all five named sections.
- The Judgments section carries one block per review step 3 through 7, each
  answering every question in that step.
- The Verdict section names exactly one of `accept`,
  `accept with concerns recorded`, or `reject`.
- The Signed section carries a human name and a date.
- The file states explicitly whether Phase 13.9 has been walked, and names the
  file it checked.
- The file contains no em dash character.
  </acceptance_criteria>
  <resume-signal>Reply with `accept`, `accept with concerns recorded`, or
  `reject`, plus any concerns to record.</resume-signal>
</task>

<task type="auto">
  <name>Task 3: the freeze record, or the named withholding</name>
  <files>.planning/phases/15B-quality-blueprint-acceptance/15B-FREEZE.md, .planning/phases/15B-quality-blueprint-acceptance/15B-DECISIONS.md, .planning/phases/15B-quality-blueprint-acceptance/15B-VALIDATION.md</files>
  <read_first>
- `.planning/phases/15B-quality-blueprint-acceptance/15B-TRACER-REPORT.md` and
  `15B-REVIEW.md`, both in full, as written by Tasks 1 and 2.
- `.planning/phases/15A-director-treatment-policy/15A-FREEZE.md` as landed, the
  precedent this file follows in shape, including whether it opens with a
  `Freeze withheld` section.
- `.planning/phases/14B-graph-course-package-prototype/14B-FREEZE.md` as
  landed, including the `## Amendment 15B: SECTION_ORDER gained Blueprint`
  section plan 15B-02 appended.
- `.planning/ROADMAP.md`, the Phase 13.9 governance clause and the Phase 15B
  entry with its prototype-before-freeze coupling clause.
- `.planning/phases/15B-quality-blueprint-acceptance/15B-VALIDATION.md` in
  full, its Per-Task Verification Map, its runtime placeholder, its
  Manual-Only Verifications table, and its sign-off checklist.
- `.planning/phases/15B-quality-blueprint-acceptance/15B-DECISIONS.md`, so the
  new section is appended below `## D-15B-3`.
- Every `15B-0N-SUMMARY.md` that exists, for the flagged assumptions each plan
  recorded and for the exact constant values the freeze record must enumerate.
  </read_first>
  <action>
1. Check the three freeze legs, in this order, and record the result of each:
   - **Leg 1, the tracer.** `python tests/acceptance_tracer.py` exits 0 with
     `0 failed`. Re-run it now rather than trusting Task 1's record, because
     Task 2's review may have prompted a fix and the freeze must describe the
     tree it is freezing.
   - **Leg 2, the human review.** `15B-REVIEW.md` exists, carries a Verdict of
     `accept` or `accept with concerns recorded`, and is signed with a name and
     a date. A verdict of `reject` fails this leg.
   - **Leg 3, Phase 13.9.** `.planning/phases/13.9-walking-skeleton/` contains
     at least one `*-SUMMARY.md` file. Its absence fails this leg, per
     ROADMAP.md's governance clause that no 14B-or-later freeze commits before
     the skeleton has been walked.

2. Write `.planning/phases/15B-quality-blueprint-acceptance/15B-FREEZE.md`.

   **If all three legs pass**, the file opens with the literal heading
   `## Frozen at 15B` and carries exactly these sections:
   - **What is frozen.** The public surface plans 02 through 06 built, listed
     symbol by symbol with its exact value or member list, so a later phase can
     re-verify against this file the way plan 15B-01's own precondition
     re-verified against 14A, 14B, and 15A. At minimum:
     `blueprint.BLUEPRINT_FIELDS`, `blueprint.GATE_STEPS`,
     `blueprint.BLUEPRINT_CODES` (all twenty-three members),
     `blueprint.WARN_CODES`, `blueprint.STALENESS_DISPOSITIONS`,
     `blueprint.COVERAGE_VOCABULARIES`, `blueprint.UNCERTAINTY_LEVELS`,
     `blueprint.PROPOSAL_KEYS`, `blueprint.WINDOW_KEYS`,
     `blueprint.AUDIT_ROW_KEYS`, `blueprint.AUDIT_REPORT_KEYS`,
     `blueprint.SPARSE_MAX`, `blueprint.MODERATE_MAX`; the three new schema
     files with their `x-itembank-version` values; `graph.accept_migration`,
     `graph.reject_migration`, `graph.add_blueprint`, `graph.blueprints`, and
     the three new `GraphError` codes; `course.bind_blueprint`,
     `course.accept_migration`, `course.reject_migration`; `director.accept_revision`,
     `director.ACCEPT_RECORD_TYPE`, `director.ACCEPT_OUTCOMES`, and the two new
     `DirectorError` codes; the one new `journal.RECORD_TYPES` member; and
     `authoring.build_proposal`'s new `blueprint_findings` parameter with the
     `gates.blueprint_findings` array.
   - **What is NOT frozen.** In plain sentences, quoting ROADMAP's coupling
     clause: this is not the course schema freeze, not a lesson-profile grammar
     freeze, not an agent job protocol freeze, and not a learner-facing surface
     freeze. It also does not freeze `fixtures/corpus_15b.py`, which is test
     data, and it does not freeze the caller-supplied item-fact contract, which
     plan 15B-02 recorded as resting on caller honesty.
   - **Evidence.** The tracer command and its final line verbatim, the review
     verdict and signer, the Phase 13.9 file checked, and the date.
   - **Measured, not promised.** The figures from `15B-TRACER-REPORT.md`'s
     Measured budgets section, with their machine and Python version.
   - **Open items carried forward.** Every concern `15B-REVIEW.md` recorded,
     plus each of these flagged assumptions with the phase or reviewer that
     owns it: the unclassified RELIABILITY-03 probe row (plan 15B-03); the
     caller-supplied item-fact honesty gap (plan 15B-02); the unauthenticated
     reviewer identity (plans 15B-03 and 15B-04); the concurrency backstop
     (plan 15B-04); the three-vocabulary stability assumption (plan 15B-05);
     the evidence-to-graph objective join backstop (plan 15B-06); and the named
     uncertainty bands (plan 15B-06).

   **If any leg fails**, the file instead opens with the literal heading
   `## Freeze withheld` followed immediately by a section naming each failing
   leg, what it would take to satisfy it, and one sentence stating that Phase
   15B stays open. Do not write `## Frozen at 15B` anywhere in that version of
   the file. Do not describe a failing leg as satisfied and do not omit it.

3. Append to `15B-DECISIONS.md` a dated section
   `## D-15B-4. The Phase 15B freeze scope` recording the freeze-scope decision
   this plan's objective table locked, in the same voice the earlier three
   sections use, and stating explicitly that 15B does not freeze the course
   schema, the lesson profile, the agent job protocol, or any learner-facing
   surface.

4. Fill `15B-VALIDATION.md`:
   - Update the **Per-Task Verification Map**'s Status column for every row to
     `pass` or to the reason it is not. The map was populated at plan time and
     already carries one row per task across all seven plans; do not rewrite
     the rows, only their statuses.
   - Replace the **Estimated runtime** placeholder in the Test Infrastructure
     table with the measured full-suite figure from `15B-TRACER-REPORT.md`,
     labeled measured and dated, with the machine named.
   - Fill the **Manual-Only Verifications** table's Test Instructions cell with
     a pointer to Task 2's `how-to-verify` steps and to `15B-REVIEW.md`.
   - Replace the **Max feedback latency** placeholder with the measured
     single-file `python tests/blueprint_roundtrip.py` figure.
   - Check the six **Validation Sign-Off** boxes that are genuinely satisfied
     and leave any that are not unchecked with a one-line reason beneath.
   - Set `nyquist_compliant: true` in the frontmatter only if every task in the
     map has an automated command and no three consecutive tasks lack one.
     Otherwise leave it `false` and say why.
   - Set `status: validated` in the frontmatter only when the freeze legs all
     passed.
   - Set `wave_0_complete: true` only when `tests/acceptance_tracer.py`,
     `tests/blueprint_roundtrip.py`, the three new schema files, and
     `fixtures/corpus_15b.py` all exist.

5. Run `python itembank.py guard .` and confirm `0 offending files`. Run
   `for t in tests/*.py; do python "$t" || exit 1; done` one final time and
   confirm exit 0.
  </action>
  <verify>
  <automated>python tests/acceptance_tracer.py && python itembank.py guard .</automated>
Expected: the tracer's final line ends in `0 failed` and exits 0, and guard
prints `0 offending files`. The degraded behavior this task must prove rather
than paper over is the withholding itself: if any leg fails, the freeze file
opens with `## Freeze withheld`, the string `## Frozen at 15B` appears nowhere
in it, and the phase stays open. Confirm both conditions on whichever branch
actually ran.
  </verify>
  <acceptance_criteria>
- `python tests/acceptance_tracer.py` exits 0.
- `for t in tests/*.py; do python "$t" || exit 1; done` exits 0.
- `python itembank.py guard .` prints `0 offending files` and exits 0.
- `.planning/phases/15B-quality-blueprint-acceptance/15B-FREEZE.md` exists and
  contains exactly one of the headings `## Frozen at 15B` or
  `## Freeze withheld`, never both.
- When the heading is `## Frozen at 15B`, the file carries all five named
  sections, and its What is frozen section names `blueprint.BLUEPRINT_FIELDS`,
  `blueprint.GATE_STEPS`, `blueprint.STALENESS_DISPOSITIONS`,
  `blueprint.COVERAGE_VOCABULARIES`, `blueprint.UNCERTAINTY_LEVELS`,
  `blueprint.PROPOSAL_KEYS`, and all twenty-three `blueprint.BLUEPRINT_CODES`
  members with their exact values.
- When the heading is `## Frozen at 15B`, the Open items section names all
  seven flagged assumptions listed in step 2, each with an owner.
- When the heading is `## Freeze withheld`, every failing leg is named and the
  string `## Frozen at 15B` does not appear in the file.
- `15B-DECISIONS.md` contains the literal heading
  `## D-15B-4. The Phase 15B freeze scope`.
- `15B-VALIDATION.md`'s Per-Task Verification Map has no row whose Status is
  still `planned`, and its Estimated runtime cell no longer contains the word
  `Unknown`.
- `15B-VALIDATION.md`'s Max feedback latency line no longer contains the phrase
  `to be measured`.
- None of `15B-FREEZE.md`, `15B-DECISIONS.md`, or `15B-VALIDATION.md` contains
  an em dash character.
  </acceptance_criteria>
  <precondition>Task 1's tracer is green and Task 2's review is recorded and signed.</precondition>
  <reversibility rating="costly">The freeze record is what plan 16A's and
  16B's preconditions will assert against, the same way plan 15B-01's
  precondition asserted against 14A, 14B, and 15A. It is costly rather than
  one-way because the recorded mechanism for changing a frozen surface already
  exists and is visible: a surface enumerated here and then changed forces a
  dated amendment section appended to this file, which is exactly the
  discipline plan 15B-02 followed when it amended `14B-FREEZE.md` for
  `graph.SECTION_ORDER`. The genuinely one-way decisions this record enumerates
  were each gated upstream by their own blocking checkpoint: `D-15B-1`,
  `D-15B-2`, and `D-15B-3`. This task makes none of its own, and the human
  judgment it does require is the blocking `checkpoint:human-verify` in Task 2
  immediately above it.</reversibility>
  <done>Phase 15B is either frozen with its surface enumerated, its evidence
  recorded, and its seven open items owned, or held open with the missing leg
  named.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| tracer to shipped suites | A green phase tracer could mask a regression in the shipped parser, scorer, or authoring loop if it does not run those suites itself. |
| fixture corpus to repository | Synthetic blueprint and lesson material enters version control and could drift toward real course content. |
| freeze record to later phases | Whatever this file says is frozen is what plan 16A's precondition will assert against. |
| human review to freeze | A signature is the only thing standing between a green machine and an accepted claim about acceptance quality. |
| first run to replay | A replay in the same process could pass by reading state the first run left behind rather than by reading the journal. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-15B-07-01 | Spoofing | an agent self-certifying the acceptance-quality review | high | mitigate | The review is a blocking `checkpoint:human-verify` producing a signed file with a named verdict; Task 3 fails leg 2 on a missing signature or a `reject` verdict, and the freeze is withheld by name. |
| T-15B-07-02 | Repudiation | a freeze record claiming a leg that was not run | high | mitigate | Task 3 re-runs the tracer rather than trusting Task 1's record, checks the review file's verdict and signature, and checks the Phase 13.9 summary file. A failing leg produces a `## Freeze withheld` file in which the frozen heading appears nowhere, asserted in the acceptance criteria. |
| T-15B-07-03 | Tampering | a regression in the shipped runtime hidden behind a green phase tracer | high | mitigate | `shipped_suite_check()` runs six shipped suites as subprocesses before any 15B module is imported, and a red suite skips every scenario rather than reporting passes. The full suite runs again in Task 3. |
| T-15B-07-04 | Tampering | a replay that passes by reading in-memory state | high | mitigate | The replay runs in a fresh subprocess receiving only the base path, imports only `journal`, and asserts an integer equality on the entry count rather than a subset check. |
| T-15B-07-05 | Tampering | a staleness scenario that proves only string comparison | high | mitigate | The scenario edits a real fixture source file and recomputes the live fingerprint through `identity.object_fingerprint` on the file's bytes, rather than passing two hand-written strings. |
| T-15B-07-06 | Repudiation | an invented budget figure in the tracer report | high | mitigate | `measure_budgets()` asserts nothing and prints only what the run produced, the report labels every figure measured with its machine and Python version, and the plan forbids any number that was not measured. |
| T-15B-07-07 | Information Disclosure | real course, exam, or learner content entering through the tracer corpus | high | mitigate | `build_all_15b` composes existing fictional fixed-seed builders and adds one fictional lesson stand-in, the plan forbids paraphrase as well as copying, and `python itembank.py guard .` is in Tasks 1 and 3 acceptance criteria. |
| T-15B-07-08 | Tampering | the tracer writing a learner evidence event | high | mitigate | The evidence log's bytes are captured before the tracer and compared after, and the equality is an acceptance criterion; `blueprint.py` imports no `evidence` and nothing else in the run writes one. |
| T-15B-07-09 | Elevation of Privilege | a capability quietly added at the freeze gate to make a scenario pass | high | mitigate | The plan forbids adding a public function, constant, or schema in this plan and requires a scenario that cannot pass without one to be recorded as a planning miss in the tracer report's Open items section instead. |
| T-15B-07-10 | Repudiation | an open item dropped rather than carried forward | high | mitigate | Task 3 step 2 names all seven flagged assumptions explicitly, and the acceptance criteria require the Open items section to name all seven with an owner each. |
| T-15B-07-11 | Tampering | supply chain: a dependency introduced by the tracer | high | mitigate | None is added; the tracer runs `subprocess`, `time`, `os`, and `json` from the standard library against in-repo modules. Per `PLANNING-DIRECTIVES.md` section 4a the absence of dependencies is explicitly not the mitigation: any dependency ever added here is vendored at a pinned version with a recorded checksum and a named license review. |
| T-15B-07-12 | Denial of Service | a fixture temp directory left behind on a failed run | low | accept | `fixtures/corpus_15b.teardown` runs in the tracer's exit path, and a leftover temp directory on a hard failure is a local disk artifact with no data at risk. Accepted because the failure is loud and local. |
</threat_model>

<out_of_scope>
Refused by this plan, by name, so no adjacent temptation is decided by executor
judgment:

- No new public function, constant, refusal code, or schema on `blueprint.py`,
  `graph.py`, `course.py`, `director.py`, `journal.py`, or `authoring.py`. This
  plan proves; it does not build. A fix forced by a red scenario is a fix and is
  recorded as such.
- No live model backend run. The gate is designed against fixture and mock data
  by `15B-RESEARCH.md`'s Environment Availability row, and a real provider run
  is neither required nor sufficient for it.
- No real course, exam, syllabus, lesson, or learner content, and no paraphrase
  of any.
- No course schema freeze. ROADMAP's own coupling clause says so and 14B's
  freeze record already said it first; 15B inherits the boundary and repeats
  it.
- No lesson-profile grammar freeze, no agent job protocol freeze, and no
  learner-facing surface freeze.
- No accessibility certification. This phase ships no learner-facing surface,
  and an agent never self-certifies accessibility.
- No CLI command and no daemon route for anything in this phase.
- No change to `build.py`'s `STAGE_FILES`. Packaging the
  `identity`/`journal`/`discovery`/`graph`/`course`/`course_package`/`director`/`blueprint`
  module family is one coherent change owned by whichever phase first ships a
  CLI surface for them.
- No milestone-level audit or retrospective. This plan closes one phase.
</out_of_scope>

<flagged_assumptions>
Carried forward into the freeze record's Open items section, not silently
dropped. Every one of these was recorded by an earlier plan in this phase and
each is repeated here so Task 3 has the complete list in one place:

- **RELIABILITY-03, unclassified edge row (unresolved, plan 15B-03).** The
  deterministic edge probe could not classify RELIABILITY-03 into any shape
  category, so no acceptance criterion was derived from it. Its Fixture
  sentence is covered by `scenario_staleness_blocks()` and its Degraded clause
  by `blueprint.acceptance_block`, but the row itself remains an open
  assumption for the phase verifier to review by hand.
- **The caller-supplied item-fact honesty gap (plan 15B-02).** Five of
  ACTIVITY-02's eight blueprint fields are checked against what the caller
  asserts, because the bank format carries none of them. A caller asserting a
  false fact produces a green gate over a false premise. Closing it means adding
  those fields to the parsed format, an additive change with its own
  byte-identical fixture proof, owned by whichever phase does that.
- **The unauthenticated reviewer identity (plans 15B-03 and 15B-04).** The
  reviewer role is a string this product does not authenticate, matching
  `journal.commit_operation`'s existing `origin` model.
- **The concurrency backstop (plan 15B-04).** The interleavings the fixtures
  reach all leave one valid state because `journal.commit_operation`'s lock is
  the one serialization point; whether some interleaving exists that the
  fixtures do not reach is unproven and is owned by the phase that first runs
  two agent clients against one course root in earnest.
- **The three-vocabulary stability assumption (plan 15B-05).** A stored course
  audit citing a vocabulary whose members later change fails its own membership
  check on re-validation, which is the safe direction but is a re-validation
  failure rather than a migration; whichever phase changes one of the three
  owns that migration.
- **The evidence-to-graph objective join backstop (plan 15B-06).** The evidence
  log keys events by objective text while the course graph keys objectives by
  opaque id; `blueprint.objective_key` normalizes without folding case or
  matching prefixes, and the join itself is the caller's, proven only for this
  phase's fixture objectives.
- **The named uncertainty bands (plan 15B-06).** `SPARSE_MAX` of `5` and
  `MODERATE_MAX` of `19` are legible thresholds chosen so AGENT-03's
  two-attempt fixture reads `sparse`; they are deliberately not tuned to a
  statistical criterion, because a tuned threshold would itself be a confidence
  claim.
</flagged_assumptions>

<summary_obligations>
`15B-07-SUMMARY.md` records: the tracer's final line verbatim from both Task 1
and the Task 3 re-run; every scenario that was red at first and the fix it
forced, named as a fix; the review verdict, the signer, and every concern
recorded; whether Phase 13.9 was walked and which file proved it; which of the
three freeze legs passed and which withheld; the exact `blueprint.BLUEPRINT_CODES`
tuple as frozen; the measured full-suite and single-file runtimes with the
machine and Python version; the seven open items and their owners; and any
deviation from this plan with its reason.
</summary_obligations>

<output>
Create
`.planning/phases/15B-quality-blueprint-acceptance/15B-07-SUMMARY.md`
when done.
</output>
