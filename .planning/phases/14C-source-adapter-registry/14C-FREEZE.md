---
phase: 14C
slug: source-adapter-registry
frozen: 2026-08-28
plans: 8
---

# Phase 14C freeze: the source adapter registry

Ten adapters, one locator sidecar contract, one import boundary, two routes,
two CLI commands. This file is what a later phase reads to know what it may
build against, what breaks if it moves, what every planning-source item
resolved to, and what conditions reopen a parked decision.

## Frozen at 14C

**The ten `ADAPTER_REGISTRY` keys.** `markdown`, `text`, `pdf`, `docx`,
`pptx`, `web`, `transcript`, `ocr`, `epub`, `asr`. `ADAPTER_VERSIONS` reads
`1.0.0` for nine and `0.0.0` for `asr`, which has no backend. Adding a medium
is a registration, never a caller change.

**The twelve `SOURCE_ADAPTER_CODES` members**, sorted by construction:
`source.adapter_unknown`, `source.approval_required`,
`source.backend_unconfigured`, `source.dependency_missing`,
`source.encrypted`, `source.fetch_failed`, `source.internal_error`,
`source.malformed_input`, `source.origin_refused`, `source.oversized`,
`source.redirect_refused`, `source.unsupported`. Later plans append; nothing
is renamed.

**`schemas/source_locator.schema.json` at `x-itembank-version` 1.** Twelve
envelope fields (`schema_version`, `source_id`, `adapter`, `adapter_version`,
`fingerprint`, `captured_at`, `origin`, `rights`, `confidence`,
`reading_order`, `locators`, `unsupported`); `$defs.origin` with six fields
and a `kind` enum of `local_file` and `remote_url`; `$defs.locator` with
`id`, `span_id`, `kind`, and `body`; the frozen `kind` vocabulary; and
**nine** per-medium bodies, `body_asr` having been added by plan `14C-08` as
an additive `oneOf` branch. `additionalProperties: false` at every object
level.

**The four public functions and their signatures.**
`import_source(base, adapter, raw_object_id, actor_kind, actor_name, rights_grant=None, options=None, confirm=False)`,
`preview_source(base, adapter, raw_object_id, options=None)`,
`capture_url(base, url, actor_kind, actor_name, options=None, confirm=False)`,
and `recheck_origin(base, source_object_id, options=None)`. Only
`journal.JournalError` escapes any of them.

**The two route literals** `POST /api/source/import` and
`POST /api/source/recheck`, both mapped to the one `source` CLI twin in
`ROUTE_CLI` and both carrying a reserved tool name in `SURFACE_PARITY`.
`API_ROUTES` is fifteen entries.

**The two CLI commands** `itembank source import` (with `--file` or `--url`,
`--adapter`, `--grant`, `--preview`, `--snapshot-storage`, `--confirm`,
`--json`) and `itembank source recheck` (with `--base`, a positional
`object_id`, `--json`), the second exiting 0 for all three reported states.

**The six `source` settings keys** and their restrictive defaults:
`bind_policy` `approve_before_bind`, `snapshot_storage` `auto`,
`snapshot_inline_max_bytes` 8388608, `allow_private_origins` false,
`fetch_timeout_seconds` 15, `max_input_bytes` 209715200. Mirrored in
`source_adapters.SOURCE_OPTION_DEFAULTS`, which
`check_option_defaults_match_schema` holds equal to the schema's own default.

**The directory names** `_sources` and `_sources/cache`, and the derived-path
rule: a local file yields `<raw path>.md` and `<raw path>.locator.json`; a
capture yields `_sources/<source_id>.md` and
`_sources/<source_id>.locator.json`, both built from the minted id and never
from the URL.

**The `span_id` join rule.** An adapter emits Markdown one structure per line
and records which derived line each locator produced; the caller fills in the
span id that `auditor.normalize_source` assigned to that line. No adapter
computes a span id.

**The one line of `journal.py` this phase changed.** Plan `14C-01` added the
`rights=None` parameter to `journal.op_link`, additively. Every other 14C
commit leaves `journal.py` untouched, and every 14C commit leaves
`runtime.py`, `model.py`, and `auditor.py` untouched, measured per commit
below.

## What breaks if this is changed later

**Renaming a sidecar field** breaks every sidecar already written and every
citation naming a span in one. A sidecar is a durable record read back by the
recheck path and by any future binding code; a field rename is a migration,
not an edit.

