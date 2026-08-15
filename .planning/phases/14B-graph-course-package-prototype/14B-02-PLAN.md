---
phase: 14B-graph-course-package-prototype
plan: 02
type: execute
wave: 2
depends_on: ["14B-01"]
files_modified:
  - graph.py
  - schemas/course_graph.schema.json
  - fixtures/corpus_14b.py
  - tests/graph_roundtrip.py
autonomous: true
requirements: [GRAPH-01, GRAPH-02]
must_haves:
  truths:
    - "A structural container accepts any local label without a schema change: containers labeled program, semester, module, week, unit, chapter, and the invented label fortnight all parse, all round-trip, and all render in the outline, and no enum anywhere in graph.py or schemas/course_graph.schema.json restricts the label value (GRAPH-01)."
    - "Structural order never implies prerequisite status: building the three-domain corpus with every container and every objective adds exactly zero edges, and graph.validate_order reports a warning when a prerequisite-of edge is violated by the authored order but never reorders the authored sequence (GRAPH-01)."
    - "The outline projection reads authored structural order verbatim and is byte-identical across two runs over the same document, so a diff of two outlines shows only what a human changed (GRAPH-01, D-14A-1 diffable clause)."
    - "An edge carries all five GRAPH-02 fields: edge_type, authority, rationale, confidence, and an override policy; the default override is advisory and a hard-gate value is the exceptional case a human must write explicitly (GRAPH-02)."
    - "An unknown edge type is kept and downgraded, never dropped and never a hard block: graph.validate_edge returns effective_type recommended-before, authority advisory, override advisory, and preserves the original string in original_type, and the same downgrade applies to an empty edge_type cell (GRAPH-02, GRAPH-02 empty edge)."
    - "Two edge rows with the same source, edge_type, and target collide and are refused by name with graph.duplicate_edge; they are never merged and never recorded twice. An edge whose source equals its target is refused with graph.self_edge. Edges that share only a source or only a target stay separate (GRAPH-02 adjacency edge)."
    - "Output order is specified and stable when elements compare equal: edges and objectives are re-emitted in authored order on round trip, and graph.propose_order breaks ties by object_id ascending so two runs over the same graph, with the input list shuffled between them, return identical lists (GRAPH-02 ordering edge)."
    - "A prerequisite cycle is reported by name with graph.prerequisite_cycle listing its members and is never silently broken and never left to loop; the outline still renders from authored order because authored order is primary (GRAPH-01, GRAPH-02)."
    - "Identity comparison in the graph is exact ASCII byte equality over minted object ids only; a display title or statement is never compared for identity, and no Unicode NFC or NFD normalization is applied anywhere in graph.py, so two objective statements differing only in accent composition produce two different course fingerprints (GRAPH-01 encoding edge, D-14A-2, FILE-03)."
    - "schemas/course_graph.schema.json passes schema_validate.check_schema without raising SchemaError, which means every keyword in it is inside the shipped SUPPORTED frozenset and the whole document was checked rather than half of it."
    - "The shipped bank and lesson parser is untouched and its output is byte-identical: the golden parse of fixtures/lesson_bank.md recorded before this phase still matches after it, and git diff lists no change to model.py (non-negotiable 4, additive format change proven by a byte-identical fixture)."
    - statement: "The typed graph kernel is additive machinery and never a second document model: graph.py never parses bank or lesson bytes, and the only tabular record format it reads is its own sidecar, exactly as surfaces/day.py:129 parse_lanes reads lanes.md."
      verification: backstop
  prohibitions:
    - statement: "The typed graph kernel must not become a second document model or a second parser for bank or lesson content."
      status: kept
      verification: flagged-unverified
    - statement: "The graph must not produce or cache a single aggregate completion, mastery, or readiness value; the honest-progress tuple is read over the graph, never stored in it."
      status: kept
      verification: flagged-unverified
  artifacts:
    - "graph.py gains validate_edge, validate_order, propose_order, and the GRAPH-02 field constants"
    - "schemas/course_graph.schema.json, validated by the shipped schema_validate.py subset validator"
    - "fixtures/corpus_14b.py widened to three fictional domains with module, week, and chapter containers plus one invented label"
    - "tests/graph_roundtrip.py gains check_edges, check_structure_and_outline, check_schema_file, and check_format_additivity"
  key_links:
    - "The degrade rule and the schema are two different jobs. The closed four-name vocabulary is expressible with a plain enum, but the unknown-type downgrade is NOT expressible in schema_validate.py's supported keyword set and belongs only in graph.py's read path. Encoding it in the schema would need a conditional keyword the validator refuses outright, turning a green schema check into a hard SchemaError."
    - "Authored order is primary and the prerequisite graph validates it. If a later phase makes the projection sort the graph on every read, two runs over an unchanged graph can differ wherever a topological tie exists, and every diff becomes noise, which breaks the diffable half of D-14A-1."
---

<objective>
Widen the proven slice into the full typed graph kernel: the closed edge
vocabulary with its degrade path and its five GRAPH-02 carried fields, the
structural containment layer that accepts any local label without a schema
change, the deterministic outline projection with its order validation and its
topological fallback, and the published sidecar schema. The three-domain
synthetic corpus is built here so plans 03 through 06 have real structure to
work against.

