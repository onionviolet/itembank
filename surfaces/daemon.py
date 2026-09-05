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
import datetime, email.message, errno, hashlib, html, json, os, re, secrets, socket, socketserver, sys, threading, time
import urllib.parse, urllib.request, uuid

import evidence
import resources
import sample_course
import retention
import runner
import selection
import source_adapters
import server
import subjects
from model import (lesson_slug, load, parse_activities, parse_bank,
                   parse_key_blocks, parse_lesson, parse_media, parse_terms)
from runtime import (checkpoint_feedback, explain_payload, glossable,
                     lesson_run_advance, lesson_run_record, read_lesson_run,
                     read_session, start_lesson_run, upgrade_session)
from surfaces import (day, evidence_cli, home, ia, launcher, lesson,
                      presentation, quiz, quiz_page, retention_view, seeding,
                      session, settings, study, update)
from surfaces import audio as audio_surface
from surfaces import theme
from surfaces.session import UNKNOWN_LANGUAGE_COPY


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
# The D-09 locked sentence for refusing check execution when the daemon is
# reachable from the network and check.allow_lan is false (plan 05-03 Task 3).
# Reproduced exactly from the 05-UI-SPEC Copywriting Contract's "LAN execution
# refusal" row; a decision, not a fault report.
LAN_REFUSAL_COPY = (
    "Code execution is turned off while itembank is serving on your network "
    "(--lan). Ask whoever runs itembank to turn on check.allow_lan in settings "
    "if this device should be trusted, or answer this item from the machine "
    "itembank is running on.")

# The two server-side check refusals the served page branches on. Both are
# returned as a normal JSON body -- never a thrown error -- carrying the
# locked sentence under `refused` and the cause under `refused_reason`, so
# the page can style them differently (plan 05-06): the network refusal is a
# boundary (pending treatment), the unknown-language refusal is a
# misconfiguration (error treatment).
REFUSAL_REASON_LAN = "lan"
REFUSAL_REASON_LANG = "language"


def _refusal_body(reason, copy):
    return {"refused": copy, "refused_reason": reason}


def _refusal_from_exit(exc_code, q):
    """Map a session.do_action SystemExit onto a server-side refusal body, or
    None when the exit is not a check refusal. The unknown-language refusal
    is raised as SystemExit(UNKNOWN_LANGUAGE_COPY % lang) by the shared
    gate; the served page must receive it as a normal response, not a
    thrown error, so it can render the locked language sentence (plan
    05-06 Task 2)."""
    msg = str(exc_code)
    if q is not None and q.get("type") == "check" and msg == (
            UNKNOWN_LANGUAGE_COPY % (q.get("lang") or "python")):
        return _refusal_body(REFUSAL_REASON_LANG, msg)
    return None


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

# The vendored reading faces (03.1-06), served the same way KaTeX is -- the
# reviewed precedent for exactly this problem. `/assets/fonts/<name>`
# resolves only through the closed FONT_ASSETS map below; the name regex
# admits the same narrow safe character set, the handler never joins the
# client's name to a filesystem path, and anything not in the map is a plain
# 404 (T-e2m-01). The map is populated from fonts/MANIFEST.json's own file
# rows, so the manifest, the map, and presentation.SHARED_CSS's @font-face
# urls cannot drift apart (tests/stylesheet_roundtrip.py cross-asserts all
# three).
# A course's own media, served from the directory the bank lives in
# (`/media/<stem>/<name>`). Unlike KaTeX and the reading faces, this map
# cannot be closed in advance: the files are the learner's, named by their
# own bank's `## MEDIA` registry. So the containment is done by resolution
# instead of by allowlist, exactly the way `journal.commit_operation` and
# `course_package.safe_target` already do it: the name admits a narrow
# character set, `..` is refused rather than clamped, the resolved real path
# must sit inside the bank's own directory after link resolution, and the
# extension must be one of a closed set of static media types. Anything else
# is a plain 404, never a partial answer.
#
# The route exists because the served lesson had no way to reach its own
# pictures: a bank-relative `media/x.svg` on a page at `/lesson/<stem>`
# resolves to `/lesson/media/x.svg`, so the one diagram in the 17B tracer's
# lesson was a broken image in the app while its alt text carried the
# meaning alone.
MEDIA_ASSET_RE = re.compile(
    r"^/media/(?P<stem>[^/]+)/(?P<name>[A-Za-z0-9_][A-Za-z0-9_./-]*)$")

MEDIA_ASSET_TYPES = {
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".avif": "image/avif",
}


def media_base(stem):
    """The URL prefix `lesson.lesson_page` should resolve a bank-relative
    media path against for this bank. One function, so the route pattern and
    the rendered `src` cannot drift apart."""
    return "/media/" + urllib.parse.quote(stem, safe="")


FONT_ASSET_PREFIX = "/assets/fonts/"
FONT_ASSET_RE = re.compile(r"^/assets/fonts/(?P<name>[A-Za-z0-9_./-]+)$")

FONT_ASSETS = {}
for _dir, _name in (
        ("source-serif", "SourceSerif4-Regular.ttf.woff2"),
        ("source-serif", "SourceSerif4-Semibold.ttf.woff2"),
        ("ia-writer-quattro", "iAWriterQuattroS-Regular.woff2"),
        ("ia-writer-quattro", "iAWriterQuattroS-Bold.woff2")):
    FONT_ASSETS["%s/%s" % (_dir, _name)] = (
        "fonts/%s/%s" % (_dir, _name), "font/woff2")
del _dir, _name

LESSON_CHECK_RE = re.compile(r"^/lesson/(?P<stem>[^/]+)/check$")
LESSON_SKIP_RE = re.compile(r"^/lesson/(?P<stem>[^/]+)/skip$")
GLOSS_GET_RE = re.compile(r"^/gloss/(?P<stem>[^/]+)/(?P<slug>[^/]+)$")
KEY_REVIEW_RE = re.compile(r"^/key/(?P<key_id>[^/]+)/review$")
DAY_GET_RE = re.compile(r"^/day/(?P<stem>[^/]+)$")
DAY_SAVE_RE = re.compile(r"^/day/(?P<stem>[^/]+)/save$")
DAY_OPEN_RE = re.compile(r"^/day/(?P<stem>[^/]+)/open$")
DAY_EDIT_RE = re.compile(r"^/day/(?P<stem>[^/]+)/edit$")
# The bounded character class is the path-traversal refusal, not a
# convenience: a code cannot contain a separator, a percent escape, or an
# unbounded run, so a traversal attempt is refused by the dispatcher
# before `handle_help_get` runs and before any lookup key is built.
HELP_GET_RE = re.compile(r"^/help/(?P<code>[a-z0-9_.]{1,64})$")
# The same bounded-character-class refusal as HELP_GET_RE: a course id and a
# lesson id cannot contain a path separator, a percent escape, or an unbounded
# run, so a traversal attempt is refused at dispatch before any handler runs.
# The area alternation is a closed vocabulary mirroring `ia.COURSE_AREAS` minus
# `overview`, which COURSE_GET_RE serves at the bare course path.
COURSE_GET_RE = re.compile(r"^/course/(?P<course_id>[A-Za-z0-9_.-]{1,64})$")
COURSE_AREA_RE = re.compile(r"^/course/(?P<course_id>[A-Za-z0-9_.-]{1,64})/(?P<area>learn|practice|test|map|sources|build|evidence)$")
COURSE_LESSON_RE = re.compile(r"^/course/(?P<course_id>[A-Za-z0-9_.-]{1,64})/learn/(?P<lesson_id>[A-Za-z0-9_.-]{1,64})$")

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

# Plan 16B-09's one mutating route accepts exactly one field. A raw filesystem
# path, an object id, and a full-document replacement are all refused by name:
# the only path `ia.apply_shelf_action` ever deletes is the daemon root joined
# with `sample_course.SAMPLE_COURSE_DIRNAME`, so a body carrying a path would
# be a field nothing reads and an invitation to try.
SHELF_ALLOWED_FIELDS = ("action",)

# The only body fields `POST /api/source/import` reads (plan 14C-01). An
# adapter name and an opaque object id, never a filesystem path: `path` and
# `out` are refused here for the same reason `API_FORBIDDEN_FIELDS` refuses
# them everywhere else, and this route accepts no path field at all.
# The only body field `POST /api/source/recheck` reads (plan 14C-04).
SOURCE_RECHECK_ALLOWED_FIELDS = ("source_object_id",)

SOURCE_IMPORT_ALLOWED_FIELDS = ("adapter", "source_object_id", "url",
                                "rights_grant", "snapshot_storage",
                                "preview", "confirm")

# The `/api/*` session routes: D-04's four plus Phase 6's `/api/hint`,
# plan 06.1-02's `/api/interact`, plan 08-05's `/api/rubric-review`, Phase
# 10's `/api/override` and `/api/lesson-complete`, Phase 09.1's
# `/api/export_audio`, and Phase 13.5's `/api/teach` -- the authored six-tier
# ladder's first route to any browser (plan 14-03, DEFECT D-D). `/api/teach`
# is deliberately separate from `/api/hint`: `hint` is Phase 8's model
# orchestration and plan 08-05 removed the legacy tier shim from it on
# purpose. Fixed literals, not stem-parameterised: a session or a bank is
# addressed by an opaque identifier in the JSON body (T-2-01), never by a
# path segment, so there is no `<stem>`/`<id>` group in any of these
# patterns at all. Phase 14C's `/api/source/import` is the thirteenth: it
# turns one linked book, document, page, or transcript into derived Markdown
# plus a locator sidecar, addressed by an opaque `source_object_id` resolved
# server-side against the daemon's own journal registry. Plan 14C-04 adds
# `/api/source/recheck` beside it: a READ that reports whether a captured
# remote origin still matches and changes nothing, which is why it is gated
# by the read-side cross-origin check rather than the write-side one. The
# fifteen-entry length is asserted by
# `check_api_route_scope` in `tests/daemon_roundtrip.py`, and every entry
# is mirrored in ROUTE_CLI and SURFACE_PARITY (Extensibility Rule 9(a)).
API_ROUTES = (
    ("POST", "/api/start", "handle_api_start"),
    ("POST", "/api/next", "handle_api_next"),
    ("POST", "/api/submit", "handle_api_submit"),
    ("POST", "/api/hint", "handle_api_hint"),
    ("POST", "/api/teach", "handle_api_teach"),
    ("POST", "/api/interact", "handle_api_interact"),
    ("POST", "/api/report", "handle_api_report"),
    ("POST", "/api/override", "handle_api_override"),
    ("POST", "/api/lesson-complete", "handle_api_lesson_complete"),
    ("POST", "/api/rubric-review", "handle_api_rubric_review"),
    ("POST", "/api/mark", "handle_api_mark"),
    ("POST", "/api/export_audio", "handle_api_export_audio"),
    ("POST", "/api/lesson/run", "handle_api_lesson_run"),
    ("POST", "/api/source/import", "handle_api_source_import"),
    ("POST", "/api/source/recheck", "handle_api_source_recheck"),
    ("POST", "/api/shelf", "handle_api_shelf"),
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
    ("GET", "/banks", "handle_banks"),
    ("GET", MARKER_PATH, "handle_marker"),
    ("GET", "/day", "handle_day_index"),
    ("GET", "/report", "handle_report_get"),
    ("GET", "/settings", "handle_settings_get"),
    ("GET", "/disclosure", "handle_disclosure"),
    ("GET", "/activity", "handle_activity_get"),
    ("POST", "/api/theme", "handle_theme_post"),
    ("POST", "/cli-twin", "handle_cli_twin"),
    ("POST", "/seed/accept", "handle_seed_accept"),
) + API_ROUTES + (
    ("GET", KATEX_ASSET_RE, "handle_katex_asset"),
    ("GET", FONT_ASSET_RE, "handle_font_asset"),
    ("GET", MEDIA_ASSET_RE, "handle_media_asset"),
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
    ("GET", HELP_GET_RE, "handle_help_get"),
    ("GET", COURSE_GET_RE, "handle_course_get"),
    ("GET", COURSE_AREA_RE, "handle_course_area_get"),
    ("GET", COURSE_LESSON_RE, "handle_course_lesson_get"),
)

