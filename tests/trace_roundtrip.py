#!/usr/bin/env python3
"""Plan 999.1-03 tracer (trace): the trace_path family, end to end.

Drives the additive protocol-1 extension for re-tracing a reference polyline
through every layer: parser -> key-free public contract (axes, point_count,
public reference polyline in initial) -> canonical
{"kind":"trace_path","points":[{"x":SCALAR,"y":SCALAR},...]} response ->
runtime.score_response (element-wise per-coordinate tolerance, fixed count,
pinned boundaries) -> runtime-bounded observation (point_count, in_bounds,
out_of_domain, wrong_point_count) -> committed place_trace_point /
move_trace_point actions via session.do_interact -> one visual_action event.

It also pins that the accepted path never leaves the server (the public
reference path in initial is scene data only), schema validation, the served
renderer dispatch (renderTrace, no canvas), the static offline refusal, and
GIFT's loud refusal of trace items.

Standard library only, no test framework, runnable as
`python tests/trace_roundtrip.py`.
"""
import json, os, re, shutil, subprocess, sys, tempfile, threading, time
import urllib.error, urllib.request


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ITEMBANK = os.path.join(ROOT, "itembank.py")
BANK = os.path.join(ROOT, "fixtures", "advanced_visual_bank.md")
sys.path.insert(0, ROOT)

import model                                           # noqa: E402
import runtime                                         # noqa: E402
import schema_validate                                 # noqa: E402
from surfaces import session as session_surface        # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def ok(msg):
    print("ok: " + msg)


ACTION_ID = "123e4567-e89b-42d3-a456-426614174000"

PRIVATE_SENTINELS = ("accepted", "tolerance", "partial_credit", "scoring",
                     "model", "why", "disc", "second", "trap", "da",
                     "reveal", "solution")


def assert_public_payload_clean(payload, label):
    text = json.dumps(payload, sort_keys=True)
    for sentinel in PRIVATE_SENTINELS:
        if re.search(r'"%s"\s*:' % re.escape(sentinel), text):
            fail("%s: public payload leaks private sentinel %r" % (label, sentinel))


def load_bank(path=BANK):
    return model.parse_bank(open(path, encoding="utf-8").read())


def trace_items(qs):
    return [q for q in qs if q["type"] == "visual"
            and q["interaction"] == "trace"]


# ---- 1. parser --------------------------------------------------------------

def check_parser():
    qs = load_bank()
    visual = [q for q in qs if q["type"] == "visual"]
    if len(visual) != 12:
        fail("expected 12 visual items, parsed %d" % len(visual))
    tr = trace_items(qs)
    if len(tr) != 2:
        fail("expected 2 trace items, parsed %d" % len(tr))
    return tr


# ---- 2. key-free public contract --------------------------------------------

def check_public(tr):
    for q in tr:
        item = runtime.public_item(q)
        assert_public_payload_clean(item, "public_item")
        c = item["interaction_contract"]
        if c["version"] != runtime.VISUAL_PROTOCOL_VERSION \
                or c["interaction"] != "trace":
            fail("trace contract header wrong: %r" % c)
        if c["response_schema"]["kind"] != "trace_path":
            fail("trace response_schema kind is %r" % c["response_schema"]["kind"])
        rc = c["renderer_config"]
        for key in ("axes", "point_count", "initial", "actions",
                    "accessibility"):
            if key not in rc:
                fail("trace renderer_config missing %r" % key)
        if rc["point_count"] != 3:
            fail("trace point_count is %r" % rc["point_count"])
        if not (rc["initial"].get("points") or []):
            fail("trace public reference polyline missing from initial")
        # The reference polyline is public scene data; the accepted path must
        # not leak anywhere.
        blob = json.dumps(item)
        for banned in ('"accepted"', '"tolerance"', '"partial_credit"'):
            if banned in blob:
                fail("trace public item leaks %s" % banned)
    ok("public contract: key-free trace scene (axes/point_count/initial ref)")


# ---- 3. scoring: element-wise, fixed count, pinned borders ------------------

