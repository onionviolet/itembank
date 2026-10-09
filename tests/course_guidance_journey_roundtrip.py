#!/usr/bin/env python3
"""Native synthetic guidance, truthful evidence and exact saved-sitting return."""
import argparse
from contextlib import contextmanager
import hashlib
import html
import json
from pathlib import Path
import shutil
import sys
import urllib.parse

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
import course
import evidence
import journal
import runtime
from surfaces import course_workbench as cw, daemon, session
from a5_served_integration_roundtrip import request
from daemon_roundtrip import start_daemon
from quiz_symbol_return_roundtrip import BANK, Page
from reading_desk_roundtrip import ReadingDesk
from surfaces import reading_desk


@contextmanager
def fixture(destination=None, reported_reading=False):
    case = ReadingDesk('test_live_http_route_and_note')
    case.setUp()
    try:
        reading = case.create()['occurrence']
        lesson = ('## LESSON\n\n### Invented color rule\n\n'
                  'The synthetic rule selects purple in both invented examples. '
                  '[Source: sources/example.md, line 2]\n\n')
        bank = BANK.replace('Q1.', lesson + 'Q1.', 1)
        bank = bank.replace('[OBJECTIVE: logic:notation]',
                            '[OBJECTIVE: ' + case.objective + ']\n'
                            '[LESSON-REF: Invented color rule]')
        short = ('# Synthetic pending explanation\n\nQ1. Explain the invented rule.\n'
                 '[TYPE: short]\n[OBJECTIVE: ' + case.objective + ']\n'
                 'MODEL: The invented rule selects purple.\n\nRUBRIC:\n'
                 '- Describes the invented selection rule.\n'
                 '- Applies that rule to an invented example.\n\n'
                 'TRAP: Treating a pending answer as an incorrect answer.\n'
                 'CONFIDENCE: high\n')
        for stem, raw in (('symbols', bank), ('pending', short)):
            Path(case.base, stem + '.md').write_text(raw, encoding='utf-8')
            linked = journal.op_link(case.base, 'bank', stem + '.md', 'human', 'test',
                                     rights={'read': 'granted', 'transform': 'granted'})
            journal.op_adopt(case.base, linked['object_id'], linked['fingerprint'], 'human', 'test')
            course.bind_treatment(case.base, case.objective, case.source_id, 'practice',
                                  stem + '.md', 'covered', 'high', 'human', 'test')
        course.bind_treatment(case.base, case.objective, case.source_id, 'guided-lesson',
                              'symbols.md', 'covered', 'high', 'human', 'test')
        if reported_reading:
            case.declare(case.confirmation(reading))
        root = Path(case.root)
        if destination:
            shutil.copytree(root, destination)
            root = destination
        base = root / 'synthetic'
        banks = [(stem, str(base / (stem + '.md'))) for stem in ('pending', 'symbols')]
        yield root, base, banks, {
            'reading': reading_desk.href('synthetic', reading),
            'objective': case.objective,
            'course': 'synthetic',
            'source_id': case.source_id,
            'source_fingerprint': case.source_fp,
        }
    finally:
        case.doCleanups()


def snapshot(root, *, allow_indexes=False, timed_sitting=None):
    """Hash canonical bytes, with explicit allowances for index and view timing.

    Index files are disposable. An intentional quiz GET refreshes served_ts
    for response timing; every other saved-session field remains authoritative.
    Guidance, explanation and damaged-evidence checks use strict defaults.
    """
    hashes = {}
    for path in root.rglob('*'):
        if not path.is_file():
            continue
        if allow_indexes and path.parent.name == '_evidence' and path.name in (
                'evidence_index.sqlite3', 'evidence_index.sqlite3.lock'):
            continue
        raw = path.read_bytes()
        if timed_sitting and path == Path(timed_sitting):
            data = json.loads(raw)
            data.pop('served_ts', None)
            raw = json.dumps(data, sort_keys=True).encode()
        hashes[str(path.relative_to(root))] = hashlib.sha256(raw).hexdigest()
    return hashes


