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
import ipaddress
import json
import os
import posixpath
import re
import shutil
import socket
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from xml.etree import ElementTree

import discovery

import auditor
import identity
import journal
import resources
import schema_validate
from extension_registry import build_registry


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


# The WordprocessingML main namespace, spelled as the ElementTree prefix so a
# tag test is a string comparison and never a namespace-map lookup.
W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

# The package parts python-docx's object model never surfaces. Read directly,
# each one through `_read_zip_part` and `_parse_xml_safely`, because an adapter
# built on python-docx alone silently produces nothing for a document whose
# content lives in a footnote, a header, or a comment (RESEARCH Pitfall 1).
DOCX_EXTRA_PARTS = ("word/footnotes.xml", "word/endnotes.xml",
                    "word/comments.xml")

# PresentationML and the package relationships namespace, spelled as
# ElementTree prefixes for the same reason W_NS is.
P_NS = "{http://schemas.openxmlformats.org/presentationml/2006/main}"
R_NS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
PKG_REL_NS = "{http://schemas.openxmlformats.org/package/2006/relationships}"

# Bounded structure, so a hostile part cannot cost unbounded work.
MAX_XML_DEPTH = 100
MAX_ZIP_MEMBERS = 4096

# The Compound File Binary header. An OOXML container sealed with a password
# is a CFB wrapper around the encrypted package, not a zip, so `zipfile`
# reports it as a bad zip and the signature is the only way to tell "encrypted"
# from "corrupt" by name rather than by guess.
_OLE_SIGNATURE = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"


def _load_schema():
    return json.loads(resources.read_text(SCHEMA_RESOURCE))


_LOCATOR_SCHEMA = _load_schema()


def _options(options):
    """Caller options merged over the restrictive defaults. A caller that
    passes nothing gets `approve_before_bind`, private origins denied, and
    the shipped caps, which is the same thing a surface reading
    `itembank.json` would get from an untouched install."""
    merged = dict(SOURCE_OPTION_DEFAULTS)
    merged.update(options or {})
    return merged


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


# ---------------------------------------------------------------------------
# The one hardened container seam. Every zip-backed adapter (docx here, pptx in
# plan 14C-03, epub in plan 14C-07) reads through these two functions. A later
# adapter that opens a ZipFile and calls .read() directly bypasses the size cap
# for its own format, and the bomb guard then covers only the formats that did
# call through; that is the failure mode this seam exists to prevent.


def _zip_member_error(zf, name, options):
    """The checks `_read_zip_part` runs before it reads anything, factored out
    so a caller can preflight every member of an archive it is about to hand
    to a third-party reader. Returns an error dict or None. Never raises."""
    max_input_bytes = (options or {}).get("max_input_bytes",
                                          MAX_INPUT_BYTES_DEFAULT)
    try:
        info = zf.getinfo(name)
    except KeyError:
        return {"code": "source.malformed_input",
                "message": "the package has no %s member; it is not a "
                           "readable document of this kind" % name}
    if info.file_size > max_input_bytes:
        return {"code": "source.oversized",
                "message": "oversized zip part: %s declares %d uncompressed "
                           "bytes, over the %d-byte intake cap, and was "
                           "refused without being decompressed"
                           % (name, info.file_size, max_input_bytes)}
    if len(zf.namelist()) > MAX_ZIP_MEMBERS:
        return {"code": "source.oversized",
                "message": "oversized zip part: the archive holds %d members, "
                           "over the %d-member cap"
                           % (len(zf.namelist()), MAX_ZIP_MEMBERS)}
    normalized = posixpath.normpath(name.replace("\\", "/"))
    if normalized.startswith("/") or normalized == ".." or \
            normalized.startswith("../") or ":" in normalized.split("/")[0][1:]:
        return {"code": "source.malformed_input",
                "message": "the archive names a member outside the package "
                           "(%s); nothing was read" % name}
    return None


def _read_zip_part(zf, name, options):
    """Read one archive member, or refuse by name. Returns `(bytes, None)` or
    `(None, error_dict)` and never raises.

    The declared `ZipInfo.file_size` is checked before `zf.read` is called, so
    a high-ratio member is refused without being decompressed: a guard that
    refuses only after decompressing is not a guard (T-14C-09)."""
    error = _zip_member_error(zf, name, options)
    if error is not None:
        return None, error
    try:
        return zf.read(name), None
    except Exception as exc:
        return None, {"code": "source.malformed_input",
                      "message": "the archive member %s could not be read "
                                 "(%s)" % (name, type(exc).__name__)}


def _xml_depth(element, depth=1):
    if depth > MAX_XML_DEPTH:
        return depth
    deepest = depth
    for child in list(element):
        found = _xml_depth(child, depth + 1)
        if found > deepest:
            deepest = found
        if deepest > MAX_XML_DEPTH:
            return deepest
    return deepest


def _parse_xml_safely(raw, options):
    """Parse one container XML part, or refuse by name. Returns
    `(element, error_dict)` with exactly one side populated. Never raises.

    Bytes carrying a `<!DOCTYPE` or a `<!ENTITY` declaration are refused
    before the parser is invoked at all. Neither is legal in a well-formed
    OOXML or EPUB content part, so refusing outright costs no real document
    anything and removes the entity-expansion class entirely rather than
    bounding it (T-14C-10). Do not soften this back to a depth limit or an
    expansion budget: a budget still runs the expander, and this does not.
    """
    probe = raw[:8192] if isinstance(raw, bytes) else raw[:8192].encode("utf-8")
    if b"<!DOCTYPE" in probe or b"<!ENTITY" in probe:
        return None, {
            "code": "source.malformed_input",
            "message": "entity declaration in an OOXML part: a document type "
                       "definition or entity declaration is not accepted, and "
                       "the part was refused without being expanded"}
    try:
        element = ElementTree.fromstring(raw)
    except ElementTree.ParseError as exc:
        return None, {"code": "source.malformed_input",
                      "message": "the XML part is not well formed (%s)" % exc}
    if _xml_depth(element) > MAX_XML_DEPTH:
        return None, {"code": "source.malformed_input",
                      "message": "the XML part nests deeper than %d elements"
                                 % MAX_XML_DEPTH}
    return element, None


_PDFPLUMBER_INSTALL = ("run: pip install pdfplumber==0.11.10 "
                       "pdfminer.six==20260107")


# Page-geometry thresholds for the PDF adapter, in PDF points. These are
# heuristics, and they are named constants rather than inline numbers so that
# the sidecar `confidence` field and these values can be read together.
PDF_RUNNING_MARGIN = 50.0
PDF_FOOTNOTE_BAND = 0.8
PDF_LINE_TOLERANCE = 3.0

_PDF_TABLE_SETTINGS = {"vertical_strategy": "text",
                       "horizontal_strategy": "text"}


def _pdf_lines(words):
    """Group words into lines by their vertical position. Words are grouped
    rather than `extract_text()` split, because `extract_text()` joins a
    two-column page across the gutter and the two-column gold case records the
    columns read one after the other, not interleaved."""
    lines = []
    for word in sorted(words, key=lambda w: (round(w["top"], 1), w["x0"])):
        if lines and abs(lines[-1][0]["top"] - word["top"]) <= PDF_LINE_TOLERANCE:
            lines[-1].append(word)
        else:
            lines.append([word])
    return lines


def _pdf_line_record(line_words):
    text = " ".join(word["text"] for word in line_words)
    bbox = [min(w["x0"] for w in line_words),
            min(w["top"] for w in line_words),
            max(w["x1"] for w in line_words),
            max(w["bottom"] for w in line_words)]
    return text, bbox


def _pdf_columns(words, page_width):
    """Return the per-column word lists when the page really is in columns,
    or a single list when it is not.

    Two bands only, split at the page midpoint, and only when the bands do not
    overlap horizontally: a gutter is what makes a two-column page different
    from a wide table, and the table gold case (whose second column starts at
    x0 300 on a 612-point page) must not be mistaken for one."""
    mid = page_width / 2.0
    left = [w for w in words if w["x0"] < mid]
    right = [w for w in words if w["x0"] >= mid]
    if not left or not right:
        return [words]
    if max(w["x1"] for w in left) > min(w["x0"] for w in right):
        return [words]
    return [left, right]


def _pdf_tables(page):
    """Tables pdfplumber's text strategy finds, filtered to the ones that are
    really tables. The text strategy detects an alignment grid, so a page of
    ordinary left-aligned prose comes back as a one-column table; requiring at
    least two columns and at least two non-empty rows is what separates the
    table gold case from the footnote gold case, both of which the raw call
    reports as a table."""
    kept = []
    for table in page.find_tables(_PDF_TABLE_SETTINGS):
        grid = table.extract()
        rows = [(index, row) for index, row in enumerate(grid)
                if any((cell or "").strip() for cell in row)]
        if len(rows) < 2 or max(len(row) for _index, row in rows) < 2:
            continue
        kept.append((table, rows))
    return kept


