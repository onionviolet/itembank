#!/usr/bin/env python3
"""Saved note rediscovery, exact reading return and recovery on synthetic data."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest
import urllib.parse
import urllib.request
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
import course
import journal
import notes
import reading_desk
from surfaces import course_notes
from surfaces import daemon
import reading_desk_roundtrip as desk_tests
from context_help_native_roundtrip import native
from course_source_search_roundtrip import tree


class CourseNotes(unittest.TestCase):
    def setUp(self):
        self.case = desk_tests.ReadingDesk('test_live_http_route_and_note')
        self.case.setUp()
        self.addCleanup(self.case.doCleanups)
        self.row = self.case.create()['occurrence']
        self.base = self.case.base

    def save(self, wording='Remember the Straße rule.\n<script>not executable</script>', note_id='a' * 32):
        private = reading_desk.note_root(self.base)
        document = notes.read_note_document(private, self.case.read()['object_id'])
        return self.case.save(self.row, wording, note_id, document['fingerprint'] if document else None)

    def test_saved_note_search_objective_unicode_escape_and_no_mutations(self):
        self.save()
        before = tree(self.base)
        state = course_notes.collection(self.base, {'notes_query': ['STRASSE']})
        self.assertEqual((state['total'], state['matched']), (1, 1))
        self.assertEqual(state['rows'][0]['note']['note_id'], 'a' * 32)
        self.assertTrue(state['rows'][0]['links'])
        self.assertIn(self.row['revision_id'], state['rows'][0]['links'][0]['href'])
        self.assertEqual(course_notes.collection(self.base, {'notes_query': ['Compare the synthetic']})['matched'], 1)
        markup = course_notes.panel(self.base, {'notes_query': ['STRASSE']})
        self.assertIn('&lt;script&gt;not executable&lt;/script&gt;', markup)
        self.assertNotIn('<script>', markup)
        self.assertIn('line 2', markup)
        self.assertEqual(tree(self.base), before)

    def test_empty_no_matches_invalid_query_and_result_page_recovery(self):
        before = tree(self.base)
        self.assertIn('No saved notes yet', course_notes.panel(self.base))
        self.assertEqual(tree(self.base), before)
        self.save()
        self.assertIn('No notes match this query', course_notes.panel(self.base, {'notes_query': ['nonexistent']}))
        for fields in ({'notes_query': ['one', 'two']}, {'notes_query': ['x' * 161]},
                       {'notes_query': ['\n']}, {'notes_offset': ['-1']}, {'notes_offset': ['invalid']}):
            self.assertIn('Show all my notes', course_notes.panel(self.base, fields))
        self.assertIn('First note results', course_notes.panel(self.base, {'notes_offset': ['20']}))
        self.assertIsNone(course_notes.reading_return('synthetic', {'notes_return': ['yes', 'yes']}))
        result = course_notes.reading_return('synthetic', {'notes_return': ['yes'], 'notes_query': ['https://foreign.invalid/?x=1&y=2']})
        self.assertTrue(result['href'].startswith('/course/synthetic/learn?'))

    def test_pagination_is_stable_and_does_not_count_deleted_notes(self):
        for index in range(22):
            self.save('Memory note %d' % index, '%032x' % index)
        first = course_notes.collection(self.base)
        second = course_notes.collection(self.base, {'notes_offset': ['20']})
        self.assertEqual((first['total'], len(first['rows']), len(second['rows'])), (22, 20, 2))
        second_href = second['rows'][0]['links'][0]['href']
        self.assertIn('notes_offset=20', second_href)
        return_action = course_notes.reading_return('synthetic', urllib.parse.parse_qs(urllib.parse.urlsplit(second_href).query, keep_blank_values=True))
        self.assertIn('notes_offset=20#course-notes', return_action['href'])
        self.assertFalse({r['note']['note_id'] for r in first['rows']} & {r['note']['note_id'] for r in second['rows']})
        private = reading_desk.note_root(self.base)
        document = notes.read_note_document(private, self.case.read()['object_id'])
        sidecar = copy.deepcopy(document['sidecar'])
        sidecar = notes.delete_note(sidecar, sidecar['notes'][0]['note_id'])['sidecar']
        notes.write_note_document(private, self.case.read()['object_id'], document['markdown'], sidecar, document['fingerprint'])
        self.assertEqual(course_notes.collection(self.base)['total'], 21)

    def test_broken_source_and_removed_assignment_preserve_notes(self):
        self.save()
        source = Path(self.base, journal.read_registry(self.base)[self.case.source_id]['path'])
        source.write_text('Changed source bytes', encoding='utf-8')
        before = tree(self.base)
        state = course_notes.collection(self.base)
        self.assertEqual(state['rows'][0]['links'], [])
        self.assertIn('Straße rule', state['rows'][0]['note']['learner_wording'])
        self.assertIn('Reading link unavailable', course_notes.panel(self.base))
        self.assertEqual(tree(self.base), before)
        read = self.case.read()
        read['doc']['reading_occurrences'] = []
        read['doc']['reading_placement'] = []
        course.write_course(self.base, read['doc'], read['fingerprint'], 'human', 'test')
        self.assertEqual(course_notes.collection(self.base)['total'], 1)
        self.assertEqual(course_notes.collection(self.base)['rows'][0]['links'], [])

    def test_note_pair_conflict_has_recovery_and_no_partial_disclosure(self):
        self.save()
        Path(reading_desk.note_root(self.base), 'notes.md').write_text('Outside edit')
        before = tree(self.base)
        markup = course_notes.panel(self.base)
        self.assertIn('Notes need recovery', markup)
        self.assertNotIn('Straße rule', markup)
        self.assertEqual(tree(self.base), before)

    def test_lan_course_preview_never_reads_private_notes(self):
        self.save()
        handler = type('Remote', (), {'client_address': ('192.0.2.10', 12345), 'path': '/course/synthetic/learn'})()
        with patch.object(course_notes, 'collection') as read_notes:
            markup = daemon._course_area_extra(handler, {'area': 'learn', 'course_id': 'synthetic'}, self.base)
        read_notes.assert_not_called()
        self.assertIn('available on this computer', markup)
        self.assertNotIn('Straße', markup)

    def test_native_return_and_fresh_process_reopen(self):
        self.save()
        before = tree(self.base)
        with native(self.case.root) as url:
            route = 'course/synthetic/learn?notes_query=STRASSE'
            with urllib.request.urlopen(url + route) as response:
                markup = response.read().decode()
            self.assertIn('My course notes', markup)
            self.assertIn('Straße rule', markup)
            href = course_notes.collection(self.base, {'notes_query': ['STRASSE']})['rows'][0]['links'][0]['href']
            with urllib.request.urlopen(url.rstrip('/') + href) as response:
                reading = response.read().decode()
            self.assertIn('Back to my course notes', reading)
            self.assertIn('/learn?notes_query=STRASSE&amp;notes_offset=0#course-notes', reading)
            self.assertIn('First synthetic paragraph', reading)
        program = 'import json,sys; from surfaces.course_notes import collection; print(json.dumps(collection(sys.argv[1])))'
        child = subprocess.run([sys.executable, '-c', program, self.base], cwd=ROOT, capture_output=True, text=True, timeout=20)
        self.assertEqual(child.returncode, 0, child.stderr)
        self.assertEqual(json.loads(child.stdout)['rows'][0]['note']['note_id'], 'a' * 32)
        self.assertEqual(tree(self.base), before)


def browser_check(destination):
    from playwright.sync_api import sync_playwright
    destination.mkdir(parents=True, exist_ok=True)
    case = CourseNotes('test_native_return_and_fresh_process_reopen')
    case.setUp()
    results = []
    try:
        with native(case.case.root) as url, sync_playwright() as pw:
            browser = pw.chromium.launch(channel='chrome', headless=True)
            try:
                # Actually save through the normal reading UI before retrieval.
                context = browser.new_context()
                page = context.new_page()
                row = case.row
                page.goto(url + 'course/synthetic/reading/%s/%s' % (row['occurrence_id'], row['revision_id']))
                page.get_by_label('A note to yourself', exact=True).fill('Remember the Straße rule.\nThis note survives reopening.')
                page.get_by_role('button', name='Save to my notes', exact=True).click()
                page.get_by_text('Saved to your notes.', exact=True).wait_for()
                context.close()
                before = tree(case.base)
                for width in (1280, 390, 320):
                    for scripts in (True, False):
                        context = browser.new_context(viewport={'width': width, 'height': 900}, java_script_enabled=scripts,
                            color_scheme='dark' if width == 390 else 'light', reduced_motion='reduce')
                        page = context.new_page()
                        errors = []
                        page.on('pageerror', lambda error: errors.append(str(error)))
                        page.goto(url + 'course/synthetic/learn')
                        panel = page.locator('.course-notes')
                        panel.get_by_label('Search my notes', exact=True).fill('STRASSE')
                        panel.get_by_role('button', name='Search notes', exact=True).focus()
                        with page.expect_navigation():
                            page.keyboard.press('Enter')
                        self_note = page.locator('.course-note-wording')
                        assert self_note.inner_text().startswith('Remember the Straße rule.')
                        page.reload()
                        page.locator('.course-notes a').filter(has_text='Open reading:').first.focus()
                        with page.expect_navigation():
                            page.keyboard.press('Enter')
                        assert 'First synthetic paragraph' in page.locator('#source-content').inner_text()
                        page.get_by_role('link', name='Back to my course notes').focus()
                        with page.expect_navigation():
                            page.keyboard.press('Enter')
                        assert page.get_by_label('Search my notes', exact=True).input_value() == 'STRASSE'
                        assert page.url.endswith('#course-notes')
                        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), width
                        assert not errors, errors
                        page.locator('.course-notes').screenshot(path=str(destination / ('notes-%s-%s.png' % (width, scripts))))
                        results.append({'width': width, 'scripts': scripts, 'keyboard_search_return_reload': 'passed'})
                        context.close()
                assert tree(case.base) == before, 'Retrieval changed durable learner files'
            finally:
                browser.close()
        (destination / 'browser.json').write_text(json.dumps(results, indent=2) + '\n')
        print('Course notes: actual UI save and six Chrome search/reload/reading-return journeys passed')
    finally:
        case.doCleanups()


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--browser':
        browser_check(Path(sys.argv[2]))
    else:
        unittest.main()
