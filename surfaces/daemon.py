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
from runtime import (PolynomialRefusal, assessment_feedback_released, checkpoint_feedback, explain_payload, fill_response_error, matching_response_error, ordering_response_error, glossable,
                     lesson_run_advance, lesson_run_record, read_lesson_run,
                     read_session, start_lesson_run, upgrade_session,
                     submission_feedback)
from surfaces import (binding_cli, course_ops, day, evidence_cli, home, ia, launcher,
                      lesson, looks, palette, presentation, quiz, quiz_page,
                      retention_view, seeding, session, settings, study,
                      update)
from surfaces import audio as audio_surface
from surfaces import theme
from surfaces import storage
from surfaces.discovery_cache import DiscoveryCache
from surfaces.session import UNKNOWN_LANGUAGE_COPY

from surfaces.routes.quiz import (
    QUIZ_ANSWER_RE,
    QUIZ_AUTHORITY_FIELDS,
    QUIZ_GET_RE,
    QUIZ_SESSION_LOCK,
    QUIZ_TOKEN_CAP,
    QUIZ_TOKEN_TTL,
    _consume_quiz_flash,
    _content_type,
    _echo_quiz_failure,
    _form_answer,
    _mint_quiz_flash,
    _mint_quiz_token,
    _prune_quiz_store,
    _quiz_launch_mode,
    _quiz_session_config,
    _send_quiz_page,
    handle_quiz_answer,
    handle_quiz_get,
)
from surfaces.routes.api import (
    _scoped_session_for,
    _teach_reject_authority,
    handle_api_bind,
    handle_api_course_accept_migration,
    handle_api_course_add_container,
    handle_api_course_add_edge,
    handle_api_course_add_objective,
    handle_api_course_add_source,
    handle_api_course_agent_operation,
    handle_api_course_apply_recommendation,
    handle_api_course_audit,
    handle_api_course_autonomy,
    handle_api_course_begin_operation,
    handle_api_course_bind_blueprint,
    handle_api_course_bind_treatment,
    handle_api_course_bindings,
    handle_api_course_blueprint_gate,
    handle_api_course_confirm_reading,
    handle_api_course_create,
    handle_api_course_create_reading,
    handle_api_course_declare_reading,
    handle_api_course_export_package,
    handle_api_course_merge_objectives,
    handle_api_course_overlay_objective,
    handle_api_course_package_losses,
    handle_api_course_place_reading,
    handle_api_course_reading_view,
    handle_api_course_recommend,
    handle_api_course_recommend_pass,
    handle_api_course_register_source,
    handle_api_course_reject_migration,
    handle_api_course_rename,
    handle_api_course_rename_objective,
    handle_api_course_replay,
    handle_api_course_restore_package,
    handle_api_course_reverse_operation,
    handle_api_course_revise_reading,
    handle_api_course_save_reading_note,
    handle_api_course_split_objective,
    handle_api_course_staleness,
    handle_api_course_structure,
    handle_api_course_treatments,
    handle_api_course_verify_package,
    handle_api_export_audio,
    handle_api_hint,
    handle_api_interact,
    handle_api_lesson_complete,
    handle_api_lesson_run,
    handle_api_mark,
    handle_api_next,
    handle_api_override,
    handle_api_report,
    handle_api_rights,
    handle_api_rubric_review,
    handle_api_shelf,
    handle_api_source_import,
    handle_api_source_recheck,
    handle_api_start,
    handle_api_submit,
    handle_api_teach,
)

from surfaces.routes.course import (
    _artifact_context,
    _restore_reopen_result,
    _send_course_artifacts,
    _send_course_context_help,
    _send_course_research,
    _send_outline_decision_recovery,
    _send_restore_workspace,
    handle_course_area_post,
    handle_course_artifacts_get,
    handle_course_artifacts_post,
    handle_course_context_help_api,
    handle_course_context_help_get,
    handle_course_context_help_post,
    handle_course_outline_post,
    handle_course_read_get,
    handle_course_reading_get,
    handle_course_research_get,
    handle_course_research_post,
    handle_restore_get,
    handle_restore_post,
    handle_restored_workspace_open,
    handle_storage_get,
    handle_storage_post,
)

from surfaces.routes.day import (
    _consume_day_force_token,
    _draft_hash,
    _gate_outcome_html,
    _issue_day_force_token,
    _plan_day_state,
    _report_card,
    _report_figure,
    _report_objective_rows,
    _retention_report_body,
    handle_day_edit,
    handle_day_get,
    handle_day_index,
    handle_day_open,
    handle_day_save,
    handle_day_task,
    handle_report_get,
    handle_study_get,
)

from surfaces.routes.lesson import (
    _gate_answer_from_form,
    _section_after_check,
    handle_gloss_get,
    handle_lesson_check,
    handle_lesson_skip,
    handle_media_asset,
)

from surfaces.routes.pages import (
    _desk_loose_banks,
    handle_banks,
    handle_disclosure,
    handle_help_get,
    handle_index,
    handle_key_review,
    handle_palette,
    sessions_by_bank,
)

from surfaces.routes.assets import (
    handle_font_asset,
    handle_katex_asset,
    handle_marker,
)

NATIVE_COURSE_TOOL_ERRORS = (ValueError, OSError, course_ops.journal.JournalError,
                             course_ops.course_module.CourseError, course_ops.course_package.PackageError)

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


def _fill_entry_error_body(exc_code, q, answer):
    """Map the runtime's key-free fill validation refusal to a retryable body."""
    if q is None or (q.get("type") != "fill" and "matching" not in q and "ordering" not in q):
        return None
    if "ordering" in q:
        message = ordering_response_error(q, answer)
    else:
        message = matching_response_error(q, answer) if "matching" in q else fill_response_error(q, answer)
    if message and str(exc_code) == message:
        return {"entry_error": message}
    return None


SKIP_DIRS = {".git", ".github", "_attempts", "_evidence"}

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
DAY_TASK_RE = re.compile(r"^/day/(?P<stem>[^/]+)/task$")
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
COURSE_READING_RE = re.compile(r"^/course/(?P<course_id>[A-Za-z0-9_.-]{1,64})/reading/(?P<occurrence_id>[a-f0-9]{16,64})/(?P<revision_id>[a-f0-9]{16,64})$")
COURSE_GET_RE = re.compile(r"^/course/(?P<course_id>[A-Za-z0-9_.-]{1,64})$")
COURSE_AREA_RE = re.compile(r"^/course/(?P<course_id>[A-Za-z0-9_.-]{1,64})/(?P<area>learn|practice|test|map|sources|build|agent|evidence)$")
COURSE_OUTLINE_RE = re.compile(r"^/course/(?P<course_id>[A-Za-z0-9_.-]{1,64})/outline/(?P<action>propose|accept|reject|undo)$")
COURSE_RESEARCH_RE = re.compile(r"^/course/(?P<course_id>[A-Za-z0-9_.-]{1,64})/research$")
COURSE_CONTEXT_HELP_RE = re.compile(r"^/course/(?P<course_id>[A-Za-z0-9_.-]{1,64})/help$")
CONTEXT_HELP_API_RE = re.compile(r"^/api/course/context-help-(?P<action>preview|start|status|cancel)$")
COURSE_ARTIFACTS_RE = re.compile(r"^/course/(?P<course_id>[A-Za-z0-9_.-]{1,64})/artifacts$")
COURSE_LESSON_RE = re.compile(r"^/course/(?P<course_id>[A-Za-z0-9_.-]{1,64})/learn/(?P<lesson_id>[A-Za-z0-9_.-]{1,64})$")
COURSE_READ_RE = re.compile(r"^/api/course/(?P<operation>outline|coverage|untreated|protocol|parity)/(?P<course_id>[A-Za-z0-9_.-]{1,64})$")

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

# The shelf route accepts the original action-only body, or one exact reorder
# body. A request never supplies a path, root, member record, or replacement
# document. The server derives those authority-shaped values from the shelf it
# just rendered and accepts only a permutation of those stable course ids.
SHELF_ACTION_ALLOWED_FIELDS = ("action",)
SHELF_REORDER_ALLOWED_FIELDS = ("action", "course_ids", "expected_fingerprint")

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
# by the read-side cross-origin check rather than the write-side one.
# Phase 19A opens the `/api/course/<operation>` namespace beside them, one
# fixed literal route per course operation (19A-CONTEXT D-02), because the
# Phase 999.3 tool table generates one MCP tool per entry here and a single
# generic `/api/course` with a discriminator would collapse the whole course
# engine into one untyped tool. `create` and `rename` are 19A-01's family;
# `bind` and `rights` moved into the namespace in the same commit, with
# their original paths kept serving in `LEGACY_API_ALIASES` below.
# 19A-02 completes the source-binding family beside them: `add-source`
# records the sidecar row that `bind` needs and that no surface wrote, and
# `bindings` is the family's one READ, so it is the one route here gated by
# the read-side check rather than the write-side one. 19A-03 adds the
# structure and objective-editing families: three rows that add a container,
# an objective or an edge, four that move objective identity as a reviewed
# proposal, and `structure`, the second READ. The
# length is asserted by `check_api_route_scope` in
# `tests/daemon_roundtrip.py`, and every entry is mirrored in ROUTE_CLI and
# SURFACE_PARITY (Extensibility Rule 9(a)).
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
    ("POST", "/api/course/create-reading", "handle_api_course_create_reading"),
    ("POST", "/api/course/reading-view", "handle_api_course_reading_view"),
    ("POST", "/api/course/save-reading-note", "handle_api_course_save_reading_note"),
    ("POST", "/api/course/confirm-reading", "handle_api_course_confirm_reading"),
    ("POST", "/api/course/declare-reading", "handle_api_course_declare_reading"),
    ("POST", "/api/course/revise-reading", "handle_api_course_revise_reading"),
    ("POST", "/api/course/place-reading", "handle_api_course_place_reading"),
    ("POST", "/api/course/create", "handle_api_course_create"),
    ("POST", "/api/course/register-source", "handle_api_course_register_source"),
    ("POST", "/api/course/rename", "handle_api_course_rename"),
    ("POST", "/api/course/add-source", "handle_api_course_add_source"),
    ("POST", "/api/course/bind", "handle_api_bind"),
    ("POST", "/api/course/bind-treatment", "handle_api_course_bind_treatment"),
    ("POST", "/api/course/treatments", "handle_api_course_treatments"),
    ("POST", "/api/course/autonomy", "handle_api_course_autonomy"),
    ("POST", "/api/course/begin-operation", "handle_api_course_begin_operation"),
    ("POST", "/api/course/replay", "handle_api_course_replay"),
    ("POST", "/api/course/reverse-operation", "handle_api_course_reverse_operation"),
    ("POST", "/api/course/recommend", "handle_api_course_recommend"),
    ("POST", "/api/course/recommend-pass", "handle_api_course_recommend_pass"),
    ("POST", "/api/course/apply-recommendation", "handle_api_course_apply_recommendation"),
    ("POST", "/api/course/rights", "handle_api_rights"),
    ("POST", "/api/course/bindings", "handle_api_course_bindings"),
    ("POST", "/api/course/add-container", "handle_api_course_add_container"),
    ("POST", "/api/course/add-objective", "handle_api_course_add_objective"),
    ("POST", "/api/course/add-edge", "handle_api_course_add_edge"),
    ("POST", "/api/course/structure", "handle_api_course_structure"),
    ("POST", "/api/course/rename-objective", "handle_api_course_rename_objective"),
    ("POST", "/api/course/split-objective", "handle_api_course_split_objective"),
    ("POST", "/api/course/merge-objectives", "handle_api_course_merge_objectives"),
    ("POST", "/api/course/overlay-objective", "handle_api_course_overlay_objective"),
    ("POST", "/api/course/accept-migration", "handle_api_course_accept_migration"),
    ("POST", "/api/course/reject-migration", "handle_api_course_reject_migration"),
    ("POST", "/api/course/bind-blueprint", "handle_api_course_bind_blueprint"),
    ("POST", "/api/course/blueprint-gate", "handle_api_course_blueprint_gate"),
    ("POST", "/api/course/audit", "handle_api_course_audit"),
    ("POST", "/api/course/staleness", "handle_api_course_staleness"),
    ("POST", "/api/course/export-package", "handle_api_course_export_package"),
    ("POST", "/api/course/verify-package", "handle_api_course_verify_package"),
    ("POST", "/api/course/restore-package", "handle_api_course_restore_package"),
    ("POST", "/api/course/package-losses", "handle_api_course_package_losses"),
    ("POST", "/api/course/agent-operation", "handle_api_course_agent_operation"),
    ("POST", "/api/export_audio", "handle_api_export_audio"),
    ("POST", "/api/lesson/run", "handle_api_lesson_run"),
    ("POST", "/api/source/import", "handle_api_source_import"),
    ("POST", "/api/source/recheck", "handle_api_source_recheck"),
    ("POST", "/api/shelf", "handle_api_shelf"),
)

# The two paths the source-binding door landed on before this namespace
# existed (2026-09-05), kept serving so nothing that already calls them
# breaks, and kept OUT of API_ROUTES on purpose (19A-01, amending 19A-CONTEXT
# D-02). They are deprecated aliases of the canonical `/api/course/bind` and
# `/api/course/rights`, not a second convention: an entry here reserves no MCP
# tool name and appears in no SURFACE_PARITY row, so the Phase 999.3 tool
# table generated from API_ROUTES gets exactly one tool per operation instead
# of an operation and its alias. They are retired by an explicit `migrate`
# once nothing calls them, which is the additive-then-deprecate path
# non-negotiable 4 describes; retiring them silently is what is forbidden.
LEGACY_API_ALIASES = (
    ("POST", "/api/bind", "handle_api_bind"),
    ("POST", "/api/rights", "handle_api_rights"),
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
    ("GET", "/courses", "handle_courses_get"),
    ("GET", "/banks", "handle_banks"),
    ("GET", "/restore", "handle_restore_get"),
    ("POST", "/restore", "handle_restore_post"),
    ("POST", "/restore/open", "handle_restored_workspace_open"),
    ("GET", MARKER_PATH, "handle_marker"),
    ("GET", "/day", "handle_day_index"),
    ("GET", "/report", "handle_report_get"),
    ("GET", "/settings", "handle_settings_get"),
    ("GET", "/settings/storage", "handle_storage_get"),
    ("POST", "/settings/storage", "handle_storage_post"),
    ("GET", "/palette", "handle_palette"),
    ("GET", "/disclosure", "handle_disclosure"),
    ("GET", "/activity", "handle_activity_get"),
    ("POST", "/api/theme", "handle_theme_post"),
    ("POST", "/cli-twin", "handle_cli_twin"),
    ("POST", "/seed/accept", "handle_seed_accept"),
    ("POST", "/mcp", "handle_mcp"),
) + API_ROUTES + LEGACY_API_ALIASES + (
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
    ("POST", DAY_TASK_RE, "handle_day_task"),
    ("GET", HELP_GET_RE, "handle_help_get"),
    ("GET", COURSE_READING_RE, "handle_course_reading_get"),
    ("GET", COURSE_GET_RE, "handle_course_get"),
    ("GET", COURSE_AREA_RE, "handle_course_area_get"),
    ("POST", COURSE_AREA_RE, "handle_course_area_post"),
    ("POST", COURSE_OUTLINE_RE, "handle_course_outline_post"),
    ("GET", COURSE_RESEARCH_RE, "handle_course_research_get"),
    ("POST", COURSE_RESEARCH_RE, "handle_course_research_post"),
    ("GET", COURSE_CONTEXT_HELP_RE, "handle_course_context_help_get"),
    ("POST", COURSE_CONTEXT_HELP_RE, "handle_course_context_help_post"),
    ("POST", CONTEXT_HELP_API_RE, "handle_course_context_help_api"),
    ("GET", COURSE_ARTIFACTS_RE, "handle_course_artifacts_get"),
    ("POST", COURSE_ARTIFACTS_RE, "handle_course_artifacts_post"),
    ("GET", COURSE_LESSON_RE, "handle_course_lesson_get"),
    ("GET", COURSE_READ_RE, "handle_course_read_get"),
)

