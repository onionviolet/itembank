---
phase: 15B-quality-blueprint-acceptance
plan: 05
type: execute
wave: 5
depends_on: ["15B-04"]
files_modified:
  - blueprint.py
  - schemas/course_audit_report.schema.json
  - fixtures/corpus_15b.py
  - tests/blueprint_roundtrip.py
  - .planning/phases/15B-quality-blueprint-acceptance/15B-DECISIONS.md
autonomous: false
requirements: [ACTIVITY-02, RELIABILITY-03]
estimate:
  tokens: 70000
  raw_tokens: 70000
  tasks: 2
  confidence: low
must_haves:
  truths:
    - "The course audit is a read-only aggregation over four signals a caller has already computed (treatment state, coverage state, quality findings, blueprint compliance); blueprint.course_audit recomputes none of the four, reads no file, and calls no classifier that produced any of them."
    - "Every coverage row in the report names which of the three existing vocabularies its state came from in a required vocabulary field whose value is a member of blueprint.COVERAGE_VOCABULARIES, and a row whose state is not a member of the vocabulary it names is refused before the report is returned."
    - "blueprint.COVERAGE_VOCABULARIES has exactly three members and blueprint.py defines no coverage-state tuple of its own; a fourth vocabulary cannot be minted because the audit never invents a state, it only carries one forward with its provenance attached."
    - "The report carries a stale boolean derived at build time from the supplied fingerprint pair, following the shipped audit_report.schema.json field of the same name, and a stale report is never treated as current: a stale course audit names every stale input in its own stale_inputs list rather than only setting a flag."
    - "The report is deterministic: two calls over the same four signals produce byte-identical canonical_json renderings, rows are sorted by (objective_id, vocabulary, source_object_id), and shuffling any input list does not change the output."
    - "No aggregate value appears anywhere in the report: a recursive walk finds no float and no key whose lowercase name contains mastery, completion, readiness, progress, percent, or score, so a reader cannot mistake a count for a mastery claim."
    - "An empty course produces a valid report rather than an error: course_audit over zero objectives returns a report whose rows list is empty, whose counts are all zero, and which still names its course, its fingerprints, and its stale state."
  prohibitions:
    - statement: "A fourth coverage-state vocabulary must not be minted, and the three existing vocabularies must not be renamed, merged, or unified into a reconciling superset."
      status: kept
      verification: flagged-unverified
    - statement: "A course-audit row must not carry a state without naming which vocabulary it came from; a state that could plausibly have come from either graph.BINDING_STATES or auditor.coverage_report without the row saying which is a claim with no provenance."
      status: kept
      verification: flagged-unverified
    - statement: "The audit must not recompute a signal it was given; re-deriving coverage, treatment state, or quality findings inside the audit produces a second answer that can silently disagree with the one that was recorded."
      status: kept
      verification: flagged-unverified
  artifacts:
    - "schemas/course_audit_report.schema.json, x-itembank-version 1, or the recorded alternative from D-15B-3"
    - "blueprint.py gains COVERAGE_VOCABULARIES, AUDIT_ROW_KEYS, AUDIT_REPORT_KEYS, audit_row, and course_audit"
    - "blueprint.BLUEPRINT_CODES gains two members: blueprint.unknown_vocabulary and blueprint.state_not_in_vocabulary"
    - "fixtures/corpus_15b.py gains build_audit_signals"
    - "tests/blueprint_roundtrip.py gains check_course_audit"
    - "15B-DECISIONS.md gains the dated D-15B-3 section"
  key_links:
    - "The audit takes the four signals as arguments and never calls director.untreated_objectives, director.classify_coverage, auditor.coverage_report, authoring.quality_gate, or blueprint_gate itself. That is what keeps blueprint.py free of a director import and what makes the report a view of what was recorded rather than a second computation that can disagree with it."
    - "COVERAGE_VOCABULARIES is a tuple of vocabulary NAMES, not of states. It exists so a row can cite its source vocabulary without blueprint.py holding a copy of any vocabulary's members, which is exactly how a fourth vocabulary would get minted by accident. The member check reads the live tuple from the module that owns it."
    - "The stale field follows schemas/audit_report.schema.json's shipped stale field in meaning and derivation but lives in a separate schema, because that schema's coverage_row is bound by additionalProperties false to auditor.py's syllabus-to-bank pairing. Forcing an objective-to-source-to-blueprint pairing through the same $defs would require loosening additionalProperties on shipped Phase 11 fixtures, which is a real strictness regression."
---

<objective>
Aggregate what four already-computed signals say about one course into one
cited report, and say where each claim came from.

The ROADMAP 15B goal names the shape exactly, quoted: "a course audit
aggregates treatment state, coverage state, quality findings, and blueprint
compliance into one cited report that names which existing state vocabulary
each claim came from and mints no fourth".

The reason the last clause is in the goal at all is that three coverage-state
vocabularies already exist in this codebase and they overlap in spirit without
being identical: `auditor.coverage_report`'s five shipped states (`covered`,
`gap`, `partial`, `conflicting`, `unknown`),
`schemas/audit_report.schema.json`'s six-state `coverage_row.state` enum (the
same five plus `stale`), and `graph.BINDING_STATES`'s five states (`covered`,
`thin`, `missing`, `conflicting`, `unknown`). A report that carries a bare
`covered` is ambiguous between the first and the third, and the tempting fix,
a fourth unified vocabulary, is the failure `15B-RESEARCH.md` Pitfall 2 names
by name.

