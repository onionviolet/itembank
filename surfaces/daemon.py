"""One process, one port, one ordered route table.

Every earlier surface bound its own socket: `serve` for a sitting, `day` for
the cockpit, `study` for flashcards, and a static `build` page with nothing
behind it at all. That duplication is the point this module removes.
`DaemonHandler` is the one `server.Handler` subclass this phase adds; `ROUTES`
is the one ordered table every request walks; every route handler resolves
its identifier through a startup-built allowlist and then calls into the
render and runtime functions that already exist -- `quiz.page_for()`,
`quiz.record_answer()`, `study.study_page()`, `day.day_render()`,
`day.apply_day_post()`, `runtime.score_response()` (by way of
`record_answer`), `evidence.append_event()` (by way of `record_answer` and
`apply_day_post`) -- never a second copy of any of them living in a route
handler.
"""
import datetime, html, os, re, socketserver, sys, threading, urllib.parse, uuid, webbrowser

import evidence
import server
from model import load, parse_bank
from runtime import explain_payload
from surfaces import day, quiz, study
from surfaces.theme import THEME_CSS


MARKER_PATH = "/__itembank__"

# Same directories `cmd_guard` skips, plus the two this daemon itself writes
# into -- neither an attempt file nor the evidence log is ever a candidate
# bank or day plan.
SKIP_DIRS = {".git", ".github", "_attempts", "_evidence"}

QUIZ_GET_RE = re.compile(r"^/quiz/(?P<stem>[^/]+)$")
QUIZ_ANSWER_RE = re.compile(r"^/quiz/(?P<stem>[^/]+)/answer$")
STUDY_GET_RE = re.compile(r"^/study/(?P<stem>[^/]+)$")
DAY_GET_RE = re.compile(r"^/day/(?P<stem>[^/]+)$")
DAY_SAVE_RE = re.compile(r"^/day/(?P<stem>[^/]+)/save$")
DAY_OPEN_RE = re.compile(r"^/day/(?P<stem>[^/]+)/open$")

# Order is load-bearing: every fixed literal route comes before every
# stem-parameterised route, so a bank or plan whose stem happens to be
# "report", "day" or "api" can never shadow a fixed route. Dispatch is
# first-match-wins over this tuple, walked in order by
# `DaemonHandler._dispatch`. `/day` is the one fixed route with plan-scoped
# siblings (`/day/<stem>`, `/day/<stem>/save`, `/day/<stem>/open`); it is
# ordered ahead of them for the same reason.
ROUTES = (
    ("GET", "/", "handle_index"),
    ("GET", MARKER_PATH, "handle_marker"),
    ("GET", "/day", "handle_day_index"),
    ("GET", QUIZ_GET_RE, "handle_quiz_get"),
    ("POST", QUIZ_ANSWER_RE, "handle_quiz_answer"),
    ("GET", STUDY_GET_RE, "handle_study_get"),
    ("GET", DAY_GET_RE, "handle_day_get"),
    ("POST", DAY_SAVE_RE, "handle_day_save"),
    ("POST", DAY_OPEN_RE, "handle_day_open"),
)

# Every route in ROUTES has a CLI command that reaches the same runtime
# call -- SURF-04's "every route has a CLI equivalent" as a machine-checkable
# inventory instead of a claim in prose. The key set here is asserted equal
# to ROUTES' (method, pattern) pairs, so a route added without an entry here
# fails the build instead of shipping silently.
ROUTE_CLI = {
    ("GET", "/"): "daemon",
    ("GET", MARKER_PATH): "daemon",
    ("GET", QUIZ_GET_RE): "serve",
    ("POST", QUIZ_ANSWER_RE): "serve",
    ("GET", STUDY_GET_RE): "study",
    ("GET", "/day"): "day",
    ("GET", DAY_GET_RE): "day",
    ("POST", DAY_SAVE_RE): "day",
    ("POST", DAY_OPEN_RE): "day",
}


