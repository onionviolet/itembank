#!/usr/bin/env python3
"""The source-adapter boundary (Phase 14C, plan 14C-01).

One typed `import_source(...)` boundary normalizes any number of extraction
backends behind `ADAPTER_REGISTRY`, so adding a medium is a registration and
never a caller change (D-14C-1). Every failure -- an unknown adapter, an
unknown raw object, an oversized input, a missing optional dependency, an
encrypted or malformed file, a structure no adapter can address, an
unexpected exception -- converts to one typed result carrying a named
`source.*` code before any surface, journal, or evidence call. Nothing here
raises, with exactly one deliberate exception named below.

Adapters produce sources and never import `model.py` or `runtime.py` (D-05).
Span identity comes from `auditor.normalize_source`, never from a second
splitter: an adapter emits Markdown line by line and records which origin
locator produced each line, and the caller fills in the span id the one
parser assigned. That is what keeps exactly one parser structurally true
while the registry grows to eight media, and it is why a citation record
needs no new shape to resolve into a PDF page.

The one deliberate exception to "nothing here raises" is `journal.JournalError`,
which is re-raised rather than swallowed. A rights refusal is the journal's
contract to report by name; `journal.rights_unknown` is not a `source.*` code
and must not be laundered into one.

`source.oversized` here and `auditor.source.oversize` are deliberately
distinct: the first is an input file or archive member exceeding the intake
cap, the second is the derived text exceeding `auditor.MAX_SOURCE_BYTES`.
"""
import io
import json
import os

import auditor
import identity
import journal
import resources
import schema_validate


SCHEMA_RESOURCE = "schemas/source_locator.schema.json"

SOURCE_LOCATOR_VERSION = 1

SIDECAR_SUFFIX = ".locator.json"
DERIVED_MD_SUFFIX = ".md"
REMOTE_DIRNAME = "_sources"

# 200 MiB. An intake cap, not a normalization cap: a file over this is refused
# before any extraction backend is handed the bytes.
MAX_INPUT_BYTES_DEFAULT = 209715200

# The typed refusal codes this boundary can produce. Built from a
# set-then-sorted tuple so sortedness is structural, the same construction
# `model_adapter.ADAPTER_CODES` uses. Later plans append; nothing is renamed.
SOURCE_ADAPTER_CODES = tuple(sorted({
    "source.adapter_unknown", "source.approval_required",
    "source.backend_unconfigured", "source.dependency_missing",
    "source.encrypted", "source.fetch_failed", "source.internal_error",
    "source.malformed_input", "source.origin_refused", "source.oversized",
    "source.redirect_refused", "source.unsupported",
}))

# The frozen union vocabulary of structure kinds across every medium, lifted
# verbatim from the gold cases in `fixtures/audit/locator_fidelity_cases.py`
# so the acceptance corpus and the schema cannot disagree.
LOCATOR_KINDS = ("page", "paragraph", "column", "table", "table_cell",
                 "heading", "list_item", "header", "footer", "footnote",
                 "endnote", "tracked_insert", "tracked_delete", "comment",
                 "slide", "notes", "spine_item", "block", "cue", "segment",
                 "image_region")


def _load_schema():
    return json.loads(resources.read_text(SCHEMA_RESOURCE))


_LOCATOR_SCHEMA = _load_schema()


class _Refusal(Exception):
    """Internal control flow only: an extraction function raises this to
    return a typed code without threading a result tuple through every
    branch. It never escapes `import_source`."""

    def __init__(self, code, message):
        Exception.__init__(self, code, message)
        self.code = code
        self.message = message


