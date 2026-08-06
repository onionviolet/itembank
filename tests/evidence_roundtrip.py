#!/usr/bin/env python3
"""End-to-end: one submitted response reaches the evidence log and comes back
out of it through a single command, and no second writer can silently appear.

Drives the real CLI via subprocess, the same way a learner or agent does,
rather than calling functions directly, so the test exercises the actual path
from `itembank submit` to `_evidence/evidence.jsonl` to `itembank evidence`.

Standard library only, runnable as `python tests/evidence_roundtrip.py`.
"""
import json, os, re, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import itembank                                            # noqa: E402

BANK = os.path.join(ROOT, "fixtures", "sample_bank.md")
BROKEN_BANK = os.path.join(ROOT, "fixtures", "broken_bank.md")

# The 22 keys named in 01-02-PLAN.md's must_haves. The event also carries a
# 23rd key, "bank", named in the plan's own field list and required by its
# threat model (T-1-06); this set is the floor, not the ceiling.
EXPECTED_KEYS = {
    "schema_version", "event_id", "event_type", "ts", "session_id", "item_id",
    "item_ref", "item_type", "objective", "subject", "mode", "attempt_number",
    "answer", "canonical", "score", "response_time_ms", "confidence",
    "error_category", "hint_tier", "review_state", "dedupe_key", "source_ref",
}


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def run(args, cwd):
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


def start_and_submit(cwd, bank, mode):
    started = json.loads(run(
        ["start", bank, "--count", "1", "--seed", "0", "--mode", mode], cwd))
    session_file = started["session_file"]
    item = started["item"]
    qs = itembank.load(bank)
    q = next(x for x in qs if x["id"] == item["id"])
    submitted = json.loads(run(
        ["submit", session_file, "--answer", correct_answer(q), "--confidence", "high"],
        cwd))
    return item["objective"], submitted, q


