#!/usr/bin/env python3
"""Pure source help admission, exact citations, owned cancellation and no writes."""
from contextlib import contextmanager
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
import course
import identity
import journal
import model_adapter
import notes
import reading_desk
import source_adapters
from surfaces import context_help as help_surface, course_ops, research_context
from a5_research_context_roundtrip import fixture
import reading_ops_roundtrip as reading_operations


CFG = {'model_backend': {'active': 'synthetic', 'profiles': [{'name': 'synthetic',
    'transport': 'synthetic_help', 'model': 'fictional', 'timeout_seconds': 5,
    'max_output_bytes': 65536, 'context_window': 8192}]}}


def tree(base):
    return {str(p.relative_to(base)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in Path(base).rglob('*') if p.is_file()}


@contextmanager
def synthetic_contract(transport):
    """Test-only candidate contract while direct production acceptance is pending."""
    schema = copy.deepcopy(model_adapter._SCHEMA)
    schema['$defs']['request']['properties']['operation']['enum'].append('source_question')
    schema['$defs']['payload']['properties']['context_request'] = {'type': 'object'}
    with patch.object(model_adapter, '_SCHEMA', schema), patch.object(model_adapter, '_PAYLOAD_KEYS',
            (*model_adapter._PAYLOAD_KEYS, 'context_request')), patch.dict(model_adapter.TRANSPORT_REGISTRY,
            {'synthetic_help': transport}):
        yield


def candidate(payload):
    return {'schema_version': 1, 'answer': 'The invented phrase is repeated in the selected source.',
            'citations': [{'citation_id': 'S1', 'quote': payload['source_spans'][0]['text']}],
            'uncertainty': 'Synthetic advice; no learning or factual-support acceptance is implied.'}


def transport(request, **_kwargs):
    return {'status': 'ok', 'candidate': candidate(request['payload']['context_request'])}


def wait(base, request_id, cfg=CFG):
    until = time.monotonic() + 5
    while time.monotonic() < until:
        result = help_surface.status(base, {'request_id': request_id}, cfg)
        if result['state'] != 'running':
            return result
        time.sleep(.01)
    raise AssertionError('Synthetic request did not finish')


class SourceHelp(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='context_help_')
        self.addCleanup(self.temp.cleanup)
        self.base, self.refs = fixture(Path(self.temp.name))
        self.read = course.read_course(self.base)
        self.body = {'expected_fingerprint': self.read['fingerprint'],
                     'source': self.refs[0], 'question': 'Why is this invented phrase repeated?', 'note_ids': []}

    def test_exact_duplicate_picker_preview_and_private_note_exclusion(self):
        token = {k: self.refs[0][k] for k in ('source_id', 'fingerprint')}
        choices = research_context.locator_choices(self.base, token)
        repeated = [r for r in choices if r['label'].endswith('Same sentence.')]
        self.assertEqual([r['ref']['locator_id'] for r in repeated], ['L2', 'L4'])
        self.assertNotEqual(repeated[0]['label'], repeated[1]['label'])
        copied = notes.transfer_source_note(self.base, reading_desk.note_root(self.base), self.read['object_id'],
            self.refs[0], 'copy', None, confirm=True)
        document = notes.read_note_document(reading_desk.note_root(self.base), self.read['object_id'])
        sidecar = copy.deepcopy(document['sidecar'])
        excluded = copy.deepcopy(sidecar['notes'][0])
        excluded.update(note_id=notes.new_note_id(), learner_wording='EXCLUDED_PRIVATE_SENTINEL')
        sidecar['notes'].append(excluded)
        document = notes.write_note_document(reading_desk.note_root(self.base), self.read['object_id'],
            document['markdown'] + '\nEXCLUDED_PRIVATE_SENTINEL\n', sidecar, document['fingerprint'])
        body = dict(self.body, note_ids=[sidecar['notes'][0]['note_id']], notes_fingerprint=document['fingerprint'])
        before = tree(self.base)
        preview = help_surface.preview(self.base, body, CFG)
        self.assertEqual(preview['source_spans'][0]['locator_id'], 'L4')
        self.assertEqual(preview['excluded_notes'], 1)
        self.assertNotIn('EXCLUDED_PRIVATE_SENTINEL', json.dumps(preview))
        captured = []
        def capture(request, **kwargs):
            captured.append(request)
            return transport(request, **kwargs)
        with synthetic_contract(capture):
            # Fresh preview reflects candidate-contract readiness without changing any file.
            preview = help_surface.preview(self.base, body, CFG)
            first = help_surface.start(self.base, {'preview_id': preview['preview_id'], 'confirm': True}, CFG)
            result = wait(self.base, first['request_id'])
            self.assertEqual(result['state'], 'answered', result)
            replay = help_surface.start(self.base, {'preview_id': preview['preview_id'], 'confirm': True}, CFG)
            self.assertEqual(replay['request_id'], first['request_id'])
        self.assertEqual(len(captured), 1)
        self.assertEqual(captured[0]['operation'], 'source_question')
        self.assertNotIn('EXCLUDED_PRIVATE_SENTINEL', json.dumps(captured))
        self.assertEqual(tree(self.base), before, 'Help wrote durable files or evidence')

    def test_bank_formal_linkage_unknown_denied_stale_and_profile_off(self):
        before = tree(self.base)
        for body in (dict(self.body, source=self.refs[2]), dict(self.body, session_id='formal'),
                     dict(self.body, permitted_tier=5)):
            with self.assertRaises(ValueError):
                help_surface.preview(self.base, body, CFG)
        disabled = {'model_backend': {'active': '', 'profiles': []}}
        preview = help_surface.preview(self.base, self.body, disabled)
        with synthetic_contract(transport), self.assertRaisesRegex(ValueError, 'Enable'):
            help_surface.start(self.base, {'preview_id': preview['preview_id'], 'confirm': True}, disabled)
        self.assertEqual(tree(self.base), before)
        for state in ('unknown', 'denied'):
            journal.op_grant_rights(self.base, self.refs[0]['source_id'], {'remote_process': state},
                self.refs[0]['fingerprint'], 'human', 'test')
            with self.assertRaisesRegex(ValueError, state):
                help_surface.preview(self.base, self.body, CFG)
        journal.op_grant_rights(self.base, self.refs[0]['source_id'], {'remote_process': 'granted'},
            self.refs[0]['fingerprint'], 'human', 'test')
        row = journal.read_registry(self.base)[self.refs[0]['source_id']]
        Path(self.base, row['path']).write_text('CHANGED_SOURCE_MUST_BE_WITHHELD')
        with self.assertRaises(ValueError):
            help_surface.preview(self.base, self.body, CFG)

    def test_no_unsupported_contract_provider_request(self):
        preview = help_surface.preview(self.base, self.body, CFG)
        before = tree(self.base)
        with patch.object(model_adapter, 'invoke') as invoke:
            for malformed in ([], {}, None, '', 'x' * 129):
                with self.assertRaises(ValueError):
                    help_surface.start(self.base, {'preview_id': malformed, 'confirm': True}, CFG)
            invoke.assert_not_called()
        self.assertEqual(tree(self.base), before)
        with patch.object(help_surface, 'contract_ready', return_value=False), patch.object(model_adapter, 'invoke') as invoke:
            with self.assertRaisesRegex(ValueError, 'contract'):
                help_surface.start(self.base, {'preview_id': preview['preview_id'], 'confirm': True}, CFG)
            invoke.assert_not_called()

    def test_unaccepted_locator_sidecar_cannot_redirect_a_duplicate(self):
        row = journal.read_registry(self.base)[self.refs[0]['source_id']]
        path = Path(self.base, source_adapters.sidecar_path_for(row['path']))
        sidecar = json.loads(path.read_text())
        first = next(loc for loc in sidecar['locators'] if loc['id'] == 'L2')
        second = next(loc for loc in sidecar['locators'] if loc['id'] == 'L4')
        second['span_id'] = first['span_id']
        path.write_text(json.dumps(sidecar))
        with self.assertRaises(ValueError):
            help_surface.preview(self.base, self.body, CFG)
        with self.assertRaises(ValueError):
            research_context.locator_choices(self.base, {k: self.refs[0][k] for k in ('source_id', 'fingerprint')})

    def test_candidate_refuses_bad_citations_extra_fields_and_note_only_support(self):
        preview = help_surface.preview(self.base, self.body, CFG)
        for bad in (dict(candidate(preview), score=1), dict(candidate(preview), citations=[]),
                    dict(candidate(preview), citations=[{'citation_id': 'N1', 'quote': 'private'}]),
                    dict(candidate(preview), citations=[{'citation_id': 'S1', 'quote': 'invented outside quote'}])):
            with self.assertRaises(ValueError):
                help_surface.validate_candidate(bad, preview)
        good = candidate(preview)
        self.assertEqual(help_surface.validate_candidate(good, preview), good)

    def test_cancel_discards_late_success_and_restart_does_not_replay(self):
        entered, release = threading.Event(), threading.Event()
        def late(request, **kwargs):
            entered.set()
            release.wait(4)
            return transport(request, **kwargs)
        before = tree(self.base)
        with synthetic_contract(late):
            preview = help_surface.preview(self.base, self.body, CFG)
            started = help_surface.start(self.base, {'preview_id': preview['preview_id'], 'confirm': True}, CFG)
            self.assertTrue(entered.wait(2))
            canceled = help_surface.cancel(self.base, {'request_id': started['request_id']}, CFG)
            self.assertEqual(canceled['state'], 'canceled')
            release.set()
            job = help_surface._JOBS[(str(Path(self.base).resolve()), started['request_id'])]
            self.assertTrue(job['done'].wait(2))
            self.assertEqual(wait(self.base, started['request_id'])['state'], 'canceled')
            self.assertNotIn('candidate', wait(self.base, started['request_id']))
        with patch.dict(help_surface._JOBS, {}, clear=True), patch.object(model_adapter, 'invoke') as invoke:
            result = help_surface.status(self.base, {'request_id': started['request_id']}, CFG)
            self.assertEqual(result['code'], 'help.request_unowned')
            invoke.assert_not_called()
        self.assertEqual(tree(self.base), before)

    def test_source_changes_before_send_during_request_and_after_answer(self):
        entered, release = threading.Event(), threading.Event()
        row = journal.read_registry(self.base)[self.refs[0]['source_id']]
        path = Path(self.base, row['path'])
        original = path.read_bytes()
        with synthetic_contract(transport):
            preview = help_surface.preview(self.base, self.body, CFG)
            path.write_text('WITHHELD_BEFORE_SEND')
            with patch.object(model_adapter, 'invoke') as invoke, self.assertRaises(ValueError):
                help_surface.start(self.base, {'preview_id': preview['preview_id'], 'confirm': True}, CFG)
            invoke.assert_not_called()
            path.write_bytes(original)
            first = help_surface.start(self.base, {'preview_id': preview['preview_id'], 'confirm': True}, CFG)
            self.assertEqual(wait(self.base, first['request_id'])['state'], 'answered')
            path.write_text('WITHHELD_AFTER_ANSWER')
            self.assertEqual(wait(self.base, first['request_id'])['state'], 'unavailable')
            path.write_bytes(original)
        def late(request, **kwargs):
            entered.set(); release.wait(4)
            return transport(request, **kwargs)
        with synthetic_contract(late):
            preview = help_surface.preview(self.base, self.body, CFG)
            first = help_surface.start(self.base, {'preview_id': preview['preview_id'], 'confirm': True}, CFG)
            self.assertTrue(entered.wait(2))
            path.write_text('WITHHELD_DURING_REQUEST')
            release.set()
            result = wait(self.base, first['request_id'])
            self.assertEqual(result['state'], 'unavailable', result)
            self.assertNotIn('candidate', result)


class ReadingSelection(unittest.TestCase):
    run_op = reading_operations.ReadingOperations.run_op
    read = reading_operations.ReadingOperations.read
    bind = reading_operations.ReadingOperations.bind
    values = reading_operations.ReadingOperations.values
    create = reading_operations.ReadingOperations.create

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='help_selection_')
        self.addCleanup(self.temp.cleanup)
        self.root = self.temp.name
        self.base = str(Path(self.root, 'synthetic'))
        self.run_op('create', title='Synthetic selected reading')
        self.run_op('add_objective', statement='Compare invented repetitions')
        self.objective = self.read()['doc']['objectives'][0]['id']
        source = self.run_op('register_source', filename='example.md',
            content='# Example\n🟣 Same phrase. Same phrase.\n', grants={op: 'granted' for op in identity.RIGHTS_OPERATIONS})
        self.source_id, self.source_fp = source['source_object_id'], source['fingerprint']
        self.run_op('add_source', source_object_id=self.source_id, title='Invented repetition')
        self.bind('line 2')
        self.row = self.create()['occurrence']

    def test_second_duplicate_exact_offsets_unicode_and_exact_return(self):
        raw = course.validate_reading_source(self.base, self.row['source_ref'])['verbatim']
        start = raw.rindex('Same phrase.')
        body = {'expected_fingerprint': self.read()['fingerprint'],
                'reading': {k: self.row[k] for k in ('occurrence_id', 'revision_id')},
                'selection': {'start': start, 'end': start + len('Same phrase.'), 'quote': 'Same phrase.'},
                'question': 'Why is the second phrase repeated?', 'note_ids': []}
        before = tree(self.base)
        preview = help_surface.preview(self.base, body, CFG)
        self.assertEqual(preview['source_spans'][0]['text'], 'Same phrase.')
        self.assertEqual(preview['return_href'], '/course/synthetic/reading/%s/%s#source-content' % (
            self.row['occurrence_id'], self.row['revision_id']))
        for selection in ({'start': start - 1, 'end': start + 11, 'quote': 'Same phrase.'},
                          {'start': True, 'end': 3, 'quote': 'Same phrase.'}):
            with self.assertRaises(ValueError):
                help_surface.preview(self.base, dict(body, selection=selection), CFG)
        self.assertEqual(tree(self.base), before)


if __name__ == '__main__':
    unittest.main()
