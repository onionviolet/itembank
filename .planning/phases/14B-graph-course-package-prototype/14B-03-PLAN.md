---
phase: 14B-graph-course-package-prototype
plan: 03
type: execute
wave: 3
depends_on: ["14B-02"]
files_modified:
  - graph.py
  - course.py
  - schemas/course_graph.schema.json
  - fixtures/corpus_14b.py
  - tests/graph_roundtrip.py
  - .planning/phases/14B-graph-course-package-prototype/14B-DECISIONS.md
autonomous: true
requirements: [GRAPH-01]
must_haves:
  truths:
    - "Rights are enforced at the binding, not only at export: a binding against a source whose required right is unknown or denied is refused before the write, by name, naming the right, the source, the current state, and the one edit that fixes it (RIGHTS-01, D-12.6-9)."
    - "Unknown rights stay restrictive and never relax: a freshly minted source carries seven unknown rights from identity.rights_default and every binding against it refuses until a grant is recorded; nothing in course.py ever writes a grant it was not given."
    - "A binding reads the source's current rights record from the journal registry at the moment of the operation and never treats a value copied into a binding row as authorization: after a source's right is changed to denied, a new binding refuses even though an earlier binding row still shows a granted snapshot."
    - "The treatment vocabulary is TREAT-01's eleven values and is closed; a twelfth value is refused by name with graph.unknown_treatment_kind, and this phase invents no new treatment kind."
    - "An imported scope binds as an immutable version: after a local edit through graph.overlay_objective, every field of the imported objective row is byte-identical to what it was before, and a new local objective row exists carrying its own minted id, an overlays reference to the imported id, and a migration row with kind overlay."
    - "A field lives in the sidecar only when two or more independently identified objects must agree on it; a value duplicated into the sidecar for readability is marked derived and is never the value a binding or an edge is validated against (D-12.6-8)."
    - "A sidecar declaring a schema version this build does not know is refused by name and never partially read, and a sidecar declaring an older known version is upgraded through a named upgrade step and re-serialized at the current version, so the version migration is prototyped rather than promised (PLANNING-DIRECTIVES section 3a)."
  prohibitions: []
  artifacts:
    - "graph.py gains the treatment and binding vocabularies, add_binding, add_source, overlay_objective, upgrade_document, and UPGRADES"
    - "course.py gains bind_source, bind_treatment, and rights_for_binding"
    - "schemas/course_graph.schema.json gains the binding and treatment enums"
    - "tests/graph_roundtrip.py gains check_bindings_and_rights and check_version_migration"
  key_links:
    - "course.bind_source and course.bind_treatment must call identity.rights_state and identity.rights_granted, the exact pair 14A-03 already gates op_import and op_copy with. A second rights vocabulary anywhere in this phase breaks non-negotiable 2 and silently creates a way for unknown to read as permitted."
    - "The rights_snapshot column exists for history only. If any code path ever reads it to decide whether an operation may proceed, a revoked right stays effective forever, which is Pitfall 5 in 14B-RESEARCH.md."
    - "graph.upgrade_document runs before any validation, and future_schema_version is refused before any field is read. An older build that partially reads a newer sidecar and then rewrites it destroys the fields it did not understand."
---

<objective>
Bind sources and treatments to objectives, and enforce rights at the moment of
the binding rather than at export. This is where RIGHTS-01's "unknown stays
unknown and restrictive, and finding a file never grants permission to transmit
or modify it" stops being a reserved field and starts gating a write. It is also
where GRAPH-01's second sentence lands: an imported scope binds as an immutable
version and a local edit is an overlay record with its own identity and a
migration relation, never an edit to the import.

This plan also builds the version-migration prototype
`PLANNING-DIRECTIVES.md` section 3a requires before any course schema freeze,
alongside the outline projection prototype delivered in plan 14B-02.

Decisions already made, cited, and never re-derived here:

- **RIGHTS-01 shape, built by 14A-03**: `identity.RIGHTS_STATES = ("granted",
  "denied", "unknown")`, `identity.rights_state(record, operation)`,
  `identity.rights_granted(record, operation)`, exact ASCII string match, no
  case folding. This plan adds a second call site for those two functions and
  invents no second rights vocabulary.
- **The 14A-03 rights gate precedent**: `op_import` and `op_copy` require the
  source's `transform` right to equal the exact string `"granted"`; `link`,
  `move`, `edit_in_place`, and `supersede` consume no rights because they act on
  already-owned objects.
- **D-14A-1**: the sidecar holds cross-object relations; a field wholly owned by
  one file's content stays in that file.
