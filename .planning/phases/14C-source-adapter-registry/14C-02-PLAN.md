---
phase: 14C-source-adapter-registry
plan: 02
type: execute
wave: 2
depends_on: ["14C-01"]
files_modified:
  - source_adapters.py
  - fixtures/audit/locator_fidelity_cases.py
  - tests/source_adapters_roundtrip.py
  - tests/file_fault_tracer.py
autonomous: true
requirements: [D-01, D-05, ROSTER-1-DOCX, ROSTER-1-PDF-TABLES, FILE-03, RIGHTS-01, TREAT-02]
estimate:
  tokens: 165000
  raw_tokens: 82000
  tasks: 3
  confidence: low
must_haves:
  truths:
    - "All twelve DOCX gold cases in fixtures/audit/locator_fidelity_cases.py resolve through the docx adapter to their recorded reading_order, including the four extra-parts cases (footnote and endnote, header and footer, tracked changes, comments) that python-docx's own object model never surfaces."
    - "The three PDF gold cases the tracer left unhandled (two-column reordered, table, footnote) resolve to their recorded reading_order through the pdf adapter, so every non-refusing PDF gold case passes."
    - "The three PDF refusal gold cases return their recorded unsupported message verbatim: image-only page: no text-bearing structure, encrypted PDF: no unauthenticated structure, and malformed/truncated PDF."
    - "One shared zip reading helper caps every part it reads. A zip member whose declared uncompressed size exceeds the source.max_input_bytes setting is refused with source.oversized before a single byte is decompressed, so a compression bomb never reaches memory."
    - "An XML part containing a nested entity-expansion payload is refused with source.malformed_input rather than expanding, and the refusal arrives in bounded time."
    - "A fault injected between the sidecar write and the journal append leaves either the prior valid state or an orphan sidecar with no journal entry, never an applied source object with no sidecar beside it."
    - "The existing eighteen-case gate in tests/audit_coverage_roundtrip.py still passes unchanged: auditor.normalize_source still refuses kind=pdf and kind=docx with source.adapter_unregistered, and every gold case's expectation field still reads unsupported_now."
  prohibitions:
    - statement: "No second parser, scorer, or evidence store. The DOCX extra-parts reads use stdlib zipfile and xml.etree over the OOXML parts; they do not build a second document model and they do not touch model.py."
      status: flagged-unverified
      verification: "check_no_second_parser in tests/source_adapters_roundtrip.py, already added in plan 14C-01, is re-run and still passes; git diff --stat model.py runtime.py reports no change."
    - statement: "No rewrite of itembank in TypeScript and no plugin kernel reimplemented in Python."
      status: flagged-unverified
      verification: "files_modified contains only four Python files, none of them a loader, kernel, or registry-mounting module."
    - statement: "No hosted multi-tenant anything. Every write stays under the caller-supplied approved base root."
      status: flagged-unverified
      verification: "every fixture in this plan materializes into a tempfile.mkdtemp() base; check_write_containment from plan 14C-01 is re-run."
    - statement: "PyMuPDF is not adopted, and ebooklib is not adopted. Both stay parked on an explicit Weibao AGPL decision."
      status: flagged-unverified
      verification: "grep -i -E 'pymupdf|fitz|ebooklib' source_adapters.py finds those strings only inside comments recording the parking, never inside an import statement."
    - statement: "An unresolved rights grant is never treated as permissive."
      status: flagged-unverified
      verification: "check_rights_refusal from plan 14C-01 is re-run against a DOCX input and still refuses."
  artifacts:
    - "_extract_docx and its helper _docx_extra_parts in source_adapters.py"
    - "_read_zip_part and _parse_xml_safely in source_adapters.py, the one hardened zip and XML seam every container adapter calls through"
    - "the adapter_expectation key added additively to every gold case in fixtures/audit/locator_fidelity_cases.py"
    - "the zip-bomb and entity-expansion adversarial cases in fixtures/audit/locator_fidelity_cases.py"
    - "check_two_file_pair_atomicity in tests/file_fault_tracer.py"
  key_links:
    - "python-docx's Document object walks document.paragraphs and document.tables only. Footnotes, endnotes, headers, footers, comments, and tracked-change ranges live in separate package parts (word/footnotes.xml, word/endnotes.xml, word/header1.xml, word/footer1.xml, word/comments.xml) that it never exposes. Four of the twelve DOCX gold cases are exactly those parts. An adapter built on python-docx alone passes the easy eight and silently produces nothing for the other four."
    - "The gold cases carry expectation: unsupported_now, which tests/audit_coverage_roundtrip.py:165 asserts is unchanged. That field means auditor.normalize_source refuses these bytes, which stays true forever because the adapter converts to Markdown first and auditor never sees a PDF. The new adapter_expectation key is added beside it, never in place of it, so the existing gate does not change by one line."
    - "_read_zip_part is the single seam. If a later adapter (PPTX in plan 14C-03, EPUB in plan 14C-07) opens a ZipFile and calls .read() directly, the size cap is silently bypassed for that format and the bomb guard covers only DOCX."
