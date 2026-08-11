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
import datetime, errno, hashlib, html, json, os, re, secrets, socket, socketserver, sys, threading
import urllib.parse, urllib.request, uuid

import evidence
import resources
import retention
import selection
import server
import subjects
from model import (lesson_slug, load, parse_bank, parse_key_blocks,
                   parse_lesson, parse_terms)
from runtime import explain_payload, glossable, read_session, upgrade_session
from surfaces import (day, launcher, lesson, presentation, quiz, retention_view,
                      seeding, session, settings, study, update)
from surfaces import audio as audio_surface
from surfaces import theme


MARKER_PATH = "/__itembank__"

# The one place that chooses whether the daemon speaks to just this machine
# or to the whole local network -- every other spot in this module that
# needs to know reads this constant rather than repeating the literal, so
# "how many places decide the bind host" stays a one-line answer instead of
# a claim to trust (checked by this plan's own acceptance criteria).
ALL_INTERFACES = "0.0.0.0"

# The fixed stdout handshake the sidecar prints after binding (D-03/D-04):
# one `itembank-key:value` line per field, in this dict's order. The shell's
# parser and this plan's tests read these same constant strings, so a framing
# change is one edit, not a second protocol (T-13-02). The per-launch token
# travels on this stdout channel -- inherited by the shell, never a CLI
# argument visible to other processes (T-13-04).
SIDECAR_HANDSHAKE = {
    "port": "itembank-port",
    "token": "itembank-token",
    "version": "itembank-version",
}

# The request header a sidecar-mode daemon requires on the shell-used API
# routes when a per-launch token is configured (D-04). Same shared-constant
# discipline as SIDECAR_HANDSHAKE: the shell and the tests read this one name.
SIDECAR_TOKEN_HEADER = "X-Itembank-Token"

# 13-UI-SPEC 3.3(e), the `port-held` / attach-failed state copy, verbatim
# (D-06): the sidecar refuses by name when a second launch finds its
# configured port held by a listener that does not answer the itembank
# marker -- the "running instance is not reachable" case. The full copy
# carries a pid the daemon side cannot know (no stdlib port->pid mapping),
# so the name is filled here and the pid is the shell's to add in its own
# window document (plan 13-02).
SIDECAR_PORT_HELD_COPY = (
    "itembank is already running, but this window could not attach to it. "
    "Close the other itembank window, or end the process named itembank, "
    "then start itembank again."
)

# Same directories `cmd_guard` skips, plus the two this daemon itself writes
# into -- neither an attempt file nor the evidence log is ever a candidate
# bank or day plan.
SKIP_DIRS = {".git", ".github", "_attempts", "_evidence"}

QUIZ_GET_RE = re.compile(r"^/quiz/(?P<stem>[^/]+)$")
QUIZ_ANSWER_RE = re.compile(r"^/quiz/(?P<stem>[^/]+)/answer$")
STUDY_GET_RE = re.compile(r"^/study/(?P<stem>[^/]+)$")
LESSON_GET_RE = re.compile(r"^/lesson/(?P<stem>[^/]+)$")

# 09-04: the one static-asset channel. `/assets/katex/<name>` resolves only
# through the closed KATEX_ASSETS map below -- a known URL suffix to a
# vendored archive-relative path and MIME type. The name regex admits only
# a narrow safe character set (letters, digits, `_`, `.`, `/`, `-`), and the
# handler never joins the client's name to a filesystem path; an unknown,
# encoded, nested, traversal, or query-manipulated name is a 404 (T-09-09).
KATEX_ASSET_RE = re.compile(r"^/assets/katex/(?P<name>[A-Za-z0-9_./-]+)$")

# The closed route map for the vendored KaTeX distribution (09-04). Keys are
# exact URL suffixes after `/assets/katex/`; values are
# (archive-relative path, MIME type) pairs loaded through the one resource
# reader. The font names come from the reviewed vendor inventory (the 60
# files katex.min.css references), never from a request path. Serving a font
# from the map rather than from the request keeps the map closed: every name
# the CSS can emit is present, and nothing the browser cannot name is.
KATEX_ASSETS = {}
for _font in (
        "KaTeX_AMS-Regular", "KaTeX_Caligraphic-Bold",
        "KaTeX_Caligraphic-Regular", "KaTeX_Fraktur-Bold",
        "KaTeX_Fraktur-Regular", "KaTeX_Main-Bold",
        "KaTeX_Main-BoldItalic", "KaTeX_Main-Italic",
        "KaTeX_Main-Regular", "KaTeX_Math-BoldItalic",
        "KaTeX_Math-Italic", "KaTeX_SansSerif-Bold",
        "KaTeX_SansSerif-Italic", "KaTeX_SansSerif-Regular",
        "KaTeX_Script-Regular", "KaTeX_Size1-Regular",
        "KaTeX_Size2-Regular", "KaTeX_Size3-Regular",
        "KaTeX_Size4-Regular", "KaTeX_Typewriter-Regular"):
    for _ext, _mime in ((".woff2", "font/woff2"), (".woff", "font/woff"),
                        (".ttf", "font/ttf")):
        KATEX_ASSETS["fonts/%s%s" % (_font, _ext)] = (
            "vendor/katex/fonts/%s%s" % (_font, _ext), _mime)
KATEX_ASSETS.update({
    "katex.min.css": ("vendor/katex/katex.min.css",
                      "text/css; charset=utf-8"),
    "katex.min.js": ("vendor/katex/katex.min.js",
                     "application/javascript; charset=utf-8"),
    "contrib/auto-render.min.js": (
        "vendor/katex/contrib/auto-render.min.js",
        "application/javascript; charset=utf-8"),
})
del _font, _ext, _mime

LESSON_CHECK_RE = re.compile(r"^/lesson/(?P<stem>[^/]+)/check$")
LESSON_SKIP_RE = re.compile(r"^/lesson/(?P<stem>[^/]+)/skip$")
GLOSS_GET_RE = re.compile(r"^/gloss/(?P<stem>[^/]+)/(?P<slug>[^/]+)$")
KEY_REVIEW_RE = re.compile(r"^/key/(?P<key_id>[^/]+)/review$")
DAY_GET_RE = re.compile(r"^/day/(?P<stem>[^/]+)$")
DAY_SAVE_RE = re.compile(r"^/day/(?P<stem>[^/]+)/save$")
DAY_OPEN_RE = re.compile(r"^/day/(?P<stem>[^/]+)/open$")
DAY_EDIT_RE = re.compile(r"^/day/(?P<stem>[^/]+)/edit$")

# Fields a browser may send on `POST /day/<stem>/edit`. Everything else is
# refused before any helper runs (T-04-21): the client addresses the plan by
# URL stem only, and the body carries the revision plus changed structured
# cells -- never a filesystem path, a full-document replacement, or any other
# authority field.
DAY_EDIT_ALLOWED_FIELDS = ("revision", "edits", "force_token", "confirmation",
                           "force")

# The only body fields `POST /seed/accept` reads (plan 03.2-03): a bank
# addressed by scanned stem, one of the three accept-loop actions, and the
# draft item dict for the accept action. Everything else is refused by name,
# the same authority-shaped-field discipline every mutating route here takes.
SEED_ACCEPT_ALLOWED_FIELDS = ("bank", "action", "draft")

# The `/api/*` session routes: D-04's four plus Phase 6's `/api/hint`,
# plan 06.1-02's `/api/interact`, plan 08-05's `/api/rubric-review`, Phase
# 10's `/api/override` and `/api/lesson-complete`, and Phase 09.1's
# `/api/export_audio`. Fixed literals, not stem-parameterised: a session
# or a bank is addressed by an opaque identifier in the JSON body (T-2-01),
# never by a path segment, so there is no `<stem>`/`<id>` group in any of
# these patterns at all. The ten-entry length is asserted by
# `check_api_route_scope` in `tests/daemon_roundtrip.py`, and every entry
# is mirrored in ROUTE_CLI and SURFACE_PARITY (Extensibility Rule 9(a)).
API_ROUTES = (
    ("POST", "/api/start", "handle_api_start"),
    ("POST", "/api/next", "handle_api_next"),
    ("POST", "/api/submit", "handle_api_submit"),
    ("POST", "/api/hint", "handle_api_hint"),
    ("POST", "/api/interact", "handle_api_interact"),
    ("POST", "/api/report", "handle_api_report"),
    ("POST", "/api/override", "handle_api_override"),
    ("POST", "/api/lesson-complete", "handle_api_lesson_complete"),
    ("POST", "/api/rubric-review", "handle_api_rubric_review"),
    ("POST", "/api/export_audio", "handle_api_export_audio"),
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
    ("GET", "/settings", "handle_settings_get"),
    ("GET", "/disclosure", "handle_disclosure"),
    ("POST", "/api/theme", "handle_theme_post"),
    ("POST", "/cli-twin", "handle_cli_twin"),
    ("POST", "/seed/accept", "handle_seed_accept"),
) + API_ROUTES + (
    ("GET", KATEX_ASSET_RE, "handle_katex_asset"),
    ("GET", QUIZ_GET_RE, "handle_quiz_get"),
    ("POST", QUIZ_ANSWER_RE, "handle_quiz_answer"),
    ("GET", STUDY_GET_RE, "handle_study_get"),
    ("GET", LESSON_GET_RE, "handle_lesson_get"),
    ("POST", LESSON_CHECK_RE, "handle_lesson_check"),
    ("POST", LESSON_SKIP_RE, "handle_lesson_skip"),
    ("GET", GLOSS_GET_RE, "handle_gloss_get"),
    ("POST", KEY_REVIEW_RE, "handle_key_review"),
    ("GET", DAY_GET_RE, "handle_day_get"),
    ("POST", DAY_SAVE_RE, "handle_day_save"),
    ("POST", DAY_OPEN_RE, "handle_day_open"),
    ("POST", DAY_EDIT_RE, "handle_day_edit"),
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
    ("GET", "/settings"): "theme",
    ("GET", "/disclosure"): "disclosure",
    ("POST", "/api/theme"): "theme",
    ("POST", "/cli-twin"): "cli-twin",
    ("POST", "/seed/accept"): "seed",
    ("POST", "/api/start"): "start",
    ("POST", "/api/next"): "next",
    ("POST", "/api/submit"): "submit",
    ("POST", "/api/hint"): "hint",
    ("POST", "/api/interact"): "interact",
    ("POST", "/api/report"): "report",
    ("POST", "/api/override"): "override",
    ("POST", "/api/lesson-complete"): "lesson",
    ("POST", "/api/rubric-review"): "rubric-review",
    ("GET", KATEX_ASSET_RE): "daemon",
    ("POST", "/api/export_audio"): "export",
    ("GET", QUIZ_GET_RE): "serve",
    ("POST", QUIZ_ANSWER_RE): "serve",
    ("GET", STUDY_GET_RE): "study",
    ("GET", LESSON_GET_RE): "lesson",
    ("POST", LESSON_CHECK_RE): "lesson-check",
    ("POST", LESSON_SKIP_RE): "lesson-skip",
    ("GET", GLOSS_GET_RE): "gloss",
    ("POST", KEY_REVIEW_RE): "key-review",
    ("GET", "/day"): "day",
    ("GET", DAY_GET_RE): "day",
    ("POST", DAY_SAVE_RE): "day",
    ("POST", DAY_OPEN_RE): "day",
    ("POST", DAY_EDIT_RE): "day",
}

