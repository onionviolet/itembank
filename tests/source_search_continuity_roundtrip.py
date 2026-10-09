#!/usr/bin/env python3
"""Exact search occurrence navigation, current-admission recovery and reflow."""
import argparse
from contextlib import contextmanager
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
import unittest
import urllib.parse

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
import journal
from surfaces import course_source_search as search, research_context
import product_gm_parity_search_roundtrip as synthetic
from context_help_native_roundtrip import native
from course_source_search_native_roundtrip import post
from course_source_search_roundtrip import tree


class Forms(HTMLParser):
    def __init__(self, markup):
        super().__init__()
        self.forms, self.current, self.in_button = [], None, False
        self.feed(markup)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'form':
            self.current = {'action': attrs.get('action', ''), 'fields': {}, 'button': ''}
        elif self.current is not None:
            if tag == 'input' and attrs.get('type') == 'hidden':
                self.current['fields'][attrs['name']] = attrs.get('value', '')
            elif tag == 'button':
                self.in_button = True

    def handle_data(self, text):
        if self.current is not None and self.in_button:
            self.current['button'] += text

    def handle_endtag(self, tag):
        if tag == 'button':
            self.in_button = False
        elif tag == 'form' and self.current is not None:
            self.forms.append(self.current)
            self.current = None

    def returning(self):
        found = [form for form in self.forms if form['button'] == 'Return to this course source search']
        assert len(found) == 1, found
        return found[0]


@contextmanager
def fixture():
    case = synthetic.PagedCourseSearch('test_three_pages_original_unicode_ranges_and_no_mutations')
    case.setUp()
    try:
        yield case
    finally:
        case.doCleanups()


def preview_fields(case):
    hit = search.search(case.base, 'STRASSE', match_case=False, offset=32)['hits'][21]
    fields = {'operation': 'preview',
        'source': json.dumps({key: hit[key] for key in ('source_id', 'fingerprint')}),
        'locator': hit['locator_id'], 'return_query': 'STRASSE',
        'match_start': str(hit['start']), 'match_end': str(hit['end']),
        'return_ignore_case': 'yes', 'return_offset': '32'}
    return hit, fields


