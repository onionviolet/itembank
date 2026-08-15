---
phase: 14B-graph-course-package-prototype
plan: 06
type: execute
wave: 6
depends_on: ["14B-01", "14B-02", "14B-03", "14B-04", "14B-05"]
files_modified:
  - tests/three_domain_tracer.py
  - fixtures/corpus_14b.py
  - .planning/phases/14B-graph-course-package-prototype/14B-TRACER-REPORT.md
  - .planning/phases/14B-graph-course-package-prototype/14B-AUTHORABILITY-REVIEW.md
  - .planning/phases/14B-graph-course-package-prototype/14B-FREEZE.md
  - .planning/phases/14B-graph-course-package-prototype/14B-VALIDATION.md
  - .planning/REQUIREMENTS.md
  - .planning/phases/14B-graph-course-package-prototype/14B-DECISIONS.md
autonomous: false
requirements: [GRAPH-01, GRAPH-02, GRAPH-04, PORT-03]
must_haves:
  truths:
    - "The freeze gate is three-legged and all three legs are evidenced in one place: a green three-domain graph tracer, a clean restore drill, and an authorability review a human performed and signed."
    - "No 14B freeze closes before Phase 13.9 has been walked: the freeze task checks for the recorded 13.9 evidence as a precondition, and on its absence writes a Freeze withheld section naming exactly what is missing instead of a Frozen at 14B section (ROADMAP Phase 13.9 gate)."
    - "No freeze is declared on a red tracer: if the tracer's final line does not report zero failures, no freeze section is written, the red scenario is named, and Phase 14B stays open."
    - "The three-domain graph tracer proves GRAPH-01, GRAPH-02, and GRAPH-04 together on one synthetic corpus spanning three fictional domains with containers labeled module, week, and chapter, asserting the outline projection reads in plain Markdown and structural order mints no prerequisite edge."
    - "The tracer carries one edge of every registered type plus one deliberately unknown edge type, and asserts the unknown type renders as an advisory recommended-before and never a hard block (GRAPH-02 Fixture)."
    - "The tracer splits one synthetic objective and renames another, asserting a reviewed migration proposal is generated and unmigrated evidence reads unknown on the new identity (GRAPH-04 Fixture)."
    - "The tracer exports a synthetic course and restores it on a clean offline destination against its manifest, asserting every loss is reported (PORT-03 Fixture)."
    - "The authorability review is a human judgment and is never self-certified by the agent: an agent may prepare the artifact and run the round-trip assertion, and only a human records the sign-off."
    - "All nine probe-surfaced requirement edges are accounted for at the end of this phase: eight are authored as truths across plans 01 through 05, and one, the GRAPH-04 unclassified row, is carried forward as a flagged assumption in plan 14B-04's out-of-scope section. Nothing was silently dropped."
  prohibitions: []
  artifacts:
    - "tests/three_domain_tracer.py, the freeze-gate tracer following tests/file_fault_tracer.py's structure"
    - ".planning/phases/14B-graph-course-package-prototype/14B-TRACER-REPORT.md"
    - ".planning/phases/14B-graph-course-package-prototype/14B-AUTHORABILITY-REVIEW.md"
    - ".planning/phases/14B-graph-course-package-prototype/14B-FREEZE.md"
    - "14B-VALIDATION.md with its Per-Task Verification Map filled and its sign-off checked"
    - "14B-DECISIONS.md gains the dated D-14B-5 freeze-scope answer"
  key_links:
    - "The Phase 13.9 gate is a ROADMAP clause, not a comment: no 14B-or-later freeze closes before the walking skeleton has been walked. If the freeze task treats it as advisory, the phase that was inserted to keep a real learner slice ahead of durability work is quietly overtaken by durability work."
    - "The freeze declares what a later subphase may build against. Anything named as not frozen stays cheap to change; anything named as frozen costs a migration. A freeze that names everything is not a freeze, it is a commitment nobody can afford to keep."
---

<objective>
Close Phase 14B on its three-legged freeze gate, or leave it open with the
failing leg named. The ROADMAP's own entry for this phase states the gate:
"Freeze gate: three-domain graph tracer, clean restore, authorability review."
It also states a precondition this plan must check rather than assume, from the
Phase 13.9 entry: "Gate: no 14B-or-later freeze closes before this has been
walked."

This plan writes no new capability. It proves the ones plans 01 through 05
built, on one corpus, in one run, and records what may and may not be treated as
durable afterwards. Phase 14B is itself the reversible prototype
`PLANNING-DIRECTIVES.md` section 3a requires before a course schema freeze; the
freeze this plan declares is 14B's own interface freeze, not the course schema
freeze, and the freeze record says so explicitly so a later subphase does not
inherit a commitment this phase did not make.

Decisions already made, cited, and never re-derived here:

- **ROADMAP Phase 14B and Phase 13.9 entries**, quoted above.
- **`14A-04-PLAN.md` Task 4's discipline**: re-run the gate, capture the output
  verbatim, and if the failed count is not zero, stop, write no freeze section,
  and report which scenario is red. A freeze declared on a red tracer is the one
  outcome that task existed to prevent, and it is the one outcome this task
  exists to prevent.
