#!/usr/bin/env python3
"""Practice entry: loose banks stay reachable from the desk, and the course
Practice tab leads with practice rather than a button leading away from it."""
from pathlib import Path
import re
import shutil
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
from course_guidance_journey_roundtrip import fixture, served, snapshot, get


class DeskLooseBanks(unittest.TestCase):
    def test_loose_bank_gets_practice_and_study_links_and_course_banks_do_not(self):
        with fixture() as (root, base, banks, meta):
            shutil.copy(ROOT / 'fixtures' / 'subject_loop_math.md', root / 'loose_math.md')
            before = snapshot(root)
            with served(root) as url:
                page = get(url, '/')
                self.assertEqual(snapshot(root), before, 'desk GET changed durable state')
                loose = re.findall(r'data-loose-bank="([^"]+)"', page)
                self.assertEqual(loose, ['loose_math'])
                self.assertIn('href="/quiz/loose_math?mode=practice"', page)
                self.assertIn('href="/study/loose_math"', page)
                self.assertIn('href="/banks"', page)
                self.assertIn('Synthetic reading', page)
                quiz = get(url, '/quiz/loose_math?mode=practice')
                self.assertNotIn('data-loose-bank', quiz)

    def test_practice_tab_leads_with_practice_when_advice_is_only_start(self):
        with fixture() as (root, base, banks, meta):
            with served(root) as url:
                courses = get(url, '/courses')
                course = re.search(r'href="(/course/[0-9a-f]+)"', courses).group(1)
                page = get(url, course + '/practice')
            self.assertNotIn('class="course-guidance"', page)
            hint = page.index('data-course-guidance="start"')
            self.assertLess(page.index('/quiz/symbols'), hint)
            self.assertIn('Start with the source</a> first.', page)

    def test_no_section_when_every_bank_is_in_a_course(self):
        with fixture() as (root, base, banks, meta):
            with served(root) as url:
                page = get(url, '/')
            self.assertNotIn('data-loose-bank', page)
            self.assertNotIn('loose-banks-title', page)


if __name__ == '__main__':
    unittest.main()
