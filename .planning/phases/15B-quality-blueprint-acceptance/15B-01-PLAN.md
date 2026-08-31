---
phase: 15B-quality-blueprint-acceptance
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - .planning/phases/15B-quality-blueprint-acceptance/15B-PRECONDITION.md
  - .planning/phases/15B-quality-blueprint-acceptance/15B-DECISIONS.md
autonomous: false
requirements: [ACTIVITY-02, RELIABILITY-03, AGENT-03]
estimate:
  tokens: 52000
  raw_tokens: 52000
  tasks: 3
  confidence: low
must_haves:
  truths:
    - "Phase 15B writes no code that imports identity, journal, graph, course, or director until a recorded precondition check has confirmed that all seven dependency modules exist and that every constant this phase was planned against matches on disk; a divergence halts the wave by name instead of surfacing as an ImportError or a silent vocabulary drift mid-task."
    - "All three freeze records, 14A-FREEZE.md, 14B-FREEZE.md, and 15A-FREEZE.md, are checked for their own frozen headings, and a file that opens with a Freeze withheld heading counts as a failed check rather than as a present record."
    - "The two one-way doors this phase cannot silently adopt are settled and recorded before any module file exists: where the blueprint, staleness, audit, and acceptance code lives (D-15B-1), and where a blueprint document lives plus which write path records an acceptance plus which journal record type it uses (D-15B-2)."
    - "Every 15B plan that follows reads 15B-DECISIONS.md for its module boundary and its write path rather than re-deriving either, so the executor never chooses a module name or a write path by judgment."
    - "The shipped Phase 11 surface this phase composes is re-checked live before it is composed: authoring.DETECTOR_VERSIONS still has exactly four members, model.LINT_CODES still carries bank.answer_position_skew, item.duplicate_stem, and item.distractor_no_would_be, and schemas/audit_report.schema.json's gates object still requires exactly lint_errors, lint_warnings, and quality_findings."
  prohibitions:
    - statement: "A failed precondition check must not be worked around by stubbing a missing module, by wrapping the import in a try or except, by continuing with a reduced check set, or by recording the divergence and proceeding anyway; the halt is the correct outcome."
      status: kept
      verification: flagged-unverified
    - statement: "An unanswered checkpoint must not receive a silent default; a decision recorded as chosen when nobody chose it is a false record of authority."
      status: kept
      verification: flagged-unverified
  artifacts:
    - ".planning/phases/15B-quality-blueprint-acceptance/15B-PRECONDITION.md with its four named sections"
    - ".planning/phases/15B-quality-blueprint-acceptance/15B-DECISIONS.md carrying the dated headings D-15B-1 and D-15B-2"
  key_links:
    - "The precondition check re-asserts graph.MIGRATION_STATES and the continued existence of the graph.migration_state_not_settable refusal code. Plan 15B-04 adds the only two functions permitted to perform the proposed-to-accepted transition; if 14B landed without the refusal in place, 15B-04 would be adding an accept path beside an already-open one and the test that the bypass still refuses would pass for the wrong reason."
    - "D-15B-2 decides three coupled things at once (the blueprint document's durable home, which of the two existing write paths records an acceptance, and the one new journal.RECORD_TYPES member). They are one decision because a blueprint stored in the course sidecar is written by course.write_course by construction, and a blueprint stored in its own file is not. Splitting them would let a later plan pick a home and a write path that disagree."
    - "15B-DECISIONS.md is read by every later 15B plan before its first task. A decision recorded here in words a plan cannot act on (for example a chosen option with no recorded consequence for the files_modified lists) leaves the executor choosing after all, which is the exact failure PLANNING-DIRECTIVES section 5 exists to prevent."
---

<objective>
Do the three things that must happen before any Phase 15B code exists.

First, verify that Phases 14A, 14B, and 15A actually landed on disk with the
surface 15B was planned against, and halt by name if they did not. This is one
step deeper than the same check plans 14B-01 and 15A-01 already ran:
`15B-RESEARCH.md`'s "Critical caveat: Phase 15B's entire dependency chain is
unexecuted" records that `identity.py`, `journal.py`, `discovery.py`,
`graph.py`, `course.py`, `course_package.py`, `director.py`, and
`fixtures/corpus_14b.py` all read MISSING at the repository root when this
phase was researched and planned, and that no `*-FREEZE.md` file existed for
any of the three phases. Every signature this phase imports was therefore read
from plan text, never from source.

Second and third, settle the two one-way design doors this phase cannot
silently adopt, both named as checkpoint candidates by `15B-RESEARCH.md`'s own
Assumptions Log (A1 and A3) and by its Open Questions.

Decisions already made, cited, and never re-derived here:

- **PLANNING-DIRECTIVES section 4**, all five non-negotiables, in particular
  number 2 (exactly one parser, one scorer, one evidence store) and number 4
  (format changes are additive, proven by a byte-identical fixture and not by
  promise).
- **PLANNING-DIRECTIVES section 4a**, the citation-discipline rule: this plan
  quotes the sentence behind every constraint it invokes.
- **PLANNING-DIRECTIVES section 2 rule 1**: a planning session stops only for
  an action that is hard to reverse, "such as an append-only evidence field, a
  published schema, a format decision other phases will build against". Both
  checkpoints in this plan are exactly that class and are the only two this
  plan raises.
- **ROADMAP.md Phase 15B "Depends on"**, quoted: "Phases 14A, 14B, and 15A are
  planned but not yet executed, so every signature this phase imports is read
  from plan text at planning time; the first 15B plan opens with a recorded
  precondition check that halts by name on any divergence, the same pattern
  plans 14B-01 and 15A-01 set, extended to check for a `15A-FREEZE.md` record."
- **15B-RESEARCH.md Don't Hand-Roll table**: every problem this phase touches
  already has a shipped or planned owner. This plan set composes; it does not
  rebuild `authoring.quality_gate`, `audit_writer.write_units`,
  `journal.commit_operation`, `model.lint`, `runtime.score_response`,
  `director.authorize_write`, or `graph.migration_proposal`.

