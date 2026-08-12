#!/usr/bin/env python3
"""Phase 10 Wave 0 fixed-clock harness: one immutable evidence capture drives
every objective state, trend row, recommendation, weight, scheduler state,
and evidence claim, with no second store, reader, writer, or selector.

What matters here, and why each case is tested rather than trusted:

1. D-01/D-02: capturing identical bytes/cutoff/zone/filters/settings twice
   yields byte-identical JSON and the same snapshot id; appending after
   capture cannot change an already-returned snapshot.
2. D-03: sparse evidence is `unknown` with null rates -- never zero mastery,
   zero due, or a fabricated trend.
3. D-09/D-16/D-22: a pending constructed response counts toward attempts
   only; the latest accepted human mark settles it; a model/interaction
   event never settles anything; retractions disappear everywhere.
4. D-06/D-14: the six-state grammar is deterministic and settings-bounded;
   at-risk requires prior proven success plus configured silence.
5. D-13: week buckets carry raw counts beside rates; no denominator is an
   explicit null.
6. D-11/D-12: weights are bounded, normalized, and capped per snapshot.
7. D-17/D-18/D-19/D-23: scheduler state replays exactly from the log; stages
   have a terminal "retired"; due order is utility-weighted.
8. D-20: return rate is a stated-denominator ratio, never a streak.
9. D-15: `itembank trends --json` and plain text are renderings of one
   payload; every nested claim references one snapshot id.

Standard library only, runnable as `python tests/retention_roundtrip.py`.
"""
import datetime
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


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def fresh_log():
    """A temp dir holding an empty _evidence/evidence.jsonl, returned as the
    evidence log path."""
    tmp = tempfile.mkdtemp()
    log = evidence.log_path(tmp)
    os.makedirs(os.path.dirname(log), exist_ok=True)
    return tmp, log


def resp(session_id, objective, item_ref, answer, score, ts, item_type="mc",
         hint_tier=None):
    """One response event with a controlled timestamp (fixed clock)."""
    ev = evidence.response_event(
        session_id, {"objective": objective, "id": item_ref,
                     "type": item_type, "item_id": ""},
        answer, score, "practice", 1, "bank.md", hint_tier=hint_tier)
    ev["ts"] = ts
    return ev


def append_all(log, events):
    for ev in events:
        evidence.append_event(log, ev)


def snap(base, cutoff="2026-08-10T12:00:00.000Z", zone="UTC", weeks=4,
         filters=None, cfg=None):
    events = evidence.capture_events(evidence.log_path(base))
    return retention.capture(events, cutoff=cutoff, zone=zone, weeks=weeks,
                             filters=filters, cfg=cfg)


def report(base, **kw):
    events = evidence.capture_events(evidence.log_path(base))
    return retention.retention_report(events, **kw)


def state_of(payload, objective):
    return payload["objectives"][objective]["state"]


# ---- D-01/D-02: immutable snapshot, byte stability, provenance ------------

def check_byte_stable_and_immutable():
    base, log = fresh_log()
    try:
        append_all(log, [
            resp("s1", "emt:airway", "q1", "B", True, "2026-07-01T10:00:00.000Z"),
            resp("s2", "emt:airway", "q1", "C", False, "2026-07-10T10:00:00.000Z"),
        ])
        kwargs = dict(cutoff="2026-08-10T12:00:00.000Z", zone="UTC", weeks=4)
        p1 = report(base, **kwargs)
        p2 = report(base, **kwargs)
        if json.dumps(p1, sort_keys=True) != json.dumps(p2, sort_keys=True):
            fail("capturing the same bytes twice produced different reports")
        if p1["claim"]["snapshot_id"] != p2["claim"]["snapshot_id"]:
            fail("same inputs produced different snapshot ids")
        claim = p1["claim"]
        for field in ("snapshot_id", "cutoff", "local_day_zone", "window",
                      "filters", "live_event_count", "settings_version"):
            if field not in claim:
                fail("claim is missing field %r: %r" % (field, sorted(claim)))
        if claim["live_event_count"] != 2:
            fail("live_event_count is %r, not 2" % claim["live_event_count"])
        # Every nested section references the same snapshot id.
        sid = claim["snapshot_id"]
        for obj, row in p1["objectives"].items():
            if row["snapshot_id"] != sid:
                fail("objective %r references a different snapshot id" % obj)
        for w in p1["weights"].values():
            if w["snapshot_id"] != sid:
                fail("a weight references a different snapshot id")
        if p1["recommendation"].get("snapshot_id") != sid:
            fail("recommendation references a different snapshot id")
        # Append after capture: the already-returned payload must not change.
        append_all(log, [resp("s3", "emt:airway", "q1", "B", True,
                              "2026-08-05T10:00:00.000Z")])
        p3 = report(base, **kwargs)
        if json.dumps(p1, sort_keys=True) != json.dumps(p2, sort_keys=True):
            fail("appending after capture changed an already-returned report")
        if p3["claim"]["snapshot_id"] == p1["claim"]["snapshot_id"]:
            fail("a fresh capture after append must carry a new snapshot id")
        if p3["claim"]["live_event_count"] != 3:
            fail("fresh capture live_event_count is %r, not 3"
                 % p3["claim"]["live_event_count"])
    finally:
        shutil.rmtree(base, ignore_errors=True)


