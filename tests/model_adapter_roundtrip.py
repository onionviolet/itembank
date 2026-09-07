#!/usr/bin/env python3
"""The model-adapter boundary contract (Phase 8, plan 08-02).

Hosted CLI and local OpenAI-compatible transports normalize through one
invoke(request, settings) boundary (MODEL-01/MODEL-02); every provider failure
-- disabled profile, missing executable, nonzero exit, timeout, HTTP/URL
error, malformed JSON, oversized output, provider refusal -- converts to one
typed unavailable result with a named adapter.* code and never raises
(D-04/MODEL-03); a third backend is a TRANSPORT_REGISTRY entry, not a code
fork (D-27); credentials come from the environment by name, never the
settings file value, and never enter requests, results, or evidence
(D-03/D-15); and the request/result contract structurally carries no score,
tier decision, or accepted-mark field (MODEL-05).

Standard library only, runnable as `python tests/model_adapter_roundtrip.py`.
"""
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import model_adapter                       # noqa: E402
import schema_validate                     # noqa: E402
from surfaces import settings as settings_surface  # noqa: E402

SCHEMA_PATH = os.path.join(ROOT, "schemas", "model_adapter.schema.json")
SETTINGS_ON_DISK = os.path.join(ROOT, "itembank.json")
SETTINGS_SCHEMA_PATH = os.path.join(ROOT, "schemas", "settings.schema.json")

