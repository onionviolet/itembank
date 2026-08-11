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
    executable script under tmp."""
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
    result = model_adapter.invoke(
        bad, make_settings("", [hosted_profile("", name="unused")]))
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


def main():
    test_hosted_cli_roundtrip()
    test_request_envelope_and_unknown_field()
    test_missing_executable_and_nonzero_exit()
    test_adapter_never_touches_evidence()
    print("model adapter: ok (hosted CLI roundtrip, request envelope, "
          "executable-missing/refusal typed unavailable)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
