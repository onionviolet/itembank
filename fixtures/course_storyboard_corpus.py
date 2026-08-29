#!/usr/bin/env python3
"""The synthetic course corpus behind Phase 16B's storyboard and route tests.

Every course, objective, lesson, and item named here is invented. Kestrel
County, Mirefield, and Halloway are fictional places; none of this is real
course, exam, clinical, or learner material, and none of it derives from any.
The corpus exists only to drive the 16B shelf, area, and storyboard fixtures.

Any activity-shaped content here means a durable agent or maintenance job, the
Activity IA area. It is a different object from `REQUIREMENTS.md`'s
`ACTIVITY-01/02/03` family of purpose-first learner questions (Decision D6).

Every builder writes deterministic bytes into a caller-supplied destination
directory and never outside it: no `random`, no clock reading, and no path
above `dest_dir`. Each course directory gets exactly one file, named by
`course.COURSE_SIDECAR_FILENAME`, whose current value is `course-graph.md`.
Because that name ends in `.md`, builders must be pointed at a temporary
directory outside the repository; nothing this module writes lands in a path
`itembank guard` walks.
"""
import json
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import course                                                # noqa: E402
import graph                                                 # noqa: E402


# Three invented courses. `attention`, `due_count`, `pending_review_count`,
# `resume_cue`, and `last_activity` have no source in the landed 14B course
# record; they are carried here so every attention state can be exercised, and
# `course_shelf_state` defaults each one when a record omits it.
FICTIONAL_COURSES = (
    {"course_id": "crs-kestrel-01", "name": "Kestrel County Field Basics",
     "attention": "due", "due_count": 3, "pending_review_count": 0,
     "resume_cue": "Continue reading: Airway adjuncts",
     "last_activity": "2026-03-02T09:00:00Z"},
    {"course_id": "crs-mirefield-02", "name": "Mirefield Numeracy",
     "attention": "up_to_date", "due_count": 0, "pending_review_count": 0,
     "resume_cue": "Not started",
     "last_activity": None},
    {"course_id": "crs-halloway-03", "name": "Halloway Systems Reading",
     "attention": "pending_review", "due_count": 0,
     "pending_review_count": 2,
     "resume_cue": "Continue draft review: 2 findings to resolve",
     "last_activity": "2026-03-01T18:30:00Z"},
)

# A malformed sidecar: the real `graph.parse_course` refuses any text whose
# first line is not its title line, so this is genuinely unreadable rather
# than merely odd.
CORRUPT_SIDECAR_TEXT = "this file is not a course graph\n"


class FakeCourseModule(object):
    """An explicit synthetic stand-in for `course.py`, named as a stand-in so
    no reader mistakes it for the real module.

    It exists because the corrupted-record and module-absent branches of
    `ia.course_shelf_state` are otherwise unreachable in a tree whose
    precondition already proved 14B landed. The real `course.py` is exercised
    end to end by `check_shelf_end_to_end`.
    """

    def __init__(self, records, unreadable=()):
        self.COURSE_SIDECAR_FILENAME = course.COURSE_SIDECAR_FILENAME
        self.records = dict(records)
        self.unreadable = set(unreadable)

    def read_course(self, course_root):
        name = os.path.basename(os.path.normpath(course_root))
        if name in self.unreadable:
            raise ValueError("synthetic corrupted course record")
        return self.records[name]


def _sidecar_text(record):
    """A valid course graph naming this fictional course, so a healthy card is
    healthy through the real `course.read_course` as well as through the
    stand-in."""
    object_id = (record["course_id"].replace("-", "")[:16]).ljust(16, "0")
    return graph.serialize_course(
        graph.new_course(record["name"], object_id))


def _make_course_dir(dest_dir, record, text):
    path = os.path.join(dest_dir, record["course_id"])
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, course.COURSE_SIDECAR_FILENAME), "w",
              encoding="utf-8") as fh:
        fh.write(text)
    return path


def build_two_course_shelf(dest_dir):
    """Two healthy fictional courses. Returns the stand-in and the directories
    it made."""
    records, dirs = {}, []
    for record in FICTIONAL_COURSES[:2]:
        dirs.append(_make_course_dir(dest_dir, record, _sidecar_text(record)))
        records[record["course_id"]] = dict(record)
    return FakeCourseModule(records), dirs


def build_corrupted_course(dest_dir):
    """APP-01's fixture: the same two courses, with `crs-mirefield-02`'s record
    unreadable, so one card is healthy and one is degraded."""
    records, dirs = {}, []
    for record in FICTIONAL_COURSES[:2]:
        broken = record["course_id"] == "crs-mirefield-02"
        text = CORRUPT_SIDECAR_TEXT if broken else _sidecar_text(record)
        dirs.append(_make_course_dir(dest_dir, record, text))
        records[record["course_id"]] = dict(record)
    return FakeCourseModule(records, unreadable={"crs-mirefield-02"}), dirs


def build_same_name_pair(dest_dir):
    """Two courses whose display names are identical and whose attention and
    timestamps are equal, so only the course-ID tiebreak can order them."""
    records, dirs = {}, []
    for course_id in ("crs-twin-a", "crs-twin-b"):
        record = {"course_id": course_id, "name": "Field Basics",
                  "attention": "up_to_date", "due_count": 0,
                  "pending_review_count": 0, "resume_cue": "Not started",
                  "last_activity": "2026-03-01T00:00:00Z"}
        dirs.append(_make_course_dir(dest_dir, record, _sidecar_text(record)))
        records[course_id] = record
    return FakeCourseModule(records), dirs


# One fixed mid-loop interruption point per loop. None sits on a boundary
# another loop also uses, so a scenario that resumed the wrong loop would
# produce a visibly wrong step rather than a coincidentally right one.
LOOP_INTERRUPTIONS = {"A": 4, "B": 2, "C": 6, "D": 3, "E": 1, "F": 7, "G": 5}


def build_loop_storyboard(dest_dir):
    """One durable mid-loop position record per loop, written atomically.

    Writes `<dest_dir>/_ia/loop_<letter>.json` for all seven loops, through
    the same write-then-replace shape `ia.write_ia_state` uses, so an
    interrupted write leaves the old file or the new file and never a
    half-written one. Writes no `.md` file, reads no clock, and uses no random
    source. Returns the loop letter to written path mapping.
    """
    directory = os.path.join(dest_dir, "_ia")
    if not os.path.isdir(directory):
        os.makedirs(directory)
    written = {}
    for letter, completed in sorted(LOOP_INTERRUPTIONS.items()):
        record = {"loop": letter, "completed_step": completed,
                  "course_id": "crs-kestrel-01",
                  "last_activity": "2026-03-02T09:00:00Z"}
        final = os.path.join(directory, "loop_%s.json" % letter.lower())
        staged = final + ".tmp"
        with open(staged, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(record, indent=2, ensure_ascii=False))
            fh.flush()
        os.replace(staged, final)
        written[letter] = final
    return written
