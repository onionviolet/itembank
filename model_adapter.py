#!/usr/bin/env python3
"""The model-adapter boundary (Phase 8, plan 08-02).

One typed invoke(request, settings) boundary normalizes any number of
provider transports behind TRANSPORT_REGISTRY, so switching providers is a
settings change, never a caller change (D-01, D-02, MODEL-02). Every failure
-- disabled profile, missing executable, nonzero exit, timeout, HTTP/URL
error, malformed JSON, oversized output, provider refusal, an invalid request
-- converts to one typed unavailable result with a named adapter.* code
before any surface or evidence call (D-04, MODEL-03). Nothing here raises.

Transports are stdlib subprocess and urllib only -- no provider SDK, no
runtime dependency (AI-SPEC section 2). Credentials are resolved from
os.environ by name (profile.secret_env), never from the settings file value,
and never enter requests, results, logs, or evidence (D-03, D-15).
"""
import json
import os
import subprocess
import time
import urllib.error
import urllib.request

import resources
import schema_validate
from surfaces.settings import resolve_profile as _resolve_profile


SCHEMA_RESOURCE = "schemas/model_adapter.schema.json"

# The typed unavailable codes this boundary can produce. Built from a
# set-then-sorted tuple so sortedness is structural (the SETTINGS_CODES /
# LINT_CODES construction precedent).
ADAPTER_CODES = tuple(sorted({
    "adapter.executable_missing", "adapter.http_error", "adapter.internal_error",
    "adapter.malformed_response", "adapter.output_cap_exceeded",
    "adapter.profile_disabled", "adapter.profile_invalid",
    "adapter.profile_unknown", "adapter.provider_refused",
    "adapter.request_invalid", "adapter.subprocess_error", "adapter.timeout",
    "adapter.transport_unknown", "adapter.unreachable",
}))


def _load_schema():
    return json.loads(resources.read_text(SCHEMA_RESOURCE))


_SCHEMA = _load_schema()

# The fixed payload keys request_from_operation may carry. A bounded builder
# is how the contract stays closed: a caller cannot smuggle an unplanned
# field into a request (MODEL-05). author_request is the Phase 11 additive
# bounded-authoring payload (plan 11-05, operation author).
# recommendation_request is the Phase 15A additive bounded course-scope
# payload (plan 15A-01, operation treatment_recommend); it is appended last so
# the six prior keys keep their positions and every request built before this
# phase serializes to the byte-identical JSON it did before.
_PAYLOAD_KEYS = ("item_context", "learner_response", "permitted_tier",
                 "fact_manifest", "rubric_points", "author_request",
                 "recommendation_request")


def unavailable_result(code, message, interaction_id):
    """The typed unavailable envelope every failure converts into.
    `interaction_id` may be None only when the request itself was unreadable.
    """
    return {
        "schema_version": 1,
        "interaction_id": interaction_id,
        "status": "unavailable",
        "candidate": None,
        "provider": None,
        "elapsed_ms": None,
        "error": {"code": code, "message": message},
    }


def request_from_operation(operation, interaction_id, profile, **payload):
    """Build a bounded adapter request: exactly the fixed envelope fields and
    the fixed payload keys, nothing else. A payload key that was not passed
    is left absent; invoke's runtime check requires payload.rubric_points for
    operation rubric_review (adapter.request_invalid)."""
    return {
        "schema_version": 1,
        "operation": operation,
        "interaction_id": interaction_id,
        "profile": profile,
        "version": "1",
        "payload": {k: payload[k] for k in _PAYLOAD_KEYS if k in payload},
    }


def resolve_profile(settings_data, name=None):
    """The active-profile resolver, owned by surfaces/settings.py so config
    and adapter share one read; re-exported here as part of this module's
    public boundary. Returns (profile_or_None, error_or_None); exactly one is
    non-None. An empty active profile or empty profiles array is
    adapter.profile_disabled; a bad registry is settings.invalid_value; an
    active name that matches no profile is adapter.profile_unknown."""
    return _resolve_profile(settings_data, name)


def _ok_result(request, backend_class, profile, candidate, elapsed_ms):
    return {
        "schema_version": 1,
        "interaction_id": request["interaction_id"],
        "status": "ok",
        "candidate": candidate,
        "provider": {"backend_class": backend_class,
                     "profile": profile.get("name")},
        "elapsed_ms": elapsed_ms,
        "error": None,
    }


def _secret_value(profile):
    """The credential for this profile, resolved from os.environ by the
    profile.secret_env NAME and from nowhere else (D-03/D-15). None when
    secret_env is unset or the variable is not in the environment -- never an
    error, never a fallback to the settings file value."""
    name = profile.get("secret_env")
    if not name:
        return None
    return os.environ.get(name)


