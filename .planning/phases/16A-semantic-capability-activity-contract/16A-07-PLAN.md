---
phase: 16A-semantic-capability-activity-contract
plan: 07
type: execute
wave: 7
depends_on: ["16A-06"]
files_modified:
  - capabilities.py
  - fixtures/lesson_capability_corpus.py
  - tests/capability_stress_corpus_tracer.py
autonomous: true
requirements: [CAP-03, PORT-01]
estimate:
  tokens: 72000
  raw_tokens: 72000
  tasks: 2
  confidence: low
must_haves:
  truths:
    - "Two registered output modes, outline and glossary, compose from one stress-corpus lesson's shared schemas: the outline reads model.parse_lesson's headings list and, when a course graph is supplied, graph.outline_projection's objective spine, and the glossary reads model.parse_terms's output, so neither mode owns a private extractor and no second outline generator exists anywhere in this phase."
    - "Every registered output mode is derived and disposable: composing twice from the same canonical lesson produces equal records, and every string in a composed record appears in the canonical Markdown source, so deleting every derived view loses nothing that was not also in the file (CAP-03 derivation probe, the row the edge probe returned as unclassified)."
    - "The eight modes CAP-03 names that are not registered here stay as backburner catalog entries rather than disappearing: notebook page, Cornell notes, concept map, formula sheet, timeline, comparison table, study guide, and source-extracted notes each carry a shared primitive, a dependency, a cost, and a revisit trigger, which is exactly CAP-03's Degraded clause and PLANNING-DIRECTIVES section 3a's breadth-preservation rule."
    - "No new canonical type is minted for either registered mode: an output mode is a derived record built by a pure function from an already parsed lesson, and capabilities.py contains no open( call after this plan just as it did not before."
    - "backburner_entry refuses an entry missing any of its four fields, so a mode cannot be parked with an empty trigger and quietly forgotten; a catalog entry with no revisit condition is how breadth turns into silent cutting."
  prohibitions:
    - statement: "A derived view must not become the only understandable copy; an outline, a glossary, a rendered page, an index, or a cache is disposable, and the canonical Markdown must stay complete with every one of them deleted."
      status: kept
      verification: flagged-unverified
    - statement: "A viable capability must not be dropped for being untimely, optional, expensive, or simple; an unregistered mode is parked with its primitive, dependency, cost, and trigger recorded, never removed, per the append-only breadth discipline."
      status: kept
      verification: flagged-unverified
    - statement: "A second outline generator must not be written; where a course graph is in play, graph.outline_projection is the one projection, and a private reimplementation inside this phase would be the duplicated-truth pattern CAP-03 rejects by name."
      status: kept
      verification: flagged-unverified
  artifacts:
    - "capabilities.OUTPUT_MODES, capabilities.BACKBURNER_MODES, capabilities.OUTPUT_MODE_KEYS, capabilities.BACKBURNER_KEYS"
    - "capabilities.compose_outline, capabilities.compose_glossary, capabilities.backburner_entry, capabilities.backburner_catalog"
    - "fixtures/lesson_capability_corpus.py gains build_output_mode_lesson"
    - "tests/capability_stress_corpus_tracer.py gains scenario_output_modes and scenario_backburner_catalog"
  key_links:
    - "compose_outline takes an optional graph_doc and delegates the objective spine to graph.outline_projection when one is supplied. Without that delegation the function would be a second outline generator, which 16A-RESEARCH.md's Don't Hand-Roll table names as the duplicated-truth anti-pattern CAP-03 rejects. Without the optional argument the function could not run on a lesson alone, which is what the freeze-gate fixture actually composes."
    - "The derivation proof asserts every string in a composed record appears in the canonical source bytes. Asserting only that composing twice is deterministic would pass for a function that invented content deterministically, and inventing content is exactly how a derived view becomes the only understandable copy."
    - "backburner_entry validates all four fields because the trigger is the field that gets left empty. A parked capability with a primitive, a dependency, and a cost but no revisit condition looks documented and is functionally deleted, which is the failure PLANNING-DIRECTIVES section 3a's append-only rule exists to prevent."
    - "OUTPUT_MODES and BACKBURNER_MODES together must equal CAP-03's ten named modes exactly. If they did not, a mode could fall out of both lists and vanish without any check noticing, which is the silent omission the same section-3a rule forbids."
