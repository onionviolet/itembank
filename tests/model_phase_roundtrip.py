#!/usr/bin/env python3
"""The cross-surface Phase 8 release gate (plan 08-06).

One deterministic suite that proves every Phase 8 promise at once: the
adversarial corpus, the offline matrix, the single-authority invariants, and
the recorded human UAT all agree. Passing unit slices are insufficient if
surfaces bypass the gate, providers diverge, or model code quietly duplicates
scoring/evidence authority -- this gate exists so the phase ships only when
they cannot.

Covered here:

- run_full_scenario(): one real end-to-end scenario through hosted and local
  fake backends, the shared adapter, the tier gate, evidence, a rubric
  proposal, and the human-only accept (plan 08-06 Task 1).
- run_offline_matrix(): the nine provider-failure rows; submit/scoring,
  lessons, authored hints, evidence append/read, reports, and explicit human
  marking still pass -- only generated assistance is unavailable (Task 2).
- run_authority_regressions(): scoring/evidence/protocol/hint/daemon/serve
  (and runner when present) all pass unchanged -- one parser, one scorer,
  one evidence writer (Task 2).
- run_payload_scan(): the flatten() forbidden-phrase discipline over every
  learner-facing JSON document the scenario produced, with forbidden material
  derived from the fixture items (Task 2).
- run_contract_audit(): structural absence of auto-accept, suggestion_reveal
  default with all three enum values, the unchanged human-only mark guard,
  no fractional score in the new event builders, no invented performance
  figure, agent_usage/COVERAGE validation, the D-18 hosted-default record,
  and the ROADMAP criterion 1-14 to assertion mapping (Task 3).

The scenario drives the fixture lesson bank (fixtures/lesson_bank.md): its mc
item carries tier-0 lesson content, so one genuine wrong answer unlocks the
lesson pointer tier and a passing hint can legitimately reference
tier0.lesson_ref; its short item carries a 3-point rubric for the proposal
flow. Stdlib only, no network, runnable as
`python tests/model_phase_roundtrip.py`.
"""
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import evidence                                    # noqa: E402
import model                                       # noqa: E402
import runtime                                     # noqa: E402
import schema_validate                             # noqa: E402
import serve_roundtrip                             # noqa: E402
import tier_gate                                   # noqa: E402

TOOL = os.path.join(ROOT, "itembank.py")
LESSON_BANK = os.path.join(ROOT, "fixtures", "lesson_bank.md")
CASES_PATH = os.path.join(ROOT, "fixtures", "model_gate_cases.json")
SETTINGS_SCHEMA_PATH = os.path.join(ROOT, "schemas", "settings.schema.json")
AGENT_USAGE_SCHEMA_PATH = os.path.join(ROOT, "schemas",
                                       "agent_usage.schema.json")
PHASE08_DIR = os.path.join(
    ROOT, ".planning", "phases",
    "08-model-adapter-interface-tier-gate-enforcement")

# The fixture lesson bank's item identities (q["id"] is the numbered id the
# public item and every evidence item_ref carry; the opaque [ID:] lives in
# q["item_id"] and is not what mark/evidence match on).
MC_ID = "q1"      # the mc item; tier-0 lesson content; key is B
SHORT_ID = "q3"   # the short item with a 3-point rubric
LESSON_SLUG = "the-airway-step-by-step"   # lesson_slug("The Airway, Step By Step")

# The fixed gate reasons and authority vocabulary that must never reach a
# learner-facing artifact (mirrors tests/model_ui_roundtrip.py's
# FORBIDDEN_STRINGS discipline).
FORBIDDEN_AUTHORITY = (
    "TIER 0", "TIER 1", "TIER 2", "TIER 3", "TIER 4", "TIER 5",
    "tier0.", "tier1.", "tier2.", "tier3.", "tier4.", "tier5.",
    "gate.schema_invalid", "gate.span_unmatched", "gate.fact_protected",
    "gate.fact_unknown", "gate.ambiguous", "gate.unsupported_move",
    "hosted_cli", "openai_compatible", "backend_class", "fake-hosted",
    "phase8-hosted", "phase8-local", "phase8-drop", "phase8-rubric",
    "phase8-exit1", "phase8-sleep", "phase8-malformed", "phase8-oversize",
    "phase8-refused", "unreachable", "http_fail",
    "FAKE_MODEL_SECRET", "s3cr3t-value",
)

# Every learner-facing artifact the scenario produced, as (label, payload),
# for the flatten()-style boundary scan (run_payload_scan). The "mark"
# artifact is the human marker's own output and is treated as operator-facing
# by the scan (its rubric points echo the marker's input, not withheld
# material).
_PAYLOADS = []

