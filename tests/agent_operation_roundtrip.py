#!/usr/bin/env python3
"""Plan 17A-07: the Agent area's run-propose-accept state machine.

The plan joins two halves that already shipped and were never wired:
model_adapter.invoke (the only way this page may reach a model) and
journal.commit_operation (the only way a draft becomes a real change).
This suite holds the machine to both boundaries and to no others.

Nothing here needs the network. Every endpoint is a loopback stub or a
closed port, the same discipline tests/local_harness_roundtrip.py uses.
"""
import json
import os
import shutil
import socket
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "surfaces"))

import model_adapter                                        # noqa: E402
import journal                                              # noqa: E402
import identity                                             # noqa: E402
from surfaces import agent_operation as ao                  # noqa: E402

PROFILE_NAME = "local-qwen"
SKILL = "author-bank"
TARGET = "banks/lesson-draft.md"
KIND = "bank"
ORIGINAL = "# Lesson draft\n\nWritten by hand before any run.\n"
DRAFT = ("# Lesson draft\n\nRewritten by the model draft.\n\n"
         "Q1. Which boundary settles a score? [OBJECTIVE: a1]\n")
CITATIONS = ["LESSON: What a predicate is", "source: syllabus p.12"]

failures = []


def fail(msg):
    failures.append(msg)
    print("FAIL: " + msg)


def ok(msg):
    print("OK   " + msg)


def make_settings(active=None, profiles=None, autonomy=None, runs=True):
    doc = {"model_backend": {
        "active": active or "",
        "profiles": profiles if profiles is not None else []}}
    if autonomy is not None:
        doc["auditor_autonomy"] = autonomy
    if runs:
        doc["agent_runs"] = {SKILL: {"target": TARGET, "kind": KIND}}
    return doc


def local_profile(port, timeout=5):
    return {"name": PROFILE_NAME, "transport": "openai_compatible",
            "endpoint": "http://127.0.0.1:%d/v1/chat/completions" % port,
            "model": "qwen3.8-27b:latest",
            "timeout_seconds": timeout,
            "max_output_bytes": 65536,
            "context_window": 32768}


def closed_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


