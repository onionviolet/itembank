#!/usr/bin/env python3
"""A source-grounded lesson correction stays reviewable and reversible."""
import os
import sys
import tempfile
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))

from agent_operation_roundtrip import _Stub, local_profile  # noqa: E402
import course  # noqa: E402
import course_package  # noqa: E402
import identity  # noqa: E402
import journal  # noqa: E402
from surfaces import agent_operation as ao  # noqa: E402


def check_lesson_correction():
    with tempfile.TemporaryDirectory(prefix="itembank-author-review-") as base:
        course.create_course(base, "Synthetic author review", "human", "tester")
        rights = {operation: "granted" for operation in identity.RIGHTS_OPERATIONS}
        source = Path(base, "sources", "direct-reading.md")
        source.parent.mkdir()
        source.write_text("# Direct reading\n\nThis source stays a direct reading.\n",
                          encoding="utf-8")
        source_row = journal.op_link(base, "source", "sources/direct-reading.md",
                                     "human", "tester", rights=rights)
        journal.op_adopt(base, source_row["object_id"],
                         source_row["fingerprint"], "human", "tester")
        target = Path(base, "lessons", "missing-lesson.md")
        target.parent.mkdir()
        original = "## LESSON\n\n### Earlier note\n\nKeep this paragraph.\n"
        target.write_text(original, encoding="utf-8")
        lesson_row = journal.op_link(base, "lesson", "lessons/missing-lesson.md",
                                     "human", "tester", rights=rights)
        journal.op_adopt(base, lesson_row["object_id"],
                         lesson_row["fingerprint"], "human", "tester")
        source_before = source.read_bytes()
        first = "The draft explanation has a mistake. [Source: direct-reading.md]"
        corrected = "The corrected explanation cites the source. [Source: direct-reading.md]"
        draft = ("## LESSON\n\n### New concept\n\n" + first +
                 "\n\nA second paragraph remains exactly as drafted.\n")
        citation = "source:direct-reading.md"
        stub = _Stub(candidate={"draft": draft, "citations": [citation],
                                "validation": {"state": "passed", "findings": []}})
        settings = {"model_backend": {"active": "local-qwen",
                                     "profiles": [local_profile(stub.port)]},
                    "auditor_autonomy": "draft_and_approve",
                    "agent_runs": {"author-lesson": {
                        "target": "lessons/missing-lesson.md", "kind": "lesson",
                        "request": "Draft only the missing lesson.",
                        "citations": [citation],
                        "source_paths": ["sources/direct-reading.md"]}}}
        try:
            proposed = ao.start("author-lesson", settings, base)
        finally:
            stub.close()
        assert proposed["disposition"] == "proposed", proposed
        assert proposed["validation"]["state"] == "passed", proposed
        pid = proposed["proposal_id"]
        assert target.read_text(encoding="utf-8") == original
        before_preview = ao.lesson_preview(base, pid)
        assert first in before_preview["html"]
        revised = ao.revise(base, pid, first, corrected,
                            before_preview["draft_fingerprint"])
        assert corrected in revised["draft"]
        assert "A second paragraph remains exactly as drafted." in revised["draft"]
        assert first not in revised["draft"]
        assert revised["validation"] == {"state": "not_run", "findings": []}
        assert ao.status(base, pid)["validation"] == revised["validation"]
        assert target.read_text(encoding="utf-8") == original
        try:
            ao.revise(base, pid, corrected, first,
                      before_preview["draft_fingerprint"])
        except ValueError as exc:
            assert str(exc) == "agent.draft_stale", exc
        else:
            raise AssertionError("stale paragraph edit was accepted")
        preview = ao.lesson_preview(base, pid)
        assert corrected in preview["html"]
        assert "<section" in preview["html"]
        assert preview["markdown"] == revised["draft"]
        assert preview["citations"] == [citation]
        assert any(corrected in line for line in preview["diff"]["lines"])
        accepted = ao.accept(pid, settings, base=base, reviewer="author")
        assert accepted["disposition"] == "accepted", accepted
        assert accepted["validation"] == revised["validation"]
        assert target.read_text(encoding="utf-8") == revised["draft"]
        assert source.read_bytes() == source_before
        reopened = ao.status(base, pid)
        assert reopened["entry_id"] == accepted["entry_id"]
        with tempfile.TemporaryDirectory(prefix="itembank-author-package-") as outside:
            package = os.path.join(outside, "package")
            destination = os.path.join(outside, "restored")
            course_package.export_package(base, base, package)
            os.makedirs(destination)
            course_package.restore_package(package, destination, "human", "tester")
            restored_lesson = Path(destination, "lessons", "missing-lesson.md")
            restored_source = Path(destination, "sources", "direct-reading.md")
            assert restored_lesson.read_text(encoding="utf-8") == revised["draft"]
            assert restored_source.read_bytes() == source_before
        undone = ao.undo(base, pid, reviewer="author")
        assert undone["restored_byte_identical"] is True
        assert target.read_text(encoding="utf-8") == original
        assert source.read_bytes() == source_before


def check_changed_source_refuses_accept():
    with tempfile.TemporaryDirectory(prefix="itembank-author-stale-") as base:
        source = Path(base, "source.md")
        source.write_text("Accepted source text.\n", encoding="utf-8")
        target = Path(base, "lesson.md")
        target.write_text("## LESSON\n\n### Existing\n\nOld.\n", encoding="utf-8")
        before = target.read_bytes()
        citation = "source:source.md"
        stub = _Stub(candidate={"draft": "## LESSON\n\n### New\n\nA cited draft.\n",
                                "citations": [citation]})
        settings = {"model_backend": {"active": "local-qwen",
                                     "profiles": [local_profile(stub.port)]},
                    "auditor_autonomy": "draft_and_approve",
                    "agent_runs": {"author-lesson": {
                        "target": "lesson.md", "kind": "lesson",
                        "request": "Draft a lesson.", "citations": [citation],
                        "source_paths": ["source.md"]}}}
        try:
            proposed = ao.start("author-lesson", settings, base)
        finally:
            stub.close()
        assert proposed["disposition"] == "proposed", proposed
        source.write_text("The source changed after drafting.\n", encoding="utf-8")
        settled = ao.accept(proposed["proposal_id"], settings, base=base)
        assert settled["code"] == "agent.source_stale", settled
        assert settled["disposition"] == "conflicted"
        assert target.read_bytes() == before


def check_keyed_content_refused():
    for draft in ("## LESSON\n\n### Topic\n\nCORRECT: B\n",
                  "## LESSON\n\n### Topic\n\nQ1. Secret answer\n",
                  "## LESSON\n\n### Topic\n\nSafe prose.\n\n## ANSWER KEY\n\nB\n",
                  "CORRECT: B\n\n## LESSON\n\n### Topic\n\nSafe prose.\n",
                  "Q1. Secret answer\n\n## LESSON\n\n### Topic\n\nSafe prose.\n",
                  "## ANSWER KEY\n\nB\n\n## LESSON\n\n### Topic\n\nSafe prose.\n"):
        try:
            ao._lesson_preview_body(draft)
        except ValueError as exc:
            assert str(exc) == "agent.lesson_keyed_content", exc
        else:
            raise AssertionError("keyed content entered a lesson preview")


if __name__ == "__main__":
    check_lesson_correction()
    check_changed_source_refuses_accept()
    check_keyed_content_refused()
    print("agent lesson revision roundtrip passed")