- **TREAT-01's eleven-item vocabulary** (`REQUIREMENTS.md` TREAT-01, quoted
  verbatim in `14B-RESEARCH.md` Open Question 4): "direct reading, excerpt,
  guided lesson, notes or terms, worked example, visual or demonstration,
  practice, formal test, assessment-first diagnostic, learner artifact, or human
  review". This is the closed enum for a binding's `treatment_kind`. This phase
  invents no twelfth value.
- **TREAT-02's state vocabulary**: covered, thin, missing, conflicting, unknown;
  heading or name similarity alone cannot produce covered.

Decisions this plan makes and locks, resolving two decisions whose own records
say "pending confirmation at 14B plan time":

| Open question | Locked answer | One-line rationale |
|---|---|---|
| **D-12.6-8**, the metadata threshold between local lesson fields and course registries | Confirmed as recommended: a field lives in the lesson or bank file when it describes only that file's content, and in the sidecar when two or more independently identified objects must agree on it. A registry value duplicated into a file, or a file value duplicated into the sidecar, is a derived regenerable annotation marked `derived` in its column and is never the value anything is validated against | The recommendation is the resolved D-14A-1 hybrid rule restated for metadata; adopting a second, different threshold would give the same question two answers. |
| **D-12.6-9**, rights representation when the user does not know | Confirmed as recommended: `unknown` is an explicit third state distinct from granted and denied, defaulting to restrictive for quote, transform, remote_process, package, export, and share; a refusal names the missing grant so the fix is one edit | 14A-01 already built exactly this shape (`identity.rights_default()` returns seven `unknown` values), so confirming it costs nothing and contradicting it would need a second rights store. The closed provenance vocabulary and the binding user interface named in D-12.6-9 belong to a phase that ships a surface; 14B ships none, and that half is recorded as deferred rather than dropped. |
| Which right each treatment consumes | A locked eleven-key `graph.TREATMENT_RIGHTS` map, given in full in Task 1 | Leaving this to the executor would produce eleven judgment calls; the plan makes them once. |
| Which right a source binding consumes | `read`. A coverage claim records a locator and reproduces nothing | Quoting is what `excerpt` does; a coverage claim points. Even so a fresh source refuses, because `read` also defaults to `unknown`. |
| Whether a binding stores a rights snapshot | Yes, in a `rights_snapshot` column labeled historical in the schema description, never consulted for authorization | An operation journal that cannot say what the rights looked like at bind time cannot be audited; Pitfall 5 is handled by never reading the column back, which the revocation test asserts. |
| How an older sidecar version upgrades | `graph.UPGRADES`, a dict keyed by from-version whose values are named single-step upgrade functions, applied in sequence by `graph.upgrade_document` before any validation | A named, testable step per version is the smallest mechanism that makes the migration a prototype rather than a promise, which section 3a asks for by name. |

Purpose: an objective without a bound source and a chosen treatment is a label;
this is where the graph starts carrying the course.
Output: the binding layer with its rights gate, the imported-scope overlay
mechanism, and the version-migration prototype.
</objective>

<context>
@.planning/phases/14B-graph-course-package-prototype/14B-RESEARCH.md
@.planning/phases/14B-graph-course-package-prototype/14B-02-PLAN.md
@.planning/DECISIONS-12.6-REMAINING-2026-08-14.md
@.planning/DECISIONS-PRE-14A-2026-08-14.md
@.planning/PLANNING-DIRECTIVES.md
@.planning/phases/14A-identity-lifecycle-operation/14A-03-PLAN.md
</context>

## Artifacts this phase produces (plan 14B-03 share)

Added to `graph.py`. Every symbol below is new in this phase.

- Constants: `TREATMENT_KINDS` (the eleven TREAT-01 tokens),
  `TREATMENT_RIGHTS` (an eleven-key dict), `BINDING_KINDS = ("source",
  "treatment")`, `BINDING_STATES = ("covered", "thin", "missing",
  "conflicting", "unknown")`, `SOURCE_BINDING_RIGHT = "read"`,
  `OBJECTIVE_ORIGINS = ("local", "imported")`, `UPGRADES` (a dict keyed by
  from-version).
- Functions: `add_source(...)`, `add_binding(...)`,
  `overlay_objective(doc, imported_objective_id, statement, actor)`,
  `treatment_right(treatment_kind)`, `upgrade_document(doc, from_version)`,
  `upgrade_0_to_1(doc)`.
- New `GraphError` codes: `graph.unknown_treatment_kind`,
  `graph.imported_objective_immutable`, `graph.unknown_upgrade_path`.

Added to `course.py`:

- Functions: `bind_source(...)`, `bind_treatment(...)`,
  `rights_for_binding(base, source_object_id, operation)`.