# Extensibility Rule 9(a) (ROADMAP.md): every /api/* route reserves its
# future MCP tool name in the same commit it ships -- the third surface
# (MCP) arrives as a third column here, never as a second parity map, and an
# unmapped entry fails `check_surface_parity` instead of shipping silently.
# Each row is (route, CLI command, reserved MCP tool name); the tool names
# are the locked reserved vocabulary (start, next, submit, report, hint,
# override, lesson_complete, rubric_review).
SURFACE_PARITY = (
    (("POST", "/api/start"), "start", "start"),
    (("POST", "/api/next"), "next", "next"),
    (("POST", "/api/submit"), "submit", "submit"),
    (("POST", "/api/hint"), "hint", "hint"),
    (("POST", "/api/interact"), "interact", "interact"),
    (("POST", "/api/report"), "report", "report"),
    (("POST", "/api/override"), "override", "override"),
    (("POST", "/api/lesson-complete"), "lesson", "lesson_complete"),
    (("POST", "/api/rubric-review"), "rubric-review", "rubric_review"),
    (("POST", "/api/export_audio"), "export", "export_audio"),
)


def cli_twin_for(path):
    """The CLI command that reaches the same runtime call as a served view
    path -- the daemon-owned mapping behind the shell's "Copy the CLI command
    for this view" menu item (13-UI-SPEC 2.2): the shell holds no per-view
    knowledge, the daemon owns the routes and therefore the mapping. Returns
    None when no GET route matches the path.
    """
    for method, pattern, _handler in ROUTES:
        if method != "GET":
            continue
        if isinstance(pattern, str):
            if path != pattern:
                continue
            name = ROUTE_CLI[(method, pattern)]
            return "itembank daemon ." if name == "daemon" else "itembank %s" % name
        m = pattern.match(path)
        if m:
            name = ROUTE_CLI[(method, pattern)]
            groups = m.groupdict()
            parts = [name]
            for key in ("stem", "slug", "key_id"):
                if groups.get(key):
                    parts.append(groups[key])
            return "itembank " + " ".join(parts)
    return None


def handle_cli_twin(handler):
    """`POST /cli-twin` -- `{"path": "<view path>"}` -> `{"command":
    "<cli equivalent>"}`. Read-only, never mutates; a path no GET route
    serves is a 404, and a non-path body is a 400 (T-2-02's resolve-through-
    allowlist discipline applied to a query, not a file).
    """
    if _reject_cross_origin(handler):
        return
    data, failed = api_read_json(handler)
    if failed:
        return
    path = data.get("path")
    if not isinstance(path, str) or not path.startswith("/"):
        handler.send_error(400, "path must be a route path")
        return
    command = cli_twin_for(path)
    if command is None:
        handler.send_error(404, "no CLI twin for this path")
        return
    handler.send_bytes(json.dumps({"command": command}).encode("utf-8"),
                       "application/json")


def handle_disclosure(handler):
    """`GET /disclosure` -- the one-disclosure render hook the shell's
    StatusNotice reads (13-UI-SPEC 7.2): the daemon owns the single
    `notified_at` record; showing the notice performs no check (the policy
    gate already ran at daemon start). Read-only, token-gated like every
    route except the probe marker.
    """
    handler.send_bytes(
        json.dumps(update.disclosure_state(handler.root)).encode("utf-8"),
        "application/json")


def handle_seed_accept(handler):
    """`POST /seed/accept` -- the daemon half of the one accept endpoint
    (D-07, plan 03.2-03). The browser surface is a client of the same
    `seeding.accept_candidate` function the `itembank seed` CLI calls -- one
    implementation, two surfaces, never two decisions.

    The body carries `{"bank": <scanned stem>, "action": accept|skip|cancel,
    "draft": {...}}`. The bank stem is resolved through the startup allowlist
    (`handler.banks`), never joined onto a filesystem path (T-2-01). Accept
    is the mutating write: it requires a loopback client (the same authority
    model `handle_theme_post` established -- a `--lan` daemon exposes the
    route to the network, so the bank write is loopback-only) and calls
    `seeding.accept_candidate`, which lint-gates the draft and appends a
    clean item exactly once. Skip defers (the item stays in the draft set and
    is reported at the end); cancel writes nothing (D-09) and returns the
    verbatim summary `Nothing was written.`
    """
    if not _same_origin(handler):
        handler.send_error(403, "cross-origin seed request refused")
        return
    data, failed = api_read_json(handler)
    if failed:
        return
    bank = data.get("bank")
    if not isinstance(bank, str) or bank not in handler.banks:
        handler.send_not_found(bank)
        return
    extra = sorted(k for k in data if k not in SEED_ACCEPT_ALLOWED_FIELDS)
    if extra:
        handler.send_error(
            400, "field %r is not accepted by /seed/accept; only bank, action, "
            "and draft are read" % extra[0])
        return
    action = data.get("action")
    if action not in ("accept", "skip", "cancel"):
        handler.send_error(400, "action must be one of accept|skip|cancel")
        return
    if action == "accept":
        if not _client_is_loopback(handler):
            handler.send_error(403, "seed accept requires a loopback client")
            return
        draft = data.get("draft")
        if not isinstance(draft, dict):
            handler.send_error(400, "accept requires a draft item object")
            return
        try:
            result = seeding.accept_candidate(handler.banks[bank], draft)
        except Exception as exc:                # never let a bad POST kill the daemon
            handler.send_server_error(exc)
            return
        handler.send_json(result)
        return
    if action == "skip":
        handler.send_json({
            "action": "skip", "deferred": True,
            "copy": "Skipped item deferred; it stays in the draft set and is "
                    "reported at the end."})
        return
    handler.send_json({"action": "cancel", "cancelled": True,
                       "summary": seeding.CANCELLED_SUMMARY})


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

# The index and report documents are no longer authored in this module:
# both pages render through `presentation.surface_shell` with a per-render
# `theme.theme_css(load_settings(root))` block (plan 04-04 Task 2), so no
# second stylesheet or palette owner exists anywhere in the daemon. The
# body-only fragments below are the state/content markup the handlers feed
# into that shell.