---

<objective>
Complete roster item 1 by landing the DOCX adapter, finish the PDF adapter's
table and column locators, and put the one hardened zip and XML seam in place
before two more container formats are built on it. Prove the sidecar-then-journal
ordering with a real fault injection rather than trusting it.

Roster item 1 in `14C-CONTEXT.md` names PDF and DOCX as one plan. It is split
across plans `14C-01` and `14C-02` for one reason, stated here so the split is a
recorded decision rather than drift: the tracer discipline requires the thinnest
possible end-to-end path first, and one PDF gold case through one route is
thinner than two adapters through one route. Plan `14C-01` proved the spine;
this plan completes the roster item.

Decisions already made, cited, and never re-litigated here:

- **D-01** (`14C-CONTEXT.md` lines 22 to 27): python-docx for DOCX, pypdf as the
  page-level fallback, dependencies already chosen and already pinned by plan
  `14C-01` Task 2.
- **D-05**: the adapter never touches the scorer.
- **D-14C-1** (`14C-DECISIONS.md`, recorded by plan `14C-01` Task 1): the frozen
  sidecar contract. This plan writes `body_docx` locators against it and changes
  no field.
- **PLANNING-DIRECTIVES.md section 4** non-negotiable 4: format changes are
  additive, proven by a byte-identical fixture, not promised. That is why the
  gold-case file gains a new key beside `expectation` rather than repurposing it.
- **RESEARCH Pitfall 1** (`14C-RESEARCH.md`): python-docx does not read
  footnotes, endnotes, headers, footers, comments, or tracked changes.
- **RESEARCH Pitfall 3**: zip and XML hardening for the three container formats.
- **RESEARCH Pitfall 5**: pdfplumber's geometry calls are expensive on pages
  with nothing to extract.

Purpose: finish the format that has the most gold coverage in the repository,
and install the container-format guard before two more container formats arrive.
Output: two more working adapters' worth of locator kinds, the hardened zip
seam, the additive fixture extension, and the two-file fault tracer.
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
@.planning/PLAN-TEMPLATE.md
@fixtures/audit/locator_fidelity_cases.py
@tests/audit_coverage_roundtrip.py
@tests/file_fault_tracer.py
@journal.py
</context>

## Artifacts this phase produces (plan 14C-02 share)

- `source_adapters.py`
  - New functions: `_extract_docx(raw_bytes, options)`,
    `_docx_extra_parts(zf, options)`, `_read_zip_part(zf, name, options)`,
    `_parse_xml_safely(raw, options)`.
  - New constants: `W_NS`, the WordprocessingML namespace prefix string
    `"{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"`;
    `DOCX_EXTRA_PARTS`, the tuple of package part names read directly;
    `MAX_XML_DEPTH = 100`; `MAX_ZIP_MEMBERS = 4096`.
  - `ADAPTER_REGISTRY` gains the key `"docx"`.
  - `_extract_pdf` gains table and column locator emission.
- `fixtures/audit/locator_fidelity_cases.py`
  - Every existing case gains one new key, `adapter_expectation`, valued
    `"supported"` or `"unsupported"`. No existing key changes value.
  - Two new cases: `zip-bomb-oversized-part` and `xml-entity-expansion`, both
    `kind` `"docx"`, both with `adapter_expectation` `"unsupported"`.
  - `materialize()` is unchanged; the new cases build through the existing
    `docx_bytes` helper.
- `tests/source_adapters_roundtrip.py`
  - New functions: `check_pdf_gold_cases`, `check_docx_gold_cases`,
    `check_docx_extra_parts`, `check_zip_bomb_guard`,
    `check_xml_entity_guard`.
- `tests/file_fault_tracer.py`
  - New function: `check_two_file_pair_atomicity`.

New refusal codes introduced by this plan: none. `source.oversized`,
`source.malformed_input`, `source.encrypted`, `source.unsupported`, and
`source.dependency_missing` are all already in `SOURCE_ADAPTER_CODES` from plan
`14C-01`.

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: the one hardened zip and XML seam, plus its adversarial fixtures</name>
  <files>source_adapters.py, fixtures/audit/locator_fidelity_cases.py, tests/source_adapters_roundtrip.py</files>
  <read_first>
- `.planning/phases/14C-source-adapter-registry/14C-RESEARCH.md`, Pitfall 3 in
  full, and the Security Domain table rows for V12 File Handling and the zip
  bomb pattern.
- `fixtures/audit/locator_fidelity_cases.py` lines 1 to 30 (the stdlib-only,
  deterministic, repository-independent contract every builder honors), 132 to
  182 (`_entry`, `_zi`, `docx_bytes`, `w`, `doc_xml`, the DOCX assembly
  helpers), and 613 to 626 (`materialize`).
