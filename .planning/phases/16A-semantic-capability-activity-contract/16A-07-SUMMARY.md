# 16A-07 summary: two composed output modes, eight parked with a route back, and one derivation proof

**Executed 2026-08-28.** Darwin arm64, Python 3.14.6. Plan
`16A-07-PLAN.md`, two tasks, both complete.

Output: two composers over shared schemas, an eight-entry backburner catalog
whose every entry carries a testable trigger, and the proof that a composed view
carries nothing the canonical Markdown does not.

---

## 1. The four closed tuples as written

```python
OUTPUT_MODES = ("outline", "glossary")

BACKBURNER_MODES = ("notebook_page", "cornell_notes", "concept_map",
                    "formula_sheet", "timeline", "comparison_table",
                    "study_guide", "source_extracted_notes")

OUTPUT_MODE_KEYS = ("mode", "title", "entries", "provenance", "derived_from")

BACKBURNER_KEYS = ("mode", "shared_primitive", "dependency", "cost",
                   "trigger")
```

```
$ python -c "import capabilities as C; print(C.OUTPUT_MODES, len(C.BACKBURNER_MODES), len(set(C.OUTPUT_MODES)|set(C.BACKBURNER_MODES)))"
('outline', 'glossary') 8 10
```

Ten modes, no overlap, none in neither list. Both the unit check and the tracer
assert that union, because a mode that fell out of both lists would vanish with
nothing noticing, which is the silent omission
`PLANNING-DIRECTIVES.md` section 3a forbids.

## 2. How the outline delegates rather than reimplements

`compose_outline(lesson, graph_doc=None)` builds its entries from
`lesson["headings"]`, using each heading's own `text` and the `slug`
`parse_lesson` already computed. **No slug is recomputed.** A composer that
computed a second one would drift from every anchor, every `[LESSON-REF:]`, and
every `[!CHECK:]` in the tree. `depth` is `1` for every lesson heading because
the shipped grammar has exactly one heading level under `## LESSON`.

With a `graph_doc` supplied, the objective spine comes from
`graph.outline_projection` through `_graph_outline_entries`, and this module
computes no objective ordering of its own. That is the Don't Hand-Roll row
executed: a private walk of the graph here would be the duplicated-truth pattern
CAP-03 rejects by name.

**Deviation on the landed signature, recorded because the plan told me to.**
Plan 16A-07 Task 1 step 2 says to "prepend its result to `entries` in whatever
shape it returns, normalized only enough to carry `text`, `slug`, and `depth`",
and adds "If the landed `outline_projection` returns entries lacking a slug,
derive one through `model.lesson_slug`". The landed
`graph.outline_projection(doc)` at `graph.py:510` returns **the course as a
plain Markdown string**, not a list of records at all: its own docstring says
"The course as plain Markdown, in authored order. This is a projection and never
a second source of truth." So the normalization reads that string's heading
lines, takes each heading's text and its `#` count as the depth, and derives the
slug through `model.lesson_slug` exactly as the plan's fallback branch
instructs. Both `graph` and `model` are imported inside the function, so
`capabilities.py` gains no top-level dependency on a Phase 14B module.

```
$ grep -cE "^import graph|^from graph|^import model|^from model" capabilities.py
0
$ grep -c "open(" capabilities.py
0
$ grep -cE "^import (evidence|runtime)|^from (evidence|runtime)" capabilities.py
0
```

`compose_glossary` reads `model.parse_terms`'s `terms` mapping, sorted by slug
so the glossary has one stable reading order regardless of authored row order.
A term is never re-extracted from the lesson body: `parse_terms` is the one term
extractor and has been since Phase 3.1.

## 3. The eight parked modes and their triggers

Every entry carries a shared primitive, a dependency, an honest cost sentence,
and a trigger a reader can test. None says `when needed`, and both the unit
check and the tracer assert that phrase is absent.

