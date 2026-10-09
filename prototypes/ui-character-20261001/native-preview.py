"""Preview the synthetic course journey through the native daemon."""
import argparse
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]

from surfaces import ia, session  # noqa: E402
from daemon_roundtrip import get, json_request, start_daemon  # noqa: E402

FIXTURES = (
    ROOT / 'fixtures' / 'coding_boundary_unit.md',
    ROOT / 'fixtures' / 'lesson_comparison.md',
    ROOT / 'fixtures' / 'terms_above_lesson_bank.md',
)


def prepare(root):
    """Copy the glossary fixture outside the course bank allowlist."""
    root = Path(root)
    shutil.copy2(FIXTURES[2], root / FIXTURES[2].name)


def _post_json(base, route, payload):
    status, body = json_request(base + route, payload)
    if status != 200:
        raise RuntimeError('%s returned %s: %s' % (route, status, body))
    return body


def prepare_course(root, base):
    """Create an empty-activity synthetic course through native operations.

    Sources are registered as .txt to keep source copies out of bank discovery.
    Their native .md bank copies live in the course. The graph records lesson
    and coding-practice treatments with unknown confidence and no learner
    completion or mastery state.
    """
    folder_id = 'synthetic-interaction-lab'
    created = _post_json(base, 'api/course/create', {
        'course_id': folder_id, 'title': 'Synthetic interaction lab'})
    course_id = created['course_object_id']
    course_dir = ia.course_dir_for(root, course_id)
    if course_dir is None:
        raise RuntimeError('canonical course lookup did not resolve the new course')
    container = _post_json(base, 'api/course/add-container', {
        'course_id': course_id, 'label': 'unit',
        'title': 'Native interaction specimens'})
    coding_source_id = coding_objective_id = None
    for bank_name, source_name, statement in (
            ('coding_boundary_unit.md', 'coding-boundary-source.txt',
             'Explain and repair coding boundaries.'),
            ('lesson_comparison.md', 'comparison-source.txt',
             'Compare equal intervals with a native visual.')):
        source = next(path for path in FIXTURES if path.name == bank_name)
        content = source.read_text(encoding='utf-8')
        imported = _post_json(base, 'api/course/register-source', {
            'course_id': course_id, 'filename': source_name, 'content': content,
            'grants': {'read': 'granted', 'transform': 'granted'}})
        source_id = imported['source_object_id']
        _post_json(base, 'api/course/add-source', {
            'course_id': course_id, 'source_object_id': source_id,
            'title': source.stem})
        objective = _post_json(base, 'api/course/add-objective', {
            'course_id': course_id, 'container': container['container_id'],
            'statement': statement})
        _post_json(base, 'api/course/bind-treatment', {
            'course_id': course_id, 'objective': objective['objective_id'],
            'source': source_id, 'treatment': 'guided-lesson'})
        shutil.copy2(source, Path(course_dir) / bank_name)
        if bank_name == 'coding_boundary_unit.md':
            coding_source_id = source_id
            coding_objective_id = objective['objective_id']
    _post_json(base, 'api/course/bind-treatment', {
        'course_id': course_id, 'objective': coding_objective_id,
        'source': coding_source_id, 'treatment': 'practice',
        'locator': 'coding_boundary_unit.md, Q1'})
    # Refreshes the native bank allowlist after creating course-contained banks.
    get(base + 'courses')
    view = session.do_start(
        str(Path(course_dir) / 'coding_boundary_unit.md'),
        {'count': 4, 'seed': 0, 'pair': 'boundary-workshop'}, 'practice',
        str(Path(root) / '_attempts' / 'session_boundary_workshop.json'),
        False)
    return course_id, view


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=0)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='itembank-native-journey-') as root:
        prepare(root)
        proc = None
        try:
            proc, base, _lines = start_daemon(root, '--port', str(args.port))
            course_id, view = prepare_course(root, base)
            print('Courses: ' + base + 'courses', flush=True)
            print('Synthetic course: ' + base + 'course/' + course_id,
                  flush=True)
            print('Course Learn: ' + base + 'course/' + course_id + '/learn',
                  flush=True)
            print('Coding lesson, continuous: ' + base +
                  'lesson/coding_boundary_unit', flush=True)
            print('Coding lesson, guided: ' + base +
                  'lesson/coding_boundary_unit?view=guided', flush=True)
            print('Comparison lesson: ' + base +
                  'lesson/lesson_comparison', flush=True)
            print('Glossary lesson: ' + base +
                  'lesson/terms_above_lesson_bank', flush=True)
            print('Saved coding practice: ' + base +
                  'quiz/coding_boundary_unit?mode=practice&session=' +
                  view['session_id'] + '&course=' + course_id, flush=True)
            print('Disposable synthetic root: ' + root, flush=True)
            try:
                input('Press Enter to stop the preview and remove its synthetic files: ')
            except (EOFError, KeyboardInterrupt):
                pass
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


if __name__ == '__main__':
    main()