- **PLANNING-DIRECTIVES section 3a**: reversible prototypes precede durable
  commitment. Both required prototypes exist: the graph-to-outline projection
  in plan 14B-02 and the version migration in plan 14B-03.
- **`OPERATION-CONTRACT.md`**: "An agent never self-certifies accessibility."
  The authorability review is the same class of judgment and is recorded by a
  human.

Purpose: a format other phases build against is either proven or it is not, and
the difference is written down in one place.
Output: the tracer, the tracer report, the authorability review, the freeze
record, and the requirement status updates.
</objective>

<context>
@.planning/phases/14B-graph-course-package-prototype/14B-RESEARCH.md
@.planning/phases/14B-graph-course-package-prototype/14B-VALIDATION.md
@.planning/phases/14B-graph-course-package-prototype/14B-01-PLAN.md
@.planning/phases/14B-graph-course-package-prototype/14B-05-PLAN.md
@.planning/phases/14A-identity-lifecycle-operation/14A-04-PLAN.md
@.planning/ROADMAP.md
@.planning/REQUIREMENTS.md
@.agents/skills/OPERATION-CONTRACT.md
</context>

## Artifacts this phase produces (plan 14B-06 share)

- `tests/three_domain_tracer.py` with these functions: `fail(msg)`,
  `shipped_suite_check()`, `scenario_three_domain_outline()`,
  `scenario_edge_vocabulary()`, `scenario_migration()`,
  `scenario_clean_restore()`, `scenario_authorability_roundtrip()`,
  `measure_budgets()`, and `main()`.
- `fixtures/corpus_14b.py` gains `build_all(dest)`, which builds the three
  domains, their sources with their rights values, their evidence seeds, and
  their stub course in one call, so the tracer sets up in one statement.
- `.planning/phases/14B-graph-course-package-prototype/14B-TRACER-REPORT.md`.
- `.planning/phases/14B-graph-course-package-prototype/14B-AUTHORABILITY-REVIEW.md`.
- `.planning/phases/14B-graph-course-package-prototype/14B-FREEZE.md`.
- `.planning/phases/14B-graph-course-package-prototype/14B-DECISIONS.md` gains
  the dated section `## D-14B-5. The Phase 14B freeze scope`.

No new module, no new public function on `graph.py`, `course.py`, or
`course_package.py`, no CLI command, no daemon route, and no journal record
type is produced by this plan.

<tasks>

<task type="auto">
  <name>Task 1: the three-domain graph tracer</name>
  <files>tests/three_domain_tracer.py, fixtures/corpus_14b.py</files>
  <read_first>
- `tests/file_fault_tracer.py` in full, as Phase 14A-04 delivered it: its named
  scenario functions, its `shipped_suite_check()` precondition, its final
  `TRACER: N passed, M skipped, 0 failed` line, and its exit-code discipline.
  This file is the structural template.
- `.planning/REQUIREMENTS.md` GRAPH-01, GRAPH-02, GRAPH-04, and PORT-03, in
  full, including all four Fixture sentences. Each scenario function below
  implements exactly one of them.
- `graph.py`, `course.py`, and `course_package.py` in full, as they stand after
  plan 14B-05.
- `fixtures/corpus_14b.py` in full, as it stands after plan 14B-05.
- `.planning/phases/14B-graph-course-package-prototype/14B-VALIDATION.md`, the
  Per-Task Verification Map and the Wave 0 Requirements list.
  </read_first>
  <action>
1. Add `build_all(dest)` to `fixtures/corpus_14b.py`, composing the existing
   builders into one call and returning a dict with the keys `domains` (a list
   of three course-root paths), `stub_root`, `evidence_seeds`, and `platform`
   (a dict recording whether symlinks and archive symlink entries were
   creatable, so a skip is recorded rather than silent).

2. Create `tests/three_domain_tracer.py`, following `tests/file_fault_tracer.py`
   exactly in structure. Its module docstring states in one paragraph what this
   tracer proves end to end and that it is the Phase 14B freeze gate.

3. Implement `shipped_suite_check()` as the FIRST thing `main()` calls. It runs
   the 14B subset `python tests/graph_roundtrip.py` and
   `python tests/course_package_roundtrip.py` plus the shipped anchors
   `python tests/scoring_roundtrip.py`, `python tests/evidence_roundtrip.py`,
   and `python tests/lesson_roundtrip.py` through `subprocess`. If any exits
   non-zero, print `PRECONDITION FAILED: <name> is red; the tracer does not run
   against a red suite` and exit 1. A tracer that runs against a red suite
   proves nothing.