def _extract_pdf(raw_bytes, options):
    """Born-digital PDF text: headers, body paragraphs in column order,
    tables, footnotes, and footers, one locator each.

    `pdfplumber` is imported inside the function body, never at module top, so
    `import source_adapters` succeeds on a machine with none of the optional
    packages present and only the pdf adapter refuses.

    A PDF carries no footnote structure, so a footnote is detected
    positionally: a line in the bottom fifth of the page that is not in the
    footer margin, and whose font size is no larger than the page's modal font
    size. That is a heuristic and the sidecar says so: any PDF whose locator
    set includes a footnote records `confidence` `medium` rather than `high`.
    Headers and footers are the same kind of judgement, made at the top and
    bottom `PDF_RUNNING_MARGIN` points of the page.
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

    def emit(locator_id, kind, text, page_number, index, column, bbox,
             ordered=True):
        lines_out.append(text)
        locators.append({
            "id": locator_id,
            "kind": kind,
            "body": {"medium": "pdf", "page": page_number, "index": index,
                     "column": column, "bbox": bbox},
            "_line": len(lines_out),
        })
        if ordered:
            reading_order.append(locator_id)

    try:
        with pdfplumber.open(io.BytesIO(raw_bytes)) as pdf:
            # Unreachable for a file sealed by the standard security handler,
            # which fails inside `open` before this line (D-14C-4), and kept
            # for a document that parses and reports encryption afterwards.
            if getattr(pdf, "is_encrypted", False):
                raise _Refusal("source.encrypted",
                               "encrypted PDF: no unauthenticated structure")
            for page_number, page in enumerate(pdf.pages, start=1):
                # RESEARCH Pitfall 5: check the cheap char list before paying
                # for word grouping, table finding, and text extraction on an
                # image-only page.
                if not page.chars:
                    continue
                _extract_pdf_page(page, page_number, emit)
    except _Refusal:
        raise
    except Exception as exc:
        if b"/Encrypt" in raw_bytes:
            raise _Refusal("source.encrypted",
                           "encrypted PDF: no unauthenticated structure")
        raise _Refusal("source.malformed_input", "malformed/truncated PDF")

    if not locators:
        return "", [], [], [{
            "code": "source.unsupported",
            "message": "image-only page: no text-bearing structure",
        }]
    return "\n".join(lines_out) + "\n", locators, reading_order, []


def _extract_pdf_page(page, page_number, emit):
    """One page's worth of emission, in the order a reader reads it: running
    header, then body (column by column, or table cell by table cell), then
    footnotes, then running footer.

    Columns are resolved before lines are grouped, not after. A line is a run
    of words at one vertical position, and on a two-column page that run
    spans the gutter, so grouping first and splitting afterwards produces one
    line holding both columns, which is exactly the interleaving the
    two-column gold case exists to refuse."""
    words = page.extract_words()
    if not words:
        return
    height = page.height
    tables = _pdf_tables(page)
    table_boxes = [table.bbox for table, _rows in tables]

    def inside_a_table(word):
        for x0, top, x1, bottom in table_boxes:
            if word["x0"] >= x0 - 1 and word["x1"] <= x1 + 1 and \
                    word["top"] >= top - 1 and word["bottom"] <= bottom + 1:
                return True
        return False

    loose = [word for word in words if not inside_a_table(word)]
    columns = _pdf_columns(loose, page.width) if loose else []

    headers, footers, footnotes = [], [], []
    body_columns = []
    for column_words in columns:
        body = []
        for line_words in _pdf_lines(column_words):
            text, bbox = _pdf_line_record(line_words)
            if bbox[1] < PDF_RUNNING_MARGIN:
                headers.append((text, bbox))
            elif bbox[3] > height - PDF_RUNNING_MARGIN:
                footers.append((text, bbox))
            elif bbox[1] > PDF_FOOTNOTE_BAND * height:
                footnotes.append((text, bbox))
            else:
                body.append((text, bbox))
        body_columns.append(body)

    for text, bbox in headers:
        emit("hdr%d" % page_number, "header", text, page_number, 0, None, bbox)

    for table_index, (table, rows) in enumerate(tables, start=1):
        emit("t" if len(tables) == 1 else "t%d" % table_index,
             "table", "", page_number, 0, None, list(table.bbox),
             ordered=False)
        for row_index, (grid_index, row) in enumerate(rows):
            for col_index, cell_text in enumerate(row):
                cell = table.rows[grid_index].cells[col_index]
                emit("t.r%dc%d" % (row_index, col_index), "table_cell",
                     cell_text or "", page_number, row_index, None,
                     list(cell) if cell else None)

    two_column = len(body_columns) == 2
    for column_number, body in enumerate(body_columns, start=1):
        for index, (text, bbox) in enumerate(body):
            if two_column:
                emit("p%d.c%d.%d" % (page_number, column_number, index),
                     "paragraph", text, page_number, index, column_number,
                     bbox)
            else:
                emit("p%d.%d" % (page_number, index), "paragraph", text,
                     page_number, index, None, bbox)

    for index, (text, bbox) in enumerate(footnotes):
        emit("fn%d.%d" % (page_number, index), "footnote", text, page_number,
             index, None, bbox)

    for text, bbox in footers:
        emit("ftr%d" % page_number, "footer", text, page_number, 0, None, bbox)


def _extract_confidence(adapter, locators):
    """The sidecar's advisory confidence. A PDF whose locator set includes a
    positionally detected footnote is `medium`, not `high`: that is what the
    field is for, and leaving a heuristic result at `high` would be a claim
    the adapter cannot support. Media whose structure is declared rather than
    inferred record no confidence at all."""
    if adapter == "epub":
        # The reading order is declared by the package document rather than
        # inferred, a stronger guarantee than the PDF geometry heuristics.
        return "high"
    if adapter == "ocr":
        # A vision model transcribing a photograph is the least reliable
        # extraction in the registry, and a citation into it should say so.
        return "low"
    if adapter == "transcript":
        # An SRT or WebVTT file declares both timings. The bracketed shape's
        # ends are inferred from the following cue, which is exactly the
        # distinction this field exists for.
        if any(loc.get("_inferred_ends") for loc in locators):
            return "medium"
        return "high"
    if adapter == "web":
        # A capture whose bytes had to be decoded by a replacing fallback is
        # text the adapter is not certain it read correctly.
        if any(loc.get("_exact_decode") is False for loc in locators):
            return "medium"
        return "high"
    if adapter != "pdf":
        return None
    if any(loc.get("kind") == "footnote" for loc in locators):
        return "medium"
    return "high"


_PYTHON_DOCX_INSTALL = "run: pip install python-docx==1.2.0"

_DOCX_LIST_STYLES = ("ListBullet", "ListNumber", "ListParagraph")

_HEADING_LEVEL = re.compile(r"^Heading(\d+)$")


def _w_text(element, tag="t"):
    """The text of every `w:<tag>` descendant, joined. `w:t` carries ordinary
    run text and `w:delText` carries the text of a tracked deletion, which is
    why a deletion never appears inside the paragraph text: the two live under
    different tags and this function reads one of them at a time."""
    return "".join(node.text or "" for node in element.iter(W_NS + tag))


def _docx_part_locators(zf, name, options, wrapper_tag, id_prefix, kind,
                        part, skip_ids=()):
    """One locator per `wrapper_tag` element in one package part, read through
    the hardened seam. Returns `(records, error)`."""
    if name not in zf.namelist():
        return [], None
    raw, error = _read_zip_part(zf, name, options)
    if error is not None:
        return [], error
    root, error = _parse_xml_safely(raw, options)
    if error is not None:
        return [], error
    records = []
    for index, node in enumerate(root.iter(W_NS + wrapper_tag)):
        ref_id = node.get(W_NS + "id")
        if ref_id in skip_ids:
            continue
        text = _w_text(node)
        if not text.strip():
            continue
        records.append({
            "id": "%s.%s" % (id_prefix, ref_id),
            "kind": kind,
            "text": text,
            "part": part,
            "paragraph_index": index,
            "ref_id": ref_id,
        })
    return records, None


def _docx_running_parts(zf, options, stem, prefix, kind, part):
    """Header or footer parts, which are named `word/header1.xml` and so on
    rather than living in one part. The gold cases record the id as `hdr` when
    there is one and `hdr1`, `hdr2` when there are several."""
    names = sorted(n for n in zf.namelist()
                   if re.match(r"^word/%s\d*\.xml$" % stem, n))
    records = []
    for index, name in enumerate(names, start=1):
        raw, error = _read_zip_part(zf, name, options)
        if error is not None:
            return [], error
        root, error = _parse_xml_safely(raw, options)
        if error is not None:
            return [], error
        text = _w_text(root)
        if not text.strip():
            continue
        records.append({
            "id": prefix if len(names) == 1 else "%s%d" % (prefix, index),
            "kind": kind,
            "text": text,
            "part": part,
            "paragraph_index": index - 1,
            "ref_id": None,
        })
    return records, None


def _docx_extra_parts(zf, options):
    """Footnotes, endnotes, comments, headers, and footers: the five parts
    python-docx's `Document` object never surfaces (RESEARCH Pitfall 1). An
    adapter built on `document.paragraphs` plus `document.tables` alone passes
    the easy cases and silently produces nothing for these, which is why they
    are read here directly and why four gold cases exist to catch it.

    Returns `(headers, tail, error)`: headers sort before the body and the
    tail (footnotes, endnotes, comments, footers) sorts after it, which is the
    order the gold cases record."""
    headers, error = _docx_running_parts(zf, options, "header", "hdr",
                                          "header", "header")
    if error is not None:
        return [], [], error
    footers, error = _docx_running_parts(zf, options, "footer", "ftr",
                                          "footer", "footer")
    if error is not None:
        return [], [], error
    tail = []
    for name, wrapper, prefix, kind, part, skip in (
            ("word/footnotes.xml", "footnote", "fn", "footnote", "footnote",
             ("0", "-1")),
            ("word/endnotes.xml", "endnote", "en", "endnote", "endnote",
             ("0", "-1")),
            ("word/comments.xml", "comment", "cmt", "comment", "comment", ()),
    ):
        records, error = _docx_part_locators(zf, name, options, wrapper,
                                             prefix, kind, part, skip)
        if error is not None:
            return [], [], error
        tail.extend(records)
    tail.extend(footers)
    return headers, tail, None


def _docx_body_records(body, unsupported):
    """Walk the body in document order. `document.paragraphs` followed by
    `document.tables` loses the interleaving, and the nested-table gold case
    depends on the real order, so the children of `w:body` are walked once."""
    records = []
    heading_counts = {}
    list_count = 0
    para_count = 0
    for block_index, child in enumerate(body):
        if child.tag == W_NS + "p":
            text = _w_text(child)
            if not text.strip():
                if list(child.iter(W_NS + "drawing")):
                    unsupported.append({
                        "code": "source.unsupported",
                        "message": "drawing/text-box object (no text-bearing "
                                   "structure without drawingml extraction)",
                    })
                continue
            style = child.find("%spPr/%spStyle" % (W_NS, W_NS))
            style_val = style.get(W_NS + "val") if style is not None else None
            numbered = child.find("%spPr/%snumPr" % (W_NS, W_NS)) is not None
            heading = _HEADING_LEVEL.match(style_val or "")
            if heading:
                level = int(heading.group(1))
                index = heading_counts.get(level, 0)
                heading_counts[level] = index + 1
                records.append({"id": "h%d.%d" % (level, index),
                                "kind": "heading", "text": text,
                                "part": "body", "paragraph_index": block_index,
                                "ref_id": None})
            elif numbered or (style_val or "") in _DOCX_LIST_STYLES:
                records.append({"id": "li.%d" % list_count,
                                "kind": "list_item", "text": text,
                                "part": "body", "paragraph_index": block_index,
                                "ref_id": None})
                list_count += 1
            else:
                records.append({"id": "p.%d" % para_count,
                                "kind": "paragraph", "text": text,
                                "part": "body", "paragraph_index": block_index,
                                "ref_id": None})
                para_count += 1
            # Tracked ranges are body content, so they follow their own
            # paragraph rather than sorting into a separate part. The id comes
            # from the w:id attribute the document itself carries, not from a
            # positional counter: the gold cases record ins.1 and del.2, which
            # are the document's own ids and not the adapter's.
            for tag, kind in (("ins", "tracked_insert"),
                              ("del", "tracked_delete")):
                for node in child.iter(W_NS + tag):
                    marked = _w_text(node,
                                     "delText" if tag == "del" else "t")
                    if not marked.strip():
                        continue
                    records.append({
                        "id": "%s.%s" % (tag, node.get(W_NS + "id")),
                        "kind": kind, "text": marked, "part": "body",
                        "paragraph_index": block_index,
                        "ref_id": node.get(W_NS + "id")})
        elif child.tag == W_NS + "tbl":
            rows = [c for c in child if c.tag == W_NS + "tr"]
            for row_index, row in enumerate(rows):
                cells = [c for c in row if c.tag == W_NS + "tc"]
                for col_index, cell in enumerate(cells):
                    records.append({
                        "id": "t.r%dc%d" % (row_index, col_index),
                        "kind": "table_cell", "text": _w_text(cell),
                        "part": "body", "paragraph_index": block_index,
                        "ref_id": None})
    return records


def _extract_docx(raw_bytes, options):
    """WordprocessingML, including the parts python-docx does not expose.

    `docx` is imported inside the function body, so a machine without it
    keeps every other adapter and every other command working and only this
    one refuses, by name and with its install line.
    """
    try:
        import docx
    except ImportError:
        raise _Refusal("source.dependency_missing",
                       "the docx adapter needs python-docx, which is not "
                       "installed. It is optional and every other command is "
                       "unaffected. To enable docx import, %s"
                       % _PYTHON_DOCX_INSTALL)

    try:
        archive = zipfile.ZipFile(io.BytesIO(raw_bytes))
    except zipfile.BadZipFile:
        if raw_bytes[:8] == _OLE_SIGNATURE:
            raise _Refusal("source.encrypted",
                           "encrypted DOCX: no unauthenticated structure")
        raise _Refusal("source.malformed_input",
                       "malformed package: not a readable zip")

    unsupported = []
    with archive as zf:
        # Preflight every member through the one seam's checks before any
        # third-party reader is handed the archive, so a bomb in a part this
        # adapter never names is still refused rather than decompressed by
        # python-docx on its way to building a Document.
        for name in zf.namelist():
            error = _zip_member_error(zf, name, options)
            if error is not None:
                raise _Refusal(error["code"], error["message"])

        raw_document, error = _read_zip_part(zf, "word/document.xml", options)
        if error is not None:
            raise _Refusal(error["code"], error["message"])
        _root, error = _parse_xml_safely(raw_document, options)
        if error is not None:
            raise _Refusal(error["code"], error["message"])

        headers, tail, error = _docx_extra_parts(zf, options)
        if error is not None:
            raise _Refusal(error["code"], error["message"])

        if any(name.startswith("word/embeddings/") for name in zf.namelist()):
            unsupported.append({"code": "source.unsupported",
                                "message": "embedded OLE object: opaque "
                                           "binary"})

    document = docx.Document(io.BytesIO(raw_bytes))
    records = headers + _docx_body_records(document.element.body,
                                           unsupported) + tail

    if not records:
        raise _Refusal("source.unsupported",
                       "the document part parsed but carries no text-bearing "
                       "structure; nothing was written")

    lines = []
    locators = []
    reading_order = []
    for record in records:
        lines.append(record["text"])
        locators.append({
            "id": record["id"],
            "kind": record["kind"],
            "body": {
                "medium": "docx",
                "part": record["part"],
                "paragraph_index": record["paragraph_index"],
                "ref_id": record["ref_id"],
            },
            "_line": len(lines),
        })
        reading_order.append(record["id"])
    return "\n".join(lines) + "\n", locators, reading_order, unsupported


_PYTHON_PPTX_INSTALL = "run: pip install python-pptx==1.0.2"


def _pptx_slide_order(zf, options):
    """The slide part names in reading order, or `(None, error)`.

    Reading order is the order of `p:sldId` children in `p:sldIdLst` inside
    `ppt/presentation.xml`, resolved through
    `ppt/_rels/presentation.xml.rels`. It is NOT the numeric order of the
    `slideN.xml` filenames: PowerPoint keeps a slide's original part name when
    a deck is reordered, so sorting filenames produces the wrong reading order
    with no visible symptom at all. The `pptx-reordered-slides` gold case is
    the one that goes red if that is ever done.
    """
    raw, error = _read_zip_part(zf, "ppt/presentation.xml", options)
    if error is not None:
        return None, error
    presentation, error = _parse_xml_safely(raw, options)
    if error is not None:
        return None, error
    raw_rels, error = _read_zip_part(zf, "ppt/_rels/presentation.xml.rels",
                                     options)
    if error is not None:
        return None, error
    rels, error = _parse_xml_safely(raw_rels, options)
    if error is not None:
        return None, error

    targets = {}
    for node in rels.iter(PKG_REL_NS + "Relationship"):
        targets[node.get("Id")] = node.get("Target")

    ordered = []
    for slide_id in presentation.iter(P_NS + "sldId"):
        target = targets.get(slide_id.get(R_NS + "id"))
        if target is None:
            continue
        ordered.append(posixpath.normpath(posixpath.join("ppt", target)))
    return ordered, None


def _extract_pptx(raw_bytes, options):
    """PresentationML: on-slide text and speaker notes, slide by slide.

    Two things about this adapter are worth stating where they cannot be
    missed. Slide order comes from the presentation part, never from sorted
    filenames, for the reason `_pptx_slide_order` gives. And
    `slide.part.partname` on a loaded deck reports the slide's POSITION, not
    the archive member it was read from, so it cannot be used to join the
    resolved order back to python-pptx's slides; the join is positional, and
    the resolved order is used to fix the count and to prove the ordering
    contract holds.

    The derived Markdown carries one `## Slide N` heading per slide, then one
    line per on-slide shape, then one `> ` quoted line per speaker note. The
    heading is presentation, not content: it has no locator and no span, and
    it should stay that way, because a citation into a deck names a shape or a
    note and never the divider a reader was given to see where a slide began.
    """
    try:
        import pptx
    except ImportError:
        raise _Refusal("source.dependency_missing",
                       "the pptx adapter needs python-pptx, which is not "
                       "installed. It is optional and every other command is "
                       "unaffected. To enable pptx import, %s"
                       % _PYTHON_PPTX_INSTALL)

    try:
        archive = zipfile.ZipFile(io.BytesIO(raw_bytes))
    except zipfile.BadZipFile:
        raise _Refusal("source.malformed_input", "malformed/truncated PPTX")

    with archive as zf:
        for name in zf.namelist():
            error = _zip_member_error(zf, name, options)
            if error is not None:
                raise _Refusal(error["code"], error["message"])
        ordered, error = _pptx_slide_order(zf, options)
        if error is not None:
            raise _Refusal(error["code"], error["message"])

    try:
        presentation = pptx.Presentation(io.BytesIO(raw_bytes))
        slides = list(presentation.slides)
    except _Refusal:
        raise
    except Exception:
        raise _Refusal("source.malformed_input", "malformed/truncated PPTX")

    if len(ordered) != len(slides):
        raise _Refusal("source.malformed_input",
                       "the presentation part lists %d slides but the package "
                       "carries %d; the deck is inconsistent"
                       % (len(ordered), len(slides)))

    lines = []
    locators = []
    reading_order = []
    unsupported = []

    for slide_number, slide in enumerate(slides, start=1):
        lines.append("## Slide %d" % slide_number)
        emitted = 0
        for shape_index, shape in enumerate(slide.shapes):
            if not shape.has_text_frame:
                continue
            text = shape.text_frame.text
            if not text.strip():
                continue
            lines.append(text)
            locator_id = "s%d.%d" % (slide_number, shape_index)
            locators.append({
                "id": locator_id,
                "kind": "slide",
                "body": {"medium": "pptx", "slide": slide_number,
                         "shape_index": shape_index, "notes": False},
                "_line": len(lines),
            })
            reading_order.append(locator_id)
            emitted += 1
        # `has_notes_slide` is the guard, not a try/except: a deck saved with
        # no notes carries no notesSlide part at all, and touching
        # `notes_slide` on one raises rather than returning empty.
        if slide.has_notes_slide:
            note_text = slide.notes_slide.notes_text_frame.text
            if note_text.strip():
                lines.append("> " + note_text)
                locator_id = "s%d.n0" % slide_number
                locators.append({
                    "id": locator_id,
                    "kind": "notes",
                    "body": {"medium": "pptx", "slide": slide_number,
                             "shape_index": 0, "notes": True},
                    "_line": len(lines),
                })
                reading_order.append(locator_id)
                emitted += 1
        if not emitted:
            unsupported.append({
                "code": "source.unsupported",
                "message": "slide %d: media-only slide, no text-bearing shape"
                           % slide_number})

    if not locators:
        raise _Refusal("source.unsupported",
                       "media-only deck: no text-bearing shape")
    return "\n".join(lines) + "\n", locators, reading_order, unsupported


# ---------------------------------------------------------------------------
# Roster item 3: remote capture (plan 14C-04).
#
# D-04: a remote source binds as a captured snapshot, never as a URL. The
# whole binding model runs on fingerprints and a URL has no stable bytes, so
# the capture is what is fingerprinted and the URL plus the capture timestamp
# are recorded beside it as provenance. That is what keeps a citation stable
# when a page is edited, keeps bound material readable with the network
# unplugged, and makes a changed origin a detectable state rather than a
# silently broken citation.
#
# Text fetched from a remote origin is DATA. Nothing in this module builds a
# prompt, a tool call, or a shell command from it, and a later phase that
# hands this text to a model does so knowing it is third-party authored
# (T-14C-25).

MAX_REDIRECTS = 5

USER_AGENT = "itembank-source-adapter/1.0 (+local, no telemetry)"

SNAPSHOT_DIRNAME = REMOTE_DIRNAME
SNAPSHOT_CACHE_DIRNAME = "cache"

# Advisory report states for `recheck_origin`. These are NOT journal entry
# states and NOT members of `SOURCE_ADAPTER_CODES`; the two vocabularies must
# never be confused, because a `source.*` code names a refusal and one of
# these names a fact about a remote origin that changed nothing.
RECHECK_STATES = ("origin_unchanged", "origin_changed", "origin_unreachable")

# Mirrors the `source` group's defaults in `schemas/settings.schema.json`,
# which is the source of truth; `check_option_defaults_match_schema` fails if
# the two ever drift. They are duplicated here so a direct call with no
# options is governed by the same restrictive defaults a surface would load.
SOURCE_OPTION_DEFAULTS = {
    "bind_policy": "approve_before_bind",
    "snapshot_storage": "auto",
    "snapshot_inline_max_bytes": 8388608,
    "allow_private_origins": False,
    "fetch_timeout_seconds": 15,
    "max_input_bytes": MAX_INPUT_BYTES_DEFAULT,
}

WEB_BLOCK_TAGS = ("h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "blockquote",
                  "pre", "figcaption", "dt", "dd", "td", "th")

# Chrome that a reader skips and a citation should never land in. readability
# strips most of it; a navigation bar sometimes survives its summary, so the
# skip list is applied here as well rather than trusted to the library.
WEB_SKIP_TAGS = ("nav", "footer", "aside", "script", "style", "noscript",
                 "form")

_READABILITY_INSTALL = "run: pip install readability-lxml==0.8.4.1"

_META_CHARSET = re.compile(rb"""charset\s*=\s*["']?([A-Za-z0-9_.:-]+)""")


