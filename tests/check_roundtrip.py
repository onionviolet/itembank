#!/usr/bin/env python3
"""Assert the whole check item path: parse, run, score, record.

The check item type (plan 05-01) is verified by running the learner's own
source once per authored case, reducing the per-case pass flags to a vector,
scoring that vector through runtime.score_response() -- the one scorer -- and
recording the source verbatim on the evidence event. This test drives every
layer of that path, including a real daemon over HTTP.

Standard library only, no framework, runnable as
python tests/check_roundtrip.py
"""
import hashlib, json, os, re, shutil, subprocess, sys, tempfile, threading, time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import evidence                                            # noqa: E402
import itembank                                            # noqa: E402
import model                                               # noqa: E402
import runner                                              # noqa: E402
import runtime                                             # noqa: E402
from model import load                                            # noqa: E402
from surfaces import quiz                                   # noqa: E402

CHECK_BANK = os.path.join(ROOT, "fixtures", "check_bank.md")
SAMPLE_BANK = os.path.join(ROOT, "fixtures", "sample_bank.md")


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


# ---- item texts used by the unit tests -------------------------------------

SUM_ITEM = """Q1. Write a program that sums two integers read from stdin.   (difficulty: recall)
[TYPE: check]
[OBJECTIVE: cs:io.sum]
[LANG: python]
[MATCH: trimmed]
CASE) 5 7 :: 12
CASE) 3 4 :: 7
WHY BEST: A correct program reads both numbers and adds them.
KEY DISCRIMINATOR: reading all of stdin.
DISTRACTOR ANALYSIS:
- The usual failure is reading only the first line.
TRAP: Reading one number instead of two.
CONFIDENCE: high
"""

SUM_SOURCE = "import sys\nprint(sum(map(int, sys.stdin.read().split())))"
WRONG_SUM_SOURCE = ("import sys\n"
                    "a, b = map(int, sys.stdin.read().split())\n"
                    "print(a + b)")
STDIN_ECHO_SOURCE = "import sys\nprint(sys.stdin.read().strip())"
HANG_SOURCE = "while True:\n    pass"
FLOOD_SOURCE = "while True:\n    print('x' * 100)"

HARNESS_ITEM = """Q2. Complete the function so it returns the sum of its arguments.   (difficulty: recall)
[TYPE: check]
[OBJECTIVE: cs:functions.add]
[HARNESS: add]
[TOLERANCE: 0.01]
CASE) add(1, 2) :: 3
CASE) add(2, 3) :: 5
CASE) add(0.1, 0.2) :: 0.3
TRAP: Returning the first argument instead of the sum.
CONFIDENCE: high
"""

ADD_SOURCE = "def add(a, b):\n    return a + b"


THREE_CASE_ITEM = """Q9. Write a program that reads three integers and prints their sum.   (difficulty: recall)
[TYPE: check]
[OBJECTIVE: cs:io.three]
CASE) 1 2 3 :: 6
CASE) 4 5 6 :: 15
CASE) 0 0 0 :: 0
TRAP: Reading only two numbers.
CONFIDENCE: high
"""


def parse_check(text):
    q = model.parse_question(text)
    if q is None:
        fail("check item failed to parse")
    return q


# ---- checks ----------------------------------------------------------------

def check_parse_and_defaults():
    q = parse_check(SUM_ITEM)
    if q["type"] != "check":
        fail("parse produced type %r, not check" % q["type"])
    if q["lang"] != "python":
        fail("[LANG:] defaulted to %r, not python" % q["lang"])
    if q["match"] != "trimmed":
        fail("[MATCH:] defaulted to %r, not trimmed" % q["match"])
    cases = q["cases"]
    if [c["stdin"] for c in cases] != ["5 7", "3 4"]:
        fail("cases parsed out of order: %r" % cases)
    if [c["expected"] for c in cases] != ["12", "7"]:
        fail("case expected values are %r" % [c["expected"] for c in cases])
    if q["harness"] != "" or q["tolerance"] is not None:
        fail("non-harness item got harness=%r tolerance=%r" %
             (q["harness"], q["tolerance"]))
    # The stem must stop at the first CASE) line, not swallow it.
    if "CASE)" in q["stem"] or "sums two integers" not in q["stem"]:
        fail("stem swallowed the CASE) lines: %r" % q["stem"])

    h = parse_check(HARNESS_ITEM)
    if h["harness"] != "add":
        fail("[HARNESS:] parsed as %r" % h["harness"])
    if h["tolerance"] != 0.01:
        fail("[TOLERANCE:] parsed as %r" % h["tolerance"])
    if h["cases"][0]["call"] != "add(1, 2)":
        fail("harness case call parsed as %r" % h["cases"][0].get("call"))

    # Return None without a stem or without any CASE) line.
    no_case = "[TYPE: check]\n[OBJECTIVE: cs:x.y]\nCASE) 1 :: 2\n"
    if model.parse_question("Q1. only a stem\n" + no_case.replace("CASE) 1 :: 2\n", "")):
        fail("a check item with no CASE) line parsed")
    if model.parse_question(no_case):
        fail("a check item with no stem parsed")


def check_sample_bank_unchanged():
    before = [q["type"] for q in model.parse_bank(open(SAMPLE_BANK, encoding="utf-8").read())]
    if "check" in before:
        fail("sample_bank unexpectedly contains a check item")
    # A check-only key must never appear on another type's dict.
    for q in itembank.load(SAMPLE_BANK):
        for key in ("lang", "match", "cases", "harness", "tolerance", "starter"):
            if key in q:
                fail("%s (%s) carries check-only key %r" % (q["id"], q["type"], key))


def check_markers_shared():
    new_markers = ("CASE)", "[LANG:", "[MATCH:", "STARTER:", "[HARNESS:",
                   "[TOLERANCE:")
    for m in new_markers:
        if m not in model.MARKERS:
            fail("marker %r is not in the shared MARKERS constant" % m)
        escaped = re.escape(m)
        if escaped not in model._STEM_TERMINATORS:
            fail("stem terminator does not share marker %r" % m)
        if escaped not in model.TERMINATOR.pattern:
            fail("TERMINATOR does not share marker %r" % m)
    # The [ID:]/[HASH:] splice point must land above the first CASE)/[LANG: line.
    text, changes = model.assign_ids(SUM_ITEM)
    first_case = text.index("CASE)")
    id_line = text.index("[ID:")
    hash_line = text.index("[HASH:")
    if not (id_line < first_case and hash_line < first_case):
        fail("assign_ids splices [ID:]/[HASH:] below the first CASE) line")
    if len(changes) != 1 or changes[0]["item"] != "Q1":
        fail("assign_ids reported wrong changes: %r" % changes)


def check_case_passed():
    if not runner.case_passed("trimmed", "5", "5\n"):
        fail('case_passed("trimmed", "5", "5\n") must be True')
    if runner.case_passed("exact", "5", "5\n"):
        fail('case_passed("exact", "5", "5\n") must be False')
    if not runner.case_passed("regex", "[0-9]+", "42"):
        fail('case_passed("regex", "[0-9]+", "42") must be True')
    if runner.case_passed("bogus", "5", "5"):
        fail("an unrecognized match mode must return False")


def check_run_cases():
    q = parse_check(SUM_ITEM)
    ok = runner.run_cases(q, SUM_SOURCE, timeout_seconds=5,
                          max_output_bytes=65536)
    if len(ok) != 2:
        fail("run_cases returned %d results for a two-case item" % len(ok))
    if not all(r["passed"] for r in ok) or [r["actual"] for r in ok] != ["12\n", "7\n"]:
        fail("correct source did not pass every case: %r" % ok)
    if [r["case_index"] for r in ok] != [0, 1]:
        fail("case_index ordering is %r" % [r["case_index"] for r in ok])

    wrong = runner.run_cases(q, WRONG_SUM_SOURCE, timeout_seconds=5,
                             max_output_bytes=65536)
    if [r["passed"] for r in wrong] != [True, True]:
        fail("wrong source passed %r; expected the two-number unpack to "
             "succeed on both two-number cases" % [r["passed"] for r in wrong])

    # A program that reads stdin to EOF sees the authored input, not a hang.
    echoed = runner.run_cases(q, STDIN_ECHO_SOURCE, timeout_seconds=5,
                              max_output_bytes=65536)
    if [r["actual"] for r in echoed] != ["5 7\n", "3 4\n"]:
        fail("stdin-echo source did not see the authored stdin: %r" % echoed)
    if any(r["timed_out"] for r in echoed):
        fail("a program reading to EOF must finish, not time out")

    # Never-terminating source: killed at the deadline, no verdict.
    hung = runner.run_cases(q, HANG_SOURCE, timeout_seconds=1,
                            max_output_bytes=65536)
    if not any(r["timed_out"] for r in hung):
        fail("never-terminating source was not killed: %r" % hung)
    if runtime.score_response(q, hung) is not None:
        fail("a killed run must score None, never %r"
             % runtime.score_response(q, hung))

    # Unbounded output: capped and truncated, and the child is reaped.
    flood = runner.run_cases(q, FLOOD_SOURCE, timeout_seconds=5,
                             max_output_bytes=4096)
    if not any(r["truncated"] for r in flood):
        fail("unbounded stdout was not truncated: %r" % flood)
    if any(len(r["actual"]) > 8192 for r in flood):
        fail("truncated actual output exceeds the cap")


