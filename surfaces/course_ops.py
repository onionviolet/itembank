"""The course operating surface's dispatch spine, and its first operation
family.

Phase 19A's finding was not that a course operation is missing. It is that
387 KB of frozen, tested course engine has no door: `course.create_course`
was reachable only by importing Python, so neither a person nor an agent
client could start a course at all. This module is the door frame every
later 19A wave hangs an operation in, and the course lifecycle family is the
first operation hung in it.

Three rules make it a spine rather than a pile of endpoints, and each one is
a rule a later wave copies rather than re-decides:

- **The request document is read off disk.** `schemas/course_operation.json`
  carries one `$defs` node per operation, and `validate_request` checks a
  request against the node the route's own path selects, before anything is
  read or written. That is what makes the Phase 999.3 MCP tool table
  mechanical: the tool signature is the schema node, so a schema edit
  changes the tool with no code edit.
- **The write is the frozen one.** Every operation here reaches durable
  state through `course.create_course` / `course.write_course`, which is
  `journal.commit_operation` with an expected base fingerprint. Nothing in
  this module opens a course file for writing, and
  `journal.OPERATION_TYPES` stays at its six values: a rename is an
  `edit_in_place`, not a seventh operation type.
- **One implementation, two surfaces.** `run` is what the route calls and
  what the CLI command calls, so a twin is the same call rather than a
  similar print. That is D-03's "a CLI twin means the subcommand reaches the
  same runtime call".

A refusal is typed and says what to do next, because "you may not do that
yet" is an answer and not an error to hide.
"""
import json
import os
import sys

import course as course_module
import graph
import journal
import resources
import schema_validate
from surfaces import ia


# The published request document, read off disk on every dispatch. Not
# cached: the architecture forbids module-level caches, and a schema a
# process is holding from before an edit is exactly the drift D-04 exists to
# prevent.
REQUEST_SCHEMA_PATH = "schemas/course_operation.schema.json"

# The course lifecycle family, and the engine function each operation
# reaches. Every later wave appends its family here rather than growing a
# second table: this is the list the route set, the CLI actions, and the
# reserved MCP tool names are all checked against.
OPERATION_ENGINE = {
    "create": "course.create_course",
    "rename": "course.write_course",
}


def request_schema():
    """The whole published document, parsed. One reader, so the route, the
    CLI, and `itembank schema` cannot disagree about what a request is."""
    return json.loads(resources.read_text(REQUEST_SCHEMA_PATH))


def operation_schema(operation, document=None):
    """The one `$defs` node that is `operation`'s signature.

    Resolved by name rather than by walking `oneOf`, so a request is checked
    against the operation the route's path names and a refusal can say
    "title is required" instead of "no branch matched".
    """
    document = document if document is not None else request_schema()
    node = (document.get("$defs") or {}).get(operation)
    if node is None:
        raise course_module.CourseError(
            "course.unknown_operation",
            "%s is not a published course operation; the operations are %s. "
            "Next safe action: call one of those, or read the request "
            "document at %s."
            % (operation, ", ".join(sorted(OPERATION_ENGINE)),
               REQUEST_SCHEMA_PATH))
    return node, document


def validate_request(operation, request):
    """Refuse anything the published document does not describe, before a
    single file is read.

    The schema itself is walked first by `schema_validate.check_schema`, so a
    schema that rots fails loudly here rather than silently checking half the
    contract.
    """
    node, document = operation_schema(operation)
    if not isinstance(request, dict):
        raise course_module.CourseError(
            "course.invalid_request",
            "a course operation request is a JSON object, not %s. Next safe "
            "action: send an object with an `operation` field."
            % type(request).__name__)
    try:
        schema_validate.check_schema(document)
    except schema_validate.SchemaError as err:
        raise course_module.CourseError(
            "course.schema_unreadable",
            "%s could not be read as a schema this validator implements "
            "(%s), so no request can be checked against it and nothing was "
            "written. Next safe action: repair the document, or reinstall "
            "this release." % (REQUEST_SCHEMA_PATH, err))
    errors = schema_validate.validate(request, node, root=document)
    if errors:
        raise course_module.CourseError(
            "course.invalid_request",
            "this %s request does not match %s#/$defs/%s: %s. Next safe "
            "action: correct the named field and send it again; nothing was "
            "read or written."
            % (operation, REQUEST_SCHEMA_PATH, operation, "; ".join(errors)))
    return request


def resolve_course(root, course_id):
    """The directory a course id names, resolved the one way the course
    frame already resolves it.

    A request never carries a filesystem path. `ia.course_dir_for` matches
    the pinned `course_object_id` first and the directory basename only as
    the declared degraded fallback, so a client addresses a course by the id
    it sees on the page and the server decides where that lives.
    """
    base = ia.course_dir_for(root, course_id, module=course_module)
    if base is None or not os.path.isdir(base):
        raise course_module.CourseError(
            "course.unknown_course",
            "no course under %s answers to %s. Next safe action: list the "
            "courses with `itembank shelf`, or create this one with "
            "`itembank course create %s --title ...`."
            % (os.path.abspath(root), course_id, course_id))
    return base


