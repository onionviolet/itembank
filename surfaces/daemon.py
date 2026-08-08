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
import datetime, errno, html, json, os, re, socketserver, sys, threading
import urllib.parse, urllib.request, uuid

import evidence
import server
from model import load, parse_bank
from runtime import explain_payload, read_session
from surfaces import day, launcher, quiz, session, settings, study
from surfaces.theme import THEME_CSS


MARKER_PATH = "/__itembank__"

# The one place that chooses whether the daemon speaks to just this machine
# or to the whole local network -- every other spot in this module that
# needs to know reads this constant rather than repeating the literal, so
# "how many places decide the bind host" stays a one-line answer instead of
# a claim to trust (checked by this plan's own acceptance criteria).
ALL_INTERFACES = "0.0.0.0"

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

# The four `/api/*` session routes D-04 scopes for this phase. Fixed
# literals, not stem-parameterised: a session or a bank is addressed by an
# opaque identifier in the JSON body (T-2-01), never by a path segment, so
# there is no `<stem>`/`<id>` group in any of these patterns at all. The
# four-entry length is asserted by `check_api_route_scope` in
# `tests/daemon_roundtrip.py` and by this plan's own acceptance criteria --
# the browser-holds-no-key rework that would want more of them is Phase 4's
# SURF-02 job, not this one.
API_ROUTES = (
    ("POST", "/api/start", "handle_api_start"),
    ("POST", "/api/next", "handle_api_next"),
    ("POST", "/api/submit", "handle_api_submit"),
    ("POST", "/api/report", "handle_api_report"),
)

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
    ("GET", "/report", "handle_report_get"),
) + API_ROUTES + (
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
    ("GET", "/report"): "report",
    ("POST", "/api/start"): "start",
    ("POST", "/api/next"): "next",
    ("POST", "/api/submit"): "submit",
    ("POST", "/api/report"): "report",
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
        try:
            text = open(path, encoding="utf-8").read()
        except (OSError, UnicodeDecodeError):
            continue                            # unreadable or not UTF-8; skip silently
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
    <a href="/study/__STEM__">Study this bank</a>__REPORT_LINK__
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

# The other genuinely new page this phase authors -- no existing render
# function to call into, per RESEARCH.md Open Question 2. Follows
# INDEX_TEMPLATE's own `str.replace()` substitution convention (`__THEME__`,
# `__TITLE__`, `__BODY__`) so the daemon's two new pages read as one family.
# Same 8-point spacing scale, the same four font sizes (12.5/16/21/34) and
# the same 60/30/10 color split as the index -- `--accent` reserved for the
# headline score number and for link hover/focus rings, nothing else. Table
# and figure cells wrap (`overflow-wrap:anywhere`); no `white-space:nowrap`
# and no `text-overflow` ellipsis anywhere in this stylesheet, matching the
# index's own no-truncation rule. The objective table sits in ordinary
# document flow -- no max-height, no scroll container -- so a session with
# many pending items scrolls with the page (the overflow backstop this
# plan's must_haves carries).
REPORT_TEMPLATE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>
__THEME__
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font:16px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
.wrap{max-width:800px;margin:0 auto;padding:64px 24px}
h1{font-size:21px;font-weight:700;margin:0 0 32px}
.empty h2{font-size:21px;font-weight:700;margin:0 0 16px}
.empty p{color:var(--mut);font-size:16px}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;
  padding:24px;margin-bottom:24px}
.headline{font-size:34px;font-weight:700;color:var(--accent);line-height:1.1}
.headline-label{font-size:12.5px;color:var(--mut);margin:4px 0 0}
.status{font-size:12.5px;color:var(--mut);margin:16px 0 0}
.figures{display:flex;gap:32px;flex-wrap:wrap;margin-top:24px}
.figure-value{font-size:21px;font-weight:700}
.figure-label{font-size:12.5px;color:var(--mut);margin-top:4px}
table{width:100%;border-collapse:collapse;margin-top:8px}
th,td{text-align:left;padding:8px;border-bottom:1px solid var(--line);
  font-size:16px;overflow-wrap:anywhere}
