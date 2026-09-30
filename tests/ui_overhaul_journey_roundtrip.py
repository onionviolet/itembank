#!/usr/bin/env python3
"""Synthetic source journey, exact return, reload and refused note retry."""
import argparse
import html
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import urllib.parse

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
import course
import evidence
import runtime
from surfaces import daemon, reading_desk, settings, theme
from reading_desk_roundtrip import ReadingDesk
from quiz_symbol_return_roundtrip import BANK, Page
from daemon_roundtrip import start_daemon, json_request
from a5_served_integration_roundtrip import request


def fixture(destination=None):
    case = ReadingDesk('test_live_http_route_and_note')
    case.setUp()
    row = case.create()['occurrence']
    bank = BANK.replace('Q1.', '## LESSON\n\n### Invented color rule\n\n'
                        + ('Read the invented rule carefully. 中文 source context remains readable. ' * 90)
                        + '\n\nQ1.', 1)
    Path(case.base, 'symbols.md').write_text(bank, encoding='utf-8')
    Path(case.root, 'itembank.json').write_text(json.dumps({'theme': 'system'}))
    root = case.root
    if destination:
        shutil.copytree(root, destination)
        root = str(destination)
    metadata = {'course': 'synthetic', 'reading': reading_desk.href('synthetic', row),
                'row': row, 'fingerprint': case.read()['fingerprint']}
    return case, root, metadata


def snapshot(root):
    return {str(p.relative_to(root)): p.read_bytes() for p in Path(root).rglob('*') if p.is_file()}


def check_http(root, meta):
    proc, url, _ = start_daemon(root)
    try:
        before = snapshot(root)
        for route in ('', 'courses', 'course/synthetic', meta['reading'].lstrip('/')):
            status, _, page = request(url + route)
            assert status == 200, (route, status)
            expected = 'First synthetic paragraph.' if '/reading/' in route else 'Synthetic reading'
            assert expected in page, route
        assert snapshot(root) == before, 'entry and reading GETs mutated accepted files'
        config_path = Path(root, 'itembank.json')
        prior_config = config_path.read_bytes()
        try:
            config_path.write_text(json.dumps({'theme': 'dark', 'accent': {'source': '#0e6e62'}}))
            themed = request(url + meta['reading'].lstrip('/'))[2]
            assert theme.theme_css(settings.load_settings(root)) in themed, 'reading ignored saved theme/accent'
        finally:
            config_path.write_bytes(prior_config)
        context = dict(course_id='synthetic', expected_fingerprint=meta['fingerprint'],
                       occurrence_id=meta['row']['occurrence_id'], revision_id=meta['row']['revision_id'])
        body = dict(context, note_id='f' * 32, wording='Synthetic private note', notes_fingerprint=None)
        assert json_request(url + 'api/course/save-reading-note', body)[0] == 200
        body.update(note_id='e' * 32, wording='Keep refused draft')
        accepted = snapshot(root)
        assert json_request(url + 'api/course/save-reading-note', body)[0] == 400
        assert snapshot(root) == accepted, 'refused save changed accepted bytes'
        status, view = json_request(url + 'api/course/reading-view', context)
        assert status == 200
        body['notes_fingerprint'] = view['notes_fingerprint']
        assert json_request(url + 'api/course/save-reading-note', body)[0] == 200
        assert 'Keep refused draft' in request(url + meta['reading'].lstrip('/'))[2]
        for mode in ('practice', 'exam'):
            route = 'quiz/symbols?' + urllib.parse.urlencode({'mode': mode, 'course': 'synthetic'})
            status, _, page = request(url + route)
            assert status == 200
            parsed = Page(page)
            sid = parsed.card['data-session-id']
            item = parsed.card['data-item-id']
            resume = '/quiz/symbols?' + urllib.parse.urlencode({'mode': mode, 'session': sid, 'course': 'synthetic'})
            symbol = next(link for link in parsed.links if 'data-gloss-fetch' in link)
            events = list(evidence.live_events(evidence.log_path(root)))
            definition = request(urllib.parse.urljoin(url, html.unescape(symbol['href'])))[2]
            back = Page(definition).links[0]['href']
            returned = Page(request(urllib.parse.urljoin(url, html.unescape(back)))[2])
            assert returned.card['data-session-id'] == sid and returned.card['data-item-id'] == item
            lesson = request(url + 'lesson/symbols?' + urllib.parse.urlencode({'return': resume}))[2]
            assert 'Return to saved sitting' in lesson and 'Invented color rule' in lesson
            assert list(evidence.live_events(evidence.log_path(root))) == events, 'reference detour recorded a response'
            status, _, answered = request(urllib.parse.urljoin(url, parsed.answer_path),
                {'action': 'submit', 'form_token': parsed.form_token, 'option': 'A'})
            assert status == 200
            saved = runtime.read_session(daemon.session_index(root)[sid])
            assert saved['responses'][0]['answer'] == 'A'
            if mode == 'exam':
                assert 'The invented rule selects the second color.' not in answered
            reloaded = Page(request(url + resume.lstrip('/'))[2])
            assert reloaded.card['data-session-id'] == sid
            assert len(runtime.read_session(daemon.session_index(root)[sid])['responses']) == 1
        return url
    finally:
        proc.terminate()
        proc.wait(timeout=10)


