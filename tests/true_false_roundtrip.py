"""Explicit binary decisions retain ordinary MC scoring and private keys."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import model
import runtime
import schema_validate
from surfaces import session

TEXT = """Q1. The invented beacon is lit.
[FORMAT: true-false]
A) True
B) False
CORRECT: B
WHY BEST: The beacon is off.
KEY DISCRIMINATOR: Check its light.
SECOND-BEST: True would fit a lit beacon.
DISTRACTOR ANALYSIS:
- A) This would be correct if the beacon were lit.
- B) Correct for an unlit beacon.
TRAP: Guessing from its name.
CONFIDENCE: high
"""


class BinaryDecisions(unittest.TestCase):
    def test_explicit_format_lint_public_schema_and_original_scorer(self):
        q = model.parse_bank(TEXT)[0]
        self.assertEqual(q["stem"], "The invented beacon is lit.")
        self.assertEqual(model.lint([q])[0], [])
        self.assertTrue(runtime.score_response(q, "B"))
        self.assertFalse(runtime.score_response(q, "A"))
        public = runtime.public_item(q)
        self.assertEqual(public["answer_format"], "true-false")
        self.assertNotIn("correct", public)
        schema = json.loads((ROOT / "schemas/item.schema.json").read_text())
        self.assertEqual(schema_validate.validate(public, schema), [])
        ordinary = dict(q, answer_format="")
        self.assertIn("item.too_few_options", {e.code for e in model.lint([ordinary])[0]})
        del public["answer_format"]
        self.assertTrue(schema_validate.validate(public, schema))
        self.assertNotEqual(model.content_fingerprint(q), model.content_fingerprint(ordinary))

    def test_invalid_and_reversed_binary_declarations(self):
        q = model.parse_bank(TEXT)[0]
        for update, code in (({"answer_format": "unknown"}, "item.unknown_format"),
                             ({"type": "multi"}, "item.invalid_true_false"),
                             ({"opts": {"A": "Yes", "B": "No"}}, "item.invalid_true_false"),
                             ({"opts": {"A": "True", "B": "False", "C": "Maybe"}}, "item.invalid_true_false")):
            self.assertIn(code, {e.code for e in model.lint([dict(q, **update)])[0]})
        reverse = copy.deepcopy(q)
        reverse["opts"] = {"A": "False", "B": "True"}
        reverse["correct"] = ["A"]
        self.assertEqual(model.lint([reverse])[0], [])
        self.assertTrue(runtime.score_response(reverse, "A"))

    def test_real_formal_sitting_withholds_binary_outcome(self):
        with tempfile.TemporaryDirectory() as directory:
            bank = Path(directory) / "binary.md"
            bank.write_text(TEXT + "\n" + TEXT.replace("Q1.", "Q2.").replace(
                "The invented beacon is lit.", "The second fictional beacon is lit."))
            path = Path(directory) / "session.json"
            session.do_start(str(bank), {"count": 2, "seed": 1}, "exam", str(path), False)
            result = session.do_submit(str(path), "B", None)
            self.assertNotIn("score", result)
            self.assertEqual(result["next"]["item"]["answer_format"], "true-false")
            session.do_submit(str(path), "B", None)
            self.assertEqual(session.do_report(str(path))["summary"]["auto_correct"], 2)


if __name__ == "__main__":
    unittest.main()