# The documented empty-state copy (04-UI-SPEC Copywriting Contract),
# rendered instead of a report table with all-zero or blank cells whenever
# a session has recorded neither an auto-marked response nor a
# pending-manual one.
REPORT_EMPTY = """<div class="empty">
  <h2>Nothing has been answered yet.</h2>
  <p>This sitting has not recorded a response. Sit the bank, then refresh
  this report.</p>
  <div class="actions"><a class="go primary" data-action-primary
    href="/">Back to itembank</a></div>
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
    output); no count is recomputed from a responses list. Pending-manual
    responses are disclosed in plain text (04-UI-SPEC: auto-graded totals
    exclude them), and the evidence the figures rest on stays visible as
    text rather than implied by the numbers.
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
    partial = ""
    if pending:
        partial = ('<p class="status" data-field="pending-notice">Some responses '
                   'still need review. Auto-graded totals exclude them.</p>')
    rows = _report_objective_rows(summary["objectives"])
    return (
        '<div class="card" data-status="%s">'
        '<div class="headline" data-field="pct">%d%%</div>'
        '<p class="headline-label">auto-marked accuracy</p>'
        '%s'
        '%s'
        '<div class="figures">%s</div>'
        '</div>'
        '<div class="table-wrap">'
        '<table><thead><tr><th>Objective</th><th>Attempts</th>'
        '<th>Correct</th><th>Pending</th></tr></thead>'
        '<tbody>%s</tbody></table>'
        "</div>"
        '<p class="status" data-provenance>This report is compiled from the '
        'recorded evidence for this sitting.</p>'
        % (html.escape(status), pct, progress, partial, figures, rows))


def _retention_report_body(payload, params):
    """The retention overview / drilldown page body, rendered from the
    SAME `retention.retention_report` payload `itembank trends` prints
    (D-15): no browser-side arithmetic, no second derivation, no paths or
    keys. `params` carries the allowlisted weeks/subject/objective query
    identifiers; the week controls and drilldown links preserve the
    current selection."""
    claim = payload.get("claim") or {}
    subject = params.get("subject")
    objective = params.get("objective")
    weeks = params.get("weeks")
    base = "/report"
    q = ["weeks=%d" % weeks] if weeks else []
    if subject:
        q.append("subject=" + urllib.parse.quote(subject))
    href = base + ("?" + "&".join(q) if q else "")
    parts = [retention_view.snapshot_stamp(claim)]
    week_links = "".join(
        '<a class="go%s" href="%s">%dw</a>'
        % (" active" if (weeks or 4) == w else "",
           base + "?weeks=%d" % w + ("&subject=" + urllib.parse.quote(subject)
                                     if subject else ""), w)
        for w in (1, 2, 4, 8, 12))
    parts.append('<p class="weeks">Window: %s</p>' % week_links)

    def obj_href(obj):
        extra = "&objective=" + urllib.parse.quote(obj)
        return base + "?weeks=%d" % (weeks or 4) + \
            ("&subject=" + urllib.parse.quote(subject) if subject else "") + extra

    if objective:
        row = (payload.get("objectives") or {}).get(objective)
        if row is None:
            parts.append('<p class="empty">No objective %r in this snapshot.</p>'
                         % html.escape(objective))
        else:
            back = base + ("?weeks=%d" % (weeks or 4)) + \
                ("&subject=" + urllib.parse.quote(row.get("subject") or "")
                 if row.get("subject") else "")
            parts.append('<p class="back"><a href="%s">&larr; %s</a></p>'
                         % (html.escape(back),
                            html.escape(row.get("subject") or "subjects")))
            parts.append("<h2>%s</h2>" % html.escape(objective))
            parts.append(retention_view.objective_detail(row, claim))
            parts.append(retention_view.evidence_drawer(row, claim,
                                                        row.get("subject")))
    elif subject:
        parts.append("<h2>Subject %s</h2>" % html.escape(subject))
        rows = []
        for obj, o in sorted((payload.get("objectives") or {}).items()):
            if evidence.subject_of(obj) != subject:
                continue
            state = o.get("state") or "unknown"
            rows.append(
                "<tr><th scope=row><a href=\"%s\">%s</a></th><td>%s</td>"
                "<td>%d</td><td>%d</td><td>%d</td><td>%s</td></tr>"
                % (html.escape(obj_href(obj)), html.escape(obj),
                   retention_view.objective_state(state),
                   o.get("attempts", 0), o.get("settled", 0),
                   o.get("correct", 0), html.escape(o.get("last_evidence") or "")))
        if not rows:
            parts.append('<p class="empty">No objectives for %r in this '
                         'snapshot.</p>' % html.escape(subject))
        parts.append('<div class="trend-wrap"><table class="trend">'
                     "<thead><tr><th>Objective</th><th>State</th>"
                     "<th>Attempts</th><th>Settled</th><th>Correct</th>"
                     "<th>Last evidence</th></tr></thead><tbody>%s</tbody>"
                     "</table></div>" % "".join(rows))
    else:
        parts.append("<h2>Subjects</h2>")
        rows = []
        for s, sub in sorted((payload.get("subjects") or {}).items()):
            rows.append(
                "<tr><th scope=row><a href=\"%s\">%s</a></th><td>%d</td>"
                "<td>%d</td><td>%d</td><td>%d</td></tr>"
                % (html.escape(base + "?weeks=%d" % (weeks or 4)
                               + "&subject=" + urllib.parse.quote(s)),
                   html.escape(s), sub.get("objective_count", 0),
                   sub.get("attempts", 0), sub.get("settled", 0),
                   sub.get("due", 0)))
        parts.append('<div class="trend-wrap"><table class="trend">'
                     "<thead><tr><th>Subject</th><th>Objectives</th>"
                     "<th>Attempts</th><th>Settled</th><th>Due</th>"
                     "</tr></thead><tbody>%s</tbody></table></div>"
                     % "".join(rows))
    rr = payload.get("return_rate")
    if rr is not None:
        parts.append('<p class="return-rate">Return rate: %s (%d occurred / '
                     "%d due sittings)</p>"
                     % (retention_view._fmt_rate(rr.get("rate")),
                        rr.get("occurred", 0), rr.get("due", 0)))
    parts.append(retention_view.trend_text(payload))
    parts.append(retention_view.trend_table(payload))
    return "\n".join(parts)


REPORT_FAILURE_COPY = ("This report could not be derived from the current "
                       "evidence snapshot. Try again or run the report "
                       "command; no recommendation was made.")


def handle_report_get(handler):
    """`GET /report` -- TWO branches. With `?session=<id>` it renders a
    session's summary from exactly the dict `session.do_report()` returns
    (the same body `itembank report` prints, SURF-04). Without `session`
    (10-05 Task 3) it renders the retention overview / subject / objective
    drilldown from the SAME `retention.retention_report` payload
    `itembank trends` prints, with allowlisted week/subject/objective
    query identifiers (D-15); snapshot failure serves the locked report-
    failure copy and makes no recommendation.

    `session_id` comes off the query string and is resolved through the
    same `session_index(root)`-backed `api_session_path` lookup `/api/*`
    uses; a value that is not a key in that lookup takes the same 404
    branch as an unknown bank stem and is never joined to a path (T-2-01).
    """
    params = urllib.parse.parse_qs(urllib.parse.urlsplit(handler.path).query)
    session_id = (params.get("session") or [""])[0]
    if not session_id:
        # 10-05 Task 3: `GET /report` without `session` is the retention
        # overview / drilldown surface. The page renders the SAME payload
        # `itembank trends` prints (D-15); the report failure copy is
        # served when the snapshot cannot be derived, and no recommendation
        # is made (T-10-22).
        theme_block = theme.theme_css(settings.load_settings(handler.root))
        try:
            weeks_raw = (params.get("weeks") or [""])[0]
            try:
                weeks = int(weeks_raw) if weeks_raw else 4
            except ValueError:
                weeks = 4
            if weeks not in (1, 2, 4, 8, 12):
                handler.send_error(400, "weeks must be one of 1, 2, 4, 8, 12")
                return
            subject = (params.get("subject") or [""])[0] or None
            objective = (params.get("objective") or [""])[0] or None
            filters = {}
            if subject:
                filters["subject"] = subject
            if objective:
                filters["objective"] = objective
            log = evidence.log_path(handler.root)
            events = evidence.capture_events(log) \
                if os.path.exists(log) else ()
            payload = retention.retention_report(
                events, weeks=weeks, filters=filters,
                cfg=settings.load_settings(handler.root))
            body = _retention_report_body(payload, {"weeks": weeks,
                                                    "subject": subject,
                                                    "objective": objective})
        except Exception:
            body = '<p class="empty">%s</p>' % html.escape(REPORT_FAILURE_COPY)
        title = "Retention & trends"
        if objective:
            title = "Objective report"
        elif subject:
            title = "Subject report"
        page = presentation.surface_shell(
            title, body, theme_css=theme_block,
            back={"href": "/", "label": "itembank"})
        handler.send_html(page.encode("utf-8"))
        return
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
    theme_block = theme.theme_css(settings.load_settings(handler.root))
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
    # The gate outcome split (06.2-UI-SPEC section 11, GATE-06): the
    # report-surface readout, derived from the evidence log at request
    # time -- never stored, and never rendered in the reading column.
    # The lesson's declared check->mode map is what marks a pair as a
    # required gate (a recommended gate is excluded by construction).
    data = read_session(path)
    bank_path = data.get("bank")
    gate_html = ""
    if bank_path and os.path.exists(bank_path):
        les = parse_lesson(bank_path)
        gate_modes = {}
        if les:
            for cid in lesson._check_ids(les):
                gate_modes[cid] = les.get("gate") or "recommended"
        split = evidence.gate_outcome_split(
            evidence.log_path(os.path.dirname(bank_path)),
            os.path.basename(bank_path), data.get("session_id", ""),
            gate_modes=gate_modes)
        gate_html = _gate_outcome_html(split)
    page = presentation.surface_shell(
        "itembank report", body + gate_html, theme_css=theme_block,
        back={"href": "/", "label": "itembank"})
    handler.send_html(page.encode("utf-8"))


def _gate_outcome_html(split):
    """The gate outcome split readout (06.2-UI-SPEC section 11): a plain
    Ledger-voice table under the stated denominator, no target, no streak,
    no percentage-fill bar against a 100% track. The empty state renders
    the denominator line and no ratio."""
    rows = ""
    if split["denominator"]:
        for label, count, share in (
                ("cleared", split["cleared"], split["share_cleared"]),
                ("skipped", split["skipped"], split["share_skipped"])):
            share_text = ("%d%%" % round(share * 100)) if share is not None \
                else "\u2014"
            rows += ("<tr><td>%s</td><td>%d</td><td>%s</td></tr>"
                     % (html.escape(label), count, share_text))
        table = ("<table><thead><tr><th>Outcome</th><th>Count</th>"
                 "<th>Share</th></tr></thead><tbody>%s</tbody></table>" % rows)
    else:
        table = ""
    return ('<div class="gate-outcome"><p class="status" data-field='
            '"gate-denominator">%s</p>%s<p class="status" data-field='
            '"gate-exclusion">%s</p></div>'
            % (html.escape(lesson.GATE_DENOMINATOR_COPY.format(
                n=split["denominator"])), table,
               html.escape(lesson.GATE_EXCLUSION_COPY)))


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
    startup, rendered through the shared presentation shell with the
    per-render theme block (plan 04-04 Task 2). The page distinguishes the
    populated case, the no-configured-banks/plans case, and stem collisions
    (files that were found but are not served because another file shares
    their stem) as a labelled warning with recovery actions.
    """
    banks, plans = handler.banks, handler.plans
    theme_block = theme.theme_css(settings.load_settings(handler.root))
    stems = sorted(set(banks) | set(plans), key=str.lower)
    if stems:
        report_links = sessions_by_bank(handler.root, banks)
        rows = []
        for stem in stems:
            esc = html.escape(stem)
            if stem in banks:
                session_id = report_links.get(stem)
                link = ('\n    <a class="go secondary" data-action-secondary '
                        'href="/report?session=%s">View report</a>'
                        % html.escape(session_id)) if session_id else ""
                row = BANK_ROW.replace("__STEM__", esc).replace("__REPORT_LINK__", link)
            else:
                row = PLAN_ROW.replace("__STEM__", esc)
            rows.append(row)
        body = "\n".join(rows)
        if handler.collisions:
            losers = sorted(stem for _, _, loser in handler.collisions
                            for stem in [os.path.splitext(
                                os.path.basename(loser))[0]])
            body += presentation.state_panel({
                "kind": "warn",
                "status": ("Some files were not served because another file "
                           "shares their name: %s. The served file wins; "
                           "rename one of them and restart the daemon to "
                           "make it available."
                           % ", ".join(losers)),
            })
    else:
        served_dir = html.escape(os.path.abspath(handler.root))
        body = EMPTY_STATE.replace("__DIR__", served_dir)
    page = presentation.surface_shell("itembank", body, theme_css=theme_block)
    handler.send_html(page.encode("utf-8"))


def handle_marker(handler):
    """`GET /__itembank__` -- the identifying response plan 02-06's
    detect-and-attach probe looks for.
    """
    handler.send_json({"itembank": True})


def _client_is_loopback(handler):
    """True when the request's remote address is loopback -- the only client
    allowed to mutate host settings or open a host-side picker dialog. The
    daemon may bind 0.0.0.0 under `--lan` (T-04-13/T-04-14), so the *client
    address*, not the bind host, is the authority here.
    """
    return handler.client_address[0] in ("127.0.0.1", "::1")


def _origin_netloc(origin):
    """`(hostname, port)` parsed from an Origin or Host header value, with
    the scheme's default port applied when none is spelled out -- so
    `http://127.0.0.1:8730` and `127.0.0.1:8730` compare equal, and a URL
    that spells its default port out does not read as a different origin.
    """
    if "://" not in origin:
        origin = "//" + origin
    parts = urllib.parse.urlsplit(origin)
    host = (parts.hostname or "").lower()
    try:
        port = parts.port
    except ValueError:
        port = None
    if port is None:
        port = 443 if parts.scheme == "https" else 80
    return host, port


def _same_origin(handler):
    """Same-origin check applied when an `Origin` header is present: the
    page's own origin (the request `Host`) is the only one allowed. A
    request with no `Origin` (CLI/curl-style clients) is accepted here and
    still must satisfy the loopback policy below.
    """
    origin = handler.headers.get("Origin")
    if not origin:
        return True
    host = handler.headers.get("Host") or ""
    if not host:
        return False
    return _origin_netloc(origin) == _origin_netloc(host)


def _reject_cross_origin(handler):
    """Refuse a state-changing request whose `Origin` is not the page's own
    host -- the first half of the authority model `handle_theme_post`
    established (T-04-13/T-04-14). A request with no `Origin` (CLI/curl-style
    clients) is accepted here and still must satisfy the loopback policy
    where one applies.
    """
    if not _same_origin(handler):
        handler.send_error(403, "cross-origin request refused")
        return True
    return False


def _reject_cross_origin_write(handler):
    """The full authority gate for a mutating route, mirroring
    `handle_theme_post`: same-origin when an Origin is present plus a
    loopback client. A `--lan` daemon binds 0.0.0.0 and exposes every
    mutating day route to the network, so writes are loopback-only exactly
    like theme save/reset -- a phone may read the cockpit but never tick a
    lane, open a host-side editor, or rewrite a plan for another device.
    """
    if _reject_cross_origin(handler):
        return True
    if not _client_is_loopback(handler):
        handler.send_error(403, "day write requires a loopback client")
        return True
    return False


THEME_ACTIONS = ("preview", "pick", "save", "reset")
THEME_ALLOWED_FIELDS = ("action", "source", "confirm")


def handle_settings_get(handler):
    """`GET /settings` -- the browser half of D-05 through D-07: one quiet
    Theme section where the learner previews, natively picks or browser-picks,
    saves, and resets the shared source accent. The page is generated by
    `theme.theme_page(config)` from the daemon root's own validated settings
    -- the same per-render generator every other page consumes -- and carries
    no validator of its own (the route is the validator's only browser twin).
    """
    try:
        cfg = settings.load_settings(handler.root)
    except SystemExit as exc:
        handler.send_server_error(RuntimeError(str(exc.code)))
        return
    handler.send_html(theme.theme_page(cfg).encode("utf-8"))


