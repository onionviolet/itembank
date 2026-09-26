#!/usr/bin/env python3
"""Silent check sittings keep all execution feedback behind runtime policy."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import runtime
from surfaces import session
from check_roundtrip import CHECK_BANK, SUM_SOURCE, _serve_base, post

PRIVATE = {"score", "verdict", "passed", "expected", "input", "actual",
           "run_result", "interaction_result", "observations", "explain",
           "selection_feedback", "stdout", "stderr", "exit_code"}


def assert_silent(payload):
    # Serialize the entire body first, including every nested adapter envelope.
    body = json.loads(json.dumps(payload))
    def walk(value):
        if isinstance(value, dict):
            assert not PRIVATE.intersection(value), value
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)
    walk(body)
    return body


def main():
    nested = {"replay": [{"score": True, "run_result": [{"passed": True}],
                            "verdict": True, "expected": "secret", "input": "secret"}]}
    assert_silent(runtime.submission_feedback(nested, "exam"))
    assert runtime.submission_feedback(nested, "practice") == nested
    for mode in ("exam", "diagnostic"):
        with tempfile.TemporaryDirectory() as work:
            bank = os.path.join(work, "check_bank.md")
            shutil.copyfile(CHECK_BANK, bank)
            path = os.path.join(work, "session.json")
            session.do_start(bank, {"count": 6, "seed": 0, "focus": "q1"},
                             mode, path, False)
            before = runtime.read_session(path)
            result = assert_silent(session.do_submit(path, SUM_SOURCE, None))
            assert result["status"] == "active"
            assert result["action"] == "defer_feedback"
            # Reproduce the crash window: evidence committed, session write lost.
            runtime.write_session(path, before)
            cli = subprocess.run([sys.executable, os.path.join(ROOT, "itembank.py"),
                                  "submit", path, "--answer", json.dumps(SUM_SOURCE)],
                                 capture_output=True, text=True)
            assert cli.returncode == 0, cli.stderr
            replay = assert_silent(json.loads(cli.stdout))
            assert replay["accepted"] is False
            assert replay["evidence"]["status"] == "already_recorded"
            assert session.do_report(path)["summary"]["auto_correct"] is None
            # Finish using a different result vector after the replay.
            for _ in range(6):
                if runtime.read_session(path)["status"] != "active":
                    break
                assert_silent(session.do_submit(path, "print('wrong')", None))
            assert runtime.read_session(path)["status"] == "complete"
            assert isinstance(session.do_report(path)["summary"]["auto_correct"], int)

    with tempfile.TemporaryDirectory() as work:
        bank = os.path.join(work, "check_bank.md")
        shutil.copyfile(CHECK_BANK, bank)
        process, base = _serve_base(bank, os.path.join(work, "attempt.md"), [])
        try:
            assert base
            for mode in ("exam", "diagnostic", "practice"):
                started = post(base + "api/start", {"bank": "check_bank", "count": 6,
                                                     "mode": mode, "focus": "q1"})
                result = post(base + "api/submit", {"session_id": started["session_id"],
                                                    "answer": SUM_SOURCE})
                if mode == "practice":
                    assert result["score"] is True
                    assert result["interaction_result"]["observations"][0]["expected"]
                    assert result["run_result"][0]["passed"] is True
                else:
                    assert_silent(result)
                    assert result["status"] == "active"
        finally:
            process.terminate()
            process.wait(timeout=10)
    print("check disclosure: JSON, CLI replay, API, practice and completion passed")


if __name__ == "__main__":
    main()
