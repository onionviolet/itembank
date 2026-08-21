---
phase: 14C-source-adapter-registry
plan: 03
type: execute
wave: 3
depends_on: ["14C-02"]
files_modified:
  - source_adapters.py
  - fixtures/audit/pptx_fidelity_cases.py
  - tests/source_adapters_roundtrip.py
autonomous: true
requirements: [D-01, D-05, ROSTER-2-PPTX, TREAT-02]
estimate:
  tokens: 120000
  raw_tokens: 60000
  tasks: 2
  confidence: low
must_haves:
  truths:
    - "A PPTX slide deck extracts to Markdown in slide order, and every emitted locator carries the one-based slide number so a citation can name the slide it came from."
    - "Speaker-notes text is extracted and is distinguishable from on-slide text by the boolean notes flag on its locator body, never by a naming convention or by position in the reading order."
    - "A slide whose only content is an embedded video or an image with no text returns a typed unsupported entry naming that slide, while the other slides in the same deck still extract; a deck of only such slides returns a typed unsupported result and writes nothing."
    - "Every PPTX part is read through the same _read_zip_part and _parse_xml_safely seam the DOCX adapter uses, so the size cap and the entity-declaration refusal cover PPTX without a second implementation."
    - "fixtures/audit/pptx_fidelity_cases.py builds every fixture from stdlib zipfile and hand-assembled XML, imports no third-party library, and reads and writes nothing in the repository, so the adapter under test is the only thing exercising python-pptx."
  prohibitions:
    - statement: "No second parser, scorer, or evidence store."
      status: flagged-unverified
      verification: "check_no_second_parser is re-run; git diff --stat model.py runtime.py auditor.py reports no change."
    - statement: "No rewrite of itembank in TypeScript and no plugin kernel reimplemented in Python."
      status: flagged-unverified
      verification: "files_modified contains three Python files, none of them a loader or kernel module."
    - statement: "No hosted multi-tenant anything."
      status: flagged-unverified
      verification: "every fixture materializes into a tempfile.mkdtemp() base and the fixture module writes nothing in the repository."
    - statement: "PyMuPDF and ebooklib are not adopted."
      status: flagged-unverified
      verification: "grep -i -E 'pymupdf|fitz|ebooklib' source_adapters.py fixtures/audit/pptx_fidelity_cases.py finds no import of either."
    - statement: "An unresolved rights grant is never treated as permissive."
      status: flagged-unverified
      verification: "check_rights_refusal is re-run with a PPTX input."
  artifacts:
    - "fixtures/audit/pptx_fidelity_cases.py with its own CASE_TABLE, sha256 helper, pptx_bytes builder, and materialize function"
    - "_extract_pptx in source_adapters.py and the pptx key in ADAPTER_REGISTRY"
    - "check_pptx_gold_cases and check_pptx_notes_flag in tests/source_adapters_roundtrip.py"
  key_links:
    - "The fixture builder must assemble PPTX bytes by hand with stdlib zipfile, exactly the way fixtures/audit/locator_fidelity_cases.py assembles DOCX bytes. If the fixture is built with python-pptx, the test proves only that python-pptx round-trips its own output, and a real deck authored by PowerPoint could still fail."
    - "python-pptx exposes slide.has_notes_slide and slide.notes_slide.notes_text_frame. A deck saved without notes has no notesSlide part at all, so has_notes_slide is the guard that must be checked before touching notes_slide, or the adapter raises on every ordinary deck."
    - "PPTX slide order is the order of sldId elements in ppt/presentation.xml, not the numeric order of the ppt/slides/slideN.xml filenames. A deck whose slides were reordered in PowerPoint keeps its original filenames, so sorting filenames produces the wrong reading order silently."
---

<objective>
Land the PPTX adapter. `14C-CONTEXT.md` roster item 2 says PPTX was unscoped
anywhere in `.planning/` until this phase, and that it is how both CSCI 1100 and
EMT actually run: the lecture deck is the primary artifact for both courses.
Clean locators, no rights problem, and the container hardening it needs already
exists from plan `14C-02`.

