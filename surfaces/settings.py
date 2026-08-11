"""The settings surface: `itembank config` is to `itembank.json` what `itembank
spec` is to the bank format and `itembank schema` is to the published
documents -- one contract, printed either as a human summary or verbatim off
disk, and one validator behind every write.

There is exactly one validator here, `schema_validate.validate()` -- the same
function `schemas/*.json` already use. `classify_error` is a thin string
classifier over that validator's plain-string error output; it does not
duplicate any type or range check, it only names which of the six published
codes (`SETTINGS_CODES`) a given validator message belongs to.
"""
import json
import os
import sys

import resources
import schema_validate


# Archive-relative path (see resources.py): resolves inside a checkout and
# inside a .pyz alike, unlike the __file__-relative path this replaced.
SCHEMA_RESOURCE = "schemas/settings.schema.json"

SETTINGS_FILE = "itembank.json"

# This phase's own identifier; a key whose x-itembank-phase is at or below
# this number is "read by this phase" rather than reported as inert. A float
# so a sub-phase (2.1) can sit strictly between its parent (2) and the next
# whole phase (3) without renumbering anything.
THIS_PHASE = 9

# The published dotted error-code namespace (D-06), extending Phase 1's D-16
# lint-code precedent. Built from a set-then-sorted tuple so it is provably
# sorted and duplicate-free regardless of the order the codes are written
# below. Adding a code here is additive; renaming or removing one is a
# breaking change for every consumer that branches on it.
SETTINGS_CODES = tuple(sorted({
    "settings.invalid_type", "settings.invalid_value", "settings.out_of_range",
    "settings.unknown_key", "settings.missing_key", "settings.malformed_file",
}))


# The phase 3.1 style settings group defaults (plan 03.1-05 Task 3). The
# schema remains the source of truth -- defaults_from_schema() mirrors it
# into itembank.json and into a missing key's effective value -- and this
# accessor exists so the authoring loops and the roundtrip tests can read the
# shipped defaults without a settings load.
STYLE_SETTINGS_DEFAULTS = {"imperative_cap": 7, "warn_fp_threshold": 0.20}


# The plan 03.2-04 paraphrase lint settings group defaults (D-13). The
# schema remains the source of truth -- defaults_from_schema() mirrors it
# into itembank.json -- and this accessor exists so the linter and the
# roundtrip tests can read the shipped defaults without a settings load.
PARAPHRASE_SETTINGS_DEFAULTS = {"winnow_threshold": 8, "jaccard_threshold": 0.25}


def style_defaults():
    """The `style` settings group's shipped defaults: `imperative_cap`
    (default 7, D-17) and `warn_fp_threshold` (default 0.20, D-14)."""
    return dict(STYLE_SETTINGS_DEFAULTS)


def paraphrase_defaults():
    """The `paraphrase` settings group's shipped defaults (D-13):
    `winnow_threshold` (default 8 consecutive copied words -> error) and
    `jaccard_threshold` (default 0.25 fingerprint overlap -> warning)."""
    return dict(PARAPHRASE_SETTINGS_DEFAULTS)


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
        raw = json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError) as exc:
        sys.exit("settings.malformed_file: cannot read %s: %s" % (path, exc))
    if not isinstance(raw, dict):
        sys.exit("settings.malformed_file: %s does not contain a JSON object" % path)
    merged = merge_over_defaults(defaults, raw)
    errs = []
    for key, subschema in schema.get("properties", {}).items():
        if key in merged:
            errs.extend(schema_validate.validate(merged[key], subschema))
    if errs:
        sys.exit("%s: %s" % (classify_error(errs[0]), errs[0]))
    return merged


def write_settings(base, data):
    """Write itembank.json tmp-then-os.replace(), matching
    runtime.write_session's crash-safety and byte layout exactly -- the same
    json.dump(..., ensure_ascii=False, indent=2) plus a trailing newline,
    which is what makes a repeated `config set` byte-identical rather than
    merely equivalent.
    """
    target = settings_path(base)
    target_dir = os.path.dirname(os.path.abspath(target))
    os.makedirs(target_dir, exist_ok=True)
    tmp = target + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    os.replace(tmp, target)


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


def get_at(data, dotted):
    node = data
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def set_at(data, dotted, value):
    parts = dotted.split(".")
    node = data
    for part in parts[:-1]:
        node = node.setdefault(part, {})
    node[parts[-1]] = value


