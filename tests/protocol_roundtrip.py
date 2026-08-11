#!/usr/bin/env python3
"""The protocol contract harness: lint codes, schema versions, and the five
published schema documents under schemas/.

Standard library only, runnable as `python tests/protocol_roundtrip.py`.
"""
import json, os, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import itembank                                            # noqa: E402
import schema_validate                                     # noqa: E402

BROKEN_BANK = os.path.join(ROOT, "fixtures", "broken_bank.md")
SAMPLE_BANK = os.path.join(ROOT, "fixtures", "sample_bank.md")
SCHEMAS_DIR = os.path.join(ROOT, "schemas")

# The namespace prefixes the protocol contract accepts. Plan 03-03 Task 3
# reads this set from this module (tests/lesson_roundtrip.py imports it)
# rather than restating the literal, so the two files cannot drift -- a second
# copy of the prefix list is the same class of drift this set exists to
# prevent.
LINT_PREFIXES = ("item", "bank", "lesson", "terms", "key", "style", "prov")


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
        if prefix not in LINT_PREFIXES:
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
    # Phase 6 moved the closed response shape into $defs.response_event so
    # the top-level document can also describe the hint event via oneOf; the
    # response event's required key set lives there now.
    required_keys = set(response_doc["$defs"]["response_event"]["required"])

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
        seen = set()
        while data["status"] == "active":
            nxt = json.loads(run(["next", session_file], tmp))
            if nxt["status"] != "active":
                break
            item = nxt["item"]
            q = qs[item["id"]]
            # Phase 6: a `short` response stays pending for a human marker
            # and never advances the cursor, so submit it once and stop.
            if q["type"] == "short":
                short_checked = True
            if q["id"] in seen:
                break
            seen.add(q["id"])
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


# ---- validator + delivery (01-06): every real payload checked against ------
# schemas/*.json, and itembank schema --all is self-contained and stable.