def check_scoring(tr):
    exact, tol = tr

    def path(pts):
        return {"kind": "trace_path", "points": pts}

    good = [{"x": "0", "y": "0"}, {"x": "2", "y": "2"}, {"x": "4", "y": "0"}]
    if not runtime.score_response(exact, path(good)):
        fail("exact trace path did not score True")
    wrong_mid = [{"x": "0", "y": "0"}, {"x": "2", "y": "0"},
                 {"x": "4", "y": "0"}]
    if runtime.score_response(exact, path(wrong_mid)):
        fail("trace with wrong middle point scored True")
    reordered = [{"x": "4", "y": "0"}, {"x": "2", "y": "2"}, {"x": "0", "y": "0"}]
    if runtime.score_response(exact, path(reordered)):
        fail("reordered trace scored True (order matters)")
    short = [{"x": "0", "y": "0"}, {"x": "2", "y": "2"}]
    if runtime.score_response(exact, path(short)):
        fail("trace with wrong point count scored True")
    for p in ({"x": "9", "y": "0"}, {"x": "0", "y": "1e3"}):
        if runtime.score_response(exact, path([p, good[1], good[2]])):
            fail("out-of-domain point scored True")
    forged = {"kind": "trace_path", "points": good, "score": True}
    if runtime.score_response(exact, forged) is not False:
        fail("forged authority field influenced the verdict")

    # Tolerance item: the left arm at (0, 2) tolerates a half-unit shift.
    # (1/2, 3/2) is on both boundaries and passes; (1, 3/2) is a full unit
    # off in x and fails.
    border_ok = [{"x": "1/2", "y": "3/2"}, {"x": "2", "y": "0"},
                 {"x": "4", "y": "2"}]
    if not runtime.score_response(tol, path(border_ok)):
        fail("boundary-shifted trace (1/2, 3/2) should pass")
    border_bad = [{"x": "1", "y": "3/2"}, {"x": "2", "y": "0"},
                  {"x": "4", "y": "2"}]
    if runtime.score_response(tol, path(border_bad)):
        fail("full-unit-shifted trace (1, 3/2) passed")

    for bad in ({"kind": "trace_path"}, {"kind": "trace_path", "points": {}},
                {"kind": "trace_path", "points": [{"x": "0", "y": "0"}]},
                {"kind": "hotspot", "region": "a"},
                "not a response", None):
        if runtime.score_response(exact, bad) is not False:
            fail("malformed trace response %r scored non-False" % (bad,))
    ok("scoring: element-wise tolerance, order + count enforced, borders "
       "1/2 pass / 1 fail, invalid fail closed")


# ---- 4. observation ---------------------------------------------------------

def check_observation(tr):
    exact = tr[0]
    state = runtime.canonical_visual_response(
        exact, {"kind": "trace_path",
                "points": [{"x": "0", "y": "0"}, {"x": "2", "y": "2"},
                           {"x": "4", "y": "0"}]})
    obs = runtime.visual_observation(exact, state, True, hint_tier=0)
    if "point_count" not in obs["invariants"] \
            or "in_bounds" not in obs["invariants"]:
        fail("correct observation invariants are %r" % obs["invariants"])
    short = runtime.canonical_visual_response(
        exact, {"kind": "trace_path",
                "points": [{"x": "0", "y": "0"}, {"x": "2", "y": "2"}]})
    if short is not None:
        fail("a short trace response canonicalized (count must be fixed)")
    bad = runtime.visual_observation(
        exact, {"kind": "trace_path",
                "points": [{"x": "0", "y": "0"}]},
        False, hint_tier=None)
    if bad["error_category"] != "wrong_point_count":
        fail("short trace category is %r" % bad["error_category"])
    text = json.dumps(obs)
    if '"accepted"' in text or re.search(r'"tolerance"\s*:', text):
        fail("observation leaks private scoring material")
    ok("observation: point_count/in_bounds + wrong_point_count, leak-free")


# ---- 5. lint ----------------------------------------------------------------