def _transport_hosted_cli(request, request_json, profile, settings):
    """The hosted CLI transport: subprocess.run over a configured argument
    vector, shell=False, with per-profile timeout and output cap (the
    launcher.py house pattern). A nonzero exit is a refusal; output beyond
    the cap and non-JSON output are typed unavailable."""
    interaction_id = request["interaction_id"]
    command = [str(c) for c in (profile.get("command") or [])]
    timeout = profile.get("timeout_seconds") or 60
    max_bytes = profile.get("max_output_bytes") or 65536
    start = time.monotonic()
    try:
        completed = subprocess.run(
            command, input=request_json, text=True, capture_output=True,
            timeout=timeout, shell=False)
    except subprocess.TimeoutExpired:
        return unavailable_result("adapter.timeout",
                                  "hosted CLI timed out after %ss" % timeout,
                                  interaction_id)
    except OSError:
        return unavailable_result("adapter.executable_missing",
                                  "hosted CLI executable could not be started: %r"
                                  % command[0] if command else "no command",
                                  interaction_id)
    except subprocess.SubprocessError:
        return unavailable_result("adapter.subprocess_error",
                                  "hosted CLI subprocess failed",
                                  interaction_id)
    elapsed_ms = int((time.monotonic() - start) * 1000)
    if completed.returncode != 0:
        return unavailable_result("adapter.provider_refused",
                                  "hosted CLI exited with status %d"
                                  % completed.returncode,
                                  interaction_id)
    if len(completed.stdout) > max_bytes:
        return unavailable_result("adapter.output_cap_exceeded",
                                  "hosted CLI output exceeded %d bytes" % max_bytes,
                                  interaction_id)
    try:
        candidate = json.loads(completed.stdout)
    except ValueError:
        return unavailable_result("adapter.malformed_response",
                                  "hosted CLI returned non-JSON output",
                                  interaction_id)
    return _ok_result(request, "hosted", profile, candidate, elapsed_ms)


# hosted_cli first (D-18: the hosted CLI is the design target and the default
# when a backend is enabled), then the local OpenAI-compatible HTTP transport
# behind the same interface (MODEL-01). Adding a third backend is a registry
# entry plus a config entry, with zero edits to tier-gate, evidence, or
# prompt-assembly code (D-27).
def _transport_openai_compatible(request, request_json, profile, settings):
    """The local OpenAI-compatible HTTP transport: urllib POST to the
    profile's endpoint with a per-profile timeout and a read capped at
    max_output_bytes plus one to detect oversize (update.py's "nothing here
    raises" shape). HTTPError precedes URLError because the former subclasses
    the latter; a timeout inside URLError is its own named code."""
    interaction_id = request["interaction_id"]
    endpoint = profile.get("endpoint")
    timeout = profile.get("timeout_seconds") or 60
    max_bytes = profile.get("max_output_bytes") or 65536
    headers = {"Content-Type": "application/json"}
    token = _secret_value(profile)
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(endpoint, data=request_json.encode("utf-8"),
                                 method="POST", headers=headers)
    start = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read(max_bytes + 1)
    except urllib.error.HTTPError as exc:
        return unavailable_result("adapter.http_error",
                                  "endpoint returned HTTP %d" % exc.code,
                                  interaction_id)
    except urllib.error.URLError as exc:
        if isinstance(exc.reason, TimeoutError):
            return unavailable_result("adapter.timeout",
                                      "endpoint timed out after %ss" % timeout,
                                      interaction_id)
        return unavailable_result("adapter.unreachable",
                                  "endpoint unreachable: %s" % endpoint,
                                  interaction_id)
    except TimeoutError:
        return unavailable_result("adapter.timeout",
                                  "endpoint timed out after %ss" % timeout,
                                  interaction_id)
    except OSError:
        return unavailable_result("adapter.unreachable",
                                  "endpoint unreachable: %s" % endpoint,
                                  interaction_id)
    elapsed_ms = int((time.monotonic() - start) * 1000)
    if len(body) > max_bytes:
        return unavailable_result("adapter.output_cap_exceeded",
                                  "endpoint body exceeded %d bytes" % max_bytes,
                                  interaction_id)
    try:
        candidate = json.loads(body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return unavailable_result("adapter.malformed_response",
                                  "endpoint returned non-JSON body",
                                  interaction_id)
    return _ok_result(request, "local", profile, candidate, elapsed_ms)


TRANSPORT_REGISTRY = {
    "hosted_cli": _transport_hosted_cli,
    "openai_compatible": _transport_openai_compatible,
}


def _invoke(request, settings):
    if not isinstance(request, dict):
        return unavailable_result("adapter.request_invalid",
                                  "request must be a JSON object", None)
    interaction_id = request.get("interaction_id")
    errs = schema_validate.validate(request, _SCHEMA)
    if errs:
        return unavailable_result("adapter.request_invalid", errs[0],
                                  interaction_id)
    if request.get("operation") == "rubric_review" and \
            not (request.get("payload") or {}).get("rubric_points"):
        return unavailable_result("adapter.request_invalid",
                                  "rubric_review requires payload.rubric_points",
                                  interaction_id)
    if request.get("operation") == "treatment_recommend" and \
            not (request.get("payload") or {}).get("recommendation_request"):
        return unavailable_result(
            "adapter.request_invalid",
            "treatment_recommend requires payload.recommendation_request",
            interaction_id)
    profile, reason = resolve_profile(settings, request.get("profile") or None)
    if reason is not None:
        code = reason["code"]
        if code.startswith("settings."):
            code = "adapter.profile_invalid"
        return unavailable_result(code, reason["message"], interaction_id)
    transport = TRANSPORT_REGISTRY.get(profile.get("transport"))
    if transport is None:
        return unavailable_result("adapter.transport_unknown",
                                  "no transport registered for %r"
                                  % profile.get("transport"),
                                  interaction_id)
    request_json = json.dumps(request, ensure_ascii=False, sort_keys=True)
    return transport(request=request, request_json=request_json,
                     profile=profile, settings=settings)


def invoke(request, settings):
    """The single public boundary (D-01/D-02). Every failure family converts
    to one typed unavailable result; no exception escapes (RESEARCH Pattern 2
    -- authored hints, scoring, lessons, reports and marking continue)."""
    try:
        return _invoke(request, settings)
    except Exception:  # last-resort safety net, never a traceback
        interaction_id = request.get("interaction_id") \
            if isinstance(request, dict) else None
        return unavailable_result("adapter.internal_error",
                                  "unexpected adapter failure", interaction_id)
