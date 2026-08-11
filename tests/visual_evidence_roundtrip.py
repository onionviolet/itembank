#!/usr/bin/env python3
"""Plan 06.1-02 Tasks 2 and 3: committed visual-action evidence and the one
CLI/API interact operation.

Proves the D-04/D-05 committed-action contract end to end: exactly the four
locked action types append exactly one `visual_action` event per successful
commit (with the common audit fields plus interaction_version, action_id,
action_type, before/after state, error_category, invariants, feedback_anchor,
hint_tier, dedupe_key); duplicate retries replay as already_recorded and id
reuse with different action/state is a conflict; `visual_actions()` reads
through live_events in commit order; final submit stays the ordinary response
event; the CLI `interact` and POST /api/interact call the same do_interact
body and return the same JSON; and raw pointer/private authority fields are
refused at the boundary.

Standard library only, no test framework, runnable as
`python tests/visual_evidence_roundtrip.py`.
"""
import json, os, re, shutil, subprocess, sys, tempfile, threading, time, uuid
import urllib.error, urllib.request


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ITEMBANK = os.path.join(ROOT, "itembank.py")
BANK = os.path.join(ROOT, "fixtures", "visual_bank.md")
sys.path.insert(0, ROOT)

import evidence                                        # noqa: E402
import model                                           # noqa: E402
import runtime                                         # noqa: E402
from surfaces import session as session_surface        # noqa: E402
import schema_validate                                 # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def ok(msg):
    print("ok: " + msg)


ACTION_ID = "123e4567-e89b-42d3-a456-426614174000"      # a canonical uuid-v4


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


def session_actions(work, session_file):
    """The visual_action events for one session's log (the shared scratch
    log accumulates across check functions, so count per session)."""
    data = runtime.read_session(session_file)
    return [ev for ev in load_log(work)
            if ev.get("event_type") == "visual_action"
            and ev.get("session_id") == data["session_id"]]


def fresh_session(work):
    """Copy the visual bank into a scratch dir and start a 4-item practice
    session; returns (session_file, qs_by_number)."""
    isolated = os.path.join(work, "visual_bank.md")
    shutil.copyfile(BANK, isolated)
    started = run(["start", isolated, "--count", "4", "--mode", "practice",
                   "--out", os.path.join(work, "session.json")], work)
    session_file = started["session_file"]
    qs = model.parse_bank(open(isolated, encoding="utf-8").read())
    return session_file, qs


def item_at(session_file, qs):
    data = runtime.read_session(session_file)
    return qs[data["items"][data["cursor"]]]


CORRECT = {
    1: {"kind": "point", "x": "2", "y": "3"},
    2: {"kind": "numberline_point", "value": "1/2"},
    3: {"kind": "interval", "start": "-1", "end": "3/2",
        "start_closed": True, "end_closed": False},
    4: {"kind": "numberline_point", "value": "3/2"},
}


def advance_to(session_file, qs, number):
    """Advance the session until the current item has the given number by
    submitting the fixture's correct response for each item passed over
    (selection may serve items in any order, and only a submit advances the
    cursor). Returns the session file."""
    for _ in range(8):
        if item_at(session_file, qs)["number"] == number:
            return session_file
        session_surface.do_submit(
            session_file, json.dumps(CORRECT[item_at(session_file, qs)["number"]]),
            None)
    fail("session never reached item %d" % number)


# ---- Task 2: the committed-action event contract -----------------------------