def scan_dir(root):
    """Walk `root` once and classify every `.md` file as a bank, a day plan,
    or neither.

    This is the startup-built allowlist every route resolves a client-
    supplied stem through -- a handler never joins a client string onto a
    filesystem path (T-2-01). `parse_bank()` returning a non-empty list
    means bank; otherwise `surfaces.day.parse_plan()` returning a non-empty
    dict means day plan; otherwise the file is skipped silently, the same
    graceful-empty-list classification `cmd_guard` already relies on.

    Candidates are iterated in case-insensitive stem order (broken by full
    path for files that tie), so the winner of a stem collision is
    deterministic across restarts. Returns `(banks, plans, collisions)`,
    the first two keyed by filename stem, `collisions` a list of
    `(stem, winner_path, loser_path)`.
    """
    candidates = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name.lower().endswith(".md"):
                candidates.append(os.path.join(dirpath, name))
    candidates.sort(key=lambda p: (os.path.splitext(os.path.basename(p))[0].lower(), p))

    year = datetime.date.today().year
    banks, plans, collisions = {}, {}, []
    winners = {}                                # lower stem -> winning path
    for path in candidates:
        stem = os.path.splitext(os.path.basename(path))[0]
        stem_key = stem.lower()
        text = open(path, encoding="utf-8").read()
        qs = parse_bank(text)
        if qs:
            kind, table = "bank", banks
        else:
            plan = day.parse_plan(path, year)
            if not plan:
                continue                        # neither a bank nor a plan; skip silently
            kind, table = "plan", plans
        if stem_key in winners:
            collisions.append((stem, winners[stem_key], path))
            continue
        winners[stem_key] = path
        table[stem] = path
    return banks, plans, collisions


NOT_FOUND_BODY = (
    '<!doctype html><html lang="en"><head><meta charset="utf-8">'
    "<title>Not found</title></head><body><h1>Not found</h1>"
    "<p>No bank or session matching &quot;%s&quot; is being served from this "
    "daemon. It may have been renamed, or the daemon was started in a "
    "different folder.</p></body></html>"
)

# `GET /day`'s defined behaviour for the ambiguous case (D-08's plan): with
# zero or with two-or-more plans scanned there is no single answer for
# "the" day plan, so this is the documented outcome rather than a guess at
# which one the client meant. Carries no filesystem path (T-2-05).
DAY_AMBIGUOUS_BODY = (
    '<!doctype html><html lang="en"><head><meta charset="utf-8">'
    "<title>Not found</title></head><body><h1>Not found</h1>"
    "<p>%s day plan%s scanned from this daemon, so <code>/day</code> alone is "
    'ambiguous. Visit <a href="/">/</a> and open the plan you want by name '
    "instead.</p></body></html>"
)

EMPTY_STATE = """<div class="empty">
  <h2>Nothing to serve here yet</h2>
  <p>This daemon serves whatever bank and day-plan files it found in __DIR__
  when it started. Add a bank (any .md file with items) or a day plan, then
  restart the daemon.</p>
</div>"""

BANK_ROW = """<div class="row">
  <div class="name">__STEM__</div>
  <div class="links">
    <a href="/quiz/__STEM__">Sit this bank</a>
    <a href="/study/__STEM__">Study this bank</a>
  </div>
</div>"""

PLAN_ROW = """<div class="row">
  <div class="name">__STEM__</div>
  <div class="links">
    <a href="/day/__STEM__">Open day view</a>
  </div>
</div>"""

# Genuinely new HTML with no existing render function to call into -- the
# 8-point spacing scale, the four font sizes and the __THEME__ substitution
# convention `quiz.page_for()` already uses, per 02-UI-SPEC.md. Row link
# text is left to wrap naturally: no `white-space:nowrap`, no ellipsis
# truncation anywhere in this stylesheet. Rows are a plain vertical list in
# ordinary document flow -- no max-height, no scroll container -- so any
# number of rows scrolls with the page.
INDEX_TEMPLATE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>itembank</title>
<style>
__THEME__
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font:16px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
.wrap{max-width:800px;margin:0 auto;padding:64px 24px}
h1{font-size:21px;font-weight:700;margin:0 0 32px}
.empty h2{font-size:21px;font-weight:700;margin:0 0 16px}
.empty p{color:var(--mut);font-size:16px}
.row{background:var(--card);border:1px solid var(--line);border-radius:8px;
  padding:16px;margin-bottom:24px}
