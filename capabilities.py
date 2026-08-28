#!/usr/bin/env python3
"""The capability support profile registry (Phase 16A, CAP-02, D-16A-2).

A capability profile answers one question: does a renderer for this authored
capability exist here, and what does a learner see when it does not. It
records the accessible behavior, the offline fallback, the renderer
availability, the profile version, how the capability is validated, and its
known limits, so an authored block's degradation is a published fact rather
than a discovery made at render time.

**A capability profile never decides disclosure.** Renderer availability
describes whether a renderer exists; it never describes whether a learner may
see an answer, a key, a rationale, or a hint tier. That decision belongs to
`runtime.public_item` and `runtime.glossable` and to no other module, and
nothing here may be read as widening it. A capability that is `available`
grants a rendering path and grants nothing else.

**This module is pure.** It reads no file, writes no file, holds no session
state, and imports neither `evidence` nor `runtime`. Every public function
returns a value computed from its arguments and this module's own constants,
so calling one twice with the same arguments returns the same answer and
calling one never changes what another sees.

Adding a capability is a one-entry registration in the module-level dict
below, the pattern `model.GATE_VALUES` and `surfaces/lesson.py`'s
`_CALLOUT_KINDS` already establish. `register()` returns a new dict rather
than mutating the module's own, so a fixture or a test that registers a
synthetic capability cannot leak it into another caller's view.

`SEMANTIC_ROLE_CATALOG` is a catalog and not a source of truth (D-16A-1
option-a): `surfaces.lesson._CALLOUT_KINDS` and the seven shipped mechanisms
outside it remain authoritative for what a role means, and the catalog exists
only so CAP-01's fourteen-role completeness claim is machine checkable rather
than prose that can quietly go stale.
"""

# The exact key set every capability profile carries, in this order. A profile
# missing a key or carrying an extra one is refused by `register`, so a
# half-described capability cannot enter the registry and be discovered later
# by a renderer that assumed the field was there.
CAPABILITY_PROFILE_KEYS = ("name", "accessible_behavior", "offline_fallback",
                           "renderer_availability", "version", "validation",
                           "known_limits")

# The closed renderer-availability vocabulary (D-16A-5), in GATE_VALUES' exact
# shape. Three members rather than two: the binary present-or-absent split
# cannot describe a renderer that works partially, and a partial renderer
# reported as `available` is how a learner meets a half-drawn block with no
# warning.
RENDERER_AVAILABILITY = ("available", "degraded", "unavailable")


class CapabilityError(Exception):
    """A malformed capability registration: a wrong key set, an availability
    value outside the closed vocabulary, or a name already registered."""


# Seeded with exactly one profile on purpose. This plan is a tracer, and the
# point of a tracer is that one capability travels the whole path rather than
# that a registry is complete before anything reads it. Plan 16A-04 adds the
# rest.
_CAPABILITY_PROFILES = {
    "callout_prerequisite": {
        "name": "callout_prerequisite",
        "accessible_behavior": (
            "Renders as a labelled section with a visible text label; "
            "reachable in document order by keyboard and by screen reader "
            "with no interaction required."),
        "offline_fallback": (
            "The block renders as a labelled paragraph with no script and no "
            "network."),
        "renderer_availability": "available",
        "version": 1,
        "validation": (
            "model.lint reports an unknown callout kind as "
            "lesson.unknown_semantic."),
        "known_limits": (
            "The label is not translated; the block carries the lesson's "
            "document language."),
    },
}


def _registry_or_default(registry):
    return _CAPABILITY_PROFILES if registry is None else registry


def profile(name, registry=None):
    """The profile registered under `name`, as a shallow copy, or `None`.

    A copy rather than the stored dict, so a caller that edits what it was
    handed cannot silently rewrite the registry for every later caller. An
    unregistered name returns `None` rather than raising and rather than
    returning a partial dict: an absent capability is an ordinary answer here,
    and the caller decides what to do about it.
    """
    entry = _registry_or_default(registry).get(name)
    return dict(entry) if entry is not None else None


def profiles(registry=None):
    """Every registered profile, as shallow copies, in insertion order, which
    for the module's own registry is its literal source order."""
    return tuple(dict(entry)
                 for entry in _registry_or_default(registry).values())


def register(entry, registry=None):
    """Return a NEW registry carrying `entry` alongside the existing ones.

    Mutates nothing. `register` is the only way a capability enters a
    registry, so its three refusals are the only place a malformed profile can
    be caught: a key set that is not exactly `CAPABILITY_PROFILE_KEYS`, a
    `renderer_availability` outside the closed vocabulary, and a name already
    present. Each raises `CapabilityError` naming the offending value, because
    a registration is code and not authored content, so it fails loudly rather
    than falling back.
    """
    if not isinstance(entry, dict):
        raise CapabilityError(
            "a capability profile must be a dict, got %s"
            % type(entry).__name__)
    keys = tuple(sorted(entry))
    if keys != tuple(sorted(CAPABILITY_PROFILE_KEYS)):
        raise CapabilityError(
            "a capability profile carries exactly the keys %s; got %s"
            % (", ".join(CAPABILITY_PROFILE_KEYS), ", ".join(keys)))
    availability = entry["renderer_availability"]
    if availability not in RENDERER_AVAILABILITY:
        raise CapabilityError(
            "renderer_availability %r is not one of %s"
            % (availability, ", ".join(RENDERER_AVAILABILITY)))
    current = _registry_or_default(registry)
    name = entry["name"]
    if name in current:
        raise CapabilityError(
            "a capability named %r is already registered; registering a "
            "second one would make which profile a renderer reads depend on "
            "registration order" % name)
    merged = dict(current)
    merged[name] = dict(entry)
    return merged


