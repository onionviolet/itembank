#!/usr/bin/env python3
"""The Phase 11 transactional writer boundary (plan 11-01; Git backend and
recovery journal completed by plan 11-05).

One writer (`write_units`) is the only bank-mutation seam of the closed
authoring loop (D-15). It accepts only an immutable preflighted proposal
plus the expected bank fingerprint and rechecks both under its own control;
it never trusts caller attestation. This module implements the content-
addressed shadow path:

- deterministic write id derived from the proposal's provenance fields;
- a prepared manifest plus a SHA-256-addressed before-image persisted
  *before* any mutation, so an interruption cannot leave an unreported bank;
- same-directory temp file plus `os.replace` for atomic replacement;
- an after-fingerprint guard before the manifest is marked applied;
- one-step `undo(write_id)` that restores the exact before bytes only when
  the current fingerprint still equals the recorded after-image -- a stale
  or conflicting target refuses without any force path (T-11-17).

The Git backend (tracked-clean targets, one machine-authored commit per
accepted unit, `git revert` undo) joins in plan 11-05 behind the same
manifest/undo API; callers never choose a backend (D-15).
"""
import contextlib
import hashlib
import json
import os
import subprocess
import time

from authoring import WRITE_SCHEMA_VERSION, TOOL_VERSION, bank_fingerprint, \
    canonical_json

# The manifest directory names inside `state_dir`.
MANIFESTS_DIR = "manifests"
BEFORE_DIR = "before"

# The lock timeout: a concurrent writer that cannot acquire the per-bank OS
# lock within this many seconds gets an explicit writer.busy result (T-11-20).
LOCK_TIMEOUT_SECONDS = 10.0

# The in-repo manifest directory for Git-backend writes: the manifest is
# committed with the item so the machine-authored change is fully declared
# (D-15/D-16) and undo can route by it.
GIT_MANIFESTS_RELPATH = os.path.join(".itembank", "audit", "manifests")


@contextlib.contextmanager
def _bank_lock(state_dir):
    """The per-bank cross-platform OS lock (msvcrt on Windows, fcntl where
    available) held around fingerprint revalidation and mutation (T-11-18).
    Non-blocking acquire with a bounded timeout and an explicit busy error;
    never a silent fallback and never an unsafe stale-lock deletion."""
    os.makedirs(state_dir, exist_ok=True)
    lock_path = os.path.join(state_dir, "writer.lock")
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
                raise WriterError(
                    "writer.busy",
                    "another writer holds the per-bank lock for %s"
                    % lock_path)
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


def _git_repo_root(target_path):
    """The Git worktree root containing `target_path`, or None. Unlike
    _git_target this works regardless of the target's tracked/dirty state,
    so manifest lookup and undo routing still function for a dirty bank."""
    abspath = os.path.abspath(target_path)
    directory = os.path.dirname(abspath) or "."
    try:
        root = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"], cwd=directory,
            capture_output=True, text=True, timeout=10)
        if root.returncode != 0:
            return None
        return root.stdout.strip()
    except Exception:
        return None


def _git_target(target_path):
    """Detect the exact target's Git state under the lock: the repo root,
    tracked status, and staged/unstaged cleanliness at that exact path
    (T-11-18). Returns a dict {root, rel} when the target is tracked and
    clean -- the only case the Git backend may handle -- else None (shadow)."""
    # realpath, not abspath: `git rev-parse --show-toplevel` reports the
    # physical worktree root, so a symlinked path component in the target
    # (macOS /var -> /private/var, /tmp -> /private/tmp) would otherwise
    # produce a bogus ../.. relative path and misroute a tracked-clean
    # bank to the shadow backend.
    abspath = os.path.realpath(target_path)
    root = _git_repo_root(target_path)
    if root is None:
        return None
    rel = os.path.relpath(abspath, os.path.realpath(root))
    try:
        tracked = subprocess.run(
            ["git", "ls-files", "--error-unmatch", "--", rel],
            cwd=root, capture_output=True, text=True, timeout=10)
        if tracked.returncode != 0:
            return None
        status = subprocess.run(
            ["git", "status", "--porcelain", "--", rel],
            cwd=root, capture_output=True, text=True, timeout=10)
        if status.stdout.strip():
            return None  # staged or unstaged change -> shadow, never git
        return {"root": root, "rel": rel}
    except Exception:
        return None


