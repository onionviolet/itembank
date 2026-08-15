---
phase: 15A-director-treatment-policy
plan: 06
type: execute
wave: 6
depends_on: ["15A-05"]
files_modified:
  - fixtures/corpus_14b.py
  - fixtures/mock_backends.py
  - tests/four_subject_review.py
  - .planning/phases/15A-director-treatment-policy/15A-TRACER-REPORT.md
  - .planning/phases/15A-director-treatment-policy/15A-REVIEW.md
  - .planning/phases/15A-director-treatment-policy/15A-FREEZE.md
  - .planning/phases/15A-director-treatment-policy/15A-DECISIONS.md
  - .planning/phases/15A-director-treatment-policy/15A-VALIDATION.md
autonomous: false
requirements: [TREAT-01, TREAT-02, RIGHTS-02, RELIABILITY-02, AGENT-01, AGENT-02]
estimate:
  tokens: 72000
  raw_tokens: 72000
  tasks: 3
  confidence: low
must_haves:
  truths:
    - "One recommendation operation runs over four synthetic subject outlines standing in for EMT, Math 1400, CSCI 1100, and a standardized-exam blueprint, and in that one run at least one objective is bound to direct reading as a complete result and at least one is deliberately left untreated with its reason recorded."
    - "The same synthetic operation runs through a mock hosted profile and a mock local profile and produces identical artifacts and journals: the two recommendation records and the two agent dicts are equal after director.parity_view removes the volatile keys, and the two runs differ only in the profile name and the backend class."
    - "Disabling the active backend after those two runs leaves the core loop operable: the pass returns untreated entries with a typed adapter code, writes no binding, and the same objective is then bound by a human actor through course.bind_treatment directly, which is the manual-continuation half of AGENT-02's degraded clause."
    - "The egress log lists exactly the approved synthetic source spans: the set of source object id and locator pairs recorded across the whole four-subject run equals the set the rights matrix approved, computed independently in the tracer rather than read back from the same function that produced it."
    - "The operation replays step by step from the journal alone against the thirteen-step protocol checklist, in a fresh process, and every one of the thirteen steps is recorded or is not-applicable with a stated reason. A missing step withholds the freeze."
    - "No 15A freeze record is written on a red tracer, on a missing human review, or on absent Phase 13.9 evidence. On any missing leg the file opens with a Freeze withheld section naming that leg, and the phase stays open."
    - "The tracer measures rather than asserts: every duration, byte count, span count, and journal entry count in the tracer report is a figure the run produced on the machine and Python version the report names, and no budget number appears that was not measured."
  prohibitions:
    - statement: "The four-subject corpus must not contain, paraphrase, or be derived from real course material, real exam content, a real syllabus, a real learner's notes, or any real bank; the subjects are fictional stand-ins whose only relationship to EMT, Math 1400, CSCI 1100, and a standardized exam is their shape."
      status: kept
      verification: flagged-unverified
    - statement: "The freeze record must not claim a leg that was not run; a leg that could not be executed is named as withheld rather than described as satisfied or omitted from the list."
      status: kept
      verification: flagged-unverified
  artifacts:
    - "fixtures/corpus_14b.py gains build_four_subjects and build_all_15a"
    - "fixtures/mock_backends.py gains a per-subject deterministic branch and the shared candidate_for stays the one builder both transports call"
    - "tests/four_subject_review.py, the freeze-gate tracer"
    - ".planning/phases/15A-director-treatment-policy/15A-TRACER-REPORT.md"
    - ".planning/phases/15A-director-treatment-policy/15A-REVIEW.md"
    - ".planning/phases/15A-director-treatment-policy/15A-FREEZE.md"
    - "15A-VALIDATION.md with its Per-Task Verification Map filled and its sign-off checked"
    - "15A-DECISIONS.md gains the dated D-15A-3 freeze-scope answer"
  key_links:
    - "The parity assertion compares two recommend-only runs against one course root, so both runs see identical object ids and neither writes. If either run were given approved-bounded-write autonomy, the first would mutate the state the second reads and the comparison would prove nothing. The accept path is exercised separately, once."
    - "The egress assertion must compute the approved span set independently, from the rights matrix the fixture built, rather than by calling director.approved_spans again. Comparing a function's output to itself is a green test that measures nothing."
    - "Phase 13.9 must be walked before this freeze closes. ROADMAP.md's Phase 13.9 governance clause reads no 14B-or-later freeze commits before this skeleton has been walked, and 14B-06 already checks it as an explicit precondition. This freeze carries the same check."
---

<objective>
Run the phase's own freeze gate: one recommendation operation across four
synthetic subjects, through two backends, replayed from the journal, with its
egress checked against an independently computed approved-span set, its
untreated objective visible, and a human signing the recommendation review that
an agent may never sign for itself.

This is the last plan of Phase 15A. It builds no new capability. It proves the
five it inherited, records what it measured, and either writes the freeze or
names the leg that withheld it.

Decisions already made, cited, and never re-derived here:

- **ROADMAP.md Phase 15A freeze gate**, quoted: "the four-subject
  recommendation review: one recommendation operation over four synthetic
  subject outlines (EMT, Math 1400, CSCI 1100, and one standardized-exam
  blueprint), including one objective bound to direct reading as a complete
  result and one left untreated, replayed step by step from the operation
  journal against the protocol checklist, run through a mock hosted and a mock
  local backend with identical artifacts and journals, with the egress log
  listing exactly the approved synthetic source spans."
- **ROADMAP.md Phase 13.9 governance clause**, quoted: "no 14B-or-later freeze
  commits before this skeleton has been walked." Plan 14B-06 already checks it
  as an explicit precondition; this freeze carries the same check.
- **PLANNING-DIRECTIVES section 3a**, quoted: "An agent never self-certifies
  accessibility", and the accepted-recommendation discipline requiring every
  accepted recommendation to name its owner, its verification, its evidence
  class, and its failure condition.
- **15A-RESEARCH.md Assumption A4**: the fourth synthetic domain extends
  `fixtures/corpus_14b.py`'s existing generator rather than a new fixture
  module.
- **15A-RESEARCH.md Open Question 1**, recommendation: the freeze gate uses the
  internal-API shape, matching how 14A-04 and 14B-06 exercise their modules
  directly rather than through a CLI. Any CLI or daemon surface for accepting a
  recommendation is explicitly out of scope for 15A.

Decisions this plan makes and locks, so the executor never guesses:

| Open question | Locked answer | One-line rationale |
|---|---|---|
| The four subject stand-ins | The three fictional domains `fixtures/corpus_14b.py` already builds, plus a fourth named `beacon-standards-blueprint` | `14B-02-PLAN.md` already established `meridian-field-response`, `orrery-algebra`, and `lantern-computing` as the EMT, Math, and CS stand-ins; adding a fourth to the same generator is the additive path A4 names. |
| Which subject carries the direct-reading binding | `beacon-standards-blueprint`, the exam-blueprint stand-in | A blueprint objective whose best treatment is reading the blueprint itself is the clearest case where generation would be the wrong answer, which is exactly what TREAT-01 asks the gate to demonstrate. |
| Which objective is left untreated | One objective in `lantern-computing` whose only source has all seven rights `unknown` | The untreated case is then caused by a real policy state rather than by the fixture declining to call the backend, so the recorded reason is a true reason. |
| Parity run autonomy | Both parity runs use `recommend-only` and write nothing | A writing first run would mutate the state the second reads, so the comparison would compare two different situations. |
| How the egress set is checked | Computed independently in the tracer from the rights matrix the fixture built, then compared to the recorded egress | Calling the same function twice and comparing proves the function is deterministic, not that it is correct. |
| Freeze scope | The 15A freeze covers the recommendation, coverage, egress, autonomy, and protocol surfaces this phase built, and explicitly does NOT freeze the course schema, the lesson profile, or any learner-facing surface | 14B's own freeze record already states it is not the course schema freeze; 15A inherits that boundary and says so rather than letting a reader infer scope from the word freeze. |

Purpose: prove the phase rather than describe it.
Output: the tracer, the measured report, the human review, and either the
freeze or the named withholding.
</objective>

<context>
@.planning/phases/15A-director-treatment-policy/15A-RESEARCH.md
@.planning/phases/15A-director-treatment-policy/15A-PATTERNS.md
@.planning/phases/15A-director-treatment-policy/15A-VALIDATION.md
@.planning/phases/15A-director-treatment-policy/15A-01-PLAN.md
@.planning/phases/15A-director-treatment-policy/15A-05-PLAN.md
@.planning/phases/14B-graph-course-package-prototype/14B-06-PLAN.md
@.planning/ROADMAP.md
@.planning/REQUIREMENTS.md
@.planning/PLANNING-DIRECTIVES.md
@.agents/skills/OPERATION-CONTRACT.md
</context>

## Artifacts this phase produces (plan 15A-06 share)

- `tests/four_subject_review.py` with these functions: `fail(msg)`,
  `shipped_suite_check()`, `scenario_four_subject_recommendation()`,
  `scenario_direct_reading_and_untreated()`, `scenario_coverage_states()`,
  `scenario_egress_exactness()`, `scenario_backend_parity()`,
  `scenario_backend_loss()`, `scenario_protocol_replay()`,
  `measure_budgets()`, and `main()`, whose final line is
  `TRACER: N passed, M skipped, 0 failed`.
- `fixtures/corpus_14b.py` gains `build_four_subjects(dest)` adding the fourth
  domain `beacon-standards-blueprint`, and `build_all_15a(dest)` which builds
  the four domains, their sources with their rights values, their objectives,
  and the rights matrix in one call so the tracer sets up in one statement.
- `fixtures/mock_backends.py` gains a per-subject deterministic branch inside
  the existing `candidate_for`, so a blueprint objective is recommended
  `direct-reading`. `candidate_for` stays the single builder both transports
  call.
- `.planning/phases/15A-director-treatment-policy/15A-TRACER-REPORT.md`,
  `15A-REVIEW.md`, `15A-FREEZE.md`.
- `15A-DECISIONS.md` gains the dated section
  `## D-15A-3. The Phase 15A freeze scope`.
