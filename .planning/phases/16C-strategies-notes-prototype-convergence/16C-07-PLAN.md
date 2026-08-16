---
phase: 16C-strategies-notes-prototype-convergence
plan: 07
type: execute
wave: 4
depends_on: ["16C-02", "16C-03", "16C-06"]
files_modified:
  - note_outputs.py
  - tests/note_trio_roundtrip.py
  - fixtures/note_strategy_corpus.py
autonomous: true
requirements: [NOTE-01, NOTE-02, STRATEGY-01]
estimate:
  tokens: 80000
  raw_tokens: 80000
  tasks: 3
  confidence: low
must_haves:
  truths:
    - "The note-output trio (notebook page, Cornell notes, concept map) is three validated projections of one content instance parsed once by the one parser: parse_lesson and parse_terms are each called exactly once per instance, proven by a call-counting wrapper, with zero re-parsing and zero per-style content forks."
    - "Each mode's validator fails meaningfully on its deliberately broken fixture: a cue without notes, an unlabelled edge, and an anchor to a moved block each produce a named failure in the validator's own words, never a generic error."
    - "Each output degrades to coherent plain Markdown: the notebook page with role labels and provenance as plain text, Cornell linearized cues-then-notes-then-summary, the concept map as textual adjacency lines; a validator failure renders the locked refusal sentence followed by the plain form, so content is never lost or blocked."
    - "Prototype A holds: an interrupted guided-note-spine pass loses no note draft, every note block returns to its source anchor, and no answer key appears anywhere in any projection."
    - "Prototype B holds: a wrong worked-reasoning explanation stays a learner claim and cannot seed a key; it renders under its role label and never enters an accepted or keyed output."
    - "Prototype C holds: provenance relocation distinguishes exact, probable-requires-confirmation, and orphan recovery, and a note document survives export and reimport without losing ownership."
  prohibitions:
    - statement: "No second parser, second renderer, or second content truth: projections consume the parsed dicts and declared relations only, and no projection re-reads the bank file."
      status: kept
      verification: flagged-unverified
    - statement: "No output mode beyond the trio registers in this phase; the remaining seven modes and genre styles wait for the trio to pass (STYLE-DISCIPLINE binding order)."
      status: kept
      verification: flagged-unverified
    - statement: "No hover-only meaning and no drag-only construct: the concept map's accessible form IS the textual adjacency structure, and nothing renders that the plain form does not carry."
      status: kept
      verification: flagged-unverified
  artifacts:
    - "note_outputs.py with OUTPUT_MODES, MODE_NAMES, NOTE_OUTPUT_CHECKS, VALIDATOR_FAILURE_COPY, TEXTUAL_FALLBACK_LINE, content_instance, validate_mode, the three projections, and render_mode"
    - "fixtures/note_strategy_corpus.py gains broken_trio_fixtures"
    - "tests/note_trio_roundtrip.py green including scenario_a, scenario_b, and scenario_c"
  key_links:
    - "content_instance is the single seam between the parser and every projection; the parse-once proof counts calls through this function, so any projection that reads a file bypasses the proof and fails the ast scan."
    - "The concept map's edges come only from [[term]] refs plus the fixture's declared typed relations (D-16C-7); an inline edge grammar would be a second parser."
    - "The anchor checks reuse notes.resolve_anchor and notes.hash_quoted_context from 16C-02; a second relocation rule here would drift from the note schema's."
    - "The refusal copy is the D11 sentence with the failing check in the validator's own words; the three broken fixtures assert those exact words so the refusal can never go generic."
---

<objective>
Prove the trio: notebook page, Cornell notes, and concept map as three
validated projections of one parse, with meaningful validator failures,
plain-Markdown degradation, and the three prototype tracers
PLANNING-DIRECTIVES section 3a requires before the strategy registry
freezes.

Decisions already made, cited, and never re-derived here:

- **16C-DECISIONS.md `## D-16C-7`**: the one parsed content instance is the
  `parse_lesson` plus `parse_terms` pair; typed relations are fixture data;
  anchors are heading slugs today.
- **16C-DECISIONS.md `## D11` (UI-SPEC)**: the validator-failure refusal
  sentence and its `--warn` presentation, following the shipped
  `RENDER_REFUSAL_COPY` precedent.