This is the reversible prototype of the graph-to-outline projection that
`PLANNING-DIRECTIVES.md` section 3a requires before any course schema freeze:
"Prototype the graph-to-outline projection and the denominator or version
migration before a course schema freeze". Phase 14B is that prototype; the
freeze belongs to a later subphase.

Decisions already made, cited, and never re-derived here:

- **D-14A-1**: the edge vocabulary is exactly four names, frozen. This plan adds
  no fifth name. Registration of further relations is explicitly later work,
  and the degrade path is how an unregistered relation survives in the meantime
  without being invented into the frozen set.
- **D-14A-2**: identity is opaque and minted, never derived from content, a
  path, or a display name. Fingerprint normalization strips trailing whitespace
  and normalizes line endings, and applies no Unicode normalization.
- **GRAPH-03 constraint** (owned by 16C, quoted in `14B-RESEARCH.md`
  "Phase Requirements"): the graph stores structure, edges, and bindings; the
  honest-progress tuple is computed on demand over the graph plus the evidence
  store. The graph itself must never compute or cache a rolled-up completion or
  mastery value.

Decisions this plan makes and locks:

| Open question | Locked answer | One-line rationale |
|---|---|---|
| What the five GRAPH-02 fields hold | `edge_type` from the frozen four; `authority` from `("authored", "imported", "proposed")` defaulting to `proposed`; `rationale` free text that may be empty; `confidence` from `("high", "medium", "low", "unknown")` defaulting to `unknown`; `override` from `("advisory", "recommended-before", "hard-gate")` defaulting to `advisory` | GRAPH-02 says hard gates are exceptional, so the exceptional value is the one a human must write explicitly and every default is the non-blocking one. |
| What an unrecognized value in any of those four closed sets does | Degrades to that field's default and preserves the source string under `original_<field>` | The same discipline as the unknown edge type, applied consistently, so no unrecognized value can ever escalate authority or blocking behavior. |
| Where the degrade rule lives | In `graph.validate_edge`, never in the schema | `schema_validate.py`'s `SUPPORTED` frozenset has no conditional keyword, and its own docstring says a schema using a keyword outside that set is refused rather than partially checked, so encoding a conditional there is a hard `SchemaError`. |
| Whether the outline sorts | No. Authored structural order is read verbatim. `propose_order` exists and is called only when a set of objectives has prerequisite edges and no authored container placement | `14B-RESEARCH.md` Pattern 4 and Pitfall 2; sorting on every read makes every diff noisy and defeats D-14A-1's diffable clause. |
| Tie-break in `propose_order` | Kahn's algorithm with the ready set sorted by `object_id` ascending before each pop, and successors sorted before decrement | `14B-RESEARCH.md` Pattern 4; a tie-break-free sort is a determinism bug waiting to happen, and dict iteration order is not a specification. |
| Three fictional domains | `meridian-field-response` with `module` containers, `orrery-algebra` with `week` containers plus one `fortnight` container, `lantern-computing` with `chapter` containers | GRAPH-01's fixture names module, week, and chapter; the invented `fortnight` label is what proves a local label needs no schema change. Names are fictional and structurally faithful; `itembank guard` forbids real content. |

Purpose: the graph kernel is the durable instructional spine every later
subphase composes onto, so it is proven against three shaped domains before
anything is bound to it.
Output: the full `graph.py` kernel, the published schema, the three-domain
corpus, and four new assertion functions.
</objective>

<context>
@.planning/phases/14B-graph-course-package-prototype/14B-RESEARCH.md
@.planning/phases/14B-graph-course-package-prototype/14B-PATTERNS.md
@.planning/phases/14B-graph-course-package-prototype/14B-01-PLAN.md
@.planning/phases/14B-graph-course-package-prototype/14B-PRECONDITION.md
@.planning/DECISIONS-PRE-14A-2026-08-14.md
@.planning/PLANNING-DIRECTIVES.md
@schema_validate.py
@schemas/selection.schema.json
</context>

## Artifacts this phase produces (plan 14B-02 share)

Added to `graph.py`. Every symbol below is new in this phase.

- Constants: `EDGE_AUTHORITIES = ("authored", "imported", "proposed")`,
  `EDGE_CONFIDENCES = ("high", "medium", "low", "unknown")`,
  `EDGE_OVERRIDES = ("advisory", "recommended-before", "hard-gate")`,
  `EDGE_FIELD_DEFAULTS` (a dict mapping `authority`, `confidence`, and
  `override` to their defaults), `CONTAINER_LABEL_EXAMPLES` (documentation only,
  never a validation set).
- Functions: `validate_edge(record)`, `edge_key(record)`,
  `validate_order(doc)`, `propose_order(objective_ids, prerequisite_edges)`,
  `public_api()`.
- New `GraphError` codes: `graph.duplicate_edge`, `graph.self_edge`,
  `graph.prerequisite_cycle`, `graph.unknown_objective`.

New schema file: `schemas/course_graph.schema.json`, with
`x-itembank-version` `1`.

