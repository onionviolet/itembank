---
phase: 15B-quality-blueprint-acceptance
plan: 02
type: execute
wave: 2
depends_on: ["15B-01"]
files_modified:
  - blueprint.py
  - schemas/blueprint.schema.json
  - schemas/audit_report.schema.json
  - schemas/course_graph.schema.json
  - graph.py
  - course.py
  - authoring.py
  - fixtures/corpus_15b.py
  - tests/blueprint_roundtrip.py
  - .planning/phases/14B-graph-course-package-prototype/14B-FREEZE.md
autonomous: true
requirements: [ACTIVITY-02]
estimate:
  tokens: 84000
  raw_tokens: 84000
  tasks: 2
  confidence: low
assumption_delta_decision:
  kind: pluralization
  term: second
  snippet: "blueprint-fidelity classifier, never a second parser or scorer; a course audit"
  primary_noun: "the one parser, model.parse_bank, and the one scorer, runtime.score_response"
  decision: no-change
  rationale: "The detected snippet is the ROADMAP 15B goal asserting that NO second parser or scorer is created. This plan honors that literally: the blueprint-fidelity classifier is a pure comparison over questions that model.parse_bank already parsed, gate 5 calls runtime.score_response rather than reimplementing it, and blueprint.py imports model and runtime precisely so it cannot own a parse or a verdict of its own. Singular stays singular and PLANNING-DIRECTIVES section 4 non-negotiable 2 is untouched, so no noun is promoted and nothing is added alongside."
must_haves:
  truths:
    - "One synthetic drafted question set paired with one synthetic cited blueprint travels the whole ACTIVITY-02 path end to end in one commit: it is parsed by model.parse_bank, linted by model.lint, reviewed by authoring.quality_gate, checked against the accepted blueprint by the new blueprint_gate, smoke-tested through runtime.score_response, and only then written by audit_writer.write_units through authoring.run_authoring, with the blueprint document itself durable in the course sidecar through course.write_course."
    - "The exam-fidelity claim is False until every one of the five GATE_STEPS members has reported passed; blueprint.fidelity_claim over a partial gate-result list returns False rather than raising or returning a truthy partial, and no surface reads a claim value this function did not produce."
    - "With no blueprint bound to the course, blueprint_gate returns exactly one finding whose code is blueprint.absent at severity warn, blueprint_gate_blocks returns False, and blueprint.fidelity_claim returns False, so the course presents practice without an exam-fidelity claim rather than refusing to present practice at all."
    - "A drafted set whose observed domain-weight share differs from the blueprint's declared share by exactly the declared tolerance passes the blueprint gate; equality passes, matching the shipped equality-passes precedent in authoring.SKEW_BLOCK_ABOVE where skew blocks only above 0.40."
    - "blueprint_gate over an empty question list returns an empty findings list and blocks nothing, and blueprint_gate over a single-question list applies every share check against a denominator of one rather than dividing by zero or short-circuiting."
    - "blueprint_gate returns its findings sorted by (item, code, canonical_json(evidence)), the same three-part deterministic key authoring.quality_gate already sorts by, so two runs over the same input produce byte-identical findings lists and equal-comparing findings have a specified stable order."
    - "The blueprint gate produces per-field findings and never an aggregate compliance value: no function in blueprint.py returns a float, a percentage, or a single number standing for overall blueprint compliance, following authoring.py's own stated rule that the second quality gate is never an aggregate score."
    - "schemas/audit_report.schema.json's gates object grows by exactly one optional property, blueprint_findings, and its required array is unchanged at lint_errors, lint_warnings, and quality_findings; a proposal built before this plan validates byte-for-byte as it did before, proven by re-running tests/audit_authoring_roundtrip.py and tests/audit_roundtrip.py green."
    - "A course sidecar with no Blueprint section parses and serializes byte-identically after this plan, proven by a stored golden fixture compared byte for byte, not by promise."
  prohibitions:
    - statement: "An exam-fidelity claim must not surface for a drafted set before all five of parser, lint, review, blueprint, and runtime have reported passed, and must not surface at all when no blueprint is bound."
      status: kept
      verification: flagged-unverified
    - statement: "Blueprint compliance must not be collapsed into one opaque percentage, score, grade, or pass rate that hides which of the eight declared fields actually failed."
      status: kept
      verification: flagged-unverified
    - statement: "The blueprint gate must not re-derive a failure mode that model.lint or authoring.quality_gate already owns, in particular duplicate stems, answer-position skew, answer leak, and distractor rationale; a third pass over the same failure mode at a third rigor level lets two detectors silently disagree."
      status: kept
      verification: flagged-unverified
  artifacts:
    - "blueprint.py at the repository root, a pure classifier module importing only model and runtime from this repository, in its thinnest production-quality form"
    - "schemas/blueprint.schema.json, x-itembank-version 1, requiring ACTIVITY-02's eight fields verbatim plus schema_version, blueprint_id, version, and citations"
    - "schemas/audit_report.schema.json with one new optional gates property, blueprint_findings, and one new $defs member, blueprint_finding_ref"
    - "graph.py with SECTION_ORDER gaining the member Blueprint, plus add_blueprint and blueprints"
    - "course.py with bind_blueprint"
    - "authoring.py with blueprint_gate wired into run_authoring's retry loop and its preflight recheck, and build_proposal carrying blueprint_findings"
    - "fixtures/corpus_15b.py with build_blueprint_fixture, build_draft_set, build_golden_sidecar, and teardown"
    - "tests/blueprint_roundtrip.py with check_thin_slice() as its first function"
    - "14B-FREEZE.md with a dated amendment section recording the SECTION_ORDER addition"
  key_links:
    - "blueprint.py imports model and runtime and nothing else from this repository. That is what makes gate 5 a call to the one scorer rather than a second one, and it is what lets authoring.py import blueprint without transitively pulling surfaces.settings into the shipped Phase 11 loop. If blueprint.py ever imports director, course, or journal, the structural assertion that it cannot write and cannot authorize is gone and the import weight lands on authoring.py."
    - "The five gate steps are checked in the fixed GATE_STEPS order and gate 4 runs after gate 3, because authoring.quality_gate's findings are an input a blueprint finding may cite. Running blueprint before quality would make the blueprint gate the first thing a bad draft hits, so its findings would describe a set that lint and quality were going to reject anyway, which is noise rather than signal."
    - "blueprint.fidelity_claim reads a list of gate results and never reads the questions, the blueprint, or the proposal directly. If it re-derived any gate's verdict itself, there would be two answers to whether a gate passed and the claim could disagree with the report that recorded it."
    - "The item facts the bank format does not carry (demand, timing_seconds, tools, construct, feedback_conditions) are supplied by the caller and are never guessed. A field with no supplied fact produces a blueprint.unverifiable warn finding, never a silent pass, because a silent pass would let an exam-fidelity claim rest on five checked fields while claiming eight."
---

<objective>
Land the thinnest real path through this whole phase, end to end, before any
layer is widened: one synthetic drafted practice set and one synthetic cited
blueprint, walked from draft through all five ACTIVITY-02 gates to an accepted
bank write and a durable blueprint document, with the exam-fidelity claim
appearing only after the fifth gate. `blueprint.py` is created here in its
thinnest production-quality form, not as a prototype: the code written in this
plan stays and is expanded by plans 03 through 06.

ACTIVITY-02 names five gates in its own prose: "practice-generated questions
stay drafts until parser, lint, review, blueprint, and runtime gates pass".
Three of the five are shipped and are reused unmodified (`model.parse_bank`,
`model.lint`, `authoring.quality_gate`). One is the shipped scorer called as a
conformance smoke test and not extended (`runtime.score_response`). Exactly one
is new: the blueprint-fidelity classifier this plan builds.

Decisions already made, cited, and never re-derived here:

- **D-15B-1** in `15B-DECISIONS.md`, recorded by plan 15B-01 Task 2: where the
  blueprint, staleness, audit, and acceptance code lives. This plan is written
  against `option-a`. If the recorded answer is `option-b` or `option-c`, read
  the consequence list that decision recorded before Task 1.
- **D-15B-2** in `15B-DECISIONS.md`, recorded by plan 15B-01 Task 3: where a
  blueprint lives and which write path records an acceptance. This plan is
  written against `option-a`, the additive `## Blueprint` section in the 14B
  course sidecar written through `course.write_course`.
