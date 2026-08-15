---
phase: 14B-graph-course-package-prototype
plan: 04
type: execute
wave: 4
depends_on: ["14B-03"]
files_modified:
  - graph.py
  - course.py
  - journal.py
  - schemas/course_graph.schema.json
  - fixtures/corpus_14b.py
  - tests/graph_roundtrip.py
  - .planning/phases/14B-graph-course-package-prototype/14B-DECISIONS.md
autonomous: false
requirements: [GRAPH-04]
must_haves:
  truths:
    - "A split, merge, rename, demand change, or overlay produces a reviewed migration proposal whose state is proposed; nothing in Phase 14B accepts a proposal, and no code path sets a migration state to accepted (GRAPH-04)."
    - "Historical evidence is never transferred: after splitting one synthetic objective into two, the evidence store holds the same event count it held before, every existing event still carries the original objective identity, and the two new identities carry zero events."
    - "Unmigrated evidence reads unknown on the new identity: graph.objective_evidence_state returns the string unknown for an objective with zero events and never a number, never a percentage, and never a completion or mastery value (GRAPH-04 degraded clause, GRAPH-03 constraint)."
    - "course.py structurally cannot transfer evidence: the imported module exposes no attribute named evidence, so the rule is enforced by the module boundary rather than by care."
    - "migrate is added to journal.RECORD_TYPES and journal.OPERATION_TYPES stays at exactly six members, following the precedent 14A-03 set when it added reconcile the same way; the six frozen operation names are unchanged, so no one-way amendment to the 14A freeze is made by this phase."
    - "A rename keeps the original objective row intact and adds a new identified row plus a migration relation; nothing is deleted, so the append-only discipline the rejection ledger requires of ideas also holds for objective identity."
    - "A migration proposal names its actor and its rationale, and a proposal with an empty rationale is refused by name, so a proposal a reviewer cannot evaluate is never recorded."
  prohibitions:
    - statement: "A migration, alignment, split, merge, or rename must not transfer a learner's historical evidence to a new objective identity, automatically or by any code path in this phase."
      status: kept
      verification: flagged-unverified
  artifacts:
    - "graph.py gains MIGRATION_KINDS, MIGRATION_STATES, migration_proposal, objective_evidence_state, split_objective, and rename_objective"
    - "course.py gains record_migration"
    - "journal.py gains exactly one member in RECORD_TYPES and nothing else"
    - "tests/graph_roundtrip.py gains check_migration"
  key_links:
    - "journal.OPERATION_TYPES is named in 14A-FREEZE.md's Frozen list as the six operation names. Adding migrate there would be a one-way schema break needing an amendment to a freeze this phase does not own. RECORD_TYPES already has an established additive growth path, used twice in 14A, and that is the path this plan takes."
    - "graph.objective_evidence_state takes an event count as an argument rather than reading the evidence store, which is what lets graph.py stay a pure model-tier module with no input or output while still giving GRAPH-04's degraded clause a named function to assert against."
---

<objective>
Land GRAPH-04: objective splits, merges, renames, and changed demand generate
reviewed migration proposals, and historical evidence is never transferred
automatically. The load-bearing half of this plan is the half that does nothing:
a migration in Phase 14B moves identity and records a relation, and it does not
touch a single evidence event.

This is a hard-rejected pattern in this project's own permanent ledger. From
`14B-RESEARCH.md` "Common Pitfalls" number 6: a helpful migration
implementation that copies old evidence onto the new objective identity so the
learner's history looks continuous silently reintroduces exactly the pattern
synthesis section 12.4 hard-rejects. The mitigation here is structural rather
than careful: `course.py` does not import `evidence`, and the test asserts that
it does not.

Decisions already made, cited, and never re-derived here:

- **14A-03's own deferral**, quoted in `14B-RESEARCH.md` "User Constraints":
  `migrate` was recorded as out of scope for 14A and routed to 14B, and the
  omission was recorded deliberately so 14B inherits it rather than
  rediscovering it.
- **14A-03's precedent**, quoted from its Task 2 step 5: add the new name to
  `RECORD_TYPES`, keeping `OPERATION_TYPES` at exactly six. `reconcile` was
  added exactly this way. `migrate` follows it.
