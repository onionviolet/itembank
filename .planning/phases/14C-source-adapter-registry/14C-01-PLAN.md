---
phase: 14C-source-adapter-registry
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - schemas/source_locator.schema.json
  - source_adapters.py
  - journal.py
  - surfaces/daemon.py
  - surfaces/cli.py
  - schemas/settings.schema.json
  - itembank.json
  - deps/source-adapter-pins.txt
  - VENDORED.md
  - tests/source_adapters_roundtrip.py
  - tests/daemon_roundtrip.py
  - tests/config_roundtrip.py
  - .planning/phases/14C-source-adapter-registry/14C-DECISIONS.md
autonomous: false
requirements: [D-01, D-02, D-04, D-05, OQ-1, OQ-2, OQ-3, OQ-5, ROSTER-1-PDF, FILE-01, FILE-03, RIGHTS-01, TREAT-02]
user_setup:
  - service: pypi
    why: "The PDF adapter needs pdfplumber and pdfminer.six installed once at checkout time. SUPPLY-CHAIN-POLICY.md section 2.1 forbids the running app fetching them, so a human runs the pinned install once."
    dashboard_config:
      - task: "Run the pinned install command printed in deps/source-adapter-pins.txt after the package-legitimacy checkpoint clears"
        location: "a shell in the repository root"
estimate:
  tokens: 190000
  raw_tokens: 95000
  tasks: 4
  confidence: low
assumption_delta_decision:
  noun: "a source object carrying an adapter name and a locator sidecar"
  decision: promote
  rationale: "itembank accepted exactly one source medium (Markdown or plain UTF-8) and this phase introduces eight. The general representation is promoted to primary: every source, hand-written Markdown included, now enters through the one import path, with markdown and text registered as identity adapters that pass bytes through unchanged. Adding the new media alongside a still-privileged Markdown side door would silently contradict the generalization."
  what_would_force_revisit: "not applicable; this is the promote branch. If a later phase adds a source-creation path that does not call source_adapters.import_source, the promotion has been quietly reverted and check_one_import_path goes red."
must_haves:
  truths:
    - "One PDF gold case travels the whole phase path end to end in one commit: bytes are extracted to Markdown, a locator sidecar is written and schema-validated, one fingerprint is minted through identity.object_fingerprint(md_bytes, \"source\"), one applied journal entry is appended, and POST /api/source/import reaches the same function the CLI reaches."
    - "source_adapters.py never raises: every failure family, including a missing third-party library, an unknown adapter name, a scanned page with no text, and an unexpected internal exception, converts to one typed result carrying a named source.* reason code before any caller sees it."
    - "A scanned, image-only PDF returns a typed unsupported result with reason code source.unsupported, writes no Markdown, writes no sidecar, and appends no applied journal entry. It is never a silent empty extraction."
    - "source_adapters.py computes no spans of its own. Span identity comes from auditor.normalize_source(md_bytes, source_id, kind=\"markdown\"), so the sidecar's span_id values are the one parser's span ids and not a second numbering scheme."
    - "A raw file whose recorded transform right is not exactly \"granted\" cannot be imported from: journal refuses by name with journal.rights_unknown before any mutation, and the orphan sidecar is removed, leaving no half-written pair."
    - "A rights grant supplied on the wire applies only when the raw file is being linked for the first time. It never overwrites the rights already recorded on an existing registry row."
    - "POST /api/source/import refuses a cross-origin request with 403 and refuses a non-loopback client with 403, before any extraction, any file write, and any journal append."
    - "itembank source import and POST /api/source/import reach the same source_adapters.import_source call; neither surface re-implements extraction, fingerprinting, or the journal append."
    - "A missing pdfplumber degrades only the pdf adapter. Importing a Markdown source, starting the daemon, and every existing command all behave byte-identically with the third-party libraries absent."
  prohibitions:
    - statement: "No second parser, scorer, or evidence store. source_adapters.py imports auditor, identity, journal, and discovery only; it never imports model.py or runtime.py, and it never splits text into spans itself."
      status: flagged-unverified
      verification: "check_no_second_parser in tests/source_adapters_roundtrip.py asserts that source_adapters has no attribute named model or runtime after import, and that the module source contains no local span-splitting function."
    - statement: "No rewrite of itembank in TypeScript and no plugin kernel reimplemented in Python. The boundary is one daemon route and one CLI command on the existing surfaces."
      status: flagged-unverified
      verification: "files_modified in this plan contains no .ts, .js, or plugin-loader file, and no module named plugin, kernel, or loader is created."
    - statement: "No hosted multi-tenant anything. Snapshots, sidecars, derived Markdown, and journal entries are written only under the caller-supplied approved base root on local disk."
      status: flagged-unverified
      verification: "every durable write in source_adapters.py goes through journal.commit_operation, whose discovery.inside_any_root preflight refuses a path outside base with journal.path_outside_root; check_write_containment asserts a base-escaping rel_path is refused."
    - statement: "PyMuPDF is not adopted. It stays parked on an explicit Weibao AGPL decision, and ebooklib now joins it on the same grounds."
      status: flagged-unverified
      verification: "grep deps/source-adapter-pins.txt and VENDORED.md for the strings PyMuPDF, fitz, and ebooklib; all three must be absent from every pin line and present only inside a parked-decision comment."
    - statement: "An unresolved rights grant is never treated as permissive. Unknown rights stay restrictive."
      status: flagged-unverified
      verification: "check_rights_refusal in tests/source_adapters_roundtrip.py links a raw file with no rights argument, attempts an import from it, and asserts journal.rights_unknown plus zero applied entries plus zero files on disk."
  artifacts:
    - "schemas/source_locator.schema.json, the frozen locator sidecar contract"
    - "source_adapters.py at the repository root, a runtime-tier peer of journal.py"
    - "deps/source-adapter-pins.txt, the pinned optional adapter dependency set"
    - "VENDORED.md at the repository root, created by this plan per SUPPLY-CHAIN-POLICY.md section 2.2"
    - "tests/source_adapters_roundtrip.py with check_thin_slice() as its first function"
    - "POST /api/source/import in daemon.API_ROUTES, daemon.ROUTE_CLI, and daemon.SURFACE_PARITY"
    - "itembank source import in surfaces/cli.py"
    - "the source settings group in schemas/settings.schema.json and in the shipped itembank.json"
    - ".planning/phases/14C-source-adapter-registry/14C-DECISIONS.md"
  key_links:
    - "The sidecar's locators[].span_id equals auditor.normalize_source(md_bytes, source_id, kind=\"markdown\")[\"spans\"][N][\"span_id\"], which is the literal string \"sp-N\" for the N-th line of the derived Markdown. This is the only join between the origin locator (a page, a slide, a millisecond offset) and the citation record auditor.citation already produces. If an adapter emits a span_id the one parser never produced, every citation into that source resolves to nothing and the failure is silent."
    - "The sidecar file is written FIRST and the journal entry SECOND. Reversing the order can leave an applied source object with no locators beside it, which a later citation cannot detect. The sidecar is the cheap, self-evidently repairable half; the journal entry is the authoritative half."
    - "ROUTE_CLI[(\"POST\", \"/api/source/import\")] must be the literal string source, not the two-word string \"source import\". tests/daemon_roundtrip.py:check_route_cli_inventory greps surfaces/cli.py for add_parser(\"<value>\") and fails on anything that is not a registered parser name. The existing (\"POST\", \"/api/lesson/run\"): \"lesson\" row is the precedent."
    - "journal.op_link gains an optional rights parameter in this plan. It must default to None so every existing caller and every existing test stays byte-identical; commit_operation already defaults a kind=source object with no rights to identity.rights_default()."
---

<objective>
Freeze the locator sidecar contract once, for every medium, and prove it end to
end on the thinnest real path: one PDF gold case, extracted to Markdown, with a
schema-validated sidecar beside it, one fingerprint, one applied journal entry,
one daemon route, one CLI command, one green roundtrip test. Everything the rest
of this phase does is an expansion of the spine built here.

This plan also closes four of CONTEXT.md's five open questions in plan text so
the executor never re-derives one, and gates the fifth (the frozen schema)
behind a blocking decision checkpoint because it is a one-way door: the moment a
sidecar is written and a citation points into it, the field names are a
published contract and undoing them needs a migration.

Decisions already made, cited, and never re-litigated here:

- **D-01** (`14C-CONTEXT.md` lines 22 to 27): one registry, not one subphase per
  format. pdfplumber pinned with pdfminer.six for PDF, python-docx for DOCX,
  pypdf as the page-level fallback. PyMuPDF stays parked on its AGPL decision.
  Adoption runs through `SUPPLY-CHAIN-POLICY.md` section 3.
- **D-02** (`14C-CONTEXT.md` lines 28 to 35): Python, and the boundary is the
  existing daemon. Intake gets a route there like every other capability. An
  external harness is an HTTP client of that route.
- **D-04** (`14C-CONTEXT.md` lines 40 to 45): bind a snapshot, not a URL.
  Relevant here only in that the sidecar envelope carries `origin` and
  `captured_at` from the start; the fetch itself lands in plan `14C-04`.
- **D-05** (`14C-CONTEXT.md` lines 46 to 47): the adapter never touches the
  scorer. This plan adds zero lines to `runtime.py` and `model.py`.
- **PLANNING-DIRECTIVES.md section 4**, all five non-negotiables, in particular
  number 2 (exactly one parser, one scorer, one evidence store) and number 4
  (format changes are additive, proven by a byte-identical fixture).
- **SUPPLY-CHAIN-POLICY.md section 2.1**: no install-time network fetch on the
  learner's machine.

Open questions this plan closes, with the locked answer and its rationale, so the
executor never guesses (the `PLANNING-DIRECTIVES.md` section 5 bar):

