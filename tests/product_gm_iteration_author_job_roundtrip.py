#!/usr/bin/env python3
"""Native/browser author job review, cancellation and truthful unowned recovery."""
import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
from agent_cancel_retry_roundtrip import config, wait_for
from course_guidance_journey_roundtrip import fixture, served, get
from a5_served_integration_roundtrip import request
from surfaces import agent_operation as ao


def waiting_adapter(root):
    script = root / 'fake_cli.txt'
    script.write_text('import json,sys,time\njson.load(sys.stdin)\ntime.sleep(30)\n', encoding='utf-8')
    cfg = config(script)
    (root / 'itembank.json').write_text(json.dumps(cfg), encoding='utf-8')
    return script, cfg


def check_native():
    with fixture() as (root, base, banks, info):
        script, cfg = waiting_adapter(root)
        target = base / 'draft.md'
        original = b'# Existing synthetic draft\n'
        target.write_bytes(original)
        first = ao.start_background('fictional-author', cfg, base)
        try:
            with served(root) as url:
                markup = get(url, '/course/synthetic/build')
                assert 'unresolved' in markup
                assert 'Cancel this request' not in markup
                assert 'may repeat provider cost' in markup
                status, _, refused = request(url + 'course/synthetic/build',
                    {'action': 'cancel', 'proposal_id': first['proposal_id']})
                assert status == 400 and 'agent.transport_unowned' in refused
                assert target.read_bytes() == original
        finally:
            ao.cancel_request(base, first['proposal_id'])
            wait_for(lambda: ao.request_history(base)[0]['request_state'] == 'settled')
    print('Native unowned job is unresolved; cancellation refuses and accepted target stays unchanged.')


def dimensions(page):
    page.evaluate('window.scrollTo({left:0,top:scrollY,behavior:"instant"})')
    return page.evaluate('({width:innerWidth,scroll:document.documentElement.scrollWidth})')


