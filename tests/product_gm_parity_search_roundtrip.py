#!/usr/bin/env python3
"""Paged course retrieval keeps original ranges, admission and native return."""
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
import course
import graph
import identity
import journal
import source_adapters
from surfaces import course_source_search as search, research_context
from a5_research_context_roundtrip import fixture
from context_help_native_roundtrip import native
from course_source_search_native_roundtrip import post
from course_source_search_roundtrip import tree
from daemon_roundtrip import start_daemon


class Forms(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.forms, self.current = [], None
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'form':
            self.current = {'fields': {}, 'button': ''}
        elif tag == 'input' and self.current is not None and attrs.get('type') == 'hidden':
            self.current['fields'][attrs['name']] = attrs.get('value', '')

    def handle_data(self, data):
        if self.current is not None:
            self.current['button'] += data

    def handle_endtag(self, tag):
        if tag == 'form' and self.current is not None:
            self.forms.append(self.current)
            self.current = None

    def fields(self, button):
        return next(form['fields'] for form in self.forms if form['button'].strip() == button)


class PagedCourseSearch(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='product-gm-parity-search-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.base, self.refs = fixture(self.root)
        self.text = '🟣 ' + ' '.join(['Straße'] * 70) + '\n'
        Path(self.base, 'many.md').write_text(self.text, encoding='utf-8')
        linked = journal.op_link(self.base, 'source', 'many.md', 'human', 'test',
                                rights={right: 'granted' for right in identity.RIGHTS_OPERATIONS})
        imported = source_adapters.import_source(self.base, 'markdown', linked['object_id'], 'human', 'test')
        self.sid = imported['source_id']
        read = course.read_course(self.base)
        graph.add_source(read['doc'], self.sid, 'Fictional street examples')
        course.write_course(self.base, read['doc'], read['fingerprint'], 'human', 'test')

    def test_three_pages_original_unicode_ranges_and_no_mutations(self):
        before = tree(self.base)
        seen = []
        for offset, count, following in ((0, 32, 32), (32, 32, 64), (64, 6, None)):
            result = search.search(self.base, 'STRASSE', match_case=False, offset=offset)
            self.assertEqual(len(result['hits']), count)
            self.assertEqual(result['next_offset'], following)
            for hit in result['hits']:
                self.assertEqual(hit['source_id'], self.sid)
                self.assertEqual(self.text[hit['start']:hit['end']], 'Straße')
                self.assertIn('<mark>Straße</mark>', search.excerpt_text(hit, 'STRASSE'))
                seen.append((hit['source_id'], hit['locator_id'], hit['start'], hit['end']))
        self.assertEqual(len(set(seen)), 70)
        self.assertEqual(search.search(self.base, 'STRASSE')['hits'], [])
        street_hits = [hit for hit in search.search(self.base, 's', match_case=False)['hits']
                       if hit['source_id'] == self.sid]
        self.assertEqual(street_hits[0]['end'], 3)
        self.assertTrue(all(self.text[hit['start']:hit['end']].casefold() == 's'
                            for hit in street_hits), 'A folded match must not select half of ß.')
        self.assertEqual(tree(self.base), before)

    def test_next_page_rights_and_revision_rechecked_without_snippets(self):
        first = search.search(self.base, 'STRASSE', match_case=False)
        self.assertEqual(first['next_offset'], 32)
        record = journal.read_registry(self.base)[self.sid]
        journal.op_grant_rights(self.base, self.sid, {'quote': 'denied'}, record['fingerprint'], 'human', 'test')
        before = tree(self.base)
        second = search.search(self.base, 'STRASSE', match_case=False, offset=32)
        self.assertEqual(second['hits'], [])
        self.assertTrue(any(row['state'] == 'rights_unavailable' for row in second['omitted_sources']))
        self.assertEqual(tree(self.base), before)
        journal.op_grant_rights(self.base, self.sid, record['rights'], record['fingerprint'], 'human', 'test')
        Path(self.base, record['path']).write_text('CHANGED SOURCE ONLY', encoding='utf-8')
        second = search.search(self.base, 'STRASSE', match_case=False, offset=32)
        self.assertEqual(second['hits'], [])
        self.assertTrue(any(row['state'] == 'stale' for row in second['omitted_sources']))

    def test_modes_pages_and_tampered_preview_fail_closed(self):
        for kwargs in ({'offset': -1}, {'offset': 4097}, {'offset': True},
                       {'match_case': 'yes'}, {'offset': 1.5}):
            with self.assertRaises(ValueError):
                search.search(self.base, 'street', **kwargs)
        for body in ({'ignore_case': ['true']}, {'offset': ['x']}, {'offset': ['4097']}):
            with self.assertRaises(ValueError):
                research_context.apply(self.base, dict(operation=['search_course_sources'], query=['street'], **body))
        result = search.search(self.base, 'STRASSE', match_case=False, offset=32)
        hit = result['hits'][0]
        fields = {'operation': ['preview'], 'source': [json.dumps({key: hit[key] for key in ('source_id', 'fingerprint')})],
                  'locator': [hit['locator_id']], 'return_query': ['STRASSE'],
                  'return_ignore_case': ['yes'], 'return_offset': ['32'],
                  'match_start': [str(hit['start'])], 'match_end': [str(hit['end'])]}
        preview = research_context.apply(self.base, fields)
        self.assertEqual(preview['offset'], 32)
        self.assertFalse(preview['match_case'])
        self.assertIn('<mark>Straße</mark>', search.preview_text(preview))
        for change in ({'return_ignore_case': ['']}, {'return_offset': ['4097']},
                       {'match_start': [str(hit['start'] + 1)]}):
            with self.assertRaises(ValueError):
                research_context.apply(self.base, dict(fields, **change))

    def test_omitted_source_does_not_consume_page_slots(self):
        original = research_context._safe_source
        changed = False
        def refuse_after_scan(base, ref):
            nonlocal changed
            result = original(base, ref)
            if ref['source_id'] == self.refs[0]['source_id'] and not changed:
                changed = True
                path = Path(base, journal.read_registry(base)[ref['source_id']]['path'])
                path.write_text('CHANGED DURING SEARCH', encoding='utf-8')
            return result
        with patch.object(research_context, '_safe_source', side_effect=refuse_after_scan):
            result = search.search(self.base, 'STRASSE', match_case=False, offset=32)
        self.assertEqual(len(result['hits']), 32)
        self.assertEqual({hit['source_id'] for hit in result['hits']}, {self.sid})

    def test_final_admission_slot_loss_requires_explicit_page_retry(self):
        Path(self.base, 'early.md').write_text(' '.join(['Straße'] * 32) + '\n', encoding='utf-8')
        linked = journal.op_link(self.base, 'source', 'early.md', 'human', 'test',
                                rights={right: 'granted' for right in identity.RIGHTS_OPERATIONS})
        imported = source_adapters.import_source(self.base, 'markdown', linked['object_id'], 'human', 'test')
        sid = imported['source_id']
        read = course.read_course(self.base)
        graph.add_source(read['doc'], sid, 'Fictional early matches')
        early = read['doc']['sources'].pop()
        index = next(i for i, row in enumerate(read['doc']['sources']) if row['source_object_id'] == self.sid)
        read['doc']['sources'].insert(index, early)
        course.write_course(self.base, read['doc'], read['fingerprint'], 'human', 'test')
        path = Path(self.base, journal.read_registry(self.base)[sid]['path'])
        original = research_context._safe_source
        def change_earlier(base, ref):
            passage = original(base, ref)
            if ref['source_id'] == self.sid:
                path.write_text('CHANGED EARLY SOURCE', encoding='utf-8')
            return passage
        with patch.object(research_context, '_safe_source', side_effect=change_earlier):
            result = search.search(self.base, 'STRASSE', match_case=False)
        self.assertTrue(result['retry_required'])
        self.assertEqual(result['hits'], [])
        self.assertIsNone(result['next_offset'])
        fields = Forms(search.panel(self.base, result)).fields('Retry current course search page')
        repeated = research_context.apply(self.base, {key: [value] for key, value in fields.items()})
        self.assertEqual(len(repeated['hits']), 32)
        self.assertEqual(repeated['next_offset'], 32)
        self.assertEqual({hit['source_id'] for hit in repeated['hits']}, {self.sid})

    def test_rejected_partial_expansion_keeps_later_full_unicode_match(self):
        self.assertEqual(list(research_context._literal_ranges('sß', 'ss', False)), [(1, 2)])
        Path(self.base, 'expanded.md').write_text('sß\n', encoding='utf-8')
        linked = journal.op_link(self.base, 'source', 'expanded.md', 'human', 'test',
                                rights={right: 'granted' for right in identity.RIGHTS_OPERATIONS})
        imported = source_adapters.import_source(self.base, 'markdown', linked['object_id'], 'human', 'test')
        sid = imported['source_id']
        read = course.read_course(self.base)
        graph.add_source(read['doc'], sid, 'Fictional expansion edge')
        course.write_course(self.base, read['doc'], read['fingerprint'], 'human', 'test')
        result = search.search(self.base, 'ss', match_case=False, offset=64)
        hits = [hit for hit in result['hits'] if hit['source_id'] == sid]
        self.assertEqual([(hit['start'], hit['end']) for hit in hits], [(1, 2)])
        with native(self.root) as url:
            status, page = post(url + 'course/synthetic/research',
                                {'operation': 'search_course_sources', 'query': 'ss', 'ignore_case': 'yes', 'offset': '64'})
            self.assertEqual(status, 200, page)
            self.assertIn('s<mark>ß</mark>', page)

    def test_native_page_preview_exact_page_return_and_restart(self):
        before = tree(self.base)
        with native(self.root) as url:
            address = url + 'course/synthetic/research'
            status, first = post(address, {'operation': 'search_course_sources', 'query': 'STRASSE', 'ignore_case': 'yes'})
            self.assertEqual(status, 200, first)
            status, second = post(address, Forms(first).fields('Next course search results'))
            self.assertEqual(status, 200, second)
            self.assertIn('Result offset: 32.', second)
            fields = Forms(second).fields('Open exact course search match')
            status, preview = post(address, fields)
            self.assertEqual(status, 200, preview)
            self.assertIn('<mark>Straße</mark>', preview)
            returning = Forms(preview).fields('Return to this course source search')
            self.assertEqual(returning['offset'], '32')
            self.assertEqual(returning['ignore_case'], 'yes')
        process, url, _lines = start_daemon(str(self.root))
        try:
            cid = course.read_course(self.base)['object_id']
            status, second = post(url + 'course/' + cid + '/research', returning)
            self.assertEqual(status, 200, second)
            self.assertIn('Result offset: 32.', second)
            self.assertIn('name="ignore_case" value="yes" checked', second)
            status, last = post(url + 'course/' + cid + '/research', Forms(second).fields('Next course search results'))
            self.assertEqual(status, 200, last)
            self.assertIn('6 hits.', last)
            self.assertNotIn('Next course search results', last)
        finally:
            process.terminate()
            process.wait(timeout=8)
            if process.stdout:
                process.stdout.close()
        self.assertEqual(tree(self.base), before)

    def test_refused_native_preview_retains_exact_search_page_and_mode(self):
        with native(self.root) as url:
            address = url + 'course/synthetic/research'
            status, page = post(address, {'operation': 'search_course_sources', 'query': 'STRASSE',
                                          'ignore_case': 'yes', 'offset': '32'})
            self.assertEqual(status, 200, page)
            preview_fields = Forms(page).fields('Open exact course search match')
            record = journal.read_registry(self.base)[self.sid]
            journal.op_grant_rights(self.base, self.sid, {'quote': 'denied'}, record['fingerprint'], 'human', 'test')
            before = tree(self.base)
            status, refused = post(address, preview_fields)
            self.assertEqual(status, 400, refused)
            self.assertNotIn('<mark>Straße</mark>', refused)
            returning = Forms(refused).fields('Return to this course source search')
            self.assertEqual(returning['offset'], '32')
            self.assertEqual(returning['ignore_case'], 'yes')
            self.assertEqual(returning['query'], 'STRASSE')
            status, unavailable = post(address, returning)
            self.assertEqual(status, 200, unavailable)
            self.assertIn('Result offset: 32.', unavailable)
            self.assertIn('quote rights', unavailable)
            self.assertEqual(tree(self.base), before)


if __name__ == '__main__':
    unittest.main()
