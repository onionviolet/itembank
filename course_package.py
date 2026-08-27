"""Course packages: export a course to a portable directory tree, and restore
one on a destination that never saw the original.

`course_package.py` is a peer of `audit_writer.py` in the runtime tier. It
follows the same shape `audit_writer.py` already ships: the manifest is
written before any payload, every write is a temporary file followed by an
atomic replace, and the manifest is only flipped to its final state once every
payload has been re-read and re-fingerprinted.

A package is a plain directory tree first and an archive only as optional
transport, so a person can read what is in one without this tool.

A package received from another machine is untrusted input the moment it
crosses a machine boundary. This is the one place in Phase 14B where the
project's single-local-user posture stops applying, because of the
friend-installs-a-copy goal recorded in the amended Users constraint. Every
restore target path is therefore resolved and contained before anything is
written, and a traversing entry is refused by name rather than clamped to a
safe path: silently correcting a hostile path teaches the caller nothing and
hides the attempt.

A restore recomputes every payload's fingerprint rather than trusting the
manifest's own claim about it. A restore that believes the manifest is not a
validated restore, and PORT-03 asks for a validated one: the report says what
was verified, not what was promised.

This module imports no `urllib`, no `socket`, and no `subprocess`. A restore
is structurally an offline operation, not merely an offline one by habit.
"""
import json
import os
import zipfile

import evidence
import identity
import journal

PACKAGE_SCHEMA_VERSION = 1
MANIFEST_FILENAME = "manifest.json"
PAYLOAD_DIRNAME = "payload"

# `prepared` means the export was interrupted before every payload verified.
# Only `applied` may be restored.
PACKAGE_STATES = ("prepared", "applied")

MANIFEST_ENTRY_KEYS = ("object_id", "kind", "revision", "relpath",
                       "fingerprint")

# The seven manifest keys, fixed by D-14B-5. A package may be handed to
# another person, so this key set is a published contract and grows only
# additively.
MANIFEST_KEYS = ("schema_version", "package_id", "created",
                 "course_object_id", "state", "entries", "loss_report")

EVIDENCE_DIRNAME = "evidence"
EVIDENCE_FILENAME = "evidence_export.jsonl"
LOSS_REPORT_FILENAME = "LOSS-REPORT.md"

# Every way a package can fail to carry something, named. A loss is reported
# with its category, its target, and its reason; it is never silently
# dropped, because a restored course that looks complete and is not is worse
# than one that says what is missing.
LOSS_CATEGORIES = ("external-link", "rights-restricted", "machine-local",
                   "unreachable-source", "unsupported-kind")

# The one operation-specific right that gates payload inclusion (RIGHTS-01).
# `export` is handing a file to a person; `package` is writing it into a
# bundle. A grant for one never implies the other.
PACKAGE_RIGHT = "package"

PACKAGED_KINDS = ("course", "objective", "source", "lesson", "bank")

# A package is a plain directory tree first (D-14B-5). `None` is the default
# and means the tree itself; `zip` is optional transport and never the source
# of truth.
ARCHIVE_FORMATS = (None, "zip")

# A declared uncompressed size above this is refused before a byte is
# written, so a decompression bomb in a received archive is a refusal rather
# than a full disk.
MAX_ENTRY_BYTES = 104857600

LOSS_REASONS = {
    "external-link": "linked, not imported; the external file keeps its own "
                     "identity and location and is not copied into a package",
    "rights-restricted": "the %s right for this source is %s; unknown and "
                         "denied both stay restrictive, so this object is "
                         "named here rather than packaged",
    "machine-local": "not included by design; model backend configuration, "
                     "update policy, and local paths belong to the machine, "
                     "not to the course",
    "unreachable-source": "the recorded root was unavailable when this "
                          "package was built; the object is named here "
                          "rather than omitted silently",
    "unsupported-kind": "kind %s is not one of the packaged kinds course, "
                        "objective, source, lesson, bank; it is named here "
                        "rather than dropped",
}


class PackageError(Exception):
    """A typed package failure: machine-readable `code` plus message, the
    same two-argument shape `identity.IdentityError` uses."""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message


def _write_json(path, data):
    """The repository's UTF-8, pretty JSON, trailing newline, tmp-then-replace
    convention (`audit_writer.py:250`)."""
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    os.replace(tmp, path)


def _write_bytes_atomic(path, raw):
    tmp = path + ".tmp"
    with open(tmp, "wb") as fh:
        fh.write(raw)
    os.replace(tmp, path)