def _origin_of(url):
    """Scheme, host, and port, the triple that decides whether a redirect
    left the origin it started on.

    A deliberate duplicate of `surfaces/update.py`'s function of the same
    name, and it must stay in step with it. It is copied rather than imported
    because `source_adapters` is a model-tier module that no surface-tier
    import should reach up into: `surfaces/update.py` pulls in the whole
    updater, its settings, and its manifest schema, none of which a source
    adapter has any business loading to compare three strings.
    """
    parts = urllib.parse.urlsplit(url)
    return (parts.scheme, (parts.hostname or "").lower(), parts.port)


class SchemeLockedRedirectHandler(urllib.request.HTTPRedirectHandler):
    """`AuthStrippingRedirectHandler` plus a scheme lock.

    Two hardenings, both against a header a remote server controls. The
    scheme lock refuses a redirect to anything that is not http or https, so
    a `file:` or `ftp:` Location cannot turn a page fetch into a local file
    read. The Authorization strip is copied from `surfaces/update.py`, which
    carries it because the defect already happened once (CR-01, a token
    leaked onto GitHub's separately-hosted CDN origin); the strip is sticky,
    because each hop's Request is built from the previous hop's headers.

    `super()` still decides whether a redirect is legal at all. This subclass
    only narrows, including the hop cap: stdlib's own `max_redirections` is
    10, and `MAX_REDIRECTS` lowers it rather than leaving the constant
    declared and unenforced.
    """

    max_redirections = MAX_REDIRECTS

    def _refuse_foreign_scheme(self, req, headers):
        """stdlib checks the redirect scheme itself, in `http_error_302`,
        before `redirect_request` is ever called, and its allowed set is
        http, https, AND ftp. So the scheme lock has to sit here rather than
        in `redirect_request`: by the time `redirect_request` runs, a
        refusable target has either already been refused by stdlib with its
        own message or is an ftp URL stdlib was content to follow. Measured,
        not assumed: an unpatched run against the fixture's `file:` redirect
        came back as stdlib's HTTPError 302 and never entered the subclass.
        """
        target = headers.get("location") or headers.get("uri") or ""
        resolved = urllib.parse.urljoin(req.full_url, target)
        scheme = urllib.parse.urlsplit(resolved).scheme.lower()
        if scheme and scheme not in ("http", "https"):
            raise urllib.error.URLError(
                "redirect refused: the origin redirected to a %s: URL, and "
                "only http and https are followed" % scheme)

    def http_error_302(self, req, fp, code, msg, headers):
        self._refuse_foreign_scheme(req, headers)
        return urllib.request.HTTPRedirectHandler.http_error_302(
            self, req, fp, code, msg, headers)

    # stdlib binds 301, 303, 307, and 308 as aliases of its own function on
    # the base class, so overriding 302 alone would leave four unlocked.
    http_error_301 = http_error_302
    http_error_303 = http_error_302
    http_error_307 = http_error_302
    http_error_308 = http_error_302

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        new = urllib.request.HTTPRedirectHandler.redirect_request(
            self, req, fp, code, msg, headers, newurl)
        if new is None:
            return None
        if _origin_of(req.full_url) != _origin_of(newurl):
            for key in list(new.headers):
                if key.lower() == "authorization":
                    del new.headers[key]
            for key in list(new.unredirected_hdrs):
                if key.lower() == "authorization":
                    del new.unredirected_hdrs[key]
        return new


