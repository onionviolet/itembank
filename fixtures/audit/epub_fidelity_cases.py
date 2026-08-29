#!/usr/bin/env python3
"""Deterministic EPUB byte fixtures plus gold manifests
(Phase 14C, plan 14C-07).

Roster item 7 in `14C-CONTEXT.md`: EPUB is export-only today and import is
additive. These fixtures are the import direction's acceptance corpus.

The bytes are hand-assembled from stdlib `zipfile` and literal XML for a
reason beyond the usual one: `ebooklib` is parked under `D-14C-2` pending an
explicit Weibao AGPL decision, so the fixture and the adapter it tests are
both stdlib and neither depends on the parked library.

Three of the seven cases exist because a real book differs from the
conventional layout in ways that all look plausible on a tidy one: the spine
lists chapters in an order the filenames do not, the package document lives
somewhere other than `OEBPS/content.opf`, and a DRM-locked book's container
and spine parse perfectly well while only its content is unreadable.

`expectation` is absent here for the same reason it is absent from the three
sibling files added by plans 14C-03 through 14C-05: that key belongs to the
Phase 11 auditor gate, which enumerates `locator_fidelity_cases.CASE_TABLE`
only. This file carries `adapter_expectation`, `unsupported` exactly when
`reading_order` is empty.

Stdlib only (hashlib, io, os, zipfile) and repository-independent: the case
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
# EPUB assembly (stdlib zipfile; fixed entry timestamps for determinism)
# ---------------------------------------------------------------------------

_ZIP_TIME = (2020, 1, 1, 0, 0, 0)
_ZIP_CREATE_SYSTEM = 3

_OPF_NS = "http://www.idpf.org/2007/opf"
_DC_NS = "http://purl.org/dc/elements/1.1/"
_CONTAINER_NS = "urn:oasis:names:tc:opendocument:xmlns:container"
_XHTML_NS = "http://www.w3.org/1999/xhtml"


def _entry(name, stored=False):
    info = zipfile.ZipInfo(name)
    info.date_time = _ZIP_TIME
    info.create_system = _ZIP_CREATE_SYSTEM
    info.compress_type = zipfile.ZIP_STORED if stored else zipfile.ZIP_DEFLATED
    return info


def container_xml(opf_path):
    return ('<?xml version="1.0" encoding="UTF-8"?>'
            '<container version="1.0" xmlns="%s"><rootfiles>'
            '<rootfile full-path="%s" '
            'media-type="application/oebps-package+xml"/>'
            '</rootfiles></container>' % (_CONTAINER_NS, opf_path))


def opf_xml(items, spine_idrefs):
    """`items` are (id, href) pairs relative to the OPF's own directory."""
    manifest = "".join(
        '<item id="%s" href="%s" media-type="application/xhtml+xml"/>'
        % (item_id, href) for item_id, href in items)
    spine = "".join('<itemref idref="%s"/>' % idref for idref in spine_idrefs)
    return ('<?xml version="1.0" encoding="UTF-8"?>'
            '<package xmlns="%s" version="3.0" unique-identifier="bookid">'
            '<metadata xmlns:dc="%s"><dc:title>Fixture Book</dc:title>'
            '<dc:identifier id="bookid">itembank-fixture</dc:identifier>'
            '</metadata>'
            '<manifest>%s</manifest><spine>%s</spine></package>'
            % (_OPF_NS, _DC_NS, manifest, spine))


def xhtml(body):
    return ('<?xml version="1.0" encoding="UTF-8"?>'
            '<html xmlns="%s"><head><title>Fixture</title></head>'
            '<body>%s</body></html>' % (_XHTML_NS, body))


def chapter_xhtml(heading, paragraphs):
    body = "<h1>%s</h1>" % heading
    body += "".join("<p>%s</p>" % text for text in paragraphs)
    return xhtml(body)