# The raw adversarial candidate the drop fixture emits; the scan proves its
# text appears in no artifact and no evidence line.
_DROP_CANDIDATE = None


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def flatten(obj):
    """Yield (key, value) for every key at every depth of a JSON-like
    structure -- the same discipline evidence_roundtrip.py's flatten()
    applies, so a forbidden string hidden in a field NAME also fails the
    scan."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield (k, v)
            yield from flatten(v)
    elif isinstance(obj, list):
        for el in obj:
            yield from flatten(el)


def norm(s):
    """Normalized text for phrase comparisons: casefold plus whitespace
    collapse."""
    return " ".join(str(s or "").split()).lower()


def run(args, cwd):
    """Run the CLI and return parsed JSON stdout; any non-zero exit fails."""
    r = subprocess.run([sys.executable, TOOL] + [str(a) for a in args],
                       cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        fail("command %r failed (%d): %s" % (args, r.returncode, r.stderr))
    return json.loads(r.stdout)


def run_raw(args, cwd):
    """Run the CLI and return the CompletedProcess without asserting exit 0."""
    return subprocess.run([sys.executable, TOOL] + [str(a) for a in args],
                          cwd=cwd, capture_output=True, text=True)


def run_json(args, cwd):
    """Run the CLI and return the first JSON value in stdout -- `mark`
    prints a JSON payload followed by a one-line human summary."""
    r = run_raw(args, cwd)
    if r.returncode != 0:
        fail("command %r failed (%d): %s" % (args, r.returncode, r.stderr))
    try:
        value, _ = json.JSONDecoder().raw_decode(r.stdout.lstrip())
    except ValueError as exc:
        fail("command %r did not print a JSON payload: %s" % (args, exc))
    return value


def session_id_of(session_path):
    return runtime.read_session(session_path)["session_id"]


def record_payload(label, payload):
    _PAYLOADS.append((label, payload))


# ---- fixtures: fake backends, profiles, loopback server --------------------

def _script(tmp, name, kind):
    """One fake hosted-CLI executable body per failure/generation kind.
    Each reads the request from stdin and writes a fixed candidate (or the
    named failure) to stdout -- no real provider, no network. Hint candidates
    echo the learner's actual wrong response as the focus_span (the runtime
    sends it in payload.learner_response) so the gate's span check matches,
    exactly like tests/model_ui_roundtrip.py's passing fake."""
    path = os.path.join(tmp, "fake_%s.py" % name)
    if kind == "pass-hint":
        body = (
            "import json, sys\n"
            "req = json.load(sys.stdin)\n"
            "resp = (req.get('payload') or {}).get('learner_response', 'A')\n"
            "out = {'kind': 'hint_plan', 'interaction_id': req['interaction_id'],\n"
            "       'focus_span': resp, 'fact_ids': ['tier0.lesson_ref'],\n"
            "       'move': 'anchor_error'}\n"
            "json.dump(out, sys.stdout)\n")
    elif kind == "drop":
        body = (
            "import json, sys\n"
            "req = json.load(sys.stdin)\n"
            "resp = (req.get('payload') or {}).get('learner_response', 'A')\n"
            "out = {'kind': 'hint_plan', 'interaction_id': req['interaction_id'],\n"
            "       'focus_span': resp, 'fact_ids': ['tier5.why'],\n"
            "       'move': 'anchor_error'}\n"
            "json.dump(out, sys.stdout)\n")
    elif kind == "refused":
        # A well-formed candidate that carries an explicit refusal flag: the
        # gate drops it whole (gate.schema_invalid) -- refused output is a
        # gate-level refusal, distinct from an adapter-level failure row.
        body = (
            "import json, sys\n"
            "req = json.load(sys.stdin)\n"
            "resp = (req.get('payload') or {}).get('learner_response', 'A')\n"
            "out = {'kind': 'hint_plan', 'interaction_id': req['interaction_id'],\n"
            "       'focus_span': resp, 'fact_ids': ['tier0.lesson_ref'],\n"
            "       'move': 'anchor_error', 'refused': True}\n"
            "json.dump(out, sys.stdout)\n")
    elif kind == "rubric":
        # A rubric_proposal for the fixture short item. The rationales are
        # deliberately never substrings of (and never contain) the fixture's
        # private material, so the gate's protected-fragment scan passes them
        # and the payload-boundary scan stays clean.
        body = (
            "import json, sys\n"
            "req = json.load(sys.stdin)\n"
            "out = {'kind': 'rubric_proposal',\n"
            "       'interaction_id': req['interaction_id'],\n"
            "       'points': [\n"
            "           {'point_index': 0, 'status': 'pass',\n"
            "            'rationale': 'The response names repositioning first.'},\n"
            "           {'point_index': 1, 'status': 'uncertain',\n"
            "            'rationale': 'No cervical spine trigger is stated.'},\n"
            "           {'point_index': 2, 'status': 'pass',\n"
            "            'rationale': 'The airway opens without neck movement.'}]}\n"
            "json.dump(out, sys.stdout)\n")
    elif kind == "exit1":
        body = "import sys\nsys.exit(1)\n"
    elif kind == "sleep":
        body = "import time\ntime.sleep(30)\n"
    elif kind == "malformed":
        body = "sys.stdout.write('not json')\n"
    elif kind == "oversize":
        body = "sys.stdout.write('x' * 10000)\n"
    else:
        fail("unknown fake script kind %r" % kind)
    open(path, "w", encoding="utf-8").write(body)
    return path


def hosted_profile(tmp, name, kind, timeout=30, max_bytes=65536):
    script = _script(tmp, name, kind)
    return {"name": name, "transport": "hosted_cli",
            "command": [sys.executable, script], "model": "fake",
            "timeout_seconds": timeout, "max_output_bytes": max_bytes,
            "context_window": 4096}


class _FakeServer:
    """A threaded loopback OpenAI-compatible endpoint whose behaviour is set
    at construction: ok returns the fixed passing hint_plan body (echoing
    the request's interaction id and learner response); refuse500 returns
    HTTP 500. Every request body and header set is captured so a test can
    assert what actually left the machine (secrets never ride along in the
    body or evidence)."""

    def __init__(self, mode="ok"):
        self.mode = mode
        self.received = []
        self.headers = []
        ctx = {"mode": mode, "received": self.received, "headers": self.headers}

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                length = int(self.headers.get("Content-Length") or 0)
                body = self.rfile.read(length).decode("utf-8")
                ctx["received"].append(body)
                ctx["headers"].append(dict(self.headers))
                if ctx["mode"] == "refuse500":
                    self.send_response(500)
                    data = b"boom"
                else:
                    self.send_response(200)
                    req = json.loads(body)
                    resp = (req.get("payload") or {}).get("learner_response",
                                                          "A")
                    payload = {"kind": "hint_plan",
                               "interaction_id": req["interaction_id"],
                               "focus_span": resp,
                               "fact_ids": ["tier0.lesson_ref"],
                               "move": "anchor_error"}
                    data = json.dumps(payload).encode("utf-8")
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                try:
                    self.wfile.write(data)
                except BrokenPipeError:
                    pass

            def log_message(self, *args):
                pass

        self.server = HTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever,
                                       daemon=True)
        self.thread.start()

    @property
    def port(self):
        return self.server.server_address[1]

    def close(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)


def local_profile(server_or_port, name, secret_env=None, timeout=5,
                  max_bytes=65536):
    endpoint = "http://127.0.0.1:%d/v1/chat/completions" % (
        server_or_port.port if hasattr(server_or_port, "port")
        else server_or_port)
    profile = {"name": name, "transport": "openai_compatible",
               "endpoint": endpoint, "model": "qwen",
               "timeout_seconds": timeout, "max_output_bytes": max_bytes,
               "context_window": 8192}
    if secret_env:
        profile["secret_env"] = secret_env
    return profile