class _Stub(object):
    """A loopback stub standing in for the model backend. The default
    answers with a well-formed authoring candidate; candidate= overrides
    the body outright; mode "junk" answers with well-formed JSON that is
    not a candidate at all."""

    def __init__(self, mode="author", candidate=None):
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                length = int(self.headers.get("Content-Length") or 0)
                self.rfile.read(length)
                if outer.candidate is not None:
                    body = json.dumps(outer.candidate).encode("utf-8")
                elif outer.mode == "junk":
                    body = json.dumps({"weather": "sunny"}).encode("utf-8")
                else:
                    body = json.dumps({
                        "draft": DRAFT,
                        "citations": CITATIONS}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                try:
                    self.wfile.write(body)
                except (BrokenPipeError, ConnectionResetError):
                    pass

            def log_message(self, *args):
                pass

        self.mode = mode
        self.candidate = candidate
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
        self.thread.join(timeout=3)


class _Course(object):
    """A temporary approved root with one existing target file."""

    def __init__(self):
        self.base = tempfile.mkdtemp(prefix="itembank-17a07-")
        os.makedirs(os.path.join(self.base, os.path.dirname(TARGET)))
        with open(os.path.join(self.base, TARGET), "w",
                  encoding="utf-8") as fh:
            fh.write(ORIGINAL)

    def path(self, rel=TARGET):
        return os.path.join(self.base, rel)

    def bytes(self, rel=TARGET):
        with open(self.path(rel), "rb") as fh:
            return fh.read()

    def journal_lines(self):
        log = journal.log_path(self.base)
        if not os.path.exists(log):
            return []
        with open(log, encoding="utf-8") as fh:
            return [json.loads(line) for line in fh if line.strip()]

    def close(self):
        shutil.rmtree(self.base, ignore_errors=True)


def check_only_four_states_exist():
    """The machine is bounded: idle, running, proposed, settled, and no
    fifth state can appear in any state dict it returns."""
    if ao.STATES != ("idle", "running", "proposed", "settled"):
        fail("STATES is %r, not the four named states" % (ao.STATES,))
        return
    idle = ao.idle()
    if idle.get("state") != "idle":
        fail("idle() returned %r" % (idle,))
        return
    ok("the machine declares exactly idle, running, proposed, settled")


def check_next_actions_cover_every_adapter_code():
    """One next action per code in ADAPTER_CODES, no fewer and no more.
    A missing entry is a test failure, never a fallback, so a new adapter
    code cannot ship with no copy on the page."""
    codes = set(model_adapter.ADAPTER_CODES)
    named = set(ao.NEXT_ACTIONS)
    if named != codes:
        fail("NEXT_ACTIONS covers %d of %d adapter codes (missing %r, "
             "extra %r)" % (len(named & codes), len(codes),
                            sorted(codes - named)[:3],
                            sorted(named - codes)[:3]))
        return
    for code, action in ao.NEXT_ACTIONS.items():
        if not isinstance(action, str) or len(action) < 20:
            fail("next action for %s is not a real sentence" % code)
            return
    if "Studying" not in ao.NEXT_ACTIONS["adapter.profile_disabled"]:
        fail("the no-active-profile copy does not say studying continues")
        return
    ok("every one of the %d adapter codes has a named next action"
       % len(codes))


def check_no_active_profile_is_first_class():
    """The shipped state of a fresh install: model_backend.active empty.
    resolve_profile refuses every name then, so a run settles immediately
    with the typed code, its copy, and zero journal lines."""
    course = _Course()
    try:
        state = ao.start(SKILL, make_settings(), course.base)
        if state.get("state") != "settled":
            fail("no active profile gave %r, not settled" % state.get("state"))
            return
        if state.get("code") != "adapter.profile_disabled":
            fail("no active profile gave %r" % state.get("code"))
            return
        if state.get("next_action") != \
                ao.NEXT_ACTIONS["adapter.profile_disabled"]:
            fail("the settled state did not carry the map's next action")
            return
        if course.journal_lines():
            fail("a refused start wrote journal lines")
            return
        ok("an inactive backend settles first-class with its next action")
    finally:
        course.close()


def check_unreachable_endpoint_settles_typed():
    """Nothing listening is the ordinary state; it must settle typed, not
    raise, and name what to do next."""
    course = _Course()
    stub_port = closed_port()
    try:
        state = ao.start(
            SKILL,
            make_settings(PROFILE_NAME, [local_profile(stub_port)]),
            course.base)
        if state.get("code") != "adapter.unreachable":
            fail("a closed port gave %r" % state.get("code"))
            return
        if not state.get("next_action"):
            fail("adapter.unreachable carried no next action")
            return
        ok("an unreachable endpoint settles with its named next action")
    finally:
        course.close()


def check_ok_result_proposes_a_bounded_diff():
    """An ok candidate becomes proposed: draft, citations, target, and a
    difflib diff against the current bytes, with the expected base
    fingerprint the proposal was computed against."""
    course = _Course()
    stub = _Stub("author")
    try:
        state = ao.start(
            SKILL,
            make_settings(PROFILE_NAME, [local_profile(stub.port)],
                          autonomy="draft_and_approve"),
            course.base)
    finally:
        stub.close()
    if state.get("state") != "proposed":
        fail("an ok candidate gave %r (%r)" % (state.get("state"),
                                               state.get("code")))
        return
    if state.get("draft") != DRAFT:
        fail("the proposal lost the draft text")
        return
    if list(state.get("citations") or []) != CITATIONS:
        fail("the proposal lost the citations: %r" % state.get("citations"))
        return
    if state.get("target") != TARGET:
        fail("the proposal names target %r" % state.get("target"))
        return
    expected_fp = identity.object_fingerprint(ORIGINAL.encode("utf-8"), KIND)
    if state.get("expected_fingerprint") != expected_fp:
        fail("the proposal fingerprint is not the current bytes' "
             "fingerprint")
        return
    diff = state.get("diff") or {}
    shown = diff.get("lines") or []
    if not any(line.startswith("+") for line in shown):
        fail("the diff shows no added lines: %r" % shown[:3])
        return
    if diff.get("withheld") != 0:
        fail("a small diff claimed to withhold %r lines"
             % diff.get("withheld"))
        return
    if course.bytes() != ORIGINAL.encode("utf-8"):
        fail("proposing changed the target file")
        return
    ok("an ok result proposes draft, citations, target, bounded diff")


def check_diff_cap_says_what_it_withheld():
    """A diff longer than the cap shows the cap and counts the rest out
    loud instead of truncating silently."""
    big_draft = "".join("line %d changed\n" % i for i in range(200))
    course = _Course()
    stub = _Stub(candidate={"draft": big_draft, "citations": []})
    try:
        state = ao.start(
            SKILL,
            make_settings(PROFILE_NAME, [local_profile(stub.port)],
                          autonomy="draft_and_approve"),
            course.base)
    finally:
        stub.close()
    diff = state.get("diff") or {}
    if state.get("state") != "proposed":
        fail("the big draft gave %r (%r)" % (state.get("state"),
                                             state.get("code")))
        return
    if len(diff.get("lines") or []) != ao.DIFF_MAX_LINES:
        fail("the diff showed %d lines, not the stated cap %d"
             % (len(diff.get("lines") or []), ao.DIFF_MAX_LINES))
        return
    if not diff.get("withheld"):
        fail("a capped diff did not say how many lines it withheld")
        return
    ok("a long diff shows %d lines and names the %d withheld"
       % (ao.DIFF_MAX_LINES, diff.get("withheld")))


def check_accept_writes_once_through_the_journal():
    """Accept calls journal.commit_operation once: the file carries the
    draft, the journal records exactly one operation for it, and the
    settled state carries the entry id and the prior revision."""
    course = _Course()
    stub = _Stub("author")
    try:
        settings = make_settings(PROFILE_NAME, [local_profile(stub.port)],
                                 autonomy="draft_and_approve")
        proposed = ao.start(SKILL, settings, course.base)
    finally:
        stub.close()
    settled = ao.accept(proposed, settings)
    if settled.get("state") != "settled" or not settled.get("ok"):
        fail("accept gave %r" % settled)
        return
    if course.bytes() != DRAFT.encode("utf-8"):
        fail("accept did not land the draft bytes")
        return
    entries = course.journal_lines()
    applied = [e for e in entries if e.get("state") == "applied"]
    prepared = [e for e in entries if e.get("state") == "prepared"]
    refused = [e for e in entries if e.get("state") == "refused"]
    if refused:
        fail("the happy path recorded refusals: %r"
             % [e.get("code") for e in refused])
        return
    if len(applied) != 1 or len(prepared) != 1:
        fail("one accept produced %d prepared and %d applied entries"
             % (len(prepared), len(applied)))
        return
    if applied[0].get("resolves_entry") != prepared[0].get("entry_id"):
        fail("the applied entry does not resolve the prepared one")
        return
    if settled.get("entry_id") != applied[0].get("entry_id"):
        fail("the settled state lost the journal entry id")
        return
    ok("one accept lands one journalled change, entry %s"
       % settled.get("entry_id"))


def check_double_accept_records_nothing():
    """A second submit on an already-settled state returns the same state
    unchanged and writes nothing: the guard lives in the module, so the
    page cannot double-write by passing the state twice."""
    course = _Course()
    stub = _Stub("author")
    try:
        settings = make_settings(PROFILE_NAME, [local_profile(stub.port)],
                                 autonomy="draft_and_approve")
        proposed = ao.start(SKILL, settings, course.base)
    finally:
        stub.close()
    first = ao.accept(proposed, settings)
    before = course.journal_lines()
    second = ao.accept(first, settings)
    after = course.journal_lines()
    if second != first:
        fail("a second accept returned a different state")
        return
    if len(after) != len(before):
        fail("a second accept wrote %d extra journal lines"
             % (len(after) - len(before)))
        return
    if course.bytes() != DRAFT.encode("utf-8"):
        fail("the file changed after a second accept")
        return
    ok("a second accept changes nothing and writes nothing")


def check_report_only_refuses_by_name():
    """report_only autonomy disables accept visibly: the refusal is a
    settled state naming the setting, where it lives, and what to change
    it to. Nothing is written anywhere."""
    course = _Course()
    stub = _Stub("author")
    try:
        settings = make_settings(PROFILE_NAME, [local_profile(stub.port)],
                                 autonomy="report_only")
        proposed = ao.start(SKILL, settings, course.base)
    finally:
        stub.close()
    if proposed.get("state") != "proposed":
        fail("report_only must not block proposing, gave %r"
             % proposed.get("state"))
        return
    settled = ao.accept(proposed, settings)
    if settled.get("state") != "settled" or settled.get("ok"):
        fail("report_only accept gave %r" % settled)
        return
    reason = settled.get("reason") or ""
    for needle in ("auditor_autonomy", "report_only", "draft_and_approve"):
        if needle not in reason:
            fail("the refusal reason misses %r: %r" % (needle, reason))
            return
    if course.bytes() != ORIGINAL.encode("utf-8"):
        fail("a report_only refusal changed the file")
        return
    if course.journal_lines():
        fail("a report_only refusal wrote journal lines")
        return
    again = ao.accept(proposed, settings)
    if again != settled:
        fail("retrying a refused accept diverged")
        return
    ok("report_only refuses accepts by name and writes nothing")


def check_stale_target_is_conflict_not_overwrite():
    """If the file changed between propose and accept, the write refuses
    and the page says so in words a learner can act on, naming the file.
    The edited content stays exactly as the learner left it."""
    course = _Course()
    stub = _Stub("author")
    try:
        settings = make_settings(PROFILE_NAME, [local_profile(stub.port)],
                                 autonomy="draft_and_approve")
        proposed = ao.start(SKILL, settings, course.base)
    finally:
        stub.close()
    learners_edit = "The learner rewrote this while the draft was open.\n"
    with open(course.path(), "w", encoding="utf-8") as fh:
        fh.write(learners_edit)
    settled = ao.accept(proposed, settings)
    if settled.get("state") != "settled" or settled.get("ok"):
        fail("a stale accept gave %r" % settled)
        return
    if not settled.get("conflict"):
        fail("the stale settle does not read as a conflict: %r" % settled)
        return
    if TARGET not in (settled.get("reason") or ""):
        fail("the conflict reason does not name the file: %r"
             % settled.get("reason"))
        return
    if course.bytes() != learners_edit.encode("utf-8"):
        fail("the conflict overwrote the learner's edit")
        return
    ok("a stale target settles as a conflict that names the file")


def check_junk_candidate_never_proposes():
    """Well-formed JSON that is not an authoring candidate settles with a
    typed page-level code instead of producing an empty proposal."""
    course = _Course()
    stub = _Stub("junk")
    try:
        state = ao.start(
            SKILL,
            make_settings(PROFILE_NAME, [local_profile(stub.port)]),
            course.base)
    finally:
        stub.close()
    if state.get("state") != "settled":
        fail("junk JSON gave %r" % state.get("state"))
        return
    if state.get("code") != "agent.candidate_invalid":
        fail("junk JSON gave %r, not agent.candidate_invalid"
             % state.get("code"))
        return
    ok("a candidate that is not a draft settles typed, not empty")


def check_unknown_skill_or_missing_target_names_the_problem():
    """A skill with no agent_runs entry cannot guess a file to write. It
    settles saying which skill lacks a target and where to add one."""
    course = _Course()
    try:
        state = ao.start(
            "guiding-questions",
            make_settings(),
            course.base)
        if state.get("state") != "settled":
            fail("a skill with no run spec gave %r" % state.get("state"))
            return
        if "guiding-questions" not in (state.get("reason") or ""):
            fail("the missing-target reason does not name the skill")
            return
        if "agent_runs" not in (state.get("reason") or ""):
            fail("the missing-target reason does not name agent_runs")
            return
        ok("a skill with no run target settles naming the skill and key")
    finally:
        course.close()


def main():
    check_only_four_states_exist()
    check_next_actions_cover_every_adapter_code()
    check_no_active_profile_is_first_class()
    check_unreachable_endpoint_settles_typed()
    check_ok_result_proposes_a_bounded_diff()
    check_diff_cap_says_what_it_withheld()
    check_accept_writes_once_through_the_journal()
    check_double_accept_records_nothing()
    check_report_only_refuses_by_name()
    check_stale_target_is_conflict_not_overwrite()
    check_junk_candidate_never_proposes()
    check_unknown_skill_or_missing_target_names_the_problem()
    if failures:
        print("\n%d failure(s)" % len(failures))
        return 1
    print("\nall agent-operation checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
