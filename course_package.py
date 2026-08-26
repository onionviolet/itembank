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


def export_package(base, course_root, dest):
    """Export the course object at `course_root` into a package at `dest`.

    The manifest is written in the `prepared` state before any payload, and
    flipped to `applied` only after every payload has been re-read and
    re-fingerprinted from disk. An export interrupted at any point therefore
    leaves a manifest a restore will refuse, rather than one that looks
    complete.
    """
    import course as course_module

    read = course_module.read_course(course_root)
    os.makedirs(os.path.join(dest, PAYLOAD_DIRNAME), exist_ok=True)

    entries = [{
        "object_id": read["object_id"],
        "kind": course_module.COURSE_KIND,
        "revision": read["revision"],
        "relpath": course_module.COURSE_SIDECAR_FILENAME,
        "fingerprint": read["fingerprint"],
    }]
    manifest = {
        "schema_version": PACKAGE_SCHEMA_VERSION,
        "state": "prepared",
        "course_object_id": read["object_id"],
        "entries": entries,
    }
    manifest_path = os.path.join(dest, MANIFEST_FILENAME)
    _write_json(manifest_path, manifest)

    for entry in entries:
        source = os.path.join(os.path.abspath(course_root), entry["relpath"])
        with open(source, "rb") as fh:
            raw = fh.read()
        _write_bytes_atomic(
            os.path.join(dest, PAYLOAD_DIRNAME, entry["object_id"] + ".md"),
            raw)

    for entry in entries:
        payload = os.path.join(dest, PAYLOAD_DIRNAME,
                               entry["object_id"] + ".md")
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
    return manifest


def read_manifest(package_root):
    path = os.path.join(package_root, MANIFEST_FILENAME)
    if not os.path.exists(path):
        raise PackageError(
            "package.not_applied",
            "this package's manifest state is %s, not applied; it was "
            "interrupted during export and must not be restored" % "absent")
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def restore_package(package_root, dest, actor_kind, actor_name):
    """Restore a package into `dest` and report what was verified.

    `dest` needs no shared journal, no shared registry, and no shared
    evidence store: a restore mints the destination's own journal as it
    writes, which is what makes a clean-machine restore a real one.
    """
    manifest = read_manifest(package_root)
    state = manifest.get("state")
    if state != "applied":
        raise PackageError(
            "package.not_applied",
            "this package's manifest state is %s, not applied; it was "
            "interrupted during export and must not be restored" % state)

    verified = 0
    for entry in manifest.get("entries", []):
        payload = os.path.join(package_root, PAYLOAD_DIRNAME,
                               entry["object_id"] + ".md")
        with open(payload, "rb") as fh:
            raw = fh.read()
        found = identity.object_fingerprint(raw, entry["kind"])
        if found != entry["fingerprint"]:
            raise PackageError(
                "package.fingerprint_mismatch",
                "payload %s does not match its manifest fingerprint; "
                "expected %s, found %s"
                % (entry["object_id"], entry["fingerprint"], found))
        safe_target(dest, entry["relpath"])
        journal.commit_operation(
            base=dest, object_id=entry["object_id"], kind=entry["kind"],
            rel_path=entry["relpath"], operation="restore", new_bytes=raw,
            expected_fingerprint=None, actor_kind=actor_kind,
            actor_name=actor_name, create_if_missing=True)
        verified += 1

    return {
        "entries_verified": verified,
        "entries_in_manifest": len(manifest.get("entries", [])),
        "complete": verified == len(manifest.get("entries", [])),
        "course_object_id": manifest.get("course_object_id"),
    }
