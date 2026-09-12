#!/usr/bin/env python3
"""Reading history transport through the existing offline package authority."""
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
import course
import course_package
import evidence
import graph
import journal
import reading
import reading_desk
import identity
import source_adapters
import reading_declarations_roundtrip as declarations


class ReadingPackage(unittest.TestCase):
    setUp = declarations.ReadingDeclarations.setUp
    run_op = declarations.ReadingDeclarations.run_op
    read = declarations.ReadingDeclarations.read
    bind = declarations.ReadingDeclarations.bind
    values = declarations.ReadingDeclarations.values
    create = declarations.ReadingDeclarations.create
    confirmation = declarations.ReadingDeclarations.confirmation
    declare = declarations.ReadingDeclarations.declare

    def history(self):
        first = self.create()['occurrence']
        second = self.create()['occurrence']
        receipt = self.declare(self.confirmation(first))
        correction = evidence.retraction_event(receipt['event_id'], 'Synthetic correction')
        evidence.append_event(evidence.log_path(self.base), correction)
        latest = self.declare(self.confirmation(first))
        return first, second, [receipt['event'], correction, latest['event']]

    def restore(self, name='package'):
        package = str(Path(self.root, name))
        dest = str(Path(self.root, name + '-restored'))
        Path(dest).mkdir()
        course_package.export_package(self.base, self.base, package)
        result = course_package.restore_package(package, dest, 'human', 'test')
        return package, dest, result

    def test_exact_history_rights_omission_and_repeated_restore(self):
        first, second, rows = self.history()
        package, dest, result = self.restore()
        self.assertEqual(result['evidence_recorded'], 3)
        self.assertEqual(list(evidence.events(evidence.log_path(dest))), rows)
        self.assertTrue(any(r['category'] == 'rights-restricted' and
                            r['target'] == self.source_id for r in result['losses']))
        self.assertFalse(Path(dest, 'sources/example.md').exists())
        body = dict(expected_fingerprint=course.read_course(dest)['fingerprint'],
                    occurrence_id=first['occurrence_id'], revision_id=first['revision_id'])
        with self.assertRaises(course.CourseError) as raised:
            reading.confirm(dest, dict(body, confirmation='read'))
        self.assertEqual(raised.exception.code, 'course.unknown_source')
        self.assertEqual(result['reading_acceptance'], 'accepted')
        view = reading_desk.snapshot(dest, body)
        self.assertIsNone(view['content'])
        self.assertEqual(view['availability']['state'], 'course.unknown_source')
        self.assertEqual(view['reading_state']['state'], 'reported-read')
        cid = self.read()['object_id']
        state = evidence.reading_state(evidence.log_path(dest), cid,
                                       first['occurrence_id'], first['revision_id'])
        self.assertEqual(state['state'], 'reported-read')
        self.assertEqual(state['event_ids'], [rows[-1]['event_id']])
        self.assertEqual(evidence.reading_state(evidence.log_path(dest), cid,
                         second['occurrence_id'], second['revision_id'])['state'], 'not-reported')
        again = course_package.restore_package(package, dest, 'human', 'test')
        self.assertEqual(again['evidence_recorded'], 0)
        self.assertEqual(again['evidence_already_recorded'], 3)
        self.assertEqual(list(evidence.events(evidence.log_path(dest))), rows)

    def test_native_source_original_receipts_and_exact_undo(self):
        first, second, rows = self.history()
        request = self.confirmation(second)
        journal.op_grant_rights(self.base, self.source_id, {'package': 'granted'}, self.source_fp, 'human', 'test')
        original = list(journal.entries(self.base))
        package, dest, result = self.restore()
        self.assertEqual(result['reading_acceptance'], 'accepted')
        self.assertEqual(list(journal.entries(dest)), original)
        self.assertEqual(journal._compute_registry(dest), journal._compute_registry(self.base))
        body = dict(expected_fingerprint=self.read()['fingerprint'],
                    occurrence_id=first['occurrence_id'], revision_id=first['revision_id'])
        view = reading_desk.snapshot(dest, body)
        self.assertEqual(view['content'], 'First synthetic paragraph.')
        self.assertEqual(reading.declare(dest, request)['status'], 'recorded')
        applied = [e for e in original if e['object_id'] == self.read()['object_id'] and e['state'] == 'applied']
        journal.undo(dest, applied[-1]['entry_id'], 'human', 'test')
        read = course.read_course(dest)
        self.assertEqual(course.accepted_reading_graph(dest, read['fingerprint'])['fingerprint'], read['fingerprint'])

    def test_missing_provenance_is_degraded_and_named(self):
        first, second, rows = self.history()
        image = next(e['before_image'] for e in journal.entries(self.base) if e.get('before_image'))
        Path(journal.journal_dir(self.base), image).unlink()
        package, dest, result = self.restore()
        self.assertEqual(result['reading_acceptance'], 'unknown')
        self.assertTrue(any(r['category'] == 'reading-transport-loss' and r['target'] == self.read()['object_id'] for r in result['losses']))
        self.assertEqual(list(evidence.events(evidence.log_path(dest))), rows)
        self.assertEqual(course_package.restore_package(package, dest, 'human', 'test')['evidence_recorded'], 0)

    def test_missing_confirmation_requires_fresh_intent(self):
        first = self.create()['occurrence']
        request = self.confirmation(first)
        self.declare(request)
        journal.op_grant_rights(self.base, self.source_id, {'package': 'granted'}, self.source_fp, 'human', 'test')
        original = [e for e in journal.entries(self.base) if e['object_id'] is not None]
        Path(journal.log_path(self.base)).write_text(''.join(json.dumps(e) + '\n' for e in original))
        package, dest, result = self.restore()
        self.assertTrue(any('Confirmation receipt' in r['reason'] for r in result['losses']))
        with self.assertRaises(course.CourseError) as error:
            reading.declare(dest, request)
        self.assertEqual(error.exception.code, 'course.reading_confirmation_missing')
        context = {k: v for k, v in request.items() if k != 'intent_id'}
        fresh = reading.confirm(dest, dict(context, confirmation='read'))
        self.assertEqual(reading.declare(dest, dict(context, intent_id=fresh['intent_id']))['status'], 'already_recorded')

    def test_transport_tampering_refuses_before_destination_mutation(self):
        self.history()
        package, _dest, _result = self.restore()
        path = Path(package, course_package.READING_TRANSPORT_FILENAME)
        transport = json.loads(path.read_bytes())
        applied = next(e for e in transport['entries'] if e['state'] == 'applied' and e['object_id'])
        applied['resolves_entry'] = 'f' * 32
        raw = json.dumps(transport).encode(); path.write_bytes(raw)
        mpath = Path(package, course_package.MANIFEST_FILENAME)
        manifest = json.loads(mpath.read_bytes()); manifest['reading_transport_fingerprint'] = course_package._digest(raw)
        mpath.write_text(json.dumps(manifest))
        dest = Path(self.root, 'tampered'); dest.mkdir()
        with self.assertRaises(course_package.PackageError) as error:
            course_package.restore_package(package, str(dest), 'human', 'test')
        self.assertEqual(error.exception.code, 'package.invalid_transport')
        self.assertEqual(list(dest.iterdir()), [])

    def test_known_empty_and_missing_history_stay_distinct(self):
        first = self.create()['occurrence']
        self.confirmation(first)
        _package, dest, _result = self.restore('empty')
        self.assertTrue(Path(evidence.log_path(dest)).is_file())
        self.assertEqual(Path(evidence.log_path(dest)).read_bytes(), b'')
        Path(evidence.log_path(self.base)).unlink()
        _package, dest, result = self.restore('missing')
        self.assertFalse(Path(evidence.log_path(dest)).exists())
        self.assertTrue(any(r['target'] == 'reading-history' for r in result['losses']))

    def test_interrupted_publication_and_object_conflict_preserve_destination(self):
        self.history()
        package = str(Path(self.root, 'interrupted'))
        dest = Path(self.root, 'target'); dest.mkdir()
        course_package.export_package(self.base, self.base, package)
        with mock.patch.object(course_package, 'publish_directory', side_effect=OSError('synthetic interruption')):
            with self.assertRaises(OSError):
                course_package.restore_package(package, str(dest), 'human', 'test')
        self.assertEqual(list(dest.iterdir()), [])
        (dest / 'course.md').write_bytes(b'Existing unrelated bytes')
        before = {str(p.relative_to(dest)): p.read_bytes() for p in dest.rglob('*') if p.is_file()}
        with self.assertRaises(course_package.PackageError) as error:
            course_package.restore_package(package, str(dest), 'human', 'test')
        self.assertEqual(error.exception.code, 'package.object_conflict')
        self.assertEqual(before, {str(p.relative_to(dest)): p.read_bytes() for p in dest.rglob('*') if p.is_file()})

    def test_adapted_source_companion_crosses_with_accepted_descriptor(self):
        raw = b'Adapted synthetic paragraph.\n'; sid = identity.new_object_id()
        side = source_adapters.build_sidecar(sid, 'markdown', raw,
            {'kind': 'local_file', 'value': 'synthetic.md', 'fetched_at': None,
             'http_etag': None, 'http_last_modified': None, 'snapshot_rel_path': None},
            identity.rights_default(), [{'id': 'L1', 'kind': 'block', 'span_id': 'sp-0',
             'body': {'medium': 'markdown', 'line': 1}}], ['L1'], [])
        sidebytes = json.dumps(side).encode(); path = 'sources/adapted.md'
        rev = journal.commit_operation(self.base, sid, 'source', path, 'mint', raw, None,
            'human', 'test', create_if_missing=True, rights={'read': 'granted', 'package': 'granted'},
            companions=({'path': source_adapters.sidecar_path_for(path), 'expected_digest': None, 'new_bytes': sidebytes},))
        self.source_id = sid; self.source_fp = rev['fingerprint']
        self.run_op('add_source', source_object_id=sid, title='Adapted'); self.bind('L1')
        values = self.values(); values['source_ref']['locator'] = 'L1'
        values['source_ref']['range'] = {'span_id': 'sp-0', 'locator_id': 'L1',
            'locator_sidecar_fingerprint': identity.object_fingerprint(sidebytes, 'source')}
        first = self.run_op('create_reading', expected_fingerprint=self.read()['fingerprint'],
            binding_index=1, values=values, title='Adapted', activation='Now')['occurrence']
        self.declare(self.confirmation(first))
        _package, dest, result = self.restore()
        self.assertEqual(Path(dest, source_adapters.sidecar_path_for(path)).read_bytes(), sidebytes)
        body = dict(expected_fingerprint=self.read()['fingerprint'],
                    occurrence_id=first['occurrence_id'], revision_id=first['revision_id'])
        self.assertEqual(reading_desk.snapshot(dest, body)['content'], 'Adapted synthetic paragraph.')
        Path(self.base, source_adapters.sidecar_path_for(path)).unlink()
        _package, dest, result = self.restore('missing-locator')
        self.assertTrue(any(r['target'] == source_adapters.sidecar_path_for(path) for r in result['losses']))
        self.assertIsNone(reading_desk.snapshot(dest, body)['content'])

    def test_foreign_reading_and_correction_are_not_carried(self):
        first, second, rows = self.history()
        foreign = copy.deepcopy(first)
        other = evidence.reading_declared_event('f' * 16, foreign, 'e' * 32, None)
        evidence.append_event(evidence.log_path(self.base), other, precommit=lambda: None)
        evidence.append_event(evidence.log_path(self.base), evidence.retraction_event(
            other['event_id'], 'Foreign private correction'))
        scope = course_package.evidence_scope(self.base, self.base)
        # A matching session cannot override the explicit foreign course ID.
        forged = dict(other, session_id='shared', objective=self.objective)
        self.assertFalse(course_package._event_claimed(forged, scope, {'shared'}))
        lines, losses = course_package.evidence_export_lines(self.base, scope)
        self.assertEqual([json.loads(line) for line in lines], rows)
        self.assertEqual(len(losses), 1)
        self.assertNotIn('Foreign private correction', json.dumps(losses))
        self.assertIn('2 event(s)', losses[0]['reason'])

    def test_orphan_occurrence_history_survives_and_tampering_refuses(self):
        first, second, rows = self.history()
        doc = copy.deepcopy(self.read()['doc'])
        doc['reading_occurrences'] = []
        doc['reading_placement'] = []
        course.write_course(self.base, doc, self.read()['fingerprint'], 'human', 'test')
        package, dest, result = self.restore()
        self.assertEqual(list(evidence.events(evidence.log_path(dest))), rows)
        self.assertEqual(graph.validate_reading_graph(course.read_course(dest)['doc'])['occurrences'], [])
        payload = Path(package, course_package.EVIDENCE_DIRNAME, course_package.EVIDENCE_FILENAME)
        payload.write_bytes(payload.read_bytes() + b' ')
        untouched = Path(self.root, 'refused')
        untouched.mkdir()
        with self.assertRaises(course_package.PackageError) as raised:
            course_package.restore_package(package, str(untouched), 'human', 'test')
        self.assertEqual(raised.exception.code, 'package.fingerprint_mismatch')
        self.assertEqual(list(untouched.iterdir()), [])

    def test_divergent_event_refuses_before_destination_objects_change(self):
        first, second, rows = self.history()
        package, dest, result = self.restore()
        log = Path(evidence.log_path(dest))
        changed = copy.deepcopy(rows)
        changed[1]['reason'] = 'A different correction under the same identity'
        log.write_text(''.join(json.dumps(row) + '\n' for row in changed))
        before = {str(p.relative_to(dest)): p.read_bytes()
                  for p in Path(dest).rglob('*') if p.is_file()}
        with self.assertRaises(course_package.PackageError) as raised:
            course_package.restore_package(package, dest, 'human', 'test')
        self.assertEqual(raised.exception.code, 'package.evidence_identity_conflict')
        after = {str(p.relative_to(dest)): p.read_bytes()
                 for p in Path(dest).rglob('*') if p.is_file()}
        self.assertEqual(after, before)

    def test_foreign_payload_refuses_even_with_updated_manifest_checksum(self):
        first, second, rows = self.history()
        package, dest, result = self.restore()
        foreign = evidence.reading_declared_event('f' * 16, first, 'e' * 32, None)
        raw = (json.dumps(foreign) + '\n').encode()
        Path(package, course_package.EVIDENCE_DIRNAME,
             course_package.EVIDENCE_FILENAME).write_bytes(raw)
        manifest_path = Path(package, course_package.MANIFEST_FILENAME)
        manifest = json.loads(manifest_path.read_text())
        manifest['evidence_fingerprint'] = course_package._digest(raw)
        manifest_path.write_text(json.dumps(manifest))
        target = Path(self.root, 'foreign-refused')
        target.mkdir()
        with self.assertRaises(course_package.PackageError) as raised:
            course_package.restore_package(package, str(target), 'human', 'test')
        self.assertEqual(raised.exception.code, 'package.reading_course_conflict')
        self.assertEqual(list(target.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
