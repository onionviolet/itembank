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
import contextlib
import ctypes
import errno
import hashlib
import json
import ntpath
import os
import re
import stat
import sys
import tempfile
import zipfile

import evidence
import identity
import journal
import schema_validate

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

# Version 1 readers retain the original required keys. New exports bind the
# evidence bytes to the manifest with this additive integrity field. Legacy
# packages without evidence remain readable. Unbound evidence is refused.
MANIFEST_OPTIONAL_KEYS = ("evidence_fingerprint",)

EVIDENCE_DIRNAME = "evidence"
EVIDENCE_FILENAME = "evidence_export.jsonl"
LOSS_REPORT_FILENAME = "LOSS-REPORT.md"

PACKAGE_DIRNAME = "_packages"
PACKAGE_STAGING_DIRNAME = "_staging"
PACKAGE_RESTORE_DIRNAME = "_restore"

_OBJECT_ID_RE = re.compile(r"^[0-9a-f]{16}$")
_FINGERPRINT_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
LOSS_ROW_KEYS = ("category", "target", "reason")

# Every way a package can fail to carry something, named. A loss is reported
# with its category, its target, and its reason; it is never silently
# dropped, because a restored course that looks complete and is not is worse
# than one that says what is missing.
LOSS_CATEGORIES = ("external-link", "rights-restricted", "machine-local",
                   "unreachable-source", "unsupported-kind",
                   "evidence-not-carried", "unregistered-file",
                   "provenance-not-carried")

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
    # `17B-04 D-06 item 11`: before this category an unexportable event was
    # simply absent, so a restored course read complete on the evidence axis
    # while empty. An event this course cannot claim is named here with what
    # it was scoped by, never dropped in silence.
    # `17C-AUDIT.md` F-LOSS-3, F-LOSS-4, and F-LOSS-5. A package carries
    # registry objects, so a file inside the course root that no operation
    # ever bound is invisible to it: in the audited course that was a README,
    # a treatments record, six session files, and the media a restored bank
    # cites by name and digest. The file not crossing is defensible; the
    # report not saying so is what made a restored course read complete and
    # not be.
    "unregistered-file": "inside the course root and bound by no operation, "
                         "so no object carries it; named here rather than "
                         "left out in silence. Bind it (link, import, or "
                         "copy) if it belongs to the course",
    # `17C-AUDIT.md` F-LOSS-1 and F-LOSS-2. A restore mints the destination's
    # own journal, which is what makes a clean-machine restore clean. The
    # cost is that provenance and recorded rights do not travel, and until
    # this row nothing said so.
    "provenance-not-carried": "the operation journal is not packaged: %d "
                              "applied entr(y/ies) of history, and the "
                              "rights recorded on them, stay on the "
                              "exporting machine. A restored object arrives "
                              "at revision 1 with its rights unknown, and "
                              "unknown stays restrictive",
    "evidence-not-carried": "%d event(s) in the evidence log at this course "
                            "root belong to no bank, objective, or session "
                            "of this course (%s); they stay in the store "
                            "they were recorded in rather than crossing "
                            "into another course's package",
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
    if not isinstance(relpath, str) or "\x00" in relpath or \
            os.path.isabs(relpath) or ntpath.splitdrive(relpath)[0]:
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


def validate_package_id(package_id):
    """Return one opaque package id, or refuse a path-shaped substitute."""
    if not isinstance(package_id, str) or not _OBJECT_ID_RE.fullmatch(package_id):
        raise PackageError(
            "package.invalid_id",
            "package id %r is not 16 lowercase hexadecimal characters; "
            "a package is addressed by its id, never by a path" % package_id)
    return package_id


