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
import json, os, re, shutil, subprocess, sys, tempfile, threading, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAN = os.path.join(ROOT, "fixtures", "sample_plan.md")
sys.path.insert(0, ROOT)
import itembank


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def cap_ts(hour, minute=0):
    """A UTC timestamp inside the pacing counter's current local day.

    The counter's local day comes from the snapshot zone, which defaults to
    UTC; building the stamp from `datetime.date.today()` instead used the
    *machine's* local date, so west of Greenwich after 18:00 the seeded
    evidence landed on the previous counted day and every ordinary-attempt
    count came back 0. Same fix pacing_roundtrip already carries.
    """
    import datetime as _dt
    d = _dt.datetime.now(_dt.timezone.utc).date()
    return _dt.datetime(d.year, d.month, d.day, hour, minute,
                        tzinfo=_dt.timezone.utc
                        ).strftime("%Y-%m-%dT%H:%M:%S.000Z")


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

    # `itembank day` is now a daemon launch scoped to one plan (plan 02-02):
    # the printed URL already names `/day/<stem>`, but this regex only
    # needs the base -- the cockpit page itself is scraped explicitly below,
    # and its save target is plan-scoped (`/day/<stem>/save`), not the bare
    # `/save` a single-plan process used to hardcode.
    stem = os.path.splitext(os.path.basename(PLAN))[0]
    base = None
    for _ in range(60):
        time.sleep(0.1)
        m = re.search(r"http://127\.0\.0\.1:\d+/", "".join(lines))
        if m:
            base = m.group(0)
            break
    if not base:
        proc.kill()
        fail("server never printed a URL. Output was:\n" + "".join(lines))
    day_url = base + "day/%s" % stem

    try:
        # The cold render walks the plan, git evidence and (10-04) the
        # evidence snapshot; under heavy parallel-agent load on a /mnt/c
        # mount this can take far longer than the old 5s, so the timeout is
        # generous -- the assertion is about correctness, not speed.
        page = urllib.request.urlopen(day_url, timeout=60).read().decode("utf-8")
        if "ch 2 first half" not in page:
            fail("the served page did not contain the plan's EMT task for that date")

        body = json.dumps({"date": "2026-01-06",
                           "done": list(itembank.FLOOR_LANES)}).encode("utf-8")
        req = urllib.request.Request(day_url + "/save", data=body,
                                     headers={"Content-Type": "application/json"})
        got = json.loads(urllib.request.urlopen(req, timeout=60).read().decode("utf-8"))
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


def namespaced_response(session_id, objective, ts, score=True, item_ref=None):
    """One synthetic namespaced response event for the 10-04 pacing corpus,
    mirroring evidence.response_event's shape."""
    import evidence
    item_ref = item_ref or ("Q" + evidence.new_event_id()[:8])
    return {
        "schema_version": evidence.EVENT_SCHEMA_VERSION,
        "event_id": evidence.new_event_id(),
        "event_type": "response",
        "ts": ts,
        "session_id": session_id,
        "item_id": "",
        "item_ref": item_ref,
        "item_type": "short" if score is None else "mc",
        "bank": "plan_bank.md",
        "objective": objective,
        "subject": evidence.subject_of(objective),
        "mode": "practice",
        "attempt_number": 1,
        "answer": "x" if score is None else "B",
        "canonical": "B" if score is not None else "short:x",
        "score": score,
        "response_time_ms": 1000,
        "confidence": None,
        "error_category": None,
        "hint_tier": None,
        "selection_mode": "practice",
        "review_state": "pending" if score is None else "n/a",
        "dedupe_key": evidence.dedupe_key(session_id, item_ref, 1,
                                          "B" if score is not None else "short:x"),
        "source_ref": None,
    }


def write_evidence(tmp, events):
    evdir = os.path.join(tmp, "_evidence")
    os.makedirs(evdir, exist_ok=True)
    with open(os.path.join(evdir, "evidence.jsonl"), "a", encoding="utf-8") as fh:
        for ev in events:
            fh.write(json.dumps(ev, sort_keys=True) + "\n")
    return os.path.join(evdir, "evidence.jsonl")