def source_fingerprints():
    paths = ('evidence.py', 'runtime.py',
               'runtime_sessions.py', 'runtime_teaching.py', 'runtime_feedback.py', 'runtime_visual_contract.py', 'runtime_gloss.py', 'surfaces/course_workbench.py',
             'surfaces/daemon.py', 'surfaces/presentation.py',
             'surfaces/ia.py', 'surfaces/session.py', 'surfaces/lesson.py',
             'tests/course_guidance_journey_roundtrip.py')
    return {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in paths}


def guidance(root, base, banks):
    before = snapshot(root)
    result = cw.course_guidance(str(root), str(base), course.read_course(base)['doc'], banks)
    assert snapshot(root) == before, 'guidance changed durable accepted state'
    assert {'kind', 'title', 'reason', 'href', 'objective'} <= result.keys(), result
    assert result['kind'] in ('review', 'resume', 'pending', 'start', 'unavailable'), result
    assert result['title'] and result['reason'] and result['href'], result
    return result


@contextmanager
def served(root):
    process, url, lines = start_daemon(str(root))
    try:
        yield url
    finally:
        process.terminate()
        process.wait(timeout=10)
        if process.stdout:
            process.stdout.close()


def get(url, route):
    status, _, markup = request(urllib.parse.urljoin(url, route))
    assert status == 200, (route, status, markup[:250])
    return markup


def rendered_guidance(markup, result):
    assert html.escape(result['title']) in markup, result
    assert html.escape(result['reason']) in markup, result
    assert html.escape(result['href'], quote=True) in markup, result
    if result.get('resume_href'):
        assert html.escape(result['resume_href'], quote=True) in markup, result


def start_saved(root, base, stem='symbols', mode='practice', count=2):
    attempts = root / '_attempts'
    attempts.mkdir(exist_ok=True)
    path = attempts / ('session_' + mode + '_' + stem + '.json')
    started = session.do_start(str(base / (stem + '.md')),
                               {'count': count, 'seed': 0, 'selection_mode': 'exam'},
                               mode, str(path), False)
    return path, started


def check_no_auto_start():
    with fixture() as (root, base, banks, meta):
        missing = evidence.course_counts(evidence.log_path(base))
        assert missing['complete'] and missing['responses'] == 0, missing
        result = guidance(root, base, banks)
        assert result['kind'] == 'start', result
        assert not result['href'].startswith('/quiz/'), result
        with served(root) as url:
            before = snapshot(root)
            for route in ('/', '/courses', '/course/synthetic', '/course/synthetic/learn',
                          '/course/synthetic/practice', '/course/synthetic/test',
                          '/course/synthetic/evidence', meta['reading']):
                markup = get(url, route)
                if route == '/course/synthetic':
                    rendered_guidance(markup, result)
            assert snapshot(root) == before, 'normal course entry GET started or wrote work'
        log = Path(evidence.log_path(base))
        log.parent.mkdir(exist_ok=True)
        log.write_text('', encoding='utf-8')
        empty = evidence.course_counts(str(log))
        assert empty['complete'] and empty['events'] == 0, empty
        assert guidance(root, base, banks)['kind'] == 'start'


def check_reading_only():
    with fixture(reported_reading=True) as (root, base, banks, _meta):
        counts = evidence.course_counts(evidence.log_path(base))
        assert counts['complete'] and counts['responses'] == 0 and counts['sessions'] == 0, counts
        history = cw.review_history(str(root), str(base), course.read_course(base)['doc'], banks)
        assert history['counts']['reading_reported'] == 1 and history['counts']['settled'] == 0, history
        result = guidance(root, base, banks)
        assert result['kind'] == 'start' and not result['href'].startswith('/quiz/'), result
        with served(root) as url:
            before = snapshot(root)
            rendered_guidance(get(url, '/course/synthetic'), result)
            get(url, result['href'])
            assert snapshot(root) == before, 'reading-only guidance/start GET wrote assessment work'
            before_evidence = snapshot(root, allow_indexes=True)
            get(url, '/course/synthetic/evidence')
            assert snapshot(root, allow_indexes=True) == before_evidence
        return {'counts': counts, 'guidance': result, 'reading_declarations': 1,
                'assessment_responses': 0}


