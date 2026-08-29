#!/usr/bin/env python3
"""Deterministic transcript byte fixtures plus gold manifests
(Phase 14C, plan 14C-05).

Roster item 4 in `14C-CONTEXT.md` is sequenced ahead of ASR for one reason:
a learner-supplied `.srt`, `.vtt`, or hand-typed timestamped transcript needs
no speech backend, so it lands cheaply and proves the timestamp locator.
These fixtures are that locator's acceptance corpus, and roster item 5 will
reuse them unchanged, because ASR is a new way of producing cues and not a
new locator shape or a new sidecar field.

Four of the eight cases exist because real caption files differ from tidy
ones: a Windows export carries a byte order mark and CRLF endings, a WebVTT
file routinely omits the hour field, a styled WebVTT carries NOTE, STYLE, and
REGION blocks between its cues, and a hand-edited file sometimes carries a
cue whose end precedes its start.

`expectation` is absent here for the same reason it is absent from the two
sibling files added by plans 14C-03 and 14C-04: that key belongs to the Phase
11 auditor gate, which enumerates `locator_fidelity_cases.CASE_TABLE` only.
This file carries `adapter_expectation`, `unsupported` exactly when
`reading_order` is empty.

Stdlib only (hashlib, os) and repository-independent: the case table is
immutable data, the builders are pure functions, and nothing here reads or
writes the repository.
"""
import hashlib
import os


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


# ---------------------------------------------------------------------------
# builders
# ---------------------------------------------------------------------------

def srt_bytes(cues, bom=False, crlf=False):
    """`cues` are (start, end, lines) triples with timestamps already spelled
    the way the fixture wants them tested."""
    blocks = []
    for number, (start, end, lines) in enumerate(cues, start=1):
        body = "\n".join(lines)
        blocks.append("%d\n%s --> %s\n%s" % (number, start, end, body))
    text = "\n\n".join(blocks) + "\n"
    if crlf:
        text = text.replace("\n", "\r\n")
    raw = text.encode("utf-8")
    if bom:
        raw = b"\xef\xbb\xbf" + raw
    return raw


def vtt_bytes(cues, header_blocks=None):
    parts = ["WEBVTT"]
    for block in header_blocks or []:
        parts.append(block)
    for start, end, lines in cues:
        # An `end` of None means `start` already holds the whole timing line,
        # which is how the cue-settings case carries its trailing
        # `align:start position:10%` without a second builder.
        timing = start if end is None else "%s --> %s" % (start, end)
        parts.append("%s\n%s" % (timing, "\n".join(lines)))
    return ("\n\n".join(parts) + "\n").encode("utf-8")


def plain_bytes(lines):
    return ("\n".join(lines) + "\n").encode("utf-8")


# ---------------------------------------------------------------------------
# the immutable case table
# ---------------------------------------------------------------------------

_THREE_CUES = [
    ("00:00:01,000", "00:00:04,500", ["Airway comes first."]),
    ("00:00:04,500", "00:00:09,250", ["Then breathing."]),
    ("00:01:02,500", "00:01:06,000", ["Then circulation."]),
]

_THREE_CUES_NO_HOUR = [
    ("00:01.000", "00:04.500", ["Airway comes first."]),
    ("00:04.500", "00:09.250", ["Then breathing."]),
    ("01:02.500", "01:06.000", ["Then circulation."]),
]

