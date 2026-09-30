#!/usr/bin/env python3
"""Working-area composition retains native controls and authority boundaries."""
import sys
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from model import load, parse_lesson
from runtime import public_item
from surfaces import lesson, quiz, quiz_page, reading_desk


class Elements(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.rows = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        self.rows.append((tag, dict(attrs)))


def reading_page():
    row = {'occurrence_id': 'synthetic-reading', 'revision_id': 'revision-one',
           'preparation_mode': 'read', 'purpose': 'Compare two invented systems.',
           'source_ref': {'locator': 'Invented source, lines 1-4'}}
    view = {'occurrence': row, 'placements': {'synthetic-reading': {'title': 'Invented systems'}},
            'occurrences': [row], 'reading_state': {'state': 'not-reported'},
            'notes': [{'learner_wording': 'Saved wording stays separate.',
                       'anchor_state': 'current', 'owner': 'learner'}],
            'note_error': None, 'availability': {'state': 'available'},
            'content': 'A fictional source.\n\n一个例子。 ' + 'Compare this system carefully. ' * 25}
    return reading_desk.render('synthetic', {'fingerprint': 'base'},
                               row['occurrence_id'], row['revision_id'], view)


class Workspace(unittest.TestCase):
    def test_reading_source_notes_and_recovery_are_distinct(self):
        source = reading_page()
        rows = Elements(source).rows
        by_id = {a['id']: (tag, a) for tag, a in rows if 'id' in a}
        self.assertEqual(by_id['note'][0], 'textarea')
        self.assertEqual(by_id['source-content'][0], 'div')
        self.assertEqual(by_id['saved-notes'][0], 'div')
        self.assertIn('disabled', by_id['save-note'][1])
        self.assertIn('Saved wording stays separate.', source)
        self.assertIn('Unsaved draft', source)
        self.assertIn('The source range is readable here.', source)
        self.assertTrue(any(tag == 'aside' and a.get('aria-label') == 'Private source notes'
                            for tag, a in rows))
        self.assertTrue(any(tag == 'a' and a.get('aria-current') == 'page' for tag, a in rows))

    def test_native_answers_and_failed_submission_values_survive(self):
        for q in load(str(ROOT / 'fixtures/sample_bank.md')):
            item = public_item(q)
            source = quiz_page.baseline_for({'session_id': 'same-sitting', 'item': item},
                                            {}, '/answer/same-sitting', {'submit': 'token'},
                                            prefill={'answer': ['Keep my draft'], 'option': ['B']})
            rows = Elements(source).rows
            forms = [a for tag, a in rows if tag == 'form' and 'data-answer-form' in a]
            self.assertEqual(forms[0]['action'], '/answer/same-sitting')
            self.assertTrue(any(a.get('name') == 'form_token' and a.get('value') == 'token'
                                for _, a in rows))
            self.assertTrue(any(a.get('data-session-id') == 'same-sitting' for _, a in rows))
            self.assertTrue(any(a.get('role') == 'status' for _, a in rows))
            if q.get('why'):
                self.assertNotIn(q['why'], source)
            if item['type'] == 'short':
                self.assertIn('Keep my draft', source)
        short = {'id': 'prose', 'type': 'short', 'stem': 'Explain the invented process.'}
        pending = quiz_page.baseline_for({'session_id': 'same-sitting', 'item': short},
                    {}, '/answer', {'submit': 'token'}, flash={'action': 'defer_feedback'})
        self.assertIn('waiting on a mark', pending)
        self.assertNotIn('Correct.', pending)

    def test_lesson_and_served_question_keep_content_anchors(self):
        path = str(ROOT / 'fixtures/lesson_bank.md')
        source = lesson.lesson_page(path, load(path), parse_lesson(path))
        rows = Elements(source).rows
        self.assertTrue(any(a.get('id') == 'lesson-content' for _, a in rows))
        self.assertIn('overhaul-lesson', source)
        _, served = quiz.page_for(path, load(path), serve=True, bank_stem='synthetic')
        self.assertIn('<div id="host"></div>', served)
        self.assertTrue(any(tag == 'main' and a.get('aria-label') == 'Active question'
                            for tag, a in Elements(served).rows))
        self.assertNotIn('const Q =', served)


if __name__ == '__main__':
    unittest.main()
