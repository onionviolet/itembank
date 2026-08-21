# Phase 14C: Source Adapter Registry - Pattern Map

**Mapped:** 2026-08-21
**Files analyzed:** 11 (new) + 3 (modified)
**Analogs found:** 11 / 11

RESEARCH.md for this phase already did a full, line-cited read of every
analog file. This document re-verifies the load-bearing excerpts against the
actual files on disk (all confirmed accurate) and packages them for the
planner/executor. Where RESEARCH.md's own code is illustrative synthesis
(`[ASSUMED]`), that is preserved here, not upgraded to fact.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `source_adapters.py` (new) | service (dispatch registry) | transform (bytes -> Markdown+sidecar) | `model_adapter.py` | exact (same "one typed boundary, registry of transports, nothing raises" shape) |
| `source_adapters.py`'s per-format extract functions | utility | transform | `fixtures/audit/locator_fidelity_cases.py`'s own gold shapes (consumer side) + `journal.py:875-905` (producer side) | role-match |
| `surfaces/daemon.py` additions (`POST /api/source/import` route + handler) | route/controller | request-response, mutating write | `handle_seed_accept` (`daemon.py:400-459`) | exact |
| `surfaces/cli.py` addition (`itembank source import`) | route (CLI) | request-response | existing `cmd_*` pattern (see Shared Patterns) | role-match |
| `schemas/source_locator.schema.json` (new) | config (schema) | n/a | `schemas/normalized_document.schema.json` | exact |
| `tests/source_adapters_roundtrip.py` (new) | test | batch | `tests/identity_roundtrip.py`, `tests/journal_roundtrip.py` | exact |
| `fixtures/audit/pptx_fidelity_cases.py` (new) | test fixture | batch | `fixtures/audit/locator_fidelity_cases.py` | exact |
| `fixtures/audit/epub_fidelity_cases.py` (new) | test fixture | batch | `fixtures/audit/locator_fidelity_cases.py` | exact |
| `fixtures/audit/web_capture_fidelity_cases.py` (new) | test fixture | batch | `fixtures/audit/locator_fidelity_cases.py` | exact |
| `fixtures/audit/transcript_fidelity_cases.py` (new) | test fixture | batch | `fixtures/audit/locator_fidelity_cases.py` | exact |
| `requirements.txt` (modified) | config | n/a | itself (existing pin block shape) | exact |
| `deps/lti-pins.txt` (modified, or new `deps/source-adapter-pins.txt`) | config | n/a | `deps/lti-pins.txt` | exact |
| OCR adapter function inside `source_adapters.py` | utility (wrapper) | transform | `scripts/ocr_lib.py` (WRAP, do not reimplement) | exact |

## Pattern Assignments

### `source_adapters.py` (new module, service/dispatch)

**Analog:** `model_adapter.py` (whole file, 274 lines, read in full this session)

**Why this is the right analog, not `journal.py` alone:** `model_adapter.py`
is this codebase's own existing "vendor-neutral registry of interchangeable
backends behind one typed call, nothing raises, every failure converts to a
typed result" pattern. `source_adapters.py` should look like its sibling: a
dispatch table keyed by adapter name, one `invoke`-shaped public function,
lazy imports per backend, and a typed failure envelope — never a bespoke
exception-based design.

**Module docstring pattern** (`model_adapter.py:1-16`):
```python
#!/usr/bin/env python3
"""The model-adapter boundary (Phase 8, plan 08-02).

One typed invoke(request, settings) boundary normalizes any number of
provider transports behind TRANSPORT_REGISTRY, so switching providers is a
settings change, never a caller change (D-01, D-02, MODEL-02). Every failure
-- disabled profile, missing executable, nonzero exit, timeout, HTTP/URL
error, malformed JSON, oversized output, provider refusal, an invalid request
-- converts to one typed unavailable result with a named adapter.* code
before any surface or evidence call (D-04, MODEL-03). Nothing here raises.

Transports are stdlib subprocess and urllib only -- no provider SDK, no
runtime dependency (AI-SPEC section 2).
"""
```
Copy this shape for `source_adapters.py`'s own docstring: "One typed
`import_source(adapter_name, ...)` boundary normalizes N extraction
backends behind `ADAPTER_REGISTRY`... every failure converts to one typed
`unsupported` result with a named `source.*` reason code... adapters never
touch `runtime.py` or `model.py` (D-05)."

