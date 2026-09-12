#!/usr/bin/env python3
"""Journaled reading operations on synthetic local courses only."""
import copy
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
sys.path.insert(0, str(ROOT / 'tests'))
import course
import graph
import identity
import journal
import source_adapters
from surfaces import course_ops, daemon
from reading_graph_roundtrip import occurrence_values
from daemon_roundtrip import start_daemon, json_request


class ReadingOperations(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='reading_ops_')
        self.addCleanup(self.temp.cleanup)
        self.root = self.temp.name
        self.base = os.path.join(self.root, 'synthetic')
        self.run_op('create', title='Synthetic reading')
        self.run_op('add_objective', statement='Compare the synthetic examples')
        self.objective = self.read()['doc']['objectives'][0]['id']
        source = self.run_op('register_source', filename='example.md',
                             content='# Example\nFirst synthetic paragraph.\nSecond paragraph.\n',
                             grants={'read': 'granted', 'transform': 'granted'})
        self.source_id = source['source_object_id']
        self.source_fp = source['fingerprint']
        self.run_op('add_source', source_object_id=self.source_id, title='Example')
        self.bind('line 2')

    def run_op(self, operation, **body):
        return course_ops.run(self.root, operation, dict(course_id='synthetic', **body))

    def read(self):
        return course.read_course(self.base)

    def bind(self, locator):
        return self.run_op('bind_treatment', objective=self.objective,
                           source=self.source_id, treatment='direct-reading',
                           locator=locator)

    def values(self):
        values = occurrence_values({'binding_id': 'a'*16, 'binding_revision_id': 'b'*16,
                                    'locator': 'line 2'}, self.objective, self.source_id)
        values.pop('binding_ref')
        values['source_ref']['source_fingerprint'] = self.source_fp
        values['source_ref']['range']['span_id'] = 'sp-1'
        return values

    def create(self, **overrides):
        body = dict(expected_fingerprint=self.read()['fingerprint'], binding_index=0,
                    values=self.values(), title='First reading', activation='Now')
        body.update(overrides)
        return self.run_op('create_reading', **body)

    def edit(self, operation, receipt, **extra):
        return self.run_op(operation, expected_fingerprint=self.read()['fingerprint'],
                           occurrence_id=receipt['occurrence']['occurrence_id'],
                           revision_id=receipt['occurrence']['revision_id'], **extra)

    def refused(self, call, code=None):
        before = Path(course.sidecar_path(self.base)).read_bytes()
        with self.assertRaises((course.CourseError, graph.GraphError, journal.JournalError)) as raised:
            call()
        if code:
            self.assertEqual(raised.exception.code, code)
        self.assertEqual(Path(course.sidecar_path(self.base)).read_bytes(), before)

    def test_atomic_shared_revision_placement_restart_undo(self):
        before = Path(course.sidecar_path(self.base)).read_bytes()
        prior = len([e for e in journal.entries(self.base) if e['state'] == 'applied'])
        first = self.create()
        self.assertEqual(len([e for e in journal.entries(self.base) if e['state'] == 'applied']), prior + 1)
        journal.undo(self.base, first['entry_id'], 'human', 'test')
        self.assertEqual(Path(course.sidecar_path(self.base)).read_bytes(), before)
        first = self.create()
        values = self.values(); values['binding_ref'] = first['binding_ref']
        second = self.run_op('create_reading', expected_fingerprint=self.read()['fingerprint'],
                             values=values, title='Reread', activation='Library')
        self.assertNotEqual(first['occurrence']['occurrence_id'], second['occurrence']['occurrence_id'])
        self.assertEqual(first['binding_ref'], second['binding_ref'])
        placed = self.edit('place_reading', first, title='Renamed', activation='Library')
        self.assertEqual(placed['occurrence'], first['occurrence'])
        changed = self.edit('revise_reading', first, changes={'purpose': 'Compare a new distinction'},
                            title='Changed task', activation='Now')
        records = graph.validate_reading_graph(self.read()['doc'])['occurrences']
        self.assertIn(first['occurrence'], records)
        self.assertEqual(changed['occurrence']['supersedes_revision_id'], first['occurrence']['revision_id'])
        self.refused(lambda: self.edit('revise_reading', first, changes={'purpose': 'Ancestor edit'}),
                     'course.reading_revision_stale')
        journal.rebuild_registry(self.base)
        script = 'import course,graph,sys; r=course.accepted_reading_graph(sys.argv[1],sys.argv[2]); print(len(graph.validate_reading_graph(r["doc"])["occurrences"]))'
        proc = subprocess.run([sys.executable, '-c', script, self.base, self.read()['fingerprint']],
                              cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr); self.assertEqual(proc.stdout.strip(), '3')
        journal.undo(self.base, changed['entry_id'], 'human', 'test')
        self.assertEqual(graph.validate_reading_graph(self.read()['doc'])['occurrences'], records[:-1])

    def test_refusals_preserve_graph(self):
        self.refused(lambda: self.create(expected_fingerprint='sha256:'+'0'*64), 'course.reading_stale')
        self.refused(lambda: self.create(expected_fingerprint=''), 'course.invalid_request')
        self.refused(lambda: self.create(binding_index=99))
        values = self.values(); values['source_ref']['range']['span_id'] = 'missing'
        self.refused(lambda: self.create(values=values), 'course.reading_range_unsupported')
        values = self.values(); values['source_ref']['source_fingerprint'] = 'sha256:'+'0'*64
        self.refused(lambda: self.create(values=values), 'course.reading_source_stale')
        for state in ('denied', 'unknown'):
            journal.op_grant_rights(self.base, self.source_id, {'read': state}, self.source_fp, 'human', 'test')
            self.refused(self.create, 'course.rights_not_granted')
        journal.op_grant_rights(self.base, self.source_id, {'read': 'granted'}, self.source_fp, 'human', 'test')
        path = Path(self.base)/'sources/example.md'
        path.write_text('Changed source\n')
        self.refused(self.create, 'course.reading_source_stale')
        path.unlink(); path.symlink_to(ROOT/'README.md')
        self.refused(self.create, 'course.reading_outside_root')

    def test_missing_provenance_and_external_graph(self):
        path = Path(course.sidecar_path(self.base))
        path.write_text(path.read_text().replace('Synthetic reading', 'External edit'))
        self.refused(self.create, 'course.reading_acceptance_unknown')
        Path(journal.log_path(self.base)).write_text('')
        self.refused(self.create, 'course.reading_acceptance_unknown')

    def test_ambiguous_native_locator(self):
        path = Path(self.base)/'sources/example.md'
        journal.op_edit_in_place(self.base, self.source_id, 'source', 'sources/example.md',
                                 b'# Example\n# Example\n', self.source_fp, 'human', 'test')
        self.source_fp = journal.read_registry(self.base)[self.source_id]['fingerprint']
        self.bind('Example')
        values = self.values(); values['source_ref']['locator'] = 'Example'
        values['source_ref']['range']['span_id'] = 'sp-0'
        self.refused(lambda: self.create(binding_index=1, values=values), 'course.reading_range_unsupported')

    def test_failed_replace_and_locked_rights_recheck(self):
        original = journal._write_bytes_atomic
        def fail_target(path, raw):
            if path == course.sidecar_path(self.base):
                raise OSError('synthetic disk failure')
            return original(path, raw)
        before = Path(course.sidecar_path(self.base)).read_bytes()
        with mock.patch.object(journal, '_write_bytes_atomic', side_effect=fail_target):
            with self.assertRaises(OSError): self.create()
        self.assertEqual(Path(course.sidecar_path(self.base)).read_bytes(), before)
        # The validator runs inside the same lock as graph acceptance.
        validate = course.validate_reading_source
        def probe(base, ref):
            with self.assertRaises(journal.JournalError) as raised:
                journal.op_grant_rights(base, self.source_id, {'read': 'denied'}, self.source_fp, 'human', 'race')
            self.assertEqual(raised.exception.code, 'journal.busy')
            return validate(base, ref)
        with mock.patch.object(course, 'validate_reading_source', side_effect=probe):
            self.create()

    def test_material_range_and_combined_failure(self):
        first = self.create()
        source = copy.deepcopy(first['occurrence']['source_ref'])
        source['locator'] = 'line 3'
        source['range']['span_id'] = 'sp-2'
        changed = self.edit('revise_reading', first, changes={'source_ref': source},
                            revise_binding=True, title='New range', activation='Library')
        self.assertEqual(changed['binding_ref']['binding_id'], first['binding_ref']['binding_id'])
        self.assertNotEqual(changed['binding_ref']['binding_revision_id'], first['binding_ref']['binding_revision_id'])
        self.assertEqual(len(self.read()['doc']['bindings']), 2)
        self.assertEqual(changed['occurrence']['supersedes_revision_id'], first['occurrence']['revision_id'])
        bad = copy.deepcopy(source); bad['range']['span_id'] = 'missing'
        self.refused(lambda: self.edit('revise_reading', changed,
                     changes={'source_ref': bad, 'purpose': 'Rejected task'},
                     title='Rejected title', activation='Now'), 'course.reading_range_unsupported')
        self.assertEqual(graph.validate_reading_graph(self.read()['doc'])['placements'][
            first['occurrence']['occurrence_id']]['title'], 'New range')
        self.refused(lambda: self.edit('place_reading', changed, title='Only title'),
                     'course.invalid_request')

    def test_missing_prepared_and_missing_native_locator(self):
        values = self.values(); values['source_ref']['locator'] = 'missing section'
        self.bind('missing section')
        self.refused(lambda: self.create(binding_index=1, values=values), 'course.reading_range_unsupported')
        rows = list(journal.entries(self.base))
        last = journal.read_registry(self.base)[self.read()['object_id']]['last_entry_id']
        prepared = next(row['resolves_entry'] for row in rows if row['entry_id'] == last)
        Path(journal.log_path(self.base)).write_text(''.join(json.dumps(row)+'\n' for row in rows
                                                          if row['entry_id'] != prepared))
        self.refused(self.create, 'course.reading_acceptance_unknown')

    def test_adapted_locator_acceptance(self):
        # Synthetic already-adapted bytes and sidecar enter through the existing
        # journal companion path. No adapter generation is under test here.
        raw = b'Adapted synthetic paragraph.\n'
        source_id = identity.new_object_id()
        locators = [{'id':'L1', 'kind':'block', 'span_id':'sp-0',
                     'body':{'medium':'markdown','line':1}}]
        sidecar = source_adapters.build_sidecar(source_id, 'markdown', raw,
                    {'kind':'local_file','value':'synthetic.md','fetched_at':None,
                     'http_etag':None,'http_last_modified':None,'snapshot_rel_path':None},
                    identity.rights_default(), locators, ['L1'], [])
        sidebytes = json.dumps(sidecar).encode()
        path = 'sources/adapted.md'; sidepath = source_adapters.sidecar_path_for(path)
        revision = journal.commit_operation(self.base, source_id, 'source', path, 'mint', raw,
                    None, 'human', 'test', create_if_missing=True, rights={'read':'granted'},
                    companions=({'path':sidepath,'expected_digest':None,'new_bytes':sidebytes},))
        self.source_id = source_id; self.source_fp = revision['fingerprint']
        self.run_op('add_source', source_object_id=source_id, title='Adapted')
        self.bind('L1')
        values = self.values(); values['source_ref']['locator']='L1'
        values['source_ref']['range'] = {'span_id':'sp-0','locator_id':'L1',
                'locator_sidecar_fingerprint':identity.object_fingerprint(sidebytes,'source')}
        wrong = copy.deepcopy(values)
        wrong['source_ref']['range']['locator_id'] = 'absent'
        self.refused(lambda: self.create(binding_index=1, values=wrong), 'course.reading_locator_invalid')
        wrong = copy.deepcopy(values)
        wrong['source_ref']['range']['locator_sidecar_fingerprint'] = 'sha256:'+'0'*64
        self.refused(lambda: self.create(binding_index=1, values=wrong), 'course.reading_locator_stale')
        self.create(binding_index=1, values=values)
        side = Path(self.base)/sidepath
        side.write_bytes(sidebytes+b' ')
        self.refused(lambda: self.create(binding_index=0, values=values))
        self.refused(lambda: course.validate_reading_source(self.base, values['source_ref']),
                     'course.reading_locator_unaccepted')

    def test_http_cli_and_schema(self):
        proc, url, _ = start_daemon(self.root)
        self.addCleanup(proc.wait); self.addCleanup(proc.terminate)
        request = dict(course_id='synthetic', expected_fingerprint=self.read()['fingerprint'],
                       values=self.values(), binding_index=0, title='HTTP reading', activation='Now')
        status, result = json_request(url+'api/course/create-reading', request)
        self.assertEqual(status, 200, result)
        item = result['occurrence']
        cmd = [sys.executable, str(ROOT/'itembank.py'), 'course', 'place-reading', 'synthetic',
               '--root', self.root, '--expect', self.read()['fingerprint'],
               '--occurrence-id', item['occurrence_id'], '--revision-id', item['revision_id'],
               '--title', 'CLI rename', '--activation', 'Library', '--json']
        reply = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(reply.returncode, 0, reply.stderr)
        self.assertEqual(json.loads(reply.stdout)['occurrence'], item)
        self.refused(lambda: self.edit('revise_reading', result, changes={'revision_id':'f'*16}),
                     'course.invalid_request')
        for operation in ('create_reading','revise_reading','place_reading'):
            route = ('POST','/api/course/'+operation.replace('_','-'))
            self.assertEqual(daemon.ROUTE_CLI[route], 'course')
            self.assertIn((route,'course','course_'+operation), daemon.SURFACE_PARITY)


if __name__ == '__main__':
    unittest.main()
