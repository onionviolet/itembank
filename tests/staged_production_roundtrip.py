"""Production staged commitments, disclosure and durable recovery on synthetic banks."""
import json
import multiprocessing
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import evidence, model, runtime, schema_validate
from surfaces import session

CASE = {'version': 1, 'activity_id': 'synthetic:counter-staged',
        'stimulus': 'A fictional counter starts at 3 and adds 2 once.',
        'children': ['a200000000000001', 'a200000000000002'],
        'order': ['answer', 'reason']}


def process_commit(path, action, queue):
    try:
        queue.put(('accepted', session.do_action(path, action)['accepted']))
    except SystemExit as exc:
        queue.put(('refused', str(exc)))


class StagedProduction(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.bank = self.base / 'bank.md'
        text = (ROOT / 'prototypes/audit-question-families/fixtures/bank.md').read_text()
        text = text[:text.index('Q3.')]
        self.bank.write_text('STAGED-CASES: ' + json.dumps([CASE]) + '\n' + text)
        self.path = str(self.base / 'sitting.json')

    def start(self, mode='practice'):
        return session.do_start(str(self.bank), {'count': 2, 'selection_mode': 'exam'},
                                mode, self.path, False)

    def action(self, answer='B'):
        activity = session.do_next(self.path)['activity']
        return dict(kind='submit', answer=answer, **{
            key: activity[key] for key in ('activity_id', 'child_id', 'submission_token')})

    def test_wrong_commit_advances_and_release_keeps_child_denominators(self):
        self.start()
        result = session.do_action(self.path, self.action())
        self.assertNotIn('score', result)
        self.assertEqual(result['next']['activity']['stage'], 'reason')
        self.assertEqual(result['next']['activity']['committed_answer'], 'B')
        self.assertFalse(session.do_teach(self.path)['teaching']['available'])
        self.assertIsNone(session.do_report(self.path)['summary']['auto_correct'])
        result = session.do_action(self.path, self.action())
        self.assertEqual([row['score'] for row in result['activity_feedback']], [False, True])
        rows = list(evidence.events(evidence.log_path(str(self.base))))
        rows = [row for row in rows if row['event_type'] == 'response']
        self.assertEqual([row['stage'] for row in rows], ['answer', 'reason'])
        self.assertEqual(len({row['objective'] for row in rows}), 2)
        for row in rows:
            self.assertEqual(schema_validate.validate(row, json.loads((ROOT/'schemas/response.schema.json').read_text())), [])
        self.assertEqual(schema_validate.validate(runtime.read_session(self.path), json.loads((ROOT/'schemas/session.schema.json').read_text())), [])

    def test_invalid_forged_stale_replay_and_binding_refusal(self):
        self.start()
        action = self.action()
        original = Path(self.path).read_bytes()
        for changes in ({'answer':'Z'}, {'stage':'reason'}, {'child_id':'unknown'}, {'submission_token':'stale'}, {'kind':'hint'}):
            with self.assertRaises(SystemExit):
                session.do_action(self.path, dict(action, **changes))
            self.assertEqual(Path(self.path).read_bytes(), original)
        session.do_action(self.path, action)
        with self.assertRaises(SystemExit):
            session.do_action(self.path, action)
        self.bank.write_text(self.bank.read_text()+'\n')
        with self.assertRaises(SystemExit):
            session.do_action(self.path, self.action())

    def test_process_serialization_identical_and_conflicting(self):
        for second_answer in ('B', 'A'):
            self.start()
            action = self.action()
            context = multiprocessing.get_context('spawn')
            queue = context.Queue()
            processes = [context.Process(target=process_commit, args=(self.path, dict(action, answer=answer), queue))
                         for answer in ('B', second_answer)]
            for process in processes: process.start()
            for process in processes: process.join(20); self.assertEqual(process.exitcode, 0)
            outcomes = [queue.get(timeout=2)[0] for _ in processes]
            self.assertEqual(sorted(outcomes), ['accepted', 'refused'])
            self.assertEqual(len(runtime.read_session(self.path)['responses']), 1)
            queue.close()

    def test_crash_after_append_repairs_without_new_attempt(self):
        self.start()
        action = self.action()
        original = Path(self.path).read_bytes()
        with patch.object(session, 'write_session', side_effect=OSError('injected write boundary')):
            with self.assertRaises(OSError): session.do_action(self.path, action)
        self.assertEqual(Path(self.path).read_bytes(), original)
        with patch.object(session, 'score_response', side_effect=AssertionError('must not rescore recovery')):
            recovered = session.do_next(self.path)
        self.assertEqual(recovered['activity']['stage'], 'reason')
        self.assertEqual(len(runtime.read_session(self.path)['responses']), 1)
        with self.assertRaises(SystemExit): session.do_action(self.path, action)
        session.do_action(self.path, self.action())
        self.assertEqual(len(runtime.read_session(self.path)['responses']), 2)

    def test_before_append_crash_preserves_and_missing_binding_freezes(self):
        self.start()
        action = self.action()
        original = Path(self.path).read_bytes()
        with patch.object(evidence, 'append_event', side_effect=OSError('injected append boundary')):
            with self.assertRaises(OSError): session.do_action(self.path, action)
        self.assertEqual(Path(self.path).read_bytes(), original)
        data = runtime.read_session(self.path)
        data['staged_cases'] = []
        runtime.write_session(self.path, data)
        with self.assertRaises(SystemExit): session.do_next(self.path)

    def test_partial_count_filters_and_formal_withholding(self):
        for spec in ({'count':1}, {'count':2,'objective':'synthetic:counter-result'}):
            with self.assertRaises(SystemExit):
                session.do_start(str(self.bank), spec, 'practice', self.path, False)
        for mode in ('exam','diagnostic'):
            self.start(mode)
            first = session.do_action(self.path, self.action())
            self.assertNotIn('score', first)
            final = session.do_action(self.path, self.action())
            self.assertNotIn('activity_feedback', final)
            self.assertNotIn('score', final)

    def test_completed_case_release_survives_next_case_and_bad_event_binding(self):
        text = self.bank.read_text()
        body = text[text.index('Q1.'):]
        second = body.replace('Q1. What', 'Q3. Again, what').replace('Q2. Which', 'Q4. Again, which').replace(
            'a200000000000001', 'a200000000000003').replace(
            'a200000000000002', 'a200000000000004')
        second_case = dict(CASE, activity_id='synthetic:second',
                           children=['a200000000000003', 'a200000000000004'])
        self.bank.write_text('STAGED-CASES: '+json.dumps([CASE,second_case])+'\n'+body+second)
        session.do_start(str(self.bank), {'count':4,'pair':'a2-counter'},
                         'practice', self.path, False)
        session.do_action(self.path, self.action())
        result = session.do_action(self.path, self.action())
        self.assertEqual(result['next']['activity']['activity_id'], second_case['activity_id'])
        self.assertEqual(len(result['activity_feedback']), 2)
        data = runtime.read_session(self.path)
        events = [event for event in evidence.events(evidence.log_path(str(self.base)))
                  if event['event_type']=='response']
        self.assertIn('score', runtime.evidence_feedback(events[0], data))
        self.assertNotIn('score', runtime.evidence_feedback(
            dict(events[0], case_revision='changed'), data))
        self.assertNotIn('score', runtime.evidence_feedback(
            dict(events[0], session_id='changed'), data))
        self.assertNotIn('score', runtime.evidence_feedback(events[0], None))

    def test_replay_into_following_ordinary_item_and_all_hint_routes(self):
        text = self.bank.read_text()
        body = text[text.index('Q1.'):text.index('Q2.')]
        ordinary = body.replace('Q1. What', 'Q3. Separately, what').replace('a200000000000001','a200000000000003')
        self.bank.write_text(text+ordinary)
        session.do_start(str(self.bank), {'count':3,'pair':'a2-counter'},
                         'practice', self.path, False)
        for hint in (session.do_hint, runtime.invoke_hint):
            with self.assertRaises(SystemExit): hint(self.path)
        session.do_action(self.path, self.action())
        reason = self.action()
        session.do_action(self.path, reason)
        original = Path(self.path).read_bytes()
        with self.assertRaises(SystemExit): session.do_action(self.path, reason)
        self.assertEqual(original, Path(self.path).read_bytes())

    def test_ordinary_retries_before_case_and_whole_exclusion(self):
        text = self.bank.read_text()
        body = text[text.index('Q1.'):]
        ordinary = body[:body.index('Q2.')].replace(
            'Q1. What', 'Q1. Separately, what').replace(
            'a200000000000001', 'a200000000000003')
        case_body = body.replace('Q1.', 'Q2.').replace('Q2. Which', 'Q3. Which')
        self.bank.write_text('STAGED-CASES: '+json.dumps([CASE])+'\n'+ordinary+case_body)
        session.do_start(str(self.bank), {'count':3,'pair':'a2-counter'},
                         'practice', self.path, False)
        session.do_submit(self.path, 'B', None)
        session.do_submit(self.path, 'A', None)
        view = session.do_next(self.path)
        self.assertEqual(view['activity']['stage'], 'answer')
        session.do_action(self.path, self.action())
        self.assertEqual(session.do_next(self.path)['activity']['committed_answer'], 'B')
        result = session.do_action(self.path, self.action())
        self.assertEqual([row['score'] for row in result['activity_feedback']], [False,True])
        self.assertEqual(len(runtime.read_session(self.path)['responses']), 4)
        excluded = session.do_start(str(self.bank),
            {'count':1,'exclude_item_ids':CASE['children'],'selection_mode':'exam'},
            'practice', str(self.base/'excluded.json'), False)
        self.assertNotIn('activity', excluded)

    def test_expired_timed_binding_conflict_preserves_session(self):
        session.do_start(str(self.bank), {'count':2,'selection_mode':'exam'},
                         'exam', self.path, False, time_limit_minutes=1)
        data = runtime.read_session(self.path)
        data['timing']['deadline'] = '2000-01-01T00:00:00.000Z'
        runtime.write_session(self.path, data)
        self.bank.write_text(self.bank.read_text()+'\n')
        original = Path(self.path).read_bytes()
        for entry in (session.do_next, session.do_report):
            with self.assertRaises(SystemExit): entry(self.path)
            self.assertEqual(original, Path(self.path).read_bytes())
        with self.assertRaises(SystemExit): session.do_action(self.path, {'kind':'submit','answer':'A'})
        self.assertEqual(original, Path(self.path).read_bytes())

    def test_upgrade_has_no_inferred_case_and_future_refuses(self):
        self.start()
        data = runtime.read_session(self.path)
        for version in (1,2,3):
            legacy = dict(data, schema_version=version)
            legacy.pop('staged_cases'); legacy.pop('staged_binding_required')
            self.assertEqual(runtime.upgrade_session(legacy)['staged_cases'], [])
        with self.assertRaises(SystemExit):
            runtime.upgrade_session(dict(data,schema_version=runtime.SESSION_VERSION+1))


if __name__ == '__main__': unittest.main()
