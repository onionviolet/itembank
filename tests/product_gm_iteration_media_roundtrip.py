#!/usr/bin/env python3
"""Native lesson media reflows, retains authored descriptions and preserves local admission."""
import argparse
from contextlib import contextmanager
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
import model
from fixtures import lesson_capability_corpus as corpus
from course_guidance_journey_roundtrip import served

ALT = 'A fictional curve rises from low water at 04:12 on the left to high water at 10:38 on the right. It describes the shape between turning points, not exact height at every clock time.'
MISSING_ALT = 'A fictional tide gauge has a low mark and a high mark; both describe the same invented water-height scale.'
CREDIT = 'Synthetic chart drawn for this product fixture.'
DERIVATION = 'Handwritten SVG of an invented curve; no external source.'
SVG = b'<svg xmlns="http://www.w3.org/2000/svg" width="960" height="240" viewBox="0 0 960 240"><rect width="960" height="240" fill="#fff"/><path d="M40 195 C220 195 500 45 920 45" fill="none" stroke="#2a5599" stroke-width="6"/><text x="40" y="225" font-size="18">Low at 04:12</text><text x="770" y="30" font-size="18">High at 10:38</text></svg>'


def snapshot(root):
    return {str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in root.rglob('*') if path.is_file()}


@contextmanager
def fixture():
    with tempfile.TemporaryDirectory(prefix='gm-media-') as folder:
        root = Path(folder)
        asset = root / 'plot.svg'
        asset.write_bytes(SVG)
        digest = hashlib.sha256(SVG).hexdigest()
        text = ('# Synthetic local-media teaching\n\n[SEMANTIC-PROFILE: 1]\n\n## MEDIA\n\n'
            f'plot | plot.svg | {CREDIT} | {ALT} | granted | {DERIVATION} | present | sha256:{digest}\n'
            f'unavailable | absent.svg | Synthetic gauge fixture. | {MISSING_ALT} | granted | Invented drawing, no external source. | missing | sha256:{"0" * 64}\n\n'
            '## LESSON\n\n### Reading A Tide Chart\n\n'
            'This invented chart compares two turning points. Its curve describes their intervening shape.\n\n'
            '[MEDIA: plot]\n\n[MEDIA: unavailable]\n\n' + corpus.MEDIA_BANK[corpus.MEDIA_BANK.index('Q1.'):])
        bank = root / 'synthetic_media.md'
        bank.write_text(text, encoding='utf-8')
        subprocess.run([sys.executable, str(ROOT / 'itembank.py'), 'id-assign', str(bank)],
                       check=True, capture_output=True, text=True)
        errors, warnings = model.lint(model.load(str(bank)), lesson=model.parse_lesson(str(bank)), media=model.parse_media(str(bank)))
        assert not errors and not warnings, ([str(e) for e in errors], [str(w) for w in warnings])
        yield root, bank, asset


def request(url):
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return response.status, response.headers.get('Content-Type'), response.read()
    except urllib.error.HTTPError as exc:
        try:
            return exc.code, exc.headers.get('Content-Type'), exc.read()
        finally:
            exc.close()


class MediaHTML(HTMLParser):
    def __init__(self, markup):
        super().__init__()
        self.images, self.descriptions = [], []
        self.in_description = False
        self.depth = 0
        self.feed(markup)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'img':
            self.images.append(attrs)
        if tag == 'details' and attrs.get('class') == 'media-description':
            self.in_description = True
            self.depth = 1
        elif self.in_description and tag == 'details':
            self.depth += 1

    def handle_endtag(self, tag):
        if self.in_description and tag == 'details':
            self.depth -= 1
            if self.depth == 0:
                self.in_description = False

    def handle_data(self, value):
        if self.in_description:
            self.descriptions.append(value)


