#!/usr/bin/env python3
"""Truthful evidence state and exact next-activity links in the native course UI."""
import html
import os
import shutil
import sys
import tempfile
from types import SimpleNamespace
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from surfaces import course_workbench, daemon, ia
import evidence


def check(value, message):
    if not value:
        raise AssertionError(message)


def counts(state, responses=0):
    unavailable = state == "unavailable"
    return {"state": state, "complete": state in ("empty", "ready"),
            "issues": ["Synthetic record cannot be read."] if state in ("unavailable", "incomplete") else [],
            "responses": None if unavailable else responses,
            "marks": None if unavailable else 0,
            "sessions": None if unavailable else (1 if responses else 0),
            "events": None if unavailable else responses}


def check_truthful_evidence_states(handler, root, doc):
    with mock.patch("course.read_course", return_value={"doc": doc}):
        for state_name in ("empty", "ready", "incomplete", "unavailable"):
            reading = counts(state_name, 2 if state_name in ("ready", "incomplete") else 0)
            with mock.patch.object(daemon.evidence, "course_counts", return_value=reading, create=True):
                lead, rows = daemon._course_area_rows(
                    handler, {"area": "evidence", "course_id": "synthetic"}, root)
                overview, _ = daemon._course_area_rows(
                    handler, {"area": "overview", "course_id": "synthetic"}, root)
            text = lead + daemon._course_rows_html(rows)
            if state_name == "empty":
                check("No assessment response history" in text and
                      "No response history" in overview, "empty history lost its stated state")
            elif state_name == "unavailable":
                check("Counts are unknown" in text and "counts are unknown" in overview,
                      "unreadable history did not state unknown counts")
                check("0 response" not in text + overview,
                      "unreadable history displayed a clean zero")
                check('href="#course-review-history"' in text and "Reload evidence" in text,
                      "unreadable history has no inspection/reload recovery")
            elif state_name == "incomplete":
                check("partial" in text and "readable records" in text + overview,
                      "incomplete history presented complete counts")
            else:
                check("2 responses recorded" in text and "2 recorded responses" in overview,
                      "readable response counts were omitted")


def check_guidance_links(handler, root, doc):
    exact = "/quiz/admitted_alias?mode=practice&session=saved-exact&course=synthetic"
    reason = "One released practice response needs another look <safely>."
    base = {"title": "Read the linked explanation", "reason": reason,
            "href": "/lesson/admitted_alias#review", "objective": "synthetic:flow",
            "resume_href": exact, "answer": "PRIVATE_RESPONSE_SENTINEL"}
    with mock.patch("course.read_course", return_value={"doc": doc}):
        for kind in ("review", "resume", "pending", "unavailable"):
            projection = dict(base, kind=kind)
            if kind == "resume":
                projection["href"] = exact
            if kind == "pending":
                projection.update(title="Inspect pending review", reason="This prose response still awaits review.")
            with mock.patch.object(course_workbench, "course_guidance", return_value=projection, create=True):
                page = daemon._course_guidance_html(
                    handler, {"course_id": "synthetic"}, root)
            check('data-course-guidance="%s"' % kind in page, "next activity lost its state")
            check("Why this activity:" in page and "Current objective:" in page,
                  "next activity lacks its reason or objective")
            check("Explain an unfamiliar learning flow" in page,
                  "objective identity was not connected to the course statement")
            check('data-course-resume' in page and html.escape(exact, quote=True) in page,
                  "exact saved sitting return was lost")
            check("PRIVATE_RESPONSE_SENTINEL" not in page,
                  "guidance rendered a private field")
            if kind == "review":
                check("&lt;safely&gt;" in page and "<safely>" not in page,
                      "guidance reason was not escaped")
            if kind == "pending":
                check("awaits review" in page and "miss" not in page,
                      "pending prose was described as a miss")
            if kind == "unavailable":
                check("Reload course" in page, "recovery state has no safe reload")


def check_start_uses_bound_path(handler, root, doc):
    guidance = {"kind": "start", "title": "Open Learn", "reason": "Begin with accepted course material.",
                "href": "/course/synthetic/learn", "objective": None}
    with mock.patch("course.read_course", return_value={"doc": doc}), \
            mock.patch.object(daemon.evidence, "course_counts", return_value=counts("empty"), create=True), \
            mock.patch.object(course_workbench, "course_guidance", return_value=guidance, create=True):
        _lead, path = daemon._course_area_rows(
            handler, {"area": "overview", "course_id": "synthetic"}, root)
        quizzes = [row for row in path if row.get("href", "").startswith("/quiz/")]
        check(len(quizzes) == 1 and "/quiz/admitted_alias?" in quizzes[0]["href"],
              "overview used an arbitrary unbound bank for practice")
        for href, reason in (("/lesson/admitted_alias", "Begin with the current linked lesson."),
                             ("/quiz/admitted_alias?mode=practice&course=synthetic", "Bound practice is the first available activity."),
                             ("/course/synthetic/learn", "Inspect assigned activities before starting.")):
            chosen = dict(guidance, href=href, reason=reason)
            with mock.patch.object(course_workbench, "course_guidance", return_value=chosen):
                page = daemon._course_guidance_html(handler, {"course_id": "synthetic"}, root)
            check(html.escape(href, quote=True) in page and reason in page,
                  "renderer overrode the engine's admitted start route or reason")