def _git_manifest_dir(repo_root):
    return os.path.join(repo_root, GIT_MANIFESTS_RELPATH)


def _git_commit(git, rels, message):
    """Stage exactly the declared paths and create one machine-authored
    commit; returns the commit hash. Raises WriterError on failure so the
    prepared journal keeps the run visible and recoverable."""
    add = subprocess.run(["git", "add", "--"] + rels, cwd=git["root"],
                         capture_output=True, text=True, timeout=10)
    if add.returncode != 0:
        raise WriterError("git.stage_failed", add.stderr.strip())
    commit = subprocess.run(
        ["git", "commit", "-m", message], cwd=git["root"],
        capture_output=True, text=True, timeout=10)
    if commit.returncode != 0:
        raise WriterError("git.commit_failed", commit.stderr.strip())
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=git["root"],
                          capture_output=True, text=True, timeout=10)
    if head.returncode != 0:
        raise WriterError("git.commit_failed", head.stderr.strip())
    return head.stdout.strip()


def _git_revert(git, commit_hash):
    """Non-interactive git revert of the machine-authored commit; refuses
    when the bank path carries newer human work (T-11-17). The writer's own
    .itembank/audit metadata (the applied-state update, regenerable) is
    reset to the committed form first so it cannot conflict with the
    revert; human work on the bank is never touched."""
    status = subprocess.run(["git", "status", "--porcelain", "--",
                             git["rel"]],
                            cwd=git["root"], capture_output=True, text=True,
                            timeout=10)
    if status.stdout.strip():
        raise WriterError(
            "undo.git_dirty",
            "the bank path carries newer human work; refusing to revert the "
            "machine-authored commit (no force path)")
    subprocess.run(["git", "checkout", "--", GIT_MANIFESTS_RELPATH],
                   cwd=git["root"], capture_output=True, text=True,
                   timeout=10)
    revert = subprocess.run(["git", "revert", "--no-edit", commit_hash],
                            cwd=git["root"], capture_output=True, text=True,
                            timeout=30)
    if revert.returncode != 0:
        raise WriterError("undo.git_conflict", revert.stderr.strip())


class WriterError(Exception):
    """A typed writer failure: stale preflight, missing target, manifest
    corruption, a refused undo. Machine-readable `code` plus message."""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def _state_paths(state_dir):
    manifests = os.path.join(state_dir, MANIFESTS_DIR)
    before = os.path.join(state_dir, BEFORE_DIR)
    return manifests, before


def _ensure_dirs(state_dir):
    manifests, before = _state_paths(state_dir)
    os.makedirs(manifests, exist_ok=True)
    os.makedirs(before, exist_ok=True)
    return manifests, before


def _content_path(before_dir, fingerprint):
    """The content-addressed before-image path: the fingerprint IS the
    address, so identical banks share one image and a tampered image is
    detectable by name."""
    digest = fingerprint.split(":", 1)[-1]
    return os.path.join(before_dir, digest + ".bin")


def _manifest_path(manifests_dir, write_id):
    return os.path.join(manifests_dir, write_id + ".json")


def _read_manifest(manifests_dir, write_id):
    path = _manifest_path(manifests_dir, write_id)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict) or data.get("schema_version") != WRITE_SCHEMA_VERSION:
        raise WriterError("manifest.corrupt",
                          "manifest %s is missing or malformed" % write_id)
    return data


def _write_json(path, data):
    """The repository's UTF-8, pretty JSON, trailing newline, tmp-then-
    replace convention (runtime.py:178-185)."""
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    os.replace(tmp, path)


