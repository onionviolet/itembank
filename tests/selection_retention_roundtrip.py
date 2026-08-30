#!/usr/bin/env python3
"""Plan 10-03 fixed-seed harness: Phase 7 remains the SOLE item chooser; Phase
10 supplies only a server-derived retention context -- one snapshot claim plus
the bounded normalized objective-weight map -- through an additive
keyword-only parameter (D-01, D-04, D-10 through D-12).

What matters here, and why each case is tested rather than trusted:

1. D-10/D-11: a weak/due objective receives the higher normalized weight and is
   chosen ahead of an equal mastered objective in an ordinary practice sitting;
   `retention.py` returns no item indices and no choices originate outside
   `selection.select`.
2. D-11: mastered objectives leave ordinary practice/remediation rotation while
   a non-mastered eligible objective exists, but remain reachable through the
   explicit all-mastered fallback.
3. D-12: exam selection is byte-for-byte evidence-neutral (identical items AND
   trace with or without the context), diagnostic preserves Phase 7's coverage
   policy, and weight movement is bounded per snapshot by `max_weight_step`
   using the prior live selection event as the previous map -- no weight cache.
4. T-10-10/T-10-13: forged contexts (unknown keys, non-finite or non-positive
   weights, mismatched snapshot, answer-key/model/path payloads) are rejected,
   and a model event never changes the derived weights (D-16/D-22).
5. D-01: session file, selection evidence event, returned trace, and every
   chosen reason name one identical snapshot id.

Standard library only, runnable as `python tests/selection_retention_roundtrip.py`.
"""
import datetime
import inspect
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import evidence
import retention
import selection
import surfaces.session as session_mod


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


BANK_TEXT = """# Retention selection (synthetic)

Q1. Which sign most clearly suggests the airway is at risk?   (difficulty: recall)
[OBJECTIVE: emt:airway]

A) Snoring with a weak effort
B) A patient speaking in full sentences
C) A capillary refill of two seconds
D) Warm, dry skin

CORRECT: A

WHY BEST: Snoring with a weak effort is obstruction with failing compensation.

KEY DISCRIMINATOR: The finding must describe air movement itself.

SECOND-BEST: B. Full sentences mean a patent airway; this would be correct if the question asked which finding rules out obstruction.

DISTRACTOR ANALYSIS:
- A) Correct: obstruction with failing compensation.
- B) A patent airway; this would be correct if the question asked which finding rules out obstruction.
- C) A perfusion finding; this would be correct if the question asked about circulation.
- D) A perfusion finding; this would be correct if the question asked about circulation.

TRAP: Reaching for any abnormal finding instead of the one that describes air movement.

CONFIDENCE: high

Q2. Which adjunct fits an airway that is at risk?   (difficulty: application)
[OBJECTIVE: emt:airway]

A) Oropharyngeal airway
B) Nasal cannula
C) A tourniquet
D) A defibrillator

CORRECT: A

WHY BEST: An oropharyngeal airway holds the tongue off the posterior pharynx.

KEY DISCRIMINATOR: The adjunct must act on the airway itself.

SECOND-BEST: B. A nasal cannula delivers oxygen; this would be correct if the question asked which device adds oxygen.

DISTRACTOR ANALYSIS:
- A) Correct: the airway adjunct.
- B) An oxygen delivery device; this would be correct if the question asked which device adds oxygen.
- C) A circulation device; this would be correct if the question asked about hemorrhage.
- D) A rhythm device; this would be correct if the question asked about cardiac arrest.

TRAP: Reaching for any device instead of the one that opens the airway.

CONFIDENCE: high

Q3. Which property makes a number easy to factor mentally?   (difficulty: recall)
[OBJECTIVE: emt:math]

A) It is a small prime
B) It is a large composite with two close factors
C) It is irrational
D) It has a fractional exponent

CORRECT: A

WHY BEST: A small prime factors trivially by trial division.

KEY DISCRIMINATOR: The property must make factoring fast.

SECOND-BEST: B. Close factors still require search; this would be correct if the question asked which number is hardest to factor.

DISTRACTOR ANALYSIS:
- A) Correct: trivially factored.
- B) Close factors make factoring harder; this would be correct if the question asked which is hardest.
- C) Irrational numbers are not integers; this would be correct if the question asked about real numbers.
- D) Fractional exponents are not integers; this would be correct if the question asked about exponent rules.

TRAP: Confusing "easy to factor" with "interesting number".

CONFIDENCE: high

Q4. Which method computes a greatest common divisor?   (difficulty: application)
[OBJECTIVE: emt:math]

A) Euclidean algorithm
B) Quadratic formula
C) Newton's method
D) Sieve of Eratosthenes

CORRECT: A

WHY BEST: The Euclidean algorithm repeatedly reduces the pair to their GCD.

KEY DISCRIMINATOR: The method must compute GCD, not primes or roots.

SECOND-BEST: D. The sieve finds primes; this would be correct if the question asked which method lists primes.

DISTRACTOR ANALYSIS:
- A) Correct: the GCD algorithm.
- B) Solves quadratics; this would be correct if the question asked which finds roots.
- C) Finds roots/optima; this would be correct if the question asked which approximates roots.
- D) Lists primes; this would be correct if the question asked which finds primes.

TRAP: Reaching for any famous algorithm.

CONFIDENCE: high
"""