- **GRAPH-03's constraint** on this phase, from `14B-RESEARCH.md` "Phase
  Requirements": the graph stores structure, edges, and bindings; it must never
  compute or cache a rolled-up completion or mastery value. `graph.py` returning
  anything resembling a percentage is out of scope and would violate a
  hard-rejected pattern.
- **PLANNING-DIRECTIVES section 3a**, the append-only rejection record: a
  superseded item is never deleted. This plan applies the same discipline to
  objective identity.

Purpose: a course is revised, and a revision that quietly rewrites the learner's
history is worse than no revision at all.
Output: the migration layer, the single additive journal record type, and the
split-and-rename scenario with its evidence assertions.
</objective>

<context>
@.planning/phases/14B-graph-course-package-prototype/14B-RESEARCH.md
@.planning/phases/14B-graph-course-package-prototype/14B-03-PLAN.md
@.planning/phases/14A-identity-lifecycle-operation/14A-03-PLAN.md
@.planning/PLANNING-DIRECTIVES.md
@evidence.py
</context>

## Artifacts this phase produces (plan 14B-04 share)

Added to `graph.py`. Every symbol below is new in this phase.

- Constants: `MIGRATION_KINDS = ("split", "merge", "rename", "demand-change",
  "overlay")`, `MIGRATION_STATES = ("proposed", "accepted", "rejected")`,
  `EVIDENCE_CLAIM_STATES = ("unknown", "present")`.
- Functions: `migration_proposal(kind, from_ids, to_ids, rationale, actor)`,
  `split_objective(doc, objective_id, statements, rationale, actor)`,
  `rename_objective(doc, objective_id, statement, rationale, actor)`,
  `merge_objectives(doc, objective_ids, statement, rationale, actor)`,
  `objective_evidence_state(doc, objective_id, event_count)`.
- New `GraphError` codes: `graph.empty_rationale`,
  `graph.unknown_migration_kind`, `graph.migration_state_not_settable`.

Added to `course.py`: `record_migration(course_root, proposal, actor_kind,
actor_name)`.

Added to `journal.py`: exactly one new member in `RECORD_TYPES`, the string
`"migrate"`. Nothing else in `journal.py` changes.

Added to `schemas/course_graph.schema.json`: the migration `kind` and `state`
enums, already reserved by plan 14B-02 Task 3 and filled here if they were left
as placeholders.

New test function in `tests/graph_roundtrip.py`: `check_migration()`.

No CLI command and no daemon route is produced by this plan.

<tasks>

<task type="checkpoint:decision" gate="blocking">
  <name>Task 1: the migration record shape and where migrate lives</name>
  <files>.planning/phases/14B-graph-course-package-prototype/14B-DECISIONS.md</files>
  <decision>
Does `migrate` become a seventh member of the frozen `journal.OPERATION_TYPES`,
or an additive member of `journal.RECORD_TYPES`, and what fields does a
migration proposal carry?
  </decision>
  <context>
`journal.OPERATION_TYPES` is named explicitly in `14A-FREEZE.md`'s Frozen list
as "the six operation names". `journal.RECORD_TYPES` is the non-frozen superset
that already grew twice during Phase 14A, gaining `mint`, `restore`,
`external_edit`, and then `reconcile`.

