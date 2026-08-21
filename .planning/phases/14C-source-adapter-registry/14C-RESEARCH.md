# Phase 14C: Source Adapter Registry - Research

**Researched:** 2026-08-21
**Domain:** File-format and remote-content extraction adapters producing Markdown plus a JSON locator sidecar, journaled through the existing 14A identity/journal kernel and exposed through the existing daemon JSON API
**Confidence:** MEDIUM-HIGH (the PDF/DOCX library choice and the identity/journal integration are HIGH confidence, verified against source; the exact sidecar field names and the remote-staleness mechanism are design recommendations the planner must lock, tagged ASSUMED)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Decisions already made, do not re-litigate

- **D-01. One registry, not one subphase per format.** The locator sidecar
  schema is designed once here. `IL-20260815-07` owns the dependency choices
  already: pdfplumber pinned with pdfminer.six for PDF, python-docx for DOCX,
  pypdf as the page-level fallback. PyMuPDF stays parked on its AGPL decision.
  Adoption runs through `SUPPLY-CHAIN-POLICY.md` section 3.
- **D-02. Python, and the boundary is the existing daemon.** `surfaces/daemon.py`
  already exposes a token-gated JSON API, and line 1022 records that a request
  with no `Origin` header (a CLI or curl-style client) is accepted deliberately.
  Intake gets a route there like every other capability. No TypeScript rewrite,
  no reimplemented plugin kernel. An external harness, DeepSeek's Cordis-based
  one included, is an HTTP client of that route. HTTP is the wider contract:
  Cordis can consume it, and nothing that is not Cordis can consume a Cordis
  plugin.
- **D-03. Remote sources are in scope.** "Learner-owned" is interpretation
  drift, not language from `USER-VISION.md`. Recorded in
  `USER-VISION-INBOX.md` (2026-08-20). Online courses, video, and web material
  are first-class source types.
- **D-04. Bind a snapshot, not a URL.** A remote source has no stable bytes, and
  the whole binding model runs on fingerprints. Capture on bind, fingerprint the
  capture, record the URL and capture timestamp as provenance. This keeps
  citations stable when a video is re-uploaded, keeps bound material readable
  offline (the degrade-never-block rule), and makes a changed remote source a
  detectable stale state rather than a silently broken citation.
- **D-05. The adapter never touches the scorer.** Adapters produce sources.
  One parser, one scorer, one evidence store is unchanged.

### The adapter contract

Every adapter is the same function, differing only in extraction:

    bytes or a fetch descriptor, plus a rights grant
      -> Markdown (plain UTF-8) + a JSON locator sidecar
      -> one fingerprint via identity.object_fingerprint(raw, "source")
      -> one operation journal entry

Failure is explicit and typed. A scanned PDF returns `unsupported` with a reason
code, never a silent empty extraction. Compare-and-swap rules apply: expected
base fingerprint, temp file, validate, atomic commit, journal append.

### The locator sidecar table (envelope + per-medium body)

| Medium | Locator body |
|---|---|
| PDF | page number, plus word or table-cell geometry |
| DOCX | section or paragraph index, footnote and comment refs |
| PPTX | slide number, plus notes-field flag |
| EPUB | spine item plus fragment anchor |
| Web capture | CSS or text anchor, plus capture timestamp |
| Video, audio | start and end timestamps in milliseconds |
| OCR | source page plus bounding box, plus a confidence score |

Envelope fields common to all: `source_id`, `adapter`, `adapter_version`,
`fingerprint`, `captured_at`, `origin` (path or URL), `rights`, `confidence`.
The planner owns turning this table into the frozen schema and its fixture.
Gold cases already exist in `fixtures/audit/locator_fidelity_cases.py`.

### Adapter roster and disposition (build in this order; one plan each)

1. **PDF and DOCX.** Research done, dependencies chosen, gold cases exist.
2. **PPTX.** Unscoped anywhere in `.planning/` until now, and it is how both
   CSCI 1100 and EMT actually run. Clean locators, no rights problem.
3. **Web capture.** Fetch, extract readable text, snapshot, anchor.
4. **Transcript intake.** A learner-supplied `.srt`, `.vtt`, or plain transcript
   with timestamps. No ASR dependency, so it lands cheaply and proves the
   timestamp locator.
5. **Video and audio via ASR.** Needs whisper.cpp or a hosted call. The 7900 XTX
   build does not exist, so this is CPU or hosted at first. Registered, planned
   last.
6. **OCR.** The local-Ollama `ocr` skill exists but is a side tool with no
   binding path, so a photographed page cannot become a cited objective today.
   Wrap the existing skill as an adapter; do not write a second OCR path.
7. **EPUB.** Currently export-only. Import is additive.

### Where considerations conflict, build both

- **Agent auto-fetch versus approve-before-bind.** Build both paths behind one
  setting. Search and read stay free in both. The bind step is the gated one.
  Default to approve-before-bind; the setting exists so the learner can lift it.
- **Snapshot storage: inline copy versus reference plus cache.** Both. Inline
  for anything small enough to live beside the course, cached-with-reference for
  large media. Same fingerprint either way.

### Out of scope, refuse these

- Any second parser, scorer, or evidence store.
- Rewriting itembank in TypeScript, or reimplementing a plugin kernel in Python.
- Hosted multi-tenant anything. Snapshots and evidence stay on disk.
- Adopting PyMuPDF. It is parked on an explicit Weibao AGPL decision.
- Treating an unresolved rights grant as permissive. Unknown rights stay
  restrictive.

### Claude's Discretion

CONTEXT.md is deliberately short (bounded-context format for the lesser-model
executor split) and leaves no separate "discretion" section distinct from the
"build both" and roster items above; those items are this phase's discretion
space. Everything not explicitly a decision, a roster item, or an
out-of-scope refusal is the planner's and researcher's judgment call, most
concretely: the exact sidecar JSON field names and per-medium locator shapes,
the exact daemon route name and body shape, the exact remote-staleness
signal, and whether adapter dependencies are pip-installed at setup time or
first-use-lazy-imported.

### Deferred Ideas (OUT OF SCOPE)

None named separately in CONTEXT.md beyond the "Out of scope, refuse these"
list above, which is reproduced verbatim there.
</user_constraints>

<phase_requirements>
## Phase Requirements

ROADMAP.md assigns no `REQUIREMENTS.md` IDs to Phase 14C; coverage is derived
from CONTEXT.md's five decisions (D-01..D-05), the seven-adapter roster, and
the two "build both" items, per the phase description's own instruction.

| ID | Description | Research Support |
|----|-------------|------------------|
| D-01 | One registry; PDF/DOCX libraries already chosen by IL-20260815-07 | Standard Stack section confirms pdfplumber+pdfminer.six+python-docx+pypdf versions and licenses via `pip index versions` and PyPI JSON metadata (2026-08-21); Package Legitimacy Audit records the automated verdict for each |
| D-02 | Daemon is the boundary; one HTTP route, opaque-identifier addressing | Open Question 3 below traces the exact `API_ROUTES`/`ROUTE_CLI`/`SURFACE_PARITY`/`_reject_cross_origin_write` mechanics a new route must satisfy, read from `surfaces/daemon.py` this session |
| D-03 | Remote sources in scope | Adapter roster items 3-5 (web, transcript, ASR) get library landscape and a stdlib-first fetch pattern in Code Examples / Common Pitfalls |
| D-04 | Bind a snapshot, not a URL; staleness must be detectable without breaking a citation | Open Question 4 below traces `journal.py`'s `object_state`/`detect_external_edits`/`reconcile` machinery and explains why none of it fires for remote staleness, then proposes the advisory-flag design |
| D-05 | Adapter never touches the scorer | Architectural Responsibility Map places every adapter entirely in a new module that imports `identity`/`journal`/`discovery` only, never `model.py` or `runtime.py` |
| Roster 1 (PDF/DOCX) | Adopt IL-20260815-07's recommendation | Standard Stack, Code Examples (locator body shapes traced against `fixtures/audit/locator_fidelity_cases.py`) |
| Roster 2 (PPTX) | New research, unscoped elsewhere | Standard Stack (python-pptx), Code Examples |
| Roster 3 (Web capture) | Fetch, extract, snapshot, anchor | Standard Stack (readability-lxml vs trafilatura), Common Pitfalls (SSRF, JS-rendered pages), Security Domain |
| Roster 4 (Transcript) | `.srt`/`.vtt`, no ASR dependency | Standard Stack (recommend stdlib hand-rolled parser over a dependency) |
| Roster 5 (ASR) | whisper.cpp or hosted; registered, planned last | State of the Art table names the landscape without picking a library (out of this phase's build order) |
| Roster 6 (OCR) | Wrap the existing `ocr` skill, don't reimplement | Common Pitfalls documents the skill's actual output shape (flat text only, read from `scripts/ocr.py`/`scripts/ocr_lib.py` this session) versus the locator table's bbox+confidence ask |
| Roster 7 (EPUB) | Import, additive | Standard Stack flags `ebooklib` as AGPL (verified via PyPI JSON metadata) and recommends a stdlib zipfile+xml.etree path instead, mirroring the DOCX precedent |
| Sidecar schema (open question 1) | Frozen schema + fixture | Open Question 1 below, plus Code Examples |
| Object-kind question (open question 2) | source vs artifact in 14B graph | Open Question 2 below, verified against `identity.py` and `14A-FREEZE.md` |
| Route shape (open question 3) | one route vs one per adapter | Open Question 3 below |
| Stale origin (open question 4) | detectable without breaking citation | Open Question 4 below |
| Install timing (open question 5) | eager vs first-use | Open Question 5 below |
</phase_requirements>

## Summary

This phase closes a schema question the 2026-08-17 PDF/DOCX research pass
deliberately left open, and generalizes it to seven media. The library choice
for PDF and DOCX is already settled and re-verified here against the live
PyPI registry: **pdfplumber 0.11.10** (pinned with **pdfminer.six 20260107**
as its engine) for PDF, **python-docx 1.2.0** for DOCX, **pypdf 6.16.1** as a
page-level fallback. Every one of these libraries, plus **python-pptx 1.0.2**
for the newly-scoped PPTX adapter, is MIT-licensed, pure or near-pure Python,
and ships clean Windows wheels. **PyMuPDF stays parked on its AGPL decision**
exactly as CONTEXT.md instructs. A second copyleft trap surfaced in this
research pass that CONTEXT.md does not mention: **`ebooklib`, the obvious
EPUB library, is AGPL** (verified via its own PyPI license metadata), so the
recommended EPUB path is the same stdlib `zipfile` + `xml.etree` approach the
DOCX fixture builders and the DOCX footnote/header/comment reads already use,
not a new dependency.

The five open questions CONTEXT.md hands the planner all have grounded
answers in code already in this repository:

1. **The sidecar schema** should key its per-medium locator bodies directly to
   the shapes already encoded in `fixtures/audit/locator_fidelity_cases.py`'s
   gold manifests (`page`/`paragraph`/`table`/`footnote`/`header`/`footer` for
   PDF; `heading`/`list_item`/`table`/`footnote`/`endnote`/`tracked_insert`/
   `tracked_delete`/`comment` for DOCX), because that fixture file is the
   acceptance gate IL-20260815-07 already committed to and its `reading_order`
   field is a ready-made linkage between Markdown block order and locator
   identity.
2. **A captured snapshot is a `source` object, not a new kind.**
   `identity.OBJECT_KINDS` is a frozen six-member tuple (`course`,
   `objective`, `source`, `lesson`, `bank`, `component`) and `14A-FREEZE.md`
   states explicitly that adding a kind "forces a review of every
   kind-conditional rule" already in the codebase. The Markdown+sidecar pair
   is one `source` object; the sidecar is a companion file, never a second
   identity-bearing object.
3. **One route, `POST /api/source/import`, with an `adapter` field in the
   body**, not one route per adapter. This is the only shape that fits the
   daemon's own documented pattern (fixed literal paths, opaque identifiers in
   the JSON body, never in the path) and the only shape that does not require
   growing `API_ROUTES`, `ROUTE_CLI`, and `SURFACE_PARITY` by seven entries
   each plus the `check_api_route_scope` length assertion in
   `tests/daemon_roundtrip.py`.
