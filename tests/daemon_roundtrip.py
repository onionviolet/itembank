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
import hashlib, http.server, json, os, re, shutil, socketserver, subprocess, sys, tempfile, threading, time, uuid
import urllib.error, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import itembank                                            # noqa: E402
import evidence                                             # noqa: E402
from surfaces import cli, daemon, day, session, study        # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agent_roundtrip                                       # noqa: E402
import serve_roundtrip                                      # noqa: E402

BANK = os.path.join(ROOT, "fixtures", "sample_bank.md")
PLAN = os.path.join(ROOT, "fixtures", "sample_plan.md")


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def start_daemon(workdir, *extra_args, force_port_zero=True):
    """Launch `itembank daemon <workdir> --no-open[, --port 0]`, drain its
    stdout on a background thread, and return `(proc, url, lines)` once the
    printed banner's URL has been scraped -- the same subprocess-plus-
    background-thread shape `tests/serve_roundtrip.py` and
    `tests/day_roundtrip.py` already use, generalized to a daemon that can
    be pointed at any prepared directory. Exported at module level so later
    plans in this phase (02-02, 02-04, 02-05, 02-06) can import or copy it.

    `force_port_zero` defaults to True: every earlier caller relies on
    getting an OS-assigned free port so concurrent test runs never collide,
    and `extra_args` can still override it (argparse keeps the last `--port`
    it sees) the way plan 02-06's own `--lan`/known-port checks below do.
    Pass `False` for the one case that needs `--port` omitted entirely so a
    settings-driven default in `itembank.json` can take effect.
    """
    args = [sys.executable, "-u", os.path.join(ROOT, "itembank.py"), "daemon", workdir,
            "--no-open"]
    if force_port_zero:
        args += ["--port", "0"]
    args += list(extra_args)
    proc = subprocess.Popen(
        args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
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


def free_port():
    """A currently-free TCP port, found by binding a throwaway server on
    port 0 and reading the OS-assigned number back before closing it --
    used wherever a startup-case test below needs a *known* port rather
    than the usual 0, matching `tests/day_roundtrip.py`'s own
    fixed-port-versus-port-zero split for exactly the same reason.
    """
    srv = socketserver.TCPServer(("127.0.0.1", 0), socketserver.BaseRequestHandler)
    port = srv.server_address[1]
    srv.server_close()
    return port


def start_decoy(port, body=b"plain text, not itembank", content_type="text/plain",
                status=200):
    """A throwaway HTTP listener on a known port that is definitely not an
    itembank daemon -- the false-positive guard `probe()` must survive
    (T-2-08), and the squatter the reserved/occupied-by-something-else
    startup case falls back around. Returns the bound server; the caller
    shuts it down.
    """
    class Decoy(http.server.BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    srv = socketserver.TCPServer(("127.0.0.1", port), Decoy)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def run_daemon_once(args, timeout=10):
    """Launch `itembank <args>` and wait for it to exit on its own, rather
    than serve forever -- for the already-running attach case, which is
    expected to print its line and exit 0 quickly instead of binding
    anything. Returns `(returncode, output)`.
    """
    result = subprocess.run(
        [sys.executable, "-u", os.path.join(ROOT, "itembank.py")] + list(args),
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=timeout)
    return result.returncode, result.stdout


def get(url):
    with urllib.request.urlopen(url, timeout=5) as res:
        return res.status, res.read().decode("utf-8")


def post(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=5) as res:
        return json.loads(res.read().decode("utf-8"))


def json_request(url, payload=None, method="POST", timeout=5):
    """A reusable JSON request helper returning `(status, body)` for any HTTP
    outcome -- `body` is parsed JSON on a JSON response, otherwise the text.
    Unlike `post()`, a non-2xx is not raised; the caller asserts the code.
    """
    body = b"" if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(url, data=body, method=method,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            raw = res.read()
            status = res.status
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        status = exc.code
    except urllib.error.URLError as exc:
        return None, str(exc.reason)
    try:
        return status, json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return status, raw.decode("utf-8", errors="replace")


def temp_dir_with(bank=True, plan=False, settings_overrides=None, name="work"):
    """A temp directory pre-loaded with the fixture bank/plan and, when
    `settings_overrides` is given, an itembank.json built from the shipped
    defaults merged with those overrides -- the isolated settings base later
    Phase 4 route checks (accent save, LAN policy) will build on.
    """
    workdir = tempfile.mkdtemp(prefix=name + "-")
    if bank:
        shutil.copy(BANK, os.path.join(workdir, os.path.basename(BANK)))
    if plan:
        shutil.copy(PLAN, os.path.join(workdir, os.path.basename(PLAN)))
    if settings_overrides:
        write_settings_file(workdir, settings_overrides)
    return workdir


def write_settings_file(base, overrides):
    """Write itembank.json into `base` from the schema defaults merged over
    `overrides`, through the existing validated `settings.write_settings`.
    """
    from surfaces import settings
    data = settings.load_settings(base)
    for dotted, value in overrides.items():
        node = data
        parts = dotted.split(".")
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = value
    settings.write_settings(base, data)
    return data


def assert_fixed_routes_before_patterned(routes):
    """Every fixed-literal route must precede every regex route in the daemon's
    ordered route table -- the shadowing rule that keeps a bank stem named
    "report" or "api" from hijacking a fixed route.
    """
    saw_patterned = False
    for method, pattern, _ in routes:
        if hasattr(pattern, "match"):
            saw_patterned = True
        elif saw_patterned:
            fail("fixed route (%s, %s) appears after a regex route; the "
                 "ordered route table can be shadowed" % (method, pattern))


def token_store():
    """A one-use, draft/revision-bound force-token recorder for Phase 4 plan
    04-06's conflict-recovery scenario: `issue` returns a token, `consume`
    succeeds exactly once per token and rejects replay, `state` exposes the
    recorded bindings. Harness-only; the production token lives in the day
    document seam later plans implement.
    """
    state = {"issued": [], "consumed": []}

    def issue(bound_revision):
        token = uuid.uuid4().hex
        state["issued"].append({"token": token, "revision": bound_revision})
        return token

    def consume(token):
        if any(c["token"] == token for c in state["consumed"]):
            return False
        issued = [i for i in state["issued"] if i["token"] == token]
        if not issued:
            return False
        state["consumed"].append(issued[0])
        return True

    return {"issue": issue, "consume": consume, "state": state}


def legacy_answer_url(quiz_url):
    """The legacy bank-scoped answer route (`/quiz/<stem>/answer`) the old
    browser flow posted to. The new served flow uses /api/start + /api/submit,
    but the legacy route must stay compatible (success criteria), so these
    checks still drive it directly.
    """
    return quiz_url.rstrip("/") + "/answer"


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


def day_boot_data(page):
    """Parse the `window.__day__` JSON embedded in one rendered day page."""
    m = re.search(r"window\.__day__=(\{.*?\});\n", page, re.S)
    if not m:
        return None
    return json.loads(m.group(1))


def day_page_css(page):
    """The concatenated `<style>` blocks of one rendered day page."""
    return "".join(re.findall(r"<style>(.*?)</style>", page, re.S))


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
        serve_roundtrip.check_served_boot(page, qs, "sample_bank", "practice")
        serve_roundtrip.check_served_page_js(page, "sample_bank")
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
        answer_url = legacy_answer_url(quiz_url)
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
        answer_url = legacy_answer_url(quiz_url)
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


def check_day_edit_route():
    """Plan 04-06 Task 1 tests 1-5 (daemon side): GET /day/<stem> embeds the
    snapshot boot data; POST /day/<stem>/edit patches only requested cells and
    returns a new revision that the next render reflects; the edit route
    resolves the stem only through `handler.plans`, rejects path/full-document
    authority fields, sits after fixed literals, and maps to the `day` CLI;
    tick-save/open routes keep working while a plan edit invalidates only
    parsed plan/render state.
    """
    if not hasattr(daemon, "DAY_EDIT_RE"):
        fail("daemon has no DAY_EDIT_RE for the plan edit route")
    routes = daemon.ROUTES
    fixed_after = False
    edit_pos = None
    for i, (method, pattern, name) in enumerate(routes):
        if name == "handle_day_edit":
            edit_pos = i
        if edit_pos is not None and not hasattr(pattern, "match"):
            fixed_after = True
    if edit_pos is None:
        fail("ROUTES has no handle_day_edit entry")
    if fixed_after:
        fail("handle_day_edit is not ordered after every fixed literal route")
    if not any(method == "POST" and getattr(pattern, "pattern", None)
               == daemon.DAY_EDIT_RE.pattern
               for method, pattern, name in routes):
        fail("ROUTES does not carry the DAY_EDIT_RE pair")
    cli_match = [v for (m, p), v in daemon.ROUTE_CLI.items()
                 if m == "POST" and getattr(p, "pattern", None)
                 == daemon.DAY_EDIT_RE.pattern]
    if cli_match != ["day"]:
        fail("POST /day/<stem>/edit does not map to the day CLI twin")

    workdir = tempfile.mkdtemp()
    iso = write_today_plan(os.path.join(workdir, "sample_plan.md"),
                           "ch 2 first half")
    proc, url, lines = start_daemon(workdir)
    try:
        status, page = get(url + "day/sample_plan")
        if status != 200:
            fail("GET /day/<stem> returned %d for the edit test" % status)
        boot = day_boot_data(page)
        if boot is None:
            fail("day page has no boot data for the edit route")
        snap = boot.get("snapshot")
        if not snap or snap.get("status") != "ready":
            fail("day boot snapshot not ready for the edit route: %r" % snap)
        if not re.fullmatch(r"[0-9a-f]{64}", snap.get("revision", "")):
            fail("day boot snapshot revision is not SHA-256")
        if snap.get("cells", {}).get("EMT (top priority)") != "ch 2 first half":
            fail("day boot snapshot lost the current cell value")
        if "plan.md" in json.dumps(boot) or workdir in json.dumps(boot):
            fail("day boot data leaks a filesystem path")
        if "Edit plan" not in page or "Save changes" not in page:
            fail("day page has no Edit plan / Save changes controls")
        if "<textarea" in page:
            fail("day editor exposes a raw Markdown textarea")

        saved = post(url + "day/sample_plan/edit", {
            "revision": snap["revision"],
            "edits": {"EMT (top priority)": "ch 3, start"}})
        if saved.get("status") != "saved":
            fail("day edit route returned %r, want saved" % saved.get("status"))
        if saved.get("revision") == snap["revision"]:
            fail("day edit route returned the stale revision")
        if saved.get("cells", {}).get("EMT (top priority)") != "ch 3, start":
            fail("day edit route did not return the saved cells")
        if saved.get("row", {}).get("EMT") != "ch 3, start":
            fail("day edit route did not return the fresh parsed row")
        _status, page2 = get(url + "day/sample_plan")
        if "ch 3, start" not in page2:
            fail("next render after a plan edit does not show the new plan text")
        boot2 = day_boot_data(page2)
        if boot2["snapshot"]["revision"] == snap["revision"]:
            fail("next render after a plan edit kept the stale revision")
        plan_bytes_now = open(os.path.join(workdir, "sample_plan.md"),
                              "rb").read()
        if b"ch 3, start" not in plan_bytes_now:
            fail("plan edit did not reach the file bytes")

        invalid = post(url + "day/sample_plan/edit", {
            "revision": boot2["snapshot"]["revision"],
            "edits": {"EMT (top priority)": "bad\nvalue"}})
        if invalid.get("status") != "invalid":
            fail("day edit invalid status %r, want invalid" % invalid.get("status"))
        if invalid.get("draft") != {"EMT (top priority)": "bad\nvalue"}:
            fail("day edit invalid response lost the draft: %r"
                 % invalid.get("draft"))
        if open(os.path.join(workdir, "sample_plan.md"), "rb").read() != plan_bytes_now:
            fail("day edit invalid response wrote to the file")

        for forged in ({"path": "/etc/passwd"},
                       {"document": "full file"},
                       {"plan": "other.md"},
                       {"bytes": "AA=="}):
            status_f, body = json_request(
                url + "day/sample_plan/edit",
                {"revision": snap["revision"],
                 "edits": {"EMT": "x"},
                 "force_token": "t"} | forged)
            if status_f != 200 or body.get("status") != "invalid":
                fail("day edit accepted authority field %r: %r"
                     % (forged, body))

        got = post(url + "day/sample_plan/save",
                   {"date": iso, "done": list(itembank.FLOOR_LANES)})
        if got.get("status") != "floor":
            fail("tick save after a plan edit broke: %r" % got.get("status"))
    finally:
        proc.terminate()


def edit_draft_hash(edits):
    """The canonical draft hash the daemon binds force tokens to: sorted keys,
    JSON-encoded key/value pairs joined with `,`, SHA-256 over UTF-8."""
    parts = []
    for key in sorted(edits):
        parts.append(json.dumps(key, ensure_ascii=False, sort_keys=True) + ":" +
                     json.dumps(edits[key], ensure_ascii=False, sort_keys=True))
    return hashlib.sha256(",".join(parts).encode("utf-8")).hexdigest()


def check_day_edit_conflict_and_force():
    """Plan 04-06 Task 2 tests 1, 3, 4, and 7 (daemon side): an external byte
    edit after page load yields a no-write conflict carrying the draft, both
    revisions, and a one-use force token bound to stem, stale revision,
    current revision, and draft hash; no-token, wrong-token, changed-draft,
    replayed-token, missing-confirmation, wrong-stem, and third-version
    requests write nothing; a confirmed force patches only submitted cells
    against a fresh revision and consumes the token.
    """
    workdir = tempfile.mkdtemp()
    os.makedirs(os.path.join(workdir, "a"))
    os.makedirs(os.path.join(workdir, "b"))
    plan_a = os.path.join(workdir, "a", "plan_a.md")
    plan_b = os.path.join(workdir, "b", "plan_b.md")
    iso = write_today_plan(plan_a, "ch 2 first half")
    write_today_plan(plan_b, "other plan task")
    proc, url, lines = start_daemon(workdir)
    try:
        status, page = get(url + "day/plan_a")
        if status != 200:
            fail("conflict test could not load /day/plan_a")
        snap = day_boot_data(page)["snapshot"]
        stale_rev = snap["revision"]
        original = open(plan_a, "rb").read()
        external = original.replace(b"ch 2 first half",
                                    b"changed by Obsidian")
        with open(plan_a, "wb") as fh:
            fh.write(external)

        conflict = post(url + "day/plan_a/edit",
                        {"revision": stale_rev,
                         "edits": {"EMT (top priority)": "my draft"}})
        if conflict.get("status") != "conflict":
            fail("stale save returned %r, want conflict" % conflict.get("status"))
        if open(plan_a, "rb").read() != external:
            fail("conflict response wrote to the file")
        if conflict.get("draft") != {"EMT (top priority)": "my draft"}:
            fail("conflict response lost the draft: %r" % conflict.get("draft"))
        current = conflict.get("current", {})
        if current.get("revision") != conflict.get("revision"):
            fail("conflict response current/revision mismatch")
        if current.get("cells", {}).get("EMT (top priority)") != "changed by Obsidian":
            fail("conflict response did not carry the fresh current cell")
        if current.get("revision") == stale_rev:
            fail("conflict response current revision equals the stale revision")
        token = conflict.get("force_token")
        if not isinstance(token, str) or not re.fullmatch(r"[0-9a-f]{64}", token):
            fail("conflict did not issue a one-use token: %r" % token)
        fhash = conflict.get("force_draft_hash")
        if fhash != edit_draft_hash({"EMT (top priority)": "my draft"}):
            fail("conflict draft hash %r does not match the canonical hash"
                 % fhash)

        force_base = {"revision": conflict["revision"],
                      "edits": {"EMT (top priority)": "my draft"},
                      "force": True,
                      "confirmation": ("I understand this replaces these edited "
                                       "cells using the latest plan version.")}

        st, body = json_request(url + "day/plan_a/edit",
                                dict(force_base, force_token="0" * 64))
        if st != 200 or body.get("status") != "invalid":
            fail("wrong force token was not refused: %r" % body)
        if open(plan_a, "rb").read() != external:
            fail("wrong-token force wrote to the file")

        st, body = json_request(url + "day/plan_a/edit",
                                dict(force_base, force_token=token,
                                     confirmation="nope"))
        if st != 200 or body.get("status") != "invalid":
            fail("force without the exact confirmation was not refused: %r"
                 % body)

        st, body = json_request(url + "day/plan_a/edit",
                                dict(force_base, force_token=token,
                                     edits={"EMT (top priority)": "changed draft"}))
        if st != 200 or body.get("status") != "invalid":
            fail("changed-draft force was not refused: %r" % body)
        if open(plan_a, "rb").read() != external:
            fail("changed-draft force wrote to the file")

        st, body = json_request(url + "day/plan_a/edit",
                                dict(force_base, force_token=token))
        if st != 200 or body.get("status") != "saved":
            fail("confirmed force was not saved: %r" % body)
        saved_bytes = open(plan_a, "rb").read()
        if saved_bytes == external:
            fail("confirmed force did not patch the file")
        if b"my draft" not in saved_bytes or b"Ch 1 sets, problems 1-6" not in saved_bytes:
            fail("confirmed force lost the draft cell or the concurrent Math edit")
        if body.get("revision") == stale_rev:
            fail("confirmed force returned the stale revision")
        if body.get("cells", {}).get("EMT (top priority)") != "my draft":
            fail("confirmed force did not return the saved cells")
        if token in daemon.DaemonHandler.day_force_tokens:
            fail("confirmed force did not consume the one-use token")

        replay = post(url + "day/plan_a/edit",
                      dict(force_base, force_token=token))
        if replay.get("status") != "invalid":
            fail("replayed force token was not refused: %r" % replay)
        if open(plan_a, "rb").read() != saved_bytes:
            fail("replayed force wrote to the file")

        st, body = json_request(url + "day/plan_b/edit",
                                dict(force_base, force_token=token))
        if st != 200 or body.get("status") != "invalid":
            fail("wrong-stem force was not refused: %r" % body)

        conflict2 = post(url + "day/plan_a/edit",
                         {"revision": stale_rev,
                          "edits": {"EMT (top priority)": "my draft"}})
        if conflict2.get("status") != "conflict":
            fail("second stale save returned %r, want conflict"
                 % conflict2.get("status"))
        token2 = conflict2.get("force_token")
        if not isinstance(token2, str) or not re.fullmatch(r"[0-9a-f]{64}", token2):
            fail("second conflict did not issue a fresh token: %r" % token2)
        if token2 == token:
            fail("second conflict reused the consumed token")

        third = saved_bytes.replace(b"Ch 1 sets, problems 1-6",
                                    b"changed a third time")
        with open(plan_a, "wb") as fh:
            fh.write(third)
        st, body = json_request(url + "day/plan_a/edit",
                                dict(force_base,
                                     revision=conflict2["revision"],
                                     force_token=token2))
        if st != 200 or body.get("status") != "conflict":
            fail("third-version force was not a fresh conflict: %r" % body)
        if open(plan_a, "rb").read() != third:
            fail("third-version force wrote to the file")
        if "force_token" in body:
            fail("third-version conflict reissued a usable force token")
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


def check_served_api_flow():
    """Test 2: the served quiz is a client of the canonical API -- the page's
    boot metadata drives POST /api/start, and POST /api/submit returns the
    server-issued score, explanation and next state (SURF-02).
    """
    workdir = tempfile.mkdtemp()
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    proc, url, lines = start_daemon(workdir)
    try:
        qs = itembank.parse_bank(open(BANK, encoding="utf-8").read())
        quiz_url = url + "quiz/sample_bank"
        _, page = get(quiz_url)
        boot = serve_roundtrip.served_boot(page)
        started = post(url + "api/start",
                       {"bank": boot["bank"], "count": boot["count"],
                        "mode": boot["mode"]})
        if "correct" in started["item"] or "explain" in started["item"]:
            fail("POST /api/start's item carries answer material")
        session_id = started["session_id"]
        answer = api_correct_answer(api_by_id(), started["item"])
        submitted = post(url + "api/submit",
                         {"session_id": session_id, "answer": answer})
        if submitted["score"] is not True:
            fail("served API flow scored the correct answer %r, expected True"
                 % submitted["score"])
        if "explain" not in submitted:
            fail("served API flow returned no explanation payload")
        if "next" not in submitted:
            fail("served API flow returned no next state")
        if submitted["evidence"]["status"] != "recorded":
            fail("served API flow did not record the response: %r"
                 % submitted["evidence"])
    finally:
        proc.terminate()


def check_api_forged_fields():
    """Test 3: `/api/submit` rejects every client field that claims an item
    id, score, key, explanation, bank path, or output path -- the current item
    is resolved from the allowlisted session, never from client authority.
    """
    workdir = tempfile.mkdtemp()
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    proc, url, lines = start_daemon(workdir)
    try:
        started = post(url + "api/start",
                       {"bank": "sample_bank", "count": 1, "seed": 0})
        session_id = started["session_id"]
        for field in ("item_id", "score", "key", "explanation",
                      "bank_path", "out", "session"):
            try:
                post(url + "api/submit", {"session_id": session_id,
                                          "answer": "A", field: "forged"})
                fail("api/submit accepted a forged %r field" % field)
            except urllib.error.HTTPError as exc:
                if exc.code != 400:
                    fail("forged %r on api/submit returned HTTP %d, expected 400"
                         % (field, exc.code))
    finally:
        proc.terminate()


def check_serve_attempt_refresh():
    """Test 4: `itembank serve --out attempt.md` still refreshes the configured
    attempt view atomically after API submissions, and its progress line is
    based on the API session id, not a stale page-owned counter.
    """
    out = os.path.join(tempfile.mkdtemp(), "attempt.md")
    proc = subprocess.Popen(
        [sys.executable, "-u", os.path.join(ROOT, "itembank.py"), "serve", BANK,
         "--no-open", "--port", "0", "--out", out],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    lines = []
    threading.Thread(target=lambda: [lines.append(l) for l in proc.stdout],
                     daemon=True).start()
    base = None
    for _ in range(60):
        time.sleep(0.1)
        m = re.search(r"http://127\.0\.0\.1:\d+/", "".join(lines))
        if m:
            base = m.group(0)
            break
    if not base:
        proc.terminate()
        fail("scoped serve never printed a URL. Output was:\n" + "".join(lines))
    try:
        qs = itembank.parse_bank(open(BANK, encoding="utf-8").read())
        _, page = get(base + "quiz/sample_bank")
        boot = serve_roundtrip.served_boot(page)
        started = post(base + "api/start",
                       {"bank": boot["bank"], "count": boot["count"],
                        "mode": boot["mode"]})
        session_id = started["session_id"]
        answer = api_correct_answer(api_by_id(), started["item"])
        submitted = post(base + "api/submit",
                         {"session_id": session_id, "answer": answer})
        if submitted["score"] is not True:
            fail("scoped serve API submit scored %r, expected True"
                 % submitted["score"])

        text = open(out, encoding="utf-8").read()
        if "[auto: correct]" not in text:
            fail("configured attempt view was not refreshed after the API submit")
        output = "".join(lines)
        log = evidence.log_path(os.path.dirname(os.path.abspath(BANK)) or ".")
        api_count = len(set(ev["item_ref"]
                            for ev in evidence.session_events(log, session_id)))
        want_progress = "  %d/%d answered, saved" % (api_count, len(qs))
        if want_progress not in output:
            fail("scoped serve progress did not print the API session count: %r"
                 % output[-400:])
        if api_count < 1:
            fail("the API session recorded no events for the progress count")
    finally:
        proc.terminate()


def check_wave0_helpers():
    """Task 1 self-check for the reusable Phase 4 helpers: route order,
    temp-dir/settings bases, one-use force tokens, and JSON request handling.
    Pure helper checks -- no daemon needed, so this stays fast.
    """
    assert_fixed_routes_before_patterned(daemon.ROUTES)

    workdir = temp_dir_with(bank=True, plan=True,
                            settings_overrides={"daemon.port": 8123,
                                                "theme": "light"})
    try:
        if not os.path.isfile(os.path.join(workdir, "sample_bank.md")):
            fail("temp_dir_with did not copy the bank fixture")
        if not os.path.isfile(os.path.join(workdir, "sample_plan.md")):
            fail("temp_dir_with did not copy the plan fixture")
        from surfaces import settings as settings_mod
        cfg = settings_mod.load_settings(workdir)
        if cfg["daemon"]["port"] != 8123 or cfg["theme"] != "light":
            fail("temp_dir_with settings overrides did not land: %r" % cfg)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)

    store = token_store()
    token = store["issue"]("rev-abc")
    if store["consume"](token) is not True:
        fail("freshly issued force token was not consumable")
    if store["consume"](token) is not False:
        fail("one-use force token was consumed twice")
    if store["consume"]("never-issued") is not False:
        fail("an unknown force token was accepted")

    status, _ = json_request("http://127.0.0.1:1/api/start",
                             {"bank": "nope"}, timeout=1)
    if status is not None and status not in (400, 404):
        fail("json_request against a closed port returned unexpected status %r"
             % status)


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


# ---- /report -- the last route SURF-01 names, and the last new page this
# phase authors. Two rows this plan's own UI-SPEC carries as deliberate
# backstops, confirmed at UAT rather than automated here: the overflow
# behaviour of a report carrying ten or more pending `short` items, and the
# concrete visual layout of the populated case. Their absence below is not
# an oversight.

REPORT_FIELD_RE_TMPL = r'data-field="%s"[^>]*>(?:<div class="figure-value">)?(\d+)'


def report_field(body, field):
    """The integer value at `REPORT_TEMPLATE`'s `data-field="<field>"`
    marker -- a narrow regex against a stable attribute, not a scrape of
    prose that a later copywriting change could silently break.
    """
    m = re.search(REPORT_FIELD_RE_TMPL % re.escape(field), body)
    return int(m.group(1)) if m else None


def report_progress(body):
    """`(position, total)` from the in-progress state's own `data-field`
    marker, or `None` if the report carries no progress line at all.
    """
    m = re.search(r'data-field="progress">In progress -- (\d+) of (\d+) items', body)
    return (int(m.group(1)), int(m.group(2))) if m else None


def report_objective_rows(body):
    """Every `<tr>...</tr>` inside the report's objective `<tbody>`, or an
    empty list if the report has no table at all (the empty state).
    """
    m = re.search(r"<tbody>(.*?)</tbody>", body, re.S)
    if not m:
        return []
    return re.findall(r"<tr>.*?</tr>", m.group(1), re.S)


def drive_sitting(url, session_id, by_id, short_answer="leave this one for a human marker"):
    """Answer every remaining item in an active session over `/api/submit`,
    scoring correctly whenever the item is auto-markable and leaving a
    `short` item's text unmarked -- the mixed-outcome fixture several report
    checks below share.
    """
    state = post(url + "api/next", {"session_id": session_id})
    while state["status"] == "active":
        item = state["item"]
        q = by_id[item["id"]]
        answer = short_answer if q["type"] == "short" else api_correct_answer(by_id, item)
        result = post(url + "api/submit", {"session_id": session_id, "answer": answer})
        state = result["next"]
    return state


def check_report_populated():
    """Populated: a session mixing correct, incorrect and pending responses
    renders 200, carries every objective the fixture bank names, and
    carries the auto-marked/correct/pending-manual figures.
    """
    workdir = tempfile.mkdtemp()
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    proc, url, lines = start_daemon(workdir)
    try:
        by_id = api_by_id()
        started = post(url + "api/start",
                       {"bank": "sample_bank", "count": 6, "seed": 7, "mode": "practice"})
        session_id = started["session_id"]
        state = started
        wrong_done = False
        while state["status"] == "active":
            item = state["item"]
            q = by_id[item["id"]]
            if q["type"] == "short":
                answer = "leave this one for a human marker"
            elif not wrong_done:
                answer = serve_roundtrip.wrong_answer(q)
                wrong_done = True
            else:
                answer = api_correct_answer(by_id, item)
            result = post(url + "api/submit", {"session_id": session_id, "answer": answer})
            state = result["next"]

        status, body = get(url + "report?session=%s" % session_id)
        if status != 200:
            fail("GET /report on a populated session returned %d, expected 200" % status)
        qs = itembank.parse_bank(open(BANK, encoding="utf-8").read())
        for objective in set(q.get("objective", "") for q in qs):
            if objective and objective not in body:
                fail("the populated report is missing objective %r" % objective)
        for field in ("auto_attempts", "auto_correct", "pending_manual"):
            if report_field(body, field) is None:
                fail("the populated report has no %s figure" % field)
    finally:
        proc.terminate()


def check_report_matches_command():
    """SURF-04's real assertion: the page and `session.do_report` agree on
    `auto_attempts`, `auto_correct` and `pending_manual` for the same
    session, compared as three named numeric fields rather than a substring
    of prose.
    """
    workdir = tempfile.mkdtemp()
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    proc, url, lines = start_daemon(workdir)
    body = None
    try:
        by_id = api_by_id()
        started = post(url + "api/start",
                       {"bank": "sample_bank", "count": 6, "seed": 3, "mode": "practice"})
        session_id = started["session_id"]
        session_file = started["session_file"]
        drive_sitting(url, session_id, by_id)

        status, body = get(url + "report?session=%s" % session_id)
        if status != 200:
            fail("GET /report returned %d, expected 200" % status)
    finally:
        proc.terminate()

    want = session.do_report(session_file)["summary"]
    for field in ("auto_attempts", "auto_correct", "pending_manual"):
        got = report_field(body, field)
        if got != want[field]:
            fail("the report page's %s figure is %r but session.do_report says %r"
                 % (field, got, want[field]))


def check_report_empty():
    workdir = tempfile.mkdtemp()
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    proc, url, lines = start_daemon(workdir)
    try:
        started = post(url + "api/start", {"bank": "sample_bank", "count": 6, "seed": 0})
        session_id = started["session_id"]
        status, body = get(url + "report?session=%s" % session_id)
        if status != 200:
            fail("GET /report on a fresh session returned %d, expected 200" % status)
        if "Nothing has been answered yet." not in body:
            fail("an empty session's report is missing the documented empty-state heading")
        if "<table" in body:
            fail("an empty session's report renders an objective table")
    finally:
        proc.terminate()


def check_report_in_progress():
    workdir = tempfile.mkdtemp()
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    proc, url, lines = start_daemon(workdir)
    try:
        by_id = api_by_id()
        started = post(url + "api/start", {"bank": "sample_bank", "count": 6, "seed": 7})
        session_id = started["session_id"]
        answer = api_correct_answer(by_id, started["item"])
        result = post(url + "api/submit", {"session_id": session_id, "answer": answer})
        if result["next"]["status"] != "active":
            fail("answering one of six items did not leave the session active")

        status, body = get(url + "report?session=%s" % session_id)
        if status != 200:
            fail("GET /report on an in-progress session returned %d, expected 200" % status)
        progress = report_progress(body)
        if progress != (1, 6):
            fail("an in-progress report's position-of-total reading is %r, expected "
                 "(1, 6)" % (progress,))
        if 'data-status="complete"' in body:
            fail("an in-progress report reads as a completed session")
    finally:
        proc.terminate()


def check_report_zero_auto_marked():
    """A session whose only response is a `short` item has zero auto-marked
    responses; the page's percentage must render 0 -- never a
    `ZeroDivisionError`, never `NaN`, and never an exception swallowed into
    a 500 that only the daemon's own captured stdout would reveal.

    Seed 8 with count 1 is the fixture bank's only way to reach this: of
    the six items, exactly one (`Q6`) is `short`, and seed 8 is the seed
    under which `do_start`'s shuffle serves it first (found once, recorded
    here rather than searched at test time).
    """
    workdir = tempfile.mkdtemp()
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    proc, url, lines = start_daemon(workdir)
    try:
        started = post(url + "api/start", {"bank": "sample_bank", "count": 1, "seed": 8})
        if started["item"]["type"] != "short":
            fail("the zero-auto-marked fixture's seed no longer serves the short item "
                 "first -- item type is %r" % started["item"]["type"])
        session_id = started["session_id"]
        result = post(url + "api/submit",
                      {"session_id": session_id, "answer": "some prose, never auto-marked"})
        if result["status"] != "complete":
            fail("answering the sole item did not complete a count-1 session")

        status, body = get(url + "report?session=%s" % session_id)
        if status != 200:
            fail("GET /report on a zero-auto-marked session returned %d, expected 200"
                 % status)
        if "NaN" in body:
            fail("the report body contains a NaN percentage")
        pct = report_field(body, "pct")
        if pct != 0:
            fail("a session with zero auto-marked responses rendered pct=%r, expected 0"
                 % pct)
        output = "".join(lines)
        if "ZeroDivisionError" in body or "ZeroDivisionError" in output:
            fail("a ZeroDivisionError leaked into the report body or the daemon's "
                 "captured stdout")
    finally:
        proc.terminate()


def check_report_objective_rows_one_and_many():
    """The per-objective row markup is the same shape at one objective as
    at many -- compared by row count and by tag structure, not by text.
    """
    workdir = tempfile.mkdtemp()
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    proc, url, lines = start_daemon(workdir)
    try:
        by_id = api_by_id()

        one = post(url + "api/start", {"bank": "sample_bank", "count": 1, "seed": 7})
        one_answer = api_correct_answer(by_id, one["item"])
        post(url + "api/submit", {"session_id": one["session_id"], "answer": one_answer})
        _, one_body = get(url + "report?session=%s" % one["session_id"])
        one_rows = report_objective_rows(one_body)

        many = post(url + "api/start", {"bank": "sample_bank", "count": 6, "seed": 7})
        drive_sitting(url, many["session_id"], by_id)
        _, many_body = get(url + "report?session=%s" % many["session_id"])
        many_rows = report_objective_rows(many_body)

        if len(one_rows) != 1:
            fail("a one-item session's report has %d objective rows, expected 1"
                 % len(one_rows))
        if len(many_rows) <= 1:
            fail("a six-item session's report has %d objective rows, expected more "
                 "than 1" % len(many_rows))
        one_shape = re.sub(r">[^<]*<", "><", one_rows[0])
        many_shape = re.sub(r">[^<]*<", "><", many_rows[0])
        if one_shape != many_shape:
            fail("the objective row's tag structure differs between one objective and "
                 "many:\n  one:  %r\n  many: %r" % (one_shape, many_shape))
    finally:
        proc.terminate()


def check_report_not_found():
    workdir = tempfile.mkdtemp()
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    proc, url, lines = start_daemon(workdir)
    try:
        for query in ("", "session=nope",
                      "session=" + urllib.parse.quote("../../etc/passwd", safe="")):
            target = url + "report" + ("?" + query if query else "")
            try:
                get(target)
                fail("GET /report with query %r did not return a 404" % query)
            except urllib.error.HTTPError as exc:
                if exc.code != 404:
                    fail("GET /report with query %r returned HTTP %d, expected 404"
                         % (query, exc.code))
                body = exc.read().decode("utf-8")
                if "Not found" not in body:
                    fail("the /report 404 body is missing the documented not-found "
                         "copy for query %r" % query)
                if "Traceback" in body:
                    fail("the /report 404 body leaked a traceback for query %r" % query)
                if workdir in body:
                    fail("the /report 404 body leaked the served directory for query "
                         "%r" % query)
        status, _ = get(url)
        if status != 200:
            fail("the daemon did not survive the /report not-found cases: GET / "
                 "returned %d" % status)
    finally:
        proc.terminate()


def check_report_no_truncation():
    workdir = tempfile.mkdtemp()
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    proc, url, lines = start_daemon(workdir)
    try:
        by_id = api_by_id()
        started = post(url + "api/start", {"bank": "sample_bank", "count": 6, "seed": 7})
        drive_sitting(url, started["session_id"], by_id)
        _, body = get(url + "report?session=%s" % started["session_id"])
        low = body.lower()
        if "nowrap" in low:
            fail("the served report declares a nowrap rule; table/figure text must wrap")
        if "text-overflow" in low:
            fail("the served report declares a text-overflow ellipsis rule")
    finally:
        proc.terminate()


# ---- /settings and /api/theme -- plan 04-04 Task 1: the browser half of
# D-05 through D-07. The page is generated by `theme.theme_page(config)` and
# served per-render from the daemon root's own validated settings; the route
# is the browser twin of the `itembank theme` CLI, with loopback+same-origin
# mutation policy and the tested source/.pyz picker child bridge.

THEME_ROUTE = "/api/theme"
SETTINGS_ROUTE = "/settings"


def theme_request(url, payload, headers=None):
    """POST JSON to /api/theme, returning `(status, body)` for any HTTP
    outcome -- the same shape as `json_request`, with extra header support
    for the same-origin checks.
    """
    body = b"" if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(url, data=body, method="POST",
                                 headers={"Content-Type": "application/json"})
    if headers:
        for name, value in headers.items():
            req.add_header(name, value)
    try:
        with urllib.request.urlopen(req, timeout=5) as res:
            raw = res.read()
            status = res.status
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        status = exc.code
    except urllib.error.URLError as exc:
        return None, str(exc.reason)
    try:
        return status, json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return status, raw.decode("utf-8", errors="replace")


def settings_bytes(base):
    path = os.path.join(base, "itembank.json")
    with open(path, "rb") as fh:
        return fh.read()


def settings_source(base):
    from surfaces import settings as settings_mod
    return settings_mod.load_settings(base)["accent"]["source"]


def native_picker_would_block():
    """True when a real Tk color dialog would appear and block the picker
    child (an interactive Windows/macOS/Linux session). Headless environments
    (CI) fail fast instead, so the live `/api/theme` pick path is only
    exercised there; the fail-closed mapping itself is unit-proven in
    `tests/theme_roundtrip.py` against the launcher seam.
    """
    if sys.platform == "win32":
        return True
    return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))


def check_settings_page():
    """Test 1 + part of Test 6: GET /settings renders the labeled browser
    color input, exact picker/save/reset copy, side-by-side light/dark
    preview samples with contrast disclosure, one quiet Theme section, an
    Accessibility details disclosure, and a persistent polite status region.
    """
    workdir = temp_dir_with(bank=True, settings_overrides={"theme": "system"})
    proc, url, lines = start_daemon(workdir)
    try:
        status, body = get(url + SETTINGS_ROUTE)
        if status != 200:
            fail("GET %s returned %d, expected 200" % (SETTINGS_ROUTE, status))
        if '<input type="color"' not in body:
            fail("settings page carries no labeled browser color input")
        if 'data-settings-source' not in body:
            fail("settings page color input has no stable data-settings-source hook")
        if "Choose with system picker" not in body:
            fail("settings page is missing the exact 'Choose with system picker' control")
        if "Save accent" not in body:
            fail("settings page is missing the Save accent primary action")
        if "Reset accent" not in body:
            fail("settings page is missing the Reset action")
        if "Reset accent to the app default? Your current custom source color will be replaced." not in body:
            fail("settings page is missing the locked reset-confirmation copy")
        if 'data-preview="light"' not in body or 'data-preview="dark"' not in body:
            fail("settings page is missing the side-by-side light/dark preview samples")
        if "Light mode" not in body or "Dark mode" not in body:
            fail("each settings preview card does not name its mode")
        if "contrast" not in body.lower():
            fail("settings page carries no contrast disclosure text")
        if "Adjusted for readable contrast. Your chosen color is saved; this preview shows the accessible rendered color." not in body:
            fail("settings page is missing the locked accent-adjustment copy")
        if body.count('data-section="theme"') != 1:
            fail("settings page must have exactly one quiet Theme section")
        if "Accessibility details" not in body:
            fail("settings page is missing the Accessibility details disclosure")
        if '<details' not in body:
            fail("settings page uses no native details disclosure")
        if 'role="status"' not in body and 'aria-live="polite"' not in body:
            fail("settings page has no persistent polite status region")
        if "#0e6e62" not in body:
            fail("settings page does not show the current source accent")
        if '<input type="color"' not in body:
            fail("settings page lost its browser color fallback input")
    finally:
        proc.terminate()


def check_theme_route_contract():
    """Test 2: POST /api/theme preview/pick/save/reset follow the CLI twin's
    own helper contract -- preview is read-only, save persists the normalized
    source and returns it with a generated preview, reset requires the literal
    confirmation RESET, and unknown/authority fields are refused.
    """
    workdir = temp_dir_with(bank=True, settings_overrides={"theme": "system"})
    base = os.path.join(workdir, "itembank.json")
    before = settings_bytes(workdir)
    proc, url, lines = start_daemon(workdir)
    try:
        endpoint = url + THEME_ROUTE
        status, body = theme_request(endpoint, {"action": "preview", "source": "#0e6e62"})
        if status != 200:
            fail("preview returned %d, expected 200" % status)
        for key in ("source", "normalized_source", "light", "dark", "ratios",
                    "adjusted_modes", "notices"):
            if key not in body:
                fail("preview payload is missing %r: %r" % (key, body))
        if body["normalized_source"] != "#0e6e62":
            fail("preview did not normalize the source: %r" % body["normalized_source"])
        if not body["light"].get("accent") or not body["dark"].get("accent"):
            fail("preview carries no derived light/dark accent pair")
        if settings_bytes(workdir) != before:
            fail("preview wrote itembank.json")

        status, body = theme_request(endpoint, {"action": "preview", "source": "#ffff00"})
        if status != 200:
            fail("adjusted preview returned %d, expected 200" % status)
        if body["source"] != "#ffff00":
            fail("adjusted preview did not preserve the learner's source")
        if not body["notices"]:
            fail("adjusted preview carries no adjustment notice")
        if settings_bytes(workdir) != before:
            fail("adjusted preview wrote itembank.json")

        status, _ = theme_request(endpoint, {"action": "preview", "source": "not-a-color"})
        if status != 400:
            fail("an invalid preview source returned %d, expected 400" % status)
        if settings_bytes(workdir) != before:
            fail("a rejected preview wrote itembank.json")

        status, body = theme_request(endpoint, {"action": "save", "source": "#123ABC"})
        if status != 200:
            fail("save returned %d, expected 200" % status)
        if body.get("saved") is not True:
            fail("save did not report saved: %r" % body)
        if body.get("source") != "#123abc":
            fail("save did not return the normalized persisted source: %r" % body)
        if not body.get("preview", {}).get("light", {}).get("accent"):
            fail("save returned no generated preview")
        if settings_source(workdir) != "#123abc":
            fail("save persisted %r, expected #123abc" % settings_source(workdir))

        status, _ = theme_request(endpoint, {"action": "reset", "confirm": "RESETX"})
        if status != 400:
            fail("reset without the literal RESET confirmation returned %d, expected 400"
                 % status)
        if settings_source(workdir) != "#123abc":
            fail("a refused reset still changed the persisted source")
        status, body = theme_request(endpoint, {"action": "reset", "confirm": "RESET"})
        if status != 200:
            fail("reset with RESET returned %d, expected 200" % status)
        if body.get("source") != "#0e6e62":
            fail("reset did not restore the default source: %r" % body)
        if settings_source(workdir) != "#0e6e62":
            fail("reset did not persist the default source")

        status, _ = theme_request(endpoint, {"action": "explode"})
        if status != 400:
            fail("an unknown action returned %d, expected 400" % status)
        for field in ("css", "path", "tokens", "config", "accent_light"):
            status, _ = theme_request(endpoint,
                                      {"action": "save", "source": "#0e6e62", field: "x"})
            if status != 400:
                fail("an authority field %r on /api/theme returned %d, expected 400"
                     % (field, status))
    finally:
        proc.terminate()


def check_theme_pick_contract():
    """Test 3: the pick action goes through the tested no-shell
    source/.pyz child bridge (never Tk in the daemon thread), a child
    failure reads as available:false with the exact fallback reason and no
    write, and the settings page keeps its browser color input usable.
    The live child is only driven where it fails fast (headless CI); the
    fail-closed mapping itself is unit-proven in theme_roundtrip.
    """
    import inspect
    src = inspect.getsource(daemon.handle_theme_post)
    if "run_native_picker" not in src:
        fail("handle_theme_post does not delegate pick to launcher.run_native_picker")
    if "subprocess" in src or "Popen" in src:
        fail("handle_theme_post spawns processes directly instead of the launcher bridge")

    workdir = temp_dir_with(bank=True, settings_overrides={"theme": "system"})
    before = settings_bytes(workdir)
    proc, url, lines = start_daemon(workdir)
    try:
        if not native_picker_would_block():
            status, body = theme_request(url + THEME_ROUTE, {"action": "pick"})
            if status != 200:
                fail("pick returned %d, expected 200" % status)
            if body.get("available") is not False:
                fail("a headless pick must read available:false, got %r" % body)
            if body.get("reason") != "System picker is unavailable here. Choose a color below instead.":
                fail("unavailable pick returned the wrong fallback reason: %r" % body)
            if body.get("saved") is not False:
                fail("a native pick must be preview-only until an explicit save")
            if settings_bytes(workdir) != before:
                fail("an unavailable pick wrote itembank.json")
        _, page = get(url + SETTINGS_ROUTE)
        if '<input type="color"' not in page:
            fail("settings page dropped the browser color fallback input")
        if settings_bytes(workdir) != before:
            fail("visiting /settings after a pick attempt wrote itembank.json")
    finally:
        proc.terminate()


def check_theme_route_loopback_and_origin():
    """Test 5: mutation and native-picker actions require a loopback,
    same-origin JSON client; LAN clients may preview but never alter host
    settings or open a host dialog.
    """
    workdir = temp_dir_with(bank=True, settings_overrides={"theme": "system"})
    base = os.path.join(workdir, "itembank.json")
    proc, url, lines = start_daemon(workdir)
    try:
        endpoint = url + THEME_ROUTE
        status, _ = theme_request(endpoint, {"action": "save", "source": "#123abc"},
                                  headers={"Origin": "http://evil.example"})
        if status != 403:
            fail("a cross-origin save returned %d, expected 403" % status)
        if settings_source(workdir) != "#0e6e62":
            fail("a cross-origin save mutated host settings")
        status, _ = theme_request(endpoint, {"action": "save", "source": "#123abc"},
                                  headers={"Origin": url.rstrip("/")})
        if status != 200:
            fail("a same-origin save returned %d, expected 200" % status)
        status, _ = theme_request(endpoint, {"action": "reset", "confirm": "RESET"})
        if status != 200:
            fail("a loopback reset returned %d, expected 200" % status)
        if settings_source(workdir) != "#0e6e62":
            fail("loopback reset did not restore the default")
    finally:
        proc.terminate()

    addr = day.lan_address()
    if addr == "127.0.0.1":
        print("skip: lan_address() returned loopback (no LAN route on this machine) -- "
              "skipping the LAN preview-only theme policy checks")
    else:
        port = free_port()
        workdir = temp_dir_with(bank=True, settings_overrides={"theme": "system"})
        proc, url, lines = start_daemon(workdir, "--lan", "--port", str(port))
        try:
            lan_url = "http://%s:%d/" % (addr, port)
            status, body = theme_request(lan_url + THEME_ROUTE,
                                         {"action": "preview", "source": "#0e6e62"})
            if status != 200 or not body.get("light", {}).get("accent"):
                fail("a LAN preview was refused (status %r, body %r)" % (status, body))
            for action in ({"action": "save", "source": "#123abc"},
                           {"action": "pick"},
                           {"action": "reset", "confirm": "RESET"}):
                status, _ = theme_request(lan_url + THEME_ROUTE, action)
                if status != 403:
                    fail("a LAN %r action returned %d, expected 403" % (action, status))
            if settings_source(workdir) != "#0e6e62":
                fail("a LAN client mutated host settings")
            status, _ = get(lan_url + SETTINGS_ROUTE)
            if status != 200:
                fail("a LAN client could not read the settings page")
        finally:
            proc.terminate()


def check_settings_page_states_and_js():
    """Tests 4 and 6: the page wires `input` to live preview and `change` to
    dirty-save enablement, shows adjusted rendered tokens separately from the
    preserved source before save, and carries loading/save-in-progress/
    save-error/unavailable-picker/reset-confirmation state hooks with focus
    recovery and a persistent status region.
    """
    workdir = temp_dir_with(bank=True, settings_overrides={"theme": "system"})
    proc, url, lines = start_daemon(workdir)
    try:
        status, body = get(url + SETTINGS_ROUTE)
        if status != 200:
            fail("GET %s returned %d, expected 200" % (SETTINGS_ROUTE, status))
        for hook in ('addEventListener("input"', 'addEventListener("change"'):
            if hook not in body:
                fail("settings client is missing the %s wiring hook" % hook)
        if ".focus()" not in body:
            fail("settings client has no focus-recovery call")
        if 'data-rendered' not in body:
            fail("rendered tokens are not shown separately from the preserved source")
        for state_copy in ("Loading", "Save accent", "System picker is unavailable here. "
                           "Choose a color below instead.", "Accessibility details",
                           "Reset accent to the app default? Your current custom source "
                           "color will be replaced."):
            if state_copy not in body:
                fail("settings page is missing the %r state/copy hook" % state_copy)
        for sample in ("Correct", "Incorrect", "Warning", "Selected", "Focus"):
            if sample not in body:
                fail("settings preview samples are missing the %r labelled sample" % sample)
        if 'data-settings-source' not in body:
            fail("settings page lost the draft source input")
    finally:
        proc.terminate()


# ---- startup -- plan 02-06's detect-and-attach probe, the three
# bind-failure cases, `--lan`, and the settings-driven port/LAN defaults.
# The false-positive guard (`check_probe_non_itembank_listener`) is the
# most important assertion in this section: without it, `probe()` could
# return True for anything that answers at all.

def check_probe_closed_port():
    port = free_port()                          # nothing is listening once closed
    if daemon.probe(port, timeout=0.2) is not False:
        fail("probe() on a closed port did not return False")


def check_probe_non_itembank_listener():
    """The false-positive guard: a plain-text 200 and a JSON body missing
    the `itembank` field must both read as False, never True (T-2-08).
    """
    port = free_port()
    decoy = start_decoy(port, body=b"plain text, not itembank", content_type="text/plain")
    try:
        if daemon.probe(port, timeout=0.5) is not False:
            fail("probe() returned True against a plain-text, non-JSON listener")
    finally:
        decoy.shutdown()
        decoy.server_close()

    port = free_port()
    decoy = start_decoy(port, body=json.dumps({"other": True}).encode("utf-8"),
                        content_type="application/json")
    try:
        if daemon.probe(port, timeout=0.5) is not False:
            fail("probe() returned True against JSON lacking the itembank field")
    finally:
        decoy.shutdown()
        decoy.server_close()


def check_probe_real_daemon():
    workdir = tempfile.mkdtemp()
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    port = free_port()
    proc, url, lines = start_daemon(workdir, "--port", str(port))
    try:
        if daemon.probe(port, timeout=1.0) is not True:
            fail("probe() on a real running daemon did not return True")
        status, body = get(url + "__itembank__")
        if status != 200 or json.loads(body) != {"itembank": True}:
            fail("GET /__itembank__ did not return the documented marker shape")
    finally:
        proc.terminate()


def check_startup_second_attaches():
    """A second `itembank daemon` on a port the first holds attaches
    instead of binding: it exits 0, prints the already-running line, prints
    no URL of its own (the free-port fallback line's absence, T-2-20), and
    the first daemon is still the one answering afterward.
    """
    workdir = tempfile.mkdtemp()
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    port = free_port()
    proc, url, lines = start_daemon(workdir, "--port", str(port))
    try:
        code, output = run_daemon_once(
            ["daemon", workdir, "--no-open", "--port", str(port)])
        if code != 0:
            fail("a second daemon on a held port exited %d, expected 0" % code)
        if "itembank is already running at" not in output:
            fail("a second daemon on a held port did not print the already-running "
                 "line: %r" % output)
        # The "already running" line itself names a URL; what must be
        # absent is `serve_scoped()`'s own banner line, printed only once a
        # socket has actually been bound.
        if re.search(r"(?m)^\s*url\s+http://127\.0\.0\.1:\d+/", output):
            fail("a second daemon on a held port printed serve_scoped()'s own url "
                 "line -- it bound a socket instead of attaching: %r" % output)

        status, body = get(url + "__itembank__")
        if status != 200 or json.loads(body) != {"itembank": True}:
            fail("the first daemon stopped answering after a second start attempt")
    finally:
        proc.terminate()


def check_startup_squatter_falls_back():
    """A configured port held by a non-itembank listener falls back to a
    free port and serves successfully there, rather than hard-failing --
    the flagged planner_assumption this case pins down.
    """
    workdir = tempfile.mkdtemp()
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    port = free_port()
    decoy = start_decoy(port)
    try:
        proc, url, lines = start_daemon(workdir, "--port", str(port))
        try:
            output = "".join(lines)
            if ("http://127.0.0.1:%d/" % port) in output:
                fail("the daemon bound the squatted port instead of falling back")
            status, _ = get(url)
            if status != 200:
                fail("the daemon did not start successfully after falling back from "
                     "a squatted port: GET / returned %d" % status)
        finally:
            proc.terminate()
    finally:
        decoy.shutdown()
        decoy.server_close()


def check_startup_loopback_by_default():
    workdir = tempfile.mkdtemp()
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    proc, url, lines = start_daemon(workdir)
    try:
        if not url.startswith("http://127.0.0.1:"):
            fail("the default daemon banner does not show a loopback URL: %r" % url)
        if "phone" in "".join(lines).lower():
            fail("a daemon started without --lan printed a phone line")
    finally:
        proc.terminate()


def check_startup_lan_binds_all():
    """`--lan` binds all interfaces and the banner carries both the
    loopback URL and a phone line. Cross-device reachability itself is a
    manual check (02-VALIDATION.md); this proves the bind widened, by
    reaching the LAN address from this same machine.
    """
    workdir = tempfile.mkdtemp()
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    port = free_port()
    proc, url, lines = start_daemon(workdir, "--lan", "--port", str(port))
    try:
        output = "".join(lines)
        if "http://127.0.0.1:" not in output:
            fail("a --lan daemon's banner is missing the loopback URL")
        addr = day.lan_address()
        if addr == "127.0.0.1":
            print("skip: lan_address() returned loopback (no LAN route on this "
                 "machine) -- skipping the phone-line and cross-interface checks")
        else:
            if ("phone   http://%s:%d/" % (addr, port)) not in output:
                fail("a --lan daemon's banner is missing the phone line: %r" % output)
            status, _ = get("http://%s:%d/" % (addr, port))
            if status != 200:
                fail("a --lan daemon did not answer on its LAN address")
    finally:
        proc.terminate()


def check_lan_path_validation_unchanged():
    """`--lan` widens who can reach the routes, never what a request may
    name -- two of plan 02-04's hostile cases still return the same 4xx
    under a `--lan` daemon.
    """
    workdir = tempfile.mkdtemp()
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    port = free_port()
    proc, url, lines = start_daemon(workdir, "--lan", "--port", str(port))
    try:
        try:
            post(url + "api/start", {"bank": "../../etc/passwd", "count": 1})
            fail("a path-shaped bank field was accepted by a --lan daemon")
        except urllib.error.HTTPError as exc:
            if exc.code < 400 or exc.code >= 500:
                fail("a path-shaped bank field on a --lan daemon returned HTTP %d, "
                     "expected 4xx" % exc.code)
        try:
            post(url + "api/next", {"session_id": "no-such-session-id"})
            fail("an unknown session_id was accepted by a --lan daemon")
        except urllib.error.HTTPError as exc:
            if exc.code != 404:
                fail("an unknown session_id on a --lan daemon returned HTTP %d, "
                     "expected 404" % exc.code)
    finally:
        proc.terminate()


def check_settings_driven_port():
    """With no `--port` given at all, the daemon binds `itembank.json`'s own
    `daemon.port` -- the settings group this plan makes live, proven
    against a temp `--base` rather than the repo's own shipped file.
    """
    workdir = tempfile.mkdtemp()
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    port = free_port()
    subprocess.run(
        [sys.executable, "-u", os.path.join(ROOT, "itembank.py"), "config", "set",
         "daemon.port", str(port), "--base", workdir],
        check=True, capture_output=True, text=True)
    proc, url, lines = start_daemon(workdir, force_port_zero=False)
    try:
        if url != "http://127.0.0.1:%d/" % port:
            fail("with no --port given, the daemon did not bind the settings-driven "
                 "port %d: bound %r instead" % (port, url))
    finally:
        proc.terminate()


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
        check_day_edit_route,
        check_day_edit_conflict_and_force,
        check_route_cli_inventory,
        check_api_route_scope,
        check_api_sitting,
        check_api_duplicate_submit_dedupes,
        check_api_survives_routine_error,
        check_api_bank_not_found,
        check_api_start_traversal,
        check_api_reject_path_fields,
        check_served_api_flow,
        check_api_forged_fields,
        check_serve_attempt_refresh,
        check_wave0_helpers,
        check_api_malformed_json,
        check_api_cli_parity,
        check_report_populated,
        check_report_matches_command,
        check_report_empty,
        check_report_in_progress,
        check_report_zero_auto_marked,
        check_report_objective_rows_one_and_many,
        check_report_not_found,
        check_report_no_truncation,
        check_settings_page,
        check_theme_route_contract,
        check_theme_pick_contract,
        check_theme_route_loopback_and_origin,
        check_settings_page_states_and_js,
        check_probe_closed_port,
        check_probe_non_itembank_listener,
        check_probe_real_daemon,
        check_startup_second_attaches,
        check_startup_squatter_falls_back,
        check_startup_loopback_by_default,
        check_startup_lan_binds_all,
        check_lan_path_validation_unchanged,
        check_settings_driven_port,
    )
    for check in checks:
        check()
    print("ok: daemon served %d checks -- index, quiz, answer scoring, cross-bank "
          "isolation, stem collisions, the route/CLI inventory, the /api/* session "
          "routes, the /report page, and the detect-and-attach startup path all held"
          % len(checks))
    return 0


if __name__ == "__main__":
    sys.exit(main())