- **STYLE-DISCIPLINE-16A-2026-08-14.md** (binding order): the trio's three
  validator foci (notebook: ownership, anchors, provenance; Cornell: every
  cue maps to notes, linear degradation; concept map: every edge typed,
  textual adjacency fallback); the prototype-before-long-tail rule; the
  one-parse proof requirements quoted in the tasks below.
- **16C-UI-SPEC.md Note-Output Trio Render Target Contract**: the per-mode
  required content and degradations, transcribed into the projections.
- **PLANNING-DIRECTIVES.md section 3a**: the guided-note, worked-reasoning,
  and provenance-relocation pathways are prototyped before the strategy
  registry freezes; report 12 section 12's A, B, and C success gates are the
  tracer assertions.

Purpose: the gate on the entire output-mode long tail; nothing beyond the
trio registers until this passes.
Output: one projection module, three broken fixtures, one green test with
three prototype tracers.
</objective>

<context>
@.planning/phases/16C-strategies-notes-prototype-convergence/16C-DECISIONS.md
@.planning/phases/16C-strategies-notes-prototype-convergence/16C-UI-SPEC.md
@.planning/phases/16C-strategies-notes-prototype-convergence/16C-RESEARCH.md
@.planning/STYLE-DISCIPLINE-16A-2026-08-14.md
@model.py
@notes.py
@strategies.py
@fixtures/note_strategy_corpus.py
@tests/note_schema_roundtrip.py
</context>

## Artifacts this phase produces (plan 16C-07 share)

New symbols introduced by this plan, and by nothing earlier:

- `note_outputs.py`: `OUTPUT_MODES`, `MODE_NAMES`, `NOTE_OUTPUT_CHECKS`,
  `VALIDATOR_FAILURE_COPY`, `TEXTUAL_FALLBACK_LINE`, `RELATION_TYPES`,
  `content_instance`, `validate_mode`, `project_notebook_page`,
  `project_cornell`, `project_concept_map`, `render_mode`.
- `fixtures/note_strategy_corpus.py`: `broken_trio_fixtures`.
- `tests/note_trio_roundtrip.py` with its `check_*` and `scenario_*`
  functions.

The phase-wide symbol union is repeated in `16C-01-PLAN.md`.

<tasks>

<task type="auto">
  <name>Task 1: one parse, three projections, plain degradation</name>
  <files>note_outputs.py, tests/note_trio_roundtrip.py</files>
  <read_first>
- `STYLE-DISCIPLINE-16A-2026-08-14.md`, "Prototype before the long tail" in
  full: the four proof bullets are this task's and Task 2's acceptance
  frame.
- `16C-UI-SPEC.md`, the trio render-target table: rich content, plain
  degradation, and failure focus per mode.
- `model.py` `parse_lesson` (line 469) and `parse_terms` (line 625) return
  shapes; `notes.py` `hash_quoted_context`, `resolve_anchor`,
  `ANCHOR_STATE_LABELS`.
- `fixtures/note_strategy_corpus.py`: `build_subject_bank`,
  `typed_relations`, `build_note_set`.
  </read_first>
  <action>
1. Create `note_outputs.py` at the repository root, importing `model` and
   `notes` only (stdlib aside). It must not import `runtime`, `evidence`,
   or anything from `surfaces/`. Module docstring: a semantic style is a
   validator plus a projection over the one parsed content model
   (STYLE-DISCIPLINE corollary, quoted); this module never opens the bank
   file itself.

2. Define:

```
OUTPUT_MODES = ("notebook_page", "cornell_notes", "concept_map")
MODE_NAMES = {"notebook_page": "Notebook page",
              "cornell_notes": "Cornell notes",
              "concept_map": "Concept map"}
RELATION_TYPES = ("part_of", "causes", "contrasts_with", "requires")
VALIDATOR_FAILURE_COPY = "The {mode} view can't be built from this content: {check}. Showing plain Markdown instead."
TEXTUAL_FALLBACK_LINE = "relates to {node}: {relation}"
```

   The two copy strings are the UI-SPEC rows verbatim (the fallback line is
   the documented pattern with named placeholders).

