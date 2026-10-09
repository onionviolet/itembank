#!/usr/bin/env python3
"""Live checkpoint outlines cannot move the band or expose locked headings."""
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
from surfaces import lesson
import product_gm_ui_lesson_roundtrip as fixture


class GatedOutline(unittest.TestCase):
    def test_live_second_section_outline_stays_after_band_and_names_visible_sections(self):
        case = fixture.LessonPresentation('test_outline_only_names_rendered_headings')
        case.setUp()
        self.addCleanup(case.doCleanups)
        source = Path(case.path)
        text = source.read_text()
        source.write_text(text.replace('### Second\n\n',
            '### Second\n\n> [!CHECK: q1]\n\nLOCKED TAIL SENTINEL\n\n', 1))
        case.qs = fixture.load(case.path)
        case.parsed = fixture.parse_lesson(case.path)
        gate = {'policy': 'required', 'states': {'q1': 'open'},
                'resolve': lambda cid: case.qs[0], 'bank': case.path,
                'stem': 'fiction', 'skip': 'off'}
        opened = lesson.lesson_page(case.path, case.qs, case.parsed,
                                    runtime=True, gate=gate)
        nav = re.search(r'<nav class="reader-nav".*?</nav>', opened, re.S)
        self.assertIsNotNone(nav)
        self.assertEqual(nav.group().count('class="nav-n"'), 2)
        self.assertIn('href="#first"', nav.group())
        self.assertIn('href="#second"', nav.group())
        self.assertNotIn('href="#third"', nav.group())
        self.assertNotIn('LOCKED TAIL SENTINEL', opened)
        self.assertNotIn('Additional material', opened)
        self.assertGreater(nav.start(), opened.index('<section class="gate">'))

        def before_band(page):
            markers = ('<section class="callout callout-check">', '<section class="gate">')
            for marker in markers:
                if marker in page:
                    return page.split(marker, 1)[0]
            self.fail('The checkpoint band is missing.')

        inert = lesson.lesson_page(case.path, case.qs, case.parsed, runtime=True)
        self.assertEqual(before_band(opened), before_band(inert))
        cleared = lesson.lesson_page(case.path, case.qs, case.parsed,
            runtime=True, gate=dict(gate, states={'q1': 'cleared'}))
        self.assertEqual(before_band(opened), before_band(cleared))
        self.assertIn('href="#third"', cleared)
        self.assertIn('LOCKED TAIL SENTINEL', cleared)


if __name__ == '__main__':
    unittest.main()