---

<objective>
Compose two registered output modes from one lesson's shared schemas, prove they
are derived rather than authoritative, and park the other eight without losing
them.

CAP-03, quoted: "Registered output modes (notebook page, outline, Cornell notes,
concept map, glossary, formula sheet, timeline, comparison table, study guide,
source-extracted notes) compose from shared note and activity schemas plus
provenance; a new canonical type is minted only when validation or behavior
genuinely differs. Owner: lesson-authoring skill. Durable object: registered
output-mode record. Authority: capability registry. Degraded: an unregistered
mode stays a backburner catalog entry naming its shared primitive, dependency,
cost, and trigger."

The synthesis's own disposition for these ten, quoted from
`research/phase-16/14-synthesis.md` section 12.2: "Registered output modes after
prototype ... They share stable relations and provenance but retain distinct
intent, structures, learner actions, and validators."

Two of the ten are chosen because both already have a shared primitive that
ships or lands in this milestone. The outline's spine is `parse_lesson`'s
`headings` list plus, when a course is in play, `graph.outline_projection`. The
glossary's spine is `parse_terms`'s output, which has shipped since Phase 3.1.
Neither mode gets a private extractor, and this phase writes no second outline
generator: `16A-RESEARCH.md`'s Don't Hand-Roll table names that as the
duplicated-truth pattern CAP-03 rejects.

The other eight are parked, not cut. `PLANNING-DIRECTIVES.md` section 3a,
quoted: "A capability is not dropped merely because it is optional, expensive,
specialized, or absent from the next wave. Simplicity alone is not a rejection
reason." A backburner entry that names its primitive, its dependency, its cost,
and its revisit trigger is a capability with a route back. One with an empty
trigger is a deletion wearing a catalog entry's clothes, which is why
`backburner_entry` refuses it.

The derivation question is the one this plan actually settles. PORT-01, quoted:
"derived HTML, index, or cache is never the sole understandable copy". An output
mode is the most tempting place for that to break, because a well-composed study
guide feels like a document rather than a view. The proof is not that composing
twice is deterministic, which a content-inventing function would also pass, but
that every string in a composed record appears in the canonical Markdown source.

Decisions already made, cited, and never re-derived here:

- **`16A-DECISIONS.md` `## D-16A-2`**: which module holds `compose_outline`.
  Under `option-a` it is `capabilities.py`.
- **`16A-RESEARCH.md`'s Don't Hand-Roll table**, the outline row:
  `graph.outline_projection(doc)` is the one projection where a course graph is
  in play.
- **`PLANNING-DIRECTIVES.md` section 3a**, the breadth-preservation and
  append-only rules, quoted above.
- **The phase-shape constraint on visual scope**: no color, spacing,
  typography, motion, or token decision anywhere in Phase 16A.

Purpose: prove two modes compose from one schema and keep the other eight alive.
Output: two composers, eight parked entries, and one derivation proof.
</objective>

<context>
@.planning/phases/16A-semantic-capability-activity-contract/16A-DECISIONS.md
@.planning/phases/16A-semantic-capability-activity-contract/16A-PRECONDITION.md
@.planning/phases/16A-semantic-capability-activity-contract/16A-RESEARCH.md
@.planning/phases/16A-semantic-capability-activity-contract/16A-PATTERNS.md
@.planning/phases/16A-semantic-capability-activity-contract/16A-VALIDATION.md
@.planning/REQUIREMENTS.md
@.planning/PLANNING-DIRECTIVES.md
@capabilities.py
@model.py
@tests/capability_stress_corpus_tracer.py
</context>

## Artifacts this phase produces (plan 16A-07 share)

New symbols introduced by this plan, and by nothing earlier:

- `capabilities.OUTPUT_MODES` (two-member tuple)
- `capabilities.BACKBURNER_MODES` (eight-member tuple)
- `capabilities.OUTPUT_MODE_KEYS` (five-member tuple)
- `capabilities.BACKBURNER_KEYS` (five-member tuple)
- `capabilities.compose_outline`, `capabilities.compose_glossary`
- `capabilities.backburner_entry`, `capabilities.backburner_catalog`
- `fixtures/lesson_capability_corpus.py`: `build_output_mode_lesson`
- `tests/capability_stress_corpus_tracer.py`: `scenario_output_modes`,
  `scenario_backburner_catalog`

