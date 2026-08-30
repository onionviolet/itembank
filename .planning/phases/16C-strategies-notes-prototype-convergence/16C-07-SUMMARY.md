# 16C-07 summary

**Plan:** 16C-07, the note-output trio and the three prototype tracers.
**Executed:** 2026-08-29. **Tasks:** 3 of 3. **Files:** `note_outputs.py`,
`fixtures/note_strategy_corpus.py`, `tests/note_trio_roundtrip.py`.

## Verification, with actual final lines

```
python3 tests/note_trio_roundtrip.py       ->  NOTE TRIO: 9 passed, 0 failed  (exit 0)
python3 tests/lesson_roundtrip.py          ->  exit 0
python3 tests/note_schema_roundtrip.py     ->  exit 0
python3 tests/note_promotion_roundtrip.py  ->  exit 0
python3 itembank.py guard .                ->  0 offending files
```

No em dash character in any file this plan wrote.

## One parse, counted

`check_parse_once` replaces `model.parse_lesson` and `model.parse_terms` with
counting wrappers, builds one instance, and renders all three modes twice.
Both counters read 1 after six renders. That is the STYLE-DISCIPLINE proof
bullet measured rather than asserted, and it is only meaningful because
`check_no_file_reads` walks `note_outputs.py`'s AST and finds no `open(` call
and no import of `runtime`, `evidence`, or any surface: a projection cannot
reach around the one seam to a file.

`check_no_content_fork` changes one note's wording in a copy of the instance
and confirms every projection follows the copy while the original renders
unchanged, so no projection caches or forks the content.

## Plain coherence

Each projection is a standalone Markdown document opening with a heading and
carrying no markup at all. The notebook page shows a role label, an owner,
and a provenance line per block. Cornell carries cues and a `## Summary`. The
concept map carries at least four `relates to` lines.

The concept map's textual adjacency is not a description of a diagram, it is
the map. A rich rendering may draw it later and must keep this structure as
its accessible equivalent, because a graphic whose meaning lives only in
position and hover is a graphic a keyboard cannot read.

## Three validators, three broken fixtures, three exact sentences

| Fixture | Break | Code | Refusal |
|---|---|---|---|
| `cornell` | a heading nothing is anchored to | `note_output.cue_without_notes` | `The Cornell notes view can't be built from this content: a cue has no matching notes. Showing plain Markdown instead.` |
| `concept_map` | one edge typed `related` | `note_output.edge_untyped` | `The Concept map view can't be built from this content: a relation has no type. Showing plain Markdown instead.` |
| `notebook` | the anchored heading replaced under the note | `note_output.anchor_moved` | `The Notebook page view can't be built from this content: an anchor points to a block that moved. Showing plain Markdown instead.` |

Each break is the smallest one that makes exactly one mode unable to render,
so a validator firing on the wrong fixture is caught rather than credited.
The good instance passes all three. Every refusal still carries the plain
projection, asserted non-empty and heading-led. The notebook's other two
checks, ownership and provenance, are driven separately by blanking an owner
and blanking a locator. An unregistered mode name raises.

## The three prototype gates

**A, guided note spine.** Three drafts written, the third planted as a
corrupt `notes.md.json.tmp` rather than completed. The document re-reads with
both accepted drafts intact, every block's anchor resolves to `resolved`, and
the notebook page shows `Provenance: Anchored`. All three projections were
scanned for the corpus bank's answer keys and for the markers `CORRECT:`,
`WHY BEST:`, `KEY DISCRIMINATOR:`, `MODEL:`, and `RUBRIC:`. None appears.

**B, worked reasoning.** A deliberately wrong explanation of the CS
off-by-one renders under `**My claim**`, and its block carries no `correct`,
`verdict`, or `score` marker. Promotion with the claim unsourced blocks with
`Every keyed or factual claim needs an accepted source. 1 claims have no
accepted source yet.` and produces no derived record. A wrong learner claim
stays a labeled learner claim and cannot seed a key.

**C, provenance relocation.** A renamed heading with the same body reads
`relocated_exact` with one candidate. A same-title heading with a replaced
body reads `relocated_probable`, and the stored sidecar is byte-compared
before and after resolution to prove nothing auto-applies. A deleted heading
reads `orphaned` and the note keeps its objective ids. The document pair is
copied byte-for-byte to a second directory and re-read: the sidecar is
identical and every note's owner survives as `weibao`.

## Deviations from the plan

1. **`_edges` calls `model._term_refs`.** The project convention is that
   module-level functions carry no leading underscore, and this one does. The
   call is still the right choice: `_term_refs` is the one `[[term]]`
   reference reader and the one slugifier behind it, and a local regex here
   would be the second grammar this module exists to avoid. A reference that
   resolved differently in the concept map than in the glossary would be
   worse than an underscore. Recorded in the code with that reasoning.
2. **The Cornell validator checks the rendered shape.** The plan describes a
   separate cue list; the projection emits one cue per heading, so a heading
   nothing is anchored to IS a cue with no matching notes. Checking what the
   projection actually emits keeps the validator and the projection from
   disagreeing about what a cue is.
3. **`broken_trio_fixtures` returns note, relation, and heading sets rather
   than composed instances.** The fixtures module imports no projection, so
   composing the instance stays the caller's job and the fixture builder
   keeps its one-way dependency.
4. **`PROJECTIONS` exists as a module-level mapping**, so `render_mode` and
   the tests dispatch through one table rather than a chain of conditionals.
5. The plan's commands are written as `python`; this machine has only
   `python3`.
