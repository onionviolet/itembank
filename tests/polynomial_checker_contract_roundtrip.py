"""Authored synthetic checker contract cases, no learner evidence or marks."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "polynomial_v2", ROOT / "prototypes/audit-question-families/polynomial_v2.py")
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)

# Private authored test table. Every row pins the checker revision; no row is
# exposed as a question or used to record learner correctness.
AUTHORED_CASES = [
    {"input": raw, "state": state, "diagnostic_id": diagnostic,
     "checker_version": checker.VERSION}
    for raw, state, diagnostic in (
        ("2*x+2", "correct", None),
        ("2+2*x", "correct", None),
        ("2.0*x+4/2", "correct", None),
        ("4/2*x+2.00", "correct", None),
        (".5*4*x+2", "correct", None),
        ("  2*x + 2\t", "correct", None),
        ("(2*x)+(2)", "correct", None),
        ("2*(x+1)", "wrong_form", None),
        ("(x+1)*2", "wrong_form", None),
        ("-( -2*x-2)", "wrong_form", None),
        ("2*x+1", "mathematically_wrong", "distribution-omission"),
        ("1+2*x", "mathematically_wrong", "distribution-omission"),
        ("2*x-2", "mathematically_wrong", "sign-error"),
        ("2*(x-1)", "mathematically_wrong", "sign-error"),
        ("3*x+2", "mathematically_wrong", None),
        ("2*(", "invalid", None),
        ("", "invalid", None),
        ("2x+2", "invalid", None),
        ("x x", "invalid", None),
        ("1/0", "invalid", None),
        ("1/", "invalid", None),
        ("x^", "invalid", None),
        ("2..0*x+2", "invalid", None),
        ("2*x+2\n", "invalid", None),
        ("sin(x)", "unsupported", None),
        ("1/x", "unsupported", None),
        ("x/2", "unsupported", None),
        ("1.0/2", "unsupported", None),
        ("x^-1", "unsupported", None),
        ("x^1.0", "unsupported", None),
        ("x^01", "unsupported", None),
        ("x^5", "unsupported", None),
        ("x^2^2", "unsupported", None),
        ("x**2", "unsupported", None),
        ("(x^4)*(x^4)", "unsupported", None),
        ("1000001*x", "unsupported", None),
        ("1/1000001*x", "unsupported", None),
        ("1000000+1-1", "unsupported", None),
        ("1000000000000", "unsupported", None),
        ("x" * 161, "unsupported", None),
        ("(" * 17 + "x" + ")" * 17, "unsupported", None),
        ("+".join(["x"] * 33), "unsupported", None),
        ("+".join(["x"] * 49), "unsupported", None),
        ("+".join(["x^4"] * 5), "unsupported", None),
        ("２*x+2", "unsupported", None),
        ("2×x+2", "unsupported", None),
        ("__import__('os')", "unsupported", None),
        ("1e2*x", "unsupported", None),
    )
]


class PolynomialContract(unittest.TestCase):
    def test_authored_table_and_preserved_originals(self):
        for case in AUTHORED_CASES:
            with self.subTest(raw=case["input"]):
                outcome = checker.analyze(case["input"])
                self.assertEqual(outcome["state"], case["state"])
                self.assertEqual(outcome.get("diagnostic_id"), case["diagnostic_id"])
                self.assertEqual(outcome["checker_version"], case["checker_version"])
                self.assertEqual(outcome["original"], case["input"])
                self.assertIsNone(outcome["settled_score"])
                if case["state"] in ("invalid", "unsupported"):
                    self.assertIsNone(outcome["runtime_comparison"])
        self.assertEqual(AUTHORED_CASES, json.loads(json.dumps(AUTHORED_CASES)))

    def test_exact_equivalence_and_syntax_form_are_separate(self):
        for left, right in (("(x+1)^2", "x^2+2*x+1"),
                            ("0.1*x+0.2*x", "3/10*x"),
                            ("-x^2", "-(x^2)"),
                            ("(-x)^2", "x^2")):
            self.assertEqual(checker.canonicalize(left)[0], checker.canonicalize(right)[0])
        for raw in ("x*x", "(x+1)^2", "-(x+1)", "2^2", "0*(x+1)"):
            self.assertFalse(checker.canonicalize(raw)[1], raw)
        for raw in ("x^2+2*x+1", "-2*x^2+3", "2*3*x", "x^0", "-(2*x)"):
            self.assertTrue(checker.canonicalize(raw)[1], raw)
        # Unsimplified additive sums remain expanded under the declared AST rule.
        self.assertTrue(checker.canonicalize("x+x+2")[1])

    def test_private_spec_validation_and_overlap_rejection(self):
        for target in ("2*(x+1)", "2*(", "sin(x)", "x^5", None):
            spec = copy.deepcopy(checker.DEFAULT_SPEC)
            spec["target"] = target
            self.assertEqual(checker.analyze("2*x+2", spec)["state"], "unavailable")
        for key, value in (("variable", "y"), ("checker_version", "future"),
                           ("required_form", "factored"), ("diagnostics", [None])):
            spec = copy.deepcopy(checker.DEFAULT_SPEC)
            spec[key] = value
            self.assertEqual(checker.analyze("2*x+2", spec)["state"], "unavailable")
        for answer, rule_id in (("1+2*x", "other"), ("2*x+2", "other"),
                               ("2*x-2", "distribution-omission")):
            spec = copy.deepcopy(checker.DEFAULT_SPEC)
            spec["diagnostics"][1] = {"id": rule_id, "answer": answer}
            self.assertEqual(checker.analyze("2*x+1", spec)["state"], "unavailable")
        spec = copy.deepcopy(checker.DEFAULT_SPEC)
        spec["diagnostics"].reverse()
        for raw in ("2*x+1", "2*x-2", "2*x+2"):
            self.assertEqual(checker.analyze(raw), checker.analyze(raw, spec))

    def test_disclosure_is_runtime_gated_and_wrong_session_fails_closed(self):
        for mode in ("exam", "diagnostic"):
            for raw in ("2*x+1", "2*x+2", "2*(x+1)"):
                for session in (None, {"mode": mode, "status": "active"},
                                {"mode": "practice", "status": "complete"}):
                    result = checker.analyze(raw, mode=mode, session=session)
                    self.assertEqual(result["state"], "withheld")
                    self.assertIsNone(result["runtime_comparison"])
                    self.assertNotIn("diagnostic_id", result)
                    self.assertNotIn("target", result)
                released = checker.analyze(raw, mode=mode,
                                           session={"mode": mode, "status": "complete"})
                self.assertNotEqual(released["state"], "withheld")
        self.assertEqual(checker.analyze("2*x+1", mode="unknown")["state"], "unavailable")

    def test_runtime_comparison_and_failures_never_settle_scores(self):
        with patch.object(checker.runtime, "score_response", wraps=checker.runtime.score_response) as scorer:
            result = checker.analyze("2*x+2")
            self.assertEqual(result["state"], "correct")
            self.assertGreater(scorer.call_count, 0)
            self.assertTrue(all(call.args[0]["type"] == "fill" for call in scorer.call_args_list))
        for raw in ("2*x+2", "2*x+1", "1/x"):
            result = checker.analyze(raw, fail=True)
            self.assertEqual(result["state"], "error")
            self.assertEqual(result["original"], raw)
            self.assertIsNone(result["runtime_comparison"])
            self.assertIsNone(result["settled_score"])
        with patch.object(checker.runtime, "score_response", side_effect=RuntimeError("injected")):
            self.assertEqual(checker.analyze("2*x+2")["state"], "error")

    def test_refusal_precedence_and_no_file_writes(self):
        spec = copy.deepcopy(checker.DEFAULT_SPEC)
        spec["target"] = "bad"
        self.assertEqual(checker.analyze("1/0", spec)["state"], "unavailable")
        # Lexical unsupported precedes later malformed-grammar analysis.
        self.assertEqual(checker.analyze("2*(sin(x)")["state"], "unsupported")
        with patch("builtins.open", side_effect=AssertionError("Unexpected file access")), \
                patch.object(Path, "open", side_effect=AssertionError("Unexpected path access")):
            for case in AUTHORED_CASES:
                checker.analyze(case["input"])
        source = (ROOT / "prototypes/audit-question-families/polynomial_v2.py").read_text()
        self.assertNotIn("eval(", source)
        self.assertNotIn("random", source)
        self.assertNotIn("write_text", source)


if __name__ == "__main__":
    print("Authored synthetic cases:", len(AUTHORED_CASES), flush=True)
    unittest.main(verbosity=2)