- **PLANNING-DIRECTIVES section 4** non-negotiable 2, quoted: "Exactly **one
  parser, one scorer, one evidence store**", and non-negotiable 4, quoted:
  "Format changes are **additive**. A bank not using a new block parses
  unchanged, proven by a byte-identical fixture, not promised."
- **PLANNING-DIRECTIVES section 4a**, quoted: "§4.2 forbids a **second**
  parser, scorer, or evidence store. It does not freeze the one parser's
  grammar." Adding a `## Blueprint` section to the course sidecar is additive
  growth of one format, not a second document model.
- **15B-RESEARCH.md Pitfall 1**: some of AUDIT-07's named failure modes are
  already `model.LINT_CODES` members and the four `quality_finding` detectors
  are a separate, more heavily evidenced pass. The blueprint gate covers
  neither; it covers construct, domain weight, demand, format, difficulty,
  timing, tools, and feedback conditions and nothing else.
- **15B-RESEARCH.md Assumption A2**: `blueprint_gate` is a sibling function to
  `authoring.quality_gate`, not a fifth member of
  `quality_finding.schema.json`'s closed four-member `detector` enum.
- **15B-RESEARCH.md Pattern 2**: a new gate's findings follow
  `quality_finding.schema.json`'s existing record shape and slot into
  `audit_report.schema.json`'s existing `proposal.gates` object as one more
  named array, rather than inventing a second report envelope.

Decisions this plan makes and locks, so the executor never guesses (the
`PLANNING-DIRECTIVES.md` section 5 bar):

| Open question | Locked answer | One-line rationale |
|---|---|---|
| Which ACTIVITY-02 fields the gate can check from a parsed bank alone | Exactly three: `format` from `q["type"]` and the question count, `difficulty` from `q["difficulty"]`, and `domain_weight` from `q["objective"]` | These three are the only blueprint dimensions the shipped `model.parse_bank` question dict already carries. Deriving the other five would require inventing five new bank fields, which non-negotiable 4 would then require a byte-identical-fixture proof for, in a phase whose scope is acceptance rather than format growth. |
| How the other five fields are checked | The caller supplies them: `blueprint_gate(questions, blueprint_doc, item_facts=None)`, where `item_facts` carries `construct` and `feedback_conditions` at the set level and `demand`, `timing_seconds`, and `tools` per item id | An honest supplied fact is checkable; a guessed one is not. A field with no supplied fact produces one `blueprint.unverifiable` finding at severity `warn`, never a silent pass. |
| Whether the gate blocks on an unverifiable field | No. `blueprint.unverifiable` and `blueprint.absent` are `warn`; every other blueprint code is `block` | ACTIVITY-02's Degraded clause reads "absent a blueprint, the course presents practice without an exam-fidelity claim". A missing fact withholds the claim; it does not withhold the practice. |
| Numeric representation in the blueprint | Integer percentage points, `0` through `100`, for every share and tolerance; no float appears anywhere in `schemas/blueprint.schema.json` or in a blueprint finding's evidence | Floats reintroduce the comparison ambiguity the equality-passes rule exists to settle, and `schema_validate.py`'s supported keyword set has no float-safe comparison. Integers make the tolerance boundary exact. |
| The tolerance boundary rule | Inclusive. An observed share differing from the declared share by exactly the declared tolerance passes | Matches the shipped precedent: `authoring.SKEW_BLOCK_ABOVE` blocks only above `0.40`, and `authoring.py`'s own comment records that equality passes to match the live lint precedent. |
| Whether `blueprint_gate` reads the course sidecar | No. It takes an already-validated blueprint dict as an argument, exactly as `auditor.coverage_report` takes an already-normalized document | Keeps `blueprint.py` pure and keeps the two write paths the only code that touches disk. |

Purpose: prove the five-gate architecture end to end on one path before four
more capabilities are built on it.
Output: `blueprint.py`, the blueprint schema, the additive report and sidecar
schema changes, the gate wiring in `authoring.py`, the first fixture builder,
and the first roundtrip test.
</objective>

<context>
@.planning/phases/15B-quality-blueprint-acceptance/15B-RESEARCH.md
@.planning/phases/15B-quality-blueprint-acceptance/15B-PATTERNS.md
@.planning/phases/15B-quality-blueprint-acceptance/15B-DECISIONS.md
@.planning/phases/15B-quality-blueprint-acceptance/15B-PRECONDITION.md
@.planning/PLANNING-DIRECTIVES.md
@.planning/PLAN-TEMPLATE.md
@.planning/REQUIREMENTS.md
@authoring.py
@auditor.py
@schemas/quality_finding.schema.json
@schemas/audit_report.schema.json
@schema_validate.py
</context>

## Artifacts this phase produces (plan 15B-02 share)

New modules and the public symbols this plan creates. Every symbol below is new
in this phase and exists in no shipped file.

- `blueprint.py`
  - Constants: `BLUEPRINT_SCHEMA_VERSION = 1`,
    `BLUEPRINT_SCHEMA_RESOURCE = "schemas/blueprint.schema.json"`,
    `BLUEPRINT_FIELDS` (ACTIVITY-02's eight tokens in the requirement's own
    order, defined in Task 1), `BLUEPRINT_DETECTOR = "blueprint_fidelity"`,
    `BLUEPRINT_DETECTOR_VERSION = 1`,
    `GATE_STEPS = ("parser", "lint", "review", "blueprint", "runtime")`,
    `GATE_RESULT_KEYS = ("step", "passed", "findings")`,
    `SET_FACT_KEYS = ("construct", "feedback_conditions")`,
    `ITEM_FACT_KEYS = ("demand", "timing_seconds", "tools")`,
    `BLUEPRINT_CODES` (a set-then-sorted tuple, the `ADAPTER_CODES`
    construction precedent, with the thirteen members listed in Task 1),
    `WARN_CODES = ("blueprint.absent", "blueprint.unverifiable")`.
  - Exception: `BlueprintError(Exception)` with `.code` and `.message`.
  - Functions created here: `canonical_json(obj)`, `validate_blueprint(doc)`,
    `blueprint_finding(code, severity, item, evidence, remediation)`,
    `blueprint_gate(questions, blueprint_doc, item_facts=None)`,
    `blueprint_gate_blocks(questions, blueprint_doc, item_facts=None)`,
    `runtime_conformance(questions)`, `gate_result(step, passed, findings)`,
    `fidelity_claim(gate_results)`.
- `schemas/blueprint.schema.json`, `x-itembank-version` `1`.
- `fixtures/corpus_15b.py`
  - `build_blueprint_fixture(dest)`, `build_draft_set(dest, variant)`,
    `build_golden_sidecar(dest)`, `teardown(dest)`.
- `tests/blueprint_roundtrip.py`, a direct-execution script, exit 0 on pass,
  whose first function is `check_thin_slice()`, plus `check_blueprint_fields()`
  and `check_gate_edges()`.

Modified shipped and planned files, and the exact symbols added:

- `schemas/audit_report.schema.json`: `$defs.proposal.properties.gates.properties`
  gains `blueprint_findings`; `$defs` gains `blueprint_finding_ref`. The
  `gates.required` array is unchanged. No other change.
- `graph.py`: `SECTION_ORDER` gains the member `"Blueprint"`; two new
  functions, `add_blueprint(doc, blueprint)` and `blueprints(doc)`; one new
  `GraphError` code, `graph.blueprint_invalid`.
- `course.py`: one new function,
  `bind_blueprint(course_root, blueprint, actor_kind, actor_name, expected_fingerprint)`.
- `schemas/course_graph.schema.json`: one new optional section shape for the
  blueprint rows. No existing `required` array changes.
- `authoring.py`: one new import, `blueprint`; `run_authoring` reads
  `config["blueprint"]` and `config["item_facts"]`; the retry loop and the
  preflight recheck each gain one `blueprint_gate` call; `build_proposal`
  gains a `blueprint_findings` parameter appended last with a default of
  `None`, and writes `gates.blueprint_findings`.
- `.planning/phases/14B-graph-course-package-prototype/14B-FREEZE.md`: one
  dated amendment section.

New refusal codes introduced by this plan: the thirteen `BLUEPRINT_CODES`
members and `graph.blueprint_invalid`.

New journal record types introduced by this plan: none. `journal.py` is not
modified by this plan.

No CLI command and no daemon route is produced by this plan.

<tasks>

<task type="tracer" tdd="true">
  <name>Task 1: one drafted set from blueprint to accepted write, end to end, one path only</name>
  <files>blueprint.py, schemas/blueprint.schema.json, schemas/audit_report.schema.json, schemas/course_graph.schema.json, graph.py, course.py, authoring.py, fixtures/corpus_15b.py, tests/blueprint_roundtrip.py, .planning/phases/14B-graph-course-package-prototype/14B-FREEZE.md</files>
  <read_first>