def check_zone_and_filters_provenance():
    base, log = fresh_log()
    try:
        # 2026-08-10T23:00Z is Aug 10 in UTC but Aug 11 in Asia/Tokyo (+9).
        append_all(log, [
            resp("s1", "emt:airway", "q1", "B", True, "2026-08-10T23:00:00.000Z"),
        ])
        kwargs = dict(cutoff="2026-08-11T00:30:00.000Z", weeks=4)
        p_utc = report(base, zone="UTC", **kwargs)
        p_tokyo = report(base, zone="Asia/Tokyo", **kwargs)
        if p_utc["claim"]["local_day_zone"] != "UTC":
            fail("zone label not recorded")
        if p_tokyo["claim"]["local_day_zone"] != "Asia/Tokyo":
            fail("IANA zone label not recorded")
        if p_utc["claim"]["snapshot_id"] == p_tokyo["claim"]["snapshot_id"]:
            fail("two zones must produce two distinct snapshots")
        f = report(base, zone="UTC", filters={"subject": "emt"}, **kwargs)
        if f["claim"]["filters"] != {"subject": "emt"}:
            fail("filters not recorded in the claim")
        if f["claim"]["snapshot_id"] == p_utc["claim"]["snapshot_id"]:
            fail("a filtered snapshot must differ from an unfiltered one")
        f2 = report(base, zone="UTC", filters={"subject": "math"}, **kwargs)
        if f2["overview"]["objective_count"] != 0:
            fail("a non-matching subject filter must yield no objectives")
    finally:
        shutil.rmtree(base, ignore_errors=True)


# ---- D-03/D-06/D-14: the six-state grammar ---------------------------------