def _host_is_private(host):
    """True when `host` resolves to any address a fetch should not reach:
    loopback, private, link-local, reserved, multicast, or unspecified. An
    unresolvable host is also True, because an unresolvable name is refused
    rather than attempted.

    Best effort, and deliberately not called a security boundary. It resolves
    once and does not pin the resolved address for the connection, so DNS
    rebinding is open; `14C-RESEARCH.md` judges closing that gap
    disproportionate for a single-user local product whose recorded threat
    model has no attacker on the machine. The check exists because it is
    cheap and correct for the real case, which is an agent handed a URL that
    happens to point at the learner's own network.
    """
    if not host:
        return True
    try:
        infos = socket.getaddrinfo(host, None)
    except (socket.gaierror, socket.error, UnicodeError):
        return True
    for info in infos:
        address = info[4][0]
        try:
            parsed = ipaddress.ip_address(address.split("%")[0])
        except ValueError:
            return True
        if (parsed.is_loopback or parsed.is_private or parsed.is_link_local
                or parsed.is_reserved or parsed.is_multicast
                or parsed.is_unspecified):
            return True
    return False


def _fetch_url(url, options, conditional=None):
    """One hardened GET. Returns
    `(raw_bytes, content_type, etag, last_modified, status)` and never
    raises: every transport failure becomes a typed `_Refusal`.

    `conditional` is an optional `(header_name, value)` pair for the
    `source recheck` path; a 304 comes back with `status` 304 and empty
    bytes.

    Every `INTEGRATE` row of `COVERAGE.md` surface 1 is here and every
    `OPT-OUT` row is deliberately absent. No cookie jar, no credential, no
    client certificate, no non-GET method, no range request.
    """
    options = _options(options)
    parts = urllib.parse.urlsplit(url)
    scheme = (parts.scheme or "").lower()
    if scheme not in ("http", "https"):
        raise _Refusal("source.redirect_refused",
                       "%s: is not a fetchable scheme; only http and https "
                       "are fetched" % (scheme or "(none)"))
    if not options["allow_private_origins"] and _host_is_private(parts.hostname):
        raise _Refusal("source.origin_refused",
                       "the host %s resolves to a private, loopback, or "
                       "link-local address, which is refused by default. Set "
                       "source.allow_private_origins to true in itembank.json "
                       "to allow it." % (parts.hostname or url))

    cap = options["max_input_bytes"]
    opener = urllib.request.build_opener(SchemeLockedRedirectHandler())
    request = urllib.request.Request(url, method="GET")
    request.add_header("User-Agent", USER_AGENT)
    if conditional:
        request.add_header(conditional[0], conditional[1])
    try:
        with opener.open(request,
                          timeout=options["fetch_timeout_seconds"]) as response:
            declared = response.headers.get("Content-Length")
            if declared is not None and declared.isdigit() and \
                    int(declared) > cap:
                raise _Refusal("source.oversized",
                               "the origin declares %s bytes, over the "
                               "%d-byte intake cap; nothing was fetched"
                               % (declared, cap))
            # A chunked response declares no length, so the read itself is
            # bounded: one byte over the cap is enough to know it is over.
            raw = response.read(cap + 1)
            if len(raw) > cap:
                raise _Refusal("source.oversized",
                               "the origin returned more than the %d-byte "
                               "intake cap; nothing was captured" % cap)
            return (raw, response.headers.get("Content-Type"),
                    response.headers.get("ETag"),
                    response.headers.get("Last-Modified"),
                    getattr(response, "status", 200))
    except _Refusal:
        raise
    except urllib.error.HTTPError as exc:
        if exc.code == 304:
            return b"", None, None, None, 304
        raise _Refusal("source.fetch_failed",
                       "the origin returned HTTP %d for %s" % (exc.code, url))
    except urllib.error.URLError as exc:
        reason = getattr(exc, "reason", exc)
        if isinstance(reason, socket.timeout) or \
                "timed out" in str(reason).lower():
            raise _Refusal("source.fetch_failed",
                           "the fetch of %s timed out after %s seconds"
                           % (url, options["fetch_timeout_seconds"]))
        if "redirect refused" in str(reason):
            raise _Refusal("source.redirect_refused", str(reason))
        raise _Refusal("source.fetch_failed",
                       "the fetch of %s failed: %s" % (url, reason))
    except (socket.timeout, TimeoutError):
        raise _Refusal("source.fetch_failed",
                       "the fetch of %s timed out after %s seconds"
                       % (url, options["fetch_timeout_seconds"]))
    except OSError as exc:
        raise _Refusal("source.fetch_failed",
                       "the fetch of %s failed: %s" % (url, exc))


def _decode_html(raw, content_type):
    """Return `(text, exact)`. `exact` is False when the bytes were decoded
    by a replacing fallback, which is what makes the sidecar record
    `confidence` `medium` rather than `high` for that capture."""
    charset = None
    if content_type:
        match = re.search(r"charset=([A-Za-z0-9_.:-]+)", content_type)
        if match:
            charset = match.group(1)
    if charset is None:
        match = _META_CHARSET.search(raw[:4096])
        if match:
            charset = match.group(1).decode("ascii", "replace")
    for candidate in ([charset] if charset else []) + ["utf-8"]:
        try:
            return raw.decode(candidate), True
        except (UnicodeDecodeError, LookupError):
            continue
    return raw.decode("utf-8", errors="replace"), False


