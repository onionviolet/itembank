---
phase: 14C-source-adapter-registry
plan: 07
type: execute
wave: 7
depends_on: ["14C-06"]
files_modified:
  - source_adapters.py
  - fixtures/audit/epub_fidelity_cases.py
  - tests/source_adapters_roundtrip.py
  - .planning/IDEA-LEDGER.md
  - .planning/phases/14C-source-adapter-registry/14C-DECISIONS.md
autonomous: false
requirements: [D-01, D-05, ROSTER-7-EPUB, PORT-02, TREAT-02]
estimate:
  tokens: 140000
  raw_tokens: 70000
  tasks: 3
  confidence: low
must_haves:
  truths:
    - "An EPUB imports through the one path with no new dependency: the container is read with stdlib zipfile and xml.etree through the same hardened seam the DOCX and PPTX adapters use, so ebooklib's AGPL license never becomes a decision this phase forces."
    - "Spine order is preserved. Content documents are read in the order the OPF package document lists them in its spine element, not in filename order and not in manifest order, so a book's chapters arrive in reading order."
    - "One fragment-anchored citation resolves: a locator carrying a spine_idref plus an element_index plus a fragment resolves back to the exact element in the exact content document it came from."
    - "A DRM-locked or encrypted EPUB returns a typed unsupported result naming encryption, writes nothing, and appends no journal entry. It is never a silent partial extraction of whatever happened to decrypt."
    - "The ebooklib AGPL finding is recorded as a dated, appended decision with a reconsideration condition, in both the phase decisions file and the idea ledger, so the parking is a durable record rather than a fact that existed only in a research document."
    - "REQUIREMENTS.md's EPUB position is unchanged by this plan: PORT-02 already describes EPUB as an interchange prototype with an explicit semantic loss report, and this adapter's sidecar unsupported list is that loss report for the import direction."
  prohibitions:
    - statement: "No second parser, scorer, or evidence store. The OPF and NCX reads use the same _read_zip_part and _parse_xml_safely seam plan 14C-02 built; no second container reader is written."
      status: flagged-unverified
      verification: "check_epub_uses_shared_seam asserts that inspect.getsource of _extract_epub contains _read_zip_part and _parse_xml_safely and contains no direct ZipFile.read call; check_no_second_parser is re-run."
    - statement: "No rewrite of itembank in TypeScript and no plugin kernel reimplemented in Python."
      status: flagged-unverified
      verification: "files_modified contains two Python files, one fixture file, and two planning documents, none of them a loader or kernel module."
    - statement: "No hosted multi-tenant anything."
      status: flagged-unverified
      verification: "every fixture materializes into a tempfile.mkdtemp() base; the fixture module writes nothing in the repository."
    - statement: "PyMuPDF is not adopted, and ebooklib is not adopted. Both stay parked on an explicit Weibao AGPL decision, now recorded in two durable places."
      status: flagged-unverified
      verification: "grep -i -E 'pymupdf|fitz|ebooklib' source_adapters.py fixtures/audit/epub_fidelity_cases.py deps/source-adapter-pins.txt finds no import and no pin line; the parking record exists in 14C-DECISIONS.md and in .planning/IDEA-LEDGER.md."
    - statement: "An unresolved rights grant is never treated as permissive."
      status: flagged-unverified
      verification: "check_rights_refusal is re-run with an EPUB input."
  artifacts:
    - "fixtures/audit/epub_fidelity_cases.py with its own CASE_TABLE, sha256 helper, epub_bytes builder, and materialize function"
    - "_extract_epub, _epub_container_root, and _epub_spine_order in source_adapters.py"
    - "the epub key in ADAPTER_REGISTRY"
    - "check_epub_gold_cases, check_epub_spine_order, check_epub_fragment_anchor, check_epub_drm_refused, and check_epub_uses_shared_seam in tests/source_adapters_roundtrip.py"
    - "the D-14C-2 AGPL parking record in 14C-DECISIONS.md and its ledger entry in .planning/IDEA-LEDGER.md"
  key_links:
    - "An EPUB's spine order is the order of itemref elements in the OPF package document's spine element, each referencing a manifest item by idref. Filename order and manifest order are both wrong and both look plausible on a tidy fixture, which is why the gold corpus includes a book whose three chapters are named in one order and spined in another."
    - "META-INF/container.xml names the OPF package document's path with a rootfile full-path attribute. Hard-coding OEBPS/content.opf works on most books and fails on the rest, silently, with a file-not-found that looks like a malformed EPUB."
    - "An encrypted EPUB carries META-INF/encryption.xml. Its presence is the DRM signal and must be checked before any content document is read, because a DRM-locked book's spine and manifest parse perfectly well and only the content is unreadable, which would otherwise produce a book-shaped source with garbage in it."
    - "REQUIREMENTS.md:763 and its surrounding PORT-02 text describe EPUB as an interchange prototype in the export direction. This plan adds the import direction and changes no requirement text; the sidecar unsupported list is the semantic loss report PORT-02 already asks every interchange adapter to carry."
---