def check_native():
    with fixture() as (root, bank, asset), tempfile.TemporaryDirectory(prefix='gm-outside-') as outside:
        outside_asset = Path(outside) / 'outside.svg'
        outside_asset.write_bytes(SVG)
        (root / 'outside.svg').symlink_to(outside_asset)
        (root / 'private.txt').write_text('Synthetic private marker, not an image.\n', encoding='utf-8')
        before = snapshot(root)
        with served(root) as url:
            status, _, raw = request(url + 'lesson/synthetic_media')
            assert status == 200
            page = MediaHTML(raw.decode())
            assert len(page.images) == 1 and page.images[0]['alt'] == ALT
            assert page.images[0]['src'] == '/media/synthetic_media/plot.svg'
            assert ALT in ''.join(page.descriptions)
            assert CREDIT in raw.decode() and DERIVATION in raw.decode() and MISSING_ALT in raw.decode()
            assert request(url + 'media/synthetic_media/plot.svg') == (200, 'image/svg+xml', SVG)
            for path in ('media/synthetic_media/outside.svg', 'media/synthetic_media/../outside.svg',
                         'media/synthetic_media/private.txt', 'media/not-admitted/plot.svg'):
                status, _, body = request(url + path)
                assert status == 404 and b'Synthetic private marker' not in body and body != SVG
            assert snapshot(root) == before
            source = bank.read_text()
            assert all(value in source for value in (ALT, CREDIT, DERIVATION, MISSING_ALT))
            asset.unlink()
            changed = snapshot(root)
            assert request(url + 'media/synthetic_media/plot.svg')[0] == 404
            status, _, raw = request(url + 'lesson/synthetic_media')
            assert status == 200 and ALT in ''.join(MediaHTML(raw.decode()).descriptions)
            assert model.parse_media(str(bank))['assets']['plot']['availability'] == 'present'
            assert snapshot(root) == changed
    print('Native media: authored alternative/credit/static meaning, valid local bytes, missing file and containment refusals pass')


def check_browser(output):
    from playwright.sync_api import sync_playwright
    output.mkdir(parents=True, exist_ok=True)
    rows = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel=os.environ.get('ITEMBANK_VISUAL_QA_CHANNEL', 'chrome'), headless=True)
        try:
            for width, scripts, touch in ((1280, True, False), (390, True, False), (320, False, True)):
                with fixture() as (root, bank, asset), served(root) as url:
                    context = browser.new_context(viewport={'width': width, 'height': 900},
                        java_script_enabled=scripts, has_touch=touch, reduced_motion='reduce',
                        color_scheme='dark' if width == 390 else 'light')
                    try:
                        page = context.new_page()
                        remote = []
                        def admitted_request(route):
                            if route.request.url.startswith(url):
                                route.continue_()
                            else:
                                remote.append(route.request.url); route.abort()
                        context.route('**/*', admitted_request)
                        before = snapshot(root)
                        response = page.goto(url + 'lesson/synthetic_media', wait_until='networkidle')
                        assert response.status == 200
                        image = page.locator('#media-plot img')
                        assert image.evaluate('img => img.complete && img.naturalWidth === 960')
                        assert image.get_attribute('alt') == ALT
                        assert image.evaluate('img => img.getBoundingClientRect().width') <= page.locator('#media-plot').evaluate('el => el.getBoundingClientRect().width') + 1
                        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
                        assert page.locator('#media-plot figcaption').inner_text() == CREDIT + '\n' + DERIVATION
                        assert MISSING_ALT in page.locator('#media-unavailable').inner_text()
                        assert not page.locator('#media-unavailable img').count()
                        summary = page.locator('#media-plot .media-description summary')
                        assert summary.evaluate('el => el.getBoundingClientRect().height') >= 44
                        assert summary.evaluate('el => getComputedStyle(el).display') == 'list-item'
                        if touch:
                            summary.tap()
                        else:
                            summary.focus(); page.keyboard.press('Enter')
                        description = page.locator('#media-plot .media-description p')
                        assert description.is_visible() and description.inner_text() == ALT
                        assert snapshot(root) == before and not remote
                        page.screenshot(path=str(output / ('present-%s.png' % width)), full_page=True)
                        asset.unlink()
                        changed = snapshot(root)
                        response = page.reload(wait_until='networkidle')
                        assert response.status == 200 and snapshot(root) == changed and not remote
                        assert image.evaluate('img => img.complete && img.naturalWidth === 0')
                        summary = page.locator('#media-plot .media-description summary')
                        summary.focus(); page.keyboard.press('Enter')
                        assert description.is_visible() and description.inner_text() == ALT
                        assert page.locator('#media-plot figcaption').inner_text() == CREDIT + '\n' + DERIVATION
                        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
                        page.screenshot(path=str(output / ('missing-%s.png' % width)), full_page=True)
                        rows.append({'width': width, 'scripts': scripts, 'touch_emulated': touch,
                            'image_fits': True, 'authored_description_exact': True, 'caption_exact': True,
                            'declared_unavailable_fallback': True, 'actual_missing_file_description': True,
                            'disclosure_marker_native': True, 'min_control_height': 44,
                            'no_remote_requests': True, 'no_durable_mutation': True})
                    finally:
                        context.close()
        finally:
            browser.close()
    (output / 'observations.json').write_text(json.dumps(rows, indent=2) + '\n', encoding='utf-8')
    print('Chrome media: 3 desktop/narrow/static keyboard/touch present and missing-file journeys pass')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--browser', type=Path)
    args = parser.parse_args()
    check_native()
    if args.browser:
        check_browser(args.browser)
