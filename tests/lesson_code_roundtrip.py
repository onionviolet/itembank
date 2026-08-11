"""Plan 09-05 Task 1: runnable lesson code through the one bounded runner.

Run as a direct script:

    python tests/lesson_code_roundtrip.py

Covers (09-05-PLAN Task 1 / 09-UI-SPEC "Runnable code example"):

1. An enabled Python fence posts edited source and receives the bounded
   observation -- stdout, stderr, exit_code, timed_out, truncated -- with no
   `passed`, `score`, `correct`, or `verdict` field (D-11).
2. Disabled profile language, missing runner setting, LAN-default refusal,
   unknown session/block, oversized source, extra authority-shaped fields,
   timeout, and output cap each produce an explicit bounded state before
   any unsafe work.
3. `run_cases()` retains its Phase 5 behavior while delegating its process
   invocation to the same `run_source()` primitive lesson Run uses (D-09:
   one runner).
4. A lesson Run changes no session cursor/teaching state and appends no
   response/hint/correctness evidence (D-11).
5. Automated DOM/source assertions pin the `09-UI-SPEC.md` runnable-code
   contract: stable `data-code-block` ids, visible labels, the exact
   ready/loading/completed/timeout/truncated/request-error/refusal copy,
   persistent concise `role="status"`, non-live labelled streams, edit
   retention, independent block state, focus hooks, editor escape
   instructions, and the responsive/reduced-motion hooks. Keyboard-only,
   narrow/zoom, and assistive behaviour are the manual phase-verification
   items, recorded in 09-VERIFICATION.md.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))
import itembank                                            # noqa: E402
import runner                                              # noqa: E402
import subjects                                            # noqa: E402
from surfaces import daemon, lesson                        # noqa: E402

CS_BANK = """# CS Lesson Loop (synthetic, 09-05)

## LESSON

### First Program

Reading two integers and printing their sum is the first skill this lesson
builds on. The example below is safe to run: it reads until end of input.

```python
print(sum(int(x) for x in input().split()))
```

A language the CS profile does not enable stays inert:

```ruby
puts "hi"
```

Q1. Write a program that prints the sum of two integers.
[OBJECTIVE: cs:io.sum]
[TYPE: check]
[LANG: python]
[MATCH: trimmed]
CASE) 5 7 :: 12
CASE) 1 2 :: 3
TRAP: x
CONFIDENCE: high
"""

TIMEOUT_BANK = """# CS Timeout Lesson (synthetic, 09-05)

## LESSON

### Loop

```python
while True:
    pass
```

