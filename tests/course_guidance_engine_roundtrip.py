#!/usr/bin/env python3
"""Truthful live counts and safe next activity over synthetic saved sittings."""
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
import urllib.parse
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tests'))

import course
import evidence
import graph
import journal
import model
import runtime
from surfaces import course_workbench as cw, session
import reading_declarations_roundtrip as declarations


def snapshot(root):
    return {str(path.relative_to(root)): path.read_bytes()
            for path in Path(root).rglob('*') if path.is_file()}


def seed(root, prose=False, staged=False):
    base = Path(root) / 'course'
    base.mkdir()
    course.create_course(str(base), 'Synthetic guidance course', 'human', 'test')
    source = base / 'source.md'
    source.write_text('# Source\n\nA synthetic explanation remains source-backed.\n', encoding='utf-8')
    record = journal.op_link(str(base), 'source', 'source.md', 'human', 'test',
                             rights={'read': 'granted', 'transform': 'granted'})
    journal.op_adopt(str(base), record['object_id'], record['fingerprint'], 'human', 'test')
    sample = (ROOT / 'fixtures/sample_bank.md').read_text(encoding='utf-8')
    if staged:
        text = (ROOT / 'prototypes/audit-question-families/fixtures/bank.md').read_text(encoding='utf-8')
        text = text[:text.index('Q3.')]
        case = {'version': 1, 'activity_id': 'synthetic:counter-staged',
                'stimulus': 'A fictional counter starts at 3 and adds 2 once.',
                'children': ['a200000000000001', 'a200000000000002'],
                'order': ['answer', 'reason']}
        text = 'STAGED-CASES: ' + json.dumps([case]) + '\n' + text
    else:
        text = sample[sample.index('Q1.'):sample.index('Q2.')]
        text += (sample[sample.index('Q6.'):].replace('Q6.', 'Q2.', 1) if prose else
                 sample[sample.index('Q2.'):sample.index('Q3.')])
        text = ('# Synthetic guidance bank\n\n## LESSON\n\n### Source explanation\n\n'
                'Synthetic source-backed explanation. [Source: source.md]\n\n' + text)
    bank = base / 'guidance_bank.md'
    bank.write_text(text, encoding='utf-8')
    bank_record = journal.op_link(str(base), 'bank', bank.name, 'human', 'test')
    journal.op_adopt(str(base), bank_record['object_id'], bank_record['fingerprint'], 'human', 'test')
    read = course.read_course(str(base))
    doc = read['doc']
    graph.add_source(doc, record['object_id'], 'Synthetic source')
    for q in model.load(str(bank)):
        if q['objective'] not in {row['id'] for row in doc['objectives']}:
            graph.add_objective(doc, 'Explain the synthetic concept', objective_id=q['objective'])
            graph.add_binding(doc, 'treatment', q['objective'], record['object_id'],
                              treatment_kind='guided-lesson', locator=bank.name,
                              state='covered', confidence='high', rights_snapshot='granted')
            graph.add_binding(doc, 'treatment', q['objective'], record['object_id'],
                              treatment_kind='practice', locator=bank.name,
                              state='covered', confidence='high', rights_snapshot='granted')
    course.write_course(str(base), doc, read['fingerprint'], 'human', 'test')
    return base, bank, record