# Every route in ROUTES has a CLI command that reaches the same runtime
# call -- SURF-04's "every route has a CLI equivalent" as a machine-checkable
# inventory instead of a claim in prose. The key set here is asserted equal
# to ROUTES' (method, pattern) pairs, so a route added without an entry here
# fails the build instead of shipping silently.
ROUTE_CLI = {
    ("GET", "/"): "daemon",
    ("GET", "/courses"): "daemon",
    ("GET", "/banks"): "daemon",
    ("GET", MARKER_PATH): "daemon",
    ("GET", "/report"): "report",
    ("GET", "/settings"): "theme",
    ("GET", "/settings/storage"): "storage",
    ("POST", "/settings/storage"): "storage",
    # The palette's own CLI twin is `itembank help-code`, the other command
    # whose whole job is telling a person what exists.
    ("GET", "/palette"): "help-code",
    ("GET", "/disclosure"): "disclosure",
    ("GET", "/activity"): "activity",
    ("POST", "/api/theme"): "theme",
    ("POST", "/cli-twin"): "cli-twin",
    ("POST", "/seed/accept"): "seed",
    ("POST", "/mcp"): "mcp",
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
    ("POST", "/api/course/create-reading"): "course",
    ("POST", "/api/course/reading-view"): "course",
    ("POST", "/api/course/save-reading-note"): "course",
    ("POST", "/api/course/confirm-reading"): "course",
    ("POST", "/api/course/declare-reading"): "course",
    ("POST", "/api/course/revise-reading"): "course",
    ("POST", "/api/course/place-reading"): "course",
    ("POST", "/api/course/create"): "course",
    ("POST", "/api/course/register-source"): "course",
    ("POST", "/api/course/rename"): "course",
    ("POST", "/api/course/add-source"): "course",
    ("POST", "/api/course/bind"): "bind",
    ("POST", "/api/course/bind-treatment"): "bind",
    ("POST", "/api/course/treatments"): "bind",
    ("POST", "/api/course/autonomy"): "course",
    ("POST", "/api/course/begin-operation"): "course",
    ("POST", "/api/course/replay"): "course",
    ("POST", "/api/course/reverse-operation"): "course",
    ("POST", "/api/course/recommend"): "course",
    ("POST", "/api/course/recommend-pass"): "course",
    ("POST", "/api/course/apply-recommendation"): "course",
    ("POST", "/api/course/rights"): "bind",
    ("POST", "/api/course/bindings"): "bind",
    ("POST", "/api/course/add-container"): "course",
    ("POST", "/api/course/add-objective"): "course",
    ("POST", "/api/course/add-edge"): "course",
    ("POST", "/api/course/structure"): "course",
    ("POST", "/api/course/rename-objective"): "course",
    ("POST", "/api/course/split-objective"): "course",
    ("POST", "/api/course/merge-objectives"): "course",
    ("POST", "/api/course/overlay-objective"): "course",
    ("POST", "/api/course/accept-migration"): "course",
    ("POST", "/api/course/reject-migration"): "course",
    ("POST", "/api/course/bind-blueprint"): "course",
    ("POST", "/api/course/blueprint-gate"): "course",
    ("POST", "/api/course/audit"): "course",
    ("POST", "/api/course/staleness"): "course",
    ("POST", "/api/course/export-package"): "course",
    ("POST", "/api/course/verify-package"): "course",
    ("POST", "/api/course/restore-package"): "course",
    ("POST", "/api/course/package-losses"): "course",
    ("POST", "/api/course/agent-operation"): "course",
    # The two deprecated aliases. Same twin as the canonical route, because
    # they are the same call.
    ("POST", "/api/bind"): "bind",
    ("POST", "/api/rights"): "bind",
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
    ("POST", DAY_TASK_RE): "day",
    ("GET", HELP_GET_RE): "help-code",
    ("GET", COURSE_READING_RE): "course",
    ("GET", COURSE_GET_RE): "daemon",
    ("GET", COURSE_AREA_RE): "daemon",
    ("POST", COURSE_AREA_RE): "course",
    ("POST", COURSE_OUTLINE_RE): "course",
    ("GET", COURSE_RESEARCH_RE): "daemon",
    ("POST", COURSE_RESEARCH_RE): "daemon",
    ("GET", COURSE_LESSON_RE): "daemon",
    ("GET", COURSE_CONTEXT_HELP_RE): "daemon",
    ("POST", COURSE_CONTEXT_HELP_RE): "daemon",
    ("POST", CONTEXT_HELP_API_RE): "daemon",
    ("GET", COURSE_ARTIFACTS_RE): "daemon",
    ("POST", COURSE_ARTIFACTS_RE): "daemon",
    ("GET", "/restore"): "daemon",
    ("POST", "/restore"): "daemon",
    ("POST", "/restore/open"): "daemon",
    ("GET", COURSE_READ_RE): "course",
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
    (("POST", "/api/course/create-reading"), "course", "course_create_reading"),
    (("POST", "/api/course/reading-view"), "course", "course_reading_view"),
    (("POST", "/api/course/save-reading-note"), "course", "course_save_reading_note"),
    (("POST", "/api/course/confirm-reading"), "course", "course_confirm_reading"),
    (("POST", "/api/course/declare-reading"), "course", "course_declare_reading"),
    (("POST", "/api/course/revise-reading"), "course", "course_revise_reading"),
    (("POST", "/api/course/place-reading"), "course", "course_place_reading"),
    (("POST", "/api/course/create"), "course", "course_create"),
    (("POST", "/api/course/register-source"), "course", "course_register_source"),
    (("POST", "/api/course/rename"), "course", "course_rename"),
    (("POST", "/api/course/add-source"), "course", "course_add_source"),
    (("POST", "/api/course/bind"), "bind", "bind"),
    (("POST", "/api/course/bind-treatment"), "bind", "bind_treatment"),
    (("POST", "/api/course/treatments"), "bind", "course_treatments"),
    (("POST", "/api/course/autonomy"), "course", "course_autonomy"),
    (("POST", "/api/course/begin-operation"), "course", "course_begin_operation"),
    (("POST", "/api/course/replay"), "course", "course_replay"),
    (("POST", "/api/course/reverse-operation"), "course", "course_reverse_operation"),
    (("POST", "/api/course/recommend"), "course", "course_recommend"),
    (("POST", "/api/course/recommend-pass"), "course", "course_recommend_pass"),
    (("POST", "/api/course/apply-recommendation"), "course", "course_apply_recommendation"),
    (("POST", "/api/course/rights"), "bind", "rights_record"),
    (("POST", "/api/course/bindings"), "bind", "course_bindings"),
    (("POST", "/api/course/add-container"), "course", "course_add_container"),
    (("POST", "/api/course/add-objective"), "course", "course_add_objective"),
    (("POST", "/api/course/add-edge"), "course", "course_add_edge"),
    (("POST", "/api/course/structure"), "course", "course_structure"),
    (("POST", "/api/course/rename-objective"), "course", "course_rename_objective"),
    (("POST", "/api/course/split-objective"), "course", "course_split_objective"),
    (("POST", "/api/course/merge-objectives"), "course", "course_merge_objectives"),
    (("POST", "/api/course/overlay-objective"), "course", "course_overlay_objective"),
    (("POST", "/api/course/accept-migration"), "course", "course_accept_migration"),
    (("POST", "/api/course/reject-migration"), "course", "course_reject_migration"),
    (("POST", "/api/course/bind-blueprint"), "course", "course_bind_blueprint"),
    (("POST", "/api/course/blueprint-gate"), "course", "course_blueprint_gate"),
    (("POST", "/api/course/audit"), "course", "course_audit"),
    (("POST", "/api/course/staleness"), "course", "course_staleness"),
    (("POST", "/api/course/export-package"), "course", "course_export_package"),
    (("POST", "/api/course/verify-package"), "course", "course_verify_package"),
    (("POST", "/api/course/restore-package"), "course", "course_restore_package"),
    (("POST", "/api/course/package-losses"), "course", "course_package_losses"),
    (("POST", "/api/course/agent-operation"), "course", "course_agent_operation"),
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
        if not body:
            body = ('<section class="empty"><h2>No activity yet</h2>'
                    '<p>Agent and maintenance work will appear here when it '
                    'needs attention or finishes.</p>'
                    '<p><a class="go" href="/courses">Browse courses</a></p>'
                    '</section>')
    handler.send_html(presentation.surface_shell(
        "Activity", body,
        theme_css=theme.theme_css(settings.load_settings(handler.root)),
        back={"href": "/courses", "label": "Back to courses"},
        palette=True).encode("utf-8"))


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
  var dirty = false;
  function warnOnUnsaved(e) {
    if (!dirty) { return; }
    e.preventDefault();
    e.returnValue = "";
  }
  document.addEventListener("input", function (e) {
    if (e.target && e.target.closest("form")) {
      dirty = true;
      window.addEventListener("beforeunload", warnOnUnsaved);
    }
  });
  document.addEventListener("submit", function () {
    dirty = false;
    window.removeEventListener("beforeunload", warnOnUnsaved);
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
    """Use the evidence reader's live counts and explicit availability state."""
    return evidence.course_counts(evidence.log_path(course_dir))


def _current_binding_rows(doc):
    """Return legacy bindings plus the head of each versioned chain.

    A superseded treatment must not keep publishing an activity in a course
    area. Validation owns malformed-chain refusal; this projection only needs
    the same unambiguous head rule for already parsed course documents.
    """
    rows = list(doc.get("bindings") or ())
    superseded = {row.get("supersedes_binding_revision_id") for row in rows
                  if row.get("supersedes_binding_revision_id")}
    return [row for row in rows
            if not row.get("binding_revision_id")
            or row.get("binding_revision_id") not in superseded]


def _course_bank_treatments(course_dir, doc, banks):
    """Map each scanned course bank to its explicit assessment treatments.

    The source object records the evidence and rights basis. The locator names
    the derived assessment artifact. Resolve only the locator's path component
    inside the course root. A missing, ambiguous, or escaping locator
    classifies nothing.
    """
    course_root = os.path.realpath(course_dir)
    by_path = dict((os.path.realpath(path), stem) for stem, path in banks)
    bank_objectives = {}
    for stem, path in banks:
        try:
            bank_objectives[stem] = {q.get("objective") for q in load(path)
                                     if q.get("objective")}
        except Exception:
            bank_objectives[stem] = set()
    source_ids = {row.get("source_object_id")
                  for row in (doc.get("sources") or ())}
    treatments = dict((stem, set()) for stem, _path in banks)
    for row in _current_binding_rows(doc):
        if (row.get("binding_kind") != "treatment"
                or row.get("source_object_id") not in source_ids
                or row.get("treatment_kind") not in ("practice", "formal-test")):
            continue
        locator = row.get("locator")
        if not isinstance(locator, str) or not locator.strip():
            continue
        match = re.match(r"^(.+?\.md)(?=$|[\s,;#])", locator.strip(), re.I)
        if match is None:
            continue
        rel_path = match.group(1)
        if os.path.isabs(rel_path):
            continue
        candidate = os.path.realpath(os.path.join(course_dir, rel_path))
        try:
            inside = os.path.commonpath([course_root, candidate]) == course_root
        except ValueError:
            inside = False
        if not inside:
            continue
        stem = by_path.get(candidate)
        if stem is not None:
            treatments[stem].add(row["treatment_kind"])
            continue
        # Older graphs located the supporting source passage rather than the
        # derived bank. Exact objective identity still provides a bounded,
        # non-filename join for those accepted records.
        for bank_stem, objectives in bank_objectives.items():
            if row.get("objective") in objectives:
                treatments[bank_stem].add(row["treatment_kind"])
    return treatments


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
            "bank_stem": stem,
            "title": title,
            "meta": "%d item%s" % (len(qs), "" if len(qs) == 1 else "s"),
            "note": "Practice keeps you on an item until it is right."})

    record = None
    course_module = graph_module = None
    try:
        import course as course_module
        import graph as graph_module
        record = course_module.read_course(course_dir)
    except Exception:
        record = None
    doc = (record or {}).get("doc") or {}

    readings = []
    if area in ("learn", "overview") and record:
        try:
            from surfaces.reading_desk import href
            validated = graph_module.validate_reading_graph(doc)
            reading_rows = validated["occurrences"]
            parents = {row["supersedes_revision_id"] for row in reading_rows}
            for row in reading_rows:
                if row["revision_id"] not in parents:
                    readings.append({"href": href(state["course_id"], row),
                                     "title": validated["placements"][row["occurrence_id"]]["title"],
                                     "meta": row.get("preparation_mode", ""),
                                     "note": "Open the accepted source range and shared private notes."})
        except (ValueError, KeyError):
            pass
    if area == "learn":
        return ("Start with the source, then use a lesson where it helps. "
                "Both remain readable outside this app."), readings + lessons
    assessment_treatments = _course_bank_treatments(course_dir, doc, banks)
    resume = ia._course_resume_state(
        getattr(handler, 'root', os.path.dirname(course_dir)), course_dir)
    def sitting_rows(row, mode):
        path = next(path for stem, path in banks if stem == row["bank_stem"])
        saved = [s for s in resume["sessions"]
                 if os.path.realpath(s["bank"]) == os.path.realpath(path)
                 and s["mode"] == mode]
        if saved:
            result = []
            for sitting in saved:
                href = ("/report?session=" + urllib.parse.quote(sitting["session_id"], safe="")
                        if sitting["status"] == "complete" else
                        _quiz_path(row["bank_stem"], mode,
                                   session_id=sitting["session_id"],
                                   course_id=state["course_id"]))
                result.append(dict(row, href=href,
                                   title=("Resume " if sitting["status"] == "active" else "Report: ") + row["title"],
                                   meta=("%s, item %d of %d" %
                                         (mode.capitalize(), min(sitting["position"] + 1,
                                                                  sitting["total"]), sitting["total"])
                                         if sitting["status"] == "active" else
                                         "%s complete" % mode.capitalize()),
                                   note="Saved on this device."))
            return result
        if resume["state"] == "unavailable":
            return [dict(row, href="", title=row["title"] + " needs recovery",
                         note="A saved sitting could not be read. Review session files before starting again.")]
        return [dict(row, href=_quiz_path(row["bank_stem"], mode,
                                          course_id=state["course_id"]))]
    if area == "practice":
        rows = [sitting for row in quizzes
                if "practice" in assessment_treatments.get(row["bank_stem"], set())
                for sitting in sitting_rows(row, "practice")]
        return ("A practice sitting scores as you go, unlocks one hint tier "
                "per genuine wrong attempt, and never shows a key you have "
                "not earned."), rows
    if area == "test":
        rows = []
        for row in quizzes:
            stem = row["bank_stem"]
            if "formal-test" not in assessment_treatments.get(stem, set()):
                continue
            rows.extend(sitting_rows(dict(
                row, note="A fixed sitting uses every item and defers feedback until completion."),
                "exam"))
        return ("A formal test uses the runtime's exam policy, a fixed complete "
                "selection, and no answer-by-answer feedback."), rows
    if area == "map":
        rows = []
        containers = {c.get("id"): c.get("title") or c.get("label") or ""
                      for c in (doc.get("structure") or [])}
        for index, rec in enumerate(doc.get("objectives") or []):
            rows.append({
                "href": "#objective-%d" % index,
                "title": rec.get("statement") or rec.get("id") or "",
                "meta": containers.get(rec.get("container"), ""),
                "note": ""})
        return ("The objectives this course is accountable for, in the order "
                "its scope records them."), rows
    if area == "sources":
        rows = []
        for index, rec in enumerate(doc.get("sources") or []):
            oid = rec.get("source_object_id") or ""
            state = "unknown"
            if course_module is not None and graph_module is not None:
                try:
                    state = course_module.rights_for_binding(
                        course_dir, oid, graph_module.SOURCE_BINDING_RIGHT)
                except Exception:
                    state = "unknown"
            rows.append({
                "href": "?source=%d#source-%d" % (index, index),
                "title": rec.get("title") or oid,
                "meta": "read right: %s" % state,
                "note": rec.get("note") or ""})
        return ("What this course is built from. A source is bound where it "
                "lives; nothing here is a copy."), rows
    if area == "evidence":
        counts = _course_evidence_counts(course_dir)
        if counts["state"] == "unavailable":
            return ("Evidence history is unavailable. Counts are unknown until "
                    "the local record can be read."), [
                {"href": "#course-review-history", "title": "Inspect recorded evidence",
                 "meta": "", "note": "Review the recovery details below, then reload this page."},
                {"href": ia.deep_link_target(state["course_id"], "evidence")["path"],
                 "title": "Reload evidence", "meta": "",
                 "note": "Reload after restoring access or repairing the record."}]
        if counts["state"] == "empty":
            return "No assessment response history is recorded in this course yet.", [
                {"href": "#course-review-history", "title": "Inspect recorded evidence",
                 "meta": "", "note": "Reading declarations and saved sittings are shown separately below."}]
        partial = counts["state"] == "incomplete"
        rows = [
            {"href": "#evidence-responses", "title": "%d response%s recorded"
             % (counts["responses"], "" if counts["responses"] == 1 else "s"),
             "meta": "Readable records only" if partial else "", "note": ""},
            {"href": "#evidence-marks", "title": "%d mark%s settled"
             % (counts["marks"], "" if counts["marks"] == 1 else "s"),
             "meta": "", "note": ""},
            {"href": "#evidence-sessions", "title": "%d sitting%s"
             % (counts["sessions"], "" if counts["sessions"] == 1 else "s"),
             "meta": "", "note": ""},
        ]
        if partial:
            rows.insert(0, {"href": "#course-review-history",
                            "title": "Inspect incomplete evidence history", "meta": "",
                            "note": "Some records are unreadable or unsupported. These counts cover readable records only."})
            rows.append({"href": ia.deep_link_target(state["course_id"], "evidence")["path"],
                         "title": "Reload evidence", "meta": "",
                         "note": "Reload after restoring the local record."})
            return "Evidence history is incomplete. Counts below are partial.", rows
        return ("Your own record, in this course's own store. Nothing here "
                "left this machine."), rows
    if area == "overview":
        rows = []
        if readings:
            rows.append(dict(readings[0], href=readings[0]["href"] + "?from=overview",
                             title="Read the source",
                             note=readings[0]["title"]))
        if lessons:
            rows.append({"href": lessons[0]["href"], "title": "Explore the lesson",
                         "meta": lessons[0]["meta"], "note": lessons[0]["title"]})
        practice = next((row for row in quizzes
                         if "practice" in assessment_treatments.get(row["bank_stem"], set())), None)
        if practice:
            practice_rows = sitting_rows(practice, "practice")
            activity = next((row for row in practice_rows
                             if row["title"].startswith("Resume ")), practice_rows[0])
            rows.append(dict(activity,
                             title=("Resume practice" if activity["title"].startswith("Resume ")
                                    else "Review practice report" if activity["title"].startswith("Report: ")
                                    else "Practice what you learned" if activity.get("href")
                                    else "Practice needs recovery"),
                             note=activity.get("note") if not activity.get("href")
                             else practice["title"]))
        objectives = len(doc.get("objectives") or [])
        sources = len(doc.get("sources") or [])
        counts = _course_evidence_counts(course_dir)
        lead = ("%d objective%s, %d bound source%s, %d bank%s. "
                % (objectives, "" if objectives == 1 else "s",
                   sources, "" if sources == 1 else "s",
                   len(quizzes), "" if len(quizzes) == 1 else "s"))
        if counts["state"] == "unavailable":
            lead += "Evidence history is unavailable; response counts are unknown."
        elif counts["state"] == "incomplete":
            lead += ("Evidence history is incomplete: %d response%s in readable records."
                     % (counts["responses"], "" if counts["responses"] == 1 else "s"))
        elif counts["state"] == "empty":
            lead += "No response history is recorded yet."
        else:
            lead += "%d recorded response%s." % (
                counts["responses"], "" if counts["responses"] == 1 else "s")
        return lead, rows
    return "", []


def _course_missed_review_forms(handler, course_dir, course_id):
    """Offer a new practice sitting only for recorded, auto-scored misses.

    The form names a scanned bank stem. The POST resolves that stem again and
    the selector re-reads live evidence, so this display grants no authority.
    """
    forms = []
    for stem, path in _course_banks(handler, course_dir):
        log = evidence.log_path(os.path.dirname(os.path.abspath(path)))
        if not os.path.exists(log):
            continue
        counts = evidence.course_counts(log)
        if not counts["complete"]:
            return ('<p role="status">Missed-item review is unavailable while '
                    'recorded evidence is incomplete or unreadable. Inspect '
                    'the recorded history below, then reload.</p>')
        if counts["state"] == "empty":
            continue
        try:
            history = evidence.objective_history(
                log, "", bank=os.path.basename(path))
            missed = selection.missed_item_keys(history)
            count = sum(1 for q in load(path)
                        if evidence.evidence_key(q) in missed)
        except Exception:
            return ('<p role="status">Missed-item review is unavailable. '
                    'The recorded evidence could not be read.</p>')
        if not count:
            continue
        active = _active_missed_session(handler, path)
        label = ("Resume missed-item review" if active else
                 "Review %d previously missed practice item%s in %s" %
                 (count, "" if count == 1 else "s",
                  _bank_title(path, stem)))
        forms.append(
            '<form method="post" action="/course/%s/evidence">'
            '<input type="hidden" name="action" value="review_missed">'
            '<input type="hidden" name="bank" value="%s">'
            '<button class="go" type="submit">%s</button></form>'
            % (presentation.esc(course_id), presentation.esc(stem),
               presentation.esc(label)))
    if not forms:
        return ('<p>No previously missed practice items are recorded. '
                'Pending prose and blind test responses are excluded.</p>')
    return ('<section aria-labelledby="missed-review"><h3 id="missed-review">'
            'Review previous misses</h3><p>Open a practice sitting with the '
            'recorded items, or resume one already in progress. Pending prose '
            'and blind test responses '
            'are excluded.</p>%s</section>' % "".join(forms))


def _course_mock_forms(handler, course_dir, course_id):
    """Show available item types for a separate, configurable exam sitting."""
    forms = []
    for stem, path in _course_banks(handler, course_dir):
        counts = {}
        try:
            for question in load(path):
                name = question.get("type")
                if name in ("mc", "multi", "table", "dnd", "build",
                            "short", "check", "visual"):
                    counts[name] = counts.get(name, 0) + 1
        except Exception:
            continue
        if not counts:
            continue
        inputs = []
        for index, (name, available) in enumerate(sorted(counts.items())):
            initial = min(available, 10) if (
                name == "mc" or ("mc" not in counts and index == 0)) else 0
            inputs.append(
                '<label><span>%s <small>(%d available)</small></span>'
                '<input type="number" name="mix_%s" min="0" max="%d" '
                'value="%d" required></label>' %
                (presentation.esc(name.upper()), available,
                 presentation.esc(name), available, initial))
        forms.append(
            '<form class="mock-form" method="post" action="/course/%s/test">'
            '<input type="hidden" name="action" value="start_mock">'
            '<input type="hidden" name="bank" value="%s">'
            '<fieldset><legend>%s</legend><div class="mock-fields">%s'
            '<label><span>Minutes <small>(0 for untimed)</small></span>'
            '<input type="number" name="minutes" min="0" max="240" '
            'value="30" required></label></div></fieldset>'
            '<button class="go" type="submit">Start mock test</button>'
            '</form>' % (presentation.esc(course_id), presentation.esc(stem),
                         presentation.esc(_bank_title(path, stem)),
                         "".join(inputs)))
    if not forms:
        return '<p>No assessment bank is available for a mock test.</p>'
    return ('<style>.mock-form{max-width:46rem;padding:1rem 1.2rem;'
            'margin:1rem 0;border:1px solid rgba(127,127,127,.4);'
            'border-radius:.8rem}.mock-form fieldset{border:0;padding:0;'
            'margin:0}.mock-form legend{font-weight:600;margin-bottom:.8rem}'
            '.mock-fields{display:flex;flex-wrap:wrap;gap:1rem 1.5rem}'
            '.mock-fields label{display:grid;gap:.35rem;min-width:9rem}'
            '.mock-fields small{font-weight:400}.mock-fields input{'
            'box-sizing:border-box;width:100%%;max-width:9rem;padding:.45rem;'
            'font:inherit;color:inherit;background:transparent;'
            'border:1px solid rgba(127,127,127,.55);border-radius:.35rem}'
            '.mock-form button{margin-top:1rem}</style>'
            '<section aria-labelledby="mock-test"><h3 id="mock-test">'
            'Configure a mock test</h3><p>Choose an exact mix. The sitting '
            'uses exam feedback and stays separate from the fixed formal '
            'test.</p>%s</section>' % "".join(forms))


def _active_missed_session(handler, bank_path):
    """The newest active review for this exact scanned bank, if one exists."""
    matches = []
    for session_id, path in session_index(handler.root).items():
        try:
            data = read_session(path)
            if (data.get("bank") == os.path.abspath(bank_path)
                    and data.get("status") == "active"
                    and data.get("mode") == "practice"
                    and data.get("selection_mode") == "missed"):
                matches.append((os.path.getmtime(path), session_id))
        except (OSError, ValueError, SystemExit):
            continue
    return max(matches, default=(None, None))[1]


# The bind panel (2026-09-05). The surface grid measured `source binding /
# create` as the central act of building a course and as having no surface at
# all; this is that surface, and it is deliberately plain: two selects, a
# locator, the two vocabularies as selects rather than free text, and the
# rights record beside it, because a binding refused for a right the learner
# never declared is the most likely outcome on a fresh course and the way
# out has to be on the same page.
BIND_PANEL = """
<style>
.bind-panel .bind-grid{min-width:0}
.bind-panel .bind-grid select,.bind-panel .bind-grid input{width:100%;
  min-width:0;box-sizing:border-box}
.bind-panel .area-lead,.bind-panel .status{overflow-wrap:anywhere}
</style>
<section class="bind-panel" aria-labelledby="bind-heading">
<h3 id="bind-heading">Bind a source to an objective</h3>
<p class="area-lead">A binding is a claim that this passage covers this
objective. It records what it consumes: a coverage binding needs the source's
read right, and a treatment needs whichever right that treatment consumes.</p>
<div class="bind-grid">
  <label for="bind-objective">Objective</label>
  <select id="bind-objective" data-bind-objective>__OBJECTIVES__</select>
  <label for="bind-source">Source</label>
  <select id="bind-source" data-bind-source>__SOURCES__</select>
  <label for="bind-locator">Locator</label>
  <input id="bind-locator" type="text" data-bind-locator
    placeholder="sources/notes.md#a-heading, or a page range">
  <label for="bind-treatment">Treatment</label>
  <select id="bind-treatment" data-bind-treatment>__TREATMENTS__</select>
  <label for="bind-state">Coverage state</label>
  <select id="bind-state" data-bind-state>__STATES__</select>
  <label for="bind-confidence">Confidence</label>
  <select id="bind-confidence" data-bind-confidence>__CONFIDENCES__</select>
</div>
<p class="actions"><button type="button" class="go" data-bind-submit>Record
this binding</button></p>
<p class="status" role="status" aria-live="polite" data-bind-status>__TWIN__</p>
</section>
<section class="bind-panel" aria-labelledby="rights-heading">
<h3 id="rights-heading">What may be done with each source</h3>
<p class="area-lead">Your declaration about your own file. Unknown stays
restrictive, so a source refuses a binding until you say otherwise. Recording
a right changes no bytes.</p>
__RIGHTS_ROWS__
<p class="status" role="status" aria-live="polite" data-rights-status></p>
</section>
<script>
(function () {
  var course = "__COURSE_ID__";
  function post(route, body, status, ok) {
    status.textContent = "Recording…";
    fetch(window.location.origin + route, {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify(body)
    }).then(function (res) {
      if (!res.ok) { return res.text().then(function (t) { throw new Error(t); }); }
      return res.json();
    }).then(function () { window.location.reload(); })
      .catch(function (err) {
        var text = String(err.message || err);
        var at = text.indexOf("<p>");
        if (at >= 0) { text = text.slice(at + 3, text.indexOf("</p>", at)); }
        status.textContent = text.replace(/&#x27;/g, "'") || "That was refused.";
      });
  }
  var submit = document.querySelector("[data-bind-submit]");
  var status = document.querySelector("[data-bind-status]");
  if (submit) {
    submit.addEventListener("click", function () {
      var treatment = document.querySelector("[data-bind-treatment]").value;
      var payload = {
        course_id: course,
        objective: document.querySelector("[data-bind-objective]").value,
        source: document.querySelector("[data-bind-source]").value,
        locator: document.querySelector("[data-bind-locator]").value,
        state: document.querySelector("[data-bind-state]").value,
        confidence: document.querySelector("[data-bind-confidence]").value,
        binding_kind: treatment ? "treatment" : "source"
      };
      if (treatment) { payload.treatment = treatment; }
      post("/api/course/bind", payload, status);
    });
  }
  var rstatus = document.querySelector("[data-rights-status]");
  Array.prototype.forEach.call(
    document.querySelectorAll("[data-rights-set]"), function (button) {
      button.addEventListener("click", function () {
        var grants = {};
        grants[button.getAttribute("data-right")] =
          button.getAttribute("data-value");
        post("/api/course/rights", {
          course_id: course,
          source: button.getAttribute("data-rights-set"),
          grants: grants
        }, rstatus);
      });
    });
})();
</script>
"""


def _options(values, labels=None, blank=""):
    out = []
    if blank:
        out.append('<option value="">%s</option>' % presentation.esc(blank))
    for value in values:
        label = (labels or {}).get(value, value)
        out.append('<option value="%s">%s</option>'
                   % (presentation.esc(value), presentation.esc(label)))
    return "".join(out)


def _agent_area_html(handler, state, course_dir):
    """The durable, JavaScript-optional proposal review flow."""
    from surfaces import agent_operation as agent_op
    cfg = settings.load_settings(handler.root)
    records = agent_op.proposals(course_dir)
    requests = agent_op.request_history(course_dir)
    selected = urllib.parse.parse_qs(urllib.parse.urlsplit(getattr(handler, "path", "")).query).get("proposal", [""])[-1]
    active = next((r for r in records if r.get("proposal_id") == selected), None)
    if active is None:
        active = next((r for r in records if r.get("disposition") == "proposed"),
                      records[0] if records else None)
    cid = presentation.esc(state["course_id"])
    area = "build" if state.get("area") == "build" else "agent"
    action_path = "/course/%s/%s" % (cid, area)

    def field(name, value):
        return '<input type="hidden" name="%s" value="%s">' % (
            presentation.esc(name), presentation.esc(value or ""))

    starts = []
    for skill, spec in sorted((cfg.get("agent_runs") or {}).items()):
        target = spec.get("target") if isinstance(spec, dict) else ""
        starts.append('<li><form method="post" action="%s">%s%s'
                      '<button class="go" type="submit">Start %s</button> '
                      '<span class="mono">Target: %s</span>%s</form></li>'
                      % (action_path, field("action", "start_async"), field("skill", skill),
                         presentation.esc(skill), presentation.esc(target),
                         ('<p>Requested sources: %s</p>' % presentation.esc(", ".join(spec.get("citations") or []))
                          if isinstance(spec, dict) and spec.get("citations") else "")))
    if not starts:
        starts.append('<li>No course drafting operation is configured. Add an agent run in Settings with a course-local target and source citations.</li>')

    if active:
        pid = active.get("proposal_id") or ""
        disposition = active.get("disposition") or "unavailable"
        copy = {"proposed": "Proposal pending review.",
                "accepted": "Proposal accepted. One journaled change was applied.",
                "rejected": "Proposal rejected. No accepted course content changed.",
                "conflicted": "The target changed after this proposal was created. Nothing was overwritten.",
                "undone": "Accepted change undone. The previous accepted state was restored and the reversal was recorded."}.get(
                    disposition, "Agent operation unavailable. %s" % (active.get("reason") or "Record unreadable."))
        citations = "".join("<li>%s</li>" % presentation.esc(str(c))
                            for c in active.get("citations") or []) or "<li>No citations supplied.</li>"
        diff_info = active.get("diff") or {}
        diff = presentation.esc("\n".join(diff_info.get("lines") or []))
        if diff_info.get("withheld"):
            diff += "\n%s more lines withheld from this preview." % int(diff_info["withheld"])
        validation = active.get("validation") or {}
        findings = "".join('<li>%s</li>' % presentation.esc(str(finding))
                           for finding in validation.get("findings") or [])
        controls = ""
        lesson_review = ""
        if disposition == "proposed":
            if active.get("kind") == "lesson":
                try:
                    preview = agent_op.lesson_preview(course_dir, pid)
                except ValueError:
                    lesson_review = '<p role="status">Lesson preview is unavailable for this draft.</p>'
                else:
                    lesson_review = (
                        '<h4>Lesson preview</h4><div class="lesson-preview" '
                        'role="region" aria-label="Learner lesson preview">%s</div>'
                        '<details><summary>Plain Markdown draft</summary><pre>%s</pre></details>'
                        '<form method="post" action="%s">%s%s%s'
                        '<p><label>Paragraph to replace<textarea name="before_paragraph" '
                        'required></textarea></label></p>'
                        '<p><label>Replacement paragraph<textarea name="after_paragraph" '
                        'required></textarea></label></p>'
                        '<button class="go" type="submit">Revise this paragraph</button></form>'
                        % (preview["html"], presentation.esc(preview["markdown"]),
                           action_path, field("action", "revise"),
                           field("proposal_id", pid),
                           field("expected_draft_fingerprint", preview["draft_fingerprint"])))
            decision_draft = (field("expected_draft_fingerprint", agent_op.draft_fingerprint(active["draft"]))
                              if active.get("skill") == "course-outline" else "")
            reject = ('<form method="post" action="%s">%s%s%s'
                      '<button class="go" type="submit" aria-label="Reject proposal %s">Reject proposal</button></form>'
                      % (action_path, field("action", "reject"), field("proposal_id", pid), decision_draft, presentation.esc(pid)))
            if (cfg.get("auditor_autonomy") or "report_only") in agent_op.AUTONOMY_MAY_WRITE:
                accept = ('<form method="post" action="%s">%s%s%s'
                          '<button class="go primary" type="submit" aria-label="Accept proposal %s">Accept proposal</button></form>'
                          % (action_path, field("action", "accept"), field("proposal_id", pid), decision_draft, presentation.esc(pid)))
            else:
                accept = '<p>Accept is unavailable because auditor_autonomy is report_only. Change it in Settings, Agent autonomy, if you want reviewed proposals to become revisions.</p>'
            controls = '<div class="actions" role="group" aria-label="Proposal decision">%s%s</div>' % (accept, reject)
        elif disposition == "accepted" and active.get("undoable"):
            controls = ('<form method="post" action="%s">%s%s'
                        '<button class="go primary" type="submit" aria-label="Undo accepted change for %s">Undo accepted change</button></form>'
                        % (action_path, field("action", "undo"), field("proposal_id", pid),
                           presentation.esc(active.get("target") or pid)))
        review = ('<section aria-labelledby="agent-review"><h3 id="agent-review">Review proposed change</h3>'
                  '<div role="status" aria-live="polite"><p>%s</p></div>'
                  '<dl><dt>Proposal</dt><dd class="mono">%s</dd><dt>Target</dt><dd>%s</dd>'
                  '<dt>Expected fingerprint</dt><dd class="mono">%s</dd><dt>Validation</dt><dd>%s</dd>'
                  '<dt>Egress</dt><dd>%s</dd></dl><h4>Citations</h4><ul>%s</ul>'
                  '<h4>Validation findings</h4>%s'
                  '<div class="vf-diff" role="region" aria-label="Proposed change diff"><pre tabindex="0" aria-label="Proposed change text">%s</pre></div>%s%s'
                  '<details><summary>Review evidence</summary><p class="mono">Operation %s. Interaction %s. Journal %s. Undo %s.</p></details></section>'
                  % (presentation.esc(copy), presentation.esc(pid), presentation.esc(active.get("target") or "Unavailable"),
                     presentation.esc(active.get("expected_fingerprint") or "new file"),
                     presentation.esc(str(validation.get("state") or "unknown")),
                     presentation.esc(str((active.get("egress") or {}).get("destination") or "local")), citations,
                     '<ul>%s</ul>' % findings if findings else '<p>No findings recorded.</p>', diff,
                     lesson_review, controls,
                     presentation.esc(active.get("operation_id") or ""), presentation.esc(active.get("interaction_id") or ""),
                     presentation.esc(active.get("entry_id") or "none"), presentation.esc(active.get("undo_entry_id") or "none")))
    else:
        review = '<section><h3>No saved proposals yet</h3><p>Start a skill to create a reviewable proposal. Accepted files change only after review and acceptance.</p></section>'
    history = "".join('<li><a href="/course/%s/%s?proposal=%s">%s</a> '
                      '<span class="mono">%s</span>, %s</li>'
                      % (cid, area, urllib.parse.quote(r.get("proposal_id") or "", safe=""),
                         presentation.esc(r.get("disposition") or "unavailable"),
                         presentation.esc(r.get("proposal_id") or "unknown"),
                         presentation.esc(r.get("target") or r.get("reason") or "")) for r in records)
    request_rows = []
    for r in requests:
        control = ''
        action, label = None, None
        if r.get('request_state') == 'running':
            action, label = 'cancel', 'Cancel this request'
        elif r.get('request_state') in ('settled', 'unresolved'):
            action, label = 'retry', 'Retry as a new request (may repeat provider cost)'
        if action:
            control = ('<form method="post" action="%s">%s%s'
                '<button class="go" type="submit">%s</button></form>') % (
                action_path, field('action', action), field('proposal_id', r.get('proposal_id')), label)
        request_rows.append('<li><strong>%s</strong>: %s <span class="mono">%s</span>'
            '<p>%s</p>%s%s</li>' % (
                presentation.esc(r.get('skill') or 'Author request'),
                presentation.esc(r.get('request_state') or 'unknown'),
                presentation.esc(r.get('target') or ''),
                presentation.esc(r.get('next_action') or 'No durable result yet.'),
                '<p>Retry of %s.</p>' % presentation.esc(r['retry_of']) if r.get('retry_of') else '', control))
    request_rows = ''.join(request_rows)
    request_section = ('<section aria-label="Author request recovery"><h3>Request history</h3>'
                       '<p><a href="%s">Refresh request status</a></p>'
                       '<ul class="course-rows">%s</ul></section>' % (action_path, request_rows)) if request_rows else ""
    return ('<div class="agent-operation-workspace"><p>Configured operations draft a course-local file for review. Check the '
            '<a href="/course/%s/map">objective map</a> and '
            '<a href="/course/%s/sources">bound sources</a> before starting. '
            'The runtime remains the sole scoring authority.</p>'
            '<section><h3>Start an agent operation</h3><ul class="course-rows">%s</ul></section>%s%s'
            '<section><h3>Review history</h3><ul class="course-rows">%s</ul></section>'
            '<p class="mono">CLI twin: itembank course agent-operation %s status --proposal-id &lt;id&gt;</p></div>'
            % (cid, cid, "".join(starts), request_section, review, history or "<li>No records.</li>", cid))


def _course_area_extra(handler, state, course_dir):
    """Context, review, and source binding markup beyond area rows."""
    if course_dir is not None and state.get("area") == "learn":
        return '<p><a href="/course/%s/artifacts">Save and review my original work</a></p>' % urllib.parse.quote(state["course_id"], safe="")
    if course_dir is not None and state.get("area") in ("agent", "build"):
        body = _agent_area_html(handler, state, course_dir)
        if state.get("area") == "build":
            from surfaces import course_workbench
            try:
                import course
                query = urllib.parse.parse_qs(urllib.parse.urlsplit(handler.path).query)
                selected = query.get("outline", [None])
                if len(selected) != 1:
                    raise ValueError("agent.invalid_outline_selection")
                body += course_workbench.outline_panel(
                    course_dir, course.read_course(course_dir)["doc"], selected[0])
            except Exception as exc:
                body += '<p role="status">Outline is unavailable: %s. Reload the accepted course and proposal before editing.</p>' % presentation.esc(str(exc))
        return body
    if course_dir is not None and state.get("area") in ("map", "sources", "evidence"):
        from surfaces import course_workbench
        try:
            import course
            doc = course.read_course(course_dir)["doc"]
        except Exception:
            return ('<p role="status">Course details are unavailable until the '
                    'course record can be read. Repair the course record, then reload.</p>')
        banks = _course_banks(handler, course_dir)
        detail = course_workbench.details(handler, state, course_dir, doc, banks)
        if state.get("area") != "sources":
            return detail
    else:
        detail = ""
    if course_dir is None or state.get("area") != "sources":
        return ""
    from surfaces import open_notebook
    detail += '<p><a href="/course/%s/research">Select exact source context and private quote notes</a></p>' % urllib.parse.quote(state["course_id"], safe="")
    detail += open_notebook.panel()
    try:
        reading = binding_cli.bindings(course_dir)
    except Exception:
        return detail + '<p role="status">Source binding controls are unavailable. Review the accepted source details above.</p>'
    objectives = {}
    for row in reading["objectives"]:
        text = row["statement"] or row["id"]
        objectives[row["id"]] = text[:96]
    sources = {}
    for row in reading["sources"]:
        sources[row["source_object_id"]] = row["title"]
    treatments = dict(
        (kind, "%s (consumes %s)" % (kind, reading["treatment_rights"][kind]))
        for kind in reading["treatment_kinds"])
    rights_rows = []
    for row in reading["sources"]:
        chips = []
        for name in sorted(row["rights"]):
            value = row["rights"][name]
            want = "denied" if value == "granted" else "granted"
            chips.append(
                '<button type="button" class="go ghost" data-rights-set="%s" '
                'data-right="%s" data-value="%s">%s: %s &rarr; %s</button>'
                % (presentation.esc(row["source_object_id"]),
                   presentation.esc(name), want, presentation.esc(name),
                   presentation.esc(value), want))
        rights_rows.append(
            '<div class="row"><div class="row-head"><b>%s</b></div>'
            '<p class="actions">%s</p></div>'
            % (presentation.esc(row["title"]), "".join(chips)))
    return (detail + BIND_PANEL
            .replace("__OBJECTIVES__",
                     _options(sorted(objectives), objectives))
            .replace("__SOURCES__", _options(sorted(sources), sources))
            .replace("__TREATMENTS__",
                     _options(reading["treatment_kinds"], treatments,
                              blank="None: a coverage binding"))
            .replace("__STATES__", _options(reading["states"]))
            .replace("__CONFIDENCES__", _options(reading["confidences"]))
            .replace("__RIGHTS_ROWS__", "".join(rights_rows))
            .replace("__COURSE_ID__", presentation.esc(state["course_id"]))
            .replace("__TWIN__", presentation.esc(
                "The CLI twin is itembank bind source --objective <id> "
                "--source <id> --locator <where>.")))


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


def _course_guidance_state(handler, state, course_dir):
    """Read one recommendation for the course frame and its action links."""
    from surfaces import course_workbench
    try:
        import course
        doc = course.read_course(course_dir)["doc"]
        guidance = course_workbench.course_guidance(
            handler.root, course_dir, doc, _course_banks(handler, course_dir))
    except (OSError, ValueError, KeyError):
        doc = {}
        guidance = {"kind": "unavailable", "title": "Inspect recorded evidence",
                    "reason": "The course or recorded history could not be read. Restore access to the local records, then reload.",
                    "href": ia.deep_link_target(state["course_id"], "evidence")["path"],
                    "objective": None}
    return doc, guidance


def _course_guidance_html(handler, state, course_dir, *, recommendation=None):
    """Render the shared read-only recommendation, preserving exact return links."""
    doc, guidance = (recommendation if recommendation is not None else
                     _course_guidance_state(handler, state, course_dir))
    kind = guidance["kind"]
    href = guidance["href"]
    title = guidance["title"]
    reason = guidance["reason"]
    objective_html = ""
    objective = guidance.get("objective")
    if objective:
        matched = next(((index, row) for index, row in enumerate(doc.get("objectives") or ())
                        if row.get("id") == objective), None)
        objective_text = objective
        if matched:
            objective_text = matched[1].get("statement") or objective
            target = ia.deep_link_target(state["course_id"], "map")["path"] + "#objective-%d" % matched[0]
            objective_html = ('<p class="course-guidance-objective">Current objective: '
                              '<a href="%s">%s</a></p>' % (
                                  presentation.esc(target), presentation.esc(objective_text)))
        else:
            objective_html = '<p class="course-guidance-objective">Current objective: %s</p>' % presentation.esc(objective_text)
    actions = ['<a class="go primary" data-guidance-action href="%s">%s</a>'
               % (presentation.esc(href), presentation.esc(title))]
    if kind == 'due':
        query = urllib.parse.parse_qs(urllib.parse.urlsplit(href).query)
        actions = ['<form method="post" action="%s"><input type="hidden" name="action" value="start_due">'
                       '<input type="hidden" name="bank" value="%s"><input type="hidden" name="objective" value="%s">'
                       '<button class="go primary" data-guidance-action style="width:100%%" type="submit">Start due practice</button></form>' % (
                           presentation.esc(ia.deep_link_target(state['course_id'], 'practice')['path']),
                           presentation.esc(query['bank'][0]), presentation.esc(objective))]
        actions.append('<a class="go ghost" href="%s">Choose another activity</a>' %
                       presentation.esc(ia.deep_link_target(state['course_id'], 'learn')['path']))
    resume_href = guidance.get("resume_href")
    if resume_href and resume_href != href:
        actions.append('<a class="go ghost" data-course-resume href="%s">Resume this exact sitting</a>'
                       % presentation.esc(resume_href))
    elif kind == "resume":
        actions[0] = actions[0].replace("data-guidance-action", "data-guidance-action data-course-resume")
    if kind == "unavailable":
        actions.append('<a class="go ghost" href="%s">Reload course</a>'
                       % presentation.esc(ia.deep_link_target(state["course_id"], "overview")["path"]))
    return ('<section id="course-guidance" class="course-guidance" '
            'data-course-guidance="%s" aria-labelledby="course-guidance-title">'
            '<h3 id="course-guidance-title">Next activity</h3>%s'
            '<p class="course-guidance-reason"><strong>Why this activity:</strong> %s</p>'
            '<div class="course-guidance-actions">%s</div></section>'
            % (presentation.esc(kind), objective_html, presentation.esc(reason), "".join(actions)))


def _app_nav(current):
    """The small, stable application frame shared by shelf and course pages."""
    courses_current = ' aria-current="page"' if current == "courses" else ""
    return ('<nav class="app-nav" aria-label="Application">'
            '<a class="app-name" href="/"%s>itembank</a><ul>'
            '<li><a href="/courses"%s>Courses</a></li>'
            '<li><a href="/activity">Activity</a></li>'
            '<li><a href="/settings">Settings</a></li></ul></nav>'
            % (' aria-current="page"' if current == "home" else "", courses_current))


def _course_action_label(card):
    """Keep the canonical verb visible when the course name is beside it."""
    resume = card.get("resume") or {}
    if resume.get("state") == "active" and card["cta_href"].startswith("/quiz/"):
        active = [row for row in resume.get("sessions", ())
                  if row.get("status") == "active"]
        if len(active) == 1 and active[0].get("mode") in ("practice", "exam"):
            return "Resume practice" if active[0]["mode"] == "practice" else "Resume test"
    if resume.get("state") == "ambiguous":
        return "Choose a saved sitting"
    label = card["cta_label"]
    for verb in ("Start", "Resume", "Open", "Choose", "Reconcile"):
        if label == verb + " " + card["name"]:
            return verb
    return label


def _desk_session_context(card):
    """Describe a known runtime position without inferring scores or mastery."""
    resume = card.get("resume") or {}
    if resume.get("state") != "active":
        return ""
    active = [row for row in resume.get("sessions", ()) if row.get("status") == "active"]
    if len(active) != 1:
        return ""
    row = active[0]
    position, total = row.get("position"), row.get("total")
    if (type(position) is not int or type(total) is not int
            or not 0 <= position < total or row.get("mode") not in ("practice", "exam")):
        return ""
    return "%s · Question %d of %d" % (
        "Practice" if row["mode"] == "practice" else "Test", position + 1, total)


def _desk_focus_card(cards):
    """Prefer a canonical resumable sitting, preserving course order as the tie-break."""
    return next((card for card in cards
                 if (card.get("resume") or {}).get("state") == "active"
                 and card["cta_href"].startswith("/quiz/")), cards[0] if cards else None)


def _desk_hero(card):
    """Lead with a saved sitting when available, otherwise the first course."""
    if card is None:
        return ""
    return (
        '<section class="desk-focus" aria-labelledby="desk-focus-title">'
        '<div class="desk-focus-copy">'
        '<p class="desk-eyebrow">%s</p>'
        '<h2 id="desk-focus-title">%s</h2>'
        '<p class="desk-session-context"%s>%s</p>'
        '<p class="resume-cue">%s</p></div>'
        '<div class="desk-focus-actions"><a class="go primary" href="%s" aria-label="%s">%s</a></div>'
        '</section>'
        % ("Continue a saved session" if (card.get("resume") or {}).get("state") == "active"
           and card["cta_href"].startswith("/quiz/") else "First in your course order",
           presentation.esc(card["name"]),
           "" if _desk_session_context(card) else " hidden",
           presentation.esc(_desk_session_context(card)),
           presentation.esc(card["resume_cue"]),
           presentation.esc(card["cta_href"]),
           presentation.esc(card["cta_label"]),
           presentation.esc(_course_action_label(card))))


COURSE_FRAME_CSS = """
.course-workspace > h1{font-size:var(--text-title);line-height:1.15;
  margin-block:var(--space-2) var(--space-4);overflow-wrap:anywhere}
.course-workspace .course-areas{margin-bottom:var(--space-3)}
.course-workspace .overhaul-course-content > h2{margin-block:var(--space-3)}
.course-workspace .course-guidance{margin-block:var(--space-3);padding:var(--space-3)}
.course-workspace .overhaul-saved-sittings{margin-block:var(--space-4)}
.course-workspace .overhaul-saved-sittings > summary{cursor:pointer;
  min-height:44px;display:list-item;padding-block:var(--space-2);font-weight:600}
"""


def _course_frame(handler, state, back, course_dir=None):
    """One course-level page: the area nav, the area's own stated state,
    a real anchor target on the heading, and the hidden anchor-missing region
    the restoration script reveals. No pagination control, no page-number link,
    and no item cap, so reading scrolls."""
    nav = []
    primary_nav = []
    tool_nav = []
    for index, entry in enumerate(state["nav"]):
        item = ('<li><a aria-label="%s" href="%s"%s>%s</a></li>'
                % (presentation.esc(entry["label"]),
                   presentation.esc(entry["href"]),
                   ' aria-current="page"' if entry["current"] else "",
                   presentation.esc(entry["label"])))
        nav.append(item)
        (primary_nav if index < 4 else tool_nav).append(item)
    heading_id = ia.anchor_slug(state["area_label"]) or "area"
    lead, rows = _course_area_rows(handler, state, course_dir)
    overview_had_activities = bool(rows)
    recommendation = None
    if state["area"] == "overview" and course_dir:
        recommendation = _course_guidance_state(handler, state, course_dir)
        doc, guidance = recommendation
        accepted_id = doc.get("header", {}).get("course_object_id", state["course_id"])

        def action_key(href):
            target = urllib.parse.urlsplit(href or "")
            query = [(key, accepted_id if key == "course" and value == state["course_id"] else value)
                     for key, value in urllib.parse.parse_qsl(target.query, keep_blank_values=True)]
            return (target.scheme, target.netloc, target.path, tuple(sorted(query)), target.fragment)

        current_actions = {action_key(guidance["href"]), action_key(guidance.get("resume_href"))}
        rows = [row for row in rows if not row.get("href") or
                action_key(row["href"]) not in current_actions]
    saved_html = ""
    if state["area"] == "evidence" and course_dir:
        saved_html = _course_missed_review_forms(
            handler, course_dir, state["course_id"])
    if state["area"] == "test" and course_dir:
        saved_html = _course_mock_forms(
            handler, course_dir, state["course_id"])
    if state["area"] == "overview" and course_dir:
        resume = ia._course_resume_state(handler.root, course_dir)
        saved_rows = []
        admitted_banks = {}
        for stem, path in _course_banks(handler, course_dir):
            admitted_banks.setdefault(os.path.realpath(path), []).append(stem)
        for sitting in resume["sessions"]:
            matches = admitted_banks.get(os.path.realpath(sitting["bank"])) or []
            if len(matches) != 1:
                saved_rows.append({"href": "", "title": "Saved sitting is unavailable",
                                   "note": "Restore the exact admitted bank and sitting before resuming."})
                continue
            stem = matches[0]
            title = _bank_title(sitting["bank"], stem)
            href = ("/report?session=" + urllib.parse.quote(sitting["session_id"], safe="")
                    if sitting["status"] == "complete" else
                    _quiz_path(stem, sitting["mode"],
                               session_id=sitting["session_id"],
                               course_id=state["course_id"]))
            saved_rows.append({"href": href,
                               "title": ("Resume " if sitting["status"] == "active" else "Review ") + title,
                               "meta": ("%s, item %d of %d" %
                                        (sitting["mode"].capitalize(),
                                         min(sitting["position"] + 1, sitting["total"]),
                                         sitting["total"])
                                        if sitting["status"] == "active" else
                                        "%s complete" % sitting["mode"].capitalize()),
                               "note": "Saved on this device."})
        if saved_rows:
            needs_recovery = (resume["state"] == "unavailable" or
                              any(not row.get("href") for row in saved_rows))
            saved_html = ('<details class="overhaul-saved-sittings"%s>'
                          '<summary id="saved-sittings">Saved sittings (%d)</summary>%s</details>'
                          % (" open" if needs_recovery else "", len(saved_rows),
                             _course_rows_html(saved_rows)))
            if resume.get("cue") and "unavailable" in resume["cue"]:
                saved_html = '<p role="status">%s</p>' % presentation.esc(resume["cue"]) + saved_html
        elif resume["state"] == "unavailable":
            saved_html = '<p role="status">A saved sitting is unavailable. Review session files before starting again.</p>'
    if state["area"] in ("build", "agent"):
        content = ""
    elif state["area"] == "overview" and course_dir:
        course_path = ('' if overview_had_activities and not rows else
                       '<section class="overview-path" aria-labelledby="course-path">'
                       '<h3 id="course-path">Your course path</h3>%s</section>' % (
                           _course_rows_html(rows) if rows else
                           '<p>No learning activity is bound to this course yet.</p>'))
        content = ('%s<p class="area-lead">%s</p>%s'
                   % (_course_guidance_html(handler, state, course_dir,
                                            recommendation=recommendation),
                      presentation.esc(lead), course_path))
    elif state['area'] == 'practice' and course_dir:
        recommendation = _course_guidance_state(handler, state, course_dir)
        guidance = recommendation[1]
        if rows and guidance["kind"] == "start":
            # A learner who opened Practice should not meet a primary button
            # leading away from it. The generic first-step advice stays as a
            # secondary link; due, resume, review and pending advice keep the band.
            content = ('<p class="area-lead">%s</p>%s<p class="practice-source-hint" '
                       'data-course-guidance="start">New to this objective? '
                       '<a data-guidance-action href="%s">%s</a> first.</p>' % (
                           presentation.esc(lead), _course_rows_html(rows),
                           presentation.esc(guidance["href"]),
                           presentation.esc(guidance["title"])))
        else:
            content = '<p class="area-lead">%s</p>%s%s' % (
                presentation.esc(lead),
                _course_guidance_html(handler, state, course_dir,
                                      recommendation=recommendation),
                _course_rows_html(rows) if rows else '<p>No practice is bound to this course yet.</p>')
    elif rows:
        content = ('<p class="area-lead">%s</p>%s'
                   % (presentation.esc(lead), _course_rows_html(rows))
                   if lead else _course_rows_html(rows))
    else:
        action = state.get("next_action")
        action_html = (('<p><a class="go" href="%s">%s</a></p>'
                        % (presentation.esc(action["href"]),
                           presentation.esc(action["label"]))) if action else "")
        notice = ("No fixed formal test is bound to this course yet."
                  if state["area"] == "test" and
                  'action="/course/' in saved_html else state["notice"])
        content = ('<div class="area-state" data-course-state="%s">'
                   '<p>%s</p>%s</div>'
                   % (presentation.esc(state.get("display_state", "empty")),
                      presentation.esc(notice), action_html))
    tool_current = state["area"] not in ("overview", "learn", "practice", "test")
    tool_label = ("Course tools: %s" % state["area_label"] if tool_current
                  else "Course tools")
    tool_menu = ('<details class="course-tools"><summary>%s</summary>'
                 '<ul>%s</ul></details>'
                 % (presentation.esc(tool_label), "".join(tool_nav))
                 if tool_nav else "")
    desktop_nav = ('<nav class="course-areas course-nav-desktop" '
                   'aria-label="Course areas"><ul>%s</ul>%s</nav>'
                   % ("".join(primary_nav), tool_menu))
    mobile_nav = ('<details class="course-areas course-nav-mobile">'
                  '<summary>Course area: %s</summary>'
                  '<nav aria-label="Course areas"><ul>%s</ul></nav></details>'
                  % (presentation.esc(state["area_label"]), "".join(nav)))
    body = (_app_nav("course") + desktop_nav + mobile_nav
            + ('<div class="state" data-anchor-missing hidden role="status">'
               "<p>%s</p></div>"
               '<div class="overhaul-course-content"><h2 id="%s">%s</h2>%s%s</div>'
               % (presentation.esc(ia.ANCHOR_NOT_FOUND_NOTICE),
                  presentation.esc(heading_id),
                  presentation.esc(state["area_label"]),
                  content + saved_html if state["area"] == "overview" else saved_html + content,
                  _course_area_extra(handler, state, course_dir))))
    cfg = settings.load_settings(handler.root)
    profile, _notice = settings.resolve_presentation_profile(cfg)
    return presentation.surface_shell(
        state["course_name"], body,
        theme_css=theme.theme_css(cfg),
        back=back, noscript=COURSE_NOSCRIPT, tail=RESTORE_SCRIPT,
        palette=True, presentation_profile=profile,
        classes="course-workspace", extra_css=COURSE_FRAME_CSS)


def _course_not_found(handler):
    """A 404 that carries no filesystem path and links the one page that
    explains the state."""
    body = ('<p>%s</p><p><a href="/help/ia.route_not_found">'
            "Read more about this</a></p>"
            % presentation.esc(ia.AREA_NOT_FOUND_NOTICE))
    handler.send_html(presentation.surface_shell(
        "That link does not resolve", body,
        theme_css=theme.theme_css(settings.load_settings(handler.root)),
        back={"href": "/courses", "label": "Back to courses"}).encode("utf-8"), 404)


def _course_page_state(handler, course_id, area):
    """Resolve a page through the read-operation door before rendering it.

    The page state remains presentation data owned by ``ia``.  The canonical
    outline read establishes that the addressed course is readable through the
    same operation layer an agent uses, instead of letting the page be an
    unvalidated, parallel course lookup.
    """
    _refresh_discovery(handler)
    try:
        course_ops.run(handler.root, "outline", {"course_id": course_id})
    except Exception:
        return None
    return ia.course_area_state(handler.root, course_id, area)


def _course_source_return(handler, course_id, query=None):
    """Derive read-only source-review navigation from one admitted identity.

    Query values never supply a URL or source text. The current clean course
    graph owns membership and order, so removed or ambiguous identities retain
    the task's existing origin. ``query`` admits the same field inside an
    already validated saved-sitting return.
    """
    if query is None:
        query = urllib.parse.parse_qs(
            urllib.parse.urlsplit(getattr(handler, "path", "")).query,
            keep_blank_values=True)
    values = query.get("return_source", [])
    if (not course_id or len(values) != 1 or
            not isinstance(values[0], str) or
            not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", values[0])):
        return None
    try:
        import course
        base = course_ops.resolve_course(handler.root, course_id)
        read = course.read_course(base)
        if read.get("state") != "clean":
            return None
        doc = read["doc"]
        current_id = doc["header"]["course_object_id"]
        matches = [index for index, row in enumerate(doc.get("sources") or [])
                   if row.get("source_object_id") == values[0]]
        if len(matches) != 1 or not isinstance(current_id, str) or not current_id:
            return None
        index = matches[0]
        return {"href": "/course/%s/sources?source=%d#source-%d" % (
                    urllib.parse.quote(current_id, safe=""), index, index),
                "label": "Back to source review", "course_id": current_id,
                "source_id": values[0]}
    except Exception:
        # A failed optional return projection cannot make the task unavailable.
        return None


def handle_course_get(handler, course_id):
    """`GET /course/<course_id>` -- the course Overview frame."""
    state = _course_page_state(handler, course_id, "overview")
    if state is None:
        _course_not_found(handler)
        return
    if not state["found"]:
        _course_not_found(handler)
        return
    handler.send_html(_course_frame(
        handler, state, {"href": "/courses", "label": "Back to courses"},
        course_dir=ia.course_dir_for(handler.root, course_id)).encode("utf-8"))


def handle_course_area_get(handler, course_id, area):
    """`GET /course/<course_id>/<area>` -- one named course area.

    Layout width is a rendering decision inside this handler and never a
    second URL for the same object, so both widths are served by this one
    route and the nav lists all eight areas at either width.
    """
    state = _course_page_state(handler, course_id, area)
    if state is None:
        _course_not_found(handler)
        return
    if not state["found"]:
        _course_not_found(handler)
        return
    back = {"href": "/course/" + course_id,
            "label": "Back to " + state["course_name"]}
    if area == "map":
        back = _course_source_return(handler, course_id) or back
    handler.send_html(_course_frame(
        handler, state, back,
        course_dir=ia.course_dir_for(handler.root, course_id)).encode("utf-8"))


def handle_course_lesson_get(handler, course_id, lesson_id):
    """`GET /course/<course_id>/learn/<lesson_id>` -- one lesson inside Learn."""
    state = _course_page_state(handler, course_id, "learn")
    if state is None:
        _course_not_found(handler)
        return
    if not state["found"]:
        _course_not_found(handler)
        return
    handler.send_html(_course_frame(
        handler, state,
        {"href": "/course/" + course_id,
         "label": "Back to " + state["course_name"]}).encode("utf-8"))


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


def scan_dir(root, classification_cache=None):
    """Walk current candidates, optionally reusing unchanged classifications."""
    if classification_cache is None:
        return _scan_dir(root)
    with classification_cache.scan(root) as classification:
        return _scan_dir(root, classification)


def _scan_dir(root, classification=None):
    """Walk `root` and its explicitly linked courses, then classify `.md`.

    This is the startup-built allowlist every route resolves a client-
    supplied stem through -- a handler never joins a client string onto a
    filesystem path (T-2-01). `parse_bank()` returning a non-empty list
    means bank; otherwise `surfaces.day.parse_plan()` returning a non-empty
    dict means day plan; otherwise the file is skipped silently, the same
    graceful-empty-list classification `cmd_guard` already relies on.

    An immediate directory symlink is an approved course root only when its
    resolved target contains its own in-target course sidecar. This is the
    same explicit link the course shelf admits. Nested symlinks never widen
    either root: a directory link is not followed, and a file whose real path
    escapes the active scan root is refused. Thus linking a course into the
    workspace grants read access to that course, not to arbitrary paths the
    course happens to link onward.

    Candidates are iterated in case-insensitive stem order (broken by full
    path for files that tie), so the winner of a stem collision is
    deterministic across restarts. Returns `(banks, plans, collisions)`,
    the first two keyed by filename stem, `collisions` a list of
    `(stem, winner_path, loser_path)`.
    """
    root = os.path.abspath(root)
    scan_roots = [(root, os.path.realpath(root))]
    try:
        entries = sorted(os.listdir(root))
    except OSError:
        entries = []
    try:
        import course as course_module
        sidecar_name = course_module.COURSE_SIDECAR_FILENAME
    except ImportError:
        sidecar_name = ""
    for entry in entries:
        linked = os.path.join(root, entry)
        if not os.path.islink(linked) or not os.path.isdir(linked):
            continue
        target = os.path.realpath(linked)
        sidecar = os.path.join(linked, sidecar_name)
        try:
            sidecar_inside = (sidecar_name and os.path.isfile(sidecar)
                              and os.path.commonpath(
                                  [target, os.path.realpath(sidecar)]) == target)
        except ValueError:
            sidecar_inside = False
        if sidecar_inside:
            scan_roots.append((linked, target))

    candidates = []
    seen_candidates = set()
    for scan_root, allowed_real in scan_roots:
        for dirpath, dirnames, filenames in os.walk(scan_root):
            kept = []
            for name in dirnames:
                child = os.path.join(dirpath, name)
                try:
                    inside = os.path.commonpath(
                        [allowed_real, os.path.realpath(child)]) == allowed_real
                except ValueError:
                    inside = False
                if name not in SKIP_DIRS and not os.path.islink(child) and inside:
                    kept.append(name)
            dirnames[:] = kept
            for name in filenames:
                if not name.lower().endswith(".md"):
                    continue
                path = os.path.join(dirpath, name)
                real = os.path.realpath(path)
                try:
                    inside = os.path.commonpath([allowed_real, real]) == allowed_real
                except ValueError:
                    inside = False
                if inside and real not in seen_candidates:
                    candidates.append((path, allowed_real))
                    seen_candidates.add(real)
    candidates.sort(key=lambda row: (os.path.splitext(os.path.basename(row[0]))[0].lower(), row[0]))

    year = datetime.date.today().year
    banks, plans, collisions = {}, {}, []
    winners = {}                                # lower stem -> winning path
    for path, allowed_real in candidates:
        stem = os.path.splitext(os.path.basename(path))[0]
        stem_key = stem.lower()
        if classification is not None:
            kind = classification.classify(path, allowed_real, year,
                                           parse_bank, day.parse_plan)
            if kind is None:
                continue
            table = banks if kind == "bank" else plans
        else:
            try:
                with open(path, encoding="utf-8") as stream:
                    text = stream.read()
            except (OSError, UnicodeDecodeError):
                continue
            if parse_bank(text):
                table = banks
            elif day.parse_plan(path, year):
                table = plans
            else:
                continue
        if stem_key in winners:
            collisions.append((stem, winners[stem_key], path))
            continue
        winners[stem_key] = path
        table[stem] = path
    return banks, plans, collisions


DISCOVERY_REFRESH_LOCK = threading.Lock()
DISCOVERY_CLASSIFICATION_CACHE = DiscoveryCache()


def _refresh_discovery(handler):
    """Refresh the identifier allowlists without invalidating live sittings.

    Course, home, palette, and bank-list GETs call this read-side refresh, so
    reloading one of those pages is the documented rescan action. Dictionary
    replacement is atomic for request readers. Existing per-bank session
    configuration is never discarded; newly admitted banks receive the same
    configuration startup builds.
    """
    with DISCOVERY_REFRESH_LOCK:
        banks, plans, collisions = scan_dir(handler.root, DISCOVERY_CLASSIFICATION_CACHE)
        old_banks = getattr(handler, "banks", None) or {}
        old_sessions = getattr(handler, "sessions", None) or {}
        # A removed or renamed bank becomes unreachable through `banks`, but
        # its live bookkeeping remains available to an in-flight request and
        # to a later reappearance under the same stem.
        sessions = dict(old_sessions)
        missing = {}
        for stem, path in banks.items():
            if old_banks.get(stem) != path or stem not in old_sessions:
                missing[stem] = path
        sessions.update(_build_sessions(missing))
        # HTTP handler instances are per request, while these allowlists live
        # on their shared handler class. Publish support before the new bank
        # allowlist on both: an overlapping request may see the old bank set,
        # but never a newly visible bank without its session configuration.
        handler_class = type(handler)
        for name, value in (("sessions", sessions), ("plans", plans),
                            ("collisions", collisions), ("banks", banks)):
            setattr(handler_class, name, value)
            setattr(handler, name, value)
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


REPORT_FAILURE_COPY = ("This report could not be derived from the current "
                       "evidence snapshot. Try again or run the report "
                       "command; no recommendation was made.")


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


SHELF_NOSCRIPT = ("The walkthrough, sample-course, and course-order controls "
                  "need scripting. Their offline CLI twin is itembank shelf "
                  "<action> .")

SHELF_SCRIPT = """<script>
(function () {
  var status = document.querySelector("[data-shelf-status]");
  document.querySelectorAll("form[data-shelf-form]").forEach(function (form) {
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      var button = event.submitter || form.querySelector("button[name=action]");
      if (!button) { return; }
      if (status) { status.textContent = "Working..."; }
      fetch("/api/shelf", {
        method: "POST", headers: {"Content-Type": "application/json"},
        body: JSON.stringify({action: button.value})
      }).then(function (response) {
        if (!response.ok) { throw new Error("That action was refused."); }
        window.location.href = "/";
      }).catch(function (error) {
        if (status) { status.textContent = error.message; }
      });
    });
  });

  var shelf = document.querySelector("[data-course-shelf]");
  if (!shelf) { return; }
  var fingerprint = shelf.getAttribute("data-workspace-fingerprint") || null;
  var dragging = null;
  var pointerStartOrder = null;
  var pointerId = null;
  var pointerMoved = false;
  var saving = false;

  function cards() { return Array.from(shelf.querySelectorAll("[data-course-id]")); }
  function ids() { return cards().map(function (card) { return card.dataset.courseId; }); }
  function sameOrder(left, right) {
    return left.length === right.length && left.every(function (id, index) {
      return id === right[index];
    });
  }
  function restore(order) {
    var focused = shelf.contains(document.activeElement) ? document.activeElement : null;
    order.forEach(function (id) {
      var card = shelf.querySelector('[data-course-id="' + CSS.escape(id) + '"]');
      if (card) { shelf.appendChild(card); }
    });
    syncButtons();
    if (focused && focused.isConnected) { focused.focus(); }
  }
  function syncButtons() {
    var rows = cards();
    rows.forEach(function (card, index) {
      var mark = card.querySelector('.course-mark');
      if (mark) { mark.textContent = String(index + 1).padStart(2, '0'); }
      var up = card.querySelector('[data-move="up"]');
      var down = card.querySelector('[data-move="down"]');
      if (up) { up.disabled = saving || index === 0; }
      if (down) { down.disabled = saving || index === rows.length - 1; }
    });
    var focus = document.querySelector('.desk-focus');
    var first = rows.find(function (row) { return row.dataset.resumable === 'true'; }) || rows[0];
    if (focus && first) {
      var action = first.querySelector('.course-card-actions a');
      var focusAction = focus.querySelector('.desk-focus-actions a');
      focus.querySelector('h2').textContent = first.querySelector('h2').textContent;
      focus.querySelector('.resume-cue').textContent = first.querySelector('.resume-cue').textContent;
      focus.querySelector('.desk-eyebrow').textContent = first.dataset.resumable === 'true'
        ? 'Continue a saved session' : 'First in your course order';
      var context = focus.querySelector('.desk-session-context');
      context.textContent = first.dataset.sessionContext || '';
      context.hidden = !context.textContent;
      focusAction.textContent = action.textContent;
      focusAction.setAttribute('aria-label', action.getAttribute('aria-label'));
      focusAction.href = action.href;
    }
  }
  function saveOrder(previous) {
    if (sameOrder(previous, ids())) { syncButtons(); return Promise.resolve(); }
    var failureMessage = "Could not confirm the saved course order. Reload to check it before trying again.";
    saving = true;
    syncButtons();
    if (status) { status.textContent = "Saving course order..."; }
    return fetch("/api/shelf", {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({action: "reorder_courses", course_ids: ids(),
                           expected_fingerprint: fingerprint})
    }).then(function (response) {
      if (!response.ok) {
        if (response.status === 409) {
          failureMessage = "Course order changed elsewhere. Reload and try again.";
        } else if (response.status >= 400 && response.status < 500) {
          failureMessage = "Course order could not be saved. Reload and try again.";
        }
        throw new Error(failureMessage);
      }
      return response.json();
    }).then(function (result) {
      if (!result || typeof result.fingerprint !== "string" || !result.fingerprint) {
        throw new Error(failureMessage);
      }
      fingerprint = result.fingerprint;
      shelf.setAttribute("data-workspace-fingerprint", fingerprint);
      saving = false;
      if (status) { status.textContent = "Course order saved."; }
      syncButtons();
    }).catch(function () {
      saving = false;
      restore(previous);
      if (status) { status.textContent = failureMessage; }
    });
  }

  shelf.addEventListener("click", function (event) {
    var button = event.target.closest("button[data-move]");
    if (!button || saving) { return; }
    var card = button.closest("[data-course-id]");
    var rows = cards();
    var index = rows.indexOf(card);
    var target = button.dataset.move === "up" ? rows[index - 1] : rows[index + 1];
    if (!target) { return; }
    var previous = ids();
    if (button.dataset.move === "up") { shelf.insertBefore(card, target); }
    else { shelf.insertBefore(target, card); }
    syncButtons();
    saveOrder(previous);
    var summary = card.querySelector('.course-details summary');
    if (summary) { summary.focus(); }
  });

  shelf.addEventListener("pointerdown", function (event) {
    var handle = event.target.closest("[data-drag-handle]");
    if (!handle || saving || dragging || event.isPrimary === false || event.button !== 0) { return; }
    dragging = handle.closest("[data-course-id]");
    pointerStartOrder = ids();
    pointerId = event.pointerId;
    pointerMoved = false;
    dragging.classList.add("is-dragging");
    shelf.setPointerCapture(pointerId);
    event.preventDefault();
  });
  shelf.addEventListener("pointermove", function (event) {
    if (!dragging || event.pointerId !== pointerId) { return; }
    var under = document.elementFromPoint(event.clientX, event.clientY);
    var target = under && under.closest("[data-course-id]");
    if (!target || target === dragging || !shelf.contains(target)) { return; }
    var box = target.getBoundingClientRect();
    shelf.insertBefore(dragging, event.clientY < box.top + box.height / 2
                       ? target : target.nextSibling);
    pointerMoved = true;
    event.preventDefault();
  });
  shelf.addEventListener("pointerup", function (event) {
    if (!dragging || event.pointerId !== pointerId) { return; }
    var previous = pointerStartOrder;
    dragging.classList.remove("is-dragging");
    dragging = null;
    pointerStartOrder = null;
    pointerId = null;
    shelf.releasePointerCapture(event.pointerId);
    if (pointerMoved) { saveOrder(previous); }
    pointerMoved = false;
  });
  function cancelDrag(returnFocus) {
    if (!dragging) { return; }
    var previous = pointerStartOrder;
    var handle = dragging.querySelector('[data-drag-handle]');
    var capturedPointer = pointerId;
    dragging.classList.remove("is-dragging");
    dragging = null;
    pointerStartOrder = null;
    pointerId = null;
    pointerMoved = false;
    restore(previous);
    if (shelf.hasPointerCapture && shelf.hasPointerCapture(capturedPointer)) {
      shelf.releasePointerCapture(capturedPointer);
    }
    if (returnFocus && handle) { handle.focus(); }
    if (status) { status.textContent = "Course move cancelled."; }
  }
  shelf.addEventListener("pointercancel", function (event) {
    if (event.pointerId === pointerId) { cancelDrag(false); }
  });
  shelf.addEventListener("lostpointercapture", function (event) {
    if (event.pointerId === pointerId) { cancelDrag(false); }
  });
  document.addEventListener("keydown", function (event) {
    if (dragging && event.key === "Escape") {
      event.preventDefault();
      cancelDrag(true);
    }
  });
  syncButtons();
})();
</script>"""


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
            '<button class="go" name="action" '
            'value="advance_walkthrough">%s</button>'
            '<button class="go ghost" name="action" '
            'value="skip_walkthrough">%s</button>'
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
        '<button class="go ghost" name="action" '
        'value="replay_walkthrough">%s</button>'
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


def _desk_course_choices(cards):
    """A compact Home entry list; full collection controls live on Courses."""
    choices = []
    for card in cards:
        choices.append(
            '<article class="course-card overhaul-course-choice" role="listitem" '
            'data-course-id="%s" data-attention="%s">'
            '<div class="course-card-main"><h2><a href="/course/%s">%s</a></h2>'
            '<span class="chip">%s</span><p class="resume-cue">%s</p></div>'
            '<div class="course-card-actions"><a class="go" href="%s" '
            'aria-label="%s">%s</a></div></article>' % (
                presentation.esc(card["course_id"]),
                presentation.esc(card["attention"]),
                urllib.parse.quote(card["course_id"], safe=""),
                presentation.esc(card["name"]), presentation.esc(card["chip"]),
                presentation.esc(card["resume_cue"]),
                presentation.esc(card["cta_href"]), presentation.esc(card["cta_label"]),
                presentation.esc(_course_action_label(card))))
    return ('<style>.overhaul-course-choices .course-card{'
            'grid-template-columns:minmax(0,1fr) auto}'
            '.overhaul-course-choice h2 a{overflow-wrap:anywhere}'
            '@media(max-width:640px){.overhaul-course-choices .course-card{'
            'grid-template-columns:minmax(0,1fr)}'
            '.overhaul-course-choices .course-card-actions{grid-column:1}}</style>'
            '<div class="overhaul-course-choices" role="list">%s</div>' % "".join(choices))


def _desk_loose_section(stems):
    """Quick-practice entry for loose banks, mirroring the `/banks` row links."""
    if not stems:
        return ""
    rows = []
    for stem in stems:
        quoted = urllib.parse.quote(stem, safe="")
        rows.append(
            '<article class="course-card overhaul-course-choice" role="listitem" '
            'data-loose-bank="%s"><div class="course-card-main"><h2>%s</h2>'
            '<p class="resume-cue">Not in a course</p></div>'
            '<div class="course-card-actions">'
            '<a class="go" href="/quiz/%s?mode=practice" aria-label="Practice %s">'
            'Practice</a><a class="go secondary" href="/study/%s" '
            'aria-label="Study %s">Study</a></div></article>'
            % (presentation.esc(stem), presentation.esc(stem), quoted,
               presentation.esc(stem), quoted, presentation.esc(stem)))
    return ('<section class="desk-course-section" aria-labelledby="loose-banks-title">'
            '<div class="desk-section-title"><h2 id="loose-banks-title">'
            'Practice sets</h2><a href="/banks">All files</a></div>'
            '<div class="overhaul-course-choices" role="list">%s</div></section>'
            % "".join(rows))


def _course_shelf_body(shelf, walkthrough=None, sample=None, list_only=False,
                       loose_banks=()):
    """Render the ordered course list with canonical actions and shelf hooks."""
    cards = []
    for index, card in enumerate(shelf["cards"]):
        links = []
        for action in card["actions"]:
            links.append('<a class="go secondary" href="%s">%s</a>'
                         % (presentation.esc(action["href"]),
                            presentation.esc(action["label"])))
        drag_control = ""
        order_controls = ""
        if shelf.get("reorderable"):
            drag_control = (
                '<span class="shelf-order-controls">'
                '<button type="button" data-drag-handle '
                'aria-label="Drag %s to a new position" title="Drag to reorder">'
                '&#8597; Drag</button></span>'
                % presentation.esc(card["name"]))
            order_controls = (
                '<div class="shelf-order-controls" aria-label="Order %s">'
                '<button type="button" data-move="up" aria-label="Move %s up"%s>&#8593;</button>'
                '<button type="button" data-move="down" aria-label="Move %s down"%s>&#8595;</button>'
                '</div>'
                % (presentation.esc(card["name"]),
                   presentation.esc(card["name"]), " disabled" if index == 0 else "",
                   presentation.esc(card["name"]),
                   " disabled" if index == len(shelf["cards"]) - 1 else ""))
        sample_controls = (_sample_course_controls(sample)
                           if sample and card["course_id"] == sample["course_id"]
                           else "")
        options = "".join(links) + order_controls + sample_controls
        details = ('<details class="course-details"><summary>Course options</summary>'
                   '<div class="course-options">%s</div></details>' % options
                   if options else "")
        cards.append(
            '<article class="course-card" data-course-id="%s" '
            'data-attention="%s" data-ia-token="%s" data-resumable="%s" '
            'data-session-context="%s" role="listitem">'
            '<span class="course-mark" aria-hidden="true">%02d</span>'
            '<div class="course-card-main"><h2>%s</h2>'
            '<span class="chip">%s</span>'
            '<p class="resume-cue">%s</p></div>'
            '<div class="course-card-actions">'
            '<a class="go" href="%s" aria-label="%s">%s</a>%s</div>%s</article>'
            % (presentation.esc(card["course_id"]),
               presentation.esc(card["attention"]),
               presentation.esc(card["token"]),
               "true" if (card.get("resume") or {}).get("state") == "active"
               and card["cta_href"].startswith("/quiz/") else "false",
               presentation.esc(_desk_session_context(card)),
               index + 1,
               presentation.esc(card["name"]),
               presentation.esc(card["chip"]),
               presentation.esc(card["resume_cue"]),
               presentation.esc(card["cta_href"]),
               presentation.esc(card["cta_label"]),
               presentation.esc(_course_action_label(card)),
               drag_control,
               details))
    degraded = [card for card in shelf["cards"] if card["degraded"]]
    banner = ""
    if degraded:
        # Precedence is the declared DEGRADED_STATES order (D-16B-9), not the
        # first card encountered, which is why this goes through
        # degraded_banner_for even though one state is fired today.
        banner = banner_markup(ia.degraded_banner_for(
            ["course_corrupted"], course_id=degraded[0]["course_id"]))
    offer = _walkthrough_offer(walkthrough) if walkthrough else ""
    if cards:
        help_copy = ("<p class=\"shelf-order-help\">Reorder with Drag, "
                     "or Move up and Move down in Course options.</p>"
                     if shelf.get("reorderable") else "")
        fingerprint = shelf.get("workspace_fingerprint") or ""
        content = ('%s<div class="course-shelf" role="list" data-course-shelf '
                   'data-workspace-fingerprint="%s">%s</div>'
                   % (help_copy, presentation.esc(fingerprint), "".join(cards)))
    else:
        content = ('<section class="empty shelf-empty">'
                   '<h2>%s</h2><p>%s</p>'
                   '<form class="actions" method="post" action="/api/shelf" '
                   'data-shelf-form><button class="go primary" name="action" '
                   'value="add_sample_course">Add the sample course</button>'
                   '</form></section>'
                   % (presentation.esc(shelf["empty_heading"]),
                      presentation.esc(shelf["empty_body"])))
    if list_only:
        return (content + '<p><a href="/restore">Restore a workspace copy</a></p>'
                '<p class="status" data-shelf-status role="status" '
                'aria-live="polite"></p>')
    first = _desk_focus_card(shelf["cards"])
    guidance = ("Pick up a saved session, or open a course to read and practice."
                if cards else "Add the sample course to explore this workspace.")
    heading = ('<section class="desk-heading"><div><h2>Your desk</h2>'
               '<p>%s</p></div><span class="desk-count">%d %s</span></section>'
               % (guidance, len(cards), "course" if len(cards) == 1 else "courses"))
    course_section = ('<section class="desk-course-section" aria-labelledby="course-shelf-title">'
                      '<div class="desk-section-title"><h2 id="course-shelf-title">'
                      'Your courses</h2><a href="/courses">All courses and options</a>'
                      '</div>%s</section>' % (_desk_course_choices(shelf["cards"]) if cards else content))
    help_section = ('<details class="overhaul-home-tools"><summary>Workspace help</summary>'
                    '%s<p><a href="/restore">Restore a workspace copy</a></p></details>' % offer)
    desk = ('<div class="overhaul-home">' + heading + _desk_hero(first)
            + '<div class="desk-below">' + course_section
            + _desk_loose_section(loose_banks) + '</div>' + help_section + '</div>')
    return ('%s%s%s%s%s<p class="status" data-shelf-status role="status" '
            'aria-live="polite"></p>'
            % (_app_nav("home"), desk, banner, "", ""))


def handle_courses_get(handler):
    """`GET /courses` renders the complete local shelf without desk coaching."""
    _refresh_discovery(handler)
    cfg = settings.load_settings(handler.root)
    shelf = ia.course_shelf_state(handler.root)
    cards = []
    for card in shelf.get("cards", ()):
        cards.append({
            "name": card["name"],
            "meta": card["resume_cue"],
            "chips": ({"label": card["chip"], "kind": "neutral"},),
            "actions": ({"label": _course_action_label(card),
                         "aria_label": card["cta_label"],
                         "href": card["cta_href"]},),
        })
    state = None if shelf.get("available") else {
        "kind": "unknown", "status": shelf.get("notice", "Courses unavailable")}
    course_list = (_course_shelf_body(shelf, sample=ia.sample_course_state(handler.root),
                                    list_only=True)
                   if shelf.get("available") and shelf.get("cards")
                   else presentation.course_shelf(
                       cards, empty="No courses are available yet.", state=state))
    body = (_app_nav("courses")
            + '<p class="area-lead">Every course stored on this device.</p>'
            + course_list)
    profile, _notice = settings.resolve_presentation_profile(cfg)
    handler.send_html(presentation.surface_shell(
        "Courses", body, theme_css=theme.theme_css(cfg), palette=True,
        noscript=SHELF_NOSCRIPT, tail=SHELF_SCRIPT,
        presentation_profile=profile).encode("utf-8"))


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

    Not only day routes any more: `/api/source/import` and, since 19A-02,
    every course write are gated here too, so the refusal says "this write"
    rather than naming the one family it was first written for.
    """
    if _reject_cross_origin(handler):
        return True
    if not _client_is_loopback(handler):
        handler.send_error(403, "this write requires a loopback client")
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


# `look` joined the actions on 2026-09-05: the look axis is switchable from
# the settings page, and it saves through `theme.persist_look`, the same
# single writer `itembank theme look` uses.
THEME_ACTIONS = ("preview", "pick", "save", "reset", "look", "profile", "mode")
THEME_ALLOWED_FIELDS = ("action", "source", "confirm", "look", "profile", "mode")


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
        theme.theme_page(cfg, sections=(
            '<section aria-labelledby="storage-heading"><h2 id="storage-heading">Storage</h2>'
            '<p><a href="/settings/storage">Inspect storage use and clear rebuildable caches</a></p>'
            '<p>Storage is scanned only when you open that page.</p></section>' + _mode_layer_section()),
                         palette=True, product=True).encode("utf-8"))


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
        if action == "look":
            look_id = data.get("look")
            if not looks.known(look_id):
                handler.send_error(
                    400, "settings.invalid_value: %r is not a known look; "
                    "known looks are: %s"
                    % (look_id, ", ".join(looks.LOOK_IDS)))
                return
            written = theme.persist_look(handler.root, look_id)
            handler.send_json({"saved": True, "look": written["look"],
                               "source": written["accent"],
                               "theme": written["theme"],
                               "preview": theme.theme_preview(
                                   written["accent"])})
            return
        if action == "mode":
            written = theme.persist_mode(handler.root, data.get("mode"))
            handler.send_json({"saved": True, "theme": written})
            return
        if action == "profile":
            written = theme.persist_presentation_profile(handler.root,
                                                         data.get("profile"))
            handler.send_json({"saved": True, "presentation_profile": written})
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


def _quiz_path(stem, launch_mode=None, receipt=None, answer=False,
               session_id=None, course_id=None, return_source=None):
    path = "/quiz/%s%s" % (urllib.parse.quote(stem, safe=""),
                            "/answer" if answer else "")
    query = []
    if launch_mode:
        query.append(("mode", launch_mode))
    if session_id:
        query.append(("session", session_id))
    if course_id:
        query.append(("course", course_id))
    if return_source:
        query.append(("return_source", return_source))
    if receipt:
        query.append(("receipt", receipt))
    return path + (("?" + urllib.parse.urlencode(query)) if query else "")


def _saved_quiz_session(handler, stem, path, qs, cfg=None):
    """Resolve the newest persisted sitting without starting or advancing it.

    Reuse the report index's bank matching and recency rule, narrowing to the
    requested mode for an explicit course-area launch. Validate the saved
    shape and selection against current items before handing its cursor to the
    runtime. A finished sitting stays finished, including on restart.
    """
    from schema_validate import validate

    try:
        index = session_index(handler.root)
        cfg = cfg or handler.sessions[stem]
        expected_mode = cfg.get("mode", "practice")
        candidates = []
        for session_id, candidate_path in index.items():
            try:
                data = read_session(candidate_path)
                mtime = os.path.getmtime(candidate_path)
            except (OSError, ValueError, SystemExit):
                continue
            if (data.get("bank") == os.path.abspath(path)
                    and (not cfg.get("mode_specific")
                         or data.get("mode") == expected_mode)):
                candidates.append((mtime, session_id, candidate_path, data))
        requested_id = cfg.get("requested_session_id")
        selected = (next((row for row in candidates if row[1] == requested_id), None)
                    if requested_id else max(candidates, key=lambda row: (row[0], row[1]),
                                             default=None))
        session_id = selected[1] if selected else None
        attempts = os.path.join(os.path.abspath(handler.root), "_attempts")
        try:
            files = {os.path.join(attempts, name) for name in os.listdir(attempts)
                     if name.startswith("session_") and name.endswith(".json")}
        except FileNotFoundError:
            files = set()
        if files - set(index.values()):
            raise ValueError("A saved session is unreadable. Review the session files before starting another sitting.")
        if requested_id and selected is None:
            raise ValueError("The selected saved session is unavailable. Choose a sitting from the course.")
        if session_id is None:
            return None
        saved = selected[2] if selected else None
        if saved is None:
            raise ValueError("Saved session changed while opening. Try again.")
        data = selected[3]
        schema = json.loads(resources.read_text("schemas/session.schema.json"))
        if validate(data, schema):
            raise ValueError("Saved session is invalid. Review the session files before continuing.")
        if (data["bank"] != os.path.abspath(path)
                or data["mode"] != expected_mode
                or not 0 <= data["cursor"] <= len(data["items"])
                or any(not 0 <= i < len(qs) for i in data["items"])):
            raise ValueError("Saved session does not match this quiz. Open its report before continuing.")
        selections = [event for event in evidence.events(
            evidence.log_path(os.path.dirname(os.path.abspath(path))))
            if event.get("event_type") == "selection"
            and event.get("session_id") == session_id]
        keys = [evidence.evidence_key(qs[i]) for i in data["items"]]
        if len(selections) != 1 or selections[0].get("items") != keys:
            raise ValueError("Saved session selection is unavailable or changed. Review the bank and session before continuing.")
        # Sessions do not pin a bank revision. A later file modification
        # therefore needs review even if its item ids still match.
        try:
            selected_at = datetime.datetime.fromisoformat(selections[0]["ts"])
            if selected_at.tzinfo is None or os.path.getmtime(path) > selected_at.timestamp():
                raise ValueError("bank modified after selection")
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("The bank file was modified or its saved selection time is unavailable. Review it before resuming.") from exc
        return saved, data
    except (SystemExit, OSError) as exc:
        raise ValueError("Saved session is unavailable. Review the session files before continuing.") from exc


def _ensure_quiz_session(handler, stem, path, qs, cfg=None):
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
        cfg = cfg or handler.sessions[stem]
        api_id = cfg.get("api_session_id")
        found = api_session_path(handler, api_id) if api_id else None
        if found:
            return found
        # An explicit `serve` launch owns its announced mode, seed and id.
        # Automatic restart recovery belongs to the workspace daemon only.
        saved = (None if cfg.get("progress") else
                 _saved_quiz_session(handler, stem, path, qs, cfg))
        if saved:
            found, data = saved
            cfg["api_session_id"] = data["session_id"]
            cfg["session_id"] = data["session_id"]
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


def _resolve_check(qs, check_id):
    """The one check-item resolution: by positional id or opaque [ID:], the
    same set the linter's lesson.check_ref_unknown accepts (D-01)."""
    for q in qs:
        if q["id"] == check_id or q.get("item_id") == check_id:
            return q
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


def _lesson_sitting_return(handler, lesson_path):
    """Admit an exact local sitting return without starting or advancing it."""
    try:
        outer = urllib.parse.parse_qs(urllib.parse.urlsplit(getattr(handler, "path", "")).query)
        values = outer.get("return", [])
        if len(values) != 1:
            return None
        target = urllib.parse.urlsplit(values[0])
        if target.scheme or target.netloc or not target.path.startswith("/quiz/") or "\\" in target.path:
            return None
        query = urllib.parse.parse_qs(target.query, keep_blank_values=True)
        required = {"mode", "session", "course"}
        if (not required <= set(query) or set(query) - required - {"return_source"} or
                any(len(query[k]) != 1 for k in required)):
            return None
        stem = target.path[len("/quiz/"):]
        path = handler.banks.get(stem)
        cid, sid, mode = (query[k][0] for k in ("course", "session", "mode"))
        base = ia.course_dir_for(handler.root, cid)
        if base is None or path is None or mode not in ("practice", "exam", "diagnostic"):
            return None
        admitted = {os.path.realpath(p) for _stem, p in _course_banks(handler, base)}
        if os.path.realpath(path) not in admitted or os.path.realpath(lesson_path) not in admitted:
            return None
        saved = _saved_quiz_session(handler, stem, path, load(path), cfg={
            "mode": mode, "mode_specific": True, "requested_session_id": sid})
        if saved is None or saved[1]["session_id"] != sid:
            return None
        source_return = _course_source_return(handler, cid, query=query)
        result = {"href": _quiz_path(
                    stem, mode, session_id=sid, course_id=cid,
                    return_source=source_return["source_id"] if source_return else None),
                  "label": "Return to saved sitting"}
        if source_return:
            result["source_return"] = source_return
        return result
    except (OSError, ValueError, KeyError, TypeError, SystemExit):
        return None


def _lesson_context_nav(handler, bank_path):
    """Build daemon-only lesson navigation from a uniquely owning course.

    The bank location is compared with the resolved course directory and a
    course is named only when exactly one shelf card owns the file. Every
    daemon lesson still has the Courses shelf link when course metadata is
    unavailable or ownership is ambiguous.
    """
    links = [{"href": "/courses", "label": "Courses"}]
    try:
        shelf = ia.course_shelf_state(handler.root)
    except Exception:
        return links
    matches = []
    bank_real = os.path.realpath(bank_path)
    for card in shelf.get("cards", ()):
        course_id = card.get("course_id")
        if not isinstance(course_id, str) or not course_id:
            continue
        course_dir = ia.course_dir_for(handler.root, course_id)
        if not course_dir:
            continue
        try:
            inside = (os.path.commonpath(
                [os.path.realpath(course_dir), bank_real])
                      == os.path.realpath(course_dir))
        except ValueError:
            inside = False
        if inside:
            matches.append(course_id)
    exact = _lesson_sitting_return(handler, bank_path)
    if len(matches) == 1:
        course_id = urllib.parse.quote(matches[0], safe="")
        source_return = _course_source_return(handler, matches[0])
        outer = urllib.parse.parse_qs(
            urllib.parse.urlsplit(getattr(handler, "path", "")).query,
            keep_blank_values=True)
        if "return_source" not in outer and exact:
            source_return = exact.get("source_return")
        links.insert(0, source_return or {
            "href": "/course/%s/learn" % course_id, "label": "Back to course"})
        links.append({"href": _quiz_path(
                          os.path.splitext(os.path.basename(bank_path))[0],
                          "practice", course_id=matches[0],
                          return_source=source_return["source_id"] if source_return else None),
                      "label": "Continue to practice"})
    if exact:
        links = [link for link in links if link["label"] != "Continue to practice"]
        links.insert(0, exact)
    return links


def _lesson_exploration_context(handler, bank_path, parsed_lesson, params):
    """Admit presentation continuity by source identity, revision and use."""
    if not parsed_lesson or parsed_lesson.get("error"):
        return None
    try:
        import course
        import journal
        from surfaces import course_workbench
        bank_real = os.path.realpath(bank_path)
        lesson_real = os.path.realpath(parsed_lesson.get("source") or bank_path)
        revision = hashlib.sha256(json.dumps(
            {key: value for key, value in parsed_lesson.items()
             if key not in ("source", "error", "detail")},
            ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
        matches = []
        for card in ia.course_shelf_state(handler.root).get("cards", ()):
            cid = card.get("course_id")
            base = ia.course_dir_for(handler.root, cid) if cid else None
            if base and os.path.commonpath([os.path.realpath(base), bank_real]) == os.path.realpath(base):
                matches.append((cid, base))
        requested = params.get("course", [])
        if requested:
            if len(requested) != 1 or len(matches) != 1:
                return None
            requested_base = ia.course_dir_for(handler.root, requested[0])
            if not requested_base or os.path.realpath(requested_base) != os.path.realpath(matches[0][1]):
                return None
        if len(matches) > 1:
            return None
        if not matches:
            if params.get("occurrence"):
                return None
            source_stat, bank_stat = os.stat(lesson_real), os.stat(bank_real)
            return {"lesson_id": "standalone:%s:%s" % (source_stat.st_dev, source_stat.st_ino),
                    "revision_id": revision,
                    "occurrence_id": "standalone:%s:%s" % (bank_stat.st_dev, bank_stat.st_ino)}
        cid, base = matches[0]
        read = course.read_course(base)
        if read.get("state") != "clean":
            return None
        registry = journal.read_registry(base)
        objects = [oid for oid, row in registry.items()
                   if row.get("kind") in ("bank", "lesson") and
                   os.path.realpath(os.path.join(base, row.get("path") or "")) == lesson_real and
                   journal.object_state(base, oid) == "clean"]
        if len(objects) != 1:
            return None
        bindings = []
        for row in course_workbench._current_safe_bindings(base, read["doc"]):
            if row.get("binding_kind") != "treatment" or row.get("treatment_kind") != "guided-lesson":
                continue
            locator = row.get("locator")
            match = re.match(r"^(.+?\.md)(?=$|[\s,;#])", locator.strip(), re.I) if isinstance(locator, str) else None
            if not match or os.path.isabs(match.group(1)):
                continue
            target = os.path.realpath(os.path.join(base, match.group(1)))
            if target in (bank_real, lesson_real):
                bindings.append(row)
        occurrence = params.get("occurrence", [])
        if occurrence:
            if len(occurrence) != 1:
                return None
            bindings = [row for row in bindings if row.get("binding_id") == occurrence[0]]
        if len(bindings) != 1:
            return None
        row = bindings[0]
        if not row.get("binding_id") or not row.get("binding_revision_id"):
            return None
        return {"lesson_id": objects[0], "revision_id": revision,
                "occurrence_id": "%s:%s:%s" % (cid, row["binding_id"], row["binding_revision_id"])}
    except (OSError, ValueError, TypeError, KeyError, AttributeError):
        return None


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
    context_nav = _lesson_context_nav(handler, path)
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
    if (params.get("view") or [""])[0] == "guided" and not print_mode:
        mode = "guided"
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
    exploration_context = _lesson_exploration_context(handler, path, les, params)
    reading_query = {}
    if mode != "guided":
        reading_query["view"] = "guided"
    if exploration_context:
        for key in ("course", "occurrence"):
            if len(params.get(key, [])) == 1:
                reading_query[key] = params[key][0]
    source_return = next((link for link in context_nav
                          if link.get("label") == "Back to source review"), None)
    if source_return:
        reading_query["return_source"] = source_return["source_id"]
    sitting_return = _lesson_sitting_return(handler, path)
    if sitting_return:
        reading_query["return"] = sitting_return["href"]
    context_nav = list(context_nav) + [{
        "href": "/lesson/%s%s" % (urllib.parse.quote(stem, safe=""),
                                    "?" + urllib.parse.urlencode(reading_query) if reading_query else ""),
        "label": "Read continuously" if mode == "guided" else "Read step by step"}]
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
                              tier_show_url=tier_show_url,
                              context_nav=context_nav,
                              exploration_context=exploration_context,
                              theme_css=theme.theme_css(settings.load_settings(handler.root)))
    handler.send_html(page.encode("utf-8"))


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


def _refresh_attempt_view(cfg, session_id, qs, bank_path):
    """Regenerate the configured attempt markdown atomically from the evidence
    log after an API submit, using `evidence.render_attempt_md` -- the exact
    render the legacy route and the CLI use, never a second writer -- and print
    the scoped-serve progress line from the API session's own event count.
    """
    md = evidence.render_attempt_md(cfg["log"], session_id, qs, bank_path)
    out_dir = os.path.dirname(cfg["out"])
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
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


# The whole of `/api/teach`'s accepted vocabulary (plan 14-03). Two body
# fields, one action field, two action kinds -- and nothing anywhere in it
# that could name a tier. That absence IS the D-09 boundary: a client asks
# for the next tier or for nothing, and which tier that is, and what it
# contains, stays the runtime's call (T-14-10).
TEACH_BODY_FIELDS = ("session_id", "action")
TEACH_ACTION_FIELDS = ("kind",)


COURSE_OPERATION_ACTOR_FIELDS = ("actor_kind", "reviewer_kind", "rights",
                                "rights_snapshot", "right", "fingerprint",
                                "base", "path", "root", "dest",
                                "destination", "archive", "manifest",
                                # 19A-05: the agent policy is read from
                                # settings on disk at the moment of the call
                                # and is never sent. An agent that could
                                # report its own authority could raise it,
                                # which is the self-expansion AGENT-02
                                # forbids; these four are the shapes a
                                # request would use to try.
                                "settings", "agent_policy", "autonomy_level",
                                "granted_level", "max_bindings_per_operation")


def _course_operation(handler, operation, envelope=None):
    """The dispatch spine every `/api/course/<operation>` route shares.

    One route per operation and one handler per route (D-02), but exactly one
    body of dispatch: the request is validated against the published document
    off disk before anything is read, the write is the frozen
    compare-and-swap one, and a typed refusal comes back as its code and its
    sentence so the client is told the next safe action rather than shown a
    stack trace. A later 19A wave adds an operation by adding a route, a
    ROUTE_CLI entry, a SURFACE_PARITY row and a `$defs` node, and copies
    nothing of this.

    Authority-shaped fields are refused by name, the same discipline every
    other mutating route here takes: the actor KIND is decided by the surface
    (a browser client is a human), a fingerprint of anything but the course
    being written is not a request field, and a course is addressed by its id
    and resolved server-side, never by a path.

    The gate is chosen by what the operation does, not by which route asked
    (19A-02). A course write is loopback-only, exactly like a day write and a
    theme save: a `--lan` daemon binds 0.0.0.0, and a phone on the same wifi
    may read a course but may never mint, rename, or bind one. The family's
    one read is gated by the same read-side check every other read here uses,
    because it appends no journal entry, writes no file, and changes no
    fingerprint.

    `envelope` keeps a published response shape: the two routes that landed
    before this spine existed answered `{"bound": ...}` and
    `{"recorded": ...}`, and folding them into the spine is not a licence to
    change what a client already parses. Non-negotiable 4 is about silent
    breakage, and a renamed key is exactly that.
    """
    if operation == "reading_view":
        if _reject_cross_origin_write(handler):
            return
    elif operation in course_ops.READ_OPERATIONS:
        if _reject_cross_origin(handler):
            return
    elif _reject_cross_origin_write(handler):
        return
    data, failed = api_read_json(handler)
    if failed:
        return
    for banned in COURSE_OPERATION_ACTOR_FIELDS:
        if banned in data:
            handler.send_error(400, "field %r is not accepted here; a course "
                                    "is addressed by its id, the actor kind "
                                    "is the surface's to decide, and a right "
                                    "is read from the journal, never sent"
                               % banned)
            return
    try:
        result = course_ops.run(handler.root, operation, data,
                                actor_kind=getattr(handler, "actor_kind", "human"),
                                actor_name=data.get("actor") or "")
    except Exception as exc:                       # typed course/graph errors
        code = getattr(exc, "code", None)
        if code:
            status = 404 if code == "course.unknown_course" else 400
            handler.send_error(status, "%s: %s"
                               % (code, getattr(exc, "message", str(exc))))
            return
        handler.send_server_error(exc)
        return
    if envelope is not None:
        flag, key = envelope
        handler.send_json({flag: True, key: result})
        return
    handler.send_json(result)



def handle_mcp(handler):
    """HTTP registration of the same JSON-RPC framing used by stdio."""
    if _reject_cross_origin(handler):
        return
    try:
        message = handler.read_json()
    except (ValueError, TypeError) as exc:
        handler.send_error(400, "malformed JSON-RPC body: %s" % exc)
        return
    from surfaces import mcp
    response = mcp.frame(handler, message)
    if response is None:
        handler.send_json({})
    else:
        handler.send_json(response)


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
    # Explicit Practice and Test launches keep separate runtime configurations
    # for the same bank. One must never reuse or mutate the other's sitting.
    DaemonHandler.quiz_mode_sessions = {}
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
    """One session configuration per bank for the life of this process.

    Configuration is read-only. The runtime creates `_attempts` only when a
    learner actually opens a sitting, so discovery and page refresh do not
    mutate a linked course.

    This uses the same
    session-id-printed-so-a-marker-can-find-it precedent `cmd_serve` sets,
    extended to every bank the daemon found rather than the one bank a single
    `serve` process used to hold. Shared by `cmd_daemon` and `cmd_sidecar`.
    """
    sessions = {}
    for stem, path in banks.items():
        bank_dir = os.path.dirname(os.path.abspath(path)) or "."
        out = os.path.join(bank_dir, "_attempts", "%s_attempt_%s.md" %
                           (stem, datetime.datetime.now().strftime("%Y-%m-%d_%H%M")))
        sessions[stem] = {
            "session_id": uuid.uuid4().hex,
            "log": evidence.log_path(bank_dir),
            "out": out,
            "mode": "practice",
        }
    return sessions


def cmd_daemon(a):
    root = a.dir
    banks, plans, collisions = scan_dir(root, DISCOVERY_CLASSIFICATION_CACHE)

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
    banks, plans, collisions = scan_dir(root, DISCOVERY_CLASSIFICATION_CACHE)
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