No CLI command, no daemon route, and no schema file is produced by this plan.
No new canonical type is produced by this plan.

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: two composers over shared schemas, and the eight-entry backburner catalog</name>
  <files>capabilities.py</files>
  <read_first>
- `.planning/REQUIREMENTS.md` `CAP-03` in full, for the ten mode names in the
  order the requirement lists them, and its Degraded clause's four field names.
- `.planning/PLANNING-DIRECTIVES.md` section 3a in full, the breadth,
  append-only, and accepted-recommendation paragraphs.
- `capabilities.py` in full as it stands after plan 16A-06.
- `model.py` lines 469 to 566, `parse_lesson`, specifically the `headings` list
  and each entry's `text`, `slug`, and `body` keys, which are the outline's
  spine.
- `model.py` lines 625 to 711, `parse_terms`, specifically its returned
  `terms`, `refs`, `ignored`, `empty`, and `collisions` keys, which are the
  glossary's spine.
- `.planning/phases/14B-graph-course-package-prototype/14B-02-PLAN.md`, the
  "Artifacts this phase produces" section, for `graph.outline_projection`'s
  real signature and return shape as it landed. If plan 16A-01's precondition
  recorded a deviation for this function, read that deviation first and follow
  the landed signature, not the plan text.
- `16A-RESEARCH.md`'s Don't Hand-Roll table, the outline row, verbatim.
  </read_first>
  <behavior>
- `capabilities.OUTPUT_MODES` equals `("outline", "glossary")`.
- `capabilities.BACKBURNER_MODES` equals `("notebook_page", "cornell_notes",
  "concept_map", "formula_sheet", "timeline", "comparison_table",
  "study_guide", "source_extracted_notes")`.
- The union of `OUTPUT_MODES` and `BACKBURNER_MODES` has exactly ten members and
  covers CAP-03's ten named modes with no mode in both lists and none in
  neither.
- `OUTPUT_MODE_KEYS` equals `("mode", "title", "entries", "provenance",
  "derived_from")`.
- `BACKBURNER_KEYS` equals `("mode", "shared_primitive", "dependency", "cost",
  "trigger")`.
- `compose_outline(lesson, graph_doc=None)` returns a dict whose key set is
  exactly `OUTPUT_MODE_KEYS`, whose `mode` is `"outline"`, whose `entries` is a
  list of dicts each carrying `text`, `slug`, and `depth`, built from the
  lesson's `headings` list in document order, and whose `provenance` names the
  lesson's `source` path and states whether a course graph contributed.
- `compose_outline` with a `graph_doc` supplied prepends the objective spine
  returned by `graph.outline_projection(graph_doc)` and computes no objective
  ordering of its own; its `provenance` says a course graph contributed.
- `compose_outline(lesson)` called twice on the same lesson dict returns equal
  dicts. It reads no file and writes none.
- `compose_glossary(terms)` returns a dict whose key set is exactly
  `OUTPUT_MODE_KEYS`, whose `mode` is `"glossary"`, and whose `entries` is a
  list of dicts each carrying `term`, `slug`, and `definition`, built from
  `parse_terms`'s `terms` mapping sorted by slug so the glossary has a stable
  reading order.
- `compose_glossary(None)` and `compose_glossary` of an empty terms result both
  return a record with an empty `entries` list and a `provenance` stating no
  terms registry was present. Neither raises.
- `backburner_entry(entry)` returns a shallow copy when the entry's key set is
  exactly `BACKBURNER_KEYS` and every value is a non-empty string, and raises
  `CapabilityError` naming the offending field otherwise.
- `backburner_catalog()` returns a tuple of exactly eight entries, one per
  `BACKBURNER_MODES` member, each passing `backburner_entry`'s validation.
  </behavior>
  <action>
1. Add the four closed tuples to `capabilities.py`, beside the existing
   vocabularies, with the exact members listed in the behavior block.

   Add one comment above `BACKBURNER_MODES` stating that these eight are parked
   and not cut, citing `PLANNING-DIRECTIVES.md` section 3a's sentence: "A
   capability is not dropped merely because it is optional, expensive,
   specialized, or absent from the next wave."