New fixture entry points in `fixtures/corpus_14b.py`:
`build_three_domains(dest)` widened to three roots,
`sidecar_text_with_unknowns()` returning a sidecar string that carries an
unrecognized section and an unrecognized column, and
`sidecar_text_with_cycle()`.

New test functions in `tests/graph_roundtrip.py`: `check_edges()`,
`check_structure_and_outline()`, `check_schema_file()`,
`check_format_additivity()`.

No CLI command, no daemon route, and no journal record type is produced by this
plan.

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: the closed edge vocabulary, its five carried fields, and the degrade path</name>
  <files>graph.py, tests/graph_roundtrip.py</files>
  <read_first>
- `graph.py` as delivered by plan 14B-01, in full: `EDGE_TYPES`,
  `DEGRADED_EDGE_TYPE`, `add_edge`, `parse_course`, `serialize_course`, and
  `GraphError`.
- `evidence.py` lines 51 to 55 (`KNOWN_EVENT_TYPES`) and lines 755 to 774
  (`events`, the shipped skip-and-warn-on-unknown read discipline). Copy the
  closed-vocabulary constant shape from here. Do NOT copy its behavior:
  `events()` drops an unrecognized record from its output, and GRAPH-02
  requires the opposite, keeping the record and downgrading only its effective
  value.
- `.planning/REQUIREMENTS.md` GRAPH-02 in full, including its Fixture sentence.
- `.planning/DECISIONS-PRE-14A-2026-08-14.md` D-14A-1, lines 51 to 59, for the
  frozen four-name vocabulary and the sentence stating that other relations
  register later.
  </read_first>
  <behavior>
Assertions added to `tests/graph_roundtrip.py` in a new `check_edges()`
function, written before the code.

Vocabulary and defaults:

- `graph.EDGE_TYPES` equals `("prerequisite-of", "covers-objective",
  "source-supports", "treatment-of")` and has exactly four members. This plan
  adds no fifth.
- `graph.EDGE_AUTHORITIES`, `graph.EDGE_CONFIDENCES`, and
  `graph.EDGE_OVERRIDES` each equal the tuples named in "Artifacts this phase
  produces".
- `graph.validate_edge` over a record with only `source`, `edge_type`, and
  `target` set returns `authority` `"proposed"`, `confidence` `"unknown"`,
  `override` `"advisory"`, and `rationale` the empty string.

