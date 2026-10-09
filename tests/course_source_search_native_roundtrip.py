#!/usr/bin/env python3
"""Actual served course-source search, exact occurrence return and offline refusal."""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
import course
import journal
import notes
import reading_desk
import source_adapters
from surfaces import research_context
from a5_research_context_roundtrip import fixture, fields
from context_help_native_roundtrip import native
from course_source_search_roundtrip import tree
from daemon_roundtrip import start_daemon


def post(address, body):
    request = urllib.request.Request(address, data=urllib.parse.urlencode(body, doseq=True).encode())
    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            return response.status, response.read().decode()
    except urllib.error.HTTPError as error:
        with error:
            return error.code, error.read().decode()


@contextmanager
def selected_fixture():
    with tempfile.TemporaryDirectory(prefix='native-course-search-') as directory:
        root = Path(directory)
        base, refs = fixture(root)
        copied = research_context.apply(base, fields(refs[0], 'copy', confirm='yes'))
        research_context.apply(base, {'operation': ['save_scope'], 'reference': [json.dumps(refs[0])],
            'note_id': [copied['note']['note_id']], 'confirm': ['yes'],
            'expected_notes_fingerprint': [copied['document']['fingerprint']]})
        private = reading_desk.note_root(base)
        document = notes.read_note_document(private, course.read_course(base)['object_id'])
        sidecar = json.loads(json.dumps(document['sidecar']))
        sidecar['notes'][0]['learner_wording'] = 'PRIVATE_ONLY'
        notes.write_note_document(private, sidecar['course_id'], document['markdown'] + '\nPRIVATE_ONLY\n',
                                  sidecar, document['fingerprint'])
        yield root, base, refs


class NativeCourseSearch(unittest.TestCase):
    def test_real_search_match_preview_return_and_no_durable_changes(self):
        with selected_fixture() as (root, base, refs), native(root) as url:
            address = url + 'course/synthetic/research'
            before = tree(base)
            status, page = post(address, {'operation': 'search_course_sources', 'query': 'Same sentence.'})
            self.assertEqual(status, 200, page)
            self.assertIn('2 hits. Searched 2 of 3 registered sources', page)
            self.assertEqual(page.count('Open exact course search match'), 2)
            self.assertNotIn('PRIVATE_ONLY', page)
            status, page = post(address + '#research-exact-passage', dict(fields(refs[0], 'preview'),
                return_query=['Same sentence.'], match_start=['0'], match_end=['14']))
            self.assertEqual(status, 200, page)
            self.assertIn('locator L4', page)
            self.assertIn('<mark>Same sentence.</mark>', page)
            self.assertIn('Return to this course source search', page)
            status, page = post(address, {'operation': 'search_course_sources', 'query': 'EXCLUDED SENTINEL'})
            self.assertEqual(status, 200, page)
            self.assertIn('1 hits.', page)
            self.assertNotIn('PRIVATE_ONLY', page)
            self.assertEqual(tree(base), before)

    def test_invalid_query_and_forged_range_refuse_with_input_retained(self):
        with selected_fixture() as (root, base, refs), native(root) as url:
            address = url + 'course/synthetic/research'
            before = tree(base)
            status, page = post(address, dict(fields(refs[0], 'preview'),
                return_query=['Same sentence.'], match_start=['2'], match_end=['14']))
            self.assertEqual(status, 400, page)
            self.assertIn('This match changed', page)
            self.assertIn('value="Same sentence."', page)
            status, page = post(address, {'operation': 'search_course_sources', 'query': 'x' * 161})
            self.assertEqual(status, 400, page)
            self.assertIn('1 to 160 characters', page)
            self.assertIn('x' * 161, page)
            self.assertEqual(tree(base), before)

    def test_stale_sidecar_and_changed_rights_keep_search_recovery(self):
        with selected_fixture() as (root, base, refs), native(root) as url:
            address = url + 'course/synthetic/research'
            record = journal.read_registry(base)[refs[0]['source_id']]
            path = Path(base, source_adapters.sidecar_path_for(record['path']))
            original = path.read_bytes()
            sidecar = json.loads(original)
            sidecar['locators'][0]['body']['line'] = 999
            path.write_text(json.dumps(sidecar))
            before = tree(base)
            status, page = post(address, {'operation': 'search_course_sources', 'query': 'Same sentence.'})
            self.assertEqual(status, 200, page)
            self.assertIn('0 hits.', page)
            self.assertIn('value="Same sentence."', page)
            self.assertEqual(tree(base), before)
            path.write_bytes(original)
            journal.op_grant_rights(base, refs[0]['source_id'], {'quote': 'denied'}, refs[0]['fingerprint'], 'human', 'test')
            status, page = post(address, dict(fields(refs[0], 'preview'),
                return_query=['Same sentence.'], match_start=['0'], match_end=['14']))
            self.assertEqual(status, 400, page)
            self.assertNotIn('<mark>Same sentence.</mark>', page)
            self.assertIn('quote rights', page)
            self.assertIn('value="Same sentence."', page)

    def test_fresh_daemon_process_searches_without_an_index_or_saved_context(self):
        with tempfile.TemporaryDirectory(prefix='fresh-course-search-') as directory:
            root = Path(directory)
            base, _refs = fixture(root)
            before = tree(base)
            process, url, _lines = start_daemon(str(root))
            try:
                address = url + 'course/' + course.read_course(base)['object_id'] + '/research'
                status, page = post(address, {'operation': 'search_course_sources', 'query': 'Same sentence.'})
                self.assertEqual(status, 200, page)
                self.assertIn('2 hits.', page)
                self.assertEqual(tree(base), before)
            finally:
                process.terminate()
                process.wait(timeout=8)
                if process.stdout:
                    process.stdout.close()