def workspace_package_path(root, package_id, area="package"):
    """Resolve one package-owned path below an approved workspace root.

    The caller chooses only an opaque id. Directory names are fixed here,
    and an existing symbolic-link namespace is refused rather than followed.
    """
    validate_package_id(package_id)
    root = os.path.realpath(root)
    package_dir = os.path.join(root, PACKAGE_DIRNAME)
    if os.path.lexists(package_dir) and os.path.islink(package_dir):
        raise PackageError(
            "package.symlink_payload",
            "%s is a symbolic link; the package namespace must stay inside "
            "the approved root" % PACKAGE_DIRNAME)
    if os.path.lexists(package_dir) and not os.path.isdir(package_dir):
        raise PackageError("package.not_found",
                           "%s is not a directory" % PACKAGE_DIRNAME)
    if area == "package":
        parent = package_dir
        leaf = package_id
    elif area == "staging":
        parent = os.path.join(package_dir, PACKAGE_STAGING_DIRNAME)
        leaf = package_id
    elif area == "restore":
        parent = os.path.join(package_dir, PACKAGE_RESTORE_DIRNAME)
        leaf = package_id
    else:
        raise PackageError("package.invalid_area",
                           "unknown package workspace area %r" % area)
    if os.path.lexists(parent) and os.path.islink(parent):
        raise PackageError(
            "package.symlink_payload",
            "%s is a symbolic link; package staging must stay inside the "
            "approved root" % os.path.relpath(parent, root))
    if os.path.lexists(parent) and not os.path.isdir(parent):
        raise PackageError("package.not_found",
                           "%s is not a directory"
                           % os.path.relpath(parent, root))
    return os.path.join(parent, leaf)


def publish_directory(root, staging, destination):
    """Publish without replacing a raced destination, with pinned parents.

    Python exposes a no-replace directory rename on Windows. POSIX needs
    the platform's renameat variant. Unsupported kernels fail closed.
    """
    root = os.path.realpath(root)
    relative = os.path.relpath(destination, root).replace(os.sep, "/")
    if not _valid_relpath(relative):
        raise PackageError("package.path_escape", "publication must stay below the workspace")
    parent, leaf = os.path.split(relative)
    with _directory_handle(root, parent) as target_dir:
        with _directory_handle(os.path.dirname(staging)) as source_dir:
            if os.name == "nt":
                try:
                    os.rename(staging, destination)
                except FileExistsError as err:
                    raise PackageError("package.destination_exists",
                                       "the destination appeared before publication and was preserved") from err
                return
            libc = ctypes.CDLL(None, use_errno=True)
            if sys.platform == "darwin" and hasattr(libc, "renameatx_np"):
                rename = libc.renameatx_np
                flag = 0x00000004  # RENAME_EXCL, never replace a destination.
            elif sys.platform.startswith("linux") and hasattr(libc, "renameat2"):
                rename = libc.renameat2
                flag = 1  # RENAME_NOREPLACE.
            else:
                raise PackageError("package.atomic_publish_unsupported",
                                   "this platform has no supported no-replace directory rename")
            rename.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int,
                               ctypes.c_char_p, ctypes.c_uint]
            rename.restype = ctypes.c_int
            if rename(source_dir, os.fsencode(os.path.basename(staging)),
                      target_dir, os.fsencode(leaf), flag):
                error = ctypes.get_errno()
                if error in (errno.EEXIST, errno.ENOTEMPTY):
                    raise PackageError("package.destination_exists",
                                       "the destination appeared before publication and was preserved")
                raise PackageError("package.publication_failed",
                                   "no-replace publication failed: %s" % os.strerror(error))


def ensure_package_namespace(root):
    """Create the fixed namespace through its approved parent handle."""
    root = os.path.realpath(root)
    with _directory_handle(root) as directory:
        try:
            if os.name == "nt":
                os.mkdir(os.path.join(directory, PACKAGE_DIRNAME))
            else:
                os.mkdir(PACKAGE_DIRNAME, mode=0o700, dir_fd=directory)
        except FileExistsError:
            pass
    with _directory_handle(root, PACKAGE_DIRNAME):
        pass


@contextlib.contextmanager
def private_stage(root):
    """Keep unfinished writes in an exclusive, owner-only workspace stage."""
    with tempfile.TemporaryDirectory(prefix=".package-stage-", dir=os.path.realpath(root)) as stage:
        content = os.path.join(stage, "content")
        os.mkdir(content, mode=0o700)
        yield content


def _valid_relpath(relpath):
    if not isinstance(relpath, str) or not relpath or "\x00" in relpath or \
            "\\" in relpath or ntpath.splitdrive(relpath)[0]:
        return False
    if os.path.isabs(relpath) or relpath.startswith("/"):
        return False
    parts = relpath.split("/")
    return all(part not in ("", ".", "..") for part in parts)