Decisions this plan makes and locks, so the executor never guesses (the
`PLANNING-DIRECTIVES.md` section 5 bar):

| Open question | Locked answer | One-line rationale |
|---|---|---|
| Does `DRAFT_STATES` become one seven-member tuple applied to every object kind | No. No `DRAFT_STATES` constant is minted anywhere in Phase 15B; each object kind keeps its own narrow closed state set, as `graph.MIGRATION_STATES` already does with three members | `15B-RESEARCH.md` Open Question 2, recommendation: the seven words in synthesis section 4.1 are a naming vocabulary to draw individual states from, not a single enum to instantiate wholesale. Named here explicitly so the executor does not invent a seven-member tuple no object kind uses in full. |
| Which vocabulary the staleness dispositions use | Exactly the four words `REQUIREMENTS.md` RELIABILITY-03 itself uses, in its own order: `rebind`, `migrate`, `supersede`, `retain` | RELIABILITY-03's text reads "require a rebind, migrate, supersede, or retain review". The vocabulary is transcribed from the requirement, not chosen by this phase, so there is no open question and no checkpoint is owed. Minted as `blueprint.STALENESS_DISPOSITIONS` by plan 15B-03. |
| Whether a fourth coverage-state vocabulary is minted | No. Three exist and the course audit cites which of the three each row came from | `15B-RESEARCH.md` Pitfall 2 and the ROADMAP 15B goal, quoted: "one cited report that names which existing state vocabulary each claim came from and mints no fourth". |
| Whether `blueprint_gate` becomes a fifth `quality_finding.schema.json` detector | No. It is a sibling gate function with its own findings array and its own `$defs` reference | `15B-RESEARCH.md` Assumption A2 and ACTIVITY-02's own five-gate prose ("parser, lint, review, blueprint, and runtime") listing them as distinct stages. |

Purpose: make the rest of the phase transcription rather than judgment.
Output: one recorded precondition result and two recorded decisions.
</objective>

<context>
@.planning/phases/15B-quality-blueprint-acceptance/15B-RESEARCH.md
@.planning/phases/15B-quality-blueprint-acceptance/15B-PATTERNS.md
@.planning/phases/15B-quality-blueprint-acceptance/15B-VALIDATION.md
@.planning/PLANNING-DIRECTIVES.md
@.planning/PLAN-TEMPLATE.md
@.planning/ROADMAP.md
@.planning/REQUIREMENTS.md
@.planning/phases/15A-director-treatment-policy/15A-01-PLAN.md
@.planning/phases/15A-director-treatment-policy/15A-04-PLAN.md
@.planning/phases/15A-director-treatment-policy/15A-05-PLAN.md
@.planning/phases/14A-identity-lifecycle-operation/14A-02-PLAN.md
@.planning/phases/14B-graph-course-package-prototype/14B-03-PLAN.md
@.planning/phases/14B-graph-course-package-prototype/14B-04-PLAN.md
@.agents/skills/OPERATION-CONTRACT.md
</context>

## Artifacts this phase produces (plan 15B-01 share)

This plan creates no module, no schema, no test, and no fixture. It creates
exactly two planning artifacts, both new in this phase:

- `.planning/phases/15B-quality-blueprint-acceptance/15B-PRECONDITION.md`
- `.planning/phases/15B-quality-blueprint-acceptance/15B-DECISIONS.md`

New symbols introduced by this plan: none.
New refusal codes introduced by this plan: none.
New journal record types introduced by this plan: none.
No CLI command and no daemon route is produced by this plan.

The full symbol inventory for the phase, so the plan-review source-grounding
pass can exclude newly created names from drift verification, is repeated in
each later plan's own "Artifacts this phase produces" section. The union across
plans 02 through 07 is: `blueprint.py` and every constant, exception, and
function on it; `schemas/blueprint.schema.json`;
`schemas/course_audit_report.schema.json`;
`schemas/evidence_proposal.schema.json`; `graph.accept_migration`,
`graph.reject_migration`, `graph.add_blueprint`, `graph.blueprints`;
`course.bind_blueprint`, `course.accept_migration`, `course.reject_migration`;
`director.accept_revision`; one new `journal.RECORD_TYPES` member;
`authoring.build_proposal`'s new `blueprint_findings` parameter and the
`gates.blueprint_findings` array in `schemas/audit_report.schema.json`;
`fixtures/corpus_15b.py`; `tests/blueprint_roundtrip.py`;
`tests/acceptance_tracer.py`; and the planning artifacts
`15B-PRECONDITION.md`, `15B-DECISIONS.md`, `15B-TRACER-REPORT.md`,
`15B-REVIEW.md`, `15B-FREEZE.md`.

<tasks>

<task type="auto">
  <name>Task 1: verify Phases 14A, 14B, and 15A landed, or halt by name</name>
  <files>.planning/phases/15B-quality-blueprint-acceptance/15B-PRECONDITION.md</files>
  <read_first>
- `.planning/phases/15B-quality-blueprint-acceptance/15B-RESEARCH.md`, the
  section "Critical caveat: Phase 15B's entire dependency chain is unexecuted,
  and Phase 11 is executed but partially superseded" and the Assumptions Log,
  in full. This task exists because of them.
- `.planning/phases/15A-director-treatment-policy/15A-01-PLAN.md` Task 1, in
  full. This task copies its shape exactly and extends it by one phase.
- `.planning/phases/14A-identity-lifecycle-operation/14A-01-PLAN.md`, the
  "Artifacts this phase produces" section, for the `identity.py` constant list.
- `.planning/phases/14A-identity-lifecycle-operation/14A-02-PLAN.md`, the
  "Artifacts this phase produces" section, for `journal.ENTRY_KEYS`,
  `journal.RECORD_TYPES`, `journal.OPERATION_TYPES`, and the fixed-order
  entry tuple. Read `14A-FREEZE.md` for that tuple, not `14A-02-PLAN.md`:
  the plan text lists twenty-two keys ending in `message` and is the stale
  record; the freeze record lists twenty-three ending in `rights`.