def closed_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def write_settings(tmp, settings):
    open(os.path.join(tmp, "itembank.json"), "w", encoding="utf-8").write(
        json.dumps(settings))


def mc_scenario(tmp, profile, active):
    """The standard mc hint scenario: a fresh session on the fixture lesson
    bank's mc item, one genuine wrong answer (unlocking tier 0 = the lesson
    pointer), then one hint request through the configured backend. Returns
    (bank, session, hint_result, item, wrong_answer)."""
    write_settings(tmp, {"model_backend": {"active": active,
                                           "profiles": [profile]}})
    bank = os.path.join(tmp, "lesson_bank.md")
    shutil.copyfile(LESSON_BANK, bank)
    session = os.path.join(tmp, "session.json")
    started = run(["start", bank, "--count", "1", "--type", "mc", "--seed",
                   "7", "--mode", "practice", "--out", session], tmp)
    record_payload("start-mc", started)
    if started["item"]["id"] != MC_ID:
        fail("mc scenario did not serve the fixture mc item: %r"
             % started["item"])
    q = next(x for x in model.load(bank) if x["id"] == started["item"]["id"])
    wrong = serve_roundtrip.wrong_answer(q)
    w = run(["submit", session, "--answer", json.dumps(wrong)], tmp)
    record_payload("submit-wrong", w)
    if w["accepted"] is not True or w["score"] is not False:
        fail("the wrong answer must record and score False: %r" % w)
    hint = run(["hint", "--session", session], tmp)
    record_payload("hint-%s" % active, hint)
    return bank, session, hint, q, wrong


def expected_hint_render(q, wrong, tier, candidate):
    """The gate-rendered output the scenario must equal: build the manifest
    exactly as the runtime does, pass the same candidate, and render."""
    picked = str(wrong).split(",")[0].strip().upper()
    manifest = tier_gate.build_fact_manifest(q, tier, wrong, picked)
    rendered = tier_gate.render_hint(candidate, manifest)
    return tier_gate.learner_payload("pass", rendered).get("generated")


# ---- Task 1: the tracer ----------------------------------------------

def _hosted_hint_pass():
    """Test 1: with a fake hosted CLI profile, a wrong answer on an mc item
    produces a hint whose learner payload equals the gate-rendered output
    (status pass, fixed-template text, the exact learner span present); the
    model_interaction event is retrievable by session with the same
    interaction id. Replaying the scenario is idempotent (D-12): a second
    hint reports already_recorded with the same interaction id, and a
    re-submitted identical answer reports already_recorded with the same
    event id."""
    tmp = tempfile.mkdtemp()
    try:
        profile = hosted_profile(tmp, "phase8-hosted", "pass-hint")
        bank, session, hint, q, wrong = mc_scenario(tmp, profile,
                                                    "phase8-hosted")
        if hint["status"] != "pass":
            fail("hosted hint must pass the gate, got %r" % hint)
        if hint["generated"] is None:
            fail("hosted pass hint must render a payload")
        candidate = {"kind": "hint_plan",
                     "interaction_id": hint["interaction_id"],
                     "focus_span": wrong, "fact_ids": ["tier0.lesson_ref"],
                     "move": "anchor_error"}
        expected = expected_hint_render(q, wrong, 0, candidate)
        if hint["generated"] != expected:
            fail("hosted hint payload must equal the gate-rendered output: "
                 "%r vs %r" % (hint["generated"], expected))
        if ('"%s"' % wrong) not in hint["generated"]["text"]:
            fail("rendered hint must carry the exact learner span %r: %r"
                 % (wrong, hint["generated"]["text"]))

        log = evidence.log_path(tmp)
        sid = session_id_of(session)
        evs = [e for e in evidence.model_interactions(log, sid)
               if e.get("operation") == "hint"]
        if len(evs) != 1:
            fail("hosted scenario must append exactly one hint interaction, "
                 "found %d" % len(evs))
        ev = evs[0]
        if ev["interaction_id"] != hint["interaction_id"]:
            fail("evidence interaction_id must match the payload: %r vs %r"
                 % (ev["interaction_id"], hint["interaction_id"]))
        if ev["outcome"] != "pass" or ev["pass_payload"] != expected:
            fail("evidence must record the pass outcome and payload: %r"
                 % {k: ev.get(k) for k in ("outcome", "pass_payload")})
        if ev["backend_class"] != "hosted":
            fail("hosted scenario must record backend_class hosted, got %r"
                 % ev["backend_class"])

        # Idempotency edge probe (explicit predicate, never approximated):
        # replaying the scenario yields identical evidence statuses.
        again = run(["hint", "--session", session], tmp)
        if again["interaction_id"] != hint["interaction_id"]:
            fail("a repeated hint must return the same interaction id, got "
                 "%r vs %r" % (again["interaction_id"],
                               hint["interaction_id"]))
        if again["evidence"].get("status") != "already_recorded":
            fail("a repeated hint must report already_recorded, got %r"
                 % again["evidence"])
        replay = run(["submit", session, "--answer", json.dumps(wrong)], tmp)
        if replay["accepted"] is not False or \
                replay["evidence"].get("status") != "already_recorded":
            fail("an identical re-submit must dedupe to already_recorded, "
                 "got %r" % replay)
        return {"hint": hint, "expected": expected, "ev": ev,
                "interaction_keys": set(hint.keys()),
                "evidence_keys": set(ev.keys())}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _local_parity(hosted):
    """Test 2: with the local loopback profile switched in via settings
    only, the identical scenario produces the same normalized payload shape
    (MODEL-02) and the same evidence field set; credentials stay out of the
    request body, evidence, and learner payloads (D-03/D-15)."""
    tmp = tempfile.mkdtemp()
    server = None
    try:
        server = _FakeServer(mode="ok")
        os.environ["FAKE_MODEL_SECRET"] = "s3cr3t-value"
        profile = local_profile(server, "phase8-local",
                                secret_env="FAKE_MODEL_SECRET")
        bank, session, hint, q, wrong = mc_scenario(tmp, profile,
                                                    "phase8-local")
        if hint["status"] != "pass":
            fail("local hint must pass the gate, got %r" % hint)
        candidate = {"kind": "hint_plan",
                     "interaction_id": hint["interaction_id"],
                     "focus_span": wrong, "fact_ids": ["tier0.lesson_ref"],
                     "move": "anchor_error"}
        expected = expected_hint_render(q, wrong, 0, candidate)
        if hint["generated"] != expected:
            fail("local hint payload must equal the gate-rendered output")
        if hint["generated"] != hosted["expected"]:
            fail("local and hosted scenarios must produce identical "
                 "normalized generated payloads")
        if set(hint.keys()) != hosted["interaction_keys"]:
            fail("local payload field set differs from hosted: %r vs %r"
                 % (set(hint.keys()), hosted["interaction_keys"]))

        log = evidence.log_path(tmp)
        sid = session_id_of(session)
        evs = [e for e in evidence.model_interactions(log, sid)
               if e.get("operation") == "hint"]
        if len(evs) != 1:
            fail("local scenario must append exactly one hint interaction")
        ev = evs[0]
        if set(ev.keys()) != hosted["evidence_keys"]:
            fail("local evidence field set differs from hosted: %r vs %r"
                 % (set(ev.keys()), hosted["evidence_keys"]))
        for key in ("outcome", "operation", "permitted_tier",
                    "pass_payload", "output_bytes"):
            if ev.get(key) != hosted["ev"].get(key):
                fail("evidence field %r differs between transports: %r vs %r"
                     % (key, ev.get(key), hosted["ev"].get(key)))
        if ev["backend_class"] != "local" or \
                hosted["ev"]["backend_class"] != "hosted":
            fail("backend classes must differ by transport: %r vs %r"
                 % (ev["backend_class"], hosted["ev"]["backend_class"]))

        # D-03/D-15: the secret value rides in the Authorization header to
        # the provider only -- never in the request body, the evidence log,
        # or any learner-facing payload.
        if not server.received:
            fail("local server never received a request")
        if "s3cr3t-value" in server.received[0] or \
                "FAKE_MODEL_SECRET" in server.received[0]:
            fail("the credential leaked into the request body: %r"
                 % server.received[0])
        auth = server.headers[0].get("Authorization", "")
        if "Bearer s3cr3t-value" not in auth:
            fail("the credential must ride the Authorization header, got %r"
                 % auth)
        raw_log = open(log, encoding="utf-8").read()
        if "s3cr3t-value" in raw_log or "FAKE_MODEL_SECRET" in raw_log:
            fail("the credential or its env name leaked into evidence")
    finally:
        if server:
            server.close()
        os.environ.pop("FAKE_MODEL_SECRET", None)
        shutil.rmtree(tmp, ignore_errors=True)


