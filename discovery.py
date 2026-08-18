"""The read-only multi-root discovery walker.

This module is read-only by construction: it opens no file for writing,
spawns no process, and makes no network request. Finding a file grants no
authority to transmit, transform, execute, or modify it (FILE-02). The
module deliberately does not import `journal`, `subprocess`, or `urllib`, so
the read-only property is structural rather than maintained by care -- a
caller can assert `not hasattr(discovery, "journal")` and trust it.

`inventory()` walks only inside the approved roots it is given, yields
results before the walk completes, stops within one directory of a cancel
signal, and can resume after a named relative path. `run_report()` drains it
into a single summary dict.
"""
import os

import identity

DISCOVERY_SCHEMA_VERSION = 1

ENTRY_STATES = ("readable", "denied", "symlink_out_of_root", "symlink_cycle",
                 "unavailable")


class DiscoveryError(Exception):
    """A typed discovery failure. Machine-readable `code` plus message."""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message


def _root_unapproved_error(path):
    return DiscoveryError(
        "discovery.root_unapproved",
        "%s is outside every approved root; discovery refuses to read it"
        % path)


def inside_any_root(path, roots):
    """True only when `path` is genuinely contained inside one of `roots`,
    resolved through symlinks so an escape via a link is never mistaken for
    containment."""
    real_path = os.path.realpath(path)
    for root in roots:
        real_root = os.path.realpath(root)
        try:
            common = os.path.commonpath([real_path, real_root])
        except ValueError:
            # Different drives on Windows: never the same tree.
            continue
        if common == real_root:
            return True
    return False


def _relpath(root, path):
    return os.path.relpath(path, root).replace(os.sep, "/")


def _entry(root, path, state, size=None, fingerprint=None, note=""):
    return {
        "root": root,
        "path": _relpath(root, path),
        "state": state,
        "size": size,
        "fingerprint": fingerprint,
        "note": note,
    }


def _walk_one_root(root, roots):
    """Yield entry dicts for every path under `root`, in deterministic
    pre-order (each directory's own files before its subdirectories, both
    sorted), the walk's own natural order. No cancel or resume logic lives
    here; that is layered on top in `inventory()` so the walk order itself
    stays a single, simple source of truth.
    """
    visited_real_dirs = set()
    for dirpath, dirs, files in os.walk(root, followlinks=False):
        dirs.sort()
        files.sort()
        visited_real_dirs.add(os.path.realpath(dirpath))

        remaining_dirs = []
        for d in dirs:
            dpath = os.path.join(dirpath, d)
            if os.path.islink(dpath):
                real_target = os.path.realpath(dpath)
                if not inside_any_root(dpath, roots):
                    yield _entry(root, dpath, "symlink_out_of_root")
                elif real_target in visited_real_dirs:
                    yield _entry(root, dpath, "symlink_cycle")
                else:
                    # An in-root, non-cyclic directory symlink. This walker
                    # inventories files, not directory markers; os.walk's
                    # own followlinks=False already refuses to descend into
                    # it, so nothing further is reported for it here.
                    pass
                continue
            remaining_dirs.append(d)
        dirs[:] = remaining_dirs

        for f in files:
            fpath = os.path.join(dirpath, f)
            if os.path.islink(fpath):
                real_target = os.path.realpath(fpath)
                if not inside_any_root(fpath, roots):
                    yield _entry(root, fpath, "symlink_out_of_root")
                    continue
                if real_target in visited_real_dirs or not os.path.exists(fpath):
                    yield _entry(root, fpath, "symlink_cycle")
                    continue

            try:
                with open(fpath, "rb") as fh:
                    raw = fh.read()
            except (PermissionError, OSError) as exc:
                yield _entry(root, fpath, "denied", note=str(exc))
                continue

            fingerprint = identity.object_fingerprint(raw, "source")
            yield _entry(root, fpath, "readable", size=len(raw),
                         fingerprint=fingerprint)


def inventory(roots, cancel=None, resume_after=None):
    """Yield one entry dict per inventoried path, across every root in the
    order given.

    A root that does not exist or cannot be listed yields one `unavailable`
    entry and discovery moves on to the next root; it never raises out of
    this generator. A symlink is resolved and checked against `roots`
    before it is ever opened: an out-of-root target yields
    `symlink_out_of_root` and is never read, and a repeat real path yields
    `symlink_cycle` and is never descended into. An unreadable or
    permission-denied path yields `denied` and is never mutated.

    `resume_after` is the relative path of an entry from a previous,
    possibly-cancelled run of this same root list; entries up to and
    including it are skipped by exact match against the walk's own order,
    never by a string comparison that could disagree with that order.
    `cancel`, when it returns True, stops the generator before its next
    entry, within one directory of the signal.
    """
    resuming = resume_after is not None
    for root in roots:
        if not os.path.isdir(root):
            # An unavailable root has no path to match resume_after
            # against; it is reported once, the same as an uninterrupted run.
            yield {
                "root": root, "path": "", "state": "unavailable",
                "size": None, "fingerprint": None,
                "note": "%s does not exist or is not a directory" % root,
            }
            continue

        for entry in _walk_one_root(root, roots):
            if resuming:
                if entry["path"] == resume_after and entry["root"] == root:
                    resuming = False
                continue
            if cancel is not None and cancel():
                return
            yield entry


def run_report(roots, cancel=None, resume_after=None, approved_roots=None):
    """Drain `inventory()` into a single summary dict with keys `roots`,
    `entries`, `counts`, `complete`, `cancelled`, `denied`, `refused`,
    `unavailable`, and `omitted_reason`.

    `roots` are trusted as approved by default, the same way `inventory()`
    trusts them: a caller who has already screened `roots` against an
    approved-root registry need pass nothing else. `approved_roots`, when
    given, is a second, explicit check: every entry of `roots` must be
    `inside_any_root` of `approved_roots` or this function raises
    `DiscoveryError` with code `discovery.root_unapproved` before walking
    anything, so a caller that is not itself the source of truth for what is
    approved can still be refused rather than trusted blindly.
    """
    if approved_roots is not None:
        for root in roots:
            if not inside_any_root(root, approved_roots):
                raise _root_unapproved_error(root)

    entries = []
    counts = {state: 0 for state in ENTRY_STATES}
    denied = []
    refused = []
    unavailable = []
    last_path = None

    cancelled_box = {"hit": False}

    def _cancel_wrapper():
        if cancel is None:
            return False
        if cancel():
            cancelled_box["hit"] = True
            return True
        return False

    for entry in inventory(roots, cancel=_cancel_wrapper, resume_after=resume_after):
        entries.append(entry)
        counts[entry["state"]] = counts.get(entry["state"], 0) + 1
        if entry["state"] == "denied":
            denied.append(entry["path"])
        elif entry["state"] == "symlink_out_of_root":
            refused.append(entry["path"])
        elif entry["state"] == "unavailable":
            unavailable.append(entry["root"])
        else:
            last_path = entry["path"]

    cancelled = cancelled_box["hit"]
    complete = not cancelled
    omitted_reason = ""
    if cancelled:
        omitted_reason = ("cancelled by caller; the entries after %s were "
                           "not inventoried" % last_path)

    return {
        "roots": list(roots),
        "entries": entries,
        "counts": counts,
        "complete": complete,
        "cancelled": cancelled,
        "denied": denied,
        "refused": refused,
        "unavailable": unavailable,
        "omitted_reason": omitted_reason,
    }