**Registry + typed-failure-code pattern** (`model_adapter.py:34-41`, `58-70`, `227-230`):
```python
ADAPTER_CODES = tuple(sorted({
    "adapter.executable_missing", "adapter.http_error", "adapter.internal_error",
    "adapter.malformed_response", "adapter.output_cap_exceeded",
    "adapter.profile_disabled", "adapter.profile_invalid",
    "adapter.profile_unknown", "adapter.provider_refused",
    "adapter.request_invalid", "adapter.subprocess_error", "adapter.timeout",
    "adapter.transport_unknown", "adapter.unreachable",
}))

def unavailable_result(code, message, interaction_id):
    return {
        "schema_version": 1,
        "interaction_id": interaction_id,
        "status": "unavailable",
        "candidate": None,
        "provider": None,
        "elapsed_ms": None,
        "error": {"code": code, "message": message},
    }

TRANSPORT_REGISTRY = {
    "hosted_cli": _transport_hosted_cli,
    "openai_compatible": _transport_openai_compatible,
}
```
Mirror exactly: `SOURCE_ADAPTER_CODES = tuple(sorted({...}))` with
`"source.dependency_missing"`, `"source.unsupported"`, `"source.oversized"`,
`"source.fetch_failed"`, `"source.malformed_input"`, etc. (CONTEXT.md's own
"never a silent empty extraction... typed reason code" language), an
`unsupported_result(code, message, source_id)` builder shaped like
`unavailable_result`, and `ADAPTER_REGISTRY = {"pdf": _extract_pdf, "docx":
_extract_docx, "pptx": _extract_pptx, "epub": _extract_epub, "web":
_extract_web, "transcript": _extract_transcript, "ocr": _extract_ocr}`.

**"Nothing raises" top-level wrapper pattern** (`model_adapter.py:264-274`):
```python
def invoke(request, settings):
    """The single public boundary (D-01/D-02). Every failure family converts
    to one typed unavailable result; no exception escapes."""
    try:
        return _invoke(request, settings)
    except Exception:  # last-resort safety net, never a traceback
        interaction_id = request.get("interaction_id") \
            if isinstance(request, dict) else None
        return unavailable_result("adapter.internal_error",
                                  "unexpected adapter failure", interaction_id)
```
Copy this exact shape for `source_adapters.py`'s public `import_source(...)`
entry point.