Q1. Write a program that never terminates.
[OBJECTIVE: cs:io.loop]
[TYPE: check]
[LANG: python]
[MATCH: trimmed]
CASE) 1 :: 1
TRAP: x
CONFIDENCE: high
"""


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def start_daemon(workdir):
    """Launch `itembank daemon <workdir> --no-open --port 0` and return
    `(proc, url)` once the banner URL has been scraped."""
    args = [sys.executable, "-u", os.path.join(ROOT, "itembank.py"), "daemon",
            workdir, "--no-open", "--port", "0"]
    proc = subprocess.Popen(args, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True)
    lines = []

    def drain():
        for line in proc.stdout:
            lines.append(line)

    threading.Thread(target=drain, daemon=True).start()
    url = None
    for _ in range(300):
        for line in lines:
            m = re.search(r"http://127\.0\.0\.1:\d+/", line)
            if m:
                url = m.group(0).rstrip("/")
                break
        if url:
            break
        if proc.poll() is not None:
            break
        time.sleep(0.05)
    if not url:
        proc.kill()
        fail("daemon did not print a URL; output: " + "".join(lines))
    return proc, url


def get(url):
    with urllib.request.urlopen(url, timeout=10) as res:
        return res.status, res.read().decode("utf-8")


def post(url, payload):
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            return res.status, json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        try:
            return exc.code, json.loads(body)
        except ValueError:
            return exc.code, body


def write_bank(workdir, name, text):
    path = os.path.join(workdir, name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return path


def snapshot_state(workdir):
    """A byte-level snapshot of every session file and every evidence log in
    the worktree -- the D-11 proof that lesson Run writes nothing."""
    out = {}
    for dp, _, fns in os.walk(workdir):
        for fn in fns:
            if fn.startswith("session_") and fn.endswith(".json"):
                p = os.path.join(dp, fn)
                out[p] = ("file", open(p, "rb").read())
            if fn.endswith(".jsonl"):
                p = os.path.join(dp, fn)
                out[p] = ("file", open(p, "rb").read())
    return out


def cs_workdir():
    workdir = tempfile.mkdtemp(prefix="lesson-code-")
    write_bank(workdir, "cs_loop.md", CS_BANK)
    return workdir


def start_cs_session(base):
    """POST /api/start on the CS bank; returns the session id."""
    status, body = post(base + "/api/start",
                        {"bank": "cs_loop", "count": 1, "seed": 0,
                         "mode": "practice"})
    if status != 200:
        fail("/api/start returned %d: %r" % (status, body))
    return body["session_id"]


def test_runnable_page_contract():
    """Test 1 + UI contract: the served CS lesson carries the stable
    data-code-block id, the exact labels, the Run control, keyboard help,
    persistent role=status, labelled non-live streams, and the disabled
    fence keeps escaped source with the exact unavailable copy."""
    workdir = cs_workdir()
    try:
        proc, url = start_daemon(workdir)
        try:
            sid = start_cs_session(url)
            status, page = get(url + "/lesson/cs_loop")
            if status != 200:
                fail("GET /lesson/cs_loop returned %d" % status)
            if 'data-run-session="%s"' % sid not in page:
                fail("lesson page must carry the registered session id")
            # The python fence is runnable: sequential id, language label,
            # Example code label, visible source label, textarea, Run
            # example, keyboard help, status region, labelled streams.
            m = re.search(r'<div class="scroll runnable" '
                          r'data-code-block="(?P<id>\d+)" data-lang="python">',
                          page)
            if not m:
                fail("python fence must render a runnable block with a "
                     "stable data-code-block id")
            block = page[m.start():m.start() + 1200]
            for needle in (
                    lesson.RUN_EXAMPLE_LABEL,      # "Example code"
                    'class="run-source-label"',
                    '<textarea',
                    lesson.RUN_SOURCE_LABEL,       # "Source code"
                    lesson.RUN_READY_COPY,         # "Run example" button
                    lesson.RUN_HELP_COPY,          # Tab/Shift-Tab/Escape help
                    'class="run-status" role="status" aria-live="polite"',
                    'class="run-label">%s' % lesson.RUN_STDOUT_LABEL,
                    'class="run-label">%s' % lesson.RUN_STDERR_LABEL):
                if needle not in block:
                    fail("runnable block missing %r" % needle)
            if "print(sum(int(x)" not in block:
                fail("runnable block must prefill the escaped source")
            # The ruby fence is disabled under the CS profile: escaped source
            # and the exact disabled-language copy, no Run control.
            m2 = re.search(r'data-code-block="(?P<id>\d+)" data-lang="ruby"',
                           page)
            if not m2:
                fail("ruby fence must carry its own data-code-block id")
            block2 = page[m2.start():m2.start() + 800]
            if "run-go" in block2 or "run-source" in block2:
                fail("disabled-language block must render no Run control")
            if lesson.RUN_LANG_UNAVAILABLE_COPY.format(language="ruby") \
                    not in block2:
                fail("disabled-language block must carry the exact copy")
            if "puts" not in block2:
                fail("disabled-language block must retain escaped source")
            # The adapter script ships (a runnable block exists) and the
            # exact state copies are embedded.
            if "<script" not in page:
                fail("runnable page must ship the adapter script")
            for copy in (lesson.RUN_RUNNING_COPY, lesson.RUN_TIMEOUT_COPY,
                         lesson.RUN_TRUNCATED_COPY,
                         lesson.RUN_REQUEST_ERROR_COPY):
                if copy not in page:
                    fail("adapter must embed the exact copy %r" % copy)
            # data-code-block ids are sequential: python=1, ruby=2.
            if m.group("id") != "1" or m2.group("id") != "2":
                fail("data-code-block ids must be sequential in document "
                     "order, got %s and %s" % (m.group("id"), m2.group("id")))
        finally:
            proc.terminate()
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    print("runnable page contract: ids, labels, help, status, streams, "
          "disabled copy all held")


def test_lesson_run_observation():
    """Test 1: POST /api/lesson/run on the python fence returns the bounded
    observation only -- no passed/score/correct/verdict -- and honours the
    edited source."""
    workdir = cs_workdir()
    try:
        proc, url = start_daemon(workdir)
        try:
            sid = start_cs_session(url)
            status, body = post(
                url + "/api/lesson/run",
                {"session_id": sid, "block_id": "1", "language": "python",
                 "source": 'print(1 + 2)\n'})
            if status != 200:
                fail("lesson run returned %d: %r" % (status, body))
            for field in ("stdout", "stderr", "exit_code", "timed_out",
                          "truncated"):
                if field not in body:
                    fail("observation missing %r: %r" % (field, body))
            if body["stdout"].strip() != "3" or body["exit_code"] != 0 \
                    or body["timed_out"] or body["truncated"]:
                fail("bounded observation wrong: %r" % body)
            for banned in ("passed", "score", "correct", "verdict"):
                if banned in body:
                    fail("observation carries authority field %r: %r"
                         % (banned, body))
            # Editing is honoured: the submitted source is what runs.
            status2, body2 = post(
                url + "/api/lesson/run",
                {"session_id": sid, "block_id": "1", "language": "python",
                 "source": 'print(42)\n'})
            if status2 != 200 or body2["stdout"].strip() != "42":
                fail("edited source was not what ran: %r" % (body2,))
        finally:
            proc.terminate()
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    print("lesson run observation: bounded stdout/exit_code, edited source "
          "honoured, no authority field")


def test_lesson_run_refusals_and_bounds():
    """Test 2: disabled profile language, missing runner setting, LAN-default
    refusal, unknown session/block, oversized source, extra authority-shaped
    fields, timeout, and output cap each fail closed before unsafe work."""
    # --- unit: execution_refusal decision (LAN default + missing settings) -
    class H:
        lan = False

    if daemon.execution_refusal(H(), "python", {"languages": {"python": []},
                                                "allow_lan": False}) is not None:
        fail("loopback + allowed language must not refuse")
    if daemon.execution_refusal(H(), "python", {}) is None:
        fail("missing runner settings must refuse by language (bounded state)")
    H.lan = True
    ref = daemon.execution_refusal(H(), "python",
                                   {"languages": {"python": []},
                                    "allow_lan": False})
    if ref != daemon.LAN_REFUSAL_COPY:
        fail("LAN-default refusal must carry the locked copy, got %r" % ref)

    # --- unit: run_source bounds ---------------------------------------------
    loop = runner.run_source("python", "while True:\n    pass\n", "",
                             timeout_seconds=1,
                             max_output_bytes=65536)
    if not loop["timed_out"] or loop["exit_code"] is not None:
        fail("timeout run must carry timed_out and no exit code: %r" % loop)
    loud = runner.run_source("python", 'print("x" * 100000)\n', "",
                             timeout_seconds=5,
                             max_output_bytes=1024)
    # Phase 5's drain reads 4096-byte chunks, so the cap is chunk-granular:
    # a 1024-byte cap holds the output to at most one chunk (4096) while the
    # truncated flag reports the cap was hit.
    if not loud["truncated"] or len(loud["stdout"]) >= 8192:
        fail("output cap must truncate at the cap: %r" % loud)
    try:
        runner.run_source("ruby", "puts 1", "")
        fail("unknown language must raise UnknownLanguage")
    except runner.UnknownLanguage:
        pass

    # --- daemon-level integration -------------------------------------------
    workdir = cs_workdir()
    try:
        proc, url = start_daemon(workdir)
        try:
            sid = start_cs_session(url)
            base = url + "/api/lesson/run"
            # Extra authority-shaped field refused by name.
            status, body = post(base, {"session_id": sid, "block_id": "1",
                                       "language": "python",
                                       "source": "print(1)",
                                       "verdict": True})
            if status != 400:
                fail("authority field must be refused by name, got %d"
                     % status)
            # Unknown session.
            status, body = post(base, {"session_id": "no-such",
                                       "block_id": "1", "language": "python",
                                       "source": "print(1)"})
            if status != 404:
                fail("unknown session must 404, got %d" % status)
            # Unknown block id.
            status, body = post(base, {"session_id": sid, "block_id": "99",
                                       "language": "python",
                                       "source": "print(1)"})
            if status != 404:
                fail("unknown block must 404, got %d" % status)
            # Language the stored profile does not enable.
            status, body = post(base, {"session_id": sid, "block_id": "2",
                                       "language": "ruby",
                                       "source": "puts 1"})
            if status != 200 or "refused" not in body:
                fail("disabled profile language must refuse: %d %r"
                     % (status, body))
            if body["refused"] != lesson.RUN_LANG_UNAVAILABLE_COPY.format(
                    language="ruby"):
                fail("disabled-language refusal copy wrong: %r" % body)
            # Oversized source.
            status, body = post(base, {"session_id": sid, "block_id": "1",
                                       "language": "python",
                                       "source": "#" * 70000})
            if status != 400:
                fail("oversized source must 400, got %d" % status)
            # A real timeout through the daemon (settings-bound).
            status, body = post(base, {"session_id": sid, "block_id": "1",
                                       "language": "python",
                                       "source": "while True:\n pass\n"})
            if status != 200 or not body.get("timed_out"):
                fail("daemon timeout run must carry timed_out: %d %r"
                     % (status, body))
        finally:
            proc.terminate()
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    print("refusals and bounds: LAN/language/missing-settings, unknown "
          "session/block, authority fields, oversized source, timeout, cap")


def test_lesson_run_zero_evidence_and_session_delta():
    """Test 4: Run leaves the session cursor/teaching state and every
    evidence log byte-for-byte unchanged."""
    workdir = cs_workdir()
    try:
        proc, url = start_daemon(workdir)
        try:
            sid = start_cs_session(url)
            before = snapshot_state(workdir)
            if not before:
                fail("no session/evidence files to compare")
            for _ in range(2):
                status, body = post(
                    url + "/api/lesson/run",
                    {"session_id": sid, "block_id": "1", "language": "python",
                     "source": "print(7)\n"})
                if status != 200:
                    fail("lesson run failed: %d %r" % (status, body))
            after = snapshot_state(workdir)
            if after != before:
                fail("lesson Run changed session or evidence state: %r"
                     % {k: (v[0], len(v[1])) for k, v in
                        set(after.items()) ^ set(before.items())})
        finally:
            proc.terminate()
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    print("zero evidence/session delta: two Runs, byte-identical state")


def test_run_cases_retains_phase5_contract():
    """Test 3: run_cases() keeps its comparison contract while delegating to
    run_source() -- the per-case dicts stay (passed, actual, timed_out,
    truncated, case_index) and the timeout signal still reaches the scorer
    as no-verdict."""
    import runtime
    from model import parse_bank, parse_key_blocks
    workdir = cs_workdir()
    try:
        bank = write_bank(workdir, "cs_loop.md", CS_BANK)
        qs = itembank.load(bank)
        q = next(q for q in qs if q.get("type") == "check")
        source = "print(sum(int(x) for x in input().split()))\n"
        results = runner.run_cases(q, source, timeout_seconds=5,
                                   max_output_bytes=65536)
        if [r["case_index"] for r in results] != [0, 1]:
            fail("case_index order lost: %r" % results)
        if [r["passed"] for r in results] != [True, True]:
            fail("correct cases must pass: %r" % results)
        if [r["actual"] for r in results] != ["12\n", "3\n"]:
            fail("actual outputs wrong: %r" % results)
        for r in results:
            if set(r) != {"case_index", "passed", "actual", "timed_out",
                          "truncated"}:
                fail("run_cases dict shape changed: %r" % r)
        # The timeout signal survives as a None verdict (criterion 12).
        run = [{"passed": False, "actual": "", "timed_out": True,
                "truncated": False}]
        if runtime.score_response(q, run) is not None:
            fail("timed-out run must score None, not False")
        # The primitive exists and is the shape lesson Run consumes.
        out = runner.run_source("python", "print(1)\n", "")
        if set(out) != {"stdout", "stderr", "exit_code", "timed_out",
                        "truncated"}:
            fail("run_source shape wrong: %r" % out)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    print("run_cases contract: per-case dicts, order, timeout->None, "
          "run_source shape")


def test_static_and_refused_render_states():
    """UI contract: static/no-daemon, LAN-refused, and unknown-profile
    renders carry the exact unavailable copy and escaped source; the math
    and gate pages stay script-free without runnable blocks."""
    from surfaces import lesson as lesson_surface
    qs = itembank.load(os.path.join(ROOT, "fixtures", "lesson_bank.md"))
    les = itembank.parse_lesson(os.path.join(ROOT, "fixtures",
                                             "lesson_bank.md"))
    # Static render (cmd_lesson): no run control, exact static copy.
    page = lesson_surface.lesson_page(
        os.path.join(ROOT, "fixtures", "lesson_bank.md"), qs, les)
    if lesson_surface.RUN_STATIC_COPY not in page:
        fail("static render must carry the exact static copy")
    if "run-go" in page or "run-source" in page:
        fail("static render must carry no Run control")
    # LAN-refused daemon render: the exact LAN copy, no control. Uses the CS
    # bank so the fence language is profile-enabled and the LAN gate is the
    # deciding state.
    cs_dir = tempfile.mkdtemp(prefix="lesson-code-lan-")
    cs_path = write_bank(cs_dir, "cs_loop.md", CS_BANK)
    try:
        cs_qs = itembank.load(cs_path)
        cs_les = itembank.parse_lesson(cs_path)
        cs_profile = subjects.select_profile(
            cs_qs, subjects.load_registry(cs_dir))
        page_lan = lesson_surface.lesson_page(
            cs_path, cs_qs, cs_les, runtime=True, profile=cs_profile,
            session_id="sess-1", lan_refused=True)
        if lesson_surface.RUN_LAN_REFUSAL_COPY not in page_lan:
            fail("LAN-refused render must carry the exact LAN copy")
        if "run-go" in page_lan:
            fail("LAN-refused render must carry no Run control")
        # The fence enumeration the daemon resolves block ids against matches
        # the renderer's sequential ids for the CS fixture.
        if lesson_surface.lesson_fence_languages(cs_les) != \
                ["python", "ruby"]:
            fail("fence enumeration must be ['python', 'ruby'], got %r"
                 % lesson_surface.lesson_fence_languages(cs_les))
    finally:
        shutil.rmtree(cs_dir, ignore_errors=True)
    print("static/LAN render states: exact copy, no control, fence "
          "enumeration matches renderer")


def main():
    test_runnable_page_contract()
    test_lesson_run_observation()
    test_lesson_run_refusals_and_bounds()
    test_lesson_run_zero_evidence_and_session_delta()
    test_run_cases_retains_phase5_contract()
    test_static_and_refused_render_states()
    print("lesson code roundtrip: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
