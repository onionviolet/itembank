#!/usr/bin/env python3
"""Focused Practice/Test projection and runtime-launch checks."""
import os
import shutil
import sys
import tempfile
from types import SimpleNamespace
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from surfaces import daemon


def fail(message):
    raise AssertionError(message)


def check_treatment_classification():
    root = tempfile.mkdtemp(prefix="course_assessment_area_")
    try:
        banks = [("practice_bank", os.path.join(root, "practice_bank.md")),
                 ("formal_bank", os.path.join(root, "formal_bank.md")),
                 ("semicolon_bank", os.path.join(root, "semicolon_bank.md")),
                 ("space_bank", os.path.join(root, "space_bank.md")),
                 ("unbound_bank", os.path.join(root, "unbound_bank.md"))]
        doc = {"sources": [
            {"source_object_id": "source-a"},
            {"source_object_id": "source-b"},
            {"source_object_id": "source-c"},
            {"source_object_id": "source-d"},
            {"source_object_id": "source-e"},
        ], "bindings": [
            {"binding_kind": "treatment", "source_object_id": "source-a",
             "treatment_kind": "practice",
             "locator": "practice_bank.md, Q1-Q2"},
            {"binding_kind": "treatment", "source_object_id": "source-b",
             "treatment_kind": "formal-test", "locator": "formal_bank.md"},
            {"binding_kind": "treatment", "source_object_id": "source-c",
             "treatment_kind": "formal-test", "locator": "../outside.md"},
            {"binding_kind": "treatment", "source_object_id": "source-d",
             "treatment_kind": "practice",
             "locator": "semicolon_bank.md; selected items"},
            {"binding_kind": "treatment", "source_object_id": "source-e",
             "treatment_kind": "formal-test", "locator": "space_bank.md Q1-Q4"},
            {"binding_kind": "treatment", "source_object_id": "not-a-source",
             "treatment_kind": "practice", "locator": "unbound_bank.md"},
        ]}
        mapped = daemon._course_bank_treatments(root, doc, banks)
        if mapped != {"practice_bank": {"practice"},
                      "formal_bank": {"formal-test"},
                      "semicolon_bank": {"practice"},
                      "space_bank": {"formal-test"},
                      "unbound_bank": set()}:
            fail("assessment treatments were not classified by contained locator: %r"
                 % mapped)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def check_superseded_binding_does_not_publish_twice():
    root = tempfile.mkdtemp(prefix="course_assessment_revision_")
    try:
        bank = os.path.join(root, "unit.md")
        rows = [
            {"binding_kind": "treatment", "source_object_id": "source",
             "treatment_kind": "practice", "locator": "unit.md",
             "binding_id": "a" * 16, "binding_revision_id": "b" * 16,
             "supersedes_binding_revision_id": ""},
            {"binding_kind": "treatment", "source_object_id": "source",
             "treatment_kind": "formal-test", "locator": "unit.md",
             "binding_id": "a" * 16, "binding_revision_id": "c" * 16,
             "supersedes_binding_revision_id": "b" * 16},
        ]
        mapped = daemon._course_bank_treatments(
            root, {"sources": [{"source_object_id": "source"}],
                   "bindings": rows}, [("unit", bank)])
        if mapped["unit"] != {"formal-test"}:
            fail("a superseded practice binding still published: %r" % mapped)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def check_area_rows_keep_practice_and_test_separate():
    root = tempfile.mkdtemp(prefix="course_assessment_rows_")
    try:
        practice_path = os.path.join(root, "practice.md")
        formal_path = os.path.join(root, "formal.md")
        fixture = os.path.join(ROOT, "fixtures", "sample_bank.md")
        shutil.copyfile(fixture, practice_path)
        shutil.copyfile(fixture, formal_path)
        doc = {"sources": [{"source_object_id": "source"}], "bindings": [
            {"binding_kind": "treatment", "source_object_id": "source",
             "objective": "study:spacing", "treatment_kind": "practice",
             "locator": "practice.md"},
            {"binding_kind": "treatment", "source_object_id": "source",
             "objective": "study:spacing", "treatment_kind": "formal-test",
             "locator": "formal.md"},
        ]}
        handler = SimpleNamespace(
            banks={"practice": practice_path, "formal": formal_path})
        with mock.patch("course.read_course", return_value={"doc": doc}):
            _lead, practice = daemon._course_area_rows(
                handler, {"area": "practice", "course_id": "course"}, root)
            _lead, formal = daemon._course_area_rows(
                handler, {"area": "test", "course_id": "course"}, root)
        if [row["bank_stem"] for row in practice] != ["practice"] or \
                practice[0]["href"] != "/quiz/practice?mode=practice":
            fail("Practice published the wrong assessment rows: %r" % practice)
        if [row["bank_stem"] for row in formal] != ["formal"] or \
                formal[0]["href"] != "/quiz/formal?mode=exam":
            fail("Test published the wrong assessment rows: %r" % formal)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def check_mode_specific_runtime_configs():
    handler = SimpleNamespace(
        sessions={"unit": {"mode": "practice", "selection_mode": "practice",
                           "session_id": "ordinary", "seed": 7}},
        quiz_mode_sessions={})
    practice = daemon._quiz_session_config(handler, "unit", "practice")
    exam = daemon._quiz_session_config(handler, "unit", "exam")
    if practice is exam or practice["mode"] != "practice" or exam["mode"] != "exam":
        fail("Practice and Test did not receive separate feedback-mode configs")
    if practice["selection_mode"] != "practice" or exam["selection_mode"] != "exam":
        fail("Practice and Test did not receive separate selection modes")
    if handler.sessions["unit"]["seed"] != 7 or exam["seed"] != 0:
        fail("the formal fixed seed mutated the ordinary bank configuration")
    if daemon._quiz_session_config(handler, "unit", "exam") is not exam:
        fail("the formal sitting slot was not stable across requests")
    if daemon._quiz_path("unit", "exam", answer=True) != \
            "/quiz/unit/answer?mode=exam":
        fail("the answer route dropped its formal mode")


def check_existing_runtime_receives_formal_mode():
    root = tempfile.mkdtemp(prefix="course_assessment_runtime_")
    try:
        handler = SimpleNamespace(root=root, sessions={"unit": {}},
                                  quiz_mode_sessions={})
        cfg = {"mode": "exam", "selection_mode": "exam", "seed": 0,
               "session_id": "formal"}
        created = {"session_id": "runtime-formal"}
        with mock.patch.object(daemon, "api_session_path", return_value=None), \
                mock.patch.object(daemon, "_saved_quiz_session", return_value=None), \
                mock.patch.object(daemon.session, "do_start", return_value=created) as start:
            daemon._ensure_quiz_session(handler, "unit", os.path.join(root, "unit.md"),
                                        [{"id": "q1"}], cfg)
        args = start.call_args.args
        if args[2] != "exam" or args[1]["selection_mode"] != "exam":
            fail("the formal launcher did not delegate mode authority to the runtime")
        if args[1]["count"] != 1 or args[1]["seed"] != 0:
            fail("the formal launcher did not request the complete fixed sitting")
    finally:
        shutil.rmtree(root, ignore_errors=True)


def main():
    check_treatment_classification()
    check_superseded_binding_does_not_publish_twice()
    check_area_rows_keep_practice_and_test_separate()
    check_mode_specific_runtime_configs()
    check_existing_runtime_receives_formal_mode()
    print("course assessment areas: bindings classify Practice/Test and Test uses a separate fixed exam sitting")


if __name__ == "__main__":
    main()
