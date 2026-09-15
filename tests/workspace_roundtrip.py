#!/usr/bin/env python3
"""FILE-04 durable course roots, learner order, conflict, and recovery."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import course                                               # noqa: E402
import journal                                              # noqa: E402
import workspace                                            # noqa: E402
from surfaces import ia                                     # noqa: E402


def fail(message):
    print("FAIL: " + message)
    raise SystemExit(1)


def eq(actual, expected, message):
    if actual != expected:
        fail("%s: want %r, got %r" % (message, expected, actual))


def make_course(root, dirname, title):
    path = os.path.join(root, dirname)
    os.makedirs(path)
    revision = course.create_course(path, title, "human", "test learner")
    return {"course_object_id": revision["object_id"], "name": title,
            "root": root, "path": path}


def raises_code(fn, code):
    try:
        fn()
    except workspace.WorkspaceError as exc:
        eq(exc.code, code, "typed workspace refusal")
        return
    fail("expected %s" % code)


def check_order_persists_and_undoes():
    base = tempfile.mkdtemp(prefix="workspace_order_")
    try:
        make_course(base, "alpha", "Alpha")
        make_course(base, "beta", "Beta")
        initial = ia.course_shelf_state(base)
        original = [card["course_id"] for card in initial["cards"]]
        desired = list(reversed(original))
        result = workspace.reorder(base, desired, ia.shelf_members(initial), None)
        if not result["entry_id"] or not result["undo"]:
            fail("reorder omitted its journal receipt or undo instruction")
        restarted = ia.course_shelf_state(base)
        eq([card["course_id"] for card in restarted["cards"]], desired,
           "saved order after a fresh read")
        eq(restarted["order_source"], "learner", "manual order authority")
        eq(restarted["workspace_fingerprint"], result["fingerprint"],
           "workspace compare-and-swap fingerprint")

        journal.undo(base, result["entry_id"], "human", "test learner")
        restored = ia.course_shelf_state(base)
        eq(restored["order_source"], "attention", "undo restores no workspace")
        eq([card["course_id"] for card in restored["cards"]], original,
           "undo restores the pre-order shelf")
    finally:
        shutil.rmtree(base, ignore_errors=True)


def check_stale_and_external_edit_conflict():
    base = tempfile.mkdtemp(prefix="workspace_conflict_")
    try:
        make_course(base, "alpha", "Alpha")
        make_course(base, "beta", "Beta")
        state = ia.course_shelf_state(base)
        ids = [card["course_id"] for card in state["cards"]]
        result = workspace.reorder(base, ids, ia.shelf_members(state), None)
        raises_code(lambda: workspace.reorder(
            base, list(reversed(ids)), ia.shelf_members(ia.course_shelf_state(base)),
            "sha256:" + "0" * 64), "workspace.stale_preflight")

        path = workspace.workspace_path(base)
        with open(path, "r", encoding="utf-8") as fh:
            doc = json.load(fh)
        doc["courses"][0]["name"] = "Changed outside itembank"
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        conflicted = workspace.read_workspace(base)
        eq(conflicted["state"], "conflict", "external edit state")
        shelf = ia.course_shelf_state(base)
        eq(shelf["order_source"], "attention", "conflict fallback order")
        eq(shelf["reorderable"], False, "conflict disables reorder")
        raises_code(lambda: workspace.reorder(
            base, ids, ia.shelf_members(shelf), result["fingerprint"]),
            "workspace.conflict")
    finally:
        shutil.rmtree(base, ignore_errors=True)


def check_multi_root_move_and_unavailable_recovery():
    parent = tempfile.mkdtemp(prefix="workspace_roots_")
    base = os.path.join(parent, "base")
    other = os.path.join(parent, "other")
    os.makedirs(base)
    os.makedirs(other)
    try:
        first = make_course(base, "alpha", "Alpha")
        second = make_course(other, "beta", "Beta")
        ids = [second["course_object_id"], first["course_object_id"]]
        workspace.reorder(base, ids, [second, first], None)
        shelf = ia.course_shelf_state(base)
        eq([card["course_id"] for card in shelf["cards"]], ids,
           "two-root learner order")
        eq(ia.course_dir_for(base, second["course_object_id"]), second["path"],
           "course resolution across approved roots")

        original_path = second["path"] + "-original"
        shutil.move(second["path"], original_path)
        imposter = make_course(other, "beta", "Imposter")
        conflicted = ia.course_shelf_state(base)
        pinned = next(card for card in conflicted["cards"]
                      if card["course_id"] == second["course_object_id"])
        eq(pinned["attention"], "needs_reconciliation",
           "path and sidecar identity disagreement")
        if any(card["course_id"] == imposter["course_object_id"]
               for card in conflicted["cards"]):
            fail("an identity mismatch silently enrolled the imposter course")
        shutil.rmtree(imposter["path"])
        shutil.move(original_path, second["path"])

        moved = os.path.join(base, "beta-moved")
        shutil.move(second["path"], moved)
        shelf = ia.course_shelf_state(base)
        eq([card["course_id"] for card in shelf["cards"]], ids,
           "moved course reconciles by stable id")
        eq(sum(card["course_id"] == second["course_object_id"]
               for card in shelf["cards"]), 1,
           "moved course appears once")

        shutil.move(other, other + "-offline")
        shutil.move(moved, os.path.join(other + "-offline", "beta"))
        shelf = ia.course_shelf_state(base)
        unavailable = next(card for card in shelf["cards"]
                           if card["course_id"] == second["course_object_id"])
        eq(unavailable["available"], False, "unreachable root retains card")
        eq(unavailable["chip"], "Root unavailable", "unreachable root label")
    finally:
        shutil.rmtree(parent, ignore_errors=True)


def check_cli_twin():
    base = tempfile.mkdtemp(prefix="workspace_cli_")
    try:
        make_course(base, "alpha", "Alpha")
        make_course(base, "beta", "Beta")
        desired = list(reversed(
            [card["course_id"] for card in ia.course_shelf_state(base)["cards"]]))
        command = [sys.executable, os.path.join(ROOT, "itembank.py"),
                   "shelf", "reorder_courses", base]
        for course_id in desired:
            command.extend(("--course-id", course_id))
        run = subprocess.run(command, text=True, capture_output=True)
        if run.returncode != 0:
            fail("shelf CLI reorder failed: %s" % run.stderr)
        result = json.loads(run.stdout)
        eq(result["course_ids"], desired, "CLI reorder result")
        eq([card["course_id"] for card in ia.course_shelf_state(base)["cards"]],
           desired, "CLI and browser share persisted order")
    finally:
        shutil.rmtree(base, ignore_errors=True)


CHECKS = (check_order_persists_and_undoes,
          check_stale_and_external_edit_conflict,
          check_multi_root_move_and_unavailable_recovery,
          check_cli_twin)


def main():
    for check in CHECKS:
        check()
        print("OK " + check.__name__)
    print("WORKSPACE: %d passed, 0 failed" % len(CHECKS))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