class SearchContinuity(unittest.TestCase):
    def test_native_exact_return_restart_and_no_research_selection(self):
        with fixture() as case:
            hit, fields = preview_fields(case)
            before = tree(case.base)
            with native(case.root) as url:
                code, markup = post(url + 'course/synthetic/research', fields)
                self.assertEqual(code, 200)
                self.assertIn('id="course-source-match" tabindex="-1"', markup)
                returning = Forms(markup).returning()
                target = urllib.parse.urlsplit(returning['action']).fragment
                self.assertEqual(target, search.match_anchor(hit))
                self.assertLess(markup.index(returning['action']), markup.index('Current source rights:'))
                code, current = post(urllib.parse.urljoin(url, returning['action']), returning['fields'])
                self.assertEqual(code, 200)
                self.assertIn('id="' + target + '" class="course-search-match"', current)
                self.assertIn('Match 54, returned occurrence', current)
                self.assertEqual(tree(case.base), before)
            with native(case.root) as url:
                code, reopened = post(urllib.parse.urljoin(url, returning['action']), returning['fields'])
                self.assertEqual(code, 200)
                self.assertIn('Match 54, returned occurrence', reopened)
                self.assertEqual(tree(case.base), before)

    def test_rights_or_source_change_keeps_query_without_releasing_old_match(self):
        for change in ('rights', 'source'):
            with self.subTest(change=change), fixture() as case, native(case.root) as url:
                hit, fields = preview_fields(case)
                code, markup = post(url + 'course/synthetic/research', fields)
                self.assertEqual(code, 200)
                returning = Forms(markup).returning()
                record = journal.read_registry(case.base)[case.sid]
                if change == 'rights':
                    journal.op_grant_rights(case.base, case.sid, {'quote': 'denied'}, record['fingerprint'], 'human', 'test')
                else:
                    Path(case.base, record['path']).write_text('Changed fictional passage.\n')
                before = tree(case.base)
                code, current = post(urllib.parse.urljoin(url, returning['action']), returning['fields'])
                self.assertEqual(code, 200)
                self.assertIn('That occurrence is no longer in these results.', current)
                self.assertIn('id="' + search.match_anchor(hit) + '" tabindex="-1"', current)
                self.assertIn('value="STRASSE"', current)
                self.assertIn('Result offset: 32.', current)
                self.assertNotIn('<mark>Straße</mark>', current)
                self.assertEqual(tree(case.base), before)
                retry = next(form for form in Forms(current).forms
                    if form['button'] == 'Retry this course source search')
                self.assertEqual(retry['fields']['offset'], '32')
                self.assertEqual(retry['fields']['return_match'], search.match_anchor(hit))
                if change == 'rights':
                    journal.op_grant_rights(case.base, case.sid, record['rights'], record['fingerprint'], 'human', 'test')
                    before = tree(case.base)
                    code, retried = post(urllib.parse.urljoin(url, retry['action']), retry['fields'])
                    self.assertEqual(code, 200)
                    self.assertIn('Match 54, returned occurrence', retried)
                    self.assertEqual(tree(case.base), before)

    def test_navigation_hint_cannot_admit_content_or_inject_markup(self):
        with fixture() as case, native(case.root) as url:
            before = tree(case.base)
            fields = {'operation': 'search_course_sources', 'query': 'STRASSE',
                      'ignore_case': 'yes', 'offset': '32'}
            for value in ('https://example.com', '<img src=x onerror=alert(1)>',
                          'course-search-occurrence-' + 'a' * 31, ['a', 'b']):
                code, markup = post(url + 'course/synthetic/research', dict(fields, return_match=value))
                self.assertEqual(code, 400)
                self.assertNotIn('<img src=x', markup)
            code, markup = post(url + 'course/synthetic/research',
                dict(fields, return_match='course-search-occurrence-' + '0' * 32))
            self.assertEqual(code, 200)
            self.assertIn('That occurrence is no longer in these results.', markup)
            self.assertNotIn('returned occurrence', markup)
            self.assertEqual(tree(case.base), before)


