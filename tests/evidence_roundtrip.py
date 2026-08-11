#!/usr/bin/env python3
"""End-to-end: one submitted response reaches the evidence log and comes back
out of it through a single command, and no second writer can silently appear.

Drives the real CLI via subprocess, the same way a learner or agent does,
rather than calling functions directly, so the test exercises the actual path
from `itembank submit` to `_evidence/evidence.jsonl` to `itembank evidence`.

Standard library only, runnable as `python tests/evidence_roundtrip.py`.
"""
import json, os, re, shutil, subprocess, sys, tempfile, threading, time
import urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import itembank                                            # noqa: E402
import surfaces.day                                        # noqa: E402

BANK = os.path.join(ROOT, "fixtures", "sample_bank.md")
BROKEN_BANK = os.path.join(ROOT, "fixtures", "broken_bank.md")
PLAN = os.path.join(ROOT, "fixtures", "sample_plan.md")
LANES = os.path.join(ROOT, "fixtures", "sample_lanes.md")
LEGACY_ATTEMPTS_DIR = os.path.join(ROOT, "fixtures", "legacy_attempts")
LEGACY_SESSION = os.path.join(ROOT, "fixtures", "legacy_session.json")
LEGACY_DAILY_LOG = os.path.join(ROOT, "fixtures", "legacy_daily_log.md")

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
    # C7 (03.1-03): the served item no longer carries the syllabus
    # objective; the question dict is the authoritative source.
    return q["objective"], submitted, q


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
        if len(lines) != 2:
            fail("expected selection + response lines in evidence.jsonl, found %d"
                 % len(lines))
        parsed = [json.loads(l) for l in lines]
        if not any(e.get("event_type") == "selection"
                   and e.get("selection_spec") is not None for e in parsed):
            fail("start did not record the selection event (D-03)")
        raw = next(e for e in parsed if e.get("event_type") == "response")
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
        # The Phase 7 selector is history-aware, so two sittings over the
        # SAME bank see each other's evidence and no longer pick the same
        # seed-0 item. Use one bank copy per mode so the two sittings are
        # truly independent and the mode field is the only difference.
        bank1 = os.path.join(tmp, "drill_bank.md")
        bank2 = os.path.join(tmp, "exam_bank.md")
        shutil.copyfile(BANK, bank1)
        shutil.copyfile(BANK, bank2)
        objective1, submitted1, q1 = start_and_submit(tmp, bank1, "drill")
        objective2, submitted2, q2 = start_and_submit(tmp, bank2, "exam")
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
    non_bank_errors = [t for t in error_items if t != "BANK"]
    if [item_num(t) for t in non_bank_errors] != \
       sorted(item_num(t) for t in non_bank_errors):
        fail("errors are not in non-decreasing item order: %r" % error_items)
    # Plan 03-03's lesson.duplicate_heading is the first BANK-tagged error
    # (D-06); like the bank-wide warning, it must trail every per-item finding.
    if "BANK" in error_items and error_items[-1] != "BANK":
        fail("the bank-wide entry is not last among errors: %r" % error_items)

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

        started = json.loads(run(["start", bank, "--count", "6", "--seed", "0",
                                  "--mode", "practice"], tmp))
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
                # Phase 6: a wrong practice answer holds the cursor, so
                # re-answer correctly to advance past this item before the
                # loop reads the next one.
                run(["submit", session_file, "--answer", correct_answer(q)], tmp)
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

                reflowed = "  ".join(base.upper().split())   # same words, different case/spacing
                r2 = json.loads(run(["submit", session_file, "--answer", reflowed], tmp))
                if r2["evidence"]["status"] != "already_recorded":
                    fail("a re-cased, re-spaced retry of the same short answer reported %r, "
                         "not already_recorded" % r2["evidence"]["status"])
                if r2["evidence"]["event_id"] != event_id_1:
                    fail("a re-cased, re-spaced retry of the same short answer named a "
                         "different event_id")

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
                # Phase 6: a pending short never advances the cursor, so
                # move past it explicitly (as a human marker would) so the
                # loop can finish the remaining items.
                data = json.load(open(session_file, encoding="utf-8"))
                data["cursor"] = min(data["cursor"] + 1, len(data["items"]))
                with open(session_file, "w", encoding="utf-8") as fh:
                    json.dump(data, fh, ensure_ascii=False, indent=2)
                    fh.write("\n")
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
            ["start", bank, "--objective", objective, "--count", "2", "--seed", "0",
             "--mode", "practice"], tmp))
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
            if q["type"] == "short":
                # Phase 6: a pending short never advances the cursor.
                break
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
        solo_started = json.loads(run(
            ["start", bank, "--count", "1", "--seed", "0", "--mode", "practice"], tmp))
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


def _fixture_evidence_dir(tmp):
    """Copy the phase-7 synthetic evidence fixture into a temp `_evidence/`
    directory and return the log path -- the one shared setup for the
    bank-scoping checks below, which need the fixture's three
    `other_bank.md` events and its one retraction."""
    ev_dir = os.path.join(tmp, "_evidence")
    os.makedirs(ev_dir)
    shutil.copyfile(
        os.path.join(ROOT, "fixtures", "selection_evidence.jsonl"),
        os.path.join(ev_dir, "evidence.jsonl"))
    return os.path.join(ev_dir, "evidence.jsonl")