4. **Remote staleness is a read-time advisory flag, never a mutation of the
   accepted revision.** `journal.py`'s `detect_external_edits`/`reconcile`
   machinery exists for *local* file drift and cannot fire for a URL (there is
   no on-disk file to re-hash against the recorded fingerprint). A citation
   that already names a `source_id`+`fingerprint` stays valid forever under
   D-04; "the remote page changed" is new information surfaced as
   `origin_reachable`/`origin_changed` on read, and only becomes a new
   accepted revision when the learner explicitly re-captures.
5. **Dependencies are pip-installed at setup/checkout time (pinned per
   `VENDORED.md`), lazily imported per adapter call (not at module load), and
   later bundled into the Phase 18 PyInstaller artifact** - never fetched
   live from PyPI while the app is running. This is the only reading
   consistent with `SUPPLY-CHAIN-POLICY.md` section 2.1 ("no install-time
   network fetch on the learner's machine") and the packaged-app end goal.

**Primary recommendation:** build one new module (working name
`source_adapters.py`, a peer of `identity.py`/`journal.py`, never inside
`discovery.py`, which is structurally read-only and must stay that way) that
exposes one dispatch function per adapter name, each doing exactly: extract,
write the sidecar file atomically, then call `journal.op_import` (or
`commit_operation` directly for a from-nothing remote capture) for the
Markdown - and wire it to one daemon route plus one CLI command, following
the `seed/accept` precedent for a mutating, loopback-gated route.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Byte extraction (PDF/DOCX/PPTX/EPUB parsing) | New module (`source_adapters.py`) | - | Pure transformation of bytes to Markdown+locators; no identity, no I/O beyond reading the input bytes |
| Identity minting, fingerprinting, journal append | `identity.py` + `journal.py` (existing) | New module calls them | Frozen 14A contract; a new module must never mint an id or fingerprint a different way |
| Remote fetch (web/video/audio capture) | New module (`source_adapters.py`) | - | Uses stdlib `urllib.request` directly, following `surfaces/update.py`'s redirect-hardening precedent; never touches `discovery.py` (which asserts `not hasattr(discovery, "urllib")`) |
| Route exposure | `surfaces/daemon.py` (existing `ROUTES`/`API_ROUTES` tables) | CLI (`surfaces/cli.py`) | D-02: the daemon is the boundary; SURF-04 requires a matching CLI command for the same runtime call |
| Rights gating on extraction | `journal.py`'s existing `op_import` transform-right check | New module supplies `source_object_id` when one exists | RIGHTS-01 is enforced automatically by the existing six-operation vocabulary when a local raw file is first `op_link`ed and then `op_import`ed from; no new rights code is needed for that path |
| OCR text extraction | Existing `.claude/skills/ocr` (wrapped, not reimplemented) | New module's OCR adapter calls `scripts/ocr.py`/`ocr_lib.py` as a subprocess or import | CONTEXT.md roster item 6 is explicit: wrap, do not build a second OCR path |
| Scoring, assessment authority | `runtime.py` (untouched) | - | D-05: adapters produce sources only; this phase adds zero lines to `runtime.py` or `model.py` |

## Standard Stack

### Core

| Library | Version (verified 2026-08-21) | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pdfplumber | 0.11.10 `[VERIFIED: PyPI registry via pip index versions]` | Primary PDF extraction: page, word/char bbox, table cell geometry, `page.search()` | Already the IL-20260815-07 recommendation; only library surveyed that meets every non-scanned/non-encrypted PDF gold case in `fixtures/audit/locator_fidelity_cases.py` without re-implementing pdfminer's layout tree |
| pdfminer.six | 20260107 `[VERIFIED: PyPI registry]` | pdfplumber's underlying engine; per-character bbox, `LTPage`/`LTTextLine` layout tree | Pinned alongside pdfplumber per `research/2026-08-17-pdf-docx-intake.md`; MIT license |
| python-docx | 1.2.0 `[VERIFIED: PyPI registry]` | Primary DOCX extraction: body-order paragraph/table walk, heading styles | Only surveyed DOCX library with a maintained release cadence and MIT license; does not itself read footnotes/headers/comments (see Common Pitfalls) |
| pypdf | 6.16.1 `[VERIFIED: PyPI registry]` | Fallback PDF path: page-level text via `visitor_text`, PDF hygiene (decrypt-check, metadata) | BSD-3, zero required runtime dependencies, weekly release cadence; cannot alone meet column/table/footnote locator cases |
| python-pptx | 1.0.2 `[VERIFIED: PyPI registry, license+deps via PyPI JSON metadata]` | PPTX extraction: slide order, shape text, speaker-notes flag | MIT; only maintained pure-ish-Python PPTX reader surveyed; deps are `lxml`, `Pillow`, `typing_extensions`, `XlsxWriter` (the last is unused for reading but is an unconditional install-time dependency of the package) |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| readability-lxml | 0.8.4.1 `[VERIFIED: PyPI registry+license]` | Web-capture readable-text extraction (Apache-2.0, deps: `chardet`, `lxml[html_clean]`, `cssselect`) | Recommended over `trafilatura` for the web-capture adapter: trafilatura (2.2.0, Apache-2.0) pulls in `courlan`, `htmldate`, `justext`, `charset_normalizer`, `urllib3`, `certifi` as hard runtime deps — a much larger transitive surface than `SUPPLY-CHAIN-POLICY.md` section 3's "near-zero-transitive" preference favors, for a capability (single-page readable-text extraction) readability-lxml already covers |
| stdlib `zipfile` + `xml.etree.ElementTree` | stdlib | EPUB spine/manifest/nav read; also DOCX footnotes/headers/comments/tracked-changes (parts python-docx does not itself surface) | Use in place of a dependency wherever the format is an open zip+XML container and the fixture builders already demonstrate the exact read (see `fixtures/audit/locator_fidelity_cases.py`'s DOCX extra-parts cases) |
| stdlib regex-based SRT/VTT parser (hand-rolled) | n/a | Transcript intake locator (`.srt`/`.vtt` timestamp lines) | The formats are two trivial line-grammars (`HH:MM:SS,mmm --> HH:MM:SS,mmm` for SRT; `HH:MM:SS.mmm --> HH:MM:SS.mmm` plus a `WEBVTT` header for VTT); a dependency (`webvtt-py` 0.5.1, MIT) exists but does not earn its cost for this grammar, per the section-3 adoption gate's "it does not earn its cost must be argued" test |
| `.claude/skills/ocr` (existing, wrapped) | n/a | OCR text extraction for scanned pages/photos | Do not add a new OCR library; CONTEXT.md roster item 6 requires wrapping this skill. Its current output (`scripts/ocr_lib.py`'s `TRANSCRIBE_PROMPT`) is flat transcribed text only — no bounding boxes, no confidence score (see Common Pitfalls) |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| pdfplumber+pdfminer.six | PyMuPDF (fitz) | Best-in-class locator fidelity and speed, but AGPL-3.0/paid-commercial dual license; parked on Weibao's explicit decision per CONTEXT.md, not re-opened here |
| pdfplumber+pdfminer.six | docling (IBM) | Best native provenance (page+bbox on every element) but drags torch/layout models (hundreds of MB-GB); wrong cost profile, cut in the 2026-08-17 pass |
| python-docx + stdlib XML | mammoth | Clean HTML output but no source locators at all (structure preserved, not addressable); cut for import, kept only as a rendering reference |
| stdlib zipfile+xml.etree for EPUB | `ebooklib` 0.20 | Convenient spine/TOC API, but **AGPL** `[VERIFIED: PyPI license metadata, 2026-08-21]` - requires the same explicit Weibao decision PyMuPDF is parked on; the stdlib path avoids that decision entirely and mirrors the already-accepted DOCX-extra-parts precedent |
| readability-lxml for web capture | trafilatura | Trafilatura scores higher on extraction-quality benchmarks but adds 6 hard runtime dependencies (`courlan`, `htmldate`, `justext`, `charset_normalizer`, `urllib3`, `certifi`) versus readability-lxml's 2-3; revisit trafilatura if readability-lxml's quality proves inadequate on real course PDFs-turned-web-pages |
| Hand-rolled SRT/VTT parser | `webvtt-py` 0.5.1 | Small, MIT-licensed, handles edge cases (cue settings, styling) the hand-rolled parser would skip; acceptable low-cost fallback if the hand-rolled parser proves fragile on real transcript files |
| ASR: unresolved, registered last | `faster-whisper` (CTranslate2 backend) vs whisper.cpp bindings (e.g. `pywhispercpp`, MIT) | faster-whisper is fastest on NVIDIA GPUs (not this project's target hardware, a 7900 XTX that does not exist yet); whisper.cpp is a smaller, dependency-light C++ port better suited to a CPU-first, later-AMD-GPU roadmap - this phase does not have to decide, since roster item 5 is explicitly "registered, planned last" |

**Installation (development/checkout time, not runtime-fetched — see Open Question 5):**
```bash
pip install pdfplumber==0.11.10 pdfminer.six==20260107 python-docx==1.2.0 pypdf==6.16.1 python-pptx==1.0.2 readability-lxml==0.8.4.1
```

**Version verification performed this session (2026-08-21):**
```bash
pip index versions pdfplumber        # -> 0.11.10 (latest)
pip index versions pdfminer.six      # -> 20260107 (latest)
pip index versions python-docx       # -> 1.2.0 (latest)
pip index versions pypdf             # -> 6.16.1 (latest)
pip index versions python-pptx       # -> 1.0.2 (latest)
pip index versions readability-lxml  # -> 0.8.4.1 (latest)
pip index versions trafilatura       # -> 2.2.0 (latest)
pip index versions ebooklib          # -> 0.20 (latest)
curl -s https://pypi.org/pypi/<pkg>/json | ...  # license + requires_dist for python-pptx, trafilatura, readability-lxml, ebooklib
```
All confirmed current and installable at time of research; the pdfplumber/pdfminer.six/python-docx/pypdf figures also match `research/2026-08-17-pdf-docx-intake.md`'s findings from four days earlier, re-verified rather than assumed stale.

## Package Legitimacy Audit

Ran via the package-legitimacy seam, ecosystem `pypi`, 2026-08-21:

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| pdfplumber | pypi | published 2026-06-15 (this release) | unknown (checker gap, see note) | github.com/jsvine/pdfplumber | SUS | Kept - see note |
| pdfminer.six | pypi | published 2026-01-07 (this release) | unknown | github.com/pdfminer/pdfminer.six | SUS | Kept - see note |
| python-docx | pypi | published 2025-06-16 (this release) | unknown | github.com/python-openxml/python-docx | SUS | Kept - see note |
| pypdf | pypi | published 2026-08-14 (this release) | unknown | github.com/py-pdf/pypdf | SUS ("too-new" + unknown-downloads) | Kept - see note |
| python-pptx | pypi | published 2024-08-07 (this release) | unknown | github.com/scanny/python-pptx | SUS | Kept - see note |
| readability-lxml | pypi | published 2025-05-03 (this release) | unknown | github.com/buriy/python-readability | SUS | Kept - see note |
| ebooklib | pypi | published 2025-10-26 (this release) | unknown | github.com/aerkalov/ebooklib | SUS; also AGPL | REMOVED from recommendation (AGPL, plus SUS) - use stdlib path instead |
| trafilatura | pypi | published 2026-07-31 (this release) | unknown | github.com/adbar/trafilatura | SUS ("too-new" + unknown-downloads) | Not recommended (dependency weight, see Alternatives) |

**Note on the uniform SUS verdict:** every package above was flagged `SUS` for the single reason `unknown-downloads` (and `pypdf`/`trafilatura` additionally for `too-new`, which reflects only their most recent point-release date, not the project's age). The checker could not retrieve PyPI download-count telemetry for any of these packages in this session; this reads as a gap in the checker's PyPI download-stats source, not a genuine legitimacy signal, since every package resolved to its correct, long-established, canonical GitHub repository (matching the repos already named in `research/2026-08-17-pdf-docx-intake.md`, which independently confirmed release cadence and maintenance signal for pdfplumber/pdfminer.six/python-docx/pypdf four days before this session). Per the Package Legitimacy Gate protocol, `SUS` verdicts are kept, not removed, and each is tagged for the planner to gate behind a `checkpoint:human-verify` task before the corresponding `pip install` runs, even though the reason code itself is judged low-risk here.

**Packages removed due to `[SLOP]` verdict:** none.
**Packages flagged as suspicious `[SUS]`:** pdfplumber, pdfminer.six, python-docx, pypdf, python-pptx, readability-lxml, ebooklib, trafilatura - all for `unknown-downloads`; `pypdf` and `trafilatura` additionally for `too-new`. The planner must add one `checkpoint:human-verify` task before the first `pip install` of any adapter dependency, covering this whole batch in one checkpoint rather than one per package, since they share the identical checker limitation.

**Second-ecosystem check:** none of these are cross-ecosystem name-confusion candidates; all eight resolved to their expected `pypi` names with matching canonical repositories.

**postinstall scripts:** the checker returned `"postinstall": null` for every package above (no npm-style scripts field applies to `pypi`; none of the eight ships a `setup.py` with a network-touching install hook per the maintainers' own published source, though this was not independently re-verified by downloading and inspecting each `sdist` in this session - flag as `[ASSUMED]` if that level of verification is wanted before the checkpoint above is cleared).

## Architecture Patterns

### System Architecture Diagram

```
                    learner or agent (CLI / HTTP client)
                                |
                                v
                  surfaces/cli.py  <-->  surfaces/daemon.py
                  (itembank source     (POST /api/source/import,
                   import ...)          _reject_cross_origin_write gate,
                                        sidecar-token gate when configured)
                                |
                                v
                  source_adapters.py  (NEW - this phase)
                  dispatch("pdf"|"docx"|"pptx"|"epub"|
                           "web"|"transcript"|"asr"|"ocr", input)
                    |         |          |            |
                    v         v          v            v
              pdfplumber  python-docx python-pptx  stdlib zipfile+
              (+pdfminer) + stdlib XML             xml.etree (EPUB)
              pypdf                                readability-lxml (web)
                    |         |          |            |
                    +---------+----------+------------+
                                |
                                v
                  extraction result: Markdown text +
                  locator records (per-medium body, common envelope)
                                |
                                v
              write sidecar .locator.json atomically (temp+fsync+replace)
              [cheap-to-redo file, written FIRST]
                                |
                                v (only if sidecar write succeeded)
              journal.op_link (if new local raw file) then
              journal.op_import(source_object_id=<raw file's id or None>,
                                 kind="source", rel_path=<derived .md>, raw=md_bytes)
              [authoritative, hard-to-redo entry, written SECOND;
               enforces RIGHTS-01's transform-right gate automatically
               when source_object_id is not None]
                                |
                                v
                  _journal/journal.jsonl (append-only)  +
                  _journal/objects.json (disposable projection)
                                |
                                v
                  course/objective binding (Phase 14B, out of this phase's scope)
```

### Recommended Project Structure
```
source_adapters.py       # NEW: one module, one dispatch table, no journal/identity reimplementation
tests/
  source_adapters_roundtrip.py   # NEW: exercises every locator_fidelity_cases.py case plus
                                  #      the new PPTX/EPUB/web/transcript/OCR fixtures this phase adds
fixtures/audit/
  locator_fidelity_cases.py      # EXISTING: extend, do not fork; PDF/DOCX gold cases already here
  pptx_fidelity_cases.py         # NEW, same builder-pattern as the PDF/DOCX file
  epub_fidelity_cases.py         # NEW
  web_capture_fidelity_cases.py  # NEW (static HTML fixtures, no live network in tests)
  transcript_fidelity_cases.py   # NEW (.srt/.vtt byte fixtures)
```

### Pattern 1: Two-step link-then-import for a local raw file already on disk

**What:** When the input is a file the learner already has locally (a PDF,
DOCX, PPTX, or EPUB the discovery/binding step from Phase 14B has already
found), the adapter should not mint a fresh, rights-less `source` object
directly from the extraction. It should first ensure the RAW file itself is
`op_link`ed as its own `source` object (a no-op if 14B's discovery-and-binding
already linked it), then call `journal.op_import(source_object_id=<raw
file's object_id>, ...)` for the DERIVED Markdown+sidecar. This is not new
machinery to build: `journal.py`'s existing `op_import` already refuses with
`journal.rights_unknown` unless the raw file's own recorded `transform` right
is exactly `"granted"` (verified, `journal.py:440-450`). Extraction is, in the
RIGHTS-01 vocabulary, a `transform` operation - gating it behind the raw
file's own rights record is exactly correct, and it is enforced automatically
the moment `source_object_id` is passed.

**When to use:** Every local-file adapter (PDF, DOCX, PPTX, EPUB, and
transcript files the learner already has).

**Example (design pattern; write this in `source_adapters.py`):**
```python
# Source: this session's synthesis over journal.py (read this session,
# see quoted excerpts in Open Questions section below)
import identity
import journal

def import_local_source(base, raw_file_object_id, adapter_name,
                         adapter_version, extract_fn, rel_path_md,
                         actor_kind, actor_name):
    """extract_fn(raw_bytes) -> (markdown_text, locator_records)"""
    registry = journal.read_registry(base)
    raw_row = registry.get(raw_file_object_id)
    raw_path = os.path.join(base, raw_row["path"])
    with open(raw_path, "rb") as fh:
        raw_bytes = fh.read()

    markdown_text, locator_records = extract_fn(raw_bytes)
    md_bytes = markdown_text.encode("utf-8")

    sidecar = build_sidecar(  # see Code Examples
        adapter=adapter_name, adapter_version=adapter_version,
        fingerprint=identity.object_fingerprint(md_bytes, "source"),
        captured_at=identity.utc_now(),
        origin={"kind": "local_file", "value": raw_row["path"]},
        rights=raw_row.get("rights"), confidence=None,
        locators=locator_records)
    sidecar_path = os.path.join(base, rel_path_md[:-3] + ".locator.json")
    _write_atomic(sidecar_path, json.dumps(sidecar, ensure_ascii=False,
                                           indent=2).encode("utf-8"))
    try:
        return journal.op_import(
            base, raw_file_object_id, "source", rel_path_md, md_bytes,
            actor_kind, actor_name)
    except journal.JournalError:
        try:
            os.remove(sidecar_path)   # best-effort cleanup; harmless orphan
        except OSError:
            pass
        raise
```

### Pattern 2: Direct mint for a remote capture with no pre-existing local object

**What:** A remote capture (web page, video, audio) has no linked local file
to gate a transform right against - `source_object_id` should be `None` and
`journal.commit_operation` will default `rights` to
`identity.rights_default()` (all `"unknown"`) for a fresh `kind="source"`
object when none is supplied (verified, `journal.py:419-421`). This
automatically satisfies "unknown rights stay restrictive" for a capture with
no prior rights record; an explicit rights grant is set separately at bind
time (Phase 14B's concern, not this phase's).

**When to use:** Web capture, video/audio ASR, when the origin is a URL not
a file already on disk.

### Anti-Patterns to Avoid

- **Writing the Markdown through `journal.commit_operation` before the
  sidecar exists on disk.** If the process crashes between the two writes,
  a `source` object could be journaled as `applied` with no locator sidecar
  next to it, and a later citation resolution would silently have no
  locators to point at. Write the sidecar first (see Pattern 1's ordering);
  its absence after a crash is a cheap, detectable, self-evidently-repairable
  condition (an orphan `.locator.json` with no matching journal entry, or a
  journaled source with a missing sidecar file - the second case should be
  a typed read-time error, not a crash, when a citation tries to resolve it).
- **Inventing a seventh `identity.OBJECT_KINDS` member** (`"artifact"`,
  `"snapshot"`, etc.) for the captured file. `14A-FREEZE.md` names this
  explicitly as a change that "forces a review of every kind-conditional
  rule that already exists"; there is no product need for it since `source`
  already fits.
- **Reimplementing OCR bounding-box extraction.** The existing `ocr` skill
  (`scripts/ocr_lib.py`'s `TRANSCRIBE_PROMPT`) asks the vision model to
  transcribe text only, in reading order - it returns no coordinates and no
  confidence score. Do not add a second vision-model call or a second OCR
  path to manufacture a bbox/confidence the skill was never built to produce;
  degrade the OCR locator body honestly (see Common Pitfalls).
- **Fetching a remote URL from inside `discovery.py`.** That module's own
  docstring states it "deliberately does not import `journal`, `subprocess`,
  or `urllib`" so its read-only property is structural. Remote fetch belongs
  in the new `source_adapters.py` module, never folded into discovery.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Compare-and-swap file writes, conflict detection, revision lineage | A second atomic-write helper in `source_adapters.py` | `journal.commit_operation` / `op_import` / `op_link` | This is precisely what 14A froze; a second CAS implementation would be a second source of truth for object state, which `journal.py`'s own docstring calls out as the one thing it exists to prevent |
| Object id/fingerprint minting | A locally-rolled UUID or hash scheme for `source_id` | `identity.new_object_id()` / `identity.object_fingerprint(raw, "source")` | Frozen 14A shape; any other id scheme breaks `journal.py`'s registry, which expects exactly this shape |
| PDF word/table geometry | A hand-rolled PDF content-stream tokenizer | `pdfplumber` (built on `pdfminer.six`'s layout tree) | Re-deriving word bboxes from raw content-stream operators is re-implementing pdfminer; already surveyed and rejected as a build path in `research/2026-08-17-pdf-docx-intake.md` |
| DOCX footnote/comment/tracked-change parsing | A second OOXML relationship resolver | Direct `zipfile`+`xml.etree` reads of `word/footnotes.xml`, `word/comments.xml`, etc. (python-docx does not itself surface these) | `fixtures/audit/locator_fidelity_cases.py`'s own DOCX builders already demonstrate the exact XML shape to read; the gold cases ARE the spec for this |
| EPUB spine/TOC parsing | A hand-rolled OPF/NCX walker from scratch, or the AGPL `ebooklib` | `zipfile` (EPUB is a zip) + `xml.etree` over `META-INF/container.xml` -> the OPF package document's `<spine>`/`<manifest>`, then `toc.ncx` (EPUB2) or the nav document (EPUB3) | Same reasoning as DOCX: the format is an open, small, well-documented XML container; a stdlib read avoids both a new dependency and ebooklib's AGPL license |
| SRT/VTT timestamp parsing | Nothing to avoid building here - this one genuinely is cheap to hand-roll | A ~30-line regex-based parser (`HH:MM:SS,mmm` for SRT, `HH:MM:SS.mmm` for VTT) | Explicitly flagged in Standard Stack: the dependency (`webvtt-py`) exists but the grammar is simple enough that it does not clear the adoption-gate "does not earn its cost" bar |
| Web readable-text extraction | A hand-rolled DOM-density heuristic | `readability-lxml` | Recreating Mozilla's Reader View heuristics badly is a known trap; a maintained Apache-2.0 library exists at acceptable dependency weight |

**Key insight:** every "don't hand-roll" row above except the SRT/VTT parser
maps onto an existing 14A primitive or an existing project precedent
(`fixtures/audit/locator_fidelity_cases.py`'s own DOCX-extra-parts builders,
`surfaces/update.py`'s hardened `urllib.request` usage). This phase's actual
new code surface is small: one dispatch module, five to seven extraction
functions, and one sidecar writer - not a new persistence or identity layer.

## Runtime State Inventory

Not applicable. This is a greenfield capability (a new adapter registry and a
new daemon route); it renames nothing and migrates no existing stored state.
Skipped per the instructions for non-rename/refactor phases.

## Common Pitfalls

### Pitfall 1: python-docx does not read footnotes, headers, footers, comments, or tracked changes

**What goes wrong:** A DOCX adapter built only on `python.docx.Document(...)`
walks `document.paragraphs`/`document.tables` and silently produces zero
locators for footnotes, headers, footers, comments, or tracked-change ranges
- exactly four of the twelve DOCX gold cases in
`fixtures/audit/locator_fidelity_cases.py` (`docx-footnote-endnote`,
`docx-header-footer`, `docx-tracked-changes`, `docx-comments`).

**Why it happens:** those four structures live in separate package parts
(`word/footnotes.xml`, `word/header1.xml`, `word/footer1.xml`,
`word/comments.xml`) that python-docx's high-level object model does not
expose.

**How to avoid:** read those parts directly via `zipfile.ZipFile(path).read(
"word/footnotes.xml")` + `xml.etree.ElementTree.fromstring(...)`, exactly the
shape the fixture builders themselves assemble (see
`locator_fidelity_cases.py:452-465` for the footnote/endnote XML the adapter
must be able to parse back out).

**Warning signs:** the DOCX adapter's own test suite passes on
`docx-headings-lists` and `docx-nested-table` but silently produces an empty
`unsupported` list (rather than a refusal or an actual footnote/comment
locator) on the other four cases.

### Pitfall 2: the OCR skill returns flat text, not bbox+confidence

**What goes wrong:** the locator table in CONTEXT.md asks for "source page
plus bounding box, plus a confidence score" for OCR, but the existing `ocr`
skill this phase must wrap (`scripts/ocr.py` / `scripts/ocr_lib.py`, read
this session) sends a single fixed prompt
(`TRANSCRIBE_PROMPT = "You are an OCR engine. Transcribe ALL visible text
... output only the transcribed text"`) to a local Ollama vision model and
returns `{path: text}` - no coordinates, no confidence field, in either the
plain or `--json` output mode.

**Why it happens:** the skill was built as a vision bridge for a text-only
authoring model (DeepSeek reading a screenshot), not as a structured-OCR
citation source; it was never asked to emit geometry.

**How to avoid:** do not fabricate a bounding box or confidence score. The
OCR adapter's locator body should honestly report `bbox: null` (whole-page
granularity is the accurate claim: "this text came from this page image")
and `confidence: null` unless a future change to the `ocr` skill itself adds
a structured-output mode. Document this as a known limitation in the sidecar
schema's field description, not silently omit the fields (the envelope
contract still names `confidence` as a common field, so it must be present
and explicitly `null`, distinguishable from "not attempted").

**Warning signs:** a sidecar with fabricated bbox coordinates that were never
actually measured, which would be silently wrong data reaching a citation.

### Pitfall 3: `xml.etree.ElementTree` and zip-based formats need defense against maliciously crafted files

**What goes wrong:** DOCX, PPTX, and EPUB are all zip archives containing
XML; `xml.etree.ElementTree.fromstring()` on a crafted "billion laughs"
payload can cause excessive memory/CPU use, and an unbounded
`zipfile.ZipFile.extractall()`/`.read()` on a crafted archive with a huge
compression ratio ("zip bomb") can exhaust disk or memory before the adapter
ever reports `unsupported`.

**Why it happens:** these are exactly the formats a course PDF/DOCX/PPTX
adapter must accept from arbitrary learner-supplied (or, per D-03, remotely
fetched) files; CPython's stdlib XML parsers have partial but not complete
built-in protection against entity-expansion attacks.

**How to avoid:** cap the per-entry uncompressed size read from any
`ZipInfo` (`zi.file_size`) before reading a part, refuse (typed
`unsupported`, reason `source.oversized`) above a fixed threshold (e.g. 200MB
uncompressed for a single document part is already generous for course
material); this is a cheap guard to add once in the shared zip-reading
helper every DOCX/PPTX/EPUB adapter calls through.

**Warning signs:** an adapter hanging or the process's memory climbing
sharply on one malformed input file during the fixture-corpus test run.

### Pitfall 4: a remote fetch redirect can leak the loopback API's own headers or land on an unintended scheme

**What goes wrong:** a naive `urllib.request.urlopen(url)` follows redirects
transparently, including a redirect that changes host or scheme (`file://`,
`ftp://`), which for a web-capture adapter fetching a learner-supplied URL is
a real (if low-severity, single-user) trust-boundary crossing.

**Why it happens:** stdlib `urllib.request`'s default redirect handler does
not restrict scheme or strip sensitive headers on a cross-host hop.

**How to avoid:** this project already has a hardened precedent -
`surfaces/update.py`'s `AuthStrippingRedirectHandler(urllib.request.
HTTPRedirectHandler)`, which strips auth-bearing headers on a cross-host
redirect during the GitHub-release update check (verified, `surfaces/
update.py:458`). Reuse the same pattern (or the same class) for the
web-capture fetch, and additionally refuse any redirect target whose scheme
is not `http`/`https`.

**Warning signs:** none observable without a deliberately crafted test
fixture (a local HTTP server issuing a `file://` or cross-scheme redirect);
recommend such a fixture in the Validation Architecture section below.

### Pitfall 5: pdfplumber's word/table geometry is expensive on large, image-heavy PDFs

**What goes wrong:** pdfplumber lazily parses each page but table-extraction
(`extract_tables()`) and per-word bbox extraction (`extract_words()`) walk
the full layout tree per page; on a 300-page scanned-cover PDF with only a
handful of true text pages, naive per-page full extraction can be slow.

**Why it happens:** pdfplumber optimizes for correctness/fidelity, not for
skipping non-text pages early.

**How to avoid:** check `page.extract_text()` (or `len(page.chars)`) cheaply
first; a page with no extractable characters is the `pdf-scanned-image-only`
gold case and should short-circuit to the page-level `unsupported` result
before ever calling the heavier `extract_words()`/`extract_tables()` calls.

**Warning signs:** an adapter timing out or taking multiple seconds per page
on the encrypted/scanned/malformed gold fixtures, which are specifically
designed to have nothing extractable.

## Code Examples

### Sidecar envelope shape (design recommendation - the planner must lock this as the frozen schema)

```json
{
  "schema_version": 1,
  "source_id": "3f9a1c2b4d5e6f70",
  "adapter": "pdf",
  "adapter_version": "1.0.0",
  "fingerprint": "sha256:...",
  "captured_at": "2026-08-21T00:00:00.000Z",
  "origin": {"kind": "local_file", "value": "sources/emt-workbook.pdf"},
  "rights": {"read": "granted", "quote": "granted", "transform": "granted",
             "remote_process": "unknown", "package": "unknown",
             "export": "unknown", "share": "unknown"},
  "confidence": "high",
  "reading_order": ["p1.0", "p1.1", "p2.0"],
  "locators": [
    {"id": "p1.0", "kind": "paragraph", "page": 1, "index": 0,
     "bbox": [72.0, 700.0, 400.0, 712.0]},
    {"id": "p1.1", "kind": "paragraph", "page": 1, "index": 1,
     "bbox": [72.0, 676.0, 380.0, 688.0]},
    {"id": "t.r0c0", "kind": "table_cell", "page": 2, "row": 0, "col": 0}
  ]
}
```

`locators[].id` matches an entry in `reading_order`, which is directly
modeled on the `reading_order` list every case in `fixtures/audit/
locator_fidelity_cases.py`'s `gold` dict already carries (e.g. `["p1.0",
"p1.1"]`, `["hdr1", "p1.0", "p1.1", "ftr1", ...]`) - this phase's schema
should be judged against those exact strings, not a redesign of them.
`[ASSUMED]`: the exact JSON field names (`locators`, `bbox` as a
four-element array, `origin.kind`) are this session's synthesis, not
independently verified against an existing schema elsewhere in the repo -
flag for planner/user confirmation before treating as frozen. `[VERIFIED:
fixtures/audit/locator_fidelity_cases.py:196-205,227,257]`: the
`reading_order` field name and its string-id shapes (`"p1.0"`, `"p1.c1.0"`,
`"t.r0c0"`, `"hdr1"`, `"fn1.0"`) are read directly from the existing gold
manifest and quoted here verbatim.

### PDF page-level short-circuit before geometry extraction

```python
# Source: this session's synthesis over pdfplumber's documented API
# (pdfplumber.readthedocs.io, Page.chars / Page.extract_text / Page.extract_words / Page.find_tables)
import pdfplumber

def extract_pdf(raw_bytes):
    import io
    locators = []
    reading_order = []
    md_lines = []
    with pdfplumber.open(io.BytesIO(raw_bytes)) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            if not page.chars:            # no extractable text at all
                continue                  # scanned/image-only: skip, not crash
            for idx, word_group in enumerate(page.extract_words()):
                loc_id = "p%d.%d" % (page_num, idx)
                locators.append({"id": loc_id, "kind": "paragraph",
                                  "page": page_num, "index": idx,
                                  "bbox": [word_group["x0"], word_group["top"],
                                           word_group["x1"], word_group["bottom"]]})
                reading_order.append(loc_id)
                md_lines.append(word_group["text"])
    if not locators:
        return None, [], "unsupported", "image-only page: no text-bearing structure"
    return "\n\n".join(md_lines), locators, reading_order, None
```

`[ASSUMED]`: this is illustrative shape (`page.extract_words()` returning
per-word dicts with `x0`/`top`/`x1`/`bottom`/`text` keys is pdfplumber's
documented API per training knowledge and `research/2026-08-17-pdf-docx-
intake.md`'s findings, not re-verified by running pdfplumber in this
session). The planner/executor should confirm the exact return shape against
the installed pdfplumber version's own docs before finalizing the extraction
function.

### DOCX footnote read (direct XML, the part python-docx does not expose)

```python
# Source: this session's synthesis, matching the XML shape
# fixtures/audit/locator_fidelity_cases.py's docx-footnote-endnote case
# assembles (locator_fidelity_cases.py:452-465, quoted there verbatim)
import zipfile
import xml.etree.ElementTree as ET

W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

def extract_docx_footnotes(raw_bytes):
    import io
    locators = []
    with zipfile.ZipFile(io.BytesIO(raw_bytes)) as zf:
        if "word/footnotes.xml" not in zf.namelist():
            return locators
        root = ET.fromstring(zf.read("word/footnotes.xml"))
        for footnote in root.findall(W_NS + "footnote"):
            fn_id = footnote.get(W_NS + "id")
            text = "".join(t.text or "" for t in footnote.iter(W_NS + "t"))
            locators.append({"id": "fn.%s" % fn_id, "kind": "footnote",
                              "footnote_id": int(fn_id), "text": text})
    return locators
```

### Web capture fetch with redirect hardening (following `surfaces/update.py`'s precedent)

```python
# Source: this session's synthesis, reusing the pattern read from
# surfaces/update.py:458 (AuthStrippingRedirectHandler)
import urllib.request

class SchemeLockedRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Refuses a redirect whose target scheme is not http/https - the
    web-capture adapter's equivalent of surfaces/update.py's auth-stripping
    handler, applied to scheme instead of headers."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not newurl.lower().startswith(("http://", "https://")):
            raise urllib.error.URLError(
                "redirect to non-http(s) scheme refused: %s" % newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)

def fetch_web_capture(url, timeout=15):
    opener = urllib.request.build_opener(SchemeLockedRedirectHandler())
    req = urllib.request.Request(url, headers={"User-Agent": "itembank/1.0"})
    with opener.open(req, timeout=timeout) as resp:
        return resp.read(), resp.headers.get("Content-Type", ""), \
               resp.headers.get("ETag"), resp.headers.get("Last-Modified")
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| No PDF/DOCX intake at all (rejected under stdlib-only) | pdfplumber+pdfminer.six / python-docx, adopted on merit | 2026-08-09 constraint relaxation, 2026-08-17 research pass | This phase turns the recommendation into a shipped adapter registry |
| EPUB export-only | EPUB import (this phase's roster item 7), stdlib zipfile+xml.etree, not `ebooklib` (AGPL) | This session (2026-08-21) - the AGPL finding is new | Avoids a second parked-license dependency alongside PyMuPDF |
| ASR landscape (2026) | `faster-whisper` (CTranslate2, best on NVIDIA) vs `whisper.cpp` bindings (smaller, CPU/portable-friendly) - neither picked here | Registered, not decided, per CONTEXT.md roster item 5 | This phase's PDF/DOCX/PPTX/EPUB/web/transcript adapters can all ship before the ASR question is resolved |

**Deprecated/outdated:** none directly relevant; every library recommended
above is its current stable release as of this session.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Exact sidecar JSON field names (`locators`, `origin.kind`, `bbox` as a 4-element array, `reading_order` reused verbatim from the gold fixture) | Code Examples, Open Question 1 | If the planner/executor picks different field names, the fixture extension in `fixtures/audit/locator_fidelity_cases.py` and any Phase 14B binding code written against this schema would need a migration; low risk since nothing consumes the schema yet |
| A2 | `pdfplumber.Page.extract_words()` returns dicts with exactly `x0`/`top`/`x1`/`bottom`/`text` keys | Code Examples | If the installed pdfplumber version's dict shape differs, the extraction function needs a one-line key-name fix; does not affect the architectural decisions |
| A3 | Remote-staleness signal design (advisory `origin_reachable`/`origin_changed` flags, HTTP ETag/Last-Modified as a cheap recheck) | Open Question 4 | If the planner picks a different mechanism, no existing code depends on this recommendation; it is new design surface, not a correction to something already built |
| A4 | Dependencies are pip-installed at setup/checkout time, lazily imported per-call, later bundled by Phase 18's PyInstaller build | Open Question 5, Summary point 5 | If eager module-load-time imports are chosen instead, one missing dependency (e.g. no `python-pptx` installed) would crash daemon startup entirely rather than degrading just the PPTX adapter - a real regression against "degrade never block" if not caught in review |
| A5 | The exact `/api/source/import` route name and body shape (`{"adapter": "pdf", ...}`) | Open Question 3, Summary point 3 | Low risk: any literal route name works as long as it follows the fixed-literal-path, opaque-body-identifier pattern; the name itself is not load-bearing on any existing test |
| A6 | `postinstall`/build-script safety of the eight audited packages was not independently re-verified by downloading and inspecting each sdist | Package Legitimacy Audit | Low risk given all eight are long-established, widely-used, canonical-repo-matched libraries; flagged for completeness per the audit protocol |

## Open Questions

### 1. The frozen sidecar schema and its version field

**What we know:** the envelope fields are named in CONTEXT.md
(`source_id`, `adapter`, `adapter_version`, `fingerprint`, `captured_at`,
`origin`, `rights`, `confidence`). The per-medium locator body vocabulary for
PDF and DOCX is already gold-tested in `fixtures/audit/
locator_fidelity_cases.py` (`page`, `paragraph`, `column`, `table`/`table_cell`,
`header`, `footer`, `footnote`, `endnote`, `heading`, `list_item`,
`tracked_insert`, `tracked_delete`, `comment`) with a `reading_order` array
of short string ids (`p1.0`, `t.r0c0`, `hdr1`, `fn1.0`) already established
as the citation-position linkage.

**What's unclear:** the exact field name and array-vs-object shape for
`locators`, and the locator-body vocabulary for the five media the gold
fixture does not yet cover (PPTX, EPUB, web, video/audio, OCR).

**Recommendation:** adopt the Code Examples section's envelope shape as a
starting draft; extend `locator_fidelity_cases.py` in the same session that
locks the schema, with one new gold-case file per new medium
(`pptx_fidelity_cases.py`, `epub_fidelity_cases.py`, etc.) following the
exact same deterministic-byte-fixture pattern the existing file uses
(`CASE_TABLE` of `{id, kind, filename, build, gold}` dicts with a SHA-256 of
the constructed bytes). For EPUB, model the fragment anchor loosely on EPUB
CFI's step-path idea (`/6/4[chap01]!/4/10[para05]`) but do not require full
CFI compliance - a simpler `{"spine_idref": "chap01", "element_index": 5}`
locator is sufficient since itembank's own reader, not a third-party EPUB
reading system, is the only consumer. For web capture, model the anchor on
the W3C Web Annotation Data Model's `CssSelector`+`TextQuoteSelector`
combination (a CSS selector to the containing block plus a text quote with
prefix/suffix, so a citation survives minor DOM changes) rather than a raw
DOM XPath. For video/audio, use plain integer millisecond `start_ms`/`end_ms`
fields (CONTEXT.md's own wording), not a Media Fragments URI string - the
URI syntax's value is browser interoperability, which does not apply to an
internal JSON sidecar.

### 2. Whether a captured snapshot is a source, an artifact, or both in the 14B object graph

**Resolved, HIGH confidence.** `identity.py`'s `OBJECT_KINDS = ("course",
"objective", "source", "lesson", "bank", "component")` (verified,
`identity.py:32`, quoted exactly) is a closed, frozen vocabulary:
`14A-FREEZE.md`'s "What breaks if this is changed later" section states
plainly that "Adding or removing an object kind forces a review of every
kind-conditional rule that already exists (the `bank`/`lesson`
trailing-whitespace carve-out, the `source`-only default rights record) for
whether the new or removed kind needs the same treatment" (verified,
`14A-FREEZE.md:178-181`, quoted exactly). A captured snapshot's Markdown is a
`source` object; there is no "artifact" kind in the frozen vocabulary and
inventing one is a one-way-door change this phase has no product reason to
take. The JSON locator sidecar is not itself a separately identified 14A
object - it is a companion file addressed by a deterministic path derived
from the source's own `rel_path` (e.g. `foo.md` -> `foo.locator.json`),
never minted its own `object_id` or `fingerprint`.

### 3. The daemon route shape: one `/api/source/import` versus one route per adapter

**Resolved, HIGH confidence, grounded in `surfaces/daemon.py` read this
session.** One route. Evidence:

- `API_ROUTES`'s own comment states the existing twelve routes are "Fixed
  literals, not stem-parameterised: a session or a bank is addressed by an
  opaque identifier in the JSON body (T-2-01), never by a path segment"
  (verified, `daemon.py:216-219`, quoted). An `adapter` field in the POST
  body follows this exactly, the same way `/api/start`'s body already
  carries a `mode`/`selection_mode` field selecting behavior.
- `daemon.py`'s own comment states "The twelve-entry length is asserted by
  `check_api_route_scope` in `tests/daemon_roundtrip.py`, and every entry is
  mirrored in ROUTE_CLI and SURFACE_PARITY" (verified, `daemon.py:220-222`,
  quoted). Adding seven routes (one per adapter) would require seven new
  entries in three separate tables plus updating that length assertion;
  adding one route requires one entry in each.
- The route must be a mutating write (it appends a journal entry and writes
  two files), so it should use the same authority gate `handle_seed_accept`
  already uses: `_same_origin` for the read half, `_client_is_loopback` for
  the actual write (verified, `daemon.py:417,438`, the same pattern
  documented generally by `_reject_cross_origin_write`,
  `daemon.py:1047-1060`). This means D-02's "external harness is an HTTP
  client of that route" is only true for a harness running on the same
  machine (loopback) - a `--lan`-bound daemon does not expose source import
  to other devices on the network, matching every other mutating route's
  existing authority model. If a Cordis-based harness needs to run
  cross-machine, that is a new authority question outside this phase's scope
  and should be flagged to the planner rather than silently assumed away.
- Whichever literal path is chosen, it must also gain an entry in
  `ROUTE_CLI` (a CLI command, e.g. `itembank source import`, per SURF-04's
  "every capability has both a route and a CLI command") and in
  `SURFACE_PARITY` (reserving a future MCP tool name, e.g. `source_import`,
  per Extensibility Rule 9(a), verified `daemon.py:315-321`).

### 4. How a changed or vanished remote origin surfaces as stale without breaking an already-issued citation

**Resolved at the design level, MEDIUM confidence (mechanism recommended,
not independently verified against a prior identical pattern elsewhere in
the repo - tagged `[ASSUMED]`).**

`journal.py`'s existing drift-detection machinery
(`detect_external_edits`/`object_state`/`reconcile`) exists specifically for
a *local file whose bytes changed on disk outside the journal* (verified,
`journal.py:1150-1207`, `detect_external_edits`'s docstring: "Append one
`external_edit` record for every registry row whose on-disk fingerprint
differs from its accepted fingerprint"). None of this can fire for a remote
URL, because there is no local file to re-hash against the recorded
fingerprint - the recorded fingerprint is of the *captured snapshot*, which
by D-04's own design never changes once accepted.

Recommendation: treat "the remote origin changed or vanished" as an entirely
separate, read-time-computed, advisory signal, never a mutation of the
already-accepted `source` object's revision:

1. Store `origin.value` (the URL), `origin.fetched_at`, and optionally
   `origin.http_etag`/`origin.http_last_modified` (from the capture-time
   response headers) in the sidecar.
2. On demand (not automatically - this must not make citation resolution
   depend on network reachability, per the degrade-never-block rule), an
   explicit `itembank source recheck <id>` command / route issues a cheap
   `HEAD` request (or a conditional `GET` with `If-None-Match`/
   `If-Modified-Since` when the validators were captured) and reports one of:
   `origin_reachable: false` (network/DNS/HTTP error), `origin_unchanged`
   (validators match or a fresh hash matches the recorded fingerprint),
   `origin_changed` (validators or hash differ). None of these three
   outcomes touches `journal.jsonl` or the object's `fingerprint`.
3. Only if the learner explicitly chooses to re-capture does a NEW revision
   get committed, via `op_edit_in_place` (same `object_id`, `revision`
   advances, the previous bytes remain recoverable as a `before_image` per
   `journal.py`'s existing undo machinery). Any citation that recorded the
   OLD `fingerprint` at the OLD `revision` stays exactly as valid as it was
   the moment it was made; nothing about the revision chain retroactively
   invalidates it. This is precisely the "changed remote source is a
   detectable stale state rather than a silently broken citation" property
   D-04 asks for.

### 5. Whether adapter dependencies install eagerly or on first use, given the packaged-app end goal

**Resolved at the design level, MEDIUM confidence.**
`SUPPLY-CHAIN-POLICY.md` section 2.1 states "No CDN loads, no install-time
network fetch on the learner's machine. This keeps the shipped product's
'degrade, never block' promise independent of any registry being reachable"
(verified, `SUPPLY-CHAIN-POLICY.md:29-33`, quoted). This rules out a design
where the running app silently `pip install`s a missing adapter dependency
the first time it is used - that is exactly an "install-time network fetch
on the learner's machine" the moment the app is packaged (Phase 18,
PyInstaller onedir per `CLAUDE.md`'s DEL-11 constraint).

The recommended reading, reconciling both this policy and "first use" as a
sensible-sounding phrase in the open question: "first use" should mean
Python-level lazy `import` (deferred to inside each adapter's dispatch
function, not at `source_adapters.py` module top), not network-level lazy
fetch. Concretely:

```python
def extract_pdf(raw_bytes):
    try:
        import pdfplumber
    except ImportError:
        return None, [], "unsupported", (
            "adapter.dependency_missing: pdfplumber is not installed; "
            "run `pip install pdfplumber==0.11.10 pdfminer.six==20260107`")
    ...
```

This means: (a) one missing dependency degrades only that one adapter, never
crashes the daemon or blocks the other six adapters (a real "degrade never
block" requirement this phase must satisfy on its own, independent of the
Phase 18 packaging question); (b) at development/checkout time, all
dependencies are pinned in `VENDORED.md` per `SUPPLY-CHAIN-POLICY.md`
section 3 and installed once via `pip install` (documented in a setup step,
since the project currently has no `requirements.txt`/lockfile at all per
`CLAUDE.md`'s Configuration section - this phase may be the first to need
one, or the pins may live in `VENDORED.md` alone; the planner should decide
which given no prior precedent exists); (c) Phase 18's PyInstaller build
later bundles the pinned wheels into the shipped artifact so the packaged
app needs zero post-install network access for any adapter, closing the
loop the policy's "degrade, never block... independent of any registry
being reachable" language asks for.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| pip / PyPI registry reachability | Installing adapter dependencies at dev/checkout time | Yes, confirmed reachable this session (`pip index versions` succeeded for all 8 packages) | pip 25.0.1 (25.0.1 -> 26.2.1 upgrade available, not required) | None needed; this is a one-time setup step, not a runtime dependency |
| Local Ollama server + `qwen2.5vl:7b` vision model | OCR adapter (roster item 6, wraps existing `ocr` skill) | Not probed this session (no Ollama endpoint check run); `scripts/ocr_lib.py` already auto-probes `localhost:11434` then a WSL2 gateway and raises a clear error if unreachable | n/a | The OCR adapter should surface the skill's own existing "no Ollama server reachable" error as a typed `unsupported` result, not a crash - this is already the skill's documented behavior, just needs threading through the adapter's return shape |
| whisper.cpp or a hosted ASR endpoint | Video/audio adapter (roster item 5) | Not available - explicitly registered, not built in this phase, per CONTEXT.md roster ordering | n/a | None needed this phase; roster item 5 is deliberately last and out of this phase's required build scope |
| Network access for web-capture fetch | Web capture adapter (roster item 3) | Assumed available on a typical dev machine but must degrade cleanly when absent | n/a | A `urllib.error.URLError`/timeout should surface as a typed `unsupported` result (`source.fetch_failed`), never a crash, consistent with the model-layer's existing "goes quiet when unreachable" precedent |

**Missing dependencies with no fallback:** none block this phase's minimum
viable build (PDF/DOCX/PPTX per roster items 1-2 need only pip-installable,
verified-available packages).

**Missing dependencies with fallback:** OCR (Ollama reachability) and web
capture (network reachability) both have documented, typed degraded paths
rather than blocking the whole registry.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Bespoke `tests/*_roundtrip.py` scripts, direct `python3` execution (no pytest/unittest runner) - this is the project's own established convention, confirmed by `tests/identity_roundtrip.py`, `tests/journal_roundtrip.py`, `tests/operations_roundtrip.py`, `tests/file_fault_tracer.py` already existing in this shape |
| Config file | none - see Wave 0 |
| Quick run command | `python3 tests/source_adapters_roundtrip.py` |
| Full suite command | `for t in tests/*.py; do python3 "$t" \|\| exit 1; done` (the exact command `14A-FREEZE.md` records as the project's full-suite gate) |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| Roster 1 (PDF) | Every `fixtures/audit/locator_fidelity_cases.py` PDF case produces the gold `structures`/`reading_order`/`unsupported` result | unit/fixture | `python3 tests/source_adapters_roundtrip.py -k pdf` (or equivalent internal filter, following the existing `_roundtrip.py` style of one `check_*` function per case group) | ❌ Wave 0 |
| Roster 1 (DOCX) | Every DOCX gold case, including the four extra-parts cases (footnote/endnote, header/footer, tracked-changes, comments) | unit/fixture | same file, DOCX case group | ❌ Wave 0 |
| Roster 2 (PPTX) | New gold cases (slide text, notes-field flag, at least one unsupported case e.g. an embedded video) | unit/fixture | `python3 tests/source_adapters_roundtrip.py` against a new `fixtures/audit/pptx_fidelity_cases.py` | ❌ Wave 0 (fixture file does not exist yet) |
| Roster 7 (EPUB) | New gold cases (spine order, one fragment-anchored citation, one unsupported case e.g. DRM-locked EPUB) | unit/fixture | same pattern, `fixtures/audit/epub_fidelity_cases.py` | ❌ Wave 0 |
| Roster 3 (Web capture) | Static HTML fixture (no live network in the test) produces a stable CSS/text-quote locator; a redirect-to-non-http-scheme fixture is refused | unit/fixture, one local-loopback integration test for the redirect case | `fixtures/audit/web_capture_fidelity_cases.py` plus a `tests/`-level loopback `http.server` fixture for the redirect-hardening case | ❌ Wave 0 |
| Roster 4 (Transcript) | `.srt` and `.vtt` byte fixtures produce `start_ms`/`end_ms` locators | unit/fixture | `fixtures/audit/transcript_fidelity_cases.py` | ❌ Wave 0 |
| D-02 (route shape) | `POST /api/source/import` exists in `API_ROUTES`/`ROUTE_CLI`/`SURFACE_PARITY`, rejects cross-origin, rejects non-loopback writes | integration | Extend `tests/daemon_roundtrip.py`'s existing `check_api_route_scope`-style assertions | ❌ Wave 0 (new assertions in an existing file) |
| Pattern 1/2 (journal integration) | A PDF import commits exactly one `applied` `source`-kind journal entry with `source_object_id` set when a raw file was linked; a rights-refused import raises `journal.rights_unknown` and leaves no orphan `applied` entry | integration | Extend `tests/operations_roundtrip.py` or add a new `tests/source_adapters_roundtrip.py` case exercising the full link-then-import sequence | ❌ Wave 0 |
| Pitfall 3 (zip bomb / XML entity guard) | An oversized-part fixture is refused with `source.oversized`, not a hang | unit/fixture | one adversarial case in `fixtures/audit/pptx_fidelity_cases.py` (or a shared zip-format fixture module) | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `python3 tests/source_adapters_roundtrip.py`
- **Per wave merge:** `for t in tests/*.py; do python3 "$t" || exit 1; done`
- **Phase gate:** full suite green, plus `python3 itembank.py guard .` clean (the existing convention every prior phase's freeze record - e.g. `14A-FREEZE.md` - reports)

### Wave 0 Gaps

- [ ] `tests/source_adapters_roundtrip.py` - new file, covers roster items 1-4 (PDF/DOCX/PPTX/EPUB extraction fidelity against gold fixtures) plus the journal-integration cases (Pattern 1/2)
- [ ] `fixtures/audit/pptx_fidelity_cases.py` - new gold-case file, same `CASE_TABLE` builder pattern as the existing PDF/DOCX file
- [ ] `fixtures/audit/epub_fidelity_cases.py` - new gold-case file
- [ ] `fixtures/audit/web_capture_fidelity_cases.py` - new gold-case file (static HTML fixtures; a separate loopback-server test for the redirect-hardening case, not a fixture-file case)
- [ ] `fixtures/audit/transcript_fidelity_cases.py` - new gold-case file
- [ ] New assertions inside `tests/daemon_roundtrip.py` for the new route's presence in `API_ROUTES`/`ROUTE_CLI`/`SURFACE_PARITY` and its authority gate
- [ ] Framework install: no new test framework needed; the project's existing bespoke `*_roundtrip.py` convention covers this phase without new tooling

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V1 Architecture | yes | One new module (`source_adapters.py`) with a documented, narrow dependency surface (`identity`, `journal`, `discovery` for path containment only, plus the pinned extraction libraries); never imports `runtime.py` or `model.py`, keeping D-05 structurally true rather than merely stated |
| V5 Input Validation | yes | Magic-byte sniffing before dispatch (`%PDF` for PDF, `PK\x03\x04` zip signature for DOCX/PPTX/EPUB) rather than trusting a client-supplied `adapter` field or file extension alone; `journal.py`'s existing `discovery.inside_any_root` path-containment check (already enforced for every `rel_path` passed to `commit_operation`, verified `journal.py:383-387`) covers path-traversal for the derived Markdown/sidecar output paths for free |
| V12 File Handling | yes | Per-entry uncompressed-size cap on every zip-based format read (Pitfall 3); explicit XML entity-expansion awareness (CPython's stdlib `expat`-backed parser has partial built-in limits; a size cap on the raw input plus a documented review of whether `defusedxml` is worth the added dependency is the concrete deliverable, not a blanket claim of safety) |
| V13 API and Web Service | yes | The new `/api/source/import` route reuses the exact existing authority gate (`_reject_cross_origin_write`, i.e. same-origin-when-Origin-present plus loopback-only for the write) that `handle_seed_accept` already establishes; no new authority mechanism is introduced |
| V6 Cryptography | no | This phase mints no secrets and performs no cryptographic operation beyond the existing `hashlib.sha256` change-detection fingerprint, already covered by `identity.py`'s own documented "never a security boundary" note |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| SSRF-shaped risk: a learner (or an agent acting for one) supplies a URL that resolves to a loopback or private-network address, using the web-capture adapter to probe the local network from itembank's own process | Information Disclosure / Elevation of Privilege | Given `identity.py`'s own documented threat model ("this project has a single local user and no attacker in its threat model"), full SSRF hardening (DNS-rebinding-safe IP allowlisting) is likely disproportionate; the cheap, low-cost mitigation worth taking regardless is the scheme-lock in Code Examples (refuse non-http(s) redirect targets) and a documented note in the adapter's help text that it does not attempt to fetch loopback/private-range targets specially - flag this as a planner decision, not a hard requirement, given the stated single-user threat model |
| Zip bomb / XML entity expansion via a crafted DOCX/PPTX/EPUB | Denial of Service | Per-entry size cap before read (Pitfall 3), applied uniformly in one shared zip-reading helper all three zip-based adapters call through |
| Redirect-based credential/scheme confusion during web capture | Tampering / Information Disclosure | `SchemeLockedRedirectHandler` (Code Examples), directly modeled on the existing `AuthStrippingRedirectHandler` precedent in `surfaces/update.py` |
| Path traversal via a crafted `rel_path` for the derived Markdown/sidecar output | Tampering | Already closed structurally by `journal.commit_operation`'s existing `discovery.inside_any_root` check (verified, `journal.py:383-387`); the adapter module must not bypass `commit_operation` with a direct file write for the Markdown half of the pair |
| A conflicting/forged `source_object_id` claiming an existing raw file's rights without actually owning it | Spoofing | Already closed structurally by `journal.py`'s ID-02 conflict detection (`registry_fingerprint != compare_fingerprint` refusal, verified `journal.py:459-469`); no new code needed, but the adapter must resolve `source_object_id` server-side from the daemon's own registry, never accept a raw fingerprint/rights claim from the client body |

## Sources

### Primary (HIGH confidence)

- `identity.py` (read this session in full) - `OBJECT_KINDS`, `REVISION_KEYS`, `rights_default`, `mint_object`, `next_revision`
- `journal.py` (read this session in full) - `ENTRY_KEYS`, `OPERATION_TYPES`, `commit_operation`/`_commit_impl`, `op_link`/`op_import`/`op_copy`/`op_move`/`op_edit_in_place`/`op_supersede`, `detect_external_edits`, `reconcile`, `_write_bytes_atomic`
- `.planning/phases/14A-identity-lifecycle-operation/14A-FREEZE.md` (read this session in full) - the frozen-vocabulary "what breaks if changed" section
- `fixtures/audit/locator_fidelity_cases.py` (read this session in full) - the PDF/DOCX gold-case manifests, `reading_order` shape, `unsupported` result shape
- `surfaces/daemon.py` (read this session, targeted sections: lines 1-70, 200-520, 980-1080, 2249-2420, 2291-2410, 3285-3340) - `API_ROUTES`/`ROUTES`/`ROUTE_CLI`/`SURFACE_PARITY`, `_reject_cross_origin`/`_reject_cross_origin_write`/`_client_is_loopback`, `_sidecar_token_ok`/`_dispatch`, `handle_seed_accept`, `api_read_json`
- `.planning/SUPPLY-CHAIN-POLICY.md` (read this session in full)
- `.planning/phases/14C-source-adapter-registry/14C-CONTEXT.md` (read this session in full)
- `.planning/IDEA-LEDGER.md` IL-20260815-07 entry (read this session)
- `.planning/research/2026-08-17-pdf-docx-intake.md` (read this session in full)
- `.claude/skills/ocr/SKILL.md`, `scripts/ocr.py`, `scripts/ocr_lib.py` (read this session in full)
- `discovery.py` (read this session, header/docstring + `inside_any_root`)
- `surfaces/update.py` (grep-confirmed `AuthStrippingRedirectHandler` at line 458)
- PyPI registry, `pip index versions` and PyPI JSON API (`https://pypi.org/pypi/<pkg>/json`), run this session (2026-08-21) for pdfplumber, pdfminer.six, python-docx, pypdf, python-pptx, readability-lxml, trafilatura, ebooklib, webvtt-py

### Secondary (MEDIUM confidence)

- `research/2026-08-17-pdf-docx-intake.md`'s own WebSearch-sourced candidate table (dated 2026-08-17, re-verified rather than assumed stale by this session's independent `pip index versions` run)
- WebSearch results this session on EPUB CFI (idpf.org/w3c.github.io spec pages), W3C Media Fragments URI (w3.org/TR/media-frags), W3C Web Annotation Data Model (w3.org/TR/annotation-model) - used only to shape the locator-body design recommendation, not as a compliance requirement
- WebSearch results this session on python-pptx, trafilatura vs readability-lxml, webvtt-py, faster-whisper vs whisper.cpp licensing and dependency landscape

### Tertiary (LOW confidence)

- The package-legitimacy seam's automated verdicts (`SUS` for all eight audited packages) - judged in this document as a checker-side gap (`unknown-downloads`) rather than a genuine risk signal, but the planner should still honor the protocol's `checkpoint:human-verify` requirement for the batch

## Metadata

**Confidence breakdown:**
- Standard stack (PDF/DOCX/PPTX libraries, versions, licenses): HIGH - every claim independently re-verified against the live PyPI registry this session, not carried over from memory
- Identity/journal integration (Open Questions 2 and 3, Pattern 1/2): HIGH - every claim quotes a specific line range from a file read in full this session
- Sidecar schema exact field names (Open Question 1, Code Examples): MEDIUM - grounded in existing gold-fixture vocabulary but the exact envelope shape is this session's synthesis, explicitly flagged `[ASSUMED]` for planner lock
- Remote staleness mechanism (Open Question 4): MEDIUM - grounded in what `journal.py` demonstrably cannot do for a URL, but the proposed advisory-flag mechanism is new design, not a verified existing pattern
- Dependency install timing (Open Question 5): MEDIUM - grounded in `SUPPLY-CHAIN-POLICY.md`'s explicit language, but the project currently has no `requirements.txt`/lockfile precedent to model the "pip-install-at-setup-time" half against
- OCR/ASR/web-capture pitfalls: HIGH for OCR (the skill's actual code was read in full) and the web-capture redirect hardening (existing precedent read in full); MEDIUM for ASR (landscape research only, no library chosen, matching CONTEXT.md's "registered, planned last")

**Research date:** 2026-08-21
**Valid until:** 30 days for the architectural findings (identity/journal/daemon integration - these are frozen 14A/existing-daemon contracts, unlikely to move); 14 days for the exact library versions (PyPI releases move faster than the architecture)