def safe_target(dest, relpath):
    """The absolute path `relpath` may be written to inside `dest`, or a
    raise.

    Refuses an absolute path, refuses any `..` component, and refuses any
    result that does not genuinely resolve inside `dest` after link
    resolution. The refusal is a raise, never a clamp: a package entry that
    tries to escape is reported, not quietly corrected.
    """
    if os.path.isabs(relpath):
        raise PackageError(
            "package.path_escape",
            "the package entry %s resolves outside the restore destination; "
            "refused, never clamped" % relpath)
    parts = relpath.replace("\\", "/").split("/")
    if os.pardir in parts:
        raise PackageError(
            "package.path_escape",
            "the package entry %s resolves outside the restore destination; "
            "refused, never clamped" % relpath)
    root = os.path.realpath(dest)
    target = os.path.realpath(os.path.join(root, relpath))
    try:
        contained = os.path.commonpath([root, target]) == root
    except ValueError:
        contained = False
    if not contained or target == root:
        raise PackageError(
            "package.path_escape",
            "the package entry %s resolves outside the restore destination; "
            "refused, never clamped" % relpath)
    return target


def _loss_row(category, target, reason):
    return {"category": category, "target": target, "reason": reason}


def _payload_relpath(entry):
    """Where one object's bytes live inside the package.

    Named by `object_id`, never by content: two byte-identical sources under
    two ids are two objects, so they get two payload files and are never
    deduplicated into one (ID-02).
    """
    return "/".join((PAYLOAD_DIRNAME, entry["object_id"] + ".md"))


def _externally_owned(base):
    """The ids whose FIRST applied journal entry was a `link`.

    Read from the journal rather than from the registry's latest row on
    purpose: the registry projects the most recent operation, so recording a
    rights grant on a linked source would otherwise erase the fact that it
    was linked. What makes an object external is how it entered the course,
    which only the journal remembers.
    """
    seen, linked = set(), set()
    for entry in journal.entries(base):
        if entry.get("state") != "applied":
            continue
        object_id = entry.get("object_id")
        if not object_id or object_id in seen:
            continue
        seen.add(object_id)
        if entry.get("operation") == "link":
            linked.add(object_id)
    return linked


def build_manifest(base, course_root):
    """The manifest for a package of the course at `course_root`, with every
    object either carried as a payload entry or named in the loss report.

    Rights are read from the CURRENT registry at the moment of the call and
    never from a value copied into a binding row or a previous manifest: a
    revoked right takes effect on the next export rather than staying
    effective behind a stale snapshot. Inclusion requires
    `identity.rights_granted(rights, PACKAGE_RIGHT)` to be exactly True, so
    unknown and denied both stay restrictive and both are named.

    The course sidecar is always entry one and is not rights-gated: it is the
    course's own record rather than a bound source, and a package without it
    would carry no course at all.
    """
    import course as course_module

    read = course_module.read_course(course_root)
    course_object_id = read["object_id"]

    entries = [{
        "object_id": course_object_id,
        "kind": course_module.COURSE_KIND,
        "revision": read["revision"],
        "relpath": course_module.COURSE_SIDECAR_FILENAME,
        "fingerprint": read["fingerprint"],
    }]
    losses = [_loss_row("machine-local", "settings",
                        LOSS_REASONS["machine-local"])]

    registry = journal.read_registry(base)
    linked = _externally_owned(base)
    for row in identity.registry_rows(list(registry.values())):
        object_id = row.get("object_id")
        if object_id == course_object_id:
            continue
        kind = row.get("kind")
        if kind not in PACKAGED_KINDS:
            losses.append(_loss_row("unsupported-kind", object_id,
                                    LOSS_REASONS["unsupported-kind"] % kind))
            continue
        rights = row.get("rights")
        if not identity.rights_granted(rights, PACKAGE_RIGHT):
            state = identity.rights_state(rights, PACKAGE_RIGHT)
            losses.append(_loss_row(
                "rights-restricted", object_id,
                LOSS_REASONS["rights-restricted"] % (PACKAGE_RIGHT, state)))
            continue
        # The rights gate runs first on purpose: a source nobody granted the
        # package right for is reported as rights-restricted whatever else is
        # true of it, so a permission problem is never reported as a
        # bookkeeping one. A link that IS granted the right still stays out,
        # because copying it would change what `link` means.
        if object_id in linked:
            losses.append(_loss_row("external-link", object_id,
                                    LOSS_REASONS["external-link"]))
            continue
        source = os.path.join(os.path.abspath(base), row.get("path") or "")
        if not os.path.exists(source):
            losses.append(_loss_row("unreachable-source", object_id,
                                    LOSS_REASONS["unreachable-source"]))
            continue
        entries.append({
            "object_id": object_id,
            "kind": kind,
            "revision": row.get("revision"),
            "relpath": row.get("path"),
            "fingerprint": row.get("fingerprint"),
        })

    entries.sort(key=lambda e: (e["kind"], e["object_id"]))
    losses.sort(key=lambda r: (r["category"], r["target"]))
    return {
        "schema_version": PACKAGE_SCHEMA_VERSION,
        "package_id": identity.new_object_id(),
        "created": identity.utc_now(),
        "course_object_id": course_object_id,
        "state": "prepared",
        "entries": entries,
        "loss_report": losses,
    }


