#!/usr/bin/env python3
"""Supported reading desk and pairwise private note persistence on synthetic data."""
import copy
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
import evidence
import graph
import journal
import notes
import reading_desk
from surfaces import course_ops, reading_desk as desk
import reading_declarations_roundtrip as declarations
from daemon_roundtrip import start_daemon, json_request


class ReadingDesk(unittest.TestCase):
    setUp = declarations.ReadingDeclarations.setUp
    run_op = declarations.ReadingDeclarations.run_op
    read = declarations.ReadingDeclarations.read
    bind = declarations.ReadingDeclarations.bind
    values = declarations.ReadingDeclarations.values
    create = declarations.ReadingDeclarations.create
    confirmation = declarations.ReadingDeclarations.confirmation
    declare = declarations.ReadingDeclarations.declare

    def context(self, row):
        return dict(expected_fingerprint=self.read()['fingerprint'],
                    occurrence_id=row['occurrence_id'], revision_id=row['revision_id'])

    def view(self, row):
        return self.run_op('reading_view', **self.context(row))

    def save(self, row, wording='My private wording', note_id='a'*32, fingerprint=None):
        return self.run_op('save_reading_note', **self.context(row), wording=wording,
                           note_id=note_id, notes_fingerprint=fingerprint)

    def test_separate_completion_shared_note_restart_retraction(self):
        a=self.create()['occurrence']; b=self.create()['occurrence']
        request=self.confirmation(a); event=self.declare(request)
        self.save(a)
        for row in (a,b):
            self.assertEqual(self.view(row)['notes'][0]['learner_wording'], 'My private wording')
        self.assertEqual(self.view(a)['reading_state']['state'], 'reported-read')
        self.assertEqual(self.view(b)['reading_state']['state'], 'not-reported')
        args=[sys.executable, 'itembank.py','course','reading-view','synthetic','--root',self.root,
              '--expect',self.read()['fingerprint'],'--occurrence-id',a['occurrence_id'],
              '--revision-id',a['revision_id'],'--json']
        run=subprocess.run(args,cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(run.returncode,0,run.stderr)
        self.assertEqual(json.loads(run.stdout)['notes'][0]['note_id'],'a'*32)
        evidence.append_event(evidence.log_path(self.base),evidence.retraction_event(event['event_id'],'Correction'))
        self.assertEqual(self.view(a)['reading_state']['state'],'not-reported')
        self.assertTrue(self.declare(request)['retracted'])
        Path(evidence.log_path(self.base)).unlink()
        self.assertEqual(self.view(a)['reading_state']['state'],'unavailable')

    def test_note_fault_rollback_and_recovery(self):
        row=self.create()['occurrence']; self.save(row)
        root=reading_desk.note_root(self.base)
        old=notes.read_note_document(root)
        setter=journal._set_file
        def fail_markdown(path,raw):
            if path.endswith('notes.md') and raw != old['markdown'].encode():
                raise OSError('sample disk full')
            return setter(path,raw)
        with mock.patch.object(journal,'_set_file',side_effect=fail_markdown):
            with self.assertRaises(course.CourseError):
                self.save(row,'Keep this unsaved wording','b'*32,old['fingerprint'])
        self.assertEqual(notes.read_note_document(root),old)
        self.assertEqual(self.save(row,'Keep this unsaved wording','b'*32,old['fingerprint'])['status'],'saved')
        accepted=notes.read_note_document(root)
        def crash_markdown(path,raw):
            if path.endswith('notes.md'): raise SystemExit('simulated interruption')
            return setter(path,raw)
        with mock.patch.object(journal,'_set_file',side_effect=crash_markdown):
            with self.assertRaises(SystemExit):
                self.save(row,'Interrupted wording','c'*32,accepted['fingerprint'])
        with self.assertRaises(journal.JournalError): notes.read_note_document(root)
        self.assertIn('recovery',self.view(row)['note_error'])
        report=journal.replay(root)
        entry=report['mixed'][0]
        journal.undo(root,entry['entry_id'],'human','test')
        self.assertEqual(notes.read_note_document(root)['sidecar'],accepted['sidecar'])

    def test_missing_moved_removed_anchor_and_privacy(self):
        row=self.create()['occurrence'];self.save(row)
        original=self.view(row)['notes'][0]
        journal.op_move(self.base,self.source_id,'moved.md',self.source_fp,'human','test')
        self.assertEqual(self.view(row)['notes'][0],original)
        Path(self.base,'moved.md').unlink()
        view=self.view(row)
        self.assertIsNone(view['content'])
        self.assertIn('unavailable',view['notes'][0]['anchor_state'])
        self.assertEqual(view['notes'][0]['learner_wording'],original['learner_wording'])
        doc=copy.deepcopy(self.read()['doc'])
        # Removal is a journaled graph change, not deletion from the private notes.
        doc['reading_occurrences']=[]
        doc['reading_placement']=[]
        course.write_course(self.base,doc,self.read()['fingerprint'],'human','test')
        view=self.view(row)
        self.assertIsNone(view['occurrence'])
        self.assertEqual(view['notes'][0]['note_id'],original['note_id'])
        self.assertNotIn('My private wording',Path(course.sidecar_path(self.base)).read_text())
        self.assertNotIn('My private wording',json.dumps(list(journal.entries(self.base))))
        self.assertNotIn('My private wording',json.dumps(list(journal.entries(reading_desk.note_root(self.base)))))

    def test_stale_rights_changed_bytes_and_note_cas(self):
        row=self.create()['occurrence']; self.save(row)
        self.assertEqual(self.save(row)['status'],'saved')
        with self.assertRaises(course.CourseError):self.save(row,'Another','b'*32)
        journal.op_grant_rights(self.base,self.source_id,{'read':'denied'},self.source_fp,'human','test')
        self.assertIsNone(self.view(row)['content'])
        with self.assertRaises(course.CourseError):self.save(row,'Another','b'*32)
        journal.op_grant_rights(self.base,self.source_id,{'read':'granted'},self.source_fp,'human','test')
        Path(self.base,journal._compute_registry(self.base)[self.source_id]['path']).write_text('Different bytes')
        self.assertIsNone(self.view(row)['content'])
        with self.assertRaises(course.CourseError):self.save(row,'Another','b'*32)

    def test_stale_revision_and_placement_preserve_private_note(self):
        row = self.create()['occurrence']
        self.save(row)
        declared = self.declare(self.confirmation(row))
        self.run_op('place_reading', **self.context(row), title='Renamed reading', activation='Library')
        self.assertEqual(self.view(row)['reading_state']['event_ids'], [declared['event_id']])
        self.assertEqual(self.view(row)['placements'][row['occurrence_id']]['title'], 'Renamed reading')
        revised = self.run_op('revise_reading', **self.context(row), changes={'purpose':'A new demand'})['occurrence']
        self.assertIsNone(self.view(row)['content'])
        self.assertEqual(self.view(revised)['reading_state']['state'], 'not-reported')
        self.assertEqual(self.view(revised)['notes'][0]['note_id'], 'a'*32)
        with self.assertRaises(course.CourseError):
            self.save(row, 'Stale draft', 'b'*32)

    def test_pair_tamper_and_symlink_refuse_without_losing_words(self):
        row = self.create()['occurrence']
        self.save(row)
        root = Path(reading_desk.note_root(self.base))
        md = root / 'notes.md'
        original = md.read_bytes()
        md.write_bytes(original + b' ')
        with self.assertRaises(journal.JournalError): notes.read_note_document(root)
        md.write_bytes(original)
        outside = Path(self.root, 'outside.md')
        outside.write_text('Unrelated private file')
        md.unlink()
        md.symlink_to(outside)
        with self.assertRaises(journal.JournalError): notes.read_note_document(root)
        self.assertIsNotNone(self.view(row)['note_error'])
        md.unlink()
        md.write_bytes(original)
        self.assertEqual(notes.read_note_document(root)['sidecar']['notes'][0]['learner_wording'], 'My private wording')
        md.unlink()
        (root / 'notes.md.json').unlink()
        with self.assertRaises(journal.JournalError): notes.read_note_document(root)
        with self.assertRaises(course.CourseError): self.save(row, 'Do not recreate missing history', 'b'*32)


    def test_live_http_route_and_note(self):
        row=self.create()['occurrence']
        proc,url,_ = start_daemon(self.root)
        self.addCleanup(proc.wait, timeout=10)
        self.addCleanup(proc.terminate)
        import urllib.request
        page=urllib.request.urlopen(url+desk.href('synthetic',row)).read().decode()
        self.assertIn('First synthetic paragraph.',page)
        self.assertNotIn('Second paragraph.',page)
        self.assertIn('A note to yourself',page)
        body=dict(course_id='synthetic',**self.context(row),note_id='f'*32,
                  wording='HTTP learner wording',notes_fingerprint=None)
        status,payload=json_request(url+'/api/course/save-reading-note',body)
        self.assertEqual(status,200,payload)
        status,_=json_request(url+'/api/course/save-reading-note',body,headers={'Origin':'https://example.invalid'})
        self.assertEqual(status,403)
        self.assertEqual(self.view(row)['notes'][0]['learner_wording'],'HTTP learner wording')
        view = self.view(row)
        command = [sys.executable, 'itembank.py', 'course', 'save-reading-note', 'synthetic',
                   '--root', self.root, '--expect', self.read()['fingerprint'],
                   '--occurrence-id', row['occurrence_id'], '--revision-id', row['revision_id'],
                   '--note-id', 'e'*32, '--wording', 'CLI learner wording',
                   '--notes-fingerprint', view['notes_fingerprint'], '--json']
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'saved')



if __name__=='__main__':unittest.main()
