"""Production rational polynomial grammar, author acceptance and scorer boundaries."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import audit_writer
import authoring
import evidence
import model
import runtime
import schema_validate
from surfaces import session

VERSION = "a5-rational-polynomial-v2"


def field_fixture():
    spec = {"domain": "rational-polynomial", "checker_version": VERSION,
            "variable": "x", "required_form": "expanded", "target": "2*x+2",
            "diagnostics": [{"id": "distribution-omission", "answer": "2*x+1"},
                            {"id": "sign-error", "answer": "2*x-2"}]}
    tests = [{"input": raw, "state": state, "diagnostic_id": diagnostic,
              "checker_version": VERSION}
             for raw, state, diagnostic in (
                 ("2*x+2", "correct", None), ("2+2*x", "correct", None),
                 (".5*4*x+2", "correct", None), ("4/2*x+2.00", "correct", None),
                 ("2*(x+1)", "wrong_form", None),
                 ("2*x+1", "mathematically_wrong", "distribution-omission"),
                 ("2*(x-1)", "mathematically_wrong", "sign-error"),
                 ("3*x+2", "mathematically_wrong", None),
                 ("2x", "invalid", None), ("1/0", "invalid", None),
                 ("sin(x)", "unsupported", None), ("x^5", "unsupported", None))]
    return {"id": "expression", "label": "Expanded expression", "kind": "polynomial",
            "checker": spec, "checker_tests": tests}


def bank_fixture():
    return """Q1. Expand 2*(x+1), using explicit multiplication.
