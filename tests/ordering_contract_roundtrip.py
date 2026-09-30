#!/usr/bin/env python3
"""Structural ordering preserves identity, alternate answers and disclosure."""
import copy
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import evidence
import model
import runtime
import schema_validate


def authored_text(distractor=True):
    ids = ["a", "b", "c"] + (["spare"] if distractor else [])
    declaration = dict(version=1, blocks=ids, required=["a", "b", "c"],
                       dependencies=[["a", "c"], ["b", "c"]])
    steps = "\n".join("STEP) %s | %s" % (i, "Token" if i in ("a", "b") else i) for i in ids)
    return '''Q1. Assemble the synthetic prerequisite sequence.
[TYPE: build]
[OBJECTIVE: synthetic:ordering]
[ORDERING: %s]
%s
WHY BEST: Both independent prerequisites precede the final block.
KEY DISCRIMINATOR: Identity and dependencies determine the sequence.
DISTRACTOR ANALYSIS:
- Spare would be correct only if required by the task.
TRAP: Sorting equal labels rather than stable identities.
CONFIDENCE: high
''' % (json.dumps(declaration), steps)


class OrderingContract(unittest.TestCase):
    def setUp(self):
        self.q = model.parse_bank(authored_text())[0]

    def test_alternative_orders_and_diagnostics(self):
        self.assertEqual(model.lint([self.q])[0], [])
        for answer in (["a", "b", "c"], ["b", "a", "c"]):
            self.assertTrue(runtime.score_response(self.q, answer))
        for answer, category in ((["a", "c", "b"], "dependency_violation"),
                                 (["a", "b"], "missing_required"),
                                 (["a", "b", "c", "spare"], "selected_distractor"),
                                 ([], "missing_required")):
            self.assertFalse(runtime.score_response(self.q, answer))
            self.assertEqual(runtime.ordering_diagnostic(self.q, answer), category)
        for answer in (["a", "a"], ["foreign"], [1], {}, None):
            self.assertTrue(runtime.ordering_response_error(self.q, answer))
            self.assertFalse(runtime.score_response(self.q, answer))
        unconstrained = copy.deepcopy(self.q)
        unconstrained["ordering"]["dependencies"] = []
        self.assertTrue(runtime.score_response(unconstrained, ["c", "b", "a"]))

    def test_graph_lint_and_fingerprint(self):
        original = model.content_fingerprint(self.q)
        for update in (dict(version=True), dict(version=2), dict(required=[]),
                       dict(required=["missing"]), dict(required=["a", "a"]),
                       dict(blocks=["a", "a", "c", "spare"]),
                       dict(dependencies=[["a", "a"]]),
                       dict(dependencies=[["a", "spare"]]),
                       dict(dependencies=[["a", "b"], ["b", "a"]]),
                       dict(dependencies=[["a", "c"], ["a", "c"]]),
                       dict(dependencies=[["a", "b"]] * 257)):
            damaged = copy.deepcopy(self.q)
            damaged["ordering"].update(update)
            self.assertTrue(model.ordering_spec_errors(damaged), update)
            self.assertIn("item.invalid_ordering", [e.code for e in model.lint([damaged])[0]])
        for declaration in ('[ORDERING: broken]', '[ORDERING: ]',
                            '[ORDERING: {"version":1,"version":1}]'):
            parsed = model.parse_bank(re.sub(r"(?m)^\[ORDERING:.*$", declaration, authored_text()))
            self.assertEqual(len(parsed), 1)
            self.assertTrue(model.ordering_spec_errors(parsed[0]))
        for key, value in (("dependencies", []), ("required", ["a", "b", "c", "spare"])):
            changed = copy.deepcopy(self.q)
            changed["ordering"][key] = value
            self.assertNotEqual(model.content_fingerprint(changed), original)
        for changes in (dict(id="other"), dict(text="")):
            damaged = copy.deepcopy(self.q)
            damaged["blocks"][0].update(changes)
            self.assertTrue(model.ordering_spec_errors(damaged))
        oversized = copy.deepcopy(self.q)
        oversized["ordering"]["blocks"] = ["block%d" % i for i in range(65)]
        oversized["blocks"] = [{"id": i, "text": "Token"} for i in oversized["ordering"]["blocks"]]
        self.assertTrue(model.ordering_spec_errors(oversized))
        missing = model.parse_bank(authored_text().replace("STEP) spare | spare\n", ""))[0]
        self.assertTrue(model.ordering_spec_errors(missing))

    def test_public_schema_and_release(self):
        schema = json.loads((ROOT / "schemas/item.schema.json").read_text())
        public = runtime.public_item(self.q)
        self.assertEqual(schema_validate.validate(public, schema), [])
        self.assertEqual(public["ordering"], {"version": 1, "revision": model.content_fingerprint(self.q)})
        self.assertEqual(set(public["ordering"]), {"version", "revision"})
        for key, value in (("dependencies", []), ("required", ["a", "b", "c", "spare"])):
            changed = copy.deepcopy(self.q)
            changed["ordering"][key] = value
            self.assertNotEqual(runtime.public_item(changed)["ordering"]["revision"], public["ordering"]["revision"])
        shuffled = runtime.public_item(self.q, shuffle_seed=100)
        self.assertEqual(shuffled["ordering"]["revision"], public["ordering"]["revision"])
        self.assertNotIn("required", public["response_schema"])
        self.assertEqual(set(public["response_schema"]["allowed"]), {"a", "b", "c", "spare"})
        self.assertEqual(runtime.canonical_key(self.q), None)
        offline = runtime.page_item(self.q, offline=True)
        self.assertTrue(offline["served_required"])
        self.assertNotIn("key", offline)
        explain = runtime.explain_payload(self.q)
        self.assertTrue(runtime.score_response(self.q, explain["example_order"]))
        self.assertNotIn("spare", explain["steps"])
        for mode in ("practice", "remediation", "exam", "diagnostic"):
            session = dict(mode=mode, teaching_state={}, cursor=0, items=["q1"], status="active")
            before = copy.deepcopy(session)
            with self.assertRaises(SystemExit):
                runtime.teaching_transition(session, self.q, dict(kind="submit", answer=["a", "a"]))
            self.assertEqual(session, before)
            result = runtime.teaching_transition(session, self.q, dict(kind="submit", answer=["a", "c", "b"]))
            self.assertEqual("ordering_diagnostic" in result, mode in ("practice", "remediation"))
            if mode in ("exam", "diagnostic"):
                self.assertEqual(result["action"], "defer_feedback")
                self.assertNotIn("reveal", result)
        diagnostic = {"version": 1, "category": "missing_required"}
        payload = {"nested": [{"ordering_diagnostic": diagnostic}]}
        for mode in ("exam", "diagnostic"):
            self.assertEqual(runtime.submission_feedback(payload, mode), {"nested": [{}]})
        self.assertEqual(runtime.submission_feedback(payload, "practice"), payload)

    def test_legacy_exact_text(self):
        q = model.parse_bank("Q1. Synthetic order.\n[TYPE: build]\nSTEP) First\nSTEP) Second\n")[0]
        self.assertTrue(runtime.score_response(q, ["First", "Second"]))
        self.assertFalse(runtime.score_response(q, ["Second", "First"]))
        self.assertEqual(runtime.canonical_key(q), "First\x1fSecond")
        self.assertNotIn("ordering", runtime.public_item(q))

    def test_cli_refusal_durable_ids_and_checker_version(self):
        def run(*args, success=True):
            result = subprocess.run([sys.executable, str(ROOT / "itembank.py"), *map(str, args)],
                                    capture_output=True, text=True, cwd=ROOT)
            self.assertEqual(result.returncode == 0, success, result.stderr)
            return json.loads(result.stdout) if success else result
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            bank, session = base / "bank.md", base / "session.json"
            bank.write_text(authored_text())
            run("start", bank, "--count", "1", "--mode", "exam", "--out", session)
            before = session.read_bytes()
            events_before = list(evidence.live_events(evidence.log_path(folder)))
            for invalid in (["a", "a"], ["foreign"]):
                run("submit", session, "--answer", json.dumps(invalid), success=False)
                self.assertEqual(session.read_bytes(), before)
                self.assertEqual(list(evidence.live_events(evidence.log_path(folder))), events_before)
            result = run("submit", session, "--answer", '["b","a","c"]')
            self.assertNotIn("score", result)
            self.assertNotIn("explain", result)
            events = [e for e in evidence.live_events(evidence.log_path(folder)) if e["event_type"] == "response"]
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0]["answer"], ["b", "a", "c"])
            self.assertTrue(events[0]["score"])
            self.assertEqual(events[0]["checker_version"], 1)


if __name__ == "__main__":
    unittest.main()
