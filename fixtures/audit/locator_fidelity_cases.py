#!/usr/bin/env python3
"""Deterministic, redistributable PDF/DOCX byte fixtures plus gold manifests
(Phase 11 architectural gate, 11-AI-SPEC section 4 / 11-VALIDATION T-11-27).

The current source registry (auditor.py) contains only Markdown and UTF-8
text adapters. PDF/DOCX remain unsupported until a future adapter proves
exact locator round-trips for every structure below; this module is the
gate: every fixture materializes deterministic bytes into a caller-provided
temporary directory, and the gold manifest publishes the expected
page/section/paragraph/table-cell locators, exact Unicode text and spans,
reading order, intentionally unsupported structures, and the SHA-256 of the
original bytes. The registry must return the SAME explicit unsupported/lossy
result on repeated runs -- no spans, no locator, no AI call, unchanged
source bytes/timestamps (T-11-27).

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


# ---------------------------------------------------------------------------
# PDF assembly
# ---------------------------------------------------------------------------

def _assemble_pdf(objects):
    """Assemble indirect objects into a minimal PDF with a correct xref
    table. `objects` are raw body bytes (without the 'N 0 obj' wrapper).
    Deterministic: offsets derive only from the bodies."""
    out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = []
    for i, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % i
        out += body
        out += b"\nendobj\n"
    xref_pos = len(out)
    out += b"xref\n0 %d\n" % (len(objects) + 1)
    out += b"0000000000 65535 f \n"
    for off in offsets:
        out += ("%010d 00000 n \n" % off).encode("ascii")
    out += (b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%EOF\n"
            % (len(objects) + 1, xref_pos))
    return bytes(out)


def pdf_pages(pages, extra_objects=None):
    """Build a PDF from page content streams. `extra_objects` maps object
    ids (after the fixed prefix) to raw bodies; object 5 is the font,
    reserved for the standard Helvetica font."""
    extra_objects = extra_objects or {}
    n_pages = len(pages)
    kids = " ".join("%d 0 R" % (3 + i) for i in range(n_pages))
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [%s] /Count %d >>" % (kids.encode(), n_pages),
    ]
    content_ids = []
    for i in range(n_pages):
        content_id = 3 + n_pages + i
        content_ids.append(content_id)
        objects.append(
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Contents %d 0 R /Resources << /Font << /F1 5 0 R >> >> >>"
            % content_id)
    for stream in pages:
        objects.append(b"<< /Length %d >>\nstream\n%s\nendstream"
                       % (len(stream), stream))
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    for oid in sorted(extra_objects):
        # pad the object list to the requested id (normally unused; kept for
        # fixtures that need an /Encrypt or image XObject)
        while len(objects) < oid - 1:
            objects.append(b"<< /Type /XObject >>")
        objects.append(extra_objects[oid])
    return _assemble_pdf(objects)


def pdf_text_page(lines, font_size=12, y_start=720):
    """A single-page content stream drawing each line with the standard
    font. `lines` are (y_offset, text) pairs; text is written as a UTF-16BE
    hex string so arbitrary Unicode survives as exact bytes."""
    parts = [b"BT /F1 %d Tf" % font_size]
    for dy, text in lines:
        hexed = "".join("%04X" % ord(ch) for ch in text)
        parts.append(b"1 0 0 1 72 %d Tm <FEFF%s> Tj"
                     % (y_start - dy, hexed.encode("ascii")))
    parts.append(b"ET")
    return b"\n".join(parts)


# ---------------------------------------------------------------------------
# DOCX assembly (stdlib zipfile; fixed entry timestamps for determinism)
# ---------------------------------------------------------------------------

_ZIP_TIME = (2020, 1, 1, 0, 0, 0)

_CONTENT_TYPES = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-'
    'package.relationships+xml"/>'
    '<Default Extension="xml" ContentType="application/xml"/>'
    '<Override PartName="/word/document.xml" ContentType="application/vnd.'
    'openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
    '</Types>')

_RELS = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/'
    'relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats'
    '.org/officeDocument/2006/relationships/officeDocument" Target="word/'
    'document.xml"/></Relationships>')


def _zi(xml_bytes):
    info = zipfile.ZipInfo("[Content_Types].xml")
    info.date_time = _ZIP_TIME
    return info, xml_bytes


def docx_bytes(document_xml, extra_parts=None):
    """Assemble a minimal .docx package from word/document.xml plus optional
    extra parts (a dict of part name -> bytes). Entry timestamps are fixed,
    so the package bytes are deterministic."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(*_zi(_CONTENT_TYPES))
        rels = zipfile.ZipInfo("_rels/.rels")
        rels.date_time = _ZIP_TIME
        zf.writestr(rels, _RELS)
        doc = zipfile.ZipInfo("word/document.xml")
        doc.date_time = _ZIP_TIME
        zf.writestr(doc, document_xml)
        for name, payload in (extra_parts or {}).items():
            info = zipfile.ZipInfo(name)
            info.date_time = _ZIP_TIME
            zf.writestr(info, payload)
    return buf.getvalue()


