#!/usr/bin/env python3
"""Independent native Chrome continuity variants on disposable fictional banks."""
import argparse
import json
from pathlib import Path
import sys
import urllib.parse

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
from daemon_roundtrip import start_daemon
from quiz_symbol_return_roundtrip import BANK
from ui_overhaul_journey_roundtrip import fixture
from staged_checker_ui_roundtrip import response_events


def check(shots):
    from playwright.sync_api import sync_playwright
    case, root, _ = fixture()
    bank = BANK.replace('Read P in the first invented example.',
                        'Read P in the first invented example. ' + 'Read the fictional rule before choosing. ' * 100)
    for width in (1280, 390, 320):
        Path(root, 'synthetic', f'continuity_{width}.md').write_text(bank)
        Path(root, 'synthetic', f'held_{width}.md').write_text(BANK)
    Path(root, 'synthetic/storage_refusal.md').write_text(bank)
    proc, base, _ = start_daemon(root)
    shots.mkdir(parents=True, exist_ok=True)
    measured = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(channel='chrome', headless=True)
            for width in (1280, 390, 320):
                ctx = browser.new_context(viewport={'width': width, 'height': 800}, reduced_motion='reduce')
                page = ctx.new_page()
                page.goto(base + f'quiz/continuity_{width}?mode=practice&course=synthetic')
                page.wait_for_load_state('networkidle')
                card = page.locator('[data-server-baseline]')
                sid = card.get_attribute('data-session-id')
                iid = card.get_attribute('data-item-id')
                resume = page.url + '&session=' + sid
                radio = page.get_by_role('radio').first
                radio.focus()
                page.keyboard.press('Space')
                page.evaluate('window.scrollTo(0,document.documentElement.scrollHeight)')
                y = page.evaluate('scrollY')
                target = page.locator('a[data-gloss-fetch]').first.get_attribute('href')
                page.goto(urllib.parse.urljoin(base, target))
                page.locator('a[href*="/quiz/"]').last.click()
                page.wait_for_load_state('networkidle')
                page.wait_for_function('(y)=>Math.abs(scrollY-y)<3', arg=y)
                assert radio.is_checked() and page.evaluate('document.activeElement.type') == 'radio'
                assert card.get_attribute('data-session-id') == sid and card.get_attribute('data-item-id') == iid
                page.screenshot(path=str(shots / f'reference-return-{width}.png'), full_page=True)
                # Browser Back is a separate path from the definition's return link.
                page.goto(urllib.parse.urljoin(base, target))
                page.go_back()
                page.wait_for_load_state('networkidle')
                assert radio.is_checked()
                # A resized return uses the surviving control anchor, not old coordinates.
                radio.focus()
                page.goto(urllib.parse.urljoin(base, target))
                other_width = 390 if width == 320 else 320
                page.set_viewport_size({'width': other_width, 'height': 800})
                page.locator('a[href*="/quiz/"]').last.click()
                page.wait_for_load_state('networkidle')
                assert radio.is_checked()
                page.wait_for_function('document.activeElement.type === "radio"')
                box = radio.bounding_box()
                assert 0 <= box['y'] <= 700, box
                # Popover help keeps exact occurrence focus and closes with Escape.
                symbol = page.locator('a[data-gloss-fetch]').first
                symbol.focus()
                page.keyboard.press('Enter')
                page.wait_for_selector('.gloss:popover-open')
                page.keyboard.press('Escape')
                assert page.locator('.gloss:popover-open').count() == 0
                assert symbol.evaluate('(el)=>el===document.activeElement')
                assert page.evaluate('document.documentElement.scrollWidth') == other_width
                assert not response_events(root, sid), 'reference/help recorded an answer'
                # Public revision change visibly discards the old choice and position.
                radio.focus()
                page.goto(urllib.parse.urljoin(base, target))
                source = Path(root, 'synthetic', f'continuity_{width}.md')
                source.write_text(bank.replace('A) Orange', 'A) A different fictional color'))
                page.locator('a[href*="/quiz/"]').last.click()
                page.wait_for_load_state('networkidle')
                assert not radio.is_checked()
                assert 'older question revision' in page.locator('[data-answer-form]').inner_text()
                assert page.evaluate('document.activeElement.tagName') == 'H1'
                assert not response_events(root, sid)
                # A wrong ordinary response is genuinely HELD, then its course detour
                # preserves the exact runtime item and response count.
                page.goto(base + f'quiz/held_{width}?mode=practice&course=synthetic')
                page.wait_for_load_state('networkidle')
                sid = card.get_attribute('data-session-id')
                iid = card.get_attribute('data-item-id')
                resume = page.url + '&session=' + sid
                radio.check()
                page.get_by_role('button', name='Submit answer', exact=True).click()
                page.wait_for_load_state('networkidle')
                assert 'Not correct. Re-read the question' in page.locator('.feedback').inner_text()
                assert not page.locator('[data-feedback-pause]').count()
                assert len(response_events(root, sid)) == 1
                course_link = page.locator('a[href="/course/synthetic"]').first
                assert course_link.count() == 1
                course_link.click()
                page.wait_for_load_state('networkidle')
                assert '/course/synthetic' in page.url
                page.goto(resume)
                page.wait_for_load_state('networkidle')
                assert card.get_attribute('data-session-id') == sid and card.get_attribute('data-item-id') == iid
                assert len(response_events(root, sid)) == 1
                measured.append({'width': width, 'resized': other_width, 'same_sitting': True,
                                 'revision_notice': True, 'held_course_return': True})
                ctx.close()
            ctx = browser.new_context(viewport={'width': 320, 'height': 800})
            ctx.add_init_script('Storage.prototype.getItem=function(){throw new Error("synthetic unavailable storage")}; Storage.prototype.setItem=function(){throw new Error("synthetic unavailable storage")};')
            page = ctx.new_page()
            page.goto(base + 'quiz/storage_refusal?course=synthetic')
            page.wait_for_load_state('networkidle')
            sid = page.locator('[data-server-baseline]').get_attribute('data-session-id')
            page.get_by_role('radio').first.check()
            target = page.locator('a[data-gloss-fetch]').first.get_attribute('href')
            page.goto(urllib.parse.urljoin(base, target))
            page.locator('a[href*="/quiz/"]').last.click()
            page.wait_for_load_state('networkidle')
            assert page.get_by_role('button', name='Submit answer', exact=True).is_enabled()
            assert page.locator('[data-server-baseline]').get_attribute('data-session-id') == sid
            assert not response_events(root, sid)
            ctx.close()
            browser.close()
        (shots / 'continuity-measurements.json').write_text(json.dumps(measured, indent=2))
        print('Chrome 1280/390/320: explicit return, Back, resize, key-free help, revision notice, held course detour and unavailable storage pass')
    finally:
        proc.terminate()
        proc.wait(timeout=10)
        case.tearDown()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--browser-shots', type=Path)
    args = parser.parse_args()
    if args.browser_shots:
        check(args.browser_shots)
    else:
        print('Use --browser-shots PATH for the optional installed Chrome continuity journey.')
