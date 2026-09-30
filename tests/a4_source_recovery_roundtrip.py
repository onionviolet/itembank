#!/usr/bin/env python3
"""Explicit local context, exact note return and fail-closed restore checks."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import course
import course_package
import identity
import journal
import notes
import source_adapters


def snapshot(root):
    return {str(path.relative_to(root)): path.read_bytes()
            for path in Path(root).rglob('*') if path.is_file()}


class SourceRecovery(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='a4-source-recovery-')
        self.addCleanup(self.tmp.cleanup)
        self.base = str(Path(self.tmp.name, 'course'))
        Path(self.base).mkdir()
        self.cid = course.create_course(self.base, 'Synthetic research', 'human', 'test')['object_id']
        self.private = str(Path(self.tmp.name, 'private-notes'))
        self.scope_root = str(Path(self.tmp.name, 'scope'))
        self.citation = self.source('duplicate.md', 'First context\nSame sentence.\nSecond context\nSame sentence.\n', 'L4')

    def source(self, name, text, locator='L1'):
        Path(self.base, name).write_text(text, encoding='utf-8')
        rights = {operation: 'granted' for operation in identity.RIGHTS_OPERATIONS}
        raw = journal.op_link(self.base, 'source', name, 'human', 'test', rights=rights)
        result = source_adapters.import_source(self.base, 'markdown', raw['object_id'], 'human', 'test')
        self.assertEqual(result['status'], 'ok')
        sidecar = json.loads(Path(self.base, result['sidecar_rel_path']).read_text())
        return {'source_id': result['source_id'], 'locator_id': locator, 'fingerprint': sidecar['fingerprint']}

    def transfer(self, mode='copy', confirm=True, expected=None):
        return notes.transfer_source_note(self.base, self.private, self.cid, self.citation,
                                          mode, expected, confirm=confirm)

    def test_scope_restart_and_new_inventory_do_not_include_excluded_content(self):
        copied = self.transfer()
        note = copied['note']
        saved = source_adapters.write_context_scope(
            self.scope_root, self.cid, [self.citation], [note['note_id']],
            copied['document']['fingerprint'], None, self.base, self.private, confirm=True)
        self.source('excluded.md', 'EXCLUDED SECRET\n')
        restarted = source_adapters.read_context_scope(self.scope_root, self.cid)
        self.assertEqual(restarted, saved)
        with mock.patch('urllib.request.urlopen', side_effect=AssertionError('no provider calls')):
            context = source_adapters.resolve_context_scope(self.base, restarted['scope'], self.private)
        self.assertEqual(context['status'], 'ok')
        self.assertNotIn('EXCLUDED SECRET', json.dumps(context))
        self.assertEqual(context['sources'][0]['origin']['line'], 4)
        self.assertEqual(context['notes'][0]['kind'], 'learner_note')
        self.assertEqual(context['egress'], 'none')
        journal.op_grant_rights(self.base, self.citation['source_id'], {'transform': 'unknown'},
                                self.citation['fingerprint'], 'human', 'test')
        refused = source_adapters.resolve_context_scope(self.base, restarted['scope'], self.private)
        self.assertEqual(refused['status'], 'conflict')
        self.assertEqual(refused['sources'], [])
        self.assertEqual(refused['notes'], [])
        with self.assertRaises(ValueError):
            source_adapters.write_context_scope(self.scope_root, self.cid, [], [], None,
                                                None, self.base, confirm=True)

    def test_link_copy_exact_return_edit_and_stale_refusal(self):
        linked = self.transfer('link')
        self.assertNotIn('Same sentence.', Path(self.private, 'notes.md').read_text())
        copied = self.transfer(expected=linked['document']['fingerprint'])
        self.assertNotEqual(linked['note']['note_id'], copied['note']['note_id'])
        document = notes.read_note_document(self.private, self.cid)
        document['sidecar']['notes'][1]['learner_wording'] += ' My private comment.'
        notes.write_note_document(self.private, self.cid, document['markdown'] + '\nMy private comment.\n',
                                  document['sidecar'], document['fingerprint'])
        restarted = notes.read_note_document(self.private, self.cid)
        returned = notes.resolve_source_note(self.base, restarted['sidecar']['notes'][1])
        self.assertEqual(returned[0]['origin']['line'], 4)
        self.assertIn('My private comment.', restarted['sidecar']['notes'][1]['learner_wording'])
        row = journal.read_registry(self.base)[self.citation['source_id']]
        Path(self.base, row['path']).write_text('Changed source\n')
        before = snapshot(self.private)
        self.assertEqual(notes.resolve_source_note(self.base, copied['note'])[0]['status'], 'stale')
        with self.assertRaises(ValueError):
            self.transfer(expected=restarted['fingerprint'])
        self.assertEqual(snapshot(self.private), before)
        self.assertIn('Same sentence.', restarted['markdown'])

    def test_cancel_denied_unknown_and_undo(self):
        self.assertEqual(self.transfer(confirm=False)['status'], 'canceled')
        self.assertFalse(Path(self.private).exists())
        for state in ('denied', 'unknown'):
            journal.op_grant_rights(self.base, self.citation['source_id'], {'quote': state},
                                    self.citation['fingerprint'], 'human', 'test')
            with self.assertRaises(ValueError):
                self.transfer()
            self.assertFalse(Path(self.private).exists())
        linked = self.transfer('link')
        prior = notes.read_note_document(self.private, self.cid)
        journal.op_grant_rights(self.base, self.citation['source_id'], {'quote': 'granted'},
                                self.citation['fingerprint'], 'human', 'test')
        self.transfer(expected=linked['document']['fingerprint'])
        applied = [entry for entry in journal.entries(self.private) if entry['state'] == 'applied'][-1]
        journal.undo(self.private, applied['entry_id'], 'human', 'test')
        self.assertEqual(notes.read_note_document(self.private, self.cid), prior)

    def test_changed_notes_refuse_all_context_and_cancel_scope_writes_nothing(self):
        copied = self.transfer()
        source_adapters.write_context_scope(self.scope_root, self.cid, [self.citation],
            [copied['note']['note_id']], copied['document']['fingerprint'], None,
            self.base, self.private, confirm=True)
        scope = source_adapters.read_context_scope(self.scope_root, self.cid)['scope']
        doc = notes.read_note_document(self.private, self.cid)
        doc['sidecar']['notes'][0]['learner_wording'] += ' Edited'
        notes.write_note_document(self.private, self.cid, doc['markdown'] + 'Edited\n',
                                  doc['sidecar'], doc['fingerprint'])
        context = source_adapters.resolve_context_scope(self.base, scope, self.private)
        self.assertEqual(context['status'], 'conflict')
        self.assertEqual(context['sources'], [])
        self.assertEqual(context['notes'], [])
        before = snapshot(self.scope_root)
        source_adapters.write_context_scope(self.scope_root, self.cid, [], [], None,
                                            None, self.base, confirm=False)
        self.assertEqual(snapshot(self.scope_root), before)

    def test_native_extraction_measurement_preserves_tables_and_failed_original(self):
        raw = b'# Formula\n\nE = mc^2\n\n| x | y |\n|---|---|\n| 1 | 2 |\n'
        Path(self.base, 'table.md').write_bytes(raw)
        rid = journal.op_link(self.base, 'source', 'table.md', 'human', 'test',
                              rights={operation: 'granted' for operation in identity.RIGHTS_OPERATIONS})['object_id']
        preview = source_adapters.preview_source(self.base, 'markdown', rid)
        self.assertEqual(preview['status'], 'ok')
        self.assertEqual(preview['preview']['markdown'].encode(), raw)
        self.assertEqual(preview['preview']['sidecar']['unsupported'], [])
        self.assertTrue(all(locator['span_id'] for locator in preview['preview']['sidecar']['locators']))
        self.assertEqual(Path(self.base, 'table.md').read_bytes(), raw)
        Path(self.base, 'invalid.md').write_bytes(b'\xff\xfe')
        invalid = journal.op_link(self.base, 'source', 'invalid.md', 'human', 'test')['object_id']
        before = snapshot(self.base)
        self.assertEqual(source_adapters.preview_source(self.base, 'markdown', invalid)['status'], 'unsupported')
        self.assertEqual(snapshot(self.base), before)

    def test_ordinary_restore_rechecks_bytes_before_skipping_same_fingerprint(self):
        package = str(Path(self.tmp.name, 'package'))
        destination = str(Path(self.tmp.name, 'restored'))
        Path(destination).mkdir()
        course_package.export_package(self.base, self.base, package)
        result = course_package.restore_package(package, destination, 'human', 'test')
        self.assertTrue(result['complete'])
        sidecar = Path(destination, course.COURSE_SIDECAR_FILENAME)
        sidecar.write_bytes(sidecar.read_bytes() + b' ')
        before = snapshot(destination)
        with self.assertRaises(course_package.PackageError) as raised:
            course_package.restore_package(package, destination, 'human', 'test')
        self.assertEqual(raised.exception.code, 'package.object_conflict')
        self.assertEqual(snapshot(destination), before)

    def test_later_destination_conflict_prevents_earlier_course_write(self):
        lesson_id = identity.new_object_id()
        journal.commit_operation(self.base, lesson_id, 'lesson', 'later-lesson.md', 'mint',
                                 b'# Synthetic lesson\n\nReadable offline.\n', None,
                                 'human', 'test', create_if_missing=True)
        journal.op_grant_rights(self.base, lesson_id, {'package': 'granted'},
                                journal.read_registry(self.base)[lesson_id]['fingerprint'], 'human', 'test')
        package = str(Path(self.tmp.name, 'conflict-package'))
        manifest = course_package.export_package(self.base, self.base, package)
        self.assertTrue(any(row['object_id'] == lesson_id for row in manifest['entries']))
        destination = Path(self.tmp.name, 'conflicting-destination')
        destination.mkdir()
        (destination / 'later-lesson.md').write_text('Existing unrelated draft\n')
        before = snapshot(destination)
        with self.assertRaises(course_package.PackageError) as raised:
            course_package.restore_package(package, str(destination), 'human', 'test')
        self.assertEqual(raised.exception.code, 'package.object_conflict')
        self.assertEqual(snapshot(destination), before)


if __name__ == '__main__':
    unittest.main()