4. Implement `scenario_three_domain_outline()`, which is GRAPH-01's Fixture
   sentence made executable. Over all three domains built by `build_all`:
   - Every container label used across the three domains includes `module`,
     `week`, and `chapter`, plus the invented label `fortnight`, and all four
     parse and render.
   - `graph.outline_projection(doc)` for each domain returns text whose every
     non-blank line begins with `#`, `-`, or a letter, contains no HTML tag,
     contains no JSON brace at the start of a line, and contains no em dash
     character. It reads in plain Markdown.
   - Writing each outline to a file and reading it back is byte-identical, and
     two calls to `outline_projection` on the same document return identical
     strings.
   - Across all three domains, the count of `prerequisite-of` edges equals
     exactly the number the generator wrote deliberately, and building the
     containers and objectives alone produces zero edges. Structural order
     mints no prerequisite edge.

5. Implement `scenario_edge_vocabulary()`, which is GRAPH-02's Fixture sentence
   made executable. On one document:
   - Add one edge of each of the four registered types, plus one edge with the
     deliberately unregistered type `alternate-path`, five edges in total.
   - Assert the unknown one reads `effective_type` `recommended-before`,
     `authority` `advisory`, and `override` `advisory`, and that it is still
     present in `doc["edges"]`, so it degraded rather than being dropped.
   - Assert the unknown one produces no order warning from
     `graph.validate_order`, and that setting its `override` cell to
     `hard-gate` in the file does not make it block: the effective override is
     still `advisory` after a round trip.
   - Assert all five edges survive a `serialize_course` and `parse_course` round
     trip with their original type strings intact.

6. Implement `scenario_migration()`, which is GRAPH-04's Fixture sentence made
   executable. On the `lantern-computing` domain, which carries a seeded
   evidence event:
   - Record the evidence event count before anything runs.
   - Split one objective into two and rename another.
   - Assert one reviewed migration proposal exists per operation, each with
     `state` `proposed`.
   - Assert the evidence event count is unchanged, the existing event still
     carries its original objective identity byte for byte, and each new
     identity has zero events.
   - Assert `graph.objective_evidence_state(doc, new_id, 0)` returns exactly
     `unknown`.

7. Implement `scenario_clean_restore()`, which is PORT-03's Fixture sentence
   made executable. Over one full domain:
   - Export the course, including its rights-restricted source, its linked
     source, and its unreachable-root source.
   - Restore into a `clean_machine_dest` with the environment overrides applied.
   - Assert `verify_manifest` reports `complete` True, that the restored sidecar
     bytes equal the original, and that both `losses` and `restore_losses` are
     returned.
   - Assert every loss category that applies to this corpus appears in the
     report with a non-empty reason: `external-link`, `rights-restricted`,
     `machine-local`, and `unreachable-source`. Every loss is reported.
   - Run the traversing-archive refusal once here too, so the freeze gate covers
     it directly rather than only through the roundtrip file.

8. Implement `scenario_authorability_roundtrip()`, the machine half of the
   authorability leg. Task 2 owns the human half.
   - Serialize a domain's sidecar, change exactly one `order` cell in the
     `## Structure` table by hand-editing the text with a string replacement,
     parse it, re-serialize it, and assert the diff between the original text
     and the final text is exactly one line. A human reordering two chapters by
     editing one cell must produce a one-line diff.
   - Assert the re-projected outline reflects the reordering, so a hand edit
     round-trips through the projection.
   - Assert the sidecar text contains no line longer than two hundred
     characters, so a table row stays readable in a plain editor without
     horizontal scrolling that defeats reading.

9. Implement `measure_budgets()` recording, and only recording, the wall-clock
   time of: one `build_all`, one full `outline_projection` over three domains,
   one `export_package`, and one `restore_package`. Print each as a line of the
   form `budget <name>: <seconds> s (measured on this machine, recorded not
   promised)`. No measurement is a build-breaking assertion. This follows
   D-12.6-10's own measured-not-promised posture, and `14B-RESEARCH.md` Open
   Question 3, which recommends no performance budget for the freeze gate.

10. Implement `main()` printing, as its final line, exactly
    `TRACER: %d passed, %d skipped, %d failed`, and exiting 0 only when the
    failed count is zero. Every skip prints its own named `SKIP:` line first,
    so a platform fallback is recorded rather than passing silently.

11. Run `python tests/three_domain_tracer.py` until green.
  </action>
  <verify>
  <automated>python tests/three_domain_tracer.py</automated>
Expected: final line `TRACER: N passed, M skipped, 0 failed`, exit code 0.
Degraded states this tracer proves in one run: an unknown edge type renders
advisory and never blocks; a prerequisite cycle is named and the outline still
renders; a migration leaves the evidence store untouched and the new identity
reads unknown; a rights-restricted source is named in the loss report rather
than packaged; an unreachable root is named; a traversing archive entry is
refused; and any platform that cannot create a symlink prints a named SKIP line
rather than passing silently.
  </verify>
  <acceptance_criteria>
- `python tests/three_domain_tracer.py` exits 0 and its final line matches
  `TRACER: ` followed by counts ending in `0 failed`.
- `tests/three_domain_tracer.py` contains `def shipped_suite_check(`,
  `def scenario_three_domain_outline(`, `def scenario_edge_vocabulary(`,
  `def scenario_migration(`, `def scenario_clean_restore(`,
  `def scenario_authorability_roundtrip(`, and `def measure_budgets(`.