def check_damaged_evidence():
    observed = []
    for state in ('unreadable', 'malformed', 'future'):
        with fixture() as (root, base, banks, _meta):
            log = Path(evidence.log_path(base))
            log.parent.mkdir(exist_ok=True)
            if state == 'unreadable':
                log.mkdir()
            elif state == 'malformed':
                path, _started = start_saved(root, base)
                assert session.do_submit(str(path), 'A', None)['accepted']
                with log.open('a', encoding='utf-8') as handle:
                    handle.write('not JSON\n')
            else:
                log.write_text(json.dumps({'schema_version': evidence.EVENT_SCHEMA_VERSION + 1,
                                          'event_type': 'response', 'event_id': 'f' * 32}) + '\n')
            counts = evidence.course_counts(str(log))
            assert not counts['complete'] and counts['issues'], (state, counts)
            assert counts['state'] not in ('missing', 'empty', 'available'), (state, counts)
            if state == 'unreadable':
                assert all(counts[name] is None for name in ('events', 'responses', 'marks', 'sessions')), counts
            if state == 'malformed':
                assert counts['responses'] == 1, 'readable partial evidence was discarded: %r' % counts
            result = guidance(root, base, banks)
            assert result['kind'] == 'unavailable', (state, result)
            with served(root) as url:
                before = snapshot(root)
                overview = get(url, '/course/synthetic')
                rendered_guidance(overview, result)
                markup = get(url, '/course/synthetic/evidence')
                assert 'unavailable' in markup.lower() or 'incomplete' in markup.lower(), (state, markup)
                after = snapshot(root)
                assert after == before, (state, 'damaged-evidence GET mutated durable files',
                                         [name for name in set(before) | set(after) if before.get(name) != after.get(name)])
            observed.append({'fault': state, 'counts': counts, 'guidance': result})
    return observed


def submit_native(url, route, answer='A'):
    page = Page(get(url, route))
    status, _, answered = request(urllib.parse.urljoin(url, page.answer_path),
                                  {'action': 'submit', 'form_token': page.form_token, 'option': answer})
    assert status == 200, (status, answered[:300])
    return page.card['data-session-id'], answered


def check_miss_detour_restart(destination=None):
    with fixture(destination) as (root, base, banks, meta):
        with served(root) as url:
            sid, _answered = submit_native(url, '/quiz/symbols?mode=practice&course=synthetic')
            saved_path = daemon.session_index(str(root))[sid]
            saved = runtime.read_session(saved_path)
            assert len(saved['responses']) == 1, saved
            counts = evidence.course_counts(evidence.log_path(base))
            assert counts['complete'] and counts['responses'] == 1, counts
            result = guidance(root, base, banks)
            assert result['kind'] == 'review' and result['objective'] == meta['objective'], result
            assert result['href'].startswith('/lesson/symbols?') and sid in result['href'], result
            assert sid in result['resume_href'], result
            exact = urllib.parse.parse_qs(urllib.parse.urlsplit(result['href']).query)['return'][0]
            assert exact == result['resume_href'], result
            reference = Page(get(url, exact)).card
            assert reference['data-session-id'] == sid
            before = snapshot(root)
            sitting_before = json.loads(Path(saved_path).read_text())
            rendered_guidance(get(url, '/course/synthetic'), result)
            assert snapshot(root) == before, 'course overview guidance changed accepted state'
            lesson = get(url, result['href'])
            assert snapshot(root) == before, 'linked explanation GET changed accepted state'
            assert 'Return to saved sitting' in lesson and 'Invented color rule' in lesson
            assert html.escape(exact, quote=True) in lesson
            before_navigation = snapshot(root, timed_sitting=saved_path)
            for _ in range(2):
                returned = Page(get(url, exact)).card
                assert returned['data-session-id'] == sid
                assert returned['data-item-id'] == reference['data-item-id'], (reference, returned)
            after = snapshot(root, timed_sitting=saved_path)
            sitting_after = json.loads(Path(saved_path).read_text())
            assert after == before_navigation, ('exact quiz return changed more than response timing',
                                     [name for name in set(before_navigation) | set(after) if before_navigation.get(name) != after.get(name)],
                                     {name: (sitting_before.get(name), sitting_after.get(name))
                                      for name in set(sitting_before) | set(sitting_after)
                                      if sitting_before.get(name) != sitting_after.get(name)})
        with served(root) as url:
            before = snapshot(root, timed_sitting=saved_path)
            restarted = guidance(root, base, banks)
            assert restarted == result, (result, restarted)
            returned = Page(get(url, exact)).card
            assert returned['data-session-id'] == sid and returned['data-item-id'] == reference['data-item-id']
            assert len(runtime.read_session(saved_path)['responses']) == 1
            assert snapshot(root, timed_sitting=saved_path) == before, 'daemon restart/return rewrote durable history'
        response = next(row for row in evidence.live_events(evidence.log_path(base))
                        if row.get('event_type') == 'response')
        evidence.append_event(evidence.log_path(base), evidence.retraction_event(response['event_id'], 'Synthetic correction'))
        retracted = evidence.course_counts(evidence.log_path(base))
        assert retracted['complete'] and retracted['responses'] == 0, retracted
        after_retraction = guidance(root, base, banks)
        assert after_retraction['kind'] == 'resume', after_retraction
        assert sid in after_retraction['href'] and not after_retraction['href'].startswith('/lesson/'), after_retraction
        return {'saved_session': sid, 'saved_item': reference['data-item-id'],
                'guidance': result, 'retracted_guidance': after_retraction,
                'timing_only_change': {'path': str(Path(saved_path).relative_to(root)),
                                      'field': 'served_ts', 'before': sitting_before['served_ts'],
                                      'after': sitting_after['served_ts']}}


