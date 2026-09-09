"""Focused source, fallback, contrast and no-egress checks for the prototype."""
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.tags = []
        self.quote = []
        self.in_quote = False
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))
        if tag == 'blockquote':
            self.in_quote = True

    def handle_endtag(self, tag):
        if tag == 'blockquote':
            self.in_quote = False

    def handle_data(self, data):
        if self.in_quote:
            self.quote.append(data)


class StaticTests(unittest.TestCase):
    def test_source_quote_and_fingerprint_are_unchanged(self):
        source = ROOT.parent / 'rainfall.txt'
        baseline = json.loads((ROOT / 'baseline.json').read_text())
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),
                         baseline['prototypes/competition/rainfall.txt'])
        page = Page((ROOT / 'index.html').read_text())
        self.assertEqual(''.join(page.quote), source.read_text().strip())
        self.assertIn('> ' + source.read_text().strip(), (ROOT / 'lesson.md').read_text())

    def test_no_script_fallback_and_local_links(self):
        text = (ROOT / 'index.html').read_text()
        page = Page(text)
        self.assertTrue(any(t == 'div' and a.get('id') == 'controls' and 'hidden' in a
                            for t, a in page.tags))
        self.assertEqual(sum(t == 'table' for t, _ in page.tags), 1)
        self.assertIn('Takeaway:', text)
        for _, attrs in page.tags:
            for attr in ('href', 'src'):
                target = attrs.get(attr)
                if target and not target.startswith('#'):
                    self.assertNotIn('://', target)
                    self.assertTrue((ROOT / target).is_file(), target)

    def test_egress_is_denied_and_no_assessment_surface(self):
        text = (ROOT / 'index.html').read_text()
        page = Page(text)
        csp = next(a['content'] for t, a in page.tags
                   if t == 'meta' and a.get('http-equiv') == 'Content-Security-Policy')
        self.assertIn("connect-src 'none'", csp)
        self.assertIn("form-action 'none'", csp)
        self.assertFalse(any(t in ('form', 'iframe') for t, _ in page.tags))
        code = (ROOT / 'lesson.js').read_text()
        for forbidden in ('fetch(', 'XMLHttpRequest', 'WebSocket', 'localStorage',
                          'sessionStorage', 'indexedDB', 'sendBeacon', 'innerHTML'):
            self.assertNotIn(forbidden, code)

    def test_highlight_contrast(self):
        def luminance(color):
            rgb = [int(color[i:i+2], 16)/255 for i in (0, 2, 4)]
            rgb = [v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in rgb]
            return sum(v*w for v, w in zip(rgb, (.2126, .7152, .0722)))
        css = (ROOT / 'lesson.css').read_text()
        for background in ('ffe66b', 'b7f3c3'):
            self.assertIn('#'+background, css)
            ratio = (luminance(background)+.05)/(luminance('18332d')+.05)
            self.assertGreater(ratio, 7)
            print(f'Highlight #{background} / #18332d: {ratio:.2f}:1')


if __name__ == '__main__':
    unittest.main()
