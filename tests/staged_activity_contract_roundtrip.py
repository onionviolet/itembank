"""Synthetic staged contract tests, with no production format registration."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "prototypes" / "audit-question-families")]
import model
import runtime
import schema_validate
from surfaces import session
from staged_v2 import StagedJourney, Refusal, declaration, validate_case, validate_cases


class StagedContract(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name) / "journey"

    def create(self, mode="exam"):
        return StagedJourney.create(self.base, mode)

    def commit(self, obj, answer):
        view = obj.view()
        return obj.submit(view["item"]["id"], answer, view["revision"])

    def test_invalid_forged_unopened_and_replay_preserve_commitment(self):
        obj = self.create()
        view = obj.view()
        original = obj.sitting.read_bytes()
        for item, answer, stage in [(view["item"]["id"], "Z", None),
                                     ("q2", "B", None),
                                     (view["item"]["id"], "B", "reason")]:
            with self.assertRaises(Refusal):
                obj.submit(item, answer, view["revision"], stage=stage)
            self.assertEqual(original, obj.sitting.read_bytes())
        result = self.commit(obj, "B")
        self.assertTrue(result["accepted"])
        committed = obj.sitting.read_bytes()
        with self.assertRaises(Refusal):
            obj.submit(view["item"]["id"], "B", view["revision"])
        self.assertEqual(committed, obj.sitting.read_bytes())
        self.assertEqual(len(obj.linked_events()), 1)

    def test_wrong_answer_reload_process_restart_and_two_linked_events(self):
        obj = self.create()
        self.commit(obj, "B")
        self.assertEqual(StagedJourney(self.base).view()["stage"], "reason")
        script = "import sys,json; from staged_v2 import StagedJourney; print(json.dumps(StagedJourney(sys.argv[1]).view()))"
        import os
        env = dict(os.environ, PYTHONPATH=str(ROOT / "prototypes" / "audit-question-families"))
        restarted = subprocess.run([sys.executable, "-c", script, str(self.base)],
                                   env=env, capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(restarted.stdout)["committed_answer"], "B")
        self.commit(obj, "B")
        events = obj.linked_events()
        self.assertEqual([ev["stage"] for ev in events], ["answer", "reason"])
        self.assertEqual(len({ev["event_id"] for ev in events}), 2)
        self.assertEqual(len({ev["activity_id"] for ev in events}), 1)
        self.assertEqual(len({ev["case_revision"] for ev in events}), 1)
        self.assertEqual([ev["score"] for ev in events], [False, True])
        self.assertEqual(len({ev["objective"] for ev in events}), 2)

    def test_practice_barrier_and_formal_disclosure(self):
        for mode in ("practice", "exam", "diagnostic"):
            obj = StagedJourney.create(Path(self.tmp.name) / mode, mode)
            result = self.commit(obj, "B")
            for payload in (result, obj.view(), obj.linked_events(), session.do_report(str(obj.sitting))):
                encoded = json.dumps(payload)
                for private in ('"score"', '"why"', '"explain"'):
                    self.assertNotIn(private, encoded)
                self.assertNotIn('"correct": true', encoded)
                self.assertNotIn('"correct": false', encoded)
            self.assertNotIn("Adding two to three gives five", obj.render())
            self.assertNotIn("child_feedback", obj.view())
            self.commit(obj, "B")
            if mode == "practice":
                self.assertEqual(len(obj.view()["child_feedback"]), 2)
                self.assertEqual(obj.view()["transport_mode"], "exam")
            else:
                self.assertNotIn("child_feedback", obj.view())

    def test_stale_missing_revision_and_crash_window_refuse_without_loss(self):
        obj = self.create()
        self.commit(obj, "B")
        before = obj.sitting.read_bytes()
        bank = obj.bank.read_bytes()
        obj.bank.write_bytes(bank + b"\n")
        with self.assertRaises(Refusal):
            obj.view()
        self.assertEqual(before, obj.sitting.read_bytes())
        obj.bank.write_bytes(bank)
        data = runtime.read_session(str(obj.sitting))
        data["staged_prototype"]["case"]["stimulus"] += " Changed."
        runtime.write_session(str(obj.sitting), data)
        with self.assertRaisesRegex(Refusal, "Stale case"):
            obj.view()
        obj.sitting.write_bytes(before)
        data = runtime.read_session(str(obj.sitting))
        del data["staged_prototype"]
        runtime.write_session(str(obj.sitting), data)
        with self.assertRaises(Refusal):
            obj.view()
        obj.sitting.write_bytes(before)
        with patch.object(session, "write_session", side_effect=OSError("synthetic disk failure")):
            with self.assertRaises(OSError):
                self.commit(obj, "B")
        self.assertEqual(before, obj.sitting.read_bytes())
        with self.assertRaisesRegex(Refusal, "crash window"):
            obj.view()

    def test_concurrent_duplicate_and_conflicting_commit(self):
        for answers in (("B", "B"), ("A", "B")):
            obj = StagedJourney.create(Path(self.tmp.name) / ("".join(answers)))
            view = obj.view()
            def submit(answer):
                try:
                    obj.submit(view["item"]["id"], answer, view["revision"])
                    return "committed"
                except Refusal:
                    return "refused"
            with ThreadPoolExecutor(max_workers=2) as pool:
                statuses = list(pool.map(submit, answers))
            self.assertEqual(sorted(statuses), ["committed", "refused"])
            self.assertEqual(obj.view()["stage"], "reason")
            self.assertEqual(len(obj.linked_events()), 1)

    def test_declaration_complete_selection_and_additive_schema(self):
        obj = self.create()
        qs = model.load(str(obj.bank))
        self.assertEqual(model.lint(qs)[0], [])
        case = declaration(obj.bank)
        overlapping = copy.deepcopy(case)
        overlapping["activity_id"] += ":second"
        with self.assertRaisesRegex(Refusal, "overlapping"):
            validate_cases([case, overlapping], qs, obj.bank)
        for mutate in (lambda c: c.update(children=[c["children"][0]] * 2),
                       lambda c: c.update(children=["missing", c["children"][1]]),
                       lambda c: c.update(order=["reason", "answer"]),
                       lambda c: c.update(children=[c["children"][0], "a200000000000003"])):
            broken = copy.deepcopy(case)
            mutate(broken)
            with self.assertRaises(Refusal):
                validate_case(broken, qs, obj.bank)
        with self.assertRaises(Refusal):
            StagedJourney.create(Path(self.tmp.name) / "split", selected=case["children"][:1])
        schema = json.loads((ROOT / "schemas" / "session.schema.json").read_text())
        self.assertEqual(schema_validate.validate(runtime.read_session(str(obj.sitting)), schema), [])
        legacy = runtime.read_session(str(obj.sitting))
        del legacy["staged_prototype"]
        self.assertEqual(schema_validate.validate(legacy, schema), [])


if __name__ == "__main__":
    unittest.main()
