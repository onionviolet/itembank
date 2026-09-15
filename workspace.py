"""The learner-owned, machine-local course workspace record.

The record is the durable authority for approved course roots and learner
order. The course index remains derived: readers scan the approved roots and
reconcile cards by ``course_object_id``. Every mutation goes through
``journal.commit_operation`` so stale browser tabs, external edits, and undo
use the same compare-and-swap authority as every other durable object.
"""
import json
import os

import identity
import journal


WORKSPACE_SCHEMA_VERSION = 1
WORKSPACE_KIND = "workspace"
WORKSPACE_REL_PATH = os.path.join("_ia", "workspace.json")


class WorkspaceError(Exception):
    """A typed workspace failure with a stable code and actionable message."""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message


def workspace_path(base):
    return os.path.join(os.path.abspath(base), WORKSPACE_REL_PATH)


def _clean_root(path):
    if not isinstance(path, str) or not os.path.isabs(path):
        raise WorkspaceError("workspace.invalid_root",
                             "workspace roots must be absolute paths")
    return os.path.abspath(path)


def _validate(doc):
    if not isinstance(doc, dict) or set(doc) != {
            "schema_version", "workspace_object_id", "roots", "courses"}:
        raise WorkspaceError(
            "workspace.invalid_record",
            "workspace record must contain schema_version, "
            "workspace_object_id, roots, and courses")
    if doc["schema_version"] != WORKSPACE_SCHEMA_VERSION:
        raise WorkspaceError("workspace.future_schema",
                             "workspace schema is not supported by this build")
    object_id = doc["workspace_object_id"]
    if (not isinstance(object_id, str) or len(object_id) != 16
            or any(ch not in "0123456789abcdef" for ch in object_id)):
        raise WorkspaceError("workspace.invalid_record",
                             "workspace_object_id must be a 16-character hex id")
    roots = doc["roots"]
    if not isinstance(roots, list):
        raise WorkspaceError("workspace.invalid_record",
                             "workspace roots must be a list")
    clean_roots = [_clean_root(path) for path in roots]
    if len(set(clean_roots)) != len(clean_roots):
        raise WorkspaceError("workspace.invalid_record",
                             "workspace roots must be unique")
    courses = doc["courses"]
    if not isinstance(courses, list):
        raise WorkspaceError("workspace.invalid_record",
                             "workspace courses must be a list")
    ids = []
    for member in courses:
        if not isinstance(member, dict) or set(member) != {
                "course_object_id", "root_index", "path", "name"}:
            raise WorkspaceError("workspace.invalid_record",
                                 "each workspace course has an id, root, path, and name")
        course_id = member["course_object_id"]
        if not isinstance(course_id, str) or not course_id:
            raise WorkspaceError("workspace.invalid_record",
                                 "course_object_id must be a non-empty string")
        root_index = member["root_index"]
        if type(root_index) is not int or not 0 <= root_index < len(roots):
            raise WorkspaceError("workspace.invalid_record",
                                 "course root_index is outside the approved roots")
        rel_path = member["path"]
        if (not isinstance(rel_path, str) or not rel_path
                or os.path.isabs(rel_path) or rel_path in (".", "..")
                or rel_path.startswith(".." + os.sep)):
            raise WorkspaceError("workspace.invalid_record",
                                 "course path must stay relative to its approved root")
        if not isinstance(member["name"], str):
            raise WorkspaceError("workspace.invalid_record",
                                 "course name must be text")
        ids.append(course_id)
    if len(set(ids)) != len(ids):
        raise WorkspaceError("workspace.invalid_record",
                             "a course_object_id may appear only once")
    return doc