- `.planning/phases/15B-quality-blueprint-acceptance/15B-DECISIONS.md` in full,
  both recorded decisions. If `D-15B-1` is not `option-a` or `D-15B-2` is not
  `option-a`, read that decision's recorded consequence list and apply it
  before step 1.
- `.planning/phases/15B-quality-blueprint-acceptance/15B-PRECONDITION.md`, the
  Deviations found section. A non-empty section means the landed 14B and 15A
  surfaces differ from this plan's citations and every signature below must be
  re-read against the three freeze records first.
- `authoring.py` in full: the module docstring lines 1 to 32, `DETECTOR_VERSIONS`
  lines 65 to 70, `SKEW_MIN_ITEMS` through `LEAK_MIN_RUN` lines 93 to 97,
  `canonical_json` line 169, `quality_gate` and `quality_gate_blocks` lines 539
  to 559, `_quality_findings_payload` line 576, `build_proposal` lines 607 to
  645, and `run_authoring` lines 659 to 798. The retry loop's
  `quality_findings` block at lines 751 to 754 and the preflight recheck at
  lines 772 to 791 are the two exact insertion points.
- `auditor.py` lines 370 to 421, `coverage_report`, the pure-transform shape
  `blueprint.py` copies: precomputed values in as arguments, one structured
  dict out, nothing read and nothing written.
- `schemas/quality_finding.schema.json` in full, the record shape a blueprint
  finding must match field for field.
- `schemas/audit_report.schema.json`, the `$defs.proposal` object and its
  `gates` property, and the `$defs.quality_finding_ref` object that
  `blueprint_finding_ref` is modeled on.
- `schema_validate.py` lines 27 to 38, the `SUPPORTED` and `ANNOTATIONS`
  keyword ceiling. The new schema uses only keywords already present in
  `schemas/quality_finding.schema.json`.
- `model.py`: `parse_bank` at line 60 and `lint` at line 2864, for the exact
  question dict keys (`id`, `item_id`, `type`, `stem`, `difficulty`,
  `objective`, `opts`, `correct`) and the `(errors, warnings)` return shape.
- `runtime.py` lines 260 to 320, `canonical_response`, `canonical_key`, and
  `score_response`, for the exact conformance call gate 5 makes.
- `graph.py` as landed: `SECTION_ORDER`, `parse_course`, `serialize_course`,
  `add_binding`, and `GraphError`.
- `course.py` as landed: `read_course`, `write_course`, `bind_treatment`, and
  `CourseError`.
- `fixtures/corpus_14b.py` as landed: `build_three_domains`, `build_all`, and
  `teardown`, for the fixed-seed, fictional-content-only convention
  `fixtures/corpus_15b.py` follows.
- `tests/audit_authoring_roundtrip.py` and `tests/evidence_roundtrip.py` lines
  1 to 40, for the local `fail(msg)` helper and the `ROOT` plus
  `sys.path.insert` header convention every existing roundtrip test uses. Each
  test file defines its own helper; there is no shared test module.
- `evidence.py` lines 1 to 19, the peer-module docstring contract this project
  restates in every new root module.
  </read_first>
  <behavior>
Assertions `check_thin_slice()` in `tests/blueprint_roundtrip.py` must make,
written before `blueprint.py` exists. Run the test first and confirm it fails.

The new schema is valid and closed:

- `schema_validate.check_schema(json.load(open("schemas/blueprint.schema.json")))`
  raises nothing.
- The document's `required` array equals, in this exact order,
  `["schema_version", "blueprint_id", "version", "construct", "domain_weight",
  "demand", "format", "difficulty", "timing", "tools", "feedback_conditions",
  "citations"]`.
- `additionalProperties` is `false` at the top level and in every nested
  object.
- The string `"number"` does not appear as a `type` value anywhere in the file.

The module surface is exactly what later plans import:

- `blueprint.BLUEPRINT_FIELDS` equals, in this exact order, `("construct",
  "domain_weight", "demand", "format", "difficulty", "timing", "tools",
  "feedback_conditions")`, and has exactly eight members.
- `blueprint.GATE_STEPS` equals `("parser", "lint", "review", "blueprint",
  "runtime")`.
- `blueprint.WARN_CODES` equals `("blueprint.absent", "blueprint.unverifiable")`
  and every member of it is also a member of `blueprint.BLUEPRINT_CODES`.
- `len(blueprint.BLUEPRINT_CODES)` equals `13` and the tuple is sorted.
- `hasattr(blueprint, "evidence")` is `False`.
- `hasattr(blueprint, "journal")` is `False`.
- `hasattr(blueprint, "course")` is `False`.
- `hasattr(blueprint, "director")` is `False`.
- `hasattr(blueprint, "graph")` is `False`.
- `hasattr(blueprint, "audit_writer")` is `False`.
- `blueprint.model` and `blueprint.runtime` are both modules. These two imports
  are the point: gate 5 calls the one scorer rather than owning a verdict.

Validation refuses before it reads:

- `blueprint.validate_blueprint` on the fixture blueprint returns a dict whose
  key set equals the schema's `required` set.
- `blueprint.validate_blueprint` on a blueprint missing its `citations` key
  raises `BlueprintError` with code `blueprint.invalid`, and the message names
  the missing key.
- `blueprint.validate_blueprint` on a blueprint whose `version` is `0` raises
  `BlueprintError` with code `blueprint.invalid`.

The one new gate, in its thin form, checks `format` only:

- `blueprint.blueprint_gate(questions, bp)` where every question's `type` is in
  `bp["format"]["permitted_types"]` and `len(questions)` equals
  `bp["format"]["item_count"]` returns findings containing no member whose
  `code` is `blueprint.format_not_permitted` and none whose `code` is
  `blueprint.item_count_out_of_tolerance`.
- A question whose `type` is not in `permitted_types` produces exactly one
  finding whose `code` is `blueprint.format_not_permitted`, whose `severity` is
  `block`, whose `item` is that question's `id`, and whose `evidence` names
  both the observed type and the permitted list.
- A question count outside `item_count` plus or minus `count_tolerance`
  produces exactly one finding whose `code` is
  `blueprint.item_count_out_of_tolerance`, whose `item` is the literal string
  `BANK`, and whose `severity` is `block`.
- A question count differing from `item_count` by exactly `count_tolerance`
  produces no such finding. Equality passes.
- Every finding's key set equals `{"schema_version", "detector",
  "detector_version", "severity", "code", "item", "evidence", "remediation"}`,
  its `detector` is `"blueprint_fidelity"`, its `detector_version` is `1`, and
  it validates against `schemas/audit_report.schema.json`'s new
  `$defs.blueprint_finding_ref`.
- In this thin form the other seven `BLUEPRINT_FIELDS` members each produce
  exactly one `blueprint.unverifiable` finding at severity `warn` naming the
  field, so nothing passes silently.
- `blueprint.blueprint_gate_blocks(questions, bp)` is `True` when any finding
  has `severity` `block` and `False` otherwise.

Gate 5 is the shipped scorer, called and not extended:

- `blueprint.runtime_conformance(questions)` returns an empty findings list for
  the fixture set, and for each question it calls `runtime.score_response(q,
  answer)` with the answer derived from that question's own
  `runtime.canonical_key(q)` and asserts the verdict is `True`.
- For a question of type `short`, whose `runtime.canonical_key` is `None` and
  whose `score_response` returns `None`, `runtime_conformance` produces no
  finding at all rather than treating not-yet-marked as a failure.
- A deliberately corrupted question whose recorded key does not score `True`
  produces exactly one finding whose `code` is `blueprint.runtime_mismatch` at
  severity `block`.

The claim appears only after all five:

- `blueprint.fidelity_claim([])` is `False`.
- `blueprint.fidelity_claim` over four passing gate results and no `runtime`
  result is `False`.
- `blueprint.fidelity_claim` over all five `GATE_STEPS` with `passed` `True` is
  `True`.
- `blueprint.fidelity_claim` over all five with any one `passed` `False` is
  `False`.
- `blueprint.fidelity_claim` never returns a value other than `True` or
  `False`.

The report envelope grows additively:

- `schemas/audit_report.schema.json`'s
  `$defs.proposal.properties.gates.required` still equals
  `["lint_errors", "lint_warnings", "quality_findings"]`.
- `"blueprint_findings"` is in that same `gates.properties`.
- `schema_validate.check_schema` on the whole edited document raises nothing.
- `python tests/audit_authoring_roundtrip.py` and `python tests/audit_roundtrip.py`
  both exit 0, unchanged by this plan.

The sidecar grows additively:

- `graph.SECTION_ORDER` contains `"Blueprint"`.
- `graph.serialize_course(graph.parse_course(golden_text))` equals
  `golden_text` byte for byte, where `golden_text` is the stored
  `fixtures/corpus_15b.py` golden sidecar written before this plan's change and
  carrying no `## Blueprint` section. A sidecar not using the new section
  parses unchanged, proven by bytes.