- New `CourseError` code: `course.rights_not_granted`, `course.unknown_source`.

Added to `schemas/course_graph.schema.json`: the `binding_kind`,
`treatment_kind`, `state`, and `origin` enums, and the `rights_snapshot`
property with its historical-only description.

New test functions in `tests/graph_roundtrip.py`:
`check_bindings_and_rights()` and `check_version_migration()`.

No CLI command, no daemon route, and no journal record type is produced by this
plan.

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: source and treatment bindings, gated by rights at bind time</name>
  <files>graph.py, course.py, fixtures/corpus_14b.py, tests/graph_roundtrip.py</files>
  <read_first>
- `identity.py` as landed: `rights_default`, `rights_state`, `rights_granted`,
  `RIGHTS_OPERATIONS`, `RIGHTS_STATES`. Read the docstrings; they state that an
  absent or empty rights record is identical to an all-unknown record and that
  unknown is restrictive.
- `journal.py` as landed: `read_registry`, `read_object`, `commit_operation`.
- `.planning/phases/14A-identity-lifecycle-operation/14A-03-PLAN.md`, the
  `op_import` and `op_copy` rights gate and the exact `journal.rights_unknown`
  refusal shape. This task copies that shape at a new call site.
- `.planning/REQUIREMENTS.md` RIGHTS-01, TREAT-01, and TREAT-02, in full,
  including their Fixture sentences.
- `.planning/DECISIONS-12.6-REMAINING-2026-08-14.md` D-12.6-8 and D-12.6-9, in
  full.
- `14B-RESEARCH.md` "Pattern 5" and "Common Pitfalls" number 5, in full.
- `course.py` as it stands after plan 14B-01: `read_course`, `write_course`.
  </read_first>
  <behavior>
Assertions added to `tests/graph_roundtrip.py` in a new
`check_bindings_and_rights()` function, written before the code.

Vocabulary:

- `graph.TREATMENT_KINDS` equals, in this order, `("direct-reading",
  "excerpt", "guided-lesson", "notes-or-terms", "worked-example",
  "visual-or-demonstration", "practice", "formal-test",
  "assessment-first-diagnostic", "learner-artifact", "human-review")` and has
  exactly eleven members.
- `graph.BINDING_STATES` equals `("covered", "thin", "missing", "conflicting",
  "unknown")`.
- `graph.add_binding` with `treatment_kind` `"flashcards"` raises `GraphError`
  with code `graph.unknown_treatment_kind`, and the message contains the word
  `eleven`.
- `graph.treatment_right(k)` returns exactly the mapped operation for each of
  the eleven keys, and raises `graph.unknown_treatment_kind` for a twelfth.
- `graph.BINDING_STATES` has no member `"verified"` and no member `"assumed"`.
  The vocabulary is TREAT-02's and is closed.

The rights gate at bind time (RIGHTS-01, Pattern 5):

- Against `meridian-field-response`'s source, whose seven rights are all
  `unknown`: `course.bind_source(...)` raises `CourseError` with code
  `course.rights_not_granted`. The message contains the source object id, the
  string `read`, and the string `unknown`.
- The refusal names the fix: the message contains the substring
  `next safe action: record`.
- After the refusal, the sidecar bytes on disk are unchanged and
  `len(journal.entries(root))` is unchanged. A refused binding writes nothing.
- Against `orrery-algebra`'s source, whose `quote` right is `granted` but whose
  `read` right is `unknown`: `course.bind_source` still refuses, because a
  source binding consumes `read`. A granted right does not imply another.
- With `read` set to `granted`, `course.bind_source` succeeds, returns a
  revision record whose `revision` is one greater than before, and the sidecar
  gains exactly one `## Bindings` row whose `binding_kind` is `source`.
- Against `lantern-computing`'s source, whose `transform` right is `granted`:
  `course.bind_treatment(..., treatment_kind="guided-lesson", ...)` succeeds
  because `guided-lesson` maps to `transform`.
- The same source with `treatment_kind` `"excerpt"`, which maps to `quote`,
  refuses with `course.rights_not_granted` naming `quote`.
- `course.bind_treatment(..., treatment_kind="direct-reading", ...)` against a
  source whose `read` right is `unknown` refuses. Direct reading is a complete
  treatment result, not a free pass.
- Binding against an object id that is not in `journal.read_registry(root)`
  raises `CourseError` with code `course.unknown_source`.

No stale snapshot ever authorizes (Pitfall 5):

- After a successful bind, the written row's `rights_snapshot` cell records the
  state at bind time.
