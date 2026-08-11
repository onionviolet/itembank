#!/usr/bin/env python3
"""Pacing (10-04): the per-subject daily cap is a live-evidence projection.

Task 1's fixture: at four live ordinary responses against cap four, start is
blocked with the exact locked copy; at three, start serves at most one item
and a second genuine submit is blocked. A pending manual response counts; a
retracted response, a duplicate retry, and events on the previous local day
do not. `--override-cap` without the exact confirmation writes nothing; with
it, exactly one append-only cap_override event is bound to the generated
session id / subject / local day / snapshot and authorizes only that sitting,
then expires when the sitting ends.

The bank is copied into a temp dir so every evidence event lands in
tmp/_evidence and fixtures/_evidence is never touched. Local-day boundaries
are deterministic: the surfaces capture with zone UTC, so an event stamped on
today's calendar date (any time) is in the local day and one stamped on
yesterday is outside it -- computed from `datetime.now(utc)` at run time.

Standard library only, runnable as `python tests/pacing_roundtrip.py`.
"""
import datetime
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import evidence                                            # noqa: E402
import retention                                           # noqa: E402
from surfaces import session                                # noqa: E402

BANK = os.path.join(ROOT, "fixtures", "sample_bank.md")

# The locked UI copy (10-UI-SPEC.md line 163): U+2019 curly apostrophe,
# no second sentence, exact punctuation.
CAP_BLOCK_COPY = ("Today\u2019s {subject} cap is reached "
                  "({count} of {cap} ordinary attempts).")

CAP = 4
ZONE = "UTC"


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def now_utc():
    return datetime.datetime.now(datetime.timezone.utc)


def iso(dt):
    """An ISO-8601 UTC timestamp matching `_parse_utc`'s
    `%Y-%m-%dT%H:%M:%S.%fZ` format (fixed millisecond digits)."""
    return dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def today_ts(hour, minute=0):
    """A UTC timestamp on today's calendar date -- deterministically inside
    the local day no matter what wall-clock time the test runs at."""
    d = now_utc().date()
    return iso(datetime.datetime(d.year, d.month, d.day, hour, minute,
                                 tzinfo=datetime.timezone.utc))


def yesterday_ts(hour, minute=0):
    """A UTC timestamp on yesterday's calendar date -- deterministically
    outside the local day."""
    d = now_utc().date() - datetime.timedelta(days=1)
    return iso(datetime.datetime(d.year, d.month, d.day, hour, minute,
                                 tzinfo=datetime.timezone.utc))


def make_bank_dir():
    """A temp dir holding a copy of the fixture bank and a settings file with
    the small daily cap the test needs. The caller must rmtree it."""
    tmp = tempfile.mkdtemp()
    bank = os.path.join(tmp, "sample_bank.md")
    shutil.copyfile(BANK, bank)
    with open(os.path.join(tmp, "itembank.json"), "w", encoding="utf-8") as fh:
        json.dump({"daily_cap": CAP}, fh, ensure_ascii=False, indent=2)
    return tmp, bank


def evidence_log(bank_dir):
    return os.path.join(bank_dir, "_evidence", "evidence.jsonl")


def read_log(bank_dir):
    path = evidence_log(bank_dir)
    if not os.path.exists(path):
        return []
    return [json.loads(l) for l in open(path, encoding="utf-8").read().splitlines()
            if l.strip()]


def write_event(bank_dir, ev):
    os.makedirs(os.path.dirname(evidence_log(bank_dir)), exist_ok=True)
    with open(evidence_log(bank_dir), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(ev, ensure_ascii=False, sort_keys=True) + "\n")


def response(bank_dir, session_id, objective, ts, score=True, item_ref=None,
             bank="sample_bank.md"):
    """One synthetic response event for the pacing corpus. Pending (score
    None, item_type 'short') counts toward pacing; settled does too; the
    event shape mirrors evidence.response_event."""
    item_ref = item_ref or "Q%d" % len(read_log(bank_dir))
    return {
        "schema_version": evidence.EVENT_SCHEMA_VERSION,
        "event_id": evidence.new_event_id(),
        "event_type": "response",
        "ts": ts,
        "session_id": session_id,
        "item_id": "",
        "item_ref": item_ref,
        "item_type": "short" if score is None else "mc",
        "bank": bank,
        "objective": objective,
        "subject": evidence.subject_of(objective),
        "mode": "practice",
        "attempt_number": 1,
        "answer": "x" if score is None else "B",
        "canonical": "B" if score is not None else "short:x",
        "score": score,
        "response_time_ms": 1000,
        "confidence": None,
        "error_category": None,
        "hint_tier": None,
        "selection_mode": "practice",
        "review_state": "pending" if score is None else "n/a",
        "dedupe_key": evidence.dedupe_key(session_id, item_ref, 1,
                                          "B" if score is not None else "short:x"),
        "source_ref": None,
    }


