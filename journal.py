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
import hashlib
import json
import os
import sys
import time
import uuid

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
# operation types above, plus the three this plan's own machinery writes
# ("mint" for a brand-new object, "restore" for an undo, and
# "external_edit" reserved for a future detector of an out-of-band change).
RECORD_TYPES = OPERATION_TYPES + ("mint", "restore", "external_edit")

# The journal entry key order, fixed. Every entry this module writes carries
# exactly this key set, in exactly this order, so `list(entry.keys())` is
# itself an assertable contract the same way `identity.REVISION_KEYS` is.
ENTRY_KEYS = (
    "schema_version", "entry_id", "timestamp", "operation", "state",
    "resolves_entry", "object_id", "kind", "revision", "parent_revision",
    "path", "expected_fingerprint", "before_fingerprint", "after_fingerprint",
    "before_image", "undo", "source_object_id", "source_revision",
    "restores_revision", "origin", "code", "message",
)

# The per-object registry projection key order. Deliberately a superset of
# `identity.REVISION_KEYS` plus `path` and `last_entry_id`: the journal does
# not carry `profile_version`, `source_version`, `generator_version`, or
# `rights` in its own entries, so those three ride along as None here rather
# than being silently dropped from the revision-record shape a caller
# expects back.
REGISTRY_OBJECT_KEYS = (
    "object_id", "kind", "path", "revision", "parent_revision", "fingerprint",
    "timestamp", "origin", "profile_version", "source_version",
    "generator_version", "rights", "last_entry_id",
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
                   restores_revision):
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
    }


def commit_operation(base, object_id, kind, rel_path, operation, new_bytes,
                      expected_fingerprint, actor_kind, actor_name,
                      create_if_missing=False, source_object_id=None,
                      source_revision=None):
    """The one compare-and-swap write path every durable object kind goes
    through. See the module docstring's Walking-skeleton usage paragraph for
    the minimal three-call sequence. Raises `JournalError` on refusal;
    returns the new revision record on success."""
    return _commit_impl(
        base, object_id, kind, rel_path, operation, new_bytes,
        expected_fingerprint, actor_kind, actor_name,
        create_if_missing=create_if_missing,
        source_object_id=source_object_id, source_revision=source_revision,
        restores_revision=None)


def _commit_impl(base, object_id, kind, rel_path, operation, new_bytes,
                  expected_fingerprint, actor_kind, actor_name,
                  create_if_missing, source_object_id, source_revision,
                  restores_revision):
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

    with _journal_lock(base):
        target_path = os.path.join(os.path.abspath(base), rel_path)
        exists = os.path.exists(target_path)
        before_raw = None
        if exists:
            with open(target_path, "rb") as fh:
                before_raw = fh.read()
        before_fingerprint = identity.object_fingerprint(before_raw, kind) \
            if before_raw is not None else None
        after_fingerprint = identity.object_fingerprint(new_bytes, kind)

        registry = _compute_registry(base)
        prev = registry.get(object_id)

        template = _new_template(
            operation, object_id, kind, rel_path, actor_kind, actor_name,
            source_object_id, source_revision, restores_revision)
        template["expected_fingerprint"] = expected_fingerprint
        template["before_fingerprint"] = before_fingerprint
        template["after_fingerprint"] = after_fingerprint

        if prev is not None and expected_fingerprint is None:
            _refuse(base, template, "journal.missing_fingerprint",
                    "object %s carries no fingerprint, so a compare-and-swap "
                    "write cannot be checked; the write is refused rather "
                    "than performed blind" % object_id)

        if expected_fingerprint is not None and \
                expected_fingerprint != before_fingerprint:
            registry_fingerprint = prev["fingerprint"] if prev is not None \
                else None
            if registry_fingerprint != before_fingerprint:
                _refuse(base, template, "journal.conflict",
                        "object %s has the same id and divergent bytes: on "
                        "disk %s, last accepted revision %d recorded %s. "
                        "This is a conflict, not an overwrite. Next safe "
                        "action: read the object, reconcile the difference "
                        "by hand, then re-run the operation with the "
                        "on-disk fingerprint as the expected base."
                        % (object_id, before_fingerprint,
                           prev["revision"] if prev is not None else 0,
                           registry_fingerprint))
            _refuse(base, template, "journal.stale_preflight",
                    "current fingerprint %s does not match the expected "
                    "base fingerprint %s; the object changed since this "
                    "operation was prepared"
                    % (before_fingerprint, expected_fingerprint))

        if after_fingerprint == before_fingerprint:
            _refuse(base, template, "journal.no_change",
                    "the new bytes for %s are identical to the current "
                    "bytes; no revision was recorded" % object_id)

        revision = 1 if prev is None else prev["revision"] + 1
        parent_revision = None if prev is None else prev["revision"]

        before_image = None
        if exists:
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

        _write_bytes_atomic(target_path, new_bytes)

        with open(target_path, "rb") as fh:
            committed_raw = fh.read()
        committed_fingerprint = identity.object_fingerprint(committed_raw,
                                                              kind)
        if committed_fingerprint != after_fingerprint:
            refused = dict(template)
            refused["state"] = "refused"
            refused["resolves_entry"] = prepared["entry_id"]
            refused["code"] = "journal.after_guard_failed"
            refused["message"] = (
                "the committed bytes of %s fingerprint as %s but the "
                "operation expected %s; the journal entry stays prepared "
                "and the previous revision is still the last accepted one"
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
            origin=_origin(actor_kind, actor_name, operation))


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
    """
    objects = {}
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
            "rights": None,
            "last_entry_id": entry.get("entry_id"),
        }
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
