#!/usr/bin/env python3
"""Original unit: native prediction, check/repair, transfer and honest evidence."""
import importlib.util
import copy
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from urllib.error import HTTPError
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
import evidence
import model
import runtime
from schema_validate import validate
from surfaces import session
from surfaces import quiz_page
from daemon_roundtrip import get, json_request, start_daemon
from check_disclosure_roundtrip import assert_silent

spec = importlib.util.spec_from_file_location(
    'coding_unit_preview', ROOT / 'prototypes/coding-unit-20261001/preview.py')
preview = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preview)

OVER_BAD = 'def count_over(values, limit):\n    return sum(value >= limit for value in values)'
OVER_OK = 'def count_over(values, limit):\n    return sum(value > limit for value in values)'
MOST_OK = 'def count_at_most(values, ceiling):\n    return sum(value <= ceiling for value in values)'
ACTIVE_BAD = 'def count_active(windows, moment):\n    return sum(start <= moment <= stop for start, stop in windows)'
ACTIVE_OK = 'def count_active(windows, moment):\n    return sum(start <= moment < stop for start, stop in windows)'


class CodingUnit(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='coding-unit-test-')
        self.root = Path(self.temp.name)
        self.view = preview.prepare(self.root)
        self.path = self.root / '_attempts' / 'session_boundary_workshop.json'
        self.bank = self.root / preview.BANK.name
        self.sid = self.view['session_id']
        self.proc = None

    def tearDown(self):
        if self.proc is not None:
            self.proc.terminate()
            self.proc.wait(timeout=5)
            self.proc.stdout.close()
        self.temp.cleanup()

    def responses(self, sid=None):
        return [row for row in evidence.live_events(evidence.log_path(str(self.root)))
                if row.get('event_type') == 'response' and row.get('session_id') == (sid or self.sid)]

    def start_server(self):
        self.proc, self.base, _ = start_daemon(str(self.root))

    def request(self, route, payload):
        status, body = json_request(self.base + route, payload)
        self.assertEqual(status, 200, body)
        return body

    def submit(self, answer):
        return self.request('api/submit', {'session_id': self.sid, 'answer': answer})

    def test_explanation_is_saved_pending_review_and_reopens_after_mark_retraction(self):
        explanation = session.do_start(str(self.bank), {'count': 1, 'seed': 0, 'type': 'short'},
            'practice', str(self.root / '_attempts' / 'session_explanation.json'), False)
        self.sid = explanation['session_id']
        self.start_server()
        page = get(self.base + 'quiz/coding_boundary_unit?mode=practice&session=' + self.sid)[1]
        self.assertIn('unfamiliar boundary rule', page)
        self.assertNotIn('MODEL:', page)
        answer = 'Original fictional proof: equality at opening counts and equality at closing does not.'
        result = self.submit(answer)
        response = self.responses()[-1]
        self.assertIsNone(response['score'])
        self.assertEqual(response['answer'], answer)
        saved = runtime.read_session(str(self.root / '_attempts' / 'session_explanation.json'))
        self.assertEqual(saved['bank'], str(self.bank))
        current = self.request('api/next', {'session_id': self.sid})
        self.assertEqual(current['item']['type'], 'short')
        self.proc.terminate()
        self.proc.wait(timeout=5)
        self.proc.stdout.close()
        self.proc = None
        self.start_server()
        reopened = self.request('api/next', {'session_id': self.sid})
        self.assertEqual(reopened['item']['id'], current['item']['id'])
        marked = self.request('api/mark', {'session_id': self.sid, 'item_ref': response['item_ref'],
            'verdict': True, 'notes': 'Synthetic reviewer: inspect the authored criteria.'})
        self.assertEqual(marked['view']['status'], 'complete')
        evidence.append_event(evidence.log_path(str(self.root)),
            evidence.retraction_event(marked['event_id'], 'Synthetic reviewer withdrawal'))
        report = session.do_report(str(self.root / '_attempts' / 'session_explanation.json'))
        self.assertIn('pending', json.dumps(report).lower())

    def test_native_complete_loop_and_repaired_transfer(self):
        questions = model.load(str(self.bank))
        errors, _warnings = model.lint(questions)
        self.assertEqual(errors, [])
        self.assertEqual(runtime.read_session(str(self.path))['items'], [0, 1, 2, 3])
        self.start_server()
        _, lesson = get(self.base + 'lesson/coding_boundary_unit')
        self.assertIn('Ask the boundary question', lesson)
        self.assertNotIn('Fresh transfer:', lesson)
        _, page = get(self.base + 'quiz/coding_boundary_unit?mode=practice&session=' + self.sid)
        self.assertIn('Predict the printed value', page)
        self.assertIn('Read-only code', page)
        self.assertIn('matches += 1', page)
        self.assertIn('    if value &gt;= 9:', page)
        self.assertNotIn('Fresh transfer:', page)
        self.assertEqual(self.responses(), [])
        first = self.request('api/next', {'session_id': self.sid})
        self.assertEqual(first['item']['id'], 'q1')
        self.assertNotIn('correct', first['item'])
        self.assertEqual(self.submit('B')['action'], 'advance')
        wrong = self.submit(OVER_BAD)
        self.assertEqual(wrong['action'], 'hold')
        rows = wrong['interaction_result']['observations']
        self.assertEqual(rows[1]['reason'], 'wrong_output')
        self.assertNotEqual(rows[1]['expected'], rows[1]['actual'])
        native = quiz_page.baseline_for(session.do_next(str(self.path)), {}, '/answer',
                                       {'submit': 'synthetic'}, flash=wrong)
        self.assertIn('Execution observations', native)
        self.assertIn('Output differs', native)
        self.assertIn('count_over([3, 3], 3)', native)
        self.assertEqual(runtime.read_session(str(self.path))['cursor'], 1)
        current = self.request('api/next', {'session_id': self.sid})
        self.assertEqual(current['item']['id'], 'q2')
        self.assertNotIn('cases', current['item'])
        before = len(self.responses())
        self.submit(OVER_BAD)
        self.assertEqual(len(self.responses()), before, 'replay created another response')
        self.assertEqual(self.submit(OVER_OK)['action'], 'advance')
        starter = questions[2]['starter']
        self.assertEqual(self.submit(starter)['action'], 'hold')
        self.assertEqual(self.submit(MOST_OK)['action'], 'advance')
        transfer = self.request('api/next', {'session_id': self.sid})
        self.assertEqual(transfer['item']['id'], 'q4')
        self.assertNotIn('cases', transfer['item'])
        self.assertNotIn(ACTIVE_OK, json.dumps(transfer))
        self.assertEqual(self.submit(ACTIVE_BAD)['action'], 'hold')
        final = self.submit(ACTIVE_OK)
        self.assertEqual(final['action'], 'complete')
        events = self.responses()
        self.assertEqual(len(events), 7)
        code_events = [row for row in events if row.get('check_source') is not None]
        self.assertEqual([row['check_source'] for row in code_events],
                         [OVER_BAD, OVER_OK, starter, MOST_OK, ACTIVE_BAD, ACTIVE_OK])
        self.assertEqual([row['score'] for row in code_events], [False, True, False, True, False, True])
        self.assertTrue(all(row['objective'] == 'cs:boundary-filtering' for row in events))
        self.assertEqual(runtime.read_session(str(self.path))['status'], 'complete')

    def test_practice_restart_keeps_cursor_feedback_and_original_attempt(self):
        session.do_action(str(self.path), {'kind': 'submit', 'answer': 'B'})
        wrong = session.do_action(str(self.path), {'kind': 'submit', 'answer': OVER_BAD})
        self.assertEqual(wrong['action'], 'hold')
        saved = session.do_check_feedback(str(self.path))
        self.assertEqual(saved['interaction_result'], wrong['interaction_result'])
        self.assertIsNone(session.do_check_feedback(str(self.path), {
            'session_id': self.sid, 'position': 3, 'item': {'id': 'q4'}}))
        session.do_teach(str(self.path), kind='hint')
        tier = runtime.read_session(str(self.path))['teaching_state']
        errors = validate(runtime.read_session(str(self.path)), json.loads(
            (ROOT / 'schemas/session.schema.json').read_text()))
        self.assertEqual(errors, [])
        self.start_server()
        view = self.request('api/next', {'session_id': self.sid})
        self.assertEqual(view['item']['id'], 'q2')
        self.assertEqual(runtime.read_session(str(self.path))['teaching_state'], tier)
        self.assertEqual(self.responses()[-1]['check_source'], OVER_BAD)
        log = Path(evidence.log_path(str(self.root)))
        evidence_bytes = log.read_bytes()
        session_bytes = self.path.read_bytes()
        with patch('surfaces.session.run_check_source', side_effect=AssertionError('reran code')):
            self.assertEqual(session.do_check_feedback(str(self.path)), saved)
        self.assertEqual(log.read_bytes(), evidence_bytes)
        self.assertEqual(self.path.read_bytes(), session_bytes)
        route = self.base + 'quiz/coding_boundary_unit?mode=practice&session=' + self.sid
        for _ in range(2):
            try:
                _, page = get(route)
            except HTTPError as exc:
                self.fail(exc.read().decode('utf-8'))
            self.assertIn('Saved run. Current edits have not been checked.', page)
            self.assertIn('Output differs', page)
            self.assertIn('count_over([3, 3], 3)', page)
            self.assertIn('Code from this run', page)
        self.assertEqual(log.read_bytes(), evidence_bytes)
        self.assertEqual(self.submit(OVER_OK)['action'], 'advance')
        _, page = get(route)
        self.assertNotIn('Execution observations', page)

    def test_saved_feedback_refuses_stale_legacy_and_other_session_events(self):
        session.do_action(str(self.path), {'kind': 'submit', 'answer': 'B'})
        session.do_action(str(self.path), {'kind': 'submit', 'answer': OVER_BAD})
        data = runtime.read_session(str(self.path))
        qs = model.load(str(self.bank))
        event = self.responses()[-1]
        response_schema = json.loads((ROOT / 'schemas/response.schema.json').read_text())
        self.assertEqual(validate(event, response_schema), [])
        item_schema = json.loads((ROOT / 'schemas/item.schema.json').read_text())
        envelope = event['check_feedback']['interaction_result']
        self.assertEqual(validate(envelope, {
            '$defs': item_schema['$defs'], '$ref': '#/$defs/interaction_result'}), [])
        revision = hashlib.sha256(self.bank.read_bytes()).hexdigest()
        self.assertIsNotNone(runtime.saved_check_feedback(event, data, qs, revision))
        variants = [dict(event, session_id='other'), dict(event, mode='exam'),
                    dict(event, item_ref='q4'), dict(event, item_id='different'),
                    dict(event, bank='other.md'), dict(event, score=True)]
        legacy = dict(event)
        legacy.pop('check_feedback')
        variants.append(legacy)
        held = dict(event, activity_id='unreleased')
        variants.append(held)
        for candidate in variants:
            self.assertIsNone(runtime.saved_check_feedback(candidate, data, qs, revision))
        self.assertIsNone(runtime.saved_check_feedback(event, data, qs, 'changed'))
        changed = copy.deepcopy(qs)
        changed[1]['stem'] += ' Revised.'
        self.assertIsNone(runtime.saved_check_feedback(event, data, changed, revision))
        for state in (dict(data, mode='exam'), dict(data, mode='diagnostic'),
                      dict(data, cursor=3), dict(data, status='complete')):
            self.assertIsNone(runtime.saved_check_feedback(event, state, qs, revision))
        self.bank.write_text(self.bank.read_text() + '\n', encoding='utf-8')
        self.assertIsNone(session.do_check_feedback(str(self.path)))
        self.bank.write_bytes(preview.BANK.read_bytes())
        evidence.append_event(evidence.log_path(str(self.root)),
                              evidence.retraction_event(event['event_id'], 'synthetic check'))
        self.assertIsNone(session.do_check_feedback(str(self.path)))

    def test_new_session_does_not_inherit_saved_feedback(self):
        session.do_action(str(self.path), {'kind': 'submit', 'answer': 'B'})
        session.do_action(str(self.path), {'kind': 'submit', 'answer': OVER_BAD})
        other = self.root / '_attempts' / 'session_other.json'
        session.do_start(str(self.bank), {'count': 4, 'pair': 'boundary-workshop'},
                         'practice', str(other), False)
        session.do_action(str(other), {'kind': 'submit', 'answer': 'B'})
        self.assertIsNone(session.do_check_feedback(str(other)))

    def test_formal_sitting_holds_all_check_feedback_until_completion(self):
        path = self.root / '_attempts' / 'formal.json'
        view = session.do_start(str(self.bank), {'count': 4, 'pair': 'boundary-workshop'},
                                'exam', str(path), False)
        self.assertEqual(runtime.read_session(str(path))['items'], [0, 1, 2, 3])
        for answer in ('B', OVER_BAD, MOST_OK):
            result = session.do_action(str(path), {'kind': 'submit', 'answer': answer})
            self.assertEqual(result['action'], 'defer_feedback')
            assert_silent(result)
            before = session.do_next(str(path))
            page = quiz_page.baseline_for(before, {}, '/answer', {'submit': 'synthetic'}, flash=result)
            self.assertNotIn('Execution observations', page)
        result = session.do_action(str(path), {'kind': 'submit', 'answer': ACTIVE_OK})
        self.assertEqual(runtime.read_session(str(path))['status'], 'complete')
        self.assertEqual(len(self.responses(view['session_id'])), 4)
        self.assertIsInstance(session.do_report(str(path))['summary']['auto_correct'], int)

    def test_public_code_panel_preserves_text_and_escapes_markup(self):
        stem = 'Predict.\n\n```python\nif 2 < 3:\n    print("<img src=x onerror=alert(1)>")\n```'
        rendered = quiz_page.question_stem_html(stem)
        self.assertIn('    print(&quot;&lt;img', rendered)
        self.assertNotIn('<img', rendered)
        self.assertIn('role="region" aria-label="Read-only code"', rendered)
        plain = quiz_page.question_stem_html('Plain <text>.')
        self.assertEqual(plain, '<h1 class="stem" tabindex="-1">Plain &lt;text&gt;.</h1>')
        broken = 'Predict.\n\n```python\nmissing closing fence'
        self.assertIn(broken, quiz_page.question_stem_html(broken))
        observations = {'interaction_result': {'observations': [{'case_index': 1,
            'passed': False, 'reason': 'runtime_error', 'expected_kind': 'pattern',
            'input': 'synthetic', 'expected': '[0-9]+', 'actual': '<img src=x>',
            'stderr': '<script>synthetic</script>'}]}}
        feedback = quiz_page._check_feedback_html(observations)
        self.assertIn('Expected (pattern)', feedback)
        self.assertIn('Program stopped', feedback)
        self.assertNotIn('<img', feedback)
        self.assertNotIn('<script>', feedback)


if __name__ == '__main__':
    unittest.main()