- `.planning/phases/14B-graph-course-package-prototype/14B-01-PLAN.md`, the
  "Artifacts this phase produces" section, for `graph.SECTION_ORDER`,
  `course.COURSE_SIDECAR_FILENAME`, and `course.write_course`'s signature.
- `.planning/phases/14B-graph-course-package-prototype/14B-03-PLAN.md`, the
  "Artifacts this phase produces" section, for `graph.TREATMENT_KINDS`,
  `graph.BINDING_STATES`, `graph.BINDING_KINDS`, `course.bind_treatment`, and
  `course.rights_for_binding`.
- `.planning/phases/14B-graph-course-package-prototype/14B-04-PLAN.md`, the
  "Artifacts this phase produces" section and the `<behavior>` lines 266 to
  293, for `graph.MIGRATION_KINDS`, `graph.MIGRATION_STATES`,
  `graph.migration_proposal`'s eight-key return, the
  `graph.migration_state_not_settable` refusal, and
  `course.record_migration`.
- `.planning/phases/15A-director-treatment-policy/15A-01-PLAN.md`,
  `15A-04-PLAN.md`, and `15A-05-PLAN.md`, the "Artifacts this phase produces"
  section of each, for `director.AGENT_ENTRY_KEYS`, `director.EGRESS_KEYS`,
  `director.RECOMMENDATION_KEYS`, `director.AUTONOMY_LEVELS`,
  `director.autonomy_level`, `director.authorize_write`,
  `director.untreated_objectives`, `director.classify_coverage`,
  `director.PROTOCOL_STEPS`, and `director.record_phase`.
- `.planning/phases/14B-graph-course-package-prototype/14B-DECISIONS.md`, the
  dated section `## D-14B-1. Sidecar path and the Phase 13.9 supersession`, and
  `## D-14B-3. Where migrate lives and what a proposal carries`. The options
  recorded there decide which filename and which journal vocabulary step 4
  below asserts. Read the recorded options and use them; do not assume either.
  </read_first>
  <action>
1. Check that the seven dependency modules import. Run:

```
python -c "import identity, journal, discovery, graph, course, course_package, director; print('modules present')"
```

   Expected stdout: `modules present`, exit code 0.

2. Check that the frozen 14A constants match what Phase 15B was planned
   against. Run a single `python -c` that asserts, in this order, every one of
   the following, printing `14A surface matches` on success:
   - `identity.OBJECT_KINDS` equals `("course", "objective", "source",
     "lesson", "bank", "component")`.
   - `identity.RIGHTS_OPERATIONS` equals `("read", "quote", "transform",
     "remote_process", "package", "export", "share")`.
   - `identity.RIGHTS_STATES` equals `("granted", "denied", "unknown")`.
   - Every one of these names is callable on its module:
     `identity.new_object_id`, `identity.object_fingerprint`,
     `identity.rights_state`, `identity.rights_granted`,
     `journal.commit_operation`, `journal.append_entry`, `journal.entries`,
     `journal.read_registry`, `journal.undo`, `journal.object_state`.
   - `journal.OPERATION_TYPES` has exactly six members.
   - `journal.ENTRY_KEYS` has exactly `24` members and its last member is
     `"agent"` (twenty-three frozen in `14A-FREEZE.md` plus the one member
     plan 15A-01 appended). (Corrected by the 2026-08-30 planning pass: the landed pre-15A tuple has twenty-three keys ending in `rights`, per `14A-FREEZE.md`, not the twenty-two `14A-02-PLAN.md` lists. See `15A-PRECONDITION.md`.)
   - `"reconcile"`, `"migrate"`, and `"agent_operation"` are all in
     `journal.RECORD_TYPES`.

3. Check that the frozen 14B constants match. Run a single `python -c` that
   asserts, in this order, every one of the following, printing
   `14B surface matches` on success:
   - `graph.TREATMENT_KINDS` has exactly eleven members.
   - `graph.BINDING_STATES` equals `("covered", "thin", "missing",
     "conflicting", "unknown")`.
   - `graph.BINDING_KINDS` equals `("source", "treatment")`.
   - `graph.MIGRATION_KINDS` equals `("split", "merge", "rename",
     "demand-change", "overlay")`.
   - `graph.MIGRATION_STATES` equals `("proposed", "accepted", "rejected")`.
   - `graph.COURSE_GRAPH_VERSION` equals `1`.
   - `graph.SECTION_ORDER` is a tuple, and the string `"Blueprint"` is NOT in
     it. Plan 15B-02 adds it; finding it already present means something else
     added it and the plan must be re-read before it does.
   - Every one of these names is callable on its module:
     `graph.parse_course`, `graph.serialize_course`, `graph.add_binding`,
     `graph.add_source`, `graph.migration_proposal`, `graph.treatment_right`,
     `course.read_course`, `course.write_course`, `course.bind_source`,
     `course.bind_treatment`, `course.rights_for_binding`,
     `course.record_migration`.
   - `course.COURSE_SIDECAR_FILENAME` equals the filename the recorded
     `D-14B-1` option implies: `"course-graph.md"` under option-a,
     `"course.md"` under option-b. Under option-c, record the value found and
     treat a mismatch with option-a as a deviation rather than a halt.
   - `hasattr(graph, "accept_migration")` is `False` and
     `hasattr(graph, "reject_migration")` is `False`. Phase 14B refused to
     build the acceptance path and named this phase as its owner; finding one
     present means the gap plan 15B-04 was written to close is already closed
     by something else.
   - `"graph.migration_state_not_settable"` is still a live refusal: calling
     the 14B function that sets a recorded migration row's state (read
     `14B-04-PLAN.md` step 4 for its name) with `state="accepted"` raises
     `GraphError` with that code. If the function cannot be reached from
     outside, assert instead that the literal string
     `graph.migration_state_not_settable` appears in `graph.py`'s source.