- `15A-VALIDATION.md` with its Per-Task Verification Map filled, its runtime
  placeholder replaced by a measured figure, and its sign-off boxes checked.

No new module, no new public function on `director.py`, no CLI command, no
daemon route, no schema file, and no journal record type is produced by this
plan.

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: the fourth subject and the four-subject review tracer</name>
  <files>fixtures/corpus_14b.py, fixtures/mock_backends.py, tests/four_subject_review.py</files>
  <read_first>
- `fixtures/corpus_14b.py` in full as it stands after plan 15A-05:
  `build_three_domains`, `build_all`, `build_stub_course`,
  `build_recommendation_fixture`, `build_coverage_fixture`,
  `build_rights_matrix_fixture`, `build_interrupted_operation`,
  `revoke_right`, `teardown`, and the fixed-seed rule every generator follows.
- `fixtures/mock_backends.py` in full: `candidate_for`, `main_cli`, `serve`,
  and the `__main__` dispatch.
- `tests/three_domain_tracer.py` in full as landed, the 14B freeze-gate tracer
  this file copies in structure: its `fail(msg)`, its named `scenario_*()`
  functions, its `shipped_suite_check()`, its `measure_budgets()`, and its
  final `TRACER:` line format.
- `tests/file_fault_tracer.py` in full as landed, the 14A tracer that
  `tests/three_domain_tracer.py` itself was modeled on.
- `director.py` in full as it stands after plan 15A-05.
- `.planning/REQUIREMENTS.md`, the six Fixture sentences for TREAT-01,
  TREAT-02, RIGHTS-02, RELIABILITY-02, AGENT-01, and AGENT-02. Each scenario
  function implements exactly one of them and names it in its docstring.
  </read_first>
  <behavior>
Assertions `tests/four_subject_review.py` must make. Write the file first and
confirm it fails before touching the fixtures.

`shipped_suite_check()`, run first, before any 15A module is imported:

- `python tests/scoring_roundtrip.py`, `python tests/evidence_roundtrip.py`,
  and `python tests/protocol_roundtrip.py` each exit 0, run as subprocesses. A
  red shipped suite skips every scenario and the final line reports the skips
  rather than reporting passes.
- Both `14A-FREEZE.md` and `14B-FREEZE.md` exist with their `## Frozen at`
  headings. Their absence skips every scenario.

`scenario_four_subject_recommendation()`, implementing TREAT-01's Fixture
sentence:

- `fixtures.corpus_14b.build_all_15a(dest)` builds four course roots named
  `meridian-field-response`, `orrery-algebra`, `lantern-computing`, and
  `beacon-standards-blueprint`, each with at least three objectives and at
  least one registered source.
- One `director.recommend_treatments` pass over all four subjects returns one
  entry per objective, and the sum of the three
  `director.RECOMMENDATION_OUTCOMES` counts equals the objective count.
- Every entry whose `outcome` is `bound` names a `treatment_kind` in
  `graph.TREATMENT_KINDS`, and no entry names a twelfth token.
- Nothing was silently generated: every objective not bound appears in
  `director.untreated_objectives` for its own course with a reason in
  `director.UNTREATED_REASONS`.

`scenario_direct_reading_and_untreated()`, the two named cases:

- Exactly one objective in `beacon-standards-blueprint` is bound with
  `treatment_kind` `direct-reading`, and after the pass it is not listed by
  `director.untreated_objectives`. Direct reading is a complete result.
- Exactly one objective in `lantern-computing` is left untreated because its
  only source has all seven rights `unknown`, and it is listed by
  `director.untreated_objectives` with reason `rights-not-granted`.
- The journal carries an entry for that untreated objective whose `state` is
  `refused` and whose message names the missing right, so the reason is
  recorded and not merely computed.

`scenario_coverage_states()`, implementing TREAT-02's Fixture sentence:

- Across the four subjects, `director.coverage_claims_for` produces at least
  one claim classified into each of the five `graph.BINDING_STATES` members.
- The heading-similarity decoy in `beacon-standards-blueprint`, whose locator
  is its objective's statement word for word, classifies `unknown` and not
  `covered`.
- Every state string produced anywhere in the run is a member of
  `graph.BINDING_STATES`, asserted by collecting them all and comparing sets.

`scenario_egress_exactness()`, implementing RIGHTS-02's Fixture sentence:

- The tracer computes the expected approved-span set independently: it walks
  the four course roots' `## Bindings` source rows, reads each source's rights
  from `journal.read_registry`, resolves the required right from
  `graph.TREATMENT_RIGHTS` for the treatment each entry actually used, and
  builds the set of `(source_object_id, locator)` pairs that should have been
  approved. It does not call `director.approved_spans` to build this set.
- The union of the `spans` lists across every recorded egress dict in the run
  equals that independently computed set exactly. Not a subset, not a superset.
- The union of the `omitted` lists carries every source that was refused, each
  with a reason in `director.OMISSION_REASONS`, and no pair appears in both
  unions.
- No egress record anywhere in the run has `evidence_included` `True`, and no
  recorded value anywhere is an endpoint, a command vector, or an environment
  variable name.

`scenario_backend_parity()`, implementing AGENT-02's Fixture sentence:

- One course root, one objective, `recommend-only` autonomy, run twice: once
  through a profile whose `transport` is `hosted_cli` pointed at
  `fixtures/mock_backends.py --cli`, once through a profile whose `transport`
  is `openai_compatible` pointed at the fixture HTTP server.
- `director.parity_view` of the two recommendation records are equal.
- `director.parity_view` of the two journal `agent` dicts are equal.
- The two adapter results differ in exactly the expected places: the hosted
  result's `provider.backend_class` is `hosted` and the local result's is
  `local`, and the two `provider.profile` names differ. Every other compared
  field is equal.
- Neither run wrote a binding: the sidecar's revision number is unchanged
  across both.
- Both runs went through the one shared `candidate_for`, asserted by comparing
  each transport's returned candidate to a direct in-process call of
  `fixtures.mock_backends.candidate_for(request)`.

`scenario_backend_loss()`, the degraded half of AGENT-02:

- With the active profile name set to a name matching no profile, the pass
  returns untreated entries with adapter code `adapter.profile_unknown`, writes
  no binding, and raises nothing.
- With `profiles` set to an empty list, the pass returns untreated entries with
  adapter code `adapter.profile_disabled`.
- After either loss, the same objective is bound by a human actor calling
  `course.bind_treatment` directly with `actor_kind` `human`, and that binding
  succeeds. Manual continuation works.
- The egress record for every backend-loss entry has `destination` `local` and
  `payload_bytes` `0`.

`scenario_protocol_replay()`, implementing AGENT-01's and RELIABILITY-02's
Fixture sentences:

- The four-subject operation is replayed by a fresh subprocess that imports
  `director` and `journal`, opens only the journal directory, and prints the
  report as JSON. No value from the tracer process is passed to it.
- The replayed report's `verdict` is `complete`, all thirteen steps are
  `recorded` or `not-applicable` with a stated reason, and `out_of_order` is
  empty.
- The `preview` step is `not-applicable` with its fixed reason string.
- The operation is then interrupted at each of the thirteen phases through
  `fixtures.corpus_14b.build_interrupted_operation`, and for each,
  `director.resume_point` in a fresh subprocess names the killed-after phase
  and the next one.
- `director.reverse_operation` on the completed operation restores the four
  sidecars to bytes equal to their pre-operation values, compared byte for
  byte.

`measure_budgets()`:

- Records, as measured figures and never as assertions: the wall-clock seconds
  of one full four-subject pass; the number of journal entries the pass
  appended; the total `payload_bytes` across the run; the largest single
  `payload_bytes`; the number of spans approved and the number omitted; and the
  wall-clock seconds of one full `tests/four_subject_review.py` run.
- Records the machine and the Python version each figure came from, read from
  `platform` and `sys.version`.
- Asserts nothing about these numbers. It prints them for the report.

`main()`:

- Runs `shipped_suite_check()` first, then every scenario, counting passes,
  skips, and failures, and prints as its final line
  `TRACER: N passed, M skipped, 0 failed` with the real counts substituted.
- Exits 0 only when the failure count is zero.
  </behavior>
  <action>
1. Create `tests/four_subject_review.py` first, following
   `tests/three_domain_tracer.py`'s structure function for function, with every
   assertion above and its own local `fail(msg)` helper. Each `scenario_*()`
   function's docstring names the one requirement Fixture sentence it
   implements, quoted. Run `python tests/four_subject_review.py` and confirm it
   fails because the fourth domain does not exist yet.

2. Add `build_four_subjects(dest)` to `fixtures/corpus_14b.py`. It calls the
   existing `build_three_domains` and then adds the fourth domain
   `beacon-standards-blueprint`, a fictional standardized-exam blueprint with
   one container labeled `domain`, three objectives, one registered source
   whose `read` right is `granted` and whose `transform` right is `unknown`,
   and one heading-similarity decoy claim. Add `build_all_15a(dest)` which
   calls `build_four_subjects`, sets the rights values each scenario needs
   including `lantern-computing`'s all-unknown source, and returns a dict
   naming every course root, objective id, source object id, and the two
   specifically named objectives: the blueprint's direct-reading objective and
   the lantern untreated objective. Everything is generated from the same fixed
   seed the existing generators use so a rebuild is byte-identical. All content
   is fictional. No real course, book, learner, exam, or bank content of any
   kind, and no paraphrase of any.

3. Extend `candidate_for` in `fixtures/mock_backends.py` with a deterministic
   per-subject branch: when the request's `course_object_id` matches the
   blueprint course, return `direct-reading` as the `treatment_kind`;
   otherwise keep the existing index rule. Keep `candidate_for` as the one
   builder both `main_cli` and `serve` call. Add no randomness and no clock
   read.

4. Re-run `python tests/four_subject_review.py` until it passes and its final
   line reads `TRACER: N passed, 0 skipped, 0 failed` with the real pass count.
   If any scenario exposes a real defect in `director.py`, fix `director.py`
   rather than weakening the scenario, and record the fix in the summary. Then
   run the full suite with
   `for t in tests/*.py; do python "$t" || exit 1; done`, expected exit 0, and
   `python itembank.py guard .`, expected `0 offending files`.