def check_lint():
    qs = load_bank()
    errs, warns = model.lint(qs, lesson=model.parse_lesson(BANK))
    codes = [e.code for e in errs]
    if codes:
        fail("advanced fixture does not lint clean: %r" % codes)

    def lint_one(text):
        q = model.parse_bank(text)[0]
        errs, _ = model.lint([q], lesson=None)
        return [e.code for e in errs]

    base = (
        "Q1. Trace a path.   (difficulty: recall)\n"
        "[OBJECTIVE: test:probe]\n"
        "[TYPE: visual]\n[INTERACTION: trace]\n"
        "[VISUAL: {\"version\":1,\"axes\":{\"x\":{\"min\":\"0\",\"max\":\"4\","
        "\"step\":\"1\"},\"y\":{\"min\":\"0\",\"max\":\"4\",\"step\":\"1\"}},"
        "\"point_count\":3,\"initial\":{\"points\":[{\"x\":\"0\",\"y\":\"0\"},"
        "{\"x\":\"2\",\"y\":\"2\"},{\"x\":\"4\",\"y\":\"0\"}]},"
        "\"actions\":[\"place_trace_point\"],"
        "\"accessibility\":{\"description\":\"d\"}}]\n"
        "[SCORING: {\"kind\":\"trace_path\","
        "\"accepted\":[{\"points\":[{\"x\":\"0\",\"y\":\"0\"},"
        "{\"x\":\"2\",\"y\":\"2\"},{\"x\":\"4\",\"y\":\"0\"}]}],"
        "\"tolerance\":{\"x\":\"0\",\"y\":\"0\"},\"partial_credit\":false}]\n"
        "WHY BEST: The points reproduce the reference path exactly.\n")
    if lint_one(base):
        fail("valid trace item did not lint clean: %r" % lint_one(base))
    bad_count = base.replace('"point_count":3', '"point_count":0')
    codes = lint_one(bad_count)
    if "item.visual_invalid_geometry" not in codes:
        fail("point_count 0 did not yield visual_invalid_geometry: %r" % codes)
    bad_ref = base.replace(
        '{"x":"4","y":"0"}]}', '{"x":"4","y":"0"},{"x":"5","y":"0"}]}')
    codes = lint_one(bad_ref)
    if "item.visual_invalid_geometry" not in codes:
        fail("reference polyline mismatching point_count did not yield "
             "visual_invalid_geometry: %r" % codes)
    ok("lint: trace point_count/reference grammar, geometry codes named")


# ---- 6. committed action + evidence -----------------------------------------

