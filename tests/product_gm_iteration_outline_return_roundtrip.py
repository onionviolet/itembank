"""Exercise reviewed structural order without changing learning identity or history."""
import argparse
from contextlib import contextmanager
import copy
import json
from pathlib import Path
import re
import sys
import tempfile
import urllib.parse

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
import course
import graph
import journal
from surfaces import agent_operation as ao, session
import course_guidance_journey_roundtrip as guide
from a5_served_integration_roundtrip import request


def files(root):
    return {str(path.relative_to(root)): path.read_bytes() for path in root.rglob('*') if path.is_file()}


def protected(root, base):
    result = {}
    for path in root.rglob('*'):
        if not path.is_file(): continue
        name = path.relative_to(root).as_posix()
        if '_journal' in path.parts or ao.STORE_DIR in name or path == base / 'course-graph.md': continue
        if path.name in ('evidence_index.sqlite3', 'evidence_index.sqlite3.lock') and path.parent.name == '_evidence': continue
        result[name] = path.read_bytes()
    rows = journal.read_registry(str(base))
    result['registered-non-course'] = {oid: row for oid, row in rows.items() if row['kind'] != 'course'}
    return result


def semantics(doc):
    result = copy.deepcopy(doc)
    objectives = sorted(result['objectives'], key=lambda row: row['id'])
    for row in objectives: row.pop('order', None)
    result['objectives'] = objectives
    return result


@contextmanager
def outline_case():
    with guide.fixture(reported_reading=True) as (root, base, banks, meta):
        read = course.read_course(str(base))
        first = read['doc']['objectives'][0]['id']
        second = graph.add_objective(read['doc'], 'Apply the fictional rule to a second example')['id']
        third = graph.add_objective(read['doc'], 'Review an independent fictional observation')['id']
        graph.add_edge(read['doc'], first, 'prerequisite-of', second, authority='authored',
            confidence='high', rationale='Synthetic author fixture prerequisite.')
        course.write_course(str(base), read['doc'], read['fingerprint'], 'human', 'synthetic-author')
        (root / 'itembank.json').write_text(json.dumps({'auditor_autonomy': 'draft_and_approve'}))
        path, _ = guide.start_saved(root, base, 'symbols', 'practice', 2)
        for _ in range(2): assert session.do_submit(str(path), 'B', None)['score'] is True
        read = course.read_course(str(base))
        assert [row['id'] for row in read['doc']['objectives']] == [first, second, third]
        yield root, base, [first, second, third], read, protected(root, base)


def form(read, ids):
    return {'expected_course_fingerprint': read['fingerprint'],
        'order-' + ids[0]: '2', 'order-' + ids[1]: '3', 'order-' + ids[2]: '1'}


def reordered(base, read, ids, prior):
    current = course.read_course(str(base))
    assert current['revision'] == read['revision'] + 1
    assert [row['id'] for row in current['doc']['objectives']] == [ids[2], ids[0], ids[1]]
    assert semantics(current['doc']) == semantics(read['doc'])
    assert protected(base.parent, base) == prior
    return current