INTERACTION_ID = "int-00000001"


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def flatten(obj):
    """Yield (key, value) for every key at every depth -- used to assert a
    forbidden key or a secret value is absent anywhere in a structure, not
    just at the top level."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield (k, v)
            yield from flatten(v)
    elif isinstance(obj, list):
        for el in obj:
            yield from flatten(el)


def fake_cli_script(kind="ok", secret_env=None):
    """A fake hosted-CLI executable: reads the request from stdin and writes
    a fixed hint_plan-shaped JSON to stdout (or the requested failure mode).
    """
    lines = ["import json, sys, os",
             "req = json.load(sys.stdin)",
             "if len(sys.argv) > 1:",
             "    json.dump(req, open(sys.argv[1], 'w'))"]
    if kind == "ok":
        lines += ["out = {'kind': 'hint_plan', 'interaction_id': req['interaction_id'],",
                  "       'focus_span': 'the wrong answer', 'fact_ids': ['tier2.trap'],",
                  "       'move': 'anchor_error'}",
                  "json.dump(out, sys.stdout)"]
    elif kind == "malformed":
        lines += ["sys.stdout.write('not json')"]
    elif kind == "oversize":
        lines += ["sys.stdout.write('x' * 10000)"]
    elif kind == "refuse":
        lines += ["sys.exit(1)"]
    elif kind == "timeout":
        lines += ["import time", "time.sleep(30)"]
    elif kind == "secret":
        assert secret_env
        lines += ["out = {'kind': 'hint_plan', 'interaction_id': req['interaction_id'],",
                  "       'focus_span': 'the wrong answer', 'fact_ids': ['tier2.trap'],",
                  "       'move': 'anchor_error',",
                  "       'env_secret_present': bool(os.environ.get(%r))}" % secret_env,
                  "json.dump(out, sys.stdout)"]
    return "\n".join(lines) + "\n"


def hosted_profile(tmp, name="hosted", script_kind="ok", capture=None,
                   timeout=30, max_bytes=65536, secret_env=None,
                   model="fake-hosted"):
    """A model_backend profile record whose hosted_cli command runs a fake
    executable script under tmp.

    `tmp` must be an absolute directory. It was unchecked until 2026-08-30,
    and one caller passed `""` for a profile that is never invoked, so the
    script landed in the process cwd -- the repository root when the suite
    runs from there -- and `fake_hosted_unused.py` was committed as source in
    `46f0f50`. A test may write whatever it likes under a temp dir; it may
    not write into the tree it is checking.
    """
    if not os.path.isabs(tmp):
        raise ValueError(
            "hosted_profile needs an absolute temp directory, not %r; a "
            "relative path writes the fake script into the process cwd" % tmp)
    script = os.path.join(tmp, "fake_hosted_%s.py" % name)
    open(script, "w", encoding="utf-8").write(fake_cli_script(script_kind, secret_env))
    command = [sys.executable, script]
    if capture:
        command.append(capture)
    profile = {"name": name, "transport": "hosted_cli", "command": command,
               "model": model, "timeout_seconds": timeout,
               "max_output_bytes": max_bytes, "context_window": 4096}
    if secret_env:
        profile["secret_env"] = secret_env
    return profile


def make_settings(active, profiles):
    return {"model_backend": {"active": active, "profiles": profiles}}


def sample_request(profile="hosted", operation="hint"):
    payload = {
        "item_context": {"item_id": "x1", "type": "mc"},
        "learner_response": "the wrong answer",
        "permitted_tier": 2,
        "fact_manifest": {"tier2.trap": "The trap text."},
    }
    if operation == "rubric_review":
        payload["rubric_points"] = [
            {"point": "Mentions the mechanism.", "pass": True,
             "rationale": "The response names the mechanism."},
        ]
    return model_adapter.request_from_operation(operation, INTERACTION_ID,
                                                profile, **payload)


# ---- Task 1: the tracer -- one hosted-CLI call through invoke ---------------

def test_hosted_cli_roundtrip():
    """A fake hosted CLI executable, invoked through the public boundary,
    returns the normalized typed result: status ok, the same interaction_id,
    a candidate object, provider.backend_class "hosted", the profile name,
    an integer elapsed_ms, and no error."""
    tmp = tempfile.mkdtemp()
    try:
        profile = hosted_profile(tmp)
        settings = make_settings("hosted", [profile])
        request = sample_request("hosted")
        result = model_adapter.invoke(request, settings)
        if result["status"] != "ok":
            fail("hosted roundtrip status is %r: %r" % (result["status"], result))
        if result["interaction_id"] != INTERACTION_ID:
            fail("interaction_id did not round-trip: %r" % result["interaction_id"])
        if not isinstance(result.get("candidate"), dict) or \
                result["candidate"].get("kind") != "hint_plan":
            fail("candidate is not the parsed provider plan: %r"
                 % result.get("candidate"))
        if result["provider"]["backend_class"] != "hosted":
            fail("backend_class is %r, not hosted" % result["provider"]["backend_class"])
        if result["provider"]["profile"] != "hosted":
            fail("provider.profile is %r, not 'hosted'" % result["provider"]["profile"])
        if not isinstance(result["elapsed_ms"], int) or result["elapsed_ms"] < 0:
            fail("elapsed_ms is not a non-negative int: %r" % result["elapsed_ms"])
        if result["error"] is not None:
            fail("an ok result carries an error: %r" % result["error"])
        schema = json.load(open(SCHEMA_PATH, encoding="utf-8"))
        errs = schema_validate.validate(result, schema)
        if errs:
            fail("ok result does not validate against the adapter schema: %s"
                 % errs[0])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_request_envelope_and_unknown_field():
    """A bounded request validates against the published envelope; a request
    carrying an extra field returns typed unavailable adapter.request_invalid
    -- never raised."""
    schema = json.load(open(SCHEMA_PATH, encoding="utf-8"))
    request = sample_request()
    errs = schema_validate.validate(request, schema)
    if errs:
        fail("a bounded request does not validate: %s" % errs[0])
    bad = dict(request)
    bad["smuggled_field"] = "nope"
    tmp = tempfile.mkdtemp()
    try:
        result = model_adapter.invoke(
            bad, make_settings("", [hosted_profile(tmp, name="unused")]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if result["status"] != "unavailable" or \
            result["error"]["code"] != "adapter.request_invalid":
        fail("a request with an unknown field is not adapter.request_invalid: %r"
             % result)
    if result["interaction_id"] != INTERACTION_ID:
        fail("request_invalid result lost the interaction_id: %r" % result)


def test_missing_executable_and_nonzero_exit():
    """A missing executable returns unavailable adapter.executable_missing
    and a nonzero exit returns adapter.provider_refused; neither raises and
    neither touches evidence."""
    tmp = tempfile.mkdtemp()
    try:
        missing = {"name": "gone", "transport": "hosted_cli",
                   "command": ["/nonexistent/itembank-hosted-bin"],
                   "model": "x", "timeout_seconds": 5,
                   "max_output_bytes": 65536, "context_window": 4096}
        r1 = model_adapter.invoke(
            sample_request("gone"), make_settings("gone", [missing]))
        if r1["status"] != "unavailable" or \
                r1["error"]["code"] != "adapter.executable_missing":
            fail("missing executable is not adapter.executable_missing: %r" % r1)

        refuse = hosted_profile(tmp, name="refuse", script_kind="refuse")
        r2 = model_adapter.invoke(
            sample_request("refuse"), make_settings("refuse", [refuse]))
        if r2["status"] != "unavailable" or \
                r2["error"]["code"] != "adapter.provider_refused":
            fail("nonzero exit is not adapter.provider_refused: %r" % r2)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_adapter_never_touches_evidence():
    """The adapter boundary is transport only: it neither imports evidence
    nor writes it (plan 08-03 owns evidence). Structural scan, the same
    one-writer discipline scoring_roundtrip/evidence_roundtrip enforce."""
    source = open(os.path.join(ROOT, "model_adapter.py"), encoding="utf-8").read()
    if "import evidence" in source or "append_event" in source:
        fail("model_adapter.py references the evidence store")


# ---- Task 2: hosted/local parity and the full failure matrix ----------------

class _FakeServer:
    """A threaded loopback OpenAI-compatible endpoint whose behaviour is set
    at construction: ok returns a fixed hint_plan body; refuse returns HTTP
    503; timeout sleeps past the profile timeout; malformed and oversize
    return the named bodies. Every request body is captured so a test can
    assert what actually left the machine (secrets never ride along)."""

    def __init__(self, mode="ok"):
        self.mode = mode
        self.received = []
        self.headers = []
        ctx = {"mode": mode, "received": self.received, "headers": self.headers}

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                length = int(self.headers.get("Content-Length") or 0)
                ctx["received"].append(self.rfile.read(length).decode("utf-8"))
                ctx["headers"].append(dict(self.headers))
                mode = ctx["mode"]
                if mode == "refuse":
                    self.send_response(503)
                    data = b"refused"
                elif mode == "timeout":
                    time.sleep(2)
                    self.send_response(200)
                    data = b"{}"
                elif mode == "malformed":
                    self.send_response(200)
                    data = b"not json"
                elif mode == "oversize":
                    self.send_response(200)
                    data = b"x" * 10000
                else:
                    self.send_response(200)
                    payload = {"kind": "hint_plan",
                               "interaction_id": "int-00000001",
                               "focus_span": "the wrong answer",
                               "fact_ids": ["tier2.trap"],
                               "move": "anchor_error"}
                    data = json.dumps(payload).encode("utf-8")
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                try:
                    self.wfile.write(data)
                except BrokenPipeError:
                    # The client (a timed-out transport) is already gone; the
                    # timeout row's server thread must not spew a traceback.
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


def local_profile(server_or_port, name="local", timeout=5, max_bytes=65536,
                  model="qwen", secret_env=None):
    endpoint = "http://127.0.0.1:%d/v1/chat/completions" % (
        server_or_port.port if hasattr(server_or_port, "port")
        else server_or_port)
    profile = {"name": name, "transport": "openai_compatible",
               "endpoint": endpoint, "model": model,
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


def test_openai_parity_and_config_switch():
    """A fake loopback OpenAI-compatible server returns the same normalized
    result shape as the hosted CLI for the same request, and switching the
    active profile is a settings-only change (MODEL-02): the identical
    invoke(request, settings) call produces the parity shape."""
    tmp = tempfile.mkdtemp()
    server = None
    try:
        server = _FakeServer(mode="ok")
        # The same request, the same active profile name "local", and two
        # settings documents that differ ONLY in the profile record's
        # transport -- the identical invoke call is the config-only switch
        # (MODEL-02).
        hosted = hosted_profile(tmp, name="local")
        local = local_profile(server, name="local")
        request = sample_request("local")
        rh = model_adapter.invoke(request, make_settings("local", [hosted]))
        rl = model_adapter.invoke(request, make_settings("local", [local]))
        for r in (rh, rl):
            if r["status"] != "ok":
                fail("parity transport status is %r: %r" % (r["status"], r))
        if rh["candidate"] != rl["candidate"]:
            fail("candidate shapes differ between transports: %r vs %r"
                 % (rh["candidate"], rl["candidate"]))
        if rh["interaction_id"] != rl["interaction_id"] or \
                rh["error"] != rl["error"] or rh["status"] != rl["status"]:
            fail("parity fields differ: %r vs %r" % (rh, rl))
        if rh["provider"]["backend_class"] != "hosted" or \
                rl["provider"]["backend_class"] != "local":
            fail("backend classes wrong: %r vs %r"
                 % (rh["provider"], rl["provider"]))
        if rh["provider"]["profile"] != "local" or \
                rl["provider"]["profile"] != "local":
            fail("provider profile differs: %r vs %r"
                 % (rh["provider"], rl["provider"]))
        for r in (rh, rl):
            if not isinstance(r["elapsed_ms"], int) or r["elapsed_ms"] < 0:
                fail("elapsed_ms is not a non-negative int: %r" % r["elapsed_ms"])
    finally:
        if server:
            server.close()
        shutil.rmtree(tmp, ignore_errors=True)


def test_stable_replay():
    """Identical requests replay with the same normalized shape: the request
    is serialized with stable key ordering, and the normalized result is
    deterministic modulo elapsed_ms."""
    tmp = tempfile.mkdtemp()
    try:
        profile = hosted_profile(tmp, name="hosted")
        settings = make_settings("hosted", [profile])
        request = sample_request("hosted")
        r1 = model_adapter.invoke(request, settings)
        r2 = model_adapter.invoke(request, settings)
        for key in ("status", "interaction_id", "candidate", "provider", "error"):
            if r1[key] != r2[key]:
                fail("replay changed normalized %r: %r vs %r"
                     % (key, r1[key], r2[key]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_failure_matrix_typed_unavailable():
    """Every failure-matrix row returns status unavailable with a named
    adapter.* code and no exception escapes (MODEL-03); authored hints stay
    usable afterwards."""
    tmp = tempfile.mkdtemp()
    servers = []
    try:
        cases = []
        unused = hosted_profile(tmp, name="unused")
        cases.append(("disabled-active", make_settings("", [unused]),
                      "adapter.profile_disabled"))
        cases.append(("disabled-profiles", make_settings("some", []),
                      "adapter.profile_disabled"))
        missing = {"name": "gone", "transport": "hosted_cli",
                   "command": ["/nonexistent/itembank-hosted-bin"],
                   "model": "x", "timeout_seconds": 5,
                   "max_output_bytes": 65536, "context_window": 4096}
        cases.append(("missing-exe", make_settings("gone", [missing]),
                      "adapter.executable_missing"))
        refuse = hosted_profile(tmp, name="refuse", script_kind="refuse")
        cases.append(("nonzero-exit", make_settings("refuse", [refuse]),
                      "adapter.provider_refused"))
        timeout_cli = hosted_profile(tmp, name="timeout", script_kind="timeout",
                                     timeout=1)
        cases.append(("timeout", make_settings("timeout", [timeout_cli]),
                      "adapter.timeout"))
        malformed = hosted_profile(tmp, name="malformed",
                                   script_kind="malformed")
        cases.append(("malformed-json", make_settings("malformed", [malformed]),
                      "adapter.malformed_response"))
        oversize = hosted_profile(tmp, name="oversize", script_kind="oversize",
                                  max_bytes=2048)
        cases.append(("oversized-output",
                      make_settings("oversize", [oversize]),
                      "adapter.output_cap_exceeded"))

        unreachable = local_profile(closed_port(), name="unreachable")
        cases.append(("unreachable", make_settings("unreachable", [unreachable]),
                      "adapter.unreachable"))

        # Every loopback server stays alive until the matrix loop below has
        # run, so each row exercises its own live endpoint.
        http_fail_server = _FakeServer(mode="refuse")
        servers.append(http_fail_server)
        http_fail = local_profile(http_fail_server, name="http_fail")
        cases.append(("http-error", make_settings("http_fail", [http_fail]),
                      "adapter.http_error"))
        http_timeout_server = _FakeServer(mode="timeout")
        servers.append(http_timeout_server)
        http_timeout = local_profile(http_timeout_server, name="http_timeout",
                                     timeout=1)
        cases.append(("http-timeout", make_settings("http_timeout", [http_timeout]),
                      "adapter.timeout"))
        http_malformed_server = _FakeServer(mode="malformed")
        servers.append(http_malformed_server)
        http_malformed = local_profile(http_malformed_server,
                                       name="http_malformed")
        cases.append(("http-malformed",
                      make_settings("http_malformed", [http_malformed]),
                      "adapter.malformed_response"))
        http_oversize_server = _FakeServer(mode="oversize")
        servers.append(http_oversize_server)
        http_oversize = local_profile(http_oversize_server, name="http_oversize",
                                      max_bytes=2048)
        cases.append(("http-oversize",
                      make_settings("http_oversize", [http_oversize]),
                      "adapter.output_cap_exceeded"))

        # profile "" on the request means "use the active profile", so each
        # matrix row exercises exactly its own configured failure.
        for label, settings, code in cases:
            try:
                result = model_adapter.invoke(sample_request(""), settings)
            except Exception as exc:
                fail("%s raised out of invoke: %r" % (label, exc))
            if result["status"] != "unavailable":
                fail("%s status is %r, not unavailable: %r"
                     % (label, result["status"], result))
            if result["error"]["code"] != code:
                fail("%s error code is %r, expected %r"
                     % (label, result["error"]["code"], code))
            if result["candidate"] is not None:
                fail("%s carries a candidate: %r" % (label, result["candidate"]))
            if result["elapsed_ms"] is not None:
                fail("%s carries elapsed_ms on an unavailable result: %r"
                     % (label, result["elapsed_ms"]))
            schema = json.load(open(SCHEMA_PATH, encoding="utf-8"))
            errs = schema_validate.validate(result, schema)
            if errs:
                fail("%s result does not validate: %s" % (label, errs[0]))
    finally:
        for s in servers:
            s.close()
        shutil.rmtree(tmp, ignore_errors=True)


def test_authored_fallback_after_unavailable():
    """MODEL-03's offline floor: after an adapter failure, the authored hint
    ladder still resolves -- the model layer going quiet never blocks study."""
    import runtime
    import itembank
    qs = itembank.load(os.path.join(ROOT, "fixtures", "sample_bank.md"))
    hint = runtime.authored_hint(qs[0], 2, None)
    if not hint["available"] or not hint["content"]:
        fail("authored tier-2 hint unavailable: %r" % hint)


# ---- Task 3: the named profile registry, secret env references, and --------
# ---- the third-backend stub proof ------------------------------------------

def test_profile_registry_validation():
    """Settings accept model_backend as {active, profiles} with unique profile
    names; a duplicate name, an unknown active profile, or a profile missing
    its transport-required field is a typed reason -- settings.invalid_value
    for a bad registry, adapter.profile_unknown for a missing active name --
    never a silent fallback (RESEARCH Pitfall 3, T-08-13)."""
    tmp = tempfile.mkdtemp()
    try:
        a = hosted_profile(tmp, name="a")
        b = hosted_profile(tmp, name="b")
        settings = make_settings("a", [a, b])
        profile, reason = settings_surface.resolve_profile(settings)
        if profile is None or reason is not None:
            fail("a valid unique-name registry did not resolve: %r %r"
                 % (profile, reason))
        if profile.get("name") != "a":
            fail("the active profile resolved to %r, not 'a'"
                 % profile.get("name"))

        dup = make_settings("a", [a, dict(a, name="b"), b])
        profile, reason = settings_surface.resolve_profile(dup)
        if profile is not None or reason is None or \
                reason["code"] != "settings.invalid_value":
            fail("a duplicate profile name is not settings.invalid_value: %r %r"
                 % (profile, reason))

        unknown = make_settings("ghost", [a])
        profile, reason = settings_surface.resolve_profile(unknown)
        if profile is not None or reason is None or \
                reason["code"] != "adapter.profile_unknown":
            fail("an unknown active profile is not adapter.profile_unknown: %r %r"
                 % (profile, reason))

        missing_cmd = dict(a)
        del missing_cmd["command"]
        profile, reason = settings_surface.resolve_profile(
            make_settings("a", [missing_cmd]))
        if profile is not None or reason is None or \
                reason["code"] != "settings.invalid_value":
            fail("a hosted_cli profile missing command is not "
                 "settings.invalid_value: %r %r" % (profile, reason))

        missing_endpoint = dict(local_profile(closed_port(), name="loc"))
        del missing_endpoint["endpoint"]
        profile, reason = settings_surface.resolve_profile(
            make_settings("loc", [missing_endpoint]))
        if profile is not None or reason is None or \
                reason["code"] != "settings.invalid_value":
            fail("an openai_compatible profile missing endpoint is not "
                 "settings.invalid_value: %r %r" % (profile, reason))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_load_settings_rejects_bad_registry():
    """A schema-invalid model_backend registry (a profile missing a required
    field) is rejected by load_settings with a named settings.* code -- never
    a silent fallback to disabled."""
    tmp = tempfile.mkdtemp()
    try:
        base = os.path.join(tmp, "base")
        os.makedirs(base)
        data = {"model_backend": {"active": "a", "profiles": [
            {"name": "a", "transport": "hosted_cli", "command": ["x"]},
        ]}}
        json.dump(data, open(os.path.join(base, "itembank.json"), "w",
                             encoding="utf-8"))
        try:
            settings_surface.load_settings(base)
        except SystemExit as exc:
            msg = str(exc)
            if "settings." not in msg:
                fail("a bad registry was rejected with a non-settings code: %r"
                     % msg)
        else:
            fail("a profile missing required fields loaded silently")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_transport_descriptor_registration():
    """The two shipped transport declarations use EXT-01's validated shape.
    Their handler map stays mutable so the separate third-backend proof keeps
    its mutation-based isolation and no transport is invoked at import time.
    """
    names = ("hosted_cli", "openai_compatible")
    if tuple(model_adapter.TRANSPORT_REGISTRY) != names:
        fail("transport declaration order changed: %r"
             % tuple(model_adapter.TRANSPORT_REGISTRY))
    if model_adapter.TRANSPORT_REGISTRY["hosted_cli"] is not \
            model_adapter._transport_hosted_cli:
        fail("hosted CLI handler identity changed")
    if model_adapter.TRANSPORT_REGISTRY["openai_compatible"] is not \
            model_adapter._transport_openai_compatible:
        fail("OpenAI-compatible handler identity changed")
    if tuple(model_adapter.TRANSPORT_VERSIONS.values()) != ("1.0.0", "1.0.0"):
        fail("transport versions changed: %r" % model_adapter.TRANSPORT_VERSIONS)
    for name in names:
        description = model_adapter.TRANSPORT_DESCRIPTIONS.get(name)
        if description is None or description.get("name") != name or \
                not description.get("capability") or not description.get("fallback") or \
                description.get("handler") is not None:
            fail("transport description is incomplete: %r" % description)


def test_stub_third_backend_registration():
    """A stub third backend registers through TRANSPORT_REGISTRY and invoke
    routes to it with zero edits to tier-gate, evidence, or prompt-assembly
    code (D-27): one registry entry plus one config entry, and the same
    invoke(request, settings) call serves it. The result envelope keeps the
    no-score contract (MODEL-05)."""
    called = {}

    def stub_transport(request, request_json, profile, settings):
        called["profile"] = profile.get("name")
        return model_adapter._ok_result(
            request, "hosted", profile,
            {"kind": "hint_plan", "interaction_id": request["interaction_id"],
             "focus_span": "stubbed", "fact_ids": [], "move": "anchor_error"},
            1)

    model_adapter.TRANSPORT_REGISTRY["stub_transport"] = stub_transport
    try:
        profile = {"name": "stub", "transport": "stub_transport",
                   "model": "stub-model", "timeout_seconds": 5,
                   "max_output_bytes": 65536, "context_window": 4096}
        result = model_adapter.invoke(
            sample_request("stub"), make_settings("stub", [profile]))
        if result["status"] != "ok":
            fail("the stub backend did not route through invoke: %r" % result)
        if result["candidate"].get("kind") != "hint_plan":
            fail("the stub candidate did not round-trip: %r" % result)
        if called.get("profile") != "stub":
            fail("the stub transport did not receive the active profile: %r"
                 % called)
        for key in ("score", "tier", "accepted_mark"):
            if key in result:
                fail("the result envelope carries a %r field (MODEL-05)" % key)
    finally:
        del model_adapter.TRANSPORT_REGISTRY["stub_transport"]


def test_secrets_from_env_never_inline():
    """Credentials are read from the environment by name (secret_env), never
    stored inline in itembank.json and never present in any request, result,
    log, or evidence field (D-03/D-15). Phase 19C activates the loopback-only
    `local-qwen` profile. A shipped profile carrying a `secret_env` would be a
    different matter and is rejected below."""
    shipped = settings_surface.load_settings(ROOT)
    mb = shipped.get("model_backend")
    if not isinstance(mb, dict) or mb.get("active") != "local-qwen":
        fail("the shipped model_backend does not activate local-qwen: %r" % mb)
    else:
        profile, reason = model_adapter.resolve_profile(shipped)
        if reason is not None or profile is None:
            fail("the shipped config did not resolve local-qwen: %r / %r"
                 % (profile, reason))
        elif not profile.get("endpoint", "").startswith(
                "http://127.0.0.1:"):
            fail("the active shipped profile is not loopback-only: %r"
                 % profile.get("endpoint"))
    for record in (mb or {}).get("profiles") or []:
        if record.get("secret_env"):
            fail("a shipped profile %r names a credential variable"
                 % record.get("name"))

    raw_settings = open(SETTINGS_ON_DISK, encoding="utf-8").read()
    for needle in ("sk-", "hunter2", "Bearer "):
        if needle in raw_settings:
            fail("a credential pattern %r is inline in itembank.json" % needle)

    env_name = "ITEMBANK_TEST_SECRET_%d" % os.getpid()
    tmp = tempfile.mkdtemp()
    server = None
    try:
        server = _FakeServer(mode="ok")
        profile = local_profile(server, name="local", secret_env=env_name)
        settings = make_settings("local", [profile])
        if "hunter2" in json.dumps(settings):
            fail("the secret value is present in the settings document")
        os.environ[env_name] = "hunter2"
        try:
            result = model_adapter.invoke(sample_request("local"), settings)
        finally:
            del os.environ[env_name]
        if result["status"] != "ok":
            fail("a secret-bearing profile did not route: %r" % result)
        if not any("hunter2" in (h.get("Authorization") or "")
                   for h in server.headers):
            fail("the env secret did not reach the Authorization header")
        if "hunter2" in server.received[0]:
            fail("the secret value reached the request body")
        for key, value in flatten(result):
            if value == "hunter2":
                fail("the secret value reached result field %r" % key)
    finally:
        if server:
            server.close()
        shutil.rmtree(tmp, ignore_errors=True)


def test_suggestion_reveal_enum_and_default():
    """suggestion_reveal validates to the three enum values, defaults to
    after-self-mark, and reads back through load_settings (D-22)."""
    schema = json.load(open(SETTINGS_SCHEMA_PATH, encoding="utf-8"))
    sub = schema["properties"]["suggestion_reveal"]
    if sub["enum"] != ["after-self-mark", "before-self-mark", "after-mark"]:
        fail("suggestion_reveal enum is not the three shipped values: %r"
             % sub["enum"])
    if sub["default"] != "after-self-mark":
        fail("suggestion_reveal default is not after-self-mark: %r"
             % sub["default"])
    if sub.get("x-itembank-phase") != 8:
        fail("suggestion_reveal is not x-itembank-phase 8")
    for value in ("after-self-mark", "before-self-mark", "after-mark"):
        if schema_validate.validate(value, sub):
            fail("valid suggestion_reveal %r failed the schema" % value)
    if not schema_validate.validate("mid-mark", sub):
        fail("invalid suggestion_reveal 'mid-mark' passed the schema")

    loaded = settings_surface.load_settings(ROOT)
    if loaded.get("suggestion_reveal") != "after-self-mark":
        fail("suggestion_reveal did not read back as after-self-mark: %r"
             % loaded.get("suggestion_reveal"))

    tmp = tempfile.mkdtemp()
    try:
        base = os.path.join(tmp, "base")
        os.makedirs(base)
        json.dump({"theme": "system"},
                  open(os.path.join(base, "itembank.json"), "w",
                       encoding="utf-8"))
        loaded2 = settings_surface.load_settings(base)
        if loaded2.get("suggestion_reveal") != "after-self-mark":
            fail("a missing suggestion_reveal did not read as the default")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    test_hosted_cli_roundtrip()
    test_request_envelope_and_unknown_field()
    test_missing_executable_and_nonzero_exit()
    test_adapter_never_touches_evidence()
    test_openai_parity_and_config_switch()
    test_stable_replay()
    test_failure_matrix_typed_unavailable()
    test_authored_fallback_after_unavailable()
    test_profile_registry_validation()
    test_load_settings_rejects_bad_registry()
    test_transport_descriptor_registration()
    test_stub_third_backend_registration()
    test_secrets_from_env_never_inline()
    test_suggestion_reveal_enum_and_default()
    print("model adapter: ok (hosted CLI roundtrip, request envelope, "
          "executable-missing/refusal typed unavailable, hosted/local parity "
          "under a config-only switch, full failure matrix typed unavailable, "
          "authored fallback intact, profile registry validation, stub third "
          "backend, secret env references, suggestion_reveal contract)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
