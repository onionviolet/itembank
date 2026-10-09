#!/usr/bin/env python3
"""Verify the frozen UI programme on a disposable native learner journey."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys
import urllib.parse

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
import runtime
from course_guidance_journey_roundtrip import fixture, served, get, snapshot

SPEC = importlib.util.spec_from_file_location(
    'ui_gm_native', ROOT / 'prototypes/ui-character-20261001/native-preview.py')
PREVIEW = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PREVIEW)


def check_native():
    with fixture() as (root, base, banks, meta), served(root) as url:
        course_id, sitting = PREVIEW.prepare_course(root, url)
        saved = root / '_attempts/session_boundary_workshop.json'
        before = snapshot(root, allow_indexes=True, timed_sitting=saved)
        pages = [get(url, route) for route in (
            '/course/' + course_id, '/course/' + course_id + '/learn',
            '/lesson/coding_boundary_unit', meta['reading'],
            '/quiz/coding_boundary_unit?mode=practice&session=' +
            sitting['session_id'] + '&course=' + course_id)]
        assert all('CORRECT:' not in markup for markup in pages)
        after = snapshot(root, allow_indexes=True, timed_sitting=saved)
        # Opening this saved sitting creates its existing serialization lock.
        # Only that coordination file and served_ts are disposable view effects.
        lock = str(saved.relative_to(root)) + '.lock'
        before.pop(lock, None)
        after.pop(lock, None)
        assert after == before, {key: ('added' if key not in before else 'changed')
            for key, value in after.items() if before.get(key) != value}
        assert runtime.read_session(str(saved))['responses'] == []
        assert 'Reading tools' in pages[3] and 'Source available.' in pages[3]
        assert 'A note to yourself' in pages[3] and '<noscript>' in pages[3]
    print('UI native journey: read-only entry, public content, source/notes and exact sitting pass')


def check_browser(shots):
    from playwright.sync_api import sync_playwright
    shots.mkdir(parents=True, exist_ok=True)
    measured = []
    with fixture() as (root, base, banks, meta), served(root) as url:
        course_id, sitting = PREVIEW.prepare_course(root, url)
        saved = root / '_attempts/session_boundary_workshop.json'
        with sync_playwright() as pw:
            browser = pw.chromium.launch(channel='chrome', headless=True)
            for width, scheme in ((1280, 'light'), (390, 'light'), (320, 'dark')):
                context = browser.new_context(viewport={'width': width, 'height': 900},
                    color_scheme=scheme, reduced_motion='reduce')
                page = context.new_page()
                page.set_default_timeout(8000)
                page.goto(url + 'course/' + course_id)
                learn_link = page.locator(f'a[href="/course/{course_id}/learn"]:visible')
                if not learn_link.count():
                    page.locator('.course-nav-mobile summary').click()
                page.locator(f'a[href="/course/{course_id}/learn"]:visible').first.click()
                page.locator('a[href^="/lesson/coding_boundary_unit"]').first.click()
                assert page.locator('#lesson-content h2').count() >= 4
                assert page.locator('h1').count() == 1
                outline = page.locator('.reader-nav summary')
                outline.focus()
                page.keyboard.press('Enter')
                assert page.locator('.reader-nav details').get_attribute('open') is not None
                page.locator('.reader-nav a').first.click()
                assert urllib.parse.urlparse(page.url).fragment
                page.locator('.bl summary').first.click()
                section_link = page.locator('.bl a').first
                href = section_link.get_attribute('href')
                query = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                assert query['course'] == [course_id], href
                # A Learn entry has no sitting return request. Verify course
                # context first, then the daemon's existing exact-return seam.
                assert 'session' not in query, href
                assert '```' not in page.locator('.bl').first.inner_text()
                exact = '/quiz/coding_boundary_unit?' + urllib.parse.urlencode({
                    'mode': 'practice', 'session': sitting['session_id'], 'course': course_id})
                page.goto(url + 'lesson/coding_boundary_unit?' +
                    urllib.parse.urlencode({'course': course_id, 'return': exact}))
                page.locator('.bl summary').first.click()
                section_link = page.locator('.bl a').first
                query = urllib.parse.parse_qs(urllib.parse.urlparse(section_link.get_attribute('href')).query)
                assert query['course'] == [course_id]
                assert query['session'] == [sitting['session_id']]
                assert section_link.inner_text() == 'Return to saved sitting'
                section_link.click()
                card = page.locator('[data-server-baseline]').first
                item_id = card.get_attribute('data-item-id')
                assert card.get_attribute('data-session-id') == sitting['session_id']
                radio = page.get_by_role('radio').first
                radio.focus()
                page.keyboard.press('Space')
                choice = radio.get_attribute('value')
                page.locator(f'a[href="/course/{course_id}"]').first.click()
                page.locator(f'a[href*="session={sitting["session_id"]}"]').first.click()
                assert page.locator('[data-server-baseline]').first.get_attribute('data-item-id') == item_id
                assert page.locator(f'input[type="radio"][value="{choice}"]').is_checked()
                page.reload()
                assert page.locator(f'input[type="radio"][value="{choice}"]').is_checked()
                assert runtime.read_session(str(saved))['responses'] == []
                page.screenshot(path=str(shots / f'exact-practice-return-{width}.png'))

                page.goto(url + meta['reading'].lstrip('/'))
                page.wait_for_function('!document.querySelector("#save-note").disabled')
                summary = page.locator('#reading-tools > summary')
                summary.focus()
                page.keyboard.press('Enter')
                select_help = page.locator('#reading-help-selection')
                select_help.focus()
                page.keyboard.press('Enter')
                assert page.locator('#reading-tools').get_attribute('open') is not None
                assert select_help.evaluate('(el) => el === document.activeElement')
                assert 'Select words inside the source passage' in page.locator('#reading-tools-state').inner_text()
                page.locator('#reading-size').focus()
                page.keyboard.press('Escape')
                assert page.locator('#reading-tools').get_attribute('open') is None
                assert summary.evaluate('(el) => el === document.activeElement')
                page.get_by_role('button', name='Read', exact=True).click()
                passage_y = page.evaluate('scrollY')
                page.get_by_role('button', name='Write a note', exact=True).click()
                wording = 'Keep this fictional thought 中文 ' + str(width)
                page.locator('#note').fill(wording)
                page.locator('.reading-return').first.click()
                assert page.locator('.reading-layout').get_attribute('data-reading-mode') == 'read'
                assert page.locator('#source-content').evaluate('(el) => el === document.activeElement')
                assert abs(page.evaluate('scrollY') - passage_y) <= 2
                page.get_by_role('button', name='Write a note', exact=True).click()
                assert page.locator('#note').input_value() == wording
                page.on('dialog', lambda dialog: dialog.accept())
                def refuse(route):
                    route.fulfill(status=503, content_type='application/json', body='{}')
                page.route('**/api/course/save-reading-note', refuse)
                page.locator('#save-note').click()
                page.wait_for_function('document.querySelector("#save-state").textContent.includes("Request refused")')
                assert page.locator('#note').input_value() == wording
                page.reload()
                page.wait_for_function('document.querySelector("#note").value.includes("fictional thought")')
                page.unroute('**/api/course/save-reading-note', refuse)
                page.locator('#save-note').click()
                page.wait_for_function('document.querySelector("#saved-notes").textContent.includes("' + wording + '")')
                assert page.locator('#note').input_value() == ''
                page.get_by_role('button', name='Study', exact=True).click()
                size = page.evaluate('({width:innerWidth,scroll:document.documentElement.scrollWidth})')
                assert size['scroll'] <= width + 1, size
                page.screenshot(path=str(shots / f'reader-saved-note-{width}.png'))
                measured.append({'width': width, 'scheme': scheme, 'course': course_id,
                    'session': sitting['session_id'], 'item': item_id, 'draft_and_note': 'pass',
                    'source_scroll_return': 'pass', 'keyboard_tools': 'pass', **size})
                context.close()

            context = browser.new_context(viewport={'width': 320, 'height': 900})
            page = context.new_page()
            page.goto(url + meta['reading'].lstrip('/'))
            page.wait_for_function('!document.querySelector("#save-note").disabled')
            page.locator('#note').fill('Previous-source draft must remain copyable')
            page.on('dialog', lambda dialog: dialog.accept())
            source = base / 'sources/example.md'
            source.write_text(source.read_text() + '\nChanged fictional source.\n', encoding='utf-8')
            page.reload()
            page.wait_for_function('document.querySelector("#previous-drafts textarea") !== null')
            assert page.locator('#previous-drafts textarea').input_value() == 'Previous-source draft must remain copyable'
            assert page.locator('#save-note').is_disabled()
            assert page.locator('#mark-read').is_disabled()
            assert 'changed' in page.locator('#source-state').inner_text().lower()
            page.screenshot(path=str(shots / 'stale-source-320.png'))
            measured.append({'stale_source': 'explicit refusal; copyable prior draft; saved notes retained'})
            context.close()
            browser.close()
    (shots / 'result.json').write_text(json.dumps(measured, indent=2), encoding='utf-8')
    print('UI Chrome journey: section practice, exact draft return/reload, keyboard tools, source scroll, note refusal/retry and stale source pass')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--browser-shots', type=Path)
    args = parser.parse_args()
    check_native()
    if args.browser_shots:
        check_browser(args.browser_shots)


if __name__ == '__main__':
    main()