2. Add `compose_outline(lesson, graph_doc=None)`. It is pure: no file read, no
   global, no side effect. Build `entries` from `lesson["headings"]` in document
   order, each entry carrying the heading's `text`, its `slug` as
   `parse_lesson` already computed it, and a `depth` of `1` because the shipped
   lesson grammar has one heading level under `## LESSON`. Do not recompute a
   slug and do not invent a second heading level.

   When `graph_doc` is not `None`, call `graph.outline_projection(graph_doc)`
   through a function-local import of `graph`, so `capabilities.py` gains no
   top-level dependency on a Phase 14B module, and prepend its result to
   `entries` in whatever shape it returns, normalized only enough to carry
   `text`, `slug`, and `depth`. Compute no objective ordering here. If the
   landed `outline_projection` returns entries lacking a slug, derive one
   through `model.lesson_slug` via a function-local import, and record that in
   the summary.

   `provenance` is a single sentence naming `lesson["source"]` and stating
   either `composed from the lesson headings alone` or
   `composed from the lesson headings and the course graph outline projection`.
   `derived_from` is the list of source identifiers the record was built from:
   the lesson source path, plus a course identifier when a graph contributed.

3. Add `compose_glossary(terms)`. Build `entries` from `terms["terms"]`, sorted
   by slug, each entry carrying the term's canonical text, its slug, and its
   definition exactly as `parse_terms` returned them. Do not re-extract a term
   from the lesson body and do not compute a second slug: `parse_terms` is the
   one term extractor and Phase 3.1 shipped it. `provenance` names the source
   and states that the entries came from the `## TERMS` registry.

   `compose_glossary(None)` returns the empty record described in the behavior
   block rather than raising, because a lesson with no glossary is a normal
   lesson and not an error.

4. Add `backburner_entry(entry)` and `backburner_catalog()`.
   `backburner_entry` validates the key set and the non-emptiness of every
   value, raising `CapabilityError` naming the field. `backburner_catalog`
   returns eight validated entries, one per `BACKBURNER_MODES` member.

   Write real content in all eight. Each `shared_primitive` names the existing
   or planned schema the mode would compose from, for example the lesson
   headings list, the terms registry, the activity registry, or the course
   graph's edges. Each `dependency` names what must land first, by phase or by
   symbol. Each `cost` is an honest sentence about what building it would take,
   not a number. Each `trigger` names the condition that would move the mode
   from backburner to registered, and no trigger may be the empty string or a
   vague phrase such as `when needed`; a trigger a reader cannot test is the
   same as no trigger.

5. Add one sentence to `capabilities.py`'s module docstring stating that an
   output mode record is derived and disposable, that the canonical Markdown
   stays complete with every derived view deleted, and that this is PORT-01's
   clause rather than a convention of this module.
  </action>
  <verify>
  <automated>python tests/output_mode_check.py</automated>
Create `tests/output_mode_check.py` as part of this task, following
`tests/evidence_roundtrip.py`'s convention (shebang, standard library only,
`ROOT` plus `sys.path.insert`, a local `fail(msg)`). It asserts: the four tuples
equal their documented members; the union of `OUTPUT_MODES` and
`BACKBURNER_MODES` has exactly ten members with no overlap; `compose_outline`
and `compose_glossary` on `fixtures/lesson_bank.md`'s parsed lesson and terms
return records whose key sets equal `OUTPUT_MODE_KEYS`; two consecutive calls to
each return equal dicts; `compose_glossary(None)` returns an empty-entries
record without raising; `backburner_catalog()` returns eight validated entries;
and `backburner_entry` raises `CapabilityError` naming `trigger` for an entry
whose trigger is the empty string. It prints `output modes ok` and exits 0 on
success.
The degraded state this task must also prove is the no-graph path:
`compose_outline(lesson)` with no `graph_doc` must return a record whose
`provenance` states the lesson headings alone, and must not import `graph` at
all on that path.
  </verify>
  <acceptance_criteria>
- `python tests/output_mode_check.py` prints `output modes ok` and exits 0.
- `python -c "import capabilities as C; print(C.OUTPUT_MODES, len(C.BACKBURNER_MODES), len(set(C.OUTPUT_MODES)|set(C.BACKBURNER_MODES)))"`
  prints exactly
  `('outline', 'glossary') 8 10`.