def _read_bytes(path):
    with open(path, "rb") as fh:
        return fh.read()


def _write_bytes_atomic(path, raw):
    tmp = path + ".tmp"
    with open(tmp, "wb") as fh:
        fh.write(raw)
    os.replace(tmp, path)


def deterministic_write_id(proposal):
    """The write id derives from the proposal's provenance fields (D-17,
    T-11-05, plan 11-04): request, bank-before, source fingerprints,
    profile, quality profile, and tool version -- explicitly NOT the minted
    unit ids, so two independent runs of the same bounded request produce
    the same write id and a duplicate write returns the existing result
    instead of mutating again."""
    identity = {
        "request_fingerprint": proposal["request_fingerprint"],
        "bank_before_fingerprint": proposal["bank_before_fingerprint"],
        "source_fingerprints": proposal["source_fingerprints"],
        "profile": proposal.get("profile", ""),
        "quality_profile": proposal.get("quality_profile", ""),
        "tool_version": proposal.get("tool_version", TOOL_VERSION),
    }
    digest = hashlib.sha256(
        canonical_json(identity).encode("utf-8")).hexdigest()
    return "w-" + digest[:32]


def write_units(proposal, target_path, state_dir, expected_fingerprint=None,
                create_if_missing=False):
    """Atomically apply one preflighted unit through the Git or shadow
    backend (D-15/D-16, plan 11-05 Task 3).

    Under the per-bank OS lock it rechecks the expected bank fingerprint
    (AUTH-02/T-11-02): a mismatch refuses with `stale_preflight` and never
    mutates. A tracked+clean target in a Git worktree uses the Git backend
    (one machine-authored commit per accepted unit plus its manifest);
    every other target uses the content-addressed shadow backend (durable
    before-image + prepared manifest before tmp-plus-os.replace, with an
    after-fingerprint guard). `create_if_missing` allows a newly created
    derived report artifact with `before_exists: false`.

    A duplicate write id (same proposal already applied and still matching)
    returns the existing manifest without a second mutation (AUTH-01)."""
    if not isinstance(proposal, dict) or not proposal.get("bank_after_text"):
        raise WriterError("writer.proposal_invalid",
                          "writer requires an immutable preflighted proposal")
    write_id = deterministic_write_id(proposal)
    with _bank_lock(state_dir):
        exists = os.path.exists(target_path)
        if not exists and not create_if_missing:
            raise WriterError("writer.target_missing",
                              "target bank %s does not exist" % target_path)
        before_raw = _read_bytes(target_path) if exists else b""
        before_fp = bank_fingerprint(
            before_raw.decode("utf-8")) if exists else ""
        if expected_fingerprint is not None and before_fp != expected_fingerprint:
            raise WriterError(
                "writer.stale_preflight",
                "current bank fingerprint %s does not match the preflighted "
                "%s; the bank changed since the proposal was built"
                % (before_fp, expected_fingerprint))

        manifests, before = _ensure_dirs(state_dir)

        # idempotent duplicate: the same provenance-derived write id already
        # applied and still matching the target returns the existing manifest
        existing = _find_manifest_anywhere(write_id, target_path, state_dir)
        if existing is not None:
            current_fp = bank_fingerprint(
                _read_bytes(target_path).decode("utf-8")) if exists else ""
            if existing.get("state") == "applied" and \
                    existing.get("after_fingerprint") == current_fp:
                return existing
            raise WriterError(
                "writer.duplicate_conflict",
                "write %s already exists but its after-fingerprint no longer "
                "matches the target; refusing to reapply" % write_id)

        git = _git_target(target_path) if exists else None
        if git is not None:
            return _write_git(proposal, target_path, state_dir, git, before_fp)
        return _write_shadow(proposal, target_path, state_dir, before_fp,
                             before_raw, create_if_missing)


