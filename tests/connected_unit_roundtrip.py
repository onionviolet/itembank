#!/usr/bin/env python3
"""One synthetic source, native comparison, practice, and saved result journey."""
import html
from pathlib import Path
import re
import sys
import tempfile
import urllib.parse
import urllib.request
import urllib.error

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tests'))

import course
import evidence
import runtime
from surfaces import course_ops, daemon, ia
from daemon_roundtrip import start_daemon, get


def make_unit(root):
    base = Path(root) / 'synthetic'
    call = lambda name, **fields: course_ops.run(root, name,
                                                  dict(course_id='synthetic', **fields))
    call('create', title='Rainfall comparison')
    call('add_objective', statement='Compare two readings over equal intervals')
    objective = course.read_course(str(base))['doc']['objectives'][0]['id']
    source = call('register_source', filename='rainfall.md',
                  content='# Rainfall\nA rain gauge measures rainfall depth in millimeters. '
                          'Gauge A collected 12 mm in 24 hours and gauge B collected '
                          '18 mm in 24 hours.\n',
                  grants={'read': 'granted', 'transform': 'granted'})
    source_id = source['source_object_id']
    call('add_source', source_object_id=source_id, title='Rainfall source')
    call('bind_treatment', objective=objective, source=source_id,
         treatment='direct-reading', locator='line 2')
    values = {
        'objective_ids': [objective],
        'source_ref': {'source_object_id': source_id,
                       'source_fingerprint': source['fingerprint'],
                       'locator': 'line 2',
                       'range': {'span_id': 'sp-1', 'locator_id': None,
                                 'locator_sidecar_fingerprint': None}},
        'purpose': 'Compare the two depths over equal time.',
        'preparation_mode': 'preread',
        'path_role': 'required-instructor-work',
        'learning_phase': 'Ahead',
        'sequence_evidence': {'status': 'Published', 'citation': 'synthetic source'},
        'assignment_provenance': {'authority': 'instructor',
                                  'citation': 'synthetic source'},
        'assistance_policy': {'status': 'unknown', 'citation': None,
                              'instruction': None},
    }
    reading = call('create_reading', expected_fingerprint=course.read_course(str(base))['fingerprint'],
                   binding_index=0, values=values, title='Read the gauge values',
                   activation='Now')
    bank = base / 'rainfall_unit.md'
    bank.write_text((ROOT / 'fixtures/lesson_comparison.md').read_text())
    call('bind_treatment', objective=objective, source=source_id,
         treatment='practice', locator='rainfall_unit.md')
    return base, bank, reading['occurrence']


