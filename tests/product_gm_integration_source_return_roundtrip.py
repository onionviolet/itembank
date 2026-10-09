#!/usr/bin/env python3
"""Admitted source identity preserves native task origins and sitting authority."""
import copy
import html
from html.parser import HTMLParser
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest import mock
import urllib.parse

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
import course
import evidence
import journal
import runtime
from surfaces import daemon
from a5_served_integration_roundtrip import request
from course_guidance_journey_roundtrip import fixture, get, served, snapshot, start_saved
from quiz_symbol_return_roundtrip import Page, BANK
import reading_desk_roundtrip as reading_case


class Links(HTMLParser):
    def __init__(self, markup):
        super().__init__()
        self.links = []
        self.current = None
        self.feed(markup)

    def handle_starttag(self, tag, attributes):
        if tag == 'a':
            self.current = dict(attributes, text='')
            self.links.append(self.current)

    def handle_endtag(self, tag):
        if tag == 'a':
            self.current = None

    def handle_data(self, text):
        if self.current is not None:
            self.current['text'] += text


def canonical_return(base, source_index=0):
    cid = course.read_course(base)['doc']['header']['course_object_id']
    return '/course/%s/sources?source=%d#source-%d' % (cid, source_index, source_index)


def route(path, source, **query):
    return path + '?' + urllib.parse.urlencode(dict(query, return_source=source))


def sitting_authority(path):
    data = runtime.read_session(str(path))
    return {key: copy.deepcopy(data.get(key)) for key in
            ('session_id', 'bank', 'mode', 'items', 'cursor', 'responses',
             'status', 'teaching_state', 'subject_profile', 'timing')}


