#!/usr/bin/env python3
"""Actual impact task links retain the explicit admitted source-review origin."""
import argparse
import hashlib
import json
import re
from pathlib import Path
import sys
import unittest
import urllib.parse

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
import journal
from course_guidance_journey_roundtrip import fixture, get, served, snapshot, start_saved
from course_context_journey_roundtrip import Links
import runtime


def changed_source(base, info):
    row = journal.read_registry(base)[info['source_id']]
    (base / row['path']).write_text('WITHHELD SOURCE CHANGE FOR INTEGRATION')


def impact_tasks(markup, source_id):
    block = markup.split('aria-label="Changed source impact"', 1)[1].split('</aside>', 1)[0]
    links = Links(block).links
    tasks = {}
    for row in links:
        href = row.get('href', '')
        target = urllib.parse.urlsplit(href)
        if target.path.startswith('/lesson/'):
            kind = 'lesson'
        elif '/reading/' in target.path:
            kind = 'reading'
        elif target.path.endswith('/map'):
            kind = 'map'
        elif target.path.startswith('/quiz/'):
            kind = 'practice'
        else:
            continue
        if kind not in tasks:
            assert urllib.parse.parse_qs(target.query).get('return_source') == [source_id], href
            tasks[kind] = href
    assert set(tasks) == {'reading', 'lesson', 'map', 'practice'}, tasks
    return tasks


class TextLinks(Links):
    def __init__(self, markup):
        self.current = None
        super().__init__(markup)

    def handle_starttag(self, tag, attributes):
        super().handle_starttag(tag, attributes)
        if tag == 'a':
            self.current = self.links[-1]
            self.current['text'] = ''

    def handle_data(self, data):
        if self.current is not None:
            self.current['text'] += data

    def handle_endtag(self, tag):
        if tag == 'a':
            self.current = None


def back_href(markup):
    return next(link['href'] for link in TextLinks(markup).links
                if 'Back to source review' in link.get('text', ''))


class SourceOriginJourney(unittest.TestCase):
    def test_actual_emitted_tasks_return_after_restart_without_submission(self):
        with fixture() as (root, base, banks, info):
            sittings = prepare_sittings(root, base)
            changed_source(base, info)
            before = snapshot(root)
            tasks = None
            for _ in range(2):
                with served(root) as url:
                    source_page = get(url, '/course/synthetic/sources?source=0')
                    self.assertNotIn('WITHHELD SOURCE CHANGE FOR INTEGRATION', source_page)
                    current = impact_tasks(source_page, info['source_id'])
                    if tasks is not None:
                        self.assertEqual(current, tasks)
                    tasks = current
                    for kind, href in tasks.items():
                        page = get(url, href)
                        self.assertNotIn('WITHHELD SOURCE CHANGE FOR INTEGRATION', page)
                        back = back_href(page)
                        parsed = urllib.parse.urlsplit(back)
                        self.assertTrue(parsed.path.endswith('/sources'), (kind, back))
                        self.assertEqual(urllib.parse.parse_qs(parsed.query), {'source': ['0']})
                        self.assertEqual(parsed.fragment, 'source-0')
                        returned = get(url, back)
                        self.assertIn('aria-label="Changed source impact"', returned)
                        self.assertNotIn('WITHHELD SOURCE CHANGE FOR INTEGRATION', returned)
                assert_no_learning_mutation(root, before, sittings)


def prepare_sittings(root, base):
    result = {}
    for stem, count in (('pending', 1), ('symbols', 2)):
        path, _started = start_saved(root, base, stem=stem, count=count)
        result[str(path.relative_to(root))] = runtime.read_session(str(path))
    return result


def assert_no_learning_mutation(root, before, sittings):
    after = snapshot(root)
    allowed = set(sittings) | {name + '.lock' for name in sittings}
    changed = {name for name in set(before) | set(after) if before.get(name) != after.get(name)}
    assert changed <= allowed, changed
    for name, initial in sittings.items():
        current = runtime.read_session(str(root / name))
        for key in ('cursor', 'responses', 'items', 'session_id', 'status', 'mode', 'bank'):
            assert current[key] == initial[key], (name, key)


def browser_checks(output):
    from playwright.sync_api import sync_playwright
    output.mkdir(parents=True, exist_ok=True)
    observations = []
    source_paths = ('surfaces/daemon.py', 'surfaces/reading_desk.py',
                    'surfaces/lesson.py', 'surfaces/course_workbench.py')
    hashes = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in source_paths}
    with fixture() as (root, base, banks, info):
        sittings = prepare_sittings(root, base)
        changed_source(base, info)
        before = snapshot(root)
        with sync_playwright() as pw:
            browser = pw.chromium.launch(channel='chrome', headless=True)
            try:
                for restart in range(2):
                    with served(root) as url:
                        variants = ((1280, True), (390, True), (320, True), (320, False)) if restart == 0 else ((320, False),)
                        for width, scripts in variants:
                            context = browser.new_context(viewport={'width': width, 'height': 900},
                                java_script_enabled=scripts, reduced_motion='reduce',
                                color_scheme='dark' if width == 390 else 'light')
                            page = context.new_page()
                            errors = []
                            page.on('pageerror', lambda error: errors.append(str(error)))
                            source_route = url + 'course/synthetic/sources?source=0'
                            page.goto(source_route)
                            tasks = impact_tasks(page.content(), info['source_id'])
                            for kind, href in tasks.items():
                                page.goto(source_route)
                                label = {'reading': 'Inspect assigned reading',
                                         'lesson': 'Open linked lesson',
                                         'practice': 'Open linked practice'}.get(kind)
                                link = (page.locator('.course-source-impact a[href]').filter(has_text=label)
                                        if label else page.locator('.course-source-impact a[href*="/map"]'))
                                link.first.focus()
                                with page.expect_navigation(wait_until='networkidle'):
                                    page.keyboard.press('Enter')
                                page.reload(wait_until='networkidle')
                                self_back = page.get_by_role('link', name=re.compile(r'Back to source review$'))
                                assert self_back.is_visible(), (kind, page.url)
                                assert 'WITHHELD SOURCE CHANGE FOR INTEGRATION' not in page.content()
                                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
                                filename = '%s-%d-%s-restart%d.png' % (kind, width, 'js' if scripts else 'static', restart)
                                page.screenshot(path=str(output / filename))
                                self_back.focus()
                                with page.expect_navigation(wait_until='networkidle'):
                                    page.keyboard.press('Enter')
                                assert '/sources?source=0' in page.url and page.url.endswith('#source-0'), page.url
                                assert 'WITHHELD SOURCE CHANGE FOR INTEGRATION' not in page.content()
                                assert not errors, errors
                                observations.append({'task': kind, 'width': width, 'scripts': scripts,
                                                     'restart': restart, 'screenshot': filename})
                            context.close()
                        assert_no_learning_mutation(root, before, sittings)
            finally:
                browser.close()
    assert hashes == {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in source_paths}
    (output / 'result.json').write_text(json.dumps({'inputs': hashes, 'checks': observations,
                                                 'course_notes_evidence_unchanged': True,
                                                 'no_submission_or_cursor_advance': True}, indent=2) + '\n')
    print('Explicit source-origin Chrome checks: %d passed.' % len(observations))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--browser-shots', type=Path)
    args, remaining = parser.parse_known_args()
    if args.browser_shots:
        browser_checks(args.browser_shots)
    else:
        unittest.main(argv=[sys.argv[0]] + remaining)
