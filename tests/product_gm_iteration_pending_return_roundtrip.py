"""Pending prose remains recorded on exact sitting resume, reload and restart."""
import argparse
import copy
from datetime import datetime
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import urllib.parse

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
import course
import evidence
import model
import runtime
from surfaces import course_workbench as cw, session
import course_guidance_journey_roundtrip as guide

RAW_ANSWER = '  Synthetic learner prose: café, λ and <literal>.\n\nNo real learner answer.  '
ANSWER = runtime.normalize_answer(RAW_ANSWER)


class Feedback(HTMLParser):
    def __init__(self, markup):
        super().__init__()
        self.depth = 0
        self.text = []
        self.feed(markup)

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            if self.depth:
                self.depth += 1
            elif 'feedback' in dict(attrs).get('class', '').split():
                self.depth = 1

    def handle_endtag(self, tag):
        if tag == 'div' and self.depth:
            self.depth -= 1

    def handle_data(self, value):
        if self.depth:
            self.text.append(value)


def files(root):
    return {str(path.relative_to(root)): path.read_bytes() for path in root.rglob('*') if path.is_file()}


def same_state(root, expected, sitting):
    observed = files(root)
    assert set(observed) == set(expected), 'resume created or removed a durable file'
    for name, raw in expected.items():
        if observed[name] == raw:
            continue
        assert root / name == sitting, name
        before, after = json.loads(raw), json.loads(observed[name])
        prior_ts, current_ts = before.pop('served_ts'), after.pop('served_ts')
        assert before == after, 'resume changed sitting state beyond the runtime view timestamp'
        assert datetime.fromisoformat(current_ts.replace('Z', '+00:00')) >= datetime.fromisoformat(prior_ts.replace('Z', '+00:00'))


def pending_fixture(root, base, banks):
    path, started = guide.start_saved(root, base, 'pending', 'practice', 1)
    result = session.do_submit(str(path), RAW_ANSWER, None)
    assert result['accepted'] and result['score'] is None and result['action'] == 'defer_feedback'
    saved = runtime.read_session(str(path))
    assert len(saved['responses']) == 1 and saved['responses'][0]['answer'] == ANSWER, saved['responses']
    assert saved['responses'][0]['score'] is None and saved['cursor'] == 0 and saved['status'] == 'active'
    guidance = guide.guidance(root, base, banks)
    assert guidance['kind'] == 'pending' and 'no settled mark' in guidance['reason']
    assert urllib.parse.parse_qs(urllib.parse.urlsplit(guidance['resume_href']).query)['session'] == [started['session_id']]
    history = cw.review_history(str(root), str(base), course.read_course(base)['doc'], banks)
    assert history['counts']['pending'] == 1 and history['counts']['missed'] == 0 and history['counts']['settled'] == 0
    events = [row for row in evidence.live_events(evidence.log_path(str(base)))
              if row.get('event_type') == 'response']
    assert len(events) == 1 and events[0]['answer'] == ANSWER and events[0]['score'] is None
    return path, started['session_id'], guidance


def check_native(output):
    rows = []
    with guide.fixture() as (root, base, banks, _meta):
        path, sid, guidance = pending_fixture(root, base, banks)
        expected = files(root)
        for restart in range(2):
            with guide.served(root) as url:
                home = guide.get(url, '/course/synthetic')
                guide.rendered_guidance(home, guidance)
                assert ANSWER not in home
                markup = guide.get(url, guidance['resume_href'])
                assert 'data-session-id="' + sid + '"' in markup
                assert 'The invented rule selects purple.' not in markup
                feedback = ''.join(Feedback(markup).text)
                assert 'Recorded, and waiting on a mark.' in feedback
                assert 'No model answer is shown now.' in feedback
                (output / f'native-resume-{restart}.html').write_text(markup)
                same_state(root, expected, path)
                assert guide.guidance(root, base, banks)['kind'] == 'pending'
                rows.append({'restart': restart, 'session_id': sid,
                    'recorded_notice': True,
                    'saved_response_bytes_exact': True, 'response_events': 1})
    (output / 'native-observations.json').write_text(json.dumps(rows, indent=2) + '\n')
    print('Native pending resume:', rows, flush=True)