# ---------------------------------------------------------------------------
# The extraction-function contract, held by every adapter in every later plan.
#
# An extraction function takes `(raw_bytes, options)` and returns the
# four-tuple `(markdown_text, locators, reading_order, unsupported)`:
#
#   markdown_text  a str, the derived Markdown, one emitted structure per line
#   locators       a list of dicts each carrying "id", "kind", "body", and the
#                  private key "_line" naming the one-based derived line it
#                  produced; "span_id" is absent and is filled in by the
#                  caller after normalization
#   reading_order  a list of locator ids in document reading order
#   unsupported    a list of {"code": ..., "message": ...} dicts
#
# An extraction function never writes a file, never mints an id, and never
# touches the journal. It raises `_Refusal` for a typed failure and nothing
# else; an unexpected exception is caught by `import_source`'s safety net.
# ---------------------------------------------------------------------------


def _identity_locators(text, medium):
    locators = []
    reading_order = []
    lines = text.split("\n")
    content_lines = lines[:-1] if lines and lines[-1] == "" else lines
    for number, _line in enumerate(content_lines, start=1):
        locator_id = "L%d" % number
        locators.append({
            "id": locator_id,
            "kind": "block",
            "body": {"medium": "markdown", "line": number},
            "_line": number,
        })
        reading_order.append(locator_id)
    return locators, reading_order


def _extract_markdown(raw_bytes, options):
    """The identity adapter. A hand-written Markdown file reaches disk through
    exactly the function a PDF does; that is what the promote in D-14C-1
    means in code, and it is why no Markdown-only side door survives."""
    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise _Refusal("source.malformed_input",
                       "the file is not valid UTF-8 at byte offset %d; no "
                       "derived source was produced" % exc.start)
    if not text.endswith("\n"):
        text += "\n"
    locators, reading_order = _identity_locators(text, "markdown")
    return text, locators, reading_order, []


def _extract_text(raw_bytes, options):
    """Plain UTF-8 text, treated as Markdown that happens to use no markup.
    Registered separately so the adapter name records what the learner said
    the file was, not what the extractor guessed."""
    return _extract_markdown(raw_bytes, options)


_PDFPLUMBER_INSTALL = ("run: pip install pdfplumber==0.11.10 "
                       "pdfminer.six==20260107")


def _extract_pdf(raw_bytes, options):
    """Born-digital PDF text, one locator per extracted line.

    `pdfplumber` is imported inside the function body, never at module top, so
    `import source_adapters` succeeds on a machine with none of the optional
    packages present and only the pdf adapter refuses.
    """
    try:
        import pdfplumber
    except ImportError:
        raise _Refusal("source.dependency_missing",
                       "the pdf adapter needs pdfplumber, which is not "
                       "installed. It is optional and every other command is "
                       "unaffected. To enable pdf import, %s"
                       % _PDFPLUMBER_INSTALL)

    lines_out = []
    locators = []
    reading_order = []
    try:
        with pdfplumber.open(io.BytesIO(raw_bytes)) as pdf:
            if getattr(pdf, "is_encrypted", False):
                raise _Refusal("source.encrypted",
                               "the pdf is encrypted; no text was extracted "
                               "and nothing was written")
            for page_number, page in enumerate(pdf.pages, start=1):
                # RESEARCH Pitfall 5: check the cheap char list before paying
                # for word grouping and text extraction on an image-only page.
                if not page.chars:
                    continue
                words = page.extract_words()
                text = page.extract_text() or ""
                for index, line_text in enumerate(
                        [ln for ln in text.split("\n") if ln.strip()]):
                    bbox = _line_bbox(words, line_text)
                    lines_out.append(line_text)
                    locator_id = "p%d.%d" % (page_number, index)
                    locators.append({
                        "id": locator_id,
                        "kind": "paragraph",
                        "body": {
                            "medium": "pdf",
                            "page": page_number,
                            "index": index,
                            # Column detection arrives in plan 14C-02. Null is
                            # honest here; a fabricated 0 would not be.
                            "column": None,
                            "bbox": bbox,
                        },
                        "_line": len(lines_out),
                    })
                    reading_order.append(locator_id)
    except _Refusal:
        raise
    except Exception as exc:
        raise _Refusal("source.malformed_input",
                       "the pdf could not be parsed (%s); no derived source "
                       "was produced" % type(exc).__name__)

    if not locators:
        return "", [], [], [{
            "code": "source.unsupported",
            "message": "image-only page: no text-bearing structure",
        }]
    return "\n".join(lines_out) + "\n", locators, reading_order, []