This plan's answer is provenance rather than unification: every row names its
vocabulary, and `blueprint.py` holds no vocabulary of its own to be tempted
into.

Decisions already made, cited, and never re-derived here:

- **D-15B-1** in `15B-DECISIONS.md`: where this code lives. This plan is
  written against `option-a`, which puts `course_audit` in `blueprint.py` as a
  pure function over supplied arguments.
- **15B-RESEARCH.md Pitfall 2** in full, including its named warning sign: "A
  course-audit record whose `state` field could plausibly have come from either
  `graph.BINDING_STATES` or `auditor.coverage_report` without the record itself
  saying which."
- **15B-RESEARCH.md Architectural Responsibility Map**, the course-audit row,
  quoted: "an audit is a read-only aggregation over three already-computed
  sources; it must not recompute or duplicate any of the three".
- **schemas/audit_report.schema.json line 86 to 89**, the shipped `stale` field
  and its derivation rule, which this plan's report follows for its own object
  kind.
- **PLANNING-DIRECTIVES section 4** non-negotiable 2 and section 4a's
  clarification, quoted: "It does not freeze the one parser's grammar. Additive
  growth is 4.4's subject and is permitted". A second report schema is not a
  second parser or a second evidence store; it is one more validated document
  shape.

Decisions this plan makes and locks, so the executor never guesses (the
`PLANNING-DIRECTIVES.md` section 5 bar):

| Open question | Locked answer | One-line rationale |
|---|---|---|
| Whether `blueprint.py` holds a copy of any coverage vocabulary | No. `COVERAGE_VOCABULARIES` holds three vocabulary NAMES, and membership is checked against the live tuple on the module that owns it | A copied vocabulary drifts from its original and becomes a fourth by accident, which is exactly the failure this plan exists to prevent. |
| What the audit does when a row's state is not in the vocabulary it names | Refuses with `blueprint.state_not_in_vocabulary` before returning the report | A row whose provenance does not check out is worse than no row, because it looks cited. |
| Whether the audit recomputes any signal | Never. All four arrive as arguments | Two answers to the same question can disagree, and the one the reader sees would be the newer one rather than the recorded one. |
| Whether the report has its own schema file | Yes, `schemas/course_audit_report.schema.json`, subject to the `D-15B-3` checkpoint in Task 1 | `15B-RESEARCH.md` Open Question 1's recommendation, because `audit_report.schema.json`'s `$defs.coverage_row` is bound by `additionalProperties: false` to `auditor.py`'s syllabus-to-bank pairing. |
| How a stale input is reported | Both: a top-level `stale` boolean and a `stale_inputs` list naming every stale input by object id | A boolean alone tells a reader that something is stale and not what, which makes the report unactionable. |
| Whether counts are proportions | No. Every count in the report is an integer count with its denominator beside it; no share, percentage, or ratio appears | A proportion without a denominator is the shape a mastery claim takes, and AGENT-03's ban is the reason this phase never mints one. |

Purpose: make one course's quality state legible in one document without
inventing a claim.
Output: the course-audit report function, its schema, and the recorded
`D-15B-3` decision.
</objective>

<context>
@.planning/phases/15B-quality-blueprint-acceptance/15B-RESEARCH.md
@.planning/phases/15B-quality-blueprint-acceptance/15B-PATTERNS.md
@.planning/phases/15B-quality-blueprint-acceptance/15B-DECISIONS.md
@.planning/PLANNING-DIRECTIVES.md
@.planning/REQUIREMENTS.md
@.planning/ROADMAP.md
@auditor.py
@schemas/audit_report.schema.json
@schema_validate.py
@blueprint.py
</context>

## Artifacts this phase produces (plan 15B-05 share)

Added to `blueprint.py`. Every symbol below is new in this phase.

- Constants: `COVERAGE_VOCABULARIES = ("graph.BINDING_STATES",
  "auditor.coverage_report", "audit_report.coverage_row")`,
  `AUDIT_SCHEMA_VERSION = 1`,
  `AUDIT_SCHEMA_RESOURCE = "schemas/course_audit_report.schema.json"`,
  `AUDIT_ROW_KEYS = ("objective_id", "vocabulary", "state", "source_object_id",
  "locator", "treatment_kind", "quality_finding_codes",
  "blueprint_finding_codes", "stale")`,
  `AUDIT_REPORT_KEYS = ("schema_version", "status", "course_object_id",
  "course_fingerprint", "source_fingerprints", "rows", "counts",
  "stale", "stale_inputs", "vocabularies_cited", "tool_version")`.
- Functions: `audit_row(...)`, `course_audit(...)`.
- `BLUEPRINT_CODES` gains two members: `blueprint.state_not_in_vocabulary` and
  `blueprint.unknown_vocabulary`. The tuple grows from eighteen members to
  twenty and stays sorted.

New schema file: `schemas/course_audit_report.schema.json`,
`x-itembank-version` `1`, unless `D-15B-3` records `option-b` or `option-c`.