- Change the source's rights record so the same operation now reads `denied`,
  then call the same binding again for a second objective. It refuses with
  `course.rights_not_granted` naming `denied`, even though the earlier binding
  row still shows `granted`. The current registry decides; the snapshot never
  does.
- Structural: `course.py` contains exactly one call path that reads a rights
  value for an authorization decision, and it goes through
  `identity.rights_granted`. Asserted behaviorally by the revocation case
  above; the absence of a second path is recorded as the prohibition in plan
  14B-05's `must_haves`.

Empty and adjacency behavior for bindings:

- A document with zero bindings serializes and round-trips with an empty
  `## Bindings` table (headers present, zero rows) and parses back to an empty
  list, never to `None`.
- Two bindings with the same `objective`, `binding_kind`, and
  `source_object_id` but different `locator` values are two separate rows; a
  binding is not identified by its endpoints alone.
- A binding whose `state` cell holds an unrecognized value degrades to
  `"unknown"` on read, with the source string preserved in `original_state`,
  and never to `"covered"`. TREAT-02's rule that similarity alone cannot
  produce covered is enforced by making `covered` unreachable by degradation.

The D-12.6-8 metadata threshold:

- A `## Sources` row carries a `title` cell marked with the exact suffix
  ` (derived)` when it duplicates a value owned by the source file itself, and
  `graph.py` exposes no function that validates or binds anything against a
  cell carrying that suffix. Asserted behaviorally: a binding whose
  `source_object_id` is correct succeeds even when the derived `title` cell is
  edited to a wrong value, proving the derived annotation is not load-bearing.
  </behavior>
  <action>
1. Add `check_bindings_and_rights()` to `tests/graph_roundtrip.py` first, wired
   into `main()`, with every assertion above. Run and confirm it fails.

2. Add to `graph.py`: `TREATMENT_KINDS` as the eleven-token tuple in the order
   given, with a comment citing `REQUIREMENTS.md` TREAT-01 as the canonical
   source and stating that the vocabulary is closed and that Phase 15A owns
   choosing a treatment while Phase 14B owns only the record shape.

3. Add `TREATMENT_RIGHTS` to `graph.py` as this exact eleven-key map, and give
   it a comment stating that each value is one of `identity.RIGHTS_OPERATIONS`
   and that the mapping is the plan's decision, not the executor's:
   `direct-reading` to `read`; `excerpt` to `quote`; `guided-lesson` to
   `transform`; `notes-or-terms` to `transform`; `worked-example` to
   `transform`; `visual-or-demonstration` to `transform`; `practice` to
   `transform`; `formal-test` to `transform`; `assessment-first-diagnostic` to
   `transform`; `learner-artifact` to `read`; `human-review` to `read`.

4. Add `BINDING_KINDS`, `BINDING_STATES`, `SOURCE_BINDING_RIGHT = "read"`, and
   the `graph.unknown_treatment_kind` code with the exact message template
   `"%s is not one of the eleven treatment kinds in TREAT-01; the vocabulary is
   closed and this phase adds no twelfth"`.

5. Implement `graph.add_source(doc, source_object_id, title, note="")` and
   `graph.add_binding(doc, binding_kind, objective, source_object_id,
   treatment_kind="", locator="", state="unknown", confidence="unknown",
   rights_snapshot="")`, both pure, both appending in authored order, both
   refusing an unknown objective with `graph.unknown_objective` and an unknown
   treatment kind with `graph.unknown_treatment_kind`. On read, an unrecognized
   `state` degrades to `"unknown"` with the source string preserved in
   `original_state`.

6. Implement `course.rights_for_binding(base, source_object_id, operation)`:
   read `journal.read_registry(base)`, refuse a missing object id with
   `CourseError("course.unknown_source", ...)` and the exact message template
   `"%s is not a registered object in this course root's journal registry"`,
   then return `identity.rights_state(record.get("rights"), operation)`. It
   returns a state string and makes no decision.

7. Implement `course.bind_source(...)` and `course.bind_treatment(...)`. Each
   one, in this order: resolves the required rights operation
   (`graph.SOURCE_BINDING_RIGHT` for a source binding,
   `graph.treatment_right(treatment_kind)` for a treatment binding); reads the
   CURRENT registry record; calls `identity.rights_granted(record.get("rights"),
   operation)`; on a False result raises `CourseError("course.rights_not_granted",
   ...)` with the exact message template `"the %s right for source %s is %s, so
   this binding is refused; next safe action: record %s: granted on that
   source's rights record, or choose a treatment that does not consume that
   right"` and writes nothing; on a True result calls `graph.add_binding` with
   `rights_snapshot` set to the state string and then `course.write_course` with
   the current expected fingerprint. The `bind_treatment` docstring states in
   plain sentences that the snapshot column is history and is never read back
   for an authorization decision, and that the current registry is re-read at
   every operation, which is Pitfall 5.