- `graph.add_blueprint(doc, bp)` appends one row to the blueprint section and
  `graph.blueprints(doc)` returns it.
- `graph.add_blueprint(doc, {"construct": "x"})` raises `GraphError` with code
  `graph.blueprint_invalid` because the dict fails
  `schemas/blueprint.schema.json`'s `required` set.

The one end-to-end path:

- `fixtures.corpus_15b.build_blueprint_fixture(dest)` returns a dict carrying
  the keys `course_root`, `blueprint`, `bank_path`, `state_dir`, and
  `item_facts`.
- `course.bind_blueprint(course_root, bp, "human", "weibao",
  expected_fingerprint)` returns a revision record whose `revision` is one
  greater than before, and afterwards
  `graph.blueprints(course.read_course(course_root)["doc"])` has exactly one
  more row than before.
- One `authoring.run_authoring(request, author_callable, bank_text, writer,
  config)` call with `config["blueprint"]` set to the bound blueprint and
  `config["item_facts"]` set to the fixture's facts returns a report whose
  `status` is `"written"`, whose `proposal.gates` carries a
  `blueprint_findings` array, and after which the bank file on disk contains
  the drafted items.
- The same call with a drafted set whose item count is outside the blueprint's
  tolerance returns a report whose `status` is `"failed"`, whose `outcome` is
  `"retry_cap_exhausted"`, and after which the bank file's bytes are
  unchanged. A blocked blueprint gate writes nothing.
- After the successful run, `blueprint.fidelity_claim` over the five gate
  results the run recorded is `True`; after the blocked run it is `False`.

Degraded behavior this task must prove, not paper over:

- With `config["blueprint"]` absent or `None`, `run_authoring` still completes
  and writes: the returned report's `gates.blueprint_findings` holds exactly
  one finding whose `code` is `blueprint.absent` at severity `warn`,
  `blueprint_gate_blocks` is `False`, and `blueprint.fidelity_claim` over the
  recorded gate results is `False`. Practice is presented; the exam-fidelity
  claim is not.
- With `config["item_facts"]` absent, the seven unverifiable fields each still
  produce their `blueprint.unverifiable` warn finding and the run still writes.
- The shipped suites still pass: `python tests/scoring_roundtrip.py`,
  `python tests/audit_authoring_roundtrip.py`, `python tests/audit_quality_roundtrip.py`,
  and `python tests/audit_roundtrip.py` each exit 0.
  </behavior>
  <action>
1. Create `tests/blueprint_roundtrip.py` first, with the local `fail(msg)`
   helper that prints `"FAIL: " + msg` and calls `sys.exit(1)`, the `ROOT` and
   `sys.path.insert` header convention every existing roundtrip test uses, a
   `check_thin_slice()` function holding every assertion in `<behavior>`, and a
   `main()` that calls it and prints `OK blueprint_roundtrip`. Run it with
   `python tests/blueprint_roundtrip.py` and confirm it fails because
   `blueprint.py` does not exist yet.

2. Create `schemas/blueprint.schema.json` with
   `"$schema": "https://json-schema.org/draft/2020-12/schema"`,
   `"$id": "https://itembank.local/schemas/blueprint.schema.json"`,
   `"title": "itembank assessment blueprint"`, `"x-itembank-version": 1`,
   `type: object`, `additionalProperties: false`, and `required` equal to
   `["schema_version", "blueprint_id", "version", "construct",
   "domain_weight", "demand", "format", "difficulty", "timing", "tools",
   "feedback_conditions", "citations"]`. Its properties, exactly:
   - `schema_version`: const 1.
   - `blueprint_id`: string, `minLength` 1.
   - `version`: integer, `minimum` 1. ACTIVITY-02 requires a versioned
     blueprint; version 0 does not exist.
   - `construct`: string, `minLength` 1. What the form claims to measure.
   - `domain_weight`: array of objects, each `additionalProperties: false`,
     `required` `["domain", "objective_prefix", "share", "tolerance"]`, with
     `domain` a string `minLength` 1, `objective_prefix` a string `minLength`
     1, `share` an integer `minimum` 0 `maximum` 100, and `tolerance` an
     integer `minimum` 0 `maximum` 100.
   - `demand`: array of objects, each `additionalProperties: false`, `required`
     `["level", "share", "tolerance"]`, with `level` a string `enum`
     `["recall", "application", "analysis"]`, and `share` and `tolerance`
     integers `minimum` 0 `maximum` 100.
   - `format`: object, `additionalProperties: false`, `required`
     `["permitted_types", "item_count", "count_tolerance"]`, with
     `permitted_types` an array of strings `minItems` 1, `item_count` an
     integer `minimum` 1, and `count_tolerance` an integer `minimum` 0.
   - `difficulty`: object, `additionalProperties: false`, `required`
     `["permitted_bands", "band_weight"]`, with `permitted_bands` an array of
     strings `minItems` 1 and `band_weight` an array of objects each
     `additionalProperties: false` and `required` `["band", "share",
     "tolerance"]` with the same integer bounds.
   - `timing`: object, `additionalProperties: false`, `required`
     `["total_seconds", "per_item_seconds", "tolerance_seconds"]`, all three
     integers `minimum` 0.
   - `tools`: object, `additionalProperties: false`, `required`
     `["permitted"]`, with `permitted` an array of strings. An empty array
     means no tool is permitted, which is a real declaration and not an
     omission; the description says so in plain words.
   - `feedback_conditions`: object, `additionalProperties: false`, `required`
     `["disclosure", "retry"]`, with `disclosure` a string `enum`
     `["none", "score-only", "score-and-rationale"]` and `retry` a string
     `enum` `["none", "once", "unlimited"]`.
   - `citations`: array of objects, `minItems` 1, each
     `additionalProperties: false` with `required`
     `["source_object_id", "locator"]`, both strings `minLength` 1. A blueprint
     with no citation is not a cited blueprint, so `minItems` is 1.

   The document's top-level `description` states in plain sentences that this
   is the contract ACTIVITY-02's "cited, versioned blueprint" names, that a
   surface never claims exam fidelity without a document valid against it, that
   every share and tolerance is an integer percentage point rather than a
   float so a tolerance boundary is exact, and that a share equal to the
   declared value plus or minus the declared tolerance passes. Use no schema
   keyword outside `schema_validate.SUPPORTED` and
   `schema_validate.ANNOTATIONS`. No em dash characters.

3. Create `blueprint.py` at the repository root. Open it with a module
   docstring restating the peer-module contract from `evidence.py` lines 1 to
   19, and stating in plain sentences: this module is a pure classifier; every
   function takes what it needs as an argument and reads no file, opens no
   socket, and writes nothing; it imports `model` and `runtime` and nothing
   else from this repository, and it imports them precisely so that gate 1's
   parse and gate 5's verdict are the one parser and the one scorer rather than
   copies; it deliberately does not import `evidence`, so the rule that a
   quality or acceptance decision never touches the learner evidence store is
   structural rather than maintained by care; it deliberately does not import
   `journal`, `course`, `graph`, `director`, or `audit_writer`, so the rule
   that this module never writes and never authorizes is likewise structural;
   and it never returns an aggregate compliance score, following
   `authoring.py`'s own recorded rule that the second quality gate keeps each
   detector's record and never combines them. No em dash characters anywhere
   in the file.