def loss_report_text(manifest):
    """The loss report as plain Markdown a person can read without this tool.

    A zero-loss report still says so in words. An empty file would read as
    "nothing was checked" exactly as easily as "nothing was lost", and those
    are two different claims.
    """
    rows = manifest.get("loss_report") or []
    lines = ["# Package loss report", ""]
    if not rows:
        lines.append("No losses.")
        return "\n".join(lines) + "\n"
    lines.append("| category | target | reason |")
    lines.append("|---|---|---|")
    for row in rows:
        lines.append("| %s | %s | %s |"
                     % (row["category"], row["target"], row["reason"]))
    return "\n".join(lines) + "\n"


def _course_objective_ids(course_root):
    import course as course_module

    read = course_module.read_course(course_root)
    return set(rec.get("id") for rec in read["doc"]["objectives"]
               if rec.get("id"))


def _evidence_export_lines(course_root):
    """The events this course's own objectives carry, one JSON object per
    line, in log order.

    Filtered by objective id, so a shared evidence store never exports
    another course's history into this package. An empty result is a
    zero-byte file rather than an absent one: a restore has to be able to
    tell "no evidence" from "evidence missing".
    """
    log = evidence.log_path(course_root)
    if not os.path.exists(log):
        return []
    wanted = _course_objective_ids(course_root)
    out = []
    for event in evidence.events(log):
        if event.get("objective") in wanted:
            out.append(json.dumps(event, ensure_ascii=False, sort_keys=True))
    return out


def _check_duplicate_relpaths(entries):
    seen = set()
    for entry in entries:
        relpath = entry["relpath"]
        if relpath in seen:
            raise PackageError(
                "package.duplicate_relpath",
                "two manifest entries claim the same payload path %s; "
                "refused" % relpath)
        seen.add(relpath)


def export_package(base, course_root, dest, archive=None, manifest=None):
    """Export the course object at `course_root` into a package at `dest`.

    The manifest is written in the `prepared` state before any payload, and
    flipped to `applied` only after every payload has been re-read and
    re-fingerprinted from disk. An export interrupted at any point therefore
    leaves a manifest a restore will refuse, rather than one that looks
    complete. Flipping the state earlier would make an interrupted export
    indistinguishable from a finished one.

    `archive` is optional transport only. The package is the directory tree
    at `dest`; a zip is written beside it when asked for, and is never the
    source of truth (D-14B-5).
    """
    if archive not in ARCHIVE_FORMATS:
        raise PackageError(
            "package.unsupported_archive",
            "the archive entry or format %s is not supported; refused"
            % archive)
    if manifest is None:
        manifest = build_manifest(base, course_root)
    entries = manifest.get("entries", [])
    _check_duplicate_relpaths(entries)

    os.makedirs(os.path.join(dest, PAYLOAD_DIRNAME), exist_ok=True)
    os.makedirs(os.path.join(dest, EVIDENCE_DIRNAME), exist_ok=True)

    manifest["state"] = "prepared"
    manifest_path = os.path.join(dest, MANIFEST_FILENAME)
    _write_json(manifest_path, manifest)

    course_object_id = manifest.get("course_object_id")
    for entry in entries:
        root = course_root if entry["object_id"] == course_object_id else base
        source = os.path.join(os.path.abspath(root), entry["relpath"])
        with open(source, "rb") as fh:
            raw = fh.read()
        _write_bytes_atomic(os.path.join(dest, _payload_relpath(entry)), raw)

    lines = _evidence_export_lines(course_root)
    body = ("\n".join(lines) + "\n") if lines else ""
    _write_bytes_atomic(
        os.path.join(dest, EVIDENCE_DIRNAME, EVIDENCE_FILENAME),
        body.encode("utf-8"))

    _write_bytes_atomic(os.path.join(dest, LOSS_REPORT_FILENAME),
                        loss_report_text(manifest).encode("utf-8"))

    for entry in entries:
        payload = os.path.join(dest, _payload_relpath(entry))
        with open(payload, "rb") as fh:
            written = fh.read()
        found = identity.object_fingerprint(written, entry["kind"])
        if found != entry["fingerprint"]:
            raise PackageError(
                "package.fingerprint_mismatch",
                "payload %s does not match its manifest fingerprint; "
                "expected %s, found %s"
                % (entry["object_id"], entry["fingerprint"], found))

    manifest["state"] = "applied"
    _write_json(manifest_path, manifest)

    if archive == "zip":
        _write_archive(dest, dest.rstrip(os.sep) + ".zip")
    return manifest