th{font-size:12.5px;color:var(--mut);font-weight:700}
</style></head><body><div class="wrap">
<h1>itembank report</h1>
__BODY__
</div></body></html>"""

# The documented empty-state copy (Copywriting Contract), rendered instead
# of a report table with all-zero or blank cells whenever a session has
# recorded neither an auto-marked response nor a pending-manual one.
REPORT_EMPTY = """<div class="empty">
  <h2>Nothing answered yet</h2>
  <p>This session hasn't recorded a response. Sit the bank, then refresh
  this report.</p>
</div>"""


def _report_figure(field, value, label):
    """One labelled figure (`data-field` names which of `session_summary()`'s
    three top-level counts it carries) -- a stable marker
    `check_api_cli_parity`-style page-versus-command tests can regex against
    instead of scraping prose that copywriting could change later.
    """
    return ('<div class="figure" data-field="%s"><div class="figure-value">%d</div>'
            '<div class="figure-label">%s</div></div>'
            % (field, value, html.escape(label)))


def _report_objective_rows(objectives):
    """One `<tr>` per entry in `summary["objectives"]`, sorted by name for a
    deterministic render -- the same row markup at one objective as at many
    (no count sentence, no singular/plural branch). Objective names come
    from bank content and are HTML-escaped before they reach the page.
    """
    rows = []
    for name in sorted(objectives):
        bucket = objectives[name]
        rows.append(
            "<tr><td>%s</td><td>%d</td><td>%d</td><td>%d</td></tr>"
            % (html.escape(name), bucket["attempts"], bucket["correct"], bucket["pending"]))
    return "\n".join(rows)


def _report_card(summary, status, position=None, total=None):
    """The populated/in-progress body: the headline auto-marked accuracy,
    the three labelled figures, and the per-objective table -- one render
    for both states, distinguished only by whether a progress line is
    present. All arithmetic here is `summary`'s own fields (`session_summary()`'s
    output); no count is recomputed from a responses list.
    """
    attempts = summary["auto_attempts"]
    correct = summary["auto_correct"]
    pending = summary["pending_manual"]
    # Mirrors quiz_page.py's finish() guard (`pct = autoTotal ? Math.round(...) : 0`)
    # so a session with zero auto-marked responses (e.g. every item is
    # `short`) renders 0, never a ZeroDivisionError and never NaN.
    pct = round(correct / attempts * 100) if attempts else 0
    figures = "".join((
        _report_figure("auto_attempts", attempts, "auto-marked"),
        _report_figure("auto_correct", correct, "correct"),
        _report_figure("pending_manual", pending, "pending manual"),
    ))
    progress = ""
    if status == "active" and position is not None and total is not None:
        progress = ('<p class="status" data-field="progress">In progress -- '
                     '%d of %d items answered so far.</p>' % (position, total))
    rows = _report_objective_rows(summary["objectives"])
    return (
        '<div class="card" data-status="%s">'
        '<div class="headline" data-field="pct">%d%%</div>'
        '<p class="headline-label">auto-marked accuracy</p>'
        '%s'
        '<div class="figures">%s</div>'
        '</div>'
        '<table><thead><tr><th>Objective</th><th>Attempts</th>'
        '<th>Correct</th><th>Pending</th></tr></thead>'
        '<tbody>%s</tbody></table>'
        % (html.escape(status), pct, progress, figures, rows))


def handle_report_get(handler):
    """`GET /report?session=<id>` -- a session's summary as a page on the
    same port every other surface uses, rendered from exactly the dict
    `session.do_report()` returns -- the same body `itembank report`
    prints, so the page and the command can never disagree (SURF-04).

    `session_id` comes off the query string and is resolved through the
    same `session_index(root)`-backed `api_session_path` lookup `/api/*`
    uses; a value that is not a key in that lookup takes the same 404
    branch as an unknown bank stem and is never joined to a path (T-2-01).
    """
    params = urllib.parse.parse_qs(urllib.parse.urlsplit(handler.path).query)
    session_id = (params.get("session") or [""])[0]
    path = api_session_path(handler, session_id)
    if path is None:
        handler.send_not_found(session_id)
        return
    # Both except clauses are deliberate, mirroring every /api/* handler
    # below: `session.do_report` raises SystemExit on a routine session
    # error (a malformed or future-versioned session file), and SystemExit
    # derives from BaseException, so a bare `except Exception` would not
    # catch it -- an uncaught one here would take the request loop, and
    # every other bank and tab this daemon serves, down with it (T-2-03).
    try:
        result = session.do_report(path)
    except SystemExit as exc:
        handler.send_error(400, str(exc.code))
        return
    except Exception as exc:
        handler.send_server_error(exc)
        return
    summary = result["summary"]
    status = result["status"]
    if summary["auto_attempts"] == 0 and summary["pending_manual"] == 0:
        body = REPORT_EMPTY
    else:
        position = total = None
        if status == "active":
            # Position/total come from the session's own cursor and item
            # count -- the same session data `session_summary()` was itself
            # computed from -- never recomputed from the responses list.
            data = read_session(path)
            position, total = data["cursor"], len(data["items"])
        body = _report_card(summary, status, position, total)
    page = REPORT_TEMPLATE.replace("__THEME__", THEME_CSS).replace(
        "__TITLE__", "itembank report").replace("__BODY__", body)
    handler.send_html(page.encode("utf-8"))


def sessions_by_bank(root, banks):
    """`{bank_stem: session_id}` for banks that have at least one session
    recorded under `<root>/_attempts/` -- the index's `View report` link
    (Copywriting Contract: "only if `_attempts/session_*.json` exists for
    it") is wired only for the stems this returns; a bank with none gets no
    link rather than a dead one.

    Built by reading every session `session_index(root)` already found and
    matching each one's own `bank` field (an abspath, per `do_start`)
    against `banks`' own abspaths -- never a second bank scan. A session
    file that fails to parse, or whose `bank` no longer matches anything
    scanned (renamed or removed since the session was recorded), is skipped
    rather than raised, the same allowlist-tolerance `session_index` itself
    already applies.

    When a bank has more than one recorded session, the one whose file has
    the newest mtime wins -- not whichever `session_id` (a random uuid4 hex,
    per `do_start`/`do_next`, unrelated to time) happens to sort lexically
    largest. `write_session`'s own tmp-then-`os.replace()` write refreshes
    the mtime on every `do_next`/`do_submit`, so this tracks the most
    recently *active* session, not merely the most recently created one.
    """
    index = session_index(root)
    by_abspath = dict((os.path.abspath(path), stem) for stem, path in banks.items())
    result = {}
    best_mtime = {}
    for session_id, path in sorted(index.items()):
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
            mtime = os.path.getmtime(path)
        except (OSError, ValueError):
            continue
        if not isinstance(data, dict):
            continue
        stem = by_abspath.get(data.get("bank"))
        if stem is None:
            continue
        if stem not in best_mtime or mtime > best_mtime[stem]:
            best_mtime[stem] = mtime
            result[stem] = session_id            # newest-mtime session wins
    return result


def handle_index(handler):
    """`GET /` -- the index of every bank and day plan this daemon found at
    startup. No HTML is generated anywhere else; this is the one function
    that authors it, following `quiz.page_for()`'s substitution convention.
    """
    banks, plans = handler.banks, handler.plans
    stems = sorted(set(banks) | set(plans), key=str.lower)
    if stems:
        report_links = sessions_by_bank(handler.root, banks)
        rows = []
        for stem in stems:
            esc = html.escape(stem)
            if stem in banks:
                session_id = report_links.get(stem)
                link = ('\n    <a href="/report?session=%s">View report</a>'
                        % html.escape(session_id)) if session_id else ""
                row = BANK_ROW.replace("__STEM__", esc).replace("__REPORT_LINK__", link)
            else:
                row = PLAN_ROW.replace("__STEM__", esc)
            rows.append(row)
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
        handler.send_server_error(exc)
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

    A plan with no override is rebuilt once the wall-clock date has moved
    past the cached state's own `iso`: the consolidated `itembank daemon` is
    meant to run indefinitely across multiple banks and plans, unlike the
    old short-lived per-day `cmd_day` process this replaces, so caching
    "today" forever would serve yesterday's plan row, streak and history
    past midnight with no signal it had gone stale. A backfilled/overridden
    `iso` names a specific historical date, never "today", so it is exempt
    from this re-derivation.
    """
    override = handler.day_extra.get(stem, {})
    state = handler.day_states.get(stem)
    if state is not None:
        if override.get("iso") or state["iso"] == datetime.date.today().isoformat():
            return state
    path = handler.plans[stem]
    plan_dir = os.path.dirname(os.path.abspath(path)) or "."
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
        handler.send_server_error(exc)
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
        handler.send_server_error(exc)
        return
    if result is None:
        handler.send_error(404)
        return
    handler.send_json(result)


# ---- /api/* -- SURF-04's proof: an agent drives a whole sitting over HTTP
# against the exact same runtime calls `surfaces/session.py` already makes
# from the shell. Two findings from RESEARCH.md are load-bearing here and
# are why this exists as its own section rather than three lines bolted
# onto the quiz handlers: `session.do_*` raises `SystemExit` on error
# conditions that are routine in normal use (Pitfall #3), and
# the runtime's session-file readers/writers take a raw filesystem path
# with no allowlist at all (Pitfall #5). Every handler below resolves an identifier
# through an allowlist before ever calling a `do_*`, and every `do_*` call
# is wrapped in the SystemExit/Exception containment described below.

SESSION_MODES = ("diagnostic", "practice", "exam", "remediation", "drill")
CONFIDENCE_LEVELS = ("high", "medium", "low")

# `/api/*` addresses a session by its opaque `session_id` (resolved through
# `session_index`) and a bank by its scanned stem (resolved through
# `handler.banks`) -- never by a raw filesystem path. A body naming one of
# these CLI-side field names instead is refused loudly with 400 rather than
# silently ignored, so a client that guesses the old Namespace field name
# can never reintroduce the raw-path surface D-03's bank allowlist already
# closed once (T-2-01).
API_FORBIDDEN_FIELDS = ("session", "bank_path", "out")


def session_index(root):
    """`{session_id: abspath}` built by scanning `<root>/_attempts/` for
    `session_*.json` files and reading each one's own `session_id` field.

    Built lazily per request rather than once at daemon startup, so a
    session created by `POST /api/start` -- or by an `itembank start` run
    in another terminal while the daemon is up -- is addressable
    immediately; one directory listing per API request is cheap next to
    the file reads the request is about to do anyway. Skips any file that
    does not parse as JSON, is not a JSON object, or carries no
    `session_id`, rather than raising: a half-written session file must
    not break addressing for every other session (D-03's allowlist
    principle extended to session identifiers -- RESEARCH.md Pitfall #5).
    """
    attempts_dir = os.path.join(os.path.abspath(root), "_attempts")
    index = {}
    if not os.path.isdir(attempts_dir):
        return index
    for name in os.listdir(attempts_dir):
        if not (name.startswith("session_") and name.endswith(".json")):
            continue
        path = os.path.join(attempts_dir, name)
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, ValueError):
            continue
        if not isinstance(data, dict):
            continue
        session_id = data.get("session_id")
        if isinstance(session_id, str) and session_id:
            index[session_id] = path
    return index


