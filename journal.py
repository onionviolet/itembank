"""The operation journal: the durable, append-only record of every write to
a 14A object, and the one compare-and-swap write path every later caller
mutates through.

`journal.py` is to a durable object what `runtime.score_response` is to
scoring: the single primitive every surface calls, so no surface reimplements
its own compare-and-swap guard or its own atomic commit. The log
(`journal.jsonl`) is the only authority; `objects.json` is a disposable
materialized view over it, never a second source of truth, and deleting it
and calling `rebuild_registry` regenerates a byte-identical file from the log
alone. The journal is not a cache: it is durable local record, and it must be
included in any backup story a later phase builds around this repository's
data.

The reader treats every line as untrusted input, the same posture
`evidence.py` documents: a malformed line or an unrecognized operation is
skipped and reported, never fatal, because a torn line at the tail of a
growing log is an expected failure mode.

This module is a peer of `runtime.py` and `evidence.py`, not an extension of
either. It calls `identity.py` for id minting, fingerprinting, and the
revision record shape, and it never imports `model.py` directly.

A state flip (`prepared` becoming `applied` or `refused`) is recorded as a
second, appended entry naming the first one through `resolves_entry`, never
as a rewrite of the first entry's line: the journal is append-only end to
end. The append itself happens inside the already-held journal lock
(`_journal_lock`), so the whole fingerprint check, the mutation, and both
journal appends are one critical section. Because the append is always made
under that held lock, the Windows `O_APPEND` non-atomicity hazard
`evidence.py` documents (two concurrent appenders racing `lseek` plus
`write`) does not apply here: there is never more than one appender active at
a time.

Integrity note: `hashlib.sha256` is used here purely as a change-detection
and content-addressing checksum, never as a security boundary; this project
has a single local user and no attacker in its threat model.

Walking-skeleton usage: a caller mints an object with
`identity.mint_object(...)`, commits its bytes with exactly one call to
`journal.commit_operation(base, object_id, kind, rel_path, "mint", raw,
expected_fingerprint=None, actor_kind=..., actor_name=...,
create_if_missing=True)`, and reads the recorded revision back with
`journal.read_registry(base)[object_id]`. `tests/journal_roundtrip.py`'s
`check_walking_skeleton_slice()` runs exactly this three-call sequence, and
Phase 13.9 may stub course-level storage over it.
"""
import contextlib
import difflib
import hashlib
import json
import os
import sys
import time
import uuid

import discovery
import identity

JOURNAL_SCHEMA_VERSION = 1
JOURNAL_DIRNAME = "_journal"
LOG_FILENAME = "journal.jsonl"
REGISTRY_FILENAME = "objects.json"
LOCK_FILENAME = "journal.lock"
BEFORE_DIRNAME = "before"
LOCK_TIMEOUT_SECONDS = 10.0

ENTRY_STATES = ("prepared", "applied", "refused")
OBJECT_STATES = ("clean", "conflict", "interrupted", "missing", "unavailable")

# The six operation vocabulary members plan 14A-03 gives distinct provenance
# and identity effects to. This plan validates membership only.
OPERATION_TYPES = ("link", "import", "copy", "move", "edit_in_place",
                    "supersede")

# The full set of `operation` values a journal entry may carry: the six
# operation types above, plus the four this plan's own machinery writes
# ("mint" for a brand-new object, "restore" for an undo, "external_edit" for
# a detected out-of-band change, and "reconcile" for a recorded human
# decision that clears a conflict). None of these four are added to
# OPERATION_TYPES, which stays exactly the six FILE-03 names so a caller can
# test membership against the frozen vocabulary.
RECORD_TYPES = OPERATION_TYPES + ("mint", "restore", "external_edit",
                                  "reconcile")

# The journal entry key order, fixed. Every entry this module writes carries
# exactly this key set, in exactly this order, so `list(entry.keys())` is
# itself an assertable contract the same way `identity.REVISION_KEYS` is.
ENTRY_KEYS = (
    "schema_version", "entry_id", "timestamp", "operation", "state",
    "resolves_entry", "object_id", "kind", "revision", "parent_revision",
    "path", "expected_fingerprint", "before_fingerprint", "after_fingerprint",
    "before_image", "undo", "source_object_id", "source_revision",
    "restores_revision", "origin", "code", "message", "rights",
)

# The per-object registry projection key order. Deliberately a superset of
# `identity.REVISION_KEYS` plus `path`, `last_entry_id`, `supersedes`, and
# `superseded_by`: `supersedes`/`superseded_by` are 14A-03's supersede
# relationship, filled in by `_compute_registry`'s second pass over the
# journal's `supersede` entries, never by deleting or rewriting either row.
REGISTRY_OBJECT_KEYS = (
    "object_id", "kind", "path", "revision", "parent_revision", "fingerprint",
    "timestamp", "origin", "profile_version", "source_version",
    "generator_version", "rights", "last_entry_id", "supersedes",
    "superseded_by",
)


class JournalError(Exception):
    """A typed journal failure: a stale preflight, a conflict, a busy lock,
    an unreachable root. Machine-readable `code` plus `message`, the same
    two-argument shape `identity.IdentityError` and `audit_writer.WriterError`
    already use."""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message


def journal_dir(base):
    """The `_journal/` directory beside `base`, exactly mirroring
    `evidence.evidence_dir(base)`."""
    return os.path.join(os.path.abspath(base), JOURNAL_DIRNAME)


def log_path(base):
    return os.path.join(journal_dir(base), LOG_FILENAME)


def registry_path(base):
    return os.path.join(journal_dir(base), REGISTRY_FILENAME)


def _before_dir(base):
    return os.path.join(journal_dir(base), BEFORE_DIRNAME)


def new_entry_id():
    """The full 32-character `uuid4().hex` shape `evidence.new_event_id()`
    already mints; a log entry id, distinct from the 16-character object id
    shape `identity.new_object_id()` mints."""
    return uuid.uuid4().hex


def _origin(actor_kind, actor_name, operation):
    return {"actor_kind": actor_kind, "actor_name": actor_name or "",
            "operation": operation}


