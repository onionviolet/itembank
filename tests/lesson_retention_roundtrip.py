#!/usr/bin/env python3
"""Plan 10-02 fixed-clock harness: an explicit Phase 3 lesson completion is
one append-only event, and the retention snapshot deterministically derives
the objective review-queue entry from it (SCHED-04, D-01, D-02, D-04, D-13,
D-16, D-24).

What matters here, and why each case is tested rather than trusted:

1. D-24/D-04: `itembank lesson BANK --ref HEADING --complete` resolves the
   heading through the ONE Phase 3 slugifier, discovers the sorted unique
   objectives of items referencing it, appends exactly one `lesson_complete`
   event through the ONE writer, and prints the queue date/interval/reason/
   snapshot from a fresh retention capture -- never a second parser, slugger,
   queue store, or writer.
2. D-02: retrying the identical completion is idempotent (`already_recorded`,
   still one event); a compensating retraction removes the queue row from a
   fresh snapshot without deleting the event; re-completing after retraction
   records again.
3. D-04: rendering the lesson (CLI or `lesson_page`/`GET /lesson/<stem>`)
   writes nothing; a heading with no referenced objective is refused with a
   named explanation; `--complete` without `--ref` is refused.
4. D-01/D-13: the queue row carries the event's full evidence claim --
   event_id, completed local day, exact next-review date (event local date +
   bounded `lesson_review_after_days`), configured interval, reason
   "lesson review", and the snapshot id.
5. D-09/D-16: only captured live `lesson_complete` events feed the queue; a
   response, a term lookup, and a model-shaped event never create a row.
6. Structural writer boundary: the lesson render/GET call graph cannot reach
   `append_event`; the explicit completion branch reaches exactly the one
   writer.

Standard library only, runnable as `python tests/lesson_retention_roundtrip.py`.
"""
import datetime
import inspect
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import evidence
import retention

LES_BANK = os.path.join(ROOT, "fixtures", "lesson_bank.md")


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def run(args, cwd):
    """Drive the real CLI via subprocess, the same way a learner or agent
    does."""
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, os.path.join(ROOT, "itembank.py")] + list(args),
                       cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                       env=env, timeout=60)
    return r


def fresh_log():
    """A temp dir holding an empty _evidence/evidence.jsonl, returned as the
    base and the evidence log path."""
    tmp = tempfile.mkdtemp()
    log = evidence.log_path(tmp)
    os.makedirs(os.path.dirname(log), exist_ok=True)
    return tmp, log


def snapshot_queue(base, cutoff="2026-08-20T12:00:00.000Z", zone="UTC", cfg=None):
    """Capture once and derive the lesson review queue from that snapshot."""
    events = evidence.capture_events(evidence.log_path(base))
    snapshot = retention.capture(events, cutoff=cutoff, zone=zone, cfg=cfg)
    return snapshot, retention.lesson_queue(snapshot)


def completion_events(log):
    return [ev for ev in evidence.events(log)
            if ev.get("event_type") == evidence.LESSON_COMPLETE_EVENT_TYPE]


def lesson_event(session_id="reader", bank="lesson_bank.md", slug="the-airway-step-by-step",
                 subject="emt", objectives=("emt:airway",), zone="UTC",
                 ts="2026-08-10T12:00:00.000Z"):
    ev = evidence.lesson_complete_event(
        session_id=session_id, bank=bank, lesson_slug=slug, subject=subject,
        objectives=list(objectives), zone=zone, ts=ts)
    return ev


def no_reference_bank_text():
    """A bank whose lone lesson heading is referenced by no item, so a
    completion of it must be refused (D-04)."""
    return (
        "# No-reference bank (synthetic)\n\n"
        "## LESSON\n\n"
        "### Lone Heading\n\n"
        "Teaching prose that no question references.\n\n"
        "Q1. Which one is correct?   (difficulty: recall)\n"
        "[OBJECTIVE: emt:airway]\n\n"
        "A) One\nB) Two\nC) Three\nD) Four\n\n"
        "CORRECT: A\n\n"
        "WHY BEST: One is correct.\n\n"
        "KEY DISCRIMINATOR: Correct versus not.\n\n"
        "SECOND-BEST: B. Two would be correct if the question asked for two.\n\n"
        "DISTRACTOR ANALYSIS:\n"
        "- A) Correct: one.\n"
        "- B) Two; this would be correct if the question asked for two.\n"
        "- C) Three; this would be correct if the question asked for three.\n"
        "- D) Four; this would be correct if the question asked for four.\n\n"
        "TRAP: Overthinking.\n\n"
        "CONFIDENCE: high\n")


# ---- builder validation (D-04/T-10-06/T-10-07) -----------------------------