CUTOFF = "2026-08-10T12:00:00.000Z"


def fresh_base():
    """A temp dir holding an empty _evidence/evidence.jsonl, returned as the
    base and the evidence log path."""
    tmp = tempfile.mkdtemp()
    log = evidence.log_path(tmp)
    os.makedirs(os.path.dirname(log), exist_ok=True)
    return tmp, log


def resp(session_id, objective, item_ref, score, ts):
    ev = evidence.response_event(
        session_id, {"objective": objective, "id": item_ref,
                     "type": "mc", "item_id": ""}, "B", score,
        "practice", 1, "selection_bank.md")
    ev["ts"] = ts
    return ev


def append_all(log, events):
    for ev in events:
        evidence.append_event(log, ev)


TS_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


def as_of_now(events):
    """Re-date a fixture so its recency is measured from the live clock.

    The legs that call `context()` pin the snapshot cutoff to CUTOFF, so an
    absolute fixture timestamp is deterministic there. The CLI leg cannot pin
    anything: `do_start` captures against the wall clock, so a fixture dated
    around CUTOFF decays one more real day every real day, until the weak
    objective and the mastered one both bottom out at weight 1.0, the tie
    hands the ordering back to Phase 7, and the leg fails on the calendar
    rather than on a defect. Shifting every event by one identical offset
    preserves the fixture's relative shape exactly, which is the only thing
    the weights read.
    """
    delta = (datetime.datetime.strptime(evidence.utc_now(), TS_FORMAT)
             - datetime.datetime.strptime(CUTOFF, TS_FORMAT))
    shifted = []
    for ev in events:
        moved = dict(ev)
        moved["ts"] = (datetime.datetime.strptime(ev["ts"], TS_FORMAT)
                       + delta).strftime(TS_FORMAT)[:-4] + "Z"
        shifted.append(moved)
    return shifted


def weak_airway_evidence():
    """emt:airway weak: 3 settled, 1 correct, all recent (no 28-day silence)."""
    return [
        resp("s1", "emt:airway", "q1", False, "2026-08-01T10:00:00.000Z"),
        resp("s2", "emt:airway", "q2", False, "2026-08-02T10:00:00.000Z"),
        resp("s3", "emt:airway", "q1", True, "2026-08-03T10:00:00.000Z"),
    ]


def mastered_math_evidence():
    """emt:math mastered: 4 correct on distinct local days."""
    return [
        resp("s4", "emt:math", "q3", True, "2026-07-25T10:00:00.000Z"),
        resp("s5", "emt:math", "q4", True, "2026-07-28T10:00:00.000Z"),
        resp("s6", "emt:math", "q3", True, "2026-07-30T10:00:00.000Z"),
        resp("s7", "emt:math", "q4", True, "2026-08-02T10:00:00.000Z"),
    ]