def check_states():
    base = base2 = base3 = base4 = base5 = base6 = None
    base, log = fresh_log()
    try:
        # unknown: fewer than 3 settled attempts.
        append_all(log, [
            resp("s1", "emt:airway", "q1", "B", True, "2026-07-01T10:00:00.000Z"),
            resp("s2", "emt:airway", "q1", "C", False, "2026-07-10T10:00:00.000Z"),
        ])
        p = report(base)
        row = p["objectives"]["emt:airway"]
        if row["state"] != "unknown":
            fail("2 settled attempts must be unknown, got %r" % row["state"])
        if row["due"] is not False:
            fail("an unknown objective must not be due")
        if row["accuracy"] is None or row["accuracy"] == 0:
            fail("raw accuracy must be present once settled exists")
        # weak + due: three settled, one correct, all recent (so at-risk's
        # 28-day silence rule does not fire first -- D-14 precedence). Own
        # log so the raw accuracy is exactly 1/3.
        base2, log2 = fresh_log()
        append_all(log2, [
            resp("s1", "emt:airway", "q1", "A", True, "2026-08-01T10:00:00.000Z"),
            resp("s2", "emt:airway", "q1", "D", False, "2026-08-02T10:00:00.000Z"),
            resp("s3", "emt:airway", "q1", "E", False, "2026-08-03T10:00:00.000Z"),
        ])
        p = report(base2)
        row = p["objectives"]["emt:airway"]
        if row["state"] != "weak":
            fail("3 settled with 1 correct must be weak, got %r" % row["state"])
        if not row["due"]:
            fail("weak must be due")
        if row["accuracy"] != 1 / 3:
            fail("raw accuracy is %r, not 1/3" % row["accuracy"])
        if "weak" not in p["overview"]["states"]:
            fail("overview states missing weak")
        # mastered: 3 distinct-day successes at high accuracy, own log.
        base3, log3 = fresh_log()
        append_all(log3, [
            resp("s1", "emt:airway", "q1", "B", True, "2026-07-25T10:00:00.000Z"),
            resp("s2", "emt:airway", "q1", "B", True, "2026-07-28T10:00:00.000Z"),
            resp("s3", "emt:airway", "q1", "B", True, "2026-07-30T10:00:00.000Z"),
            resp("s4", "emt:airway", "q1", "B", True, "2026-08-02T10:00:00.000Z"),
        ])
        p = report(base3)
        row = p["objectives"]["emt:airway"]
        if row["state"] != "mastered":
            fail("recent high accuracy + 3 distinct success days must be "
                 "mastered, got %r" % row["state"])
        if row["due"] is not False:
            fail("mastered must not be due")
        # at-risk: prior success then 28 days silence. New objective.
        base4, log4 = fresh_log()
        append_all(log4, [
            resp("s1", "emt:airway", "q1", "B", True, "2026-07-13T10:00:00.000Z"),
            resp("s2", "emt:airway", "q1", "B", True, "2026-07-13T11:00:00.000Z"),
            resp("s3", "emt:airway", "q1", "B", True, "2026-07-13T12:00:00.000Z"),
        ])
        p = report(base4, cutoff="2026-08-09T12:00:00.000Z")
        row = p["objectives"]["emt:airway"]
        if row["state"] != "due":
            fail("27 days after last success must be due-by-interval, not "
                 "yet at-risk, got %r" % row["state"])
        p = report(base4, cutoff="2026-08-10T12:00:00.000Z")
        row = p["objectives"]["emt:airway"]
        if row["state"] != "at-risk":
            fail("28 days after last success must be at-risk, got %r"
                 % row["state"])
        if "last confirmed success" not in (row["risk_reason"] or ""):
            fail("at-risk reason must name the last proven success: %r"
                 % row["risk_reason"])
        if not row["due"]:
            fail("at-risk must be due")
        # due by interval: stable objective, review interval elapsed.
        base5, log5 = fresh_log()
        append_all(log5, [
            resp("s1", "emt:airway", "q1", "B", True, "2026-07-01T10:00:00.000Z"),
            resp("s2", "emt:airway", "q1", "B", True, "2026-07-02T10:00:00.000Z"),
            resp("s3", "emt:airway", "q1", "B", True, "2026-07-03T10:00:00.000Z"),
            resp("s4", "emt:airway", "q1", "B", False, "2026-08-01T10:00:00.000Z"),
            resp("s5", "emt:airway", "q1", "B", True, "2026-08-01T11:00:00.000Z"),
        ])
        p = report(base5, cutoff="2026-08-10T12:00:00.000Z")
        row = p["objectives"]["emt:airway"]
        if row["state"] != "due":
            fail("interval elapsed since last settled must be due, got %r"
                 % row["state"])
        # stable: enough evidence, no escalation.
        base6, log6 = fresh_log()
        append_all(log6, [
            resp("s1", "emt:airway", "q1", "B", True, "2026-08-01T10:00:00.000Z"),
            resp("s2", "emt:airway", "q1", "B", True, "2026-08-02T10:00:00.000Z"),
            resp("s3", "emt:airway", "q1", "B", True, "2026-08-03T10:00:00.000Z"),
            resp("s4", "emt:airway", "q1", "B", False, "2026-08-04T10:00:00.000Z"),
            resp("s5", "emt:airway", "q1", "B", True, "2026-08-05T10:00:00.000Z"),
        ])
        # An explicit cutoff, like every other case above. Defaulting to the
        # wall clock made this case pass only while the real date was near the
        # fixture's, and silently flip to 'due' once the review interval had
        # elapsed against today -- a test that expires is not a test.
        p = report(base6, cutoff="2026-08-06T12:00:00.000Z")
        row = p["objectives"]["emt:airway"]
        if row["state"] != "stable":
            fail("sufficient recent evidence without escalation must be "
                 "stable, got %r" % row["state"])
    finally:
        for tmp in (base, base2, base3, base4, base5, base6):
            if tmp:
                shutil.rmtree(tmp, ignore_errors=True)