def test_runtime_matches_schemas():
    """The local mirror of the CI step 'Runtime output matches published
    schema': drives one real session end to end and checks every payload
    against its document with itembank.validate directly, so a developer
    sees this fail before pushing rather than first in CI.

    `itembank report`'s top-level payload wraps runtime.session_summary()
    under a `summary` key (session_id/status live beside it); the published
    session_summary shape describes that inner object, matching what
    01-05's own test_schema_versions_present already asserts against
    `report["summary"]["schema_version"]`. So the session-summary half of
    report.schema.json's oneOf is checked against `report["summary"]`, not
    the wrapper -- the wrapper itself is not one of the two published shapes.
    """
    tmp = tempfile.mkdtemp()
    try:
        bank = os.path.join(tmp, "bank.md")
        shutil.copyfile(SAMPLE_BANK, bank)

        started = json.loads(run(["start", bank, "--count", "3", "--seed", "1"], tmp))
        session_file = started["session_file"]
        session_data = json.load(open(session_file, encoding="utf-8"))

        errs = itembank.validate(session_data, load_schema("session.schema.json"))
        if errs:
            fail("session.schema.json: %s" % errs[0])

        errs = itembank.validate(started["item"], load_schema("item.schema.json"))
        if errs:
            fail("item.schema.json: %s" % errs[0])

        run(["submit", session_file, "--answer", "A", "--confidence", "high"], tmp)
        log = os.path.join(tmp, "_evidence", "evidence.jsonl")
        lines = [l for l in open(log, encoding="utf-8").read().splitlines() if l.strip()]
        response_schema = load_schema("response.schema.json")
        for line in lines:
            errs = itembank.validate(json.loads(line), response_schema)
            if errs:
                fail("response.schema.json: %s" % errs[0])

        report = json.loads(run(["report", session_file], tmp))
        report_schema = load_schema("report.schema.json")
        errs = itembank.validate(report["summary"], report_schema)
        if errs:
            fail("report.schema.json (session summary): %s" % errs[0])

        # C7 (03.1-03): public_item no longer carries the syllabus
        # objective, so the evidence query reads it from the question dict.
        objective = next(x for x in itembank.load(bank)
                         if x["id"] == started["item"]["id"])["objective"]
        history = json.loads(
            run(["evidence", "--objective", objective, "--base", tmp], tmp))
        errs = itembank.validate(history, report_schema)
        if errs:
            fail("report.schema.json (objective history): %s" % errs[0])

        lint_schema = load_schema("lint_error.schema.json")
        broken = run_lint_json(BROKEN_BANK)
        payload = json.loads(broken.stdout)
        for entry in payload["errors"] + payload["warnings"]:
            errs = itembank.validate(entry, lint_schema)
            if errs:
                fail("lint_error.schema.json: %s" % errs[0])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_schema_command_output():
    """PROTO-05's automated half. Confirms `itembank schema --all` parses,
    is self-contained in the senses a test can check mechanically, and is
    byte-stable across runs. Whether the output is *sufficient* for a model
    with no repository access is a sufficiency judgment -- the Task 3
    `<human-check>` in 01-06-PLAN.md's job, not this test's.
    """
    cmd = [sys.executable, os.path.join(ROOT, "itembank.py"), "schema", "--all"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        fail("itembank schema --all exited %d: %s" % (r.returncode, r.stderr))
    payload = json.loads(r.stdout)

    if payload.get("spec") != itembank.SPEC:
        fail("--all's spec does not equal model.SPEC verbatim")

    names = sorted(payload.get("contracts", {}))
    if names != ["item", "lint_error", "report", "response", "selection",
                 "session"]:
        fail("--all's contracts dict does not carry all six names in sorted "
             "order: %r" % names)

    for name, doc in payload["contracts"].items():
        try:
            schema_validate.check_schema(doc)
        except schema_validate.SchemaError as exc:
            fail("contracts[%r] does not check out as a schema: %s" % (name, exc))

    commands = payload.get("commands", [])
    subcommands = set(c["command"].split()[1] for c in commands)
    for expected in ("start", "next", "submit", "report", "evidence"):
        if expected not in subcommands:
            fail("--all's commands list does not name %r" % expected)

    for c in commands:
        contract = c.get("contract")
        if contract is not None and contract not in payload["contracts"]:
            fail("commands entry %r names contract %r, absent from contracts" %
                 (c["command"], contract))

    second = subprocess.run(cmd, capture_output=True, text=True)
    if second.stdout != r.stdout:
        fail("two runs of itembank schema --all produced different bytes")


def test_educational_objective_private_until_verdict():
    """C7/LESSON-15: the optional one-sentence Educational Objective line and
    the syllabus [OBJECTIVE:] field appear only in explain_payload(), never
    in public_item() or any pre-answer surface; a multi-sentence objective
    warns (03.1-UI-SPEC §9.5)."""
    tmp = tempfile.mkdtemp()
    bank = os.path.join(tmp, "obj_bank.md")
    open(bank, "w", encoding="utf-8").write(
        "Q1. Which device opens the airway?   (difficulty: recall)\n"
        "[OBJECTIVE: emt:airway]\n"
        "Objective: Distinguish the OPA from the NPA indications.\n"
        "A) OPA\nB) NPA\nC) King\nD) Combitube\n\n"
        "CORRECT: A\n\n"
        "WHY BEST: The OPA holds the tongue off the pharynx.\n\n"
        "KEY DISCRIMINATOR: Indication vs contraindication.\n\n"
        "SECOND-BEST: B. The NPA is softer; this would be correct if the "
        "question asked for the nasal route.\n\n"
        "DISTRACTOR ANALYSIS:\n"
        "- A) Correct: the oral airway.\n"
        "- B) The nasal airway; this would be correct if the question asked "
        "for a nasal adjunct.\n"
        "- C) A supraglottic device; this would be correct if the question "
        "asked for a rescue airway.\n"
        "- D) A supraglottic device; this would be correct if the question "
        "asked for a rescue airway.\n\n"
        "TRAP: Confusing OPA and NPA indications.\n\n"
        "CONFIDENCE: high\n")
    q = itembank.load(bank)[0]
    pub = itembank.public_item(q)
    for key in ("objective", "educational_objective"):
        if key in pub:
            fail("public_item must not expose %r pre-answer" % key)
    ex = itembank.explain_payload(q)
    if ex.get("educational_objective") != \
            "Distinguish the OPA from the NPA indications.":
        fail("explain_payload must carry the educational_objective line: %r"
             % ex)
    if ex.get("objective") != "emt:airway":
        fail("the syllabus [OBJECTIVE:] must move into explain_payload: %r"
             % ex)

    from surfaces.quiz import page_for
    # The served (pre-answer) page embeds public_item payloads only; the
    # static offline build legitimately carries explanations, so C7 is
    # asserted against the served surface.
    _, page = page_for(bank, itembank.load(bank), serve=True)
    if "Distinguish the OPA from the NPA indications." in page:
        fail("pre-answer quiz HTML leaks the objective line")
    if "emt:airway" in page:
        fail("pre-answer quiz HTML leaks the syllabus objective")

    bank2 = os.path.join(tmp, "obj_bank2.md")
    open(bank2, "w", encoding="utf-8").write(
        "Q1. Which device opens the airway?   (difficulty: recall)\n"
        "Objective: First sentence. Second sentence.\n"
        "A) OPA\nB) NPA\nC) King\nD) Combitube\n\n"
        "CORRECT: A\n\n"
        "WHY BEST: The OPA holds the tongue off the pharynx.\n\n"
        "KEY DISCRIMINATOR: Indication vs contraindication.\n\n"
        "SECOND-BEST: B. The NPA is softer; this would be correct if the "
        "question asked for the nasal route.\n\n"
        "DISTRACTOR ANALYSIS:\n"
        "- A) Correct: the oral airway.\n"
        "- B) The nasal airway; this would be correct if the question asked "
        "for a nasal adjunct.\n"
        "- C) A supraglottic device; this would be correct if the question "
        "asked for a rescue airway.\n"
        "- D) A supraglottic device; this would be correct if the question "
        "asked for a rescue airway.\n\n"
        "TRAP: Confusing OPA and NPA indications.\n\n"
        "CONFIDENCE: high\n")
    _, warnings = itembank.lint(itembank.load(bank2))
    if not any(w.code == "item.objective_line_multi_sentence"
               for w in warnings):
        fail("a multi-sentence Objective: line must warn")


def main():
    test_lint_error_shape()
    test_lint_codes_declared()
    test_lint_json_clean()
    test_lint_json_encoding()
    test_schema_versions_present()
    test_schema_version_required()
    test_event_schema_fields()
    test_runtime_matches_schemas()
    test_schema_command_output()
    test_educational_objective_private_until_verdict()
    print("protocol contract: ok (%d lint codes declared, schema versions pinned, "
          "EVID-07 field set asserted, runtime output validated against schemas/, "
          "schema --all self-contained and stable)" % len(itembank.LINT_CODES))
    return 0


if __name__ == "__main__":
    sys.exit(main())
