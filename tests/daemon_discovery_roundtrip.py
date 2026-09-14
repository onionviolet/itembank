#!/usr/bin/env python3
"""Focused regression checks for workspace and linked-course discovery."""
import os
import shutil
import sys
import tempfile


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from surfaces import daemon


BANK = os.path.join(ROOT, "fixtures", "sample_bank.md")
SIDECAR = os.path.join(ROOT, "_sample_course", "course-graph.md")


def fail(message):
    raise AssertionError(message)


def write_course(directory):
    os.makedirs(directory)
    shutil.copy(SIDECAR, os.path.join(directory, "course-graph.md"))


class Handler(object):
    banks = {}
    plans = {}
    collisions = []
    sessions = {}

    def __init__(self, root):
        self.root = root
        self.sent = ""

    def send_html(self, body):
        self.sent = body.decode("utf-8")


def check_linked_course_is_bounded():
    scratch = tempfile.mkdtemp(prefix="itembank-linked-discovery-")
    workspace = os.path.join(scratch, "workspace")
    course = os.path.join(scratch, "approved-course")
    unrelated = os.path.join(scratch, "unrelated")
    forged_course = os.path.join(scratch, "forged-course")
    nested_escape = os.path.join(scratch, "nested-escape")
    os.makedirs(workspace)
    write_course(course)
    os.makedirs(unrelated)
    os.makedirs(forged_course)
    os.makedirs(nested_escape)
    shutil.copy(BANK, os.path.join(course, "visible.md"))
    shutil.copy(BANK, os.path.join(unrelated, "not-a-course.md"))
    shutil.copy(BANK, os.path.join(forged_course, "forged.md"))
    shutil.copy(BANK, os.path.join(nested_escape, "nested-leak.md"))
    shutil.copy(BANK, os.path.join(scratch, "file-leak.md"))
    try:
        os.symlink(course, os.path.join(workspace, "course-link"),
                   target_is_directory=True)
        os.symlink(unrelated, os.path.join(workspace, "ordinary-link"),
                   target_is_directory=True)
        os.symlink(SIDECAR, os.path.join(forged_course, "course-graph.md"))
        os.symlink(forged_course, os.path.join(workspace, "forged-course-link"),
                   target_is_directory=True)
        os.symlink(nested_escape, os.path.join(course, "escape"),
                   target_is_directory=True)
        os.symlink(os.path.join(scratch, "file-leak.md"),
                   os.path.join(course, "file-leak.md"))
    except (OSError, NotImplementedError):
        shutil.rmtree(scratch, ignore_errors=True)
        print("ok - linked-course containment skipped; symlinks unavailable")
        return
    try:
        banks, plans, collisions = daemon.scan_dir(workspace)
        if set(banks) != {"visible"}:
            fail("linked-course scan admitted the wrong banks: %r" % sorted(banks))
        if plans or collisions:
            fail("bounded linked-course scan invented plans or collisions")
        if os.path.realpath(banks["visible"]) != os.path.realpath(
                os.path.join(course, "visible.md")):
            fail("the approved linked-course bank did not resolve to its target")
        print("ok - immediate course links are scanned without nested escape")
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def check_refresh_adds_bank_and_preserves_sessions():
    scratch = tempfile.mkdtemp(prefix="itembank-discovery-refresh-")
    workspace = os.path.join(scratch, "workspace")
    course = os.path.join(scratch, "approved-course")
    os.makedirs(workspace)
    write_course(course)
    try:
        os.symlink(course, os.path.join(workspace, "course-link"),
                   target_is_directory=True)
    except (OSError, NotImplementedError):
        shutil.rmtree(scratch, ignore_errors=True)
        print("ok - discovery refresh skipped; symlinks unavailable")
        return
    try:
        Handler.banks = {}
        Handler.plans = {}
        Handler.collisions = []
        Handler.sessions = {"already-running": {"marker": object()}}
        handler = Handler(workspace)
        old_session = handler.sessions["already-running"]
        daemon.handle_banks(handler)
        if handler.banks:
            fail("the empty linked course produced a bank")

        shutil.copy(BANK, os.path.join(course, "added-after-start.md"))
        refreshed = Handler(workspace)
        daemon.handle_banks(refreshed)
        if set(refreshed.banks) != {"added-after-start"}:
            fail("refresh did not admit the newly added bank: %r"
                 % sorted(refreshed.banks))
        if "added-after-start" not in refreshed.sent:
            fail("the refreshed bank-list page did not render the new bank")
        if refreshed.sessions.get("already-running") is not old_session:
            fail("refresh discarded or replaced existing session state")
        if "added-after-start" not in refreshed.sessions:
            fail("refresh did not configure the newly admitted bank")
        if os.path.exists(os.path.join(course, "_attempts")):
            fail("read-only discovery created assessment state")
        print("ok - refresh admits a new bank and preserves live sessions")
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    check_linked_course_is_bounded()
    check_refresh_adds_bank_and_preserves_sessions()
