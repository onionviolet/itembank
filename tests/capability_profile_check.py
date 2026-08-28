#!/usr/bin/env python3
"""The Phase 16A capability-registry unit check (plan 16A-04 Tasks 1 and 2).

CAP-02 says each semantic capability declares six things and that an
unavailable renderer shows the static instructional path. This file asserts
the first half: that all fifteen profiles exist, carry every field, validate
against the published schema, resolve their availability from the caller's
situation rather than from a global, and refuse a duplicate registration.

The three probe rows CAP-02 returned are answered here by name: adjacency is
the duplicate-name refusal, empty is `profile` returning None and
`profiles({})` returning an empty tuple, and ordering is the literal source
order being stable across calls.

The schema and the module tuples are read from their two homes and compared,
never restated here. A test that carried its own copy of the availability
vocabulary would go green while the two real homes drifted apart, which is
the coupling discipline `tests/protocol_roundtrip.py` already applies to the
lint namespace.

Standard library only, no test framework, runnable as
`python tests/capability_profile_check.py`.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import capabilities                                          # noqa: E402
import schema_validate                                       # noqa: E402

SCHEMA_PATH = os.path.join(ROOT, "schemas",
                           "capability_profile.schema.json")

EXPECTED_COUNT = 15


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def _schema():
    with open(SCHEMA_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def check_registry_shape():
    entries = capabilities.profiles()
    if len(entries) != EXPECTED_COUNT:
        fail("the registry carries %d profiles, expected %d"
             % (len(entries), EXPECTED_COUNT))
    want = tuple(sorted(capabilities.CAPABILITY_PROFILE_KEYS))
    for entry in entries:
        if tuple(sorted(entry)) != want:
            fail("profile %r carries the key set %s, expected exactly %s"
                 % (entry.get("name"), sorted(entry),
                    list(capabilities.CAPABILITY_PROFILE_KEYS)))
        findings = capabilities.validate_profile(entry)
        if findings:
            fail("profile %r is malformed: %s"
                 % (entry.get("name"), "; ".join(findings)))
        limits = (entry.get("known_limits") or "").strip().lower()
        if limits == "none":
            fail("profile %r says its known_limits are none; every one of "
                 "these fifteen has a real limitation and a profile that "
                 "hides it is worse than no profile" % entry.get("name"))


def check_empty_and_missing():
    """CAP-02's empty probe: an unregistered name and an empty registry are
    ordinary answers, not exceptions."""
    if capabilities.profile("no_such_name") is not None:
        fail("profile() returns something for an unregistered name")
    if capabilities.profiles({}) != ():
        fail("profiles() over an empty registry is not the empty tuple")
    if capabilities.profile("callout_key", {}) is not None:
        fail("profile() over an empty registry is not None")
    if capabilities.static_path("no_such_name") != "":
        fail("static_path() for an unregistered name is not the empty "
             "string; a caller rendering a fallback should not have to "
             "branch on whether the capability was unknown or declared none")


def check_ordering():
    """CAP-02's ordering probe: two calls in the same interpreter return
    equal tuples, in the module dict's literal source order."""
    first = capabilities.profiles()
    second = capabilities.profiles()
    if first != second:
        fail("two profiles() calls returned different tuples")
    names = [e["name"] for e in first]
    if names != sorted(names, key=names.index):
        fail("profiles() order is not stable")
    if names[0] != "callout_key" or names[-1] != "guided_mode":
        fail("profiles() order is %r; the catalog order runs callout_key "
             "first and guided_mode last" % names)


def check_catalog_coupling():
    """Fifteen profiles, fourteen catalog roles, and exactly one profile that
    is not a teaching role. Without this the two lists drift, and a role
    added in a later phase leaves a profile-less capability nothing notices.
    """
    by_name = {e["name"]: e for e in capabilities.profiles()}
    mapped = set()
    for role in capabilities.SEMANTIC_ROLE_CATALOG:
        name = capabilities.catalog_profile_name(role["role"])
        if name is None:
            fail("catalog role %r maps to no capability profile name"
                 % role["role"])
        if name not in by_name:
            fail("catalog role %r maps to %r, which is not registered"
                 % (role["role"], name))
        mapped.add(name)
    extra = sorted(set(by_name) - mapped)
    if extra != ["guided_mode"]:
        fail("the profiles with no catalog role are %r, expected exactly "
             "['guided_mode']" % extra)


def check_resolved_availability():
    if capabilities.resolved_availability("inline_check", {}) != "unavailable":
        fail("inline_check with no gate context does not resolve to "
             "unavailable, so the Degraded clause has no trigger")
    if capabilities.resolved_availability(
            "inline_check", {"gate_context": True}) != "available":
        fail("inline_check with a gate context does not resolve to available")
    if capabilities.resolved_availability("no_such_name", {}) != "unavailable":
        fail("an unregistered name does not resolve to unavailable")
    for entry in capabilities.profiles():
        for context in ({}, {"scripting": True, "serving_runtime": True},
                        {"unknown_future_fact": True}):
            got = capabilities.resolved_availability(entry["name"], context)
            if got not in capabilities.RENDERER_AVAILABILITY:
                fail("resolved_availability(%r, %r) returned %r, which is "
                     "outside the closed vocabulary"
                     % (entry["name"], context, got))