def validate_manifest(manifest, expected_package_id=None, restore_dest=None):
    """Validate the frozen manifest shape before any restore-side write."""
    if not isinstance(manifest, dict) or not set(MANIFEST_KEYS) <= set(manifest) or \
            set(manifest) - set(MANIFEST_KEYS) - set(MANIFEST_OPTIONAL_KEYS):
        raise PackageError(
            "package.invalid_manifest",
            "the package manifest needs the required keys %s and permits "
            "only the optional keys %s"
            % (", ".join(MANIFEST_KEYS), ", ".join(MANIFEST_OPTIONAL_KEYS)))
    if manifest.get("schema_version") != PACKAGE_SCHEMA_VERSION:
        raise PackageError(
            "package.invalid_manifest",
            "package schema version %r is not supported"
            % manifest.get("schema_version"))
    if "evidence_fingerprint" in manifest and (
            not isinstance(manifest["evidence_fingerprint"], str) or
            not _FINGERPRINT_RE.fullmatch(manifest["evidence_fingerprint"])):
        raise PackageError("package.invalid_manifest",
                           "the evidence fingerprint must be a sha256 digest")
    package_id = validate_package_id(manifest.get("package_id"))
    if expected_package_id is not None and package_id != expected_package_id:
        raise PackageError(
            "package.id_mismatch",
            "package %s contains a manifest for %s; package identity is not "
            "inferred from a directory name" % (expected_package_id, package_id))
    if not isinstance(manifest.get("created"), str) or not manifest["created"]:
        raise PackageError("package.invalid_manifest",
                           "the package manifest needs a created timestamp")
    course_object_id = manifest.get("course_object_id")
    if not isinstance(course_object_id, str) or not _OBJECT_ID_RE.fullmatch(
            course_object_id):
        raise PackageError("package.invalid_manifest",
                           "the course object id is not a valid opaque id")
    if manifest.get("state") not in PACKAGE_STATES:
        raise PackageError(
            "package.invalid_manifest",
            "package state %r is not one of %s"
            % (manifest.get("state"), ", ".join(PACKAGE_STATES)))

    entries = manifest.get("entries")
    if not isinstance(entries, list) or not entries:
        raise PackageError("package.invalid_manifest",
                           "the package manifest needs at least one entry")
    seen_ids, seen_paths, course_entries = set(), set(), []
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != set(MANIFEST_ENTRY_KEYS):
            raise PackageError(
                "package.invalid_manifest",
                "every manifest entry must carry exactly these keys: %s"
                % ", ".join(MANIFEST_ENTRY_KEYS))
        object_id = entry.get("object_id")
        if not isinstance(object_id, str) or not _OBJECT_ID_RE.fullmatch(object_id):
            raise PackageError("package.invalid_manifest",
                               "manifest entry object id %r is invalid"
                               % object_id)
        kind = entry.get("kind")
        if kind not in PACKAGED_KINDS:
            raise PackageError("package.invalid_manifest",
                               "manifest entry %s has unsupported kind %r"
                               % (object_id, kind))
        revision = entry.get("revision")
        if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
            raise PackageError("package.invalid_manifest",
                               "manifest entry %s has invalid revision"
                               % object_id)
        relpath = entry.get("relpath")
        if not _valid_relpath(relpath):
            raise PackageError(
                "package.path_escape",
                "the package entry %r is not a safe relative path; refused, "
                "never clamped" % relpath)
        first_component = relpath.split("/", 1)[0].split(":", 1)[0].rstrip(" .").casefold()
        if first_component in (journal.JOURNAL_DIRNAME.casefold(),
                               evidence.EVIDENCE_DIRNAME.casefold()):
            raise PackageError(
                "package.reserved_path",
                "manifest payloads cannot write runtime-owned journal or "
                "evidence paths, which have their own restore authority")
        if relpath in seen_paths:
            raise PackageError(
                "package.duplicate_relpath",
                "two manifest entries claim the same payload path %s; refused"
                % relpath)
        seen_paths.add(relpath)
        if object_id in seen_ids:
            raise PackageError("package.duplicate_object_id",
                               "manifest object id %s appears twice" % object_id)
        seen_ids.add(object_id)
        if restore_dest is not None:
            safe_target(restore_dest, relpath)
        if not isinstance(entry.get("fingerprint"), str) or not \
                _FINGERPRINT_RE.fullmatch(entry["fingerprint"]):
            raise PackageError("package.invalid_manifest",
                               "manifest entry %s has invalid fingerprint"
                               % object_id)
        if object_id == course_object_id:
            course_entries.append(entry)
    if len(course_entries) != 1 or course_entries[0]["kind"] != "course":
        raise PackageError(
            "package.invalid_manifest",
            "the manifest must contain exactly one course-kind entry whose "
            "object id matches course_object_id")

    losses = manifest.get("loss_report")
    if not isinstance(losses, list):
        raise PackageError("package.invalid_manifest",
                           "the package loss report must be an array")
    for row in losses:
        if not isinstance(row, dict) or set(row) != set(LOSS_ROW_KEYS):
            raise PackageError(
                "package.invalid_manifest",
                "every loss row must carry exactly category, target, reason")
        if row.get("category") not in LOSS_CATEGORIES:
            raise PackageError("package.invalid_manifest",
                               "unknown package loss category %r"
                               % row.get("category"))
        if not isinstance(row.get("target"), str) or not row["target"] or \
                not isinstance(row.get("reason"), str) or not row["reason"]:
            raise PackageError("package.invalid_manifest",
                               "every package loss needs a target and reason")
    return manifest


