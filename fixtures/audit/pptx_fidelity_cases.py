#!/usr/bin/env python3
"""Deterministic, redistributable PPTX byte fixtures plus gold manifests
(Phase 14C, plan 14C-03).

Roster item 2 in `14C-CONTEXT.md`: the lecture deck is the primary artifact
for both live courses, and PPTX was unscoped anywhere in `.planning/` before
this phase. This module is the acceptance corpus the PPTX adapter is held
to: every fixture materializes deterministic bytes into a caller-provided
directory, and the gold manifest publishes the expected slide and shape
locators, reading order, intentionally unsupported structures, and the
SHA-256 of the original bytes.

The bytes are hand-assembled from stdlib `zipfile` and literal XML, never
produced by python-pptx. A fixture built with the library under test proves
only that the library round-trips its own output; a deck authored by
PowerPoint could still fail. The same reasoning built
`locator_fidelity_cases.py`'s DOCX bytes by hand, and this file follows it
part for part.

`expectation` is absent here on purpose. That key belongs to the Phase 11
auditor gate, which enumerates `locator_fidelity_cases.CASE_TABLE` only;
this file carries `adapter_expectation`, whose meaning is the one that file
records: `unsupported` exactly when `reading_order` is empty.

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
# PPTX assembly (stdlib zipfile; fixed entry timestamps for determinism)
# ---------------------------------------------------------------------------

_ZIP_TIME = (2020, 1, 1, 0, 0, 0)

# zipfile.ZipInfo picks create_system from the running platform, so the same
# fixture would hash to two values depending on the checkout machine. Pinned
# to 3 (Unix) for the same reason locator_fidelity_cases.py pins it.
_ZIP_CREATE_SYSTEM = 3

_P = "http://schemas.openxmlformats.org/presentationml/2006/main"
_A = "http://schemas.openxmlformats.org/drawingml/2006/main"
_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
_CT = "application/vnd.openxmlformats-officedocument.presentationml"
_REL_BASE = ("http://schemas.openxmlformats.org/officeDocument/2006/"
             "relationships")


def _entry(name):
    """A ZipInfo whose bytes do not depend on the OS building it."""
    info = zipfile.ZipInfo(name)
    info.date_time = _ZIP_TIME
    info.create_system = _ZIP_CREATE_SYSTEM
    return info


def _zi(xml_bytes):
    return _entry("[Content_Types].xml"), xml_bytes


def content_types_xml(slide_count, notes_for=()):
    overrides = [
        '<Override PartName="/ppt/presentation.xml" ContentType="%s'
        '.presentation.main+xml"/>' % _CT,
        '<Override PartName="/ppt/slideMasters/slideMaster1.xml" '
        'ContentType="%s.slideMaster+xml"/>' % _CT,
        '<Override PartName="/ppt/slideLayouts/slideLayout1.xml" '
        'ContentType="%s.slideLayout+xml"/>' % _CT,
    ]
    for number in range(1, slide_count + 1):
        overrides.append('<Override PartName="/ppt/slides/slide%d.xml" '
                         'ContentType="%s.slide+xml"/>' % (number, _CT))
    for number in notes_for:
        overrides.append('<Override PartName="/ppt/notesSlides/notesSlide%d'
                         '.xml" ContentType="%s.notesSlide+xml"/>'
                         % (number, _CT))
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/'
            'content-types">'
            '<Default Extension="rels" ContentType="application/vnd.'
            'openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '%s</Types>' % "".join(overrides))


def _rels(pairs):
    """One relationships part. `pairs` are (id, type_suffix, target)."""
    items = "".join(
        '<Relationship Id="%s" Type="%s/%s" Target="%s"/>'
        % (rid, _REL_BASE, kind, target) for rid, kind, target in pairs)
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/'
            '2006/relationships">%s</Relationships>' % items)


def shape_xml(shape_id, name, text):
    """One text-bearing shape. `text` of None builds a picture shape instead,
    which is what a media-only slide carries."""
    if text is None:
        return ('<p:pic><p:nvPicPr><p:cNvPr id="%d" name="%s"/>'
                '<p:cNvPicPr/><p:nvPr/></p:nvPicPr>'
                '<p:blipFill><a:blip r:embed="rId9"/><a:stretch/></p:blipFill>'
                '<p:spPr/></p:pic>' % (shape_id, name))
    return ('<p:sp><p:nvSpPr><p:cNvPr id="%d" name="%s"/><p:cNvSpPr/>'
            '<p:nvPr/></p:nvSpPr><p:spPr/><p:txBody><a:bodyPr/><a:lstStyle/>'
            '<a:p><a:r><a:rPr lang="en-US"/><a:t>%s</a:t></a:r></a:p>'
            '</p:txBody></p:sp>' % (shape_id, name, text))


def slide_xml(shapes):
    """`shapes` are (name, text) pairs; a text of None is a picture."""
    body = "".join(shape_xml(index + 2, name, text)
                   for index, (name, text) in enumerate(shapes))
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<p:sld xmlns:a="%s" xmlns:r="%s" xmlns:p="%s"><p:cSld>'
            '<p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/>'
            '<p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/>'
            '%s</p:spTree></p:cSld><p:clrMapOvr/></p:sld>'
            % (_A, _R, _P, body))


def notes_xml(text):
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<p:notes xmlns:a="%s" xmlns:r="%s" xmlns:p="%s"><p:cSld>'
            '<p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/>'
            '<p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/>'
            '<p:sp><p:nvSpPr><p:cNvPr id="2" name="Notes Placeholder 1"/>'
            '<p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
            '<p:nvPr><p:ph type="body" idx="1"/></p:nvPr></p:nvSpPr>'
            '<p:spPr/><p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:r>'
            '<a:rPr lang="en-US"/><a:t>%s</a:t></a:r></a:p></p:txBody>'
            '</p:sp></p:spTree></p:cSld></p:notes>' % (_A, _R, _P, text))


def presentation_xml(slide_rids):
    """`slide_rids` in the order the deck reads, which is the whole point of
    the reordered case: the sldId list is the order, the part filenames are
    not."""
    ids = "".join('<p:sldId id="%d" r:id="%s"/>' % (256 + index, rid)
                  for index, rid in enumerate(slide_rids))
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<p:presentation xmlns:a="%s" xmlns:r="%s" xmlns:p="%s">'
            '<p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rIdM"/>'
            '</p:sldMasterIdLst>'
            '<p:sldIdLst>%s</p:sldIdLst>'
            '<p:sldSz cx="9144000" cy="6858000"/>'
            '<p:notesSz cx="6858000" cy="9144000"/></p:presentation>'
            % (_A, _R, _P, ids))


_SLIDE_MASTER = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<p:sldMaster xmlns:a="%s" xmlns:r="%s" xmlns:p="%s"><p:cSld>'
    '<p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/>'
    '<p:nvPr/></p:nvGrpSpPr><p:grpSpPr/></p:spTree></p:cSld>'
    '<p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" '
    'accent2="accent2" accent3="accent3" accent4="accent4" '
    'accent5="accent5" accent6="accent6" hlink="hlink" '
    'folHlink="folHlink"/>'
    '<p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/>'
    '</p:sldLayoutIdLst></p:sldMaster>' % (_A, _R, _P))

_SLIDE_LAYOUT = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<p:sldLayout xmlns:a="%s" xmlns:r="%s" xmlns:p="%s" type="blank">'
    '<p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/>'
    '<p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/></p:spTree>'
    '</p:cSld><p:clrMapOvr/></p:sldLayout>' % (_A, _R, _P))


def pptx_bytes(slides, notes=None, slide_order=None):
    """Assemble a minimal .pptx package.

    `slides` is a list of shape lists, one per `ppt/slides/slideN.xml` part,
    in part-name order. `notes` maps a one-based slide part number to its
    notes text. `slide_order` is the list of relationship ids in reading
    order; the default is part-name order, and the reordered case passes the
    reverse to prove the adapter reads the sldId list rather than sorting
    filenames.
    """
    notes = notes or {}
    count = len(slides)
    rids = ["rId%d" % (index + 1) for index in range(count)]
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(*_zi(content_types_xml(count, sorted(notes))))
        zf.writestr(_entry("_rels/.rels"),
                    _rels([("rId1", "officeDocument", "ppt/presentation.xml")]))
        zf.writestr(_entry("ppt/presentation.xml"),
                    presentation_xml(slide_order or rids))
        presentation_rels = [
            (rid, "slide", "slides/slide%d.xml" % (index + 1))
            for index, rid in enumerate(rids)]
        presentation_rels.append(
            ("rIdM", "slideMaster", "slideMasters/slideMaster1.xml"))
        zf.writestr(_entry("ppt/_rels/presentation.xml.rels"),
                    _rels(presentation_rels))
        zf.writestr(_entry("ppt/slideMasters/slideMaster1.xml"), _SLIDE_MASTER)
        zf.writestr(_entry("ppt/slideMasters/_rels/slideMaster1.xml.rels"),
                    _rels([("rId1", "slideLayout",
                            "../slideLayouts/slideLayout1.xml")]))
        zf.writestr(_entry("ppt/slideLayouts/slideLayout1.xml"), _SLIDE_LAYOUT)
        zf.writestr(_entry("ppt/slideLayouts/_rels/slideLayout1.xml.rels"),
                    _rels([("rId1", "slideMaster",
                            "../slideMasters/slideMaster1.xml")]))
        for index, shapes in enumerate(slides, start=1):
            zf.writestr(_entry("ppt/slides/slide%d.xml" % index),
                        slide_xml(shapes))
            slide_rels = [("rId1", "slideLayout",
                           "../slideLayouts/slideLayout1.xml")]
            if index in notes:
                slide_rels.append(("rId2", "notesSlide",
                                   "../notesSlides/notesSlide%d.xml" % index))
            zf.writestr(_entry("ppt/slides/_rels/slide%d.xml.rels" % index),
                        _rels(slide_rels))
        for number, text in sorted(notes.items()):
            zf.writestr(_entry("ppt/notesSlides/notesSlide%d.xml" % number),
                        notes_xml(text))
            zf.writestr(
                _entry("ppt/notesSlides/_rels/notesSlide%d.xml.rels" % number),
                _rels([("rId1", "slide", "../slides/slide%d.xml" % number)]))
    return buf.getvalue()


# ---------------------------------------------------------------------------
# the immutable case table
# ---------------------------------------------------------------------------

CASE_TABLE = [
    {
        "id": "pptx-two-slides-text",
        "kind": "pptx",
        "filename": "pptx-two-slides.pptx",
        "build": lambda: pptx_bytes([
            [("Title 1", "Airway Management"),
             ("Body 2", "Assess responsiveness first.")],
            [("Body 1", "Then open the airway.")],
        ]),
        "gold": {
            "sha256": "da6374623877c45935ecbfdae81105329afbcb0605210d69853ea79f70d55a3e",
            "structures": [
                {"kind": "slide", "slide": 1, "shape_index": 0,
                 "text": "Airway Management"},
                {"kind": "slide", "slide": 1, "shape_index": 1,
                 "text": "Assess responsiveness first."},
                {"kind": "slide", "slide": 2, "shape_index": 0,
                 "text": "Then open the airway."},
            ],
            "reading_order": ["s1.0", "s1.1", "s2.0"],
            "unsupported": [],
            "adapter_expectation": "supported",
        },
    },
    {
        "id": "pptx-speaker-notes",
        "kind": "pptx",
        "filename": "pptx-notes.pptx",
        "build": lambda: pptx_bytes(
            [[("Body 1", "Oxygen delivery devices")]],
            notes={1: "Mention the Venturi mask flow rates."}),
        "gold": {
            "sha256": "9711ab3bc5f3d5dc3accd91e0bdbe026c14938fadf712773e3d79cba2375ebeb",
            "structures": [
                {"kind": "slide", "slide": 1, "shape_index": 0,
                 "text": "Oxygen delivery devices"},
                {"kind": "notes", "slide": 1, "notes": True,
                 "text": "Mention the Venturi mask flow rates."},
            ],
            "reading_order": ["s1.0", "s1.n0"],
            "unsupported": [],
            "adapter_expectation": "supported",
        },
    },
    {
        "id": "pptx-reordered-slides",
        "kind": "pptx",
        "filename": "pptx-reordered.pptx",
        # Two slide parts named slide1.xml and slide2.xml, listed in
        # presentation.xml in the opposite order. The deck reads slide2 first.
        "build": lambda: pptx_bytes(
            [[("Body 1", "This part is named slide1.")],
             [("Body 1", "This part is named slide2.")]],
            slide_order=["rId2", "rId1"]),
        "gold": {
            "sha256": "5f8b3ee483d6ab73c5324f16dcd38a3237b80fd348e24a2a2bf74af918c6f1b1",
            "structures": [
                {"kind": "slide", "slide": 1, "shape_index": 0,
                 "text": "This part is named slide2."},
                {"kind": "slide", "slide": 2, "shape_index": 0,
                 "text": "This part is named slide1."},
            ],
            "reading_order": ["s1.0", "s2.0"],
            "unsupported": [],
            "adapter_expectation": "supported",
            # The assertion that separates a correct adapter from one that
            # sorted filenames: the FIRST emitted text is slide2's.
            "first_text": "This part is named slide2.",
        },
    },
    {
        "id": "pptx-video-only-slide",
        "kind": "pptx",
        "filename": "pptx-video-slide.pptx",
        "build": lambda: pptx_bytes([
            [("Body 1", "Ventilation demonstration")],
            [("Video 1", None)],
        ]),
        "gold": {
            "sha256": "0f569fcdeae8b30758d8bed813c70b1b78f5f8a48a2a2feb6ab009769d2ca4a2",
            "structures": [
                {"kind": "slide", "slide": 1, "shape_index": 0,
                 "text": "Ventilation demonstration"},
            ],
            "reading_order": ["s1.0"],
            "unsupported": ["slide 2: media-only slide, no text-bearing shape"],
            "adapter_expectation": "supported",
        },
    },
    {
        "id": "pptx-all-media-slides",
        "kind": "pptx",
        "filename": "pptx-all-media.pptx",
        "build": lambda: pptx_bytes([[("Video 1", None)]]),
        "gold": {
            "sha256": "69bff7f32d4e870599b4dc08679d543cb415dfef45125d1f429071f22d002035",
            "structures": [],
            "reading_order": [],
            "unsupported": ["media-only deck: no text-bearing shape"],
            "adapter_expectation": "unsupported",
        },
    },
    {
        "id": "pptx-malformed-truncated",
        "kind": "pptx",
        "filename": "pptx-truncated.pptx",
        "build": lambda: pptx_bytes([
            [("Title 1", "Airway Management"),
             ("Body 2", "Assess responsiveness first.")],
            [("Body 1", "Then open the airway.")],
        ])[:200],
        "gold": {
            "sha256": "63fb66877bc9aaf61088d261eddfb13882e39b3a95da3f9a7b16fd6daf394bba",
            "structures": [],
            "reading_order": [],
            "unsupported": ["malformed/truncated PPTX"],
            "adapter_expectation": "unsupported",
        },
    },
]


def materialize(dest_dir):
    """Write every fixture into `dest_dir` and return a list of
    (case_id, path, sha256_of_bytes) records. Pure file materialization;
    no adapter is invoked here."""
    os.makedirs(dest_dir, exist_ok=True)
    records = []
    for case in CASE_TABLE:
        raw = case["build"]()
        path = os.path.join(dest_dir, case["filename"])
        with open(path, "wb") as fh:
            fh.write(raw)
        records.append((case["id"], path, sha256(raw)))
    return records