def check_event_shape(work):
    session_file, qs = fresh_session(work)
    advance_to(session_file, qs, 1)      # the plot item
    q = item_at(session_file, qs)

    point = {"kind": "point", "x": "2", "y": "3"}
    result = session_surface.do_interact(session_file, {
        "interaction_version": runtime.VISUAL_PROTOCOL_VERSION,
        "action_id": ACTION_ID,
        "action_type": "place_point",
        "state": point,
    })
    if result.get("status") != "recorded":
        fail("first commit status is %r, expected recorded" % result["status"])

    events = load_log(work)
    actions = session_actions(work, session_file)
    if len(actions) != 1:
        fail("expected exactly one visual_action event, found %d" % len(actions))
    ev = actions[0]

    # Exact locked field set (06.1-RESEARCH.md item 2).
    required = {"schema_version", "event_id", "event_type", "ts", "session_id",
                "item_id", "item_ref", "item_type", "bank", "objective",
                "subject", "mode", "source_ref", "interaction_version",
                "action_id", "action_type", "before_state", "after_state",
                "error_category", "invariants", "feedback_anchor",
                "hint_tier", "dedupe_key"}
    if set(ev) != required:
        fail("visual_action event key set mismatch: extra=%r missing=%r"
             % (sorted(set(ev) - required), sorted(required - set(ev))))
    if ev["interaction_version"] != runtime.VISUAL_PROTOCOL_VERSION:
        fail("event interaction_version is %r" % ev["interaction_version"])
    if ev["action_id"] != ACTION_ID:
        fail("event action_id is %r" % ev["action_id"])
    if ev["action_type"] != "place_point":
        fail("event action_type is %r" % ev["action_type"])
    if ev["after_state"] != point:
        fail("event after_state is %r" % ev["after_state"])
    if ev["before_state"] is not None:
        fail("first commit before_state is %r, expected None" % ev["before_state"])
    if ev["item_type"] != "visual":
        fail("event item_type is %r" % ev["item_type"])
    # No pointer/private authority material anywhere in the event.
    blob = json.dumps(ev)
    for banned in ("pointer", "clientX", "getBoundingClientRect", "screenshot",
                   "accepted", "tolerance", "answer_key", "verdict"):
        if banned in blob:
            fail("visual_action event carries banned material %r" % banned)
    ok("event shape: locked field set, canonical state, no pointer/private data")


def check_dedupe_and_conflict(work):
    session_file, qs = fresh_session(work)
    advance_to(session_file, qs, 1)
    q = item_at(session_file, qs)

    point = {"kind": "point", "x": "2", "y": "3"}
    action = {"interaction_version": runtime.VISUAL_PROTOCOL_VERSION,
              "action_id": ACTION_ID, "action_type": "place_point",
              "state": point}
    first = session_surface.do_interact(session_file, action)
    if first["status"] != "recorded":
        fail("first commit status is %r" % first["status"])

    # Identical retry: already_recorded, appends nothing.
    replay = session_surface.do_interact(session_file, dict(action))
    if replay["status"] != "already_recorded":
        fail("identical retry status is %r, expected already_recorded"
             % replay["status"])
    if len(session_actions(work, session_file)) != 1:
        fail("identical retry appended a second event")

    # Same action id, different action/state: conflict.
    conflict = session_surface.do_interact(session_file, dict(
        action, action_type="move_point",
        state={"kind": "point", "x": "3", "y": "4"}))
    if conflict["status"] != "conflict":
        fail("id reuse with different action/state status is %r, expected "
             "conflict" % conflict["status"])
    if len(session_actions(work, session_file)) != 1:
        fail("conflict appended a second event")

    # A different action id with different state is a fresh commit.
    second = session_surface.do_interact(session_file, dict(
        action, action_id="123e4567-e89b-42d3-a456-426614174001",
        action_type="move_point",
        state={"kind": "point", "x": "3", "y": "4"}))
    if second["status"] != "recorded":
        fail("distinct commit status is %r" % second["status"])
    if second["before_state"] != point:
        fail("second commit before_state is %r, expected the prior committed "
             "point %r" % (second["before_state"], point))
    ok("dedupe/conflict: identical retry replays, id reuse conflicts, "
       "distinct commits append in order")


