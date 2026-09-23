#!/usr/bin/env python3
"""Exact mock composition stays in the one selector and course action."""
import os
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import model
import selection
from runtime import read_session
from surfaces import daemon
from surfaces import session


def check_exact_mix():
    questions = model.load(os.path.join(ROOT, "fixtures", "selection_bank.md"))
    available = {name: sum(q["type"] == name for q in questions)
                 for name in ("mc", "multi")}
    assert all(available.values()), available
    spec = {"selection_mode": "exam", "type_counts": {"mc": 2, "multi": 1},
            "count": 3, "seed": 7}
    chosen, trace = selection.select(questions, spec, [])
    assert [q["id"] for q in chosen] == [
        q["id"] for q in selection.select(questions, spec, [])[0]]
    assert sum(q["type"] == "mc" for q in chosen) == 2
    assert sum(q["type"] == "multi" for q in chosen) == 1
    assert trace["spec"]["type_counts"] == spec["type_counts"]
    for bad in ({"mc": available["mc"] + 1}, {"mc": 0}):
        try:
            selection.select(questions, {"selection_mode": "exam",
                                         "type_counts": bad,
                                         "count": sum(bad.values())}, [])
        except SystemExit:
            pass
        else:
            raise AssertionError("invalid mix was accepted")


def check_course_action():
    root = tempfile.mkdtemp(prefix="mock_exam_")
    try:
        course_dir = os.path.join(root, "course")
        os.mkdir(course_dir)
        bank_path = os.path.join(course_dir, "unit.md")
        shutil.copyfile(os.path.join(ROOT, "fixtures", "sample_bank.md"),
                        bank_path)
        available = {q["type"] for q in model.load(bank_path)}
        fields = {"action": ["start_mock"], "bank": ["unit"],
                  "minutes": ["30"]}
        fields.update({"mix_" + name: ["1"] for name in available})
        redirects, errors = [], []
        handler = SimpleNamespace(
            root=root, banks={"unit": bank_path}, read_form=lambda: fields,
            send_redirect=redirects.append,
            send_error=lambda code, message: errors.append((code, message)),
            send_server_error=lambda exc: errors.append((500, str(exc))))
        html = daemon._course_mock_forms(handler, course_dir, "course")
        assert 'action="/course/course/test"' in html
        assert "Start mock test" in html
        with mock.patch.object(daemon, "_reject_cross_origin_write",
                               return_value=False), \
                mock.patch.object(daemon.ia, "course_dir_for",
                                  return_value=course_dir), \
                mock.patch.object(daemon.session, "do_start",
                                  return_value={"session_id": "mock123"}) as start:
            daemon.handle_course_area_post(handler, "course", "test")
            assert start.call_args.args[1]["type_counts"] == {
                name: 1 for name in available}
            assert start.call_args.args[2] == "exam"
            assert start.call_args.kwargs["time_limit_minutes"] == 30
        assert redirects == [
            "/quiz/unit?mode=exam&session=mock123&course=course"]
        assert not errors
        fields["bank"] = ["foreign"]
        with mock.patch.object(daemon, "_reject_cross_origin_write",
                               return_value=False), \
                mock.patch.object(daemon.ia, "course_dir_for",
                                  return_value=course_dir), \
                mock.patch.object(daemon.session, "do_start") as start:
            daemon.handle_course_area_post(handler, "course", "test")
            assert not start.called
        assert errors[-1][0] == 400
        # The server, rather than the browser countdown, owns expiration.
        out = os.path.join(root, "_attempts", "timed.json")
        result = session.do_start(bank_path,
                                  {"selection_mode": "exam", "count": 2},
                                  "exam", out, False, time_limit_minutes=1)
        assert result["timing"]["minutes"] == 1
        assert session.do_report(out)["summary"]["auto_correct"] is None
        deadline = result["timing"]["deadline"]
        with mock.patch.object(session.evidence, "utc_now",
                               return_value=deadline):
            view = session.do_next(out)
            assert view["status"] == "complete"
            assert "item" not in view
            try:
                session.do_submit(out, "A", None)
            except SystemExit:
                pass
            else:
                raise AssertionError("late answer was recorded")
            report = session.do_report(out)
        assert report["timed_out"] is True
        assert report["unanswered"] == 2
        assert report["summary"]["auto_attempts"] == 0
        assert read_session(out)["timing"]["expired"] is True
        assert read_session(out)["responses"] == []
        assert session.do_next(out)["status"] == "complete"
        cli_out = os.path.join(root, "_attempts", "cli.json")
        cli = subprocess.run(
            [sys.executable, os.path.join(ROOT, "itembank.py"), "start",
             bank_path, "--mode", "exam", "--selection-mode", "exam",
             "--mix", "mc=1", "--minutes", "2", "--out", cli_out],
            cwd=ROOT, capture_output=True, text=True)
        assert cli.returncode == 0, cli.stderr
        assert read_session(cli_out)["timing"]["minutes"] == 2
    finally:
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    check_exact_mix()
    check_course_action()
    print("mock exam: exact mix, course action, persisted server deadline")
