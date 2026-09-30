#!/usr/bin/env python3
"""Real daemon staged commitments and polynomial drafts, synthetic sources only."""
import argparse
import html
import json
from pathlib import Path
import sys
import subprocess
import tempfile
import urllib.parse

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
import evidence
import model
import runtime
from surfaces import daemon, quiz_page
from daemon_roundtrip import start_daemon, json_request
from a5_served_integration_roundtrip import request
from quiz_symbol_return_roundtrip import Page
from ui_overhaul_journey_roundtrip import fixture
from polynomial_production_roundtrip import bank_fixture as polynomial_bank


def staged_bank():
    case = {'version': 1, 'activity_id': 'synthetic:ui-case',
            'stimulus': 'A fictional counter starts at three and adds two once.',
            'children': ['a200000000000001', 'a200000000000002'],
            'order': ['answer', 'reason']}
    source = (ROOT / 'prototypes/audit-question-families/fixtures/bank.md').read_text()
    source = source.split('Q3.')[0]
    source = source.replace('## Static case', 'STAGED-CASES: ' + json.dumps([case]) + '\n\n## Static case')
    return source + '''Q3. Pick the second fictional color.
[ID: a200000000000005]
[TYPE: mc]
[OBJECTIVE: synthetic:ordinary]
A) Orange
B) Purple
C) Yellow
CORRECT: B
WHY BEST: Ordinary private explanation marker.
CONFIDENCE: high
'''


def response_events(root, sid=None):
    return [row for row in evidence.live_events(evidence.log_path(str(Path(root, 'synthetic'))))
            if row.get('event_type') == evidence.RESPONSE_EVENT_TYPE and (sid is None or row.get('session_id') == sid)]


def parse_fields(source):
    import re
    source = source.split('data-answer-form>', 1)[1].split('</form>', 1)[0]
    return {name: html.unescape(value) for name, value in re.findall(
        r'<input type="hidden" name="([^"]+)" value="([^"]*)"', source)}


def submit_form(base, source, option):
    page = Page(source)
    body = parse_fields(source)
    body['option'] = option
    return request(urllib.parse.urljoin(base, page.answer_path), body)