def check_browser(output):
    from playwright.sync_api import sync_playwright
    rows = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel='chrome', headless=True)
        try:
            for width, scripts in ((1280, True), (390, True), (320, False)):
                with guide.fixture() as (root, base, banks, _meta):
                    path, sid, guidance = pending_fixture(root, base, banks)
                    expected = files(root)
                    for restart in range(2):
                        with guide.served(root) as url:
                            context = browser.new_context(viewport={'width': width, 'height': 900},
                                java_script_enabled=scripts, reduced_motion='reduce', has_touch=width == 320,
                                color_scheme='dark' if width == 390 else 'light')
                            try:
                                page = context.new_page()
                                page.goto(url + 'course/synthetic')
                                resume = page.locator('#course-guidance [data-course-resume]')
                                assert resume.get_attribute('href') == guidance['resume_href']
                                resume.focus()
                                with page.expect_navigation(wait_until='networkidle'):
                                    resume.press('Enter')
                                assert page.locator('[data-server-baseline]').get_attribute('data-session-id') == sid
                                for reloaded in (False, True):
                                    if reloaded:
                                        page.reload()
                                    same_state(root, expected, path)
                                    feedback = page.locator('[data-server-baseline] .feedback').inner_text()
                                    assert page.locator('html').evaluate('(e) => e.scrollWidth') <= width
                                    assert 'The invented rule selects purple.' not in page.locator('body').inner_text()
                                    shot = f'resume-{width}-{restart}-{int(reloaded)}.png'
                                    page.screenshot(path=str(output / shot), full_page=True)
                                    row = {'width': width, 'scripts': scripts, 'restart': restart,
                                        'reload': reloaded, 'feedback': feedback, 'session_id': sid,
                                        'response_bytes_and_none_state_exact': True, 'screenshot': shot}
                                    rows.append(row)
                                    (output / 'browser-observations.json').write_text(json.dumps(rows, indent=2) + '\n')
                                    assert 'Recorded, and waiting on a mark.' in feedback, row
                            finally:
                                context.close()
        finally:
            browser.close()
    print('Browser pending recovery: twelve exact sitting resume/reload/fresh-daemon checks pass', flush=True)


def check_projection_boundaries():
    with guide.fixture() as (root, base, banks, _meta):
        path, sid, _guidance = pending_fixture(root, base, banks)
        saved = runtime.read_session(str(path))
        qs = model.load(str(base / 'pending.md'))
        event = next(row for row in evidence.live_events(evidence.log_path(str(base)))
                     if row.get('event_type') == 'response')
        before = files(root)
        expected = runtime.session_view(saved, qs)
        assert session.do_pending_feedback(str(path), expected) == {'action': 'defer_feedback', 'score': None}
        assert files(root) == before
        changed = copy.deepcopy(expected)
        changed['item']['stem'] += ' Changed public question.'
        assert session.do_pending_feedback(str(path), changed) is None
        candidates = ({'session_id': 'other'}, {'bank': 'other.md'}, {'item_ref': 'q2'},
            {'item_id': 'other'}, {'mode': 'exam'}, {'objective': 'other'},
            {'event_type': 'hint'}, {'item_type': 'mc'}, {'score': False}, {'score': True})
        for patch in candidates:
            assert runtime.saved_pending_feedback(dict(event, **patch), saved, qs, set()) is None, patch
        incomplete = dict(event)
        incomplete.pop('score')
        assert runtime.saved_pending_feedback(incomplete, saved, qs, set()) is None
        key = runtime.teaching_key(qs[0])
        assert runtime.saved_pending_feedback(event, saved, qs, {key}) is None
        for patch in ({'status': 'complete'}, {'mode': 'exam'}, {'mode': 'diagnostic'}):
            assert runtime.saved_pending_feedback(event, dict(saved, **patch), qs, set()) is None
        assert files(root) == before
        evidence.append_event(evidence.log_path(str(base)), evidence.retraction_event(
            event['event_id'], 'Synthetic fixture response retraction.'))
        after_retraction = files(root)
        assert session.do_pending_feedback(str(path), expected) is None
        assert files(root) == after_retraction
    print('Pending projection: identity/mode/settled/retracted/stale-view boundaries and read-only bytes pass')


def check_synthetic_reviewer():
    # Artificial reviewer fixture only. This never marks real learner work or
    # substitutes an agent verdict for a person's required acceptance.
    for verdict, status in (('pass', 'settled-correct'), ('fail', 'missed')):
        with guide.fixture() as (root, base, banks, _meta):
            path, sid, guidance = pending_fixture(root, base, banks)
            response = runtime.read_session(str(path))['responses'][0]
            subprocess.run([sys.executable, str(ROOT / 'itembank.py'), 'mark',
                '--session', sid, '--base', str(base), '--item', response['item_id'],
                '--verdict', verdict], check=True, capture_output=True, text=True)
            expected = runtime.session_view(runtime.read_session(str(path)), model.load(str(base / 'pending.md')))
            assert session.do_pending_feedback(str(path), expected) is None
            with guide.served(root) as url:
                markup = guide.get(url, guidance['resume_href'])
                assert 'Session complete.' in markup
                assert 'Recorded, and waiting on a mark.' not in ''.join(Feedback(markup).text)
                state = runtime.read_session(str(path))
                assert state['status'] == 'complete' and state['cursor'] == 1
                assert state['responses'] == [response] and response['answer'] == ANSWER and response['score'] is None
                report = session.do_report(str(path))
                assert report['summary']['pending_manual'] == 0
                history = cw.review_history(str(root), str(base), course.read_course(base)['doc'], banks)
                assert history['counts']['pending'] == 0 and history['rows'][0]['status'] == status
                assert guide.guidance(root, base, banks)['kind'] != 'pending'
                before = files(root)
                guide.get(url, guidance['resume_href'])
                same_state(root, before, path)
    print('Synthetic reviewer: both explicit pass/fail close the runtime cursor without rewriting the pending response')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--browser', type=Path)
    args = parser.parse_args()
    if args.browser:
        args.browser.mkdir(parents=True, exist_ok=False)
        check_browser(args.browser)
    else:
        check_projection_boundaries()
        check_synthetic_reviewer()
        with tempfile.TemporaryDirectory(prefix='gm-pending-recovery-') as folder:
            check_native(Path(folder))
