# Plan 14C-03 summary

Executed 2026-08-28 on Darwin arm64, Python 3.14.6. Both tasks ran. The plan
is `autonomous: true` and carries no blocking human checkpoint.

## What landed

- `fixtures/audit/pptx_fidelity_cases.py`: six hand-assembled PPTX fixtures
  with recorded gold manifests, built from stdlib `zipfile` and literal XML
  and importing no third-party library.
- `_extract_pptx` and `_pptx_slide_order` in `source_adapters.py`, plus the
  `P_NS`, `R_NS`, and `PKG_REL_NS` namespace constants. `ADAPTER_REGISTRY`
  and `ADAPTER_VERSIONS` gained `pptx` at `1.0.0`.
- `check_pptx_fixture_determinism`, `check_pptx_gold_cases`,
  `check_pptx_notes_flag`, `check_pptx_slide_order`, and
  `check_pptx_partial_refusal` in `tests/source_adapters_roundtrip.py`, and
  `check_degrades_without_dependencies` extended to cover `docx` and `pptx`
  beside `pdf`.

## The minimal PPTX part set python-pptx actually accepted

The plan described this from format documentation. Observed against the
installed python-pptx 1.0.2, this is the complete set of members a package
must carry for `pptx.Presentation()` to open it and yield slides:

| Member | Why it is needed |
|---|---|
| `[Content_Types].xml` | Overrides for `presentation.xml`, every `slideN.xml`, every `notesSlideN.xml`, `slideMaster1.xml`, and `slideLayout1.xml`. A missing override for any part makes that part invisible. |
| `_rels/.rels` | `officeDocument` relationship to `ppt/presentation.xml`. |
| `ppt/presentation.xml` | Must carry `p:sldMasterIdLst` as well as `p:sldIdLst`; python-pptx resolves the master eagerly. `p:sldSz` and `p:notesSz` are accepted but not required. |
| `ppt/_rels/presentation.xml.rels` | One `slide` relationship per slide **and** the `slideMaster` relationship. |
| `ppt/slideMasters/slideMaster1.xml` plus its `_rels` | Required. Must carry a `p:clrMap` element and a `p:sldLayoutIdLst` naming at least one layout, and its rels must point at that layout. |
| `ppt/slideLayouts/slideLayout1.xml` plus its `_rels` | Required, and its rels must point back at the master. A layout with an empty `p:spTree` is accepted. |
| `ppt/slides/slideN.xml` plus its `_rels` | Each slide's rels must carry a `slideLayout` relationship, plus a `notesSlide` relationship when notes exist. |
| `ppt/notesSlides/notesSlideN.xml` plus its `_rels` | Only when notes exist. The notes text frame is found through `p:ph type="body"`, so the placeholder element is load-bearing, not decoration. |

**Plan `14C-07` builds an EPUB container fixture the same way and inherits the
shape of this finding**, though not its part list: the recurring lesson is that
a container format's reader resolves a graph of relationship parts eagerly, so
a fixture must satisfy the whole graph and not only the part under test.

## `slide.shapes` order, and a trap in `slide.part.partname`

`slide.shapes` yielded shapes in `p:spTree` document order in every fixture,
which is the visual order, so the adapter uses it directly and needs no
sort. `shape_index` is the position in that enumeration, counting non-text
shapes too, so a picture between two text boxes leaves a gap in the ids rather
than silently renumbering the text around it.