| Open question | Locked answer | Rationale |
|---|---|---|
| OQ-2. Is a captured snapshot a source, an artifact, or both in the 14B graph? | **A source.** `identity.OBJECT_KINDS` is the frozen six-member tuple `("course", "objective", "source", "lesson", "bank", "component")` and this phase passes only `"source"`. The `.locator.json` sidecar is a non-identity-bearing companion file: it is never minted an `object_id`, never fingerprinted as an object, and never appears in the registry. | `identity.py:32` plus `14A-FREEZE.md`: adding an object kind forces a review of every kind-conditional rule that already exists. There is no product need. **Closed. Do not re-decide.** |
| OQ-3. One route or one per adapter? | **One route**, `POST /api/source/import`, with an `adapter` field in the JSON body. Plan `14C-04` adds exactly one more, `POST /api/source/recheck`, for the staleness probe. | `surfaces/daemon.py:216-222` states the route table's own rule: fixed literals, opaque identifiers in the JSON body, never in a path segment, and the table length is asserted in `tests/daemon_roundtrip.py`. Seven routes would mean seven entries in three tables. **Closed.** |
| OQ-4. How does a changed or vanished remote origin surface as stale without breaking an issued citation? | **A read-time advisory, never a mutation.** The accepted revision and its fingerprint never change because a remote page changed. `itembank source recheck` reports `origin_unchanged`, `origin_changed`, or `origin_unreachable` and touches neither `journal.jsonl` nor the object's fingerprint. Only an explicit learner re-capture commits a new revision through `journal.op_edit_in_place`. Built in plan `14C-04`; the sidecar fields it reads (`origin.http_etag`, `origin.http_last_modified`, `origin.fetched_at`) are frozen here. | `journal.detect_external_edits` re-hashes an on-disk file against its accepted fingerprint; there is no on-disk file for a URL, so none of that machinery can fire. Making staleness advisory is what keeps D-04's promise that a changed remote source is detectable rather than a silently broken citation. **Closed.** |
| OQ-5. Do adapter dependencies install eagerly or on first use? | **Neither, precisely.** Installed once at checkout time from `deps/source-adapter-pins.txt`; imported lazily inside each adapter function so one missing library degrades only that one adapter; never fetched from a registry while the app runs. | `SUPPLY-CHAIN-POLICY.md` section 2.1 forbids an install-time network fetch on the learner's machine, which is exactly what a runtime `pip install` would be once the app is packaged. Lazy import is the "first use" that is actually available. **Closed.** |
| OQ-1. The frozen sidecar schema and its version field. | **Task 1 is a blocking decision checkpoint.** The recommended default is the contract tabled below. | One-way door: a citation pointing into a sidecar makes the field names published. |

The generalization decision this phase forces, recorded in frontmatter as
`assumption_delta_decision` and restated here so it is not lost: itembank
accepted exactly one source medium and now accepts eight, so the primary noun
becomes **a source object carrying an adapter name and a locator sidecar**, of
which a hand-written Markdown file is the trivial identity-adapter variant. That
is a **promote**, not an add-alongside: `ADAPTER_REGISTRY` carries `"markdown"`
and `"text"` identity adapters from the first commit, and
`check_one_import_path` asserts that a Markdown source and a PDF source reach
disk through the same function.

Purpose: prove the whole architecture on one path before eight adapters are
built on it.
Output: the frozen schema, the registry module, the route, the CLI command, the
pins, and the first green roundtrip test.
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
@.planning/PLANNING-DIRECTIVES.md
@.planning/PLAN-TEMPLATE.md
@.planning/SUPPLY-CHAIN-POLICY.md
@.planning/phases/14A-identity-lifecycle-operation/14A-FREEZE.md
@identity.py
@journal.py
@auditor.py
@model_adapter.py
@schema_validate.py
@schemas/normalized_document.schema.json
@fixtures/audit/locator_fidelity_cases.py
@deps/lti-pins.txt
</context>

## Artifacts this phase produces (plan 14C-01 share)

Every symbol below is new in this phase and exists in no shipped file.

- `schemas/source_locator.schema.json`
  - Root object with `x-itembank-version: 1`.
  - `$defs`: `locator`, `rights`, `origin`, `unsupported_entry`, and the eight
    per-medium bodies `body_markdown`, `body_pdf`, `body_docx`, `body_pptx`,
    `body_epub`, `body_web`, `body_transcript`, `body_ocr`. `body_asr` is added
    by plan `14C-08`.
- `source_adapters.py`
  - Constants: `SOURCE_LOCATOR_VERSION = 1`, `SOURCE_ADAPTER_CODES`,
    `ADAPTER_REGISTRY`, `ADAPTER_VERSIONS`, `LOCATOR_KINDS`,
    `SIDECAR_SUFFIX = ".locator.json"`, `DERIVED_MD_SUFFIX = ".md"`,
    `REMOTE_DIRNAME = "_sources"`, `MAX_INPUT_BYTES_DEFAULT = 209715200`.
  - Public functions created here: `import_source(...)`, `preview_source(...)`,
    `sidecar_path_for(md_rel_path)`, `build_sidecar(...)`,
    `unsupported_result(code, message, source_id)`, `ok_result(...)`,
    `write_sidecar_atomic(path, sidecar)`.
  - Private extraction functions created here: `_extract_markdown`,
    `_extract_text`, `_extract_pdf`.
  - Registry keys present after this plan: `markdown`, `text`, `pdf`. Plans 02
    through 08 add `docx`, `pptx`, `web`, `transcript`, `ocr`, `epub`, `asr`.
- `journal.py`
  - One additive change only: `op_link` gains a trailing keyword parameter
    `rights=None`, passed straight through to `commit_operation`. No other line
    of `journal.py` changes in this phase.
- `surfaces/daemon.py`
  - Constant: `SOURCE_IMPORT_ALLOWED_FIELDS`.
  - Handler: `handle_api_source_import(handler)`.
  - One new row each in `API_ROUTES`, `ROUTE_CLI`, and `SURFACE_PARITY`.
- `surfaces/cli.py`
  - `cmd_source(a)` plus the `source` parser with the `import` subcommand.
- `schemas/settings.schema.json` and `itembank.json`
  - The `source` settings group: `bind_policy`, `snapshot_storage`,
    `snapshot_inline_max_bytes`, `allow_private_origins`,
    `fetch_timeout_seconds`, `max_input_bytes`.
- `deps/source-adapter-pins.txt`, `VENDORED.md`
- `tests/source_adapters_roundtrip.py` with `check_thin_slice()` first.

New refusal codes introduced by this plan, the full `SOURCE_ADAPTER_CODES`
tuple as of plan 01 (later plans append and never rename):

`source.adapter_unknown`, `source.approval_required`,
`source.backend_unconfigured`, `source.dependency_missing`,
`source.encrypted`, `source.fetch_failed`, `source.internal_error`,
`source.malformed_input`, `source.origin_refused`, `source.oversized`,
`source.redirect_refused`, `source.unsupported`.

New journal record types: none. New object kinds: none.

## The frozen sidecar contract (Task 1's recommended default)

`schemas/source_locator.schema.json`, root object, `additionalProperties: false`
at every object level, `required` naming every field below.

| Field | Type and constraint | Meaning |
|---|---|---|
| `schema_version` | integer, `const: 1` | equals the document's `x-itembank-version` |
| `source_id` | string, `pattern: "^[0-9a-f]{16}$"` | the 14A `object_id` of the derived Markdown `source` object |
| `adapter` | string, `enum: ["markdown","text","pdf","docx","pptx","epub","web","transcript","asr","ocr"]` | which registry entry produced this |
| `adapter_version` | string, `pattern: "^[0-9]+\\.[0-9]+\\.[0-9]+$"` | `ADAPTER_VERSIONS[adapter]` at extraction time |
| `fingerprint` | string, `pattern: "^sha256:[0-9a-f]{64}$"` | `identity.object_fingerprint(md_bytes, "source")`, the same value the journal entry records as `after_fingerprint` |
| `captured_at` | string, `pattern: "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\\.[0-9]{3}Z$"` | `identity.utc_now()` |
| `origin` | object, `$ref: "#/$defs/origin"` | where the bytes came from |
| `rights` | object, `$ref: "#/$defs/rights"` | the seven `identity.RIGHTS_OPERATIONS` keys, each `enum: ["granted","denied","unknown"]` |
| `confidence` | `type: ["string","null"]`, `enum: ["high","medium","low",null]` | the adapter's own confidence in the extraction; `null` means not assessed |
| `reading_order` | array of string, `items.minLength: 1` | locator ids in document reading order |
| `locators` | array, `items.$ref: "#/$defs/locator"` | may be empty only when `unsupported` is non-empty |
| `unsupported` | array, `items.$ref: "#/$defs/unsupported_entry"` | every structure the adapter refused, by code and message |

`$defs.origin`, `additionalProperties: false`, required
`["kind","value","fetched_at","http_etag","http_last_modified","snapshot_rel_path"]`:

| Field | Type | Meaning |
|---|---|---|
| `kind` | string, `enum: ["local_file","remote_url"]` | |
| `value` | string, `minLength: 1` | the raw file's registry-relative path, or the URL |
| `fetched_at` | `type: ["string","null"]` | `null` for a local file |
| `http_etag` | `type: ["string","null"]` | captured response validator, `null` when absent |
| `http_last_modified` | `type: ["string","null"]` | captured response validator, `null` when absent |
| `snapshot_rel_path` | `type: ["string","null"]` | set when the snapshot was stored inline, `null` for reference-plus-cache and for a local file |

`$defs.rights`, `additionalProperties: false`, required exactly
`["read","quote","transform","remote_process","package","export","share"]`,
each `{"type": "string", "enum": ["granted","denied","unknown"]}`.

`$defs.unsupported_entry`, `additionalProperties: false`, required
`["code","message"]`, `code` an `enum` over `SOURCE_ADAPTER_CODES`.

`$defs.locator`, `additionalProperties: false`, required
`["id","span_id","kind","body"]`:

| Field | Type | Meaning |
|---|---|---|
| `id` | string, `minLength: 1` | the short reading-order id, reusing the existing gold vocabulary shapes `p1.0`, `p1.c1.0`, `t.r0c0`, `hdr1`, `fn1.0` |
| `span_id` | `type: ["string","null"]` | the `auditor.normalize_source` span id of the derived Markdown line this locator maps to, literally `"sp-N"`; `null` only when the locator maps to no derived line |
| `kind` | string, `enum` over `LOCATOR_KINDS` | |
| `body` | object, `oneOf` over the per-medium `$defs.body_*` | discriminated by its required `medium` const |

`LOCATOR_KINDS`, the frozen union vocabulary, reusing every `kind` string
already present in `fixtures/audit/locator_fidelity_cases.py` verbatim:

`page`, `paragraph`, `column`, `table`, `table_cell`, `heading`, `list_item`,
`header`, `footer`, `footnote`, `endnote`, `tracked_insert`, `tracked_delete`,
`comment`, `slide`, `notes`, `spine_item`, `block`, `cue`, `segment`,
`image_region`.

Per-medium bodies, each `additionalProperties: false` with a required
`medium` field carrying a `const` so the `oneOf` discriminates exactly one
branch (the hand-rolled validator matches `const` exactly, verified at
`schema_validate.py:161`):

| `$defs` name | required fields |
|---|---|
| `body_markdown` | `medium` const `"markdown"`, `line` integer minimum 1 |
| `body_pdf` | `medium` const `"pdf"`, `page` integer minimum 1, `index` integer minimum 0, `column` `["integer","null"]`, `bbox` `["array","null"]` of 4 numbers with `minItems: 4` |
| `body_docx` | `medium` const `"docx"`, `part` enum `["body","footnote","endnote","header","footer","comment"]`, `paragraph_index` integer minimum 0, `ref_id` `["string","null"]` |
| `body_pptx` | `medium` const `"pptx"`, `slide` integer minimum 1, `shape_index` integer minimum 0, `notes` boolean |
| `body_epub` | `medium` const `"epub"`, `spine_index` integer minimum 0, `spine_idref` string minLength 1, `element_index` integer minimum 0, `fragment` `["string","null"]` |
| `body_web` | `medium` const `"web"`, `css_selector` string minLength 1, `text_quote` object with required `exact`, `prefix`, `suffix` all strings |
| `body_transcript` | `medium` const `"transcript"`, `cue_index` integer minimum 0, `start_ms` integer minimum 0, `end_ms` integer minimum 0 |
| `body_ocr` | `medium` const `"ocr"`, `page` integer minimum 1, `bbox` `{"type": "null"}`, `confidence` `{"type": "null"}` |

`body_ocr.bbox` and `body_ocr.confidence` are typed `null` and nothing else, on
purpose: `scripts/ocr_lib.py` returns flat transcribed text with no coordinates
and no confidence score, so the schema itself makes a fabricated bounding box
invalid rather than trusting an adapter not to invent one. Reconsideration
condition: if the `ocr` skill ever gains a structured-output mode that measures
geometry, that is a `schema_version` bump and a recorded migration, not a
loosened type.

**The one join that makes this contract work.** `locators[].span_id` is the
span id `auditor.normalize_source(md_bytes, source_id, kind="markdown")` assigns
to the derived Markdown, which `auditor.py:118` builds as the literal string
`"sp-%d" % len(spans)`, one span per line of the decoded text. An adapter emits
its Markdown line by line and records, for each line it emits, which origin
locator produced it. It never invents a span id and never computes spans itself.
This is what keeps "exactly one parser" structurally true while adding eight
media, and it is what lets the already-shipped `auditor.citation(source_id,
fingerprint, span_id)` record resolve to a page number through the sidecar with
no change to the citation shape at all.

<tasks>

<task type="checkpoint:decision" gate="blocking">
  <name>Task 1: freeze the locator sidecar contract and the source-identity noun</name>
  <files>.planning/phases/14C-source-adapter-registry/14C-DECISIONS.md</files>
  <read_first>
- This plan's own section "The frozen sidecar contract (Task 1's recommended
  default)" in full. It is the option-a proposal.
- `.planning/phases/14C-source-adapter-registry/14C-RESEARCH.md`, Open Question
  1 in full, and the Assumptions Log rows A1 and A5. A1 is the reason this is a
  checkpoint: the exact field names are that session's synthesis, tagged
  `[ASSUMED]`, not read off an existing contract.
- `fixtures/audit/locator_fidelity_cases.py` lines 183 to 260, the first three
  PDF gold cases, for the `reading_order` id shapes this contract reuses
  verbatim rather than redesigning.
- `auditor.py` lines 89 to 160 (`_split_spans`) and 263 to 303
  (`normalize_source`, `citation`), for the `"sp-%d"` span id shape the sidecar
  joins on.
- `schemas/normalized_document.schema.json` in full, for the house schema shape
  this document copies.
- `schema_validate.py` lines 27 to 33 (the `SUPPORTED` keyword frozenset), so
  the proposed schema uses no keyword the validator refuses.
  </read_first>
  <decision>
Two things are being frozen in one answer, because they are the same decision
seen from two sides: the exact field names of `schemas/source_locator.schema.json`,
and whether "a source with an adapter and a locator sidecar" becomes the primary
source representation or is added alongside the existing Markdown-only path.
  </decision>
  <context>
This is a one-way door. Nothing consumes the sidecar today, so the cost of
changing it now is zero. The moment plan `14C-02` writes a second adapter
against it, and the moment 14B's binding half issues a citation that names a
`source_id` plus a `fingerprint` plus a `span_id`, the field names are a
published contract and changing one needs a migration of every sidecar already
written plus every citation already issued.

The second half matters just as much. itembank accepts exactly one source medium
today (`auditor.REGISTERED_ADAPTERS = ("markdown", "text")`). This phase
introduces eight. The usual correct move on a generalization is to promote the
new general representation to primary and demote the old specific one to a
variant, not to add the new one beside a still-privileged old one, because
adding alongside silently contradicts the generalized intent and leaves a second
path by which a source can reach disk.
  </context>
  <options>
    <option id="option-a">
      <name>RECOMMENDED DEFAULT: freeze the tabled contract, and promote</name>
      <pros>The envelope is exactly CONTEXT.md's own eight named fields plus
      `reading_order`, `locators`, and `unsupported`. Every locator `id` shape
      and every locator `kind` string is lifted verbatim from the gold cases
      already committed in `fixtures/audit/locator_fidelity_cases.py`, so the
      acceptance corpus and the schema cannot disagree. `span_id` joins the
      sidecar to the one parser's own span ids, so a citation record needs no
      new shape. `markdown` and `text` register as identity adapters from the
      first commit, so a hand-written Markdown file and a PDF reach disk through
      the same function and no Markdown-only side door survives.</pros>
      <cons>Registering `markdown` and `text` is a few lines of work CONTEXT.md's
      roster did not ask for. `body_ocr` typing `bbox` and `confidence` as
      strictly `null` means a future structured-OCR mode needs a schema version
      bump rather than a field loosening.</cons>
    </option>
    <option id="option-b">
      <name>Freeze the tabled contract, but add alongside</name>
      <pros>Smaller diff: no `markdown` or `text` registry entries, no
      `check_one_import_path` test. The roster is implemented exactly as
      CONTEXT.md lists it.</pros>
      <cons>Two ways for a source to reach disk: through an adapter, or the old
      way. A later phase writing a Markdown source without a sidecar produces a
      source no citation can locate, and nothing goes red. This is accepted
      debt, and what would force a later promote is the first citation that
      cannot resolve because its source has no sidecar.</cons>
    </option>
    <option id="option-c">
      <name>Defer the freeze: write sidecars with no published schema until plan 14C-08</name>
      <pros>Maximum freedom to discover field names while building the
      adapters.</pros>
      <cons>Eight adapters get written against an unpublished, drifting shape,
      and the schema is then reverse-engineered from whatever they happened to
      emit. This is the failure `schemas/` exists to prevent, and
      `schema_validate.py --all` cannot check a document that does not exist.</cons>
    </option>
  </options>
  <action>
1. Present the question above to Weibao with all three options and option-a
   named as the recommended default. Include the full field table from this
   plan's "The frozen sidecar contract" section in the question, so the answer
   is given against the actual names and not against a summary.

2. Record the verbatim answer in
   `.planning/phases/14C-source-adapter-registry/14C-DECISIONS.md` under a dated
   heading `## D-14C-1. The frozen locator sidecar contract and the source-identity noun`.
   The section records, in this order: the question as asked, the three options,
   the answer verbatim, the date, and the reconsideration condition.

3. What the executor does with each answer:
   - **option-a**: proceed to Task 2 unchanged. Task 3 builds exactly the tabled
     contract and registers `markdown`, `text`, and `pdf`.
   - **option-b**: proceed, but drop the `markdown` and `text` registry entries
     and the `check_one_import_path` assertion from Task 3, and record in
     `14C-DECISIONS.md` under a subheading `### Accepted debt` the exact sentence:
     `Two paths can create a source object. A Markdown source written without a sidecar will carry no locators and any citation into it resolves to nothing, silently. The promote is owed the first time that happens.`
   - **option-c**: STOP. Do not proceed to Task 2. Write the answer into
     `14C-DECISIONS.md`, then halt the wave and report that plans `14C-02`
     through `14C-08` need replanning, because every one of them names
     `schemas/source_locator.schema.json` in its verification.
   - **a modified option-a** (Weibao renames or adds a field): apply the rename
     everywhere in this plan's field table, record the delta in
     `14C-DECISIONS.md` as a numbered list of `old name -> new name` rows, then
     proceed. Do not carry the old name anywhere.
   - **no answer given**: the wave stops here. An unanswered checkpoint never
     gets a silent default.

