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


def flatten(obj):
    """Yield (key, value) for every key at every depth of a JSON-like
    structure -- used to assert a gamification key (points/level/badge/...)
    is absent anywhere in an evidence query's output, not just at the top
    level (PROJECT.md Out of Scope: no score, level, badge, streak, xp).
    """
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield (k, v)
            yield from flatten(v)
    elif isinstance(obj, list):
        for el in obj:
            yield from flatten(el)


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

        # EVID-08's visible half (01-08): a drill correct and an exam correct
        # are counted in different by_mode buckets, never summed into one.
        by_mode = result["by_mode"]
        if set(by_mode) != {"drill", "exam"}:
            fail("expected by_mode keys {'drill', 'exam'}, got %r" % set(by_mode))
        if by_mode["drill"]["correct"] != 1 or by_mode["exam"]["correct"] != 1:
            fail("expected each mode's by_mode bucket to report correct 1, got %r" % by_mode)
        combined_totals = [v for k, v in flatten(result) if k in
                           ("score_total", "combined_correct", "total_correct")]
        if combined_totals:
            fail("found a combined-total key in evidence output: %r" % combined_totals)
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


def mark_json(args_after_command, cwd):
    """Run `mark` and parse its JSON payload, which is followed by one
    trailing human-readable status line (per 01-09-PLAN.md Task 2, the same
    "%d ..., %d ..." house style `id_assign_json` above already strips).
    """
    out = run(["mark"] + list(args_after_command), cwd)
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


# ---- disposable index and cross-subject query (01-08) ---------------------
# D-08: queries are served by a disposable derived index, rebuilt whenever
# the log has grown past it and deletable at any time with no loss. This is
# phase success criterion 4: one query answers "how am I doing on objective
# X over time" across every session and every subject.

SYNTH_BANK_TEXT = """# Synthetic cross-subject bank (test fixture)

Fully invented content for exercising a namespaced, cross-subject objective
query. Not derived from any real course, exam, or textbook.

Q1. Sample synthetic item about one airway management surface, for
cross-subject and cross-session query testing.

[OBJECTIVE: emt:airway.opa]

A) Option one
B) Option two
C) Option three

CORRECT: A

WHY BEST: Placeholder rationale for the correct answer.

Q2. Sample synthetic item about a different, longer-named airway management
surface, for prefix-adjacency testing.

[OBJECTIVE: emt:airwaymanagement]

A) Option one
B) Option two
C) Option three

CORRECT: A

WHY BEST: Placeholder rationale for the correct answer.

Q3. Sample synthetic item about while loops, for cross-subject query
testing.

[OBJECTIVE: csci1100:loops.while]

A) Option one
B) Option two
C) Option three

CORRECT: A

WHY BEST: Placeholder rationale for the correct answer.
"""


def parse_json_tail(out):
    """Parse the trailing JSON document in `out`, skipping any leading
    `warn  ...` lines a fallback path may have printed to stdout ahead of
    it (evidence.py's degrade-never-block warnings never go to stderr, so a
    query that fell back still exits 0 with a parseable JSON tail).
    """
    return json.loads(out[out.index("{"):])