def handle_theme_post(handler):
    """`POST /api/theme` -- the browser twin of the `itembank theme` CLI,
    accepting exactly the four fixed JSON shapes from plan 04-04's
    `<interfaces>` block: `preview`, `pick`, `save`, and `reset`. Every
    token is derived server-side through the same theme helpers the CLI
    uses; no CSS, path, rendered pair, or override field is ever read
    (T-04-16). Preview is non-mutating; pick/save/reset require a loopback
    client, and every request with an `Origin` header must be same-origin
    (T-04-13, T-04-14). The native picker runs in the tested
    source/`.pyz` child process via `launcher.run_native_picker` -- never
    Tk inside this request thread -- and a failed/cancelled child reads as
    `available:false` with the browser fallback reason, keeping the page's
    color input usable.
    """
    if not _same_origin(handler):
        handler.send_error(403, "cross-origin theme request refused")
        return
    data, failed = api_read_json(handler)
    if failed:
        return
    action = data.get("action")
    if action not in THEME_ACTIONS:
        handler.send_error(400, "action must be one of %s"
                           % "|".join(THEME_ACTIONS))
        return
    if action != "preview" and not _client_is_loopback(handler):
        handler.send_error(403, "%s requires a loopback client" % action)
        return
    extra = sorted(k for k in data if k not in THEME_ALLOWED_FIELDS)
    if extra:
        handler.send_error(
            400, "field %r is not accepted by /api/theme; only action, source, "
            "and confirm are read" % extra[0])
        return
    try:
        if action == "preview":
            handler.send_json(theme.theme_preview(data.get("source", "")))
            return
        if action == "pick":
            cfg = settings.load_settings(handler.root)
            result = launcher.run_native_picker(cfg["accent"]["source"])
            if result["available"]:
                result["preview"] = theme.theme_preview(result["source"])
            result["saved"] = False
            handler.send_json(result)
            return
        if action == "save":
            source = data.get("source")
            src = theme.normalize_source(source)
            if src is None:
                handler.send_error(
                    400, "settings.invalid_value: %r is not an opaque #RRGGBB "
                    "color" % source)
                return
            theme.persist_source(handler.root, src)
            handler.send_json({"saved": True, "source": src,
                               "preview": theme.theme_preview(src)})
            return
        if action == "reset":
            if data.get("confirm") != "RESET":
                handler.send_error(
                    400, "theme reset requires literal confirmation RESET")
                return
            theme.persist_source(handler.root, theme.DEFAULT_ACCENT)
            handler.send_json({"saved": True, "source": theme.DEFAULT_ACCENT,
                               "preview": theme.theme_preview(
                                   theme.DEFAULT_ACCENT)})
            return
    except SystemExit as exc:               # settings helpers exit on bad files
        handler.send_error(400, str(exc.code))
        return
    except Exception as exc:                # never let a bad POST kill the daemon
        handler.send_server_error(exc)
        return


def handle_quiz_get(handler, stem):
    """`GET /quiz/<stem>` -- the quiz page for one bank, resolved through the
    startup allowlist and rendered by the existing `quiz.page_for()`. No key
    data is sent: `serve=True` is what makes `page_for` omit it. The page
    receives the same per-render theme block as index/report/settings, so
    every surface reads the one palette (D-04, plan 04-04 Task 2).
    """
    path = handler.banks.get(stem)
    if path is None:
        handler.send_not_found(stem)
        return
    qs = load(path)
    lesson = parse_lesson(path)
    lesson_slugs = set(h["slug"] for h in lesson["headings"]) if lesson else set()
    sess = handler.sessions.get(stem) or {}
    theme_block = theme.theme_css(settings.load_settings(handler.root))
    _, page = quiz.page_for(path, qs, serve=True, reveal=False,
                            post_path="/quiz/%s/answer" % stem,
                            bank_stem=stem, mode=sess.get("mode", "practice"),
                            lesson_base="/lesson/%s" % stem,
                            lesson_slugs=lesson_slugs, theme_css=theme_block,
                            assist=True)
    handler.send_html(page.encode("utf-8"))


def handle_quiz_answer(handler, stem):
    """`POST /quiz/<stem>/answer` -- the legacy served-page answer route,
    now a compatibility wrapper over the one session adapter (06-02 Task 3):
    it resolves the API session `/api/start` created for this bank stem and
    submits through `session.do_action`, so there is exactly one scoring,
    persistence and policy path for the served browser. `cmd_serve`'s
    progress line and attempt-file regeneration are preserved through the
    scoped session config's `_refresh_attempt_view`.
    """
    if _reject_cross_origin(handler):
        return
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
        # Resolve the JSON session the served page started through
        # /api/start (its session_id was registered against this stem), so
        # the legacy route and the API route share one session file.
        api_id = sess.get("api_session_id")
        session_file = api_session_path(handler, api_id) if api_id else None
        if session_file is None:
            # A legacy client that never called /api/start (or a fresh page
            # before its start call landed) gets a JSON session created for
            # this stem right here -- same session.do_start path, same
            # registration, so the page and the API never diverge.
            # selection_mode is the Phase 7 composition axis, separate from
            # the feedback mode (D-01): a drill/remediation sitting composes
            # with the practice composition unless one was chosen explicitly.
            spec = {"objective": "", "count": len(qs), "seed": 0,
                    "selection_mode": sess.get("selection_mode", "practice")}
            out = os.path.join(os.path.abspath(handler.root), "_attempts",
                               "session_%s.json" % uuid.uuid4().hex[:12])
            try:
                created = session.do_start(path, spec, sess.get("mode", "practice"),
                                           out, False)
            except SystemExit as exc:
                handler.send_error(400, str(exc.code))
                return
            api_id = created["session_id"]
            sess["api_session_id"] = api_id
            session_file = out
        result = session.do_action(
            session_file, {"kind": "submit", "answer": data.get("response")},
            confidence=None, renderer_meta=None, elapsed_ms=elapsed_ms)
        try:
            pre3 = read_session(session_file)
            legacy_mode = pre3.get("mode")
        except Exception:
            legacy_mode = None
        if legacy_mode in ("diagnostic", "exam"):
            # D-12/D-13: the legacy served route also withholds verdicts.
            result.pop("score", None)
            result.pop("explain", None)
        if result.get("action") in ("advance", "complete") and q is not None:
            result["explain"] = explain_payload(q, bool(sess.get("reveal")))
        _refresh_attempt_view(sess, api_id, qs, path)
        payload = result
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


def handle_katex_asset(handler, name):
    """`GET /assets/katex/<name>` -- the one static-asset route (09-04).
    The name is resolved through the closed `KATEX_ASSETS` map (a URL suffix
    to a vendored archive-relative path and MIME type) and the bytes come
    from `resources.read_bytes()`, the same checkout/archive reader every
    other bundled resource uses. The name is never joined to a filesystem
    path: an unknown, encoded, nested, traversal, or query-manipulated name
    is a plain 404, and only names the reviewed CSS actually references
    exist in the map (T-09-09).
    """
    entry = KATEX_ASSETS.get(name)
    if entry is None:
        handler.send_not_found(name)
        return
    relpath, mime = entry
    try:
        body = resources.read_bytes(relpath)
    except OSError:
        handler.send_not_found(name)
        return
    handler.send_bytes(body, mime)
def _resolve_check(qs, check_id):
    """The one check-item resolution: by positional id or opaque [ID:], the
    same set the linter's lesson.check_ref_unknown accepts (D-01)."""
    for q in qs:
        if q["id"] == check_id or q.get("item_id") == check_id:
            return q
    return None


def _gate_answer_from_form(q, fields):
    """Serialise a gate band form submission into the answer shape the one
    scorer (`runtime.score_response`) and the one writer
    (`evidence.response_event`) expect -- the same shape `submit --answer`
    takes, so a lesson-gate attempt and a quiz attempt are the same object
    to every consumer (D-08). `fields` is `parse_qs`-shaped ({name:
    [values]}) because multi-select checkboxes repeat their name."""
    def one(name):
        vals = fields.get(name) or []
        return vals[-1] if vals else ""
    t = q["type"]
    if t in ("mc", "multi"):
        values = [v for v in (fields.get("option") or []) if v]
        if t == "mc":
            return values[0] if values else ""
        return sorted(set(values))
    if t in ("table", "dnd"):
        out = {}
        for i in range(len(q.get("rows") or [])):
            v = one("row_%d" % i)
            if v:
                out[str(i)] = v
        return out
    if t == "build":
        out = []
        for i in range(len(q.get("steps") or [])):
            v = one("step_%d" % i)
            if v:
                out.append(v)
        return out
    return one("answer")


def _section_after_check(lesson, check_id):
    """The slug of the section that follows the one carrying the check, or
    None when the check sits in the last section -- the gate-reveal focus
    target (06.2-UI-SPEC section 7.1)."""
    for idx, h in enumerate((lesson or {}).get("headings") or []):
        if "[!CHECK: %s]" % check_id in (h.get("body") or ""):
            rest = (lesson.get("headings") or [])[idx + 1:]
            return rest[0]["slug"] if rest else None
    return None


def _log_unreachable(bank_dir):
    """True when the evidence log cannot be appended to -- the runtime
    surface a live gate depends on is unavailable, so the band states the
    section-12.1 copy and never reveals (C9, "no reveal without its
    event"). The probe is cheap and never writes: the log's parent must be
    creatable as a directory and the log must not be a directory."""
    log = evidence.log_path(bank_dir)
    parent = os.path.dirname(log)
    try:
        if os.path.isdir(log):
            return True
        os.makedirs(parent, exist_ok=True)
    except OSError:
        return True
    try:
        if not os.path.exists(log):
            return not os.access(parent, os.W_OK)
        return not os.access(log, os.W_OK)
    except OSError:
        return True


def _lesson_gate_ctx(handler, stem, path, qs, les, print_mode=False):
    """The Phase 6.2 gate context one lesson render needs, built exactly
    once per request: the resolved policy (gate_policy setting -> declared
    [GATE:] -> the diagnostic/exam degrade), the per-check states derived
    from the evidence log (D-06, never a second store), the item resolver,
    and the provenance the band needs.

    Returns None when the lesson renders ungated (gate_policy: off, a
    declared [GATE: off], or no session) -- the 3.1 compatibility floor.
    The print path returns a ctx with policy "off" and print True so every
    check prints as 3.1's D1 labelled rule (06.2-UI-SPEC section 8.2).
    """
    bank_dir = os.path.dirname(os.path.abspath(path)) or "."
    cfg = settings.load_settings(bank_dir)
    reader = cfg.get("reader") or {}
    gate_policy = reader.get("gate_policy", "as-authored")
    skip_setting = reader.get("gate_skip", "always")
    as_authored = (les or {}).get("gate") or "recommended"
    sess = handler.sessions.get(stem) or {}
    mode = sess.get("mode", "practice")
    session_id = sess.get("session_id", "reader")
    log = evidence.log_path(bank_dir)
    if print_mode:
        return {"policy": "off", "as_authored": as_authored, "states": {},
                "attempted": {}, "resolve": _resolve_check_factory(qs),
                "skip": "off", "degraded": False, "unreachable": False,
                "print": True, "stem": stem, "bank": os.path.basename(path),
                "session_id": session_id, "log": log, "mode": mode}
    if gate_policy == "off" or as_authored == "off":
        return None
    degraded = mode in ("diagnostic", "exam") and as_authored == "required"
    policy = "recommended" if degraded else as_authored
    resolve = _resolve_check_factory(qs)
    states = {}
    attempted = {}
    for cid in lesson._check_ids(les):
        states[cid] = evidence.gate_state(log, session_id, cid)
        q = resolve(cid)
        if q is not None:
            attempted[cid] = any(
                ev.get("event_type") == evidence.RESPONSE_EVENT_TYPE
                and ev.get("session_id") == session_id
                and (ev.get("item_ref") == cid
                     or ev.get("item_id") == cid)
                for ev in evidence.live_events(log))
    return {"policy": policy, "as_authored": as_authored, "states": states,
            "attempted": attempted, "resolve": resolve,
            "skip": skip_setting, "degraded": degraded,
            "unreachable": _log_unreachable(bank_dir),
            "print": False, "stem": stem, "bank": os.path.basename(path),
            "session_id": session_id, "log": log, "mode": mode}


def _resolve_check_factory(qs):
    by_id = {q["id"]: q for q in qs}
    by_id.update({q["item_id"]: q for q in qs if q.get("item_id")})
    return lambda cid: by_id.get(cid)