Added to `fixtures/corpus_15b.py`: `build_audit_signals(dest)` returning a dict
with the keys `course_object_id`, `treatment_rows`, `coverage_claims`,
`quality_findings`, `blueprint_findings`, `fingerprints`, and
`stale_fingerprints`.

New test function in `tests/blueprint_roundtrip.py`: `check_course_audit()`.

Added to `.planning/phases/15B-quality-blueprint-acceptance/15B-DECISIONS.md`:
the dated section `## D-15B-3. Where the course audit report shape lives`.

No CLI command, no daemon route, and no journal record type is produced by this
plan. `blueprint.py`'s import list is unchanged.

<tasks>

<task type="checkpoint:decision" gate="blocking">
  <name>Task 1: where the course audit report shape lives</name>
  <files>.planning/phases/15B-quality-blueprint-acceptance/15B-DECISIONS.md</files>
  <read_first>
- `15B-RESEARCH.md` Open Question 1 in full, including its "What we know",
  "What's unclear", and "Recommendation" paragraphs. That question is the
  reason this is a checkpoint rather than a silent adoption.
- `schemas/audit_report.schema.json` in full: its top-level `required` array,
  its `status` enum with the existing seven values, its `stale` field at lines
  86 to 89, and `$defs.coverage_row` with its `additionalProperties: false` and
  its four required keys `objective_key`, `state`, `source_citations`, and
  `bank_item_ids`.
- `auditor.py` lines 370 to 421, `coverage_report`'s return dict, so the
  existing `status: "coverage"` branch is understood as what it is: a
  syllabus-objective-to-bank-item pairing.
- `schemas/quality_finding.schema.json` in full, the closed four-member
  `detector` enum and the `x-itembank-version` convention any new schema
  copies.
- `schema_validate.py` lines 27 to 38, the `SUPPORTED` and `ANNOTATIONS`
  keyword ceiling any new schema must stay inside.
- `tests/audit_coverage_roundtrip.py` and `tests/audit_roundtrip.py`, the
  shipped Phase 11 fixtures that a loosened `additionalProperties` would
  affect.
- `.planning/phases/15B-quality-blueprint-acceptance/15B-DECISIONS.md`, so the
  new section is appended below `## D-15B-2`.
  </read_first>
  <decision>
Does the course audit report get its own schema file, extend the shipped
`audit_report.schema.json` with an eighth `status` value, or carry no schema at
all?
  </decision>
  <context>
`schemas/audit_report.schema.json` is a shipped, multi-purpose contract whose
`status` enum already carries seven values including `"coverage"` for Phase
11's syllabus-coverage audits, and whose structure branches on `status` into
proposal, manifest, and coverage shapes. On its face a course audit is one more
branch.

The obstacle is `$defs.coverage_row`. It is `additionalProperties: false` and
its four required keys (`objective_key`, `state`, `source_citations`,
`bank_item_ids`) encode `auditor.py`'s syllabus-objective-to-bank-item pairing
specifically. A course-scope audit row pairs an objective with a source, a
treatment, a blueprint, and a named vocabulary, which is a structurally
different pairing. Pushing it through the same `$defs` would either violate
`additionalProperties: false` or require loosening it, and that loosening lands
on shipped Phase 11 fixtures that currently prove strictness.

This is rated one-way. A schema is a published contract; `$id` values and
`x-itembank-version` numbers are read by later phases and by any agent client.
Changing the report's home after a course audit has been produced and stored
means migrating stored documents, not editing a line.
  </context>
  <options>
    <option id="option-a">
      <name>RECOMMENDED DEFAULT: a new schemas/course_audit_report.schema.json</name>
      <pros>The new pairing gets its own strict shape with its own
      `additionalProperties: false`, and shipped Phase 11 strictness is
      untouched, so `tests/audit_coverage_roundtrip.py` and
      `tests/audit_roundtrip.py` need no change at all. The two report families
      version independently: a Phase 16 change to the course audit does not bump
      `audit_report.schema.json`'s `x-itembank-version` and does not invalidate
      a stored Phase 11 report. The new file copies
      `quality_finding.schema.json`'s envelope conventions exactly, so it is one
      more file of an established shape rather than a new
      convention.</pros>
      <cons>Two report schemas now exist, so a reader asking "what does an
      itembank audit report look like" must know which audit. The `stale` field
      is defined twice, in two files, with the same meaning, and the two could
      drift in description even though neither can drift in behavior.</cons>
    </option>
    <option id="option-b">
      <name>An eighth status value in the shipped audit_report.schema.json</name>
      <pros>One report contract for every audit this tool produces. A consumer
      that already validates an audit report validates this one too, with no new
      `$id` to learn.</pros>
      <cons>It needs a `$defs.course_audit_row` added beside `coverage_row`
      anyway, because the two pairings are structurally different, so the
      claimed unification is one file rather than one shape. It also bumps a
      shipped schema's `x-itembank-version`, which every stored Phase 11 report
      and every Phase 11 fixture is validated against, for a reason unrelated to
      Phase 11.</cons>
    </option>
    <option id="option-c">
      <name>No schema; the report is a documented plain dict</name>
      <pros>Nothing new to version, nothing to migrate, and the shape can
      change freely until Phase 16 knows what it needs.</pros>
      <cons>Every other structured output this project produces is
      schema-validated, and `schema_validate.check_schema` coupling tests are
      the mechanism that catches a drift between a schema and the code that
      builds against it. An unvalidated report is the one place a fourth
      vocabulary could enter without a test noticing, which is the exact risk
      this plan exists to close.</cons>
    </option>
  </options>
  <action>