This is rated one-way. A migration proposal is appended to an append-only
journal and written into a sidecar that later subphases read. Undoing the field
set after any proposal has been recorded means migrating recorded journal
entries, which is exactly the class of change the compare-and-swap discipline
exists to make visible rather than silent. Changing `OPERATION_TYPES` would be
a one-way amendment to a freeze that Phase 14A owns and Phase 14B does not.
  </context>
  <options>
    <option id="option-a">
      <name>RECOMMENDED DEFAULT: additive RECORD_TYPES member, eight-field proposal</name>
      <pros>`journal.OPERATION_TYPES` stays at exactly six and the Phase 14A
      freeze is untouched, so no amendment is needed. `RECORD_TYPES` grows the
      way it already grew twice in 14A, a one-line change. The proposal carries
      `migration_id`, `kind`, `from`, `to`, `rationale`, `state`, `actor`, and
      `timestamp`, which is the `## Migrations` column set plan 14B-01 already
      writes, so no sidecar column changes.</pros>
      <cons>A reader must know that `RECORD_TYPES` is a superset of
      `OPERATION_TYPES`, which is one more concept than a single flat list.</cons>
    </option>
    <option id="option-b">
      <name>Seventh OPERATION_TYPES member</name>
      <pros>One flat vocabulary. `migrate` reads as a peer of the other six,
      which is how `OPERATION-CONTRACT.md`'s authority vocabulary lists it:
      "Link, import, copy, move, edit-in-place, supersede, migrate, and
      synchronize are distinct operations, never synonyms".</pros>
      <cons>It amends a freeze this phase does not own. Every consumer that
      asserted six operation names, including Phase 14A's own tests, must change.
      `14A-03-PLAN.md` set the opposite precedent deliberately.</cons>
    </option>
    <option id="option-c">
      <name>No journal record at all; the sidecar row is the only record</name>
      <pros>Smallest change. `journal.py` is untouched.</pros>
      <cons>A migration would be the only durable course operation with no
      journal entry, so `journal.replay` could not reconstruct it and the
      operation journal would stop being the complete record it is
      for.</cons>
    </option>
  </options>
  <action>
Ask Weibao the question above with all three options and the recommended
default named, and record the answer verbatim in
`.planning/phases/14B-graph-course-package-prototype/14B-DECISIONS.md` under a
dated heading `## D-14B-3. Where migrate lives and what a proposal carries`.

Note for the asker: `OPERATION-CONTRACT.md` lists `migrate` beside the six
operations in its authority vocabulary. That sentence is about the concepts
being distinct, not about the tuple's membership, and option-a keeps both true:
`migrate` is a distinct operation name recorded in the journal, and the frozen
six-name tuple is unchanged. Say so when presenting the options rather than
letting the apparent conflict decide the answer.

What the executor does with each answer:

- **option-a**: proceed as Tasks 2 and 3 are written.
- **option-b**: before Task 2, add `"migrate"` to `journal.OPERATION_TYPES`,
  update every assertion in the repository that expects six operation names,
  append an amendment section to
  `.planning/phases/14A-identity-lifecycle-operation/14A-FREEZE.md` recording
  the change with its date and reason, and record in `14B-DECISIONS.md` which
  tests changed.
- **option-c**: before Task 2, delete `course.record_migration` from Task 2 and
  from the `<behavior>` list, remove the journal assertions from Task 3, and
  record in `14B-DECISIONS.md` that a migration is not replayable from the
  journal and which later phase owns closing that gap.

Do not proceed with a silent default. An unanswered checkpoint stops the wave.
  </action>
  <verify>
`14B-DECISIONS.md` contains a dated `## D-14B-3` heading naming exactly one of
`option-a`, `option-b`, or `option-c`, with Weibao's answer recorded verbatim.
  </verify>
  <acceptance_criteria>
- `.planning/phases/14B-graph-course-package-prototype/14B-DECISIONS.md`
  contains the literal heading
  `## D-14B-3. Where migrate lives and what a proposal carries`.
- The recorded answer names exactly one of `option-a`, `option-b`, `option-c`.
- The file contains no em dash character.
  </acceptance_criteria>
  <reversibility rating="one-way">A migration proposal is appended to an
  append-only journal and written into a sidecar later subphases read. Changing
  the field set after a proposal exists means migrating recorded entries.
  Option-b additionally amends the Phase 14A freeze.</reversibility>
  <resume-signal>Reply with `option-a`, `option-b`, or `option-c`.</resume-signal>
</task>

<task type="auto" tdd="true">
  <name>Task 2: the migrate record type and the reviewed migration proposal</name>
  <files>journal.py, graph.py, course.py, schemas/course_graph.schema.json, tests/graph_roundtrip.py</files>
  <read_first>
- `journal.py` as landed, specifically `RECORD_TYPES`, `OPERATION_TYPES`,
  `commit_operation`'s step 1 validation, `append_entry`, and `entries`.
- `.planning/phases/14A-identity-lifecycle-operation/14A-03-PLAN.md`, the
  `reconcile` addition in its Task 2 and its acceptance criterion
  `python -c "import journal; print('reconcile' in journal.RECORD_TYPES, ...)"`.
  This task copies that exact shape.
