#!/usr/bin/env python3
"""Actual native help routes, synthetic CLI transport and Chrome reader return."""
import argparse
from contextlib import contextmanager
import json
from pathlib import Path
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
import course
import notes
import reading_desk
from surfaces import daemon
from context_help_roundtrip import ReadingSelection, synthetic_contract, tree
from a5_research_context_roundtrip import fixture as source_fixture
from course_guidance_journey_roundtrip import served as fresh_process


@contextmanager
def native(root):
    handler = type('SyntheticHelpHandler', (daemon.DaemonHandler,), {
        'root': str(root), 'banks': {}, 'sessions': {}, 'log_message': lambda self, *args: None})
    server = daemon.Daemon(('127.0.0.1', 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield 'http://127.0.0.1:%d/' % server.server_address[1]
    finally:
        server.shutdown(); server.server_close(); thread.join(3)


def post(url, action, body):
    request = urllib.request.Request(url + 'api/course/context-help-' + action,
        data=json.dumps(dict(body, course_id='synthetic')).encode(),
        headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as error:
        with error:
            return error.code, error.read().decode()


@contextmanager
def reading_fixture():
    case = ReadingSelection('test_second_duplicate_exact_offsets_unicode_and_exact_return')
    case.setUp()
    try:
        root = Path(case.root)
        private = reading_desk.note_root(case.base)
        body = {'expected_fingerprint': case.read()['fingerprint'],
                'occurrence_id': case.row['occurrence_id'], 'revision_id': case.row['revision_id'],
                'wording': 'EXCLUDED_PRIVATE_SENTINEL', 'note_id': 'a' * 32, 'notes_fingerprint': None}
        reading_desk.save_note(case.base, body)
        script = root / 'provider.py'
        script.write_text('import json,sys,time\nr=json.load(sys.stdin)\np=r["payload"]["context_request"]\n'
            'time.sleep(2 if "wait" in p["question"] else 0)\n'
            'json.dump({"schema_version":1,"answer":"Synthetic advisory explanation.",'
            '"citations":[{"citation_id":"S1","quote":p["source_spans"][0]["text"]}],'
            '"uncertainty":"Synthetic only."},sys.stdout)\n', encoding='utf-8')
        cfg = {'model_backend': {'active': 'synthetic', 'profiles': [{'name': 'synthetic',
            'transport': 'hosted_cli', 'command': [sys.executable, str(script)], 'model': 'fictional',
            'timeout_seconds': 5, 'max_output_bytes': 65536, 'context_window': 8192}]}}
        (root / 'itembank.json').write_text(json.dumps(cfg))
        raw = course.validate_reading_source(case.base, case.row['source_ref'])['verbatim']
        start = raw.rindex('Same phrase.')
        body = {'expected_fingerprint': case.read()['fingerprint'],
                'reading': {key: case.row[key] for key in ('occurrence_id', 'revision_id')},
                'selection': {'start': start, 'end': start + 12, 'quote': 'Same phrase.'},
                'question': 'Explain the second phrase', 'note_ids': []}
        path = 'course/synthetic/reading/%s/%s' % (case.row['occurrence_id'], case.row['revision_id'])
        yield case, root, body, path
    finally:
        case.doCleanups()


def check_routes():
    with reading_fixture() as (case, root, body, path):
        before = tree(case.base)
        with synthetic_contract(lambda **kw: None), native(root) as url:
            code, preview = post(url, 'preview', body)
            assert code == 200, preview
            assert preview['source_spans'][0]['text'] == 'Same phrase.'
            assert preview['excluded_notes'] == 1
            assert 'EXCLUDED_PRIVATE_SENTINEL' not in json.dumps(preview)
            code, started = post(url, 'start', {'preview_id': preview['preview_id'], 'confirm': True})
            assert code == 200, started
            result = started
            for _ in range(80):
                code, result = post(url, 'status', {'request_id': started['request_id']})
                if result['state'] != 'running':
                    break
                time.sleep(.02)
            assert result['state'] == 'answered', result
            assert result['return_href'].endswith('#source-content')
            assert post(url, 'preview', dict(body, session_id='formal'))[0] == 400
            assert post(url, 'preview', dict(body, return_href='https://example.com'))[0] == 400
            assert post(url, 'start', {'preview_id': preview['preview_id'], 'confirm': False})[0] == 400
            code, late_preview = post(url, 'preview', dict(body, question='wait for cancellation'))
            code, late = post(url, 'start', {'preview_id': late_preview['preview_id'], 'confirm': True})
            assert code == 200
            code, canceled = post(url, 'cancel', {'request_id': late['request_id']})
            assert canceled['state'] == 'canceled'
            assert post(url, 'status', {'request_id': late['request_id']})[1]['state'] == 'canceled'
            with urllib.request.urlopen(url + path, timeout=5) as response:
                assert 'Ask about selection' in response.read().decode()
        # A real fresh daemon cannot own or replay the previous process's handle.
        with fresh_process(root) as url:
            result = post(url, 'status', {'request_id': started['request_id']})[1]
            assert result['code'] == 'help.request_unowned', result
        assert tree(case.base) == before, 'Help routes changed durable course, notes or evidence'


def check_browser(output):
    from playwright.sync_api import sync_playwright
    output.mkdir(parents=True, exist_ok=True)
    observations = []
    with reading_fixture() as (case, root, body, path), synthetic_contract(lambda **kw: None), native(root) as url, sync_playwright() as pw:
        before = tree(case.base)
        browser = pw.chromium.launch(channel='chrome', headless=True)
        try:
            for width in (1280, 390, 320):
                context = browser.new_context(viewport={'width': width, 'height': 900}, reduced_motion='reduce')
                page = context.new_page()
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.goto(url + path)
                page.wait_for_function('document.querySelector("#help-preview").disabled === false')
                page.locator('#reading-tools > summary').click()
                page.evaluate('''() => {const source=document.querySelector('#source-content'),text=source.textContent,start=text.lastIndexOf('Same phrase.'),range=document.createRange();range.setStart(source.firstChild,start);range.setEnd(source.firstChild,start+12);const selected=window.getSelection();selected.removeAllRanges();selected.addRange(range);}''')
                page.locator('#reading-help-selection').click()
                assert 'character range 15:27' in page.locator('#help-selection-state').inner_text()
                page.locator('#help-question').fill('Explain the second phrase')
                page.locator('#help-preview').focus()
                page.keyboard.press('Enter')
                page.locator('#help-preview-content').wait_for(state='visible')
                preview = page.locator('#help-preview-content').inner_text()
                assert 'Same phrase.' in preview and 'EXCLUDED_PRIVATE_SENTINEL' not in preview
                assert '1 private notes excluded' in preview and 'Configured CLI' in preview
                assert page.locator('#help-send').is_disabled()
                page.locator('#help-consent').check()
                page.locator('#help-send').focus(); page.keyboard.press('Enter')
                page.locator('#help-answer').wait_for(state='visible')
                assert 'Synthetic advisory explanation' in page.locator('#help-answer').inner_text()
                page.reload()
                page.locator('#help-answer').wait_for(state='visible')
                page.locator('#help-return').focus(); page.keyboard.press('Enter')
                assert page.evaluate('document.activeElement.id') == 'source-content'
                assert page.evaluate('window.getSelection().toString()') == 'Same phrase.'
                assert page.evaluate('window.getSelection().getRangeAt(0).startOffset') == 16
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
                page.screenshot(path=str(output / f'help-{width}.png'), full_page=True)
                assert not errors, errors
                # A separate pending synthetic request supports real transport cancellation.
                page.locator('#help-question').fill('wait for cancellation')
                page.locator('#help-preview').click()
                page.locator('#help-consent-label').wait_for(state='visible')
                page.locator('#help-consent').check(); page.locator('#help-send').click()
                page.locator('#help-cancel').wait_for(state='visible')
                page.locator('#help-cancel').click()
                page.wait_for_function('document.querySelector("#help-state").textContent.includes("canceled")')
                assert page.locator('#help-answer').is_hidden()
                observations.append({'width': width, 'duplicate_offset': 16, 'excluded_note': True,
                                     'cited_answer': True, 'reload': True, 'keyboard_return': True, 'cancel': True})
                context.close()
            assert tree(case.base) == before, 'Browser help wrote durable learner state'
        finally:
            browser.close()
    # Script-free native picker chooses occurrence L4 rather than matching text.
    with tempfile.TemporaryDirectory(prefix='help_picker_') as directory:
        base, refs = source_fixture(Path(directory))
        with native(Path(directory)) as url, sync_playwright() as pw:
            browser = pw.chromium.launch(channel='chrome', headless=True)
            context = browser.new_context(java_script_enabled=False, viewport={'width': 320, 'height': 900})
            try:
                page = context.new_page(); page.goto(url + 'course/synthetic/help')
                page.locator('select[name=locator]').select_option('L4')
                page.locator('textarea[name=question]').fill('Explain the second occurrence')
                page.get_by_role('button', name='Preview exact inclusion and destination').click()
                assert 'Same sentence.' in page.locator('pre').first.inner_text()
                assert 'locator L4' in page.content()
                assert 'Provider disabled' in page.content()
                assert page.get_by_role('button', name='Ask configured provider').count() == 0
                page.get_by_role('link', name='Return to the exact source task').click()
                assert page.url.endswith('#research-exact-passage')
                assert page.locator('select[name=locator]').input_value() == 'L4'
                assert 'locator L4' in page.content()
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
                page.screenshot(path=str(output / 'script-free-picker-320.png'), full_page=True)
            finally:
                context.close(); browser.close()
    (output / 'observations.json').write_text(json.dumps(observations, indent=2) + '\n')


if __name__ == '__main__':
    import tempfile
    parser = argparse.ArgumentParser()
    parser.add_argument('--browser', type=Path)
    args = parser.parse_args()
    check_routes()
    if args.browser:
        check_browser(args.browser)
    print('Native context help: admitted selection, exact preview, synthetic cited CLI success, cancellation, restart and no durable writes pass')