<objective>
Land EPUB import. `14C-CONTEXT.md` roster item 7 records that EPUB is currently
export-only and that import is additive.

The research pass surfaced a finding CONTEXT.md does not mention and that this
plan is built around: `ebooklib`, the obvious EPUB library, is AGPL, verified
from its own PyPI license metadata. `SUPPLY-CHAIN-POLICY.md` section 2.4 routes
copyleft to an explicit Weibao decision, which is exactly where PyMuPDF already
sits. Rather than force a second AGPL decision to ship one adapter, this plan
takes the stdlib path: EPUB is a zip of XHTML with an XML package document, and
plan `14C-02` already built the hardened zip and XML seam that reads exactly that
shape. The parking is then recorded properly, in two durable places, so it is a
decision with a reconsideration condition rather than a fact that lived only in a
research document.

Decisions already made, cited, and never re-litigated here:

- **D-01** (`14C-CONTEXT.md` lines 22 to 27): PyMuPDF stays parked on its AGPL
  decision. Adoption runs through `SUPPLY-CHAIN-POLICY.md` section 3.
- **`14C-CONTEXT.md` out-of-scope list**: adopting PyMuPDF is refused. This plan
  extends that refusal to `ebooklib` on identical grounds and records why.
- **D-05**: the adapter never touches the scorer.
- **D-14C-1** (`14C-DECISIONS.md`): the frozen `body_epub` row, required
  `medium` const `"epub"`, `spine_index`, `spine_idref`, `element_index`, and a
  nullable `fragment`.
- **`14C-RESEARCH.md` Open Question 1**: model the fragment anchor loosely on
  EPUB CFI's step-path idea but do not require full CFI compliance, because
  itembank's own reader is the only consumer and a simpler anchor is sufficient.
- **`14C-02` Task 1**: `_read_zip_part` and `_parse_xml_safely` are the one
  hardened container seam. EPUB reads through them and adds nothing of its own.
- **PORT-02** (`REQUIREMENTS.md`): interchange adapters carry a supported
  profile, conformance fixtures, and an explicit semantic loss report. The
  sidecar `unsupported` list is that loss report for the import direction.

Purpose: import a book without taking a copyleft dependency, and record the
refusal so it survives this session.
Output: one more registry entry, one gold-case fixture file, and two durable
decision records.
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
@.planning/SUPPLY-CHAIN-POLICY.md
@.planning/IDEA-LEDGER.md
@fixtures/audit/locator_fidelity_cases.py
@source_adapters.py
</context>

## Artifacts this phase produces (plan 14C-07 share)

- `fixtures/audit/epub_fidelity_cases.py`
  - `sha256`, `CASE_TABLE`, `materialize(dest_dir)`, and the builders
    `epub_bytes(opf_path, manifest, spine, documents, extra_parts=None)`,
    `container_xml(opf_path)`, `opf_xml(manifest, spine)`,
    `xhtml_doc(title, blocks)`.
- `source_adapters.py`
  - New functions `_epub_container_root(zf, options)`,
    `_epub_spine_order(opf_element, opf_dir)`,
    `_extract_epub(raw_bytes, options)`.
  - New constants `EPUB_CONTAINER_PATH = "META-INF/container.xml"`,
    `EPUB_ENCRYPTION_PATH = "META-INF/encryption.xml"`, `OPF_NS`, `DC_NS`,
    `CONTAINER_NS`, `XHTML_NS`, and `EPUB_BLOCK_TAGS`.
  - `ADAPTER_REGISTRY` gains `"epub"`; `ADAPTER_VERSIONS` gains
    `"epub": "1.0.0"`.
- `tests/source_adapters_roundtrip.py`
  - The five check functions named in `must_haves.artifacts`.
- `.planning/phases/14C-source-adapter-registry/14C-DECISIONS.md`
  - A new dated section `## D-14C-2. ebooklib is parked on an AGPL decision`.
- `.planning/IDEA-LEDGER.md`
  - One appended entry recording the same parking, with a reconsideration
    condition, following the ledger's existing entry shape.

New refusal codes introduced by this plan: none. `source.encrypted`,
`source.malformed_input`, `source.unsupported`, and `source.oversized` are
already in `SOURCE_ADAPTER_CODES` from plan `14C-01`.

<tasks>

<task type="checkpoint:decision" gate="blocking">
  <name>Task 1: record the ebooklib AGPL parking before writing the stdlib path</name>
  <files>.planning/phases/14C-source-adapter-registry/14C-DECISIONS.md, .planning/IDEA-LEDGER.md</files>
  <read_first>
- `.planning/SUPPLY-CHAIN-POLICY.md` sections 2.4 and 3 in full. Section 2.4:
  copyleft and no-license artifacts require an explicit Weibao decision before
  adoption. Section 3: what a plan owes before adding a dependency, including
  the stdlib alternative considered with its real cost.
- `.planning/phases/14C-source-adapter-registry/14C-RESEARCH.md`, the
  Alternatives Considered row for `ebooklib`, the Package Legitimacy Audit row
  for it, and the State of the Art row recording that the AGPL finding is new as
  of the 2026-08-21 research session.
