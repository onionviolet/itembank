#!/usr/bin/env python3
"""Selected-context retrieval, exact occurrences and fail-closed disclosure."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tests'))
import course
import graph
import identity
import journal
import notes
import reading_desk
import source_adapters
from surfaces import research_context as rc
from a5_research_context_roundtrip import fixture, fields
from daemon_roundtrip import start_daemon


def tree(root):
    return {str(p.relative_to(root)): p.read_bytes()
            for p in Path(root).rglob('*') if p.is_file()}


class SelectedSearch(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='selected-search-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.base, self.refs = fixture(self.root)
        self.cid = course.read_course(self.base)['object_id']
        self.first = dict(self.refs[0], locator_id='L2')
        copied = rc.apply(self.base, fields(self.first, 'copy', confirm='yes'))
        self.notes_fingerprint = copied['document']['fingerprint']
        self.note_id = notes.read_note_document(reading_desk.note_root(self.base), self.cid)['sidecar']['notes'][-1]['note_id']
        self.select([self.first, self.refs[0]], [self.note_id])

    def select(self, refs, note_ids):
        scope_root, _ = rc._roots(self.base)
        current = source_adapters.read_context_scope(scope_root, self.cid)
        return rc.apply(self.base, {'operation': ['save_scope'],
            'reference': [json.dumps(ref) for ref in refs], 'note_id': note_ids,
            'expected_notes_fingerprint': [self.notes_fingerprint if note_ids else ''],
            'expected_scope_fingerprint': [current['fingerprint'] if current else ''], 'confirm': ['yes']})

    def test_duplicate_occurrences_private_note_and_exclusions_remain_distinct(self):
        before = tree(Path(self.base))
        result = rc.search_selected(self.base, 'Same sentence.')
        self.assertEqual(result['status'], 'search')
        self.assertEqual(len(result['hits']), 3)
        self.assertEqual([row['locator_id'] for row in result['hits'] if row['kind'] == 'source'], ['L2', 'L4'])
        self.assertEqual(result['hits'][-1]['kind'], 'learner_note')
        self.assertEqual(result['excluded_sources'], 2)
        self.assertEqual(result['egress'], 'none')
        self.assertEqual(tree(Path(self.base)), before)
        self.assertNotIn('EXCLUDED SENTINEL', rc.panel(self.base, result))
        self.assertEqual(rc.search_selected(self.base, 'No match')['hits'], [])

    def test_query_validation_and_cancel_are_read_only(self):
        before = tree(Path(self.base))
        for query in ('', ' ', '\n', 'x' * 161, None):
            with self.assertRaises(ValueError):
                rc.search_selected(self.base, query)
        canceled = rc.apply(self.base, {'operation': ['cancel']})
        self.assertEqual(canceled['status'], 'canceled')
        self.assertEqual(tree(Path(self.base)), before)

    def test_stale_source_rights_and_symlink_escape_disclose_no_snippets(self):
        registry = journal.read_registry(self.base)
        row = registry[self.first['source_id']]
        path = Path(self.base, row['path'])
        original = path.read_bytes()
        path.write_bytes(b'Changed source with Same sentence.\n')
        result = rc.search_selected(self.base, 'Same')
        self.assertEqual(result['status'], 'search_unavailable')
        self.assertEqual(result['hits'], [])
        self.assertTrue(any(f['state'] == 'stale' for f in result['failures']))
        path.write_bytes(original)
        rights = dict(row['rights'], quote='denied')
        journal.op_grant_rights(self.base, self.first['source_id'], rights, row['fingerprint'], 'human', 'test')
        result = rc.search_selected(self.base, 'Same')
        self.assertEqual(result['hits'], [])
        self.assertTrue(any(f['state'] == 'unsupported' for f in result['failures']))
        journal.op_grant_rights(self.base, self.first['source_id'], row['rights'], row['fingerprint'], 'human', 'test')
        path.unlink()
        outside = self.root / 'outside.md'
        outside.write_bytes(original)
        os.symlink(outside, path)
        result = rc.search_selected(self.base, 'Same')
        self.assertEqual(result['status'], 'search_unavailable')
        self.assertEqual(result['hits'], [])

    def test_assessment_source_cannot_become_search_corpus(self):
        scope_root, private = rc._roots(self.base)
        current = source_adapters.read_context_scope(scope_root, self.cid)
        # Simulate another native client saving a scope that lacks the UI's
        # assessment exclusion. Search re-admits it before any snippet leaves.
        source_adapters.write_context_scope(scope_root, self.cid, [self.refs[2]], [], None,
                                            current['fingerprint'], self.base, private, confirm=True)
        before = tree(Path(self.base))
        result = rc.search_selected(self.base, 'CORRECT')
        self.assertEqual(result['status'], 'search_unavailable')
        self.assertEqual(result['hits'], [])
        self.assertEqual(tree(Path(self.base)), before)

    def test_hit_cap_and_unknown_rights_are_distinct_from_zero_results(self):
        raw = Path(self.base, 'bounded.md')
        raw.write_text(' '.join(['needle'] * 40) + '\n')
        linked = journal.op_link(self.base, 'source', 'bounded.md', 'human', 'test',
                                  rights={operation: 'granted' for operation in identity.RIGHTS_OPERATIONS})
        imported = source_adapters.import_source(self.base, 'markdown', linked['object_id'], 'human', 'test')
        sidecar = json.loads(Path(self.base, imported['sidecar_rel_path']).read_text())
        ref = {'source_id': imported['source_id'], 'fingerprint': sidecar['fingerprint'],
               'locator_id': sidecar['locators'][0]['id']}
        read = course.read_course(self.base)
        graph.add_source(read['doc'], ref['source_id'], 'Bounded fictional source')
        course.write_course(self.base, read['doc'], read['fingerprint'], 'human', 'test')
        self.select([ref], [])
        result = rc.search_selected(self.base, 'needle')
        self.assertEqual(len(result['hits']), 32)
        self.assertTrue(result['truncated'])
        self.assertEqual(len({hit['start'] for hit in result['hits']}), 32)
        journal.op_grant_rights(self.base, ref['source_id'], {'quote': 'unknown'}, ref['fingerprint'], 'human', 'test')
        result = rc.search_selected(self.base, 'needle')
        self.assertEqual(result['status'], 'search_unavailable')
        self.assertEqual(result['hits'], [])

    def test_offline_fresh_process_and_native_search_open_exact_occurrence(self):
        child = subprocess.run([sys.executable, __file__, '--reopen', self.base],
                               capture_output=True, text=True, timeout=10)
        self.assertEqual(child.returncode, 0, child.stderr)
        self.assertEqual(child.stdout.strip(), '3')
        process, url, _lines = start_daemon(str(self.root))
        try:
            before = tree(Path(self.base))
            address = url + 'course/' + self.cid + '/research'
            data = urllib.parse.urlencode({'operation': 'search_context', 'query': 'Same sentence.'}).encode()
            page = urllib.request.urlopen(urllib.request.Request(address, data=data), timeout=5).read().decode()
            self.assertIn('3 hits', page)
            self.assertIn('Open exact source occurrence', page)
            self.assertIn('Private learner note', page)
            self.assertNotIn('EXCLUDED SENTINEL', page)
            self.assertEqual(tree(Path(self.base)), before)
            data = urllib.parse.urlencode({k: v[0] for k, v in fields(self.refs[0], 'preview').items()}).encode()
            page = urllib.request.urlopen(urllib.request.Request(address, data=data), timeout=5).read().decode()
            self.assertIn('locator L4', page)
            self.assertIn('Same sentence.', page)
            self.assertEqual(tree(Path(self.base)), before)
        finally:
            process.terminate()
            process.wait(timeout=8)
            if process.stdout:
                process.stdout.close()


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--reopen':
        print(len(rc.search_selected(sys.argv[2], 'Same sentence.')['hits']))
    else:
        unittest.main()