@contextlib.contextmanager
def _journal_lock(base):
    """The single advisory lock per journal root, copying
    `audit_writer._bank_lock`'s shape exactly: non-blocking acquire in a
    loop with a bounded deadline, an explicit busy refusal, release in a
    `finally`. One lock serializes the fingerprint check, the mutation, and
    both journal appends for every object under this root."""
    jdir = journal_dir(base)
    os.makedirs(jdir, exist_ok=True)
    lock_path = os.path.join(jdir, LOCK_FILENAME)
    fh = open(lock_path, "a+b")
    try:
        if fh.tell() == 0:
            fh.write(b"\n")
            fh.flush()
        deadline = time.monotonic() + LOCK_TIMEOUT_SECONDS
        while True:
            if _try_lock(fh):
                break
            if time.monotonic() >= deadline:
                raise JournalError(
                    "journal.busy",
                    "another writer holds the journal lock for %s; retry "
                    "after the running operation finishes" % lock_path)
            time.sleep(0.05)
        yield lock_path
    finally:
        try:
            _unlock(fh)
        finally:
            fh.close()


def _try_lock(fh):
    if os.name == "nt":
        import msvcrt
        try:
            msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
            return True
        except OSError:
            return False
    import fcntl
    try:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        return True
    except OSError:
        return False


def _unlock(fh):
    if os.name == "nt":
        import msvcrt
        try:
            fh.seek(0)
            msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)
        except OSError:
            pass
        return
    import fcntl
    fcntl.flock(fh.fileno(), fcntl.LOCK_UN)