- `tests/audit_coverage_roundtrip.py` lines 147 to 195, the existing eighteen-case
  gate. Note line 165: it fails if any case's `expectation` is not
  `"unsupported_now"`. This is why the new key is additive.
- `source_adapters.py` as landed by plan `14C-01`, in particular
  `SOURCE_ADAPTER_CODES`, `unsupported_result`, and the extraction-function
  four-tuple contract comment above `ADAPTER_REGISTRY`.
  </read_first>
  <behavior>
Write these assertions first, watch them fail, then implement.

- `check_zip_bomb_guard`: the `zip-bomb-oversized-part` fixture, whose
  `word/document.xml` member declares an uncompressed size above
  `options["max_input_bytes"]`, returns status `unsupported` with code
  `source.oversized`. The assertion also measures elapsed wall time and fails if
  the call takes longer than five seconds, because a guard that only refuses
  after decompressing is not a guard.
- `check_xml_entity_guard`: the `xml-entity-expansion` fixture, a well-formed
  DOCX whose `word/document.xml` carries a nested internal entity definition,
  returns status `unsupported` with code `source.malformed_input`, in under five
  seconds, and the process resident memory does not need to be measured because
  the refusal happens before any expansion.
- `check_gold_manifest_additive`: every case in
  `locator_fidelity_cases.CASE_TABLE` still carries its original
  `gold["sha256"]`, `gold["structures"]`, `gold["reading_order"]`,
  `gold["unsupported"]`, and `gold["expectation"]` values, and every case now
  also carries `gold["adapter_expectation"]` in `("supported", "unsupported")`.
  The recorded sha256 of every pre-existing case's bytes is unchanged, which is
  the byte-identical proof non-negotiable 4 asks for.
  </behavior>
  <action>
1. Add `_read_zip_part(zf, name, options)` to `source_adapters.py`. It is the
   single seam every container adapter reads a member through. In order: look up
   `zi = zf.getinfo(name)`, raising nothing on a missing member but returning
   `(None, error_tuple)`; refuse when `zi.file_size` exceeds
   `options["max_input_bytes"]` with `source.oversized` and a message naming the
   member, its declared size, and the cap; refuse when
   `len(zf.namelist()) > MAX_ZIP_MEMBERS` with `source.oversized`; refuse when
   the member name is absolute or contains a `..` segment after normalization
   with `source.malformed_input`, because a crafted archive can name a member
   that a naive extractor would write outside the target; only then call
   `zf.read(name)`. Return the two-tuple `(raw_bytes, None)` on success and
   `(None, {"code": ..., "message": ...})` on refusal. Never raise.

2. Add `_parse_xml_safely(raw, options)`. It refuses before parsing when the raw
   bytes contain a `<!DOCTYPE` or a `<!ENTITY` declaration, returning
   `source.malformed_input` with a message stating that a document type
   definition or an entity declaration is not accepted in an OOXML or EPUB part.
   Neither is legal in a well-formed OOXML part, so refusing outright costs no
   real document anything and removes the entity-expansion class entirely rather
   than bounding it. On acceptance it calls
   `xml.etree.ElementTree.fromstring(raw)` inside a `try` and
   `except ElementTree.ParseError`, converting the error to
   `source.malformed_input`. Returns `(element, None)` or `(None, error_tuple)`.
   Never raises. State the DOCTYPE-refusal reasoning in the function docstring
   so a later reader does not soften it back to a depth limit.

3. Add the two adversarial cases to `fixtures/audit/locator_fidelity_cases.py`,
   built with the existing `docx_bytes` and `_zi` helpers so they stay
   deterministic and stdlib-only:
   - `zip-bomb-oversized-part`, filename `docx-zip-bomb.docx`: a valid DOCX
     whose `word/document.xml` member is a long run of a single repeated byte,
     large enough that its declared `file_size` exceeds a test-supplied
     `max_input_bytes` of 65536 while the archive itself stays small. Build it
     by writing real bytes, not by forging a `ZipInfo` header, so the fixture
     stays a real archive that a real reader would accept. `gold` records
     `structures: []`, `reading_order: []`,
     `unsupported: ["oversized zip part"]`, `expectation: "unsupported_now"`,
     `adapter_expectation: "unsupported"`, and the sha256 of the built bytes.
   - `xml-entity-expansion`, filename `docx-entity.docx`: a DOCX whose
     `word/document.xml` begins with an XML declaration followed by a
     `<!DOCTYPE` block defining nested internal entities, then a normal
     WordprocessingML body referencing the outermost entity. `gold` records the
     same empty structures, `unsupported: ["entity declaration in an OOXML part"]`,
     `expectation: "unsupported_now"`, `adapter_expectation: "unsupported"`, and
     the sha256.

4. Add `"adapter_expectation"` to every one of the existing eighteen cases'
   `gold` dicts. Set it to `"unsupported"` for exactly the six cases whose
   `unsupported` list is non-empty today (the three PDF refusals plus the three
   DOCX refusals) and `"supported"` for the rest. Change nothing else in any
   existing case: not a byte of a builder, not a recorded sha256, not the
   `expectation` value.