- `graph.py` as it stands after plan 14B-03: `overlay_objective` and the
  `## Migrations` row it already writes, which this task generalizes.
- `.planning/REQUIREMENTS.md` GRAPH-04 in full, including its Fixture sentence.
  </read_first>
  <behavior>
Assertions added to `tests/graph_roundtrip.py` in a new `check_migration()`
function, written before the code.

The journal change, and the change that must not happen:

- `"migrate"` is in `journal.RECORD_TYPES`.
- `journal.OPERATION_TYPES` still equals `("link", "import", "copy", "move",
  "edit_in_place", "supersede")` and still has exactly six members.
- `len(journal.RECORD_TYPES)` equals `len(journal.OPERATION_TYPES) + 5`, the
  five being `mint`, `restore`, `external_edit`, `reconcile`, and `migrate`.
- `journal.commit_operation(..., operation="migrate", ...)` is accepted by step
  1's validation and writes an entry whose `operation` field is `migrate`.
- `journal.commit_operation(..., operation="synchronize", ...)` still raises
  `JournalError` with code `journal.unknown_operation`. The vocabulary stays
  closed; this plan opens it by exactly one name.

The proposal:

- `graph.MIGRATION_KINDS` equals `("split", "merge", "rename",
  "demand-change", "overlay")`.
- `graph.MIGRATION_STATES` equals `("proposed", "accepted", "rejected")`.
- `graph.migration_proposal("split", [a], [b, c], "rationale text", actor)`
  returns a dict with exactly the eight keys `migration_id`, `kind`, `from`,
  `to`, `rationale`, `state`, `actor`, `timestamp`, whose `state` is
  `"proposed"` and whose `migration_id` is a sixteen-character lowercase hex
  string minted with `identity.new_object_id()`.
- `graph.migration_proposal` with an empty or whitespace-only `rationale`
  raises `GraphError` with code `graph.empty_rationale`. A proposal a reviewer
  cannot evaluate is never recorded.
- `graph.migration_proposal` with a kind outside `MIGRATION_KINDS` raises
  `GraphError` with code `graph.unknown_migration_kind`.
- `graph.migration_proposal` accepts no `state` argument at all, and calling it
  with `state="accepted"` raises `TypeError`. Nothing in Phase 14B can mint an
  accepted proposal.
- Setting a recorded row's `state` to `"accepted"` through any `graph.py`
  function raises `GraphError` with code
  `graph.migration_state_not_settable`. Acceptance belongs to a reviewer at
  Phase 15B and is not implemented here.

The recorded migration:

- `course.record_migration(root, proposal, "agent", "claude-code")` appends one
  `## Migrations` row, returns a revision record whose `revision` is one
  greater than before, and appends journal entries whose `operation` is
  `migrate`.
- Reading the sidecar back returns the proposal with every field intact,
  including `rationale` and `actor`.
- `journal.replay(root)` after a migration returns without an entry in its
  `interrupted` list.

The boundary that must hold:

- `hasattr(course, "evidence")` is `False`.
- `hasattr(graph, "evidence")` is `False`.
- Neither `graph.py` nor `course.py` contains a call to any function on the
  `evidence` module, asserted by the two `hasattr` checks above plus the
  behavioral assertions in Task 3.
  </behavior>
  <action>
1. Add `check_migration()` to `tests/graph_roundtrip.py` first, wired into
   `main()`, with every assertion above. Run and confirm it fails.

2. Edit `journal.py` in exactly one place: append `"migrate"` to
   `RECORD_TYPES`, so the line reads `RECORD_TYPES = OPERATION_TYPES +
   ("mint", "restore", "external_edit", "reconcile", "migrate")`. Add a
   trailing comment on that line stating in plain sentences that `migrate` was
   deferred from Phase 14A to Phase 14B by `14A-03-PLAN.md`, that
   `OPERATION_TYPES` stays at exactly six because `14A-FREEZE.md` names the six
   operation names as frozen, and that this is the same additive path
   `reconcile` took. Change nothing else in `journal.py`.