- `python itembank.py guard .` prints `0 offending files` and exits 0.
- Running the tracer twice produces identical output apart from the
  `budget` lines.
- Neither `tests/three_domain_tracer.py` nor `fixtures/corpus_14b.py` contains
  an em dash character.
  </acceptance_criteria>
  <done>All four requirement Fixture sentences are executable scenario
  functions in one tracer, and the tracer refuses to run against a red
  suite.</done>
</task>

<task type="auto">
  <name>Task 2: the authorability review, prepared by the agent and signed by a human</name>
  <files>.planning/phases/14B-graph-course-package-prototype/14B-AUTHORABILITY-REVIEW.md, .planning/phases/14B-graph-course-package-prototype/14B-VALIDATION.md</files>
  <read_first>
- `.planning/phases/14B-graph-course-package-prototype/14B-VALIDATION.md`, the
  Manual-Only Verifications table, which already states this review's test
  instructions.
- `.agents/skills/OPERATION-CONTRACT.md`, protocol step 9 and the sentence "An
  agent never self-certifies accessibility". The same rule governs here.
- `14B-RESEARCH.md` "Common Pitfalls" number 8, which defines what this review
  actually tests: can a human open the file in a plain editor or in Obsidian
  and understand what it says without a decoder.
- `fixtures/sample_lanes.md`, the project's own readable pipe-table precedent,
  as the comparison point.
  </read_first>
  <action>
1. Generate the review inputs from the three-domain corpus and write them into
   a temp directory outside this repository, then create
   `.planning/phases/14B-graph-course-package-prototype/14B-AUTHORABILITY-REVIEW.md`
   with exactly these six sections and nothing more:

   - **What is being reviewed.** The `course-graph.md` sidecar and the outline
     projection for one domain, named, with their absolute temp paths.
   - **The machine half, already green.** The result of
     `scenario_authorability_roundtrip()` from Task 1, quoted: the one-line diff
     assertion, the reordering round trip, and the maximum line length.
   - **The five questions for the human.** Written out in full, each with a
     blank line under it for the answer:
     1. Open `course-graph.md` in a plain text editor. Without any tool, can
        you say what this course contains?
     2. Open the same file in Obsidian. Do the tables render, and is the file
        still readable?
     3. Reorder two chapters by editing one `order` cell by hand and save. Does
        the re-projected outline reflect your edit?
     4. Open the outline. Is it something you would be willing to read and edit
        as a course plan, or only something a tool produces?
     5. Is there any field in the sidecar whose meaning you cannot work out
        from the file alone?
   - **What a failure means.** One paragraph: a No to question 1, 2, or 5 fails
     this leg of the freeze gate. `14B-RESEARCH.md` Pitfall 8 names this as an
     outright gate failure, not a nice-to-have, and D-14A-1's own text requires
     the sidecar never to become the only readable copy.
   - **Accessibility scope note.** One paragraph stating that Phase 14B
     introduces no learner-facing surface, so the nine accessibility gates in
     `.planning/UI-SPEC.md` section 8 are not exercised by this phase and are
     not claimed as passed. This review is a plain-file readability judgment
     and is not an accessibility certification.
   - **Sign-off.** A dated line for a human answer of `authorable` or
     `not authorable`, with space for notes. Left blank by the agent.

   No em dash characters anywhere in the file.

2. Fill the Per-Task Verification Map in
   `.planning/phases/14B-graph-course-package-prototype/14B-VALIDATION.md` with
   one row per plan and task across plans 01 through 06, giving each its
   automated command and its status. Record the measured runtimes from Task 1's
   `measure_budgets()` output in the Estimated runtime row, replacing the
   placeholder text, and record the Max feedback latency as measured. Check the
   Validation Sign-Off boxes that are genuinely true and leave the rest
   unchecked. Set `nyquist_compliant: true` in the frontmatter only if every
   task in plans 01 through 06 has an automated verify or a named Wave 0
   dependency; otherwise leave it `false` and name the gap in the map.

3. Present the review to Weibao and record his answers verbatim in the
   Sign-off section. Do not answer the five questions on his behalf and do not
   record a sign-off he did not give.
  </action>
  <verify>
  <automated>python tests/three_domain_tracer.py</automated>
The machine half of this leg is `scenario_authorability_roundtrip()`, which the
tracer runs. The human half cannot be automated and is not claimed to be.
  <human-check>Weibao opens the generated `course-graph.md` in a plain text
  editor and in Obsidian, answers the five questions in
  `14B-AUTHORABILITY-REVIEW.md`, hand-edits one `order` cell, confirms the
  re-projected outline reflects the edit, and records `authorable` or
  `not authorable` with the date. An agent never records this answer on his
  behalf.</human-check>
  </verify>
  <acceptance_criteria>
- `.planning/phases/14B-graph-course-package-prototype/14B-AUTHORABILITY-REVIEW.md`
  exists with all six named sections.
- The Sign-off section contains a dated line reading exactly `authorable` or
  exactly `not authorable`, recorded by Weibao.