Ask Weibao the question above, present all three options with the recommended
default named, and record the answer verbatim in
`.planning/phases/15B-quality-blueprint-acceptance/15B-DECISIONS.md` under a
dated heading `## D-15B-3. Where the course audit report shape lives`.

What the executor does with each answer:

- **option-a**: proceed as Task 2 is already written. No plan edit is needed.
- **option-b**: before Task 2, record in `15B-DECISIONS.md` that
  `schemas/course_audit_report.schema.json` leaves this plan's `files_modified`
  list and `schemas/audit_report.schema.json` enters it; that the `status` enum
  gains the eighth member `"course_audit"`; that `$defs` gains
  `course_audit_row` with the same shape Task 2 describes; that
  `x-itembank-version` bumps to `2` and every stored Phase 11 fixture is
  re-validated; and that `python tests/audit_roundtrip.py`,
  `python tests/audit_coverage_roundtrip.py`, and
  `python tests/audit_authoring_roundtrip.py` join Task 2's verify command.
  Then build it that way.
- **option-c**: before Task 2, record in `15B-DECISIONS.md` that no schema file
  is created; that `blueprint.AUDIT_SCHEMA_RESOURCE` is not defined; that
  `course_audit` validates its own output against `AUDIT_REPORT_KEYS` and
  `AUDIT_ROW_KEYS` by key-set comparison instead of by schema validation; and
  that plan 15B-07's freeze record names the unvalidated report as an open item
  with the phase that owns closing it. Then build it that way.

Do not proceed with a silent default. An unanswered checkpoint stops the wave.
  </action>
  <verify>
`15B-DECISIONS.md` carries a dated `## D-15B-3` heading with the chosen option
id and Weibao's answer recorded verbatim.
  </verify>
  <acceptance_criteria>
- `.planning/phases/15B-quality-blueprint-acceptance/15B-DECISIONS.md` contains
  the literal heading `## D-15B-3. Where the course audit report shape lives`.
- The recorded answer names exactly one of `option-a`, `option-b`, `option-c`.
- When the answer is `option-b` or `option-c`, the file also carries the
  consequence list this task's action names for that option.
- The file contains no em dash character.
  </acceptance_criteria>
  <reversibility rating="one-way">A schema is a published contract with an
  `$id` and a version that later phases and agent clients read. Changing the
  report's home after a course audit has been produced and stored migrates
  stored documents rather than editing a line.</reversibility>
  <resume-signal>Reply with `option-a`, `option-b`, or `option-c`.</resume-signal>
</task>

<task type="auto" tdd="true">
  <name>Task 2: the cited course audit that mints no fourth vocabulary</name>
  <files>blueprint.py, schemas/course_audit_report.schema.json, fixtures/corpus_15b.py, tests/blueprint_roundtrip.py</files>
  <read_first>
- `.planning/phases/15B-quality-blueprint-acceptance/15B-DECISIONS.md`,
  `D-15B-3` as recorded by Task 1. If it is `option-b` or `option-c`, apply the
  recorded consequence list before step 1.
- `blueprint.py` in full as it stands after plan 15B-04: `BLUEPRINT_CODES`'s
  set-then-sorted construction, `canonical_json`, `blueprint_finding`,
  `classify_staleness`, `staleness_report`, and the module docstring's
  structural-ban paragraph.
- `auditor.py` lines 370 to 421, `coverage_report`'s exact return dict, the
  aggregation shape this function copies: precomputed values in as arguments,
  one structured dict out, nothing read and nothing written.
- `schemas/audit_report.schema.json`, the top-level shape, the `stale` field,
  and `$defs.coverage_row`, so the new schema is a sibling of it rather than a
  rename of it.
- `graph.py` as landed, `BINDING_STATES`, and `auditor.py`'s own five-state
  vocabulary, so the membership check reads each vocabulary from the module
  that owns it rather than from a copy.
- `.planning/phases/15A-director-treatment-policy/15A-02-PLAN.md` and
  `15A-03-PLAN.md` "Artifacts this phase produces", for
  `director.untreated_objectives`, `director.classify_coverage`, and
  `director.COVERAGE_CLAIM_KEYS`, so the supplied signals' shapes are known.
  This task calls neither function; it consumes what they produced.
- `fixtures/corpus_15b.py` as it stands after plan 15B-04.
  </read_first>
  <behavior>
Assertions `check_course_audit()` must make. Write them first and confirm they
fail before extending `blueprint.py`.

The vocabulary discipline, asserted structurally:

- `blueprint.COVERAGE_VOCABULARIES` equals `("graph.BINDING_STATES",
  "auditor.coverage_report", "audit_report.coverage_row")` and has exactly
  three members.
- Every member of `COVERAGE_VOCABULARIES` is a NAME, not a state: none of the
  strings `covered`, `gap`, `partial`, `thin`, `missing`, `conflicting`,
  `unknown`, or `stale` is a member of the tuple.