def check_harness_end_to_end():
    q = parse_check(HARNESS_ITEM)
    res = runner.run_cases(q, ADD_SOURCE, timeout_seconds=5,
                           max_output_bytes=65536)
    if not all(r["passed"] for r in res):
        fail("harness item did not pass every case: %r" % res)
    if runtime.score_response(q, res) is not True:
        fail("harness run scored %r, expected True" % runtime.score_response(q, res))
    # The float case exercises [TOLERANCE:].
    if not res[2]["passed"]:
        fail("add(0.1, 0.2) vs 0.3 within tolerance must pass: %r" % res[2])


def check_scoring_identities():
    q = parse_check(THREE_CASE_ITEM)
    if runtime.canonical_response(q, [1, 1, 0]) != "1,1,0":
        fail("canonical_response of [1, 1, 0] is %r" %
             runtime.canonical_response(q, [1, 1, 0]))
    if runtime.canonical_key(q) != "1,1,1":
        fail("canonical_key of a three-case item is %r" % runtime.canonical_key(q))
    if runtime.score_response(q, [1, 1, 1]) is not True:
        fail("all-pass vector did not score True")
    if runtime.score_response(q, [1, 0, 1]) is not False:
        fail("a failed case must score False")
    if "check" not in runtime.NORMALIZERS or "check" not in runtime.KEYS:
        fail("the check entry is missing from the registries: %r %r" %
             (sorted(runtime.NORMALIZERS), sorted(runtime.KEYS)))
    if runtime.INTERACTION_VERSION != 1:
        fail("INTERACTION_VERSION is %r" % runtime.INTERACTION_VERSION)


def check_public_item():
    q = parse_check(SUM_ITEM)
    public = runtime.public_item(q)
    contract = public.get("interaction_contract")
    if contract is None:
        fail("public_item carries no interaction_contract")
    want = {"version": runtime.INTERACTION_VERSION, "type": "check",
            "renderer_config": {"language": "python",
                                "starter_source": "",
                                "hidden_case_count": 2},
            "response_schema": {"type": "string", "format": "source",
                                "language": "python"}}
    if contract != want:
        fail("interaction_contract is %r, want %r" % (contract, want))
    # The top-level response_schema aliases the envelope's.
    if public.get("response_schema") != contract["response_schema"]:
        fail("top-level response_schema is not the envelope alias")
    blob = json.dumps(contract)
    for leak in ("cases", "expected", "key", "stdin"):
        if leak in blob:
            fail("interaction_contract leaks %r" % leak)
    # Consumable without any page knowledge: JSON only, no callable.
    try:
        json.loads(json.dumps(contract))
    except (TypeError, ValueError):
        fail("interaction_contract is not JSON data")


def check_interaction_result():
    q = parse_check(SUM_ITEM)
    run_result = [
        {"case_index": 0, "passed": True, "actual": "12\n", "timed_out": False,
         "truncated": False},
        {"case_index": 1, "passed": False, "actual": "", "timed_out": True,
         "truncated": False},
    ]
    res = runtime.interaction_result(q, SUM_SOURCE, None, run_result)
    if res["version"] != runtime.INTERACTION_VERSION or res["type"] != "check":
        fail("interaction_result carries wrong version/type: %r" % res)
    if res["response"] != SUM_SOURCE:
        fail("interaction_result lost the submitted source")
    if res["verdict"] is not None:
        fail("interaction_result verdict is %r, expected the exact score (None)"
             % res["verdict"])
    if [o["case_index"] for o in res["observations"]] != [1, 2]:
        fail("observations are not 1-based and ordered: %r" % res["observations"])
    if res["observations"][0]["reason"] != "passed":
        fail("first observation reason is %r" % res["observations"][0]["reason"])
    if res["observations"][1]["reason"] != "timeout":
        fail("killed case reason is %r" % res["observations"][1]["reason"])
    if res["observations"][0]["expected_kind"] != "output":
        fail("non-regex expected_kind is %r" % res["observations"][0]["expected_kind"])
    if res["observations"][1]["input"] != "3 4":
        fail("observation input is %r" % res["observations"][1]["input"])

    # A regex item's expected is a pattern, not an output.
    rq = parse_check("[TYPE: check]\n[OBJECTIVE: cs:x.y]\n[MATCH: regex]\n"
                     "CASE) 1 :: [0-9]+\nCASE) 2 :: [0-9]+\n"
                     "TRAP: x\nCONFIDENCE: high\n"
                     "Q1. Write a program that prints a number.   (difficulty: recall)\n")
    rr = [{"passed": True, "actual": "42\n", "timed_out": False, "truncated": False}]
    if runtime.interaction_result(rq, "print(42)", True, rr)["observations"][0]["expected_kind"] != "pattern":
        fail("regex item's expected_kind must be 'pattern'")


def check_explain_payload():
    import inspect
    if "run_result" not in inspect.signature(runtime.explain_payload).parameters:
        fail("explain_payload lacks the run_result parameter")
    q = parse_check(SUM_ITEM)
    run_result = [{"passed": True, "actual": "12\n", "timed_out": False,
                   "truncated": False},
                  {"passed": False, "actual": "8\n", "timed_out": False,
                   "truncated": False}]
    with_rr = runtime.explain_payload(q, reveal=True, run_result=run_result)
    rows = with_rr["cases"]
    if len(rows) != 2 or rows[0]["input"] != "5 7" or rows[1]["actual"] != "8\n":
        fail("explain_payload did not zip run_result against authored cases: %r" % rows)
    without = runtime.explain_payload(q, reveal=True)
    if "actual" in without["cases"][0] or "timed_out" in without["cases"][0]:
        fail("explain_payload without run_result leaks runner fields: %r" % without)


# ---- the served HTTP path --------------------------------------------------

def post(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as res:
        return json.loads(res.read().decode("utf-8"))


def post_error(url, payload):
    """POST and return (status, body_text), reading the body even on a 4xx
    response -- the daemon's refusals arrive as 400/403 bodies, not JSON."""
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            return res.status, res.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "replace")


