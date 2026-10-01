"""Independent synthetic domain mechanisms, not production-format acceptance."""
import copy
from fractions import Fraction as F
import itertools
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import question_domains as domains
import runtime


def specification(domain, target, diagnostics=()):
    value = domains.canonicalize(target, domain, runtime.fill_number)
    shape = ([len(value)] if domain == "rational-vector" else
             [len(value), len(value[0])] if domain == "rational-matrix" else None)
    return {"domain": domain, "checker_version": domains.VERSION,
            "target": target, "diagnostics": list(diagnostics), "shape": shape,
            "orientation": "column" if domain == "rational-vector" else None}


def runtime_compare(left, right):
    # Existing runtime text-fill authority compares serialized exact operands.
    # This is a synthetic mechanism harness, not a new accepted fill domain.
    encoded = lambda value: json.dumps(value, default=str, separators=(",", ":"))
    q = {"type": "fill", "fields": [{"id": "value", "label": "Value",
                                      "kind": "text", "accepted": [encoded(right)]}]}
    return runtime.score_response(q, {"value": encoded(left)})


def runtime_analyze(raw, spec):
    operands = domains.prepare_comparison(raw, spec, runtime.fill_number)
    correct = runtime_compare(operands.response, operands.target)
    result = {"state": "correct" if correct else "mathematically_wrong"}
    if not correct:
        for name, target in operands.diagnostics:
            if runtime_compare(operands.response, target):
                result["diagnostic_id"] = name
                break
    return result


def authored_cases(spec, wrong, invalid, unsupported):
    rows = [(spec["target"], "correct", None), (wrong, "mathematically_wrong", None),
            (invalid, "invalid", None), (unsupported, "unsupported", None)]
    rows += [(rule["answer"], "mathematically_wrong", rule["id"]) for rule in spec["diagnostics"]]
    return [{"input": raw, "state": state, "diagnostic_id": diagnostic,
             "checker_version": domains.VERSION} for raw, state, diagnostic in rows]