- `blueprint.py` defines no tuple or frozenset whose members are coverage
  states; asserted by walking every module-level tuple on `blueprint` and
  failing if any contains both `"covered"` and `"conflicting"`.
- `hasattr(blueprint, "graph")`, `hasattr(blueprint, "auditor")`, and
  `hasattr(blueprint, "director")` are all still `False`. The audit takes its
  signals as arguments and imports none of the modules that produce them.

Provenance is required and is checked:

- `blueprint.audit_row(...)` returns a dict whose key set equals
  `set(blueprint.AUDIT_ROW_KEYS)`.
- `audit_row` with a `vocabulary` outside `COVERAGE_VOCABULARIES` raises
  `BlueprintError` with code `blueprint.unknown_vocabulary`, and the message
  names all three permitted vocabularies.
- `course_audit` given a row whose `state` is not a member of the vocabulary it
  names raises `BlueprintError` with code
  `blueprint.state_not_in_vocabulary`, and the message names the state, the
  vocabulary, and that vocabulary's members. Assert this for a row claiming
  `graph.BINDING_STATES` with the state `gap`, which is real in
  `auditor.coverage_report` and is not a `BINDING_STATES` member, so the check
  catches a real cross-vocabulary confusion rather than a typo.
- The membership check reads each vocabulary's members from a caller-supplied
  `vocabulary_members` mapping, so `blueprint.py` holds no copy. `course_audit`
  with a `vocabulary_members` mapping missing one of the three cited
  vocabularies raises `blueprint.unknown_vocabulary` rather than skipping the
  check.
- Two rows citing two different vocabularies and carrying the same state string
  `covered` both survive and remain distinguishable in the report by their
  `vocabulary` field.

The report aggregates four signals and recomputes none:

- `course_audit(course_object_id, treatment_rows, coverage_rows,
  quality_findings, blueprint_findings, vocabulary_members,
  course_fingerprint, source_fingerprints, base_fingerprints,
  tool_version=...)` returns a dict whose key set equals
  `set(blueprint.AUDIT_REPORT_KEYS)` and whose `status` is the literal
  `"course_audit"`.
- Its `rows` list has one row per supplied coverage row, and each row carries
  the `treatment_kind` from the matching treatment row, the codes of every
  quality finding whose item belongs to that objective, and the codes of every
  blueprint finding likewise, all copied and none recomputed.
- Its `counts` object carries integer counts with their denominators beside
  them: `objectives_total`, `objectives_with_treatment`, `rows_total`,
  `rows_stale`, `quality_findings_block`, `quality_findings_warn`,
  `blueprint_findings_block`, and `blueprint_findings_warn`. Every value is an
  `int`.
- `vocabularies_cited` lists, sorted, exactly the vocabulary names that appear
  in `rows`, so a reader sees at a glance which sources the report drew on.
- Nothing in the returned report is a proportion: no key named `share`, `rate`,
  `ratio`, `percent`, or `pct` exists anywhere in it.

Staleness is derived and named:

- `course_audit` sets `stale` to `True` when any supplied fingerprint pair
  classifies stale through `classify_staleness`, and `False` otherwise.
- `stale_inputs` lists every stale input's object id, sorted, and is empty
  exactly when `stale` is `False`.
- Each row's own `stale` field equals `classify_staleness` over that row's own
  base and current fingerprints, so a report can be stale in one row and fresh
  in another.
- The report's `stale` is `True` when any row's is, asserted as an `or` over
  rows rather than as a separate computation.

Determinism, ordering, and edges:

- Two `course_audit` calls over the same inputs return dicts whose
  `canonical_json` renderings are byte identical.
- `rows` is sorted by `(objective_id, vocabulary, source_object_id)`, and
  shuffling any of the four input lists does not change the output.
- Two rows equal on all three sort keys both appear, and their relative order
  is reproducible across two runs.
- `course_audit` over zero objectives and four empty signal lists returns a
  valid report whose `rows` is `[]`, whose every `counts` value is `0`, whose
  `vocabularies_cited` is `[]`, whose `stale` is `False`, and whose
  `course_object_id` and `course_fingerprint` are still present.
- `course_audit` with `None` for any of the four signal lists behaves as if it
  were `[]`.
- A single-row course produces a one-row report with `objectives_total` of `1`
  and no division anywhere.

The schema couples to the code:

- `schema_validate.check_schema(json.load(open("schemas/course_audit_report.schema.json")))`
  raises nothing.
- `schema_validate.validate(report, schema)` passes for every report the test
  builds, including the empty one.
- The schema's top-level `required` array equals `list(AUDIT_REPORT_KEYS)`
  minus nothing; assert the schema's `required` and `AUDIT_REPORT_KEYS` agree
  member for member and in the same order, so a future addition to one that
  misses the other fails here.
- The schema's row `vocabulary` property is an `enum` equal to
  `list(COVERAGE_VOCABULARIES)`, asserted against the live tuple.
- The string `"number"` does not appear as a `type` value anywhere in the file.

No aggregate, asserted structurally:

- `check_no_aggregate(report, "course_audit")` from plan 15B-02 finds no
  `float` anywhere and no key whose lowercase name contains `mastery`,
  `completion`, `readiness`, `progress`, `percent`, or `score`.
  </behavior>
  <action>