def _write_bytes_atomic(path, raw):
    """The one atomic-write seam every mutation site in this module calls
    through: same-directory temp file, flush, fsync, `os.replace`. This is
    the single place a fault-injection test needs to patch to exercise every
    durable write this module makes (the before-image, the target, and the
    registry projection all go through this one function)."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "wb") as fh:
        fh.write(raw)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def append_entry(base, entry):
    """Append one journal entry, in `ENTRY_KEYS` order, with a single
    `write` followed by `flush` and `os.fsync`.

    The caller must already hold `_journal_lock(base)`; this function takes
    no lock of its own. `schema_version`, `entry_id`, and `timestamp` are
    filled in when absent. Returns the fully-populated entry dict so the
    caller can read back the minted `entry_id` and `timestamp`.
    """
    operation = entry.get("operation")
    if operation not in RECORD_TYPES:
        raise JournalError(
            "journal.unknown_operation",
            "%s is not a known journal record type; known types are: %s"
            % (operation, ", ".join(RECORD_TYPES)))
    entry = dict(entry)
    # `dict.setdefault` would not fire here: every entry this module builds
    # already carries these three keys with an explicit `None` (or a real
    # value for `schema_version`), so a plain setdefault would never
    # overwrite them. Fill on None instead of on absence.
    if entry.get("schema_version") is None:
        entry["schema_version"] = JOURNAL_SCHEMA_VERSION
    if entry.get("entry_id") is None:
        entry["entry_id"] = new_entry_id()
    if entry.get("timestamp") is None:
        entry["timestamp"] = identity.utc_now()
    ordered = {key: entry.get(key) for key in ENTRY_KEYS}
    line = json.dumps(ordered, ensure_ascii=False, sort_keys=False)
    path = log_path(base)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")
        fh.flush()
        os.fsync(fh.fileno())
    return ordered


def entries(base):
    """Yield journal entries from `journal.jsonl` in append order, never
    sorted.

    A malformed line or a line whose `operation` is not a member of
    `RECORD_TYPES` is skipped and reported to stderr by exact line number,
    following `evidence.events()`'s degrade-not-crash discipline for an
    untrusted log tail; it never raises.
    """
    path = log_path(base)
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for lineno, raw in enumerate(fh, start=1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                obj = json.loads(raw)
            except ValueError as exc:
                print("warning  journal line %d skipped: %s" % (lineno, exc),
                      file=sys.stderr)
                continue
            if not isinstance(obj, dict) or \
                    obj.get("operation") not in RECORD_TYPES:
                print("warning  journal line %d skipped: %s"
                      % (lineno, "unrecognized operation %r"
                         % (obj.get("operation") if isinstance(obj, dict)
                            else obj)), file=sys.stderr)
                continue
            yield obj


def _new_template(operation, object_id, kind, rel_path, actor_kind,
                   actor_name, source_object_id, source_revision,
                   restores_revision, rights=None):
    return {
        "schema_version": JOURNAL_SCHEMA_VERSION,
        "entry_id": None,
        "timestamp": None,
        "operation": operation,
        "state": None,
        "resolves_entry": None,
        "object_id": object_id,
        "kind": kind,
        "revision": None,
        "parent_revision": None,
        "path": rel_path,
        "expected_fingerprint": None,
        "before_fingerprint": None,
        "after_fingerprint": None,
        "before_image": None,
        "undo": {"kind": "none", "before_image": None, "target": None,
                 "restores_revision": None},
        "source_object_id": source_object_id,
        "source_revision": source_revision,
        "restores_revision": restores_revision,
        "origin": _origin(actor_kind, actor_name, operation),
        "code": None,
        "message": None,
        "rights": rights,
    }


def commit_operation(base, object_id, kind, rel_path, operation, new_bytes,
                      expected_fingerprint, actor_kind, actor_name,
                      create_if_missing=False, source_object_id=None,
                      source_revision=None, write_target=True, note=None,
                      rights=None):
    """The one compare-and-swap write path every durable object kind goes
    through. See the module docstring's Walking-skeleton usage paragraph for
    the minimal three-call sequence. Raises `JournalError` on refusal;
    returns the new revision record on success.

    `write_target=False` (used by `op_link` and `op_supersede`) records a
    revision without writing `new_bytes` to the target at all, so the
    target's `mtime_ns` is left untouched; `note`, when given, rides in the
    entry's `message` field as a plain-text annotation (used by `op_move` to
    record the previous path); `rights`, meaningful only for `kind ==
    "source"`, is stored on the entry and defaults to
    `identity.rights_default()` when omitted, matching
    `identity.mint_object`'s own default.
    """
    return _commit_impl(
        base, object_id, kind, rel_path, operation, new_bytes,
        expected_fingerprint, actor_kind, actor_name,
        create_if_missing=create_if_missing,
        source_object_id=source_object_id, source_revision=source_revision,
        restores_revision=None, write_target=write_target, note=note,
        rights=rights)


def _commit_impl(base, object_id, kind, rel_path, operation, new_bytes,
                  expected_fingerprint, actor_kind, actor_name,
                  create_if_missing, source_object_id, source_revision,
                  restores_revision, write_target=True, note=None,
                  rights=None):
    if operation not in RECORD_TYPES:
        raise JournalError(
            "journal.unknown_operation",
            "%s is not a known journal record type; known types are: %s"
            % (operation, ", ".join(RECORD_TYPES)))
    if not os.path.isdir(os.path.abspath(base)):
        raise JournalError(
            "journal.root_unavailable",
            "approved root %s is not reachable; the last recorded index is "
            "still readable and nothing was written" % base)

    target_path = os.path.join(os.path.abspath(base), rel_path)
    # T-14A-02-04/05: a caller-supplied rel_path that walks upward (e.g.
    # "../../etc/passwd") or a symlinked target that resolves outside base
    # must never be trusted blind. Judged by where the path actually
    # resolves to, after link resolution, the same containment check
    # discovery.inside_any_root already gives every read-only walk. This is
    # a preflight validation reached before the lock, like the operation
    # and root checks above it, so it is never journaled (a busy refusal
    # never acquired the lock either, for the same reason).
    if not discovery.inside_any_root(target_path, [base]):
        raise JournalError(
            "journal.path_outside_root",
            "%s resolves outside the approved root %s; the write is "
            "refused rather than followed" % (rel_path, base))

    with _journal_lock(base):
        exists = os.path.exists(target_path)
        before_raw = None
        if exists:
            with open(target_path, "rb") as fh:
                before_raw = fh.read()
        before_fingerprint = identity.object_fingerprint(before_raw, kind) \
            if before_raw is not None else None
        # A link or supersede records no content change: the after
        # fingerprint is the observed on-disk (or absent) fingerprint, never
        # a fingerprint of bytes that were never written.
        after_fingerprint = before_fingerprint if not write_target else \
            identity.object_fingerprint(new_bytes, kind)

        registry = _compute_registry(base)
        prev = registry.get(object_id)
        registry_fingerprint = prev["fingerprint"] if prev is not None \
            else None
        # `op_move` commits to a NEW rel_path that, by definition, does not
        # yet hold the object's bytes: `before_fingerprint` (read from
        # target_path above) is therefore not a meaningful stand-in for
        # "the object's currently accepted state" the way it is for every
        # other operation, which always targets the object's own recorded
        # path. Compare against the registry's own fingerprint instead
        # whenever the commit's rel_path differs from the object's last
        # recorded path.
        moving_to_new_path = prev is not None and prev.get("path") != rel_path
        compare_fingerprint = registry_fingerprint if moving_to_new_path \
            else before_fingerprint

        effective_rights = rights
        if kind == "source" and not effective_rights:
            effective_rights = identity.rights_default()

        template = _new_template(
            operation, object_id, kind, rel_path, actor_kind, actor_name,
            source_object_id, source_revision, restores_revision,
            rights=effective_rights)
        template["expected_fingerprint"] = expected_fingerprint
        template["before_fingerprint"] = before_fingerprint
        template["after_fingerprint"] = after_fingerprint
        if note is not None:
            template["message"] = note

        # RIGHTS-01: import and copy pull a source's bytes into a new owned
        # artifact and require the source's transform right to be exactly
        # "granted"; link, move, edit_in_place, and supersede act on objects
        # the course already owns or merely bind where they live, so no
        # source transform grant is required. The rights value is read from
        # the registry inside this held lock, at the moment of the
        # operation, and is never carried across a lock boundary.
        if operation in ("import", "copy") and source_object_id is not None:
            source_row = registry.get(source_object_id)
            source_rights = source_row.get("rights") if source_row else None
            if not identity.rights_granted(source_rights, "transform"):
                state = identity.rights_state(source_rights, "transform")
                _refuse(base, template, "journal.rights_unknown",
                        "the transform right for source %s is %s, so %s "
                        "is refused by name. Next safe action: record a "
                        "rights grant for this source, or link the file "
                        "where it lives instead of importing it."
                        % (source_object_id, state, operation))
            template["source_revision"] = source_row["revision"] \
                if source_row else None

        # ID-02: same id, divergent bytes is a conflict, and a conflict is
        # never cleared by a lucky argument. This check runs unconditionally,
        # before `expected_fingerprint` is ever consulted, so passing the
        # current on-disk fingerprint as the expected base cannot bypass it;
        # only `reconcile()` (recorded human decision) clears it.
        if prev is not None and registry_fingerprint != compare_fingerprint:
            _refuse(base, template, "journal.conflict",
                    "object %s has the same id and divergent bytes: on "
                    "disk %s, last accepted revision %d recorded %s. "
                    "This is a conflict, not an overwrite. Next safe "
                    "action: read the object, reconcile the difference "
                    "by hand, then re-run the operation with the "
                    "on-disk fingerprint as the expected base."
                    % (object_id, compare_fingerprint,
                       prev["revision"] if prev is not None else 0,
                       registry_fingerprint))

        if prev is not None and expected_fingerprint is None:
            _refuse(base, template, "journal.missing_fingerprint",
                    "object %s carries no fingerprint, so a compare-and-swap "
                    "write cannot be checked; the write is refused rather "
                    "than performed blind" % object_id)

        if expected_fingerprint is not None and \
                expected_fingerprint != compare_fingerprint:
            _refuse(base, template, "journal.stale_preflight",
                    "current fingerprint %s does not match the expected "
                    "base fingerprint %s; the object changed since this "
                    "operation was prepared"
                    % (compare_fingerprint, expected_fingerprint))

        if write_target and after_fingerprint == before_fingerprint:
            _refuse(base, template, "journal.no_change",
                    "the new bytes for %s are identical to the current "
                    "bytes; no revision was recorded" % object_id)

        revision = 1 if prev is None else prev["revision"] + 1
        parent_revision = None if prev is None else prev["revision"]

        before_image = None
        if write_target and exists:
            digest = hashlib.sha256(before_raw).hexdigest()
            before_image = "/".join((BEFORE_DIRNAME, digest + ".bin"))
            _write_bytes_atomic(
                os.path.join(_before_dir(base), digest + ".bin"), before_raw)

        template["revision"] = revision
        template["parent_revision"] = parent_revision
        template["before_image"] = before_image
        template["undo"] = {
            "kind": "restore_before_image" if before_image else "none",
            "before_image": before_image,
            "target": rel_path,
            "restores_revision": restores_revision,
        }

        prepared = dict(template)
        prepared["state"] = "prepared"
        prepared = append_entry(base, prepared)

        if write_target:
            _write_bytes_atomic(target_path, new_bytes)

            with open(target_path, "rb") as fh:
                committed_raw = fh.read()
            committed_fingerprint = identity.object_fingerprint(
                committed_raw, kind)
            if committed_fingerprint != after_fingerprint:
                refused = dict(template)
                refused["state"] = "refused"
                refused["resolves_entry"] = prepared["entry_id"]
                refused["code"] = "journal.after_guard_failed"
                refused["message"] = (
                    "the committed bytes of %s fingerprint as %s but the "
                    "operation expected %s; the journal entry stays "
                    "prepared and the previous revision is still the last "
                    "accepted one"
                    % (object_id, committed_fingerprint, after_fingerprint))
                append_entry(base, refused)
                raise JournalError(refused["code"], refused["message"])

        applied = dict(template)
        applied["state"] = "applied"
        applied["resolves_entry"] = prepared["entry_id"]
        applied = append_entry(base, applied)

        rebuild_registry(base)

        return identity.revision_record(
            object_id=object_id, kind=kind, revision=revision,
            parent_revision=parent_revision, fingerprint=after_fingerprint,
            timestamp=applied["timestamp"],
            origin=_origin(actor_kind, actor_name, operation),
            rights=effective_rights)


def _refuse(base, template, code, message):
    """Append one `refused` entry (the caller already holds the lock) and
    raise `JournalError(code, message)`. Every refusal reached inside the
    lock is journaled this way; `journal.busy` never reaches this function
    because it is refused before the lock is ever acquired."""
    entry = dict(template)
    entry["state"] = "refused"
    entry["code"] = code
    entry["message"] = message
    append_entry(base, entry)
    raise JournalError(code, message)


def _compute_registry(base):
    """Fold `entries(base)` into `{object_id: registry_entry}`, purely from
    `applied` resolution entries, in append order (a later applied entry for
    the same object overwrites an earlier one). This is the single
    computation both `rebuild_registry` and `commit_operation`'s own
    registry update run, so the live-maintained projection and a from-scratch
    rebuild are, by construction, the same function applied to the same
    log.

    A second pass folds in `supersede` entries: the superseding object's row
    gains `supersedes`, and the superseded object's row (found by
    `object_id`, its own last applied row is otherwise untouched) gains
    `superseded_by`. Neither row is ever removed by this function.
    """
    objects = {}
    supersedes_by_id = {}
    superseded_by_id = {}
    for entry in entries(base):
        if entry.get("state") != "applied":
            continue
        object_id = entry.get("object_id")
        if not object_id:
            continue
        objects[object_id] = {
            "object_id": object_id,
            "kind": entry.get("kind"),
            "path": entry.get("path"),
            "revision": entry.get("revision"),
            "parent_revision": entry.get("parent_revision"),
            "fingerprint": entry.get("after_fingerprint"),
            "timestamp": entry.get("timestamp"),
            "origin": entry.get("origin"),
            "profile_version": None,
            "source_version": None,
            "generator_version": None,
            "rights": entry.get("rights"),
            "last_entry_id": entry.get("entry_id"),
            "supersedes": None,
            "superseded_by": None,
        }
        if entry.get("operation") == "supersede":
            superseded_id = entry.get("source_object_id")
            if superseded_id:
                supersedes_by_id[object_id] = superseded_id
                superseded_by_id[superseded_id] = object_id
    for superseding_id, superseded_id in supersedes_by_id.items():
        if superseding_id in objects:
            objects[superseding_id]["supersedes"] = superseded_id
    for superseded_id, superseding_id in superseded_by_id.items():
        if superseded_id in objects:
            objects[superseded_id]["superseded_by"] = superseding_id
    return objects


def _write_registry(base, objects):
    data = {
        "schema_version": JOURNAL_SCHEMA_VERSION,
        "objects": {
            object_id: {key: objects[object_id][key]
                        for key in REGISTRY_OBJECT_KEYS}
            for object_id in sorted(objects)
        },
    }
    raw = (json.dumps(data, ensure_ascii=False, indent=2, sort_keys=False)
           + "\n").encode("utf-8")
    _write_bytes_atomic(registry_path(base), raw)


def rebuild_registry(base):
    """Regenerate `objects.json` from `journal.jsonl` alone. Deleting the
    registry and calling this function reproduces a byte-identical file,
    because this is the exact function `commit_operation` calls to update
    the registry after every successful write; there is no second code
    path."""
    objects = _compute_registry(base)
    _write_registry(base, objects)
    return objects


def read_registry(base):
    """The current registry projection, read from `objects.json`. Returns an
    empty dict when no registry has been written yet, never raises for a
    missing file."""
    path = registry_path(base)
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return data.get("objects", {})


def _unresolved_prepared_for(base, object_id):
    """The most recent `prepared` entry for `object_id` that has no matching
    `applied` or `refused` resolution entry, or None. Used by
    `object_state` to distinguish an interrupted commit (the disk still
    carries the pre-mutation bytes) from an ordinary clean or conflicting
    object."""
    resolved_ids = set()
    prepared_by_id = {}
    for entry in entries(base):
        if entry.get("object_id") != object_id:
            continue
        if entry.get("state") == "prepared":
            prepared_by_id[entry["entry_id"]] = entry
        resolves = entry.get("resolves_entry")
        if resolves:
            resolved_ids.add(resolves)
    for entry_id, entry in prepared_by_id.items():
        if entry_id not in resolved_ids:
            return entry
    return None


def object_state(base, object_id):
    """One of `OBJECT_STATES` for `object_id`: `unavailable` when the
    approved root itself is unreachable; `interrupted` when an unresolved
    `prepared` entry exists and the disk still carries its pre-mutation
    bytes; `missing` when the object is unknown or its target file does not
    exist; `clean` when the disk's fingerprint matches the registry's
    recorded fingerprint; `conflict` otherwise."""
    if not os.path.isdir(os.path.abspath(base)):
        return "unavailable"

    unresolved = _unresolved_prepared_for(base, object_id)
    if unresolved is not None:
        target_path = os.path.join(os.path.abspath(base), unresolved["path"])
        raw = None
        if os.path.exists(target_path):
            with open(target_path, "rb") as fh:
                raw = fh.read()
        fingerprint = identity.object_fingerprint(raw, unresolved["kind"]) \
            if raw is not None else None
        if fingerprint == unresolved["before_fingerprint"]:
            return "interrupted"

    registry = read_registry(base)
    obj = registry.get(object_id)
    if obj is None:
        return "missing"
    target_path = os.path.join(os.path.abspath(base), obj["path"])
    if not os.path.exists(target_path):
        return "missing"
    with open(target_path, "rb") as fh:
        raw = fh.read()
    fingerprint = identity.object_fingerprint(raw, obj["kind"])
    if fingerprint == obj["fingerprint"]:
        return "clean"
    return "conflict"


def _known_object_ids(ordered_entries):
    ids = set()
    for entry in ordered_entries:
        object_id = entry.get("object_id")
        if object_id:
            ids.add(object_id)
    return ids


def replay(base):
    """Walk the journal in append order and report, honestly, which valid
    state survived every unresolved `prepared` entry.

    Trusting a `prepared` entry's own `state` field without re-reading the
    target would misreport a committed write as failed (14A-RESEARCH.md's
    Pitfall 1): a crash between the atomic replace and the `applied` append
    leaves a `prepared` entry on disk even though the new bytes already
    landed. This function instead re-reads the target's actual current
    fingerprint for every unresolved `prepared` entry: equal to
    `after_fingerprint` means the commit landed and the entry is
    `recoverable`; equal to `before_fingerprint` means the commit did not
    land and the entry is `interrupted`; equal to neither means the object
    is genuinely in conflict, surfaced through `objects` via `object_state`
    rather than a third list here. This function only reads; it never
    mutates the target or the log, so calling it twice is idempotent.
    """
    ordered = list(entries(base))
    resolved_ids = set()
    refused = []
    for entry in ordered:
        resolves = entry.get("resolves_entry")
        if resolves:
            resolved_ids.add(resolves)
        if entry.get("state") == "refused":
            refused.append(entry)

    interrupted = []
    recoverable = []
    for entry in ordered:
        if entry.get("state") != "prepared":
            continue
        if entry["entry_id"] in resolved_ids:
            continue
        target_path = os.path.join(os.path.abspath(base), entry["path"])
        raw = None
        if os.path.exists(target_path):
            with open(target_path, "rb") as fh:
                raw = fh.read()
        fingerprint = identity.object_fingerprint(raw, entry["kind"]) \
            if raw is not None else None
        if fingerprint == entry["after_fingerprint"]:
            recoverable.append(dict(
                entry, note="the new bytes survived; the applied record "
                            "was not written"))
        elif fingerprint == entry["before_fingerprint"]:
            interrupted.append(dict(
                entry, note="the previous bytes survived; the commit did "
                            "not land"))

    objects = {object_id: object_state(base, object_id)
               for object_id in _known_object_ids(ordered)}

    return {"objects": objects, "interrupted": interrupted,
            "recoverable": recoverable, "refused": refused}


def undo(base, entry_id, actor_kind, actor_name):
    """Restore the before-image of the named journal entry as a NEW forward
    revision, journaled with operation `"restore"` and `restores_revision`
    set to the revision the restored content came from. Never deletes or
    edits a line; refuses with `journal.conflict` if the target's current
    fingerprint does not match the named entry's `after_fingerprint`,
    reusing the same message and next-safe-action wording `commit_operation`
    uses for a same-id divergent-bytes conflict.

    This function does not hold `_journal_lock` itself: the compare-and-swap
    guard inside `commit_operation` (called here as `_commit_impl` with
    `expected_fingerprint` set to the freshly-read current fingerprint)
    provides the same atomicity a second, outer lock acquisition here would
    only deadlock trying to duplicate.
    """
    entry = None
    for candidate in entries(base):
        if candidate["entry_id"] == entry_id:
            entry = candidate
            break
    if entry is None:
        raise JournalError("journal.unknown_entry",
                            "no journal entry %s found" % entry_id)

    object_id, kind, rel_path = entry["object_id"], entry["kind"], \
        entry["path"]
    target_path = os.path.join(os.path.abspath(base), rel_path)
    current_raw = None
    if os.path.exists(target_path):
        with open(target_path, "rb") as fh:
            current_raw = fh.read()
    current_fingerprint = identity.object_fingerprint(current_raw, kind) \
        if current_raw is not None else None

    if current_fingerprint != entry["after_fingerprint"]:
        registry = _compute_registry(base)
        prev = registry.get(object_id)
        registry_fingerprint = prev["fingerprint"] if prev is not None \
            else None
        raise JournalError(
            "journal.conflict",
            "object %s has the same id and divergent bytes: on disk %s, "
            "last accepted revision %d recorded %s. This is a conflict, "
            "not an overwrite. Next safe action: read the object, "
            "reconcile the difference by hand, then re-run the operation "
            "with the on-disk fingerprint as the expected base."
            % (object_id, current_fingerprint,
               prev["revision"] if prev is not None else 0,
               registry_fingerprint))

    before_image = entry.get("before_image")
    before_raw = b""
    if before_image:
        before_path = os.path.join(journal_dir(base), before_image)
        with open(before_path, "rb") as fh:
            before_raw = fh.read()

    return _commit_impl(
        base, object_id, kind, rel_path, "restore", before_raw,
        expected_fingerprint=current_fingerprint, actor_kind=actor_kind,
        actor_name=actor_name, create_if_missing=True,
        source_object_id=None, source_revision=None,
        restores_revision=entry.get("parent_revision"))


# ---------------------------------------------------------------------------
# 14A-03: the six operations, each a thin handler over `commit_operation`.
#
# Every handler below builds its own operation descriptor and calls
# `commit_operation` (through `_commit_impl`); none of them writes a byte,
# takes a lock, or appends a journal line of its own. They differ only in
# their identity effect (does a new id get minted, does the old id survive)
# and their provenance effect (what gets recorded about where the bytes came
# from), exactly the two axes FILE-03 names.


def op_link(base, kind, rel_path, actor_kind, actor_name):
    """Mint a new id for a file that stays where it lives. The bytes are
    never written by this operation: `commit_operation` is called with
    `write_target=False`, so the target's `mtime_ns` is unchanged and the
    recorded fingerprint is simply the fingerprint observed at link time.
    Binding a file this way records no source rights obligation, because
    nothing is copied out of the file's owner's control."""
    target_path = os.path.join(os.path.abspath(base), rel_path)
    raw = None
    if os.path.exists(target_path):
        with open(target_path, "rb") as fh:
            raw = fh.read()
    object_id = identity.new_object_id()
    return commit_operation(
        base, object_id, kind, rel_path, "link", raw,
        expected_fingerprint=None, actor_kind=actor_kind,
        actor_name=actor_name, create_if_missing=False,
        write_target=False)


def _op_pull_source(base, operation, source_object_id, kind, rel_path, raw,
                     actor_kind, actor_name):
    object_id = identity.new_object_id()
    return commit_operation(
        base, object_id, kind, rel_path, operation, raw,
        expected_fingerprint=None, actor_kind=actor_kind,
        actor_name=actor_name, create_if_missing=True,
        source_object_id=source_object_id)


def op_import(base, source_object_id, kind, rel_path, raw, actor_kind,
              actor_name):
    """Mint a new id for a new owned artifact pulled from `source_object_id`;
    records `source_object_id` and `source_revision` on the entry. Requires
    the source's `transform` right to be exactly `"granted"`
    (RIGHTS-01); refuses with `journal.rights_unknown` before any mutation
    otherwise. The source object's own registry row is never touched."""
    return _op_pull_source(base, "import", source_object_id, kind, rel_path,
                            raw, actor_kind, actor_name)