def context(base, cutoff=CUTOFF):
    """The same derivation the session surface performs: one capture, one
    snapshot, the normalized bounded weight map (no previous map)."""
    events = evidence.capture_events(evidence.log_path(base))
    snapshot = retention.capture(events, cutoff=cutoff, zone="UTC", cfg=None)
    weights = retention.objective_weights(
        retention.objective_summaries(snapshot), snapshot)
    return {"snapshot": snapshot["claim"], "objective_weights": weights}


def ids(items):
    return [q["id"] for q in items]


def run_cli(args, cwd):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    return subprocess.run([sys.executable, os.path.join(ROOT, "itembank.py")] + args,
                          cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                          env=env, timeout=60)


# ---- T-10-10/T-10-13: forged retention contexts are rejected ----------------

def check_context_validation():
    import model
    base, log = fresh_base()
    try:
        append_all(log, weak_airway_evidence() + mastered_math_evidence())
        tmp_bank = os.path.join(base, "bank.md")
        open(tmp_bank, "w", encoding="utf-8").write(BANK_TEXT)
        qs = model.load(tmp_bank)
        ctx = context(base)
        spec = {"count": 2, "seed": 0, "selection_mode": "practice"}
        # The valid context is accepted.
        selection.select(qs, spec, history=[], retention_context=ctx)
        w = ctx["objective_weights"]
        bad = {
            "unknown context key": {"snapshot": ctx["snapshot"],
                                    "objective_weights": w, "nonsense": 1},
            "weights not a dict": {"snapshot": ctx["snapshot"],
                                   "objective_weights": [1, 2]},
            "entry not a dict": {"snapshot": ctx["snapshot"],
                                 "objective_weights": {"emt:airway": 1.1}},
            "entry unknown key": {"snapshot": ctx["snapshot"],
                                  "objective_weights": {
                                      "emt:airway": {"weight": 1.1,
                                                     "components": {},
                                                     "snapshot_id": ctx["snapshot"]["snapshot_id"],
                                                     "answer": "B"}}},
            "non-finite weight": {"snapshot": ctx["snapshot"],
                                  "objective_weights": {
                                      "emt:airway": {"weight": float("nan"),
                                                     "components": {},
                                                     "snapshot_id": ctx["snapshot"]["snapshot_id"]}}},
            "non-positive weight": {"snapshot": ctx["snapshot"],
                                    "objective_weights": {
                                        "emt:airway": {"weight": -0.5,
                                                       "components": {},
                                                       "snapshot_id": ctx["snapshot"]["snapshot_id"]}}},
            "mismatched snapshot": {"snapshot": ctx["snapshot"],
                                    "objective_weights": {
                                        "emt:airway": {"weight": 1.1,
                                                       "components": {},
                                                       "snapshot_id": "other"}}},
            "missing snapshot id": {"snapshot": {"cutoff": "x"},
                                    "objective_weights": {}},
        }
        for name, forged in bad.items():
            try:
                selection.select(qs, spec, history=[], retention_context=forged)
                fail("forged context %r must be rejected" % name)
            except SystemExit as exc:
                if "retention" not in str(exc):
                    fail("forged context %r must name retention in the error: %r"
                         % (name, str(exc)))
    finally:
        shutil.rmtree(base, ignore_errors=True)


# ---- D-10/D-11: weak objective preferred in practice -----------------------