4. Check that the frozen 15A constants match. Run a single `python -c` that
   asserts, in this order, every one of the following, printing
   `15A surface matches` on success:
   - `len(director.PROTOCOL_STEPS)` equals `13`, and its first member is
     `"declare-intent"` and its last member is `"report"`.
   - `director.AUTONOMY_LEVELS` equals `("recommend-only", "draft-and-review",
     "approved-bounded-write")`.
   - `len(director.AGENT_ENTRY_KEYS)` equals `10`,
     `len(director.EGRESS_KEYS)` equals `7`, and
     `len(director.RECOMMENDATION_KEYS)` equals `9`.
   - `director.autonomy_level({})` returns `"recommend-only"`.
   - `director.authorize_write({}, "recommend-only", 0)` returns `None`.
   - Every one of these names is callable on its module:
     `director.authorize_write`, `director.autonomy_level`,
     `director.record_phase`, `director.begin_operation`,
     `director.replay_operation`, `director.untreated_objectives`,
     `director.classify_coverage`, `director.parity_view`.
   - `hasattr(director, "evidence")` is `False`.

5. Check that the shipped Phase 11 surface this phase composes is still what
   `15B-RESEARCH.md` read. Run:

```
python -c "import authoring, model, json; s=json.load(open('schemas/audit_report.schema.json')); g=s['\$defs']['proposal']['properties']['gates']; print(len(authoring.DETECTOR_VERSIONS), sorted(g['required']), 'blueprint_findings' in g['properties'], all(c in model.LINT_CODES for c in ('bank.answer_position_skew','item.duplicate_stem','item.distractor_no_would_be')))"
```

   Expected stdout exactly:
   `4 ['lint_errors', 'lint_warnings', 'quality_findings'] False True`

6. Check that all three freeze records exist and are real freezes, not
   withholdings:
   - `.planning/phases/14A-identity-lifecycle-operation/14A-FREEZE.md` contains
     the literal heading `## Frozen at 14A`.
   - `.planning/phases/14B-graph-course-package-prototype/14B-FREEZE.md`
     contains the literal heading `## Frozen at 14B`.
   - `.planning/phases/15A-director-treatment-policy/15A-FREEZE.md` contains
     the literal heading `## Frozen at 15A`.
   - None of the three contains the literal heading `## Freeze withheld`. A
     file carrying a withholding heading fails this check even if the frozen
     heading is also present, because a phase that withheld its freeze has not
     frozen its surface and 15B cannot plan against it.

7. If any check in steps 1 through 6 fails, STOP. Write nothing else, create no
   module, and print exactly this line with the failing item substituted for
   `<item>`, then exit non-zero:

   `HALT 15B-01 precondition: Phase 14A, Phase 14B, or Phase 15A has not landed, or its frozen surface differs from what Phase 15B was planned against. Re-verify every 15B plan against .planning/phases/14A-identity-lifecycle-operation/14A-FREEZE.md, .planning/phases/14B-graph-course-package-prototype/14B-FREEZE.md, and .planning/phases/15A-director-treatment-policy/15A-FREEZE.md before writing any code. Divergent or missing: <item>`

   Do not work around a failure by stubbing the missing module, by wrapping the
   import in a try or except, by continuing with a reduced check set, or by
   recording the divergence and proceeding anyway. A halt here is the correct
   outcome; it is what this task is for.

8. On success, create
   `.planning/phases/15B-quality-blueprint-acceptance/15B-PRECONDITION.md` with
   exactly these four sections and nothing more:
   - **Why this check exists.** One paragraph citing `15B-RESEARCH.md`'s
     Critical Caveat: every 14A, 14B, and 15A signature in the 15B research and
     pattern map was read from plan text, not from source, because the modules
     did not exist when 15B was planned, and 15B is fourth in a chain of four
     unexecuted phases.
   - **What was checked.** The full list from steps 1 through 6, one line each,
     each marked `ok` or `divergent`.
   - **Deviations found.** Every place the landed 14A, 14B, or 15A surface
     differs from the plan text, with the plan-text value and the landed value
     side by side. Write `none` when there are none. A deviation here is not a
     failure of this task; it is the signal that plans 02 through 07 must be
     re-read against the three freeze records before execution, and this
     section is where a later plan looks for it.
   - **Dated result line.** The date, the command output of steps 2, 3, 4 and 5
     verbatim, and one sentence stating whether 15B may proceed.

   No em dash characters anywhere in the file.
  </action>
  <verify>
  <automated>python -c "import identity, journal, graph, course, director; assert len(graph.MIGRATION_STATES)==3 and len(graph.BINDING_STATES)==5 and len(director.PROTOCOL_STEPS)==13 and len(journal.ENTRY_KEYS)==24 and not hasattr(graph,'accept_migration'); print('15B preconditions match')"</automated>
Expected: prints `15B preconditions match` and exits 0. The degraded state this
task must prove rather than paper over is the halt itself: if any assertion
fails, the run exits non-zero with the named HALT line and no module file is
created. Confirm this by checking that `blueprint.py` does not exist on disk at
the end of a failed run.
  </verify>
  <acceptance_criteria>
- The step 1 command prints `modules present` and exits 0.
- The step 2 command prints `14A surface matches` and exits 0.
- The step 3 command prints `14B surface matches` and exits 0.
- The step 4 command prints `15A surface matches` and exits 0.
- The step 5 command prints exactly
  `4 ['lint_errors', 'lint_warnings', 'quality_findings'] False True`.
- All three freeze files exist, each contains its own `## Frozen at` heading,
  and none contains `## Freeze withheld`.
- `.planning/phases/15B-quality-blueprint-acceptance/15B-PRECONDITION.md`
  exists with all four named sections.
- `15B-PRECONDITION.md` contains no em dash character.
  </acceptance_criteria>
  <precondition>Phases 14A, 14B, and 15A have executed and `identity.py`, `journal.py`, `discovery.py`, `graph.py`, `course.py`, `course_package.py`, and `director.py` exist at the repository root with the surfaces frozen in `14A-FREEZE.md`, `14B-FREEZE.md`, and `15A-FREEZE.md`.</precondition>
  <reversibility rating="reversible">The file records a check; nothing durable is created and the check can be re-run at any time.</reversibility>
  <done>Either 15B is cleared to proceed with the evidence recorded, or the
  wave is halted with the divergence named.</done>