def _write_shadow(proposal, target_path, state_dir, before_fp, before_raw,
                  create_if_missing):
    """The content-addressed shadow backend: durable before-image + prepared
    manifest before any mutation, tmp-plus-os.replace, after-fingerprint
    guard (T-11-02)."""
    write_id = deterministic_write_id(proposal)
    manifests, before = _ensure_dirs(state_dir)
    manifest_path = _manifest_path(manifests, write_id)
    before_exists = bool(before_raw)

    manifest = {
        "schema_version": WRITE_SCHEMA_VERSION,
        "write_id": write_id,
        "run_id": proposal.get("run_id", ""),
        "backend": "shadow",
        "state": "prepared",
        "target_path": os.path.abspath(target_path),
        "units": proposal.get("units", []),
        "before_fingerprint": before_fp,
        "before_image": _content_path(before, before_fp) if before_exists
        else "",
        "before_exists": before_exists,
        "after_fingerprint": proposal["bank_after_fingerprint"],
        "request_fingerprint": proposal["request_fingerprint"],
        "source_fingerprints": proposal.get("source_fingerprints", []),
        "tool_version": proposal.get("tool_version", TOOL_VERSION),
        "diff": proposal.get("diff", ""),
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "applied_at": None,
        "git_commit": None,
    }

    # Durable before-image + prepared manifest BEFORE any mutation
    # (T-11-02/T-11-13: interruption here leaves the bank untouched and the
    # run visible). A newly created artifact records an empty before-image
    # explicitly, never a missing fingerprint (11-05).
    if before_exists:
        _write_bytes_atomic(manifest["before_image"], before_raw)
    _write_json(manifest_path, manifest)

    # Atomic replacement: same-directory temp plus os.replace.
    after_raw = proposal["bank_after_text"].encode("utf-8")
    _write_bytes_atomic(target_path, after_raw)

    # After-fingerprint guard: the write is applied only if the target now
    # carries exactly the preflighted after fingerprint.
    current_after = bank_fingerprint(_read_bytes(target_path).decode("utf-8"))
    if current_after != proposal["bank_after_fingerprint"]:
        raise WriterError(
            "writer.after_guard_failed",
            "post-replace fingerprint %s does not match proposal %s"
            % (current_after, proposal["bank_after_fingerprint"]))
    manifest["state"] = "applied"
    manifest["applied_at"] = time.strftime(
        "%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    _write_json(manifest_path, manifest)
    return manifest


def _write_git(proposal, target_path, state_dir, git, before_fp):
    """The Git backend (T-11-18): the manifest is prepared inside the repo
    (.itembank/audit/manifests) and committed together with the one accepted
    item change in a single machine-authored commit; the commit hash is
    recorded. Interruption before the commit leaves the prepared manifest
    and the staged change visible and recoverable -- never an unreported
    dirty bank."""
    write_id = deterministic_write_id(proposal)
    manifest_dir = _git_manifest_dir(git["root"])
    os.makedirs(manifest_dir, exist_ok=True)
    manifest_path = os.path.join(manifest_dir, write_id + ".json")

    manifest = {
        "schema_version": WRITE_SCHEMA_VERSION,
        "write_id": write_id,
        "run_id": proposal.get("run_id", ""),
        "backend": "git",
        "state": "prepared",
        "target_path": os.path.abspath(target_path),
        "units": proposal.get("units", []),
        "before_fingerprint": before_fp,
        "before_image": "",
        "before_exists": True,
        "after_fingerprint": proposal["bank_after_fingerprint"],
        "request_fingerprint": proposal["request_fingerprint"],
        "source_fingerprints": proposal.get("source_fingerprints", []),
        "tool_version": proposal.get("tool_version", TOOL_VERSION),
        "diff": proposal.get("diff", ""),
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "applied_at": None,
        "git_commit": None,
    }
    _write_json(manifest_path, manifest)

    # Apply the one accepted item change on disk, then verify the guard.
    after_raw = proposal["bank_after_text"].encode("utf-8")
    _write_bytes_atomic(target_path, after_raw)
    current_after = bank_fingerprint(_read_bytes(target_path).decode("utf-8"))
    if current_after != proposal["bank_after_fingerprint"]:
        raise WriterError(
            "writer.after_guard_failed",
            "post-write fingerprint %s does not match proposal %s"
            % (current_after, proposal["bank_after_fingerprint"]))

    rels = [git["rel"],
            os.path.relpath(manifest_path, git["root"])]
    message = ("itembank audit: machine-authored write %s (request %s, "
               "backend git)") % (write_id, proposal["request_fingerprint"])
    commit_hash = _git_commit(git, rels, message)
    # The committed manifest records the prepared state; the applied-state
    # update (with the commit hash) is post-commit metadata on disk -- the
    # bank change itself is fully committed and the worktree is clean at
    # the bank path (T-11-18).
    manifest["state"] = "applied"
    manifest["applied_at"] = time.strftime(
        "%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    manifest["git_commit"] = commit_hash
    _write_json(manifest_path, manifest)
    return manifest


def _manifest_dirs(target_path, state_dir):
    """Every manifest directory a write id may live in: the caller's state
    dir plus, for a Git target, the repo's own committed manifest dir (found
    even when the bank is currently dirty)."""
    dirs = [_state_paths(state_dir)[0]]
    root = _git_repo_root(target_path)
    if root is not None:
        dirs.append(_git_manifest_dir(root))
    return dirs


def _find_manifest_anywhere(write_id, target_path, state_dir):
    for d in _manifest_dirs(target_path, state_dir):
        m = _read_manifest(d, write_id)
        if m is not None:
            return m
    return None


def undo(write_id, target_path, state_dir):
    """The sole public undo operation (D-15): route by manifest backend and
    restore. Git undo runs a documented non-interactive `git revert` of the
    machine-authored commit and refuses a dirty/conflicting worktree; shadow
    undo verifies the current target fingerprint equals the recorded
    after-image before restoring, refusing without a force path (T-11-17).
    An already-reverted write is idempotent. Callers never choose a backend.
    Returns a machine-readable result dict; raises WriterError on refusal."""
    manifest = _find_manifest_anywhere(write_id, target_path, state_dir)
    if manifest is None:
        raise WriterError("undo.unknown_write",
                          "no manifest found for write %s" % write_id)
    backend = manifest.get("backend")
    if manifest.get("state") == "reverted":
        return {"schema_version": WRITE_SCHEMA_VERSION,
                "write_id": write_id, "status": "already_reverted",
                "backend": backend}
    if backend == "git":
        return _undo_git(manifest, write_id, target_path)
    return _undo_shadow(manifest, write_id, target_path)


def _undo_shadow(manifest, write_id, target_path):
    """Shadow restore: exact after-fingerprint equality required; a newly
    created artifact (before_exists false) is removed; no force path."""
    if not os.path.exists(target_path):
        raise WriterError("undo.target_missing",
                          "target %s does not exist" % target_path)
    current_fp = bank_fingerprint(_read_bytes(target_path).decode("utf-8"))
    if current_fp != manifest.get("after_fingerprint"):
        raise WriterError(
            "undo.stale_target",
            "target fingerprint %s does not match the recorded after-image "
            "%s; refusing to overwrite newer human work (no force path)"
            % (current_fp, manifest.get("after_fingerprint")))
    if manifest.get("before_exists") is False:
        # A newly created report artifact: restore is removal of the file.
        os.remove(target_path)
        _mark_reverted(manifest, target_path, _state_dir_arg(manifest))
        return {"schema_version": WRITE_SCHEMA_VERSION,
                "write_id": write_id, "status": "reverted",
                "backend": "shadow", "before_exists": False}
    before_path = manifest.get("before_image")
    if not before_path or not os.path.exists(before_path):
        raise WriterError("undo.before_missing",
                          "before-image for %s is missing" % write_id)
    before_raw = _read_bytes(before_path)
    restored_fp = bank_fingerprint(before_raw.decode("utf-8"))
    if restored_fp != manifest.get("before_fingerprint"):
        raise WriterError("undo.before_tampered",
                          "before-image content does not match its recorded "
                          "fingerprint; refusing to restore")
    _write_bytes_atomic(target_path, before_raw)
    _mark_reverted(manifest, target_path, _state_dir_arg(manifest))
    return {"schema_version": WRITE_SCHEMA_VERSION,
            "write_id": write_id, "status": "reverted", "backend": "shadow",
            "before_fingerprint": restored_fp}


def _undo_git(manifest, write_id, target_path):
    """Git restore: a documented non-interactive `git revert` of the
    machine-authored commit; a dirty bank path or a conflict refuses with no
    force path (T-11-17)."""
    root = _git_repo_root(target_path)
    if root is None:
        raise WriterError("undo.git_target_changed",
                          "target %s is no longer inside a Git worktree; "
                          "refusing to revert" % target_path)
    # realpath for the same symlink reason as _git_target: git reports the
    # physical root, so the target path must be resolved before relpath.
    git = {"root": root,
           "rel": os.path.relpath(os.path.realpath(target_path),
                                  os.path.realpath(root))}
    commit_hash = manifest.get("git_commit")
    if not commit_hash:
        raise WriterError("undo.git_commit_missing",
                          "manifest %s has no git commit to revert" % write_id)
    _git_revert(git, commit_hash)
    _mark_reverted(manifest, target_path, _state_dir_arg(manifest))
    return {"schema_version": WRITE_SCHEMA_VERSION,
            "write_id": write_id, "status": "reverted", "backend": "git",
            "git_commit": commit_hash}


def _state_dir_arg(manifest):
    """The state dir is not stored in the manifest; the caller's state dir
    is recoverable from the manifest's sibling location when the write used
    the shadow backend (the before-image lives under <state>/before). For
    git manifests the target's repo manifest dir is found by _mark_reverted."""
    before_image = manifest.get("before_image") or ""
    if before_image:
        parent = os.path.dirname(os.path.abspath(before_image))
        if os.path.basename(parent) == BEFORE_DIR:
            return os.path.dirname(parent)
    return os.path.dirname(manifest.get("target_path") or ".")


def _mark_reverted(manifest, target_path, state_dir):
    """Locate the manifest by write id across the candidate dirs and record
    the reverted state. The manifest path is not stored inside the manifest
    itself, so the write id is the key."""
    write_id = manifest.get("write_id", "")
    for d in _manifest_dirs(target_path, state_dir):
        candidate = os.path.join(d, write_id + ".json")
        if os.path.exists(candidate):
            manifest["state"] = "reverted"
            _write_json(candidate, manifest)
            return
    # Unknown location: the undo already restored the target; the manifest
    # update is best-effort but the restore result stands.
    manifest["state"] = "reverted"


def find_applied_manifest(run_id, target_path, state_dir):
    """The authoring loop's duplicate-run probe (AUTH-01): return the applied
    manifest for `run_id` whose after-fingerprint still matches the target
    (meaning the write is current), else None. Searches the state dir and
    the Git repo's own manifest dir. Never mutates."""
    if not os.path.exists(target_path):
        return None
    current_fp = bank_fingerprint(_read_bytes(target_path).decode("utf-8"))
    seen = []
    for manifests in _manifest_dirs(target_path, state_dir):
        if not os.path.isdir(manifests):
            continue
        for name in sorted(os.listdir(manifests)):
            if not name.endswith(".json") or name in seen:
                continue
            seen.append(name)
            try:
                manifest = _read_manifest(manifests, name[:-5])
            except WriterError:
                continue
            if manifest.get("run_id") == run_id and \
                    manifest.get("state") == "applied" and \
                    manifest.get("after_fingerprint") == current_fp:
                return manifest
    return None