3. Define `content_instance(lesson, terms, relations, notes_list)`: takes
   the dict `parse_lesson` returned, the dict `parse_terms` returned, the
   declared typed relations, and the learner notes; returns one instance
   dict `{"lesson": ..., "terms": ..., "relations": ..., "notes": ...}`.
   This function is the only entry to every projection; it reads no file
   and calls no parser; the caller parses once and passes the dicts in. A
   comment cites D-16C-7.

4. Define the three projections, each taking the instance and returning a
   plain-Markdown string, each also serving as its own degraded form (the
   rich layer is 17A's; this text IS the contract):
   - `project_notebook_page(instance)`: the learner's notes in document
     order under their anchored headings; every block prefixed with its
     epistemic role label (the `CAPTURE_COPY["role_choices"]` word for its
     role); every anchored block carrying a provenance line with the
     anchor's state label from `notes.ANCHOR_STATE_LABELS` and its locator
     as plain text, basename only for any path; ownership always visible
     (the owner marker on each block). Coherent as a standalone Markdown
     document.
   - `project_cornell(instance)`: linear degradation per the UI-SPEC: each
     cue as a heading (cues derive from the notes marked `learner_question`
     plus each anchored heading's title), that cue's notes as body text
     beneath, and a `## Summary` region last built from the notes marked
     `learner_claim`. Reads coherently top to bottom.
   - `project_concept_map(instance)`: textual adjacency: each node (term
     canonical names plus heading titles referenced by relations) as a
     heading followed by one `TEXTUAL_FALLBACK_LINE` per edge with `{node}`
     and `{relation}` substituted. Edges come only from the instance's
     `relations` plus `[[term]]` refs (a ref yields a `requires` edge from
     its enclosing heading to the term); no other edge source exists.

5. Create `tests/note_trio_roundtrip.py` in the shipped shape with a local
   `fail(msg)`. First checks:
   - `check_parse_once`: wrap `model.parse_lesson` and `model.parse_terms`
     with counting wrappers (assign counting functions over the module
     attributes inside the test, restore after); build one corpus bank in a
     temp dir; call each parser exactly once; build the instance; render
     all three projections twice each; assert both counters still read 1.
     This is the STYLE-DISCIPLINE proof bullet: all three outputs are
     projections of one parse, zero re-parsing.
   - `check_no_content_fork`: render all three projections from the same
     instance, then mutate one note's wording in a copy of the instance and
     re-render: assert every projection reflects the same single source
     (the original three contain the original wording; the copies contain
     the changed wording; no projection caches or forks).
   - `check_plain_coherence`: each projection's output parses as
     non-empty text whose first line is a Markdown heading, contains at
     least one role label (notebook), the `## Summary` heading (Cornell),
     and at least four `relates to` lines (concept map); and contains no
     HTML tag (the plain form is Markdown, not markup).
   - `check_no_file_reads`: via `ast` over `note_outputs.py`, assert no
     `open(` call and no import of `runtime`, `evidence`, or `surfaces`.
   - `main()` prints `NOTE TRIO: 4 passed, 0 failed`.

6. Run:

```
python tests/note_trio_roundtrip.py
python tests/lesson_roundtrip.py
```

   Expected: final line `NOTE TRIO: 4 passed, 0 failed`, exit 0; then exit
   0 (the shipped lesson suite is the regression net because the trio reads
   lesson parsing).

   No em dash characters in any file this task writes.
  </action>
  <verify>
  <automated>python tests/note_trio_roundtrip.py && python tests/lesson_roundtrip.py</automated>
Expected: `NOTE TRIO: 4 passed, 0 failed` then exit 0. The degraded state
this task proves is plain coherence: every projection is a coherent
standalone Markdown document with no rich layer present at all.
  </verify>
  <acceptance_criteria>
- `python tests/note_trio_roundtrip.py` exits 0 with final line
  `NOTE TRIO: 4 passed, 0 failed`.
- The parse counters read exactly 1 each after six renders.
- Each projection meets its structural assertions and contains no HTML tag.
- `note_outputs.py` opens no file and imports only model and notes beyond
  stdlib.
- No file this task writes contains an em dash character, verified with the
  `chr(0x2014)` form.
  </acceptance_criteria>
  <reversibility rating="reversible">Pure projections over parsed dicts;
  deleting the module removes the trio without touching the parser or the
  note store.</reversibility>
  <done>Three projections of one parse exist, each coherent as plain
  Markdown, with re-parsing structurally absent.</done>
</task>

<task type="auto">
  <name>Task 2: three validators, three broken fixtures, one refusal shape</name>
  <files>note_outputs.py, fixtures/note_strategy_corpus.py, tests/note_trio_roundtrip.py</files>
  <read_first>
- `STYLE-DISCIPLINE-16A-2026-08-14.md`, the note-output validator-focus
  table rows for the three modes.
- `16C-DECISIONS.md` `## D11`, the refusal presentation.
- `model.py` `STYLE_CHECK_CATALOGUE` (line 2250), the closed-catalogue
  shape `NOTE_OUTPUT_CHECKS` copies.
- `surfaces/lesson.py` line 86 area, `RENDER_REFUSAL_COPY`, the shipped
  refusal precedent named by D11.
  </read_first>
  <action>
1. Add to `note_outputs.py` the closed check catalogue, the
   `STYLE_CHECK_CATALOGUE` shape:

```
NOTE_OUTPUT_CHECKS = {
    "note_output.ownership_missing": "error",
    "note_output.anchor_moved": "error",
    "note_output.provenance_missing": "error",
    "note_output.cue_without_notes": "error",
    "note_output.edge_untyped": "error",
}
```

   with the comment that adding a check is a code change here; no style or
   fixture file can add one.

2. Add `validate_mode(mode, instance, headings)`: returns a list of failure
   dicts `{"code": ..., "check": <the failing check in the validator's own
   words>}`. The three foci, exactly:
   - `notebook_page`: every note block carries a non-empty owner
     (`ownership_missing`, words `a note block has no owner`); every
     anchored note's `resolve_anchor` state against `headings` is
     `resolved` or `relocated_exact` (`anchor_moved`, words
     `an anchor points to a block that moved`); every anchored block
     carries a locator (`provenance_missing`, words
     `an anchored block has no locator`).
   - `cornell_notes`: every cue maps to at least one note
     (`cue_without_notes`, words `a cue has no matching notes`).
   - `concept_map`: every edge's relation type is a member of
     `RELATION_TYPES` (`edge_untyped`, words `a relation has no type`).

3. Add `render_mode(mode, instance, headings)`: runs the validator; on an
   empty failure list returns `{"ok": True, "text": <the projection>}`; on
   failures returns `{"ok": False, "copy": VALIDATOR_FAILURE_COPY with
   {mode} replaced by MODE_NAMES[mode] and {check} by the first failure's
   words, "text": <the projection anyway>}`. The content always renders in
   plain form; the refusal names what it cannot do and why (D11; derived
   views never become the only understandable copy).

4. Add `broken_trio_fixtures(dest_dir)` to
   `fixtures/note_strategy_corpus.py`: builds one bank and returns three
   deliberately broken instances beside the good one:
   - a Cornell case with one cue whose notes list is empty;
   - a concept-map case with one edge carrying relation type `"related"`
     (outside `RELATION_TYPES`);
   - a notebook case whose note anchors a heading that `revise_lesson`
     then moved.

5. Extend `tests/note_trio_roundtrip.py`:
   - `check_validators_fail_meaningfully`: for each broken fixture, the
     matching mode's `validate_mode` returns exactly the expected code, and
     `render_mode` returns `ok` False with copy exactly, for example:
     `The Cornell notes view can't be built from this content: a cue has no
     matching notes. Showing plain Markdown instead.` (assert all three
     full sentences), while `text` still carries the plain projection.
   - `check_good_instance_passes`: the unbroken instance validates clean in
     all three modes and `render_mode` returns `ok` True.
   - Update `main()` to run six checks and print
     `NOTE TRIO: 6 passed, 0 failed`.

6. Run:

```
python tests/note_trio_roundtrip.py
python itembank.py guard .
```

   Expected: `NOTE TRIO: 6 passed, 0 failed`, exit 0; `0 offending files`.

   No em dash characters in any file this task writes.
  </action>
  <verify>
  <automated>python tests/note_trio_roundtrip.py && python itembank.py guard .</automated>
Expected: `NOTE TRIO: 6 passed, 0 failed` then `0 offending files`. The
degraded state this task proves is the refusal path: a failing validator
yields the locked sentence naming the check in its own words, followed by
the still-readable plain Markdown, never a blank and never a generic error.
  </verify>
  <acceptance_criteria>
- `python tests/note_trio_roundtrip.py` exits 0 with final line
  `NOTE TRIO: 6 passed, 0 failed`.
- Each broken fixture fails exactly its own check with the exact sentence;
  the good instance passes all three.
- `NOTE_OUTPUT_CHECKS` is closed at five codes and severities are declared
  in code.
- `python itembank.py guard .` reports `0 offending files`.
- No file this task writes contains an em dash character, verified with the
  `chr(0x2014)` form.
  </acceptance_criteria>
  <reversibility rating="reversible">Validators and fixtures; the catalogue
  is additive by construction.</reversibility>
  <done>Each mode can fail, fails in its own words, and never takes the
  content down with it.</done>
</task>

<task type="auto">
  <name>Task 3: prototype tracers A, B, and C</name>
  <files>tests/note_trio_roundtrip.py</files>
  <read_first>
- `16C-RESEARCH.md` Open Question 7 and its recommendation: the three
  tracers and their success gates from report 12 section 12.
- `notes.py`: `write_note_document`, `read_note_document`,
  `resolve_anchor`, `request_review`, `review_promotion`.
- `strategies.py`: `strategy_contract("guided_note_spine")` and
  `strategy_contract("worked_reasoning")`, whose `tests` fields name this
  file.
- `fixtures/note_strategy_corpus.py` as extended by Task 2.
  </read_first>
  <action>
1. Add `scenario_a_guided_note_spine()`: drive a guided-note-spine pass
   over one corpus bank in a temp dir: create three note drafts anchored to
   three headings, writing the note document after each via
   `write_note_document`; simulate an interruption by planting a corrupt
   `notes.md.json.tmp` after the second write and re-reading; assert (gate
   A): no note draft is lost (the last accepted document carries both
   written notes), every note block in `project_notebook_page` returns to
   its source (its provenance line carries a resolvable anchor whose state
   is `resolved`), and no answer key appears in any projection: render all
   three modes and assert the corpus bank's `CORRECT:` answer strings and
   the literal marker `CORRECT:` are absent from every output.
2. Add `scenario_b_worked_reasoning()`: create a note with role
   `learner_claim` carrying a deliberately wrong invented explanation of
   the CS off-by-one subject; assert (gate B): it renders in the notebook
   page under the `My claim` label; `review_promotion` with its claim
   unsourced blocks with the source-check sentence at N=1; and no path
   marks it correct: it appears in no derived record and scanning every
   projection finds no verdict marker (assert the strings `correct` and
   `verdict` absent from its rendered block, lowercase comparison scoped to
   the block).
3. Add `scenario_c_provenance_relocation()`: anchor three notes; then (a)
   rename one heading keeping its body (assert `relocated_exact` with one
   candidate), (b) revise another heading's body keeping its title (assert
   `relocated_probable` and that nothing auto-applies: the stored sidecar
   is unchanged until an explicit confirm step rewrites it through
   `write_note_document`), (c) delete the third heading (assert `orphaned`
   and the note still lists its objective, orphan recovery per NOTE-01);
   then export and reimport: copy the note document pair to a second temp
   directory byte-for-byte, `read_note_document` there, and assert every
   note's `owner` survives unchanged (gate C: export and reimport without
   losing ownership).
