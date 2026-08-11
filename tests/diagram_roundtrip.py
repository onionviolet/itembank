#!/usr/bin/env python3
"""Plan 999.1-03 tracer (diagram): the diagram_connection family, end to end.

Drives the additive protocol-1 extension for node connection through every
layer: parser -> key-free public contract -> canonical
{"kind":"diagram_connection","from":ID,"to":ID} response ->
runtime.score_response (ordered pair, no self-loops, known nodes only) ->
runtime-bounded observation (known_nodes, distinct_nodes, unknown_node) ->
committed connect_diagram action via session.do_interact -> one visual_action
event.

It also pins the closed scene grammar (plane + nodes with unique ids and
in-plane coordinates), schema validation, the served renderer dispatch
(renderDiagram, no canvas), the static offline refusal, and GIFT's loud
refusal of diagram items.

Standard library only, no test framework, runnable as
`python tests/diagram_roundtrip.py`.
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


def diagram_items(qs):
    return [q for q in qs if q["type"] == "visual"
            and q["interaction"] == "diagram"]


# ---- 1. parser --------------------------------------------------------------

def check_parser():
    qs = load_bank()
    visual = [q for q in qs if q["type"] == "visual"]
    if len(visual) != 12:
        fail("expected 12 visual items, parsed %d" % len(visual))
    dg = diagram_items(qs)
    if len(dg) != 1:
        fail("expected 1 diagram item, parsed %d" % len(dg))
    return dg[0]


# ---- 2. key-free public contract --------------------------------------------

def check_public(q):
    item = runtime.public_item(q)
    assert_public_payload_clean(item, "public_item")
    c = item["interaction_contract"]
    if c["version"] != runtime.VISUAL_PROTOCOL_VERSION \
            or c["interaction"] != "diagram":
        fail("diagram contract header wrong: %r" % c)
    if c["response_schema"]["kind"] != "diagram_connection":
        fail("diagram response_schema kind is %r" % c["response_schema"]["kind"])
    rc = c["renderer_config"]
    for key in ("plane", "nodes", "initial", "actions", "accessibility"):
        if key not in rc:
            fail("diagram renderer_config missing %r" % key)
    if set(rc["plane"]) != {"width", "height"}:
        fail("diagram plane is %r" % rc["plane"])
    for n in rc["nodes"]:
        if set(n) != {"id", "label", "x", "y"}:
            fail("diagram node shape is %r" % n)
    ok("public contract: key-free diagram scene (plane/nodes/actions/accessibility)")


# ---- 3. scoring: ordered pair, no self-loops --------------------------------

def check_scoring(q):
    if not runtime.score_response(q, {"kind": "diagram_connection",
                                      "from": "a", "to": "c"}):
        fail("accepted connection a->c did not score True")
    if runtime.score_response(q, {"kind": "diagram_connection",
                                  "from": "b", "to": "c"}):
        fail("wrong premise b->c scored True")
    if runtime.score_response(q, {"kind": "diagram_connection",
                                  "from": "c", "to": "a"}):
        fail("reversed connection c->a scored True")
    if runtime.score_response(q, {"kind": "diagram_connection",
                                  "from": "a", "to": "a"}):
        fail("self-loop a->a scored True")
    if runtime.score_response(q, {"kind": "diagram_connection",
                                  "from": "nope", "to": "c"}):
        fail("unknown node scored True")
    if runtime.score_response(q, {"kind": "diagram_connection", "from": "a",
                                  "to": "c", "score": True}):
        fail("forged authority field influenced the verdict")
    for bad in ({"kind": "diagram_connection", "from": "a"},
                {"kind": "diagram_connection", "from": "a", "to": "c",
                 "extra": 1},
                {"kind": "hotspot", "region": "a"},
                "not a response", None):
        if runtime.score_response(q, bad) is not False:
            fail("malformed diagram response %r scored non-False" % (bad,))
    ok("scoring: ordered pair, self-loop/unknown/forged/malformed fail closed")


# ---- 4. observation ---------------------------------------------------------

def check_observation(q):
    state = runtime.canonical_visual_response(
        q, {"kind": "diagram_connection", "from": "a", "to": "c"})
    obs = runtime.visual_observation(q, state, True, hint_tier=0)
    if "known_nodes" not in obs["invariants"] \
            or "distinct_nodes" not in obs["invariants"]:
        fail("correct observation invariants are %r" % obs["invariants"])
    bad = runtime.visual_observation(
        q, runtime.canonical_visual_response(
            q, {"kind": "diagram_connection", "from": "nope", "to": "c"}),
        False, hint_tier=None)
    if bad["error_category"] != "unknown_node":
        fail("unknown node category is %r" % bad["error_category"])
    text = json.dumps(obs)
    if '"accepted"' in text or re.search(r'"tolerance"\s*:', text):
        fail("observation leaks private scoring material")
    ok("observation: known_nodes/distinct_nodes + unknown_node, leak-free")


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

    dup = (
        "Q1. Connect nodes.   (difficulty: recall)\n"
        "[OBJECTIVE: test:probe]\n"
        "[TYPE: visual]\n[INTERACTION: diagram]\n"
        "[VISUAL: {\"version\":1,\"plane\":{\"width\":\"8\",\"height\":\"6\"},"
        "\"nodes\":[{\"id\":\"a\",\"label\":\"A\",\"x\":\"2\",\"y\":\"4\"},"
        "{\"id\":\"a\",\"label\":\"B\",\"x\":\"6\",\"y\":\"4\"}],"
        "\"initial\":{\"connections\":[]},\"actions\":[\"connect_diagram\"],"
        "\"accessibility\":{\"description\":\"d\"}}]\n"
        "[SCORING: {\"kind\":\"diagram_connection\","
        "\"accepted\":[{\"from\":\"a\",\"to\":\"a\"}],"
        "\"tolerance\":{},\"partial_credit\":false}]\n")
    codes = lint_one(dup)
    if "item.visual_duplicate_id" not in codes:
        fail("duplicate node ids did not yield visual_duplicate_id: %r" % codes)

    oob = (
        "Q1. Connect nodes.   (difficulty: recall)\n"
        "[OBJECTIVE: test:probe]\n"
        "[TYPE: visual]\n[INTERACTION: diagram]\n"
        "[VISUAL: {\"version\":1,\"plane\":{\"width\":\"8\",\"height\":\"6\"},"
        "\"nodes\":[{\"id\":\"a\",\"label\":\"A\",\"x\":\"2\",\"y\":\"40\"},"
        "{\"id\":\"b\",\"label\":\"B\",\"x\":\"6\",\"y\":\"4\"}],"
        "\"initial\":{\"connections\":[]},\"actions\":[\"connect_diagram\"],"
        "\"accessibility\":{\"description\":\"d\"}}]\n"
        "[SCORING: {\"kind\":\"diagram_connection\","
        "\"accepted\":[{\"from\":\"a\",\"to\":\"b\"}],"
        "\"tolerance\":{},\"partial_credit\":false}]\n")
    codes = lint_one(oob)
    if "item.visual_invalid_geometry" not in codes:
        fail("out-of-plane node did not yield visual_invalid_geometry: %r"
             % codes)
    ok("lint: diagram nodes closed grammar, duplicate/geometry codes named")


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
    if q["interaction"] == "diagram":
        return json.dumps({"kind": "diagram_connection", "from": "a",
                           "to": "c"})
    if q["interaction"] == "trace":
        acc = q["scoring"]["accepted"][0]["points"]
        return json.dumps({"kind": "trace_path", "points": acc})
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
    advance_to(session_file, qs, 10)     # the diagram item
    q = item_at(session_file, qs)

    result = session_surface.do_interact(session_file, {
        "interaction_version": runtime.VISUAL_PROTOCOL_VERSION,
        "action_id": ACTION_ID, "action_type": "connect_diagram",
        "state": {"kind": "diagram_connection", "from": "a", "to": "c"}})
    if result.get("status") != "recorded":
        fail("first diagram commit status is %r" % result["status"])
    events = session_actions(work, session_file)
    if len(events) != 1:
        fail("expected exactly one visual_action event, found %d" % len(events))
    ev = events[0]
    if ev["action_type"] != "connect_diagram":
        fail("event action_type is %r" % ev["action_type"])
    if ev["after_state"] != {"kind": "diagram_connection", "from": "a",
                             "to": "c"}:
        fail("event after_state is %r" % ev["after_state"])
    blob = json.dumps(ev)
    for banned in ("pointer", "clientX", "getBoundingClientRect", "screenshot",
                   "accepted", "tolerance", "answer_key", "verdict"):
        if banned in blob:
            fail("visual_action event carries banned material %r" % banned)

    replay = session_surface.do_interact(session_file, {
        "interaction_version": runtime.VISUAL_PROTOCOL_VERSION,
        "action_id": ACTION_ID, "action_type": "connect_diagram",
        "state": {"kind": "diagram_connection", "from": "a", "to": "c"}})
    if replay["status"] != "already_recorded":
        fail("identical retry status is %r" % replay["status"])
    try:
        session_surface.do_interact(session_file, {
            "interaction_version": runtime.VISUAL_PROTOCOL_VERSION,
            "action_id": "123e4567-e89b-42d3-a456-426614174001",
            "action_type": "connect_diagram",
            "state": {"kind": "diagram_connection", "from": "a", "to": "a"}})
        fail("self-loop state was not refused")
    except SystemExit:
        pass
    ok("interact/evidence: connect_diagram commits once, dedupes, "
       "self-loop refuses")


def check_schemas(work):
    session_file, qs = fresh_session(work)
    advance_to(session_file, qs, 10)
    q = item_at(session_file, qs)
    result = session_surface.do_interact(session_file, {
        "interaction_version": runtime.VISUAL_PROTOCOL_VERSION,
        "action_id": ACTION_ID, "action_type": "connect_diagram",
        "state": {"kind": "diagram_connection", "from": "a", "to": "c"}})
    doc = json.load(open(os.path.join(ROOT, "schemas",
                                      "visual_interaction.schema.json"),
                         encoding="utf-8"))
    errs = schema_validate.validate(
        {"session_id": runtime.read_session(session_file)["session_id"],
         "interaction_version": runtime.VISUAL_PROTOCOL_VERSION,
         "action_id": ACTION_ID, "action_type": "connect_diagram",
         "state": {"kind": "diagram_connection", "from": "a", "to": "c"}}, doc)
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
    ok("schemas: diagram request/observation/event/public item validate")


# ---- 7. served renderer + offline refusal -----------------------------------

def _correct_for_served(q):
    interaction = (q.get("interaction_contract") or {}).get("interaction")
    if interaction == "diagram":
        return json.dumps({"kind": "diagram_connection", "from": "a",
                           "to": "c"})
    if interaction == "trace":
        if q["number"] == 11:
            pts = [{"x": "0", "y": "0"}, {"x": "2", "y": "2"},
                   {"x": "4", "y": "0"}]
        else:
            pts = [{"x": "0", "y": "2"}, {"x": "2", "y": "0"},
                   {"x": "4", "y": "2"}]
        return json.dumps({"kind": "trace_path", "points": pts})
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
        for marker in ("function renderDiagram", '"connect_diagram"'):
            if marker not in html:
                fail("served page is missing %r" % marker)
        if "<canvas" in html:
            fail("served page uses canvas for the diagram slice")

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
    ok("served: renderDiagram dispatch, no canvas, full 12-item sitting scores")


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
    ok("offline: diagram items refuse loudly, no key/scoring material")


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
    q = check_parser()
    check_public(q)
    check_scoring(q)
    check_observation(q)
    check_lint()
    work = tempfile.mkdtemp()
    try:
        check_interact_evidence(work)
        check_schemas(work)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    check_served()
    check_offline()
    print("PASS diagram_roundtrip.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
