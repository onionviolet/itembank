#!/usr/bin/env python3
"""The protocol contract harness: lint codes, schema versions, and the five
published schema documents under schemas/.

Standard library only, runnable as `python tests/protocol_roundtrip.py`.
"""
import json, os, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import itembank                                            # noqa: E402

BROKEN_BANK = os.path.join(ROOT, "fixtures", "broken_bank.md")
SAMPLE_BANK = os.path.join(ROOT, "fixtures", "sample_bank.md")
SCHEMAS_DIR = os.path.join(ROOT, "schemas")


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def run(args, cwd):
    """Drive the real CLI via subprocess, the same way a learner or agent
    does, so version-stamp and evidence-shape tests exercise the actual path
    rather than calling functions directly.
    """
    r = subprocess.run([sys.executable, os.path.join(ROOT, "itembank.py")] + list(args),
                       cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        fail("command %r failed (%d): %s" % (args, r.returncode, r.stderr))
    return r.stdout


def correct_answer(q):
    if q["type"] == "mc":
        return q["correct"][0]
    if q["type"] == "multi":
        return json.dumps(list(q["correct"]))
    if q["type"] in ("table", "dnd"):
        return json.dumps(dict((str(i), r["cat"]) for i, r in enumerate(q["rows"])))
    if q["type"] == "build":
        return json.dumps(list(q["steps"]))
    return "A concise constructed response."


def load_schema(name):
    return json.load(open(os.path.join(SCHEMAS_DIR, name), encoding="utf-8"))


def run_lint_json(bank_path):
    # PYTHONIOENCODING forces the child's stdout to UTF-8 regardless of the host
    # console code page (cp1252 on a default Windows console), which would otherwise
    # raise UnicodeEncodeError the moment a lint message carries non-ASCII content.
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    return subprocess.run(
        [sys.executable, os.path.join(ROOT, "itembank.py"), "lint", bank_path, "--json"],
        capture_output=True, text=True, encoding="utf-8", env=env)


def test_lint_error_shape():
    qs = itembank.load(BROKEN_BANK)
    errors, warnings = itembank.lint(qs)
    if not errors or not warnings:
        fail("broken_bank.md produced no errors or no warnings; it can no longer exercise "
             "this test")
    for entry in list(errors) + list(warnings):
        if not isinstance(entry, itembank.LintError):
            fail("lint entry is not a LintError: %r" % (entry,))
        if not entry.code or "." not in entry.code:
            fail("code %r is not a non-empty dotted string" % (entry.code,))
        if entry.code not in itembank.LINT_CODES:
            fail("code %r is not declared in LINT_CODES" % (entry.code,))
        if not entry.field:
            fail("field is empty on %r" % (entry,))
        if not entry.item:
            fail("item is empty on %r" % (entry,))
        if str(entry) != "%s: %s" % (entry.item, entry.message):
            fail("str() does not reproduce '%%s: %%s' for %r" % (entry,))


def test_lint_codes_declared():
    codes = itembank.LINT_CODES
    if list(codes) != sorted(codes):
        fail("LINT_CODES is not sorted")
    if len(set(codes)) != len(codes):
        fail("LINT_CODES has duplicates")
    for c in codes:
        prefix = c.split(".", 1)[0]
        if prefix not in ("item", "bank"):
            fail("code %r has an undeclared namespace prefix %r" % (c, prefix))


def test_lint_json_clean():
    clean = run_lint_json(SAMPLE_BANK)
    if clean.returncode != 0:
        fail("lint --json on the clean fixture exited %d: %s" % (clean.returncode, clean.stderr))
    payload = json.loads(clean.stdout)
    if payload["errors"] != []:
        fail("lint --json on the clean fixture reported errors: %r" % (payload["errors"],))

    broken = run_lint_json(BROKEN_BANK)
    if broken.returncode == 0:
        fail("lint --json on the broken fixture exited 0")
    payload = json.loads(broken.stdout)
    for e in payload["errors"]:
        if set(e.keys()) != {"code", "field", "item", "message"}:
            fail("error object has unexpected keys: %r" % (sorted(e.keys()),))


def test_lint_json_encoding():
    """A rubric point can be one word by str.split() and dozens of UTF-8 bytes, so the
    MODEL/RUBRIC length thresholds have to measure whitespace-separated tokens on the
    Unicode code-point string, never bytes. And --json has to round-trip non-ASCII
    content unescaped, or ensure_ascii regressed.

    Two items: Q1's deliberately-unknown table category is CJK text, and it is echoed
    verbatim into an error message, proving the round-trip; Q2's rubric point is 30 CJK
    characters, one whitespace-separated token, proving the threshold counts tokens
    on the code-point string rather than bytes.
    """
    tmpdir = tempfile.mkdtemp()
    bank_path = os.path.join(tmpdir, "encoding_bank.md")
    category_cjk = "在线"       # echoed verbatim into item.row_category_unknown
    rubric_cjk = "的" * 30      # 30 Chinese characters: one whitespace-separated word
    bank_text = (
        "Q1. 一个简单的问题。\n"
        "[TYPE: table]\n"
        "[CATEGORIES: Online | Offline]\n\n"
        "ROW) First thing :: %s\n"
        "ROW) Second thing :: Offline\n\n"
        "WHY BEST: Placeholder.\n\n"
        "DISTRACTOR ANALYSIS:\n"
        "- Placeholder bullet.\n\n"
        "TRAP: Placeholder.\n\n"
        "CONFIDENCE: high\n\n"
        "Q2. Explain why redundancy matters in a distributed system.\n"
        "[TYPE: short]\n\n"
        "MODEL: A short model answer.\n\n"
        "RUBRIC:\n"
        "- %s\n"
        "- Mentions a second, distinct checkable claim in English.\n\n"
        "TRAP: Reciting jargon instead of explaining the mechanism.\n\n"
        "CONFIDENCE: high\n"
    ) % (category_cjk, rubric_cjk)
    open(bank_path, "w", encoding="utf-8").write(bank_text)

    result = run_lint_json(bank_path)
    if category_cjk not in result.stdout:
        fail("lint --json escaped non-ASCII characters; ensure_ascii=False is not in effect "
             "(stdout: %r)" % (result.stdout[:400],))
    payload = json.loads(result.stdout)
    codes = [e["code"] for e in payload.get("errors", []) + payload.get("warnings", [])]
    if "item.row_category_unknown" not in codes:
        fail("the deliberately-unknown CJK table category did not raise "
             "item.row_category_unknown; the fixture no longer exercises this test")
    if "item.rubric_point_too_long" in codes:
        fail("a 30-character CJK rubric point (one whitespace-separated token) was flagged "
             "as too long; length must be measured in tokens on the code-point string, "
             "not bytes")


# ---- schema versions (01-05): every payload states which contract version --
# it was written against, and that version matches its published document.

def test_schema_versions_present():
    """PROTO-01. Goes red when a payload gains a version stamp in code but
    not in its document, or the reverse.
    """
    qs = itembank.load(SAMPLE_BANK)
    for q in qs:
        item = itembank.public_item(q)
        if item["schema_version"] != itembank.ITEM_VERSION:
            fail("public_item(%s)'s schema_version is %r, not ITEM_VERSION %r" %
                 (q["id"], item["schema_version"], itembank.ITEM_VERSION))

    tmp = tempfile.mkdtemp()
    try:
        bank = os.path.join(tmp, "sample_bank.md")
        shutil.copyfile(SAMPLE_BANK, bank)
        started = json.loads(run(["start", bank, "--count", "1", "--seed", "0"], tmp))
        session_file = started["session_file"]
        session_data = json.load(open(session_file, encoding="utf-8"))
        if session_data["schema_version"] != itembank.SESSION_VERSION:
            fail("session file schema_version is %r, not SESSION_VERSION %r" %
                 (session_data["schema_version"], itembank.SESSION_VERSION))

        item = started["item"]
        q = next(x for x in itembank.load(bank) if x["id"] == item["id"])
        run(["submit", session_file, "--answer", correct_answer(q)], tmp)

        report = json.loads(run(["report", session_file], tmp))
        if report["schema_version"] != itembank.REPORT_VERSION:
            fail("itembank report's top-level schema_version is %r, not REPORT_VERSION %r" %
                 (report["schema_version"], itembank.REPORT_VERSION))
        if report["summary"]["schema_version"] != itembank.REPORT_VERSION:
            fail("itembank report's summary.schema_version is %r, not REPORT_VERSION %r" %
                 (report["summary"]["schema_version"], itembank.REPORT_VERSION))

        summary = itembank.session_summary(json.load(open(session_file, encoding="utf-8")))
        if summary["schema_version"] != itembank.REPORT_VERSION:
            fail("runtime.session_summary()'s schema_version is %r, not REPORT_VERSION %r" %
                 (summary["schema_version"], itembank.REPORT_VERSION))

        log = os.path.join(tmp, "_evidence", "evidence.jsonl")
        lines = [l for l in open(log, encoding="utf-8").read().splitlines() if l.strip()]
        raw = json.loads(lines[-1])
        if raw["schema_version"] != itembank.EVENT_SCHEMA_VERSION:
            fail("response event schema_version is %r, not EVENT_SCHEMA_VERSION %r" %
                 (raw["schema_version"], itembank.EVENT_SCHEMA_VERSION))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # itembank lint --json's own envelope hardcodes schema_version: 1
    # (surfaces/cli.py:cmd_lint); it has no exported version constant of its
    # own, so lint_error.schema.json is tied to that literal instead.
    version_constants = {
        "item.schema.json": itembank.ITEM_VERSION,
        "session.schema.json": itembank.SESSION_VERSION,
        "response.schema.json": itembank.EVENT_SCHEMA_VERSION,
        "report.schema.json": itembank.REPORT_VERSION,
        "lint_error.schema.json": 1,
    }
    for name, constant in version_constants.items():
        doc = load_schema(name)
        if doc["x-itembank-version"] != constant:
            fail("%s's x-itembank-version is %r, does not match the constant it "
                 "describes (%r)" % (name, doc["x-itembank-version"], constant))


def test_schema_version_required():
    """PROTO-01's empty edge: a payload with no schema_version is rejected
    with a named error rather than silently accepted, and every published
    document lists schema_version as required so the plan 01-06 validator
    rejects an unstamped instance too.
    """
    tmp = tempfile.mkdtemp()
    try:
        session_file = os.path.join(tmp, "unstamped.json")
        data = {"session_id": "x", "bank": SAMPLE_BANK, "items": [0], "cursor": 0,
                "responses": [], "status": "active", "mode": "diagnostic",
                "objective": "", "seed": 0}
        json.dump(data, open(session_file, "w", encoding="utf-8"))
        r = subprocess.run(
            [sys.executable, "-c",
             "import itembank; itembank.read_session(%r)" % session_file],
            capture_output=True, text=True)
        if r.returncode == 0:
            fail("read_session accepted a session with no schema_version")
        if "schema_version" not in (r.stderr + r.stdout):
            fail("the rejection message does not name schema_version: %r" %
                 (r.stderr + r.stdout,))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    for name in ("item.schema.json", "session.schema.json", "response.schema.json"):
        doc = load_schema(name)
        if "schema_version" not in doc.get("required", []):
            fail("%s does not require schema_version" % name)

    report_doc = load_schema("report.schema.json")
    for variant_name in ("session_summary", "objective_history"):
        variant = report_doc["$defs"][variant_name]
        if "schema_version" not in variant.get("required", []):
            fail("report.schema.json's %s variant does not require schema_version" %
                 variant_name)


# ---- EVID-07 field set (01-05): the code and the published contract -------
# cannot drift apart without a test going red.

def test_event_schema_fields():
    """EVID-07. Drives a real session to completion, one item of every type,
    and checks each recorded event's key set against response.schema.json's
    required array, plus the dispositions the schema documents.
    """
    response_doc = load_schema("response.schema.json")
    required_keys = set(response_doc["required"])

    tmp = tempfile.mkdtemp()
    try:
        bank = os.path.join(tmp, "sample_bank.md")
        shutil.copyfile(SAMPLE_BANK, bank)
        started = json.loads(
            run(["start", bank, "--count", "6", "--seed", "0", "--mode", "practice"], tmp))
        session_file = started["session_file"]
        qs = {q["id"]: q for q in itembank.load(bank)}
        log = os.path.join(tmp, "_evidence", "evidence.jsonl")

        auto_scored_checked = short_checked = False
        data = json.load(open(session_file, encoding="utf-8"))
        while data["status"] == "active":
            nxt = json.loads(run(["next", session_file], tmp))
            if nxt["status"] != "active":
                break
            item = nxt["item"]
            q = qs[item["id"]]
            answer = correct_answer(q)
            json.loads(run(
                ["submit", session_file, "--answer", answer, "--confidence", "medium"], tmp))

            lines = [l for l in open(log, encoding="utf-8").read().splitlines() if l.strip()]
            raw = json.loads(lines[-1])

            if set(raw.keys()) != required_keys:
                fail("raw event key set does not equal response.schema.json's required "
                     "array: extra=%r missing=%r" %
                     (sorted(set(raw.keys()) - required_keys),
                      sorted(required_keys - set(raw.keys()))))
            if not isinstance(raw["response_time_ms"], int) or raw["response_time_ms"] < 0:
                fail("response_time_ms is not a non-negative int: %r" %
                     raw["response_time_ms"])
            if raw["confidence"] != "medium":
                fail("confidence is %r, not medium" % raw["confidence"])
            if raw["mode"] != "practice":
                fail("mode is %r, not the session's own mode" % raw["mode"])
            if raw["error_category"] is not None:
                fail("error_category is %r, not exactly None" % raw["error_category"])
            if raw["hint_tier"] is not None:
                fail("hint_tier is %r, not exactly None" % raw["hint_tier"])

            if q["type"] == "short":
                if raw["review_state"] != "pending":
                    fail("short item's review_state is %r, not pending" %
                         raw["review_state"])
                if raw["score"] is not None:
                    fail("short item's score is %r, not None" % raw["score"])
                short_checked = True
            else:
                if raw["review_state"] != "n/a":
                    fail("auto-scored item's review_state is %r, not n/a" %
                         raw["review_state"])
                auto_scored_checked = True

            data = json.load(open(session_file, encoding="utf-8"))

        if not auto_scored_checked:
            fail("no auto-scored item was submitted; review_state 'n/a' was never exercised")
        if not short_checked:
            fail("no short item was submitted; review_state 'pending' was never exercised")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    test_lint_error_shape()
    test_lint_codes_declared()
    test_lint_json_clean()
    test_lint_json_encoding()
    test_schema_versions_present()
    test_schema_version_required()
    test_event_schema_fields()
    print("protocol contract: ok (%d lint codes declared, schema versions pinned, "
          "EVID-07 field set asserted)" % len(itembank.LINT_CODES))
    return 0


if __name__ == "__main__":
    sys.exit(main())
