#!/usr/bin/env python3
"""Assert that the consolidated daemon behaves as one process on one port
should, and never as two processes wearing one port number.

The failure this guards against is silent by construction: a daemon that
looks fine per-route while cross-contaminating banks, letting a filename
shadow a fixed route, serving the answer key, or losing its route-to-CLI
inventory would pass a glance at any single endpoint and only show up the
moment two banks, or a stem collision, or an unknown identifier, is tried
against the same running process. Every check below tries exactly one of
those things.

Standard library only, no test framework, runnable as
`python tests/daemon_roundtrip.py`.
"""
import json, os, re, shutil, socketserver, subprocess, sys, tempfile, threading, time
import urllib.error, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import itembank                                            # noqa: E402
import evidence                                             # noqa: E402
from surfaces import cli, daemon, study                    # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agent_roundtrip                                       # noqa: E402
import serve_roundtrip                                      # noqa: E402

BANK = os.path.join(ROOT, "fixtures", "sample_bank.md")
PLAN = os.path.join(ROOT, "fixtures", "sample_plan.md")


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def start_daemon(workdir, *extra_args):
    """Launch `itembank daemon <workdir> --no-open --port 0`, drain its
    stdout on a background thread, and return `(proc, url, lines)` once the
    printed banner's URL has been scraped -- the same subprocess-plus-
    background-thread shape `tests/serve_roundtrip.py` and
    `tests/day_roundtrip.py` already use, generalized to a daemon that can
    be pointed at any prepared directory. Exported at module level so later
    plans in this phase (02-02, 02-04, 02-05, 02-06) can import or copy it.
    """
    proc = subprocess.Popen(
        [sys.executable, "-u", os.path.join(ROOT, "itembank.py"), "daemon", workdir,
         "--no-open", "--port", "0"] + list(extra_args),
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    lines = []
    threading.Thread(target=lambda: [lines.append(l) for l in proc.stdout],
                     daemon=True).start()
    url = None
    for _ in range(60):                        # up to ~6s for the bind and banner
        time.sleep(0.1)
        m = re.search(r"http://127\.0\.0\.1:\d+/", "".join(lines))
        if m:
            url = m.group(0)
            break
    if not url:
        proc.terminate()
        fail("daemon never printed a URL. Output was:\n" + "".join(lines))
    return proc, url, lines


def get(url):
    with urllib.request.urlopen(url, timeout=5) as res:
        return res.status, res.read().decode("utf-8")


def post(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=5) as res:
        return json.loads(res.read().decode("utf-8"))


def served_post_path(quiz_url, page):
    """The answer-POST target the served page's own script carries, resolved
    against the page's URL -- reading this off the page rather than
    assuming the `/quiz/<stem>/answer` convention is what gives the
    isolation and answer-scoring checks below actual teeth against the
    `__POST__` substitution: an unsubstituted placeholder resolves to a
    path nothing serves, and posting there fails loudly instead of the
    check silently posting to a URL it guessed.
    """
    m = re.search(r'fetch\("([^"]+)"', page)
    if not m:
        fail("could not find the answer-POST target in the served page")
    return urllib.parse.urljoin(quiz_url, m.group(1))


def write_today_plan(path, emt_task="synthetic EMT task for today"):
    """A one-row plan dated to the real "today", since the daemon's day
    routes always resolve `iso` from `datetime.date.today()` -- there is no
    `--date` override on `itembank daemon` (unlike `itembank day --date`,
    which `tests/day_roundtrip.py` uses instead). Returns the ISO date
    written, for tests that need to POST against it.
    """
    from datetime import date
    iso = date.today().isoformat()
    text = ("# plan\n\n"
            "| Date | EMT (top priority) | Math, ~25 min | CS + other |\n"
            "|---|---|---|---|\n"
            "| %s | %s | Ch 1 sets, problems 1-6 | Build: hello world |\n"
            % (iso, emt_task))
    open(path, "w", encoding="utf-8").write(text)
    return iso


def check_index_populated():
    workdir = tempfile.mkdtemp()
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    shutil.copy(PLAN, os.path.join(workdir, "sample_plan.md"))
    proc, url, lines = start_daemon(workdir)
    try:
        status, body = get(url)
        if status != 200:
            fail("GET / returned %d, expected 200" % status)
        for needle in ("sample_bank", "sample_plan", "Sit this bank",
                       "Study this bank", "Open day view",
                       "/quiz/sample_bank", "/study/sample_bank"):
            if needle not in body:
                fail("populated index missing %r" % needle)
    finally:
        proc.terminate()


def check_index_order():
    workdir = tempfile.mkdtemp()
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    shutil.copy(BANK, os.path.join(workdir, "alpha_bank.md"))
    order = None
    for attempt in range(2):                  # two restarts over the same directory
        proc, url, lines = start_daemon(workdir)
        try:
            _, body = get(url)
            a, b = body.find("alpha_bank"), body.find("sample_bank")
            if a < 0 or b < 0:
                fail("index is missing one of the two bank stems")
            this_order = a < b
            if not this_order:
                fail("alpha_bank did not sort before sample_bank in case-insensitive "
                     "stem order")
            if order is not None and this_order != order:
                fail("index order changed between two restarts over the same directory")
            order = this_order
        finally:
            proc.terminate()


def check_index_empty():
    workdir = tempfile.mkdtemp()
    proc, url, lines = start_daemon(workdir)
    try:
        status, body = get(url)
        if status != 200:
            fail("an empty directory's GET / returned %d, expected 200" % status)
        if "Nothing to serve here yet" not in body:
            fail("empty-directory index is missing the documented empty-state heading")
    finally:
        proc.terminate()


def check_index_malformed_tolerated():
    workdir = tempfile.mkdtemp()
    open(os.path.join(workdir, "notjunk.md"), "w", encoding="utf-8").write(
        "# Just some notes\n\nNothing structured here -- not a bank, not a dated plan.\n")
    proc, url, lines = start_daemon(workdir)
    try:
        status, body = get(url)
        if status != 200:
            fail("a directory holding only a malformed .md file did not return 200")
        if "notjunk" in body:
            fail("a file that is neither a bank nor a plan appeared in the index")
    finally:
        proc.terminate()


def check_index_no_truncation():
    workdir = tempfile.mkdtemp()
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    proc, url, lines = start_daemon(workdir)
    try:
        _, body = get(url)
        low = body.lower()
        if "nowrap" in low:
            fail("index stylesheet declares a nowrap rule; row link text must wrap")
        if "ellipsis" in low:
            fail("index stylesheet declares an ellipsis truncation rule")
    finally:
        proc.terminate()


def check_quiz_no_key():
    workdir = tempfile.mkdtemp()
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    proc, url, lines = start_daemon(workdir)
    try:
        _, page = get(url + "quiz/sample_bank")
        qs = itembank.parse_bank(open(BANK, encoding="utf-8").read())
        serve_roundtrip.check_no_key(page, qs)
    finally:
        proc.terminate()


def check_answer_scoring():
    workdir = tempfile.mkdtemp()
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    proc, url, lines = start_daemon(workdir)
    try:
        qs = itembank.parse_bank(open(BANK, encoding="utf-8").read())
        quiz_url = url + "quiz/sample_bank"
        _, page = get(quiz_url)
        answer_url = served_post_path(quiz_url, page)
        first = qs[0]
        bad = post(answer_url,
                   {"id": first["id"], "response": serve_roundtrip.wrong_answer(first)})
        if bad["score"] is not False:
            fail("a wrong answer scored %r, expected False" % bad["score"])
        if not bad["explain"].get("why"):
            fail("the verdict carried no explanation")
        for q in qs:
            got = post(answer_url,
                       {"id": q["id"], "response": serve_roundtrip.correct_answer(q)})
            want = None if q["type"] == "short" else True
            if got["score"] is not want:
                fail("item %s (%s) scored %r, expected %r"
                     % (q["id"], q["type"], got["score"], want))
    finally:
        proc.terminate()


def check_two_bank_isolation():
    """The Pitfall #1 regression guard: an answer posted to one bank's path
    must never land in another bank's attempt file or evidence event, even
    though both banks share one evidence log in this directory.
    """
    workdir = tempfile.mkdtemp()
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    shutil.copy(BANK, os.path.join(workdir, "alpha_bank.md"))
    proc, url, lines = start_daemon(workdir)
    try:
        qs = itembank.parse_bank(open(BANK, encoding="utf-8").read())
        quiz_url = url + "quiz/alpha_bank"
        _, page = get(quiz_url)
        answer_url = served_post_path(quiz_url, page)
        if "alpha_bank" not in answer_url:
            fail("alpha_bank's served page posts its answer to %r, which is not "
                 "scoped to alpha_bank" % answer_url)
        first = qs[0]
        post(answer_url,
             {"id": first["id"], "response": serve_roundtrip.correct_answer(first)})

        log = evidence.log_path(workdir)
        responses = [ev for ev in evidence.live_events(log) if ev.get("event_type") == "response"]
        if not responses:
            fail("posting to alpha_bank's answer path recorded no response event at all")
        if any(ev["bank"] != "alpha_bank.md" for ev in responses):
            fail("an answer posted to alpha_bank recorded against a different bank: %r"
                 % [ev["bank"] for ev in responses])

        attempts_dir = os.path.join(workdir, "_attempts")
        sample_attempts = [f for f in os.listdir(attempts_dir)
                           if f.startswith("sample_bank_attempt_")] \
            if os.path.isdir(attempts_dir) else []
        for name in sample_attempts:
            text = open(os.path.join(attempts_dir, name), encoding="utf-8").read()
            if "[auto: correct]" in text or "[auto: WRONG]" in text:
                fail("sample_bank's attempt file gained a recorded answer from a "
                     "post made to alpha_bank")
    finally:
        proc.terminate()


def check_stem_collision():
    workdir = tempfile.mkdtemp()
    os.makedirs(os.path.join(workdir, "a"))
    os.makedirs(os.path.join(workdir, "b"))
    a_path = os.path.join(workdir, "a", "notes_bank.md")
    b_path = os.path.join(workdir, "b", "notes_bank.md")
    shutil.copy(BANK, a_path)
    shutil.copy(BANK, b_path)
    proc, url, lines = start_daemon(workdir)
    try:
        status, _ = get(url + "quiz/notes_bank")
        if status != 200:
            fail("the colliding stem was not reachable at /quiz/notes_bank at all")
        output = "".join(lines)
        if a_path not in output or b_path not in output:
            fail("startup output did not name both colliding paths:\n" + output)
        if "loses" not in output.lower() and "collision" not in output.lower():
            fail("startup output did not name the losing file:\n" + output)
    finally:
        proc.terminate()


def check_fixed_routes_not_shadowed():
    workdir = tempfile.mkdtemp()
    shutil.copy(BANK, os.path.join(workdir, "report.md"))
    shutil.copy(BANK, os.path.join(workdir, "api.md"))
    proc, url, lines = start_daemon(workdir)
    try:
        status, _ = get(url + "quiz/report")
        if status != 200:
            fail("a bank whose stem is 'report' was shadowed by a fixed route")
        status, body = get(url + "__itembank__")
        if status != 200:
            fail("GET /__itembank__ returned %d, expected 200" % status)
        data = json.loads(body)
        if data != {"itembank": True}:
            fail("the marker route returned %r, expected {'itembank': true}" % data)
    finally:
        proc.terminate()


def check_unknown_stem():
    workdir = tempfile.mkdtemp()
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    proc, url, lines = start_daemon(workdir)
    try:
        try:
            get(url + "quiz/no-such-bank")
            fail("an unknown stem did not return a 404")
        except urllib.error.HTTPError as exc:
            if exc.code != 404:
                fail("an unknown stem returned HTTP %d, expected 404" % exc.code)
            body = exc.read().decode("utf-8")
            if workdir in body or "Traceback" in body:
                fail("the 404 body leaked the served directory or a traceback")
            if "Not found" not in body:
                fail("the 404 body is missing the documented not-found copy")
    finally:
        proc.terminate()


def check_concurrency():
    """Two overlapping requests must both complete -- `Daemon` mixes in
    `socketserver.ThreadingMixIn`, checked here both structurally (the
    import-time assertion) and behaviourally (several concurrent requests
    that must all resolve rather than serialize behind one another).
    """
    if not issubclass(daemon.Daemon, socketserver.ThreadingMixIn):
        fail("daemon.Daemon does not mix in socketserver.ThreadingMixIn")

    workdir = tempfile.mkdtemp()
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    proc, url, lines = start_daemon(workdir)
    try:
        results = {}

        def hit(key):
            try:
                status, _ = get(url + "quiz/sample_bank")
                results[key] = status
            except Exception as exc:                # noqa: BLE001 -- recorded, not raised
                results[key] = exc

        threads = [threading.Thread(target=hit, args=(i,)) for i in range(6)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10)
        if any(t.is_alive() for t in threads):
            fail("a concurrent request against the daemon never completed")
        for key, value in results.items():
            if value != 200:
                fail("concurrent request %s did not return 200: %r" % (key, value))
    finally:
        proc.terminate()


def check_study_route():
    """`GET /study/<stem>` renders through `study.study_page()`, byte for
    byte -- no second copy of the study template lives in `daemon.py`.
    """
    workdir = tempfile.mkdtemp()
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    proc, url, lines = start_daemon(workdir)
    try:
        status, page = get(url + "study/sample_bank")
        if status != 200:
            fail("GET /study/<stem> returned %d, expected 200" % status)
        qs = itembank.parse_bank(open(BANK, encoding="utf-8").read())
        want = study.study_page(BANK, qs)
        if page != want:
            fail("the served study page differs from study.study_page()'s own return "
                 "value for the same bank")
        try:
            get(url + "study/no-such-bank")
            fail("an unknown study stem did not return a 404")
        except urllib.error.HTTPError as exc:
            if exc.code != 404:
                fail("an unknown study stem returned HTTP %d, expected 404" % exc.code)
    finally:
        proc.terminate()


def check_study_cmd_matches_study_page():
    """`study_page()` and `cmd_study()` must render from one substitution
    chain (D-08 extended to the study surface): the file `cmd_study` writes
    to disk must equal `study_page()`'s own return value for the same bank.
    """
    import argparse
    qs = itembank.parse_bank(open(BANK, encoding="utf-8").read())
    want = study.study_page(BANK, qs)
    out = os.path.join(tempfile.mkdtemp(), "study.html")
    study.cmd_study(argparse.Namespace(bank=BANK, out=out, force=False))
    got = open(out, encoding="utf-8").read()
    if got != want:
        fail("cmd_study's written file differs from study.study_page()'s own return "
             "value for the same bank")


def check_day_route():
    workdir = tempfile.mkdtemp()
    write_today_plan(os.path.join(workdir, "sample_plan.md"), "ch 2 first half")
    proc, url, lines = start_daemon(workdir)
    try:
        status, page = get(url + "day/sample_plan")
        if status != 200:
            fail("GET /day/<stem> returned %d, expected 200" % status)
        if "ch 2 first half" not in page:
            fail("the served day page is missing today's plan task text")
        try:
            get(url + "day/no-such-plan")
            fail("an unknown day stem did not return a 404")
        except urllib.error.HTTPError as exc:
            if exc.code != 404:
                fail("an unknown day stem returned HTTP %d, expected 404" % exc.code)
    finally:
        proc.terminate()


def check_day_index_single_plan():
    """`GET /day` with exactly one scanned plan serves that plan."""
    workdir = tempfile.mkdtemp()
    write_today_plan(os.path.join(workdir, "sample_plan.md"), "single-plan task text")
    proc, url, lines = start_daemon(workdir)
    try:
        status, page = get(url + "day")
        if status != 200:
            fail("GET /day with exactly one scanned plan returned %d, expected 200" % status)
        if "single-plan task text" not in page:
            fail("GET /day did not serve the sole scanned plan's page")
    finally:
        proc.terminate()


def check_day_index_ambiguous():
    """`GET /day` with zero or with two-or-more scanned plans returns 404
    carrying the documented not-found copy and no filesystem path.
    """
    workdir = tempfile.mkdtemp()
    proc, url, lines = start_daemon(workdir)
    try:
        try:
            get(url + "day")
            fail("GET /day with zero scanned plans did not return a 404")
        except urllib.error.HTTPError as exc:
            if exc.code != 404:
                fail("GET /day with zero plans returned HTTP %d, expected 404" % exc.code)
            if "Not found" not in exc.read().decode("utf-8"):
                fail("GET /day's zero-plan 404 body is missing the documented not-found copy")
    finally:
        proc.terminate()

    workdir = tempfile.mkdtemp()
    os.makedirs(os.path.join(workdir, "a"))
    os.makedirs(os.path.join(workdir, "b"))
    write_today_plan(os.path.join(workdir, "a", "plan_a.md"))
    write_today_plan(os.path.join(workdir, "b", "plan_b.md"))
    proc, url, lines = start_daemon(workdir)
    try:
        try:
            get(url + "day")
            fail("GET /day with two scanned plans did not return a 404")
        except urllib.error.HTTPError as exc:
            if exc.code != 404:
                fail("GET /day with two plans returned HTTP %d, expected 404" % exc.code)
            body = exc.read().decode("utf-8")
            if "Not found" not in body:
                fail("GET /day's ambiguous 404 body is missing the documented not-found copy")
            if workdir in body:
                fail("GET /day's ambiguous 404 body leaked a filesystem path")
    finally:
        proc.terminate()


def check_day_save_and_isolation():
    """POST /day/<stem>/save writes that plan's own daily_log.md, and a save
    against one plan leaves a second plan's log file untouched (T-2-12).
    """
    workdir = tempfile.mkdtemp()
    os.makedirs(os.path.join(workdir, "a"))
    os.makedirs(os.path.join(workdir, "b"))
    iso = write_today_plan(os.path.join(workdir, "a", "plan_a.md"))
    write_today_plan(os.path.join(workdir, "b", "plan_b.md"))
    proc, url, lines = start_daemon(workdir)
    try:
        got = post(url + "day/plan_a/save",
                   {"date": iso, "done": list(itembank.FLOOR_LANES)})
        if got.get("status") != "floor":
            fail("POST /day/plan_a/save returned status %r, expected 'floor'"
                 % got.get("status"))
        if got.get("streak") != 1:
            fail("POST /day/plan_a/save returned streak %r, expected 1" % got.get("streak"))
        if "hist" not in got:
            fail("POST /day/plan_a/save did not return a hist field")

        log_a = os.path.join(workdir, "a", "daily_log.md")
        log_b = os.path.join(workdir, "b", "daily_log.md")
        if not os.path.exists(log_a):
            fail("saving against plan_a did not write plan_a's own daily_log.md")
        if os.path.exists(log_b):
            fail("saving against plan_a wrote a daily_log.md for plan_b, which was "
                 "never posted to")
    finally:
        proc.terminate()


def check_day_open_out_of_range():
    """An out-of-range `(lane, index)` on `POST /day/<stem>/open` is a 404
    that opens nothing (T-2-10).
    """
    workdir = tempfile.mkdtemp()
    write_today_plan(os.path.join(workdir, "sample_plan.md"))
    proc, url, lines = start_daemon(workdir)
    try:
        get(url + "day/sample_plan")           # prime the per-plan day_state
        try:
            post(url + "day/sample_plan/open", {"lane": "EMT", "i": 5})
            fail("an out-of-range open index did not return a 404")
        except urllib.error.HTTPError as exc:
            if exc.code != 404:
                fail("an out-of-range open index returned HTTP %d, expected 404" % exc.code)
    finally:
        proc.terminate()


def check_route_cli_inventory():
    """SURF-04: every route has a CLI equivalent, checked as an inventory
    rather than trusted as a claim in prose.
    """
    if set(daemon.ROUTE_CLI) != set(e[:2] for e in daemon.ROUTES):
        fail("ROUTE_CLI's key set does not match ROUTES -- a route is missing its "
             "CLI equivalent, or ROUTE_CLI carries a stale one")
    import inspect
    src = inspect.getsource(cli)
    for name in set(daemon.ROUTE_CLI.values()):
        if ('add_parser("%s"' % name) not in src and ("add_parser('%s'" % name) not in src:
            fail("CLI command %r named in ROUTE_CLI has no add_parser registration in "
                 "surfaces/cli.py" % name)


def check_api_route_scope():
    """D-04 scopes `/api/*` to exactly four routes this phase, and the count
    is asserted rather than trusted.
    """
    if len(daemon.API_ROUTES) != 4:
        fail("D-04 scopes /api/* to exactly four routes this phase; API_ROUTES has "
             "%d" % len(daemon.API_ROUTES))
    if not {"start", "next", "submit", "report"} <= set(daemon.ROUTE_CLI.values()):
        fail("ROUTE_CLI is missing one of the four session CLI commands")


def snapshot_dirs(root):
    """Every directory under `root`, as absolute paths -- used to prove a
    hostile request created nothing on disk.
    """
    found = set()
    for dirpath, dirnames, _ in os.walk(root):
        for d in dirnames:
            found.add(os.path.join(dirpath, d))
    return found


def api_by_id(bank=BANK):
    """`{item_id: full_bank_item}` for `bank`, so a check can look up the
    real `q` dict (with `correct`/`rows`/`steps`) behind an `/api/*`
    response's stripped-down public item payload.
    """
    qs = itembank.parse_bank(open(bank, encoding="utf-8").read())
    return {q["id"]: q for q in qs}


def api_correct_answer(by_id, item):
    """The correct response for an `/api/*` public item payload, resolved
    through the full bank item -- `agent_roundtrip.answer_for()` only
    guarantees a validly-SHAPED answer, not a correct one (a `dnd`/
    `table`/`build` item's first listed category or step order is not
    necessarily its key).
    """
    return serve_roundtrip.correct_answer(by_id[item["id"]])


def check_api_sitting():
    """The happy path: `/api/start` -> `/api/next` -> `/api/submit` ->
    `/api/report`, each printing the same shape the CLI does, over the
    exact same runtime calls (SURF-04, SURF-01).
    """
    workdir = tempfile.mkdtemp()
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    proc, url, lines = start_daemon(workdir)
    try:
        started = post(url + "api/start",
                       {"bank": "sample_bank", "count": 6, "seed": 7, "mode": "practice"})
        if started["status"] != "active":
            fail("POST /api/start did not return an active session")
        if "correct" in started["item"]:
            fail("POST /api/start's item payload carries an answer key")
        session_id = started["session_id"]

        nxt = post(url + "api/next", {"session_id": session_id})
        if "item" not in nxt:
            fail("POST /api/next did not return the current item")

        answer = api_correct_answer(api_by_id(), nxt["item"])
        submitted = post(url + "api/submit", {"session_id": session_id, "answer": answer})
        if submitted["accepted"] is not True:
            fail("POST /api/submit did not accept a valid response")
        if submitted["score"] is not True:
            fail("POST /api/submit against the correct answer scored %r, expected True"
                 % submitted["score"])
        if submitted["evidence"]["status"] != "recorded":
            fail("POST /api/submit's response was not recorded: %r" % submitted["evidence"])

        report = post(url + "api/report", {"session_id": session_id})
        if report["session_id"] != session_id:
            fail("POST /api/report returned a different session_id than it was asked for")
        if report["summary"]["auto_attempts"] < 1:
            fail("POST /api/report's summary shows no auto_attempts after one submit")
    finally:
        proc.terminate()


def check_api_duplicate_submit_dedupes():
    """Submitting the same answer twice for the same item -- simulating a
    client retry after a crash between the evidence append and the
    session write (D-17) -- returns `evidence.status` `already_recorded`
    the second time, matching the CLI (`tests/evidence_roundtrip.py`'s own
    dedupe test proves the CLI half of this).
    """
    workdir = tempfile.mkdtemp()
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    proc, url, lines = start_daemon(workdir)
    try:
        started = post(url + "api/start", {"bank": "sample_bank", "count": 1, "seed": 0})
        session_id = started["session_id"]
        session_file = started["session_file"]
        answer = api_correct_answer(api_by_id(), started["item"])

        first = post(url + "api/submit", {"session_id": session_id, "answer": answer})
        if first["evidence"]["status"] != "recorded":
            fail("the first submit was not recorded: %r" % first["evidence"])

        with open(session_file, encoding="utf-8") as fh:
            data = json.load(fh)
        data["cursor"] -= 1
        data["status"] = "active"
        with open(session_file, "w", encoding="utf-8") as fh:
            json.dump(data, fh)

        second = post(url + "api/submit", {"session_id": session_id, "answer": answer})
        if second["evidence"]["status"] != "already_recorded":
            fail("resubmitting the same answer for the same item returned %r, expected "
                 "already_recorded" % second["evidence"]["status"])
    finally:
        proc.terminate()


def check_api_survives_routine_error():
    """The plan's real point: driving a session to completion over
    `/api/submit`, submitting once more, must return a 4xx and leave the
    daemon serving every other route -- not a dead process (T-2-03).
    """
    workdir = tempfile.mkdtemp()
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    proc, url, lines = start_daemon(workdir)
    try:
        started = post(url + "api/start", {"bank": "sample_bank", "count": 6, "seed": 7})
        session_id = started["session_id"]
        by_id = api_by_id()
        state = started
        while state["status"] == "active":
            answer = api_correct_answer(by_id, state["item"])
            result = post(url + "api/submit", {"session_id": session_id, "answer": answer})
            state = result["next"]
        if state["status"] != "complete":
            fail("driving a full sitting over /api/* did not reach status complete")

        try:
            post(url + "api/submit", {"session_id": session_id, "answer": "anything"})
            fail("submitting past a complete session did not return a 4xx")
        except urllib.error.HTTPError as exc:
            if exc.code < 400 or exc.code >= 500:
                fail("submitting past a complete session returned HTTP %d, expected 4xx"
                     % exc.code)

        # The test with teeth: without this second assertion the check above
        # would pass on a daemon that just died from an uncaught SystemExit.
        status, _ = get(url)
        if status != 200:
            fail("the daemon did not survive a routine error: GET / returned %d" % status)
    finally:
        proc.terminate()


def check_api_bank_not_found():
    workdir = tempfile.mkdtemp()
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    proc, url, lines = start_daemon(workdir)
    try:
        try:
            post(url + "api/start", {"bank": "no-such-bank", "count": 1})
            fail("POST /api/start with a bank stem that was not scanned did not "
                 "return a 4xx")
        except urllib.error.HTTPError as exc:
            if exc.code != 404:
                fail("POST /api/start with an unscanned bank stem returned HTTP %d, "
                     "expected 404" % exc.code)
        attempts_dir = os.path.join(workdir, "_attempts")
        if os.path.isdir(attempts_dir) and os.listdir(attempts_dir):
            fail("POST /api/start against an unscanned bank stem created a session file")
    finally:
        proc.terminate()


def check_api_start_traversal():
    """A `bank` field naming a path outside the served directory -- absolute,
    or with parent-directory segments -- returns 4xx, creates no directory
    and writes no file (T-2-01, T-2-02).
    """
    workdir = tempfile.mkdtemp()
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    proc, url, lines = start_daemon(workdir)
    try:
        parent = os.path.dirname(workdir)
        before = snapshot_dirs(parent)
        hostile_values = (
            "../../etc/passwd",
            "..\\..\\Windows\\System32\\evil",
            os.path.abspath(os.path.join(workdir, "..", "escaped")),
        )
        for hostile in hostile_values:
            try:
                post(url + "api/start", {"bank": hostile, "count": 1})
                fail("a path-shaped bank field was accepted instead of returning a "
                     "4xx: %r" % hostile)
            except urllib.error.HTTPError as exc:
                if exc.code < 400 or exc.code >= 500:
                    fail("a path-shaped bank field returned HTTP %d, expected 4xx"
                         % exc.code)
        after = snapshot_dirs(parent)
        if after != before:
            fail("a hostile bank field on /api/start created a new directory: %r"
                 % (after - before))
        attempts_dir = os.path.join(workdir, "_attempts")
        if os.path.isdir(attempts_dir) and os.listdir(attempts_dir):
            fail("a hostile bank field on /api/start wrote a session file")
    finally:
        proc.terminate()


def check_api_reject_path_fields():
    """A `session`, `bank_path` or `out` field on any `/api/*` body is a 400
    naming the field, never silently ignored -- accepting one would
    reintroduce the raw-path surface D-03's allowlist closed (T-2-01). An
    unknown `session_id` is a 404, and neither case reads a file.
    """
    workdir = tempfile.mkdtemp()
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    proc, url, lines = start_daemon(workdir)
    try:
        started = post(url + "api/start", {"bank": "sample_bank", "count": 1, "seed": 0})
        session_id = started["session_id"]

        for field, value in (("session", os.path.join(workdir, "_attempts", "x.json")),
                             ("bank_path", BANK), ("out", "somewhere.json")):
            try:
                post(url + "api/next", {"session_id": session_id, field: value})
                fail("a %r field on /api/next was silently accepted" % field)
            except urllib.error.HTTPError as exc:
                if exc.code != 400:
                    fail("a %r field on /api/next returned HTTP %d, expected 400"
                         % (field, exc.code))

        try:
            post(url + "api/next", {"session_id": "no-such-session-id"})
            fail("an unknown session_id on /api/next did not return a 4xx")
        except urllib.error.HTTPError as exc:
            if exc.code != 404:
                fail("an unknown session_id on /api/next returned HTTP %d, expected 404"
                     % exc.code)
    finally:
        proc.terminate()


def check_api_malformed_json():
    """A malformed JSON body on `/api/submit` returns 4xx and the daemon
    stays up.
    """
    workdir = tempfile.mkdtemp()
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    proc, url, lines = start_daemon(workdir)
    try:
        req = urllib.request.Request(
            url + "api/submit", data=b"{not valid json",
            headers={"Content-Type": "application/json"})
        try:
            urllib.request.urlopen(req, timeout=5)
            fail("a malformed JSON body on /api/submit did not return a 4xx")
        except urllib.error.HTTPError as exc:
            if exc.code < 400 or exc.code >= 500:
                fail("a malformed JSON body on /api/submit returned HTTP %d, expected "
                     "4xx" % exc.code)
        status, _ = get(url)
        if status != 200:
            fail("the daemon did not survive a malformed JSON body: GET / returned %d"
                 % status)
    finally:
        proc.terminate()


def check_api_cli_parity():
    """SURF-04's real assertion: a sitting driven over `/api/*` and the same
    sitting driven over the CLI, against the same bank and the same seed,
    record matching evidence events on `score`, `objective`, `mode` and
    `canonical` -- proving the daemon reaches the same runtime call rather
    than a second implementation.
    """
    api_dir = tempfile.mkdtemp()
    cli_dir = tempfile.mkdtemp()
    shutil.copy(BANK, os.path.join(api_dir, "sample_bank.md"))
    shutil.copy(BANK, os.path.join(cli_dir, "sample_bank.md"))

    by_id = api_by_id()

    proc, url, lines = start_daemon(api_dir)
    try:
        started = post(url + "api/start",
                       {"bank": "sample_bank", "count": 6, "seed": 7, "mode": "practice"})
        session_id = started["session_id"]
        state = started
        while state["status"] == "active":
            answer = api_correct_answer(by_id, state["item"])
            result = post(url + "api/submit", {"session_id": session_id, "answer": answer})
            state = result["next"]
    finally:
        proc.terminate()

    cli_bank = os.path.join(cli_dir, "sample_bank.md")
    cli_session = os.path.join(cli_dir, "session.json")
    first = agent_roundtrip.run("start", cli_bank, "--count", "6", "--seed", "7",
                                "--mode", "practice", "--out", cli_session)
    while first["status"] == "active":
        answer = api_correct_answer(by_id, first["item"])
        result = agent_roundtrip.run("submit", cli_session, "--answer",
                                     json.dumps(answer))
        first = result["next"]

    api_log = evidence.log_path(api_dir)
    cli_log = evidence.log_path(cli_dir)
    api_events = [ev for ev in evidence.live_events(api_log) if ev["event_type"] == "response"]
    cli_events = [ev for ev in evidence.live_events(cli_log) if ev["event_type"] == "response"]
    if len(api_events) != len(cli_events):
        fail("the /api/* sitting recorded %d response events but the CLI sitting "
             "recorded %d, for the same bank and seed"
             % (len(api_events), len(cli_events)))

    api_by_ref = {ev["item_ref"]: ev for ev in api_events}
    cli_by_ref = {ev["item_ref"]: ev for ev in cli_events}
    if set(api_by_ref) != set(cli_by_ref):
        fail("the /api/* and CLI sittings recorded events for different items")
    for ref, api_ev in api_by_ref.items():
        cli_ev = cli_by_ref[ref]
        for field in ("score", "objective", "mode", "canonical"):
            if api_ev.get(field) != cli_ev.get(field):
                fail("item %s: /api/* recorded %s=%r but the CLI recorded %s=%r"
                     % (ref, field, api_ev.get(field), field, cli_ev.get(field)))


def main():
    checks = (
        check_index_populated,
        check_index_order,
        check_index_empty,
        check_index_malformed_tolerated,
        check_index_no_truncation,
        check_quiz_no_key,
        check_answer_scoring,
        check_two_bank_isolation,
        check_stem_collision,
        check_fixed_routes_not_shadowed,
        check_unknown_stem,
        check_concurrency,
        check_study_route,
        check_study_cmd_matches_study_page,
        check_day_route,
        check_day_index_single_plan,
        check_day_index_ambiguous,
        check_day_save_and_isolation,
        check_day_open_out_of_range,
        check_route_cli_inventory,
        check_api_route_scope,
        check_api_sitting,
        check_api_duplicate_submit_dedupes,
        check_api_survives_routine_error,
        check_api_bank_not_found,
        check_api_start_traversal,
        check_api_reject_path_fields,
        check_api_malformed_json,
        check_api_cli_parity,
    )
    for check in checks:
        check()
    print("ok: daemon served %d checks -- index, quiz, answer scoring, cross-bank "
          "isolation, stem collisions and the route/CLI inventory all held"
          % len(checks))
    return 0


if __name__ == "__main__":
    sys.exit(main())
