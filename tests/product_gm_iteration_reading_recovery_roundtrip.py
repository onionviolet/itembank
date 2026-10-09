#!/usr/bin/env python3
"""Native quote, note save and explicit stale-draft recovery on synthetic data."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
from course_guidance_journey_roundtrip import fixture, served, snapshot, get
from reading_desk_roundtrip import ReadingDesk


def check_native():
    case = ReadingDesk('test_live_http_route_and_note')
    case.setUp()
    try:
        row = case.create()['occurrence']
        wording = 'Saved synthetic wording 中文\n  Original spacing.'
        case.save(row, wording)
        root = Path(case.root)
        base = Path(case.base)
        source = base / 'sources/example.md'
        source.write_text(source.read_text(encoding='utf-8') + '\nChanged synthetic source.\n', encoding='utf-8')
        from surfaces.reading_desk import href
        with served(root) as url:
            before = snapshot(root, allow_indexes=True)
            markup = get(url, href('synthetic', row))
            assert wording in markup
            assert 'The source changed' in markup
            assert '<button id="recover-reading-draft" type="button" hidden>' in markup
            assert snapshot(root, allow_indexes=True) == before
    finally:
        case.doCleanups()
    print('Native stale-source static saved notes retain exact wording without mutation.')


def check_browser(shots):
    from playwright.sync_api import sync_playwright
    shots.mkdir(parents=True, exist_ok=True)
    measured = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel='chrome', headless=True)
        try:
            for width in (1280, 390, 320):
                with fixture() as (root, base, banks, meta), served(root) as url:
                    context = browser.new_context(viewport={'width': width, 'height': 900},
                        color_scheme='dark' if width == 320 else 'light', reduced_motion='reduce',
                        has_touch=width == 320)
                    try:
                        page = context.new_page()
                        page.set_default_timeout(8000)
                        errors = []
                        page.on('pageerror', lambda error: errors.append(str(error)))
                        page.on('dialog', lambda dialog: dialog.accept())
                        page.goto(url + meta['reading'].lstrip('/'))
                        page.wait_for_function('!document.querySelector("#save-note").disabled')
                        before = snapshot(root, allow_indexes=True)
                        selected = page.locator('#source-content').evaluate('''el => {
                            const text = el.firstChild;
                            const end = Math.min(18, text.length);
                            const range = document.createRange();
                            range.setStart(text, 0); range.setEnd(text, end);
                            const selection = window.getSelection();
                            selection.removeAllRanges(); selection.addRange(range);
                            return selection.toString().trim();
                        }''')
                        activate = 'tap' if width == 320 else 'click'
                        getattr(page.locator('#reading-tools > summary'), activate)()
                        assert page.evaluate('window.getSelection().toString().trim()') == selected
                        getattr(page.locator('#reading-help-selection'), activate)()
                        assert selected in page.locator('#help-selection-state').inner_text()
                        assert page.locator('#help-question').evaluate('el => el === document.activeElement')
                        assert snapshot(root, allow_indexes=True) == before
                        page.locator('#help-return').click()
                        assert page.evaluate('window.getSelection().toString().trim()') == selected
                        getattr(page.locator('#reading-tools > summary'), activate)()
                        getattr(page.locator('#reading-quote'), activate)()
                        quote = 'Source passage: ' + selected + '\nMy thought: '
                        assert page.locator('#note').input_value() == quote, {
                            'expected': quote,
                            'actual': page.locator('#note').input_value(),
                            'selection': page.evaluate('window.getSelection().toString()'),
                            'state': page.locator('#reading-tools-state').inner_text(),
                        }
                        assert page.locator('#reading-tools').get_attribute('open') is None
                        assert snapshot(root, allow_indexes=True) == before
                        saved_wording = quote + 'Fictional comparison 中文\n  Keep this spacing.'
                        page.locator('#note').fill(saved_wording)
                        page.locator('#save-note').click()
                        page.wait_for_function('document.querySelector("#note").value === ""')
                        page.reload()
                        page.wait_for_function('!document.querySelector("#save-note").disabled')
                        assert saved_wording in page.locator('#saved-notes').inner_text()
                        prior = 'Unsaved later thought 中文\n  Distinct from saved notes.'
                        page.locator('#note').fill(prior)
                        page.get_by_role('button', name='Read', exact=True).click()
                        source = base / 'sources/example.md'
                        source.write_text(source.read_text(encoding='utf-8') + '\nChanged synthetic source.\n', encoding='utf-8')
                        page.reload()
                        recovery = page.get_by_role('button', name='Review previous unsaved draft', exact=True)
                        recovery.wait_for(state='visible')
                        assert page.locator('.reading-notes').is_hidden()
                        assert page.locator('#save-note').is_disabled()
                        assert page.locator('#mark-read').is_disabled()
                        page.screenshot(path=str(shots / f'recovery-action-{width}.png'))
                        before = snapshot(root, allow_indexes=True)
                        storage = page.evaluate('''Object.fromEntries(Object.entries(sessionStorage)
                            .filter(([key]) => key.startsWith('itembank-reading:') && !key.endsWith(':workspace')))''')
                        recovery.focus()
                        page.keyboard.press('Enter')
                        field = page.locator('#previous-drafts textarea')
                        assert field.is_visible()
                        assert field.input_value() == prior
                        assert field.evaluate('el => el.readOnly && el === document.activeElement')
                        assert page.locator('#note').input_value() == ''
                        assert saved_wording in page.locator('#saved-notes').inner_text()
                        assert page.locator('#save-note').is_disabled()
                        assert page.locator('#mark-read').is_disabled()
                        assert page.evaluate('''Object.fromEntries(Object.entries(sessionStorage)
                            .filter(([key]) => key.startsWith('itembank-reading:') && !key.endsWith(':workspace')))''') == storage
                        assert snapshot(root, allow_indexes=True) == before
                        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
                        assert not errors, errors
                        page.screenshot(path=str(shots / f'recovered-draft-{width}.png'))
                        measured.append({'width': width, 'quote_save_reload': 'pass',
                            'help_exact_selection_without_provider_call': 'pass',
                            'stale_draft_keyboard_recovery': 'pass', 'canonical_state_unchanged': True})
                    finally:
                        context.close()
                    static = browser.new_context(viewport={'width': width, 'height': 900}, java_script_enabled=False)
                    try:
                        page = static.new_page()
                        before = snapshot(root, allow_indexes=True)
                        page.goto(url + meta['reading'].lstrip('/'))
                        assert saved_wording in page.locator('#saved-notes').inner_text()
                        assert page.locator('#recover-reading-draft').is_hidden()
                        assert snapshot(root, allow_indexes=True) == before
                    finally:
                        static.close()
        finally:
            browser.close()
    (shots / 'result.json').write_text(json.dumps(measured, indent=2) + '\n', encoding='utf-8')
    print('Chrome 1280/390/320 quote/save/reload, keyboard draft recovery and script-free saved notes pass.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--browser-shots', type=Path)
    args = parser.parse_args()
    check_native()
    if args.browser_shots:
        check_browser(args.browser_shots)