CASE_TABLE = [
    {
        "id": "srt-three-cues",
        "kind": "transcript",
        "filename": "lecture.srt",
        "build": lambda: srt_bytes(_THREE_CUES),
        "gold": {
            "sha256": "21a97788224c839682c6632133efd4ee8294ac695b8758a046e253d4014fc5a2",
            "structures": [
                {"kind": "cue", "cue_index": 0, "start_ms": 1000,
                 "end_ms": 4500, "text": "Airway comes first."},
                {"kind": "cue", "cue_index": 1, "start_ms": 4500,
                 "end_ms": 9250, "text": "Then breathing."},
                {"kind": "cue", "cue_index": 2, "start_ms": 62500,
                 "end_ms": 66000, "text": "Then circulation."},
            ],
            "reading_order": ["c.0", "c.1", "c.2"],
            "unsupported": [],
            "adapter_expectation": "supported",
            "start_ms": [1000, 4500, 62500],
            "end_ms": [4500, 9250, 66000],
        },
    },
    {
        "id": "srt-multiline-cue",
        "kind": "transcript",
        "filename": "lecture-multiline.srt",
        "build": lambda: srt_bytes([
            ("00:00:01,000", "00:00:06,000",
             ["A patent airway is the first", "priority in every patient",
              "regardless of mechanism."]),
        ]),
        "gold": {
            "sha256": "80867a880d1c65ad0889e51235e130b7260c94d9ad39dda61b25793505cffd11",
            "structures": [
                {"kind": "cue", "cue_index": 0, "start_ms": 1000,
                 "end_ms": 6000,
                 "text": "A patent airway is the first priority in every "
                         "patient regardless of mechanism."},
            ],
            "reading_order": ["c.0"],
            "unsupported": [],
            "adapter_expectation": "supported",
        },
    },
    {
        "id": "srt-bom-and-crlf",
        "kind": "transcript",
        "filename": "lecture-bom.srt",
        # What a Windows-exported caption file actually looks like. The BOM
        # and the line endings must not shift the parse by one character.
        "build": lambda: srt_bytes(_THREE_CUES, bom=True, crlf=True),
        "gold": {
            "sha256": "30c78e2d54016e73ba551b4919592040730a93a8ca8b06214267bc3d20a2018e",
            "structures": [],
            "reading_order": ["c.0", "c.1", "c.2"],
            "unsupported": [],
            "adapter_expectation": "supported",
        },
    },
    {
        "id": "vtt-hour-omitted",
        "kind": "transcript",
        "filename": "lecture.vtt",
        # The single most likely way this adapter fails on real material: a
        # regex that requires HH: rejects most real WebVTT files.
        "build": lambda: vtt_bytes(_THREE_CUES_NO_HOUR),
        "gold": {
            "sha256": "95c229c400239e5551c3da43915b48f78f47929a744bcca2e97c5186db9ec674",
            "structures": [],
            "reading_order": ["c.0", "c.1", "c.2"],
            "unsupported": [],
            "adapter_expectation": "supported",
            "start_ms": [1000, 4500, 62500],
            "end_ms": [4500, 9250, 66000],
        },
    },
    {
        "id": "vtt-with-settings-and-notes",
        "kind": "transcript",
        "filename": "lecture-styled.vtt",
        "build": lambda: vtt_bytes(
            [("00:00:01.000 --> 00:00:04.500 align:start position:10%",
              None, ["Airway comes first."]),
             ("00:00:04.500 --> 00:00:09.250 align:middle",
              None, ["Then breathing."])],
            header_blocks=["NOTE this deck was exported twice",
                           "STYLE\n::cue { color: white }",
                           "REGION\nid:top width:40%"]),
        "gold": {
            "sha256": "901ee9f66888f4016eb87a7d9e014923b741f6430332c0dae65711251f655106",
            "structures": [],
            "reading_order": ["c.0", "c.1"],
            "unsupported": ["skipped a NOTE block", "skipped a STYLE block",
                            "skipped a REGION block"],
            "adapter_expectation": "supported",
        },
    },
    {
        "id": "plain-bracketed-timestamps",
        "kind": "transcript",
        "filename": "lecture-notes.txt",
        "build": lambda: plain_bytes([
            "[00:00:05] The primary survey begins with the airway.",
            "[00:00:30] Breathing is assessed next.",
            "[00:01:10] Circulation closes the survey.",
        ]),
        "gold": {
            "sha256": "9b50f688f75d96ae5ff0946c5b060d055b872b805355e7ede738df3a3d936c1d",
            "structures": [
                {"kind": "cue", "cue_index": 0, "start_ms": 5000,
                 "end_ms": 30000},
                {"kind": "cue", "cue_index": 1, "start_ms": 30000,
                 "end_ms": 70000},
                {"kind": "cue", "cue_index": 2, "start_ms": 70000,
                 "end_ms": 70000},
            ],
            "reading_order": ["c.0", "c.1", "c.2"],
            "unsupported": [],
            "adapter_expectation": "supported",
            "start_ms": [5000, 30000, 70000],
            "end_ms": [30000, 70000, 70000],
        },
    },
    {
        "id": "srt-end-before-start",
        "kind": "transcript",
        "filename": "lecture-inverted.srt",
        "build": lambda: srt_bytes([
            ("00:00:01,000", "00:00:04,500", ["Airway comes first."]),
            ("00:00:09,000", "00:00:04,000", ["This cue is inverted."]),
            ("00:00:10,000", "00:00:12,000", ["Then circulation."]),
        ]),
        "gold": {
            "sha256": "46975f92500de4abae10908a7683590d4f00bdd1bf819388e217b29a87b01f8d",
            "structures": [],
            "reading_order": ["c.0", "c.1"],
            "unsupported": ["cue 2: end timestamp precedes start timestamp"],
            "adapter_expectation": "supported",
        },
    },
    {
        "id": "transcript-no-timestamps",
        "kind": "transcript",
        "filename": "lecture-plain.txt",
        "build": lambda: plain_bytes([
            "The primary survey begins with the airway.",
            "Breathing is assessed next.",
        ]),
        "gold": {
            "sha256": "c93850fa9b1e0b92d71a616f03ed17ce90dd5f4ebe9196791c9927824926430a",
            "structures": [],
            "reading_order": [],
            # A transcript with no timestamps is a plain text file and belongs
            # to the `text` adapter. The refusal says so rather than producing
            # cues with invented timings.
            "unsupported": ["no timestamped cue found"],
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