def check_weak_objective_preferred_in_practice():
    import model
    base, log = fresh_base()
    try:
        append_all(log, weak_airway_evidence() + mastered_math_evidence())
        ctx = context(base)
        w = ctx["objective_weights"]
        if w["emt:airway"]["weight"] <= w["emt:math"]["weight"]:
            fail("weak objective must outrank mastered: %r" % w)
        tmp_bank = os.path.join(base, "bank.md")
        open(tmp_bank, "w", encoding="utf-8").write(BANK_TEXT)
        qs = model.load(tmp_bank)
        spec = {"count": 2, "seed": 0, "selection_mode": "practice"}
        items, trace = selection.select(qs, spec, history=[],
                                        retention_context=ctx)
        chosen = ids(items)
        if sorted(chosen) != ["q1", "q2"]:
            fail("weak objective must fill the practice count first: %r"
                 % chosen)
        sid = ctx["snapshot"]["snapshot_id"]
        ret = trace.get("retention")
        if not ret or ret["snapshot_id"] != sid:
            fail("trace must name the context snapshot id: %r" % ret)
        for block in trace["chosen"]:
            if block["objective_weight"] != w[block["objective"]]["weight"]:
                fail("chosen entry must carry the final normalized multiplier: %r"
                     % block)
            if block.get("retention_snapshot_id") != sid:
                fail("chosen entry must name the snapshot id: %r" % block)
            if sid not in block["reason"]:
                fail("chosen reason must name the snapshot id: %r"
                     % block["reason"])
        if trace["chosen"][0]["reason"].find("weight") == -1:
            fail("chosen reason must name the weight influence: %r"
                 % trace["chosen"][0]["reason"])
    finally:
        shutil.rmtree(base, ignore_errors=True)


# ---- D-11: mastered fallback -----------------------------------------------

def check_mastered_fallback():
    import model
    base, log = fresh_base()
    try:
        # All objectives mastered -> the bounded fallback still serves.
        append_all(log, [
            resp("s1", "emt:airway", "q1", True, "2026-07-25T10:00:00.000Z"),
            resp("s2", "emt:airway", "q2", True, "2026-07-28T10:00:00.000Z"),
            resp("s3", "emt:airway", "q1", True, "2026-07-30T10:00:00.000Z"),
            resp("s4", "emt:airway", "q2", True, "2026-08-02T10:00:00.000Z"),
            resp("s5", "emt:math", "q3", True, "2026-07-25T10:00:00.000Z"),
            resp("s6", "emt:math", "q4", True, "2026-07-28T10:00:00.000Z"),
            resp("s7", "emt:math", "q3", True, "2026-07-30T10:00:00.000Z"),
            resp("s8", "emt:math", "q4", True, "2026-08-02T10:00:00.000Z"),
        ])
        ctx = context(base)
        tmp_bank = os.path.join(base, "bank.md")
        open(tmp_bank, "w", encoding="utf-8").write(BANK_TEXT)
        qs = model.load(tmp_bank)
        items, trace = selection.select(
            qs, {"count": 2, "seed": 1, "selection_mode": "practice"},
            history=[], retention_context=ctx)
        if len(items) != 2:
            fail("all-mastered fallback must still fill the count, got %d"
                 % len(items))
        if not any("mastered" in note for note in trace["notes"]):
            fail("the all-mastered fallback must be named in the trace notes: %r"
                 % trace["notes"])
        # Mixed: mastered exists but non-mastered fills the count first.
        base2, log2 = fresh_base()
        append_all(log2, weak_airway_evidence() + mastered_math_evidence())
        ctx2 = context(base2)
        qs2 = model.load(tmp_bank)
        items2, trace2 = selection.select(
            qs2, {"count": 2, "seed": 0, "selection_mode": "practice"},
            history=[], retention_context=ctx2)
        if sorted(ids(items2)) != ["q1", "q2"]:
            fail("non-mastered work must fill the count before mastered "
                 "fallback: %r" % ids(items2))
        if not any("fallback" in note for note in trace2["notes"]):
            fail("the mastered deferral must be named in the trace notes: %r"
                 % trace2["notes"])
        shutil.rmtree(base2, ignore_errors=True)
    finally:
        shutil.rmtree(base, ignore_errors=True)


# ---- D-12: exam/diagnostic neutrality --------------------------------------

def check_exam_and_diagnostic_neutrality():
    import model
    base, log = fresh_base()
    try:
        append_all(log, weak_airway_evidence() + mastered_math_evidence())
        ctx = context(base)
        tmp_bank = os.path.join(base, "bank.md")
        open(tmp_bank, "w", encoding="utf-8").write(BANK_TEXT)
        qs = model.load(tmp_bank)
        for mode in ("exam", "diagnostic"):
            spec = {"count": 3, "seed": 7, "selection_mode": mode}
            plain_items, plain_trace = selection.select(
                qs, dict(spec), history=[], retention_context=None)
            ctx_items, ctx_trace = selection.select(
                qs, dict(spec), history=[], retention_context=ctx)
            if ids(plain_items) != ids(ctx_items):
                fail("%s must be evidence-neutral in items: %r vs %r"
                     % (mode, ids(plain_items), ids(ctx_items)))
            if json.dumps(plain_trace, sort_keys=True) != \
                    json.dumps(ctx_trace, sort_keys=True):
                fail("%s must be evidence-neutral in the trace" % mode)
    finally:
        shutil.rmtree(base, ignore_errors=True)


