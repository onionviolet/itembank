#!/usr/bin/env python3
"""Source-only synthetic reference detours preserve draft and reading position."""
import argparse
import json
from pathlib import Path
import sys
import tempfile
import urllib.parse

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
import evidence
from daemon_roundtrip import start_daemon, get
from quiz_symbol_return_roundtrip import BANK, Page


def check(browser=False):
    with tempfile.TemporaryDirectory(prefix='quiz-reference-continuity-') as temp:
        bank = BANK.replace('Read P in the first invented example.',
                            'Read P in the first invented example. ' +
                            'Read this fictional explanation before choosing a color. ' * 75)
        Path(temp, 'symbols.md').write_text(bank)
        proc, base, _ = start_daemon(temp)
        try:
            _, raw = get(base + 'quiz/symbols?mode=practice')
            parsed = Page(raw)
            assert 'data-presentation-signature=' in raw
            assert parsed.card['data-item-id']
            if not browser:
                print('Public revision-scoped native quiz return metadata passes')
                return
            from playwright.sync_api import sync_playwright
            with sync_playwright() as pw:
                chrome = pw.chromium.launch(channel='chrome', headless=True)
                results = []
                for width in (1280, 390):
                    context = chrome.new_context(viewport={'width': width, 'height': 800},
                                                 reduced_motion='reduce')
                    page = context.new_page()
                    page.goto(base + 'quiz/symbols?mode=practice')
                    page.wait_for_load_state('networkidle')
                    card = page.locator('[data-server-baseline]').first
                    sitting = card.get_attribute('data-session-id')
                    item = card.get_attribute('data-item-id')
                    radio = page.get_by_role('radio').first
                    radio.focus()
                    page.keyboard.press('Space')
                    assert radio.is_checked()
                    page.evaluate('window.scrollTo(0, document.documentElement.scrollHeight)')
                    prior_y = page.evaluate('window.scrollY')
                    assert prior_y > 100
                    target = page.locator('a[data-gloss-fetch]').first.get_attribute('href')
                    page.goto(urllib.parse.urljoin(base, target))
                    page.locator('a[href*="/quiz/"]').last.click()
                    page.wait_for_load_state('networkidle')
                    page.wait_for_function('(y)=>Math.abs(scrollY-y)<3', arg=prior_y)
                    assert page.get_by_role('radio').first.is_checked()
                    assert page.locator('[data-server-baseline]').first.get_attribute('data-session-id') == sitting
                    assert page.locator('[data-server-baseline]').first.get_attribute('data-item-id') == item
                    assert page.evaluate('document.activeElement.type') == 'radio'
                    page.reload()
                    page.wait_for_load_state('networkidle')
                    assert page.get_by_role('radio').first.is_checked()
                    page.wait_for_function('(y)=>Math.abs(scrollY-y)<3', arg=prior_y)
                    # Draft and position are browser state, never an attempt.
                    assert not [event for event in evidence.live_events(evidence.log_path(temp))
                                if event.get('event_type') == 'response']
                    results.append({'width': width, 'scroll_y': prior_y, 'draft': 'A',
                                    'same_sitting': True, 'same_item': True})
                    context.close()
                chrome.close()
                print(json.dumps(results))
        finally:
            proc.terminate()
            proc.wait(timeout=10)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--browser', action='store_true')
    check(parser.parse_args().browser)