**Changing the `span_id` join** breaks the link between an origin locator and
the one parser's spans, which is the only thing that makes a citation resolve
into a PDF page or an EPUB fragment. It is also what keeps "one parser"
structurally true across ten media: if an adapter ever computed a span id, the
repository would have two parsers whether or not anyone called it that.

**Renaming a route literal or a CLI command** breaks any external harness,
including the Cordis-based one D-02 explicitly invites. Both are published
contract, which is why plan `14C-04` rated the recheck route's naming costly
rather than reversible.

**Removing or retyping a field inside an existing `oneOf` branch** is not
additive and needs a `schema_version` bump plus an explicit `migrate`
operation. Adding a branch is additive, which is what `body_asr` proved:
every existing gold-case end-to-end check was re-run against the amended
document rather than inspected.

**Loosening `body_ocr`'s null-typed `bbox` and `confidence`** would let an
adapter start inventing geometry the OCR bridge never measured. The null
typing is not an oversight to be corrected; it is what makes honest
degradation enforceable, asserted by feeding the schema a fabricated bbox and
requiring it to be rejected.

**Changing the two-file write ordering** reintroduces the
applied-source-with-no-sidecar state that `check_two_file_pair_atomicity`
exists to prevent. The sidecar is written first and removed on a journal
refusal, so a fault leaves the old pair or the new pair and never half of one.

**Wiring `recheck_origin` into the journal** would make a citation's validity
depend on network reachability, which breaks D-04 and the degrade-never-block
rule in one move. It is a read, asserted mechanically.

**Making the private-origin refusal liftable by a request body field** rather
than by the `source.allow_private_origins` setting would let an agent reach
the learner's own network by asking. The whole test section lifts it through
the setting, which is itself the proof that the default denies.

## Multi-source coverage audit

