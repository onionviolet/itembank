#!/usr/bin/env python3
"""Focused regression checks for the Sources binding form.

The form must submit the published request shape for coverage bindings, keep
its controls after a refused request, and fit a narrow course surface.
"""
import os
import shutil
import tempfile
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import course
import journal
from surfaces import course_ops, daemon


def main():
    panel = daemon.BIND_PANEL
    if "treatment: treatment" in panel:
        raise SystemExit("coverage payload still sends an empty treatment")
    if "if (treatment) { payload.treatment = treatment; }" not in panel:
        raise SystemExit("treatment bindings no longer send their treatment")
    if ".bind-panel .bind-grid select,.bind-panel .bind-grid input" not in panel:
        raise SystemExit("source controls have no narrow viewport constraint")
    if "width:100%" not in panel or "min-width:0" not in panel:
        raise SystemExit("source controls can still widen their container")
    if "window.location.reload()" not in panel or ".catch(function (err)" not in panel:
        raise SystemExit("binding refusal no longer stays on the form")

    tmp = tempfile.mkdtemp(prefix="source_binding_surface_")
    try:
        course_ops.run(tmp, "create", {"course_id": "fen", "title": "Fen"})
        base = os.path.join(tmp, "fen")
        os.makedirs(os.path.join(base, "sources"))
        with open(os.path.join(base, "sources", "notes.md"), "w",
                  encoding="utf-8") as fh:
            fh.write("# Notes\n")
        source_id = journal.op_link(
            base, "source", "sources/notes.md", "human", "tester")["object_id"]
        course_ops.run(tmp, "add_source",
                       {"course_id": "fen", "source_object_id": source_id,
                        "title": "Field notes"}, actor_name="tester")
        course_ops.run(tmp, "rights", {"course_id": "fen", "source": source_id,
                                         "grants": {"read": "granted"}},
                       actor_name="tester")
        container = course_ops.run(
            tmp, "add_container", {"course_id": "fen", "label": "module",
                                    "title": "M1"}, actor_name="tester")
        objective = course_ops.run(
            tmp, "add_objective",
            {"course_id": "fen", "container": container["container_id"],
             "statement": "Read the notes."}, actor_name="tester")["objective_id"]
        result = course_ops.run(
            tmp, "bind",
            {"course_id": "fen", "objective": objective, "source": source_id,
             "locator": "notes.md#heading", "state": "thin",
             "confidence": "low", "binding_kind": "source"},
            actor_name="tester")
        if result.get("binding_kind") != "source":
            raise SystemExit("default form binding did not create coverage")
        row = course.read_course(base)["doc"]["bindings"][-1]
        if row.get("locator") != "notes.md#heading":
            raise SystemExit("real locator was not retained")
        treatment = course_ops.run(
            tmp, "bind",
            {"course_id": "fen", "objective": objective, "source": source_id,
             "locator": "notes.md#heading", "state": "thin",
             "confidence": "low", "binding_kind": "treatment",
             "treatment": "direct-reading"}, actor_name="tester")
        if treatment.get("binding_kind") != "treatment" or \
                treatment.get("treatment_kind") != "direct-reading":
            raise SystemExit("treatment binding did not retain its kind")
        course_ops.run(tmp, "rights", {"course_id": "fen", "source": source_id,
                                         "grants": {"read": "denied"}},
                       actor_name="tester")
        before = len(course.read_course(base)["doc"]["bindings"])
        try:
            course_ops.run(
                tmp, "bind",
                {"course_id": "fen", "objective": objective, "source": source_id,
                 "locator": "notes.md#refused", "state": "thin",
                 "confidence": "low", "binding_kind": "source"},
                actor_name="tester")
        except course.CourseError:
            pass
        else:
            raise SystemExit("a refused source binding was accepted")
        if len(course.read_course(base)["doc"]["bindings"]) != before:
            raise SystemExit("a refused source binding changed the course")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("ok: source binding form submits coverage and treatment shapes, "
          "retains refusals, and constrains narrow controls")


if __name__ == "__main__":
    main()