def test_bank_scoped_query():
    """SEL-03 (D-13): a bank-scoped exposure query returns only that bank's
    responses, the two bank scopes are disjoint and together equal the
    unscoped set, and every returned row carries the requested bank -- the
    scope is real, not a parameter that is accepted and dropped."""
    tmp = tempfile.mkdtemp()
    try:
        log = _fixture_evidence_dir(tmp)
        scoped = itembank.objective_history(log, "", bank="selection_bank.md")
        other = itembank.objective_history(log, "", bank="other_bank.md")
        unscoped = itembank.objective_history(log, "")
        scoped_keys = {json.dumps(r, sort_keys=True) for r in scoped}
        other_keys = {json.dumps(r, sort_keys=True) for r in other}
        if scoped_keys & other_keys:
            fail("bank scopes overlap: %r" % (scoped_keys & other_keys))
        if len(scoped_keys) + len(other_keys) != len(unscoped):
            fail("bank scopes do not partition the unscoped query: "
                 "%d + %d != %d" % (len(scoped_keys), len(other_keys),
                                    len(unscoped)))
        for row in scoped:
            if row.get("bank") != "selection_bank.md":
                fail("scoped row carries bank %r" % row.get("bank"))
        for row in other:
            if row.get("bank") != "other_bank.md":
                fail("other-bank row carries bank %r" % row.get("bank"))
        print("bank scoped query: disjoint, exhaustive, every row banked")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_history_row_width():
    """Every `objective_history()` row names its own `objective` and `bank`
    so a caller can group without re-reading the log, and the objective is
    the recorded one -- never re-derived."""
    tmp = tempfile.mkdtemp()
    try:
        log = _fixture_evidence_dir(tmp)
        rows = itembank.objective_history(log, "")
        if not rows:
            fail("fixture history produced no rows")
        for row in rows:
            if "objective" not in row or "bank" not in row:
                fail("row lacks objective/bank keys: %r" % row)
        recorded = {}
        for ev in itembank.live_events(log):
            if ev.get("event_type") == "response":
                recorded.setdefault(ev["item_ref"], ev.get("objective"))
        for row in rows:
            if row.get("objective") != recorded.get(row.get("item_ref")):
                fail("row objective %r is not the recorded one for %s"
                     % (row.get("objective"), row.get("item_ref")))
        print("history row width: objective/bank on every row, recorded values")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_index_bank_disposable_and_version():
    """The new `bank` column did not turn the cache into a second source of
    truth: deleting the index re-answers identically, and an index whose
    `meta.index_version` is stale (1) is rebuilt rather than queried."""
    tmp = tempfile.mkdtemp()
    try:
        log = _fixture_evidence_dir(tmp)
        index = os.path.join(tmp, "_evidence", "evidence_index.sqlite3")
        first = itembank.objective_history(log, "", bank="selection_bank.md")
        if not os.path.exists(index):
            fail("a bank-scoped query never built the index")
        os.remove(index)
        second = itembank.objective_history(log, "", bank="selection_bank.md")
        if second != first:
            fail("deleting the index changed the bank-scoped answer")
        import sqlite3
        con = sqlite3.connect(index)
        con.execute("UPDATE meta SET value = '1' WHERE key = 'index_version'")
        con.commit()
        con.close()
        third = itembank.objective_history(log, "", bank="selection_bank.md")
        if third != first:
            fail("a stale v1-shaped index answered instead of rebuilding")
        con = sqlite3.connect(index)
        ver = con.execute(
            "SELECT value FROM meta WHERE key = 'index_version'").fetchone()
        con.close()
        if not ver or ver[0] != "3":
            fail("index was not rebuilt at version 3 after the stale check")
        print("index bank disposability: delete rebuilds, stale shape rebuilds")
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
            r = json.loads(run(["submit", session_file, "--answer", answer], tmp))
            # Phase 6: a pending short never advances the cursor; move past
            # it explicitly (as a marker would) so the sitting finishes.
            data = json.load(open(session_file, encoding="utf-8"))
            data["cursor"] = min(data["cursor"] + 1, len(data["items"]))
            with open(session_file, "w", encoding="utf-8") as fh:
                json.dump(data, fh, ensure_ascii=False, indent=2)
                fh.write("\n")
        else:
            auto_refs.append(q["id"])
            answer = correct_answer(q) if i % 2 == 0 else different_answer(q)
            r = json.loads(run(["submit", session_file, "--answer", answer], tmp))
            if r.get("action") == "hold":
                # Phase 6: a wrong practice answer holds the cursor; retry
                # correctly to advance.
                run(["submit", session_file, "--answer", correct_answer(q)], tmp)
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

        session_id, qs, qs_by_id, short_ref, auto_refs = drive_full_session(
            tmp, bank, mode="practice")
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


# ---- serve and day, pinned against the log (01-10) -------------------------
# The last two writers -- `itembank serve`'s attempt file and `itembank day`'s
# daily_log.md -- are proven end to end against the real CLI/loopback path,
# the same way plan 01-09's renders were: checked against the log directly
# (session_events, day_log_from_events), not against themselves.