| Source | Item | Covered by | Verified by | Status |
|---|---|---|---|---|
| GOAL | ROADMAP Phase 14C: one adapter contract and one locator sidecar schema for every source medium | plans 01 to 08 | `python3 -c "import source_adapters as s; sorted(s.ADAPTER_REGISTRY)"` returns ten keys; `python3 schema_validate.py --all` exit 0 | covered |
| REQ | no requirement IDs assigned to 14C in ROADMAP | n/a | coverage derived from CONTEXT.md per the phase description's own instruction; recorded here rather than left implicit | covered by derivation |
| REQ | FILE-01 (an approved root's files are addressable objects) | 01 T3, 02 T3 | `check_thin_slice`, `check_write_containment` | covered |
| REQ | FILE-03 (a durable write is atomic and journaled) | 02 T3 | `check_two_file_pair_atomicity` in `tests/file_fault_tracer.py` | covered |
| REQ | RIGHTS-01 (an unresolved grant is never permissive) | 01 T3, 04 T2 | `check_rights_refusal`, `check_no_rights_escalation`, `check_remote_capture_rights` | covered |
| REQ | TREAT-02 (a source is addressable at a place, not only as a file) | every adapter plan | `check_pdf_gold_cases`, `check_docx_gold_cases`, `check_pptx_gold_cases`, `check_web_locator_anchors`, `check_transcript_timestamp_locators`, `check_epub_fragment_anchor` | covered |
| REQ | PORT-02 (interchange carries an explicit semantic loss report) | 07 T3 | `check_epub_gold_cases` asserts the unread navigation document is named in every EPUB sidecar's unsupported list | covered, requirement not completed |
| RESEARCH | Pitfall 1: python-docx reads no footnotes, headers, footers, comments, or tracked changes | 02 T2 | `check_docx_extra_parts` | covered |
| RESEARCH | Pitfall 2: the OCR skill returns flat text, not bbox plus confidence | 06 T1 | `check_ocr_honest_degradation`, including the schema refusing a fabricated bbox | covered |
| RESEARCH | Pitfall 3: zip and XML hardening for the container formats | 02 T1 | `check_zip_bomb_guard`, `check_xml_entity_guard`, `check_epub_uses_shared_seam` | covered |
| RESEARCH | Pitfall 4: a redirect can leak headers or land on an unintended scheme | 04 T2 | `check_redirect_hardening`, four scenarios plus a direct unit assertion on the handler | covered |
| RESEARCH | Pitfall 5: pdfplumber geometry is expensive on image-heavy pages | 02 T3 | the `page.chars` short circuit before `extract_words` and `find_tables`; `check_pdf_gold_cases` covers the image-only page | covered |
| RESEARCH | A1: exact sidecar field names | 01 T1 | `schemas/source_locator.schema.json` built from the plan's table verbatim; `check_thin_slice` validates a written sidecar against it | covered, assumption held |
| RESEARCH | A2: `pdfplumber.Page.extract_words()` key names | 01 T3 | measured against the installed 0.11.10 and recorded in `14C-01-SUMMARY.md`; the four assumed keys are all present | covered, assumption held |
| RESEARCH | A3: remote-staleness signal design | 04 T3 | `check_recheck_states`, `check_recheck_preserves_citation`, `check_recheck_no_validator_falls_back` | covered, design implemented as recommended |
| RESEARCH | A4: dependencies pip-installed and lazily imported per call | 01 T2, every adapter | `check_degrades_without_dependencies` blocks six libraries and asserts each adapter refuses by name while others work | covered, assumption held |
| RESEARCH | A5: the `/api/source/import` route name and body shape | 01 T4 | `check_api_route_scope`, `check_api_source_import_route` | covered, assumption held |
| RESEARCH | A6: postinstall safety of the eight audited packages not independently re-verified | 01 T2 | recorded as an accepted limit in `D-14C-3`; not closed by this phase | flagged-unverified: an sdist build-script inspection was never run, and no plan in 14C promised one |
| RESEARCH | the `ebooklib` AGPL finding, new as of 2026-08-21 | 07 T1 | `D-14C-2` plus `IL-20260828-05`; `scripts/check_vendored.py` fails on a row naming it | covered |
| RESEARCH | the RIGHTS-01 no-new-code finding (the journal already gates transform) | 01 T3 | `check_rights_refusal` shows the refusal comes from `journal.rights_unknown`, not from adapter code | covered |
| RESEARCH | the OCR flat-text finding | 06 T1 | `check_ocr_honest_degradation` | covered |
| RESEARCH | the eight-package legitimacy batch | 01 T2 | `D-14C-3` records per-package PyPI, GitHub, and OSV evidence and Weibao's approval | covered |
| CONTEXT | D-01: one registry, not one subphase per format | 01 T1 | `check_one_import_path` proves markdown reaches disk through the same function a PDF does | covered |
| CONTEXT | D-02: Python, and the boundary is the existing daemon | 01 T4, 04 T3 | `check_api_route_scope`, `check_cli_and_route_parity` | covered |
| CONTEXT | D-03: remote sources are in scope | 04 T2 | `check_private_origin_refused` and the loopback capture path | covered |
| CONTEXT | D-04: bind a snapshot, not a URL | 04 T2 | `check_snapshot_both_ways`, which reads both captures back with the origin stopped | covered |
| CONTEXT | D-05: the adapter never touches the scorer | every plan | `check_no_second_parser`; per-commit `git diff` on `runtime.py`, `model.py`, `auditor.py` is empty for all eight 14C commits | covered |
| CONTEXT | Roster 1: PDF and DOCX | 01 T3, 02 T2, 02 T3 | `check_pdf_gold_cases` (9 of 9), `check_docx_gold_cases` (11 of 11) | covered |
| CONTEXT | Roster 2: PPTX | 03 T2 | `check_pptx_gold_cases` (6 of 6), `check_pptx_slide_order` | covered |
| CONTEXT | Roster 3: web capture | 04 T2 | `check_web_gold_cases` (6 of 6), `check_fetch_limits`, `check_snapshot_containment` | covered |
| CONTEXT | Roster 4: transcript intake | 05 T2 | `check_transcript_gold_cases` (8 of 8), `check_transcript_no_dependency` | covered |
| CONTEXT | Roster 5: video and audio via ASR | 08 T1 | `check_asr_registered_not_built`, `check_asr_locator_shape_frozen` | covered as registered-not-built, which is the roster's own disposition |
| CONTEXT | Roster 6: OCR | 06 T1 | `check_ocr_stubbed_extraction`, `check_ocr_single_implementation` | covered; the live-model eye check is recorded UNRUN in `14C-06-SUMMARY.md` |
| CONTEXT | Roster 7: EPUB | 07 T3 | `check_epub_gold_cases` (7 of 7), `check_epub_spine_order`, `check_epub_drm_refused` | covered |
| CONTEXT | Build both: agent auto-fetch versus approve-before-bind | 04 T2 | `check_bind_policy_gate`, four cases plus the free-preview assertion under both policies | covered, both paths ship |
| CONTEXT | Build both: inline snapshot versus reference plus cache | 04 T2 | `check_snapshot_both_ways`, asserting one identical fingerprint across both modes | covered, both paths ship |
| CONTEXT | Out of scope: no second parser, scorer, or evidence store | every plan | `check_no_second_parser`; the empty per-commit diff above | honored |
| CONTEXT | Out of scope: no TypeScript rewrite, no plugin kernel | every plan | the phase produced one Python module, one schema, four fixture modules, one script, and no loader or kernel; inventory below | honored |
| CONTEXT | Out of scope: no hosted multi-tenant anything | 04 T2 | `check_write_containment`, `check_snapshot_containment` | honored |
| CONTEXT | Out of scope: PyMuPDF is not adopted | 01 T2, 08 T2 | `scripts/check_vendored.py` fails on a row naming it; no import exists | honored |
| CONTEXT | Out of scope: an unresolved rights grant is never permissive | 01 T3, 04 T2 | `check_rights_refusal`, `check_no_rights_escalation`, `check_remote_capture_rights` | honored |
| CONTEXT | OQ-1: the frozen sidecar schema and its version field | 01 T1 | `D-14C-1`; `python3 schema_validate.py --all` | closed |
| CONTEXT | OQ-2: whether a snapshot is a source, an artifact, or both | 04 T2 | a capture is a `kind="source"` journal object with an `origin.kind` of `remote_url`; `check_remote_capture_rights` reads the registry row | closed |
| CONTEXT | OQ-3: one route or one route per adapter | 01 T4 | one fixed-literal route per capability with an opaque body identifier; `check_api_route_scope` | closed |
| CONTEXT | OQ-4: how a changed or vanished remote origin surfaces | 04 T3 | `check_recheck_states`, `check_recheck_preserves_citation` | closed |
| CONTEXT | OQ-5: eager or lazy adapter dependency install | 01 T2, every adapter | lazy per-call import; `check_degrades_without_dependencies` | closed |
| VALIDATION | Wave 0 harness | 01 T3 | `check_thin_slice` | green |
| VALIDATION | Roster 1 PDF: a scanned page is a typed refusal, never silent empty text | 02 T3 | `check_pdf_gold_cases`, `check_scanned_pdf_is_typed_unsupported` | green |
| VALIDATION | Roster 1 DOCX: six extra parts resolve to gold locators | 02 T2 | `check_docx_gold_cases`, `check_docx_extra_parts` | green |
| VALIDATION | Roster 2 PPTX: slide text plus a notes flag; a media-only slide refused per slide | 03 T2 | `check_pptx_gold_cases`, `check_pptx_notes_flag`, `check_pptx_partial_refusal` | green |
| VALIDATION | Roster 3 web: a stable anchor and a refused non-http redirect | 04 T1, 04 T2 | `check_web_gold_cases`, `check_web_locator_anchors`, `check_redirect_hardening` | green |
| VALIDATION | Roster 4 transcript: SRT and VTT produce `start_ms` and `end_ms` | 05 T2 | `check_transcript_gold_cases`, `check_transcript_timestamp_locators` | green |
| VALIDATION | Roster 7 EPUB: spine order, one resolving fragment anchor, DRM refused | 07 T3 | `check_epub_spine_order`, `check_epub_fragment_anchor`, `check_epub_drm_refused` | green |
| VALIDATION | D-02 route shape and its authority gate | 01 T4, 04 T3 | `check_api_route_scope`, `check_api_source_import_route`, `check_api_source_recheck_route`, `check_cross_origin_gate_on_mutating_routes` | green |
| VALIDATION | Journal integration and the rights refusal | 01 T3, 04 T2 | `check_thin_slice`, `check_rights_refusal`, `check_no_rights_escalation` | green |
| VALIDATION | Zip and XML hardening | 02 T1 | `check_zip_bomb_guard`, `check_xml_entity_guard` | green |
| VALIDATION | Two-file atomic write | 02 T3 | `check_two_file_pair_atomicity` | green |
| VALIDATION | Roster 6 OCR honest degradation | 06 T1 | `check_ocr_stubbed_extraction`, `check_ocr_honest_degradation` | green |
| VALIDATION | Roster 5 ASR registered with a frozen locator shape | 08 T1 | `check_asr_registered_not_built`, `check_asr_locator_shape_frozen`, `check_asr_body_matches_transcript_body` | green |
| VALIDATION | Supply chain: recorded checksums are recomputed in CI | 08 T2 | `python3 scripts/check_vendored.py`; `check_vendored_manifest`, which observes the gate failing three ways | green |

**One row is `flagged-unverified` and it is the A6 row**: no plan in this
phase downloaded and inspected the eight audited packages' sdist build
scripts, and none promised to. It is recorded as an accepted limit in
`D-14C-3` rather than quietly marked covered.

**Artifact inventory**, for the no-kernel-no-rewrite prohibition: this phase
produced one Python module (`source_adapters.py`, extended across eight
plans), one schema (`schemas/source_locator.schema.json`), four new fixture
modules (`pptx_`, `web_capture_`, `transcript_`, and `epub_fidelity_cases.py`),
one CI script (`scripts/check_vendored.py`), one root document
(`VENDORED.md`), one preflight gate mirroring the new CI step, two daemon
handlers, two CLI subcommand surfaces, and no loader, kernel, plugin mount, or
dynamic import machinery of any kind.

## Spec-less probe fallback

Phase 14C had **no `SPEC.md`** and **no requirement IDs in ROADMAP**. The
spec-less probe fallback was therefore skipped on purpose during planning; no
probe-derived predicates were generated, and no plan's `must_haves` claims to
descend from one. They were derived instead from `14C-CONTEXT.md`'s five
decisions, seven roster items, two build-both directives, and five
out-of-scope refusals, and from `14C-VALIDATION.md`'s frozen behavior rows,
which is why the coverage audit above enumerates those sources item by item
rather than a probe list. This is a recorded choice and not a silent gap.

## Recorded deviations

Lifted from the seven summaries. Each is recorded there in full; this is the
index.

- **Roster item 1 was split across plans `14C-01` and `14C-02`** for tracer
  discipline: one PDF gold case through one route is a thinner first slice
  than two adapters through one route.
- **`pdfplumber.Page.extract_words()` returned exactly the four keys the plan
  assumed** (`x0`, `top`, `x1`, `bottom`), so A2 held. `find_tables()` cells
  are **plain 4-tuples**, not dicts, and the line-based strategy finds zero
  tables in the gold fixtures, so the text strategy plus a two-column,
  two-non-empty-row filter is what separates the table case from ordinary
  prose.
- **`surfaces.update._origin_of` was duplicated, not imported**, because
  `source_adapters` is a model-tier module and the import would pull the whole
  updater in to compare three strings. The copy is marked as a deliberate
  duplicate that must stay in step.
- **One gold case's recorded reading order could not be reproduced, and the
  manifest was corrected rather than the adapter.** `pdf-footnote`'s content
  stream draws three lines and its manifest recorded two, omitting a mid-page
  decoy line. The bytes and the recorded sha256 are untouched.
- **`adapter_expectation` is defined mechanically** as `unsupported` exactly
  when `reading_order` is empty, not as the plan's "every case with a
  non-empty unsupported list", which would have demanded a refusal from two
  cases whose gold records a reading order.
- **stdlib checks a redirect's scheme before `redirect_request` runs, and
  allows ftp**, so the scheme lock sits in `http_error_302` with the four
  aliases re-bound.
- **`ok_result`'s `journal_entry_id` had been null since `14C-01`**, because
  `journal.commit_operation` returns a registry row carrying no entry id.
  Found by reading the JSON of a real capture; fixed inside `source_adapters`.
- **`slide.part.partname` reports a slide's position, not its archive member**,
  so the resolved sldId order is joined to python-pptx's slides positionally.
- **python-pptx needs a slide master and a slide layout** with their
  relationship parts before it will open a package; the plan's minimal part
  list omitted both.
- **The OCR temp-file cleanup, the sidecar temp-file cleanup, and the
  `_zip_member_error` archive preflight** are three small hardenings none of
  the plans named, each added because a test written first went red without
  it.
- **`scripts/preflight.py` gained a `vendored` gate**, which plan `14C-08`
  did not list. `tests/preflight_roundtrip.py` fails on any CI step that no
  local gate mirrors and `CI_ONLY` does not excuse, so adding the CI checksum
  step alone broke that test. Mirroring it as a real local gate is the right
  half of that choice: `CI_ONLY` would have said "push and read the CI log"
  for a check that runs in under a second locally.

## Open reconsideration conditions

Every parked or refused thing in this phase, with the condition that reopens
it. A later session should be able to find all of them here.

- **`ebooklib` 0.20, parked on AGPL** (`D-14C-2`, `IL-20260828-05`). Reopens
  if a real EPUB proves unreadable by the stdlib path; or if the product's
  licensing posture changes, for example a decision to ship itembank as AGPL
  open source; or if the stdlib path's extraction fidelity or reading
  presentation is visibly worse than a library's in a way that matters to a
  learner. The third trigger is Weibao's own, from his rider.
- **PyMuPDF, parked on AGPL** (`IL-20260815-07`, note of 2026-08-17). Same
  licensing trigger.
- **`trafilatura` 2.2.0, refused on dependency weight**, not on legitimacy.
  Reopens if `readability-lxml`'s extraction quality proves inadequate on real
  course material.
- **`webvtt-py`, refused on cost.** Reopens if the hand-rolled SRT and VTT
  parser proves fragile on a real caption file. Nothing has fired it: all
  eight transcript fixtures parse, but they are fixtures written from the
  specifications, not files exported by a real captioning tool.
- **`body_ocr`'s null-typed `bbox` and `confidence`.** A structured-output OCR
  mode that really measures geometry is a `schema_version` bump and a recorded
  migration, never a loosened type.
- **`_parse_xml_safely`'s outright DOCTYPE refusal.** No legitimate XHTML or
  OOXML part in any of the twenty-seven container fixtures needed a doctype,
  so the refusal never had to become format-specific. Reopens if a real EPUB
  or DOCX carries one; the change would be a per-format allowance, not a
  softening to a depth limit, since a budget still runs the expander.
- **The DNS-rebinding limit in `_host_is_private`.** It resolves once and does
  not pin the resolved address for the connection. Recorded in the function's
  own docstring as a known limit rather than left silently absent.
- **The unread EPUB navigation document.** Every EPUB sidecar names it in the
  unsupported list, so a course built on EPUB imports carries no hierarchical
  table of contents and says so.
- **`COVERAGE.md`'s HEAD-probe row**, moved from `INTEGRATE` to `OPT-OUT` by
  plan `14C-04` with its reason. Reopens if a reachability-only probe is ever
  wanted on its own.
- **`pypdf`'s pin.** `D-14C-3` records an agent choice to pin 6.16.2; the pins
  file and `VENDORED.md` both still read 6.16.1. Moving it means fetching the
  wheel and recording its own hash, which is a supply-chain action rather than
  a text edit. Recorded in `VENDORED.md`'s update-cadence section.
- **The OCR live-model checkpoint, UNRUN.** `14C-06-SUMMARY.md` carries the
  four eye checks and the degraded-run step still owed, with the date it could
  not run and why.

## Evidence

Commands and their output, not claims about them.

```
$ for t in tests/*.py; do python3 "$t" || exit 1; done
(no output; every one of the 88 suite files exits 0)

$ python3 schema_validate.py --all
ok: write_manifest.schema.json
20 schema documents self-check clean

$ python3 scripts/check_vendored.py
ok: pdfplumber (pin 0.11.10)
ok: pdfminer.six (pin 20260107)
ok: python-docx (pin 1.2.0)
ok: pypdf (pin 6.16.1)
ok: python-pptx (pin 1.0.2)
ok: readability-lxml (pin 0.8.4.1)
ok: vendor/katex/katex.min.js
ok: vendor/katex/katex.min.css
ok: assets/vendor/codemirror/codemirror.bundle.js
ok: fonts/source-serif (2 files via fonts/MANIFEST.json)
ok: fonts/ia-writer-quattro (2 files via fonts/MANIFEST.json)
11 vendored artifacts match their recorded checksums

$ python3 itembank.py guard .

0 offending files

$ for c in <the eight 14C commits>; do git show --stat --format= $c -- runtime.py model.py auditor.py; done
(no output for any of the eight)

$ for c in <the eight 14C commits>; do git show --stat --format= $c -- journal.py; done
 journal.py | 14 +++++++++++---
 1 file changed, 11 insertions(+), 3 deletions(-)
(from 99dd2ba, plan 14C-01's op_link rights parameter, and from no other commit)
```

The whole-repository `git diff` against a pre-phase commit is deliberately not
quoted here: other phases committed to `runtime.py` and `model.py` in the same
window, so a range diff would attribute their work to 14C. The per-commit form
above is the honest measurement and it is empty for all eight.
