#!/usr/bin/env python3
"""Synthetic whole-root restore fault, crash and no-replace publication gates."""
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
    return {str(path.relative_to(root)): path.read_bytes()
            for path in Path(root).rglob('*') if path.is_file()}


class OrdinaryRestoreAtomicity(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='ordinary-restore-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        domain = corpus_14b.build_three_domains(str(self.root))['domains'][0]
        self.source = domain['root']
        corpus_14b.packaged_source(self.source, 'carried-source')
        corpus_14b.seed_objective_evidence(self.source, domain['objectives'][0])
        self.package = str(self.root / 'package')
        self.manifest = course_package.export_package(self.source, self.source, self.package)
        self.assertNotIn('reading_transport_fingerprint', self.manifest)
        self.dest = self.root / 'destination'

    def restore(self):
        return course_package.restore_package(self.package, str(self.dest), 'human', 'test')

    def test_missing_parent_is_named_and_creates_nothing(self):
        self.dest = self.root / 'absent-parent' / 'destination'
        with self.assertRaises(course_package.PackageError) as error:
            self.restore()
        self.assertEqual(error.exception.code, 'package.destination_unavailable')
        self.assertFalse(self.dest.parent.exists())

    def test_already_private_stage_defers_publication_to_course_owner(self):
        with course_package.private_stage(str(self.root)) as stage:
            with mock.patch.object(course_package, 'publish_directory') as publish:
                result = course_package.restore_package(self.package, stage, 'human', 'test',
                                                        _staging=True)
            self.assertTrue(result['complete'])
            self.assertTrue(journal.read_registry(stage))
            publish.assert_not_called()

    def assert_complete(self):
        registry = journal.read_registry(str(self.dest))
        for entry in self.manifest['entries']:
            self.assertEqual(registry[entry['object_id']]['fingerprint'], entry['fingerprint'])
            self.assertEqual(identity.object_fingerprint(
                (self.dest / entry['relpath']).read_bytes(), entry['kind']), entry['fingerprint'])
            self.assertEqual(journal.object_state(str(self.dest), entry['object_id']), 'clean')
        self.assertEqual(len(evidence._reading_history(evidence.log_path(str(self.dest)))), 1)

    def test_absent_and_empty_roots_publish_only_complete_journal_and_evidence(self):
        publish = course_package.publish_directory
        for existed in (False, True):
            with self.subTest(existed=existed):
                self.dest = self.root / ('empty' if existed else 'absent')
                if existed:
                    self.dest.mkdir()
                def observe(parent, stage, destination):
                    self.assertFalse(Path(destination).exists())
                    self.assertEqual(len(journal.read_registry(stage)), len(self.manifest['entries']))
                    self.assertEqual(len(evidence._reading_history(evidence.log_path(stage))), 1)
                    return publish(parent, stage, destination)
                with mock.patch.object(course_package, 'publish_directory', side_effect=observe):
                    self.assertTrue(self.restore()['complete'])
                self.assert_complete()

    def test_second_object_failure_leaves_empty_destination_and_no_stage(self):
        self.dest.mkdir()
        commit = journal.commit_operation
        calls = 0
        def fail_later(*args, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError('synthetic disk full')
            return commit(*args, **kwargs)
        with mock.patch.object(journal, 'commit_operation', side_effect=fail_later):
            with self.assertRaises(OSError):
                self.restore()
        self.assertEqual(list(self.dest.iterdir()), [])
        self.assertEqual(list(self.root.glob('.package-stage-*')), [])
        self.assertTrue(self.restore()['complete'])

    def test_evidence_failure_after_objects_never_publishes(self):
        restore = course_package._restore_evidence
        def fail_after_objects(events, dest, course_id=None):
            if journal.read_registry(dest):
                raise OSError('synthetic evidence failure')
            return restore(events, dest, course_id)
        with mock.patch.object(course_package, '_restore_evidence', side_effect=fail_after_objects):
            with self.assertRaises(OSError):
                self.restore()
        self.assertFalse(self.dest.exists())
        self.assertEqual(list(self.root.glob('.package-stage-*')), [])

    def test_publication_failure_and_cancel_restore_empty_root(self):
        self.dest.mkdir()
        for error in (OSError('synthetic rename failure'), KeyboardInterrupt()):
            with mock.patch.object(course_package, 'publish_directory', side_effect=error):
                with self.assertRaises(type(error)):
                    self.restore()
            self.assertTrue(self.dest.is_dir())
            self.assertEqual(list(self.dest.iterdir()), [])
            self.assertEqual(list(self.root.glob('.package-stage-*')), [])

    def test_raced_destination_before_publish_is_preserved(self):
        publish = course_package.publish_directory
        def race(parent, stage, destination):
            Path(destination).mkdir()
            Path(destination, 'racer.txt').write_bytes(b'Raced private draft')
            return publish(parent, stage, destination)
        with mock.patch.object(course_package, 'publish_directory', side_effect=race):
            with self.assertRaises(course_package.PackageError) as error:
                self.restore()
        self.assertEqual(error.exception.code, 'package.destination_exists')
        self.assertEqual(files(self.dest), {'racer.txt': b'Raced private draft'})

    def test_raced_write_before_empty_removal_is_preserved(self):
        self.dest.mkdir()
        restore = course_package._restore_ordinary_package
        def race(*args):
            result = restore(*args)
            (self.dest / 'racer.txt').write_bytes(b'Raced private draft')
            return result
        with mock.patch.object(course_package, '_restore_ordinary_package', side_effect=race):
            with self.assertRaises(OSError):
                self.restore()
        self.assertEqual(files(self.dest), {'racer.txt': b'Raced private draft'})

    def test_process_crash_during_staging_preserves_absent_and_empty_roots(self):
        for existed in (False, True):
            with self.subTest(existed=existed):
                self.dest = self.root / ('crash-empty' if existed else 'crash-absent')
                if existed:
                    self.dest.mkdir()
                child = subprocess.run([sys.executable, __file__, '--crash', 'staging',
                                        self.package, str(self.dest)], capture_output=True)
                self.assertEqual(child.returncode, 71, child.stderr.decode())
                self.assertEqual(self.dest.exists(), existed)
                self.assertEqual(files(self.dest), {})
                self.assertTrue(self.restore()['complete'])
                self.assert_complete()

    def test_process_crash_after_publish_leaves_complete_retryable_root(self):
        child = subprocess.run([sys.executable, __file__, '--crash', 'published',
                                self.package, str(self.dest)], capture_output=True)
        self.assertEqual(child.returncode, 71, child.stderr.decode())
        self.assert_complete()
        before = files(self.dest)
        result = self.restore()
        self.assertEqual(result['evidence_already_recorded'], 1)
        self.assertEqual(files(self.dest), before)

    def test_populated_root_merge_and_conflict_behavior_is_retained(self):
        self.dest.mkdir()
        (self.dest / 'private.txt').write_bytes(b'Unrelated draft')
        before = files(self.dest)
        with self.assertRaises(course_package.PackageError) as error:
            course_package.restore_package(self.package, str(self.dest), 'human', 'test',
                                           require_root_atomic=True)
        self.assertEqual(error.exception.code, 'package.atomic_merge_unsupported')
        self.assertEqual(files(self.dest), before)
        with mock.patch.object(course_package, 'publish_directory', side_effect=AssertionError('no replacement')):
            result = self.restore()
            self.assertTrue(result['complete'])
            self.assertEqual(result['publication'], 'per-object')
        self.assertEqual((self.dest / 'private.txt').read_bytes(), b'Unrelated draft')
        entry = self.manifest['entries'][-1]
        (self.dest / entry['relpath']).write_bytes(b'Changed outside journal')
        before = files(self.dest)
        with self.assertRaises(course_package.PackageError) as error:
            self.restore()
        self.assertEqual(error.exception.code, 'package.object_conflict')
        self.assertEqual(files(self.dest), before)

    def test_destination_symlink_is_refused_without_touching_target(self):
        outside = self.root / 'outside'
        outside.mkdir()
        self.dest.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(course_package.PackageError) as error:
            self.restore()
        self.assertEqual(error.exception.code, 'package.destination_exists')
        self.assertEqual(list(outside.iterdir()), [])


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--crash':
        _flag, phase, package, dest = sys.argv[1:]
        if phase == 'staging':
            original = journal.commit_operation
            def crash(*args, **kwargs):
                original(*args, **kwargs)
                os._exit(71)
            journal.commit_operation = crash
        else:
            original = course_package.publish_directory
            def crash(*args):
                original(*args)
                os._exit(71)
            course_package.publish_directory = crash
        course_package.restore_package(package, dest, 'human', 'test')
        sys.exit(2)
    unittest.main()