def check_refusals(work):
    session_file, qs = fresh_session(work)
    advance_to(session_file, qs, 1)
    q = item_at(session_file, qs)
    point = {"kind": "point", "x": "2", "y": "3"}
    base = {"interaction_version": runtime.VISUAL_PROTOCOL_VERSION,
            "action_id": ACTION_ID, "action_type": "place_point",
            "state": point}

    def expect_refusal(mutator, why):
        action = dict(base)
        mutator(action)
        try:
            session_surface.do_interact(session_file, action)
        except SystemExit as exc:
            if why not in str(exc.code):
                fail("refusal %r did not name %r: %s" % (why, why, exc.code))
            return
        fail("interact with %s was not refused" % why)

    expect_refusal(lambda a: a.update(action_id="not-a-uuid"), "action_id")
    expect_refusal(lambda a: a.update(interaction_version=99),
                   "interaction_version")
    expect_refusal(lambda a: a.update(action_type="drag_fire"), "action_type")
    expect_refusal(lambda a: a.update(state={"kind": "point", "x": "1e3",
                                             "y": "3"}), "state")
    expect_refusal(lambda a: a.update(state={"kind": "point", "x": "2",
                                             "y": "99"}), "domain")
    expect_refusal(lambda a: a.update(score=True), "unknown field")
    expect_refusal(lambda a: a.update(item_id="q1"), "unknown field")

    # A nonvisual session refuses: start the sample bank and interact.
    sample = os.path.join(work, "sample_bank.md")
    shutil.copyfile(os.path.join(ROOT, "fixtures", "sample_bank.md"), sample)
    started = run(["start", sample, "--count", "3", "--out",
                   os.path.join(work, "sample_session.json")], work)
    try:
        session_surface.do_interact(started["session_file"], dict(base))
    except SystemExit as exc:
        if "not a visual item" not in str(exc.code):
            fail("nonvisual interact refusal: %s" % exc.code)
    else:
        fail("interact on a nonvisual item was not refused")
    ok("refusals: bad id/version/action/state/domain, authority fields, "
       "nonvisual sessions all named")


def check_visual_actions_query(work):
    session_file, qs = fresh_session(work)
    advance_to(session_file, qs, 1)
    q = item_at(session_file, qs)
    point = {"kind": "point", "x": "2", "y": "3"}
    session_surface.do_interact(session_file, {
        "interaction_version": runtime.VISUAL_PROTOCOL_VERSION,
        "action_id": ACTION_ID, "action_type": "place_point", "state": point})
    log = evidence.log_path(os.path.dirname(session_file))
    data = runtime.read_session(session_file)
    trail = evidence.visual_actions(log, data["session_id"])
    if len(trail) != 1 or trail[0]["action_type"] != "place_point":
        fail("visual_actions query returned %r" % trail)
    if trail[0]["after_state"] != point:
        fail("visual_actions trail lost the canonical state")
    # The final response event carries the same item/session/protocol identity
    # and normalized final state (plan 02 Task 2 closing requirement).
    session_surface.do_submit(session_file, json.dumps(point), None)
    events = load_log(work)
    response = [ev for ev in events if ev.get("event_type") == "response"][-1]
    action = [ev for ev in events if ev.get("event_type") == "visual_action"][-1]
    if response["item_ref"] != action["item_ref"]:
        fail("response and action events disagree on item_ref")
    if response["session_id"] != action["session_id"]:
        fail("response and action events disagree on session_id")
    if json.loads(response["canonical"]) != action["after_state"]:
        fail("response canonical state differs from the final committed state")
    ok("visual_actions: live, ordered, reconciled to the final response")


# ---- Task 3: one semantic interact operation through CLI and API -------------