5. Extend the module docstring of `fixtures/audit/locator_fidelity_cases.py`
   with one paragraph explaining the two-key arrangement: `expectation` records
   what `auditor.normalize_source` does with these bytes, which is refuse, and
   stays `unsupported_now` permanently because `auditor` normalizes decoded text
   and never sees a PDF or a DOCX; `adapter_expectation` records what
   `source_adapters.import_source` does with them, which is what Phase 14C
   changed. Naming both keeps the Phase 11 gate honest and the Phase 14C gate
   meaningful at the same time.

6. Add `check_zip_bomb_guard`, `check_xml_entity_guard`, and
   `check_gold_manifest_additive` to `tests/source_adapters_roundtrip.py` and to
   its `__main__` check sequence.
  </action>
  <verify>
  <automated>python3 tests/source_adapters_roundtrip.py &amp;&amp; python3 tests/audit_coverage_roundtrip.py</automated>
Expected: both exit 0. The second is the load-bearing one: it proves the fixture
extension was additive and the Phase 11 gate is untouched. The degraded state
this task must prove is that the guard refuses in bounded time rather than after
decompressing, asserted by the five-second wall-clock bound inside
`check_zip_bomb_guard`.
  </verify>
  <acceptance_criteria>
- `python3 tests/source_adapters_roundtrip.py` exits 0.
- `python3 tests/audit_coverage_roundtrip.py` exits 0 with its existing output
  line unchanged apart from the case count.
- `python3 -c "import sys,os; sys.path.insert(0,os.path.join('fixtures','audit')); import locator_fidelity_cases as g; assert len(g.CASE_TABLE)==20; assert all('adapter_expectation' in c['gold'] for c in g.CASE_TABLE); assert all(c['gold']['expectation']=='unsupported_now' for c in g.CASE_TABLE); print('fixtures additive')"` prints `fixtures additive`.
- `python3 -c "import source_adapters as s; assert callable(s._read_zip_part) and callable(s._parse_xml_safely); print('zip seam present')"` prints `zip seam present`.
- `grep -c "DOCTYPE" source_adapters.py` returns at least 1, confirming the
  entity-declaration refusal is present in source and not merely intended.
- `python3 itembank.py guard .` exits 0.
- No file changed by this task contains an em dash character.
  </acceptance_criteria>
  <precondition>Plan 14C-01 landed source_adapters.py with SOURCE_ADAPTER_CODES and the extraction-function four-tuple contract.</precondition>
  <reversibility rating="reversible">Both helpers are new private functions with no external consumers; the fixture change is additive and its removal restores the file exactly.</reversibility>
  <done>One hardened seam exists that every container adapter reads through, and two adversarial fixtures prove it refuses in bounded time.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: the DOCX adapter, including the four parts python-docx never surfaces</name>
  <files>source_adapters.py, tests/source_adapters_roundtrip.py</files>
  <read_first>
- `.planning/phases/14C-source-adapter-registry/14C-RESEARCH.md`, Pitfall 1 in
  full, and the Code Examples section headed "DOCX footnote read (direct XML,
  the part python-docx does not expose)".
- `fixtures/audit/locator_fidelity_cases.py` lines 400 to 612, all twelve DOCX
  gold cases. Read every one. Lines 452 to 465 carry the footnote and endnote
  XML the adapter must be able to read back out, and lines 498 to 560 carry the
  header, footer, tracked-change, and comment cases. The `reading_order` id
  shapes recorded there (`h1.0`, `li.0`, `li.1`, `t.r0c0`, `p.0`, `fn.1`,
  `en.1`, `hdr`, `ftr`, `ins.1`, `del.2`, `cmt.1`) are the exact strings the
  adapter must produce; do not redesign them.
- `fixtures/audit/locator_fidelity_cases.py` lines 132 to 182 again, so the
  adapter reads back exactly the parts the builders write.
- `source_adapters.py` as landed by plan `14C-01` and extended by Task 1: the
  four-tuple extraction contract, `_read_zip_part`, `_parse_xml_safely`, and
  the lazy per-adapter import discipline in `_extract_pdf`.
- The frozen `body_docx` row in `14C-01-PLAN.md`'s "The frozen sidecar contract"
  section: required `medium` const `"docx"`, `part` enum, `paragraph_index`,
  and `ref_id`.
  </read_first>
  <behavior>
Write these assertions first, watch them fail, then implement.

- `check_docx_gold_cases`: for each of the twelve DOCX cases in
  `CASE_TABLE`, materialize the bytes, run `_extract_docx`, and assert that the
  produced `reading_order` equals `case["gold"]["reading_order"]` exactly, in
  order, for every case whose `adapter_expectation` is `"supported"`; and that
  the result is a typed refusal whose message equals the recorded
  `unsupported[0]` string for every case whose `adapter_expectation` is
  `"unsupported"`.