- `backburner_catalog()` returns eight entries, every one passing
  `backburner_entry`, and no entry's `trigger` value is the empty string or
  contains the phrase `when needed`.
- `grep -cE "^import graph|^from graph|^import model|^from model" capabilities.py`
  reports `0`, proving both imports stayed function-local.
- `grep -c "open(" capabilities.py` reports `0`.
- `grep -cE "^import (evidence|runtime)|^from (evidence|runtime)" capabilities.py`
  reports `0`.
- `python tests/capability_profile_check.py` exits 0.
- The two golden SHA-256 values in `16A-PRECONDITION.md` are unchanged.
- No em dash character appears in any line this task added.
  </acceptance_criteria>
  <reversibility rating="costly">`OUTPUT_MODES`, `BACKBURNER_MODES`, and the two
  record shapes become a published contract Phases 16B, 16C, and 17A read.
  Nothing authored depends on them yet, so a rename is a code change rather than
  a content migration, but the backburner catalog's eight entries are the
  breadth record this milestone is judged against.</reversibility>
  <done>Two modes compose from shared schemas, eight are parked with a testable
  route back, and no second outline generator exists.</done>
</task>

<task type="auto">
  <name>Task 2: the composition fixture and the derivation proof</name>
  <files>fixtures/lesson_capability_corpus.py, tests/capability_stress_corpus_tracer.py</files>
  <read_first>
- `.planning/REQUIREMENTS.md` `CAP-03`'s Fixture sentence, verbatim: "a 16A
  fixture composing two registered output modes (outline and glossary) from one
  stress-corpus lesson's shared schemas, plus one unregistered mode entry
  asserting it stays a backburner catalog record naming its primitive,
  dependency, cost, and trigger".
- `.planning/REQUIREMENTS.md` `PORT-01`, the clause "derived HTML, index, or
  cache is never the sole understandable copy", verbatim.
- `fixtures/lesson_capability_corpus.py` in full as it stands after plan
  16A-06.
- `tests/capability_stress_corpus_tracer.py` in full.
- `capabilities.py` as it stands after Task 1.
- `.planning/phases/16A-semantic-capability-activity-contract/16A-VALIDATION.md`.
  </read_first>
  <action>
1. Add `build_output_mode_lesson(dest_dir)` to
   `fixtures/lesson_capability_corpus.py`, following the established shape:
   literal fictional content, no `random`, deterministic bytes, no em dash
   characters.

   The generated bank carries a `## TERMS` registry with at least four rows and
   a `## LESSON` section with at least three `### ` headings, so both composers
   have real material. Every term definition and every heading text is a
   distinct fictional string, so the derivation assertion in step 3 has
   something to find rather than matching by accident on a common word.

2. Add `scenario_output_modes()` to
   `tests/capability_stress_corpus_tracer.py`. It builds the output-mode
   lesson, parses it with `model.parse_lesson` and `model.parse_terms`, composes
   both modes, and asserts:
   - Both records' key sets equal `capabilities.OUTPUT_MODE_KEYS`.
   - The outline's `entries` count equals the parsed lesson's heading count and
     its entry order equals the heading order.
   - The glossary's `entries` count equals the parsed terms count and its entry
     order is sorted by slug.
   - Each record's `provenance` is a non-empty string naming the lesson source.
   - Both composers are shared-schema readers rather than private extractors:
     assert every outline entry's `slug` equals the corresponding
     `parse_lesson` heading's `slug` value, and every glossary entry's `slug`
     equals the corresponding `parse_terms` key. A composer that recomputed a
     slug would drift here.

3. Add the derivation proof to the same scenario, which is CAP-03's probe row
   resolved:
   - Compose both records twice and assert the two pairs are equal, proving
     determinism.
   - Read the generated bank's raw bytes and assert that every heading `text`
     in the outline record and every `term` and `definition` in the glossary
     record appears as a substring of those bytes. This is the assertion that
     distinguishes a derived view from an invented one: a deterministic function
     that invented content would pass the first check and fail this one.
   - Delete every derived artifact the fixture produced, including any rendered
     HTML the scenario wrote to its temporary directory, recompose both records
     from the canonical Markdown alone, and assert the recomposed records equal
     the originals. That is PORT-01's rebuild clause executed literally.

