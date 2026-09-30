#!/usr/bin/env python3
"""Native exact context selection, quote-note recovery and assessment refusal."""
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import course
import course_package
import graph
import identity
import journal
import notes
import reading_desk
import source_adapters
from surfaces import research_context


def fixture(root):
    base = root / 'synthetic'
    base.mkdir()
    course.create_course(str(base), 'Synthetic research', 'human', 'test')
    refs = []
    for name, text in [('duplicate.md', 'First context\nSame sentence.\nSecond context\nSame sentence.\n'),
                       ('excluded.md', 'EXCLUDED SENTINEL\n'),
                       ('assessment.md', (ROOT / 'fixtures/sample_bank.md').read_text())]:
        (base / name).write_text(text)
        grants = {operation: 'granted' for operation in identity.RIGHTS_OPERATIONS}
        linked = journal.op_link(str(base), 'source', name, 'human', 'test', rights=grants)
        imported = source_adapters.import_source(str(base), 'markdown', linked['object_id'], 'human', 'test')
        sidecar = json.loads((base / imported['sidecar_rel_path']).read_text())
        ref = {'source_id': imported['source_id'], 'fingerprint': sidecar['fingerprint'],
               'locator_id': 'L4' if name == 'duplicate.md' else sidecar['locators'][0]['id']}
        refs.append(ref)
        read = course.read_course(str(base))
        graph.add_source(read['doc'], ref['source_id'], name)
        course.write_course(str(base), read['doc'], read['fingerprint'], 'human', 'test')
    return str(base), refs


def fields(ref, operation, **extra):
    return dict(source=[json.dumps({key: ref[key] for key in ('source_id', 'fingerprint')})],
                locator=[ref['locator_id']], operation=[operation], **{key: [value] for key, value in extra.items()})


def main():
    with tempfile.TemporaryDirectory(prefix='a5-research-') as directory:
        root = Path(directory)
        base, refs = fixture(root)
        cid = course.read_course(base)['object_id']
        initial = research_context.panel(base)
        assert 'Exact locator ID' in initial and 'name="confirm"' in initial
        preview = research_context.apply(base, fields(refs[0], 'preview'))
        assert preview['passage']['origin']['line'] == 4
        assert not Path(base, '_notes').exists() and not Path(base, '_research').exists()
        canceled = research_context.apply(base, fields(refs[0], 'copy'))
        assert canceled['status'] == 'canceled' and not Path(base, '_notes').exists()
        linked = research_context.apply(base, fields(refs[0], 'link', confirm='yes'))
        private = reading_desk.note_root(base)
        linked_document = notes.read_note_document(private, cid)
        assert 'Same sentence.' not in linked_document['markdown']
        copied = research_context.apply(base, fields(refs[0], 'copy', confirm='yes',
            expected_notes_fingerprint=linked['document']['fingerprint']))
        copied_document = notes.read_note_document(private, cid)
        assert copied['status'] == 'draft' and 'Same sentence.' in copied_document['markdown']
        markup = research_context.panel(base, copied)
        assert 'Exact source preview' in markup and 'Undo latest private-note change' in markup
        selected = dict(operation=['save_scope'], reference=[json.dumps(refs[0])],
                        note_id=[copied['note']['note_id']],
                        expected_notes_fingerprint=[copied['document']['fingerprint']], confirm=['yes'])
        assert research_context.apply(base, selected)['status'] == 'saved'
        requested = research_context.apply(base, {'operation': ['request_context']})
        assert requested['sources'][0]['origin']['line'] == 4
        assert requested['notes'][0]['kind'] == 'learner_note'
        assert requested['excluded_sources'] == 2 and requested['egress'] == 'none'
        assert 'EXCLUDED SENTINEL' not in research_context.panel(base, requested)
        try:
            research_context.apply(base, fields(refs[2], 'preview'))
            raise AssertionError('Assessment source disclosed through research preview')
        except ValueError as exc:
            assert 'runtime' in str(exc)
        package = str(root / 'package')
        dest = str(root / 'restored')
        course_package.export_package(base, base, package, include_private_notes=True,
                                      include_private_note_history=True)
        manifest = json.loads(Path(package, course_package.MANIFEST_FILENAME).read_text())
        assert any(row['target'] == '_research/research-scope.json' for row in manifest['loss_report'])
        Path(dest).mkdir()
        restored = course_package.restore_package(package, dest, 'human', 'test')
        assert restored['restore_losses'] == []
        document = notes.read_note_document(reading_desk.note_root(dest), cid)
        assert document == copied_document
        returned = notes.resolve_source_note(dest, document['sidecar']['notes'][-1])
        assert returned[0]['status'] == 'ok' and returned[0]['origin']['line'] == 4
        assert not Path(dest, '_research').exists()
        entry = [row for row in journal.entries(private) if row['state'] == 'applied'][-1]
        research_context.apply(base, {'operation': ['undo_note'], 'entry_id': [entry['entry_id']]})
        assert notes.read_note_document(private, cid) == linked_document
        before = Path(base, '_research/research-scope.json').read_bytes()
        try:
            research_context.apply(base, selected)
            raise AssertionError('Stale note/scope selection accepted')
        except ValueError:
            pass
        assert Path(base, '_research/research-scope.json').read_bytes() == before
    print('A5 native context: exact occurrence, explicit inclusion, cancel, link/copy, no assessment disclosure, clean note restore, named scope loss and undo pass')


if __name__ == '__main__':
    main()
