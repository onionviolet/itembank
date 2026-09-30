#!/usr/bin/env python3
"""Structural ordering gate controls and all shared recorder refusals."""
import json
from pathlib import Path
import runpy
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import evidence
import model
import runtime
import schema_validate
from surfaces import daemon, lesson, quiz


def main():
    text = runpy.run_path(str(ROOT / 'tests/ordering_workflow_roundtrip.py'))['authored_text']()
    qs = model.parse_bank(text)
    q = qs[1]
    with tempfile.TemporaryDirectory(prefix='itembank-order-gate-') as directory:
        root = Path(directory)
        bank = root / 'gate.md'
        bank.write_text(text)
        log = evidence.log_path(directory)
        markup = lesson._gate_check_answer(q)
        assert 'value="start"' in markup and 'Independent task (left)' in markup
        fields = dict(step_0=['start'], step_1=[''], step_2=['right'], step_3=['left'])
        assert daemon._gate_answer_from_form(q, fields) == ['start','right','left']
        for invalid in (['start','start'], ['foreign'], {'start':'left'}):
            for recorder in ('gate', 'serve'):
                before = Path(log).read_bytes() if Path(log).exists() else None
                try:
                    if recorder == 'gate':
                        quiz.record_gate_check(str(bank), q['id'], invalid)
                    else:
                        quiz.record_answer(str(bank), qs, 'synthetic', log,
                                           str(root/'attempt.md'), 'practice', q, invalid, 0)
                    raise AssertionError('Invalid structural response recorded')
                except SystemExit as exc:
                    assert str(exc) == runtime.ordering_response_error(q, invalid)
                assert (Path(log).read_bytes() if Path(log).exists() else None) == before
        assert quiz.record_gate_check(str(bank), q['id'], ['start','right','left']) is True
        events = list(evidence.live_events(log))
        assert len(events) == 1
        event = events[0]
        assert event['context'] == 'lesson_gate'
        assert event['answer'] == ['start','right','left'] and event['checker_version'] == 1
        schema = json.loads((ROOT/'schemas/response.schema.json').read_text())
        assert not schema_validate.validate(event, schema)
    print('Ordering gates: stable-ID native controls, form compaction, gate/serve refusal without evidence and versioned raw response schema pass')


if __name__ == '__main__':
    main()
