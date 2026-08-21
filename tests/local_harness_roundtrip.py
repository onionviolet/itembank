#!/usr/bin/env python3
"""Plan 17A-06 Task 2: the shipped local-qwen profile, and the five ways
reaching a local model can fail without taking anything else down.

Measured before this suite was written (17A-06-PLAN findings 1-3): a local
model needs a settings entry, not a transport module, because
model_adapter._transport_openai_compatible already speaks the OpenAI-compatible
protocol Ollama and llama.cpp serve, and already tags its result "local".

The field is `endpoint`. A profile written with `base_url` is the likeliest
setup mistake there is, and it fails with settings.invalid_value rather than
with a silent fallback, so it gets its own check here.

Nothing in this suite needs the network. Every endpoint is a loopback stub, a
closed port, or a socket that never answers.
"""
import json
import os
import socket
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "surfaces"))

import model_adapter                                     # noqa: E402
from surfaces.settings import resolve_profile            # noqa: E402

SETTINGS_FILE = os.path.join(ROOT, "itembank.json")
PROFILE_NAME = "local-qwen"
INTERACTION_ID = "int-17a0601"

failures = []


def fail(msg):
    failures.append(msg)
    print("FAIL: " + msg)


def ok(msg):
    print("OK   " + msg)


def shipped_settings():
    with open(SETTINGS_FILE, encoding="utf-8") as fh:
        return json.load(fh)


def make_settings(active, profiles):
    return {"model_backend": {"active": active, "profiles": profiles}}


def sample_request(profile):
    return model_adapter.request_from_operation(
        "hint", INTERACTION_ID, profile,
        item_context={"item_id": "x1", "type": "mc"},
        learner_response="the wrong answer",
        permitted_tier=2,
        fact_manifest={"tier2.trap": "The trap text."})


def closed_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


class _Stub(object):
    """A loopback stub standing in for Ollama. mode "ok" answers with a
    well-formed JSON body, mode "html" answers with a body that is not JSON
    at all (what a wrong endpoint path actually returns), and mode "hang"
    never answers, which is the only honest way to test a timeout."""

    def __init__(self, mode):
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                length = int(self.headers.get("Content-Length") or 0)
                self.rfile.read(length)
                if outer.mode == "hang":
                    outer.released.wait(10)
                    return
                if outer.mode == "html":
                    body = b"<html><body>404 page not found</body></html>"
                    ctype = "text/html"
                else:
                    body = json.dumps({
                        "kind": "hint_plan",
                        "interaction_id": INTERACTION_ID,
                        "focus_span": "the wrong answer",
                        "fact_ids": ["tier2.trap"],
                        "move": "anchor_error"}).encode("utf-8")
                    ctype = "application/json"
                self.send_response(200)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                try:
                    self.wfile.write(body)
                except (BrokenPipeError, ConnectionResetError):
                    pass

            def log_message(self, *args):
                pass

        self.mode = mode
        self.released = threading.Event()
        self.server = HTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever,
                                       daemon=True)
        self.thread.start()

    @property
    def port(self):
        return self.server.server_address[1]

    def close(self):
        self.released.set()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)


def local_profile(port, timeout=5):
    return {"name": PROFILE_NAME, "transport": "openai_compatible",
            "endpoint": "http://127.0.0.1:%d/v1/chat/completions" % port,
            "model": "qwen3.8-27b:latest",
            "timeout_seconds": timeout,
            "max_output_bytes": 65536,
            "context_window": 32768}


def check_shipped_profile_resolves():
    """The repo's own itembank.json carries local-qwen and it resolves once
    it is the active profile, so the record is exercised rather than merely
    documented.

    Measured 2026-08-21: resolve_profile refuses every name, including an
    explicitly passed one, while model_backend.active is empty. Switching a
    local model on is therefore one settings edit and not two, and the
    "fresh install phones nobody" guarantee does not depend on the registry
    being empty. This suite activates the shipped record in memory; the file
    on disk keeps active empty, which check_fresh_install_reaches_no_model
    asserts."""
    data = shipped_settings()
    profiles = data.get("model_backend", {}).get("profiles") or []
    names = [p.get("name") for p in profiles]
    if PROFILE_NAME not in names:
        fail("itembank.json ships no %r profile (found %r)"
             % (PROFILE_NAME, names))
        return
    activated = make_settings(PROFILE_NAME, profiles)
    profile, reason = resolve_profile(activated, PROFILE_NAME)
    if reason is not None:
        fail("shipped %r does not resolve once active: %r"
             % (PROFILE_NAME, reason))
        return
    if profile.get("transport") != "openai_compatible":
        fail("shipped %r uses transport %r, not the shipped local one"
             % (PROFILE_NAME, profile.get("transport")))
    if not profile.get("endpoint"):
        fail("shipped %r has no endpoint" % PROFILE_NAME)
    if "base_url" in profile:
        fail("shipped %r carries base_url, which is not a field"
             % PROFILE_NAME)
    ok("shipped %r resolves through the existing openai_compatible transport"
       % PROFILE_NAME)


