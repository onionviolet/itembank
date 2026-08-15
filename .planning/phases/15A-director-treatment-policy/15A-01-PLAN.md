---
phase: 15A-director-treatment-policy
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - director.py
  - model_adapter.py
  - schemas/model_adapter.schema.json
  - schemas/treatment_recommendation.schema.json
  - journal.py
  - fixtures/mock_backends.py
  - tests/director_roundtrip.py
  - .planning/phases/15A-director-treatment-policy/15A-PRECONDITION.md
  - .planning/phases/15A-director-treatment-policy/15A-DECISIONS.md
autonomous: false
requirements: [TREAT-01, RELIABILITY-02, AGENT-02]
estimate:
  tokens: 78000
  raw_tokens: 78000
  tasks: 4
  confidence: low
must_haves:
  truths:
    - "Phase 15A writes no code that imports identity, journal, graph, or course until a recorded precondition check has confirmed that all five modules exist and that the constants this phase was planned against match on disk; a divergence halts the wave by name instead of surfacing as an ImportError or a silent vocabulary drift mid-task."
    - "One synthetic objective travels the whole phase path end to end in one commit: an agent operation is opened in the one journal, a bounded recommendation request is built, it crosses the shipped model_adapter.invoke boundary to a mock hosted backend, the returned candidate is schema-validated and rights-checked live, and it becomes a treatment binding through course.bind_treatment with the operation, its checkpoint, and its egress recorded on one journal entry."
    - "The recommendation path never touches tier_gate.py. The imported director module exposes no attribute named tier_gate, because the learner-facing five-step no-leak gate protects a different asymmetry than a course-builder recommendation and importing it would produce refusal codes that mean the wrong thing."
    - "director.py holds no second rights vocabulary and no second journal: the imported module exposes no attribute named evidence, every rights decision reaches identity.rights_granted, and every durable write reaches journal.commit_operation through course.py."
    - "schemas/model_adapter.schema.json's operation enum grows by exactly one member and loses none; a request built with operation hint, rubric_review, or author validates byte-for-byte as it did before this plan, proven by re-running tests/model_adapter_roundtrip.py green."
    - "journal.py's diff for this whole phase is exactly two lines: one new RECORD_TYPES member and one new ENTRY_KEYS member. OPERATION_TYPES stays at exactly six."
    - "A backend that cannot be reached leaves the objective untreated and the core loop working: model_adapter.invoke returns a typed unavailable result, director records the operation outcome as unavailable, no binding is written, and the shipped scoring and evidence suites still pass."
  prohibitions:
    - statement: "An egress payload must not carry learner evidence, attempt records, scores, marks, session state, or private learner notes, in any field, under any treatment kind."
      status: kept
      verification: flagged-unverified
  artifacts:
    - "director.py at the repository root, an agent-client-tier peer of model_adapter.py, in its thinnest production-quality form"
    - "schemas/treatment_recommendation.schema.json, the candidate contract director validates a provider result against"
    - "schemas/model_adapter.schema.json with treatment_recommend as a fourth operation and recommendation_request as a bounded payload key"
    - "model_adapter.py with one new _PAYLOAD_KEYS member and one new runtime required-payload check"
    - "journal.py with exactly one new RECORD_TYPES member and one new ENTRY_KEYS member"
    - "fixtures/mock_backends.py, the one deterministic candidate builder both mock transports share"
    - "tests/director_roundtrip.py with check_thin_slice() as its first function"
    - ".planning/phases/15A-director-treatment-policy/15A-PRECONDITION.md"
    - ".planning/phases/15A-director-treatment-policy/15A-DECISIONS.md"
  key_links:
    - "The mock hosted CLI and the mock local HTTP server must both call one shared candidate_for(request) function in fixtures/mock_backends.py. If each fixture builds its own candidate, the AGENT-02 parity assertion in plan 15A-06 proves that two fixtures agree with each other rather than that two transports carry one contract, which is a green test measuring nothing."
    - "The rights check runs at the write call, reading the live registry through identity.rights_granted. A rights value observed while drafting the recommendation is display context only. If any code path reads the recommendation's own rights field to decide whether the bind may proceed, a revoked right stays effective forever, which is Pitfall 2 in 15A-RESEARCH.md and Pitfall 5 in 14B-RESEARCH.md."
    - "journal.ENTRY_KEYS gains exactly one member, agent, whose value is a dict. This mirrors the undo key's precedent (a dict value with a documented key set) and keeps RELIABILITY-02's field list inside the one journal entry shape rather than fanning out into nine new top-level keys that every existing reader would have to learn."
---

<objective>
Land the thinnest real path through this whole phase, end to end, before any
layer is widened: one synthetic objective, whose treatment is proposed by a
model across the shipped adapter boundary, validated, rights-checked live, and
bound into the course sidecar with the operation, its checkpoint, and its
egress recorded on one journal entry. `director.py` is created here in its
thinnest production-quality form, not as a prototype: the code written in this
plan stays and is expanded by plans 02 through 05.

This plan also does the three things that must happen before any 15A code
exists. First, it verifies that Phases 14A and 14B actually landed on disk with
the surface 15A was planned against, and halts by name if they did not
(`15A-RESEARCH.md` "Critical caveat: Phase 15A's entire dependency chain is
unexecuted": `identity.py`, `journal.py`, `discovery.py`, `graph.py`,
`course.py`, and `course_package.py` all read MISSING at the repository root
when this phase was researched and planned). Second and third, it settles the
two one-way design doors this phase cannot silently adopt.

Decisions already made, cited, and never re-derived here:

- **PLANNING-DIRECTIVES section 4**, all five non-negotiables, in particular
  number 2 (exactly one parser, one scorer, one evidence store, extended
  structurally to one rights vocabulary and one operation journal), number 3
  (evidence and banks stay on disk, no telemetry) and number 4 (format changes
  are additive, proven by a byte-identical fixture and not by promise).
- **PLANNING-DIRECTIVES section 4a**, the citation-discipline rule: this plan
  quotes the sentence behind every constraint it invokes.
- **REQUIREMENTS.md TREAT-01**: the eleven treatment kinds are a closed
  vocabulary, direct reading is a complete result, and generation is never the
  automatic default. The vocabulary itself is `graph.TREATMENT_KINDS`, already
  locked by plan 14B-03; this phase adds no twelfth member.