4. Define in `blueprint.py`: `BLUEPRINT_SCHEMA_VERSION = 1`;
   `BLUEPRINT_SCHEMA_RESOURCE = "schemas/blueprint.schema.json"`;
   `BLUEPRINT_FIELDS = ("construct", "domain_weight", "demand", "format",
   "difficulty", "timing", "tools", "feedback_conditions")` with a comment
   recording that the order is ACTIVITY-02's own and is not to be sorted;
   `BLUEPRINT_DETECTOR = "blueprint_fidelity"`;
   `BLUEPRINT_DETECTOR_VERSION = 1`;
   `GATE_STEPS = ("parser", "lint", "review", "blueprint", "runtime")` with a
   comment recording that the order is ACTIVITY-02's own five-gate prose and
   that gate 4 runs after gate 3 deliberately;
   `GATE_RESULT_KEYS = ("step", "passed", "findings")`;
   `SET_FACT_KEYS = ("construct", "feedback_conditions")`;
   `ITEM_FACT_KEYS = ("demand", "timing_seconds", "tools")`;
   `WARN_CODES = ("blueprint.absent", "blueprint.unverifiable")`; and
   `BLUEPRINT_CODES` as a set-then-sorted tuple following `ADAPTER_CODES`'s
   construction, holding exactly these thirteen members:
   `blueprint.absent`, `blueprint.construct_mismatch`,
   `blueprint.demand_out_of_tolerance`, `blueprint.difficulty_out_of_band`,
   `blueprint.difficulty_share_out_of_tolerance`,
   `blueprint.domain_weight_out_of_tolerance`,
   `blueprint.feedback_conditions_mismatch`, `blueprint.format_not_permitted`,
   `blueprint.invalid`, `blueprint.item_count_out_of_tolerance`,
   `blueprint.runtime_mismatch`, `blueprint.timing_out_of_tolerance`,
   `blueprint.tools_not_permitted`, `blueprint.unverifiable`.

   Note the list above names fourteen strings and `BLUEPRINT_CODES` holds
   thirteen: `blueprint.invalid` is a `BlueprintError` code raised by
   `validate_blueprint` and is not a finding code, so it is defined as its own
   module constant `BLUEPRINT_INVALID = "blueprint.invalid"` and is excluded
   from `BLUEPRINT_CODES`. Record that distinction in a comment above the
   tuple.

5. Define `BlueprintError(Exception)` carrying `.code` and `.message`, using
   the same two-argument constructor shape `graph.GraphError` and
   `course.CourseError` use. Its message templates for this plan, verbatim:
   - `blueprint.invalid`: `"the blueprint document is not valid against
     schemas/blueprint.schema.json: %s; a blueprint that does not validate is
     never bound and never gates anything"`

6. Implement `canonical_json(obj)` as a one-line wrapper over
   `json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))`,
   matching `authoring.canonical_json`'s purpose so the two sort keys agree.
   Implement `validate_blueprint(doc)` by loading
   `schemas/blueprint.schema.json` through `resources.py`'s existing resource
   resolution if one exists, otherwise by an explicit path join from
   `os.path.dirname(os.path.abspath(__file__))`, then calling
   `schema_validate.validate(doc, schema)`, raising `BlueprintError` with code
   `blueprint.invalid` on any failure and returning the document otherwise.
   `blueprint.py` may import `schema_validate`, `json`, `os`, and `re` in
   addition to `model` and `runtime`; `schema_validate` is a pure validator and
   does not weaken any structural ban.

7. Implement `blueprint_finding(code, severity, item, evidence, remediation)`
   returning a dict with exactly the eight keys
   `schema_version`, `detector`, `detector_version`, `severity`, `code`,
   `item`, `evidence`, `remediation`, with `schema_version` `1`, `detector`
   `BLUEPRINT_DETECTOR`, and `detector_version` `BLUEPRINT_DETECTOR_VERSION`.
   Raise `ValueError` when `code` is not in `BLUEPRINT_CODES` or `severity` is
   not `"block"` or `"warn"`, so a typo cannot mint a finding.

8. Implement `blueprint_gate(questions, blueprint_doc, item_facts=None)` in its
   thin form:
   - `questions or []` and `item_facts or {}` first, so an empty or null input
     is a real case and not a crash.
   - When `blueprint_doc` is falsy, return exactly
     `[blueprint_finding("blueprint.absent", "warn", "BANK", {"bound": False},
     "bind a blueprint through course.bind_blueprint before claiming exam fidelity")]`
     and nothing else.
   - Otherwise call `validate_blueprint(blueprint_doc)` first, so the gate
     never reads a field of an unvalidated document.
   - Check `format` only: for each question whose `type` is not in
     `blueprint_doc["format"]["permitted_types"]`, emit one
     `blueprint.format_not_permitted` block finding whose `item` is the
     question's `id` and whose `evidence` is
     `{"observed_type": <type>, "permitted_types": <sorted list>}`, with the
     remediation string `"replace or remove this item; the blueprint permits
     only the listed response types"`. Then, when
     `abs(len(questions) - item_count) > count_tolerance`, emit one
     `blueprint.item_count_out_of_tolerance` block finding whose `item` is the
     literal `"BANK"` and whose `evidence` is `{"observed_count": ...,
     "declared_count": ..., "tolerance": ...}`, with the remediation string
     `"add or remove items until the set is within the blueprint's declared
     count tolerance"`. The comparison is strictly greater than, so a
     difference equal to the tolerance passes.
   - For each of the seven `BLUEPRINT_FIELDS` members other than `format`, emit
     exactly one `blueprint.unverifiable` warn finding whose `item` is `"BANK"`
     and whose `evidence` is `{"field": <name>, "reason":
     "not-yet-implemented"}`, with the remediation string `"this blueprint
     field is declared but not yet checked; the exam-fidelity claim rests only
     on the fields reported as checked"`.
   - Return `sorted(findings, key=lambda f: (f["item"], f["code"],
     canonical_json(f["evidence"])))`.

   Implement `blueprint_gate_blocks(questions, blueprint_doc, item_facts=None)`
   as `any(f["severity"] == "block" for f in blueprint_gate(...))`, mirroring
   `authoring.quality_gate_blocks` exactly.

9. Implement `runtime_conformance(questions)`: for each question, compute
   `runtime.canonical_key(q)`; when it is `None`, skip the question entirely
   (a constructed response is not-yet-marked, not wrong); otherwise call
   `runtime.score_response(q, <the answer that reproduces that key>)` and when
   the verdict is not `True`, emit one `blueprint.runtime_mismatch` block
   finding whose `item` is the question's `id` and whose `evidence` is
   `{"canonical_key": <key>, "verdict": <verdict>}`, with the remediation
   string `"this item's recorded key does not score correct through the one
   scorer; fix the key before the item leaves draft"`. Return the findings
   sorted by the same three-part key. This function calls the shipped scorer
   and defines no scoring rule of its own.

10. Implement `gate_result(step, passed, findings)` returning a dict with
    exactly `GATE_RESULT_KEYS`, raising `ValueError` when `step` is not in
    `GATE_STEPS`. Implement `fidelity_claim(gate_results)` returning `True`
    only when the set of `step` values present equals `set(GATE_STEPS)` and
    every `passed` is `True`, and `False` in every other case including an
    empty list, a partial list, and a list carrying a step twice. It reads
    nothing else.

11. Edit `schemas/audit_report.schema.json`. Add to
    `$defs.proposal.properties.gates.properties` one new property
    `blueprint_findings`, an array whose `items` is
    `{"$ref": "#/$defs/blueprint_finding_ref"}`, with the description
    `"blueprint-fidelity findings from the fourth ACTIVITY-02 gate; absent on a
    proposal built before Phase 15B, and present but carrying one
    blueprint.absent warn record when no blueprint is bound."` Do not change
    `gates.required`. Add to `$defs` a new member `blueprint_finding_ref`
    copying `quality_finding_ref`'s shape exactly, except that its `detector`
    enum is `["blueprint_fidelity"]` and its `code` enum is the thirteen
    `BLUEPRINT_CODES` members. Run `python schema_validate.py` over the schemas
    directory and confirm it reports no error.

12. Edit `graph.py`. Append `"Blueprint"` to `SECTION_ORDER` as its last
    member, with a one-line comment naming Phase 15B and ACTIVITY-02 as its
    reason and stating that a sidecar with no such section parses unchanged.
    Add `add_blueprint(doc, blueprint)`, which calls
    `blueprint.validate_blueprint` is NOT permitted here because `graph.py` may
    not import `blueprint`; instead it checks the blueprint dict's key set
    against a module-level `BLUEPRINT_REQUIRED_KEYS` tuple holding the same
    twelve names as the schema's `required` array and raises `GraphError` with
    code `graph.blueprint_invalid` and the message `"a blueprint row needs
    every one of the twelve required blueprint keys; missing: %s"` on any
    absence. Add `blueprints(doc)` returning the section's rows in insertion
    order. Add the shape for the new section to
    `schemas/course_graph.schema.json` as an optional property; change no
    existing `required` array in that file.