| Mode | Trigger |
|---|---|
| `notebook_page` | Phase 16B lands a durable reading position and the learner-note object has a recorded source of truth |
| `cornell_notes` | a learner note has a source of truth and an accepted-revision path, so the summary band cannot silently become the lesson |
| `concept_map` | Phase 17A has a component foundation and an accessible node-and-edge traversal has passed the authored-output accessibility review |
| `formula_sheet` | a lesson can declare what a symbol means in a form `parse_terms` or a successor can read |
| `timeline` | a structured date or effective-period field lands with 15B's staleness machinery, which is the phase `D-16A-7` names |
| `comparison_table` | the first time a real lesson needs a comparison a reader reads rather than answers |
| `study_guide` | a per-objective evidence read is available to a composer and Phase 15A's treatment policy can say what to study next |
| `source_extracted_notes` | the subphase that owns rights enforcement can re-check a quote grant live at the moment of extraction, which is the discipline `D-16A-8` already names |

Two of the eight are worth calling out because their entries say something a
reader would not guess:

- **`comparison_table`'s dependency is "None that is missing."** It is
  unregistered because two registered modes were enough to prove the
  composition claim, not because it is blocked. Its cost is the smallest of the
  eight and its trigger is "the first thing to try after Phase 16A freezes".
  Recording that honestly is the difference between a parked capability and one
  that looks harder than it is.
- **`source_extracted_notes`'s blocker is authority, not code.** Extracting a
  note from a source is exactly the operation `D-16A-8` says 16A declares and
  does not enforce, so its trigger names the rights-enforcement subphase rather
  than a rendering milestone.

`backburner_entry` refuses an entry missing any of the five fields, naming the
field. The unit check exercises all five, not just `trigger`, and also refuses
an entry carrying an extra key. The reason the refusal exists at all is the
trigger: a parked capability with a primitive, a dependency, and a cost but no
revisit condition looks documented and is functionally deleted.

## 4. The derivation proof

`scenario_output_modes` runs three checks in order, and only the third is worth
much on its own.

1. **Determinism.** Composing both records twice returns equal dicts.
2. **Derivation.** Every heading `text` in the outline record and every `term`
   and `definition` in the glossary record is asserted to appear as a substring
   of the canonical bank's raw bytes. This is the check that distinguishes a
   derived view from an invented one: a deterministic function that invented
   content would pass check 1 and fail this.
3. **Rebuild.** The scenario writes a rendered HTML page and a JSON outline into
   a `derived/` directory, deletes both and the directory, recomposes from the
   canonical Markdown alone, and asserts the recomposed records equal the
   originals and the canonical file's SHA-256 is unchanged. That is PORT-01's
   rebuild clause executed literally rather than asserted.

The fixture is built so check 2 can actually fail: every term definition and
every heading text in `build_output_mode_lesson` is a distinct fictional string,
so a match cannot happen by accident on a common word.

## 5. The tracer's final summary line, verbatim

```
scenario thin_slice: pass
scenario additivity_golden_parse: pass
scenario fourteen_roles: pass
scenario unknown_semantics: pass
scenario example_order: pass
scenario capability_profiles: pass
scenario unavailable_renderer: pass
scenario media_metadata: pass
scenario activity_declarations: pass
scenario unsupported_response_form: pass
scenario output_modes: pass
scenario backburner_catalog: pass
TRACER: 12 passed, 0 skipped, 0 failed
```

Exit 0. `16A-VALIDATION.md`'s expected count after 16A-07 is 12.

`tests/output_mode_check.py` prints `output modes ok` and exits 0.

## 6. The additivity proof, re-verified

```
fixtures/lesson_golden_phase3_parse.json 4078e7532ed33b341a6d551791d8ecc72175e1e479c63420b56db2b635a8e5aa
fixtures/lesson_golden_phase3_content.txt 800edb4cc180cda67885dc558e6784e713e9d636f9ebf8336919c1df93318a3c
fixtures/lesson_bank.md e34d5c9d3c2c16115257d5b1640f8aa9386e037ff6a15bc1eb6480d82c64398e
```

