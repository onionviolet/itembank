#!/usr/bin/env python3
"""Opt-in inline fields preserve legacy scoring, raw input and keyed withholding."""
import copy
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import audit_writer
import authoring
import evidence
import model
import runtime
import schema_validate
from surfaces import daemon, quiz_page, session


def main():
    text = (ROOT / 'fixtures/a5_inline_fields.md').read_text()
    qs = model.parse_bank(text)
    assert len(qs) == 1 and not model.lint(qs)[0]
    q = qs[0]
    assert q['fill_layout'] == 'inline' and q['stem'].endswith('{{count}} stripes.')
    public = runtime.public_item(q)
    schema = json.loads((ROOT / 'schemas/item.schema.json').read_text())
    assert not schema_validate.validate(public, schema)
    assert 'accepted' not in json.dumps(public) and '2.5' not in json.dumps(public)
    invalid = ['The flag is {{color}}.', '{{color}} {{color}} {{count}}',
               '{{color}} {{unknown}}', '{{color}} {{count', '{{color}} {{count}} {{}}']
    for stem in invalid:
        bad = dict(q, stem=stem)
        assert runtime.fill_spec_errors(bad)
        try:
            runtime.public_item(bad)
            raise AssertionError('Malformed inline markers reached the surface')
        except ValueError:
            pass
    for layout, count in [('unknown', 1), ('inline', 2), ('', 1)]:
        assert runtime.fill_spec_errors(dict(q, fill_layout=layout, fill_layout_count=count))
    legacy = copy.deepcopy(q)
    legacy.pop('fill_layout'); legacy.pop('fill_layout_count')
    legacy['stem'] = '{{literal}} is legacy mathematical notation.'
    assert not runtime.fill_spec_errors(legacy)
    assert 'fill_layout' not in runtime.public_item(legacy)
    raw = {'color': '  BLUE  ', 'count': '5/2'}
    assert runtime.score_response(q, raw) is True and runtime.score_response(legacy, raw) is True
    native = quiz_page._form_controls(public, {'fill_color': ['  BLUE  '], 'fill_count': ['oops']})
    assert 'fill-inline' in native and '{{' not in native
    assert native.index('fill_color') < native.index('fill_count')
    assert '  BLUE  ' in native and 'oops' in native and 'type="number"' not in native
    assert daemon._form_answer(public, {'fill_color': ['  BLUE  '], 'fill_count': ['5/2']}) == raw
    with tempfile.TemporaryDirectory(prefix='a5-inline-') as directory:
        root = Path(directory)
        target = root / 'author.md'
        before = '# Synthetic approved author target\n'
        target.write_text(before)
        citation = dict(source_id='synthetic', fingerprint='synthetic-v1', span_id='flag')
        request = dict(schema_version=authoring.AUTHORING_SCHEMA_VERSION,
            objectives=['synthetic:inline-fields'], count=1, item_types=['fill'],
            citations=[citation], mode='draft_and_approve', retry_cap=1)
        response = dict(schema_version=authoring.AUTHORING_SCHEMA_VERSION, items=[dict(
            objective='synthetic:inline-fields', type='fill', citations=[citation], text=text[text.index('Q1.'):])])
        cfg = dict(target_path=str(target), state_dir=str(root / 'author-state'))
        proposed = authoring.run_authoring(request, lambda _: response, before, audit_writer.write_units, cfg)
        assert proposed['status'] == 'awaiting_approval' and target.read_text() == before
        assert 'FILL-LAYOUT' in proposed['proposal']['diff']
        cfg['approved_write_ids'] = proposed['pending_write_ids']
        accepted = authoring.run_authoring(request, lambda _: response, before, audit_writer.write_units, cfg)
        assert accepted['status'] == 'written'
        sitting = root / 'sitting.json'
        session.do_start(str(target), dict(count=1, seed=0), 'exam', str(sitting), False)
        initial = sitting.read_bytes()
        log = evidence.log_path(directory)
        events_before = Path(log).read_bytes()
        try:
            session.do_submit(str(sitting), json.dumps(dict(raw, count='oops')), None)
            raise AssertionError('Invalid numeric inline response was committed')
        except SystemExit:
            pass
        assert sitting.read_bytes() == initial and Path(log).read_bytes() == events_before
        result = session.do_submit(str(sitting), json.dumps(raw), None)
        assert result['action'] == 'defer_feedback' and 'score' not in result
        reopened = runtime.read_session(str(sitting))
        assert reopened['responses'][0]['answer'] == raw
        rows = [row for row in evidence.live_events(log) if row['event_type'] == 'response']
        assert len(rows) == 1 and rows[0]['answer'] == raw
    print('A5 inline fields: explicit grammar, marker refusal, legacy compatibility, escaped native order, reviewed authoring, invalid no-write and raw formal evidence pass')


if __name__ == '__main__':
    main()