def op_copy(base, source_object_id, kind, rel_path, raw, actor_kind,
            actor_name):
    """Mint a new id for a new owned artifact duplicated from
    `source_object_id`; records `source_object_id` and `source_revision` on
    the entry. Same `transform`-right gate as `op_import`, for the same
    reason: this operation pulls a source's bytes into a new owned artifact
    (RIGHTS-01). The source object's own registry row is never touched."""
    return _op_pull_source(base, "copy", source_object_id, kind, rel_path,
                            raw, actor_kind, actor_name)


def op_move(base, object_id, new_rel_path, expected_fingerprint, actor_kind,
            actor_name):
    """Keep `object_id`; the recorded path changes to `new_rel_path` and the
    revision advances. The previous path rides in the entry's `message`
    field as a plain-text note, since move's provenance is the previous path
    rather than a source object. After the new path is committed, the old
    file is removed so the object's bytes live in exactly one place; a
    caller who wants the old bytes preserved should `op_copy` first. No
    source transform grant is required: the object being moved is already
    owned."""
    prev = read_registry(base).get(object_id)
    if prev is None:
        raise JournalError("journal.unknown_object",
                            "no such object %s" % object_id)
    old_rel_path = prev["path"]
    old_target = os.path.join(os.path.abspath(base), old_rel_path)
    with open(old_target, "rb") as fh:
        raw = fh.read()
    record = commit_operation(
        base, object_id, prev["kind"], new_rel_path, "move", raw,
        expected_fingerprint, actor_kind, actor_name,
        note="moved from %s" % old_rel_path)
    new_target = os.path.join(os.path.abspath(base), new_rel_path)
    if os.path.abspath(old_target) != os.path.abspath(new_target) and \
            os.path.exists(old_target):
        os.remove(old_target)
    return record


