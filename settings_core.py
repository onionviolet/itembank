"""Shared settings loading, profile resolution, and mode precedence."""
import json
import os
import sys

import resources
import schema_validate


SCHEMA_RESOURCE = "schemas/settings.schema.json"


SETTINGS_FILE = "itembank.json"


SETTINGS_CODES = tuple(sorted({
    "settings.invalid_type", "settings.invalid_value", "settings.out_of_range",
    "settings.unknown_key", "settings.missing_key", "settings.malformed_file",
}))


def settings_path(base):
    return os.path.join(base or ".", SETTINGS_FILE)


def load_schema():
    return json.loads(resources.read_text(SCHEMA_RESOURCE))


def defaults_from_schema(schema):
    """Walk `properties` recursively and build the full default object from
    the `default` annotations -- the source of truth for both the shipped
    itembank.json (Task 2) and a missing key's effective value (this task).
    """
    defaults = {}
    for key, sub in schema.get("properties", {}).items():
        if sub.get("type") == "object" and "properties" in sub:
            defaults[key] = defaults_from_schema(sub)
        else:
            defaults[key] = sub.get("default")
    return defaults


def merge_over_defaults(defaults, raw):
    """Merge `raw` (the file on disk) over `defaults`, one level of nested
    objects deep, so a settings file missing a key -- or missing one nested
    key inside a known object -- reads as that key's schema default rather
    than as absent. Any top-level key in `raw` that `defaults` does not know
    about is preserved verbatim: unknown, not dropped.
    """
    merged = dict(defaults)
    for key, value in defaults.items():
        if key not in raw:
            continue
        if isinstance(value, dict) and isinstance(raw[key], dict):
            merged[key] = merge_over_defaults(value, raw[key])
        else:
            merged[key] = raw[key]
    for key, value in raw.items():
        if key not in merged:
            merged[key] = value
    return merged


def load_settings(base):
    """Read itembank.json (when present) merged over the schema's own
    defaults, so a missing key reads as its default rather than as absent
    (the planner_assumptions resolution). A file that will not parse as JSON
    exits with settings.malformed_file naming the path and the decode error
    -- the same sys.exit-on-bad-file shape runtime.read_session already uses
    for session files.

    The merged document is then validated one known top-level key at a time
    against that key's own subschema -- the same `schema_validate.validate()`
    call `cmd_config`'s `set` action already runs against a single new value.
    A syntactically-valid-JSON settings file that is schema-*invalid* (a
    string where `daemon` should be an object, a non-integer `daemon.port`,
    ...) exits here with a `settings.*`-coded message instead of reaching a
    caller (`cmd_daemon`, `set_at`, a raw socket bind) and crashing with a
    Python traceback. Validating per-key rather than validating the whole
    document at once deliberately does not enforce the schema's top-level
    `additionalProperties: false` -- an unrecognized top-level key must keep
    reading back and round-tripping untouched (see `merge_over_defaults`'s
    own "unknown, not dropped" contract and `test_unknown_key_preserved`).
    """
    schema = load_schema()
    defaults = defaults_from_schema(schema)
    path = settings_path(base)
    if not os.path.exists(path):
        return dict(defaults)
    try:
        with open(path, encoding="utf-8") as source_handle:
            raw = json.load(source_handle)
    except (OSError, ValueError) as exc:
        sys.exit("settings.malformed_file: cannot read %s: %s" % (path, exc))
    if not isinstance(raw, dict):
        sys.exit("settings.malformed_file: %s does not contain a JSON object" % path)
    merged = merge_over_defaults(defaults, raw)
    errs = []
    for key, subschema in schema.get("properties", {}).items():
        if key in merged:
            # A profile saved by a future or removed registration must not
            # make Settings inaccessible. Preserve it for a visible fallback
            # notice while validating its basic scalar shape here.
            if key == "presentation_profile":
                if not isinstance(merged[key], str):
                    errs.append("presentation_profile is not a string")
                continue
            errs.extend(schema_validate.validate(merged[key], subschema))
    if errs:
        sys.exit("%s: %s" % (classify_error(errs[0]), errs[0]))
    return merged