def handle_lesson_get(handler, stem):
    """`GET /lesson/<stem>` -- the lesson reader for one bank, resolved
    through the startup allowlist and rendered by `lesson.lesson_page()`.
    No second copy of the lesson template lives here; the handler generates
    no HTML of its own. The page is daemon-served (runtime=True, so [!KEY]
    cards carry their Add-to-review form) and honours `?print=drill` as the
    drill-print pass (03.1-03 Task 3); `?print=1` forces the gate policy
    off so a gated lesson prints complete and ungated (06.2-UI-SPEC
    section 8.2). A `?focus=<slug>` query (from a 303 after a gate reveal)
    renders that section's h2 with tabindex=-1 autofocus (section 7.1).
    """
    path = handler.banks.get(stem)
    if path is None:
        handler.send_not_found(stem)
        return
    qs = load(path)
    les = parse_lesson(path)
    params = urllib.parse.parse_qs(urllib.parse.urlsplit(handler.path).query)
    drill = "drill" in (params.get("print") or [])
    # 09-04: the lesson reader resolves the subject profile exactly as a
    # session would (subjects.select_profile over the bank; the stored
    # snapshot is consumed once a session id exists -- 09-05 wires the
    # explicit id and the snapshot through the clients). Only the profile's
    # lesson.math flag turns the local KaTeX enhancement on; EMT/plain
    # profiles stay ordinary reader output (D-08).
    try:
        profile = subjects.select_profile(
            qs, subjects.load_registry(
                os.path.dirname(os.path.abspath(path)) or "."))
    except subjects.SubjectProfileError:
        profile = None
    print_mode = bool(params.get("print"))
    gate = _lesson_gate_ctx(handler, stem, path, qs, les,
                            print_mode=print_mode)
    focus = (params.get("focus") or [""])[0] or None
    # The composed announcement (06.2-UI-SPEC section 7.2): the gate band
    # contributes exactly one clause after a reveal -- the reveal clause
    # after a cleared check, the skip string after a skip. Composed here so
    # the redirect target carries the intent and the page renders the text
    # inside the single role=status region.
    reveal = (params.get("reveal") or [""])[0] or None
    announce = None
    if reveal == "skip":
        announce = lesson.SKIP_RECORDED_COPY
    elif reveal == "check":
        announce = lesson.REVEAL_CLAUSE_COPY
    page = lesson.lesson_page(path, qs, les, runtime=True, drill=drill,
                              gate=gate, focus=focus, announce=announce,
                              profile=profile)
    handler.send_html(page.encode("utf-8"))


def handle_lesson_check(handler, stem):
    """`POST /lesson/<stem>/check` -- the gate band's check submission:
    scores through `runtime.score_response()` via the one shared
    `quiz.record_gate_check` path, records ordinary response evidence with
    context="lesson_gate" (D-08), and issues a 303 to the re-rendered
    lesson so a reload never re-submits the check (section 7.1). Under
    required with a cleared check the next section renders and focus
    targets its h2; the composed announcement appends `The next section is
    below.` (7.2).
    """
    if _reject_cross_origin_write(handler):
        return
    path = handler.banks.get(stem)
    if path is None:
        handler.send_not_found(stem)
        return
    try:
        qs = load(path)
        les = parse_lesson(path)
        fields = handler.read_form()
        check_id = (fields.get("check") or [""])[-1]
        q = _resolve_check(qs, check_id)
        if q is None:
            handler.send_error(404, "no item %r in this bank" % check_id)
            return
        answer = _gate_answer_from_form(q, fields)
        sess = handler.sessions[stem]
        bank_dir = os.path.dirname(os.path.abspath(path)) or "."
        log = evidence.log_path(bank_dir)
        session_id = sess.get("session_id", "reader")
        score = quiz.record_gate_check(
            path, check_id, answer, mode=sess.get("mode", "practice"),
            session_id=session_id)
        if score is None:
            handler.send_error(404, "no item %r in this bank" % check_id)
            return
        gate = _lesson_gate_ctx(handler, stem, path, qs, les)
        next_slug = None
        if gate is not None and gate["policy"] == "required" \
                and not gate.get("degraded") \
                and evidence.gate_state(log, session_id, check_id) == "cleared":
            next_slug = _section_after_check(les, check_id)
        if next_slug:
            target = ("/lesson/%s?focus=%s&reveal=check#%s"
                      % (stem, next_slug, next_slug))
        else:
            target = "/lesson/%s" % stem
        handler.send_redirect(target)
    except Exception as exc:
        handler.send_server_error(exc)


def handle_lesson_skip(handler, stem):
    """`POST /lesson/<stem>/skip` -- the recorded-skip action (D-11, C17):
    appends exactly one `gate_skip` event (never a response, never a hint
    tier), re-renders with the next section appended, and leaves the band
    live and answerable. A skip that was not recorded never advances the
    reading position (section 6.3): the event is written through the one
    shared `quiz.record_gate_skip` path before the redirect, and an
    unwritable log renders the section-12.1 copy instead of revealing.
    """
    if _reject_cross_origin_write(handler):
        return
    path = handler.banks.get(stem)
    if path is None:
        handler.send_not_found(stem)
        return
    try:
        qs = load(path)
        les = parse_lesson(path)
        fields = handler.read_form()
        check_id = (fields.get("check") or [""])[-1]
        gate = _lesson_gate_ctx(handler, stem, path, qs, les)
        if gate is None or gate.get("degraded") or gate.get("unreachable"):
            # A degraded sitting records no gate_skip (there is nothing to
            # skip); an unreachable runtime must not reveal without its
            # event. Re-render with the honest copy (section 12.1).
            page = lesson.lesson_page(path, qs, les, runtime=True, gate=gate)
            handler.send_html(page.encode("utf-8"))
            return
        sess = handler.sessions[stem]
        status = quiz.record_gate_skip(
            path, check_id, mode=sess.get("mode", "practice"),
            session_id=sess.get("session_id", "reader"))
        if status is None:
            handler.send_error(404, "no item %r in this bank" % check_id)
            return
        if status == "off":
            handler.send_error(400, "an off lesson offers no skip")
            return
        next_slug = _section_after_check(les, check_id)
        if next_slug:
            target = ("/lesson/%s?focus=%s&reveal=skip#%s"
                      % (stem, next_slug, next_slug))
        else:
            target = "/lesson/%s?reveal=skip" % stem
        handler.send_redirect(target)
    except Exception as exc:
        handler.send_server_error(exc)


def handle_key_review(handler, key_id):
    """`POST /key/<id>/review` -- add a [!KEY] card to review. The key id is
    resolved against the daemon's scanned banks' parsed key blocks (never
    joined to a filesystem path), the existing loopback authority gate
    applies, and a `key_review` event is recorded through the one evidence
    writer (D-19, T-031-11). The status region announces `Added to review.`
    once -- no streak, no count-up, no celebration (C17)."""
    if _reject_cross_origin(handler):
        return
    for stem, path in handler.banks.items():
        keys = parse_key_blocks(path)
        if not any(k.get("id") == key_id for k in keys):
            continue
        sess = handler.sessions.get(stem) or {}
        status = lesson.record_key_review(
            path, key_id,
            mode=sess.get("mode", "practice"),
            session_id=sess.get("session_id", "reader"))
        if status is None:
            handler.send_not_found(key_id)
            return
        handler.send_html(
            ('<div class="status" role="status">%s</div>' % html.escape(status))
            .encode("utf-8"))
        return
    handler.send_not_found(key_id)


def handle_gloss_get(handler, stem, slug):
    """`GET /gloss/<stem>/<slug>` -- one term's definition from the bank's
    `## TERMS` block, gated server-side by `glossable()` before any
    definition leaves the process (D-20), with a `term_lookup` event
    recorded through the one evidence writer (D-19, UI-SPEC §8.3/§8.5).

    A suppressed term returns the same bare 404 an unknown slug gets, with
    no event: per-term disclosure is exactly what §8.4 forbids, and an
    indistinguishable 404 is how the route keeps that promise structurally.
    The session_id and mode come from the daemon's own per-bank session
    bookkeeping when present, falling back to a stable reader identity and
    the practice default -- the route records provenance, never a guess.
    """
    path = handler.banks.get(stem)
    if path is None:
        handler.send_not_found(stem)
        return
    status, record = lesson.gloss_lookup(path, slug)
    if status != "ok":
        handler.send_not_found(slug)
        return
    sess = handler.sessions.get(stem) or {}
    bank_dir = os.path.dirname(os.path.abspath(path)) or "."
    event = evidence.term_lookup_event(
        session_id=sess.get("session_id", "reader"),
        bank=os.path.basename(path),
        term_slug=lesson_slug(slug),
        mode=sess.get("mode", "practice"),
        source="session")
    evidence.append_event(evidence.log_path(bank_dir), event)
    handler.send_html(lesson.gloss_page(stem, record, lesson_slug(slug))
                      .encode("utf-8"))


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
    # 10-05: the daemon's scanned banks ride on the day state so the Today
    # panel can offer focused starts and lesson recovery; the scoped
    # `itembank day` launch has none, and the page degrades honestly.
    state["banks"] = dict(handler.banks)
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
    if _reject_cross_origin_write(handler):
        return
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
    if _reject_cross_origin_write(handler):
        return
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


def _draft_hash(edits):
    """One canonical hash of a submitted draft, shared by issuance and the
    force request: sorted keys, JSON-encoded key/value pairs joined with `,`.
    The browser computes the identical string client-side, so a token minted
    for one draft can never be spent on a different draft (T-04-23).
    """
    parts = []
    for key in sorted(edits):
        parts.append(json.dumps(key, ensure_ascii=False, sort_keys=True) + ":" +
                     json.dumps(edits[key], ensure_ascii=False, sort_keys=True))
    return hashlib.sha256(",".join(parts).encode("utf-8")).hexdigest()


def _issue_day_force_token(handler, stem, stale_revision, current_revision, edits):
    """Mint one cryptographically random, one-use force token bound to the
    plan stem, the stale revision the browser edited against, the current
    revision the conflict reported, and the exact draft hash (T-04-23). Any
    earlier token for the same stem is dropped -- another conflict always
    returns to recovery rather than reusing an old gate.
    """
    token = secrets.token_hex(32)
    # The browser re-submits against the conflict's current revision, so the
    # token is bound to that revision as the revision a force request must
    # present; the fresh disk recheck still happens inside day_document.save.
    handler.day_force_tokens[token] = {
        "stem": stem, "stale_revision": current_revision,
        "current_revision": current_revision,
        "draft_hash": _draft_hash(edits)}
    return token


def _consume_day_force_token(handler, stem, token, stale_revision, edits):
    """Validate and consume one force token. Returns `(ok, reason)`; `ok` is
    False -- and nothing is consumed -- for an unknown token, a replay, a
    token minted for another plan, a stale-revision mismatch, or a draft that
    changed since issuance. The token is removed before the save so a replay
    can never pass even if the file were somehow unchanged (T-04-23).
    """
    bound = handler.day_force_tokens.get(token)
    if bound is None:
        return False, "no force token was issued for this conflict"
    if bound["stem"] != stem:
        return False, "force token belongs to another plan"
    if bound["stale_revision"] != stale_revision:
        return False, "force token was issued for a different revision"
    if bound["draft_hash"] != _draft_hash(edits):
        return False, "the draft changed after the conflict; reapply and retry"
    del handler.day_force_tokens[token]
    return True, None


