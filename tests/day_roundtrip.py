#!/usr/bin/env python3
"""Assert that `itembank day` reads a plan, records ticks, and counts a streak.

Three properties matter here and each has burned someone already:

1. A plan table is found by its dated first column, and any other table in the
   same document is ignored. Plans live inside dashboards, next to unrelated
   tables.
2. A tick reaches disk immediately. The whole point of the surface is that the
   day is visibly done; a tick that evaporates is worse than no tick, because
   the streak then lies.
3. The floor is what counts, not the full day. If `day_status` ever demands
   every lane, a floor day reads as a miss and the streak breaks on exactly the
   days the floor exists to protect.

Standard library only, runnable as `python tests/day_roundtrip.py`.
"""
import json, os, re, subprocess, sys, tempfile, threading, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAN = os.path.join(ROOT, "fixtures", "sample_plan.md")
sys.path.insert(0, ROOT)
import itembank


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def check_parser():
    plan = itembank.parse_plan(PLAN, 2026)
    if "2026-01-05" not in plan:
        fail("`**Mon Jan 5**` did not parse into a dated row. Got: %s" % sorted(plan))
    if "2026-01-07" not in plan:
        fail("an ISO first column did not parse. Got: %s" % sorted(plan))
    if len(plan) != 3:
        fail("expected 3 dated rows, got %d. The decoy settings table was probably "
             "read as a plan." % len(plan))
    row = plan["2026-01-05"]
    for lane in ("EMT", "Math", "CS"):
        if lane not in row:
            fail("lane %s missing from the parsed row: %s" % (lane, row))
    if "Mandarin" in row:
        fail("Mandarin is not a column in the fixture and must not be invented")


def check_floor():
    if itembank.day_status(set(itembank.FLOOR_LANES)) != "floor":
        fail("the floor lanes alone did not produce a floor day")
    if itembank.day_status(set(itembank.DAY_LANES)) != "full":
        fail("every lane did not produce a full day")
    if itembank.day_status({"CS", "Mandarin"}) != "miss":
        fail("a day missing the floor lanes did not count as a miss")


def check_streak_ignores_unfinished_today():
    from datetime import date, timedelta
    today = date(2026, 1, 7)
    log = {"2026-01-05": set(itembank.DAY_LANES),
           "2026-01-06": set(itembank.FLOOR_LANES),
           "2026-01-07": set()}                       # today, not started yet
    if itembank.day_streak(log, today) != 2:
        fail("an unstarted today broke the streak; got %d, expected 2"
             % itembank.day_streak(log, today))


def check_server():
    log_path = os.path.join(tempfile.mkdtemp(), "daily_log.md")
    proc = subprocess.Popen(
        [sys.executable, "-u", os.path.join(ROOT, "itembank.py"), "day", PLAN,
         "--no-open", "--port", "0", "--log", log_path, "--date", "2026-01-06"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    lines = []
    threading.Thread(target=lambda: [lines.append(l) for l in proc.stdout],
                     daemon=True).start()

    url = None
    for _ in range(60):
        time.sleep(0.1)
        m = re.search(r"http://127\.0\.0\.1:\d+/", "".join(lines))
        if m:
            url = m.group(0)
            break
    if not url:
        proc.kill()
        fail("server never printed a URL. Output was:\n" + "".join(lines))

    try:
        page = urllib.request.urlopen(url, timeout=5).read().decode("utf-8")
        if "ch 2 first half" not in page:
            fail("the served page did not contain the plan's EMT task for that date")

        body = json.dumps({"date": "2026-01-06",
                           "done": list(itembank.FLOOR_LANES)}).encode("utf-8")
        req = urllib.request.Request(url + "save", data=body,
                                     headers={"Content-Type": "application/json"})
        got = json.loads(urllib.request.urlopen(req, timeout=5).read().decode("utf-8"))
        if got.get("status") != "floor":
            fail("posting the floor lanes returned status %r, expected 'floor'" % got.get("status"))
        if got.get("streak") != 1:
            fail("streak after one floor day was %r, expected 1" % got.get("streak"))
    finally:
        proc.kill()

    if not os.path.exists(log_path):
        fail("no log file was written; a tick was lost")
    written = itembank.load_day_log(log_path)
    if written.get("2026-01-06") != set(itembank.FLOOR_LANES):
        fail("the log did not round-trip. Read back: %r" % written)


def main():
    check_parser()
    check_floor()
    check_streak_ignores_unfinished_today()
    check_server()
    print("PASS: plan parsed, floor honored, ticks round-tripped to disk")


if __name__ == "__main__":
    main()