def resolve_profile(settings_data, name=None):
    """The active model_backend profile resolver, shared by the adapter and
    `itembank config` (RESEARCH.md Architectural Responsibility Map row 1:
    configuration and adapter read the same validated settings). Returns
    (profile_or_None, error_or_None); exactly one is non-None.

    A duplicate profile name or a profile missing its transport-required
    field is settings.invalid_value (a bad registry, never a silent
    fallback); an active name that matches no profile is
    adapter.profile_unknown; an empty active profile or empty profiles array
    is adapter.profile_disabled (a typed unavailable, never a crash). An
    unrecognized transport name is NOT rejected here: it routes if a
    TRANSPORT_REGISTRY entry exists (D-27 -- a third backend is a module
    plus a config entry, no resolver edit), and the adapter resolves an
    unregistered transport to adapter.transport_unknown -- still typed
    unavailable, never a silent fallback.
    """
    mb = (settings_data or {}).get("model_backend")
    if not isinstance(mb, dict):
        return None, {"code": "settings.invalid_value",
                      "message": "model_backend is not an object"}
    active = mb.get("active") or ""
    profiles = mb.get("profiles") or []
    if not isinstance(profiles, list):
        return None, {"code": "settings.invalid_value",
                      "message": "model_backend.profiles is not an array"}
    if not active or not profiles:
        return None, {"code": "adapter.profile_disabled",
                      "message": "no active model backend profile (model_backend.active "
                                 "is empty or profiles is empty)"}
    by_name = {}
    for i, profile in enumerate(profiles):
        if not isinstance(profile, dict):
            return None, {"code": "settings.invalid_value",
                          "message": "model_backend.profiles[%d] is not an object" % i}
        pname = profile.get("name")
        if not isinstance(pname, str) or not pname:
            return None, {"code": "settings.invalid_value",
                          "message": "model_backend.profiles[%d] has no non-empty name" % i}
        if pname in by_name:
            return None, {"code": "settings.invalid_value",
                          "message": "duplicate model backend profile name %r" % pname}
        transport = profile.get("transport")
        if not isinstance(transport, str) or not transport:
            return None, {"code": "settings.invalid_value",
                          "message": "profile %r has no transport" % pname}
        if transport == "hosted_cli" and not profile.get("command"):
            return None, {"code": "settings.invalid_value",
                          "message": "profile %r (hosted_cli) requires a command array"
                          % pname}
        if transport == "openai_compatible" and not profile.get("endpoint"):
            return None, {"code": "settings.invalid_value",
                          "message": "profile %r (openai_compatible) requires an endpoint"
                          % pname}
        # Any other transport name is deferred to the adapter's
        # TRANSPORT_REGISTRY (see the docstring's D-27 note).
        by_name[pname] = profile
    target = name or active
    if target not in by_name:
        return None, {"code": "adapter.profile_unknown",
                      "message": "no model backend profile named %r" % target}
    return by_name[target], None


def classify_error(msg):
    """Map one schema_validate.validate() output string to one of
    SETTINGS_CODES by matching the substrings that validator actually emits.
    This is the one place a validator message becomes a dotted code; it does
    not change schema_validate.validate()'s own return contract (a list of
    plain strings), which every existing CI caller still depends on.
    """
    if "expected type" in msg or "does not equal const" in msg:
        return "settings.invalid_type"
    if "is not one of" in msg:
        return "settings.invalid_value"
    if "is less than minimum" in msg or "is greater than maximum" in msg:
        return "settings.out_of_range"
    if "additional property" in msg:
        return "settings.unknown_key"
    if "missing required key" in msg:
        return "settings.missing_key"
    return "settings.invalid_value"


# Ordered lowest authority first. Later layers override earlier ones.
MODE_LAYERS = ("learner_preference", "author_strategy", "objective_constraint",
               "accommodation_override", "instructor_policy",
               "runtime_authority", "system_safety")


MODE_LAYERS_FIXED = ("runtime_authority", "system_safety")


MODE_LAYER_CONFLICT_TEMPLATE = ("{setting} is set by {layer} for this course "
                                "and can't be changed here.")


MODE_LAYER_DISPLAY_PHRASES = {
    "learner_preference": "your own preference",
    "author_strategy": "this course's design",
    "objective_constraint": "this objective's requirements",
    "accommodation_override": "your accommodation settings",
    "instructor_policy": "your instructor's policy",
    "runtime_authority": "itembank's assessment rules",
    "system_safety": "itembank's safety rules",
}


def mode_layer_conflict_copy(setting_name, layer):
    """The exact locked sentence for one refused control. Raises `KeyError`
    for an unknown layer rather than emitting a sentence naming nothing."""
    return MODE_LAYER_CONFLICT_TEMPLATE.format(
        setting=setting_name, layer=MODE_LAYER_DISPLAY_PHRASES[layer])


def mode_layer_resolve(setting_name, requests):
    """The pure half of the mode-layer contract.

    It reads only its two arguments. It imports no strategy, accommodation, or
    instructor record and touches no file. The collector that populates
    `requests` from live state is Phase 16C's under D8 and D-16B-12, so there
    is one precedence rule in this repository and not two.

    The winning layer is the highest-indexed member of `MODE_LAYERS` present
    in `requests`. An unknown key raises `ValueError` rather than being
    ignored, because silently dropping a layer would let a caller believe its
    request was considered.
    """
    for key in requests:
        if key not in MODE_LAYERS:
            raise ValueError("unknown mode layer: %r" % key)

    present = [layer for layer in MODE_LAYERS if layer in requests]
    if not present:
        return {"value": None, "winning_layer": None, "conflict": False,
                "copy": ""}

    winner = present[-1]
    value = requests[winner]
    conflict = any(requests[layer] != value for layer in present[:-1])
    return {"value": value, "winning_layer": winner, "conflict": conflict,
            "copy": (mode_layer_conflict_copy(setting_name, winner)
                     if conflict else "")}