def _serialize(doc):
    _validate(doc)
    return (json.dumps(doc, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def read_workspace(base):
    """Read the workspace without writing or accepting divergent bytes."""
    path = workspace_path(base)
    if not os.path.exists(path):
        return {"present": False, "state": "absent", "doc": None,
                "fingerprint": None, "accepted_fingerprint": None,
                "revision": None}
    try:
        with open(path, "rb") as fh:
            raw = fh.read()
        doc = _validate(json.loads(raw.decode("utf-8")))
    except (OSError, UnicodeError, ValueError, WorkspaceError) as exc:
        return {"present": True, "state": "conflict", "doc": None,
                "fingerprint": None, "accepted_fingerprint": None,
                "revision": None, "error": str(exc)}
    object_id = doc["workspace_object_id"]
    registry = journal.read_registry(base)
    row = registry.get(object_id)
    fingerprint = identity.object_fingerprint(raw, WORKSPACE_KIND)
    if row is None or row.get("kind") != WORKSPACE_KIND:
        state = "conflict"
        accepted = None
        revision = None
    else:
        state = journal.object_state(base, object_id)
        accepted = row.get("fingerprint")
        revision = row.get("revision")
    return {"present": True, "state": state, "doc": doc,
            "fingerprint": fingerprint,
            "accepted_fingerprint": accepted, "revision": revision}


def approved_roots(base):
    """Return accepted roots, or the serving root in degraded mode."""
    state = read_workspace(base)
    if state["state"] != "clean":
        return [os.path.abspath(base)]
    return list(state["doc"]["roots"]) or [os.path.abspath(base)]


def _document(base, object_id, ordered_members):
    roots = [os.path.abspath(base)]
    for member in ordered_members:
        root = os.path.abspath(member["root"])
        if root not in roots:
            roots.append(root)
    courses = []
    for member in ordered_members:
        root = os.path.abspath(member["root"])
        path = os.path.relpath(os.path.abspath(member["path"]), root)
        if path == ".." or path.startswith(".." + os.sep):
            raise WorkspaceError("workspace.path_outside_root",
                                 "course path leaves its approved root")
        courses.append({
            "course_object_id": member["course_object_id"],
            "root_index": roots.index(root),
            "path": path,
            "name": member["name"],
        })
    return {"schema_version": WORKSPACE_SCHEMA_VERSION,
            "workspace_object_id": object_id,
            "roots": roots, "courses": courses}


def reorder(base, course_ids, members, expected_fingerprint,
            actor_kind="human", actor_name="local learner"):
    """Persist exactly one permutation of the currently rendered courses."""
    if not isinstance(course_ids, list) or any(
            not isinstance(value, str) or not value for value in course_ids):
        raise WorkspaceError("workspace.invalid_order",
                             "course_ids must be a list of course ids")
    if len(set(course_ids)) != len(course_ids):
        raise WorkspaceError("workspace.invalid_order",
                             "course_ids contains a duplicate")
    by_id = {member["course_object_id"]: member for member in members}
    if len(by_id) != len(members) or set(course_ids) != set(by_id):
        raise WorkspaceError(
            "workspace.stale_courses",
            "the shelf changed while it was being reordered; reload and try again")

    current = read_workspace(base)
    if current["present"] and current["state"] != "clean":
        raise WorkspaceError(
            "workspace.conflict",
            "the saved shelf order changed outside itembank; reconcile it before reordering")
    if current["present"]:
        if expected_fingerprint != current["fingerprint"]:
            raise WorkspaceError(
                "workspace.stale_preflight",
                "the saved shelf order changed; reload before moving another course")
        object_id = current["doc"]["workspace_object_id"]
        operation = "edit_in_place"
        create = False
    else:
        if expected_fingerprint is not None:
            raise WorkspaceError(
                "workspace.stale_preflight",
                "no saved shelf order matches the supplied fingerprint; reload and try again")
        object_id = identity.new_object_id()
        operation = "mint"
        create = True

    ordered = [by_id[course_id] for course_id in course_ids]
    raw = _serialize(_document(base, object_id, ordered))
    try:
        revision = journal.commit_operation(
            base=base, object_id=object_id, kind=WORKSPACE_KIND,
            rel_path=WORKSPACE_REL_PATH, operation=operation, new_bytes=raw,
            expected_fingerprint=expected_fingerprint, actor_kind=actor_kind,
            actor_name=actor_name, create_if_missing=create)
    except journal.JournalError as exc:
        raise WorkspaceError(exc.code, exc.message)
    applied = next((entry for entry in reversed(list(journal.entries(base)))
                    if entry.get("object_id") == object_id
                    and entry.get("state") == "applied"), None)
    return {"ok": True, "action": "reorder_courses",
            "course_ids": list(course_ids),
            "fingerprint": revision["fingerprint"],
            "revision": revision["revision"],
            "entry_id": applied.get("entry_id") if applied else None,
            "undo": "Reverse journal entry %s" % applied["entry_id"]
                    if applied else None}