3. Add to `graph.py` the constants `MIGRATION_KINDS`, `MIGRATION_STATES`, and
   `EVIDENCE_CLAIM_STATES`, and the three new `GraphError` codes with these
   exact message templates:
   - `graph.empty_rationale`: `"a migration proposal needs a rationale a
     reviewer can evaluate; an empty rationale is refused"`
   - `graph.unknown_migration_kind`: `"%s is not one of the migration kinds
     split, merge, rename, demand-change, or overlay"`
   - `graph.migration_state_not_settable`: `"a migration state is set by a
     reviewer at acceptance time, and Phase 14B implements no acceptance path;
     a proposal is recorded as proposed and stays proposed"`

4. Implement `graph.migration_proposal(kind, from_ids, to_ids, rationale,
   actor)` returning the eight-key dict described in `<behavior>`. It takes no
   `state` parameter. Its docstring states in plain sentences that a proposal is
   reviewed and never automatic, following the same recorded-human-decision
   posture `journal.reconcile` uses, and that nothing in this phase accepts one.

5. Implement `course.record_migration(course_root, proposal, actor_kind,
   actor_name)`: read the current course, append the proposal as a
   `## Migrations` row through `graph.py`, and write through
   `course.write_course` with `operation="migrate"`. Its docstring states that
   this function touches no evidence and that `course.py` deliberately does not
   import `evidence` so the rule is structural.

6. Fill the migration `kind` and `state` enums in
   `schemas/course_graph.schema.json` if plan 14B-02 left them as placeholders,
   and re-run `python schema_validate.py`.

7. Re-run the test until green, then run the shipped anchor suites
   `python tests/evidence_roundtrip.py` and `python tests/scoring_roundtrip.py`
   and confirm both exit 0, proving the one-line `journal.py` edit disturbed
   nothing.
  </action>
  <verify>
  <automated>python tests/graph_roundtrip.py &amp;&amp; python tests/evidence_roundtrip.py &amp;&amp; python tests/scoring_roundtrip.py &amp;&amp; python schema_validate.py</automated>
Expected: all four exit 0. Degraded states this task proves: a proposal with no
rationale is refused rather than recorded unevaluable; an unrecognized
migration kind is refused by name; a state of `accepted` cannot be produced by
any code path in this phase; and an operation name outside the opened
vocabulary still raises `journal.unknown_operation`, so the vocabulary opened by
exactly one name and not more.
  </verify>
  <acceptance_criteria>
- `python tests/graph_roundtrip.py` exits 0.
- `python -c "import journal; print('migrate' in journal.RECORD_TYPES, len(journal.OPERATION_TYPES))"`
  prints `True 6`.
- `python -c "import journal; print(journal.OPERATION_TYPES)"` prints
  `('link', 'import', 'copy', 'move', 'edit_in_place', 'supersede')`.
- `git diff --stat journal.py` reports exactly one changed line.
- `python -c "import graph; print(graph.MIGRATION_STATES)"` prints
  `('proposed', 'accepted', 'rejected')`.
- `graph.py` contains `def migration_proposal(` and `course.py` contains
  `def record_migration(`.
- `python -c "import graph, course; print(hasattr(graph,'evidence'), hasattr(course,'evidence'))"`
  prints `False False`.
- `python tests/evidence_roundtrip.py` and `python tests/scoring_roundtrip.py`
  both exit 0.
- `journal.py`, `graph.py`, and `course.py` contain no em dash character.
  </acceptance_criteria>
  <reversibility rating="costly">Adding one name to `RECORD_TYPES` is additive
  and cheap; removing it later would orphan any recorded `migrate` entry.
  `OPERATION_TYPES` is left untouched precisely so the genuinely one-way
  change is not made.</reversibility>
  <done>`migrate` is an additive record type, `OPERATION_TYPES` is still six,
  and a migration proposal is reviewed, rationale-bearing, and never
  self-accepting.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: split one objective, rename another, and prove no evidence moved</name>
  <files>graph.py, fixtures/corpus_14b.py, tests/graph_roundtrip.py</files>
  <read_first>
- `evidence.py` lines 108 to 120 (`utc_now`, `new_event_id`), lines 394 to 448
  (`response_event`, the shipped builder whose exact key set the synthetic
  fixture event must match), lines 735 to 755 (`append_event`, the one evidence
  writer and its `recorded` versus `already_recorded` answer), lines 755 to 774
  (`events`), and lines 95 to 105 (`evidence_dir` and `log_path`).
