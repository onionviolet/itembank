#!/usr/bin/env python3
"""Plan 06.1-01 tracer: the interactive visual assessment protocol, end to end.

Drives one declarative plot item and the shared number-line variants through
every layer the phase owns:

  parser (model.parse_bank) -> key-free public contract (runtime.public_item)
  -> canonical SCALAR response -> runtime.score_response (sole scorer)
  -> normalized interaction_result + runtime-bounded observation
  -> append-only response evidence via the existing served submit path.

It also pins the locked protocol fixtures from 06.1-VALIDATION.md (the exact
SCALAR grammar, the three wire response shapes, rational reduction, decimal
trailing-zero removal, negative-zero normalisation, reversed-interval closure
swapping, exact step alignment, the 201-tick cap, and the refusal of
exponents/non-finite/symbolic values) and the private/public leakage sentinels.

Standard library only, no test framework, runnable as
`python tests/visual_roundtrip.py`.
"""
import json, os, re, shutil, subprocess, sys, tempfile, threading, time
import urllib.error, urllib.request


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ITEMBANK = os.path.join(ROOT, "itembank.py")
BANK = os.path.join(ROOT, "fixtures", "visual_bank.md")
sys.path.insert(0, ROOT)

import model           # noqa: E402
import runtime         # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def ok(msg):
    print("ok: " + msg)


# ---- the private scoring sentinels a public payload must never carry --------
PRIVATE_SENTINELS = ("accepted", "tolerance", "partial_credit", "scoring",
                     "model", "why", "disc", "second", "trap", "da",
                     "reveal", "solution")


def assert_public_payload_clean(payload, label):
    text = json.dumps(payload, sort_keys=True)
    for sentinel in PRIVATE_SENTINELS:
        # "accepted"/"tolerance" as bare keys inside the payload are leaks;
        # a stem word like "correct" would be a false positive, so we match
        # JSON key positions only.
        if re.search(r'"%s"\s*:' % re.escape(sentinel), text):
            fail("%s: public payload leaks private sentinel %r" % (label, sentinel))


def public_contract(q):
    """The interaction_contract every visual item must carry in public_item."""
    item = runtime.public_item(q)
    assert_public_payload_clean(item, "public_item")
    if item["type"] != "visual":
        fail("public_item type is %r, expected 'visual'" % item["type"])
    contract = item.get("interaction_contract")
    if not isinstance(contract, dict):
        fail("visual item carries no interaction_contract")
    if contract.get("version") != runtime.VISUAL_PROTOCOL_VERSION:
        fail("interaction_contract version is %r, expected %d" %
             (contract.get("version"), runtime.VISUAL_PROTOCOL_VERSION))
    if contract.get("type") != "visual":
        fail("interaction_contract type is %r, expected 'visual'"
             % contract.get("type"))
    return contract


# ---- 1. the parser: declarative visual fields, one private envelope ---------

def check_parser():
    qs = model.parse_bank(open(BANK, encoding="utf-8").read())
    visual = [q for q in qs if q["type"] == "visual"]
    if len(visual) != 4:
        fail("expected 4 visual items, parsed %d" % len(visual))
    plot = next(q for q in visual if q["interaction"] == "plot")
    nl = [q for q in visual if q["interaction"] == "numberline"]
    if len(nl) != 3:
        fail("expected 3 numberline items, parsed %d" % len(nl))
    # Private parsed envelope lives on the server item; no executable fields.
    for q in visual:
        if not isinstance(q.get("visual"), dict):
            fail("visual scene not parsed as dict for Q%d" % q["number"])
        if not isinstance(q.get("scoring"), dict):
            fail("scoring envelope not parsed as dict for Q%d" % q["number"])
        if "function" in json.dumps(q.get("visual")) or "<script" in json.dumps(q.get("visual")):
            fail("Q%d: scene carries an executable/script-bearing member" % q["number"])
    return plot, nl[0], nl[1], nl[2]


# ---- 2. the key-free public contract ----------------------------------------

