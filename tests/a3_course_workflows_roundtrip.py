#!/usr/bin/env python3
"""A3 readiness, editable treatments and durable review over synthetic files."""
import hashlib
import html
import os
from pathlib import Path
import shutil
import sys
import tempfile
from datetime import datetime, timezone, timedelta
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

import course
import evidence
import graph
import identity
import journal
import model
from surfaces import agent_operation as ao, course_workbench as cw, retention_view, session
from course_ops_roundtrip import seed_17b_journal
from formal_assessment_connected_roundtrip import temporary_bank


def tree_hash(base):
    return {str(path.relative_to(base)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in Path(base).rglob('*') if path.is_file()}


def expect_value_error(call, code):
    try:
        call()
    except ValueError as exc:
        assert str(exc) == code, exc
    else:
        raise AssertionError("Expected " + code)


def seed(base):
    course.create_course(base, "Synthetic course workflow", "human", "test")
    doc = course.read_course(base)["doc"]
    first = graph.add_objective(doc, "Read a clear source", objective_id="synthetic:read")["id"]
    second = graph.add_objective(doc, "Apply the concept", objective_id="synthetic:apply")["id"]
    raw = "# Source\n\nA source stays useful as direct reading.\n"
    Path(base, "source.md").write_text(raw, encoding="utf-8")
    source = journal.op_link(base, "source", "source.md", "human", "test",
                             rights={"read": "granted", "transform": "granted"})
    journal.op_adopt(base, source["object_id"], source["fingerprint"], "human", "test")
    graph.add_source(doc, source["object_id"], "Synthetic source")
    course.write_course(base, doc, course.read_course(base)["fingerprint"], "human", "test")
    course.bind_treatment(base, first, source["object_id"], "direct-reading", "Source", "covered", "high", "human", "test")
    return first, second, source


def check_readiness():
    with tempfile.TemporaryDirectory(prefix="a3-ready-") as base:
        shutil.copytree(ROOT / "course_fixture_17b", base, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("_journal", "_evidence", "_attempts"))
        seed_17b_journal(base)
        banks = [("unit3_bank", os.path.join(base, "unit3_bank.md"))]
        before = tree_hash(base)
        payload = cw.readiness(base, banks)
        assert payload["read_only"] and payload["state"] != "error", payload
        assert any(r["kind"] == "bank" and r["state"] == "clean" for r in payload["rows"]), payload
        assert tree_hash(base) == before
        os.unlink(os.path.join(base, "sources", "fen_hydrology_field_notes.md"))
        bank = Path(base, "unit3_bank.md")
        bank.write_text(bank.read_text().replace("[LESSON-SRC: unit3_lesson.md]", "[LESSON-SRC: absent.md]") +
                        "\nQ99. Broken synthetic item\n[TYPE: mc]\n[OBJECTIVE: synthetic:missing]\n[LESSON-REF: Absent heading]\nA. One\nB. Two\nCORRECT: A\n", encoding="utf-8")
        read = course.read_course(base)
        doc = read["doc"]
        graph.add_binding(doc, "treatment", doc["objectives"][0]["id"], doc["sources"][0]["source_object_id"],
                          treatment_kind="guided-lesson", locator="missing-lesson.md", state="unknown", confidence="unknown")
        course.write_course(base, doc, read["fingerprint"], "human", "test")
        before = tree_hash(base)
        broken = cw.readiness(base, banks)
        assert broken["state"] == "needs-review", broken
        assert any(r["kind"] == "source" and r["state"] == "missing" for r in broken["rows"])
        assert any(r["code"] == "binding.artifact_missing" for r in broken["rows"])
        assert any(r["kind"] in ("lesson-link", "bank") and r["state"] == "invalid" for r in broken["rows"])
        assert tree_hash(base) == before
        with mock.patch.object(model, "load", side_effect=OSError("failed check")):
            failed = cw.readiness(base, banks)
        assert failed["state"] == "error" and any(r["code"] == "bank.check_failed" for r in failed["rows"])
        assert "failed check" not in cw.readiness_panel(failed)
        assert tree_hash(base) == before


def check_proposal():
    with tempfile.TemporaryDirectory(prefix="a3-imported-outline-") as base:
        first, second, _source = seed(base)
        read = course.read_course(base)
        doc = read["doc"]
        doc["objectives"][0]["origin"] = "imported"
        doc["objectives"][0]["import_version"] = "synthetic-v1"
        course.write_course(base, doc, read["fingerprint"], "human", "test")
        before = tree_hash(base)
        expect_value_error(lambda: ao.propose_course_outline(base, [], [second, first]), "agent.imported_outline_immutable")
        assert tree_hash(base) == before
    with tempfile.TemporaryDirectory(prefix="a3-outline-") as base:
        first, second, source = seed(base)
        accepted = Path(base, "course-graph.md").read_bytes()
        direct = course.read_course(base)["doc"]["bindings"][0].copy()
        choice = {"objective": second, "source": source["object_id"], "treatment": "guided-lesson", "locator": "Source"}
        form = {"expected_course_fingerprint": course.read_course(base)["fingerprint"],
                "order-" + first: "1", "order-" + second: "2",
                "treatment-" + second: choice["treatment"], "source-" + second: choice["source"],
                "locator-" + second: choice["locator"]}
        expect_value_error(lambda: cw.outline_action(base, "propose", dict(form, target="elsewhere.md"), {}), "agent.invalid_outline_fields")
        pending = cw.outline_action(base, "propose", form, {})
        pid = pending["proposal_id"]
        assert Path(base, "course-graph.md").read_bytes() == accepted
        assert graph.parse_course(pending["draft"])["bindings"][0] == direct
        edited = dict(choice, treatment="worked-example")
        revised = ao.propose_course_outline(base, [edited], [second, first], pid, ao.draft_fingerprint(pending["draft"]))
        expect_value_error(lambda: ao.propose_course_outline(base, [choice], proposal_id=pid,
                           expected_draft_fingerprint=ao.draft_fingerprint(pending["draft"])), "agent.draft_stale")
        assert graph.parse_course(revised["draft"])["bindings"][0] == direct
        pane = cw.outline_panel(base, course.read_course(base)["doc"], pid)
        assert 'method="post"' in pane and "Keep adequate direct readings" in pane and "Cancel proposal" in pane
        assert ao.status(base, pid)["draft"] == revised["draft"]
        expect_value_error(lambda: ao.accept(pid, {"auditor_autonomy": "draft_and_approve"}, base=base,
                          expected_draft_fingerprint=ao.draft_fingerprint(pending["draft"])), "agent.draft_stale")
        result = cw.outline_action(base, "accept", {"proposal_id": pid,
                                   "expected_draft_fingerprint": ao.draft_fingerprint(revised["draft"])},
                                   {"auditor_autonomy": "draft_and_approve"}, reviewer="test")
        assert result["disposition"] == "accepted", result
        assert course.read_course(base)["doc"]["bindings"][0] == direct
        assert ao.accept(pid, {"auditor_autonomy": "draft_and_approve"}, base=base)["entry_id"] == result["entry_id"]
        assert cw.outline_action(base, "undo", {"proposal_id": pid}, {})["restored_byte_identical"]
        assert Path(base, "course-graph.md").read_bytes() == accepted
        rights_pending = ao.propose_course_outline(base, [choice])
        current_source = journal.read_registry(base)[source["object_id"]]
        journal.op_grant_rights(base, source["object_id"], {"transform": "denied"}, current_source["fingerprint"], "human", "test")
        refused = ao.accept(rights_pending["proposal_id"], {"auditor_autonomy": "draft_and_approve"}, base=base)
        assert refused["code"] == "agent.treatment_right_not_granted", refused
        assert Path(base, "course-graph.md").read_bytes() == accepted
        current_source = journal.read_registry(base)[source["object_id"]]
        journal.op_grant_rights(base, source["object_id"], {"transform": "granted"}, current_source["fingerprint"], "human", "test")
        stale_course = ao.propose_course_outline(base, [choice])
        read = course.read_course(base)
        doc = read["doc"]
        doc["header"]["title"] = "A separate accepted course edit"
        course.write_course(base, doc, read["fingerprint"], "human", "test")
        changed = Path(base, "course-graph.md").read_bytes()
        result = ao.accept(stale_course["proposal_id"], {"auditor_autonomy": "draft_and_approve"}, base=base)
        assert result["disposition"] == "conflicted" and Path(base, "course-graph.md").read_bytes() == changed
        accepted = changed
        canceled = ao.propose_course_outline(base, [choice])
        assert ao.reject(base, canceled["proposal_id"])["disposition"] == "rejected"
        assert Path(base, "course-graph.md").read_bytes() == accepted
        pending = ao.propose_course_outline(base, [choice])
        Path(base, "source.md").write_text("Changed source\n", encoding="utf-8")
        result = ao.accept(pending["proposal_id"], {"auditor_autonomy": "draft_and_approve"}, base=base)
        assert result["code"] == "agent.source_stale", result
        assert Path(base, "course-graph.md").read_bytes() == accepted


def check_review():
    with tempfile.TemporaryDirectory(prefix="a3-review-") as root:
        base = os.path.join(root, "course")
        os.mkdir(base)
        first, second, source = seed(base)
        bank = temporary_bank(base)
        Path(bank).write_text(Path(bank).read_text().replace(
            "# Synthetic formal assessment\n", "# Synthetic formal assessment\n\n## LESSON\n\n### Source explanation\n\nSynthetic source-backed explanation. [Source: source.md]\n"), encoding="utf-8")
        # Keep a coherent synthetic lesson alongside the bank and link the
        # actual question objective, not an inferred heading match.
        questions = model.load(bank)
        objective = questions[0]["objective"]
        read = course.read_course(base)
        doc = read["doc"]
        graph.add_objective(doc, "Synthetic assessment target", objective_id=objective)
        graph.add_binding(doc, "treatment", objective, source["object_id"], treatment_kind="guided-lesson",
                          locator="formal_synthetic.md", state="covered", confidence="high", rights_snapshot="granted")
        course.write_course(base, doc, read["fingerprint"], "human", "test")
        stem = "formal_synthetic"
        banks = [(stem, bank)]
        attempt = os.path.join(root, "_attempts", "session_a3.json")
        started = session.do_start(bank, {"count": 2, "seed": 0, "selection_mode": "exam"}, "exam", attempt, False)
        sid = started["session_id"]
        view = started
        for _ in range(2):
            q = view["item"]
            answer = "PRIVATE prose stays pending" if q["type"] == "short" else "A"
            response = session.do_submit(attempt, answer, None)
            view = response["next"]
            if response["accepted"] and q["type"] != "short":
                interim = cw.review_history(root, base, course.read_course(base)["doc"], banks)
                markup = retention_view.course_review_history(interim)
                assert "CORRECT:" not in markup and "PRIVATE" not in markup
                assert interim["rows"][0]["status"] == "feedback-withheld"
                assert interim["counts"]["settled"] == 0 and interim["counts"]["missed"] == 0
        doc = course.read_course(base)["doc"]
        before = tree_hash(root)
        payload = cw.review_history(root, base, doc, banks)
        assert payload["counts"]["pending"] == 1, payload
        assert payload["counts"]["settled"] == 1 and payload["counts"]["missed"] == 1, payload
        assert tree_hash(root) == before
        assert cw.review_history(root, base, doc, banks)["rows"] == payload["rows"]
        page = html.unescape(retention_view.course_review_history(payload))
        assert "pending" in page and "Source:" in page and "Lesson:" in page
        assert "return=" in page and sid in page
        assert "PRIVATE prose" not in page and "WHY BEST" not in page
        ambiguous = cw.review_history(root, base, doc, banks + [("alias", bank)])
        assert ambiguous["state"] == "error" and not ambiguous["rows"]
        for index, answer in enumerate(("A", "B")):
            other = os.path.join(root, "_attempts", "session_due_%d.json" % index)
            session.do_start(bank, {"count": 1, "seed": 0, "selection_mode": "exam", "type_counts": {"mc": 1}}, "exam", other, False)
            session.do_submit(other, answer, None)
        cutoff = (datetime.now(timezone.utc) + timedelta(days=10)).isoformat()
        later = cw.review_history(root, base, doc, banks, cutoff=cutoff)
        assert later["counts"]["settled"] == 3 and later["counts"]["pending"] == 1, later
        assert later["due"]["objectives"][objective]["due"]
        assert "Due objective work" in retention_view.course_review_history(later)
        active = os.path.join(root, "_attempts", "session_active.json")
        running = session.do_start(bank, {"count": 2, "seed": 0, "selection_mode": "exam"}, "exam", active, False)
        session.do_submit(active, "A", None)
        history = cw.review_history(root, base, doc, banks)
        active_row = next(r for r in history["rows"] if r["session_id"] == running["session_id"])
        assert active_row["resume_href"] and running["session_id"] in active_row["resume_href"]
        assert active_row["status"] == "feedback-withheld" and not active_row["context_links"]
        assert session.do_next(active)["item"]["type"] == "short"
        # Malformed evidence must not become a clean zero-findings view.
        with open(evidence.log_path(base), "a", encoding="utf-8") as handle:
            handle.write("not JSON\n")
        assert cw.review_history(root, base, doc, banks)["state"] == "error"


if __name__ == "__main__":
    check_readiness()
    check_proposal()
    check_review()
    print("A3 course workflows: read-only readiness, editable CAS proposal, cancel/stale/accept/restart/undo, durable review passed")
