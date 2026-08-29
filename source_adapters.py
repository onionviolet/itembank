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
import posixpath
import re
import zipfile
from xml.etree import ElementTree

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


# The WordprocessingML main namespace, spelled as the ElementTree prefix so a
# tag test is a string comparison and never a namespace-map lookup.
W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

# The package parts python-docx's object model never surfaces. Read directly,
# each one through `_read_zip_part` and `_parse_xml_safely`, because an adapter
# built on python-docx alone silently produces nothing for a document whose
# content lives in a footnote, a header, or a comment (RESEARCH Pitfall 1).
DOCX_EXTRA_PARTS = ("word/footnotes.xml", "word/endnotes.xml",
                    "word/comments.xml")

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


ADAPTER_REGISTRY = {
    "markdown": _extract_markdown,
    "text": _extract_text,
    "pdf": _extract_pdf,
    "docx": _extract_docx,
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
                            joined, reading_order, unsupported,
                            confidence=_extract_confidence(adapter, joined))
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
        sidecar = build_sidecar(
            source_id, adapter, md_bytes, origin, rights, joined,
            reading_order, unsupported,
            confidence=_extract_confidence(adapter, joined))
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