- `.planning/IDEA-LEDGER.md`, the `IL-20260815-07` entry in full, in particular
  its 2026-08-17 note recording PyMuPDF as parked and not rejected. The new
  entry follows that shape.
- `.planning/PLANNING-DIRECTIVES.md` section 3a, the append-only rejection and
  supersession record: a parked or rejected idea is never deleted, and each
  entry records the proposal, the evidence, the exact reason, the conflicting
  rule, the retained alternative, the date, and the reconsideration condition.
  </read_first>
  <decision>
Is the stdlib `zipfile` plus `xml.etree` path the accepted way to import EPUB,
with `ebooklib` parked alongside PyMuPDF pending an explicit AGPL decision?
  </decision>
  <context>
`ebooklib` 0.20 is AGPL, verified from its own PyPI license metadata during the
2026-08-21 research pass. CONTEXT.md's out-of-scope list already refuses
PyMuPDF on exactly these grounds and does not mention `ebooklib`, because the
finding is newer than CONTEXT.md.

This is recorded as a decision rather than executed silently for one reason:
`SUPPLY-CHAIN-POLICY.md` section 2.4 says copyleft requires an explicit Weibao
decision, and quietly choosing the stdlib path in order to avoid asking is still
making the decision, just without leaving a record. The record is what stops a
future session from adopting `ebooklib` because nobody remembered why it was
not used.

The cost is real and should be stated plainly: the stdlib path means writing
roughly a hundred lines of OPF and container parsing that a library would have
provided, and it means the EPUB adapter reads the spine and the manifest but
does not read the navigation document's hierarchical table of contents, which
`ebooklib` would have given for free. What it buys is that EPUB ships in this
phase instead of waiting on a licensing decision, and that the container reading
goes through the hardened seam plan `14C-02` already built and tested.
  </context>
  <options>
    <option id="option-a">
      <name>RECOMMENDED DEFAULT: stdlib path, ebooklib parked</name>
      <pros>EPUB ships now with no new dependency and no new licensing decision.
      The container read reuses `_read_zip_part` and `_parse_xml_safely`, so the
      zip bomb and entity-expansion guards cover EPUB for free. It mirrors the
      DOCX extra-parts precedent, which already reads OOXML parts with stdlib
      `zipfile` and `xml.etree` and is proven against twelve gold cases. The
      parking is recorded in two durable places with a reconsideration
      condition.</pros>
      <cons>About a hundred lines of container and OPF parsing this project now
      maintains. No hierarchical table of contents from the navigation document
      in this phase.</cons>
    </option>
    <option id="option-b">
      <name>Adopt ebooklib, accepting AGPL</name>
      <pros>Less code. A maintained spine, manifest, and navigation API.</pros>
      <cons>AGPL in a product whose end goal is a packaged desktop app that a
      friend installs (`ROADMAP.md` Phase 18). AGPL's network-use clause is the
      strictest copyleft term in common use, and taking it for one adapter is a
      product-wide licensing commitment. This is Weibao's call and nobody
      else's.</cons>
    </option>
    <option id="option-c">
      <name>Defer EPUB import to a later phase</name>
      <pros>No code and no decision now.</pros>
      <cons>`14C-CONTEXT.md` lists EPUB as roster item 7 of this phase and the
      whole point of D-01 is designing the schema once for every medium.
      Deferring one medium after freezing the schema for all eight leaves a
      `body_epub` definition in the frozen contract with no adapter producing
      it, which is the shape of a contract nobody has tested.</cons>
    </option>
  </options>
  <action>
1. Present the question with all three options and option-a named as the
   recommended default.

2. Record the verbatim answer in
   `.planning/phases/14C-source-adapter-registry/14C-DECISIONS.md` under a dated
   heading `## D-14C-2. ebooklib is parked on an AGPL decision`. The section
   records, per `PLANNING-DIRECTIVES.md` section 3a: the proposal, the evidence
   (the PyPI license metadata finding and its date), the exact reason, the
   conflicting rule quoted from `SUPPLY-CHAIN-POLICY.md` section 2.4, the
   retained alternative (the stdlib path), the date, and the reconsideration
   condition, which is: revisit if a real EPUB proves unreadable by the stdlib
   path, or if the product's licensing posture changes.

3. Append one entry to `.planning/IDEA-LEDGER.md` following the shape of the
   existing `IL-20260815-07` entry: an `IL-` identifier with today's date, the
   proposal, why now, disposition `Parked (needs an explicit Weibao AGPL
   decision)`, and the same revisit trigger. Do not modify or delete any
   existing ledger entry; the ledger is append-only.

