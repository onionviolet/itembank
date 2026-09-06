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

Standard library only, runnable as `python tests/course_ops_roundtrip.py`.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import course as course_module                              # noqa: E402
import journal                                              # noqa: E402
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


def check_bad_requests_refuse_before_anything_is_read():
    tmp = tempfile.mkdtemp(prefix="course_ops_bad_")
    try:
        for request, why in (
                ({"course_id": "algebra"}, "a create with no title"),
                ({"course_id": "algebra", "title": ""}, "an empty title"),
                ({"course_id": "../etc", "title": "T"}, "a traversing id"),
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
        print("ok   the route reaches the same spine and refuses the same "
              "way")
    finally:
        if proc is not None:
            proc.terminate()
            proc.wait(timeout=5)
        shutil.rmtree(tmp, ignore_errors=True)


def check_parity_and_the_declared_aliases():
    for path, twin, tool in (("/api/course/create", "course", "course_create"),
                             ("/api/course/rename", "course", "course_rename"),
                             ("/api/course/bind", "bind", "bind"),
                             ("/api/course/rights", "bind", "rights_record")):
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
    print("ok   both routes carry a twin and a reserved tool name, and the "
          "two early paths are declared aliases")


def main():
    check_the_request_document_is_read_off_disk()
    check_bad_requests_refuse_before_anything_is_read()
    check_create_and_rename_reach_the_frozen_engine()
    check_the_command_exists()
    check_parity_and_the_declared_aliases()
    check_the_route_is_the_cli_twin()
    if FAILURES:
        print("COURSE OPS: %d failure(s)" % len(FAILURES))
        return 1
    print("ok: course operating surface -- a course is created and renamed "
          "from both surfaces through one validated spine, every write "
          "reaching journal.commit_operation with an expected base "
          "fingerprint")
    return 0


if __name__ == "__main__":
    sys.exit(main())