def check_duplicate_registration():
    """CAP-02's adjacency probe: a second registration under a live name is
    refused by name, and nothing is merged and nothing is replaced."""
    before = capabilities.profiles()
    clash = dict(before[0])
    try:
        capabilities.register(clash)
    except capabilities.CapabilityError as exc:
        if clash["name"] not in str(exc):
            fail("the duplicate-registration refusal does not name the "
                 "duplicate: %s" % exc)
    else:
        fail("registering a name already in the registry did not raise")
    if capabilities.profiles() != before:
        fail("a refused registration changed the module registry")


def check_register_is_pure():
    before = len(capabilities.profiles())
    synthetic = {
        "name": "synthetic_probe",
        "accessible_behavior": "Fictional. Renders as text.",
        "offline_fallback": "Fictional. Renders as text with no script.",
        "renderer_availability": "unavailable",
        "version": 1,
        "validation": "Fictional. Nothing validates a probe.",
        "known_limits": "Fictional. It teaches nothing.",
    }
    merged = capabilities.register(synthetic)
    if "synthetic_probe" not in merged:
        fail("register() did not return a registry carrying the new entry")
    if len(capabilities.profiles()) != before:
        fail("register() mutated the module registry; a fixture registering "
             "a synthetic capability would leak it into every later caller")
    if capabilities.profile("synthetic_probe") is not None:
        fail("register() leaked a synthetic capability into the module "
             "registry")
    if capabilities.static_path("synthetic_probe", merged) \
            != synthetic["offline_fallback"]:
        fail("static_path over the returned registry does not read the new "
             "entry's fallback")


def check_schema_accepts_itself():
    schema = _schema()
    try:
        schema_validate.check_schema(schema)
    except schema_validate.SchemaError as exc:
        fail("schemas/capability_profile.schema.json uses a keyword the "
             "shipped validator refuses: %s" % exc)


def check_schema_validates_every_profile():
    schema = _schema()
    for entry in capabilities.profiles():
        errors = schema_validate.validate(entry, schema)
        if errors:
            fail("profile %r does not validate against the published "
                 "schema: %s" % (entry["name"], "; ".join(errors)))


def check_schema_refuses_broken_profiles():
    """Four deliberately broken profiles, each of which must fail. A schema
    that accepted any of these would be publishing a contract it does not
    enforce."""
    schema = _schema()
    good = dict(capabilities.profile("callout_key"))

    missing = dict(good)
    del missing["offline_fallback"]
    bad_state = dict(good, renderer_availability="sometimes")
    extra = dict(good, colour="blue")
    empty = dict(good, offline_fallback="")

    for label, instance, needle in (
            ("a profile missing offline_fallback", missing,
             "offline_fallback"),
            ("a profile whose renderer_availability is 'sometimes'",
             bad_state, "renderer_availability"),
            ("a profile carrying an extra 'colour' key", extra, "colour"),
            ("a profile whose offline_fallback is empty", empty,
             "offline_fallback")):
        errors = schema_validate.validate(instance, schema)
        if not errors:
            fail("%s validated clean against the published schema" % label)
        if not any(needle in e for e in errors):
            fail("%s produced errors that do not name %r: %s"
                 % (label, needle, "; ".join(errors)))


def check_schema_drift():
    """The schema and the module tuples are two homes for one vocabulary.
    Compared here rather than restated, so a change to either goes red."""
    schema = _schema()
    enum = schema["properties"]["renderer_availability"]["enum"]
    if enum != list(capabilities.RENDERER_AVAILABILITY):
        fail("the schema's renderer_availability enum is %r but "
             "capabilities.RENDERER_AVAILABILITY is %r"
             % (enum, list(capabilities.RENDERER_AVAILABILITY)))
    required = sorted(schema["required"])
    if required != sorted(capabilities.CAPABILITY_PROFILE_KEYS):
        fail("the schema's required array is %r but "
             "capabilities.CAPABILITY_PROFILE_KEYS is %r"
             % (required, sorted(capabilities.CAPABILITY_PROFILE_KEYS)))
    if schema.get("additionalProperties") is not False:
        fail("the schema does not set additionalProperties to false, so an "
             "unknown key would validate clean")


def check_validator_still_refuses_unsupported_keywords():
    """The validator's own refusal path, proven rather than assumed: a copy
    of the schema carrying a keyword outside SUPPORTED and outside
    ANNOTATIONS is refused outright. Nothing is written to disk."""
    broken = _schema()
    broken["patternProperties"] = {"^x": {"type": "string"}}
    try:
        schema_validate.check_schema(broken)
    except schema_validate.SchemaError:
        return
    fail("schema_validate.check_schema accepted an unsupported keyword, so "
         "a schema could go green while half its contract went unchecked")


CHECKS = (check_registry_shape, check_empty_and_missing, check_ordering,
          check_catalog_coupling, check_resolved_availability,
          check_duplicate_registration, check_register_is_pure,
          check_schema_accepts_itself, check_schema_validates_every_profile,
          check_schema_refuses_broken_profiles, check_schema_drift,
          check_validator_still_refuses_unsupported_keywords)


def main():
    for check in CHECKS:
        check()
    print("capability registry ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
