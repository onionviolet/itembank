#!/usr/bin/env python3
"""Regressions from fresh review of learner drafts and bounded source search."""
from pathlib import Path
import builtins
import shutil
import subprocess
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]

import journal
import course
import model
import notes
from surfaces import course_source_search, course_workbench, day, learner_artifacts
import learner_artifacts_roundtrip as artifact_tests
import course_source_search_roundtrip as source_tests
from course_guidance_journey_roundtrip import fixture, snapshot


class DraftAdmission(unittest.TestCase):
    def setUp(self):
        self.case = artifact_tests.LearnerArtifact("test_readonly_no_session_and_script_free_form_contract")
        self.case.setUp()
        self.addCleanup(self.case.tearDown)

    def test_question_changed_after_form_validation_refuses_first_save(self):
        case = self.case
        body = case.body(wording="My original explanation of the earlier question.")
        original = learner_artifacts._target
        calls = 0

        def change_before_save(bank_path, item_ref):
            nonlocal calls
            calls += 1
            if calls == 2:
                case.bank.write_text(case.bank.read_text().replace(
                    "Explain an unfamiliar boundary rule", "Explain a revised boundary rule"))
            return original(bank_path, item_ref)

        with patch.object(learner_artifacts, "_target", side_effect=change_before_save):
            with self.assertRaises(journal.JournalError) as caught:
                learner_artifacts.apply("save", body, **case.args)
        self.assertEqual(caught.exception.code, "artifact.target_changed")
        self.assertIsNone(notes.read_note_document(str(case.note_root), "fictional-course"))

    def test_question_changed_while_loading_refuses_mixed_target_revision(self):
        case = self.case
        original = model.load

        def change_during_load(bank_path):
            case.bank.write_text(case.bank.read_text().replace(
                "Explain an unfamiliar boundary rule", "Explain a revised boundary rule"))
            return original(bank_path)

        with patch.object(model, "load", side_effect=change_during_load):
            with self.assertRaises(journal.JournalError) as caught:
                learner_artifacts.view(**case.args)
        self.assertEqual(caught.exception.code, "artifact.target_changed")
        self.assertIsNone(notes.read_note_document(str(case.note_root), "fictional-course"))


class SourceActivities(unittest.TestCase):
    def test_each_source_has_one_activity_group_without_repeated_readings(self):
        with fixture() as (root, base, banks, _info):
            before = snapshot(root)
            handler = SimpleNamespace(root=str(root), path="/course/synthetic/sources")
            state = {"area": "sources", "area_label": "Sources", "course_id": "synthetic"}
            markup = course_workbench.details(handler, state, str(base),
                                               course.read_course(base)["doc"], banks)
            self.assertEqual(markup.count(">Open assigned reading</a>"), 1)
            self.assertEqual(markup.count(">Open linked lesson</a>"), 1)
            self.assertEqual(markup.count(">Open linked practice</a>"), 2)
            self.assertEqual(markup.count("<h4>Learning activities</h4>"), 1)
            self.assertNotIn("No assigned reading or linked activity is available here.", markup)
            self.assertEqual(snapshot(root), before)


class ParserResources(unittest.TestCase):
    def test_lesson_parser_closes_bank_handles_before_returning(self):
        original = builtins.open
        handles = []

        def retain_handle(*args, **kwargs):
            handle = original(*args, **kwargs)
            handles.append(handle)
            return handle

        try:
            with patch.object(builtins, "open", side_effect=retain_handle):
                lesson = model.parse_lesson(str(ROOT / "fixtures/lesson_comparison.md"))
            self.assertTrue(lesson["headings"])
            self.assertTrue(handles)
            self.assertTrue(all(handle.closed for handle in handles),
                            "Parsing leaves file handles open until garbage collection")
        finally:
            for handle in handles:
                handle.close()


class DayEditorScript(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Node is unavailable for JS syntax validation")
    def test_shipped_day_editor_script_parses(self):
        checked = subprocess.run(["node", "--check"], input=day.DAY_JS,
                                 text=True, capture_output=True)
        self.assertEqual(checked.returncode, 0, checked.stderr)


class SearchPresentation(unittest.TestCase):
    def test_each_excerpt_marks_only_its_exact_occurrence_and_escapes_source_text(self):
        case = source_tests.CourseSourceSearch("test_unsaved_course_corpus_exact_duplicate_occurrences_and_no_writes")
        case.setUp()
        self.addCleanup(case.doCleanups)
        case.add_source("🟣 Same phrase. Same phrase. <tag>literal</tag>\n")
        result = course_source_search.search(case.base, "Same phrase.")
        markup = course_source_search.panel(case.base, result)
        self.assertEqual(len(result["hits"]), 2)
        self.assertEqual(markup.count("<mark>Same phrase.</mark>"), 2)
        self.assertIn("&lt;tag&gt;literal&lt;/tag&gt;", markup)
        self.assertNotIn("<tag>", markup)
        self.assertIn('aria-describedby="course-search-position-0 course-search-hit-0 course-search-location-0"', markup)
        self.assertIn('aria-describedby="course-search-position-1 course-search-hit-1 course-search-location-1"', markup)


if __name__ == "__main__":
    unittest.main()