def check_pacing_check_output():
    """`itembank day PLAN --check` reports each configured subject's
    ordinary count/cap and due objective count from ONE snapshot, then the
    separate owner-labelled Anki line -- and the exact locked copy when Anki
    is unavailable (10-04 Task 2, D-01/D-05/D-07)."""
    import datetime
    from datetime import timezone
    tmp = tempfile.mkdtemp()
    try:
        today = datetime.date.today()
        iso = today.isoformat()
        plan = os.path.join(tmp, "plan.md")
        with open(plan, "w", encoding="utf-8") as fh:
            fh.write("# plan\n\n"
                     "| Date | EMT | Math | CS | Linux | Mandarin | Anki |\n"
                     "|---|---|---|---|---|---|---|\n"
                     "| %s | water practice | sets | | | | |\n" % iso)
        with open(os.path.join(tmp, "lanes.md"), "w", encoding="utf-8") as fh:
            fh.write("# lanes\n\n"
                     "| Lane | Anki deck | Notes file | Notes glob | Fuse | Fuse date |\n"
                     "|---|---|---|---|---|---|\n"
                     "| EMT | EMT | | | | |\n")
        with open(os.path.join(tmp, "itembank.json"), "w", encoding="utf-8") as fh:
            json.dump({"daily_cap": 4}, fh)
        ts = cap_ts
        # water:distribution.residual: 3 settled (1 correct -> weak, due),
        # water:notify: 1 pending (counts toward pacing, never correctness).
        write_evidence(tmp, [
            namespaced_response("s1", "water:distribution.residual", ts(8),
                                score=True, item_ref="R1"),
            namespaced_response("s1", "water:distribution.residual", ts(9),
                                score=False, item_ref="R2"),
            namespaced_response("s1", "water:distribution.residual", ts(10),
                                score=False, item_ref="R3"),
            namespaced_response("s1", "water:notify", ts(11),
                                score=None, item_ref="P1"),
        ])
        proc = subprocess.run(
            [sys.executable, "-u", os.path.join(ROOT, "itembank.py"), "day",
             plan, "--check", "--date", iso],
            capture_output=True, text=True, timeout=120)
        out = proc.stdout + proc.stderr
        if proc.returncode != 0:
            fail("day --check exited %d: %s" % (proc.returncode, out[-900:]))
        # 3 settled + 1 pending = 4 ordinary attempts today, cap 4.
        if "water: 4 of 4 ordinary attempts today" not in out:
            fail("day --check did not report water's ordinary count/cap "
                 "from the snapshot: %r" % out[-900:])
        if "1 due objective" not in out:
            fail("day --check did not report the due objective count "
                 "(residual is weak after 1/3): %r" % out[-900:])
        if "itembank snapshot" not in out:
            fail("day --check did not print the snapshot marker: %r" % out[-900:])
        if "Anki is unavailable; card counts are not shown." not in out:
            fail("day --check with Anki closed did not print the exact locked "
                 "copy: %r" % out[-900:])
        if "Anki:" in out:
            fail("Anki closed must not render a stale/zero-looking count line")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("  day --check: snapshot-derived count/cap, due count, locked Anki copy")