[TYPE: fill]
[OBJECTIVE: synthetic:polynomial]
[FIELDS: %s]
WHY BEST: Distribution applies to each term.
KEY DISCRIMINATOR: Both terms receive the scalar.
TRAP: Multiplying only the variable term.
CONFIDENCE: high
""" % json.dumps([field_fixture()])


def item_fixture():
    return model.parse_bank(bank_fixture())[0]


class PolynomialProductionTests(unittest.TestCase):
    def test_parser_lint_public_projection_and_exact_score(self):
        q = item_fixture()
        self.assertEqual(model.lint([q])[0], [])
        for raw in ("2+2*x", "4/2*x+2.00", ".5*4*x+2", "(2*x)+(2)"):
            self.assertTrue(runtime.score_response(q, {"expression": raw}))
        for raw in ("2*(x+1)", "2*x+1", "x*x"):
            self.assertFalse(runtime.score_response(q, {"expression": raw}))
        public = runtime.public_item(q)
        self.assertEqual(public["fields"][0]["checker"]["checker_version"], VERSION)
        rendered = json.dumps(public)
        for private in ('"target"', '"diagnostics"', '"checker_tests"', 'distribution-omission', 'sign-error'):
            self.assertNotIn(private, rendered)
        schema = json.loads((Path(__file__).resolve().parents[1] / "schemas/item.schema.json").read_text())
        self.assertEqual(schema_validate.validate(public, schema), [])

    def test_config_test_replay_overlap_and_fingerprint(self):
        original = item_fixture()
        for mutate in (lambda f: f["checker"].update(checker_version="future"),
                       lambda f: f["checker"].update(extra=1),
                       lambda f: f["checker"]["diagnostics"][0].update(answer="2+2*x"),
                       lambda f: f["checker"]["diagnostics"][1].update(answer="1+2*x"),
                       lambda f: f["checker_tests"][0].update(state="wrong_form"),
                       lambda f: f.update(checker_tests=[])):
            q = copy.deepcopy(original); mutate(q["fields"][0])
            self.assertTrue(runtime.fill_spec_errors(q))
            self.assertNotEqual(model.content_fingerprint(q), model.content_fingerprint(original))
            with self.assertRaises(runtime.PolynomialRefusal) as caught:
                runtime.score_response(q, {"expression": "2*x+2"})
            self.assertEqual(caught.exception.state, "unavailable")

    def test_refusals_do_not_become_false_or_pending(self):
        q = item_fixture()
        cases = (("2x", "invalid"), ("2..0", "invalid"), ("x**2", "unsupported"),
                 ("x^01", "unsupported"), ("x^2^2", "unsupported"),
                 ("1/x", "unsupported"), ("1000000+1-1", "unsupported"),
                 ("("*17 + "x" + ")"*17, "unsupported"),
                 ("x"*161, "unsupported"), ("２*x", "unsupported"))
        for raw, state in cases:
            with self.subTest(raw=raw):
                self.assertTrue(runtime.fill_response_error(q, {"expression": raw}))
                with self.assertRaises(runtime.PolynomialRefusal) as caught:
                    runtime.score_response(q, {"expression": raw})
                self.assertEqual(caught.exception.state, state)

    def test_form_is_in_response_identity_and_raw_evidence_is_preserved(self):
        q = item_fixture()
        a = {"expression": "2*(x+1)"}; b = {"expression": " 2*x+2 "}
        self.assertNotEqual(runtime.canonical_response(q, a), runtime.canonical_response(q, b))
        self.assertEqual(runtime.canonical_response(q, b), runtime.canonical_response(q, {"expression":"2+2*x"}))
        event = evidence.response_event("synthetic", q, b, True, "practice", 1, "synthetic.md")
        self.assertEqual(event["answer"], b)
        self.assertEqual(event["checker_outcomes"]["expression"]["checker_version"], VERSION)
        self.assertEqual(event["checker_outcomes"]["expression"]["state"], "correct")

    def test_exact_unary_and_expanded_rules(self):
        for raw, vector, form in (("-x^2", ["0","0","-1"], True),
                                  ("x+x+2", ["2","2"], True),
                                  ("2*3*x", ["0","6"], True),
                                  ("x*x", ["0","0","1"], False),
                                  ("-(x+1)", ["-1","-1"], False)):
            actual, expanded = runtime.polynomial_canonicalize(raw)
            self.assertEqual([str(v) for v in actual], vector)
            self.assertEqual(expanded, form)

    def test_internal_error_never_records_or_changes_a_real_session(self):
        q = item_fixture()
        with patch.object(runtime, "polynomial_validate_spec", side_effect=ArithmeticError("injected")):
            with self.assertRaises(runtime.PolynomialRefusal) as caught:
                runtime.score_response(q, {"expression": "2*x+2"})
            self.assertEqual(caught.exception.state, "error")
        with tempfile.TemporaryDirectory(prefix="itembank-poly-error-") as directory:
            root = Path(directory); bank = root / "synthetic.md"; bank.write_text(bank_fixture())
            path = root / "session.json"
            session.do_start(str(bank), {"count":1, "seed":1}, "practice", str(path), False)
            before = path.read_bytes(); log = evidence.log_path(str(root)); events = list(evidence.events(log))
            with patch.object(runtime, "polynomial_validate_spec", side_effect=ArithmeticError("injected")):
                with self.assertRaises(SystemExit):
                    session.do_submit(str(path), {"expression":"2*x+2"}, None)
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(list(evidence.events(log)), events)

    def test_diagnostic_identity_waits_for_hint_tier(self):
        outcome = runtime.polynomial_outcomes(item_fixture(), {"expression":"2*x+1"})
        self.assertNotIn("diagnostic_id", runtime.polynomial_feedback(outcome, 1)["expression"])
        self.assertEqual(runtime.polynomial_feedback(outcome, 2)["expression"]["diagnostic_id"],
                         "distribution-omission")

    def test_reviewed_authoring_accept_and_byte_exact_undo(self):
        text = bank_fixture(); q = item_fixture()
        citation = {"source_id":"synthetic", "fingerprint":"synthetic-v1", "span_id":"polynomial"}
        request = {"schema_version":authoring.AUTHORING_SCHEMA_VERSION,
                   "objectives":[q["objective"]], "count":1, "item_types":["fill"],
                   "citations":[citation], "mode":"draft_and_approve", "retry_cap":1}
        response = {"schema_version":authoring.AUTHORING_SCHEMA_VERSION,
                    "items":[{"objective":q["objective"], "type":"fill", "citations":[citation], "text":text}]}
        with tempfile.TemporaryDirectory(prefix="itembank-poly-author-") as directory:
            root=Path(directory); bank=root/"author.md"; before="# Synthetic author target\n"; bank.write_text(before)
            config={"target_path":str(bank), "state_dir":str(root/"state")}
            report=authoring.run_authoring(request, lambda _:response, before, audit_writer.write_units, config)
            self.assertEqual(report["status"], "awaiting_approval")
            self.assertEqual(bank.read_text(), before)
            bank.write_text(before + "Newer author bytes.\n")
            newer = bank.read_bytes()
            with self.assertRaises(audit_writer.WriterError):
                audit_writer.write_units(report["proposal"], str(bank), config["state_dir"],
                                         expected_fingerprint=authoring.bank_fingerprint(before))
            self.assertEqual(bank.read_bytes(), newer)
            bank.write_text(before)
            config["approved_write_ids"]=report["pending_write_ids"]
            accepted=authoring.run_authoring(request, lambda _:response, before, audit_writer.write_units, config)
            self.assertEqual(accepted["status"], "written")
            self.assertEqual(model.lint(model.load(str(bank)))[0], [])
            manifest=json.loads(next((root/"state"/"manifests").glob("*.json")).read_text())
            audit_writer.undo(manifest["write_id"], str(bank), config["state_dir"])
            self.assertEqual(bank.read_bytes(), before.encode())


if __name__ == "__main__":
    unittest.main()
