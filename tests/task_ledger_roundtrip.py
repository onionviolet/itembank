"""Owner-backed assignment adapter and Today rendering checks."""
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURE = os.path.join(ROOT, "fixtures", "sample_assignments.md")
sys.path.insert(0, ROOT)

from surfaces import day, task_ledger


def fail(message):
    raise AssertionError(message)


def copy_fixture(tmp):
    path = os.path.join(tmp, "Sample_Assignments.md")
    shutil.copyfile(FIXTURE, path)
    return path


def task(view, owner_id):
    return next(item for item in view["tasks"] if item["owner_id"] == owner_id)


def check_read_rank_and_render():
    with tempfile.TemporaryDirectory() as tmp:
        path = copy_fixture(tmp)
        view = task_ledger.snapshot([path], "2026-09-12")
        if view["issues"]:
            fail("valid ledger reported issues: %r" % view["issues"])
        if [item["bucket"] for item in view["tasks"][:3]] != ["Now", "Now", "Next"]:
            fail("tasks were not ranked Now, Now, Next: %r" % view["tasks"])
        html = day.task_section(view, "/day/sample")
        for text in ("Now", "Next", "Later", "Read the opening chapter",
                     "Sample Course", "Overdue by 1 day", "Not provided",
                     "Purpose", "Completion gate", "Authoritative source",
                     "owner-task", "aria-describedby"):
            if text not in html:
                fail("Today task rendering omitted %r" % text)


def check_check_and_uncheck_are_owner_writes():
    with tempfile.TemporaryDirectory() as tmp:
        path = copy_fixture(tmp)
        view = task_ledger.snapshot([path], "2026-09-12")
        before = task(view, "SAMPLE-002")
        result = task_ledger.set_checked(before, True, before["revision"], "2026-09-12")
        if result["status"] != "saved":
            fail("check did not save: %r" % result)
        raw = open(path, encoding="utf-8").read()
        if "| 2026-09-12 | done 2026-09-12 |" not in raw:
            fail("check did not update the exact Status cell")
        if not os.path.exists(os.path.join(tmp, "_journal", "journal.jsonl")):
            fail("check did not append an operation record")
        after = task(task_ledger.snapshot([path], "2026-09-12"), "SAMPLE-002")
        reopened = task_ledger.set_checked(after, False, after["revision"], "2026-09-12")
        if reopened["status"] != "saved":
            fail("uncheck did not save: %r" % reopened)
        raw = open(path, encoding="utf-8").read()
        if "| 2026-09-12 | planned |" not in raw:
            fail("uncheck did not restore the open ledger state")
        entries = open(os.path.join(tmp, "_journal", "journal.jsonl"),
                       encoding="utf-8").read().splitlines()
        if len(entries) != 4:
            fail("two writes should append prepared and applied rows each: %d" % len(entries))


def check_concurrent_external_edit_refuses():
    with tempfile.TemporaryDirectory() as tmp:
        path = copy_fixture(tmp)
        before = task(task_ledger.snapshot([path], "2026-09-12"), "SAMPLE-001")
        with open(path, "a", encoding="utf-8") as fh:
            fh.write("\nExternal owner edit.\n")
        result = task_ledger.set_checked(before, True, before["revision"], "2026-09-12")
        if result["status"] != "conflict" or "nothing was overwritten" not in result["reason"]:
            fail("external edit was not a named no-write conflict: %r" % result)
        if "done 2026-09-12" in open(path, encoding="utf-8").read():
            fail("conflict overwrote the owner")


def check_malformed_and_unavailable():
    with tempfile.TemporaryDirectory() as tmp:
        malformed = os.path.join(tmp, "Malformed_Assignments.md")
        with open(malformed, "w", encoding="utf-8") as fh:
            fh.write("| ID | Type | Title | Source | Assigned | Due | Status | Link |\n"
                     "|---|---|---|---|---|---|---|---|\n"
                     "| BAD-1 | reading | Broken | source | 2026-09-12 | not-a-date | planned | x |\n")
        missing = os.path.join(tmp, "Missing_Assignments.md")
        view = task_ledger.snapshot([malformed, missing], "2026-09-12")
        states = {issue["state"] for issue in view["issues"]}
        if states != {"malformed", "unavailable"}:
            fail("degraded owners were not distinct: %r" % view["issues"])
        html = day.task_section(view, "/day/sample")
        if "malformed owner" not in html or "unavailable owner" not in html:
            fail("degraded owner states were not rendered")


def check_day_surface_wiring_and_post():
    with tempfile.TemporaryDirectory() as tmp:
        ledger = copy_fixture(tmp)
        plan = os.path.join(tmp, "plan.md")
        lanes = os.path.join(tmp, "lanes.md")
        log = os.path.join(tmp, "daily_log.md")
        with open(plan, "w", encoding="utf-8") as fh:
            fh.write("| Date | Math |\n|---|---|\n| 2026-09-12 | Work |\n")
        with open(lanes, "w", encoding="utf-8") as fh:
            fh.write("| Lane | Assignments |\n|---|---|\n| Math | Sample_Assignments.md |\n")
        state = day.day_state(plan, log, lanes, "2026-09-12", base="/day/sample")
        info = day.day_info(state["plan"], state["log"], state["iso"], plan, lanes)
        wired = task(info["tasks"], "SAMPLE-002")
        text_view = day.day_text("2026-09-12", "Saturday",
                                 state["plan"]["2026-09-12"], state["log"], 0, info)
        if "Tasks, owned by their assignment ledgers" not in text_view or \
                "gate: Ledger Status is done" not in text_view:
            fail("CLI task projection omitted owner or completion-gate context")
        rendered = day.day_render(state).decode("utf-8")
        if "Owner-backed to-do" not in rendered or "D.base+'/task'" not in rendered:
            fail("full Day render omitted the wired task UI or task route")
        result = day.apply_task_post(state, {"task_id": wired["task_id"],
                                             "revision": wired["revision"],
                                             "checked": True})
        if result["status"] != "saved":
            fail("Day task route wrapper did not save: %r" % result)
        if state["log"]:
            fail("assignment completion changed Day lane evidence")
        if "done 2026-09-12" not in open(ledger, encoding="utf-8").read():
            fail("Day task wrapper did not update its wired owner")


if __name__ == "__main__":
    check_read_rank_and_render()
    check_check_and_uncheck_are_owner_writes()
    check_concurrent_external_edit_refuses()
    check_malformed_and_unavailable()
    check_day_surface_wiring_and_post()
    print("task ledger roundtrip: ok")
