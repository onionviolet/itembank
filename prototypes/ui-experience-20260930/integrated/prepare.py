"""Build a disposable synthetic source-served course through existing operations."""
import json
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
import course
from surfaces import course_ops, reading_desk
from reading_ops_roundtrip import ReadingOperations
from quiz_symbol_return_roundtrip import BANK

PASSAGE = ('For constant speed, distance equals speed multiplied by elapsed time. '
           'Walker A moves at 3 metres per second. Walker B moves at 5 metres per second. '
           'After six seconds, A has travelled 18 metres and B has travelled 30 metres. '
           'The 12 metre gap comes from their speed difference, 2 metres per second, '
           'multiplied by six seconds. Both walkers share the same clock. '
           'Equal intervals add equal distances for each walker, but different speeds '
           'produce different distances. This model assumes each speed stays constant.')


def prepare(destination):
    if destination.exists():
        raise SystemExit('Destination already exists; keep prior preview state.')
    with tempfile.TemporaryDirectory(prefix='motion-source-') as root:
        base = Path(root) / 'synthetic'
        def op(name, **body):
            return course_ops.run(root, name, dict(course_id='synthetic', **body))
        op('create', title='Motion studies (synthetic)')
        op('add_objective', statement='Explain how speed and elapsed time determine distance.')
        objective = course.read_course(base)['doc']['objectives'][0]['id']
        source = op('register_source', filename='motion.md', content='# Constant speed\n'+PASSAGE+'\n',
                    grants={'read': 'granted', 'transform': 'granted'})
        op('add_source', source_object_id=source['source_object_id'], title='Constant speed, synthetic source')
        op('bind_treatment', objective=objective, source=source['source_object_id'],
           treatment='direct-reading', locator='line 2')
        case = ReadingOperations()
        case.objective, case.source_id, case.source_fp = objective, source['source_object_id'], source['fingerprint']
        values = case.values()
        values.update(purpose='Compare the two walkers at the same elapsed time.', path_role='learner-chosen')
        row = op('create_reading', expected_fingerprint=course.read_course(base)['fingerprint'],
                 binding_index=0, values=values, title='Two walkers, one clock', activation='Now')['occurrence']
        lesson = '## LESSON\n\n### Two walkers, one clock\n\n'+PASSAGE+'\n\n'
        bank = BANK.replace('Q1.', lesson+'Q1.', 1)
        (base / 'symbols.md').write_text(bank)
        Path(root, 'itembank.json').write_text(json.dumps({'theme': 'system'}))
        shutil.copytree(root, destination)
        metadata = dict(reading=reading_desk.href('synthetic', row), course='synthetic',
                        fingerprint=course.read_course(base)['fingerprint'])
        (destination / 'preview.json').write_text(json.dumps(metadata, indent=2))
        print(json.dumps(metadata))


if __name__ == '__main__':
    prepare(Path(sys.argv[1]))