def _css_selector(element, root):
    """A CSS selector from the readable fragment's root to `element`, built
    from tag names, ids, and nth-of-type positions. An index-free path would
    not identify a repeated block, and an XPath index alone breaks on any
    shifted sibling; this is the middle ground the `body_web` row asks for."""
    steps = []
    node = element
    while node is not None and node is not root:
        parent = node.getparent()
        tag = str(node.tag)
        step = tag
        node_id = node.get("id")
        if node_id:
            step = "%s#%s" % (tag, node_id)
        elif parent is not None:
            same = [child for child in parent if str(child.tag) == tag]
            if len(same) > 1:
                step = "%s:nth-of-type(%d)" % (tag, same.index(node) + 1)
        steps.append(step)
        node = parent
    steps.reverse()
    return " > ".join(steps) if steps else str(element.tag)


def _readable_html(raw, content_type, options):
    """Readable text from an HTML document, one record per block-level
    element, each with a CSS selector and a quote carrying prefix and
    suffix.

    Returns `(records, exact_decode)`. A record is
    `{"text", "css_selector", "prefix", "suffix"}`.
    """
    try:
        from readability import Document
        from lxml import html as lxml_html
    except ImportError:
        raise _Refusal("source.dependency_missing",
                       "the web adapter needs readability-lxml, which is not "
                       "installed. It is optional and every other command is "
                       "unaffected. To enable web capture, %s"
                       % _READABILITY_INSTALL)

    text, exact = _decode_html(raw, content_type)
    try:
        summary = Document(text).summary()
        root = lxml_html.fromstring(summary)
    except Exception:
        raise _Refusal("source.malformed_input",
                       "the fetched document could not be parsed as HTML")

    blocks = []
    for element in root.iter():
        tag = str(element.tag).lower() if isinstance(element.tag, str) else ""
        if tag not in WEB_BLOCK_TAGS:
            continue
        skip = False
        ancestor = element.getparent()
        while ancestor is not None:
            ancestor_tag = str(ancestor.tag).lower() \
                if isinstance(ancestor.tag, str) else ""
            if ancestor_tag in WEB_SKIP_TAGS or ancestor_tag in WEB_BLOCK_TAGS:
                skip = True
                break
            ancestor = ancestor.getparent()
        if skip:
            continue
        block_text = " ".join(element.text_content().split())
        if not block_text:
            continue
        blocks.append((element, block_text))

    if not blocks:
        if "<script" in text.lower():
            raise _Refusal("source.unsupported",
                           "no readable text: the page renders its content "
                           "with JavaScript")
        raise _Refusal("source.unsupported",
                       "no readable text: malformed document")

    texts = [block_text for _element, block_text in blocks]
    records = []
    for index, (element, block_text) in enumerate(blocks):
        before = " ".join(texts[:index])
        after = " ".join(texts[index + 1:])
        records.append({
            "text": block_text,
            "css_selector": _css_selector(element, root),
            "prefix": before[-32:],
            "suffix": after[:32],
        })
    return records, exact


def _extract_web(raw_bytes, options):
    """A fetched HTML page, one locator per readable block.

    The locator carries a CSS selector to its containing block plus a text
    quote with prefix and suffix, so a citation survives a minor DOM change
    rather than breaking on a shifted index, and so two identical sentences
    on one page stay distinguishable.
    """
    options = _options(options)
    records, exact = _readable_html(raw_bytes, options.get("content_type"),
                                    options)
    lines = []
    locators = []
    reading_order = []
    for index, record in enumerate(records):
        lines.append(record["text"])
        locator_id = "w.%d" % index
        locators.append({
            "id": locator_id,
            "kind": "block",
            "body": {
                "medium": "web",
                "css_selector": record["css_selector"],
                "text_quote": {"exact": record["text"],
                               "prefix": record["prefix"],
                               "suffix": record["suffix"]},
            },
            "_line": len(lines),
            "_exact_decode": exact,
        })
        reading_order.append(locator_id)
    return "\n".join(lines) + "\n", locators, reading_order, []


# ---------------------------------------------------------------------------
# Roster item 4: transcript intake (plan 14C-05). This adapter imports nothing
# outside the standard library, so it has no lazy-import guard and no
# `source.dependency_missing` path. Do not add one for symmetry with the
# others: its absence is the phase's cleanest proof that the core loop
# degrades and never blocks.

CUE_ARROW = "-->"

VTT_SKIP_BLOCKS = ("NOTE", "STYLE", "REGION")

# One regex for SRT and WebVTT, because exported caption files are routinely
# renamed between the two extensions without being reformatted, and a parser
# that accepts only its own separator silently rejects half of a learner's
# real files. The hour group is optional: a WebVTT timestamp may be plain
# MM:SS.mmm, and requiring HH: is the single most likely way this adapter
# would fail on real material rather than on fixtures. Every quantifier is
# bounded except the hour's, and there is no nested quantifier and no
# alternation inside a repeated group, so it cannot backtrack catastrophically
# (T-14C-31).
TIMESTAMP_RE = re.compile(r"(?:(\d+):)?(\d{1,2}):(\d{2})[.,](\d{1,3})")

_BRACKETED_RE = re.compile(r"^\[\s*((?:\d+:)?\d{1,2}:\d{2}(?:[.,]\d{1,3})?)"
                           r"\s*\]\s*(.*)$")


def _timestamp_to_ms(text):
    """Integer milliseconds, or None when `text` carries no timestamp.

    The fractional part is padded to three digits rather than read as written:
    `1:02.5` is a half second, which is 500 milliseconds and not 5. Getting
    that wrong is a silent hundred-fold error in every cue of the file.
    """
    if not text:
        return None
    match = TIMESTAMP_RE.search(text)
    if not match:
        return None
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2))
    seconds = int(match.group(3))
    fraction = (match.group(4) + "00")[:3]
    return ((hours * 3600 + minutes * 60 + seconds) * 1000) + int(fraction)


def _ms_to_stamp(total_ms):
    seconds, _remainder = divmod(int(total_ms), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return "[%02d:%02d:%02d]" % (hours, minutes, seconds)


def _cue_from_block(lines, block_number, unsupported):
    """One cue dict from one blank-line-separated block, or None with a named
    entry appended to `unsupported`."""
    timing_index = None
    for index, line in enumerate(lines):
        if CUE_ARROW in line:
            timing_index = index
            break
    if timing_index is None:
        unsupported.append({
            "code": "source.unsupported",
            "message": "cue %d: no timestamp line" % block_number})
        return None
    left, _arrow, right = lines[timing_index].partition(CUE_ARROW)
    start_ms = _timestamp_to_ms(left)
    # Only up to the second timestamp: a WebVTT timing line's trailing cue
    # settings are presentation, not content, and `search` stops at the first
    # match in the remainder anyway.
    end_ms = _timestamp_to_ms(right)
    if start_ms is None or end_ms is None:
        unsupported.append({
            "code": "source.unsupported",
            "message": "cue %d: no timestamp line" % block_number})
        return None
    if end_ms < start_ms:
        unsupported.append({
            "code": "source.unsupported",
            "message": "cue %d: end timestamp precedes start timestamp"
                       % block_number})
        return None
    text = " ".join(line.strip() for line in lines[timing_index + 1:]
                    if line.strip())
    return {"start_ms": start_ms, "end_ms": end_ms, "text": text}


def _blocks(text):
    blocks = []
    current = []
    for line in text.split("\n"):
        if line.strip():
            current.append(line)
        elif current:
            blocks.append(current)
            current = []
    if current:
        blocks.append(current)
    return blocks


def _parse_srt(text):
    """SRT cues. A leading numeric index line is tolerated and its absence is
    tolerated too, because half the files that carry SRT timing lines were
    written by something that did not number them."""
    cues = []
    unsupported = []
    for block_number, lines in enumerate(_blocks(text), start=1):
        if lines and lines[0].strip().isdigit() and \
                len(lines) > 1 and CUE_ARROW in lines[1]:
            lines = lines[1:]
        cue = _cue_from_block(lines, block_number, unsupported)
        if cue is not None:
            cues.append(cue)
    return cues, unsupported


def _parse_vtt(text):
    """WebVTT cues. NOTE, STYLE, and REGION blocks are recognized and skipped
    without breaking the cue stream, and each one is recorded in `unsupported`
    so the loss is reported rather than silent."""
    cues = []
    unsupported = []
    block_number = 0
    for lines in _blocks(text):
        first = lines[0].strip()
        if first.upper().startswith("WEBVTT"):
            continue
        keyword = first.split()[0].upper() if first.split() else ""
        if keyword in VTT_SKIP_BLOCKS:
            unsupported.append({
                "code": "source.unsupported",
                "message": "skipped a %s block" % keyword})
            continue
        block_number += 1
        if len(lines) > 1 and CUE_ARROW not in first and CUE_ARROW in lines[1]:
            # A cue identifier line before the timing line.
            lines = lines[1:]
        cue = _cue_from_block(lines, block_number, unsupported)
        if cue is not None:
            cues.append(cue)
    return cues, unsupported


def _parse_plain_timestamps(text):
    """Hand-typed lines that begin `[HH:MM:SS]`.

    A cue's `end_ms` is the next cue's `start_ms`, and the last cue's `end_ms`
    equals its own `start_ms`. A final line has no known duration, and
    inventing one would put a wrong number into a citation; an end equal to
    the start is the honest zero-length answer. The sidecar records
    `confidence` `medium` for this shape for the same reason, because these
    ends are inferred rather than declared.

    A line with no bracketed timestamp joins the preceding cue's text, so a
    wrapped paragraph does not become a lost line.
    """
    cues = []
    unsupported = []
    for line in text.split("\n"):
        match = _BRACKETED_RE.match(line)
        if match is None:
            if line.strip() and cues:
                cues[-1]["text"] = (cues[-1]["text"] + " " + line.strip()).strip()
            continue
        start_ms = _timestamp_to_ms(match.group(1) if "." in match.group(1)
                                    or "," in match.group(1)
                                    else match.group(1) + ".000")
        if start_ms is None:
            continue
        cues.append({"start_ms": start_ms, "end_ms": start_ms,
                     "text": match.group(2).strip()})
    for index in range(len(cues) - 1):
        cues[index]["end_ms"] = cues[index + 1]["start_ms"]
    return cues, unsupported


def _extract_transcript(raw_bytes, options):
    """A learner-supplied SRT, WebVTT, or bracketed-timestamp transcript.

    The shape is detected from the content and never from a filename, because
    a caption file renamed between `.srt` and `.vtt` is the ordinary case
    rather than the exotic one.

    Every locator carries integer `start_ms` and `end_ms`, so a citation names
    a moment rather than a line number. That is the whole reason roster item 4
    is sequenced ahead of ASR: when a speech backend eventually arrives it
    produces cues, not a new locator shape and not a new sidecar field.
    """
    try:
        text = raw_bytes.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise _Refusal("source.malformed_input",
                       "the transcript is not valid UTF-8 at byte offset %d; "
                       "no derived source was produced" % exc.start)
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    stripped = [line for line in text.split("\n") if line.strip()]
    first = stripped[0].strip().upper() if stripped else ""
    if first.startswith("WEBVTT"):
        cues, unsupported = _parse_vtt(text)
        inferred_ends = False
    elif CUE_ARROW in text:
        cues, unsupported = _parse_srt(text)
        inferred_ends = False
    elif any(_BRACKETED_RE.match(line) for line in text.split("\n")):
        cues, unsupported = _parse_plain_timestamps(text)
        inferred_ends = True
    else:
        raise _Refusal("source.unsupported", "no timestamped cue found")

    if not cues:
        raise _Refusal("source.unsupported", "no timestamped cue found")

    lines_out = []
    locators = []
    reading_order = []
    for cue_index, cue in enumerate(cues):
        lines_out.append("%s %s" % (_ms_to_stamp(cue["start_ms"]),
                                    cue["text"]))
        locator_id = "c.%d" % cue_index
        locators.append({
            "id": locator_id,
            "kind": "cue",
            "body": {"medium": "transcript", "cue_index": cue_index,
                     "start_ms": cue["start_ms"], "end_ms": cue["end_ms"]},
            "_line": len(lines_out),
            "_inferred_ends": inferred_ends,
        })
        reading_order.append(locator_id)
    return "\n".join(lines_out) + "\n", locators, reading_order, unsupported


# ---------------------------------------------------------------------------
# Roster item 6: OCR (plan 14C-06). CONTEXT.md's instruction is exact: wrap the
# existing `ocr` skill, do not write a second OCR path. This adapter therefore
# names no endpoint, encodes nothing, and carries no transcription prompt; all
# three live in `scripts/ocr_lib.py` and stay there.

OCR_NO_TEXT_SENTINEL = "[no text]"

# Magic signature to filename suffix. The suffix matters because the bridge
# takes a path and a vision model may key on the extension; the signature
# matters because a caller-supplied extension is not evidence of anything.
OCR_IMAGE_SUFFIXES = (
    (b"\x89PNG\r\n\x1a\n", ".png"),
    (b"\xff\xd8\xff", ".jpg"),
    (b"RIFF", ".webp"),
    (b"GIF87a", ".gif"),
    (b"GIF89a", ".gif"),
    (b"BM", ".bmp"),
    (b"II*\x00", ".tif"),
    (b"MM\x00*", ".tif"),
)


def _ocr_bridge():
    """The one OCR implementation in this repository, imported lazily.

    `scripts/` carries no `__init__.py`, so the working import form is a
    `sys.path` entry plus a flat `import ocr_lib`. Verified on this tree
    rather than assumed. Returning the module object rather than the function
    is deliberate: a test stubs `ocr_lib.ocr_image` on the module, and a
    function captured at import time would not see the stub.
    """
    import sys as _sys
    scripts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "scripts")
    if scripts_dir not in _sys.path:
        _sys.path.insert(0, scripts_dir)
    import ocr_lib
    return ocr_lib


