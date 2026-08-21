# Phase 14C context: source adapter registry and remote intake

**Status:** bounded context, written 2026-08-21. Deliberately short. Under the
lesser-model executor split, plans carry every decision and context carries
only what a planner needs to write them. Phase 14A ran 25,446 words of
scaffolding against 21,302 words of plan; this document does not repeat that.

**Phase:** 14C. **Depends on:** 14A (identity, fingerprint, revision, journal
primitives in `identity.py`). **Blocks:** the source-binding half of 14B, which
cannot bind a PDF today. **Executes:** DeepSeek V4, sequentially.

## Why this phase exists

`SOURCE-TO-COURSE.md` says a course may begin with a book, syllabus, or exam
blueprint. Those arrive as PDF, DOCX, PPTX, video, and web pages. itembank
accepts Markdown and plain UTF-8 only, so the binding milestone assumes an
intake path that does not exist. `IL-20260815-07` researched the PDF and DOCX
half on 2026-08-17 and left the schema open. This phase closes it once, for
every medium, rather than per format.

## Decisions already made, do not re-litigate

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

## The adapter contract

Every adapter is the same function, differing only in extraction:

    bytes or a fetch descriptor, plus a rights grant
      -> Markdown (plain UTF-8) + a JSON locator sidecar
      -> one fingerprint via identity.object_fingerprint(raw, "source")
      -> one operation journal entry

Failure is explicit and typed. A scanned PDF returns `unsupported` with a reason
code, never a silent empty extraction. Compare-and-swap rules apply: expected
base fingerprint, temp file, validate, atomic commit, journal append.

## The locator sidecar, the one open design

Every medium needs a page-number equivalent so a citation can point at a place.
The shape is one envelope with a per-medium locator body:

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

## Adapter roster and disposition

Build in this order. Each is one plan.

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
7. **EPUB.** Currently export-only (`REQUIREMENTS.md:763`). Import is additive.

## Where considerations conflict, build both

Per the standing directive: implement both and let the learner choose, rather
than deciding for them now.

- **Agent auto-fetch versus approve-before-bind.** Build both paths behind one
  setting. Search and read stay free in both. The bind step is the gated one,
  because an agent that binds unattended can quietly build a course from
  unvetted material. Default to approve-before-bind; the setting exists so the
  learner can lift it.
- **Snapshot storage: inline copy versus reference plus cache.** Both. Inline
  for anything small enough to live beside the course, cached-with-reference for
  large media. Same fingerprint either way, so the citation contract does not
  notice which was used.

## Out of scope, refuse these

- Any second parser, scorer, or evidence store.
- Rewriting itembank in TypeScript, or reimplementing a plugin kernel in Python.
- Hosted multi-tenant anything. Snapshots and evidence stay on disk.
- Adopting PyMuPDF. It is parked on an explicit Weibao AGPL decision.
- Treating an unresolved rights grant as permissive. Unknown rights stay
  restrictive.

## Open questions the planner must close

1. The frozen sidecar schema and its version field.
2. Whether a captured snapshot is a source, an artifact, or both in the 14B graph.
3. The daemon route shape: one `/api/source/import` taking an adapter name, or
   one route per adapter.
4. How a changed or vanished remote origin surfaces as stale without breaking a
   citation that already cites it.
5. Whether adapter dependencies install eagerly or on first use, given the
   packaged-app end goal.
