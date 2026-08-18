"""The identity kernel: durable opaque ids, a change-detection fingerprint,
and the revision record shape every later 14A object builds on.

`identity.py` is to object identity what `model.new_item_id()` and
`model.content_fingerprint()` are to an item: the single primitive every
later module mints and fingerprints through, so no caller invents a second id
shape or a second fingerprint job. This module is a peer of `model.py`, not
an extension of it: identity lives in the model tier, and this module
performs no file input or output and never imports a runtime-tier module
(`runtime.py`, `evidence.py`, or `journal.py`). It is pure functions over
bytes and dicts that a runtime-tier caller supplies.

Integrity note: `hashlib.sha256` is used here purely as a change-detection
checksum, never as a security boundary; this project has a single local user
and no attacker in its threat model.

`identity.object_fingerprint` and `model.content_fingerprint` are two
different fingerprints for two different jobs, and they are never unified:
`model.content_fingerprint` stays byte-exact over tested item fields so a
scoring-relevant change is never masked, while `identity.object_fingerprint`
tolerates a cosmetic reformat of a course, objective, source, or lesson
record. Mixing the two would let a cosmetic normalization mask a
scoring-relevant change, which D-14A-2 forbids by name.
"""
import hashlib
import re
import uuid
import datetime

IDENTITY_SCHEMA_VERSION = 1

OBJECT_KINDS = ("course", "objective", "source", "lesson", "bank", "component")

# `bank` and `lesson` are the only two 14A object kinds whose storage bytes
# can carry keyed assessment content: a bank's `CORRECT:` lines, a lesson's
# rubric text, or a `> [!KEY]` cloze answer. Stripping trailing whitespace
# there could mask a scoring-relevant change, which D-14A-2 forbids, so these
# two kinds are exempt from trailing-whitespace normalization. Line-ending
# normalization still applies to every kind, including these two: line
# endings are already established as not scoring-relevant in this repository
# (the CRLF byte-comparison defect in `runner.py` was fixed, not enshrined).
TRAILING_WS_EXEMPT_KINDS = ("bank", "lesson")

# Component ids are minted only for lesson blocks that are cited, gated, or
# evidence-bearing (D-14A-2); a component that is none of these has no
# reason to carry a durable id.
COMPONENT_ROLES = ("cited", "gated", "evidence_bearing")

RIGHTS_OPERATIONS = ("read", "quote", "transform", "remote_process",
                      "package", "export", "share")
RIGHTS_UNKNOWN = "unknown"

ACTOR_KINDS = ("human", "agent", "runtime")

COMPONENT_MARKER = "[CID:%s]"

# The eleven-key revision record shape, in fixed order. Every record this
# module returns is built with exactly these keys, in exactly this order, so
# `list(record.keys())` is itself an assertable contract.
REVISION_KEYS = ("object_id", "kind", "revision", "parent_revision",
                  "fingerprint", "timestamp", "origin", "profile_version",
                  "source_version", "generator_version", "rights")

_COMPONENT_ANCHOR_RE = re.compile(r"\[CID:([0-9a-f]{16})\]")


class IdentityError(Exception):
    """A typed identity-kernel failure: an unknown object kind or an
    ineligible component role. Machine-readable `code` plus message, the
    same two-argument shape `audit_writer.WriterError` already uses."""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message


def _unknown_kind_error(kind):
    return IdentityError(
        "identity.unknown_kind",
        "%s is not a known object kind; known kinds are: course, "
        "objective, source, lesson, bank, component" % kind)