def check_pending_and_blind_modes():
    observed = []
    for mode in ('practice', 'exam', 'diagnostic'):
        with fixture() as (root, base, banks, _meta):
            stem, count = ('pending', 1) if mode == 'practice' else ('symbols', 2)
            path, started = start_saved(root, base, stem, mode, count)
            wording = 'PRIVATE synthetic pending wording' if stem == 'pending' else 'A'
            submitted = session.do_submit(str(path), wording, None)
            assert submitted['accepted'], submitted
            result = guidance(root, base, banks)
            if stem == 'pending':
                assert result['kind'] == 'pending', result
                history = cw.review_history(str(root), str(base), course.read_course(base)['doc'], banks)
                assert history['counts']['pending'] == 1 and history['counts']['missed'] == 0, history
            else:
                assert result['kind'] in ('resume', 'unavailable'), (mode, result)
                assert not result['href'].startswith('/lesson/'), (mode, result)
                if result['kind'] == 'unavailable':
                    assert result['objective'] is None, (mode, result)
                assert 'missed' not in result['reason'].lower() and 'incorrect' not in result['reason'].lower(), result
                assert not runtime.assessment_feedback_released(mode, runtime.read_session(str(path)))
            with served(root) as url:
                raw_before = snapshot(root)
                before = snapshot(root, allow_indexes=True)
                for route in ('/course/synthetic', '/course/synthetic/evidence'):
                    markup = get(url, route)
                    if stem == 'pending':
                        assert wording not in markup, 'course history disclosed raw learner prose'
                    assert 'The invented rule selects the second color.' not in markup
                    assert 'CORRECT:' not in markup and 'WHY BEST:' not in markup
                    if route == '/course/synthetic':
                        rendered_guidance(markup, result)
                        assert snapshot(root) == raw_before, 'course guidance changed accepted bytes or caches'
                    if stem != 'pending':
                        assert 'name="action" value="review_missed"' not in markup, 'blind response leaked into missed-item review'
                raw_after = snapshot(root)
                cache_changes = [name for name in set(raw_before) | set(raw_after)
                                 if raw_before.get(name) != raw_after.get(name)]
                after = snapshot(root, allow_indexes=True)
                assert after == before, (mode, 'course feedback GET changed durable history',
                                         [name for name in set(before) | set(after) if before.get(name) != after.get(name)])
            observed.append({'mode': mode, 'guidance': result, 'session': started['session_id'],
                             'derived_cache_changes': cache_changes})
    return observed


