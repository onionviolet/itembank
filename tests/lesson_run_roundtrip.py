#!/usr/bin/env python3
"""Plan 16D-02: the lesson-run session, the additive context label, the
denominator exclusion, and the tier ladder.

One evidence store, one scorer, one session store (D-PACED-2): a checkpoint
attempt inside a paced lesson run is an ordinary attempt with the shape
every attempt has, labelled `context: "lesson_run"`, and the AGENT-03
proposal denominator excludes that label by default as a read-time policy.
The wrong-checkpoint disclosure (D-PACED-3) is released by the runtime in
tiers; exam and diagnostic sittings are refused, and `multi` scoring stays
all-or-nothing at every tier.

Standard library only, runnable as `python tests/lesson_run_roundtrip.py`.
Writes only under a temp dir.
"""
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import blueprint                                        # noqa: E402
import evidence                                         # noqa: E402
import model                                            # noqa: E402
import runtime                                          # noqa: E402
import schema_validate                                  # noqa: E402

FIXTURE = os.path.join(ROOT, "fixtures", "paced_lesson_bank.md")
RESPONSE_SCHEMA = json.load(open(
    os.path.join(ROOT, "schemas", "response.schema.json"), encoding="utf-8"))
RUN_SCHEMA = json.load(open(
    os.path.join(ROOT, "schemas", "lesson_run.schema.json"), encoding="utf-8"))


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def ok(msg):
    print("ok: " + msg)


def load_items():
    qs = model.load(FIXTURE)
    return qs[0], qs[1]


def check_lifecycle():
    work = tempfile.mkdtemp()
    try:
        path = os.path.join(work, "lessonrun_paced.json")
        steps = [s["id"] for s in
                 model.lesson_steps(model.parse_lesson(FIXTURE))]
        data = runtime.start_lesson_run(FIXTURE, path, steps)
        if data.get("error"):
            fail("start_lesson_run refused a valid run: %r" % data)
        if data["kind"] != "lesson_run" or data["step"] != steps[0]:
            fail("a new run must open at the first step of its own kind")
        refused = runtime.lesson_run_advance(path, "never-a-step")
        if refused.get("error") != "lesson_run.unknown_step":
            fail("an unknown step id must be refused by name, got %r"
                 % refused)
        advanced = runtime.lesson_run_advance(path, steps[2])
        if advanced.get("error") or advanced["step"] != steps[2]:
            fail("advancing to a real step failed: %r" % advanced)
        recorded = runtime.lesson_run_record(
            path, "d6ac6b415a7d49a5",
            {"state": "held", "attempt": 1, "tier": 1})
        if recorded.get("error") or len(recorded["attempts"]) != 1:
            fail("recording an attempt summary failed: %r" % recorded)
        on_disk = json.load(open(path, encoding="utf-8"))
        errors = schema_validate.validate(on_disk, RUN_SCHEMA)
        if errors:
            fail("the run file does not validate: %r" % errors)
        empty = runtime.start_lesson_run(FIXTURE,
                                         os.path.join(work, "x.json"), [])
        if empty.get("error") != "lesson_run.no_steps":
            fail("a run with no steps must be refused")
    finally:
        shutil.rmtree(work, ignore_errors=True)
    ok("lifecycle: create, refuse unknown step, advance, record, "
       "schema-valid on disk")


