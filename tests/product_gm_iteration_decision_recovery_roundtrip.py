"""Return stale outline decisions to the exact current review without deciding."""
import argparse
import copy
import json
from pathlib import Path
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
if not (ROOT / 'itembank.py').exists():
    ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / 'itembank.py').exists())
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
import course
import graph
from surfaces import agent_operation as ao
import course_guidance_journey_roundtrip as guide
import product_gm_iteration_outline_return_roundtrip as outline


def request(url, values=None, headers=None):
    data = urllib.parse.urlencode(values, doseq=True).encode() if values is not None else None
    req = urllib.request.Request(url, data=data, headers=headers or {})
    try:
        response = urllib.request.urlopen(req, timeout=10)
    except urllib.error.HTTPError as exc:
        response = exc
    with response:
        return response.status, response.geturl(), response.read().decode()


def changed_proposal(root, base, ids, read, url):
    prefix = url + 'course/synthetic'
    status, destination, _ = request(prefix + '/outline/propose', outline.form(read, ids))
    assert status == 200
    pid = urllib.parse.parse_qs(urllib.parse.urlsplit(destination).query)['outline'][0]
    token = ao.draft_fingerprint(ao.status(str(base), pid)['draft'])
    return prefix, pid, token


def revise(prefix, read, ids, pid, token):
    assert request(prefix + '/outline/propose', outline.revised_form(read, ids, pid, token))[0] == 200


def check_native():
    for route in ('outline', 'build'):
        with outline.outline_case() as (root, base, ids, read, prior):
            with guide.served(root) as url:
                prefix, pid, old = changed_proposal(root, base, ids, read, url)
                revise(prefix, read, ids, pid, old)
                record = ao.status(str(base), pid)
                frozen = outline.files(root)
                for action in ('accept', 'reject'):
                    target = prefix + ('/outline/' + action if route == 'outline' else '/build')
                    for token in (old, ''):
                        fields = {'proposal_id': pid, 'expected_draft_fingerprint': token}
                        if route == 'build': fields['action'] = action
                        status, _, markup = request(target, fields)
                        assert status == 400 and 'agent.draft_stale' in markup
                        href = '/course/synthetic/build?outline=' + pid + '#course-outline-proposal'
                        assert 'href="' + href + '"' in markup, markup[:800]
                        assert 'Review current proposal' in markup and 'No decision was applied' in markup
                        assert '<form' not in markup
                        assert outline.files(root) == frozen
                        assert ao.status(str(base), pid) == record
                status, _, review = request(url + href.lstrip('/'))
                assert status == 200 and ao.draft_fingerprint(record['draft']) in review
                assert outline.files(root) == frozen
                # Re-read current proposal after a fresh daemon. Recovery itself stays read-only.
            with guide.served(root) as url:
                assert request(url + href.lstrip('/'))[0] == 200
                assert outline.files(root) == frozen
                verdict = {'proposal_id': pid, 'expected_draft_fingerprint': ao.draft_fingerprint(record['draft'])}
                assert request(url + 'course/synthetic/outline/accept', verdict)[0] == 200
                current = course.read_course(str(base))
                assert current['revision'] == read['revision'] + 1
                assert [row['id'] for row in current['doc']['objectives']] == [ids[0], ids[2], ids[1]]
                assert outline.semantics(current['doc']) == outline.semantics(read['doc'])
                assert outline.protected(root, base) == prior
                assert request(url + 'course/synthetic/outline/undo', {'proposal_id': pid})[0] == 200
                assert (base / 'course-graph.md').read_text() == read['text']
                assert outline.protected(root, base) == prior
    print('Native stale Accept/Reject and missing token: 400, exact review, read-only restart, explicit current accept and exact undo pass')


