"""The course sidecar's lifecycle: create, read, compare-and-swap write, and
the non-destructive migration of a Phase 13.9 stub.

`course.py` is a peer of `journal.py` and `evidence.py` in the runtime tier,
not an extension of either. Every durable write in this module goes through
`journal.commit_operation`, the one compare-and-swap write path, and this
module adds no second atomic-write helper and no second staleness check: a
stale write is refused by the 14A path, by name, and not by a private guard
here.

The sidecar is exactly one `kind="course"` object with exactly one
compare-and-swap lineage (D-14A-1, and `14B-RESEARCH.md` Pattern 1).
Objectives, containers, and edges are addressable records inside that one
file, never independently tracked files, because `journal.commit_operation`
binds exactly one `object_id` to exactly one path per call: giving an
objective its own compare-and-swap file would put two object kinds in
competition for the same physical bytes.

This module deliberately does not import `evidence`. The rule that a course
migration never transfers evidence is therefore structural rather than
maintained by care, which is what plan 14B-04's migration work depends on.

Under D-14B-1 this module never opens the Phase 13.9 `course.md` stub for
writing. `migrate_stub` reads it, emits a separate sidecar, journals the
import, and leaves the hand-authored file byte-identical.
"""
import os

import graph
import identity
import journal

COURSE_SIDECAR_FILENAME = "course-graph.md"
STUB_FILENAME = "course.md"
COURSE_KIND = "course"

# The Phase 13.9 stub's own column names, read for migration only. These are
# not this phase's format and are never written by this module.
STUB_OBJECTIVE_COLUMNS = ("id", "objective", "citation", "treatment", "reason")
STUB_SOURCE_COLUMNS = ("id", "path", "format", "size", "sha256")


class CourseError(Exception):
    """A typed course-lifecycle failure: machine-readable `code` plus
    message, the same two-argument shape `identity.IdentityError` uses."""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message


def sidecar_path(course_root):
    return os.path.join(os.path.abspath(course_root), COURSE_SIDECAR_FILENAME)


def stub_path(course_root):
    return os.path.join(os.path.abspath(course_root), STUB_FILENAME)


def _no_sidecar(path):
    return CourseError(
        "course.no_sidecar",
        "no course graph exists at %s; create one with course.create_course "
        "before reading or binding anything" % path)


def _sidecar_exists(path):
    return CourseError(
        "course.sidecar_exists",
        "a course graph already exists at %s; refusing to overwrite it" % path)


def create_course(course_root, title, actor_kind, actor_name):
    """Mint a fresh course object and write its sidecar through the frozen
    14A compare-and-swap path. Returns the 14A revision record."""
    path = sidecar_path(course_root)
    if os.path.exists(path):
        raise _sidecar_exists(path)
    course_object_id = identity.new_object_id()
    doc = graph.new_course(title, course_object_id)
    raw = graph.serialize_course(doc).encode("utf-8")
    return journal.commit_operation(
        base=course_root, object_id=course_object_id, kind=COURSE_KIND,
        rel_path=COURSE_SIDECAR_FILENAME, operation="mint", new_bytes=raw,
        expected_fingerprint=None, actor_kind=actor_kind,
        actor_name=actor_name, create_if_missing=True)


def read_course(course_root):
    """The sidecar's document, its bytes, its fingerprint, its last accepted
    revision, its object id, and its 14A object state.

    The object id is read from the sidecar's own header rather than from the
    registry, so the file stays self-describing: a sidecar that travels in a
    package still names the object it is.
    """
    path = sidecar_path(course_root)
    if not os.path.exists(path):
        raise _no_sidecar(path)
    with open(path, "rb") as fh:
        raw = fh.read()
    text = raw.decode("utf-8")
    doc = graph.parse_course(text)
    object_id = doc["header"].get("course_object_id", "")
    registry = journal.read_registry(course_root)
    row = registry.get(object_id) or {}
    return {
        "doc": doc,
        "text": text,
        "fingerprint": identity.object_fingerprint(raw, COURSE_KIND),
        "revision": row.get("revision"),
        "object_id": object_id,
        "state": journal.object_state(course_root, object_id),
    }


def write_course(course_root, doc, expected_fingerprint, actor_kind,
                 actor_name, operation="edit_in_place"):
    """Write `doc` back to the sidecar through the one compare-and-swap path.

    `expected_fingerprint` is passed straight through to
    `journal.commit_operation`, so a stale write is refused by the 14A path
    with `journal.stale_preflight` and never by a second check here.
    """
    raw = graph.serialize_course(doc).encode("utf-8")
    return journal.commit_operation(
        base=course_root, object_id=doc["header"]["course_object_id"],
        kind=COURSE_KIND, rel_path=COURSE_SIDECAR_FILENAME,
        operation=operation, new_bytes=raw,
        expected_fingerprint=expected_fingerprint, actor_kind=actor_kind,
        actor_name=actor_name)


def _stub_tables(text):
    """The Phase 13.9 stub's `## Sources` and `## Objectives` rows, read for
    migration only.

    This reads one records file's pipe tables, the same way
    `surfaces/day.py:129 parse_lanes` reads `lanes.md`. It is not a second
    document model and it never touches bank or lesson bytes.
    """
    tables, section = {}, None
    for line in text.split("\n"):
        if line.startswith("## "):
            section = line[3:].strip()
            tables.setdefault(section, [])
            continue
        if section and line.lstrip().startswith("|"):
            cells = graph.split_row(line)
            if graph.is_rule_row(cells):
                continue
            tables[section].append(cells)
    return tables


def migrate_stub(course_root, actor_kind, actor_name):
    """Read a Phase 13.9 `course.md` stub, emit a course sidecar beside it,
    and journal the import.

    Under D-14B-1 the stub is opened for reading only and is never rewritten.
    A hand-authored objective map is carried forward, not edited in place by
    a tool.
    """
    stub = stub_path(course_root)
    if not os.path.exists(stub):
        raise CourseError(
            "course.stub_absent",
            "no Phase 13.9 course stub exists at %s; nothing to migrate"
            % stub)
    target = sidecar_path(course_root)
    if os.path.exists(target):
        raise _sidecar_exists(target)

    with open(stub, "r", encoding="utf-8") as fh:
        text = fh.read()
    tables = _stub_tables(text)

    title = ""
    for line in text.split("\n"):
        if line.startswith("# "):
            title = line[2:].strip()
            break

    course_object_id = identity.new_object_id()
    doc = graph.new_course(title, course_object_id)

    source_rows = tables.get("Sources", [])
    for cells in source_rows[1:]:
        record = graph.new_record("Sources", {
            "source_object_id": identity.new_object_id(),
            "title": cells[1] if len(cells) > 1 else "",
            "note": "migrated from the Phase 13.9 stub"})
        doc["sources"].append(record)

    objective_rows = tables.get("Objectives", [])
    for cells in objective_rows[1:]:
        graph.add_objective(doc, cells[1] if len(cells) > 1 else "",
                            origin="imported-13.9")

    raw = graph.serialize_course(doc).encode("utf-8")
    revision = journal.commit_operation(
        base=course_root, object_id=course_object_id, kind=COURSE_KIND,
        rel_path=COURSE_SIDECAR_FILENAME, operation="import", new_bytes=raw,
        expected_fingerprint=None, actor_kind=actor_kind,
        actor_name=actor_name, create_if_missing=True)
    return {
        "object_id": course_object_id,
        "objectives": len(doc["objectives"]),
        "sources": len(doc["sources"]),
        "revision": revision["revision"],
        "stub_rewritten": False,
    }