Decisions already made, cited, and never re-litigated here:

- **D-01**: python-pptx 1.0.2, MIT, reviewed and pinned by plan `14C-01`
  Task 2's blocking human checkpoint. No new dependency decision is open.
- **D-05**: the adapter never touches the scorer.
- **D-14C-1** (`14C-DECISIONS.md`): the frozen sidecar contract, including the
  `body_pptx` row with required `medium` const `"pptx"`, `slide`,
  `shape_index`, and `notes`.
- **`14C-02` Task 1**: `_read_zip_part` and `_parse_xml_safely` are the one
  hardened seam. PPTX reads through them and adds nothing of its own.

Purpose: cover the medium the learner's two live courses actually ship in.
Output: one more registry entry, one new gold-case fixture file, and the tests
that hold the adapter to it.
</objective>

<execution_context>
@$HOME/.claude/gsd-core/workflows/execute-plan.md
@$HOME/.claude/gsd-core/templates/summary.md
</execution_context>

<context>
@.planning/phases/14C-source-adapter-registry/14C-CONTEXT.md
@.planning/phases/14C-source-adapter-registry/14C-RESEARCH.md
@.planning/phases/14C-source-adapter-registry/14C-PATTERNS.md
@.planning/phases/14C-source-adapter-registry/14C-VALIDATION.md
@.planning/phases/14C-source-adapter-registry/14C-DECISIONS.md
@.planning/phases/14C-source-adapter-registry/14C-01-PLAN.md
@.planning/phases/14C-source-adapter-registry/14C-02-PLAN.md
@fixtures/audit/locator_fidelity_cases.py
@source_adapters.py
</context>

## Artifacts this phase produces (plan 14C-03 share)

- `fixtures/audit/pptx_fidelity_cases.py`
  - `sha256(raw)` helper, identical to the one in
    `fixtures/audit/locator_fidelity_cases.py`.
  - Builders: `_zi(xml_bytes)`, `pptx_bytes(slides, notes=None, extra_parts=None)`,
    `slide_xml(shapes)`, `notes_xml(text)`, `presentation_xml(slide_count)`.
  - `CASE_TABLE`, a list of case dicts with the same
    `{id, kind, filename, build, gold}` shape the DOCX and PDF file uses, where
    `gold` carries `sha256`, `structures`, `reading_order`, `unsupported`, and
    `adapter_expectation`.
  - `materialize(dest_dir)` returning `(case_id, path, sha256)` records.
- `source_adapters.py`
  - New function `_extract_pptx(raw_bytes, options)`.
  - `ADAPTER_REGISTRY` gains `"pptx"`; `ADAPTER_VERSIONS` gains `"pptx": "1.0.0"`.
  - New constant `P_NS`, the PresentationML namespace prefix string, and
    `R_NS`, the officeDocument relationships namespace prefix string, used for
    reading the `sldId` order from `ppt/presentation.xml`.
- `tests/source_adapters_roundtrip.py`
  - New functions `check_pptx_gold_cases`, `check_pptx_notes_flag`,
    `check_pptx_slide_order`.

New refusal codes introduced by this plan: none.

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: the PPTX gold-case fixture file, built by hand from stdlib zipfile</name>
  <files>fixtures/audit/pptx_fidelity_cases.py, tests/source_adapters_roundtrip.py</files>
  <read_first>
- `fixtures/audit/locator_fidelity_cases.py` lines 1 to 30 (the module docstring
  stating the stdlib-only, deterministic, repository-independent contract), 26
  to 28 (`sha256`), 132 to 182 (`_entry`, `_zi`, `docx_bytes`, `w`, `doc_xml`,
  the exact hand-assembly idiom for an OOXML zip container), 183 to 205 (one
  complete case dict, for the shape), and 613 to 626 (`materialize`).