</task>

<task type="checkpoint:decision" gate="blocking">
  <name>Task 2: where the blueprint, staleness, audit, and acceptance code lives</name>
  <files>.planning/phases/15B-quality-blueprint-acceptance/15B-DECISIONS.md</files>
  <read_first>
- `15B-RESEARCH.md`, the "Summary" section, the "Architectural Responsibility
  Map" table, the "Alternatives Considered" table, and Assumption A1, all in
  full. A1 is the reason this is a checkpoint rather than a silent adoption.
- `15B-PATTERNS.md`, the `blueprint.py` row of the File Classification table
  and its Pattern Assignment section, for the `auditor.py` analog this module
  would follow.
- `auditor.py` lines 370 to 421, `coverage_report`, the shipped pure-transform
  precedent option-a copies.
- `.planning/phases/15A-director-treatment-policy/15A-01-PLAN.md`, the
  objective's decision table row reading "Module name and tier", which locked
  `director.py`'s scope as an agent-client-tier peer of `model_adapter.py`.
  That lock is what option-b widens.
- `.planning/phases/14B-graph-course-package-prototype/14B-01-PLAN.md`, the
  "Artifacts this phase produces" section, for the pure-versus-I/O split
  between `graph.py` and `course.py` that option-a extends.
- `.planning/phases/15B-quality-blueprint-acceptance/15B-DECISIONS.md` if it
  already exists, so the new section is appended rather than overwriting one.
  </read_first>
  <decision>
Does Phase 15B add one new pure classifier module and extend the three existing
owners for the parts that touch authority and disk, or does one new module own
the whole capability including its orchestration, or do two new modules split
the two halves?
  </decision>
  <context>
Phase 15B adds four capabilities: blueprint fidelity, a course audit, an
accepted revision, and staleness with dependency impact. Three of the four are
pure computations over data a caller supplies. The fourth, accepted revision,
must re-check the live autonomy policy and the live rights registry at the
moment of acceptance (`15B-RESEARCH.md` Pitfall 3) and must write through
`course.write_course`, so it is not pure.

`14B` already established a pure-versus-I/O split in this exact domain:
`graph.py` is the pure kernel that owns `MIGRATION_STATES` and
`migration_proposal`, and `course.py` is the I/O layer that owns
`record_migration` and calls `journal.commit_operation`. `15A` added
`director.py` above both, which already owns `authorize_write`,
`autonomy_level`, and `record_phase`.

This is rated one-way. The chosen module name and boundary appear in every
import in plans 02 through 07, in every `hasattr` structural-ban assertion, in
the 15B freeze record, and in whatever Phase 16 builds on top. Undoing it after
the freeze means renaming a published surface, not editing a line.
  </context>
  <options>
    <option id="option-a">
      <name>RECOMMENDED DEFAULT: one new pure module plus three extensions of the existing owners</name>
      <pros>One new root-level module, `blueprint.py`, importing only `model`
      and `runtime` from this repository and holding every classifier and
      report builder as a pure function over its arguments: blueprint schema
      logic, `blueprint_gate`, `runtime_conformance`, `classify_staleness`,
      `STALENESS_DISPOSITIONS`, `course_audit`, and `evidence_proposal`. The
      acceptance capability is split across the three modules that already own
      its parts: the pure proposed-to-accepted transition goes to `graph.py`
      beside `MIGRATION_STATES` (which is exactly where `15B-RESEARCH.md`'s
      "New in this phase" table already assigns
      `graph.accept_migration`/`graph.reject_migration`), its compare-and-swap
      write goes to `course.py` beside `record_migration`, and the live
      autonomy and rights re-check goes to `director.py` beside
      `authorize_write`. No import cycle is possible, because `blueprint.py`
      imports nothing that imports it, and `authoring.py` gains exactly one
      new lightweight import. `hasattr(blueprint, "evidence")`,
      `hasattr(blueprint, "journal")`, and `hasattr(blueprint, "course")` are
      all `False`, so the rules that this module never writes, never reads the
      evidence store, and never authorizes anything are structural rather than
      maintained by care.</pros>
      <cons>The acceptance capability is spread across four files, so a reader
      answering "how does a migration get accepted" follows three hops.
      `director.py`'s 15A-locked scope widens from "the treatment recommender
      and its rights and egress gate" to include one acceptance function, which
      is a real widening even though it lands beside the function it depends
      on.</cons>
    </option>
    <option id="option-b">
      <name>One new module owning the whole capability, orchestration included</name>
      <pros>One file answers "how does an acceptance work" completely.
      `director.py` stays exactly at its 15A-locked scope. This is closest to
      `15B-RESEARCH.md`'s literal primary recommendation, quoted: "build the
      blueprint/audit/acceptance layer as one new root-level peer
      module".</pros>
      <cons>`blueprint.py` then imports `identity`, `journal`, `graph`,
      `course`, `director`, `model`, and `runtime`, which makes the "pure
      classifier" claim false and makes the structural bans unavailable: a
      module that imports `journal` cannot assert that it never writes.
      `authoring.py`, shipped Phase 11 code that today imports only `model`,
      would transitively pull in `surfaces.settings` through `director`, which
      is a real weight increase on the shipped authoring loop for the sake of
      two gate functions.</cons>
    </option>
    <option id="option-c">
      <name>Two new modules, one pure and one orchestrating</name>
      <pros>Clean separation, `director.py` untouched, and `authoring.py`
      imports only the pure half. The most literal reading of 14B's own
      graph-versus-course precedent.</pros>
      <cons>Two new root-level modules in one phase, where the second holds
      three functions. It also duplicates the layering `graph.py` plus
      `course.py` plus `director.py` already provide, so a reader must learn
      why acceptance has its own stack when treatment binding does not.</cons>
    </option>
  </options>
  <action>
