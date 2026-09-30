#!/usr/bin/env python3
"""Executable fixed-anchor proposal over shipped owners, fictional data only."""
import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
PROTO = ROOT / "prototypes/evidence-anchor-contract-20260930"
spec = importlib.util.spec_from_file_location("anchor_contract", PROTO / "anchor_contract.py")
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)
import course
import evidence
import journal
import model
import runtime
from surfaces import session


class Controls(HTMLParser):
    def __init__(self):
        super().__init__(); self.inputs = []; self.labels = []
    def handle_starttag(self, tag, attrs):
        if tag == "input": self.inputs.append(dict(attrs))
        if tag == "label": self.labels.append(dict(attrs))


class Contract(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="anchor-proposal-")
        self.addCleanup(self.tmp.cleanup)
        self.obj = adapter.Journey.create(self.tmp.name)

    def declaration(self):
        return copy.deepcopy(self.obj.state()["declaration"])

    def validate(self, declaration):
        return adapter.validate(self.obj.base, declaration, model.load(str(self.obj.bank))[0])

    def submit(self, ids, obj=None):
        obj = obj or self.obj
        view = obj.view()
        return obj.submit(view["item"]["id"], ids, view["draft_fingerprint"], view["responses"])

    def events(self, obj=None):
        obj = obj or self.obj
        sid = runtime.read_session(str(obj.sitting))["session_id"]
        return [e for e in evidence.live_events(evidence.log_path(str(obj.base)))
                if e.get("session_id") == sid and e.get("event_type") == evidence.RESPONSE_EVENT_TYPE]

    def test_exact_unicode_and_distinct_occurrences(self):
        declaration = self.declaration()
        self.assertEqual(self.validate(declaration), adapter.PASSAGE)
        first, _, last = declaration["anchors"]
        self.assertEqual(first["label"], last["label"])
        self.assertEqual(first["quote"], last["quote"])
        self.assertNotEqual(first["id"], last["id"])
        self.assertNotEqual(first["start"], last["start"])
        self.assertEqual(model.lint(model.load(str(self.obj.bank)))[0], [])
        q = model.load(str(self.obj.bank))[0]
        q["objective"] = "unbound-objective"
        with self.assertRaises(adapter.Refusal) as error:
            adapter.validate(self.obj.base, declaration, q)
        self.assertEqual(error.exception.code, "objective-mismatch")
        changed = self.declaration(); changed["anchors"][0]["start"] += 1
        with self.assertRaises(adapter.Refusal): self.validate(changed)

    def test_malformed_offsets_overlap_and_projection(self):
        mutations = [
            lambda d: d.update(version=True), lambda d: d.update(offset_unit="utf-16"),
            lambda d: d.update(unknown=True), lambda d: d.update(anchors=[]),
            lambda d: d["anchors"][0].update(start=-1),
            lambda d: d["anchors"][0].update(start=True),
            lambda d: d["anchors"][0].update(end=500),
            lambda d: d["anchors"][0].update(end=8),
            lambda d: d["anchors"][0].update(quote="add two."),
            lambda d: d["anchors"][2].update(id="rule-first"),
            lambda d: d["anchors"][2].update(option="A"),
            lambda d: d["anchors"][2].update(option="Z"),
            lambda d: d["anchors"][0].update(label=""),
            lambda d: d["anchors"][0].update(start=17, end=32, quote="Start at three."),
            lambda d: d["binding_ref"].update(binding_revision_id="0" * 16),
            lambda d: d["source_ref"].update(source_object_id="0" * 16),
            lambda d: d.update(passage_fingerprint="sha256:" + "0" * 64),
            lambda d: d.update(source_bytes_fingerprint=[]),
            lambda d: d["source_ref"].update(source_object_id=[]),
            lambda d: d["source_ref"].update(locator=False),
            lambda d: d["source_ref"].update(range={}),
            lambda d: d["source_ref"]["range"].update(locator_id="L1"),
            lambda d: d["binding_ref"].update(binding_id={}),
        ]
        before = self.obj.sitting.read_bytes()
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                declaration = self.declaration(); mutate(declaration)
                with self.assertRaises(adapter.Refusal): self.validate(declaration)
        self.assertEqual(before, self.obj.sitting.read_bytes())
        self.assertEqual(self.events(), [])

    def test_source_move_preserves_identity_and_draft(self):
        view = self.obj.view()
        self.obj.save_draft(view["item"]["id"], ["rule-second", "rule-first"], self.obj.fingerprint())
        ref = self.declaration()["source_ref"]
        journal.op_move(str(self.obj.base), ref["source_object_id"], "moved.md",
                        ref["source_fingerprint"], "human", "synthetic")
        reopened = adapter.Journey(self.obj.base).view()
        self.assertEqual(reopened["draft"]["anchor_ids"], ["rule-second", "rule-first"])
        self.assertEqual(reopened["anchors"], view["anchors"])
        self.submit(["rule-second", "rule-first"])
        self.assertTrue(self.events()[0]["score"])

    def test_changed_unavailable_and_wrong_revision_keep_draft(self):
        view = self.obj.view()
        self.obj.save_draft(view["item"]["id"], ["start"], self.obj.fingerprint())
        old_draft, old_session = self.obj.sidecar.read_bytes(), self.obj.sitting.read_bytes()
        ref = self.declaration()["source_ref"]
        path = self.obj.base / journal.read_registry(str(self.obj.base))[ref["source_object_id"]]["path"]
        original = path.read_bytes()
        for changed in (b"Changed fictional source.\n", original.replace(b"\n", b"\r\n")):
            path.write_bytes(changed)
            with self.assertRaises((course.CourseError, adapter.Refusal)): self.obj.view()
            self.assertEqual(old_draft, self.obj.sidecar.read_bytes())
            self.assertEqual(old_session, self.obj.sitting.read_bytes())
        path.unlink()
        with self.assertRaises(course.CourseError) as error: self.obj.view()
        self.assertEqual(error.exception.code, "course.reading_source_unavailable")
        path.write_bytes(original)
        self.assertEqual(adapter.Journey(self.obj.base).view()["draft"]["anchor_ids"], ["start"])
        self.assertEqual(self.events(), [])

    def test_bank_declaration_and_stale_draft_refuse(self):
        view = self.obj.view(); expected = self.obj.fingerprint()
        self.obj.save_draft(view["item"]["id"], ["rule-first"], expected)
        before = self.obj.sidecar.read_bytes()
        with self.assertRaises(journal.JournalError):
            self.obj.save_draft(view["item"]["id"], ["start"], expected)
        self.assertEqual(before, self.obj.sidecar.read_bytes())
        bank = self.obj.bank.read_bytes(); self.obj.bank.write_bytes(bank + b"\n")
        with self.assertRaises(adapter.Refusal): self.obj.view()
        self.obj.bank.write_bytes(bank)
        state = json.loads(before); state["declaration"]["anchors"][0]["label"] = "changed"
        self.obj.sidecar.write_bytes(self.obj.encode(state))
        with self.assertRaises(adapter.Refusal): self.obj.view()
        self.obj.sidecar.write_bytes(before)

    def test_fresh_process_reads_exact_draft_without_evidence(self):
        view = self.obj.view()
        self.obj.save_draft(view["item"]["id"], ["rule-second", "rule-first"], self.obj.fingerprint())
        before = self.obj.sitting.read_bytes()
        result = subprocess.run([sys.executable, str(PROTO / "anchor_contract.py"),
                                 "--inspect-root", str(self.obj.base)],
                                capture_output=True, text=True, check=True)
        reopened = json.loads(result.stdout)
        self.assertEqual(reopened["draft"]["anchor_ids"], ["rule-second", "rule-first"])
        self.assertEqual(reopened["declaration_revision"], view["declaration_revision"])
        before_state = json.loads(before)
        after_state = runtime.read_session(str(self.obj.sitting))
        before_state.pop("served_ts", None); after_state.pop("served_ts", None)
        self.assertEqual(before_state, after_state)
        self.assertEqual(self.events(), [])

    def test_invalid_selection_never_records_attempt(self):
        for ids in (["rule-first", "rule-first"], ["unknown"], "rule-first", [], None, 12):
            with self.assertRaises(adapter.Refusal): self.submit(ids)
        self.assertEqual(self.events(), [])
        self.assertEqual(runtime.read_session(str(self.obj.sitting))["cursor"], 0)
        self.assertIn("<fieldset>", self.obj.render())

    def test_replayed_practice_form_cannot_record_twice(self):
        obj = adapter.Journey.create(Path(self.tmp.name) / "replay", "practice")
        view = obj.view()
        obj.submit(view["item"]["id"], ["start", "rule-first"],
                   view["draft_fingerprint"], view["responses"])
        with self.assertRaises(adapter.Refusal) as error:
            obj.submit(view["item"]["id"], ["start", "rule-first"],
                       obj.fingerprint(), view["responses"])
        self.assertEqual(error.exception.code, "sitting-stale")
        self.assertEqual(len(self.events(obj)), 1)

    def test_rights_and_accepted_source_revision_refuse(self):
        ref = self.declaration()["source_ref"]
        row = journal.read_registry(str(self.obj.base))[ref["source_object_id"]]
        journal.op_grant_rights(str(self.obj.base), ref["source_object_id"],
                               {"read": "denied"}, row["fingerprint"], "human", "synthetic")
        with self.assertRaises(course.CourseError) as error: self.obj.view()
        self.assertEqual(error.exception.code, "course.rights_not_granted")
        row = journal.read_registry(str(self.obj.base))[ref["source_object_id"]]
        journal.op_grant_rights(str(self.obj.base), ref["source_object_id"],
                               {"read": "granted"}, row["fingerprint"], "human", "synthetic")
        journal.op_edit_in_place(str(self.obj.base), ref["source_object_id"], "source", row["path"],
                                 b"Accepted fictional successor.\n", row["fingerprint"], "human", "synthetic")
        with self.assertRaises(course.CourseError) as error: self.obj.view()
        self.assertEqual(error.exception.code, "course.reading_source_stale")
        self.assertEqual(self.events(), [])

    def test_diagnostic_feedback_withheld_before_completion(self):
        obj = adapter.Journey.create(Path(self.tmp.name) / "diagnostic", "diagnostic")
        result = self.submit(["rule-first", "start"], obj)
        self.assertNotIn("score", result)
        self.assertEqual(runtime.read_session(str(obj.sitting))["cursor"], 1)
        self.submit(["rule-first", "rule-second"], obj)
        self.assertEqual(runtime.read_session(str(obj.sitting))["status"], "complete")
        self.assertEqual(len(self.events(obj)), 2)

    def test_actual_formal_release_and_runtime_score(self):
        with patch("runtime.score_response", wraps=runtime.score_response) as scorer:
            result = self.submit(["rule-first", "start"])
            self.assertGreater(scorer.call_count, 0)
        self.assertTrue(result["accepted"])
        self.assertFalse(self.events()[0]["score"])
        self.assertEqual(runtime.read_session(str(self.obj.sitting))["cursor"], 1)
        for data in (result, self.obj.view(), session.do_report(str(self.obj.sitting))):
            text = json.dumps(data)
            for forbidden in ('"score"', '"why"', '"explanation"', '"selection_feedback"'):
                self.assertNotIn(forbidden, text)
            def check_hidden(value):
                if isinstance(value, dict):
                    for key, child in value.items():
                        if key in ("correct", "auto_correct"):
                            self.assertIsNone(child)
                        check_hidden(child)
                elif isinstance(value, list):
                    for child in value: check_hidden(child)
            check_hidden(data)
        self.submit(["rule-first", "rule-second"])
        self.assertEqual(runtime.read_session(str(self.obj.sitting))["status"], "complete")
        report = session.do_report(str(self.obj.sitting))
        self.assertIn("correct", json.dumps(report))
        self.assertEqual(len(self.events()), 2)

    def test_actual_practice_wrong_holds_then_correct_advances(self):
        obj = adapter.Journey.create(Path(self.tmp.name) / "practice", "practice")
        result = self.submit(["rule-first", "start"], obj)
        self.assertTrue(result["accepted"])
        self.assertFalse(self.events(obj)[0]["score"])
        self.assertEqual(runtime.read_session(str(obj.sitting))["cursor"], 0)
        self.assertFalse(result["score"])
        self.assertEqual(result["selection_feedback"]["kind"], "own_selections")
        reopened = adapter.Journey(obj.base)
        self.assertEqual(reopened.view()["draft"]["anchor_ids"], ["rule-first", "start"])
        self.submit(["rule-first", "rule-second"], reopened)
        self.assertEqual(runtime.read_session(str(obj.sitting))["cursor"], 1)
        self.assertEqual(len(self.events(obj)), 2)

    def test_native_static_controls(self):
        raw = self.obj.render(); parser = Controls(); parser.feed(raw)
        checkboxes = [x for x in parser.inputs if x.get("type") == "checkbox"]
        self.assertEqual([x["id"] for x in checkboxes], [x["for"] for x in parser.labels])
        self.assertEqual(len(checkboxes), 3)
        for token in ("<fieldset>", "<legend>", "method=\"post\"", ":focus-visible", "min-height:44px"):
            self.assertIn(token, raw)
        self.assertNotIn("<script", raw)
        self.assertIn("rule-second", (PROTO / "fixtures" / "bank.md").read_text())


if __name__ == "__main__":
    unittest.main()