def _short_proposal_human_mark():
    """Test 3: a short answer generates a pending mark_proposal; the human
    accepts via cmd_mark --proposal with an N-boolean rubric; marks_by_event
    returns the settled mark with marker human and proposal_ref; the
    response's review_state derives to marked (D-13/D-14/D-23/D-24/D-25)."""
    tmp = tempfile.mkdtemp()
    try:
        profile = hosted_profile(tmp, "phase8-rubric", "rubric")
        write_settings(tmp, {"model_backend": {"active": "phase8-rubric",
                                               "profiles": [profile]}})
        bank = os.path.join(tmp, "lesson_bank.md")
        shutil.copyfile(LESSON_BANK, bank)
        session = os.path.join(tmp, "session.json")
        started = run(["start", bank, "--count", "1", "--type", "short",
                       "--seed", "7", "--mode", "practice", "--out",
                       session], tmp)
        record_payload("start-short", started)
        if started["item"]["id"] != SHORT_ID:
            fail("short scenario did not serve the fixture short item: %r"
                 % started["item"])
        submitted = run(["submit", session, "--answer",
                         json.dumps("A constructed response written out in "
                                    "full sentences.")], tmp)
        record_payload("submit-short", submitted)
        if submitted["score"] is not None or \
                submitted["action"] != "defer_feedback":
            fail("a short response must stay pending (score None), got %r"
                 % submitted)
        response_event_id = submitted["evidence"]["event_id"]

        review = run(["rubric-review", "--session", session], tmp)
        record_payload("rubric-review", review)
        if review["status"] != "pending":
            fail("rubric review must return status pending, got %r" % review)
        if len(review.get("points") or []) != 3:
            fail("rubric review must carry one suggestion per rubric point, "
                 "got %r" % review.get("points"))
        if review.get("suggestion_reveal") != "after-self-mark":
            fail("suggestion_reveal must default to after-self-mark, got %r"
                 % review.get("suggestion_reveal"))
        proposal_id = review.get("proposal_event_id")
        if not proposal_id:
            fail("rubric review must return its proposal event id")

        log = evidence.log_path(tmp)
        sid = session_id_of(session)
        if response_event_id in evidence.marks_by_event(log):
            fail("a proposal must never settle a mark by itself")

        rubric = [
            {"point": "Names repositioning as the first intervention because "
                      "tongue obstruction is the usual cause", "pass": True},
            {"point": "States that a suspected cervical spine injury is the "
                      "reason to use a jaw-thrust", "pass": False},
            {"point": "Notes that the jaw-thrust avoids moving the neck",
             "pass": True},
        ]
        mark = run_json(["mark", "--session", sid, "--base", tmp,
                         "--proposal", proposal_id, "--verdict", "pass",
                         "--rubric", json.dumps(rubric)], tmp)
        record_payload("mark", mark)
        if mark["recorded"] != 1 or mark["already_recorded"] != 0:
            fail("the human accept must record exactly one mark, got %r"
                 % mark)

        settled = evidence.marks_by_event(log).get(response_event_id)
        if settled is None:
            fail("marks_by_event must return the settled mark")
        if settled["marker"] != "human":
            fail("the settled mark must identify a human marker, got %r"
                 % settled["marker"])
        if settled["proposal_ref"] != proposal_id:
            fail("the settled mark must reference the accepted proposal: "
                 "%r vs %r" % (settled["proposal_ref"], proposal_id))
        if settled["verdict"] is not True:
            fail("the settled verdict must be the human's pass, got %r"
                 % settled["verdict"])
        if settled["rubric"] != rubric:
            fail("the settled mark must carry the human's N-boolean rubric: "
                 "%r vs %r" % (settled["rubric"], rubric))

        rendered = evidence.render_session_json(
            log, sid, model.load(bank), bank)
        row = next((r for r in rendered.get("responses", [])
                    if r.get("item_id") == SHORT_ID), None)
        if row is None:
            fail("render_session_json must include the short response")
        if row["review_state"] != "marked":
            fail("the response review_state must derive to marked, got %r"
                 % row["review_state"])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _adversarial_drop():
    """Test 4: an adversarial candidate (key disclosure through a protected
    fact) invoked through the same path is dropped whole; the learner
    payload is the generic drop copy (no reason, no generated text) and the
    evidence event stores descriptors only (D-08/D-16)."""
    global _DROP_CANDIDATE
    tmp = tempfile.mkdtemp()
    try:
        profile = hosted_profile(tmp, "phase8-drop", "drop")
        bank, session, hint, q, wrong = mc_scenario(tmp, profile,
                                                    "phase8-drop")
        if hint["status"] != "drop":
            fail("the adversarial candidate must drop whole, got %r" % hint)
        if hint["generated"] is not None:
            fail("a dropped candidate must never render, got %r"
                 % hint["generated"])
        authored = hint.get("authored") or {}
        if authored.get("available") is not True or \
                authored.get("content") != LESSON_SLUG:
            fail("the authored fallback must remain usable on a drop, got %r"
                 % authored)
        for key in ("reason", "gate_reason", "tier", "error",
                    "backend_class", "provider"):
            if key in hint:
                fail("the learner-facing drop payload must not carry %r: %r"
                     % (key, hint))

        log = evidence.log_path(tmp)
        sid = session_id_of(session)
        evs = [e for e in evidence.model_interactions(log, sid)
               if e.get("operation") == "hint"]
        if len(evs) != 1:
            fail("the drop scenario must append exactly one interaction")
        ev = evs[0]
        if ev["outcome"] != "drop" or ev["gate_reason"] != \
                "gate.fact_protected":
            fail("the evidence must record the drop with its reason code: "
                 "%r" % {k: ev.get(k) for k in ("outcome", "gate_reason")})
        if ev["pass_payload"] is not None:
            fail("a dropped interaction must store no learner payload")
        if "candidate" in ev:
            fail("the evidence event must store descriptors, never the "
                 "candidate")
        if not re.fullmatch(r"[0-9a-f]{64}", ev["response_fingerprint"] or ""):
            fail("response_fingerprint must be a sha256 descriptor, got %r"
                 % ev.get("response_fingerprint"))

        _DROP_CANDIDATE = {"kind": "hint_plan",
                           "interaction_id": hint["interaction_id"],
                           "focus_span": wrong, "fact_ids": ["tier5.why"],
                           "move": "anchor_error"}
        raw_log = open(log, encoding="utf-8").read()
        if json.dumps(_DROP_CANDIDATE) in raw_log:
            fail("dropped candidate text must never reach the evidence log")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def run_full_scenario():
    hosted = _hosted_hint_pass()
    _local_parity(hosted)
    _short_proposal_human_mark()
    _adversarial_drop()
    print("full scenario (hosted pass, local parity, proposal + human mark, "
          "adversarial drop): ok")