def check_public(plot, nlp, nli, nlt):
    c = public_contract(plot)
    rc = c["renderer_config"]
    if set(rc["axes"]) != {"x", "y"}:
        fail("plot renderer_config axes are %r, expected x and y" % list(rc["axes"]))
    if rc["axes"]["x"]["step"] != "1":
        fail("plot x step is %r, expected '1'" % rc["axes"]["x"]["step"])
    if rc.get("actions") != ["place_point", "move_point"]:
        fail("plot actions are %r" % rc.get("actions"))
    if not (rc.get("accessibility") or {}).get("description"):
        fail("plot scene has no accessible description")
    if c["response_schema"]["kind"] != "point":
        fail("plot response_schema kind is %r" % c["response_schema"]["kind"])

    for q, kind in ((nlp, "numberline_point"), (nli, "interval"), (nlt, "numberline_point")):
        c = public_contract(q)
        rc = c["renderer_config"]
        if "axis" not in rc:
            fail("numberline renderer_config has no axis")
        if rc["axis"]["step"] != "1/2":
            fail("numberline step is %r, expected '1/2'" % rc["axis"]["step"])
        if c["response_schema"]["kind"] != kind:
            fail("numberline response_schema kind is %r, expected %s"
                 % (c["response_schema"]["kind"], kind))
    ok("public contract: key-free, versioned, scene/actions/accessibility only")


# ---- 3. the SCALAR grammar ---------------------------------------------------

def check_scalar_grammar():
    c = runtime.canonical_scalar
    cases = {
        "2": "2", "0": "0", "-0": "0", "+0": "0", "2.0": "2", "2.50": "5/2",
        "0.5": "1/2", "1/2": "1/2", "-1/2": "-1/2", "2/4": "1/2",
        "4/2": "2", "0.000001": "1/1000000", "-3.25": "-13/4",
    }
    for raw, want in cases.items():
        got = c(raw)
        if got != want:
            fail("canonical_scalar(%r) = %r, expected %r" % (raw, got, want))
    bad = ("1e3", "1E3", "NaN", "Infinity", "-Infinity", "1 1/2", "3x", "",
           "1.0000000", "1/0", "0/0", "1/1000001", "1000000001", "2.5.5")
    for raw in bad:
        got = c(raw)
        if got is not None:
            fail("canonical_scalar(%r) = %r, expected None (invalid)" % (raw, got))
    ok("SCALAR grammar: exact rational canonicalization, bounds, refusals")


# ---- 4. canonical response shapes + deterministic scoring --------------------

def canonical(q, answer):
    """The canonical semantic state dict a renderer/agent submits."""
    if isinstance(answer, str):
        return json.loads(answer)
    return answer


def check_scoring(plot, nlp, nli, nlt):
    # Locked golden fixtures from 06.1-VALIDATION.md.
    point = {"kind": "point", "x": "2", "y": "3"}
    nl_pt = {"kind": "numberline_point", "value": "1/2"}
    interval = {"kind": "interval", "start": "-1", "end": "3/2",
                "start_closed": True, "end_closed": False}

    if not runtime.score_response(plot, point):
        fail("plot accepted point (2,3) did not score True")
    if runtime.score_response(plot, {"kind": "point", "x": "2", "y": "2"}):
        fail("plot wrong point (2,2) scored True")
    if runtime.score_response(plot, {"kind": "point", "x": "2.0", "y": "3.0"}) is not True:
        fail("plot decimal aliases 2.0/3.0 did not canonicalize to the accepted point")

    if not runtime.score_response(nlp, nl_pt):
        fail("numberline accepted point 1/2 did not score True")
    if not runtime.score_response(nlp, {"kind": "numberline_point", "value": "0.5"}):
        fail("numberline decimal alias 0.5 did not canonicalize to 1/2")
    if runtime.score_response(nlp, {"kind": "numberline_point", "value": "1"}):
        fail("numberline wrong point 1 scored True")

    if not runtime.score_response(nli, interval):
        fail("interval accepted shape did not score True")
    reversed_interval = {"kind": "interval", "start": "3/2", "end": "-1",
                         "start_closed": False, "end_closed": True}
    if not runtime.score_response(nli, reversed_interval):
        fail("reversed interval with swapped closures did not normalize to the accepted shape")
    if runtime.score_response(nli, {"kind": "interval", "start": "-1", "end": "3/2",
                                    "start_closed": False, "end_closed": False}):
        fail("interval with wrong closures scored True")

    # Tolerance: 1/2 boundaries pass, the adjacent representable values fail.
    if not runtime.score_response(nlt, {"kind": "numberline_point", "value": "1/2"}):
        fail("tolerance lower boundary 1/2 did not pass")
    if not runtime.score_response(nlt, {"kind": "numberline_point", "value": "3/2"}):
        fail("tolerance upper boundary 3/2 did not pass")
    if runtime.score_response(nlt, {"kind": "numberline_point", "value": "0"}):
        fail("tolerance value 0 (adjacent to boundary) passed")
    if runtime.score_response(nlt, {"kind": "numberline_point", "value": "2"}):
        fail("tolerance value 2 (adjacent to boundary) passed")
    ok("scoring: exact discrete, decimal aliases, interval reversal, tolerance borders")