1. Add `check_course_audit()` to `tests/blueprint_roundtrip.py` with every
   assertion in `<behavior>`, wire it into `main()`, and run
   `python tests/blueprint_roundtrip.py` to confirm it fails.

2. Add `build_audit_signals(dest)` to `fixtures/corpus_15b.py`, returning the
   seven keys named in this plan's Artifacts section. It builds at least one
   coverage row per cited vocabulary, at least one row that is stale and at
   least one that is fresh, at least one objective with a treatment and one
   without, at least one blocking and one warning quality finding, at least one
   blocking and one warning blueprint finding, and one deliberately
   cross-vocabulary row for the refusal case. It also returns the
   `vocabulary_members` mapping built by reading `graph.BINDING_STATES` and
   `auditor`'s own five states live, so no vocabulary is copied into a fixture
   literal either. All content is fictional and fixed-seed.

3. Create `schemas/course_audit_report.schema.json` copying
   `schemas/quality_finding.schema.json`'s envelope conventions exactly:
   `$schema`, `$id` of
   `https://itembank.local/schemas/course_audit_report.schema.json`, `title` of
   `itembank course audit report`, a `description`, `x-itembank-version` of
   `1`, `type: object`, `additionalProperties: false`, and `required` equal to
   `AUDIT_REPORT_KEYS` in that exact order. Its properties, exactly:
   - `schema_version`: const 1.
   - `status`: string, `const` `"course_audit"`.
   - `course_object_id`: string, `minLength` 1.
   - `course_fingerprint`: string.
   - `source_fingerprints`: array of strings.
   - `rows`: array of `{"$ref": "#/$defs/audit_row"}`.
   - `counts`: object, `additionalProperties: false`, `required` naming all
     eight count keys, each an integer with `minimum` 0.
   - `stale`: boolean, with the description
     `"True when any cited input fingerprint no longer matches the fingerprint
     this report's rows were built against; a stale course audit is never
     treated as current, and stale_inputs names which inputs moved."`
   - `stale_inputs`: array of strings.
   - `vocabularies_cited`: array of strings, each an `enum` member equal to
     `COVERAGE_VOCABULARIES`.
   - `tool_version`: string.
   Add `$defs.audit_row`, `additionalProperties: false`, `required` equal to
   `AUDIT_ROW_KEYS` in that exact order, with `vocabulary` an `enum` of the
   three vocabulary names, `state` a plain string (its permitted values belong
   to the cited vocabulary and are checked in code, not here, which is the
   point), `quality_finding_codes` and `blueprint_finding_codes` arrays of
   strings, and `stale` a boolean. The top-level `description` states in plain
   sentences that this report cites which of three existing vocabularies each
   row's state came from, that it mints no fourth, that its `state` field is
   deliberately unconstrained here because constraining it would require this
   schema to hold a copy of three vocabularies that would then drift, and that
   the membership check lives in `blueprint.course_audit` against the live
   tuples. Use no schema keyword outside `schema_validate.SUPPORTED` and
   `schema_validate.ANNOTATIONS`. No em dash characters.

4. Add to `blueprint.py` the constants `COVERAGE_VOCABULARIES`,
   `AUDIT_SCHEMA_VERSION`, `AUDIT_SCHEMA_RESOURCE`, `AUDIT_ROW_KEYS`, and
   `AUDIT_REPORT_KEYS` exactly as listed in this plan's Artifacts section.
   Above `COVERAGE_VOCABULARIES`, write a comment recording that these are
   vocabulary NAMES and not states; that `blueprint.py` deliberately holds no
   copy of any vocabulary's members, because a copy drifts and becomes a fourth
   vocabulary by accident; that the caller supplies `vocabulary_members` read
   live from the owning modules; and that the ROADMAP 15B goal requires the
   report to name which existing vocabulary each claim came from and to mint no
   fourth.

5. Add the two new `BLUEPRINT_CODES` members, keeping the set-then-sorted
   construction so the tuple grows from eighteen to twenty and stays sorted,
   with these exact message templates:
   - `blueprint.unknown_vocabulary`: `"%s is not one of the three coverage
     vocabularies graph.BINDING_STATES, auditor.coverage_report, or
     audit_report.coverage_row; a course audit cites an existing vocabulary and
     mints no fourth"`
   - `blueprint.state_not_in_vocabulary`: `"state %s is not a member of the
     vocabulary %s this row cites; its members are %s, and a state whose
     provenance does not check out is worse than an uncited one because it
     looks cited"`

6. Implement `audit_row(...)` returning the nine-key dict and refusing an
   unknown vocabulary before building anything. Implement `course_audit(...)`
   as a pure aggregation: treat `None` for any signal list as `[]`; validate
   each row's vocabulary and state against the supplied `vocabulary_members`;
   join treatments, quality findings, and blueprint findings onto rows by
   objective id and item id without recomputing any of them; derive each row's
   `stale` and the report's `stale` and `stale_inputs` through
   `classify_staleness`; build `counts` as integers; build
   `vocabularies_cited` as the sorted set of vocabularies present in `rows`;
   sort `rows` by `(objective_id, vocabulary, source_object_id)`; and validate
   the finished report against `schemas/course_audit_report.schema.json` before
   returning it, raising `BlueprintError` with code `blueprint.invalid` on a
   failure. Write its docstring stating that it recomputes nothing, that it
   calls no classifier, and that every claim it carries was computed elsewhere
   and is reproduced with its provenance attached.