def check_changed_context_refusal():
    observed = []
    for fault in ('rights', 'source-stale', 'bank-stale', 'ambiguous'):
        with fixture() as (root, base, banks, meta):
            path, _started = start_saved(root, base)
            assert session.do_submit(str(path), 'A', None)['accepted']
            initial = guidance(root, base, banks)
            assert initial['kind'] == 'review' and initial['href'].startswith('/lesson/'), initial
            if fault == 'rights':
                journal.op_grant_rights(str(base), meta['source_id'], {'transform': 'denied'},
                                        meta['source_fingerprint'], 'human', 'test')
            elif fault in ('source-stale', 'bank-stale'):
                changed = base / ('sources/example.md' if fault == 'source-stale' else 'symbols.md')
                changed.write_text(changed.read_text() + '\nExternal synthetic edit.\n', encoding='utf-8')
            else:
                second = root / '_attempts' / 'session_second.json'
                session.do_start(str(base / 'symbols.md'),
                                 {'count': 2, 'seed': 1, 'selection_mode': 'exam'},
                                 'practice', str(second), False)
            result = guidance(root, base, banks)
            assert not result['href'].startswith('/lesson/'), (fault, result)
            if fault in ('rights', 'source-stale'):
                assert result['kind'] == 'review' and result['resume_href'] == initial['resume_href'], (fault, result)
            else:
                assert result['kind'] == 'unavailable' and not result.get('resume_href'), (fault, result)
            with served(root) as url:
                before = snapshot(root)
                markup = get(url, '/course/synthetic')
                assert html.escape(result['title']) in markup, (fault, result)
                rendered_guidance(markup, result)
                assert snapshot(root) == before, (fault, 'refused guidance changed accepted bytes')
            observed.append({'refusal': fault, 'guidance': result})
    return observed