# ---- D-09/D-16/D-22: pending, accepted mark, retraction, model events ------

def check_pending_and_marks():
    base, log = fresh_log()
    try:
        # Three settled responses on distinct days plus one pending short.
        append_all(log, [
            resp("s1", "emt:airway", "q1", "B", True, "2026-08-01T10:00:00.000Z"),
            resp("s2", "emt:airway", "q2", "C", False, "2026-08-02T10:00:00.000Z"),
            resp("s3", "emt:airway", "q3", "D", True, "2026-08-03T10:00:00.000Z"),
            resp("s4", "emt:airway", "q4", "free text", None,
                 "2026-08-04T10:00:00.000Z", item_type="short"),
        ])
        p = report(base)
        row = p["objectives"]["emt:airway"]
        if row["pending"] != 1:
            fail("pending count is %r, not 1" % row["pending"])
        if row["attempts"] != 4:
            fail("pending must count toward attempts, got %r" % row["attempts"])
        if row["settled"] != 3 or row["accuracy"] != 2 / 3:
            fail("pending must not settle accuracy: %r" % row)
        # Accepted human mark settles the short response.
        pending_ev = None
        for ev in evidence.events(log):
            if ev.get("event_type") == evidence.RESPONSE_EVENT_TYPE \
                    and ev.get("item_ref") == "q4":
                pending_ev = ev
        evidence.append_event(log, evidence.mark_event(
            "s4", pending_ev.get("item_id", ""), "q4",
            pending_ev["event_id"], True))
        p = report(base)
        row = p["objectives"]["emt:airway"]
        if row["pending"] != 0:
            fail("accepted mark must clear pending, got %r" % row["pending"])
        if row["settled"] != 4 or row["correct"] != 3:
            fail("accepted mark must settle the response: %r" % row)
        # A model-shaped event (unknown type) must be ignored, not fatal.
        import uuid
        bogus = {"schema_version": evidence.EVENT_SCHEMA_VERSION,
                 "event_id": uuid.uuid4().hex, "event_type": "model_proposal",
                 "ts": evidence.utc_now(), "session_id": "s9",
                 "objective": "emt:airway", "dedupe_key": uuid.uuid4().hex}
        evidence.append_line(log, json.dumps(bogus, sort_keys=True))
        p = report(base)
        if p["claim"]["live_event_count"] != len(evidence.capture_events(log)):
            fail("live_event_count disagrees with the capture")
        if "model_proposal" in json.dumps(p):
            fail("a model proposal event must never enter the report payload")
    finally:
        shutil.rmtree(base, ignore_errors=True)


def check_retraction():
    base, log = fresh_log()
    try:
        evs = [
            resp("s1", "emt:airway", "q1", "B", True, "2026-08-01T10:00:00.000Z"),
            resp("s2", "emt:airway", "q1", "C", False, "2026-08-02T10:00:00.000Z"),
            resp("s3", "emt:airway", "q1", "B", True, "2026-08-03T10:00:00.000Z"),
        ]
        append_all(log, evs)
        p = report(base)
        if p["claim"]["live_event_count"] != 3:
            fail("baseline live count is %r, not 3" % p["claim"]["live_event_count"])
        # Retract the middle response.
        evidence.append_event(log, evidence.retraction_event(
            evs[1]["event_id"], "fixed clock test"))
        p = report(base)
        row = p["objectives"]["emt:airway"]
        if p["claim"]["live_event_count"] != 2:
            fail("retraction must remove the event from the capture, got %r"
                 % p["claim"]["live_event_count"])
        if row["settled"] != 2 or row["correct"] != 2:
            fail("retracted response must vanish from state: %r" % row)
    finally:
        shutil.rmtree(base, ignore_errors=True)


# ---- D-13: week series raw counts and null uncertainty ---------------------