8. Extend `fixtures/corpus_14b.py` so each of the three domains registers its
   source through `journal.op_link` with the rights values named in plan
   14B-02 Task 2, and add a `revoke_right(root, source_object_id, operation)`
   helper the revocation assertion uses.

9. Re-run the test until green, then run `python itembank.py guard .`.
  </action>
  <verify>
  <automated>python tests/graph_roundtrip.py</automated>
Expected: prints `OK graph_roundtrip` and exits 0. Also run
`python itembank.py guard .`, expected `0 offending files`. Degraded states
this task proves, each with its own assertion: a source with unknown rights
refuses every binding and names the missing grant; a granted right for one
operation does not imply another; a revoked right refuses a new binding even
though a stale snapshot row still reads granted; an unrecognized binding state
degrades to unknown and never to covered; and a refused binding leaves both the
sidecar bytes and the journal length unchanged.
  </verify>
  <acceptance_criteria>
- `python tests/graph_roundtrip.py` exits 0.
- `python -c "import graph; print(len(graph.TREATMENT_KINDS), len(graph.TREATMENT_RIGHTS))"`
  prints `11 11`.
- `python -c "import graph; print(graph.treatment_right('excerpt'), graph.treatment_right('guided-lesson'), graph.treatment_right('direct-reading'))"`
  prints `quote transform read`.
- `python -c "import graph,identity; print(all(v in identity.RIGHTS_OPERATIONS for v in graph.TREATMENT_RIGHTS.values()))"`
  prints `True`.
- `course.py` contains `def bind_source(`, `def bind_treatment(`, and
  `def rights_for_binding(`.
- `python -c "import course; print(hasattr(course,'evidence'))"` prints
  `False`.
- `python itembank.py guard .` prints `0 offending files` and exits 0.
- Neither `graph.py` nor `course.py` contains an em dash character.
  </acceptance_criteria>
  <precondition>Phase 14A's `identity.rights_state` and `identity.rights_granted` are present and return the states recorded in `14B-PRECONDITION.md`.</precondition>
  <reversibility rating="costly">The eleven-key `TREATMENT_RIGHTS` map and the
  binding column set are written into every sidecar this phase produces.
  Changing a mapping later means re-reviewing every binding written under the
  old mapping.</reversibility>
  <done>A binding against a source whose right is unknown or denied is refused
  by name before anything is written, and the refusal states the one edit that
  fixes it.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: an imported scope is an immutable version and a local edit is an overlay</name>
  <files>graph.py, fixtures/corpus_14b.py, tests/graph_roundtrip.py</files>
  <read_first>
- `.planning/REQUIREMENTS.md` GRAPH-01, the sentence beginning "An imported
  scope or framework binds as an immutable version", in full.
- `14B-RESEARCH.md` "Pattern 1", the paragraph headed "Consequence for
  GRAPH-01's immutable version, local edits are overlay records clause", in
  full.
- `graph.py` as it stands after Task 1: `add_objective`, `OBJECTIVE_ORIGINS`,
  the `## Objectives` column set including `origin`, `import_version`, and
  `overlays`.
  </read_first>
  <behavior>
Assertions added to `check_bindings_and_rights()` or a sibling function in
`tests/graph_roundtrip.py`, written before the code.

- `graph.OBJECTIVE_ORIGINS` equals `("local", "imported")`.
- `graph.add_objective(doc, statement, origin="imported",
  import_version="scope-2026.1")` writes a row whose `origin` is `imported` and
  whose `import_version` is `scope-2026.1`.
- `graph.overlay_objective(doc, imported_id, "a revised statement", actor)`:
  - leaves the imported row byte-identical. Asserted by capturing the
    serialized `## Objectives` line for that id before the call and comparing it
    to the same line after the call, character for character.
  - creates a new row with a freshly minted id, `origin` `local`, and
    `overlays` equal to the imported id.
  - appends one `## Migrations` row whose `kind` is `overlay`, whose `from`
    holds the imported id, whose `to` holds the new id, and whose `state` is
    `proposed`.
  - returns the new objective record.
- Calling `graph.add_objective` with an existing imported objective's id in a
  way that would rewrite it raises `GraphError` with code
  `graph.imported_objective_immutable`. There is no code path that edits an
  imported row's `statement` in place.
- An overlay of an overlay chains: overlaying the local row produces a third
  row whose `overlays` points at the second, and the first two rows are both
  unchanged. Nothing in the chain is deleted.