def check_identity_refusals():
    with outline.outline_case() as (root, base, ids, read, prior), guide.served(root) as url:
        prefix, pid, token = changed_proposal(root, base, ids, read, url)
        revise(prefix, read, ids, pid, token)
        record = ao.status(str(base), pid)
        path = base / ao.STORE_DIR / (pid + '.json')
        original = path.read_bytes()
        cases = [({}, None), ({'proposal_id': 'p_missing'}, None), ({'proposal_id': 'p_' + 'f' * 32}, None),
            ({'proposal_id': '../foreign'}, None), ({'proposal_id': [pid, 'p_missing']}, None)]
        malformed = copy.deepcopy(record); malformed['proposal_id'] = 'p_other'
        future = copy.deepcopy(record); future['schema_version'] = 999
        foreign = copy.deepcopy(record)
        doc = graph.parse_course(foreign['draft']); doc['header']['course_object_id'] = 'foreign_course'
        foreign['draft'] = graph.serialize_course(doc)
        wrong_target = copy.deepcopy(record); wrong_target['target'] = 'private.md'
        cases.extend([({'proposal_id': pid}, b'{invalid'), ({'proposal_id': pid}, json.dumps(malformed).encode()),
            ({'proposal_id': pid}, json.dumps(future).encode()), ({'proposal_id': pid}, json.dumps(foreign).encode()),
            ({'proposal_id': pid}, json.dumps(wrong_target).encode())])
        for route in ('outline/accept', 'build'):
            for fields, raw in cases:
                path.write_bytes(original if raw is None else raw)
                frozen = outline.files(root)
                fields = dict(fields, expected_draft_fingerprint=token)
                if route == 'build': fields['action'] = 'accept'
                status, _, markup = request(prefix + '/' + route, fields)
                supplied = fields.get('proposal_id') or ''
                selected = supplied[-1] if isinstance(supplied, list) else supplied
                unavailable = ao.status(str(base), selected).get('state') == 'unavailable'
                expected = 200 if route == 'build' and re.fullmatch(r'p_[0-9a-f]{32}', selected) and unavailable else 400
                assert status == expected and 'Review current proposal' not in markup, (route, fields, status)
                if expected == 200 and raw is not None:
                    assert 'Agent operation unavailable' in markup
                assert outline.files(root) == frozen
            path.write_bytes(original)
            status, _, markup = request(prefix + '/' + route,
                {'action': 'accept', 'proposal_id': pid, 'expected_draft_fingerprint': token},
                {'Origin': 'https://foreign.invalid'})
            assert status == 403 and 'Review current proposal' not in markup
        assert request(url + 'course/missing/build', {'action': 'accept', 'proposal_id': pid})[0] == 400
        assert request(url + 'course/missing/outline/accept', {'proposal_id': pid})[0] == 404
        assert outline.protected(root, base) == prior
    print('Missing, malformed, foreign, future, duplicate and cross-origin identities have no current-review shortcut and retain files')


def check_browser(output):
    from playwright.sync_api import sync_playwright
    rows = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel='chrome', headless=True)
        try:
            for route in ('outline', 'build'):
                for width, scripts in ((1280, True), (390, True), (320, False)):
                    with outline.outline_case() as (root, base, ids, read, prior):
                        with guide.served(root) as url:
                            prefix, pid, token = changed_proposal(root, base, ids, read, url)
                            context = browser.new_context(viewport={'width': width, 'height': 900},
                                java_script_enabled=scripts, reduced_motion='reduce', has_touch=width == 320,
                                color_scheme='dark' if width == 390 else 'light')
                            try:
                                page = context.new_page()
                                query = '?outline=' if route == 'outline' else '?proposal='
                                page.goto(prefix + '/build' + query + pid)
                                revise(prefix, read, ids, pid, token)
                                frozen = outline.files(root)
                                button = (page.locator('#course-outline-proposal').get_by_role('button', name='Accept proposal', exact=True)
                                    if route == 'outline' else page.get_by_role('button', name=re.compile('^Accept proposal p_')))
                                button.focus()
                                with page.expect_navigation(wait_until='networkidle') as response: button.press('Enter')
                                assert response.value.status == 400
                                page.screenshot(path=str(output / f'stale-{route}-{width}.png'), full_page=True)
                                assert outline.files(root) == frozen
                                link = page.get_by_role('link', name='Review current proposal', exact=True)
                                assert link.count() == 1
                                link.focus()
                                with page.expect_navigation(wait_until='networkidle'): link.press('Enter')
                                assert page.url.endswith('?outline=' + pid + '#course-outline-proposal')
                                assert outline.files(root) == frozen
                                assert page.locator('html').evaluate('(e) => e.scrollWidth') <= width
                                page.screenshot(path=str(output / f'current-review-{route}-{width}.png'), full_page=True)
                                accept = page.locator('#course-outline-proposal').get_by_role('button', name='Accept proposal', exact=True)
                                accept.focus()
                                with page.expect_navigation(wait_until='networkidle'): accept.press('Enter')
                                assert course.read_course(str(base))['revision'] == read['revision'] + 1
                                assert outline.protected(root, base) == prior
                                accepted = outline.files(root)
                                page.reload(); assert outline.files(root) == accepted
                            finally:
                                context.close()
                        with guide.served(root) as url:
                            context = browser.new_context(viewport={'width': width, 'height': 900}, java_script_enabled=scripts)
                            try:
                                page = context.new_page(); page.goto(url + 'course/synthetic/build?outline=' + pid)
                                assert outline.files(root) == accepted
                                undo = page.locator('#course-outline-proposal').get_by_role('button', name='Undo accepted proposal', exact=True)
                                undo.focus()
                                with page.expect_navigation(wait_until='networkidle'): undo.press('Enter')
                                assert (base / 'course-graph.md').read_text() == read['text']
                                assert outline.protected(root, base) == prior
                            finally:
                                context.close()
                        rows.append({'route': route, 'width': width, 'scripts': scripts, 'status': 400,
                            'current_review_exact': True, 'no_automatic_decision': True, 'explicit_accept_restart_undo': True})
        finally:
            browser.close()
    (output / 'browser-observations.json').write_text(json.dumps(rows, indent=2) + '\n')
    print('Six actual Chrome stale -> current review -> explicit accept -> restart -> exact Undo journeys pass')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--browser', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.browser:
        assert args.output is not None
        args.output.mkdir(parents=True, exist_ok=True)
        check_browser(args.output)
    else:
        check_native(); check_identity_refusals()
