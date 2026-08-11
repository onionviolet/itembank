#!/usr/bin/env python3
"""Plan 999.1-02 tracer: the timeline family, end to end.

Drives the additive protocol-1 extension for time-series placement through
every layer: parser -> key-free public contract -> canonical
{"kind":"timeline_event","event":ID,"value":SCALAR} response ->
runtime.score_response (exact event id + per-coordinate tolerance on value,
with pinned boundaries) -> runtime-bounded observation (known_event,
in_bounds, out_of_domain, off_grid) -> committed place_timeline_event /
move_timeline_event actions via session.do_interact -> one visual_action
event per commit.

It also pins the closed scene grammar (axis + events with unique ids),
schema validation, the served renderer dispatch (renderTimeline, no canvas),
the static offline refusal, and GIFT's loud refusal of timeline items.

Standard library only, no test framework, runnable as
`python tests/timeline_roundtrip.py`.
"""
import json, os, re, shutil, subprocess, sys, tempfile, threading, time
import urllib.error, urllib.request


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ITEMBANK = os.path.join(ROOT, "itembank.py")
BANK = os.path.join(ROOT, "fixtures", "advanced_visual_bank.md")
sys.path.insert(0, ROOT)

import evidence                                        # noqa: E402
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


def timeline_items(qs):
    return [q for q in qs if q["type"] == "visual"
            and q["interaction"] == "timeline"]


# ---- 1. parser --------------------------------------------------------------

def check_parser():
    qs = load_bank()
    visual = [q for q in qs if q["type"] == "visual"]
    if len(visual) != 9:
        fail("expected 9 visual items, parsed %d" % len(visual))
    tl = timeline_items(qs)
    if len(tl) != 2:
        fail("expected 2 timeline items, parsed %d" % len(tl))
    for q in tl:
        if not isinstance(q.get("visual"), dict) \
                or not isinstance(q.get("scoring"), dict):
            fail("timeline scene/scoring not parsed as dict for Q%d" % q["number"])
    return tl


# ---- 2. key-free public contract --------------------------------------------

def check_public(tl):
    for q in tl:
        item = runtime.public_item(q)
        assert_public_payload_clean(item, "public_item")
        c = item["interaction_contract"]
        if c["version"] != runtime.VISUAL_PROTOCOL_VERSION \
                or c["interaction"] != "timeline":
            fail("timeline contract header wrong: %r" % c)
        if c["response_schema"]["kind"] != "timeline_event":
            fail("timeline response_schema kind is %r"
                 % c["response_schema"]["kind"])
        rc = c["renderer_config"]
        for key in ("axis", "events", "initial", "actions", "accessibility"):
            if key not in rc:
                fail("timeline renderer_config missing %r" % key)
        if set(rc["axis"]) != {"min", "max", "step", "ticks"}:
            fail("timeline axis is %r" % rc["axis"])
        for ev in rc["events"]:
            if set(ev) != {"id", "label"}:
                fail("timeline event shape is %r" % ev)
        if rc["actions"] != ["place_timeline_event", "move_timeline_event"]:
            fail("timeline actions are %r" % rc["actions"])
    ok("public contract: key-free timeline scene (axis/events/actions/accessibility)")
    return tl


# ---- 3. scoring: event id exact, value tolerance ----------------------------

def check_scoring(tl):
    exact, tol = tl
    # Exact placement.
    if not runtime.score_response(exact, {"kind": "timeline_event",
                                          "event": "fall", "value": "5"}):
        fail("Q%d accepted placement did not score True" % exact["number"])
    if runtime.score_response(exact, {"kind": "timeline_event",
                                      "event": "fall", "value": "8"}):
        fail("exact item with wrong value scored True")
    if runtime.score_response(exact, {"kind": "timeline_event",
                                      "event": "printing", "value": "5"}):
        fail("exact item with wrong event scored True")
    if runtime.score_response(exact, {"kind": "timeline_event",
                                      "event": "fall", "value": "5",
                                      "score": True, "hint_tier": 5}):
        fail("forged authority fields influenced the verdict")
    if runtime.score_response(exact, {"kind": "timeline_event",
                                      "event": "nope", "value": "5"}):
        fail("unknown event scored True")
    if runtime.score_response(exact, {"kind": "timeline_event",
                                      "event": "fall", "value": "15"}):
        fail("out-of-axis value scored True")

    # Tolerance: [6, 8] pass (boundaries inclusive), 5 and 9 fail.
    for value in ("6", "7", "8"):
        if not runtime.score_response(tol, {"kind": "timeline_event",
                                            "event": "industrial",
                                            "value": value}):
            fail("tolerance value %s should pass" % value)
    for value in ("5", "9"):
        if runtime.score_response(tol, {"kind": "timeline_event",
                                        "event": "industrial",
                                        "value": value}):
            fail("tolerance value %s (adjacent to boundary) passed" % value)

    # Malformed responses fail closed.
    for bad in ({"kind": "timeline_event", "event": "fall"},
                {"kind": "timeline_event", "value": "5"},
                {"kind": "timeline_event", "event": "fall", "value": "1e3"},
                {"kind": "timeline_event", "event": "fall", "value": "x"},
                {"kind": "hotspot", "region": "heart"},
                "not a response", None):
        if runtime.score_response(exact, bad) is not False:
            fail("malformed timeline response %r scored non-False" % (bad,))
    for bad_event in ("x" * 65, "a b", ""):
        if runtime.score_response(exact, {"kind": "timeline_event",
                                          "event": bad_event,
                                          "value": "5"}) is not False:
            fail("identifier %r was accepted" % bad_event)
    ok("scoring: exact event id, tolerance borders 6/7/8 pass 5/9 fail, "
       "invalid/forged fail closed")


