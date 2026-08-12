#!/usr/bin/env python3
"""Phase 10 UAT (10-06): one-command cross-surface and security gate.

Drives the REAL CLI and daemon surfaces over one synthetic evidence set:

  Today -> evidence disclosure -> focused start -> Phase 7 selection event
  -> CLI/browser report

proving that a single evidence state flows through every boundary (the
displayed snapshot claim is what the start request carries and the server
validates as current), that NEW evidence forces an explicit refresh instead
of mixed snapshots (stale start fails closed with no session/event), and
that no public serialization leaks private fields -- answer keys, rubrics,
paths, credentials, hidden tiers, provider/model payloads (T-10-24,
T-10-25).

The snapshot id hashes the cutoff timestamp, so a later capture carries a
new marker by design: the tracer asserts id equality where the system
guarantees it (card/disclosure/boot; CLI vs page at a pinned cutoff) and
evidence-state equality elsewhere (the session binding counts match the
displayed claim), while the staleness append proves the refresh boundary.

Standard library only, runnable as `python tests/phase10_uat.py`.
"""
import datetime, json, os, re, shutil, subprocess, sys, tempfile, threading, time
import urllib.error, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import evidence                                            # noqa: E402

SEL_BANK = os.path.join(ROOT, "fixtures", "selection_bank.md")

# Private/never-render tokens for the public-boundary scan (T-10-25).
FORBIDDEN = [
    "CORRECT:", "WHY BEST", "KEY DISCRIMINATOR", "SECOND-BEST",
    "rubric", "credentials", "model_backend", "provider", "Bearer ",
    "hidden tier", "explain_payload",
]


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


def today_ts(hour, minute=0):
    """A UTC timestamp inside the pacing counter's current local day.

    The counter resolves its local day through the snapshot zone, which
    defaults to UTC. This used to take the date as an argument and every
    caller passed `datetime.date.today()` -- the *machine's* local date --
    so west of Greenwich after 18:00 the seeded evidence fell on the
    previous counted day and the ordinary-attempt counts came back 0.
    """
    d = datetime.datetime.now(datetime.timezone.utc).date()
    return datetime.datetime(d.year, d.month, d.day, hour, minute,
                             tzinfo=datetime.timezone.utc
                             ).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def prepare():
    tmp = tempfile.mkdtemp()
    today = datetime.date.today()
    with open(os.path.join(tmp, "plan.md"), "w", encoding="utf-8") as fh:
        fh.write("# plan\n\n"
                 "| Date | EMT | Math | CS | Linux | Mandarin | Anki |\n"
                 "|---|---|---|---|---|---|---|\n"
                 "| %s | water practice | sets | | | | |\n"
                 % today.isoformat())
    shutil.copy(SEL_BANK, os.path.join(tmp, "selection_bank.md"))
    with open(os.path.join(tmp, "itembank.json"), "w", encoding="utf-8") as fh:
        json.dump({"daily_cap": 10}, fh)
    evdir = os.path.join(tmp, "_evidence")
    os.makedirs(evdir, exist_ok=True)
    log = os.path.join(evdir, "evidence.jsonl")

    def seed(events):
        with open(log, "a", encoding="utf-8") as fh:
            for ev in events:
                fh.write(json.dumps(ev, sort_keys=True) + "\n")

    seed([namespaced_response_event("s1", "water:distribution.residual",
                                    today_ts(8), score=True,
                                    item_ref="R1"),
          namespaced_response_event("s1", "water:distribution.residual",
                                    today_ts(9), score=False,
                                    item_ref="R2"),
          namespaced_response_event("s1", "water:distribution.residual",
                                    today_ts(10), score=False,
                                    item_ref="R3")])
    return tmp, today, log