def run(args, cwd):
    r = subprocess.run([sys.executable, ITEMBANK] + args, cwd=cwd,
                       capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        fail("itembank %s exited %d: %s" % (" ".join(args), r.returncode,
                                            (r.stderr or r.stdout)[-800:]))
    return json.loads(r.stdout)


def load_log(work):
    path = os.path.join(work, "_evidence", "evidence.jsonl")
    if not os.path.exists(path):
        return []
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def fresh_session(work):
    isolated = os.path.join(work, "advanced_visual_bank.md")
    shutil.copyfile(BANK, isolated)
    started = run(["start", isolated, "--count", "12", "--mode", "practice",
                   "--out", os.path.join(work, "session.json")], work)
    session_file = started["session_file"]
    qs = load_bank(isolated)
    return session_file, qs


def item_at(session_file, qs):
    data = runtime.read_session(session_file)
    return qs[data["items"][data["cursor"]]]


def _correct_for(q):
    if q["interaction"] == "trace":
        return json.dumps({"kind": "trace_path",
                           "points": q["scoring"]["accepted"][0]["points"]})
    if q["interaction"] == "diagram":
        return json.dumps({"kind": "diagram_connection", "from": "a",
                           "to": "c"})
    if q["interaction"] == "timeline":
        return json.dumps({"kind": "timeline_event",
                           "event": q["scoring"]["accepted"][0]["event"],
                           "value": q["scoring"]["accepted"][0]["value"]})
    if q["interaction"] == "hotspot":
        return json.dumps({"kind": "hotspot",
                           "region": q["scoring"]["accepted"][0]["region"]})
    if q["interaction"] == "plot":
        return json.dumps({"kind": "point", "x": "2", "y": "3"})
    if q["scoring"]["kind"] == "interval":
        return json.dumps({"kind": "interval", "start": "-1", "end": "3/2",
                           "start_closed": True, "end_closed": False})
    return json.dumps({"kind": "numberline_point",
                       "value": "3/2" if q["number"] == 4 else "1/2"})


def advance_to(session_file, qs, number):
    for _ in range(18):
        if item_at(session_file, qs)["number"] == number:
            return session_file
        session_surface.do_submit(session_file, _correct_for(item_at(session_file, qs)),
                                  None)
    fail("session never reached item %d" % number)


def session_actions(work, session_file):
    data = runtime.read_session(session_file)
    return [ev for ev in load_log(work)
            if ev.get("event_type") == "visual_action"
            and ev.get("session_id") == data["session_id"]]


def check_interact_evidence(work):
    session_file, qs = fresh_session(work)
    advance_to(session_file, qs, 11)     # the exact trace item
    q = item_at(session_file, qs)
    full = {"kind": "trace_path",
            "points": [{"x": "0", "y": "0"}, {"x": "2", "y": "2"},
                       {"x": "4", "y": "0"}]}

    first = session_surface.do_interact(session_file, {
        "interaction_version": runtime.VISUAL_PROTOCOL_VERSION,
        "action_id": ACTION_ID, "action_type": "place_trace_point",
        "state": full})
    if first.get("status") != "recorded":
        fail("first trace commit status is %r" % first["status"])
    events = session_actions(work, session_file)
    if len(events) != 1:
        fail("expected exactly one visual_action event, found %d" % len(events))
    ev = events[0]
    if ev["action_type"] != "place_trace_point":
        fail("event action_type is %r" % ev["action_type"])
    if ev["after_state"] != full:
        fail("event after_state is %r" % ev["after_state"])
    blob = json.dumps(ev)
    for banned in ("pointer", "clientX", "getBoundingClientRect", "screenshot",
                   "accepted", "tolerance", "answer_key", "verdict"):
        if banned in blob:
            fail("visual_action event carries banned material %r" % banned)

    # A changed path commits as move_trace_point with before/after.
    moved = {"kind": "trace_path",
             "points": [{"x": "0", "y": "0"}, {"x": "2", "y": "1"},
                        {"x": "4", "y": "0"}]}
    second = session_surface.do_interact(session_file, {
        "interaction_version": runtime.VISUAL_PROTOCOL_VERSION,
        "action_id": "123e4567-e89b-42d3-a456-426614174001",
        "action_type": "move_trace_point", "state": moved})
    if second.get("status") != "recorded":
        fail("move commit status is %r" % second["status"])
    events = session_actions(work, session_file)
    moved_ev = events[-1]
    if moved_ev["action_type"] != "move_trace_point" \
            or moved_ev["before_state"] != full \
            or moved_ev["after_state"] != moved:
        fail("move event before/after is wrong: %r" % moved_ev)

    replay = session_surface.do_interact(session_file, {
        "interaction_version": runtime.VISUAL_PROTOCOL_VERSION,
        "action_id": "123e4567-e89b-42d3-a456-426614174001",
        "action_type": "move_trace_point", "state": moved})
    if replay["status"] != "already_recorded":
        fail("identical retry status is %r" % replay["status"])
    try:
        session_surface.do_interact(session_file, {
            "interaction_version": runtime.VISUAL_PROTOCOL_VERSION,
            "action_id": "123e4567-e89b-42d3-a456-426614174002",
            "action_type": "move_trace_point",
            "state": {"kind": "trace_path",
                      "points": [{"x": "0", "y": "0"}, {"x": "2", "y": "2"}]}})
        fail("short trace state was not refused")
    except SystemExit:
        pass
    ok("interact/evidence: place then move full-path commits, before/after, "
       "dedupe, short-path refusal")


def check_schemas(work):
    session_file, qs = fresh_session(work)
    advance_to(session_file, qs, 11)
    q = item_at(session_file, qs)
    full = {"kind": "trace_path",
            "points": [{"x": "0", "y": "0"}, {"x": "2", "y": "2"},
                       {"x": "4", "y": "0"}]}
    result = session_surface.do_interact(session_file, {
        "interaction_version": runtime.VISUAL_PROTOCOL_VERSION,
        "action_id": ACTION_ID, "action_type": "place_trace_point",
        "state": full})
    doc = json.load(open(os.path.join(ROOT, "schemas",
                                      "visual_interaction.schema.json"),
                         encoding="utf-8"))
    errs = schema_validate.validate(
        {"session_id": runtime.read_session(session_file)["session_id"],
         "interaction_version": runtime.VISUAL_PROTOCOL_VERSION,
         "action_id": ACTION_ID, "action_type": "place_trace_point",
         "state": full}, doc)
    if errs:
        fail("interact_request schema: %s" % errs[0])
    errs = schema_validate.validate(result["observation"], doc)
    if errs:
        fail("observation schema: %s" % errs[0])
    ev = session_actions(work, session_file)[-1]
    errs = schema_validate.validate(ev, doc)
    if errs:
        fail("visual_action_event schema: %s" % errs[0])
    item_doc = json.load(open(os.path.join(ROOT, "schemas",
                                           "item.schema.json"),
                              encoding="utf-8"))
    errs = schema_validate.validate(runtime.public_item(q), item_doc)
    if errs:
        fail("item.schema.json visual branch: %s" % errs[0])
    ok("schemas: trace request/observation/event/public item validate")


# ---- 7. served renderer + offline refusal -----------------------------------

def _correct_for_served(q):
    interaction = (q.get("interaction_contract") or {}).get("interaction")
    if interaction == "trace":
        if q["number"] == 11:
            pts = [{"x": "0", "y": "0"}, {"x": "2", "y": "2"},
                   {"x": "4", "y": "0"}]
        else:
            pts = [{"x": "0", "y": "2"}, {"x": "2", "y": "0"},
                   {"x": "4", "y": "2"}]
        return json.dumps({"kind": "trace_path", "points": pts})
    if interaction == "diagram":
        return json.dumps({"kind": "diagram_connection", "from": "a",
                           "to": "c"})
    if interaction == "timeline":
        if q["number"] == 8:
            return json.dumps({"kind": "timeline_event", "event": "fall",
                               "value": "5"})
        return json.dumps({"kind": "timeline_event", "event": "industrial",
                           "value": "7"})
    if interaction == "hotspot":
        return json.dumps({"kind": "hotspot",
                           "region": {5: "heart", 6: "montana",
                                      7: "ring"}[q["number"]]})
    if q["number"] == 1:
        return json.dumps({"kind": "point", "x": "2", "y": "3"})
    if q["number"] == 3:
        return json.dumps({"kind": "interval", "start": "-1", "end": "3/2",
                           "start_closed": True, "end_closed": False})
    return json.dumps({"kind": "numberline_point",
                       "value": "3/2" if q["number"] == 4 else "1/2"})


def check_served():
    work = tempfile.mkdtemp()
    proc = None
    try:
        isolated = os.path.join(work, "advanced_visual_bank.md")
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
        stem = os.path.splitext(os.path.basename(isolated))[0]
        html = urllib.request.urlopen(
            base + "quiz/%s" % stem, timeout=5).read().decode("utf-8")
        for marker in ("function renderTrace", '"place_trace_point"',
                       '"move_trace_point"'):
            if marker not in html:
                fail("served page is missing %r" % marker)
        if "<canvas" in html:
            fail("served page uses canvas for the trace slice")

        start = api(base, "start", {"bank": stem, "mode": "practice", "count": 12})
        if start["status"] != "active":
            fail("POST /api/start did not return an active session")
        sid = start["session_id"]
        seen = set()
        for _ in range(12):
            cur = api(base, "next", {"session_id": sid}) if seen else start
            q = cur["item"]
            if q["number"] in seen:
                fail("session served item %d twice" % q["number"])
            seen.add(q["number"])
            v = api(base, "submit", {"session_id": sid,
                                     "answer": _correct_for_served(q)})
            if v.get("score") is not True:
                fail("served submit of Q%d returned score %r"
                     % (q["number"], v.get("score")))
        if seen != set(range(1, 13)):
            fail("sitting did not serve every fixture item: %s" % sorted(seen))
    finally:
        if proc:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
        shutil.rmtree(work, ignore_errors=True)
    ok("served: renderTrace dispatch, no canvas, full 12-item sitting scores")


def check_offline():
    work = tempfile.mkdtemp()
    try:
        isolated = os.path.join(work, "advanced_visual_bank.md")
        shutil.copyfile(BANK, isolated)
        out = os.path.join(work, "out.html")
        r = subprocess.run(
            [sys.executable, ITEMBANK, "build", isolated, out, "--force"],
            capture_output=True, text=True, encoding="utf-8")
        if r.returncode != 0:
            fail("static build of the advanced bank failed: %s"
                 % (r.stderr or r.stdout)[-500:])
        html = open(out, encoding="utf-8").read()
        if "needs a served itembank session" not in html:
            fail("static build page has no served-runtime-required refusal")
        for banned in ('"accepted"', '"tolerance"', '"partial_credit"',
                       '"key"'):
            if banned in html:
                fail("static build page leaks %s" % banned)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    ok("offline: trace items refuse loudly, no key/scoring material")


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
    tr = check_parser()
    check_public(tr)
    check_scoring(tr)
    check_observation(tr)
    check_lint()
    work = tempfile.mkdtemp()
    try:
        check_interact_evidence(work)
        check_schemas(work)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    check_served()
    check_offline()
    print("PASS trace_roundtrip.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
