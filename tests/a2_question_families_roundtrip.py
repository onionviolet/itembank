#!/usr/bin/env python3
"""Executable synthetic journeys, isolated from learner files and shared writes."""
import copy
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
PROTO = ROOT / "prototypes" / "audit-question-families"
BANK = PROTO / "fixtures" / "bank.md"
sys.path[:0] = [str(ROOT), str(PROTO)]
import evidence
import identity
import journal
import model
import runtime
from families import ANCHORS, PASSAGE, Journey, Refusal
from polynomial import VERSION, analyze, canonicalize, DomainError


class NativeControls(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inputs = []
        self.buttons = []
        self.labels = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "input":
            self.inputs.append(attrs)
        if tag == "button":
            self.buttons.append(attrs)
        if tag == "label":
            self.labels.append(attrs)


class Families(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="itembank-a2-test-")
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)

    def journey(self, family="staged", mode="exam"):
        return Journey.create(self.base / family, family, mode)

    def submit(self, obj, answer):
        view = obj.view()
        return obj.submit(view["item"]["id"], answer, view["presentation_revision"],
                          view["bank_revision"])

    def events(self, obj):
        return [e for e in evidence.live_events(evidence.log_path(str(obj.base)))
                if e.get("session_id") == runtime.read_session(str(obj.sitting))["session_id"]
                and e.get("event_type") == evidence.RESPONSE_EVENT_TYPE]

    def test_authored_bank_uses_one_parser_and_lints(self):
        qs = model.load(str(BANK))
        self.assertEqual(len(qs), 4)
        self.assertEqual(model.lint(qs)[0], [])
        self.assertEqual([f["id"] for f in qs[2]["fields"]], ["color", "count"])
        self.assertIn("{{color}}", qs[2]["stem"])
        self.assertIn("{{count}}", qs[2]["stem"])

    def test_staged_wrong_answer_advances_without_unopened_feedback(self):
        obj = self.journey()
        initial = obj.view()
        self.assertEqual(initial["stage"], "answer")
        before = obj.sitting.read_bytes()
        with self.assertRaises(Refusal):
            self.submit(obj, "Z")
        self.assertEqual(obj.sitting.read_bytes(), before)
        result = self.submit(obj, "B")
        self.assertTrue(result["accepted"])
        reason = obj.view()
        self.assertEqual(reason["stage"], "reason")
        self.assertEqual(reason["committed_answer"], "B")
        self.assertEqual(reason["branch"], "route-b")
        for payload in (result, reason, obj.report()):
            text = json.dumps(payload)
            for forbidden in ('"score"', '"why"', '"rationale"', 'distribution-omission'):
                self.assertNotIn(forbidden, text)
            def no_verdict(value):
                if isinstance(value, dict):
                    for key, child in value.items():
                        if key in ("correct", "auto_correct"):
                            self.assertIsNone(child)
                        no_verdict(child)
                elif isinstance(value, list):
                    for child in value:
                        no_verdict(child)
            no_verdict(payload)
        self.assertNotIn("Static observation", obj.render())
        self.assertNotIn("Adding two to three gives five", obj.render())
        with self.assertRaises(Refusal):
            obj.checkpoint(60, True, obj.revision())
        # Restart in a fresh Python process. Merely reading appends no evidence.
        events_before = Path(evidence.log_path(str(obj.base))).read_bytes()
        script = "import json,sys; from families import Journey; print(json.dumps(Journey(sys.argv[1]).view()))"
        env = dict(os.environ, PYTHONPATH=os.pathsep.join((str(ROOT), str(PROTO))))
        reopened = subprocess.run([sys.executable, "-c", script, str(obj.base)],
                                  env=env, capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(reopened.stdout), reason)
        self.assertEqual(Path(evidence.log_path(str(obj.base))).read_bytes(), events_before)
        # Replaying the first stage is refused, never repurposed as the reason.
        with self.assertRaises(Refusal):
            obj.submit(initial["item"]["id"], "B", obj.revision(), initial["bank_revision"])
        self.submit(obj, "B")
        self.assertEqual(obj.view()["stage"], "complete")
        events = self.events(obj)
        self.assertEqual(len(events), 2)
        self.assertEqual([ev["score"] for ev in events], [False, True])
        self.assertEqual(len({ev["item_id"] for ev in events}), 2)
        self.assertEqual(len({ev["objective"] for ev in events}), 2)
        self.assertIn("Static observation", obj.render())

    def test_practice_is_explicitly_unavailable_without_files(self):
        with self.assertRaisesRegex(Refusal, "practice is unavailable"):
            self.journey(mode="practice")
        self.assertFalse((self.base / "staged").exists())

    def test_branch_and_checkpoint_journal_cas_restart_and_undo(self):
        obj = self.journey()
        with self.assertRaises(Refusal):
            obj.checkpoint(0, False, obj.revision())
        self.submit(obj, "A")
        self.submit(obj, "B")
        before = obj.sidecar.read_bytes()
        revision = obj.revision()
        obj.checkpoint(30, False, revision)
        self.assertEqual(Journey(obj.base).view()["checkpoint"], {"seconds": 30, "complete": False})
        with self.assertRaises(journal.JournalError):
            obj.checkpoint(60, True, revision)
        with self.assertRaises(Refusal):
            obj.checkpoint(30, True, obj.revision())
        obj.checkpoint(60, True, obj.revision())
        self.assertEqual(obj.view()["checkpoint"], {"seconds": 60, "complete": True})
        self.assertEqual(len(self.events(obj)), 2)
        # Undo one presentation revision through the existing journal only.
        lines = [json.loads(line) for line in (obj.base / "_journal" / "journal.jsonl").read_text().splitlines()]
        applied = [e for e in lines if e["state"] == "applied"][-1]
        journal.undo(str(obj.base), applied["entry_id"], "agent", "a2-synthetic")
        self.assertEqual(obj.view()["checkpoint"], {"seconds": 30, "complete": False})
        self.assertNotEqual(obj.sidecar.read_bytes(), before)

    def test_multiple_blanks_invalid_refusal_draft_restart_and_stale_revision(self):
        obj = self.journey("blanks")
        v = obj.view()
        wrong = {"color": "BLUE", "count": "oops"}
        obj.save_draft(v["item"]["id"], wrong, v["presentation_revision"])
        before = obj.sitting.read_bytes()
        try:
            self.submit(obj, wrong)
        except SystemExit:
            pass
        else:
            self.fail("Invalid numeric input was not refused")
        self.assertEqual(obj.sitting.read_bytes(), before)
        self.assertEqual(Journey(obj.base).view()["draft"], wrong)
        self.assertEqual(self.events(obj), [])
        with self.assertRaises(journal.JournalError):
            obj.save_draft(v["item"]["id"], {}, v["presentation_revision"])
        with self.assertRaises(Refusal):
            obj.submit(v["item"]["id"], {"color": "blue", "count": "2.5"},
                       v["presentation_revision"], v["bank_revision"])
        self.submit(obj, {"color": "blue", "count": "5/2"})
        self.assertNotIn("draft", obj.view())
        ev = self.events(obj)[0]
        self.assertEqual(ev["answer"], {"color": "blue", "count": "5/2"})
        self.assertTrue(ev["score"])

    def test_stale_bank_and_anchor_preserve_originals(self):
        obj = self.journey()
        before = obj.sitting.read_bytes()
        obj.bank.write_bytes(obj.bank.read_bytes() + b"\nChanged revision.\n")
        with self.assertRaisesRegex(Refusal, "Stale bank"):
            obj.view()
        self.assertEqual(obj.sitting.read_bytes(), before)
        evidence_obj = self.journey("evidence")
        with patch("families.PASSAGE", PASSAGE + " changed"):
            with self.assertRaisesRegex(Refusal, "Stale evidence anchors"):
                evidence_obj.view()

    def test_unsaved_invalid_entry_preserved_and_identical_draft_is_noop(self):
        obj = self.journey("blanks")
        raw = {"color": "new raw spelling", "count": "not-a-number"}
        before = obj.sitting.read_bytes()
        with self.assertRaises(SystemExit):
            self.submit(obj, raw)
        self.assertEqual(Journey(obj.base).view()["draft"], raw)
        self.assertEqual(obj.sitting.read_bytes(), before)
        journal_path = obj.base / "_journal" / "journal.jsonl"
        bytes_before = journal_path.read_bytes()
        obj.save_draft(obj.view()["item"]["id"], raw, obj.revision())
        self.assertEqual(journal_path.read_bytes(), bytes_before)

    def test_evidence_selection_stable_anchors_and_runtime_verdict(self):
        obj = self.journey("evidence", "diagnostic")
        view = obj.view()
        self.assertEqual(view["anchors"], ANCHORS)
        for anchor in ANCHORS.values():
            self.assertEqual(PASSAGE[anchor["start"]:anchor["end"]], anchor["quote"])
        for invalid in (["A", "A"], ["X"], "A"):
            with self.assertRaises(Refusal):
                self.submit(obj, invalid)
        self.assertEqual(self.events(obj), [])
        obj.save_draft(view["item"]["id"], ["C", "A"], obj.revision())
        self.assertEqual(Journey(obj.base).view()["draft"], ["C", "A"])
        self.submit(obj, ["C", "A"])
        self.assertTrue(self.events(obj)[0]["score"])

    def test_native_static_controls_and_no_script_dependency(self):
        for family in ("staged", "blanks", "evidence"):
            obj = self.journey(family)
            raw = obj.render()
            parser = NativeControls()
            parser.feed(raw)
            self.assertNotIn("<script", raw)
            self.assertIn('method="post"', raw)
            self.assertIn(":focus-visible", raw)
            self.assertEqual(len(parser.buttons), 2)
            self.assertEqual(len(parser.labels), {"evidence": 3, "staged": 4, "blanks": 2}[family])
            if family == "blanks":
                ids = [inp["id"] for inp in parser.inputs if "id" in inp]
                self.assertEqual(ids, ["color", "count"])
                self.assertEqual([label["for"] for label in parser.labels], ids)
        self.assertIn("Static case", BANK.read_text())