- `.planning/phases/14B-graph-course-package-prototype/14B-VALIDATION.md`
  Per-Task Verification Map has one row per task across plans 01 through 06,
  and the Estimated runtime row holds a measured figure rather than the word
  Unknown.
- `14B-AUTHORABILITY-REVIEW.md` contains no em dash character.
  </acceptance_criteria>
  <precondition>Task 1's tracer is green, so the generated sidecar and outline the human reviews are the ones the tracer proved.</precondition>
  <done>The authorability leg has both halves: a green machine round-trip
  assertion and a dated human judgment the agent did not write.</done>
</task>

<task type="checkpoint:decision" gate="blocking">
  <name>Task 3: confirm the freeze scope before anything is declared durable</name>
  <files>.planning/phases/14B-graph-course-package-prototype/14B-DECISIONS.md</files>
  <read_first>
- Task 4 step 4 of this plan, the proposed Frozen and Not frozen lists, in
  full. They are the options' content and must be presented verbatim.
- `.planning/phases/14A-identity-lifecycle-operation/14A-FREEZE.md`, the
  `## Frozen at 14A` section, as the precedent for what a freeze record says
  and what it deliberately leaves open.
- The tracer output from Task 1 and the sign-off line from Task 2 of this plan,
  plus the three Phase 13.9 check results from Task 4 step 2. The answer is
  given against real evidence, never against a prediction.
- `.planning/ROADMAP.md`, the subphase dependency table showing that 15A, 15B,
  16A, and 16C all depend on 14B, so the reader knows what composes onto this.
- `.planning/PLANNING-DIRECTIVES.md` section 3a, the reversible-prototype
  paragraph, for why this freeze is not the course schema freeze.
- `.planning/phases/14B-graph-course-package-prototype/14B-DECISIONS.md`, so
  the new section is appended.
  </read_first>
  <decision>
Which Phase 14B interfaces are declared frozen, and which stay deliberately
changeable?
  </decision>
  <context>
Task 4 writes a freeze record later subphases build against. Naming an item
frozen and then changing it forces a migration of every artifact written under
it; naming too little frozen means Phase 15A and Phase 16A have nothing stable
to compose onto. This is the last point at which the scope can be adjusted for
free.

Present the proposed frozen list and the proposed not-frozen list from Task 4
step 4 verbatim, alongside the three legs' evidence from Tasks 1 and 2 and the
three Phase 13.9 checks, so the answer is given against real results rather
than against a plan's prediction.
  </context>
  <options>
    <option id="option-a">
      <name>RECOMMENDED DEFAULT: freeze the vocabularies and the record shapes, leave copy and layout changeable</name>
      <pros>Freezes the sidecar file name and section order, the seven table
      column sets, the four-name edge vocabulary and its three closed field
      sets, the unknown-type downgrade rule, the eleven treatment kinds and
      their rights mapping, the five migration kinds and three states, the
      seven-key manifest and its five-key entry shape, and the five loss
      categories. Leaves refusal wording, outline formatting, loss report reason
      sentences, and internal directory names free. This is exactly the split
      Phase 14A used: freeze what a consumer parses, leave what a human
      reads.</pros>
      <cons>The treatment rights mapping and the loss categories are the
      youngest of these decisions, proven only against three synthetic domains
      and never against a real course.</cons>
    </option>
    <option id="option-b">
      <name>Freeze less: vocabularies only, record shapes stay open</name>
      <pros>The column sets and the manifest entry shape stay cheap to change
      through Phase 15A, when a real course first exercises them.</pros>
      <cons>Phase 15A and Phase 16A would compose onto shapes that may still
      move, which is the coupling the subphase table's freeze gates exist to
      prevent.</cons>
    </option>
    <option id="option-c">
      <name>Withhold the freeze deliberately even on three green legs</name>
      <pros>Nothing is committed until a real course has run through the graph,
      which the walking skeleton starts and Phase 15A completes.</pros>
      <cons>Phase 15A depends on 14B in the ROADMAP subphase table; withholding
      leaves it with no stable base and moves the decision rather than making
      it.</cons>
    </option>
  </options>
  <action>
Present all three options with the recommended default named, alongside the
verbatim evidence from Tasks 1 and 2 and the three Phase 13.9 check results
from Task 4 step 2, and record the answer in
`.planning/phases/14B-graph-course-package-prototype/14B-DECISIONS.md` under a
dated heading `## D-14B-5. The Phase 14B freeze scope`.

What the executor does with each answer:

- **option-a**: proceed as Task 4 step 4 is written.
- **option-b**: before Task 4, move the seven table column sets, the manifest
  key set, and the entry key set from the Frozen subsection to the Not frozen
  subsection, and record in `14B-DECISIONS.md` which later subphase is expected
  to freeze them and on what evidence.
- **option-c**: before Task 4, write only a `## Freeze withheld` section naming
  this decision as the reason rather than a missing leg, leave the four
  `REQUIREMENTS.md` rows as `Pending`, and record in `14B-DECISIONS.md` what
  evidence would change the answer.

If the Phase 13.9 precondition in Task 4 step 2 fails or the tracer is red, this
checkpoint is not asked at all: the freeze is withheld on that ground and Task 4
writes the `## Freeze withheld` section directly.

