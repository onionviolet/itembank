#!/usr/bin/env python3
"""Plan 16D-01: the pacing ladder, its lint findings, and rung-3 additivity.

Pacing is authored and read through a precedence ladder (D-PACED-1,
16D-CONTEXT D-16D-1/D-16D-2): an explicit `[STEP: <id>]` marker wins, else
the configured `[LESSON-PACE:]` heading level, else the whole document as
one step, which must be byte-identical to pre-16D behaviour. A step id is a
resumable identity, so it must survive edits elsewhere in the document, and
malformed or duplicated ids are lint errors rather than silent fallbacks.

Standard library only, no test framework, runnable as
`python tests/paced_steps_roundtrip.py`. Writes only under a temp dir.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import model                                           # noqa: E402

FIXTURE = os.path.join(ROOT, "fixtures", "paced_lesson_bank.md")
PLAIN = os.path.join(ROOT, "fixtures", "lesson_bank.md")


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def ok(msg):
    print("ok: " + msg)


def check_rung1():
    lesson = model.parse_lesson(FIXTURE)
    steps = model.lesson_steps(lesson)
    ids = [s["id"] for s in steps]
    if ids != ["intro", "orientation", "mechanism", "application"]:
        fail("rung 1 ids are %r" % ids)
    if any(s["rung"] != 1 for s in steps):
        fail("rung 1 steps must all carry rung 1")
    for s in steps:
        if "[STEP:" in s["content"]:
            fail("marker line leaked into step %s content" % s["id"])
    if steps[1]["title"] != "What A Keeper Watches":
        fail("step title should be the first heading inside the step, got %r"
             % steps[1]["title"])
    ok("rung 1: four steps in document order, markers never rendered")


def check_marker_precedence():
    lesson = model.parse_lesson(FIXTURE)
    if lesson["pace"] != "h3":
        fail("the fixture's [LESSON-PACE: h3] did not parse: %r"
             % lesson["pace"])
    steps = model.lesson_steps(lesson)
    if steps[0]["rung"] != 1:
        fail("markers must win over the configured pace (ladder precedence)")
    ok("precedence: authored markers beat [LESSON-PACE: h3]")


def check_rung2():
    text = open(FIXTURE, encoding="utf-8").read()
    stripped = re.sub(r"(?m)^\[STEP:.*\n?", "", text)
    work = tempfile.mkdtemp()
    try:
        path = os.path.join(work, "rung2.md")
        open(path, "w", encoding="utf-8").write(stripped)
        lesson = model.parse_lesson(path)
        steps = model.lesson_steps(lesson)
        slugs = [h["slug"] for h in lesson["headings"]]
        got = [s["id"] for s in steps if s["id"] != "intro"]
        if got != slugs:
            fail("rung 2 ids %r are not the heading slugs %r" % (got, slugs))
        if any(s["rung"] != 2 for s in steps):
            fail("rung 2 steps must all carry rung 2")
        if steps[0]["id"] != "intro":
            fail("prose before the first heading must become the intro step")
    finally:
        shutil.rmtree(work, ignore_errors=True)
    ok("rung 2: one step per ### heading, ids are the existing slugs")


def check_rung3_additivity():
    lesson = model.parse_lesson(PLAIN)
    steps = model.lesson_steps(lesson)
    if len(steps) != 1 or steps[0]["id"] != "document" or steps[0]["rung"] != 3:
        fail("a markerless, pace-less lesson must be one whole-document step")
    if steps[0]["content"] != lesson["body"]:
        fail("rung 3 content must be the effective lesson text, unsliced")
    expected_keys = {
        "source", "gate", "semantic_profile", "semantic_profile_raw",
        "lang", "lang_raw", "dir", "dir_raw", "dir_declared",
        "example_order", "example_order_reason", "pace", "pace_raw",
        "body", "intro", "headings", "error", "detail"}
    if set(lesson.keys()) != expected_keys:
        fail("parse_lesson key set drifted: %r"
             % sorted(set(lesson.keys()) ^ expected_keys))
    if lesson["pace"] != "none" or lesson["pace_raw"] != "":
        fail("a lesson that never asked for pacing must read pace none")
    ok("rung 3: whole document, and parse_lesson grew only the pace pair")


def check_identity_stability():
    text = open(FIXTURE, encoding="utf-8").read()
    edited = text.replace("## LESSON\n", "## LESSON\n\n[STEP: preface]\n", 1)
    work = tempfile.mkdtemp()
    try:
        path = os.path.join(work, "edited.md")
        open(path, "w", encoding="utf-8").write(edited)
        steps = model.lesson_steps(model.parse_lesson(path))
        ids = [s["id"] for s in steps]
        if ids != ["preface", "orientation", "mechanism", "application"]:
            fail("inserting an earlier marker changed later ids: %r" % ids)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    ok("identity: an inserted earlier step renames no later step")


def lint_of(text):
    work = tempfile.mkdtemp()
    try:
        path = os.path.join(work, "bank.md")
        open(path, "w", encoding="utf-8").write(text)
        r = subprocess.run(
            [sys.executable, os.path.join(ROOT, "itembank.py"), "lint", path],
            capture_output=True, text=True, encoding="utf-8")
        return r.stdout + r.stderr
    finally:
        shutil.rmtree(work, ignore_errors=True)


def check_lint_findings():
    text = open(FIXTURE, encoding="utf-8").read()
    out = lint_of(text.replace("[STEP: orientation]", "[STEP: Bad_Id!]"))
    if "id must be 1-64 chars" not in out:
        fail("lesson.invalid_step did not fire on a malformed id")
    out = lint_of(text.replace("[STEP: mechanism]", "[STEP: orientation]"))
    if "appears more than once" not in out:
        fail("lesson.duplicate_step did not fire on a duplicated id")
    out = lint_of(text.replace("[LESSON-PACE: h3]", "[LESSON-PACE: pages]"))
    if "is not one of none, h3" not in out:
        fail("lesson.invalid_pace did not fire on an unknown value")
    r = subprocess.run(
        [sys.executable, os.path.join(ROOT, "itembank.py"), "lint", FIXTURE],
        capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0 or " 0 errors" not in r.stdout:
        fail("the shipped fixture must lint with zero errors:\n" + r.stdout)
    ok("lint: invalid_step, duplicate_step, invalid_pace all fire; "
       "the shipped fixture is clean")


def main():
    check_rung1()
    check_marker_precedence()
    check_rung2()
    check_rung3_additivity()
    check_identity_stability()
    check_lint_findings()
    print("PASS paced_steps_roundtrip.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