4. `14C-DECISIONS.md` contains no em dash character.
  </action>
  <verify>
  <automated>test -f .planning/phases/14C-source-adapter-registry/14C-DECISIONS.md &amp;&amp; grep -c "D-14C-1" .planning/phases/14C-source-adapter-registry/14C-DECISIONS.md</automated>
Expected: the file exists and the grep count is at least 1. The degraded state
this task must prove rather than paper over is the unanswered case: with no
answer recorded, `source_adapters.py` and `schemas/source_locator.schema.json`
must not exist on disk when the wave stops.
  </verify>
  <acceptance_criteria>
- `.planning/phases/14C-source-adapter-registry/14C-DECISIONS.md` exists and
  contains the literal heading `## D-14C-1. The frozen locator sidecar contract and the source-identity noun`.
- The recorded section contains the question, all three options, the verbatim
  answer, and a dated line.
- The file contains zero em dash characters, verified by
  `python3 -c "import sys; p='.planning/phases/14C-source-adapter-registry/14C-DECISIONS.md'; sys.exit(1 if chr(8212) in open(p,encoding='utf-8').read() else 0)"` exiting 0. Note that `chr(8212)` is used rather than the literal character so this plan file stays clean under the same rule it is enforcing.
- If the answer is option-c, `source_adapters.py` does not exist on disk.
  </acceptance_criteria>
  <reversibility rating="one-way">A sidecar field name becomes published the moment a citation names a span in it; renaming later means migrating every sidecar and every citation already written.</reversibility>
  <resume-signal>Reply with option-a, option-b, option-c, or option-a plus the specific field changes you want.</resume-signal>
  <done>The sidecar contract and the source-identity noun are recorded as a dated decision, or the wave is stopped with the reason named.</done>
</task>

<task type="checkpoint:human-verify" gate="blocking-human">
  <name>Task 2: batched package-legitimacy sign-off before any pin lands</name>
  <files>deps/source-adapter-pins.txt, VENDORED.md</files>
  <read_first>
- `.planning/SUPPLY-CHAIN-POLICY.md` sections 2 and 3 in full. Section 3 is the
  adoption gate this checkpoint discharges.
- `.planning/phases/14C-source-adapter-registry/14C-RESEARCH.md`, the
  "Package Legitimacy Audit" section in full, including the note explaining the
  uniform `SUS` verdict.
- `deps/lti-pins.txt` in full. It is the exact precedent for a scoped, optional,
  pinned, checksummed, license-reviewed dependency file.
  </read_first>
  <what-built>
Nothing yet. This checkpoint runs BEFORE the first `pip install` and before
`deps/source-adapter-pins.txt` is written, because the Package Legitimacy Gate
protocol requires a human to clear a `SUS` verdict before the corresponding
install.

