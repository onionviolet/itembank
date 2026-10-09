#!/usr/bin/env python3
"""Long-source detours preserve selected passage position without canonical writes."""
import argparse
from contextlib import contextmanager
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
from reading_desk_roundtrip import ReadingDesk
from course_guidance_journey_roundtrip import served, snapshot, get
from surfaces.reading_desk import href

TARGET = 'TARGET deep synthetic source 中文 🧭.'


@contextmanager
def long_fixture():
    case = ReadingDesk('test_live_http_route_and_note')
    case.setUp()
    try:
        text = 'Invented comparison before the target. ' * 110 + TARGET + 'Invented comparison after the target. ' * 100
        source = case.run_op('register_source', filename='long.md', content='# Long source\n' + text + '\n',
                            grants={'read': 'granted', 'transform': 'granted'})
        case.source_id = source['source_object_id']
        case.source_fp = source['fingerprint']
        case.run_op('add_source', source_object_id=case.source_id, title='Long source')
        case.bind('line 2')
        row = case.run_op('create_reading', expected_fingerprint=case.read()['fingerprint'],
            binding_index=1, values=case.values(), title='Long reading', activation='Now')['occurrence']
        assert case.view(row)['content'] == text
        yield Path(case.root), Path(case.base), href('synthetic', row)
    finally:
        case.doCleanups()


def position(page):
    return page.evaluate('''() => ({y:scrollY,sourceY:document.querySelector('#source-content').scrollTop,
        mode:document.querySelector('.reading-layout').dataset.readingMode})''')


def select_deep(page, mode):
    page.get_by_role('button', name='Read' if mode == 'read' else 'Notebook', exact=True).click()
    page.locator('#source-content').evaluate('''(el,target) => {
        if(document.querySelector('.reading-layout').dataset.readingMode==='notebook'){
            el.scrollIntoView({block:'center',behavior:'instant'});
        }
        const text=el.firstChild,start=text.textContent.indexOf(target);
        const range=document.createRange();range.setStart(text,start);range.setEnd(text,start+target.length);
        const box=range.getBoundingClientRect();
        if(document.querySelector('.reading-layout').dataset.readingMode==='notebook'){
            const bounds=el.getBoundingClientRect();el.scrollTop+=box.top-bounds.top-50;
        }else{window.scrollTo({top:box.top+scrollY-250,behavior:'instant'});}
        const selected=window.getSelection();selected.removeAllRanges();selected.addRange(range);
    }''', TARGET)
    # The user-visible selection event settles before the separate tool action.
    page.wait_for_function('window.getSelection().toString() === ' + json.dumps(TARGET))
    page.wait_for_function('selectedPassageReturn !== null')
    assert page.evaluate('''() => {
        const box=window.getSelection().getRangeAt(0).getBoundingClientRect();
        return box.bottom>0 && box.top<innerHeight;
    }''')
    return position(page)


def check_native():
    with long_fixture() as (root, base, route), served(root) as url:
        before = snapshot(root, allow_indexes=True)
        markup = get(url, route)
        assert TARGET in markup and 'Return to passage' in markup
        assert snapshot(root, allow_indexes=True) == before
    print('Native long-source passage is admitted and static rendering preserves canonical bytes.')


def check_browser(shots):
    from playwright.sync_api import sync_playwright
    shots.mkdir(parents=True, exist_ok=True)
    rows = []
    with long_fixture() as (root, base, route), served(root) as url, sync_playwright() as pw:
        browser = pw.chromium.launch(channel='chrome', headless=True)
        try:
            for width in (1280, 390, 320):
                for mode in ('read', 'notebook'):
                    for action in ('quote', 'help'):
                        context = browser.new_context(viewport={'width': width, 'height': 900},
                            has_touch=width == 320, color_scheme='dark' if width == 320 else 'light',
                            reduced_motion='reduce')
                        try:
                            page = context.new_page()
                            page.set_default_timeout(8000)
                            errors = []
                            page.on('pageerror', lambda error: errors.append(str(error)))
                            page.goto(url + route.lstrip('/'))
                            page.wait_for_function('!document.querySelector("#save-note").disabled')
                            before_files = snapshot(root, allow_indexes=True)
                            before = select_deep(page, mode)
                            assert before['y'] > 1500 if mode == 'read' else before['sourceY'] > 1500
                            activation = 'tap' if width == 320 else 'click'
                            getattr(page.locator('#reading-tools > summary'), activation)()
                            getattr(page.locator('#reading-quote' if action == 'quote' else '#reading-help-selection'), activation)()
                            if action == 'quote':
                                wording = page.locator('#note').input_value()
                                assert TARGET in wording
                                page.locator('.reading-return').first.focus()
                                page.keyboard.press('Enter')
                                assert page.locator('#note').input_value() == wording
                            else:
                                assert TARGET in page.locator('#help-selection-state').inner_text()
                                original = page.evaluate('JSON.stringify(helpReturn)')
                                page.locator('#help-question').fill('Explain this invented comparison.')
                                page.evaluate('helpRememberReturn()')
                                assert page.evaluate('JSON.stringify(helpReturn)') == original
                                page.locator('#help-return').focus()
                                page.keyboard.press('Enter')
                                assert page.evaluate('window.getSelection().toString()') == TARGET
                            after = position(page)
                            assert after['mode'] == before['mode'], (before, after)
                            assert abs(after['y'] - before['y']) <= 2, (before, after)
                            assert abs(after['sourceY'] - before['sourceY']) <= 2, (before, after)
                            assert page.locator('#source-content').evaluate('el => el === document.activeElement')
                            assert page.locator('#reading-tools').get_attribute('open') is None
                            assert snapshot(root, allow_indexes=True) == before_files
                            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
                            assert not errors, errors
                            if width == 320:
                                page.screenshot(path=str(shots / f'return-{mode}-{action}-320.png'))
                            rows.append({'width': width, 'mode': mode, 'action': action,
                                'before': before, 'after': after, 'canonical_bytes_unchanged': True})
                        finally:
                            context.close()

            # A return from old bytes cannot restore obsolete view coordinates.
            context = browser.new_context(viewport={'width': 390, 'height': 900})
            try:
                page = context.new_page()
                page.goto(url + route.lstrip('/'))
                page.wait_for_function('!document.querySelector("#save-note").disabled')
                select_deep(page, 'read')
                page.locator('#reading-tools > summary').click()
                page.locator('#reading-quote').click()
                wording = page.locator('#note').input_value()
                source = base / 'sources/long.md'
                source.write_text(source.read_text(encoding='utf-8') + '\nChanged synthetic bytes.\n', encoding='utf-8')
                page.evaluate('refresh()')
                page.locator('.reading-return').first.focus()
                before = position(page)
                before_files = snapshot(root, allow_indexes=True)
                page.keyboard.press('Enter')
                assert position(page) == before
                assert page.locator('#note').input_value() == wording
                assert snapshot(root, allow_indexes=True) == before_files
                rows.append({'changed_source_return': 'refused without moving or losing wording'})
            finally:
                context.close()
        finally:
            browser.close()
    (shots / 'result.json').write_text(json.dumps(rows, indent=2) + '\n', encoding='utf-8')
    print('12 long-source quote/help returns and changed-source refusal pass in Chrome at 1280/390/320.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--browser', type=Path)
    args = parser.parse_args()
    check_native()
    if args.browser:
        check_browser(args.browser)
