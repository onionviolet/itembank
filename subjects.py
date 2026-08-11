"""Subject-profile data policy (Phase 9, 09-CONTEXT D-01 through D-04).

This module is deliberately surface-free: it owns profile validation,
selection, the conservative fallback, and the stored-snapshot helper, and it
imports no surface. It is the only place a subject id becomes a profile.

The invariants it enforces:

- Profiles are versioned data -- id, version, lesson capabilities
  (markdown/tables/math/runnable_languages), allowed item types, and a named
  verifier -- never Python subclasses (D-01, D-02).
- An explicit known id wins; one unambiguous namespaced subject selects its
  entry; no usable subject selects a copy of the conservative default (D-03);
  several subject namespaces refuse unless an explicit id is given (D-04).
- A selected profile rejects item types outside its allowlist before any
  session exists, and reports every requested unavailable capability by name.
- Subject extraction always goes through `evidence.subject_of()` -- the one
  namespaced-objective extractor -- never a local string split (D-04).

The shipped known subjects live in a temporary constant here until plan 09-02
moves them into validated settings data (`subject_profiles`); the conservative
default remains code-owned forever (D-03).
"""
import copy

import evidence

PROFILE_SCHEMA_VERSION = 1


class SubjectProfileError(Exception):
    """A registry, bank, or explicit request cannot be resolved to one valid
    subject profile. The message names subject/profile/capability identifiers
    but never an absolute bank path (T-09-03)."""


# The one conservative fallback (D-03): plain markdown, the established
# non-check item types, the shared runtime scorer, no math, no runnable
# language. Code-owned; never replaced by settings data.
DEFAULT_PROFILE = {
    "id": "default",
    "version": PROFILE_SCHEMA_VERSION,
    "lesson": {"markdown": True, "tables": True, "math": False,
               "runnable_languages": []},
    "allowed_item_types": ["mc", "multi", "table", "dnd", "build", "short"],
    "verifier": "runtime",
}

# Known verifier identifiers (D-01). The shared runtime scorer exists today;
# Phase 5's `check` verifier joins before plan 09-02 ships the CS entry.
KNOWN_VERIFIERS = ("runtime",)

_PROFILE_KEYS = frozenset(
    ["id", "version", "lesson", "allowed_item_types", "verifier"])
_LESSON_KEYS = frozenset(
    ["markdown", "tables", "math", "runnable_languages"])


def _fail(msg):
    raise SubjectProfileError(msg)


def _require(condition, msg):
    if not condition:
        _fail(msg)


def _validate_profile(profile):
    """Closed-shape validation of one profile dict (T-09-01/T-09-06)."""
    _require(isinstance(profile, dict),
             "each subject profile must be an object")
    extra = set(profile) - _PROFILE_KEYS
    _require(not extra,
             "profile carries unknown keys: %s" % ", ".join(sorted(extra)))
    missing = _PROFILE_KEYS - set(profile)
    _require(not missing,
             "profile is missing required keys: %s" % ", ".join(sorted(missing)))
    pid = profile["id"]
    _require(isinstance(pid, str) and pid,
             "profile id must be a non-empty string")
    _require(isinstance(profile["version"], int) and profile["version"] >= 1,
             "profile %r version must be a positive integer" % pid)
    lesson = profile["lesson"]
    _require(isinstance(lesson, dict),
             "profile %r lesson must be an object" % pid)
    extra = set(lesson) - _LESSON_KEYS
    _require(not extra,
             "profile %r lesson carries unknown keys: %s"
             % (pid, ", ".join(sorted(extra))))
    missing = _LESSON_KEYS - set(lesson)
    _require(not missing,
             "profile %r lesson is missing required keys: %s"
             % (pid, ", ".join(sorted(missing))))
    for key in ("markdown", "tables", "math"):
        _require(isinstance(lesson[key], bool),
                 "profile %r lesson.%s must be a boolean" % (pid, key))
    langs = lesson["runnable_languages"]
    _require(isinstance(langs, list) and
             all(isinstance(x, str) for x in langs),
             "profile %r lesson.runnable_languages must be a string array"
             % pid)
    _require(len(set(langs)) == len(langs),
             "profile %r lesson.runnable_languages contains duplicates" % pid)
    types = profile["allowed_item_types"]
    _require(isinstance(types, list) and
             all(isinstance(x, str) for x in types),
             "profile %r allowed_item_types must be a string array" % pid)
    _require(len(set(types)) == len(types),
             "profile %r allowed_item_types contains duplicates" % pid)
    _require(profile["verifier"] in KNOWN_VERIFIERS,
             "profile %r uses unknown verifier %r; known verifiers: %s"
             % (pid, profile["verifier"], ", ".join(KNOWN_VERIFIERS)))
    return profile


def _registry_entries(registry):
    """The profile list of a validated registry, from either the object form
    (id -> profile) or the list form (profile dicts each carrying `id`)."""
    entries = registry["entries"]
    if isinstance(entries, dict):
        return list(entries.values())
    return list(entries)