def check_native(output):
    with outline_case() as (root, base, ids, read, prior):
        original = (base / 'course-graph.md').read_bytes()
        with guide.served(root) as url:
            prefix = url + 'course/synthetic'
            status, destination, markup = request(prefix + '/outline/propose', form(read, ids))
            assert status == 200 and 'Exact diff' in markup, (status, markup[:300])
            pid = urllib.parse.parse_qs(urllib.parse.urlsplit(destination).query)['outline'][0]
            proposal = ao.status(str(base), pid)
            assert proposal['disposition'] == 'proposed'
            assert (base / 'course-graph.md').read_bytes() == original and protected(root, base) == prior
            before = files(root)
            guide.get(url, '/course/synthetic/build?outline=' + pid)
            assert files(root) == before
            stale = dict(proposal_id=pid, expected_draft_fingerprint='sha256:' + '0' * 64)
            assert request(prefix + '/outline/accept', stale)[0] == 400
            assert (base / 'course-graph.md').read_bytes() == original and protected(root, base) == prior
            verdict = dict(proposal_id=pid, expected_draft_fingerprint=ao.draft_fingerprint(proposal['draft']))
            assert request(prefix + '/outline/accept', verdict)[0] == 200
            reordered(base, read, ids, prior)
            assert ao.status(str(base), pid)['disposition'] == 'accepted'
            accepted = files(root)
            guide.get(url, '/course/synthetic/build?outline=' + pid)
            assert files(root) == accepted
        with guide.served(root) as url:
            markup = guide.get(url, '/course/synthetic/build?outline=' + pid)
            assert 'Undo accepted proposal' in markup and files(root) == accepted
            assert request(url + 'course/synthetic/outline/undo', {'proposal_id': pid})[0] == 200
            assert (base / 'course-graph.md').read_bytes() == original
            assert protected(root, base) == prior
            undone = files(root)
            guide.get(url, '/course/synthetic/build?outline=' + pid)
            assert files(root) == undone and ao.status(str(base), pid)['disposition'] == 'undone'
        (output / 'native-observations.json').write_text(json.dumps({'objectives': ids,
            'reordered': [ids[2], ids[0], ids[1]], 'one_accepted_revision': True,
            'bindings_prerequisites_reading_and_evidence_unchanged': True,
            'stale_draft_refused': True, 'restart_and_exact_undo': True}, indent=2) + '\n')
    print('Native course outline: preview/stale refusal/one revision/reload/restart/exact undo preserve learning identity and history')


def check_browser(output):
    from playwright.sync_api import sync_playwright
    rows = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel='chrome', headless=True)
        try:
            for width, scripts in ((1280, True), (390, True), (320, False)):
                with outline_case() as (root, base, ids, read, prior):
                    original = (base / 'course-graph.md').read_bytes()
                    with guide.served(root) as url:
                        context = browser.new_context(viewport={'width': width, 'height': 900},
                            java_script_enabled=scripts, reduced_motion='reduce', has_touch=width == 320,
                            color_scheme='dark' if width == 390 else 'light')
                        try:
                            page = context.new_page()
                            page.goto(url + 'course/synthetic/build')
                            pane = page.locator('#course-outline-proposal')
                            for oid, position in zip(ids, ('2', '3', '1')):
                                pane.locator('input[name="order-' + oid + '"]').fill(position)
                            preview = pane.get_by_role('button', name='Preview proposal', exact=True)
                            preview.focus()
                            with page.expect_navigation(wait_until='networkidle'): preview.press('Enter')
                            pid = urllib.parse.parse_qs(urllib.parse.urlsplit(page.url).query)['outline'][0]
                            assert ao.status(str(base), pid)['disposition'] == 'proposed'
                            assert (base / 'course-graph.md').read_bytes() == original and protected(root, base) == prior
                            dimensions = page.locator('html').evaluate('(e) => ({width:innerWidth, scroll:e.scrollWidth})')
                            page.screenshot(path=str(output / f'preview-{width}.png'), full_page=True)
                            (output / f'dimensions-{width}.json').write_text(json.dumps(dimensions) + '\n')
                            assert dimensions['scroll'] <= width, dimensions
                            before = files(root)
                            page.reload()
                            assert files(root) == before
                            accept = pane.get_by_role('button', name='Accept proposal', exact=True)
                            accept.focus()
                            with page.expect_navigation(wait_until='networkidle'): accept.press('Enter')
                            reordered(base, read, ids, prior)
                            accepted = files(root)
                            page.reload()
                            assert files(root) == accepted
                            page.screenshot(path=str(output / f'accepted-{width}.png'), full_page=True)
                        finally:
                            context.close()
                    with guide.served(root) as url:
                        context = browser.new_context(viewport={'width': width, 'height': 900}, java_script_enabled=scripts)
                        try:
                            page = context.new_page()
                            page.goto(url + 'course/synthetic/build?outline=' + pid)
                            assert files(root) == accepted
                            undo = page.get_by_role('button', name='Undo accepted proposal', exact=True)
                            undo.focus()
                            with page.expect_navigation(wait_until='networkidle'): undo.press('Enter')
                            assert (base / 'course-graph.md').read_bytes() == original and protected(root, base) == prior
                            assert page.locator('html').evaluate('(e) => e.scrollWidth') <= width
                            undone = files(root)
                            page.reload()
                            assert files(root) == undone
                            page.screenshot(path=str(output / f'undone-{width}.png'), full_page=True)
                        finally:
                            context.close()
                    rows.append({'width': width, 'scripts': scripts, 'same_objective_ids_and_semantics': True,
                        'preview_accept_reload_restart_undo': True, 'protected_learner_files_unchanged': True})
        finally:
            browser.close()
    (output / 'browser-observations.json').write_text(json.dumps(rows, indent=2) + '\n')
    print('Browser course outline: three native reviewed reorder/reload/restart/undo journeys pass')