4. Add `scenario_backburner_catalog()`. It asserts `backburner_catalog()`
   returns eight entries; that every entry's key set equals `BACKBURNER_KEYS`;
   that every value is a non-empty string; that no `trigger` contains the phrase
   `when needed`; that the union of `OUTPUT_MODES` and the catalog's modes has
   exactly ten members; and that `backburner_entry` raises `CapabilityError`
   naming `trigger` when given an otherwise valid entry whose trigger is the
   empty string. It then picks one specific unregistered mode by name,
   `concept_map`, and asserts its entry names a shared primitive, a dependency,
   a cost, and a trigger, which is CAP-03's Fixture sentence executed on a named
   mode rather than in aggregate.

5. Update `16A-VALIDATION.md`'s Per-Task Verification Map with two rows for plan
   16A-07's tasks, naming `tests/output_mode_check.py`,
   `scenario_output_modes`, and `scenario_backburner_catalog`, with a Status of
   `passing`.
  </action>
  <verify>
  <automated>python tests/capability_stress_corpus_tracer.py</automated>
Expected final line: `TRACER: 12 passed, 0 skipped, 0 failed`, exit code 0. The
degraded state this task must also prove is the rebuild clause: after deleting
every derived artifact the scenario produced, recomposing from the canonical
Markdown alone must reproduce equal records, and the canonical file's SHA-256
must be unchanged by the delete-and-rebuild cycle.
  </verify>
  <acceptance_criteria>
- `python tests/capability_stress_corpus_tracer.py` exits 0 with the final line
  `TRACER: 12 passed, 0 skipped, 0 failed`.
- Every heading text in the composed outline and every term and definition in
  the composed glossary appears as a substring of the canonical bank's raw
  bytes.
- The delete-and-rebuild cycle reproduces equal records and leaves the canonical
  file's SHA-256 unchanged.
- Every outline entry slug equals the corresponding `parse_lesson` heading slug,
  and every glossary entry slug equals the corresponding `parse_terms` key.
- `scenario_backburner_catalog` asserts on `concept_map` by name and its entry
  carries four non-empty fields.
- `for t in tests/*.py; do python "$t" || exit 1; done` exits 0.
- `python itembank.py guard .` reports `0 offending files`.
- The two golden SHA-256 values in `16A-PRECONDITION.md` are unchanged.
- `16A-VALIDATION.md` has two new filled rows naming plan `16A-07`.
- No em dash character appears in any line this task added.
  </acceptance_criteria>
  <reversibility rating="reversible">A fixture builder and two test scenarios.
  Both can be rewritten without migrating content or renaming a published
  surface.</reversibility>
  <done>Two output modes compose from one lesson's shared schemas, every string
  in them is proven to come from the canonical file, and eight parked modes
  carry a route back.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| composed record to canonical source | A composed outline or glossary reads like a document and is the most tempting place for a derived view to acquire content the canonical file does not have. |