def op_edit_in_place(base, object_id, kind, rel_path, raw,
                      expected_fingerprint, actor_kind, actor_name):
    """Keep `object_id` and `rel_path`; the revision advances. Records
    nothing extra beyond the revision lineage itself, which is its own
    provenance. No source transform grant is required: the object being
    edited is already owned."""
    return commit_operation(
        base, object_id, kind, rel_path, "edit_in_place", raw,
        expected_fingerprint, actor_kind, actor_name)


def op_supersede(base, superseding_object_id, superseded_object_id,
                  expected_fingerprint, actor_kind, actor_name):
    """Keep both ids alive. The superseded object's registry row gains
    `superseded_by`; the superseding object's row gains `supersedes`.
    Neither row is deleted and neither loses its id (per
    `PLANNING-DIRECTIVES.md` section 3a's append-only ledger discipline,
    applied here to artifacts as well as ideas). No bytes are written
    (`write_target=False`): supersede is a relationship annotation, not a
    content edit. Raises `journal.supersede_self` if the two ids are equal.
    No source transform grant is required: both objects are already owned.
    """
    if superseding_object_id == superseded_object_id:
        raise JournalError(
            "journal.supersede_self",
            "object %s cannot supersede itself" % superseding_object_id)
    registry = read_registry(base)
    prev = registry.get(superseding_object_id)
    if prev is None:
        raise JournalError("journal.unknown_object",
                            "no such object %s" % superseding_object_id)
    if superseded_object_id not in registry:
        raise JournalError("journal.unknown_object",
                            "no such object %s" % superseded_object_id)
    return commit_operation(
        base, superseding_object_id, prev["kind"], prev["path"], "supersede",
        None, expected_fingerprint, actor_kind, actor_name,
        source_object_id=superseded_object_id, write_target=False)