7. Run `python tests/blueprint_roundtrip.py`, `python schema_validate.py`,
   `for t in tests/*.py; do python "$t" || exit 1; done`, and
   `python itembank.py guard .`, and confirm all four succeed.
  </action>
  <verify>
  <automated>python tests/blueprint_roundtrip.py && python schema_validate.py && python tests/audit_coverage_roundtrip.py && python itembank.py guard .</automated>
Expected: `tests/blueprint_roundtrip.py` exits 0 with `check_course_audit` run,
`schema_validate.py` reports no error, the shipped Phase 11 coverage suite
exits 0 unchanged, and `guard` prints `0 offending files`. The degraded
behavior this task must prove rather than paper over is the cross-vocabulary
refusal: a row citing `graph.BINDING_STATES` while carrying the state `gap`,
which is a real `auditor.coverage_report` state and not a `BINDING_STATES`
member, raises `blueprint.state_not_in_vocabulary` and no report is returned.
Confirm the code and that the function returned nothing.
  </verify>
  <acceptance_criteria>
- `python tests/blueprint_roundtrip.py` exits 0 with `check_course_audit` run.
- `python -c "import blueprint; print(blueprint.COVERAGE_VOCABULARIES)"` prints
  `('graph.BINDING_STATES', 'auditor.coverage_report', 'audit_report.coverage_row')`.
- `python -c "import blueprint; v=set(blueprint.COVERAGE_VOCABULARIES); print(v & {'covered','gap','partial','thin','missing','conflicting','unknown','stale'})"`
  prints `set()`.
- `python -c "import blueprint; print(len(blueprint.BLUEPRINT_CODES), blueprint.BLUEPRINT_CODES == tuple(sorted(blueprint.BLUEPRINT_CODES)))"`
  prints `20 True`.
- `python -c "import blueprint; print(hasattr(blueprint,'graph'), hasattr(blueprint,'auditor'), hasattr(blueprint,'director'), hasattr(blueprint,'evidence'))"`
  prints `False False False False`.
- `python -c "import json,schema_validate; schema_validate.check_schema(json.load(open('schemas/course_audit_report.schema.json'))); print('schema ok')"`
  prints `schema ok`.
- `python -c "import json,blueprint; s=json.load(open('schemas/course_audit_report.schema.json')); print(s['required'] == list(blueprint.AUDIT_REPORT_KEYS), s['\$defs']['audit_row']['required'] == list(blueprint.AUDIT_ROW_KEYS), s['\$defs']['audit_row']['properties']['vocabulary']['enum'] == list(blueprint.COVERAGE_VOCABULARIES))"`
  prints `True True True`.
- `python tests/audit_coverage_roundtrip.py`, `python tests/audit_roundtrip.py`,
  and `python tests/audit_authoring_roundtrip.py` each exit 0, unchanged by
  this plan.
- `check_no_aggregate` over a built report finds no `float` and no key
  containing `mastery`, `completion`, `readiness`, `progress`, `percent`, or
  `score`.
- `for t in tests/*.py; do python "$t" || exit 1; done` exits 0.
- `python itembank.py guard .` prints `0 offending files`.
- None of `blueprint.py`, `schemas/course_audit_report.schema.json`,
  `fixtures/corpus_15b.py`, or `tests/blueprint_roundtrip.py` contains an em
  dash character.
  </acceptance_criteria>
  <precondition>Task 1 recorded an answer under `## D-15B-3` in `15B-DECISIONS.md`, and plan 15B-04 is green.</precondition>
  <reversibility rating="costly">`AUDIT_ROW_KEYS` and `AUDIT_REPORT_KEYS` are
  consumed by plan 15B-07's tracer and by the schema they must agree with.
  Changing them before the 15B freeze costs one edit in each plus one fixture
  regeneration. The genuinely one-way part, the report's schema home, is gated
  by Task 1.</reversibility>
  <done>One course's treatment state, coverage state, quality findings, and
  blueprint compliance appear in one schema-validated report in which every row
  names the vocabulary its state came from, no fourth vocabulary exists, and no
  number in the document is a proportion.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| four supplied signals to one report | The audit reproduces claims it did not compute; a signal it silently recomputes would produce a second answer the reader cannot see disagreeing with the recorded one. |