def check_builder_validation():
    # Empty Phase 3 lesson slug is refused.
    for kw in ({"slug": ""}, {"slug": None}):
        try:
            evidence.lesson_complete_event("reader", "b.md", kw["slug"],
                                           "emt", ["emt:airway"])
            fail("builder accepted an empty lesson slug")
        except ValueError:
            pass
    # Unnamespaced objectives / empty subject are refused.
    try:
        evidence.lesson_complete_event("reader", "b.md", "s", "", ["airway"])
        fail("builder accepted an unnamespaced objective")
    except ValueError:
        pass
    # Empty objective list is refused.
    try:
        evidence.lesson_complete_event("reader", "b.md", "s", "emt", [])
        fail("builder accepted an empty objective list")
    except ValueError:
        pass
    # A client-derived path as bank is refused (T-10-07): basename only.
    try:
        evidence.lesson_complete_event("reader", "/abs/path/b.md", "s", "emt",
                                       ["emt:airway"])
        fail("builder accepted a path as bank")
    except ValueError:
        pass
    # Sorted-unique objectives are canonicalized, never trusted to the caller.
    ev = evidence.lesson_complete_event("reader", "b.md", "s", "emt",
                                        ["emt:b", "emt:a", "emt:b"])
    if ev["objectives"] != ["emt:a", "emt:b"]:
        fail("objectives were not sorted and deduped: %r" % ev["objectives"])
    # Same completion identity -> same dedupe key (idempotency).
    a = lesson_event()
    b = lesson_event()
    if a["dedupe_key"] != b["dedupe_key"] or a["event_id"] == b["event_id"]:
        fail("deterministic dedupe identity not reproduced")


# ---- D-24/D-04: explicit completion through the real CLI -------------------

def check_cli_explicit_completion():
    tmp = tempfile.mkdtemp()
    try:
        bank = os.path.join(tmp, "lesson_bank.md")
        shutil.copyfile(LES_BANK, bank)
        r = run(["lesson", bank, "--ref", "The Airway, Step By Step",
                 "--complete", "--zone", "UTC"], tmp)
        if r.returncode != 0:
            fail("lesson --complete exited %d: %s" % (r.returncode, r.stderr))
        out = r.stdout
        for needle in ("recorded", "lesson review", "snapshot:", "14 day",
                       "emt:airway", "next review"):
            if needle not in out:
                fail("completion output missing %r:\n%s" % (needle, out))
        log = evidence.log_path(tmp)
        events = completion_events(log)
        if len(events) != 1:
            fail("exactly one completion event expected, got %d" % len(events))
        ev = events[0]
        for field in ("schema_version", "event_id", "event_type", "ts",
                      "session_id", "bank", "lesson_slug", "subject",
                      "objectives", "zone", "actor", "dedupe_key"):
            if field not in ev:
                fail("completion event missing %r" % field)
        if ev["lesson_slug"] != "the-airway-step-by-step":
            fail("event must name the Phase 3 slug, got %r" % ev["lesson_slug"])
        if ev["subject"] != "emt":
            fail("event subject is %r, not emt" % ev["subject"])
        if ev["objectives"] != ["emt:airway"]:
            fail("event objectives are %r, not the sorted unique set"
                 % ev["objectives"])
        if ev["bank"] != "lesson_bank.md":
            fail("event bank must be the basename, got %r" % ev["bank"])
        if ev["session_id"] != "reader":
            fail("reader session id expected, got %r" % ev["session_id"])
        # The queue row derives from the snapshot: interval 14, exact
        # next-review date from the event's own ts, reason, snapshot id.
        _snapshot, rows = snapshot_queue(tmp)
        if len(rows) != 1:
            fail("one queue row expected, got %r" % rows)
        row = rows[0]
        due = (datetime.datetime.strptime(ev["ts"], "%Y-%m-%dT%H:%M:%S.%fZ")
               .replace(tzinfo=datetime.timezone.utc).date()
               + datetime.timedelta(days=14)).isoformat()
        for field, value in (("objective", "emt:airway"),
                             ("lesson_slug", "the-airway-step-by-step"),
                             ("bank", "lesson_bank.md"),
                             ("event_id", ev["event_id"]),
                             ("interval_days", 14),
                             ("reason", "lesson review"),
                             ("next_review_date", due)):
            if row.get(field) != value:
                fail("queue row %r is %r, expected %r"
                     % (field, row.get(field), value))
        if row["snapshot_id"] != _snapshot["claim"]["snapshot_id"]:
            fail("queue row must carry the snapshot's provenance id")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_idempotent_retry():
    tmp = tempfile.mkdtemp()
    try:
        bank = os.path.join(tmp, "lesson_bank.md")
        shutil.copyfile(LES_BANK, bank)
        r1 = run(["lesson", bank, "--ref", "The Airway, Step By Step",
                  "--complete", "--zone", "UTC"], tmp)
        r2 = run(["lesson", bank, "--ref", "The Airway, Step By Step",
                  "--complete", "--zone", "UTC"], tmp)
        if r2.returncode != 0 or "already_recorded" not in r2.stdout:
            fail("retry must report already_recorded: %r" % r2.stdout)
        log = evidence.log_path(tmp)
        if len(completion_events(log)) != 1:
            fail("a retried completion must not append a second event")
        _snapshot, rows = snapshot_queue(tmp)
        if len(rows) != 1:
            fail("a retried completion must not double the queue")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_retraction_removes_entry_and_recompletes():
    tmp = tempfile.mkdtemp()
    try:
        bank = os.path.join(tmp, "lesson_bank.md")
        shutil.copyfile(LES_BANK, bank)
        run(["lesson", bank, "--ref", "The Airway, Step By Step",
             "--complete", "--zone", "UTC"], tmp)
        log = evidence.log_path(tmp)
        ev = completion_events(log)[0]
        _snapshot, rows = snapshot_queue(tmp)
        if not rows:
            fail("baseline queue must have a row")
        r = run(["retract", ev["event_id"], "--reason", "fixed clock test",
                 "--base", tmp], tmp)
        if r.returncode != 0:
            fail("retract exited %d: %s" % (r.returncode, r.stderr))
        # The event line is still physically in the log...
        if len(completion_events(log)) != 1:
            fail("retraction must not delete the original event line")
        # ...but a fresh snapshot contains neither the row nor the reason.
        _snapshot, rows = snapshot_queue(tmp)
        if rows:
            fail("fresh capture after retraction must contain no queue row: %r"
                 % rows)
        # Re-completing after retraction records again (the dedupe key is dead).
        r2 = run(["lesson", bank, "--ref", "The Airway, Step By Step",
                  "--complete", "--zone", "UTC"], tmp)
        if "recorded" not in r2.stdout:
            fail("re-completion after retraction must record: %r" % r2.stdout)
        if len(completion_events(log)) != 2:
            fail("re-completion must append a new event line")
        _snapshot, rows = snapshot_queue(tmp)
        if len(rows) != 1:
            fail("re-completed lesson must re-enter the queue once")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---- D-04: read paths stay side-effect-free; refusals are named ------------

