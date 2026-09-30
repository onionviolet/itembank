#!/usr/bin/env python3
"""Reviewed structural-order authoring, stale-write refusal and exact undo."""
from pathlib import Path
import re
import runpy
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import audit_writer
import authoring
import model
import runtime
from surfaces import quiz_page


def main():
    text = runpy.run_path(str(ROOT / 'tests/ordering_workflow_roundtrip.py'))['authored_text']()
    questions = model.parse_bank(text)
    assert len(questions) == 2
    blocks = re.split(r'(?m)(?=^Q\d+\.)', text)[1:]
    citation = dict(source_id='synthetic', fingerprint='synthetic-v1', span_id='ordering')
    request = dict(schema_version=authoring.AUTHORING_SCHEMA_VERSION,
                   objectives=[q['objective'] for q in questions], count=2,
                   item_types=['build'], citations=[citation],
                   mode='draft_and_approve', retry_cap=1)
    response = dict(schema_version=authoring.AUTHORING_SCHEMA_VERSION, items=[
        dict(objective=q['objective'], type='build', citations=[citation], text=block)
        for q, block in zip(questions, blocks)])
    with tempfile.TemporaryDirectory(prefix='itembank-order-author-') as directory:
        root = Path(directory)
        bank = root / 'author.md'
        before = '# Synthetic author target\n'
        bank.write_text(before)
        config = dict(target_path=str(bank), state_dir=str(root / 'state'))
        report = authoring.run_authoring(request, lambda _: response, before,
                                        audit_writer.write_units, config)
        assert report['status'] == 'awaiting_approval', report
        assert bank.read_text() == before
        assert '[ORDERING:' in report['proposal']['diff']
        for q in questions:
            public = runtime.public_item(q)
            markup = quiz_page._form_controls(public, {})
            assert all(block['id'] in markup for block in public['blocks'])
            assert 'required' not in public['ordering']
            assert 'dependencies' not in public['ordering']
        # A reviewed proposal cannot overwrite a newer author's bytes.
        bank.write_text(before + '\nNewer author wording.\n')
        stale = bank.read_bytes()
        try:
            audit_writer.write_units(report['proposal'], str(bank), config['state_dir'],
                                     expected_fingerprint=authoring.bank_fingerprint(before))
            raise AssertionError('Stale proposal overwrote newer content')
        except audit_writer.WriterError as exc:
            assert 'stale' in exc.code or 'fingerprint' in str(exc), exc
        assert bank.read_bytes() == stale
        bank.write_text(before)
        config['approved_write_ids'] = report['pending_write_ids']
        accepted = authoring.run_authoring(request, lambda _: response, before,
                                          audit_writer.write_units, config)
        assert accepted['status'] == 'written', accepted
        after = bank.read_bytes()
        parsed = model.parse_bank(after.decode())
        errors, _ = model.lint(parsed)
        assert not errors, errors
        assert all(q['ordering']['version'] == 1 for q in parsed)
        manifests = list((root / 'state' / 'manifests').glob('*.json'))
        assert len(manifests) == 1, manifests
        import json
        manifest = json.loads(manifests[0].read_text())
        bank.write_bytes(after + b'\nNewer author wording.\n')
        newer = bank.read_bytes()
        try:
            audit_writer.undo(manifest['write_id'], str(bank), config['state_dir'])
            raise AssertionError('Undo overwrote newer content')
        except audit_writer.WriterError as exc:
            assert exc.code == 'undo.stale_target', exc
        assert bank.read_bytes() == newer
        bank.write_bytes(after)
        undone = audit_writer.undo(manifest['write_id'], str(bank), config['state_dir'])
        assert undone['status'] == 'reverted', undone
        assert bank.read_bytes() == before.encode()
    print('Ordering authoring: cited proposal, lint, plain/native preview, exact approval, stale write/undo refusal and byte-exact undo pass')


if __name__ == '__main__':
    main()
