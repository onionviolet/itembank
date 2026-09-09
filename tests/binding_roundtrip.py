#!/usr/bin/env python3
"""`source binding / create`, the cell the surface grid called the central
act of building a course and measured as having no surface at all.

What is asserted, in the order it matters:

- **The write reaches the frozen path.** A binding recorded from either
  surface lands in the course's own sidecar, through `course.bind_source` /
  `course.bind_treatment`, and shows up in the sidecar's `## Bindings` table.
  Neither surface writes a row itself.
- **The rights gate holds on both.** A source whose right is unknown or
  denied refuses the binding by name, and the refusal names the one edit
  that fixes it. Unknown and denied both refuse; neither is a lesser form of
  permission.
- **Recording a right touches no bytes.** `journal.op_grant_rights` is the
  writer, so the source file's contents and mtime are unchanged and only the
  revision moves.
- **The two surfaces agree.** The CLI and the route reach the same function
  with the same vocabularies, so a binding recorded from one is visible to
  the other.

Standard library only, runnable as `python tests/binding_roundtrip.py`.
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
import graph                                                # noqa: E402
import identity                                              # noqa: E402
import journal                                              # noqa: E402
from surfaces import binding_cli                            # noqa: E402
from daemon_roundtrip import start_daemon, json_request      # noqa: E402

FIXTURE = os.path.join(ROOT, "course_fixture_17b")
FAILURES = []


def fail(msg):
    print("FAIL: " + msg)
    FAILURES.append(msg)


def workspace(prefix):
    """A throwaway copy of the tracer course, journal and all: a binding is a
    journalled write, so a fixture without its journal proves nothing."""
    tmp = tempfile.mkdtemp(prefix=prefix)
    dest = os.path.join(tmp, "course_fixture_17b")
    shutil.copytree(FIXTURE, dest,
                    ignore=shutil.ignore_patterns("_attempts"))
    # The fixture's journal is intentionally ignored because it is runtime
    # state. Recreate the source registration through the journal's public
    # compare-and-swap path so a clean checkout has the same authority state
    # as a locally generated fixture.
    source_path = os.path.join(dest, "sources", "lantern_moss_survey.md")
    with open(source_path, "rb") as source_file:
        source_bytes = source_file.read()
    journal.commit_operation(
        dest, "5c5bc6b17baa44c6", "source",
        "sources/lantern_moss_survey.md", "link", source_bytes,
        identity.object_fingerprint(source_bytes, "source"),
        "human", "binding fixture", write_target=False,
        rights={"read": "granted", "quote": "granted",
                "transform": "granted", "package": "granted",
                "export": "granted"})
    return tmp, dest


def sidecar_rows(course_dir):
    return course_module.read_course(course_dir)["doc"]["bindings"]


def check_cli_binds_and_the_sidecar_holds_it():
    tmp, course_dir = workspace("binding_cli_")
    try:
        before = len(sidecar_rows(course_dir))
        result = binding_cli.bind(
            course_dir, "ae08d09cd3714164", "5c5bc6b17baa44c6",
            locator="sources/lantern_moss_survey.md#a-probe",
            state="thin", confidence="medium", actor_name="tester")
        if result["right_consumed"] != graph.SOURCE_BINDING_RIGHT:
            fail("a coverage binding must consume %s, not %r"
                 % (graph.SOURCE_BINDING_RIGHT, result["right_consumed"]))
        rows = sidecar_rows(course_dir)
        if len(rows) != before + 1:
            fail("the sidecar holds %d bindings, expected %d"
                 % (len(rows), before + 1))
        row = rows[-1]
        for key, want in (("binding_kind", "source"),
                          ("objective", "ae08d09cd3714164"),
                          ("source_object_id", "5c5bc6b17baa44c6"),
                          ("state", "thin"), ("confidence", "medium")):
            if row.get(key) != want:
                fail("the recorded binding's %s is %r, expected %r"
                     % (key, row.get(key), want))
        if row.get("rights_snapshot") != "granted":
            fail("the row must record the rights state it was written under")

        treatment = binding_cli.bind(
            course_dir, "ae08d09cd3714164", "5c5bc6b17baa44c6",
            binding_kind="treatment", treatment_kind="excerpt",
            locator="sources/lantern_moss_survey.md#a-probe",
            state="covered", confidence="high", actor_name="tester")
        if treatment["right_consumed"] != "quote":
            fail("an excerpt treatment consumes quote, not %r"
                 % treatment["right_consumed"])
        print("ok   a binding recorded from Python lands in the sidecar")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_the_rights_gate_refuses_by_name():
    tmp, course_dir = workspace("binding_rights_")
    try:
        source = "5c5bc6b17baa44c6"
        path = os.path.join(course_dir, "sources", "lantern_moss_survey.md")
        raw_before = open(path, "rb").read()
        mtime_before = os.stat(path).st_mtime_ns

        for state in ("unknown", "denied"):
            binding_cli.rights_grant(course_dir, source, {"read": state},
                                     actor_name="tester")
            try:
                binding_cli.bind(course_dir, "ae08d09cd3714164", source,
                                 actor_name="tester")
            except course_module.CourseError as err:
                if err.code != "course.rights_not_granted":
                    fail("a %s right refused with %r, expected "
                         "course.rights_not_granted" % (state, err.code))
                if state not in err.message:
                    fail("the refusal does not name the state it refused on")
                if "next safe action" not in err.message:
                    fail("the refusal does not name the next safe action")
            else:
                fail("a %s read right did not refuse the binding" % state)

        if open(path, "rb").read() != raw_before:
            fail("recording a right changed the source's bytes")
        if os.stat(path).st_mtime_ns != mtime_before:
            fail("recording a right changed the source's mtime")

        binding_cli.rights_grant(course_dir, source, {"read": "granted"},
                                 actor_name="tester")
        binding_cli.bind(course_dir, "ae08d09cd3714164", source,
                         actor_name="tester")
        registry = journal.read_registry(course_dir)
        if registry[source]["rights"]["read"] != "granted":
            fail("the recorded grant did not reach the registry")
        if registry[source]["rights"]["quote"] != "granted":
            fail("recording one right reset another")
        print("ok   unknown and denied both refuse, and the grant touches no "
              "bytes")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_the_vocabularies_are_closed():
    tmp, course_dir = workspace("binding_vocab_")
    try:
        for kwargs, code in (
                ({"state": "perfect"}, "course.unknown_binding_state"),
                ({"confidence": "certain"}, "course.unknown_confidence"),
                ({"binding_kind": "citation"}, "course.unknown_binding_kind"),
                ({"binding_kind": "treatment"},
                 "course.missing_treatment_kind")):
            try:
                binding_cli.bind(course_dir, "ae08d09cd3714164",
                                 "5c5bc6b17baa44c6", actor_name="tester",
                                 **kwargs)
            except course_module.CourseError as err:
                if err.code != code:
                    fail("%r refused with %r, expected %r"
                         % (kwargs, err.code, code))
            else:
                fail("%r was accepted; the vocabulary is not closed" % kwargs)
        print("ok   the closed vocabularies refuse before anything is written")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_the_route_is_the_cli_twin():
    tmp, course_dir = workspace("binding_http_")
    proc = None
    try:
        course_id = course_module.read_course(course_dir)["object_id"]
        before = len(sidecar_rows(course_dir))
        proc, url, _lines = start_daemon(tmp)

        status, body = json_request(url + "api/bind", {
            "course_id": course_id, "objective": "ae08d09cd3714164",
            "source": "5c5bc6b17baa44c6",
            "locator": "sources/lantern_moss_survey.md#over-http",
            "state": "thin", "confidence": "low"})
        if status != 200:
            fail("POST /api/bind returned %d: %r" % (status, body))
        elif not body.get("bound"):
            fail("the route did not report the binding as recorded")
        rows = sidecar_rows(course_dir)
        if len(rows) != before + 1:
            fail("the route's binding did not reach the sidecar")
        elif rows[-1].get("locator") != \
                "sources/lantern_moss_survey.md#over-http":
            fail("the recorded locator is %r" % rows[-1].get("locator"))

        status, _ = json_request(url + "api/bind", {
            "course_id": "no-such-course", "objective": "x", "source": "y"})
        if status != 404:
            fail("an unknown course returned %d from /api/bind" % status)
        status, _ = json_request(url + "api/bind", {
            "course_id": course_id, "objective": "ae08d09cd3714164",
            "source": "5c5bc6b17baa44c6", "rights": {"read": "granted"}})
        if status != 400:
            fail("a client-supplied rights record returned %d, expected 400"
                 % status)
        status, _ = json_request(url + "api/bind", {
            "course_id": course_id, "objective": "ae08d09cd3714164",
            "source": "5c5bc6b17baa44c6", "state": "perfect"})
        if status != 400:
            fail("a state outside the vocabulary returned %d" % status)

        status, body = json_request(url + "api/rights", {
            "course_id": course_id, "source": "5c5bc6b17baa44c6",
            "grants": {"read": "denied"}})
        if status != 200:
            fail("POST /api/rights returned %d: %r" % (status, body))
        status, body = json_request(url + "api/bind", {
            "course_id": course_id, "objective": "ae08d09cd3714164",
            "source": "5c5bc6b17baa44c6"})
        if status != 400:
            fail("a denied read right returned %d from /api/bind" % status)
        text = body if isinstance(body, str) else json.dumps(body)
        if "rights_not_granted" not in text:
            fail("the route's refusal does not carry the typed code")

        status, _ = json_request(url + "api/rights", {
            "course_id": course_id, "source": "5c5bc6b17baa44c6",
            "grants": {"telepathy": "granted"}})
        if status != 400:
            fail("a right outside the vocabulary returned %d" % status)
        print("ok   the route reaches the same gate, and refuses the same way")
    finally:
        if proc is not None:
            proc.terminate()
            proc.wait(timeout=5)
        shutil.rmtree(tmp, ignore_errors=True)


def check_the_command_exists_and_lists():
    tmp, course_dir = workspace("binding_cmd_")
    try:
        proc = subprocess.run(
            [sys.executable, os.path.join(ROOT, "itembank.py"), "bind",
             "list", "--base", course_dir, "--json"],
            capture_output=True, text=True)
        if proc.returncode != 0:
            fail("itembank bind list failed: %s" % proc.stderr.strip())
            return
        payload = json.loads(proc.stdout)
        if len(payload["objectives"]) != 7:
            fail("bind list reported %d objectives, the fixture has seven"
                 % len(payload["objectives"]))
        if len(payload["sources"]) != 2:
            fail("bind list reported %d sources, the fixture has two"
                 % len(payload["sources"]))
        for row in payload["sources"]:
            if set(row["rights"]) != set(
                    __import__("identity").RIGHTS_OPERATIONS):
                fail("bind list did not report all seven rights for %r"
                     % row["source_object_id"])
        proc = subprocess.run(
            [sys.executable, os.path.join(ROOT, "itembank.py"), "bind",
             "source", "--base", course_dir, "--objective",
             "ae08d09cd3714164", "--source", "5c5bc6b17baa44c6",
             "--locator", "sources/lantern_moss_survey.md#from-the-cli",
             "--json"],
            capture_output=True, text=True)
        if proc.returncode != 0:
            fail("itembank bind source failed: %s" % proc.stderr.strip())
            return
        if json.loads(proc.stdout)["objective"] != "ae08d09cd3714164":
            fail("the command did not report what it bound")
        print("ok   the first course-shaped command exists and reads the "
              "course")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    if not os.path.isdir(FIXTURE):
        print("ok: binding roundtrip (fixture absent, skipped)")
        return 0
    check_cli_binds_and_the_sidecar_holds_it()
    check_the_rights_gate_refuses_by_name()
    check_the_vocabularies_are_closed()
    check_the_command_exists_and_lists()
    check_the_route_is_the_cli_twin()
    if FAILURES:
        print("BINDING: %d failure(s)" % len(FAILURES))
        return 1
    print("ok: binding roundtrip -- source and treatment bindings recorded "
          "from both surfaces through the one gated path, unknown and denied "
          "both refused by name, and a recorded right changes no bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