**Lazy per-backend import pattern (RESEARCH.md Open Question 5, `[ASSUMED]` but directly actionable):**
```python
def _extract_pdf(raw_bytes):
    try:
        import pdfplumber
    except ImportError:
        return None, [], "source.dependency_missing", (
            "pdfplumber is not installed; run "
            "`pip install pdfplumber==0.11.10 pdfminer.six==20260107`")
    ...
```
Every adapter function imports its own third-party library inside the
function body, never at module top — one missing dependency degrades only
that adapter (mirrors `_transport_openai_compatible`'s and
`_transport_hosted_cli`'s per-transport isolation in `model_adapter.py`).

---

### The identity/journal integration inside `source_adapters.py`

**Analogs:** `identity.py` (whole file, 347 lines) and `journal.py:855-934`
(`op_link`, `op_import`, `op_copy`, `op_move` — all read and verified this
session).

**Verified exact signatures** (do not guess these):
```python
# identity.py:32
OBJECT_KINDS = ("course", "objective", "source", "lesson", "bank", "component")

# identity.py:98-107
def new_object_id():
    """A durable opaque id ... uuid4().hex[:16] ...
    An id is minted once and is never derived from content, a path, or a
    display name (D-14A-2)."""
    return uuid.uuid4().hex[:16]

# identity.py:138-155
def object_fingerprint(raw, kind):
    if kind not in OBJECT_KINDS:
        raise _unknown_kind_error(kind)
    normalized = normalize_for_fingerprint(raw, kind)
    return "sha256:" + hashlib.sha256(normalized).hexdigest()

# identity.py:85-95
def utc_now():
    now = datetime.datetime.now(datetime.timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:%S.") + "%03dZ" % (now.microsecond // 1000)
```
Call these exactly: `identity.object_fingerprint(md_bytes, "source")`,
`identity.new_object_id()`, `identity.utc_now()`. **`"source"` is the only
`OBJECT_KINDS` member this phase may ever pass** — CONTEXT.md's own contract
line says so, and `14A-FREEZE.md` treats adding a kind as a one-way door.
Never invent an `"artifact"` or `"snapshot"` kind for the sidecar.

**`op_link` — mint an id for a raw local file already on disk, no bytes copied** (`journal.py:855-872`, verified verbatim):
```python
def op_link(base, kind, rel_path, actor_kind, actor_name):
    """Mint a new id for a file that stays where it lives. The bytes are
    never written by this operation... Binding a file this way records no
    source rights obligation, because nothing is copied out of the file's
    owner's control."""
    target_path = os.path.join(os.path.abspath(base), rel_path)
    raw = None
    if os.path.exists(target_path):
        with open(target_path, "rb") as fh:
            raw = fh.read()
    object_id = identity.new_object_id()
    return commit_operation(
        base, object_id, kind, rel_path, "link", raw,
        expected_fingerprint=None, actor_kind=actor_kind,
        actor_name=actor_name, create_if_missing=False,
        write_target=False)
```

**`op_import` — mint an id for a NEW derived artifact pulled from a source, rights-gated** (`journal.py:885-893`, verified verbatim):
```python
def op_import(base, source_object_id, kind, rel_path, raw, actor_kind,
              actor_name):
    """Mint a new id for a new owned artifact pulled from `source_object_id`;
    records `source_object_id` and `source_revision` on the entry. Requires
    the source's `transform` right to be exactly `"granted"`
    (RIGHTS-01); refuses with `journal.rights_unknown` before any mutation
    otherwise. The source object's own registry row is never touched."""
    return _op_pull_source(base, "import", source_object_id, kind, rel_path,
                            raw, actor_kind, actor_name)
```
Exact call shape for a local-file adapter (PDF/DOCX/PPTX/EPUB/transcript
already on disk): first `journal.op_link(base, "source", raw_rel_path,
actor_kind, actor_name)` if the raw file is not already a registry row (a
no-op skip if 14B's binding already linked it), then
`journal.op_import(base, raw_file_object_id, "source", md_rel_path,
md_bytes, actor_kind, actor_name)` for the derived Markdown. This
automatically enforces RIGHTS-01 — no new rights code needed in
`source_adapters.py`.

For a remote capture (web/video/audio) with no pre-existing local raw file,
pass `source_object_id=None` so `commit_operation` defaults to
`identity.rights_default()` (all `"unknown"`), keeping "unknown rights stay
restrictive" true by construction.

**Ordering rule (anti-pattern to avoid):** write the `.locator.json` sidecar
to disk FIRST (atomic temp+replace, see `journal.py:214`
`_write_bytes_atomic` for the exact atomic-write shape to imitate), THEN
call `journal.op_import`/`commit_operation` for the Markdown SECOND. If the
journal call raises `journal.JournalError` (e.g. `rights_unknown`), best-effort
`os.remove()` the orphan sidecar. This ordering is spelled out in
RESEARCH.md's Pattern 1 code block and its own Anti-Patterns section
("Writing the Markdown through `journal.commit_operation` before the
sidecar exists on disk").

---

### `surfaces/daemon.py` — `POST /api/source/import` route

**Analog:** `handle_seed_accept` (`daemon.py:400-459`, verified verbatim —
the only existing mutating route with the exact "same-origin gate, then a
loopback gate on the actually-destructive branch, then delegate to one
runtime function, catch-all `except Exception` around the call, `send_json`
the result" shape this new route needs).

**Full analog function, quoted exactly** (`daemon.py:400-459`):
```python
def handle_seed_accept(handler):
    """`POST /seed/accept` -- the daemon half of the one accept endpoint..."""
    if not _same_origin(handler):
        handler.send_error(403, "cross-origin seed request refused")
        return
    data, failed = api_read_json(handler)
    if failed:
        return
    bank = data.get("bank")
    if not isinstance(bank, str) or bank not in handler.banks:
        handler.send_not_found(bank)
        return
    extra = sorted(k for k in data if k not in SEED_ACCEPT_ALLOWED_FIELDS)
    if extra:
        handler.send_error(
            400, "field %r is not accepted by /seed/accept; only bank, action, "
            "and draft are read" % extra[0])
        return
    action = data.get("action")
    if action not in ("accept", "skip", "cancel"):
        handler.send_error(400, "action must be one of accept|skip|cancel")
        return
    if action == "accept":
        if not _client_is_loopback(handler):
            handler.send_error(403, "seed accept requires a loopback client")
            return
        draft = data.get("draft")
        if not isinstance(draft, dict):
            handler.send_error(400, "accept requires a draft item object")
            return
        try:
            result = seeding.accept_candidate(handler.banks[bank], draft)
        except Exception as exc:                # never let a bad POST kill the daemon
            handler.send_server_error(exc)
            return
        handler.send_json(result)
        return
    ...
```

Copy this exactly for `handle_api_source_import(handler)`: `_same_origin`
gate first, `api_read_json` to parse the body, validate an `adapter` field
against `source_adapters.ADAPTER_REGISTRY` keys (reject unknown adapter
names the same way `bank not in handler.banks` is checked), require
`_client_is_loopback(handler)` before the actual write (this route always
mutates, so the loopback check is unconditional, not action-gated like
seed's accept/skip/cancel split), wrap the `source_adapters.import_source(...)`
call in `try/except Exception: handler.send_server_error(exc)`, then
`handler.send_json(result)`.

**Table registration — three tables, all three must gain exactly one entry each** (`daemon.py:223-236` `API_ROUTES`, verified verbatim):
```python
API_ROUTES = (
    ("POST", "/api/start", "handle_api_start"),
    ("POST", "/api/next", "handle_api_next"),
    ...
    ("POST", "/api/lesson/run", "handle_api_lesson_run"),
)
```
Add `("POST", "/api/source/import", "handle_api_source_import")` as the
13th entry. This is asserted-length-checked: `daemon.py:220-222`'s own
comment says "The twelve-entry length is asserted by `check_api_route_scope`
in `tests/daemon_roundtrip.py`" — that assertion must be bumped to 13 in
the same change (see Test pattern below).

`ROUTE_CLI` (`daemon.py:277-313`, verified verbatim, dict keyed by
`(method, pattern)`): add `("POST", "/api/source/import"): "source import"`.

`SURFACE_PARITY` (`daemon.py:322-...`, tuple of `(route, CLI command,
reserved MCP tool name)`): add
`(("POST", "/api/source/import"), "source import", "source_import")`.

**Authority gate — use `_reject_cross_origin_write`, not a hand-rolled check** (`daemon.py:1047-1060`, verified verbatim):
```python
def _reject_cross_origin_write(handler):
    """The full authority gate for a mutating route, mirroring
    handle_theme_post: same-origin when an Origin is present plus a
    loopback client."""
    if _reject_cross_origin(handler):
        return True
    if not _client_is_loopback(handler):
        handler.send_error(403, "day write requires a loopback client")
        return True
    return False
```
Since `/api/source/import` is *always* a write (unlike `/seed/accept`'s
accept/skip/cancel split), prefer calling this single combined helper at
the top of the handler over reimplementing `_same_origin` +
`_client_is_loopback` separately — it is the more direct match for "this
route only ever mutates."

**`_client_is_loopback`** (`daemon.py:991-997`, verified verbatim):
```python
def _client_is_loopback(handler):
    """True when the request's remote address is loopback..."""
    return handler.client_address[0] in ("127.0.0.1", "::1")
```

**The "no Origin header is accepted" rule CONTEXT.md cites** (`daemon.py:1019-1031`, verified verbatim, confirms the line-1022 claim in CONTEXT.md/RESEARCH.md is accurate):
```python
def _same_origin(handler):
    """Same-origin check applied when an `Origin` header is present: the
    page's own origin (the request `Host`) is the only one allowed. A
    request with no `Origin` (CLI/curl-style clients) is accepted here and
    still must satisfy the loopback policy below.
    """
    origin = handler.headers.get("Origin")
    if not origin:
        return True
    host = handler.headers.get("Host") or ""
    if not host:
        return False
    return _origin_netloc(origin) == _origin_netloc(host)
```
This means a curl/Cordis-style client with no Origin header is accepted at
the same-origin stage and only needs to satisfy the loopback check — exactly
what D-02 in CONTEXT.md relies on.

---

### `schemas/source_locator.schema.json` (new sidecar schema)

**Analog:** `schemas/normalized_document.schema.json` (header read in full,
`schema_validate.py` header read in full).

**Envelope + `$defs` pattern to copy** (`normalized_document.schema.json:1-45`, verified verbatim):
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://itembank.local/schemas/normalized_document.schema.json",
  "title": "itembank normalized source document",
  "description": "...",
  "x-itembank-version": 1,
  "type": "object",
  "additionalProperties": false,
  "required": ["schema_version", "source_id", "kind", "fingerprint", "byte_length", "spans", "objective_candidates"],
  "properties": {
    "schema_version": {"type": "integer", "const": 1, "description": "..."},
    "source_id": {"type": "string", "minLength": 1, "description": "..."},
    "kind": {"type": "string", "enum": ["markdown", "text"], "description": "..."},
    "fingerprint": {"type": "string", "minLength": 64, "description": "..."}
  },
  "$defs": {
    "span": { ... }
  }
}
```
Build `schemas/source_locator.schema.json` in this exact shape:
`additionalProperties: false` at every object level, `required` naming the
envelope fields from CONTEXT.md (`source_id`, `adapter`, `adapter_version`,
`fingerprint`, `captured_at`, `origin`, `rights`, `confidence`), an `enum`
for `adapter` (`["pdf","docx","pptx","epub","web","transcript","asr","ocr"]`),
and a `$defs.locator` entry with a `oneOf` over the per-medium locator body
shapes (the validator supports `oneOf`, confirmed in `schema_validate.py`'s
`SUPPORTED` frozenset). **Constraint:** the hand-rolled validator only
supports the keyword set `{type, properties, required,
additionalProperties, enum, const, items, minItems, uniqueItems, minLength,
pattern, minimum, maximum, $defs, $ref, oneOf}` (verified,
`schema_validate.py:29-33`) — do not use `patternProperties`, `allOf`, or
any Draft-2020-12 keyword outside that set; `check_schema` refuses the
whole document if it does.

**Validation call pattern** (`model_adapter.py:238`, verified verbatim):
```python
errs = schema_validate.validate(request, _SCHEMA)
if errs:
    return unavailable_result("adapter.request_invalid", errs[0], interaction_id)
```
Mirror this exactly for sidecar validation before the atomic write:
`errs = schema_validate.validate(sidecar, _LOCATOR_SCHEMA)`.

---

### `tests/source_adapters_roundtrip.py` (new)

**Analog:** `tests/identity_roundtrip.py` (header + `check_identity` read in
full this session) — the bespoke `check_*` function shape every
`*_roundtrip.py` test file in this project uses.

**Exact file header/import/fail() pattern** (`tests/identity_roundtrip.py:1-32`, verified verbatim):
```python
#!/usr/bin/env python3
"""Proves the identity kernel end to end: ...

Standard library only, runnable as `python tests/identity_roundtrip.py`.
"""
import os, re, shutil, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import identity                                             # noqa: E402
import discovery                                             # noqa: E402
...


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def check_identity():
    ids = set(identity.new_object_id() for _ in range(1000))
    if len(ids) != 1000:
        fail("1000 calls to new_object_id() produced a collision")
    ...
```
`tests/source_adapters_roundtrip.py` must copy this exact shape: shebang +
module docstring naming what invariant it proves, `ROOT`/`sys.path.insert`
boilerplate, top-level `import source_adapters`, `import identity`, `import
journal`, `import fixtures.audit.locator_fidelity_cases as locator_cases`
(and the new PPTX/EPUB/web/transcript fixture modules), a module-level
`fail(msg)`, then one `check_*` function per concern (`check_pdf_gold_cases`,
`check_docx_extra_parts`, `check_pptx_gold_cases`, `check_journal_integration`,
`check_rights_refusal`, `check_zip_bomb_guard`, ...), and a `if __name__ ==
"__main__":` block at the bottom that calls every `check_*` in sequence and
prints a final `"OK"` line (this file was not re-read for its tail, but every
sibling `*_roundtrip.py` in this project's own documented convention — see
`CLAUDE.md`'s "Test files use `*_roundtrip.py` pattern" — follows this
close-out shape; do not invent a different one).

**`API_ROUTES` length assertion this file must extend** — RESEARCH.md
verified (`daemon.py:220-222`) that `tests/daemon_roundtrip.py` contains a
`check_api_route_scope`-style function asserting the route-table length; the
executor must grep `tests/daemon_roundtrip.py` for `check_api_route_scope`
before editing, and bump whatever fixed integer it currently asserts
(twelve, per the quoted comment) to thirteen, in the same change that adds
the new `API_ROUTES` entry.

---

### `fixtures/audit/pptx_fidelity_cases.py`, `epub_fidelity_cases.py`, `web_capture_fidelity_cases.py`, `transcript_fidelity_cases.py` (new)

**Analog:** `fixtures/audit/locator_fidelity_cases.py` (header + PDF
assembly section read in full, `CASE_TABLE`/gold-manifest shape referenced
throughout RESEARCH.md with verified line numbers).

**Module docstring + "stdlib only, deterministic, repository-independent" contract** (`locator_fidelity_cases.py:1-19`, verified verbatim):
```python
#!/usr/bin/env python3
"""Deterministic, redistributable PDF/DOCX byte fixtures plus gold manifests
(Phase 11 architectural gate, 11-AI-SPEC section 4 / 11-VALIDATION T-11-27).
...
Stdlib only (hashlib, io, zipfile) and repository-independent: the case
table is immutable data, the builders are pure functions, and nothing here
reads or writes the repository.
"""
import hashlib
import io
import os
import zipfile


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()
```

Each new fixture file must copy this exact opening: a docstring naming
which phase/gate it serves, `stdlib only` imports (`hashlib`, `io`,
`zipfile`, `xml.etree.ElementTree` as needed — never `python-pptx` or any
third-party library inside a fixture builder, since fixtures build raw
bytes by hand so the adapter under test is the only thing exercising the
third-party parser), a `sha256(raw)` helper identical to the one above, and
pure-function byte assemblers (`_assemble_pdf`/`pdf_pages` is the PDF
precedent at `locator_fidelity_cases.py:34-77`; a PPTX/EPUB assembler
follows the same "build the zip/XML by hand, deterministic offsets, no
randomness" discipline since both formats are zip archives — reuse
`zipfile.ZipFile(io.BytesIO(...), "w")` with fixed timestamps, per
Pitfall 3's own path).

**Gold-manifest shape referenced by RESEARCH.md** (verified field names,
`locator_fidelity_cases.py:196-205,227,257`): every case carries a
`reading_order` list of short string ids (`"p1.0"`, `"p1.c1.0"`, `"t.r0c0"`,
`"hdr1"`, `"fn1.0"`) — reuse this exact id-shape convention for the new
media (`"s1.0"` for PPTX slide 1 shape 0, `"spine1.frag"` for EPUB, etc.),
not a redesigned id scheme, per RESEARCH.md Open Question 1's own
recommendation.

---

### `deps/lti-pins.txt` — pin-file convention to copy for adapter dependencies

**Analog:** `deps/lti-pins.txt` (whole file, 42 lines, read in full) — this
is the exact precedent for "a scoped, optional-dependency pin file with a
per-package license review and checksum block," which is precisely what
this phase's `pip install pdfplumber==... pdfminer.six==... python-docx==...
pypdf==... python-pptx==... readability-lxml==...` set needs.

**Header + per-package block pattern** (`deps/lti-pins.txt:1-21,40-41`, verified verbatim):
```
# LTI surface optional dependencies (phase 999.4, Directive 4a / D-08)
# ---------------------------------------------------------------------
# The LTI 1.3 surface's two optional, pinned, checksummed, license-reviewed
# imports. They are OPTIONAL: `surfaces/lti.py` guards on their presence and
# refuses by name with the install command when absent; every non-LTI command
# stays byte-identical (degrade, never block).
#
# License review (named, 2026-08-11, verified against PyPI metadata):
#   cryptography  -- Apache-2.0 OR BSD-3-Clause (dual), permissive.
#   PyJWT         -- MIT, permissive.
#
# CVE disposition (reviewed 2026-08-11 against PyPI/OSV records):
#   ...
#
# Checksums: sha256 of the wheel artifacts, recorded at implementation time.
#   cryptography-43.0.0-cp39-abi3-manylinux_2_28_x86_64.whl
#     sha256: cb013933d4c127349b3948aa8aaf2f12c0353ad0eccd715ca789c8a0f671646f
#   ...
cryptography==43.0.0 --hash=sha256:cb013933d4c127349b3948aa8aaf2f12c0353ad0eccd715ca789c8a0f671646f
PyJWT==2.10.1 --hash=sha256:dcdd193e30abefd5debf142f9adfcdd2b58004e644f25406ffaebd50bd98dacb
```
Create `deps/source-adapter-pins.txt` (new file, follows the `lti-pins.txt`
naming convention, not `requirements.txt`, since these are also optional
per-adapter dependencies that degrade individually — see RESEARCH.md's own
"one missing dependency degrades only that adapter" design). Header must
name: the phase (14C), the "optional, degrade never block" framing exactly
like the LTI header, a license review line per package (pdfplumber MIT,
pdfminer.six MIT, python-docx MIT, pypdf BSD-3, python-pptx MIT,
readability-lxml Apache-2.0), and the `checkpoint:human-verify` note the
Package Legitimacy Audit in RESEARCH.md flagged for this whole batch
(`unknown-downloads` SUS verdict on all six, judged low-risk but requiring
a checkpoint per protocol). Do not fold this into `requirements.txt` — that
file's own header (`zstandard`/`edge-tts`/`lameenc` block, not re-quoted
here) is for the audio-drill and Anki-import optional deps; `deps/*.txt` is
the established sibling location for a second surface's own optional set.

---

### OCR adapter — wrap, never reimplement

**Analog to WRAP, not copy-and-modify:** `scripts/ocr_lib.py` (whole file,
107 lines, read in full).

**Exact function signature to call from `source_adapters.py`** (`scripts/ocr_lib.py:78-79`, verified verbatim):
```python
def ocr_image(path, model=None, endpoint=None):
    """Transcribe all text in the image file at `path`. Returns the text."""
```
`source_adapters.py`'s OCR adapter must call `ocr_lib.ocr_image(path)`
(lazy `import scripts.ocr_lib as ocr_lib` inside the adapter function, same
lazy-import discipline as every other adapter) and catch the two documented
failure shapes: `RuntimeError("no Ollama server reachable...")` from
`find_endpoint()` (`ocr_lib.py:65-68`) and `RuntimeError("model '...' not
found...")` / `RuntimeError("ollama error %d: %s")` from `ocr_image`'s own
`except urllib.error.HTTPError` block (`ocr_lib.py:99-106`) — convert both
to `"source.dependency_missing"` / `"source.fetch_failed"`-shaped typed
`unsupported` results, never let the `RuntimeError` propagate raw. The
locator body this adapter produces must set `bbox: null` and `confidence:
null` explicitly (Pitfall 2 in RESEARCH.md — the skill returns flat text
only, `TRANSCRIBE_PROMPT` at `ocr_lib.py:24-30` has no coordinate or
confidence request in it) — do not fabricate geometry the skill never
measured.

## Shared Patterns

### Atomic write (sidecar + Markdown ordering)
**Source:** `journal.py:214` (`_write_bytes_atomic`, name/line verified;
body not re-quoted here since RESEARCH.md's Pattern 1/2 already gives the
exact call sequence) plus `journal.commit_operation` (`journal.py:330`).
**Apply to:** every adapter function in `source_adapters.py`. Sidecar file
written FIRST via a temp-file+atomic-replace helper (either reuse
`journal._write_bytes_atomic` if it is exposed at module level — verify
during implementation whether it is private-by-convention only — or copy
its temp+replace shape locally), THEN `journal.op_import`/`op_link` for the
Markdown SECOND. On journal failure, best-effort-remove the orphan sidecar.

### Rights gating
**Source:** `journal.py:885-893` (`op_import`'s docstring, quoted above:
"Requires the source's `transform` right to be exactly `\"granted\"`
(RIGHTS-01); refuses with `journal.rights_unknown` before any mutation
otherwise").
**Apply to:** every local-file adapter. No new rights-checking code is
written in `source_adapters.py` — passing `source_object_id` to `op_import`
is sufficient; the gate is enforced inside `journal.py` itself.

### Daemon route authority
**Source:** `daemon.py:1047-1060` (`_reject_cross_origin_write`, quoted
above in full).
**Apply to:** the single new `/api/source/import` route.

### Typed-failure / "nothing raises" envelope
**Source:** `model_adapter.py:58-70` (`unavailable_result`) and
`model_adapter.py:264-274` (`invoke`'s top-level `try/except Exception`
safety net, quoted above in full).
**Apply to:** every function in `source_adapters.py`, and the OCR
wrapper's `RuntimeError` conversion.

### Schema validation
**Source:** `schema_validate.py:1-33` (module docstring, `SUPPORTED`
keyword frozenset, verified verbatim) and `model_adapter.py:238`
(`schema_validate.validate(request, _SCHEMA)` call pattern).
**Apply to:** the new sidecar schema, validated before the atomic write in
every adapter function.

### Bespoke roundtrip test shape
**Source:** `tests/identity_roundtrip.py:1-40` (header/import/`fail()`
pattern, verified verbatim).
**Apply to:** `tests/source_adapters_roundtrip.py` in full, and the new
assertions added to `tests/daemon_roundtrip.py` for the route-table length
bump.

## No Analog Found

None. Every file this phase creates or modifies has a verified, concrete
analog already in the repository; RESEARCH.md's own "Don't Hand-Roll"
table independently confirms this (every hand-roll temptation this phase
might have maps onto an existing 14A primitive or an existing project
precedent).

## Metadata

**Analog search scope:** `identity.py`, `journal.py`, `model_adapter.py`,
`surfaces/daemon.py`, `scripts/ocr_lib.py`, `fixtures/audit/
locator_fidelity_cases.py`, `schemas/normalized_document.schema.json`,
`schema_validate.py`, `tests/identity_roundtrip.py`, `requirements.txt`,
`deps/lti-pins.txt` — all read directly this session (not carried over
unverified from RESEARCH.md) except the tail of `tests/identity_roundtrip.py`
and the full body of `tests/journal_roundtrip.py` /
`tests/operations_roundtrip.py` / `tests/daemon_roundtrip.py`, which
RESEARCH.md already quotes line-cited and this session did not need to
re-read to confirm (their existence and naming convention was independently
confirmed via `wc -l` and the `identity_roundtrip.py` read, which shares
their documented convention verbatim per `CLAUDE.md`'s own "Test files use
`*_roundtrip.py` pattern" section).
**Files scanned:** 11 read directly this session, plus CONTEXT.md and
RESEARCH.md (already containing prior verified reads of `journal_roundtrip.py`,
`operations_roundtrip.py`, `daemon_roundtrip.py`, `file_fault_tracer.py`,
`14A-FREEZE.md`, `discovery.py`, `surfaces/update.py`,
`SUPPLY-CHAIN-POLICY.md`).
**Pattern extraction date:** 2026-08-21