4. What the executor does with each answer:
   - **option-a**: proceed to Task 2 unchanged.
   - **option-b**: STOP. Do not proceed. Adopting an AGPL dependency needs the
     full `SUPPLY-CHAIN-POLICY.md` section 3 adoption record plus a
     `VENDORED.md` row plus a legitimacy checkpoint, none of which is in this
     plan. Record the answer, then report that plan `14C-07` needs replanning
     around the dependency.
   - **option-c**: record the answer and report that roster item 7 is deferred.
     Plan `14C-08` must then record, in the phase freeze, that `body_epub` is a
     frozen schema definition with no adapter producing it, so the untested
     contract is a visible known state rather than a silent one.
   - **no answer given**: the wave stops here. An unanswered checkpoint never
     gets a silent default.

5. Neither file gains an em dash character. The existing content of
   `.planning/IDEA-LEDGER.md` is not rewritten.
  </action>
  <verify>
  <automated>grep -c "D-14C-2" .planning/phases/14C-source-adapter-registry/14C-DECISIONS.md</automated>
Expected: returns at least 1. The degraded state this task must prove is the
unanswered one: with no answer recorded, `fixtures/audit/epub_fidelity_cases.py`
must not exist on disk when the wave stops.
  </verify>
  <acceptance_criteria>
- `.planning/phases/14C-source-adapter-registry/14C-DECISIONS.md` contains the
  literal heading `## D-14C-2. ebooklib is parked on an AGPL decision` and a
  section carrying all seven fields `PLANNING-DIRECTIVES.md` section 3a
  requires.
- `.planning/IDEA-LEDGER.md` contains one new `IL-` entry naming `ebooklib` and
  AGPL, and `git diff .planning/IDEA-LEDGER.md` shows additions only, no
  deletions and no modified lines outside the appended block.
- `python3 -c "import sys; t=open('.planning/phases/14C-source-adapter-registry/14C-DECISIONS.md',encoding='utf-8').read(); sys.exit(1 if chr(8212) in t else 0)"` exits 0.
- If the answer is option-b or option-c, `fixtures/audit/epub_fidelity_cases.py`
  does not exist on disk.
  </acceptance_criteria>
  <reversibility rating="one-way">Adopting an AGPL dependency is a product-wide licensing commitment that cannot be quietly undone once the code depends on it; parking it is the reversible branch, which is why parking is the recommended default.</reversibility>
  <resume-signal>Reply with option-a, option-b, or option-c.</resume-signal>
  <done>The ebooklib parking is a dated, durable record in two places, or the wave is stopped with the reason named.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: EPUB gold cases, built by hand from stdlib zipfile</name>
  <files>fixtures/audit/epub_fidelity_cases.py, tests/source_adapters_roundtrip.py</files>
  <read_first>
- `fixtures/audit/locator_fidelity_cases.py` lines 1 to 30, 26 to 28, 132 to
  182, and 613 to 626, for the fixture family contract and the OOXML zip
  assembly idiom an EPUB container follows closely.
- `fixtures/audit/pptx_fidelity_cases.py` as built by plan `14C-03`. Its summary
  recorded the minimal part set that a real library accepted, which is the
  nearest precedent for getting a minimal EPUB container right on the first try.
- `.planning/phases/14C-source-adapter-registry/14C-RESEARCH.md`, the Don't
  Hand-Roll table row for EPUB spine and TOC parsing, which names the exact read
  path: `META-INF/container.xml` to the OPF package document's `spine` and
  `manifest`, then `toc.ncx` for EPUB 2 or the navigation document for EPUB 3.
- `.planning/phases/14C-source-adapter-registry/14C-VALIDATION.md`, the
  "Roster 7 EPUB" row: spine order preserved, one fragment-anchored citation
  resolves, a DRM-locked EPUB returns typed unsupported.
  </read_first>
  <behavior>
Write `check_epub_fixture_determinism` first, watch it fail, then build.

- Every case's `build()` is byte-stable across two calls in one process and
  hashes to its recorded `gold["sha256"]`.
- `materialize()` writes only inside the temporary directory it is given.
- The fixture module has no attribute named `ebooklib` after import, proving it
  builds its bytes by hand.
  </behavior>
  <action>
1. Create `fixtures/audit/epub_fidelity_cases.py` with a module docstring in the
   register of its four sibling fixture files: name the phase and plan (14C,
   plan `14C-07`), state that the case table is immutable data, the builders are
   pure functions, nothing reads or writes the repository, and imports are
   stdlib only (`hashlib`, `io`, `os`, `zipfile`). Add one sentence recording
   that these bytes are hand-assembled specifically because `ebooklib` is parked
   under D-14C-2, so the fixture and the adapter are both stdlib and neither
   depends on the parked library.

2. Implement the builders. A minimal valid EPUB is a zip whose first member is
   an uncompressed `mimetype` file containing exactly
   `application/epub+zip` with no trailing newline, followed by
   `META-INF/container.xml`, an OPF package document at a path the container
   names, and one XHTML content document per spine item. Write the `mimetype`
   member with `zipfile.ZIP_STORED` and every other member with the default
   compression, and use a fixed `ZipInfo` timestamp throughout so the archive
   bytes are deterministic.