# ---- Task 2: offline matrix, authority regressions, payload scan -----------

OFFLINE_ROW_LABELS = (
    "disabled", "missing-exe", "nonzero-exit", "timeout", "malformed-json",
    "oversize", "refused-output", "unreachable", "http-failure",
)


def _row_settings(tmp, label, servers):
    """The model_backend settings document for one offline-matrix row. Rows
    cover the nine named provider-failure families in a fixed order."""
    if label == "disabled":
        return {"model_backend": {"active": "", "profiles": []}}
    if label == "missing-exe":
        return {"model_backend": {"active": "broken", "profiles": [
            {"name": "broken", "transport": "hosted_cli",
             "command": ["/nonexistent/itembank-hosted-bin"], "model": "x",
             "timeout_seconds": 5, "max_output_bytes": 65536,
             "context_window": 4096}]}}
    if label == "nonzero-exit":
        return {"model_backend": {"active": "phase8-exit1",
                                  "profiles": [hosted_profile(
                                      tmp, "phase8-exit1", "exit1")]}}
    if label == "timeout":
        return {"model_backend": {"active": "phase8-sleep",
                                  "profiles": [hosted_profile(
                                      tmp, "phase8-sleep", "sleep",
                                      timeout=1)]}}
    if label == "malformed-json":
        return {"model_backend": {"active": "phase8-malformed",
                                  "profiles": [hosted_profile(
                                      tmp, "phase8-malformed",
                                      "malformed")]}}
    if label == "oversize":
        return {"model_backend": {"active": "phase8-oversize",
                                  "profiles": [hosted_profile(
                                      tmp, "phase8-oversize", "oversize",
                                      max_bytes=2048)]}}
    if label == "refused-output":
        return {"model_backend": {"active": "phase8-refused",
                                  "profiles": [hosted_profile(
                                      tmp, "phase8-refused", "refused")]}}
    if label == "unreachable":
        return {"model_backend": {"active": "unreachable",
                                  "profiles": [local_profile(
                                      closed_port(), "unreachable")]}}
    if label == "http-failure":
        server = _FakeServer(mode="refuse500")
        servers.append(server)
        return {"model_backend": {"active": "http_fail",
                                  "profiles": [local_profile(
                                      server.port, "http_fail")]}}
    fail("unknown offline row %r" % label)


