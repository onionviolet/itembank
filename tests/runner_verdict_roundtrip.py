#!/usr/bin/env python3
"""Regression checks for process outcomes in check-item runner verdicts.

Matching output is necessary but insufficient. A case passes only when the
candidate process also exits successfully. The runner keeps bounded stdout,
stderr, and exit status so the versioned interaction layer can explain a
released result without rerunning learner code.

Standard library only, no framework, runnable as
python tests/runner_verdict_roundtrip.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import runner                                              # noqa: E402
import runtime                                             # noqa: E402


def fail(message):
    print("FAIL: " + message)
    sys.exit(1)


def output_question(expected="42"):
    return {
        "type": "check",
        "lang": "python",
        "match": "trimmed",
        "cases": [{"stdin": "", "expected": expected}],
    }


def harness_question():
    return {
        "type": "check",
        "lang": "python",
        "match": "trimmed",
        "harness": "add",
        "tolerance": None,
        "cases": [{"call": "add(1, 2)", "stdin": "add(1, 2)",
                   "expected": "3"}],
    }


def one_case(question, source, timeout=2, cap=4096):
    result = runner.run_cases(
        question, source, timeout_seconds=timeout, max_output_bytes=cap)
    if len(result) != 1:
        fail("runner returned %d cases, expected one: %r"
             % (len(result), result))
    return result[0]


def check_matching_output_then_error_fails():
    source = 'print(42)\nraise RuntimeError("synthetic audit probe")\n'
    case = one_case(output_question(), source)
    if case["actual"] != "42\n":
        fail("crashing source lost its matching stdout: %r" % case)
    if case["passed"] is not False:
        fail("matching stdout followed by a runtime error passed: %r" % case)
    if case["exit_code"] in (None, 0):
        fail("runtime error has no nonzero exit status: %r" % case)
    if "RuntimeError" not in case["stderr"]:
        fail("runtime error diagnostic was not retained: %r" % case)
    if runtime.score_response(output_question(), [case]) is not False:
        fail("runtime error did not reduce to a settled false verdict")
    observation = runtime._check_observation(output_question(), 0, case)
    if observation["reason"] != "runtime_error" or observation["exit_code"] == 0:
        fail("matching output crash was mislabeled as wrong output: %r" % observation)
    if "RuntimeError" not in observation["stderr"]:
        fail("released crash observation lost its diagnostic: %r" % observation)
    feedback = {"interaction_result": {"observations": [observation]}}
    if runtime.submission_feedback(feedback, "practice") != feedback:
        fail("practice lost released diagnostics")
    for mode in ("exam", "diagnostic"):
        if runtime.submission_feedback(feedback, mode):
            fail("silent mode leaked crash diagnostics")


def check_success_and_silent_crash():
    good = one_case(output_question(), "print(42)\n")
    if good["passed"] is not True or good["exit_code"] != 0:
        fail("normal successful execution did not pass: %r" % good)
    if good["stderr"] != "":
        fail("normal successful execution produced stderr: %r" % good)

    crashed = one_case(output_question(), 'raise RuntimeError("silent")\n')
    if crashed["passed"] is not False or crashed["actual"] != "":
        fail("a no-output crash did not fail cleanly: %r" % crashed)
    if crashed["exit_code"] in (None, 0) or "RuntimeError" not in crashed["stderr"]:
        fail("a no-output crash lost its process diagnostics: %r" % crashed)


def check_function_harness_requires_successful_exit():
    question = harness_question()
    good = one_case(question, "def add(a, b):\n    return a + b\n")
    if good["passed"] is not True or good["exit_code"] != 0:
        fail("normal function harness execution did not pass: %r" % good)

    source = ('print("int:3")\n'
              'raise RuntimeError("failed during module import")\n'
              'def add(a, b):\n'
              '    return a + b\n')
    crashed = one_case(question, source)
    if crashed["actual"] != "int:3\n":
        fail("harness crash did not retain its matching typed line: %r"
             % crashed)
    if crashed["passed"] is not False or crashed["exit_code"] in (None, 0):
        fail("function harness passed output from a failed process: %r"
             % crashed)
    if "RuntimeError" not in crashed["stderr"]:
        fail("function harness lost the import failure diagnostic: %r"
             % crashed)


def check_existing_bounds_keep_their_verdicts():
    timed = one_case(output_question(""), "while True:\n    pass\n",
                     timeout=0.2)
    if timed["timed_out"] is not True or timed["exit_code"] is not None:
        fail("timeout did not retain the no-exit-status shape: %r" % timed)
    if timed["passed"] is not False:
        fail("timed-out case carried a passing case result: %r" % timed)
    if runtime.score_response(output_question(""), [timed]) is not None:
        fail("timeout no longer reduces to a pending verdict")

    source = ('import sys\n'
              'print(42)\n'
              'while True:\n'
              '    sys.stderr.write("x" * 1000)\n'
              '    sys.stderr.flush()\n')
    capped = one_case(output_question(), source, timeout=2, cap=1024)
    if capped["truncated"] is not True or capped["timed_out"] is not False:
        fail("output cap no longer records a truncated run: %r" % capped)
    if capped["passed"] is not False:
        fail("truncated matching output passed: %r" % capped)
    if runtime.score_response(output_question(), [capped]) is not False:
        fail("truncated run no longer reduces to a settled false verdict")


def main():
    checks = [
        check_matching_output_then_error_fails,
        check_success_and_silent_crash,
        check_function_harness_requires_successful_exit,
        check_existing_bounds_keep_their_verdicts,
    ]
    for check in checks:
        check()
    print("runner_verdict_roundtrip: %d checks passed" % len(checks))
    return 0


if __name__ == "__main__":
    sys.exit(main())