Do not proceed with a silent default. An unanswered checkpoint stops the wave.
  </action>
  <verify>
`14B-DECISIONS.md` contains a dated `## D-14B-5` heading naming exactly one of
`option-a`, `option-b`, or `option-c`, with Weibao's answer recorded verbatim.
  </verify>
  <acceptance_criteria>
- `.planning/phases/14B-graph-course-package-prototype/14B-DECISIONS.md`
  contains the literal heading `## D-14B-5. The Phase 14B freeze scope`.
- The recorded answer names exactly one of `option-a`, `option-b`, `option-c`.
- The file contains no em dash character.
  </acceptance_criteria>
  <reversibility rating="one-way">A freeze record is what Phase 15A, 15B, 16A,
  and 16C build against. Naming an item frozen and then changing it forces a
  migration of every artifact written under it.</reversibility>
  <resume-signal>Reply with `option-a`, `option-b`, or `option-c`.</resume-signal>
</task>

<task type="auto">
  <name>Task 4: check the Phase 13.9 gate, then declare the freeze or withhold it</name>
  <files>.planning/phases/14B-graph-course-package-prototype/14B-TRACER-REPORT.md, .planning/phases/14B-graph-course-package-prototype/14B-FREEZE.md, .planning/REQUIREMENTS.md</files>
  <read_first>
- `.planning/ROADMAP.md`, the Phase 13.9 entry and the Phase 14B entry, in
  full. The Phase 13.9 entry's final sentence is the precondition this task
  checks: "Gate: no 14B-or-later freeze closes before this has been walked."
- `.planning/phases/13.9-walking-skeleton/13.9-01-PLAN.md`,
  `13.9-02-PLAN.md`, and `13.9-03-PLAN.md`, for what their completion produces
  and therefore what this task looks for.
- `.planning/phases/14A-identity-lifecycle-operation/14A-04-PLAN.md` Task 4, in
  full. This task copies its four-subsection freeze-record shape and its
  no-freeze-on-red discipline exactly.
- The tracer's final output line from Task 1, and the sign-off line from Task 2.
- `.planning/REQUIREMENTS.md`, the status table rows for GRAPH-01, GRAPH-02,
  GRAPH-04, and PORT-03.
  </read_first>
  <action>
1. Re-run all three legs one final time and capture the output verbatim.
   - `python tests/three_domain_tracer.py`. Expected final line
     `TRACER: N passed, M skipped, 0 failed`, exit code 0.
   - `for t in tests/*.py; do python "$t" || exit 1; done`. Expected exit 0.
   - `python itembank.py guard .`. Expected final line `0 offending files`,
     exit code 0.
   If the tracer's failed count is not zero, STOP. Write no freeze section.
   Write `14B-TRACER-REPORT.md` naming the red scenario and its output, and
   report that Phase 14B stays open. A freeze declared on a red tracer is the
   one outcome this task exists to prevent.

2. Check the Phase 13.9 precondition explicitly. It is satisfied only when ALL
   of the following are true:
   - `.planning/phases/13.9-walking-skeleton/13.9-DECISIONS.md` exists and
     contains a dated approval line for the objective map.
   - `.planning/phases/13.9-walking-skeleton/13.9-01-SUMMARY.md`,
     `13.9-02-SUMMARY.md`, and `13.9-03-SUMMARY.md` all exist.
   - `.planning/ROADMAP.md`'s Phase 13.9 entry is marked complete.
   Record the result of each of the three checks, `ok` or `missing`, by name.

3. Write `14B-TRACER-REPORT.md` with exactly these five sections:
   - **The three legs.** One subsection each for the three-domain graph tracer,
     the clean restore drill, and the authorability review, each quoting its
     evidence verbatim: the tracer's final line, the restore report's
     `entries_verified` and both loss lists, and the authorability sign-off
     line.
   - **The four Fixture sentences.** One row per requirement, quoting the
     Fixture sentence from `REQUIREMENTS.md` and naming the scenario function
     that implements it.
   - **Measured, not promised.** The `budget` lines from `measure_budgets()`,
     verbatim, with a sentence stating these are single measurements on one
     machine and are not budgets any later phase may assert against.
   - **Platform fallbacks.** Every named SKIP line the tracer printed, with the
     platform it ran on.
   - **The nine probe-surfaced edges.** A table with one row per edge, naming
     the requirement, the edge category, and where it landed: eight as truths in
     plans 01 through 05, and the GRAPH-04 unclassified row as a flagged
     assumption in plan 14B-04's out-of-scope section. State the equality
     explicitly: nine surfaced, eight authored, one flagged, zero dropped.