- `check_docx_extra_parts`: the four extra-parts cases specifically
  (`docx-footnote-endnote`, `docx-header-footer`, `docx-tracked-changes`,
  `docx-comments`) each produce at least one locator whose `body["part"]` is
  not `"body"`, and the set of distinct `body["part"]` values across those four
  cases is exactly `{"footnote", "endnote", "header", "footer", "comment"}` plus
  `"body"`. Tracked insertions and deletions are `part` `"body"` with `kind`
  `tracked_insert` and `tracked_delete`, because they live in the body part.
  This assertion is the one that goes red when an adapter is built on
  python-docx alone.
- `check_docx_end_to_end`: one DOCX gold case imported through
  `source_adapters.import_source` produces a schema-valid sidecar, one applied
  journal entry, and a derived Markdown whose line count equals the sidecar's
  `reading_order` length.
  </behavior>
  <action>
1. Implement `_extract_docx(raw_bytes, options)` in `source_adapters.py`.
   Import `docx` inside the function body; on `ImportError` return
   `source.dependency_missing` whose message ends with the literal
   `run: pip install python-docx==1.2.0`. Open the bytes as a
   `zipfile.ZipFile(io.BytesIO(raw_bytes))` inside a `try` and
   `except zipfile.BadZipFile`, converting to `source.malformed_input`.

2. Walk the body in document order with python-docx: iterate
   `document.element.body` children rather than `document.paragraphs` followed
   by `document.tables`, because those two lists lose the interleaving and the
   `docx-nested-table` gold case depends on the real order. Emit, per element:
   - a `w:p` carrying a heading style: locator id `"h%d.%d" % (level, index)`,
     `kind` `"heading"`, body `part` `"body"`.
   - a `w:p` carrying a list numbering property: locator id `"li.%d" % index`,
     `kind` `"list_item"`.
   - any other `w:p`: locator id `"p.%d" % index`, `kind` `"paragraph"`.
   - a `w:tbl`: one locator per cell, id `"t.r%dc%d" % (row, col)`, `kind`
     `"table_cell"`.
   - a `w:ins` run inside a paragraph: id `"ins.%d" % index`, `kind`
     `"tracked_insert"`. A `w:del` run: id `"del.%d" % index`, `kind`
     `"tracked_delete"`.
   - a `w:commentRangeStart`: id `"cmt.%s" % comment_id`, `kind` `"comment"`,
     body `part` `"comment"`, `ref_id` the comment id string.
   Match the recorded gold ids exactly. Where a gold case records `"p1.0"` style
   ids and another records `"p.0"` style ids, follow the recorded string for
   that case; the fixture is the specification and the adapter conforms to it,
   not the other way round.

3. Implement `_docx_extra_parts(zf, options)`, which reads the parts
   python-docx never exposes, each through `_read_zip_part` and
   `_parse_xml_safely`, skipping any part the archive does not contain:
   - `word/footnotes.xml`: one locator per `w:footnote` whose `w:id` is not
     `"0"` or `"-1"` (those two are the separator and continuation separator
     that Word always writes). Locator id `"fn.%s" % footnote_id`, `kind`
     `"footnote"`, body `part` `"footnote"`, `ref_id` the id string.
   - `word/endnotes.xml`: the same shape with id `"en.%s"`, `kind` `"endnote"`,
     `part` `"endnote"`.
   - every member matching `word/header*.xml`: id `"hdr"` when there is one and
     `"hdr%d"` when there are several, matching whichever the gold case records,
     `kind` `"header"`, `part` `"header"`.
   - every member matching `word/footer*.xml`: the same with `"ftr"`, `kind`
     `"footer"`, `part` `"footer"`.
   - `word/comments.xml`: one locator per `w:comment`, id `"cmt.%s" % id`,
     `kind` `"comment"`, `part` `"comment"`, `ref_id` the id string.
   Text is joined from every `w:t` descendant with
   `"".join(t.text or "" for t in element.iter(W_NS + "t"))`.

4. Append the extra-parts locators to the body locators in the order the gold
   cases record. Read each gold case's `reading_order` to see where the header,
   footer, footnote, and comment entries sit relative to the body entries; the
   `docx-header-footer` case records header first and footer last, and the
   footnote case records the footnote after the body paragraph.

5. Register `"docx"` in `ADAPTER_REGISTRY` and add `"docx": "1.0.0"` to
   `ADAPTER_VERSIONS`.

6. Refusals: a DOCX with no `word/document.xml` member returns
   `source.malformed_input`; an encrypted OOXML container, which presents as a
   Compound File Binary rather than a zip and therefore raises
   `zipfile.BadZipFile`, returns `source.encrypted` when the first eight bytes
   equal the OLE compound-file signature and `source.malformed_input` otherwise;
   a document part that parses but yields zero locators returns
   `source.unsupported` with the exact message the corresponding gold case
   records.