- `.planning/phases/14C-source-adapter-registry/14C-PATTERNS.md`, the section
  headed "fixtures/audit/pptx_fidelity_cases.py ... (new)", for the id-shape
  convention it recommends (`"s1.0"` for slide 1 shape 0).
- `tests/audit_coverage_roundtrip.py` lines 29 and 147 to 152, for the
  `sys.path.insert(0, FIXTURES)` import idiom this repository uses; there is no
  package under `fixtures/`, so a dotted import fails.
  </read_first>
  <behavior>
Write `check_pptx_fixture_determinism` first, watch it fail, then build.

- `check_pptx_fixture_determinism`: calling each case's `build()` twice in the
  same process produces byte-identical output, and each case's built bytes hash
  to its recorded `gold["sha256"]`. `materialize()` into a temporary directory
  returns one record per case and writes nothing outside that directory.
- The same check asserts that `pptx_fidelity_cases` has no attribute named
  `pptx` after import, proving the fixture module does not use python-pptx to
  build the bytes it tests python-pptx against.
  </behavior>
  <action>
1. Create `fixtures/audit/pptx_fidelity_cases.py` with a module docstring in the
   register of `locator_fidelity_cases.py`'s: name the phase and plan (14C, plan
   `14C-03`), state that the case table is immutable data, the builders are pure
   functions, nothing here reads or writes the repository, and imports are
   stdlib only (`hashlib`, `io`, `os`, `zipfile`). State in one sentence why the
   bytes are hand-assembled rather than produced by python-pptx: a fixture built
   with the library under test proves only that the library round-trips its own
   output.

2. Implement the builders. A minimal valid PPTX is a zip carrying
   `[Content_Types].xml`, `_rels/.rels`, `ppt/presentation.xml`,
   `ppt/_rels/presentation.xml.rels`, and one `ppt/slides/slideN.xml` per slide
   with its own `ppt/slides/_rels/slideN.xml.rels`. A notes slide adds
   `ppt/notesSlides/notesSlideN.xml` plus a relationship from the slide.
   Assemble every member with a fixed `ZipInfo` timestamp, exactly the way
   `_zi` in `locator_fidelity_cases.py` does, so the archive bytes are
   deterministic across runs and machines.

3. Build these six cases. Every `gold` records `sha256`, `structures`,
   `reading_order`, `unsupported`, and `adapter_expectation`.
   - `pptx-two-slides-text`, filename `pptx-two-slides.pptx`: slide 1 with a
     title shape reading `Airway Management` and a body shape reading
     `Assess responsiveness first.`; slide 2 with one body shape reading
     `Then open the airway.`. `reading_order` is
     `["s1.0", "s1.1", "s2.0"]`. `adapter_expectation` `"supported"`.
   - `pptx-speaker-notes`, filename `pptx-notes.pptx`: one slide with one body
     shape reading `Oxygen delivery devices` and a notes slide reading
     `Mention the Venturi mask flow rates.`. `reading_order` is
     `["s1.0", "s1.n0"]`, where the `n` in the second id marks a notes locator.
     `adapter_expectation` `"supported"`.
   - `pptx-reordered-slides`, filename `pptx-reordered.pptx`: two slide parts
     named `slide1.xml` and `slide2.xml`, but `ppt/presentation.xml` lists their
     `sldId` entries in the opposite order, so the correct reading order is
     `slide2` first. `reading_order` is `["s1.0", "s2.0"]` where slide index 1
     is the part named `slide2.xml`. This case is the one that goes red if the
     adapter sorts filenames instead of reading the `sldId` list.
     `adapter_expectation` `"supported"`.
   - `pptx-video-only-slide`, filename `pptx-video-slide.pptx`: two slides, the
     first with text and the second carrying only a `p:pic` element with a video
     relationship and no `a:t` text run. `reading_order` is `["s1.0"]`, and
     `unsupported` is `["slide 2: media-only slide, no text-bearing shape"]`.
     `adapter_expectation` `"supported"`, because the deck as a whole extracts;
     the refusal is a per-slide entry, not a whole-file result.
   - `pptx-all-media-slides`, filename `pptx-all-media.pptx`: one slide, media
     only. `structures` and `reading_order` are empty, `unsupported` is
     `["media-only deck: no text-bearing shape"]`, `adapter_expectation`
     `"unsupported"`.
   - `pptx-malformed-truncated`, filename `pptx-truncated.pptx`: the bytes of
     `pptx-two-slides.pptx` sliced to their first 200 bytes, mirroring the
     `pdf-malformed-truncated` case's own construction. `unsupported` is
     `["malformed/truncated PPTX"]`, `adapter_expectation` `"unsupported"`.

