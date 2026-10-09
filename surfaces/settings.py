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

import retention
from settings_core import (SCHEMA_RESOURCE, SETTINGS_FILE, SETTINGS_CODES,
                           settings_path, load_schema, defaults_from_schema,
                           merge_over_defaults, load_settings, resolve_profile,
                           classify_error)


# This phase's own identifier; a key whose x-itembank-phase is at or below
# this number is "read by this phase" rather than reported as inert. A float
# so a sub-phase (2.1) can sit strictly between its parent (2) and the next
# whole phase (3) without renumbering anything.
THIS_PHASE = 10

# The phase 3.1 style settings group defaults (plan 03.1-05 Task 3). The
# schema remains the source of truth -- defaults_from_schema() mirrors it
# into itembank.json and into a missing key's effective value -- and this
# accessor exists so the authoring loops and the roundtrip tests can read the
# shipped defaults without a settings load.
STYLE_SETTINGS_DEFAULTS = {"imperative_cap": 7, "warn_fp_threshold": 0.20}


# The Phase 16B (16.2) network-egress group defaults. The schema remains the
# source of truth -- defaults_from_schema() mirrors it into itembank.json and
# into a missing key's effective value -- and this accessor exists so callers
# and the roundtrip tests can read the shipped defaults without a settings
# load.
NETWORK_EGRESS_SETTINGS_DEFAULTS = {"hosted_operations": "off",
                                    "last_disclosure": ""}

# The Phase 16B (16.2) accessibility group defaults, same contract as above:
# the schema is the source of truth and this mirrors it for callers and tests.
ACCESSIBILITY_SETTINGS_DEFAULTS = {"reduced_motion": "system",
                                   "high_contrast": "system"}

# The Phase 16B (16.2) storage group defaults, same contract as above. Backups
# are off and neither directory names a real path, which is the restrictive
# default the group's schema description states.
STORAGE_SETTINGS_DEFAULTS = {"data_dir": "", "backups_enabled": False,
                             "backup_dir": ""}

# The Chrome-voice panel label for each settings group the 16B UI-SPEC's
# Settings Expansion Contract names. One file owns the label text so a later
# surface reads it rather than restating it. `model_backend` and
# `update_policy` are listed for label completeness only: neither key's
# schema, default, nor behavior changes in this phase.
SETTINGS_GROUP_LABELS = {
    "approved_roots": "Approved roots",
    "network_egress": "Network & sharing",
    "accessibility": "Accessibility",
    "storage": "Storage & backups",
    "model_backend": "Model backends",
    "update_policy": "Updates",
}

# Printed once beside any top-level group the runtime does not act on yet, so
# a preference says so on the same screen it is offered rather than implying
# an effect. Driven by the group's own x-itembank-phase against THIS_PHASE,
# never by a hard-coded key list, so the line disappears by itself when a
# later phase raises THIS_PHASE.
SETTINGS_DECLARED_NOT_ENFORCED_NOTE = ("Declared for a later release. itembank "
                                       "records this preference and nothing "
                                       "acts on it yet.")


# The plan 03.2-04 paraphrase lint settings group defaults (D-13). The
# schema remains the source of truth -- defaults_from_schema() mirrors it
# into itembank.json -- and this accessor exists so the linter and the
# roundtrip tests can read the shipped defaults without a settings load.
PARAPHRASE_SETTINGS_DEFAULTS = {"winnow_threshold": 8, "jaccard_threshold": 0.25}

# The Phase 6.2 gate settings group defaults (06.2-UI-SPEC section 10):
# `gate_skip` (always default) and `gate_policy` (as-authored default, may
# only weaken a declared gate -- the enum has no strengthening value). The
# schema remains the source of truth; this accessor exists so the daemon
# and the roundtrip tests can read the shipped defaults without a load.
GATE_SETTINGS_DEFAULTS = {"gate_skip": "always", "gate_policy": "as-authored"}

# The Phase 13.5 `teaching` group defaults (13.5-UI-SPEC section 16): where the
# authored hint ladder sits (`hint_display`, slot) and how much of its locked
# remainder is previewed (`hint_locked_preview`, full). The schema remains the
# source of truth; this accessor exists so the teach adapter and the roundtrip
# tests can read the shipped defaults without a settings load -- and so a
# settings file that somehow carries no `teaching` object still resolves the
# preview server-side rather than leaving it to a client.
TEACHING_SETTINGS_DEFAULTS = {"hint_display": "slot",
                              "hint_locked_preview": "full"}

# Phase 20 presentation is a composition axis. These values are durable
# settings names, unlike CSS classes or the current visual recipe.
PRESENTATION_PROFILES = ("field-guide", "trajectory-deck")
DEFAULT_PRESENTATION_PROFILE = "field-guide"


def style_defaults():
    """The `style` settings group's shipped defaults: `imperative_cap`
    (default 7, D-17) and `warn_fp_threshold` (default 0.20, D-14)."""
    return dict(STYLE_SETTINGS_DEFAULTS)


def paraphrase_defaults():
    """The `paraphrase` settings group's shipped defaults (D-13):
    `winnow_threshold` (default 8 consecutive copied words -> error) and
    `jaccard_threshold` (default 0.25 fingerprint overlap -> warning)."""
    return dict(PARAPHRASE_SETTINGS_DEFAULTS)


def retention_defaults():
    """The `retention` settings group's shipped defaults (Phase 10, D-06):
    the conservative researched thresholds and weight terms, mirrored from
    `retention.RETENTION_SETTINGS_DEFAULTS` -- the same accessor pattern as
    the style/paraphrase groups, so tests and the pure module read one set
    of numbers without a settings load."""
    return dict(retention.RETENTION_SETTINGS_DEFAULTS)


def gate_defaults():
    """The Phase 6.2 `reader` gate settings' shipped defaults (06.2-UI-SPEC
    section 10): `gate_skip` (always) and `gate_policy` (as-authored)."""
    return dict(GATE_SETTINGS_DEFAULTS)


def teaching_defaults():
    """The Phase 13.5 `teaching` settings' shipped defaults (13.5-UI-SPEC section
    16): `hint_display` (slot) and `hint_locked_preview` (full)."""
    return dict(TEACHING_SETTINGS_DEFAULTS)


def resolve_presentation_profile(settings_data):
    """Return ``(active, notice)`` without mutating a saved preference.

    A missing value is the additive migration path. An unknown value is kept
    visible and falls back safely, so removing a recipe cannot affect course,
    bank, session, or evidence files.
    """
    value = (settings_data or {}).get("presentation_profile")
    if value in PRESENTATION_PROFILES:
        return value, None
    if value in (None, ""):
        return DEFAULT_PRESENTATION_PROFILE, None
    return DEFAULT_PRESENTATION_PROFILE, (
        "Unsupported presentation profile '%s'. Showing Field Guide until you save a supported profile."
        % value)


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
        phase = sub.get("x-itembank-phase")
        if phase is not None and phase > THIS_PHASE:
            label = SETTINGS_GROUP_LABELS.get(name)
            print("  %-26s %s%s" % ("", (label + ": ") if label else "",
                                    SETTINGS_DECLARED_NOT_ENFORCED_NOTE))
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