# ---------------------------------------------------------------------------
# 14A-03: candidate lists. Every one of these is read-only, returns a
# path-sorted list (never raises for an empty registry or an empty input),
# and is consumed by nothing else in this module: a caller decides what, if
# anything, to do with a hint or a candidate.


def name_hints(base, name, limit=10):
    """Near-name matches for `name` against every path currently in the
    registry, using `difflib.get_close_matches` over lowercased base names.

    This is a search hint only. No operation and no candidate function in
    this module ever consumes this result to decide identity: a similar
    name never establishes identity (FILE-03; the name-based-identity
    rejection in synthesis 12.4). Every returned dict carries the literal
    key `hint` set to `True` so a caller can never mistake a hint for a
    confirmed match.
    """
    registry = read_registry(base)
    by_lower_name = {}
    for object_id, row in registry.items():
        path = row.get("path") or ""
        lower_name = os.path.basename(path).lower()
        by_lower_name.setdefault(lower_name, []).append((path, object_id))
    matches = difflib.get_close_matches(
        name.lower(), list(by_lower_name.keys()), n=limit, cutoff=0.6)
    hints = []
    for matched_name in matches:
        for path, object_id in by_lower_name[matched_name]:
            hints.append({"path": path, "object_id": object_id, "hint": True})
    hints.sort(key=lambda h: h["path"])
    return hints


