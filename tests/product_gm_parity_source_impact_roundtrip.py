#!/usr/bin/env python3
"""Exact changed-source impact through native read-only Sources routes."""
import copy
import argparse
import json
import urllib.parse
from pathlib import Path
import sys
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
import course
import evidence
import graph
import journal
from surfaces import course_workbench as cw, reading_desk
from course_guidance_journey_roundtrip import fixture, get, served, snapshot
from course_context_journey_roundtrip import Links


def check_native_impact():
    with fixture(reported_reading=True) as (root, base, banks, info):
        read = course.read_course(base)
        doc = read['doc']
        old = graph.validate_reading_graph(doc)['occurrences'][0]
        current = graph.append_reading_revision(doc, old['occurrence_id'],
                                                {'purpose': 'Review the invented rule in a new context.'})
        treatment = next(b for b in doc['bindings'] if b.get('treatment_kind') == 'guided-lesson')
        if not treatment.get('binding_id'):
            treatment = graph.enroll_binding(doc, doc['bindings'].index(treatment), info['source_fingerprint'])
        prior_binding = treatment['binding_revision_id']
        treatment = graph.append_binding_revision(doc, treatment['binding_id'],
                                                  {'locator': 'symbols.md#Invented color rule'})
        course.write_course(base, doc, read['fingerprint'], 'human', 'test')
        log = evidence.log_path(base)
        assert evidence.reading_state(log, old['course_id'], old['occurrence_id'], old['revision_id'])['state'] == 'reported-read'
        assert evidence.reading_state(log, current['course_id'], current['occurrence_id'], current['revision_id'])['state'] == 'not-reported'
        source_row = journal.read_registry(base)[info['source_id']]
        (base / source_row['path']).write_text('PRIVATE CHANGED SOURCE BYTES', encoding='utf-8')
        before = snapshot(root)
        impact = cw.source_impact(base, doc, info['source_id'])
        assert impact['readings'] == [current], impact
        assert impact['historical_readings'] == 1 and impact['historical_bindings'] == 1
        assert prior_binding not in [b.get('binding_revision_id') for b in impact['treatments']]
        for restart in range(2):
            with served(root) as url:
                markup = get(url, '/course/synthetic/sources?source=0')
                block = markup.split('aria-label="Changed source impact"', 1)[1].split('</aside>', 1)[0]
                assert current['occurrence_id'] in block and current['revision_id'] in block
                assert 'Reading revision details' in block and 'Binding revision details' in block
                assert old['revision_id'] not in block and prior_binding not in block
                assert treatment['binding_id'] in block and treatment['binding_revision_id'] in block
                assert 'PRIVATE CHANGED SOURCE BYTES' not in markup and 'CORRECT:' not in markup
                assert 'Prior reading declarations stay on their recorded revisions' in block
                hrefs = [a['href'] for a in Links(block).links]
                reading = reading_desk.href('synthetic', current) + '?' + urllib.parse.urlencode({'return_source': info['source_id']})
                source_map = '/course/synthetic/map?' + urllib.parse.urlencode({'return_source': info['source_id']}) + '#objective-0'
                assert reading in hrefs and source_map in hrefs
                for href in hrefs:
                    assert urllib.parse.parse_qs(urllib.parse.urlsplit(href).query).get('return_source') == [info['source_id']], href
                assert 'Open assigned reading' in block, 'Exact direct-reading binding was labeled unavailable.'
                lesson = next(h for h in hrefs if h.startswith('/lesson/'))
                assert 'occurrence=' + treatment['binding_id'] in lesson
                reading_page = get(url, reading)
                assert 'PRIVATE CHANGED SOURCE BYTES' not in reading_page
                assert 'Return' in reading_page or 'Back to' in reading_page
                assert 'Invented color rule' in get(url, lesson)
                assert 'Invented' in get(url, '/course/synthetic/map#objective-0')
            assert snapshot(root) == before, 'impact or task inspection changed durable files'