def check_fresh_install_reaches_no_model():
    """Shipping a profile must not switch a model on. model_backend.active
    stays empty, so an install that nobody configured still phones nobody."""
    data = shipped_settings()
    active = data.get("model_backend", {}).get("active")
    if active:
        fail("model_backend.active is %r; shipping a profile must not "
             "activate it" % active)
        return
    profile, reason = resolve_profile(data)
    if profile is not None or \
            (reason or {}).get("code") != "adapter.profile_disabled":
        fail("empty active resolved to %r / %r instead of "
             "adapter.profile_disabled" % (profile, reason))
        return
    ok("empty active still resolves to adapter.profile_disabled")


def check_stubbed_endpoint_returns_a_result():
    stub = _Stub("ok")
    try:
        result = model_adapter.invoke(
            sample_request(PROFILE_NAME),
            make_settings(PROFILE_NAME, [local_profile(stub.port)]))
    finally:
        stub.close()
    if result["status"] != "ok":
        fail("stubbed endpoint gave %r: %r" % (result["status"], result))
        return
    if result["provider"]["backend_class"] != "local":
        fail("stubbed local endpoint tagged %r, not local"
             % result["provider"]["backend_class"])
    if result["provider"]["profile"] != PROFILE_NAME:
        fail("result names profile %r" % result["provider"]["profile"])
    if result["interaction_id"] != INTERACTION_ID:
        fail("result lost the interaction id: %r" % result["interaction_id"])
    if result["error"] is not None:
        fail("an ok result carries an error: %r" % result["error"])
    ok("a stubbed local endpoint returns a well-formed local result")


def _expect_unavailable(label, result, code):
    if result["status"] != "unavailable":
        fail("%s gave status %r, not unavailable" % (label, result["status"]))
        return
    if result["error"]["code"] != code:
        fail("%s gave code %r, not %s"
             % (label, result["error"]["code"], code))
        return
    if result["candidate"] is not None:
        fail("%s returned a candidate alongside an error" % label)
        return
    if result["interaction_id"] != INTERACTION_ID:
        fail("%s lost the interaction id" % label)
        return
    ok("%s is typed %s" % (label, code))


def check_refused_connection():
    """Nothing listening is the ordinary state of a machine whose model
    server is not running. It is a typed unavailable, never an exception."""
    settings = make_settings(PROFILE_NAME, [local_profile(closed_port())])
    _expect_unavailable("a refused connection",
                        model_adapter.invoke(sample_request(PROFILE_NAME),
                                             settings),
                        "adapter.unreachable")


def check_timeout():
    stub = _Stub("hang")
    try:
        result = model_adapter.invoke(
            sample_request(PROFILE_NAME),
            make_settings(PROFILE_NAME,
                          [local_profile(stub.port, timeout=1)]))
    finally:
        stub.close()
    _expect_unavailable("a server that never answers", result,
                        "adapter.timeout")


def check_non_json_body():
    stub = _Stub("html")
    try:
        result = model_adapter.invoke(
            sample_request(PROFILE_NAME),
            make_settings(PROFILE_NAME, [local_profile(stub.port)]))
    finally:
        stub.close()
    _expect_unavailable("a non-JSON body", result,
                        "adapter.malformed_response")


def check_base_url_is_not_a_field():
    """The likeliest setup mistake: `base_url` copied from an OpenAI SDK
    snippet. The resolver rejects it as an invalid registry, and invoke
    surfaces that as adapter.profile_invalid rather than pretending the
    profile is merely unknown."""
    broken = local_profile(closed_port())
    broken["base_url"] = broken.pop("endpoint")
    settings = make_settings(PROFILE_NAME, [broken])
    profile, reason = resolve_profile(settings, PROFILE_NAME)
    if profile is not None:
        fail("a base_url profile resolved instead of failing")
        return
    if reason["code"] != "settings.invalid_value":
        fail("base_url gave %r, not settings.invalid_value" % reason["code"])
        return
    if "endpoint" not in reason["message"]:
        fail("the base_url message does not name the endpoint field: %r"
             % reason["message"])
        return
    _expect_unavailable("a base_url profile through invoke",
                        model_adapter.invoke(sample_request(PROFILE_NAME),
                                             settings),
                        "adapter.profile_invalid")


def check_unknown_transport_stays_typed():
    """A profile naming a transport with no registry entry (a dsh_stdio row
    written before the module exists) is typed, not a crash."""
    profile = local_profile(closed_port())
    profile["transport"] = "dsh_stdio"
    _expect_unavailable("an unregistered transport",
                        model_adapter.invoke(
                            sample_request(PROFILE_NAME),
                            make_settings(PROFILE_NAME, [profile])),
                        "adapter.transport_unknown")