def seed_emt(bank_dir, settled=0, pending=0, yesterday=0):
    """Write `settled` live emt responses today, `pending` live emt pending
    responses today, and `yesterday` live emt responses on the previous local
    day. Returns the list of written events."""
    written = []
    sid = "seed-%s" % os.path.basename(bank_dir)
    for i in range(settled):
        ev = response(bank_dir, sid, "emt:objective-%d" % i, today_ts(8 + i % 8),
                      score=True, item_ref="R%d" % (100 + i))
        write_event(bank_dir, ev)
        written.append(ev)
    for i in range(pending):
        ev = response(bank_dir, sid, "emt:pending-%d" % i, today_ts(10 + i % 8),
                      score=None, item_ref="P%d" % (200 + i))
        write_event(bank_dir, ev)
        written.append(ev)
    for i in range(yesterday):
        ev = response(bank_dir, sid, "emt:old-%d" % i, yesterday_ts(23, 30 + i % 29),
                      score=True, item_ref="Y%d" % (300 + i))
        write_event(bank_dir, ev)
        written.append(ev)
    return written


def retract(bank_dir, ev):
    write_event(bank_dir, evidence.retraction_event(ev["event_id"], "test"))


def start(bank_dir, bank, subject, count, **kw):
    spec = {"subject": subject, "count": count, "seed": kw.get("seed", 0),
            "selection_mode": "practice"}
    if kw.get("objective"):
        spec["objective"] = kw["objective"]
    if kw.get("forged"):
        spec.update(kw["forged"])
    return session.do_start(bank, spec, kw.get("mode", "practice"),
                            kw.get("out"), kw.get("force", False),
                            override_token=kw.get("override_token"))


def expect_block(fn, subject, count, cap):
    try:
        fn()
    except SystemExit as exc:
        msg = str(exc.code)
        want = CAP_BLOCK_COPY.format(subject=subject, count=count, cap=cap)
        if msg != want:
            fail("block message %r != locked copy %r" % (msg, want))
        return
    fail("expected a cap block, got none")


def correct_answer(qs, qid):
    q = next(x for x in qs if x["id"] == qid)
    if q["type"] == "mc":
        return q["correct"][0]
    if q["type"] == "multi":
        return json.dumps(list(q["correct"]))
    if q["type"] in ("table", "dnd"):
        return json.dumps(dict((str(i), r["cat"]) for i, r in enumerate(q["rows"])))
    if q["type"] == "build":
        return json.dumps(list(q["steps"]))
    return "A concise constructed response."


def wrong_answer(qs, qid):
    q = next(x for x in qs if x["id"] == qid)
    if q["type"] == "mc":
        return [o for o in q["options"] if o != q["correct"][0]][0]
    return "A materially different constructed response."


def check_cap_block_at_four():
    tmp, bank = make_bank_dir()
    try:
        seed_emt(tmp, settled=4)
        expect_block(lambda: start(tmp, bank, "emt", 5), "emt", 4, CAP)
        if os.path.exists(os.path.join(tmp, "_attempts")):
            fail("at-cap start must not write a session file")
        for ev in read_log(tmp):
            if ev.get("event_type") == "cap_override":
                fail("a plain at-cap start must not append a cap_override event")
    finally:
        shutil.rmtree(tmp)
    print("  at-cap start blocked with the exact locked copy and nothing written")


