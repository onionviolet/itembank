"""Binding a source to an objective, from a surface.

The 2026-09-05 surface grid measured `source binding / create` as empty, and
called it the central act of building a course: `course.bind_source` and
`course.bind_treatment` are implemented, gated on rights, journaled, and
reachable only by importing Python. `objective / explain` was empty for the
same reason from the other side: an objective's cited passage is recorded in
the sidecar and shown to nobody.

This module is the CLI half of that door and the daemon route's own
implementation, so both surfaces reach the same three functions rather than
two copies of the same argument handling. It adds no authority: every write
goes through `course.bind_source` / `course.bind_treatment`, which refuse
unless the right the treatment consumes is exactly granted, and the sidecar
write is the compare-and-swap one `course.write_course` already performs.

Rights are the reason binding refuses more often than it succeeds, and the
refusal is the useful half: a source found on disk is not a source you may
build a course out of. `rights_grant` records the learner's own declaration
about their own file through `journal.op_grant_rights`, which touches no
bytes; it is the same act `itembank source import --grant` performs at link
time, available afterwards, because a decision about a file should not
require re-importing it.
"""
import json
import os
import sys

import course as course_module
import graph
import identity
import journal


BINDING_KINDS = graph.BINDING_KINDS


def _course_base(base):
    path = os.path.abspath(base)
    if not os.path.isdir(path):
        raise course_module.CourseError(
            "course.unknown_root",
            "%s is not a directory; a binding is recorded in a course's own "
            "sidecar, so the course root has to exist first" % base)
    return path


def bind(base, objective, source_object_id, binding_kind="source",
         treatment_kind="", locator="", state="unknown",
         confidence="unknown", actor_kind="human", actor_name=""):
    """Record one binding and return a plain result dict.

    The rights gate, the vocabularies and the sidecar write all belong to
    `course` and `graph`; this validates the shape of the request and hands
    it over, so a bad `binding_kind` is refused before a file is read.
    """
    if binding_kind not in BINDING_KINDS:
        raise course_module.CourseError(
            "course.unknown_binding_kind",
            "%s is not a binding kind; the two are %s"
            % (binding_kind, " and ".join(BINDING_KINDS)))
    if binding_kind == "treatment" and not treatment_kind:
        raise course_module.CourseError(
            "course.missing_treatment_kind",
            "a treatment binding names which of the eleven treatments it "
            "is, because the treatment decides which right it consumes")
    if state not in graph.BINDING_STATES:
        raise course_module.CourseError(
            "course.unknown_binding_state",
            "%s is not a coverage state; the five are %s"
            % (state, ", ".join(graph.BINDING_STATES)))
    if confidence not in graph.EDGE_CONFIDENCES:
        raise course_module.CourseError(
            "course.unknown_confidence",
            "%s is not a confidence; the four are %s"
            % (confidence, ", ".join(graph.EDGE_CONFIDENCES)))
    path = _course_base(base)
    right = (graph.treatment_right(treatment_kind) if binding_kind == "treatment"
             else graph.SOURCE_BINDING_RIGHT)
    if binding_kind == "treatment":
        record = course_module.bind_treatment(
            path, objective, source_object_id, treatment_kind,
            locator=locator, state=state, confidence=confidence,
            actor_kind=actor_kind, actor_name=actor_name)
    else:
        record = course_module.bind_source(
            path, objective, source_object_id, locator=locator, state=state,
            confidence=confidence, actor_kind=actor_kind,
            actor_name=actor_name)
    return {"binding_kind": binding_kind, "objective": objective,
            "source_object_id": source_object_id,
            "treatment_kind": treatment_kind, "locator": locator,
            "state": state, "confidence": confidence,
            "right_consumed": right,
            "revision": record.get("revision"),
            "fingerprint": record.get("fingerprint")}


def bindings(base):
    """Every binding this course records, plus the objectives and sources a
    new one may name. One read, so a surface offering the choice and a
    surface listing the result cannot disagree about what exists."""
    path = _course_base(base)
    read = course_module.read_course(path)
    doc = read["doc"]
    registry = journal.read_registry(path)
    sources = []
    for row in doc.get("sources") or ():
        oid = row.get("source_object_id") or ""
        record = registry.get(oid) or {}
        rights = record.get("rights") or {}
        sources.append({
            "source_object_id": oid,
            "title": row.get("title") or oid,
            "note": row.get("note") or "",
            "rights": dict((op, identity.rights_state(rights, op))
                           for op in identity.RIGHTS_OPERATIONS),
        })
    objectives = [{"id": row.get("id") or "",
                   "statement": row.get("statement") or "",
                   "container": row.get("container") or ""}
                  for row in doc.get("objectives") or ()]
    return {"course_object_id": read.get("object_id"),
            "fingerprint": read.get("fingerprint"),
            "objectives": objectives, "sources": sources,
            "bindings": list(doc.get("bindings") or ()),
            "treatment_kinds": list(graph.TREATMENT_KINDS),
            "treatment_rights": dict(graph.TREATMENT_RIGHTS),
            "states": list(graph.BINDING_STATES),
            "confidences": list(graph.EDGE_CONFIDENCES)}