def check_connected_unit():
    with tempfile.TemporaryDirectory(prefix='connected_unit_') as root:
        base, bank, occurrence = make_unit(root)
        course_id = course.read_course(str(base))['object_id']
        proc, url, lines = start_daemon(root)
        try:
            status, home = get(url)
            assert status == 200 and 'Rainfall comparison' in home
            status, overview = get(url + 'course/' + course_id)
            assert status == 200 and 'Rainfall comparison' in overview
            assert 'Your course path' in overview
            assert 'Read the source' in overview and 'Explore the lesson' in overview
            assert 'Practice what you learned' in overview
            assert ('quiz/rainfall_unit?mode=practice&amp;course=' + course_id) in overview
            assert overview.index('Read the source') < overview.index('Explore the lesson')
            assert 'Course tools' in overview
            overview_reading = re.search(r'href="([^"]+\?from=overview)"[^>]*>Read the source</a>',
                                         overview)
            assert overview_reading
            status, overview_source = get(url + html.unescape(overview_reading.group(1)).lstrip('/'))
            assert status == 200 and 'Back to overview' in overview_source
            assert ('href="/course/' + course_id + '"') in overview_source
            status, learn = get(url + 'course/' + course_id + '/learn')
            reading_url = ('course/%s/reading/%s/%s' %
                           (course_id, occurrence['occurrence_id'], occurrence['revision_id']))
            assert status == 200 and reading_url in learn
            assert '/lesson/rainfall_unit' in learn
            status, source_page = get(url + reading_url)
            assert status == 200 and 'Gauge A collected 12 mm' in source_page
            assert '/course/' + course_id + '/learn' in source_page
            status, lesson_page = get(url + 'lesson/rainfall_unit')
            assert status == 200 and 'class="lesson-comparison"' in lesson_page
            assert 'Static examples' in lesson_page
            practice_url = 'quiz/rainfall_unit?mode=practice&course=' + course_id
            assert practice_url.replace('&', '&amp;') in lesson_page
            status, practice_area = get(url + 'course/' + course_id + '/practice')
            assert status == 200 and practice_url.replace('&', '&amp;') in practice_area
            status, practice = get(url + practice_url)
            assert status == 200 and 'course=' + course_id in practice
            index = daemon.session_index(root)
            assert len(index) == 1
            session_id, path = next(iter(index.items()))
            before = runtime.read_session(path)
            assert before['mode'] == 'practice' and before['status'] == 'active'
            status, overview_active = get(url + 'course/' + course_id)
            assert status == 200 and 'Resume practice' in overview_active
            assert ('session=' + session_id + '&amp;course=' + course_id) in overview_active
            exact = ia.course_shelf_state(root)['cards'][0]['cta_href']
            assert 'session=' + session_id in exact and 'course=' + course_id in exact
            proc.terminate(); proc.wait(timeout=5)
            proc, url, lines = start_daemon(root)
            assert ia.course_shelf_state(root)['cards'][0]['cta_href'] == exact
            status, resumed_page = get(url + exact.lstrip('/'))
            assert status == 200
            after = runtime.read_session(path)
            assert all(after[key] == before[key]
                       for key in ('session_id', 'cursor', 'items', 'responses'))
            token = re.search(r'name="form_token" value="([^"]+)"', resumed_page)
            action = re.search(r'<form[^>]+action="([^"]*rainfall_unit/answer[^"]*)"',
                               resumed_page)
            assert token and action
            fields = urllib.parse.urlencode({
                'option': 'C', 'form_token': token.group(1), 'action': 'submit',
            }).encode()
            request = urllib.request.Request(
                urllib.parse.urljoin(url, html.unescape(action.group(1))),
                data=fields, method='POST',
                headers={'Content-Type': 'application/x-www-form-urlencoded'})
            try:
                with urllib.request.urlopen(request, timeout=5) as response:
                    feedback = response.read().decode()
            except urllib.error.HTTPError as exc:
                raise AssertionError(exc.read().decode() + '\n' + ''.join(lines[-12:])) from exc
            assert 'View summary' in feedback
            assert 'session=' + session_id in feedback
            assert runtime.read_session(path)['status'] == 'complete'
            attempt_dir = base / '_attempts'
            assert attempt_dir.is_dir()
            assert any(p.is_file() and p.suffix == '.md' and p.resolve().is_relative_to(base.resolve())
                       for p in attempt_dir.iterdir())
            log = evidence.log_path(str(base))
            responses = lambda: [event for event in evidence.events(log)
                                 if event.get('event_type') == 'response'
                                 and event.get('session_id') == session_id]
            assert len(responses()) == 1
            with urllib.request.urlopen(request, timeout=5) as response:
                replay = response.read().decode()
            assert 'Back to course' in replay
            assert len(responses()) == 1
            assert proc.poll() is None, ''.join(lines[-12:])
            status, report = get(url + 'report?session=' + session_id)
            assert status == 200 and 'Back to course' in report
            assert '/course/' + course_id in report
            status, returned = get(url + 'course/' + course_id)
            assert status == 200 and 'Saved sittings' in returned
            assert '/report?session=' + session_id in returned
            assert 'Saved on this device.' in returned
            assert 'Saved sitting ' not in returned
        finally:
            proc.terminate(); proc.wait(timeout=5)


if __name__ == '__main__':
    check_connected_unit()
    print('ok connected synthetic source, comparison, practice, result, return and restart')