Unchanged. `python itembank.py guard .` reports `0 offending files`.
`git diff -U0 | grep '^+' | grep -c "—"` returns `0`.

**Full suite.** The same three pre-existing red files and no others:
`tests/day_roundtrip.py`, `tests/phase_062_audit.py`, and
`tests/retention_ui_roundtrip.py`.

## 7. Which truth was verified by which command

| Truth | Command | Result |
|---|---|---|
| two modes compose from shared schemas, no private extractor | `check_compose_outline`, `check_compose_glossary` | every outline slug equals its `parse_lesson` slug; every glossary slug is a `parse_terms` key |
| composed records are derived and disposable | `scenario_output_modes`'s derivation and rebuild legs | every string found in the source bytes; recomposed records equal; file hash unchanged |
| eight modes parked, not cut | `scenario_backburner_catalog` | eight entries, five non-empty fields each, no vague trigger |
| a mode cannot fall out of both lists | the union assertion in both files | `10` |
| an entry cannot be parked with an empty trigger | `check_backburner_refuses_empty_trigger` | `CapabilityError` naming each of the five fields in turn |
| no second outline generator | `grep -cE "^import graph\|^from graph" capabilities.py` and `_graph_outline_entries`'s delegation | `0`; the objective order is whatever `outline_projection` emitted |
| no new canonical type, nothing written | `grep -c "open(" capabilities.py` | `0` |

## 8. Deviations from the plan, with reasons

Three.

**D1. `graph.outline_projection` returns a Markdown string, so
`_graph_outline_entries` parses its heading lines.** Recorded in full in section
2. The plan anticipated a shape mismatch and named the fallback (`derive a slug
through model.lesson_slug`), which is what happened; what it did not anticipate
was that the return is a document rather than a record list. The delegation
principle is intact: this module computes no objective ordering and takes
whatever order the projection emitted.

**D2. `compose_glossary` takes an optional second argument, `source=""`.** The
plan's signature is `compose_glossary(terms)`, and its behavior block requires a
`provenance` that names the source. `model.parse_terms` is the one preamble
reader in `model.py` that does **not** carry a `path` key in its return, unlike
`parse_sources`, `parse_media`, and `parse_activities`, so with the plan's exact
signature the provenance sentence could not name anything. The argument is
optional and defaults to the empty string, so the plan's own call form still
works and simply yields a less specific provenance sentence; the tracer and the
unit check both pass the path. The alternative, adding a `path` key to
`parse_terms`'s return, would have changed a shipped parser's shape for a
Phase 16A convenience and is not worth it.

**D3. `check_compose_glossary` reads `fixtures/terms_above_lesson_bank.md`
rather than `fixtures/lesson_bank.md`.** The plan's verify block names
`fixtures/lesson_bank.md`'s "parsed lesson and terms". That bank carries no
`## TERMS` section, so `parse_terms` returns `None` and the glossary assertions
would have been vacuous. The outline half still uses `lesson_bank.md` as the
plan says; the glossary half uses the shipped fixture that actually has a terms
registry, and the `None` case is covered separately by
`check_glossary_degrades`.

## 9. Open items recorded rather than filled

- **No composed record reaches a surface.** Both composers return dicts and
  nothing renders them: no CLI command, no daemon route, and no HTML. That is
  the plan's scope, and it means the two registered modes are proven to compose
  and are not yet proven to be readable. Whichever phase surfaces them owns that.
- **`compose_outline`'s graph path is exercised by no fixture.** The tracer
  composes from a lesson alone, which is what the freeze-gate corpus has. The
  graph branch is covered by `_graph_outline_entries`'s own delegation and by
  the no-graph provenance assertion, not by a composed-with-graph record. A
  fixture carrying a real course sidecar would be the honest way to close that,
  and it belongs to whichever phase first composes a course rather than a lesson.
- **`derived_from` is a list of identifier strings and nothing validates them.**
  It names the lesson source path and, when a graph contributed, a course
  identifier read from the graph header. Nothing checks that either resolves.
  Recorded so the field is understood as a pointer back rather than as a
  verified link.