class CountStates(unittest.TestCase):
    def test_absent_empty_unreadable_and_no_writes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            log = Path(evidence.log_path(temp))
            before = snapshot(root)
            self.assertEqual(evidence.course_counts(log), {
                'responses': 0, 'marks': 0, 'sessions': 0, 'events': 0,
                'state': 'empty', 'complete': True, 'issues': []})
            self.assertEqual(snapshot(root), before)
            log.parent.mkdir()
            log.write_text('\n', encoding='utf-8')
            self.assertEqual(evidence.course_counts(log)['state'], 'empty')
            before = snapshot(root)
            with patch('builtins.open', side_effect=PermissionError('private path unavailable')):
                result = evidence.course_counts(log)
            self.assertEqual(result['state'], 'unavailable')
            self.assertFalse(result['complete'])
            self.assertTrue(all(result[name] is None for name in ('responses', 'marks', 'sessions', 'events')))
            self.assertNotIn('private path', json.dumps(result))
            self.assertEqual(snapshot(root), before)

    def test_partial_future_unknown_and_retractions_use_the_reader(self):
        with tempfile.TemporaryDirectory() as temp:
            log = Path(evidence.log_path(temp))
            q = {'id': 'Q1', 'type': 'mc', 'objective': 'synthetic:counts', 'item_id': 'count-item'}
            response = evidence.response_event('sitting', q, 'PRIVATE ANSWER', False, 'practice', 1, 'bank.md')
            evidence.append_event(str(log), response)
            mark = evidence.mark_event('sitting', 'count-item', 'Q1', response['event_id'], True)
            evidence.append_event(str(log), mark)
            ready = evidence.course_counts(log)
            self.assertEqual([ready[k] for k in ('responses', 'marks', 'sessions', 'events')], [1, 1, 1, 2])
            self.assertEqual(ready['state'], 'ready')
            future = dict(response, schema_version=evidence.EVENT_SCHEMA_VERSION + 1, event_id='future')
            unknown = dict(response, event_type='PRIVATE UNKNOWN TYPE', event_id='unknown')
            with log.open('a', encoding='utf-8') as handle:
                handle.write('torn PRIVATE ANSWER\n[]\n' + json.dumps(future) + '\n' + json.dumps(unknown) + '\n')
            before = snapshot(Path(temp))
            with patch('builtins.print') as printed:
                partial = evidence.course_counts(log)
            printed.assert_not_called()
            self.assertEqual(partial['state'], 'incomplete')
            self.assertFalse(partial['complete'])
            self.assertEqual(partial['responses'], 1)
            self.assertEqual(len(partial['issues']), 4)
            self.assertNotIn('PRIVATE', json.dumps(partial))
            self.assertEqual(snapshot(Path(temp)), before)
            evidence.append_event(str(log), evidence.retraction_event(response['event_id'], 'Synthetic withdrawal'))
            self.assertEqual(evidence.course_counts(log)['responses'], 0)
            # A compensating record may appear before the record it retracts.
            other = Path(temp) / 'forward.jsonl'
            other.write_text(json.dumps(evidence.retraction_event(response['event_id'], 'Imported order')) + '\n' +
                             json.dumps(response) + '\n', encoding='utf-8')
            self.assertEqual(evidence.course_counts(other)['events'], 0)
            self.assertEqual(evidence.course_counts(other)['state'], 'empty')