def check_remediation_consumes_weights():
    import model
    base, log = fresh_base()
    try:
        append_all(log, weak_airway_evidence() + mastered_math_evidence())
        ctx = context(base)
        tmp_bank = os.path.join(base, "bank.md")
        open(tmp_bank, "w", encoding="utf-8").write(BANK_TEXT)
        qs = model.load(tmp_bank)
        # Remediation draws only from objectives with a recorded failure
        # (airway), and consumes the retention ordering on top.
        items, trace = selection.select(
            qs, {"count": 2, "seed": 0, "selection_mode": "remediation"},
            history=weak_airway_evidence(), retention_context=ctx)
        if sorted(ids(items)) != ["q1", "q2"]:
            fail("remediation must serve the failed objective: %r" % ids(items))
        if trace.get("retention", {}).get("snapshot_id") != \
                ctx["snapshot"]["snapshot_id"]:
            fail("remediation trace must name the retention snapshot")
    finally:
        shutil.rmtree(base, ignore_errors=True)


# ---- D-12: bounded step from the prior live selection event ----------------

def check_step_bound_from_previous_selection_event():
    base, log = fresh_base()
    try:
        append_all(log, weak_airway_evidence() + mastered_math_evidence())
        # A prior sitting's selection event records the weights it consumed.
        prior = {
            "snapshot_id": "prev0001",
            "objective_weights": {
                "emt:airway": {"weight": 1.5, "components": {},
                               "snapshot_id": "prev0001"},
                "emt:math": {"weight": 0.5, "components": {},
                             "snapshot_id": "prev0001"},
            },
            "trace": None,
        }
        evidence.append_event(log, evidence.selection_event(
            "prev_session", "selection_bank.md",
            {"selection_mode": "practice", "count": 2, "seed": 0},
            ["q1", "q2"], retention=prior))
        ctx = session_mod._retention_context(evidence.log_path(base), None)
        w = ctx["objective_weights"]
        step = retention.RETENTION_SETTINGS_DEFAULTS["max_weight_step"]
        for obj, entry in w.items():
            prev = prior["objective_weights"][obj]["weight"]
            if abs(entry["weight"] - prev) > step + 1e-9:
                fail("weight for %r moved %r, over max_weight_step %r"
                     % (obj, abs(entry["weight"] - prev), step))
        # Without the previous map the same capture moves further, proving the
        # cap actually engaged (uncapped weak weight is ~1.19, far from 1.5).
        uncapped = context(base)
        moved_far = abs(uncapped["objective_weights"]["emt:airway"]["weight"]
                        - 1.5) > step
        if not moved_far:
            fail("fixture: uncapped weight must exceed the step, so the cap "
                 "has something to prove")
    finally:
        shutil.rmtree(base, ignore_errors=True)


# ---- D-01: session + selection event + trace share one snapshot id ---------