# ---- 4. observation ---------------------------------------------------------

def check_observation(tl):
    exact = tl[0]
    state = runtime.canonical_visual_response(
        exact, {"kind": "timeline_event", "event": "fall", "value": "5"})
    obs = runtime.visual_observation(exact, state, True, hint_tier=0)
    if "known_event" not in obs["invariants"] or "in_bounds" not in obs["invariants"]:
        fail("correct observation invariants are %r" % obs["invariants"])
    if obs["error_category"] not in (None, "ok"):
        fail("correct observation error_category is %r" % obs["error_category"])
    bad = runtime.visual_observation(
        exact, runtime.canonical_visual_response(
            exact, {"kind": "timeline_event", "event": "nope", "value": "5"}),
        False, hint_tier=None)
    if bad["error_category"] != "unknown_event":
        fail("unknown event category is %r" % bad["error_category"])
    oob = runtime.visual_observation(
        exact, runtime.canonical_visual_response(
            exact, {"kind": "timeline_event", "event": "fall", "value": "15"}),
        False, hint_tier=None)
    if oob["error_category"] != "out_of_domain":
        fail("out-of-axis category is %r" % oob["error_category"])
    text = json.dumps(obs)
    if '"accepted"' in text or re.search(r'"tolerance"\s*:', text):
        fail("observation leaks private scoring material")
    ok("observation: known_event/in_bounds + unknown_event/out_of_domain, leak-free")


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

    # Duplicate event ids.
    dup = (
        "Q1. Place an event.   (difficulty: recall)\n"
        "[OBJECTIVE: test:probe]\n"
        "[TYPE: visual]\n[INTERACTION: timeline]\n"
        "[VISUAL: {\"version\":1,\"axis\":{\"min\":\"0\",\"max\":\"10\","
        "\"step\":\"1\"},\"events\":[{\"id\":\"e1\",\"label\":\"A\"},"
        "{\"id\":\"e1\",\"label\":\"B\"}],\"initial\":{\"placements\":[]},"
        "\"actions\":[\"place_timeline_event\"],"
        "\"accessibility\":{\"description\":\"d\"}}]\n"
        "[SCORING: {\"kind\":\"timeline_event\","
        "\"accepted\":[{\"event\":\"e1\",\"value\":\"5\"}],"
        "\"tolerance\":{\"value\":\"0\"},\"partial_credit\":false}]\n")
    if "item.visual_duplicate_id" not in lint_one(dup):
        fail("duplicate event ids did not yield visual_duplicate_id")

    # Invalid axis on a timeline item.
    bad_axis = dup.replace('"max":"10"', '"max":"10.5"')
    if "item.visual_invalid_axis" not in lint_one(bad_axis):
        fail("invalid timeline axis did not yield visual_invalid_axis")
    ok("lint: timeline events/axis closed grammar, duplicate/axis codes named")


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
    started = run(["start", isolated, "--count", "9", "--mode", "practice",
                   "--out", os.path.join(work, "session.json")], work)
    session_file = started["session_file"]
    qs = load_bank(isolated)
    return session_file, qs


def item_at(session_file, qs):
    data = runtime.read_session(session_file)
    return qs[data["items"][data["cursor"]]]