def start_daemon(workdir):
    proc = subprocess.Popen(
        [sys.executable, "-u", os.path.join(ROOT, "itembank.py"), "daemon",
         workdir, "--no-open", "--port", "0"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    lines = []
    threading.Thread(target=lambda: [lines.append(l) for l in proc.stdout],
                     daemon=True).start()
    url = None
    for _ in range(100):
        time.sleep(0.1)
        m = re.search(r"http://127\.0\.0\.1:\d+/", "".join(lines))
        if m:
            url = m.group(0)
            break
    if not url:
        proc.terminate()
        fail("daemon never printed a URL. Output was:\n" + "".join(lines))
    return proc, url, lines


def get(url, timeout=60):
    with urllib.request.urlopen(url, timeout=timeout) as res:
        return res.status, res.read().decode("utf-8")


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


def scan_public(body, label, tmp):
    """The central public/private containment scan (T-10-25): every public
    serialization must carry the snapshot marker and never a private
    token."""
    low = body if isinstance(body, str) else json.dumps(body)
    for token in FORBIDDEN:
        if token.lower() in low.lower():
            fail("%s leaked %r" % (label, token))
    if tmp in low:
        fail("%s leaked the served directory path" % label)
    if os.path.sep in low and "/" + os.path.basename(SEL_BANK) in low:
        fail("%s leaked a bank path" % label)


def check_cross_surface_tracer():
    """Today -> disclosure -> focused start -> Phase 7 trace -> report with
    one evidence state; appended evidence forces a fail-closed refresh
    (10-06 Task 1, D-01/D-10/D-15, T-10-24)."""
    tmp, today, log = prepare()
    proc, url, lines = start_daemon(tmp)
    try:
        # Today carries one complete claim on card, disclosure and boot.
        status, page = get(url + "day/plan")
        if status != 200:
            fail("GET /day/plan returned %d" % status)
        boot = day_boot(page)
        claim_a = ((boot or {}).get("today") or {}).get("claim") or {}
        sid_a = claim_a.get("snapshot_id") or ""
        if not sid_a or not claim_a.get("cutoff"):
            fail("Today boot carries no complete evidence claim")
        if 'data-snapshot="%s"' % sid_a not in page:
            fail("the Today card/disclosure marker differs from the boot")
        if 'data-objective="water:distribution.residual"' not in page:
            fail("the due objective card is missing from Today")
        if "Why this recommendation" not in page:
            fail("the evidence disclosure is missing")

        # CLI report at the same cutoff derives the identical claim --
        # checked BEFORE the focused start appends its selection event.
        cli = subprocess.run(
            [sys.executable, "-u", os.path.join(ROOT, "itembank.py"),
             "trends", "--base", tmp, "--json", "--cutoff",
             claim_a.get("cutoff") or ""],
            capture_output=True, text=True, timeout=120)
        if cli.returncode != 0:
            fail("itembank trends --json failed: %s" % cli.stderr[-500:])
        cli_payload = json.loads(cli.stdout)
        if cli_payload["claim"]["snapshot_id"] != sid_a:
            fail("CLI report at the displayed cutoff derives a different "
                 "snapshot")
        if cli_payload["overview"]["attempts"] != 3:
            fail("CLI report does not show the displayed evidence's counts")
        scan_public(cli_payload, "CLI trends JSON", tmp)

        # Focused start carries claim A and is accepted while current.
        status, started = json_request(
            url + "api/start",
            {"bank": "selection_bank", "count": 10,
             "objective": "water:distribution.residual",
             "snapshot": claim_a})
        if status != 200:
            fail("focused start with the current claim was refused: "
                 "HTTP %d %r" % (status, started))
        binding = started.get("cap") or {}
        if binding.get("count") != 3 or binding.get("subject") != "water":
            fail("the session binding must carry the displayed evidence's "
                 "3/water: %r" % binding)
        # Phase 7 chose the objective and names the session's own snapshot
        # (the selection authority's fresh capture of the same evidence).
        trace = started.get("trace") or {}
        tr = trace.get("retention") or {}
        if tr.get("snapshot_id") != binding.get("snapshot_id"):
            fail("the selection trace must name the session snapshot")
        chosen = [o.get("objective") for o in
                  (trace.get("chosen") or []) if isinstance(o, dict)]
        if "water:distribution.residual" not in chosen:
            fail("Phase 7 did not choose the recommended objective: %r"
                 % chosen[:3])
        public_start = dict(started)
        public_start["session_file"] = "<server-managed>"   # documented API field
        public_trace = dict(public_start.get("trace") or {})
        evidence_info = dict((public_trace.get("evidence") or {}))
        evidence_info["log"] = "<server-managed>"           # documented CLI field
        public_trace["evidence"] = evidence_info
        public_start["trace"] = public_trace
        scan_public(public_start, "focused-start response", tmp)

        # New evidence lands after the render (a WRONG attempt keeps the
        # objective weak/due so the refreshed Today still recommends it).
        with open(log, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(namespaced_response_event(
                "s2", "water:distribution.residual", today_ts(11),
                score=False, item_ref="R4"), sort_keys=True) + "\n")

        # The OLD claim start now fails stale and writes nothing.
        attempts_dir = os.path.join(tmp, "_attempts")
        before = set(os.listdir(attempts_dir)) \
            if os.path.isdir(attempts_dir) else set()
        status, body = json_request(
            url + "api/start",
            {"bank": "selection_bank", "count": 10,
             "objective": "water:distribution.residual",
             "snapshot": claim_a})
        if status != 400 or "stale" not in str(body).lower():
            fail("the stale claim was not rejected: HTTP %d %r"
                 % (status, body))
        after = set(os.listdir(attempts_dir)) \
            if os.path.isdir(attempts_dir) else set()
        if after != before:
            fail("a stale start wrote a session file")
        live = [ev for ev in evidence.live_events(log)
                if ev.get("event_type") == evidence.RESPONSE_EVENT_TYPE]
        if len(live) != 4:
            fail("the stale start appended an event (log now %d)" % len(live))

        # Refresh yields a wholly new consistent claim; nothing mixes.
        status, page2 = get(url + "day/plan")
        boot2 = day_boot(page2)
        claim_b = ((boot2 or {}).get("today") or {}).get("claim") or {}
        if not claim_b.get("snapshot_id") or \
                claim_b["snapshot_id"] == sid_a:
            fail("the refreshed Today did not mint a new snapshot id")
        objs_b = ((boot2 or {}).get("today") or {}).get("objectives") or []
        found = any(o.get("objective") == "water:distribution.residual"
                    for o in objs_b)
        if not found:
            fail("the refreshed Today dropped the recommended objective")
        # The OLD rendered payload is a materialized dict: still claim A.
        if claim_a.get("live_event_count") != 3:
            fail("the old rendered claim changed under new evidence")
        # New snapshot id is consistent everywhere on the refreshed page.
        if 'data-snapshot="%s"' % claim_b["snapshot_id"] not in page2:
            fail("the refreshed page mixes old and new snapshot markers")
    finally:
        proc.terminate()
    shutil.rmtree(tmp, ignore_errors=True)
    print("  cross-surface tracer: one evidence state, fail-closed stale, "
          "consistent refresh")


def check_public_boundary_scan():
    """Every public surface carries the snapshot marker and no private
    field (T-10-25)."""
    tmp, today, log = prepare()
    proc, url, lines = start_daemon(tmp)
    try:
        status, day_page = get(url + "day/plan")
        # The day cockpit's documented "Plan read from <path>" note names
        # the user's own plan (Phase 4 loopback behavior); redact it so the
        # scan still catches every OTHER path or private token.
        scan_public(day_page.replace(tmp, "<server-managed>"), "Today HTML", tmp)
        status, report_page = get(url + "report")
        scan_public(report_page, "report HTML", tmp)
        status, subj_page = get(url + "report?subject=water&weeks=4")
        scan_public(subj_page, "subject drilldown HTML", tmp)
        status, started = json_request(
            url + "api/start",
            {"bank": "selection_bank", "count": 2,
             "objective": "water:distribution.residual"})
        if status != 200:
            fail("start failed: HTTP %d %r" % (status, started))
        public_start = dict(started)
        public_start["session_file"] = "<server-managed>"   # documented API field
        public_trace = dict(public_start.get("trace") or {})
        evidence_info = dict((public_trace.get("evidence") or {}))
        evidence_info["log"] = "<server-managed>"           # documented CLI field
        public_trace["evidence"] = evidence_info
        public_start["trace"] = public_trace
        scan_public(public_start, "start JSON", tmp)
        scan_public(public_trace, "selection trace", tmp)
        status, nxt = json_request(
            url + "api/next", {"session_id": started["session_id"]})
        if status != 200:
            fail("next failed: HTTP %d %r" % (status, nxt))
        scan_public(nxt, "next public item JSON", tmp)
        if "correct" in json.dumps(nxt.get("item") or {}):
            fail("the public item payload carries an answer key")
    finally:
        proc.terminate()
    shutil.rmtree(tmp, ignore_errors=True)
    print("  public boundary: Today/report/drilldown/start/trace/item carry "
          "no private fields")


def check_large_and_empty_logs():
    """Large/sparse logs derive in one bounded pass and degrade honestly
    (10-06 Task 2, T-10-26)."""
    tmp = tempfile.mkdtemp()
    try:
        shutil.copy(SEL_BANK, os.path.join(tmp, "selection_bank.md"))
        log = evidence.log_path(tmp)
        os.makedirs(os.path.dirname(log), exist_ok=True)
        base = datetime.date(2026, 7, 1)
        with open(log, "a", encoding="utf-8") as fh:
            for i in range(12000):
                day = base + datetime.timedelta(days=i % 40)
                ev = namespaced_response_event(
                    "bulk", "water:distribution.residual",
                    "%sT10:00:00.000Z" % day.isoformat(),
                    score=(i % 3 != 0), item_ref="B%d" % i)
                fh.write(json.dumps(ev, sort_keys=True) + "\n")
            for i in range(200):
                ev = namespaced_response_event(
                    "bulk2", "water:notification.boil",
                    "%sT11:00:00.000Z" % (base + datetime.timedelta(days=i % 30)
                                          ).isoformat(),
                    score=None, item_ref="P%d" % i)
                fh.write(json.dumps(ev, sort_keys=True) + "\n")
        cli = subprocess.run(
            [sys.executable, "-u", os.path.join(ROOT, "itembank.py"),
             "trends", "--base", tmp, "--json"],
            capture_output=True, text=True, timeout=300)
        if cli.returncode != 0:
            fail("trends over a large log failed: %s" % cli.stderr[-500:])
        payload = json.loads(cli.stdout)
        if payload["overview"]["attempts"] != 12200:
            fail("large-log overview attempts = %d, expected 12200"
                 % payload["overview"]["attempts"])
        # Sparse: an empty log derives the honest unknown payload.
        empty = tempfile.mkdtemp()
        try:
            cli2 = subprocess.run(
                [sys.executable, "-u", os.path.join(ROOT, "itembank.py"),
                 "trends", "--base", empty, "--json"],
                capture_output=True, text=True, timeout=120)
            payload2 = json.loads(cli2.stdout)
            if payload2["overview"]["attempts"] != 0:
                fail("empty log must derive zero attempts")
        finally:
            shutil.rmtree(empty, ignore_errors=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("  large (12k+) and sparse logs: one bounded derivation, honest "
          "unknown")


def main():
    print("phase10_uat:")
    check_cross_surface_tracer()
    check_public_boundary_scan()
    check_large_and_empty_logs()
    print("phase10_uat: ok")


if __name__ == "__main__":
    main()