def test_tracer_end_to_end():
    tmp = tempfile.mkdtemp()
    try:
        bank = os.path.join(tmp, "sample_bank.md")
        shutil.copyfile(BANK, bank)
        objective, submitted, q = start_and_submit(tmp, bank, "drill")
        if submitted["score"] is not True:
            fail("correct answer for %s scored %r, not True" % (q["id"], submitted["score"]))

        out = run(["evidence", "--objective", objective, "--base", tmp], tmp)
        result = json.loads(out)
        if result["count"] != 1:
            fail("expected count 1 from evidence --objective, got %r" % result["count"])

        ev = result["events"][0]
        if ev["mode"] != "drill":
            fail("evidence query row mode is %r, not drill" % ev["mode"])
        if ev["confidence"] != "high":
            fail("evidence query row confidence is %r, not high" % ev["confidence"])
        if not isinstance(ev["response_time_ms"], int) or ev["response_time_ms"] < 0:
            fail("response_time_ms is not a non-negative int: %r" % ev["response_time_ms"])

        log = os.path.join(tmp, "_evidence", "evidence.jsonl")
        lines = [l for l in open(log, encoding="utf-8").read().splitlines() if l.strip()]
        if len(lines) != 1:
            fail("expected exactly one line in evidence.jsonl, found %d" % len(lines))

        raw = json.loads(lines[0])
        missing = EXPECTED_KEYS - set(raw)
        if missing:
            fail("raw log line missing keys: %r" % sorted(missing))
        if "bank" not in raw:
            fail("raw log line missing the bank field")
        if raw["error_category"] is not None or raw["hint_tier"] is not None:
            fail("error_category/hint_tier are not reserved null: %r / %r" %
                 (raw["error_category"], raw["hint_tier"]))
        if raw["mode"] != "drill":
            fail("raw log line mode is %r, not drill" % raw["mode"])
        if raw["confidence"] != "high":
            fail("raw log line confidence is %r, not high" % raw["confidence"])
        if raw["score"] is not True:
            fail("raw log line score is %r, not True" % raw["score"])
        if os.sep in raw["bank"] or "/" in raw["bank"]:
            fail("bank field carries a path separator: %r" % raw["bank"])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_mode_recorded():
    tmp = tempfile.mkdtemp()
    try:
        bank = os.path.join(tmp, "sample_bank.md")
        shutil.copyfile(BANK, bank)
        objective1, submitted1, q1 = start_and_submit(tmp, bank, "drill")
        objective2, submitted2, q2 = start_and_submit(tmp, bank, "exam")
        if objective1 != objective2 or q1["id"] != q2["id"]:
            fail("expected the same deterministic item across both seed-0 sessions")

        out = run(["evidence", "--objective", objective1, "--base", tmp], tmp)
        result = json.loads(out)
        if result["count"] != 2:
            fail("expected 2 events across two sessions, got %r" % result["count"])
        modes = sorted(e["mode"] for e in result["events"])
        if modes != ["drill", "exam"]:
            fail("expected drill and exam modes, got %r" % modes)
        refs = set(e["item_ref"] for e in result["events"])
        if len(refs) != 1:
            fail("expected both events to agree on item_ref, got %r" % refs)
        scores = set(e["score"] for e in result["events"])
        if scores != {True}:
            fail("expected both correct responses to agree on score, got %r" % scores)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_empty_log():
    tmp = tempfile.mkdtemp()
    try:
        out = run(["evidence", "--objective", "nothing here", "--base", tmp], tmp)
        result = json.loads(out)
        if result["count"] != 0:
            fail("expected count 0 for an objective with no log at all, got %r" %
                 result["count"])
        if result["events"] != []:
            fail("expected an empty events list, got %r" % result["events"])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_one_writer():
    """One `append_event` in the whole codebase, structurally asserted the way
    `tests/scoring_roundtrip.py` already asserts one scorer.
    """
    writers = []
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "tests")]
        for f in sorted(files):
            if not f.endswith(".py"):
                continue
            path = os.path.join(base, f)
            source = open(path, encoding="utf-8").read()
            writers += [(os.path.relpath(path, ROOT), n)
                       for n in re.findall(r"(?m)^def (append_event)\(", source)]
    if writers != [("evidence.py", "append_event")]:
        fail("expected exactly one append_event writer, found %r" % (writers,))


# ---- item identity (01-04): the evidence key survives an edit ---------------
# `fixtures/sample_bank.md` already carries [ID:]/[HASH:] lines, assigned for
# real by 01-04's Task 2 (`itembank id-assign`). These tests copy it into a
# tempdir, the same isolation pattern the tracer tests above use, so nothing
# here reads or writes the repository's own fixture.

def load_bank_text(path):
    return open(path, encoding="utf-8").read()


def write_bank_text(path, text):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


def strip_identity(text):
    """Remove every `[ID: ...]` and `[HASH: ...]` line, for constructing an
    id-less bank from one that already carries identity fields.
    """
    lines = [l for l in text.splitlines(keepends=True)
             if not re.match(r"^\[ID:\s|^\[HASH:\s", l)]
    return "".join(lines)


def id_assign_json(args_after_command, cwd):
    """Run `id-assign` and parse its JSON payload, which is followed by one
    trailing human-readable status line (per 01-04-PLAN.md Task 2) that would
    otherwise make the whole of stdout fail json.loads().
    """
    out = run(["id-assign"] + list(args_after_command), cwd)
    lines = out.splitlines()
    return json.loads("\n".join(lines[:-1]))


def lint_text(bank, cwd=None):
    r = subprocess.run([sys.executable, os.path.join(ROOT, "itembank.py"), "lint", bank],
                       cwd=cwd, capture_output=True, text=True)
    return r.returncode, r.stdout


