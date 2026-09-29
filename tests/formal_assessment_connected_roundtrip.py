#!/usr/bin/env python3
"""Walk a mixed formal sitting through the served HTTP session and report.

The temporary bank contains two synthetic fixture questions. This test never
settles a learner's prose or reads answer material from a served payload.
"""

import json
import os
import re
import sys
import tempfile
import urllib.error
import urllib.request

import serve_roundtrip as serve


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def get(url):
    with urllib.request.urlopen(url, timeout=5) as response:
        return response.read().decode("utf-8")


def temporary_bank(root):
    with open(serve.BANK, encoding="utf-8") as source:
        fixture = source.read()
    first = re.search(r"(?ms)^Q1\. .*?(?=^Q2\.)", fixture).group()
    prose = re.search(r"(?ms)^Q6\. .*\Z", fixture).group()
    prose = prose.replace("Q6.", "Q2.", 1)
    path = os.path.join(root, "formal_synthetic.md")
    with open(path, "w", encoding="utf-8") as target:
        target.write("# Synthetic formal assessment\n\n" + first + prose)
    return path


def assert_no_key(payload):
    item = payload.get("item") or (payload.get("next") or {}).get("item") or {}
    text = json.dumps(item)
    for secret in ("WHY BEST", "MODEL:", "RUBRIC:", '"correct":', '"explain":'):
        check(secret not in text, "formal response disclosed %s" % secret)
    check("explain" not in payload, "formal submit disclosed an explanation")


def run():
    with tempfile.TemporaryDirectory(prefix="formal-connected-") as root:
        bank = temporary_bank(root)
        out = os.path.join(root, "attempt.md")
        proc, base = serve.start_serve(bank, out)
        try:
            shell = get(base + "quiz/formal_synthetic")
            check("const SERVE = true" in shell, "served shell is absent")
            check("data-server-baseline" in shell, "native served baseline is absent")
            started = serve.api_start(base, "formal_synthetic", 2, "exam")
            check(started["status"] == "active", "formal sitting did not start")
            check(started["total"] == 2, "formal sitting has the wrong length")
            assert_no_key(started)
            session_id = started["session_id"]
            view = started
            seen = set()
            short_ref = None
            for _ in range(2):
                item = view["item"]
                item_ref = item["id"]
                check(item_ref not in seen, "formal cursor repeated an answered item")
                seen.add(item_ref)
                if item["type"] == "short":
                    short_ref = item_ref
                answer = ("The standard and the customer's experience differ."
                          if item["type"] == "short" else "A")
                result = serve.api_submit(base, session_id, answer)
                check(result["accepted"] is True, "formal response was refused")
                check(result["action"] == "defer_feedback",
                      "formal response did not defer feedback")
                check(result["evidence"]["status"] == "recorded",
                      "formal response was not recorded")
                assert_no_key(result)
                view = result["next"]
            check(view["status"] == "complete", "formal sitting did not close")
            check(short_ref is not None, "synthetic prose item was not served")
            check(view["summary"]["pending_manual"] == 1,
                  "unreviewed prose did not remain pending")

            reopened = serve.post(base + "api/next", {"session_id": session_id})
            check(reopened["status"] == "complete", "reopen lost completion")
            assert_no_key(reopened)
            report = serve.post(base + "api/report", {"session_id": session_id})
            check(report["summary"]["pending_manual"] == 1,
                  "report lost pending prose")
            check(report["summary"]["auto_attempts"] == 1,
                  "report miscounted the auto-marked item")
            page = get(base + "report?session=" + session_id)
            check("Pending" in page or "pending" in page,
                  "reopened report hides pending review")

            try:
                serve.post(base + "api/mark", {"session_id": session_id,
                                                "item_ref": "never-answered",
                                                "verdict": True})
            except urllib.error.HTTPError as error:
                check(error.code == 404, "unanswered mark returned %d" % error.code)
            else:
                raise AssertionError("mark accepted for an unanswered item")

            marked = serve.post(base + "api/mark", {"session_id": session_id,
                                                     "item_ref": short_ref,
                                                     "verdict": False})
            check(marked["status"] == "recorded", "human mark was not recorded")
            settled = serve.post(base + "api/report", {"session_id": session_id})
            check(settled["summary"]["pending_manual"] == 0,
                  "human-reviewed prose still counts as pending")
            check(settled["summary"]["auto_attempts"] == 1,
                  "human mark changed the auto-marked denominator")
        finally:
            proc.terminate()
            proc.wait(timeout=5)


if __name__ == "__main__":
    run()
    print("ok: served formal assessment closes, reopens, and reserves prose review")