def copy_candidates_from_registry(base):
    """Path-sorted pairs of registry rows that share a fingerprint and
    differ in `object_id`, comparing ids first and fingerprints second.

    Comparing fingerprints without comparing ids first would collapse
    ID-02's three distinct outcomes (conflict, copy candidate, move
    candidate) into one: the registry holds exactly one row per id, so the
    "same id, divergent bytes" conflict case can never appear here (it is
    caught during `commit_operation`'s compare-and-swap instead), but the
    id comparison still runs first, as a matter of the module's one
    invariant, not as a shortcut available only in this function.
    """
    registry = read_registry(base)
    ids = sorted(registry.keys())
    pairs = []
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            id_a, id_b = ids[i], ids[j]
            if id_a == id_b:
                continue
            row_a, row_b = registry[id_a], registry[id_b]
            fp_a, fp_b = row_a.get("fingerprint"), row_b.get("fingerprint")
            if fp_a is None or fp_b is None or fp_a != fp_b:
                continue
            a, b = (row_a, row_b) if (row_a.get("path") or "") <= \
                (row_b.get("path") or "") else (row_b, row_a)
            pairs.append({
                "object_id_a": a["object_id"], "path_a": a.get("path"),
                "object_id_b": b["object_id"], "path_b": b.get("path"),
                "fingerprint": fp_a,
            })
    pairs.sort(key=lambda p: (p["path_a"] or "", p["path_b"] or ""))
    return pairs


def duplicate_groups(base):
    """Path-sorted groups of two or more registry rows that share one
    fingerprint, each group itself sorted by path. A copy-candidate pair is
    the two-member case of this same grouping."""
    registry = read_registry(base)
    by_fingerprint = {}
    for object_id in sorted(registry):
        row = registry[object_id]
        fp = row.get("fingerprint")
        if fp is None:
            continue
        by_fingerprint.setdefault(fp, []).append(row)
    groups = []
    for fp, rows in by_fingerprint.items():
        if len(rows) < 2:
            continue
        rows_sorted = sorted(rows, key=lambda r: r.get("path") or "")
        groups.append({"fingerprint": fp, "objects": rows_sorted})
    groups.sort(key=lambda g: g["objects"][0].get("path") or "")
    return groups


def move_candidates(base, candidate_entries):
    """Move candidates from `candidate_entries`, a caller-prepared list of
    dicts carrying at least `path` and `fingerprint`, and optionally a
    claimed `object_id`, `revision`, and `parent_revision`.

    A candidate whose `fingerprint` matches a registry row's fingerprint at
    a different `path` is accepted as a move only when it carries no claimed
    identity (an ordinary discovery-shaped entry with no lineage claim to
    check) or when its claimed `object_id`, `revision`, and `parent_revision`
    agree exactly with that row's own recorded lineage. A candidate that
    claims a known `object_id` at a new path but whose claimed revision
    lineage does not match the registry's is refused with
    `journal.move_lineage_mismatch` rather than silently accepted: T-14A-03-01
    names this as the crafted-path hijack this check exists to close. The
    path-and-id pair alone is never trusted on its own.
    """
    registry = read_registry(base)
    by_fingerprint = {}
    for object_id, row in registry.items():
        by_fingerprint.setdefault(row.get("fingerprint"), []).append(
            (object_id, row))

    candidates = []
    for entry in candidate_entries:
        fp = entry.get("fingerprint")
        path = entry.get("path")
        if fp is None or path is None:
            continue
        for object_id, row in by_fingerprint.get(fp, []):
            if row.get("path") == path:
                continue
            claimed_id = entry.get("object_id")
            if claimed_id is not None and claimed_id != object_id:
                continue
            if claimed_id is not None:
                claimed_revision = entry.get("revision")
                claimed_parent = entry.get("parent_revision")
                if claimed_revision != row.get("revision") or \
                        claimed_parent != row.get("parent_revision"):
                    raise JournalError(
                        "journal.move_lineage_mismatch",
                        "path %s carries the id of object %s but its "
                        "revision lineage does not match the recorded "
                        "one; this is reported as a conflict for review, "
                        "not accepted as a move" % (path, object_id))
            candidates.append({
                "path": path, "object_id": object_id,
                "from_path": row.get("path"), "fingerprint": fp,
            })
    candidates.sort(key=lambda c: c["path"])
    return candidates


