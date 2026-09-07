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

Plan 19A-02 hangs the source-binding family in the same frame and adds one
rule to it, the only one binding needed that a lifecycle write did not:
**a surface may say where a course lives, and a request may not.** `run`
takes an optional already-resolved `base`, which is how `itembank bind
--base .` addresses the course root a person is standing in, while the
request it builds still carries the course's own object id and no path. The
route passes no base and resolves the id server-side, exactly as before.

The family is four operations and the whole path from a linked file to a
coverage claim: `add_source` records the sidecar row (the one function in
this family that had no door at all, so an imported source could never be
named by the course that imported it), `rights` records what the learner
declares may be done with it, `bind` makes the claim and is refused unless
the right that binding kind consumes is granted at that moment, and
`bindings` reads the result back with every state passed through
`graph.validate_binding` and every right re-read through
`course.rights_for_binding`. That last pair is the point of the read: a
binding stores the rights snapshot it was made under, and a snapshot that
still says granted after the grant was revoked is history, not permission.

Plan 19A-04 adds the treatment family and one more rule, which is about what
a published node can SAY rather than about what an operation does.
`bind_treatment` writes exactly what `bind` with `binding_kind: "treatment"`
already wrote, and exists anyway because this validator has no `if`/`then`:
on a node serving both kinds `treatment` has to be optional while the runtime
insists on it, so the tool generated from that node fails at call time rather
than at type time. **An operation is worth its own node when the node can
require something the shared one cannot.** The older mode keeps serving and
says it is deprecated; a test asserts the two write byte-identical rows, so
the deprecation is a deprecation and not a fork.