def check_saved_sitting_admission(handler, root, doc):
    bank = handler.banks["admitted_alias"]
    saved = {"session_id": "saved-exact", "bank": bank, "status": "active",
             "mode": "practice", "position": 1, "total": 3}
    state = {"area": "overview", "area_label": "Overview", "course_id": "synthetic",
             "course_name": "Synthetic flow", "nav": [], "notice": "No activity yet."}
    guidance = {"kind": "resume", "title": "Resume practice", "reason": "Continue the admitted saved sitting.",
                "href": "/quiz/admitted_alias?mode=practice&session=saved-exact&course=synthetic",
                "objective": None}
    with mock.patch("course.read_course", return_value={"doc": doc}), \
            mock.patch.object(daemon.evidence, "course_counts", return_value=counts("empty"), create=True), \
            mock.patch.object(course_workbench, "course_guidance", return_value=guidance, create=True), \
            mock.patch.object(daemon, "_course_area_extra", return_value=""), \
            mock.patch.object(ia, "_course_resume_state", return_value={"state": "active", "sessions": [saved]}):
        page = daemon._course_frame(handler, state, {"href": "/courses", "label": "Back to courses"}, root)
        check("/quiz/admitted_alias?" in page and "/quiz/practice?" not in page,
              "saved sitting route guessed the bank stem from its filename")
        check(page.index('id="course-guidance"') < page.index('id="saved-sittings"'),
              "saved sitting list displaced the next activity")
        unknown = dict(saved, bank=os.path.join(root, "unadmitted", "practice.md"), session_id="unadmitted")
        with mock.patch.object(ia, "_course_resume_state", return_value={"state": "unavailable", "sessions": [unknown]}):
            page = daemon._course_frame(handler, state, {"href": "/courses", "label": "Back to courses"}, root)
        check("Saved sitting is unavailable" in page and "session=unadmitted" not in page,
              "an unadmitted same-basename bank gained a Resume link")


def check_missed_review_recovery():
    with tempfile.TemporaryDirectory(prefix="course-guidance-review-recovery-") as root:
        nested = os.path.join(root, "nested")
        os.mkdir(nested)
        bank = os.path.join(nested, "practice.md")
        shutil.copyfile(os.path.join(ROOT, "fixtures", "sample_bank.md"), bank)
        handler = SimpleNamespace(root=root, banks={"nested-practice": bank})
        log = evidence.log_path(nested)
        os.makedirs(os.path.dirname(log), exist_ok=True)
        for state in ("empty", "incomplete", "unavailable"):
            if state == "unavailable":
                os.mkdir(log)
            else:
                with open(log, "w", encoding="utf-8") as fh:
                    if state == "incomplete":
                        fh.write("not a JSON event\n")
            before = tuple(sorted(os.listdir(os.path.dirname(log))))
            with mock.patch.object(evidence, "objective_history") as indexed:
                forms = daemon._course_missed_review_forms(handler, root, "synthetic")
            check(not indexed.called and 'method="post"' not in forms,
                  "empty or unreadable evidence reached indexed missed-item selection")
            check(tuple(sorted(os.listdir(os.path.dirname(log)))) == before,
                  "evidence recovery display created index files")
            if state == "unavailable":
                os.rmdir(log)
            else:
                os.remove(log)
        question = daemon.load(bank)[0]
        event = evidence.response_event("synthetic-review", question, "B", False,
                                        "practice", 1, os.path.basename(bank))
        evidence.append_event(log, event)
        with mock.patch.object(evidence, "objective_history", return_value=[event]):
            forms = daemon._course_missed_review_forms(handler, root, "synthetic")
        check('method="post"' in forms and 'value="nested-practice"' in forms,
              "empty course-root history blocked a healthy nested-bank review")


def main():
    with tempfile.TemporaryDirectory(prefix="course-guidance-ui-") as root:
        for name in ("practice", "unbound"):
            shutil.copyfile(os.path.join(ROOT, "fixtures", "sample_bank.md"),
                            os.path.join(root, name + ".md"))
        handler = SimpleNamespace(root=root, banks={"admitted_alias": os.path.join(root, "practice.md"),
                                                   "unbound": os.path.join(root, "unbound.md")})
        doc = {"objectives": [{"id": "synthetic:flow", "statement": "Explain an unfamiliar learning flow"}],
               "sources": [{"source_object_id": "synthetic-source"}],
               "bindings": [{"binding_kind": "treatment", "source_object_id": "synthetic-source",
                             "objective": "synthetic:flow", "treatment_kind": "practice", "locator": "practice.md"}]}
        check_truthful_evidence_states(handler, root, doc)
        check_guidance_links(handler, root, doc)
        check_start_uses_bound_path(handler, root, doc)
        check_saved_sitting_admission(handler, root, doc)
    check_missed_review_recovery()
    print("course guidance UI: truthful counts, reasons, objectives, admitted starts and exact resume links ok")


if __name__ == "__main__":
    main()