def rights_grant(base, source_object_id, grants, actor_kind="human",
                 actor_name=""):
    """Record the learner's declaration about one source's rights.

    `journal.op_grant_rights` is the writer, so the bytes are untouched, the
    revision advances, the grant merges onto what was recorded, and a name or
    value outside the closed vocabularies is refused rather than stored.
    Recording `denied` is the same operation, which is why this is not called
    `grant`.
    """
    path = _course_base(base)
    registry = journal.read_registry(path)
    record = registry.get(source_object_id)
    if record is None:
        raise course_module.CourseError(
            "course.unknown_source",
            "%s is not a registered object in this course root's journal "
            "registry" % source_object_id)
    revision = journal.op_grant_rights(
        path, source_object_id, grants, record["fingerprint"],
        actor_kind, actor_name,
        note="rights declared by the owner of this source")
    return {"source_object_id": source_object_id,
            "rights": revision.get("rights"),
            "revision": revision.get("revision")}


def _emit(payload, as_json):
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    return payload


def _through_the_spine(a, operation, request):
    """Send one `itembank bind` request through the course operating
    surface's dispatch spine, so the command and the route validate against
    the same published node (19A-02).

    Two things are worth stating about the shape of this call. The import is
    function-local because the spine imports THIS module for the binding
    implementation: one direction at import time, the other at call time, so
    there is no cycle and no third module holding two halves of one
    operation. And the course id is read from the sidecar at `--base` rather
    than asked for: the request that reaches the spine carries the course's
    own object id and no path, exactly like the route's, while the person at
    the terminal still addresses the course as the directory they are
    standing in.
    """
    from surfaces import course_ops

    base = _course_base(a.base)
    request = dict(request)
    request["course_id"] = course_module.read_course(base)["object_id"]
    if getattr(a, "actor", ""):
        request["actor"] = a.actor
    return course_ops.run(os.path.dirname(base), operation, request,
                          actor_kind="human",
                          actor_name=getattr(a, "actor", "") or "", base=base)


def cmd_bind(a):
    """`itembank bind` -- the first course-shaped command.

    Three actions, all of them one call into `course`: `source` and
    `treatment` record a binding, and `list` reads what a course holds so a
    caller can see the objective ids and source ids the other two need.

    Since 19A-02 every action goes through `course_ops.run`, so the command
    is refused by the same published request document the route is refused
    by, and `list` prints the effective reading of each binding rather than
    the raw row: what it claims, and whether the right it was made under
    still reads the same way.
    """
    try:
        if a.action == "list":
            payload = _through_the_spine(a, "bindings", {})
            if getattr(a, "json", False):
                return _emit(payload, True) and 0
            print("course %s" % payload["course_object_id"])
            print("\nObjectives")
            for row in payload["objectives"]:
                print("  %s  %s" % (row["id"], row["statement"][:88]))
            print("\nSources")
            for row in payload["sources"]:
                print("  %s  %s" % (row["source_object_id"], row["title"]))
                print("      rights: %s"
                      % ", ".join("%s=%s" % (k, v)
                                  for k, v in sorted(row["rights"].items())))
            print("\nBindings (%d)" % len(payload["bindings"]))
            for row in payload["readings"]:
                print("  %-9s %s -> %s  %s"
                      % (row["binding_kind"], row["objective"],
                         row["source_object_id"], row["locator"]))
                print("      %s %s, consumes %s (recorded %s, now %s)%s"
                      % (row["state"], row["confidence"],
                         row["right_consumed"] or "an unknown right",
                         row["rights_snapshot"] or "nothing",
                         row["rights_now"],
                         "  <-- the right has changed"
                         if row["rights_diverged"] else ""))
            if payload["diverged"]:
                print("\n%d binding(s) rest on a right that has changed "
                      "since they were recorded. A snapshot is history, not "
                      "permission: the next write against that source reads "
                      "the registry again." % payload["diverged"])
            return 0
        if a.action == "rights":
            names = [n.strip() for n in (a.grant or "").split(",") if n.strip()]
            denied = [n.strip() for n in (a.deny or "").split(",") if n.strip()]
            if not names and not denied:
                sys.exit("bind rights needs --grant or --deny")
            grants = {}
            for name in names:
                grants[name] = "granted"
            for name in denied:
                grants[name] = "denied"
            payload = _through_the_spine(a, "rights",
                                         {"source": a.source,
                                          "grants": grants})
            if getattr(a, "json", False):
                return _emit(payload, True) and 0
            print("recorded on %s: %s"
                  % (payload["source_object_id"],
                     ", ".join("%s=%s" % (k, v) for k, v
                               in sorted((payload["rights"] or {}).items()))))
            print("  undo: %s" % payload["undo"])
            return 0
        payload = _through_the_spine(
            a, "bind",
            dict({"objective": a.objective, "source": a.source,
                  "binding_kind": a.action, "locator": a.locator or "",
                  "state": a.state, "confidence": a.confidence},
                 # Omitted rather than sent empty: the published node closes
                 # `treatment` to the eleven kinds, and "" is not one of them.
                 **({"treatment": a.treatment}
                    if getattr(a, "treatment", "") else {})))
        if getattr(a, "json", False):
            return _emit(payload, True) and 0
        print("bound %s -> %s (%s binding, consumes %s, state %s, "
              "confidence %s)"
              % (payload["objective"], payload["source_object_id"],
                 payload["binding_kind"], payload["right_consumed"],
                 payload["state"], payload["confidence"]))
        if payload["locator"]:
            print("  locator: %s" % payload["locator"])
        print("  sidecar revision %s" % payload["revision"])
        print("  undo: %s" % payload["undo"])
        return 0
    except (course_module.CourseError, graph.GraphError,
            journal.JournalError) as err:
        sys.exit("%s: %s" % (err.code, err.message))