def _image_suffix(raw_bytes):
    for signature, suffix in OCR_IMAGE_SUFFIXES:
        if raw_bytes.startswith(signature):
            return suffix
    return None


def _extract_ocr(raw_bytes, options):
    """A photographed or scanned page, transcribed by the learner's own local
    vision model through the `ocr` skill's bridge.

    `bbox` and `confidence` are None on every locator because
    `scripts/ocr_lib.py` measures neither: it returns flat transcribed text
    with no coordinates and no per-line score. The frozen schema types both
    fields as null and nothing else, so a later change cannot quietly start
    inventing geometry; a structured-output OCR mode that really measures
    where a line sat is a `schema_version` bump with a recorded migration,
    never a loosened type. A citation into an OCR source names the page.

    The sidecar envelope confidence is `low` for every OCR source. A vision
    model transcribing a photograph is the least reliable extraction in the
    registry and a citation into it should say so.
    """
    import tempfile

    try:
        ocr_lib = _ocr_bridge()
    except ImportError:
        raise _Refusal("source.backend_unconfigured",
                       "the OCR bridge scripts/ocr_lib.py could not be "
                       "imported, so no page can be transcribed. Every other "
                       "source adapter is unaffected.")

    suffix = _image_suffix(raw_bytes)
    if suffix is None:
        raise _Refusal("source.malformed_input",
                       "the file is not a recognized image; the accepted "
                       "formats are PNG, JPEG, WebP, GIF, BMP, and TIFF. "
                       "Nothing was sent to the vision model.")

    workdir = tempfile.mkdtemp(prefix="itembank-ocr-")
    try:
        image_path = os.path.join(workdir, "page" + suffix)
        with open(image_path, "wb") as fh:
            fh.write(raw_bytes)
        try:
            text = ocr_lib.ocr_image(image_path)
        except RuntimeError as exc:
            message = str(exc)
            if message.startswith("no Ollama server reachable"):
                raise _Refusal(
                    "source.backend_unconfigured",
                    "the local OCR bridge could not reach an Ollama server. "
                    "Start Ollama, or set OLLAMA_HOST, then run the import "
                    "again. Every other source adapter is unaffected.")
            if "not found on" in message:
                raise _Refusal(
                    "source.backend_unconfigured",
                    "the local OCR bridge reached Ollama but the vision model "
                    "is not installed. Pull the model named in the error, "
                    "then run the import again.")
            raise _Refusal("source.fetch_failed", message)
        except _Refusal:
            raise
        except Exception:
            # A future change to the bridge that raises a different class
            # still cannot propagate out of an adapter.
            raise _Refusal("source.internal_error",
                           "the OCR bridge failed in an unexpected way; "
                           "nothing was written")
    finally:
        # A decoded image left in a temp directory is an untracked copy of
        # learner material. This runs on every path, including every refusal.
        try:
            shutil.rmtree(workdir, ignore_errors=True)
        except Exception:
            pass

    if text.strip() == OCR_NO_TEXT_SENTINEL:
        # The bridge's own prompt promises this exact string for an image with
        # no text. Emitting it as content would put the literal "[no text]"
        # into a learner's source Markdown as if a human had written it.
        raise _Refusal("source.unsupported", "no text found in the image")

    lines_out = []
    locators = []
    reading_order = []
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        lines_out.append(stripped)
        locator_id = "o1.%d" % (len(lines_out) - 1)
        locators.append({
            "id": locator_id,
            "kind": "image_region",
            # One image is one page. A multi-page scan is imported one image
            # at a time; joining them is a later phase's concern.
            "body": {"medium": "ocr", "page": 1, "bbox": None,
                     "confidence": None},
            "_line": len(lines_out),
        })
        reading_order.append(locator_id)

    if not locators:
        raise _Refusal("source.unsupported", "no text found in the image")
    return "\n".join(lines_out) + "\n", locators, reading_order, []


# ---------------------------------------------------------------------------
# Roster item 7: EPUB import (plan 14C-07). No third-party dependency at all,
# and therefore no lazy-import guard and no `source.dependency_missing` path.
# That is a recorded decision, not an omission: D-14C-2 parks `ebooklib` on an
# explicit Weibao AGPL decision, so the container is read with stdlib zipfile
# and xml.etree through the same hardened seam DOCX and PPTX read through.

EPUB_CONTAINER_PATH = "META-INF/container.xml"
EPUB_ENCRYPTION_PATH = "META-INF/encryption.xml"

EPUB_BLOCK_TAGS = ("h1", "h2", "h3", "h4", "h5", "h6", "p", "li",
                   "blockquote", "pre")

EPUB_HEADING_TAGS = ("h1", "h2", "h3", "h4", "h5", "h6")

# Tags carrying text this adapter knowingly does not emit. Each distinct one
# encountered becomes a line in the sidecar's unsupported list, which is the
# import direction's semantic loss report that PORT-02 asks every interchange
# adapter to carry.
EPUB_SKIPPED_TAGS = ("table", "figure", "figcaption", "aside")


def _local_tag(element):
    tag = element.tag
    if not isinstance(tag, str):
        return ""
    return tag.rsplit("}", 1)[-1].lower()


def _epub_container_root(zf, options):
    """The package document's archive path and its containing directory.

    `META-INF/container.xml` names the OPF with a `rootfile` `full-path`
    attribute. Hard-coding `OEBPS/content.opf` works on most books and fails
    on the rest silently, with a file-not-found that reads like a malformed
    EPUB. The directory is returned beside the path because every manifest
    `href` is relative to the OPF's own directory, and joining them against
    the archive root instead is the second most likely silent failure here.
    """
    if EPUB_CONTAINER_PATH not in zf.namelist():
        raise _Refusal("source.malformed_input",
                       "malformed EPUB: no META-INF/container.xml")
    raw, error = _read_zip_part(zf, EPUB_CONTAINER_PATH, options)
    if error is not None:
        raise _Refusal(error["code"], error["message"])
    container, error = _parse_xml_safely(raw, options)
    if error is not None:
        raise _Refusal(error["code"], error["message"])
    for node in container.iter():
        if _local_tag(node) != "rootfile":
            continue
        full_path = node.get("full-path")
        if full_path:
            return full_path, posixpath.dirname(full_path)
    raise _Refusal("source.malformed_input",
                   "malformed EPUB: container names no package document")


