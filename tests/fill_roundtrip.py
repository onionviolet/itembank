#!/usr/bin/env python3
"""Typed answers preserve exact data, assessment authority, and evidence."""
import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import evidence
import authoring
import model
import runtime
import schema_validate

FIXTURE = ROOT / "fixtures" / "fill_bank.md"


class FillContract(unittest.TestCase):
    def setUp(self):
        self.items = model.load(str(FIXTURE))

    def test_authoring_request_accepts_fill(self):
        request = {"schema_version": 1, "objectives": ["sample:description"],
                   "count": 1, "item_types": ["fill"], "retry_cap": 1,
                   "mode": "report_only", "citations": [{
                       "source_id": "synthetic", "span_id": "one",
                       "fingerprint": "0" * 64}]}
        self.assertEqual(authoring.validate_request(request), [])
        schema = json.loads((ROOT / "schemas/authoring_request.schema.json").read_text())
        self.assertEqual(schema_validate.validate(request, schema), [])

    def test_parser_lint_and_fingerprint(self):
        self.assertEqual(len(self.items), 3)
        self.assertEqual(model.lint(self.items)[0], [])
        raw = FIXTURE.read_text()
        for bad in ('[FIELDS: broken]', '[FIELDS: {}]', '[FIELDS: []]',
                    '[FIELDS: [{"id":"x","id":"y"}]]'):
            import re
            damaged = re.sub(r"(?m)^\[FIELDS:.*$", lambda _: bad, raw)
            parsed = model.parse_bank(damaged)
            self.assertEqual(len(parsed), 3)
            self.assertIn("item.fill_invalid", [e.code for e in model.lint(parsed)[0]])
        q = self.items[1]
        original = model.content_fingerprint(q)
        for key, value in (("answer", "2"), ("atol", "0.1"), ("rtol", ".1"),
                           ("units", {"m": "1", "cm": ".02"}), ("label", "New")):
            changed = copy.deepcopy(q)
            changed["fields"][0][key] = value
            self.assertNotEqual(model.content_fingerprint(changed), original)

    def test_mixed_bank_reports_actual_scoring_capability(self):
        # Visual and fill compare structured responses without a string normalizer.
        # Adding a check item must not mislabel those types as pending.
        items = self.items + model.load(str(ROOT / "fixtures" / "check_bank.md"))
        items += model.load(str(ROOT / "fixtures" / "visual_bank.md"))
        items += model.parse_bank("Q91. Synthetic prose.\n[TYPE: short]\n")
        warnings = [w for w in model.lint(items)[1] if w.code == "item.no_normalizer"]
        self.assertEqual(len(warnings), 1)
        self.assertIn("short items", str(warnings[0]))
        self.assertTrue(runtime.supports_auto_score("visual"))
        self.assertTrue(runtime.supports_auto_score("fill"))
        self.assertFalse(runtime.supports_auto_score("short"))

    def test_text_rules_and_multiple_fields(self):
        q = self.items[0]
        self.assertTrue(runtime.score_response(q, {"color": " BLUE ", "count": "5/2"}))
        self.assertTrue(runtime.score_response(q, {"color": "azure", "count": "2.51"}))
        self.assertFalse(runtime.score_response(q, {"color": "not blue", "count": "2.5"}))
        self.assertFalse(runtime.score_response(q, {"color": "blue", "count": "2.5101"}))
        self.assertEqual(runtime.canonical_response(q, {"color": "BLUE", "count": "2.5"}),
                         runtime.canonical_response(q, {"color": " blue ", "count": "5/2"}))
        accented = self.items[2]
        self.assertTrue(runtime.score_response(accented, {"name": "cafe\u0301"}))
        for wrong in ("cafe", "Café", " café", "café "):
            self.assertFalse(runtime.score_response(accented, {"name": wrong}))
        field = accented["fields"][0]
        field.update(accepted=["two words"], whitespace="collapse", case_sensitive=False)
        self.assertTrue(runtime.score_response(accented, {"name": " TWO   words "}))
        for control in ("\n", "\r", "\t", "\x00", "\x85", "\u2028", "\u2029", "\ud800"):
            value = "two" + control + "words"
            self.assertTrue(runtime.fill_response_error(accented, {"name": value}))
            changed = copy.deepcopy(accented)
            changed["fields"][0]["accepted"] = [value]
            self.assertTrue(runtime.fill_spec_errors(changed))
            changed = copy.deepcopy(accented)
            changed["fields"][0]["label"] = value
            self.assertTrue(runtime.fill_spec_errors(changed))
        field["accepted"] = ["two words", "TWO WORDS"]
        self.assertTrue(runtime.fill_spec_errors(accented))

    def test_numeric_and_unit_boundaries(self):
        q = self.items[1]
        for value in ("1 m", "100 cm", "1e2 cm", "200/2 cm"):
            self.assertTrue(runtime.score_response(q, {"length": value}), value)
        self.assertFalse(runtime.score_response(q, {"length": "1 cm"}))
        self.assertEqual(runtime.canonical_response(q, {"length": "100 cm"}),
                         runtime.canonical_response(q, {"length": "1 m"}))
        for value in ("", "1", "1 kg", "NaN m", "Infinity m", "1/0 m", "1e999 m",
                      "1,0 m", "1+0 m", "1m", "9" * 129 + " m"):
            self.assertTrue(runtime.fill_response_error(q, {"length": value}), value)
        field = q["fields"][0]
        field.update(answer="-10", atol="0.5", rtol="0.1")
        self.assertTrue(runtime.score_response(q, {"length": "-9 m"}))
        self.assertFalse(runtime.score_response(q, {"length": "-8.99 m"}))
        field.update(answer="0", atol="0", rtol="1")
        self.assertFalse(runtime.score_response(q, {"length": ".001 m"}))
        for invalid in ({"unit": "mm"}, {"atol": "-1"}, {"rtol": "NaN"},
                        {"units": {"m": "2"}}, {"units": {"m": "1", "cm": "0"}},
                        {"unknown": 1}):
            changed = copy.deepcopy(q)
            changed["fields"][0].update(invalid)
            self.assertTrue(runtime.fill_spec_errors(changed), invalid)

    def test_invalid_response_and_public_projection(self):
        q = self.items[0]
        for answer in ({}, [], None, {"color": "blue"}, {"color": "blue", "count": 2.5},
                       {"color": "blue", "count": "2.5", "extra": "x"}):
            self.assertTrue(runtime.fill_response_error(q, answer))
            self.assertFalse(runtime.score_response(q, answer))
            self.assertEqual(runtime.canonical_response(q, answer), "")
        schema = json.loads((ROOT / "schemas" / "item.schema.json").read_text())
        for item in self.items:
            public = runtime.public_item(item)
            self.assertEqual(schema_validate.validate(public, schema), [])
            wire = json.dumps(public)
            for private in ('"accepted"', '"answer"', '"atol"', '"rtol"', '"scales"'):
                self.assertNotIn(private, wire)
            forged = copy.deepcopy(public)
            forged["fields"][0]["accepted"] = ["leak"]
            self.assertTrue(schema_validate.validate(forged, schema))
            offline = runtime.page_item(item, offline=True)
            self.assertTrue(offline["served_required"])
            self.assertNotIn("key", offline)
            self.assertNotIn("explain", offline)
        self.assertFalse(runtime.glossable([q], {"def": "The answer is azure."}))
        self.assertFalse(runtime.glossable([self.items[1]], {"def": "The answer is 1."}))
        self.assertIn("Rod length: 100 cm",
                      runtime.response_text(self.items[1], {"length": "100 cm"}))

    def test_glossary_uses_text_equivalence_and_withholds_numeric_definitions(self):
        text = copy.deepcopy(self.items[2])
        self.assertFalse(runtime.glossable([text], {"def": "The name is cafe\u0301."}))
        self.assertTrue(runtime.glossable([text], {"def": "A fictional place name."}))
        text["fields"][0].update(accepted=["Straße"], case_sensitive=False)
        self.assertFalse(runtime.glossable([text], {"def": "The answer is STRASSE."}))
        quantity = copy.deepcopy(self.items[1])
        quantity["fields"][0]["answer"] = "0.5"
        self.assertTrue(runtime.score_response(quantity, {"length": "50 cm"}))
        for definition in ("The answer is 50 cm.", "Use 1/2 m.", "An unrelated word."):
            self.assertFalse(runtime.glossable([quantity], {"def": definition}))

    def test_cli_evidence_and_malformed_refusal(self):
        def run(*args, ok=True):
            result = subprocess.run([sys.executable, str(ROOT / "itembank.py"),
                                     *map(str, args)], cwd=ROOT, text=True,
                                    capture_output=True)
            if ok:
                self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
                return json.loads(result.stdout)
            self.assertNotEqual(result.returncode, 0)
            return result
        answers = {"q1": {"color": " BLUE ", "count": "5/2"},
                   "q2": {"length": "100 cm"}, "q3": {"name": "cafe\u0301"}}
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            bank, session = base / "fill.md", base / "session.json"
            shutil.copyfile(FIXTURE, bank)
            view = run("start", bank, "--count", "3", "--mode", "exam",
                       "--out", session)
            before = session.read_bytes()
            before_events = list(evidence.live_events(evidence.log_path(folder)))
            run("submit", session, "--answer", "{}", ok=False)
            self.assertEqual(session.read_bytes(), before)
            self.assertEqual(list(evidence.live_events(evidence.log_path(folder))), before_events)
            while view["status"] == "active":
                response = answers[view["item"]["id"]]
                result = run("submit", session, "--answer", json.dumps(response))
                self.assertNotIn("score", result)
                self.assertNotIn("explain", result)
                view = result["next"]
            events = list(evidence.live_events(evidence.log_path(folder)))
            responses = [row for row in events if row["event_type"] == "response"]
            self.assertEqual(len(responses), 3)
            self.assertTrue(all(row["score"] is True for row in responses))
            self.assertIn({"color": " BLUE ", "count": "5/2"},
                          [row["answer"] for row in responses])
            session_schema = json.loads((ROOT / "schemas/session.schema.json").read_text())
            self.assertEqual(schema_validate.validate(json.loads(session.read_text()), session_schema), [])
            response_schema = json.loads((ROOT / "schemas/response.schema.json").read_text())
            for row in responses:
                self.assertEqual(schema_validate.validate(row, response_schema), [])


if __name__ == "__main__":
    unittest.main()
