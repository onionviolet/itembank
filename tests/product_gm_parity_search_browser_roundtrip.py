#!/usr/bin/env python3
"""Opt-in installed-Chrome check for the paged native source-search task."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
import product_gm_parity_search_roundtrip as synthetic
from context_help_native_roundtrip import native
from course_source_search_roundtrip import tree


def check_browser(output):
    from playwright.sync_api import sync_playwright
    output.mkdir(parents=True, exist_ok=True)
    case = synthetic.PagedCourseSearch('test_three_pages_original_unicode_ranges_and_no_mutations')
    case.setUp()
    observations = []
    try:
        with native(case.root) as url, sync_playwright() as pw:
            before = tree(case.base)
            browser = pw.chromium.launch(channel='chrome', headless=True)
            try:
                for width in (1280, 390, 320):
                    for scripts in (True, False):
                        context = browser.new_context(viewport={'width': width, 'height': 900},
                            java_script_enabled=scripts, reduced_motion='reduce', color_scheme='dark' if width == 390 else 'light')
                        page = context.new_page()
                        errors = []
                        page.on('pageerror', lambda error: errors.append(str(error)))
                        page.goto(url + 'course/synthetic/research')
                        search = page.locator('section[aria-labelledby="course-source-search"]')
                        search.get_by_label('Course source query', exact=True).fill('STRASSE')
                        search.get_by_label('Ignore capitalization', exact=True).check()
                        search.get_by_role('button', name='Search course sources', exact=True).focus()
                        with page.expect_navigation(wait_until='networkidle'):
                            page.keyboard.press('Enter')
                        search = page.locator('section[aria-labelledby="course-source-search"]')
                        search.get_by_role('button', name='Next course search results', exact=True).focus()
                        with page.expect_navigation(wait_until='networkidle'):
                            page.keyboard.press('Enter')
                        assert 'Result offset: 32.' in search.inner_text()
                        search.get_by_role('button', name='Open exact course search match', exact=True).nth(1).focus()
                        with page.expect_navigation(wait_until='networkidle'):
                            page.keyboard.press('Enter')
                        assert page.locator('#research-exact-passage + pre mark').inner_text() == 'Straße'
                        page.get_by_role('button', name='Return to this course source search', exact=True).focus()
                        with page.expect_navigation(wait_until='networkidle'):
                            page.keyboard.press('Enter')
                        page.reload(wait_until='networkidle')
                        search = page.locator('section[aria-labelledby="course-source-search"]')
                        assert 'Result offset: 32.' in search.inner_text()
                        assert search.get_by_label('Ignore capitalization', exact=True).is_checked()
                        assert search.get_by_label('Course source query', exact=True).input_value() == 'STRASSE'
                        assert search.get_by_role('button', name='Open exact course search match', exact=True).count() == 32
                        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
                        assert not errors, errors
                        page.screenshot(path=str(output / ('page-two-%d-%s.png' % (width, 'scripts' if scripts else 'plain'))))
                        observations.append({'width': width, 'scripts': scripts, 'keyboard': True,
                            'original_unicode_range': True, 'exact_page_mode_return_reload': True,
                            'no_overflow': True, 'no_durable_change': tree(case.base) == before})
                        context.close()
                assert tree(case.base) == before
            finally:
                browser.close()
    finally:
        case.doCleanups()
    (output / 'observations.json').write_text(json.dumps(observations, indent=2) + '\n', encoding='utf-8')
    print('Six installed-Chrome keyboard/page/preview/return/reload journeys pass, including script-free 320px.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--browser', type=Path)
    args = parser.parse_args()
    if args.browser:
        check_browser(args.browser)
    else:
        print('Opt-in browser gate: pass --browser with a disposable evidence directory.')