| backburner catalog to breadth record | A parked capability with no testable trigger is functionally deleted while looking documented. |
| output-mode composer to shared schema | A composer that recomputes a slug or re-extracts a term becomes a second extractor that drifts from the one that ships. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-16A-07-01 | Repudiation | a derived view carrying content the canonical Markdown does not have, making it the only understandable copy | high | mitigate | Task 2 step 3 asserts every heading text, term, and definition in both composed records appears as a substring of the canonical bank's raw bytes, and asserts a delete-and-rebuild cycle reproduces equal records. Determinism alone would not catch an invented string; the substring check does. |
| T-16A-07-02 | Repudiation | a capability parked with an untestable trigger, turning breadth preservation into silent cutting | high | mitigate | `backburner_entry` raises `CapabilityError` on any empty field, and the acceptance criteria assert no trigger contains the vague phrase `when needed`. The freeze-gate human review in plan 16A-10 reads the eight triggers for whether they are genuinely testable, which is the part a grep cannot check. |
| T-16A-07-03 | Tampering | a second outline generator drifting from `graph.outline_projection` | high | mitigate | `compose_outline` delegates the objective spine and computes no objective ordering, and its lesson spine reads `parse_lesson`'s already-computed slugs rather than recomputing them; the tracer asserts slug equality against both source functions. |
| T-16A-07-04 | Spoofing | a mode falling out of both the registered and the backburner list and vanishing without notice | medium | mitigate | The tracer asserts the union of `OUTPUT_MODES` and `BACKBURNER_MODES` has exactly ten members with no overlap, so a mode removed from one list without being added to the other fails immediately. |
| T-16A-07-05 | Elevation of Privilege | a composer reaching a disclosure or scoring decision | high | mitigate | Both composers are pure functions over already parsed data, and `capabilities.py` still imports neither `runtime` nor `evidence`, asserted by grep in the acceptance criteria. A glossary entry's definition comes from `parse_terms`, and `runtime.glossable`'s suppression gate remains the only thing deciding whether a definition reaches a learner in the reader. |
| T-16A-07-06 | Information Disclosure | real course content entering the repository through the output-mode fixture | high | mitigate | Every string in `build_output_mode_lesson` is a literal fictional constant with no `random` and no external read; `python itembank.py guard .` reporting `0 offending files` is an acceptance criterion. |
| T-16A-07-07 | Tampering | supply chain: a third-party dependency introduced by this plan | high | mitigate | None is added; every change is standard library only. Per `PLANNING-DIRECTIVES.md` section 4a the absence of dependencies is explicitly not the mitigation: the mitigation is that any dependency ever added here is vendored at a pinned version with a recorded checksum and a named license review, following the KaTeX precedent in `09-03-PLAN.md`. |
</threat_model>

<out_of_scope>
Refused by this plan, by name, so no adjacent temptation is decided by executor
judgment:

- Building any of the eight backburner modes. They are catalogued with a
  primitive, a dependency, a cost, and a trigger, and building one is the work
  its trigger names, in the phase its dependency names.
- A second outline generator, an objective ordering computed inside
  `capabilities.py`, or any recomputation of a heading slug or a term slug.
- A rendered HTML surface for either output mode. An output mode is a record in
  this phase; a surface that displays one is Phase 16B's or 17A's.
- A CLI command or a daemon route for either mode. Neither is a runtime
  capability in this phase and neither has a learner-facing surface yet.
- Any new canonical type. CAP-03 permits one only when validation or behavior
  genuinely differs, and neither registered mode's does.
- Any change to `model.parse_terms`, `model.parse_lesson`, or
  `graph.outline_projection`. This plan reads all three and changes none.
- The localization fixture set and the adversarial suite. Plans 16A-08 and
  16A-09 own them.
</out_of_scope>

<flagged_assumptions>
- **CAP-03's probe row, returned by the edge-coverage probe as `unclassified`,
  is classified by this plan as a derivation question** and resolved explicitly:
  can an output mode become the only understandable copy. The acceptance
  criterion is carried in `must_haves.truths` as the substring proof plus the
  delete-and-rebuild proof. The classification and its reason are recorded in
  `16A-DECISIONS.md`'s Probe classification note by plan 16A-01.
- **Outline and glossary were chosen as the two registered modes because both
  already have a shared primitive**, not because they are the most valuable of
  the ten. `parse_terms` ships and `parse_lesson`'s headings ship, so composing
  them proves the composition claim without first building a note schema. The
  choice is recorded here so a later reader does not infer a value judgment
  about the other eight.
- **`depth` is always `1` in an outline entry built from a lesson.** The shipped
  lesson grammar has one heading level under `## LESSON`, so a second depth
  would be invented. The field exists because a graph-contributed spine can
  carry more than one level, and the constant lesson value is recorded rather
  than left to be discovered as odd.
</flagged_assumptions>

<summary_obligations>
`16A-07-SUMMARY.md` records: the two registered mode names and the eight
backburner mode names as written; all eight backburner entries in full, with
their primitive, dependency, cost, and trigger, since they are this milestone's
breadth record; `graph.outline_projection`'s landed signature and return shape
as actually found, and whether a slug had to be derived for its entries; the
result of the substring derivation proof and of the delete-and-rebuild cycle;
the tracer's final summary line verbatim; the two golden SHA-256 values as
re-verified; which truth was verified by which command with the command's actual
stdout; and any deviation from this plan with its reason.
</summary_obligations>

<output>
Create
`.planning/phases/16A-semantic-capability-activity-contract/16A-07-SUMMARY.md`
when done.
</output>