def utc_now():
    """ISO-8601 UTC to millisecond precision with a `Z` suffix, the exact
    string shape `evidence.utc_now()` produces.

    `identity.py` cannot import `evidence` without crossing the model/runtime
    tier split, so the two formats agree by construction here and the
    agreement is asserted directly in `tests/identity_roundtrip.py` instead
    of by a shared import.
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:%S.") + "%03dZ" % (now.microsecond // 1000)


def new_object_id():
    """A durable opaque id, the same `uuid4().hex[:16]` shape
    `model.new_item_id()` already mints.

    An id is minted once and is never derived from content, a path, or a
    display name (D-14A-2): the same bytes minted twice produce two
    different ids, and two files with identical bytes are a copy candidate,
    never a merge.
    """
    return uuid.uuid4().hex[:16]


def new_component_id():
    """Same shape as `new_object_id()`; kept as a distinct name so a
    component id and an object id read differently at the call site even
    though the underlying shape is identical."""
    return uuid.uuid4().hex[:16]


def normalize_for_fingerprint(raw, kind):
    """Return a normalized copy of `raw` for change-detection hashing;
    never mutates `raw`, and never touches the bytes actually stored on
    disk.

    Line endings (`\\r\\n` and bare `\\r`) are normalized to `\\n` for every
    kind. Trailing whitespace is additionally stripped from every line for
    every kind except `bank` and `lesson`: those are the only two 14A object
    kinds whose storage bytes can carry keyed assessment content (a `CORRECT:`
    line, a rubric, a `> [!KEY]` cloze answer), so stripping there could mask
    a scoring-relevant change, which D-14A-2 forbids.
    """
    if kind not in OBJECT_KINDS:
        raise _unknown_kind_error(kind)
    text = raw.decode("utf-8", errors="surrogateescape")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if kind not in TRAILING_WS_EXEMPT_KINDS:
        text = "\n".join(line.rstrip() for line in text.split("\n"))
    return text.encode("utf-8", errors="surrogateescape")


def object_fingerprint(raw, kind):
    """The change-detection fingerprint of an object's normalized bytes.

    This is not, and must never become, a substitute for
    `model.content_fingerprint`, which stays byte-exact over tested item
    fields and never applies cosmetic normalization. The two fingerprints
    exist for two different jobs: this one detects that a course, objective,
    source, lesson, or bank record changed at all; `model.content_fingerprint`
    detects that what an item asks changed.

    No Unicode normalization (NFC or NFD) is ever applied: a name written
    with a precomposed accent and one written with a combining accent
    fingerprint differently, on purpose (FILE-03).
    """
    if kind not in OBJECT_KINDS:
        raise _unknown_kind_error(kind)
    normalized = normalize_for_fingerprint(raw, kind)
    return "sha256:" + hashlib.sha256(normalized).hexdigest()


def rights_default():
    """A fresh dict mapping every entry of `RIGHTS_OPERATIONS` to
    `RIGHTS_UNKNOWN`.

    An absent or empty rights record is identical to an all-unknown record:
    unknown is restrictive, never permissive (RIGHTS-01). The identity
    kernel never records a rights grant it was not given.
    """
    return {op: RIGHTS_UNKNOWN for op in RIGHTS_OPERATIONS}


def _effective_rights(rights):
    if not rights:
        return rights_default()
    return dict(rights)


def revision_record(object_id, kind, revision, parent_revision, fingerprint,
                     timestamp, origin, profile_version=None,
                     source_version=None, generator_version=None,
                     rights=None):
    """Build one revision record in `REVISION_KEYS` order.

    `origin` is a dict with exactly the three keys `actor_kind` (a member of
    `ACTOR_KINDS`), `actor_name` (a string, default `""`), and `operation`
    (a string). `origin` records who triggered the change without deciding
    who may accept it: the still-open self-acceptance decision (D-12.6-4) is
    not foreclosed by this format.
    """
    if kind not in OBJECT_KINDS:
        raise _unknown_kind_error(kind)
    return {
        "object_id": object_id,
        "kind": kind,
        "revision": revision,
        "parent_revision": parent_revision,
        "fingerprint": fingerprint,
        "timestamp": timestamp,
        "origin": origin,
        "profile_version": profile_version,
        "source_version": source_version,
        "generator_version": generator_version,
        "rights": _effective_rights(rights) if kind == "source" else rights,
    }


def _origin(actor_kind, actor_name, operation):
    return {"actor_kind": actor_kind, "actor_name": actor_name or "",
            "operation": operation}


def mint_object(kind, path, raw, actor_kind, actor_name, operation,
                rights=None, profile_version=None, source_version=None,
                generator_version=None):
    """Mint a fresh object: a new opaque id, revision 1, parent_revision
    None, and the fingerprint of `raw` for `kind`.

    `path` is accepted for the caller's convenience (it is where the bytes
    came from) but never contributes to the minted id or fingerprint: an id
    is never derived from a path (D-14A-2).

    Passing `raw=None` records `fingerprint=None` rather than an empty
    string, so a caller with no fingerprint to compare against can be told
    "no fingerprint" instead of being handed a falsely-empty one that a
    later compare-and-swap write could mistake for "matches anything".
    """
    if kind not in OBJECT_KINDS:
        raise _unknown_kind_error(kind)
    fingerprint = object_fingerprint(raw, kind) if raw is not None else None
    return revision_record(
        object_id=new_object_id(), kind=kind, revision=1,
        parent_revision=None, fingerprint=fingerprint, timestamp=utc_now(),
        origin=_origin(actor_kind, actor_name, operation),
        profile_version=profile_version, source_version=source_version,
        generator_version=generator_version, rights=rights)


def next_revision(prev, raw, actor_kind, actor_name, operation, rights=None):
    """Advance `prev` by one revision, keeping its `object_id` and `kind`.

    `revision` becomes `prev["revision"] + 1` and `parent_revision` becomes
    `prev["revision"]`, so a caller can walk a revision chain backward
    without a separate index.
    """
    kind = prev["kind"]
    fingerprint = object_fingerprint(raw, kind) if raw is not None else None
    return revision_record(
        object_id=prev["object_id"], kind=kind,
        revision=prev["revision"] + 1, parent_revision=prev["revision"],
        fingerprint=fingerprint, timestamp=utc_now(),
        origin=_origin(actor_kind, actor_name, operation),
        profile_version=prev.get("profile_version"),
        source_version=prev.get("source_version"),
        generator_version=prev.get("generator_version"),
        rights=rights if rights is not None else prev.get("rights"))


def mint_component(parent_object_id, role):
    """Mint a durable component id for one lesson block, only when `role`
    is a member of `COMPONENT_ROLES` (D-14A-2: component ids are minted only
    for cited, gated, or evidence-bearing blocks).

    `parent_object_id` is accepted for the caller's bookkeeping but, like
    `mint_object`'s `path`, never contributes to the minted id.
    """
    if role not in COMPONENT_ROLES:
        raise IdentityError(
            "identity.component_role_ineligible",
            "component ids are minted only for cited, gated, or "
            "evidence-bearing blocks; role %s is not one of them" % role)
    return new_component_id()


def component_anchor(component_id):
    """The literal marker text for `component_id`, joining the shipped
    `[ID:]`/`[HASH:]` marker family."""
    return COMPONENT_MARKER % component_id


def find_component_anchors(text):
    """Return `(component_id, offset)` pairs for every `[CID:...]` marker in
    `text`, in match order.

    This builds no document model: it locates one marker with one compiled
    regular expression, the same way `[ID:]` and `[HASH:]` are located as
    plain marker lines rather than parsed by a second content format.
    """
    return [(m.group(1), m.start()) for m in _COMPONENT_ANCHOR_RE.finditer(text)]


def registry_rows(records):
    """Return `records` sorted by `(kind, object_id)`, so two objects that
    compare equal on kind still come back in a stable, specified order
    across runs, regardless of the order the caller supplied them in."""
    return sorted(records, key=lambda r: (r["kind"], r["object_id"]))


RIGHTS_STATES = ("granted", "denied", "unknown")


def rights_state(record, operation):
    """The string state of `operation` on `record`, one of `RIGHTS_STATES`.

    Returns `RIGHTS_UNKNOWN` for an absent record (`None`), an empty record,
    an operation name outside the closed `RIGHTS_OPERATIONS` vocabulary, or a
    stored value outside `RIGHTS_STATES`. The comparison is exact lowercase
    ASCII string equality: no case folding, no trimming, no near match
    (RIGHTS-01). A source's rights authority is its owner or its license
    terms, never the local reader of the file; this function only reports
    what was recorded, and an unrecognized or missing record reads as
    unknown rather than as permission.
    """
    if not record:
        return RIGHTS_UNKNOWN
    if operation not in RIGHTS_OPERATIONS:
        return RIGHTS_UNKNOWN
    value = record.get(operation)
    if value not in RIGHTS_STATES:
        return RIGHTS_UNKNOWN
    return value


def rights_granted(record, operation):
    """True only when `rights_state(record, operation)` is exactly the
    string `"granted"`; unknown and denied both return False, and neither
    is treated as a lesser form of permission."""
    return rights_state(record, operation) == "granted"


def copy_candidates(records):
    """Return path-sorted pairs of records that share a fingerprint and
    differ in `object_id`: byte-identical content under two different ids is
    reported as a copy candidate, never merged and never given one id
    (ID-01 adjacency edge, ID-02)."""
    by_fingerprint = {}
    for rec in records:
        fp = rec.get("fingerprint")
        if fp is None:
            continue
        by_fingerprint.setdefault(fp, []).append(rec)
    pairs = []
    for fp, group in sorted(by_fingerprint.items()):
        ids = sorted(set(r["object_id"] for r in group))
        if len(ids) < 2:
            continue
        recs_by_id = {r["object_id"]: r for r in group}
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                pairs.append((recs_by_id[ids[i]], recs_by_id[ids[j]]))
    return pairs