def _correct_for(q):
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
    for _ in range(14):
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
    advance_to(session_file, qs, 8)      # first timeline item
    q = item_at(session_file, qs)

    first = session_surface.do_interact(session_file, {
        "interaction_version": runtime.VISUAL_PROTOCOL_VERSION,
        "action_id": ACTION_ID, "action_type": "place_timeline_event",
        "state": {"kind": "timeline_event", "event": "fall", "value": "5"}})
    if first.get("status") != "recorded":
        fail("first timeline commit status is %r" % first["status"])
    events = session_actions(work, session_file)
    if len(events) != 1:
        fail("expected exactly one visual_action event, found %d" % len(events))
    ev = events[0]
    if ev["action_type"] != "place_timeline_event":
        fail("event action_type is %r" % ev["action_type"])
    if ev["after_state"] != {"kind": "timeline_event", "event": "fall",
                             "value": "5"}:
        fail("event after_state is %r" % ev["after_state"])
    blob = json.dumps(ev)
    for banned in ("pointer", "clientX", "getBoundingClientRect", "screenshot",
                   "accepted", "tolerance", "answer_key", "verdict"):
        if banned in blob:
            fail("visual_action event carries banned material %r" % banned)

    # A changed placement commits as move_timeline_event with before/after.
    second = session_surface.do_interact(session_file, {
        "interaction_version": runtime.VISUAL_PROTOCOL_VERSION,
        "action_id": "123e4567-e89b-42d3-a456-426614174001",
        "action_type": "move_timeline_event",
        "state": {"kind": "timeline_event", "event": "fall", "value": "6"}})
    if second.get("status") != "recorded":
        fail("move commit status is %r" % second["status"])
    events = session_actions(work, session_file)
    if len(events) != 2:
        fail("expected two visual_action events, found %d" % len(events))
    moved = events[-1]
    if moved["action_type"] != "move_timeline_event" \
            or moved["before_state"] != {"kind": "timeline_event",
                                         "event": "fall", "value": "5"} \
            or moved["after_state"] != {"kind": "timeline_event",
                                        "event": "fall", "value": "6"}:
        fail("move event before/after is wrong: %r" % moved)

    # Identical retry dedupes; unknown event refuses.
    replay = session_surface.do_interact(session_file, {
        "interaction_version": runtime.VISUAL_PROTOCOL_VERSION,
        "action_id": "123e4567-e89b-42d3-a456-426614174001",
        "action_type": "move_timeline_event",
        "state": {"kind": "timeline_event", "event": "fall", "value": "6"}})
    if replay["status"] != "already_recorded":
        fail("identical retry status is %r" % replay["status"])
    try:
        session_surface.do_interact(session_file, {
            "interaction_version": runtime.VISUAL_PROTOCOL_VERSION,
            "action_id": "123e4567-e89b-42d3-a456-426614174002",
            "action_type": "move_timeline_event",
            "state": {"kind": "timeline_event", "event": "nope", "value": "6"}})
        fail("unknown event state was not refused")
    except SystemExit:
        pass
    ok("interact/evidence: place then move, before/after states, dedupe, refusal")


def check_schemas(work):
    session_file, qs = fresh_session(work)
    advance_to(session_file, qs, 8)
    q = item_at(session_file, qs)
    result = session_surface.do_interact(session_file, {
        "interaction_version": runtime.VISUAL_PROTOCOL_VERSION,
        "action_id": ACTION_ID, "action_type": "place_timeline_event",
        "state": {"kind": "timeline_event", "event": "fall", "value": "5"}})
    doc = json.load(open(os.path.join(ROOT, "schemas",
                                      "visual_interaction.schema.json"),
                         encoding="utf-8"))
    errs = schema_validate.validate(
        {"session_id": runtime.read_session(session_file)["session_id"],
         "interaction_version": runtime.VISUAL_PROTOCOL_VERSION,
         "action_id": ACTION_ID, "action_type": "place_timeline_event",
         "state": {"kind": "timeline_event", "event": "fall", "value": "5"}}, doc)
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
    ok("schemas: timeline request/observation/event/public item validate")


# ---- 7. served renderer + offline refusal -----------------------------------

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
        for marker in ("function renderTimeline", '"place_timeline_event"',
                       '"move_timeline_event"'):
            if marker not in html:
                fail("served page is missing %r" % marker)
        if "<canvas" in html:
            fail("served page uses canvas for the timeline slice")

        start = api(base, "start", {"bank": stem, "mode": "practice", "count": 9})
        if start["status"] != "active":
            fail("POST /api/start did not return an active session")
        sid = start["session_id"]
        seen = set()
        for _ in range(9):
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
        if seen != set(range(1, 10)):
            fail("sitting did not serve every fixture item: %s" % sorted(seen))
    finally:
        if proc:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
        shutil.rmtree(work, ignore_errors=True)
    ok("served: renderTimeline dispatch, no canvas, full 9-item sitting scores")


def _correct_for_served(q):
    interaction = (q.get("interaction_contract") or {}).get("interaction")
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
    ok("offline: timeline items refuse loudly, no key/scoring material")


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
    tl = check_parser()
    check_public(tl)
    check_scoring(tl)
    check_observation(tl)
    check_lint()
    work = tempfile.mkdtemp()
    try:
        check_interact_evidence(work)
        check_schemas(work)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    check_served()
    check_offline()
    print("PASS timeline_roundtrip.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