def test_objective_query():
    """EVID-04, the cross-subject requirement specifically: one query
    answers the objective question across every session and every subject,
    exact match is the default, prefix matching is explicit and does not
    match a longer word, an empty history is not an error, and events
    sharing a `ts` keep a stable log order across a rebuilt index.
    """
    tmp = tempfile.mkdtemp()
    try:
        bank = os.path.join(tmp, "synth_bank.md")
        write_bank_text(bank, SYNTH_BANK_TEXT)
        id_assign_json([bank], tmp)
        rc, lint_out = lint_text(bank, tmp)
        if rc != 0:
            fail("synthetic cross-subject bank fixture does not lint clean:\n%s" % lint_out)
        qs = {q["id"]: q for q in itembank.load(bank)}

        # Two sessions, the same objective (emt:airway.opa): cross-session
        # reach for one objective, the thing that was impossible before
        # this phase.
        sA = json.loads(run(
            ["start", bank, "--objective", "emt:airway.opa", "--count", "1",
             "--seed", "0", "--mode", "drill"], tmp))
        run(["submit", sA["session_file"], "--answer",
             correct_answer(qs[sA["item"]["id"]])], tmp)

        sB = json.loads(run(
            ["start", bank, "--objective", "emt:airway.opa", "--count", "1",
             "--seed", "0", "--mode", "exam"], tmp))
        run(["submit", sB["session_file"], "--answer",
             correct_answer(qs[sB["item"]["id"]])], tmp)

        # A third session, a different (longer) objective under the same
        # subject -- the prefix-adjacency guard.
        sD = json.loads(run(
            ["start", bank, "--objective", "emt:airwaymanagement", "--count", "1",
             "--seed", "0"], tmp))
        run(["submit", sD["session_file"], "--answer",
             correct_answer(qs[sD["item"]["id"]])], tmp)

        # A fourth session, a second subject entirely.
        sC = json.loads(run(
            ["start", bank, "--objective", "csci1100:loops.while", "--count", "1",
             "--seed", "0", "--mode", "exam"], tmp))
        run(["submit", sC["session_file"], "--answer",
             correct_answer(qs[sC["item"]["id"]])], tmp)

        # Exact match, cross-session: both sessionA and sessionB's rows,
        # ascending ts order, neither the emt:airwaymanagement nor the
        # csci1100 row.
        exact = parse_json_tail(run(
            ["evidence", "--objective", "emt:airway.opa", "--base", tmp], tmp))
        if exact["count"] != 2:
            fail("expected 2 events under emt:airway.opa across two sessions, got %r" %
                 exact["count"])
        sessions = set(e["session_id"] for e in exact["events"])
        if len(sessions) != 2:
            fail("expected rows from two distinct sessions, got session_ids %r" % sessions)
        tss = [e["ts"] for e in exact["events"]]
        if tss != sorted(tss):
            fail("emt:airway.opa events are not in ascending ts order: %r" % tss)

        # Subject alone, no --objective: only the csci1100 row, and a
        # subject-only query is accepted.
        by_subject = parse_json_tail(run(
            ["evidence", "--subject", "csci1100", "--base", tmp], tmp))
        if by_subject["count"] != 1:
            fail("expected 1 event under subject csci1100, got %r" % by_subject["count"])
        if by_subject["events"][0]["item_ref"] != sC["item"]["id"]:
            fail("subject query returned the wrong item: %r" % by_subject["events"][0])

        # Adjacency: exact "emt:airway" matches nothing; --prefix matches
        # the two emt:airway.opa rows and never the longer
        # emt:airwaymanagement objective.
        no_prefix = parse_json_tail(run(
            ["evidence", "--objective", "emt:airway", "--base", tmp], tmp))
        if no_prefix["count"] != 0:
            fail("exact match on 'emt:airway' unexpectedly matched %r rows" %
                 no_prefix["count"])

        with_prefix = parse_json_tail(run(
            ["evidence", "--objective", "emt:airway", "--prefix", "--base", tmp], tmp))
        if with_prefix["count"] != 2:
            fail("prefix match on 'emt:airway' expected 2 rows, got %r" %
                 with_prefix["count"])
        prefix_refs = set(e["item_ref"] for e in with_prefix["events"])
        if prefix_refs != {sA["item"]["id"]}:
            fail("prefix match on 'emt:airway' returned unexpected item_refs %r "
                 "(the emt:airwaymanagement item must never appear here)" % prefix_refs)

        # Empty rule: an objective with no recorded events is count 0, exit 0.
        empty = parse_json_tail(run(
            ["evidence", "--objective", "nothing:here", "--base", tmp], tmp))
        if empty["count"] != 0 or empty["events"] != []:
            fail("expected an empty history for an unused objective, got %r" % empty)

        # Ordering rule: two hand-built events sharing one ts, appended in a
        # specific log order under their own objective, are returned in
        # that log order -- not sorted by event_id -- and the order
        # survives an explicit --rebuild-index.
        log = itembank.log_path(tmp)
        shared_ts = "2020-01-01T00:00:00.000Z"
        sample_q = next(iter(qs.values()))
        first = itembank.response_event(
            "order-session", sample_q, "A", False, "drill", 1, "synth_bank.md")
        first["objective"], first["subject"] = "emt:ordertest", "emt"
        first["ts"] = shared_ts
        first["event_id"] = "zzzz_first_by_log_order"
        second = itembank.response_event(
            "order-session", sample_q, "A", True, "drill", 2, "synth_bank.md")
        second["objective"], second["subject"] = "emt:ordertest", "emt"
        second["ts"] = shared_ts
        second["event_id"] = "aaaa_second_by_log_order"
        itembank.append_line(log, json.dumps(first, ensure_ascii=False, sort_keys=True))
        itembank.append_line(log, json.dumps(second, ensure_ascii=False, sort_keys=True))

        ordered = parse_json_tail(run(
            ["evidence", "--objective", "emt:ordertest", "--base", tmp], tmp))
        if [e["score"] for e in ordered["events"]] != [False, True]:
            fail("hand-built same-ts events were not returned in log order: %r" %
                 ordered["events"])

        rebuilt = parse_json_tail(run(
            ["evidence", "--objective", "emt:ordertest", "--rebuild-index", "--base", tmp],
            tmp))
        if [e["score"] for e in rebuilt["events"]] != [False, True]:
            fail("same-ts log order changed after --rebuild-index: %r" % rebuilt["events"])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_index_is_disposable():
    """D-08's central claim: the sqlite3 projection is a disposable cache,
    never a second source of truth. Deleting it, corrupting it, or making
    its path permanently unwritable must never change a query's answer,
    and a query must never write to the log itself.
    """
    tmp = tempfile.mkdtemp()
    try:
        bank = os.path.join(tmp, "sample_bank.md")
        shutil.copyfile(BANK, bank)
        objective, submitted, q = start_and_submit(tmp, bank, "drill")
        if submitted["score"] is not True:
            fail("setup: correct answer for %s scored %r, not True" % (q["id"], submitted["score"]))

        log = itembank.log_path(tmp)
        index = os.path.join(tmp, "_evidence", "evidence_index.sqlite3")

        args = ["evidence", "--objective", objective, "--base", tmp]
        first = run(args, tmp)
        if not os.path.exists(index):
            fail("a query never built the disposable index at all")
        if "evidence index unavailable" in first:
            fail("the very first query, with nothing wrong yet, printed the "
                 "fallback warning -- ensure_index() is not being called before "
                 "the index is read, or is failing when it should not: %r" % first)

        # Staleness: an event appended directly to the log (bypassing the
        # CLI, so the index just built above is now behind it) must be
        # reflected on the very next query -- proving the query path
        # actually calls ensure_index() rather than reading a frozen index.
        # A regression that skipped ensure_index would leave the existing,
        # still-valid index answering with the old, now-wrong count, and a
        # regression that skipped it AND left the index unbuilt in the first
        # place would print the fallback warning above instead of staying
        # silent -- either way this section catches it.
        extra = itembank.response_event(
            "stale-check-session", q, correct_answer(q), True, "drill", 1,
            os.path.basename(bank))
        extra["objective"], extra["subject"] = objective, itembank.subject_of(objective)
        itembank.append_line(log, json.dumps(extra, ensure_ascii=False, sort_keys=True))
        refreshed_raw = run(args, tmp)
        if "evidence index unavailable" in refreshed_raw:
            fail("a routine query after a plain log append printed the fallback "
                 "warning: %r" % refreshed_raw)
        refreshed = parse_json_tail(refreshed_raw)
        if refreshed["count"] != 2:
            fail("a query did not pick up an event appended directly to the log since "
                 "the index was last built -- ensure_index must run on every query, "
                 "got count %r" % refreshed["count"])

        # Re-baseline: everything from here on treats this two-event state
        # as the ground truth the index must never be able to diverge from.
        first = run(args, tmp)
        log_bytes_before = open(log, "rb").read()

        # Deleting the index and re-running the same query returns
        # byte-identical output: the index is rebuilt from the log alone,
        # with no prompt.
        os.remove(index)
        second = run(args, tmp)
        if second != first:
            fail("deleting the index changed the query's output:\nbefore=%r\nafter=%r" %
                 (first, second))
        if not os.path.exists(index):
            fail("re-running the query after deleting the index did not rebuild it")

        # Corrupting the index (a few bytes of garbage, not a valid sqlite3
        # file) still returns the same rows and exits 0 -- either by
        # rebuilding or through the fallback.
        with open(index, "wb") as fh:
            fh.write(b"not a sqlite database")
        third = run(args, tmp)
        if parse_json_tail(third)["events"] != parse_json_tail(first)["events"]:
            fail("a corrupted index changed the query's rows")

        # Making the index path permanently unwritable (an existing
        # directory at that exact path) still returns the same rows,
        # prints the fallback warning, and exits 0 -- the assertion that
        # the index is a cache and not the store.
        if os.path.exists(index):
            if os.path.isdir(index):
                shutil.rmtree(index)
            else:
                os.remove(index)
        os.makedirs(index)
        try:
            fourth = run(args, tmp)
            if "evidence index unavailable" not in fourth:
                fail("an unwritable index path did not print the fallback warning")
            if parse_json_tail(fourth)["events"] != parse_json_tail(first)["events"]:
                fail("an unwritable index changed the query's rows")
        finally:
            shutil.rmtree(index, ignore_errors=True)

        # A query never writes to the system of record.
        log_bytes_after = open(log, "rb").read()
        if log_bytes_after != log_bytes_before:
            fail("evidence.jsonl changed after a series of queries; "
                 "a query must never write to the log")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---- renders and marking (01-09): D-11's views over the log, and D-12's ----