def static_path(name, registry=None):
    """The profile's `offline_fallback` sentence, or the empty string for an
    unregistered name.

    The empty string rather than an exception on purpose: an unregistered
    capability degrades to nothing, which is the same shape as a capability
    that declares no fallback, and a caller rendering a fallback should not
    have to branch on which of those two it met.
    """
    entry = _registry_or_default(registry).get(name)
    return entry["offline_fallback"] if entry is not None else ""


# CAP-01's fourteen semantic teaching roles, in the order the requirement
# lists them, each pointing at the concrete mechanism that renders it. Seven
# of the fourteen shipped before Phase 16A and are catalogued here rather than
# rebuilt; the seven carrying `shipped_in` "16A" are this phase's own.
#
# This tuple is a catalog, never an authority. Nothing renders from it and
# nothing gates on it. It exists so a test can walk CAP-01's completeness
# claim and fail by name when an entry stops resolving, which prose in a
# requirements file cannot do.
SEMANTIC_ROLE_CATALOG = (
    {"role": "key idea",
     "mechanism": "the [!KEY] index card",
     "module": "surfaces.lesson",
     "shipped_in": "3.1",
     "reachable_by": "> [!KEY]"},
    {"role": "warning",
     "mechanism": "the [!WARNING] callout",
     "module": "surfaces.lesson",
     "shipped_in": "3.1",
     "reachable_by": "> [!WARNING]"},
    {"role": "prerequisite",
     "mechanism": "the [!PREREQUISITE] callout",
     "module": "surfaces.lesson",
     "shipped_in": "16A",
     "reachable_by": "> [!PREREQUISITE]"},
    {"role": "misconception",
     "mechanism": "the [!MISCONCEPTION] callout",
     "module": "surfaces.lesson",
     "shipped_in": "16A",
     "reachable_by": "> [!MISCONCEPTION]"},
    {"role": "expert tip",
     "mechanism": "the [!TIP] callout",
     "module": "surfaces.lesson",
     "shipped_in": "16A",
     "reachable_by": "> [!TIP]"},
    {"role": "worked example",
     "mechanism": "the [!EXAMPLE] callout",
     "module": "surfaces.lesson",
     "shipped_in": "3.1",
     "reachable_by": "> [!EXAMPLE]"},
    {"role": "counterexample",
     "mechanism": "the [!COUNTEREXAMPLE] callout",
     "module": "surfaces.lesson",
     "shipped_in": "16A",
     "reachable_by": "> [!COUNTEREXAMPLE]"},
    {"role": "source excerpt",
     "mechanism": "the [!EXCERPT] callout",
     "module": "surfaces.lesson",
     "shipped_in": "16A",
     "reachable_by": "> [!EXCERPT]"},
    {"role": "term and definition",
     "mechanism": "the ## TERMS registry and [[term]] references",
     "module": "model",
     "shipped_in": "3.1",
     "reachable_by": "model.parse_terms"},
    {"role": "uncertainty",
     "mechanism": "the [!UNCERTAINTY] callout",
     "module": "surfaces.lesson",
     "shipped_in": "16A",
     "reachable_by": "> [!UNCERTAINTY]"},
    {"role": "summary",
     "mechanism": "the [!SUMMARY] callout",
     "module": "surfaces.lesson",
     "shipped_in": "16A",
     "reachable_by": "> [!SUMMARY]"},
    {"role": "inline check",
     "mechanism": "the [!CHECK: <id>] reserved slot and its gate band",
     "module": "surfaces.lesson",
     "shipped_in": "6.2",
     "reachable_by": "surfaces.lesson._gate_band_html"},
    {"role": "hint",
     "mechanism": "the six-tier authored hint ladder",
     "module": "runtime",
     "shipped_in": "6",
     "reachable_by": "runtime.authored_hint"},
    {"role": "accessible visual interaction",
     "mechanism": "the visual item type and its interaction contract",
     "module": "runtime",
     "shipped_in": "06.1",
     "reachable_by": "runtime.public_item"},
)


def role_mechanism(role):
    """The `SEMANTIC_ROLE_CATALOG` entry for `role`, as a shallow copy, or
    `None` for a name CAP-01 does not list.

    A copy for `profile()`'s reason: a caller that edits what it was handed
    must not be able to rewrite the catalog every later caller reads.
    """
    for entry in SEMANTIC_ROLE_CATALOG:
        if entry["role"] == role:
            return dict(entry)
    return None