def _line_bbox(words, line_text):
    """The [x0, top, x1, bottom] box enclosing the words of one extracted
    line, or None when no word matched. The key names are pdfplumber's own,
    confirmed against the installed 0.11.10 rather than assumed (RESEARCH
    assumption A2)."""
    wanted = line_text.split()
    if not wanted:
        return None
    box = None
    remaining = list(wanted)
    for word in words:
        if not remaining:
            break
        if word.get("text") != remaining[0]:
            continue
        remaining.pop(0)
        corners = (word["x0"], word["top"], word["x1"], word["bottom"])
        if box is None:
            box = list(corners)
        else:
            box[0] = min(box[0], corners[0])
            box[1] = min(box[1], corners[1])
            box[2] = max(box[2], corners[2])
            box[3] = max(box[3], corners[3])
    return box


ADAPTER_REGISTRY = {
    "markdown": _extract_markdown,
    "text": _extract_text,
    "pdf": _extract_pdf,
}

ADAPTER_VERSIONS = {name: "1.0.0" for name in ADAPTER_REGISTRY}


# ---------------------------------------------------------------------------
def unsupported_result(code, message, source_id):
    """The typed envelope every failure converts into, shaped like
    `model_adapter.unavailable_result`. `source_id` may be None when the
    failure was reached before an id was minted."""
    return {
        "schema_version": SOURCE_LOCATOR_VERSION,
        "source_id": source_id,
        "status": "unsupported",
        "adapter": None,
        "md_rel_path": None,
        "sidecar_rel_path": None,
        "journal_entry_id": None,
        "error": {"code": code, "message": message},
    }


def ok_result(source_id, adapter, md_rel_path, sidecar_rel_path,
              journal_entry_id):
    return {
        "schema_version": SOURCE_LOCATOR_VERSION,
        "source_id": source_id,
        "status": "ok",
        "adapter": adapter,
        "md_rel_path": md_rel_path,
        "sidecar_rel_path": sidecar_rel_path,
        "journal_entry_id": journal_entry_id,
        "error": None,
    }


def sidecar_path_for(md_rel_path):
    """The sidecar path is derived from the derived-Markdown path and never
    comes from a caller, so no argument can steer a write."""
    if md_rel_path.endswith(DERIVED_MD_SUFFIX):
        return md_rel_path[:-len(DERIVED_MD_SUFFIX)] + SIDECAR_SUFFIX
    return md_rel_path + SIDECAR_SUFFIX


def build_sidecar(source_id, adapter, md_bytes, origin, rights, locators,
                  reading_order, unsupported, confidence=None):
    """Return exactly the frozen envelope. The fingerprint comes from
    `identity.object_fingerprint` and is computed no other way, so the
    sidecar, the journal entry, and the registry row can never disagree."""
    return {
        "schema_version": SOURCE_LOCATOR_VERSION,
        "source_id": source_id,
        "adapter": adapter,
        "adapter_version": ADAPTER_VERSIONS.get(adapter, "1.0.0"),
        "fingerprint": identity.object_fingerprint(md_bytes, "source"),
        "captured_at": identity.utc_now(),
        "origin": origin,
        "rights": rights,
        "confidence": confidence,
        "reading_order": list(reading_order),
        "locators": [dict(loc) for loc in locators],
        "unsupported": list(unsupported),
    }