The degrade path (GRAPH-02's Degraded clause and its Fixture):

- For each of the four known types, `graph.validate_edge` returns
  `effective_type` equal to the input type and `original_type` equal to the
  input type.
- For the input `"alternate-path"`, `graph.validate_edge` returns
  `effective_type` `"recommended-before"`, `authority` `"advisory"`,
  `override` `"advisory"`, and `original_type` `"alternate-path"`. The record
  is returned, not dropped: the returned value is a dict, never `None`.
- For an empty string `edge_type` and for a missing `edge_type` key, the same
  downgrade applies. An empty cell is unknown, not an error.
- An unknown `edge_type` forces `override` to `"advisory"` even when the source
  row wrote `"hard-gate"`, and the source string is preserved in
  `original_override`. An unknown type can never hard-block.
- An unrecognized `authority` degrades to `"proposed"` with the source string
  in `original_authority`; an unrecognized `confidence` degrades to
  `"unknown"` with the source string in `original_confidence`; an unrecognized
  `override` degrades to `"advisory"` with the source string in
  `original_override`.
- A round trip preserves the original strings: after
  `graph.serialize_course(graph.parse_course(text))` on a sidecar containing an
  `alternate-path` edge row with `override` `hard-gate`, the emitted table row
  still reads `alternate-path` and `hard-gate`. The file records what the human
  wrote; only the effective reading is downgraded.

Adjacency, the GRAPH-02 adjacency edge:

- `graph.edge_key(record)` returns the tuple `(source, edge_type, target)`,
  using the ORIGINAL `edge_type`, not the effective one, so two different
  unregistered types stay distinct.
- Adding a second edge with the same `(source, edge_type, target)` raises
  `GraphError` with code `graph.duplicate_edge`, and `doc["edges"]` still has
  exactly one member afterward. Never merged and never recorded twice.
- Adding an edge whose `source` equals its `target` raises `GraphError` with
  code `graph.self_edge`.
- Two edges sharing only a `source`, and two edges sharing only a `target`, are
  both accepted and stay separate: `len(doc["edges"])` is `2` in each case.
- Adding an edge naming an objective id not in `doc["objectives"]` and not in
  `doc["sources"]` raises `GraphError` with code `graph.unknown_objective`.

Empty, the GRAPH-02 empty edge:

- A document with zero edges: `graph.validate_order(doc)` returns an empty
  list, and `graph.outline_projection(doc)` still renders every objective.
- `graph.propose_order([], [])` returns an empty list and does not raise.
- `graph.propose_order([one_id], [])` returns `[one_id]`.
  </behavior>
  <action>
1. Add `check_edges()` to `tests/graph_roundtrip.py` first, wired into
   `main()`, with every assertion above. Run `python tests/graph_roundtrip.py`
   and confirm the new function fails.

2. Add to `graph.py` the constants `EDGE_AUTHORITIES`, `EDGE_CONFIDENCES`,
   `EDGE_OVERRIDES`, and `EDGE_FIELD_DEFAULTS`. Give `EDGE_OVERRIDES` a comment
   stating in plain sentences that `hard-gate` is the exceptional value GRAPH-02
   names, that it is never a default, and that it is never reachable from an
   unrecognized edge type.

3. Add the three new `GraphError` codes with these exact message templates:
   - `graph.duplicate_edge`: `"an edge %s %s %s is already recorded; a
     duplicate edge is refused, never merged and never recorded twice"`
   - `graph.self_edge`: `"an edge cannot point an object at itself: %s %s %s"`
   - `graph.unknown_objective`: `"%s is not a recorded objective or source in
     this course graph"`

4. Implement `validate_edge(record)` as a pure function returning a NEW dict.
   It never mutates its input and never returns `None`. Its docstring states in
   plain sentences: the four-name vocabulary is frozen by D-14A-1; an
   unrecognized type is kept and downgraded rather than dropped, which is where
   this function deliberately differs from `evidence.events`; and an
   unrecognized value can only ever move a field toward its least-blocking
   default, never toward `hard-gate`.

5. Implement `edge_key(record)` returning the three-element tuple, and wire
   `add_edge` to refuse a duplicate key, a self edge, and an unknown endpoint
   before appending. `add_edge` keeps appending in authored order and never
   sorts.

6. Re-run the test until `check_edges()` passes.
  </action>
  <verify>
  <automated>python tests/graph_roundtrip.py</automated>
Expected: prints `OK graph_roundtrip` and exits 0. Degraded states this task
proves, each with its own assertion: an unknown edge type renders as an
advisory `recommended-before` and never a hard block; an empty edge type cell
degrades identically rather than raising; an unrecognized value in any closed
field degrades to that field's least-blocking default with the original string
preserved; and a zero-edge document still projects an outline.
  </verify>
  <acceptance_criteria>
- `python tests/graph_roundtrip.py` exits 0.
- `python -c "import graph; print(len(graph.EDGE_TYPES))"` prints `4`.
- `python -c "import graph; print(graph.validate_edge({'source':'a','edge_type':'alternate-path','target':'b','override':'hard-gate'})['effective_type'])"`
  prints `recommended-before`.
- `python -c "import graph; print(graph.validate_edge({'source':'a','edge_type':'alternate-path','target':'b','override':'hard-gate'})['override'])"`
  prints `advisory`.
- `python -c "import graph; print(graph.validate_edge({'source':'a','edge_type':'','target':'b'})['original_type'])"`
  prints an empty line.
- `graph.py` contains `def validate_edge(` and `def edge_key(`.
- `graph.py` contains no em dash character.
  </acceptance_criteria>
  <reversibility rating="costly">The five carried field names and their closed
  value sets are written into every sidecar this phase produces. Changing them
  before the 14B freeze gate costs one edit plus a fixture regeneration.
  Changing them after a later subphase freezes the course schema means a
  sidecar migration.</reversibility>
  <done>Every registered edge type and one deliberately unknown type round-trip
  through the sidecar, the unknown one reads as an advisory recommended-before,
  and a duplicate or self edge is refused by name.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: structural containers, the deterministic outline, order validation, and the topological fallback</name>
  <files>graph.py, fixtures/corpus_14b.py, tests/graph_roundtrip.py</files>
  <read_first>
- `graph.py` as it stands after Task 1: `add_container`, `add_objective`,
  `outline_projection`, `SECTION_ORDER`.
- `.planning/REQUIREMENTS.md` GRAPH-01 in full, including its Fixture sentence
  and the clause "structural order never implies prerequisite status".
- `14B-RESEARCH.md` "Pattern 4" in full, including the `propose_order`
  reference implementation and its cycle-handling paragraph, and
  "Common Pitfalls" numbers 2 and 3.
- `fixtures/corpus_14b.py` as delivered by plan 14B-01.
- `identity.py` `registry_rows`, for the shipped tie-break-by-sorted-key
  discipline this task follows.
  </read_first>
  <behavior>
Assertions added to `tests/graph_roundtrip.py` in a new
`check_structure_and_outline()` function, written before the code.

Local labels without a schema change (GRAPH-01):

- Containers created with each of the labels `program`, `semester`, `module`,
  `week`, `unit`, `chapter`, and the invented label `fortnight` all parse,
  round-trip byte-identically, and render in the outline with their label in
  parentheses after the container title.
- `graph.py` contains no tuple, frozenset, or membership test that restricts a
  container label. Asserted structurally: `graph.add_container(doc, "quarter",
  "Q1")` and `graph.add_container(doc, "sprint", "S1")` both succeed and no
  `GraphError` is raised for any non-empty label string.
- `schemas/course_graph.schema.json` (Task 3) likewise carries no `enum` on the
  container label field. Asserted in `check_schema_file()`.

Structural order mints no prerequisite status (GRAPH-01):

- After `fixtures.corpus_14b.build_three_domains(dest)`, for each of the three
  domain documents, `len([e for e in doc["edges"] if e["edge_type"] ==
  "prerequisite-of"])` equals exactly the number of `prerequisite-of` rows the
  generator wrote deliberately, and building containers and objectives alone
  with no explicit `add_edge` call yields `doc["edges"] == []`.
- The outline of a container whose children are ordered 1, 2, 3 emits them in
  1, 2, 3 order, and reversing two `order` values and re-serializing changes
  exactly the two affected lines of the outline and nothing else.

Deterministic outline (D-14A-1 diffable clause, Pitfall 2):

- `graph.outline_projection(doc)` called twice on the same document returns two
  identical strings.
- `graph.outline_projection(graph.parse_course(graph.serialize_course(doc)))`
  equals `graph.outline_projection(doc)`.
- The outline is plain Markdown: every non-blank line starts with `#`, `-`, or
  a letter, and the string contains no HTML tag, no JSON brace at the start of
  a line, and no em dash character.
- When a `prerequisite-of` edge is violated by the authored order, the outline
  is UNCHANGED from the outline of the same document with the edge absent. The
  projection never silently reorders a human's authored sequence.

Order validation, not order generation:

- `graph.validate_order(doc)` returns a list of warning strings. For a document
  where objective B is a prerequisite of objective A and B appears after A in
  authored order, the list has exactly one member and that string contains both
  ids and the words `appears after`.
- For a document whose authored order satisfies every `prerequisite-of` edge,
  the list is empty.
- A `covers-objective`, `source-supports`, or `treatment-of` edge never
  produces an order warning; only `prerequisite-of` does.
- An edge whose effective type was downgraded to `recommended-before` produces
  no order warning at all, because an advisory relation cannot be violated.

The topological fallback and its tie-break (GRAPH-02 ordering edge, Pattern 4):

- `graph.propose_order(ids, edges)` over a graph with two independent roots
  returns them in `object_id` ascending order.
- Calling `propose_order` twice with the input `ids` list shuffled between the
  two calls returns two identical lists.
- The returned order satisfies every prerequisite edge: for each edge, the
  index of the prerequisite is less than the index of its dependent.
- `propose_order` over a graph containing a cycle raises `GraphError` with code
  `graph.prerequisite_cycle`, and the message lists the cycle members in sorted
  order. It never returns a partial, silently truncated order and never loops.
- With the cycle present, `graph.outline_projection(doc)` still returns the
  authored outline and does not raise, because authored order is primary. The
  cycle surfaces through `validate_order` as a warning instead.

Encoding and identity (GRAPH-01 encoding edge):

- Two objectives whose statements differ only in accent composition, one with a
  precomposed character and one with a combining mark, are two different
  records with two different ids, and the two serialized documents produce two
  different values from `identity.object_fingerprint(text, "course")`. No
  Unicode normalization is applied.
- `graph.py` imports no `unicodedata` module: `hasattr(graph, "unicodedata")`
  is `False`.
- Identity comparisons in `graph.py` are over minted ids only. Asserted
  behaviorally: two objectives with the identical statement string and
  different ids remain two separate records, and neither `add_objective` nor
  `add_edge` ever matches a record by its `statement` or `title` value.

The public surface stays what it says it is:

- `graph.public_api()` returns the sorted list of this module's public callable
  names, and it equals an explicit expected list held in the test. This
  assertion is the phase's guard against unplanned API growth, and it is what
  keeps a completion, mastery, or readiness computation from ever appearing in
  this module without a plan edit that also edits the expected list.
  </behavior>
  <action>
1. Add `check_structure_and_outline()` to `tests/graph_roundtrip.py` first,
   wired into `main()`, with every assertion above and the explicit expected
   `public_api()` list. Run and confirm it fails.

2. Widen `fixtures/corpus_14b.py`'s `build_three_domains(dest)` to build three
   fictional course roots, all content generated from a fixed seed so a rebuild
   is byte-identical, all names invented:
   - `meridian-field-response`: containers labeled `module`, six objectives,
     three `prerequisite-of` edges, one `covers-objective` edge, one source with
     every right `unknown`.
   - `orrery-algebra`: containers labeled `week` plus exactly one container
     labeled `fortnight`, five objectives, two `prerequisite-of` edges forming a
     violation of authored order (a prerequisite placed after its dependent),
     one `source-supports` edge, one source whose `quote` right is `granted`.
   - `lantern-computing`: containers labeled `chapter`, five objectives, one
     `treatment-of` edge, one edge with the unregistered type `alternate-path`
     carrying `override` `hard-gate`, and one source whose `transform` right is
     `granted` and whose `package` right is `denied`.
   No real course, book, learner, bank, or lesson content of any kind. Every
   statement is invented filler that reads like a learning objective without
   naming a real subject, textbook, or person.

3. Add `sidecar_text_with_unknowns()` returning a sidecar string carrying a
   `## Cohorts` section `graph.SECTION_ORDER` does not name and an `owner`
   column in the `## Objectives` table, and `sidecar_text_with_cycle()`
   returning a sidecar whose `## Edges` table contains a three-node
   `prerequisite-of` cycle.

4. In `graph.py`, add `CONTAINER_LABEL_EXAMPLES` as a documentation-only tuple
   with a comment stating in plain sentences that it is a list of examples for a
   human reader and is never used in a membership test, because GRAPH-01
   requires a local label to be accepted without a schema change.

5. Implement `validate_order(doc)` returning a list of warning strings, one per
   violated `prerequisite-of` edge, each of the exact shape
   `"prerequisite %s appears after dependent %s in the authored order; the
   authored order is unchanged and this is reported for review"`. It considers
   only edges whose effective type is `prerequisite-of` after
   `validate_edge`, and it never mutates `doc`.

6. Implement `propose_order(objective_ids, prerequisite_edges)` exactly as
   `14B-RESEARCH.md` Pattern 4 specifies: Kahn's algorithm, the ready set
   sorted ascending by `object_id` before each pop, successors sorted before
   each decrement, and a re-sort of the ready set after each expansion. On a
   remaining-node condition raise `GraphError` with code
   `graph.prerequisite_cycle` and the exact message template `"a prerequisite
   cycle involves at least these objectives: %s; reported for review, never
   silently broken"`. The docstring states that this function is the fallback
   used only when a set of objectives has prerequisite edges and no authored
   container placement, that the normal path reads authored order verbatim, and
   that the sorted tie-break exists so two runs over one graph produce a
   byte-identical proposed order.

7. Implement `public_api()` returning
   `sorted(n for n in globals() if not n.startswith("_") and
   callable(globals()[n]))`, excluding imported module objects and exception
   classes, with a docstring stating that the test asserts this list against an
   explicit expected set so the module's surface cannot grow without a plan
   edit.

8. Re-run the test until green, then run `python itembank.py guard .` and
   confirm `0 offending files`.
  </action>
  <verify>
  <automated>python tests/graph_roundtrip.py</automated>
Expected: prints `OK graph_roundtrip` and exits 0. Also run
`python itembank.py guard .`, expected final line `0 offending files`.
Degraded states this task proves: a prerequisite cycle is named rather than
looped or truncated, and the outline still renders while the cycle is present;
an order violation is reported as a warning while the authored sequence is left
exactly as the human wrote it; a container label the code has never seen is
accepted without a schema change; and an advisory downgraded edge produces no
order warning at all.
  </verify>
  <acceptance_criteria>
- `python tests/graph_roundtrip.py` exits 0.
- `python itembank.py guard .` prints `0 offending files` and exits 0.
- `graph.py` contains `def validate_order(`, `def propose_order(`, and
  `def public_api(`.
- `python -c "import graph; print(hasattr(graph,'unicodedata'))"` prints
  `False`.
- `python -c "import graph,tempfile,sys; sys.path.insert(0,'.'); import fixtures.corpus_14b as c; d=tempfile.mkdtemp(); r=c.build_three_domains(d); print(len(r['domains'])); c.teardown(d)"`
  prints `3`.
- Running `python tests/graph_roundtrip.py` twice produces identical stdout.
- Neither `graph.py` nor `fixtures/corpus_14b.py` contains an em dash
  character.
  </acceptance_criteria>
  <done>The three-domain corpus exists with module, week, chapter, and one
  invented container label; the outline reads authored order verbatim and is
  stable across runs; order violations and cycles are reported by name and
  never silently resolved.</done>
</task>

<task type="auto">
  <name>Task 3: the published sidecar schema and the byte-identical additivity fixture</name>
  <files>schemas/course_graph.schema.json, tests/graph_roundtrip.py</files>
  <read_first>
- `schema_validate.py` lines 1 to 75 in full: the module docstring's
  "refused, not partially checked" rule, the `SUPPORTED` frozenset, the
  `ANNOTATIONS` frozenset, and `check_schema`. The `SUPPORTED` set is the hard
  ceiling on what this schema may use.
- `schemas/selection.schema.json` in full, for the house schema shape,
  including `$schema`, `$id`, `title`, `description`, `x-itembank-version`,
  `additionalProperties`, and the per-property `description` convention.
- `fixtures/lesson_golden_phase3_parse.json` and
  `fixtures/lesson_golden_phase3_content.txt`, the shipped golden parse
  snapshot that predates this phase, and the existing test that consumes them,
  for how the golden comparison is performed today.
- `.planning/PLANNING-DIRECTIVES.md` section 4 item 4 and section 4a's
  paragraph beginning "4.2 forbids a second parser", in full. That paragraph is
  the reason this phase is additive rather than a violation.
  </read_first>
  <action>
1. Add `check_schema_file()` and `check_format_additivity()` to
   `tests/graph_roundtrip.py` first, wired into `main()`, with these assertions:

   - `schema_validate.check_schema(json.load(open("schemas/course_graph.schema.json")))`
     returns without raising `SchemaError`.
   - Running `python schema_validate.py` (the shipped self-check step) exits 0.
   - The schema's `x-itembank-version` is `1`.
   - The schema's edge-type property carries an `enum` whose members equal
     `list(graph.EDGE_TYPES)`, proving the frozen vocabulary is published.
   - The schema's container label property carries NO `enum` key, proving
     GRAPH-01's local-label clause is honored in the published contract and not
     only in the code.
   - The schema contains no key outside `schema_validate.SUPPORTED` union
     `schema_validate.ANNOTATIONS`. Asserted by the `check_schema` call above,
     which walks the whole document.
   - `schema_validate.validate(schema, instance)` accepts the serialized header
     and edge records of the `meridian-field-response` domain document and
     rejects an edge record missing its `target` key.
   - **The byte-identical additivity fixture.** Read
     `fixtures/lesson_bank.md` bytes, parse with `model.load`, and compare the
     result against the shipped golden snapshot
     `fixtures/lesson_golden_phase3_parse.json` using the same comparison the
     existing lesson test uses. It must match exactly. A bank or lesson that
     uses no graph block parses byte-identically after this phase, because this
     phase adds no branch to `model.py` at all.
   - `graph.py` does not import `model`: `hasattr(graph, "model")` is `False`.
   - The sidecar round trip preserves unknown structure:
     `graph.serialize_course(graph.parse_course(
     fixtures.corpus_14b.sidecar_text_with_unknowns()))` equals that text
     exactly, byte for byte.

   Run the test and confirm the new functions fail.

2. Create `schemas/course_graph.schema.json` following
   `schemas/selection.schema.json`'s shape exactly: `$schema` set to
   `https://json-schema.org/draft/2020-12/schema`, `$id` set to
   `https://itembank.local/schemas/course_graph.schema.json`, `title` set to
   `itembank course graph sidecar`, a `description` naming this as the
   published contract for the structured portions of `course-graph.md`,
   `x-itembank-version` `1`, `type` `object`, and `additionalProperties`
   `false`.

   Define `$defs` for `header`, `container`, `objective`, `source`, `edge`,
   `binding`, and `migration`. Constrain only what the shipped validator can
   express: `type`, `properties`, `required`, `additionalProperties`, `enum`,
   `items`, `minLength`, and `pattern`. Put an `enum` on `edge_type` with the
   four frozen names, on `authority`, `confidence`, and `override` with their
   closed sets, on `origin` with `local` and `imported`, on `binding_kind`,
   `state`, and `treatment_kind` with the sets plan 14B-03 will use, and on
   migration `kind` and `state` with the sets plan 14B-04 will use. Put a
   `pattern` of `^[0-9a-f]{16}$` on every id property.

   Put NO `enum` on the container `label` property. Add a `description` on that
   property reading exactly: `A local structural label such as program,
   semester, module, week, unit, or chapter. The value is deliberately
   unconstrained: GRAPH-01 requires a local label to be accepted without a
   schema change.`

   Use no keyword outside `schema_validate.SUPPORTED` and
   `schema_validate.ANNOTATIONS`. In particular use no `patternProperties`, no
   `allOf`, no `anyOf`, no `not`, and no `if` or `then`. The unknown-edge-type
   downgrade rule is NOT expressible here and belongs only in
   `graph.validate_edge`; attempting to express it would make `check_schema`
   raise `SchemaError` and turn a green check into a hard failure. Add a
   top-level `description` sentence saying so.

3. No em dash characters in the schema file, including inside any
   `description` string.

4. Re-run the test until green. Then run the two shipped anchor suites,
   `python tests/scoring_roundtrip.py` and `python tests/lesson_roundtrip.py`,
   and confirm both exit 0. Then run `python itembank.py guard .`.
  </action>
  <verify>
  <automated>python tests/graph_roundtrip.py &amp;&amp; python schema_validate.py &amp;&amp; python tests/scoring_roundtrip.py &amp;&amp; python tests/lesson_roundtrip.py</automated>
Expected: all four exit 0. The degraded behavior proved here is the honest
non-action one: this phase adds no parse branch to `model.py`, so the shipped
golden parse snapshot still matches byte for byte and the two anchor suites
stay green. The additivity claim is an assertion against a snapshot that
predates this phase, not a promise in prose.
  </verify>
  <acceptance_criteria>
- `python tests/graph_roundtrip.py` exits 0.
- `python schema_validate.py` exits 0.
- `python tests/scoring_roundtrip.py` and `python tests/lesson_roundtrip.py`
  both exit 0.
- `python -c "import json,schema_validate as s; s.check_schema(json.load(open('schemas/course_graph.schema.json'))); print('schema fully checked')"`
  prints `schema fully checked` and exits 0.
- `python -c "import json; d=json.load(open('schemas/course_graph.schema.json')); print(d['\$defs']['edge']['properties']['edge_type']['enum'])"`
  prints the four frozen edge type names.
- `python -c "import json; d=json.load(open('schemas/course_graph.schema.json')); print('enum' in d['\$defs']['container']['properties']['label'])"`
  prints `False`.
- `git diff --name-only` after this task does not list `model.py`,
  `runtime.py`, `evidence.py`, `journal.py`, or `identity.py`.
- `python itembank.py guard .` prints `0 offending files` and exits 0.
- `schemas/course_graph.schema.json` contains no em dash character.
  </acceptance_criteria>
  <reversibility rating="costly">A published schema under `schemas/` is a
  contract other clients read. Adding a field later is additive and cheap;
  removing or renaming one after a sidecar has been written means a
  migration.</reversibility>
  <done>The sidecar's structured portions have a published contract the shipped
  subset validator checks in whole, and the additivity claim is proven against a
  golden parse snapshot that predates this phase.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| course root to sidecar reader | Arbitrary, hand-edited or externally edited Markdown crosses into `graph.parse_course`, including malformed tables, unknown sections, and cyclic edge sets. |
| edge record to authority decision | A row in a text file decides whether a relation reads as advisory or as a hard gate. |
| schema file to validator | A schema using an unsupported keyword would silently check half the contract if the validator allowed it. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-14B-02-01 | Elevation of Privilege | an unrecognized edge type or field value escalating to `hard-gate` | high | mitigate | `validate_edge` forces `override` to `advisory` whenever `edge_type` is not one of the frozen four, and every unrecognized closed-set value degrades to its least-blocking default. Asserted with an `alternate-path` edge that writes `hard-gate` explicitly. |
| T-14B-02-02 | Denial of Service | a prerequisite cycle looping or silently truncating the projection | high | mitigate | Kahn's algorithm detects the remaining-node condition and raises `graph.prerequisite_cycle` listing the members; the outline still renders from authored order so a cycle cannot break the read path. The corpus contains a real three-node cycle so a regression fails the test rather than shipping. |
| T-14B-02-03 | Tampering | a malformed or hostile sidecar row crashing the reader or dropping a record | medium | mitigate | Unknown sections and unknown columns are preserved verbatim; a section that is not a table raises `graph.malformed_section` and performs no write, since `graph.py` has no file input or output at all. |
| T-14B-02-04 | Tampering | a schema that checks half the contract while reporting green | high | mitigate | `schema_validate.check_schema` walks the whole document and raises `SchemaError` on any keyword outside `SUPPORTED`; this task asserts that call passes, and forbids `patternProperties`, `allOf`, `anyOf`, `not`, and `if` by name. |
| T-14B-02-05 | Spoofing | edge or objective identity derived from record content or from a display string | high | mitigate | Ids are minted with `identity.new_object_id()` only; edge identity is the `(source, edge_type, target)` tuple; no function matches a record by `statement` or `title`, and no Unicode normalization is applied so two visually similar strings are never conflated. |
| T-14B-02-06 | Tampering | a format change that silently breaks a shipped bank or lesson | high | mitigate | This phase adds no branch to `model.py`; asserted by the golden parse snapshot `fixtures/lesson_golden_phase3_parse.json`, which predates this phase, plus a `git diff --name-only` acceptance check. |
| T-14B-02-07 | Information Disclosure | real course content entering the repository through the three-domain corpus | high | mitigate | All three domains are invented, generated from a fixed seed, and built into temp directories; `python itembank.py guard .` is in this plan's acceptance criteria twice. |
| T-14B-02-08 | Tampering | supply chain: a graph library or JSON Schema library added for this work | high | mitigate | None is added. `14B-RESEARCH.md` "Alternatives Considered" records the real cost of `networkx` and of a `jsonschema` dependency rather than rejecting either on principle. Per `PLANNING-DIRECTIVES.md` section 4a the absence of dependencies is not the mitigation: any dependency added here must be vendored at a pinned version with a recorded checksum and a named license review, the KaTeX precedent. |
| T-14B-02-09 | Repudiation | an order proposal that differs between two runs, making a diff unreviewable | medium | mitigate | `propose_order` sorts the ready set by `object_id` before each pop and the test shuffles its input between two calls and asserts identical output. |
</threat_model>

<out_of_scope>
Refused by this plan, by name:

- No fifth edge type. D-14A-1 froze exactly four names and said other relations
  register later. The degrade path is how an unregistered relation survives
  until then; it is not permission to add one here.
- No CLI command, no daemon route, no skill documentation. See plan 14B-01's
  out-of-scope section and `OPERATION-CONTRACT.md` "Pending surfaces".
- No source binding, no treatment binding, no rights check. Plan 14B-03.
- No migration, no split, merge, or rename. Plan 14B-04.
- No package, manifest, loss report, or restore. Plan 14B-05.
- No treatment recommendation. 14B ships the record shape; choosing a treatment
  is Phase 15A's "director and treatment policy" subphase.
- No progress, completion, mastery, readiness, or percentage value of any kind
  anywhere in `graph.py`. `public_api()` plus its explicit expected list is the
  structural guard, and the prohibition is recorded in this plan's
  `must_haves.prohibitions`.
- No reordering of a human's authored sequence under any circumstance,
  including a detected violation or a detected cycle. The projection reports;
  it does not correct.
- No SQLite or other index over the sidecar. `14B-RESEARCH.md` "Alternatives
  Considered" allows a disposable rebuildable index if the three-domain scale
  showed it was needed; it does not, and a first cut does not add one.
</out_of_scope>

<summary_obligations>
`14B-02-SUMMARY.md` records: the exact `public_api()` list as it stands at the
end of this plan, so plans 03 through 06 extend it deliberately; the three
domain names and their container labels; whether the golden parse comparison
needed any adjustment to run and why; which truth was verified by which
command; and any deviation from this plan with its reason.
</summary_obligations>

<output>
Create
`.planning/phases/14B-graph-course-package-prototype/14B-02-SUMMARY.md`
when done.
</output>
