#!/usr/bin/env python3
"""Retention UI (10-05): Today, cap recovery, and the longitudinal report.

Fixtures over the Today page and the `/report` markup, all driven through
the real daemon with synthetic evidence in a temp dir (fixtures/_evidence
is never touched):

- Today with one due objective: owner-labelled itembank signal, state
  chip, raw counts, `Why this recommendation` disclosure, `Start focused
  session`, and one snapshot id on card/disclosure/boot.
- Sparse/unknown evidence renders the exact `Not enough evidence yet`
  copy and ordinary practice stays available.
- Anki closed renders the exact locked copy and never alters the itembank
  snapshot/recommendation.
- At cap, the exact cap-block copy plus recovery and the one-sitting
  override dialog (exact title/buttons); the page itself writes nothing.
- Focused start carries the displayed snapshot claim; a forged/stale claim
  is rejected and writes no session.
- POST /api/lesson-complete: explicit completion appends one event,
  duplicates reconcile, unknown refs are refused, and merely viewing the
  lesson page writes nothing.
- GET /report renders the retention overview/drilldown with the same
  snapshot id and counts as `itembank trends`, allowlisted weeks, and no
  answer/key/path leakage.

Standard library only, runnable as `python tests/retention_ui_roundtrip.py`.
"""
import datetime, json, os, re, shutil, subprocess, sys, tempfile, threading, time
import urllib.error, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import evidence                                            # noqa: E402
from surfaces import session                                # noqa: E402

SEL_BANK = os.path.join(ROOT, "fixtures", "selection_bank.md")
LESSON_BANK = os.path.join(ROOT, "fixtures", "lesson_bank.md")

CAP_BLOCK_COPY = ("Today\u2019s {subject} cap is reached "
                  "({count} of {cap} ordinary attempts).")
ANKI_UNAVAILABLE = "Anki is unavailable; card counts are not shown."
NO_EVIDENCE_COPY = "Not enough evidence yet"


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def namespaced_response_event(session_id, objective, ts, score=True,
                              item_ref=None, bank="selection_bank.md"):
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
        "bank": bank,
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
                                          "B" if score is not None
                                          else "short:x"),
        "source_ref": None,
    }


def today_ts(dt, hour, minute=0):
    return datetime.datetime(dt.year, dt.month, dt.day, hour, minute,
                             tzinfo=datetime.timezone.utc
                             ).strftime("%Y-%m-%dT%H:%M:%S.000Z")


DAEMON_LINES = []