- The outline projection renders the newest local row in the chain and does not
  render the superseded rows twice. The superseded rows remain in the file.
  </behavior>
  <action>
1. Add the assertions above to `tests/graph_roundtrip.py` first. Run and
   confirm they fail.

2. Add `OBJECTIVE_ORIGINS` and the `graph.imported_objective_immutable` code
   with the exact message template `"objective %s was imported at version %s
   and is never edited in place; record a local overlay with
   graph.overlay_objective instead"`.

3. Implement `graph.overlay_objective(doc, imported_objective_id, statement,
   actor)` exactly as described in `<behavior>`. Its docstring states in plain
   sentences that the import's bytes are never targeted by an edit because the
   overlay is a sibling record rather than a patch, which is what makes
   GRAPH-01's immutability true by construction rather than by care.

4. Extend `fixtures/corpus_14b.py` so `orrery-algebra` carries two objectives
   with `origin` `imported` at `import_version` `orrery-scope-2026.1`, so the
   overlay assertions have a real imported block to work against.

5. Re-run the test until green.
  </action>
  <verify>
  <automated>python tests/graph_roundtrip.py</automated>
Expected: exits 0. The degraded behavior proved here is the honest non-action
one: an attempt to edit an imported objective raises rather than succeeding
quietly, and the imported row's serialized line is compared character for
character before and after an overlay to prove nothing moved.
  </verify>
  <acceptance_criteria>
- `python tests/graph_roundtrip.py` exits 0.
- `graph.py` contains `def overlay_objective(`.
- `python -c "import graph; print(graph.OBJECTIVE_ORIGINS)"` prints
  `('local', 'imported')`.
- `graph.py` contains no em dash character.
  </acceptance_criteria>
  <done>An imported scope's rows are never rewritten, and a local revision is a
  new identified record joined to the import by a recorded overlay
  relation.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: the version-migration prototype</name>
  <files>graph.py, fixtures/corpus_14b.py, tests/graph_roundtrip.py, .planning/phases/14B-graph-course-package-prototype/14B-DECISIONS.md</files>
  <read_first>
- `.planning/PLANNING-DIRECTIVES.md` section 3a, the paragraph beginning
  "Reversible prototypes are mandatory", in full. It names the graph-to-outline
  projection and the version migration as the two things that must be
  prototyped before a course schema freeze.
- `graph.py` as it stands: `COURSE_GRAPH_VERSION`, `parse_course`,
  `graph.future_schema_version` from plan 14B-01.
- `evidence.py` lines 755 to 774, `events`, for the shipped precedent of
  refusing a `schema_version` newer than this build supports rather than
  guessing at it.
- `runtime.py`'s session upgrade seam, for the shipped precedent of an
  in-place forward upgrade of an older schema version.
  </read_first>
  <behavior>
Assertions added to `tests/graph_roundtrip.py` in a new
`check_version_migration()` function, written before the code.

- `graph.COURSE_GRAPH_VERSION` equals `1`.
- `graph.UPGRADES` is a dict whose keys are integers and whose values are
  callables, and it contains the key `0`.
- `fixtures.corpus_14b.sidecar_text_version_0()` returns a sidecar whose header
  declares `graph_schema_version` `0` and whose `## Edges` table lacks the
  `override` column entirely, which is the difference version 1 introduces.
- `graph.parse_course(sidecar_text_version_0())` succeeds, returns a document
  whose `header["graph_schema_version"]` is `1`, and records
  `doc["upgraded_from"] == 0`.
- Every edge in the upgraded document has `override` equal to `"advisory"`, the
  default the upgrade step supplies. The upgrade adds the missing field with
  the least-blocking value and never guesses a `hard-gate`.
- `graph.serialize_course` of the upgraded document emits the header at version
  `1` and the `## Edges` table with the `override` column present. The upgrade
  is forward and is written back at the current version.
- A version-0 sidecar's unknown sections and unknown columns survive the
  upgrade: round-tripping a version-0 sidecar that also carries a `## Cohorts`
  section emits that section unchanged.
- `graph.parse_course` of a sidecar declaring version `2` raises `GraphError`
  with code `graph.future_schema_version`. The message contains both `2` and
  `1`. The document is not partially read: the raise happens before any section
  is parsed, asserted by giving the version-2 fixture a deliberately malformed
  `## Edges` section and confirming the raised code is
  `graph.future_schema_version` and not `graph.malformed_section`.
- `graph.upgrade_document(doc, 7)` raises `GraphError` with code
  `graph.unknown_upgrade_path`, so a gap in the upgrade chain is named rather
  than skipped.
  </behavior>
  <action>