class SourceReturn(unittest.TestCase):
    def assert_return(self, markup, target, label=True):
        matches = [link for link in Links(markup).links if link.get('href') == target]
        self.assertTrue(matches, 'current admitted source return was absent')
        if label:
            self.assertTrue(any('Back to source review' in link['text'] for link in matches))

    def test_practice_only_overview_deduplication_does_not_claim_an_empty_course(self):
        case = reading_case.ReadingDesk('test_live_http_route_and_note')
        case.setUp()
        try:
            root, base = Path(case.root), Path(case.base)
            with served(root) as url:
                before = snapshot(root)
                empty = get(url, '/course/synthetic')
                self.assertIn('No learning activity is bound to this course yet.', empty)
                self.assertEqual(snapshot(root), before)
            bank = base / 'symbols.md'
            bank.write_text(BANK.replace('logic:notation', case.objective), encoding='utf-8')
            linked = journal.op_link(base, 'bank', 'symbols.md', 'human', 'test',
                                     rights={'read': 'granted', 'transform': 'granted'})
            journal.op_adopt(base, linked['object_id'], linked['fingerprint'], 'human', 'test')
            course.bind_treatment(base, case.objective, case.source_id, 'practice',
                                  'symbols.md', 'covered', 'high', 'human', 'test')
            saved, created = start_saved(root, base)
            before = snapshot(root)
            with served(root) as url:
                page = get(url, '/course/synthetic')
                self.assertIn('data-course-resume', page)
                self.assertIn(created['session_id'], page)
                self.assertNotIn('No learning activity is bound to this course yet.', page)
                self.assertNotIn('<section class="overview-path"', page)
            self.assertEqual(snapshot(root), before)
        finally:
            case.doCleanups()

    def test_helper_uses_current_course_identity_order_and_single_nonempty_value(self):
        with fixture() as (root, base, banks, info):
            before = snapshot(root)
            handler = SimpleNamespace(root=str(root), path=route('/course/synthetic/map', info['source_id']))
            actual = daemon._course_source_return(handler, 'synthetic')
            self.assertEqual(actual['href'], canonical_return(base))
            self.assertEqual(actual['label'], 'Back to source review')
            self.assertEqual(actual['source_id'], info['source_id'])
            self.assertEqual(actual['course_id'], course.read_course(base)['object_id'])
            for query in ('return_source=', 'return_source=unknown',
                          'return_source=https%3A%2F%2Fexample.test',
                          'return_source=' + 'x' * 129,
                          'return_source=' + info['source_id'] + '&return_source=',
                          'return_source=' + info['source_id'] + '&return_source=' + info['source_id']):
                handler.path = '/course/synthetic/map?' + query
                self.assertIsNone(daemon._course_source_return(handler, 'synthetic'), query)
            self.assertEqual(snapshot(root), before)

    def test_duplicate_removed_cross_course_and_unclean_source_membership_fall_back(self):
        with fixture() as (root, base, banks, info), fixture() as other:
            other_source = other[3]['source_id']
            handler = SimpleNamespace(root=str(root), path=route('/course/synthetic/map', other_source))
            self.assertIsNone(daemon._course_source_return(handler, 'synthetic'))
            self.assertIsNone(daemon._course_source_return(handler, 'unadmitted-course'))
            read = course.read_course(base)
            handler.path = route('/course/synthetic/map', info['source_id'])
            for change in ('duplicate', 'removed', 'unclean'):
                altered = copy.deepcopy(read)
                if change == 'duplicate':
                    altered['doc']['sources'].append(copy.deepcopy(altered['doc']['sources'][0]))
                elif change == 'removed':
                    altered['doc']['sources'] = []
                else:
                    altered['state'] = 'diverged'
                with mock.patch.object(course, 'read_course', return_value=altered):
                    self.assertIsNone(daemon._course_source_return(handler, 'synthetic'), change)
            ordered = copy.deepcopy(read)
            ordered['doc']['sources'].insert(0, {'source_object_id': 'other-admitted-source'})
            with mock.patch.object(course, 'read_course', return_value=ordered):
                self.assertEqual(daemon._course_source_return(handler, 'synthetic')['href'],
                                 canonical_return(base, 1))

    def test_native_map_lesson_reload_restart_withhold_changed_source_and_do_not_start(self):
        with fixture() as (root, base, banks, info):
            source = journal.read_registry(base)[info['source_id']]
            Path(base, source['path']).write_text('PRIVATE CHANGED SOURCE BYTES', encoding='utf-8')
            before = snapshot(root)
            target = canonical_return(base)
            for restart in range(2):
                with served(root) as url:
                    for _reload in range(2):
                        map_page = get(url, route('/course/synthetic/map', info['source_id']))
                        self.assert_return(map_page, target)
                        page = get(url, route('/lesson/symbols', info['source_id']))
                        self.assert_return(page, target)
                        switch = next(link['href'] for link in Links(page).links
                                      if link['text'] == 'Read step by step')
                        self.assertEqual(urllib.parse.parse_qs(urllib.parse.urlsplit(switch).query)
                                         ['return_source'], [info['source_id']])
                        guided = get(url, switch)
                        self.assert_return(guided, target)
                        continuous = next(link['href'] for link in Links(guided).links
                                          if link['text'] == 'Read continuously')
                        self.assert_return(get(url, continuous), target)
                        for markup in (map_page, page, guided):
                            self.assertNotIn('PRIVATE CHANGED SOURCE BYTES', markup)
                            self.assertNotIn('CORRECT:', markup)
                    self.assertEqual(snapshot(root), before)
            self.assertFalse((root / '_attempts').exists(), 'read-only inspection started a sitting')

    def test_native_malformed_unknown_and_cross_course_keep_existing_origins(self):
        with fixture() as (root, base, banks, info), fixture() as other:
            before = snapshot(root)
            with served(root) as url:
                for query in ('return_source=', 'return_source=unknown',
                              'return_source=' + other[3]['source_id'],
                              'return_source=' + info['source_id'] + '&return_source=',
                              'return_source=' + info['source_id'] + '&return_source=' + info['source_id'],
                              'return_source=https%3A%2F%2Fexample.test'):
                    for path in ('/course/synthetic/map', '/lesson/symbols'):
                        page = get(url, path + '?' + query)
                        self.assertNotIn('Back to source review', page)
                        if path.startswith('/lesson/'):
                            self.assertIn('Back to course', page)
                            switches = [link for link in Links(page).links if link['text'] == 'Read step by step']
                            self.assertTrue(switches)
                            self.assertNotIn('return_source', switches[0]['href'])
            self.assertEqual(snapshot(root), before)

    def test_native_reading_source_return_reload_restart_preserves_read_only_authority(self):
        with fixture() as (root, base, banks, info):
            source = journal.read_registry(base)[info['source_id']]
            Path(base, source['path']).write_text('PRIVATE CHANGED SOURCE BYTES', encoding='utf-8')
            before = snapshot(root)
            target = canonical_return(base)
            for restart in range(2):
                with served(root) as url:
                    for _reload in range(2):
                        page = get(url, route(info['reading'], info['source_id']))
                        self.assert_return(page, target)
                        self.assertNotIn('PRIVATE CHANGED SOURCE BYTES', page)
                        assignments = [link for link in Links(page).links
                                       if '/reading/' in link.get('href', '')]
                        for link in assignments:
                            query = urllib.parse.parse_qs(urllib.parse.urlsplit(link['href']).query)
                            self.assertEqual(query.get('return_source'), [info['source_id']])
                    self.assertEqual(snapshot(root), before)

    def test_existing_reading_route_remains_usable_with_unadmitted_source_return(self):
        with fixture() as (root, base, banks, info):
            before = snapshot(root)
            with served(root) as url:
                page = get(url, route(info['reading'], 'unknown'))
                self.assertIn('Back to Learn', page)
                self.assertNotIn('Back to source review', page)
            self.assertEqual(snapshot(root), before)

    def test_native_practice_source_return_reload_restart_preserves_exact_sitting(self):
        with fixture() as (root, base, banks, info):
            saved, created = start_saved(root, base)
            origin = route('/quiz/symbols', info['source_id'], mode='practice',
                           session=created['session_id'], course='synthetic')
            authority = sitting_authority(saved)
            source_target = canonical_return(base)
            before = snapshot(root)
            before.pop(str(saved.relative_to(root)))
            for restart in range(2):
                with served(root) as url:
                    for _reload in range(2):
                        markup = get(url, origin)
                        self.assert_return(markup, source_target, label=False)
                        current = Page(markup)
                        self.assertEqual(current.card['data-session-id'], created['session_id'])
                        self.assertEqual(urllib.parse.parse_qs(urllib.parse.urlsplit(current.answer_path).query)
                                         ['return_source'], [info['source_id']])
                        self.assertEqual(sitting_authority(saved), authority)
                        self.assertNotIn('CORRECT:', markup)
                after = snapshot(root)
                after.pop(str(saved.relative_to(root)))
                lock_name = str(saved.relative_to(root)) + '.lock'
                if lock_name in after:
                    self.assertEqual(Path(str(saved) + '.lock').read_bytes(), b'')
                    after.pop(lock_name)
                self.assertEqual(after, before, 'practice opening changed non-session durable state')

    def test_native_practice_unadmitted_and_duplicate_origins_retain_course_and_sitting(self):
        with fixture() as (root, base, banks, info), fixture() as other:
            saved, created = start_saved(root, base)
            exact = daemon._quiz_path('symbols', 'practice', session_id=created['session_id'],
                                     course_id='synthetic')
            authority = sitting_authority(saved)
            with served(root) as url:
                for source_query in ('return_source=', 'return_source=unknown',
                                     'return_source=' + other[3]['source_id'],
                                     'return_source=' + info['source_id'] + '&return_source='):
                    page = get(url, exact + '&' + source_query)
                    current = Page(page)
                    self.assertTrue(any(link.get('href') == '/course/synthetic'
                                        for link in current.links))
                    self.assertEqual(current.card['data-session-id'], created['session_id'])
                    self.assertNotIn('return_source', current.answer_path)
                    self.assertNotIn('Back to source review', page)
                    symbol = next(link for link in current.links if 'data-gloss-fetch' in link)
                    symbol_return = urllib.parse.parse_qs(urllib.parse.urlsplit(symbol['href']).query)['return'][0]
                    self.assertNotIn('return_source', symbol_return)
                    self.assertEqual(sitting_authority(saved), authority)

    def test_native_practice_prg_and_symbol_detour_preserve_source_and_submission_authority(self):
        with fixture() as (root, base, banks, info):
            saved, created = start_saved(root, base)
            origin = route('/quiz/symbols', info['source_id'], mode='practice',
                           session=created['session_id'], course='synthetic')
            with served(root) as url:
                markup = get(url, origin)
                page = Page(markup)
                symbol = next(link for link in page.links if 'data-gloss-fetch' in link)
                expected = urllib.parse.parse_qs(urllib.parse.urlsplit(symbol['href']).query)['return'][0]
                self.assertEqual(urllib.parse.parse_qs(urllib.parse.urlsplit(expected).query)
                                 ['return_source'], [info['source_id']])
                old_authority = sitting_authority(saved)
                old_events = list(evidence.live_events(evidence.log_path(base)))
                definition = get(url, symbol['href'])
                back = next(link['href'] for link in Links(definition).links
                            if link['href'] == expected)
                returned = get(url, back)
                self.assert_return(returned, canonical_return(base), label=False)
                self.assertEqual(sitting_authority(saved), old_authority)
                new_events = list(evidence.live_events(evidence.log_path(base)))
                self.assertEqual(new_events[:len(old_events)], old_events)
                self.assertTrue(new_events[len(old_events):])
                self.assertTrue(all(row['event_type'] == 'term_lookup' for row in new_events[len(old_events):]))
                current = Page(returned)
                status, location, feedback = request(urllib.parse.urljoin(url, current.answer_path), {
                    'action': 'submit', 'form_token': current.form_token, 'option': 'B'})
                self.assertEqual(status, 200)
                query = urllib.parse.parse_qs(urllib.parse.urlsplit(location).query)
                self.assertEqual(query['return_source'], [info['source_id']])
                self.assertEqual(query['session'], [created['session_id']])
                self.assert_return(feedback, canonical_return(base), label=False)
                continued = next(link['href'] for link in Links(feedback).links
                                 if 'data-feedback-continue' in link)
                self.assertEqual(urllib.parse.parse_qs(urllib.parse.urlsplit(continued).query)
                                 ['return_source'], [info['source_id']])
                state = runtime.read_session(str(saved))
                self.assertEqual(state['cursor'], 1)
                self.assertEqual(len(state['responses']), 1)
                self.assertTrue(state['responses'][0]['score'])
                get(url, continued)
                self.assertEqual(runtime.read_session(str(saved))['responses'], state['responses'])

    def test_nested_lesson_sitting_return_validates_optional_source_before_preserving(self):
        with fixture() as (root, base, banks, info):
            saved, created = start_saved(root, base)
            exact = daemon._quiz_path('symbols', 'practice', session_id=created['session_id'],
                                     course_id='synthetic', return_source=info['source_id'])
            before = snapshot(root)
            with served(root) as url:
                page = get(url, '/lesson/symbols?' + urllib.parse.urlencode({'return': exact}))
                self.assert_return(page, canonical_return(base))
                self.assertTrue(any(link.get('href') == exact and link['text'] == 'Return to saved sitting'
                                    for link in Links(page).links))
                switched = next(link['href'] for link in Links(page).links if link['text'] == 'Read step by step')
                self.assert_return(get(url, switched), canonical_return(base))
                for optional in ('unknown', '', info['source_id'] + '&return_source=unknown'):
                    malformed = daemon._quiz_path('symbols', 'practice', session_id=created['session_id'],
                                                 course_id='synthetic') + '&return_source=' + optional
                    page = get(url, '/lesson/symbols?' + urllib.parse.urlencode({'return': malformed}))
                    self.assertNotIn('Back to source review', page)
                    exact_link = next(link['href'] for link in Links(page).links
                                      if link['text'] == 'Return to saved sitting')
                    self.assertNotIn('return_source', exact_link)
                wrong = exact.replace(created['session_id'], 'unknown-sitting')
                refused = get(url, '/lesson/symbols?' + urllib.parse.urlencode({'return': wrong}))
                self.assertNotIn('Return to saved sitting', refused)
            self.assertEqual(snapshot(root), before, 'lesson return admission changed canonical state')


if __name__ == '__main__':
    unittest.main()