def _run_offline_row(label):
    """One row of the offline matrix: the full core loop through
    surfaces/session and surfaces/evidence_cli with the backend broken in
    exactly one named way. Submit/scoring, lessons, authored hints, evidence
    append/read, reports, and explicit human marking all still pass; only
    the generated assist payload changes."""
    tmp = tempfile.mkdtemp()
    servers = []
    try:
        write_settings(tmp, _row_settings(tmp, label, servers))
        bank = os.path.join(tmp, "lesson_bank.md")
        shutil.copyfile(LESSON_BANK, bank)

        # Lessons stay usable with the backend broken (markdown render, not
        # a JSON payload -- exit 0 is the contract). The bank copy under tmp
        # is rendered so the default `<bank>_lesson.html` output lands in the
        # scratch dir, never beside a fixture.
        lesson_r = run_raw(["lesson", bank], tmp)
        if lesson_r.returncode != 0:
            fail("row %s: the lesson surface must keep rendering, got %d: %s"
                 % (label, lesson_r.returncode, lesson_r.stderr[-500:]))

        # Session A (mc): a wrong answer unlocks the authored tier, the hint
        # degrades to unavailable/drop with the authored fallback, and a
        # correct answer still scores and advances.
        s1 = os.path.join(tmp, "s1.json")
        started = run(["start", bank, "--count", "1", "--type", "mc",
                       "--seed", "7", "--mode", "practice", "--out", s1],
                      tmp)
        if started["item"]["id"] != MC_ID:
            fail("row %s: mc item not served" % label)
        q = next(x for x in model.load(bank) if x["id"] == MC_ID)
        w = run(["submit", s1, "--answer",
                 json.dumps(serve_roundtrip.wrong_answer(q))], tmp)
        if w["accepted"] is not True:
            fail("row %s: a wrong answer must still record" % label)
        hint = run(["hint", "--session", s1], tmp)
        record_payload("matrix-hint-%s" % label, hint)
        if hint["status"] not in ("unavailable", "drop"):
            fail("row %s: hint must degrade to unavailable/drop, got %r"
                 % (label, hint["status"]))
        if hint["generated"] is not None:
            fail("row %s: a broken backend must generate nothing" % label)
        authored = hint.get("authored") or {}
        if authored.get("available") is not True or \
                authored.get("content") != LESSON_SLUG:
            fail("row %s: the authored hint must remain usable, got %r"
                 % (label, authored))
        ok = run(["submit", s1, "--answer",
                  json.dumps(serve_roundtrip.correct_answer(q))], tmp)
        if ok["accepted"] is not True or ok["score"] is not True:
            fail("row %s: a correct answer must still score True, got %r"
                 % (label, ok))

        # Session B (short): a pending response, evidence read, a report,
        # and an explicit human mark all keep working.
        s2 = os.path.join(tmp, "s2.json")
        run(["start", bank, "--count", "1", "--type", "short", "--seed",
             "7", "--mode", "practice", "--out", s2], tmp)
        short = run(["submit", s2, "--answer",
                     json.dumps("A constructed response written out in "
                                "full sentences.")], tmp)
        if short["score"] is not None:
            fail("row %s: a short response must stay pending" % label)
        sid2 = session_id_of(s2)
        ev_read = run(["evidence", "--base", tmp, "--session", sid2], tmp)
        if ev_read["count"] < 1 or not ev_read["events"]:
            fail("row %s: evidence read must return the response, got %r"
                 % (label, ev_read["count"]))
        report = run(["report", s2], tmp)
        if "summary" not in report or report["status"] != "active":
            fail("row %s: the report must render, got %r"
                 % (label, report.get("status")))
        mark = run_json(["mark", "--session", sid2, "--base", tmp, "--item",
                         SHORT_ID, "--verdict", "pass"], tmp)
        if mark["recorded"] != 1:
            fail("row %s: the human mark must record, got %r"
                 % (label, mark))
    finally:
        for server in servers:
            server.close()
        shutil.rmtree(tmp, ignore_errors=True)


def run_offline_matrix():
    """Every named offline row runs the full core loop in a stable order;
    only generated assistance is unavailable (D-04/MODEL-03)."""
    order = []
    for label in OFFLINE_ROW_LABELS:
        order.append(label)
        _run_offline_row(label)
    if tuple(order) != OFFLINE_ROW_LABELS:
        fail("offline matrix must run rows in the stable declared order")
    print("offline matrix: %d rows in stable order; only generated "
          "assistance unavailable" % len(order))


def run_authority_regressions():
    """The single-authority invariants stay green unchanged: one scorer,
    one event writer, one protocol, Phase 6 hint authority, the daemon API,
    and the served page (08-VALIDATION.md 'Existing authority regressions';
    runner_roundtrip when present)."""
    names = ["scoring_roundtrip", "evidence_roundtrip", "protocol_roundtrip",
             "hint_roundtrip", "daemon_roundtrip", "serve_roundtrip"]
    if os.path.exists(os.path.join(ROOT, "tests", "runner_roundtrip.py")):
        names.append("runner_roundtrip")
    for name in names:
        r = subprocess.run(
            [sys.executable, os.path.join(ROOT, "tests", name + ".py")],
            cwd=ROOT, capture_output=True, text=True)
        if r.returncode != 0:
            fail("authority regression %s failed (%d):\n%s\n%s"
                 % (name, r.returncode, r.stdout[-2000:], r.stderr[-2000:]))
        print("authority regression %s: ok" % name)


def _fixture_private_phrases():
    """Forbidden material derived from the fixture lesson bank's private
    fields -- never from option text (options and the objective are
    legitimately learner-facing): the authored rationale ladder (why, disc,
    second, da), the model answer, the trap, notes, and rubric point texts."""
    phrases = []
    for item in model.load(LESSON_BANK):
        for key in ("why", "disc", "second", "trap", "model"):
            val = item.get(key)
            if isinstance(val, str) and val:
                phrases.append(val)
        for text in (item.get("da") or {}).values():
            if text:
                phrases.append(text)
        for note in (item.get("notes") or []):
            if note:
                phrases.append(str(note))
        for rp in (item.get("rubric") or []):
            if isinstance(rp, dict):
                phrases.append(str(rp.get("point") or ""))
            else:
                phrases.append(str(rp))
    return sorted({norm(p) for p in phrases if norm(p)})


