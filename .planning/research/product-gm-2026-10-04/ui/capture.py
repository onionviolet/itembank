"""Capture the current synthetic native learner surfaces with installed Chrome."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
from course_guidance_journey_roundtrip import fixture, served
from playwright.sync_api import sync_playwright

SPEC = importlib.util.spec_from_file_location(
    'ui_native_preview', ROOT / 'prototypes/ui-character-20261001/native-preview.py')
PREVIEW = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PREVIEW)
OWNED = ('presentation', 'home', 'reading_desk', 'lesson', 'day',
         'day_document', 'quiz_page', 'quiz', 'study')


def hashes():
    return {f'surfaces/{name}.py': hashlib.sha256(
        (ROOT / 'surfaces' / (name + '.py')).read_bytes()).hexdigest()
        for name in OWNED}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--baseline', action='store_true')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    before = hashes()
    if args.baseline:
        backup = args.output / 'base'
        backup.mkdir(exist_ok=True)
        for name in OWNED:
            (backup / (name + '.py.txt')).write_bytes(
                (ROOT / 'surfaces' / (name + '.py')).read_bytes())
    result = {'input_hashes': before, 'screens': []}
    with fixture() as (root, course_base, banks, meta), served(root) as url:
        course_id, sitting = PREVIEW.prepare_course(root, url)
        result['synthetic_course_id'] = course_id
        result['synthetic_session_id'] = sitting['session_id']
        routes = {
            'course': 'course/' + course_id,
            'lesson': 'lesson/coding_boundary_unit?course=' + course_id,
            'guided': 'lesson/coding_boundary_unit?view=guided&course=' + course_id,
            'practice': 'quiz/coding_boundary_unit?mode=practice&session=' +
                        sitting['session_id'] + '&course=' + course_id,
            'reading': meta['reading'].lstrip('/'),
        }
        with sync_playwright() as pw:
            browser = pw.chromium.launch(channel='chrome', headless=True)
            for width, scheme, scripts in (
                    (1280, 'light', True), (390, 'light', True),
                    (320, 'light', True), (1280, 'dark', True),
                    (390, 'dark', True), (390, 'light', False)):
                context = browser.new_context(viewport={'width': width, 'height': 900},
                    color_scheme=scheme, java_script_enabled=scripts,
                    reduced_motion='reduce')
                page = context.new_page()
                for name, route in routes.items():
                    response = page.goto(url + route)
                    assert response.status == 200, (name, response.status)
                    page.locator('h1').first.wait_for()
                    page.wait_for_timeout(120)
                    filename = f'{name}-{width}-{scheme}-' + ('js' if scripts else 'static') + '.png'
                    page.screenshot(path=str(args.output / filename))
                    if scripts:
                        metrics = page.evaluate('''() => {
                            const h = document.querySelector('#lesson-content h2') || document.querySelector('#source-content') || document.querySelector('.stem') || document.querySelector('h1');
                            const links = [...document.querySelectorAll('.bl a')].map(a => ({text:a.innerText,href:a.getAttribute('href')}));
                            return {width:innerWidth,scroll:document.documentElement.scrollWidth,
                                firstContentY:h ? h.getBoundingClientRect().top + scrollY : null,
                                title:document.querySelector('h1').innerText,links};
                        }''')
                        assert metrics['scroll'] <= width + 1, (name, width, metrics)
                    else:
                        metrics = {'static_readable': bool(page.locator('h1').first.inner_text())}
                    result['screens'].append({'surface': name, 'width': width,
                        'scheme': scheme, 'scripts': scripts, 'screenshot': filename, **metrics})
                context.close()
            browser.close()
    assert before == hashes(), 'reserved source changed during capture'
    (args.output / 'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(f'Captured {len(result["screens"])} actual native surface views to {args.output}')


if __name__ == '__main__':
    main()