def check_cli_api_parity(work):
    isolated = os.path.join(work, "visual_bank.md")
    shutil.copyfile(BANK, isolated)
    # Default --out places the session under <bank_dir>/_attempts/, which is
    # exactly where the daemon's session_index scans, so the API can address
    # the same session the CLI just used.
    started = run(["start", isolated, "--count", "4", "--mode", "practice"], work)
    session_file = started["session_file"]
    qs = model.parse_bank(open(isolated, encoding="utf-8").read())
    advance_to(session_file, qs, 1)
    q = item_at(session_file, qs)
    point = {"kind": "point", "x": "2", "y": "3"}
    action = {"interaction_version": runtime.VISUAL_PROTOCOL_VERSION,
              "action_id": ACTION_ID, "action_type": "place_point",
              "state": point}

    cli = run(["interact", session_file, "--action", json.dumps(action)], work)
    if cli["status"] != "recorded":
        fail("CLI interact status is %r" % cli["status"])
    if cli["observation"]["submitted"] != point:
        fail("CLI interact observation lost the submitted state")

    # POST /api/interact on the same session: the daemon must reach the same
    # do_interact body. Because the CLI already committed this exact action,
    # the API returns already_recorded with the identical observation shape.
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
        fail("server never printed a URL")
    try:
        data = runtime.read_session(session_file)
        sid = data["session_id"]
        req = urllib.request.Request(
            base + "api/interact",
            data=json.dumps(dict(action, session_id=sid)).encode(),
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as res:
            api_result = json.loads(res.read().decode("utf-8"))
        if api_result["status"] != "already_recorded":
            fail("API interact replay status is %r, expected already_recorded"
                 % api_result["status"])
        for key in ("observation", "action_id"):
            if api_result.get(key) != cli.get(key):
                fail("API/CLI parity broken on %r: CLI=%r API=%r"
                     % (key, cli.get(key), api_result.get(key)))

        # Authority fields are refused by name at the HTTP boundary.
        bad = dict(action, session_id=sid, item_id="q1", score=True,
                   tolerance={"x": "5", "y": "5"})
        req = urllib.request.Request(
            base + "api/interact", data=json.dumps(bad).encode(),
            headers={"Content-Type": "application/json"})
        try:
            urllib.request.urlopen(req, timeout=5)
        except urllib.error.HTTPError as exc:
            if exc.code != 400:
                fail("authority-field refusal returned %d" % exc.code)
            body = exc.read().decode("utf-8", "replace")
            if "item_id" not in body:
                fail("authority-field refusal does not name the field: %s" % body)
        else:
            fail("authority fields were accepted by /api/interact")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
    ok("CLI/API parity: one do_interact body, identical observation shape, "
       "authority fields refused")


def check_schemas(work):
    session_file, qs = fresh_session(work)
    advance_to(session_file, qs, 1)
    q = item_at(session_file, qs)
    point = {"kind": "point", "x": "2", "y": "3"}
    result = session_surface.do_interact(session_file, {
        "interaction_version": runtime.VISUAL_PROTOCOL_VERSION,
        "action_id": ACTION_ID, "action_type": "place_point", "state": point})
    doc = json.load(open(os.path.join(ROOT, "schemas",
                                      "visual_interaction.schema.json"),
                         encoding="utf-8"))
    # The request validates (against the whole document, so the $refs in
    # $defs.semantic_state resolve).
    errs = schema_validate.validate(
        {"session_id": runtime.read_session(session_file)["session_id"],
         "interaction_version": runtime.VISUAL_PROTOCOL_VERSION,
         "action_id": ACTION_ID, "action_type": "place_point", "state": point},
        doc)
    if errs:
        fail("interact_request schema: %s" % errs[0])
    # The observation and the appended evidence event validate (against the
    # whole document so $defs refs resolve; each instance matches exactly one
    # oneOf branch).
    errs = schema_validate.validate(result["observation"], doc)
    if errs:
        fail("observation schema: %s" % errs[0])
    events = load_log(work)
    ev = [e for e in events if e.get("event_type") == "visual_action"][-1]
    errs = schema_validate.validate(ev, doc)
    if errs:
        fail("visual_action_event schema: %s" % errs[0])
    # The response event schema also validates the visual response event.
    session_surface.do_submit(session_file, json.dumps(point), None)
    resp_doc = json.load(open(os.path.join(ROOT, "schemas",
                                           "response.schema.json"),
                              encoding="utf-8"))
    response = [e for e in load_log(work) if e.get("event_type") == "response"][-1]
    errs = schema_validate.validate(response, resp_doc)
    if errs:
        fail("response.schema.json with a visual event: %s" % errs[0])
    ok("schemas: request/observation/event validate; visual response event "
       "validates against response.schema.json")


def main():
    work = tempfile.mkdtemp()
    try:
        check_event_shape(work)
        check_dedupe_and_conflict(work)
        check_refusals(work)
        check_visual_actions_query(work)
        check_cli_api_parity(work)
        check_schemas(work)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    print("PASS visual_evidence_roundtrip.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