def _reject_symlink_tree(package_root):
    """Refuse every symbolic link in an untrusted plain-directory package."""
    if os.path.islink(package_root):
        raise PackageError("package.symlink_payload",
                           "the package root is a symbolic link; refused")
    if not os.path.isdir(package_root):
        raise PackageError("package.not_found",
                           "package %s is not a readable directory"
                           % os.path.basename(package_root))
    for dirpath, dirnames, filenames in os.walk(package_root, followlinks=False):
        for name in list(dirnames) + list(filenames):
            path = os.path.join(dirpath, name)
            if os.path.islink(path):
                raise PackageError(
                    "package.symlink_payload",
                    "the package entry %s is a symbolic link; a package "
                    "payload carries files only"
                    % os.path.relpath(path, package_root).replace(os.sep, "/"))


def read_validated_manifest(package_root, expected_package_id=None,
                            restore_dest=None):
    """Read and strictly validate one untrusted plain-directory package."""
    _reject_symlink_tree(package_root)
    manifest = read_manifest(package_root)
    return validate_manifest(manifest, expected_package_id, restore_dest)


def manifest_bytes_digest(package_root):
    """The lowercase sha256 of the exact manifest bytes used for staging."""
    path = os.path.join(package_root, MANIFEST_FILENAME)
    if os.path.islink(path):
        raise PackageError("package.symlink_payload",
                           "the package manifest is a symbolic link; refused")
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


@contextlib.contextmanager
def _directory_handle(root, relpath=""):
    """Pin each directory component without following package-owned links."""
    parts = relpath.replace(os.sep, "/").split("/") if relpath else []
    if any(p in ("", ".", "..") for p in parts):
        raise PackageError("package.path_escape", "invalid directory path")
    if os.name == "nt":
        path = root
        # Directory handles deny delete sharing, which prevents a checked
        # namespace being renamed or replaced while Windows path APIs use it.
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        create = kernel.CreateFileW
        create.argtypes = [ctypes.c_wchar_p, ctypes.c_uint32, ctypes.c_uint32,
                           ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32,
                           ctypes.c_void_p]
        create.restype = ctypes.c_void_p
        close = kernel.CloseHandle
        close.argtypes = [ctypes.c_void_p]
        close.restype = ctypes.c_int
        handles = []
        try:
            for part in [""] + parts:
                path = os.path.join(path, part) if part else path
                handle = create(path, 0x80, 1, None, 3, 0x02200000, None)
                if handle == ctypes.c_void_p(-1).value:
                    raise PackageError("package.directory_unavailable",
                                       "the package directory could not be pinned safely")
                handles.append(handle)
                info = os.lstat(path)
                if not stat.S_ISDIR(info.st_mode) or getattr(info, "st_reparse_tag", 0):
                    raise PackageError("package.symlink_payload",
                                       "a package directory is a link or junction")
            yield path
        finally:
            for handle in reversed(handles):
                close(handle)
        return
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    fd = None
    try:
        fd = os.open(root, flags)
        for part in parts:
            child = os.open(part, flags, dir_fd=fd)
            os.close(fd)
            fd = child
        yield fd
    except OSError as err:
        if err.errno in (errno.ELOOP, errno.ENOTDIR):
            raise PackageError("package.symlink_payload",
                               "a package directory changed or became a link") from err
        raise
    finally:
        if fd is not None:
            os.close(fd)