def serve_correct_answer(q):
    """The response `score_response` marks true, in the raw shape a browser
    POSTs (not the JSON-stringified shape `correct_answer()` above builds
    for a CLI `--answer` string argument) -- `tests/serve_roundtrip.py`'s
    own helper, duplicated here rather than imported because that file has
    no importable surface of its own.
    """
    if q["type"] == "mc":
        return q["correct"][0]
    if q["type"] == "multi":
        return list(q["correct"])
    if q["type"] in ("table", "dnd"):
        return dict((str(i), r["cat"]) for i, r in enumerate(q["rows"]))
    if q["type"] == "build":
        return list(q["steps"])
    return "A constructed response, written out in full sentences."


def start_serve(bank, out, mode):
    """Start `itembank serve` on a background thread and return `(proc,
    quiz_url, session_id)` -- `tests/serve_roundtrip.py`'s loopback-driving
    pattern, extended to also capture the session id this plan's startup
    banner now prints.

    `itembank serve` is now a daemon launch scoped to one bank (plan
    02-02): the printed URL line already carries `/quiz/<stem>`, but the
    banner-scraping regex below only captures the base (host:port/), so
    `quiz_url` is built explicitly from the bank's own stem rather than
    assumed to be the server root.
    """
    proc = subprocess.Popen(
        [sys.executable, "-u", os.path.join(ROOT, "itembank.py"), "serve", bank,
         "--no-open", "--port", "0", "--out", out, "--mode", mode],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    lines = []
    threading.Thread(target=lambda: [lines.append(l) for l in proc.stdout],
                     daemon=True).start()
    base = session_id = None
    for _ in range(60):                       # up to ~6s for the bind and banner
        time.sleep(0.1)
        joined = "".join(lines)
        m = re.search(r"http://127\.0\.0\.1:\d+/", joined)
        sm = re.search(r"(?m)^\s*session\s+(\S+)\s*$", joined)
        if m and sm:
            base, session_id = m.group(0), sm.group(1)
            break
    if not base or not session_id:
        proc.kill()
        fail("serve never printed both a url and a session id. Output was:\n" +
             "".join(lines))
    stem = os.path.splitext(os.path.basename(bank))[0]
    return proc, base + "quiz/%s" % stem, session_id


def served_post_path(quiz_url, page):
    """The legacy bank-scoped answer route (`/quiz/<stem>/answer`) the old
    served script posted to. The new served page is an /api/* client (plan
    04-01), but the legacy route stays compatible, and this Phase 1 test
    still drives it directly to pin the evidence shape.
    """
    return quiz_url.rstrip("/") + "/answer"


def post_answer(answer_url, item_id, response, elapsed_ms=None):
    """POST one answer, mirroring the quiz page's own `{id, response,
    elapsed_ms}` body -- `elapsed_ms` omitted entirely (not sent as null)
    when the caller passes `None`, the same shape an older cached page
    with no `elapsed_ms` field at all would send.
    """
    payload = {"id": item_id, "response": response}
    if elapsed_ms is not None:
        payload["elapsed_ms"] = elapsed_ms
    req = urllib.request.Request(answer_url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=5) as res:
        return json.loads(res.read().decode("utf-8"))


def served_items_from_page(page):
    """The served page's item payload -- empty under serve since plan 04-01,
    which replaced the full item array with bootstrap metadata plus one item
    per /api/start and /api/submit response.
    """
    m = re.search(r"(?m)^const Q = (\[.*\]);$", page)
    return json.loads(m.group(1)) if m else []


def test_serve_writes_events():
    """EVID-03 and EVID-08 on the browser surface: a graded sitting writes
    every answer through evidence.append_event(), records a real mode and
    response_time_ms, its attempt file is byte-identical to
    render_attempt_md()'s own output, and by_mode keeps two sittings'
    scores apart.
    """
    tmp = tempfile.mkdtemp()
    try:
        bank = os.path.join(tmp, "sample_bank.md")
        shutil.copyfile(BANK, bank)
        qs = itembank.load(bank)
        log = itembank.log_path(tmp)
        out = os.path.join(tmp, "attempt.md")

        proc, quiz_url, _banner_session = start_serve(bank, out, "drill")
        try:
            page = urllib.request.urlopen(quiz_url, timeout=5).read().decode("utf-8")
            if served_items_from_page(page):
                fail("served page carries a full item array under serve")
            for item in served_items_from_page(page):
                for leak in ("key", "explain", "correct", "opts", "cats", "da",
                            "why", "model", "rubric"):
                    if leak in item:
                        fail("served item %r carries %r under serve" %
                             (item.get("id"), leak))

            answer_url = served_post_path(quiz_url, page)
            by_id = {q["id"]: q for q in qs}
            # The served session answers its CURRENT item (cursor order),
            # not a client-chosen id. Replicate the serve session's own
            # selection (count 6, seed 0, practice composition) to learn the
            # order, then answer the first two items in that order.
            answered = []
            probe = json.loads(run(
                ["start", bank, "--count", "6", "--seed", "0",
                 "--mode", "drill", "--out", os.path.join(tmp, "probe.json")], tmp))
            current = by_id[probe["item"]["id"]]
            r1 = post_answer(answer_url, current["id"],
                             serve_correct_answer(current), elapsed_ms=1234)
            # The legacy answer route uses the lazily-created JSON session
            # (Phase 6), whose id is stamped on the responses -- not the
            # banner session id, which belongs to the pre-Phase-6 path.
            session_id = (r1.get("next") or {}).get("session_id")
            answered.append((r1.get("item_id"), r1.get("evidence", {}).get("status")))
            if r1.get("action") != "advance" or not r1.get("explain"):
                fail("drill-mode submit must advance with explanation: %r" % r1)
            nxt = (r1.get("next") or {}).get("item") or {}
            second = by_id.get(nxt.get("id"))
            if second is None:
                fail("drill submit returned no next item: %r" % r1)
            r2 = post_answer(answer_url, second["id"],
                             serve_correct_answer(second))
            answered.append((r2.get("item_id"), r2.get("evidence", {}).get("status")))
            if not r2.get("explain"):
                fail("second answer (no elapsed_ms) carried no explanation")
            # The cursor now sits on a third item; re-post the previous one
            # to prove the client cannot jump items (it answers the current
            # item instead and records a fresh response).
            r3 = post_answer(answer_url, second["id"], serve_correct_answer(second),
                             elapsed_ms=1234)
            answered.append((r3.get("item_id"), r3.get("evidence", {}).get("status")))
            if not r3.get("explain"):
                fail("repeat answer carried no explanation")
        finally:
            proc.terminate()

        lines = [l for l in open(log, encoding="utf-8").read().splitlines() if l.strip()]
        response_lines = [l for l in lines if json.loads(l)["event_type"] == "response"]
        if len(response_lines) != 3:
            fail("expected 3 response lines (3 genuine submits), found %d"
                 % len(response_lines))
        events_by_ref = {}
        for l in response_lines:
            ev = json.loads(l)
            events_by_ref[ev["item_ref"]] = ev
        if any(ev["mode"] != "drill" for ev in events_by_ref.values()):
            fail("not every event recorded mode 'drill': %r" %
                 [ev["mode"] for ev in events_by_ref.values()])
        first_ref = answered[0][0]
        if first_ref not in events_by_ref:
            fail("the first answered item never appeared in the log")
        if events_by_ref[first_ref]["response_time_ms"] != 1234:
            fail("first answer's response_time_ms is %r, not 1234" %
                 events_by_ref[first_ref]["response_time_ms"])

        rendered = itembank.render_attempt_md(log, session_id, qs, bank)
        on_disk = open(out, encoding="utf-8").read()
        if on_disk != rendered:
            fail("the attempt file on disk is not byte-identical to "
                 "render_attempt_md()'s output for this session")

        # A second sitting, a different mode, the same item: by_mode keeps
        # the two scores in separate buckets (EVID-08, proven from the
        # browser surface).
        out2 = os.path.join(tmp, "attempt2.md")
        proc2, quiz_url2, _ = start_serve(bank, out2, "exam")
        try:
            page2 = urllib.request.urlopen(quiz_url2, timeout=5).read().decode("utf-8")
            answer_url2 = served_post_path(quiz_url2, page2)
            r4 = post_answer(answer_url2, by_id["q1"]["id"],
                             serve_correct_answer(by_id["q1"]),
                             elapsed_ms=999)
            if r4.get("action") != "defer_feedback":
                fail("exam-mode answer must defer feedback: %r" % r4)
            if "explain" in r4 or "score" in r4:
                fail("exam-mode answer leaked feedback: %r" % r4)
        finally:
            proc2.terminate()

        objective = current.get("objective") or ""
        result = parse_json_tail(run(["evidence", "--objective", objective,
                                      "--base", tmp], tmp))
        by_mode = result["by_mode"]
        if not {"drill", "exam"} <= set(by_mode):
            fail("expected both a drill and an exam by_mode bucket, got %r" %
                 set(by_mode))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_day_ticks_are_events():
    """EVID-03 on the day surface: a tick is an event, un-ticking is a
    retraction, daily_log.md is a byte-faithful render of write_day_log()'s
    own shape for the same tick set, and the file can be deleted and
    regenerated with no loss.
    """
    tmp = tempfile.mkdtemp()
    try:
        plan = os.path.join(tmp, "sample_plan.md")
        lanes = os.path.join(tmp, "sample_lanes.md")
        shutil.copyfile(PLAN, plan)
        shutil.copyfile(LANES, lanes)
        log_path = os.path.join(tmp, "daily_log.md")
        evidence_log = itembank.log_path(tmp)

        proc = subprocess.Popen(
            [sys.executable, "-u", os.path.join(ROOT, "itembank.py"), "day", plan,
             "--no-open", "--port", "0", "--log", log_path, "--lanes", lanes,
             "--date", "2026-01-06"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        lines = []
        threading.Thread(target=lambda: [lines.append(l) for l in proc.stdout],
                         daemon=True).start()
        # `itembank day` is now a daemon launch scoped to one plan (plan
        # 02-02): the printed URL already names `/day/<stem>`, but this
        # regex only captures the base, so the save target is built
        # explicitly from the plan's own stem (`/day/<stem>/save`) rather
        # than the bare `/save` a single-plan process used to hardcode.
        stem = os.path.splitext(os.path.basename(plan))[0]
        base = None
        for _ in range(60):
            time.sleep(0.1)
            m = re.search(r"http://127\.0\.0\.1:\d+/", "".join(lines))
            if m:
                base = m.group(0)
                break
        if not base:
            proc.kill()
            fail("day server never printed a URL. Output was:\n" + "".join(lines))
        day_url = base + "day/%s" % stem

        def save(done):
            body = json.dumps({"date": "2026-01-06", "done": done}).encode("utf-8")
            req = urllib.request.Request(day_url + "/save", data=body,
                                         headers={"Content-Type": "application/json"})
            return json.loads(urllib.request.urlopen(req, timeout=5).read().decode("utf-8"))

        try:
            r1 = save(["Anki", "EMT"])
            if r1.get("status") not in ("floor", "miss", "full"):
                fail("day POST route did not return a recognizable status: %r" % r1)

            events_after_tick = [
                json.loads(l) for l in
                open(evidence_log, encoding="utf-8").read().splitlines() if l.strip()]
            ticks = [e for e in events_after_tick if e["event_type"] == "day_tick"]
            if len(ticks) != 2:
                fail("expected 2 day_tick events after ticking two lanes, got %d" %
                     len(ticks))

            written = itembank.load_day_log(log_path)
            if written.get("2026-01-06") != {"Anki", "EMT"}:
                fail("regenerated daily_log.md does not mark both ticked lanes: %r" %
                     written.get("2026-01-06"))

            # Ticking the same two lanes again appends nothing.
            save(["Anki", "EMT"])
            events_after_repeat = [
                json.loads(l) for l in
                open(evidence_log, encoding="utf-8").read().splitlines() if l.strip()]
            ticks_after_repeat = [e for e in events_after_repeat
                                  if e["event_type"] == "day_tick"]
            if len(ticks_after_repeat) != 2:
                fail("re-ticking the same two lanes appended a new day_tick event: "
                     "%d -> %d" % (len(ticks), len(ticks_after_repeat)))

            # Un-ticking one lane appends a retraction, not a deletion --
            # the log grows by one line.
            save(["EMT"])
            events_after_untick = [
                json.loads(l) for l in
                open(evidence_log, encoding="utf-8").read().splitlines() if l.strip()]
            if len(events_after_untick) != len(events_after_repeat) + 1:
                fail("un-ticking a lane did not append exactly one line: %d -> %d" %
                     (len(events_after_repeat), len(events_after_untick)))
            retractions = [e for e in events_after_untick
                          if e["event_type"] == "retraction"]
            if len(retractions) != 1:
                fail("un-ticking a lane did not append exactly one retraction event, "
                     "found %d" % len(retractions))

            written2 = itembank.load_day_log(log_path)
            if written2.get("2026-01-06") != {"EMT"}:
                fail("regenerated daily_log.md still shows the un-ticked lane: %r" %
                     written2.get("2026-01-06"))
            remaining = itembank.day_log_from_events(evidence_log)
            if remaining.get("2026-01-06") != {"EMT"}:
                fail("day_log_from_events still reports the un-ticked lane as done: %r" %
                     remaining.get("2026-01-06"))
        finally:
            proc.kill()

        # The render is a faithful replacement for write_day_log's own
        # output over the same tick set.
        via_render = itembank.render_daily_log(
            remaining, itembank.DAY_LANES, itembank.FLOOR_LANES, itembank.day_status)
        legacy_out = os.path.join(tmp, "legacy_daily_log.md")
        itembank.write_day_log(legacy_out, remaining)
        legacy_text = open(legacy_out, encoding="utf-8").read()
        if via_render != legacy_text:
            fail("render_daily_log()'s output is not byte-identical to "
                 "write_day_log()'s output for the same tick set")

        # The file is an output: deleting it and re-rendering restores it.
        os.remove(log_path)
        via_render2 = itembank.render_daily_log(
            remaining, itembank.DAY_LANES, itembank.FLOOR_LANES, itembank.day_status)
        if via_render2 != via_render:
            fail("re-rendering after deleting daily_log.md changed the output")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---- migration (01-11): D-13's re-runnability, D-14's unresolved rule, and --
# the phase's second success criterion -- pre/post counts reconcile exactly --
# proven against a total this test computes independently of
# surfaces/migrate.py, per its own read_first instruction that a
# reconciliation test asking the tool to check its own arithmetic proves
# nothing.

def _lay_out_legacy_tree(base):
    """The layout a real machine has: the bank at `base`, attempt markdown
    and session JSON under `base/_attempts/`, the day log beside the bank.
    """
    shutil.copyfile(BANK, os.path.join(base, "sample_bank.md"))
    attempts_dir = os.path.join(base, "_attempts")
    os.makedirs(attempts_dir, exist_ok=True)
    for f in sorted(os.listdir(LEGACY_ATTEMPTS_DIR)):
        shutil.copyfile(os.path.join(LEGACY_ATTEMPTS_DIR, f),
                        os.path.join(attempts_dir, f))
    shutil.copyfile(LEGACY_SESSION, os.path.join(attempts_dir, "legacy_session.json"))
    shutil.copyfile(LEGACY_DAILY_LOG, os.path.join(base, "daily_log.md"))


def _independent_legacy_count(base):
    """Count the source records directly -- a simple `## Item ` count per
    attempt file, `len(responses)` from the session JSON, and
    `surfaces.day.load_day_log`'s own tick mapping -- never by calling
    `surfaces.migrate.scan_legacy` or anything else under test.
    """
    attempts_dir = os.path.join(base, "_attempts")
    attempt_total = 0
    session_total = 0
    for f in sorted(os.listdir(attempts_dir)):
        full = os.path.join(attempts_dir, f)
        if f.endswith(".md"):
            text = open(full, encoding="utf-8").read()
            attempt_total += len(re.findall(r"(?m)^## Item ", text))
        elif f.endswith(".json"):
            data = json.load(open(full, encoding="utf-8"))
            session_total += len(data.get("responses") or [])
    tick_log = surfaces.day.load_day_log(os.path.join(base, "daily_log.md"))
    tick_total = sum(len(v) for v in tick_log.values())
    return attempt_total, session_total, tick_total


def _fingerprint_legacy_files(base):
    """A byte fingerprint of every legacy source file under `base`, so a
    caller can assert migration reads them and never writes to them.
    """
    out = {}
    attempts_dir = os.path.join(base, "_attempts")
    for f in sorted(os.listdir(attempts_dir)):
        p = os.path.join(attempts_dir, f)
        out[p] = open(p, "rb").read()
    daily = os.path.join(base, "daily_log.md")
    out[daily] = open(daily, "rb").read()
    return out


def migrate_json(args_after_command, cwd):
    """Run `migrate` and parse its trailing JSON reconciliation object,
    which follows two human-readable `found:`/`wrote:` (or `would write:`)
    status lines in the house `"%d ..., %d ..."` style.
    """
    return parse_json_tail(run(["migrate"] + list(args_after_command), cwd))


def test_migration_reconciliation():
    """EVID-06 and both of its probe edges (idempotency, concurrency),
    plus D-14's unresolved rule -- the phase's second success criterion,
    proven against fixtures/legacy_attempts, fixtures/legacy_session.json
    and fixtures/legacy_daily_log.md, laid out under a temp directory the
    way a real machine has them.
    """
    tmp = tempfile.mkdtemp()
    try:
        _lay_out_legacy_tree(tmp)
        expected_attempt, expected_session, expected_tick = _independent_legacy_count(tmp)
        expected_total = expected_attempt + expected_session + expected_tick
        if expected_total < 15:
            fail("test setup: expected the legacy fixtures to carry more than "
                 "%d records (attempt=%d session=%d tick=%d)" %
                 (expected_total, expected_attempt, expected_session, expected_tick))
        before_files = _fingerprint_legacy_files(tmp)
        log = itembank.log_path(tmp)

        # Dry run: nothing appended, and its found total matches the
        # independently computed one.
        dry = migrate_json(["--base", tmp], tmp)
        if dry["dry_run"] is not True:
            fail("a migrate run with no --write reported dry_run %r, not True" %
                 dry["dry_run"])
        if os.path.exists(log):
            fail("a dry run created or appended to the evidence log")
        found_total = sum(dry["found"].values())
        if found_total != expected_total:
            fail("dry run found %d records, independently counted %d: %r" %
                 (found_total, expected_total, dry["found"]))

        # Real run: written + already_present accounts for the whole found
        # total, and the log's own line count for response/day_tick events
        # matches what was reported written.
        real = migrate_json(["--base", tmp, "--write"], tmp)
        if real["dry_run"] is not False:
            fail("a --write migrate run reported dry_run %r, not False" % real["dry_run"])
        w = real["written"]
        accounted = w["resolved"] + w["unresolved"] + w["unparsed"] + w["ticks"] + w["already_present"]
        if accounted != found_total:
            fail("real run found %d but accounted for %d: %r" %
                 (found_total, accounted, w))
        if w["already_present"] != 0:
            fail("the first --write run against a fresh log reported "
                 "already_present %d, not 0" % w["already_present"])
        if w["resolved"] + w["unresolved"] + w["ticks"] == 0:
            fail("a --write run against a fresh log wrote nothing at all")

        live_events = [json.loads(l) for l in
                       open(log, encoding="utf-8").read().splitlines() if l.strip()]
        live_response_or_tick = [e for e in live_events
                                 if e["event_type"] in ("response", "day_tick")]
        if len(live_response_or_tick) != w["resolved"] + w["unresolved"] + w["ticks"]:
            fail("the log's response/day_tick line count %d does not match what "
                 "the real run reported writing (%d resolved+unresolved, %d ticks)" %
                 (len(live_response_or_tick), w["resolved"] + w["unresolved"], w["ticks"]))

        # Idempotency edge: running --write again imports zero new events;
        # already_present covers the whole found total, and the log's line
        # count is unchanged.
        again = migrate_json(["--base", tmp, "--write"], tmp)
        aw = again["written"]
        # A record that never parses (the deliberately corrupted fixture
        # section) never reaches append_event at all, so it is never
        # "already present" -- it lands in `unparsed` again, every run.
        # The full found total is therefore accounted for by
        # already_present plus that same unparsed count, not by
        # already_present alone.
        if aw["already_present"] != found_total - aw["unparsed"]:
            fail("a second --write run reported already_present %d and "
                 "unparsed %d, which do not sum to the full found total %d: %r" %
                 (aw["already_present"], aw["unparsed"], found_total, aw))
        if aw["resolved"] != 0 or aw["unresolved"] != 0 or aw["ticks"] != 0:
            fail("a second --write run reported new resolved/unresolved/tick "
                 "records: %r" % aw)
        lines_after_second = [l for l in
                              open(log, encoding="utf-8").read().splitlines() if l.strip()]
        if len(lines_after_second) != len(live_events):
            fail("a second --write run changed the log's line count: %d -> %d" %
                 (len(live_events), len(lines_after_second)))

        # Unresolved rule (D-14): every imported response under the q9
        # reference is present, not dropped, carries item_id "", and names
        # its resolution as unresolved.
        q9_events = [e for e in live_events
                    if e.get("event_type") == "response" and e.get("item_ref") == "q9"]
        if not q9_events:
            fail("no imported response carries item_ref 'q9' -- the "
                 "unresolvable fixture record was dropped rather than imported")
        for e in q9_events:
            if e["item_id"] != "":
                fail("a q9 response carries item_id %r, not empty" % e["item_id"])
            source_ref = e.get("source_ref") or {}
            if source_ref.get("resolution") != "unresolved":
                fail("a q9 response's source_ref does not report 'unresolved': %r" %
                     source_ref)

        after_files = _fingerprint_legacy_files(tmp)
        if after_files != before_files:
            fail("one or more legacy source files changed after migration runs "
                 "against %s -- migration must read them and never write to them" % tmp)

        # Concurrency edge: kill the migration partway through on a fresh
        # copy of the same tree, then resume it to completion. The final
        # event count must equal the uninterrupted run's, and at most one
        # malformed line may result from the kill.
        tmp2 = tempfile.mkdtemp()
        try:
            _lay_out_legacy_tree(tmp2)
            log2 = itembank.log_path(tmp2)
            proc = subprocess.Popen(
                [sys.executable, os.path.join(ROOT, "itembank.py"), "migrate",
                 "--base", tmp2, "--write"],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            time.sleep(0.05)
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)

            run(["migrate", "--base", tmp2, "--write"], tmp2)
            final = migrate_json(["--base", tmp2, "--write"], tmp2)
            fw = final["written"]
            if fw["already_present"] != expected_total - fw["unparsed"]:
                fail("after an interrupted-then-resumed migration, a final "
                     "confirming run reported already_present %d and unparsed "
                     "%d, which do not sum to the expected total %d: %r" %
                     (fw["already_present"], fw["unparsed"], expected_total, fw))
            if fw["resolved"] != 0 or fw["unresolved"] != 0 or fw["ticks"] != 0:
                fail("after an interrupted-then-resumed migration, a final "
                     "confirming run still reported new records: %r" % fw)

            bad = 0
            if os.path.exists(log2):
                for line in open(log2, encoding="utf-8").read().splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        json.loads(line)
                    except ValueError:
                        bad += 1
            if bad > 1:
                fail("an interrupted-then-resumed migration left %d malformed "
                     "lines in the log, expected at most 1" % bad)
        finally:
            shutil.rmtree(tmp2, ignore_errors=True)

        # Opt-in resolution: a fresh copy migrated with
        # --resolve-by-position resolves q1..q6 to the bank's [ID:] values
        # and records source_ref.resolution 'position', while q9 stays
        # unresolved and still counted.
        tmp3 = tempfile.mkdtemp()
        try:
            _lay_out_legacy_tree(tmp3)
            bank3 = os.path.join(tmp3, "sample_bank.md")
            qs_by_ref = {q["id"]: q for q in itembank.load(bank3)}
            run(["migrate", "--base", tmp3, "--write",
                 "--resolve-by-position", bank3], tmp3)
            log3 = itembank.log_path(tmp3)
            events3 = [json.loads(l) for l in
                      open(log3, encoding="utf-8").read().splitlines() if l.strip()]
            resolved_seen = False
            for e in events3:
                if e.get("event_type") != "response":
                    continue
                ref = e.get("item_ref")
                if ref == "q9":
                    if e["item_id"] != "" or e["source_ref"]["resolution"] != "unresolved":
                        fail("q9 resolved under --resolve-by-position, which D-14 "
                             "forbids: %r" % e)
                    continue
                q = qs_by_ref.get(ref)
                if q and q.get("item_id") and e["item_id"] == q["item_id"]:
                    if e["source_ref"]["resolution"] != "position":
                        fail("a resolved event %r did not record "
                             "source_ref.resolution 'position'" % e)
                    resolved_seen = True
            if not resolved_seen:
                fail("--resolve-by-position resolved nothing at all")
        finally:
            shutil.rmtree(tmp3, ignore_errors=True)

        # Scope rule (T-1-03): --legacy-dir pointed outside --base exits
        # non-zero and appends nothing.
        tmp4 = tempfile.mkdtemp()
        outside = tempfile.mkdtemp()
        try:
            _lay_out_legacy_tree(tmp4)
            log4 = itembank.log_path(tmp4)
            r = subprocess.run(
                [sys.executable, os.path.join(ROOT, "itembank.py"), "migrate",
                 "--base", tmp4, "--legacy-dir", outside, "--write"],
                cwd=tmp4, capture_output=True, text=True)
            if r.returncode == 0:
                fail("migrate --legacy-dir pointed outside --base exited 0")
            if os.path.exists(log4):
                fail("migrate --legacy-dir pointed outside --base appended to "
                     "the evidence log")
        finally:
            shutil.rmtree(tmp4, ignore_errors=True)
            shutil.rmtree(outside, ignore_errors=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---- plan 03.1-02: term_lookup events (D-19) -------------------------------

def test_term_lookup_event():
    """term_lookup is a first-class, additive event type: the builder mirrors
    the response-event envelope with every key present, carries no score key,
    appends through the one writer, dedupes on replay, and reads back through
    both the raw and live readers (D-19)."""
    tmp = tempfile.mkdtemp()
    try:
        log = itembank.log_path(tmp)
        ev = itembank.term_lookup_event(
            session_id="sess-1", bank="lesson_bank.md", term_slug="airway",
            mode="practice", source="reader")
        for key in ("schema_version", "event_id", "event_type", "ts",
                    "session_id", "bank", "term_slug", "source", "mode",
                    "actor", "dedupe_key"):
            if key not in ev:
                fail("term_lookup event missing key %r: %r" % (key, ev))
        if ev["event_type"] != "term_lookup":
            fail("event_type wrong: %r" % ev["event_type"])
        if ev["source"] not in ("reader", "session"):
            fail("source must be reader or session, got %r" % ev["source"])
        if ev["actor"] != "learner":
            fail("default actor must be 'learner', got %r" % ev["actor"])
        if "score" in ev:
            fail("a term_lookup event must carry no score key (D-19): %r" % ev)

        res = itembank.append_event(log, ev)
        if res["status"] != "recorded":
            fail("first append must record, got %r" % res)
        replay = itembank.append_event(log, ev)
        if replay["status"] != "already_recorded":
            fail("replaying the same lookup must dedupe, got %r" % replay)

        read_back = list(itembank.events(log))
        if len(read_back) != 1 or read_back[0]["term_slug"] != "airway":
            fail("events() must yield the term_lookup event: %r" % read_back)
        live = list(itembank.live_events(log))
        if len(live) != 1 or live[0]["event_type"] != "term_lookup":
            fail("live_events() must yield the term_lookup event: %r" % live)

        # A reader that predates the type must degrade, not crash: a raw line
        # carrying an event type outside KNOWN_EVENT_TYPES is skipped (D-09).
        raw_unknown = os.path.join(tmp, "unknown.jsonl")
        open(raw_unknown, "w", encoding="utf-8").write(
            json.dumps({"schema_version": 1, "event_id": "x",
                        "event_type": "future_event",
                        "ts": "2026-01-01T00:00:00.000Z"}) + "\n")
        if list(itembank.events(raw_unknown)) != []:
            fail("a reader predating a type must skip it with a warning")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_term_lookup_registered_in_schema():
    """The new type is registered in KNOWN_EVENT_TYPES and in the schema's
    event_type enum plus a $defs shape -- never in the top-level required
    list, matching the mark/retraction/day_tick precedent."""
    if "term_lookup" not in itembank.KNOWN_EVENT_TYPES:
        fail("term_lookup must be a member of KNOWN_EVENT_TYPES")
    schema = json.load(open(os.path.join(ROOT, "schemas", "response.schema.json"),
                            encoding="utf-8"))
    # Phase 6 moved the response shape into $defs.response_event (a const
    # discriminator) so the top-level document can also describe the hint
    # event via oneOf; the other event types ride the catch-all branch.
    if schema["$defs"]["response_event"]["properties"]["event_type"].get("const") != "response":
        fail("response_event branch must discriminate on event_type const")
    if "term_lookup" not in schema["$defs"]:
        fail("response.schema.json must carry a $defs.term_lookup shape")
    if "term_lookup" not in schema["$defs"]["other_event"]["properties"]["event_type"]["enum"]:
        fail("the catch-all branch must accept term_lookup")
    if "hint_event" not in schema["$defs"]:
        fail("response.schema.json must carry a $defs.hint_event shape")
    if schema["$defs"]["hint_event"]["properties"]["event_type"].get("const") != "hint":
        fail("hint_event branch must discriminate on event_type const")


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
    test_bank_scoped_query()
    test_history_row_width()
    test_index_bank_disposable_and_version()
    test_renders_match_log()
    test_mark_flow()
    test_serve_writes_events()
    test_day_ticks_are_events()
    test_migration_reconciliation()
    test_term_lookup_event()
    test_term_lookup_registered_in_schema()
    print("evidence contract: ok (tracer end-to-end, mode recorded, empty log, one writer, "
          "identity survives edit, missing/duplicate ids, fingerprint stability, hash "
          "states, lint order, duplicate-submit dedupe, retraction, objective query, "
          "index disposability, bank scoping, row width, index bank version, renders match log, mark flow, serve writes events, "
          "day ticks are events, migration reconciliation, term_lookup)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