def handle_day_edit(handler, stem):
    """`POST /day/<stem>/edit` -- the structured plan editor (plan 04-06).
    The normal branch delegates to `day.apply_day_edit`, the one surface
    wrapper around `day_document.save`. The force branch additionally
    requires a separate explicit confirmation plus a one-use token bound to
    the stem, stale revision, current revision, and draft hash; the token is
    consumed before the save and `day_document.save` performs its own fresh
    revision recheck, so a third concurrent version still produces a new
    no-write conflict (T-04-22, T-04-23).
    """
    if _reject_cross_origin_write(handler):
        return
    if stem not in handler.plans:
        handler.send_not_found(stem)
        return
    try:
        data = handler.read_json()
        unknown = [k for k in data if k not in DAY_EDIT_ALLOWED_FIELDS]
        if unknown:
            handler.send_json({"status": "invalid",
                               "reason": "unexpected fields: %s"
                                         % ", ".join(sorted(unknown))})
            return
        if data.get("force_token") and not data.get("force"):
            handler.send_json({"status": "invalid",
                               "reason": "a force token without a force "
                                         "request is refused"})
            return
        edits = data.get("edits")
        revision = data.get("revision")
        if not isinstance(edits, dict) or not all(
                isinstance(v, str) for v in edits.values()):
            handler.send_json({"status": "invalid",
                               "reason": "edits must be a map of column to "
                                         "single-line text"})
            return
        if not isinstance(revision, str) or not revision:
            handler.send_json({"status": "invalid",
                               "reason": "a SHA-256 revision is required"})
            return
        state = _plan_day_state(handler, stem)
        revision = data["revision"]
        edits = data["edits"]
        if data.get("force"):
            if data.get("confirmation") != (
                    "I understand this replaces these edited cells using the "
                    "latest plan version."):
                handler.send_json({"status": "invalid",
                                   "reason": "force requires the explicit "
                                             "confirmation statement"})
                return
            token = data.get("force_token")
            if not isinstance(token, str) or not token:
                handler.send_json({"status": "invalid",
                                   "reason": "force requires a one-use token "
                                             "issued by the conflict"})
                return
            ok, reason = _consume_day_force_token(
                handler, stem, token, revision, edits)
            if not ok:
                handler.send_json({"status": "invalid", "reason": reason})
                return
            result = day.apply_day_edit(state, data, force=True)
            if result.get("status") == "conflict":
                # The consumed token is gone; another conflict returns to
                # recovery without a reusable gate (T-04-23).
                result.pop("force_token", None)
            handler.send_json(result)
            return
        result = day.apply_day_edit(state, data)
        if result.get("status") == "conflict":
            result["force_token"] = _issue_day_force_token(
                handler, stem, revision, result.get("revision", ""), edits)
            result["force_draft_hash"] = _draft_hash(edits)
        handler.send_json(result)
    except Exception as exc:
        handler.send_server_error(exc)


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
API_FORBIDDEN_FIELDS = ("session", "bank_path", "out",
                        "item_id", "score", "key", "explanation",
                        # Plan 08-05 authority fields (D-09): a client can
                        # never smuggle a tier, backend profile, fact
                        # manifest, candidate body, proposal, marker, or
                        # verdict onto the wire -- those exist only on the
                        # runtime side of the boundary.
                        "tier", "profile", "facts", "candidate", "proposal",
                        "marker", "verdict")

# Phase 6 authority-shaped fields (T-06-12) rejected on the action routes
# (`/api/submit`, `/api/hint`) by name before any policy work: mode, tier,
# correct, advance, reveal, and the concrete visual/canvas action/observation
# state that belongs exclusively to Phase 06.1. Kept separate from
# API_FORBIDDEN_FIELDS because `/api/start` legitimately accepts `mode`.
API_ACTION_FORBIDDEN_FIELDS = ("mode", "tier", "correct", "advance",
                               "reveal", "observation", "canvas_state")