4. Update `main()` to run nine checks and print
   `NOTE TRIO: 9 passed, 0 failed`. Run:

```
python tests/note_trio_roundtrip.py
python tests/note_schema_roundtrip.py
python tests/note_promotion_roundtrip.py
```

   Expected: `NOTE TRIO: 9 passed, 0 failed` and exit 0 from all three.

   No em dash characters in any file this task writes.
  </action>
  <verify>
  <automated>python tests/note_trio_roundtrip.py</automated>
Expected: final line `NOTE TRIO: 9 passed, 0 failed`, exit 0. The degraded
state this task proves is interruption safety: a corrupt temp file after
the second write leaves both accepted notes readable and anchored, which is
prototype A's no-note-loss gate.
  </verify>
  <acceptance_criteria>
- `python tests/note_trio_roundtrip.py` exits 0 with final line
  `NOTE TRIO: 9 passed, 0 failed`.
- Gate A: no draft lost, every block returns to source, no key and no
  `CORRECT:` marker in any projection.
- Gate B: the wrong explanation stays a labeled learner claim, blocks at
  promotion with N=1, and carries no verdict.
- Gate C: exact, probable-without-auto-apply, and orphan states all
  exercised; ownership survives export and reimport byte-for-byte.
- No file this task writes contains an em dash character, verified with the
  `chr(0x2014)` form.
  </acceptance_criteria>
  <reversibility rating="reversible">Test scenarios only.</reversibility>
  <done>The three pathways PLANNING-DIRECTIVES section 3a requires are
  prototyped with their report 12 success gates asserted, clearing the
  registry to freeze at 16C-09.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| parser to projections | A projection that re-reads the file forks content truth. |