- `tests/evidence_roundtrip.py` lines 1 to 40, for the header convention and
  the `EXPECTED_KEYS` assertion style.
- `.planning/REQUIREMENTS.md` GRAPH-04 in full, especially its Degraded clause:
  "unmigrated evidence stays on the original objective identity and reads as
  unknown for the new one".
- `14B-RESEARCH.md` "Common Pitfalls" number 6, in full.
- `graph.py` as it stands after Task 2.
  </read_first>
  <behavior>
Assertions added to `check_migration()`, written before the code.

Setup, which the fixture builds:

- A temp course root with the `lantern-computing` domain and its own evidence
  store under `_evidence/`.
- One synthetic evidence event, built by calling `evidence.response_event(...)`
  with a synthetic question dict whose `objective` value is the sixteen-hex id
  of the objective about to be split, appended through `evidence.append_event`.
  The event's key set must equal the key set `response_event` returns; nothing
  is hand-assembled.
- Record `before_count = len(list(evidence.events(log)))`, which is `1`.

Split (GRAPH-04's Fixture):

- `graph.split_objective(doc, old_id, ["statement one", "statement two"],
  "the original objective asked for two separable things", actor)` returns a
  tuple of the two new objective records and the proposal.
- The original objective row is still present in `doc["objectives"]` with its
  id and statement unchanged. Nothing is deleted.
- Exactly two new rows exist with freshly minted ids, both with `origin`
  `local`, both with `overlays` empty (a split is not an overlay).
- Exactly one `## Migrations` row is appended, with `kind` `split`, `from`
  holding the old id, `to` holding both new ids space separated, and `state`
  `proposed`.
- `len(list(evidence.events(log)))` still equals `before_count`. No event was
  added, removed, or rewritten.
- The one existing event's `objective` field still equals the OLD id, byte for
  byte.
- For each new id, the number of events whose `objective` equals that id is
  `0`.
- `graph.objective_evidence_state(doc, new_id, 0)` returns exactly the string
  `unknown`.
- `graph.objective_evidence_state(doc, old_id, 1)` returns exactly the string
  `present`.
- `graph.objective_evidence_state` returns a member of
  `graph.EVIDENCE_CLAIM_STATES` for every input and never an integer, never a
  float, and never a string containing a percent sign. Asserted by calling it
  with event counts 0, 1, and 1000 and checking the return type is `str` and
  the value is in the two-member tuple.

Rename:

- `graph.rename_objective(doc, other_id, "a clearer statement", "the original
  wording was ambiguous", actor)` leaves the original row present and unchanged
  and adds one new row plus one `## Migrations` row with `kind` `rename`.
- The evidence count is still `before_count` and the existing event still
  carries its original identity.

Merge and demand change, so the vocabulary is exercised in full:

- `graph.merge_objectives(doc, [id_a, id_b], "one combined statement",
  "rationale", actor)` leaves both originals present, adds one new row, and
  writes one `## Migrations` row with `kind` `merge` and both ids in `from`.
- A `demand-change` proposal is recorded through `graph.migration_proposal`
  directly, with both `from` and `to` holding the same single id, and it round
  trips through the sidecar.

Round trip and byte stability:

- After all four migrations, `graph.serialize_course(graph.parse_course(text))`
  equals `text`.
- The `## Migrations` rows appear in the order they were recorded and are never
  sorted.
  </behavior>
  <action>
1. Add the assertions above to `check_migration()` first. Run and confirm they
   fail.

2. Extend `fixtures/corpus_14b.py` with
   `seed_objective_evidence(course_root, objective_id)`, which builds the
   synthetic question dict, calls `evidence.response_event`, appends through
   `evidence.append_event`, and returns the event id. The synthetic question
   dict names no real bank, item, or subject; its `id` and `item_id` values are
   generated. The fixture is the only place `evidence` is imported in this
   phase's non-test code, and it is a fixture, not a module under test.

3. Implement `graph.split_objective`, `graph.rename_objective`, and
   `graph.merge_objectives`. Each one: mints the new objective rows with
   `identity.new_object_id()` through the existing `add_objective`, builds a
   proposal through `graph.migration_proposal`, appends the proposal row, and
   returns the new records plus the proposal. None of them removes a row. None
   of them takes or touches an evidence log path, an event, or an event count.

4. Implement `graph.objective_evidence_state(doc, objective_id, event_count)`
   returning `"unknown"` when `event_count` is `0` and `"present"` otherwise.
   Its docstring states in plain sentences: this function takes a count as an
   argument rather than reading the evidence store, because `graph.py` performs
   no input or output; it returns one of two state words and never a number,
   because GRAPH-03 forbids the graph from producing an aggregate value; and it
   exists so GRAPH-04's degraded clause, that unmigrated evidence reads unknown
   on the new identity, has a named function to assert against.

5. Re-run the test until green. Then run the full suite the way CI runs it and
   `python itembank.py guard .`.
  </action>
  <verify>
  <automated>python tests/graph_roundtrip.py</automated>
Expected: exits 0. Then run `for t in tests/*.py; do python "$t" || exit 1;
done`, expected exit 0, and `python itembank.py guard .`, expected
`0 offending files`. Degraded states this task proves, each with its own named
assertion: after a split, the evidence event count is unchanged, the existing
event still carries the original identity byte for byte, each new identity has
zero events, and `objective_evidence_state` reads `unknown` on each new
identity. The honest non-action is the point: the correct implementation of
GRAPH-04 is one that leaves the evidence store completely alone.
  </verify>
  <acceptance_criteria>
- `python tests/graph_roundtrip.py` exits 0.
- `for t in tests/*.py; do python "$t" || exit 1; done` exits 0.
- `python itembank.py guard .` prints `0 offending files` and exits 0.
- `graph.py` contains `def split_objective(`, `def rename_objective(`,
  `def merge_objectives(`, and `def objective_evidence_state(`.
- `python -c "import graph; print(graph.objective_evidence_state({}, 'x', 0), graph.objective_evidence_state({}, 'x', 7))"`
  prints `unknown present`.
- `python -c "import graph; print(graph.EVIDENCE_CLAIM_STATES)"` prints
  `('unknown', 'present')`.
- `python -c "import graph, course; print(hasattr(graph,'evidence'), hasattr(course,'evidence'))"`
  prints `False False`.
- `graph.py` and `fixtures/corpus_14b.py` contain no em dash character.
  </acceptance_criteria>
  <done>An objective splits and another renames, both producing reviewed
  proposals, and the evidence store is provably untouched with every new
  identity reading unknown.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| migration operation to evidence store | The one boundary in this phase that must never be crossed. A migration moves identity; the learner's recorded history stays where it was recorded. |
| proposal to acceptance | A recorded proposal could be mistaken for an accepted decision if the state field were settable here. |
| operation vocabulary to the Phase 14A freeze | Adding a name to the wrong tuple amends a freeze this phase does not own. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-14B-04-01 | Tampering / Repudiation | automatic evidence transfer laundered through a migration | high | mitigate | `course.py` and `graph.py` import no `evidence` module, asserted at runtime; `split_objective`, `rename_objective`, and `merge_objectives` take no log path, no event, and no count; the split fixture asserts the event count is unchanged, the existing event still carries the old identity byte for byte, and each new identity has zero events. This is a hard-rejected pattern in synthesis section 12.4. |
| T-14B-04-02 | Elevation of Privilege | a proposal minted or set to `accepted` without a reviewer | high | mitigate | `migration_proposal` takes no `state` argument, so `state="accepted"` raises `TypeError`; setting a recorded row's state through any `graph.py` function raises `graph.migration_state_not_settable`. Acceptance is Phase 15B's. |
| T-14B-04-03 | Tampering | the frozen six-name operation vocabulary silently amended | high | mitigate | `migrate` is added to `RECORD_TYPES` only, following the `reconcile` precedent; the test asserts `OPERATION_TYPES` still has exactly six members and `git diff --stat journal.py` must report exactly one changed line. Option-b at Task 1 is the only path that amends the freeze, and it requires an explicit amendment section in `14A-FREEZE.md`. |
| T-14B-04-04 | Repudiation | a migration recorded with no rationale a reviewer could evaluate | medium | mitigate | `graph.empty_rationale` refuses an empty or whitespace-only rationale before a proposal exists. |
| T-14B-04-05 | Tampering | an objective row deleted by a split, merge, or rename, losing the identity evidence is recorded against | high | mitigate | None of the three functions removes a row; the test asserts the original row is present and unchanged after each operation. The append-only discipline `PLANNING-DIRECTIVES.md` section 3a requires of the rejection ledger is applied to objective identity here. |
| T-14B-04-06 | Information Disclosure | a completion or mastery value leaking into the graph through the evidence state helper | high | mitigate | `objective_evidence_state` returns one of exactly two state words, takes its count as an argument rather than reading the store, and is asserted to return a `str` in a two-member tuple for counts 0, 1, and 1000. GRAPH-03's tuple is 16C's and is read over the graph, never stored in it. |
| T-14B-04-07 | Information Disclosure | real learner evidence entering the repository through the migration fixture | high | mitigate | `seed_objective_evidence` builds a synthetic question dict naming no real bank, item, or subject, writes into a temp directory, and `python itembank.py guard .` is in this plan's acceptance criteria. |
| T-14B-04-08 | Tampering | supply chain: a diff, merge, or graph library added for the migration work | high | mitigate | None is added; `difflib` and `uuid` are Python 3.11 standard library. Per `PLANNING-DIRECTIVES.md` section 4a the absence of dependencies is not the mitigation: any dependency added here is vendored at a pinned version with a recorded checksum and a named license review, the KaTeX precedent. |
</threat_model>

<out_of_scope>
Refused by this plan, by name:

- No acceptance path. A reviewer accepting or rejecting a migration proposal is
  Phase 15B's "accepted revision" work. Phase 14B records proposals only.
- No evidence migration, no evidence relinking, and no evidence rewriting of any
  kind, including a reviewed one. Even a reviewed transfer would need a design
  Phase 14B has no requirement for, and the hard rejection in synthesis section
  12.4 stands.
- No automatic detection of when a split or rename is warranted. This plan
  builds the operation; noticing that an objective should be split is a
  recommender, which is Phase 15A's.
- No reconciliation of the shipped item-level free-text `objective` field with
  the new objective ids, which is what would be needed for a real course's
  evidence to follow a migration. See plan 14B-01's out-of-scope section.
- No change to `journal.py` beyond exactly one line, and no change to
  `identity.py`, `discovery.py`, `evidence.py`, `model.py`, `runtime.py`, or
  anything under `surfaces/`.
- No package, manifest, loss report, or restore. Plan 14B-05.
- No CLI command, no daemon route, no skill documentation.

## Flagged assumption carried forward, not silently dropped

**GRAPH-04, unclassified edge.** The deterministic edge probe over GRAPH-04's
requirement text produced one row it could not classify, recorded here rather
than resolved by guess and rather than dropped.

The question: GRAPH-04 names four triggers, "splits, merges, renames, and
changed demand". Three of them are structural and this plan implements them
directly. The fourth, **changed demand**, refers to the cognitive level or
performance demand an objective asks for. No artifact read while planning this
phase, including `REQUIREMENTS.md`, the Phase 16 synthesis, and every decision
record, defines a demand vocabulary or states what values demand can take. This
plan therefore models `demand-change` as one of the five `MIGRATION_KINDS` and
records a proposal carrying it, and deliberately invents no demand vocabulary.

The reviewer's question when this plan is verified: does GRAPH-04's "changed
demand" require a typed demand field on the objective record in Phase 14B, or is
demand a Phase 16A capability-contract concept that 14B is correct to leave
untyped? If the former, it becomes a 14B gap-closure item. If the latter, close
it in the 14B tracer report. Do not resolve it by adding a demand vocabulary
this phase has no source for.
</out_of_scope>

<summary_obligations>
`14B-04-SUMMARY.md` records: the option Weibao chose at Task 1 and any changes
it forced; the exact one-line `journal.py` diff, quoted; the evidence event
count before and after each migration, quoted from a real run; the disposition
of the flagged GRAPH-04 unclassified edge if it was discussed; which truth was
verified by which command; and any deviation from this plan with its reason.
</summary_obligations>

<output>
Create
`.planning/phases/14B-graph-course-package-prototype/14B-04-SUMMARY.md`
when done.
</output>