# batch marking command, both proven end to end against the real CLI and
# against the log directly rather than against themselves.

SHORT_ANSWER_TEXT = ("The plant meets primary limits, but customers notice iron "
                     "staining and an odour, which are secondary aesthetic "
                     "parameters, not health violations.")


def drive_full_session(tmp, bank, mode="diagnostic"):
    """Start a session covering every item in `bank`, answer every item
    (alternating correct/wrong for auto-scored types, a real sentence for
    the `short` item), and return `(session_id, qs, qs_by_id, short_ref,
    auto_refs)`. Shared by `test_renders_match_log` and `test_mark_flow` so
    neither reimplements the driving loop.
    """
    qs = itembank.load(bank)
    qs_by_id = {q["id"]: q for q in qs}
    started = json.loads(run(
        ["start", bank, "--count", str(len(qs)), "--seed", "0", "--mode", mode], tmp))
    session_file = started["session_file"]
    session_id = started["session_id"]

    short_ref = None
    auto_refs = []
    i = 0
    data = json.load(open(session_file, encoding="utf-8"))
    while data["status"] == "active":
        nxt = json.loads(run(["next", session_file], tmp))
        if nxt["status"] != "active":
            break
        q = qs_by_id[nxt["item"]["id"]]
        if q["type"] == "short":
            short_ref = q["id"]
            answer = SHORT_ANSWER_TEXT
        else:
            auto_refs.append(q["id"])
            answer = correct_answer(q) if i % 2 == 0 else different_answer(q)
        run(["submit", session_file, "--answer", answer], tmp)
        i += 1
        data = json.load(open(session_file, encoding="utf-8"))

    if short_ref is None:
        fail("no short item was served while driving the session")
    return session_id, qs, qs_by_id, short_ref, auto_refs