def check_http(root):
    assert not model.lint(model.load(str(Path(root, 'synthetic/staged.md'))))[0]
    existing_output = Path(root, 'staged-static.html')
    existing_output.write_text('Keep the existing synthetic static artifact.')
    built = subprocess.run([sys.executable, str(ROOT / 'itembank.py'), 'build',
        str(Path(root, 'synthetic/staged.md')), str(existing_output)], capture_output=True, text=True)
    assert built.returncode != 0 and 'served runtime' in built.stderr, built
    assert existing_output.read_text() == 'Keep the existing synthetic static artifact.'
    proc, base, _ = start_daemon(root)
    try:
        for mode in ('practice', 'exam'):
            status, _, initial = request(base + 'quiz/staged?mode=' + mode + '&course=synthetic')
            assert status == 200, initial[:500]
            parsed = Page(initial)
            sid = parsed.card['data-session-id']
            resume = 'quiz/staged?' + urllib.parse.urlencode({'mode': mode, 'session': sid, 'course': 'synthetic'})
            assert 'data-activity-stage="answer"' in initial
            assert 'Adding two to three gives five.' not in initial
            status, _, reason = submit_form(base, initial, 'B')
            assert status == 200, reason[:500]
            assert 'data-activity-stage="reason"' in reason
            assert 'data-committed-answer' in reason and '>B</b>' in reason
            assert 'Adding two to three gives five.' not in reason
            assert len(response_events(root, sid)) == 1
            _, _, reloaded = request(base + resume)
            assert 'data-activity-stage="reason"' in reloaded
            status, _, feedback = submit_form(base, reloaded, 'B')
            assert status == 200, feedback[:500]
            assert len(response_events(root, sid)) == 2
            if mode == 'practice':
                host = feedback.split('<div id="host">', 1)[1].split('</main>', 1)[0]
                assert host.count('<section data-child-feedback>') == 2, host
                assert 'Answer feedback' in feedback and 'Reason feedback' in feedback
                assert 'Adding two to three gives five.' in feedback
            else:
                assert 'Adding two to three gives five.' not in feedback
                host = feedback.split('<div id="host">', 1)[1].split('</main>', 1)[0]
                assert '<section data-child-feedback>' not in host
            _, _, ordinary = request(base + resume)
            assert 'Pick the second fictional color.' in ordinary
            assert 'Ordinary private explanation marker.' not in ordinary
        status, view = json_request(base + 'api/start', {'bank': 'staged_api', 'mode': 'diagnostic', 'count': 2})
        assert status == 200, view
        for answer in ('B', 'B'):
            activity = view['activity']
            binding = {name: activity[name] for name in ('activity_id', 'child_id', 'submission_token')}
            status, submitted = json_request(base + 'api/submit', {'session_id': view['session_id'],
                'action': dict(kind='submit', answer=answer, **binding)})
            assert status == 200, submitted
            assert 'score' not in submitted and 'explain' not in submitted and 'activity_feedback' not in submitted
            view = submitted['next']
        assert view['status'] == 'complete'
        _, _, polynomial = request(base + 'quiz/polynomial?mode=practice&course=synthetic')
        sid = Page(polynomial).card['data-session-id']
        saved = daemon.session_index(root)[sid]
        before = Path(saved).read_bytes()
        assert 'Expand products. Example: 3*x^2 + 4*x + 1.' in polynomial
        for forbidden in ('"target"', '"diagnostics"', '"checker_tests"', 'distribution-omission', 'sign-error'):
            assert forbidden not in polynomial
        fields = parse_fields(polynomial)
        fields['fill_expression'] = '  sin(x)  '
        status, _, refused = request(urllib.parse.urljoin(base, Page(polynomial).answer_path), fields)
        assert status == 400, (status, refused[refused.index('<div id="host">'):refused.index('<div id="host">') + 1400])
        assert 'value="  sin(x)  "' in refused
        prior, after = json.loads(before), runtime.read_session(saved)
        assert all(prior[key] == after[key] for key in ('cursor', 'responses', 'status')), {
            key: (prior.get(key), after.get(key)) for key in prior if prior.get(key) != after.get(key)}
        assert not response_events(root, sid)
        fields = parse_fields(refused)
        fields['fill_expression'] = '2+2*x'
        status, _, accepted = request(urllib.parse.urljoin(base, Page(refused).answer_path), fields)
        assert status == 200 and len(response_events(root, sid)) == 1
        status, view = json_request(base + 'api/start', {'bank': 'polynomial_api', 'mode': 'exam', 'count': 1})
        assert status == 200, view
        status, refused = json_request(base + 'api/submit', {'session_id': view['session_id'], 'answer': {'expression': 'x**2'}})
        assert status == 200 and 'entry_error' in refused, refused
        assert not response_events(root, view['session_id'])
        status, accepted = json_request(base + 'api/submit', {'session_id': view['session_id'], 'answer': {'expression': '2*x+1'}})
        assert status == 200 and 'score' not in accepted and 'explain' not in accepted
        print('Served staged form/API: practice, exam, diagnostic nested action, reload, commitments and ordinary successor pass')
    finally:
        proc.terminate()
        proc.wait(timeout=10)