def _read_relative(directory, relpath):
    """Read a regular file through a pinned directory, never a symlink."""
    parts = relpath.split("/")
    if not _valid_relpath(relpath):
        raise PackageError("package.path_escape", "invalid payload path")
    if os.name == "nt":
        path = os.path.join(directory, *parts)
        with _directory_handle(directory, "/".join(parts[:-1])):
            before = os.lstat(path)
            if not stat.S_ISREG(before.st_mode) or getattr(before, "st_reparse_tag", 0):
                raise PackageError("package.symlink_payload", "payload is not a regular file")
            with open(path, "rb") as fh:
                opened = os.fstat(fh.fileno())
                if not os.path.samestat(before, opened):
                    raise PackageError("package.stale_payload", "payload changed before opening")
                raw = fh.read(MAX_ENTRY_BYTES + 1)
            if not os.path.samestat(before, opened) or not os.path.samestat(
                    opened, os.lstat(path)):
                raise PackageError("package.stale_payload", "payload changed while being read")
    else:
        fd = os.dup(directory)
        try:
            for part in parts[:-1]:
                child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                dir_fd=fd)
                os.close(fd)
                fd = child
            file_fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                              dir_fd=fd)
            with os.fdopen(file_fd, "rb") as fh:
                if not stat.S_ISREG(os.fstat(fh.fileno()).st_mode):
                    raise PackageError("package.symlink_payload", "payload is not a regular file")
                raw = fh.read(MAX_ENTRY_BYTES + 1)
        except OSError as err:
            if err.errno in (errno.ELOOP, errno.ENOTDIR):
                raise PackageError("package.symlink_payload", "payload became a link") from err
            raise
        finally:
            os.close(fd)
    if len(raw) > MAX_ENTRY_BYTES:
        raise PackageError("package.payload_too_large", "payload exceeds the package size limit")
    return raw


def _digest(raw):
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def package_snapshot(package_root, expected_package_id=None, workspace_root=None):
    """Capture and verify the exact bytes a restore is allowed to consume.

    The handle anchors reads even if the package path is replaced afterward.
    No restore write reopens a mutable input pathname.
    """
    anchor = os.path.realpath(workspace_root) if workspace_root else os.path.dirname(
        os.path.abspath(package_root))
    relative = os.path.relpath(os.path.abspath(package_root), anchor).replace(os.sep, "/")
    _reject_symlink_tree(package_root)
    with _directory_handle(anchor, relative) as directory:
        try:
            manifest_raw = _read_relative(directory, MANIFEST_FILENAME)
        except FileNotFoundError as err:
            raise PackageError("package.not_applied", "the package manifest is absent") from err
        try:
            manifest = json.loads(manifest_raw)
        except (ValueError, UnicodeError) as err:
            raise PackageError("package.manifest_unreadable", "the manifest is not valid JSON") from err
        validate_manifest(manifest, expected_package_id)
        verified, payloads, missing, mismatches = 0, {}, [], []
        for entry in manifest["entries"]:
            try:
                raw = _read_relative(directory, _payload_relpath(entry))
            except FileNotFoundError:
                missing.append({"object_id": entry["object_id"],
                                "relpath": entry["relpath"],
                                "payload": _payload_relpath(entry)})
                continue
            found = identity.object_fingerprint(raw, entry["kind"])
            if found != entry["fingerprint"]:
                mismatches.append({"object_id": entry["object_id"],
                                   "expected": entry["fingerprint"], "found": found})
            else:
                verified += 1
                payloads[entry["object_id"]] = raw
        evidence_path = EVIDENCE_DIRNAME + "/" + EVIDENCE_FILENAME
        try:
            evidence_raw = _read_relative(directory, evidence_path)
        except FileNotFoundError:
            evidence_raw = None
        expected = manifest.get("evidence_fingerprint")
        rows = []
        if expected is None and evidence_raw:
            raise PackageError("package.evidence_unbound",
                               "legacy evidence has no manifest digest, so it cannot be restored")
        if expected is not None and evidence_raw is None:
            missing.append({"object_id": "evidence", "relpath": evidence_path,
                            "payload": evidence_path})
        elif expected is not None and _digest(evidence_raw) != expected:
            mismatches.append({"object_id": "evidence", "expected": expected,
                               "found": _digest(evidence_raw)})
        elif evidence_raw:
            rows = _validated_evidence_events(evidence_raw)
        report = {"entries_verified": verified, "mismatches": mismatches,
                  "missing": missing,
                  "complete": verified == len(manifest["entries"]) and not missing and not mismatches}
        return {"manifest": manifest, "manifest_raw": manifest_raw,
                "payloads": payloads, "evidence": rows, "verification": report}