def api_reject_path_fields(data):
    """The first `API_FORBIDDEN_FIELDS` name present in `data`, or `None`."""
    for field in API_FORBIDDEN_FIELDS:
        if field in data:
            return field
    return None


def api_read_json(handler):
    """`handler.read_json()`, but a malformed or non-object body is reported
    to the caller as `(None, True)` instead of letting the decode error
    propagate into the generic `except Exception` -> 500 clause every
    handler below also carries -- a client typo in a JSON body is exactly
    the routine, not-exotic condition D-05 asks for a clean 4xx on, not a
    500. Returns `(data, failed)`; the caller has already sent the error
    response when `failed` is true.
    """
    try:
        data = handler.read_json()
    except (ValueError, TypeError) as exc:
        handler.send_error(400, "malformed JSON body: %s" % exc)
        return None, True
    if not isinstance(data, dict):
        handler.send_error(400, "JSON body must be a JSON object")
        return None, True
    bad = api_reject_path_fields(data)
    if bad:
        handler.send_error(
            400, "field %r is not accepted here; a session is addressed by its "
            "session_id and a bank by its scanned stem, never by a path" % bad)
        return None, True
    return data, False


def api_session_path(handler, session_id):
    """The resolved session path for a client-supplied `session_id`, or
    `None` -- a miss (wrong type, empty, or simply unknown) is always a
    404, and `session_id` is never joined to a path itself; it is only
    ever a dict key into `session_index`'s own allowlist.
    """
    if not isinstance(session_id, str) or not session_id:
        return None
    return session_index(handler.root).get(session_id)


