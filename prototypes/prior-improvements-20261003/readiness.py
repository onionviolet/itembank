#!/usr/bin/env python3
"""Read-only synthetic checks for the pending F3/F4 contracts."""
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
import model_adapter
import notes
import schema_validate
from surfaces import context_help


class ContractReadiness(unittest.TestCase):
    def test_source_context_overlay_is_closed_without_registering_it(self):
        node = json.loads(Path(__file__).with_name('source_question.schema.json').read_text())
        schema_validate.check_schema(node)
        payload = {'schema_version': 1, 'course_object_id': 'fictional-course',
                   'question': 'What does this invented rule mean?', 'attempt': 1,
                   'source_spans': [{'citation_id': 'S1', 'source_id': 'fictional-source',
                                     'locator_id': 'line-1', 'fingerprint': 'synthetic-accepted-revision',
                                     'text': 'The invented gate includes its opening and excludes its closing.'}],
                   'learner_notes': []}
        self.assertEqual(schema_validate.validate(payload, node), [])
        for changed in (dict(payload, permitted_tier=5), dict(payload, source_spans=[]),
                        dict(payload, question='x' * 2001), dict(payload, attempt=2)):
            self.assertTrue(schema_validate.validate(changed, node))
        before = copy.deepcopy(model_adapter._SCHEMA)
        overlay = copy.deepcopy(before)
        overlay['$defs']['request']['properties']['operation']['enum'].append('source_question')
        overlay['$defs']['payload']['properties']['context_request'] = node
        with patch.object(model_adapter, '_SCHEMA', overlay), \
                patch.object(model_adapter, '_PAYLOAD_KEYS', (*model_adapter._PAYLOAD_KEYS, 'context_request')):
            request = model_adapter.request_from_operation('source_question', 'synthetic-request-id', '', context_request=payload)
            self.assertEqual(schema_validate.validate(request, overlay), [])
            self.assertTrue(context_help.contract_ready())
            answer = {'schema_version': 1, 'answer': 'Opening is included; closing is excluded.',
                      'citations': [{'citation_id': 'S1', 'quote': 'includes its opening'}],
                      'uncertainty': 'This fictional example establishes no broader result.'}
            self.assertEqual(context_help.validate_candidate(answer, payload), answer)
            with self.assertRaises(ValueError):
                context_help.validate_candidate(dict(answer, citations=[{'citation_id': 'S1', 'quote': 'fabricated'}]), payload)
        self.assertEqual(model_adapter._SCHEMA, before)

    def test_proposed_provenance_preserves_original_bytes_and_rejects_scores(self):
        schema = json.loads(Path(__file__).with_name('submission_provenance.schema.json').read_text())
        schema_validate.check_schema(schema)
        text = '  Original fictional proof π\n'
        snapshot = {'schema_version': 1, 'origin_note_id': 'fictional-draft',
                    'origin_note_revision': 'fictional-revision',
                    'submitted_content_revision': notes.artifact_content_revision(text),
                    'item_revision': 'fictional-authored-item-revision',
                    'rubric_snapshot': ['Explain the fictional inclusive opening.'], 'artifact_kind': 'proof'}
        original = copy.deepcopy(snapshot)
        self.assertEqual(schema_validate.validate(snapshot, schema), [])
        self.assertNotEqual(snapshot['submitted_content_revision'], notes.artifact_content_revision(text.strip()))
        self.assertTrue(schema_validate.validate(dict(snapshot, score=True), schema))
        self.assertTrue(schema_validate.validate(dict(snapshot, rubric_snapshot=[{'pass': True}]), schema))
        self.assertEqual(snapshot, original)


if __name__ == '__main__':
    unittest.main()
