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


def main():
    test_tracer_end_to_end()
    test_mode_recorded()
    test_empty_log()
    test_one_writer()
    print("evidence contract: ok (tracer end-to-end, mode recorded, empty log, one writer)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
