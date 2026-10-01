#!/usr/bin/env python3
"""Real director receipts, delayed requests, process restart and native page."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest import mock
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tests'))
import director
import journal
import model_adapter
import sample_course
from surfaces import agent_operation as ao, ia
from daemon_roundtrip import start_daemon


def configured():
    return {'agent_runs': {'fictional-author': {'target': 'draft.md', 'kind': 'bank',
            'request': 'Draft fictional content.', 'source_paths': ['source.md'], 'citations': []}},
            'auditor_autonomy': 'draft_and_approve',
            'model_backend': {'active': 'fictional', 'profiles': [{'name': 'fictional',
             'transport': 'openai_compatible', 'endpoint': 'http://127.0.0.1:1/v1/chat/completions',
             'model': 'fictional', 'timeout_seconds': 2, 'max_output_bytes': 65536,
             'context_window': 32768}]}}


def candidate():
    return {'status': 'ok', 'candidate': {'draft': (ROOT / 'fixtures/sample_bank.md').read_text(),
                                         'citations': []}}


class RequestRecovery(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='author-recovery-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        ia.apply_shelf_action(str(self.root), 'add_sample_course')
        self.base = Path(ia.course_dir_for(str(self.root), sample_course.SAMPLE_COURSE_ID))
        (self.base / 'source.md').write_text('# Fictional source\n')
        (self.base / 'draft.md').write_text('# Existing fictional draft\n')
        (self.root / 'itembank.json').write_text(json.dumps(configured()))
        self.original = (self.base / 'draft.md').read_bytes()

    def test_delayed_call_is_visible_and_never_accepts_or_retries(self):
        entered, release = threading.Event(), threading.Event()
        outcomes, calls = [], []
        def delayed(*args):
            calls.append(1)
            entered.set()
            if not release.wait(5):
                raise RuntimeError('Synthetic barrier timed out')
            return candidate()
        with mock.patch.object(model_adapter, 'invoke', side_effect=delayed):
            thread = threading.Thread(target=lambda: outcomes.append(ao.start('fictional-author', configured(), str(self.base))))
            thread.start()
            try:
                self.assertTrue(entered.wait(3))
                rows = ao.request_history(str(self.base))
                self.assertEqual(len(rows), 1)
                self.assertEqual(rows[0]['request_state'], 'unresolved')
                self.assertEqual(director.resume_point(str(self.base), rows[0]['operation_id'])['last_phase'], 'declare-intent')
                self.assertIn('cost', rows[0]['next_action'])
                self.assertEqual((self.base / 'draft.md').read_bytes(), self.original)
                self.assertEqual(ao.pending(str(self.base)), [])
            finally:
                release.set()
                thread.join(5)
        self.assertFalse(thread.is_alive())
        self.assertEqual(calls, [1])
        self.assertEqual(outcomes[0]['state'], 'proposed')
        self.assertEqual(ao.request_history(str(self.base))[0]['request_state'], 'proposed')
        before = len(list(journal.entries(str(self.base))))
        for _ in range(3):
            ao.request_history(str(self.base))
        self.assertEqual(len(list(journal.entries(str(self.base)))), before)

    def test_hard_exit_before_result_and_after_saved_candidate_reopens_exactly(self):
        for boundary in ('invoke', 'persisted'):
            process = subprocess.run([sys.executable, __file__, '--exit', boundary, str(self.base)],
                                     capture_output=True, text=True, timeout=15)
            self.assertEqual(process.returncode, 31, process.stderr)
            rows = ao.request_history(str(self.base))
            row = next(r for r in rows if r['request_state'] == ('unresolved' if boundary == 'invoke' else 'proposed'))
            self.assertEqual((self.base / 'draft.md').read_bytes(), self.original)
            reopened = subprocess.run([sys.executable, __file__, '--reopen', str(self.base), row['operation_id']],
                                      capture_output=True, text=True, timeout=15)
            self.assertEqual(reopened.returncode, 0, reopened.stderr)
            self.assertEqual(reopened.stdout.strip(), row['request_state'])

    def test_unavailable_and_source_change_have_durable_named_recovery(self):
        unavailable = model_adapter.unavailable_result('adapter.unreachable', 'Fictional unavailable', 'test')
        with mock.patch.object(model_adapter, 'invoke', return_value=unavailable):
            result = ao.start('fictional-author', configured(), str(self.base))
        self.assertEqual(result['code'], 'adapter.unreachable')
        self.assertTrue(any(r.get('code') == result['code'] and r['request_state'] == 'settled'
                            for r in ao.request_history(str(self.base))))
        def stale(*args):
            (self.base / 'source.md').write_text('# Changed fictional source\n')
            return candidate()
        with mock.patch.object(model_adapter, 'invoke', side_effect=stale):
            result = ao.start('fictional-author', configured(), str(self.base))
        self.assertEqual(result['code'], 'agent.source_stale')
        self.assertEqual((self.base / 'draft.md').read_bytes(), self.original)

    def test_metadata_failure_prevents_provider_call_and_interrupt_never_replays(self):
        with mock.patch.object(director, 'begin_operation', side_effect=OSError('disk full')):
            with mock.patch.object(model_adapter, 'invoke') as invoke:
                with self.assertRaises(OSError):
                    ao.start('fictional-author', configured(), str(self.base))
                invoke.assert_not_called()
        with mock.patch.object(model_adapter, 'invoke', side_effect=KeyboardInterrupt) as invoke:
            with self.assertRaises(KeyboardInterrupt):
                ao.start('fictional-author', configured(), str(self.base))
            self.assertEqual(invoke.call_count, 1)
        self.assertEqual(ao.request_history(str(self.base))[0]['request_state'], 'unresolved')
        self.assertEqual((self.base / 'draft.md').read_bytes(), self.original)

    def test_native_served_agent_page_reports_interrupted_request(self):
        with mock.patch.object(model_adapter, 'invoke', side_effect=SystemExit('cancel')):
            with self.assertRaises(SystemExit):
                ao.start('fictional-author', configured(), str(self.base))
        process, url, lines = start_daemon(str(self.root))
        try:
            page = urllib.request.urlopen(url + 'course/' + sample_course.SAMPLE_COURSE_ID + '/agent', timeout=5).read().decode()
            self.assertIn('Author request recovery', page)
            self.assertIn('unresolved', page)
            self.assertIn('retry may repeat provider work and cost', page)
            self.assertIn('fictional-author', page)
            self.assertEqual((self.base / 'draft.md').read_bytes(), self.original)
        finally:
            process.terminate()
            process.wait(timeout=8)
            if process.stdout:
                process.stdout.close()


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--exit':
        boundary, base = sys.argv[2:]
        if boundary == 'invoke':
            model_adapter.invoke = lambda *args: os._exit(31)
        else:
            model_adapter.invoke = lambda *args: candidate()
            write = ao._write_record
            def persist_then_exit(*args):
                write(*args)
                os._exit(31)
            ao._write_record = persist_then_exit
        ao.start('fictional-author', configured(), base)
    elif len(sys.argv) > 1 and sys.argv[1] == '--reopen':
        base, operation_id = sys.argv[2:]
        print(next(r['request_state'] for r in ao.request_history(base) if r['operation_id'] == operation_id))
    else:
        unittest.main()