def _payload_relpath(entry):
    """Where one object's bytes live inside the package.

    Named by `object_id`, never by content: two byte-identical sources under
    two ids are two objects, so they get two payload files and are never
    deduplicated into one (ID-02).
    """
    return "/".join((PAYLOAD_DIRNAME, entry["object_id"] + ".md"))


def _externally_owned(base):
    """The ids whose FIRST applied journal entry was a `link` and which the
    owner has not adopted.

    Read from the journal rather than from the registry's latest row on
    purpose: the registry projects the most recent operation, so recording a
    rights grant on a linked source would otherwise erase the fact that it
    was linked. What makes an object external is how it entered the course,
    which only the journal remembers.

    An adopted object (`journal.op_adopt`) is the one exception, and it is
    not an exception to the rule so much as an answer to it: the owner has
    recorded that the bound file is the course's own artifact rather than
    someone else's file kept where it lives, so packaging it copies nothing
    out of anyone else's control (`17B-04 D-06 item 10`).
    """
    adopted = journal.adopted_ids(base)
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
    return linked - adopted


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

    # The evidence axis is reported in the same loss report as the file
    # axis: a package whose payloads all crossed and whose events all
    # vanished is not a complete package, and before `17B-04 D-06 item 11`
    # nothing said so.
    _carried, evidence_losses = evidence_export_lines(
        course_root, evidence_scope(base, course_root))
    losses.extend(evidence_losses)
    losses.extend(unregistered_file_losses(base, course_root, registry))
    losses.extend(provenance_losses(base))

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


# Directories inside a course root this walk never reports: the journal has
# its own loss row, the evidence store is exported beside the payload, and
# neither is an unbound file a person put there.
UNREGISTERED_SKIP_DIRS = ("_journal", "_evidence")


def unregistered_file_losses(base, course_root, registry):
    """One loss row per file inside `course_root` that no registry object
    binds.

    A package carries registry objects, so an unbound file is invisible to
    it: the exporter cannot see it, which is a different claim from the
    learner not needing it (`17C-AUDIT.md` F-LOSS-4). The row is the
    difference between the two, and it is what stops a restored course
    reading complete while a bank's cited media is missing (F-LOSS-5).
    """
    root = os.path.abspath(course_root)
    if not os.path.isdir(root):
        return []
    bound = set()
    for row in registry.values():
        path = row.get("path")
        if path:
            bound.add(os.path.normpath(
                os.path.join(os.path.abspath(base), path)))
    rows = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames
                             if d not in UNREGISTERED_SKIP_DIRS)
        for name in sorted(filenames):
            full = os.path.normpath(os.path.join(dirpath, name))
            if full in bound:
                continue
            rows.append(_loss_row(
                "unregistered-file",
                os.path.relpath(full, root).replace(os.sep, "/"),
                LOSS_REASONS["unregistered-file"]))
    return rows


def provenance_losses(base):
    """The one row saying the operation journal does not travel.

    Reported once, with the count of applied entries left behind, rather
    than per object: it is one fact about the package, not a property of
    any single artifact (`17C-AUDIT.md` F-LOSS-1 and F-LOSS-2).
    """
    try:
        applied = sum(1 for entry in journal.entries(base)
                      if entry.get("state") == "applied")
    except Exception:
        return []
    if not applied:
        return []
    return [_loss_row("provenance-not-carried", journal.LOG_FILENAME,
                      LOSS_REASONS["provenance-not-carried"] % applied)]


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


def evidence_scope(base, course_root):
    """What this course can claim in an evidence log: its objective ids, the
    bank names its own registry rows carry, and (filled in per log) the
    sessions those two identify.

    `17B-04 D-06 item 11`: the sidecar's `## Objectives` `id` column holds
    graph object ids while an evidence event's `objective` field holds a bank
    slug such as `afe:unit3.threshold`. The two vocabularies never intersect,
    so an objective-id filter alone exported nothing. A bank name is the join
    that actually exists on both sides today, and it is read from the registry
    rather than guessed from a filename.
    """
    banks = set()
    try:
        registry = journal.read_registry(base)
    except Exception:
        registry = {}
    for row in registry.values():
        if row.get("kind") != "bank":
            continue
        path = row.get("path") or ""
        if path:
            banks.add(path)
            banks.add(os.path.basename(path))
    return {"objectives": _course_objective_ids(course_root), "banks": banks}


def _event_claimed(event, scope, sessions):
    bank = event.get("bank")
    if bank and (bank in scope["banks"]
                 or os.path.basename(bank) in scope["banks"]):
        return True
    if event.get("objective") in scope["objectives"]:
        return True
    session = event.get("session_id")
    return bool(session) and session in sessions


