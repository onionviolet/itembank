#!/usr/bin/env python3
"""Unregistered P5 D6 authority join on fictional accepted readings only.

This probes the proposed reference against existing owners. It does not add a
graph field, route, scorer, source transcript, or assessment format.
"""
import copy
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import course
import evidence
import journal
import reading
import runtime
import reading_ops_roundtrip as reading_fixture


def resolve_proposed_ref(base, ref, expected_course_fingerprint):
    """Test-only admission join; a production public resolver is still needed."""
    if (type(ref) is not dict or set(ref) != {"course_id", "occurrence_id", "revision_id"}
            or any(type(value) is not str or not value for value in ref.values())):
        raise ValueError("Use the exact three opaque accepted reading identities.")
    request = dict(expected_fingerprint=expected_course_fingerprint,
                   occurrence_id=ref["occurrence_id"], revision_id=ref["revision_id"])
    accepted, occurrence = reading._current(base, request)
    if accepted["object_id"] != ref["course_id"]:
        raise ValueError("The reference does not name this admitted course.")
    return request, occurrence


class RichPracticeReadingReadiness(unittest.TestCase):
    setUp = reading_fixture.ReadingOperations.setUp
    run_op = reading_fixture.ReadingOperations.run_op
    read = reading_fixture.ReadingOperations.read
    bind = reading_fixture.ReadingOperations.bind
    values = reading_fixture.ReadingOperations.values
    create = reading_fixture.ReadingOperations.create
    edit = reading_fixture.ReadingOperations.edit

    def reference(self, receipt):
        occurrence = receipt["occurrence"]
        return dict(course_id=self.read()["object_id"],
                    occurrence_id=occurrence["occurrence_id"],
                    revision_id=occurrence["revision_id"])

    def resolve(self, ref, expected=None):
        return resolve_proposed_ref(self.base, ref,
                                    self.read()["fingerprint"] if expected is None else expected)

    def snapshot(self):
        return {str(path.relative_to(self.base)): path.read_bytes()
                for path in Path(self.base).rglob("*") if path.is_file()}

    def events(self):
        path = evidence.log_path(self.base)
        return list(evidence.live_events(path)) if Path(path).exists() else []

    def confirmed(self, ref):
        request, _ = self.resolve(ref)
        result = reading.confirm(self.base, dict(request, confirmation="read"))
        return dict(request, intent_id=result["intent_id"])

    def refused_without_mutation(self, ref, expected=None):
        before = self.snapshot()
        with self.assertRaises((ValueError, course.CourseError)):
            self.resolve(ref, expected)
        self.assertEqual(self.snapshot(), before)

    def test_exact_admitted_identity_and_read_only_resolution(self):
        ref = self.reference(self.create())
        before = self.snapshot()
        request, occurrence = self.resolve(ref)
        self.assertEqual(occurrence["occurrence_id"], ref["occurrence_id"])
        self.assertEqual(occurrence["revision_id"], ref["revision_id"])
        self.assertEqual(request["expected_fingerprint"], self.read()["fingerprint"])
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.events(), [])
        for key in ref:
            changed = copy.deepcopy(ref)
            changed[key] = "0" * 16
            self.refused_without_mutation(changed)
            changed[key] = []
            self.refused_without_mutation(changed)
        self.refused_without_mutation(dict(ref, activity_id="assessment-node"))
        self.refused_without_mutation({key: value for key, value in ref.items() if key != "course_id"})
        self.refused_without_mutation(ref, "")
        self.refused_without_mutation(ref, "sha256:" + "0" * 64)

    def test_two_occurrences_do_not_share_reported_read_or_scores(self):
        first = self.create()
        values = self.values()
        values["binding_ref"] = first["binding_ref"]
        second = self.run_op("create_reading", expected_fingerprint=self.read()["fingerprint"],
                             values=values, title="Separate source reading", activation="Library")
        a, b = self.reference(first), self.reference(second)
        self.assertEqual(self.resolve(a)[1]["source_ref"], self.resolve(b)[1]["source_ref"])
        with patch.object(runtime, "score_response", side_effect=AssertionError("reading was scored")):
            request = self.confirmed(a)
            self.assertEqual(self.events(), [])
            result = reading.declare(self.base, request)
        event = result["event"]
        self.assertEqual(event["occurrence_id"], a["occurrence_id"])
        self.assertEqual(event["occurrence_revision_id"], a["revision_id"])
        self.assertEqual(len(self.events()), 1)
        for field in ("correct", "score", "mastery", "answer", "bank"):
            self.assertNotIn(field, event)
        state = evidence.reading_state(evidence.log_path(self.base), b["course_id"],
                                       b["occurrence_id"], b["revision_id"])
        self.assertEqual(state["state"], "not-reported")
        with self.assertRaises(course.CourseError):
            reading.confirm(self.base, dict(self.resolve(b)[0], confirmation="read"), "model")
        with self.assertRaises(course.CourseError):
            reading.declare(self.base, dict(self.resolve(b)[0], intent_id="0" * 16))

    def test_revision_refusal_and_exact_journal_undo(self):
        first = self.create()
        ref = self.reference(first)
        before = self.snapshot()
        old_course = self.read()["fingerprint"]
        revised = self.edit("revise_reading", first, changes={"purpose": "Changed synthetic demand"})
        newer = self.reference(revised)
        self.refused_without_mutation(ref, old_course)
        self.refused_without_mutation(ref)
        self.assertEqual(self.resolve(newer)[1]["supersedes_revision_id"], ref["revision_id"])
        self.assertEqual(self.events(), [])
        journal.undo(self.base, revised["entry_id"], "human", "readiness")
        self.assertEqual(Path(course.sidecar_path(self.base)).read_bytes(), before[course.COURSE_SIDECAR_FILENAME])
        self.assertEqual(self.resolve(ref)[1]["revision_id"], ref["revision_id"])
        self.refused_without_mutation(newer)

    def test_rights_unavailable_and_changed_source_preserve_reference(self):
        ref = self.reference(self.create())
        original = copy.deepcopy(ref)
        source = Path(self.base) / "sources/example.md"
        raw = source.read_bytes()
        for state in ("unknown", "denied"):
            journal.op_grant_rights(self.base, self.source_id, {"read": state},
                                    self.source_fp, "human", "readiness")
            self.refused_without_mutation(ref)
        journal.op_grant_rights(self.base, self.source_id, {"read": "granted"},
                                self.source_fp, "human", "readiness")
        source.write_bytes(raw + b"Changed source.\n")
        self.refused_without_mutation(ref)
        source.unlink()
        self.refused_without_mutation(ref)
        source.write_bytes(raw)
        self.assertEqual(self.resolve(ref)[1]["revision_id"], ref["revision_id"])
        self.assertEqual(ref, original)
        self.assertEqual(self.events(), [])

    def test_first_declaration_rechecks_source_and_replay_preserves_receipt(self):
        ref = self.reference(self.create())
        request = self.confirmed(ref)
        source = Path(self.base) / "sources/example.md"
        raw = source.read_bytes()
        source.write_bytes(raw + b"Changed after confirmation.\n")
        before = self.snapshot()
        with self.assertRaises(course.CourseError):
            reading.declare(self.base, request)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.events(), [])
        source.write_bytes(raw)
        first = reading.declare(self.base, request)
        source.unlink()
        replay = reading.declare(self.base, request)
        self.assertEqual(replay["status"], "already_recorded")
        self.assertEqual(replay["event_id"], first["event_id"])
        self.assertEqual(replay["availability"]["state"], "source-unavailable")
        self.assertEqual(len(self.events()), 1)
        self.refused_without_mutation(ref)

    def test_fresh_process_admission_and_concurrent_declaration(self):
        ref = self.reference(self.create())
        expected = self.read()["fingerprint"]
        before = self.snapshot()
        proc = subprocess.run([sys.executable, __file__, "--probe", self.base,
                               json.dumps(ref), expected], cwd=ROOT, capture_output=True,
                              text=True, timeout=30)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        result = json.loads(proc.stdout)
        self.assertEqual(result["revision_id"], ref["revision_id"])
        self.assertEqual(self.snapshot(), before)
        request = self.confirmed(ref)
        args = [sys.executable, __file__, "--declare", self.base, json.dumps(request)]
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(subprocess.run, args, cwd=ROOT,
                                       capture_output=True, text=True, timeout=30) for _ in range(2)]
            processes = [future.result() for future in futures]
        for process in processes:
            self.assertEqual(process.returncode, 0, process.stderr)
        results = [json.loads(process.stdout) for process in processes]
        self.assertEqual(results[0]["event_id"], results[1]["event_id"])
        self.assertEqual(sorted(result["status"] for result in results), ["already_recorded", "recorded"])
        self.assertEqual(len(self.events()), 1)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--probe":
        _, occurrence = resolve_proposed_ref(sys.argv[2], json.loads(sys.argv[3]), sys.argv[4])
        print(json.dumps({key: occurrence[key] for key in ("occurrence_id", "revision_id")}))
    elif len(sys.argv) > 1 and sys.argv[1] == "--declare":
        print(json.dumps(reading.declare(sys.argv[2], json.loads(sys.argv[3]))))
    else:
        unittest.main()