class Guidance(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def prepare(self, **kwargs):
        self.base, self.bank, self.source = seed(self.root, **kwargs)
        self.banks = [('guidance_bank', str(self.bank))]
        self.attempt = self.root / '_attempts' / 'session_guidance.json'

    def start(self, mode='practice', **spec):
        return session.do_start(str(self.bank), {'count': 2, 'seed': 0, 'selection_mode': 'exam', **spec},
                                mode, str(self.attempt), False)

    def guidance(self, banks=None):
        # Session selection may build a disposable index. This read must not
        # require it or recreate it when it is absent.
        for path in self.root.rglob('evidence_index.sqlite3'):
            path.unlink()
        before = snapshot(self.root)
        payload = cw.course_guidance(str(self.root), str(self.base),
                                     course.read_course(str(self.base))['doc'], self.banks if banks is None else banks)
        self.assertEqual(snapshot(self.root), before, 'a recommendation mutated accepted state')
        self.assertEqual(set(payload) - {'resume_href'}, {'kind', 'title', 'reason', 'href', 'objective'})
        for secret in ('PRIVATE', 'CORRECT:', 'WHY BEST', '"answer":', '"score":'):
            self.assertNotIn(secret, json.dumps(payload))
        self.assertFalse(list(self.root.rglob('evidence_index.sqlite3')))
        return payload

    def test_source_first_then_miss_resume_correction_and_retraction(self):
        self.prepare()
        initial = self.guidance()
        self.assertEqual(initial['kind'], 'start')
        self.assertTrue(initial['href'].startswith('/lesson/guidance_bank?'))
        started = self.start()
        session.do_submit(str(self.attempt), 'A', None)
        missed = self.guidance()
        self.assertEqual(missed['kind'], 'review')
        self.assertTrue(missed['href'].startswith('/lesson/guidance_bank?'))
        query = urllib.parse.parse_qs(urllib.parse.urlsplit(missed['href']).query)
        self.assertEqual(query['return'], [missed['resume_href']])
        self.assertEqual(urllib.parse.parse_qs(urllib.parse.urlsplit(missed['resume_href']).query)['session'],
                         [started['session_id']])
        accepted = session.do_submit(str(self.attempt), 'B', None)
        self.assertTrue(accepted['accepted'])
        self.assertEqual(self.guidance()['kind'], 'resume', 'a corrected miss stayed unresolved')
        corrected = [row for row in evidence.live_events(evidence.log_path(str(self.base)))
                     if row['event_type'] == 'response'][-1]['event_id']
        evidence.append_event(evidence.log_path(str(self.base)), evidence.retraction_event(corrected, 'Synthetic correction undone'))
        self.assertEqual(self.guidance()['kind'], 'review')

    def test_real_reading_declaration_has_no_sitting_and_starts_with_the_source(self):
        fixture = declarations.ReadingDeclarations('test_restart_full_history_replay')
        fixture.setUp()
        try:
            occurrence = fixture.create()['occurrence']
            fixture.declare(fixture.confirmation(occurrence))
            root = Path(fixture.root)
            before = snapshot(root)
            read = fixture.read()
            payload = cw.course_guidance(fixture.root, fixture.base, read['doc'], [])
            counts = evidence.course_counts(evidence.log_path(fixture.base))
            self.assertEqual(counts['sessions'], 0)
            self.assertEqual(counts['events'], 1)
            self.assertEqual(payload['kind'], 'start')
            self.assertIn('/reading/', payload['href'], payload)
            self.assertNotIn('resume_href', payload)
            self.assertEqual(snapshot(root), before)
        finally:
            fixture.doCleanups()

    def test_orphan_response_hint_and_mark_remain_unavailable(self):
        self.prepare()
        q = model.load(str(self.bank))[0]
        response = evidence.response_event('orphan', q, 'A', False, 'practice', 1, self.bank.name)
        mark = evidence.mark_event('orphan', q.get('item_id'), q['id'], response['event_id'], False)
        hint = dict(response, event_type='hint')
        log = Path(evidence.log_path(str(self.base)))
        log.parent.mkdir(exist_ok=True)
        for event in (response, hint, mark):
            log.write_text(json.dumps(event) + '\n', encoding='utf-8')
            self.assertEqual(self.guidance()['kind'], 'unavailable')

    def test_pending_mark_correction_and_mark_retraction(self):
        self.prepare(prose=True)
        started = self.start(count=1, type_counts={'short': 1})
        session.do_submit(str(self.attempt), 'PRIVATE prose response', None)
        self.assertEqual(self.guidance()['kind'], 'pending')
        event = next(row for row in evidence.live_events(evidence.log_path(str(self.base))) if row['event_type'] == 'response')
        mark = evidence.mark_event(started['session_id'], event['item_id'], event['item_ref'], event['event_id'], False)
        evidence.append_event(evidence.log_path(str(self.base)), mark)
        self.assertEqual(self.guidance()['kind'], 'review')
        correction = evidence.mark_event(started['session_id'], event['item_id'], event['item_ref'], event['event_id'], True)
        evidence.append_event(evidence.log_path(str(self.base)), correction)
        self.assertEqual(self.guidance()['kind'], 'resume')
        evidence.append_event(evidence.log_path(str(self.base)), evidence.retraction_event(correction['event_id'], 'Corrected mark undone'))
        self.assertEqual(self.guidance()['kind'], 'review')
        evidence.append_event(evidence.log_path(str(self.base)), evidence.retraction_event(mark['event_id'], 'Original mark undone'))
        self.assertEqual(self.guidance()['kind'], 'pending')

    def test_formal_feedback_stays_withheld_and_diagnostic_fails_closed(self):
        self.prepare()
        self.start(mode='exam')
        session.do_submit(str(self.attempt), 'A', None)
        held = self.guidance()
        self.assertEqual(held['kind'], 'resume')
        self.assertIsNone(held['objective'])
        self.assertNotIn('miss', held['reason'])
        self.attempt.unlink()
        self.start(mode='diagnostic')
        session.do_submit(str(self.attempt), 'A', None)
        diagnostic = self.guidance()
        self.assertEqual(diagnostic['kind'], 'unavailable')
        self.assertIsNone(diagnostic['objective'])
        self.assertNotIn('miss', diagnostic['reason'])

    def test_unsafe_binding_rights_and_stale_bank_have_no_explanation(self):
        self.prepare()
        self.start()
        session.do_submit(str(self.attempt), 'A', None)
        record = journal.read_registry(str(self.base))[self.source['object_id']]
        journal.op_grant_rights(str(self.base), record['object_id'], {'transform': 'denied'},
                                record['fingerprint'], 'human', 'test')
        refused = self.guidance()
        self.assertEqual(refused['kind'], 'review')
        self.assertIn('/evidence#', refused['href'])
        self.assertEqual(self.guidance(self.banks + [('alias', str(self.bank))])['kind'], 'unavailable')
        self.bank.write_text(self.bank.read_text(encoding='utf-8') + '\n', encoding='utf-8')
        future = evidence.utc_now()
        os.utime(self.bank, (os.path.getmtime(self.bank) + 5, os.path.getmtime(self.bank) + 5))
        self.assertEqual(self.guidance()['kind'], 'unavailable', future)

    def test_malformed_history_cannot_support_a_precise_claim(self):
        self.prepare()
        self.start()
        session.do_submit(str(self.attempt), 'A', None)
        with open(evidence.log_path(str(self.base)), 'a', encoding='utf-8') as handle:
            handle.write('PRIVATE broken tail\n')
        payload = self.guidance()
        self.assertEqual(payload['kind'], 'unavailable')
        self.assertIsNone(payload['objective'])
        self.assertNotIn('missed', payload['reason'])
        with patch.object(evidence, 'live_events', side_effect=OSError('PRIVATE read failure')):
            self.assertEqual(self.guidance()['kind'], 'unavailable')

    def test_damaged_json_field_types_produce_failure_views(self):
        self.prepare()
        self.start()
        result = session.do_submit(str(self.attempt), 'A', None)
        self.assertTrue(result['accepted'])
        log = Path(evidence.log_path(str(self.base)))
        valid_bytes = log.read_bytes()
        response = next(row for row in evidence.live_events(str(log)) if row['event_type'] == 'response')
        for changes in ({'event_id': ['unhashable']}, {'session_id': ['unhashable']},
                        {'event_type': 'retraction', 'retracts': ['unhashable']}):
            log.write_bytes(valid_bytes + (json.dumps(dict(response, **changes)) + '\n').encode('utf-8'))
            before = snapshot(self.root)
            history = cw.review_history(str(self.root), str(self.base),
                                        course.read_course(str(self.base))['doc'], self.banks)
            self.assertEqual(history['state'], 'error')
            self.assertEqual(self.guidance()['kind'], 'unavailable')
            self.assertEqual(snapshot(self.root), before)

    def test_staged_feedback_is_held_until_the_whole_case_closes(self):
        self.prepare(staged=True)
        self.start()
        activity = session.do_next(str(self.attempt))['activity']
        action = {key: activity[key] for key in ('activity_id', 'child_id', 'submission_token')}
        session.do_action(str(self.attempt), dict(action, kind='submit', answer='B'))
        history = cw.review_history(str(self.root), str(self.base), course.read_course(str(self.base))['doc'], self.banks)
        self.assertEqual(history['rows'][0]['status'], 'feedback-withheld')
        self.assertEqual(history['rows'][0]['context_links'], [])
        self.assertEqual(self.guidance()['kind'], 'resume')

    def test_newest_item_miss_wins_after_interleaved_updates_and_ties(self):
        self.prepare()
        def row(item, stamp):
            return {'artifact': 'guidance_bank', 'item_id': item, 'item_ref': item,
                    'timestamp': stamp, 'status': 'missed', 'mode': 'practice',
                    'objective': 'synthetic:' + item, 'session_id': 'closed',
                    'context_links': []}
        older = '2026-09-01T12:00:00+00:00'
        newer = '2026-09-01T12:00:01+00:00'
        # Item A's first insertion precedes B, but A's later retry is newest.
        history = {'state': 'available', 'session_state': 'complete', 'sessions': (),
                   'rows': [row('A', older), row('B', older), row('A', newer)]}
        with patch.object(cw, 'review_history', return_value=history):
            self.assertEqual(self.guidance()['objective'], 'synthetic:A')

        # Equal timestamps preserve original log order as the tie-breaker.
        history['rows'][-1]['timestamp'] = older
        with patch.object(cw, 'review_history', return_value=history):
            self.assertEqual(self.guidance()['objective'], 'synthetic:A')

    def test_due_practice_uses_existing_retention_and_current_binding(self):
        self.prepare()
        objective = model.load(str(self.bank))[0]['objective']
        for index in range(3):
            self.attempt = self.root / '_attempts' / ('session_due_%d.json' % index)
            self.start(count=1, objective=objective)
            session.do_submit(str(self.attempt), 'B', None)
        cutoff = (datetime.now(timezone.utc) + timedelta(days=14)).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        original = cw.review_history
        report = original(str(self.root), str(self.base), course.read_course(str(self.base))['doc'], self.banks, cutoff=cutoff)
        self.assertEqual(report['due']['objectives'][objective]['settled'], 3)
        self.assertTrue(report['due']['objectives'][objective]['due'], report['due']['objectives'][objective])
        self.assertIsNotNone(cw._due_practice_activity(str(self.base), course.read_course(str(self.base))['doc'], self.banks, report['due']),
                             cw._current_safe_bindings(str(self.base), course.read_course(str(self.base))['doc']))
        with patch.object(cw, 'review_history', side_effect=lambda *args: original(*args, cutoff=cutoff)):
            suggested = self.guidance()
        self.assertEqual(suggested['kind'], 'due', suggested)
        self.assertEqual(suggested['objective'], objective)
        self.assertIn('3 settled response', suggested['reason'])
        self.assertEqual(urllib.parse.parse_qs(urllib.parse.urlsplit(suggested['href']).query),
                         {'bank': ['guidance_bank'], 'objective': [objective]})
        with patch.object(cw, '_current_safe_bindings', return_value=[]), \
                patch.object(cw, 'review_history', side_effect=lambda *args: original(*args, cutoff=cutoff)):
            self.assertEqual(self.guidance()['kind'], 'start')

    def test_due_work_never_displaces_selected_sitting_or_pending_review(self):
        self.prepare()
        self.start()
        history = cw.review_history(str(self.root), str(self.base), course.read_course(str(self.base))['doc'], self.banks)
        objective = model.load(str(self.bank))[0]['objective']
        history['due'] = {'due_order': [{'objective': objective}],
                          'objectives': {objective: {'due': True, 'settled': 1}}}
        with patch.object(cw, 'review_history', return_value=history):
            self.assertEqual(self.guidance()['kind'], 'resume')
        history['sessions'] = ()
        history['rows'] = [{'artifact': 'guidance_bank', 'item_ref': 'Q1', 'item_id': 'pending',
                            'timestamp': datetime.now(timezone.utc).isoformat(), 'status': 'pending',
                            'objective': objective, 'session_id': 'closed'}]
        with patch.object(cw, 'review_history', return_value=history):
            self.assertEqual(self.guidance()['kind'], 'pending')


if __name__ == '__main__':
    unittest.main()
