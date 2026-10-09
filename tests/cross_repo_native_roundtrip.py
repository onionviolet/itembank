#!/usr/bin/env python3
"""Native exploration admission separates equal text, occurrences and revisions."""
from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
import course
import graph
import journal
import model
import workspace
from surfaces import daemon, ia, lesson
from course_guidance_journey_roundtrip import fixture, served, get


class ExplorationAdmission(unittest.TestCase):
    def test_explicit_direct_course_reopens_without_discovering_original_workspace(self):
        with fixture() as (root, base, _banks, _info):
            read = course.read_course(base)
            cid = read['object_id']
            shelf = ia.course_shelf_state(str(base))
            self.assertEqual([row['course_id'] for row in shelf['cards']], [cid])
            self.assertEqual(ia.course_dir_for(str(base), cid), str(base))
            self.assertIsNone(ia.course_dir_for(str(base), 'synthetic'))
            with served(base) as url:
                page = get(url, '/course/' + cid + '/learn')
                self.assertIn('Save and review my original work', page)
                self.assertIn('sources', page)
            competing = Path(workspace.workspace_path(base))
            competing.parent.mkdir(exist_ok=True)
            competing.write_text('{}')
            self.assertIsNone(ia._root_course_record(str(base), course))
            self.assertIsNone(ia.course_dir_for(str(base), cid))

    def test_standalone_equal_text_has_distinct_file_scope_and_changed_revision(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first, second = root / 'first.md', root / 'second.md'
            raw = (ROOT / 'fixtures/lesson_comparison.md').read_text()
            first.write_text(raw)
            second.write_text(raw)
            handler = SimpleNamespace(root=str(root))
            one = daemon._lesson_exploration_context(handler, str(first), model.parse_lesson(first), {})
            two = daemon._lesson_exploration_context(handler, str(second), model.parse_lesson(second), {})
            self.assertNotEqual(one['lesson_id'], two['lesson_id'])
            self.assertNotEqual(one['occurrence_id'], two['occurrence_id'])
            self.assertEqual(one['revision_id'], two['revision_id'])
            first.write_text(raw.replace('time is held equal', 'the time interval stays fixed'))
            changed = daemon._lesson_exploration_context(handler, str(first), model.parse_lesson(first), {})
            self.assertEqual(one['lesson_id'], changed['lesson_id'])
            self.assertNotEqual(one['revision_id'], changed['revision_id'])
            self.assertIsNone(daemon._lesson_exploration_context(
                handler, str(first), model.parse_lesson(first), {'course': ['unadmitted']}))

    def test_course_occurrence_is_exact_and_ambiguous_use_has_no_restore(self):
        with fixture() as (root, base, _banks, info):
            path = str(base / 'symbols.md')
            handler = SimpleNamespace(root=str(root))
            parsed = model.parse_lesson(path)
            read = course.read_course(base)
            for index, row in enumerate(read['doc']['bindings']):
                if row.get('treatment_kind') == 'guided-lesson':
                    graph.enroll_binding(read['doc'], index, info['source_fingerprint'])
            course.write_course(base, read['doc'], read['fingerprint'], 'human', 'test')
            one = daemon._lesson_exploration_context(handler, path, parsed, {'course': ['synthetic']})
            self.assertIsNotNone(one)
            read = course.read_course(base)
            first_binding = next(row for row in read['doc']['bindings']
                                 if row.get('treatment_kind') == 'guided-lesson')
            added = graph.add_objective(read['doc'], 'Another original use of the same lesson.')
            course.write_course(base, read['doc'], read['fingerprint'], 'human', 'test')
            course.bind_treatment(base, added['id'], info['source_id'], 'guided-lesson',
                                  'symbols.md', 'covered', 'high', 'human', 'test')
            read = course.read_course(base)
            graph.enroll_binding(read['doc'], len(read['doc']['bindings']) - 1, info['source_fingerprint'])
            course.write_course(base, read['doc'], read['fingerprint'], 'human', 'test')
            self.assertIsNone(daemon._lesson_exploration_context(handler, path, parsed, {}))
            exact = daemon._lesson_exploration_context(
                handler, path, parsed, {'course': ['synthetic'],
                                       'occurrence': [first_binding['binding_id']]})
            self.assertEqual(one, exact)
            self.assertIsNone(daemon._lesson_exploration_context(
                handler, path, parsed, {'occurrence': ['foreign-binding']}))
            self.assertIsNone(daemon._lesson_exploration_context(
                handler, path, parsed, {'course': ['synthetic', 'synthetic']}))
            registered = journal.read_registry(base)
            bank_id = next(oid for oid, row in registered.items() if row.get('path') == 'symbols.md')
            Path(path).write_text(Path(path).read_text() + '\nExternal unaccepted edit.\n')
            self.assertNotEqual('clean', journal.object_state(base, bank_id))
            self.assertIsNone(daemon._lesson_exploration_context(
                handler, path, model.parse_lesson(path), {'occurrence': [first_binding['binding_id']]}))

    def test_static_render_has_no_exploration_restore_hook(self):
        path = ROOT / 'fixtures/lesson_comparison.md'
        context = {'lesson_id': 'admitted-example', 'revision_id': 'revision-example',
                   'occurrence_id': 'occurrence-example'}
        static = lesson.lesson_page(str(path), model.load(path), model.parse_lesson(path),
                                    exploration_context=context)
        served = lesson.lesson_page(str(path), model.load(path), model.parse_lesson(path),
                                    runtime=True, exploration_context=context)
        self.assertNotIn('data-exploration-lesson=', static)
        self.assertIn('data-exploration-occurrence="occurrence-example"', served)


if __name__ == '__main__':
    unittest.main()