def revised_form(read, ids, pid, token):
    return {'expected_course_fingerprint': read['fingerprint'], 'proposal_id': pid,
        'expected_draft_fingerprint': token,
        'order-' + ids[0]: '1', 'order-' + ids[1]: '3', 'order-' + ids[2]: '2'}


def check_decision_gate():
    with outline_case() as (root, base, ids, read, prior), guide.served(root) as url:
        prefix = url + 'course/synthetic'
        original = (base / 'course-graph.md').read_bytes()
        _, destination, markup = request(prefix + '/outline/propose', form(read, ids))
        pid = urllib.parse.parse_qs(urllib.parse.urlsplit(destination).query)['outline'][0]
        old = ao.status(str(base), pid)
        token = ao.draft_fingerprint(old['draft'])
        assert ('name="expected_draft_fingerprint" value="' + token + '"') in markup
        assert request(prefix + '/outline/propose', revised_form(read, ids, pid, token))[0] == 200
        pending = ao.status(str(base), pid)
        current_token = ao.draft_fingerprint(pending['draft'])
        assert current_token != token
        for action in ('accept', 'reject'):
            for fields in ({'proposal_id': pid}, {'proposal_id': pid, 'expected_draft_fingerprint': token}):
                status, _, error = request(prefix + '/build', dict(fields, action=action))
                assert status == 400 and 'agent.draft_stale' in error, (status, error[:200])
                assert (base / 'course-graph.md').read_bytes() == original
                assert ao.status(str(base), pid) == pending and protected(root, base) == prior
        verdict = {'action': 'accept', 'proposal_id': pid, 'expected_draft_fingerprint': current_token}
        assert request(prefix + '/build', verdict)[0] == 200
        accepted = course.read_course(str(base))
        assert accepted['revision'] == read['revision'] + 1
        assert [row['id'] for row in accepted['doc']['objectives']] == [ids[0], ids[2], ids[1]]
        assert semantics(accepted['doc']) == semantics(read['doc']) and protected(root, base) == prior
        # A replay cannot accept a second revision.
        assert request(prefix + '/build', verdict)[0] == 200
        assert course.read_course(str(base))['revision'] == accepted['revision']
        assert request(prefix + '/build', {'action': 'undo', 'proposal_id': pid})[0] == 200
        assert (base / 'course-graph.md').read_bytes() == original and protected(root, base) == prior
        _, destination, _ = request(prefix + '/outline/propose', form(course.read_course(str(base)), ids))
        pid = urllib.parse.parse_qs(urllib.parse.urlsplit(destination).query)['outline'][0]
        pending = ao.status(str(base), pid)
        current = course.read_course(str(base))
        current['doc']['header']['title'] = 'Separate synthetic accepted title'
        course.write_course(str(base), current['doc'], current['fingerprint'], 'human', 'synthetic-other-author')
        accepted_bytes = (base / 'course-graph.md').read_bytes()
        assert request(prefix + '/outline/accept', {'proposal_id': pid,
            'expected_draft_fingerprint': ao.draft_fingerprint(pending['draft'])})[0] == 200
        result = ao.status(str(base), pid)
        assert result['disposition'] == 'conflicted' and result['code'] == 'journal.stale_preflight'
        assert (base / 'course-graph.md').read_bytes() == accepted_bytes and protected(root, base) == prior
    print('Outline gate: generic stale/missing Accept/Reject refuse, current token accepts once, exact Undo and stale course base pass')