def _epub_spine_order(package, opf_dir, unsupported):
    """`(spine_idref, resolved_href)` pairs in spine order.

    Spine order is the order of `itemref` children of the `spine` element,
    each naming a manifest item by `idref`. Filename order and manifest order
    both look plausible on a tidy book and are both wrong, which is exactly
    what `epub-spine-out-of-order` exists to catch.
    """
    hrefs = {}
    for node in package.iter():
        if _local_tag(node) != "item":
            continue
        item_id = node.get("id")
        href = node.get("href")
        if item_id and href:
            hrefs[item_id] = posixpath.normpath(
                posixpath.join(opf_dir, href)) if opf_dir else href
    ordered = []
    for node in package.iter():
        if _local_tag(node) != "itemref":
            continue
        idref = node.get("idref")
        if not idref:
            continue
        href = hrefs.get(idref)
        if href is None:
            unsupported.append({
                "code": "source.unsupported",
                "message": "spine item %s: no manifest entry" % idref})
            continue
        ordered.append((idref, href))
    return ordered


def _epub_blocks(document):
    """`(element, text, fragment)` for every block-level element carrying
    text, plus the set of skipped tags that carried text."""
    parents = {}
    for parent in document.iter():
        for child in parent:
            parents[child] = parent

    def fragment_for(element):
        node = element
        while node is not None:
            node_id = node.get("id")
            if node_id:
                return node_id
            node = parents.get(node)
        return None

    blocks = []
    skipped = []
    for element in document.iter():
        tag = _local_tag(element)
        text = " ".join("".join(element.itertext()).split())
        if not text:
            continue
        if tag in EPUB_SKIPPED_TAGS:
            if tag not in skipped:
                skipped.append(tag)
            continue
        if tag not in EPUB_BLOCK_TAGS:
            continue
        # A block nested inside another block is emitted once, by its
        # innermost owner, exactly as the web adapter does.
        outer = parents.get(element)
        nested = False
        while outer is not None:
            if _local_tag(outer) in EPUB_BLOCK_TAGS:
                nested = True
                break
            outer = parents.get(outer)
        if nested:
            continue
        blocks.append((element, text, fragment_for(element)))
    return blocks, skipped


def _extract_epub(raw_bytes, options):
    """An EPUB, read in spine order with resolvable fragment anchors.

    XHTML is XML, so `_parse_xml_safely` is the correct parser for a content
    document and no HTML parser is needed. That is the reason this adapter
    needs no third-party library while the web adapter does, and it is what
    makes the D-14C-2 stdlib path cheap rather than merely principled.
    """
    try:
        archive = zipfile.ZipFile(io.BytesIO(raw_bytes))
    except zipfile.BadZipFile:
        raise _Refusal("source.malformed_input", "malformed/truncated EPUB")

    unsupported = []
    lines_out = []
    locators = []
    reading_order = []

    with archive as zf:
        # FIRST, before anything else is read. A DRM-locked book's container,
        # spine, and manifest all parse perfectly well and only its content is
        # unreadable, so checking later would build a book-shaped source with
        # garbage in it.
        if EPUB_ENCRYPTION_PATH in zf.namelist():
            raise _Refusal("source.encrypted",
                           "encrypted EPUB: no unauthenticated content")

        for name in zf.namelist():
            error = _zip_member_error(zf, name, options)
            if error is not None:
                raise _Refusal(error["code"], error["message"])

        opf_path, opf_dir = _epub_container_root(zf, options)
        raw_opf, error = _read_zip_part(zf, opf_path, options)
        if error is not None:
            raise _Refusal(error["code"], error["message"])
        package, error = _parse_xml_safely(raw_opf, options)
        if error is not None:
            raise _Refusal(error["code"], error["message"])

        spine = _epub_spine_order(package, opf_dir, unsupported)
        if not spine:
            raise _Refusal("source.unsupported",
                           "no spine item: the package lists no reading order")

        skipped_tags = []
        for spine_index, (idref, href) in enumerate(spine):
            raw_doc, error = _read_zip_part(zf, href, options)
            if error is not None:
                unsupported.append({
                    "code": error["code"],
                    "message": "spine item %s: %s" % (idref, error["message"])})
                continue
            document, error = _parse_xml_safely(raw_doc, options)
            if error is not None:
                unsupported.append({
                    "code": error["code"],
                    "message": "spine item %s: %s" % (idref, error["message"])})
                continue
            blocks, skipped = _epub_blocks(document)
            for tag in skipped:
                if tag not in skipped_tags:
                    skipped_tags.append(tag)
            for element_index, (element, text, fragment) in enumerate(blocks):
                lines_out.append(text)
                locator_id = "sp%d.%d" % (spine_index, element_index)
                locators.append({
                    "id": locator_id,
                    "kind": ("spine_item"
                             if _local_tag(element) in EPUB_HEADING_TAGS
                             else "block"),
                    "body": {
                        "medium": "epub",
                        "spine_index": spine_index,
                        "spine_idref": idref,
                        "element_index": element_index,
                        "fragment": fragment,
                    },
                    "_line": len(lines_out),
                })
                reading_order.append(locator_id)

    if not locators:
        raise _Refusal("source.unsupported",
                       "no readable content document in the spine")

    # PORT-02's semantic loss report for the import direction. These entries
    # do not fail the extraction; they are what makes the sidecar honest about
    # being a prototype-grade interchange adapter rather than a complete one.
    unsupported.append({
        "code": "source.unsupported",
        "message": "navigation document not read: no hierarchical table of "
                   "contents"})
    for tag in skipped_tags:
        unsupported.append({"code": "source.unsupported",
                            "message": "skipped a %s element" % tag})
    return "\n".join(lines_out) + "\n", locators, reading_order, unsupported


# ---------------------------------------------------------------------------
# Roster item 5: ASR (plan 14C-08). Registered, not built.
#
# Empty on purpose. `14C-CONTEXT.md` roster item 5 registers ASR and plans it
# last, because it needs whisper.cpp or a hosted call and the 7900 XTX build
# does not exist. The plan that adds the first backend adds a member here and
# a resolution function beside it; until then the emptiness is what
# `_extract_asr` refuses on, so the refusal cannot rot into a stale hard-coded
# message that outlives the condition it describes.
ASR_BACKENDS = ()


def _extract_asr(raw_bytes, options):
    """Speech recognition, registered and not yet built.

    The `body_asr` locator shape is frozen in
    `schemas/source_locator.schema.json` and tested before any backend exists,
    which is the whole point of registering now: when a real backend lands it
    produces cues into an already-frozen, already-tested locator rather than
    inventing a second timing shape beside the transcript adapter's.
    """
    if not ASR_BACKENDS:
        raise _Refusal(
            "source.backend_unconfigured",
            "no speech recognition backend is configured. Roster item 5 is "
            "registered and not yet built (14C-CONTEXT.md). Supply a "
            "transcript file and use the transcript adapter instead, which "
            "needs no backend.")
    raise _Refusal("source.internal_error",
                   "an ASR backend is registered but no plan has wired it")


SOURCE_ADAPTER_ENTRIES = [
    {"name": n, "version": "0.0.0" if n == "asr" else "1.0.0", "handler": h,
     "capability": "Registered source adapter.", "fallback": "Use the existing refusal behavior.",
     "check": "python3 tests/source_adapters_roundtrip.py"}
    for n, h in (("markdown", _extract_markdown), ("text", _extract_text),
                 ("pdf", _extract_pdf), ("docx", _extract_docx), ("pptx", _extract_pptx),
                 ("web", _extract_web), ("transcript", _extract_transcript),
                 ("ocr", _extract_ocr), ("epub", _extract_epub), ("asr", _extract_asr))]
ADAPTER_REGISTRY, ADAPTER_VERSIONS, SOURCE_ADAPTER_DESCRIPTIONS = build_registry(SOURCE_ADAPTER_ENTRIES)



# ---------------------------------------------------------------------------
def _last_entry_id(base, object_id):
    """The id of the newest applied journal entry for `object_id`.

    `journal.commit_operation` returns a registry-row-shaped record that
    carries no entry id at all, so `ok_result`'s `journal_entry_id` was
    always null. Found 2026-08-28 while driving a real capture through the
    CLI (plan 14C-04), fixed here rather than in `journal.py`, which this
    phase does not modify.
    """
    found = None
    for entry in journal.entries(base):
        if entry.get("object_id") == object_id and \
                entry.get("state") == "applied":
            found = entry.get("entry_id")
    return found


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
    try:
        with open(tmp, "wb") as fh:
            fh.write(raw)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except Exception:
        # A fault between the open and the replace leaves the sidecar itself
        # old-or-new, which is the property that matters, but it would also
        # leave a half-written `.locator.json.tmp` beside it forever. Sweep it
        # here so the only litter a fault can leave is none.
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise


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
                   rights_grant, options, confirm=False):
    refused = _bind_gate(actor_kind, confirm, options)
    if refused is not None:
        return refused
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
                            joined, reading_order, unsupported,
                            confidence=_extract_confidence(adapter, locators))
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
        journal.commit_operation(
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
                      _last_entry_id(base, source_id))


def import_source(base, adapter, raw_object_id, actor_kind, actor_name,
                  rights_grant=None, options=None, confirm=False):
    """The one public write boundary. Returns a typed result; the only
    exception that escapes is `journal.JournalError`, deliberately, because a
    rights refusal is the journal's to report by name."""
    try:
        return _import_source(base, adapter, raw_object_id, actor_kind,
                              actor_name, rights_grant, options, confirm)
    except journal.JournalError:
        raise
    except _Refusal as refusal:
        return unsupported_result(refusal.code, refusal.message, None)
    except Exception:  # last-resort safety net, never a traceback
        return unsupported_result("source.internal_error",
                                   "unexpected source-adapter failure", None)