def evidence_export_lines(course_root, scope):
    """The events this course can claim, one JSON object per line in log
    order, plus one loss row per unclaimed group.

    Two passes on purpose. The first identifies every session a claimed
    event names; the second carries the whole of those sessions, because a
    mark, a hint, and a selection are the same sitting as the response they
    resolve and carry no bank or objective of their own. Anything still
    unclaimed is named in the loss report rather than dropped, so a shared
    evidence store still never exports another course's history and a
    restore can tell "no evidence" from "evidence missing".
    """
    log = evidence.log_path(course_root)
    if not os.path.exists(log):
        return [], []
    events = list(evidence.events(log))

    sessions = set()
    for event in events:
        if _event_claimed(event, scope, sessions=set()):
            session = event.get("session_id")
            if session:
                sessions.add(session)

    out, unclaimed = [], []
    for event in events:
        if _event_claimed(event, scope, sessions):
            out.append(json.dumps(event, ensure_ascii=False, sort_keys=True))
        else:
            unclaimed.append(event)

    losses = []
    if unclaimed:
        scoped_by = sorted(set(
            str(e.get("bank") or e.get("objective") or e.get("session_id")
                or "no bank, objective, or session")
            for e in unclaimed))
        losses.append(_loss_row(
            "evidence-not-carried", EVIDENCE_FILENAME,
            LOSS_REASONS["evidence-not-carried"]
            % (len(unclaimed), ", ".join(scoped_by))))
    return out, losses


def _evidence_export_lines(course_root, scope):
    lines, _losses = evidence_export_lines(course_root, scope)
    return lines


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


@contextlib.contextmanager
def export_guard(base, course_root):
    """Use the same locks as canonical writers while capturing and publishing."""
    with journal._journal_lock(base):
        log = evidence.log_path(course_root)
        with contextlib.ExitStack() as stack:
            if os.path.exists(log):
                fh = stack.enter_context(open(log, "rb"))
                stack.enter_context(evidence.locked(fh.fileno()))
            yield


def capture_export(base, course_root, expected_fingerprint=None, manifest=None):
    """Capture payloads, rights, evidence and loss inputs under export_guard."""
    current = build_manifest(base, course_root)
    course_entry = next(
        e for e in current["entries"]
        if e["object_id"] == current["course_object_id"])
    if expected_fingerprint is not None and course_entry["fingerprint"] != expected_fingerprint:
        raise PackageError("package.stale_course", "the course changed before export capture")
    if manifest is not None:
        validate_manifest(manifest)
        for key in ("entries", "loss_report", "course_object_id"):
            if manifest[key] != current[key]:
                raise PackageError("package.stale_course", "the export inputs changed since planning")
        current["package_id"] = manifest["package_id"]
        current["created"] = manifest["created"]
    payloads = {}
    for entry in current["entries"]:
        root = (course_root if entry["object_id"] == current["course_object_id"]
                else base)
        with _directory_handle(os.path.realpath(root)) as directory:
            raw = _read_relative(directory, entry["relpath"])
        if identity.object_fingerprint(raw, entry["kind"]) != entry["fingerprint"]:
            raise PackageError("package.fingerprint_mismatch",
                               "source bytes differ from the accepted export revision")
        payloads[entry["object_id"]] = raw
    lines, losses = evidence_export_lines(course_root, evidence_scope(base, course_root))
    if losses != [r for r in current["loss_report"] if r["category"] == "evidence-not-carried"]:
        raise PackageError("package.stale_course", "evidence losses changed during capture")
    raw = (("\n".join(lines) + "\n") if lines else "").encode("utf-8")
    _validated_evidence_events(raw)
    current["evidence_fingerprint"] = _digest(raw)
    return {"manifest": current, "payloads": payloads, "evidence_raw": raw}


def recheck_export(base, course_root, snapshot):
    """Refuse changes to any inclusion, rights, evidence or loss input."""
    current = capture_export(base, course_root, manifest=snapshot["manifest"])
    if current["payloads"] != snapshot["payloads"] or \
            current["evidence_raw"] != snapshot["evidence_raw"]:
        raise PackageError("package.stale_course", "the export snapshot changed before publication")