13. Edit `course.py`. Add
    `bind_blueprint(course_root, blueprint, actor_kind, actor_name, expected_fingerprint)`,
    which reads the course through `read_course`, calls `graph.add_blueprint`,
    and writes through `write_course` with the supplied
    `expected_fingerprint`, following `bind_treatment`'s existing shape exactly
    including its `CourseError` propagation. It performs no rights check and no
    autonomy check; those belong to plan 15B-04's acceptance path and are out
    of scope here.

14. Edit `authoring.py`. Add `import blueprint` beside `import model`. In
    `run_authoring`, read `bp = config.get("blueprint")` and
    `item_facts = config.get("item_facts")` beside the existing `target_path`
    and `state_dir` reads. Inside the retry loop, immediately after the
    existing `quality_findings` block at lines 751 to 754, add:
    `blueprint_findings = blueprint.blueprint_gate(questions, bp, item_facts)`
    and, when any has `severity` `"block"`, append a new
    `_blueprint_findings_payload(blueprint_findings)` to `findings_chain` and
    `continue`. Define `_blueprint_findings_payload(findings)` beside
    `_quality_findings_payload`, returning
    `{"schema_version": 1, "kind": "blueprint", "records": findings}`. In the
    preflight recheck at lines 772 to 791, recompute `blueprint_findings` and
    add its blocking condition to the existing `if` alongside `scope_findings`
    and `lint_errors`. Pass `blueprint_findings` to `build_proposal` as a new
    last parameter with a default of `None`, and have `build_proposal` write
    `"blueprint_findings": blueprint_findings or []` inside its `gates` dict.
    Change nothing else in this file.

15. Create `fixtures/corpus_15b.py` with `build_blueprint_fixture(dest)`,
    `build_draft_set(dest, variant)`, `build_golden_sidecar(dest)`, and
    `teardown(dest)`, following `fixtures/corpus_14b.py`'s fixed-seed,
    no-randomness, no-clock-read convention so two calls with the same
    arguments produce equal output. `build_golden_sidecar` writes a sidecar
    with no `## Blueprint` section and returns its exact bytes, which the
    byte-identical assertion compares against. `build_draft_set(dest,
    variant)` accepts the variants `"conforming"`, `"wrong_type"`,
    `"over_count"`, and `"bad_key"`. All content is fictional: the subject is a
    fictional standards blueprint stand-in, and no real course, book, exam,
    learner, or bank content of any kind appears. Run
    `python itembank.py guard .` and confirm `0 offending files`.

16. Append to
    `.planning/phases/14B-graph-course-package-prototype/14B-FREEZE.md` a dated
    section headed `## Amendment 15B: SECTION_ORDER gained Blueprint` recording
    the date, the added member, the reason (ACTIVITY-02's durable blueprint
    object, per `D-15B-2` option-a), the statement that no existing member
    changed position or value, and the byte-identical golden fixture that
    proves a sidecar without the section parses unchanged. Do this only when
    `D-15B-2` recorded `option-a`. No em dash characters.
  </action>
  <verify>
  <automated>python tests/blueprint_roundtrip.py && python tests/audit_authoring_roundtrip.py && python tests/audit_roundtrip.py && python schema_validate.py && python itembank.py guard .</automated>
Expected: `tests/blueprint_roundtrip.py` prints `OK blueprint_roundtrip` and
exits 0; both shipped audit suites exit 0 unchanged; `schema_validate.py`
reports no error; `guard` prints `0 offending files`. The degraded behavior this
task must prove rather than paper over is the unbound-blueprint path: with
`config["blueprint"]` absent, `run_authoring` still writes, the proposal carries
exactly one `blueprint.absent` warn finding, and `fidelity_claim` is `False`.
Confirm both halves, the write and the withheld claim, in the same run.
  </verify>
  <acceptance_criteria>
- `python tests/blueprint_roundtrip.py` exits 0 and prints
  `OK blueprint_roundtrip`.
- `python -c "import blueprint; print(len(blueprint.BLUEPRINT_FIELDS), len(blueprint.GATE_STEPS), len(blueprint.BLUEPRINT_CODES))"`
  prints `8 5 13`.
- `python -c "import blueprint; print(hasattr(blueprint,'evidence'), hasattr(blueprint,'journal'), hasattr(blueprint,'course'), hasattr(blueprint,'director'), hasattr(blueprint,'graph'))"`
  prints `False False False False False`.
- `python -c "import blueprint; print(blueprint.fidelity_claim([]))"` prints
  `False`.
- `python -c "import json,schema_validate; schema_validate.check_schema(json.load(open('schemas/blueprint.schema.json'))); print('schema ok')"`
  prints `schema ok`.
- `python -c "import json; s=json.load(open('schemas/audit_report.schema.json')); g=s['\$defs']['proposal']['properties']['gates']; print(sorted(g['required']), 'blueprint_findings' in g['properties'], 'blueprint_finding_ref' in s['\$defs'])"`
  prints `['lint_errors', 'lint_warnings', 'quality_findings'] True True`.
- `python -c "import graph; print('Blueprint' in graph.SECTION_ORDER, callable(graph.add_blueprint), callable(graph.blueprints))"`
  prints `True True True`.
- `python tests/audit_authoring_roundtrip.py`, `python tests/audit_quality_roundtrip.py`,
  `python tests/audit_roundtrip.py`, and `python tests/scoring_roundtrip.py`
  each exit 0.
- `python schema_validate.py` reports no error.
- `python itembank.py guard .` prints `0 offending files`.
- `grep -n "number" schemas/blueprint.schema.json | grep -v '^#'` returns no
  line in which `number` is a `type` value.
- None of `blueprint.py`, `schemas/blueprint.schema.json`,
  `fixtures/corpus_15b.py`, or `tests/blueprint_roundtrip.py` contains an em
  dash character.
  </acceptance_criteria>
  <precondition>Plan 15B-01 recorded a clean precondition and recorded answers under `## D-15B-1` and `## D-15B-2` in `15B-DECISIONS.md`.</precondition>
  <reversibility rating="costly">`blueprint.BLUEPRINT_FIELDS`,
  `blueprint.GATE_STEPS`, and `blueprint.BLUEPRINT_CODES` are consumed by plans
  03 through 07. Changing them before the 15B freeze gate costs one edit plus
  one fixture regeneration. The genuinely one-way parts, the module boundary
  and the blueprint's durable home, are gated by plan 15B-01's two
  checkpoints.</reversibility>
  <done>One drafted set and one cited blueprint travel parse, lint, review,
  blueprint, and runtime to an accepted bank write in one green test, the
  exam-fidelity claim is False until the fifth gate reports, and `blueprint.py`
  exists in its thinnest production-quality form.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: the seven remaining blueprint fields and the claim discipline</name>
  <files>blueprint.py, fixtures/corpus_15b.py, tests/blueprint_roundtrip.py</files>
  <read_first>
- `blueprint.py` in full as it stands after Task 1, in particular
  `BLUEPRINT_FIELDS`, `BLUEPRINT_CODES`, `blueprint_finding`, and
  `blueprint_gate`'s thin `format` branch, which this task extends rather than
  replaces.
- `schemas/blueprint.schema.json` as written by Task 1, all twelve required
  properties and their exact inner shapes.
- `.planning/REQUIREMENTS.md` ACTIVITY-02 in full, including its Fixture
  sentence and its Degraded clause, quoted: "absent a blueprint, the course
  presents practice without an exam-fidelity claim".
- `authoring.py` lines 380 to 559, the four shipped detectors and
  `quality_gate`'s sort key, so this task's added checks stay clear of the
  failure modes those four already own.
- `model.py` `parse_bank` at line 60, for the exact question dict keys
  `difficulty` and `objective` this task's `difficulty` and `domain_weight`
  checks read.
- `fixtures/corpus_15b.py` as written by Task 1, the four `build_draft_set`
  variants this task extends.
  </read_first>
  <behavior>
Assertions `check_blueprint_fields()` and `check_gate_edges()` in
`tests/blueprint_roundtrip.py` must make. Write them first and confirm they
fail before extending `blueprint.py`.

`check_blueprint_fields()`, one case per remaining field:

- `domain_weight`: a set whose observed share for a declared domain, computed
  as the count of questions whose `objective` starts with that domain's
  `objective_prefix` divided by the question count and rounded to the nearest
  integer percentage point with ties rounding up, differs from the declared
  `share` by more than the declared `tolerance` produces exactly one
  `blueprint.domain_weight_out_of_tolerance` block finding whose `item` is
  `"BANK"` and whose `evidence` carries `observed_share`, `declared_share`,
  `tolerance`, and `domain`.