class ExactDomainTests(unittest.TestCase):
    def canon(self, raw, domain):
        return domains.canonicalize(raw, domain, runtime.fill_number)

    def refuse(self, state, operation, *args):
        with self.assertRaises(domains.DomainRefusal) as caught:
            operation(*args)
        self.assertEqual(caught.exception.state, state)

    def test_rational_set_order_duplicates_empty_and_exact_boundaries(self):
        for raw in ("{1/2,1,-2}", "{-2.00,0.5,1e0}", "{1,1/2,-2,0.50,1}"):
            self.assertEqual(self.canon(raw, "rational-set"), (F(-2), F(1, 2), F(1)))
        self.assertEqual(self.canon("{}", "rational-set"), ())
        self.assertEqual(self.canon("{  }", "rational-set"), ())
        self.assertEqual(self.canon("{1/1000000,-1000000,1000000}", "rational-set"),
                         (F(-1000000), F(1, 1000000), F(1000000)))
        self.assertEqual(len(self.canon("{" + ",".join(map(str, range(32))) + "}", "rational-set")), 32)
        for raw in ("{1000001}", "{1/1000001}", "{1e-7}", "{" + ",".join(["1"] * 33) + "}"):
            self.refuse("unsupported", self.canon, raw, "rational-set")
        for raw in ("", "{1,}", "{,}", "{1/0}", "{1/}", "{1", "[1]", "{1+2}"):
            self.refuse("invalid", self.canon, raw, "rational-set")
        for raw in ("{x}", "{1 m}", "{inf}", "{{1}}", "{２}", "{sqrt(2)}"):
            self.refuse("unsupported", self.canon, raw, "rational-set")

    def test_interval_equivalence_empty_infinity_and_endpoint_closure(self):
        equivalent = [
            ("[0,1] U (1,2)", "[0,2)"),
            ("(0,1) U [1,2]", "(0,2]"),
            ("[0,0] U (0,1)", "[0,1)"),
            ("(0,1) U [0,0] U [1,1]", "[0,1]"),
            ("[0,3] U (1,2) U [0,3]", "[0,3]"),
            ("[1,2] U [0,1]", "[0,2]"),
            ("(-inf,0) U [0,inf)", "(-inf,inf)"),
            ("[.5,1e0]", "[1/2,1]"),
            ("(1,1)", "empty"), ("[1,1)", "empty"), ("(1,1]", "empty"),
        ]
        for left, right in equivalent:
            self.assertEqual(self.canon(left, "rational-interval-set"), self.canon(right, "rational-interval-set"), (left, right))
        for left, right in (("(0,1) U (1,2)", "(0,2)"),
                            ("[0,1)", "[0,1]"), ("[1,1]", "empty"),
                            ("(-inf,0)", "(-inf,0]")):
            self.assertNotEqual(self.canon(left, "rational-interval-set"), self.canon(right, "rational-interval-set"))
        for raw in ("[1,0]", "[inf,inf]", "[-inf,1]", "[0,inf]", "[0,1] U", "[0,1,2]", "()", "[0 1]"):
            self.refuse("invalid", self.canon, raw, "rational-interval-set")
        self.refuse("unsupported", self.canon, "[0,sqrt(2)]", "rational-interval-set")
        self.assertEqual(self.canon(" U ".join(["[0,1]"] * 8), "rational-interval-set"), self.canon("[0,1]", "rational-interval-set"))
        self.refuse("unsupported", self.canon, " U ".join(["[0,1]"] * 9), "rational-interval-set")

    def test_interval_union_independent_membership_oracle(self):
        # Oracle uses elementary set membership, not the merge algorithm. Test
        # every ordered endpoint pair and closure combination, including empty
        # pieces, across all two-piece unions at endpoints and between them.
        pieces = [(a, b, lc, hc) for a in (-1, 0, 1) for b in (-1, 0, 1)
                  if a <= b for lc in (False, True) for hc in (False, True)]
        points = [F(n, 2) for n in range(-3, 4)]
        def render(p):
            a, b, lc, hc = p
            return ("[" if lc else "(") + str(a) + "," + str(b) + ("]" if hc else ")")
        def belongs(x, p):
            a, b, lc, hc = p
            return (a < x or (a == x and lc)) and (x < b or (x == b and hc))
        for left, right in itertools.product(pieces, repeat=2):
            raw = render(left) + " U " + render(right)
            normalized = self.canon(raw, "rational-interval-set")
            # Normalized pieces must be ordered, nonempty and unmergeable.
            for a, b in zip(normalized, normalized[1:]):
                self.assertTrue(a[1] < b[0] or (a[1] == b[0] and not a[3] and not b[2]))
            for point in points:
                expected = belongs(point, left) or belongs(point, right)
                actual = any(belongs(point, (a[1], b[1], lc, hc)) for a, b, lc, hc in normalized)
                self.assertEqual(actual, expected, (raw, point))

    def test_vector_and_matrix_order_shape_and_exact_values(self):
        self.assertEqual(self.canon("[.5,-2e0,3/2]", "rational-vector"), (F(1, 2), F(-2), F(3, 2)))
        self.assertEqual(self.canon("[[.5,-2e0],[3/2,0]]", "rational-matrix"),
                         ((F(1, 2), F(-2)), (F(3, 2), F(0))))
        self.assertNotEqual(self.canon("[1,2]", "rational-vector"), self.canon("[2,1]", "rational-vector"))
        self.assertNotEqual(self.canon("[[1,2],[3,4]]", "rational-matrix"), self.canon("[[1,3],[2,4]]", "rational-matrix"))
        for domain, raws in (("rational-vector", ("[]", "[1,]", "1,2", "[1/0]")),
                             ("rational-matrix", ("[]", "[[]]", "[[1],[2,3]]", "[[1],]", "[[1] [2]]", "[1,2]"))):
            for raw in raws:
                self.refuse("invalid", self.canon, raw, domain)
        for domain, raw in (("rational-vector", "[1,2,3,4,5,6,7,8,9]"),
                            ("rational-matrix", "[" + ",".join(["[1]"] * 9) + "]"),
                            ("rational-matrix", "[[1,2,3,4,5,6,7,8,9]]")):
            self.refuse("unsupported", self.canon, raw, domain)
        self.assertEqual(len(self.canon("[1,2,3,4,5,6,7,8]", "rational-vector")), 8)
        matrix = "[" + ",".join(["[1,2,3,4,5,6,7,8]"] * 8) + "]"
        self.assertEqual(len(self.canon(matrix, "rational-matrix")), 8)
        for domain, target, different_shape in (("rational-vector", "[1,2]", "[1]"),
                                                ("rational-matrix", "[[1,2]]", "[[1],[2]]")):
            spec = specification(domain, target)
            self.refuse("invalid", domains.prepare_comparison, different_shape, spec, runtime.fill_number)

    def test_spec_validation_diagnostic_overlap_and_precedence(self):
        base = specification("rational-set", "{1,2}", [{"id": "missing-member", "answer": "{1}"}])
        for key, value in (("checker_version", "future"), ("domain", "CAS"), ("shape", [2]),
                           ("orientation", "row"), ("target", "{1/0}"),
                           ("diagnostics", [{"id": "missing-member", "answer": "{2,1,1}"}]),
                           ("diagnostics", [{"id": "same", "answer": "{3}"}, {"id": "other", "answer": "{3.0}"}]),
                           ("diagnostics", [{"id": "same", "answer": "{3}"}, {"id": "same", "answer": "{4}"}])):
            spec = copy.deepcopy(base)
            spec[key] = value
            self.refuse("unavailable", domains.prepare_comparison, "{1/0}", spec, runtime.fill_number)
        for domain, target in (("rational-vector", "[1,2]"), ("rational-matrix", "[[1,2]]")):
            spec = specification(domain, target)
            for shape in ([True], [0], [9], [1.0], [2, 1, 1], None):
                bad = dict(spec, shape=shape)
                self.refuse("unavailable", domains.validate_spec, bad, runtime.fill_number)
        unknown = dict(base, extra=True)
        self.refuse("unavailable", domains.validate_spec, unknown, runtime.fill_number)
        vector = specification("rational-vector", "[1]")
        for orientation in (None, "unknown", ["row"]):
            self.refuse("unavailable", domains.validate_spec, dict(vector, orientation=orientation), runtime.fill_number)

    def test_runtime_authority_and_private_pinned_test_tables(self):
        examples = [
            ("rational-set", "{1,2}", "{3}", "{1,}", "{x}", "{1}", "{2,1,1.0}"),
            ("rational-interval-set", "[0,2)", "(0,2)", "[1,0]", "[0,x]", "[0,2]", "[0,1] U (1,2)"),
            ("rational-vector", "[1,2]", "[3,4]", "[1]", "[x,2]", "[2,1]", "[1.0,4/2]"),
            ("rational-matrix", "[[1,2]]", "[[3,4]]", "[[1]]", "[[x,2]]", "[[2,1]]", "[[1e0,4/2]]"),
        ]
        for domain, target, wrong, invalid, unsupported, diagnostic, equivalent in examples:
            spec = specification(domain, target, [{"id": "specific-error", "answer": diagnostic}])
            rows = authored_cases(spec, wrong, invalid, unsupported)
            with patch.object(runtime, "score_response", wraps=runtime.score_response) as scorer:
                self.assertEqual(domains.private_test_errors(spec, rows, runtime.fill_number, runtime_analyze), [])
                self.assertEqual(runtime_analyze(equivalent, spec)["state"], "correct")
                self.assertEqual(runtime_analyze(diagnostic, spec)["diagnostic_id"], "specific-error")
                self.assertGreater(scorer.call_count, 0)
            for transform in (lambda r: r[:-1], lambda r: [dict(row, checker_version="future") for row in r],
                              lambda r: [dict(row, state="correct") for row in r]):
                self.assertTrue(domains.private_test_errors(spec, transform(rows), runtime.fill_number, runtime_analyze))
            reversed_spec = dict(spec, diagnostics=list(reversed(spec["diagnostics"])))
            self.assertEqual(runtime_analyze(diagnostic, spec), runtime_analyze(diagnostic, reversed_spec))
            self.assertTrue(domains.private_test_errors(spec, rows, runtime.fill_number, lambda *_: {"state": "error"}))
            self.assertTrue(domains.private_test_errors(spec, rows, runtime.fill_number, lambda *_: None))
            with patch.object(runtime, "score_response", side_effect=RuntimeError("injected")):
                self.assertTrue(domains.private_test_errors(spec, rows, runtime.fill_number, runtime_analyze))

    def test_two_diagnostics_reordering_equivalent_overlap_and_invalid_tests(self):
        for domain, target, first, second, duplicate in (
                ("rational-set", "{1,2}", "{1}", "{2}", "{1,1.0}"),
                ("rational-interval-set", "[0,2)", "[0,2]", "(0,2)", "[0,1] U (1,2]"),
                ("rational-vector", "[1,2]", "[2,1]", "[1,1]", "[2e0,1.0]"),
                ("rational-matrix", "[[1,2]]", "[[2,1]]", "[[1,1]]", "[[2e0,1.0]]")):
            spec = specification(domain, target, [{"id": "first", "answer": first}, {"id": "second", "answer": second}])
            reversed_spec = dict(spec, diagnostics=list(reversed(spec["diagnostics"])))
            for raw in (target, first, second):
                self.assertEqual(runtime_analyze(raw, spec), runtime_analyze(raw, reversed_spec))
            overlap = dict(spec, diagnostics=[spec["diagnostics"][0], {"id": "duplicate", "answer": duplicate}])
            self.refuse("unavailable", domains.validate_spec, overlap, runtime.fill_number)
        spec = specification("rational-set", "{1}")
        good = authored_cases(spec, "{2}", "{1,}", "{x}")
        for rows in (None, [], good * 33, good + [None],
                     good + [dict(good[0], extra=True)],
                     good + [dict(good[0], diagnostic_id=1)]):
            self.assertTrue(domains.private_test_errors(spec, rows, runtime.fill_number, runtime_analyze))

    def test_no_scores_no_file_mutation_public_projection_and_failure(self):
        spec = specification("rational-set", "{1,2}", [{"id": "missing-member", "answer": "{1}"}])
        before = copy.deepcopy(spec)
        public = domains.public_contract(spec, runtime.fill_number)
        self.assertEqual(set(public), {"domain", "checker_version", "shape", "orientation", "grammar", "limits"})
        self.assertNotIn("target", public)
        self.assertNotIn("diagnostics", public)
        public["limits"]["set_entries"] = 999
        self.assertEqual(domains.LIMITS["set_entries"], 32)
        with tempfile.TemporaryDirectory() as tmp:
            saved = Path(tmp) / "session.json"
            saved.write_bytes(b'{"responses":[],"status":"active"}')
            prior = saved.read_bytes()
            with patch("builtins.open", side_effect=AssertionError("Unexpected file access")), \
                    patch.object(Path, "open", side_effect=AssertionError("Unexpected path access")):
                for raw in (" {2,1.0,1} ", "{1}", "{1/0}", "{x}"):
                    try:
                        operands = domains.prepare_comparison(raw, spec, runtime.fill_number)
                        self.assertEqual(operands.original, raw)
                        self.assertNotIn("score", vars(operands))
                        self.assertNotIn("state", vars(operands))
                    except domains.DomainRefusal as exc:
                        self.assertIn(exc.state, ("invalid", "unsupported"))
            self.assertEqual(saved.read_bytes(), prior)
        self.assertEqual(spec, before)
        with patch.object(runtime, "fill_number", side_effect=RuntimeError("injected")):
            self.refuse("error", domains.prepare_comparison, "{1}", spec, runtime.fill_number)
        self.refuse("error", domains.canonicalize, "{1}", "rational-set", lambda _: 1.0)
        self.refuse("unsupported", self.canon, "{" + "1" * 4096 + "}", "rational-set")
        self.refuse("invalid", self.canon, "{1}\n", "rational-set")
        self.refuse("invalid", self.canon, "{1}\t", "rational-set")
        self.refuse("unsupported", self.canon, "{1}\u00a0", "rational-set")
        self.refuse("unavailable", self.canon, "{1}", "unknown")
        source = (ROOT / "question_domains.py").read_text()
        self.assertNotIn("eval(", source)
        self.assertNotIn("write_text", source)
        self.assertNotIn("import runtime", source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
