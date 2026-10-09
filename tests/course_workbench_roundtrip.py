#!/usr/bin/env python3
"""Course detail links and the Build and review flow over real loopback HTTP."""

import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
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
import evidence
from surfaces import agent_operation, course_workbench, daemon, ia, session
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


def start_runtime(root, runtime):
    """Exercise a packaged server while retaining disposable fixture setup."""
    if runtime is None:
        return start_daemon(root)
    runtime = os.path.abspath(runtime)
    check(os.path.isfile(runtime), "runtime does not exist: " + runtime)
    command = ([sys.executable, "-u", runtime]
               if runtime.endswith((".pyz", ".py")) else [runtime])
    proc = subprocess.Popen(command + ["daemon", root, "--no-open", "--port", "0"],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, cwd=root)
    lines = []
    def consume_output():
        for line in proc.stdout:
            lines.append(line)
    threading.Thread(target=consume_output, daemon=True).start()
    try:
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            match = re.search(r"http://127\.0\.0\.1:\d+/", "".join(lines))
            if match:
                base = match.group(0)
                try:
                    if get(base + "__itembank__", timeout=1)[0] == 200:
                        return proc, base, lines
                except (OSError, urllib.error.URLError):
                    pass
            if proc.poll() is not None:
                break
            time.sleep(0.1)
        raise AssertionError("packaged daemon did not become ready:\n" + "".join(lines))
    except BaseException:
        if proc.poll() is None:
            proc.terminate()
        proc.wait(timeout=5)
        proc.stdout.close()
        raise


def main(runtime=None, browser_hold=False):
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
        with mock.patch("course.read_course", side_effect=OSError):
            unavailable_course = daemon._course_area_extra(
                SimpleNamespace(root=root),
                {"area": "map", "course_id": cid}, course_dir)
        check("Course details are unavailable" in unavailable_course and
              "No current source" not in unavailable_course,
              "unreadable course was presented as an empty map")
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
        proc, base, _lines = start_runtime(root, runtime)
        prefix = base + "course/" + cid + "/"
        if browser_hold:
            print(json.dumps({"browser_build_url": prefix + "build", "root": root,
                              "target": target}), flush=True)
            input("Press Enter after the disposable browser journey to stop its server: ")
            return

        status, page = get(prefix + "map")
        check(status == 200 and 'href="#objective-0"' in page, "objective row has no detail link")
        source_link = re.search(r'href="(/course/[^"<>]+/sources\?[^"<>]+#source-0)"', page)
        source_query = (urllib.parse.parse_qs(urllib.parse.urlsplit(
            html.unescape(source_link.group(1))).query) if source_link else {})
        check('id="objective-0"' in page and source_query.get('source') == ['0'] and
              source_query.get('return_objective') == [objective_id],
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
        failed_handler = SimpleNamespace(root=root, path="/course/%s/evidence" % cid)
        failed_state = {"area": "evidence", "area_label": "Evidence", "course_id": cid}
        with mock.patch.object(course_workbench.evidence, "events", side_effect=OSError):
            failed_evidence = course_workbench.details(
                failed_handler, failed_state, course_dir, doc,
                [("unit3_bank", practice_bank)])
        check("Evidence counts are unavailable" in failed_evidence and
              "0 recorded" not in failed_evidence,
              "unreadable evidence was presented as a clean zero")
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

        with tempfile.TemporaryDirectory(prefix="course-evidence-retraction-") as evidence_base:
            log = evidence.log_path(evidence_base)
            event = evidence.response_event(
                "retracted-sitting", {"objective": "synthetic:review", "id": "R1",
                                      "type": "mc", "item_id": ""},
                "B", False, "practice", 1, "synthetic.md")
            evidence.append_event(log, event)
            with mock.patch.object(ia, "_course_resume_state", return_value={"sessions": ()}):
                before_retract = course_workbench.details(
                    fake_handler, fake_state, evidence_base, doc, [])
                evidence.append_event(log, evidence.retraction_event(
                    event["event_id"], "Synthetic response withdrawn"))
                after_retract = course_workbench.details(
                    fake_handler, fake_state, evidence_base, doc, [])
            check("<h3>Responses</h3><p>1 recorded." in before_retract,
                  "live response was not counted")
            check("<h3>Responses</h3><p>0 recorded." in after_retract and
                  "<h3>Sittings</h3><p>0 recorded." in after_retract,
                  "retracted response still contributes to course evidence counts")

        status, page = get(prefix + "build")
        check(status == 200 and 'action="/course/%s/build"' % cid in page,
              "Build and review has no script-free form")
        _, final_url, page = post(prefix + "build", {"action": "start", "skill": "draft-lesson"})
        check("proposal=" in final_url and "Accept proposal" in page,
              "proposal did not reach the review page")
        proposal_id = urllib.parse.parse_qs(urllib.parse.urlsplit(final_url).query)["proposal"][0]
        check("synthetic source section" in page and "Proposed change diff" in page,
              "proposal does not show citation and diff")
        check("Learner lesson preview" in page and "Plain Markdown draft" in page and
              "Revise this paragraph" in page,
              "pending lesson lacks preview and correction controls")
        draft_token = agent_operation.draft_fingerprint(
            agent_operation.status(course_dir, proposal_id)["draft"])
        _, _, page = post(prefix + "build", {
            "action": "revise", "proposal_id": proposal_id,
            "before_paragraph": "A synthetic course draft.",
            "after_paragraph": "A corrected synthetic course draft.",
            "expected_draft_fingerprint": draft_token})
        check("A corrected synthetic course draft." in page and
              "Proposed change diff" in page,
              "corrected proposal did not return to review")
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
            proc.stdout.close()
        stub.close()
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", help="Packaged .pyz or frozen executable to exercise")
    parser.add_argument("--browser-hold", action="store_true",
                        help="Hold the disposable authoring fixture for a real browser journey")
    args = parser.parse_args()
    main(args.runtime, args.browser_hold)