def handle_api_start(handler):
    """`POST /api/start` -- `{"bank": "<stem>", "count", "objective", "mode",
    "seed"}`. `bank` is resolved through the same stem allowlist the GET
    routes use: a value that is not a key in `handler.banks` is a 404, full
    stop -- it is never joined to a path, never normalised, never checked
    for traversal segments, because it is never treated as a path at all.
    The output path is computed server-side under `<root>/_attempts/`,
    exactly what `session.do_start` defaults to when no `out` is given;
    `out` is never read from the body (T-2-02).
    """
    data, failed = api_read_json(handler)
    if failed:
        return
    bank = data.get("bank")
    path = handler.banks.get(bank) if isinstance(bank, str) else None
    if path is None:
        handler.send_not_found(bank if isinstance(bank, str) else "")
        return
    count = data.get("count", 10)
    if not isinstance(count, int) or isinstance(count, bool):
        count = 10
    seed = data.get("seed", 0)
    if not isinstance(seed, int) or isinstance(seed, bool):
        seed = 0
    mode = data.get("mode", "diagnostic")
    if mode not in SESSION_MODES:
        mode = "diagnostic"
    objective = data.get("objective", "")
    if not isinstance(objective, str):
        objective = ""
    out = os.path.join(os.path.abspath(handler.root), "_attempts",
                       "session_%s.json" % uuid.uuid4().hex[:12])
    # Both except clauses below are deliberate and both required, not one
    # collapsed into the other: SystemExit derives from BaseException, not
    # Exception, so the bare `except Exception` clause every other route
    # handler in this module already uses would NOT catch it -- an
    # uncaught SystemExit here would propagate out through socketserver's
    # request loop and kill the process serving every other bank, every
    # other tab and the day view. The conditions that raise it are routine
    # here, not exotic: a bank with lint errors, an objective matching no
    # items, a session already complete. Do not collapse these two clauses
    # into one in a later refactor.
    try:
        result = session.do_start(path, count, objective, mode, seed, out, False)
    except SystemExit as exc:
        handler.send_error(400, str(exc.code))
        return
    except Exception as exc:
        handler.send_server_error(exc)
        return
    handler.send_json(result)


