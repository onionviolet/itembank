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
import hashlib
import json
import os
import time

from authoring import WRITE_SCHEMA_VERSION, TOOL_VERSION, bank_fingerprint, \
    canonical_json

# The manifest directory names inside `state_dir`.
MANIFESTS_DIR = "manifests"
BEFORE_DIR = "before"


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


def write_units(proposal, target_path, state_dir, expected_fingerprint=None):
    """Atomically apply one preflighted unit through the shadow backend.

    Rechecks the expected bank fingerprint under this writer's control
    (AUTH-02/T-11-02): a mismatch refuses with `stale_preflight` and never
    mutates. Persists the before-image and a prepared manifest before the
    replace, then marks the manifest applied only after the after-fingerprint
    guard passes. Returns the applied manifest.

    A duplicate write id (same proposal already applied and still matching)
    returns the existing manifest without a second mutation (AUTH-01)."""
    if not isinstance(proposal, dict) or not proposal.get("bank_after_text"):
        raise WriterError("writer.proposal_invalid",
                          "writer requires an immutable preflighted proposal")
    if not os.path.exists(target_path):
        raise WriterError("writer.target_missing",
                          "target bank %s does not exist" % target_path)
    before_raw = _read_bytes(target_path)
    before_fp = bank_fingerprint(before_raw.decode("utf-8"))
    if expected_fingerprint is not None and before_fp != expected_fingerprint:
        raise WriterError(
            "writer.stale_preflight",
            "current bank fingerprint %s does not match the preflighted %s; "
            "the bank changed since the proposal was built"
            % (before_fp, expected_fingerprint))

    write_id = deterministic_write_id(proposal)
    manifests, before = _ensure_dirs(state_dir)
    manifest_path = _manifest_path(manifests, write_id)

    existing = _read_manifest(manifests, write_id)
    if existing is not None:
        current_fp = bank_fingerprint(
            _read_bytes(target_path).decode("utf-8"))
        if existing.get("state") == "applied" and \
                existing.get("after_fingerprint") == current_fp:
            return existing  # idempotent duplicate: no second mutation
        raise WriterError(
            "writer.duplicate_conflict",
            "write %s already exists but its after-fingerprint no longer "
            "matches the target; refusing to reapply" % write_id)

    manifest = {
        "schema_version": WRITE_SCHEMA_VERSION,
        "write_id": write_id,
        "run_id": proposal.get("run_id", ""),
        "backend": "shadow",
        "state": "prepared",
        "target_path": os.path.abspath(target_path),
        "units": proposal.get("units", []),
        "before_fingerprint": before_fp,
        "before_image": _content_path(before, before_fp),
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
    # run visible).
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


def undo(write_id, target_path, state_dir):
    """The sole public undo operation (D-15): route by manifest backend and
    restore. Shadow undo verifies the current target fingerprint equals the
    recorded after-image; any mismatch refuses without a force path
    (T-11-17). An already-reverted write is idempotent. Returns a
    machine-readable result dict; raises WriterError on refusal."""
    manifests, _ = _state_paths(state_dir)
    manifest = _read_manifest(manifests, write_id)
    if manifest is None:
        raise WriterError("undo.unknown_write",
                          "no manifest found for write %s" % write_id)
    if manifest.get("backend") != "shadow":
        raise WriterError("undo.backend_unavailable",
                          "write %s used backend %r; undo is routed by the "
                          "manifest and is not available here"
                          % (write_id, manifest.get("backend")))
    if manifest.get("state") == "reverted":
        return {"schema_version": WRITE_SCHEMA_VERSION,
                "write_id": write_id, "status": "already_reverted",
                "backend": "shadow"}
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
    manifest["state"] = "reverted"
    _write_json(_manifest_path(manifests, write_id), manifest)
    return {"schema_version": WRITE_SCHEMA_VERSION,
            "write_id": write_id, "status": "reverted", "backend": "shadow",
            "before_fingerprint": restored_fp}


def find_applied_manifest(run_id, target_path, state_dir):
    """The authoring loop's duplicate-run probe (AUTH-01): return the applied
    manifest for `run_id` whose after-fingerprint still matches the target
    (meaning the write is current), else None. Never mutates."""
    manifests, _ = _state_paths(state_dir)
    if not os.path.isdir(manifests):
        return None
    if not os.path.exists(target_path):
        return None
    current_fp = bank_fingerprint(_read_bytes(target_path).decode("utf-8"))
    for name in sorted(os.listdir(manifests)):
        if not name.endswith(".json"):
            continue
        try:
            manifest = _read_manifest(manifests, name[:-5])
        except WriterError:
            continue
        if manifest.get("run_id") == run_id and \
                manifest.get("state") == "applied" and \
                manifest.get("after_fingerprint") == current_fp:
            return manifest
    return None