- `domain_weight` boundary: a set whose observed share differs from the
  declared share by exactly the tolerance produces no such finding.
- `difficulty`: a question whose `difficulty` is not in `permitted_bands`
  produces exactly one `blueprint.difficulty_out_of_band` block finding whose
  `item` is that question's `id`.
- `difficulty` share: a band whose observed share is outside its declared
  `share` plus or minus `tolerance` produces exactly one
  `blueprint.difficulty_share_out_of_tolerance` block finding whose `item` is
  `"BANK"`.
- `demand`: with `item_facts` supplying a `demand` per item id, a level whose
  observed share is outside tolerance produces exactly one
  `blueprint.demand_out_of_tolerance` block finding; a level with no supplied
  fact for any item produces exactly one `blueprint.unverifiable` warn finding
  naming `demand` and no block finding.
- `timing`: with `item_facts` supplying `timing_seconds` per item id, a summed
  total outside `total_seconds` plus or minus `tolerance_seconds`, or any item
  whose seconds exceed `per_item_seconds` plus `tolerance_seconds`, produces
  exactly one `blueprint.timing_out_of_tolerance` block finding per violation,
  with the per-item one carrying that item's `id`.
- `tools`: an item whose supplied `tools` list contains a value outside
  `permitted` produces exactly one `blueprint.tools_not_permitted` block
  finding carrying that item's `id`. An empty `permitted` array with a
  non-empty supplied `tools` list produces the same finding; an empty
  `permitted` array with an empty supplied list produces none.
- `construct`: a supplied set-level `construct` fact whose value is not equal
  to the blueprint's `construct` after both are stripped and compared as exact
  ASCII produces exactly one `blueprint.construct_mismatch` block finding whose
  `item` is `"BANK"`.
- `feedback_conditions`: a supplied set-level `feedback_conditions` fact whose
  `disclosure` or `retry` differs from the blueprint's produces exactly one
  `blueprint.feedback_conditions_mismatch` block finding whose `evidence` names
  the differing key, its observed value, and its declared value.
- With every fact supplied and every value conforming, `blueprint_gate` returns
  an empty findings list and `blueprint_gate_blocks` is `False`.
- No `blueprint.unverifiable` finding remains for any of the eight fields when
  every fact is supplied.

`check_gate_edges()`, the three ACTIVITY-02 probe edges resolved:

- Adjacency: for every share check the gate makes (`domain_weight`,
  `demand`, `difficulty` band share) and for `format`'s count and `timing`'s
  totals, an observed value differing from the declared value by exactly the
  declared tolerance produces no finding, and by the tolerance plus one
  produces exactly one. Assert both sides for each, so equality passing is
  proven rather than assumed.
- Empty and single: `blueprint_gate([], bp)` returns `[]`;
  `blueprint_gate([q], bp)` computes every share against a denominator of one
  and raises no `ZeroDivisionError`; `blueprint_gate(None, bp)` is treated as
  `[]`; `blueprint_gate([], None)` returns exactly the one
  `blueprint.absent` finding; `blueprint_gate([], bp, {})` returns `[]`.
- Ordering and stability: two `blueprint_gate` calls over the same input return
  lists that compare equal and whose `canonical_json` renderings are byte
  identical; a set constructed so that two findings share an `item` and a
  `code` and differ only in `evidence` sorts deterministically by
  `canonical_json(evidence)`; shuffling the input question order does not
  change the returned findings list.

The no-aggregate rule, asserted structurally:

- A recursive walk over `blueprint_gate`'s full findings list and over every
  `gate_result` dict finds no value of type `float`, and no key whose lowercase
  name contains any of `mastery`, `completion`, `readiness`, `progress`,
  `percent`, or `score`. `share` and `tolerance` are integers and are the only
  proportion-shaped values present.
  </behavior>
  <action>
1. Extend `check_blueprint_fields()` and add `check_gate_edges()` in
   `tests/blueprint_roundtrip.py` with every assertion in `<behavior>`, wire
   both into `main()`, and run `python tests/blueprint_roundtrip.py` to confirm
   they fail.

2. Extend `fixtures/corpus_15b.py`'s `build_draft_set(dest, variant)` with the
   variants `"domain_skew"`, `"domain_boundary"`, `"bad_band"`,
   `"band_share_skew"`, `"demand_skew"`, `"timing_over"`, `"tool_forbidden"`,
   `"construct_mismatch"`, `"feedback_mismatch"`, and `"fully_conforming"`,
   plus a `build_item_facts(dest, variant)` returning the matching supplied
   facts dict keyed by item id with `SET_FACT_KEYS` at the top level. All
   content stays fictional and fixed-seed.

3. Extend `blueprint_gate` in `blueprint.py` so each of the seven remaining
   `BLUEPRINT_FIELDS` members is checked when its fact is supplied and produces
   exactly one `blueprint.unverifiable` warn finding naming the field when it
   is not. Order the checks in `BLUEPRINT_FIELDS` order, and keep the single
   final `sorted(...)` call as the only thing that decides output order.

4. Implement the share computation once, as a module-level helper
   `observed_share(count, total)` returning
   `int((count * 200 + total) // (total * 2))` for `total` greater than zero
   and `0` for `total` equal to zero, which is integer rounding to the nearest
   percentage point with ties rounding up and no float anywhere. Every share
   check calls it; none computes its own.

5. Implement the tolerance comparison once, as a module-level helper
   `within_tolerance(observed, declared, tolerance)` returning
   `abs(observed - declared) <= tolerance`. Every tolerance check calls it. The
   comparison is less than or equal, which is what makes the boundary
   inclusive, and a comment above it records that this matches the shipped
   `authoring.SKEW_BLOCK_ABOVE` equality-passes precedent.

6. Add the recursive-walk assertion helper to `tests/blueprint_roundtrip.py`
   as `check_no_aggregate(obj, where)`, which walks dicts, lists, and tuples,
   fails on any `float`, and fails on any dict key whose `lower()` contains one
   of the six banned substrings. Call it on the findings list, on every
   `gate_result`, and on the fixture blueprint itself.

7. Confirm the exam-fidelity claim discipline end to end: with the
   `"fully_conforming"` draft set and full facts, the five gate results are all
   `passed` and `fidelity_claim` is `True`; with `"tool_forbidden"`, gate 4
   reports `passed` `False` and `fidelity_claim` is `False` even though gates
   1, 2, 3, and 5 all pass. Assert both.
  </action>
  <verify>
  <automated>python tests/blueprint_roundtrip.py && python tests/audit_authoring_roundtrip.py && python itembank.py guard .</automated>
Expected: `tests/blueprint_roundtrip.py` prints `OK blueprint_roundtrip` and
exits 0, the shipped authoring suite exits 0 unchanged, and `guard` prints
`0 offending files`. The degraded behavior this task must prove rather than
paper over is the partially supplied facts case: with `item_facts` supplying
`demand` but not `tools`, the gate produces the `demand` findings it can and
exactly one `blueprint.unverifiable` warn finding for `tools`, and
`fidelity_claim` is still computed from the five gate results rather than being
suppressed. A field nobody could check is reported, never assumed passing.
  </verify>
  <acceptance_criteria>
- `python tests/blueprint_roundtrip.py` exits 0 with
  `check_blueprint_fields` and `check_gate_edges` both run.
- `python -c "import blueprint; print(blueprint.within_tolerance(45,40,5), blueprint.within_tolerance(46,40,5))"`
  prints `True False`.
- `python -c "import blueprint; print(blueprint.observed_share(1,3), blueprint.observed_share(0,0), blueprint.observed_share(1,2))"`
  prints `33 0 50`.
- `python -c "import blueprint; print(blueprint.blueprint_gate([], None)[0]['code'], len(blueprint.blueprint_gate([], None)))"`
  prints `blueprint.absent 1`.
- `python -c "import blueprint; print(blueprint.blueprint_gate(None, None) == blueprint.blueprint_gate([], None))"`
  prints `True`.
- `check_no_aggregate` runs over the findings list, every gate result, and the
  fixture blueprint, and finds no `float` and no key containing `mastery`,
  `completion`, `readiness`, `progress`, `percent`, or `score`.