- **REQUIREMENTS.md AGENT-02**: hosted and registered local backends reach the
  same operations and schemas. The mechanism is `model_adapter.py`'s shipped
  `TRANSPORT_REGISTRY` plus `settings.model_backend.profiles`; a third backend
  is a registry entry, not a code fork (D-27, quoted verbatim in
  `schemas/settings.schema.json`'s transport description).
- **REQUIREMENTS.md RELIABILITY-02**: one durable local operation journal. The
  journal is `journal.py`, frozen (pending execution) by plan 14A-02. 15A adds
  one record type and one entry key to it and creates no second log.
- **15A-RESEARCH.md Summary and Architectural Responsibility Map**: the
  recommendation path is a rights gate, never the tier gate.

Decisions this plan makes and locks, so the executor never guesses (the
`PLANNING-DIRECTIVES.md` section 5 bar):

| Open question | Locked answer | One-line rationale |
|---|---|---|
| Module name and tier | One new root-level module `director.py`, an agent-client-tier peer of `model_adapter.py`, calling down into `course.py` and never being imported by it | `15A-RESEARCH.md` Assumption A3: a recommender that calls `model_adapter.invoke()` (which itself imports `surfaces.settings`) sits more naturally as a peer that calls into `course.py` than inside it, and `course.py` already carries a structural ban on importing `evidence` that a recommender must not weaken. |
| Which gate validates a candidate | A new narrow pass in `director.py`: JSON Schema validation against `schemas/treatment_recommendation.schema.json`, then a live rights check through `identity.rights_granted` | `15A-RESEARCH.md` Anti-Patterns: `tier_gate.py`'s five-step no-leak algorithm exists to stop a model over-disclosing to a learner mid-sitting; a course-builder recommendation has no learner tier to gate and instead needs a rights gate. |
| Where RELIABILITY-02's field list lives | Exactly one new `journal.ENTRY_KEYS` member named `agent`, holding a dict whose key set is `director.AGENT_ENTRY_KEYS` | `15A-RESEARCH.md` Pitfall 3: RELIABILITY-02 is a requirement on what the journal must be able to express, not a mandate for a second journal. One dict-valued key mirrors the existing `undo` key exactly and keeps `journal.py`'s whole-phase diff at two lines. |
| Mock backend construction | One fixture file, `fixtures/mock_backends.py`, exposing `candidate_for(request)` plus a `--cli` stdin/stdout mode and a `serve()` HTTP mode that both call it | `15A-RESEARCH.md` Pitfall 4: two independently written mocks would let plan 15A-06's parity assertion pass by coincidence. One shared builder makes parity a property of the transports. |
| Provider result trust | The provider candidate is untrusted input. It is schema-validated before any field is read, and a candidate naming a treatment kind outside `graph.TREATMENT_KINDS` is refused before any write | The shipped `model_adapter.schema.json` describes the candidate as `type: object` with no inner shape, and says in plain words that provider output "remains untrusted and is validated by the authoring pipeline, never accepted by the adapter". 15A is that pipeline for this operation. |

Purpose: prove the architecture end to end on one path before four more layers
are built on it.
Output: `director.py`, the two schema changes, the two-line journal change, the
shared mock backend fixture, the first roundtrip test, and the two recorded
decision artifacts.
</objective>

<context>
@.planning/phases/15A-director-treatment-policy/15A-RESEARCH.md
@.planning/phases/15A-director-treatment-policy/15A-PATTERNS.md
@.planning/PLANNING-DIRECTIVES.md
@.planning/PLAN-TEMPLATE.md
@.planning/phases/14A-identity-lifecycle-operation/14A-01-PLAN.md
@.planning/phases/14A-identity-lifecycle-operation/14A-02-PLAN.md
@.planning/phases/14A-identity-lifecycle-operation/14A-03-PLAN.md
@.planning/phases/14B-graph-course-package-prototype/14B-01-PLAN.md
@.planning/phases/14B-graph-course-package-prototype/14B-03-PLAN.md
@.agents/skills/OPERATION-CONTRACT.md
@model_adapter.py
@schemas/model_adapter.schema.json
</context>

## Artifacts this phase produces (plan 15A-01 share)

New modules and the public symbols this plan creates. Every symbol below is new
in this phase and exists in no shipped file.

- `director.py`
  - Constants: `DIRECTOR_SCHEMA_VERSION = 1`,
    `RECOMMENDATION_OPERATION = "treatment_recommend"`,
    `RECOMMENDATION_SCHEMA_RESOURCE = "schemas/treatment_recommendation.schema.json"`,
    `AGENT_RECORD_TYPE = "agent_operation"`,
    `AGENT_ENTRY_KEYS` (the fixed-order ten-key tuple defined in Task 4),
    `EGRESS_DESTINATIONS = ("local", "hosted", "registered-local")`,
    `EGRESS_KEYS` (the fixed-order seven-key tuple defined in Task 4),
    `RECOMMENDATION_KEYS` (the fixed-order nine-key tuple defined in Task 4),
    `DIRECTOR_CODES` (a set-then-sorted tuple, the `ADAPTER_CODES`
    construction precedent).
  - Exception: `DirectorError(Exception)` with `.code` and `.message`.
  - Functions created here: `new_operation_id()`, `begin_operation(...)`,
    `recommendation_request(...)`, `validate_recommendation(candidate)`,
    `record_phase(...)`, `apply_recommendation(...)`.
- `schemas/treatment_recommendation.schema.json`, `x-itembank-version` `1`.
- `fixtures/mock_backends.py`
  - `candidate_for(request)`, `main_cli()`, `serve(host, port)`, and a
    `__main__` block dispatching on `--cli` and `--refuse`.
- `tests/director_roundtrip.py`, a direct-execution script, exit 0 on pass,
  whose first function is `check_thin_slice()`.
- `.planning/phases/15A-director-treatment-policy/15A-PRECONDITION.md` and
  `15A-DECISIONS.md`.

Modified shipped files and the exact symbols added:

- `model_adapter.py`: `_PAYLOAD_KEYS` gains the member
  `"recommendation_request"`; `_invoke` gains one runtime required-payload
  check for the new operation. No other change.
- `schemas/model_adapter.schema.json`: the `operation` enum gains the member
  `"treatment_recommend"`; `$defs.payload.properties` gains
  `recommendation_request`. No restructuring of `oneOf`, `$defs.request`, or
  `$defs.result`.
- `journal.py`: `RECORD_TYPES` gains the member `"agent_operation"`;
  `ENTRY_KEYS` gains the member `"agent"`, appended last. `OPERATION_TYPES`
  stays at exactly six.

New refusal codes introduced by this plan: `director.recommendation_invalid`,
`director.unknown_treatment_kind`, `director.rights_not_granted`,
`director.backend_unavailable`, `director.evidence_forbidden`.

New journal record types introduced by this plan: exactly one,
`agent_operation`.

No CLI command and no daemon route is produced by this plan.

<tasks>

<task type="auto">
  <name>Task 1: verify Phases 14A and 14B landed, or halt by name</name>
  <files>.planning/phases/15A-director-treatment-policy/15A-PRECONDITION.md</files>
  <read_first>
- `.planning/phases/15A-director-treatment-policy/15A-RESEARCH.md`, the section
  "Critical caveat: Phase 15A's entire dependency chain is unexecuted" and the
  Assumptions Log, in full. This task exists because of them.
- `.planning/phases/14A-identity-lifecycle-operation/14A-01-PLAN.md`, the
  "Artifacts this phase produces" section, for the `identity.py` constant list.
- `.planning/phases/14A-identity-lifecycle-operation/14A-02-PLAN.md`, the
  "Artifacts this phase produces" section, for `journal.ENTRY_KEYS` and
  `journal.RECORD_TYPES`.
- `.planning/phases/14A-identity-lifecycle-operation/14A-03-PLAN.md`, the
  "Artifacts this phase produces" section, for `identity.RIGHTS_STATES`,
  `identity.rights_state`, `identity.rights_granted`, and
  `journal.read_registry`.
- `.planning/phases/14B-graph-course-package-prototype/14B-01-PLAN.md` Task 1,
  the shipped precedent this task copies in shape.
- `.planning/phases/14B-graph-course-package-prototype/14B-03-PLAN.md`, the
  behavior block lines naming `graph.TREATMENT_KINDS`, `graph.BINDING_STATES`,
  `graph.TREATMENT_RIGHTS`, `course.bind_source`, and `course.bind_treatment`.
- `.planning/phases/14B-graph-course-package-prototype/14B-DECISIONS.md`, the
  dated section `## D-14B-1. Sidecar path and the Phase 13.9 supersession`. The
  option recorded there decides which filename step 3 below asserts. Read the
  recorded option and use it; do not assume one.
  </read_first>
  <action>
1. Check that the five dependency modules import. Run:

```
python -c "import identity, journal, discovery, graph, course, course_package; print('modules present')"
```

   Expected stdout: `modules present`, exit code 0.

2. Check that the frozen 14A constants match what Phase 15A was planned
   against. Run a single `python -c` that asserts, in this order, every one of
   the following, printing `14A surface matches` on success:
   - `identity.OBJECT_KINDS` equals `("course", "objective", "source",
     "lesson", "bank", "component")`.
   - `identity.RIGHTS_OPERATIONS` equals `("read", "quote", "transform",
     "remote_process", "package", "export", "share")`.
   - `identity.RIGHTS_STATES` equals `("granted", "denied", "unknown")`.
   - `identity.rights_state(None, "transform")` returns `"unknown"`, and
     `identity.rights_granted({"transform": "GRANTED"}, "transform")` returns
     `False`. Exact ASCII match only, no case folding.
   - `journal.OPERATION_TYPES` has exactly six members.
   - `"reconcile"` and `"migrate"` are both in `journal.RECORD_TYPES`, and
     `"agent_operation"` is not yet.
   - `len(journal.ENTRY_KEYS)` equals `22`, and `"agent"` is not in
     `journal.ENTRY_KEYS`.
   - Every one of these names is callable on its module:
     `identity.new_object_id`, `identity.object_fingerprint`,
     `identity.rights_state`, `identity.rights_granted`,
     `journal.commit_operation`, `journal.entries`, `journal.read_registry`,
     `journal.undo`, `journal.object_state`.

3. Check that the frozen 14B constants match. Run a single `python -c` that
   asserts, in this order, every one of the following, printing
   `14B surface matches` on success:
   - `graph.TREATMENT_KINDS` equals, in this exact order,
     `("direct-reading", "excerpt", "guided-lesson", "notes-or-terms",
     "worked-example", "visual-or-demonstration", "practice", "formal-test",
     "assessment-first-diagnostic", "learner-artifact", "human-review")` and
     has exactly eleven members.
   - `graph.BINDING_STATES` equals `("covered", "thin", "missing",
     "conflicting", "unknown")`.
   - `len(graph.TREATMENT_RIGHTS)` equals `11`, and every value in it is a
     member of `identity.RIGHTS_OPERATIONS`.
   - `graph.EDGE_CONFIDENCES` equals `("high", "medium", "low", "unknown")`.
   - `graph.EDGE_TYPES` equals `("prerequisite-of", "covers-objective",
     "source-supports", "treatment-of")`.
   - `graph.COURSE_GRAPH_VERSION` equals `1`.
   - `course.COURSE_SIDECAR_FILENAME` equals the filename the recorded
     `D-14B-1` option implies: `"course-graph.md"` under option-a,
     `"course.md"` under option-b. Under option-c, record the value found and
     treat a mismatch with option-a as a deviation rather than a halt.
   - Every one of these names is callable on its module:
     `graph.add_binding`, `graph.add_source`, `graph.treatment_right`,
     `graph.parse_course`, `graph.serialize_course`, `course.read_course`,
     `course.write_course`, `course.bind_source`, `course.bind_treatment`,
     `course.rights_for_binding`.

4. Check that the shipped Phase 8 surface this phase extends is still where
   this plan expects it. Run:

```
python -c "import model_adapter; print(len(model_adapter.ADAPTER_CODES), sorted(model_adapter.TRANSPORT_REGISTRY))"
```

   Expected stdout exactly: `14 ['hosted_cli', 'openai_compatible']`.

5. Check that both freeze records exist:
   `.planning/phases/14A-identity-lifecycle-operation/14A-FREEZE.md` contains
   the literal heading `## Frozen at 14A`, and
   `.planning/phases/14B-graph-course-package-prototype/14B-FREEZE.md`
   contains the literal heading `## Frozen at 14B`.

6. If any check in steps 1 through 5 fails, STOP. Write nothing else, create no
   module, and print exactly this line with the failing item substituted for
   `<item>`, then exit non-zero:

   `HALT 15A-01 precondition: Phase 14A or Phase 14B has not landed, or its frozen surface differs from what Phase 15A was planned against. Re-verify every 15A plan against .planning/phases/14A-identity-lifecycle-operation/14A-FREEZE.md and .planning/phases/14B-graph-course-package-prototype/14B-FREEZE.md before writing any code. Divergent or missing: <item>`

   Do not work around a failure by stubbing the missing module, by wrapping the
   import in a try or except, or by continuing with a reduced check set. A halt
   here is the correct outcome; it is what this task is for.

7. On success, create
   `.planning/phases/15A-director-treatment-policy/15A-PRECONDITION.md` with
   exactly these four sections and nothing more:
   - **Why this check exists.** One paragraph citing `15A-RESEARCH.md`'s
     Critical Caveat: every 14A and 14B signature in the 15A research and
     pattern map was read from plan text, not from source, because the modules
     did not exist when 15A was planned.
   - **What was checked.** The full list from steps 1 through 5, one line each,
     each marked `ok` or `divergent`.
   - **Deviations found.** Every place the landed 14A or 14B surface differs
     from the plan text, with the plan-text value and the landed value side by
     side. Write `none` when there are none. A deviation here is not a failure
     of this task; it is the signal that plans 02 through 06 must be re-read
     against the two freeze records before execution, and this section is where
     a later plan looks for it.
   - **Dated result line.** The date, the command output of steps 2, 3 and 4
     verbatim, and one sentence stating whether 15A may proceed.

   No em dash characters anywhere in the file.
  </action>
  <verify>
  <automated>python -c "import identity, journal, graph, course; assert len(graph.TREATMENT_KINDS)==11 and len(graph.BINDING_STATES)==5 and len(journal.ENTRY_KEYS)==22 and 'agent_operation' not in journal.RECORD_TYPES; print('15A preconditions match')"</automated>
Expected: prints `15A preconditions match` and exits 0. The degraded state this
task must prove rather than paper over is the halt itself: if any assertion
fails, the run exits non-zero with the named HALT line and no module file is
created. Confirm this by checking that `director.py` does not exist on disk at
the end of a failed run.
  </verify>
  <acceptance_criteria>
- The step 1 command prints `modules present` and exits 0.
- The step 2 command prints `14A surface matches` and exits 0.
- The step 3 command prints `14B surface matches` and exits 0.
- The step 4 command prints exactly `14 ['hosted_cli', 'openai_compatible']`.
- Both freeze files exist and contain their respective `## Frozen at 14A` and
  `## Frozen at 14B` headings.
- `.planning/phases/15A-director-treatment-policy/15A-PRECONDITION.md` exists
  with all four named sections.
- `15A-PRECONDITION.md` contains no em dash character.
  </acceptance_criteria>
  <precondition>Phases 14A and 14B have executed and `identity.py`, `journal.py`, `discovery.py`, `graph.py`, `course.py`, and `course_package.py` exist at the repository root with the surfaces frozen in `14A-FREEZE.md` and `14B-FREEZE.md`.</precondition>
  <done>Either 15A is cleared to proceed with the evidence recorded, or the
  wave is halted with the divergence named.</done>
</task>

<task type="checkpoint:decision" gate="blocking">
  <name>Task 2: the wire boundary a treatment recommendation crosses</name>
  <files>.planning/phases/15A-director-treatment-policy/15A-DECISIONS.md</files>
  <read_first>
- `15A-RESEARCH.md`, the "Summary" section and Assumption A1, in full. A1 is
  the reason this is a checkpoint rather than a silent adoption.
- `schemas/model_adapter.schema.json` lines 26 to 29, the exact three-member
  `operation` enum this decision either extends or leaves alone.
- `model_adapter.py` lines 34 to 96, `ADAPTER_CODES`, `_PAYLOAD_KEYS`,
  `unavailable_result`, and `request_from_operation`.
- `tier_gate.py` lines 1 to 60, so the option list is understood against what
  the tier gate actually does rather than against its name.
- `.planning/phases/15A-director-treatment-policy/15A-DECISIONS.md` if it
  already exists, so the new section is appended rather than overwriting one.
  </read_first>
  <decision>
Does a treatment recommendation cross the shipped `model_adapter.invoke()`
boundary as a fourth member of its closed `operation` enum, or does it travel a
separate path that never enters the learner-facing adapter?
  </decision>
  <context>
`model_adapter.py` is the shipped, executed typed boundary that normalizes any
number of provider transports behind `TRANSPORT_REGISTRY`, so switching
providers is a settings change and never a caller change. Its three existing
operations, `hint`, `rubric_review`, and `author`, are all learner-facing or
item-scoped. A treatment recommendation is course-scoped and has no learner
tier to gate against.

This is rated one-way. `schemas/model_adapter.schema.json` is a published
contract that plans 02 through 06, Phase 15B, and every later agent client read
against. Undoing the choice after a recommendation has been journaled means a
schema migration plus a rewrite of every recorded operation. It also decides
whether AGENT-02's backend-parity guarantee is inherited from shipped, tested
machinery or has to be rebuilt and re-proved.
  </context>
  <options>
    <option id="option-a">
      <name>RECOMMENDED DEFAULT: a fourth adapter operation, treatment_recommend</name>
      <pros>AGENT-02's "same operations and schemas across backends" is
      inherited from `TRANSPORT_REGISTRY`, profile resolution, the typed
      unavailable envelope, and the secret-resolution discipline, all shipped
      and tested since Phase 8. The change is additive: one enum member and one
      bounded payload key. No second dispatcher exists to drift. The
      `treatment_recommend` result is deliberately NOT routed through
      `tier_gate.py`; `director.py` validates it against its own schema and a
      live rights check instead.</pros>
      <cons>The adapter's operation enum now mixes a learner-facing family with
      a course-builder operation, so a future reader must know that only three
      of the four go near the tier gate. That distinction has to be written
      into the schema description and into `director.py`'s docstring rather
      than being obvious from the enum.</cons>
    </option>
    <option id="option-b">
      <name>A separate course-scope transport owned by director.py</name>
      <pros>The learner-facing adapter stays exactly as shipped, and the
      enum keeps one meaning.</pros>
      <cons>Duplicates `TRANSPORT_REGISTRY`, profile resolution, timeout and
      output caps, the typed unavailable envelope, and secret resolution. Two
      transport layers means AGENT-02's parity guarantee has to be re-proved
      for the second one and can silently drift from the first. This is the one
      outcome `15A-RESEARCH.md`'s "Don't Hand-Roll" table forbids by name.</cons>
    </option>
    <option id="option-c">
      <name>No model in the loop for 15A: journal-only, human-authored recommendations</name>
      <pros>Smallest surface. No schema change at all.</pros>
      <cons>AGENT-02's fixture requires the same operation to run through a
      mock hosted and a mock local backend with identical artifacts and
      journals. With no adapter path there is no backend to run through, so the
      phase cannot meet its own stated freeze gate.</cons>
    </option>
  </options>
  <action>
Ask Weibao the question above, present all three options with the recommended
default named, and record the answer verbatim in
`.planning/phases/15A-director-treatment-policy/15A-DECISIONS.md` under a dated
heading `## D-15A-1. The recommendation wire boundary`.

What the executor does with each answer:

- **option-a**: proceed as every task in plans 01 through 06 is already
  written. No plan edit is needed.
- **option-b**: before Task 4, record in `15A-DECISIONS.md` that
  `schemas/model_adapter.schema.json` and `model_adapter.py` leave this plan's
  `files_modified` list, that `director.py` gains its own
  `DIRECTOR_TRANSPORT_REGISTRY` with the same two transport names and the same
  typed unavailable envelope, and that plan 15A-06's parity scenario must
  additionally assert the two registries carry the same transport names. Then
  build the separate path.
- **option-c**: before Task 4, record in `15A-DECISIONS.md` that AGENT-02's
  Fixture sentence cannot be met by Phase 15A, that the requirement is deferred
  with the deferral reason and the phase that will own it, and that plan
  15A-06's freeze record must open with a `Freeze withheld` section naming
  AGENT-02. Then stop and hand the plan set back for replanning.

Do not proceed with a silent default. An unanswered checkpoint stops the wave.
  </action>
  <verify>
`15A-DECISIONS.md` exists and carries a dated `## D-15A-1` heading with the
chosen option id and Weibao's answer recorded verbatim.
  </verify>
  <acceptance_criteria>
- `.planning/phases/15A-director-treatment-policy/15A-DECISIONS.md` contains
  the literal heading `## D-15A-1. The recommendation wire boundary`.
- The recorded answer names exactly one of `option-a`, `option-b`, `option-c`.
- The file contains no em dash character.
  </acceptance_criteria>
  <reversibility rating="one-way">`schemas/model_adapter.schema.json` is a
  published contract. Plans 02 through 06, Phase 15B, and any external agent
  client build against the enum. Undoing the choice after a recommendation has
  been journaled means migrating recorded operations, not editing one
  line.</reversibility>
  <resume-signal>Reply with `option-a`, `option-b`, or `option-c`.</resume-signal>
</task>

<task type="checkpoint:decision" gate="blocking">
  <name>Task 3: where the egress record lives</name>
  <files>.planning/phases/15A-director-treatment-policy/15A-DECISIONS.md</files>
  <read_first>
- `15A-RESEARCH.md`, the "Alternatives Considered" table row on egress
  recording, and Assumption A2, in full.
- `REQUIREMENTS.md`, the RIGHTS-02 entry in full, including its Fixture
  sentence, and the RELIABILITY-02 entry in full.
- `.planning/phases/14A-identity-lifecycle-operation/14A-02-PLAN.md`, the
  "Artifacts this phase produces" section, for the twenty-two-member
  `journal.ENTRY_KEYS` tuple and the `undo` key's dict-valued precedent.
- `.planning/phases/15A-director-treatment-policy/15A-DECISIONS.md`, so the new
  section is appended below `## D-15A-1`.
  </read_first>
  <decision>
Is the record of exactly what left this machine, and to whom, a set of fields
on the existing journal entry, or a sibling append-only file beside the
journal?
  </decision>
  <context>
RIGHTS-02 requires that hosted operations minimize and disclose exact egress,
and names "operation manifest plus egress log" as its durable object.
RELIABILITY-02 requires one durable local operation journal, singular, and
names the journal as the durable job record rather than a chat transcript.
Nothing in the shipped or planned code owns egress disclosure today; this is
the phase's one genuinely new durable object.

This is rated one-way. Whichever shape is chosen becomes the shape every
recorded operation carries from this point on, and it is append-only by
construction, so a later change is a migration of existing records rather than
an edit. It also decides whether an auditor answering "what happened in this
operation" reads one file or joins two.
  </context>
  <options>
    <option id="option-a">
      <name>RECOMMENDED DEFAULT: one new dict-valued journal entry key</name>
      <pros>`journal.ENTRY_KEYS` gains exactly one member, `agent`, whose value
      is a dict carrying `director.AGENT_ENTRY_KEYS`, one of which is `egress`.
      One file answers "what happened in this operation" completely, which is
      exactly the auditability RELIABILITY-02 asks for. It mirrors the existing
      `undo` key's precedent (a dict value with a documented key set) rather
      than inventing a new pattern. `journal.py`'s whole-phase diff stays at
      two lines, which `15A-RESEARCH.md` names as the drift signal to
      watch.</pros>
      <cons>The journal entry grows a nested structure, so a reader that wants
      only egress has to reach one level in. Egress and object mutation are
      genuinely different concerns sharing one record.</cons>
    </option>
    <option id="option-b">
      <name>A sibling append-only egress log beside the journal</name>
      <pros>Egress is a separate concern and gets a separate, flat, easily
      audited file. A privacy review reads one file with nothing else in
      it.</pros>
      <cons>Two append-only operation records now exist in `_journal/`. Even if
      that does not break RELIABILITY-02's literal member count, it splits the
      answer to "what happened in this operation" across two files with no
      transactional relationship, so a crash between the two writes leaves them
      disagreeing and neither is authoritative.</cons>
    </option>
    <option id="option-c">
      <name>Both: the field is authoritative, the sibling file is a derived view</name>
      <pros>One source of truth plus the flat audit file a privacy review
      wants.</pros>
      <cons>A derived view that a reader mistakes for the record is exactly the
      failure the project's own rule against derived views becoming the only
      understandable copy is written to prevent. Costs a rebuild command and a
      staleness rule this phase would otherwise not need.</cons>
    </option>
  </options>
  <action>
Ask Weibao the question above, present all three options with the recommended
default named, and record the answer verbatim in
`.planning/phases/15A-director-treatment-policy/15A-DECISIONS.md` under a dated
heading `## D-15A-2. Where the egress record lives`.

What the executor does with each answer:

- **option-a**: proceed as every task in plans 01 through 06 is already
  written. No plan edit is needed.
- **option-b**: before Task 4, record in `15A-DECISIONS.md` that
  `director.AGENT_ENTRY_KEYS` drops its `egress` member, that `director.py`
  gains `EGRESS_LOG_FILENAME = "egress.jsonl"` written under
  `journal.journal_dir(base)` through the same atomic tmp-then-replace idiom
  `journal.append_entry` uses, that each egress line carries the owning
  `entry_id` so the join is possible, and that plan 15A-04's tests assert the
  crash-between-writes case leaves the journal entry present and the egress
  line absent rather than the reverse.
- **option-c**: before Task 4, record in `15A-DECISIONS.md` that the field is
  authoritative, that the sibling file is rebuilt by a new
  `director.rebuild_egress_view(base)` and is deletable at any time, and that
  plan 15A-04's tests assert deleting the sibling file and rebuilding it
  reproduces it byte-identically, the same disposability discipline the
  evidence index already carries.

Do not proceed with a silent default. An unanswered checkpoint stops the wave.
  </action>
  <verify>
`15A-DECISIONS.md` carries a dated `## D-15A-2` heading with the chosen option
id and Weibao's answer recorded verbatim.
  </verify>
  <acceptance_criteria>
- `.planning/phases/15A-director-treatment-policy/15A-DECISIONS.md` contains
  the literal heading `## D-15A-2. Where the egress record lives`.
- The recorded answer names exactly one of `option-a`, `option-b`, `option-c`.
- The file contains no em dash character.
  </acceptance_criteria>
  <reversibility rating="one-way">The record is append-only by construction.
  Every operation recorded from this point carries the chosen shape, so a later
  change is a migration of existing records rather than an edit.</reversibility>
  <resume-signal>Reply with `option-a`, `option-b`, or `option-c`.</resume-signal>
</task>

<task type="tracer" tdd="true">
  <name>Task 4: one objective from intent to accepted binding, end to end, one path only</name>
  <files>director.py, model_adapter.py, schemas/model_adapter.schema.json, schemas/treatment_recommendation.schema.json, journal.py, fixtures/mock_backends.py, tests/director_roundtrip.py</files>
  <read_first>
- `model_adapter.py` in full: `ADAPTER_CODES`, `_PAYLOAD_KEYS`,
  `unavailable_result`, `request_from_operation`, `resolve_profile`,
  `_transport_hosted_cli`, `_transport_openai_compatible`,
  `TRANSPORT_REGISTRY`, `_invoke`, and `invoke`. The `rubric_review` required
  payload check inside `_invoke` is the exact shape the new check copies.
- `schemas/model_adapter.schema.json` in full, especially `$defs.payload` and
  the `author_request` property, which is the precedent for adding one bounded
  object-valued payload key with its own inner shape.
- `schema_validate.py` lines 1 to 70, the `SUPPORTED` and `ANNOTATIONS`
  keyword ceiling. The new schema uses only keywords already present in
  `schemas/model_adapter.schema.json`.
- `identity.py` as landed: `rights_state`, `rights_granted`, `RIGHTS_STATES`,
  `new_object_id`.
- `journal.py` as landed: `ENTRY_KEYS`, `RECORD_TYPES`, `commit_operation`,
  `append_entry`, `entries`, `read_registry`, and `JournalError`.
- `graph.py` as landed: `TREATMENT_KINDS`, `TREATMENT_RIGHTS`,
  `BINDING_STATES`, `EDGE_CONFIDENCES`, `treatment_right`, `add_binding`.
- `course.py` as landed: `read_course`, `write_course`, `bind_treatment`,
  `rights_for_binding`, and `CourseError`.
- `fixtures/corpus_14b.py` as landed: `build_three_domains`, `build_all`, and
  `revoke_right`. This plan reuses that corpus and adds no fourth domain; the
  fourth domain is plan 15A-06's.
- `tests/evidence_roundtrip.py` lines 1 to 40, for the local `fail(msg)`
  helper and the `ROOT` plus `sys.path.insert` header convention every existing
  roundtrip test uses. Each test file defines its own helper; there is no
  shared test module.
- `evidence.py` lines 1 to 19, the peer-module docstring contract this project
  restates in every new root module.
  </read_first>
  <behavior>
Assertions `check_thin_slice()` in `tests/director_roundtrip.py` must make,
written before any module exists. Run the test first and confirm it fails.

The adapter extension is additive and breaks nothing:

- `schemas/model_adapter.schema.json`'s `operation` enum equals, in this exact
  order, `["hint", "rubric_review", "author", "treatment_recommend"]`.
- `model_adapter._PAYLOAD_KEYS` contains `"recommendation_request"` and still
  contains all six of its prior members in their prior order.
- A request built with `operation="hint"` and the payload keys
  `item_context`, `learner_response`, `permitted_tier`, and `fact_manifest`
  serializes to exactly the same JSON string it did before this plan, proven by
  a golden string recorded in the test.
- `model_adapter.invoke` with `operation="treatment_recommend"` and no
  `payload.recommendation_request` returns status `unavailable` with error code
  `adapter.request_invalid` and the message
  `treatment_recommend requires payload.recommendation_request`.
- `schema_validate.check_schema(json.loads(open("schemas/treatment_recommendation.schema.json").read()))`
  raises nothing.

The journal extension is exactly two lines:

- `"agent_operation"` is in `journal.RECORD_TYPES`.
- `journal.ENTRY_KEYS` has exactly `23` members, its last member is `"agent"`,
  and its first twenty-two members are unchanged in value and order.
- `len(journal.OPERATION_TYPES)` is still `6`.
- `director.AGENT_ENTRY_KEYS` equals, in this exact order, `("operation_id",
  "intent", "actor_role", "autonomy", "scopes", "phase", "phase_index",
  "checkpoint", "proposal", "egress")`.

The mock backend is one shared candidate builder:

- `fixtures.mock_backends.candidate_for(request)` returns a dict whose
  `treatment_kind` is a member of `graph.TREATMENT_KINDS`.
- Running `python fixtures/mock_backends.py --cli` with the request JSON on
  stdin prints a JSON object equal to `candidate_for(request)` and exits 0.
- Posting the same request JSON to the server returned by
  `fixtures.mock_backends.serve("127.0.0.1", 0)` returns a JSON body equal to
  `candidate_for(request)`.
- Running `python fixtures/mock_backends.py --refuse` exits non-zero, and
  `model_adapter.invoke` against a profile whose command carries `--refuse`
  returns status `unavailable` with code `adapter.provider_refused`.

The one end-to-end path:

- `director.new_operation_id()` returns a string of at least eight characters,
  and two calls never return the same value.
- `director.begin_operation(base, course_root, intent, actor_kind, actor_name,
  actor_role, autonomy)` appends exactly one journal entry whose `operation` is
  `"agent_operation"`, whose `state` is `"applied"`, and whose `agent` dict has
  exactly the key set `set(director.AGENT_ENTRY_KEYS)` with `phase` equal to
  `"declare-intent"` and `phase_index` equal to `0`.
- `director.recommendation_request(doc, objective_id, spans, profile,
  interaction_id)` returns a dict that validates against
  `schemas/model_adapter.schema.json` and whose
  `payload.recommendation_request.treatment_kinds` equals
  `list(graph.TREATMENT_KINDS)` and whose
  `payload.recommendation_request.binding_states` equals
  `list(graph.BINDING_STATES)`.
- `director.validate_recommendation` on the mock candidate returns a normalized
  record whose key set equals `set(director.RECOMMENDATION_KEYS)`.
- `director.validate_recommendation` on a candidate whose `treatment_kind` is
  `"flashcards"` raises `DirectorError` with code
  `director.unknown_treatment_kind`, and the message contains the word
  `eleven`.
- `director.validate_recommendation` on a candidate missing its `citations` key
  raises `DirectorError` with code `director.recommendation_invalid`, and the
  message names the missing key.
- `director.apply_recommendation` against a source whose `transform` right is
  `granted` calls `course.bind_treatment`, and afterwards
  `course.read_course(course_root)["doc"]["bindings"]` has exactly one more row
  than before, whose `binding_kind` is `treatment` and whose `treatment_kind`
  is the candidate's.
- `director.apply_recommendation` against a source whose required right is
  `unknown` raises `DirectorError` with code `director.rights_not_granted`,
  the message names the right and the state, the sidecar bytes on disk are
  unchanged, and the journal gains exactly one entry whose `agent.phase` is
  `"review"` and whose `state` is `"refused"`. A refused recommendation writes
  no binding but is still recorded.
- The rights check is live: after a successful bind, revoke the right with
  `fixtures.corpus_14b.revoke_right`, then call `apply_recommendation` again
  for a second objective with a recommendation record whose own rights field
  still reads `granted`. It refuses with `director.rights_not_granted` naming
  `denied`. The record's own field never authorizes.
- After the whole path runs once, exactly one journal entry carries a non-null
  `agent.egress` dict whose key set equals `set(director.EGRESS_KEYS)`, whose
  `destination` is `"hosted"`, and whose `spans` is a non-empty list.

Degraded behavior this task must prove, not paper over:

- With the profile's command pointed at a path that does not exist,
  `director.recommend_once` returns a result whose `status` is `"unavailable"`
  and whose `code` is `adapter.executable_missing`; no binding is written; the
  journal records the operation with `agent.phase` equal to `"plan-treatment"`
  and `state` equal to `"refused"`; and `course.read_course` still reads the
  sidecar unchanged.
- The objective left untreated by that unavailable run is still untreated: no
  row with its objective id and `binding_kind` `treatment` exists.

Tier and boundary assertions, structural rather than maintained by care:

- `hasattr(director, "tier_gate")` is `False`.
- `hasattr(director, "evidence")` is `False`.
- `hasattr(director, "runtime")` is `False`.
- `hasattr(director, "model")` is `False`.
- `director.py` reaches `course.bind_treatment` for every durable write: after
  the whole path runs, `len(journal.entries(base))` is greater than it was
  before, and no file under the course root was written by `open(..., "w")`
  from `director.py`, proven behaviorally by the sidecar's revision number
  advancing by exactly one per successful bind.
  </behavior>
  <action>
1. Create `tests/director_roundtrip.py` first, with the local `fail(msg)`
   helper that prints `"FAIL: " + msg` and calls `sys.exit(1)`, the `ROOT` and
   `sys.path.insert` header convention every existing roundtrip test uses, a
   `check_thin_slice()` function holding every assertion in `<behavior>`, and a
   `main()` that calls it and prints `OK director_roundtrip`. Run it with
   `python tests/director_roundtrip.py` and confirm it fails because
   `director.py` does not exist yet.

2. Edit `schemas/model_adapter.schema.json`. Add `"treatment_recommend"` as the
   fourth member of the `operation` enum, keeping the existing three in their
   existing order, and extend that property's description by appending exactly
   this sentence: `treatment_recommend carries a course-scope treatment and
   coverage proposal for one objective; it is the one operation that is never
   routed through the learner-facing tier gate, because it has no learner
   disclosure boundary and is gated on source rights instead.` Then add to
   `$defs.payload.properties` a `recommendation_request` property following the
   `author_request` precedent exactly: a `oneOf` of an object and null, the
   object carrying `additionalProperties: false`, `required` equal to
   `["schema_version", "course_object_id", "objective_id",
   "objective_statement", "treatment_kinds", "binding_states", "source_spans",
   "attempt"]`, and these properties: `schema_version` const 1;
   `course_object_id` a string with `minLength` 1; `objective_id` a string with
   `minLength` 1; `objective_statement` a string; `treatment_kinds` an array of
   strings; `binding_states` an array of strings; `source_spans` an array of
   objects; `attempt` an integer with `minimum` 1. Use no schema keyword that
   is not already present somewhere in this file.

3. Edit `model_adapter.py`. Add `"recommendation_request"` as the seventh
   member of `_PAYLOAD_KEYS`, appended last so the existing six keep their
   positions, and extend the comment above the tuple with one sentence naming
   it as the Phase 15A bounded course-scope payload. Then, immediately after
   the existing `rubric_review` required-payload check inside `_invoke`, add
   the same shape for the new operation: if `request.get("operation")` equals
   `"treatment_recommend"` and `(request.get("payload") or {})` has no truthy
   `recommendation_request`, return
   `unavailable_result("adapter.request_invalid", "treatment_recommend requires payload.recommendation_request", interaction_id)`.
   Change nothing else in this file.

4. Edit `journal.py`. Add exactly two members and nothing else: the string
   `"agent_operation"` to `RECORD_TYPES`, and the string `"agent"` appended as
   the last member of `ENTRY_KEYS`. Give each a one-line comment naming Phase
   15A and RELIABILITY-02 as its reason, and stating that `agent` holds a dict
   or null whose key set is owned by `director.AGENT_ENTRY_KEYS`, following the
   `undo` key's dict-valued precedent. Do not touch `OPERATION_TYPES`.

5. Create `schemas/treatment_recommendation.schema.json` with
   `"$schema": "https://json-schema.org/draft/2020-12/schema"`,
   `"$id": "https://itembank.local/schemas/treatment_recommendation.schema.json"`,
   `"x-itembank-version": 1`, `type: object`,
   `additionalProperties: false`, and `required` equal to
   `["schema_version", "objective_id", "treatment_kind", "rationale",
   "synthesis", "confidence", "coverage", "alternatives", "citations"]`. Its
   properties, exactly:
   - `schema_version`: const 1.
   - `objective_id`: string, `minLength` 1.
   - `treatment_kind`: string, `enum` equal to the eleven `TREATMENT_KINDS`
     tokens plus the empty string as a twelfth enum member. The empty string is
     how a provider says it has no recommendation; it is not a twelfth
     treatment kind, and the description says so in plain words.
   - `rationale`: string.
   - `synthesis`: const `true`. The description states that a rationale is
     always model synthesis and is never a source passage, and that this
     constant is what makes the label structural rather than a convention.
   - `confidence`: string, `enum` `["high", "medium", "low", "unknown"]`.
   - `coverage`: object, `additionalProperties: false`, `required`
     `["state", "locator", "confidence", "source_object_id", "match_kind"]`,
     with `state` an enum of the five `BINDING_STATES`, `locator` a string,
     `confidence` the same four-token enum, `source_object_id` a string, and
     `match_kind` an enum `["locator", "heading-similarity", "none"]`.
   - `alternatives`: array of objects, each `additionalProperties: false` with
     `required` `["treatment_kind", "confidence"]`.
   - `citations`: array of objects, each `additionalProperties: false` with
     `required` `["source_object_id", "locator"]`.

   The document's top-level `description` states in plain sentences that this
   is the contract a provider candidate is validated against before any field
   of it is read, that provider output is untrusted input, and that a candidate
   failing this schema is refused with `director.recommendation_invalid` and
   never partially applied. No em dash characters.

6. Create `fixtures/mock_backends.py`. It defines `candidate_for(request)`,
   which reads `request["payload"]["recommendation_request"]` and returns a
   dict valid against `schemas/treatment_recommendation.schema.json`, built by
   a fixed rule with no randomness and no clock read, so two calls with the
   same request return equal dicts. The fixed rule: `treatment_kind` is the
   member of `treatment_kinds` at index `len(objective_statement) % 11`;
   `confidence` is `"medium"`; `coverage.state` is `"covered"` when
   `source_spans` is non-empty and `"missing"` when it is empty;
   `coverage.match_kind` is `"locator"` when `source_spans` is non-empty and
   `"none"` when it is empty; `coverage.locator` and
   `coverage.source_object_id` come from the first span; `alternatives` holds
   the next two members of `treatment_kinds` cyclically, each with confidence
   `"low"`; `citations` holds one entry per span; `rationale` is the exact
   string `Recommended from the supplied source spans. This rationale is model
   synthesis, not a source passage.`; `synthesis` is `True`. It also defines
   `main_cli()` reading one JSON object from stdin and printing
   `json.dumps(candidate_for(request), ensure_ascii=False, sort_keys=True)`,
   and `serve(host="127.0.0.1", port=0)` returning `(httpd, port)` where the
   POST handler calls the same `candidate_for`. The `__main__` block dispatches
   on `--cli` and on `--refuse`, where `--refuse` prints nothing and exits `3`.
   All content is fictional. No real course, book, learner, or bank content of
   any kind.

7. Create `director.py` at the repository root. Open it with a module docstring
   restating the peer-module contract from `evidence.py` lines 1 to 19, and
   stating in plain sentences: this module is the agent-client tier; it drafts
   and validates, it never owns accepted truth or assessment authority; every
   durable write reaches disk through `course.py`, which reaches
   `journal.commit_operation`, so this module adds no second write path; every
   rights decision reaches `identity.rights_granted` against the live registry
   at the moment of the operation, and a rights value carried on a
   recommendation record is display context that never authorizes anything;
   this module deliberately does not import `tier_gate`, because that gate
   protects a learner from over-disclosure mid-sitting and a course-builder
   recommendation has no such boundary; and this module deliberately does not
   import `evidence`, `runtime`, or `model`, so the rule that a recommendation
   never touches learner evidence or the one scorer is structural rather than
   maintained by care. No em dash characters anywhere in the file.

8. Define in `director.py`: `DIRECTOR_SCHEMA_VERSION = 1`;
   `RECOMMENDATION_OPERATION = "treatment_recommend"`;
   `RECOMMENDATION_SCHEMA_RESOURCE = "schemas/treatment_recommendation.schema.json"`;
   `AGENT_RECORD_TYPE = "agent_operation"`;
   `AGENT_ENTRY_KEYS = ("operation_id", "intent", "actor_role", "autonomy",
   "scopes", "phase", "phase_index", "checkpoint", "proposal", "egress")`;
   `EGRESS_DESTINATIONS = ("local", "hosted", "registered-local")`;
   `EGRESS_KEYS = ("destination", "backend_class", "profile", "spans",
   "omitted", "payload_bytes", "evidence_included")`;
   `RECOMMENDATION_KEYS = ("schema_version", "objective_id", "treatment_kind",
   "rationale", "synthesis", "confidence", "coverage", "alternatives",
   "citations")`; and `DIRECTOR_CODES` as a set-then-sorted tuple following
   `ADAPTER_CODES`'s construction, holding for this plan exactly
   `director.backend_unavailable`, `director.evidence_forbidden`,
   `director.recommendation_invalid`, `director.rights_not_granted`, and
   `director.unknown_treatment_kind`.

9. Define `DirectorError(Exception)` carrying `.code` and `.message`, using the
   same two-argument constructor shape `graph.GraphError` and `course.CourseError`
   use. Its five message templates for this plan, verbatim:
   - `director.recommendation_invalid`: `"the provider candidate does not
     validate against the recommendation contract: %s; nothing was applied"`
   - `director.unknown_treatment_kind`: `"%s is not one of the eleven
     treatment kinds in TREAT-01; the vocabulary is closed and this phase adds
     no twelfth"`
   - `director.rights_not_granted`: `"the %s right for source %s is %s, so
     this recommendation is refused; next safe action: record %s: granted on
     that source's rights record, or choose a treatment that does not consume
     that right"`
   - `director.backend_unavailable`: `"no model backend answered (%s); the
     objective stays untreated and the core loop is unaffected; next safe
     action: record the treatment by hand with course.bind_treatment, or enable
     another registered profile"`
   - `director.evidence_forbidden`: `"a recommendation payload may not carry
     learner evidence, attempts, scores, marks, or session state; the field %s
     was refused"`

10. Implement `new_operation_id()` returning `identity.new_object_id()`;
    `begin_operation(base, course_root, intent, actor_kind, actor_name,
    actor_role, autonomy, scopes)` which builds the `agent` dict with
    `phase="declare-intent"` and `phase_index=0` and appends it through
    `journal.append_entry`; and `record_phase(base, operation_id, phase,
    phase_index, state, checkpoint=None, proposal=None, egress=None,
    code="", message="")` which appends one further entry carrying the same
    `operation_id`. Both use `journal.append_entry`, never a direct file write.

11. Implement `recommendation_request(doc, objective_id, spans, profile,
    interaction_id, attempt=1)` building the payload dict described in step 2
    and passing it to `model_adapter.request_from_operation` under the key
    `recommendation_request`. Before building, refuse any span dict carrying
    any of the keys `score`, `verdict`, `attempt_number`, `session_id`,
    `mark`, `response`, `canonical`, or `note` by raising `DirectorError` with
    code `director.evidence_forbidden` naming the offending key. Learner
    evidence never reaches a backend.

12. Implement `validate_recommendation(candidate)`: load the recommendation
    schema through `resources.read_text`, validate with
    `schema_validate.validate`, raise `director.recommendation_invalid` on any
    error naming the first error message, then raise
    `director.unknown_treatment_kind` if the non-empty `treatment_kind` is not
    in `graph.TREATMENT_KINDS`, then return a dict whose key order is
    `RECOMMENDATION_KEYS`. Read no field before the schema call returns clean.

13. Implement `recommend_once(base, course_root, objective_id, settings,
    profile_name, actor_kind, actor_name, actor_role, autonomy)`: begin the
    operation, build the spans from the objective's existing source bindings,
    build the request, call `model_adapter.invoke(request, settings)`, and on a
    result whose `status` is not `"ok"` record the phase `plan-treatment` with
    state `refused`, the adapter's error code and message, and return a dict
    `{"status": "unavailable", "code": <adapter code>, "record": None}`
    without raising. On `status == "ok"`, validate the candidate and return
    `{"status": "ok", "code": "", "record": <normalized record>}`.

14. Implement `apply_recommendation(base, course_root, record, source_object_id,
    actor_kind, actor_name)`: resolve the required right with
    `graph.treatment_right(record["treatment_kind"])`, read the CURRENT
    registry through `course.rights_for_binding`, call
    `identity.rights_granted` on the current record, and on a False result
    record the phase `review` with state `refused` and raise
    `DirectorError("director.rights_not_granted", ...)` writing nothing. On a
    True result call `course.bind_treatment`, then record the phase `accept`
    with state `applied` and the egress dict. Never read a rights value carried
    on `record` for this decision; the function signature deliberately does not
    take one.

15. Re-run `python tests/director_roundtrip.py` until it passes. Then run
    `python tests/model_adapter_roundtrip.py`, `python tests/scoring_roundtrip.py`,
    `python tests/evidence_roundtrip.py`, and `python tests/protocol_roundtrip.py`
    and confirm all four still pass. Then run `python itembank.py guard .` and
    confirm it reports `0 offending files`.
  </action>
  <verify>
  <automated>python tests/director_roundtrip.py</automated>
Expected: prints `OK director_roundtrip` and exits 0. Also run
`python tests/model_adapter_roundtrip.py`, expected exit 0, which is the
additivity proof that the fourth enum member broke none of the three shipped
operations. Also run `python itembank.py guard .`, expected final line
`0 offending files` and exit code 0. Degraded states this task proves, each
with its own assertion in `<behavior>`: a missing backend executable returns a
typed unavailable result and leaves the objective untreated; a provider refusal
returns `adapter.provider_refused`; a candidate failing the schema is refused
before any field of it is read; a candidate naming a twelfth treatment kind is
refused by name; and a revoked right refuses a bind whose recommendation record
still claims the right was granted.
  </verify>
  <acceptance_criteria>
- `python tests/director_roundtrip.py` exits 0 and prints `OK director_roundtrip`.
- `python tests/model_adapter_roundtrip.py` exits 0.
- `python tests/scoring_roundtrip.py` exits 0.
- `python tests/evidence_roundtrip.py` exits 0.
- `python tests/protocol_roundtrip.py` exits 0.
- `python itembank.py guard .` prints `0 offending files` and exits 0.
- `python -c "import json; d=json.load(open('schemas/model_adapter.schema.json')); print(d['\$defs']['request']['properties']['operation']['enum'])"`
  prints `['hint', 'rubric_review', 'author', 'treatment_recommend']`.
- `python -c "import model_adapter; print(len(model_adapter._PAYLOAD_KEYS), model_adapter._PAYLOAD_KEYS[-1])"`
  prints `7 recommendation_request`.
- `python -c "import journal; print(len(journal.ENTRY_KEYS), journal.ENTRY_KEYS[-1], len(journal.OPERATION_TYPES), 'agent_operation' in journal.RECORD_TYPES)"`
  prints `23 agent 6 True`.
- `python -c "import director; print(hasattr(director,'tier_gate'), hasattr(director,'evidence'), hasattr(director,'runtime'), hasattr(director,'model'))"`
  prints `False False False False`.
- `python -c "import director; print(len(director.AGENT_ENTRY_KEYS), len(director.EGRESS_KEYS), len(director.RECOMMENDATION_KEYS))"`
  prints `10 7 9`.
- `python -c "import json,schema_validate; schema_validate.check_schema(json.load(open('schemas/treatment_recommendation.schema.json'))); print('schema ok')"`
  prints `schema ok`.
- `git diff --stat journal.py` reports exactly two changed lines of added
  content beyond comments.
- `git diff --name-only` after this task does not list `tier_gate.py`,
  `identity.py`, `graph.py`, `course.py`, `course_package.py`, `model.py`,
  `runtime.py`, `evidence.py`, or any path under `surfaces/`.
- None of `director.py`, `fixtures/mock_backends.py`,
  `schemas/treatment_recommendation.schema.json`, or
  `tests/director_roundtrip.py` contains an em dash character.
  </acceptance_criteria>
  <precondition>Task 1 recorded a clean precondition, and Tasks 2 and 3 recorded answers under `## D-15A-1` and `## D-15A-2` in `15A-DECISIONS.md`.</precondition>
  <reversibility rating="costly">`director.AGENT_ENTRY_KEYS`,
  `director.EGRESS_KEYS`, and `director.RECOMMENDATION_KEYS` are consumed by
  plans 02 through 06. Changing them before the 15A freeze gate costs one edit
  plus one fixture regeneration; changing them after operations have been
  journaled means migrating recorded entries. The genuinely one-way parts, the
  adapter enum and the egress record's home, are gated by Tasks 2 and 3
  above.</reversibility>
  <done>One synthetic objective travels intent, request, adapter invoke,
  candidate validation, live rights check, treatment binding, and journaled
  egress in one green test, and `director.py` exists in its thinnest
  production-quality form.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| director to model backend | Approved source spans leave this machine for a hosted CLI subprocess or an HTTP endpoint. This is the one place in Phase 15A where local content crosses out. |
| model backend to director | The provider candidate is untrusted input returning across the same boundary and is read only after schema validation. |
| recommendation record to course sidecar | An agent-authored proposal becomes a durable, rights-gated write. |
| rights registry to write decision | A registry value read at the moment of the operation decides whether a durable write proceeds. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-15A-01-01 | Information Disclosure | `director.recommendation_request` span assembly | high | mitigate | Spans are built only from the objective's existing source bindings, and any span dict carrying `score`, `verdict`, `attempt_number`, `session_id`, `mark`, `response`, `canonical`, or `note` is refused with `director.evidence_forbidden` before the request is built. `director.py` imports no `evidence` and no `runtime`, asserted at runtime, so learner evidence is structurally unreachable from the egress path. |
| T-15A-01-02 | Elevation of Privilege | `director.apply_recommendation` rights decision | high | mitigate | The required right is resolved from `graph.treatment_right`, the CURRENT registry is read through `course.rights_for_binding`, and the decision goes through `identity.rights_granted`. The function signature takes no rights argument, so a stale value cannot be passed in. Asserted by the revocation case. |
| T-15A-01-03 | Tampering | an untrusted provider candidate applied without validation | high | mitigate | `validate_recommendation` validates against `schemas/treatment_recommendation.schema.json` before reading any field, then re-checks the treatment kind against the closed eleven-member vocabulary. A failing candidate raises before any write and is journaled as refused. |
| T-15A-01-04 | Spoofing | a provider naming a treatment kind, coverage state, or confidence value outside the closed vocabularies | high | mitigate | Every enumerable field in the recommendation schema is a closed `enum`; `treatment_kind` is re-checked against `graph.TREATMENT_KINDS` at runtime so the schema and the module cannot silently drift. |
| T-15A-01-05 | Repudiation | a recommendation applied with no durable record of what was sent and to whom | high | mitigate | Every phase of the operation appends a journal entry carrying `operation_id`, `intent`, `actor_role`, `autonomy`, `scopes`, `phase`, `phase_index`, and `egress`. A refused operation is journaled exactly as an applied one is. |
| T-15A-01-06 | Information Disclosure | a credential reaching a request, a result, a log, or the journal | high | mitigate | Credentials are resolved by `model_adapter._secret_value` from `os.environ` by the profile's `secret_env` NAME only, shipped and unchanged by this plan. `director.py` never reads `secret_env` and never writes a profile dict into a journal entry; the egress record carries only the profile NAME and the backend class. |
| T-15A-01-07 | Elevation of Privilege | routing a course-builder recommendation through the learner-facing tier gate and inheriting the wrong authority model | medium | mitigate | `director.py` imports no `tier_gate`, asserted at runtime. The refusal vocabulary is `DIRECTOR_CODES`, disjoint from `GATE_REASON_CODES`. |
| T-15A-01-08 | Denial of Service | a provider returning an unbounded body or hanging | medium | mitigate | Inherited unchanged from the shipped adapter: per-profile `timeout_seconds` and `max_output_bytes`, with `adapter.timeout` and `adapter.output_cap_exceeded` as typed unavailable results. This plan adds no new transport. |
| T-15A-01-09 | Tampering | supply chain: a third-party agent, schema, or HTTP library introduced here | high | mitigate | None is added; `json`, `os`, `subprocess`, `urllib`, and `http.server` are Python 3.11 standard library already imported by shipped modules. Per `PLANNING-DIRECTIVES.md` section 4a the absence of dependencies is explicitly not the mitigation: the mitigation is that any dependency ever added here is vendored at a pinned version with a recorded checksum and a named license review, following the KaTeX precedent in `09-03-PLAN.md`. |
| T-15A-01-10 | Information Disclosure | real course or learner content entering this repository as a fixture | high | mitigate | `fixtures/mock_backends.py` generates fictional content from a fixed rule, the corpus comes from `fixtures/corpus_14b.py` into temp directories, and `python itembank.py guard .` is part of this task's acceptance criteria. |
| T-15A-01-11 | Repudiation | an operation recorded with an empty actor name | low | accept | `journal.commit_operation` records `origin` with `actor_kind` and `actor_name`; a caller passing an empty name records an empty name honestly. Accepted because 15A has a single local user and the acceptance-policy decision D-12.6-4 is still open. |
</threat_model>

<out_of_scope>
Refused by this plan, by name, so no adjacent temptation is decided by executor
judgment:

- No CLI command and no daemon route for anything in this phase.
  `OPERATION-CONTRACT.md` "Pending surfaces" names the course, discovery,
  binding, and rights-grant commands as not yet shippable and says in plain
  words: do not invent commands for them. `15A-RESEARCH.md` Open Question 1
  recommends the internal-API shape for the freeze gate, matching how 14A-04
  and 14B-06 exercise their modules directly.
- No addition of `treatment_recommendation` to `CONTRACT_NAMES` in
  `surfaces/protocol_cli.py`. That allowlist is asserted at exactly seven names
  by `tests/protocol_roundtrip.py::test_schema_command_output`, and this schema
  is an internal validation contract, not one of the seven published protocol
  documents.
- No change to `build.py`'s `STAGE_FILES`. Packaging the `identity`, `journal`,
  `discovery`, `graph`, `course`, `course_package`, and `director` module family
  into the release artifact is one coherent change owned by whichever phase
  first ships a CLI surface for them; adding `director.py` alone would leave the
  artifact importing a module whose five dependencies are absent.
- No change to `tier_gate.py`. It stays exactly as shipped.
- No second rights vocabulary, no boolean permission flag, no cached grant.
- No coverage classification logic. The recommendation carries a `coverage`
  block and this plan only round-trips it; classifying into
  `graph.BINDING_STATES` is plan 15A-03's.
- No autonomy enforcement, no settings block, no egress minimization caps.
  Those are plan 15A-04's; this plan records the egress dict it is handed.
- No protocol replay, no resume, no reverse, no thirteen-step checklist. Those
  are plan 15A-05's.
- No fourth synthetic domain and no freeze record. Plan 15A-06 owns both, and
  the freeze closes only on a green four-subject review with the Phase 13.9
  precondition satisfied.
- No evidence-based remediation proposal of any kind. That is AGENT-03, owned
  by Phase 15B, and `15A-RESEARCH.md`'s State of the Art table names it out of
  scope for 15A explicitly.
- No progress, completion, mastery, or readiness value. That tuple is
  GRAPH-03's, owned by 16C.
</out_of_scope>

<flagged_assumptions>
Surfaced, not silently dropped, per the spec-less probe fallback protocol:

- **AGENT-02, unclassified edge row (unresolved).** The edge probe could not
  classify AGENT-02 into any of its eight shape categories, so no acceptance
  criterion was derived from it and none is invented here. The requirement's
  own Fixture sentence is covered by plan 15A-06's parity and fallback
  scenarios, and its prohibition list (never self-expand scope, never
  self-certify accessibility, never silently accept an uncertain source claim,
  never transfer evidence, never cross runtime disclosure) is covered by plans
  15A-04 and 15A-05. This row is carried forward as an open assumption for the
  phase verifier to review by hand rather than resolved by guess.
</flagged_assumptions>

<summary_obligations>
`15A-01-SUMMARY.md` records: the precondition result and every deviation the
landed 14A and 14B surfaces showed against their plan text; the options Weibao
chose at Tasks 2 and 3 and any plan edits those choices forced in plans 02
through 06; which truth was verified by which command; the measured wall-clock
time of one `check_thin_slice()` run, recorded and not promised; the exact
`git diff --stat journal.py` output proving the two-line rule; and any
deviation from this plan with its reason.
</summary_obligations>

<output>
Create
`.planning/phases/15A-director-treatment-policy/15A-01-SUMMARY.md`
when done.
</output>