Ask Weibao the question above, present all three options with the recommended
default named, and record the answer verbatim in
`.planning/phases/15B-quality-blueprint-acceptance/15B-DECISIONS.md` under a
dated heading `## D-15B-1. Where the blueprint, staleness, audit, and
acceptance code lives`.

What the executor does with each answer:

- **option-a**: proceed as every task in plans 02 through 07 is already
  written. No plan edit is needed.
- **option-b**: before plan 15B-02 Task 1, record in `15B-DECISIONS.md` that
  `graph.py`, `course.py`, and `director.py` leave the `files_modified` lists
  of plans 15B-02 and 15B-04; that `blueprint.py` gains
  `accept_migration(course_root, migration_id, reviewer_kind, reviewer_name,
  rationale, expected_fingerprint)` and `reject_migration(...)` performing the
  transition, the write, and the authority re-check itself; that the
  `hasattr(blueprint, "evidence")` assertion stays and the
  `hasattr(blueprint, "journal")` and `hasattr(blueprint, "course")`
  assertions are dropped and replaced by a behavioral assertion that
  `blueprint.py` contains no `open(` call with a write mode; and that
  `authoring.py` imports `blueprint` anyway, accepting the transitive
  `surfaces.settings` import. Then build it that way.
- **option-c**: before plan 15B-02 Task 1, record in `15B-DECISIONS.md` that a
  second new module `acceptance.py` is created by plan 15B-04 holding
  `accept_migration`, `reject_migration`, and the authority re-check; that
  `graph.py`, `course.py`, and `director.py` leave plan 15B-04's
  `files_modified` list; and that plan 15B-07's freeze record enumerates two
  new modules rather than one. Then build it that way.

Do not proceed with a silent default. An unanswered checkpoint stops the wave.
  </action>
  <verify>
`15B-DECISIONS.md` exists and carries a dated `## D-15B-1` heading with the
chosen option id and Weibao's answer recorded verbatim.
  </verify>
  <acceptance_criteria>
- `.planning/phases/15B-quality-blueprint-acceptance/15B-DECISIONS.md` contains
  the literal heading `## D-15B-1. Where the blueprint, staleness, audit, and
  acceptance code lives`.
- The recorded answer names exactly one of `option-a`, `option-b`, `option-c`.
- When the answer is `option-b` or `option-c`, the file also carries the
  consequence list this task's action names for that option.
- The file contains no em dash character.
  </acceptance_criteria>
  <reversibility rating="one-way">The module name and boundary appear in every
  import in plans 02 through 07, in every structural-ban assertion, in the 15B
  freeze record, and in whatever Phase 16 builds on it. Undoing it after the
  freeze renames a published surface.</reversibility>
  <resume-signal>Reply with `option-a`, `option-b`, or `option-c`.</resume-signal>
</task>

<task type="checkpoint:decision" gate="blocking">
  <name>Task 3: where a blueprint lives, which write path records an acceptance, and which journal record type it uses</name>
  <files>.planning/phases/15B-quality-blueprint-acceptance/15B-DECISIONS.md</files>
  <read_first>
- `15B-RESEARCH.md`, the "Alternatives Considered" table row on routing
  bank-item acceptance through `journal.commit_operation`, the "Anti-Patterns
  to Avoid" section's first bullet on a third write path, and Assumption A3,
  all in full.
- `authoring.py` lines 1 to 32, the module docstring, specifically the sentence
  quoted: "`writer` is the one mutation seam (`audit_writer.write_units` in
  production): it accepts only an immutable preflighted proposal plus the
  expected bank fingerprint and rechecks under its own lock."
- `audit_writer.py` lines 200 to 206 and 288 to 322, `WriterError` and
  `write_units`'s stale-preflight refusal, the shipped compare-and-swap path
  for bank content.
- `.planning/phases/14A-identity-lifecycle-operation/14A-02-PLAN.md`, the
  "Artifacts this phase produces" section, for `journal.RECORD_TYPES`,
  `journal.OPERATION_TYPES`, and the twenty-three-key entry tuple frozen in
  `14A-FREEZE.md`.
- `.planning/phases/14B-graph-course-package-prototype/14B-04-PLAN.md` Task 1,
  the recorded `D-14B-3` checkpoint that already answered the same shape of
  question for `migrate`, and its options list.
- `.planning/phases/14B-graph-course-package-prototype/14B-01-PLAN.md`, the
  `graph.SECTION_ORDER` constant and `course.write_course`'s signature.
- `.planning/REQUIREMENTS.md` ACTIVITY-02 in full, including its Fixture
  sentence and its "Durable object: blueprint plus frozen form" clause.
- `.planning/phases/15B-quality-blueprint-acceptance/15B-DECISIONS.md`, so the
  new section is appended below `## D-15B-1`.
  </read_first>
  <decision>
Where does a cited, versioned blueprint document durably live, which of the two
existing write paths records an accepted revision, and does
`journal.RECORD_TYPES` gain a member for it?
  </decision>
  <context>