def check_anki_owner_and_states():
    """Anki is an optional read-only external signal: populated, zero, and
    unavailable states change ONLY the Anki line -- never the pacing
    numbers, snapshot id, or recommendation (10-04 Task 2, D-05/SCHED-03).
    Zero is a real read and renders; a failure renders the exact locked
    copy instead of a stale count."""
    import datetime
    from datetime import timezone
    from surfaces import day as day_mod
    tmp = tempfile.mkdtemp()
    try:
        today = datetime.date.today()
        iso = today.isoformat()
        plan = os.path.join(tmp, "plan.md")
        with open(plan, "w", encoding="utf-8") as fh:
            fh.write("# plan\n\n"
                     "| Date | EMT | Math | CS | Linux | Mandarin | Anki |\n"
                     "|---|---|---|---|---|---|---|\n"
                     "| %s | water practice | sets | | | | |\n" % iso)
        lanes = os.path.join(tmp, "lanes.md")
        with open(lanes, "w", encoding="utf-8") as fh:
            fh.write("# lanes\n\n"
                     "| Lane | Anki deck | Notes file | Notes glob | Fuse | Fuse date |\n"
                     "|---|---|---|---|---|---|\n"
                     "| EMT | EMT | | | | |\n")
        ts = cap_ts
        write_evidence(tmp, [
            namespaced_response("s1", "water:distribution.residual", ts(8),
                                score=True, item_ref="R1"),
            namespaced_response("s1", "water:distribution.residual", ts(9),
                                score=False, item_ref="R2"),
            namespaced_response("s1", "water:distribution.residual", ts(10),
                                score=False, item_ref="R3"),
        ])
        log_path = os.path.join(tmp, "daily_log.md")
        state = day_mod.day_state(plan, log_path, lanes, iso)
        cfg = {"daily_cap": 4}
        pacing = day_mod.day_pacing(state, cfg)
        snap_id = pacing["claim"]["snapshot_id"]
        water = pacing["subjects"]["water"]
        baseline = (water["count"], water["cap"], water["due"])

        def info_with_anki(anki_result):
            orig = day_mod.anki_read
            day_mod.anki_read = lambda decks: anki_result
            try:
                info = day_mod.day_info(state["plan"], state["log"], iso,
                                        plan, lanes)
            finally:
                day_mod.anki_read = orig
            info["pacing"] = day_mod.day_pacing(state, cfg)
            return info

        def pacing_numbers(pacing_dict):
            w = pacing_dict["subjects"]["water"]
            return (w["count"], w["cap"], w["due"],
                    bool(pacing_dict["claim"].get("snapshot_id")))

        populated = info_with_anki(({"EMT": (3, 2)}, ["EMT"]))
        text = day_mod.day_text(iso, today.strftime("%A"), state["plan"].get(iso, {}),
                                state["log"], day_mod.day_streak(state["log"], state["today"]),
                                populated)
        if "Anki: 3 due · 2 new" not in text:
            fail("populated Anki counts did not render owner-labelled: %r" % text)
        if pacing_numbers(populated["pacing"]) != (baseline[0], baseline[1],
                                                   baseline[2], True):
            fail("Anki counts changed the itembank pacing numbers/snapshot")

        zero = info_with_anki(({"EMT": (0, 0)}, ["EMT"]))
        text0 = day_mod.day_text(iso, today.strftime("%A"), state["plan"].get(iso, {}),
                                 state["log"], day_mod.day_streak(state["log"], state["today"]),
                                 zero)
        if "Anki: 0 due · 0 new" not in text0:
            fail("a genuine zero Anki read did not render: %r" % text0)

        closed = info_with_anki((None, None))
        textc = day_mod.day_text(iso, today.strftime("%A"), state["plan"].get(iso, {}),
                                 state["log"], day_mod.day_streak(state["log"], state["today"]),
                                 closed)
        if "Anki is unavailable; card counts are not shown." not in textc:
            fail("Anki closed did not render the exact locked copy: %r" % textc)
        if "Anki: 0 due" in textc:
            fail("Anki failure must not render as a zero-looking count")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("  Anki: populated/zero/unavailable only touch the labelled Anki line")


def check_no_anki_write_methods():
    """D-05/SCHED-03: day.py holds NO Anki write path -- only the two
    read-only AnkiConnect actions (deckNames, findCards)."""
    src = open(os.path.join(ROOT, "surfaces", "day.py"), encoding="utf-8").read()
    import re as _re
    calls = _re.findall(r"_anki_post\(\s*[^,]+,\s*\"([^\"]+)\"", src)
    if not calls:
        fail("expected to find the read-only AnkiConnect calls")
    for action in calls:
        if action not in ("deckNames", "findCards"):
            fail("day.py issues an Anki action that is not a read: %r" % action)
    print("  day.py Anki surface is read-only: only deckNames/findCards")


