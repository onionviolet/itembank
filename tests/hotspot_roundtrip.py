#!/usr/bin/env python3
"""Plan 999.1-01 tracer: the hotspot family, end to end.

Drives the additive protocol-1 extension for click-on-region mapping through
every layer:

  parser (model.parse_bank) -> key-free public contract (runtime.public_item)
  -> canonical {"kind":"hotspot","region":ID} response -> runtime.score_response
  -> interaction_result + runtime-bounded observation (known_region /
     unknown_region) -> committed select_hotspot action via
     session.do_interact -> one visual_action evidence event.

It also pins the exact-id scoring rule (wrong region, unknown region, forged
fields, and the wrong response kind all score False), the closed scene grammar
(plane/regions/initial/actions/accessibility only; rect/circle/polygon
geometry inside the plane; unique ids), the new lint codes
(item.visual_invalid_geometry, item.visual_duplicate_id), schema validation,
the served renderer dispatch (renderHotspot, no canvas), the static offline
refusal, and GIFT's loud refusal of hotspot items.

Standard library only, no test framework, runnable as
`python tests/hotspot_roundtrip.py`.
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
import surfaces.quiz as quiz_surface                   # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def ok(msg):
    print("ok: " + msg)


ACTION_ID = "123e4567-e89b-42d3-a456-426614174000"

# The private scoring sentinels a public payload must never carry.
PRIVATE_SENTINELS = ("accepted", "tolerance", "partial_credit", "scoring",
                     "model", "why", "disc", "second", "trap", "da",
                     "reveal", "solution")


def assert_public_payload_clean(payload, label):
    text = json.dumps(payload, sort_keys=True)
    for sentinel in PRIVATE_SENTINELS:
        if re.search(r'"%s"\s*:' % re.escape(sentinel), text):
            fail("%s: public payload leaks private sentinel %r" % (label, sentinel))


def load_bank(path=BANK):
    qs = model.parse_bank(open(path, encoding="utf-8").read())
    return qs


def hotspot_items(qs):
    return [q for q in qs if q["type"] == "visual"
            and q["interaction"] == "hotspot"]


# ---- 1. parser --------------------------------------------------------------

def check_parser():
    qs = load_bank()
    visual = [q for q in qs if q["type"] == "visual"]
    if len(visual) != 12:
        fail("expected 12 visual items, parsed %d" % len(visual))
    hs = hotspot_items(qs)
    if len(hs) != 3:
        fail("expected 3 hotspot items, parsed %d" % len(hs))
    for q in hs:
        if not isinstance(q.get("visual"), dict) \
                or not isinstance(q.get("scoring"), dict):
            fail("hotspot scene/scoring not parsed as dict for Q%d" % q["number"])
        if "<script" in json.dumps(q.get("visual")):
            fail("Q%d: scene carries a script-bearing member" % q["number"])
    # The carried-over plot/numberline items are byte-compatible (D-999.1-01).
    plot = next(q for q in visual if q["interaction"] == "plot")
    if runtime.public_item(plot)["interaction_contract"]["version"] != 1:
        fail("carried-over plot item changed protocol version")
    return hs


# ---- 2. key-free public contract --------------------------------------------

def check_public(hs):
    for q in hs:
        item = runtime.public_item(q)
        assert_public_payload_clean(item, "public_item")
        c = item["interaction_contract"]
        if c["version"] != runtime.VISUAL_PROTOCOL_VERSION:
            fail("hotspot contract version is %r" % c["version"])
        if c["type"] != "visual":
            fail("hotspot contract type is %r" % c["type"])
        if c["interaction"] != "hotspot":
            fail("hotspot contract interaction is %r" % c["interaction"])
        if c["response_schema"]["kind"] != "hotspot":
            fail("hotspot response_schema kind is %r" % c["response_schema"]["kind"])
        rc = c["renderer_config"]
        for key in ("plane", "regions", "initial", "actions", "accessibility"):
            if key not in rc:
                fail("hotspot renderer_config missing %r" % key)
        if set(rc["plane"]) != {"width", "height"}:
            fail("hotspot plane is %r" % rc["plane"])
        if rc["actions"] != ["select_hotspot"]:
            fail("hotspot actions are %r" % rc["actions"])
        if not rc["accessibility"]["description"]:
            fail("hotspot scene has no accessible description")
        for reg in rc["regions"]:
            if set(reg) != {"id", "label", "shape", "coords"}:
                fail("hotspot region shape is %r" % reg)
    ok("public contract: key-free hotspot scene (plane/regions/actions/accessibility)")
    return hs


# ---- 3. scoring: exact region id --------------------------------------------

def check_scoring(hs):
    for q in hs:
        rid = q["scoring"]["accepted"][0]["region"]
        if not runtime.score_response(q, {"kind": "hotspot", "region": rid}):
            fail("Q%d accepted region %r did not score True" % (q["number"], rid))
    # Wrong region, unknown region, forged fields, wrong kind all fail.
    q = hs[0]
    if runtime.score_response(q, {"kind": "hotspot", "region": "liver"}):
        fail("wrong region scored True")
    if runtime.score_response(q, {"kind": "hotspot", "region": "nope"}):
        fail("unknown region scored True")
    if runtime.score_response(q, {"kind": "hotspot", "region": "heart",
                                  "score": True, "hint_tier": 5}):
        fail("forged authority fields influenced the verdict")
    if runtime.score_response(q, {"kind": "point", "x": "2", "y": "3"}):
        fail("wrong response kind scored True")
    for bad in ("heart", 5, None, {"kind": "hotspot"}, {"kind": "hotspot",
                                                        "region": "b ad"}):
        if runtime.score_response(q, bad) is not False:
            fail("malformed hotspot response %r scored non-False" % (bad,))
    # Decimal-id / oversized-id rejections via the identifier grammar.
    for bad_id in ("x" * 65, "a b", "a/b", ""):
        if runtime.score_response(q, {"kind": "hotspot", "region": bad_id}) is not False:
            fail("identifier %r was accepted" % bad_id)
    ok("scoring: exact region id, forged/unknown/malformed all fail closed")


# ---- 4. observation ---------------------------------------------------------

def check_observation(hs):
    q = hs[0]
    state = runtime.canonical_visual_response(q, {"kind": "hotspot", "region": "heart"})
    obs = runtime.visual_observation(q, state, True, hint_tier=0)
    if obs["error_category"] not in (None, "ok"):
        fail("correct observation error_category is %r" % obs["error_category"])
    if "known_region" not in obs["invariants"]:
        fail("correct observation lacks known_region: %r" % obs["invariants"])
    if obs["hint_tier"] != 0:
        fail("observation hint_tier is %r, expected the supplied entitlement 0"
             % obs["hint_tier"])
    bad = runtime.canonical_visual_response(q, {"kind": "hotspot", "region": "nope"})
    obs2 = runtime.visual_observation(q, bad, False, hint_tier=None)
    if obs2["error_category"] != "unknown_region":
        fail("unknown region observation category is %r" % obs2["error_category"])
    text = json.dumps(obs)
    if '"accepted"' in text or re.search(r'"tolerance"\s*:', text):
        fail("observation leaks private scoring material")
    result = runtime.interaction_result(q, state, True, [obs])
    if result["version"] != runtime.VISUAL_PROTOCOL_VERSION \
            or result["type"] != "visual" or result["verdict"] is not True:
        fail("interaction_result shape is wrong: %r" % result)
    assert_public_payload_clean(result, "interaction_result")
    ok("observation/result: known_region + unknown_region, bounded, leak-free")


# ---- 5. lint: closed grammar, new codes -------------------------------------

def check_lint(hs):
    qs = load_bank()
    errs, warns = model.lint(qs, lesson=model.parse_lesson(BANK))
    codes = [e.code for e in errs]
    if codes:
        fail("advanced fixture does not lint clean: %r" % codes)

    # A malformed geometry must name the field with item.visual_invalid_geometry.
    bad_geom = (
        "Q1. Select a region.   (difficulty: recall)\n"
        "[OBJECTIVE: test:probe]\n"
        "[TYPE: visual]\n[INTERACTION: hotspot]\n"
        "[VISUAL: {\"version\":1,\"plane\":{\"width\":\"10\",\"height\":\"6\"},"
        "\"regions\":[{\"id\":\"r1\",\"label\":\"R\",\"shape\":\"rect\","
        "\"coords\":[\"0\",\"0\",\"2\"]}],\"initial\":{\"region\":null},"
        "\"actions\":[\"select_hotspot\"],\"accessibility\":{\"description\":\"d\"}}]\n"
        "[SCORING: {\"kind\":\"hotspot\",\"accepted\":[{\"region\":\"r1\"}],"
        "\"tolerance\":{},\"partial_credit\":false}]\n")
    q = model.parse_bank(bad_geom)[0]
    errs, _ = model.lint([q], lesson=None)
    if "item.visual_invalid_geometry" not in [e.code for e in errs]:
        fail("malformed hotspot geometry did not yield item.visual_invalid_geometry: %r"
             % [e.code for e in errs])

    # Duplicate region ids.
    bad_dup = (
        "Q1. Select a region.   (difficulty: recall)\n"
        "[OBJECTIVE: test:probe]\n"
        "[TYPE: visual]\n[INTERACTION: hotspot]\n"
        "[VISUAL: {\"version\":1,\"plane\":{\"width\":\"10\",\"height\":\"6\"},"
        "\"regions\":[{\"id\":\"r1\",\"label\":\"R\",\"shape\":\"rect\","
        "\"coords\":[\"0\",\"0\",\"2\",\"2\"]},"
        "{\"id\":\"r1\",\"label\":\"S\",\"shape\":\"circle\","
        "\"coords\":[\"5\",\"3\",\"1\"]}],\"initial\":{\"region\":null},"
        "\"actions\":[\"select_hotspot\"],\"accessibility\":{\"description\":\"d\"}}]\n"
        "[SCORING: {\"kind\":\"hotspot\",\"accepted\":[{\"region\":\"r1\"}],"
        "\"tolerance\":{},\"partial_credit\":false}]\n")
    q = model.parse_bank(bad_dup)[0]
    errs, _ = model.lint([q], lesson=None)
    if "item.visual_duplicate_id" not in [e.code for e in errs]:
        fail("duplicate region ids did not yield item.visual_duplicate_id: %r"
             % [e.code for e in errs])

    # A plot scene member on a hotspot item is an unknown member.
    bad_member = (
        "Q1. Select a region.   (difficulty: recall)\n"
        "[OBJECTIVE: test:probe]\n"
        "[TYPE: visual]\n[INTERACTION: hotspot]\n"
        "[VISUAL: {\"version\":1,\"plane\":{\"width\":\"10\",\"height\":\"6\"},"
        "\"regions\":[{\"id\":\"r1\",\"label\":\"R\",\"shape\":\"rect\","
        "\"coords\":[\"0\",\"0\",\"2\",\"2\"]}],\"axes\":{\"x\":{\"min\":\"0\","
        "\"max\":\"1\",\"step\":\"1\"}},\"initial\":{\"region\":null},"
        "\"actions\":[\"select_hotspot\"],\"accessibility\":{\"description\":\"d\"}}]\n"
        "[SCORING: {\"kind\":\"hotspot\",\"accepted\":[{\"region\":\"r1\"}],"
        "\"tolerance\":{},\"partial_credit\":false}]\n")
    q = model.parse_bank(bad_member)[0]
    errs, _ = model.lint([q], lesson=None)
    if "item.visual_unknown_member" not in [e.code for e in errs]:
        fail("plot member on hotspot item did not yield visual_unknown_member: %r"
             % [e.code for e in errs])

    # A non-zero tolerance on an exact-id family is an authoring error.
    valid = (
        "Q1. Select a region.   (difficulty: recall)\n"
        "[OBJECTIVE: test:probe]\n"
        "[TYPE: visual]\n[INTERACTION: hotspot]\n"
        "[VISUAL: {\"version\":1,\"plane\":{\"width\":\"10\",\"height\":\"6\"},"
        "\"regions\":[{\"id\":\"r1\",\"label\":\"R\",\"shape\":\"rect\","
        "\"coords\":[\"0\",\"0\",\"2\",\"2\"]}],\"initial\":{\"region\":null},"
        "\"actions\":[\"select_hotspot\"],\"accessibility\":{\"description\":\"d\"}}]\n"
        "[SCORING: {\"kind\":\"hotspot\",\"accepted\":[{\"region\":\"r1\"}],"
        "\"tolerance\":{},\"partial_credit\":false}]\n")
    q = model.parse_bank(valid)[0]
    errs, _ = model.lint([q], lesson=None)
    if any(e.code == "item.visual_invalid_geometry" for e in errs):
        fail("valid hotspot scene failed geometry lint: %r"
             % [e.message for e in errs])
    bad_tol = valid.replace('"tolerance":{}', '"tolerance":{"region":"1"}')
    q = model.parse_bank(bad_tol)[0]
    errs, _ = model.lint([q], lesson=None)
    if not any("exact-id" in e.message for e in errs):
        fail("non-zero hotspot tolerance was not flagged: %r"
             % [e.message for e in errs])
    ok("lint: closed per-interaction grammar; invalid_geometry/duplicate_id/"
       "unknown_member/tolerance codes named")


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


def advance_to(session_file, qs, number):
    for _ in range(12):
        if item_at(session_file, qs)["number"] == number:
            return session_file
        session_surface.do_submit(
            session_file, _correct_for(item_at(session_file, qs)), None)
    fail("session never reached item %d" % number)


def _correct_for(q):
    """The fixture's correct semantic response for a served item, by
    number/interaction -- the public contract never carries accepted states."""
    if q["interaction"] == "hotspot":
        return json.dumps({"kind": "hotspot",
                           "region": q["scoring"]["accepted"][0]["region"]})
    if q["interaction"] == "timeline":
        return json.dumps({"kind": "timeline_event",
                           "event": q["scoring"]["accepted"][0]["event"],
                           "value": q["scoring"]["accepted"][0]["value"]})
    if q["interaction"] == "diagram":
        return json.dumps({"kind": "diagram_connection", "from": "a",
                           "to": "c"})
    if q["interaction"] == "trace":
        return json.dumps({"kind": "trace_path",
                           "points": q["scoring"]["accepted"][0]["points"]})
    if q["interaction"] == "plot":
        return json.dumps({"kind": "point", "x": "2", "y": "3"})
    if q["scoring"]["kind"] == "interval":
        return json.dumps({"kind": "interval", "start": "-1", "end": "3/2",
                           "start_closed": True, "end_closed": False})
    return json.dumps({"kind": "numberline_point",
                       "value": "3/2" if q["number"] == 4 else "1/2"})


def check_interact_evidence(work):
    session_file, qs = fresh_session(work)
    advance_to(session_file, qs, 5)      # first hotspot item (Q5)
    q = item_at(session_file, qs)

    result = session_surface.do_interact(session_file, {
        "interaction_version": runtime.VISUAL_PROTOCOL_VERSION,
        "action_id": ACTION_ID,
        "action_type": "select_hotspot",
        "state": {"kind": "hotspot", "region": "heart"},
    })
    if result.get("status") != "recorded":
        fail("first hotspot commit status is %r" % result["status"])
    data = runtime.read_session(session_file)
    events = [ev for ev in load_log(work)
              if ev.get("event_type") == "visual_action"
              and ev.get("session_id") == data["session_id"]]
    if len(events) != 1:
        fail("expected exactly one visual_action event, found %d" % len(events))
    ev = events[0]
    if ev["action_type"] != "select_hotspot":
        fail("event action_type is %r" % ev["action_type"])
    if ev["after_state"] != {"kind": "hotspot", "region": "heart"}:
        fail("event after_state is %r" % ev["after_state"])
    if ev["before_state"] is not None:
        fail("first commit before_state is %r" % ev["before_state"])
    blob = json.dumps(ev)
    for banned in ("pointer", "clientX", "getBoundingClientRect", "screenshot",
                   "accepted", "tolerance", "answer_key", "verdict"):
        if banned in blob:
            fail("visual_action event carries banned material %r" % banned)

    # Identical retry dedupes; id reuse with different state conflicts.
    replay = session_surface.do_interact(session_file, {
        "interaction_version": runtime.VISUAL_PROTOCOL_VERSION,
        "action_id": ACTION_ID, "action_type": "select_hotspot",
        "state": {"kind": "hotspot", "region": "heart"}})
    if replay["status"] != "already_recorded":
        fail("identical retry status is %r" % replay["status"])
    conflict = session_surface.do_interact(session_file, {
        "interaction_version": runtime.VISUAL_PROTOCOL_VERSION,
        "action_id": ACTION_ID, "action_type": "select_hotspot",
        "state": {"kind": "hotspot", "region": "liver"}})
    if conflict["status"] != "conflict":
        fail("id reuse with different state status is %r" % conflict["status"])

    # Unknown region state refuses by name.
    try:
        session_surface.do_interact(session_file, {
            "interaction_version": runtime.VISUAL_PROTOCOL_VERSION,
            "action_id": "123e4567-e89b-42d3-a456-426614174001",
            "action_type": "select_hotspot",
            "state": {"kind": "hotspot", "region": "nope"}})
        fail("unknown region state was not refused")
    except SystemExit:
        pass
    # Final submit stays the ordinary response event.
    session_surface.do_submit(session_file, json.dumps(
        {"kind": "hotspot", "region": "heart"}), None)
    log = load_log(work)
    submits = [e for e in log if e.get("event_type") == "response"]
    if not submits:
        fail("no response event after the hotspot final submit")
    ok("interact/evidence: select_hotspot commits once, dedupes, conflicts, "
       "refuses unknown regions")


def check_schemas(work):
    session_file, qs = fresh_session(work)
    advance_to(session_file, qs, 5)
    q = item_at(session_file, qs)
    result = session_surface.do_interact(session_file, {
        "interaction_version": runtime.VISUAL_PROTOCOL_VERSION,
        "action_id": ACTION_ID, "action_type": "select_hotspot",
        "state": {"kind": "hotspot", "region": "heart"}})
    doc = json.load(open(os.path.join(ROOT, "schemas",
                                      "visual_interaction.schema.json"),
                         encoding="utf-8"))
    errs = schema_validate.validate(
        {"session_id": runtime.read_session(session_file)["session_id"],
         "interaction_version": runtime.VISUAL_PROTOCOL_VERSION,
         "action_id": ACTION_ID, "action_type": "select_hotspot",
         "state": {"kind": "hotspot", "region": "heart"}}, doc)
    if errs:
        fail("interact_request schema: %s" % errs[0])
    errs = schema_validate.validate(result["observation"], doc)
    if errs:
        fail("observation schema: %s" % errs[0])
    data = runtime.read_session(session_file)
    ev = [e for e in load_log(work)
          if e.get("event_type") == "visual_action"
          and e.get("session_id") == data["session_id"]][-1]
    errs = schema_validate.validate(ev, doc)
    if errs:
        fail("visual_action_event schema: %s" % errs[0])
    # The public item validates against item.schema.json's visual branch.
    item_doc = json.load(open(os.path.join(ROOT, "schemas",
                                           "item.schema.json"),
                              encoding="utf-8"))
    errs = schema_validate.validate(runtime.public_item(q), item_doc)
    if errs:
        fail("item.schema.json visual branch: %s" % errs[0])
    ok("schemas: hotspot request/observation/event/public item validate")


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
        for marker in ("function renderHotspot", "renderHotspot(q, c, body, act, card)",
                       '"select_hotspot"'):
            if marker not in html:
                fail("served page is missing %r" % marker)
        if "<canvas" in html:
            fail("served page uses canvas for the hotspot slice")

        start = api(base, "start", {"bank": stem, "mode": "practice", "count": 12})
        if start["status"] != "active":
            fail("POST /api/start did not return an active session")
        item = start["item"]
        assert_public_payload_clean(item, "/api/start item")
        if item["type"] != "visual":
            fail("served first item is %r, expected visual" % item["type"])
        sid = start["session_id"]
        seen = set()
        for _ in range(12):
            cur = api(base, "next", {"session_id": sid}) if seen else start
            q = cur["item"]
            num = q.get("number")
            if num in seen:
                fail("session served item %d twice" % num)
            seen.add(num)
            v = api(base, "submit", {"session_id": sid,
                                     "answer": _correct_for_item_num(q)})
            if v.get("score") is not True:
                fail("served submit of Q%d returned score %r" % (num, v.get("score")))
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
    ok("served: renderHotspot dispatch, no canvas, full 12-item sitting scores")


def _correct_for_item_num(q):
    if (q.get("interaction_contract") or {}).get("interaction") == "hotspot":
        # The served item never carries the accepted region; map by number
        # from the fixture's known answers (mirrors visual_roundtrip.py).
        return json.dumps({"kind": "hotspot",
                           "region": {5: "heart", 6: "montana",
                                      7: "ring"}[q["number"]]})
    if q["number"] == 1:
        return json.dumps({"kind": "point", "x": "2", "y": "3"})
    if q["number"] == 3:
        return json.dumps({"kind": "interval", "start": "-1", "end": "3/2",
                           "start_closed": True, "end_closed": False})
    if q["number"] == 8:
        return json.dumps({"kind": "timeline_event", "event": "fall",
                           "value": "5"})
    if q["number"] == 9:
        return json.dumps({"kind": "timeline_event", "event": "industrial",
                           "value": "7"})
    if q["number"] == 10:
        return json.dumps({"kind": "diagram_connection", "from": "a",
                           "to": "c"})
    if q["number"] in (11, 12):
        pts = [{"x": "0", "y": "0"}, {"x": "2", "y": "2"},
               {"x": "4", "y": "0"}] if q["number"] == 11 else \
              [{"x": "0", "y": "2"}, {"x": "2", "y": "0"},
               {"x": "4", "y": "2"}]
        return json.dumps({"kind": "trace_path", "points": pts})
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
        if "asVisualOffline" not in html:
            fail("static build page does not include the offline refusal renderer")
    finally:
        shutil.rmtree(work, ignore_errors=True)
    ok("offline: advanced visual items refuse loudly, no key/scoring material")


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
    hs = check_parser()
    check_public(hs)
    check_scoring(hs)
    check_observation(hs)
    check_lint(hs)
    work = tempfile.mkdtemp()
    try:
        check_interact_evidence(work)
        check_schemas(work)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    check_served()
    check_offline()
    print("PASS hotspot_roundtrip.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