def check_agent_panel_calls_the_local_profile_local():
    """The Agent panel's egress sentence is the one thing on that screen a
    learner cannot check for themselves, so it gets a guard.

    Before this plan the panel matched a list of transport names that did not
    include `openai_compatible`, so the shipped local-qwen profile would have
    been labelled hosted with "Item text and lesson prose leave this
    machine." Local is now derived from the endpoint host, so a profile
    pointing at a real remote server is still correctly called hosted."""
    from surfaces import visual_fixture

    data = shipped_settings()
    profiles = data.get("model_backend", {}).get("profiles") or []
    shipped = [p for p in profiles if p.get("name") == PROFILE_NAME]
    if not shipped:
        fail("no %r profile to classify" % PROFILE_NAME)
        return
    if not visual_fixture.profile_is_local(shipped[0]):
        fail("the shipped %r profile is classified as hosted" % PROFILE_NAME)
        return
    remote = dict(shipped[0])
    remote["endpoint"] = "https://api.example.com/v1/chat/completions"
    if visual_fixture.profile_is_local(remote):
        fail("an openai_compatible profile pointing off-machine is called "
             "local")
        return
    cli = {"name": "hosted", "transport": "hosted_cli", "command": ["claude"]}
    if visual_fixture.profile_is_local(cli):
        fail("a hosted_cli profile is called local")
        return
    rows, _note = visual_fixture.live_backends(ROOT)
    row = [r for r in rows if r["id"] == PROFILE_NAME]
    if not row:
        fail("live_backends dropped the shipped %r profile" % PROFILE_NAME)
        return
    if row[0]["where"] != "local" or "leave this machine" in row[0]["egress"]:
        fail("the panel row for %r reads %r / %r"
             % (PROFILE_NAME, row[0]["where"], row[0]["egress"]))
        return
    ok("the Agent panel calls the shipped local profile local, and a remote "
       "endpoint hosted")


def check_agent_tab_embeds_the_pinned_console():
    """The Agent tab frames `dsh` rather than rebuilding it, and the frame is
    honest about being a different program.

    Three things are guarded because all three are easy to lose in an edit
    and none of them is visible in a screenshot:

    1. The version rendered on the panel matches the version pinned in
       deps/dsh-pins.txt. A bump in code without a bump in the pin is the
       exact drift 17A-06-DECISIONS.md warns about, and a developer preview
       with SESSION_FORMAT_VERSION 0 will punish it.
    2. The frame carries an explicit lang and a title. The served document is
       <html lang="zh-CN"> and a framed document's language cannot be
       reassigned from outside, so the element must at least declare the
       language of the text itembank itself supplies.
    3. The panel does not claim the console's traffic stays on the machine.
       `dsh` reads its own configuration, so itembank cannot know."""
    import re
    from surfaces import visual_fixture

    pins = os.path.join(ROOT, "deps", "dsh-pins.txt")
    if not os.path.exists(pins):
        fail("deps/dsh-pins.txt is missing, so nothing pins the console")
        return
    pinned = open(pins, encoding="utf-8").read()
    if visual_fixture.DSH_VERSION not in pinned:
        fail("the panel renders %r but deps/dsh-pins.txt does not pin it"
             % visual_fixture.DSH_VERSION)
        return

    with open(os.path.join(ROOT, "fixtures", "visual_system_flow.json"),
              encoding="utf-8") as fh:
        data = json.load(fh)
    html = visual_fixture.page(data, "structured-studio",
                               stage_id="agent_harness", base=ROOT)
    frames = re.findall(r"<iframe\b[^>]*>", html)
    if len(frames) != 1:
        fail("the Agent tab renders %d frames, not one" % len(frames))
        return
    frame = frames[0]
    if visual_fixture.DSH_URL not in frame:
        fail("the frame does not point at the console: %r" % frame)
        return
    if 'lang="' not in frame:
        fail("the frame sets no explicit lang, so it inherits zh-CN: %r"
             % frame)
        return
    if 'title="' not in frame:
        fail("the frame has no title, so it is unnamed to a screen reader")
        return
    if visual_fixture.DSH_VERSION not in html:
        fail("the panel does not say which console version it framed")
        return
    console = html.split('class="vf-console"', 1)[1].split("</section>", 1)[0]
    if "Nothing leaves this machine" in console:
        fail("the console panel claims an egress it cannot know")
        return
    ok("the Agent tab frames %s %s, named and with an explicit lang"
       % (visual_fixture.DSH_PACKAGE, visual_fixture.DSH_VERSION))


def check_every_code_is_declared():
    """Each code this suite asserts is in ADAPTER_CODES, so a renamed code
    fails here rather than reaching a surface that switches on a string."""
    for code in ("adapter.unreachable", "adapter.timeout",
                 "adapter.malformed_response", "adapter.profile_invalid",
                 "adapter.profile_disabled", "adapter.transport_unknown"):
        if code not in model_adapter.ADAPTER_CODES:
            fail("%s is not declared in ADAPTER_CODES" % code)
    ok("every unavailable code this suite names is declared")


def main():
    check_shipped_profile_resolves()
    check_fresh_install_reaches_no_model()
    check_stubbed_endpoint_returns_a_result()
    check_refused_connection()
    check_timeout()
    check_non_json_body()
    check_base_url_is_not_a_field()
    check_unknown_transport_stays_typed()
    check_agent_panel_calls_the_local_profile_local()
    check_agent_tab_embeds_the_pinned_console()
    check_every_code_is_declared()
    if failures:
        print("\n%d failure(s)" % len(failures))
        return 1
    print("\nall local-harness checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
