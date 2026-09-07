#!/usr/bin/env python3
"""`course / create` and `course / change`, the two cells the 2026-09-05
surface grid named first, and the dispatch spine every later 19A wave copies.

What is asserted, in the order it matters:

- **The spine validates off disk.** A request is checked against the
  `$defs` node its own operation names in
  `schemas/course_operation.schema.json` before a single file is read, so a
  missing title, an unknown field, or a course id a URL could not hold is
  refused with nothing written. The document is read from the repository, not
  from a copy embedded in Python.
- **Both surfaces reach the frozen engine.** A course created from the CLI
  and a course created from the route both land as one `course-graph.md`
  sidecar written by `journal.commit_operation`, and a rename is one
  `edit_in_place` that leaves identity, sections and evidence alone.
- **Compare-and-swap is real.** A rename that states a stale
  `expected_fingerprint` is refused by `journal.stale_preflight`, by name,
  and the sidecar is unchanged.
- **The route is the CLI twin.** The same request, sent to the route and
  given to the command, reaches the same function and produces the same
  shape.
- **The parity discipline held.** Both routes carry a `ROUTE_CLI` entry and
  a `SURFACE_PARITY` row, and the two paths the source-binding door landed on
  early still serve as declared aliases.

Plan 19A-02 adds the source-binding family to the same spine, and four more
things are asserted here:

- **The path from a linked file to a coverage claim is walkable from a
  surface.** Link a source, record it in the course, declare the right, bind
  it: four operations, no Python import, and each one refusing before it
  writes when the step before it was skipped.
- **`add_source` refuses what it cannot stand behind.** A source the journal
  registry does not hold, and a source already recorded, are both refused by
  name with nothing written.
- **A rights snapshot is history.** A binding made while `read` was granted
  still reads its snapshot as `granted` after the grant is revoked, and the
  read reports the divergence rather than either hiding it or rewriting the
  row.
- **A course write is loopback-only.** The spine gates a write with the same
  check a day write and a theme save use, and gates the family's one read
  with the read-side check, so a `--lan` daemon exposes reading a course and
  never minting or binding one.

Plan 19A-03 adds the structure and objective-editing families, and what is
asserted about them is mostly what they REFUSE to do:

- **Structure claims nothing about order.** A container and an objective each
  add exactly zero edges, so the outline never becomes a prerequisite claim by
  accident.
- **The authored order is never rewritten.** A prerequisite pointing backwards
  through the authored sequence is recorded and reported as a warning, a cycle
  is named and never broken, and a proposed order is returned rather than
  written.
- **An identity move adds rows and deletes none.** Rename, split and merge each
  leave the original row exactly as it was and record a migration as
  `proposed`, so the identity a learner's evidence was recorded against still
  names something.
- **An imported objective is immutable and still revisable.** A rename of an
  imported row refuses by name, and the overlay it points to leaves the
  import's row untouched.

Standard library only, runnable as `python tests/course_ops_roundtrip.py`.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "fixtures"))

import course as course_module                              # noqa: E402
import course_package                                       # noqa: E402
import corpus_15b                                           # noqa: E402
import director                                             # noqa: E402
import graph                                                # noqa: E402
import identity                                             # noqa: E402
import journal                                              # noqa: E402
import model                                                # noqa: E402
from surfaces import course_ops, daemon                      # noqa: E402
from daemon_roundtrip import start_daemon, json_request      # noqa: E402

FAILURES = []


def fail(msg):
    print("FAIL: " + msg)
    FAILURES.append(msg)


def check_the_request_document_is_read_off_disk():
    """D-04: the request shape is a published file, not a Python literal."""
    doc = course_ops.request_schema()
    for operation in ("create", "rename"):
        node, _ = course_ops.operation_schema(operation, doc)
        if node["properties"]["operation"].get("const") != operation:
            fail("%s's $defs node does not pin its own operation name"
                 % operation)
        if node.get("additionalProperties") is not False:
            fail("%s's node accepts unlisted fields; a request document that "
                 "does not close is not a signature" % operation)
    for operation in course_ops.OPERATIONS:
        if operation not in doc["$defs"]:
            fail("operation %r has no $defs node; the MCP tool table "
                 "generated from these routes would have no signature for it"
                 % operation)
    try:
        course_ops.operation_schema("delete")
    except course_module.CourseError as err:
        if err.code != "course.unknown_operation":
            fail("an unpublished operation refused with %r" % err.code)
        if "Next safe action" not in err.message:
            fail("the refusal does not name the next safe action")
    else:
        fail("an unpublished operation was accepted")
    print("ok   the request document is read off disk and closes")



def check_every_closed_vocabulary_matches_its_source_of_truth():
    """A published enum is a copy, and a copy drifts.

    This check exists because it caught a real defect the day the family
    landed: the `bind` node's `treatment` enum had been written out by hand
    and named seven treatments the engine does not have while omitting seven
    it does, so a legitimate `notes-or-terms` binding was refused by the
    document on both surfaces at once, and an invented `quiz` passed the
    document and was refused by `graph.treatment_right` one call later.

    Neither failure is visible from inside the schema. The request document
    is the MCP tool signature, so an enum that disagrees with the engine is a
    tool that advertises operations the runtime will not perform, which is
    exactly the second competing authority the non-negotiables forbid. The
    fix is not care; it is this assertion.
    """
    doc = course_ops.request_schema()
    defs = doc["$defs"]
    for label, published, actual in (
            ("binding_state", defs["binding_state"]["enum"],
             list(graph.BINDING_STATES)),
            ("confidence", defs["confidence"]["enum"],
             list(graph.EDGE_CONFIDENCES)),
            ("binding_kind", defs["bind"]["properties"]["binding_kind"]["enum"],
             list(graph.BINDING_KINDS)),
            ("treatment_kind", defs["treatment_kind"]["enum"],
             list(graph.TREATMENT_KINDS)),
            ("grants names", sorted(defs["grants"]["properties"]),
             sorted(identity.RIGHTS_OPERATIONS))):
        if published != actual:
            fail("the published %s vocabulary has drifted from the engine's: "
                 "the document names %s that the engine does not, and omits "
                 "%s that it does"
                 % (label, sorted(set(published) - set(actual)) or "nothing",
                    sorted(set(actual) - set(published)) or "nothing"))
    # 19A-04: the treatment vocabulary is published ONCE and every node that
    # names a treatment refs it. Two copies of an engine tuple drift apart
    # twice as fast as one, and the one copy that existed drifted the day it
    # was written.
    for node_name in ("bind", "bind_treatment"):
        field = defs[node_name]["properties"]["treatment"]
        if field.get("$ref") != "#/$defs/treatment_kind":
            fail("the %s node inlines its own treatment vocabulary instead "
                 "of referencing the one published copy, which is how the "
                 "first copy came to name seven treatments the engine does "
                 "not have" % node_name)
    for name, node in defs["grants"]["properties"].items():
        if node["enum"] != list(identity.RIGHTS_STATES):
            fail("the published states for the %s right are %r, not the "
                 "three identity.RIGHTS_STATES holds" % (name, node["enum"]))
    print("ok   every closed vocabulary the document publishes equals the "
          "engine tuple it copies")


def check_bad_requests_refuse_before_anything_is_read():
    tmp = tempfile.mkdtemp(prefix="course_ops_bad_")
    try:
        for request, why in (
                ({"course_id": "algebra"}, "a create with no title"),
                ({"course_id": "algebra", "title": ""}, "an empty title"),
                ({"course_id": "../etc", "title": "T"}, "a traversing id"),
                ({"course_id": ".", "title": "T"}, "the workspace itself"),
                ({"course_id": "..", "title": "T"}, "the workspace parent"),
                ({"course_id": "algebra", "title": "T", "base": tmp},
                 "a filesystem path"),
                ({"course_id": "algebra", "title": "T",
                  "operation": "rename"}, "a mismatched operation")):
            try:
                course_ops.run(tmp, "create", request)
            except course_module.CourseError as err:
                if err.code not in ("course.invalid_request",
                                    "course.operation_mismatch"):
                    fail("%s refused with %r" % (why, err.code))
                if "Next safe action" not in err.message:
                    fail("%s refused without naming the next safe action"
                         % why)
            else:
                fail("%s was accepted" % why)
        if os.listdir(tmp):
            fail("a refused request wrote %r into the workspace"
                 % os.listdir(tmp))
        print("ok   a request the document does not describe writes nothing")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_create_and_rename_reach_the_frozen_engine():
    tmp = tempfile.mkdtemp(prefix="course_ops_engine_")
    try:
        made = course_ops.run(tmp, "create",
                              {"course_id": "algebra", "title": "Math 1400"},
                              actor_name="tester")
        sidecar = os.path.join(tmp, "algebra",
                               course_module.COURSE_SIDECAR_FILENAME)
        if not os.path.exists(sidecar):
            fail("create wrote no sidecar at %s" % sidecar)
            return
        read = course_module.read_course(os.path.join(tmp, "algebra"))
        if read["doc"]["header"].get("title") != "Math 1400":
            fail("the minted sidecar does not carry the title")
        if made["course_object_id"] != read["object_id"]:
            fail("create reported an object id the sidecar does not carry")
        if not made.get("undo"):
            fail("create reported no undo; the operation protocol requires "
                 "one")

        state = journal.object_state(os.path.join(tmp, "algebra"),
                                     read["object_id"])
        if not state:
            fail("the mint left no journal state for the course object")

        renamed = course_ops.run(
            tmp, "rename", {"course_id": "algebra", "title": "Algebra I"},
            actor_name="tester")
        after = course_module.read_course(os.path.join(tmp, "algebra"))
        if after["doc"]["header"].get("title") != "Algebra I":
            fail("rename did not change the title")
        if after["object_id"] != read["object_id"]:
            fail("rename changed the course's identity; a title is display")
        if renamed["previous_title"] != "Math 1400":
            fail("rename did not report what it replaced")

        try:
            course_ops.run(tmp, "rename",
                           {"course_id": "algebra", "title": "Stale",
                            "expected_fingerprint": read["fingerprint"]})
        except journal.JournalError as err:
            if "stale" not in err.code:
                fail("a stale expected fingerprint refused with %r" % err.code)
        else:
            fail("a stale expected fingerprint was accepted; the "
                 "compare-and-swap is not reaching the frozen path")
        final = course_module.read_course(os.path.join(tmp, "algebra"))
        if final["doc"]["header"].get("title") != "Algebra I":
            fail("a refused write changed the sidecar")

        try:
            course_ops.run(tmp, "create",
                           {"course_id": "algebra", "title": "Again"})
        except course_module.CourseError as err:
            if err.code != "course.sidecar_exists":
                fail("creating over an existing course refused with %r"
                     % err.code)
        else:
            fail("creating over an existing course overwrote it")
        print("ok   create mints and rename edits in place, both through "
              "journal.commit_operation")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_the_command_exists():
    tmp = tempfile.mkdtemp(prefix="course_ops_cli_")
    try:
        def run(*args):
            return subprocess.run(
                [sys.executable, os.path.join(ROOT, "itembank.py"), "course"]
                + list(args), capture_output=True, text=True)

        proc = run("create", "emt", "--title", "EMT Basic", "--root", tmp,
                   "--json")
        if proc.returncode != 0:
            fail("itembank course create failed: %s" % proc.stderr.strip())
            return
        made = json.loads(proc.stdout)
        if made["engine"] != "course.create_course":
            fail("the command did not report the engine function it reached")

        proc = run("rename", "emt", "--title", "EMT Basic, revised",
                   "--root", tmp, "--json")
        if proc.returncode != 0:
            fail("itembank course rename failed: %s" % proc.stderr.strip())
            return
        if json.loads(proc.stdout)["previous_title"] != "EMT Basic":
            fail("the command did not report the title it replaced")

        proc = run("show", "emt", "--root", tmp, "--json")
        if proc.returncode != 0:
            fail("itembank course show failed: %s" % proc.stderr.strip())
            return
        shown = json.loads(proc.stdout)
        if shown["title"] != "EMT Basic, revised":
            fail("show reports %r after a rename" % shown["title"])
        if shown["counts"]["objectives"] != 0:
            fail("a minted course is not empty")

        proc = run("rename", "no-such-course", "--title", "X", "--root", tmp)
        if proc.returncode == 0:
            fail("renaming a course that does not exist succeeded")
        elif "course.unknown_course" not in proc.stderr:
            fail("the refusal is not typed: %s" % proc.stderr.strip())
        print("ok   the CLI twin creates, renames and reads a course")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_the_route_is_the_cli_twin():
    tmp = tempfile.mkdtemp(prefix="course_ops_http_")
    proc = None
    try:
        proc, url, _lines = start_daemon(tmp)
        status, body = json_request(url + "api/course/create",
                                    {"course_id": "csci", "title": "CSCI 1100"})
        if status != 200:
            fail("POST /api/course/create returned %r: %r" % (status, body))
            return
        if body.get("engine") != "course.create_course":
            fail("the route did not reach course.create_course")
        read = course_module.read_course(os.path.join(tmp, "csci"))
        if read["doc"]["header"].get("title") != "CSCI 1100":
            fail("the route's course did not reach the sidecar")

        status, body = json_request(url + "api/course/rename",
                                    {"course_id": "csci",
                                     "title": "CSCI 1100 Fall"})
        if status != 200:
            fail("POST /api/course/rename returned %r: %r" % (status, body))
        elif body.get("previous_title") != "CSCI 1100":
            fail("the rename route did not report what it replaced")

        status, body = json_request(url + "api/course/rename",
                                    {"course_id": "nope", "title": "X"})
        if status != 404:
            fail("an unknown course returned %r from the rename route"
                 % status)
        status, body = json_request(url + "api/course/create",
                                    {"course_id": "x"})
        if status != 400:
            fail("a create with no title returned %r" % status)
        text = body if isinstance(body, str) else json.dumps(body)
        if "course.invalid_request" not in text:
            fail("the route's refusal does not carry the typed code")
        status, _ = json_request(url + "api/course/create",
                                 {"course_id": "y", "title": "Y",
                                  "actor_kind": "agent"})
        if status != 400:
            fail("a body claiming an actor kind returned %r" % status)

        # The 19A-02 family over HTTP. Asserted here rather than only
        # in-process because a route whose handler name is misspelled
        # dispatches to nothing, and the tables would still look right.
        base = os.path.join(tmp, "csci")
        folder = os.path.join(base, "sources")
        if not os.path.isdir(folder):
            os.makedirs(folder)
        with open(os.path.join(folder, "notes.md"), "w",
                  encoding="utf-8") as fh:
            fh.write("# Notes\n")
        source_id = journal.op_link(base, "source", "sources/notes.md",
                                    "human", "tester")["object_id"]
        status, body = json_request(url + "api/course/add-source",
                                    {"course_id": "csci",
                                     "source_object_id": source_id,
                                     "title": "Notes"})
        if status != 200:
            fail("POST /api/course/add-source returned %r: %r" % (status, body))
        elif body.get("engine") != "graph.add_source":
            fail("the add-source route did not reach graph.add_source")
        status, body = json_request(url + "api/course/add-source",
                                    {"course_id": "csci",
                                     "source_object_id": source_id,
                                     "title": "Notes"})
        if status != 400:
            fail("a duplicate Sources row returned %r from the route"
                 % status)
        status, body = json_request(url + "api/course/bindings",
                                    {"course_id": "csci"})
        if status != 200:
            fail("POST /api/course/bindings returned %r: %r" % (status, body))
        elif [s["source_object_id"] for s in body["sources"]] != [source_id]:
            fail("the read does not show the source add-source recorded")
        elif body["readings"] or body["diverged"]:
            fail("a course with no bindings reported readings")
        status, body = json_request(url + "api/course/bind",
                                    {"course_id": "csci", "objective": "o",
                                     "source": source_id,
                                     "state": "perfect"})
        if status != 400:
            fail("a state outside the vocabulary returned %r from the bind "
                 "route" % status)
        text = body if isinstance(body, str) else json.dumps(body)
        if "course.invalid_request" not in text:
            fail("the bind route no longer refuses through the published "
                 "document: %r" % text)

        # 19A-04 over HTTP: the table reads, and the write it describes
        # requires the treatment the older route cannot require.
        status, body = json_request(url + "api/course/treatments",
                                    {"course_id": "csci",
                                     "source": source_id})
        if status != 200:
            fail("POST /api/course/treatments returned %r: %r"
                 % (status, body))
        elif len(body["treatments"]) != len(graph.TREATMENT_KINDS):
            fail("the treatments route reported %d of the eleven kinds"
                 % len(body["treatments"]))
        elif body["bindable"]:
            fail("every right on this source is unrecorded and the route "
                 "still called %r bindable" % body["bindable"])
        status, body = json_request(url + "api/course/bind-treatment",
                                    {"course_id": "csci", "objective": "o",
                                     "source": source_id})
        if status != 400:
            fail("a treatment binding with no treatment returned %r from "
                 "the route" % status)
        text = body if isinstance(body, str) else json.dumps(body)
        if "treatment" not in text:
            fail("the bind-treatment refusal does not name the missing "
                 "field: %r" % text)

        print("ok   the route reaches the same spine and refuses the same "
              "way, for both families")

    finally:
        if proc is not None:
            proc.terminate()
            proc.wait(timeout=5)
        shutil.rmtree(tmp, ignore_errors=True)

def check_every_course_route_dispatches_to_a_real_handler():
    """`_dispatch` resolves a route's handler by name out of the daemon
    module's globals, so a handler name with a typo in it dispatches to
    nothing while both route tables still look right.

    Asserted statically rather than by POSTing to every route. The HTTP sweep
    that first did this was flaky for a reason it was not measuring: this
    daemon intermittently stops answering on some hosts, the same symptom
    `check_concurrent_requests_share_one_session` fails on, and a test that
    fails for a defect it is not about is a test nobody reads. Whether the
    name resolves is a static property, so it is checked statically, and the
    behaviour of the routes is covered by the request checks above.
    """
    module = vars(daemon)
    for method, route, handler_name in daemon.API_ROUTES:
        if not route.startswith("/api/course/"):
            continue
        target = module.get(handler_name)
        if target is None:
            fail("%s %s names the handler %r, which does not exist in "
                 "surfaces/daemon.py; _dispatch would raise a KeyError on "
                 "the first request" % (method, route, handler_name))
        elif not callable(target):
            fail("%s %s's handler %r is not callable"
                 % (method, route, handler_name))
    for method, route, handler_name in daemon.LEGACY_API_ALIASES:
        if not callable(module.get(handler_name)):
            fail("the declared alias %s %s names no real handler"
                 % (method, route))
    print("ok   every course route and declared alias names a handler that "
          "exists and is callable")


def check_parity_and_the_declared_aliases():
    for path, twin, tool in (
            ("/api/course/create", "course", "course_create"),
            ("/api/course/rename", "course", "course_rename"),
            ("/api/course/add-source", "course", "course_add_source"),
            ("/api/course/bind", "bind", "bind"),
            ("/api/course/bind-treatment", "bind", "bind_treatment"),
            ("/api/course/treatments", "bind", "course_treatments"),
            ("/api/course/rights", "bind", "rights_record"),
            ("/api/course/bindings", "bind", "course_bindings")):
        if daemon.ROUTE_CLI.get(("POST", path)) != twin:
            fail("POST %s has no CLI twin" % path)
        if (("POST", path), twin, tool) not in daemon.SURFACE_PARITY:
            fail("POST %s reserves no MCP tool name %r" % (path, tool))
    aliases = set(e[:2] for e in daemon.LEGACY_API_ALIASES)
    if aliases != {("POST", "/api/bind"), ("POST", "/api/rights")}:
        fail("the two early source-binding paths are not declared aliases")
    if aliases & set(e[:2] for e in daemon.API_ROUTES):
        fail("an alias is also an API route, which would mint a second MCP "
             "tool for one operation")
    print("ok   every course route carries a twin and a reserved tool "
          "name, and the two early paths are declared aliases")


def _linked_source(base, name, text):
    """One source file linked into a course's journal registry, the way
    `source import` leaves it: the object exists and every right on it is
    unknown, because finding a file grants nothing."""
    folder = os.path.join(base, "sources")
    if not os.path.isdir(folder):
        os.makedirs(folder)
    with open(os.path.join(folder, name), "w", encoding="utf-8") as fh:
        fh.write(text)
    record = journal.op_link(base, "source", "sources/" + name, "human",
                             "tester")
    return record["object_id"]


def check_the_family_walks_from_a_linked_file_to_a_claim():
    """The whole point of the wave: four operations, no Python import, and
    each step refusing when the one before it was skipped."""
    tmp = tempfile.mkdtemp(prefix="course_ops_family_")
    try:
        course_ops.run(tmp, "create",
                       {"course_id": "fen", "title": "Fen Hydrology"},
                       actor_name="tester")
        base = os.path.join(tmp, "fen")
        source_id = _linked_source(base, "notes.md", "# Notes\n\nText.\n")

        try:
            course_ops.run(tmp, "add_source",
                           {"course_id": "fen", "source_object_id": "nope",
                            "title": "Nothing"})
        except course_module.CourseError as err:
            if err.code != "course.unknown_source":
                fail("an unregistered source refused with %r" % err.code)
            if "Next safe action" not in err.message:
                fail("the unregistered-source refusal names no next action")
        else:
            fail("a Sources row was written for an object nothing holds")

        added = course_ops.run(tmp, "add_source",
                               {"course_id": "fen",
                                "source_object_id": source_id,
                                "title": "Field notes",
                                "note": "linked for this check"},
                               actor_name="tester")
        if added["engine"] != "graph.add_source":
            fail("add_source did not report the engine function it reached")
        if added["bindable"]:
            fail("a freshly linked source reported itself bindable; unknown "
                 "is restrictive and finding a file grants nothing")
        doc = course_module.read_course(base)["doc"]
        rows = [r.get("source_object_id") for r in doc.get("sources") or ()]
        if rows != [source_id]:
            fail("the Sources section holds %r after one add_source" % rows)

        try:
            course_ops.run(tmp, "add_source",
                           {"course_id": "fen",
                            "source_object_id": source_id, "title": "Again"})
        except course_module.CourseError as err:
            if err.code != "course.source_already_recorded":
                fail("a duplicate source row refused with %r" % err.code)
        else:
            fail("one source was recorded twice; a Sources row is a "
                 "reference, and two would be two answers to one question")

        # An objective to bind to. Objective editing is 19A-03's family, so
        # this reaches graph directly and the sidecar write is the same
        # compare-and-swap one every operation here uses.
        read = course_module.read_course(base)
        objective = graph.add_objective(read["doc"], "O1 Read the notes.")
        course_module.write_course(base, read["doc"], read["fingerprint"],
                                   "human", "tester")

        try:
            course_ops.run(tmp, "bind",
                           {"course_id": "fen", "objective": objective["id"],
                            "source": source_id})
        except course_module.CourseError as err:
            if err.code != "course.rights_not_granted":
                fail("binding an unknown-rights source refused with %r"
                     % err.code)
        else:
            fail("a source whose read right was never declared was bound; "
                 "unknown is not a lesser form of permission")

        granted = course_ops.run(tmp, "rights",
                                 {"course_id": "fen", "source": source_id,
                                  "grants": {"read": "granted"}},
                                 actor_name="tester")
        if granted["previous"] != {"read": "unknown"}:
            fail("the rights operation did not report the state it replaced")
        if granted["bytes_touched"]:
            fail("recording a right claimed to touch the source's bytes")
        before = open(os.path.join(base, "sources", "notes.md"),
                      encoding="utf-8").read()

        bound = course_ops.run(tmp, "bind",
                               {"course_id": "fen",
                                "objective": objective["id"],
                                "source": source_id,
                                "locator": "sources/notes.md#top",
                                "state": "thin", "confidence": "low"},
                               actor_name="tester")
        if bound["right_consumed"] != graph.SOURCE_BINDING_RIGHT:
            fail("a source binding reported consuming %r"
                 % bound["right_consumed"])
        after = open(os.path.join(base, "sources", "notes.md"),
                     encoding="utf-8").read()
        if after != before:
            fail("binding a source rewrote the source")
        print("ok   link, record, declare, bind: the family walks from a "
              "file to a coverage claim with no Python import")
        return tmp, base, source_id, objective["id"]
    except Exception:
        shutil.rmtree(tmp, ignore_errors=True)
        raise


def check_a_rights_snapshot_is_history():
    """The read's reason to exist: a binding cannot notice that the grant it
    was made under has been revoked, so the read says so."""
    made = check_the_family_walks_from_a_linked_file_to_a_claim()
    if made is None:
        return
    tmp, base, source_id, objective = made
    try:
        reading = course_ops.run(tmp, "bindings", {"course_id": "fen"})
        if len(reading["readings"]) != 1:
            fail("the read reported %d bindings, one was made"
                 % len(reading["readings"]))
            return
        row = reading["readings"][0]
        if row["rights_snapshot"] != "granted" or row["rights_now"] != \
                "granted" or row["rights_diverged"]:
            fail("a binding made under a live grant reads as diverged")
        if row["objective_statement"] != "O1 Read the notes.":
            fail("the read does not name the objective the binding claims")

        course_ops.run(tmp, "rights",
                       {"course_id": "fen", "source": source_id,
                        "grants": {"read": "denied"}}, actor_name="tester")
        after = course_ops.run(tmp, "bindings", {"course_id": "fen"})
        row = after["readings"][0]
        if row["rights_snapshot"] != "granted":
            fail("revoking the grant rewrote the row's snapshot; a snapshot "
                 "is what was recorded, not what is true now")
        if row["rights_now"] != "denied" or not row["rights_diverged"]:
            fail("the read did not notice that the right behind the claim "
                 "changed: snapshot %r, now %r"
                 % (row["rights_snapshot"], row["rights_now"]))
        if after["diverged"] != 1:
            fail("the read counted %d diverged bindings" % after["diverged"])
        if "has since changed" not in row["explanation"]:
            fail("the explanation does not say the right changed: %r"
                 % row["explanation"])

        # The sidecar row is untouched by the read, and the next write is
        # what enforces the revocation.
        try:
            course_ops.run(tmp, "bind",
                           {"course_id": "fen", "objective": objective,
                            "source": source_id})
        except course_module.CourseError as err:
            if err.code != "course.rights_not_granted":
                fail("a write after revocation refused with %r" % err.code)
        else:
            fail("a revoked right did not refuse the next binding")
        print("ok   a rights snapshot is history, the read names the "
              "divergence, and the next write enforces it")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_the_treatment_table_has_a_reader():
    """19A-04's real gap, and the reason this wave is not just a rename.

    `graph.TREATMENT_RIGHTS` decides which of the eleven treatments a course
    may use for a given source, and it had no reader on any surface. The only
    way to learn that a guided lesson needs `transform` while a direct
    reading needs `read` was to attempt a binding and be refused, one kind at
    a time.

    The assertion that matters is not that the table prints. It is that what
    the read reports and what the next write enforces cannot disagree: every
    kind the read calls bindable is bound here for real, and every kind it
    calls refusing is refused for real, against the same course at the same
    moment.
    """
    tmp = tempfile.mkdtemp(prefix="course_ops_treatments_")
    try:
        course_ops.run(tmp, "create", {"course_id": "fen", "title": "Fen"})
        base = os.path.join(tmp, "fen")
        source_id = _linked_source(base, "notes.md", "# Notes\n")
        course_ops.run(tmp, "add_source",
                       {"course_id": "fen", "source_object_id": source_id,
                        "title": "Field notes"}, actor_name="tester")
        container = course_ops.run(tmp, "add_container",
                                   {"course_id": "fen", "label": "module",
                                    "title": "M1"}, actor_name="tester")
        objective = course_ops.run(
            tmp, "add_objective",
            {"course_id": "fen", "container": container["container_id"],
             "statement": "O1 Read the notes."}, actor_name="tester")["objective_id"]

        # With no source named the mapping is reported and no right is
        # resolved, which is a different answer from "nothing is granted".
        table = course_ops.run(tmp, "treatments", {"course_id": "fen"})
        if len(table["treatments"]) != len(graph.TREATMENT_KINDS):
            fail("the read reported %d treatments; the vocabulary is closed "
                 "at %d" % (len(table["treatments"]),
                            len(graph.TREATMENT_KINDS)))
        for row in table["treatments"]:
            if row["right_consumed"] != graph.TREATMENT_RIGHTS[
                    row["treatment_kind"]]:
                fail("the read says a %s consumes %r; the engine says %r"
                     % (row["treatment_kind"], row["right_consumed"],
                        graph.TREATMENT_RIGHTS[row["treatment_kind"]]))
            if row["bindable"] is not None or row["rights_state"]:
                fail("no source was named and the read still claimed a "
                     "rights answer for %s" % row["treatment_kind"])
        if table["rights_resolved"] or table["bindable"] or table["refused"]:
            fail("a read with no source split the eleven into allowed and "
                 "refused, which it cannot know")

        # `read` granted and nothing else: the three read-consuming kinds
        # bind and the eight quote/transform kinds refuse.
        course_ops.run(tmp, "rights",
                       {"course_id": "fen", "source": source_id,
                        "grants": {"read": "granted"}}, actor_name="tester")
        table = course_ops.run(tmp, "treatments",
                               {"course_id": "fen", "source": source_id})
        expected = [k for k in graph.TREATMENT_KINDS
                    if graph.TREATMENT_RIGHTS[k] == "read"]
        if table["bindable"] != expected:
            fail("with only `read` granted the read calls %r bindable; the "
                 "kinds that consume read are %r"
                 % (table["bindable"], expected))
        if len(table["refused"]) != len(graph.TREATMENT_KINDS) - len(expected):
            fail("the read did not refuse every kind consuming a right that "
                 "is unrecorded")
        for row in table["treatments"]:
            if not row["bindable"] and "refuses" not in row["explanation"]:
                fail("a refusing treatment does not say it refuses: %r"
                     % row["explanation"])

        # The read and the write agree, checked by doing both.
        for kind in table["bindable"]:
            course_ops.run(tmp, "bind_treatment",
                           {"course_id": "fen", "objective": objective,
                            "source": source_id, "treatment": kind},
                           actor_name="tester")
        for kind in table["refused"]:
            try:
                course_ops.run(tmp, "bind_treatment",
                               {"course_id": "fen", "objective": objective,
                                "source": source_id, "treatment": kind},
                               actor_name="tester")
            except course_module.CourseError as err:
                if err.code != "course.rights_not_granted":
                    fail("a %s binding the read called refused was refused "
                         "with %r instead" % (kind, err.code))
            else:
                fail("the read called a %s binding refused and it was "
                     "accepted; the table and the gate disagree" % kind)

        # Recording the right the read named is what changes the answer, and
        # the read counts what the course now does as well as what it may do.
        course_ops.run(tmp, "rights",
                       {"course_id": "fen", "source": source_id,
                        "grants": {"transform": "granted"}},
                       actor_name="tester")
        after = course_ops.run(tmp, "treatments",
                               {"course_id": "fen", "source": source_id})
        if "guided-lesson" not in after["bindable"]:
            fail("granting transform did not make a guided lesson bindable; "
                 "the read is not reading the registry fresh")
        if "excerpt" in after["bindable"]:
            fail("granting transform made an excerpt bindable; a right "
                 "granted for one operation never implies another")
        bound = dict((row["treatment_kind"], row["bound_here"])
                     for row in after["treatments"])
        if [k for k, n in bound.items() if n] != expected:
            fail("the read counted this course's own treatment bindings as "
                 "%r; %r were made" % (sorted(k for k, n in bound.items()
                                              if n), expected))

        # A read writes nothing.
        before = course_module.read_course(base)
        course_ops.run(tmp, "treatments",
                       {"course_id": "fen", "source": source_id})
        if course_module.read_course(base)["fingerprint"] != \
                before["fingerprint"]:
            fail("the treatments read advanced the sidecar")
        try:
            course_ops.run(tmp, "treatments",
                           {"course_id": "fen", "source": "no-such-object"})
        except course_module.CourseError as err:
            if err.code != "course.unknown_source":
                fail("a source this course does not name refused with %r"
                     % err.code)
        else:
            fail("the read resolved a table against a source the course "
                 "does not name")
        print("ok   the eleven-kind treatment table has a reader, and every "
              "kind it calls bindable binds while every kind it calls "
              "refused refuses")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_the_deprecated_bind_mode_writes_the_same_row():
    """`bind_treatment` is a TYPING of what `bind` already did, not a second
    writer, and this is the assertion that keeps it one.

    Non-negotiable 4 forbids silent breakage, so `POST /api/course/bind` with
    `binding_kind: treatment` keeps working. What makes that a deprecation
    rather than a fork is that both reach `course.bind_treatment` and leave
    the identical sidecar row; if they ever diverge, this repository has two
    writers for one durable object and the older one is the trap.
    """
    tmp = tempfile.mkdtemp(prefix="course_ops_deprecated_")
    try:
        course_ops.run(tmp, "create", {"course_id": "fen", "title": "Fen"})
        base = os.path.join(tmp, "fen")
        source_id = _linked_source(base, "notes.md", "# Notes\n")
        course_ops.run(tmp, "add_source",
                       {"course_id": "fen", "source_object_id": source_id,
                        "title": "Field notes"}, actor_name="tester")
        course_ops.run(tmp, "rights",
                       {"course_id": "fen", "source": source_id,
                        "grants": {"read": "granted"}}, actor_name="tester")
        container = course_ops.run(tmp, "add_container",
                                   {"course_id": "fen", "label": "module",
                                    "title": "M1"}, actor_name="tester")
        objective = course_ops.run(
            tmp, "add_objective",
            {"course_id": "fen", "container": container["container_id"],
             "statement": "O1 Read the notes."}, actor_name="tester")["objective_id"]

        shared = {"course_id": "fen", "objective": objective,
                  "source": source_id, "locator": "p. 3",
                  "state": "thin", "confidence": "low"}
        old_way = course_ops.run(tmp, "bind",
                                 dict(shared, binding_kind="treatment",
                                      treatment="direct-reading"),
                                 actor_name="tester")
        new_way = course_ops.run(tmp, "bind_treatment",
                                 dict(shared, treatment="direct-reading"),
                                 actor_name="tester")
        rows = course_module.read_course(base)["doc"]["bindings"]
        if len(rows) != 2:
            fail("two treatment bindings wrote %d rows" % len(rows))
        elif rows[0] != rows[1]:
            fail("the deprecated bind mode and bind_treatment wrote "
                 "different rows, so they are two writers and not one: %r "
                 "vs %r" % (rows[0], rows[1]))
        if "deprecated" not in old_way:
            fail("binding a treatment through `bind` did not say it is "
                 "deprecated, so nothing tells a caller to move")
        if "deprecated" in new_way:
            fail("the canonical treatment operation reports itself "
                 "deprecated")
        if new_way["right_consumed"] != "read" or \
                new_way["engine"] != "course.bind_treatment":
            fail("bind_treatment reported %r through %r"
                 % (new_way["right_consumed"], new_way["engine"]))

        # The typing is the whole reason the operation exists: the treatment
        # is required here and cannot be required on the node it replaces.
        node, _ = course_ops.operation_schema("bind_treatment")
        if "treatment" not in node["required"]:
            fail("bind_treatment does not require the treatment, which is "
                 "the only thing it has that `bind` cannot express")
        try:
            course_ops.run(tmp, "bind_treatment", dict(shared))
        except course_module.CourseError as err:
            if err.code != "course.invalid_request":
                fail("a bind_treatment with no treatment refused with %r"
                     % err.code)
            elif "treatment" not in err.message:
                fail("the refusal does not name the missing field: %r"
                     % err.message)
        else:
            fail("a treatment binding with no treatment was accepted")
        print("ok   the deprecated bind mode and bind_treatment write the "
              "identical row, and only the new one can require a treatment")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _director_fixture(root, course_id):
    course_ops.run(root, "create", {"course_id": course_id,
                                    "title": "Director acceptance"})
    base = os.path.join(root, course_id)
    source_id = _linked_source(base, "director.md", "# Director source\n")
    course_ops.run(root, "add_source",
                   {"course_id": course_id, "source_object_id": source_id,
                    "title": "Director source"}, actor_name="tester")
    course_ops.run(root, "rights",
                   {"course_id": course_id, "source": source_id,
                    "grants": {"transform": "granted"}},
                   actor_name="tester")
    container = course_ops.run(
        root, "add_container", {"course_id": course_id, "label": "module",
                                "title": "Module 1"}, actor_name="tester")
    objective = course_ops.run(
        root, "add_objective",
        {"course_id": course_id, "container": container["container_id"],
         "statement": "Explain the director source."}, actor_name="tester")
    objective_id = objective["objective_id"]
    record = {
        "schema_version": 1,
        "objective_id": objective_id,
        "treatment_kind": "guided-lesson",
        "rationale": "A guided treatment makes the sequence explicit.",
        "synthesis": True,
        "confidence": "high",
        "coverage": {"state": "thin", "locator": "director.md#top",
                     "confidence": "high", "source_object_id": source_id,
                     "match_kind": "locator"},
        "alternatives": [],
        "citations": [{"source_object_id": source_id,
                       "locator": "director.md#top"}],
    }
    return base, source_id, objective_id, record


def _assert_one_accepted_entry_and_restored(base, operation_id,
                                             original_bytes, label):
    matching = director.operation_entries(base, operation_id)
    accepted = [entry for entry in matching
                if (entry.get("agent") or {}).get("phase") == "accept"]
    if len(accepted) != 1:
        fail("%s acceptance produced %d operation journal entries, not one"
             % (label, len(accepted)))
        return
    entry = accepted[0]
    if entry.get("state") != "applied":
        fail("%s acceptance entry is %r" % (label, entry.get("state")))
    if (entry.get("undo") or {}).get("kind") != "restore_before_image":
        fail("%s acceptance entry does not own its restore before-image"
             % label)
    if not entry.get("before_image"):
        fail("%s acceptance entry names no before-image" % label)
    restored = course_ops.run(
        os.path.dirname(base), "reverse_operation",
        {"course_id": os.path.basename(base), "operation_id": operation_id},
        actor_name="tester")
    if len(restored["reversed_entries"]) != 1:
        fail("%s reversal restored %d entries, not one"
             % (label, len(restored["reversed_entries"])))
    with open(os.path.join(base, course_module.COURSE_SIDECAR_FILENAME),
              "rb") as fh:
        after = fh.read()
    if after != original_bytes:
        fail("%s reversal did not restore the sidecar's original bytes"
             % label)
    try:
        course_module.read_course(base)
    except Exception as err:
        fail("%s reversal left an invalid course: %s" % (label, err))


def check_director_family_reaches_route_and_cli_with_one_reversible_accept():
    """19A-05: all seven doors, with accepted-write and undo evidence."""
    route_root = tempfile.mkdtemp(prefix="course_ops_director_route_")
    cli_root = tempfile.mkdtemp(prefix="course_ops_director_cli_")
    proc = None
    try:
        base, source_id, objective_id, record = _director_fixture(
            route_root, "route-course")
        proc, url, _lines = start_daemon(route_root)

        def post(name, body):
            status, payload = json_request(url + "api/course/" + name, body)
            if status != 200:
                fail("POST /api/course/%s returned %r: %r"
                     % (name, status, payload))
                return {}
            return payload

        common = {"course_id": "route-course", "actor_role": "builder",
                  "autonomy": "recommend-only"}
        post("autonomy", {"course_id": "route-course",
                          "declared_level": "recommend-only"})
        declared = post("begin-operation", dict(
            common, intent="accept one reviewed recommendation"))
        operation_id = declared.get("operation_id")
        post("replay", {"course_id": "route-course",
                        "operation_id": operation_id})
        post("recommend", dict(common, objective=objective_id))
        post("recommend-pass", dict(common, objectives=[objective_id]))
        before = open(os.path.join(base, course_module.COURSE_SIDECAR_FILENAME),
                      "rb").read()
        post("apply-recommendation",
             {"course_id": "route-course", "source": source_id,
              "record": record, "operation_id": operation_id})
        _assert_one_accepted_entry_and_restored(
            base, operation_id, before, "route")

        base, source_id, objective_id, record = _director_fixture(
            cli_root, "cli-course")

        def run(*args):
            completed = subprocess.run(
                [sys.executable, os.path.join(ROOT, "itembank.py")] +
                list(args), capture_output=True, text=True)
            if completed.returncode != 0:
                fail("itembank %s failed: %s"
                     % (" ".join(args), completed.stderr.strip()))
                return {}
            return json.loads(completed.stdout)

        root_args = ("--root", cli_root, "--json")
        run("course", "autonomy", "cli-course", "--declare",
            "recommend-only", *root_args)
        declared = run("course", "begin-operation", "cli-course",
                       "--intent", "accept one reviewed recommendation",
                       "--role", "builder", "--autonomy", "recommend-only",
                       *root_args)
        operation_id = declared.get("operation_id")
        run("course", "replay", "cli-course", "--operation", operation_id,
            *root_args)
        run("course", "recommend", "cli-course", "--objective", objective_id,
            "--role", "builder", "--autonomy", "recommend-only", *root_args)
        run("course", "recommend-pass", "cli-course", "--objective",
            objective_id, "--role", "builder", "--autonomy",
            "recommend-only", *root_args)
        before = open(os.path.join(base, course_module.COURSE_SIDECAR_FILENAME),
                      "rb").read()
        run("course", "apply-recommendation", "cli-course", "--source",
            source_id, "--record", json.dumps(record), "--operation",
            operation_id, *root_args)
        reversed_payload = run("course", "reverse-operation", "cli-course",
                               "--operation", operation_id, *root_args)
        accepted = [entry for entry in director.operation_entries(
            base, operation_id)
                    if (entry.get("agent") or {}).get("phase") == "accept"]
        if len(accepted) != 1:
            fail("CLI acceptance produced %d operation journal entries, not one"
                 % len(accepted))
        elif (accepted[0].get("undo") or {}).get("kind") != \
                "restore_before_image":
            fail("CLI acceptance entry does not own its restore before-image")
        if len(reversed_payload.get("reversed_entries") or ()) != 1:
            fail("CLI reversal did not report exactly one restored entry")
        with open(os.path.join(base, course_module.COURSE_SIDECAR_FILENAME),
                  "rb") as fh:
            if fh.read() != before:
                fail("CLI reversal did not restore the original bytes")
        course_module.read_course(base)
        print("ok   all seven director operations reach both route and CLI; "
              "each accepted mutation is one operation entry whose one "
              "before-image restores the original valid course bytes")
    finally:
        if proc is not None:
            proc.terminate()
            proc.wait(timeout=10)
        shutil.rmtree(route_root, ignore_errors=True)
        shutil.rmtree(cli_root, ignore_errors=True)


def check_blueprint_operations_reach_route_and_cli_without_read_mutation():
    """19A-06: bind advances the revision, the three reports do not."""
    route_root = tempfile.mkdtemp(prefix="course_ops_blueprint_route_")
    cli_root = tempfile.mkdtemp(prefix="course_ops_blueprint_cli_")
    proc = None
    blueprint_document = corpus_15b.build_blueprint()
    questions = model.parse_bank(corpus_15b.build_draft_set())
    item_facts = corpus_15b.build_item_facts(questions)
    signals = corpus_15b.build_audit_signals()
    dependents = [{"object_id": "bank-1", "object_kind": "bank",
                   "dependency_object_id": "source-1",
                   "dependency_kind": "source", "base_fingerprint": "a",
                   "current_fingerprint": "b"}]
    try:
        course_ops.run(route_root, "create", {
            "course_id": "route-blueprint", "title": "Route blueprint"})
        route_base = os.path.join(route_root, "route-blueprint")
        proc, url, _lines = start_daemon(route_root)

        def route(operation, body):
            status, payload = json_request(
                url + "api/course/" + operation.replace("_", "-"), body)
            if status != 200:
                fail("POST /api/course/%s returned %r: %r"
                     % (operation, status, payload))
                return {}
            return payload

        def cli(operation, course_id, root, args):
            completed = subprocess.run(
                [sys.executable, os.path.join(ROOT, "itembank.py"), "course",
                 operation.replace("_", "-"), course_id] + args +
                ["--root", root, "--json"], capture_output=True, text=True)
            if completed.returncode != 0:
                fail("itembank course %s failed: %s"
                     % (operation, completed.stderr.strip()))
                return {}
            return json.loads(completed.stdout)

        def exercise(call, course_id, base, cli_style=False):
            before = course_module.read_course(base)["fingerprint"]
            if cli_style:
                bound = call("bind_blueprint", course_id, os.path.dirname(base), [
                    "--blueprint", json.dumps(blueprint_document),
                    "--expect", before])
            else:
                bound = call("bind_blueprint", {
                    "course_id": course_id, "blueprint": blueprint_document,
                    "expected_fingerprint": before})
            after_bind = course_module.read_course(base)["fingerprint"]
            if (bound.get("operation") != "bind_blueprint" or
                    bound.get("fingerprint") != after_bind or
                    not bound.get("revision") or after_bind == before):
                fail("%s bind-blueprint did not report its new fingerprint and revision"
                     % ("CLI" if cli_style else "route"))
            reads = (
                ("blueprint_gate", {"questions": questions,
                                     "blueprint": blueprint_document,
                                     "item_facts": item_facts}, "findings"),
                ("audit", dict(signals, tool_version="19A-06"), "rows"),
                ("staleness", {"dependents": dependents}, "rows"),
            )
            for operation, fields, result_key in reads:
                if cli_style:
                    args = []
                    for name, value in fields.items():
                        args.extend(["--" + name.replace("_", "-"),
                                     json.dumps(value)])
                    payload = call(operation, course_id, os.path.dirname(base), args)
                else:
                    payload = call(operation, dict(fields, course_id=course_id))
                if (payload.get("operation") != operation or
                        not isinstance(payload.get(result_key), list)):
                    fail("%s %s did not return its published result shape"
                         % ("CLI" if cli_style else "route", operation))
                if course_module.read_course(base)["fingerprint"] != after_bind:
                    fail("%s changed the course fingerprint" % operation)

        exercise(route, "route-blueprint", route_base)

        course_ops.run(cli_root, "create", {
            "course_id": "cli-blueprint", "title": "CLI blueprint"})
        exercise(cli, "cli-blueprint", os.path.join(cli_root, "cli-blueprint"),
                 cli_style=True)
        print("ok   blueprint bind reaches route and CLI with a new revision; "
              "gate, audit, and staleness keep the fingerprint unchanged")
    finally:
        if proc is not None:
            proc.terminate()
            proc.wait(timeout=10)
        shutil.rmtree(route_root, ignore_errors=True)
        shutil.rmtree(cli_root, ignore_errors=True)


def check_a_degraded_state_never_reads_as_covered():
    """A binding row carrying a state this build cannot read degrades to
    unknown. TREAT-02 forbids inferring coverage from resemblance, and this
    is the surface half of that rule."""
    effective = graph.validate_binding(
        {"binding_kind": "source", "objective": "o", "state": "perfect",
         "confidence": "certain", "rights_snapshot": "granted"})
    if effective["state"] != "unknown" or effective["confidence"] != "unknown":
        fail("an unreadable state or confidence did not degrade to unknown")
    if effective["original_state"] != "perfect":
        fail("the original value was not preserved beside the degraded one")
    print("ok   an unreadable binding state degrades to unknown, never to "
          "covered, and the original is kept beside it")


def check_the_family_is_the_cli_twin():
    tmp = tempfile.mkdtemp(prefix="course_ops_family_cli_")
    try:
        def run(*args):
            return subprocess.run(
                [sys.executable, os.path.join(ROOT, "itembank.py")]
                + list(args), capture_output=True, text=True)

        proc = run("course", "create", "fen", "--title", "Fen", "--root", tmp)
        if proc.returncode != 0:
            fail("itembank course create failed: %s" % proc.stderr.strip())
            return
        base = os.path.join(tmp, "fen")
        source_id = _linked_source(base, "notes.md", "# Notes\n")

        proc = run("course", "add-source", "fen", "--root", tmp, "--source",
                   source_id, "--title", "Field notes", "--json")
        if proc.returncode != 0:
            fail("itembank course add-source failed: %s" % proc.stderr.strip())
            return
        payload = json.loads(proc.stdout)
        if payload["source_object_id"] != source_id:
            fail("add-source reported %r" % payload["source_object_id"])
        if set(payload["rights"]) != set(identity.RIGHTS_OPERATIONS):
            fail("add-source did not report all seven rights")

        proc = run("bind", "list", "--base", base, "--json")
        if proc.returncode != 0:
            fail("itembank bind list failed: %s" % proc.stderr.strip())
            return
        listed = json.loads(proc.stdout)
        if [s["source_object_id"] for s in listed["sources"]] != [source_id]:
            fail("bind list does not show the source add-source recorded")
        if listed["readings"] != []:
            fail("a course with no bindings reported readings")

        proc = run("course", "add-source", "fen", "--root", tmp, "--source",
                   source_id, "--title", "Again")
        if proc.returncode == 0:
            fail("a duplicate source row succeeded from the CLI")
        elif "course.source_already_recorded" not in proc.stderr:
            fail("the duplicate refusal is not typed: %s" % proc.stderr.strip())

        # 19A-04's twins. `bind treatments` answers before the attempt and
        # `bind treatment` makes it, and the answer has to hold: a kind the
        # table calls refused is refused by the command, and recording the
        # right the table named is what changes that.
        proc = run("bind", "treatments", "--base", base, "--source",
                   source_id, "--json")
        if proc.returncode != 0:
            fail("itembank bind treatments failed: %s" % proc.stderr.strip())
            return
        table = json.loads(proc.stdout)
        if table["bindable"]:
            fail("nothing is granted on this source and `bind treatments` "
                 "called %r bindable" % table["bindable"])
        proc = run("bind", "treatment", "--base", base, "--objective",
                   "o", "--source", source_id, "--treatment",
                   "guided-lesson")
        if proc.returncode == 0:
            fail("a treatment the table called refused was bound from the "
                 "CLI")
        elif "course.rights_not_granted" not in proc.stderr:
            fail("the refusal is not typed: %s" % proc.stderr.strip())
        elif "transform" not in proc.stderr:
            fail("the refusal does not name the right a guided lesson "
                 "consumes: %s" % proc.stderr.strip())
        print("ok   the CLI twin records a source, reads it back, refuses a "
              "second row for it, and answers which treatments its rights "
              "allow before one is attempted")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_a_course_write_is_loopback_only():
    """A course write is gated like a day write and a theme save, and the
    family's reads are gated like every other read (19A-02, 19A-03).

    The literal set is not the assertion; the behaviour is. Every operation
    the spine calls a read is RUN against a real course and has to leave the
    sidecar's fingerprint exactly as it found it, so a later wave that
    classifies a write as a read fails here rather than serving that write to
    a phone on the same wifi.
    """
    for name in course_ops.READ_OPERATIONS:
        if name not in course_ops.OPERATIONS:
            fail("%r is classified as a read and is not an operation" % name)
    for name in course_ops.OPERATIONS:
        if name not in course_ops.OPERATION_ENGINE:
            fail("operation %r names no engine function" % name)

    # What each read needs beyond a course id to be runnable. Declared, and
    # asserted complete below, so a wave that adds a read with required
    # fields cannot quietly drop it out of this check: an unexercised read is
    # a write nobody noticed until a phone on the same wifi found it.
    read_fields = {"bindings": {}, "structure": {}, "treatments": {},
                   "autonomy": {"declared_level": "approved-bounded-write",
                                "bindings_requested": 3},
                   "replay": {"operation_id": "*declared*"},
                   "blueprint_gate": {"questions": []},
                   "audit": {"vocabulary_members": {}},
                   "staleness": {"dependents": []},
                   "verify_package": {"package_id": "*exported*"},
                   "package_losses": {"package_id": "*exported*"}}
    for name in course_ops.READ_OPERATIONS:
        if name not in read_fields:
            fail("the read %r has no entry in this check's field table, so "
                 "it is never run and its read-ness is asserted by the "
                 "READ_OPERATIONS tuple alone" % name)

    tmp = tempfile.mkdtemp(prefix="course_ops_gate_")
    try:
        course_ops.run(tmp, "create", {"course_id": "fen", "title": "Fen"})
        base = os.path.join(tmp, "fen")
        declared = course_ops.run(
            tmp, "begin_operation",
            {"course_id": "fen", "intent": "exercise every read",
             "actor_role": "course-builder",
             "autonomy": "recommend-only"}, actor_name="tester")
        exported = course_ops.run(
            tmp, "export_package", {"course_id": "fen"}, actor_name="tester")
        for name in course_ops.READ_OPERATIONS:
            extra = dict(read_fields[name])
            if extra.get("operation_id") == "*declared*":
                extra["operation_id"] = declared["operation_id"]
            if extra.get("package_id") == "*exported*":
                extra["package_id"] = exported["package_id"]
            before = course_module.read_course(base)
            request = dict(extra)
            if "package_id" not in request:
                request["course_id"] = "fen"
            course_ops.run(tmp, name, request)
            after = course_module.read_course(base)
            if after["fingerprint"] != before["fingerprint"]:
                fail("the %r operation is served behind the read-side gate "
                     "and changed the sidecar's fingerprint; a --lan daemon "
                     "would expose that write to the network" % name)
            if after["revision"] != before["revision"]:
                fail("the %r operation advanced the sidecar's revision" % name)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    source = open(os.path.join(ROOT, "surfaces", "daemon.py"),
                  encoding="utf-8").read()
    spine = source.split("def _course_operation(", 1)[1].split("\ndef ", 1)[0]
    if "_reject_cross_origin_write(handler)" not in spine:
        fail("the course spine does not reach the write-side gate, so a "
             "--lan daemon would let a phone mint, rename or bind a course")
    if "READ_OPERATIONS" not in spine:
        fail("the course spine gates every operation the same way, so its "
             "reads are refused or its writes are exposed")
    print("ok   a course write is loopback-only, and every operation the "
          "spine calls a read leaves the sidecar untouched")

def _course_with_two_objectives(tmp, course_id="fen"):
    """One course, one container, two objectives, all through the spine."""
    course_ops.run(tmp, "create", {"course_id": course_id, "title": "Fen"})
    container = course_ops.run(tmp, "add_container",
                               {"course_id": course_id, "label": "module",
                                "title": "Module 1"}, actor_name="tester")
    first = course_ops.run(tmp, "add_objective",
                           {"course_id": course_id,
                            "container": container["container_id"],
                            "statement": "O1 Explain minerotrophy."},
                           actor_name="tester")
    second = course_ops.run(tmp, "add_objective",
                            {"course_id": course_id,
                             "container": container["container_id"],
                             "statement": "O2 Predict the water table."},
                            actor_name="tester")
    return container, first, second


def check_structure_adds_no_edges_and_claims_no_order():
    """GRAPH-01: where a container sits in the outline is structure, not a
    prerequisite claim. A course whose week 2 follows week 1 has said nothing
    about what must be learned first, and a surface that inferred otherwise
    would gate a learner on a guess."""
    tmp = tempfile.mkdtemp(prefix="course_ops_structure_")
    try:
        container, first, second = _course_with_two_objectives(tmp)
        doc = course_module.read_course(os.path.join(tmp, "fen"))["doc"]
        if doc["edges"]:
            fail("adding a container and two objectives recorded %d edges; "
                 "structure is not a prerequisite claim" % len(doc["edges"]))
        if len(doc["structure"]) != 1 or len(doc["objectives"]) != 2:
            fail("the sidecar holds %d containers and %d objectives"
                 % (len(doc["structure"]), len(doc["objectives"])))
        if first["origin"] != "local":
            fail("an objective added from a surface has origin %r; no "
                 "request may claim imported" % first["origin"])
        node, _ = course_ops.operation_schema("add_objective")
        if "origin" in node["properties"]:
            fail("the add_objective node publishes an origin field, so a "
                 "client could claim `imported` and make a hand-authored row "
                 "un-editable for a reason that was never true")

        try:
            course_ops.run(tmp, "add_objective",
                           {"course_id": "fen", "container": "nosuch",
                            "statement": "X"})
        except course_module.CourseError as err:
            if err.code != "course.unknown_container":
                fail("an unknown container refused with %r" % err.code)
            if "Next safe action" not in err.message:
                fail("the unknown-container refusal names no next action")
        else:
            fail("an objective was placed in a container that does not exist")
        print("ok   a container and an objective each add zero edges, and "
              "an objective from a surface is always local")
        return tmp, first, second
    except Exception:
        shutil.rmtree(tmp, ignore_errors=True)
        raise


def check_the_authored_order_is_reported_never_rewritten():
    made = check_structure_adds_no_edges_and_claims_no_order()
    if made is None:
        return
    tmp, first, second = made
    try:
        one, two = first["objective_id"], second["objective_id"]
        course_ops.run(tmp, "add_edge",
                       {"course_id": "fen", "source": one,
                        "edge_type": "prerequisite-of", "target": two,
                        "rationale": "chemistry before dynamics"},
                       actor_name="tester")
        for request, code in (
                ({"source": one, "edge_type": "prerequisite-of",
                  "target": two}, "graph.duplicate_edge"),
                ({"source": one, "edge_type": "prerequisite-of",
                  "target": one}, "graph.self_edge"),
                ({"source": one, "edge_type": "prerequisite-of",
                  "target": "nosuch"}, "graph.unknown_objective")):
            request["course_id"] = "fen"
            try:
                course_ops.run(tmp, "add_edge", request)
            except graph.GraphError as err:
                if err.code != code:
                    fail("%r refused with %r, expected %r"
                         % (request, err.code, code))
            else:
                fail("%r was accepted; a graph that swallows a contradiction "
                     "cannot answer a question" % request)

        # A prerequisite pointing backwards through the authored order is
        # RECORDED and warned about. Refusing it would be this daemon
        # deciding the author's sequence for them.
        before = len(course_module.read_course(
            os.path.join(tmp, "fen"))["doc"]["edges"])
        added = course_ops.run(tmp, "add_edge",
                               {"course_id": "fen", "source": two,
                                "edge_type": "prerequisite-of",
                                "target": one}, actor_name="tester")
        after = course_module.read_course(os.path.join(tmp, "fen"))["doc"]
        if len(after["edges"]) != before + 1:
            fail("a backwards prerequisite was not recorded")
        if not added["order_warnings"]:
            fail("a backwards prerequisite produced no warning")
        if [row["id"] for row in after["objectives"]] != [one, two]:
            fail("the authored order was rewritten; it is the author's and "
                 "a projection that silently reorders makes every future "
                 "diff unreadable")

        reading = course_ops.run(tmp, "structure", {"course_id": "fen"})
        if len(reading["order_warnings"]) < 2:
            fail("the read reports %d order warnings; a violated "
                 "prerequisite and a cycle are two"
                 % len(reading["order_warnings"]))
        if not any("cycle" in line for line in reading["order_warnings"]):
            fail("a prerequisite cycle is not named in the reading")
        proposed = course_ops.run(tmp, "structure",
                                  {"course_id": "fen",
                                   "propose_order": True})
        if proposed["proposed_order"] is not None:
            fail("an order was proposed over a cycle")
        if "cycle" not in proposed["proposed_order_refused"]:
            fail("the refusal to propose an order does not say why")
        print("ok   a backwards prerequisite is recorded and warned about, a "
              "cycle is named and never broken, and no order is rewritten")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_an_identity_move_adds_rows_and_deletes_none():
    """GRAPH-04, from the surface. An objective the learner's evidence was
    recorded against has to stay in the file, or that evidence stops naming
    anything."""
    tmp = tempfile.mkdtemp(prefix="course_ops_identity_")
    try:
        _container, first, second = _course_with_two_objectives(tmp)
        one, two = first["objective_id"], second["objective_id"]
        before = list(course_module.read_course(
            os.path.join(tmp, "fen"))["doc"]["objectives"])

        renamed = course_ops.run(tmp, "rename_objective",
                                 {"course_id": "fen", "objective": one,
                                  "statement": "O1 Explain the fen.",
                                  "rationale": "narrower and testable"},
                                 actor_name="tester")
        split = course_ops.run(tmp, "split_objective",
                               {"course_id": "fen", "objective": two,
                                "statements": ["O2a First half.",
                                               "O2b Second half."],
                                "rationale": "two demands"},
                               actor_name="tester")
        merged = course_ops.run(tmp, "merge_objectives",
                                {"course_id": "fen",
                                 "objectives": [one, two],
                                 "statement": "O Combined.",
                                 "rationale": "one demand after all"},
                                actor_name="tester")

        doc = course_module.read_course(os.path.join(tmp, "fen"))["doc"]
        rows = dict((row["id"], row) for row in doc["objectives"])
        for row in before:
            if row["id"] not in rows:
                fail("objective %s was removed by an identity move; nothing "
                     "in an identity chain is ever deleted" % row["id"])
            elif rows[row["id"]]["statement"] != row["statement"]:
                fail("objective %s was edited in place rather than "
                     "succeeded" % row["id"])
        if len(split["successor_ids"]) != 2:
            fail("a split into two produced %d rows"
                 % len(split["successor_ids"]))
        for result in (renamed, split, merged):
            if result["migration_state"] != "proposed":
                fail("a %s was recorded as %r rather than proposed; settling "
                     "it is a reviewer's act"
                     % (result["operation"], result["migration_state"]))
            if result["settled"]:
                fail("%s reported itself settled" % result["operation"])
            if "reject" not in result["undo"]:
                fail("%s's undo does not point at rejecting the migration"
                     % result["operation"])
        kinds = sorted(row["kind"] for row in doc["migrations"])
        if kinds != ["merge", "rename", "split"]:
            fail("the sidecar records migrations %r" % kinds)
        print("ok   rename, split and merge each add rows, delete none, and "
              "record a migration a reviewer still has to settle")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_an_imported_objective_is_immutable_and_still_revisable():
    tmp = tempfile.mkdtemp(prefix="course_ops_overlay_")
    try:
        course_ops.run(tmp, "create", {"course_id": "fen", "title": "Fen"})
        base = os.path.join(tmp, "fen")
        read = course_module.read_course(base)
        imported = graph.add_objective(read["doc"], "I An imported objective.",
                                       origin="imported", import_version="v1")
        course_module.write_course(base, read["doc"], read["fingerprint"],
                                   "human", "tester")

        overlay = course_ops.run(tmp, "overlay_objective",
                                 {"course_id": "fen",
                                  "objective": imported["id"],
                                  "statement": "I A local revision."},
                                 actor_name="tester")
        doc = course_module.read_course(base)["doc"]
        rows = dict((row["id"], row) for row in doc["objectives"])
        original = rows[imported["id"]]
        if original["statement"] != "I An imported objective.":
            fail("the imported row was edited; GRAPH-01 binds an imported "
                 "scope as an immutable version")
        if original["origin"] != "imported":
            fail("the imported row's origin changed to %r"
                 % original["origin"])
        made = rows[overlay["overlay_id"]]
        if made["overlays"] != imported["id"]:
            fail("the overlay does not point back at the import")
        if made["origin"] != "local":
            fail("an overlay was recorded with origin %r" % made["origin"])
        if overlay["migration_kind"] != "overlay":
            fail("the overlay recorded migration kind %r"
                 % overlay["migration_kind"])
        print("ok   an imported objective is never edited in place, and an "
              "overlay revises it as a sibling row that points back at it")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_the_command_builds_its_request_from_the_document():
    """The CLI fills each published property from the argparse attribute of
    the same name, so a field the document publishes and the parser forgot is
    a visible gap rather than a silently dropped argument."""
    from surfaces import cli

    parser = cli.build_parser()
    actions = {}
    for action in parser._subparsers._group_actions[0].choices["course"] \
            ._subparsers._group_actions[0].choices.items():
        actions[action[0]] = action[1]
    for name, sub in sorted(actions.items()):
        operation = name.replace("-", "_")
        if operation not in course_ops.OPERATIONS:
            continue                                   # `show`, a read helper
        node, _ = course_ops.operation_schema(operation)
        dests = set(a.dest for a in sub._actions)
        for field in node.get("properties") or ():
            if field == "operation":
                continue
            if field not in dests:
                fail("`itembank course %s` has no argument for the published "
                     "field %r, so a caller can reach that field from the "
                     "route and not from the command" % (name, field))
        for field in node.get("required") or ():
            if field in ("operation", "course_id"):
                continue
            required = [a for a in sub._actions
                        if a.dest == field and a.required]
            if not required:
                fail("`itembank course %s` does not require %r, which the "
                     "published node does" % (name, field))
    print("ok   every published field of every course operation has an "
          "argument on its CLI twin, and every required one is required")


def check_the_bind_commands_reach_every_published_field():
    """The same gap-finder `itembank course` gets, applied to the two twins
    19A-04 hangs under `itembank bind`.

    It is a separate check because the mapping is not one-to-one there: the
    course commands are schema-driven and name every argument exactly as the
    node names it, while `bind` predates the spine and spells two fields
    differently (`--grant`/`--deny` build the `grants` object, and the course
    id is read from the sidecar at `--base` rather than typed). So the
    correspondence is declared rather than assumed, and the assertion is that
    every published field is reachable from the command by SOME argument.
    """
    from surfaces import cli

    parser = cli.build_parser()
    binds = parser._subparsers._group_actions[0].choices["bind"] \
        ._subparsers._group_actions[0].choices
    # `course_id` is never an argument here: `--base` is the course root a
    # person is standing in and the id is read off its sidecar (19A-02).
    supplied = {"course_id", "operation"}
    for action, operation, spelled in (
            ("treatment", "bind_treatment", {}),
            ("treatments", "treatments", {}),
            # `bind`'s deprecated treatment mode is deliberately not
            # reachable from the command: `bind treatment` sends
            # `bind_treatment` instead, so the deprecation has one caller
            # (a client that already used it) rather than two.
            ("source", "bind", {"binding_kind": None, "treatment": None}),
            ("list", "bindings", {}),
            ("rights", "rights", {"grants": "grant"})):
        sub = binds[action]
        dests = set(a.dest for a in sub._actions)
        node, _ = course_ops.operation_schema(operation)
        for field in node.get("properties") or ():
            if field in supplied:
                continue
            if field in spelled:
                if spelled[field] and spelled[field] not in dests:
                    fail("`itembank bind %s` declares %r for the published "
                         "field %r and has no such argument"
                         % (action, spelled[field], field))
                continue
            if field not in dests:
                fail("`itembank bind %s` has no argument for the published "
                     "field %r, so a caller can reach that field from POST "
                     "/api/course/%s and not from the command"
                     % (action, field, operation.replace("_", "-")))
        for field in node.get("required") or ():
            if field in supplied or field in spelled:
                continue
            if not [a for a in sub._actions if a.dest == field and a.required]:
                fail("`itembank bind %s` does not require %r, which the "
                     "published node does" % (action, field))
    print("ok   every published field of the bind-family operations is "
          "reachable from its CLI twin")


def check_migration_settlement_surfaces():
    def proposed(root, course_id):
        base = os.path.join(root, course_id)
        course_ops.run(root, "create", {"course_id": course_id,
                                         "title": course_id},
                       actor_name="proposer")
        course_ops.run(root, "add_objective", {"course_id": course_id,
                                                "statement": "learn"},
                       actor_name="proposer")
        oid = course_module.read_course(base)["doc"]["objectives"][0]["id"]
        made = course_ops.run(
            root, "rename_objective", {"course_id": course_id,
                                         "objective": oid,
                                         "statement": "learn more",
                                         "rationale": "clarify"},
            actor_name="proposer")
        return base, made["migration_id"]

    def snapshot(base):
        read = course_module.read_course(base)
        return (read["fingerprint"],
                json.dumps(read["doc"]["objectives"], sort_keys=True),
                json.dumps(read["doc"]["migrations"], sort_keys=True))

    def refused(label, base, invoke, code):
        before = snapshot(base)
        result = invoke()
        if code not in str(result):
            fail("%s refused with %r, not %s" % (label, result, code))
        after = snapshot(base)
        if after != before:
            fail("%s changed fingerprint, objective rows, or migration rows"
                 % label)

    def cli(root, operation, course_id, migration_id, rationale, actor,
            expected=None):
        command = [sys.executable, "itembank.py", "course", operation,
                   course_id, "--migration-id", migration_id,
                   "--rationale", rationale, "--actor", actor,
                   "--root", root, "--json"]
        if expected is not None:
            command.extend(["--expect", expected])
        return subprocess.run(command, text=True, capture_output=True)

    tmp = tempfile.mkdtemp(prefix="course_migration_surface_")
    try:
        base, mid = proposed(tmp, "cli_course")
        refused("CLI proposer acceptance", base,
                lambda: cli(tmp, "accept-migration", "cli_course", mid,
                            "review", "proposer").stderr,
                "graph.migration_self_accept")
        refused("CLI proposer rejection", base,
                lambda: cli(tmp, "reject-migration", "cli_course", mid,
                            "review", "proposer").stderr,
                "graph.migration_self_accept")
        refused("CLI empty rationale", base,
                lambda: cli(tmp, "accept-migration", "cli_course", mid,
                            "   ", "reviewer").stderr,
                "graph.empty_rationale")
        refused("CLI unknown migration", base,
                lambda: cli(tmp, "accept-migration", "cli_course", "unknown",
                            "review", "reviewer").stderr,
                "graph.migration_unknown")
        refused("CLI stale fingerprint", base,
                lambda: cli(tmp, "accept-migration", "cli_course", mid,
                            "review", "reviewer", "stale").stderr,
                "journal.stale_preflight")
        objectives = snapshot(base)[1]
        proc = cli(tmp, "accept-migration", "cli_course", mid, "reviewed",
                   "reviewer")
        if proc.returncode or json.loads(proc.stdout).get("migration_state") != "accepted":
            fail("CLI migration acceptance failed: %s" % proc.stderr)
        accepted = course_module.read_course(base)
        row = [r for r in accepted["doc"]["migrations"]
               if r["migration_id"] == mid][0]
        if (row.get("reviewer") != "reviewer" or
                json.dumps(accepted["doc"]["objectives"], sort_keys=True) != objectives or
                hasattr(course_module, "evidence")):
            fail("CLI acceptance changed objective rows or transferred evidence")
        refused("CLI already-settled migration", base,
                lambda: cli(tmp, "reject-migration", "cli_course", mid,
                            "again", "reviewer").stderr,
                "graph.migration_already_settled")

        route, mid = proposed(tmp, "route_course")
        proc, url, _ = start_daemon(tmp)
        def route_request(operation, migration_id, rationale, actor="reviewer",
                          expected=None):
            body = {"course_id": "route_course", "migration_id": migration_id,
                    "rationale": rationale, "actor": actor}
            if expected is not None:
                body["expected_fingerprint"] = expected
            return json_request(url + "api/course/" + operation, body)

        refused("route proposer acceptance", route,
                lambda: route_request("accept-migration", mid, "review", "proposer"),
                "graph.migration_self_accept")
        refused("route proposer rejection", route,
                lambda: route_request("reject-migration", mid, "review", "proposer"),
                "graph.migration_self_accept")
        refused("route empty rationale", route,
                lambda: route_request("reject-migration", mid, "   "),
                "graph.empty_rationale")
        refused("route unknown migration", route,
                lambda: route_request("reject-migration", "unknown", "review"),
                "graph.migration_unknown")
        refused("route stale fingerprint", route,
                lambda: route_request("reject-migration", mid, "review",
                                      expected="stale"),
                "journal.stale_preflight")
        objectives = snapshot(route)[1]
        status, body = route_request("reject-migration", mid, "not ready")
        if status != 200 or body.get("migration_state") != "rejected":
            fail("route migration rejection failed: %r" % body)
        read = course_module.read_course(route)
        row = [r for r in read["doc"]["migrations"] if r["migration_id"] == mid][0]
        if (row.get("reviewer") != "reviewer" or
                json.dumps(read["doc"]["objectives"], sort_keys=True) != objectives or
                hasattr(course_module, "evidence")):
            fail("route rejection changed objective rows or transferred evidence")
        refused("route already-settled migration", route,
                lambda: route_request("accept-migration", mid, "again"),
                "graph.migration_already_settled")
        print("ok   migration settlement refusals preserve rows on CLI and route")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_package_family_reaches_route_and_cli_with_clean_restore():
    """19A-08: all four package doors use fixed local workspace paths."""
    tmp = tempfile.mkdtemp(prefix="course_ops_package_")
    route_source = os.path.join(tmp, "route_source")
    route_dest = os.path.join(tmp, "route_dest")
    cli_source = os.path.join(tmp, "cli_source")
    cli_dest = os.path.join(tmp, "cli_dest")
    for path in (route_source, route_dest, cli_source, cli_dest):
        os.makedirs(path)
    proc = None
    try:
        course_ops.run(route_source, "create",
                       {"course_id": "route-course", "title": "Route package"})
        route_course = os.path.join(route_source, "route-course")
        with open(os.path.join(route_course, "not-bound.txt"), "w",
                  encoding="utf-8") as fh:
            fh.write("this file is named as a loss, not carried\n")
        route_read = course_module.read_course(route_course)
        proc, url, _lines = start_daemon(route_source)

        status, _stale = json_request(
            url + "api/course/export-package",
            {"course_id": "route-course",
             "expected_fingerprint": "sha256:" + "0" * 64})
        if status != 400 or os.path.exists(os.path.join(
                route_source, course_package.PACKAGE_DIRNAME)):
            fail("a stale export preflight wrote into the package namespace")

        status, exported = json_request(
            url + "api/course/export-package",
            {"course_id": "route-course",
             "expected_fingerprint": route_read["fingerprint"]})
        if status != 200:
            fail("route package export returned %r: %r" % (status, exported))
            return
        package_id = exported.get("package_id")
        expected_relpath = "_packages/" + str(package_id)
        if exported.get("package_path") != expected_relpath:
            fail("route package path was %r, not %r"
                 % (exported.get("package_path"), expected_relpath))
        for key in ("losses", "loss_report_text", "rights_basis",
                    "remote_egress", "complete", "restorable", "undo"):
            if key not in exported:
                fail("route export response omitted %s" % key)
        if exported.get("remote_egress") != "none" or \
                not exported.get("complete") or not exported.get("restorable"):
            fail("route export did not report local, complete, restorable: %r"
                 % exported)
        if not any(row.get("category") == "unregistered-file" and
                   row.get("target") == "not-bound.txt"
                   for row in exported.get("losses") or ()):
            fail("the current F-LOSS unregistered row did not reach the surface")
        if exported.get("loss_report_text") != course_package.loss_report_text(
                course_package.read_manifest(os.path.join(
                    route_source, expected_relpath))):
            fail("the route did not expose the exact package loss report text")

        for name in ("verify-package", "package-losses"):
            status, payload = json_request(
                url + "api/course/" + name, {"package_id": package_id})
            if status != 200 or payload.get("package_id") != package_id:
                fail("route %s returned %r: %r" % (name, status, payload))
            elif payload.get("losses") != exported.get("losses") or \
                    payload.get("loss_report_text") != \
                    exported.get("loss_report_text"):
                fail("route %s changed the package's loss report" % name)

        status, _bad = json_request(
            url + "api/course/export-package",
            {"course_id": "route-course", "dest": "/tmp/not-allowed"})
        if status != 400:
            fail("a route request chose its package destination")
        if os.path.exists(os.path.join(route_source, "tmp", "not-allowed")):
            fail("a refused destination field wrote a directory")

        proc.terminate()
        proc.wait(timeout=10)
        proc = None
        os.makedirs(os.path.join(route_dest, course_package.PACKAGE_DIRNAME))
        shutil.copytree(os.path.join(route_source, expected_relpath),
                        os.path.join(route_dest, expected_relpath))
        proc, url, _lines = start_daemon(route_dest)
        status, restored = json_request(
            url + "api/course/restore-package", {"package_id": package_id})
        if status != 200:
            fail("route package restore returned %r: %r" % (status, restored))
        elif not os.path.isdir(os.path.join(
                route_dest, restored.get("course_object_id", "missing"))):
            fail("route restore did not publish under course object identity")
        elif restored.get("course_path") != restored.get("course_object_id"):
            fail("route restore exposed a path other than course identity")
        if os.path.exists(os.path.join(
                route_dest, course_package.PACKAGE_DIRNAME,
                course_package.PACKAGE_RESTORE_DIRNAME)) and any(os.scandir(
                    os.path.join(route_dest, course_package.PACKAGE_DIRNAME,
                                 course_package.PACKAGE_RESTORE_DIRNAME))):
            fail("successful route restore left its staging directory behind")
        published = os.path.join(route_dest, restored["course_object_id"])
        alias = os.path.join(route_dest, "same-course-different-folder")
        os.rename(published, alias)
        status, duplicate = json_request(
            url + "api/course/restore-package", {"package_id": package_id})
        if status != 400 or "package.duplicate_course" not in str(duplicate):
            fail("restore did not refuse a duplicate identity at another path")

        proc.terminate()
        proc.wait(timeout=10)
        proc = None
        course_ops.run(cli_source, "create",
                       {"course_id": "cli-course", "title": "CLI package"})

        def cli(*args):
            completed = subprocess.run(
                [sys.executable, os.path.join(ROOT, "itembank.py")] + list(args),
                capture_output=True, text=True)
            if completed.returncode != 0:
                fail("itembank %s failed: %s"
                     % (" ".join(args), completed.stderr.strip()))
                return {}
            return json.loads(completed.stdout)

        cli_export = cli("course", "export-package", "cli-course",
                         "--root", cli_source, "--json")
        cli_id = cli_export.get("package_id")
        for action in ("verify-package", "package-losses"):
            read = cli("course", action, cli_id, "--root", cli_source,
                       "--json")
            if read.get("loss_report_text") != cli_export.get("loss_report_text"):
                fail("CLI %s changed the loss report" % action)
        cli_relpath = os.path.join(course_package.PACKAGE_DIRNAME, cli_id)
        os.makedirs(os.path.join(cli_dest, course_package.PACKAGE_DIRNAME))
        shutil.copytree(os.path.join(cli_source, cli_relpath),
                        os.path.join(cli_dest, cli_relpath))
        cli_restore = cli("course", "restore-package", cli_id,
                          "--root", cli_dest, "--actor", "tester", "--json")
        if not cli_restore.get("complete") or not os.path.isdir(os.path.join(
                cli_dest, cli_restore.get("course_object_id", "missing"))):
            fail("CLI restore did not publish a complete course")
        print("ok   package export, verify, losses, and fresh restore reach "
              "route and CLI through fixed local workspace paths")
    finally:
        if proc is not None:
            proc.terminate()
            proc.wait(timeout=10)
        shutil.rmtree(tmp, ignore_errors=True)


def check_create_containment_route_cli_and_runtime():
    """F1: every door refuses dot paths, and runtime checks resolved roots."""
    with tempfile.TemporaryDirectory(prefix="course_create_containment_") as tmp:
        root = os.path.join(tmp, "workspace")
        outside = os.path.join(tmp, "outside")
        os.mkdir(root)
        os.mkdir(outside)
        proc, url, _lines = start_daemon(root)
        try:
            for course_id in (".", ".."):
                status, _ = json_request(url + "api/course/create",
                    {"course_id": course_id, "title": "Invalid"})
                if status != 400:
                    fail("F1 route accepted the dot-directory id %r" % course_id)
                result = subprocess.run([sys.executable, os.path.join(ROOT, "itembank.py"),
                    "course", "create", course_id, "--title", "Invalid", "--root", root],
                    capture_output=True, text=True)
                if result.returncode == 0:
                    fail("F1 CLI accepted the dot-directory id %r" % course_id)
                try:
                    course_ops._op_create(root, {"course_id": course_id, "title": "Invalid"},
                                          "human", "fixture")
                except course_module.CourseError as err:
                    if err.code != "course.path_outside_root":
                        fail("F1 runtime gave the wrong containment refusal")
                else:
                    fail("F1 direct runtime accepted %r" % course_id)
            try:
                os.symlink(outside, os.path.join(root, "linked-course"), target_is_directory=True)
            except (OSError, NotImplementedError):
                pass
            else:
                try:
                    course_ops.run(root, "create", {"course_id": "linked-course", "title": "Invalid"})
                except course_module.CourseError as err:
                    if err.code != "course.path_outside_root":
                        fail("F1 symlink escape gave the wrong refusal")
                else:
                    fail("F1 runtime followed a course directory outside the root")
            for directory in (tmp, root, outside):
                if os.path.exists(os.path.join(directory, course_module.COURSE_SIDECAR_FILENAME)):
                    fail("F1 a rejected create wrote a sidecar")
            if os.listdir(outside):
                fail("F1 the outside directory was changed")
        finally:
            proc.terminate()
            proc.wait(timeout=10)
        print("ok   F1 schema, runtime, route and CLI reject dot paths and resolved escapes")


def check_package_publication_races():
    """F2/F4/F5: stale, incomplete and raced packages never publish."""
    with tempfile.TemporaryDirectory(prefix="course_package_races_") as tmp:
        root = os.path.join(tmp, "workspace")
        os.mkdir(root)
        course_ops.run(root, "create", {"course_id": "source", "title": "Synthetic"})
        base = os.path.join(root, "source")
        original_publish = course_package.publish_directory

        def expect_refusal(fn, code):
            try:
                fn()
            except course_package.PackageError as err:
                if err.code != code:
                    fail("package race expected %s, got %s" % (code, err.code))
            else:
                fail("package race was accepted instead of %s" % code)

        collisions = []

        def race_destination(workspace, staging, destination):
            os.mkdir(destination)
            collisions.append((destination, os.stat(destination)))
            return original_publish(workspace, staging, destination)

        with mock.patch.object(course_package, "publish_directory", side_effect=race_destination):
            expect_refusal(lambda: course_ops.run(root, "export_package", {"course_id": "source"}),
                           "package.destination_exists")
        for path, before in collisions:
            if not os.path.samestat(before, os.stat(path)) or os.listdir(path):
                fail("F5 no-replace export did not preserve the raced empty destination")

        exported = course_ops.run(root, "export_package", {"course_id": "source"})
        package = os.path.join(root, exported["package_path"])
        dest = os.path.join(tmp, "restore-workspace")
        os.mkdir(dest)
        os.mkdir(os.path.join(dest, course_package.PACKAGE_DIRNAME))
        copied = os.path.join(dest, exported["package_path"])
        shutil.copytree(package, copied)
        with mock.patch.object(course_package, "publish_directory", side_effect=race_destination):
            expect_refusal(lambda: course_ops.run(dest, "restore_package",
                {"package_id": exported["package_id"]}), "package.destination_exists")
        raced, before = collisions[-1]
        if not os.path.samestat(before, os.stat(raced)) or os.listdir(raced):
            fail("F5 no-replace restore did not preserve the raced empty destination")
        os.rmdir(raced)

        manifest = course_package.read_manifest(copied)
        payload = os.path.join(copied, course_package._payload_relpath(manifest["entries"][0]))
        with open(payload, "ab") as fh:
            fh.write(b"\nTampered before restore.\n")
        verified = course_ops.run(dest, "verify_package", {"package_id": exported["package_id"]})
        if verified["complete"] or verified["restorable"]:
            fail("F2 an incomplete package was reported restorable")
        expect_refusal(lambda: course_ops.run(dest, "restore_package",
            {"package_id": exported["package_id"]}), "package.restore_incomplete")
        if os.path.exists(raced):
            fail("F2 incomplete restore published a course")

        original_write = course_package._write_bytes_atomic
        sidecar = os.path.join(base, course_module.COURSE_SIDECAR_FILENAME)
        sidecar_raw = open(sidecar, "rb").read()
        expected = course_module.read_course(base)["fingerprint"]
        changed = []

        def change_course(path, raw):
            original_write(path, raw)
            if not changed:
                changed.append(True)
                with open(sidecar, "wb") as fh:
                    fh.write(sidecar_raw.replace(b"Synthetic", b"Concurrent revision"))

        with mock.patch.object(course_package, "_write_bytes_atomic", side_effect=change_course):
            expect_refusal(lambda: course_ops.run(root, "export_package", {
                "course_id": "source", "expected_fingerprint": expected}), "package.stale_course")
        with open(sidecar, "wb") as fh:
            fh.write(sidecar_raw)

        outside = os.path.join(tmp, "outside")
        os.mkdir(outside)
        link_probe = os.path.join(tmp, "link-probe")
        try:
            os.symlink(outside, link_probe, target_is_directory=True)
        except (OSError, NotImplementedError):
            print("skip F5 symlink races: directory symlinks unavailable")
        else:
            os.unlink(link_probe)
            namespace = os.path.join(root, course_package.PACKAGE_DIRNAME)
            saved_namespace = namespace + "-saved"
            original_ensure = course_package.ensure_package_namespace

            def swap_namespace(workspace):
                original_ensure(workspace)
                os.rename(namespace, saved_namespace)
                os.symlink(outside, namespace, target_is_directory=True)

            with mock.patch.object(course_package, "ensure_package_namespace", side_effect=swap_namespace):
                expect_refusal(lambda: course_ops.run(root, "export_package", {"course_id": "source"}),
                               "package.symlink_payload")
            if os.listdir(outside):
                fail("F5 namespace swap wrote outside the approved workspace")
            os.unlink(namespace)
            os.rename(saved_namespace, namespace)
            original_check = course_package._reject_symlink_tree

            def swap_after_check(path):
                original_check(path)
                os.rename(namespace, saved_namespace)
                os.symlink(outside, namespace, target_is_directory=True)

            with mock.patch.object(course_package, "_reject_symlink_tree", side_effect=swap_after_check):
                expect_refusal(lambda: course_ops.run(root, "verify_package",
                    {"package_id": exported["package_id"]}), "package.symlink_payload")
            os.unlink(namespace)
            os.rename(saved_namespace, namespace)
        print("ok   F2/F4/F5 incomplete restore, stale export, namespace swaps and no-replace publication")


def main():
    check_the_request_document_is_read_off_disk()
    check_every_closed_vocabulary_matches_its_source_of_truth()
    check_bad_requests_refuse_before_anything_is_read()
    check_create_and_rename_reach_the_frozen_engine()
    check_the_command_exists()
    check_a_degraded_state_never_reads_as_covered()
    check_a_rights_snapshot_is_history()
    check_the_treatment_table_has_a_reader()
    check_the_deprecated_bind_mode_writes_the_same_row()
    check_the_family_is_the_cli_twin()
    check_a_course_write_is_loopback_only()
    check_the_authored_order_is_reported_never_rewritten()
    check_an_identity_move_adds_rows_and_deletes_none()
    check_an_imported_objective_is_immutable_and_still_revisable()
    check_the_command_builds_its_request_from_the_document()
    check_the_bind_commands_reach_every_published_field()
    check_parity_and_the_declared_aliases()
    check_the_route_is_the_cli_twin()
    check_director_family_reaches_route_and_cli_with_one_reversible_accept()
    check_blueprint_operations_reach_route_and_cli_without_read_mutation()
    check_every_course_route_dispatches_to_a_real_handler()
    check_migration_settlement_surfaces()
    check_package_family_reaches_route_and_cli_with_clean_restore()
    check_create_containment_route_cli_and_runtime()
    check_package_publication_races()
    if FAILURES:
        print("COURSE OPS: %d failure(s)" % len(FAILURES))
        return 1
    print("ok: course operating surface -- a course is created, renamed, "
          "given a source, granted a right, bound and read back from both "
          "surfaces through one validated spine, every write reaching "
          "journal.commit_operation with an expected base fingerprint and "
          "every right read fresh at the moment of the write")
    return 0


if __name__ == "__main__":
    sys.exit(main())