1. Add `check_version_migration()` to `tests/graph_roundtrip.py` first, wired
   into `main()`, with every assertion above, plus
   `fixtures.corpus_14b.sidecar_text_version_0()`. Run and confirm it fails.

2. Add `graph.UPGRADES` and `graph.upgrade_0_to_1(doc)`. The upgrade step adds
   an `override` value of `"advisory"` to every edge record that has none, sets
   `header["graph_schema_version"]` to `1`, and leaves every other field,
   including every unknown section and unknown column, untouched. Its docstring
   states which single version step it performs and what it supplies for the
   missing field.

3. Implement `graph.upgrade_document(doc, from_version)` applying
   `UPGRADES[from_version]`, then `UPGRADES[from_version + 1]`, and so on until
   `COURSE_GRAPH_VERSION` is reached, raising `GraphError` with code
   `graph.unknown_upgrade_path` and the exact message template `"no upgrade
   step is registered from course graph version %d; the chain to version %d is
   incomplete and this build refuses to guess"` when a step is missing.

4. Wire `parse_course` so the version check is the FIRST thing it does, before
   any section is read: refuse a declared version above `COURSE_GRAPH_VERSION`
   with `graph.future_schema_version`, call `upgrade_document` for a lower
   known version, and record `doc["upgraded_from"]`. Add a comment stating in
   plain sentences that an older build that partially reads a newer sidecar and
   then rewrites it destroys the fields it did not understand, which is why the
   refusal comes first.

5. Append to
   `.planning/phases/14B-graph-course-package-prototype/14B-DECISIONS.md` a
   dated section `## D-14B-2. D-12.6-8 and D-12.6-9 confirmed at 14B plan time`
   recording, in three short paragraphs: the D-12.6-8 metadata threshold as
   confirmed and how the `derived` suffix implements it; the D-12.6-9 rights
   representation as confirmed, with the explicit note that the closed
   provenance vocabulary (owned, licensed, fair-use-claimed, unknown) and the
   binding user interface named in D-12.6-9's recommendation are deferred to
   the subphase that ships a surface, deferred and not dropped, because Phase
   14B ships no surface; and the version-migration prototype as the section 3a
   deliverable, naming `graph.UPGRADES` and the version-0 fixture as its
   evidence. No em dash characters.

6. Re-run the test until green, then run the full suite the way CI runs it and
   confirm exit 0.
  </action>
  <verify>
  <automated>python tests/graph_roundtrip.py</automated>
Expected: exits 0. Then run `for t in tests/*.py; do python "$t" || exit 1;
done`, expected exit code 0. Degraded states this task proves: a future schema
version is refused before any field is read, so an older build never partially
consumes and then destroys a newer file; an older known version upgrades
forward through a named step that supplies the least-blocking default; a gap in
the upgrade chain is refused by name rather than skipped; and unknown sections
survive an upgrade untouched.
  </verify>
  <acceptance_criteria>
- `python tests/graph_roundtrip.py` exits 0.
- `for t in tests/*.py; do python "$t" || exit 1; done` exits 0.
- `graph.py` contains `def upgrade_document(` and `def upgrade_0_to_1(`.
- `python -c "import graph; print(sorted(graph.UPGRADES.keys()))"` prints
  `[0]`.
- `python -c "import graph; print(graph.COURSE_GRAPH_VERSION)"` prints `1`.
- `.planning/phases/14B-graph-course-package-prototype/14B-DECISIONS.md`
  contains the literal heading
  `## D-14B-2. D-12.6-8 and D-12.6-9 confirmed at 14B plan time`.
- `14B-DECISIONS.md` contains no em dash character.
  </acceptance_criteria>
  <reversibility rating="costly">The upgrade chain and the version number are a
  published contract. A wrong default supplied by an upgrade step is written
  into every file it touches, so it is cheap to change now and expensive after
  a real course is upgraded.</reversibility>
  <done>Both reversible prototypes `PLANNING-DIRECTIVES.md` section 3a requires
  before a course schema freeze now exist and are green: the graph-to-outline
  projection from plan 14B-02 and the version migration here.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| source rights record to binding writer | A registry field decides whether a durable write proceeds and whether source material may be transformed. |