| three existing vocabularies to one row | A state string crossing a vocabulary boundary without its provenance is a claim that looks cited and is not. |
| report to reader | The report is what a course builder acts on; a number in it that looks like a proportion would be read as one. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-15B-05-01 | Tampering | a fourth coverage-state vocabulary minted by accident | high | mitigate | `COVERAGE_VOCABULARIES` holds names rather than states, a test asserts no coverage state is a member of it, another asserts no module-level tuple on `blueprint` contains both `covered` and `conflicting`, and membership is checked against a caller-supplied mapping read live from the owning modules. |
| T-15B-05-02 | Spoofing | a state presented as cited while carrying the wrong provenance | high | mitigate | `course_audit` refuses with `blueprint.state_not_in_vocabulary` before returning, and the asserted case is the real cross-vocabulary confusion (`gap` claimed as a `graph.BINDING_STATES` state) rather than a typo. |
| T-15B-05-03 | Tampering | the audit recomputing a signal and disagreeing with the record | high | mitigate | All four signals arrive as arguments; `hasattr(blueprint, "graph")`, `"auditor"`, and `"director"` are all asserted `False`, so the modules that produce them are unreachable from this one. |
| T-15B-05-04 | Spoofing | a count read as a mastery or completion claim | high | mitigate | Every `counts` value is an integer with its denominator beside it, no key named `share`, `rate`, `ratio`, `percent`, or `pct` exists, and `check_no_aggregate` walks the whole report for floats and for the six banned key substrings. |
| T-15B-05-05 | Tampering | a stale report read as current | high | mitigate | `stale` is derived at build time through `classify_staleness` and is never stored on an input, and `stale_inputs` names every stale input so the flag is actionable rather than decorative. |
| T-15B-05-06 | Tampering | a shipped Phase 11 schema loosened for this phase's convenience | high | mitigate | `option-a` creates a sibling schema and touches `audit_report.schema.json` not at all; the three shipped audit suites are in this task's acceptance criteria to prove it, and `option-b`'s consequence list makes the cost of the alternative explicit rather than silent. |
| T-15B-05-07 | Tampering | the schema and the code drifting apart | high | mitigate | The test asserts the schema's `required` arrays equal `AUDIT_REPORT_KEYS` and `AUDIT_ROW_KEYS` member for member and in order, and that the row `vocabulary` enum equals the live `COVERAGE_VOCABULARIES`, so an addition to one that misses the other fails here. |
| T-15B-05-08 | Information Disclosure | real course content entering through the audit fixture | high | mitigate | `build_audit_signals` builds fictional fixed-seed content and reads vocabularies live rather than copying them into literals, and `python itembank.py guard .` is in this task's acceptance criteria. |
| T-15B-05-09 | Tampering | supply chain: a reporting or templating dependency added | high | mitigate | None is added; the report is a dict built from supplied lists and validated by the in-repo `schema_validate`. Per `PLANNING-DIRECTIVES.md` section 4a the absence of dependencies is explicitly not the mitigation: any dependency ever added here is vendored at a pinned version with a recorded checksum and a named license review. |
| T-15B-05-10 | Repudiation | a report that does not say which vocabularies it drew on | medium | mitigate | `vocabularies_cited` is a required top-level field listing exactly the vocabularies present in `rows`, sorted, so the report's own provenance is legible without reading every row. |
| T-15B-05-11 | Denial of Service | a large course making the join quadratic | low | accept | The join walks the quality and blueprint findings once per row. Accepted because the input is one repository-local course a human authored, and a slow report is a loud local failure with no data at risk. |
</threat_model>

<out_of_scope>
Refused by this plan, by name, so no adjacent temptation is decided by executor
judgment:

- No fourth coverage-state vocabulary, no renaming of any of the three, and no
  reconciling superset.
- No call to `director.untreated_objectives`, `director.classify_coverage`,
  `auditor.coverage_report`, `authoring.quality_gate`, or
  `blueprint.blueprint_gate` from inside `course_audit`. It consumes their
  output and imports none of them.
- No change to `auditor.py`, to `schemas/audit_report.schema.json`, or to any
  shipped Phase 11 fixture, under `option-a`.
- No evidence reading of any kind. The audit's four signals are treatment,
  coverage, quality, and blueprint; learner evidence is AGENT-03's and is plan
  15B-06's, and `blueprint.py` still imports no `evidence`.
- No proportion, share, rate, ratio, percentage, or aggregate anywhere in the
  report.
- No remediation, next action, or recommendation. The audit reports state; what
  to do about it is AGENT-03's proposal record in plan 15B-06.
- No CLI command, no daemon route, and no rendered HTML view of the report.
- No stored report file. `course_audit` returns a dict; whichever phase ships a
  surface decides where a report is written and through which write path.
</out_of_scope>

<flagged_assumptions>
Surfaced, not silently dropped:

- **The three vocabularies are assumed stable within this phase (assumption,
  recorded).** `COVERAGE_VOCABULARIES` names three vocabularies whose members
  this plan reads live rather than copying, precisely so a change to any of
  them does not silently invalidate a stored report. What is not proven is what
  a stored report means after one of the three vocabularies gains or loses a
  member in a later phase: a row citing a vocabulary whose members have since
  changed would fail its own membership check on re-validation, which is the
  safe direction but is a re-validation failure rather than a migration.
  Whichever phase changes one of the three vocabularies owns that migration.
  Recorded so plan 15B-07's freeze record carries it as an open item.
</flagged_assumptions>

<summary_obligations>
`15B-05-SUMMARY.md` records: the option Weibao chose at Task 1 and every plan
edit it forced; which truth was verified by which command, with the command's
actual stdout; the exact `BLUEPRINT_CODES` tuple after this plan's two
additions; the byte-identical determinism check result, quoted; the three
shipped Phase 11 audit suites' exit codes, proving `option-a` touched none of
them; the measured wall-clock time of one full `tests/blueprint_roundtrip.py`
run; and any deviation from this plan with its reason.
</summary_obligations>

<output>
Create
`.planning/phases/15B-quality-blueprint-acceptance/15B-05-SUMMARY.md`
when done.
</output>