def check_session_and_selection_event_provenance():
    tmp = tempfile.mkdtemp()
    try:
        bank = os.path.join(tmp, "bank.md")
        open(bank, "w", encoding="utf-8").write(BANK_TEXT)
        append_all(evidence.log_path(tmp),
                   as_of_now(weak_airway_evidence()
                             + mastered_math_evidence()))
        r = run_cli(["start", bank, "--count", "2", "--seed", "0",
                     "--mode", "practice", "--selection-mode", "practice",
                     "--out", os.path.join(tmp, "s.json")], tmp)
        if r.returncode != 0:
            fail("itembank start exited %d: %s" % (r.returncode, r.stderr))
        started = json.loads(r.stdout)
        session_file = started["session_file"]
        data = json.load(open(session_file, encoding="utf-8"))
        ret = data.get("retention")
        if not ret or not ret.get("snapshot_id"):
            fail("session file must carry the retention snapshot id: %r"
                 % (ret,))
        if not isinstance(ret.get("objective_weights"), dict) \
                or "emt:airway" not in ret["objective_weights"]:
            fail("session must carry the public weight map: %r" % (ret,))
        if not isinstance(ret["objective_weights"]["emt:airway"]["weight"],
                          (int, float)):
            fail("session weight map must carry bounded weights: %r" % (ret,))
        sid = ret["snapshot_id"]
        # The trace returned by start names the same snapshot id.
        trace_ret = started["trace"].get("retention")
        if not trace_ret or trace_ret["snapshot_id"] != sid:
            fail("start trace must name the session snapshot id: %r"
                 % (trace_ret,))
        # The live selection event carries the identical snapshot id and the
        # full component map.
        log = evidence.log_path(tmp)
        sel_ev = None
        for ev in evidence.events(log):
            if ev.get("event_type") == evidence.SELECTION_EVENT_TYPE:
                sel_ev = ev
        if sel_ev is None:
            fail("no selection event recorded")
        ev_ret = sel_ev.get("retention") or {}
        if ev_ret.get("snapshot_id") != sid:
            fail("selection event snapshot id differs from the session's: %r"
                 % ev_ret.get("snapshot_id"))
        weights = ev_ret.get("objective_weights") or {}
        for obj, entry in weights.items():
            if entry.get("snapshot_id") != sid:
                fail("weight entry %r names a different snapshot" % obj)
            if not isinstance(entry.get("components"), dict):
                fail("weight entry %r must carry the component trace" % obj)
        # The session weight map equals the event's weight values.
        for obj, entry in weights.items():
            if obj in ret["objective_weights"] and \
                    ret["objective_weights"][obj]["weight"] != entry["weight"]:
                fail("session and event weight maps disagree on %r" % obj)
        # The weak objective fills the sitting.
        import model as model_mod
        chosen_ids = [model_mod.load(bank)[i]["id"] for i in data["items"]]
        if sorted(chosen_ids) != ["q1", "q2"]:
            fail("the weak objective must fill the sitting: %r" % chosen_ids)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---- D-10/T-10-11: retention is not a chooser; D-16: model events ignored --

def check_retention_module_is_not_a_chooser():
    src = inspect.getsource(retention)
    for needle in ("import selection", "selection.select", "select(",
                   "append_event", "model.load"):
        if needle in src:
            fail("retention.py must not %r: it is a projection, never a "
                 "chooser or writer" % needle)


def check_model_event_never_changes_weights():
    import uuid
    base, log = fresh_base()
    try:
        append_all(log, weak_airway_evidence() + mastered_math_evidence())
        before = context(base)["objective_weights"]
        model_line = {"schema_version": evidence.EVENT_SCHEMA_VERSION,
                      "event_id": uuid.uuid4().hex,
                      "event_type": "model_proposal",
                      "ts": "2026-08-05T10:00:00.000Z",
                      "session_id": "s9", "objective": "emt:airway",
                      "dedupe_key": uuid.uuid4().hex}
        evidence.append_line(log, json.dumps(model_line, sort_keys=True))
        after = context(base)["objective_weights"]
        if json.dumps(before, sort_keys=True) != \
                json.dumps(after, sort_keys=True):
            fail("a model event must never change derived weights (D-16)")
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main():
    check_context_validation()
    check_weak_objective_preferred_in_practice()
    check_mastered_fallback()
    check_exam_and_diagnostic_neutrality()
    check_remediation_consumes_weights()
    check_step_bound_from_previous_selection_event()
    check_session_and_selection_event_provenance()
    check_retention_module_is_not_a_chooser()
    check_model_event_never_changes_weights()
    print("selection retention contract: ok (weighted practice ordering, "
          "mastered fallback, exam/diagnostic neutrality, bounded step from "
          "prior selection event, shared snapshot provenance, forged-context "
          "rejection, model-event immunity, sole-chooser boundary)")


if __name__ == "__main__":
    main()