# ---------------------------------------------------------------------------
# 14A-03: external edits, conflicted reads, and explicit reconciliation.


def read_object(base, object_id):
    """The current bytes, state, and both fingerprints for `object_id`,
    read without ever writing. A conflicted object still reads: its current
    on-disk bytes are returned alongside `state == "conflict"`, the last
    accepted `revision`, and both `fingerprint` (on disk now) and
    `accepted_fingerprint` (the last journaled revision), so a caller can
    render the divergence honestly instead of being blocked from reading at
    all (RELIABILITY-01's degraded clause)."""
    registry = read_registry(base)
    row = registry.get(object_id)
    state = object_state(base, object_id)
    if row is None:
        return {"bytes": None, "state": state, "revision": None,
                "fingerprint": None, "accepted_fingerprint": None}
    target_path = os.path.join(os.path.abspath(base), row["path"])
    raw = None
    if os.path.exists(target_path):
        with open(target_path, "rb") as fh:
            raw = fh.read()
    fingerprint = identity.object_fingerprint(raw, row["kind"]) \
        if raw is not None else None
    return {"bytes": raw, "state": state, "revision": row.get("revision"),
            "fingerprint": fingerprint,
            "accepted_fingerprint": row.get("fingerprint")}


def detect_external_edits(base):
    """Append one `external_edit` record for every registry row whose
    on-disk fingerprint differs from its accepted fingerprint and which has
    no `external_edit` record since its last `applied` record; return the
    list of affected object ids.

    Idempotency is exactly that "since its last applied record" clause: a
    second immediate call finds the same divergence already covered by the
    record the first call appended, and appends nothing for it. The record
    carries `before_fingerprint` (the last accepted fingerprint) and
    `after_fingerprint` (the observed on-disk fingerprint), so a history
    view can render the divergence honestly instead of it disappearing as
    silent drift (editor-landscape R9).
    """
    affected = []
    with _journal_lock(base):
        registry = _compute_registry(base)
        external_since_applied = {}
        for entry in entries(base):
            object_id = entry.get("object_id")
            if not object_id:
                continue
            if entry.get("state") == "applied":
                external_since_applied[object_id] = False
            elif entry.get("operation") == "external_edit":
                external_since_applied[object_id] = True

        for object_id, row in registry.items():
            if external_since_applied.get(object_id):
                continue
            target_path = os.path.join(os.path.abspath(base), row["path"])
            raw = None
            if os.path.exists(target_path):
                with open(target_path, "rb") as fh:
                    raw = fh.read()
            fingerprint = identity.object_fingerprint(raw, row["kind"]) \
                if raw is not None else None
            if fingerprint == row.get("fingerprint"):
                continue
            entry = _new_template(
                "external_edit", object_id, row["kind"], row["path"],
                "runtime", "", None, None, None, rights=row.get("rights"))
            entry["state"] = "applied"
            # `_compute_registry` treats every `applied` entry, regardless
            # of operation, as the object's complete current row: revision
            # and parent_revision must be carried forward unchanged here, or
            # this passive detection record would silently corrupt the
            # registry's revision lineage.
            entry["revision"] = row.get("revision")
            entry["parent_revision"] = row.get("parent_revision")
            entry["before_fingerprint"] = row.get("fingerprint")
            entry["after_fingerprint"] = fingerprint
            entry["message"] = (
                "detected outside the journal: the object's bytes changed "
                "without going through commit_operation")
            append_entry(base, entry)
            affected.append(object_id)
    return affected


def reconcile(base, object_id, chosen_fingerprint, actor_kind, actor_name,
              note):
    """Record a human's chosen base fingerprint for a conflicted object and
    append one `reconcile` record. There is no merge function anywhere in
    this module: reconciliation is a recorded human decision, never an
    algorithm (the append-only rejection of ambiguous auto-merge, synthesis
    12.4).

    `chosen_fingerprint` must equal either the object's current on-disk
    fingerprint or its last accepted fingerprint; any other value refuses
    with `journal.stale_preflight` and appends no record. Choosing the
    on-disk fingerprint accepts the external edit as the new truth, after
    which `object_state` reads `clean` again; choosing the last accepted
    fingerprint records that the human rejected the external edit, though
    the bytes on disk are untouched by this function (there is no merge, and
    no automatic revert either).
    """
    with _journal_lock(base):
        registry = _compute_registry(base)
        row = registry.get(object_id)
        if row is None:
            raise JournalError("journal.unknown_object",
                                "no such object %s" % object_id)
        target_path = os.path.join(os.path.abspath(base), row["path"])
        raw = None
        if os.path.exists(target_path):
            with open(target_path, "rb") as fh:
                raw = fh.read()
        on_disk_fingerprint = identity.object_fingerprint(raw, row["kind"]) \
            if raw is not None else None
        accepted_fingerprint = row.get("fingerprint")

        if chosen_fingerprint not in (on_disk_fingerprint,
                                       accepted_fingerprint):
            raise JournalError(
                "journal.stale_preflight",
                "chosen fingerprint %s matches neither the on-disk "
                "fingerprint %s nor the last accepted fingerprint %s for "
                "object %s; nothing was recorded"
                % (chosen_fingerprint, on_disk_fingerprint,
                   accepted_fingerprint, object_id))

        entry = _new_template(
            "reconcile", object_id, row["kind"], row["path"], actor_kind,
            actor_name, None, None, None)
        entry["state"] = "applied"
        entry["revision"] = row.get("revision")
        entry["parent_revision"] = row.get("parent_revision")
        entry["before_fingerprint"] = on_disk_fingerprint
        entry["after_fingerprint"] = chosen_fingerprint
        entry["message"] = note
        entry["rights"] = row.get("rights")
        applied = append_entry(base, entry)
        rebuild_registry(base)
        return applied