| keyed bank content to note outputs | The projections read the same file that carries keys; a key leaking into a note output would breach assessment disclosure. |
| learner claim to rendered authority | A wrong claim rendered without its role label reads as fact. |
| rich render to plain form | If the rich form carried meaning the plain form lacks, the derived view would become the only understandable copy. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-16C-07-01 | Information Disclosure | an answer key leaking into a note projection | critical | mitigate | Scenario A scans every projection for the bank's answer strings and the CORRECT: marker; the projections consume only lesson, terms, relations, and notes, never item dicts. |
| T-16C-07-02 | Tampering | a second parse forking content truth | high | mitigate | The counting-wrapper proof asserts one call per parser across six renders, and the ast scan asserts no open( call in note_outputs.py. |
| T-16C-07-03 | Spoofing | a learner claim rendering as settled fact | high | mitigate | Every block carries its role label; scenario B asserts the wrong claim stays labeled, blocks at promotion, and carries no verdict marker. |
| T-16C-07-04 | Repudiation | a validator failure hiding content behind a generic error | medium | mitigate | render_mode always returns the plain text beside the locked refusal sentence naming the check in its own words. |
| T-16C-07-05 | Tampering | a guessed relocation silently rewriting provenance | high | mitigate | Scenario C asserts the sidecar is unchanged after a probable relocation until an explicit confirm rewrites it through the atomic writer. |
| T-16C-07-06 | Tampering | supply chain: a third-party dependency introduced by this plan | high | mitigate | None is added; stdlib only. Per PLANNING-DIRECTIVES section 4a, any future dependency is vendored at a pinned version with a recorded checksum and a named license review. |
</threat_model>

<out_of_scope>
Refused by this plan, by name:

- No fourth output mode, no genre style, no glossary, outline, formula
  sheet, timeline, comparison table, study guide, or source-extracted
  notes; the long tail registers only after the trio passes, one validator
  and one representative fixture each (STYLE-DISCIPLINE backburner rule).
- No graphic concept-map rendering, no SVG, no interactive traversal; the
  textual adjacency structure is the 16C contract and any richer 17A
  graphic must keep it as the accessible equivalent.
- No HTML output and no route; the projections are plain Markdown.
- No new inline grammar for relations, cues, or anchors.
- No trio registration into the 16A capability registry; the registration
  seam is precondition-gated and recorded in the freeze, not wired here.
</out_of_scope>

<flagged_assumptions>
- **Cue derivation (learner questions plus anchored heading titles) is this
  plan's concrete rule for the Cornell projection.** The UI-SPEC fixes the
  scaffold and the validator focus, not the cue source; the rule is data
  visible in the projection and revisable without touching the validator.
- **The `[[term]]`-ref edge type defaulting to `requires` is this plan's
  concrete rule.** Declared relations carry their own types; a reviewer may
  re-map the default in a later plan without a parser change.
- **The parse-counting wrapper mutates module attributes inside the test
  and restores them**; if a landed test-runner constraint forbids that, the
  fallback is a subprocess counting via a sitecustomize shim, and the
  executor records the deviation.
</flagged_assumptions>

<summary_obligations>
`16C-07-SUMMARY.md` records: the final line of every verify command with
actual stdout; the parse-counter values after six renders; all three refusal
sentences as rendered, quoted; each prototype gate's result with the
specific assertion evidence (which strings were scanned for the key check,
which states scenario C produced); and any deviation from this plan with
its reason.
</summary_obligations>

<output>
Create
`.planning/phases/16C-strategies-notes-prototype-convergence/16C-07-SUMMARY.md`
when done.
</output>