def export_package(base, course_root, dest, archive=None, manifest=None, _snapshot=None):
    """Capture under writer locks, then emit and verify one coherent export."""
    if _snapshot is not None:
        return _export_package(base, course_root, dest, archive, _snapshot)
    with export_guard(base, course_root):
        snapshot = capture_export(base, course_root, manifest=manifest)
        return _export_package(base, course_root, dest, archive, snapshot)


def _export_package(base, course_root, dest, archive, snapshot):
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
    manifest = dict(snapshot["manifest"])
    validate_manifest(manifest)
    entries = manifest.get("entries", [])
    _check_duplicate_relpaths(entries)

    os.makedirs(os.path.join(dest, PAYLOAD_DIRNAME), exist_ok=True)
    os.makedirs(os.path.join(dest, EVIDENCE_DIRNAME), exist_ok=True)

    manifest["state"] = "prepared"
    manifest_path = os.path.join(dest, MANIFEST_FILENAME)
    _write_json(manifest_path, manifest)

    for entry in entries:
        raw = snapshot["payloads"][entry["object_id"]]
        _write_bytes_atomic(os.path.join(dest, _payload_relpath(entry)), raw)

    _write_bytes_atomic(
        os.path.join(dest, EVIDENCE_DIRNAME, EVIDENCE_FILENAME),
        snapshot["evidence_raw"])

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

    with _directory_handle(os.path.realpath(dest)) as directory:
        written_evidence = _read_relative(directory, EVIDENCE_DIRNAME + "/" + EVIDENCE_FILENAME)
    if _digest(written_evidence) != manifest["evidence_fingerprint"]:
        raise PackageError("package.fingerprint_mismatch",
                           "the written evidence differs from the export snapshot")

    recheck_export(base, course_root, snapshot)
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
    return package_snapshot(package_root)["verification"]


def restore_package(package_root, dest, actor_kind, actor_name, _snapshot=None):
    """Restore a package into `dest` and report what was verified.

    `dest` needs no shared journal, no shared registry, and no shared
    evidence store: a restore mints the destination's own journal as it
    writes, which is what makes a clean-machine restore a real one.

    Two loss lists come back and neither replaces the other: `losses` is the
    export-time report copied from the manifest, and `restore_losses` is what
    this restore itself could not carry.
    """
    snapshot = _snapshot if _snapshot is not None else package_snapshot(package_root)
    manifest = snapshot["manifest"]
    validate_manifest(manifest, restore_dest=dest)
    state = manifest.get("state")
    if state != "applied":
        raise PackageError(
            "package.not_applied",
            "this package's manifest state is %s, not applied; it was "
            "interrupted during export and must not be restored" % state)

    entries = manifest.get("entries", [])
    _check_duplicate_relpaths(entries)

    report = snapshot["verification"]
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
        raw = snapshot["payloads"][entry["object_id"]]
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

    recorded, already = _restore_evidence(snapshot["evidence"], dest)

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


def _restore_evidence(events, dest):
    """Append every exported event into the destination's own evidence log
    through `evidence.append_event`, the one evidence writer.

    No second evidence store is created here and none may ever be. The one
    writer already answers `recorded` versus `already_recorded`, so counting
    its answers makes a second restore of the same package idempotent for
    free rather than by a dedupe rule invented in this module.
    """
    log = evidence.log_path(dest)
    recorded, already = 0, 0
    for event in events:
        answer = evidence.append_event(log, event)
        if answer.get("status") == "recorded":
            recorded += 1
        else:
            already += 1
    return recorded, already


def _validated_evidence_events(raw):
    """Read every carried evidence row before restore mutation begins."""
    with open(os.path.join(os.path.dirname(__file__), "schemas",
                           "response.schema.json"), encoding="utf-8") as fh:
        schema = json.load(fh)
    try:
        text = raw.decode("utf-8")
    except UnicodeError as err:
        raise PackageError("package.evidence_unreadable", "evidence is not UTF-8") from err
    rows = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except ValueError as err:
            raise PackageError(
                "package.evidence_unreadable",
                "evidence export line %d is not valid JSON: %s"
                % (lineno, err))
        errors = schema_validate.validate(event, schema)
        if not errors and (event.get("event_type") not in evidence.KNOWN_EVENT_TYPES or
                           not 1 <= event["schema_version"] <= evidence.EVENT_SCHEMA_VERSION):
            errors = ["the evidence runtime does not support this event type or version"]
        if errors:
            raise PackageError(
                "package.evidence_invalid",
                "evidence export line %d fails the evidence schema: %s"
                % (lineno, "; ".join(errors)))
        rows.append(event)
    return rows


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