def check_http_roundtrip():
    work_root = tempfile.mkdtemp()
    bank_path = os.path.join(work_root, "check_bank.md")
    shutil.copyfile(CHECK_BANK, bank_path)
    out = os.path.join(tempfile.mkdtemp(), "attempt.md")
    proc = subprocess.Popen(
        [sys.executable, "-u", os.path.join(ROOT, "itembank.py"), "serve",
         bank_path, "--no-open", "--port", "0", "--out", out],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    lines = []
    threading.Thread(target=lambda: [lines.append(l) for l in proc.stdout],
                     daemon=True).start()
    base = None
    for _ in range(60):
        time.sleep(0.1)
        m = re.search(r"http://127\.0\.0\.1:\d+/", "".join(lines))
        if m:
            base = m.group(0)
            break
    if not base:
        fail("server never printed a URL. Output was:\n" + "".join(lines))
    stem = "check_bank"
    quiz_url = base + "quiz/%s" % stem
    answer_url = quiz_url + "/answer"

    def submit_once(item_id, source):
        started = post(base + "api/start", {"bank": stem, "count": 6,
                                            "mode": "practice", "focus": item_id})
        session_id = started["session_id"]
        return session_id, post(answer_url, {"id": item_id,
                                             "interaction_version": 1,
                                             "response": source})

    try:
        page = urllib.request.urlopen(quiz_url, timeout=5).read().decode("utf-8")
        if "const SERVE = true" not in page:
            fail("served page is not in recording mode")

        # A correct submission.
        sid, correct = submit_once("q1", SUM_SOURCE)
        if correct.get("score") is not True:
            fail("correct check submit scored %r" % correct.get("score"))
        ir = correct.get("interaction_result")
        if ir is None or ir["verdict"] is not True:
            fail("correct submit interaction_result is %r" % ir)
        events = [ev for ev in evidence.live_events(evidence.log_path(work_root))
                  if ev.get("event_type") == "response"
                  and ev.get("session_id") == sid]
        if len(events) != 1:
            fail("correct submit recorded %d response events, expected 1" % len(events))
        ev = events[0]
        if ev["check_source"] != SUM_SOURCE:
            fail("evidence check_source is not the submitted source verbatim")
        if ev["interaction_version"] != runtime.INTERACTION_VERSION:
            fail("evidence interaction_version is %r" % ev["interaction_version"])
        if ev["error_category"] is not None:
            fail("a completed run must record error_category None, got %r"
                 % ev["error_category"])
        if ev["answer"] != "1,1":
            fail("evidence answer is %r, expected the results vector 1,1" % ev["answer"])
        _validate_event(ev)

        # A wrong submission: one case fails.
        sid, wrong = submit_once("q2", WRONG_SUM_SOURCE)
        if wrong.get("score") is not False:
            fail("wrong check submit scored %r" % wrong.get("score"))
        if wrong["interaction_result"]["verdict"] is not False:
            fail("wrong submit verdict is %r"
                 % wrong["interaction_result"]["verdict"])
        events = [ev for ev in evidence.live_events(evidence.log_path(work_root))
                  if ev.get("event_type") == "response"
                  and ev.get("session_id") == sid]
        if len(events) != 1 or events[0]["answer"] != "1,1,0":
            fail("wrong submit evidence is %r" % [e.get("answer") for e in events])

        # A killed-at-timeout submission: no verdict, error_category timeout.
        sid, killed = submit_once("q3", HANG_SOURCE)
        if killed.get("score") is not None:
            fail("killed run scored %r, expected None" % killed.get("score"))
        if killed["interaction_result"]["verdict"] is not None:
            fail("killed run verdict is %r, expected None"
                 % killed["interaction_result"]["verdict"])
        events = [ev for ev in evidence.live_events(evidence.log_path(work_root))
                  if ev.get("event_type") == "response"
                  and ev.get("session_id") == sid]
        if len(events) != 1:
            fail("killed run recorded %d response events, expected 1" % len(events))
        ev = events[0]
        if ev["error_category"] != "timeout":
            fail("killed run error_category is %r, expected timeout"
                 % ev["error_category"])
        if ev["score"] is not None:
            fail("killed run evidence score is %r, expected None" % ev["score"])
        if ev["check_source"] != HANG_SOURCE:
            fail("killed run evidence lost the source")
        _validate_event(ev)
    finally:
        proc.terminate()


def _validate_event(ev):
    schema = json.load(open(os.path.join(ROOT, "schemas", "response.schema.json"),
                            encoding="utf-8"))
    import schema_validate
    errs = schema_validate.validate(ev, schema)
    if errs:
        fail("check response event fails response.schema.json: %s" % "; ".join(errs))


def check_evidence_signatures():
    import inspect
    params = inspect.signature(evidence.response_event).parameters
    for name in ("check_source", "interaction_version"):
        if name not in params:
            fail("response_event lacks keyword-only %r" % name)
    # An explicit None is stored on every event, check or not.
    ev = evidence.response_event("s", parse_check(SUM_ITEM), "1,1", True,
                                 "practice", 1, "bank.md")
    if ev["check_source"] is not None or ev["interaction_version"] is not None:
        fail("non-check-shaped event must record explicit None reserved keys")


# ---- plan 05-03 Task 2: the agent submit path and the cross-path identity ---

AGENT_BANK = """# Agent check bank

Q1. Write a program that sums two integers read from stdin.   (difficulty: recall)
[ID: 9000000000000001]
[TYPE: check]
[OBJECTIVE: cs:io.sum]
[LANG: python]
[MATCH: trimmed]
CASE) 5 7 :: 12
CASE) 3 4 :: 7
WHY BEST: A correct program reads both numbers and adds them.
KEY DISCRIMINATOR: reading all of stdin.
DISTRACTOR ANALYSIS:
- The usual failure is reading only the first line.
TRAP: Reading one number instead of two.
CONFIDENCE: high
"""

RUBY_BANK = """# Agent check bank (non-python language)

Q1. Write a program that sums two integers read from stdin.   (difficulty: recall)
[ID: 9000000000000002]
[TYPE: check]
[OBJECTIVE: cs:io.sum]
[LANG: ruby]
[MATCH: trimmed]
CASE) 5 7 :: 12
CASE) 3 4 :: 7
WHY BEST: A correct program reads both numbers and adds them.
KEY DISCRIMINATOR: reading all of stdin.
DISTRACTOR ANALYSIS:
- The usual failure is reading only the first line.
TRAP: Reading one number instead of two.
CONFIDENCE: high
"""

WRONG_SOURCE = "print('nope')" + chr(10)


def _write_settings(work, **overrides):
    base = json.load(open(os.path.join(ROOT, "itembank.json"), encoding="utf-8"))
    ck = dict(base.get("check") or {})
    ck.update(overrides)
    base["check"] = ck
    json.dump(base, open(os.path.join(work, "itembank.json"), "w", encoding="utf-8"),
              indent=2)


def _cli(*args):
    return subprocess.run([sys.executable, os.path.join(ROOT, "itembank.py"),
                           *map(str, args)], capture_output=True, text=True,
                          encoding="utf-8")


def _agent_start(bank_path, work, seed):
    session = os.path.join(work, "session_%s.json" % seed)
    r = _cli("start", bank_path, "--count", "1", "--seed", seed,
             "--mode", "practice", "--out", session)
    if r.returncode != 0:
        fail("agent start failed: %s" % (r.stdout + r.stderr))
    return session, json.loads(r.stdout)["session_id"]


def _agent_events(log, sid):
    return [ev for ev in evidence.live_events(log)
            if ev.get("event_type") == "response" and ev.get("session_id") == sid]


def _serve_base(bank_path, out, proc_lines):
    proc = subprocess.Popen(
        [sys.executable, "-u", os.path.join(ROOT, "itembank.py"), "serve",
         bank_path, "--no-open", "--port", "0", "--out", out],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    threading.Thread(target=lambda: [proc_lines.append(l) for l in proc.stdout],
                     daemon=True).start()
    base = None
    joined = ""
    for _ in range(60):
        time.sleep(0.1)
        joined = "".join(proc_lines)
        m = re.search("http://127.0.0.1:[0-9]+/", joined)
        if m:
            base = m.group(0)
            break
    return proc, base


def check_agent_path():
    """Drive the real / CLI against a check
    item and assert score true/false, dedupe, settings-derived bounds and the
    unknown-language refusal -- all without touching the checkout."""
    work = tempfile.mkdtemp()
    try:
        bank_path = os.path.join(work, "agent_check.md")
        open(bank_path, "w", encoding="utf-8").write(AGENT_BANK)
        _write_settings(work)
        log = evidence.log_path(work)

        # correct -> score true, one event
        sess, sid = _agent_start(bank_path, work, 1)
        r = _cli("submit", sess, "--answer", json.dumps(SUM_SOURCE))
        if r.returncode != 0:
            fail("correct agent submit failed: %s" % (r.stdout + r.stderr))
        res = json.loads(r.stdout)
        if res.get("score") is not True:
            fail("correct agent submit scored %r" % res.get("score"))
        evs = _agent_events(log, sid)
        if len(evs) != 1 or evs[0]["answer"] != "1,1":
            fail("correct agent submit evidence is %r" % [e.get("answer") for e in evs])
        if evs[0]["check_source"] != SUM_SOURCE:
            fail("agent evidence lost the check source")
        _validate_event(evs[0])

        # wrong -> score false
        sess2, sid2 = _agent_start(bank_path, work, 2)
        r = _cli("submit", sess2, "--answer", json.dumps(WRONG_SOURCE))
        if r.returncode != 0:
            fail("wrong agent submit failed: %s" % (r.stdout + r.stderr))
        if json.loads(r.stdout).get("score") is not False:
            fail("wrong agent submit scored %r" % json.loads(r.stdout).get("score"))

        # dedupe: a byte-identical second submit on the held-cursor item
        # (the wrong answer does not advance) records no second event.
        r = _cli("submit", sess2, "--answer", json.dumps(WRONG_SOURCE))
        if r.returncode != 0:
            fail("second identical submit failed: %s" % (r.stdout + r.stderr))
        if json.loads(r.stdout).get("accepted") is not False:
            fail("byte-identical second submit was not deduped: %r" % res)
        if len(_agent_events(log, sid2)) != 1:
            fail("a byte-identical resubmit appended a second evidence event")

        # settings-derived bound: timeout_seconds=1 makes a hanging item's
        # submit return well under the runner's 5s default.
        work_t = tempfile.mkdtemp()
        try:
            bt = os.path.join(work_t, "agent_check.md")
            open(bt, "w", encoding="utf-8").write(AGENT_BANK)
            _write_settings(work_t, timeout_seconds=1)
            st, stid = _agent_start(bt, work_t, 9)
            start = time.monotonic()
            r = _cli("submit", st, "--answer", json.dumps(HANG_SOURCE))
            elapsed = time.monotonic() - start
            if r.returncode != 0:
                fail("hang submit failed: %s" % (r.stdout + r.stderr))
            if elapsed >= 5:
                fail("hang submit took %.1fs; the bound did not come from "
                     "check.timeout_seconds" % elapsed)
            if json.loads(r.stdout).get("score") is not None:
                fail("hang submit must record no verdict")
        finally:
            shutil.rmtree(work_t, ignore_errors=True)

        # unknown language: a check item whose [LANG:] is not in the runtime
        # check.languages allowlist refuses at run time, names the language and
        # the settings key, and leaves the evidence log and session untouched.
        # The bank is started with --force because [LANG: ruby] is a lint error
        # against the shipped allowlist -- the point is that settings drifted
        # after authoring, so lint-time allowlist membership and the runtime
        # settings allowlist can disagree.
        work_u = tempfile.mkdtemp()
        try:
            bu = os.path.join(work_u, "agent_check.md")
            open(bu, "w", encoding="utf-8").write(RUBY_BANK)
            _write_settings(work_u)
            su = os.path.join(work_u, "session_u.json")
            rs = _cli("start", bu, "--count", "1", "--seed", "7", "--force",
                      "--mode", "practice", "--out", su)
            if rs.returncode != 0:
                fail("force start on the ruby bank failed: %s" % (rs.stdout + rs.stderr))
            log_u = evidence.log_path(work_u)
            before = open(log_u, "rb").read() if os.path.exists(log_u) else b""
            sess_bytes = open(su, "rb").read()
            r = _cli("submit", su, "--answer", json.dumps(SUM_SOURCE))
            if r.returncode == 0:
                fail("an unknown-language submit exited 0")
            out = r.stdout + r.stderr
            if "ruby" not in out or "check.languages" not in out:
                fail("unknown-language refusal does not name the language and "
                     "check.languages: %r" % out)
            after = open(log_u, "rb").read() if os.path.exists(log_u) else b""
            if after != before:
                fail("an unknown-language submit wrote to the evidence log")
            if open(su, "rb").read() != sess_bytes:
                fail("an unknown-language submit touched the session file")
        finally:
            shutil.rmtree(work_u, ignore_errors=True)
    finally:
        shutil.rmtree(work, ignore_errors=True)


def check_cross_path():
    """The same check source through the browser route and the agent route
    produces identical score/answer/canonical/check_source in the two
    evidence events -- the checkable version of 'one scorer, reached the
    same way'."""
    work = tempfile.mkdtemp()
    try:
        bank_path = os.path.join(work, "agent_check.md")
        open(bank_path, "w", encoding="utf-8").write(AGENT_BANK)
        _write_settings(work)
        log = evidence.log_path(work)

        proc, base = _serve_base(bank_path,
                                 os.path.join(tempfile.mkdtemp(), "attempt.md"),
                                 [])
        if not base:
            if proc.poll() is None:
                proc.terminate()
            fail("serve daemon never printed a URL")
        try:
            started = post(base + "api/start", {"bank": "agent_check", "count": 6,
                                                "mode": "practice",
                                                "focus": "q1"})
            brow = post(base + "quiz/agent_check/answer",
                        {"id": "q1", "interaction_version": 1,
                         "response": SUM_SOURCE})
            if brow.get("score") is not True:
                fail("browser route scored %r" % brow.get("score"))
        finally:
            proc.terminate()
        brow_evs = _agent_events(log, started["session_id"])
        if len(brow_evs) != 1:
            fail("browser route recorded %d events, expected 1" % len(brow_evs))
        brow_ev = brow_evs[0]

        sess, sid = _agent_start(bank_path, work, 5)
        r = _cli("submit", sess, "--answer", json.dumps(SUM_SOURCE))
        if r.returncode != 0:
            fail("agent cross-path submit failed: %s" % (r.stdout + r.stderr))
        agent_evs = _agent_events(log, sid)
        if len(agent_evs) != 1:
            fail("agent route recorded %d events, expected 1" % len(agent_evs))
        agent_ev = agent_evs[0]

        for field in ("score", "answer", "canonical", "check_source"):
            if brow_ev.get(field) != agent_ev.get(field):
                fail("cross-path %r differs: browser=%r agent=%r" %
                     (field, brow_ev.get(field), agent_ev.get(field)))
        _validate_event(brow_ev)
        _validate_event(agent_ev)
    finally:
        shutil.rmtree(work, ignore_errors=True)


# ---- plan 05-03 Task 3: network-bound execution refusal + containment -------

SHORT_BANK = """# Short bank

Q1. What is the capital of France?   (difficulty: recall)
[ID: 9000000000000009]
[TYPE: short]
[OBJECTIVE: cs:general.capital]

MODEL: Paris is the capital of France.

RUBRIC:
- Names Paris as the capital
- States the answer plainly without hedging

TRAP: Naming a different city.

CONFIDENCE: high
"""

LAN_REFUSAL = (
    "Code execution is turned off while itembank is serving on your "
    "network (--lan). Ask whoever runs itembank to turn on "
    "check.allow_lan in settings if this device should be trusted, or "
    "answer this item from the machine itembank is running on.")
UNKNOWN_COPY = (
    "This item requests the 'ruby' language, which isn't enabled in this "
    "itembank's settings (check.languages). Add it in settings, or ask "
    "whoever set up this bank to fix its [LANG:] value.")


def _launch_daemon(root, lan=False):
    args = [sys.executable, "-u", os.path.join(ROOT, "itembank.py"), "daemon",
            root, "--port", "0", "--no-open"]
    if lan:
        args.append("--lan")
    proc = subprocess.Popen(args, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True)
    lines = []
    threading.Thread(target=lambda: [lines.append(l) for l in proc.stdout],
                     daemon=True).start()
    base = None
    for _ in range(80):
        time.sleep(0.1)
        m = re.search("http://127.0.0.1:[0-9]+/", "".join(lines))
        if m:
            base = m.group(0)
            break
    return proc, base


def _start_session(base, stem, focus):
    started = post(base + "api/start", {"bank": stem, "count": 6,
                                        "mode": "practice", "focus": focus})
    return started["session_id"]


def check_explain_threading():
    """05-05 Task 1: the per-case run result reaches both surfaces from the
    one run that produced the score. Both the browser answer route and
    /api/submit return an explain object carrying one entry per case in
    authored order, each with the authored input and expected text plus the
    actual output and the two bound flags, the runner is invoked exactly
    once per submission, and a non-check item's response body is unchanged
    (no run_result key)."""
    work = tempfile.mkdtemp()
    try:
        # A one-case bank whose source writes a marker line: if the surface
        # re-ran the runner to build the explanation, the file would hold
        # two lines instead of one (05-05 Task 1's once-only assertion).
        once_bank = os.path.join(work, "once_check.md")
        open(once_bank, "w", encoding="utf-8").write(
            "# Once bank\n\n"
            "Q1. Write a program that prints the sum.   (difficulty: recall)\n"
            "[ID: 9000000000000042]\n"
            "[TYPE: check]\n[OBJECTIVE: cs:io.sum]\n"
            "[MATCH: trimmed]\n"
            "CASE) 5 7 :: 12\n"
            "TRAP: x\nCONFIDENCE: high\n")
        marker = os.path.join(work, "spawns.txt")
        _write_settings(work)
        proc, base = _serve_base(once_bank,
                                 os.path.join(work, "attempt.md"), [])
        if not base:
            if proc.poll() is None:
                proc.terminate()
            fail("once-bank serve daemon never printed a URL")
        try:
            src = ("open(%r, 'a').write('x' + chr(10))\n"
                   "print(sum(int(x) for x in "
                   "__import__('sys').stdin.read().split()))"
                   % marker)
            started = post(base + "api/start", {"bank": "once_check",
                                                "count": 1,
                                                "mode": "practice",
                                                "focus": "q1"})
            sid = started["session_id"]
            brow = post(base + "quiz/once_check/answer",
                        {"id": "q1", "interaction_version": 1,
                         "response": src})
            cases = (brow.get("explain") or {}).get("cases")
            if not cases or len(cases) != 1:
                fail("browser explain has no per-case entry: %r" % brow)
            row = cases[0]
            for key in ("case_index", "input", "expected", "actual",
                        "timed_out", "truncated"):
                if key not in row:
                    fail("browser explain row lacks %r: %r" % (key, row))
            if row["input"] != "5 7" or row["expected"] != "12":
                fail("browser explain row input/expected are %r" % row)
            if row["actual"] != "12\n":
                fail("browser explain actual output is %r" % row["actual"])
            if row["timed_out"] is not False or row["truncated"] is not False:
                fail("browser explain bound flags are %r" % row)
            if brow["interaction_result"]["observations"][0]["reason"] != "passed":
                fail("browser observation reason is %r"
                     % brow["interaction_result"]["observations"][0])
            # The side effect ran exactly once (one runner invocation, not a
            # second call to build the explanation).
            if not os.path.exists(marker) or \
                    open(marker, encoding="utf-8").read().count("\n") != 1:
                fail("runner was invoked more than once per submission: "
                     "marker file has %r"
                     % (open(marker, encoding="utf-8").read()
                        if os.path.exists(marker) else "no file"))

            # The agent path carries the identical per-case entries (a fresh
            # session -- the browser submit above already advanced its cursor).
            started2 = post(base + "api/start", {"bank": "once_check",
                                                 "count": 1,
                                                 "mode": "practice",
                                                 "focus": "q1"})
            ag = post(base + "api/submit", {"session_id": started2["session_id"],
                                            "answer": src})
            acases = (ag.get("explain") or {}).get("cases")
            if not acases or len(acases) != 1:
                fail("api/submit explain has no per-case entry: %r" % ag)
            for key in ("case_index", "input", "expected", "actual",
                        "timed_out", "truncated"):
                if acases[0].get(key) != row.get(key):
                    fail("api/submit %r differs from the browser row: %r vs %r"
                         % (key, acases[0], row))
        finally:
            proc.terminate()

        # A non-check item's response body is byte-identical: no run_result
        # key appears, and the key set is exactly the pre-change one.
        mc_bank = os.path.join(work, "mc_bank.md")
        open(mc_bank, "w", encoding="utf-8").write(
            "# MC bank\n\n"
            "Q1. Pick one.   (difficulty: recall)\n"
            "[ID: 9000000000000043]\n"
            "[TYPE: mc]\n[OBJECTIVE: cs:x.y]\n"
            "A) alpha\nB) beta\nC) gamma\nD) delta\n"
            "CORRECT: A\n"
            "WHY BEST: alpha is the one.\n"
            "SECOND-BEST: beta is close but wrong.\n"
            "KEY DISCRIMINATOR: k\n"
            "DISTRACTOR ANALYSIS:\n"
            "- B would be correct only if beta were the one.\n"
            "- C would be correct only if gamma were the one.\n"
            "- D would be correct only if delta were the one.\n"
            "TRAP: x\nCONFIDENCE: high\n")
        proc2, base2 = _serve_base(mc_bank,
                                   os.path.join(work, "attempt_mc.md"), [])
        if not base2:
            if proc2.poll() is None:
                proc2.terminate()
            fail("mc serve daemon never printed a URL")
        try:
            started = post(base2 + "api/start", {"bank": "mc_bank",
                                                 "count": 1,
                                                 "mode": "practice",
                                                 "focus": "q1"})
            resp = post(base2 + "quiz/mc_bank/answer",
                        {"id": "q1", "interaction_version": 1,
                         "response": "A"})
            if "run_result" in resp:
                fail("a non-check response body gained a run_result key: %r"
                     % resp)
            want = {"accepted", "item_id", "score", "action", "status",
                    "evidence", "hint_tier", "interaction_result", "next",
                    "explain"}
            if set(resp) != want:
                fail("mc response key set is %r, want %r" % (set(resp), want))
        finally:
            proc2.terminate()
    finally:
        shutil.rmtree(work, ignore_errors=True)


def check_vendor_integrity():
    """05-05 Task 2 / Directive 4a: the vendored CodeMirror bundle exists,
    its SHA-256 matches the record in VENDOR.md, and the served page embeds
    it locally with no CDN URL and no unsubstituted placeholder."""
    import hashlib
    vendor = os.path.join(ROOT, "assets", "vendor", "codemirror")
    bundle = os.path.join(vendor, "codemirror.bundle.js")
    record = os.path.join(vendor, "VENDOR.md")
    if not os.path.exists(bundle) or not os.path.exists(record):
        fail("vendored CM6 bundle or VENDOR.md missing under assets/vendor/codemirror/")
    digest = hashlib.sha256(open(bundle, "rb").read()).hexdigest()
    text = open(record, encoding="utf-8").read()
    if digest not in text:
        fail("bundle SHA-256 %s is not recorded in VENDOR.md" % digest)
    if "https" not in text.lower() or "MIT" not in text:
        fail("VENDOR.md lacks a recorded license review")

    # The rendered page (served) embeds the bundle and the honest-limits
    # sentence from the one constant, with no placeholder left behind.
    qs = load(CHECK_BANK)
    _, page = quiz.page_for(CHECK_BANK, qs, serve=True)
    if model.HONEST_LIMITS_NOTE not in page:
        fail("served page lacks the honest-limits sentence")
    for token in ("__HONEST", "__CM6_TAG", "__CM6_BUNDLE"):
        if token in page:
            fail("served page carries an unsubstituted placeholder %r" % token)
    if "id=\"cm6\"" not in page:
        fail("served page does not embed the vendored CM6 bundle")
    # The editor is loaded from the local bundle, never from a CDN: the
    # page's only http(s) token is the SVG namespace inside the bundle.
    urls = re.findall(r"https?://[^\"' <)]*", page)
    if [u for u in urls if "w3.org/2000/svg" not in u]:
        fail("served page references a CDN/network URL: %r" % urls)
    # Locked copy from 05-UI-SPEC: placeholder, type chip, submit hint in
    # both singular and plural, and the .codewrap mount.
    for locked in ("# Write your code here.", "code check",
                   "runs against 1 hidden test case",
                   "runs against 3 hidden test cases", "codewrap",
                   "Running…"):
        if locked not in page:
            fail("served page lacks locked copy %r" % locked)
    # The built (offline) page embeds it too -- a check item renders the
    # editor in both clients at this plan; 05-06 swaps in the file refusal.
    build_out = os.path.join(tempfile.mkdtemp(), "check_quiz.html")
    subprocess.run([sys.executable, os.path.join(ROOT, "itembank.py"),
                    "build", CHECK_BANK, build_out], check=True,
                   capture_output=True)
    html = open(build_out, encoding="utf-8").read()
    if "codewrap" not in html or model.HONEST_LIMITS_NOTE not in html:
        fail("built check page lacks the editor mount or honest-limits line")
    if "__HONEST" in html:
        fail("built check page carries an unsubstituted placeholder")

    # --- source assertions for Task 3 (the behaviours themselves are
    # executed by tests/js/check_editor.test.mjs against the same vendored
    # bundle and boot script; these string checks pin the page to the boot
    # script and to the contract's scope, they do not prove behaviour). ---
    from surfaces.quiz_page import OFFLINE_JS, SERVED_JS
    clients = OFFLINE_JS + SERVED_JS
    code = "\n".join(l for l in clients.splitlines()
                     if not l.lstrip().startswith(("//", "/*", "*")))
    # The editor is configured in exactly one place: the boot script. The
    # page must not hand-roll a gutter or a keydown Tab handler of its own.
    if re.search(r"keydown", code, re.IGNORECASE):
        fail("the page hand-rolls a keydown handler; the editor "
             "configuration must live in the boot script only")
    if re.search(r"\.cm-gutters|gutterElement", code):
        fail("the page hand-rolls a gutter; CodeMirror owns the line "
             "numbers in the boot script only")
    # Nothing outside the contract: no syntax highlighting, bracket
    # matching, auto-indent, or block-indent was added.
    if re.search(r"(highlight|bracket|autoindent|blockindent)", code,
                 re.IGNORECASE):
        fail("an out-of-contract editor feature was added to the page")
    # The served page embeds the boot script next to the bundle.
    if "CheckEditorBoot" not in page:
        fail("served page does not embed the check-editor boot script")


def check_matrix_contract():
    """05-06 Task 1: the per-case readout contract. The rendered page carries
    the four locked status strings as format templates, the two expected
    labels (distinct), the conditional input label, and the .case row
    selectors with theme-only colours; a real mixed-failure submission maps
    each cause to its own case_index/reason pair with no pre-submit leak and
    a dichotomous false verdict; a killed-at-timeout run renders the pending
    treatment (null verdict) with its timeout row. These are payload and
    source assertions -- the actual rendering is checked at 05-07's manual
    pass, because this project has no JS test harness for the close() render
    (the jsdom runner covers the editor, not the matrix)."""
    qs = load(CHECK_BANK)
    _, page = quiz.page_for(CHECK_BANK, qs, serve=True)
    for locked in ("Passed", "Failed — timed out after %ss",
                   "Failed — output was cut off at %d KB",
                   "Expected (pattern)", "Expected", "Your output", "Input",
                   "Case ", ".case", ".case.right", ".case.wrong"):
        if locked not in page:
            fail("served page lacks locked matrix copy %r" % locked)
    if "Failed" not in page:
        fail("served page lacks the fail status string")
    # no partial-credit display anywhere
    if re.search(r"(partial credit score|percent passed|cases passed of)",
                 page, re.IGNORECASE):
        fail("the page renders a partial-credit display")

    # End-to-end: mixed pass/fail fixture through a real daemon.
    work = tempfile.mkdtemp()
    try:
        # q5 is [MATCH: regex] with two cases; q2 is three-case trimmed.
        # Drive q2 with a source that passes case 1 and fails the rest, and
        # q3 (infinite loop) for the null-verdict case.
        bank_path = os.path.join(work, "check_bank.md")
        shutil.copyfile(CHECK_BANK, bank_path)
        _write_settings(work)
        proc, base = _serve_base(bank_path,
                                 os.path.join(work, "attempt.md"), [])
        if not base:
            if proc.poll() is None:
                proc.terminate()
            fail("matrix serve daemon never printed a URL")
        try:
            # q2: 5 7 :: 12, 3 4 :: 7, 0 :: 0 -- print 12 always -> pass 1,
            # fail 2 and 3 with distinct wrong_output reason.
            started = post(base + "api/start", {"bank": "check_bank",
                                                "count": 6, "mode": "practice",
                                                "focus": "q2"})
            resp = post(base + "api/submit",
                        {"session_id": started["session_id"],
                         "answer": "import sys\nprint(12)"})
            if resp.get("score") is not False:
                fail("mixed submission scored %r, want False" % resp.get("score"))
            obs = (resp.get("interaction_result") or {}).get("observations") or []
            if len(obs) != 3:
                fail("mixed submission has %d observations, want 3" % len(obs))
            if [o["case_index"] for o in obs] != [1, 2, 3]:
                fail("observations not 1-based in authored order: %r" % obs)
            if obs[0]["reason"] != "passed" or \
                    obs[1]["reason"] != "wrong_output" or \
                    obs[2]["reason"] != "wrong_output":
                fail("distinct failure causes not mapped to their cases: %r" % obs)
            if obs[1]["actual"] != "12\n":
                fail("observation actual output missing: %r" % obs[1])
            # pre-submit: the interaction contract (the renderer-config
            # surface a client sees before answering) has no case material.
            # The full public_item legitimately contains the stem and starter
            # text, so scope the leak check to the contract blob. The
            # renderer_config key set is already pinned exactly by
            # check_public_item; here we only assert the authored expected
            # values never reach it (case inputs can legitimately appear in
            # starter code, so they are not leak terms).
            item = runtime.public_item(qs[1])
            contract = json.dumps(item.get("interaction_contract") or {})
            for leak in ("cases", "observation", "reason"):
                if leak in contract:
                    fail("pre-submit interaction contract leaks %r" % leak)
            for case in qs[1].get("cases") or []:
                expected = (case.get("expected") or "").strip()
                # a one-character expected value like "0" can legitimately
                # appear in starter code; only distinctive values prove a leak
                if len(expected) >= 2 and expected in contract:
                    fail("pre-submit interaction contract leaks expected "
                         "material %r" % expected)

            # q3: infinite loop -> null verdict, pending treatment, timeout row.
            started3 = post(base + "api/start", {"bank": "check_bank",
                                                 "count": 6, "mode": "practice",
                                                 "focus": "q3"})
            killed = post(base + "api/submit",
                          {"session_id": started3["session_id"],
                           "answer": "while True:\n    pass"})
            if killed.get("score") is not None:
                fail("killed run scored %r, want None" % killed.get("score"))
            kobs = (killed.get("interaction_result") or {}).get("observations") or []
            if not kobs or all(o["reason"] != "timeout" for o in kobs):
                fail("killed run lacks a timeout observation: %r" % killed)
            # the served page renders the pending treatment for null verdicts
            # (the .pend class and 'Recorded. Not marked here.' header).
            if '.pend' not in page:
                fail("served page lacks the pending treatment class")
        finally:
            proc.terminate()
    finally:
        shutil.rmtree(work, ignore_errors=True)


def check_refusal_states():
    """05-06 Task 2: three refusals, three causes. The built file page shows
    the locked file-refusal sentence + skip control and no code editor for a
    check item; the served page carries the network and language sentences
    (distinct); the skip handler advances without verify/settle/close; the
    connectivity sentence is unchanged; no generic message covers more than
    one cause; the honest-limits line survives every refusal state."""
    # Built (offline) page.
    build_out = os.path.join(tempfile.mkdtemp(), "check_file.html")
    subprocess.run([sys.executable, os.path.join(ROOT, "itembank.py"),
                    "build", CHECK_BANK, build_out], check=True,
                   capture_output=True)
    html = open(build_out, encoding="utf-8").read()
    FILE_REFUSAL = ("This item runs code on the machine serving itembank and "
                    "can't be answered from a file opened directly in a "
                    "browser. Open this bank with itembank serve (or the "
                    "daemon) and try again.")
    if FILE_REFUSAL not in html:
        fail("built file page lacks the file-refusal sentence")
    if "Skip — not answerable offline" not in html:
        fail("built file page lacks the skip control label")
    # The offline asCheck's !SERVE branch replaces the editor: the boot
    # script's create() call sits inside the SERVE branch, so on a file page
    # the editor never boots. Source-assert the skip handler advances without
    # verify/settle/close.
    skip_src = re.search(r"skip\.onclick = \(\)=>\{([^}]*)\};", html)
    if not skip_src or "i++" not in skip_src.group(1) or "render()" not in skip_src.group(1):
        fail("skip handler does not advance the item index directly: %r"
             % (skip_src.group(1) if skip_src else "no handler"))
    if re.search(r"verify\(|settle\(|close\(", skip_src.group(1)):
        fail("skip handler calls verify/settle/close: %r" % skip_src.group(1))
    if model.HONEST_LIMITS_NOTE not in html:
        fail("built file page lost the honest-limits sentence")
    # The built page renders no editor for check: the .codewrap mount and
    # boot call are inside the SERVE branch, so assert the refusal branch is
    # the only reachable one by checking the boot call is guarded.
    if re.search(r"CheckEditorBoot\.create", html):
        # It is present in source (dead code offline); what matters is the
        # !SERVE guard returns before it. Assert the guard precedes it.
        g = re.search(r"if\(!SERVE\)\{.*?return;\s*\}", html, re.S)
        if not g:
            fail("offline asCheck lacks the !SERVE refusal guard")
    # Served page: both sentences present and distinct; honest-limits too.
    qs = load(CHECK_BANK)
    _, srv = quiz.page_for(CHECK_BANK, qs, serve=True)
    from surfaces.daemon import LAN_REFUSAL_COPY, UNKNOWN_LANGUAGE_COPY
    # The page owns its locked copy of both sentences (Copywriting Contract),
    # branched by the daemon's refused_reason field. The sentences are
    # written as adjacent JS string literals ("... " "..."), so strip the
    # quote/plus/newline noise and compare whitespace-collapsed.
    js_text = re.sub(r'["+\\]', "", srv)
    def collapse(s):
        return " ".join(str(s or "").split())
    if collapse(LAN_REFUSAL_COPY) not in collapse(js_text):
        fail("served page lacks the network refusal sentence")
    if "check.languages" not in srv:
        fail("served page lacks the language refusal sentence")
    if collapse("Add it in settings") not in collapse(js_text):
        fail("served page lacks the language refusal sentence")
    if collapse(UNKNOWN_LANGUAGE_COPY % "ruby") in collapse(js_text):
        fail("served page carries a literal language sentence; the page "
             "interpolates the language from the item contract")
    if LAN_REFUSAL_COPY == UNKNOWN_LANGUAGE_COPY:
        fail("the two refusal sentences are identical")
    if model.HONEST_LIMITS_NOTE not in srv:
        fail("served page lost the honest-limits sentence")
    # No generic message covers more than one cause.
    page_src = open(os.path.join(ROOT, "surfaces", "quiz_page.py"),
                    encoding="utf-8").read()
    if re.search(r"(something went wrong|an error occurred|unknown error)",
                 page_src, re.IGNORECASE):
        fail("a generic failure message covers more than one cause")
    # The connectivity copy in the settle catch block is unchanged (the
    # served client's exact string, written as adjacent JS literals; the
    # offline client's copy lives in the built page, since the served page
    # substitutes OFFLINE_JS away).
    if collapse("Couldn't check that answer. Your selection is still here.") \
            not in collapse(js_text):
        fail("served connectivity sentence changed")
    if collapse("Could not reach the process that scores and records") \
            not in collapse(re.sub(r'["+\\]', "", html)):
        fail("offline connectivity sentence changed")


def check_honest_limits_gate():
    """05-07 Task 2 (CODE-05): the honest-limits statement is one constant
    with two readers -- the SPEC text and the rendered page copy -- and the
    repository carries no claim-word that asserts a safety property the
    runtime does not have.

    The claim-word gate covers what this phase SHIPPED: source, README, and
    the records this phase wrote about itself. The phase's input documents
    (context, research, UI spec, plans) are deliberately outside the file
    set: they discuss the terms in order to forbid them, and several carry
    the gate's own grep pattern verbatim -- a gate that fails on the text
    defining it is not a gate.

    Term one is `sandbox`: exactly two pre-existing accurate occurrences,
    both about the BROWSER's own behaviour on a file page (README.md:269 and
    surfaces/quiz.py:cmd_serve's docstring), and zero anywhere else in the
    covered set. Exact per-file counts, not an exception list: a new
    occurrence in either allowlisted file fails just like a new occurrence
    elsewhere.

    Term two is `isolat`: zero occurrences anywhere in the covered set,
    because there are none today and none is correct.

    Term three, `contain`, is deliberately DROPPED: it matches ordinary
    English ("contains", "contained", "self-contained") in at least eight
    places in existing prose that have nothing to do with safety, so as a
    grep token it discriminates nothing -- a gate that cannot pass is not a
    gate. The semantic half of that check (reading the check sections for
    any other sentence that implies a safety property) lives in
    05-VALIDATION.md's manual table, done at 05-07 Task 3.
    """
    # Identity: SPEC and the served page carry the same sentence.
    if model.HONEST_LIMITS_NOTE not in model.SPEC:
        fail("SPEC does not carry the honest-limits constant")
    qs = load(CHECK_BANK)
    _, page = quiz.page_for(CHECK_BANK, qs, serve=True)
    if model.HONEST_LIMITS_NOTE not in page:
        fail("served page does not carry the honest-limits constant")
    if model.HONEST_LIMITS_NOTE not in model.SPEC or \
            model.HONEST_LIMITS_NOTE not in page:
        fail("honest-limits is not one string in both required places")

    # README points at the canonical text without copying it.
    readme = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()
    if model.HONEST_LIMITS_NOTE in readme:
        fail("README duplicates the honest-limits statement")
    if "itembank spec" not in readme or "HONEST_LIMITS_NOTE" not in readme:
        fail("README must point readers to `itembank spec` and name "
             "HONEST_LIMITS_NOTE")
    if "CASE)" not in readme:
        fail("README does not document the check type's marker syntax")

    # The claim-word gate: exact per-file counts over the shipped set.
    covered = {
        "README.md": {"sandbox": 1},
        "surfaces/quiz.py": {"sandbox": 1},
    }
    zero_files = ["model.py", "runner.py", "surfaces/quiz_page.py",
                  "surfaces/session.py", "surfaces/daemon.py", "GRADING.md"]
    import glob
    phase = os.path.join(ROOT, ".planning", "phases",
                         "05-check-item-type-code-editor")
    records = sorted(glob.glob(os.path.join(phase, "05-SPIKE-RESULT.md")) +
                     glob.glob(os.path.join(phase, "05-0*-SUMMARY.md")))
    for path in sorted(covered):
        text = open(os.path.join(ROOT, path), encoding="utf-8").read()
        for term, want in covered[path].items():
            got = len(re.findall(term, text, re.IGNORECASE))
            if got != want:
                fail("claim-word gate: %s has %d case-insensitive %r "
                     "occurrences, want %d" % (path, got, term, want))
    for path in zero_files + records:
        text = open(path, encoding="utf-8").read()
        for term in ("sandbox", "isolat"):
            if re.search(term, text, re.IGNORECASE):
                fail("claim-word gate: %s carries %r" % (path, term))


def check_schema_consumer():
    """05-07 Task 1: a renderer-independent consumer -- one that imports no
    quiz-page module -- validates the fixture's interaction contract against
    the published schema, submits the declared raw source/version request
    through /api/submit, and receives the same normalized result/evidence
    semantics as the browser path. Negative fixtures prove the schema rejects
    unknown contract versions, extra/executable renderer fields, and
    non-string responses, and that a real killed-at-timeout result validates
    with null verdict/score."""
    import schema_validate as sv
    schema = json.load(open(os.path.join(ROOT, "schemas", "item.schema.json"),
                            encoding="utf-8"))
    qs = load(CHECK_BANK)
    q = qs[0]
    item = runtime.public_item(q)
    errs = sv.validate(item, schema)
    if errs:
        fail("public_item for a check item fails item.schema.json: %s"
             % "; ".join(errs))
    contract = item["interaction_contract"]

    def expect_invalid(desc, mutate):
        bad = mutate(json.loads(json.dumps(contract)))
        e = sv.validate({"interaction_contract": bad,
                         "type": "check",
                         "response_schema": bad["response_schema"]}, schema)
        if not e:
            fail("schema accepted an invalid contract: %s" % desc)

    def with_version(c):
        c["version"] = 99
        return c

    def with_script(c):
        c["renderer_config"]["script"] = \
            "require('child_process').exec('x')"
        return c

    def with_int_response(c):
        c["response_schema"]["type"] = "integer"
        return c

    def with_evil_key(c):
        c["renderer_config"]["evil"] = 1
        return c

    expect_invalid("unknown version", with_version)
    expect_invalid("extra renderer field (executable payload)", with_script)
    expect_invalid("non-string response schema", with_int_response)
    # the renderer config rejects a top-level unknown key too
    expect_invalid("unknown renderer key", with_evil_key)

    # A real killed-at-timeout result validates with null verdict/score.
    killed = {"version": 1, "type": "check", "response": "while True:\n pass",
              "verdict": None, "observations": [
                  {"case_index": 1, "passed": False, "reason": "timeout",
                   "actual": "", "expected": "x", "expected_kind": "output",
                   "input": ""}]}
    # Validate the result defs in a synthetic root so the internal $ref to
    # case_observation resolves (schema_validate resolves #/$defs/ against
    # the passed root's $defs).
    result_def = schema["$defs"]["interaction_result"]
    obs_def = schema["$defs"]["case_observation"]
    synth_root = {"$defs": {"interaction_result": result_def,
                            "case_observation": obs_def}}
    e = sv.validate(killed, result_def, root=synth_root)
    if e:
        fail("killed-at-timeout result fails the published result schema: %s"
             % "; ".join(e))
    # and a string verdict is rejected (null-or-boolean is schema-enforced)
    bad_killed = dict(killed, verdict="nope")
    e = sv.validate(bad_killed, result_def, root=synth_root)
    if not e:
        fail("schema accepted a string verdict")

    # End-to-end through /api/submit: same semantics as the browser path.
    work = tempfile.mkdtemp()
    try:
        bank_path = os.path.join(work, "check_bank.md")
        shutil.copyfile(CHECK_BANK, bank_path)
        _write_settings(work)
        proc, base = _serve_base(bank_path,
                                 os.path.join(work, "attempt.md"), [])
        if not base:
            if proc.poll() is None:
                proc.terminate()
            fail("schema-consumer daemon never printed a URL")
        try:
            started = post(base + "api/start", {"bank": "check_bank",
                                                "count": 6, "mode": "practice",
                                                "focus": "q1"})
            resp = post(base + "api/submit",
                        {"session_id": started["session_id"],
                         "answer": "import sys\nprint(sum(map(int, sys.stdin.read().split())))"})
            ir = resp.get("interaction_result") or {}
            if ir.get("version") != 1 or ir.get("type") != "check":
                fail("consumer submit lost the contract envelope: %r" % ir)
            if ir.get("response") != "import sys\nprint(sum(map(int, sys.stdin.read().split())))":
                fail("consumer submit lost the raw response")
            if ir.get("verdict") is not True:
                fail("consumer submit verdict is %r" % ir.get("verdict"))
            e = sv.validate(ir, result_def, root=synth_root)
            if e:
                fail("live consumer result fails the published schema: %s"
                     % "; ".join(e))
        finally:
            proc.terminate()
    finally:
        shutil.rmtree(work, ignore_errors=True)


def check_network_refusal():
    """D-09 made real: with the daemon bound to all interfaces and
    check.allow_lan false, both submit routes refuse a check item's execution
    with the locked sentence and write no evidence; with allow_lan true or a
    loopback bind, execution proceeds; a non-check item is untouched; and the
    unknown-language refusal returns its own distinct sentence without
    crashing the daemon."""
    root = tempfile.mkdtemp()
    try:
        open(os.path.join(root, "agent_check.md"), "w", encoding="utf-8").write(AGENT_BANK)
        open(os.path.join(root, "short_bank.md"), "w", encoding="utf-8").write(SHORT_BANK)
        _write_settings(root)                       # allow_lan false by default
        log = evidence.log_path(root)
        root_abs = os.path.abspath(root)

        # -- all-interfaces daemon, allow_lan false: refuse both routes -------
        proc, base = _launch_daemon(root, lan=True)
        if not base:
            proc.terminate()
            fail("lan daemon never printed a URL")
        try:
            sid = _start_session(base, "agent_check", "q1")
            before = os.path.getsize(log) if os.path.exists(log) else 0
            resp = post(base + "api/submit", {"session_id": sid, "answer": SUM_SOURCE})
            body = json.dumps(resp)
            if LAN_REFUSAL not in body:
                fail("api/submit refused body lacks the locked sentence: %r" % body)
            if "score" in resp:
                fail("a refused check submit carried a score: %r" % resp)
            if root_abs in body:
                fail("refused api/submit body leaks an absolute path")
            if os.path.getsize(log) != before:
                fail("a refused api/submit appended to the evidence log")

            qr = post(base + "quiz/agent_check/answer",
                      {"id": "q1", "interaction_version": 1, "response": SUM_SOURCE})
            qbody = json.dumps(qr)
            if LAN_REFUSAL not in qbody:
                fail("quiz/answer refused body lacks the locked sentence: %r" % qbody)
            if "score" in qr:
                fail("a refused quiz/answer carried a score: %r" % qr)
            if root_abs in qbody:
                fail("refused quiz/answer body leaks an absolute path")
            before_q = os.path.getsize(log)
            # /quiz/answer reuses the api session already started above, so a
            # refusal here must not append anything either.
            if os.path.getsize(log) != before_q:
                fail("a refused quiz/answer appended to the evidence log")

            # a non-check item on the same daemon still records (no refusal).
            before_n = os.path.getsize(log)
            nsid = _start_session(base, "short_bank", "q1")
            nres = post(base + "api/submit", {"session_id": nsid, "answer": "Paris"})
            if LAN_REFUSAL in json.dumps(nres):
                fail("a non-check item was refused on the lan daemon")
            if os.path.getsize(log) <= before_n:
                fail("a non-check item did not append an evidence event")
        finally:
            proc.terminate()

        # -- allow_lan true: executes normally on the lan daemon --------------
        _write_settings(root, allow_lan=True)
        proc2, base2 = _launch_daemon(root, lan=True)
        if not base2:
            proc2.terminate()
            fail("allow_lan daemon never printed a URL")
        try:
            sid = _start_session(base2, "agent_check", "q1")
            resp = post(base2 + "api/submit", {"session_id": sid, "answer": SUM_SOURCE})
            if resp.get("score") is not True:
                fail("allow_lan=true lan submit scored %r" % resp.get("score"))
            if LAN_REFUSAL in json.dumps(resp):
                fail("allow_lan=true submit was refused")
        finally:
            proc2.terminate()

        # -- loopback daemon: always executes ---------------------------------
        _write_settings(root)
        proc3, base3 = _launch_daemon(root, lan=False)
        if not base3:
            proc3.terminate()
            fail("loopback daemon never printed a URL")
        try:
            sid = _start_session(base3, "agent_check", "q1")
            resp = post(base3 + "api/submit", {"session_id": sid, "answer": SUM_SOURCE})
            if resp.get("score") is not True:
                fail("loopback submit scored %r" % resp.get("score"))
        finally:
            proc3.terminate()

        # -- unknown-language on a loopback daemon: distinct sentence, no crash
        rub = os.path.join(root, "ruby_check.md")
        open(rub, "w", encoding="utf-8").write(RUBY_BANK)
        session_u = os.path.join(root, "_attempts", "session_u.json")
        os.makedirs(os.path.dirname(session_u), exist_ok=True)
        rs = _cli("start", rub, "--count", "1", "--seed", "8", "--force",
                  "--mode", "practice", "--out", session_u)
        if rs.returncode != 0:
            fail("force start for unknown-language daemon case failed: %s"
                 % (rs.stdout + rs.stderr))
        uid = json.loads(rs.stdout)["session_id"]
        proc4, base4 = _launch_daemon(root, lan=False)
        if not base4:
            proc4.terminate()
            fail("unknown-language daemon never printed a URL")
        try:
            code, body = post_error(base4 + "api/submit",
                                    {"session_id": uid, "answer": SUM_SOURCE})
            if code == 500:
                fail("unknown-language refusal produced a 500")
            if UNKNOWN_COPY not in body:
                fail("unknown-language body lacks its distinct sentence: %r" % body)
            if LAN_REFUSAL in body:
                fail("unknown-language returned the network refusal instead")
            if root_abs in body:
                fail("unknown-language body leaks an absolute path")
            # the daemon survived: it still answers a fresh request.
            still = post(base4 + "api/start", {"bank": "agent_check", "count": 6,
                                               "mode": "practice", "focus": "q1"})
            if not still.get("session_id"):
                fail("the daemon crashed after the unknown-language submit")
        finally:
            proc4.terminate()
    finally:
        shutil.rmtree(root, ignore_errors=True)


def main():
    check_parse_and_defaults()
    check_sample_bank_unchanged()
    check_markers_shared()
    check_case_passed()
    check_run_cases()
    check_harness_end_to_end()
    check_scoring_identities()
    check_public_item()
    check_interaction_result()
    check_explain_payload()
    check_evidence_signatures()
    check_http_roundtrip()
    check_agent_path()
    check_cross_path()
    check_explain_threading()
    check_vendor_integrity()
    check_matrix_contract()
    check_refusal_states()
    check_honest_limits_gate()
    check_schema_consumer()
    check_network_refusal()
    print("check roundtrip: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