def check_local_day_recut():
    """After a recorded response, `day` captures again: the new pacing shows
    the incremented count and a NEW snapshot id, while the already-rendered
    payload dict keeps its old internally-consistent values (10-04 Task 2,
    TREND-02/D-01)."""
    import datetime
    from datetime import timezone
    from surfaces import day as day_mod
    tmp = tempfile.mkdtemp()
    try:
        today = datetime.date.today()
        iso = today.isoformat()
        plan = os.path.join(tmp, "plan.md")
        with open(plan, "w", encoding="utf-8") as fh:
            fh.write("# plan\n\n"
                     "| Date | EMT | Math | CS | Linux | Mandarin | Anki |\n"
                     "|---|---|---|---|---|---|---|\n"
                     "| %s | water practice | sets | | | | |\n" % iso)
        ts = cap_ts
        write_evidence(tmp, [
            namespaced_response("s1", "water:distribution.residual", ts(8),
                                score=True, item_ref="R1"),
        ])
        log_path = os.path.join(tmp, "daily_log.md")
        state = day_mod.day_state(plan, log_path, None, iso)
        cfg = {"daily_cap": 4}
        first = day_mod.day_pacing(state, cfg)
        c1 = first["subjects"]["water"]["count"]
        s1 = first["claim"]["snapshot_id"]
        # A second recorded response lands after the first render.
        write_evidence(tmp, [
            namespaced_response("s2", "water:distribution.residual", ts(9),
                                score=False, item_ref="R2"),
        ])
        second = day_mod.day_pacing(state, cfg)
        if second["subjects"]["water"]["count"] != c1 + 1:
            fail("re-cut did not pick up the new response: %d -> %d"
                 % (c1, second["subjects"]["water"]["count"]))
        if second["claim"]["snapshot_id"] == s1:
            fail("re-cut must mint a new snapshot id for the new capture")
        # The old payload is a materialized dict: still internally consistent.
        if first["subjects"]["water"]["count"] != c1:
            fail("the already-rendered payload changed under the new capture")
        if first["claim"]["snapshot_id"] != s1:
            fail("the already-rendered payload's snapshot marker changed")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("  day re-cuts from one fresh snapshot after a live event; old payload stable")


def check_day_composes_one_shell():
    """Plan 17A-02: the day route composes `presentation.surface_shell` rather
    than assembling a second document, and its content survives the move.

    Parity, not appearance, is what is asserted here. `day.py` was the one
    served route that owned its own doctype, so it carried neither the shared
    token layer nor a single vendored face. The migration is only worth
    anything if every section, id and boot payload the day JS binds to came
    through unchanged, so both halves are checked in one place: the shell is
    present exactly once, and every part of the route is still there.
    """
    from surfaces import day as day_mod, presentation, theme
    hist = [{"status": "full", "date": "2026-08-23"},
            {"status": "miss", "date": "2026-08-22"}]
    row = {"EMT": "water practice", "Math": "sets"}
    html_out = day_mod.day_page("2026-08-24", "Monday", row, {}, 3, hist,
                                "plan.md", theme_css=theme.THEME_CSS)

    for marker, why in ((("<!doctype html>"), "one doctype"),
                        ("<h1>", "one h1"),
                        ("<main>", "one main landmark")):
        if html_out.count(marker) != 1:
            fail("day emits %d of %s; the shell must own exactly %s"
                 % (html_out.count(marker), marker, why))
    if '<div class="surface"' not in html_out:
        fail("day is not inside the shared surface wrapper, so it did not go "
             "through presentation.surface_shell")
    if presentation.SHARED_CSS not in html_out:
        fail("the day document does not carry SHARED_CSS verbatim; a served "
             "route outside the token layer is what 17A-02 exists to end")
    faces = html_out.count("src:url(\"/assets/fonts/")
    if faces != 4:
        fail("day declares %d of the 4 vendored faces; before this migration "
             "it declared none" % faces)

    # The tab keeps the date while the heading keeps the weekday. That split
    # predates the migration and a shell that collapsed them would be a
    # silent content change.
    if "<title>2026-08-24</title>" not in html_out:
        fail("the day document title is no longer the date")
    if "<h1>Monday</h1>" not in html_out:
        fail("the day heading is no longer the weekday")

    # Every id and section the day JS binds to, plus the boot payload.
    for hook in ("id=streak", "id=streakword", "id=hist", "id=verdict",
                 "class=sub", "class=bar", "class=note",
                 "window.__day__=", "Plan read from"):
        if hook not in html_out:
            fail("the migrated day page lost %r; route content must be "
                 "unchanged by a shell migration" % hook)
    for lane in day_mod.DAY_LANES:
        if lane not in html_out:
            fail("the migrated day page lost the %s lane" % lane)
    if html_out.rstrip().index("window.__day__=") < html_out.index("</main>"):
        fail("the boot script moved inside main; it belongs after the "
             "landmark, where it was")
    print("  day composes one shared shell: token layer, 4 faces, content parity")


def main():
    check_parser()
    check_day_composes_one_shell()
    check_floor()
    check_streak_ignores_unfinished_today()
    check_server()
    check_pacing_check_output()
    check_anki_owner_and_states()
    check_no_anki_write_methods()
    check_local_day_recut()
    print("PASS: plan parsed, floor honored, ticks round-tripped to disk, "
          "snapshot pacing, owner-labelled Anki, read-only Anki, local-day recut")


if __name__ == "__main__":
    main()
