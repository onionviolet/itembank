"""Preview or inspect the native reading modes on disposable original material."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
from daemon_roundtrip import start_daemon
from reading_desk_roundtrip import ReadingDesk
from surfaces.reading_desk import href

PARAGRAPH = (
    'A trail counter records visitors at a checkpoint. The first system counts '
    'people when they enter; the second counts people when they leave. Both '
    'totals are useful, but they answer different questions. To compare them, '
    'choose the same time window and decide how to handle someone still on the '
    'trail when that window ends. A boundary rule is part of the claim, not a '
    'detail to add after calculating a result. '
)
PASSAGE = PARAGRAPH + (
    'Suppose five people enter between noon and one o\'clock. Three leave '
    'during that hour and two leave later. The entry counter reports five; '
    'the exit counter reports three. Neither number is a mistake. The first '
    'describes arrivals and the second describes departures. If someone asks '
    'how busy the trail was, we need a clearer question before choosing a total. '
    'For a staffing decision, the useful quantity might be the number of people '
    'on the trail at each moment. An arrival increases that number, while a '
    'departure decreases it. A count of either event alone cannot show the full '
    'pattern. Keeping the events in time order lets us reconstruct the pattern, '
    'provided we also know how many people were present at the start. '
    'Now consider a person who arrives at exactly one o\'clock. If the first '
    'window includes that endpoint and the next window includes its starting '
    'point, the same arrival appears twice. A consistent rule can include each '
    'window\'s start and exclude its end. The arrival then belongs to the next '
    'window. Another convention can work too, as long as every event has one '
    'place and adjacent windows use the same convention. '
    'To test a counter, choose examples that expose the rule. An arrival just '
    'before the start checks exclusion. An arrival at the start checks the '
    'included boundary. An arrival inside the window checks the ordinary '
    'case. An arrival at the end checks the excluded boundary. Passing only '
    'ordinary examples leaves the most important ambiguity unresolved. '
    'When comparing reports, record the question, interval, boundary rule and '
    'initial count beside the result. These details make a number interpretable. '
    'A useful note might explain which question each counter answers, then give '
    'one example where their totals differ. Before taking a new measurement, '
    'predict what each counter should report and identify the event that would '
    'change your prediction. This turns a displayed total into a claim you can '
    'inspect, question and reproduce.'
)


def fixture():
    case = ReadingDesk('test_live_http_route_and_note')
    case.setUp()
    source = case.run_op('register_source', filename='trail-counters.md',
                        content='# Two trail counters\n' + PASSAGE + '\n',
                        grants={'read': 'granted', 'transform': 'granted'})
    case.source_id, case.source_fp = source['source_object_id'], source['fingerprint']
    case.run_op('add_source', source_object_id=case.source_id, title='Two trail counters')
    case.bind('line 2')
    row = case.run_op('create_reading', expected_fingerprint=case.read()['fingerprint'],
                      binding_index=len(case.read()['doc']['bindings']) - 1,
                      values=case.values(), title='Two trail counters', activation='Now')['occurrence']
    return case, row


def snapshot(root):
    return {str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in Path(root).rglob('*') if path.is_file()}


def inspect(case, url, route, output):
    from playwright.sync_api import sync_playwright
    output.mkdir(parents=True, exist_ok=True)
    before = snapshot(case.root)
    observations = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel='chrome', headless=True)
        try:
            for width in (1280, 390, 320):
                for scheme in ('light', 'dark'):
                    context = browser.new_context(viewport={'width': width, 'height': 900},
                                                  color_scheme=scheme, reduced_motion='reduce')
                    page = context.new_page()
                    errors = []
                    page.on('pageerror', lambda error: errors.append(str(error)))
                    page.on('dialog', lambda dialog: dialog.accept())
                    page.goto(url + route)
                    page.wait_for_load_state('networkidle')
                    for mode in ('study', 'read', 'notebook'):
                        page.locator('[data-reading-mode-button="%s"]' % mode).click()
                        page.evaluate('window.scrollTo(0,0)')
                        geometry = page.evaluate('''() => {
                            const source=document.querySelector('.reading-column').getBoundingClientRect();
                            const notes=document.querySelector('.reading-notes').getBoundingClientRect();
                            return {width:innerWidth,scroll:document.documentElement.scrollWidth,
                                    sourceWidth:source.width,noteWidth:notes.width};
                        }''')
                        assert geometry['scroll'] <= width + 1, (mode, scheme, geometry)
                        if width == 1280 and mode == 'notebook':
                            assert geometry['noteWidth'] > geometry['sourceWidth'], geometry
                        page.screenshot(path=str(output / f'{mode}-{width}-{scheme}.png'), full_page=True)
                        observations.append(dict(mode=mode, scheme=scheme, **geometry))
                    page.locator('#note').fill('An unfinished thought about the time boundary.')
                    page.locator('[data-reading-mode-button="read"]').click()
                    page.get_by_text('Reading tools', exact=True).click()
                    page.locator('#reading-size').select_option('22')
                    page.locator('#reading-measure').select_option('58')
                    page.reload()
                    page.wait_for_load_state('networkidle')
                    assert page.locator('.reading-layout').get_attribute('data-reading-mode') == 'read'
                    assert page.locator('#note').input_value() == 'An unfinished thought about the time boundary.'
                    assert page.locator('#reading-size').input_value() == '22'
                    assert page.locator('#reading-measure').input_value() == '58'
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
                    page.locator('#reading-note-open').click()
                    assert page.locator('.reading-layout').get_attribute('data-reading-mode') == 'notebook'
                    page.locator('.reading-return').first.click()
                    assert page.locator('.reading-layout').get_attribute('data-reading-mode') == 'read'
                    assert page.evaluate('document.activeElement.id') == 'source-content'
                    page.locator('[data-reading-mode-button="notebook"]').click()
                    page.locator('#source-content').focus()
                    page.keyboard.press('ArrowDown')
                    page.wait_for_function('document.querySelector("#source-content").scrollTop > 0')
                    assert not errors, errors
                    context.close()
            context = browser.new_context(java_script_enabled=False, viewport={'width': 390, 'height': 900})
            page = context.new_page()
            page.goto(url + route)
            assert PARAGRAPH.strip() in page.locator('#source-content').inner_text()
            assert page.locator('.reading-notes').is_visible()
            page.screenshot(path=str(output / 'no-script-390.png'), full_page=True)
            context.close()
        finally:
            browser.close()
    assert snapshot(case.root) == before, 'view controls changed accepted course, note or evidence files'
    (output / 'observations.json').write_text(json.dumps(observations, indent=2) + '\n')
    print('18 light/dark layouts, 6 draft/view reloads, keyboard passage scrolling, script-free fallback and unchanged durable files pass.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--output', type=Path, default=ROOT / '.reasonix/reading-modes-20261001')
    args = parser.parse_args()
    case, row = fixture()
    proc, url, _ = start_daemon(case.root)
    route = href('synthetic', row).lstrip('/')
    try:
        if args.verify:
            inspect(case, url, route, args.output)
        else:
            print(url + route, flush=True)
            input('Disposable original material. Press Enter to stop and remove this preview.\n')
    finally:
        proc.terminate()
        proc.wait(timeout=10)
        case.doCleanups()


if __name__ == '__main__':
    main()
