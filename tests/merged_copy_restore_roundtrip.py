#!/usr/bin/env python3
"""Synthetic offline merge-copy publication, conflicts and recovery."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import course_package
import evidence
import identity
import journal
from fixtures import corpus_14b


def files(root):
    return {str(p.relative_to(root)): p.read_bytes()
            for p in Path(root).rglob('*') if p.is_file()}


class MergedCopy(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='merged-copy-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        domain = corpus_14b.build_three_domains(str(self.root))['domains'][0]
        original = domain['root']
        corpus_14b.packaged_source(original, 'fictional-source')
        corpus_14b.seed_objective_evidence(original, domain['objectives'][0])
        self.package = self.root / 'package'
        self.manifest = course_package.export_package(original, original, str(self.package))
        self.source = self.root / 'existing'
        self.source.mkdir()
        (self.source / 'private.txt').write_bytes(b'Fictional private draft\n')
        (self.source / 'empty').mkdir()
        self.other_id = identity.new_object_id()
        journal.commit_operation(str(self.source), self.other_id, 'lesson', 'other.md',
                                 'mint', b'# Fictional unrelated lesson\n', None,
                                 'human', 'test', create_if_missing=True)
        journal.op_grant_rights(str(self.source), self.other_id,
                                {operation: 'granted' for operation in identity.RIGHTS_OPERATIONS},
                                journal.read_registry(str(self.source))[self.other_id]['fingerprint'],
                                'human', 'test')
        self.dest = self.root / 'union'
        self.revision = course_package.merge_source_fingerprint(str(self.source))

    def merge(self):
        return course_package.restore_merged_copy(str(self.package), str(self.source),
                                                 str(self.dest), 'human', 'test', self.revision)

    def test_union_preserves_original_and_reopens_offline_in_fresh_process(self):
        before = files(self.source)
        result = self.merge()
        self.assertEqual(result['publication'], 'whole-root-copy')
        self.assertTrue(result['complete'])
        self.assertEqual(files(self.source), before)
        for relative, raw in before.items():
            if relative not in (os.path.relpath(journal.log_path(str(self.source)), self.source),
                                os.path.relpath(journal.registry_path(str(self.source)), self.source)):
                self.assertEqual((self.dest / relative).read_bytes(), raw)
        self.assertTrue((self.dest / 'empty').is_dir())
        for entry in self.manifest['entries']:
            self.assertEqual(journal.object_state(str(self.dest), entry['object_id']), 'clean')
        self.assertEqual(journal.object_state(str(self.dest), self.other_id), 'clean')
        process = subprocess.run([sys.executable, __file__, '--reopen', str(self.package),
                                  str(self.dest)], capture_output=True, text=True, timeout=20)
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(process.stdout.strip(), 'unchanged')
        self.assertEqual(len(evidence._reading_history(evidence.log_path(str(self.dest)))), 1)

    def test_stale_expected_revision_and_outside_destination_refuse(self):
        (self.source / 'private.txt').write_bytes(b'Changed draft\n')
        with self.assertRaises(course_package.PackageError) as raised:
            self.merge()
        self.assertEqual(raised.exception.code, 'package.destination_changed')
        self.assertFalse(self.dest.exists())
        self.dest = self.source / 'nested'
        with self.assertRaises(course_package.PackageError):
            self.merge()
        self.assertFalse(self.dest.exists())

    def test_conflicting_package_path_and_diverged_acceptance_preserve_source(self):
        entry = self.manifest['entries'][0]
        target = self.source / entry['relpath']
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b'Other owner\n')
        self.revision = course_package.merge_source_fingerprint(str(self.source))
        before = files(self.source)
        with self.assertRaises(course_package.PackageError) as raised:
            self.merge()
        self.assertEqual(raised.exception.code, 'package.object_conflict')
        self.assertEqual(files(self.source), before)
        self.assertFalse(self.dest.exists())
        target.unlink()
        (self.source / 'other.md').write_bytes(b'External conflicting edit\n')
        self.revision = course_package.merge_source_fingerprint(str(self.source))
        with self.assertRaises(course_package.PackageError) as raised:
            self.merge()
        self.assertEqual(raised.exception.code, 'package.object_conflict')

    def test_observed_source_change_during_replay_refuses_publication(self):
        replay = course_package.restore_package
        def race(*args, **kwargs):
            result = replay(*args, **kwargs)
            (self.source / 'new.txt').write_bytes(b'Concurrent draft\n')
            return result
        with mock.patch.object(course_package, 'restore_package', side_effect=race):
            with self.assertRaises(course_package.PackageError) as raised:
                self.merge()
        self.assertEqual(raised.exception.code, 'package.destination_changed')
        self.assertFalse(self.dest.exists())
        self.assertEqual((self.source / 'new.txt').read_bytes(), b'Concurrent draft\n')

    def test_cancel_disk_failure_and_publication_race_leave_original_intact(self):
        before = files(self.source)
        for owner, name, failure in ((course_package, 'restore_package', SystemExit('cancel')),
                                     (course_package, '_write_bytes_atomic', OSError('disk full')),
                                     (course_package, 'publish_directory', OSError('publication denied'))):
            with mock.patch.object(owner, name, side_effect=failure):
                with self.assertRaises((SystemExit, OSError)):
                    self.merge()
            self.assertEqual(files(self.source), before)
            self.assertFalse(self.dest.exists())
        publish = course_package.publish_directory
        def race(*args):
            self.dest.mkdir()
            (self.dest / 'racer').write_bytes(b'Another writer\n')
            return publish(*args)
        with mock.patch.object(course_package, 'publish_directory', side_effect=race):
            with self.assertRaises(course_package.PackageError):
                self.merge()
        self.assertEqual((self.dest / 'racer').read_bytes(), b'Another writer\n')
        self.assertEqual(files(self.source), before)

    def test_symlink_and_nonregular_sources_are_refused(self):
        os.symlink(self.package, self.source / 'link')
        with self.assertRaises(course_package.PackageError) as raised:
            self.merge()
        self.assertEqual(raised.exception.code, 'package.symlink_payload')
        self.assertFalse(self.dest.exists())
        (self.source / 'link').unlink()
        if hasattr(os, 'mkfifo'):
            os.mkfifo(self.source / 'pipe')
            with self.assertRaises(course_package.PackageError):
                self.merge()

    def test_permissions_and_stable_identity_are_preserved(self):
        os.chmod(self.source / 'private.txt', 0o600)
        self.revision = course_package.merge_source_fingerprint(str(self.source))
        self.merge()
        self.assertEqual(os.stat(self.dest / 'private.txt').st_mode & 0o777, 0o600)
        self.assertEqual(journal.read_registry(str(self.dest))[self.other_id],
                         journal.read_registry(str(self.source))[self.other_id])

    def test_process_exit_before_and_after_publication_allows_exact_recovery(self):
        before = files(self.source)
        for boundary in ('before', 'after'):
            self.dest = self.root / ('exit-' + boundary)
            process = subprocess.run([sys.executable, __file__, '--exit', boundary,
                                      str(self.package), str(self.source), str(self.dest),
                                      self.revision], capture_output=True, text=True, timeout=20)
            self.assertEqual(process.returncode, 29, process.stderr)
            self.assertEqual(files(self.source), before)
            if boundary == 'before':
                self.assertFalse(self.dest.exists())
                self.merge()
            self.assertEqual((self.dest / 'private.txt').read_bytes(), b'Fictional private draft\n')
            for entry in self.manifest['entries']:
                self.assertEqual(journal.object_state(str(self.dest), entry['object_id']), 'clean')
            retry = course_package.restore_package(str(self.package), str(self.dest),
                                                  'human', 'test', require_root_atomic=True)
            self.assertEqual(retry['publication'], 'unchanged')

    def test_equal_normalized_fingerprint_cannot_hide_divergent_exact_bytes(self):
        course_package.restore_package(str(self.package), str(self.source), 'human', 'test')
        for object_id, row in journal.read_registry(str(self.source)).items():
            journal.op_grant_rights(str(self.source), object_id,
                                    {operation: 'granted' for operation in identity.RIGHTS_OPERATIONS},
                                    row['fingerprint'], 'human', 'test')
        entry = next(row for row in self.manifest['entries'] if row['kind'] == 'source')
        target = self.source / entry['relpath']
        original = target.read_bytes()
        changed = original.replace(b'\n', b'\r\n')
        self.assertNotEqual(original, changed)
        self.assertEqual(identity.object_fingerprint(changed, 'source'), entry['fingerprint'])
        target.write_bytes(changed)
        self.revision = course_package.merge_source_fingerprint(str(self.source))
        before = files(self.source)
        with self.assertRaises(course_package.PackageError) as raised:
            self.merge()
        self.assertEqual(raised.exception.code, 'package.object_conflict')
        self.assertEqual(files(self.source), before)
        self.assertFalse(self.dest.exists())

    def test_malformed_copied_evidence_refuses_without_repairing_original(self):
        log = Path(evidence.log_path(str(self.source)))
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_bytes(b'not a JSON event\n')
        self.revision = course_package.merge_source_fingerprint(str(self.source))
        before = files(self.source)
        with self.assertRaises(course_package.PackageError) as raised:
            self.merge()
        self.assertEqual(raised.exception.code, 'package.evidence_unreadable')
        self.assertEqual(files(self.source), before)
        self.assertFalse(self.dest.exists())

    def test_unknown_or_denied_export_rights_refuse_before_payload_copy(self):
        for state in ('unknown', 'denied'):
            row = journal.read_registry(str(self.source))[self.other_id]
            journal.op_grant_rights(str(self.source), self.other_id, {'export': state},
                                    row['fingerprint'], 'human', 'test')
            before = files(self.source)
            with mock.patch.object(course_package, '_read_relative', side_effect=AssertionError('Read restricted source bytes')):
                # Pin the already verified package separately, then guard the
                # source-tree read itself. No restricted payload is copied.
                with self.assertRaises(course_package.PackageError) as raised:
                    course_package.merge_source_fingerprint(str(self.source))
            self.assertEqual(raised.exception.code, 'package.rights_restricted')
            self.assertEqual(files(self.source), before)
            self.assertFalse(self.dest.exists())


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--exit':
        boundary, package, source, dest, revision = sys.argv[2:]
        publish = course_package.publish_directory
        def exit_at_publication(*args):
            if boundary == 'after':
                publish(*args)
            os._exit(29)
        course_package.publish_directory = exit_at_publication
        course_package.restore_merged_copy(package, source, dest, 'human', 'test', revision)
    elif len(sys.argv) > 1 and sys.argv[1] == '--reopen':
        result = course_package.restore_package(sys.argv[2], sys.argv[3], 'human', 'test',
                                               require_root_atomic=True)
        print(result['publication'])
    else:
        unittest.main()