# Every route in ROUTES has a CLI command that reaches the same runtime
# call -- SURF-04's "every route has a CLI equivalent" as a machine-checkable
# inventory instead of a claim in prose. The key set here is asserted equal
# to ROUTES' (method, pattern) pairs, so a route added without an entry here
# fails the build instead of shipping silently.
ROUTE_CLI = {
    ("GET", "/"): "daemon",
    ("GET", "/banks"): "daemon",
    ("GET", MARKER_PATH): "daemon",
    ("GET", "/report"): "report",
    ("GET", "/settings"): "theme",
    ("GET", "/disclosure"): "disclosure",
    ("GET", "/activity"): "activity",
    ("POST", "/api/theme"): "theme",
    ("POST", "/cli-twin"): "cli-twin",
    ("POST", "/seed/accept"): "seed",
    ("POST", "/api/start"): "start",
    ("POST", "/api/next"): "next",
    ("POST", "/api/submit"): "submit",
    ("POST", "/api/hint"): "hint",
    ("POST", "/api/teach"): "teach",
    ("POST", "/api/interact"): "interact",
    ("POST", "/api/report"): "report",
    ("POST", "/api/override"): "override",
    ("POST", "/api/lesson-complete"): "lesson",
    ("POST", "/api/rubric-review"): "rubric-review",
    ("POST", "/api/mark"): "mark",
    ("GET", KATEX_ASSET_RE): "daemon",
    ("GET", FONT_ASSET_RE): "daemon",
    ("GET", MEDIA_ASSET_RE): "daemon",
    ("POST", "/api/export_audio"): "export",
    ("POST", "/api/lesson/run"): "lesson",
    ("POST", "/api/source/import"): "source",
    # Both source routes map to the one `source` CLI parser, exactly as the
    # three day routes map to `day`.
    ("POST", "/api/source/recheck"): "source",
    ("POST", "/api/shelf"): "shelf",
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
    ("GET", HELP_GET_RE): "help-code",
    ("GET", COURSE_GET_RE): "daemon",
    ("GET", COURSE_AREA_RE): "daemon",
    ("GET", COURSE_LESSON_RE): "daemon",
}