def _write_bytes_atomic_under(path, raw):
    """The same same-directory temp, write, flush, fsync, replace shape
    `write_sidecar_atomic` uses, for a snapshot's raw bytes."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".tmp"
    try:
        with open(tmp, "wb") as fh:
            fh.write(raw)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except Exception:
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise


def _snapshot_extension(content_type):
    if content_type and "html" in content_type.lower():
        return ".html"
    if content_type and "text/plain" in content_type.lower():
        return ".txt"
    return ".bin"


def _store_snapshot(base, source_id, raw, content_type, options):
    """Both snapshot storage paths, which is `PLANNING-DIRECTIVES.md`
    section 3's "build both" answer to `14C-CONTEXT.md`'s snapshot question.

    `inline` writes the captured bytes beside the course as an owned file and
    returns its relative path for `origin.snapshot_rel_path`. `reference`
    writes them under `_sources/cache`, which is disposable derived state a
    future cleanup may evict, and returns `None`, so the sidecar records that
    the capture is cached rather than owned. `auto` picks inline when the
    capture is at or under `snapshot_inline_max_bytes`.

    The derived Markdown fingerprint is computed from the extraction and
    never from the snapshot bytes, which is why both modes produce the
    identical fingerprint and a citation cannot tell which was used.

    Returns `(snapshot_rel_path_or_None, stored_rel_path)`.
    """
    options = _options(options)
    mode = options["snapshot_storage"]
    if mode == "auto":
        mode = ("inline" if len(raw) <= options["snapshot_inline_max_bytes"]
                else "reference")
    extension = _snapshot_extension(content_type)
    if mode == "inline":
        rel = posixpath.join(SNAPSHOT_DIRNAME,
                             "%s.snapshot%s" % (source_id, extension))
    else:
        rel = posixpath.join(SNAPSHOT_DIRNAME, SNAPSHOT_CACHE_DIRNAME,
                             "%s.snapshot%s" % (source_id, extension))
    target = os.path.join(os.path.abspath(base), rel)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    if not discovery.inside_any_root(target, [os.path.abspath(base)]):
        raise _Refusal("source.malformed_input",
                       "the snapshot path resolves outside the approved "
                       "root; nothing was written")
    _write_bytes_atomic_under(target, raw)
    return (rel if mode == "inline" else None), rel


def _bind_gate(actor_kind, confirm, options):
    """The approve-before-bind gate, `PLANNING-DIRECTIVES.md` section 3's
    answer to `14C-CONTEXT.md`'s auto-fetch question. Both paths ship and the
    learner chooses. Searching and reading stay free under either, because
    `preview_source` never consults this function; only the write is gated."""
    options = _options(options)
    if options["bind_policy"] != "approve_before_bind":
        return None
    if actor_kind != "agent" or confirm:
        return None
    return unsupported_result(
        "source.approval_required",
        "an agent bind requires explicit approval under the "
        "approve_before_bind policy; pass confirm to proceed, or set "
        "source.bind_policy to auto_fetch", None)


def capture_url(base, url, actor_kind, actor_name, options=None,
                confirm=False):
    """The remote sibling of `import_source`: fetch a page, snapshot it,
    extract it, fingerprint the extraction, and journal one applied source.

    Three differences from `import_source`, each deliberate:

    1. The bytes come from `_fetch_url` rather than from a registry row,
       because there is no local file to link.
    2. Every path is derived from the minted object id and never from any
       part of the URL. A URL is attacker-shaped input; a path built from one
       is a directory traversal waiting to be written.
    3. `journal.commit_operation` is called with `source_object_id=None`, so
       the RIGHTS-01 transform gate does not fire and the new `kind="source"`
       object is minted with `identity.rights_default()`, all seven rights
       unknown. That default is the point rather than an oversight: a
       captured page carries no rights record until the learner records one,
       and any later import derived from it is refused by name until they do.
    """
    try:
        return _capture_url(base, url, actor_kind, actor_name, options,
                            confirm)
    except journal.JournalError:
        raise
    except _Refusal as refusal:
        return unsupported_result(refusal.code, refusal.message, None)
    except Exception:
        return unsupported_result("source.internal_error",
                                   "unexpected source-adapter failure", None)


def _capture_url(base, url, actor_kind, actor_name, options, confirm):
    options = _options(options)
    refused = _bind_gate(actor_kind, confirm, options)
    if refused is not None:
        return refused

    raw, content_type, etag, last_modified, _status = _fetch_url(url, options)
    fetched_at = identity.utc_now()

    extract_options = dict(options)
    extract_options["content_type"] = content_type
    md_text, locators, reading_order, unsupported = \
        _extract_web(raw, extract_options)

    md_bytes = md_text.encode("utf-8")
    source_id = identity.new_object_id()
    spans = auditor.normalize_source(md_bytes, source_id,
                                      kind="markdown")["spans"]
    joined = _join_span_ids(locators, spans)

    snapshot_rel, _stored_rel = _store_snapshot(base, source_id, raw,
                                                content_type, options)

    md_rel_path = posixpath.join(SNAPSHOT_DIRNAME, "%s.md" % source_id)
    sidecar_rel_path = sidecar_path_for(md_rel_path)

    origin = {
        "kind": "remote_url",
        "value": url,
        "fetched_at": fetched_at,
        "http_etag": etag,
        "http_last_modified": last_modified,
        "snapshot_rel_path": snapshot_rel,
    }
    rights = dict(identity.rights_default())

    sidecar = build_sidecar(source_id, "web", md_bytes, origin, rights,
                            joined, reading_order, unsupported,
                            confidence=_extract_confidence("web", locators))
    errors = schema_validate.validate(sidecar, _LOCATOR_SCHEMA)
    if errors:
        return unsupported_result("source.internal_error", errors[0],
                                   source_id)

    sidecar_abs = os.path.join(os.path.abspath(base), sidecar_rel_path)
    write_sidecar_atomic(sidecar_abs, sidecar)
    try:
        journal.commit_operation(
            base, source_id, "source", md_rel_path, "import", md_bytes,
            expected_fingerprint=None, actor_kind=actor_kind,
            actor_name=actor_name, create_if_missing=True,
            source_object_id=None)
    except journal.JournalError:
        try:
            os.remove(sidecar_abs)
        except OSError:
            pass
        raise
    return ok_result(source_id, "web", md_rel_path, sidecar_rel_path,
                      _last_entry_id(base, source_id))


_RECHECK_NOTES = {
    "origin_unchanged":
        "The remote origin still matches the captured snapshot. Nothing "
        "needs to change.",
    "origin_changed":
        "The remote origin has changed since it was captured. The captured "
        "snapshot and every citation into it are still valid; re-capture "
        "only if you want the newer version.",
    "origin_unreachable":
        "The remote origin could not be reached. The captured snapshot is "
        "still readable offline and every citation into it is unaffected.",
}


def _recheck_report(source_id, state, origin, note=None):
    return {
        "schema_version": SOURCE_LOCATOR_VERSION,
        "source_id": source_id,
        "state": state,
        "checked_at": identity.utc_now(),
        "origin": origin,
        "note": note or _RECHECK_NOTES[state],
    }


def recheck_origin(base, source_object_id, options=None):
    """Report whether a captured remote origin still matches, and change
    nothing at all.

    This function is a READ. It calls none of the journal's commit or append
    operations, neither of the two atomic writers in this module, and nothing
    that stores a snapshot, and it must stay that way. The acceptance check
    for that is a grep over this function's own source for those four names,
    which is why they are spelled around rather than quoted here: a docstring
    that names them would satisfy the grep without the code satisfying the
    property. Wiring remote staleness into the journal would
    make a citation's validity depend on network reachability, which breaks
    D-04 and the degrade-never-block rule in one move. A changed origin is a
    fact about the world, not a defect in an accepted revision, and every
    citation issued against the captured revision stays exactly as valid as
    it was when it was made (OQ-4).

    A learner who wants the newer version re-captures explicitly, through
    the journal's edit-in-place operation, which keeps the same object id and
    leaves the
    previous bytes recoverable as a before-image. No plan in Phase 14C builds
    that command; naming the operation here is what stops a later plan from
    inventing a different mechanism for it.

    An unreachable network is `origin_unreachable`, a named state, never a
    traceback and never a failure.
    """
    options = _options(options)
    registry = journal.read_registry(base)
    row = registry.get(source_object_id)
    if row is None:
        return unsupported_result(
            "source.malformed_input",
            "no object %s is recorded in this root's registry"
            % source_object_id, None)
    sidecar_abs = os.path.join(os.path.abspath(base),
                               sidecar_path_for(row["path"]))
    try:
        with open(sidecar_abs, encoding="utf-8") as fh:
            sidecar = json.load(fh)
    except (OSError, ValueError):
        return unsupported_result(
            "source.malformed_input",
            "no readable locator sidecar beside %s; a recheck needs the "
            "captured origin block" % row["path"], source_object_id)

    origin = sidecar.get("origin") or {}
    if origin.get("kind") != "remote_url":
        return _recheck_report(
            sidecar.get("source_id"), "origin_unchanged", origin,
            note="This source came from a local file. Drift in a local file "
                 "is reported by the journal's own external-edit detection, "
                 "not by a remote recheck.")

    conditional = None
    if origin.get("http_etag"):
        conditional = ("If-None-Match", origin["http_etag"])
    elif origin.get("http_last_modified"):
        conditional = ("If-Modified-Since", origin["http_last_modified"])

    try:
        raw, content_type, _etag, _last_modified, status = _fetch_url(
            origin["value"], options, conditional=conditional)
    except _Refusal as refusal:
        if refusal.code in ("source.fetch_failed", "source.origin_refused",
                            "source.redirect_refused"):
            return _recheck_report(sidecar.get("source_id"),
                                   "origin_unreachable", origin)
        return unsupported_result(refusal.code, refusal.message,
                                   sidecar.get("source_id"))

    if status == 304:
        return _recheck_report(sidecar.get("source_id"), "origin_unchanged",
                               origin)

    try:
        extract_options = dict(options)
        extract_options["content_type"] = content_type
        md_text, _locators, _order, _unsupported = _extract_web(
            raw, extract_options)
    except _Refusal:
        return _recheck_report(sidecar.get("source_id"), "origin_changed",
                               origin)

    fresh = identity.object_fingerprint(md_text.encode("utf-8"), "source")
    state = ("origin_unchanged" if fresh == sidecar.get("fingerprint")
             else "origin_changed")
    return _recheck_report(sidecar.get("source_id"), state, origin)


def preview_source(base, adapter, raw_object_id, options=None):
    """The free half of the auto-fetch versus approve-before-bind pair: the
    same path an import takes, up to and including the span join, returning
    the would-be sidecar and writing nothing at all.

    This function never consults `_bind_gate`, under either policy and for
    either actor kind, because searching and reading a source are free in
    both and only the bind step is gated. An agent that may not write may
    still look."""
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
        sidecar = build_sidecar(
            source_id, adapter, md_bytes, origin, rights, joined,
            reading_order, unsupported,
            confidence=_extract_confidence(adapter, locators))
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