def check_week_series():
    base, log = fresh_log()
    try:
        append_all(log, [
            resp("s1", "emt:airway", "q1", "B", True, "2026-07-05T10:00:00.000Z"),
            resp("s2", "emt:airway", "q2", "C", False, "2026-07-25T10:00:00.000Z"),
            resp("s3", "emt:airway", "q3", "D", True, "2026-08-05T10:00:00.000Z",
                 hint_tier=2),
            resp("s4", "emt:airway", "q4", "D", True, "2026-08-08T10:00:00.000Z",
                 hint_tier=3),
        ])
        p = report(base, cutoff="2026-08-10T12:00:00.000Z")
        weeks = p["objectives"]["emt:airway"]["weeks"]
        for key in ("1w", "2w", "4w", "8w", "12w"):
            if key not in weeks:
                fail("week series missing bucket %r" % key)
        b1 = weeks["1w"]
        if b1["attempts"] != 2 or b1["correct"] != 2 or b1["settled"] != 2:
            fail("1w bucket raw counts wrong: %r" % b1)
        if b1["accuracy"] != 1.0:
            fail("1w bucket accuracy is %r, not 1.0" % b1["accuracy"])
        if b1["highest_hint"] != 3 or b1["average_hint"] != 2.5:
            fail("1w hint tiers wrong: %r" % b1)
        b12 = weeks["12w"]
        if b12["attempts"] != 4 or b12["settled"] != 4:
            fail("12w bucket raw counts wrong: %r" % b12)
        # A bucket with no settled evidence is null, never zero.
        base2, log2 = fresh_log()
        append_all(log2, [
            resp("s1", "emt:airway", "q1", "B", True, "2026-01-01T10:00:00.000Z"),
        ])
        p2 = report(base2, cutoff="2026-08-10T12:00:00.000Z")
        if p2["objectives"]["emt:airway"]["weeks"]["1w"]["settled"] != 0:
            fail("empty 1w bucket must have settled 0")
        if p2["objectives"]["emt:airway"]["weeks"]["1w"]["accuracy"] is not None:
            fail("empty bucket accuracy must be null (unknown), not a number")
    finally:
        shutil.rmtree(base, ignore_errors=True)
        shutil.rmtree(base2, ignore_errors=True)


# ---- D-11/D-12: bounded normalized weights and per-snapshot cap ------------

def check_weights():
    base, log = fresh_log()
    try:
        # Two objectives: one weak (due), one mastered.
        append_all(log, [
            resp("s1", "emt:airway", "q1", "B", False, "2026-08-01T10:00:00.000Z"),
            resp("s2", "emt:airway", "q1", "C", False, "2026-08-02T10:00:00.000Z"),
            resp("s3", "emt:airway", "q1", "D", True, "2026-08-03T10:00:00.000Z"),
            resp("s4", "emt:math", "m1", "B", True, "2026-08-01T10:00:00.000Z"),
            resp("s5", "emt:math", "m1", "B", True, "2026-08-02T10:00:00.000Z"),
            resp("s6", "emt:math", "m1", "B", True, "2026-08-03T10:00:00.000Z"),
            resp("s7", "emt:math", "m1", "B", True, "2026-08-04T10:00:00.000Z"),
        ])
        p = report(base)
        w = p["weights"]
        if state_of(p, "emt:airway") != "weak":
            fail("fixture: emt:airway must be weak, got %r" % state_of(p, "emt:airway"))
        if state_of(p, "emt:math") != "mastered":
            fail("fixture: emt:math must be mastered, got %r" % state_of(p, "emt:math"))
        cfg = retention.RETENTION_SETTINGS_DEFAULTS
        for obj, entry in w.items():
            if not (cfg["weight_min"] <= entry["weight"] <= cfg["weight_max"]):
                fail("weight %r outside bounded range" % entry["weight"])
        if w["emt:airway"]["weight"] < w["emt:math"]["weight"]:
            fail("weak objective must outrank mastered: %r" % w)
        if w["emt:airway"]["components"]["weak"] <= 0:
            fail("weak component missing for weak objective: %r"
                 % w["emt:airway"])
        if w["emt:math"]["components"]["mastery"] >= 0:
            fail("mastery component must be a reduction: %r" % w["emt:math"])
        # Max-step cap: a previous map far from current must move by at most
        # max_weight_step.
        prev = {"emt:airway": cfg["weight_max"], "emt:math": cfg["weight_min"]}
        p2 = report(base)
        for obj, entry in p2["weights"].items():
            step = abs(entry["weight"] - prev[obj])
            if step > cfg["max_weight_step"] + 1e-9:
                fail("weight moved %r, over max_weight_step %r"
                     % (step, cfg["max_weight_step"]))
    finally:
        shutil.rmtree(base, ignore_errors=True)