4. Compute each case's `sha256` by running the builder once and recording the
   result. Do not hand-write a hash. Record it in the case dict so a later
   accidental change to a builder is caught by
   `check_pptx_fixture_determinism` rather than silently shifting the gold.

5. Implement `materialize(dest_dir)` byte for byte in the shape
   `locator_fidelity_cases.materialize` uses: `os.makedirs(dest_dir,
   exist_ok=True)`, loop the case table, write each build output, return
   `(case_id, path, sha256(raw))` records.

6. Add `check_pptx_fixture_determinism` to `tests/source_adapters_roundtrip.py`
   and to its `__main__` sequence.
  </action>
  <verify>
  <automated>python3 tests/source_adapters_roundtrip.py</automated>
Expected: exit 0. The degraded state this task must prove is a fixture that
cannot drift silently: `check_pptx_fixture_determinism` fails if a builder's
output no longer hashes to its recorded gold, which is the same guarantee the
existing PDF and DOCX fixture file gives.
  </verify>
  <acceptance_criteria>
- `python3 tests/source_adapters_roundtrip.py` exits 0.
- `python3 -c "import sys,os; sys.path.insert(0,os.path.join('fixtures','audit')); import pptx_fidelity_cases as g; assert len(g.CASE_TABLE)==6; assert all(set(c['gold'])>={'sha256','structures','reading_order','unsupported','adapter_expectation'} for c in g.CASE_TABLE); print('pptx fixtures ok')"` prints `pptx fixtures ok`.
- `python3 -c "import sys,os; sys.path.insert(0,os.path.join('fixtures','audit')); import pptx_fidelity_cases as g; assert not hasattr(g,'pptx'); print('fixture is stdlib only')"` prints `fixture is stdlib only`.
- `python3 -c "import sys,os,tempfile,shutil; sys.path.insert(0,os.path.join('fixtures','audit')); import pptx_fidelity_cases as g; d=tempfile.mkdtemp(); r=g.materialize(d); assert len(r)==6; shutil.rmtree(d); print('materialize ok')"` prints `materialize ok`.
- `python3 itembank.py guard .` exits 0.
- The new fixture file contains no em dash character.
  </acceptance_criteria>
  <precondition>fixtures/audit/ exists and tests import fixture modules through sys.path.insert, not through a package import.</precondition>
  <reversibility rating="reversible">A new fixture file with no consumers until Task 2; deleting it restores the tree.</reversibility>
  <done>Six deterministic, hand-assembled PPTX fixtures exist with recorded gold manifests, and none of them was built with the library they will test.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: the PPTX adapter, slide order from presentation.xml and a real notes flag</name>
  <files>source_adapters.py, tests/source_adapters_roundtrip.py</files>
  <read_first>
- `fixtures/audit/pptx_fidelity_cases.py` as built in Task 1, all six cases and
  their recorded `reading_order` strings.
- `source_adapters.py` as landed by plans `14C-01` and `14C-02`: the four-tuple
  extraction contract comment above `ADAPTER_REGISTRY`, `_read_zip_part`,
  `_parse_xml_safely`, the lazy per-adapter import discipline in
  `_extract_docx`, and the `unsupported_result` builder.