def start_daemon(workdir):
    proc = subprocess.Popen(
        [sys.executable, "-u", os.path.join(ROOT, "itembank.py"), "daemon",
         workdir, "--no-open", "--port", "0"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    DAEMON_LINES[:] = []
    threading.Thread(
        target=lambda: [DAEMON_LINES.append(l) for l in proc.stdout],
        daemon=True).start()
    url = None
    for _ in range(100):
        time.sleep(0.1)
        m = re.search(r"http://127\.0\.0\.1:\d+/", "".join(DAEMON_LINES))
        if m:
            url = m.group(0)
            break
    if not url:
        proc.terminate()
        fail("daemon never printed a URL. Output was:\n" + "".join(DAEMON_LINES))
    return proc, url, DAEMON_LINES


def get(url, timeout=60):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as res:
            return res.status, res.read().decode("utf-8")
    except urllib.error.HTTPError:
        raise                       # expected 4xx; no daemon diagnostic needed
    except Exception as exc:
        print("DAEMON OUT:\n" + "".join(DAEMON_LINES[-60:]))
        raise


def post(url, payload, timeout=60):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as res:
        return json.loads(res.read().decode("utf-8"))


def json_request(url, payload, timeout=60):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            return res.status, json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        try:
            return exc.code, json.loads(raw.decode("utf-8"))
        except ValueError:
            return exc.code, raw.decode("utf-8", errors="replace")


def day_boot(page):
    m = re.search(r"window\.__day__=(\{.*?\});\n", page, re.S)
    if not m:
        return None
    return json.loads(m.group(1))


def write_evidence(tmp, events):
    evdir = os.path.join(tmp, "_evidence")
    os.makedirs(evdir, exist_ok=True)
    with open(os.path.join(evdir, "evidence.jsonl"), "a",
              encoding="utf-8") as fh:
        for ev in events:
            fh.write(json.dumps(ev, sort_keys=True) + "\n")
    return os.path.join(evdir, "evidence.jsonl")


def prepare(extra_banks=(), daily_cap=40, lanes_deck=None, evidence=()):
    """A temp daemon root with a today-dated plan, the requested banks, an
    optional lanes deck, a settings file, and synthetic evidence."""
    tmp = tempfile.mkdtemp()
    today = datetime.date.today()
    iso = today.isoformat()
    with open(os.path.join(tmp, "plan.md"), "w", encoding="utf-8") as fh:
        fh.write("# plan\n\n"
                 "| Date | EMT | Math | CS | Linux | Mandarin | Anki |\n"
                 "|---|---|---|---|---|---|---|\n"
                 "| %s | water practice | sets | | | | |\n" % iso)
    shutil.copy(SEL_BANK, os.path.join(tmp, "selection_bank.md"))
    for src, name in extra_banks:
        shutil.copy(src, os.path.join(tmp, name))
    if lanes_deck:
        with open(os.path.join(tmp, "lanes.md"), "w", encoding="utf-8") as fh:
            fh.write("# lanes\n\n"
                     "| Lane | Anki deck | Notes file | Notes glob | Fuse | "
                     "Fuse date |\n|---|---|---|---|---|---|\n"
                     "| EMT | %s | | | | |\n" % lanes_deck)
    with open(os.path.join(tmp, "itembank.json"), "w", encoding="utf-8") as fh:
        json.dump({"daily_cap": daily_cap}, fh)
    if evidence:
        write_evidence(tmp, evidence)
    return tmp, today, iso


def check_today_due_and_focused_start():
    """One due objective renders owner/state/counts/disclosure and a
    focused start that carries the displayed snapshot claim (10-05 Task 1,
    D-01/D-04/D-10)."""
    today = datetime.date.today()
    evs = [namespaced_response_event("s1", "water:distribution.residual",
                                     today_ts(today, 8), score=True,
                                     item_ref="R1"),
           namespaced_response_event("s1", "water:distribution.residual",
                                     today_ts(today, 9), score=False,
                                     item_ref="R2"),
           namespaced_response_event("s1", "water:distribution.residual",
                                     today_ts(today, 10), score=False,
                                     item_ref="R3")]
    tmp, today, iso = prepare(evidence=evs)
    proc, url, lines = start_daemon(tmp)
    try:
        status, page = get(url + "day/plan")
        if status != 200:
            fail("GET /day/plan returned %d" % status)
        boot = day_boot(page)
        today_payload = (boot or {}).get("today") or {}
        claim = today_payload.get("claim") or {}
        sid = claim.get("snapshot_id") or ""
        if not sid:
            fail("the Today boot carries no snapshot claim")
        objs = today_payload.get("objectives") or []
        if len(objs) != 1 or objs[0]["objective"] != "water:distribution.residual":
            fail("Today should recommend exactly the weak/due residual "
                 "objective: %r" % objs)
        if objs[0]["state"] != "weak":
            fail("1/3 settled is weak, got %r" % objs[0]["state"])
        # Markup: owner label, state chip, raw counts, disclosure, action.
        if "itembank" not in page or "objective(s) recommended" not in page:
            fail("the Today page is missing the owner-labelled itembank signal")
        if "Start focused session" not in page:
            fail("the Today page is missing the focused-session action")
        if "Why this recommendation" not in page:
            fail("the Today page is missing the evidence disclosure")
        if "weak" not in page or "3 attempt(s), 3 settled" not in page:
            fail("the Today card is missing the state chip or raw counts")
        # The 10-04 pacing block shows the real configured cap (40 here),
        # never a guessed number.
        if "3 of 40 ordinary attempts today" not in page:
            fail("the pacing block is missing the configured 3/40 count")
        # Same snapshot id on the stamp and the boot claim.
        if 'data-snapshot="%s"' % sid not in page:
            fail("the card/disclosure snapshot marker does not match the boot")

        # Focused start carries the displayed claim: accepted, session
        # binding server-derived, and the same counts as the display.
        status, result = json_request(
            url + "api/start",
            {"bank": "selection_bank", "count": 10,
             "objective": "water:distribution.residual",
             "snapshot": claim})
        if status != 200:
            fail("focused start with the displayed snapshot was refused: "
                 "HTTP %d %r" % (status, result))
        if result.get("status") != "active":
            fail("focused start did not produce an active session")
        binding = result.get("cap") or {}
        if binding.get("subject") != "water" or binding.get("count") != 3:
            fail("the session cap binding must be server-derived 3/cap: %r"
                 % binding)
    finally:
        proc.terminate()
    shutil.rmtree(tmp, ignore_errors=True)
    print("  Today due card: owner/state/counts/disclosure + snapshot "
          "linkage + focused start")


def check_today_unknown_and_stale():
    """Sparse evidence shows the exact unknown copy and practice stays
    available; a forged/stale snapshot claim is rejected with no session
    (10-05 Task 1, D-03/D-04/T-10-19)."""
    tmp, today, iso = prepare(evidence=())
    proc, url, lines = start_daemon(tmp)
    try:
        status, page = get(url + "day/plan")
        if status != 200:
            fail("GET /day/plan returned %d" % status)
        if NO_EVIDENCE_COPY not in page:
            fail("sparse Today is missing the exact not-enough-evidence copy")
        if "objective(s) recommended" in page:
            fail("sparse Today must not claim a recommendation")
        boot = day_boot(page)
        claim = ((boot or {}).get("today") or {}).get("claim") or {}
        # A forged claim is rejected as stale and writes no session.
        attempts_dir = os.path.join(tmp, "_attempts")
        before = set(os.listdir(attempts_dir)) \
            if os.path.isdir(attempts_dir) else set()
        status, body = json_request(
            url + "api/start",
            {"bank": "selection_bank", "count": 10,
             "objective": "water:distribution.residual",
             "snapshot": {"snapshot_id": "forged"}})
        if status != 400 or "stale" not in str(body).lower():
            fail("a forged snapshot claim must be rejected as stale: "
                 "HTTP %d %r" % (status, body))
        after = set(os.listdir(attempts_dir)) \
            if os.path.isdir(attempts_dir) else set()
        if after != before:
            fail("a stale-snapshot start wrote a session file")
        # Ordinary practice (no snapshot claim) still works below cap.
        status, result = json_request(
            url + "api/start",
            {"bank": "selection_bank", "count": 2,
             "objective": "water:distribution.residual"})
        if status != 200:
            fail("ordinary practice below cap was refused: HTTP %d %r"
                 % (status, result))
    finally:
        proc.terminate()
    shutil.rmtree(tmp, ignore_errors=True)
    print("  sparse Today: exact unknown copy, forged-claim rejection, "
          "practice available")


def check_today_anki_separation():
    """Anki closed renders the exact locked copy on Today and never alters
    the itembank snapshot/recommendation (10-05 Task 1, D-05)."""
    today = datetime.date.today()
    evs = [namespaced_response_event("s1", "water:distribution.residual",
                                     today_ts(today, 8), score=True,
                                     item_ref="R1"),
           namespaced_response_event("s1", "water:distribution.residual",
                                     today_ts(today, 9), score=False,
                                     item_ref="R2"),
           namespaced_response_event("s1", "water:distribution.residual",
                                     today_ts(today, 10), score=False,
                                     item_ref="R3")]
    tmp, today, iso = prepare(lanes_deck="EMT", evidence=evs)
    proc, url, lines = start_daemon(tmp)
    try:
        status, page = get(url + "day/plan")
        if status != 200:
            fail("GET /day/plan returned %d" % status)
        if ANKI_UNAVAILABLE not in page:
            fail("Anki closed must render the exact locked copy on Today")
        if "Anki: 0 due" in page:
            fail("Anki failure must not render as a zero-looking count")
        boot = day_boot(page)
        today_payload = (boot or {}).get("today") or {}
        objs = today_payload.get("objectives") or []
        if not objs or objs[0]["objective"] != "water:distribution.residual":
            fail("Anki state must not change the itembank recommendation")
    finally:
        proc.terminate()
    shutil.rmtree(tmp, ignore_errors=True)
    print("  Today Anki separation: locked copy, recommendation unaffected")


def check_cap_recovery_and_override_dialog():
    """At cap the exact block copy plus recovery and the one-sitting
    override dialog render; the page itself writes nothing (10-05 Task 2,
    D-07/D-08)."""
    today = datetime.date.today()
    evs = [namespaced_response_event("s1", "water:distribution.residual",
                                     today_ts(today, 8 + i), score=True,
                                     item_ref="R%d" % (100 + i))
           for i in range(2)]
    tmp, today, iso = prepare(daily_cap=2, evidence=evs)
    proc, url, lines = start_daemon(tmp)
    try:
        status, page = get(url + "day/plan")
        if status != 200:
            fail("GET /day/plan returned %d" % status)
        if CAP_BLOCK_COPY.format(subject="water", count=2, cap=2) not in page:
            fail("the exact at-cap block copy is missing from Today")
        if "Review evidence" not in page or \
                "Request one-sitting override" not in page:
            fail("at-cap recovery options are missing")
        if "Start one additional water sitting?" not in page:
            fail("the override dialog title is missing")
        if "Start one additional sitting" not in page or \
                "Keep today\u2019s cap" not in page:
            fail("the override dialog buttons are missing")
        # Rendering writes no cap_override event.
        log = evidence.log_path(tmp)
        overrides = [ev for ev in evidence.live_events(log)
                     if ev.get("event_type") == evidence.CAP_OVERRIDE_EVENT_TYPE]
        if overrides:
            fail("rendering Today must not append a cap_override event")
    finally:
        proc.terminate()
    shutil.rmtree(tmp, ignore_errors=True)
    print("  at-cap Today: locked copy, recovery, override dialog, no write")


def check_lesson_complete_route():
    """POST /api/lesson-complete appends exactly one event for a
    server-resolved heading; duplicates reconcile; unknown refs are
    refused; viewing the lesson page writes nothing (10-05 Task 2,
    SCHED-04/D-24)."""
    tmp, today, iso = prepare(extra_banks=[(LESSON_BANK, "lesson_bank.md")])
    proc, url, lines = start_daemon(tmp)
    try:
        log = evidence.log_path(tmp)
        # Viewing writes nothing.
        status, page = get(url + "lesson/lesson_bank")
        if status != 200:
            fail("GET /lesson/lesson_bank returned %d" % status)
        before = [ev for ev in evidence.live_events(log)
                  if ev.get("event_type") == evidence.LESSON_COMPLETE_EVENT_TYPE]
        if before:
            fail("merely opening the lesson page wrote a completion event")

        # Today offers the explicit completion affordance for the bank's
        # server-resolved headings.
        status, day_page = get(url + "day/plan")
        if status != 200:
            fail("GET /day/plan returned %d" % status)
        if 'data-bank="lesson_bank"' not in day_page or \
                "Mark lesson complete" not in day_page:
            fail("Today is missing the lesson-complete affordance")

        # Unknown heading refused.
        status, body = json_request(
            url + "api/lesson-complete",
            {"bank": "lesson_bank", "ref": "no such heading"})
        if status != 400:
            fail("unknown lesson ref must be refused: HTTP %d %r"
                 % (status, body))

        # Explicit completion appends exactly one event.
        status, body = json_request(
            url + "api/lesson-complete",
            {"bank": "lesson_bank", "ref": "The Airway, Step By Step"})
        if status != 200:
            fail("lesson completion was refused: HTTP %d %r" % (status, body))
        if body.get("status") != "recorded":
            fail("lesson completion status is %r" % body.get("status"))
        if body.get("subject") != "emt" or \
                body.get("objectives") != ["emt:airway"]:
            fail("lesson completion must name the single emt:airway "
                 "objective set: %r" % body)
        events = [ev for ev in evidence.live_events(log)
                  if ev.get("event_type") == evidence.LESSON_COMPLETE_EVENT_TYPE]
        if len(events) != 1:
            fail("expected exactly one lesson_complete event, found %d"
                 % len(events))

        # Duplicate completion reconciles (already_recorded), appends nothing.
        status, body = json_request(
            url + "api/lesson-complete",
            {"bank": "lesson_bank", "ref": "The Airway, Step By Step"})
        if status != 200 or body.get("status") != "already_recorded":
            fail("duplicate completion must reconcile: HTTP %d %r"
                 % (status, body))
        events = [ev for ev in evidence.live_events(log)
                  if ev.get("event_type") == evidence.LESSON_COMPLETE_EVENT_TYPE]
        if len(events) != 1:
            fail("duplicate completion appended a second event")
    finally:
        proc.terminate()
    shutil.rmtree(tmp, ignore_errors=True)
    print("  lesson-complete route: one event, reconcile, refusal, "
          "read-only view")


def check_report_drilldown_parity():
    """GET /report (no session) renders the retention overview/drilldown
    from the same payload as `itembank trends`, with allowlisted weeks and
    no answer/key/path leakage (10-05 Task 3, D-15)."""
    today = datetime.date.today()
    evs = [namespaced_response_event("s1", "water:distribution.residual",
                                     today_ts(today, 8), score=True,
                                     item_ref="R1"),
           namespaced_response_event("s1", "water:distribution.residual",
                                     today_ts(today, 9), score=False,
                                     item_ref="R2"),
           namespaced_response_event("s1", "water:distribution.residual",
                                     today_ts(today, 10), score=False,
                                     item_ref="R3")]
    tmp, today, iso = prepare(evidence=evs)
    proc, url, lines = start_daemon(tmp)
    try:
        status, page = get(url + "report")
        if status != 200:
            fail("GET /report returned %d" % status)
        m = re.search(r'class="stamp" data-snapshot="([^"]+)" data-cutoff="([^"]*)"',
                      page)
        if not m:
            fail("the report page carries no snapshot stamp")
        page_sid, page_cutoff = m.group(1), m.group(2)
        # Pin the CLI capture to the page's own cutoff so the two derive
        # the identical snapshot (the id hashes the cutoff timestamp).
        cli = subprocess.run(
            [sys.executable, "-u", os.path.join(ROOT, "itembank.py"),
             "trends", "--base", tmp, "--json", "--cutoff", page_cutoff],
            capture_output=True, text=True, timeout=120)
        if cli.returncode != 0:
            fail("itembank trends --json failed: %s" % cli.stderr[-500:])
        payload = json.loads(cli.stdout)
        claim = payload["claim"]
        if claim["snapshot_id"] != page_sid:
            fail("the report page snapshot %r != CLI payload snapshot %r"
                 % (page_sid, claim["snapshot_id"]))
        if "Snapshot %s" % claim["snapshot_id"][:8] not in page:
            fail("the report page stamp does not show the CLI snapshot")
        if str(payload["overview"]["attempts"]) not in page:
            fail("the report page is missing the CLI payload's raw attempt "
                 "count")
        if "return rate" not in page.lower():
            fail("the report page is missing the stated-denominator return "
                 "rate")
        # Answer material must never appear.
        for leak in ("CORRECT", "WHY BEST", "correct option", "=>",
                     tmp, "itembank.py"):
            if leak in page:
                fail("the report page leaked %r" % leak)
        # Drilldown: subject, then objective.
        status, subj_page = get(url + "report?subject=water&weeks=4")
        if status != 200 or "Subject water" not in subj_page:
            fail("subject drilldown failed: HTTP %d" % status)
        obj = "water:distribution.residual"
        status, obj_page = get(
            url + "report?subject=water&objective=" +
            urllib.parse.quote(obj) + "&weeks=4")
        if status != 200 or obj not in obj_page:
            fail("objective drilldown failed: HTTP %d" % status)
        if "highest hint" not in obj_page.lower():
            fail("objective detail is missing the hint field")
        # Weeks allowlist: an out-of-range window is refused, not guessed.
        try:
            get(url + "report?weeks=3")
            fail("weeks=3 must be refused by the allowlist")
        except urllib.error.HTTPError as exc:
            if exc.code != 400:
                fail("weeks=3 returned HTTP %d, expected 400" % exc.code)
    finally:
        proc.terminate()
    shutil.rmtree(tmp, ignore_errors=True)
    print("  /report: CLI payload parity, subject/objective drilldown, "
          "public boundary")


def main():
    print("retention_ui_roundtrip:")
    check_today_due_and_focused_start()
    check_today_unknown_and_stale()
    check_today_anki_separation()
    check_cap_recovery_and_override_dialog()
    check_lesson_complete_route()
    check_report_drilldown_parity()
    print("retention_ui_roundtrip: ok")


if __name__ == "__main__":
    main()