def check_read_only_render():
    tmp = tempfile.mkdtemp()
    try:
        bank = os.path.join(tmp, "lesson_bank.md")
        shutil.copyfile(LES_BANK, bank)
        r = run(["lesson", bank], tmp)
        if r.returncode != 0:
            fail("plain lesson render exited %d" % r.returncode)
        log = evidence.log_path(tmp)
        if os.path.exists(log) and completion_events(log):
            fail("rendering the lesson must write no completion event")
        # The same read path through lesson_page directly.
        import itembank
        import surfaces.lesson as lesson_mod
        qs = itembank.load(bank)
        lesson = itembank.parse_lesson(bank)
        lesson_mod.lesson_page(bank, qs, lesson, ref="The Airway, Step By Step")
        if os.path.exists(log) and completion_events(log):
            fail("lesson_page must be read-only")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_heading_without_objective_refused():
    tmp = tempfile.mkdtemp()
    try:
        bank = os.path.join(tmp, "no_ref.md")
        open(bank, "w", encoding="utf-8").write(no_reference_bank_text())
        r = run(["lesson", bank, "--ref", "Lone Heading", "--complete",
                 "--zone", "UTC"], tmp)
        if r.returncode == 0:
            fail("a heading with no referenced objective must be refused")
        if "no_referenced_objective" not in (r.stderr + r.stdout):
            fail("the refusal must be named: %r" % (r.stderr + r.stdout))
        log = evidence.log_path(tmp)
        if os.path.exists(log) and completion_events(log):
            fail("a refused completion must append nothing")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_complete_requires_ref():
    tmp = tempfile.mkdtemp()
    try:
        bank = os.path.join(tmp, "lesson_bank.md")
        shutil.copyfile(LES_BANK, bank)
        r = run(["lesson", bank, "--complete"], tmp)
        if r.returncode == 0:
            fail("--complete without --ref must be refused")
        if "--ref" not in (r.stderr + r.stdout):
            fail("the --complete-without---ref refusal must name --ref: %r"
                 % (r.stderr + r.stdout))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---- D-01/D-13: fixed-clock due boundary and provenance --------------------