3. Build these seven cases. Every `gold` records `sha256`, `structures`,
   `reading_order`, `unsupported`, and `adapter_expectation`.
   - `epub-three-chapters`, filename `book.epub`: OPF at `OEBPS/content.opf`,
     three XHTML documents each with an `h1` and two `p` elements, spined in
     document order. `reading_order` is nine ids of the form
     `"sp%d.%d" % (spine_index, element_index)`, zero-based on both.
     `adapter_expectation` `"supported"`.
   - `epub-spine-out-of-order`, filename `book-reordered.epub`: three documents
     named `chap1.xhtml`, `chap2.xhtml`, `chap3.xhtml`, whose `itemref` entries
     in the OPF `spine` list them in the order 3, 1, 2. `reading_order` follows
     the spine, so the first emitted ids belong to `chap3.xhtml`. This is the
     case that goes red if the adapter sorts filenames or walks the manifest.
     `adapter_expectation` `"supported"`.
   - `epub-nonstandard-opf-path`, filename `book-odd-path.epub`: the OPF lives
     at `content/package.opf` rather than `OEBPS/content.opf`, and
     `META-INF/container.xml` names it. This is the case that goes red if the
     adapter hard-codes the conventional path. `adapter_expectation`
     `"supported"`.
   - `epub-fragment-anchors`, filename `book-anchors.epub`: one document whose
     three `section` elements each carry an `id` attribute. Each emitted locator
     carries a `fragment` equal to that id, and locators for elements with no
     enclosing identified element carry `fragment` `None`.
     `adapter_expectation` `"supported"`.
   - `epub-drm-encrypted`, filename `book-drm.epub`: a structurally valid EPUB
     that additionally contains `META-INF/encryption.xml`. `structures` and
     `reading_order` are empty, `unsupported` is
     `["encrypted EPUB: no unauthenticated content"]`, `adapter_expectation`
     `"unsupported"`.
   - `epub-no-container`, filename `book-no-container.epub`: a zip with a
     correct `mimetype` member but no `META-INF/container.xml`. `unsupported` is
     `["malformed EPUB: no META-INF/container.xml"]`, `adapter_expectation`
     `"unsupported"`.
   - `epub-empty-spine`, filename `book-empty.epub`: a valid container and OPF
     whose `spine` element has no `itemref` children. `unsupported` is
     `["no spine item: the package lists no reading order"]`,
     `adapter_expectation` `"unsupported"`.

4. Compute each case's `sha256` by running the builder once and recording the
   result. Do not hand-write a hash.

5. Implement `materialize(dest_dir)` in the same shape the four sibling fixture
   files use.

6. Add `check_epub_fixture_determinism` to `tests/source_adapters_roundtrip.py`
   and to its `__main__` sequence.
  </action>
  <verify>
  <automated>python3 tests/source_adapters_roundtrip.py</automated>
Expected: exit 0. The degraded state this task must prove is fixture drift
detection, the same guarantee the four sibling fixture files give: a builder
whose output no longer hashes to its recorded gold fails the check.
  </verify>
  <acceptance_criteria>
- `python3 tests/source_adapters_roundtrip.py` exits 0.
- `python3 -c "import sys,os; sys.path.insert(0,os.path.join('fixtures','audit')); import epub_fidelity_cases as g; assert len(g.CASE_TABLE)==7; assert all(set(c['gold'])>={'sha256','structures','reading_order','unsupported','adapter_expectation'} for c in g.CASE_TABLE); print('epub fixtures ok')"` prints `epub fixtures ok`.
- `python3 -c "import sys,os; sys.path.insert(0,os.path.join('fixtures','audit')); import epub_fidelity_cases as g; assert not hasattr(g,'ebooklib'); print('fixture is stdlib only')"` prints `fixture is stdlib only`.
- `python3 -c "import sys,os,tempfile,shutil,zipfile; sys.path.insert(0,os.path.join('fixtures','audit')); import epub_fidelity_cases as g; d=tempfile.mkdtemp(); r=g.materialize(d); z=zipfile.ZipFile(os.path.join(d,'book.epub')); n=z.namelist(); assert n[0]=='mimetype'; assert z.read('mimetype')==b'application/epub+zip'; shutil.rmtree(d); print('container ok')"` prints `container ok`.
- `python3 itembank.py guard .` exits 0.
- The new fixture file contains no em dash character.
  </acceptance_criteria>
  <precondition>Task 1 recorded option-a in 14C-DECISIONS.md.</precondition>
  <reversibility rating="reversible">A new fixture file with no consumers until Task 3.</reversibility>
  <done>Seven deterministic, hand-assembled EPUB fixtures exist, including the three ways a real book differs from the conventional layout.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: the EPUB adapter, spine order and fragment anchors through the shared seam</name>
  <files>source_adapters.py, tests/source_adapters_roundtrip.py</files>
  <read_first>
- `fixtures/audit/epub_fidelity_cases.py` as built in Task 2, all seven cases
  and their recorded reading orders and unsupported messages.
- `source_adapters.py` as landed by plans `14C-01` through `14C-06`, in
  particular `_read_zip_part` and `_parse_xml_safely` from plan `14C-02` Task 1,
  and `_extract_docx`'s use of them, which is the closest working example of
  reading a zip-plus-XML container through the shared seam.
