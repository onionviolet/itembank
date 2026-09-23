#!/usr/bin/env python3
"""Missed-practice review uses recorded misses and a course-scoped POST."""
import os
import shutil
import sys
import tempfile
from types import SimpleNamespace
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import evidence
import model
from surfaces import daemon


def check_course_action():
    root = tempfile.mkdtemp(prefix="missed_review_")
    try:
        course_dir = os.path.join(root, "course")
        os.mkdir(course_dir)
        bank_path = os.path.join(course_dir, "unit.md")
        shutil.copyfile(os.path.join(ROOT, "fixtures", "sample_bank.md"),
                        bank_path)
        question = model.load(bank_path)[0]
        row = {"item_id": question.get("item_id") or "",
               "item_ref": question["id"], "score": False,
               "mode": "practice"}
        log = evidence.log_path(course_dir)
        os.makedirs(os.path.dirname(log), exist_ok=True)
        open(log, "a", encoding="utf-8").close()
        redirects, errors = [], []
        handler = SimpleNamespace(
            root=root, banks={"unit": bank_path},
            read_form=lambda: {"action": ["review_missed"], "bank": ["unit"]},
            send_redirect=redirects.append,
            send_error=lambda code, message: errors.append((code, message)),
            send_server_error=lambda exc: errors.append((500, str(exc))))
        with mock.patch.object(daemon.evidence, "objective_history",
                               return_value=[row]):
            forms = daemon._course_missed_review_forms(
                handler, course_dir, "course")
        if 'method="post"' not in forms or \
                "Review 1 previously missed practice item" not in forms or \
                "CORRECT:" in forms or "WHY BEST:" in forms:
            raise AssertionError("missed review action or key safety is wrong")
        with mock.patch.object(daemon, "_reject_cross_origin_write",
                               return_value=False), \
                mock.patch.object(daemon.ia, "course_dir_for",
                                  return_value=course_dir), \
                mock.patch.object(daemon.session, "do_start",
                                  return_value={"session_id": "saved123"}) as start:
            daemon.handle_course_area_post(handler, "course", "evidence")
            if start.call_args.args[1]["selection_mode"] != "missed" or \
                    start.call_args.args[2] != "practice" or \
                    not start.call_args.args[3].startswith(
                        os.path.join(root, "_attempts")):
                raise AssertionError("course action bypassed runtime selection")
        if errors or redirects != [
                "/quiz/unit?mode=practice&session=saved123&course=course"]:
            raise AssertionError("review did not open its exact saved sitting")
        handler.read_form = lambda: {"action": ["review_missed"],
                                     "bank": ["outside"]}
        with mock.patch.object(daemon, "_reject_cross_origin_write",
                               return_value=False), \
                mock.patch.object(daemon.ia, "course_dir_for",
                                  return_value=course_dir), \
                mock.patch.object(daemon.session, "do_start") as start:
            daemon.handle_course_area_post(handler, "course", "evidence")
            if start.called or errors[-1][0] != 400:
                raise AssertionError("course action accepted a foreign bank")
    finally:
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    check_course_action()
    print("missed review: recorded practice miss, exact runtime launch, foreign bank refused")