- `python itembank.py guard .` prints `0 offending files`.
- `git diff --name-only` after this task lists only `blueprint.py`,
  `fixtures/corpus_15b.py`, and `tests/blueprint_roundtrip.py`.
- None of the three changed files contains an em dash character.
  </acceptance_criteria>
  <precondition>Task 1 is green and `blueprint.py` exists with its thin `format` branch.</precondition>
  <reversibility rating="reversible">Every check added here is an internal
  branch of one function with its own finding code; adding, removing, or
  retuning one costs one edit and one fixture variant.</reversibility>
  <done>All eight ACTIVITY-02 blueprint fields are checked when their facts are
  supplied and reported unverifiable when they are not, the tolerance boundary
  is inclusive and proven on both sides, and the exam-fidelity claim is False
  whenever any of the five gates has not reported passed.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| drafted set to accepted bank | A model-authored question set becomes durable repository content; five gates stand between the draft and the write. |
| caller-supplied item facts to the gate | The five blueprint fields the bank format does not carry arrive as caller assertions and are untrusted input. |
| blueprint document to gate decision | An unvalidated blueprint could authorize a fidelity claim over fields nobody checked. |
| shipped Phase 11 loop to the new gate | `authoring.run_authoring` is shipped, executed, tested code; a new gate inserted into it can break a shipped contract. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-15B-02-01 | Spoofing | an exam-fidelity claim surfacing without all five gates | high | mitigate | `fidelity_claim` returns `True` only when the set of recorded `step` values equals `set(GATE_STEPS)` and every `passed` is `True`; the empty, partial, and duplicated-step cases are each asserted to return `False`. |
| T-15B-02-02 | Tampering | a blueprint field silently passing because nobody could check it | high | mitigate | Every unsupplied fact produces one `blueprint.unverifiable` warn finding naming the field; the thin form in Task 1 emits seven of them by construction, so a field is never absent from the report. |
| T-15B-02-03 | Tampering | an unvalidated blueprint document gating a claim | high | mitigate | `blueprint_gate` calls `validate_blueprint` before reading any field, and `graph.add_blueprint` refuses a row missing any of the twelve required keys with `graph.blueprint_invalid` before it is ever stored. |
| T-15B-02-04 | Elevation of Privilege | `blueprint.py` acquiring the ability to write or to authorize | high | mitigate | The module imports only `model`, `runtime`, `schema_validate`, `json`, `os`, and `re`; the absence of `journal`, `course`, `graph`, `director`, `audit_writer`, and `evidence` is asserted at runtime by five `hasattr` checks. |
| T-15B-02-05 | Tampering | a second scorer or a second parser entering through the fifth gate | high | mitigate | `runtime_conformance` calls `runtime.canonical_key` and `runtime.score_response` and defines no comparison of its own; the `None` case for a constructed response is passed through rather than reinterpreted, so not-yet-marked never becomes wrong. |
| T-15B-02-06 | Tampering | a shipped Phase 11 contract broken by the new gate | high | mitigate | `gates.required` is unchanged, `build_proposal`'s new parameter is appended last with a default of `None`, and `tests/audit_authoring_roundtrip.py`, `tests/audit_quality_roundtrip.py`, and `tests/audit_roundtrip.py` are in this task's acceptance criteria. |
| T-15B-02-07 | Tampering | a course sidecar format change breaking existing documents | high | mitigate | The `## Blueprint` section is appended to `SECTION_ORDER` and validated as optional; a stored golden sidecar written without the section round-trips byte identically through `parse_course` and `serialize_course`, asserted as bytes rather than promised. |
| T-15B-02-08 | Information Disclosure | real course, exam, or bank content entering as a fixture | high | mitigate | `fixtures/corpus_15b.py` builds fictional content from a fixed rule with no randomness and no clock read, the plan forbids paraphrase as well as copying, and `python itembank.py guard .` is in both tasks' acceptance criteria. |
| T-15B-02-09 | Tampering | supply chain: a diff, NLP, or numeric dependency added for the classifier | high | mitigate | None is added; blueprint fidelity is closed-vocabulary comparison over already-structured integers and strings. Per `PLANNING-DIRECTIVES.md` section 4a the absence of dependencies is explicitly not the mitigation: any dependency ever added here is vendored at a pinned version with a recorded checksum and a named license review, following the KaTeX precedent in `09-03-PLAN.md`. |
| T-15B-02-10 | Repudiation | a blocked gate whose reason is not recorded | medium | mitigate | Every blocking path appends a `_blueprint_findings_payload` to `findings_chain`, which the failed report returns, so a refused write carries the per-field reason it was refused. |
| T-15B-02-11 | Denial of Service | a pathological question set making the gate quadratic | low | accept | Every check is a single pass over the question list; the only nested loop is over the blueprint's own declared domains, which the schema does not bound but which a human authors. Accepted because the input is repository-local and a slow gate is a loud local failure with no data at risk. |
</threat_model>

<out_of_scope>
Refused by this plan, by name, so no adjacent temptation is decided by executor
judgment:

- No staleness check of any kind. `blueprint.classify_staleness`,
  `STALENESS_DISPOSITIONS`, and the acceptance block are plan 15B-03's.
- No acceptance path. `graph.accept_migration`, `graph.reject_migration`,
  `course.accept_migration`, `director.accept_revision`, and the new
  `journal.RECORD_TYPES` member are plan 15B-04's. This plan writes a blueprint
  through `course.bind_blueprint` with no rights check and no autonomy check,
  and says so in that function's docstring.
- No course audit. `blueprint.course_audit` and
  `schemas/course_audit_report.schema.json` are plan 15B-05's.
- No evidence-based proposal. `blueprint.evidence_proposal` and
  `schemas/evidence_proposal.schema.json` are plan 15B-06's, and `evidence.py`
  is not imported by anything this plan writes.
- No fifth `quality_finding.schema.json` detector. The four-member `detector`
  enum in that shipped schema is unchanged; blueprint findings live in their
  own `$defs.blueprint_finding_ref`.
- No new bank format field. `demand`, `timing_seconds`, `tools`, `construct`,
  and `feedback_conditions` are supplied by the caller, not parsed from a bank.
  Adding them to the format is a separate additive change with its own
  byte-identical fixture proof and its own phase.
- No re-derivation of duplicate stems, answer-position skew, answer leak, or
  distractor rationale. Those are `model.lint`'s and
  `authoring.quality_gate`'s, at two different rigor levels, and a third pass
  would let three detectors disagree.
- No CLI command and no daemon route. `OPERATION-CONTRACT.md`'s "Pending
  surfaces" section names the course and binding commands as not yet shippable
  and says in plain words not to invent commands for them.
- No change to `build.py`'s `STAGE_FILES`. Packaging the new module family is
  one coherent change owned by whichever phase first ships a CLI surface for
  it.
- No aggregate compliance value anywhere, in any function, under any name.
</out_of_scope>

<flagged_assumptions>
Surfaced, not silently dropped, per the spec-less probe fallback protocol. All
three ACTIVITY-02 probe rows are resolved above and appear in this plan's
`must_haves.truths` as explicit statements: adjacency is the inclusive
tolerance boundary, empty is the empty and single-question and unbound-blueprint
behavior, and ordering is the three-part deterministic sort key. None of the
three is carried forward as an open assumption.

- **The five caller-supplied fields rest on caller honesty (assumption,
  recorded).** `construct`, `demand`, `timing_seconds`, `tools`, and
  `feedback_conditions` are checked against what the caller asserts, because
  the bank format carries none of them. A caller asserting a false fact
  produces a green gate over a false premise. This is not closed by this phase;
  closing it means adding those fields to the parsed format, which is an
  additive format change with its own byte-identical fixture proof, and is
  owned by whichever phase does that. Recorded here so plan 15B-07's freeze
  record carries it as an open item rather than implying the eight fields are
  equally well grounded.
</flagged_assumptions>

<summary_obligations>
`15B-02-SUMMARY.md` records: which truth was verified by which command, with
the command's actual stdout; the exact `git diff --stat authoring.py` output,
so the size of the change to shipped Phase 11 code is visible; the byte
comparison result for the golden sidecar, quoted; the measured wall-clock time
of one `check_thin_slice()` run and one full `tests/blueprint_roundtrip.py`
run, recorded and not promised; whether the `14B-FREEZE.md` amendment was
written and under which recorded `D-15B-2` option; and any deviation from this
plan with its reason.
</summary_obligations>

<output>
Create
`.planning/phases/15B-quality-blueprint-acceptance/15B-02-SUMMARY.md`
when done.
</output>