- The frozen `body_epub` row in `14C-01-PLAN.md`'s "The frozen sidecar contract"
  section: required `medium` const `"epub"`, `spine_index` integer minimum 0,
  `spine_idref` string minLength 1, `element_index` integer minimum 0,
  `fragment` nullable string.
- `.planning/phases/14C-source-adapter-registry/14C-RESEARCH.md`, Open Question
  1's EPUB paragraph, which records that a simple
  `{"spine_idref": ..., "element_index": ...}` locator is sufficient because
  itembank's own reader, not a third-party EPUB reading system, is the only
  consumer, and that full CFI compliance is deliberately not required.
  </read_first>
  <behavior>
Write these assertions first, watch them fail, then implement.

- `check_epub_gold_cases`: each of the seven cases produces exactly its recorded
  `reading_order` when `adapter_expectation` is `"supported"`, and a typed
  refusal whose message equals the recorded `unsupported[0]` string when it is
  `"unsupported"`.
- `check_epub_spine_order`: for `epub-spine-out-of-order`, the text of the first
  emitted locator is the text of `chap3.xhtml`, and the `spine_idref` values
  across the emitted locators appear in spine order and not in filename order.
  Assert on the actual text, not only on the ids, so the test fails loudly if
  the adapter produced the right-looking ids from the wrong documents.
- `check_epub_container_indirection`: `epub-nonstandard-opf-path` extracts
  successfully, which proves the OPF path came from
  `META-INF/container.xml`'s `rootfile` and not from a hard-coded constant.
- `check_epub_fragment_anchor`: for `epub-fragment-anchors`, three locators
  carry a non-null `fragment` equal to their enclosing element's `id`, and at
  least one carries `fragment` `None`. Then build an
  `auditor.citation(source_id, fingerprint, span_id)` for one of the anchored
  locators and resolve it back through the sidecar to its
  `(spine_idref, element_index, fragment)` triple, asserting the triple names
  the element the text actually came from. That resolution is the frozen
  behavior row this task satisfies.
- `check_epub_drm_refused`: `epub-drm-encrypted` returns `source.encrypted`,
  writes no Markdown, writes no sidecar, and appends no journal entry. Assert
  additionally that the refusal happens before any content document is read, by
  checking that a deliberately malformed content document inside the same
  fixture never causes a different error; the encryption check comes first.
- `check_epub_uses_shared_seam`: `inspect.getsource(_extract_epub)` and the
  sources of its two helpers contain `_read_zip_part` and `_parse_xml_safely`
  and contain no direct `.read(` call on a `ZipFile`. This is the mechanical
  form of the one-seam rule.
- Extend `check_degrades_without_dependencies` with the epub case: with every
  third-party adapter library unimportable, the epub adapter still returns `ok`,
  because it has no third-party dependency at all.
  </behavior>
  <action>
1. Implement `_epub_container_root(zf, options)`. Read
   `EPUB_CONTAINER_PATH` through `_read_zip_part` and parse it through
   `_parse_xml_safely`. Find the first `rootfile` element and take its
   `full-path` attribute. A missing member, a missing `rootfile`, or a missing
   attribute returns the refusal message
   `malformed EPUB: no META-INF/container.xml` for the missing-member case and
   `malformed EPUB: container names no package document` for the other two.
   Return the OPF path and its containing directory, because every manifest
   `href` is relative to the OPF's own directory and joining them against the
   archive root instead is the second most likely silent failure in this
   adapter.

2. Implement `_epub_spine_order(opf_element, opf_dir)`. Build a mapping from
   manifest `id` to the manifest item's `href` resolved against `opf_dir`, then
   walk the `spine` element's `itemref` children in document order and return
   the ordered list of `(spine_idref, resolved_href)` pairs. Skip an `itemref`
   whose `idref` names no manifest item, appending
   `"spine item %s: no manifest entry" % idref` to the unsupported list rather
   than raising. Record in the docstring, in one sentence, that filename order
   and manifest order both look plausible on a tidy book and are both wrong,
   which is why `epub-spine-out-of-order` exists.