# The only renderer handoff Phase 6 accepts: one opaque UTF-8 string of at
# most 256 bytes, discarded before policy/persistence/evidence/logs
# (D-12/T-06-12). Mirrors surfaces/session.RENDERER_META_MAX_BYTES.
RENDERER_META_MAX_BYTES = 256


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
            try:
                # A session written by a NEWER build (or otherwise invalid)
                # must not make every other session unaddressable, nor kill
                # the request thread via read_session's sys.exit -- the index
                # skips it and the handler's own read reports the 4xx.
                upgrade_session(data)
            except SystemExit:
                continue
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
    "seed", "focus", "selection_mode", "preview"}`. `bank` is resolved through the same stem allowlist the GET
    routes use: a value that is not a key in `handler.banks` is a 404, full
    stop -- it is never joined to a path, never normalised, never checked
    for traversal segments, because it is never treated as a path at all.
    `focus`, when present, is an item id (the `#<id>` fragment a lesson
    backlink carries); the sitting starts with that item first (D-09).
    `preview: true` (strictly the boolean) returns the selection's items and
    trace without starting a session -- no output path, no `_attempts/`
    write, no evidence append (D-14 keeps /api/* at four routes).
    The output path is computed server-side under `<root>/_attempts/`,
    exactly what `session.do_start` defaults to when no `out` is given;
    `out` is never read from the body (T-2-02).
    """
    if _reject_cross_origin(handler):
        return
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
    selection_mode = data.get("selection_mode", "practice")
    if selection_mode not in selection.SELECTION_MODES:
        selection_mode = "practice"
    objective = data.get("objective", "")
    if not isinstance(objective, str):
        objective = ""
    focus = data.get("focus")
    if not isinstance(focus, str) or not focus:
        focus = None
    # 10-05 (T-10-19): a focused start from Today carries the displayed
    # snapshot claim. The handler re-captures CURRENT evidence and
    # re-derives the snapshot at the displayed cutoff: the id is a pure
    # hash of (cutoff, zone, window, filters, settings, event identities),
    # so it matches exactly when no evidence has changed since the display
    # and differs on any change or forgery -- reject with refresh guidance
    # and NO session/event. A valid action derives every private authority
    # server-side (cap, weights, path, override); client cap/weight/path/
    # answer/hidden/model fields are never read here.
    snapshot = data.get("snapshot")
    if snapshot is not None:
        if not isinstance(snapshot, dict) or \
                not isinstance(snapshot.get("snapshot_id"), str) or \
                not snapshot["snapshot_id"]:
            handler.send_error(400, "snapshot must carry a non-empty "
                                    "snapshot_id")
            return
        log = evidence.log_path(os.path.dirname(os.path.abspath(path)) or ".")
        live = evidence.capture_events(log) if os.path.exists(log) else ()
        cfg = settings.load_settings(
            os.path.dirname(os.path.abspath(path)) or ".")
        try:
            cutoff = snapshot.get("cutoff") or None
            zone = snapshot.get("local_day_zone") or "UTC"
            weeks = (snapshot.get("window") or {}).get("weeks") or 4
            filters = snapshot.get("filters") or {}
            fresh = retention.capture(live, cutoff=cutoff, zone=zone,
                                      weeks=weeks, filters=filters, cfg=cfg)
        except Exception:
            handler.send_error(
                400, "Today\u2019s snapshot could not be re-derived; refresh "
                     "Today and try again. No session was started.")
            return
        if fresh["claim"]["snapshot_id"] != snapshot["snapshot_id"]:
            handler.send_error(
                400, "Today\u2019s snapshot is stale; refresh Today and try "
                     "again. No session was started.")
            return
    # The D-09 focus pin and the selection fields ride inside the spec dict
    # the working tree's `session.do_start(bank_path, spec, mode, out, force)`
    # takes -- the same signature `itembank start`'s own CLI path uses.
    spec = {"objective": objective, "count": count, "seed": seed,
            "selection_mode": selection_mode}
    if focus:
        spec["focus"] = focus
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
        if data.get("preview") is True:
            result = session.do_select(path, spec, False)
            result["preview"] = True
        else:
            result = session.do_start(path, spec, mode, out, False)
    except SystemExit as exc:
        handler.send_error(400, str(exc.code))
        return
    except Exception as exc:
        handler.send_server_error(exc)
        return
    # Register the API session against the allowlisted bank stem so a scoped
    # `itembank serve` launch can regenerate its configured attempt markdown
    # and print progress after every submit (plan 04-01 Test 4). A preview
    # has no session to register.
    if data.get("preview") is not True:
        sess_cfg = handler.sessions.get(bank)
        if sess_cfg is not None:
            sess_cfg["api_session_id"] = result["session_id"]
    handler.send_json(result)


def handle_api_override(handler):
    """`POST /api/override` -- `{"bank", "objective", "count", "seed",
    "mode", "selection_mode", "token"}`. The daemon twin of
    `itembank override` (plan 10-04, D-08): starts one additional sitting
    past a reached cap, but ONLY with the exact explicit confirmation phrase
    in `token`, and writes exactly one append-only cap_override event bound
    to the server-generated session id. The subject is derived server-side
    from the namespaced `objective` -- a client-supplied subject, cap,
    snapshot or override value is refused/ignored (T-10-14, T-10-15); a
    wrong or missing token, or an objective with no namespace, is a 400 and
    writes nothing. Same containment as every handle_api_*: cross-origin
    reject, api_read_json, SystemExit -> 400, Exception -> path-free 500.
    """
    if _reject_cross_origin(handler):
        return
    data, failed = api_read_json(handler)
    if failed:
        return
    bank = data.get("bank")
    path = handler.banks.get(bank) if isinstance(bank, str) else None
    if path is None:
        handler.send_not_found(bank if isinstance(bank, str) else "")
        return
    token = data.get("token")
    if not isinstance(token, str) or not token:
        handler.send_error(400, "override requires the exact explicit "
                                "confirmation token")
        return
    objective = data.get("objective", "")
    if not isinstance(objective, str) or not objective:
        handler.send_error(400, "override requires a namespaced objective so "
                                "the subject can be derived server-side")
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
    selection_mode = data.get("selection_mode", "practice")
    if selection_mode not in selection.SELECTION_MODES:
        selection_mode = "practice"
    spec = {"objective": objective, "count": count, "seed": seed,
            "selection_mode": selection_mode}
    out = os.path.join(os.path.abspath(handler.root), "_attempts",
                       "session_%s.json" % uuid.uuid4().hex[:12])
    try:
        result = session.do_start(path, spec, mode, out, False,
                                  override_token=token)
    except SystemExit as exc:
        handler.send_error(400, str(exc.code))
        return
    except Exception as exc:
        handler.send_server_error(exc)
        return
    sess_cfg = handler.sessions.get(bank)
    if sess_cfg is not None:
        sess_cfg["api_session_id"] = result["session_id"]
    handler.send_json(result)


def handle_api_lesson_complete(handler):
    """`POST /api/lesson-complete` -- `{"bank": "<stem>", "ref": "<heading>"}`.
    The daemon twin of `itembank lesson BANK --ref HEADING --complete`
    (plan 10-02, SCHED-04/D-24): the ONE explicit completion seam. The
    heading is resolved through the Phase 3 slugifier and reader (never a
    second parser, slugger, or a filesystem path from client input), the
    sorted unique objectives of items referencing it are discovered, one
    `lesson_complete` event is appended through the ONE evidence writer,
    and the derived next-review queue rows for that event are returned.
    Merely viewing/opening a lesson writes nothing; an unknown heading, a
    heading no item references with an [OBJECTIVE:] line, or a
    multi-subject reference set is refused with a named explanation and
    writes nothing. Same containment as every handle_api_*: cross-origin
    reject, api_read_json, SystemExit -> 400, Exception -> path-free 500.
    """
    if _reject_cross_origin(handler):
        return
    data, failed = api_read_json(handler)
    if failed:
        return
    bank = data.get("bank")
    path = handler.banks.get(bank) if isinstance(bank, str) else None
    if path is None:
        handler.send_not_found(bank if isinstance(bank, str) else "")
        return
    ref = data.get("ref")
    if not isinstance(ref, str) or not ref:
        handler.send_error(400, "lesson completion requires a ref: a "
                                "completion names exactly one Phase 3 "
                                "lesson heading")
        return
    try:
        qs = load(path)
        lesson = parse_lesson(path)
        slug = lesson_slug(ref)
        if lesson is None or not any(h["slug"] == slug
                                     for h in lesson["headings"]):
            handler.send_error(400, "no lesson heading matching %r in %s"
                                % (ref, os.path.basename(path)))
            return
        objectives = sorted({q.get("objective", "") for q in qs
                             if q.get("lesson_slug") == slug
                             and q.get("objective")})
        if not objectives:
            handler.send_error(
                400, "lesson.no_referenced_objective: no item referencing "
                     "%r carries an [OBJECTIVE:] line, so nothing can enter "
                     "the review queue" % (ref,))
            return
        subject = evidence.subject_of(objectives[0])
        if not subject or any(evidence.subject_of(o) != subject
                              for o in objectives):
            handler.send_error(
                400, "lesson.no_single_subject: items referencing %r must "
                     "share one namespaced subject to record a completion"
                     % (ref,))
            return
        zone = data.get("zone") if isinstance(data.get("zone"), str) \
            else "UTC"
        bank_dir = os.path.dirname(os.path.abspath(path)) or "."
        event = evidence.lesson_complete_event(
            session_id="reader", bank=os.path.basename(path),
            lesson_slug=slug, subject=subject, objectives=objectives,
            zone=zone)
        result = evidence.append_event(evidence.log_path(bank_dir), event)
        cfg = settings.load_settings(bank_dir)
        events = evidence.capture_events(evidence.log_path(bank_dir))
        snapshot = retention.capture(events, zone=zone, cfg=cfg)
        rows = [r for r in retention.lesson_queue(snapshot)
                if r["event_id"] == result["event_id"]]
    except SystemExit as exc:
        handler.send_error(400, str(exc.code))
        return
    except Exception as exc:
        handler.send_server_error(exc)
        return
    handler.send_json({
        "status": result["status"],
        "event_id": result["event_id"],
        "ref": ref,
        "subject": subject,
        "objectives": objectives,
        "queue": rows,
        "snapshot_id": snapshot["claim"]["snapshot_id"],
    })


def handle_api_next(handler):
    """`POST /api/next` -- `{"session_id": "<id>"}`. `session_id` is resolved
    through `session_index`; a miss is a 404.
    """
    if _reject_cross_origin(handler):
        return
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


def _scoped_session_for(handler, session_id):
    """The sessions-dict entry whose `api_session_id` matches `session_id`,
    or None. `/api/start` registers the API session against the allowlisted
    bank stem (plan 04-01 Task 2), so a scoped `itembank serve` launch can
    keep regenerating its configured attempt markdown and printing progress
    based on the API session id after every submit.
    """
    for cfg in handler.sessions.values():
        if cfg.get("api_session_id") == session_id:
            return cfg
    return None


def _refresh_attempt_view(cfg, session_id, qs, bank_path):
    """Regenerate the configured attempt markdown atomically from the evidence
    log after an API submit, using `evidence.render_attempt_md` -- the exact
    render the legacy route and the CLI use, never a second writer -- and print
    the scoped-serve progress line from the API session's own event count.
    """
    md = evidence.render_attempt_md(cfg["log"], session_id, qs, bank_path)
    tmp = cfg["out"] + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(md)
    os.replace(tmp, cfg["out"])
    if cfg.get("progress"):
        answered = len(set(ev["item_ref"]
                           for ev in evidence.session_events(cfg["log"], session_id)))
        sys.stdout.write("  %d/%d answered, saved\n" % (answered, len(qs)))
        sys.stdout.flush()
        if answered >= len(qs):
            print("\n  finished. Attempt file: %s" % cfg["out"])


def handle_api_submit(handler):
    """`POST /api/submit` -- `{"session_id": "<id>", "answer": ...}` or the
    normalized Phase 6 action envelope `{"action": {"kind": "submit",
    "answer": ...}}`, plus the optional opaque `renderer_meta` string (at
    most 256 UTF-8 bytes, discarded before policy, never persisted). The two
    answer representations are mutually exclusive (T-06-12).

    `answer` is passed through untouched (`session.do_action` normalizes it
    the same way the CLI's `--answer` string already was); `confidence`
    must be one of the three levels or absent.

    The current question is resolved server-side from the allowlisted session
    BEFORE `session.do_action` runs -- the cursor advances only when the
    runtime transition returns advance/complete. The server-issued
    `explain_payload` for that exact question is appended to the result under
    the scoped session's reveal policy and only for actions that legally
    release it (drill/practice advance/complete; diagnostic and exam never).
    A client field claiming an item id, score, key or explanation was already
    rejected by `api_read_json`'s forbidden-field gate (T-04-01/T-06-12).
    Finally, when this session was registered against a bank stem carrying a
    scoped `serve` launch, the configured attempt view is regenerated
    atomically and progress is printed from the API session's own evidence.
    """
    if _reject_cross_origin(handler):
        return
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
    renderer_meta = data.get("renderer_meta")
    if renderer_meta is not None and not isinstance(renderer_meta, str):
        handler.send_error(400, "renderer_meta must be a string or absent")
        return
    if isinstance(renderer_meta, str) and \
            len(renderer_meta.encode("utf-8")) > RENDERER_META_MAX_BYTES:
        handler.send_error(400, "renderer_meta must be at most %d UTF-8 bytes"
                           % RENDERER_META_MAX_BYTES)
        return
    action = data.get("action")
    if action is not None:
        if not isinstance(action, dict):
            handler.send_error(400, "action must be an object")
            return
        if action.get("kind") != "submit":
            handler.send_error(400, "action.kind must be 'submit' on /api/submit")
            return
        if "answer" in data and "answer" in action:
            handler.send_error(400, "answer given both top-level and inside action")
            return
        if "answer" not in action:
            handler.send_error(400, "action must carry answer")
            return
        # Extra authority-shaped keys inside the action are refused by name.
        bad = api_reject_path_fields(action)
        if bad or any(k in action for k in API_ACTION_FORBIDDEN_FIELDS):
            handler.send_error(400, "action carries an authority-shaped field")
            return
        answer = action.get("answer")
    else:
        answer = data.get("answer")
        # The legacy answer form must not smuggle authority fields either.
        if any(k in data for k in API_ACTION_FORBIDDEN_FIELDS):
            handler.send_error(400, "body carries an authority-shaped field")
            return
    # Pre-submit read: resolve the current question before do_submit advances
    # the cursor. Failures here are deliberately swallowed -- do_action itself
    # validates the session and reports the authoritative error.
    q = None
    qs = []
    bank_path = ""
    try:
        pre = read_session(path)
        bank_path = pre.get("bank") or ""
        if isinstance(bank_path, str) and bank_path:
            qs = load(bank_path)
            cursor = pre.get("cursor", -1)
            items = pre.get("items") or []
            idx = items[cursor] if isinstance(cursor, int) \
                and 0 <= cursor < len(items) else None
            if isinstance(idx, int) and 0 <= idx < len(qs):
                q = qs[idx]
    except Exception:
        q = None
    try:
        result = session.do_action(
            path, {"kind": "submit", "answer": answer},
            confidence=confidence, renderer_meta=renderer_meta)
    except SystemExit as exc:
        handler.send_error(400, str(exc.code))
        return
    except Exception as exc:
        handler.send_server_error(exc)
        return
    cfg = _scoped_session_for(handler, session_id)
    mode = None
    try:
        pre2 = read_session(path)
        mode = pre2.get("mode")
    except Exception:
        mode = None
    release_explain = result.get("action") in ("advance", "complete") and \
        mode in ("practice", "drill", "remediation")
    if q is not None and release_explain:
        result["explain"] = explain_payload(
            q, bool(cfg.get("reveal")) if cfg is not None else False)
    if mode in ("diagnostic", "exam") and result.get("action") != "advance":
        # D-12/D-13: diagnostic and unmarked exam responses carry no verdict,
        # answer, hint, explanation, or key -- the score is stripped here so
        # the served client cannot infer correctness before the release gate.
        result.pop("score", None)
        result.pop("explain", None)
    if cfg is not None and result.get("accepted") and qs:
        _refresh_attempt_view(cfg, session_id, qs, bank_path)
    handler.send_json(result)


def handle_api_hint(handler):
    """`POST /api/hint` -- `{"session_id": "<id>", "retry": bool}`.
    Identifier-addressed exactly like the other /api/* session routes; returns
    the same typed payload as the CLI `hint` command -- the model
    orchestration in `session.do_hint` (plan 08-04): `{"status", "generated",
    "authored", "interaction_id", "evidence"}` with `status` one of the typed
    pass/drop/unavailable outcomes, never a Phase 6 tier reveal. The legacy
    `stumped` shim was removed here in plan 08-05; the explicit tier-reveal
    path stays in the runtime teaching transition.
    """
    if _reject_cross_origin(handler):
        return
    data, failed = api_read_json(handler)
    if failed:
        return
    session_id = data.get("session_id")
    path = api_session_path(handler, session_id)
    if path is None:
        handler.send_not_found(session_id if isinstance(session_id, str) else "")
        return
    retry = data.get("retry", False)
    if not isinstance(retry, bool):
        handler.send_error(400, "retry must be a boolean")
        return
    try:
        result = session.do_hint(path, retry=retry)
    except SystemExit as exc:
        handler.send_error(400, str(exc.code))
        return
    except Exception as exc:
        handler.send_server_error(exc)
        return
    handler.send_json(result)


def handle_api_rubric_review(handler):
    """`POST /api/rubric-review` -- `{"session_id": "<id>"}`.
    Identifier-addressed like every other /api/* session route; returns the
    pending per-point rubric suggestions from `session.do_rubric_review`
    (plan 08-04 Task 2) -- never a score and never an accept path (D-14,
    D-25). The browser may render these; only the trusted local reviewer CLI
    (`itembank mark --proposal`) may settle them.
    """
    if _reject_cross_origin(handler):
        return
    data, failed = api_read_json(handler)
    if failed:
        return
    session_id = data.get("session_id")
    path = api_session_path(handler, session_id)
    if path is None:
        handler.send_not_found(session_id if isinstance(session_id, str) else "")
        return
    try:
        result = session.do_rubric_review(path)
    except SystemExit as exc:
        handler.send_error(400, str(exc.code))
        return
    except Exception as exc:
        handler.send_server_error(exc)
        return
    handler.send_json(result)


def handle_api_interact(handler):
    """`POST /api/interact` -- the browser twin of `itembank interact`
    (plan 06.1-02 Task 3, D-04/D-05). The body accepts exactly
    `session_id`, `interaction_version`, `action_id`, `action_type`, and
    canonical semantic `state`; the session and current item are resolved
    server-side, and client fields claiming an item, path, score, key,
    tolerance, tier, observation, or evidence are rejected by name. Returns
    the same JSON shape as the CLI command: the versioned runtime
    observation plus the append result (recorded / already_recorded /
    conflict / refused).
    """
    if _reject_cross_origin(handler):
        return
    data, failed = api_read_json(handler)
    if failed:
        return
    session_id = data.get("session_id")
    path = api_session_path(handler, session_id)
    if path is None:
        handler.send_not_found(session_id if isinstance(session_id, str) else "")
        return
    # The five-field request; every authority-shaped field is refused by
    # name (T-06.1-06). The session item is never client-chosen.
    action = {"interaction_version": data.get("interaction_version"),
              "action_id": data.get("action_id"),
              "action_type": data.get("action_type"),
              "state": data.get("state")}
    bad = [k for k in data
           if k not in ("session_id", "interaction_version", "action_id",
                        "action_type", "state")]
    if bad:
        handler.send_error(
            400, "field(s) %s are not accepted by /api/interact; the session "
            "is addressed by session_id and the item is resolved server-side"
            % ", ".join(sorted(bad)))
        return
    try:
        result = session.do_interact(path, action)
    except SystemExit as exc:
        handler.send_error(400, str(exc.code))
        return
    except Exception as exc:
        handler.send_server_error(exc)
        return
    handler.send_json(result)


def handle_api_report(handler):
    """`POST /api/report` -- `{"session_id": "<id>"}`."""
    if _reject_cross_origin(handler):
        return
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


def handle_api_export_audio(handler):
    """`POST /api/export_audio` -- the daemon half of D-08: `{"bank",
    "objective", "out_dir", "engine"?, "split"?, "container"?}`. The bank is
    resolved through the same scanned-stem allowlist the other /api/* routes
    use (never a raw path, T-2-01), and the request calls the SAME runtime
    call the CLI reaches (`audio_surface.export_audio`) -- one implementation,
    two surfaces (D-08). The response carries the written pack file names and
    the transcript path.

    `out_dir` is an output DIRECTORY for the pack, joined under the daemon's
    served root (never an absolute path from the client, never `..`); the
    default is `<root>/_attempts/audio`. A refusal (unknown bank, unknown
    objective, unknown or unavailable engine, invalid body) returns the
    named-error shape other /api handlers use and writes no files (D-04).
    """
    if _reject_cross_origin(handler):
        return
    data, failed = api_read_json(handler)
    if failed:
        return
    bank = data.get("bank")
    bank_path = handler.banks.get(bank) if isinstance(bank, str) else None
    if bank_path is None:
        handler.send_not_found(bank if isinstance(bank, str) else "")
        return
    objective = data.get("objective")
    if not isinstance(objective, str) or not objective:
        handler.send_error(400, "export_audio requires a non-empty objective")
        return
    out_dir = data.get("out_dir")
    if not isinstance(out_dir, str) or not out_dir:
        out_dir = os.path.join("_attempts", "audio")
    root = os.path.abspath(handler.root)
    joined = os.path.normpath(os.path.join(root, out_dir))
    if not (joined == root or joined.startswith(root + os.sep)):
        handler.send_error(400, "export_audio out_dir must stay under the "
                                "served root")
        return
    engine = data.get("engine")
    if engine is not None and not isinstance(engine, str):
        handler.send_error(400, "export_audio engine must be a string")
        return
    split = data.get("split")
    if split not in (None, "per-pack", "per-item"):
        handler.send_error(400, "export_audio split must be per-pack or "
                                "per-item")
        return
    container = data.get("container")
    if container not in (None, "mp3", "wav"):
        handler.send_error(400, "export_audio container must be mp3 or wav")
        return
    try:
        cfg = settings.load_settings(handler.root)
    except SystemExit as exc:
        handler.send_error(400, str(exc.code))
        return
    try:
        result = audio_surface.export_audio(
            bank_path, objective, joined, engine=engine, split=split,
            container=container, settings=cfg)
    except audio_surface.EngineError as exc:
        handler.send_error(400, "export_audio: %s" % exc)
        return
    except SystemExit as exc:
        handler.send_error(400, str(exc.code))
        return
    except Exception as exc:
        handler.send_server_error(exc)
        return
    handler.send_json({"engine": result["engine"],
                       "base": result["base"],
                       "transcript": result["transcript"],
                       "audio": result["audio"]})


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
    day_force_tokens = {}
    # Set to a fresh `secrets.token_hex(16)` by cmd_sidecar; left None, the
    # CLI daemon path stays completely ungated (D-04). The token lives only in
    # this process and the shell that read it off the handshake -- never
    # persisted, never a CLI argument (T-13-01, T-13-04).
    sidecar_token = None

    def send_error(self, code, message=None, explain=None):
        """Encoding-safe 4xx/5xx (10-04 containment). The built-in
        `send_error` encodes the HTTP reason phrase as latin-1, which
        raises `UnicodeEncodeError` on any non-latin-1 character -- 10-04's
        locked cap copy carries U+2019 ("Today's"), so the at-cap 400 would
        kill the request thread and close the connection with no response.
        The exact message (whatever its encoding) is sent in a UTF-8 body;
        only the HTTP reason phrase stays the standard ASCII phrase. Never
        a path or a traceback (T-2-05).
        """
        import http.client
        phrase = http.client.responses.get(code, "Error")
        text = message if isinstance(message, str) else (explain or phrase)
        body = ("<!doctype html><html lang=en><head><meta charset=utf-8>"
                "<title>%d %s</title></head><body><h1>%s</h1><p>%s</p>"
                "</body></html>"
                % (code, html.escape(phrase), html.escape(phrase),
                   html.escape(text)))
        self.send_bytes(body.encode("utf-8"), "text/html; charset=utf-8",
                        status=code)

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

    def _sidecar_token_ok(self, path):
        """The D-04 loopback token gate. With no per-launch token configured
        (the CLI daemon path) every request passes unchanged. With a token
        configured (sidecar mode), every route except the probe marker
        requires it in `SIDECAR_TOKEN_HEADER`: the shell injects the header
        on every request the packaged window makes, and the marker stays
        token-free so the detect-and-attach probe works.
        """
        token = self.sidecar_token
        if token is None:
            return True
        if path == MARKER_PATH:
            return True
        # Constant-time comparison (T-13-01): the token is the only secret on
        # this loopback surface; an equality short-circuit would leak its
        # prefix length to a local timing probe.
        return secrets.compare_digest(
            self.headers.get(SIDECAR_TOKEN_HEADER, ""), token)

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
            if not self._sidecar_token_ok(path):
                self.send_error(401)
                return
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
                 no_open=False, extra=None, on_bound=None, srv=None, window="app",
                 quiet=False):
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
    DaemonHandler.day_force_tokens = {}            # one-use edit-conflict gates

    bound = srv if srv is not None else _bind(port, host)
    with bound:
        bound_port = bound.server_address[1]
        display_host = "127.0.0.1" if host in (ALL_INTERFACES, "127.0.0.1") else host
        url = "http://%s:%d%s" % (display_host, bound_port, open_path)
        if not quiet:
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


def _port_silent(port, host="127.0.0.1", timeout=0.4):
    """True when something accepts TCP connections on `(host, port)` but
    never sends a single byte in response to a marker GET -- a listener that
    is bound but not serving, or a foreign process holding the port without
    answering. This is the D-06 "running instance is not reachable" case:
    the sidecar refuses by name rather than falling back to a free port,
    because the occupant may be a second itembank still starting up and a
    competing sidecar must never exist (T-13-03). A responder -- even one
    that is not an itembank -- returns False, leaving the three-case
    startup's free-port fallback to handle the squatter exactly as the CLI
    daemon does.
    """
    try:
        with socket.create_connection((host, port), timeout=timeout) as conn:
            conn.sendall(b"GET %s HTTP/1.0\r\nHost: %s\r\n\r\n"
                         % (MARKER_PATH.encode("ascii"), host.encode("ascii")))
            conn.settimeout(timeout)
            try:
                conn.recv(1)
            except socket.timeout:
                return True
            return False
    except OSError:
        return False


def _build_sessions(banks):
    """One session per bank, opened for the life of this process -- the same
    session-id-printed-so-a-marker-can-find-it precedent `cmd_serve` sets,
    extended to every bank the daemon found rather than the one bank a single
    `serve` process used to hold. Shared by `cmd_daemon` and `cmd_sidecar`.
    """
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
    return sessions


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

    # The silent background release check (DEL-07): started on its own
    # daemon thread before the socket even binds, so a slow or unreachable
    # GitHub can never delay or block serving the index page. Wrapped a
    # second time here even though background_check already swallows its
    # own exceptions -- a failing update check must never reach this
    # startup path as a traceback, the same degrade-never-block contract
    # surfaces/day.py already keeps when Anki is closed.
    def _background_check_thread():
        try:
            update.background_check(update.update_root(), cfg)
        except Exception:
            pass

    threading.Thread(target=_background_check_thread, daemon=True).start()

    print("itembank daemon")
    print("  dir     %s" % os.path.abspath(root))
    print("  banks   %d" % len(banks))
    print("  plans   %d" % len(plans))
    for stem, winner, loser in collisions:
        print("  collision  stem %r: %s wins, %s loses" % (stem, winner, loser))

    # One session per bank, opened for the life of this process (see
    # `_build_sessions` for the shape).
    sessions = _build_sessions(banks)

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


def cmd_sidecar(a):
    """The packaged-app launch path (D-02/D-03/D-04/D-06): the same daemon
    entry the CLI uses, with the sidecar contract bolted on. It binds
    127.0.0.1 only, prints the fixed stdout handshake -- bound port,
    per-launch token, version -- after binding, and gates the shell-used API
    routes with that token. Single-instance (D-06): a second launch against a
    reachable running instance attaches through start_server()'s existing
    occupied-by-itembank branch (already-running line, exit 0); a requested
    port held by a listener that does not answer the itembank marker is
    refused by name with the 13-UI-SPEC 3.3(e) port-held copy. A responding
    non-itembank squatter and an OS-reserved port still fall back to a free
    port exactly as the CLI daemon does.
    """
    import itembank                                    # lazy, like surfaces.cli.main()
    root = a.dir
    banks, plans, collisions = scan_dir(root)
    cfg = settings.load_settings(root)
    port = a.port if a.port is not None else cfg["daemon"]["port"]
    host = "127.0.0.1"                                 # D-04: loopback only
    window = cfg["daemon"]["window"]

    # The per-launch token (D-04): generated here, held only by this process
    # and handed to the shell on the stdout handshake. None means ungated, so
    # a later CLI daemon in the same process stays byte-compatible.
    token = secrets.token_hex(16)
    DaemonHandler.sidecar_token = token

    # D-06: refuse by name when the requested port is held by a listener that
    # never answers the itembank marker -- a starting or hung runtime. The
    # reachable attach case and the squatter/reserved free-port fallback are
    # start_server()'s own three-case path below, reused unchanged (D-02).
    if port != 0 and _port_silent(port, host):
        print(SIDECAR_PORT_HELD_COPY)
        sys.stdout.flush()
        return 1

    sessions = _build_sessions(banks)

    # The existing detect-and-attach probe (D-02): a second sidecar launch on
    # a port a first instance holds attaches and exits 0 instead of binding;
    # no_open=True keeps the shell in charge of windows.
    srv, bound_port, fell_back = start_server(DaemonHandler, port, host,
                                              no_open=True, window=window)

    def on_bound(actual_port):
        # The fixed stdout handshake (D-03/D-04), the one new protocol
        # surface -- a handshake, not an IPC channel. The shell parses these
        # lines with the same SIDECAR_HANDSHAKE constants this module defines.
        print("%s:%d" % (SIDECAR_HANDSHAKE["port"], actual_port))
        print("%s:%s" % (SIDECAR_HANDSHAKE["token"], DaemonHandler.sidecar_token))
        print("%s:%s" % (SIDECAR_HANDSHAKE["version"], itembank.__version__))
        sys.stdout.flush()

    serve_scoped(root, banks, plans, port, host=host, open_path="/", no_open=True,
                 extra={"sessions": sessions, "collisions": collisions},
                 on_bound=on_bound, srv=srv, window=window, quiet=True)
    return 0


def cmd_cli_twin(a):
    """The CLI twin of the shell's own route-to-command query (13-UI-SPEC
    2.2): `itembank cli-twin /quiz/sample_bank` prints the command that
    reaches the same runtime call. Exists so the route's ROUTE_CLI entry is a
    real command, keeping the every-route-has-a-CLI-equivalent inventory
    honest.
    """
    command = cli_twin_for(a.path)
    if command is None:
        print("no CLI twin for %s" % a.path)
        return 1
    print(command)
    return 0


def cmd_disclosure(a):
    """The CLI twin of the /disclosure route: prints the one-disclosure
    render-hook state (13-UI-SPEC 7.2) so the route/CLI inventory stays
    honest -- every route has a real CLI command.
    """
    print(json.dumps(update.disclosure_state(a.dir), ensure_ascii=False,
                     indent=2))
    return 0