def check_context_label_and_additivity():
    q1, _ = load_items()
    event = evidence.response_event(
        "lr-test-session", q1, "A", False, "paced", 1,
        os.path.basename(FIXTURE), context=evidence.LESSON_RUN_CONTEXT)
    errors = schema_validate.validate(event, RESPONSE_SCHEMA)
    if errors:
        fail("a lesson_run response event does not validate: %r" % errors)
    bogus = dict(event, context="not-a-context")
    if not schema_validate.validate(bogus, RESPONSE_SCHEMA):
        fail("an unknown context value must still fail validation")
    baselines = 0
    for name in ("lesson_retention_events.jsonl", "selection_evidence.jsonl"):
        path = os.path.join(ROOT, "fixtures", name)
        for line in open(path, encoding="utf-8"):
            record = json.loads(line)
            if record.get("event_type") != evidence.RESPONSE_EVENT_TYPE:
                continue
            errors = schema_validate.validate(record, RESPONSE_SCHEMA)
            if errors:
                fail("pre-16D baseline %s no longer validates: %r"
                     % (name, errors))
            baselines += 1
    if not baselines:
        fail("no pre-change response events found; the additivity proof "
             "proved nothing")
    ok("context: lesson_run validates, junk still fails, and %d pre-change "
       "baseline events still validate (additive)" % baselines)


def check_denominator_exclusion():
    q1, _ = load_items()
    window = {"start": "2026-01-01T00:00:00Z", "end": "2027-01-01T00:00:00Z",
              "boundary": "half-open"}
    rows = []
    for n, ctx in enumerate(("quiz", "quiz", "lesson_gate", "lesson_run",
                             "lesson_run")):
        rows.append({"ts": "2026-06-01T00:00:0%dZ" % n,
                     "objective": q1["objective"], "score": True,
                     "context": ctx})
    proposal = blueprint.evidence_proposal(
        q1["objective"], rows, window, ["response"], [],
        ["a small sample can look like a trend"])
    if proposal["denominator"] != 3:
        fail("the denominator must exclude lesson_run rows by default: "
             "got %d, wanted 3" % proposal["denominator"])
    ok("denominator: 5 rows, 2 lesson_run, proposal counts 3")


def check_tier_ladder():
    q1, q2 = load_items()
    t1 = runtime.checkpoint_feedback(q1, "A", 1, False)
    if t1["tier"] != 1:
        fail("first wrong attempt must release tier 1")
    marks = {m["option"]: m["state"] for m in t1["selection_marks"]}
    if marks != {"A": "not_right"}:
        fail("tier 1 must mark only the learner's own selections: %r" % marks)
    if list(t1["touched_da"]) != ["A"]:
        fail("tier 2 must carry DA for touched options only: %r"
             % list(t1["touched_da"]))
    if t1["reveal"] is not None:
        fail("tier 1 must not carry the full reveal")
    blob = json.dumps(t1)
    if "Warm the enclosure" in blob:
        fail("tier 1 leaked the unselected correct option's text")

    t1m = runtime.checkpoint_feedback(q2, ["A", "C"], 1, False)
    marksm = {m["option"]: m["state"] for m in t1m["selection_marks"]}
    if marksm != {"A": "right", "C": "not_right"}:
        fail("tier 1 on multi must mark each touched option: %r" % marksm)
    if t1m["correct"] is not False:
        fail("a partially right multi selection must still score wrong "
             "(all-or-nothing)")

    t3 = runtime.checkpoint_feedback(q1, "A", 2, False)
    if t3["tier"] != 3 or not t3["reveal"]:
        fail("a second wrong attempt must release the full reveal")
    t3r = runtime.checkpoint_feedback(q1, "A", 1, True)
    if t3r["tier"] != 3:
        fail("an explicit learner request must release the full reveal")

    for mode in ("exam", "diagnostic"):
        refused = runtime.checkpoint_feedback(q1, "A", 1, False,
                                              session_mode=mode)
        if refused.get("error") != "checkpoint.assessment_mode":
            fail("%s must be refused by name, got %r" % (mode, refused))

    right = runtime.checkpoint_feedback(q1, "B", 0, False)
    if right["tier"] != 0 or right["correct"] is not True:
        fail("a correct answer discloses nothing beyond its verdict")
    ok("tiers: own picks only at 1, touched DA at 2, full reveal at 3 or on "
       "request, exam and diagnostic refused, multi stays all-or-nothing")


def main():
    check_lifecycle()
    check_context_label_and_additivity()
    check_denominator_exclusion()
    check_tier_ladder()
    print("PASS lesson_run_roundtrip.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
