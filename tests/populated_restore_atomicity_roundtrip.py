#!/usr/bin/env python3
"""Fictional populated-root refusal, exact retry and writer-admission probes."""
import contextlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
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


class PopulatedRestore(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='populated-restore-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        domain = corpus_14b.build_three_domains(str(self.root))['domains'][0]
        self.source = domain['root']
        corpus_14b.packaged_source(self.source, 'fictional-source')
        corpus_14b.seed_objective_evidence(self.source, domain['objectives'][0])
        self.package = self.root / 'package'
        self.manifest = course_package.export_package(self.source, self.source, str(self.package))
        self.dest = self.root / 'populated'
        self.dest.mkdir()
        (self.dest / 'private.txt').write_bytes(b'Unrelated fictional draft\n')

    def restore(self, **options):
        return course_package.restore_package(str(self.package), str(self.dest),
                                              'human', 'fictional-test',
                                              require_root_atomic=True, **options)

    def refuse(self, code='package.atomic_merge_unsupported'):
        before = files(self.dest)
        with self.assertRaises(course_package.PackageError) as raised:
            self.restore()
        self.assertEqual(raised.exception.code, code)
        self.assertEqual(files(self.dest), before)
        return str(raised.exception)

    def sibling(self):
        destination = self.root / 'fresh-sibling'
        result = course_package.restore_package(str(self.package), str(destination),
                                              'human', 'fictional-test', require_root_atomic=True)
        self.assertTrue(result['complete'])
        self.assertEqual(result['publication'], 'whole-root')
        return destination

    def process(self, mode, *args):
        return subprocess.Popen([sys.executable, __file__, '--child', mode,
                                 *map(str, args)], stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

    def finish(self, child, code=0):
        out, err = child.communicate(timeout=10)
        self.assertEqual(child.returncode, code, err.decode())
        return out.decode().strip()

    def wait_ready(self, child, ready):
        deadline = time.monotonic() + 5
        while not ready.exists():
            if child.poll() is not None or time.monotonic() >= deadline:
                child.kill()
                self.fail('Fictional writer failed to reach the barrier: ' + self.finish(child))
            time.sleep(0.01)

    def test_refusal_precedes_all_mutation_and_preserves_unrelated_acceptance(self):
        journal.commit_operation(str(self.dest), identity.new_object_id(), 'lesson',
                                 'accepted.md', 'mint', b'# Fictional accepted lesson\n',
                                 None, 'human', 'test', create_if_missing=True)
        with contextlib.ExitStack() as stack:
            for owner, name in ((journal, 'commit_operation'), (evidence, 'append_event'),
                                (course_package, 'private_stage'),
                                (course_package, 'publish_directory'),
                                (course_package, '_write_bytes_atomic')):
                stack.enter_context(mock.patch.object(owner, name,
                    side_effect=AssertionError('Populated refusal attempted mutation')))
            message = self.refuse()
        self.assertIn('sibling directory', message)
        self.assertIn('review', message)

    def test_fresh_sibling_reopens_with_source_evidence_and_exact_retry(self):
        before = files(self.dest)
        sibling = self.sibling()
        self.assertEqual(files(self.dest), before)
        self.dest = sibling
        (sibling / 'unrelated.txt').write_bytes(b'Preserved after restore\n')
        accepted_before = files(sibling)
        result = self.restore()
        self.assertEqual(result['publication'], 'unchanged')
        self.assertEqual(result['evidence_recorded'], 0)
        self.assertEqual(result['evidence_already_recorded'], 1)
        self.assertEqual(files(sibling), accepted_before)
        for entry in self.manifest['entries']:
            self.assertEqual(journal.object_state(str(sibling), entry['object_id']), 'clean')
            self.assertEqual(identity.object_fingerprint(
                (sibling / entry['relpath']).read_bytes(), entry['kind']), entry['fingerprint'])
        child = self.process('retry', self.package, sibling)
        self.assertEqual(self.finish(child), 'unchanged')

    def test_missing_object_and_missing_evidence_refuse_instead_of_replay(self):
        self.dest = self.sibling()
        log = Path(evidence.log_path(str(self.dest)))
        log.unlink()
        self.refuse()
        self.assertFalse(log.exists())
        # Restore a partial closure through the existing owner-controlled
        # stage only. Public restore must never complete it in place.
        partial = course_package.package_snapshot(str(self.package))
        partial['manifest'] = dict(partial['manifest'], entries=partial['manifest']['entries'][:-1])
        self.dest = self.root / 'partial'
        self.dest.mkdir()
        course_package.restore_package(str(self.package), str(self.dest), 'human', 'test',
                                       _snapshot=partial, _staging=True)
        self.refuse()

    def test_same_id_divergent_bytes_and_path_owner_stay_conflicts(self):
        self.dest = self.sibling()
        entry = self.manifest['entries'][-1]
        (self.dest / entry['relpath']).write_bytes(b'Changed fictional source\n')
        self.refuse('package.object_conflict')
        self.dest = self.root / 'path-conflict'
        self.dest.mkdir()
        target = self.dest / entry['relpath']
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b'Other fictional owner\n')
        self.refuse('package.object_conflict')

    def test_divergent_immutable_evidence_is_not_rewritten(self):
        self.dest = self.sibling()
        log = Path(evidence.log_path(str(self.dest)))
        event = json.loads(log.read_text().splitlines()[0])
        event['score'] = not event['score']
        log.write_text(json.dumps(event) + '\n')
        self.refuse('package.evidence_identity_conflict')

    def test_stale_package_refuses_before_destination_work(self):
        entry = self.manifest['entries'][-1]
        payload = self.package / course_package.PAYLOAD_DIRNAME / (entry['object_id'] + '.md')
        payload.write_bytes(payload.read_bytes() + b'Corruption\n')
        self.refuse('package.fingerprint_mismatch')

    def test_cancellation_and_read_failure_leave_no_mutation_or_stage(self):
        before = files(self.dest)
        for fault in (KeyboardInterrupt(), OSError('Fictional read failure')):
            with mock.patch.object(course_package, '_ordinary_destination_preflight', side_effect=fault):
                with self.assertRaises(type(fault)):
                    self.restore()
            self.assertEqual(files(self.dest), before)
            self.assertEqual(list(self.root.glob('.package-stage-*')), [])

    def test_racing_destination_edit_is_preserved_and_detected(self):
        self.dest = self.sibling()
        preflight = course_package._ordinary_destination_preflight
        entry = self.manifest['entries'][-1]
        def edit(snapshot, destination):
            result = preflight(snapshot, destination)
            (self.dest / entry['relpath']).write_bytes(b'Live fictional edit\n')
            return result
        with mock.patch.object(course_package, '_ordinary_destination_preflight', side_effect=edit):
            with self.assertRaises(course_package.PackageError) as raised:
                self.restore()
        self.assertEqual(raised.exception.code, 'package.destination_changed')
        self.assertEqual((self.dest / entry['relpath']).read_bytes(), b'Live fictional edit\n')

    def test_write_failure_cannot_reach_populated_destination(self):
        with mock.patch.object(journal, '_write_bytes_atomic', side_effect=OSError('Fictional disk full')):
            self.refuse()
        # The recovery route must also preserve the existing root when its
        # private build fails. No sibling is published on injected failure.
        before = files(self.dest)
        with mock.patch.object(journal, 'commit_operation', side_effect=OSError('Fictional disk full')):
            with self.assertRaises(OSError):
                self.sibling()
        self.assertEqual(files(self.dest), before)
        self.assertFalse((self.root / 'fresh-sibling').exists())

    def test_racing_root_replacement_refuses_even_with_identical_bytes(self):
        self.dest = self.sibling()
        before = files(self.dest)
        retired = self.root / 'raced-retired'
        preflight = course_package._ordinary_destination_preflight
        def replace(snapshot, destination):
            result = preflight(snapshot, destination)
            os.rename(self.dest, retired)
            shutil.copytree(retired, self.dest)
            return result
        with mock.patch.object(course_package, '_ordinary_destination_preflight', side_effect=replace):
            with self.assertRaises(course_package.PackageError) as raised:
                self.restore()
        self.assertEqual(raised.exception.code, 'package.destination_changed')
        self.assertEqual(files(self.dest), before)
        self.assertEqual(files(retired), before)

    def test_process_crash_and_competing_restores_preserve_populated_root(self):
        before = files(self.dest)
        child = self.process('crash', self.package, self.dest)
        self.finish(child, 73)
        self.assertEqual(files(self.dest), before)
        children = [self.process('refuse', self.package, self.dest) for _ in range(2)]
        for child in children:
            self.assertEqual(self.finish(child), 'package.atomic_merge_unsupported')
        self.assertEqual(files(self.dest), before)
        self.assertEqual(list(self.root.glob('.package-stage-*')), [])

    def test_active_canonical_journal_writer_is_not_displaced(self):
        ready, release = self.root / 'ready', self.root / 'release'
        child = self.process('journal-writer', self.dest, ready, release)
        try:
            self.wait_ready(child, ready)
            self.refuse()
        finally:
            release.touch()
        self.finish(child)
        self.assertEqual((self.dest / 'live.md').read_bytes(), b'# Fictional live writer\n')
        self.assertTrue(any(row['path'] == 'live.md'
                            for row in journal.read_registry(str(self.dest)).values()))

    def test_directory_swap_probe_leaves_open_evidence_writer_on_old_inode(self):
        # A prototype admission probe, never the production restore path:
        # swapping complete copies does not coordinate an already-open writer.
        self.dest = self.sibling()
        stage, retired = self.root / 'swap-probe', self.root / 'retired-probe'
        shutil.copytree(self.dest, stage)
        event = list(evidence._reading_history(evidence.log_path(str(self.dest))))[0]
        event['event_id'] = evidence.new_event_id()
        event['session_id'] = identity.new_object_id()
        event['dedupe_key'] = evidence.dedupe_key(event['session_id'], event['item_id'],
                                                event['attempt_number'], event['canonical'])
        event_path = self.root / 'fictional-event.json'
        event_path.write_text(json.dumps(event))
        ready, release = self.root / 'ready', self.root / 'release'
        child = self.process('evidence-writer', self.dest, event_path, ready, release)
        try:
            self.wait_ready(child, ready)
            os.rename(self.dest, retired)
            os.rename(stage, self.dest)
        finally:
            release.touch()
        self.finish(child)
        live_ids = {e['event_id'] for e in evidence._reading_history(evidence.log_path(str(self.dest)))}
        retired_ids = {e['event_id'] for e in evidence._reading_history(evidence.log_path(str(retired)))}
        self.assertNotIn(event['event_id'], live_ids)
        self.assertIn(event['event_id'], retired_ids)


def child_main(mode, args):
    if mode in ('retry', 'refuse', 'crash'):
        package, dest = args
        if mode == 'crash':
            course_package._ordinary_destination_preflight = lambda *args: os._exit(73)
        try:
            result = course_package.restore_package(package, dest, 'human', 'fictional-child',
                                                    require_root_atomic=True)
        except course_package.PackageError as err:
            if mode != 'refuse':
                raise
            print(err.code)
        else:
            print(result['publication'])
        return
    dest, *args = args
    if mode == 'journal-writer':
        ready, release = map(Path, args)
        original = journal._journal_lock
        @contextlib.contextmanager
        def barrier(base):
            with original(base):
                ready.touch()
                wait_release(release)
                yield
        journal._journal_lock = barrier
        journal.commit_operation(dest, identity.new_object_id(), 'lesson', 'live.md', 'mint',
                                 b'# Fictional live writer\n', None, 'human', 'test', create_if_missing=True)
    elif mode == 'evidence-writer':
        event_path, ready, release = map(Path, args)
        original = evidence.locked
        @contextlib.contextmanager
        def barrier(fd):
            with original(fd):
                ready.touch()
                wait_release(release)
                yield
        evidence.locked = barrier
        evidence.append_event(evidence.log_path(dest), json.loads(event_path.read_text()))
    else:
        raise ValueError(mode)


def wait_release(release):
    deadline = time.monotonic() + 5
    while not release.exists():
        if time.monotonic() >= deadline:
            raise TimeoutError('Fictional writer barrier expired')
        time.sleep(0.01)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--child':
        child_main(sys.argv[2], sys.argv[3:])
    else:
        unittest.main()