# Extensibility Rule 9(a) (ROADMAP.md): every /api/* route reserves its
# future MCP tool name in the same commit it ships -- the third surface
# (MCP) arrives as a third column here, never as a second parity map, and an
# unmapped entry fails `check_surface_parity` instead of shipping silently.
# Each row is (route, CLI command, reserved MCP tool name); the tool names
# are the locked reserved vocabulary (start, next, submit, report, hint,
# teach, override, lesson_complete, rubric_review).
SURFACE_PARITY = (
    (("POST", "/api/start"), "start", "start"),
    (("POST", "/api/next"), "next", "next"),
    (("POST", "/api/submit"), "submit", "submit"),
    (("POST", "/api/hint"), "hint", "hint"),
    (("POST", "/api/teach"), "teach", "teach"),
    (("POST", "/api/interact"), "interact", "interact"),
    (("POST", "/api/report"), "report", "report"),
    (("POST", "/api/override"), "override", "override"),
    (("POST", "/api/lesson-complete"), "lesson", "lesson_complete"),
    (("POST", "/api/rubric-review"), "rubric-review", "rubric_review"),
    (("POST", "/api/export_audio"), "export", "export_audio"),
    (("POST", "/api/lesson/run"), "lesson", "lesson_run"),
    (("POST", "/api/source/import"), "source", "source_import"),
    (("POST", "/api/source/recheck"), "source", "source_recheck"),
    (("POST", "/api/shelf"), "shelf", "shelf"),
    (("POST", "/api/mark"), "mark", "mark"),
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


def handle_activity_get(handler):
    """`GET /activity` -- the Activity view: durable agent and maintenance
    jobs, read from the journal and rendered read-only.

    This is a read model. The handler writes nothing, offers no resolve
    control, and reaches no journal write path, because Phase 16B ships no
    Activity write authority at all (D-16B-8). Every string it renders comes
    from `ia.ACTIVITY_COPY`.

    The Activity area here means durable agent and maintenance jobs. It is a
    different object from `REQUIREMENTS.md`'s `ACTIVITY-01/02/03` family of
    purpose-first learner questions (D6).
    """
    state = ia.activity_view_state(handler.root)
    if not state["available"]:
        body = (presentation.state_panel(
                    {"kind": "unknown", "status": state["notice"]})
                + '<p><a href="/help/ia.activity_unavailable">'
                  'Read more about this</a></p>'
                + banner_markup(ia.degraded_banner("agent_unavailable")))
    else:
        parts = []
        if state["needs_input"]:
            parts.append("<h2>%s</h2>"
                         % presentation.esc(ia.ACTIVITY_COPY["needs_input"]))
        for job in state["jobs"]:
            parts.append(
                '<article class="job" data-ia-state="%s" data-ia-token="%s">'
                "<h3>%s</h3><p>%s</p></article>"
                % (presentation.esc(job["state"]),
                   presentation.esc(job["token"]),
                   presentation.esc(job["label"]),
                   presentation.esc(job["intent"])))
        body = "".join(parts)
    handler.send_html(presentation.surface_shell(
        "Activity", body,
        theme_css=theme.theme_css(settings.load_settings(handler.root)),
        back={"href": "/", "label": "Back to courses"}).encode("utf-8"))


def handle_help_get(handler, code):
    """`GET /help/<code>` -- the offline help page for one named error code.

    The whole lookup is local and in memory: no file is opened and no socket
    is used, so help resolves exactly when connectivity, a hosted model, or a
    configured agent is the thing that broke (APP-03). An unrecognized code is
    a 200 carrying the fallback sentence, never a 404 and never a broken link;
    a malformed one never reaches here, because `HELP_GET_RE`'s bounded
    character class refuses it at dispatch.
    """
    entry = ia.help_entry(code)
    body = '<p class="help-cause">%s</p>' % presentation.esc(entry["cause"])
    if entry["next_action"]:
        body += ('<p class="help-next">%s</p>'
                 % presentation.esc(entry["next_action"]))
    body += ('<p class="help-code">Error code: %s</p>'
             % presentation.esc(entry["code"]))
    handler.send_html(presentation.surface_shell(
        entry["title"], body,
        theme_css=theme.theme_css(settings.load_settings(handler.root)),
        back={"href": "/", "label": "Back to courses"}).encode("utf-8"))


# Progressive enhancement only, emitted by the three course-level handlers.
# It restores an anchor's focus and scroll position and remembers where the
# reader was; every route, every anchor target, and every back control works
# with it disabled, which is what the `noscript` sentence beside it states.
# It adds no library, no framework, no polyfill, and no network request, and
# it never changes page content beyond revealing the already-rendered
# `data-anchor-missing` region.
RESTORE_SCRIPT = """<script>
(function () {
  var KEY = "itembank.ia.restore";
  function contextOffset() {
    var bar = document.querySelector("[data-surface-context]");
    return bar ? bar.offsetHeight : 0;
  }
  function fullyInView(el) {
    var r = el.getBoundingClientRect();
    return r.top >= 0 && r.bottom <= (window.innerHeight ||
      document.documentElement.clientHeight);
  }
  function focusHeading() {
    var h1 = document.querySelector("h1");
    if (h1) { h1.tabIndex = -1; h1.focus({preventScroll: true}); }
  }
  function revealMissing() {
    var note = document.querySelector("[data-anchor-missing]");
    if (note) { note.removeAttribute("hidden"); }
  }
  function restoreStored() {
    var raw = null;
    try { raw = window.sessionStorage.getItem(KEY); } catch (e) { return; }
    if (!raw) { return; }
    var saved = null;
    try { saved = JSON.parse(raw); } catch (e) { return; }
    if (!saved || saved.path !== location.pathname) { return; }
    window.scrollTo(0, saved.scrollY || 0);
    var prior = saved.activeId && document.getElementById(saved.activeId);
    if (prior) { prior.tabIndex = -1; prior.focus({preventScroll: true}); }
    else { focusHeading(); }
  }
  function onLoad() {
    var hash = location.hash;
    if (!hash) { restoreStored(); return; }
    var target = document.getElementById(hash.slice(1));
    if (!target) { focusHeading(); revealMissing(); return; }
    if (!fullyInView(target)) {
      target.scrollIntoView({block: "start"});
      window.scrollBy(0, -contextOffset());
    }
    target.tabIndex = -1;
    target.focus({preventScroll: true});
  }
  window.addEventListener("pagehide", function () {
    var active = document.activeElement;
    try {
      window.sessionStorage.setItem(KEY, JSON.stringify({
        path: location.pathname, hash: location.hash,
        scrollY: window.scrollY,
        activeId: active && active.id ? active.id : ""
      }));
    } catch (e) { /* a browser refusing storage loses only the cue */ }
  });
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", onLoad);
  } else { onLoad(); }
})();
</script>"""

COURSE_NOSCRIPT = ("Links to a specific part of this page still work. Your "
                   "browser jumps to it without the extra focus handling.")


# --- course area content (`17B-03 D-06 item 3`) ------------------------------
# Phase 16B shipped the eight course areas with `content_available: False` and
# a stated notice, because the record shapes that fill them belonged to 14A
# and 14B. Both have landed, so the areas read the course's own accepted
# artifacts here: the banks and lessons inside the course directory, the
# sidecar's objectives and sources, and the evidence log's own counts. The
# resolution is read-only and composes no new authority: every row is a link
# to a route that already exists, and an area with nothing to show still says
# so in its own words rather than rendering an empty region.


def _bank_title(path, stem):
    """The bank's own `# ` heading, or its stem. The same rule
    `surfaces/quiz.py` already uses for the page title, so the shelf, the
    quiz and the course areas name a bank identically."""
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("# "):
                    return line[2:].strip() or stem
                if line.startswith("Q1."):
                    break
    except OSError:
        pass
    return stem


def _course_banks(handler, course_dir):
    """The (stem, path) pairs of banks the startup scan admitted that live
    inside this course's directory, path-sorted."""
    root = os.path.realpath(course_dir)
    found = []
    for stem, path in (handler.banks or {}).items():
        real = os.path.realpath(path)
        try:
            inside = os.path.commonpath([root, real]) == root
        except ValueError:
            inside = False
        if inside:
            found.append((stem, path))
    return sorted(found, key=lambda pair: pair[1])


def _course_evidence_counts(course_dir):
    """Responses, marks and sittings recorded in this course's own log."""
    log = evidence.log_path(course_dir)
    counts = {"responses": 0, "marks": 0, "sessions": 0, "events": 0}
    if not os.path.exists(log):
        return counts
    sessions = set()
    try:
        for event in evidence.events(log):
            counts["events"] += 1
            kind = event.get("event_type")
            if kind == "response":
                counts["responses"] += 1
            elif kind == "mark":
                counts["marks"] += 1
            if event.get("session_id"):
                sessions.add(event["session_id"])
    except Exception:
        return counts
    counts["sessions"] = len(sessions)
    return counts


def _course_area_rows(handler, state, course_dir):
    """`(lead, rows)` for one course area, read from the course's own
    artifacts. `rows` empty means the area states itself as before."""
    if course_dir is None:
        return "", []
    area = state.get("area")
    banks = _course_banks(handler, course_dir)
    lessons, quizzes = [], []
    for stem, path in banks:
        try:
            qs = load(path)
        except Exception:
            continue
        try:
            les = parse_lesson(path)
        except Exception:
            les = None
        title = _bank_title(path, stem)
        headings = len((les or {}).get("headings") or [])
        if headings:
            lessons.append({
                "href": "/lesson/%s" % urllib.parse.quote(stem, safe=""),
                "title": title,
                "meta": "%d section%s" % (headings, "" if headings == 1 else "s"),
                "note": "Read the lesson, then sit its items."})
        quizzes.append({
            "href": "/quiz/%s" % urllib.parse.quote(stem, safe=""),
            "title": title,
            "meta": "%d item%s" % (len(qs), "" if len(qs) == 1 else "s"),
            "note": "Practice keeps you on an item until it is right."})

    record = None
    try:
        import course as course_module
        record = course_module.read_course(course_dir)
    except Exception:
        record = None
    doc = (record or {}).get("doc") or {}

    if area == "learn":
        return ("Every lesson this course holds, as a durable document you can "
                "also read outside the app."), lessons
    if area == "practice":
        return ("A practice sitting scores as you go, unlocks one hint tier "
                "per genuine wrong attempt, and never shows a key you have "
                "not earned."), quizzes
    if area == "map":
        rows = []
        containers = {c.get("id"): c.get("title") or c.get("label") or ""
                      for c in (doc.get("structure") or [])}
        for rec in (doc.get("objectives") or []):
            rows.append({
                "href": "", "title": rec.get("statement") or rec.get("id") or "",
                "meta": containers.get(rec.get("container"), ""),
                "note": ""})
        return ("The objectives this course is accountable for, in the order "
                "its scope records them."), rows
    if area == "sources":
        rows = []
        for rec in (doc.get("sources") or []):
            rows.append({
                "href": "", "title": rec.get("title") or rec.get("source_object_id") or "",
                "meta": "bound source", "note": rec.get("note") or ""})
        return ("What this course is built from. A source is bound where it "
                "lives; nothing here is a copy."), rows
    if area == "evidence":
        counts = _course_evidence_counts(course_dir)
        if not counts["events"]:
            return "", []
        rows = [
            {"href": "", "title": "%d response%s recorded"
             % (counts["responses"], "" if counts["responses"] == 1 else "s"),
             "meta": "", "note": ""},
            {"href": "", "title": "%d mark%s settled"
             % (counts["marks"], "" if counts["marks"] == 1 else "s"),
             "meta": "", "note": ""},
            {"href": "", "title": "%d sitting%s"
             % (counts["sessions"], "" if counts["sessions"] == 1 else "s"),
             "meta": "", "note": ""},
        ]
        return ("Your own record, in this course's own store. Nothing here "
                "left this machine."), rows
    if area == "overview":
        rows = []
        if lessons:
            rows.append({"href": lessons[0]["href"], "title": "Start reading",
                         "meta": lessons[0]["title"], "note": ""})
        if quizzes:
            rows.append({"href": quizzes[0]["href"], "title": "Sit the items",
                         "meta": quizzes[0]["meta"], "note": ""})
        objectives = len(doc.get("objectives") or [])
        sources = len(doc.get("sources") or [])
        counts = _course_evidence_counts(course_dir)
        lead = ("%d objective%s, %d bound source%s, %d bank%s, %d recorded "
                "response%s." % (objectives, "" if objectives == 1 else "s",
                                 sources, "" if sources == 1 else "s",
                                 len(quizzes), "" if len(quizzes) == 1 else "s",
                                 counts["responses"],
                                 "" if counts["responses"] == 1 else "s"))
        return lead, rows
    return "", []


def _course_rows_html(rows):
    out = []
    for row in rows:
        title = presentation.esc(row.get("title") or "")
        meta = presentation.esc(row.get("meta") or "")
        note = presentation.esc(row.get("note") or "")
        head = ('<a href="%s">%s</a>' % (presentation.esc(row["href"]), title)
                if row.get("href") else '<b>%s</b>' % title)
        out.append('<li class="row"><div class="row-head">%s%s</div>%s</li>'
                   % (head,
                      '<span class="row-meta mono">%s</span>' % meta if meta else "",
                      '<p class="row-note">%s</p>' % note if note else ""))
    return '<ul class="course-rows">%s</ul>' % "".join(out)


def _course_frame(handler, state, back, course_dir=None):
    """One course-level page: the eight-area nav, the area's own stated state,
    a real anchor target on the heading, and the hidden anchor-missing region
    the restoration script reveals. No pagination control, no page-number link,
    and no item cap, so reading scrolls."""
    nav = []
    for entry in state["nav"]:
        nav.append('<li><a href="%s"%s>%s</a></li>'
                   % (presentation.esc(entry["href"]),
                      ' aria-current="page"' if entry["current"] else "",
                      presentation.esc(entry["label"])))
    heading_id = ia.anchor_slug(state["area_label"]) or "area"
    lead, rows = _course_area_rows(handler, state, course_dir)
    if rows:
        content = ('<p class="area-lead">%s</p>%s'
                   % (presentation.esc(lead), _course_rows_html(rows))
                   if lead else _course_rows_html(rows))
    else:
        content = '<p class="area-state">%s</p>' % presentation.esc(
            state["notice"])
    body = ('<nav class="course-areas" aria-label="Course areas"><ul>%s</ul>'
            "</nav>"
            '<div class="state" data-anchor-missing hidden role="status">'
            "<p>%s</p></div>"
            '<h2 id="%s">%s</h2>%s'
            % ("".join(nav),
               presentation.esc(ia.ANCHOR_NOT_FOUND_NOTICE),
               presentation.esc(heading_id),
               presentation.esc(state["area_label"]),
               content))
    return presentation.surface_shell(
        state["course_name"], body,
        theme_css=theme.theme_css(settings.load_settings(handler.root)),
        back=back, noscript=COURSE_NOSCRIPT, tail=RESTORE_SCRIPT)


def _course_not_found(handler):
    """A 404 that carries no filesystem path and links the one page that
    explains the state."""
    body = ('<p>%s</p><p><a href="/help/ia.route_not_found">'
            "Read more about this</a></p>"
            % presentation.esc(ia.AREA_NOT_FOUND_NOTICE))
    handler.send_html(presentation.surface_shell(
        "That link does not resolve", body,
        theme_css=theme.theme_css(settings.load_settings(handler.root)),
        back={"href": "/", "label": "Back to courses"}).encode("utf-8"), 404)


def handle_course_get(handler, course_id):
    """`GET /course/<course_id>` -- the course Overview frame."""
    state = ia.course_area_state(handler.root, course_id, "overview")
    if not state["found"]:
        _course_not_found(handler)
        return
    handler.send_html(_course_frame(
        handler, state, {"href": "/", "label": "Back to courses"},
        course_dir=ia.course_dir_for(handler.root, course_id)).encode("utf-8"))


def handle_course_area_get(handler, course_id, area):
    """`GET /course/<course_id>/<area>` -- one named course area.

    Layout width is a rendering decision inside this handler and never a
    second URL for the same object, so both widths are served by this one
    route and the nav lists all eight areas at either width.
    """
    state = ia.course_area_state(handler.root, course_id, area)
    if not state["found"]:
        _course_not_found(handler)
        return
    handler.send_html(_course_frame(
        handler, state,
        {"href": "/course/" + course_id,
         "label": "Back to " + state["course_name"]},
        course_dir=ia.course_dir_for(handler.root, course_id)).encode("utf-8"))


def handle_course_lesson_get(handler, course_id, lesson_id):
    """`GET /course/<course_id>/learn/<lesson_id>` -- one lesson inside Learn."""
    state = ia.course_area_state(handler.root, course_id, "learn")
    if not state["found"]:
        _course_not_found(handler)
        return
    handler.send_html(_course_frame(
        handler, state,
        {"href": "/course/" + course_id,
         "label": "Back to " + state["course_name"]}).encode("utf-8"))


def handle_api_shelf(handler):
    """`POST /api/shelf` -- the one mutating route Phase 16B adds.

    Four small first-run and shelf actions behind one route, so the parity
    tables gain one row for one capability rather than four rows. The body may
    carry exactly one field, `action`, and its value must be a member of
    `ia.SHELF_ACTIONS`; anything else is refused with 400 before any helper
    runs. Loopback-only and same-origin, like every other mutating route.
    """
    if _reject_cross_origin_write(handler):
        return
    data, failed = api_read_json(handler)
    if failed:
        return
    extra = sorted(k for k in data if k not in SHELF_ALLOWED_FIELDS)
    if extra:
        handler.send_error(400, "body may carry only: %s"
                                % ", ".join(SHELF_ALLOWED_FIELDS))
        return
    action = data.get("action")
    if action not in ia.SHELF_ACTIONS:
        handler.send_error(400, "action must be one of %s"
                                % "|".join(ia.SHELF_ACTIONS))
        return
    handler.send_bytes(
        json.dumps(ia.apply_shelf_action(handler.root, action)).encode("utf-8"),
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


def handle_api_source_import(handler):
    """`POST /api/source/import` -- the daemon half of the one source-import
    boundary (plan 14C-01). The browser and agent surface is a client of the
    same `source_adapters.import_source` function `itembank source import`
    calls: one implementation, two surfaces, never two decisions.

    The body carries an `adapter` name and an opaque `source_object_id`,
    never a filesystem path (T-2-01). The raw file is resolved server-side
    from the daemon's own journal registry, so a client can never assert a
    path, a fingerprint, or a rights record it does not own; the transform
    right that governs the write is read from that registry inside the
    journal's own lock and a body field cannot widen it.

    Markdown extracted from a learner-supplied or fetched file is data
    returned to the caller. It is never instructions this daemon, or any
    downstream agent reading the response, acts on.

    `preview: true` runs the same extraction and returns the would-be
    sidecar without writing anything, which is the free read half of the
    bind-policy pair: searching and reading a source stay free under either
    policy and only the write is gated.
    """
    if _reject_cross_origin_write(handler):
        return
    data, failed = api_read_json(handler)
    if failed:
        return
    extra = sorted(k for k in data if k not in SOURCE_IMPORT_ALLOWED_FIELDS)
    if extra:
        handler.send_error(
            400, "field %r is not accepted by /api/source/import; only "
            "adapter, source_object_id, url, rights_grant, snapshot_storage, "
            "preview, and confirm are read" % extra[0])
        return
    adapter = data.get("adapter")
    if not isinstance(adapter, str) or \
            adapter not in source_adapters.ADAPTER_REGISTRY:
        handler.send_error(
            400, "adapter must be one of %s"
            % ", ".join(sorted(source_adapters.ADAPTER_REGISTRY)))
        return
    source_object_id = data.get("source_object_id")
    if not isinstance(source_object_id, str) or not source_object_id:
        handler.send_error(
            400, "source_object_id must be the opaque id of a linked object")
        return
    base = getattr(handler, "root", None) or os.getcwd()
    if data.get("preview") is True:
        try:
            result = source_adapters.preview_source(
                base, adapter, source_object_id)
        except Exception as exc:          # never let a bad POST kill the daemon
            handler.send_server_error(exc)
            return
        handler.send_json(result)
        return
    try:
        # An HTTP client is not a human at a terminal, so the recorded actor
        # is the agent kind under this daemon's name. The journal entry says
        # who wrote, and nothing in the body can claim otherwise.
        # The daemon is an agent actor, so under the approve_before_bind
        # default this write needs `confirm: true` in the body. That is the
        # gate working, not a defect: a human at the CLI is their own
        # approval and an HTTP client is not.
        options = dict((settings.load_settings(base) or {}).get("source") or {})
        if isinstance(data.get("snapshot_storage"), str):
            options["snapshot_storage"] = data["snapshot_storage"]
        result = source_adapters.import_source(
            base, adapter, source_object_id, "agent", "daemon",
            rights_grant=data.get("rights_grant"), options=options,
            confirm=data.get("confirm") is True)
    except Exception as exc:              # never let a bad POST kill the daemon
        handler.send_server_error(exc)
        return
    handler.send_json(result)


def handle_api_source_recheck(handler):
    """`POST /api/source/recheck` -- report whether a captured remote origin
    still matches the snapshot that was bound (plan 14C-04, OQ-4).

    This is a READ, so it is gated by `_reject_cross_origin` rather than by
    `_reject_cross_origin_write`, matching how the other read routes are
    gated. That difference is a recorded choice and not an omission: the
    handler appends no journal entry, writes no file, and changes no
    fingerprint, so there is no mutation for the stricter gate to protect.

    The three states are advisory. `origin_changed` never invalidates a
    citation already issued against the captured revision, and
    `origin_unreachable` is a state rather than a failure, because a source
    that was captured stays readable with the network unplugged.

    Text fetched from a remote origin is data returned to the caller. It is
    never instructions this daemon, or any downstream agent reading the
    response, acts on.
    """
    if _reject_cross_origin(handler):
        return
    data, failed = api_read_json(handler)
    if failed:
        return
    extra = sorted(k for k in data if k not in SOURCE_RECHECK_ALLOWED_FIELDS)
    if extra:
        handler.send_error(
            400, "field %r is not accepted by /api/source/recheck; only "
            "source_object_id is read" % extra[0])
        return
    source_object_id = data.get("source_object_id")
    if not isinstance(source_object_id, str) or not source_object_id:
        handler.send_error(
            400, "source_object_id must be the opaque id of a captured "
            "source object")
        return
    base = getattr(handler, "root", None) or os.getcwd()
    try:
        options = dict((settings.load_settings(base) or {}).get("source") or {})
        result = source_adapters.recheck_origin(base, source_object_id,
                                                 options=options)
    except Exception as exc:              # never let a bad POST kill the daemon
        handler.send_server_error(exc)
        return
    if result.get("state") is None:
        handler.send_not_found(
            "no captured source %s is recorded in this root" % source_object_id)
        return
    handler.send_json(result)


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

# The reading link comes first because the reading comes first. Weibao sat the
# 13.9 skeleton on 2026-08-21 and reported the lesson as "gated behind the
# quiz", which read as inverted. The gate was doing the right thing; the index
# was the problem. /lesson/<stem> already existed, rendered the whole lesson,
# and linked into each item, and nothing anywhere linked to it. A route with no
# entrance is a route nobody has.
BANK_ROW = """<div class="row">
  <div class="name">__STEM__</div>
  <div class="links">__LESSON_LINK__
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


def banner_markup(banner):
    """One degraded-state banner rendered through the shared polite status
    region. Adds no styling and no new element, and returns the empty string
    for `None`.

    Only two 16B routes can actually produce a degraded state today, and only
    those two are wired. A crash banner, a disk-full banner, an offline banner,
    a permission-denied banner, and a future-schema banner each need a producer
    this phase does not build. They exist as data with their own tests, and
    plans 16B-09 and 16B-10 exercise the ones their fixtures can genuinely
    cause. Wiring a banner into a route that cannot produce its state would be
    a state nothing can reach, asserted as if it could.
    """
    if not banner:
        return ""
    return presentation.state_panel({"kind": banner["token"],
                                     "status": banner["text"],
                                     "actions": banner["actions"]})


SHELF_NOSCRIPT = ("The walkthrough and the sample-course controls submit as "
                  "ordinary forms. Every one of them also has a CLI twin: "
                  "itembank shelf <action> .")


def _walkthrough_offer(walkthrough):
    """The first-run offer as an in-page dismissible region, never a modal and
    never anything that hides the shelf: the card list renders in the same
    response, above or below it, and is reachable without answering.

    The replay control renders at every status, so skipping is never a lost
    opportunity.
    """
    parts = []
    if walkthrough["status"] == "unseen":
        parts.append(
            '<section class="walkthrough-offer" data-walkthrough-offer>'
            "<p>%s</p>"
            '<form method="post" action="/api/shelf" data-shelf-form>'
            '<button name="action" value="advance_walkthrough">%s</button>'
            '<button name="action" value="skip_walkthrough">%s</button>'
            "</form></section>"
            % (presentation.esc(walkthrough["offer_copy"]),
               presentation.esc(walkthrough["start_copy"]),
               presentation.esc(walkthrough["skip_copy"])))
    if walkthrough["status"] == "in_progress":
        step = walkthrough["current"]
        parts.append(
            '<section class="walkthrough-step" data-walkthrough-step>'
            "<h2>%s</h2><p>%s</p>"
            '<p><a href="%s">Open this</a></p></section>'
            % (presentation.esc(step["title"]),
               presentation.esc(step["body"]),
               presentation.esc(step["href"])))
    parts.append(
        '<form method="post" action="/api/shelf" data-shelf-form '
        'class="walkthrough-replay">'
        '<button name="action" value="replay_walkthrough">%s</button>'
        "</form>" % presentation.esc(walkthrough["replay_copy"]))
    return "".join(parts)


def _sample_course_controls(sample):
    """The sample course's note and its removal control, with the destructive
    confirmation stated on the control rather than only in a dialog."""
    return ('<p class="sample-note">%s</p>'
            '<form method="post" action="/api/shelf" data-shelf-form>'
            '<button name="action" value="remove_sample_course" '
            'data-confirm="%s">%s</button>'
            '<span class="confirm-copy">%s</span></form>'
            % (presentation.esc(sample["note"]),
               presentation.esc(sample["confirm_copy"]),
               presentation.esc(sample["remove_label"]),
               presentation.esc(sample["confirm_copy"])))


def _course_shelf_body(shelf, walkthrough=None, sample=None):
    """One article per course card. No pagination control, no page-number
    link, and no item cap, so a many-course shelf scrolls rather than
    paginating. The two `data-*` attributes and the two class names are stable
    hooks for tests and for Phase 17A, not styling; this plan adds no CSS rule
    and no inline style."""
    cards = []
    for card in shelf["cards"]:
        links = ['<a class="go" href="%s">%s</a>'
                 % (presentation.esc(card["cta_href"]),
                    presentation.esc(card["cta_label"]))]
        for action in card["actions"]:
            links.append('<a class="go secondary" href="%s">%s</a>'
                         % (presentation.esc(action["href"]),
                            presentation.esc(action["label"])))
        cards.append(
            '<article class="course-card" data-course-id="%s" '
            'data-attention="%s" data-ia-token="%s">'
            "<h2>%s</h2>"
            '<span class="chip">%s</span>'
            '<p class="resume-cue">%s</p>'
            '<p class="actions">%s</p>%s</article>'
            % (presentation.esc(card["course_id"]),
               presentation.esc(card["attention"]),
               presentation.esc(card["token"]),
               presentation.esc(card["name"]),
               presentation.esc(card["chip"]),
               presentation.esc(card["resume_cue"]),
               "".join(links),
               (_sample_course_controls(sample)
                if sample and card["course_id"] == sample["course_id"]
                else "")))
    degraded = [card for card in shelf["cards"] if card["degraded"]]
    banner = ""
    if degraded:
        # Precedence is the declared DEGRADED_STATES order (D-16B-9), not the
        # first card encountered, which is why this goes through
        # degraded_banner_for even though one state is fired today.
        banner = banner_markup(ia.degraded_banner_for(
            ["course_corrupted"], course_id=degraded[0]["course_id"]))
    offer = _walkthrough_offer(walkthrough) if walkthrough else ""
    return ('%s%s<div class="course-shelf">%s</div>'
            % (banner, offer, "".join(cards)))


def handle_index(handler):
    """`GET /` -- the configured home (plan 17A-08), now gated on course
    existence (Decision D1). The course shelf lives here rather than at a new
    `/home` or `/courses` route, so the app keeps one entry point and the
    literal `"/"` and its `ROUTE_CLI` value `daemon` do not change.

    The gate is two-way, and the second half is deliberately a fall-through
    rather than a branch. When at least one course exists, the shelf renders.
    When no course exists, for any reason (the course module absent, no course
    bound yet, a fresh install), the entire existing body below runs unchanged:
    the shipped bank and plan listing when banks or plans exist, and the
    shipped `EMPTY_STATE` copy when they do not. That is D1 verbatim, and it is
    why the shelf's own `empty_heading` and `empty_body` are carried in
    `ia.course_shelf_state`'s returned state for a caller that wants them
    rather than substituted for a shipped page here. One data function
    (`home.home_state`) still feeds every mode; the setting picks the shape and
    an unknown value falls back to the shelf saying so. The old stem list stays
    reachable at `/banks`, which is also where a stem collision is reported.
    """
    try:
        cfg = settings.load_settings(handler.root)
    except SystemExit as exc:
        handler.send_server_error(RuntimeError(str(exc.code)))
        return
    banks, plans = handler.banks, handler.plans
    theme_block = theme.theme_css(cfg)
    sample = ia.sample_course_state(handler.root)
    # Only a genuinely fresh root gets the sample course: no bank, no day
    # plan, and no course already bound. A root that already serves something
    # is not a first launch, and materializing into it would replace a working
    # home with a sample the learner never asked for.
    fresh = not banks and not plans and not ia.course_shelf_state(
        handler.root)["cards"]
    if fresh and not sample["present"] and not sample["removed"]:
        try:
            sample_course.write_sample_course(
                os.path.join(handler.root,
                             sample_course.SAMPLE_COURSE_DIRNAME))
        except OSError:
            # A read-only root or a full disk must not block first launch.
            # The shelf renders without the sample rather than erroring.
            pass
    shelf = ia.course_shelf_state(handler.root)
    if shelf["available"] and shelf["cards"]:
        handler.send_html(presentation.surface_shell(
            "Courses",
            _course_shelf_body(shelf, ia.walkthrough_state(handler.root),
                               sample),
            theme_css=theme_block,
            noscript=SHELF_NOSCRIPT).encode("utf-8"))
        return
    if not banks and not plans:
        served_dir = html.escape(os.path.abspath(handler.root))
        body = EMPTY_STATE.replace("__DIR__", served_dir)
    else:
        mode, note = home.resolve_mode(
            cfg.get("home") if isinstance(cfg, dict) else None)
        state = home.build_state(handler.root, banks, plans,
                                 handler.collisions)
        body = home.render_home(state, mode, note=note)
    page = presentation.surface_shell(
        "itembank", body,
        theme_css=theme_block + home.HOME_CSS)
    handler.send_html(page.encode("utf-8"))


def handle_banks(handler):
    """`GET /banks` -- the file list that used to be `GET /`: every bank
    and day-plan stem this daemon found at startup, plus the labelled
    warning naming any files it could not serve because another file
    shares their stem. The home links here instead of duplicating the
    list, because this is the only view that shows a collision."""
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
                # Offered only when this bank actually has a lesson, so the
                # index never advertises a reading that does not exist.
                # parse_lesson is falsy for a bank with no LESSON section and
                # no external lesson source, which is the whole test.
                try:
                    has_lesson = bool(parse_lesson(banks[stem]))
                except Exception:      # a bank we cannot read is not a lesson
                    has_lesson = False
                lesson_link = ('\n    <a class="go primary" '
                               'data-action-primary href="/lesson/%s">'
                               "Read the lesson</a>" % esc) if has_lesson else ""
                row = (BANK_ROW.replace("__STEM__", esc)
                       .replace("__LESSON_LINK__", lesson_link)
                       .replace("__REPORT_LINK__", link))
            else:
                row = PLAN_ROW.replace("__STEM__", esc)
            rows.append(row)
        body = "\n".join(rows)
        body += ('\n<p class="vf-status"><a href="/">Back to the '
                 "home</a></p>")
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


def _check_refusal_body(handler, q):
    """The server-side refusal body for a check submission, or None when
    execution may proceed -- the shared `execution_refusal` decision mapped
    to the locked refusal body (reason + copy) the served page branches on
    (plan 05-06). Only check items are gated here; every other submission
    passes through untouched."""
    if q is None or q.get("type") != "check":
        return None
    cfg = settings.load_settings(handler.root)
    refusal = execution_refusal(handler, q.get("lang") or "python",
                                cfg.get("check") or {})
    if refusal is None:
        return None
    reason = (REFUSAL_REASON_LAN if refusal == LAN_REFUSAL_COPY
              else REFUSAL_REASON_LANG)
    return _refusal_body(reason, refusal)


def execution_refusal(handler, language, check_settings):
    """The one pre-execution refusal decision shared by check submission and
    lesson Run (plan 09-05): returns the locked refusal copy to send, or
    None when the run may proceed. Order is fixed -- the LAN boundary first
    (a network view never executes under the default policy), then the
    language allowlist. Both copies are the exact strings the Phase 5
    surfaces already shipped, so the check-submit paths keep their
    byte-for-behavior copy."""
    if getattr(handler, "lan", False) and \
            not (check_settings or {}).get("allow_lan"):
        return LAN_REFUSAL_COPY
    if language not in ((check_settings or {}).get("languages") or {}):
        return UNKNOWN_LANGUAGE_COPY % language
    return None


def _session_id_for(handler, stem):
    """The API session id registered against a served bank stem, or None --
    the session the lesson Run adapter posts against (plan 09-05)."""
    sess = handler.sessions.get(stem) or {}
    return sess.get("api_session_id")


def _lan_refused(handler):
    """True when this daemon serves on the network with check.allow_lan off
    -- the render-time gate that turns every runnable fence into the LAN
    refusal state (09-UI-SPEC "LAN refusal")."""
    if not getattr(handler, "lan", False):
        return False
    cfg = settings.load_settings(handler.root)
    return not (cfg.get("check") or {}).get("allow_lan")


THEME_ACTIONS = ("preview", "pick", "save", "reset")
THEME_ALLOWED_FIELDS = ("action", "source", "confirm")


def _mode_layer_section():
    """All seven mode layers as read-only text inside one native disclosure.

    The two fixed layers are rendered as text and never as a toggle: a fixed
    layer rendered as a control would be an affordance that cannot take
    effect, which is worse than no control at all. The five configurable
    layers are listed too, as informational text naming who decides, so a
    reader sees seven layers rather than two. This section links to no control
    and contains no `input`, `select`, `button`, `textarea`, `contenteditable`,
    or form of any kind; the actual controls for the learner-preference and
    accommodation layers are the settings groups plan 16B-06 added and the
    shipped theme control above.
    """
    rows = []
    for row in ia.mode_layer_rows():
        classes = "fixed-layer" if row["fixed"] else "configurable-layer"
        rows.append('<div class="%s"><p class="layer-label">%s</p>'
                    '<p class="layer-controller">%s</p>'
                    '<p class="layer-example">%s</p></div>'
                    % (classes, presentation.esc(row["label"]),
                       presentation.esc(row["controller"]),
                       presentation.esc(row["example"])))
    body = ("<h2>%s</h2>%s"
            % (presentation.esc(ia.MODE_LAYER_FIXED_HEADING), "".join(rows)))
    return presentation.details_section(
        ia.MODE_LAYER_FIXED_HEADING, body,
        data={"mode-layers": "read-only"})


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
    handler.send_html(
        theme.theme_page(cfg, sections=_mode_layer_section()).encode("utf-8"))


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
    view = teaching = None
    try:
        session_file = _ensure_quiz_session(handler, stem, path, qs)
        view = session.do_next(session_file)
        teaching = session.do_teach(session_file)
    except SystemExit:
        # Some legacy synthetic banks deliberately mix subject namespaces
        # and require an explicit profile at /api/start. Preserve their
        # established client-started page instead of guessing authority or
        # turning a readable quiz route into a 400.
        pass
    except Exception as exc:
        handler.send_error(400, str(getattr(exc, "code", exc)))
        return
    receipt = urllib.parse.parse_qs(urllib.parse.urlsplit(handler.path).query).get("receipt", [""])[-1]
    flash = _consume_quiz_flash(handler, receipt, view) if receipt and view else None
    _send_quiz_page(handler, stem, path, qs, sess, view, teaching, lesson_slugs, flash)


def _send_quiz_page(handler, stem, path, qs, sess, view, teaching, lesson_slugs,
                    flash=None, prefill=None, status=200):
    """Render and send `GET /quiz/<stem>`'s page for the state it is in.

    Shared with the POST failure paths (plan item 2, 2026-08-24): a submit
    that does not go through comes back as this page with a fresh token and
    the learner's own answer echoed into the controls, instead of the bare
    error document that ate a written response during the 13.9 sitting.
    """
    tokens = (dict((kind, _mint_quiz_token(handler, view, kind))
                   for kind in ("submit", "hint", "stumped")) if view else None)
    theme_block = theme.theme_css(settings.load_settings(handler.root))
    _, page = quiz.page_for(path, qs, serve=True, reveal=False,
                            post_path="/quiz/%s/answer" % stem,
                            bank_stem=stem, mode=sess.get("mode", "practice"),
                            lesson_base="/lesson/%s" % stem,
                            lesson_slugs=lesson_slugs, theme_css=theme_block,
                            assist=True, home_href="/")
    if view is not None:
        baseline = quiz_page.baseline_for(view, teaching,
                                          "/quiz/%s/answer" % stem, tokens, flash,
                                          prefill)
        page = page.replace('<div id="host"></div>', '<div id="host">%s</div>' % baseline, 1)
    handler.send_html(page.encode("utf-8"), status)


QUIZ_AUTHORITY_FIELDS = frozenset(("tier", "tier_id", "tier_index", "requested_tier",
                                   "key", "correct", "score", "entitled"))
# Four hours, not five minutes. The token is minted when an item RENDERS and
# checked when the answer is submitted, so its lifetime is a budget on how long
# a learner may spend reading and thinking. Five minutes is shorter than one
# real item: the 13.9 sitting on 2026-08-24 hit `403 invalid or expired quiz
# form token` on an EMT item whose source block runs several pages, and the
# sitting recorded nothing at all.
#
# What the token defends is replay and cross-origin submission on a loopback
# server serving one learner, and that defence is not weakened by outliving a
# reading session: the token is still single-session, single-item, single-use,
# and `_reject_cross_origin` is the check that actually guards the origin. A
# budget on thinking time was never the point.
QUIZ_TOKEN_TTL = 4 * 60 * 60
QUIZ_TOKEN_CAP = 2048


# Module-level, not a `DaemonHandler` attribute, and deliberately not
# `quiz_state_lock`. Module-level because one process serves one daemon, and
# because `_ensure_quiz_session` is called directly with a stand-in handler by
# `tests/serve_roundtrip.py` and `tests/model_phase_roundtrip.py`, which should
# not have to know that a lock lives on the handler class. Separate from
# `quiz_state_lock` because that one guards short in-memory critical sections
# over the token and flash stores, while this one spans `session.do_start`,
# which does file I/O: sharing them would make every token mint wait on a
# sitting being created.
QUIZ_SESSION_LOCK = threading.Lock()


def _ensure_quiz_session(handler, stem, path, qs):
    """The one session `GET /quiz/<stem>` reads, created once per bank.

    Held under `QUIZ_SESSION_LOCK` because the check and the create are one
    decision, not two. Unlocked, six concurrent first hits on a fresh daemon
    each read `api_session_id` as None and each ran `do_start`: measured on
    2026-08-30 as six session files under `_attempts/` for one bank, with
    `cfg["api_session_id"]` left pointing at whichever thread finished last
    and the other five sittings orphaned with their evidence attached.

    The lock covers `do_start` rather than only the dictionary write. A lock
    released before the create would still let two threads both decide to
    create.
    """
    with QUIZ_SESSION_LOCK:
        cfg = handler.sessions[stem]
        api_id = cfg.get("api_session_id")
        found = api_session_path(handler, api_id) if api_id else None
        if found:
            return found
        # The seed was hardcoded to 0 until 2026-08-24, so a scoped `serve` had
        # no way to influence item order. That is not cosmetic: a sitting parks
        # on a constructed response until a marker rules on it, so a bank whose
        # short item lands first under seed 0 ends at item one. `itembank serve
        # --seed` is the way out, and 0 stays the default so every existing
        # caller and every recorded sitting order is unchanged.
        spec = {"objective": "", "count": len(qs),
                "seed": int(cfg.get("seed", 0) or 0),
                "selection_mode": cfg.get("selection_mode", "practice")}
        out = os.path.join(os.path.abspath(handler.root), "_attempts",
                           "session_%s.json" % uuid.uuid4().hex[:12])
        # A scoped `itembank serve` has already run its full bank plus lesson
        # lint gate before constructing the handler configuration (`progress`
        # is its existing marker). Do not make that validated surface fail a
        # second, narrower lint pass when the daemon creates its public
        # baseline.
        created = session.do_start(path, spec, cfg.get("mode", "practice"), out,
                                   bool(cfg.get("progress")),
                                   preset_session_id=cfg.get("session_id"))
        cfg["api_session_id"] = created["session_id"]
        return out


def _prune_quiz_store(store):
    now = time.monotonic()
    for key in [k for k, v in store.items() if v["expires"] <= now]:
        store.pop(key, None)
    while len(store) >= QUIZ_TOKEN_CAP:
        store.pop(next(iter(store)))


def _mint_quiz_token(handler, view, action):
    token = secrets.token_urlsafe(24)
    with handler.quiz_state_lock:
        _prune_quiz_store(handler.quiz_form_tokens)
        handler.quiz_form_tokens[token] = {
            "session_id": view.get("session_id"), "item_id": (view.get("item") or {}).get("id"),
            "cursor": view.get("position"), "action": action,
            "expires": time.monotonic() + QUIZ_TOKEN_TTL}
    return token


def _mint_quiz_flash(handler, before, after, result):
    receipt = secrets.token_urlsafe(24)
    target = ((result.get("next") or {}).get("item") or {}).get("id")
    if target is None:
        target = (after.get("item") or {}).get("id")
    with handler.quiz_state_lock:
        _prune_quiz_store(handler.quiz_flash_receipts)
        handler.quiz_flash_receipts[receipt] = {
            "session_id": before.get("session_id"), "source_item_id": (before.get("item") or {}).get("id"),
            "cursor": after.get("position"), "status": after.get("status"), "target": target,
            "result": result, "expires": time.monotonic() + QUIZ_TOKEN_TTL}
    return receipt


def _consume_quiz_flash(handler, receipt, view):
    with handler.quiz_state_lock:
        _prune_quiz_store(handler.quiz_flash_receipts)
        rec = handler.quiz_flash_receipts.pop(receipt, None)
    if not rec or rec["session_id"] != view.get("session_id") or \
            rec["cursor"] != view.get("position") or rec["status"] != view.get("status"):
        return None
    current = (view.get("item") or {}).get("id")
    if rec["status"] == "complete":
        return rec["result"] if rec["target"] is None and current is None else None
    if current not in (rec["source_item_id"], rec["target"]):
        return None
    return rec["result"]


def _content_type(handler):
    raw = handler.headers.get("Content-Type")
    if not raw:
        return None
    try:
        msg = email.message.Message(); msg["content-type"] = raw
        value = msg.get_content_type().lower()
    except Exception:
        return None
    return value if "/" in value and not any(c in raw for c in "\r\n") else None


def _form_answer(item, fields):
    one = lambda name: (fields.get(name) or [""])[-1]
    t = item.get("type")
    if t == "mc": return one("option")
    if t == "multi": return sorted(set(fields.get("option") or []))
    if t in ("table", "dnd"):
        return dict((str(i), one("row_%d" % i)) for i, _ in enumerate(item.get("rows") or []) if one("row_%d" % i))
    if t == "build": return [one("step_%d" % i) for i, _ in enumerate(item.get("steps") or []) if one("step_%d" % i)]
    return one("answer")


def _echo_quiz_failure(handler, stem, path, qs, session_file, fields, message,
                      status=403):
    """A quiz POST that did not go through, answered with the quiz page rather
    than a bare error document: same item, a fresh token, the learner's own
    submitted fields echoed back into the controls, and `message` shown in the
    feedback region.

    The 13.9 sitting on 2026-08-24 lost a written constructed response to a
    `403 invalid or expired quiz form token`. The expiry itself is fixed at
    its trigger, but a network blip, a server restart or a stray reload throws
    the same answer away, so the class is closed here. The status still says
    the submission failed; only the body becomes useful.

    Nothing echoed is authority: `prefill` reaches the rendered controls and
    nothing else, and the answer is not recorded until a submit succeeds.
    """
    sess = handler.sessions.get(stem) or {}
    lesson = parse_lesson(path)
    lesson_slugs = set(h["slug"] for h in lesson["headings"]) if lesson else set()
    try:
        view = session.do_next(session_file)
        teaching = session.do_teach(session_file)
    except Exception:
        handler.send_error(status, message)
        return
    _send_quiz_page(handler, stem, path, qs, sess, view, teaching, lesson_slugs,
                    flash={"refused": message}, prefill=fields, status=status)


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
    media = _content_type(handler)
    if media not in ("application/json", "application/x-www-form-urlencoded"):
        handler.send_error(415, "quiz answers require application/json or application/x-www-form-urlencoded")
        return
    path = handler.banks.get(stem)
    if path is None:
        handler.send_not_found(stem)
        return
    try:
        qs = load(path)
        by_id = dict((q["id"], q) for q in qs)
        if media == "application/json":
            data, failed = api_read_json(handler)
            if failed: return
        else:
            try:
                fields = handler.read_form()
            except (UnicodeDecodeError, ValueError, TypeError):
                handler.send_error(400, "malformed form body"); return
            if any(name in fields for name in QUIZ_AUTHORITY_FIELDS):
                handler.send_error(400, "authority-shaped form field refused"); return
            action = (fields.get("action") or [""])[-1]
            token = (fields.get("form_token") or [""])[-1]
            if action not in ("submit", "hint", "stumped"):
                handler.send_error(400, "unknown quiz form action"); return
            session_file = _ensure_quiz_session(handler, stem, path, qs)
            before = session.do_next(session_file)
            with handler.quiz_state_lock:
                _prune_quiz_store(handler.quiz_form_tokens)
                # Read, do not spend. The token used to be popped here, before
                # `do_action` ran, so any later failure burned it and a
                # back-then-resubmit hit a second 403. It is spent below, once
                # the action has actually produced a result.
                grant = handler.quiz_form_tokens.get(token)
            expected = {"session_id": before.get("session_id"), "item_id": (before.get("item") or {}).get("id"),
                        "cursor": before.get("position"), "action": action}
            if not grant or any(grant.get(k) != v for k, v in expected.items()):
                _echo_quiz_failure(
                    handler, stem, path, qs, session_file, fields,
                    "That submission did not go through: this page's form token "
                    "was expired, already used, or minted for a different item. "
                    "Your answer is still here, exactly as you wrote it. "
                    "Submit it again.")
                return
            q = by_id.get(expected["item_id"])
            refusal = _check_refusal_body(handler, q) if action == "submit" else None
            try:
                if refusal is not None:
                    result = refusal
                elif action == "submit":
                    result = session.do_action(session_file, {"kind": "submit", "answer": _form_answer(before["item"], fields)},
                                               confidence=None, renderer_meta=None, elapsed_ms=None)
                else:
                    result = session.do_teach(session_file, action)
            except SystemExit as exc:
                result = _refusal_from_exit(exc.code, q)
                if result is None:
                    _echo_quiz_failure(handler, stem, path, qs, session_file,
                                       fields, str(exc.code), status=400)
                    return
            # The action ran and produced a result, so the token is spent
            # now: a replay finds it gone, and every path that bailed out
            # above left it usable for the resubmit it asked for.
            with handler.quiz_state_lock:
                handler.quiz_form_tokens.pop(token, None)
            if action == "submit" and result.get("accepted"):
                # The browser form path wrote evidence but never the second,
                # human-readable copy: `_refresh_attempt_view` was reachable
                # only from the JSON route, so every `serve` sitting printed
                # an attempt path it never wrote (found 2026-08-24 after the
                # 13.9 sitting finished with an empty `_attempts/` markdown).
                cfg = handler.sessions[stem]
                _refresh_attempt_view(cfg, cfg.get("api_session_id"), qs, path)
            after = session.do_next(session_file)
            receipt = _mint_quiz_flash(handler, before, after, result)
            handler.send_redirect("/quiz/%s?receipt=%s" % (stem, urllib.parse.quote(receipt)))
            return
        q = by_id.get(data.get("id"))
        if q is None:
            handler.send_error(404, "no item %r in this bank" % data.get("id"))
            return
        refusal = _check_refusal_body(handler, q)
        if refusal is not None:
            handler.send_json(refusal)
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
            # Defence in depth: the transition never releases own-selection
            # feedback in a silent mode, and a silent mode never ships it.
            result.pop("selection_feedback", None)
        if result.get("action") in ("advance", "complete") and q is not None:
            # The rebuild applies the reveal policy, and for a check item it
            # must carry the one run's per-case result (05-05 Task 1) or the
            # actual output would be dropped from the page's explanation.
            result["explain"] = explain_payload(
                q, bool(sess.get("reveal")),
                run_result=result.get("run_result"))
        _refresh_attempt_view(sess, api_id, qs, path)
        payload = result
    except SystemExit as exc:
        body = _refusal_from_exit(exc.code, q)
        if body is not None:
            handler.send_json(body)
        else:
            handler.send_error(400, str(exc.code))
        return
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


def handle_font_asset(handler, name):
    """`GET /assets/fonts/<name>` -- the vendored reading faces, built
    exactly like `handle_katex_asset`: the name is resolved through the
    closed `FONT_ASSETS` map (a URL suffix to an archive-relative path and
    a MIME type) and the bytes come from `resources.read_bytes()`, so the
    checkout, the .pyz and the frozen build all serve the same files. The
    name is never joined to a filesystem path: an unknown, encoded, nested,
    traversal, or query-manipulated name is a plain 404 (T-e2m-01).
    """
    entry = FONT_ASSETS.get(name)
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


def handle_media_asset(handler, stem, name):
    """`GET /media/<stem>/<name>` -- one media file from the directory the
    bank at `stem` lives in, so a lesson can show the picture its own
    `## MEDIA` registry declares.

    Contained by resolution rather than by allowlist, because the files are
    the learner's and cannot be enumerated in advance: the stem must be one
    the startup scan already admitted, `..` is refused rather than clamped,
    the resolved real path must sit inside the bank's own directory after
    link resolution, and the extension must be a known static image type.
    Every refusal is the same plain 404, so a probe learns nothing about the
    filesystem it did not already know.
    """
    path = handler.banks.get(stem)
    if path is None:
        handler.send_not_found(stem)
        return
    if os.path.pardir in name.replace("\\", "/").split("/"):
        handler.send_not_found(name)
        return
    mime = MEDIA_ASSET_TYPES.get(os.path.splitext(name)[1].lower())
    if mime is None:
        handler.send_not_found(name)
        return
    root = os.path.realpath(os.path.dirname(os.path.abspath(path)))
    target = os.path.realpath(os.path.join(root, name))
    try:
        contained = os.path.commonpath([root, target]) == root
    except ValueError:
        contained = False
    if not contained or target == root or not os.path.isfile(target):
        handler.send_not_found(name)
        return
    try:
        with open(target, "rb") as fh:
            body = fh.read()
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
    creatable as a directory and the log must not be a directory. It never
    calls makedirs -- a lesson fetch is presentation-only and must not
    create `_evidence/` (Phase 9 D-08), so creatability is inferred from
    the grandparent instead."""
    log = evidence.log_path(bank_dir)
    parent = os.path.dirname(log)
    try:
        if os.path.isdir(log):
            return True
        if not os.path.isdir(parent):
            if os.path.exists(parent):
                # A file (or other non-directory) where the log's parent
                # directory must be: creation is impossible.
                return True
            # The parent can be created iff its own parent exists and is
            # writable; infer that without creating anything.
            grand = os.path.dirname(parent)
            if not os.path.isdir(grand) or not os.access(grand, os.W_OK):
                return True
            return False
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


def _lesson_run_path(handler, stem, path):
    """The one lesson-run file per bank stem, in the same `_attempts/`
    directory every session lives in. One file rather than one per opening,
    because a paced position is presentation state and the newest state is
    the only state worth resuming."""
    bank_dir = os.path.dirname(os.path.abspath(path)) or "."
    return os.path.join(bank_dir, "_attempts", "lessonrun_%s.json" % stem)


def _paced_context(handler, stem, path, les, params):
    """Everything one paced GET needs (plan 16D-03): the run (created on
    first entry, resumed after), the selected step, the tier disclosure to
    re-render after a wrong checkpoint, and the composed announcements.
    Degrades to None (the continuous document) when the lesson has no
    renderable steps or the run store cannot be used; a paced view that
    cannot record must not pretend it did."""
    view_steps = lesson.paced_view_steps(les) if les else []
    if not view_steps:
        return None
    step_ids = [v["id"] for v in view_steps]
    run_path = _lesson_run_path(handler, stem, path)
    run = read_lesson_run(run_path)
    if run.get("error"):
        try:
            run = start_lesson_run(path, run_path, step_ids)
        except OSError:
            run = {"error": "lesson_run.unwritable"}
    if run.get("error"):
        return {"run": None, "run_path": None, "step_id": None,
                "tier_payload": None, "tier_show_url": None,
                "announce": None}
    step_param = (params.get("step") or [""])[0] or None
    announce = None
    if step_param and step_param in step_ids:
        run = lesson_run_advance(run_path, step_param) or run
        step_id = step_param
    elif step_param:
        step_id = step_param   # lesson_page renders the fallback line
    else:
        step_id = run.get("step") or step_ids[0]
        if step_id not in step_ids:
            pass               # recorded step is gone; lesson_page renders
                               # the fallback line and shows step 1
        elif step_id != step_ids[0]:
            announce = ("Resuming at step %d."
                        % (step_ids.index(step_id) + 1))
    tier_payload = None
    tier_show_url = None
    checked = (params.get("checked") or [""])[0] or None
    show = (params.get("show") or [""])[0] or None
    target = checked or show
    if target:
        qs_all = load(path)
        q = _resolve_check(qs_all, target)
        if q is not None:
            attempts = [a for a in run.get("attempts", ())
                        if a.get("item_id") == target]
            wrong = sum(1 for a in attempts if a.get("state") == "held")
            last = next((a.get("answer") for a in reversed(attempts)
                         if "answer" in a), None)
            if last is not None:
                tier_payload = checkpoint_feedback(
                    q, last, wrong, bool(show))
                if wrong >= 1 and not show \
                        and not (tier_payload or {}).get("reveal"):
                    tier_show_url = ("/lesson/%s?view=paced&step=%s&show=%s"
                                      % (stem, step_id or step_ids[0],
                                         target))
    return {"run": run, "run_path": run_path, "step_id": step_id,
            "tier_payload": tier_payload, "tier_show_url": tier_show_url,
            "announce": announce}


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
    # 09-04/09-05: the lesson reader resolves the subject profile exactly as
    # a session would (subjects.select_profile over the bank; the stored
    # snapshot is consumed once a session id exists). Only the profile's
    # lesson.math flag turns the local KaTeX enhancement on; EMT/plain
    # profiles stay ordinary reader output (D-08). `?profile=<id>` supplies
    # the one explicit id a client may send (plan 09-05): the selector
    # resolves it once, and a profile object is never accepted.
    explicit_id = (params.get("profile") or [None])[0]
    try:
        profile = subjects.select_profile(
            qs, subjects.load_registry(
                os.path.dirname(os.path.abspath(path)) or "."),
            explicit_id=explicit_id)
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
    # Phase 16D: `?view=paced` renders one ladder step with the jump-only
    # Steps list and the pager; everything else about the render is the one
    # lesson path above. A lesson with no renderable steps, or a run store
    # that cannot be used, degrades to the continuous document.
    mode = "continuous"
    step_id = None
    tier_payload = None
    tier_show_url = None
    if (params.get("view") or [""])[0] == "paced" and not print_mode:
        paced = _paced_context(handler, stem, path, les, params)
        if paced is not None:
            mode = "paced"
            step_id = paced["step_id"]
            tier_payload = paced["tier_payload"]
            tier_show_url = paced["tier_show_url"]
            if paced["announce"]:
                announce = ((announce + " ") if announce else "") \
                    + paced["announce"]
            if gate is not None and step_id is not None:
                gate = dict(gate, paced_step=step_id)
    page = lesson.lesson_page(path, qs, les, runtime=True, drill=drill,
                              gate=gate, focus=focus, announce=announce,
                              profile=profile,
                              session_id=_session_id_for(handler, stem),
                              lan_refused=_lan_refused(handler),
                              media=parse_media(path),
                              media_base=media_base(stem),
                              activities=parse_activities(path),
                              mode=mode, step_id=step_id,
                              tier_payload=tier_payload,
                              tier_show_url=tier_show_url)
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
        # Phase 16D: a check submitted from the paced view is a lesson-run
        # checkpoint: same scorer, same store, context "lesson_run" and
        # mode "paced" on the event (D-PACED-2), the attempt summarised
        # into the run for gating and tier counts, and the redirect coming
        # back to the same paced step.
        paced_step = None
        if (fields.get("view") or [""])[-1] == "paced":
            paced_step = (fields.get("step") or [""])[-1] or None
        score = quiz.record_gate_check(
            path, check_id, answer,
            mode=("paced" if paced_step else sess.get("mode", "practice")),
            session_id=session_id,
            context=("lesson_run" if paced_step else "lesson_gate"))
        if score is None:
            handler.send_error(404, "no item %r in this bank" % check_id)
            return
        if paced_step:
            run_path = _lesson_run_path(handler, stem, path)
            run = read_lesson_run(run_path)
            prior = ([a for a in run.get("attempts", ())
                      if a.get("item_id") == check_id]
                     if not run.get("error") else [])
            wrong_before = sum(1 for a in prior if a.get("state") == "held")
            state = "correct" if score is True else "held"
            tier = 0 if score is True else (1 if wrong_before == 0 else 3)
            stored = (answer if isinstance(answer, str)
                      else [str(x) for x in answer]
                      if isinstance(answer, list) else str(answer))
            lesson_run_record(run_path, check_id,
                             {"state": state, "attempt": len(prior) + 1,
                              "tier": tier, "answer": stored})
            if score is True:
                target = ("/lesson/%s?view=paced&step=%s&reveal=check"
                          % (stem, paced_step))
            else:
                target = ("/lesson/%s?view=paced&step=%s&checked=%s"
                          % (stem, paced_step, check_id))
            handler.send_redirect(target)
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
            page = lesson.lesson_page(
                path, qs, les, runtime=True, gate=gate,
                media=parse_media(path), media_base=media_base(stem),
                activities=parse_activities(path))
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
        # Phase 16D: a paced skip opens the gate (gate on attempted; a skip
        # is the ordinary control 6.2 already made it) and returns to the
        # same step. The gate_skip event above is unchanged.
        if (fields.get("view") or [""])[-1] == "paced":
            paced_step = (fields.get("step") or [""])[-1] or None
            if paced_step:
                run_path = _lesson_run_path(handler, stem, path)
                run = read_lesson_run(run_path)
                prior = ([a for a in run.get("attempts", ())
                          if a.get("item_id") == check_id]
                         if not run.get("error") else [])
                lesson_run_record(run_path, check_id,
                                 {"state": "skipped",
                                  "attempt": len(prior) + 1, "tier": 0})
                handler.send_redirect(
                    "/lesson/%s?view=paced&step=%s&reveal=skip"
                    % (stem, paced_step))
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


def api_read_json(handler, allowed_ids=()):
    """`handler.read_json()`, but a malformed or non-object body is reported
    to the caller as `(None, True)` instead of letting the decode error
    propagate into the generic `except Exception` -> 500 clause every
    handler below also carries -- a client typo in a JSON body is exactly
    the routine, not-exotic condition D-05 asks for a clean 4xx on, not a
    500. Returns `(data, failed)`; the caller has already sent the error
    response when `failed` is true.

    `allowed_ids` names the API_FORBIDDEN_FIELDS a route may receive as a
    plain identifier -- `/api/start` accepts `profile` as a subject-profile
    ID (plan 09-05): only the id crosses the boundary, never profile
    content, which remains forbidden everywhere.
    """
    try:
        data = handler.read_json()
    except (ValueError, TypeError) as exc:
        handler.send_error(400, "malformed JSON body: %s" % exc)
        return None, True
    if not isinstance(data, dict):
        handler.send_error(400, "JSON body must be a JSON object")
        return None, True
    for field in API_FORBIDDEN_FIELDS:
        if field in data and field not in allowed_ids:
            handler.send_error(
                400, "field %r is not accepted here; a session is addressed by its "
                "session_id and a bank by its scanned stem, never by a path" % field)
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
    data, failed = api_read_json(handler, allowed_ids=("profile",))
    if failed:
        return
    bank = data.get("bank")
    path = handler.banks.get(bank) if isinstance(bank, str) else None
    if path is None:
        handler.send_not_found(bank if isinstance(bank, str) else "")
        return
    # Plan 09-05: an optional subject-profile ID. Only the id crosses the
    # boundary -- profile content, capabilities and verifiers are still
    # forbidden everywhere -- and do_start resolves it once server-side,
    # persisting the complete snapshot with the session (D-02/D-04).
    profile_id = data.get("profile")
    if profile_id is not None and (
            not isinstance(profile_id, str) or not profile_id):
        handler.send_error(400, "profile must be a non-empty profile id")
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
            result = session.do_start(path, spec, mode, out, False,
                                      profile_id=profile_id)
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
    refusal = _check_refusal_body(handler, q)
    if refusal is not None:
        handler.send_json(refusal)
        return
    try:
        result = session.do_action(
            path, {"kind": "submit", "answer": answer},
            confidence=confidence, renderer_meta=renderer_meta)
    except SystemExit as exc:
        body = _refusal_from_exit(exc.code, q)
        if body is not None:
            handler.send_json(body)
        else:
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
            q, bool(cfg.get("reveal")) if cfg is not None else False,
            run_result=result.get("run_result"))
    if mode in ("diagnostic", "exam") and result.get("action") != "advance":
        # D-12/D-13: diagnostic and unmarked exam responses carry no verdict,
        # answer, hint, explanation, or key -- the score is stripped here so
        # the served client cannot infer correctness before the release gate.
        result.pop("score", None)
        result.pop("explain", None)
        # Defence in depth: the transition never releases own-selection
        # feedback in a silent mode, and a silent mode never ships it.
        result.pop("selection_feedback", None)
    if cfg is not None and result.get("accepted") and qs:
        _refresh_attempt_view(cfg, session_id, qs, bank_path)
    handler.send_json(result)


# The one body /api/lesson/run accepts (plan 09-05): a session id, a stable
# block id, the block's language, and the edited source. Anything else --
# including every authority-shaped field (answer, action, score, correct,
# tier, evidence, path, bank, verifier, capabilities, argv) -- is refused by
# name before any state is touched (T-09-12).
LESSON_RUN_FIELDS = ("session_id", "block_id", "language", "source")
LESSON_RUN_FORBIDDEN = ("answer", "action", "score", "correct", "tier",
                        "evidence", "path", "bank", "verifier",
                        "capabilities", "argv")
LESSON_SOURCE_MAX_BYTES = 65536


def handle_api_lesson_run(handler):
    """`POST /api/lesson/run` -- `{"session_id", "block_id", "language",
    "source"}`: run one lesson code fence as an observation through the same
    bounded runner check submission uses (`runner.run_source`, plan 09-05
    D-09). The session, its stored subject profile, the bank, and the block
    are all resolved server-side; the language must be enabled in BOTH the
    stored profile's runnable_languages and the live check.languages
    settings, the default-closed LAN policy applies, and the source is
    capped at 65536 UTF-8 bytes -- every gate before `run_source()` is
    invoked (T-09-12/T-09-13).

    The response is observation only: stdout, stderr, exit_code, timed_out
    and truncated -- no passed/score/correct/verdict field exists, and the
    run changes no cursor, teaching state, or evidence (D-11, T-09-14).
    """
    if _reject_cross_origin(handler):
        return
    data, failed = api_read_json(handler)
    if failed:
        return
    extra = sorted(set(data) - set(LESSON_RUN_FIELDS))
    if extra:
        handler.send_error(400, "/api/lesson/run accepts only session_id, "
                           "block_id, language and source; field %r is not "
                           "read" % extra[0])
        return
    for forbidden in LESSON_RUN_FORBIDDEN:
        if forbidden in data:
            handler.send_error(400, "field %r is not accepted by "
                               "/api/lesson/run" % forbidden)
            return
    session_id = data.get("session_id")
    block_id = data.get("block_id")
    language = data.get("language")
    source = data.get("source")
    if not isinstance(session_id, str) or not session_id:
        handler.send_error(400, "session_id must be a non-empty string")
        return
    if not isinstance(block_id, str) or not block_id:
        handler.send_error(400, "block_id must be a non-empty string")
        return
    if not isinstance(language, str) or not language:
        handler.send_error(400, "language must be a non-empty string")
        return
    if not isinstance(source, str):
        handler.send_error(400, "source must be a string")
        return
    if len(source.encode("utf-8")) > LESSON_SOURCE_MAX_BYTES:
        handler.send_error(400, "source exceeds the %d UTF-8 byte limit"
                           % LESSON_SOURCE_MAX_BYTES)
        return
    path = api_session_path(handler, session_id)
    if path is None:
        handler.send_not_found(session_id)
        return
    try:
        data2 = read_session(path)
    except Exception as exc:
        handler.send_server_error(exc)
        return
    bank_path = data2.get("bank") or ""
    if not isinstance(bank_path, str) or not bank_path:
        handler.send_error(400, "session carries no bank")
        return
    # The stored profile snapshot (filled once at start; a legacy null slot
    # resolves in memory here -- never written -- so a lesson Run changes no
    # session state, D-11).
    profile_snapshot = data2.get("subject_profile")
    if profile_snapshot is None:
        try:
            profile_snapshot = subjects.select_profile(
                load(bank_path), subjects.load_registry(
                    os.path.dirname(os.path.abspath(bank_path)) or "."))
        except subjects.SubjectProfileError as exc:
            handler.send_error(400, str(exc))
            return
    run_languages = ((profile_snapshot.get("profile") or {})
                     .get("lesson", {}).get("runnable_languages") or [])
    if language not in run_languages:
        handler.send_json({
            "refused": lesson.RUN_LANG_UNAVAILABLE_COPY.format(
                language=language)})
        return
    cfg = settings.load_settings(handler.root)
    check_settings = cfg.get("check") or {}
    refusal = execution_refusal(handler, language, check_settings)
    if refusal is not None:
        handler.send_json({"refused": refusal})
        return
    # Confirm the block against the parsed lesson's ordered fence list
    # (the same enumeration the renderer's data-code-block ids follow).
    les = parse_lesson(bank_path)
    fences = lesson.lesson_fence_languages(les)
    try:
        index = int(block_id) - 1
    except (TypeError, ValueError):
        handler.send_error(400, "block_id must be a fence number")
        return
    if index < 0 or index >= len(fences) or fences[index] != language:
        handler.send_error(404, "no %s block %s in this lesson"
                           % (language, block_id))
        return
    check = check_settings
    try:
        result = runner.run_source(
            language, source, "",
            timeout_seconds=check.get("timeout_seconds",
                                      runner.DEFAULT_TIMEOUT_SECONDS),
            max_output_bytes=check.get("max_output_bytes",
                                       runner.DEFAULT_MAX_OUTPUT_BYTES),
            languages=check.get("languages"))
    except runner.UnknownLanguage as exc:
        handler.send_json({
            "refused": lesson.RUN_LANG_UNAVAILABLE_COPY.format(
                language=language)})
        return
    except Exception as exc:
        handler.send_server_error(exc)
        return
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


# The whole of `/api/teach`'s accepted vocabulary (plan 14-03). Two body
# fields, one action field, two action kinds -- and nothing anywhere in it
# that could name a tier. That absence IS the D-09 boundary: a client asks
# for the next tier or for nothing, and which tier that is, and what it
# contains, stays the runtime's call (T-14-10).
TEACH_BODY_FIELDS = ("session_id", "action")
TEACH_ACTION_FIELDS = ("kind",)


def _teach_reject_authority(handler, obj, where):
    """Refuse an authority-shaped field on `/api/teach` BY NAME, before any
    policy work. `API_ACTION_FORBIDDEN_FIELDS` names `tier` explicitly, which
    is the single field this route exists to keep out of a client's hands.
    Returns True when a response has already been sent.
    """
    for field in API_ACTION_FORBIDDEN_FIELDS:
        if field in obj:
            handler.send_error(
                400, "field %r is not accepted by /api/teach %s; the tier a "
                "learner reaches next is the runtime's decision and is never "
                "named by a client (D-09)" % (field, where))
            return True
    return False


def handle_api_teach(handler):
    """`POST /api/teach` -- `{"session_id": "<id>"}`, optionally with
    `{"action": {"kind": "hint" | "stumped"}}`. The browser twin of
    `itembank teach` and the first route the fixed six-tier authored ladder
    has ever had (plan 14-03, DEFECT D-D).

    Deliberately NOT a widened `/api/hint`: that route is Phase 8's model
    orchestration, and plan 08-05 removed the legacy tier shim from it on
    purpose. This one reaches `runtime.teaching_payload` through
    `session.do_teach`; the two never share a body.

    With no action this is a read -- no transition, no evidence write, no
    session write. With an action it opens exactly one tier through the same
    `session.do_action` every other sitting action goes through.

    Field discipline, in order and before any policy work: cross-origin is
    refused; `api_read_json` refuses `API_FORBIDDEN_FIELDS` (which names
    `tier`); `API_ACTION_FORBIDDEN_FIELDS` is applied to the body AND to the
    action object; any other field in either is refused 400 by name; and a
    `kind` outside the two legal values is refused naming both. There is no
    request shape that addresses a tier, and none that names the locked
    preview -- that is resolved server-side from the settings file.
    """
    if _reject_cross_origin(handler):
        return
    data, failed = api_read_json(handler)
    if failed:
        return
    if _teach_reject_authority(handler, data, "at the top level"):
        return
    unknown = sorted(k for k in data if k not in TEACH_BODY_FIELDS)
    if unknown:
        handler.send_error(
            400, "field(s) %s are not accepted by /api/teach; the session is "
            "addressed by session_id, the item is resolved server-side, and "
            "the ladder's own settings are read from disk, never from a "
            "request" % ", ".join(unknown))
        return

    kind = None
    action = data.get("action")
    if action is not None:
        if not isinstance(action, dict):
            handler.send_error(400, "action must be an object")
            return
        if _teach_reject_authority(handler, action, "inside action"):
            return
        bad = api_reject_path_fields(action)
        if bad:
            handler.send_error(
                400, "field %r is not accepted inside /api/teach's action" % bad)
            return
        unknown = sorted(k for k in action if k not in TEACH_ACTION_FIELDS)
        if unknown:
            handler.send_error(
                400, "field(s) %s are not accepted inside /api/teach's action; "
                "it carries a kind and nothing else"
                % ", ".join(unknown))
            return
        kind = action.get("kind")
        if kind not in session.TEACH_ACTION_KINDS:
            handler.send_error(
                400, "action.kind must be one of %s; a client asks for the "
                "next tier, never for a particular one (D-09)"
                % ", ".join(session.TEACH_ACTION_KINDS))
            return

    session_id = data.get("session_id")
    path = api_session_path(handler, session_id)
    if path is None:
        handler.send_not_found(session_id if isinstance(session_id, str) else "")
        return
    try:
        result = session.do_teach(path, kind=kind)
    except SystemExit as exc:
        # SystemExit derives from BaseException, so this clause must come
        # first: an except-Exception handler alone would let a routine
        # refusal kill the daemon thread instead of reporting a 400.
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


def handle_api_mark(handler):
    """`POST /api/mark` -- `{"session_id": "<id>", "item_ref": "<ref>",
    "verdict": true|false, "notes": "<optional>"}`. The browser twin of
    `itembank mark`, and the way out of a parked sitting.

    A constructed response is scored by nobody: the runtime records it with
    `score=None` and parks the sitting until a human marker rules, which is
    deliberate and stays deliberate. Until now the only place that ruling
    could be made was a terminal, so a learner sitting a bank whose short
    item came up first reached a dead end in the app and was told to go and
    type a command. This route is the same act on the surface they are
    already using.

    It composes no new authority. The verdict comes from the person at the
    keyboard, never from a model: `evidence.mark_event` pins `marker` to
    `"human"`, and a model may still only propose through
    `/api/rubric-review`. The runtime, not this handler, decides what a
    settled mark means for the cursor: the mark is appended to the same
    evidence log the CLI writes, and the next `session.do_next` collects it
    through `settled_mark_keys` and `runtime.marker_close` exactly as it
    collects a mark made from a terminal.
    """
    if _reject_cross_origin(handler):
        return
    # `verdict` is in API_FORBIDDEN_FIELDS (D-09) and stays there for every
    # other route: no client may smuggle a verdict onto a scoring path. This
    # route is the one place a verdict is the whole point, so it is admitted
    # by name through the same `allowed_ids` hatch `/api/start` uses for
    # `profile`. What that changes, recorded rather than assumed: the browser
    # on loopback is now a reviewer surface for the learner's own sitting,
    # which D-14/D-25 previously reserved to the CLI. It is the learner's
    # decision, taken 2026-09-05, because the alternative was a sitting that
    # dead-ended in the app and told them to open a terminal. Nothing else
    # moves: `marker` remains forbidden, `evidence.mark_event` still pins the
    # marker to "human", a model still may only propose through
    # `/api/rubric-review`, and the runtime still decides what a settled mark
    # means for the cursor.
    data, failed = api_read_json(handler, allowed_ids=("verdict",))
    if failed:
        return
    for banned in ("score", "correct", "rubric_pass"):
        if banned in data:
            handler.send_error(400,
                               "authority-shaped field %r refused" % banned)
            return
    session_id = data.get("session_id")
    session_file = api_session_path(handler, session_id)
    if session_file is None:
        handler.send_not_found(session_id if isinstance(session_id, str) else "")
        return
    item_ref = data.get("item_ref")
    if not isinstance(item_ref, str) or not item_ref:
        handler.send_error(400, "a mark names the item it marks")
        return
    verdict = data.get("verdict")
    if not isinstance(verdict, bool):
        handler.send_error(400, "a verdict is true or false, and nothing else")
        return
    notes = data.get("notes") or ""
    if not isinstance(notes, str):
        handler.send_error(400, "notes are text")
        return
    try:
        with open(session_file, encoding="utf-8") as fh:
            recorded = json.load(fh)
        log = evidence.log_path(os.path.dirname(recorded["bank"]))
        target = evidence_cli.resolve_marks_event(
            log, recorded["session_id"], item_ref)
        if target is None:
            handler.send_error(
                404, "no response recorded for %s in this sitting; marking "
                     "something that was never answered is not allowed"
                     % item_ref)
            return
        event = evidence.mark_event(
            recorded["session_id"], target.get("item_id", ""), item_ref,
            target["event_id"], verdict, notes=notes)
        written = evidence.append_event(log, event)
        view = session.do_next(session_file)
    except SystemExit as exc:
        handler.send_error(400, str(exc.code))
        return
    except Exception as exc:
        handler.send_server_error(exc)
        return
    handler.send_json({"schema_version": evidence.EVENT_SCHEMA_VERSION,
                       "status": written.get("status"),
                       "event_id": written.get("event_id"),
                       "item_ref": item_ref, "view": view})


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
    quiz_state_lock = threading.Lock()
    quiz_form_tokens = {}
    quiz_flash_receipts = {}
    # Set to a fresh `secrets.token_hex(16)` by cmd_sidecar; left None, the
    # CLI daemon path stays completely ungated (D-04). The token lives only in
    # this process and the shell that read it off the handshake -- never
    # persisted, never a CLI argument (T-13-01, T-13-04).
    sidecar_token = None
    # Whether this daemon is bound to all interfaces (--lan), pinned by
    # serve_scoped from cmd_daemon's lan value. Default False (loopback):
    # a caller that passes nothing -- cmd_serve, cmd_day, cmd_sidecar -- gets
    # the loopback assumption, which is what they all want.
    lan = False

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

    `request_queue_size` is set, unlike `allow_reuse_address`, because the
    stdlib default of 5 is a measured limit rather than a safe one: on
    2026-08-30, twelve concurrent connections against one daemon produced
    `ConnectionResetError(54)` on the connections past the backlog, while six
    did not. One page load already opens several connections, so 5 is inside
    the range a single learner reaches. This is a queue depth for connections
    already accepted by the kernel, not a thread cap -- `daemon_threads`
    still governs what serves them.
    """
    daemon_threads = True
    request_queue_size = 64


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
    DaemonHandler.lan = extra.get("lan", False)    # bind mode; loopback by default

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
                extra={"sessions": sessions, "collisions": collisions,
                        "lan": lan},
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
