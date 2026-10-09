#!/usr/bin/env python3
"""Read-only prerequisite and source detours return to the exact objective."""

import argparse
from contextlib import contextmanager
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
import urllib.parse

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]

import course
import graph
import journal
from surfaces import course_context_view
from course_guidance_journey_roundtrip import fixture, get, served, snapshot


class Links(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.links.append(dict(attrs))


@contextmanager
def context_fixture():
    with fixture() as (root, base, banks, info):
        read = course.read_course(base)
        doc = read['doc']
        dependent = graph.add_objective(doc, 'Apply the invented color rule to a new signal pattern')
        graph.add_edge(doc, info['objective'], 'prerequisite-of', dependent['id'],
                       authority='authored', confidence='high',
                       rationale='Use the selection rule to explain which signal changes the outcome.')
        course.write_course(base, doc, read['fingerprint'], 'human', 'test')
        info.update(origin=dependent['id'], target=info['objective'], origin_index=len(doc['objectives']) - 1)
        yield root, base, banks, info


def check_routes():
    with context_fixture() as (root, base, _banks, info):
        before = snapshot(root)
        with served(root) as url:
            page = get(url, '/course/synthetic/map')
            assert 'CORRECT:' not in page
            prerequisite = next(a['href'] for a in Links(page).links
                                if a.get('class') == 'course-prerequisite-link')
            query = urllib.parse.parse_qs(urllib.parse.urlsplit(prerequisite).query)
            assert query['from_objective'] == [info['origin']]
            assert query['to_objective'] == [info['target']]
            returned = get(url, prerequisite)
            origin_href = '/course/synthetic/map#objective-%d' % info['origin_index']
            assert origin_href in returned and 'Return to Apply the invented color rule' in returned
            source = next(a['href'] for a in Links(returned).links
                          if 'return_objective' in urllib.parse.parse_qs(
                              urllib.parse.urlsplit(a.get('href', '')).query))
            source_query = urllib.parse.parse_qs(urllib.parse.urlsplit(source).query)
            assert source_query['return_objective'] == [info['origin']], source
            source_page = get(url, source)
            assert origin_href in source_page and 'Return to Apply the invented color rule' in source_page
            assert 'Source text' in source_page and 'CORRECT:' not in source_page
            assert 'Builds on' in get(url, origin_href)
        assert snapshot(root) == before, 'view-only map/source detours changed durable files'
        # A fresh native process retains exact navigation without another state store.
        with served(root) as url:
            assert origin_href in get(url, prerequisite)
            assert origin_href in get(url, source)
            for query in ('return_objective=unknown', 'return_objective=//example.com',
                          'return_objective=%s&return_objective=%s' % (info['origin'], info['target'])):
                markup = get(url, '/course/synthetic/sources?source=0&' + query)
                assert '<p class="course-context-return">' not in markup
            bad_map = '/course/synthetic/map?' + urllib.parse.urlencode({
                'from_objective': info['target'], 'to_objective': info['origin']})
            assert '<p class="course-context-return">' not in get(url, bad_map)
        assert snapshot(root) == before, 'restart or invalid-return display changed durable files'
        source_record = journal.read_registry(base)[info['source_id']]
        (base / source_record['path']).write_text('CHANGED SOURCE MUST STAY WITHHELD', encoding='utf-8')
        changed_before = snapshot(root)
        with served(root) as url:
            changed = get(url, source)
            assert 'Source revision needs review' in changed and 'Affected objectives' in changed
            assert 'Revision details' in changed and origin_href in changed
            assert 'CHANGED SOURCE MUST STAY WITHHELD' not in changed
        assert snapshot(root) == changed_before, 'source-impact inspection changed accepted state'


def check_escaped_presentation():
    oid = 'original'
    row = {'id': oid, 'statement': '<script>title</script>'}
    edge = dict(source='prerequisite', title='<b>unsafe</b>', href='/course/synthetic/map#objective-0',
                rationale='<script>rationale</script>', evidence='<b>history</b>',
                authority='authored', confidence='unknown', override='advisory')
    markup = course_context_view.objective_section(1, row, [edge], '<p>Source</p>', '<p>Activity</p>', '')
    assert '<script>' not in markup and '<b>unsafe' not in markup and '<b>history' not in markup
    assert '&lt;script&gt;' in markup


def check_browser(output):
    from playwright.sync_api import sync_playwright
    output.mkdir(parents=True, exist_ok=True)
    observations = []
    with context_fixture() as (root, base, _banks, _info), served(root) as url, sync_playwright() as pw:
        before = snapshot(root)
        browser = pw.chromium.launch(channel='chrome', headless=True)
        try:
            for width in (1280, 390, 320):
                for scheme in ('light', 'dark'):
                    context = browser.new_context(viewport={'width': width, 'height': 900},
                                                  color_scheme=scheme, reduced_motion='reduce')
                    page = context.new_page()
                    errors = []
                    page.on('pageerror', lambda e: errors.append(str(e)))
                    page.goto(url + 'course/synthetic/map')
                    link = page.locator('.course-prerequisite-link').first
                    link.focus()
                    with page.expect_navigation(wait_until='networkidle'):
                        page.keyboard.press('Enter')
                    target = page.locator('.course-context-return').first
                    assert target.is_visible()
                    page.screenshot(path=str(output / f'map-{width}-{scheme}.png'), full_page=True)
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
                    source_details = page.locator('#objective-0 .course-objective-alignment')
                    source_details.locator('summary').focus()
                    page.keyboard.press('Enter')
                    source_link = source_details.locator('a').first
                    source_link.focus()
                    with page.expect_navigation(wait_until='networkidle'):
                        page.keyboard.press('Enter')
                    assert page.locator('.course-context-return').first.is_visible()
                    assert page.locator('.course-source-text').is_visible()
                    page.locator('.course-context-return a').first.focus()
                    with page.expect_navigation(wait_until='networkidle'):
                        page.keyboard.press('Enter')
                    assert page.url.endswith('#objective-1'), page.url
                    assert page.evaluate('document.activeElement.id') == 'objective-1'
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
                    assert not errors, errors
                    observations.append(dict(width=width, scheme=scheme, exact_return=True))
                    context.close()
            context = browser.new_context(java_script_enabled=False, viewport={'width': 320, 'height': 900},
                                          reduced_motion='reduce')
            page = context.new_page()
            page.goto(url + 'course/synthetic/map')
            with page.expect_navigation(wait_until='networkidle'):
                page.locator('.course-prerequisite-link').first.click()
            assert page.locator('.course-context-return').first.is_visible()
            with page.expect_navigation(wait_until='networkidle'):
                page.locator('.course-context-return a').first.click()
            assert page.url.endswith('#objective-1')
            context.close()
            source_record = journal.read_registry(base)[_info['source_id']]
            (base / source_record['path']).write_text('WITHHELD CHANGED SOURCE', encoding='utf-8')
            changed_before = snapshot(root)
            context = browser.new_context(viewport={'width': 320, 'height': 900})
            page = context.new_page()
            page.goto(url + 'course/synthetic/sources?source=0')
            revision = page.locator('.course-source-impact details')
            assert revision.get_attribute('open') is None
            revision.locator('summary').focus()
            page.keyboard.press('Enter')
            assert revision.locator('dd').first.is_visible()
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
            assert 'WITHHELD CHANGED SOURCE' not in page.content()
            page.screenshot(path=str(output / 'changed-source-320.png'), full_page=True)
            context.close()
            assert snapshot(root) == changed_before
            # The source change above is the only intended durable mutation.
            before.pop(str((base / source_record['path']).relative_to(root)))
            final = snapshot(root)
            final.pop(str((base / source_record['path']).relative_to(root)))
            assert final == before, 'browser navigation mutated durable learning state'
        finally:
            browser.close()
    (output / 'observations.json').write_text(json.dumps(observations, indent=2) + '\n')
    print('Chrome: six light/dark layouts, keyboard exact return, script-free return and revision disclosure pass')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--browser-shots', type=Path)
    args = parser.parse_args()
    check_routes()
    check_escaped_presentation()
    if args.browser_shots:
        check_browser(args.browser_shots)
    print('course context: exact prerequisite/source return, restart, changed-source refusal and read-only GETs pass')


if __name__ == '__main__':
    main()
