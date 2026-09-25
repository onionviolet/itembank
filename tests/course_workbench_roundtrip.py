#!/usr/bin/env python3
"""Course detail links and the Build and review flow over real loopback HTTP."""

import html
import json
import os
import re
import shutil
import sys
import tempfile
import urllib.parse
import urllib.error
import urllib.request
from types import SimpleNamespace
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import graph
import journal
from surfaces import agent_operation, course_workbench, ia, session
from daemon_roundtrip import get, start_daemon
from agent_operation_roundtrip import _Stub, local_profile


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def post(url, fields):
    data = urllib.parse.urlencode(fields).encode("utf-8")
    request = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status, response.url, response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raise AssertionError("POST %s returned %d: %s" %
                             (url, exc.code, exc.read().decode("utf-8")[:500])) from exc


def main():
    root = tempfile.mkdtemp(prefix="course-workbench-")
    stub = _Stub(candidate={"draft": "## LESSON\n\n### Safe summary\n\nA synthetic course draft.\n",
                            "citations": ["synthetic source section"]})
    proc = None
    try:
        ia.write_ia_state(root, "sample_course", {"removed": True})
        course_dir = os.path.join(root, "course_fixture_17b")
        shutil.copytree(os.path.join(ROOT, "course_fixture_17b"), course_dir,
                        ignore=shutil.ignore_patterns("_journal", "_evidence", "_attempts"))
        with open(os.path.join(course_dir, "course-graph.md"), encoding="utf-8") as stream:
            doc = graph.parse_course(stream.read())
        cid = doc["header"]["course_object_id"]
        source_rel = "sources/fen_hydrology_field_notes.md"
        source_record = journal.op_link(course_dir, "source", source_rel,
                                        "human", "synthetic-test", rights={"read": "granted"})
        keyed_rel = "sources/keyed.md"
        with open(os.path.join(course_dir, keyed_rel), "w", encoding="utf-8") as stream:
            stream.write("Q1. Synthetic check?\nA. Yes\nB. No\nCORRECT: A\n")
        keyed_record = journal.op_link(course_dir, "source", keyed_rel,
                                       "human", "synthetic-test", rights={"read": "granted"})
        keyed_text, keyed_notice = course_workbench._source_text(
            course_dir, keyed_record["object_id"], set())
        check(keyed_text is None and "Assessment source" in keyed_notice,
              "a registered keyed source leaked through the preview")
        doc["sources"][0]["source_object_id"] = source_record["object_id"]
        for binding in doc["bindings"]:
            if binding["source_object_id"] != doc["sources"][1]["source_object_id"]:
                binding["source_object_id"] = source_record["object_id"]
        objective_id = doc["objectives"][0]["id"]
        practice_bank = os.path.join(course_dir, "unit3_bank.md")
        with open(practice_bank, encoding="utf-8") as stream:
            bank_text = stream.read()
        bank_text = bank_text.replace("[OBJECTIVE: afe:unit3.layers]",
                                      "[OBJECTIVE: %s]" % objective_id, 1)
        with open(practice_bank, "w", encoding="utf-8") as stream:
            stream.write(bank_text)
        formal_bank = os.path.join(course_dir, "unit3_formal.md")
        with open(formal_bank, "w", encoding="utf-8") as stream:
            stream.write(bank_text)
        graph.add_binding(doc, "treatment", objective_id, source_record["object_id"],
                          treatment_kind="practice", locator="unit3_bank.md, Q1",
                          state="covered", confidence="high", rights_snapshot="granted")
        graph.add_binding(doc, "treatment", objective_id, source_record["object_id"],
                          treatment_kind="formal-test", locator="unit3_formal.md, Q1",
                          state="covered", confidence="high", rights_snapshot="granted")
        with open(os.path.join(course_dir, "course-graph.md"), "w", encoding="utf-8") as stream:
            stream.write(graph.serialize_course(doc))

        settings = {"model_backend": {"active": "local-qwen",
                                       "profiles": [local_profile(stub.port)]},
                    "auditor_autonomy": "draft_and_approve",
                    "agent_runs": {"draft-lesson": {
                        "target": "drafts/synthetic-lesson.md", "kind": "lesson",
                        "request": "Draft a source-grounded synthetic lesson.",
                        "citations": ["synthetic source section"]}}}
        target = os.path.join(course_dir, "drafts", "synthetic-lesson.md")
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "w", encoding="utf-8") as stream:
            stream.write("## LESSON\n\n### Original\n\nA prior local draft.\n")
        journal.op_link(course_dir, "lesson", "drafts/synthetic-lesson.md",
                        "human", "synthetic-test")
        with open(os.path.join(root, "itembank.json"), "w", encoding="utf-8") as stream:
            json.dump(settings, stream)
        proc, base, _lines = start_daemon(root)
        prefix = base + "course/" + cid + "/"

        status, page = get(prefix + "map")
        check(status == 200 and 'href="#objective-0"' in page, "objective row has no detail link")
        check('id="objective-0"' in page and '/sources?source=0#source-0' in page,
              "objective detail lost source alignment")
        map_links = html.unescape(page)
        check('/quiz/unit3_bank?mode=practice&course=' in map_links and
              '/quiz/unit3_formal?mode=exam&course=' in map_links,
              "exact bound bank treatments are not linked")
        check('/quiz/unit3_formal?mode=practice' not in map_links and
              '/quiz/unit3_bank?mode=exam' not in map_links,
              "treatment kind leaked to another bank sharing the objective")
        check("CORRECT:" not in page, "course map exposed a key")

        status, page = get(prefix + "sources")
        check(status == 200 and 'href="?source=0#source-0"' in page,
              "source row has no detail link")
        check("Open this source to read" in page, "unselected source preview read eagerly")
        status, page = get(prefix + "sources?source=0")
        check("Source text" in page and "minerotrophic" in html.unescape(page).lower(),
              "rights-granted source is not readable")
        check('/map#objective-0' in page, "source detail has no objective return link")

        attempt = os.path.join(root, "_attempts", "session_workbench.json")
        started = session.do_start(
            os.path.join(course_dir, "unit3_bank.md"),
            {"selection_mode": "exam", "type_counts": {"mc": 1},
             "count": 1, "seed": 0}, "exam", attempt, False)
        session.do_submit(attempt, "A", None)
        status, page = get(prefix + "evidence")
        check(status == 200 and 'href="#evidence-responses"' in page,
              "evidence row has no detail link")
        check('id="evidence-sessions"' in page and "A count does not imply mastery" in page,
              "evidence detail is missing context")
        report_href = '/report?session=' + started["session_id"]
        check(report_href in page, "completed sitting has no report link")
        check(get(base + report_href.lstrip('/'))[0] == 200,
              "evidence report link does not resolve")
        resumed = session.do_start(
            os.path.join(course_dir, "unit3_bank.md"),
            {"selection_mode": "exam", "type_counts": {"mc": 1},
             "count": 1, "seed": 1}, "exam",
            os.path.join(root, "_attempts", "session_resume.json"), False)
        status, active_page = get(prefix + "evidence")
        check(status == 200 and "Resume saved sitting" in active_page,
              "active sitting has no resume link")
        resume_href = ('quiz/unit3_bank?mode=exam&amp;session=' +
                       resumed["session_id"] + '&amp;course=' + cid)
        check(resume_href in active_page, "active sitting link has wrong route")
        check(get(base + html.unescape(resume_href))[0] == 200,
              "evidence resume link does not resolve")
        fake_handler = SimpleNamespace(root=root, path="/course/%s/evidence" % cid)
        fake_state = {"area": "evidence", "area_label": "Evidence", "course_id": cid}
        wrong_bank = os.path.join(course_dir, "other", "unit3_bank.md")
        fake_resume = {"sessions": ({"session_id": "unadmitted", "bank": wrong_bank,
                                      "mode": "exam", "status": "active"},)}
        with mock.patch.object(ia, "_course_resume_state", return_value=fake_resume):
            unavailable = course_workbench.details(
                fake_handler, fake_state, course_dir, doc,
                [("unit3_bank", practice_bank)])
            collision = course_workbench.details(
                fake_handler, fake_state, course_dir, doc,
                [("unit3_bank", wrong_bank), ("alias", wrong_bank)])
        check("Saved sitting is unavailable" in unavailable and
              "Resume saved sitting" not in unavailable,
              "unadmitted same-basename sitting gained a resume link")
        check("Saved sitting is unavailable" in collision and
              "Resume saved sitting" not in collision,
              "ambiguous admitted path gained a resume link")
        check("CORRECT:" not in page, "evidence page exposed a key")

        status, page = get(prefix + "build")
        check(status == 200 and 'action="/course/%s/build"' % cid in page,
              "Build and review has no script-free form")
        _, final_url, page = post(prefix + "build", {"action": "start", "skill": "draft-lesson"})
        check("proposal=" in final_url and "Accept proposal" in page,
              "proposal did not reach the review page")
        proposal_id = urllib.parse.parse_qs(urllib.parse.urlsplit(final_url).query)["proposal"][0]
        check("synthetic source section" in page and "Proposed change diff" in page,
              "proposal does not show citation and diff")
        with open(target, encoding="utf-8") as stream:
            check("Original" in stream.read(), "start accepted a draft without review")
        _, _, page = post(prefix + "build", {"action": "accept", "proposal_id": proposal_id})
        check(os.path.exists(target) and "Undo accepted change" in page,
              "accept did not journal the draft")
        _, _, page = post(prefix + "build", {"action": "undo", "proposal_id": proposal_id})
        with open(target, encoding="utf-8") as stream:
            restored = stream.read()
        check("Original" in restored and "undone" in page.lower(),
              "undo did not restore the prior state")

        settings["agent_runs"]["draft-lesson"]["target"] = "drafts/new-lesson.md"
        with open(os.path.join(root, "itembank.json"), "w", encoding="utf-8") as stream:
            json.dump(settings, stream)
        _, final_url, _ = post(prefix + "build", {"action": "start", "skill": "draft-lesson"})
        mint_id = urllib.parse.parse_qs(urllib.parse.urlsplit(final_url).query)["proposal"][0]
        minted = os.path.join(course_dir, "drafts", "new-lesson.md")
        _, _, page = post(prefix + "build", {"action": "accept", "proposal_id": mint_id})
        check(os.path.exists(minted), "accepted mint did not create the draft")
        _, _, page = post(prefix + "build", {"action": "undo", "proposal_id": mint_id})
        check(not os.path.lexists(minted) and "undone" in page.lower(),
              "mint undo did not restore prior absence")
        check(agent_operation.status(course_dir, mint_id)["restored_byte_identical"],
              "mint undo did not record an exact restoration")

        settings["agent_runs"]["draft-lesson"]["target"] = "drafts/synthetic-lesson.md"
        with open(os.path.join(root, "itembank.json"), "w", encoding="utf-8") as stream:
            json.dump(settings, stream)

        _, final_url, _ = post(prefix + "build", {"action": "start", "skill": "draft-lesson"})
        stale_id = urllib.parse.parse_qs(urllib.parse.urlsplit(final_url).query)["proposal"][0]
        with open(target, "w", encoding="utf-8") as stream:
            stream.write("External edit\n")
        _, _, page = post(prefix + "build", {"action": "accept", "proposal_id": stale_id})
        check("conflicted" in page.lower(), "stale proposal was not marked conflicted")
        with open(target, encoding="utf-8") as stream:
            check(stream.read() == "External edit\n", "stale proposal overwrote the external edit")

        settings["auditor_autonomy"] = "report_only"
        with open(os.path.join(root, "itembank.json"), "w", encoding="utf-8") as stream:
            json.dump(settings, stream)
        _, final_url, page = post(prefix + "build", {"action": "start", "skill": "draft-lesson"})
        check("Accept is unavailable" in page, "report-only mode exposed accept form")
        report_id = urllib.parse.parse_qs(urllib.parse.urlsplit(final_url).query)["proposal"][0]
        _, _, page = post(prefix + "build", {"action": "accept", "proposal_id": report_id})
        check("report_only" in page, "direct report-only POST lacked refusal")
        check(agent_operation.status(course_dir, report_id)["disposition"] == "proposed",
              "report-only refusal settled a reviewable proposal")
        print("COURSE WORKBENCH: loopback navigation, proposal review, accept, undo, conflict, and report-only passed")
    finally:
        if proc is not None:
            proc.terminate()
            proc.wait(timeout=5)
        stub.close()
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    main()