**`slide.part.partname` is not usable as slide identity.** In the
`pptx-reordered-slides` case, python-pptx yields the slides in the correct
`sldIdLst` order (the first slide's text is `This part is named slide2.`) while
reporting that slide's `part.partname` as `/ppt/slides/slide1.xml`, which is
the archive member the *other* slide came from. The partname reflects the
slide's position in the loaded collection, not the member it was read from.

This changed the implementation. The plan's step 2 has the adapter resolve
`sldIdLst` to part names and use that as the reading order; the join back to
python-pptx's slide objects cannot be done by partname, so it is positional,
and the resolved order is used to fix the count (a mismatch is a typed
`source.malformed_input` naming both numbers) and to hold the ordering
contract. The property the plan wanted is intact and is proven by the
reordered gold case, which is exactly the case that goes red if slide order
ever comes from sorted filenames. The trap is written into `_extract_pptx`'s
docstring so a later reader does not "fix" the positional join into a
partname lookup.

## Gold reading orders the adapter could not reproduce

**None.** All six cases resolve exactly as recorded, including the two typed
refusals.

## Which truth was verified by which command and which check

| Truth | Command | `check_*` |
|---|---|---|
| Six hand-assembled cases, deterministic within a process, every recorded sha256 stable, `materialize` writing only inside its own directory | `python3 tests/source_adapters_roundtrip.py` | `check_pptx_fixture_determinism` |
| The fixture module never imports python-pptx | same | same check, `hasattr(module, "pptx")` is false |
| All six gold cases resolve as recorded | same | `check_pptx_gold_cases` |
| A speaker note carries a real boolean on its locator body and the same slide number as its slide | same | `check_pptx_notes_flag` |
| Reading order comes from the `sldId` list, proven by the first emitted text being slide2's | same | `check_pptx_slide_order` |
| A media-only slide is named in the sidecar while the rest of the deck imports, with a schema-valid sidecar | same | `check_pptx_partial_refusal` |
| pdf, docx, and pptx each refuse by name with their own install command while markdown still imports | same | `check_degrades_without_dependencies` |
| `pptx` is registered at version 1.0.0 | `python3 -c "import source_adapters as s; ..."` | prints `pptx registered` |
| Slide order is read from the presentation part | `grep -c "sldIdLst" source_adapters.py` | 1 |
| The notes guard is real | `grep -c "has_notes_slide" source_adapters.py` | 2 |
| The per-slide refusal message is in source | `grep -c "media-only slide, no text-bearing shape" source_adapters.py` | 1 |
| Every schema document still self-checks | `python3 schema_validate.py --all` | exit 0 |
| No repository-authored em dash | `python3 itembank.py guard .` | exit 0, `0 offending files` |
| `runtime.py`, `model.py`, `auditor.py`, `journal.py` untouched | `git diff --stat` on the four | empty |
| The whole suite | `for t in tests/*.py; do python3 "$t" || exit 1; done` | **88 of 88 pass** |

## Deviations from the plan, each with its reason

1. **The join to python-pptx is positional, not by part name.** Forced by the
   `partname` finding above. Recorded there in full.

2. **The fixture builder writes a slide master and a slide layout.** The
   plan's step 2 lists `[Content_Types].xml`, `_rels/.rels`,
   `ppt/presentation.xml`, `ppt/_rels/presentation.xml.rels`, and the slide
   parts. A package with only those does not open: python-pptx resolves the
   master eagerly. The two extra parts are inert (an empty shape tree, a blank
   layout) and exist only to satisfy the reader.

3. **The notes locator id is `s%d.n0`, one note per slide.** The plan's
   `"s%d.n%d" % (slide_number, index)` implies several notes per slide.
   python-pptx exposes exactly one notes text frame per slide, so the index is
   always 0. The id shape is kept so a future adapter reading individual note
   paragraphs can use `n1`, `n2` without breaking the recorded gold.

4. **`fixtures/audit/pptx_fidelity_cases.py` carries no `expectation` key.**
   That key is the Phase 11 auditor gate's, and
   `tests/audit_coverage_roundtrip.py` enumerates
   `locator_fidelity_cases.CASE_TABLE` only, so adding it here would have been
   a claim about a gate this file is not in. Stated in the module docstring.
   `adapter_expectation` is present and follows the same reading-order
   invariant plan `14C-02` recorded, asserted by
   `check_pptx_fixture_determinism`.

5. **The `pptx-reordered-slides` gold carries an extra `first_text` key.** It
   is what makes `check_pptx_slide_order` fail loudly rather than
   coincidentally: two slides with the same reading order ids differ only in
   their text, so the text is the assertion.

## What this plan did not do

It did not open plan `14C-04`. It touched no file under `surfaces/`, and left
`runtime.py`, `model.py`, `auditor.py`, and `journal.py` unchanged. It added no
package and did not edit `deps/source-adapter-pins.txt`. It extracted no slide
image, chart, layout placeholder, or embedded media, all of which its
`out_of_scope` refuses. `web`, `transcript`, `ocr`, `epub`, and `asr` remain
plans 04 through 08.