def check_below_cap_remaining_and_submit_guard():
    tmp, bank = make_bank_dir()
    try:
        seed_emt(tmp, settled=3)
        out = os.path.join(tmp, "_attempts", "session_test.json")
        result = start(tmp, bank, "emt", 5, out=out)
        if result.get("total") != 1:
            fail("below-cap start should serve exactly the remaining capacity "
                 "(1), served %s" % result.get("total"))
        binding = result["cap"] if "cap" in result else None
        if not binding or binding["count"] != 3 or binding["cap"] != CAP:
            fail("session must carry the cap binding count 3/cap %d: %r"
                 % (CAP, binding))
        qs = __import__("itembank").load(bank)
        item = result["item"]
        first = correct_answer(qs, item["id"])
        submitted = session.do_submit(out, first, "high")
        if submitted["accepted"] is not True:
            fail("first genuine submit below cap must be recorded, got %r"
                 % submitted["accepted"])
        # Re-arm the sitting as the long-sitting / crash-retry case: a
        # session whose cursor/status still allow the item (a resumed
        # multi-item sitting written before the remaining-capacity limit).
        # A duplicate retry of the SAME canonical answer is not a new
        # ordinary attempt: it must replay as already_recorded, not be
        # blocked and not double-count.
        resumed = session.read_session(out)
        resumed["status"] = "active"
        resumed["cursor"] = 0
        session.write_session(out, resumed)
        replay = session.do_submit(out, first, "high")
        if replay["accepted"] is not False or \
                replay["evidence"]["status"] != "already_recorded":
            fail("duplicate retry must dedupe to already_recorded, got %r"
                 % replay["evidence"]["status"])
        # A concurrent sitting on the same bank was authorized by the same
        # remaining capacity and records one more emt response in the same
        # local day -- the race the live recheck exists to stop. Now the
        # live count is 4/4 and a genuinely new attempt must be blocked
        # with the exact locked copy, while the replay above never
        # double-counted.
        write_event(tmp, response(tmp, "concurrent", "emt:concurrent-0",
                                  today_ts(12), score=True))
        second = wrong_answer(qs, item["id"])
        expect_block(lambda: session.do_submit(out, second, "high"), "emt", 4, CAP)
        count_resp = sum(1 for ev in read_log(tmp)
                         if ev.get("event_type") == "response")
        if count_resp != 5:
            fail("exactly 5 live responses expected (3 seeded + 1 genuine "
                 "+ 1 concurrent; the replay and the blocked attempt append "
                 "nothing), got %d" % count_resp)
    finally:
        shutil.rmtree(tmp)
    print("  remaining-capacity start, replay dedupe, and beyond-cap submit block")


def check_pending_counts_toward_cap():
    tmp, bank = make_bank_dir()
    try:
        seed_emt(tmp, settled=3, pending=1)
        expect_block(lambda: start(tmp, bank, "emt", 5), "emt", 4, CAP)
    finally:
        shutil.rmtree(tmp)
    print("  a pending manual response counts as an ordinary attempt")


def check_retracted_does_not_count():
    tmp, bank = make_bank_dir()
    try:
        evs = seed_emt(tmp, settled=4)
        retract(tmp, evs[2])
        out = os.path.join(tmp, "_attempts", "session_retract.json")
        result = start(tmp, bank, "emt", 5, out=out)
        if result.get("total") != 1:
            fail("with one of four retracted, remaining capacity is 1, served %s"
                 % result.get("total"))
        binding = result["cap"]
        if binding["count"] != 3:
            fail("retracted response must not count; count is %r" % binding["count"])
    finally:
        shutil.rmtree(tmp)
    print("  a retracted response does not count toward the cap")


def check_outside_local_day_does_not_count():
    tmp, bank = make_bank_dir()
    try:
        seed_emt(tmp, settled=3, yesterday=4)
        out = os.path.join(tmp, "_attempts", "session_day.json")
        result = start(tmp, bank, "emt", 5, out=out)
        if result.get("total") != 1:
            fail("previous-local-day events must not consume capacity; served %s"
                 % result.get("total"))
        binding = result["cap"]
        if binding["count"] != 3:
            fail("yesterday's responses must not count; count is %r"
                 % binding["count"])
    finally:
        shutil.rmtree(tmp)
    print("  events immediately outside the local-day boundary do not count")


def override_events(bank_dir):
    return [ev for ev in read_log(bank_dir)
            if ev.get("event_type") == "cap_override"]