def handle_api_next(handler):
    """`POST /api/next` -- `{"session_id": "<id>"}`. `session_id` is resolved
    through `session_index`; a miss is a 404.
    """
    data, failed = api_read_json(handler)
    if failed:
        return
    session_id = data.get("session_id")
    path = api_session_path(handler, session_id)
    if path is None:
        handler.send_not_found(session_id if isinstance(session_id, str) else "")
        return
    try:
        result = session.do_next(path)
    except SystemExit as exc:
        handler.send_error(400, str(exc.code))
        return
    except Exception as exc:
        handler.send_server_error(exc)
        return
    handler.send_json(result)


def handle_api_submit(handler):
    """`POST /api/submit` -- `{"session_id": "<id>", "answer": ..., "confidence"}`.
    `answer` is passed through untouched (`session.do_submit` normalizes it
    the same way the CLI's `--answer` string already was); `confidence`
    must be one of the three levels or absent.
    """
    data, failed = api_read_json(handler)
    if failed:
        return
    session_id = data.get("session_id")
    path = api_session_path(handler, session_id)
    if path is None:
        handler.send_not_found(session_id if isinstance(session_id, str) else "")
        return
    confidence = data.get("confidence")
    if confidence not in (None,) + CONFIDENCE_LEVELS:
        handler.send_error(
            400, "confidence must be one of %s" % ", ".join(CONFIDENCE_LEVELS))
        return
    answer = data.get("answer")
    try:
        result = session.do_submit(path, answer, confidence)
    except SystemExit as exc:
        handler.send_error(400, str(exc.code))
        return
    except Exception as exc:
        handler.send_server_error(exc)
        return
    handler.send_json(result)