def test_renders_match_log():
    """EVID-03: the attempt markdown and the session JSON are views over
    the log, never a second store, checked against `session_events`
    directly (not against themselves) for ordering and idempotency, and
    against the schema for shape.
    """
    tmp = tempfile.mkdtemp()
    try:
        bank = os.path.join(tmp, "sample_bank.md")
        shutil.copyfile(BANK, bank)
        log = itembank.log_path(tmp)

        session_id, qs, qs_by_id, short_ref, auto_refs = drive_full_session(
            tmp, bank, mode="practice")

        log_events = itembank.session_events(log, session_id)
        if not log_events:
            fail("session_events returned nothing for a driven session")

        session_json = itembank.render_session_json(log, session_id, qs, bank)
        if len(session_json["responses"]) != len(log_events):
            fail("rendered session JSON has %d responses, the log holds %d" %
                 (len(session_json["responses"]), len(log_events)))
        for rendered, ev in zip(session_json["responses"], log_events):
            if rendered["item_id"] != ev["item_ref"]:
                fail("rendered response item_id %r does not match the log's item_ref %r" %
                     (rendered["item_id"], ev["item_ref"]))
            if rendered["score"] != ev["score"]:
                fail("rendered response score %r does not match the log's score %r for %r" %
                     (rendered["score"], ev["score"], ev["item_ref"]))

        schema = json.load(open(os.path.join(ROOT, "schemas", "session.schema.json"),
                                encoding="utf-8"))
        errs = itembank.validate(session_json, schema)
        if errs:
            fail("rendered session JSON fails schema validation: %r" % errs)

        # Idempotency: rendering twice, from the same log, is byte-identical.
        attempt_1 = itembank.render_attempt_md(log, session_id, qs, bank)
        attempt_2 = itembank.render_attempt_md(log, session_id, qs, bank)
        if attempt_1 != attempt_2:
            fail("render_attempt_md is not byte-identical across two calls")
        session_text_1 = json.dumps(session_json, ensure_ascii=False, sort_keys=True)
        session_text_2 = json.dumps(
            itembank.render_session_json(log, session_id, qs, bank),
            ensure_ascii=False, sort_keys=True)
        if session_text_1 != session_text_2:
            fail("render_session_json is not byte-identical across two calls")

        # Appending an event for a DIFFERENT session changes nothing here --
        # the render is scoped to its own session_id.
        other_q = qs[0]
        other_event = itembank.response_event(
            "unrelated-session", other_q, correct_answer(other_q), True, "drill", 1,
            os.path.basename(bank))
        itembank.append_line(log, json.dumps(other_event, ensure_ascii=False, sort_keys=True))
        attempt_3 = itembank.render_attempt_md(log, session_id, qs, bank)
        if attempt_3 != attempt_1:
            fail("rendering after an unrelated session's event changed the output")

        # runtime.response_text's own documented property survives the move
        # to a render: the attempt markdown carries option TEXT for an
        # mc/multi answer, not a bare letter that a reshuffled page would
        # reassign to a different option next time.
        text_found = False
        for ev in log_events:
            if ev.get("item_type") not in ("mc", "multi"):
                continue
            q = qs_by_id[ev["item_ref"]]
            given = ev["answer"] if isinstance(ev["answer"], list) else [ev["answer"]]
            option_text = q["opts"].get(str(given[0]).strip().upper())
            if option_text and option_text in attempt_1:
                text_found = True
                break
        if not text_found:
            fail("attempt markdown does not carry option text for any mc/multi answer")

        # Ordering: two hand-built response events sharing one ts, appended
        # in a specific log order, render in that log order -- not sorted
        # by event_id -- and the order survives an explicit --rebuild-index
        # of the (unrelated) disposable query index.
        order_session = "order-session-" + session_id[:8]
        shared_ts = "2020-06-01T00:00:00.000Z"
        sample_q = qs[0]
        first = itembank.response_event(
            order_session, sample_q, "A", False, "drill", 1, os.path.basename(bank))
        first["ts"] = shared_ts
        first["event_id"] = "zzzz_first_by_log_order"
        second = itembank.response_event(
            order_session, sample_q, "A", True, "drill", 2, os.path.basename(bank))
        second["ts"] = shared_ts
        second["event_id"] = "aaaa_second_by_log_order"
        itembank.append_line(log, json.dumps(first, ensure_ascii=False, sort_keys=True))
        itembank.append_line(log, json.dumps(second, ensure_ascii=False, sort_keys=True))

        ordered = itembank.session_events(log, order_session)
        if [ev["score"] for ev in ordered] != [False, True]:
            fail("hand-built same-ts events were not returned in log order: %r" %
                 [ev["event_id"] for ev in ordered])

        run(["evidence", "--session", order_session, "--rebuild-index", "--base", tmp], tmp)
        ordered_after_rebuild = itembank.session_events(log, order_session)
        if [ev["score"] for ev in ordered_after_rebuild] != [False, True]:
            fail("same-ts log order changed after --rebuild-index: %r" %
                 [ev["event_id"] for ev in ordered_after_rebuild])

        # Retraction: retracting one response removes exactly its section
        # and drops the status line's count by one -- every count in a
        # render is post-retraction (D-10).
        target_event = next(ev for ev in log_events if ev["item_ref"] != short_ref)
        before_count = len(itembank.session_events(log, session_id))
        if ("**Status:** %d response(s)" % before_count) not in attempt_1:
            fail("test setup: expected the status line to name %d responses "
                 "before retraction:\n%s" % (before_count, attempt_1))
        run(["retract", target_event["event_id"], "--reason", "render test retraction",
             "--base", tmp], tmp)

        after_events = itembank.session_events(log, session_id)
        if len(after_events) != before_count - 1:
            fail("retracting one response did not drop session_events by exactly one")
        attempt_after = itembank.render_attempt_md(log, session_id, qs, bank)
        if ("**Status:** %d response(s)" % (before_count - 1)) not in attempt_after:
            fail("attempt markdown's status count did not drop by one after "
                 "retraction:\n%s" % attempt_after)
        retracted_q = qs_by_id[target_event["item_ref"]]
        if retracted_q["stem"][:30] in attempt_after:
            fail("the retracted item's stem is still present in the rendered "
                 "attempt markdown after retraction")

        session_after = itembank.render_session_json(log, session_id, qs, bank)
        if len(session_after["responses"]) != before_count - 1:
            fail("rendered session JSON did not drop by one response after retraction")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_mark_flow():
    """D-12 and EVID-07's review_state: a batch marks several answers in
    one invocation, a corrected verdict records as a new live mark rather
    than mutating the old one, an undo restores the prior verdict, and the
    underlying response event's own score is never touched by any of it.
    """
    tmp = tempfile.mkdtemp()
    try:
        bank = os.path.join(tmp, "sample_bank.md")
        shutil.copyfile(BANK, bank)
        log = itembank.log_path(tmp)

        session_id, qs, qs_by_id, short_ref, auto_refs = drive_full_session(tmp, bank)
        if len(auto_refs) < 2:
            fail("expected at least two auto-scored items to mark alongside the "
                 "short item, got %r" % auto_refs)

        attempt_before = itembank.render_attempt_md(log, session_id, qs, bank)
        if "MARK: pending" not in attempt_before:
            fail("an unmarked short item did not render MARK: pending:\n%s" %
                 attempt_before)

        short_q = qs_by_id[short_ref]
        marks_file = os.path.join(tmp, "marks.ndjson")
        with open(marks_file, "w", encoding="utf-8") as fh:
            fh.write(json.dumps({
                "item_ref": short_ref, "verdict": True,
                "rubric": [{"point": p, "pass": True} for p in short_q["rubric"]],
                "notes": "covers every rubric point",
            }) + "\n")
            fh.write(json.dumps({"item_ref": auto_refs[0], "verdict": True}) + "\n")
            fh.write(json.dumps({"item_ref": auto_refs[1], "verdict": True}) + "\n")

        result1 = mark_json(["--session", session_id, "--file", marks_file], tmp)
        if result1["recorded"] != 3 or result1["already_recorded"] != 0:
            fail("a genuine three-entry batch reported %r, not recorded 3" % result1)

        attempt_marked = itembank.render_attempt_md(log, session_id, qs, bank)
        if "MARK: PASS" not in attempt_marked:
            fail("a marked short item did not render MARK: PASS:\n%s" % attempt_marked)
        if "(pass)" not in attempt_marked:
            fail("a marked short item's rubric outcomes did not render:\n%s" %
                 attempt_marked)

        # Re-running the identical batch dedupes: the log grows by zero lines.
        lines_before_replay = len(
            [l for l in open(log, encoding="utf-8").read().splitlines() if l.strip()])
        result2 = mark_json(["--session", session_id, "--file", marks_file], tmp)
        if result2["already_recorded"] != 3 or result2["recorded"] != 0:
            fail("replaying an identical mark batch reported %r, not "
                 "already_recorded 3" % result2)
        lines_after_replay = len(
            [l for l in open(log, encoding="utf-8").read().splitlines() if l.strip()])
        if lines_after_replay != lines_before_replay:
            fail("replaying an identical mark batch appended a line to the log: "
                 "%d -> %d" % (lines_before_replay, lines_after_replay))

        # A correction: mark the short item again with the opposite verdict.
        result3 = mark_json(
            ["--session", session_id, "--item", short_ref, "--verdict", "fail"], tmp)
        if result3["recorded"] != 1:
            fail("a corrected verdict reported %r, not recorded" % result3)
        flip_event_id = result3["marks"][0]["event_id"]
        attempt_flipped = itembank.render_attempt_md(log, session_id, qs, bank)
        if "MARK: FAIL" not in attempt_flipped:
            fail("the corrected verdict did not render as MARK: FAIL:\n%s" %
                 attempt_flipped)

        # Undo the correction: the render shows the original verdict again.
        run(["retract", flip_event_id, "--reason", "undo the test correction",
             "--base", tmp], tmp)
        attempt_restored = itembank.render_attempt_md(log, session_id, qs, bank)
        if "MARK: PASS" not in attempt_restored:
            fail("retracting the correcting mark did not restore MARK: PASS:\n%s" %
                 attempt_restored)

        # The response event's own score is untouched throughout -- a mark
        # is a separate fact about it, never a mutation of it (T-1-23).
        short_events = [ev for ev in itembank.session_events(log, session_id)
                        if ev["item_ref"] == short_ref]
        if len(short_events) != 1:
            fail("expected exactly one live response event for the short item, "
                 "found %d" % len(short_events))
        if short_events[0]["score"] is not None:
            fail("the short item's response event score changed after marking: %r" %
                 short_events[0]["score"])

        # Marking something never answered in this session is a named error,
        # and appends nothing.
        lines_before_bad = len(
            [l for l in open(log, encoding="utf-8").read().splitlines() if l.strip()])
        r = subprocess.run(
            [sys.executable, os.path.join(ROOT, "itembank.py"), "mark",
             "--session", session_id, "--item", "not-a-real-item-ref",
             "--verdict", "pass", "--base", tmp],
            cwd=tmp, capture_output=True, text=True)
        if r.returncode == 0:
            fail("marking an item never answered in this session exited 0")
        if "not-a-real-item-ref" not in (r.stdout + r.stderr):
            fail("marking an unresolved item_ref did not name it: %r" %
                 (r.stdout + r.stderr))
        lines_after_bad = len(
            [l for l in open(log, encoding="utf-8").read().splitlines() if l.strip()])
        if lines_after_bad != lines_before_bad:
            fail("marking an unresolved item_ref appended a line to the log")

        # A non-human marker is rejected outright (T-1-24).
        try:
            itembank.mark_event(session_id, "", short_ref, "x", True, marker="model")
            fail("mark_event accepted a non-human marker")
        except ValueError:
            pass
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
    test_objective_query()
    test_index_is_disposable()
    test_renders_match_log()
    test_mark_flow()
    print("evidence contract: ok (tracer end-to-end, mode recorded, empty log, one writer, "
          "identity survives edit, missing/duplicate ids, fingerprint stability, hash "
          "states, lint order, duplicate-submit dedupe, retraction, objective query, "
          "index disposability, renders match log, mark flow)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