.row .name{font-size:16px;font-weight:700;overflow-wrap:anywhere}
.row .links{margin-top:8px;display:flex;gap:16px;flex-wrap:wrap;font-size:12.5px}
.row a{color:var(--accent)}
.row a:hover,.row a:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
</style></head><body><div class="wrap">
<h1>itembank</h1>
__BODY__
</div></body></html>"""


def handle_index(handler):
    """`GET /` -- the index of every bank and day plan this daemon found at
    startup. No HTML is generated anywhere else; this is the one function
    that authors it, following `quiz.page_for()`'s substitution convention.
    """
    banks, plans = handler.banks, handler.plans
    stems = sorted(set(banks) | set(plans), key=str.lower)
    if stems:
        rows = []
        for stem in stems:
            esc = html.escape(stem)
            row = BANK_ROW if stem in banks else PLAN_ROW
            rows.append(row.replace("__STEM__", esc))
        body = "\n".join(rows)
    else:
        served_dir = html.escape(os.path.abspath(handler.root))
        body = EMPTY_STATE.replace("__DIR__", served_dir)
    page = INDEX_TEMPLATE.replace("__THEME__", THEME_CSS).replace("__BODY__", body)
    handler.send_html(page.encode("utf-8"))


def handle_marker(handler):
    """`GET /__itembank__` -- the identifying response plan 02-06's
    detect-and-attach probe looks for.
    """
    handler.send_json({"itembank": True})


def handle_quiz_get(handler, stem):
    """`GET /quiz/<stem>` -- the quiz page for one bank, resolved through the
    startup allowlist and rendered by the existing `quiz.page_for()`. No key
    data is sent: `serve=True` is what makes `page_for` omit it.
    """
    path = handler.banks.get(stem)
    if path is None:
        handler.send_not_found(stem)
        return
    qs = load(path)
    _, page = quiz.page_for(path, qs, serve=True, reveal=False,
                            post_path="/quiz/%s/answer" % stem)
    handler.send_html(page.encode("utf-8"))


def handle_quiz_answer(handler, stem):
    """`POST /quiz/<stem>/answer` -- score and record one response against
    the one bank the client's stem resolves to. This function never calls
    `score_response` or `evidence.append_event` directly; it goes through
    `quiz.record_answer`, which keeps "one scorer, one writer" structural
    rather than remembered.

    `reveal` (whether `explain_payload` returns the short-item model answer)
    and `progress` (whether to write the "d/N answered, saved" progress line
    `cmd_serve` used to write from its own closure) both come off the bank's
    session dict, defaulting to off -- a general multi-bank daemon launch
    never sets either, so its behaviour is unchanged; `cmd_serve`'s scoped
    launch sets both through `serve_scoped`'s `extra`.
    """
    path = handler.banks.get(stem)
    if path is None:
        handler.send_not_found(stem)
        return
    try:
        qs = load(path)
        by_id = dict((q["id"], q) for q in qs)
        data = handler.read_json()
        q = by_id.get(data.get("id"))
        if q is None:
            handler.send_error(404, "no item %r in this bank" % data.get("id"))
            return
        elapsed_ms = data.get("elapsed_ms")
        if not isinstance(elapsed_ms, int) or isinstance(elapsed_ms, bool):
            # Absent, non-integer, or an older cached page that never sent
            # the field at all: record an honest null rather than a
            # fabricated number, matching `cmd_serve`'s own type guard.
            elapsed_ms = None
        sess = handler.sessions[stem]
        size_before = os.path.getsize(sess["log"]) if os.path.exists(sess["log"]) else -1
        score = quiz.record_answer(path, qs, sess["session_id"], sess["log"], sess["out"],
                                   sess["mode"], q, data.get("response"), elapsed_ms)
        if sess.get("progress"):
            # The only feedback a learner sitting `itembank serve` gets that
            # an answer was actually written to disk -- preserved from the
            # closure `cmd_serve` used to hold before it lost its own
            # handler class.
            already = size_before >= 0 and os.path.getsize(sess["log"]) == size_before
            answered = len(set(ev["item_ref"]
                               for ev in evidence.session_events(sess["log"], sess["session_id"])))
            note = " (already recorded)" if already else ""
            sys.stdout.write("\r  %d/%d answered, saved%s" % (answered, len(qs), note))
            sys.stdout.flush()
            if answered >= len(qs):
                print("\n  finished. Attempt file: %s" % sess["out"])
        payload = {"item_id": q["id"], "score": score,
                   "explain": explain_payload(q, sess.get("reveal", False))}
    except Exception as exc:                    # never let a bad POST kill the daemon
        handler.send_error(500, str(exc))
        return
    handler.send_json(payload)


def handle_study_get(handler, stem):
    """`GET /study/<stem>` -- the flashcard/Learn page for one bank, resolved
    through the startup allowlist and rendered by `study.study_page()`. No
    second copy of the study template lives here.
    """
    path = handler.banks.get(stem)
    if path is None:
        handler.send_not_found(stem)
        return
    qs = load(path)
    page = study.study_page(path, qs)
    handler.send_html(page.encode("utf-8"))


def _plan_day_state(handler, stem):
    """Get or lazily build this plan's `day.day_state`, cached on the
    handler class so ticks accumulate across requests exactly as they did
    within one `cmd_day` process (T-2-12). The log/lanes paths default to
    beside the plan file, the same defaulting `cmd_day` does when `--log`/
    `--lanes` are not given, and `iso` defaults to today -- unless
    `day_extra` (set by `cmd_day`'s scoped launch through `serve_scoped`)
    names an override for this stem, which is how `itembank day --date`
    (backfilling a missed day) still works once `day` is a daemon launch.
    """
    state = handler.day_states.get(stem)
    if state is not None:
        return state
    path = handler.plans[stem]
    plan_dir = os.path.dirname(os.path.abspath(path)) or "."
    override = handler.day_extra.get(stem, {})
    log_path = override.get("log_path") or os.path.join(plan_dir, "daily_log.md")
    lanes_path = override.get("lanes_path") or os.path.join(plan_dir, "lanes.md")
    iso = override.get("iso") or datetime.date.today().isoformat()
    state = day.day_state(path, log_path, lanes_path, iso, base="/day/%s" % stem)
    handler.day_states[stem] = state
    return state


def handle_day_get(handler, stem):
    """`GET /day/<stem>` -- one plan's cockpit, rendered by `day.day_render()`
    with its own plan-scoped `base` so the page's own POSTs come back to
    this same stem (T-2-12).
    """
    if stem not in handler.plans:
        handler.send_not_found(stem)
        return
    state = _plan_day_state(handler, stem)
    handler.send_html(day.day_render(state))


def handle_day_index(handler):
    """`GET /day` -- serves the sole scanned plan when exactly one exists;
    the ambiguous case (zero, or two-or-more) is the documented 404 rather
    than a guess at which plan the client meant.
    """
    if len(handler.plans) == 1:
        (stem,) = handler.plans
        handle_day_get(handler, stem)
        return
    n = len(handler.plans)
    body = DAY_AMBIGUOUS_BODY % ("No" if n == 0 else str(n), "" if n == 1 else "s")
    handler.send_bytes(body.encode("utf-8"), "text/html; charset=utf-8", status=404)


def handle_day_save(handler, stem):
    """`POST /day/<stem>/save` -- one plan's tick save, through
    `day.apply_day_post()`. Never calls `evidence.append_event()` or
    `evidence.render_daily_log()` directly (T-2-11, T-2-12).
    """
    if stem not in handler.plans:
        handler.send_not_found(stem)
        return
    try:
        state = _plan_day_state(handler, stem)
        data = handler.read_json()
        result = day.apply_day_post(state, "save", data)
    except Exception as exc:                    # never let a bad POST kill the daemon
        handler.send_error(500, str(exc))
        return
    handler.send_json(result)


def handle_day_open(handler, stem):
    """`POST /day/<stem>/open` -- one plan's "open in editor", through
    `day.apply_day_post()`. An out-of-range `(lane, index)` comes back as
    `None`, which this handler alone turns into a 404 (T-2-10) --
    `apply_day_post` has no `self` to call `send_error` on.
    """
    if stem not in handler.plans:
        handler.send_not_found(stem)
        return
    try:
        state = _plan_day_state(handler, stem)
        data = handler.read_json()
        result = day.apply_day_post(state, "open", data)
    except Exception as exc:                    # never let a bad POST kill the daemon
        handler.send_error(500, str(exc))
        return
    if result is None:
        handler.send_error(404)
        return
    handler.send_json(result)


class DaemonHandler(server.Handler):
    """The one `Handler` subclass this phase adds. Its state -- the
    `banks`/`plans` allowlists, the served root, and each bank's session
    bookkeeping -- is set as class attributes by `cmd_daemon` before the
    server starts, the same closure-over-startup-state shape `cmd_serve`
    used before consolidation.
    """
    banks = {}
    plans = {}
    collisions = []
    root = "."
    sessions = {}
    day_states = {}
    day_extra = {}

    def send_not_found(self, name):
        """The documented not-found copy: the stem the client asked for and
        nothing else. Never a served directory, an absolute path, or a
        traceback (T-2-05).
        """
        body = NOT_FOUND_BODY % html.escape(name)
        self.send_bytes(body.encode("utf-8"), "text/html; charset=utf-8", status=404)

    def _dispatch(self):
        path = urllib.parse.urlsplit(self.path).path
        for method, pattern, handler_name in ROUTES:
            if method != self.command:
                continue
            if isinstance(pattern, str):
                if path != pattern:
                    continue
                kwargs = {}
            else:
                m = pattern.match(path)
                if not m:
                    continue
                kwargs = m.groupdict()
            globals()[handler_name](self, **kwargs)
            return
        self.send_error(404)

    def do_GET(self):
        self._dispatch()

    def do_POST(self):
        self._dispatch()


class Daemon(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """One process now serves quiz, study, day and api concurrently, and
    `day`'s AnkiConnect calls carry a two-second timeout per lane -- a plain
    single-threaded server would let one slow render stall every other
    route (RESEARCH.md Pitfall #4).
    """
    daemon_threads = True
    allow_reuse_address = True


def _bind(port, host="127.0.0.1"):
    """The same free-port fallback `server.bind()` already implements,
    applied to `Daemon` instead of `socketserver.TCPServer` -- `server.bind()`
    itself constructs a fixed server class, so this mirrors its logic rather
    than widening that module's scope outside this plan.
    """
    try:
        return Daemon((host, port), DaemonHandler)
    except OSError as exc:
        print("  port %d unavailable (%s), using a free one instead"
              % (port, exc.__class__.__name__))
        return Daemon((host, 0), DaemonHandler)


def serve_scoped(root, banks, plans, port, host="127.0.0.1", open_path="/",
                 no_open=False, extra=None, on_bound=None):
    """Bind the one `Daemon`/`DaemonHandler` pair, scoped to whatever
    `banks` and `plans` a caller passes in, print the URL line, optionally
    open a browser after the same 0.4-second timer every launch has always
    used, and run `serve_forever()` inside the `KeyboardInterrupt` guard --
    the tail every daemon launch shares now, whether it is `cmd_daemon`
    scanning a whole directory or `cmd_serve`/`cmd_day` scoped to the single
    bank or plan they were pointed at. This is the whole of what "`serve`
    and `day` become daemon launches" means: after this function exists,
    binding a socket happens in exactly one place in the codebase.

    `extra` carries whatever a caller needs pinned onto the handler class
    the same way `banks`/`plans` are: `sessions` (bank stem -> session
    bookkeeping, including the `reveal`/`progress` flags `handle_quiz_answer`
    reads), `collisions` (`scan_dir`'s collision list, empty for a scoped
    single-bank/single-plan launch), and `day_extra` (plan stem ->
    `{"log_path", "lanes_path"}` overrides for `--log`/`--lanes`).

    `on_bound(port)`, if given, runs right after the URL line is printed --
    the caller's chance to print anything that needs the actual bound port
    (`cmd_day`'s `--lan` phone address) followed by its own final line
    before the browser timer starts and `serve_forever()` takes over.
    """
    extra = extra or {}
    DaemonHandler.banks = banks
    DaemonHandler.plans = plans
    DaemonHandler.collisions = extra.get("collisions", [])
    DaemonHandler.root = root
    DaemonHandler.sessions = extra.get("sessions", {})
    DaemonHandler.day_states = {}                  # built lazily, one per served plan
    DaemonHandler.day_extra = extra.get("day_extra", {})

    srv = _bind(port, host)
    with srv:
        bound_port = srv.server_address[1]
        display_host = "127.0.0.1" if host in ("0.0.0.0", "127.0.0.1") else host
        url = "http://%s:%d%s" % (display_host, bound_port, open_path)
        print("  url     %s" % url)
        if on_bound:
            on_bound(bound_port)
        sys.stdout.flush()
        if not no_open:
            threading.Timer(0.4, lambda: webbrowser.open(url)).start()
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped.")
    return bound_port


def cmd_daemon(a):
    root = a.dir
    banks, plans, collisions = scan_dir(root)

    print("itembank daemon")
    print("  dir     %s" % os.path.abspath(root))
    print("  banks   %d" % len(banks))
    print("  plans   %d" % len(plans))
    for stem, winner, loser in collisions:
        print("  collision  stem %r: %s wins, %s loses" % (stem, winner, loser))

    # One session per bank, opened for the life of this process -- the same
    # session-id-printed-so-a-marker-can-find-it precedent `cmd_serve` sets,
    # extended to every bank this daemon found rather than the one bank a
    # single `serve` process used to hold.
    sessions = {}
    for stem, path in banks.items():
        bank_dir = os.path.dirname(os.path.abspath(path)) or "."
        out = os.path.join(bank_dir, "_attempts", "%s_attempt_%s.md" %
                           (stem, datetime.datetime.now().strftime("%Y-%m-%d_%H%M")))
        os.makedirs(os.path.dirname(out), exist_ok=True)
        sessions[stem] = {
            "session_id": uuid.uuid4().hex,
            "log": evidence.log_path(bank_dir),
            "out": out,
            "mode": "practice",
        }

    serve_scoped(root, banks, plans, a.port, open_path="/", no_open=a.no_open,
                extra={"sessions": sessions, "collisions": collisions})
    return 0
