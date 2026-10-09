#!/usr/bin/env python3
"""Owned local transport cancellation, late-result refusal and linked retry."""
import json
import os
from pathlib import Path
import sys
import subprocess
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
import course
import journal
import model_adapter
from surfaces import agent_operation as ao, daemon, course_ops
from course_guidance_journey_roundtrip import fixture, served, get
from a5_served_integration_roundtrip import request


def config(script):
    return {'agent_runs': {'fictional-author': {'target': 'draft.md', 'kind': 'bank',
        'request': 'Draft synthetic content.', 'source_paths': ['sources/example.md'], 'citations': []}},
        'auditor_autonomy': 'draft_and_approve',
        'model_backend': {'active': 'synthetic', 'profiles': [{'name': 'synthetic',
            'transport': 'hosted_cli', 'command': [sys.executable, str(script)],
            'model': 'fictional', 'timeout_seconds': 5, 'max_output_bytes': 65536,
            'context_window': 4096}]}}


def wait_for(predicate):
    deadline = time.monotonic() + 6
    while time.monotonic() < deadline:
        result = predicate()
        if result:
            return result
        time.sleep(0.02)
    raise AssertionError('Synthetic request did not reach its expected state')


class CancelRetry(unittest.TestCase):
    def test_cli_async_launch_keeps_transport_owned_until_proposal_is_saved(self):
        with fixture() as (root, base, banks, info):
            script = root / 'fake_cli.txt'
            candidate = {'draft': '# Synthetic CLI draft\n', 'citations': []}
            script.write_text('import json,sys,time\njson.load(sys.stdin)\ntime.sleep(0.2)\n'
                'sys.stdout.write(' + repr(json.dumps(candidate)) + ')\n')
            (root / 'itembank.json').write_text(json.dumps(config(script)))
            result = subprocess.run([sys.executable, str(ROOT / 'itembank.py'), 'course',
                'agent-operation', 'synthetic', 'start_async', '--skill', 'fictional-author',
                '--root', str(root), '--json'], capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)['state'], 'proposed')
            self.assertEqual(ao.request_history(base)[0]['request_state'], 'proposed')

    def test_native_start_cancel_retry_review_accept_and_undo(self):
        with fixture() as (root, base, banks, info):
            script = root / 'fake_cli.txt'
            script.write_text('import json,sys,time\njson.load(sys.stdin)\ntime.sleep(30)\n')
            (root / 'itembank.json').write_text(json.dumps(config(script)))
            target = base / 'draft.md'
            target.write_text('# Existing synthetic draft\n')
            original = target.read_bytes()
            with served(root) as url:
                endpoint = url + 'course/synthetic/build'
                status, _, markup = request(endpoint, {'action': 'start_async', 'skill': 'fictional-author'})
                self.assertEqual(status, 200)
                first = ao.request_history(base)[0]
                self.assertIn('Cancel this request', markup)
                status, _, _ = request(endpoint, {'action': 'cancel', 'proposal_id': first['proposal_id']})
                self.assertEqual(status, 200)
                wait_for(lambda: ao.request_history(base)[0]['request_state'] == 'settled')
                self.assertEqual(ao.request_history(base)[0]['code'], 'adapter.cancelled')
                self.assertEqual(target.read_bytes(), original)
                candidate = {'draft': (ROOT / 'fixtures/sample_bank.md').read_text(), 'citations': []}
                script.write_text('import json,sys\njson.load(sys.stdin)\n'
                    'sys.stdout.write(' + repr(json.dumps(candidate)) + ')\n')
                status, _, _ = request(endpoint, {'action': 'retry', 'proposal_id': first['proposal_id']})
                self.assertEqual(status, 200)
                child = wait_for(lambda: next((r for r in ao.request_history(base)
                    if r['request_state'] == 'proposed'), None))
                self.assertEqual(child['retry_of'], first['operation_id'])
                self.assertEqual(target.read_bytes(), original)
                status, _, markup = request(endpoint, {'action': 'accept', 'proposal_id': child['proposal_id']})
                self.assertEqual(status, 200)
                self.assertIn('Proposal accepted', markup)
                status, _, markup = request(endpoint, {'action': 'undo', 'proposal_id': child['proposal_id']})
                self.assertEqual(status, 200)
                self.assertIn('Accepted change undone', markup)
                self.assertEqual(target.read_bytes(), original)

    def test_local_process_ends_no_proposal_retry_links_parent_and_publishes_once(self):
        with fixture() as (root, base, banks, info):
            script = root / 'fake_cli.txt'
            script.write_text('import json,sys,time\njson.load(sys.stdin)\ntime.sleep(30)\n')
            cfg = config(script)
            target = base / 'draft.md'
            target.write_text('# Existing synthetic draft\n')
            first = ao.start_background('fictional-author', cfg, base)
            pid = first['proposal_id']
            self.assertEqual(ao.request_history(base)[0]['request_state'], 'running')
            with self.assertRaisesRegex(ValueError, 'request_running'):
                ao.start_background('fictional-author', cfg, base)
            alias = root / 'course_alias'
            alias.symlink_to(base, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, 'request_running'):
                ao.start_background('fictional-author', cfg, alias)
            parent = ao.request_history(base)[0]['operation_id']
            ao.cancel_request(base, pid)
            wait_for(lambda: ao.request_history(base)[0]['request_state'] == 'settled')
            self.assertEqual(ao.request_history(base)[0]['code'], 'adapter.cancelled')
            self.assertEqual(ao.proposals(base), [])
            self.assertEqual(target.read_text(), '# Existing synthetic draft\n')
            script.write_text('import json,sys\njson.load(sys.stdin)\n'
                'json.dump({"draft":"# New synthetic draft\\n","citations":[]},sys.stdout)\n')
            second = ao.retry_request(base, pid, cfg)
            wait_for(lambda: any(r['request_state'] == 'proposed' for r in ao.request_history(base)))
            child = next(r for r in ao.request_history(base) if r['request_state'] == 'proposed')
            self.assertEqual(child['retry_of'], parent)
            self.assertNotEqual(child['proposal_id'], pid)
            self.assertNotEqual(child['interaction_id'], ao.request_history(base)[1]['interaction_id'])
            with self.assertRaises(ao.AgentRequestError) as finished:
                ao.cancel_request(base, child['proposal_id'])
            self.assertEqual(finished.exception.code, 'agent.request_finished')
            accepted = ao.accept(child['proposal_id'], cfg, base=base, reviewer='synthetic-human')
            self.assertTrue(accepted['ok'], accepted)
            before = list(journal.entries(base))
            ao.accept(child['proposal_id'], cfg, base=base, reviewer='synthetic-human')
            self.assertEqual(list(journal.entries(base)), before)

    def test_late_success_is_discarded_and_target_base_is_pinned_before_invoke(self):
        with fixture() as (root, base, banks, info):
            cfg = config(root / 'unused.txt')
            target = base / 'draft.md'
            target.write_text('# Original\n')
            entered, release = threading.Event(), threading.Event()
            def late(request, settings, **kwargs):
                entered.set()
                release.wait(3)
                return {'status': 'ok', 'candidate': {'draft': '# Late draft\n', 'citations': []}}
            with patch.object(model_adapter, 'invoke', side_effect=late):
                first = ao.start_background('fictional-author', cfg, base)
                self.assertTrue(entered.wait(1))
                ao.cancel_request(base, first['proposal_id'])
                release.set()
                wait_for(lambda: ao.request_history(base)[0]['request_state'] == 'settled')
            self.assertEqual(ao.proposals(base), [])
            self.assertEqual(target.read_text(), '# Original\n')
            def concurrent(request, settings):
                target.write_text('# User edit during provider work\n')
                return {'status': 'ok', 'candidate': {'draft': '# Stale draft\n', 'citations': []}}
            with patch.object(model_adapter, 'invoke', side_effect=concurrent):
                proposed = ao.start('fictional-author', cfg, base)
            accepted = ao.accept(proposed['proposal_id'], cfg, base=base)
            self.assertFalse(accepted.get('ok', False))
            self.assertEqual(accepted['disposition'], 'conflicted')
            self.assertEqual(target.read_text(), '# User edit during provider work\n')

    def test_restart_receipt_is_unresolved_and_native_forms_expose_explicit_actions(self):
        with fixture() as (root, base, banks, info):
            cfg = config(root / 'unused.txt')
            entered, release = threading.Event(), threading.Event()
            def delayed(request, settings, **kwargs):
                entered.set()
                release.wait(3)
                return model_adapter.unavailable_result('adapter.timeout', 'Synthetic timeout', request['interaction_id'])
            with patch.object(model_adapter, 'invoke', side_effect=delayed):
                first = ao.start_background('fictional-author', cfg, base)
                self.assertTrue(entered.wait(1))
                self.addCleanup(release.set)
                with served(root) as url:
                    # Another process has no right to claim ownership of this transport.
                    markup = get(url, '/course/synthetic/build')
                    self.assertIn('unresolved', markup)
                    self.assertIn('may repeat provider cost', markup)
                handler = type('Handler', (), {'root': str(root), 'path': '/course/synthetic/build'})()
                with patch.object(daemon.settings, 'load_settings', return_value=cfg):
                    markup = daemon._agent_area_html(handler, {'course_id': 'synthetic', 'area': 'build'}, base)
                self.assertIn('Cancel this request', markup)
                self.assertIn('value="start_async"', markup)
                release.set()
                wait_for(lambda: ao.request_history(base)[0]['request_state'] == 'settled')
            with self.assertRaisesRegex(ValueError, 'transport_unowned'):
                ao.cancel_request(base, first['proposal_id'])
            with self.assertRaises(ao.AgentRequestError) as refusal:
                course_ops.run(root, 'agent_operation', {'course_id': 'synthetic',
                    'action': 'cancel', 'proposal_id': first['proposal_id']})
            self.assertEqual(refusal.exception.code, 'agent.transport_unowned')


if __name__ == '__main__':
    unittest.main()