def check_invalid_rejection(plot, nlp, nli):
    invalid = [
        {"kind": "point", "x": "1e3", "y": "3"},          # exponent
        {"kind": "point", "x": "NaN", "y": "3"},          # non-finite
        {"kind": "point", "x": "2", "y": "10"},           # outside authored domain
        {"kind": "point", "x": "2", "y": "3", "score": True},   # forged authority field
        {"kind": "numberline_point", "value": "1.0000000"},     # excessive precision
        {"kind": "numberline_point", "value": "1/0"},           # malformed rational
        {"kind": "interval", "start": "-1", "end": "3/2"},      # missing closures
        {"kind": "interval", "start": "-1", "end": "3/2", "start_closed": True, "end_closed": "yes"},
        {"kind": "point", "x": "2", "y": "3", "tolerance": {"x": "1", "y": "1"}},
        {"kind": "hotspot"},                                     # unknown state kind
        "not a response",
        42,
    ]
    for answer in invalid:
        for q in (plot, nlp, nli):
            if runtime.score_response(q, answer) is not False:
                fail("invalid response %r scored non-False on Q%d"
                     % (answer, q["number"]))
    ok("invalid responses: non-finite, precision, domain, forged fields, malformed refuse")


# ---- 5. the normalized result + runtime-bounded observation ------------------

def check_interaction_result(plot, nlp, nli):
    point = {"kind": "point", "x": "2", "y": "3"}
    state = runtime.canonical_response(plot, point)
    verdict = runtime.score_response(plot, point)
    obs = runtime.visual_observation(plot, state, verdict, hint_tier=0)
    result = runtime.visual_interaction_result(plot, state, verdict, [obs])
    if result["version"] != runtime.VISUAL_PROTOCOL_VERSION:
        fail("interaction_result version is %r" % result["version"])
    if result["type"] != "visual":
        fail("interaction_result type is %r" % result["type"])
    if result["verdict"] is not True:
        fail("interaction_result verdict is %r, expected the exact score" % result["verdict"])
    if not isinstance(result["observations"], list) or not result["observations"]:
        fail("interaction_result observations missing")
    assert_public_payload_clean(result, "interaction_result")

    ob = result["observations"][0]
    for key in ("submitted", "error_category", "invariants", "feedback_anchor",
                "hint_tier"):
        if key not in ob:
            fail("observation missing %r: %r" % (key, ob))
    if ob["hint_tier"] != 0:
        fail("observation hint_tier is %r, expected the supplied Phase-6 entitlement 0"
             % ob["hint_tier"])
    if ob["error_category"] not in (None, "ok"):
        fail("correct observation has error_category %r" % ob["error_category"])
    text = json.dumps(ob)
    if '"accepted"' in text or re.search(r'"tolerance"\s*:', text):
        fail("observation leaks private scoring material")
    # A forged client hint tier must never raise the entitlement: the strict
    # response grammar rejects the extra authority field, so the forged
    # response is invalid (scored False) rather than upgraded.
    forged = dict(point, hint_tier=5, score=True)
    st2 = runtime.canonical_visual_response(plot, forged)
    if st2 is not None:
        fail("forged authority fields were not rejected by the response grammar")
    if runtime.score_response(plot, forged) is not False:
        fail("forged authority fields influenced the verdict")
    ok("interaction_result/observation: normalized, bounded, leak-free")


# ---- 6. served end-to-end: submit -> evidence --------------------------------