def browser_checks(output):
    from playwright.sync_api import sync_playwright
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    observations = []
    with selected_fixture() as (root, base, _refs), native(root) as url, sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel=os.environ.get('ITEMBANK_VISUAL_QA_CHANNEL', 'chrome'))
        try:
            before = tree(base)
            for width in (1280, 390, 320):
                for scripts in (True, False):
                    context = browser.new_context(viewport={'width': width, 'height': 900},
                        java_script_enabled=scripts, reduced_motion='reduce')
                    page = context.new_page()
                    page.goto(url + 'course/synthetic/research')
                    page.get_by_label('Course source query', exact=True).fill('Same sentence.')
                    assert page.get_by_label('Course source query', exact=True).bounding_box()['height'] >= 44
                    assert page.get_by_role('button', name='Search course sources', exact=True).bounding_box()['height'] >= 44
                    page.get_by_role('button', name='Search course sources', exact=True).focus()
                    page.keyboard.press('Enter')
                    page.wait_for_url('**#course-source-search')
                    assert '2 hits.' in page.get_by_role('status').all_inner_texts()[-1]
                    assert page.get_by_role('button', name='Open exact course search match', exact=True).nth(1).bounding_box()['height'] >= 44
                    page.get_by_role('button', name='Open exact course search match', exact=True).nth(1).focus()
                    page.keyboard.press('Enter')
                    page.wait_for_url('**#research-exact-passage')
                    assert page.locator('#research-exact-passage + pre mark').inner_text() == 'Same sentence.'
                    assert 'locator L4' in page.locator('#research-exact-passage').locator('xpath=following-sibling::p[1]').inner_text()
                    page.get_by_role('button', name='Return to this course source search', exact=True).focus()
                    page.keyboard.press('Enter')
                    page.wait_for_url('**#course-source-search')
                    assert page.get_by_label('Course source query', exact=True).input_value() == 'Same sentence.'
                    assert page.get_by_role('button', name='Open exact course search match', exact=True).count() == 2
                    if scripts:
                        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
                    screenshot = output / ('search-%s-%s.png' % (width, 'scripts' if scripts else 'plain'))
                    page.screenshot(path=str(screenshot), full_page=True)
                    observations.append({'width': width, 'scripts': scripts, 'exact_L4': True,
                        'query_return': True, 'keyboard': True, 'no_durable_change': tree(base) == before})
                    context.close()
            assert tree(base) == before
        finally:
            browser.close()
    (output / 'observations.json').write_text(json.dumps(observations, indent=2) + '\n')
    print('Six Chrome course-search/preview/return journeys pass.')


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--browser-shots':
        browser_checks(sys.argv[2])
    else:
        unittest.main()