def test_identity_survives_edit():
    """Phase success criterion 1: a stem edit leaves the evidence trail
    intact, because the key recorded against a response is the opaque
    `[ID:]`, never the content.
    """
    tmp = tempfile.mkdtemp()
    try:
        bank = os.path.join(tmp, "sample_bank.md")
        shutil.copyfile(BANK, bank)
        id_assign_json([bank], tmp)   # already assigned in the fixture; confirms idempotence

        objective, submitted, q = start_and_submit(tmp, bank, "drill")
        item_id = q["item_id"]
        if not item_id:
            fail("the served item carries no item_id even after id-assign")
        if submitted["score"] is not True:
            fail("correct answer for %s scored %r, not True" % (q["id"], submitted["score"]))

        out = run(["evidence", "--objective", objective, "--base", tmp], tmp)
        before = json.loads(out)
        if before["count"] != 1:
            fail("expected 1 recorded event before the edit, got %r" % before["count"])
        trail_before = before["events"]
        if trail_before[0]["item_id"] != item_id:
            fail("recorded event's item_id %r does not match the served item's %r" %
                 (trail_before[0]["item_id"], item_id))

        # Edit the served item's stem, leaving every other byte alone.
        text = load_bank_text(bank)
        stem_fragment = q["stem"][:40]
        if stem_fragment not in text:
            fail("could not locate the served item's stem in the bank text to edit it")
        edited = text.replace(stem_fragment, stem_fragment + ", mid-shift,", 1)
        if edited == text:
            fail("the stem edit produced no change to the bank text")
        write_bank_text(bank, edited)

        rc, lint_out = lint_text(bank, tmp)
        if rc != 0:
            fail("lint exited %d after a stem edit; a content-hash drift must be a "
                 "warning, not an error (D-04):\n%s" % (rc, lint_out))
        if "content changed since [HASH:] was recorded" not in lint_out:
            fail("lint did not report content drift after the stem edit:\n%s" % lint_out)

        qs_after_lint = itembank.load(bank)
        q_after_lint = next((x for x in qs_after_lint if x["item_id"] == item_id), None)
        if q_after_lint is None:
            fail("lint wrote to the bank: the item id %r no longer appears on disk" % item_id)

        out = run(["evidence", "--objective", objective, "--base", tmp], tmp)
        after_lint = json.loads(out)
        if after_lint["events"] != trail_before:
            fail("the evidence trail changed after a stem edit and a lint run:\n"
                 "before=%r\nafter=%r" % (trail_before, after_lint["events"]))

        reassigned = id_assign_json([bank], tmp)
        change = next((c for b in reassigned["banks"] for c in b["changes"]
                       if c["item_id"] == item_id), None)
        if change is None:
            fail("id-assign after the edit reported no change entry for item_id %r" % item_id)
        if change["hash_action"] != "updated":
            fail("id-assign after an edit reported hash_action %r, not updated" %
                 change["hash_action"])
        if change["action"] != "kept":
            fail("id-assign after an edit reported action %r, not kept -- the id must "
                 "survive the edit" % change["action"])

        out = run(["evidence", "--objective", objective, "--base", tmp], tmp)
        final = json.loads(out)
        if final["events"] != trail_before:
            fail("the evidence trail changed after re-running id-assign to refresh the hash")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_missing_and_duplicate_ids():
    tmp = tempfile.mkdtemp()
    try:
        # A bank with every [ID:]/[HASH:] line stripped lints with
        # item.missing_id warnings, zero errors, and nothing is assigned as
        # a side effect of linting.
        missing_bank = os.path.join(tmp, "missing_ids.md")
        write_bank_text(missing_bank, strip_identity(load_bank_text(BANK)))
        rc, lint_out = lint_text(missing_bank, tmp)
        if rc != 0:
            fail("lint on an id-less bank exited non-zero: %r" % lint_out)
        if lint_out.count("no [ID:] line") != 6:
            fail("expected 6 item.missing_id warnings, got:\n%s" % lint_out)
        if any(q["item_id"] for q in itembank.load(missing_bank)):
            fail("linting a bank assigned an item_id as a side effect")

        # Two items sharing the same [ID:] value: an item.duplicate_id error.
        dup_bank = os.path.join(tmp, "dup_ids.md")
        shutil.copyfile(BANK, dup_bank)
        qs = itembank.load(dup_bank)
        first_id, second_id = qs[0]["item_id"], qs[1]["item_id"]
        text = load_bank_text(dup_bank).replace(
            "[ID: %s]" % second_id, "[ID: %s]" % first_id, 1)
        write_bank_text(dup_bank, text)
        rc, lint_out = lint_text(dup_bank, tmp)
        if rc == 0:
            fail("lint with two items sharing one [ID:] exited 0")
        if "duplicate item id" not in lint_out:
            fail("lint did not report item.duplicate_id:\n%s" % lint_out)

        # id-assign over two id-less banks in one invocation assigns every id
        # distinctly across both.
        bank_a = os.path.join(tmp, "bank_a.md")
        bank_b = os.path.join(tmp, "bank_b.md")
        write_bank_text(bank_a, strip_identity(load_bank_text(BANK)))
        write_bank_text(bank_b, strip_identity(load_bank_text(BANK)))
        id_assign_json([bank_a, bank_b], tmp)
        ids_a = [q["item_id"] for q in itembank.load(bank_a)]
        ids_b = [q["item_id"] for q in itembank.load(bank_b)]
        all_ids = ids_a + ids_b
        if not all(all_ids):
            fail("id-assign left an item without an id: %r / %r" % (ids_a, ids_b))
        if len(set(all_ids)) != len(all_ids):
            fail("id-assign over two banks in one invocation produced colliding ids: %r" %
                 all_ids)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_fingerprint_whitespace_stability():
    qs = itembank.load(BANK)
    for q in qs:
        whitespace_only = dict(q)
        whitespace_only["stem"] = re.sub(r" ", "  ", q["stem"]) + "\n"
        if itembank.content_fingerprint(whitespace_only) != itembank.content_fingerprint(q):
            fail("doubling internal spaces and adding a trailing newline to the stem "
                 "changed the fingerprint for %s" % q["id"])

        one_char_changed = dict(q)
        stem = q["stem"]
        flipped = "Z" if stem[-1:] != "Z" else "Y"
        one_char_changed["stem"] = stem[:-1] + flipped
        if itembank.content_fingerprint(one_char_changed) == itembank.content_fingerprint(q):
            fail("changing one stem character left the fingerprint unchanged for %s" %
                 q["id"])