def run_served_submit():
    work = tempfile.mkdtemp()
    isolated = os.path.join(work, "visual_bank.md")
    shutil.copyfile(BANK, isolated)
    proc = subprocess.Popen(
        [sys.executable, "-u", ITEMBANK, "serve", isolated,
         "--no-open", "--port", "0", "--out", os.path.join(work, "attempt.md")],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    lines = []
    threading.Thread(target=lambda: [lines.append(l) for l in proc.stdout],
                     daemon=True).start()
    base = None
    for _ in range(80):
        time.sleep(0.1)
        m = re.search(r"http://127\.0\.0\.1:\d+/", "".join(lines))
        if m:
            base = m.group(0)
            break
    if not base:
        fail("server never printed a URL. Output was:\n" + "".join(lines))
    try:
        stem = os.path.splitext(os.path.basename(isolated))[0]
        page = urllib.request.urlopen(base + "quiz/%s" % stem, timeout=5)
        html = page.read().decode("utf-8")
        if "function asVisual" not in html:
            fail("served page has no asVisual renderer")
        if "visual:asVisual" not in html:
            fail("served page does not register asVisual in the renderer dispatch")

        start = api(base, "start", {"bank": stem, "mode": "practice", "count": 4})
        if start["status"] != "active":
            fail("POST /api/start did not return an active session")
        item = start["item"]
        assert_public_payload_clean(item, "/api/start item")
        if item["type"] != "visual":
            fail("served first item is %r, expected visual" % item["type"])
        contract = item.get("interaction_contract") or {}
        if contract.get("version") != runtime.VISUAL_PROTOCOL_VERSION:
            fail("served interaction_contract version mismatch")
        sid = start["session_id"]

        # Answer the sitting by item number: selection may serve the items in
        # any order, and the public contract never carries the accepted
        # states, so the test maps each served item number to the fixture's
        # correct semantic response.
        CORRECT = {
            1: {"kind": "point", "x": "2", "y": "3"},
            2: {"kind": "numberline_point", "value": "1/2"},
            3: {"kind": "interval", "start": "-1", "end": "3/2",
                "start_closed": True, "end_closed": False},
            4: {"kind": "numberline_point", "value": "3/2"},
        }
        seen = set()
        for _ in range(4):
            cur = api(base, "next", {"session_id": sid}) \
                if seen else start
            q = cur["item"]
            if q["type"] != "visual":
                fail("served item is %r, expected visual" % q["type"])
            num = q.get("number")
            if num not in CORRECT:
                fail("served visual item number %r has no fixture answer" % num)
            seen.add(num)
            v = api(base, "submit", {"session_id": sid,
                                     "answer": json.dumps(CORRECT[num])})
            if v.get("score") is not True:
                fail("served submit of Q%d accepted response returned score %r"
                     % (num, v.get("score")))
        if seen != set(CORRECT):
            fail("sitting did not serve every fixture item: %s" % sorted(seen))

        log = os.path.join(work, "_evidence", "evidence.jsonl")
        if not os.path.exists(log):
            fail("no evidence log written beside the served bank")
        events = [json.loads(l) for l in open(log, encoding="utf-8") if l.strip()]
        responses = [ev for ev in events if ev.get("event_type") == "response"]
        if len(responses) < 4:
            fail("expected 4 response events, found %d" % len(responses))
        last = responses[-1]
        if last.get("item_type") != "visual":
            fail("response event item_type is %r" % last.get("item_type"))
        answer = last.get("answer")
        if isinstance(answer, str):
            answer = json.loads(answer)
        if answer != {"kind": "numberline_point", "value": "3/2"}:
            fail("response event does not carry the canonical semantic state: %r"
                 % last.get("answer"))
        if "score" in json.dumps(answer):
            fail("response event answer carries an authority field")
        ok("served submit: /api/start -> /api/submit -> one response event with "
           "the canonical semantic state")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


def api(base, route, payload):
    req = urllib.request.Request(
        base + "api/" + route, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as res:
            return json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        fail("POST /api/%s failed: %s %s" %
             (route, exc.code, exc.read().decode("utf-8", "replace")))


def main():
    plot, nlp, nli, nlt = check_parser()
    check_public(plot, nlp, nli, nlt)
    check_scalar_grammar()
    check_scoring(plot, nlp, nli, nlt)
    check_invalid_rejection(plot, nlp, nli)
    check_interaction_result(plot, nlp, nli)
    run_served_submit()
    print("PASS visual_roundtrip.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