| binding row to authorization decision | A value written into a text file at bind time could be mistaken for a current permission. |
| older or newer sidecar to reader | A file written by a different build of this tool crosses into `graph.parse_course` and could be partially read and then rewritten. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-14B-03-01 | Elevation of Privilege | rights bypass through a stale cached snapshot at bind time | high | mitigate | `bind_source` and `bind_treatment` re-read `journal.read_registry` on every call and route the decision through `identity.rights_granted`. The `rights_snapshot` column is described as historical in the schema and is never read back. Asserted by the revocation case: after a right becomes `denied`, a new binding refuses while the old row still shows `granted`. |
| T-14B-03-02 | Elevation of Privilege | unknown rights relaxing to permitted | high | mitigate | `identity.rights_granted` returns True only on the exact ASCII string `granted`; every treatment maps to an explicit right through the locked eleven-key `TREATMENT_RIGHTS`; a fresh source defaults to seven `unknown` values and refuses everything. Asserted against all three domain sources. |
| T-14B-03-03 | Elevation of Privilege | a granted right for one operation implying another | high | mitigate | The map is per-treatment and the check is per-operation; the `orrery-algebra` case asserts that a granted `quote` does not permit a binding that consumes `read`. |
| T-14B-03-04 | Tampering | an imported scope silently edited in place | high | mitigate | There is no code path that rewrites an imported objective row; `graph.imported_objective_immutable` refuses one, and the overlay test compares the imported row's serialized line character for character before and after. |
| T-14B-03-05 | Tampering | an older build partially reading a newer sidecar and then rewriting it, destroying unknown fields | high | mitigate | The version check is the first statement in `parse_course` and refuses a future version before any section is read, asserted by a version-2 fixture with a deliberately malformed section that still raises `graph.future_schema_version`. Unknown sections and columns are also preserved verbatim on every write. |
| T-14B-03-06 | Tampering | an upgrade step guessing a blocking value for a field the older file did not carry | medium | mitigate | `upgrade_0_to_1` supplies `override` `advisory`, the least-blocking default, and a missing chain step raises `graph.unknown_upgrade_path` rather than skipping. |
| T-14B-03-07 | Information Disclosure | source material transformed into lesson prose without a transform grant | high | mitigate | Every generative treatment maps to `transform` in `TREATMENT_RIGHTS`, and the binding is refused before the write. Phase 14B ships no generator, so this gate is the only place the decision is made in this phase. |
| T-14B-03-08 | Tampering | supply chain: a rights, permissions, or schema library added here | high | mitigate | None is added; the rights primitive is `identity.py` from Phase 14A. Per `PLANNING-DIRECTIVES.md` section 4a the absence of dependencies is not the mitigation: any dependency added here is vendored at a pinned version with a recorded checksum and a named license review, the KaTeX precedent. |
| T-14B-03-09 | Repudiation | a binding recorded with no actor and no rights basis | low | accept | `journal.commit_operation` records `origin`, and `rights_snapshot` records the state at bind time. Accepted because 14B has a single local user and the acceptance-policy decision D-12.6-4 is still open. |
</threat_model>

<out_of_scope>
Refused by this plan, by name:

- No treatment recommendation. Phase 14B ships the binding record and its rights
  gate; an agent proposing which treatment an objective should get is Phase
  15A's "director and treatment policy" subphase. TREAT-01 and TREAT-02 are
  therefore deliberately absent from this plan's `requirements` field.
- No rights-grant command, no rights user interface, and no provenance
  vocabulary picker. `OPERATION-CONTRACT.md` "Pending surfaces" names "A
  rights-grant record or per-operation rights command" as not yet shippable.
  D-12.6-9's closed provenance vocabulary is deferred to the subphase that ships
  a surface, recorded in `14B-DECISIONS.md`, not dropped.
- No second rights vocabulary, no second rights store, and no per-binding rights
  record beyond the historical snapshot column.
- No draft, branch, or accepted-revision object. `14A-02-PLAN.md` and
  `14A-03-PLAN.md` both route that to Phase 15B and nothing in 14B's roadmap
  row reassigns it.
- No migration of objective identity. Split, merge, rename, and demand change
  are plan 14B-04's. The `overlay` migration kind is built here only because
  GRAPH-01's own sentence requires it for the imported-scope case.
- No package, manifest, or restore. Plan 14B-05.
- No reconciliation of the shipped item-level free-text `objective` field with
  the new objective ids. See plan 14B-01's out-of-scope section.
- No change to `identity.py`, `journal.py`, `discovery.py`, `model.py`,
  `runtime.py`, `evidence.py`, or anything under `surfaces/`.
</out_of_scope>

<summary_obligations>
`14B-03-SUMMARY.md` records: the eleven-key `TREATMENT_RIGHTS` map as landed;
the exact refusal string a rights-denied binding produced, quoted verbatim from
a real run, so a later phase can reuse the copy rather than reinvent it; the
`public_api()` list as it stands after this plan; which truth was verified by
which command; and any deviation from this plan with its reason.
</summary_obligations>

<output>
Create
`.planning/phases/14B-graph-course-package-prototype/14B-03-SUMMARY.md`
when done.
</output>
