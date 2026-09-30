#!/usr/bin/env python3
"""Ordinary native outline, source context and inline answer journeys."""
import argparse
import html
import json
from pathlib import Path
import re
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
import course
import graph
import notes
import reading_desk
import runtime
from surfaces import agent_operation, daemon
from a5_research_context_roundtrip import fixture, fields
from course_workbench_roundtrip import start_runtime


def request(url, values=None, headers=None):
    data = urllib.parse.urlencode(values, doseq=True).encode() if values is not None else None
    req = urllib.request.Request(url, data=data, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.status, response.url, response.read().decode()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.url, exc.read().decode()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime', default=str(ROOT / 'itembank.py'))
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='a5-served-') as directory:
        root = Path(directory)
        base, refs = fixture(root)
        read = course.read_course(base)
        first = graph.add_objective(read['doc'], 'Read the source', objective_id='synthetic:read')['id']
        second = graph.add_objective(read['doc'], 'Use the source', objective_id='synthetic:use')['id']
        course.write_course(base, read['doc'], read['fingerprint'], 'human', 'test')
        course.bind_treatment(base, first, refs[0]['source_id'], 'direct-reading', 'L4', 'covered', 'high', 'human', 'test')
        (root / 'itembank.json').write_text(json.dumps({'auditor_autonomy': 'draft_and_approve'}))
        bank = Path(base, 'inline.md')
        bank.write_text((ROOT / 'fixtures/a5_inline_fields.md').read_text())
        lesson_bank = Path(base, 'lesson.md')
        lesson_bank.write_text((ROOT / 'fixtures/lesson_comparison.md').read_text())
        cid = course.read_course(base)['object_id']
        accepted = Path(base, 'course-graph.md').read_bytes()
        proc, url, _lines = start_runtime(directory, args.runtime)
        try:
            prefix = url + 'course/' + cid
            status, _location, page = request(prefix + '/build')
            assert status == 200 and 'Outline and treatments' in page
            proposal = dict(expected_course_fingerprint=course.read_course(base)['fingerprint'],
                **{'order-' + first: '1', 'order-' + second: '2',
                   'treatment-' + second: 'guided-lesson', 'source-' + second: refs[0]['source_id'], 'locator-' + second: 'L4'})
            status, location, page = request(prefix + '/outline/propose', proposal)
            assert status == 200 and 'Exact diff' in page and Path(base, 'course-graph.md').read_bytes() == accepted
            pid = urllib.parse.parse_qs(urllib.parse.urlsplit(location).query)['outline'][0]
            old = agent_operation.status(base, pid)
            edited = dict(proposal, proposal_id=pid, expected_draft_fingerprint=agent_operation.draft_fingerprint(old['draft']))
            edited['treatment-' + second] = 'worked-example'
            assert request(prefix + '/outline/propose', edited)[0] == 200
            assert request(prefix + '/outline/accept', dict(proposal_id=pid,
                expected_draft_fingerprint=agent_operation.draft_fingerprint(old['draft'])))[0] == 400
            assert Path(base, 'course-graph.md').read_bytes() == accepted
            record = agent_operation.status(base, pid)
            verdict = dict(proposal_id=pid, expected_draft_fingerprint=agent_operation.draft_fingerprint(record['draft']))
            assert request(prefix + '/outline/reject', verdict)[0] == 200
            assert Path(base, 'course-graph.md').read_bytes() == accepted
            status, location, _page = request(prefix + '/outline/propose', proposal)
            pid = urllib.parse.parse_qs(urllib.parse.urlsplit(location).query)['outline'][0]
            record = agent_operation.status(base, pid)
            verdict = dict(proposal_id=pid, expected_draft_fingerprint=agent_operation.draft_fingerprint(record['draft']))
            assert request(prefix + '/outline/accept', verdict)[0] == 200
            assert Path(base, 'course-graph.md').read_bytes() != accepted
            # Duplicate fields and a foreign origin cannot mutate the course.
            before = Path(base, 'course-graph.md').read_bytes()
            assert request(prefix + '/outline/undo', {'proposal_id': [pid, pid]})[0] == 400
            assert request(prefix + '/outline/undo', {'proposal_id': pid}, {'Origin': 'https://example.invalid'})[0] == 403
            assert Path(base, 'course-graph.md').read_bytes() == before
            assert request(prefix + '/sources')[0] == 200
            status, _location, page = request(prefix + '/research')
            assert status == 200 and 'Exact locator ID' in page
            status, _location, page = request(prefix + '/research', fields(refs[0], 'preview'))
            assert status == 200 and 'Same sentence.' in page and 'Exact source preview' in page
            assert request(prefix + '/research', fields(refs[0], 'copy'))[0] == 200
            assert not Path(base, '_notes').exists()
            assert request(prefix + '/research', fields(refs[0], 'copy', confirm='yes'))[0] == 200
            document = notes.read_note_document(reading_desk.note_root(base), cid)
            selected = dict(operation=['save_scope'], reference=[json.dumps(refs[0])],
                note_id=[document['sidecar']['notes'][0]['note_id']],
                expected_notes_fingerprint=[document['fingerprint']], confirm=['yes'])
            assert request(prefix + '/research', selected)[0] == 200
            status, _location, page = request(prefix + '/research', {'operation': 'request_context'})
            assert status == 200 and 'Learner note' in page and 'EXCLUDED SENTINEL' not in page
            assert request(prefix + '/research', fields(refs[2], 'preview'))[0] == 400
            # The ordinary served form renders inline fields and preserves refusal.
            status, _location, page = request(url + 'quiz/inline?mode=exam&course=' + cid)
            assert status == 200 and 'fill-inline' in page and 'fill_color' in page and '{{color}}' not in page
            sid = re.search(r'data-session-id="([^"]+)"', page)[1]
            token = re.search(r'name="form_token" value="([^"]+)"', page)[1]
            answer_url = urllib.parse.urljoin(url, html.unescape(re.search(r'<form method="post" action="([^"]+)"', page)[1]))
            status, _location, page = request(answer_url, dict(action='submit', form_token=token,
                fill_color='  BLUE  ', fill_count='oops'))
            assert status == 400 and 'oops' in page and '  BLUE  ' in page
            token = re.search(r'name="form_token" value="([^"]+)"', page)[1]
            status, _location, page = request(answer_url, dict(action='submit', form_token=token,
                fill_color='  BLUE  ', fill_count='5/2'))
            assert status == 200 and 'Feedback is available after' in page
            saved = daemon.session_index(directory)[sid]
            assert runtime.read_session(saved)['responses'][0]['answer'] == {'color': '  BLUE  ', 'count': '5/2'}
            # Exact lesson returns validate both course and sitting admission.
            lesson_url = url + 'quiz/lesson?mode=practice&course=' + cid
            status, _location, page = request(lesson_url)
            assert status == 200
            lesson_sid = re.search(r'data-session-id="([^"]+)"', page)[1]
            resume = '/quiz/lesson?' + urllib.parse.urlencode(dict(mode='practice', session=lesson_sid, course=cid))
            status, _location, page = request(url + 'lesson/lesson?' + urllib.parse.urlencode({'return': resume}))
            assert status == 200 and 'Return to saved sitting' in page
            assert 'Return to saved sitting' not in request(url + 'lesson/lesson?' + urllib.parse.urlencode({'return': 'https://example.invalid/quiz/lesson'}))[2]
            proc.terminate(); proc.wait(timeout=5); proc.stdout.close()
            proc, url, _lines = start_runtime(directory, args.runtime)
            prefix = url + 'course/' + cid
            assert 'accepted' in request(prefix + '/build?outline=' + pid)[2]
            assert request(prefix + '/outline/undo', {'proposal_id': pid})[0] == 200
            assert Path(base, 'course-graph.md').read_bytes() == accepted
            assert 'Same sentence.' in request(prefix + '/research', {'operation': 'request_context'})[2]
            assert request(url + resume.lstrip('/'))[0] == 200
        finally:
            if proc.poll() is None:
                proc.terminate()
            proc.wait(timeout=5)
            proc.stdout.close()
    print('A5 ordinary source HTTP: corrected outline/stale/cancel/accept/restart/undo, write gates, exact local context, inline refusal/raw response and saved lesson return pass')


if __name__ == '__main__':
    main()