5. Write `.planning/phases/15A-director-treatment-policy/15A-TRACER-REPORT.md`
   with exactly these sections: **What was run** (the command and its full
   output verbatim); **Requirement coverage** (a table with one row per
   requirement id, the scenario function that implements it, and pass or skip);
   **Measured budgets** (every figure `measure_budgets()` printed, with the
   machine and Python version, each labeled measured and dated); **Defects
   found and fixed** (every fix step 4 forced, or `none`); and **What this
   tracer does not prove** (in plain sentences: it uses mock backends and not a
   real provider; it uses fictional corpora and not real course material; it
   exercises no learner-facing surface; and it does not freeze the course
   schema). No em dash characters.
  </action>
  <verify>
  <automated>python tests/four_subject_review.py</automated>
Expected: final line `TRACER: N passed, 0 skipped, 0 failed` with the real pass
count, and exit 0. Also run
`for t in tests/*.py; do python "$t" || exit 1; done`, expected exit 0, and
`python itembank.py guard .`, expected `0 offending files`. Degraded states
this tracer proves: an active profile naming no registered profile, an empty
profile list, a source whose rights are all unknown, a heading-similarity
decoy, thirteen distinct interruption points, and a full reversal back to the
pre-operation bytes.
  </verify>
  <acceptance_criteria>
- `python tests/four_subject_review.py` exits 0 and its final line matches the
  pattern `TRACER: ` followed by counts ending in `0 failed`.
- `for t in tests/*.py; do python "$t" || exit 1; done` exits 0.
- `python itembank.py guard .` prints `0 offending files` and exits 0.
- `tests/four_subject_review.py` contains all ten function definitions named in
  the artifacts section.
- `fixtures/corpus_14b.py` contains `def build_four_subjects(` and
  `def build_all_15a(`.
- `python -c "import sys; sys.path.insert(0,'fixtures'); import mock_backends,inspect; s=inspect.getsource(mock_backends); print(s.count('def candidate_for('))"`
  prints `1`.
- `.planning/phases/15A-director-treatment-policy/15A-TRACER-REPORT.md` exists
  with all five named sections.
- Every figure in the report's Measured budgets section carries a unit and the
  machine and Python version it was measured on.
- None of `fixtures/corpus_14b.py`, `fixtures/mock_backends.py`,
  `tests/four_subject_review.py`, or `15A-TRACER-REPORT.md` contains an em dash
  character.
  </acceptance_criteria>
  <done>All six requirement Fixture sentences are implemented by named scenario
  functions in one tracer, the tracer is green, and its report records measured
  figures rather than promised ones.</done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <name>Task 2: the four-subject recommendation review a human signs</name>
  <files>.planning/phases/15A-director-treatment-policy/15A-REVIEW.md</files>
  <read_first>
- `.planning/phases/15A-director-treatment-policy/15A-TRACER-REPORT.md` as
  written by Task 1, in full.
- `.planning/ROADMAP.md`, the Phase 15A freeze-gate paragraph, quoted in this
  plan's objective.
- `.planning/PLANNING-DIRECTIVES.md` section 3a, the accepted-recommendation
  discipline paragraph, which names owner, verification, evidence class, and
  failure condition as required of every accepted recommendation.
- `.agents/skills/OPERATION-CONTRACT.md`, the thirteen protocol steps, so the
  reviewer reads the same checklist the tracer replayed against.
- `.planning/phases/14B-graph-course-package-prototype/14B-AUTHORABILITY-REVIEW.md`
  if it exists, the 14B precedent for a human review artifact of this shape.
  </read_first>
  <what-built>
Task 1 built and ran the four-subject recommendation review tracer: one
recommendation operation over four synthetic subject outlines, with one
objective bound to direct reading as a complete result and one left untreated,
replayed step by step from the operation journal against the thirteen-step
protocol checklist, run through a mock hosted and a mock local backend with
identical artifacts and journals, and with the egress log checked against an
independently computed approved-span set. The tracer is green and its measured
figures are recorded in `15A-TRACER-REPORT.md`.

What the tracer cannot decide is whether the recommendations are any good. A
green test proves the machinery is honest about what it did; it cannot tell you
that recommending `direct-reading` for a blueprint objective and
`worked-example` for an algebra objective are sensible calls. That judgment is
the freeze gate's actual subject, and an agent never signs it for itself.
  </what-built>
  <how-to-verify>
1. Read `.planning/phases/15A-director-treatment-policy/15A-TRACER-REPORT.md`
   end to end.

2. Run the tracer yourself and watch it:

```
python tests/four_subject_review.py
```

   Expected final line: `TRACER: N passed, 0 skipped, 0 failed`, exit code 0.

3. Print the four subjects' recommendation entries and read them as a course
   builder would, one subject at a time:

```
python tests/four_subject_review.py --print-recommendations
```

   For each of the four subjects, answer these five questions in
   `15A-REVIEW.md`:
   - Is the recommended treatment kind a defensible choice for that objective,
     or would a course builder have picked something else?
   - Is the rationale legible, and is it obvious that it is model synthesis
     rather than a passage from the source?
   - Are the citations pointing at something a reader could actually find?
   - Does the coverage state match what you would have said after reading the
     source span yourself?
   - Would you accept this recommendation, reject it, or send it back?