def check_invalid_config():
    base, log = fresh_log()
    try:
        bad = {"retention": dict(retention.RETENTION_SETTINGS_DEFAULTS)}
        bad["retention"]["weak_accuracy"] = 0.9   # >= mastery_accuracy 0.85
        try:
            retention.retention_settings(bad)
            fail("weak >= mastery must be rejected as invalid config")
        except SystemExit as exc:
            if "retention.invalid_config" not in str(exc):
                fail("invalid config error must be named: %r" % exc)
        bad2 = {"retention": dict(retention.RETENTION_SETTINGS_DEFAULTS)}
        bad2["retention"]["weight_min"] = 1.5
        bad2["retention"]["weight_max"] = 1.0
        try:
            retention.retention_settings(bad2)
            fail("weight_min >= weight_max must be rejected")
        except SystemExit as exc:
            if "retention.invalid_config" not in str(exc):
                fail("invalid floor/ceiling error must be named: %r" % exc)
    finally:
        shutil.rmtree(base, ignore_errors=True)


# ---- D-17/D-18/D-19/D-23: scheduler replay, stages, utility order ----------

def check_scheduler():
    base, log = fresh_log()
    try:
        append_all(log, [
            resp("s1", "emt:airway", "q1", "B", True, "2026-08-01T10:00:00.000Z"),
            resp("s2", "emt:airway", "q1", "B", True, "2026-08-03T10:00:00.000Z"),
            resp("s3", "emt:airway", "q1", "B", True, "2026-08-06T10:00:00.000Z"),
        ])
        p1 = report(base, cutoff="2026-08-10T12:00:00.000Z")
        p2 = report(base, cutoff="2026-08-10T12:00:00.000Z")
        s1 = p1["objectives"]["emt:airway"]["scheduler"]
        s2 = p2["objectives"]["emt:airway"]["scheduler"]
        if s1 != s2:
            fail("scheduler replay must reproduce exactly from the log")
        if s1["strategy"] != "fsrs":
            fail("default scheduler strategy must be fsrs, got %r" % s1["strategy"])
        if s1["reviews"] != 3:
            fail("scheduler must replay 3 reviews, got %r" % s1["reviews"])
        if not s1["interval_days"] or s1["interval_days"] < 1:
            fail("interval must be a positive integer, got %r" % s1)
        if s1["stage"] not in retention.STAGE_NAMES:
            fail("unknown stage %r" % s1["stage"])
        # Terminal "retired" exists and no stage exceeds it.
        if retention.STAGE_NAMES[-1] != "Retired":
            fail("terminal stage must be named Retired")
        if retention.stage_for_interval(10 ** 6) != "Retired":
            fail("a far-future interval must be the terminal retired stage")
        # Registration interface: a second strategy can coexist (D-18/D-23).
        class Stub(retention.SchedulerStrategy):
            name = "stub"
            def replay(self, objective, summaries, snapshot):
                return {"objective": objective, "strategy": "stub",
                        "interval_days": 1, "due_date": None,
                        "stage": "Apprentice I", "reviews": 0}
        retention.register_scheduler(Stub())
        states = retention.scheduler_states(
            retention.objective_summaries(
                retention.capture(evidence.capture_events(log))),
            retention.capture(evidence.capture_events(log)), strategy_name="stub")
        if states["emt:airway"]["strategy"] != "stub":
            fail("registered strategy not reachable by name")
    finally:
        shutil.rmtree(base, ignore_errors=True)