7. Add `check_docx_gold_cases`, `check_docx_extra_parts`, and
   `check_docx_end_to_end` to `tests/source_adapters_roundtrip.py` and to its
   `__main__` sequence.
  </action>
  <verify>
  <automated>python3 tests/source_adapters_roundtrip.py</automated>
Expected: exit 0. The degraded state this task must prove is the missing
dependency: with `docx` unimportable, `_extract_docx` returns
`source.dependency_missing` naming the install command, while the markdown and
pdf adapters in the same process are unaffected. Extend
`check_degrades_without_dependencies` from plan `14C-01` with the docx case
rather than writing a second test.
  </verify>
  <acceptance_criteria>
- `python3 tests/source_adapters_roundtrip.py` exits 0.
- `python3 -c "import source_adapters as s; assert 'docx' in s.ADAPTER_REGISTRY and s.ADAPTER_VERSIONS['docx']=='1.0.0'; print('docx registered')"` prints `docx registered`.
- `grep -c "word/footnotes.xml" source_adapters.py` returns at least 1,
  `grep -c "word/comments.xml" source_adapters.py` returns at least 1, and
  `grep -c "word/endnotes.xml" source_adapters.py` returns at least 1. These
  three greps are the mechanical proof that the four extra-parts cases were not
  quietly skipped.
- `python3 tests/audit_coverage_roundtrip.py` exits 0.
- `python3 itembank.py guard .` exits 0.
- `git diff --stat runtime.py model.py` reports no change.
- No file changed by this task contains an em dash character.
  </acceptance_criteria>
  <precondition>python-docx 1.2.0 is installed from deps/source-adapter-pins.txt, and Task 1's _read_zip_part and _parse_xml_safely exist.</precondition>
  <reversibility rating="reversible">A new registry entry and a new private extraction function; removing them restores the plan 14C-01 state exactly.</reversibility>
  <done>All twelve DOCX gold cases resolve to their recorded reading order, including the four parts python-docx does not surface.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: finish the PDF locators and prove the two-file write is atomic as a pair</name>
  <files>source_adapters.py, tests/source_adapters_roundtrip.py, tests/file_fault_tracer.py</files>
  <read_first>
- `fixtures/audit/locator_fidelity_cases.py` lines 205 to 345, the
  `pdf-two-column-reordered`, `pdf-table`, `pdf-footnote`, and remaining PDF
  cases with their exact `reading_order` id shapes (`p1.c1.0`, `t.r0c0`,
  `fn1.0`).
- `.planning/phases/14C-source-adapter-registry/14C-RESEARCH.md`, Pitfall 5 in
  full, on pdfplumber's cost profile.
- `tests/file_fault_tracer.py` in full. It is the existing fault-injection
  harness and the plan's `check_two_file_pair_atomicity` follows whatever
  patching idiom it already uses; read how it currently intercepts
  `journal._write_bytes_atomic` before writing a second interception.
- `journal.py` lines 214 to 227 (`_write_bytes_atomic`) and 330 to 356
  (`commit_operation`), so the injection point is chosen deliberately.
- `.planning/phases/14C-source-adapter-registry/14C-VALIDATION.md`, the
  "Two-file atomic write" row of the per-task verification map. That row is the
  frozen behavior this task satisfies.
  </read_first>
  <behavior>
Write these assertions first, watch them fail, then implement.

- `check_pdf_gold_cases`: every PDF case in `CASE_TABLE` whose
  `adapter_expectation` is `"supported"` produces a `reading_order` equal to its
  recorded value, including `["p1.c1.0", "p1.c1.1", "p1.c2.0", "p1.c2.1"]` for
  the two-column case and the six `t.rNcM` ids for the table case. Every case
  whose `adapter_expectation` is `"unsupported"` returns a typed refusal whose
  message equals the recorded `unsupported[0]` string verbatim, which for the
  three refusal cases is `image-only page: no text-bearing structure`,
  `encrypted PDF: no unauthenticated structure`, and `malformed/truncated PDF`.
- `check_two_file_pair_atomicity` in `tests/file_fault_tracer.py`, three
  scenarios, each starting from a base that already holds one accepted source
  pair from a previous import:
  1. The sidecar write raises `OSError` partway. Assert: the previous Markdown
     and the previous sidecar are both byte-identical to before, no new journal
     entry of any state exists for a new object, and no `.tmp` file remains.
  2. The sidecar write succeeds and the journal append then raises. Assert: the
     previous Markdown is byte-identical, the orphan sidecar has been removed by
     the cleanup path, no `applied` entry exists for the new object, and
     `journal.read_registry(base)` contains no new object id.
  3. The journal append succeeds and the process is interrupted immediately
     after. Assert: both new files exist, the sidecar's `fingerprint` equals the
     new registry row's `fingerprint`, and `journal.replay(base)` reproduces the
     same registry.
  The property asserted across all three: at no point does an `applied` source
  object exist on disk without a valid sidecar beside it.
  </behavior>
  <action>