def _write_archive(package_root, archive_path):
    """Zip a finished package tree for transport. The tree stays the package;
    this is a copy of it in one file."""
    root = os.path.abspath(package_root)
    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for dirpath, _dirnames, filenames in os.walk(root):
            for name in sorted(filenames):
                full = os.path.join(dirpath, name)
                zf.write(full, os.path.relpath(full, root).replace(os.sep, "/"))
    return archive_path


def read_manifest(package_root):
    """The package's manifest, or a named refusal.

    Invalid JSON is refused by name and is never read as an empty manifest: a
    truncated manifest that parsed as zero entries would restore an empty
    course and call it complete.
    """
    path = os.path.join(package_root, MANIFEST_FILENAME)
    if not os.path.exists(path):
        raise PackageError(
            "package.not_applied",
            "this package's manifest state is %s, not applied; it was "
            "interrupted during export and must not be restored" % "absent")
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    try:
        return json.loads(text)
    except ValueError:
        raise PackageError(
            "package.manifest_unreadable",
            "the manifest at %s is not valid JSON; a package with an "
            "unreadable manifest is refused, never treated as empty" % path)


def verify_manifest(package_root):
    """Verify every payload in the package against the manifest, by
    recomputation.

    Every payload's fingerprint is computed again from the bytes on disk and
    compared with the manifest's claim. The manifest's own recorded value is
    never read back to itself: a restore that trusts the manifest validates
    nothing, and PORT-03's clause is about validation. What this function
    reports is what was verified, not what was promised.
    """
    manifest = read_manifest(package_root)
    verified, mismatches, missing = 0, [], []
    for entry in manifest.get("entries", []):
        payload = os.path.join(package_root, _payload_relpath(entry))
        if not os.path.exists(payload):
            missing.append({"object_id": entry["object_id"],
                            "relpath": entry["relpath"],
                            "payload": _payload_relpath(entry)})
            continue
        with open(payload, "rb") as fh:
            raw = fh.read()
        found = identity.object_fingerprint(raw, entry["kind"])
        if found != entry["fingerprint"]:
            mismatches.append({"object_id": entry["object_id"],
                               "expected": entry["fingerprint"],
                               "found": found})
            continue
        verified += 1
    total = len(manifest.get("entries", []))
    return {
        "entries_verified": verified,
        "mismatches": mismatches,
        "missing": missing,
        "complete": verified == total and not mismatches and not missing,
    }