The research pass flagged all eight audited packages `SUS` for the single reason
`unknown-downloads`, and `pypdf` additionally for `too-new` (which reflects only
its most recent point-release date, not the project's age). Every one of the
eight resolved to its correct, long-established, canonical GitHub repository.
The research pass judged this a gap in the checker's PyPI download-statistics
source rather than a legitimacy signal. That judgement is not a substitute for
the human sign-off the protocol requires, which is what this checkpoint is.

One batched checkpoint covers the whole set, not one per package, because they
share the identical checker limitation.
  </what-built>
  <how-to-verify>
For each of the six packages this phase actually adopts, open the PyPI project
page and confirm three things by eye: the project page exists under that exact
name, the "Homepage" or "Source" link points at the repository named below, and
the license shown matches the license named below.

1. `pdfplumber` 0.11.10, MIT, https://pypi.org/project/pdfplumber/ , repo
   github.com/jsvine/pdfplumber
2. `pdfminer.six` 20260107, MIT, https://pypi.org/project/pdfminer.six/ , repo
   github.com/pdfminer/pdfminer.six
3. `python-docx` 1.2.0, MIT, https://pypi.org/project/python-docx/ , repo
   github.com/python-openxml/python-docx
4. `pypdf` 6.16.1, BSD-3-Clause, https://pypi.org/project/pypdf/ , repo
   github.com/py-pdf/pypdf
5. `python-pptx` 1.0.2, MIT, https://pypi.org/project/python-pptx/ , repo
   github.com/scanny/python-pptx
6. `readability-lxml` 0.8.4.1, Apache-2.0, https://pypi.org/project/readability-lxml/ , repo
   github.com/buriy/python-readability

Two packages are explicitly NOT being adopted and need no sign-off, but are
named here so the refusal is visible rather than silent:

- `ebooklib` 0.20 is AGPL, verified from its own PyPI license metadata. It is
  parked exactly like PyMuPDF, pending an explicit Weibao decision. Plan
  `14C-07` builds EPUB import on stdlib `zipfile` plus `xml.etree` instead.
- `trafilatura` 2.2.0 is Apache-2.0 and legitimate, but pulls six hard runtime
  dependencies against `readability-lxml`'s two to three. Not adopted on
  dependency weight, not on legitimacy.

If any package fails the eye check, say which one and stop. Do not substitute a
different library; that is a new adoption-gate decision, not an executor call.
  </how-to-verify>
  <action>
1. Present the six-package list above and wait for the sign-off.

2. On approval, run the pinned install exactly once:
   `python3 -m pip install pdfplumber==0.11.10 pdfminer.six==20260107 python-docx==1.2.0 pypdf==6.16.1 python-pptx==1.0.2 readability-lxml==0.8.4.1`
   Record the actual resolved wheel filenames and their SHA-256 hashes from the
   pip output, or by running `python3 -m pip download --no-deps <pkg>==<ver>` and
   hashing the artifact.

3. Create `deps/source-adapter-pins.txt` following `deps/lti-pins.txt`'s
   structure exactly: a header naming the phase (14C), the optional and
   degrade-never-block framing, a license review line per package with the
   reviewer name and the date, a CVE disposition line, the recorded SHA-256
   block, then one `name==version --hash=sha256:...` line per package. State in
   the header that these are OPTIONAL, that each adapter guards on its own
   import and refuses by name with the install command when absent, and that
   every non-adapter command stays byte-identical without them. State that
   PyMuPDF and ebooklib are parked on an AGPL decision and are not pinned here.

4. Create `VENDORED.md` at the repository root, which
   `SUPPLY-CHAIN-POLICY.md` section 2.2 says the first plan adding a vendored
   artifact after the policy must create. Give it a one-paragraph header naming
   the policy, then one table with the columns: artifact, pin, upstream project
   URL, release URL, SHA-256, license, reviewer, review date. Add the six rows
   from step 3. Add a final section headed `## Backfill owed` naming KaTeX and
   CodeMirror as pre-policy vendored artifacts whose rows and CI checksum step
   are owed by plan `14C-08`.

5. Neither file contains an em dash character.
  </action>
  <verify>
  <automated>python3 -c "import pdfplumber, pdfminer; print('pdf stack present')"</automated>
Expected: prints `pdf stack present` and exits 0 after the install. The degraded
state this task must also prove is the uninstalled one: `python3 -c "import
source_adapters"` must still succeed on a machine with none of the six packages
present, because every third-party import is inside an adapter function body.
That assertion belongs to Task 3 and is named here so Task 3 does not forget it.
  </verify>
  <acceptance_criteria>
- `deps/source-adapter-pins.txt` exists, contains exactly six lines matching
  `^[A-Za-z0-9._-]+==[0-9.]+ --hash=sha256:[0-9a-f]{64}$`, and contains a named
  license review line for each of the six.
- `grep -c -i -E "pymupdf|fitz|ebooklib" deps/source-adapter-pins.txt` finds
  those strings only on comment lines beginning with `#`, never on a pin line.
- `VENDORED.md` exists at the repository root with a table carrying the six rows
  and a `## Backfill owed` section naming KaTeX and CodeMirror.
- `python3 -c "import pdfplumber; print(pdfplumber.__name__)"` exits 0.
- Neither new file contains an em dash character.
  </acceptance_criteria>
  <precondition>PyPI is reachable from this machine for a one-time install. If it is not, stop and report; SUPPLY-CHAIN-POLICY.md section 2.1 forbids deferring this fetch into the running app.</precondition>
  <resume-signal>Type "approved" once the six PyPI pages check out, or name the package that failed.</resume-signal>
  <done>The six pins are reviewed by a human, installed once, and recorded in both deps/source-adapter-pins.txt and VENDORED.md.</done>
</task>

<task type="tracer" tdd="true">
  <name>Task 3: end-to-end "import one PDF as a cited source" - one path only</name>
  <files>schemas/source_locator.schema.json, source_adapters.py, journal.py, tests/source_adapters_roundtrip.py</files>
  <read_first>
- `model_adapter.py` in full, 274 lines. It is the exact structural analog:
  one typed public boundary, a dispatch registry of interchangeable backends,
  lazy per-backend imports, every failure converted to one typed result, and a
  top-level `try` and `except Exception` safety net so nothing raises. Copy
  that shape; do not invent an exception-based design.
- `identity.py` lines 32, 49 to 51, 85 to 95, 98 to 107, 138 to 155, and 158 to
  168, for `OBJECT_KINDS`, `RIGHTS_OPERATIONS`, `utc_now`, `new_object_id`,
  `object_fingerprint`, and `rights_default`.
- `journal.py` lines 214 to 227 (`_write_bytes_atomic`, the temp file plus
  flush plus fsync plus `os.replace` shape to imitate), 330 to 356
  (`commit_operation`'s full signature and docstring), 358 to 400 (the
  `discovery.inside_any_root` path-containment preflight), 432 to 450 (the
  RIGHTS-01 transform gate, which fires on `operation in ("import","copy")` and
  a non-`None` `source_object_id`), 563 to 616 (`_compute_registry`, for the
  registry row field names), and 855 to 895 (`op_link`, `_op_pull_source`,
  `op_import`).
- `auditor.py` lines 89 to 160 (`_split_spans` and the `"sp-%d"` span id) and
  263 to 303 (`normalize_source`, `MAX_SOURCE_BYTES`, the existing
  `source.oversize` code, and `citation`).
- `schema_validate.py` lines 27 to 48 (`SUPPORTED`, `ANNOTATIONS`,
  `SchemaError`) and 120 to 242 (`validate`, including the `oneOf` branch at the
  end and the list-valued `type` handling at line 146).
- `schemas/normalized_document.schema.json` in full, the house schema shape.
- `fixtures/audit/locator_fidelity_cases.py` lines 1 to 30 (the stdlib-only,
  deterministic, repository-independent contract), 55 to 130 (`pdf_pages`,
  `pdf_text_page`), and 183 to 205 plus 346 to 366 (the
  `pdf-born-digital-single-column` and `pdf-scanned-image-only` cases, which are
  the two gold cases this tracer uses).
- `tests/identity_roundtrip.py` lines 1 to 45, the bespoke roundtrip test file
  shape: shebang, docstring naming the invariant, `ROOT` and `sys.path.insert`,
  module-level `fail(msg)`, one `check_*` per concern.
- `tests/audit_coverage_roundtrip.py` lines 29 and 148 to 150, for the exact
  idiom this repository uses to import a fixture module:
  `FIXTURES = os.path.join(ROOT, "fixtures", "audit")` then
  `sys.path.insert(0, FIXTURES)` then `import locator_fidelity_cases`. Do not
  use a dotted `fixtures.audit.` import; there is no package there.
- `.planning/phases/14C-source-adapter-registry/14C-PATTERNS.md`, the sections
  headed "source_adapters.py (new module, service/dispatch)" and "The
  identity/journal integration inside source_adapters.py".
  </read_first>
  <behavior>
Write these assertions into `tests/source_adapters_roundtrip.py` first, watch
them fail, then implement until they pass. `check_thin_slice()` is the first
function in the file and the first one the `__main__` block calls.

- Test 1, `check_thin_slice`: materialize the `pdf-born-digital-single-column`
  gold case into a temporary base directory, link it with a full rights grant,
  import it through `source_adapters.import_source`, and assert all of: the
  result status is `ok`; a derived `.md` file exists whose text contains both
  `Chapter 1: Airway Management` and `The airway is the first priority.`; a
  `.locator.json` sidecar exists beside it; `schema_validate.validate(sidecar,
  loaded_schema)` returns an empty error list; the sidecar `fingerprint` equals
  the `after_fingerprint` on the one new `applied` journal entry and equals
  `journal.read_registry(base)[source_id]["fingerprint"]`; the sidecar
  `reading_order` equals `["p1.0", "p1.1"]`; and every `locators[].span_id` is a
  key of the span ids returned by `auditor.normalize_source` over the derived
  Markdown bytes.
- Test 2, `check_scanned_pdf_is_typed_unsupported`: the
  `pdf-scanned-image-only` gold case returns status `unsupported` with code
  `source.unsupported`, writes no `.md`, writes no `.locator.json`, and adds
  zero `applied` entries to the journal.
- Test 3, `check_nothing_raises`: `import_source` with an unknown adapter name
  returns `source.adapter_unknown`; with `raw_bytes=None` returns
  `source.malformed_input`; and with an adapter function monkeypatched to raise
  `ZeroDivisionError` returns `source.internal_error`. No call raises.
- Test 4, `check_rights_refusal`: a raw file linked with no rights argument
  (all seven rights default to `unknown`) refuses the import with
  `journal.rights_unknown`, leaves zero `applied` entries for the derived
  object, and leaves no orphan `.locator.json` on disk.
- Test 5, `check_no_rights_escalation`: linking a raw file with
  `transform: "denied"` and then calling `import_source` with a wire-supplied
  grant of `transform: "granted"` still refuses. The recorded row wins.
- Test 6, `check_one_import_path`: a plain UTF-8 Markdown file imported with
  `adapter="markdown"` produces a sidecar whose every locator body has
  `medium == "markdown"`, and whose `reading_order` length equals the number of
  spans `auditor.normalize_source` reports. The identity adapter is not a
  special case in the caller; it is a registry entry.
- Test 7, `check_no_second_parser`: after `import source_adapters`, the module
  has no attribute `model` and no attribute `runtime`, and its source text
  contains neither `import model` nor `import runtime`.
- Test 8, `check_degrades_without_dependencies`: with `pdfplumber` forced
  unimportable, `import_source(adapter="pdf", ...)` returns
  `source.dependency_missing` whose message contains the literal substring
  `pip install pdfplumber==0.11.10`, while `import_source(adapter="markdown",
  ...)` in the same process still returns `ok`.
- Test 9, `check_write_containment`: a `base` plus a raw file whose registry
  path would place the derived Markdown outside `base` is refused with
  `journal.path_outside_root`, and no file is written.
  </behavior>
  <action>
1. Write `schemas/source_locator.schema.json` exactly as frozen by Task 1,
   following `schemas/normalized_document.schema.json`'s shape: `$schema`,
   `$id` of `https://itembank.local/schemas/source_locator.schema.json`,
   `title`, `description`, `x-itembank-version: 1`, `type: object`,
   `additionalProperties: false`, `required`, `properties`, `$defs`. Every field
   carries a `description`. Use only keywords in `schema_validate.SUPPORTED`;
   `patternProperties`, `allOf`, `if`, and `then` are refused outright by
   `check_schema` and would fail the whole document. Nullable fields use a
   list-valued `type` such as `["string","null"]`, which `validate` handles at
   line 146. Confirm with `python3 schema_validate.py --all` exiting 0.

2. Create `source_adapters.py` at the repository root. Module docstring, written
   in the `model_adapter.py` register, states in plain sentences: one typed
   `import_source` boundary normalizes N extraction backends behind
   `ADAPTER_REGISTRY` so adding a medium is a registration and never a caller
   change; every failure converts to one typed result carrying a named
   `source.*` code before any surface, journal, or evidence call; nothing here
   raises; adapters produce sources and never import `model.py` or `runtime.py`
   (D-05); and span identity comes from `auditor.normalize_source`, never from a
   second splitter, so exactly one parser survives eight media. The docstring
   also records, in one sentence, that `source.oversized` here and
   `auditor.source.oversize` are deliberately distinct: the first is an input
   file or zip member exceeding the intake cap, the second is the derived text
   exceeding `auditor.MAX_SOURCE_BYTES`.

3. In `source_adapters.py`, define the module constants named in this plan's
   "Artifacts this phase produces" section. `SOURCE_ADAPTER_CODES` is a
   `tuple(sorted({...}))` over the twelve codes listed there, mirroring
   `model_adapter.ADAPTER_CODES` at `model_adapter.py:34`. `ADAPTER_VERSIONS`
   maps each registry key to a `"1.0.0"` string. `ADAPTER_REGISTRY` maps
   `"markdown"` to `_extract_markdown`, `"text"` to `_extract_text`, and
   `"pdf"` to `_extract_pdf`.

4. Define the extraction function contract once, in a comment above
   `ADAPTER_REGISTRY`, and hold every later adapter to it: an extraction
   function takes `(raw_bytes, options)` and returns the four-tuple
   `(markdown_text, locators, reading_order, unsupported)` where `locators` is a
   list of dicts each missing only its `span_id` (filled in by the caller after
   normalization), `reading_order` is a list of locator ids, and `unsupported`
   is a list of `{"code": ..., "message": ...}` dicts. An extraction function
   never writes a file, never mints an id, and never touches the journal.

5. Implement `_extract_markdown` and `_extract_text` as the identity adapters:
   decode the bytes as UTF-8, emit one locator per line with `kind` `"block"`
   and body `{"medium": "markdown", "line": N}` for one-based N, and set
   `reading_order` to the locator ids `"L1"`, `"L2"`, and so on. A `UnicodeDecodeError`
   returns `source.malformed_input`. These two entries are what make the
   promote real: a hand-written Markdown source reaches disk through exactly the
   same function a PDF does.

6. Implement `_extract_pdf`. Import `pdfplumber` inside the function body, never
   at module top; on `ImportError` return `source.dependency_missing` with the
   message ending in the literal `run: pip install pdfplumber==0.11.10 pdfminer.six==20260107`.
   Open the bytes with `pdfplumber.open(io.BytesIO(raw_bytes))`. Per page,
   one-based, check `page.chars` first and skip the heavy calls when it is
   empty, per RESEARCH Pitfall 5. Emit one locator per extracted line with id
   `"p%d.%d" % (page_number, index)`, `kind` `"paragraph"`, and body
   `{"medium": "pdf", "page": ..., "index": ..., "column": None, "bbox": [x0, top, x1, bottom]}`
   taken from `page.extract_words()`. Confirm the actual key names of
   `extract_words()` against the installed pdfplumber before relying on
   `x0`, `top`, `x1`, `bottom`; RESEARCH assumption A2 flags this as unverified.
   When no page yields a locator, return `unsupported` carrying
   `{"code": "source.unsupported", "message": "image-only page: no text-bearing structure"}`,
   the exact message string the gold case already records. An encrypted PDF
   returns `source.encrypted`; a truncated or unparseable PDF returns
   `source.malformed_input`. Table and column locators are out of scope for this
   plan and are added in plan `14C-02`.

7. Implement `unsupported_result(code, message, source_id)` shaped like
   `model_adapter.unavailable_result` at `model_adapter.py:58`: a dict with
   `schema_version`, `source_id`, `status`, `adapter`, `md_rel_path`,
   `sidecar_rel_path`, `journal_entry_id`, and `error` carrying `code` and
   `message`. `ok_result(...)` is the same dict shape with `status` `"ok"` and
   `error` `None`.

8. Implement `build_sidecar(...)` returning exactly the frozen envelope. It
   calls `identity.object_fingerprint(md_bytes, "source")` and
   `identity.utc_now()`; it never computes a hash any other way.

9. Implement `write_sidecar_atomic(path, sidecar)` by copying
   `journal._write_bytes_atomic`'s shape at `journal.py:214`: same-directory
   temp file, write, flush, `os.fsync`, `os.replace`. Serialize with
   `json.dumps(sidecar, ensure_ascii=False, indent=2)` plus a trailing newline,
   matching `surfaces/settings.write_settings`'s byte layout so a repeated write
   is byte-identical.

10. Implement `import_source(base, adapter, raw_object_id, actor_kind,
    actor_name, rights_grant=None, options=None)`, which is the one public
    write boundary, in exactly this order:
    a. Validate `adapter` against `ADAPTER_REGISTRY`; unknown returns
       `source.adapter_unknown`.
    b. Resolve the raw file server-side from `journal.read_registry(base)`. If
       `raw_object_id` is not a registry key, link it is NOT this function's
       job; return `source.malformed_input` naming the unknown id. The caller
       (Task 4's route and CLI) links first.
    c. Read the raw bytes; refuse over `options["max_input_bytes"]` with
       `source.oversized`.
    d. Call the extraction function. On a non-empty `unsupported` list with an
       empty `locators` list, return `unsupported_result` and write nothing.
    e. Encode the Markdown as UTF-8. Compute
       `spans = auditor.normalize_source(md_bytes, source_id, kind="markdown")["spans"]`
       and fill each locator's `span_id` from the span at the derived line it
       came from. A locator that maps to no derived line carries `span_id: None`.
    f. Mint `source_id = identity.new_object_id()` up front, so the sidecar can
       carry it before the journal entry exists.
    g. Compute `md_rel_path` deterministically as the raw file's registry path
       plus `.md`, and `sidecar_rel_path` as `md_rel_path` with `.md` replaced
       by `.locator.json`. No path ever comes from a caller.
    h. Build the sidecar, validate it with
       `schema_validate.validate(sidecar, _LOCATOR_SCHEMA)` exactly the way
       `model_adapter.py:238` validates its request, and return
       `source.internal_error` carrying the first error string if it fails.
       Never write an invalid sidecar.
    i. Write the sidecar atomically. FIRST.
    j. Call `journal.commit_operation(base, source_id, "source", md_rel_path,
       "import", md_bytes, expected_fingerprint=None, actor_kind=actor_kind,
       actor_name=actor_name, create_if_missing=True,
       source_object_id=raw_object_id)`. SECOND. Use `commit_operation`
       directly rather than `journal.op_import` for one reason only, stated in a
       comment: `op_import` mints the `object_id` itself, and the sidecar must
       carry that id before the journal call runs. The RIGHTS-01 transform gate
       lives inside `_commit_impl` and fires identically either way, verified at
       `journal.py:432-450`.
    k. On `journal.JournalError`, best-effort `os.remove` the orphan sidecar
       inside a `try` and `except OSError`, then re-raise. The refusal is the
       journal's to report by name; do not swallow it into a typed result,
       because `journal.rights_unknown` is a journal contract and not a
       `source.*` code.
    l. Wrap the whole body in the `model_adapter.invoke` safety net at
       `model_adapter.py:264`: one outer `try` and `except Exception` returning
       `source.internal_error`, with `journal.JournalError` re-raised before it
       so the rights refusal is not swallowed.

11. Implement `preview_source(base, adapter, raw_object_id, options=None)`: the
    same path through step (e), returning the extraction result and the
    would-be sidecar, and writing nothing at all. This is the free half of the
    "agent auto-fetch versus approve-before-bind" pair: search and read stay
    free in both policies, the bind step is the gated one. Task 4 wires it.

12. Add the optional `rights` parameter to `journal.op_link`. The new signature
    is `def op_link(base, kind, rel_path, actor_kind, actor_name, rights=None)`
    and the only body change is passing `rights=rights` through to
    `commit_operation`. It must default to `None` so every existing caller and
    every existing test stays byte-identical; `commit_operation` already
    defaults a `kind="source"` object with no rights to
    `identity.rights_default()`, which is what keeps unknown rights restrictive
    by construction. Extend the docstring with one sentence naming that a rights
    grant recorded at link time is the learner's declaration about a file they
    already hold, and that it is recorded once and never overwritten by a later
    link. This is the only change to `journal.py` in this entire phase.

13. Write `tests/source_adapters_roundtrip.py` in the
    `tests/identity_roundtrip.py` shape, with the nine `check_*` functions from
    the `behavior` block, `check_thin_slice` first, and a `__main__` block that
    calls each in sequence and prints one final `ok:` line naming what held.
    Every fixture materializes into a `tempfile.mkdtemp()` base and is removed
    in a `finally`. No test writes anything into the repository tree.
  </action>
  <verify>
  <automated>python3 tests/source_adapters_roundtrip.py</automated>
Expected: exit code 0 and a final line beginning `ok:`. Also run
`python3 schema_validate.py --all` (exit 0) and `python3 itembank.py guard .`
(exit 0). The degraded state this task must prove, not assume, is
`check_degrades_without_dependencies`: with `pdfplumber` unimportable, the pdf
adapter returns a typed `source.dependency_missing` naming the install command
while the markdown adapter in the same process still returns `ok`.
  </verify>
  <acceptance_criteria>
- `python3 tests/source_adapters_roundtrip.py` exits 0.
- `python3 schema_validate.py --all` exits 0 and its output includes the line
  `ok: source_locator.schema.json`.
- `python3 itembank.py guard .` exits 0.
- `grep -c "ADAPTER_REGISTRY = {" source_adapters.py` returns 1.
- `python3 -c "import source_adapters; assert sorted(source_adapters.ADAPTER_REGISTRY) == ['markdown','pdf','text']; print('registry ok')"` prints `registry ok`.
- `python3 -c "import source_adapters; assert len(source_adapters.SOURCE_ADAPTER_CODES) == 12 and source_adapters.SOURCE_ADAPTER_CODES == tuple(sorted(source_adapters.SOURCE_ADAPTER_CODES)); print('codes ok')"` prints `codes ok`.
- `python3 -c "import source_adapters as s; assert not hasattr(s,'model') and not hasattr(s,'runtime'); print('no second parser')"` prints `no second parser`.
- `python3 -c "import inspect, journal; sig=str(inspect.signature(journal.op_link)); assert sig.endswith(\"rights=None)\"), sig; print('op_link additive')"` prints `op_link additive`.
- `for t in tests/identity_roundtrip.py tests/journal_roundtrip.py tests/operations_roundtrip.py tests/audit_coverage_roundtrip.py; do python3 "$t" || exit 1; done` exits 0, proving the `op_link` change broke nothing.
- `git diff --stat runtime.py model.py` reports no change to either file.
- `source_adapters.py` and `schemas/source_locator.schema.json` contain zero em
  dash characters.
  </acceptance_criteria>
  <precondition>Task 1 recorded option-a or a modified option-a, and Task 2's install succeeded so `import pdfplumber` works. If Task 2 was declined, this task still runs but `check_thin_slice` cannot pass; stop and report rather than stubbing the PDF path.</precondition>
  <reversibility rating="costly">source_adapters.py is new code with no consumers yet, so deleting it is cheap; the sidecar files it starts writing are the costly half, which is why Task 1 gates the schema.</reversibility>
  <done>One PDF gold case is imported end to end with a schema-valid sidecar, one fingerprint, and one applied journal entry, and every failure family returns a typed code instead of raising.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 4: expose the one route, the one CLI command, and the source settings group</name>
  <files>surfaces/daemon.py, surfaces/cli.py, schemas/settings.schema.json, itembank.json, tests/daemon_roundtrip.py, tests/config_roundtrip.py</files>
  <read_first>
- `surfaces/daemon.py` lines 210 to 335 in full: the `API_ROUTES` comment
  block and tuple, `ROUTES`, `ROUTE_CLI`, and `SURFACE_PARITY`. The comment at
  lines 216 to 222 states the fixed-literal, opaque-identifier-in-the-body rule
  and names the asserted twelve-entry length.
- `surfaces/daemon.py` lines 400 to 459 (`handle_seed_accept`), the exact
  analog: same-origin gate, `api_read_json`, allowlist resolution of a
  client-supplied identifier, an allowed-fields check that 400s on an extra
  field, a loopback gate on the mutating branch, one delegated runtime call
  wrapped in `try` and `except Exception` to `send_server_error`, then
  `send_json`.
- `surfaces/daemon.py` lines 991 to 997 (`_client_is_loopback`), 1019 to 1031
  (`_same_origin`, whose docstring records that a request with no `Origin`
  header is accepted deliberately, which is the line D-02 relies on), 1034 to
  1046 (`_reject_cross_origin`), and 1047 to 1060
  (`_reject_cross_origin_write`, the combined gate for an always-mutating
  route).
- `surfaces/daemon.py` lines 2174 to 2183 (`API_FORBIDDEN_FIELDS`) and 2249 to
  2277 (`api_read_json`). Note that `out` and `bank_path` are forbidden by name;
  this route accepts no path field at all, for the same reason.
- `tests/daemon_roundtrip.py` lines 1016 to 1029 (`check_route_cli_inventory`,
  which greps `surfaces/cli.py` for `add_parser("<value>")` and is why the
  `ROUTE_CLI` value must be the single word `source`), 1090 to 1120
  (`check_api_route_scope`, whose `!= 12` must become `!= 13`), 1122 to 1157
  (`check_surface_parity`), and 2864 to 2910
  (`check_cross_origin_gate_on_mutating_routes`, whose route list this task
  extends).
- `surfaces/cli.py` lines 1050 to 1080, the `theme` parser, for the nested
  `add_subparsers(dest="action", required=True)` idiom this repository uses for
  a two-word command.
- `surfaces/settings.py` lines 118 to 195 (`defaults_from_schema`,
  `merge_over_defaults`, `load_settings`), so the new settings group's defaults
  come from the schema and a settings file without the group still reads.
- `tests/config_roundtrip.py` lines 545 to 600, the `check` settings group test,
  which is the exact pattern the new `source` group's test copies, including the
  assertion that the shipped `itembank.json` agrees with the schema defaults.
  </read_first>
  <behavior>
Write these assertions first, watch them fail, then implement.

- In `tests/daemon_roundtrip.py`, extend `check_api_route_scope` to assert
  `len(daemon.API_ROUTES) == 13` and that
  `daemon.ROUTE_CLI[("POST", "/api/source/import")] == "source"`. Update its
  failure message to name the new route so a future reader knows what the
  thirteenth is.
- Add `check_api_source_import_route`: a `POST` to `api/source/import` carrying
  an `Origin` header of `http://evil.example` returns 403 and writes nothing; a
  body carrying an unknown field returns 400 naming that field; a body whose
  `adapter` is not a key of `source_adapters.ADAPTER_REGISTRY` returns 400; a
  body carrying a `path` or `out` field returns 400.
- Extend `check_cross_origin_gate_on_mutating_routes`'s `routes` tuple with
  `(url + "api/source/import", {"adapter": "markdown", "source_object_id": "0"*16})`.
- In `tests/config_roundtrip.py`, add `check_source_settings_group` mirroring
  the existing `check` group test: the schema declares `source` as a top-level
  required key; its `required` list is exactly the six field names sorted; the
  shipped `itembank.json` `source` object equals the schema's computed default;
  `config set source.bind_policy auto_fetch` round-trips; `config set
  source.bind_policy sometimes` is rejected with `settings.invalid_value`;
  `config set source.fetch_timeout_seconds 0` is rejected with
  `settings.out_of_range`; and a settings file with no `source` key at all
  reads back with all six defaults present.
- In `tests/source_adapters_roundtrip.py`, add `check_cli_and_route_parity`:
  importing the same Markdown fixture once through `itembank source import` and
  once through a `POST /api/source/import` against two separate temporary bases
  produces sidecars that are byte-identical after the `source_id`,
  `captured_at`, and `fingerprint` fields are removed, proving both surfaces
  reach the same function rather than two implementations.
  </behavior>
  <action>
1. Add the `source` settings group to `schemas/settings.schema.json`: a new
   top-level `source` object with `additionalProperties: false`,
   `x-itembank-phase: 14`, a `default` object carrying all six values, and
   `required` listing all six. Add the string `"source"` to the document's own
   top-level `required` array. The six fields, with their exact types, ranges,
   defaults, and descriptions:
   - `bind_policy`, string, `enum: ["approve_before_bind", "auto_fetch"]`,
     default `"approve_before_bind"`. Description: which policy governs the
     bind step when an agent actor requests an import. Searching and reading a
     source are free under both policies; only the write is gated. Under
     `approve_before_bind`, an `actor_kind` of `agent` must supply
     `confirm: true` or the import is refused by name with
     `source.approval_required`.
   - `snapshot_storage`, string, `enum: ["auto", "inline", "reference"]`,
     default `"auto"`. Description: whether a captured remote snapshot is copied
     inline beside the course or cached with a reference. `auto` picks inline
     under `snapshot_inline_max_bytes` and reference above it. The fingerprint
     is the same either way, so a citation never notices which was used. Read by
     plan `14C-04`.
   - `snapshot_inline_max_bytes`, integer, minimum 0, maximum 268435456,
     default 8388608.
   - `allow_private_origins`, boolean, default `false`. Description: whether the
     web-capture adapter may fetch a URL whose host resolves to a loopback,
     private, or link-local address. Default deny.
   - `fetch_timeout_seconds`, integer, minimum 1, maximum 120, default 15.
   - `max_input_bytes`, integer, minimum 1, maximum 2147483648, default
     209715200. Description: the largest single input file or zip member an
     adapter will read before refusing with `source.oversized`.

2. Add the same six-key `source` object, with the identical default values, to
   the shipped `itembank.json`, preserving that file's existing
   `json.dump(..., ensure_ascii=False, indent=2)` layout and trailing newline.
   `tests/config_roundtrip.py` asserts the shipped file agrees with the schema's
   computed defaults, so a mismatch is a red test, not a silent drift.

3. In `surfaces/daemon.py`, add
   `SOURCE_IMPORT_ALLOWED_FIELDS = ("adapter", "source_object_id", "url",
   "rights_grant", "snapshot_storage", "preview", "confirm")` beside the
   existing `SEED_ACCEPT_ALLOWED_FIELDS` at line 208.

4. Add `handle_api_source_import(handler)` modeled line for line on
   `handle_seed_accept`, in this order:
   a. `if _reject_cross_origin_write(handler): return`. Use this single combined
      helper rather than `_same_origin` plus `_client_is_loopback` separately,
      because unlike `/seed/accept` this route always mutates; there is no
      read-only branch to leave ungated.
   b. `data, failed = api_read_json(handler)`; return on `failed`. This already
      rejects `out`, `bank_path`, and the other `API_FORBIDDEN_FIELDS` by name.
   c. Reject any field not in `SOURCE_IMPORT_ALLOWED_FIELDS` with a 400 whose
      message is exactly
      `"field %r is not accepted by /api/source/import; only adapter, source_object_id, url, rights_grant, snapshot_storage, preview, and confirm are read" % extra[0]`,
      mirroring the `/seed/accept` message shape at line 428.
   d. Reject an `adapter` that is not a string key of
      `source_adapters.ADAPTER_REGISTRY` with a 400 whose message is exactly
      `"adapter must be one of %s" % ", ".join(sorted(source_adapters.ADAPTER_REGISTRY))`.
      Resolve it through the registry the same way `bank` is resolved through
      `handler.banks`: never joined to a path, never normalized, because it is
      never treated as a path.
   e. When `preview` is exactly the boolean `True`, call
      `source_adapters.preview_source(...)` and `send_json` the result. Nothing
      is written; this is the free read half of the bind policy pair.
   f. Otherwise call `source_adapters.import_source(...)` with `actor_kind` of
      `"agent"` (an HTTP client is not a human at a terminal) and `actor_name`
      of `"daemon"`, inside `try` and `except Exception as exc:
      handler.send_server_error(exc); return`, then `handler.send_json(result)`.
   g. Add a docstring stating in plain sentences: the body carries an `adapter`
      name and an opaque `source_object_id`, never a filesystem path (T-2-01);
      the raw file is resolved server-side from the daemon's own journal
      registry so a client can never assert a fingerprint or a rights record it
      does not own; and extracted Markdown from a learner-supplied or fetched
      file is data returned to the caller, never instructions the daemon or a
      downstream agent acts on.

5. Add exactly one row to each of the three tables:
   - `API_ROUTES`: `("POST", "/api/source/import", "handle_api_source_import")`
     as the thirteenth entry.
   - `ROUTE_CLI`: `("POST", "/api/source/import"): "source"`. The value is the
     single word `source`, not `"source import"`, because
     `check_route_cli_inventory` greps `surfaces/cli.py` for
     `add_parser("<value>")`. The existing
     `("POST", "/api/lesson/run"): "lesson"` row is the precedent.
   - `SURFACE_PARITY`: `(("POST", "/api/source/import"), "source", "source_import")`.
   Update the `API_ROUTES` comment block at lines 210 to 222 so it says thirteen
   rather than twelve and names the new route and its phase.

6. In `surfaces/cli.py`, add `cmd_source(a)` and register the parser:
   `s = sub.add_parser("source", help="import a book, document, page, or transcript as a cited source")`
   then `t = s.add_subparsers(dest="action", required=True)` then
   `ti = t.add_parser("import", help="extract one source file into Markdown plus a locator sidecar")`.
   Arguments on `import`: `--base` defaulting to `"."`, `--file` (a path to the
   raw file, accepted here because the CLI is not a network boundary),
   `--adapter` (required, choices from `sorted(source_adapters.ADAPTER_REGISTRY)`),
   `--grant` (a comma-separated subset of `identity.RIGHTS_OPERATIONS`, applied
   only when the raw file is being linked for the first time),
   `--preview` (a `store_true` that extracts and prints without writing), and
   `--json` (a `store_true` emitting the result dict). `cmd_source` resolves
   `--file` to a path relative to `--base`, calls
   `journal.op_link(base, "source", rel_path, "human", "cli", rights=<parsed grant>)`
   when that path is not already a registry row, then calls
   `source_adapters.import_source(...)` with `actor_kind` of `"human"` and
   `actor_name` of `"cli"`. On a typed unsupported result, print the code and
   message and `sys.exit(1)`. On a `journal.JournalError`, print
   `"%s: %s" % (exc.code, exc)` and `sys.exit(1)`, following the
   `sys.exit`-with-a-human-readable-message convention the other `cmd_*`
   handlers use.

7. Update `tests/daemon_roundtrip.py` per the `behavior` block: bump the
   `check_api_route_scope` length assertion from 12 to 13 and its message, add
   `check_api_source_import_route` to the file and to the `checks` tuple in
   `main`, and extend `check_cross_origin_gate_on_mutating_routes`'s `routes`
   tuple. Do not touch any other assertion in that file.

8. Update `tests/config_roundtrip.py` with `check_source_settings_group` and
   register it in that file's own check list.

9. Add `check_cli_and_route_parity` to `tests/source_adapters_roundtrip.py`.
  </action>
  <verify>
  <automated>python3 tests/daemon_roundtrip.py &amp;&amp; python3 tests/config_roundtrip.py &amp;&amp; python3 tests/source_adapters_roundtrip.py</automated>
Expected: all three exit 0. The degraded state this task must prove is the
authority gate: a cross-origin POST to `api/source/import` returns 403 and
leaves the journal, the derived Markdown, and the sidecar untouched, asserted
inside `check_cross_origin_gate_on_mutating_routes` by the same
before-and-after byte comparison it already runs on the plan file and the daily
log.
  </verify>
  <acceptance_criteria>
- `python3 -c "import sys; sys.path.insert(0,'surfaces'); import daemon; assert len(daemon.API_ROUTES)==13; assert ('POST','/api/source/import','handle_api_source_import') in daemon.API_ROUTES; assert daemon.ROUTE_CLI[('POST','/api/source/import')]=='source'; assert (('POST','/api/source/import'),'source','source_import') in daemon.SURFACE_PARITY; print('route registered')"` prints `route registered`.
- `python3 tests/daemon_roundtrip.py` exits 0.
- `python3 tests/config_roundtrip.py` exits 0.
- `python3 tests/source_adapters_roundtrip.py` exits 0.
- `python3 itembank.py source import --help` exits 0 and its output contains the
  strings `--adapter` and `--preview`.
- `python3 -c "import json; d=json.load(open('itembank.json')); assert sorted(d['source'])==['allow_private_origins','bind_policy','fetch_timeout_seconds','max_input_bytes','snapshot_inline_max_bytes','snapshot_storage']; assert d['source']['bind_policy']=='approve_before_bind'; print('settings ok')"` prints `settings ok`.
- `python3 schema_validate.py --all` exits 0.
- `for t in tests/*.py; do python3 "$t" || exit 1; done` exits 0.
- `python3 itembank.py guard .` exits 0.
- No file changed by this task contains an em dash character.
  </acceptance_criteria>
  <precondition>Task 3 landed `source_adapters.py` with `ADAPTER_REGISTRY`, `import_source`, and `preview_source`, because both new surfaces import it at module scope.</precondition>
  <reversibility rating="one-way">A published route literal and a published CLI command name become a contract for any external harness, including a Cordis-based one, the moment either is used. The names are chosen once here and not renamed later in this phase.</reversibility>
  <done>POST /api/source/import and itembank source import both reach source_adapters.import_source, both are authority-gated, the three parity tables agree, and the source settings group ships with its defaults.</done>
</task>

</tasks>

<threat_model>
ASVS level 1. Block on `high`.

## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| HTTP client to daemon | An untrusted JSON body reaches `handle_api_source_import`. The client may be a browser page, a curl-style CLI, or an external agent harness. |
| Learner-supplied file bytes to adapter | Arbitrary PDF, DOCX, PPTX, EPUB, or transcript bytes reach a third-party parser inside itembank's own process. |
| Adapter output to downstream agent | Extracted Markdown from an untrusted document becomes context a model later reads. |
| Adapter to durable disk | The derived Markdown, the sidecar, and the journal entry are written under an approved root. |
| pip registry to developer machine | Six new third-party packages enter the build. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-14C-01 | Elevation of Privilege | `handle_api_source_import` | high | mitigate | `_reject_cross_origin_write` is the first statement in the handler, so a cross-origin or non-loopback client is refused with 403 before extraction, before any file write, and before any journal append. Asserted by `check_cross_origin_gate_on_mutating_routes` with a before-and-after byte comparison. |
| T-14C-02 | Tampering | route body field handling | high | mitigate | The route accepts no filesystem path at all. `api_read_json` already rejects `out` and `bank_path` by name; `SOURCE_IMPORT_ALLOWED_FIELDS` rejects every other unexpected field with a 400. The raw file is resolved server-side from the journal registry by opaque `object_id`. |
| T-14C-03 | Spoofing | rights record on the wire | high | mitigate | A `rights_grant` in the body applies only when the raw file is being linked for the first time and never overwrites an existing registry row. `journal._commit_impl` reads the rights value from the registry inside its own held lock, never from the caller, verified at `journal.py:432-450`. Asserted by `check_no_rights_escalation`. |
| T-14C-04 | Tampering | derived output path | high | mitigate | `md_rel_path` and `sidecar_rel_path` are computed from the raw file's registry path, never from a caller. `journal.commit_operation`'s `discovery.inside_any_root` preflight refuses a base-escaping path with `journal.path_outside_root` before the lock, verified at `journal.py:383-387`. Asserted by `check_write_containment`. The sidecar write is the one durable write that does not pass through `commit_operation`, so `write_sidecar_atomic` performs the same containment check itself before opening the temp file. |
| T-14C-05 | Denial of Service | `_extract_pdf` on a hostile PDF | medium | mitigate | `options["max_input_bytes"]` caps the input at the `source.max_input_bytes` setting (200 MiB default) before the parser sees it; `page.chars` is checked before the heavy `extract_words` call so a scanned or empty page short-circuits. Zip and XML hardening for the container formats is plan `14C-02`'s task and is named there. |
| T-14C-06 | Tampering | extracted content read as instructions | medium | mitigate | The route docstring and the module docstring both state that extracted Markdown is data returned to the caller and never an instruction the daemon or a downstream agent acts on. The daemon performs no action derived from extracted text; it serializes the result and returns it. No prompt, no tool call, and no shell command is constructed from adapter output anywhere in this phase. |
| T-14C-07 | Repudiation | a half-written pair after a crash | medium | mitigate | The sidecar is written first and the journal entry second, so a fault leaves either the prior valid state or an orphan sidecar with no journal entry, which is cheap and self-evidently repairable. The reverse order could leave an applied source object with no locators, which nothing can detect. Fault injection for this ordering is plan `14C-02`'s `tests/file_fault_tracer.py` extension. |
| T-14C-08 | Information Disclosure | derived Markdown leaving disk | low | accept | Nothing in this phase transmits extracted text. The already-accepted risk that a hosted model may later see item text is recorded in `.claude/CLAUDE.md` and is unchanged by this phase. |
| T-14C-SC | Tampering | npm/pip/cargo installs | high | mitigate | Task 2 is a blocking human checkpoint against `SUPPLY-CHAIN-POLICY.md` section 3 covering all six adopted packages, run before the first `pip install`. Pins are exact with recorded SHA-256 hashes in `deps/source-adapter-pins.txt` and rows in `VENDORED.md`. Two packages are refused by name: `ebooklib` on AGPL, `trafilatura` on dependency weight. This checkpoint is never auto-approvable. |
</threat_model>

<out_of_scope>
This plan refuses these adjacent temptations by name, so scope is enforced here
and not by executor judgment.

- **Any other adapter.** Only `markdown`, `text`, and `pdf` are registered. DOCX
  is plan `14C-02`, PPTX is `14C-03`, web is `14C-04`, transcript is `14C-05`,
  OCR is `14C-06`, EPUB is `14C-07`, ASR is `14C-08`.
- **PDF table and column locators.** `_extract_pdf` emits paragraph locators
  only. `table`, `table_cell`, and `column` are in `LOCATOR_KINDS` because the
  vocabulary is frozen once, but plan `14C-02` is what makes the PDF adapter
  emit them.
- **The remote fetch.** The sidecar's `origin` fields for a remote capture are
  frozen here so no schema change is needed later, but no URL is fetched in this
  plan and `POST /api/source/recheck` does not exist yet.
- **Changing `auditor.REGISTERED_ADAPTERS`.** It stays `("markdown", "text")`.
  `auditor.normalize_source` normalizes decoded text into spans; it is not and
  does not become a medium registry. `kind="pdf"` continues to raise
  `source.adapter_unregistered`, which is correct, and
  `tests/audit_coverage_roundtrip.py`'s existing eighteen-case gate is not
  touched by this plan.
- **Any change to `runtime.py`, `model.py`, `evidence.py`, or `selection.py`.**
  D-05. `git diff --stat` on those files must report nothing.
- **A second atomic-write helper for the Markdown half.** The Markdown goes
  through `journal.commit_operation` and nothing else. Only the sidecar, which
  is not a 14A object, gets its own atomic writer.
- **A CI checksum verifier for `VENDORED.md`.** Owed by plan `14C-08` along with
  the KaTeX and CodeMirror backfill; creating the file is this plan's share.
- **Any 14B binding work.** This plan produces a `source` object. Binding it to
  an objective is 14B's half and is not touched here.
</out_of_scope>

<verification>
Run in this order after every task:

1. `python3 tests/source_adapters_roundtrip.py` (exit 0)
2. `python3 schema_validate.py --all` (exit 0)
3. `python3 tests/daemon_roundtrip.py` (exit 0)
4. `python3 tests/config_roundtrip.py` (exit 0)
5. `for t in tests/*.py; do python3 "$t" || exit 1; done` (exit 0)
6. `python3 itembank.py guard .` (exit 0)
7. `git diff --stat runtime.py model.py` (no output)
</verification>

<success_criteria>
- Every `must_haves.truths` line is asserted by a named `check_*` function in
  `tests/source_adapters_roundtrip.py`, `tests/daemon_roundtrip.py`, or
  `tests/config_roundtrip.py`.
- The full suite is green and `itembank guard .` is clean.
- `14C-DECISIONS.md` records D-14C-1 with a verbatim answer and a date.
- `VENDORED.md` and `deps/source-adapter-pins.txt` exist with six reviewed rows.
- Zero em dash characters in any file this plan created or changed.
</success_criteria>

<summary_obligations>
`.planning/phases/14C-source-adapter-registry/14C-01-SUMMARY.md` records:

- The verbatim answer to the Task 1 checkpoint and any field renames applied.
- The Task 2 sign-off outcome, the six resolved wheel filenames, and their
  SHA-256 hashes.
- The actual `pdfplumber.Page.extract_words()` key names observed, since
  RESEARCH assumption A2 flagged them unverified. If they differ from `x0`,
  `top`, `x1`, `bottom`, record the real names so plans 02 through 08 do not
  repeat the discovery.
- Which truth was verified by which command, one line each.
- Any deviation from this plan, with the reason.
- The evidence pointer for each: the test file and the `check_*` function name.
</summary_obligations>

<output>
Create `.planning/phases/14C-source-adapter-registry/14C-01-SUMMARY.md` when done.
</output>