def check_fixed_clock_zone_boundary_and_dedupe():
    base, log = fresh_log()
    try:
        # 2026-08-10T23:00Z is Aug 10 in UTC but Aug 11 in UTC+09:00; the
        # queue date must follow the event's own zone.
        ev = lesson_event(slug="airway-basics", zone="UTC+09:00",
                          objectives=["emt:airway", "emt:ventilation"],
                          ts="2026-08-10T23:00:00.000Z")
        r1 = evidence.append_event(log, ev)
        if r1["status"] != "recorded":
            fail("first append must record")
        # Same completion identity -> idempotent.
        r2 = evidence.append_event(log, lesson_event(
            slug="airway-basics", zone="UTC+09:00",
            objectives=["emt:airway", "emt:ventilation"],
            ts="2026-08-11T01:00:00.000Z"))
        if r2["status"] != "already_recorded":
            fail("identical completion must dedupe, got %r" % r2)
        _snapshot, rows = snapshot_queue(base)
        if len(rows) != 2:
            fail("one row per referenced objective expected, got %r" % rows)
        row = rows[0]
        if row["completed_on"] != "2026-08-11":
            fail("completed_on must follow the event zone, got %r"
                 % row["completed_on"])
        if row["next_review_date"] != "2026-08-25":
            fail("next_review_date must be local date + 14 days, got %r"
                 % row["next_review_date"])
        if row["interval_days"] != 14 or row["reason"] != "lesson review":
            fail("queue row must expose configured interval and reason: %r"
                 % row)
        # Compensating retraction removes both rows from a fresh snapshot.
        evidence.append_event(log, evidence.retraction_event(
            ev["event_id"], "fixed clock test"))
        _snapshot, rows = snapshot_queue(base)
        if rows:
            fail("retraction must clear the queue rows: %r" % rows)
    finally:
        shutil.rmtree(base, ignore_errors=True)


def check_queue_ignores_non_completion_events():
    base, log = fresh_log()
    try:
        resp = evidence.response_event(
            "s1", {"objective": "emt:airway", "id": "q1",
                   "type": "mc", "item_id": ""}, "B", True,
            "practice", 1, "lesson_bank.md")
        resp["ts"] = "2026-08-10T12:00:00.000Z"
        evidence.append_event(log, resp)
        evidence.append_event(log, evidence.term_lookup_event(
            "s1", "lesson_bank.md", "airway", "practice", "reader"))
        import uuid
        model_line = {"schema_version": evidence.EVENT_SCHEMA_VERSION,
                      "event_id": uuid.uuid4().hex,
                      "event_type": "model_proposal",
                      "ts": "2026-08-10T13:00:00.000Z",
                      "session_id": "s1", "objective": "emt:airway",
                      "dedupe_key": uuid.uuid4().hex}
        evidence.append_line(log, json.dumps(model_line, sort_keys=True))
        # A lesson_complete line with an unresolvable zone must degrade by
        # skipping (D-09), never fabricate a date in the snapshot's zone.
        bad_zone = lesson_event(zone="Not/AZone", ts="2026-08-10T12:00:00.000Z")
        bad_zone["dedupe_key"] = uuid.uuid4().hex
        evidence.append_line(log, json.dumps(bad_zone, sort_keys=True))
        _snapshot, rows = snapshot_queue(base)
        if rows:
            fail("response/term/model/bad-zone events must never create queue "
                 "rows: %r" % rows)
    finally:
        shutil.rmtree(base, ignore_errors=True)


# ---- structural writer boundary (D-24, T-10-06) ----------------------------

def check_structural_writer_boundary():
    """The lesson GET/render call graph cannot reach append_event; the
    explicit completion branch reaches exactly the one writer."""
    import surfaces.lesson as lesson_mod
    import surfaces.daemon as daemon_mod
    for name, fn in (("lesson_page", lesson_mod.lesson_page),
                     ("handle_lesson_get", daemon_mod.handle_lesson_get)):
        src = inspect.getsource(fn)
        if "append_event" in src:
            fail("%s must be read-only but references append_event" % name)
    complete_src = inspect.getsource(lesson_mod.cmd_lesson_complete)
    if "evidence.append_event" not in complete_src:
        fail("the completion branch must call the one evidence writer")
    if "append_line" in complete_src:
        fail("the completion branch must never call append_line directly")


def main():
    check_builder_validation()
    check_cli_explicit_completion()
    check_idempotent_retry()
    check_retraction_removes_entry_and_recompletes()
    check_read_only_render()
    check_heading_without_objective_refused()
    check_complete_requires_ref()
    check_fixed_clock_zone_boundary_and_dedupe()
    check_queue_ignores_non_completion_events()
    check_structural_writer_boundary()
    print("lesson retention contract: ok (explicit completion, one event, "
          "derived queue row with interval/date/reason/provenance, dedupe, "
          "retraction, read-only render, named refusals, writer boundary)")


if __name__ == "__main__":
    main()