4. Write `14B-FREEZE.md`.

   **If the Phase 13.9 precondition in step 2 was NOT satisfied**, write a
   `## Freeze withheld` section instead of a freeze, naming which of the three
   13.9 checks failed, quoting the ROADMAP gate sentence, and stating in one
   sentence that every interface in this phase remains changeable until the
   walking skeleton has been walked and this task is re-run. Do not write a
   `## Frozen at 14B` section. Then stop at step 6.

   **If it WAS satisfied and all three legs are green**, write a
   `## Frozen at 14B` section naming, in one place, exactly what is now frozen
   and what deliberately is not:

   - **Frozen.** The course sidecar's file name and its section order; the
     column set of each of the seven tables; the four-name edge vocabulary and
     the three closed sets for authority, confidence, and override; the
     downgrade rule for an unknown edge type; the eleven treatment kinds and
     their rights mapping; the five migration kinds and three migration states;
     the seven-key package manifest and its five-key entry shape; and the five
     loss categories.
   - **Not frozen, and deliberately so.** The refusal message wording, which is
     copy and not contract; the outline projection's exact heading and list
     formatting, which is presentation; the loss report's reason sentences; the
     `_journal` and package internal directory names, which are local layout; and
     everything routed to a later subphase in the five out-of-scope sections.
   - **What this freeze is NOT.** One paragraph stating in plain sentences that
     Phase 14B is the reversible prototype `PLANNING-DIRECTIVES.md` section 3a
     requires before a course schema freeze, that the course schema freeze
     belongs to a later subphase, and that a later phase inheriting this record
     must not read it as a course schema freeze it did not make.
   - **The evidence.** The tracer's final line quoted verbatim, the full suite
     result, the guard result, the authorability sign-off, the three Phase 13.9
     checks, and a pointer to `14B-TRACER-REPORT.md`.
   - **What breaks if this is changed later.** One sentence per frozen item
     naming the migration it would force.

   No em dash characters anywhere in the file.

5. Update `.planning/REQUIREMENTS.md`'s status table rows for `GRAPH-01`,
   `GRAPH-02`, `GRAPH-04`, and `PORT-03` from `Pending` to `Complete`, editing
   only those four rows and nothing else in the file. Do this only when step 4
   wrote a `## Frozen at 14B` section. If the freeze was withheld, leave all
   four rows as `Pending` and record that in the tracer report.

6. Run `python itembank.py guard .` one last time and confirm
   `0 offending files`.
  </action>
  <verify>
  <automated>python tests/three_domain_tracer.py</automated>
Expected: exit 0 with a failed count of zero. Then
`for t in tests/*.py; do python "$t" || exit 1; done`, expected exit 0, and
`python itembank.py guard .`, expected `0 offending files`. The degraded
behavior this task must honor rather than paper over is the withheld freeze: if
the Phase 13.9 evidence is absent or the tracer is red, no freeze section is
written, the missing item is named, and the four requirement rows stay
`Pending`. Both outcomes are correct results of this task; only a freeze
declared on a red tracer or an unwalked skeleton is a failure.
  </verify>
  <acceptance_criteria>
- `python tests/three_domain_tracer.py` exits 0 with `0 failed` in its final
  line.
- `for t in tests/*.py; do python "$t" || exit 1; done` exits 0.
- `python itembank.py guard .` prints `0 offending files` and exits 0.
- `.planning/phases/14B-graph-course-package-prototype/14B-TRACER-REPORT.md`
  exists with all five named sections, and its ninth-edge table states nine
  surfaced, eight authored, one flagged, zero dropped.
- `.planning/phases/14B-graph-course-package-prototype/14B-FREEZE.md` contains
  exactly one of the headings `## Frozen at 14B` or `## Freeze withheld`, never
  both.
- If `## Frozen at 14B` is present, it contains all five named subsections and
  the tracer's final line quoted verbatim, and
  `git diff --stat .planning/REQUIREMENTS.md` reports four changed lines.
- If `## Freeze withheld` is present, `git diff --name-only` does not list
  `.planning/REQUIREMENTS.md`.
- `14B-FREEZE.md` and `14B-TRACER-REPORT.md` contain no em dash character.
  </acceptance_criteria>
  <precondition>Phase 13.9 has been walked: `13.9-DECISIONS.md` carries a dated approval line and `13.9-01-SUMMARY.md`, `13.9-02-SUMMARY.md`, and `13.9-03-SUMMARY.md` all exist. If this is not true, the freeze is withheld rather than declared.</precondition>
  <reversibility rating="one-way">A freeze record is what later subphases build
  against. Naming an item frozen and then changing it forces a migration of
  every artifact written under it, which is why the record also names, in the
  same place, everything that is deliberately not frozen.</reversibility>
  <done>Phase 14B is either frozen on three green legs with the Phase 13.9 gate
  satisfied and the evidence recorded in one place, or it stays open with the
  missing leg named.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| tracer result to freeze record | A green or red tracer decides whether a format later subphases build against is declared durable. |