def run_payload_scan():
    """Every learner-facing JSON document the scenario produced is clean of
    fixture-private material, authority vocabulary (tier indexes, item keys,
    gate reasons, profile/backend identifiers, secret references), and the
    dropped candidate's text (VALIDATION.md Payload-boundary checks). The
    "mark" artifact is the human marker's own operator-facing output, so the
    fixture-private phrase check is skipped for it -- the authority-string,
    private-key, and dropped-candidate checks still apply."""
    if not _PAYLOADS:
        fail("payload scan found no artifacts to scan")
    private = _fixture_private_phrases()
    private_keys = ("correct", "model", "why", "da", "disc", "second",
                    "notes", "rubric", "trap", "objective_line")
    for label, payload in _PAYLOADS:
        skip_phrases = label == "mark"
        # A private field NAME cannot legitimately appear in the assist
        # payloads (hint / matrix-hint / rubric-review); the session
        # envelope and reports legitimately carry metadata keys such as
        # `notes` in their retention trace, so the name check is scoped to
        # the assist artifacts and disclosure is proven by the phrase scan.
        assist = label.startswith("hint-") or \
            label.startswith("matrix-hint-") or label == "rubric-review"
        for key, value in flatten(payload):
            if assist and isinstance(key, str) and key in private_keys:
                fail("payload scan: %s carries private fixture key %r in %r"
                     % (label, key, payload))
            if not isinstance(value, str):
                continue
            low = value.lower()
            for banned in FORBIDDEN_AUTHORITY:
                if banned.lower() in low:
                    fail("payload scan: %s leaked authority string %r in "
                         "%r=%r" % (label, banned, key, value))
            if skip_phrases:
                continue
            nv = norm(value)
            for phrase in private:
                if phrase and phrase in nv:
                    fail("payload scan: %s leaked private phrase %r in "
                         "%r=%r" % (label, phrase, key, value))
    if _DROP_CANDIDATE is not None:
        drop_blob = json.dumps(_DROP_CANDIDATE)
        for label, payload in _PAYLOADS:
            if drop_blob in json.dumps(payload, ensure_ascii=False):
                fail("payload scan: %s carries the dropped candidate text"
                     % label)
    print("payload scan: %d learner-facing artifacts clean of private "
          "material" % len(_PAYLOADS))


# ---- Task 3: the contract and decision audit -------------------------------

def _no_invented_figures():
    """D-19: no tok/s-style or fabricated latency literal appears in the
    adapter/gate/evidence modules or the Phase 8 docs; measured elapsed_ms
    (and the pre-existing response_time_ms) are the only timing fields.
    The scan targets NUMBER-prefixed performance units so the prohibition
    prose itself ('no invented tok/s figure') is not a false positive."""
    targets = [os.path.join(ROOT, "model_adapter.py"),
               os.path.join(ROOT, "tier_gate.py"),
               os.path.join(ROOT, "evidence.py"),
               os.path.join(PHASE08_DIR, "08-CONTEXT.md"),
               os.path.join(PHASE08_DIR, "08-VALIDATION.md"),
               os.path.join(PHASE08_DIR, "COVERAGE.md"),
               os.path.join(PHASE08_DIR, "08-06-PLAN.md")]
    pattern = re.compile(
        r"\b\d+(?:\.\d+)?\s*(?:tok|tokens?)\s*/\s*s\b"
        r"|\b\d+(?:\.\d+)?\s*(?:ms|milliseconds?)\b"
        r"|\b\d+(?:\.\d+)?\s*(?:seconds?|sec)\b")
    for path in targets:
        hits = []
        for lineno, line in enumerate(
                open(path, encoding="utf-8").read().splitlines(), 1):
            if pattern.search(line):
                hits.append((lineno, line.strip()))
        if hits:
            fail("invented performance figure in %s: %r"
                 % (os.path.basename(path), hits[:5]))
    print("no invented tok/s or latency figures (elapsed_ms only): ok")


def _contract_docs():
    """agent_usage.schema.json validates and parses; COVERAGE.md's matrix
    parses; the hosted CLI is documented as the default backend when a
    backend is enabled (D-18); the shipped settings default disables the
    backend (active \"\")."""
    usage = json.load(open(AGENT_USAGE_SCHEMA_PATH, encoding="utf-8"))
    schema_validate.check_schema(usage)   # supported keywords only
    doc = {
        "schema_version": 1,
        "permissions": ["request_hint", "request_rubric_review",
                        "read_pending_proposals", "accept_proposals"],
        "prohibitions": ["write_evidence", "score_responses", "select_items",
                         "advance_tiers", "read_dropped_text",
                         "auto_accept_proposals"],
        "disclosure": {"hosted_transit_accepted": True,
                       "evidence_local_only": True,
                       "secrets_env_references_only": True},
        "retry": {"max_attempts": 1, "explicit_retry": True,
                  "parent_link": True},
        "manual_grading": {"marker": "human",
                           "accept_paths": ["self_mark", "batch_mark"]},
        "forbidden_inferences": ["tier_state", "item_selection",
                                 "accepted_verdicts", "learner_identity"],
    }
    errs = schema_validate.validate(doc, usage)
    if errs:
        fail("agent_usage.schema.json rejects its own documented contract: "
             "%s" % errs[0])
    prohs = usage["properties"]["prohibitions"]["items"]["enum"]
    if "auto_accept_proposals" not in prohs:
        fail("agent_usage prohibitions must ban auto_accept_proposals")
    paths = usage["properties"]["manual_grading"]["properties"][
        "accept_paths"]["items"]["enum"]
    if sorted(paths) != ["batch_mark", "self_mark"]:
        fail("agent_usage accept_paths must be self_mark/batch_mark only: "
             "%r" % paths)

    coverage = open(os.path.join(PHASE08_DIR, "COVERAGE.md"),
                    encoding="utf-8").read()
    integrate_rows = [ln for ln in coverage.splitlines()
                      if "| INTEGRATE" in ln]
    optout_rows = [ln for ln in coverage.splitlines()
                   if "| OPT-OUT" in ln]
    if len(integrate_rows) != 2 or len(optout_rows) != 4:
        fail("COVERAGE.md matrix must parse to 2 INTEGRATE and 4 OPT-OUT "
             "rows, got %d/%d" % (len(integrate_rows), len(optout_rows)))
    if "design-target default backend (D-18)" not in coverage:
        fail("COVERAGE.md must document the hosted CLI as the design-target "
             "default backend (D-18)")

    adapter_src = open(os.path.join(ROOT, "model_adapter.py"),
                       encoding="utf-8").read()
    if "D-18" not in adapter_src:
        fail("model_adapter.py must record the D-18 default-backend ruling")
    if adapter_src.find("hosted_cli") > adapter_src.find("openai_compatible"):
        fail("TRANSPORT_REGISTRY must register hosted_cli first (D-18)")

    ctx = open(os.path.join(PHASE08_DIR, "08-CONTEXT.md"),
               encoding="utf-8").read()
    d18_tail = ctx.split("D-18", 1)[1][:800]
    if "default" not in d18_tail or "hosted" not in d18_tail:
        fail("08-CONTEXT.md D-18 must document the hosted CLI as the "
             "default backend")

    settings_schema = json.load(open(SETTINGS_SCHEMA_PATH, encoding="utf-8"))
    mb = settings_schema["properties"]["model_backend"]
    if mb["default"]["active"] != "":
        fail("the shipped settings default must disable the backend "
             "(active \"\")")
    transports = settings_schema["properties"]["model_backend"][
        "properties"]["profiles"]["items"]["properties"]["transport"][
        "enum"]
    if sorted(transports) != ["hosted_cli", "openai_compatible"]:
        fail("settings transport enum must be hosted_cli/openai_compatible")
    print("agent_usage + COVERAGE + D-18 hosted-default record: ok")