def test_hash_states():
    tmp = tempfile.mkdtemp()
    try:
        bank_text = (
            "Q1. Item that carries an id but no hash.\n"
            "[ID: aaaaaaaaaaaaaaaa]\n\n"
            "A) One\nB) Two\nC) Three\n\n"
            "CORRECT: A\n\n"
            "WHY BEST: Placeholder.\n\n"
            "TRAP: Placeholder.\n\n"
            "CONFIDENCE: high\n\n"
            "Q2. Item that carries neither an id nor a hash.\n\n"
            "A) One\nB) Two\nC) Three\n\n"
            "CORRECT: A\n\n"
            "WHY BEST: Placeholder.\n\n"
            "TRAP: Placeholder.\n\n"
            "CONFIDENCE: high\n"
        )
        bank = os.path.join(tmp, "hash_states.md")
        write_bank_text(bank, bank_text)
        r = subprocess.run(
            [sys.executable, os.path.join(ROOT, "itembank.py"), "lint", bank, "--json"],
            cwd=tmp, capture_output=True, text=True)
        payload = json.loads(r.stdout)
        by_item = {}
        for w in payload["warnings"]:
            by_item.setdefault(w["item"], []).append(w["code"])
        codes_q1 = by_item.get("Q1", [])
        codes_q2 = by_item.get("Q2", [])
        if codes_q1.count("item.missing_hash") != 1:
            fail("Q1 (has id, no hash) did not get exactly one item.missing_hash: %r" %
                 codes_q1)
        if "item.content_drift" in codes_q1:
            fail("Q1 (has id, no hash) unexpectedly got item.content_drift: %r" % codes_q1)
        if "item.missing_id" not in codes_q2:
            fail("Q2 (has neither field) did not get item.missing_id: %r" % codes_q2)
        if "item.missing_hash" in codes_q2 or "item.content_drift" in codes_q2:
            fail("Q2 (has neither field) unexpectedly got a hash warning: %r" % codes_q2)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_lint_order_stable():
    outs = []
    for _ in range(3):
        r = subprocess.run(
            [sys.executable, os.path.join(ROOT, "itembank.py"), "lint", BROKEN_BANK, "--json"],
            capture_output=True, text=True)
        outs.append(r.stdout)
    if outs[0] != outs[1] or outs[1] != outs[2]:
        fail("lint --json output is not stable across three repeated runs")
    payload = json.loads(outs[0])

    def item_num(tag):
        m = re.match(r"Q(\d+)", tag)
        return int(m.group(1)) if m else -1

    error_items = [e["item"] for e in payload["errors"]]
    if [item_num(t) for t in error_items] != sorted(item_num(t) for t in error_items):
        fail("errors are not in non-decreasing item order: %r" % error_items)

    warning_items = [w["item"] for w in payload["warnings"]]
    non_bank = [t for t in warning_items if t != "BANK"]
    if [item_num(t) for t in non_bank] != sorted(item_num(t) for t in non_bank):
        fail("warnings are not in non-decreasing item order: %r" % warning_items)
    if "BANK" in warning_items and warning_items[-1] != "BANK":
        fail("the bank-wide entry is not last among warnings: %r" % warning_items)