| tracer to repository | The tracer generates a three-domain corpus and writes reports into this repository; both are paths where synthetic content could leak into committed content. |
| measurement to record | A number measured once on one machine becomes a written record a later phase could read as a guarantee. |
| agent judgment to human sign-off | An agent could record an authorability verdict it is not permitted to give. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-14B-06-01 | Repudiation | a freeze declared on a red tracer or an unwalked walking skeleton | high | mitigate | Task 4 step 1 stops on a non-zero failed count and writes no freeze section; step 2 checks three named Phase 13.9 artifacts and writes `## Freeze withheld` on any miss; Task 3 is a blocking checkpoint that puts the freeze scope in front of a human against real evidence before anything is declared durable; the acceptance criteria assert exactly one of the two headings is present and that `REQUIREMENTS.md` is untouched when the freeze is withheld. |
| T-14B-06-02 | Spoofing | an agent recording an authorability verdict a human did not give | high | mitigate | The sign-off line is left blank by the agent and the acceptance criterion requires a dated human answer of exactly `authorable` or `not authorable`. `OPERATION-CONTRACT.md` states an agent never self-certifies this class of judgment, and the review file states it too. |
| T-14B-06-03 | Repudiation | a single measurement read by a later phase as a performance guarantee | medium | mitigate | `measure_budgets` prints each figure with the words measured not promised, no measurement is an assertion, and the tracer report repeats the caveat in its own section. This follows D-12.6-10's stated posture and `14B-RESEARCH.md` Open Question 3. |
| T-14B-06-04 | Information Disclosure | real course or learner content entering the repository through the tracer corpus or the review artifacts | high | mitigate | The corpus is generated and fictional, the review inputs are written to a temp directory outside this repository, and `python itembank.py guard .` runs twice in this plan's acceptance criteria. |
| T-14B-06-05 | Tampering | a tracer that runs against a red suite and therefore proves nothing | high | mitigate | `shipped_suite_check()` is the first call in `main()` and exits 1 with a named message if any of the five named suites is red. |
| T-14B-06-06 | Repudiation | a platform fallback passing silently as a pass | medium | mitigate | Every skip prints a named `SKIP:` line, the final line reports the skipped count separately from the passed count, and the tracer report has a Platform fallbacks section that lists them. |
| T-14B-06-07 | Repudiation | a probe-surfaced requirement edge silently dropped between planning and verification | high | mitigate | The tracer report's fifth section is a table of all nine edges with where each landed, and states the equality explicitly: nine surfaced, eight authored, one flagged, zero dropped. |
| T-14B-06-08 | Tampering | a freeze record read by a later subphase as a course schema freeze this phase did not make | high | mitigate | The freeze record carries a required `What this freeze is NOT` paragraph stating that Phase 14B is the section 3a reversible prototype and that the course schema freeze belongs to a later subphase. |
| T-14B-06-09 | Tampering | supply chain: a test, reporting, or measurement package added for the tracer | high | mitigate | None is added; `subprocess`, `time`, `tempfile`, and `json` are Python 3.11 standard library and the project uses no test framework. Per `PLANNING-DIRECTIVES.md` section 4a the absence of dependencies is not the mitigation: any dependency added here is vendored at a pinned version with a recorded checksum and a named license review, the KaTeX precedent. |
</threat_model>

<out_of_scope>
Refused by this plan, by name:

- No new capability of any kind. This plan proves what plans 01 through 05
  built and adds no public function to `graph.py`, `course.py`, or
  `course_package.py`.
- No CLI command, no daemon route, no skill documentation. The 999.5 rule
  holds: a skill documents only a shipped command surface, and this phase ships
  none. The `discovery-and-binding` skill stays a stub until a phase ships its
  surface.
- No course schema freeze. Phase 14B is the reversible prototype
  `PLANNING-DIRECTIVES.md` section 3a requires before one; the freeze record
  says so in its own required subsection.
- No accessibility certification. Phase 14B introduces no learner-facing
  surface, so the nine gates in `.planning/UI-SPEC.md` section 8 are not
  exercised and are not claimed.
- No change to `identity.py`, `journal.py`, `discovery.py`, `evidence.py`,
  `model.py`, `runtime.py`, `graph.py`, `course.py`, `course_package.py`,
  `schemas/`, or anything under `surfaces/`.
- No edit to `.planning/REQUIREMENTS.md` beyond exactly four status rows, and
  none at all if the freeze is withheld.
- No 100k-file corpus and no performance budget assertion. `14B-RESEARCH.md`
  Open Question 3 recommends no budget measurement as a gate, and D-12.6-10's
  100k size was routed to Phase 14A and deferred there with its reason
  recorded.
- No resolution of the flagged GRAPH-04 unclassified edge by inventing a demand
  vocabulary. It is carried into the tracer report as a flagged assumption for
  the reviewer, exactly as plan 14B-04 recorded it.
</out_of_scope>

<summary_obligations>
`14B-06-SUMMARY.md` records: the tracer's final line verbatim; the three Phase
13.9 precondition check results by name; the option Weibao chose at Task 3 and
any change it forced in the freeze scope; whether a freeze was declared or
withheld and why; the authorability sign-off verbatim; the measured budget
lines; every platform fallback that fired; the nine-edge tally; the disposition
of the flagged GRAPH-04 unclassified edge; which truth was verified by which
command; and any deviation from this plan with its reason.
</summary_obligations>

<output>
Create
`.planning/phases/14B-graph-course-package-prototype/14B-06-SUMMARY.md`
when done.
</output>