4. Read the untreated objective's entry specifically. Confirm that its reason
   is legible enough that a course builder reading only the report would know
   what to do next.

5. Read the direct-reading binding specifically. Confirm it reads as a
   completed decision and not as a failure to generate something.

6. Confirm Phase 13.9 has actually been walked: check that
   `.planning/phases/13.9-walking-skeleton/` contains at least one
   `*-SUMMARY.md` file and that the recorded evidence it names exists. If it
   has not been walked, say so; Task 3 will withhold the freeze on that leg.

7. Record every answer in
   `.planning/phases/15A-director-treatment-policy/15A-REVIEW.md` under a dated
   heading, with these sections: **What was reviewed**, **Per-subject
   judgments** (the five questions, four times), **Concerns**, **Verdict**
   (one of `accept`, `accept with concerns recorded`, or `reject`), and
   **Signed** (name and date).
  </how-to-verify>
  <acceptance_criteria>
- `.planning/phases/15A-director-treatment-policy/15A-REVIEW.md` exists with
  all five named sections.
- The Per-subject judgments section carries four subject blocks, each answering
  all five questions.
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
  <files>.planning/phases/15A-director-treatment-policy/15A-FREEZE.md, .planning/phases/15A-director-treatment-policy/15A-DECISIONS.md, .planning/phases/15A-director-treatment-policy/15A-VALIDATION.md</files>
  <read_first>
- `.planning/phases/15A-director-treatment-policy/15A-TRACER-REPORT.md` and
  `15A-REVIEW.md`, both in full, as written by Tasks 1 and 2.
- `.planning/phases/14B-graph-course-package-prototype/14B-FREEZE.md` as
  landed, the precedent this file follows in shape, including whether it opens
  with a `Freeze withheld` section.
- `.planning/phases/14A-identity-lifecycle-operation/14A-FREEZE.md` as landed.
- `.planning/ROADMAP.md`, the Phase 13.9 governance clause and the Phase 15A
  entry.
- `.planning/phases/15A-director-treatment-policy/15A-VALIDATION.md` in full,
  its empty Per-Task Verification Map, its runtime placeholder, and its
  sign-off checklist.
- `.planning/phases/15A-director-treatment-policy/15A-DECISIONS.md`, so the new
  section is appended below `## D-15A-2`.
  </read_first>
  <action>
1. Check the three freeze legs, in this order, and record the result of each:
   - **Leg 1, the tracer.** `python tests/four_subject_review.py` exits 0 with
     `0 failed`. Re-run it now rather than trusting Task 1's record.
   - **Leg 2, the human review.** `15A-REVIEW.md` exists, carries a Verdict of
     `accept` or `accept with concerns recorded`, and is signed with a name and
     a date. A verdict of `reject` fails this leg.
   - **Leg 3, Phase 13.9.** `.planning/phases/13.9-walking-skeleton/` contains
     at least one `*-SUMMARY.md` file. Its absence fails this leg, per
     ROADMAP.md's governance clause that no 14B-or-later freeze commits before
     the skeleton has been walked.

2. Write `.planning/phases/15A-director-treatment-policy/15A-FREEZE.md`.

   **If all three legs pass**, the file opens with the literal heading
   `## Frozen at 15A` and carries exactly these sections:
   - **What is frozen.** The public surface plans 01 through 05 built, listed
     symbol by symbol: `director.py`'s constants and functions,
     `schemas/treatment_recommendation.schema.json`, the fourth
     `model_adapter` operation and its payload key, the two `journal.py`
     additions, and the `settings.agent_policy` block. Each with its exact
     value or member list, so a later phase can re-verify against this file the
     way plan 15A-01's own precondition re-verified against 14A and 14B.
   - **What is NOT frozen.** In plain sentences: this is not the course schema
     freeze, not a lesson-profile freeze, not an agent job protocol freeze, and
     not a learner-facing surface freeze. It also does not freeze the two mock
     profiles or the fixture corpora, which are test data.
   - **Evidence.** The tracer command and its final line verbatim, the review
     verdict and signer, the Phase 13.9 file checked, and the date.
   - **Measured, not promised.** The figures from `15A-TRACER-REPORT.md`'s
     Measured budgets section, with their machine and Python version.
   - **Open items carried forward.** Every concern `15A-REVIEW.md` recorded,
     the flagged AGENT-02 unclassified edge assumption from plan 15A-01, and
     the two backstop truths from plans 15A-03 and 15A-05, each with the phase
     or reviewer that owns it.

   **If any leg fails**, the file instead opens with the literal heading
   `## Freeze withheld` followed immediately by a section naming each failing
   leg, what it would take to satisfy it, and one sentence stating that Phase
   15A stays open. Do not write `## Frozen at 15A` anywhere in that version of
   the file. Do not describe a failing leg as satisfied and do not omit it.

3. Append to `15A-DECISIONS.md` a dated section
   `## D-15A-3. The Phase 15A freeze scope` recording the freeze-scope decision
   this plan's objective table locked, in the same voice the earlier two
   sections use, and stating explicitly that 15A does not freeze the course
   schema.