def check_browser(root, meta, shots):
    from playwright.sync_api import sync_playwright
    bank = Path(root, 'synthetic', 'symbols.md').read_text()
    for width in (1280, 390):
        for scheme in ('light', 'dark'):
            Path(root, 'synthetic', f'browser_{width}_{scheme}.md').write_text(bank)
    proc, url, _ = start_daemon(root)
    shots.mkdir(parents=True, exist_ok=True)
    measured = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(channel='chrome', headless=True)
            for width in (1280, 390):
                for scheme in ('light', 'dark'):
                    context = browser.new_context(viewport={'width': width, 'height': 900}, color_scheme=scheme,
                                                  reduced_motion='reduce')
                    page = context.new_page()
                    routes = {'home': '', 'courses': 'courses', 'course': 'course/synthetic',
                              'reading': meta['reading'].lstrip('/'), 'lesson': 'lesson/symbols',
                              'practice': f'quiz/browser_{width}_{scheme}?mode=practice&course=synthetic'}
                    for name, route in routes.items():
                        page.goto(url + route)
                        page.wait_for_load_state('networkidle')
                        size = page.evaluate('({width:innerWidth, scroll:document.documentElement.scrollWidth})')
                        assert size['scroll'] <= size['width'] + 1, (name, width, scheme, size)
                        page.screenshot(path=str(shots / f'{name}-{width}-{scheme}.png'), full_page=True)
                        measured.append(dict(surface=name, scheme=scheme, **size))
                    page.goto(url)
                    page.get_by_role('link', name='Synthetic reading', exact=True).first.click()
                    assert '/course/' in page.url
                    page.goto(url + meta['reading'].lstrip('/'))
                    page.wait_for_load_state('networkidle')
                    page.locator('#note').fill('Recover this synthetic browser draft 中文')
                    def refuse(route):
                        route.fulfill(status=503, content_type='application/json', body='{"error":"synthetic save fault"}')
                    page.route('**/api/course/save-reading-note', refuse)
                    page.locator('#save-note').click()
                    page.wait_for_function('document.querySelector("#save-state").textContent.includes("Request refused")')
                    assert page.locator('#note').input_value() == 'Recover this synthetic browser draft 中文'
                    page.reload()
                    page.wait_for_load_state('networkidle')
                    assert page.locator('#note').input_value() == 'Recover this synthetic browser draft 中文'
                    page.unroute('**/api/course/save-reading-note', refuse)
                    page.locator('#save-note').click()
                    page.wait_for_function('document.querySelector("#save-state").textContent.includes("Saved to your notes")')
                    page.wait_for_function('document.querySelector("#saved-notes").textContent.includes("Recover this synthetic browser draft 中文")')
                    assert 'Recover this synthetic browser draft 中文' in page.locator('#saved-notes').inner_text()
                    page.locator('#note').focus()
                    page.keyboard.press('Tab')
                    focus = page.evaluate('({tag:document.activeElement.tagName,outline:getComputedStyle(document.activeElement).outlineStyle})')
                    assert focus['tag'] != 'BODY' and focus['outline'] != 'none', focus
                    page.goto(url + routes['practice'])
                    page.wait_for_load_state('networkidle')
                    card = page.locator('[data-server-baseline]').first
                    sid, item = card.get_attribute('data-session-id'), card.get_attribute('data-item-id')
                    symbol = page.locator('a[data-gloss-fetch]').first
                    target = symbol.get_attribute('href')
                    page.goto(urllib.parse.urljoin(url, target))
                    page.locator('a').first.click()
                    page.wait_for_load_state('networkidle')
                    card = page.locator('[data-server-baseline]').first
                    assert card.get_attribute('data-session-id') == sid and card.get_attribute('data-item-id') == item
                    page.reload()
                    page.wait_for_load_state('networkidle')
                    assert page.locator('[data-server-baseline]').first.get_attribute('data-session-id') == sid
                    radio = page.get_by_role('radio').first
                    radio.focus()
                    page.keyboard.press('Space')
                    assert radio.is_checked(), 'keyboard did not select a native answer'
                    saved_path = daemon.session_index(root)[sid]
                    response_count = len(runtime.read_session(saved_path)['responses'])
                    with page.expect_response(lambda response: '/answer' in response.url
                                              and response.request.method == 'POST'):
                        page.get_by_role('button', name='Submit answer', exact=True).click()
                    assert len(runtime.read_session(saved_path)['responses']) == response_count + 1
                    page.reload()
                    page.wait_for_load_state('networkidle')
                    assert len(runtime.read_session(saved_path)['responses']) == response_count + 1
                    context.close()
            browser.close()
        (shots / 'measurements.json').write_text(json.dumps(measured, indent=2))
        print('Chrome source journey: 24 surface/width/theme observations, keyboard focus, refused-save draft/reload/retry and exact reference return pass')
    finally:
        proc.terminate()
        proc.wait(timeout=10)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preview-root', type=Path)
    parser.add_argument('--browser-shots', type=Path)
    args = parser.parse_args()
    case, root, meta = fixture(args.preview_root)
    try:
        check_http(root, meta)
        if args.browser_shots:
            check_browser(root, meta, args.browser_shots)
        if args.preview_root:
            (args.preview_root / 'preview.json').write_text(json.dumps(meta, indent=2))
            print('Synthetic preview root: ' + str(args.preview_root))
    finally:
        case.doCleanups()
    print('UI overhaul journey: read-only entry, reading save/refusal/retry, exact reference return, practice/exam disclosure and reload pass')


if __name__ == '__main__':
    main()
