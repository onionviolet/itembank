#!/usr/bin/env python3
"""Bounded lesson presentation continuity on synthetic native course routes.

Default checks use stdlib. --browser adds installed-Chrome journey checks.
"""
import argparse
from contextlib import contextmanager
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import sys
import urllib.parse

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
import course
import graph
import journal
import model
from surfaces import course_workbench, ia, lesson_interaction
from course_guidance_journey_roundtrip import fixture, get, served, snapshot

FIXTURE = ROOT / 'tests/fixtures/exploration_lineplot.md'


class ContentIdentity(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.attrs = {}
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id') == 'lesson-content':
            self.attrs = {key: value for key, value in attrs.items()
                          if key.startswith('data-exploration-')}


@contextmanager
def exploration_fixture():
    with fixture() as (root, base, _banks, info):
        path = base / 'exploration.md'
        path.write_bytes(FIXTURE.read_bytes())
        linked = journal.op_link(base, 'bank', path.name, 'human', 'synthetic test',
                                 rights={'read': 'granted', 'transform': 'granted'})
        journal.op_adopt(base, linked['object_id'], linked['fingerprint'], 'human', 'synthetic test')
        course.bind_treatment(base, info['objective'], info['source_id'], 'guided-lesson',
                              path.name, 'covered', 'high', 'human', 'synthetic test')
        read = course.read_course(base)
        second = graph.add_objective(read['doc'], 'Transfer the invented intercept rule')
        course.write_course(base, read['doc'], read['fingerprint'], 'human', 'synthetic test')
        course.bind_treatment(base, second['id'], info['source_id'], 'guided-lesson',
                              path.name, 'covered', 'high', 'human', 'synthetic test')
        read = course.read_course(base)
        for index, row in enumerate(read['doc']['bindings']):
            if row.get('locator') == path.name:
                graph.enroll_binding(read['doc'], index, info['source_fingerprint'])
        course.write_course(base, read['doc'], read['fingerprint'], 'human', 'synthetic test')
        rows = [row for row in course_workbench._current_safe_bindings(base, course.read_course(base)['doc'])
                if row.get('locator') == path.name]
        assert len(rows) == 2
        info.update(path=path, object_id=linked['object_id'], bindings=rows,
                    course_id=ia.course_shelf_state(root)['cards'][0]['course_id'])
        yield root, base, info


def route(info, occurrence=0, guided=False):
    params = dict(course=info['course_id'], occurrence=info['bindings'][occurrence]['binding_id'])
    if guided:
        params['view'] = 'guided'
    return '/lesson/exploration?' + urllib.parse.urlencode(params)


def check_routes():
    assert lesson_interaction.exploration_attributes() == ''
    for bad in ('', ' ', 'x\n', 'x' * 257, 123, {}):
        assert lesson_interaction.exploration_attributes('lesson', 'revision', bad) == ''
    escaped = lesson_interaction.exploration_attributes('lesson"<>', 'revision', 'occurrence')
    assert escaped.startswith(' ') and '&quot;&lt;&gt;' in escaped
    errors, _ = model.lint(model.load(str(FIXTURE)), lesson=model.parse_lesson(str(FIXTURE)))
    assert errors == [], errors
    with exploration_fixture() as (root, base, info), served(root) as url:
        before = snapshot(root, allow_indexes=True)
        identities = []
        for occurrence in (0, 1):
            markup = get(url, route(info, occurrence))
            identity = ContentIdentity(markup).attrs
            assert len(identity) == 3, identity
            identities.append(identity)
            assert 'CORRECT:' not in markup and 'WHY BEST:' not in markup
            assert 'violet tile' not in markup
            assert 'Static explanation:' in markup and 'Transfer:' in markup
            assert 'class="comparison-controls" hidden' in markup
            assert 'class="lineplot-controls" hidden' in markup
        assert identities[0]['data-exploration-lesson'] == identities[1]['data-exploration-lesson']
        assert identities[0]['data-exploration-revision'] == identities[1]['data-exploration-revision']
        assert identities[0]['data-exploration-occurrence'] != identities[1]['data-exploration-occurrence']
        for query in ('', '?course=synthetic', '?course=synthetic&occurrence=unknown',
                      '?course=synthetic&course=synthetic',
                      '?course=unknown&occurrence=' + info['bindings'][0]['binding_id']):
            assert ContentIdentity(get(url, '/lesson/exploration' + query)).attrs == {}, query
        assert snapshot(root, allow_indexes=True) == before, 'lesson routes changed canonical/evidence files'
        record = journal.read_registry(base)[info['object_id']]
        raw = info['path'].read_text().replace('A records 12 mm', 'A records exactly 12 mm').encode()
        journal.op_edit_in_place(base, info['object_id'], 'bank', info['path'].name, raw,
                                 record['fingerprint'], 'human', 'synthetic revision test')
        newer = ContentIdentity(get(url, route(info))).attrs
        assert newer['data-exploration-revision'] != identities[0]['data-exploration-revision']
        assert newer['data-exploration-occurrence'] == identities[0]['data-exploration-occurrence']
    print('native identity: accepted object/revision, occurrence isolation, ambiguous refusal, static fallback and no evidence writes passed')


def check_browser(output=None):
    from playwright.sync_api import sync_playwright
    paths = ('surfaces/lesson_interaction.py', 'surfaces/lesson_progressive.py',
             'surfaces/lesson.py', 'surfaces/daemon.py',
             'tests/lesson_exploration_roundtrip.py', 'tests/fixtures/exploration_lineplot.md')
    inputs = {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in paths}
    with exploration_fixture() as (root, base, info), served(root) as url, sync_playwright() as pw:
        browser = pw.chromium.launch(channel=os.environ.get('ITEMBANK_VISUAL_QA_CHANNEL', 'chrome'), headless=True)
        context = browser.new_context(reduced_motion='reduce')
        page = context.new_page()
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        before = snapshot(root, allow_indexes=True)
        target = urllib.parse.urljoin(url, route(info))
        for width in (1280, 390, 320):
            page.set_viewport_size({'width': width, 'height': 900})
            page.goto(target)
            number = page.locator('.comparison-number')
            number.focus()
            number.fill('11')
            number.press('Enter')
            page.locator('.lineplot-prediction').select_option('all')
            page.get_by_role('button', name='Commit prediction', exact=True).click()
            page.locator('.lineplot-value').select_option('-1')
            page.goto(urllib.parse.urljoin(url, '/course/synthetic/map'))
            page.go_back()
            assert number.input_value() == '11'
            assert page.locator('.lineplot-value').input_value() == '-1'
            page.goto(urllib.parse.urljoin(url, '/course/synthetic/map'))
            page.goto(target)
            assert number.input_value() == '11'
            assert page.locator('.lineplot-value').input_value() == '-1'
            assert page.locator('.lineplot-prediction').input_value() == 'all'
            page.reload()
            assert number.input_value() == '11'
            page.locator('.lineplot-prediction').select_option('none')
            page.locator('.lineplot-prediction').press('Escape')
            assert page.locator('.lineplot-prediction').input_value() == 'all'
            number.fill('7')
            number.press('Escape')
            assert number.input_value() == '11'
            number.fill('7')
            page.get_by_role('button', name='Cancel change', exact=True).click()
            assert number.input_value() == '11'
            page.locator('.lineplot-prediction').select_option('none')
            page.get_by_role('button', name='Cancel prediction', exact=True).click()
            assert page.locator('.lineplot-prediction').input_value() == 'all'
            page.get_by_role('button', name='Reset comparison', exact=True).focus()
            page.keyboard.press('Enter')
            assert number.input_value() == '18'
            page.get_by_role('button', name='Reset exploration', exact=True).focus()
            page.keyboard.press('Enter')
            page.reload()
            assert number.input_value() == '18'
            assert page.locator('.lineplot-manipulate').is_hidden()
            fits = page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            if not fits:
                if output:
                    output.mkdir(parents=True, exist_ok=True)
                    page.screenshot(path=str(output / ('failed-reflow-%d.png' % width)), full_page=True)
                overflowing = page.evaluate("""() => Array.from(document.querySelectorAll('body *')).map(node =>
                  [node.tagName,node.className,node.getBoundingClientRect().left,node.getBoundingClientRect().right])
                  .filter(row => row[2]<0 || row[3]>innerWidth).slice(0,30)""")
                raise AssertionError('overflow at %d: %s' % (width, overflowing))
            assert page.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches")
            if output:
                output.mkdir(parents=True, exist_ok=True)
                # Show both native explorations, including the equation/table.
                page.locator('.lineplot-prediction').select_option('all')
                page.get_by_role('button', name='Commit prediction', exact=True).click()
                page.locator('.lineplot-value').select_option('-1')
                page.screenshot(path=str(output / ('native-%d.png' % width)), full_page=True)
        number.fill('9')
        number.press('Enter')
        page.goto(urllib.parse.urljoin(url, route(info, 1)))
        assert number.input_value() == '18', 'distinct occurrence leaked state'
        page.goto(target)
        assert number.input_value() == '9'
        other = context.new_page()
        other.goto(target)
        assert other.locator('.comparison-number').input_value() == '18', 'independent tab leaked state'
        other.close()
        with page.expect_popup() as opened:
            page.evaluate('(url) => window.open(url)', target)
        popup = opened.value
        popup.wait_for_load_state()
        assert popup.locator('.comparison-number').input_value() == '18', 'opener storage clone leaked state'
        popup.close()
        # A drag preview is cancelled on Escape, window blur, and detour.
        handle = page.locator('.comparison-handle')
        box = handle.bounding_box()
        page.mouse.move(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
        page.mouse.down()
        page.mouse.move(box['x'] + box['width'] / 2 + 35, box['y'] + box['height'] / 2)
        page.keyboard.press('Escape')
        page.mouse.up()
        assert number.input_value() == '9'
        box = handle.bounding_box()
        page.mouse.move(box['x'] + 22, box['y'] + 22)
        page.mouse.down()
        page.mouse.move(box['x'] + 50, box['y'] + 22)
        page.evaluate("window.dispatchEvent(new Event('blur'))")
        page.mouse.up()
        assert number.input_value() == '9'
        # Guided stages and the same comparison model share admitted identity.
        page.goto(urllib.parse.urljoin(url, route(info, guided=True)))
        page.get_by_text('Reading options', exact=True).click()
        page.get_by_role('button', name='Show all explanations', exact=True).click()
        assert number.input_value() == '9'
        page.goto(urllib.parse.urljoin(url, '/course/synthetic/learn'))
        page.goto(urllib.parse.urljoin(url, route(info, guided=True)))
        assert page.locator('.stage[hidden]').count() == 0
        assert number.input_value() == '9'
        # Corrupt storage degrades visibly; denied storage still permits changes.
        page.evaluate("sessionStorage.setItem('itembank:lesson-exploration:v1','{broken')")
        page.goto(target)
        assert number.input_value() == '18'
        assert any('unreadable' in message for message in page.locator('.exploration-continuity').all_inner_texts())
        denied = browser.new_context()
        denied.add_init_script("Object.defineProperty(window,'sessionStorage',{get(){throw new Error('synthetic denial')}})")
        denied_page = denied.new_page()
        denied_page.goto(target)
        denied_page.locator('.comparison-number').fill('6')
        denied_page.locator('.comparison-number').press('Enter')
        assert denied_page.locator('.comparison-number').input_value() == '6'
        assert 'unavailable' in denied_page.locator('.comparison-controls .exploration-continuity').inner_text()
        denied.close()
        plain = browser.new_context(java_script_enabled=False)
        plain_page = plain.new_page()
        plain_page.goto(target)
        assert plain_page.locator('.lineplot-static').is_visible()
        assert plain_page.locator('.comparison-static').is_visible()
        assert plain_page.locator('.lineplot-controls').is_hidden()
        assert 'Every' in plain_page.locator('.lineplot-static').inner_text() or 'every' in plain_page.locator('.lineplot-static').inner_text()
        plain.close()
        assert snapshot(root, allow_indexes=True) == before, 'browser exploration changed accepted content or evidence'
        record = journal.read_registry(base)[info['object_id']]
        raw = info['path'].read_text().replace('A records 12 mm', 'A records exactly 12 mm').encode()
        journal.op_edit_in_place(base, info['object_id'], 'bank', info['path'].name, raw,
                                 record['fingerprint'], 'human', 'synthetic revision test')
        number.fill('8')
        number.press('Enter')
        page.reload()
        assert number.input_value() == '18', 'changed accepted teaching revision restored old exploration'
        assert errors == [], errors
        context.close()
        browser.close()
    if output:
        after = {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in paths}
        (output / 'receipt.json').write_text(json.dumps({
            'result': 'passed', 'channel': os.environ.get('ITEMBANK_VISUAL_QA_CHANNEL', 'chrome'),
            'widths': [1280, 390, 320], 'inputs': inputs, 'after': after,
            'source_drift': [path for path in paths if inputs[path] != after[path]],
            'limits': ['source checkout only', 'synthetic data', 'automated keyboard and pointer checks',
                       'human touch, screen-reader and learning acceptance not performed']}, indent=2) + '\n')
    print('installed Chrome: native detour/reload, tab/opener/occurrence/revision isolation, reset/cancel, denied/corrupt storage, keyboard, 1280/390/320 reflow, reduced motion, script-free and no evidence writes passed')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--browser', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    check_routes()
    if args.browser:
        check_browser(args.output)
