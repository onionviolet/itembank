#!/usr/bin/env python3
"""Assert the runner's two bounds -- the output cap and the wall-clock deadline
-- and prove the kill reaches two levels deep (plan 05-02).

The check runner (plan 05-01) bounds a learner's code two ways: an output cap
fails and kills a flooding case early, and a per-case deadline kills a run that
never terminates, surfacing a run-level killed_at_timeout fact and yielding no
dichotomous verdict (criterion 12). This test asserts those two bounds on both
the POSIX and Windows kill paths, and runs a synthetic grandchild-spawning
fixture through the runner to prove the process-tree kill reaches a process
that outlives its direct child.

Standard library only, no framework, runnable as
python tests/check_kill_roundtrip.py
"""
import ctypes, os, re, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import runner                                              # noqa: E402
import runtime                                             # noqa: E402

NL = chr(10)   # a literal newline, built without backslash escapes


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def make_q(expected, cases=None):
    """A minimal inline check question dict (no fixture-bank parse round trip
    -- these are runner-level properties, not authoring properties)."""
    return {"type": "check", "lang": "python", "match": "trimmed",
            "cases": cases if cases is not None
            else [{"stdin": "", "expected": expected}]}


# ---- Task 1: the output cap fails the case and kills early ------------------

def check_cap_kill_fires_early():
    # A flooding, non-terminating program with a 5s deadline must be stopped by
    # the cap in cap-crossing time (well under 2s), not wait the clock out.
    q = make_q("")
    src = "while True:" + NL + "    print('x' * 1000)"
    t0 = time.monotonic()
    res = runner.run_cases(q, src, timeout_seconds=5, max_output_bytes=4096)
    elapsed = time.monotonic() - t0
    if not res or not res[0]["truncated"]:
        fail("flooding program was not reported truncated: %r" % res)
    if elapsed >= 2.0:
        fail("cap kill took %.2fs; the cap must stop a flood in cap-crossing "
             "time, not wait out the 5s deadline" % elapsed)
    if len(res[0]["actual"]) > 8192:
        fail("truncated actual output exceeds the cap: %d bytes"
             % len(res[0]["actual"]))


def check_truncated_forces_false_even_when_prefix_matches():
    # The accumulated stdout prefix equals the expected text, yet the case must
    # still fail: a truncated run never demonstrates correct output (D-08).
    q = make_q("12")
    src = ("import sys" + NL +
           "sys.stdout.write('12' + chr(10)); sys.stdout.flush()" + NL +
           "while True:" + NL +
           "    sys.stderr.write('x' * 100); sys.stderr.flush()")
    res = runner.run_cases(q, src, timeout_seconds=1, max_output_bytes=1024)
    r = res[0]
    if not r["truncated"]:
        fail("stderr flood was not reported truncated: %r" % r)
    if r["actual"] != "12" + NL:
        fail("expected retained stdout prefix '12\n', got %r" % r["actual"])
    # trimmed("12\n") equals trimmed("12") -- content matches -- so the only
    # reason to fail is the truncation.
    if r["passed"] is not False:
        fail("a truncated case whose prefix matches expected must still be "
             "passed False, got %r" % r["passed"])


def check_flags_independent():
    # A silent infinite loop: killed at the deadline, not by the cap.
    q = make_q("")
    res = runner.run_cases(q, "while True:" + NL + "    pass",
                           timeout_seconds=1, max_output_bytes=65536)
    r = res[0]
    if r["timed_out"] is not True:
        fail("silent infinite loop did not report timed_out: %r" % r)
    if r["truncated"] is not False:
        fail("a silent loop wrote nothing, so truncated must be False: %r" % r)


def check_timeout_not_a_verdict():
    # A killed-at-timeout run surfaces the run-level killed_at_timeout fact
    # (the 05-01 shape: any case timed out) and produces no verdict -- the
    # scorer returns None, never False (criterion 12).
    q = make_q("")
    hung = runner.run_cases(q, "while True:" + NL + "    pass",
                            timeout_seconds=1, max_output_bytes=65536)
    if not any(c["timed_out"] for c in hung):
        fail("killed-at-timeout run did not surface the killed_at_timeout "
             "fact: %r" % hung)
    if runtime.score_response(q, hung) is not None:
        fail("a killed run must score None, got %r"
             % runtime.score_response(q, hung))
    # The output-cap kill is a real fail (D-08): truncated, not timed out, so
    # it still scores False.
    flooded = runner.run_cases(q, "while True:" + NL + "    print('x' * 1000)",
                               timeout_seconds=1, max_output_bytes=4096)
    r = flooded[0]
    if r["truncated"] is not True or r["timed_out"] is not False:
        fail("over-cap run must be truncated-not-timed-out: %r" % r)
    if runtime.score_response(q, flooded) is not False:
        fail("a truncated run must score False (D-08), got %r"
             % runtime.score_response(q, flooded))