4. Fill `15A-VALIDATION.md`:
   - Populate the **Per-Task Verification Map** with one row per task across
     all six plans, in plan and task order, carrying the plan id, the task
     name, the requirement ids, the behavior in one phrase, the test type, the
     automated command verbatim, the assertion function name, and a Status of
     `pass` or the reason it is not.
   - Replace the **Estimated runtime** placeholder in the Test Infrastructure
     table with the measured full-suite figure from
     `15A-TRACER-REPORT.md`, labeled measured and dated, with the machine
     named.
   - Fill the **Manual-Only Verifications** table's Test Instructions cell with
     a pointer to Task 2's `how-to-verify` steps and to `15A-REVIEW.md`.
   - Replace the **Max feedback latency** placeholder with the measured
     single-file `python tests/director_roundtrip.py` figure.
   - Check the six **Validation Sign-Off** boxes that are genuinely satisfied
     and leave any that are not unchecked with a one-line reason beneath.
   - Set `nyquist_compliant: true` in the frontmatter only if every task in the
     map has an automated command and no three consecutive tasks lack one.
     Otherwise leave it `false` and say why.
   - Set `status: validated` in the frontmatter only when the freeze legs all
     passed.

5. Run `python itembank.py guard .` and confirm `0 offending files`. Run
   `for t in tests/*.py; do python "$t" || exit 1; done` one final time and
   confirm exit 0.
  </action>
  <verify>
  <automated>python tests/four_subject_review.py && python itembank.py guard .</automated>
Expected: the tracer's final line ends in `0 failed` and exits 0, and guard
prints `0 offending files`. The degraded behavior this task must prove rather
than paper over is the withholding itself: if any leg fails, the freeze file
opens with `## Freeze withheld`, the string `## Frozen at 15A` appears nowhere
in it, and the phase stays open. Confirm by checking both conditions on
whichever branch actually ran.
  </verify>
  <acceptance_criteria>
- `python tests/four_subject_review.py` exits 0.
- `for t in tests/*.py; do python "$t" || exit 1; done` exits 0.
- `python itembank.py guard .` prints `0 offending files` and exits 0.
- `.planning/phases/15A-director-treatment-policy/15A-FREEZE.md` exists and
  contains exactly one of the headings `## Frozen at 15A` or
  `## Freeze withheld`, never both.
- When the heading is `## Frozen at 15A`, the file carries all five named
  sections, and its What is frozen section names `director.PROTOCOL_STEPS`,
  `director.AGENT_ENTRY_KEYS`, `director.EGRESS_KEYS`,
  `director.AUTONOMY_LEVELS`, `director.MATCH_KINDS`, and
  `director.OMISSION_REASONS` with their exact member lists.
- When the heading is `## Freeze withheld`, every failing leg is named and the
  string `## Frozen at 15A` does not appear in the file.
- `15A-DECISIONS.md` contains the literal heading
  `## D-15A-3. The Phase 15A freeze scope`.
- `15A-VALIDATION.md`'s Per-Task Verification Map has at least one row per task
  across all six plans, and its Estimated runtime cell no longer contains the
  word `Unknown`.
- `15A-VALIDATION.md`'s Max feedback latency line no longer contains the phrase
  `to be measured`.
- None of `15A-FREEZE.md`, `15A-DECISIONS.md`, or `15A-VALIDATION.md` contains
  an em dash character.
  </acceptance_criteria>
  <precondition>Task 1's tracer is green and Task 2's review is recorded and signed.</precondition>
  <done>Phase 15A is either frozen with its surface enumerated and its evidence
  recorded, or held open with the missing leg named.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| tracer to shipped suites | A green phase tracer could mask a regression in the shipped runtime if it does not run those suites itself. |