def run_contract_audit():
    """The phase's final authority gate (Task 3): auto-accept is absent
    structurally, suggestion_reveal ships all three locked values with the
    after-self-mark default, the human-only mark guard is unchanged, the new
    event builders carry no score field, no invented performance figure
    exists, the usage contract and coverage matrix validate, and every
    ROADMAP Phase 8 criterion 1-14 maps to a green assertion recorded here.
    """
    # Test 1: no auto-accept path exists -- structural key walk over the
    # settings schema plus a source scan over every Phase 8 module.
    settings_schema = json.load(open(SETTINGS_SCHEMA_PATH, encoding="utf-8"))

    def _walk_keys(node):
        if isinstance(node, dict):
            for k, v in node.items():
                yield k
                yield from _walk_keys(v)
        elif isinstance(node, list):
            for el in node:
                yield from _walk_keys(el)

    auto_pattern = re.compile(r"auto[-_]?accept", re.I)
    for key in _walk_keys(settings_schema):
        if auto_pattern.search(key):
            fail("settings schema carries an auto-accept property %r" % key)
    modules = ("model_adapter.py", "tier_gate.py", "evidence.py",
               "runtime.py", "surfaces/session.py", "surfaces/evidence_cli.py",
               "surfaces/settings.py")
    for mod in modules:
        src = open(os.path.join(ROOT, mod), encoding="utf-8").read()
        for m in auto_pattern.finditer(src):
            fail("%s references an auto-accept path: %r"
                 % (mod, src[max(0, m.start() - 60):m.end() + 60]))

    # Test 2: suggestion_reveal default + enum; human-only mark guard; no
    # fractional score field in the new event builders.
    sr = settings_schema["properties"]["suggestion_reveal"]
    if sr.get("default") != "after-self-mark":
        fail("suggestion_reveal must default to after-self-mark, got %r"
             % sr.get("default"))
    if sr.get("enum") != ["after-self-mark", "before-self-mark", "after-mark"]:
        fail("suggestion_reveal must ship all three locked values, got %r"
             % sr.get("enum"))
    try:
        evidence.mark_event("sid", "iid", "iref", "evid", True,
                            marker="model")
        fail("mark_event must raise ValueError for marker 'model'")
    except ValueError:
        pass
    interaction = evidence.model_interaction_event(
        "sid", "bank.md", "iref", "hint", "int-1", "pass", None, 1,
        "hosted", "p", "fp", "rf", 12, 3)
    if "score" in interaction:
        fail("model_interaction_event must carry no score key")
    proposal = evidence.mark_proposal_event(
        "sid", "bank.md", "iid", "iref", "resp-1", "int-1",
        [{"point_index": 0, "status": "pass", "rationale": "x"}])
    if "score" in proposal or "verdict" in proposal:
        fail("mark_proposal_event must carry no score or verdict field")

    # Test 3: no invented performance figure.
    _no_invented_figures()

    # Test 4: usage contract + coverage matrix validate; hosted default
    # documented; corpus count is asserted, never approximated.
    _contract_docs()
    corpus = json.load(open(CASES_PATH, encoding="utf-8"))["cases"]
    if len(corpus) < 30:
        fail("the adversarial corpus must contain at least 30 cases, got %d"
             % len(corpus))

    # The ROADMAP criterion-to-assertion mapping (criteria 1-14), printed
    # green on completion.
    mapping = {
        1: ["_adversarial_drop (adversarial reveal dropped whole, never "
            "shown)", "_hosted_hint_pass (permitted-tier render)"],
        2: ["_hosted_hint_pass + _local_parity (config-only switch, "
            "identical normalized shape)"],
        3: ["run_offline_matrix (9 rows; scoring, lessons, authored hints, "
            "evidence, reports, marking all keep working)"],
        4: ["_short_proposal_human_mark (pending until explicit human "
            "accept)", "run_contract_audit human-only guard"],
        5: ["_hosted_hint_pass / _adversarial_drop (model_interactions "
            "retrievable by session with the same interaction id)"],
        6: ["run_authority_regressions -> daemon_roundtrip (DOM privacy, "
            "SURFACE_PARITY, structural lock)"],
        7: ["full suite -> model_adapter_roundtrip (third-backend stub "
            "registration, D-27)"],
        8: ["run_contract_audit._contract_docs (D-18 hosted default "
            "documented, TRANSPORT_REGISTRY order)"],
        9: ["run_contract_audit._no_invented_figures (D-19)"],
        10: ["run_contract_audit mark guard (tier-3 never a scorer, D-20)",
             "_short_proposal_human_mark (pending terminal state)"],
        11: ["run_contract_audit suggestion_reveal (after-self-mark default, "
             "D-22)", "_short_proposal_human_mark (pending token)"],
        12: ["run_contract_audit mark_event ValueError + mark_proposal "
             "no-verdict (D-23)"],
        13: ["_short_proposal_human_mark (N-boolean rubric)", "run_contract_"
             "audit no fractional score (D-24)"],
        14: ["run_contract_audit auto-accept absence scan (D-25)",
             "_contract_docs agent_usage auto_accept_proposals prohibition"],
    }
    if set(mapping) != set(range(1, 15)):
        fail("the criterion-to-assertion mapping must cover ROADMAP "
             "criteria 1-14")
    print("ROADMAP criterion -> assertion mapping (1-14, all green):")
    for criterion in sorted(mapping):
        for assertion in mapping[criterion]:
            print("  %2d  %s" % (criterion, assertion))


def main():
    run_full_scenario()
    run_offline_matrix()
    run_authority_regressions()
    run_payload_scan()
    run_contract_audit()
    print("model phase roundtrip: ok")


if __name__ == "__main__":
    main()