The family's read, `treatments`, is the reason the wave is not just a
renaming. `graph.TREATMENT_RIGHTS` decides which of the eleven treatments a
course may use for a source, and it had no reader anywhere: the only way to
learn that a guided lesson needs `transform` while a direct reading needs
`read` was to attempt a binding and be refused, one kind at a time.
"""
import json
import os
import sys

import course as course_module
import course_package
import director
import graph
import identity
import journal
import resources
import schema_validate
import blueprint
from surfaces import binding_cli
from surfaces import ia
from surfaces import settings as settings_module


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
    "add_source": "graph.add_source",
    "bind": "course.bind_source",
    "bind_treatment": "course.bind_treatment",
    "treatments": "graph.treatment_right",
    "autonomy": "director.autonomy_level",
    "begin_operation": "director.begin_operation",
    "replay": "director.replay_operation",
    "reverse_operation": "director.reverse_operation",
    "recommend": "director.recommend_once",
    "recommend_pass": "director.recommend_treatments",
    "apply_recommendation": "director.apply_recommendation",
    "rights": "journal.op_grant_rights",
    "bindings": "graph.validate_binding",
    "add_container": "graph.add_container",
    "add_objective": "graph.add_objective",
    "add_edge": "graph.add_edge",
    "structure": "graph.validate_order",
    "rename_objective": "graph.rename_objective",
    "split_objective": "graph.split_objective",
    "merge_objectives": "graph.merge_objectives",
    "overlay_objective": "graph.overlay_objective",
    "accept_migration": "graph.accept_migration",
    "reject_migration": "graph.reject_migration",
    "bind_blueprint": "course.bind_blueprint",
    "blueprint_gate": "blueprint.blueprint_gate",
    "audit": "blueprint.course_audit",
    "staleness": "blueprint.staleness_report",
    "export_package": "course_package.export_package",
    "verify_package": "course_package.verify_manifest",
    "restore_package": "course_package.restore_package",
    "package_losses": "course_package.loss_report_text",
}

# The operations that only read. They reach no writer, advance no revision,
# and are the only ones a surface may serve behind the read-side gate; every
# other name in OPERATION_ENGINE writes.
READ_OPERATIONS = ("bindings", "structure", "treatments", "autonomy",
                   "replay", "blueprint_gate", "audit", "staleness",
                   "verify_package", "package_losses")

# The operations whose journal origin is an AGENT rather than the human at the
# surface, because a model produced what they record. Everything absent from
# this table is `human`, which is what a browser client and a terminal are.
#
# The kind is still the SURFACE's to decide and never the request's: it is
# chosen by what the operation does, exactly as the loopback gate above is.
# A recommendation's content comes from a model, so recording it as a human's
# work would put a false origin in the durable record; a declaration, a
# reversal and a settlement are a person's acts, and `accept_revision` in
# particular has `director.proposal_self_accept` waiting for anything that
# tried to be both proposer and reviewer.
# The director writes that print as a block rather than a line. Derived from
# the family rather than typed twice: a director operation that is neither a
# read nor listed here would print nothing, and this is the list that fails
# loudly instead.
DIRECTOR_WRITES = ("begin_operation", "reverse_operation", "recommend",
                   "recommend_pass", "apply_recommendation")

OPERATION_ACTOR_KIND = {
    "recommend": "agent",
    "recommend_pass": "agent",
    "apply_recommendation": "agent",
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


def _op_create(root, body, actor_kind, actor_name, base=None):
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
    base = base or os.path.join(os.path.abspath(root), course_id)
    approved = os.path.realpath(root)
    resolved = os.path.realpath(base)
    if course_id in (".", "..") or resolved == approved or \
            os.path.commonpath([approved, resolved]) != approved:
        raise course_module.CourseError(
            "course.path_outside_root",
            "the course directory must resolve strictly below the approved "
            "workspace root. Next safe action: choose a local course id.")
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


def _op_rename(root, body, actor_kind, actor_name, base=None):
    """Retitle a course through the one compare-and-swap write.

    The title is display and never identity: `course_object_id` is untouched,
    so every binding, every evidence event, and every package manifest that
    names this course still names it. `expected_fingerprint` is passed
    through when the caller states one, so a stale write is refused by
    `journal.stale_preflight` by name rather than by a second guard here.
    """
    base = base or resolve_course(root, body["course_id"])
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


def _sources_by_id(doc):
    """The sidecar's Sources rows, keyed by the object id they name. Built
    fresh on each read: a row is a reference, and two rows naming one object
    would be two answers to one question, which `_op_add_source` refuses."""
    return dict((row.get("source_object_id") or "", row)
                for row in doc.get("sources") or ())


def _op_add_source(root, body, actor_kind, actor_name, base=None):
    """Record a reference to a source object in the course sidecar.

    The missing step, and the reason it was missing is worth stating: a
    source is imported into the course root's journal registry, but the
    course's own Sources section is written by `graph.add_source`, which no
    surface called. So an imported source could be bound (a binding row
    names an object id) and still never appear in the Sources area, in
    `itembank bind list`, or in a package manifest that walks the sidecar.

    Two refusals, both before any write. A source the registry does not hold
    is refused, because a sidecar row naming an object nothing in this course
    root has is a durable claim with nothing behind it, and it would go on to
    fail the rights read at bind time anyway. A source already recorded is
    refused rather than appended twice: a Sources row is a reference to one
    object, unlike a binding row, where two rows for one pair are two claims
    about two different places.

    No right is consumed. Naming a file is not using it, and the rights this
    row's object carries are reported here only so a caller sees, in the same
    breath, that finding a source never granted permission to build a course
    out of it.
    """
    base = base or resolve_course(root, body["course_id"])
    source_id = body["source_object_id"]
    registry = journal.read_registry(base)
    record = registry.get(source_id)
    if record is None:
        raise course_module.CourseError(
            "course.unknown_source",
            "%s is not a registered object in this course root's journal "
            "registry, so a Sources row naming it would point at nothing. "
            "Next safe action: link or import it first with `itembank source "
            "import`, then record the row." % source_id)
    read = course_module.read_course(base)
    doc = read["doc"]
    if source_id in _sources_by_id(doc):
        raise course_module.CourseError(
            "course.source_already_recorded",
            "%s is already a Sources row in this course, so nothing was "
            "written; a source is referenced once and a second row would be "
            "a second answer to one question. Next safe action: bind it to "
            "an objective with `itembank bind source`, or read what the "
            "course holds with `itembank bind list`." % source_id)
    graph.add_source(doc, source_id, body["title"], body.get("note") or "")
    revision = course_module.write_course(
        base, doc, body.get("expected_fingerprint") or read["fingerprint"],
        actor_kind, actor_name)
    rights = dict((operation,
                   identity.rights_state(record.get("rights"), operation))
                  for operation in identity.RIGHTS_OPERATIONS)
    return {
        "operation": "add_source",
        "engine": OPERATION_ENGINE["add_source"],
        "course_id": body["course_id"],
        "course_object_id": read["object_id"],
        "source_object_id": source_id,
        "title": body["title"],
        "note": body.get("note") or "",
        "rights": rights,
        "bindable": rights.get(graph.SOURCE_BINDING_RIGHT) == "granted",
        "fingerprint": revision.get("fingerprint"),
        "revision": revision.get("revision"),
        "undo": "the row is one edit_in_place on the sidecar at revision "
                "%s; no surface removes a Sources row yet, so the reversal "
                "is restoring the sidecar's previous revision from the "
                "operation journal" % revision.get("revision"),
    }


def _op_bind(root, body, actor_kind, actor_name, base=None):
    """Bind a source, or a treatment, to an objective.

    Every decision here belongs to something else, which is the whole design:
    the vocabularies are `graph`'s closed ones, the rights gate is
    `course._require_right` reading the registry at the moment of the write,
    and the write is `course.write_course`'s compare-and-swap. This function
    validates nothing the schema already validated and grants nothing.

    The right consumed is reported rather than accepted: a source binding
    consumes `read` and a treatment binding consumes whatever its treatment
    kind consumes, and neither is a field a caller may set. A request that
    tried would have been refused by the node's closed property list before
    reaching here.
    """
    base = base or resolve_course(root, body["course_id"])
    binding_kind = body.get("binding_kind") or "source"
    result = binding_cli.bind(
        base, body["objective"], body["source"], binding_kind=binding_kind,
        treatment_kind=body.get("treatment") or "",
        locator=body.get("locator") or "",
        state=body.get("state") or "unknown",
        confidence=body.get("confidence") or "unknown",
        actor_kind=actor_kind, actor_name=actor_name)
    payload = dict(result)
    payload.update({
        "operation": "bind",
        "engine": ("course.bind_treatment" if binding_kind == "treatment"
                   else OPERATION_ENGINE["bind"]),
        "course_id": body["course_id"],
        # The write happened, so the right was exactly granted when it was
        # read. Reported as a state rather than as a boolean, because the
        # three states are what the rights model has and "true" would flatten
        # denied and unknown into one word.
        "rights_state_at_write": "granted",
        "undo": "no surface removes a binding; this row is journalled at "
                "revision %s, so the reversal is restoring the sidecar's "
                "previous revision from the operation journal"
                % result.get("revision"),
    })
    if binding_kind == "treatment":
        # Deprecated in place by 19A-04, not retired: this route recorded
        # treatment bindings before the spine existed and a client is
        # entitled to keep calling it. The row is identical to the one
        # `bind_treatment` writes, asserted by test, so the notice is a
        # pointer and never a warning about the result.
        payload["deprecated"] = (
            "binding a treatment through the `bind` operation still works "
            "and wrote the same row, but `bind_treatment` is the operation "
            "for it: the treatment is required there, which this node "
            "cannot express. Nothing is retired without an explicit "
            "migrate.")
    return payload


def _op_bind_treatment(root, body, actor_kind, actor_name, base=None):
    """Bind a treatment to an objective: the decision about HOW it is taught.

    The same row as a treatment binding through `bind`, deliberately: this is
    a typing of that operation and not a second writer, so both reach
    `binding_cli.bind` and through it `course.bind_treatment`, and a test
    asserts the two produce an identical row. What this node has that the
    other cannot is a REQUIRED treatment. The request document is the
    generated tool signature, this validator has no `if`/`then`, and so on
    the `bind` node `treatment` has to be optional while the runtime insists
    on it. A tool that advertises an optional field the runtime requires
    fails at call time instead of at type time, and an agent client has no
    way to know which.

    The right consumed is `graph.treatment_right`'s answer and is never a
    request field: an excerpt refuses on `quote` and a guided lesson on
    `transform`, read from the registry at the moment of the write. It is
    reported back, because a binding that succeeded should say which right it
    spent, and `treatments` is the operation that answers the same question
    before the attempt rather than after it.
    """
    base = base or resolve_course(root, body["course_id"])
    treatment = body["treatment"]
    result = binding_cli.bind(
        base, body["objective"], body["source"], binding_kind="treatment",
        treatment_kind=treatment,
        locator=body.get("locator") or "",
        state=body.get("state") or "unknown",
        confidence=body.get("confidence") or "unknown",
        actor_kind=actor_kind, actor_name=actor_name)
    payload = dict(result)
    payload.update({
        "operation": "bind_treatment",
        "engine": OPERATION_ENGINE["bind_treatment"],
        "course_id": body["course_id"],
        "treatment_kind": treatment,
        "right_consumed": graph.treatment_right(treatment),
        # The write happened, so the right was exactly granted when it was
        # read. A state and not a boolean, because the rights model has three
        # values and "true" would flatten denied and unknown into one word.
        "rights_state_at_write": "granted",
        "undo": "no surface removes a binding; this row is journalled at "
                "revision %s, so the reversal is restoring the sidecar's "
                "previous revision from the operation journal"
                % result.get("revision"),
    })
    return payload


def _op_treatments(root, body, actor_kind, actor_name, base=None):
    """Read the eleven treatments, the right each consumes, and whether that
    right is granted on one source right now.

    A read, and the first reader `graph.TREATMENT_RIGHTS` has ever had. The
    mapping is not a detail: it decides which treatments a course may use for
    a given source, and until this operation existed the only way to discover
    it was to attempt a binding and be refused. A learner who had granted
    `read` and not `transform` could bind a direct reading and not a guided
    lesson, and no surface said so beforehand.

    Two things make it an answer rather than a printed constant. The rights
    state is re-read through `course.rights_for_binding`, the same fresh read
    the write does, so what this reports and what the next write enforces
    cannot disagree. And the count of treatment bindings this course already
    records for each kind is reported beside it, so the table says what this
    course does as well as what it may do.

    It grants nothing and refuses nothing. A `transform` that reads
    `unknown` is reported as refusing, and the way to change that answer is
    to record the right, which is a different operation with a different
    authority behind it.
    """
    base = base or resolve_course(root, body["course_id"])
    read = course_module.read_course(base)
    doc = read["doc"]
    source_id = body.get("source") or ""
    known = set(row.get("source_object_id") or ""
                for row in doc.get("sources") or ())
    if source_id and source_id not in known:
        raise course_module.CourseError(
            "course.unknown_source",
            "%s is not a source this course names, so there are no rights to "
            "resolve the treatment table against. Next safe action: record "
            "it with `itembank course add-source %s --source %s --title ...`, "
            "or ask without --source for the mapping alone."
            % (source_id, body["course_id"], source_id))
    used = {}
    for row in doc.get("bindings") or ():
        if (row.get("binding_kind") or "") != "treatment":
            continue
        kind = row.get("treatment_kind") or ""
        if source_id and (row.get("source_object_id") or "") != source_id:
            continue
        used[kind] = used.get(kind, 0) + 1
    rows, allowed, refused = [], [], []
    for kind in graph.TREATMENT_KINDS:
        right = graph.treatment_right(kind)
        state = ""
        bindable = None
        if source_id:
            try:
                state = course_module.rights_for_binding(base, source_id,
                                                         right)
            except course_module.CourseError:
                # The course names the source and the registry does not hold
                # it, which is a real divergence and not a reason to guess.
                # Unknown is the restrictive reading and it refuses.
                state = identity.RIGHTS_UNKNOWN
            bindable = state == "granted"
            (allowed if bindable else refused).append(kind)
        rows.append({
            "treatment_kind": kind,
            "right_consumed": right,
            "rights_state": state,
            "bindable": bindable,
            "bound_here": used.get(kind, 0),
            "explanation": _treatment_sentence(kind, right, state, source_id),
        })
    return {
        "operation": "treatments",
        "engine": OPERATION_ENGINE["treatments"],
        "course_id": body["course_id"],
        "course_object_id": read["object_id"],
        "fingerprint": read["fingerprint"],
        "source_object_id": source_id,
        "source_title": dict(
            (row.get("source_object_id") or "", row.get("title") or "")
            for row in doc.get("sources") or ()).get(source_id, ""),
        "treatments": rows,
        "bindable": allowed,
        "refused": refused,
        "rights_resolved": bool(source_id),
    }


def _treatment_sentence(kind, right, state, source_id):
    """One sentence per treatment: what it costs, and whether that cost is
    currently payable on this source."""
    cost = "a %s binding consumes the %s right" % (kind, right)
    if not source_id:
        return ("%s; no source was named, so whether that right is granted "
                "is not asked here" % cost)
    if state == "granted":
        return "%s, and %s is granted on this source, so it binds" % (cost,
                                                                      right)
    if state == "denied":
        return ("%s, and %s is denied on this source, so it refuses; a "
                "denial is a decision and reversing it means recording a "
                "new one" % (cost, right))
    return ("%s, and %s is unrecorded on this source, so it refuses: unknown "
            "is restrictive, and finding a file never granted permission to "
            "use it" % (cost, right))


# ---------------------------------------------------------------------------
# the director family (19A-05)
#
# One rule governs all seven and it is the reason the family is worth a wave:
# authority is READ FROM DISK AT CALL TIME and is never a request field. A
# request declares a level; settings grant one; `director.authorize_write`
# compares them and refuses an over-declaration rather than narrowing it. An
# agent that could report its own authority could raise it, which is the
# self-expansion AGENT-02 forbids by name, so there is deliberately no path
# from this namespace to `agent_policy` at all: raising the level is a person
# editing settings, and no route here can do it.
# ---------------------------------------------------------------------------


def _policy(root):
    """The agent policy this installation grants, and where it was read from.

    Reported beside every director answer rather than only consulted, because
    the commonest confusing outcome in this family is a refusal at
    `recommend-only` on a machine whose owner believes they configured
    otherwise, and the useful thing to say is which file was actually read.
    """
    settings_root = os.path.abspath(root)
    settings_data = settings_module.load_settings(settings_root)
    return settings_data, {
        "settings_root": settings_root,
        "granted_level": director.autonomy_level(settings_data),
        "max_bindings_per_operation":
            director.max_bindings_per_operation(settings_data),
    }


def _would_authorize(settings_data, level, bindings):
    """Whether `level` with `bindings` would be permitted, and why not.

    A dry run: `authorize_write` returns None or raises, and it writes
    nothing either way, so asking it is free and asking it beforehand is the
    whole point of the `autonomy` read.
    """
    try:
        director.authorize_write(settings_data, level, bindings)
    except director.DirectorError as err:
        return False, err.code, err.message
    return True, "", ""


def _op_autonomy(root, body, actor_kind, actor_name, base=None):
    """What this installation permits an agent operation to do.

    A read, and the family's answer to a question that previously had none.
    `director.autonomy_level` and `authorize_write` had no reader on any
    surface, so the only way to learn the configured authority was to declare
    a level and be refused, and a refusal after the fact is a worse answer
    than the same fact beforehand.

    Every one of the three levels is dry-run, not just the one asked about,
    so the answer is the whole shape of what is open rather than a yes or a
    no. The binding cap is reported beside it because raising the level alone
    still writes nothing: both settings have to be changed deliberately, and
    a client that saw only the level would misread a cap of zero as a bug.
    """
    base = base or resolve_course(root, body["course_id"])
    settings_data, policy = _policy(root)
    requested = body.get("bindings_requested") or 0
    levels = []
    for level in director.AUTONOMY_LEVELS:
        allowed, code, message = _would_authorize(settings_data, level,
                                                  requested)
        levels.append({"level": level, "authorized": allowed, "code": code,
                       "refusal": message,
                       "writes_bindings":
                           level == director.AUTONOMY_LEVELS[-1]})
    payload = {
        "operation": "autonomy",
        "engine": OPERATION_ENGINE["autonomy"],
        "course_id": body["course_id"],
        "bindings_requested": requested,
        "levels": levels,
        "declared_level": body.get("declared_level") or "",
        "authorized": None,
        "code": "",
        "refusal": "",
    }
    payload.update(policy)
    if body.get("declared_level"):
        allowed, code, message = _would_authorize(
            settings_data, body["declared_level"], requested)
        payload.update({"authorized": allowed, "code": code,
                        "refusal": message})
    payload["explanation"] = _autonomy_sentence(payload)
    return payload


def _autonomy_sentence(payload):
    """One sentence saying what is granted, what that permits, and what a
    declaration would meet."""
    parts = ["this installation grants %s and permits %d binding(s) per "
             "operation, read from %s"
             % (payload["granted_level"],
                payload["max_bindings_per_operation"],
                payload["settings_root"])]
    if payload["max_bindings_per_operation"] == 0:
        parts.append("the cap is zero, so raising the level alone would "
                     "still write no binding; both settings are changed "
                     "deliberately or neither takes effect")
    if payload["declared_level"]:
        if payload["authorized"]:
            parts.append("a %s operation requesting %d binding(s) is within "
                         "policy" % (payload["declared_level"],
                                     payload["bindings_requested"]))
        else:
            parts.append("a %s operation requesting %d binding(s) would be "
                         "refused (%s), and refused rather than narrowed, so "
                         "the over-declaration surfaces"
                         % (payload["declared_level"],
                            payload["bindings_requested"], payload["code"]))
    return "; ".join(parts) + "."


def _op_begin_operation(root, body, actor_kind, actor_name, base=None):
    """Declare an operation's intent, role, authority and scopes.

    Step one of the thirteen, and the only record written before the attempt.
    It writes one journal entry and no file, so it is a write by the spine's
    gate (it appends durable state) while touching no course bytes.

    The declared autonomy is NOT checked here. Declaring an intention is not
    exercising it, and `authorize_write` runs in whichever write follows; a
    check here would refuse a legitimate declaration of what an operation
    hoped to do, and the declaration is exactly the thing worth having on
    disk when the answer turns out to be no.
    """
    base = base or resolve_course(root, body["course_id"])
    _settings_data, policy = _policy(root)
    operation_id = director.begin_operation(
        base, base, body["intent"], actor_kind, actor_name,
        body["actor_role"], body["autonomy"],
        scopes=tuple(body.get("scopes") or ()))
    payload = {
        "operation": "begin_operation",
        "engine": OPERATION_ENGINE["begin_operation"],
        "course_id": body["course_id"],
        "operation_id": operation_id,
        "intent": body["intent"],
        "actor_role": body["actor_role"],
        "declared_autonomy": body["autonomy"],
        "scopes": list(body.get("scopes") or ()),
        "undo": "a declaration wrote no file; `itembank course replay %s "
                "--operation %s` reads what it recorded, and the operation "
                "is abandoned by simply not continuing it, which the replay "
                "then reports as incomplete"
                % (body["course_id"], operation_id),
    }
    payload.update(policy)
    return payload


def _op_replay(root, body, actor_kind, actor_name, base=None):
    """Replay one recorded operation against the thirteen-step protocol.

    A read of the journal and nothing else, which is the assertion rather
    than an implementation detail: an operation resumes because its history
    is on disk, not because a conversation is still open (RELIABILITY-02),
    so this takes an operation id and there is no parameter through which an
    in-memory operation could be handed to it.

    `resume_point` is reported beside the report because it answers the
    question the report leaves open. The report says which steps are missing;
    the resume point says which one comes NEXT, which is what an interrupted
    client actually needs, and it reads the same entries, so serving it here
    costs one call and cannot disagree with the report beside it.

    The egress each phase disclosed is projected out, because it is the one
    thing in this family a learner is owed and it was written to the journal
    with no reader at all: what left this machine, to whom, and what was
    held back and why.
    """
    base = base or resolve_course(root, body["course_id"])
    operation_id = body["operation_id"]
    report = director.replay_operation(base, operation_id)
    entries = director.operation_entries(base, operation_id)
    egress = []
    for entry in entries:
        agent = entry.get("agent") or {}
        record = agent.get("egress")
        if not record:
            continue
        egress.append({
            "phase": agent.get("phase") or "",
            "entry_id": entry.get("entry_id") or "",
            "destination": record.get("destination") or "",
            "backend_class": record.get("backend_class") or "",
            "profile": record.get("profile") or "",
            "spans": len(record.get("spans") or ()),
            "omitted": list(record.get("omitted") or ()),
            "payload_bytes": record.get("payload_bytes"),
            "evidence_included": record.get("evidence_included"),
        })
    payload = dict(report)
    payload.update({
        "operation": "replay",
        "engine": OPERATION_ENGINE["replay"],
        "course_id": body["course_id"],
        "entries": len(entries),
        "resume": director.resume_point(base, operation_id),
        "egress": egress,
        "left_this_machine": [row for row in egress
                              if row["destination"] != "local"],
    })
    return payload


def _op_reverse_operation(root, body, actor_kind, actor_name, base=None):
    """Undo one operation's durable writes, newest first.

    Reaches `journal.undo` through `director.reverse_operation` and adds no
    restore path of its own. That is the point rather than a convenience: a
    second way to put bytes back would make the guarantee that any fault
    leaves the old or the new valid state depend on two implementations
    agreeing about what the old state was, and the moment they disagreed
    nothing could say which was right.

    Entries that wrote no bytes are skipped rather than failed, and reported
    as skipped, so a reversal that restored nothing is legible as an
    operation that had written nothing rather than as one that failed.
    """
    base = base or resolve_course(root, body["course_id"])
    before = director.replay_operation(base, body["operation_id"])
    result = director.reverse_operation(base, body["operation_id"],
                                        actor_kind, actor_name)
    reversed_ids = list(result.get("reversed_entries") or ())
    payload = {
        "operation": "reverse_operation",
        "engine": OPERATION_ENGINE["reverse_operation"],
        "course_id": body["course_id"],
        "operation_id": body["operation_id"],
        "reversed_entries": reversed_ids,
        "restored_revisions": list(result.get("restored_revisions") or ()),
        "complete": result.get("complete"),
        "verdict_before": before.get("verdict"),
        "explanation":
            ("%d journal entry(s) carried a before-image and were restored, "
             "newest first" % len(reversed_ids)) if reversed_ids else
            ("no entry of this operation carried a before-image, so nothing "
             "was restored: it declared and recorded phases without writing "
             "bytes, which is a real state and not a failed reversal"),
        "undo": "a reversal is itself journalled; restoring the state this "
                "call replaced means reversing the restore entries it "
                "wrote, which no surface does yet",
    }
    return payload


def _director_run(root, body, base, actor_kind, actor_name, operation, call):
    """The shape every recommendation answer takes: the policy that governed
    it, what it produced, and what left the machine.

    Factored out because the honest part of a recommendation is not the
    recommendation. It is the authority it ran under and the egress it
    caused, and two separate result bodies would be two chances to report
    one and forget the other.
    """
    settings_data, policy = _policy(root)
    result = call(settings_data)
    payload = {
        "operation": operation,
        "engine": OPERATION_ENGINE[operation],
        "course_id": body["course_id"],
        "declared_autonomy": body["autonomy"],
        "actor_role": body["actor_role"],
        "profile": body.get("profile") or "",
    }
    payload.update(policy)
    payload.update(result)
    return payload


def _op_recommend(root, body, actor_kind, actor_name, base=None):
    """One objective, one recommendation attempt, end to end.

    A backend that is absent, disabled, or times out comes back
    `unavailable` with its typed adapter code, and this returns rather than
    raises, because backend loss is an EXPECTED state: the objective stays
    untreated, the core loop is unaffected, and the caller decides whether
    to retry, hand-author, or move on. A candidate that arrives and fails
    its contract does raise, because that is a broken provider rather than
    an absent one, and the two are not the same fact.

    Nothing is bound here. The recommendation comes back as a validated
    record for a reviewer, and binding it is `apply_recommendation` with its
    own live rights gate; a recommendation that could bind itself would be a
    model choosing what its own output authorizes.
    """
    base = base or resolve_course(root, body["course_id"])

    def call(settings_data):
        result = director.recommend_once(
            base, base, body["objective"], settings_data,
            body.get("profile") or "", actor_kind, actor_name,
            body["actor_role"], body["autonomy"],
            scopes=tuple(body.get("scopes") or ()))
        return {
            "objective": body["objective"],
            "status": result.get("status"),
            "code": result.get("code") or "",
            "record": result.get("record"),
            "operation_id": result.get("operation_id") or "",
            "bound": False,
            "undo": "nothing was bound; this recorded journal entries only, "
                    "and `itembank course reverse-operation` reverses the "
                    "operation id above",
        }

    payload = _director_run(root, body, base, actor_kind, actor_name,
                            "recommend", call)
    if payload["status"] != "ok":
        payload["explanation"] = (
            "no recommendation was received (%s), so the objective stays "
            "untreated with reason backend-unavailable; the core loop is "
            "unaffected and studying, scoring and authored hints keep "
            "working" % (payload["code"] or "the backend did not answer"))
    else:
        payload["explanation"] = (
            "a recommendation was received and validated against the "
            "recommendation contract, and nothing was bound: binding it is "
            "a separate operation that reads the rights again")
    return payload


def _op_recommend_pass(root, body, actor_kind, actor_name, base=None):
    """One pass over many objectives, one entry each.

    Every objective gets exactly one of the three outcomes and none is
    skipped, because a pass whose gaps were invisible is the failure this
    surface exists to prevent. The counts are reported beside the entries so
    a caller reads the shape of the pass without walking it.

    The authority check runs once, before the first objective, inside the
    engine: an over-declaring pass is refused before any binding lands
    rather than after the first one already has. Below
    `approved-bounded-write` nothing binds and every objective comes back
    untreated with its reason, which is a result and not a failure.
    """
    base = base or resolve_course(root, body["course_id"])
    objectives = list(body["objectives"])

    def call(settings_data):
        entries = director.recommend_treatments(
            base, base, objectives, settings_data,
            body.get("profile") or "", actor_kind, actor_name,
            body["actor_role"], body["autonomy"],
            scopes=tuple(body.get("scopes") or ()))
        counts = dict((name, 0) for name in director.RECOMMENDATION_OUTCOMES)
        reasons = {}
        for entry in entries:
            counts[entry["outcome"]] = counts.get(entry["outcome"], 0) + 1
            if entry.get("reason"):
                reasons[entry["reason"]] = reasons.get(entry["reason"], 0) + 1
        return {
            "objectives": objectives,
            "entries": entries,
            "counts": counts,
            "reasons": reasons,
            "undo": "each bound objective is one binding through the same "
                    "gated path a hand binding takes; no surface removes a "
                    "binding, and the reversal is restoring the sidecar's "
                    "previous journalled revision",
        }

    payload = _director_run(root, body, base, actor_kind, actor_name,
                            "recommend_pass", call)
    payload["explanation"] = (
        "%d objective(s) in, %d entry(s) out, one per objective and none "
        "skipped: %s. The pass declared %s and the policy grants %s."
        % (len(objectives), len(payload["entries"]),
           ", ".join("%d %s" % (n, name)
                     for name, n in sorted(payload["counts"].items()) if n)
           or "nothing",
           payload["declared_autonomy"], payload["granted_level"]))
    return payload


def _op_apply_recommendation(root, body, actor_kind, actor_name, base=None):
    """Bind an accepted recommendation, or refuse it against the live rights.

    The record's contract is `schemas/treatment_recommendation.schema.json`
    and `director.validate_recommendation` is what enforces it, called here
    before the engine so a malformed record is refused by name with nothing
    read or written. This module restates none of that contract: one
    published document owns the recommendation shape.

    The coverage state written is `classify_coverage`'s, never the
    provider's, and the source text is supplied so the locator can actually
    resolve; without it the claim is unverifiable and TREAT-02 makes an
    unverifiable claim read `unknown` rather than `covered`. The provider's
    own state is kept beside the computed one as history, which is what lets
    a reviewer see an overclaim that a single merged field would hide.
    """
    base = base or resolve_course(root, body["course_id"])
    record = director.validate_recommendation(body["record"])
    read = course_module.read_course(base)
    revision = director.apply_recommendation(
        base, base, record, body["source"], actor_kind, actor_name,
        operation_id=body.get("operation_id") or "",
        profile_name=body.get("profile") or "",
        source_texts=director.source_texts_for(base, read["doc"]))
    coverage = record.get("coverage") or {}
    return {
        "operation": "apply_recommendation",
        "engine": OPERATION_ENGINE["apply_recommendation"],
        "course_id": body["course_id"],
        "objective": record["objective_id"],
        "source_object_id": body["source"],
        "treatment_kind": record["treatment_kind"],
        "right_consumed": graph.treatment_right(record["treatment_kind"]),
        "locator": coverage.get("locator") or "",
        "proposed_state": coverage.get("state") or "",
        "revision": revision.get("revision"),
        "fingerprint": revision.get("fingerprint"),
        "explanation":
            "the provider proposed coverage %r and the runtime computed the "
            "state that was written; the proposal is kept beside it as "
            "history and no code path reads it back for a decision"
            % (coverage.get("state") or "nothing"),
        "undo": "no surface removes a binding; this row is journalled at "
                "revision %s, so the reversal is restoring the sidecar's "
                "previous revision, or reversing the whole operation with "
                "`itembank course reverse-operation`"
                % revision.get("revision"),
    }


def _op_rights(root, body, actor_kind, actor_name, base=None):
    """Record what the learner declares may be done with one source.

    The bytes are untouched: `journal.op_grant_rights` writes a revision
    record, not the file, so a right can be granted on an accepted artifact
    without editing the accepted artifact. The grant merges, so naming one
    right never resets the others.

    The previous state is read before the write and reported after it,
    because this is the one operation in the family with an exact undo: a
    rights decision is reversed by recording the previous decision, and the
    result says the command that does it.
    """
    base = base or resolve_course(root, body["course_id"])
    source_id = body["source"]
    grants = body["grants"]
    registry = journal.read_registry(base)
    record = registry.get(source_id)
    before = dict((name, identity.rights_state(
        (record or {}).get("rights"), name)) for name in grants)
    result = binding_cli.rights_grant(base, source_id, grants,
                                      actor_kind=actor_kind,
                                      actor_name=actor_name)
    restore = " ".join("--%s %s" % ("grant" if state == "granted" else "deny",
                                    name)
                       for name, state in sorted(before.items())
                       if state in ("granted", "denied"))
    return {
        "operation": "rights",
        "engine": OPERATION_ENGINE["rights"],
        "course_id": body["course_id"],
        "source_object_id": result["source_object_id"],
        "previous": before,
        "recorded": dict(grants),
        "rights": result.get("rights"),
        "revision": result.get("revision"),
        "bytes_touched": False,
        "undo": ("record the previous decision with `itembank bind rights "
                 "--source %s %s`" % (source_id, restore)) if restore else
                ("every right named here was unrecorded before this call, "
                 "and `unknown` cannot be re-recorded as a decision; the "
                 "nearest reversal is `--deny`, which is a decision and not "
                 "an absence"),
    }


def _op_bindings(root, body, actor_kind, actor_name, base=None):
    """Read every binding this course records, with its effective reading.

    A read, and the only operation in this family that writes nothing. It
    answers the question a coverage claim cannot answer about itself: a
    binding stores the rights snapshot it was made under, and that snapshot
    is history the moment the grant behind it changes. So each row is
    reported twice over, once as it was recorded and once as it reads now,
    and a divergence is named rather than left for a person to notice.

    States go through `graph.validate_binding`, so a value this build cannot
    read degrades to `unknown` and never to `covered`. The original is kept
    beside it: an unreadable value is a fact about the row, not a reason to
    silently rewrite it.
    """
    base = base or resolve_course(root, body["course_id"])
    payload = dict(binding_cli.bindings(base))
    statements = dict((row.get("id") or "", row.get("statement") or "")
                      for row in payload.get("objectives") or ())
    titles = dict((row.get("source_object_id") or "", row.get("title") or "")
                  for row in payload.get("sources") or ())
    readings = []
    diverged = 0
    for index, row in enumerate(payload.get("bindings") or ()):
        effective = graph.validate_binding(row)
        source_id = row.get("source_object_id") or ""
        treatment_kind = row.get("treatment_kind") or ""
        if treatment_kind:
            try:
                right = graph.treatment_right(treatment_kind)
            except graph.GraphError:
                # A treatment kind this build does not know consumes a right
                # this build cannot name. Reported as unknown, which is the
                # restrictive reading, rather than guessed at.
                right = ""
        else:
            right = graph.SOURCE_BINDING_RIGHT
        try:
            now = (course_module.rights_for_binding(base, source_id, right)
                   if right else identity.RIGHTS_UNKNOWN)
        except course_module.CourseError:
            now = identity.RIGHTS_UNKNOWN
        snapshot = row.get("rights_snapshot") or ""
        drifted = bool(snapshot) and snapshot != now
        if drifted:
            diverged += 1
        readings.append({
            "index": index,
            "binding_kind": row.get("binding_kind") or "",
            "objective": row.get("objective") or "",
            "objective_statement": statements.get(row.get("objective") or "",
                                                  ""),
            "source_object_id": source_id,
            "source_title": titles.get(source_id, ""),
            "treatment_kind": treatment_kind,
            "locator": row.get("locator") or "",
            "state": effective["state"],
            "original_state": effective["original_state"],
            "state_degraded": effective["state"] !=
                              effective["original_state"],
            "confidence": effective["confidence"],
            "original_confidence": effective["original_confidence"],
            "confidence_degraded": effective["confidence"] !=
                                   effective["original_confidence"],
            "right_consumed": right,
            "rights_snapshot": snapshot,
            "rights_now": now,
            "rights_diverged": drifted,
            "explanation": _binding_sentence(row, effective, right, snapshot,
                                             now),
        })
    payload.update({
        "operation": "bindings",
        "engine": OPERATION_ENGINE["bindings"],
        "course_id": body["course_id"],
        "readings": readings,
        "diverged": diverged,
    })
    return payload


def _op_bind_blueprint(root, body, actor_kind, actor_name, base=None):
    base = base or resolve_course(root, body["course_id"])
    revision = course_module.bind_blueprint(
        base, body["blueprint"], actor_kind, actor_name,
        body.get("expected_fingerprint"))
    read = course_module.read_course(base)
    return {"operation": "bind_blueprint", "engine": OPERATION_ENGINE["bind_blueprint"],
            "course_id": body["course_id"], "course_object_id": read["object_id"],
            "blueprint": body["blueprint"], "fingerprint": read["fingerprint"],
            "revision": revision.get("revision"),
            "undo": "restore the previous course sidecar revision"}


def _op_blueprint_gate(root, body, actor_kind, actor_name, base=None):
    return {"operation": "blueprint_gate", "engine": OPERATION_ENGINE["blueprint_gate"],
            "course_id": body["course_id"],
            "findings": blueprint.blueprint_gate(body.get("questions") or [],
                                                   body.get("blueprint"),
                                                   body.get("item_facts") or {})}


def _op_audit(root, body, actor_kind, actor_name, base=None):
    base = base or resolve_course(root, body["course_id"])
    read = course_module.read_course(base)
    args = {key: body.get(key) for key in (
        "treatment_rows", "coverage_rows", "quality_findings",
        "blueprint_findings", "vocabulary_members")}
    return dict(blueprint.course_audit(read["object_id"],
        course_fingerprint=read["fingerprint"], tool_version=body.get("tool_version") or "",
        **args), operation="audit", engine=OPERATION_ENGINE["audit"], course_id=body["course_id"])


def _op_staleness(root, body, actor_kind, actor_name, base=None):
    return {"operation": "staleness", "engine": OPERATION_ENGINE["staleness"],
            "course_id": body["course_id"],
            "rows": blueprint.staleness_report(body.get("dependents") or [])}


def _relative_package_path(root, package_root):
    return os.path.relpath(package_root, os.path.realpath(root)).replace(
        os.sep, "/")


def _package_result(operation, root, package_root, manifest, verification):
    complete = bool(verification.get("complete"))
    restorable = manifest.get("state") == "applied" and complete
    return {
        "operation": operation,
        "engine": OPERATION_ENGINE[operation],
        "package_id": manifest["package_id"],
        "course_object_id": manifest["course_object_id"],
        "package_path": _relative_package_path(root, package_root),
        "state": manifest["state"],
        "entries_in_manifest": len(manifest["entries"]),
        "entries_verified": verification.get("entries_verified", 0),
        "mismatches": list(verification.get("mismatches") or ()),
        "missing": list(verification.get("missing") or ()),
        "losses": list(manifest["loss_report"]),
        "loss_report_text": course_package.loss_report_text(manifest),
        "rights_basis": "the course sidecar is course-owned; every other "
                        "carried object had package exactly granted at "
                        "export time",
        "remote_egress": "none",
        "complete": complete,
        "restorable": restorable,
        "undo": "remove this package directory only after confirming no "
                "restore still depends on it",
    }


def _op_export_package(root, body, actor_kind, actor_name, base=None):
    """Hold the source snapshot through protected, no-replace publication."""
    base = base or resolve_course(root, body["course_id"])
    with course_package.export_guard(base, base):
        snapshot = course_package.capture_export(
            base, base, expected_fingerprint=body.get("expected_fingerprint"))
        # A separate workspace journal lock serializes identity publication.
        # The source lock is already held if the course is the workspace root.
        if os.path.realpath(base) == os.path.realpath(root):
            return _publish_export(root, body, base, snapshot)
        with journal._journal_lock(root):
            return _publish_export(root, body, base, snapshot)


def _publish_export(root, body, base, snapshot):
    manifest = snapshot["manifest"]
    package_id = manifest["package_id"]
    package_root = course_package.workspace_package_path(root, package_id)
    staging = course_package.workspace_package_path(root, package_id,
                                                     "staging")
    if os.path.lexists(package_root) or os.path.lexists(staging):
        raise course_package.PackageError(
            "package.export_collision",
            "package %s already has a final or staged directory; no existing "
            "package was overwritten" % package_id)
    course_package.ensure_package_namespace(root)
    with course_package.private_stage(root) as staging:
        manifest = course_package.export_package(base, base, staging, _snapshot=snapshot)
        verification = course_package.verify_manifest(staging)
        if not verification["complete"]:
            raise course_package.PackageError(
                "package.export_incomplete", "the staged package did not verify completely")
        course_package.recheck_export(base, base, snapshot)
        course_package.publish_directory(root, staging, package_root)
    result = _package_result("export_package", root, package_root, manifest,
                             verification)
    result["course_id"] = body["course_id"]
    result["undo"] = ("remove %s only after confirming no restore still "
                      "depends on it" % result["package_path"])
    return result


def _package_read(root, body, operation):
    package_id = body["package_id"]
    package_root = course_package.workspace_package_path(root, package_id)
    snapshot = course_package.package_snapshot(
        package_root, expected_package_id=package_id, workspace_root=root)
    manifest = snapshot["manifest"]
    verification = snapshot["verification"]
    return _package_result(operation, root, package_root, manifest,
                           verification)


def _op_verify_package(root, body, actor_kind, actor_name, base=None):
    result = _package_read(root, body, "verify_package")
    result["undo"] = "verification is read-only; there is nothing to undo"
    return result


def _op_package_losses(root, body, actor_kind, actor_name, base=None):
    result = _package_read(root, body, "package_losses")
    result["undo"] = "reading a loss report changes nothing"
    return result


def _existing_course_identity(root, course_object_id):
    return ia.course_dir_for(root, course_object_id, module=course_module)


def _op_restore_package(root, body, actor_kind, actor_name, base=None):
    """Restore into a fresh stage, then publish under course identity."""
    package_root = course_package.workspace_package_path(root, body["package_id"])
    snapshot = course_package.package_snapshot(
        package_root, expected_package_id=body["package_id"], workspace_root=root)
    if snapshot["manifest"]["state"] != "applied":
        raise course_package.PackageError("package.not_applied", "the package is not applied")
    if not snapshot["verification"]["complete"]:
        raise course_package.PackageError("package.restore_incomplete",
                                          "the package did not verify completely and was not published")
    with journal._journal_lock(root):
        return _restore_and_publish(root, body, actor_kind, actor_name, snapshot)


def _restore_and_publish(root, body, actor_kind, actor_name, snapshot):
    package_id = body["package_id"]
    package_root = course_package.workspace_package_path(root, package_id)
    manifest = snapshot["manifest"]
    if manifest["state"] != "applied":
        raise course_package.PackageError(
            "package.not_applied",
            "this package's manifest state is %s, not applied; it must not "
            "be restored" % manifest["state"])
    course_object_id = manifest["course_object_id"]
    destination = os.path.join(os.path.realpath(root), course_object_id)
    if os.path.lexists(destination):
        raise course_package.PackageError(
            "package.destination_exists",
            "restore destination %s already exists; restore requires a fresh "
            "course directory" % course_object_id)
    duplicate = _existing_course_identity(root, course_object_id)
    if duplicate is not None:
        raise course_package.PackageError(
            "package.duplicate_course",
            "course identity %s already exists at %s; a restore never creates "
            "a second copy of one identity"
            % (course_object_id, os.path.basename(duplicate)))

    digest = course_package._digest(snapshot["manifest_raw"]).split(":", 1)[1]
    restore_leaf = package_id + "-" + digest
    restore_base = course_package.workspace_package_path(root, package_id,
                                                          "restore")
    staging = restore_base + "-" + digest
    if os.path.lexists(staging):
        raise course_package.PackageError(
            "package.restore_collision",
            "restore staging directory %s already exists; no staged work was "
            "overwritten" % restore_leaf)

    if not snapshot["verification"]["complete"]:
        raise course_package.PackageError("package.restore_incomplete",
                                          "the package did not verify completely and was not published")
    with course_package.private_stage(root) as staging:
        restored = course_package.restore_package(package_root, staging,
            actor_kind, actor_name, _snapshot=snapshot)
        restored_course = course_module.read_course(staging)
        if restored_course["object_id"] != course_object_id or not restored["complete"]:
            raise course_package.PackageError(
                "package.restore_incomplete", "the staged restore did not produce the declared course")
        if os.path.lexists(destination) or _existing_course_identity(root, course_object_id) is not None:
            raise course_package.PackageError(
                "package.duplicate_course", "the course identity appeared while restore was staged")
        course_package.publish_directory(root, staging, destination)

    verification = snapshot["verification"]
    result = _package_result("restore_package", root, package_root, manifest,
                             verification)
    result.update({
        "course_path": course_object_id,
        "entries_restored": restored["entries_verified"],
        "restore_losses": list(restored["restore_losses"]),
        "evidence_recorded": restored["evidence_recorded"],
        "evidence_already_recorded": restored["evidence_already_recorded"],
        "complete": bool(restored["complete"] and verification["complete"]),
        "restorable": bool(restored["complete"] and verification["complete"]
                            and manifest["state"] == "applied"),
        "undo": "move the restored course directory %s to trash if no later "
                "work depends on it; the package remains unchanged"
                % course_object_id,
    })
    return result


def _binding_sentence(row, effective, right, snapshot, now):
    """One sentence saying what this binding claims and whether it still
    stands, in the order a person asks it: what is claimed, how sure, on
    what right, and whether that right still holds."""
    kind = row.get("binding_kind") or "source"
    what = ("%s treatment" % row.get("treatment_kind")) if kind == "treatment"         else "source"
    parts = ["this %s binding claims coverage of the objective is %s, at %s "
             "confidence" % (what, effective["state"], effective["confidence"])]
    if effective["state"] != effective["original_state"]:
        parts.append("the recorded state %r is not one this build reads, so "
                     "it degrades to unknown rather than to covered"
                     % effective["original_state"])
    if not right:
        parts.append("the right it consumes is not one this build names, so "
                     "it reads as unknown, which refuses")
    elif not snapshot:
        parts.append("it recorded no rights snapshot, so what was granted "
                     "when it was made is not known; the %s right is %s now"
                     % (right, now))
    elif snapshot != now:
        parts.append("it was recorded when the %s right was %s, and that "
                     "right is %s now, so the claim rests on a right that "
                     "has since changed" % (right, snapshot, now))
    else:
        parts.append("the %s right was %s when it was made and is %s now"
                     % (right, snapshot, now))
    return "; ".join(parts) + "."


def _edit_sidecar(root, body, base, actor_kind, actor_name, change):
    """Read a course sidecar, let `change` edit the parsed document, and
    write it back through the one compare-and-swap path.

    Every 19A-03 operation is this shape, and factoring it out is not
    tidiness: it is what keeps `journal.OPERATION_TYPES` at six. Each of the
    eight is an `edit_in_place` on one file, so if each wrote its own read
    and write there would be eight chances to forget the expected
    fingerprint, and a durable write without one is the silent overwrite the
    compare-and-swap rule exists to prevent.

    `change` returns whatever it wants reported; this returns the revision
    beside it and never inspects it.
    """
    base = base or resolve_course(root, body["course_id"])
    read = course_module.read_course(base)
    doc = read["doc"]
    result = change(doc)
    revision = course_module.write_course(
        base, doc, body.get("expected_fingerprint") or read["fingerprint"],
        actor_kind, actor_name)
    return base, read, result, revision


def _edit_result(operation, body, read, revision, extra):
    """The shape every structural write answers with: what it did, which
    engine function did it, where the sidecar now stands, and how to reverse
    it."""
    payload = {
        "operation": operation,
        "engine": OPERATION_ENGINE[operation],
        "course_id": body["course_id"],
        "course_object_id": read["object_id"],
        "fingerprint": revision.get("fingerprint"),
        "revision": revision.get("revision"),
    }
    payload.update(extra)
    payload.setdefault(
        "undo",
        "this is one edit_in_place on the sidecar at revision %s; no surface "
        "removes a structural row yet, so the reversal is restoring the "
        "sidecar's previous revision from the operation journal"
        % revision.get("revision"))
    return payload


def _op_add_container(root, body, actor_kind, actor_name, base=None):
    """Add one structural container.

    Zero edges, deliberately: where a container sits in the outline is
    structure, and structure is not a prerequisite claim (GRAPH-01). A course
    whose week 2 follows week 1 has said nothing about what must be learned
    first, and inferring otherwise is the kind of guess that ends up gating a
    learner.
    """
    def change(doc):
        if body.get("parent"):
            known = set(row.get("id") for row in doc.get("structure") or ())
            if body["parent"] not in known:
                raise course_module.CourseError(
                    "course.unknown_container",
                    "%s is not a container in this course, so nothing was "
                    "written. Next safe action: read the course's structure "
                    "with `itembank course structure %s`, or add the parent "
                    "first." % (body["parent"], body["course_id"]))
        return graph.add_container(doc, body["label"], body["title"],
                                   parent=body.get("parent") or "",
                                   order=body.get("order"))

    base, read, record, revision = _edit_sidecar(
        root, body, base, actor_kind, actor_name, change)
    return _edit_result("add_container", body, read, revision, {
        "container_id": record["id"],
        "label": record["label"],
        "title": record["title"],
        "parent": record.get("parent", ""),
        "order": record.get("order", ""),
    })


def _op_add_objective(root, body, actor_kind, actor_name, base=None):
    """Add one objective, always with origin `local`.

    A request cannot claim `imported`, and the node does not carry the field.
    An imported scope binds as an immutable version under GRAPH-01, so a
    hand-authored row that claimed that origin would become un-editable for a
    reason that was never true, and the only way back would be an overlay
    onto an import that never happened.
    """
    def change(doc):
        if body.get("container"):
            known = set(row.get("id") for row in doc.get("structure") or ())
            if body["container"] not in known:
                raise course_module.CourseError(
                    "course.unknown_container",
                    "%s is not a container in this course, so nothing was "
                    "written. Next safe action: add it with `itembank course "
                    "add-container`, or leave the objective unplaced, which "
                    "is a real state and not an error." % body["container"])
        return graph.add_objective(doc, body["statement"],
                                   container=body.get("container") or "",
                                   order=body.get("order"))

    base, read, record, revision = _edit_sidecar(
        root, body, base, actor_kind, actor_name, change)
    return _edit_result("add_objective", body, read, revision, {
        "objective_id": record["id"],
        "statement": record["statement"],
        "container": record.get("container", ""),
        "order": record.get("order", ""),
        "origin": record.get("origin", ""),
    })


def _op_add_edge(root, body, actor_kind, actor_name, base=None):
    """Add one edge between two endpoints the graph already holds.

    Three refusals belong to `graph.add_edge` and are left there: a self
    edge, a duplicate key, and an unknown endpoint. This adds none of its
    own, because a second copy of a rule is a second place for it to be
    wrong.
    """
    def change(doc):
        return graph.add_edge(
            doc, body["source"], body["edge_type"], body["target"],
            authority=body.get("authority") or
            graph.EDGE_FIELD_DEFAULTS["authority"],
            rationale=body.get("rationale") or "",
            confidence=body.get("confidence") or
            graph.EDGE_FIELD_DEFAULTS["confidence"],
            override=body.get("override") or
            graph.EDGE_FIELD_DEFAULTS["override"])

    base, read, record, revision = _edit_sidecar(
        root, body, base, actor_kind, actor_name, change)
    effective = graph.validate_edge(record)
    warnings = graph.validate_order(course_module.read_course(base)["doc"])
    return _edit_result("add_edge", body, read, revision, {
        "source": record["source"],
        "edge_type": record["edge_type"],
        "target": record["target"],
        "authority": record["authority"],
        "confidence": record["confidence"],
        "override": record["override"],
        "rationale": record.get("rationale", ""),
        "effective_type": effective["effective_type"],
        # The edge is recorded either way. A prerequisite that now points
        # backwards through the authored order is a warning and never a
        # refusal, because the authored order is the human's and reordering
        # it silently is what this whole module refuses to do.
        "order_warnings": warnings,
        "undo": "an edge is identified by (source, edge_type, target) and no "
                "surface removes one yet; the reversal is restoring the "
                "sidecar's previous revision from the operation journal",
    })


def _op_structure(root, body, actor_kind, actor_name, base=None):
    """Read the containers, objectives and edges, with each edge's effective
    reading and the warnings the authored order earns.

    Reports and never corrects. `graph.validate_order` returns one warning
    per violated prerequisite plus one naming a cycle, and both are left as
    warnings: the authored sequence is what a person wrote, and a projection
    that silently reorders makes every future diff unreadable.

    `propose_order` is opt in and returns a sequence rather than writing one,
    which is the difference between offering a course a better order and
    taking the ordering decision away from its author.
    """
    base = base or resolve_course(root, body["course_id"])
    read = course_module.read_course(base)
    doc = read["doc"]
    containers = [{"id": row.get("id") or "", "label": row.get("label") or "",
                   "title": row.get("title") or "",
                   "parent": row.get("parent") or "",
                   "order": row.get("order") or ""}
                  for row in doc.get("structure") or ()]
    objectives = [{"id": row.get("id") or "",
                   "statement": row.get("statement") or "",
                   "container": row.get("container") or "",
                   "order": row.get("order") or "",
                   "origin": row.get("origin") or "",
                   "overlays": row.get("overlays") or ""}
                  for row in doc.get("objectives") or ()]
    edges = []
    for row in doc.get("edges") or ():
        effective = graph.validate_edge(row)
        edges.append({
            "source": effective["source"], "target": effective["target"],
            "edge_type": effective["effective_type"],
            "original_type": effective["original_type"],
            "type_degraded": effective["effective_type"] !=
                             effective["original_type"],
            "authority": effective["authority"],
            "confidence": effective["confidence"],
            "override": effective["override"],
            "rationale": effective["rationale"],
        })
    payload = {
        "operation": "structure",
        "engine": OPERATION_ENGINE["structure"],
        "course_id": body["course_id"],
        "course_object_id": read["object_id"],
        "fingerprint": read["fingerprint"],
        "containers": containers,
        "objectives": objectives,
        "edges": edges,
        "order_warnings": graph.validate_order(doc),
        "edge_types": list(graph.EDGE_TYPES),
        "authorities": list(graph.EDGE_AUTHORITIES),
        "overrides": list(graph.EDGE_OVERRIDES),
        "proposed_order": None,
        "proposed_order_refused": "",
    }
    if body.get("propose_order"):
        pairs = [(e["source"], e["target"]) for e in edges
                 if e["edge_type"] == "prerequisite-of"]
        try:
            payload["proposed_order"] = graph.propose_order(
                [o["id"] for o in objectives], pairs)
        except graph.GraphError as err:
            # A cycle is reported and never broken. Returning the refusal as
            # a sentence rather than raising keeps the rest of the reading
            # available: a course with a cycle is exactly the course whose
            # structure someone needs to look at.
            payload["proposed_order_refused"] = err.message
    return payload


def _proposal_result(operation, body, read, revision, proposal, extra):
    """The shape the four identity operations answer with.

    Every one of them adds rows and deletes none, and every one records the
    migration as `proposed`. Saying so in the result matters more than it
    looks: a caller that read "renamed" and stopped would not know that the
    old identity is still in the file, still carries the evidence, and is
    still what a report counts until a reviewer settles the migration.
    """
    payload = _edit_result(operation, body, read, revision, extra)
    payload.update({
        "migration_id": proposal.get("migration_id"),
        "migration_kind": proposal.get("kind"),
        "migration_state": proposal.get("state"),
        "rationale": proposal.get("rationale"),
        "settled": False,
        "note": "the original row is untouched and still carries whatever "
                "evidence was recorded against it; this migration is "
                "recorded %s and a reviewer settles it"
                % proposal.get("state"),
        "undo": "reject the migration rather than deleting a row: nothing in "
                "an identity chain is ever removed, and accepting or "
                "rejecting %s is the settlement"
                % proposal.get("migration_id"),
    })
    return payload


def _op_rename_objective(root, body, actor_kind, actor_name, base=None):
    """Restate one objective as a reviewed proposal.

    A new row plus a migration, never an edit to the original. An imported
    objective refuses here by name, and the refusal says which operation to
    use instead, because "you may not edit this" without "here is what you
    may do" is half an answer.
    """
    holder = {}

    def change(doc):
        record, proposal = graph.rename_objective(
            doc, body["objective"], body["statement"], body["rationale"],
            actor_name or actor_kind)
        holder["proposal"] = proposal
        return record

    base, read, record, revision = _edit_sidecar(
        root, body, base, actor_kind, actor_name, change)
    return _proposal_result("rename_objective", body, read, revision,
                            holder["proposal"], {
                                "objective": body["objective"],
                                "successor_id": record["id"],
                                "statement": record["statement"],
                            })


def _op_split_objective(root, body, actor_kind, actor_name, base=None):
    """Split one objective into several as a reviewed proposal."""
    holder = {}

    def change(doc):
        records, proposal = graph.split_objective(
            doc, body["objective"], list(body["statements"]),
            body["rationale"], actor_name or actor_kind)
        holder["proposal"] = proposal
        return records

    base, read, records, revision = _edit_sidecar(
        root, body, base, actor_kind, actor_name, change)
    return _proposal_result("split_objective", body, read, revision,
                            holder["proposal"], {
                                "objective": body["objective"],
                                "successor_ids": [r["id"] for r in records],
                                "statements": [r["statement"]
                                               for r in records],
                                "evidence_note": "each new identity reads "
                                                 "unknown for evidence until "
                                                 "evidence is recorded "
                                                 "against it; unknown is not "
                                                 "zero progress",
                            })


def _op_merge_objectives(root, body, actor_kind, actor_name, base=None):
    """Merge several objectives into one as a reviewed proposal."""
    holder = {}

    def change(doc):
        record, proposal = graph.merge_objectives(
            doc, list(body["objectives"]), body["statement"],
            body["rationale"], actor_name or actor_kind)
        holder["proposal"] = proposal
        return record

    base, read, record, revision = _edit_sidecar(
        root, body, base, actor_kind, actor_name, change)
    return _proposal_result("merge_objectives", body, read, revision,
                            holder["proposal"], {
                                "objectives": list(body["objectives"]),
                                "successor_id": record["id"],
                                "statement": record["statement"],
                            })


def _op_overlay_objective(root, body, actor_kind, actor_name, base=None):
    """Record a local revision of an imported objective as a sibling row.

    The operation to reach for when a rename refuses because its target was
    imported. It is true by construction rather than by care that the import
    is untouched: an overlay is a new row joined to the import by an
    `overlays` reference, and no code path here opens the imported row for
    writing.
    """
    def change(doc):
        return graph.overlay_objective(doc, body["objective"],
                                       body["statement"],
                                       actor_name or actor_kind)

    base, read, record, revision = _edit_sidecar(
        root, body, base, actor_kind, actor_name, change)
    migrations = course_module.read_course(base)["doc"].get("migrations") or ()
    proposal = dict(migrations[-1]) if migrations else {}
    return _proposal_result("overlay_objective", body, read, revision,
                            proposal, {
                                "objective": body["objective"],
                                "overlay_id": record["id"],
                                "statement": record["statement"],
                                "overlays": record.get("overlays", ""),
                            })


def _op_settle_migration(root, body, actor_kind, actor_name, base=None):
    """Settle one proposal in one operation-identified CAS revision.

    The operation marker rides on the applied file entry rather than being a
    second journal row. That lets `reverse_operation` find exactly the write
    whose before-image restores the proposal, while keeping settlement and
    recovery on the existing course and journal authorities.
    """
    base = base or resolve_course(root, body["course_id"])
    read = course_module.read_course(base)
    operation_id = body.get("operation_id") or director.new_operation_id()
    decision = ("accepted" if body["operation"] == "accept_migration"
                else "rejected")
    fn = (course_module.accept_migration if body["operation"] == "accept_migration"
          else course_module.reject_migration)
    # Reuse the director's one frozen AGENT_ENTRY_KEYS builder. A local dict
    # would be a second grammar for the operation marker and could drift from
    # the reader that powers `reverse_operation`.
    applied_agent = director._agent_dict(
        operation_id,
        "%s migration %s" % (decision, body["migration_id"]),
        "reviewer", "human", ("course:%s" % body["course_id"],),
        "accept", 3,
        director._checkpoint_with_outcome(None, "recorded", ""),
        {"migration_id": body["migration_id"], "decision": decision},
        director.egress_record("local", "local", "", [], [], 0))
    revision = fn(base, body["migration_id"], actor_kind, actor_name,
                  body["rationale"], body.get("expected_fingerprint"),
                  applied_agent=applied_agent)
    return {
        "operation": body["operation"],
        "engine": OPERATION_ENGINE[body["operation"]],
        "course_id": body["course_id"],
        "course_object_id": read["object_id"],
        "operation_id": operation_id,
        "migration_id": body["migration_id"],
        "migration_state": decision,
        "fingerprint": revision.get("fingerprint"),
        "revision": revision.get("revision"),
        "settled": True,
        "undo": "reverse operation %s to restore the exact sidecar bytes "
                "from before this settlement; the proposal and all evidence "
                "remain recorded" % operation_id,
    }


OPERATIONS = {
    "create": _op_create,
    "rename": _op_rename,
    "add_source": _op_add_source,
    "bind": _op_bind,
    "bind_treatment": _op_bind_treatment,
    "treatments": _op_treatments,
    "autonomy": _op_autonomy,
    "begin_operation": _op_begin_operation,
    "replay": _op_replay,
    "reverse_operation": _op_reverse_operation,
    "recommend": _op_recommend,
    "recommend_pass": _op_recommend_pass,
    "apply_recommendation": _op_apply_recommendation,
    "rights": _op_rights,
    "bindings": _op_bindings,
    "add_container": _op_add_container,
    "add_objective": _op_add_objective,
    "add_edge": _op_add_edge,
    "structure": _op_structure,
    "rename_objective": _op_rename_objective,
    "split_objective": _op_split_objective,
    "merge_objectives": _op_merge_objectives,
    "overlay_objective": _op_overlay_objective,
    "accept_migration": _op_settle_migration,
    "reject_migration": _op_settle_migration,
    "bind_blueprint": _op_bind_blueprint,
    "blueprint_gate": _op_blueprint_gate,
    "audit": _op_audit,
    "staleness": _op_staleness,
    "export_package": _op_export_package,
    "verify_package": _op_verify_package,
    "restore_package": _op_restore_package,
    "package_losses": _op_package_losses,
}


def run(root, operation, request, actor_kind="human", actor_name="",
        base=None):
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
    # The actor KIND is the surface's to decide and never the request's, and
    # for three operations the surface decides `agent` because a model
    # produced what they record (19A-05). Chosen by what the operation does,
    # the same way the loopback gate is, rather than by what a caller claims:
    # recording a model's recommendation as a human's work would put a false
    # origin in the durable record, and a request that could set this could
    # launder one.
    kind = OPERATION_ACTOR_KIND.get(operation, actor_kind)
    return OPERATIONS[operation](root, body, kind,
                                 actor_name or body.get("actor") or "",
                                 base)


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


def _print_structure(payload):
    """`itembank course structure` in plain text: the outline as authored,
    the edges as this build reads them, and the warnings the order earns."""
    print("%s  %s" % (payload["course_object_id"], payload["course_id"]))
    print("\nContainers (%d)" % len(payload["containers"]))
    for row in payload["containers"]:
        print("  %s  %-9s %s%s"
              % (row["id"], row["label"], row["title"],
                 "  in %s" % row["parent"] if row["parent"] else ""))
    print("\nObjectives (%d)" % len(payload["objectives"]))
    for row in payload["objectives"]:
        print("  %s  %s" % (row["id"], row["statement"][:84]))
        if row["overlays"]:
            print("      overlays %s" % row["overlays"])
    print("\nEdges (%d)" % len(payload["edges"]))
    for row in payload["edges"]:
        print("  %s %s %s  (%s, %s, %s)"
              % (row["source"], row["edge_type"], row["target"],
                 row["authority"], row["confidence"], row["override"]))
        if row["type_degraded"]:
            print("      recorded as %r, which this build does not read, so "
                  "it is advisory and blocks nothing" % row["original_type"])
        if row["rationale"]:
            print("      %s" % row["rationale"])
    if payload["order_warnings"]:
        print("\nOrder warnings (%d). The authored order is unchanged; these "
              "are for review." % len(payload["order_warnings"]))
        for line in payload["order_warnings"]:
            print("  - %s" % line)
    if payload["proposed_order"]:
        print("\nA proposed order satisfying every prerequisite (not "
              "written):")
        for oid in payload["proposed_order"]:
            print("  %s" % oid)
    if payload["proposed_order_refused"]:
        print("\nNo order can be proposed: %s"
              % payload["proposed_order_refused"])


def _print_autonomy(payload):
    """`itembank course autonomy` in plain text: what is granted, what each
    of the three levels would meet, and where the answer was read from."""
    print("Agent policy read from %s" % payload["settings_root"])
    print("  granted level: %s" % payload["granted_level"])
    print("  bindings permitted per operation: %d"
          % payload["max_bindings_per_operation"])
    print("\nDeclaring each level, with %d binding(s) requested:"
          % payload["bindings_requested"])
    for row in payload["levels"]:
        print("  %s %-24s %s"
              % ("ok" if row["authorized"] else "no", row["level"],
                 row["refusal"] or ("writes bindings"
                                    if row["writes_bindings"]
                                    else "proposes, writes no binding")))
    print("\n%s" % payload["explanation"])


def _print_replay(payload):
    """`itembank course replay`: the thirteen steps as recorded, where an
    interrupted operation resumes, and what left this machine."""
    print("%s  %d journal entry(s), verdict %s"
          % (payload["operation_id"] or "(no operation id)",
             payload["entries"], payload["verdict"]))
    print("\nProtocol steps")
    for row in payload["steps"]:
        print("  %2d %-24s %-15s %s"
              % (row["index"], row["step"], row["outcome"],
                 row["reason"] or ""))
    if payload["out_of_order"]:
        print("\nRecorded out of the contract's order (named, never "
              "sorted): %s" % ", ".join(payload["out_of_order"]))
    resume = payload["resume"]
    print("\nResume: %s"
          % ("stopped after %s, next is %s"
             % (resume["last_phase"], resume["next_phase"])
             if resume["resumable"]
             else "not resumable (%s)" % (resume["reason"] or "unknown")))
    print("\nEgress (%d phase(s) recorded one)" % len(payload["egress"]))
    for row in payload["egress"]:
        print("  %-15s %-16s %-12s %d span(s), %s byte(s), evidence %s"
              % (row["phase"], row["destination"],
                 row["profile"] or row["backend_class"], row["spans"],
                 row["payload_bytes"], row["evidence_included"]))
        for omission in row["omitted"]:
            print("      held back: %s" % omission)
    if not payload["left_this_machine"]:
        print("  nothing left this machine.")
    if payload["reason"]:
        print("\n%s" % payload["reason"])


def _print_director(operation, payload):
    """One human block per director write. Each ends with the authority it
    ran under, because that is the thing a reader most often needs and the
    thing a result body most easily leaves out."""
    if operation == "begin_operation":
        print("declared %s" % payload["operation_id"])
        print("  intent: %s" % payload["intent"])
        print("  role %s, declaring %s, scopes %s"
              % (payload["actor_role"], payload["declared_autonomy"],
                 ", ".join(payload["scopes"]) or "(none declared)"))
    elif operation == "reverse_operation":
        print("reversed %s: %d entry(s) restored"
              % (payload["operation_id"], len(payload["reversed_entries"])))
        for entry_id, revision in zip(payload["reversed_entries"],
                                      payload["restored_revisions"]):
            print("  %s restored to revision %s" % (entry_id, revision))
        print("  %s" % payload["explanation"])
    elif operation == "recommend":
        print("%s for %s" % (payload["status"], payload["objective"]))
        record = payload["record"] or {}
        if record:
            print("  proposed treatment: %s (confidence %s)"
                  % (record.get("treatment_kind") or "(none named)",
                     record.get("confidence") or "unknown"))
            print("  operation %s" % payload["operation_id"])
        print("  %s" % payload["explanation"])
    elif operation == "recommend_pass":
        for entry in payload["entries"]:
            print("  %-9s %-20s %s%s"
                  % (entry["outcome"], entry["objective_id"],
                     entry["treatment_kind"] or "(no treatment)",
                     "  %s" % entry["reason"] if entry["reason"] else ""))
        print("\n%s" % payload["explanation"])
    elif operation == "apply_recommendation":
        print("bound %s -> %s (%s, consumes %s) at revision %s"
              % (payload["objective"], payload["source_object_id"],
                 payload["treatment_kind"], payload["right_consumed"],
                 payload["revision"]))
        print("  %s" % payload["explanation"])
    if operation in ("recommend", "recommend_pass"):
        print("  policy: %s granted, %d binding(s) per operation, read from %s"
              % (payload["granted_level"],
                 payload["max_bindings_per_operation"],
                 payload["settings_root"]))
    print("  undo: %s" % payload["undo"])


def _print_result(operation, payload):
    """One human line per operation, then the two lines every write ends
    with. A `--json` caller gets the whole payload instead."""
    if operation == "create":
        print("created %s (%s) at revision %s"
              % (payload["title"], payload["course_object_id"],
                 payload["revision"]))
    elif operation == "rename":
        print("renamed %s from %s to %s at revision %s"
              % (payload["course_object_id"], payload["previous_title"],
                 payload["title"], payload["revision"]))
    elif operation == "add_source":
        print("recorded source %s (%s) at revision %s"
              % (payload["title"], payload["source_object_id"],
                 payload["revision"]))
        print("  rights: %s"
              % ", ".join("%s=%s" % (k, v) for k, v
                          in sorted((payload["rights"] or {}).items())))
        if not payload["bindable"]:
            print("  the %s right is not granted, so binding this source "
                  "refuses until it is: itembank bind rights --source %s "
                  "--grant %s"
                  % (graph.SOURCE_BINDING_RIGHT, payload["source_object_id"],
                     graph.SOURCE_BINDING_RIGHT))
    elif operation == "add_container":
        print("added container %s (%s %s) at revision %s"
              % (payload["container_id"], payload["label"], payload["title"],
                 payload["revision"]))
    elif operation == "add_objective":
        print("added objective %s at revision %s"
              % (payload["objective_id"], payload["revision"]))
        print("  %s" % payload["statement"])
    elif operation == "add_edge":
        print("recorded %s %s %s at revision %s"
              % (payload["source"], payload["edge_type"], payload["target"],
                 payload["revision"]))
        for line in payload["order_warnings"]:
            print("  warning: %s" % line)
    elif operation in ("rename_objective", "split_objective",
                       "merge_objectives", "overlay_objective"):
        made = payload.get("successor_ids") or [payload.get("successor_id")
                                                or payload.get("overlay_id")]
        kind = payload["migration_kind"] or ""
        print("proposed %s %s at revision %s: %s -> %s"
              % ("an" if kind[:1] in "aeiou" else "a", kind,
                 payload["revision"],
                 payload.get("objective")
                 or ", ".join(payload.get("objectives") or ()),
                 ", ".join(m for m in made if m)))
        print("  migration %s is %s"
              % (payload["migration_id"], payload["migration_state"]))
        print("  %s" % payload["note"])
    elif operation in ("accept_migration", "reject_migration"):
        print("%s migration %s at revision %s"
              % (payload["migration_state"], payload["migration_id"],
                 payload["revision"]))
        print("  operation %s" % payload["operation_id"])
    print("  fingerprint %s" % payload["fingerprint"])
    print("  undo: %s" % payload["undo"])


def cmd_course(a):
    """`itembank course` -- the CLI twin of `POST /api/course/<operation>`.

    Every action reaches `run` or `show`, the same functions the routes call,
    so the twin is one call and not a similar print (D-03).

    The request is built from the operation's own published node rather than
    field by field: each property the node declares is filled from the
    argparse attribute of the same name, so adding an operation is adding a
    `$defs` node and a parser and nothing here. That is the same property
    that makes the Phase 999.3 tool table mechanical, applied to the surface
    that already exists, and it means a field the document publishes and the
    parser forgot is a visible gap rather than a silently dropped argument.
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
        # The subcommand name is the operation name, with the one spelling
        # difference a command line wants: a hyphen reads better in a shell
        # and an underscore is what a JSON field is called.
        operation = a.action.replace("-", "_")
        node, _document = operation_schema(operation)
        request = {}
        for identity_field in ("course_id", "package_id"):
            value = getattr(a, identity_field, None)
            if value:
                request[identity_field] = value
        for name in node.get("properties") or ():
            if name in ("operation", "course_id"):
                continue
            value = getattr(a, name, None)
            if value is None or value == "" or value == []:
                continue
            request[name] = value
        payload = run(a.root, operation, request, actor_kind="human",
                      actor_name=getattr(a, "actor", "") or "")
        if getattr(a, "json", False):
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 0
        if operation == "structure":
            _print_structure(payload)
            return 0
        if operation == "autonomy":
            _print_autonomy(payload)
            return 0
        if operation == "replay":
            _print_replay(payload)
            return 0
        if operation in DIRECTOR_WRITES:
            _print_director(operation, payload)
            return 0
        if operation in ("export_package", "verify_package",
                         "restore_package", "package_losses"):
            print("%s %s" % (operation.replace("_", " "),
                             payload["package_id"]))
            print("  package: %s" % payload["package_path"])
            print("  complete: %s; restorable: %s; remote egress: %s"
                  % (payload["complete"], payload["restorable"],
                     payload["remote_egress"]))
            print(payload["loss_report_text"].rstrip())
            print("  undo: %s" % payload["undo"])
            return 0
        _print_result(operation, payload)
        return 0
    except (course_module.CourseError, graph.GraphError,
            journal.JournalError, director.DirectorError,
            course_package.PackageError) as err:
        sys.exit("%s: %s" % (err.code, err.message))