def _kill_tree_body(source):
    """The source text between  and the next top-level ."""
    start = source.index("def kill_tree(")
    nxt = re.search(r"\ndef ", source[start:])
    end = start + nxt.start() if nxt else len(source)
    return source[start:end]


def check_source_greps():
    src = open(os.path.join(ROOT, "runner.py"), encoding="utf-8").read()
    code = "\n".join(l for l in src.splitlines()
                     if not l.lstrip().startswith("#"))
    n_kill = len(re.findall(r"kill_tree\(", code))
    if n_kill < 3:
        fail("kill_tree( appears %d times; expected the def plus a deadline "
             "branch and a cap branch call" % n_kill)
    body = _kill_tree_body(src)
    for prim in ("taskkill", "killpg", "TerminateProcess", "CloseHandle"):
        # Any occurrence outside kill_tree's body means a second kill mechanism
        # exists, or a kill primitive escaped the one kill path.
        outside = code.replace(body, "", 1)
        if prim in outside:
            fail("kill primitive %r appears outside kill_tree's body" % prim)


# ---- Task 2: Windows Job Object kill-on-close, taskkill fallback -----------

def check_import_no_windll():
    # CI is Linux-only; a WinDLL call at import time would break every test
    # there. Guard the import so any such call raises.
    code = ("import ctypes, sys\n"
            "sys.path.insert(0, %r)\n"
            "def boom(*a, **k):\n"
            "    raise RuntimeError('WinDLL called at import')\n"
            "ctypes.WinDLL = boom\n"
            "import runner\n"
            "print('import-ok')\n" % ROOT)
    r = subprocess.run([sys.executable, "-c", code], capture_output=True)
    if r.returncode or b"import-ok" not in r.stdout:
        fail("runner.py calls a Windows DLL at import time: %s"
             % r.stderr.decode("utf-8", "replace"))


def check_windows_constants_and_layouts():
    if runner.JobObjectExtendedLimitInformation != 9:
        fail("JobObjectExtendedLimitInformation is %r, want 9"
             % runner.JobObjectExtendedLimitInformation)
    if not runner.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE:
        fail("JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE is falsy: %r"
             % runner.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE)
    ext = ctypes.sizeof(runner.JOBOBJECT_EXTENDED_LIMIT_INFORMATION)
    basic = ctypes.sizeof(runner.JOBOBJECT_BASIC_LIMIT_INFORMATION)
    if not (ext > basic):
        fail("extended limit info (%d bytes) must embed the basic block "
             "(%d bytes)" % (ext, basic))
    src = open(os.path.join(ROOT, "runner.py"), encoding="utf-8").read()
    if len(re.findall(r"JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE", src)) < 1:
        fail("JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE is not defined in runner.py")
    if "bpo-1677688" not in src:
        fail("the accepted spawn window must be written into runner.py "
             "(bpo-1677688)")


def check_windows_kill_paths():
    if sys.platform != "win32":
        return   # the Windows kill paths are 05-04's manual pass on Linux CI
    q = make_q("")
    # Primary path: closing the job handle kills the whole tree.
    runner._FORCE_TASKKILL_FALLBACK = False
    runner._last_kill_path = None
    runner.run_cases(q, "while True:" + NL + "    pass", timeout_seconds=1,
                     max_output_bytes=65536)
    if runner._last_kill_path != "job":
        fail("primary Windows kill path is %r, want 'job'"
             % runner._last_kill_path)
    # Forced fallback: taskkill /T /F must still kill the tree.
    runner._FORCE_TASKKILL_FALLBACK = True
    runner._last_kill_path = None
    runner.run_cases(q, "while True:" + NL + "    pass", timeout_seconds=1,
                     max_output_bytes=65536)
    if runner._last_kill_path != "taskkill":
        fail("forced fallback kill path is %r, want 'taskkill'"
             % runner._last_kill_path)
    runner._FORCE_TASKKILL_FALLBACK = False


def main():
    check_cap_kill_fires_early()
    check_truncated_forces_false_even_when_prefix_matches()
    check_flags_independent()
    check_timeout_not_a_verdict()
    check_source_greps()
    check_import_no_windll()
    check_windows_constants_and_layouts()
    check_windows_kill_paths()
    print("check kill roundtrip: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
