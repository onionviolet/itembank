#!/usr/bin/env python3
"""Course retrieval admits exact sources without changing private context or evidence."""
import json
import os
from pathlib import Path
import subprocess
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
import notes
import reading_desk
import source_adapters
from surfaces import course_source_search as search, research_context
from a5_research_context_roundtrip import fixture, fields


def tree(base):
    return {str(path.relative_to(base)): path.read_bytes()
            for path in Path(base).rglob('*') if path.is_file()}


class CourseSourceSearch(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='course-source-search-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.base, self.refs = fixture(self.root)

    def add_source(self, text, name='extra.md', registered=True):
        Path(self.base, name).write_text(text, encoding='utf-8')
        linked = journal.op_link(self.base, 'source', name, 'human', 'test',
            rights={right: 'granted' for right in identity.RIGHTS_OPERATIONS})
        imported = source_adapters.import_source(self.base, 'markdown', linked['object_id'], 'human', 'test')
        if registered:
            read = course.read_course(self.base)
            graph.add_source(read['doc'], imported['source_id'], name)
            course.write_course(self.base, read['doc'], read['fingerprint'], 'human', 'test')
        return imported['source_id']

    def test_unsaved_course_corpus_exact_duplicate_occurrences_and_no_writes(self):
        before = tree(self.base)
        result = search.search(self.base, 'Same sentence.')
        self.assertEqual(result['status'], 'course_search')
        self.assertEqual([hit['locator_id'] for hit in result['hits']], ['L2', 'L4'])
        self.assertEqual([hit['origin']['line'] for hit in result['hits']], [2, 4])
        self.assertEqual(result['sources_total'], 3)
        self.assertEqual(result['sources_searched'], 2)
        self.assertEqual(result['omitted_sources'][0]['state'], 'assessment')
        self.assertFalse(result['limited'])
        self.assertEqual(result['egress'], 'none')
        self.assertEqual(tree(self.base), before)
        self.assertFalse(Path(self.base, '_research').exists())

    def test_existing_selection_private_notes_and_unregistered_files_stay_excluded(self):
        copied = research_context.apply(self.base, fields(self.refs[0], 'copy', confirm='yes'))
        selected = {'operation': ['save_scope'], 'reference': [json.dumps(self.refs[0])],
            'note_id': [copied['note']['note_id']],
            'expected_notes_fingerprint': [copied['document']['fingerprint']], 'confirm': ['yes']}
        research_context.apply(self.base, selected)
        self.add_source('UNREGISTERED_ONLY\n', registered=False)
        private = reading_desk.note_root(self.base)
        cid = course.read_course(self.base)['object_id']
        document = notes.read_note_document(private, cid)
        sidecar = json.loads(json.dumps(document['sidecar']))
        sidecar['notes'][0]['learner_wording'] = 'PRIVATE_ONLY'
        notes.write_note_document(private, cid, document['markdown'] + '\nPRIVATE_ONLY\n',
                                  sidecar, document['fingerprint'])
        before = tree(self.base)
        result = search.search(self.base, 'EXCLUDED SENTINEL')
        self.assertEqual(len(result['hits']), 1, 'Saved model scope must not limit deliberate course search')
        for query in ('UNREGISTERED_ONLY', 'PRIVATE_ONLY', 'CORRECT:'):
            self.assertEqual(search.search(self.base, query)['hits'], [])
        self.assertEqual(tree(self.base), before)

    def test_query_validation_case_sensitive_unicode_and_empty_course(self):
        for query in ('', ' ', '\n', '\x7f', 'x' * 161, None, 12):
            with self.assertRaises(ValueError):
                search.search(self.base, query)
        sid = self.add_source('🟣 Same phrase. Same phrase.\n')
        result = search.search(self.base, 'Same phrase.')
        hits = [hit for hit in result['hits'] if hit['source_id'] == sid]
        self.assertEqual([(hit['start'], hit['end']) for hit in hits], [(2, 14), (15, 27)])
        self.assertEqual(search.search(self.base, 'same phrase.')['hits'], [])
        empty = self.root / 'empty'
        empty.mkdir()
        course.create_course(str(empty), 'Empty fictional course', 'human', 'test')
        result = search.search(str(empty), 'needle')
        self.assertEqual(result['sources_total'], 0)
        self.assertEqual(result['hits'], [])
        self.assertEqual(result['omitted_sources'], [])

    def test_changed_rights_missing_source_and_symlink_escape_do_not_disclose(self):
        record = journal.read_registry(self.base)[self.refs[0]['source_id']]
        path = Path(self.base, record['path'])
        original = path.read_bytes()
        path.write_text('CHANGED_ONLY Same sentence.\n')
        result = search.search(self.base, 'Same')
        self.assertEqual(result['hits'], [])
        self.assertEqual(result['omitted_sources'][0]['state'], 'stale')
        path.write_bytes(original)
        journal.op_grant_rights(self.base, self.refs[0]['source_id'], {'quote': 'unknown'},
                                record['fingerprint'], 'human', 'test')
        result = search.search(self.base, 'Same')
        self.assertEqual(result['hits'], [])
        self.assertEqual(result['omitted_sources'][0]['state'], 'rights_unavailable')
        journal.op_grant_rights(self.base, self.refs[0]['source_id'], record['rights'],
                                record['fingerprint'], 'human', 'test')
        path.unlink()
        outside = self.root / 'outside.md'
        outside.write_bytes(original)
        os.symlink(outside, path)
        self.assertEqual(search.search(self.base, 'Same')['hits'], [])
        path.unlink()
        self.assertEqual(search.search(self.base, 'Same')['hits'], [])

    def test_tampered_sidecar_cannot_redirect_duplicate_passages(self):
        record = journal.read_registry(self.base)[self.refs[0]['source_id']]
        path = Path(self.base, source_adapters.sidecar_path_for(record['path']))
        sidecar = json.loads(path.read_text())
        first = next(row for row in sidecar['locators'] if row['id'] == 'L2')
        second = next(row for row in sidecar['locators'] if row['id'] == 'L4')
        second['span_id'], second['body'] = first['span_id'], first['body']
        path.write_text(json.dumps(sidecar))
        before = tree(self.base)
        result = search.search(self.base, 'Same')
        self.assertEqual(result['hits'], [])
        self.assertEqual(result['omitted_sources'][0]['state'], 'stale')
        self.assertEqual(tree(self.base), before)

    def test_changed_source_during_scan_discards_earlier_matches(self):
        original = research_context._safe_source
        calls = 0
        path = Path(self.base, journal.read_registry(self.base)[self.refs[0]['source_id']]['path'])
        def change(base, ref):
            nonlocal calls
            calls += 1
            passage = original(base, ref)
            if calls == 2:
                path.write_text('CONCURRENT_CHANGED_ONLY\n')
            return passage
        with patch.object(research_context, '_safe_source', side_effect=change):
            result = search.search(self.base, 'Same')
        self.assertEqual(result['hits'], [])
        self.assertTrue(any(row['source_id'] == self.refs[0]['source_id'] for row in result['omitted_sources']))

    def test_bounded_coverage_distinguishes_omission_from_no_matches(self):
        self.add_source(' '.join(['needle'] * 40) + '\n')
        result = search.search(self.base, 'needle')
        self.assertEqual(len(result['hits']), 32)
        self.assertTrue(result['limited'])
        self.assertEqual(len({hit['start'] for hit in result['hits']}), 32)
        with patch.object(search, 'MAX_SOURCES', 1):
            result = search.search(self.base, 'EXCLUDED SENTINEL')
            self.assertTrue(result['limited'])
            self.assertEqual(result['sources_searched'], 1)
            self.assertEqual(result['hits'], [])
        with patch.object(search, 'MAX_PASSAGES', 1):
            result = search.search(self.base, 'Same')
            self.assertTrue(result['limited'])
            self.assertEqual(result['passages_searched'], 1)
        with patch.object(search, 'MAX_CORPUS_BYTES', 1):
            result = search.search(self.base, 'Same')
            self.assertTrue(result['limited'])
            self.assertEqual(result['passages_searched'], 0)

    def test_later_source_change_rechecks_earlier_hits_and_course_list(self):
        original = research_context._safe_source
        path = Path(self.base, journal.read_registry(self.base)[self.refs[0]['source_id']]['path'])
        raw = path.read_bytes()
        def change_earlier(base, ref):
            passage = original(base, ref)
            if ref['source_id'] == self.refs[1]['source_id']:
                path.write_text('LATE_CHANGED_ONLY\n')
            return passage
        with patch.object(research_context, '_safe_source', side_effect=change_earlier):
            result = search.search(self.base, 'Same')
        self.assertEqual(result['hits'], [])
        path.write_bytes(raw)
        sid = self.add_source('NEW_CORPUS_ONLY\n', registered=False)
        changed = False
        def change_list(base, ref):
            nonlocal changed
            passage = original(base, ref)
            if not changed:
                changed = True
                read = course.read_course(base)
                graph.add_source(read['doc'], sid, 'A concurrently registered fictional source')
                course.write_course(base, read['doc'], read['fingerprint'], 'human', 'test')
            return passage
        with patch.object(research_context, '_safe_source', side_effect=change_list):
            with self.assertRaisesRegex(ValueError, 'course source list changed'):
                search.search(self.base, 'Same')

    def test_exact_match_preview_range_quote_admission_and_static_escape(self):
        sid = self.add_source('🟣 <script>Same phrase.</script> Same phrase.\n')
        hit = [item for item in search.search(self.base, 'Same phrase.')['hits'] if item['source_id'] == sid][-1]
        ref = {key: hit[key] for key in ('source_id', 'fingerprint', 'locator_id')}
        preview = {'status': 'preview', 'citation': ref, 'passage': research_context._safe_source(self.base, ref)}
        request = {'return_query': ['Same phrase.'], 'match_start': [str(hit['start'])], 'match_end': [str(hit['end'])]}
        result = search.admit_match(self.base, preview, request)
        self.assertEqual(result['match_start'], hit['start'])
        markup = search.preview_text(result)
        self.assertEqual(markup.count('<mark>Same phrase.</mark>'), 1)
        self.assertIn('&lt;script&gt;Same phrase.&lt;/script&gt;', markup)
        self.assertNotIn('<script>', markup)
        panel = search.panel(self.base, result)
        self.assertIn('Return to this course source search', panel)
        self.assertIn('value="Same phrase."', panel)
        with self.assertRaises(ValueError):
            search.admit_match(self.base, preview, dict(request, match_start=['0']))
        with self.assertRaises(ValueError):
            search.admit_match(self.base, preview, dict(request, match_start=['0', '2']))
        journal.op_grant_rights(self.base, sid, {'quote': 'denied'}, ref['fingerprint'], 'human', 'test')
        with self.assertRaisesRegex(ValueError, 'quote rights'):
            search.admit_match(self.base, preview, request)

    def test_size_admission_precedes_journal_content_reads_and_bad_sidecars(self):
        with patch.object(search, 'MAX_FILE_BYTES', 8), patch.object(journal, 'object_state', wraps=journal.object_state) as content_read:
            result = search.search(self.base, 'Same')
        source_ids = {ref['source_id'] for ref in self.refs}
        self.assertFalse(any(call.args[1] in source_ids for call in content_read.call_args_list))
        self.assertEqual(result['sources_searched'], 0)
        self.assertEqual(result['hits'], [])
        self.assertTrue(all(item['state'] == 'unsupported' for item in result['omitted_sources']))
        record = journal.read_registry(self.base)[self.refs[0]['source_id']]
        Path(self.base, source_adapters.sidecar_path_for(record['path'])).write_text('[]')
        result = search.search(self.base, 'Same')
        self.assertEqual(result['hits'], [])
        self.assertEqual(result['omitted_sources'][0]['state'], 'unsupported')

    def test_offline_fresh_process_search_has_no_accepted_side_effects(self):
        before = tree(self.base)
        child = subprocess.run([sys.executable, __file__, '--search', self.base],
                               capture_output=True, text=True, timeout=10)
        self.assertEqual(child.returncode, 0, child.stderr)
        self.assertEqual(child.stdout.strip(), '2')
        self.assertEqual(tree(self.base), before)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--search':
        print(len(search.search(sys.argv[2], 'Same sentence.')['hits']))
    else:
        unittest.main()