def epub_bytes(opf_path, items, spine_idrefs, documents, extra_parts=None,
               with_container=True):
    """Assemble a minimal EPUB.

    The `mimetype` member is written first and uncompressed, carrying exactly
    `application/epub+zip` with no trailing newline, which is what makes a
    zip an EPUB rather than a zip that happens to contain XHTML.

    `documents` maps an archive-relative path to its bytes or text.
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(_entry("mimetype", stored=True), "application/epub+zip")
        if with_container:
            zf.writestr(_entry("META-INF/container.xml"),
                        container_xml(opf_path))
        zf.writestr(_entry(opf_path), opf_xml(items, spine_idrefs))
        for path, payload in sorted(documents.items()):
            zf.writestr(_entry(path), payload)
        for path, payload in sorted((extra_parts or {}).items()):
            zf.writestr(_entry(path), payload)
    return buf.getvalue()


_ENCRYPTION_XML = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<encryption xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
    '<EncryptedData xmlns="http://www.w3.org/2001/04/xmlenc#">'
    '<CipherData><CipherReference URI="OEBPS/chap1.xhtml"/></CipherData>'
    '</EncryptedData></encryption>')


def _three_chapter_documents(prefix="OEBPS/"):
    return {
        prefix + "chap1.xhtml": chapter_xhtml(
            "Airway", ["Open the airway first.",
                       "Then confirm it stays open."]),
        prefix + "chap2.xhtml": chapter_xhtml(
            "Breathing", ["Look for chest rise.",
                          "Count the respiratory rate."]),
        prefix + "chap3.xhtml": chapter_xhtml(
            "Circulation", ["Check a central pulse.",
                            "Control obvious bleeding."]),
    }


_THREE_ITEMS = [("c1", "chap1.xhtml"), ("c2", "chap2.xhtml"),
                ("c3", "chap3.xhtml")]


# ---------------------------------------------------------------------------
# the immutable case table
# ---------------------------------------------------------------------------

CASE_TABLE = [
    {
        "id": "epub-three-chapters",
        "kind": "epub",
        "filename": "book.epub",
        "build": lambda: epub_bytes(
            "OEBPS/content.opf", _THREE_ITEMS, ["c1", "c2", "c3"],
            _three_chapter_documents()),
        "gold": {
            "sha256": "421a474d8a46c3f335900f7ff8f410eb737c66c7edac170b25446c9234d768dd",
            "structures": [],
            "reading_order": ["sp0.0", "sp0.1", "sp0.2",
                              "sp1.0", "sp1.1", "sp1.2",
                              "sp2.0", "sp2.1", "sp2.2"],
            "unsupported": ["navigation document not read: no hierarchical "
                            "table of contents"],
            "adapter_expectation": "supported",
        },
    },
    {
        "id": "epub-spine-out-of-order",
        "kind": "epub",
        "filename": "book-reordered.epub",
        # Three documents named 1, 2, 3 and spined 3, 1, 2. Filename order and
        # manifest order both look plausible here and are both wrong.
        "build": lambda: epub_bytes(
            "OEBPS/content.opf", _THREE_ITEMS, ["c3", "c1", "c2"],
            _three_chapter_documents()),
        "gold": {
            "sha256": "59db39441ea4dbffcea58bbbf55d8edded4285aef8f9dd544671bf440edba029",
            "structures": [],
            "reading_order": ["sp0.0", "sp0.1", "sp0.2",
                              "sp1.0", "sp1.1", "sp1.2",
                              "sp2.0", "sp2.1", "sp2.2"],
            "unsupported": ["navigation document not read: no hierarchical "
                            "table of contents"],
            "adapter_expectation": "supported",
            # The assertion that separates a correct adapter from one that
            # sorted filenames: the FIRST emitted text is chapter three's.
            "first_text": "Circulation",
            "spine_idrefs": ["c3", "c1", "c2"],
        },
    },
    {
        "id": "epub-nonstandard-opf-path",
        "kind": "epub",
        "filename": "book-odd-path.epub",
        # The package document is not at OEBPS/content.opf. An adapter that
        # hard-codes that path fails here with a file-not-found that looks
        # like a malformed book.
        "build": lambda: epub_bytes(
            "content/package.opf", _THREE_ITEMS, ["c1", "c2", "c3"],
            _three_chapter_documents(prefix="content/")),
        "gold": {
            "sha256": "c76fa511e25488e1e86a32da799d2d629a972e05e470f98aeb1643b2f09d7f5a",
            "structures": [],
            "reading_order": ["sp0.0", "sp0.1", "sp0.2",
                              "sp1.0", "sp1.1", "sp1.2",
                              "sp2.0", "sp2.1", "sp2.2"],
            "unsupported": ["navigation document not read: no hierarchical "
                            "table of contents"],
            "adapter_expectation": "supported",
        },
    },
    {
        "id": "epub-fragment-anchors",
        "kind": "epub",
        "filename": "book-anchors.epub",
        "build": lambda: epub_bytes(
            "OEBPS/content.opf", [("c1", "chap1.xhtml")], ["c1"],
            {"OEBPS/chap1.xhtml": xhtml(
                '<section id="sec-airway"><h1>Airway</h1>'
                '<p>Open the airway first.</p></section>'
                '<section id="sec-breathing"><h1>Breathing</h1>'
                '<p>Look for chest rise.</p></section>'
                '<p>An unanchored closing paragraph.</p>')}),
        "gold": {
            "sha256": "1b442e94822a13f4c91e3539d00f143b3bc8573c7b5161d6ec334050d36bdc53",
            "structures": [],
            "reading_order": ["sp0.0", "sp0.1", "sp0.2", "sp0.3", "sp0.4"],
            "unsupported": ["navigation document not read: no hierarchical "
                            "table of contents"],
            "adapter_expectation": "supported",
            "fragments": ["sec-airway", "sec-airway", "sec-breathing",
                          "sec-breathing", None],
        },
    },
    {
        "id": "epub-drm-encrypted",
        "kind": "epub",
        "filename": "book-drm.epub",
        # Structurally valid: its container, spine, and manifest all parse.
        # Only the content is unreadable, which is why the encryption check
        # must come before any content document is read.
        "build": lambda: epub_bytes(
            "OEBPS/content.opf", _THREE_ITEMS, ["c1", "c2", "c3"],
            _three_chapter_documents(),
            extra_parts={"META-INF/encryption.xml": _ENCRYPTION_XML}),
        "gold": {
            "sha256": "7575ef19746737515310ed3b39d5ba7cc14dc6b7353c5251910f845a275fd7a7",
            "structures": [],
            "reading_order": [],
            "unsupported": ["encrypted EPUB: no unauthenticated content"],
            "adapter_expectation": "unsupported",
        },
    },
    {
        "id": "epub-no-container",
        "kind": "epub",
        "filename": "book-no-container.epub",
        "build": lambda: epub_bytes(
            "OEBPS/content.opf", _THREE_ITEMS, ["c1", "c2", "c3"],
            _three_chapter_documents(), with_container=False),
        "gold": {
            "sha256": "fd22a910c6272359076005d914c6045a7354166c4ceda1aefe4b7a28025dadae",
            "structures": [],
            "reading_order": [],
            "unsupported": ["malformed EPUB: no META-INF/container.xml"],
            "adapter_expectation": "unsupported",
        },
    },
    {
        "id": "epub-empty-spine",
        "kind": "epub",
        "filename": "book-empty.epub",
        "build": lambda: epub_bytes(
            "OEBPS/content.opf", _THREE_ITEMS, [],
            _three_chapter_documents()),
        "gold": {
            "sha256": "2039cfc16087137092e4bf9f74604ba09ef296102c41dbaf21a8c81ac4d5686f",
            "structures": [],
            "reading_order": [],
            "unsupported": ["no spine item: the package lists no reading "
                            "order"],
            "adapter_expectation": "unsupported",
        },
    },
]


def materialize(dest_dir):
    """Write every fixture into `dest_dir` and return a list of
    (case_id, path, sha256_of_bytes) records."""
    os.makedirs(dest_dir, exist_ok=True)
    records = []
    for case in CASE_TABLE:
        raw = case["build"]()
        path = os.path.join(dest_dir, case["filename"])
        with open(path, "wb") as fh:
            fh.write(raw)
        records.append((case["id"], path, sha256(raw)))
    return records