def schema_for_key(schema, dotted):
    """Walk `schema`'s nested `properties` along `dotted`'s path segments.
    Returns None at any level that does not resolve -- an unknown key, be it
    top-level (`nope`) or nested under a known object (`daemon.nope`).
    """
    node = schema
    for part in dotted.split("."):
        props = node.get("properties") if isinstance(node, dict) else None
        if not props or part not in props:
            return None
        node = props[part]
    return node


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


def decode_value(raw):
    """Decode a CLI value as JSON so `9000`, `true`, `0.4` and a JSON array
    arrive as their real types; fall back to the raw string on a decode
    failure so plain words like `system` and `hosted` behave.
    """
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def range_or_enum(sub):
    if "enum" in sub:
        return "|".join(str(v) for v in sub["enum"])
    if "minimum" in sub or "maximum" in sub:
        return "%s..%s" % (sub.get("minimum", "-inf"), sub.get("maximum", "inf"))
    if sub.get("type") == "boolean":
        return "true|false"
    if sub.get("type") == "object":
        return "(see nested rows)"
    return "(free-form)"


def status_text(phase):
    if phase is not None and phase <= THIS_PHASE:
        return "read by this phase"
    # A plain ASCII dash, not an em dash: this line reaches a real console,
    # and the project's own house style already writes "--" in printed
    # prose rather than risk a non-ASCII character on a codepage console.
    return "inert -- read from phase %s" % phase


def render_value(value, is_object):
    return "(nested, see rows below)" if is_object else repr(value)


def print_row(name, sub, default, current, indent=False):
    label = ("  " if indent else "") + name
    is_object = sub.get("type") == "object"
    print("  %-26s %-9s %-30s %-14s %-14s %s" %
          (label, sub.get("type", ""), range_or_enum(sub),
           render_value(default, is_object), render_value(current, is_object),
           status_text(sub.get("x-itembank-phase"))))


def print_table(schema, data):
    defaults = defaults_from_schema(schema)
    print("itembank.json settings (schemas/settings.schema.json):\n")
    print("  %-26s %-9s %-30s %-14s %-14s %s" %
          ("KEY", "TYPE", "ALLOWED / RANGE", "DEFAULT", "CURRENT", "STATUS"))
    for name, sub in schema["properties"].items():
        print_row(name, sub, defaults.get(name), data.get(name))
        if sub.get("type") == "object" and "properties" in sub:
            nested_default = defaults.get(name) or {}
            nested_current = data.get(name) if isinstance(data.get(name), dict) else {}
            for nested_name, nested_sub in sub["properties"].items():
                print_row(name + "." + nested_name, nested_sub,
                          nested_default.get(nested_name), nested_current.get(nested_name),
                          indent=True)

    known = set(schema["properties"])
    unknown = sorted(k for k in data if k not in known)
    if unknown:
        print("\nUnknown to schemas/settings.schema.json -- preserved on write, read by "
              "nothing:")
        for k in unknown:
            print("  %s = %r" % (k, data[k]))

    print("\nRun `itembank config schema` for the raw JSON Schema document, or "
          "`itembank config set KEY VALUE` to change one setting.")


def cmd_config(a):
    schema = load_schema()

    if a.action == "schema":
        print(resources.read_text(SCHEMA_RESOURCE), end="")
        return 0

    if a.action == "set":
        if not a.key or a.value is None:
            sys.exit("usage: itembank config set KEY VALUE (key=%r value=%r)" %
                     (a.key, a.value))
        new_value = decode_value(a.value)

        subschema = schema_for_key(schema, a.key)
        if subschema is None:
            top_level = sorted(schema["properties"])
            sys.exit("settings.unknown_key: %r is not a known settings key; "
                     "top-level keys: %s" % (a.key, ", ".join(top_level)))

        errs = schema_validate.validate(new_value, subschema)
        if errs:
            sys.exit("%s: %s" % (classify_error(errs[0]), errs[0]))

        data = load_settings(a.base)
        set_at(data, a.key, new_value)
        write_settings(a.base, data)
        print("set %s = %s" % (a.key, json.dumps(new_value, ensure_ascii=False)))
        return 0

    data = load_settings(a.base)
    print_table(schema, data)
    return 0