def write_sidecar_atomic(path, sidecar):
    """Same-directory temp file, write, flush, fsync, `os.replace`: the shape
    `journal._write_bytes_atomic` uses, so a fault leaves the old or the new
    sidecar and never a half-written one. The byte layout matches
    `surfaces/settings.write_settings`, so a repeated write is byte-identical."""
    raw = (json.dumps(sidecar, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "wb") as fh:
        fh.write(raw)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def _resolve_raw(base, raw_object_id):
    registry = journal.read_registry(base)
    row = registry.get(raw_object_id)
    if row is None:
        raise _Refusal("source.malformed_input",
                       "no object %s is recorded in this root's registry. "
                       "Link the file first; import_source never links."
                       % raw_object_id)
    return row


def _read_raw_bytes(base, row, max_input_bytes):
    path = os.path.join(os.path.abspath(base), row["path"])
    try:
        size = os.path.getsize(path)
    except OSError:
        raise _Refusal("source.malformed_input",
                       "the raw file %s is not readable" % row["path"])
    if size > max_input_bytes:
        raise _Refusal("source.oversized",
                       "the raw file %s is %d bytes, over the %d-byte intake "
                       "cap; nothing was extracted"
                       % (row["path"], size, max_input_bytes))
    try:
        with open(path, "rb") as fh:
            return fh.read()
    except OSError:
        raise _Refusal("source.malformed_input",
                       "the raw file %s could not be read" % row["path"])


def _join_span_ids(locators, spans):
    """Fill each locator's `span_id` from the span the one parser assigned to
    the derived line the locator produced. A locator mapping to no derived
    line carries None. No span id is ever computed here."""
    by_line = {}
    for span in spans:
        by_line.setdefault(span["locator"]["start_line"], span["span_id"])
    joined = []
    for locator in locators:
        entry = {k: v for k, v in locator.items() if k != "_line"}
        entry["span_id"] = by_line.get(locator.get("_line"))
        joined.append({
            "id": entry["id"],
            "span_id": entry["span_id"],
            "kind": entry["kind"],
            "body": entry["body"],
        })
    return joined


def _extract(base, adapter, raw_object_id, options):
    """The read-only half both `import_source` and `preview_source` run.
    Returns `(row, raw_bytes, md_text, locators, reading_order, unsupported)`."""
    if adapter not in ADAPTER_REGISTRY:
        raise _Refusal("source.adapter_unknown",
                       "%s is not a registered source adapter; registered "
                       "adapters are: %s"
                       % (adapter, ", ".join(sorted(ADAPTER_REGISTRY))))
    row = _resolve_raw(base, raw_object_id)
    max_input_bytes = (options or {}).get("max_input_bytes",
                                           MAX_INPUT_BYTES_DEFAULT)
    raw_bytes = _read_raw_bytes(base, row, max_input_bytes)
    md_text, locators, reading_order, unsupported = \
        ADAPTER_REGISTRY[adapter](raw_bytes, options or {})
    return row, raw_bytes, md_text, locators, reading_order, unsupported


def _import_source(base, adapter, raw_object_id, actor_kind, actor_name,
                   rights_grant, options):
    row, _raw, md_text, locators, reading_order, unsupported = \
        _extract(base, adapter, raw_object_id, options)

    if unsupported and not locators:
        # A refusal writes nothing and journals nothing: an empty derived
        # source is not a success with zero locators, it is a named refusal.
        return unsupported_result(unsupported[0]["code"],
                                   unsupported[0]["message"], None)

    md_bytes = md_text.encode("utf-8")
    source_id = identity.new_object_id()
    spans = auditor.normalize_source(md_bytes, source_id,
                                      kind="markdown")["spans"]
    joined = _join_span_ids(locators, spans)

    md_rel_path = row["path"] + DERIVED_MD_SUFFIX
    sidecar_rel_path = sidecar_path_for(md_rel_path)

    origin = {
        "kind": "local_file",
        "value": row["path"],
        "fetched_at": None,
        "http_etag": None,
        "http_last_modified": None,
        "snapshot_rel_path": None,
    }
    # The rights recorded on the raw file are the rights the derived source
    # inherits. A wire-supplied grant never widens them: it is recorded as the
    # caller's claim, and the journal reads the registry row inside its own
    # lock when it decides whether the transform right permits this import.
    rights = dict(row.get("rights") or identity.rights_default())

    sidecar = build_sidecar(source_id, adapter, md_bytes, origin, rights,
                            joined, reading_order, unsupported)
    errors = schema_validate.validate(sidecar, _LOCATOR_SCHEMA)
    if errors:
        return unsupported_result("source.internal_error", errors[0],
                                   source_id)

    sidecar_abs = os.path.join(os.path.abspath(base), sidecar_rel_path)
    write_sidecar_atomic(sidecar_abs, sidecar)

    try:
        # `commit_operation` directly rather than `journal.op_import` for one
        # reason: `op_import` mints the object_id itself, and the sidecar must
        # already carry that id when it is written. The RIGHTS-01 transform
        # gate lives inside `_commit_impl` and fires identically either way.
        record = journal.commit_operation(
            base, source_id, "source", md_rel_path, "import", md_bytes,
            expected_fingerprint=None, actor_kind=actor_kind,
            actor_name=actor_name, create_if_missing=True,
            source_object_id=raw_object_id)
    except journal.JournalError:
        try:
            os.remove(sidecar_abs)
        except OSError:
            pass
        raise

    return ok_result(source_id, adapter, md_rel_path, sidecar_rel_path,
                      record.get("last_entry_id"))


def import_source(base, adapter, raw_object_id, actor_kind, actor_name,
                  rights_grant=None, options=None):
    """The one public write boundary. Returns a typed result; the only
    exception that escapes is `journal.JournalError`, deliberately, because a
    rights refusal is the journal's to report by name."""
    try:
        return _import_source(base, adapter, raw_object_id, actor_kind,
                              actor_name, rights_grant, options)
    except journal.JournalError:
        raise
    except _Refusal as refusal:
        return unsupported_result(refusal.code, refusal.message, None)
    except Exception:  # last-resort safety net, never a traceback
        return unsupported_result("source.internal_error",
                                   "unexpected source-adapter failure", None)


def preview_source(base, adapter, raw_object_id, options=None):
    """The free half of the auto-fetch versus approve-before-bind pair: the
    same path an import takes, up to and including the span join, returning
    the would-be sidecar and writing nothing at all. Search and read stay
    free under either binding policy; the bind step is the gated one."""
    try:
        row, _raw, md_text, locators, reading_order, unsupported = \
            _extract(base, adapter, raw_object_id, options)
        if unsupported and not locators:
            return unsupported_result(unsupported[0]["code"],
                                       unsupported[0]["message"], None)
        md_bytes = md_text.encode("utf-8")
        source_id = identity.new_object_id()
        spans = auditor.normalize_source(md_bytes, source_id,
                                          kind="markdown")["spans"]
        joined = _join_span_ids(locators, spans)
        origin = {
            "kind": "local_file",
            "value": row["path"],
            "fetched_at": None,
            "http_etag": None,
            "http_last_modified": None,
            "snapshot_rel_path": None,
        }
        rights = dict(row.get("rights") or identity.rights_default())
        sidecar = build_sidecar(source_id, adapter, md_bytes, origin, rights,
                                joined, reading_order, unsupported)
        result = ok_result(source_id, adapter,
                            row["path"] + DERIVED_MD_SUFFIX,
                            sidecar_path_for(row["path"] + DERIVED_MD_SUFFIX),
                            None)
        result["preview"] = {"markdown": md_text, "sidecar": sidecar}
        return result
    except _Refusal as refusal:
        return unsupported_result(refusal.code, refusal.message, None)
    except Exception:
        return unsupported_result("source.internal_error",
                                   "unexpected source-adapter failure", None)