def check_unavailable_and_exact_identity():
    with fixture() as (root, base, banks, info):
        doc = course.read_course(base)['doc']
        before = snapshot(root)
        missing = cw.source_impact(base, doc, 'missing-exact-source-id')
        assert missing['state'] == 'unavailable' and not missing['readings']
        registry = journal.read_registry(base)
        denied = copy.deepcopy(registry)
        denied[info['source_id']]['rights']['read'] = 'denied'
        with mock.patch.object(journal, 'read_registry', return_value=denied):
            impact = cw.source_impact(base, doc, info['source_id'])
            assert impact['current'] is None and any('read right' in s for s in impact['issues'])
        damaged = copy.deepcopy(doc)
        damaged['reading_occurrences'][0]['document'] = '{}'
        impact = cw.source_impact(base, damaged, info['source_id'])
        assert not impact['readings'] and any('manifest' in s for s in impact['issues'])
        unlinked = copy.deepcopy(doc)
        treatment = next(b for b in unlinked['bindings'] if b.get('treatment_kind') == 'guided-lesson')
        treatment['locator'] = 'absent.md'
        handler = type('Handler', (), {'root': str(root), 'path': '/course/synthetic/sources?source=0'})()
        state = {'area': 'sources', 'area_label': 'Sources', 'course_id': 'synthetic'}
        (base / registry[info['source_id']]['path']).write_text('WITHHELD', encoding='utf-8')
        changed = snapshot(root)
        markup = cw.details(handler, state, base, unlinked, banks)
        assert 'Task link unavailable' in markup and '/lesson/' not in markup
        assert 'WITHHELD' not in markup and snapshot(root) == changed
        # A successor binding does not make an assignment pinned to its parent current.
        revised = copy.deepcopy(doc)
        reading = graph.validate_reading_graph(revised)['occurrences'][0]
        graph.append_binding_revision(revised, reading['binding_ref']['binding_id'],
                                      {'locator': 'Changed accepted locator'})
        impact = cw.source_impact(base, revised, info['source_id'])
        assert not impact['readings'] and any('superseded binding' in s for s in impact['issues'])


def check_native_rights_and_missing_source():
    for rights in ('denied', 'unknown'):
        with fixture() as (root, base, banks, info):
            journal.op_grant_rights(base, info['source_id'], {'read': rights},
                                   info['source_fingerprint'], 'human', 'test')
            source = journal.read_registry(base)[info['source_id']]
            path = base / source['path']
            path.write_text('RESTRICTED CHANGED SOURCE BYTES', encoding='utf-8')
            before = snapshot(root)
            with served(root) as url:
                markup = get(url, '/course/synthetic/sources?source=0')
                assert 'read right is not granted' in markup
                assert 'RESTRICTED CHANGED SOURCE BYTES' not in markup
                assert 'Inspect assigned reading' in markup
            assert snapshot(root) == before
            path.unlink()
            before = snapshot(root)
            with served(root) as url:
                markup = get(url, '/course/synthetic/sources?source=0')
                assert 'Source revision needs review' in markup
                assert 'Inspect assigned reading' in markup
            assert snapshot(root) == before


def check_browser(output):
    from playwright.sync_api import sync_playwright
    output.mkdir(parents=True, exist_ok=True)
    observations = []
    with fixture() as (root, base, banks, info), served(root) as url, sync_playwright() as pw:
        record = journal.read_registry(base)[info['source_id']]
        (base / record['path']).write_text('CHANGED SOURCE MUST STAY WITHHELD', encoding='utf-8')
        before = snapshot(root)
        browser = pw.chromium.launch(channel='chrome', headless=True)
        try:
            for width, scripts in ((1280, True), (390, True), (320, True), (320, False)):
                context = browser.new_context(viewport={'width': width, 'height': 900},
                    java_script_enabled=scripts, reduced_motion='reduce')
                page = context.new_page()
                source_url = url + 'course/synthetic/sources?source=0'
                page.goto(source_url)
                block = page.locator('.course-source-impact')
                assert block.is_visible()
                assert block.locator('details').first.get_attribute('open') is None
                assert 'CHANGED SOURCE MUST STAY WITHHELD' not in page.content()
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
                block.screenshot(path=str(output / ('impact-%d-%s.png' % (width, 'scripts' if scripts else 'plain'))))
                block.get_by_role('link', name='Inspect assigned reading', exact=True).focus()
                with page.expect_navigation(wait_until='networkidle'):
                    page.keyboard.press('Enter')
                assert '/reading/' in page.url and 'CHANGED SOURCE MUST STAY WITHHELD' not in page.content()
                page.go_back(wait_until='networkidle')
                assert page.url == source_url
                page.locator('.course-source-impact').get_by_role('link', name='Open linked lesson', exact=True).focus()
                with page.expect_navigation(wait_until='networkidle'):
                    page.keyboard.press('Enter')
                assert '/lesson/' in page.url
                page.go_back(wait_until='networkidle')
                assert page.url == source_url
                page.reload(wait_until='networkidle')
                assert page.locator('.course-source-impact').is_visible()
                observations.append(dict(width=width, scripts=scripts, withheld=True,
                    no_overflow=True, exact_task=True, browser_history_return=True,
                    explicit_source_back_control='integration I1 pending'))
                context.close()
            assert snapshot(root) == before
        finally:
            browser.close()
    (output / 'observations.json').write_text(json.dumps(observations, indent=2) + '\n', encoding='utf-8')
    print('Four Chrome source-impact inspection/history-return journeys pass; explicit source-origin return remains I1.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--browser', type=Path)
    args = parser.parse_args()
    if args.browser:
        check_browser(args.browser)
    else:
        check_native_impact()
        check_unavailable_and_exact_identity()
        check_native_rights_and_missing_source()
        print('source impact: native exact current reading/map/lesson links, restart, rights, missing IDs and read-only history pass')