- The frozen `body_pptx` row in `14C-01-PLAN.md`'s "The frozen sidecar
  contract" section: required `medium` const `"pptx"`, `slide` integer minimum
  1, `shape_index` integer minimum 0, `notes` boolean.
- `.planning/phases/14C-source-adapter-registry/14C-RESEARCH.md`, the Standard
  Stack row for python-pptx, noting its dependency set (`lxml`, `Pillow`,
  `typing_extensions`, `XlsxWriter`).
  </read_first>
  <behavior>
Write these assertions first, watch them fail, then implement.

- `check_pptx_gold_cases`: each of the six cases produces exactly its recorded
  `reading_order` when `adapter_expectation` is `"supported"`, and a typed
  refusal whose message equals the recorded `unsupported[0]` string when it is
  `"unsupported"`.
- `check_pptx_notes_flag`: in the `pptx-speaker-notes` case, exactly one
  locator has `body["notes"] is True` and exactly one has
  `body["notes"] is False`; the notes locator's text appears in the derived
  Markdown; and the notes locator's `body["slide"]` equals the slide it belongs
  to, not a separate numbering.
- `check_pptx_slide_order`: the `pptx-reordered-slides` case produces its
  recorded reading order. Assert additionally that the text of the first
  emitted locator is the text of the slide part named `slide2.xml`, so the test
  fails loudly if the adapter sorted filenames.
- `check_pptx_partial_refusal`: the `pptx-video-only-slide` case returns status
  `ok` with a non-empty `locators` list and a non-empty `unsupported` list
  naming slide 2. A per-slide refusal does not discard the deck.
- Extend `check_degrades_without_dependencies` with the pptx case: with `pptx`
  unimportable, `_extract_pptx` returns `source.dependency_missing` naming the
  install command while the markdown, pdf, and docx adapters are unaffected.
  </behavior>
  <action>
1. Implement `_extract_pptx(raw_bytes, options)` in `source_adapters.py`.
   Import `pptx` inside the function body; on `ImportError` return
   `source.dependency_missing` whose message ends with the literal
   `run: pip install python-pptx==1.0.2`.

2. Determine slide order from the package, not from filenames. Open the bytes
   as a `zipfile.ZipFile`, read `ppt/presentation.xml` through
   `_read_zip_part`, parse it through `_parse_xml_safely`, and walk
   `p:sldIdLst` children in document order, resolving each child's
   `r:id` attribute against `ppt/_rels/presentation.xml.rels` to get the slide
   part name. That resolved sequence is the reading order. Record in the
   function docstring, in one sentence, that filename order is not slide order
   because PowerPoint keeps a slide's original part name when the deck is
   reordered, so sorting `slideN.xml` names produces the wrong order with no
   visible symptom.

3. Use python-pptx for the shape walk within each slide, in the order
   `slide.shapes` yields. For each shape with a text frame carrying non-empty
   text, emit a locator with id `"s%d.%d" % (slide_number, shape_index)`,
   `kind` `"slide"`, and body
   `{"medium": "pptx", "slide": slide_number, "shape_index": shape_index, "notes": False}`.
   `slide_number` is the one-based position in the resolved order from step 2,
   not the number in the part filename.

4. For notes: guard on `slide.has_notes_slide` before touching
   `slide.notes_slide`, because a deck saved with no notes has no notesSlide
   part and the attribute access raises. When notes exist and the notes text
   frame's text is non-empty, emit one locator with id
   `"s%d.n%d" % (slide_number, index)`, `kind` `"notes"`, and body with
   `"notes": True` and the same `slide` number. Notes locators follow their
   slide's shape locators in the reading order, which is what the
   `pptx-speaker-notes` gold case records.