def check_browser(shots):
    from playwright.sync_api import sync_playwright
    shots.mkdir(parents=True, exist_ok=True)
    measured = []
    with fixture() as (root, base, banks, _meta):
        with served(root) as url, sync_playwright() as pw:
            browser = pw.chromium.launch(channel='chrome', headless=True)
            try:
                for width in (1280, 390, 320):
                    context = browser.new_context(viewport={'width': width, 'height': 900}, color_scheme='light', reduced_motion='reduce')
                    page = context.new_page()
                    before = snapshot(root)
                    page.goto(url + 'course/synthetic')
                    page.wait_for_load_state('networkidle')
                    assert snapshot(root) == before, 'browser course overview auto-started work'
                    size = page.evaluate('({viewport:innerWidth, scroll:document.documentElement.scrollWidth})')
                    assert size['scroll'] <= size['viewport'] + 1, ('start', width, size)
                    page.screenshot(path=str(shots / ('start-' + str(width) + '.png')), full_page=True)
                    measured.append(dict(surface='start', width=width, browser_version=browser.version,
                                         screenshot='start-' + str(width) + '.png', **size))
                    context.close()
                submit_native(url, '/quiz/symbols?mode=practice&course=synthetic')
                result = guidance(root, base, banks)
                for width in (1280, 390, 320):
                    context = browser.new_context(viewport={'width': width, 'height': 900}, color_scheme='light', reduced_motion='reduce')
                    page = context.new_page()
                    page.goto(url + 'course/synthetic')
                    page.wait_for_load_state('networkidle')
                    size = page.evaluate('({viewport:innerWidth, scroll:document.documentElement.scrollWidth})')
                    assert size['scroll'] <= size['viewport'] + 1, ('review', width, size)
                    recommendation = page.locator('#course-guidance [data-guidance-action]')
                    assert recommendation.get_attribute('href') == result['href']
                    assert page.locator('#course-guidance [data-course-resume]').get_attribute('href') == result['resume_href']
                    for _ in range(60):
                        page.keyboard.press('Tab')
                        if recommendation.evaluate('(node) => node === document.activeElement'):
                            break
                    assert recommendation.evaluate('(node) => node === document.activeElement'), 'guidance action was not keyboard reachable'
                    focused = page.evaluate('({href:document.activeElement.getAttribute("href"),outline:getComputedStyle(document.activeElement).outlineStyle,shadow:getComputedStyle(document.activeElement).boxShadow})')
                    assert focused['href'] == result['href'] and (focused['outline'] != 'none' or focused['shadow'] != 'none'), focused
                    page.screenshot(path=str(shots / ('review-' + str(width) + '.png')), full_page=True)
                    page.keyboard.press('Tab')
                    resume_link = page.locator('#course-guidance [data-course-resume]')
                    assert resume_link.evaluate('(node) => node === document.activeElement'), 'exact Resume was not next in keyboard order'
                    resume_focus = page.evaluate('''() => {
                        const link = document.activeElement.getBoundingClientRect();
                        const nav = document.querySelector('.product-sidebar');
                        const fixed = nav && getComputedStyle(nav).position === 'fixed';
                        return {top:link.top,bottom:link.bottom,viewport:innerHeight,
                                fixed_nav_top:fixed ? nav.getBoundingClientRect().top : null};
                    }''')
                    page.screenshot(path=str(shots / ('resume-focus-' + str(width) + '.png')), full_page=True)
                    if resume_focus['fixed_nav_top'] is not None:
                        assert resume_focus['bottom'] <= resume_focus['fixed_nav_top'] + 1, ('exact Resume covered by fixed navigation', width, resume_focus)
                    page.keyboard.press('Shift+Tab')
                    assert recommendation.evaluate('(node) => node === document.activeElement')
                    sid = urllib.parse.parse_qs(urllib.parse.urlsplit(result['resume_href']).query)['session'][0]
                    saved_path = daemon.session_index(str(root))[sid]
                    before = snapshot(root, timed_sitting=saved_path)
                    with page.expect_navigation(wait_until='networkidle'):
                        page.keyboard.press('Enter')
                    assert '/lesson/symbols?' in page.url, page.url
                    page.get_by_role('link', name='Return to saved sitting', exact=True).click()
                    page.wait_for_load_state('networkidle')
                    card = page.locator('[data-server-baseline]').first
                    sid, item = card.get_attribute('data-session-id'), card.get_attribute('data-item-id')
                    assert sid in result['resume_href']
                    page.reload()
                    page.wait_for_load_state('networkidle')
                    assert page.locator('[data-server-baseline]').first.get_attribute('data-item-id') == item
                    assert snapshot(root, timed_sitting=saved_path) == before, 'keyboard reference detour/reload wrote durable state'
                    measured.append(dict(surface='review', width=width, session=sid, item=item, focus=focused,
                                         resume_focus=resume_focus, browser_version=browser.version,
                                         screenshot='review-' + str(width) + '.png', **size))
                    context.close()
            finally:
                browser.close()
    (shots / 'measurements.json').write_text(json.dumps(measured, indent=2), encoding='utf-8')
    return measured


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence-dir', type=Path)
    parser.add_argument('--browser-shots', type=Path)
    args = parser.parse_args()
    initial = source_fingerprints()
    check_no_auto_start()
    result = {'damaged': check_damaged_evidence(),
              'reading_only': check_reading_only(),
              'journey': check_miss_detour_restart(),
              'pending_and_blind': check_pending_and_blind_modes(),
              'changed_context_refusal': check_changed_context_refusal()}
    if args.browser_shots:
        result['actual_browser'] = check_browser(args.browser_shots)
    result['source_fingerprints'] = source_fingerprints()
    assert result['source_fingerprints'] == initial, 'production source changed during verification; rerun after writers release'
    result['html_http_verified'] = True
    result['browser_verified'] = bool(args.browser_shots)
    result['unverified'] = ['human preference', 'screen reader', 'physical touch', 'learning effectiveness']
    result['explicit_get_allowances'] = {
        'healthy_evidence': ['synthetic/_evidence/evidence_index.sqlite3', 'synthetic/_evidence/evidence_index.sqlite3.lock'],
        'intentional_exact_quiz_navigation': 'served_ts only in the requested existing saved sitting',
        'guidance_lesson_unavailable': 'no file changes',
    }
    if args.evidence_dir:
        args.evidence_dir.mkdir(parents=True, exist_ok=True)
        (args.evidence_dir / 'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print('Course guidance journey: truthful history, pending/blind boundaries, read-only native entry, exact detour/reload/restart and retraction pass')


if __name__ == '__main__':
    main()