def check_generic_browser(output):
    from playwright.sync_api import sync_playwright
    rows = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel='chrome', headless=True)
        try:
            for width, scripts in ((1280, True), (390, True), (320, False)):
                with outline_case() as (root, base, ids, read, prior), guide.served(root) as url:
                    original = (base / 'course-graph.md').read_bytes()
                    prefix = url + 'course/synthetic'
                    _, destination, _ = request(prefix + '/outline/propose', form(read, ids))
                    pid = urllib.parse.parse_qs(urllib.parse.urlsplit(destination).query)['outline'][0]
                    old = ao.status(str(base), pid)
                    token = ao.draft_fingerprint(old['draft'])
                    context = browser.new_context(viewport={'width': width, 'height': 900},
                        java_script_enabled=scripts, reduced_motion='reduce', has_touch=width == 320)
                    try:
                        page = context.new_page()
                        page.goto(url + 'course/synthetic/build?outline=' + pid)
                        top_accept = page.get_by_role('button', name=re.compile('^Accept proposal p_'))
                        assert top_accept.count() == 1
                        assert top_accept.locator('xpath=..').locator('input[name="expected_draft_fingerprint"]').get_attribute('value') == token
                        assert request(prefix + '/outline/propose', revised_form(read, ids, pid, token))[0] == 200
                        top_accept.focus()
                        with page.expect_navigation(wait_until='networkidle') as navigation:
                            top_accept.press('Enter')
                        assert navigation.value.status == 400
                        assert 'agent.draft_stale' in page.locator('body').inner_text()
                        assert (base / 'course-graph.md').read_bytes() == original and protected(root, base) == prior
                        page.screenshot(path=str(output / f'stale-generic-{width}.png'), full_page=True)
                        page.goto(url + 'course/synthetic/build?outline=' + pid)
                        top_accept = page.get_by_role('button', name=re.compile('^Accept proposal p_'))
                        top_accept.focus()
                        with page.expect_navigation(wait_until='networkidle'): top_accept.press('Enter')
                        accepted = course.read_course(str(base))
                        assert accepted['revision'] == read['revision'] + 1
                        assert [row['id'] for row in accepted['doc']['objectives']] == [ids[0], ids[2], ids[1]]
                        assert semantics(accepted['doc']) == semantics(read['doc']) and protected(root, base) == prior
                        undo = page.get_by_role('button', name=re.compile('^Undo accepted change for '))
                        undo.focus()
                        with page.expect_navigation(wait_until='networkidle'): undo.press('Enter')
                        assert (base / 'course-graph.md').read_bytes() == original and protected(root, base) == prior
                        page.screenshot(path=str(output / f'generic-undone-{width}.png'), full_page=True)
                        rows.append({'width': width, 'scripts': scripts, 'stale_generic_approval': 400,
                            'fresh_token_accepts_once': True, 'generic_exact_undo': True})
                    finally:
                        context.close()
        finally:
            browser.close()
    (output / 'generic-observations.json').write_text(json.dumps(rows, indent=2) + '\n')
    print('Browser generic outline: three stale-button refusal/fresh review/Accept/Undo journeys pass')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--browser', type=Path)
    args = parser.parse_args()
    if args.browser:
        args.browser.mkdir(parents=True, exist_ok=False)
        check_browser(args.browser)
        check_generic_browser(args.browser)
    else:
        check_decision_gate()
        with tempfile.TemporaryDirectory(prefix='gm-outline-recovery-') as folder:
            check_native(Path(folder))