def check_browser(output):
    from playwright.sync_api import sync_playwright

    output.mkdir(parents=True, exist_ok=True)
    observations = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel='chrome', headless=True)
        try:
            for width in (1280, 768, 390, 320):
                for scripts in (True, False):
                    with fixture() as case, native(case.root) as url:
                        before = tree(case.base)
                        context = browser.new_context(viewport={'width': width, 'height': 900},
                            java_script_enabled=scripts, reduced_motion='reduce',
                            color_scheme='dark' if width == 390 else 'light')
                        try:
                            page = context.new_page()
                            errors = []
                            page.on('pageerror', lambda error: errors.append(str(error)))
                            page.goto(url + 'course/synthetic/research')
                            panel = page.locator('section[aria-labelledby="course-source-search"]')
                            panel.get_by_label('Course source query', exact=True).fill('STRASSE')
                            panel.get_by_label('Ignore capitalization', exact=True).check()
                            def press(button):
                                button.focus()
                                with page.expect_navigation(wait_until='networkidle'):
                                    button.press('Enter')
                            def visible(locator):
                                rect = locator.bounding_box()
                                assert rect and 0 <= rect['x'] and rect['x'] + rect['width'] <= width + 1, rect
                                assert 0 <= rect['y'] < 800, rect
                                return rect
                            press(panel.get_by_role('button', name='Search course sources', exact=True))
                            press(panel.get_by_role('button', name='Next course search results', exact=True))
                            selected = page.locator('.course-search-match').nth(21)
                            target = selected.get_attribute('id')
                            description_ids = selected.get_by_role('button', name='Open exact course search match', exact=True).get_attribute('aria-describedby').split()
                            assert 'Match 54' in ' '.join(page.locator('#' + key).inner_text() for key in description_ids)
                            press(selected.get_by_role('button', name='Open exact course search match', exact=True))
                            mark = page.locator('#research-exact-passage + pre mark')
                            assert mark.inner_text() == 'Straße'
                            preview_rect = visible(mark)
                            assert page.evaluate('document.activeElement.id') == 'course-source-match'
                            controls = page.locator('.research-context-form button, .research-context-form select')
                            sizes = controls.evaluate_all('(elements) => elements.map(e => ({height:e.getBoundingClientRect().height, width:e.getBoundingClientRect().width}))')
                            assert all(size['height'] >= 44 and size['width'] <= width for size in sizes), sizes
                            dimensions = page.evaluate('''() => ({width:innerWidth, scroll:document.documentElement.scrollWidth,
                                wide:[...document.querySelectorAll('main *')].map(e => ({tag:e.tagName, class:e.className,
                                    text:e.textContent.slice(0,100), right:e.getBoundingClientRect().right}))
                                    .filter(e => e.right > innerWidth + 1).slice(0,12)})''')
                            (output / f'preview-dimensions-{width}-{scripts}.json').write_text(json.dumps(dimensions, indent=2) + '\n')
                            page.screenshot(path=str(output / f'preview-{width}-{scripts}.png'))
                            assert dimensions['scroll'] <= width + 1, dimensions
                            press(page.get_by_role('button', name='Return to this course source search', exact=True))
                            returned_rect = visible(page.locator('#' + target))
                            assert page.evaluate('document.activeElement.id') == target
                            assert 'Match 54, returned occurrence' in page.locator('#' + target).inner_text()
                            page.reload(wait_until='networkidle')
                            visible(page.locator('#' + target))
                            assert page.locator('input[name="query"]').first.input_value() == 'STRASSE'
                            assert tree(case.base) == before
                            page.screenshot(path=str(output / f'returned-{width}-{scripts}.png'))
                            press(page.locator('#' + target).get_by_role('button', name='Open exact course search match', exact=True))
                            record = journal.read_registry(case.base)[case.sid]
                            journal.op_grant_rights(case.base, case.sid, {'quote': 'denied'}, record['fingerprint'], 'human', 'test')
                            withheld = tree(case.base)
                            press(page.get_by_role('button', name='Return to this course source search', exact=True))
                            recovery = page.locator('#' + target)
                            visible(recovery)
                            assert 'That occurrence is no longer' in recovery.inner_text()
                            assert page.evaluate('document.activeElement.id') == target
                            assert 'Result offset: 32.' in panel.inner_text()
                            assert page.locator('mark').count() == 0
                            assert tree(case.base) == withheld
                            assert not errors, errors
                            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
                            page.screenshot(path=str(output / f'withheld-{width}-{scripts}.png'))
                            journal.op_grant_rights(case.base, case.sid, record['rights'], record['fingerprint'], 'human', 'test')
                            restored = tree(case.base)
                            press(page.get_by_role('button', name='Retry this course source search', exact=True))
                            visible(page.locator('#' + target))
                            assert page.evaluate('document.activeElement.id') == target
                            assert 'Match 54, returned occurrence' in page.locator('#' + target).inner_text()
                            assert tree(case.base) == restored
                            observations.append({'width': width, 'scripts': scripts, 'keyboard': True,
                                'preview_rect': preview_rect, 'returned_rect': returned_rect,
                                'exact_focus_return_reload': True, 'rights_rechecked': True,
                                'explicit_recovery_retry': True, 'controls_at_least_44px': True,
                                'numbered_match_description': True, 'no_durable_search_change': True, 'no_overflow': True})
                        finally:
                            context.close()
        finally:
            browser.close()
    (output / 'observations.json').write_text(json.dumps(observations, indent=2) + '\n')
    print('Eight Chrome exact-occurrence/reload/withheld-recovery journeys pass at 1280/768/390/320, with and without scripts.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--browser', type=Path)
    args, remaining = parser.parse_known_args()
    if args.browser:
        check_browser(args.browser)
    else:
        unittest.main(argv=[sys.argv[0]] + remaining)
