#!/usr/bin/env python3
"""Serve a synthetic auto/prose exam through its public paths."""
import os
import re
import sys
import tempfile
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import evidence  # noqa: E402
import itembank  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import daemon_roundtrip as daemon_test  # noqa: E402
import serve_roundtrip as serve_test  # noqa: E402


def check(test, message):
    if not test:
        raise AssertionError(message)


def exam_bank(root):
    source = open(serve_test.BANK, encoding="utf-8").read()
    # Both questions and their answer material are fictional fixture content.
    first = source[source.index("Q1. "):source.index("Q2. ")]
    last = source[source.index("Q6. "):]
    path = os.path.join(root, "formal_exam.md")
    with open(path, "w", encoding="utf-8") as out:
        out.write("# Synthetic formal exam\n\n" + first + last)
    questions = itembank.parse_bank(open(path, encoding="utf-8").read())
    check([q["type"] for q in questions] == ["mc", "short"],
          "two-item synthetic bank changed")
    return path, questions


def get(url):
    return daemon_test.get(url)[1]


def form_submit(url, page, answer):
    token = serve_test.submit_token(page)
    check(bool(token), "native page has no submission token")
    item_type = re.search(r'data-response-type="([^"]+)"', page)
    check(bool(item_type), "native page has no response type")
    fields = serve_test.form_fields_for({"type": item_type.group(1)}, answer)
    fields.extend([("form_token", token), ("action", "submit")])
    parts = urllib.parse.urlsplit(url)
    action_url = urllib.parse.urlunsplit(
        (parts.scheme, parts.netloc, parts.path + "/answer", parts.query, ""))
    request = urllib.request.Request(
        action_url, data=urllib.parse.urlencode(fields).encode(),
        method="POST", headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(request, timeout=5) as response:
        return response.read().decode("utf-8")


def api_journey(root, questions):
    proc, base, _lines = daemon_test.start_daemon(root)
    try:
        started = daemon_test.post(base + "api/start", {
            "bank": "formal_exam", "count": 2, "seed": 0, "mode": "exam"})
        sid = started["session_id"]
        session_file = started["session_file"]
        with open(session_file, "rb") as source:
            before_submit = source.read()
        check(started["item"]["type"] == "mc", "exam seed must start with MC")
        first = daemon_test.post(base + "api/submit", {
            "session_id": sid, "answer": "A"})
        check(first["action"] == "defer_feedback", "MC feedback was not held")
        check("score" not in first and "explain" not in first,
              "exam submission disclosed an early verdict")
        check(first["next"]["item"]["type"] == "short",
              "recorded auto answer did not reach the prose item")
        check(first["next"]["position"] == 1, "auto answer did not advance once")
        # Simulate the crash window: the event survived, but the atomic
        # session replacement did not. A read must recover once from evidence.
        with open(session_file, "wb") as old:
            old.write(before_submit)
        recovered = daemon_test.post(base + "api/next", {"session_id": sid})
        check(recovered["position"] == 1 and recovered["item"]["type"] == "short",
              "saved response did not recover the formal cursor")
        again = daemon_test.post(base + "api/next", {"session_id": sid})
        check(again["position"] == 1, "recovery advanced the cursor twice")
        partial = daemon_test.post(base + "api/report", {"session_id": sid})
        check(partial["status"] == "active" and partial["summary"]["auto_correct"] is None,
              "active formal report disclosed an auto score")
        check(all(row["correct"] is None for row in
                  partial["summary"]["objectives"].values()),
              "active formal report disclosed objective correctness")
        check("teaching_outcomes" not in partial["summary"],
              "active formal report disclosed teaching outcomes")
        incomplete = get(base + "report?session=" + sid)
        check('data-status="complete"' not in incomplete,
              "in-progress report claims completion")
        check("0/1" not in incomplete, "in-progress report leaks an auto verdict")
        check('Withheld until completion' in incomplete,
              "in-progress report must name withheld correctness")
        prose = daemon_test.post(base + "api/submit", {
            "session_id": sid, "answer": "A response for human review."})
        check(prose["action"] == "defer_feedback" and prose["next"]["position"] == 2,
              "unmarked formal prose did not advance after recording")
        check(prose["next"]["status"] == "complete", "two answered items did not close")
        check(prose["next"]["summary"]["pending_manual"] == 1,
              "completed sitting must retain pending human review")
        completed = get(base + "report?session=" + sid)
        check('data-status="complete"' in completed, "completed report did not reopen")
        check('Reopen this report after a reviewer records the marks.' in completed,
              "pending review has no next safe action")
        final = daemon_test.post(base + "api/report", {"session_id": sid})
        check(final["summary"]["auto_attempts"] == 1 and
              final["summary"]["auto_correct"] == 0 and
              final["summary"]["pending_manual"] == 1,
              "final report did not separate auto score and pending prose")
        events = [ev for ev in evidence.live_events(evidence.log_path(root))
                  if ev.get("session_id") == sid and ev.get("event_type") == "response"]
        check(len(events) == 2, "exam did not record exactly two responses")
    finally:
        proc.terminate()
        proc.wait(timeout=5)
    proc, base, _lines = daemon_test.start_daemon(root)
    try:
        check('data-status="complete"' in get(base + "report?session=" + sid),
              "exam result did not survive daemon restart")
    finally:
        proc.terminate()
        proc.wait(timeout=5)


def native_journey(root):
    proc, base, _lines = daemon_test.start_daemon(root)
    quiz = base + "quiz/formal_exam?mode=exam"
    try:
        page = get(quiz)
        check('data-response-type="mc"' in page, "native exam did not start at MC")
        pause = form_submit(quiz, page, "A")
        feedback = re.findall(r'<div class="feedback".*?</div>', pause, re.S)[0]
        check("Next question, 2 of 2" in pause and "Not correct" not in feedback,
              "native silent feedback has no honest Continue")
        next_page = get(quiz)
        check('data-response-type="short"' in next_page,
              "native Continue did not open prose item")
        pending = form_submit(quiz, next_page, "A response for human review.")
        feedback = re.findall(r'<div class="feedback".*?</div>', pending, re.S)[0]
        check("pending human review" in feedback and "Correct" not in feedback,
              "native pending prose is not explained")
        check("View summary" in pending, "native completed exam has no summary link")
        sid = re.search(r'data-session-id="([^"]+)"', next_page).group(1)
        check('data-status="complete"' in get(base + "report?session=" + sid),
              "native exam result could not open")
    finally:
        proc.terminate()
        proc.wait(timeout=5)
    proc, base, _lines = daemon_test.start_daemon(root)
    try:
        check('data-status="complete"' in get(base + "report?session=" + sid),
              "native exam result did not survive restart")
    finally:
        proc.terminate()
        proc.wait(timeout=5)


def main():
    with tempfile.TemporaryDirectory(prefix="formal-api-") as root:
        _path, questions = exam_bank(root)
        api_journey(root, questions)
    with tempfile.TemporaryDirectory(prefix="formal-native-") as root:
        exam_bank(root)
        native_journey(root)
    print("formal exam roundtrip: API and native completion paths passed")


if __name__ == "__main__":
    main()