def handle_api_report(handler):
    """`POST /api/report` -- `{"session_id": "<id>"}`."""
    data, failed = api_read_json(handler)
    if failed:
        return
    session_id = data.get("session_id")
    path = api_session_path(handler, session_id)
    if path is None:
        handler.send_not_found(session_id if isinstance(session_id, str) else "")
        return
    try:
        result = session.do_report(path)
    except SystemExit as exc:
        handler.send_error(400, str(exc.code))
        return
    except Exception as exc:
        handler.send_server_error(exc)
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

    def send_server_error(self, exc):
        """A `500` that never leaks a local filesystem path, matching
        `send_not_found`'s T-2-05 discipline for `404`. `str(exc)` on an
        `OSError`/`IOError` (permission denied, disk full, a file moved
        mid-request) typically includes the full absolute served path --
        exactly what `--lan` exposes to every other device on the network.
        The real text is logged server-side only; the client gets a
        generic, path-free message.
        """
        print("  500 %s" % exc)
        self.send_error(500, "internal error")

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

    `allow_reuse_address` is deliberately left at its stdlib default
    (`False`), not set `True`: `ThreadingMixIn` needs no help from
    `SO_REUSEADDR` to serve concurrently, and on Windows `SO_REUSEADDR`'s
    semantics are far more permissive than on POSIX -- it lets a second
    process bind an already-listening port instead of merely skipping
    TIME_WAIT, so a second daemon on a held port would bind silently instead
    of raising the `OSError` `start_server()`'s probe depends on seeing.
    Setting it `True` here (found while implementing plan 02-06's own
    detect-and-attach path, which this attribute otherwise defeats outright
    on this project's own target platform) is exactly the bug D-02 exists to
    prevent, so it stays off.
    """
    daemon_threads = True


def _bind(port, host="127.0.0.1"):
    """The same free-port fallback `server.bind()` already implements,
    applied to `Daemon` instead of `socketserver.TCPServer` -- `server.bind()`
    itself constructs a fixed server class, so this mirrors its logic rather
    than widening that module's scope outside this plan. Used by every
    caller of `serve_scoped()` that has not adopted `start_server()`'s
    detect-and-attach probe (`cmd_serve`/`cmd_day`, both scoped to a single
    bank or plan rather than a whole directory -- D-02's "no second daemon
    ever binds" framing is `cmd_daemon`'s problem, not theirs).
    """
    try:
        return Daemon((host, port), DaemonHandler)
    except OSError as exc:
        print("  port %d unavailable (%s), using a free one instead"
              % (port, exc.__class__.__name__))
        return Daemon((host, 0), DaemonHandler)


def probe(port, host="127.0.0.1", timeout=0.5):
    """Return True only when something at `<host>:<port>` positively
    identifies itself as this daemon -- a GET against `MARKER_PATH` whose
    body parses as JSON with an `itembank` field that is exactly `True`.

    Every other outcome -- a closed port, a timeout, a connection refused, a
    plain-text or otherwise non-JSON body, a JSON body of the wrong shape, a
    redirect -- means *not us* and returns False, via one blanket
    `except Exception`. This mirrors `day.anki_read()`'s own shape for the
    same reason: the asymmetry is deliberate. A false negative costs one
    unnecessary free-port fallback; a false positive would send a learner to
    somebody else's web server believing it was their study tool (T-2-08).
    """
    try:
        url = "http://%s:%d%s" % (host, port, MARKER_PATH)
        with urllib.request.urlopen(url, timeout=timeout) as r:
            data = json.load(r)
        return isinstance(data, dict) and data.get("itembank") is True
    except Exception:
        return False


def start_server(handler_cls, port, host="127.0.0.1", no_open=False, window="app"):
    """The detect-and-attach startup path (D-02): try binding `Daemon`
    directly on `(host, port)` first, and only on `OSError` decide, by the
    *kind* of failure, whether attaching to an already-running itembank is
    the right response or whether this is simply a free-port fallback like
    every other launch already has.

    Returns `(srv, bound_port, fell_back)`. Three cases:

    - **Reserved or permission-denied** (`errno.EACCES`, or Windows
      `winerror` 10013): nothing is listening here, it is the OS itself
      refusing the bind -- the Hyper-V/WSL reserved-range accommodation
      `server.bind()`'s own docstring already records. Probing would only
      burn the timeout on exactly the platform this project runs on
      (T-2-20), so this case skips straight to the free-port fallback.
    - **Occupied by another itembank** (`probe(port)` is True): print the
      already-running line, open a container at that URL through
      `launcher.open_window` (D-11's `window` setting and `no_open`
      opt-out both apply here exactly as they do on a fresh launch), and
      exit 0. This runs in the CLI entry point's own process before any
      server of this process's own exists -- not inside a request handler --
      so exiting here carries none of Pitfall #3's hazard.
    - **Occupied by something else** (`probe(port)` is False): fall back to
      a free port, same as the reserved-port case, and tell the caller a
      fallback happened so it can print the port actually bound. This is the
      third case RESEARCH.md's Open Question 3 raises and the plan's own
      flagged planner_assumption resolves as degrade-never-block rather than
      a hard failure.

    Both fallback branches call `server.bind()` rather than re-implementing
    its free-port logic a third time -- D-02 scopes this change to the
    daemon's own startup path and leaves `server.bind()` itself untouched
    and general for `cmd_serve`'s and `cmd_day`'s own calls into it.
    """
    try:
        return Daemon((host, port), handler_cls), port, False
    except OSError as exc:
        reserved = getattr(exc, "winerror", None) == 10013 or exc.errno == errno.EACCES
        if not reserved and probe(port):
            url = "http://127.0.0.1:%d/" % port
            print("itembank is already running at %s" % url)
            launcher.open_window(url, window, no_open)
            sys.exit(0)
        srv = server.bind(handler_cls, port, host)
        return srv, srv.server_address[1], True


def serve_scoped(root, banks, plans, port, host="127.0.0.1", open_path="/",
                 no_open=False, extra=None, on_bound=None, srv=None, window="app"):
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

    `srv`, if given, is an already-bound server -- `cmd_daemon`'s own
    `start_server()` result, carrying the detect-and-attach probe's outcome.
    This function binds nothing itself in that case; it only wires the
    handler class onto whatever was already bound and runs the shared tail.
    Left `None` (the default) for every caller that has not adopted the
    probe (`cmd_serve`, `cmd_day`), which keeps binding through `_bind()`'s
    own free-port fallback exactly as before.

    `window` (D-11) chooses the container `launcher.open_window` opens once
    the socket is accepting: `"app"` (the default, matching the shipped
    schema default) attempts a frameless Chromium-family window and falls
    back to a tab, `"tab"` always opens an ordinary tab. `cmd_serve` and
    `cmd_day` reach this function without a settings read of their own and
    therefore take the default, exactly like `cmd_daemon`'s own shipped
    default -- one behaviour across every daemon launch in the tool.
    """
    extra = extra or {}
    DaemonHandler.banks = banks
    DaemonHandler.plans = plans
    DaemonHandler.collisions = extra.get("collisions", [])
    DaemonHandler.root = root
    DaemonHandler.sessions = extra.get("sessions", {})
    DaemonHandler.day_states = {}                  # built lazily, one per served plan
    DaemonHandler.day_extra = extra.get("day_extra", {})

    bound = srv if srv is not None else _bind(port, host)
    with bound:
        bound_port = bound.server_address[1]
        display_host = "127.0.0.1" if host in (ALL_INTERFACES, "127.0.0.1") else host
        url = "http://%s:%d%s" % (display_host, bound_port, open_path)
        print("  url     %s" % url)
        if on_bound:
            on_bound(bound_port)
        sys.stdout.flush()
        if not no_open:
            threading.Timer(0.4, lambda: launcher.open_window(url, window, no_open)).start()
        try:
            bound.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped.")
    return bound_port


def cmd_daemon(a):
    root = a.dir
    banks, plans, collisions = scan_dir(root)

    # The `daemon` settings group's own port/LAN defaults, with an explicit
    # `--port`/`--lan` on the command line winning -- argparse defaults to
    # `None`/`False` (never a hardcoded 8730) so "the flag was not given at
    # all" is distinguishable from "the flag matches the file's own value".
    cfg = settings.load_settings(root)
    port = a.port if a.port is not None else cfg["daemon"]["port"]
    lan = True if a.lan else cfg["daemon"]["lan"]
    host = ALL_INTERFACES if lan else "127.0.0.1"
    window = cfg["daemon"]["window"]
    # D-11: open_browser gates whether anything opens at all; --no-open still
    # wins over it. This is the first reader open_browser has ever had (a
    # grep before this task found zero) -- the schema declared it, nothing
    # read it, and a learner setting it false believed it was doing
    # something. It is now.
    no_open = a.no_open or not cfg["daemon"]["open_browser"]

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

    # The detect-and-attach probe (D-02): a second `itembank daemon` on a
    # port a first daemon holds attaches instead of binding; a reserved or
    # squatted port falls back to a free one instead of hard-failing. A
    # fallback's own "port unavailable" line comes from `server.bind()`
    # itself (reused, not duplicated here); the `url` line `serve_scoped()`
    # always prints next names the port actually bound.
    srv, bound_port, fell_back = start_server(DaemonHandler, port, host,
                                              no_open=no_open, window=window)

    def on_bound(actual_port):
        if lan:
            print("  phone   http://%s:%d/   (same wifi only)"
                  % (day.lan_address(), actual_port))
            print("  LAN mode is on: every device on this network can reach this "
                  "daemon. itembank has no accounts and no authentication by design.")

    serve_scoped(root, banks, plans, port, host=host, open_path="/", no_open=no_open,
                extra={"sessions": sessions, "collisions": collisions},
                on_bound=on_bound, srv=srv, window=window)
    return 0