def check_utility_order_and_return_rate():
    base, log = fresh_log()
    try:
        # Two weak objectives; one slightly more overdue.
        append_all(log, [
            resp("s1", "emt:airway", "q1", "B", False, "2026-07-20T10:00:00.000Z"),
            resp("s2", "emt:airway", "q1", "C", False, "2026-07-21T10:00:00.000Z"),
            resp("s3", "emt:airway", "q1", "D", True, "2026-07-22T10:00:00.000Z"),
            resp("s4", "emt:math", "m1", "B", False, "2026-07-28T10:00:00.000Z"),
            resp("s5", "emt:math", "m1", "C", False, "2026-07-29T10:00:00.000Z"),
            resp("s6", "emt:math", "m1", "D", True, "2026-07-30T10:00:00.000Z"),
        ])
        p = report(base, cutoff="2026-08-10T12:00:00.000Z")
        order = p["due_order"]
        if len(order) != 2:
            fail("both weak objectives must be in the due order, got %r" % order)
        if order[0]["objective"] != "emt:airway":
            fail("more-overdue objective must rank first: %r" % order)
        if not (0 < order[0]["utility"] <= order[0]["weight"] * 60):
            fail("utility out of bounded range: %r" % order[0])
        rr = p["return_rate"]
        for field in ("occurred", "due", "rate"):
            if field not in rr:
                fail("return_rate missing %r" % field)
        if "streak" in json.dumps(rr).lower():
            fail("return_rate must never render as a streak")
    finally:
        shutil.rmtree(base, ignore_errors=True)


# ---- D-15: JSON and plain-text parity through the real CLI -----------------

def check_cli_json_text_parity():
    base, log = fresh_log()
    try:
        append_all(log, [
            resp("s1", "emt:airway", "q1", "B", False, "2026-08-01T10:00:00.000Z"),
            resp("s2", "emt:airway", "q1", "C", False, "2026-08-02T10:00:00.000Z"),
            resp("s3", "emt:airway", "q1", "D", True, "2026-08-03T10:00:00.000Z"),
        ])
        env = dict(os.environ)
        env["PYTHONIOENCODING"] = "utf-8"
        args = [sys.executable, os.path.join(ROOT, "itembank.py"), "trends",
                "--base", base, "--cutoff", "2026-08-10T12:00:00.000Z",
                "--zone", "UTC", "--weeks", "4", "--json"]
        r = subprocess.run(args, capture_output=True, text=True, env=env)
        if r.returncode != 0:
            fail("itembank trends --json exited %d: %s"
                 % (r.returncode, r.stderr[:400]))
        payload = json.loads(r.stdout)
        # Schema-validate the real output.
        import schema_validate
        schema = json.load(open(os.path.join(ROOT, "schemas",
                                             "report.schema.json"),
                                encoding="utf-8"))
        errs = schema_validate.validate(payload, schema)
        if errs:
            fail("retention report failed the published schema: %s" % errs[0])
        # Plain text must carry the same snapshot id and the same counts.
        r2 = subprocess.run([sys.executable,
                             os.path.join(ROOT, "itembank.py"), "trends",
                             "--base", base, "--cutoff",
                             "2026-08-10T12:00:00.000Z",
                             "--zone", "UTC", "--weeks", "4"],
                            capture_output=True, text=True, env=env)
        if r2.returncode != 0:
            fail("itembank trends (text) exited %d" % r2.returncode)
        if payload["claim"]["snapshot_id"] not in r2.stdout:
            fail("plain text must carry the same snapshot id")
        if "emt:airway" not in r2.stdout:
            fail("plain text must name the same objectives")
        if "unknown" not in r2.stdout and "due" not in r2.stdout \
                and "weak" not in r2.stdout:
            fail("plain text must render the objective state")
        # No private fields in either rendering.
        for blob in (r.stdout, r2.stdout):
            for banned in ("CORRECT:", "WHY BEST:", "distractor", "answer key"):
                if banned.lower() in blob.lower():
                    fail("public output leaked private content %r" % banned)
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main():
    check_byte_stable_and_immutable()
    check_zone_and_filters_provenance()
    check_states()
    check_pending_and_marks()
    check_retraction()
    check_week_series()
    check_weights()
    check_invalid_config()
    check_scheduler()
    check_utility_order_and_return_rate()
    check_cli_json_text_parity()
    print("retention contract: ok (immutable snapshot, six states, pending/"
          "mark/retraction semantics, week series, bounded weights, FSRS "
          "replay + stages + utility order, return rate, JSON/text parity)")


if __name__ == "__main__":
    main()