3. Implement `_extract_epub(raw_bytes, options)` conforming to the four-tuple
   extraction contract. In order:
   a. Open the bytes as a `zipfile.ZipFile` inside a `try` and
      `except zipfile.BadZipFile`, converting to `source.malformed_input` with
      the message `malformed/truncated EPUB`.
   b. Check for `EPUB_ENCRYPTION_PATH` in the namelist FIRST, before anything
      else is read, and return `source.encrypted` with the message
      `encrypted EPUB: no unauthenticated content` when it is present. A
      DRM-locked book's container, spine, and manifest all parse perfectly well
      and only the content is unreadable, so checking later would produce a
      book-shaped source with garbage in it.
   c. Resolve the OPF through `_epub_container_root`, parse it through
      `_parse_xml_safely`, and resolve the spine through `_epub_spine_order`.
      An empty spine returns
      `no spine item: the package lists no reading order`.
   d. For each spine item in order, read the content document through
      `_read_zip_part` and parse it through `_parse_xml_safely`. XHTML is XML,
      so the shared parser is correct here and no HTML parser is needed; state
      that in a comment, because it is the reason this adapter needs no
      third-party library while the web adapter does.
   e. Walk each document's body for elements whose tag is in
      `EPUB_BLOCK_TAGS` (`h1` through `h6`, `p`, `li`, `blockquote`, `pre`) and
      whose joined descendant text is non-empty. Emit one locator per such
      element with id `"sp%d.%d" % (spine_index, element_index)`, `kind`
      `"spine_item"` for a heading and `"block"` otherwise, and body
      `{"medium": "epub", "spine_index": ..., "spine_idref": ..., "element_index": ..., "fragment": ...}`.
      `fragment` is the nearest enclosing element's `id` attribute walking
      outward from the block, or `None` when no enclosing element carries one.
   f. Emit one Markdown line per locator, in the same order, so the derived
      line count equals the locator count and the `span_id` join from plan
      `14C-01` step 10e is a straight positional map.

4. Register `"epub"` in `ADAPTER_REGISTRY` and add `"epub": "1.0.0"` to
   `ADAPTER_VERSIONS`. Like the transcript adapter, this one imports nothing
   outside the standard library, so it has no lazy-import guard and no
   `source.dependency_missing` path; state that in a comment beside its registry
   entry, together with a pointer to D-14C-2 so a later reader sees why.

5. Record the semantic loss report PORT-02 asks for. Append to the unsupported
   list, without failing the extraction, one entry per construct this adapter
   knowingly drops: `"navigation document not read: no hierarchical table of contents"`,
   and one `"skipped a %s element" % tag` entry per distinct non-block tag
   carrying text that was not emitted (`table`, `figure`, `img` alt text). These
   entries are the import direction's loss report and they are what makes the
   sidecar honest about being a prototype-grade interchange adapter rather than
   a complete one.

6. Set the sidecar envelope `confidence` to `"high"` for EPUB. The reading order
   is declared by the package document rather than inferred, which is a stronger
   guarantee than the PDF adapter's geometry heuristics have.

7. Add every check named in the `behavior` block to
   `tests/source_adapters_roundtrip.py` and to its `__main__` sequence, and
   extend `check_degrades_without_dependencies` with the epub case.
  </action>
  <verify>
  <automated>python3 tests/source_adapters_roundtrip.py</automated>
Expected: exit 0. The degraded states this task must prove: a DRM-locked book is
refused before any content is read; a book with a non-conventional OPF path
still imports; and the whole adapter works with every third-party package
uninstalled.
  </verify>
  <acceptance_criteria>
- `python3 tests/source_adapters_roundtrip.py` exits 0.
- `python3 -c "import source_adapters as s; assert 'epub' in s.ADAPTER_REGISTRY and s.ADAPTER_VERSIONS['epub']=='1.0.0'; assert s.EPUB_CONTAINER_PATH=='META-INF/container.xml'; assert s.EPUB_ENCRYPTION_PATH=='META-INF/encryption.xml'; print('epub registered')"` prints `epub registered`.
- `python3 -c "import inspect, source_adapters as s; src=inspect.getsource(s._extract_epub)+inspect.getsource(s._epub_container_root)+inspect.getsource(s._epub_spine_order); assert '_read_zip_part' in src and '_parse_xml_safely' in src; print('shared seam used')"` prints `shared seam used`.
- `grep -c "encrypted EPUB: no unauthenticated content" source_adapters.py` returns at least 1.
- `grep -c "no spine item: the package lists no reading order" source_adapters.py` returns at least 1.
- `grep -c "navigation document not read" source_adapters.py` returns at least 1.
- `grep -c -i "ebooklib" source_adapters.py` finds the string only on a comment
  line recording D-14C-2, never on an import line.
- `python3 schema_validate.py --all` exits 0.
- `for t in tests/*.py; do python3 "$t" || exit 1; done` exits 0.
- `python3 itembank.py guard .` exits 0.
- `git diff --stat runtime.py model.py auditor.py journal.py` reports no change.
- No file changed by this task contains an em dash character.
  </acceptance_criteria>
  <precondition>Task 1 recorded option-a, Task 2's fixture file exists, and plan 14C-02's _read_zip_part and _parse_xml_safely are present. No third-party package is needed by this task.</precondition>
  <reversibility rating="reversible">One registry entry and three private functions with no external consumers.</reversibility>
  <done>An EPUB imports in spine order with resolvable fragment anchors, a DRM-locked book is refused before its content is touched, and no copyleft dependency entered the tree.</done>
</task>

</tasks>

<threat_model>
ASVS level 1. Block on `high`.

## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Learner-supplied EPUB bytes to stdlib zipfile | A crafted book archive reaches the container reader. |
| Container and OPF XML to stdlib expat | Archive-supplied XML reaches the parser, including a `rootfile` attribute that names another member. |
| Manifest href resolution | An archive-supplied relative path is joined against an archive-supplied directory. |
| Adapter to durable disk | Derived Markdown and a sidecar are written under the approved root. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-14C-43 | Denial of Service | crafted EPUB zip container | high | mitigate | Every member is read through `_read_zip_part` from plan `14C-02`, which checks the declared uncompressed size against `source.max_input_bytes` and caps member count before any decompression. A book with a thousand spine items is bounded by the member cap. |
| T-14C-44 | Denial of Service | entity expansion in `container.xml` or the OPF | high | mitigate | Every XML part is parsed through `_parse_xml_safely`, which refuses any bytes containing `<!DOCTYPE` or `<!ENTITY` before parsing. XHTML content documents go through the same function, which is stricter than a browser but correct for an import path. |
| T-14C-45 | Tampering | a `rootfile` full-path or manifest href escaping the archive | high | mitigate | Both are used only as `zipfile` member lookups through `_read_zip_part`, which refuses an absolute name or a name containing a `..` segment after normalization. Neither is ever joined onto a filesystem path and no member is extracted to disk. |
| T-14C-46 | Spoofing | a DRM-locked book producing a partial source | high | mitigate | `META-INF/encryption.xml` is checked before any content document is read, and its presence returns `source.encrypted` immediately. A DRM-locked book's container and spine parse cleanly, so a later check would produce a book-shaped source containing ciphertext. `check_epub_drm_refused` asserts the ordering, not only the outcome. |
| T-14C-47 | Repudiation | silent semantic loss in an interchange adapter | medium | mitigate | PORT-02 requires an explicit semantic loss report from every interchange adapter. The sidecar `unsupported` list records the unread navigation document and every skipped element type by name, so the losses are reported rather than discovered. |
| T-14C-48 | Information Disclosure | book content on disk | low | accept | A learner's own book stays under their approved root. Nothing transmits it. The rights gate still applies: importing from a linked book file requires its `transform` right to be `granted`. |
| T-14C-SC | Tampering | npm/pip/cargo installs | high | mitigate | No package is introduced or used. `ebooklib` is refused on AGPL grounds and the refusal is recorded in two durable places by Task 1. `deps/source-adapter-pins.txt` is not edited here. |
</threat_model>

<out_of_scope>
- **`ebooklib`.** Parked under D-14C-2 with a recorded reconsideration
  condition. Do not import it, do not pin it, and do not add it to
  `VENDORED.md`.
- **The navigation document and the hierarchical table of contents.** EPUB 3's
  nav document and EPUB 2's `toc.ncx` are not read. This is a recorded loss in
  the sidecar `unsupported` list, not an oversight. Reading them is additive and
  a later plan's if a real book needs it.
- **EPUB CFI.** `14C-RESEARCH.md` Open Question 1 records the decision: model
  the anchor on CFI's step-path idea, do not implement CFI, because itembank's
  own reader is the only consumer.
- **Images, tables, MathML, and SVG inside content documents.** Recorded as
  skipped in the loss report and dropped. Turning a book's figures into media
  artifacts is the `media-intake` skill's territory and its command surface has
  not shipped.
- **EPUB export.** The export direction already exists as a PORT-02 prototype
  and is not touched.
- **Changing any `REQUIREMENTS.md` text.** PORT-02 already covers this adapter's
  obligations and needs no edit.
- **Any change to `runtime.py`, `model.py`, `auditor.py`, `journal.py`, or
  `surfaces/`.**
</out_of_scope>

<verification>
1. `python3 tests/source_adapters_roundtrip.py` (exit 0)
2. `python3 schema_validate.py --all` (exit 0)
3. `for t in tests/*.py; do python3 "$t" || exit 1; done` (exit 0)
4. `python3 itembank.py guard .` (exit 0)
5. `git diff --stat runtime.py model.py auditor.py journal.py` (no output)
6. `git diff .planning/IDEA-LEDGER.md` shows additions only
</verification>

<success_criteria>
- All seven EPUB gold cases resolve as recorded.
- Spine order comes from the OPF, and the OPF path comes from the container,
  both proven by fixtures built to fail the shortcut.
- One fragment-anchored citation resolves back to its exact element.
- A DRM-locked book is refused before its content is touched.
- The ebooklib parking is durable in two places with a reconsideration
  condition.
- Zero em dash characters in any file this plan created or changed.
</success_criteria>

<summary_obligations>
`.planning/phases/14C-source-adapter-registry/14C-07-SUMMARY.md` records:

- The verbatim answer to the Task 1 checkpoint.
- The exact minimal EPUB part set the fixture needed, since the plan describes
  it from format documentation and not from a run.
- Whether `_parse_xml_safely`'s DOCTYPE refusal rejected any legitimate XHTML
  content document, since real XHTML files sometimes carry a doctype declaration
  even though EPUB 3 discourages it. If it did, that is a genuine finding: say
  so, and record whether the refusal should become XHTML-specific rather than
  loosening the guard for every container format.
- Which truth was verified by which command and which `check_*` function.
</summary_obligations>

<output>
Create `.planning/phases/14C-source-adapter-registry/14C-07-SUMMARY.md` when done.
</output>