This project already has two compare-and-swap write paths, one per object kind,
both built and both proven: `audit_writer.write_units` for bank markdown
content (shipped Phase 11, and `authoring.py`'s only mutation seam), and
`journal.commit_operation` reached through `course.write_course` for
course-scoped objects (planned 14A and 14B). `15B-RESEARCH.md`'s Anti-Patterns
section names building a third as the failure to avoid.

A blueprint is a new durable course-scoped object with the same lifecycle as a
binding or a migration proposal. It has no home yet. Whichever home it gets
decides which write path records it, because a blueprint stored inside the
course sidecar is written by `course.write_course` by construction, and a
blueprint stored in its own file is not.

`journal.RECORD_TYPES` has grown additively four times already (`mint`,
`restore`, `external_edit`, `reconcile` in 14A; `migrate` in 14B;
`agent_operation` in 15A) while `journal.OPERATION_TYPES` stayed at exactly six
throughout. `14B-04-PLAN.md`'s recorded `D-14B-3` decision is the precedent for
this exact question.

This is rated one-way. The journal is append-only by construction, and the
sidecar's section list is a published format that `schemas/course_graph.schema.json`
validates. Changing either after any blueprint has been accepted is a migration
of recorded entries and stored documents, not an edit.
  </context>
  <options>
    <option id="option-a">
      <name>RECOMMENDED DEFAULT: an additive Blueprint section in the course sidecar, both write paths kept, one new RECORD_TYPES member</name>
      <pros>The blueprint becomes an additive `## Blueprint` section in the 14B
      course sidecar, so it is written by `course.write_course` reaching
      `journal.commit_operation`, and no new object kind and no new write path
      exists. `graph.SECTION_ORDER` gains exactly one member and
      `schemas/course_graph.schema.json` gains one section shape; both are
      additive changes proven by a byte-identical fixture (non-negotiable 4), so
      a sidecar with no `## Blueprint` section parses exactly as it does today.
      Bank-content acceptance stays on `audit_writer.write_units` through
      `authoring.run_authoring`, untouched. `journal.RECORD_TYPES` gains
      exactly one member, `"accept_revision"`, and `OPERATION_TYPES` stays at
      six, which is the same additive path `reconcile` and `migrate` already
      took twice.</pros>
      <cons>`graph.SECTION_ORDER` is named in `14B-FREEZE.md`, so adding a
      member needs a dated amendment note appended to that file recording the
      addition and its reason. Two write paths continue to exist, so a future
      reader asking "where is the history of this change" must know which
      object kind they are asking about.</cons>
    </option>
    <option id="option-b">
      <name>A separate blueprint file under the course root with its own object kind</name>
      <pros>A blueprint is a document in its own right and gets its own file,
      its own fingerprint, and its own revision history without touching the
      sidecar format or the 14B freeze.</pros>
      <cons>`identity.OBJECT_KINDS` is a frozen six-member tuple that does not
      include a blueprint kind, so this needs a 14A freeze amendment, which is
      a larger amendment than option-a's. It also splits one course's durable
      state across two files with no transactional relationship, so a crash
      between two writes leaves the sidecar and the blueprint file
      disagreeing.</cons>
    </option>
    <option id="option-c">
      <name>Unify: migrate bank-content acceptance onto journal.commit_operation</name>
      <pros>One write path, one history view, one answer to "what happened to
      this object". Removes the two-path ambiguity permanently.</pros>
      <cons>It rewrites shipped, executed, tested Phase 11 code
      (`audit_writer.py` and `authoring.py`'s writer seam) that this phase has
      no other reason to open, and re-proves compare-and-swap logic that
      already exists correctly in two independently proven forms. This is the
      one option `15B-RESEARCH.md`'s Alternatives Considered table rejects by
      name, with the note to reconsider it only when a future phase actually
      needs one unified history view across both object kinds.</cons>
    </option>
  </options>
  <action>
Ask Weibao the question above, present all three options with the recommended
default named, and record the answer verbatim in
`.planning/phases/15B-quality-blueprint-acceptance/15B-DECISIONS.md` under a
dated heading `## D-15B-2. Where a blueprint lives and which write path records
an acceptance`.

What the executor does with each answer:

- **option-a**: proceed as every task in plans 02 through 07 is already
  written. In addition, plan 15B-02 Task 1 appends a dated amendment section to
  `.planning/phases/14B-graph-course-package-prototype/14B-FREEZE.md` recording
  that `graph.SECTION_ORDER` gained the member `"Blueprint"` in Phase 15B, with
  the date, the reason (ACTIVITY-02's durable blueprint object), and the
  statement that no existing member changed position.
- **option-b**: before plan 15B-02 Task 1, record in `15B-DECISIONS.md` that
  `identity.OBJECT_KINDS` gains a seventh member `"blueprint"`, that
  `.planning/phases/14A-identity-lifecycle-operation/14A-FREEZE.md` gains a
  dated amendment section recording it, that `graph.SECTION_ORDER` and
  `schemas/course_graph.schema.json` leave plan 15B-02's `files_modified` list,
  that `course.py` gains `blueprint_path(course_root)` and
  `write_blueprint(course_root, doc, expected_fingerprint, actor_kind,
  actor_name)` instead of `bind_blueprint`, and that plan 15B-07's tracer adds
  a scenario asserting the crash-between-writes case leaves the sidecar
  unchanged and the blueprint file absent rather than the reverse.
- **option-c**: before plan 15B-02 Task 1, record in `15B-DECISIONS.md` that
  `audit_writer.py` and the Phase 11 writer seam enter this phase's scope, that
  `tests/audit_writer_roundtrip.py` and `tests/audit_authoring_roundtrip.py`
  enter every affected plan's verify commands, and that the phase estimate
  grows by one plan for the migration. Then stop and hand the plan set back for
  replanning, because a shipped-code migration of that size is a plan, not a
  task.

Do not proceed with a silent default. An unanswered checkpoint stops the wave.
  </action>
  <verify>
`15B-DECISIONS.md` carries a dated `## D-15B-2` heading with the chosen option
id and Weibao's answer recorded verbatim.
  </verify>
  <acceptance_criteria>
- `.planning/phases/15B-quality-blueprint-acceptance/15B-DECISIONS.md` contains
  the literal heading `## D-15B-2. Where a blueprint lives and which write path
  records an acceptance`.
- The recorded answer names exactly one of `option-a`, `option-b`, `option-c`.
- The recorded answer states, in one sentence each, the blueprint's durable
  home, the write path an acceptance uses, and whether `journal.RECORD_TYPES`
  gains a member and what it is named.
- When the answer is `option-b` or `option-c`, the file also carries the
  consequence list this task's action names for that option.
- The file contains no em dash character.
  </acceptance_criteria>
  <reversibility rating="one-way">The journal is append-only by construction and
  the sidecar section list is a schema-validated published format. Every
  acceptance recorded from this point carries the chosen shape, so a later
  change migrates recorded entries and stored documents rather than editing a
  line.</reversibility>
  <resume-signal>Reply with `option-a`, `option-b`, or `option-c`.</resume-signal>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| plan text to landed code | Every 14A, 14B, and 15A signature in this phase's research was read from plan text; the precondition check is the only place that boundary is tested before code is written. |
| freeze record to this phase | Whatever the three freeze records say is frozen is what plans 02 through 07 build against; a withheld freeze read as a present one would silently authorize planning against an unproven surface. |
| checkpoint answer to plan set | A recorded decision changes which files later plans may touch; a decision recorded without being asked would authorize a one-way change nobody chose. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-15B-01-01 | Tampering | the precondition check worked around instead of obeyed | high | mitigate | Step 7 forbids stubbing, `try` or `except` wrapping, a reduced check set, and recording-and-proceeding by name, and the acceptance criteria assert `blueprint.py` does not exist after a failed run. |
| T-15B-01-02 | Spoofing | a `Freeze withheld` file read as a present freeze record | high | mitigate | Step 6 checks for the absence of the literal `## Freeze withheld` heading in addition to the presence of `## Frozen at`, and states that a file carrying both fails. |
| T-15B-01-03 | Elevation of Privilege | a one-way module or write-path decision adopted without being asked | high | mitigate | Both decisions are `checkpoint:decision` tasks with `gate="blocking"`, each recording a named option id and a verbatim answer, and each action ends with the sentence that an unanswered checkpoint stops the wave. |
| T-15B-01-04 | Repudiation | a decision recorded with no consequence, leaving the executor to choose after all | high | mitigate | Each option's action block names the exact plan edits that option forces, so a non-default answer produces an actionable record rather than a note. |
| T-15B-01-05 | Tampering | the shipped Phase 11 surface drifting between research and execution | medium | mitigate | Step 5 re-checks `authoring.DETECTOR_VERSIONS`, three `model.LINT_CODES` members, and the `gates` object's `required` array live, with an exact expected stdout. |
| T-15B-01-06 | Tampering | supply chain: a third-party dependency introduced by this plan | high | mitigate | None is added; this plan runs only `python -c` against in-repo modules. Per `PLANNING-DIRECTIVES.md` section 4a the absence of dependencies is explicitly not the mitigation: the mitigation is that any dependency ever added here is vendored at a pinned version with a recorded checksum and a named license review, following the KaTeX precedent in `09-03-PLAN.md`. |
| T-15B-01-07 | Repudiation | a precondition file recording a check that was not run | medium | mitigate | The Dated result line section requires the verbatim stdout of steps 2, 3, 4 and 5, so a fabricated record would have to fabricate four command outputs whose expected values are written into the acceptance criteria. |
| T-15B-01-08 | Information Disclosure | real course or learner content entering the repository | low | accept | This plan creates only two planning markdown files and touches no fixture, bank, or evidence path. Accepted because there is no content path to leak through; `python itembank.py guard .` remains an acceptance check on every later plan that touches `fixtures/`. |
</threat_model>

<out_of_scope>
Refused by this plan, by name, so no adjacent temptation is decided by executor
judgment:

- No module file of any kind. `blueprint.py` is created by plan 15B-02 Task 1
  and by nothing earlier.
- No schema file. `schemas/blueprint.schema.json` is plan 15B-02's,
  `schemas/course_audit_report.schema.json` is plan 15B-05's, and
  `schemas/evidence_proposal.schema.json` is plan 15B-06's.
- No edit to `journal.py`, `graph.py`, `course.py`, `director.py`,
  `authoring.py`, `audit_writer.py`, `auditor.py`, `model.py`, `runtime.py`, or
  `evidence.py`. This plan reads them and changes none.
- No third checkpoint. The course-audit report schema question
  (`15B-RESEARCH.md` Open Question 1) is a real one-way decision but it is not
  needed until plan 15B-05, and it is raised there as `D-15B-3` immediately
  before the task that acts on it.
- No fixture and no test. `fixtures/corpus_15b.py` and
  `tests/blueprint_roundtrip.py` are plan 15B-02's.
- No freeze record and no freeze amendment. Plan 15B-07 owns the 15B freeze,
  and the `14B-FREEZE.md` amendment option-a implies is written by plan 15B-02
  Task 1, beside the change it records.
</out_of_scope>

<flagged_assumptions>
Surfaced, not silently dropped, per the spec-less probe fallback protocol. The
phase's eight probe rows are distributed to the plans that own their
requirements: the three ACTIVITY-02 rows are resolved in plan 15B-02's
`must_haves`, the four AGENT-03 rows in plan 15B-06's, and the one
RELIABILITY-03 row is carried as an unresolved flagged assumption in plan
15B-03 and into the freeze record by plan 15B-07. This plan holds none of the
eight itself.

- **The landed surface may differ from plan text (open until Task 1 runs).**
  Every constant value, function signature, and refusal code this plan asserts
  in Task 1 was read from `14A-*-PLAN.md`, `14B-*-PLAN.md`, and
  `15A-*-PLAN.md`, never from source, because none of those modules existed
  when 15B was planned. Task 1's Deviations found section is where a real
  divergence is recorded; a non-empty Deviations section means plans 02 through
  07 must be re-read against the three freeze records before execution, and
  this assumption is what makes that re-read owed rather than optional.
</flagged_assumptions>

<summary_obligations>
`15B-01-SUMMARY.md` records: the precondition result and every deviation the
landed 14A, 14B, and 15A surfaces showed against their plan text, quoted side by
side; the options Weibao chose at Tasks 2 and 3 and every plan edit those
choices forced in plans 02 through 07, by plan number and by file; which truth
was verified by which command, with the command's actual stdout; whether the
three freeze records were present, frozen, and free of a withholding heading;
and any deviation from this plan with its reason.
</summary_obligations>

<output>
Create
`.planning/phases/15B-quality-blueprint-acceptance/15B-01-SUMMARY.md`
when done.
</output>
