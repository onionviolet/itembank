#!/usr/bin/env python3
"""Synthetic native artifact adapter: private drafts and immutable responses."""
import contextlib
from concurrent.futures import ThreadPoolExecutor
import hashlib
import io
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from urllib.parse import unquote
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import evidence
import journal
import model
import notes
import runtime
from surfaces import evidence_cli, learner_artifacts as panel, session


class LearnerArtifact(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="learner-artifact-test-")
        self.root = Path(self.tmp.name)
        self.bank = self.root / "coding_boundary_unit.md"
        shutil.copyfile(ROOT / "fixtures/coding_boundary_unit.md", self.bank)
        self.note_root = self.root / "_notes" / "fictional-course"
        self.session_file = self.root / "_attempts" / "session_original.json"
        self.q = next(q for q in model.load(str(self.bank)) if q["type"] == "short")
        started = session.do_start(str(self.bank), {"type": "short", "count": 1, "seed": 0},
                                   "practice", str(self.session_file), False)
        self.sid = started["session_id"]
        self.args = dict(bank_path=str(self.bank), note_root=str(self.note_root),
            course_id="fictional-course", item_ref=self.q["id"], session_file=str(self.session_file))
        self.log = evidence.log_path(str(self.root))
        self.initial_events = list(evidence.events(self.log))
        self.current = panel.view(**self.args)

    def tearDown(self):
        self.tmp.cleanup()

    def body(self, **extra):
        draft = self.current["draft"] or {}
        result = {"item_ref": self.q["id"], "note_id": draft.get("note_id", ""),
            "session_id": self.sid, "kind": "proof",
            "notes_fingerprint": self.current["notes_fingerprint"] or "",
            "note_revision": draft.get("revision_id", ""),
            "content_revision": self.current["content_revision"] or "",
            "bank_revision": self.current["bank_revision"]}
        result.update(extra)
        return result

    def act(self, action, **extra):
        result = panel.apply(action, self.body(**extra), **self.args)
        self.current = result["view"]
        return result

    def save(self, text="Original fictional proof: include opening; exclude closing."):
        self.act("save", wording=text)
        return self.current["draft"]

    def submit(self):
        self.act("preview")
        self.act("submit", confirmed="yes")
        return self.current["submitted"][0]

    def page(self, **kwargs):
        return panel.render(self.current, action_url="/course/fictional-course/artifacts",
            panel_href="/course/fictional-course/artifacts?item_ref=q5&session_id=" + self.sid,
            return_href="/course/fictional-course/learn?objective=cs%3Aboundary-filtering#activity-original",
            **kwargs)

    def test_save_reopen_submit_mark_retract_and_revised_draft(self):
        original = "  Original <proof> π\n\ndef active(a, b, t):\n    return a <= t < b\n\n  "
        draft = self.save(original)
        self.assertEqual(list(evidence.events(self.log)), self.initial_events)
        self.assertEqual(notes.read_note_document(str(self.note_root))["sidecar"]["notes"][0]["learner_wording"], original)
        saved = runtime.read_session(str(self.session_file))
        self.assertEqual(saved["responses"], [])
        self.assertEqual(self.current["rubric_state"], "withheld")
        self.assertEqual(self.current["objective"], self.q["objective"])
        self.assertIn("Objective: " + self.q["objective"], self.page())
        self.assertNotIn(self.q["model"], self.page())
        row = self.submit()
        self.assertEqual(row["wording"], original)
        self.assertEqual(row["review"]["state"], "pending")
        event = evidence.event_by_id(self.log, row["event_id"])
        self.assertIsNone(event["score"])
        self.assertEqual(event["objective"], self.q["objective"])
        self.assertEqual(row["content_revision"], "sha256:" + hashlib.sha256(original.encode()).hexdigest())
        self.assertEqual(self.current["rubric"], self.q["rubric"])
        before_revision = draft["revision_id"]
        self.save(original + "Later revision.")
        self.assertNotEqual(self.current["draft"]["revision_id"], before_revision)
        self.assertEqual(self.current["submitted"][0]["wording"], original)
        self.assertIn("differs from this submitted original", self.page())
        mark = evidence.mark_event(self.sid, event["item_id"], event["item_ref"], event["event_id"], True,
            rubric=[{"point": self.q["rubric"][0], "pass": True}], notes="Synthetic human review")
        evidence.append_event(self.log, mark)
        self.assertEqual(session.do_next(str(self.session_file))["status"], "complete")
        self.current = panel.view(**self.args, note_id=draft["note_id"], kind="proof")
        self.assertEqual(self.current["submitted"][0]["review"]["state"], "settled")
        self.assertIn("met", self.page())
        with contextlib.redirect_stdout(io.StringIO()):
            evidence_cli.cmd_retract(SimpleNamespace(base=str(self.root), event_id=mark["event_id"], reason="Synthetic reviewer withdrawal"))
        self.current = panel.view(**self.args, note_id=draft["note_id"], kind="proof")
        self.assertEqual(self.current["submitted"][0]["review"]["state"], "pending")
        self.assertIsNone(evidence.event_by_id(self.log, row["event_id"])["score"])
        child = subprocess.run([sys.executable, __file__, "--reopen", str(self.root), draft["note_id"]],
            capture_output=True, text=True, check=True)
        reopened = json.loads(child.stdout)
        self.assertEqual(reopened["submitted"][0]["wording"], original)
        self.assertEqual(reopened["draft"]["learner_wording"], original + "Later revision.")
        self.assertEqual(reopened["submitted"][0]["review"]["state"], "pending")
        download = re.search(r'download="submitted-original.txt" href="([^"]+)"', self.page()).group(1)
        self.assertEqual(unquote(download.split(',', 1)[1]), original)
        self.assertEqual(len(self.current["export_losses"]), 2)
        exported = re.search(r'download="original-work-review.json" href="([^"]+)"', self.page()).group(1)
        exported = json.loads(unquote(exported.split(',', 1)[1]))
        self.assertEqual(exported['response_event'], evidence.event_by_id(self.log, row['event_id']))
        self.assertEqual(exported['response_event']['answer'], original)
        self.assertEqual([e['event_type'] for e in exported['review_events']], ['mark', 'retraction'])
        self.assertEqual(exported['current_authored_criteria']['points'], self.q['rubric'])
        self.assertIn('originating draft ID', exported['limitations'][0])
        self.assertNotIn('origin_note_id', exported['response_event'])
        self.assertNotIn(self.q['model'], json.dumps(exported))

    def test_json_like_text_is_exact_and_never_executed(self):
        self.save('  "123"\n')
        with patch("subprocess.Popen", side_effect=AssertionError("program must not execute")):
            row = self.submit()
        self.assertEqual(row["wording"], '  "123"\n')

    def test_preview_cancel_and_unconfirmed_submit_do_not_record(self):
        self.save()
        before = runtime.read_session(str(self.session_file))
        self.assertTrue(self.act("preview")["preview"])
        self.assertFalse(self.act("cancel")["preview"])
        with self.assertRaises(journal.JournalError) as caught:
            self.act("submit")
        self.assertEqual(caught.exception.code, "artifact.confirm")
        self.assertEqual(runtime.read_session(str(self.session_file)), before)
        self.assertEqual(list(evidence.events(self.log)), self.initial_events)

    def test_competing_edit_conflict_and_private_neighbors_preserved(self):
        document_id = notes.new_note_id()
        neighbor = notes.note_record("fictional-course", ["other"], "learner_question", "Private neighbor", [])
        neighbor["note_document_id"] = document_id
        notes.write_note_document(str(self.note_root), "fictional-course", "# Existing private text\nPrivate neighbor\n",
            {"schema_version": 1, "course_id": "fictional-course", "note_document_id": document_id, "notes": [neighbor]}, None)
        self.current = panel.view(**self.args)
        self.save()
        stale = self.body(wording="A competing stale edit")
        stale_submit = self.body(confirmed="yes")
        self.save("Winning revision")
        for action, body in (("save", stale), ("submit", stale_submit)):
            with self.assertRaises(journal.JournalError) as caught:
                panel.apply(action, body, **self.args)
            self.assertEqual(caught.exception.code, "notes.stale")
        doc = notes.read_note_document(str(self.note_root))
        self.assertTrue(doc["markdown"].startswith("# Existing private text\nPrivate neighbor\n"))
        self.assertEqual(doc["sidecar"]["notes"][0], neighbor)
        self.assertEqual(self.current["draft"]["learner_wording"], "Winning revision")
        self.assertEqual(list(evidence.events(self.log)), self.initial_events)

    def test_missing_rubric_preserves_pending_original(self):
        text = self.bank.read_text()
        start = text.index("RUBRIC:\n", text.index("Q5."))
        end = text.index("\nTRAP:", start)
        self.bank.write_text(text[:start] + "RUBRIC:\n" + text[end:])
        self.current = panel.view(**self.args)
        self.save()
        self.submit()
        self.assertEqual(self.current["rubric_state"], "missing")
        self.assertIn("Rubric missing", self.page())
        self.assertEqual(self.current["submitted"][0]["review"]["state"], "pending")

    def test_two_writers_have_one_winner_and_no_submission(self):
        self.save()
        base = self.body()
        def save(wording):
            try:
                panel.apply("save", dict(base, wording=wording), **self.args)
                return "saved"
            except journal.JournalError as exc:
                return exc.code
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(save, ["First competing draft", "Second competing draft"]))
        self.assertEqual(results.count("saved"), 1, results)
        self.assertEqual(results.count("notes.stale"), 1, results)
        doc = notes.read_note_document(str(self.note_root))
        self.assertIn(doc["sidecar"]["notes"][0]["learner_wording"], ["First competing draft", "Second competing draft"])
        self.assertEqual(list(evidence.events(self.log)), self.initial_events)

    def test_evidence_first_failure_preserves_original_without_resubmit(self):
        self.save("  Exact original\r\nSecond line\r\n")
        with patch("surfaces.session.write_session", side_effect=OSError("synthetic disk failure")):
            with self.assertRaises(OSError):
                self.act("submit", confirmed="yes")
        self.current = panel.view(**self.args, note_id=self.current["draft"]["note_id"])
        self.assertEqual(self.current["submitted"][0]["wording"], "  Exact original\r\nSecond line\r\n")
        self.assertFalse(self.current["can_submit"])
        with self.assertRaises(journal.JournalError) as caught:
            self.act("submit", confirmed="yes")
        self.assertEqual(caught.exception.code, "artifact.already_submitted")
        events = [e for e in evidence.events(self.log) if e.get("event_type") == "response"]
        self.assertEqual(len(events), 1)

    def test_changed_target_and_formal_sitting_refuse_without_write(self):
        self.save()
        stale = self.body(confirmed="yes")
        self.bank.write_text(self.bank.read_text().replace("Explain an unfamiliar boundary rule", "Explain a revised boundary rule"))
        with self.assertRaises(journal.JournalError) as caught:
            panel.apply("submit", stale, **self.args)
        self.assertEqual(caught.exception.code, "artifact.target_changed")
        self.current = panel.view(**self.args, note_id=self.current["draft"]["note_id"])
        self.assertTrue(self.current["target_changed"])
        self.assertEqual(self.current["rubric_state"], "withheld")
        self.assertEqual(list(evidence.events(self.log)), self.initial_events)
        sitting = runtime.read_session(str(self.session_file))
        sitting["mode"] = "exam"
        runtime.write_session(str(self.session_file), sitting)
        with self.assertRaises(journal.JournalError) as caught:
            panel.view(**self.args)
        self.assertEqual(caught.exception.code, "artifact.sitting")

    def test_readonly_no_session_and_script_free_form_contract(self):
        args = dict(self.args, session_file=None)
        self.current = panel.view(**args)
        self.assertFalse(self.note_root.exists())
        html = self.page(preserved_wording="</textarea><script>bad()</script>")
        self.assertIn("&lt;/textarea&gt;&lt;script&gt;bad()&lt;/script&gt;", html)
        self.assertIn('method="post"', html)
        self.assertIn('name="wording"', html)
        self.assertIn('id="artifact-return"', html)
        self.assertIn('objective=cs%3Aboundary-filtering#activity-original', html)
        self.assertNotIn("name=\"path\"", html)
        with self.assertRaises(journal.JournalError):
            panel.form_body({"action": ["save", "submit"]})
        with self.assertRaises(journal.JournalError):
            panel.form_body({"verdict": "true"})


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--reopen":
        root = Path(sys.argv[2])
        print(json.dumps(panel.view(str(root / "coding_boundary_unit.md"),
            str(root / "_notes" / "fictional-course"), "fictional-course", "q5",
            str(root / "_attempts" / "session_original.json"), sys.argv[3], "proof")))
    else:
        unittest.main()