def check_browser(shots):
    from playwright.sync_api import sync_playwright
    shots.mkdir(parents=True, exist_ok=True)
    rows = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel='chrome', headless=True)
        try:
            for width in (1280, 390, 320):
                with fixture() as (root, base, banks, info):
                    script, cfg = waiting_adapter(root)
                    target = base / 'draft.md'
                    original = b'# Existing synthetic draft\n'
                    target.write_bytes(original)
                    with served(root) as url:
                        context = browser.new_context(viewport={'width': width, 'height': 900},
                            reduced_motion='reduce', color_scheme='dark' if width == 320 else 'light',
                            java_script_enabled=width != 390, has_touch=width == 320)
                        try:
                            page = context.new_page()
                            page.set_default_timeout(8000)
                            errors = []
                            page.on('pageerror', lambda error: errors.append(str(error)))
                            page.goto(url + 'course/synthetic/build')
                            start = page.get_by_role('button', name='Start fictional-author', exact=True)
                            start.focus()
                            with page.expect_navigation(wait_until='domcontentloaded'):
                                page.keyboard.press('Enter')
                            page.get_by_role('button', name='Cancel this request', exact=True).wait_for()
                            first = ao.request_history(base)[0]
                            page.reload()
                            cancel = page.get_by_role('button', name='Cancel this request', exact=True)
                            getattr(cancel, 'tap' if width == 320 else 'click')()
                            wait_for(lambda: ao.request_history(base)[0]['request_state'] == 'settled')
                            assert target.read_bytes() == original
                            candidate = {'draft': (ROOT / 'fixtures/sample_bank.md').read_text(), 'citations': []}
                            script.write_text('import json,sys\njson.load(sys.stdin)\nsys.stdout.write(' + repr(json.dumps(candidate)) + ')\n', encoding='utf-8')
                            page.get_by_role('link', name='Refresh request status', exact=True).click()
                            retry = page.get_by_role('button', name='Retry as a new request (may repeat provider cost)', exact=True)
                            retry.focus()
                            with page.expect_navigation(wait_until='domcontentloaded'):
                                page.keyboard.press('Enter')
                            child = wait_for(lambda: next((r for r in ao.request_history(base) if r['request_state'] == 'proposed'), None))
                            assert child['retry_of'] == first['operation_id']
                            assert child['proposal_id'] != first['proposal_id']
                            page.get_by_role('link', name='Refresh request status', exact=True).click()
                            page.get_by_role('button', name=re.compile('^Accept proposal ')).wait_for()
                            assert target.read_bytes() == original
                            size = dimensions(page)
                            assert size['scroll'] <= width + 1, size
                            diff = page.locator('[aria-label="Proposed change text"]')
                            diff.focus()
                            assert diff.evaluate('el => el === document.activeElement')
                            scrollable = diff.evaluate('el => el.scrollWidth > el.clientWidth + 1')
                            if scrollable:
                                page.keyboard.press('ArrowRight')
                                (shots / f'diff-diagnostic-{width}.json').write_text(json.dumps(diff.evaluate('''el => ({
                                    active:el===document.activeElement,scroll:el.scrollWidth,client:el.clientWidth,
                                    left:el.scrollLeft,overflow:getComputedStyle(el).overflowX,
                                    parentScroll:el.parentElement.scrollWidth,parentClient:el.parentElement.clientWidth,
                                    parentOverflow:getComputedStyle(el.parentElement).overflowX,
                                    parentLeft:el.parentElement.scrollLeft})'''), indent=2), encoding='utf-8')
                                wait_for(lambda: diff.evaluate('el => el.scrollLeft > 0'))
                            page.screenshot(path=str(shots / f'review-{width}.png'), full_page=True)
                            page.get_by_role('button', name=re.compile('^Accept proposal ')).focus()
                            with page.expect_navigation(wait_until='domcontentloaded'):
                                page.keyboard.press('Enter')
                            page.get_by_role('button', name=re.compile('^Undo accepted change for ')).wait_for()
                            assert target.read_text() == candidate['draft']
                            page.reload()
                            page.get_by_role('button', name=re.compile('^Undo accepted change for ')).click()
                            assert target.read_bytes() == original
                            assert dimensions(page)['scroll'] <= width + 1
                            assert not errors, errors
                            rows.append({'width': width, 'js': width != 390, 'start_cancel_retry_accept_undo': 'pass',
                                'parent_link_preserved': True, 'keyboard_diff_scroll': 'pass' if scrollable else 'not needed', **size})
                        finally:
                            context.close()

            with fixture() as (root, base, banks, info):
                script, cfg = waiting_adapter(root)
                target = base / 'draft.md'
                original = b'# Unowned synthetic target\n'
                target.write_bytes(original)
                first = ao.start_background('fictional-author', cfg, base)
                try:
                    with served(root) as url:
                        context = browser.new_context(viewport={'width': 320, 'height': 900}, java_script_enabled=False)
                        try:
                            page = context.new_page()
                            page.goto(url + 'course/synthetic/build')
                            recovery = page.get_by_role('region', name='Author request recovery', exact=True)
                            assert 'unresolved' in recovery.inner_text()
                            assert page.get_by_role('button', name='Cancel this request', exact=True).count() == 0
                            assert page.get_by_role('button', name='Retry as a new request (may repeat provider cost)', exact=True).is_visible()
                            refused = page.request.post(url + 'course/synthetic/build',
                                form={'action': 'cancel', 'proposal_id': first['proposal_id']})
                            assert refused.status == 400 and 'agent.transport_unowned' in refused.text()
                            assert target.read_bytes() == original
                            assert dimensions(page)['scroll'] <= 321
                            page.screenshot(path=str(shots / 'unresolved-320.png'), full_page=True)
                            rows.append({'unowned_restart': 'truthful unresolved state and cancellation refusal'})
                        finally:
                            context.close()
                finally:
                    ao.cancel_request(base, first['proposal_id'])
                    wait_for(lambda: ao.request_history(base)[0]['request_state'] == 'settled')
        finally:
            browser.close()
    (shots / 'result.json').write_text(json.dumps(rows, indent=2) + '\n', encoding='utf-8')
    print('Chrome 1280/390/320 author actions, narrow layout, keyboard diff and script-free unowned recovery pass.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--browser', type=Path)
    args = parser.parse_args()
    check_native()
    if args.browser:
        check_browser(args.browser)
