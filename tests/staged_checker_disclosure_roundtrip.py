"""Independent learner-facing disclosure checks for production question slices."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

import evidence
import model
import runtime
import schema_validate
from surfaces import home, session
from polynomial_production_roundtrip import bank_fixture


def staged_bank(root):
    """Reuse two fictional MC prompts, adding the production declaration."""
    source = (ROOT / "prototypes/audit-question-families/fixtures/bank.md").read_text()
    source = source.split("Q3.", 1)[0]
    declaration = {"version": 1, "activity_id": "counter-staged",
                   "stimulus": "A fictional counter starts at 3. Add 2 once.",
                   "children": ["a200000000000001", "a200000000000002"],
                   "order": ["answer", "reason"]}
    path = root / "staged.md"
    path.write_text("STAGED-CASES: " + json.dumps([declaration]) + "\n" + source)
    errors, _warnings = model.lint(model.load(str(path)))
    if errors:
        raise AssertionError(errors)
    return path


def sitting(root, bank, mode):
    attempts = root / "_attempts"
    attempts.mkdir(exist_ok=True)
    path = attempts / ("session_" + mode + ".json")
    session.do_start(str(bank), {"count": 2, "pair": "a2-counter", "seed": 3},
                     mode, str(path), False)
    return path


def commit(path, answer):
    view = session.do_next(str(path))
    activity = view.get("activity") or {}
    action = {"kind": "submit", "answer": answer}
    if activity:
        action.update({key: activity[key] for key in
                       ("activity_id", "child_id", "submission_token")})
    return session.do_action(str(path), action)


class PublicDisclosure(unittest.TestCase):
    def test_polynomial_refusal_preserves_real_sitting_and_has_no_response_event(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bank = root / "polynomial.md"
            bank.write_text(bank_fixture())
            path = root / "_attempts" / "session_polynomial.json"
            path.parent.mkdir()
            session.do_start(str(bank), {"count": 1, "seed": 1}, "practice", str(path), False)
            before = path.read_bytes()
            log = evidence.log_path(str(root))
            events_before = list(evidence.events(log))
            for raw in ("2x", "sin(x)", "1000000+1-1"):
                with self.subTest(raw=raw), self.assertRaises(SystemExit):
                    session.do_submit(str(path), {"expression": raw}, None)
                self.assertEqual(path.read_bytes(), before)
                self.assertEqual(list(evidence.events(log)), events_before)

    def test_polynomial_formal_outcomes_stay_private_until_sitting_closes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            # Two fields in separate questions keep an authentic formal sitting
            # open after the first valid checker result.
            bank = root / "polynomial.md"
            source = bank_fixture()
            second = source.replace("Q1.", "Q2.", 1).replace(
                "Expand 2*(x+1), using explicit multiplication.",
                "Distribute the scalar in 2*(x+1), then enter an expanded expression.")
            bank.write_text(source + "\n" + second)
            path = root / "_attempts" / "session_polynomial.json"
            path.parent.mkdir()
            session.do_start(str(bank), {"count": 2, "seed": 1}, "exam", str(path), False)
            raw = {"expression": " 2*x+1 "}
            result = session.do_submit(str(path), raw, None)
            data = runtime.read_session(str(path))
            self.assertEqual(data["status"], "active")
            events = [ev for ev in evidence.events(evidence.log_path(str(root)))
                      if ev["event_type"] == "response"]
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0]["answer"], raw)
            self.assertEqual(events[0]["checker_outcomes"]["expression"]["checker_version"],
                             "a5-rational-polynomial-v2")
            event_schema = json.loads((ROOT / "schemas/response.schema.json").read_text())
            self.assertEqual(schema_validate.validate(events[0], event_schema), [])
            session_schema = json.loads((ROOT / "schemas/session.schema.json").read_text())
            self.assertEqual(schema_validate.validate(data, session_schema), [])
            public_event = runtime.evidence_feedback(events[0], data)
            for payload in (result, public_event, home._activity(str(root), {"polynomial": str(bank)}),
                            session.do_report(str(path))):
                text = json.dumps(payload)
                self.assertNotIn('"score":', text)
                self.assertNotIn('"checker_outcomes":', text)
                self.assertNotIn("distribution-omission", text)
                self.assertNotIn("(wrong)", text)
            session.do_submit(str(path), {"expression": "2+2*x"}, None)
            self.assertEqual(session.do_report(str(path))["summary"]["auto_correct"], 1)

    def test_first_child_has_no_score_in_home_report_or_evidence_projection(self):
        for mode in ("practice", "exam", "diagnostic"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                bank = staged_bank(root)
                path = sitting(root, bank, mode)
                result = commit(path, "B")
                data = runtime.read_session(str(path))
                self.assertEqual(data["mode"], mode)
                self.assertEqual(len(data["responses"]), 1)
                events = list(evidence.events(evidence.log_path(str(root))))
                response = next(ev for ev in events if ev["event_type"] == "response")
                self.assertIs(response["score"], False)
                self.assertEqual(response["stage"], "answer")
                before_hint = path.read_bytes()
                with self.assertRaises(SystemExit):
                    session.do_hint(str(path))
                self.assertEqual(path.read_bytes(), before_hint)
                self.assertEqual(len(list(evidence.events(evidence.log_path(str(root))))), len(events))
                projected = runtime.evidence_feedback(response, data)
                self.assertNotIn("score", projected)
                self.assertNotIn(response, runtime.learner_evidence(events, {data["session_id"]: data}))
                report = session.do_report(str(path))
                self.assertIsNone(report["summary"]["auto_correct"])
                for payload in (result, projected, home._activity(str(root), {"staged": str(bank)})):
                    text = json.dumps(payload)
                    self.assertNotIn('"score":', text)
                    self.assertNotIn("Adding two to three gives five", text)
                    self.assertNotIn("(wrong)", text)
                # An unresolved owning sitting must not turn a linked event into
                # ordinary practice feedback when an Activity scan cannot read it.
                self.assertNotIn("score", runtime.evidence_feedback(response, None))
                path.rename(path.with_suffix(".unavailable"))
                activity = json.dumps(home._activity(str(root), {"staged": str(bank)}))
                self.assertNotIn("(wrong)", activity)

    def test_case_closure_releases_two_child_outcomes_without_changing_mode(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bank = staged_bank(root)
            path = sitting(root, bank, "practice")
            commit(path, "B")
            commit(path, "B")
            data = runtime.read_session(str(path))
            self.assertEqual(data["mode"], "practice")
            self.assertEqual(data["status"], "complete")
            responses = [ev for ev in evidence.events(evidence.log_path(str(root)))
                         if ev["event_type"] == "response"]
            self.assertEqual(len(responses), 2)
            self.assertEqual([runtime.evidence_feedback(ev, data)["score"]
                              for ev in responses], [False, True])
            activity = json.dumps(home._activity(str(root), {"staged": str(bank)}))
            self.assertIn("(wrong)", activity)
            self.assertIn("(correct)", activity)
            self.assertEqual(session.do_report(str(path))["summary"]["auto_correct"], 1)


if __name__ == "__main__":
    unittest.main()