5. Markdown emission: one `## Slide N` heading line per slide, then one line per
   shape locator, then, when notes exist, one `> ` quoted line per notes
   locator so the derived Markdown itself distinguishes speaker notes from
   on-slide text for a human reader. The heading line has no locator and no
   `span_id`; only content lines map to locators. State this in the docstring so
   a later reader does not try to make the heading citable.

6. Per-slide refusal: a slide that yields no text-bearing shape appends
   `{"code": "source.unsupported", "message": "slide %d: media-only slide, no text-bearing shape" % slide_number}`
   to the `unsupported` list and contributes no locator. The deck still
   extracts. Only when every slide is media-only does the function return the
   whole-file refusal with the message
   `media-only deck: no text-bearing shape`.

7. Whole-file refusals: bytes that are not a readable zip return
   `source.malformed_input` with the message `malformed/truncated PPTX`; a
   package with no `ppt/presentation.xml` returns `source.malformed_input`.

8. Register `"pptx"` in `ADAPTER_REGISTRY` and add `"pptx": "1.0.0"` to
   `ADAPTER_VERSIONS`.

9. Add `check_pptx_gold_cases`, `check_pptx_notes_flag`,
   `check_pptx_slide_order`, and `check_pptx_partial_refusal` to
   `tests/source_adapters_roundtrip.py` and to its `__main__` sequence, and
   extend `check_degrades_without_dependencies` with the pptx case.
  </action>
  <verify>
  <automated>python3 tests/source_adapters_roundtrip.py</automated>
Expected: exit 0. The degraded state this task must prove is two-sided: with
python-pptx absent the pptx adapter returns `source.dependency_missing` while
every other adapter still works, and with a media-only slide present the deck
still extracts rather than being discarded.
  </verify>
  <acceptance_criteria>
- `python3 tests/source_adapters_roundtrip.py` exits 0.
- `python3 -c "import source_adapters as s; assert 'pptx' in s.ADAPTER_REGISTRY and s.ADAPTER_VERSIONS['pptx']=='1.0.0'; print('pptx registered')"` prints `pptx registered`.
- `grep -c "sldIdLst" source_adapters.py` returns at least 1, the mechanical
  proof that slide order comes from the presentation part and not from sorted
  filenames.
- `grep -c "has_notes_slide" source_adapters.py` returns at least 1.
- `grep -c "media-only slide, no text-bearing shape" source_adapters.py` returns
  at least 1.
- `python3 schema_validate.py --all` exits 0.
- `for t in tests/*.py; do python3 "$t" || exit 1; done` exits 0.
- `python3 itembank.py guard .` exits 0.
- `git diff --stat runtime.py model.py auditor.py` reports no change.
- No file changed by this task contains an em dash character.
  </acceptance_criteria>
  <precondition>python-pptx 1.0.2 is installed from deps/source-adapter-pins.txt, and Task 1's fixture file exists.</precondition>
  <reversibility rating="reversible">One registry entry and one private extraction function.</reversibility>
  <done>Six PPTX gold cases resolve as recorded, slide order comes from the presentation part, and a speaker note is distinguishable from on-slide text by a real flag on its locator.</done>
</task>

</tasks>

<threat_model>
ASVS level 1. Block on `high`.

## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Learner-supplied PPTX bytes to stdlib zipfile and to python-pptx | A crafted deck reaches two parsers inside itembank's process. |
| Slide relationship resolution | An `r:id` in `presentation.xml` is resolved against a relationships part whose target string is archive-supplied. |
| Adapter to durable disk | Derived Markdown and a sidecar are written under the approved root. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-14C-15 | Denial of Service | crafted PPTX zip container | high | mitigate | Every part read goes through `_read_zip_part` from plan `14C-02`, which checks declared uncompressed size against `source.max_input_bytes` and caps member count before any decompression. python-pptx opens the same bytes, so the size cap is enforced on the raw input before the library is handed it. |
| T-14C-16 | Denial of Service | entity expansion in a PPTX XML part | high | mitigate | `_parse_xml_safely` refuses any part containing `<!DOCTYPE` or `<!ENTITY` before parsing. `presentation.xml` and the relationships parts, which this adapter parses directly, both go through it. |
| T-14C-17 | Tampering | archive-supplied relationship target | medium | mitigate | A resolved slide part name is used only as a `zipfile` member lookup through `_read_zip_part`, which refuses an absolute name or a name containing a `..` segment. It is never joined onto a filesystem path and no member is ever extracted to disk. |
| T-14C-18 | Information Disclosure | speaker notes extracted into the derived Markdown | low | accept | Speaker notes are exactly the citable content roster item 2 wants, and they stay on the learner's disk under the approved root. Recorded so the property is known rather than discovered. |
| T-14C-19 | Denial of Service | python-pptx transitive dependency surface | low | accept | python-pptx pulls `lxml`, `Pillow`, `typing_extensions`, and `XlsxWriter`; `XlsxWriter` is unused for reading but is an unconditional install-time dependency. All four were in scope of plan `14C-01` Task 2's batched legitimacy checkpoint. The adapter never invokes `Pillow` image decoding, because it reads text frames only and never touches a picture shape's blob. |
| T-14C-SC | Tampering | npm/pip/cargo installs | high | mitigate | No new package. python-pptx was reviewed and pinned by plan `14C-01` Task 2's blocking human checkpoint; `deps/source-adapter-pins.txt` is not edited here. |
</threat_model>

<out_of_scope>
- **Slide images, charts, and SmartArt.** Text frames only. An image on a slide
  is a `source.unsupported` per-slide entry if the slide has nothing else, and
  is otherwise ignored. Turning a slide image into text is the OCR adapter's
  job, plan `14C-06`, and joining the two is a later phase's.
- **Slide layouts and masters.** Placeholder text inherited from a layout is not
  slide content and is not emitted.
- **Animation, transitions, and timing.** Not citable content.
- **Embedded audio and video extraction.** A media-only slide is refused by name.
  Extracting the media and running it through ASR is roster item 5, registered
  and planned last.
- **Any second zip or XML helper.** `_read_zip_part` and `_parse_xml_safely`
  from plan `14C-02` are the only ones.
- **Any change to `runtime.py`, `model.py`, `auditor.py`, `journal.py`, or
  `surfaces/`.**
</out_of_scope>

<verification>
1. `python3 tests/source_adapters_roundtrip.py` (exit 0)
2. `python3 schema_validate.py --all` (exit 0)
3. `for t in tests/*.py; do python3 "$t" || exit 1; done` (exit 0)
4. `python3 itembank.py guard .` (exit 0)
5. `git diff --stat runtime.py model.py auditor.py journal.py` (no output)
</verification>

<success_criteria>
- All six PPTX gold cases resolve as recorded.
- Slide order comes from `ppt/presentation.xml`'s `sldIdLst`, proven by the
  reordered-slides case.
- Speaker notes carry a real boolean flag on their locator body.
- A media-only slide is a per-slide refusal, not a discarded deck.
- Zero em dash characters in any file this plan created or changed.
</success_criteria>

<summary_obligations>
`.planning/phases/14C-source-adapter-registry/14C-03-SUMMARY.md` records:

- The exact minimal PPTX part set that python-pptx actually accepted, since the
  plan describes it from format documentation and not from a run. Plan `14C-07`
  builds an EPUB container fixture the same way and will reuse the finding.
- Any gold `reading_order` the adapter could not reproduce, with the produced
  order beside it. Do not relax a gold case silently.
- Whether `slide.shapes` order matched the visual order in the fixtures, and if
  not, what the adapter used instead.
- Which truth was verified by which command and which `check_*` function.
</summary_obligations>

<output>
Create `.planning/phases/14C-source-adapter-registry/14C-03-SUMMARY.md` when done.
</output>