def check_browser(root, shots):
    from playwright.sync_api import sync_playwright
    for width in (1280, 390, 320):
        Path(root, 'synthetic', f'staged_browser_{width}.md').write_text(staged_bank())
        Path(root, 'synthetic', f'polynomial_browser_{width}.md').write_text(polynomial_bank())
    proc, base, _ = start_daemon(root)
    shots.mkdir(parents=True, exist_ok=True)
    try:
        with sync_playwright() as pw:
            chrome = pw.chromium.launch(channel='chrome', headless=True)
            for width in (1280, 390, 320):
                ctx = chrome.new_context(viewport={'width': width, 'height': 900}, reduced_motion='reduce')
                page = ctx.new_page()
                page.goto(base + f'quiz/staged_browser_{width}?mode=practice&course=synthetic')
                page.wait_for_load_state('networkidle')
                sid = page.locator('[data-server-baseline]').get_attribute('data-session-id')
                card = page.locator('[data-server-baseline]')
                assert card.locator('[data-activity-stage="answer"]').count() == 1
                page.get_by_role('radio').nth(1).focus()
                page.keyboard.press('Space')
                page.get_by_role('button', name='Submit answer', exact=True).click()
                page.wait_for_load_state('networkidle')
                assert page.locator('[data-activity-stage="reason"]').count() == 1
                assert 'Your committed answer: B.' in page.locator('[data-committed-answer]').inner_text()
                assert 'Adding two to three gives five.' not in page.content()
                page.reload()
                page.wait_for_load_state('networkidle')
                assert page.locator('[data-activity-stage="reason"]').count() == 1
                page.get_by_role('radio').nth(1).focus()
                page.keyboard.press('Space')
                page.get_by_role('button', name='Submit answer', exact=True).click()
                page.wait_for_load_state('networkidle')
                assert page.locator('[data-child-feedback]').count() == 2
                assert len(response_events(root, sid)) == 2
                size = page.evaluate('({width:innerWidth,scroll:document.documentElement.scrollWidth})')
                assert size['scroll'] == width, size
                page.screenshot(path=str(shots / f'staged-feedback-{width}.png'), full_page=True)
                page.locator('[data-feedback-continue]').click()
                page.wait_for_load_state('networkidle')
                assert 'Pick the second fictional color.' in page.locator('h1.stem').inner_text()
                assert len(response_events(root, sid)) == 2
                page.goto(base + f'quiz/polynomial_browser_{width}?mode=practice&course=synthetic')
                page.wait_for_load_state('networkidle')
                sid = page.locator('[data-server-baseline]').get_attribute('data-session-id')
                entry = page.get_by_role('textbox', name='Expanded expression')
                entry.fill('  sin(x)  ')
                page.get_by_role('button', name='Submit answer', exact=True).click()
                page.wait_for_load_state('networkidle')
                assert entry.input_value() == '  sin(x)  '
                assert not response_events(root, sid)
                assert entry.get_attribute('aria-invalid') == 'true'
                assert 'fill-entry-error' in entry.get_attribute('aria-describedby')
                input_box = entry.bounding_box()
                help_box = page.locator('#fill-help-expression').bounding_box()
                assert input_box['width'] >= min(200, width - 100), input_box
                assert help_box['y'] >= input_box['y'] + input_box['height'], (input_box, help_box)
                page.reload()
                page.wait_for_load_state('networkidle')
                assert entry.input_value() == '  sin(x)  '
                page.screenshot(path=str(shots / f'polynomial-refusal-{width}.png'), full_page=True)
                entry.fill('2+2*x')
                page.get_by_role('button', name='Submit answer', exact=True).click()
                page.wait_for_load_state('networkidle')
                assert len(response_events(root, sid)) == 1
                ctx.close()
            chrome.close()
        print('Chrome staged native keyboard/reload/feedback/ordinary continuation passes at 1280, 390, 320')
    finally:
        proc.terminate()
        proc.wait(timeout=10)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--browser-shots', type=Path)
    args = parser.parse_args()
    case, root, _ = fixture()
    try:
        Path(root, 'synthetic/staged.md').write_text(staged_bank())
        Path(root, 'synthetic/staged_api.md').write_text(staged_bank().split('Q3.')[0])
        Path(root, 'synthetic/polynomial.md').write_text(polynomial_bank())
        Path(root, 'synthetic/polynomial_api.md').write_text(polynomial_bank())
        check_http(root)
        if args.browser_shots:
            check_browser(root, args.browser_shots)
    finally:
        case.tearDown()


if __name__ == '__main__':
    main()