| fixture corpus to repository | Synthetic subject material enters version control and could drift toward real course content. |
| freeze record to later phases | Whatever this file says is frozen is what plan 15B-01's precondition will assert against. |
| human review to freeze | A signature is the only thing standing between a green machine and an accepted claim about recommendation quality. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-15A-06-01 | Spoofing | an agent self-certifying the recommendation review | high | mitigate | The review is a blocking `checkpoint:human-verify` producing a signed file with a named verdict; Task 3 fails leg 2 on a missing signature or a reject verdict, and the freeze is withheld by name. |
| T-15A-06-02 | Tampering | an egress assertion that compares a function to itself | high | mitigate | The expected approved-span set is computed independently in the tracer from the registry and the treatment rights map, and the plan forbids calling `director.approved_spans` to build it. The comparison is set equality in both directions. |
| T-15A-06-03 | Tampering | a parity assertion made meaningless by a writing first run | high | mitigate | Both parity runs use `recommend-only` autonomy against one course root, and the scenario asserts the sidecar revision is unchanged across both, so neither run could have mutated what the other read. |
| T-15A-06-04 | Information Disclosure | real course, exam, or learner content entering the repository through the fourth subject | high | mitigate | Every fixture string is fictional and generated from the existing fixed seed, the plan forbids paraphrase as well as copying, and `python itembank.py guard .` is in the acceptance criteria of Tasks 1 and 3. |
| T-15A-06-05 | Repudiation | a freeze record claiming a leg that was not run | high | mitigate | Task 3 re-runs the tracer rather than trusting Task 1's record, checks the review file's verdict and signature, and checks the Phase 13.9 summary file. A failing leg produces a `## Freeze withheld` file in which the frozen heading appears nowhere, asserted in the acceptance criteria. |
| T-15A-06-06 | Repudiation | an invented budget figure in the tracer report | high | mitigate | `measure_budgets()` asserts nothing and only prints what the run produced, the report labels every figure measured with its machine and Python version, and the plan forbids any number that was not measured. |
| T-15A-06-07 | Tampering | a regression in the shipped runtime hidden behind a green phase tracer | high | mitigate | `shipped_suite_check()` runs three shipped suites as subprocesses before any 15A module is imported, and a red suite skips every scenario rather than reporting passes. The full suite runs again in Task 3. |
| T-15A-06-08 | Tampering | a second candidate builder making backend parity a coincidence | high | mitigate | Both transports call one `candidate_for`, asserted by a source count of exactly one definition and by comparing each transport's returned candidate to a direct in-process call. |
| T-15A-06-09 | Tampering | supply chain: a test framework, HTTP client, or fixture library introduced here | high | mitigate | None is added; the tracer is a direct-execution script using `json`, `os`, `subprocess`, `sys`, `tempfile`, `platform`, and `urllib`. Per `PLANNING-DIRECTIVES.md` section 4a the absence of dependencies is not itself the mitigation: any dependency ever added here is vendored at a pinned version with a recorded checksum and a named license review, following the KaTeX precedent in `09-03-PLAN.md`. |
| T-15A-06-10 | Denial of Service | the fixture HTTP server binding a port another process holds | low | accept | `serve` binds port `0` and reports the OS-assigned port, the same fallback `server.bind` already uses for the Windows Hyper-V case. Accepted because a bind failure is a loud, local test failure with no data at risk. |
</threat_model>

<out_of_scope>
Refused by this plan, by name:

- No CLI command and no daemon route for accepting a recommendation.
  `15A-RESEARCH.md` Open Question 1 recommends the internal-API shape for this
  freeze gate and names any builder-facing surface as deferred to 16B.
- No real backend run. The gate is designed against mock profiles by
  AGENT-02's own Fixture sentence, and a real provider run is neither required
  nor sufficient for it.
- No real course, exam, syllabus, or learner content, and no paraphrase of any.
  The four subjects are fictional stand-ins whose only relationship to EMT,
  Math 1400, CSCI 1100, and a standardized exam is their shape.
- No new public function on `director.py`. This plan proves; it does not build.
  A fix forced by a red scenario is a fix, not a new capability, and is
  recorded as such.
- No course schema freeze. 14B's own freeze record already states it is not the
  course schema freeze, and 15A inherits that boundary and repeats it.
- No accessibility certification. This phase ships no learner-facing surface,
  the `preview` protocol step is recorded not-applicable with its reason, and
  an agent never self-certifies accessibility.
- No evidence-based remediation proposal. That is AGENT-03, owned by Phase 15B.
- No change to any module under `surfaces/`, to `schemas/`, or to `journal.py`,
  `identity.py`, `graph.py`, `course.py`, `model_adapter.py`, `model.py`,
  `runtime.py`, or `evidence.py`.
</out_of_scope>

<flagged_assumptions>
Carried forward into the freeze record's Open items section, not silently
dropped:

- **AGENT-02, unclassified edge row (unresolved).** The edge probe could not
  classify AGENT-02 into any shape category, so no acceptance criterion was
  derived from it. Its Fixture sentence is covered by
  `scenario_backend_parity()` and `scenario_backend_loss()`, and its
  prohibition list is covered by plans 15A-04 and 15A-05, but the row itself
  remains an open assumption for the phase verifier to review by hand.
- **The TREAT-02 encoding backstop (plan 15A-03).** Locator equality is exact
  after NFC and line-ending normalization, proven for the locator kinds the
  fixtures use; whether some future locator kind needs a normalization this
  function does not do is not proven and is owned by whichever phase introduces
  that locator kind.
- **The RELIABILITY-02 concurrency backstop (plan 15A-05).** The concurrent and
  interrupted cases the fixtures reach all leave one valid state; whether some
  interleaving exists that the fixture does not reach is not proven and is
  owned by the phase that first runs two agent clients against one course root
  in earnest.
</flagged_assumptions>

<summary_obligations>
`15A-06-SUMMARY.md` records: the tracer's full final output verbatim; the
review verdict, its signer, and every concern recorded; which of the three
freeze legs passed and which, if any, withheld the freeze; every defect Task 1
forced a fix for and what the fix was; the measured budget figures with their
machine and Python version; the Per-Task Verification Map's final row count and
whether `nyquist_compliant` was set true; and any deviation from this plan with
its reason.
</summary_obligations>

<output>
Create
`.planning/phases/15A-director-treatment-policy/15A-06-SUMMARY.md`
when done.
</output>
</content>