def check_override_scope_and_expiry():
    tmp, bank = make_bank_dir()
    try:
        seed_emt(tmp, settled=4)
        # Wrong / absent confirmation: rejected, and nothing is written.
        try:
            start(tmp, bank, "emt", 2,
                  override_token="not the confirmation")
            fail("override with the wrong token must be rejected")
        except SystemExit as exc:
            if "confirmation" not in str(exc.code):
                fail("wrong-token refusal message unexpected: %r" % str(exc.code))
        if os.path.exists(os.path.join(tmp, "_attempts")):
            fail("a rejected override must write no session file")
        if override_events(tmp):
            fail("a rejected override must append no cap_override event")

        # Exact confirmation: one append-only override event bound to the
        # generated session id / subject / local day / snapshot.
        out = os.path.join(tmp, "_attempts", "session_override.json")
        result = start(tmp, bank, "emt", 2, out=out,
                       override_token=session.OVERRIDE_CONFIRMATION)
        evs = override_events(tmp)
        if len(evs) != 1:
            fail("confirmed override must append exactly one cap_override "
                 "event, found %d" % len(evs))
        ev = evs[0]
        if ev["session_id"] != result["session_id"]:
            fail("override event must bind to the generated session id")
        if ev["subject"] != "emt":
            fail("override event subject is %r, not emt" % ev["subject"])
        if ev["local_date"] != str(now_utc().date()):
            fail("override event local_date %r != today %s"
                 % (ev["local_date"], now_utc().date()))
        if ev["zone"] != ZONE:
            fail("override event zone is %r, not %s" % (ev["zone"], ZONE))
        binding = result["cap"]
        if ev["snapshot_id"] != binding["snapshot_id"]:
            fail("override event snapshot_id must match the session binding")
        if ev["cap"] != CAP or ev["count"] != 4:
            fail("override event must record cap/count 4/4, got %r/%r"
                 % (ev["cap"], ev["count"]))
        if ev.get("scope") != "sitting":
            fail("override event must be scoped to one sitting, got %r"
                 % ev.get("scope"))
        if not ev.get("dedupe_key") or len(ev["dedupe_key"]) != 64:
            fail("override event must carry a deterministic sha256 dedupe_key")
        if "score" in ev:
            fail("a non-response event must never carry a score key")
        if not ev.get("ts") or not ev.get("event_id") or \
                ev.get("event_type") != "cap_override" or \
                ev.get("schema_version") != evidence.EVENT_SCHEMA_VERSION:
            fail("override event must carry the standard envelope")
        if ev.get("bank") != "sample_bank.md":
            fail("override event bank must be the basename only")

        # The override authorizes only that sitting: answer both items, then
        # a brand-new sitting at cap is blocked again.
        qs = __import__("itembank").load(bank)
        for _ in range(2):
            data = session.read_session(out)
            if data["status"] == "complete":
                break
            q = qs[data["items"][data["cursor"]]]
            session.do_submit(out, correct_answer(qs, q["id"]), "high")
        data = session.read_session(out)
        if data["status"] != "complete":
            fail("override sitting should complete, status is %r"
                 % data["status"])
        expect_block(lambda: start(tmp, bank, "emt", 5), "emt", 4, CAP)

        # A confirmed override is ONE additional sitting: it is bounded to
        # at most one cap's worth of items, never an unbounded binge
        # (D-07/D-08).
        out2 = os.path.join(tmp, "_attempts", "session_override2.json")
        result2 = start(tmp, bank, "emt", 99, out=out2,
                        override_token=session.OVERRIDE_CONFIRMATION)
        if result2.get("total") != CAP:
            fail("an override sitting must be clamped to the cap (%d), "
                 "served %s" % (CAP, result2.get("total")))

        # The override event itself never reduces the count.
        counts = [ev for ev in read_log(tmp) if ev.get("event_type") == "response"]
        if len(counts) < 4:
            fail("responses vanished: %d" % len(counts))
    finally:
        shutil.rmtree(tmp)
    print("  scoped override: one append-only event, that-sitting-only, expiry")


def check_client_forgery_rejected():
    tmp, bank = make_bank_dir()
    try:
        seed_emt(tmp, settled=0)
        # A client-forged subject that contradicts the objective namespace.
        try:
            start(tmp, bank, "emt", 2, objective="math:limits")
            fail("forged subject must be rejected")
        except SystemExit as exc:
            if "subject" not in str(exc.code).lower():
                fail("forged-subject refusal unexpected: %r" % str(exc.code))
        # A client-forged cap/snapshot/override in the spec is refused.
        for forged in ({"cap": 1}, {"snapshot_id": "x" * 16}, {"override": True}):
            try:
                start(tmp, bank, "emt", 2, forged=forged)
                fail("forged %r must be rejected" % sorted(forged))
            except SystemExit:
                pass
        if os.path.exists(os.path.join(tmp, "_attempts")):
            fail("forged starts must write nothing")
    finally:
        shutil.rmtree(tmp)
    print("  client-forged subject/cap/snapshot/override values rejected")


def main():
    print("pacing_roundtrip:")
    check_cap_block_at_four()
    check_below_cap_remaining_and_submit_guard()
    check_pending_counts_toward_cap()
    check_retracted_does_not_count()
    check_outside_local_day_does_not_count()
    check_override_scope_and_expiry()
    check_client_forgery_rejected()
    print("pacing_roundtrip: ok")


if __name__ == "__main__":
    main()
