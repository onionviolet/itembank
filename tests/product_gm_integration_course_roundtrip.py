#!/usr/bin/env python3
"""The course frame preserves runtime sittings while consolidating actions."""
import html
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
import unittest
import urllib.parse

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
from course_guidance_journey_roundtrip import fixture, served, start_saved, snapshot, get
from surfaces import session
import runtime


class Links(HTMLParser):
    def __init__(self, markup):
        super().__init__()
        self.links = []
        self.feed(markup)

    def handle_starttag(self, tag, attributes):
        if tag == 'a':
            self.links.append(dict(attributes))


class CourseComposition(unittest.TestCase):
    def read_overview(self, root):
        with served(root) as url:
            before = snapshot(root)
            page = get(url, '/course/synthetic')
            self.assertEqual(snapshot(root), before, 'overview GET changed durable state')
        return page

    def sitting_links(self, page, sitting):
        return [link for link in Links(page).links if urllib.parse.parse_qs(
            urllib.parse.urlsplit(link.get('href', '')).query).get('session') == [sitting]]

    def test_one_primary_resume_and_no_duplicate_course_path_for_alias_entry(self):
        with fixture() as (root, base, banks, meta):
            path, started = start_saved(root, base)
            before = runtime.read_session(str(path))
            page = self.read_overview(root)
            links = self.sitting_links(page, started['session_id'])
            self.assertEqual(sum('data-course-resume' in link for link in links), 1)
            path_section = re.search(r'<section class="overview-path".*?</section>', page, re.S).group()
            self.assertNotIn(started['session_id'], path_section)
            self.assertIn('Explore the lesson', path_section)
            history = re.search(r'<details class="overhaul-saved-sittings"([^>]*)>', page)
            self.assertIsNotNone(history)
            self.assertNotIn('open', history.group(1))
            self.assertIn('<summary id="saved-sittings">', page)
            self.assertNotIn('Current area: Overview', page)
            self.assertEqual(runtime.read_session(str(path)), before)

    def test_other_sittings_and_complete_reports_remain_in_saved_history(self):
        with fixture() as (root, base, banks, meta):
            active_path, active = start_saved(root, base)
            complete_path, complete = start_saved(root, base, mode='exam')
            for _ in range(2):
                session.do_submit(str(complete_path), 'A', None)
            self.assertEqual(runtime.read_session(str(complete_path))['status'], 'complete')
            page = self.read_overview(root)
            self.assertTrue(self.sitting_links(page, active['session_id']))
            report = self.sitting_links(page, complete['session_id'])
            self.assertTrue(any(link['href'].startswith('/report?') for link in report))
            self.assertIn('Saved sittings (2)', page)

    def test_pending_prose_remains_pending_with_its_original_sitting(self):
        with fixture() as (root, base, banks, meta):
            path, started = start_saved(root, base, 'pending', 'practice', 1)
            wording = 'PRIVATE synthetic explanation awaiting review'
            session.do_submit(str(path), wording, None)
            page = self.read_overview(root)
            self.assertIn('data-course-guidance="pending"', page)
            self.assertIn('no settled mark', page)
            self.assertNotIn(wording, page)
            self.assertTrue(self.sitting_links(page, started['session_id']))
            self.assertIsNone(runtime.read_session(str(path))['responses'][0]['score'])

    def test_changed_bank_keeps_recovery_and_refuses_a_stale_resume(self):
        with fixture() as (root, base, banks, meta):
            path, started = start_saved(root, base)
            bank = Path(base, 'symbols.md')
            bank.write_text(bank.read_text() + '\n')
            page = self.read_overview(root)
            self.assertIn('data-course-guidance="unavailable"', page)
            self.assertIn('unavailable', html.unescape(page).lower())
            self.assertFalse(self.sitting_links(page, started['session_id']))
            self.assertEqual(runtime.read_session(str(path))['cursor'], 0)


if __name__ == '__main__':
    unittest.main()
