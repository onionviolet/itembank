#!/usr/bin/env python3
"""Guided reading keeps runtime truncation and the complete static source."""
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import model
from surfaces import lesson, lesson_progressive

FIXTURE = ROOT / 'fixtures/lesson_comparison.md'


class ProgressiveTests(unittest.TestCase):
    def page(self, path=FIXTURE, **kwargs):
        return lesson.lesson_page(str(path), model.load(str(path)),
                                  model.parse_lesson(str(path)), **kwargs)

    def test_guided_keeps_static_content_and_opt_in(self):
        before = FIXTURE.read_bytes()
        page = self.page(mode='guided')
        self.assertIn('Next explanation', page)
        self.assertIn('Highlight key wording', page)
        self.assertIn('Static examples', page)
        self.assertIn('id="source-rain-01"', page)
        self.assertNotIn('class="stage" hidden', page)
        self.assertNotIn('Highlight key wording', self.page())
        self.assertEqual(before, FIXTURE.read_bytes())

    def test_show_all_cannot_cross_required_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'bank.md'
            path.write_text(FIXTURE.read_text().replace(
                '> [!EXAMPLE]', '> [!CHECK: q1]\n\n> [!EXAMPLE]'))
            qs = model.load(str(path))
            gate = {'policy': 'required', 'states': {'q1': 'open'},
                    'resolve': lambda cid: qs[0], 'stem': 'bank',
                    'bank': str(path), 'skip': 'off'}
            page = self.page(path, mode='guided', runtime=True, gate=gate)
            self.assertIn('Show all explanations', page)
            self.assertNotIn('Static examples', page)
            self.assertNotIn('id="source-rain-01"', page)
            self.assertNotIn('The inventory identifies the violet tile by its own label.', page)


if __name__ == '__main__':
    if '--serve' in sys.argv:
        from surfaces import daemon
        daemon.serve_scoped(str(ROOT), {'lesson_comparison': str(FIXTURE)}, {},
                            8769, no_open=True,
                            open_path='/lesson/lesson_comparison?view=guided')
    else:
        unittest.main()