# ---- idempotency and retraction (01-07): D-17's distinct-response rule and --
# D-10's compensating-append undo, both proven end to end through the real CLI.

def rewind_cursor(session_file, by=1):
    """Move a session's cursor back `by` positions and mark it active again --
    exactly what a crash between the evidence append and the session write
    leaves behind, so re-submitting is a resubmission of the same item, the
    scenario D-17's dedupe rule exists for.
    """
    data = json.load(open(session_file, encoding="utf-8"))
    data["cursor"] -= by
    if data["cursor"] < 0:
        fail("rewound cursor below zero for %s" % session_file)
    data["status"] = "active"
    with open(session_file, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def different_answer(q):
    """A response that is valid to submit for `q` and genuinely differs from
    `correct_answer(q)`'s canonical form, for exercising the "a different
    answer opens the next attempt" half of D-17.
    """
    if q["type"] == "mc":
        return next(k for k in sorted(q["opts"]) if k not in q["correct"])
    if q["type"] == "multi":
        return json.dumps(sorted(k for k in q["opts"] if k not in q["correct"]))
    if q["type"] in ("table", "dnd"):
        alt = q["cats"][1] if len(q["cats"]) > 1 else q["cats"][0]
        return json.dumps(dict((str(i), alt) for i in range(len(q["rows"]))))
    if q["type"] == "build":
        return json.dumps(list(reversed(q["steps"])))
    return "A genuinely different constructed response, worded differently."


def log_lines_for_item(log, item_ref):
    if not os.path.exists(log):
        return []
    out = []
    for line in open(log, encoding="utf-8").read().splitlines():
        line = line.strip()
        if not line:
            continue
        obj = json.loads(line)
        if obj.get("event_type") == "response" and obj.get("item_ref") == item_ref:
            out.append(obj)
    return out


def test_duplicate_submit_dedupes():
    """PROTO-03. An identical retry of the current item reports
    already_recorded and names the event already there; a genuinely
    different answer opens attempt 2. Covers one auto-scored item and the
    `short` item, whose fallback (RESEARCH.md Pitfall 1) is the one this
    test must not let regress: neither "the same short answer twice does
    not dedupe" nor "two different short answers dedupe" may pass.
    """
    tmp = tempfile.mkdtemp()
    try:
        bank = os.path.join(tmp, "sample_bank.md")
        shutil.copyfile(BANK, bank)
        qs_by_id = {q["id"]: q for q in itembank.load(bank)}
        log = os.path.join(tmp, "_evidence", "evidence.jsonl")

        started = json.loads(run(["start", bank, "--count", "6", "--seed", "0"], tmp))
        session_file = started["session_file"]

        auto_tested = short_tested = False
        data = json.load(open(session_file, encoding="utf-8"))
        while data["status"] == "active":
            nxt = json.loads(run(["next", session_file], tmp))
            if nxt["status"] != "active":
                break
            q = qs_by_id[nxt["item"]["id"]]

            if q["type"] != "short" and not auto_tested:
                answer1 = correct_answer(q)
                r1 = json.loads(run(["submit", session_file, "--answer", answer1], tmp))
                if r1["evidence"]["status"] != "recorded":
                    fail("first submit of %s reported %r, not recorded" %
                         (q["id"], r1["evidence"]["status"]))
                event_id_1 = r1["evidence"]["event_id"]

                rewind_cursor(session_file)
                r2 = json.loads(run(["submit", session_file, "--answer", answer1], tmp))
                if r2["evidence"]["status"] != "already_recorded":
                    fail("identical retry of %s reported %r, not already_recorded" %
                         (q["id"], r2["evidence"]["status"]))
                if r2["evidence"]["event_id"] != event_id_1:
                    fail("retry of %s named event_id %r, not the original %r" %
                         (q["id"], r2["evidence"]["event_id"], event_id_1))
                lines = log_lines_for_item(log, q["id"])
                if len(lines) != 1:
                    fail("expected 1 log line for %s after an identical retry, found %d" %
                         (q["id"], len(lines)))

                rewind_cursor(session_file)
                answer2 = different_answer(q)
                r3 = json.loads(run(["submit", session_file, "--answer", answer2], tmp))
                if r3["evidence"]["status"] != "recorded":
                    fail("a genuinely different answer to %s reported %r, not recorded" %
                         (q["id"], r3["evidence"]["status"]))
                if r3["evidence"]["event_id"] == event_id_1:
                    fail("a different answer to %s reused the first event_id" % q["id"])
                lines = log_lines_for_item(log, q["id"])
                if len(lines) != 2:
                    fail("expected 2 log lines for %s after a different answer, found %d" %
                         (q["id"], len(lines)))
                second = next(l for l in lines if l["event_id"] == r3["evidence"]["event_id"])
                if second["attempt_number"] != 2:
                    fail("a different answer to %s recorded attempt_number %r, not 2" %
                         (q["id"], second["attempt_number"]))
                auto_tested = True

            elif q["type"] == "short" and not short_tested:
                base = "The parameters are within limits, but taste and odour are separate."
                r1 = json.loads(run(["submit", session_file, "--answer", base], tmp))
                if r1["evidence"]["status"] != "recorded":
                    fail("first short submit reported %r, not recorded" %
                         r1["evidence"]["status"])
                event_id_1 = r1["evidence"]["event_id"]
                first_raw = next(l for l in log_lines_for_item(log, q["id"])
                                 if l["event_id"] == event_id_1)
                if not first_raw["canonical"].startswith("short:"):
                    fail("short event's canonical %r does not start with 'short:'" %
                         first_raw["canonical"])
                if first_raw["score"] is not None:
                    fail("short event's score is %r, not None" % first_raw["score"])

                rewind_cursor(session_file)
                reflowed = "  ".join(base.upper().split())   # same words, different case/spacing
                r2 = json.loads(run(["submit", session_file, "--answer", reflowed], tmp))
                if r2["evidence"]["status"] != "already_recorded":
                    fail("a re-cased, re-spaced retry of the same short answer reported %r, "
                         "not already_recorded" % r2["evidence"]["status"])
                if r2["evidence"]["event_id"] != event_id_1:
                    fail("a re-cased, re-spaced retry of the same short answer named a "
                         "different event_id")

                rewind_cursor(session_file)
                different = "A completely different explanation about disinfection byproducts."
                r3 = json.loads(run(["submit", session_file, "--answer", different], tmp))
                if r3["evidence"]["status"] != "recorded":
                    fail("a genuinely different short answer reported %r, not recorded" %
                         r3["evidence"]["status"])
                if r3["evidence"]["event_id"] == event_id_1:
                    fail("a genuinely different short answer reused the first event_id")
                third_raw = next(l for l in log_lines_for_item(log, q["id"])
                                 if l["event_id"] == r3["evidence"]["event_id"])
                if not third_raw["canonical"].startswith("short:"):
                    fail("second short event's canonical %r does not start with 'short:'" %
                         third_raw["canonical"])
                if third_raw["score"] is not None:
                    fail("second short event's score is %r, not None" % third_raw["score"])
                short_tested = True

            else:
                run(["submit", session_file, "--answer", correct_answer(q)], tmp)

            data = json.load(open(session_file, encoding="utf-8"))

        if not auto_tested:
            fail("no auto-scored item was tested for duplicate-submit dedupe")
        if not short_tested:
            fail("no short item was tested for duplicate-submit dedupe")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_retraction():
    """EVID-05. Undo is an append, never a removal (D-10): a retraction
    suppresses its target in every view and count without deleting the
    original line, a retraction that physically precedes its target still
    suppresses it, and a retracted response no longer holds an attempt open.
    """
    tmp = tempfile.mkdtemp()
    try:
        bank = os.path.join(tmp, "sample_bank.md")
        shutil.copyfile(BANK, bank)
        objective = "Regulatory framework"   # shared by Q5 (dnd) and Q6 (short)
        qs = {q["id"]: q for q in itembank.load(bank)}
        log = os.path.join(tmp, "_evidence", "evidence.jsonl")

        started = json.loads(run(
            ["start", bank, "--objective", objective, "--count", "2", "--seed", "0"], tmp))
        session_file = started["session_file"]
        event_ids = []
        data = json.load(open(session_file, encoding="utf-8"))
        while data["status"] == "active":
            nxt = json.loads(run(["next", session_file], tmp))
            if nxt["status"] != "active":
                break
            q = qs[nxt["item"]["id"]]
            r = json.loads(run(["submit", session_file, "--answer", correct_answer(q)], tmp))
            event_ids.append(r["evidence"]["event_id"])
            data = json.load(open(session_file, encoding="utf-8"))

        if len(event_ids) != 2:
            fail("expected 2 recorded responses under objective %r, got %d" %
                 (objective, len(event_ids)))

        before = json.loads(run(["evidence", "--objective", objective, "--base", tmp], tmp))
        if before["count"] != 2:
            fail("expected count 2 before any retraction, got %r" % before["count"])
        if before["retracted"] != 0:
            fail("expected retracted 0 before any retraction, got %r" % before["retracted"])

        lines_before = [l for l in open(log, encoding="utf-8").read().splitlines() if l.strip()]
        target = event_ids[0]
        result = json.loads(run(
            ["retract", target, "--reason", "wrong bank, superseded", "--base", tmp], tmp))
        if result["status"] != "retracted":
            fail("retracting a real event reported %r, not retracted" % result["status"])

        lines_after = [l for l in open(log, encoding="utf-8").read().splitlines() if l.strip()]
        if len(lines_after) != len(lines_before) + 1:
            fail("retraction did not append exactly one line: %d -> %d" %
                 (len(lines_before), len(lines_after)))
        original_line = next(
            (l for l in lines_after if json.loads(l).get("event_id") == target), None)
        if original_line is None:
            fail("the original event's line is no longer present after retraction")
        json.loads(original_line)   # still parses

        after = json.loads(run(["evidence", "--objective", objective, "--base", tmp], tmp))
        if after["count"] != 1:
            fail("expected count 1 after retracting one of two events, got %r" % after["count"])
        if after["retracted"] != 1:
            fail("expected retracted 1 after retracting one of two events, got %r" %
                 after["retracted"])

        # Retracting the same event again: already_retracted, no new line.
        result2 = json.loads(run(
            ["retract", target, "--reason", "duplicate retraction attempt", "--base", tmp], tmp))
        if result2["status"] != "already_retracted":
            fail("retracting an already-retracted event reported %r" % result2["status"])
        lines_after2 = [l for l in open(log, encoding="utf-8").read().splitlines() if l.strip()]
        if len(lines_after2) != len(lines_after):
            fail("retracting an already-retracted event appended a line")

        # Retracting an unknown id: non-zero exit, "no event", no new line.
        r = subprocess.run(
            [sys.executable, os.path.join(ROOT, "itembank.py"), "retract", "not-a-real-id",
             "--reason", "test", "--base", tmp],
            cwd=tmp, capture_output=True, text=True)
        if r.returncode == 0:
            fail("retracting an unknown event id exited 0")
        if "no event" not in (r.stdout + r.stderr):
            fail("retracting an unknown event id did not name 'no event': %r" %
                 (r.stdout + r.stderr))
        lines_after3 = [l for l in open(log, encoding="utf-8").read().splitlines() if l.strip()]
        if len(lines_after3) != len(lines_after2):
            fail("retracting an unknown event id appended a line")

        # A hand-built log whose retraction line physically precedes its
        # target: retracted_ids is collected over the whole log first, so
        # live_events still suppresses the target.
        synth_dir = tempfile.mkdtemp()
        try:
            synth_log = itembank.log_path(synth_dir)
            sample_q = next(iter(qs.values()))
            fake_event = itembank.response_event(
                "synth-session", sample_q, "A", True, "drill", 1, "synth_bank.md")
            fake_retraction = itembank.retraction_event(fake_event["event_id"], "ordering test")
            itembank.append_line(synth_log, json.dumps(fake_retraction, ensure_ascii=False))
            itembank.append_line(synth_log, json.dumps(fake_event, ensure_ascii=False))
            live_ids = set(ev["event_id"] for ev in itembank.live_events(synth_log))
            if fake_event["event_id"] in live_ids:
                fail("a retraction physically preceding its target failed to suppress it")
        finally:
            shutil.rmtree(synth_dir, ignore_errors=True)

        # A retracted response no longer holds an attempt open: retracting
        # the only response for a fresh item and resubmitting the same
        # answer reports 'recorded', not 'already_recorded'.
        solo_started = json.loads(run(["start", bank, "--count", "1", "--seed", "0"], tmp))
        solo_session = solo_started["session_file"]
        solo_q = qs[solo_started["item"]["id"]]
        solo_answer = correct_answer(solo_q)
        solo_r1 = json.loads(run(["submit", solo_session, "--answer", solo_answer], tmp))
        if solo_r1["evidence"]["status"] != "recorded":
            fail("solo item's first submit reported %r, not recorded" %
                 solo_r1["evidence"]["status"])
        run(["retract", solo_r1["evidence"]["event_id"], "--reason",
             "retract the only response", "--base", tmp], tmp)
        rewind_cursor(solo_session)
        solo_r2 = json.loads(run(["submit", solo_session, "--answer", solo_answer], tmp))
        if solo_r2["evidence"]["status"] != "recorded":
            fail("resubmitting the same answer after retracting the only response reported "
                 "%r, not recorded" % solo_r2["evidence"]["status"])
        if solo_r2["evidence"]["event_id"] == solo_r1["evidence"]["event_id"]:
            fail("resubmitting after retraction reused the retracted event's id")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    test_tracer_end_to_end()
    test_mode_recorded()
    test_empty_log()
    test_one_writer()
    test_identity_survives_edit()
    test_missing_and_duplicate_ids()
    test_fingerprint_whitespace_stability()
    test_hash_states()
    test_lint_order_stable()
    test_duplicate_submit_dedupes()
    test_retraction()
    print("evidence contract: ok (tracer end-to-end, mode recorded, empty log, one writer, "
          "identity survives edit, missing/duplicate ids, fingerprint stability, hash "
          "states, lint order, duplicate-submit dedupe, retraction)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
