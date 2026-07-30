#!/usr/bin/env python3
"""Assert the day surface's wiring, its two computed numbers, and its
degraded paths.

What matters here, and why each is tested rather than trusted:

1. The wiring linter names the row for each of its four error classes
   (unknown lane, missing notes path, malformed date, deck absent from Anki).
   The founding lesson of this repo is that a format that fails silently is
   not a contract, and the wiring is a format.
2. `behind` and `load` are correct against a hand-checked plan, and a
   planned zero ("none", "Slip budget") is never counted as debt.
3. A six-lane reader maps an older five-column log by its header, so a
   historical Mandarin tick stays a Mandarin tick after Linux was inserted
   into the lane order.
4. A closed Anki degrades to an omitted badge, never an error. The page must
   render with Anki closed and with lanes.md missing, and say which parts
   are reduced.

Standard library only, runnable as `python tests/due_roundtrip.py`.
"""
import os, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANES = os.path.join(ROOT, "fixtures", "sample_lanes.md")
PLAN = os.path.join(ROOT, "fixtures", "sample_plan.md")
sys.path.insert(0, ROOT)
import itembank


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def check_wiring():
    wiring, fuses, errors = itembank.parse_lanes(LANES)
    if errors:
        fail("the clean fixture produced wiring errors: %s" % errors)
    if fuses != [("Term starts", "2026-01-12")]:
        fail("global fuses misparsed: %s" % fuses)
    emt = wiring.get("EMT") or fail("EMT row missing from wiring")
    if emt["deck"] != "EMT" or emt["fuse_date"] != "2026-01-08":
        fail("EMT wiring misparsed: %s" % emt)
    if emt["glob"] != "fixtures/*.md":
        fail("the glob column collided with the notes column: %s" % emt)
    if itembank.lint_lane_paths(wiring, LANES):
        fail("path lint flagged fixture paths that exist")
    files = itembank.lane_files(emt, LANES)
    if not files or files[0][1].endswith("sample_bank.md"):
        fail("lane_files must list the notes file first: %s" % files)
    if len(files) < 2:
        fail("the glob matched nothing: %s" % files)


def check_linter_names_rows():
    bad = "\n".join([
        "| Lane | Anki deck | Notes file | Fuse | Fuse date |",
        "|---|---|---|---|---|",
        "| Sec+ | X | | | |",
        "| EMT | EMT | no/such/file.md | ch 1 | Jan 8 |",
        "",
        "| Fuse | Date |",
        "|---|---|",
        "| Term | soonish |",
    ])
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "lanes.md")
        open(p, "w", encoding="utf-8").write(bad)
        wiring, fuses, errors = itembank.parse_lanes(p)
        errors += itembank.lint_lane_paths(wiring, p)
    text = "\n".join(errors)
    for want in ("unknown lane 'Sec+'", "malformed fuse date", "does not exist",
                 "malformed date"):
        if want not in text:
            fail("wiring lint no longer reports: %s\ngot: %s" % (want, text))
    if "line 3" not in text:
        fail("the unknown-lane error does not name its line: %s" % text)
    deck_errors = itembank.lint_lane_decks({"CS": {"deck": "Nope"}},
                                           ["EMT::AAOS-12e", "MATH::1400"])
    if not deck_errors or "Nope" not in deck_errors[0]:
        fail("a deck absent from Anki was not flagged: %s" % deck_errors)
    if itembank.lint_lane_decks({"EMT": {"deck": "EMT"}}, ["EMT::AAOS-12e"]):
        fail("a parent deck with only subdecks in Anki was wrongly flagged")


def check_behind_load():
    plan = {"2026-01-05": {"EMT": "ch 1", "Math": "Ch 1 sets"},
            "2026-01-06": {"EMT": "Slip budget; no required EMT task",
                           "Math": "Ch 1 continue"},
            "2026-01-07": {"EMT": "ch 2", "Math": "none, taper"}}
    log = {"2026-01-05": {"EMT"}}
    if itembank.lane_behind(plan, log, "EMT", "2026-01-07") != 0:
        fail("a ticked day or a planned zero counted as behind for EMT")
    if itembank.lane_behind(plan, log, "Math", "2026-01-07") != 2:
        fail("two unticked Math days did not read as behind 2")
    load = itembank.lane_load(plan, log, "EMT", "2026-01-07", "2026-01-08")
    if load != 0.5:
        fail("EMT load expected 0.5 (1 owed row / 2 days), got %s" % load)
    load = itembank.lane_load(plan, log, "Math", "2026-01-07", "2026-01-07")
    if load != 2.0:
        fail("Math load expected 2.0 (2 behind + 0 today / 1 day), got %s" % load)
    if itembank.lane_load(plan, log, "Math", "2026-01-07", "2026-01-01") is not None:
        fail("a fuse in the past must yield no load, not a division error")


def check_old_log_reader():
    old = "\n".join([
        "# Daily log", "",
        "| Date | EMT | Math | CS | Mandarin | Anki | Day |",
        "|---|---|---|---|---|---|---|",
        "| 2026-01-05 | x | . | . | x | x | floor |", ""])
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "daily_log.md")
        open(p, "w", encoding="utf-8").write(old)
        log = itembank.load_day_log(p)
    if log.get("2026-01-05") != {"EMT", "Mandarin", "Anki"}:
        fail("the five-column log misread after the Linux lane was inserted: %r"
             % log.get("2026-01-05"))


def check_anki_closed():
    os.environ["ANKI_CONNECT_URL"] = "http://127.0.0.1:9"
    try:
        counts, names = itembank.anki_read(["EMT"])
    finally:
        del os.environ["ANKI_CONNECT_URL"]
    if counts is not None or names is not None:
        fail("a closed Anki did not degrade to None")


def check_reduced_page():
    with tempfile.TemporaryDirectory() as d:
        plan_path = os.path.join(d, "plan.md")
        open(plan_path, "w", encoding="utf-8").write(
            "| Date | EMT |\n|---|---|\n| 2026-01-05 | ch 1 |\n")
        plan = itembank.parse_plan(plan_path, 2026)
        info = itembank.day_info(plan, {}, "2026-01-05", plan_path,
                                 os.path.join(d, "lanes.md"))
    if not any("lanes.md" in m for m in info["notes"]):
        fail("a missing lanes.md was not named in the reduced-mode notes")
    page = itembank.day_page("2026-01-05", "Monday", {"EMT": "ch 1"}, set(),
                             0, [], plan_path, info)
    if "lanes.md" not in page:
        fail("the page does not say it is running reduced")
    text = itembank.day_text("2026-01-05", "Monday", {"EMT": "ch 1"}, {}, 0, info)
    if "EMT" not in text or "note:" not in text:
        fail("the text render lost the lane row or the reduced-mode note")


def main():
    check_wiring()
    check_linter_names_rows()
    check_behind_load()
    check_old_log_reader()
    check_anki_closed()
    check_reduced_page()
    print("PASS: wiring linted, behind/load hand-checked, old log mapped, "
          "closed Anki and missing wiring degraded")


if __name__ == "__main__":
    main()