class Polynomial(unittest.TestCase):
    def test_authored_cases_and_form(self):
        table = json.loads((PROTO / "acceptance.json").read_text())
        self.assertEqual(table["checker_version"], VERSION)
        for case in table["tests"]:
            with self.subTest(raw=case["input"]):
                result = analyze(case["input"], table["target"])
                self.assertEqual(result["state"], case["state"])
                self.assertEqual(result.get("diagnostic_id"), case.get("diagnostic_id"))
                self.assertEqual(result["original"], case["input"])
                self.assertEqual(result["authority"], "advisory-only")
        self.assertEqual(canonicalize("x^2+2*x+1")[0], canonicalize("(x+1)^2")[0])
        self.assertTrue(canonicalize("x^2+2*x+1")[1])
        self.assertFalse(canonicalize("(x+1)^2")[1])

    def test_runtime_comparison_no_second_scorer(self):
        with patch("polynomial.runtime.score_response", wraps=runtime.score_response) as scorer:
            self.assertEqual(analyze("2*x+2")["state"], "correct")
            self.assertGreater(scorer.call_count, 0)
            self.assertTrue(all(call.args[0]["type"] == "fill" for call in scorer.call_args_list))

    def test_unresolved_formal_disclosure_and_resource_limits(self):
        for mode in ("exam", "diagnostic"):
            for raw in ("2*x+1", "2*x+2", "2*(x+1)"):
                hidden = analyze(raw, mode=mode)
                self.assertEqual(hidden["state"], "withheld")
                self.assertIsNone(hidden["runtime_comparison"])
                self.assertNotIn("diagnostic_id", hidden)
            released = analyze("2*x+1", mode=mode, session={"mode": mode, "status": "complete"})
            self.assertEqual(released["diagnostic_id"], "distribution-omission")
        for raw, target, failed, state in (("2*x", "bad", False, "unavailable"),
                                         ("2*x", "2*(x+1)", False, "unavailable"),
                                         ("2*x", "2*x+2", True, "error"),
                                         ("x" * 161, "2*x+2", False, "unsupported"),
                                         ("+".join(["x"] * 30), "2*x+2", False, "unsupported")):
            result = analyze(raw, target, fail=failed)
            self.assertEqual(result["state"], state)
            self.assertIsNone(result["runtime_comparison"])
        # Diagnostics are not reused with a different accepted teacher target.
        self.assertNotIn("diagnostic_id", analyze("2*x+1", target="x+1"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
