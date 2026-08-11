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
CASE) 10 2 :: 8
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
    if [c["stdin"] for c in cases] != ["5 7", "10 2"]:
        fail("cases parsed out of order: %r" % cases)
    if [c["expected"] for c in cases] != ["12", "8"]:
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
    new_markers = ("CASE)", "[LANG:", "[MATCH:", "STARTER:", "[HARNESS:]",
                   "[TOLERANCE:]")
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
    if not all(r["passed"] for r in ok) or [r["actual"] for r in ok] != ["12\n", "8\n"]:
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
    if not echoed[0]["passed"] or echoed[0]["actual"] != "5 7":
        fail("stdin-echo source did not see the authored stdin: %r" % echoed[0])
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
    q = parse_check(SUM_ITEM)
    if runtime.canonical_response(q, [1, 1, 0]) != "1,1,0":
        fail("canonical_response of [1, 1, 0] is %r" %
             runtime.canonical_response(q, [1, 1, 0]))
    if runtime.canonical_key(q) != "1,1,1":
        fail("canonical_key of a two-case item is %r" % runtime.canonical_key(q))
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
    if res["observations"][1]["input"] != "10 2":
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
    print("check roundtrip: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