1. Extend `_extract_pdf` with column detection: group each page's words by their
   `x0` into left and right bands using the page width midpoint, and when both
   bands hold words, emit ids of the form `"p%d.c%d.%d" % (page, column, index)`
   with `body["column"]` set to the one-based column number. When only one band
   holds words, keep the existing `"p%d.%d"` shape and `body["column"]` of
   `None`. The `pdf-two-column-reordered` gold case is the acceptance test for
   this and its recorded order is column-major, left column fully before right
   column, which is what a reading-order-faithful extraction must produce.

2. Extend `_extract_pdf` with table locators: call `page.find_tables()` and, for
   each table, emit one locator per cell with id `"t.r%dc%d" % (row, col)`,
   `kind` `"table_cell"`, and `body["medium"] == "pdf"` carrying `page`, the
   cell's `index` within the reading order, and the cell `bbox`. Add a `kind`
   `"table"` locator for the table itself with the same page. Guard the call
   behind the `page.chars` emptiness check from plan `14C-01` step 6, per
   RESEARCH Pitfall 5, so a page with nothing to extract never reaches the
   expensive call.

3. Emit footnote locators for the `pdf-footnote` case with id `"fn%d.%d"`,
   `kind` `"footnote"`. A PDF has no footnote structure, so detection is
   positional: a text line in the bottom fifth of the page whose font size is
   smaller than the page's modal body font size. Record that heuristic in the
   function docstring and record its confidence honestly by setting the
   sidecar's envelope `confidence` to `"medium"` for any PDF whose locator set
   includes a footnote, and `"high"` otherwise. This is what the envelope
   `confidence` field is for; do not leave it `"high"` for a heuristic result.

4. Make the three PDF refusal messages exact. Return
   `image-only page: no text-bearing structure` when no page yields a character,
   `encrypted PDF: no unauthenticated structure` when pdfplumber or pdfminer
   reports the document is encrypted, and `malformed/truncated PDF` when the
   parse fails. These three strings are already recorded in the gold cases and
   must be reproduced character for character; a paraphrase fails
   `check_pdf_gold_cases`.

5. Add `check_two_file_pair_atomicity` to `tests/file_fault_tracer.py`,
   following the interception idiom that file already uses, and register it in
   that file's own check sequence. Do not create a second fault-injection
   harness; `tests/file_fault_tracer.py` is the one that exists.

6. Add `check_pdf_gold_cases` to `tests/source_adapters_roundtrip.py` and to its
   `__main__` sequence.
  </action>
  <verify>
  <automated>python3 tests/source_adapters_roundtrip.py &amp;&amp; python3 tests/file_fault_tracer.py</automated>
Expected: both exit 0. The degraded state this task must prove is scenario 2 of
`check_two_file_pair_atomicity`: a rights-refused or otherwise failed journal
append leaves no orphan sidecar and no half pair, which is the whole reason the
sidecar is written first.
  </verify>
  <acceptance_criteria>
- `python3 tests/source_adapters_roundtrip.py` exits 0.
- `python3 tests/file_fault_tracer.py` exits 0 and its output names
  `check_two_file_pair_atomicity`.
- `grep -c "image-only page: no text-bearing structure" source_adapters.py`
  returns at least 1.
- `grep -c "encrypted PDF: no unauthenticated structure" source_adapters.py`
  returns at least 1.
- `python3 -c "import sys,os; sys.path.insert(0,os.path.join('fixtures','audit')); import locator_fidelity_cases as g; pdf=[c for c in g.CASE_TABLE if c['kind']=='pdf']; assert len(pdf)>=9; print('pdf cases', len(pdf))"` prints a count of at least 9.
- `for t in tests/*.py; do python3 "$t" || exit 1; done` exits 0.
- `python3 itembank.py guard .` exits 0.
- No file changed by this task contains an em dash character.
  </acceptance_criteria>
  <precondition>pdfplumber 0.11.10 is installed, and tests/file_fault_tracer.py exists from Phase 14A with its interception harness intact.</precondition>
  <reversibility rating="reversible">Locator emission is additive inside one private function; the fault tracer gains one check function.</reversibility>
  <done>Every non-refusing PDF gold case matches its recorded reading order, the three refusal messages match character for character, and the sidecar-then-journal ordering is proven by fault injection rather than asserted in prose.</done>
</task>

</tasks>

<threat_model>
ASVS level 1. Block on `high`.

## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Learner-supplied container bytes to stdlib zipfile | A crafted DOCX, PPTX, or EPUB archive reaches `zipfile` inside itembank's process. |
| Container XML part to stdlib expat | A crafted OOXML part reaches `xml.etree.ElementTree`. |
| Learner-supplied PDF bytes to pdfplumber | A crafted or merely enormous PDF reaches a third-party parser. |
| Adapter to durable disk | Two files are written as one logical pair. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-14C-09 | Denial of Service | `_read_zip_part` on a compression bomb | high | mitigate | The declared `ZipInfo.file_size` is checked against `options["max_input_bytes"]` before `zf.read` is called, so a high-ratio member is refused with `source.oversized` without decompressing. Member count is capped at `MAX_ZIP_MEMBERS`. Asserted by `check_zip_bomb_guard` with a five-second wall-clock bound, so a guard that only refuses after decompressing fails the test. |
| T-14C-10 | Denial of Service | `_parse_xml_safely` on entity expansion | high | mitigate | Bytes containing `<!DOCTYPE` or `<!ENTITY` are refused before the parser is invoked at all. Neither is legal in a well-formed OOXML part, so the refusal costs no real document anything and removes the class rather than bounding it. Asserted by `check_xml_entity_guard`. |
| T-14C-11 | Tampering | crafted zip member name | high | mitigate | A member name that is absolute or contains a `..` segment after normalization is refused with `source.malformed_input` inside `_read_zip_part`, before any read. The adapter never calls `extractall` and never writes a member to disk under its archive-supplied name. |
| T-14C-12 | Repudiation | a crash between the two writes | medium | mitigate | The sidecar is written first and removed on a journal refusal; `check_two_file_pair_atomicity` injects a fault at each of the three points and asserts that an applied source object never exists without a valid sidecar beside it. |
| T-14C-13 | Denial of Service | pdfplumber geometry on a large scanned PDF | medium | mitigate | `page.chars` is checked before `extract_words` and `find_tables`, so a page with nothing to extract short-circuits to the page-level refusal without touching the expensive layout walk (RESEARCH Pitfall 5). |
| T-14C-14 | Information Disclosure | tracked deletions and comments in a shared document | low | accept | A DOCX's tracked deletions and comment threads are extracted into the derived Markdown because the gold cases require them as citable locators. They stay on the learner's disk under the approved root; nothing transmits them. Recorded here so it is a known property and not a surprise. |
| T-14C-SC | Tampering | npm/pip/cargo installs | high | mitigate | No new package is introduced by this plan. python-docx was reviewed and pinned by plan `14C-01` Task 2's blocking human checkpoint; `deps/source-adapter-pins.txt` is not edited here. |
</threat_model>

<out_of_scope>
- **PPTX and EPUB.** They use `_read_zip_part` and `_parse_xml_safely` built
  here, but their adapters are plans `14C-03` and `14C-07`.
- **`defusedxml`.** The DOCTYPE refusal removes the entity-expansion class
  outright, so the dependency does not clear
  `SUPPLY-CHAIN-POLICY.md` section 3's "it does not earn its cost" bar. Do not
  add it. If a future format legitimately needs a DOCTYPE, that is a new
  adoption-gate decision.
- **`pypdf`.** It is pinned as the recorded page-level fallback but is not
  wired in this plan. Wiring a fallback path before the primary path has a
  measured failure is speculative; the first real PDF that pdfplumber cannot
  read is the trigger.
- **Changing any existing gold case's `expectation`, builder bytes, or recorded
  sha256.** The extension is additive or it is wrong.
- **A second fault-injection harness.** `tests/file_fault_tracer.py` is the one
  that exists.
- **Any change to `runtime.py`, `model.py`, `auditor.py`, or `surfaces/`.**
</out_of_scope>

<verification>
1. `python3 tests/source_adapters_roundtrip.py` (exit 0)
2. `python3 tests/file_fault_tracer.py` (exit 0)
3. `python3 tests/audit_coverage_roundtrip.py` (exit 0)
4. `python3 schema_validate.py --all` (exit 0)
5. `for t in tests/*.py; do python3 "$t" || exit 1; done` (exit 0)
6. `python3 itembank.py guard .` (exit 0)
7. `git diff --stat runtime.py model.py auditor.py` (no output)
</verification>

<success_criteria>
- All twelve DOCX gold cases and all PDF gold cases resolve as recorded.
- The zip and XML guards refuse in bounded time, proven by a wall-clock bound.
- The two-file pair is proven atomic by three injected faults.
- The Phase 11 eighteen-case gate is untouched and still green.
- Zero em dash characters in any file this plan created or changed.
</success_criteria>

<summary_obligations>
`.planning/phases/14C-source-adapter-registry/14C-02-SUMMARY.md` records:

- Any gold case whose recorded `reading_order` the adapter could not reproduce,
  with the produced order beside the recorded one. Do not silently relax a gold
  case; report the mismatch and stop.
- The real key names of `pdfplumber.Page.find_tables()` cell objects, since the
  plan describes them from documentation and not from a run.
- Whether any DOCX gold case needed a locator id shape different from the one
  this plan predicted, so plans 03 and 07 inherit the correction.
- Which truth was verified by which command and which `check_*` function.
</summary_obligations>

<output>
Create `.planning/phases/14C-source-adapter-registry/14C-02-SUMMARY.md` when done.
</output>