def restore_package(package_root, dest, actor_kind, actor_name):
    """Restore a package into `dest` and report what was verified.

    `dest` needs no shared journal, no shared registry, and no shared
    evidence store: a restore mints the destination's own journal as it
    writes, which is what makes a clean-machine restore a real one.

    Two loss lists come back and neither replaces the other: `losses` is the
    export-time report copied from the manifest, and `restore_losses` is what
    this restore itself could not carry.
    """
    manifest = read_manifest(package_root)
    state = manifest.get("state")
    if state != "applied":
        raise PackageError(
            "package.not_applied",
            "this package's manifest state is %s, not applied; it was "
            "interrupted during export and must not be restored" % state)

    entries = manifest.get("entries", [])
    _check_duplicate_relpaths(entries)

    report = verify_manifest(package_root)
    if report["missing"]:
        gap = report["missing"][0]
        raise PackageError(
            "package.missing_payload",
            "manifest entry %s names payload %s, which is not in the package"
            % (gap["object_id"], gap["payload"]))
    if report["mismatches"]:
        bad = report["mismatches"][0]
        raise PackageError(
            "package.fingerprint_mismatch",
            "payload %s does not match its manifest fingerprint; expected "
            "%s, found %s"
            % (bad["object_id"], bad["expected"], bad["found"]))

    destination_registry = journal.read_registry(dest)
    verified, restore_losses = 0, []
    for entry in entries:
        if entry["kind"] not in PACKAGED_KINDS:
            restore_losses.append(_loss_row(
                "unsupported-kind", entry["object_id"],
                LOSS_REASONS["unsupported-kind"] % entry["kind"]))
            continue
        payload = os.path.join(package_root, _payload_relpath(entry))
        with open(payload, "rb") as fh:
            raw = fh.read()
        safe_target(dest, entry["relpath"])
        # A second restore of the same package into the same destination is
        # not a rewrite: the object is already there at the same fingerprint,
        # so nothing is written and the entry still counts as verified. A row
        # that is present at a DIFFERENT fingerprint is left to
        # `journal.commit_operation`, which refuses it as the conflict it is
        # rather than overwriting a divergence.
        existing = destination_registry.get(entry["object_id"])
        if existing is not None and \
                existing.get("fingerprint") == entry["fingerprint"]:
            verified += 1
            continue
        journal.commit_operation(
            base=dest, object_id=entry["object_id"], kind=entry["kind"],
            rel_path=entry["relpath"], operation="restore", new_bytes=raw,
            expected_fingerprint=None, actor_kind=actor_kind,
            actor_name=actor_name, create_if_missing=True)
        verified += 1

    recorded, already = _restore_evidence(package_root, dest)

    return {
        "entries_verified": verified,
        "entries_in_manifest": len(entries),
        "complete": verified == len(entries),
        "course_object_id": manifest.get("course_object_id"),
        "losses": list(manifest.get("loss_report") or []),
        "restore_losses": restore_losses,
        "evidence_recorded": recorded,
        "evidence_already_recorded": already,
    }


def _restore_evidence(package_root, dest):
    """Append every exported event into the destination's own evidence log
    through `evidence.append_event`, the one evidence writer.

    No second evidence store is created here and none may ever be. The one
    writer already answers `recorded` versus `already_recorded`, so counting
    its answers makes a second restore of the same package idempotent for
    free rather than by a dedupe rule invented in this module.
    """
    exported = os.path.join(package_root, EVIDENCE_DIRNAME, EVIDENCE_FILENAME)
    if not os.path.exists(exported):
        return 0, 0
    log = evidence.log_path(dest)
    recorded, already = 0, 0
    with open(exported, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            event = json.loads(line)
            answer = evidence.append_event(log, event)
            if answer.get("status") == "recorded":
                recorded += 1
            else:
                already += 1
    return recorded, already


def _is_symlink_entry(info):
    return (info.external_attr >> 16) & 0o170000 == 0o120000


def extract_archive(archive_path, dest, archive="zip"):
    """Extract a package archive into `dest`, one contained entry at a time.

    A package received from another person is untrusted input the moment it
    crosses a machine boundary. This is the one place in Phase 14B where the
    project's single-local-user posture stops applying, because the amended
    Users constraint makes a friend installing their own copy a supported
    goal, and the Zip Slip class of defect is exactly what an archive from
    elsewhere can carry.

    Every entry is therefore resolved and contained before anything is
    written, and `zipfile.ZipFile.extractall` is never called: it would write
    the whole archive before anything could object. An escaping or symbolic
    link entry is refused by name and never clamped to a safe path.
    """
    if archive not in ARCHIVE_FORMATS or archive is None:
        raise PackageError(
            "package.unsupported_archive",
            "the archive entry or format %s is not supported; refused"
            % archive)
    os.makedirs(dest, exist_ok=True)
    with zipfile.ZipFile(archive_path) as zf:
        for info in zf.infolist():
            if info.file_size > MAX_ENTRY_BYTES:
                raise PackageError(
                    "package.unsupported_archive",
                    "the archive entry or format %s is not supported; "
                    "refused" % info.filename)
            if _is_symlink_entry(info):
                raise PackageError(
                    "package.symlink_payload",
                    "the package entry %s is a symbolic link; a package "
                    "payload carries files only" % info.filename)
            if info.is_dir():
                continue
            target = safe_target(dest, info.filename)
            os.makedirs(os.path.dirname(target) or ".", exist_ok=True)
            with zf.open(info) as src:
                _write_bytes_atomic(target, src.read())
    return dest
