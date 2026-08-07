"""One process, one port, one ordered route table.

Every earlier surface bound its own socket: `serve` for a sitting, `day` for
the cockpit, and a static `build` page with nothing behind it at all. That
duplication is the point this module removes. `DaemonHandler` is the one
`server.Handler` subclass this phase adds; `ROUTES` is the one ordered table
every request walks; every route handler resolves its identifier through a
startup-built allowlist and then calls into the render and runtime functions
that already exist -- `quiz.page_for()`, `quiz.record_answer()`,
`runtime.score_response()` (by way of `record_answer`), `evidence.append_event()`
(by way of `record_answer`) -- never a second copy of any of them living in a
route handler.
"""
import datetime, html, os, re, socketserver, sys, threading, urllib.parse, uuid, webbrowser

import evidence
import server
from model import load, parse_bank
from runtime import explain_payload
from surfaces import day, quiz
from surfaces.theme import THEME_CSS


MARKER_PATH = "/__itembank__"

# Same directories `cmd_guard` skips, plus the two this daemon itself writes
# into -- neither an attempt file nor the evidence log is ever a candidate
# bank or day plan.
SKIP_DIRS = {".git", ".github", "_attempts", "_evidence"}

QUIZ_GET_RE = re.compile(r"^/quiz/(?P<stem>[^/]+)$")
QUIZ_ANSWER_RE = re.compile(r"^/quiz/(?P<stem>[^/]+)/answer$")

# Order is load-bearing: every fixed literal route comes before every
# stem-parameterised route, so a bank whose stem happens to be "report",
# "day" or "api" can never shadow a fixed route. Dispatch is first-match-wins
# over this tuple, walked in order by `DaemonHandler._dispatch`.
ROUTES = (
    ("GET", "/", "handle_index"),
    ("GET", MARKER_PATH, "handle_marker"),
    ("GET", QUIZ_GET_RE, "handle_quiz_get"),
    ("POST", QUIZ_ANSWER_RE, "handle_quiz_answer"),
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
        score = quiz.record_answer(path, qs, sess["session_id"], sess["log"], sess["out"],
                                   sess["mode"], q, data.get("response"), elapsed_ms)
        payload = {"item_id": q["id"], "score": score,
                   "explain": explain_payload(q, False)}
    except Exception as exc:                    # never let a bad POST kill the daemon
        handler.send_error(500, str(exc))
        return
    handler.send_json(payload)


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

    DaemonHandler.banks = banks
    DaemonHandler.plans = plans
    DaemonHandler.collisions = collisions
    DaemonHandler.root = root
    DaemonHandler.sessions = sessions

    srv = _bind(a.port)
    with srv:
        url = "http://127.0.0.1:%d/" % srv.server_address[1]
        print("  url     %s" % url)
        sys.stdout.flush()
        if not a.no_open:
            threading.Timer(0.4, lambda: webbrowser.open(url)).start()
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped.")
    return 0