def _op_create(root, body, actor_kind, actor_name):
    """Mint a course sidecar under `root`.

    The directory is made when it is absent, because a course is a folder
    with a sidecar in it and a learner asking for a course is not asking to
    make a folder first. An existing directory is used as it stands: the
    guard against clobbering is `course.create_course`'s own
    `course.sidecar_exists` refusal, which is the compare-and-swap path's
    check and not a second one here. A commit that refuses removes a
    directory this call created and nothing else, so a failure leaves the
    workspace as it was found.
    """
    course_id = body["course_id"]
    base = os.path.join(os.path.abspath(root), course_id)
    created = not os.path.isdir(base)
    if created:
        os.makedirs(base)
    try:
        revision = course_module.create_course(
            base, body["title"], actor_kind, actor_name)
    except Exception:
        if created and not os.listdir(base):
            os.rmdir(base)
        raise
    read = course_module.read_course(base)
    return {
        "operation": "create",
        "engine": OPERATION_ENGINE["create"],
        "course_id": course_id,
        "course_object_id": read["object_id"],
        "title": body["title"],
        "fingerprint": read["fingerprint"],
        "revision": revision.get("revision"),
        "created_directory": created,
        "undo": "the mint is journalled as one entry; reverse it with "
                "`itembank audit undo` against %s, which restores the "
                "absence of the sidecar" % course_id,
    }


def _op_rename(root, body, actor_kind, actor_name):
    """Retitle a course through the one compare-and-swap write.

    The title is display and never identity: `course_object_id` is untouched,
    so every binding, every evidence event, and every package manifest that
    names this course still names it. `expected_fingerprint` is passed
    through when the caller states one, so a stale write is refused by
    `journal.stale_preflight` by name rather than by a second guard here.
    """
    base = resolve_course(root, body["course_id"])
    read = course_module.read_course(base)
    doc = read["doc"]
    previous = doc["header"].get("title", "")
    doc["header"]["title"] = body["title"]
    revision = course_module.write_course(
        base, doc, body.get("expected_fingerprint") or read["fingerprint"],
        actor_kind, actor_name)
    return {
        "operation": "rename",
        "engine": OPERATION_ENGINE["rename"],
        "course_id": body["course_id"],
        "course_object_id": read["object_id"],
        "previous_title": previous,
        "title": body["title"],
        "fingerprint": revision.get("fingerprint"),
        "revision": revision.get("revision"),
        "undo": "restore the previous title with `itembank course rename %s "
                "--title %s`" % (body["course_id"], json.dumps(previous)),
    }


OPERATIONS = {
    "create": _op_create,
    "rename": _op_rename,
}


def run(root, operation, request, actor_kind="human", actor_name=""):
    """Validate one request against its published node and dispatch it.

    The route's path is the authority on which operation this is, not a
    discriminator the client sends: a body claiming a different operation
    than the path is refused rather than silently rewritten, because a
    request that says one thing and is executed as another is the exact
    ambiguity D-02's one-route-per-operation shape exists to remove.
    """
    if operation not in OPERATIONS:
        raise course_module.CourseError(
            "course.unknown_operation",
            "%s is not a published course operation; the operations are %s. "
            "Next safe action: call one of those."
            % (operation, ", ".join(sorted(OPERATIONS))))
    body = dict(request or {})
    declared = body.get("operation")
    if declared is not None and declared != operation:
        raise course_module.CourseError(
            "course.operation_mismatch",
            "this request declares operation %r but was sent to the %s "
            "operation; nothing was read or written. Next safe action: send "
            "it to the %r route, or correct the field."
            % (declared, operation, declared))
    body["operation"] = operation
    validate_request(operation, body)
    return OPERATIONS[operation](root, body, actor_kind,
                                 actor_name or body.get("actor") or "")


def show(root, course_id):
    """One course's identity, title, fingerprint and section counts.

    A read, and the only reason it lives beside the writes: a caller cannot
    state an `expected_fingerprint` for a rename without having read one, and
    sending them to Python for it would defeat the phase. The served read
    routes are 19A-09's wave; this is the CLI's half of the same reading.
    """
    base = resolve_course(root, course_id)
    read = course_module.read_course(base)
    doc = read["doc"]
    return {
        "course_id": course_id,
        "course_object_id": read["object_id"],
        "title": doc["header"].get("title", ""),
        "graph_schema_version": doc["header"].get("graph_schema_version"),
        "fingerprint": read["fingerprint"],
        "revision": read["revision"],
        "counts": dict((key, len(doc.get(key) or ()))
                       for key in ("structure", "objectives", "sources",
                                   "edges", "bindings", "migrations")),
    }


def cmd_course(a):
    """`itembank course` -- the CLI twin of `POST /api/course/<operation>`.

    Every action reaches `run` or `show`, the same functions the routes call,
    so the twin is one call and not a similar print (D-03).
    """
    try:
        if a.action == "show":
            payload = show(a.root, a.course_id)
            if getattr(a, "json", False):
                print(json.dumps(payload, ensure_ascii=False, indent=2))
                return 0
            print("%s  %s" % (payload["course_object_id"], payload["title"]))
            print("  fingerprint %s (revision %s)"
                  % (payload["fingerprint"], payload["revision"]))
            print("  " + ", ".join("%s %d" % (k, v) for k, v
                                   in sorted(payload["counts"].items())))
            return 0
        request = {"course_id": a.course_id, "title": a.title}
        if a.action == "rename" and getattr(a, "expect", ""):
            request["expected_fingerprint"] = a.expect
        if getattr(a, "actor", ""):
            request["actor"] = a.actor
        payload = run(a.root, a.action, request, actor_kind="human",
                      actor_name=getattr(a, "actor", "") or "")
        if getattr(a, "json", False):
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 0
        if a.action == "create":
            print("created %s (%s) at revision %s"
                  % (payload["title"], payload["course_object_id"],
                     payload["revision"]))
        else:
            print("renamed %s from %s to %s at revision %s"
                  % (payload["course_object_id"], payload["previous_title"],
                     payload["title"], payload["revision"]))
        print("  fingerprint %s" % payload["fingerprint"])
        print("  undo: %s" % payload["undo"])
        return 0
    except (course_module.CourseError, graph.GraphError,
            journal.JournalError) as err:
        sys.exit("%s: %s" % (err.code, err.message))
