#!/usr/bin/env python3
"""Course shelf labels project persisted sessions without advancing them."""
import json
import os
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import course
import runtime
from surfaces import daemon, ia, session
from daemon_roundtrip import start_daemon, get, json_request


def snapshot(root):
    return {str(p.relative_to(root)): p.read_bytes()
            for p in root.rglob('*') if p.is_file()}


def check_resume():
    with tempfile.TemporaryDirectory(prefix='course_resume_') as temp:
        root = Path(temp)
        directory = root / 'synthetic'
        directory.mkdir()
        course.create_course(str(directory), 'Synthetic resume', 'agent', 'test')
        bank = directory / 'resume_bank.md'
        bank.write_text((ROOT / 'fixtures/sample_bank.md').read_text().split('Q3.')[0])
        ia.write_ia_state(temp, 'sample_course', {'removed': True})
        proc, url, _ = start_daemon(temp)
        try:
            def shelf(cue, label):
                before = snapshot(root)
                status, body = get(url)
                assert status == 200 and cue in body and label in body, (cue, label)
                assert snapshot(root) == before, 'shelf read mutated durable files'

            shelf('Not started', 'Start Synthetic resume')
            assert get(url + 'quiz/resume_bank')[0] == 200
            index = daemon.session_index(temp)
            assert len(index) == 1
            sid, path = next(iter(index.items()))
            shelf('Session in progress', 'Resume Synthetic resume')
            course_id = course.read_course(str(directory))['object_id']
            card = ia.course_shelf_state(temp)['cards'][0]
            exact = 'quiz/resume_bank?mode=practice&session=%s&course=%s' % (sid, course_id)
            assert card['cta_href'] == '/' + exact
            status, page = get(url + exact)
            assert status == 200 and 'session=' + sid in page
            assert 'answer?mode=practice&amp;session=' + sid in page
            assert json_request(url + 'quiz/resume_bank?mode=practice&session=missing&course=' + course_id,
                                method='GET')[0] == 400
            assert daemon.session_index(temp) == {sid: path}
            second_path = root / '_attempts' / 'session_second.json'
            session.do_start(str(bank), {'objective': '', 'count': 2, 'seed': 0,
                                         'selection_mode': 'practice'}, 'practice',
                             str(second_path), False, preset_session_id='second')
            choices = ia.course_shelf_state(temp)['cards'][0]
            assert choices['resume']['state'] == 'ambiguous'
            assert len([row for row in choices['resume']['sessions']
                        if row['status'] == 'active']) == 2
            assert choices['cta_href'] == '/course/' + course_id
            status, chooser = get(url + 'course/' + course_id)
            assert status == 200 and 'Saved sittings' in chooser
            assert 'session=second' in chooser and 'session=' + sid in chooser
            assert get(url + exact)[0] == 200
            second_path.unlink()
            session.do_submit(path, 'B', None)
            saved = runtime.read_session(path)
            assert saved['cursor'] == 1
            shelf('Session in progress', 'Resume Synthetic resume')
            assert get(url + 'course/' + course_id)[0] == 200
            assert get(url + 'quiz/resume_bank')[0] == 200
            resumed = runtime.read_session(path)
            assert daemon.session_index(temp) == {sid: path}
            for key in ('session_id', 'cursor', 'items', 'responses'):
                assert resumed[key] == saved[key], key
            # A new process still projects the persisted active sitting.
            proc.terminate()
            proc.wait(timeout=5)
            proc, url, _ = start_daemon(temp)
            shelf('Session in progress', 'Resume Synthetic resume')
            assert ia.course_shelf_state(temp)['cards'][0]['cta_href'] == '/' + exact
            assert get(url + exact)[0] == 200
            assert daemon.session_index(temp) == {sid: path}, 'restart created another sitting'
            status, view = json_request(url + 'api/next', {'session_id': sid})
            assert status == 200 and view['session_id'] == sid and view['position'] == 1
            assert runtime.read_session(path)['responses'] == saved['responses']
            session.do_submit(path, ['A', 'C'], None)
            assert runtime.read_session(path)['status'] == 'complete'
            shelf('Recorded sessions complete', 'Open Synthetic resume')
            proc.terminate()
            proc.wait(timeout=5)
            proc, url, _ = start_daemon(temp)
            assert get(url + 'quiz/resume_bank')[0] == 200
            assert runtime.read_session(path)['status'] == 'complete'
            assert daemon.session_index(temp) == {sid: path}
            report_status, report = get(url + 'report?session=' + sid)
            assert report_status == 200
            assert 'href="/course/%s"' % course_id in report
            assert 'Back to course' in report
            Path(path).write_text('{broken')
            shelf('Session status unavailable', 'Open Synthetic resume')
            before = snapshot(root)
            status, body = json_request(url + 'quiz/resume_bank', method='GET')
            assert status == 400 and 'saved session is unreadable' in body
            assert snapshot(root) == before
            Path(path).write_text(json.dumps(dict(saved, schema_version=99999)))
            shelf('Session status unavailable', 'Open Synthetic resume')
            Path(path).unlink()
            shelf('Previous activity recorded', 'Open Synthetic resume')
            with patch('runtime.read_session', side_effect=PermissionError):
                Path(path).write_text(json.dumps(saved))
                card = ia.course_shelf_state(temp)['cards'][0]
                assert card['resume_cue'] == 'Session status unavailable'
            with patch.object(ia, '_course_resume_state', side_effect=ImportError):
                card = ia.course_shelf_state(temp)['cards'][0]
                assert card['cta_label'] == 'Open Synthetic resume'
            # Test restart validation without a warmed in-memory session id.
            from types import SimpleNamespace
            import model
            handler = SimpleNamespace(root=temp, sessions={'resume_bank': {'mode': 'practice'}})
            original = bank.read_text()
            bank.write_text(original.replace('57ae87843edb459e', 'aaaaaaaaaaaaaaaa'))
            before = snapshot(root)
            try:
                daemon._ensure_quiz_session(handler, 'resume_bank', str(bank), model.load(str(bank)))
                raise AssertionError('changed selection was resumed')
            except ValueError as exc:
                assert 'selection' in str(exc)
            assert snapshot(root) == before
            bank.write_text(original)
            # Same ids do not prove that a bank edited later is the same revision.
            before = snapshot(root)
            try:
                daemon._ensure_quiz_session(handler, 'resume_bank', str(bank), model.load(str(bank)))
                raise AssertionError('modified bank was resumed without review')
            except ValueError as exc:
                assert 'modified' in str(exc)
            assert snapshot(root) == before
            for delta in ({'cursor': -1}, {'items': [999]}, {'mode': 'exam'},
                          {'schema_version': 99999}):
                Path(path).write_text(json.dumps(dict(saved, **delta)))
                before = snapshot(root)
                try:
                    daemon._ensure_quiz_session(handler, 'resume_bank', str(bank), model.load(str(bank)))
                    raise AssertionError('invalid or mismatched sitting resumed')
                except ValueError:
                    pass
                assert snapshot(root) == before
            Path(path).write_text(json.dumps(saved))
            newer = Path(path).with_name('session_newer.json')
            newer.write_text(json.dumps(dict(saved, session_id='newer', status='complete', cursor=2)))
            stamp = Path(path).stat().st_mtime + 1
            os.utime(newer, (stamp, stamp))
            shelf('Session status unavailable', 'Open Synthetic resume')
        finally:
            proc.terminate()
            proc.wait(timeout=5)
    print('ok course shelf new, active, returned, restarted, complete, unavailable and read-only')


if __name__ == '__main__':
    check_resume()