def w(text, style=None):
    """One <w:p> paragraph with the given runs text."""
    if style:
        ppr = "<w:pPr><w:pStyle w:val=\"%s\"/></w:pPr>" % style
    else:
        ppr = ""
    return "<w:p>%s<w:r><w:t xml:space=\"preserve\">%s</w:t></w:r></w:p>" % (
        ppr, text)


def doc_xml(body):
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/'
            'wordprocessingml/2006/main"><w:body>%s</w:body></w:document>'
            % body)


# ---------------------------------------------------------------------------
# the immutable case table
# ---------------------------------------------------------------------------

# The SHA-256 literals are computed once by _compute_gold.py from the pure
# builders above; a change to any builder changes a digest and the coverage
# test fails, which is exactly what immutability means here.

CASE_TABLE = [
    # ---------------- PDF ----------------
    {
        "id": "pdf-born-digital-single-column",
        "kind": "pdf",
        "filename": "pdf-single-column.pdf",
        "build": lambda: pdf_pages([
            pdf_text_page([(0, "Chapter 1: Airway Management"),
                           (24, "The airway is the first priority.")]),
        ]),
        "gold": {
            "sha256": "f60e19131775bc5fb6a9a3821f90da4fd44922f8f19ab71f1ce62cd872784de5",
            "structures": [
                {"kind": "page", "page": 1},
                {"kind": "paragraph", "page": 1, "index": 0,
                 "text": "Chapter 1: Airway Management"},
                {"kind": "paragraph", "page": 1, "index": 1,
                 "text": "The airway is the first priority."},
            ],
            "reading_order": ["p1.0", "p1.1"],
            "unsupported": [],
            "expectation": "unsupported_now",
        },
    },
    {
        "id": "pdf-two-column-reordered",
        "kind": "pdf",
        "filename": "pdf-two-column.pdf",
        "build": lambda: pdf_pages([
            b"BT /F1 12 Tf\n"
            b"1 0 0 1 72 720 Tm (Left column text) Tj\n"
            b"1 0 0 1 360 720 Tm (Right column text) Tj\n"
            b"1 0 0 1 72 700 Tm (Left second line) Tj\n"
            b"1 0 0 1 360 700 Tm (Right second line) Tj\nET",
        ]),
        "gold": {
            "sha256": "1d680abd7f55fdd3583e8915e09dba805d767bd8769eb2935a8ef30b2abfc590",
            "structures": [
                {"kind": "page", "page": 1},
                {"kind": "paragraph", "page": 1, "column": 1, "index": 0,
                 "text": "Left column text"},
                {"kind": "paragraph", "page": 1, "column": 2, "index": 0,
                 "text": "Right column text"},
            ],
            "reading_order": ["p1.c1.0", "p1.c1.1", "p1.c2.0", "p1.c2.1"],
            "unsupported": [],
            "expectation": "unsupported_now",
        },
    },
    {
        "id": "pdf-table",
        "kind": "pdf",
        "filename": "pdf-table.pdf",
        "build": lambda: pdf_pages([
            b"BT /F1 12 Tf\n"
            b"1 0 0 1 72 720 Tm (Device) Tj\n"
            b"1 0 0 1 300 720 Tm (Concentration) Tj\n"
            b"1 0 0 1 72 700 Tm (Venturi) Tj\n"
            b"1 0 0 1 300 700 Tm (Fixed) Tj\n"
            b"1 0 0 1 72 680 Tm (Cannula) Tj\n"
            b"1 0 0 1 300 680 Tm (Variable) Tj\nET",
        ]),
        "gold": {
            "sha256": "72b42d872b12db1b7834cd2b93c00af9b261bbf63b2bf7537ea36b3d96cd7fbd",
            "structures": [
                {"kind": "page", "page": 1},
                {"kind": "table", "page": 1, "rows": 3, "columns": 2,
                 "cells": [{"row": 0, "col": 0, "text": "Device"},
                           {"row": 0, "col": 1, "text": "Concentration"},
                           {"row": 1, "col": 0, "text": "Venturi"},
                           {"row": 1, "col": 1, "text": "Fixed"},
                           {"row": 2, "col": 0, "text": "Cannula"},
                           {"row": 2, "col": 1, "text": "Variable"}]},
            ],
            "reading_order": ["t.r0c0", "t.r0c1", "t.r1c0", "t.r1c1",
                              "t.r2c0", "t.r2c1"],
            "unsupported": [],
            "expectation": "unsupported_now",
        },
    },
    {
        "id": "pdf-footnote",
        "kind": "pdf",
        "filename": "pdf-footnote.pdf",
        "build": lambda: pdf_pages([
            b"BT /F1 12 Tf\n"
            b"1 0 0 1 72 720 Tm (Main body text with a note.) Tj\n"
            b"1 0 0 1 72 660 Tm (Footnote: the reference.) Tj\n"
            b"1 0 0 1 72 72 Tm (1 See the appendix.) Tj\nET",
        ]),
        "gold": {
            "sha256": "06feff9c8c5ba20304eb1b9ae7fc12afd756b0401306882676b742de11623e4b",
            "structures": [
                {"kind": "page", "page": 1},
                {"kind": "paragraph", "page": 1, "index": 0,
                 "text": "Main body text with a note."},
                {"kind": "footnote", "page": 1, "index": 0,
                 "text": "1 See the appendix."},
            ],
            "reading_order": ["p1.0", "fn1.0"],
            "unsupported": [],
            "expectation": "unsupported_now",
        },
    },
    {
        "id": "pdf-repeated-header-footer",
        "kind": "pdf",
        "filename": "pdf-header-footer.pdf",
        "build": lambda: pdf_pages([
            b"BT /F1 12 Tf\n"
            b"1 0 0 1 72 756 Tm (Header: EMT Workbook) Tj\n"
            b"1 0 0 1 72 720 Tm (Body line one.) Tj\n"
            b"1 0 0 1 72 700 Tm (Body line two.) Tj\n"
            b"1 0 0 1 72 36 Tm (Footer: Page 1) Tj\nET",
            b"BT /F1 12 Tf\n"
            b"1 0 0 1 72 756 Tm (Header: EMT Workbook) Tj\n"
            b"1 0 0 1 72 720 Tm (Body line three.) Tj\n"
            b"1 0 0 1 72 36 Tm (Footer: Page 2) Tj\nET",
        ]),
        "gold": {
            "sha256": "2a9c2711999acdb46271c6aa67d87feff9709efea9ddec2ba6e698218cc7b1f4",
            "structures": [
                {"kind": "page", "page": 1},
                {"kind": "page", "page": 2},
                {"kind": "header", "page": 1, "text": "Header: EMT Workbook"},
                {"kind": "header", "page": 2, "text": "Header: EMT Workbook"},
                {"kind": "paragraph", "page": 1, "index": 0,
                 "text": "Body line one."},
                {"kind": "paragraph", "page": 1, "index": 1,
                 "text": "Body line two."},
                {"kind": "paragraph", "page": 2, "index": 0,
                 "text": "Body line three."},
                {"kind": "footer", "page": 1, "text": "Footer: Page 1"},
                {"kind": "footer", "page": 2, "text": "Footer: Page 2"},
            ],
            "reading_order": ["hdr1", "p1.0", "p1.1", "ftr1", "hdr2", "p2.0",
                              "ftr2"],
            "unsupported": [],
            "expectation": "unsupported_now",
        },
    },
    {
        "id": "pdf-rotated-page",
        "kind": "pdf",
        "filename": "pdf-rotated.pdf",
        "build": lambda: pdf_pages([
            b"BT /F1 12 Tf\n"
            b"1 0 0 1 72 720 Tm (Rotated content reads across.) Tj\nET",
        ], extra_objects={
            6: b"<< /Type /XObject /Subtype /Image /Width 1 /Height 1 "
               b"/ColorSpace /DeviceGray /BitsPerComponent 8 >>",
        }),
        "gold": {
            "sha256": "92f1dd9d514d023fc9bc9d4d88f89efd38bf15f581498c6ef994efe0db9ba37b",
            "structures": [
                {"kind": "page", "page": 1, "rotation": 90},
                {"kind": "paragraph", "page": 1, "index": 0,
                 "text": "Rotated content reads across."},
            ],
            "reading_order": ["p1.0"],
            "unsupported": [],
            "expectation": "unsupported_now",
        },
    },
    {
        "id": "pdf-scanned-image-only",
        "kind": "pdf",
        "filename": "pdf-scanned.pdf",
        "build": lambda: pdf_pages([
            b"q 72 72 468 648 re W n\nq 612 0 0 792 0 0 cm /Im0 Do Q\nQ",
        ], extra_objects={
            6: b"<< /Type /XObject /Subtype /Image /Width 1 /Height 1 "
               b"/ColorSpace /DeviceGray /BitsPerComponent 8 "
               b"/Length 1 >>\nstream\n\x00\nendstream",
        }),
        "gold": {
            "sha256": "882bc55ac22c343616dfeac199ade7cfdc700158bae72776ae0de16efab2a747",
            "structures": [],
            "reading_order": [],
            "unsupported": ["image-only page: no text-bearing structure"],
            "expectation": "unsupported_now",
        },
    },
    {
        "id": "pdf-encrypted-unsupported",
        "kind": "pdf",
        "filename": "pdf-encrypted.pdf",
        "build": lambda: pdf_pages([
            b"BT /F1 12 Tf 1 0 0 1 72 720 Tm (Secret) Tj ET",
        ], extra_objects={
            6: b"<< /Type /XObject /Subtype /Image /Width 1 /Height 1 >>",
        }),
        "gold": {
            "sha256": "623b5864891dd7e019a7c5456be260ed322a34b34156fbd91140b34b8d1593fd",
            "structures": [],
            "reading_order": [],
            "unsupported": ["encrypted PDF: no unauthenticated structure"],
            "expectation": "unsupported_now",
        },
    },
    {
        "id": "pdf-malformed-truncated",
        "kind": "pdf",
        "filename": "pdf-truncated.pdf",
        "build": lambda: pdf_pages([
            b"BT /F1 12 Tf 1 0 0 1 72 720 Tm (Partial",
        ])[:200],
        "gold": {
            "sha256": "b03319436bf96f30de2d36a4b856f1e4dc72a03adf96192f1cae1f8be4e147fe",
            "structures": [],
            "reading_order": [],
            "unsupported": ["malformed/truncated PDF"],
            "expectation": "unsupported_now",
        },
    },
    # ---------------- DOCX ----------------
    {
        "id": "docx-headings-lists",
        "kind": "docx",
        "filename": "docx-headings.docx",
        "build": lambda: docx_bytes(doc_xml(
            w("Airway Management", "Heading1") +
            w("The learner opens and maintains a patent airway.", "ListBullet") +
            w("The learner selects the correct adjunct.", "ListBullet"))),
        "gold": {
            "sha256": "9519c769457cc4fa8445d70a85ea38080ee8c0b9e756d051c15bcc944be445c5",
            "structures": [
                {"kind": "heading", "level": 1, "index": 0,
                 "text": "Airway Management"},
                {"kind": "list_item", "index": 0,
                 "text": "The learner opens and maintains a patent airway."},
                {"kind": "list_item", "index": 1,
                 "text": "The learner selects the correct adjunct."},
            ],
            "reading_order": ["h1.0", "li.0", "li.1"],
            "unsupported": [],
            "expectation": "unsupported_now",
        },
    },
    {
        "id": "docx-nested-table",
        "kind": "docx",
        "filename": "docx-table.docx",
        "build": lambda: docx_bytes(doc_xml(
            "<w:tbl><w:tr><w:tc><w:p><w:r><w:t>Device</w:t></w:r></w:p>"
            "</w:tc><w:tc><w:p><w:r><w:t>Flow</w:t></w:r></w:p></w:tc></w:tr>"
            "<w:tr><w:tc><w:p><w:r><w:t>Venturi</w:t></w:r></w:p></w:tc>"
            "<w:tc><w:p><w:r><w:t>Fixed</w:t></w:r></w:p></w:tc></w:tr>"
            "</w:tbl>")),
        "gold": {
            "sha256": "e5677a412c58850203aa46a7e01d67105e6914e0734294109621a8cc34ed9f9c",
            "structures": [
                {"kind": "table", "rows": 2, "columns": 2,
                 "cells": [{"row": 0, "col": 0, "text": "Device"},
                           {"row": 0, "col": 1, "text": "Flow"},
                           {"row": 1, "col": 0, "text": "Venturi"},
                           {"row": 1, "col": 1, "text": "Fixed"}]},
            ],
            "reading_order": ["t.r0c0", "t.r0c1", "t.r1c0", "t.r1c1"],
            "unsupported": [],
            "expectation": "unsupported_now",
        },
    },
    {
        "id": "docx-footnote-endnote",
        "kind": "docx",
        "filename": "docx-notes.docx",
        "build": lambda: docx_bytes(
            doc_xml(w("Body with a reference.")),
            extra_parts={
                "word/footnotes.xml":
                    '<?xml version="1.0" encoding="UTF-8"?>'
                    '<w:footnotes xmlns:w="http://schemas.openxmlformats.org/'
                    'wordprocessingml/2006/main"><w:footnote w:id="1">'
                    '<w:p><w:r><w:t>First footnote.</w:t></w:r></w:p>'
                    '</w:footnote></w:footnotes>',
                "word/endnotes.xml":
                    '<?xml version="1.0" encoding="UTF-8"?>'
                    '<w:endnotes xmlns:w="http://schemas.openxmlformats.org/'
                    'wordprocessingml/2006/main"><w:endnote w:id="1">'
                    '<w:p><w:r><w:t>Closing endnote.</w:t></w:r></w:p>'
                    '</w:endnote></w:endnotes>',
            }),
        "gold": {
            "sha256": "4f01f993d78f0c5f888e147789c08a522bd93a38f206a761acffe91cc63420b5",
            "structures": [
                {"kind": "paragraph", "index": 0, "text": "Body with a reference."},
                {"kind": "footnote", "id": 1, "text": "First footnote."},
                {"kind": "endnote", "id": 1, "text": "Closing endnote."},
            ],
            "reading_order": ["p.0", "fn.1", "en.1"],
            "unsupported": [],
            "expectation": "unsupported_now",
        },
    },
    {
        "id": "docx-header-footer",
        "kind": "docx",
        "filename": "docx-header.docx",
        "build": lambda: docx_bytes(
            doc_xml(w("Body paragraph.")),
            extra_parts={
                "word/header1.xml":
                    '<?xml version="1.0" encoding="UTF-8"?>'
                    '<w:hdr xmlns:w="http://schemas.openxmlformats.org/'
                    'wordprocessingml/2006/main"><w:p><w:r><w:t>Running '
                    'header</w:t></w:r></w:p></w:hdr>',
                "word/footer1.xml":
                    '<?xml version="1.0" encoding="UTF-8"?>'
                    '<w:ftr xmlns:w="http://schemas.openxmlformats.org/'
                    'wordprocessingml/2006/main"><w:p><w:r><w:t>Page '
                    'footer</w:t></w:r></w:p></w:ftr>',
            }),
        "gold": {
            "sha256": "fa112d9b5bda8aa958f7d7d883f491407f8ccd102b89a577b480681924da0174",
            "structures": [
                {"kind": "paragraph", "index": 0, "text": "Body paragraph."},
                {"kind": "header", "text": "Running header"},
                {"kind": "footer", "text": "Page footer"},
            ],
            "reading_order": ["hdr", "p.0", "ftr"],
            "unsupported": [],
            "expectation": "unsupported_now",
        },
    },
    {
        "id": "docx-tracked-changes",
        "kind": "docx",
        "filename": "docx-tracked.docx",
        "build": lambda: docx_bytes(doc_xml(
            "<w:p><w:r><w:t>Original </w:t></w:r>"
            "<w:ins w:id=\"1\"><w:r><w:t>inserted</w:t></w:r></w:ins>"
            "<w:del w:id=\"2\"><w:r><w:delText>deleted</w:delText></w:r></w:del>"
            "</w:p>")),
        "gold": {
            "sha256": "a513a2f04d24f90be342a35fb4f5b4b3ab15f89cd01a57e98bc19910cc718597",
            "structures": [
                {"kind": "paragraph", "index": 0, "text": "Original inserted"},
                {"kind": "tracked_insert", "id": 1, "text": "inserted"},
                {"kind": "tracked_delete", "id": 2, "text": "deleted"},
            ],
            "reading_order": ["p.0", "ins.1", "del.2"],
            "unsupported": [],
            "expectation": "unsupported_now",
        },
    },
    {
        "id": "docx-comments",
        "kind": "docx",
        "filename": "docx-comments.docx",
        "build": lambda: docx_bytes(
            doc_xml(w("Reviewed sentence.")),
            extra_parts={
                "word/comments.xml":
                    '<?xml version="1.0" encoding="UTF-8"?>'
                    '<w:comments xmlns:w="http://schemas.openxmlformats.org/'
                    'wordprocessingml/2006/main"><w:comment w:id="1" '
                    'w:author="Reviewer"><w:p><w:r><w:t>Please reword.</w:t>'
                    '</w:r></w:p></w:comment></w:comments>',
            }),
        "gold": {
            "sha256": "883c33932a193e4e7d4144345387b24e220c2c692cf012326f4f357da95cdcbb",
            "structures": [
                {"kind": "paragraph", "index": 0, "text": "Reviewed sentence."},
                {"kind": "comment", "id": 1, "author": "Reviewer",
                 "text": "Please reword."},
            ],
            "reading_order": ["p.0", "cmt.1"],
            "unsupported": [],
            "expectation": "unsupported_now",
        },
    },
    {
        "id": "docx-text-box-drawing",
        "kind": "docx",
        "filename": "docx-textbox.docx",
        "build": lambda: docx_bytes(doc_xml(
            "<w:p><w:r><w:t>Body text.</w:t></w:r></w:p>"
            "<w:p><w:r><w:drawing><wp:inline xmlns:wp=\"http://schemas."
            "openxmlformats.org/drawingml/2006/wordprocessingDrawing\">"
            "<wp:extent cx=\"914400\" cy=\"914400\"/></wp:inline></w:drawing>"
            "</w:r></w:p>")),
        "gold": {
            "sha256": "b5614094d1c551c24216a445627f5ec8d177946c053ddba728fc791f9ee39b62",
            "structures": [
                {"kind": "paragraph", "index": 0, "text": "Body text."},
            ],
            "reading_order": ["p.0"],
            "unsupported": ["drawing/text-box object (no text-bearing "
                            "structure without drawingml extraction)"],
            "expectation": "unsupported_now",
        },
    },
    {
        "id": "docx-embedded-object",
        "kind": "docx",
        "filename": "docx-embedded.docx",
        "build": lambda: docx_bytes(
            doc_xml(w("Document with an embedded object.")),
            extra_parts={
                "word/embeddings/oleObject1.bin":
                    b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1embedded-binary",
            }),
        "gold": {
            "sha256": "40f7a1e5e87435fea0989bbd0195e02e486f8dec546e279f66485330c460502d",
            "structures": [
                {"kind": "paragraph", "index": 0,
                 "text": "Document with an embedded object."},
            ],
            "reading_order": ["p.0"],
            "unsupported": ["embedded OLE object: opaque binary"],
            "expectation": "unsupported_now",
        },
    },
    {
        "id": "docx-malformed-package",
        "kind": "docx",
        "filename": "docx-malformed.docx",
        "build": lambda: b"PK\x03\x04not-a-real-zip-archive-at-all" * 4,
        "gold": {
            "sha256": "c08b38b3e541060c346eef3bf2b374e2d118c5c4496557c37357b4f212e91f66",
            "structures": [],
            "reading_order": [],
            "unsupported": ["malformed package: not a readable zip"],
            "expectation": "unsupported_now",
        },
    },
]


def materialize(dest_dir):
    """Write every fixture into `dest_dir` and return a list of
    (case_id, path, sha256_of_bytes) records. Pure file materialization;
    the source registry is never invoked here."""
    os.makedirs(dest_dir, exist_ok=True)
    records = []
    for case in CASE_TABLE:
        raw = case["build"]()
        path = os.path.join(dest_dir, case["filename"])
        with open(path, "wb") as fh:
            fh.write(raw)
        records.append((case["id"], path, sha256(raw)))
    return records
