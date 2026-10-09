#!/usr/bin/env python3
"""Exercise the synthetic course-to-native-lesson-and-practice journey."""
import importlib.util
from pathlib import Path
import shutil
import sys
import tempfile
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests'))
from daemon_roundtrip import json_request, start_daemon  # noqa: E402

PREVIEW_PATH = ROOT / 'prototypes' / 'ui-character-20261001' / 'native-preview.py'
SPEC = importlib.util.spec_from_file_location('native_preview', PREVIEW_PATH)
PREVIEW = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PREVIEW)


def get(base, path):
    try:
        with urllib.request.urlopen(base + path, timeout=5) as response:
            return response.status, response.read().decode('utf-8')
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode('utf-8')


def check_native_journey_and_disclosure():
    root = tempfile.mkdtemp(prefix='interaction_craft_native_')
    proc = None
    try:
        PREVIEW.prepare(root)
        proc, base, _lines = start_daemon(root)
        course_id, view = PREVIEW.prepare_course(root, base)

        status, shelf = get(base, 'courses')
        assert status == 200 and 'Synthetic interaction lab' in shelf

        status, course = get(base, 'course/' + course_id)
        assert status == 200 and 'Synthetic interaction lab' in course
        assert 'coding_boundary_unit' in course
        assert view['session_id'] in course
        assert 'CORRECT:' not in course and 'WHY BEST:' not in course
        status, learn = get(base, 'course/' + course_id + '/learn')
        assert status == 200
        assert 'coding_boundary_unit' in learn and 'lesson_comparison' in learn
        assert 'href="/lesson/coding_boundary_unit"' in learn
        assert 'href="/lesson/lesson_comparison"' in learn
        assert 'CORRECT:' not in learn and 'WHY BEST:' not in learn
        status, course_practice = get(base, 'course/' + course_id + '/practice')
        assert status == 200
        assert view['session_id'] in course_practice
        assert course_id in course_practice
        exact_practice = ('/quiz/coding_boundary_unit?mode=practice&amp;session=' +
                          view['session_id'] + '&amp;course=' + course_id)
        assert exact_practice in course_practice
        status, course_map = get(base, 'course/' + course_id + '/map')
        assert status == 200
        assert 'Explain and repair coding boundaries.' in course_map
        assert 'Compare equal intervals with a native visual.' in course_map
        course_areas = {}
        for area in ('learn', 'sources'):
            status, rendered_area = get(base, 'course/' + course_id + '/' + area)
            assert status == 200
            assert 'CORRECT:' not in rendered_area
            assert 'WHY BEST:' not in rendered_area
            course_areas[area] = rendered_area
        course_sources = course_areas['sources']
        assert 'coding_boundary_unit' in course_sources
        assert 'lesson_comparison' in course_sources

        status, continuous = get(base, 'lesson/coding_boundary_unit')
        assert status == 200 and 'data-reading-mode="continuous"' in continuous
        assert 'href="/course/' + course_id + '/learn"' in continuous
        assert 'class="code-source"' in continuous
        assert 'class="code-tools" hidden' in continuous
        status, guided = get(base, 'lesson/coding_boundary_unit?view=guided')
        assert status == 200 and 'data-reading-mode="guided"' in guided
        status, comparison = get(base, 'lesson/lesson_comparison')
        assert status == 200 and 'Compare equal intervals' in comparison
        assert 'class="comparison-static"' in comparison
        assert 'Starting comparison:' in comparison
        status, glossary = get(base, 'lesson/terms_above_lesson_bank')
        assert status == 200 and 'Widget' in glossary and 'Sprocket' in glossary

        query = ('quiz/coding_boundary_unit?mode=practice&session=' +
                 view['session_id'] + '&course=' + course_id)
        status, practice = get(base, query)
        assert status == 200 and 'session' in practice.lower(), practice
        course_href = 'href="/course/' + course_id + '"'
        assert course_href in practice
        assert 'CORRECT:' not in practice and 'WHY BEST:' not in practice
        status, submitted = json_request(base + 'api/submit', {
            'session_id': view['session_id'], 'answer': 'B'})
        assert status == 200, submitted
        status, after_submit = get(base, query)
        assert status == 200 and course_href in after_submit
        assert 'CORRECT:' not in after_submit and 'WHY BEST:' not in after_submit
        print('native journey: course entry, objective map, lesson modes, glossary, '
              'saved practice, course return and key withholding ok')
    finally:
        if proc is not None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except Exception:
                proc.kill()
                proc.wait(timeout=5)
            if proc.stdout:
                proc.stdout.close()
        shutil.rmtree(root, ignore_errors=True)


if __name__ == '__main__':
    check_native_journey_and_disclosure()