def _entry_by_id(registry, sid):
    for entry in _registry_entries(registry):
        if entry.get("id") == sid:
            return entry
    return None


def validate_registry(registry):
    """Closed-shape validation of a versioned registry: `version` plus
    `entries` (an id->profile object or a list of profile dicts). Rejects
    duplicate ids, missing/extra keys, invalid capability value types,
    duplicate allowed types/languages, and unknown verifier identifiers with
    `SubjectProfileError` (T-09-01, T-09-06). Returns the registry unchanged
    when valid."""
    _require(isinstance(registry, dict),
             "subject registry must be an object")
    _require("version" in registry and "entries" in registry,
             "subject registry must carry 'version' and 'entries'")
    _require(isinstance(registry["version"], int)
             and registry["version"] >= 1,
             "subject registry version must be a positive integer")
    entries = registry["entries"]
    _require(isinstance(entries, (dict, list)),
             "subject registry 'entries' must be an object or a list")
    profiles = _registry_entries(registry)
    ids = [p.get("id") for p in profiles if isinstance(p, dict)]
    _require(len(ids) == len(profiles) and len(set(ids)) == len(ids),
             "subject registry contains duplicate or id-less profile entries")
    for profile in profiles:
        _validate_profile(profile)
    return registry


def subject_ids(qs):
    """The distinct subject namespaces across the bank, in first-seen order,
    via the one extractor `evidence.subject_of()` (D-04). An unnamespaced or
    empty objective yields no id; nothing here splits strings locally."""
    seen = []
    for q in qs:
        sid = evidence.subject_of(q.get("objective") or "")
        if sid and sid not in seen:
            seen.append(sid)
    return seen


def _capability_supported(profile, capability):
    """Whether a requested capability token is supported by a profile. Tokens
    are `math`, `runnable_languages`, or `runnable_languages:<language>`; an
    unknown token is honestly unsupported rather than guessed."""
    lesson = profile["lesson"]
    if capability == "math":
        return lesson.get("math") is True
    if capability == "runnable_languages":
        return bool(lesson.get("runnable_languages"))
    if isinstance(capability, str) and \
            capability.startswith("runnable_languages:"):
        return capability.split(":", 1)[1] in lesson.get("runnable_languages", [])
    return False


def select_profile(qs, registry, explicit_id=None, requested_capabilities=()):
    """Resolve exactly one profile for a bank and return a JSON-native
    snapshot. Selection order (D-03/D-04): an explicit known id wins; one
    unique namespaced subject selects its registry entry; no usable subject
    selects a copy of `DEFAULT_PROFILE`; several subject ids raise
    `SubjectProfileError`. A profile that does not allow every item type in
    the bank also raises before any session can be written. The snapshot
    carries the registry/profile versions, the selected subject id ("" for
    the conservative default), the full resolved profile, and the list of
    requested capabilities the profile does not support."""
    validate_registry(registry)
    ids = subject_ids(qs)

    if explicit_id is not None:
        profile = _entry_by_id(registry, explicit_id)
        if profile is None:
            known = ", ".join(sorted(e.get("id", "")
                                     for e in _registry_entries(registry)))
            _fail("unknown explicit profile id %r; known profile ids: %s"
                  % (explicit_id, known or "(none)"))
        subject_id = explicit_id
    elif len(ids) == 0:
        profile, subject_id = DEFAULT_PROFILE, ""
    elif len(ids) == 1:
        entry = _entry_by_id(registry, ids[0])
        if entry is None:
            profile, subject_id = DEFAULT_PROFILE, ""
        else:
            profile, subject_id = entry, ids[0]
    else:
        _fail("bank mixes multiple subject namespaces (%s); pass an explicit "
              "profile id instead of guessing"
              % ", ".join(ids))

    for q in qs:
        if q.get("type") not in profile["allowed_item_types"]:
            _fail("profile %r does not allow item type %r"
                  % (profile["id"], q.get("type")))

    unsupported = [cap for cap in requested_capabilities
                   if not _capability_supported(profile, cap)]
    return {
        "registry_version": registry["version"],
        "profile_version": profile["version"],
        "subject_id": subject_id,
        "profile": copy.deepcopy(profile),
        "unsupported_capabilities": unsupported,
    }


def session_profile(data):
    """The persisted profile snapshot for a session dict, or None when the
    session predates Phase 9 and its null slot has not been filled yet. After
    start (or after the first action on a legacy session) this returns only
    the stored snapshot -- never a re-resolution of the bank or settings
    (D-04)."""
    return data.get("subject_profile")


# Temporary shipped registry until plan 09-02 moves the known subjects into
# the validated `subject_profiles` settings group. Only the conservative
# default above remains code-owned after that plan.
REGISTRY = {
    "version": 1,
    "entries": {
        "emt": {
            "id": "emt",
            "version": PROFILE_SCHEMA_VERSION,
            "lesson": {"markdown": True, "tables": True, "math": False,
                       "runnable_languages": []},
            "allowed_item_types": ["mc", "multi", "table", "dnd", "build",
                                   "short"],
            "verifier": "runtime",
        },
    },
}
