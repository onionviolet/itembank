#!/usr/bin/env python3
"""Scoreless declarations, immutable receipts and failure recovery on synthetic data."""
import copy
import errno
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tests'))
import course
import director
import evidence
import graph
import journal
import reading
import schema_validate
from surfaces import course_ops
from daemon_roundtrip import start_daemon, json_request
import reading_ops_roundtrip


class ReadingDeclarations(unittest.TestCase):
    setUp = reading_ops_roundtrip.ReadingOperations.setUp
    run_op = reading_ops_roundtrip.ReadingOperations.run_op
    read = reading_ops_roundtrip.ReadingOperations.read
    bind = reading_ops_roundtrip.ReadingOperations.bind
    values = reading_ops_roundtrip.ReadingOperations.values
    def create(self, **overrides):
        records = graph.validate_reading_graph(self.read()['doc'])['occurrences']
        if not records:
            return reading_ops_roundtrip.ReadingOperations.create(self, **overrides)
        values = self.values()
        values['binding_ref'] = records[0]['binding_ref']
        return self.run_op('create_reading', expected_fingerprint=self.read()['fingerprint'],
                           values=values, title='Repeated reading', activation='Library')
    edit = reading_ops_roundtrip.ReadingOperations.edit

    def confirmation(self, occurrence=None):
        occurrence = occurrence or self.create()['occurrence']
        request = dict(expected_fingerprint=self.read()['fingerprint'],
                       occurrence_id=occurrence['occurrence_id'], revision_id=occurrence['revision_id'])
        receipt = self.run_op('confirm_reading', **request, confirmation='read')
        return dict(request, intent_id=receipt['intent_id'])

    def declare(self, request):
        return self.run_op('declare_reading', **request)

    def log(self):
        return evidence.log_path(self.base)

    def state(self, request):
        return evidence.reading_state(self.log(), self.read()['object_id'],
                                       request['occurrence_id'], request['revision_id'])

    def test_restart_full_history_replay(self):
        request = self.confirmation()
        first = self.declare(request)
        evidence.append_event(self.log(), evidence.retraction_event('unrelated', 'x' * (evidence.DEDUPE_WINDOW_BYTES + 100)))
        self.assertGreater(Path(self.log()).stat().st_size, evidence.DEDUPE_WINDOW_BYTES)
        program = 'import json,sys; from surfaces import course_ops; print(json.dumps(course_ops.run(sys.argv[1],"declare_reading",json.loads(sys.argv[2]))))'
        proc = subprocess.run([sys.executable, '-c', program, self.root,
                               json.dumps(dict(request, course_id='synthetic'))], cwd=ROOT,
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        replay = json.loads(proc.stdout)
        self.assertEqual(replay['event'], first['event'])
        self.assertEqual(replay['status'], 'already_recorded')
        self.assertEqual(self.state(request)['event_ids'], [first['event_id']])

    def test_concurrent_processes_one_receipt(self):
        request = self.confirmation()
        program = 'import json,sys; from surfaces import course_ops; print(json.dumps(course_ops.run(sys.argv[1],"declare_reading",json.loads(sys.argv[2]))))'
        args = [sys.executable, '-c', program, self.root, json.dumps(dict(request, course_id='synthetic'))]
        processes = [subprocess.Popen(args, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for _ in range(2)]
        results = []
        for proc in processes:
            out, err = proc.communicate(timeout=30)
            self.assertEqual(proc.returncode, 0, err)
            results.append(json.loads(out))
        self.assertEqual(results[0]['event_id'], results[1]['event_id'])
        self.assertEqual(sorted(r['status'] for r in results), ['already_recorded', 'recorded'])
        self.assertEqual(len(list(evidence.live_events(self.log()))), 1)

    def test_retraction_recorded_and_deduped_intents(self):
        occurrence = self.create()['occurrence']
        a = self.confirmation(occurrence)
        b = self.confirmation(occurrence)
        first = self.declare(a)
        self.assertEqual(self.declare(b)['event_id'], first['event_id'])
        evidence.append_event(self.log(), evidence.retraction_event(first['event_id'], 'Learner correction'))
        self.assertEqual(self.state(a)['state'], 'not-reported')
        self.assertTrue(self.declare(a)['retracted'])
        with self.assertRaisesRegex(course.CourseError, 'stale'):
            self.declare(b)
        fresh = self.confirmation(occurrence)
        second = self.declare(fresh)
        self.assertNotEqual(second['event_id'], first['event_id'])
        self.assertEqual(second['event']['dedupe_key'], first['event']['dedupe_key'])
        self.assertIsNotNone(second['event']['base_retraction_id'])
        self.assertTrue(self.declare(a)['retracted'])
        self.assertEqual(self.state(a)['event_ids'], [second['event_id']])

    def test_rights_replay_and_first_write_checks(self):
        occurrence = self.create()['occurrence']
        first_request = self.confirmation(occurrence)
        first = self.declare(first_request)
        other = self.create()['occurrence']
        pending = self.confirmation(other)
        for state in ('denied', 'unknown'):
            journal.op_grant_rights(self.base, self.source_id, {'read': state}, self.source_fp, 'human', 'test')
            with mock.patch.object(course, 'validate_reading_source', side_effect=AssertionError('source reopened')):
                self.assertEqual(self.declare(first_request)['event'], first['event'])
                self.assertEqual(self.declare(first_request)['availability']['state'], 'rights-'+state)
            with self.assertRaises(course.CourseError):
                self.declare(pending)
            with self.assertRaises(course.CourseError):
                self.confirmation(other)
        row = journal._compute_registry(self.base)[self.source_id]
        Path(self.base, row['path']).unlink()
        self.assertEqual(self.declare(first_request)['event_id'], first['event_id'])
        self.assertEqual(self.state(pending)['state'], 'not-reported')

    def test_revisions_placement_and_separate_assignments(self):
        first = self.create()
        other = self.create()
        request = self.confirmation(first['occurrence'])
        pending = self.confirmation(other['occurrence'])
        event = self.declare(request)
        self.assertEqual(self.state(pending)['state'], 'not-reported')
        self.edit('place_reading', first, title='Renamed', activation='Library')
        self.assertEqual(self.declare(request)['event_id'], event['event_id'])
        self.assertEqual(self.state(request)['state'], 'reported-read')
        with self.assertRaises(course.CourseError):
            self.declare(pending)
        revised = self.edit('revise_reading', first, changes={'purpose':'New demand'})
        newer = self.confirmation(revised['occurrence'])
        self.assertEqual(self.state(newer)['state'], 'not-reported')
        with self.assertRaises(course.CourseError):
            self.confirmation(first['occurrence'])
        self.assertEqual(self.declare(request)['event_id'], event['event_id'])

    def test_conflicting_payload_identity_and_closed_schema(self):
        request = self.confirmation()
        event = self.declare(request)['event']
        schema = json.loads((ROOT / 'schemas/response.schema.json').read_text())
        self.assertEqual(schema_validate.validate(event, schema), [])
        for field in ('score','bank','mastery','duration','correctness'):
            changed = dict(event, **{field:True})
            self.assertTrue(schema_validate.validate(changed, schema))
        for field in ('ts', 'session_id', 'intent_id', 'objective_ids'):
            changed = copy.deepcopy(event)
            changed[field] = ['0'*16] if field == 'objective_ids' else evidence.new_event_id()
            with self.assertRaises(ValueError):
                evidence.append_event(self.log(), changed, precommit=lambda:None)
        changed = copy.deepcopy(event)
        changed.update(intent_id='1'*16,event_id=evidence.new_event_id())
        changed['source_ref']['locator'] = 'another range'
        with self.assertRaisesRegex(ValueError, 'integrity conflict'):
            evidence.append_event(self.log(), changed, precommit=lambda:None)
        with self.assertRaises(course.CourseError):
            self.declare(dict(request, expected_fingerprint='sha256:'+'0'*64))
        with self.assertRaises(course.CourseError):
            self.declare(dict(request, intent_id='0'*16))

    def test_failed_partial_fsync_and_torn_writes(self):
        request = self.confirmation()
        before = Path(self.log()).read_bytes()
        actual_write = os.write
        def partial_then_full(fd, raw):
            actual_write(fd, raw[:19])
            raise OSError(errno.ENOSPC, 'synthetic disk full')
        for failure in (PermissionError('synthetic denied'), OSError(errno.ENOSPC, 'synthetic disk full')):
            with mock.patch.object(evidence.os, 'write', side_effect=failure):
                with self.assertRaises(course.CourseError): self.declare(request)
            self.assertEqual(Path(self.log()).read_bytes(), before)
        with mock.patch.object(evidence.os, 'write', side_effect=partial_then_full):
            with self.assertRaises(course.CourseError): self.declare(request)
        self.assertEqual(Path(self.log()).read_bytes(), before)
        actual_sync = os.fsync
        failed = [False]
        def fail_once(fd):
            stat = os.fstat(fd)
            if not failed[0] and stat.st_ino == os.stat(self.log()).st_ino and stat.st_size > len(before):
                failed[0] = True
                raise OSError('synthetic fsync failure')
            return actual_sync(fd)
        with mock.patch.object(evidence.os, 'fsync', side_effect=fail_once):
            with self.assertRaises(course.CourseError): self.declare(request)
        self.assertEqual(Path(self.log()).read_bytes(), before)
        self.assertTrue(failed[0])
        with open(self.log(), 'ab') as fh: fh.write(b'{"event_type":"reading_declared","torn":')
        self.assertEqual(self.state(request)['state'], 'unsupported')
        first = self.declare(request)
        self.assertEqual(self.state(request)['event_ids'], [first['event_id']])
        tails = list(Path(self.log()).parent.glob('*.torn-*'))
        self.assertEqual(len(tails), 1)
        self.assertTrue(tails[0].read_bytes().endswith(b'"torn":'))
        self.assertEqual(self.declare(request)['event_id'], first['event_id'])

    def test_crash_after_durable_append_before_receipt(self):
        request = self.confirmation()
        program = '''import json,os,sys,evidence
from surfaces import course_ops
original=evidence._durable_evidence_line
def crash(fd,path,raw):
    original(fd,path,raw)
    os._exit(71)
evidence._durable_evidence_line=crash
course_ops.run(sys.argv[1],'declare_reading',json.loads(sys.argv[2]))
'''
        proc = subprocess.run([sys.executable, '-c', program, self.root, json.dumps(dict(request,course_id='synthetic'))],cwd=ROOT)
        self.assertEqual(proc.returncode,71)
        event = list(evidence.live_events(self.log()))[0]
        replay = self.declare(request)
        self.assertEqual(replay['status'],'already_recorded')
        self.assertEqual(replay['event'],event)

    def test_first_write_locks_and_missing_provenance(self):
        request = self.confirmation()
        original = course.validate_reading_source
        def validate(base, source_ref):
            with mock.patch.object(journal, 'LOCK_TIMEOUT_SECONDS', 0):
                with self.assertRaises(journal.JournalError) as caught:
                    journal.op_grant_rights(self.base, self.source_id, {'read':'denied'}, self.source_fp, 'human','test')
                self.assertEqual(caught.exception.code,'journal.busy')
            original(base,source_ref)
        with mock.patch.object(course,'validate_reading_source',side_effect=validate): self.declare(request)
        journal_path = Path(journal.log_path(self.base))
        saved = journal_path.read_bytes()
        journal_path.write_bytes(b'')
        with self.assertRaises(course.CourseError): self.declare(request)
        journal_path.write_bytes(saved)
        Path(self.log()).write_text('{"schema_version":99,"event_type":"reading_declared"}\n')
        self.assertEqual(self.state(request)['state'],'unsupported')
        with self.assertRaises(course.CourseError): self.declare(request)

    def test_missing_history_does_not_recreate_completion(self):
        occurrence = self.create()['occurrence']
        request = self.confirmation(occurrence)
        self.declare(request)
        Path(self.log()).unlink()
        self.assertEqual(self.state(request)['state'], 'unavailable')
        with self.assertRaises(course.CourseError): self.declare(request)
        with self.assertRaises(course.CourseError): self.confirmation(occurrence)
        self.assertFalse(Path(self.log()).exists())

    def test_lost_confirmation_requires_fresh_explicit_action(self):
        occurrence = self.create()['occurrence']
        request = self.confirmation(occurrence)
        first = self.declare(request)
        path = Path(journal.log_path(self.base))
        lines = path.read_text().splitlines(True)
        path.write_text(''.join(line for line in lines if
                               (json.loads(line).get('agent') or {}).get('operation_id') != request['intent_id']))
        with self.assertRaises(course.CourseError): self.declare(request)
        fresh = self.confirmation(occurrence)
        self.assertNotEqual(fresh['intent_id'], request['intent_id'])
        self.assertEqual(self.declare(fresh)['event_id'], first['event_id'])

    def test_retracted_payload_stays_immutable(self):
        request = self.confirmation()
        event = self.declare(request)['event']
        correction = evidence.retraction_event(event['event_id'], 'Correction')
        evidence.append_event(self.log(), correction)
        changed = copy.deepcopy(event)
        changed.update(event_id=evidence.new_event_id(), intent_id='e'*16,
                       base_retraction_id=correction['event_id'])
        changed['source_ref']['locator'] = 'different source range'
        with self.assertRaisesRegex(ValueError, 'integrity conflict'):
            evidence.append_event(self.log(), changed, precommit=lambda:None)

    def test_crash_mid_line_and_replay_sync_failure(self):
        request = self.confirmation()
        program = '''import json,os,sys,evidence
from surfaces import course_ops
def crash(fd,path,raw):
    os.write(fd,raw[:31])
    os._exit(72)
evidence._durable_evidence_line=crash
course_ops.run(sys.argv[1],'declare_reading',json.loads(sys.argv[2]))
'''
        proc = subprocess.run([sys.executable,'-c',program,self.root,json.dumps(dict(request,course_id='synthetic'))],cwd=ROOT)
        self.assertEqual(proc.returncode,72)
        self.assertEqual(self.state(request)['state'],'unsupported')
        first = self.declare(request)
        before = Path(self.log()).read_bytes()
        with mock.patch.object(evidence.os,'fsync',side_effect=OSError('failed replay sync')):
            with self.assertRaises(course.CourseError): self.declare(request)
        self.assertEqual(Path(self.log()).read_bytes(),before)
        self.assertEqual(self.declare(request)['event_id'],first['event_id'])

    def test_http_confirm_cli_declare_and_replay(self):
        occurrence = self.create()['occurrence']
        proc, url, _ = start_daemon(self.root)
        self.addCleanup(proc.wait)
        self.addCleanup(proc.terminate)
        request = dict(course_id='synthetic',expected_fingerprint=self.read()['fingerprint'],
                       occurrence_id=occurrence['occurrence_id'],revision_id=occurrence['revision_id'])
        status, receipt = json_request(url+'api/course/confirm-reading',dict(request,confirmation='read'))
        self.assertEqual(status,200,receipt)
        cmd = [sys.executable,str(ROOT/'itembank.py'),'course','declare-reading','synthetic',
               '--root',self.root,'--expect',request['expected_fingerprint'],
               '--occurrence-id',request['occurrence_id'],'--revision-id',request['revision_id'],
               '--intent-id',receipt['intent_id']]
        reply = subprocess.run(cmd,capture_output=True,text=True)
        self.assertEqual(reply.returncode,0,reply.stderr)
        self.assertIn('recorded',reply.stdout)
        status, replay = json_request(url+'api/course/declare-reading',dict(request,intent_id=receipt['intent_id']))
        self.assertEqual(status,200,replay)
        self.assertEqual(replay['status'],'already_recorded')
        status, bad = json_request(url+'api/course/confirm-reading',dict(request,confirmation='read',source_path='/tmp/ignored'))
        self.assertNotEqual(status,200,bad)


if __name__ == '__main__':
    unittest.main()
